# The play-through (round 32, the user: "from a fresh game, play every mission in the order a player would take them,
# all the way to the exam's end … do each step the way a player does it"): tests.gd --playthrough=<folder>[ --from=<k>].
# Sandra is driven by the keys as a player drives her: the mouse turns the camera where she should set off, W runs,
# A and D steer, E talks, buys, picks up; doors are walked through; on the bike, B, pedal and lean. Her routes come
# from a map of where her body fits (the physics world itself, sampled every half metre, the hill's too-steep ground
# left out). Each mission's steps come from the mission data: who gives it (MISSIONS[k].giver), and where each thing
# it needs comes from: a shop's shelf (SHOPS), the ground (the game's own list), a cupboard (the containers), or
# someone's hands. When she is short of money she earns it as a player would: bottles to the Pfand desk, shells to
# Salva, red mushrooms to Guillem.
# A step that can't be done is said in plain words (which mission, which step, where she was, what the game offered
# her) and the run stops; the game's state is saved at the start of every mission (states/<k>.json), and --from=<k>
# starts there instead of on the beach.
# The picture tour (the user, same round): every 10 s of play, the screen exactly as the player sees it, the game's
# own camera, talk boxes and all: pictures/NNN.jpg, with index.txt saying where and when each one was taken;
# tools/tour_sheet.py lays them out on captioned sheets.
#
# How to run it (standalone, not in any suite yet):
#   rm the test save (".../Flor de Lliri - Godot test/test_save.json"), then
#   Godot --audio-driver Dummy --path . -- --playthrough=<abs folder>              from the beach
#   Godot --audio-driver Dummy --path . -- --playthrough=<abs folder> --from=guell  from that mission's saved state
# A stop prints "PLAY STOPPED …" with the place, what the game offered, and (for "kept getting stopped") what held
# her: the boxes she pressed, anyone within 2 m, her real speed, and what the hill's slope rule made of her step.
# It also saves stopped_<mission>.jpg. The map of where she fits is cached in user://playthrough_map.bin (rebuilt
# when scene.json, main.gd or north.gd change; bump the "vN-" key when the map's own rules change).
#
# State at round 32's end (the user stopped it there): 13 missions played through cleanly from the beach (home to
# the pickpocket); Park Güell's salamander reached the cellar step; the ball, the level, Ponç's book (waiting for the
# path) and the exam never ran. Not in tools/run_tests.sh full — it would stall in the park.
#
# State at round 34's end: ALL DONE from a fresh game — all 17 missions, the exam passed, 47 min of play (~55 min to
# run). On the way it found three of the game's own faults (the funicular's top door 72 m off on the hillside; the
# funfair's southern 30 m sunk into a slope below its paving, Rosalia out of reach; one of Alba's wildflowers past a
# railing) and taught this test to ride the funicular from Park Güell, to keep a body's width off steep ground, to walk
# (not ride) the hills, to step back when the slope holds her, and to wait for a passer-by to clear a doorway. It
# still catches now and then on the hill path's railings at two bends and gets past on its own. Each retry is printed.
#
# NEXT TIME, TRY IT A DIFFERENT WAY (the user, round 32: "You keep running into issues in the park"). Most of the
# park's stops were this test's own steering, not the game — each needed a separate probe to tell them apart, and
# each probe a 3-minute replay. Do it in this order instead:
#   1. A reach check first, no walking: for every person, door, counter, cupboard, clue and ground item the missions
#      use, ask the map of where she fits (and the game's own offer radius, npcs.gd 'reach', nearest()'s r) whether a
#      player can stand where the game offers it, and whether that spot joins up with the beach. One launch, a list.
#      It would have found the brush in a house, Jaume in his pillar, the walled-off side stairs and the museum's door
#      in one go.
#   2. Then each mission's legs on their own: put her ~15 m from each target and walk only the last stretch with the
#      keys (door, talk, buy, pick up, E), checking the game's state after. Short, independent, re-runnable singly.
#   3. Only then the whole run from the beach, mainly for the picture tour — or take the pictures in step 2.
# And when something stops her, probe the game at that spot first (one short key-driven walk there, as seam_walk
# does) before changing either the game or this test.
extends Node

const ORDER := ["home", "gift", "dog", "bike", "crema", "brush", "profbook", "flour", "rivalry", "hat", "camera",
	"grail", "thief", "guell", "ball", "level", "exam"]
# what a player does for each one, in words the steps below understand:
#   talk <who>      walk to them and talk ("giver": whoever MISSIONS[k] says gives the mission), read every page
#   get <item> [n]  fetch it from wherever it comes from: a shop, the ground, a cupboard, someone's hands
#   use <thing>     walk to a thing (the card on her desk, the dust, the crate) and press E at it
#   in <room>       walk in through its door;  inout: in and out of the nearest door
#   ticket          buy a Park Güell ticket from the man at the gate;  trufa: call the dog;  robbed: be robbed
const STEPS := {
	"home": ["in int_sandra"],
	"gift": ["use card", "talk rosa", "get torro_joan", "talk alessandra"],
	"dog": ["talk giver", "trufa", "talk giver"],
	"bike": ["talk giver", "get bike_chain", "talk giver"],
	"crema": ["talk giver", "get crema", "talk giver"],
	"brush": ["talk giver", "get brush", "talk giver"],
	"profbook": ["talk giver", "get textbook", "talk giver"],
	"flour": ["talk giver", "get rye", "talk giver"],
	"rivalry": ["talk giver", "get torro_mar", "talk giver"],
	"hat": ["talk giver", "get cap", "talk tomas"],
	"camera": ["talk giver", "get camera_marta", "talk giver"],
	"grail": ["talk giver", "talk alba", "get flower 5", "talk alba", "talk giver"],
	"thief": ["robbed", "talk bofarull", "talk manolo"],
	"guell": ["ticket", "talk giver", "shut cellar", "get cellar_key", "in int_trias_cellar", "use crate", "talk giver"],
	"ball": ["talk giver", "get ball", "talk biel"],
	"level": ["talk toni"],                  # (round 41: the path opens as she hands it over, rule 10 #16d)
	"exam": ["talk maria", "talk oriol"],
}
# (things nobody sells and nobody drops: who hands them over)
const HANDS := {"bike_chain": "genis", "textbook": "alice", "bk_ghost": "alba"}
# (what's bought back, and by whom)
const BUYERS := {"bottle": ["anna", 100], "shell": ["salva", 100], "red_mushroom": ["guillem", 500]}

const CELL := 0.5
var SHOT_EVERY := 10.0          # (round 41: --shotevery=<s> for a closer look at one stretch)
const LOOK := 2.2                     # how far ahead along the route she aims, on foot (m)
const USE_BIKE := true                # long ways on the bike, once she has it

var tst: Node                         # tests.gd
var m                                 # main.gd
var g                                 # the story (story.gd on engine/game.gd)
var dir := ""
var grid := AStarGrid2D.new()         # where she fits on foot, outdoors
var bgrid := AStarGrid2D.new()        # …and on the bike
var gx0 := 0.0
var gz0 := 0.0
var nx := 0
var nz := 0
var dyn := []                         # [body, cells(, "gate")]: the hill path's barrier, the park's gates (shut until opened)
var rooms := {}                       # rid -> [AStarGrid2D, cell]
var mission := ""
var step := ""
var shooting := false
var shot_t := 0.0
var shot_n := 0
var t_start := 0
var fail := ""                        # why the last thing didn't work, in plain words
var blocked_by_works := false         # …and it was only the hill path's works in the way
var waiting := []                     # [mission, step] put by until the path opens
var stopped_by := ""                  # what held her, the last time she got nowhere


# ------------------------------------------------------------------ the run

func run(tests: Node, main, out_dir: String, from: String) -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shotevery="):
			SHOT_EVERY = float(a.trim_prefix("--shotevery="))
	tst = tests
	m = main
	g = m.game
	dir = out_dir
	DirAccess.make_dir_recursive_absolute(dir.path_join("pictures"))
	DirAccess.make_dir_recursive_absolute(dir.path_join("states"))
	await get_tree().create_timer(3.0).timeout
	var start := 0
	if from != "":
		# (resuming: the state saved at the start of that mission is loaded by the game itself, as a saved game)
		var pt: Dictionary = g.S.get("_pt", {})
		if pt.get("mission", "") != from:
			var f := dir.path_join("states/%s.json" % from)
			if not FileAccess.file_exists(f):
				printerr("PLAY no saved state for '%s' (%s)" % [from, f])
				tst.end_test()
				return
			DirAccess.copy_absolute(f, ProjectSettings.globalize_path(g.SAVE_PATH))
			get_tree().reload_current_scene()
			return
		g.S.erase("_pt")
		for wt in pt.get("waiting", []):
			waiting.append([String(wt[0]), int(wt[1])])
		start = ORDER.find(from)
		m.teleport(Vector3(pt.pos[0], 0, pt.pos[1]), float(pt.get("facing", 0.0)))
		m.set_clock(float(g.S.time))
		shot_n = DirAccess.get_files_at(dir.path_join("pictures")).size()
		printerr("PLAY resuming at '%s' (%s), picture %d on" % [from, g.mission_title(from), shot_n + 1])
	else:
		for f in DirAccess.get_files_at(dir.path_join("pictures")):
			DirAccess.remove_absolute(dir.path_join("pictures").path_join(f))
		var ix := FileAccess.open(dir.path_join("index.txt"), FileAccess.WRITE)
		ix.store_string("picture\tplay\tclock\tplace\tx,z\tmission: step\n")
		ix.close()
	await build_grids()
	t_start = Time.get_ticks_msec()
	shooting = true
	if from == "":
		g.intro()
		await read_on()
	for i in range(start, ORDER.size()):
		var k: String = ORDER[i]
		save_state(k)
		printerr("PLAY --- %d. %s" % [i + 1, g.mission_title(k)])
		if not await play(k, 0):
			return
		# (a mission put by because the workmen's barrier was in the way: once the path is open, back to it)
		for wt in waiting.duplicate():
			if g.S.flags.get("pathOpen", false):
				waiting.erase(wt)
				printerr("PLAY --- back to %s (the path is open now)" % g.mission_title(wt[0]))
				if not await play(wt[0], wt[1]):
					return
	if not waiting.is_empty():
		fail = "the path never opened, so these had to stay unfinished: %s" % ", ".join(waiting.map(func(w): return g.mission_title(w[0])))
		report(waiting[0][0], waiting[0][1], STEPS[waiting[0][0]].size())
		shooting = false
		tst.end_test()
		return
	shooting = false
	printerr("PLAY ALL DONE: the exam is passed (%s) in %d min of play, %d pictures" % [g.S.flags.get("examPassed", false),
		(Time.get_ticks_msec() - t_start) / 60000, shot_n])
	tst.end_test()


func play(k: String, from_j: int) -> bool:
	# a mission's steps from from_j on; false: the run is over (said why)
	mission = k
	var t1 := Time.get_ticks_msec()
	var steps: Array = STEPS[k]
	for j in range(from_j, steps.size()):
		step = steps[j]
		blocked_by_works = false
		var ok: bool = await do_step(k, step)
		if not ok and blocked_by_works:
			printerr("PLAY     (%s is past the workmen's barrier, which only opens once the path is finished: this waits till then, as a player's would)" % step_words(step, k))
			waiting.append([k, j])
			return true
		if not ok:
			report(k, j, steps.size())
			shooting = false
			tst.end_test()
			return false
	# (the exam's montage, the agent's run to Manolo: some endings take a while, with nothing to read meanwhile)
	for w in 120:
		await read_on()
		if g.m_done(k):
			break
		await get_tree().create_timer(0.5).timeout
	var done: bool = g.m_done(k)
	printerr("PLAY     %s: %s in %d s (%s, %s)" % [k, "done" if done else "NOT DONE", (Time.get_ticks_msec() - t1) / 1000,
		g.money(g.S.money), where_words()])
	if not done:
		fail = "every step went through, but the game doesn't count the mission as done (it says: \"%s\")" % g.objective_text().replace("\n", " — ")
		report(k, steps.size() - 1, steps.size())
		shooting = false
		tst.end_test()
		return false
	return true


func report(k: String, j: int, n: int) -> void:
	get_viewport().get_texture().get_image().save_jpg(dir.path_join("stopped_%s.jpg" % k), 0.88)
	var n2: Dictionary = m.nearest()
	printerr("PLAY STOPPED in \"%s\", step %d of %d (%s): %s" % [g.mission_title(k), j + 1, n, step_words(STEPS[k][j], k), fail])
	printerr("PLAY   Sandra was %s; the game offered her: %s; the mission said: \"%s\"" % [where_words(),
		"\"%s\"" % n2.label if not n2.is_empty() else "nothing", g.objective_text().replace("\n", " — ")])
	printerr("PLAY   to go on from the start of this mission after a fix: --playthrough=%s --from=%s" % [dir, k])


func step_words(s: String, k: String) -> String:
	var w := s.split(" ")
	match w[0]:
		"talk": return "talking to " + g.data.NPCS[who_of(w[1], k)].name
		"get": return "getting %s" % g.item(w[1]).name
		"use": return "using the " + w[1]
		"in": return "going into " + String(m.D.interiors.get(w[1], {}).get("name", w[1]))
		"inout": return "going in and out of a door"
		"ticket": return "buying a Park Güell ticket"
		"trufa": return "calling Trufa"
		"robbed": return "letting Manolo pick her pocket"
		"shut": return "trying the cellar door without the key"
	return s


func where_words() -> String:
	var p: Vector3 = m.player.global_position
	if m.where == "in":
		var lp: Vector3 = m.local_pos()
		return "inside %s (%.1f, %.1f)" % [m.D.interiors[m.room].get("name", m.room), lp.x, lp.z]
	return "outdoors on %s (%.0f, %.0f)%s" % [m.street_name(p), p.x, p.z, " on her bike" if m.street.riding != null else ""]


func save_state(k: String) -> void:
	g.save_game()
	var S: Dictionary = g.S.duplicate(true)
	var p: Vector3 = m.player.global_position
	if m.where == "in" and not m.room_door.is_empty():
		var d: Dictionary = m.room_door
		p = Vector3(d.pos[0] + d.normal[0] * 2.0, 0, d.pos[1] + d.normal[1] * 2.0)
	S["_pt"] = {"mission": k, "pos": [p.x, p.z], "facing": m.model.rotation.y, "waiting": waiting}
	var f := FileAccess.open(dir.path_join("states/%s.json" % k), FileAccess.WRITE)
	f.store_string(JSON.stringify(S))


# ------------------------------------------------------------------ the picture tour

func _process(dt: float) -> void:
	if not shooting:
		return
	shot_t += dt
	if shot_t < SHOT_EVERY:
		return
	shot_t -= SHOT_EVERY
	shot_n += 1
	var img := get_viewport().get_texture().get_image()
	img.save_jpg(dir.path_join("pictures/%03d.jpg" % shot_n), 0.88)
	var secs := (Time.get_ticks_msec() - t_start) / 1000
	var place: String = m.D.interiors[m.room].get("name", m.room) if m.where == "in" else m.street_name(m.player.global_position)
	if m.cutscene:
		place += " (riding)"
	elif m.where == "out" and m.street.riding != null:
		place += " (on the bike)"
	var p: Vector3 = m.player.global_position
	var line := "%03d\t%02d:%02d\t%02d:%02d\t%s\t%.0f,%.0f\t%s: %s\n" % [shot_n, secs / 60, secs % 60, int(g.S.time) / 60 % 24,
		int(g.S.time) % 60, place, p.x, p.z, mission, step]
	var ix := FileAccess.open(dir.path_join("index.txt"), FileAccess.READ_WRITE)
	if ix == null:
		ix = FileAccess.open(dir.path_join("index.txt"), FileAccess.WRITE)      # (round 40: a new run's first line)
	ix.seek_end()
	ix.store_string(line)
	ix.close()


# ------------------------------------------------------------------ the map of where she fits

func build_grids() -> void:
	var W: Dictionary = m.D.walk
	gx0 = W.x0
	gz0 = W.z0
	nx = int((W.x1 - W.x0) / CELL) + 1
	nz = int((W.z1 - W.z0) / CELL) + 1
	for gr in [grid, bgrid]:
		gr.region = Rect2i(0, 0, nx, nz)
		gr.cell_size = Vector2(CELL, CELL)
		gr.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
		gr.default_compute_heuristic = AStarGrid2D.HEURISTIC_OCTILE
		gr.default_estimate_heuristic = AStarGrid2D.HEURISTIC_OCTILE
		gr.update()
	# the story's own walls are left out of the map and put in (or not) before each route
	var skip := []
	if m.north.barrier_body:
		skip.append(m.north.barrier_body.get_rid())
		dyn.append([m.north.barrier_body, rect_cells(m.north.N.barrier)])
	# (round 38, 06 #97) each park gate its own body; the leaves' open-pose bodies are left out of the map too
	for gt in m.north.gates:
		skip.append(gt.body.get_rid())
		for l in gt.leaves:
			skip.append(l.body.get_rid())
		dyn.append([gt.body, rect_cells(gt.rect), "gate"])
	var key := "v7-%d-%d-%d" % [FileAccess.get_modified_time(m.out_dir.path_join("scene.json")),
		FileAccess.get_modified_time("res://engine/main.gd"), FileAccess.get_modified_time(m.world_res("game/north.gd"))]
	var cache := "user://playthrough_map.bin"
	var bits := PackedByteArray()
	if FileAccess.file_exists(cache):
		var f := FileAccess.open(cache, FileAccess.READ)
		if f.get_line() == key:
			bits = f.get_buffer(nx * nz)
	var t0 := Time.get_ticks_msec()
	if bits.size() != nx * nz:
		bits.resize(nx * nz)
		var pl: CharacterBody3D = m.player
		var q := PhysicsShapeQueryParameters3D.new()
		q.shape = pl.get_child(0).shape
		q.exclude = skip + [pl.get_rid()]
		var space := pl.get_world_3d().direct_space_state
		var cr: Array = m.D.city_rect
		var br: Array = m.D.get("bridge_rect", [0, 0, 0, 0])
		for iz in nz:
			for ix in nx:
				var x := gx0 + ix * CELL
				var z := gz0 + iz * CELL
				var b := 0
				q.transform = Transform3D(Basis(), Vector3(x, 0.82, z))
				q.collision_mask = m.LAYER_BODY
				if not space.intersect_shape(q, 1).is_empty():
					b = 3
				else:
					var p := Vector3(x, 0, z)
					var city: bool = x >= cr[0] and x <= cr[2] and z >= cr[1] and z <= cr[3]
					if m.ground_at(p) < -0.3:
						b = 3                                   # water
					elif not city and not (x >= br[0] - 1.7 and x <= br[2] + 1.7 and z >= br[1] - 1.7 and z <= br[3] + 1.7):
						# (round 34: and a little to each side — her body is as wide as that, and a route along the very
						# edge of a steep bank led her into it)
						var s: float = m.north.gradient(p).length()
						for off in [Vector3(0.4, 0, 0), Vector3(-0.4, 0, 0), Vector3(0, 0, 0.4), Vector3(0, 0, -0.4)]:
							s = maxf(s, m.north.gradient(p + off).length())
						# (a little under the game's limit, which is measured the way she walks; built stairs and ramps,
						# the 'flats', are made to be climbed: the dragon stairs are right at it)
						# (round 34: on steep ground only well inside a path counts — at its very edge her body is off it
						# to the game, and the slope rule held her there)
						if s > m.north.MAX_UP - 0.02 and not (m.north.on_path(p, -0.1) or m.north.on_steps(p) or on_flat(x, z) or m.north.at_doorstep(p)):
							b = 3                               # too steep to walk up (and to cut down safely)
					if b == 0:
						q.collision_mask = m.LAYER_NOBIKE
						if not space.intersect_shape(q, 1).is_empty():
							b = 2                               # sand, the thick of the wood: on foot only
						elif m.ground_at(p) > 0.01:
							b = 4                               # pavement, paths, grass: the bike goes slower there
				bits[iz * nx + ix] = b
			if iz % 40 == 0:
				await get_tree().process_frame
		var f := FileAccess.open(cache, FileAccess.WRITE)
		f.store_line(key)
		f.store_buffer(bits)
	var nfree := 0
	for iz in nz:
		for ix in nx:
			var b := bits[iz * nx + ix]
			if b & 1:
				grid.set_point_solid(Vector2i(ix, iz))
			else:
				nfree += 1
			if b & 2:
				bgrid.set_point_solid(Vector2i(ix, iz))
			elif b & 4:
				bgrid.set_point_weight_scale(Vector2i(ix, iz), 4.0)     # (a player rides on the road)
	# (doors are walked through: a route that brushes past one mustn't go in by mistake)
	for e in m.D.entrances:
		var c := cell_of(Vector2(e.pos[0] + e.normal[0] * 0.5, e.pos[1] + e.normal[1] * 0.5))
		for dz in range(-3, 4):
			for dx in range(-3, 4):
				var cc := c + Vector2i(dx, dz)
				if grid.is_in_boundsv(cc):
					grid.set_point_weight_scale(cc, 25.0)
	printerr("PLAY map of where she fits: %d x %d cells, %d free (%d s)" % [nx, nz, nfree, (Time.get_ticks_msec() - t0) / 1000])


func on_flat(x: float, z: float) -> bool:
	for f in m.D.get("flats", []):
		if x >= f[0] and x <= f[2] and z >= f[1] and z <= f[3]:
			return true
	return false


func rect_cells(r: Array) -> Array:
	var out := []
	var a := cell_of(Vector2(r[0] - 0.4, r[1] - 0.4))
	var b := cell_of(Vector2(r[2] + 0.4, r[3] + 0.4))
	for iz in range(a.y, b.y + 1):
		for ix in range(a.x, b.x + 1):
			out.append(Vector2i(ix, iz))
	return out


func cell_of(p: Vector2) -> Vector2i:
	return Vector2i(clampi(roundi((p.x - gx0) / CELL), 0, nx - 1), clampi(roundi((p.y - gz0) / CELL), 0, nz - 1))


func cell_pos(c: Vector2i) -> Vector2:
	return Vector2(gx0 + c.x * CELL, gz0 + c.y * CELL)


func free_near(gr: AStarGrid2D, c: Vector2i, most := 12) -> Vector2i:
	# the nearest cell she fits in (a person stands at a counter, a thing lies by a wall)
	if gr.is_in_boundsv(c) and not gr.is_point_solid(c):
		return c
	for r in range(1, most):
		var best := Vector2i(-1, -1)
		var bd := INF
		for dz in range(-r, r + 1):
			for dx in range(-r, r + 1):
				if maxi(absi(dx), absi(dz)) != r:
					continue
				var cc := c + Vector2i(dx, dz)
				if gr.is_in_boundsv(cc) and not gr.is_point_solid(cc) and Vector2(dx, dz).length() < bd:
					bd = Vector2(dx, dz).length()
					best = cc
		if best.x >= 0:
			return best
	return Vector2i(-1, -1)


func room_grid(rid: String) -> Array:
	if rooms.has(rid):
		return rooms[rid]
	var R: Dictionary = m.D.interiors[rid]
	var cs := 0.25
	var gr := AStarGrid2D.new()
	gr.region = Rect2i(0, 0, int(R.w / cs) + 1, int((R.h + 1.0) / cs) + 1)
	gr.cell_size = Vector2(cs, cs)
	gr.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	gr.default_compute_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	gr.default_estimate_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	gr.update()
	var pl: CharacterBody3D = m.player
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = [pl.get_rid()]
	var space := pl.get_world_3d().direct_space_state
	var base: Vector3 = m.room_base(rid)
	for iz in gr.region.size.y:
		for ix in gr.region.size.x:
			q.transform = Transform3D(Basis(), base + Vector3(ix * cs, 0.82, iz * cs))
			if not space.intersect_shape(q, 1).is_empty():
				gr.set_point_solid(Vector2i(ix, iz))
	rooms[rid] = [gr, cs]
	return rooms[rid]


func route(to: Vector2, bike := false, partial := false) -> PackedVector2Array:
	# the cells' route from where she is, as points (outdoors in the world, in a room from its corner)
	var p: Vector3 = m.local_pos()
	if m.where == "in":
		var rg: Array = room_grid(m.room)
		var gr: AStarGrid2D = rg[0]
		var cs: float = rg[1]
		var a := free_near(gr, Vector2i(roundi(p.x / cs), roundi(p.z / cs)), 8)
		var b := free_near(gr, Vector2i(clampi(roundi(to.x / cs), 0, gr.region.size.x - 1), clampi(roundi(to.y / cs), 0, gr.region.size.y - 1)), 12)
		if a.x < 0 or b.x < 0:
			return PackedVector2Array()
		var out := PackedVector2Array()
		for c in gr.get_id_path(a, b, partial):
			out.append(Vector2(c.x * cs, c.y * cs))
		return out
	var gr2: AStarGrid2D = bgrid if bike else grid
	for d in dyn:
		var shut: bool = (d[0] as StaticBody3D).collision_layer != 0
		if d.size() > 2 and m.north.park_open():
			shut = false                          # (round 38: a gate she has the ticket for, E opens on the way)
		for c in d[1]:
			grid.set_point_solid(c, shut)
			bgrid.set_point_solid(c, shut)
	var a2 := free_near(gr2, cell_of(Vector2(p.x, p.z)))
	var b2 := free_near(gr2, cell_of(to), 16)
	if a2.x < 0 or b2.x < 0:
		return PackedVector2Array()
	var out2 := PackedVector2Array()
	for c in gr2.get_id_path(a2, b2, partial):
		out2.append(cell_pos(c))
	return out2


func works_in_way(to: Vector2) -> bool:
	# would there be a way, were the hill path's barrier open?
	if m.north.barrier_body == null or m.north.barrier_body.collision_layer == 0:
		return false
	for c in dyn[0][1]:
		grid.set_point_solid(c, false)
	var a := free_near(grid, cell_of(here2()))
	var b := free_near(grid, cell_of(to), 16)
	var ok := a.x >= 0 and b.x >= 0 and not grid.get_id_path(a, b).is_empty()
	for c in dyn[0][1]:
		grid.set_point_solid(c, true)
	return ok


# ------------------------------------------------------------------ the keys

func keys(want: Dictionary) -> void:
	for k in [KEY_W, KEY_A, KEY_S, KEY_D]:
		if want.has(k):
			m.vkeys[k] = true
		else:
			m.vkeys.erase(k)


func keys_off() -> void:
	keys({})


func here2() -> Vector2:
	var p: Vector3 = m.local_pos()
	return Vector2(p.x, p.z)


func drive(want: Vector2) -> void:
	# one frame of a player's hands on the keys, to send her that way
	if m.where == "in" and not m.free_cam():
		# (a room's fixed camera: the keys are the screen's, up is away from the camera)
		var k := {}
		if want.y < -0.38:
			k[KEY_W] = true
		elif want.y > 0.38:
			k[KEY_S] = true
		if want.x < -0.38:
			k[KEY_A] = true
		elif want.x > 0.38:
			k[KEY_D] = true
		keys(k)
		return
	if m.street.riding != null:
		ride(want)
		return
	var md: Vector2 = m.move_dir
	if m.speed < 0.4 and not m.vkeys.has(KEY_W):
		# setting off: the mouse turns the camera that way, then forward
		m.cam_yaw_node.rotation.y = atan2(-want.x, -want.y)
		m.last_manual_cam = m.t
		keys({KEY_W: true})
		return
	var err := md.angle_to(want)
	if absf(err) > 1.25:
		keys_off()                                  # too far round to steer: stop, and set off again that way
	elif err < -0.05:
		keys({KEY_W: true, KEY_A: true})
	elif err > 0.05:
		keys({KEY_W: true, KEY_D: true})
	else:
		keys({KEY_W: true})


func ride(want: Vector2) -> void:
	# on the bike: pedal, lean into the turn; slow for a sharp one
	var err: float = m.move_dir.angle_to(want)
	var k := {}
	if absf(err) > 0.9 and m.speed > 3.0:
		k[KEY_S] = true                             # brake for the corner
	elif absf(err) < 1.6 or m.speed < 1.0:
		k[KEY_W] = true
	if err < -0.04:
		k[KEY_A] = true
	elif err > 0.04:
		k[KEY_D] = true
	keys(k)


# ------------------------------------------------------------------ getting about

func go(to: Vector2, arrive := 1.0, what := "") -> bool:
	# walks (or rides) her there along a route, steering; tries again round anything that stops her
	var tries := 0
	while tries < 5:
		var bike: bool = m.where == "out" and m.street.riding != null
		var pts := route(to, bike)
		if pts.is_empty():
			if bike:
				await hop_off()
				continue
			fail = "no way there that she fits through (%s)" % (what if what != "" else "to %.0f, %.0f" % [to.x, to.y])
			blocked_by_works = m.where == "out" and works_in_way(to)
			if blocked_by_works:
				return false
			# (someone behind a gate, over a railing: as close as she can get, and let the prompt decide)
			pts = route(to, false, true)
			if pts.size() < 2:
				return false
		# (a person behind a counter, a thing against a wall: the route ends at the nearest place she fits)
		var goal := to
		var arr := arrive
		if pts[-1].distance_to(to) > arrive:
			goal = pts[-1]
			arr = 0.6
		var start_p := here2()
		var r: int = await follow(pts, goal, arr)
		if r == 1:
			return true
		if r == 2:
			return false
		tries += 1
		printerr("PLAY       (try %d to %s: from %s along %d points, %s, stopped at %s: %s)" % [tries, what, start_p, pts.size(),
			"riding" if bike else "on foot", here2(), stopped_by])
		# stopped by something: a step back and a fresh start from where she is (on the bike: back it off whatever
		# she rode into; stuck twice, off and on foot)
		if m.street.riding != null:
			if tries >= 2:
				await hop_off()
			else:
				keys({KEY_S: true})
				await get_tree().create_timer(1.2).timeout
		else:
			# (on foot: a step to one side, then the other next time — head-on into the very corner of a post she
			# doesn't slide round it, and the same route would send her straight back into it)
			var side: Vector2 = (m.move_dir as Vector2).rotated(PI / 2.0 if tries % 2 == 1 else -PI / 2.0)
			# (round 34: held by the hill's slope, a step back the way she came, not sideways — sideways went downhill
			# off the path, and from there the only way on was up the slope)
			if stopped_by.contains("too steep"):
				side = -(m.move_dir as Vector2)
			keys_off()
			await settle()
			for i in 24:
				drive(side)
				await get_tree().physics_frame
		keys_off()
		await get_tree().create_timer(0.4).timeout
	fail = "she kept getting stopped on the way (%s; %s)" % [what if what != "" else "to %.0f, %.0f" % [to.x, to.y], stopped_by]
	return false


func follow(pts: PackedVector2Array, goal: Vector2, arrive: float) -> int:
	# 1 there; 0 stopped by something; 2 the place changed under her (a door, a ride)
	var where0: String = m.where
	var room0: String = m.room
	var ci := 0
	var check_p := here2()
	var check_t := 0.0
	var total := 0.0
	var length := 0.0
	for i in range(1, pts.size()):
		length += pts[i].distance_to(pts[i - 1])
	var limit := 20.0 + length / 2.0
	while true:
		await get_tree().physics_frame
		var dt := get_physics_process_delta_time()
		total += dt
		if m.where != where0 or m.room != room0:
			keys_off()
			return 2
		if m.dlg_open or m.busy or m.cutscene:
			keys_off()
			if m.dlg_open:
				await read_on()
			check_t = 0.0
			continue
		var p := here2()
		if p.distance_to(goal) < arrive:
			keys_off()
			return 1
		# where she is along the route, then a point a little ahead of that to aim at
		var best := INF
		for i in range(ci, mini(ci + 40, pts.size())):
			var d := pts[i].distance_to(p)
			if d < best:
				best = d
				ci = i
		# (indoors the keys give only eight ways, so she aims close and turns each corner of the route)
		var look: float = 0.7 if (m.where == "in" and not m.free_cam()) else LOOK * (2.0 if m.street.riding != null else 1.0)
		# (round 34: out on the hills, closer: aiming 2.2 m ahead she cut the hill path's bends onto ground too steep
		# to climb back from)
		var cr2: Array = m.D.city_rect
		if m.where == "out" and m.street.riding == null and not (p.x >= cr2[0] and p.x <= cr2[2] and p.y >= cr2[1] and p.y <= cr2[3]):
			look = 1.2
		var ti := ci
		while ti < pts.size() - 1 and pts[ti].distance_to(p) < look:
			ti += 1
		while ti > ci + 1 and not clear_line(p, pts[ti]):
			ti -= 1                                 # (never aim across a corner of something: the nearer point)
		var aim: Vector2 = pts[ti] if ti < pts.size() - 1 else goal
		if aim.distance_to(p) < 0.05:
			aim = goal
		# (round 38, 06 #97) at a shut park gate, as a player would: E, and wait for it to swing open (stepping back
		# out of its way if it swings towards her: the side gates open outwards)
		var gw: String = String(m.nearest().get("what", ""))
		if m.where == "out" and gw.begins_with("gate_"):
			keys_off()
			m.input_key(KEY_E)
			var gtd: Dictionary = m.north.gates[gw.substr(5).to_int()]
			var gr_: Array = gtd.rect
			var gc := Vector2((gr_[0] + gr_[2]) / 2.0, (gr_[1] + gr_[3]) / 2.0)
			for _w in 240:
				await get_tree().physics_frame
				if gtd.get("held", false):
					drive((here2() - gc).normalized())
				else:
					keys_off()
				if float(gtd.f) >= 1.0:
					break
			keys_off()
			check_t = 0.0
			continue
		drive((aim - p).normalized())
		check_t += dt
		if check_t > 3.5:                       # (pressed against someone she slips past after 2.2 s: give it that)
			if p.distance_to(check_p) < 0.6:
				stopped_by = what_stops() + " [keys %s, speed %.1f, heading %.0f°, aiming %.1f m off at %.0f°, route point %d of %d]" % [
					m.vkeys.keys().map(func(k): return OS.get_keycode_string(k)), m.speed, rad_to_deg(atan2(m.move_dir.x, -m.move_dir.y)),
					aim.distance_to(p), rad_to_deg(atan2(aim.x - p.x, -(aim.y - p.y))), ti, pts.size()]
				return 0
			check_t = 0.0
			check_p = p
		if total > limit:
			return 0
	return 0


func clear_line(a: Vector2, b: Vector2) -> bool:
	# nothing in the way between the two, on the map of where she fits
	var n := int(a.distance_to(b) / 0.2) + 1
	for i in range(1, n + 1):
		var q := a.lerp(b, float(i) / n)
		if m.where == "in":
			var rg: Array = room_grid(m.room)
			var c := Vector2i(roundi(q.x / rg[1]), roundi(q.y / rg[1]))
			if rg[0].is_in_boundsv(c) and rg[0].is_point_solid(c):
				return false
		elif grid.is_point_solid(cell_of(q)):
			return false
	return true


func what_stops() -> String:
	# in plain words: what she was pressing against, or the hill's rule (too steep to walk up)
	var names := []
	for i in m.player.get_slide_collision_count():
		var c = m.player.get_slide_collision(i).get_collider()
		if c and absf(m.player.get_slide_collision(i).get_normal().y) < 0.7:
			var nm: String = String(c.name)
			if c.get_parent():
				nm = String(c.get_parent().name) + "/" + nm
			var sh = m.player.get_slide_collision(i).get_collider_shape()
			if sh is CollisionShape3D and sh.shape is BoxShape3D:
				var gp: Vector3 = sh.global_position
				nm += " (a box %.1f x %.1f x %.1f m at %.1f, %.1f, %.1f)" % [sh.shape.size.x, sh.shape.size.y, sh.shape.size.z, gp.x, gp.y, gp.z]
			if not nm in names:
				names.append(nm)
	var p: Vector3 = m.player.global_position
	var steep := ""
	if m.where == "out" and m.north.gradient(p).length() > m.north.MAX_UP and not m.north.on_path(p):
		steep = "ground too steep to walk up (%.2f)" % m.north.gradient(p).length()
	var near := []
	for id in m.npcs.current():
		var q: Dictionary = m.npcs.current()[id]
		if not q.is_empty() and q.holder.visible and q.holder.global_position.distance_to(p) < 2.0:
			near.append(q.d.name)
	if m.where == "out":
		for w in m.people.people:
			if w.holder.visible and w.holder.global_position.distance_to(p) < 2.0:
				near.append("a passer-by")
		if m.street.own_bike != null and m.street.own_bike.visible and m.street.own_bike.global_position.distance_to(p) < 2.0:
			near.append("her parked bike")
	var rv: Vector3 = m.player.get_real_velocity()
	var want := Vector2(m.move_dir.x, m.move_dir.y) * 5.0
	var let: Vector2 = m.north.steer_on_slope(want, p, 0.016) if m.where == "out" else want
	var extra := " (moving at %.1f m/s; near her: %s; busy %s; at %.2f, %.2f the hill's rule turns a 5 m/s step into %.1f, %.1f)" % [Vector2(rv.x, rv.z).length(),
		", ".join(near) if not near.is_empty() else "no one", m.busy, p.x, p.z, let.x, let.y]
	if names.is_empty() and steep == "":
		return "nothing she was touching" + extra
	return "pressing against " + ", ".join(names) + (" and " if not names.is_empty() and steep != "" else "") + steep if not names.is_empty() else steep


func hop_on() -> void:
	if m.where != "out" or m.street.riding != null or not g.S.has_bike:
		return
	keys_off()
	await settle()
	m.input_key(KEY_B)
	await get_tree().create_timer(0.4).timeout


func hop_off() -> void:
	if m.street.riding == null:
		return
	keys({KEY_S: true})
	for i in 60:
		await get_tree().physics_frame
		if m.speed < 0.3:
			break
	keys_off()
	m.input_key(KEY_B)
	await get_tree().create_timer(0.4).timeout


func settle() -> void:
	keys_off()
	for i in 90:
		await get_tree().physics_frame
		if m.speed < 0.2:
			break


func travel(to: Vector2, arrive := 1.0, what := "") -> bool:
	# outdoors, a long way: on the bike once she has it (where bikes go), else on foot; up or down the hill by the
	# funicular when there's no walking way (the path's works) and she has the card for it
	if m.where == "out" and route(to).is_empty() and g.has_item("park_pass"):
		var N: Dictionary = m.north.N
		var top := Vector2(N.cable.door_top[0], N.cable.door_top[1])
		var low := Vector2(N.cable.door_low[0], N.cable.door_low[1])
		# (round 34: by which station she can walk to, not which is nearer as the crow flies — from Park Güell the top
		# station is nearer, and she was sent to ride down from a station she couldn't reach)
		var to_low := route(low).size()
		var to_top := route(top).size()
		var up: bool = to_low > 0 and (to_top == 0 or to_low < to_top)
		var door := low if up else top
		printerr("PLAY     (no way on foot: the funicular %s)" % ("up" if up else "down"))
		if not await travel_plain(door, 1.2, "the funicular"):
			return false
		if not await press_e_at(door, func(n): return n.get("act", "") == "north" and n.get("what", "") == ("cable_up" if up else "cable_down"), "the funicular"):
			return false
		for i in 400:
			await get_tree().create_timer(0.25).timeout
			if not m.cutscene and m.north.ride.is_empty() and not m.busy:
				break
		await read_on()
	return await travel_plain(to, arrive, what)


func travel_plain(to: Vector2, arrive := 1.0, what := "") -> bool:
	# (round 34: the bike only for a way that stays in the town — ridden up the hill path she drifted off its downhill
	# edge and slid below it, where the only way on was up the slope; a player leaves the bike at the bottom)
	var cr3: Array = m.D.city_rect
	var hill: bool = to.y < cr3[1] or here2().y < cr3[1]          # (north of the town: the hills, Gràcia, the park)
	if m.where == "out" and USE_BIKE and g.S.has_bike and here2().distance_to(to) > 70.0 and not hill:
		await hop_on()
		var ok: bool = await go(to, 4.0, what)
		await hop_off()
		if not ok:
			return false
	return await go(to, arrive, what)


func go_out() -> bool:
	if m.where != "in":
		return true
	var R: Dictionary = m.D.interiors[m.room]
	if R.exit == null:
		fail = "this room has no way out at the bottom"
		return false
	var ex := Vector2((R.exit[0] + R.exit[1]) / 2.0, R.h - 0.6)
	var ok: bool = await go(ex, 0.5, "the way out")
	if not ok and m.where == "in":
		return false
	for i in 240:
		if m.where == "out":
			break
		if m.free_cam():
			drive(Vector2(0, 1))
		else:
			keys({KEY_S: true})
		await get_tree().physics_frame
	keys_off()
	await get_tree().create_timer(1.0).timeout
	if m.where != "out":
		fail = "walked to the door of %s but didn't come out" % R.get("name", m.room)
		return false
	return true


func entrance_of(rid: String) -> Dictionary:
	var best := {}
	var bd := INF
	var p := here2()
	for e in m.D.entrances:
		if e.int == rid and e.get("room_side", "bottom") == "bottom":
			var d := p.distance_to(Vector2(e.pos[0], e.pos[1]))
			if d < bd:
				bd = d
				best = e
	return best


func go_in(rid: String) -> bool:
	if m.where == "in" and m.room == rid:
		return true
	if not await go_out():
		return false
	var e := entrance_of(rid)
	if e.is_empty():
		fail = "no door into %s" % rid
		return false
	var n := Vector2(e.normal[0], e.normal[1])
	var front := Vector2(e.pos[0], e.pos[1]) + n * 2.2
	if not await travel(front, 0.8, "the door of " + e.name):
		return false
	await settle()
	# and through the door, as a player walks in (round 34, the full run: a passer-by stood in Carrefour's doorway and
	# she pushed at them till the time ran out — as a player would, she steps back, lets them pass, and tries again)
	for attempt in 3:
		for i in 300:
			if m.where == "in":
				break
			if m.dlg_open:
				keys_off()
				await read_on()
				if e.get("lock", "") != "" and m.where == "out" and not g.unlocked(e.lock):
					break                                   # (locked, and no key: she stays out)
				continue
			# (round 34: at the door's middle, not straight ahead — arrived a metre to one side she walked into the
			# wall beside the bookshop's door)
			var dp := Vector2(e.pos[0], e.pos[1]) - here2()
			# (round 40, the user: a locked door is opened with E, never walked through: at it, she presses E)
			if e.get("lock", "") != "" and g.unlocked(e.lock) and dp.length() < 1.2 and i % 30 == 29:
				keys_off()
				m.input_key(KEY_E)
				await get_tree().create_timer(0.4).timeout
				continue
			drive(dp.normalized() if dp.length() > 0.3 else -n)
			await get_tree().physics_frame
		keys_off()
		if m.where == "in" or (e.get("lock", "") != "" and not g.unlocked(e.lock)):
			break
		for i in 40:
			drive(n)
			await get_tree().physics_frame
		keys_off()
		await get_tree().create_timer(3.0).timeout
	await get_tree().create_timer(1.0).timeout
	await read_on()
	if m.where != "in" or m.room != rid:
		fail = "walked at the door of %s but didn't go in" % e.name
		return false
	return true


# ------------------------------------------------------------------ talking and doing

func read_on(prefer: Array = [], buy := "") -> Array:
	# reads every page as it comes, answering a question with the first option whose words match one in prefer
	# (else the last, "no thanks", one); at a shop's counter buys `buy`, then leaves; returns what was said
	var said := []
	var quiet := 0
	while quiet < 4:
		await get_tree().create_timer(0.25).timeout
		if m.panels.is_open():
			quiet = 0
			match m.panels.kind:
				"shop":
					var stock: Array = g.shop_stock(m.panels.shop_id)
					var idx := -1
					for i in stock.size():
						if stock[i][0] == buy and not g.has_item(buy):
							idx = i
					if idx >= 0 and int(g.S.money) >= int(stock[idx][1]):
						m.panels.sel = idx
						m.panels.key(KEY_ENTER)
						said.append("[bought %s]" % buy)
						buy = ""
					else:
						m.panels.key(KEY_ESCAPE)
				_:
					m.panels.key(KEY_ESCAPE)
			continue
		if not m.dlg_open:
			if g.q.is_empty() and not m.busy:
				quiet += 1
			continue
		quiet = 0
		said.append("%s: %s" % [m.dlg_who.text, m.dlg_text.text.left(90)])
		if m.choice_box.visible:
			var pick: int = m.dlg_choices.size() - 1
			# (round 40: the funicular's turnstile asks — she rides when she came to ride)
			for want in prefer + ["ride up", "ride down"]:
				for i in m.dlg_choices.size():
					if String(want).to_lower() in String(m.dlg_choices[i]).to_lower():
						pick = i
						break
				if pick != m.dlg_choices.size() - 1:
					break
			said.append("  -> " + String(m.dlg_choices[pick]))
			m.input_key(KEY_1 + pick)
		else:
			m.input_key(KEY_E)
	return said


func press_e_at(at: Vector2, want: Callable, what: String, prefer: Array = [], buy := "") -> bool:
	# walks up to it, and when the game offers it, presses E and reads on
	if not await approach(at, want, what):
		return false
	m.input_key(KEY_E)
	var said: Array = await read_on(prefer, buy)
	for l in said:
		printerr("PLAY       " + l)
	return true


func approach(at: Vector2, want: Callable, what: String) -> bool:
	# walks up to it until the game offers it (the prompt a player would see)
	for attempt in 6:
		var n: Dictionary = m.nearest()
		if not n.is_empty() and want.call(n):
			await settle()
			n = m.nearest()
			if not n.is_empty() and want.call(n):
				return true
		var d := here2().distance_to(at)
		if attempt == 0 or d > 4.0:
			if not await go(at, 0.9 if attempt < 2 else 0.6, what) and here2().distance_to(at) > 4.0:
				return false
			await settle()
			continue
		# (round 35's fourth play-through: Trufa trotted right into her — at 0 m the game can't tell which way she
		# faces it, and offered nothing. A player steps back a pace and turns to it.)
		if d < 0.6:
			var away := (here2() - at).normalized() if d > 0.01 else Vector2(1, 0)
			for i in 20:
				drive(away)
				await get_tree().physics_frame
			await settle()
		# close, but not offered: towards it until the prompt comes up, or something (a gate, a counter) stops her
		for i in 50:
			drive((at - here2()).normalized())
			await get_tree().physics_frame
			var n3: Dictionary = m.nearest()
			if not n3.is_empty() and want.call(n3):
				break
		await settle()
	var n2: Dictionary = m.nearest()
	var spot := "somewhere she can stand"
	if m.where == "out" and grid.is_point_solid(cell_of(at)):
		var c := free_near(grid, cell_of(at), 40)
		spot = "where she can't stand (the nearest she fits is %.1f m off)" % cell_pos(c).distance_to(at) if c.x >= 0 else "where she can't stand"
	fail = "she got to within %.1f m of %s, which lies %s, but the game didn't offer it (it offered %s)" % [here2().distance_to(at),
		what, spot, "\"%s\"" % n2.label if not n2.is_empty() else "nothing"]
	return false


func who_of(w: String, k: String) -> String:
	return String(g.data.MISSIONS[k].get("giver", "")) if w == "giver" else w


func person_at(id: String) -> Array:
	# [room or "world", where they are now (in a room: from its corner)]
	var at: Array = g.data.NPCS[id].at
	var rid: String = at[0]
	var q: Dictionary
	if rid == "world":
		q = m.npcs.outdoor.get(id, {})
	elif m.where == "in" and m.room == rid:
		q = m.npcs.indoor.get(id, {})
	if not q.is_empty():
		var p: Vector3 = q.holder.global_position - (m.room_base(rid) if rid != "world" else Vector3.ZERO)
		return [rid, Vector2(p.x, p.z)]
	if rid == "world":
		var w: Vector3 = g.world_pos(at[1], at[2])
		return [rid, Vector2(w.x, w.z)]
	return [rid, Vector2(at[1], at[2])]


func talk(id: String, prefer: Array = [], buy := "") -> bool:
	var pa := person_at(id)
	if pa[0] == "world":
		if not await go_out():
			return false
		if not await travel(pa[1], 3.0, g.data.NPCS[id].name):
			return false
	else:
		if not await go_in(pa[0]):
			return false
	pa = person_at(id)
	var at: Vector2 = pa[1]
	if m.where == "in":
		at += Vector2(0, 1.5)                  # (indoors: in front of them, on the door's side of any counter)
	# (buying, the counter does as well as the keeper: it's what a player standing at it is offered)
	var want := func(n): return (n.get("act", "") == "npc" and n.get("who", "") == id) or (buy != "" and n.get("act", "") == "thing" and n.th.get("kind", "") == "counter")
	return await press_e_at(at, want, g.data.NPCS[id].name, prefer, buy)


func pick(gi: Dictionary) -> bool:
	if not await go_out():
		return false
	var at := Vector2(gi.pos.x, gi.pos.z)
	if not await travel(at, 2.5, g.item(gi.id).name):
		return false
	return await press_e_at(at, func(n): return n.get("act", "") == "pick" and n.g.key == gi.key, g.item(gi.id).name)


func nearest_ground(id: String) -> Dictionary:
	var best := {}
	var bd := INF
	var p := here2()
	for gi in g.ground:
		if gi.id == id and gi.node.visible:
			var d: float = p.distance_to(Vector2(gi.pos.x, gi.pos.z)) + (0.0 if m.where == "out" else 50.0)
			if d < bd:
				bd = d
				best = gi
	return best


func use_thing(clue: String) -> bool:
	# a thing in a room (the card on her desk, the dust in the Hypostyle Room, the crate): the room it's in, then E
	for rid in m.D.interiors:
		for th in m.D.interiors[rid].things:
			if th.get("clue", "") == clue or (clue == "card" and th.get("card", false)):
				if not await go_in(rid):
					return false
				return await press_e_at(Vector2(th.pos[0], th.pos[1]), func(n): return n.get("act", "") == "thing" and n.th == th, "the " + clue)
	fail = "nothing called %s anywhere" % clue
	return false


func shop_of(id: String) -> Array:
	for sid in g.data.SHOPS:
		for e in g.data.SHOPS[sid].items:
			if e[0] == id:
				return [sid, int(e[1])]
	return []


func keeper_of(sid: String) -> String:
	for id in g.data.NPCS:
		if g.data.NPCS[id].at[0] == sid and g.data.NPCS[id].get("shop", false):
			return id
	return ""


func get_item(id: String, n := 1) -> bool:
	var sh := shop_of(id)
	if not sh.is_empty():
		if int(g.S.money) < sh[1]:
			if not await earn(sh[1] - int(g.S.money)):
				return false
		if not await talk(keeper_of(sh[0]), [], id):
			return false
		if not g.has_item(id):
			fail = "she talked to the shopkeeper with %s in her purse but didn't come away with it" % g.money(g.S.money)
			return false
		return true
	if HANDS.has(id):
		if not await talk(HANDS[id]):
			return false
		if not g.has_item(id):
			fail = "%s didn't hand it over" % g.data.NPCS[HANDS[id]].name
			return false
		return true
	for cid in g.S.cont:
		for e in g.S.cont[cid]:
			if e.id == id:
				return await take_from(cid, id)
	while g.count_item(id) < n:
		var gi := nearest_ground(id)
		if gi.is_empty():
			fail = "there's no %s left to find (she has %d of %d)" % [g.item(id).name, g.count_item(id), n]
			return false
		if not await pick(gi):
			return false
		await read_on()
	return true


func take_from(cid: String, id: String) -> bool:
	for rid in m.D.interiors:
		for th in m.D.interiors[rid].things:
			if th.get("c", "") == cid:
				if not await go_in(rid):
					return false
				if not await approach(Vector2(th.pos[0], th.pos[1]), func(n): return n.get("act", "") == "thing" and n.th == th, "the cupboard"):
					return false
				m.input_key(KEY_E)
				# (what she sees first, "Behind a folded jacket…", then the shelves)
				for i in 30:
					await get_tree().create_timer(0.25).timeout
					if m.panels.is_open():
						break
					if m.dlg_open:
						printerr("PLAY       %s: %s" % [m.dlg_who.text, m.dlg_text.text.left(90)])
						m.input_key(KEY_E)
				if m.panels.is_open() and m.panels.kind == "container":
					var lst: Array = g.S.cont[cid]
					for i in lst.size():
						if lst[i].id == id:
							m.panels.col = 0
							m.panels.sel = i
							m.panels.key(KEY_ENTER)
							break
					await get_tree().create_timer(0.4).timeout
					await read_on()
				if not g.has_item(id):
					fail = "the cupboard opened but %s didn't come out of it" % g.item(id).name
					return false
				return true
	fail = "no cupboard in the game holds %s" % g.item(id).name
	return false


func earn(cents: int) -> bool:
	# short of money: what a player does — gather what can be sold back, and sell it
	printerr("PLAY     (short by %s: earning it)" % g.money(cents))
	var got := 0
	var plan := {}
	for id in BUYERS:
		got += g.count_item(id) * BUYERS[id][1]
	while got < cents:
		var best := {}
		var bd := INF
		for gi in g.ground:
			if gi.node.visible and (BUYERS.has(gi.id) or gi.id == "coin"):
				var v: float = (BUYERS[gi.id][1] if BUYERS.has(gi.id) else 100.0)
				var d: float = here2().distance_to(Vector2(gi.pos.x, gi.pos.z)) / v
				if d < bd:
					bd = d
					best = gi
		if best.is_empty():
			fail = "she needs %s more and there's nothing left to gather" % g.money(cents - got)
			return false
		var was: int = g.S.money
		if not await pick(best):
			return false
		got += BUYERS[best.id][1] if BUYERS.has(best.id) else int(g.S.money) - was
		if best.id == "coin":
			cents -= int(g.S.money) - was
			got -= int(g.S.money) - was
	for id in BUYERS:
		if g.count_item(id) > 0:
			if not await talk(BUYERS[id][0], ["return", "sell"]):
				return false
	return true


# ------------------------------------------------------------------ the steps

func do_step(k: String, s: String) -> bool:
	var w := s.split(" ")
	printerr("PLAY   %s (%s)" % [step_words(s, k), where_words()])
	match w[0]:
		"talk":
			var id := who_of(w[1], k)
			var prefer := ["sit the exam", "buy a ticket"]
			if k == "thief" and id == "manolo":
				return await catch_manolo()
			return await talk(id, prefer)
		"get":
			return await get_item(w[1], int(w[2]) if w.size() > 2 else 1)
		"use":
			return await use_thing(w[1])
		"in":
			return await go_in(w[1])
		"inout":
			return await in_and_out()
		"ticket":
			if m.north.park_open():
				return true
			if int(g.S.money) < 300 and not await earn(300 - int(g.S.money)):
				return false
			return await talk(ticket_seller(), ["buy a ticket"])
		"trufa":
			var tr: Node3D = m.street.trufa
			if not await travel(Vector2(tr.position.x, tr.position.z), 2.0, "Trufa"):
				return false
			return await press_e_at(Vector2(tr.position.x, tr.position.z), func(n): return n.get("act", "") == "trufa", "Trufa")
		"robbed":
			return await robbed()
		"shut":
			return await cellar_shut()
	fail = "the test doesn't know the step \"%s\"" % s
	return false


func ticket_seller() -> String:
	for id in g.data.NPCS:
		if g.data.NPCS[id].get("park_tickets", false):
			return id
	return "jaume"


func in_and_out() -> bool:
	# the nearest door she can walk through, in and out again
	var best := {}
	var bd := INF
	for e in m.D.entrances:
		if e.get("lock", "") != "" or e.get("room_side", "bottom") != "bottom":
			continue
		var d := here2().distance_to(Vector2(e.pos[0], e.pos[1]))
		if d < bd:
			bd = d
			best = e
	if not await go_in(best.int):
		return false
	await read_on()
	return await go_out()


func robbed() -> bool:
	# Manolo's patter: talked to with something in her bag he fancies, he helps himself; she notices further on
	if g.S.inv.filter(func(e): return not g.is_quest_item(e.id) and not g.is_book(e.id) and not g.is_clothes(e.id)).is_empty():
		if not await get_item("apple"):
			return false
	if not await talk("manolo"):
		return false
	if g.S.pending == null and g.S.stolen.is_empty():
		fail = "Manolo talked but took nothing"
		return false
	# on about her day: 40 m off, down the Rambla, and the bag feels lighter
	var p := here2()
	var away := p + Vector2(0, 40.0 if p.y < 60.0 else -40.0)
	await go(away, 2.0, "on down the Rambla")
	for i in 20:
		if g.S.pending == null:
			break
		await get_tree().create_timer(0.25).timeout
	await read_on()
	if g.S.stolen.is_empty():
		fail = "she was never told anything was stolen"
		return false
	return true


func catch_manolo() -> bool:
	# with the agent close behind her (he follows her), back to Manolo, and talk to him as if nothing had happened
	if not await talk("manolo"):
		return false
	for i in 40:
		await read_on()
		if g.m_done("thief"):
			return true
		await get_tree().create_timer(0.5).timeout
	fail = "Manolo was talked to with Agent Bofarull %s m behind, but he wasn't caught" % ("%.0f" % m.npcs.outdoor.bofarull.holder.global_position.distance_to(m.player.global_position))
	return false


func cellar_shut() -> bool:
	# (before the key: the cellar door must stay shut to a player who walks at it)
	if g.has_item("cellar_key"):
		return true
	if not await go_out():
		return false
	var e := entrance_of("int_trias_cellar")
	var n := Vector2(e.normal[0], e.normal[1])
	if not await travel(Vector2(e.pos[0], e.pos[1]) + n * 2.2, 0.8, "the cellar door"):
		return false
	await settle()
	for i in 120:
		if m.where == "in" or m.dlg_open:
			break
		drive(-n)
		await get_tree().physics_frame
	keys_off()
	await get_tree().create_timer(1.0).timeout
	if m.where == "in" and m.room == "int_trias_cellar":
		fail = "she walked straight into the locked cellar without the key"
		await go_out()
		return false
	await read_on()
	return true
