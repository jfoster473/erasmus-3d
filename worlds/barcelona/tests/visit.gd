# The everything-visit (round 35, the user: "talk to every person/interact with every object. Read everything that can
# be read and walk into or past every item. Take pictures and review them for things that look wrong"):
#   tests.gd --visit=<abs folder> --part=<p>
# Everything the game offers on E (people, doors and their plaques, the street-name plaques, the street things, what
# lies on the ground, the cats, the dog, the bikes, the funicular, the telescope; in every room its things, stairs and
# people) is listed once by --part=census, in a walking order, into census.json; the other parts take their share:
#   out1, out2 … (45 outdoor things each), rooms1, rooms2 … (5 rooms each), late (everyone again, at the exam's eve,
#   from the play-through's saved state: what they say once their stories are done).
# Each thing: she is put down ~9 m off where she fits and walks up with the keys until the game offers it; E, and
# every page read to its end, the whole text kept in said.txt; then she walks into it for a second (things on walls,
# doors and what lies on the ground left out) and whether she went through is noted. index.tsv: one line a thing,
# what happened. The pictures (the user: "just take a picture every 10 seconds as you are going through, then read
# them all back at the end") are the screen every 10 s, pictures/NNN.jpg, with pictures.txt saying what she was at;
# a picture of its own only when something fails (fail_*.jpg).
# The walking and reading are the play-through's own (playthrough.gd: its map of where she fits, go, approach).
# The state carries over from part to part in the test save (delete it before census/out1 for a fresh game).
extends Node

const CHUNK := 45
const ROOMS_PER := 5
const DAY := 10 * 60 + 30                      # (the clock put back to mid-morning now and then: pictures by day)

var tst: Node
var m
var g
var pt                                         # playthrough.gd
var dir := ""
var pdir := ""
var n_pic := 0
var said_f: FileAccess
var ix_f: FileAccess
var shooting := false
var shot_t := 0.0
var shot_n := 0
var doing := ""


func run(tests: Node, main, out_dir: String, part: String) -> void:
	tst = tests
	m = main
	g = m.game
	dir = out_dir
	pdir = dir.path_join(part)
	DirAccess.make_dir_recursive_absolute(pdir)
	pt = Node.new()
	pt.set_script(load(m.world_res("tests/playthrough.gd")))
	add_child(pt)
	pt.tst = tests
	pt.m = m
	pt.g = g
	pt.dir = dir
	await get_tree().create_timer(3.0).timeout
	if part == "late" and not g.S.has("_pt"):
		var f := ProjectSettings.globalize_path("res://").path_join("workshop/test-runs/barcelona/playthrough/states/exam.json")
		DirAccess.copy_absolute(f, ProjectSettings.globalize_path(g.SAVE_PATH))
		get_tree().reload_current_scene()
		return
	if g.S.has("_pt"):
		var p0: Array = g.S._pt.pos
		g.S.erase("_pt")
		m.teleport(Vector3(p0[0], 0, p0[1]), 0.0)
	if g.S.get("new", false):
		g.intro()
		await pt.read_on()
	await pt.build_grids()
	if part == "census":
		census()
		tst.end_test()
		return
	var C = JSON.parse_string(FileAccess.get_file_as_string(dir.path_join("census.json")))
	if not C is Dictionary:
		printerr("VISIT no census.json: run --part=census first")
		tst.end_test()
		return
	said_f = FileAccess.open(pdir.path_join("said.txt"), FileAccess.WRITE)
	ix_f = FileAccess.open(pdir.path_join("index.tsv"), FileAccess.WRITE)
	ix_f.store_line("pic\tkind\tlabel\tx,z\twalk\tE\tinto it")
	DirAccess.make_dir_recursive_absolute(pdir.path_join("pictures"))
	var pf := FileAccess.open(pdir.path_join("pictures.txt"), FileAccess.WRITE)
	pf.store_line("picture\tclock\tplace\tx,z\tdoing")
	pf.close()
	shooting = true
	var t0 := Time.get_ticks_msec()
	if part.begins_with("out"):
		var k := int(part.trim_prefix("out")) - 1
		var all: Array = C.out
		var mine := all.slice(k * CHUNK, (k + 1) * CHUNK)
		for i in mine.size():
			if i % 12 == 0:
				m.set_clock(DAY)
			await visit_out(mine[i])
		await greet_passers()
	elif part.begins_with("rooms"):
		var k := int(part.trim_prefix("rooms")) - 1
		var all: Array = C.rooms
		for rid in all.slice(k * ROOMS_PER, (k + 1) * ROOMS_PER):
			m.set_clock(DAY)
			await visit_room(rid)
	elif part == "redo":
		# (after fixes: just the things named in redo.txt, a line each — an outdoor label as census.json has it, or a
		# room's id — in the order given)
		for ln in FileAccess.get_file_as_string(dir.path_join("redo.txt")).split("\n"):
			ln = ln.strip_edges(true, false) if ln.ends_with(" ") else ln.strip_edges()
			if ln == "":
				continue
			m.set_clock(DAY)
			if m.D.interiors.has(ln):
				await visit_room(ln)
				continue
			var near_x := INF                     # ("label|x": only the one(s) of that name within 3 m of that x)
			var name_ := ln
			if ln.contains("|"):
				near_x = float(ln.get_slice("|", 1))
				name_ = ln.get_slice("|", 0)
			for it in C.out:
				if it.label == name_ and (near_x == INF or absf(float(it.x) - near_x) < 3.0):
					await visit_out(it)
	elif part == "late":
		m.set_clock(DAY)
		for it in C.out:
			if it.kind == "person":
				await visit_out(it)
		for rid in C.rooms:
			await visit_room(rid, true)
	shooting = false
	printerr("VISIT %s done: %d things, %d pictures, %d min" % [part, n_pic, shot_n, (Time.get_ticks_msec() - t0) / 60000])
	said_f.close()
	ix_f.close()
	tst.end_test()


# ------------------------------------------------------------------ the census

func census() -> void:
	var D: Dictionary = m.D
	var out := []
	for id in g.data.NPCS:
		if g.data.NPCS[id].at[0] == "world":
			var pa: Array = pt.person_at(id)
			out.append({"kind": "person", "key": id, "label": "Talk to " + g.data.NPCS[id].name, "x": pa[1].x, "z": pa[1].y, "r": 1.7,
				"here": m.npcs.outdoor.has(id)})
	for i in D.entrances.size():
		var e: Dictionary = D.entrances[i]
		out.append({"kind": "door", "key": str(i), "label": "Go into " + e.name, "x": e.pos[0], "z": e.pos[1], "r": 1.3})
		if e.get("plaque", "") != "":
			var n := Vector2(e.normal[0], e.normal[1])
			var side: Vector2 = Vector2(-n.y, n.x) * (float(e.size[0]) / 2.0 + 0.45)
			var pp := Vector2(e.pos[0] + side.x + n.x * 0.3, e.pos[1] + side.y + n.y * 0.3)
			if e.has("plaque_pos"):
				pp = Vector2(e.plaque_pos[0], e.plaque_pos[1])
			out.append({"kind": "plaque", "key": str(i), "label": "Read the plaque of " + e.name, "x": pp.x, "z": pp.y, "r": 0.9})
	for i in D.plaques.size():
		out.append({"kind": "sign", "key": str(i), "label": "Street sign " + D.plaques[i].text, "x": D.plaques[i].pos[0], "z": D.plaques[i].pos[1], "r": 1.5})
	for i in D.things2d.size():
		var th: Dictionary = D.things2d[i]
		out.append({"kind": "thing", "key": str(i), "label": "%s %s" % [th.type, th.get("id", "")], "x": th.pos[0], "z": th.pos[1], "r": 1.6})
	for gi in g.ground:
		out.append({"kind": "ground", "key": gi.id, "label": "Pick up " + g.item(gi.id).name, "x": gi.pos.x, "z": gi.pos.z, "r": 1.2})
	for i in m.touches.cats.size():
		var c: Dictionary = m.touches.cats[i]
		out.append({"kind": "cat", "key": str(i), "label": "Look at the cat", "x": c.pos.x, "z": c.pos.z, "r": 1.6})
	for c in m.north.candidates(Vector3.ZERO):
		out.append({"kind": "north", "key": c.what, "label": c.label, "x": c.x, "z": c.z, "r": c.r})
	if m.street.trufa:
		var tp: Vector3 = m.street.trufa.global_position
		out.append({"kind": "trufa", "key": "", "label": "The dog", "x": tp.x, "z": tp.z, "r": 1.5})
	for i in m.street.bikes.size():
		var bk: Node3D = m.street.bikes[i]
		out.append({"kind": "bike", "key": str(i), "label": "A parked bike", "x": bk.position.x, "z": bk.position.z, "r": 1.1})
	# a walking order: nearest next, from the beach
	var order := []
	var left := out.duplicate()
	var at := Vector2(m.player.global_position.x, m.player.global_position.z)
	while not left.is_empty():
		var bi := 0
		var bd := INF
		for i in left.size():
			var d := at.distance_to(Vector2(left[i].x, left[i].z))
			if d < bd:
				bd = d
				bi = i
		at = Vector2(left[bi].x, left[bi].z)
		order.append(left[bi])
		left.remove_at(bi)
	# rooms: in the order of their doors along that walk (the stairs' room after the room it's reached from)
	var rooms := []
	for it in order:
		if it.kind == "door":
			var rid: String = D.entrances[int(it.key)].int
			if not rid in rooms:
				rooms.append(rid)
	for rid in D.interiors:
		if not rid in rooms:
			rooms.append(rid)
	# can a player stand where the game offers each one, and get there from the beach?
	var rep := FileAccess.open(dir.path_join("census.txt"), FileAccess.WRITE)
	var start: Vector2i = pt.free_near(pt.grid, pt.cell_of(Vector2(m.player.global_position.x, m.player.global_position.z)))
	var bad := 0
	for it in order:
		var c: Vector2i = pt.free_near(pt.grid, pt.cell_of(Vector2(it.x, it.z)), 12)
		var note := ""
		if c.x < 0:
			note = "nowhere she fits within 6 m"
		else:
			var dd: float = pt.cell_pos(c).distance_to(Vector2(it.x, it.z))
			if dd > float(it.r) - 0.1:
				note = "the nearest she fits is %.1f m off; the game offers it from %.1f m" % [dd, it.r]
			elif pt.grid.get_id_path(start, c).is_empty():
				note = "not joined to the beach on foot"
		it["census"] = note
		if note != "":
			bad += 1
		rep.store_line("%s\t%s\t%.1f,%.1f\t%s" % [it.kind, it.label, it.x, it.z, note if note != "" else "ok"])
	var nthings := 0
	for rid in rooms:
		nthings += D.interiors[rid].things.size() + D.interiors[rid].stairs.size()
	rep.store_line("TOTAL outdoors %d (%d with a note), rooms %d with %d things and stairs" % [order.size(), bad, rooms.size(), nthings])
	rep.close()
	var f := FileAccess.open(dir.path_join("census.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify({"out": order, "rooms": rooms}, " "))
	f.close()
	printerr("VISIT census: %d outdoors (%d with a note: census.txt), %d rooms, %d room things; parts out1..out%d, rooms1..rooms%d, late" % [
		order.size(), bad, rooms.size(), nthings, ceili(order.size() / float(CHUNK)), ceili(rooms.size() / float(ROOMS_PER))])


# ------------------------------------------------------------------ one thing outdoors

func live(it: Dictionary) -> Dictionary:
	# where it is now, and how to know the game is offering it: {at, want, bump} (empty: not there now)
	var D: Dictionary = m.D
	var at := Vector2(it.x, it.z)
	var want: Callable
	var bump := true
	match String(it.kind):
		"person":
			if not m.npcs.outdoor.has(it.key) or m.npcs.outdoor[it.key].is_empty() or m.npcs.outdoor[it.key].get("gone", false):
				return {}
			var pa: Array = pt.person_at(it.key)
			at = pa[1]
			want = func(n): return n.get("act", "") == "npc" and n.get("who", "") == it.key
		"door":
			var e: Dictionary = D.entrances[int(it.key)]
			want = func(n): return n.get("act", "") == "door" and n.e.int == e.int and n.e.pos == e.pos
			bump = false
		"plaque":
			var e2: Dictionary = D.entrances[int(it.key)]
			want = func(n): return n.get("act", "") == "plaque" and n.get("bid", "") == e2.id
			bump = false
		"sign":
			want = func(n): return n.get("act", "") == "sign" and absf(n.x - it.x) < 0.01 and absf(n.z - it.z) < 0.01
			bump = false
		"thing":
			var th: Dictionary = D.things2d[int(it.key)]
			want = func(n): return n.get("act", "") == "thing" and n.th.get("pos", []) == th.pos
		"ground":
			var gi := {}
			for x in g.ground:
				if x.id == it.key and x.node.visible and Vector2(x.pos.x, x.pos.z).distance_to(at) < 3.0:
					gi = x
			if gi.is_empty():
				return {}
			want = func(n): return n.get("act", "") == "pick" and n.g == gi
			bump = false
		"cat":
			want = func(n): return n.get("act", "") == "cat" and absf(n.x - it.x) < 0.01 and absf(n.z - it.z) < 0.01
		"north":
			want = func(n): return n.get("act", "") == "north" and n.get("what", "") == it.key
			bump = it.key == "telescope"
		"trufa":
			if not m.street.trufa or m.street.trufa.in_basket != 0.0:
				return {}
			var tp: Vector3 = m.street.trufa.global_position
			at = Vector2(tp.x, tp.z)
			want = func(n): return n.get("act", "") == "trufa"
		"bike":
			if int(it.key) >= m.street.bikes.size():
				return {}
			var bk: Node3D = m.street.bikes[int(it.key)]
			at = Vector2(bk.position.x, bk.position.z)
			want = func(n): return n.get("act", "") in ["bike", "bike_locked"] and n.bike == bk
	return {"at": at, "want": want, "bump": bump}


func start_spot(at: Vector2) -> Vector2:
	# somewhere she fits ~9 m off with a short way to it (else nearer), outdoors
	var goal: Vector2i = pt.free_near(pt.grid, pt.cell_of(at), 16)
	if goal.x < 0:
		return Vector2.INF
	for rad in [9.0, 6.0, 3.5]:
		for k in 16:
			var a := TAU * k / 16.0
			var c: Vector2i = pt.cell_of(at + Vector2(cos(a), sin(a)) * rad)
			if pt.grid.is_point_solid(c):
				continue
			var path: Array = pt.grid.get_id_path(c, goal)
			if not path.is_empty() and path.size() * 0.5 < rad * 2.2:
				return pt.cell_pos(c)
	return pt.cell_pos(goal)


func visit_out(it: Dictionary) -> void:
	var L := live(it)
	n_pic += 1
	var tag := "%03d_%s" % [n_pic, slug(it.label)]
	if L.is_empty():
		line(tag, it, "not there now", "", "")
		return
	var at: Vector2 = L.at
	var s := start_spot(at)
	if s == Vector2.INF:
		line(tag, it, "nowhere she fits near it", "", "")
		return
	m.teleport(Vector3(s.x, 0, s.y), atan2(at.x - s.x, at.y - s.y))
	await get_tree().create_timer(0.6).timeout
	await pt.read_on()
	# (a person may have walked on meanwhile)
	L = live(it)
	if L.is_empty():
		line(tag, it, "gone meanwhile", "", "")
		return
	at = L.at
	doing = String(it.label)
	var ok: bool = await pt.approach(at, L.want, String(it.label))
	if not ok and it.kind == "door" and m.where == "in":
		# (walked straight in through it on the way up: that's a door working)
		await get_tree().create_timer(1.2).timeout
		var out0: bool = await pt.go_out()
		line(tag, it, "walked in through it", "went in" if out0 else "went in, and NOT OUT: " + pt.fail, "")
		return
	if not ok and it.kind in ["person", "trufa"]:
		# (someone who wanders, 'r' in their data: she follows where they are now, as a player does)
		for f in 600:
			var n0: Dictionary = m.nearest()
			if not n0.is_empty() and L.want.call(n0):
				ok = true
				break
			var L2 := live(it)
			if L2.is_empty():
				break
			at = L2.at
			pt.drive((at - pt.here2()).normalized())
			await get_tree().physics_frame
		pt.keys_off()
		if not ok:
			pt.fail += " (and followed for 10 s)"
	if not ok:
		await pic("fail_" + tag)
		line(tag, it, "NOT OFFERED: " + pt.fail, "", "")
		return
	var walk := "offered %.1f m off" % pt.here2().distance_to(at)
	m.input_key(KEY_E)
	var pages: Array = await read_all(tag)
	said(tag, it.label, pages)
	if m.where == "in":
		# (a door: in, a look round, and out again)
		await get_tree().create_timer(1.2).timeout
		var out_ok: bool = await pt.go_out()
		line(tag, it, walk, "went in" if out_ok else "went in, and NOT OUT: " + pt.fail, "")
		return
	var into := ""
	if L.bump:
		into = await bump_into(at, tag, it)
	line(tag, it, walk, "%d pages" % pages.size() if not pages.is_empty() else "NOTHING HAPPENED", into)


func bump_into(at: Vector2, tag: String, it := {}) -> String:
	var p0: Vector2 = pt.here2()
	if p0.distance_to(at) > 3.0:
		return "too far to try"
	var dmin := INF
	for i in 75:
		if not it.is_empty() and it.kind in ["person", "trufa"]:
			var L2 := live(it)
			if not L2.is_empty():
				at = L2.at                   # (someone who walks about: where they are now)
		var d: Vector2 = at - pt.here2()
		pt.drive(d.normalized() if d.length() > 0.05 else (at - p0).normalized())
		await get_tree().physics_frame
		dmin = minf(dmin, pt.here2().distance_to(at))
		if m.dlg_open or m.where == "in":
			break
	pt.keys_off()
	var p1: Vector2 = pt.here2()
	var through: bool = dmin < 0.3                  # (her middle at its middle: nothing stopped her; sliding round it is fine)
	if m.dlg_open:
		said(tag, "(walking into it)", await read_all(tag + "_x"))
	if through:
		await pic("fail_" + tag + "_through")
		return "WENT THROUGH (came within %.2f m of its middle)" % dmin
	return "stopped %.2f m from its middle" % dmin


func greet_passers() -> void:
	# a few of the passers-by, wherever she ended
	var p: Vector2 = pt.here2()
	var near := []
	for i in m.people.people.size():
		var q: Vector3 = m.people.people[i].holder.position
		near.append([p.distance_to(Vector2(q.x, q.z)), i])
	near.sort()
	for k in mini(3, near.size()):
		var i: int = near[k][1]
		var q: Vector3 = m.people.people[i].holder.position
		var it := {"kind": "passer", "label": "Say hello to a passer-by", "x": q.x, "z": q.z}
		n_pic += 1
		var tag := "%03d_passer" % n_pic
		var s := start_spot(Vector2(q.x, q.z))
		if s == Vector2.INF:
			continue
		m.teleport(Vector3(s.x, 0, s.y), 0.0)
		await get_tree().create_timer(0.4).timeout
		q = m.people.people[i].holder.position
		doing = "a passer-by"
		# (they walk on: she follows where they are now, as a player does)
		var ok := false
		for f in 600:
			var n0: Dictionary = m.nearest()
			if not n0.is_empty() and n0.get("act", "") == "person" and n0.get("who", -1) == i:
				ok = true
				break
			q = m.people.people[i].holder.position
			pt.drive((Vector2(q.x, q.z) - pt.here2()).normalized())
			await get_tree().physics_frame
		pt.keys_off()
		pt.fail = "she followed them for 10 s and was never offered them"
		if not ok:
			line(tag, it, "NOT OFFERED: " + pt.fail, "", "")
			continue
		m.input_key(KEY_E)
		var pages: Array = await read_all(tag)
		said(tag, it.label, pages)
		line(tag, it, "offered", "%d pages" % pages.size(), "")


# ------------------------------------------------------------------ one room

func visit_room(rid: String, people_only := false) -> void:
	var R: Dictionary = m.D.interiors[rid]
	var parent := ""
	for r2 in m.D.interiors:
		for st in m.D.interiors[r2].stairs:
			if st.to == rid and pt.entrance_of(rid).is_empty():
				parent = r2
	var e: Dictionary = pt.entrance_of(parent if parent != "" else rid)
	if e.is_empty():
		line("---", {"kind": "room", "label": R.get("name", rid), "x": 0, "z": 0}, "NO DOOR", "", "")
		return
	if m.where == "in":
		await pt.go_out()
	var front := Vector2(e.pos[0], e.pos[1]) + Vector2(e.normal[0], e.normal[1]) * 7.0
	var s := start_spot(front)
	m.teleport(Vector3(s.x, 0, s.y), 0.0)
	await get_tree().create_timer(0.5).timeout
	n_pic += 1
	var tag := "%03d_%s" % [n_pic, slug(R.get("name", rid))]
	var ok: bool = await pt.go_in(parent if parent != "" else rid)
	if ok and parent != "":
		var st0: Dictionary = {}
		for st in m.D.interiors[parent].stairs:
			if st.to == rid:
				st0 = st
		ok = await pt.approach(Vector2(st0.pos[0], st0.pos[1]), func(n): return n.get("act", "") == "stairs" and n.to == rid, "the stairs")
		if ok:
			m.input_key(KEY_E)
			for i in 20:
				await get_tree().create_timer(0.25).timeout
				if m.room == rid and not m.busy:
					break
			ok = m.room == rid
	await get_tree().create_timer(1.0).timeout
	if not ok:
		await pic("fail_" + tag)
		line(tag, {"kind": "room", "label": R.get("name", rid), "x": e.pos[0], "z": e.pos[1]}, "NOT IN: " + pt.fail, "", "")
		return
	line(tag, {"kind": "room", "label": R.get("name", rid), "x": e.pos[0], "z": e.pos[1]}, "in", "", "")
	var items := []
	if not people_only:
		for i in R.things.size():
			var th: Dictionary = R.things[i]
			items.append({"kind": "rthing", "label": "%s: %s" % [R.get("name", rid), m.thing_label(th) + " (" + String(th.get("kind", "")) + ")"],
				"x": th.pos[0], "z": th.pos[1], "th": th})
		for st in R.stairs:
			items.append({"kind": "rstairs", "label": "the stairs to " + st.to, "x": st.pos[0], "z": st.pos[1], "st": st})
		for c in m.touches.room_candidates(rid):
			items.append({"kind": "rtouch", "label": c.label, "x": c.x, "z": c.z, "act": c.act})
	for id in m.npcs.indoor:
		var q: Dictionary = m.npcs.indoor[id]
		if q.is_empty() or q.get("gone", false):
			continue
		var pa: Array = pt.person_at(id)
		items.append({"kind": "rperson", "label": "Talk to " + g.data.NPCS[id].name, "x": pa[1].x, "z": pa[1].y, "id": id})
	for it in items:
		if m.where != "in" or m.room != rid:
			if not await pt.go_in(rid):
				break
		n_pic += 1
		var t2 := "%03d_%s" % [n_pic, slug(it.label)]
		var want: Callable
		var stairs := false
		match String(it.kind):
			"rthing":
				var th2: Dictionary = it.th
				want = func(n): return n.get("act", "") == "thing" and n.th == th2
			"rstairs":
				want = func(n): return n.get("act", "") == "stairs"
				stairs = true
			"rtouch":
				want = func(n): return n.get("act", "") == it.act
			"rperson":
				want = func(n): return n.get("act", "") == "npc" and n.get("who", "") == it.id
		var at := Vector2(it.x, it.z)
		doing = String(it.label)
		var ok2: bool = await pt.approach(at, want, String(it.label))
		if not ok2:
			var why: String = pt.fail
			var n2: Dictionary = m.nearest()
			if it.kind == "rthing" and String(it.th.get("kind", "")) in ["counter", "libdesk", "pfand"] and not n2.is_empty() and n2.get("act", "") == "npc":
				why = "(the one behind it answers for it)"
			if not why.begins_with("("):
				await pic("fail_" + t2)
			line(t2, it, "NOT OFFERED: " + why, "", "")
			continue
		var walk := "offered %.1f m off" % pt.here2().distance_to(at)
		m.input_key(KEY_E)
		if stairs:
			await get_tree().create_timer(1.5).timeout
			line(t2, it, walk, "to " + m.room, "")
			continue
		var pages: Array = await read_all(t2)
		said(t2, it.label, pages)
		var into := ""
		if it.kind == "rthing" or it.kind == "rperson":
			into = await bump_into(at, t2)
		line(t2, it, walk, "%d pages" % pages.size() if not pages.is_empty() else "NOTHING HAPPENED", into)
	if m.where == "in" and parent != "" and m.room == rid:
		# (a room reached by stairs: down them first, as a player goes)
		for st in R.stairs:
			if await pt.approach(Vector2(st.pos[0], st.pos[1]), func(n): return n.get("act", "") == "stairs", "the stairs down"):
				m.input_key(KEY_E)
				for i in 20:
					await get_tree().create_timer(0.25).timeout
					if m.room != rid and not m.busy:
						break
	if m.where == "in":
		var ok3: bool = await pt.go_out()
		await get_tree().create_timer(1.0).timeout
		n_pic += 1
		if not ok3:
			await pic("fail_%03d_out_of_%s" % [n_pic, slug(R.get("name", rid))])
			line("%03d" % n_pic, {"kind": "room", "label": R.get("name", rid), "x": 0, "z": 0}, "NOT OUT: " + pt.fail, "", "")


# ------------------------------------------------------------------ reading, pictures, notes

func read_all(tag: String) -> Array:
	# every page to its end (a question: its last option, the "no thanks" one; a panel: a picture, then shut)
	var pages := []
	var quiet := 0
	var shot := false
	var t0 := Time.get_ticks_msec()
	var seen := {m.toast_label.text: true}
	while quiet < 5 and Time.get_ticks_msec() - t0 < 60000:
		await get_tree().create_timer(0.25).timeout
		# (the short notes at the top: money, things received)
		for tt in [m.toast_label.text] + m.toasts.map(func(e): return e[0]):
			if not seen.has(tt):
				seen[tt] = true
				pages.append("[note] " + String(tt))
		if m.north.scope_active():
			if not shot:
				shot = true
				pages.append("[the telescope's view]")
				# (a look round: left a while, then down, then step back, as a player does)
				m.vkeys[KEY_LEFT] = true
				await get_tree().create_timer(5.0).timeout
				m.vkeys.clear()
				m.vkeys[KEY_DOWN] = true
				await get_tree().create_timer(1.5).timeout
				m.vkeys.clear()
				await get_tree().create_timer(5.0).timeout
				m.input_key(KEY_E)
			quiet = 0
			continue
		if m.panels.is_open():
			await get_tree().create_timer(1.5).timeout
			pages.append("[%s panel]" % m.panels.kind)
			m.panels.key(KEY_ESCAPE)
			quiet = 0
			continue
		if not m.dlg_open:
			if g.q.is_empty() and not m.busy:
				quiet += 1
			continue
		quiet = 0
		pages.append("%s: %s" % [m.dlg_who.text, m.dlg_text.text])
		await get_tree().create_timer(0.4).timeout             # (long enough for a 10 s picture to catch a box now and then)
		if m.choice_box.visible:
			var pick: int = m.dlg_choices.size() - 1
			pages.append("   [%s] -> %s" % [" | ".join(m.dlg_choices), m.dlg_choices[pick]])
			m.input_key(KEY_1 + pick)
		else:
			m.input_key(KEY_E)
	return pages


func _process(dt: float) -> void:
	if not shooting:
		return
	shot_t += dt
	if shot_t < 10.0:
		return
	shot_t -= 10.0
	shot_n += 1
	get_viewport().get_texture().get_image().save_jpg(pdir.path_join("pictures/%03d.jpg" % shot_n), 0.85)
	var p: Vector3 = m.player.global_position
	var place: String = m.D.interiors[m.room].get("name", m.room) if m.where == "in" else m.street_name(p)
	var pf := FileAccess.open(pdir.path_join("pictures.txt"), FileAccess.READ_WRITE)
	pf.seek_end()
	pf.store_line("%03d\t%02d:%02d\t%s\t%.0f,%.0f\t%s" % [shot_n, int(g.S.time) / 60 % 24, int(g.S.time) % 60, place, p.x, p.z, doing])
	pf.close()


func pic(name: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_jpg(pdir.path_join(name + ".jpg"), 0.85)


func said(tag: String, label: String, pages: Array) -> void:
	said_f.store_line("== %s  %s" % [tag, label])
	for p in pages:
		said_f.store_line(String(p))
	said_f.flush()


func line(tag: String, it: Dictionary, walk: String, e: String, into: String) -> void:
	var s := "%s\t%s\t%s\t%.1f,%.1f\t%s\t%s\t%s" % [tag, it.kind, it.label, float(it.x), float(it.z), walk, e, into]
	ix_f.store_line(s)
	ix_f.flush()
	printerr("VISIT " + s.replace("\t", "  |  "))


func slug(s: String) -> String:
	var out := ""
	for ch in s.to_lower():
		out += ch if (ch >= "a" and ch <= "z") or (ch >= "0" and ch <= "9") else "_"
	while out.contains("__"):
		out = out.replace("__", "_")
	return out.left(40).trim_suffix("_")
