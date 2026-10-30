# Passers-by: people walking up and down the pavements, the park paths and the promenade, where
# build_assets.py left room for them (scene.json "people": stretches from a to b, metres).
# Each is one of the generic Meshy people (a man, a woman, an older man, an older woman, a child),
# made and dressed the same way as the 2D game's people (npcs.gd), in colours picked at random, so
# no two look quite alike. They pause at the ends, wait if Sandra is in their way, and say hello if
# she talks to them.
extends Node

const CROSSERS := 6              # (round 41) people who cross at the zebras, stopping to look both ways
const LOOK_T := 2.7              # (seconds at the kerb: left, right, then straight ahead)
const MAX_PEOPLE := 37           # (round 20: the city wanted busier streets; the 2D game's sixty people are about as well)
                                 # (round 40: seven more, the ones taken out of the park, north.gd park_people)
const WALK_ANIM_SPEED := 1.05    # m/s the Meshy "Walking" animation is made for

const TOPS := ["#2f4f6f", "#6b4a33", "#7a2a3a", "#4a6b3a", "#5a5a62", "#8a6a9a", "#c8322e", "#e07b39", "#d8c9a8", "#3a8a8a"]
const LEGS := ["#2f3a5a", "#3c3b45", "#6b4226", "#2d2a2a", "#8a8378", "#4a6a8a", "#e8dccb"]
const HAIR := ["#2b1d17", "#191315", "#5b3a24", "#7b4a2a", "#a4532c", "#d8b064"]
const GREY := ["#a9a39b", "#e6e1d8"]
const HELLOS := ["Bon dia!", "Hola, bona tarda!", "(A smile and a nod in passing.)", "Quina calor, eh?",
	"(Humming something. It might be Rosalía.)", "Adéu, maca!", "(On the phone: \"...i després vam anar a la platja...\")",
	"Perdona — do you know where the Sagrada Família is? ...Never mind, I'll follow the tourists."]
# (round 40, the user: "all of the people in the park just say their very brief Catalan or Spanish greetings"; rule 10 #6)
const PARK_HELLOS := ["Bon dia!", "Hola, bona tarda!", "¡Buenas!", "(A smile and a nod in passing.)", "Adéu, maca!", "Hola!"]
# (round 40, the user: the seven moved out of the park into the city "need to have proper dialogue about the world and
# Barcelona and Spain. The world specifically that the game is set in"; rule 10 #6) three lines each, in turn
const CITY_TALK := [
	["Erasmus at Pompeu Fabra? Revise in the library in the old reservoir by the Ciutadella. Everyone does, the week before exams.",
		"You live on Flor de Lliri? Lovely little street. Proper Eixample: high ceilings, and two bakeries on your corner.",
		"Lunch at two, dinner at ten. You'll get used to it. My German neighbour never did."],
	["On Sant Jordi, the 23rd of April, everyone gives a book and a rose. The whole city turns into a bookshop.",
		"In September it's La Mercè: giants, fire-runners and human towers. Wear old clothes for the correfoc.",
		"The castellers build human towers ten people high. The littlest child climbs to the top and waves. My heart stops every time."],
	["Barceloneta beach was railway yards and warehouses before the '92 Olympics. Now look at it.",
		"Before the Olympics this city turned its back on the sea. Now we can't keep away from it.",
		"Swim in the morning, before everyone else wakes up. The water's like glass."],
	["Start with 'bon dia' and people will love you. Here we switch between Catalan and Spanish in the middle of a sentence.",
		"Catalan isn't a kind of Spanish, whatever your guidebook says. Try telling someone in Gràcia that.",
		"'Gràcies' in Catalan, 'gracias' in Spanish. Mix them up and nobody minds. Much."],
	["The Sagrada Família has been building since 1882. My grandfather swore it would never be finished. We'll see.",
		"Gaudí was knocked down by a tram in 1926. He dressed so plainly that people took him for a beggar.",
		"Every corner in the Eixample is cut off at an angle, so each crossing is a little square. Look next time."],
	["A menú del dia: three courses, bread and a drink, for less than a sandwich costs in most of Europe. Find one near your faculty.",
		"Pa amb tomàquet: bread, tomato, olive oil, salt. That's all. Don't let anyone put anything else on it.",
		"Churros and thick chocolate in winter, orxata in summer. Those are the rules."],
	["If you get a free weekend, take the train to Montserrat. The monastery sits in a mountain of stone fingers.",
		"The whole country slows down in August. Half my street goes to the coast and the other half complains about the heat.",
		"Up on Tibidabo there's a funfair older than my great-grandmother. The view from the wheel is the whole city."],
]

var main: Node3D
var people: Array = []
var rng := RandomNumberGenerator.new()
var blockers: Array = []         # Vector3(x, z, radius): café tables, benches, trees, lamps and the like, to walk round
const STEP := 0.4                # (metres between the samples of a walker's way round things)
const THING_R := {"bench": 0.8, "bin": 0.35, "terrace": 1.0, "umbrella": 0.5, "kiosk": 1.6, "stall": 1.3, "fountain": 2.6,
	"sign": 0.3, "lampR": 0.2, "bikestand": 0.9}


func setup(m: Node3D) -> void:
	main = m
	rng.seed = 314
	for o in main.D.obstacles:
		blockers.append(Vector3(o.pos[0] + o.off[0], o.pos[1] + o.off[1], o.r))
	var wood := {}
	for tr in main.D.get("forest_trees", []):
		wood[Vector2(tr[0], tr[1])] = true
	for tr in main.D.trees:
		if not wood.has(Vector2(tr[0], tr[1])):              # (the wood's thousands of trunks: main.near_trunk())
			blockers.append(Vector3(tr[0], tr[1], 0.35))
	for l in main.D.lamps:
		blockers.append(Vector3(l.pos[0], l.pos[1], 0.2))
	# (round 35, the everything-visit: a passer-by walked through a rack of parked bikes by a shutter)
	for bk in main.D.get("street_life", {}).get("bikes", []):
		blockers.append(Vector3(bk.pos[0], bk.pos[1], 0.55))
	for th in main.D.get("things2d", []):
		if THING_R.has(th.type):
			blockers.append(Vector3(th.pos[0], th.pos[1], THING_R[th.type]))
	var stretches: Array = main.D.get("people", [])
	var order := range(stretches.size())
	for i in range(order.size() - 1, 0, -1):          # a fixed shuffle, so the busy streets vary
		var j := rng.randi_range(0, i)
		var tmp = order[i]
		order[i] = order[j]
		order[j] = tmp
	for k in mini(MAX_PEOPLE, order.size()):
		var st = stretches[order[k]]
		add_person(random_look(), Vector3(st.a[0], 0, st.a[1]), Vector3(st.b[0], 0, st.b[1]))
	# (round 41, the user: "It's fine if they're crossing the street at crosswalks… as long as they stop, look left and
	# right, and then cross") a few people whose way crosses a road by a zebra: along the pavement, to the kerb, a stop to
	# look both ways, over, and on along the far pavement; back the same way
	var zs: Array = main.D.get("zebras", [])
	var zo := range(zs.size())
	for i in range(zo.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var tmp = zo[i]
		zo[i] = zo[j]
		zo[j] = tmp
	for k in mini(CROSSERS, zo.size()):
		var z: Dictionary = zs[zo[k]]
		var n0 := people.size()
		add_route(random_look(), [z.a2, z.a, z.b, z.b2])
		if people.size() > n0:
			var w: Dictionary = people[people.size() - 1]
			w.stops = [[float(w.cum[1]), 1], [float(w.cum[2]), -1]]     # (the kerb they step off, going each way)
	# (round 36, the user: at the café terrace "maybe have someone sitting there") people sitting at café tables
	# (scene.json "sitters": where, and which way they face): the seated model, sitting still
	for st in main.D.get("sitters", []):
		add_sitter(Vector3(st.pos[0], 0, st.pos[1]), float(st.get("yaw", 0.0)))


const SIT_HIPS := Vector3(0.2, 0.0, -0.56)   # montse.glb Chair_Sit_Idle_F: her hips from her feet, metres


func add_sitter(pos: Vector3, yaw: float) -> void:
	# Montse's model sits by default: an older woman in a colour of her own, at her table
	var cl := next_clothes()
	var look := {"top": cl[0], "legs": cl[1], "hair": pick(GREY), "hs": "bun"}
	var holder := Node3D.new()
	main.outdoor.add_child(holder)
	var file := "montse.glb"                 # (round 38: the one model with a sitting animation)
	var sc: Node3D = main.npcs.scene_for(file)
	var m: Dictionary = main.load_meshy_sandra(file, holder, sc) if sc else {}
	if m.is_empty():
		holder.queue_free()
		return
	main.apply_look(m.mats, main.npcs.swaps_for(file, look))
	var ap: AnimationPlayer = m.ap
	if ap:
		ap.play(m.anims.idle)
	# (round 38, the user: "the lady is sinking into the ground") 'pos' is her chair's seat: the sitting animation carries
	# her hips 0.56 m back and 0.2 m to her left of the model's feet, so her feet go forward under the table until her
	# hips are over the seat, and stand on the paving
	holder.rotation.y = yaw
	pos -= holder.basis * SIT_HIPS
	pos.y = main.ground_at(pos)
	holder.position = pos
	for mat in m.mats:
		mat.set_shader_parameter("ground_y", pos.y)          # (her colours by height above her feet: npcs.swaps_for)
	var body := StaticBody3D.new()
	body.collision_layer = main.LAYER_BODY
	body.collision_mask = 0
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.3
	cap.height = 1.2
	cs.shape = cap
	cs.position = Vector3(SIT_HIPS.x, 0.6, SIT_HIPS.z)
	body.add_child(cs)
	holder.add_child(body)


func pick(list: Array) -> String:
	return list[rng.randi() % list.size()]


var dealt := 0


func next_clothes() -> Array:
	# (round 41, the user: everyone in different coloured clothes) the street's colours are dealt in turn from the
	# world's own spread (remap3d.py WALKER_LOOKS: none matches another or any named person), not picked at random
	var deck: Array = main.game.data.get("WALKER_LOOKS", []) if main.game else []
	if deck.is_empty():
		return [pick(TOPS), pick(LEGS)]
	dealt += 1
	return deck[(dealt - 1) % deck.size()]


func random_look() -> Dictionary:
	# a look in the 2D game's terms, for npcs.gd to turn into a model and its colours
	var old := rng.randf() < 0.25
	var cl := next_clothes()
	var look := {"top": cl[0], "legs": cl[1], "hair": pick(GREY) if old else pick(HAIR)}
	var r := rng.randf()
	if r < 0.45:
		look.hs = "short"
	elif r < 0.9 or old:
		look.hs = ["bun", "long", "bob", "ponytail"][rng.randi() % 4]
	else:
		look.hs = "ponytail"
		look.kid = true
	return look


func clear_end(a: Vector3, b: Vector3) -> Vector3:
	# a walk that would end on something (a pavement sign by a shop door): it ends short of it instead,
	# since the swerve round things can't bend the very ends of a walk
	var u := (b - a).normalized()
	for bl in blockers:
		var d := Vector2(bl.x - b.x, bl.y - b.z).length()
		if d < bl.z + 0.6:
			b -= u * (bl.z + 0.8 - d * 0.5)
	return b


func add_person(look: Dictionary, a: Vector3, b: Vector3) -> void:
	add_route(look, [a, b])


func add_route(look: Dictionary, way: Array, keep := 0.0, t0 := -1.0) -> void:
	# (round 39, the user: "NPCs should (generally) stick to paths and not walk through walls") a walker's way is a line
	# of points (a path's own centre line, bends and all), not only a straight stretch from a to b; 'keep' is how far to
	# the right of it they walk (as people keep right, so two coming the other way pass), t0 where along it they start
	var pts := PackedVector3Array()
	for q in way:
		var v := Vector3(q.x, 0.0, q.z) if q is Vector3 else Vector3(q[0], 0.0, q[1])
		if pts.is_empty() or v.distance_to(pts[pts.size() - 1]) > 0.05:
			pts.append(v)
	if pts.size() < 2:
		return
	var n := pts.size()
	pts[n - 1] = clear_end(pts[n - 2], pts[n - 1])
	pts[0] = clear_end(pts[1], pts[0])
	var cum := PackedFloat32Array([0.0])
	for i in range(1, n):
		cum.append(cum[i - 1] + pts[i - 1].distance_to(pts[i]))
	var holder := Node3D.new()
	main.outdoor.add_child(holder)
	var file: String = main.npcs.model_for(look)
	var sc: Node3D = main.npcs.scene_for(file)
	var m: Dictionary = main.load_meshy_sandra(file, holder, sc) if sc else {}
	if m.is_empty():
		holder.queue_free()
		return
	main.npcs.stand_tall(m, file)                            # (round 40: better posture, as every story character's)
	if look.get("kid", false) and file != "child.glb":
		sc.scale *= 0.72
	main.apply_look(m.mats, main.npcs.swaps_for(file, look))
	main.npcs.keep_face(file, m.mats, sc.scale.y)
	var ap: AnimationPlayer = m.ap
	if ap:
		for an in ["Walking", "Idle_4"]:
			if ap.has_animation(an):
				ap.get_animation(an).loop_mode = Animation.LOOP_LINEAR
		if ap.has_animation("Idle_4"):
			m.anims.idle = "Idle_4"                   # (Montse's model sits by default; passers-by stand)
		ap.play(m.anims.idle)
		ap.seek(rng.randf() * 2.0, true)
	var p := {"holder": holder, "m": m, "a": pts[0], "b": pts[n - 1], "pts": pts, "cum": cum, "L": maxf(0.5, cum[n - 1]),
		"t": t0 if t0 >= 0.0 else rng.randf(), "keep": keep, "dodge": 0.0, "wait_t": 0.0,
		"offs_f": way_round(pts, cum, keep), "offs_b": way_round(pts, cum, -keep), "dir": 1 if rng.randf() < 0.5 else -1,
		"speed": rng.randf_range(1.0, 1.4) * (0.8 if GREY.has(look.hair) else 1.0), "pause": 0.0, "moving": 0.0, "yaw": 0.0,
		"hello": rng.randi() % HELLOS.size(), "fwd": Vector3.ZERO}
	# so Sandra bumps into them rather than walking through
	var body := AnimatableBody3D.new()
	body.collision_layer = main.LAYER_BODY
	body.collision_mask = 0
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.24
	cap.height = 1.3
	cs.shape = cap
	cs.position.y = 0.65
	body.add_child(cs)
	holder.add_child(body)
	p["body"] = body
	people.append(p)
	place(p)


func mark_park(poly: PackedVector2Array) -> void:
	# (round 40, rule 10 #6) the walkers inside a park only greet; seven of the city's, spread through its streets, talk
	var city := []
	for p in people:
		var q: Vector3 = p.holder.position
		p.park = Geometry2D.is_point_in_polygon(Vector2(q.x, q.z), poly)
		if not p.park:
			city.append(p)
	for k in mini(CITY_TALK.size(), city.size()):
		var w: Dictionary = city[int(float(k) * city.size() / CITY_TALK.size())]
		w.talk = CITY_TALK[k]
		w.hello = 0


func remove_inside(poly: PackedVector2Array) -> void:
	# (round 39) the walkers whose way starts, ends or crosses the middle of an area (a park that places its own people
	# along its paths): gone
	for i in range(people.size() - 1, -1, -1):
		var p: Dictionary = people[i]
		var mid: Vector3 = (p.a + p.b) / 2.0
		for q in [p.a, p.b, mid]:
			if Geometry2D.is_point_in_polygon(Vector2(q.x, q.z), poly):
				p.holder.queue_free()
				people.remove_at(i)
				break


func frame(pts: PackedVector3Array, cum: PackedFloat32Array, s: float) -> Array:
	# where along a way s metres is, and the way's right-hand side there (from a towards b), the side eased round a bend
	# over a metre either side of it, so someone walking off the middle line doesn't jump at the corner
	var n := pts.size()
	var i := 0
	while i < n - 2 and s > cum[i + 1]:
		i += 1
	var seg: float = maxf(cum[i + 1] - cum[i], 0.001)
	var f := clampf((s - cum[i]) / seg, 0.0, 1.0)
	var c := pts[i].lerp(pts[i + 1], f)
	var u := (pts[i + 1] - pts[i]) / seg
	var side := Vector3(-u.z, 0, u.x)
	var to_end: float = cum[i + 1] - s
	var from_start: float = s - cum[i]
	if to_end < 1.0 and i < n - 2:
		var u2 := (pts[i + 2] - pts[i + 1]).normalized()
		side = side.lerp(Vector3(-u2.z, 0, u2.x), 0.5 * (1.0 - to_end)).normalized()
	elif from_start < 1.0 and i > 0:
		var u0 := (pts[i] - pts[i - 1]).normalized()
		side = side.lerp(Vector3(-u0.z, 0, u0.x), 0.5 * (1.0 - from_start)).normalized()
	return [c, side, u]


func way_round(pts: PackedVector3Array, cum: PackedFloat32Array, base := 0.0) -> PackedFloat32Array:
	# how far to the side of the way to walk (right of a→b, metres), every STEP metres along it: 'base' (keeping right),
	# swerving smoothly out and back round tables, chairs, benches, trees and lamps rather than through them
	var L: float = cum[cum.size() - 1]
	var n := int(L / STEP) + 2
	var offs := PackedFloat32Array()
	offs.resize(n)
	var dev := PackedFloat32Array()
	dev.resize(n)
	var cs := []
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for i in n:
		var fr: Array = frame(pts, cum, minf(i * STEP, L))
		cs.append(fr)
		lo = Vector2(minf(lo.x, fr[0].x), minf(lo.y, fr[0].z))
		hi = Vector2(maxf(hi.x, fr[0].x), maxf(hi.y, fr[0].z))
	for bl in blockers:
		if bl.x < lo.x - 3.0 or bl.x > hi.x + 3.0 or bl.y < lo.y - 3.0 or bl.y > hi.y + 3.0:
			continue
		var need: float = bl.z + 0.45                           # their radius and a person's
		var best := -1
		var bd := INF
		for i in n:
			var c: Vector3 = cs[i][0]
			var dd := Vector2(bl.x - c.x, bl.y - c.z).length_squared()
			if dd < bd:
				bd = dd
				best = i
		var fr2: Array = cs[best]
		var rel := Vector3(bl.x, 0, bl.y) - (fr2[0] as Vector3)
		var along := best * STEP + rel.dot(fr2[2])
		var across := rel.dot(fr2[1]) - base                   # (from where they'd walk)
		if along < -need or along > L + need or absf(across) >= need:
			continue
		var push := -(need - absf(across)) * (1.0 if across >= 0.0 else -1.0)
		if absf(across) < 0.05:
			push = -need                                    # dead ahead: round it on one side
		var reach := need + 1.2                             # start swerving a little before, back again after
		for i in n:
			var d := absf(i * STEP - along)
			if d < reach:
				var k := 1.0 if d < need * 0.6 else 0.5 + 0.5 * cos(PI * (d - need * 0.6) / (reach - need * 0.6))
				var v := push * k
				if absf(v) > absf(dev[i]):
					dev[i] = v
	for i in n:
		offs[i] = base + dev[i]
	return offs


func offset_at(p: Dictionary) -> float:
	var offs: PackedFloat32Array = p.offs_f if int(p.dir) > 0 else p.offs_b
	var f: float = p.t * float(p.L) / STEP
	var i := clampi(int(f), 0, offs.size() - 2)
	return lerpf(offs[i], offs[i + 1], clampf(f - i, 0.0, 1.0))


func blocked_at(q: Vector3, r: float) -> bool:
	# (npcs.gd) is anything solid within r of this spot?
	if main.near_trunk(q, r + 0.35):
		return true
	for bl in blockers:
		if Vector2(bl.x - q.x, bl.y - q.z).length() < bl.z + r:
			return true
	return false


func place(p: Dictionary, dt := 0.0) -> void:
	var fr: Array = frame(p.pts, p.cum, clampf(p.t, 0.0, 1.0) * float(p.L))
	var side: Vector3 = fr[1]
	# how far off the middle line: their side of it, round things, and stepping aside for someone (eased: at the end
	# of their way they cross to the other side of it as they turn back, not in one jump)
	var want: float = offset_at(p) + float(p.dodge) * float(p.dir)
	p.lat = want if dt <= 0.0 or not p.has("lat") else move_toward(float(p.lat), want, 1.2 * dt)
	var pos: Vector3 = (fr[0] as Vector3) + side * float(p.lat)
	pos += p.get("shove", Vector3.ZERO)                      # (round 37: pushed aside by her; main.gd shove_people)
	# (round 40, rule 10 #16a: no one ever walks through a wall) stepping aside, keeping to their side or pushed, never
	# into one: back towards their way's middle line until they fit
	if (absf(float(p.lat)) > 0.05 or (p.get("shove", Vector3.ZERO) as Vector3).length() > 0.05) and not main.person_fits(pos):
		var mid: Vector3 = fr[0]
		for k in [0.66, 0.33, 0.0]:
			var tr: Vector3 = mid + side * float(p.lat) * k
			if main.person_fits(tr):
				pos = tr
				p.lat = float(p.lat) * k
				p.shove = Vector3.ZERO
				break
	pos.y = main.ground_at(pos)
	var prev: Vector3 = p.holder.position
	p.holder.position = pos
	p.step = pos - prev
	p.fwd = (fr[2] as Vector3) * float(p.dir)
	p.right = side * float(p.dir)


func candidates(sp: Vector3) -> Array:
	var out := []
	for i in people.size():
		var q: Vector3 = people[i].holder.position
		out.append({"x": q.x, "z": q.z, "r": 1.4, "label": "Say hello", "act": "person", "who": i})
	return out


func greet(i: int) -> void:
	var p: Dictionary = people[i]
	p.pause = 1.0
	p.talking = 0.6                                        # stopped and turned to her until the talk box closes
	p.moving = 0.0
	var to: Vector3 = main.player.global_position - p.holder.position
	p.yaw = atan2(to.x, to.z)
	var lines: Array = PARK_HELLOS if p.get("park", false) else (p.talk if p.has("talk") else HELLOS)
	main.show_dialog("", [lines[int(p.hello) % lines.size()]])
	p.hello = (int(p.hello) + 1) % lines.size()


func give_way(p: Dictionary, here: Vector3, others: Array, dt: float) -> bool:
	# (round 39, the user: "These people walk into each other") two coming towards each other each step to their own
	# right and pass; someone standing in the way (a walker paused, a person at their post) is walked round, on the side
	# away from them; someone ahead going the same way is overtaken on the left, or followed if there's no room. Right in
	# front of someone, not yet round them: wait. Kept waiting four seconds (both hemmed in): turn back.
	var fwd: Vector3 = p.fwd
	var right: Vector3 = p.get("right", Vector3.ZERO)
	var lane: Vector3 = here - right * float(p.dodge)         # where they'd be without stepping aside
	var target := 0.0
	var go := true
	for o in others:
		if is_same(o[2], p):
			continue
		var rel: Vector3 = o[0] - lane
		if absf(rel.x) > 3.0 or absf(rel.z) > 3.0:
			continue
		rel.y = 0.0
		var ahead := rel.dot(fwd)
		var across := rel.dot(right)
		if ahead < -0.8 or ahead > 2.6 or absf(across) > 0.8:
			continue
		var ofw: Vector3 = o[1]
		var oncoming := ofw.dot(fwd) < -0.3
		var want := 0.0
		if oncoming:
			want = 0.55
		elif ofw.dot(fwd) > 0.3 and ahead > 0.0:
			want = -0.75 if ahead < 2.0 else 0.0
		else:
			want = -0.75 if across >= 0.0 else 0.75
		if want != 0.0 and blocked_at(lane + right * want, 0.3):
			want = -want if not oncoming and not blocked_at(lane - right * want, 0.3) else 0.0
		if absf(want) > absf(target):
			target = want
		var real: Vector3 = o[0] - here
		real.y = 0.0
		if real.dot(fwd) > 0.0 and real.dot(fwd) < 0.95 and absf(real.dot(right)) < 0.55:
			go = false
	p.dodge = move_toward(float(p.dodge), target, dt)
	if go:
		p.wait_t = 0.0
	else:
		p.wait_t = float(p.wait_t) + dt
		if p.wait_t > 4.0:
			p.wait_t = 0.0
			p.dir = -p.dir
			p.pause = rng.randf_range(0.5, 1.5)
	return go


func tick(dt: float) -> void:
	var sandra: Vector3 = main.player.global_position
	# everyone out walking or standing about, for the walkers to give way to: [where, which way they're going (nothing
	# if standing), who]
	var others: Array = []
	for q in people:
		if not q.get("far", false):
			others.append([q.holder.position, q.fwd if float(q.moving) > 0.3 else Vector3.ZERO, q])
	for id in main.npcs.outdoor:
		var nq: Dictionary = main.npcs.outdoor[id]
		if not nq.is_empty() and not nq.get("gone", false) and nq.holder.visible:
			others.append([nq.holder.position, Vector3.ZERO, nq])
	for p in people:
		var far: bool = p.holder.position.distance_squared_to(sandra) > 90.0 * 90.0
		if far != (p.get("far", false) as bool):
			p.far = far                                # out of sight: not drawn or animated
			p.holder.visible = not far
			if p.m.ap:
				if far:
					p.m.ap.pause()
				else:
					p.m.ap.play()
		if far:
			continue
		var len: float = p.L
		var dir: Vector3 = p.fwd
		var here: Vector3 = p.holder.position
		var go := true
		var stepping := float(p.get("shoved_t", 0.0)) > 0.0      # (round 37: pushed by her, stepping back)
		if stepping:
			p.shoved_t -= dt
			go = false
			if p.shoved_t <= 0.0 and p.has("after_face"):
				p.yaw = p.after_face                     # (round 38: pushed from behind, they turn to face her a moment)
				p.erase("after_face")
				p.pause = maxf(float(p.pause), 1.2)
				stepping = false
		elif p.has("shove") and (p.shove as Vector3).length() > 0.01 and here.distance_to(sandra) > 2.0:
			p.shove = (p.shove as Vector3).move_toward(Vector3.ZERO, 0.4 * dt)   # (drifting back to their way)
		if stepping:
			pass
		elif p.get("talking", -1.0) > -1.0:
			p.talking -= dt
			if not main.dlg_open and p.talking <= 0.0:
				# (round 38, the user: they stay facing her after the talk, and go on only once she walks away)
				var ts := sandra - here
				ts.y = 0.0
				if ts.length() > 2.5:
					p.talking = -1.0
				elif ts.length() > 0.2:
					p.yaw = atan2(ts.x, ts.z)
			go = false
		elif p.pause > 0.0:
			p.pause -= dt
			go = false
		else:
			# wait while Sandra is just in front of them
			var to := sandra - here
			to.y = 0.0
			if to.length() < 1.3 and to.normalized().dot(dir) > 0.4:
				go = false
			elif not give_way(p, here, others, dt):
				go = false
		p.moving = move_toward(p.moving, 1.0 if go else 0.0, dt * 3.0)
		if p.m.get("posture") != null:
			p.m.posture.arms_w = 1.0 - p.moving             # (round 41: arms forward standing, posture.gd)
		var s0: float = p.t * len
		p.t += p.dir * p.speed * p.moving * dt / len
		var s1: float = p.t * len
		for stp in p.get("stops", []):
			# (round 41) at the kerb, about to cross: stop and look left, then right, then go
			var sk: float = stp[0]
			if int(stp[1]) == int(p.dir) and ((p.dir > 0 and s0 < sk and s1 >= sk) or (p.dir < 0 and s0 > sk and s1 <= sk)):
				p.t = sk / len
				p.pause = LOOK_T
				p.look_t = LOOK_T
				break
		if p.t >= 1.0 or p.t <= 0.0:
			p.t = clampf(p.t, 0.0, 1.0)
			p.dir = -p.dir
			p.pause = rng.randf_range(1.0, 4.0)       # look in a shop window, then turn back
		place(p, dt)
		if stepping:
			p.yaw = p.shove_face
		elif p.moving > 0.3 and p.get("talking", -1.0) <= -1.0:
			var st: Vector3 = p.step
			if Vector2(st.x, st.z).length() > 0.0005:
				p.yaw = atan2(st.x, st.z)                # (along the way they're actually going, swerves and all)
			else:
				p.yaw = atan2(dir.x, dir.z)
		if float(p.get("look_t", 0.0)) > 0.0:
			p.look_t = float(p.look_t) - dt
			var base := atan2((p.fwd as Vector3).x, (p.fwd as Vector3).z)
			p.yaw = base + (0.9 if p.look_t > LOOK_T * 0.66 else (-0.9 if p.look_t > LOOK_T * 0.33 else 0.0))
		p.holder.rotation.y = lerp_angle(p.holder.rotation.y, p.yaw, 1.0 - exp(-6.0 * dt))
		var ap: AnimationPlayer = p.m.ap
		if ap:
			var want: String = "Walking" if (p.moving > 0.3 or stepping) and ap.has_animation("Walking") else p.m.anims.idle
			if want != "" and ap.current_animation != want:
				ap.play(want, 0.3)
			ap.speed_scale = p.speed / WALK_ANIM_SPEED if want == "Walking" else 1.0
		for mat in p.m.mats:
			mat.set_shader_parameter("ground_y", p.holder.position.y)
			mat.set_shader_parameter("root_pos", p.holder.position)
			mat.set_shader_parameter("root_right", p.holder.global_transform.basis.x.normalized())
