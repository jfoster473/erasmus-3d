# The north (round 22): what moves and what can be done up there (scene.json's "north", built by north_build.py).
#   the Giradabo   its rim turns, its gondolas hang level; a ride (Ramon, €1): the wheel slows to bring an empty
#                  gondola to the platform, the gate opens, Sandra steps in, the door closes, once round (a minute),
#                  out again
#   the Avió and the Carrusel turn
#   the funicular  two cars shuttle on the hillside track; with the Amic del Park card, a ride up or down (the ticket
#                  office is shut: without the card, the turnstile won't turn)
#   Park Güell's gates: shut until she has bought the ticket (Jaume, €3: a status, for good); then E opens one and it
#                  swings shut 6 s after she has gone; the path's barrier until it is open
#   the hillside   too steep to walk up (only the path climbs it); going down she can cut through, sliding where
#                  it is steepest
extends Node

const MAX_UP := 0.30             # rise per metre she can walk up, off the path (round 33: 0.27 → 0.30, so the park's lawns,
#                                  at most 0.28, are walked anywhere; the hill is steeper almost everywhere)
const SLIDE_AT := 0.55           # steeper than this, off the path, and she slides down it
const SLIDE_SPEED := 3.2
const WHEEL_TURN := 60.0         # seconds for the Giradabo to go once round
const GATE_SWING := 2.5          # (round 38, 06 #97) seconds for a park gate to swing open; it closes at half that speed
const GATE_WAIT := 6.0           # it closes 6 s after she has gone
const GATE_CLEAR := 2.5          # she has gone this far from the gateway; nearer, a closing gate opens again for her
const GATE_PASS := 0.6           # the gateway is solid until the leaves are this far open

var main: Node3D
var N: Dictionary = {}
var rim: Node3D
var gondolas: Array = []
var avio: Node3D
var carrusel: Node3D
var cabins: Array = []
var works: Array = []            # the path's barrier, its sign, the work site
var gates: Array = []            # Park Güell's gates: {rect, body, leaves, f (0 shut..1 open), want, away, held}
var gates_fit := false           # (round 38) the leaves lifted clear of the game's ground under their swing (fit_gates)
var barrier_body: StaticBody3D
var aside: Node3D                # (round 41, 10 #16d) the barriers pushed aside once the path is open
var aside_body: StaticBody3D
var wheel_a := 0.0               # the rim's turn (radians)
var wheel_speed := TAU / WHEEL_TURN
var cable_t := 0.0               # 0..1 along the track (car 0 up, car 1 down)
var talaia: Node3D = null
var cable_dir := 1.0
var cable_wait := 0.0
var ride := {}                   # what she's riding: {kind: "wheel"|"cable", ...}
var lantern_lights: Array = []   # (round 24) the hill path's lanterns' lights
var path_pts: Array = []         # [Vector3(x, h, z)] the path's centre line, for "on the path"
var path_cells := {}


func setup(m: Node3D) -> void:
	main = m
	N = main.D.get("north", {})
	if N.is_empty():
		return
	var root: Node = main.outdoor
	rim = root.find_child("WheelRim", true, false)
	for g in int(N.wheel.n):
		gondolas.append(root.find_child("WheelGondola_%d" % g, true, false))
	avio = root.find_child("AvioArm", true, false)
	talaia = root.find_child("TalaiaArm", true, false)
	carrusel = root.find_child("CarruselTop", true, false)
	for i in 2:
		cabins.append(root.find_child("CableCabin_%d" % i, true, false))
	# (round 41, the user: the car's glass "from the outside, it should appear black, but from the inside, it should
	# appear clear") one-sided: its faces look outwards, and from inside there is nothing to see but the view
	for gm in main.mats.get("FuniGlassOut", []):
		(gm as BaseMaterial3D).cull_mode = BaseMaterial3D.CULL_BACK
	# (round 41, the user: "add the window back in and make it a bit tinted… So you can see that there's a window there";
	# then "I still don't see the tint from the inside. Could you just put a black thing up and then fade it by 80%?")
	# the black layer just inside the glass (north_build.py FuniTint), 60% black: the world clearly darker through it
	for tm in main.mats.get("FuniTint", []):
		var tb := tm as BaseMaterial3D
		tb.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		tb.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		tb.cull_mode = BaseMaterial3D.CULL_DISABLED
		var ta := 0.6                               # (round 41, the user, shown 20% and 60%: "use dark")
		for a in OS.get_cmdline_user_args():          # (tests: --tint= tries another strength)
			if a.begins_with("--tint="):
				ta = float(a.substr(7))
		tb.albedo_color = Color(0, 0, 0, ta)
	# (round 41, the user: "for the workers building site, can you keep the items there after the mission has ended?"
	# the cones, the sand heap and the boards stay: only the barrier and its notice go once the path is open)
	for nm in ["PathWorks_Barrier", "PathWorks_Sign"]:
		var n := root.find_child(nm, true, false)
		if n:
			works.append(n)
	var b: Array = N.get("barrier", [])
	if b.size() == 4:
		barrier_body = main.static_body(main.LAYER_BODY)
		if not line_body(barrier_body, N.get("barrier_line", [])):
			main.add_box(barrier_body, Vector3((b[0] + b[2]) / 2.0, 2, (b[1] + b[3]) / 2.0), Vector3(b[2] - b[0], 4, b[3] - b[1]))
	aside = root.find_child("PathWorks_Aside", true, false)
	var ba: Array = N.get("barrier_aside", [])
	if ba.size() == 4:
		aside_body = main.static_body(main.LAYER_BODY)
		if not line_body(aside_body, N.get("barrier_aside_line", [])):
			main.add_box(aside_body, Vector3((ba[0] + ba[2]) / 2.0, 2, (ba[1] + ba[3]) / 2.0), Vector3(ba[2] - ba[0], 4, ba[3] - ba[1]))
	# (round 25: the main gate and the three side gates, Larrard, Carmel and Glòria; round 38, 06 #97: each one shut,
	# drawn shut and solid, until she has the park's ticket — every leaf built shut, GuellGate_<g>_<n>, its origin on
	# its hinge, and 'gate_leaves' says how far round it swings open)
	var grs: Array = N.park.get("gate_rects", [])
	var gls: Array = N.park.get("gate_leaves", [])
	for gi in grs.size():
		var gr: Array = grs[gi]
		var gb: StaticBody3D = main.static_body(main.LAYER_BODY)
		main.add_box(gb, Vector3((gr[0] + gr[2]) / 2.0, 2, (gr[1] + gr[3]) / 2.0), Vector3(gr[2] - gr[0], 4, gr[3] - gr[1]))
		var lv := []
		for l in (gls[gi] if gi < gls.size() else []):
			var ln: float = float(l.len)
			var hp := Vector2(l.hinge[0], l.hinge[1])
			var od := Vector2(l.open_dir[0], l.open_dir[1])
			var lb: StaticBody3D = main.static_body(0)             # (the leaf standing open: solid only then)
			var cs := CollisionShape3D.new()
			var sh := BoxShape3D.new()
			sh.size = Vector3(0.3, 4.0, ln)
			cs.shape = sh
			var mid := hp + od * ln / 2.0
			cs.transform = Transform3D(Basis(Vector3.UP, atan2(od.x, od.y)), Vector3(mid.x, 2.0, mid.y))
			lb.add_child(cs)
			lv.append({"node": root.find_child(String(l.name), true, false), "open": float(l.open), "body": lb, "a": hp, "b": hp + od * ln,
				"shut": atan2(od.x, od.y) - float(l.open), "len": ln, "foot": l.get("foot", [])})
		gates.append({"rect": gr, "body": gb, "leaves": lv, "f": 0.0, "want": false, "away": 0.0, "held": false})
	# (round 24) the path's railings and the ball glade's fences: thin walls along each stretch of rope (her body moves
	# at street level, the hill only lifts her model, so a wall at y 0-4 stops her anywhere on the hill)
	var rails: StaticBody3D = main.static_body(main.LAYER_BODY)
	for r in N.get("rails", []):
		var ra := Vector3(r[0], 2.0, r[1])
		var rb := Vector3(r[2], 2.0, r[3])
		var cs := CollisionShape3D.new()
		var sh := BoxShape3D.new()
		sh.size = Vector3(0.22, 4.0, ra.distance_to(rb) + 0.2)
		cs.shape = sh
		cs.transform = Transform3D(Basis(Vector3.UP, atan2(rb.x - ra.x, rb.z - ra.z)), (ra + rb) / 2.0)
		rails.add_child(cs)
	# (round 24) the path's lanterns: a small warm light under each after dark (north_build.py lantern()); (round 41)
	# and under each span of the funfair's fairy lights, softer and wider (rule 02 #33b: no really dark patch at the edges)
	for l in N.get("lanterns", []) + N.get("fairy", []):
		var fairy: bool = l in N.get("fairy", [])
		var ol := OmniLight3D.new()
		ol.position = Vector3(l[0], l[1] - 0.05, l[2])
		ol.light_color = Color(1.0, 0.8, 0.52) if fairy else Color(1.0, 0.78, 0.5)
		ol.omni_range = 8.0 if fairy else 7.0
		ol.set_meta("k", 0.7 if fairy else 1.3)
		ol.omni_attenuation = 1.4
		ol.light_energy = 0.0
		ol.shadow_enabled = false
		ol.visible = false
		main.outdoor.add_child(ol)
		lantern_lights.append(ol)
	var prev_v = null
	for p in N.get("path", []):
		var v := Vector3(p[0], p[2], p[1])
		path_pts.append(v)
		# (round 35, the play-through: its points lie up to 3.6 m apart, and halfway between two the edge of the path
		# was 1.8 m from either — not "on the path", so the slope rule held her by a steep bank there; filled in every
		# half metre)
		var fill := [v]
		if prev_v != null:
			var nf := int((prev_v as Vector3).distance_to(v) / 0.5)
			fill = []
			for k in range(1, nf + 2):
				fill.append((prev_v as Vector3).lerp(v, minf(1.0, float(k) / (nf + 1))))
		prev_v = v
		for fv in fill:
			var key := Vector2i(floori(fv.x / 6.0), floori(fv.z / 6.0))
			if not path_cells.has(key):
				path_cells[key] = []
			path_cells[key].append(fv)
	# (round 33: the park's footpaths are paths too — the slope rule let her up the Tibidabo path but not up these,
	# and the one to the Casa Museu rose 0.75 at its end; now graded, north.py, and climbed like any path)
	for line in N.get("park", {}).get("paths", []):
		for i in range(1, line.size()):
			var pa := Vector2(line[i - 1][0], line[i - 1][1])
			var pb := Vector2(line[i][0], line[i][1])
			var n := int(pa.distance_to(pb) / 0.5) + 1          # (round 35: every half metre, was every metre)
			for k in n + 1:
				var q2 := pa.lerp(pb, float(k) / n)
				var key2 := Vector2i(floori(q2.x / 6.0), floori(q2.y / 6.0))
				if not path_cells.has(key2):
					path_cells[key2] = []
				path_cells[key2].append(Vector3(q2.x, 0.0, q2.y))
	park_people()
	refresh()


# ------------------------------------------------------------------ Park Güell's people
# (round 39, the user: "Spread people out around the park more. In relevant places, e.g. one person in the big part in
# the middle with the colourful tiles… NPCs should (generally) stick to paths and not walk through walls.") The build
# gave the park three walkers going straight from one end of a path to the other, across the lawn by the wall: they are
# taken away, and people walk the paths themselves, bend by bend down their middle (keeping right, so two meeting pass),
# turning back short of the gates (round 40: five in all).
const PARK_KEEP := 0.35          # metres right of a path's middle line they walk
const GATE_SHORT := 2.5          # they turn back this far short of a gate


func park_people() -> void:
	var P: Array = N.get("park", {}).get("paths", [])
	if P.size() < 15 or main.people == null:
		return
	park_inside(Vector3.ZERO)                                 # (fills park_poly)
	main.people.remove_inside(park_poly)
	var sq: Array = N.park.get("square", [])
	# (round 40, the user: "there are way too many people in the park. Cut them down by over half. And move them around
	# the city.") five, was twelve: one up past the gardens and round the covered walk, one on the switchbacks, one on
	# the middle carriage road, one by Casa Trias, one across the square; the other seven walk the city's streets
	# (people.gd MAX_PEOPLE)
	var routes := [
		[joined([P[1], P[2], P[P.size() - 1], P[8]]), 1],     # up past the Austria Gardens, round the covered walk (the last), on east
		[joined([(P[4] as Array).slice(0, -1), P[5]]), 1],    # the switchbacks up to the Casa Museu, on to the covered walk's end
		[P[9], 1],                                            # the middle carriage road, over the Pont del Mig
		[joined([P[11], reversed(P[12])]), 1],                # from Casa Trias's path down and round the loop by it
	]
	if sq.size() >= 4:
		# the Plaça de la Natura (the Hypostyle's roof, the serpentine bench round its edge): one across it, well in
		# from the bench
		var cz: float = (float(sq[1]) + float(sq[3])) / 2.0
		routes.append([[[float(sq[0]) + 4.0, cz - 4.0], [float(sq[2]) - 4.0, cz - 4.0]], 1])
	for r in routes:
		var way: Array = short_of_gates(r[0])
		var n: int = r[1]
		for k in n:
			main.people.add_route(main.people.random_look(), way, PARK_KEEP if way.size() > 2 else 0.0,
				(k + 0.15 + main.people.rng.randf() * 0.5) / n)
	main.people.mark_park(park_poly)                     # (round 40: greetings in the park, real talk for seven in the city)


func reversed(a: Array) -> Array:
	var r := a.duplicate()
	r.reverse()
	return r


func joined(parts: Array) -> Array:
	# paths that meet end to end (or where one branches from the other's last bend), as one way
	var out := []
	for part in parts:
		for q in part:
			if out.is_empty() or Vector2(q[0], q[1]).distance_to(Vector2(out[-1][0], out[-1][1])) > 0.3:
				out.append(q)
	return out


func short_of_gates(way: Array) -> Array:
	# a way that ends at a gate stops GATE_SHORT before it (the gates open only for Sandra)
	var w := way.duplicate()
	for end in [0, 1]:
		if end == 1:
			w.reverse()
		var q: Array = w[0]
		var near := false
		for gr in N.park.get("gate_rects", []):
			if q[0] > gr[0] - 3.0 and q[0] < gr[2] + 3.0 and q[1] > gr[1] - 3.0 and q[1] < gr[3] + 3.0:
				near = true
		if near and w.size() >= 2:
			var cut := GATE_SHORT
			while w.size() >= 2:
				var a := Vector2(w[0][0], w[0][1])
				var b := Vector2(w[1][0], w[1][1])
				var L := a.distance_to(b)
				if L > cut + 0.5:
					var c := a.lerp(b, cut / L)
					w[0] = [c.x, c.y]
					break
				cut -= L
				w.pop_front()
		if end == 1:
			w.reverse()
	return w


func refresh() -> void:
	# what the story says: the path's works (until it's open); the park's gates move themselves (tick_gates)
	if N.is_empty():
		return
	var S: Dictionary = main.game.S
	var open_path: bool = S.flags.get("pathOpen", false)
	for n in works:
		n.visible = not open_path
	if barrier_body:
		barrier_body.process_mode = Node.PROCESS_MODE_DISABLED if open_path else Node.PROCESS_MODE_INHERIT
		barrier_body.collision_layer = 0 if open_path else main.LAYER_BODY
	if aside:
		aside.visible = open_path
	if aside_body:
		aside_body.process_mode = Node.PROCESS_MODE_INHERIT if open_path else Node.PROCESS_MODE_DISABLED
		aside_body.collision_layer = main.LAYER_BODY if open_path else 0


var park_poly := PackedVector2Array()


func park_inside(p: Vector3) -> bool:
	# (round 25: the park's wall is a polygon now, N.park.inner: a little inside it)
	if N.is_empty():
		return false
	if park_poly.is_empty():
		for q in N.park.get("inner", []):
			park_poly.append(Vector2(q[0], q[1]))
	return Geometry2D.is_point_in_polygon(Vector2(p.x, p.z), park_poly)


# ------------------------------------------------------------------ Park Güell's gates

func park_open() -> bool:
	# (round 38, 06 #97: "The ticket is not an item, it is like a status of the game") bought once from Jaume: for good
	return bool(main.game.S.flags.get("parkTicket", false))


func gate_near(gt: Dictionary, p: Vector3, pad: float) -> bool:
	var r: Array = gt.rect
	return p.x > r[0] - pad and p.x < r[2] + pad and p.z > r[1] - pad and p.z < r[3] + pad


func open_gate(gi: int) -> void:
	if gi < 0 or gi >= gates.size():
		return
	var gt: Dictionary = gates[gi]
	gt.away = 0.0
	if not gt.want:
		gt.want = true
		main.ambience.sfx("open")


func tick_gates(dt: float) -> void:
	# (06 #97, 04 #82) a gate opens for her (E, or buying the ticket) and swings shut slowly once she has been clear of
	# it for 6 s; back while it closes, it opens again: it never shuts on her
	var p: Vector3 = main.player.global_position
	var out_: bool = main.where == "out"
	if out_ and not gates_fit:
		fit_gates()
	for gt in gates:
		var near: bool = out_ and gate_near(gt, p, GATE_CLEAR)
		if out_ and gate_near(gt, p, 0.2) and gt.f < GATE_PASS:
			gt.want = true                         # (loaded or put down in the gateway itself: it stands open round her)
			gt.f = 1.0
		if gt.want:
			gt.away = 0.0 if near else gt.away + dt
			if gt.away >= GATE_WAIT:
				gt.want = false
		elif near and gt.f > 0.0 and (park_open() or park_inside(p)):
			gt.want = true                         # (back before it has shut)
			gt.away = 0.0
		var f0: float = gt.f
		var f_end: float = 1.0 if gt.want else 0.0
		# (round 38) a leaf never swings into her: standing where it has still to pass, it waits for her to step back
		var held: bool = f0 != f_end and out_ and swing_hits(gt, p, f_end)
		if held and not gt.held and gt.want:
			main.toast("Step back to let the gate swing open")
		gt.held = held
		if not held:
			gt.f = clampf(gt.f + dt / GATE_SWING * (1.0 if gt.want else -0.5), 0.0, 1.0)
		if f0 > 0.0 and gt.f == 0.0 and out_ and gate_near(gt, p, 30.0):
			main.ambience.sfx("door")              # (the latch, when she's near enough to hear it)
		place_gate(gt, p)


func swing_hits(gt: Dictionary, p: Vector3, f_to: float) -> bool:
	# would any of the gate's leaves, swinging from where they are to f_to, pass through her (0.5 m round her middle)?
	var her := Vector2(p.x, p.z)
	var e0: float = smoothstep(0.0, 1.0, float(gt.f))
	var e1: float = smoothstep(0.0, 1.0, f_to)
	for l in gt.leaves:
		var hp: Vector2 = l.a
		if her.distance_to(hp) > float(l.len) + 0.5:
			continue
		for k in 9:
			var a: float = float(l.shut) + float(l.open) * lerpf(e0, e1, k / 8.0)
			var tip: Vector2 = hp + Vector2(sin(a), cos(a)) * float(l.len)
			if Geometry2D.get_closest_point_to_segment(her, hp, tip).distance_to(her) < 0.5:
				return true
	return false


func fit_gates() -> void:
	# (round 38, the user: "make sure they don't open into the floor") the build stands each bar's foot 5 cm over the
	# highest ground its swing passes ('foot': [radius, height over the hinge's pivot]); should the game's own ground
	# (paving, a terrace's floor) stand higher anywhere under the swing, the whole leaf is lifted by that much more
	gates_fit = true
	for gt in gates:
		for l in gt.leaves:
			var nd: Node3D = l.node
			if nd == null or (l.foot as Array).is_empty():
				continue
			var base: float = nd.global_position.y
			var hp: Vector2 = l.a
			var need := 0.0
			for fr in l.foot:
				for k in 9:
					var a: float = float(l.shut) + float(l.open) * k / 8.0
					var q: Vector2 = hp + Vector2(sin(a), cos(a)) * float(fr[0])
					need = maxf(need, main.ground_at(Vector3(q.x, 0.0, q.y)) + 0.03 - (base + float(fr[1])))
			if need > 0.0:
				nd.global_position.y = base + need


func place_gate(gt: Dictionary, p: Vector3) -> void:
	var e: float = smoothstep(0.0, 1.0, float(gt.f))           # (slow off, slow in: a heavy iron gate)
	(gt.body as StaticBody3D).collision_layer = main.LAYER_BODY if gt.f < GATE_PASS else 0
	var her := Vector2(p.x, p.z)
	for l in gt.leaves:
		if l.node:
			(l.node as Node3D).rotation.y = float(l.open) * e
		# standing open, a leaf is solid where it stands (not while it swings, nor on her)
		var on_her: bool = Geometry2D.get_closest_point_to_segment(her, l.a, l.b).distance_to(her) < 0.7
		(l.body as StaticBody3D).collision_layer = main.LAYER_BODY if gt.f >= 1.0 and not on_her else 0


func on_steps(p: Vector3) -> bool:
	# (round 25) the park's side stairs: steeper than she walks up on open ground, but they're stairs
	# (round 32: 0.7 m round them, not 0.3 — the slope is read half a metre either side of her, so at 0.3 the steps'
	# own edge read as a cliff, and stepping onto the side stairs' first steps from the porch was refused)
	for r in N.get("park", {}).get("steps", []):
		if p.x >= r[0] - 0.7 and p.x <= r[2] + 0.7 and p.z >= r[1] - 0.7 and p.z <= r[3] + 0.7:
			return true
	return false


# ------------------------------------------------------------------ the hillside

func on_path(p: Vector3, margin := 0.4) -> bool:
	var w: float = float(N.get("path_w", 2.4)) / 2.0 + margin
	var key := Vector2i(floori(p.x / 6.0), floori(p.z / 6.0))
	for gx in [key.x - 1, key.x, key.x + 1]:
		for gz in [key.y - 1, key.y, key.y + 1]:
			for v in path_cells.get(Vector2i(gx, gz), []):
				if Vector2(v.x - p.x, v.z - p.z).length() < w:
					return true
	return false


func gradient(p: Vector3) -> Vector2:
	# the slope where she stands, read half a metre either side — (round 39, the user: "a place here that both I and
	# this guy got stuck in", on the bank beside the dragon stairs' wall) but never across a wall: there the side stairs'
	# porch, 1.6 m lower than the bank, read as a cliff at the wall's foot, so she slid into the wall and the bank behind
	# her was too steep to walk back up. Where a wall stands within the half metre, the slope is read on her side alone.
	var e := 0.5
	var h0: float = main.terrain_at(p.x, p.z)
	var g := Vector2.ZERO
	for ax in 2:
		var d := Vector3(e, 0, 0) if ax == 0 else Vector3(0, 0, e)
		var fw := not walled(p, d)
		var bw := not walled(p, -d)
		var hf: float = main.terrain_at(p.x + d.x, p.z + d.z) if fw else h0
		var hb: float = main.terrain_at(p.x - d.x, p.z - d.z) if bw else h0
		var span := (e if fw else 0.0) + (e if bw else 0.0)
		g[ax] = (hf - hb) / span if span > 0.0 else 0.0
	return g


func walled(p: Vector3, d: Vector3) -> bool:
	# is there a wall (anything built and solid: not a person) between here and d away?
	var q := PhysicsRayQueryParameters3D.create(Vector3(p.x, 0.5, p.z), Vector3(p.x + d.x, 0.5, p.z + d.z), main.LAYER_BODY)
	var hit := main.get_world_3d().direct_space_state.intersect_ray(q)
	return not hit.is_empty() and hit.collider is StaticBody3D


func at_doorstep(p: Vector3) -> bool:
	# (round 32's play-through: the Casa Museu Gaudí stands on a raised base, the ground rising steeply to its door, and
	# the slope stopped her 2 m out — too far to walk in or to be offered the door: Mercè, and her mission, were out of
	# reach.) The few metres before a door are its doorstep: walkable however the ground lies under them.
	for e in main.D.entrances:
		var n := Vector2(e.normal[0], e.normal[1])
		var rel := Vector2(p.x - e.pos[0], p.z - e.pos[1])
		var out := rel.dot(n)
		if out > -0.5 and out < 3.2 and absf(rel.dot(Vector2(n.y, -n.x))) < float(e.size[0]) / 2.0 + 1.0:
			return true
	return false


func line_body(body: StaticBody3D, ln: Array) -> bool:
	# (round 41: the works barriers stop her at themselves, not at a box round their slanting line) a thin wall along
	# [x0, z0, x1, z1], as deep as their feet
	if ln.size() != 4:
		return false
	var a := Vector3(float(ln[0]), 2.0, float(ln[1]))
	var e := Vector3(float(ln[2]), 2.0, float(ln[3]))
	var cs := CollisionShape3D.new()
	var sh := BoxShape3D.new()
	sh.size = Vector3(0.5, 4.0, a.distance_to(e) + 0.3)
	cs.shape = sh
	cs.transform = Transform3D(Basis(Vector3.UP, atan2(e.x - a.x, e.z - a.z)), (a + e) / 2.0)
	body.add_child(cs)
	return true


func steer_on_slope(v: Vector2, p: Vector3, dt: float) -> Vector2:
	# (main's physics, before she moves) out of doors on the hills: no walking up anything steeper than MAX_UP,
	# and on the steepest ground, off the path, she slides down it
	if N.is_empty() or main.where != "out" or not ride.is_empty():
		return v
	var cr: Array = main.D.get("city_rect", [-INF, -INF, INF, INF])
	if p.x >= cr[0] and p.x <= cr[2] and p.z >= cr[1] and p.z <= cr[3]:
		return v
	# (round 32's tests: walking EAST off the bridge she stood pinned mid-deck — under the deck the terrain
	# climbs out of the riverbed, and that buried "cliff" was eating her whole step. The deck is flat built
	# ground: no slope-steering on or just off it.)
	var br: Array = main.D.get("bridge_rect", [])
	if br.size() == 4 and p.x >= br[0] - 1.7 and p.x <= br[2] + 1.7 and p.z >= br[1] - 1.7 and p.z <= br[3] + 1.7:
		return v
	if at_doorstep(p):
		return v
	# (round 35, the user: "I walked right into the middle [of Casa Trias's portico] then could not go anywhere, just spin
	# around") a built floor (the 'flats': terraces, porches, landings, steps) is level or an even ramp, whatever the ground
	# grid does at its edges — measured across its back edge, the house's ground behind read as a cliff, the slide pushed
	# her into the back wall and the climb rule wouldn't let her walk out. On a floor the slope rule doesn't apply.
	for f in main.D.get("flats", []):
		if p.x >= f[0] and p.x <= f[2] and p.z >= f[1] and p.z <= f[3]:
			return v
	var g := gradient(p)
	var steep := g.length()
	if steep < 0.05:
		return v
	var up := g / steep
	var path := on_path(p) or on_steps(p)
	if v.length() > 0.05:
		var rise := v.normalized().dot(g)            # the slope she'd walk up, going this way
		# (round 34: on a path she climbs what the path climbs — but never a wall: the covered walk's lower walk runs
		# along the foot of the hill's 4 m retaining wall)
		# (round 35, PATH_RULES G1: no invisible walls in Park Güell — there she climbs anything she wouldn't slide
		# down; steeper ground has a low stone wall at its foot, north_build.py)
		var max_up: float = SLIDE_AT if park_inside(p) else MAX_UP
		# (round 40, the walk check of the funicular's track: on a slope a little too steep to climb straight up she
		# climbed it at an angle — the rise across it was under the limit — and zig-zagged up the whole hill to the track.
		# Off the paths, ground too steep to climb can't be climbed at any angle: only along it, or down)
		var too_steep := not path and steep > max_up and rise > 0.08
		if (rise > max_up and (not path or rise > 1.2)) or too_steep:
			var along := v.dot(up)
			if along > 0.0:
				v -= up * along                      # (the uphill part of her step is lost: she can go along it, or down)
	if steep > SLIDE_AT and not path:
		v -= up * SLIDE_SPEED * clampf((steep - SLIDE_AT) / 0.4 + 0.4, 0.4, 1.2)
	return v


# ------------------------------------------------------------------ every frame

func tick(dt: float) -> void:
	if N.is_empty():
		return
	if not scope.is_empty():
		tick_scope(dt)
	var t: float = main.t
	# the lanterns glow with the night, and only those near her are lit (each is a light to draw)
	var nk: float = float(main.P.get("nk", 0.0))
	var her: Vector3 = main.player.global_position
	for ol in lantern_lights:
		ol.visible = nk > 0.05 and main.where == "out" and Vector2(ol.position.x - her.x, ol.position.z - her.z).length() < 60.0
		ol.light_energy = float(ol.get_meta("k", 1.3)) * nk
	if avio:
		avio.rotation.y = t * 0.9                       # (round 41, the user: "the aeroplane… is going backwards")
	if talaia:
		talaia.rotation.y = sin(t * 0.12) * 1.1          # the arm swings its cabin out over the drop, and back
	if carrusel:
		carrusel.rotation.y = t * 0.55
	# the wheel
	wheel_a = fmod(wheel_a + wheel_speed * dt, TAU)
	place_wheel()
	# the funicular: shuttling, a pause at each end
	if ride.get("kind", "") != "cable":
		if cable_wait > 0.0:
			cable_wait -= dt
		else:
			cable_t += cable_dir * dt / float(N.cable.ride_s)
			if cable_t >= 1.0 or cable_t <= 0.0:
				cable_t = clampf(cable_t, 0.0, 1.0)
				cable_dir = -cable_dir
				cable_wait = 8.0
	place_cabins()
	# Park Güell's gates: opening for her, shutting 6 s after she's gone (round 38, 06 #97)
	tick_gates(dt)
	if not ride.is_empty():
		ride_tick(dt)


func gondola_pos(g: int) -> Vector3:
	var hub := Vector3(N.wheel.hub[0], N.wheel.hub[2], N.wheel.hub[1])
	var a := TAU * g / float(N.wheel.n) - PI / 2.0 + wheel_a
	return hub + Vector3(cos(a), sin(a), 0) * float(N.wheel.r)


func place_wheel() -> void:
	if rim:
		rim.rotation.z = wheel_a
	for g in gondolas.size():
		if gondolas[g]:
			gondolas[g].global_position = gondola_pos(g)


func loop_off(t: float) -> float:
	# the passing loop: how far a car stands off the line at t (the two cars take opposite sides)
	var lt: Array = N.cable.loop_t
	return float(N.cable.loop) * (smoothstep(float(lt[0]), float(lt[1]), t) - smoothstep(float(lt[2]), float(lt[3]), t))


# (round 41, the user: "This crashes into the building and maybe floor") at the bottom the car's lower end stood a metre
# inside the station's back wall: the cars' run starts this far up the track, the car's end just short of the wall;
# (round 41, the user: "Do we need to have it stop on the hill so it doesn't come down as far") 2.6: the whole car
# stands on the line's climb, past the bend at its foot, beside the stepped platform (north_build.py FuniPlatform,
# FUNI_CLEAR: the scene's cable 'clear', metres)
var cable_lo := -1.0              # (that, as a share of the track's length: worked out once)


func cable_point(t: float, side: float) -> Vector3:
	# a point on the funicular's track (built on the hillside's own climb), side -1/1 through the passing loop
	var pts: Array = N.cable.pts
	if cable_lo < 0.0:
		var L := 0.0
		for i in pts.size() - 1:
			L += Vector3(pts[i + 1][0] - pts[i][0], pts[i + 1][2] - pts[i][2], pts[i + 1][1] - pts[i][1]).length()
		cable_lo = float(N.cable.get("clear", 1.6)) / maxf(1.0, L)
	t = lerpf(cable_lo, 1.0, clampf(t, 0.0, 1.0))
	var f := clampf(t, 0.0, 1.0) * float(pts.size() - 1)
	var i := mini(int(f), pts.size() - 2)
	var a: Array = pts[i]
	var b: Array = pts[i + 1]
	var k := f - float(i)
	return Vector3(lerpf(a[0], b[0], k) + side * loop_off(t), lerpf(a[2], b[2], k), lerpf(a[1], b[1], k))


var cabin_bodies: Array = []      # (round 40) each car solid to her where it stands


func cutting_floor(x: float, z: float) -> float:
	# (round 41, the user: "press e to come in and out, especially when you are arriving and leaving. We want to avoid the
	# cutting through objects") the funicular's cutting, for the camera: within 3 m of the line, from the lower station
	# to the portal, the ground is the track's bed; elsewhere (and inside the portal, under the terrace) NAN: the hill's own
	var pts: Array = N.cable.get("pts", [])
	if pts.is_empty() or absf(x - float(pts[0][0])) > 3.0 or z > float(pts[0][1]) + 2.0 or z < float(pts[-1][1]) - 6.0:
		return NAN
	return rail_h(z) - 0.3                         # (and 6 m on into the portal's open mouth)


func rail_h(z: float) -> float:
	# the rails' height at z along the funicular's line (its points, north_build.py); near its top (where the last
	# stretches ease off into the portal) on up at the grade below, so a car standing there stays upright
	var pts: Array = N.cable.pts
	var n := pts.size()
	if z > float(pts[0][1]):
		return float(pts[0][2])                       # (below its foot the track runs level into the station)
	if z < float(pts[n - 3][1]):
		var a2: Array = pts[n - 4]
		var b2: Array = pts[n - 3]
		return float(b2[2]) + (float(b2[1]) - z) * (float(b2[2]) - float(a2[2])) / maxf(0.001, float(a2[1]) - float(b2[1]))
	for i in n - 1:
		var a: Array = pts[i]
		var b: Array = pts[i + 1]
		if float(b[1]) <= z and z <= float(a[1]):
			return lerpf(float(a[2]), float(b[2]), (float(a[1]) - z) / maxf(0.001, float(a[1]) - float(b[1])))
	return float(pts[n - 1][2])


func place_cabins() -> void:
	# the two counterbalanced cars slide along the track (round 40, the user: "It has vertical walls": built stepped for
	# the line's grade, north_build.py, so they are no longer tilted — and "she should not be able to walk into the cable
	# car… It should be a solid object": each has a body, at street level where hers is, moving with it)
	if cabins.size() != 2:
		return
	if cabin_bodies.is_empty():
		var cw: Array = N.cable.get("car", [0.9, 2.6])
		for ci in 2:
			var b := AnimatableBody3D.new()
			b.sync_to_physics = false
			b.collision_layer = main.LAYER_BODY
			b.collision_mask = 0
			var cs := CollisionShape3D.new()
			var sh := BoxShape3D.new()
			sh.size = Vector3(float(cw[0]) * 2.0 + 0.1, 4.0, float(cw[1]) * 2.0 + 0.1)
			cs.shape = sh
			cs.position.y = 2.0
			b.add_child(cs)
			main.outdoor.add_child(b)
			cabin_bodies.append(b)
	for ci in 2:
		if not cabins[ci]:
			continue
		var tt := cable_t if ci == 0 else 1.0 - cable_t
		var sd := -1.0 if ci == 0 else 1.0
		var cp := cable_point(tt, sd)
		# (round 41, the user: the car's foot "against the rails", no gap; "it's sitting on an angle. It should be
		# straight") it is built at the grade the line has at both stations, so it stands upright there; on the way,
		# where the line is gentler, it leans to the rails under it, both bogies on them
		var cl: float = float(N.cable.get("car", [0.9, 2.6])[1]) - 0.7      # (its bogies)
		var h_lo := rail_h(cp.z + cl)
		var h_up := rail_h(cp.z - cl)
		cabins[ci].global_position = Vector3(cp.x, (h_lo + h_up) / 2.0, cp.z)
		cabins[ci].rotation.x = atan((h_up - h_lo) / (2.0 * cl)) - atan(float(N.cable.get("grade", 0.41)))
		cabin_bodies[ci].global_position = Vector3(cp.x, 0.0, cp.z)
		# (riding, her own car doesn't push her: she is in it)
		(cabin_bodies[ci] as AnimatableBody3D).collision_layer = 0 if (not ride.is_empty() and String(ride.get("kind", "")) == "cable" and ci == 0) else main.LAYER_BODY


# ------------------------------------------------------------------ what she can do here

func candidates(p: Vector3) -> Array:
	var out := []
	if N.is_empty() or not ride.is_empty():
		return out
	var dl: Array = N.cable.door_low
	var dt_: Array = N.cable.door_top
	# (round 41, the user: "If I run too close to the turnstiles I can't press E… make sure that I can walk even closer")
	# the E reaches on in from the front step, through the arch, right up to the turnstile: points along the way in
	# (towards the track's end behind each station)
	var pts: Array = N.cable.pts
	for e_ in [[dl, pts[0], "Ride the funicular up", "cable_up"], [dt_, pts[pts.size() - 1], "Ride the funicular down", "cable_down"]]:
		var d0: Array = e_[0]
		var inw := Vector2(float(e_[1][0]) - float(d0[0]), float(e_[1][1]) - float(d0[1])).normalized()
		for k in 3:
			out.append({"x": float(d0[0]) + inw.x * 1.2 * k, "z": float(d0[1]) + inw.y * 1.2 * k, "r": 2.6, "label": e_[2],
				"act": "north", "what": e_[3]})
	# (round 41, the user: "she can get into any gondola? So she just walks up to it, goes up to the gate or whatever,
	# presses E, pays for it, and then gets into the next one, whatever color it is") E at the wheel's gate
	var wg: Array = N.wheel.gate
	out.append({"x": wg[0], "z": wg[1], "r": 1.6, "label": "Ride the wheel (€1)", "act": "north", "what": "wheel"})
	var tl: Array = N.get("telescope", [])
	if tl.size() >= 3:
		out.append({"x": tl[0] - sin(tl[2]) * 0.9, "z": tl[1] - cos(tl[2]) * 0.9, "r": 1.9, "label": "Look through the telescope (€1)",
			"act": "north", "what": "telescope"})
	# (round 38, 06 #97) E at a shut gate, from either side, with the ticket (or from inside, to leave: never shut in)
	if park_open() or park_inside(p):
		for gi in gates.size():
			var gt: Dictionary = gates[gi]
			if not gt.want:
				var r: Array = gt.rect
				out.append({"x": (r[0] + r[2]) / 2.0, "z": (r[1] + r[3]) / 2.0, "r": 2.6, "label": "Open the gate", "act": "north",
					"what": "gate_%d" % gi})
	return out


func act(what: String) -> void:
	var g: Node = main.game
	if what.begins_with("gate_"):
		open_gate(what.substr(5).to_int())
		return
	match what:
		"cable_up", "cable_down":
			if not g.has_item("park_pass"):
				main.show_dialog("", ["The turnstile stays shut: it only turns for an Amic del Park card, and the ticket office is closed. Sandra hasn't got a card."])
				return
			# (round 35, the user: "dogs are not allowed on the funicular, so the dog would need to stay down, and would
			# return to their owner … The same applies to the policeman")
			var st: Node = main.street
			if st.trufa and st.trufa.state == st.Dog.FOLLOW:
				if g.m_done("dog"):
					st.trufa.go_home()
					# (round 41: through the story's own queue, so the turnstile's question follows it instead of never coming)
					g.say("", "A sign by the turnstile: NO DOGS. Trufa sniffs it, gives Sandra a look, and trots off home to Montse.")
				else:
					main.show_dialog("", ["A sign by the turnstile: NO DOGS. Sandra had better take Trufa home to Montse first."])
					return
			var oq: Dictionary = main.npcs.outdoor.get("bofarull", {})
			if not oq.is_empty() and String(oq.get("mode", "")) == "follow":
				main.npcs.set_mode("bofarull", "back")
			# (round 40, the user: "walk up to the front of it and it gives you the option of ride the funicular and you
			# press E and then you have the option to do it or to not") her card at the turnstile, then the choice
			var up: bool = what == "cable_up"
			g.ask("", "The turnstile reads Sandra's Amic del Park card with a little green light. Ride the funicular %s?" % ("up to Tibidabo" if up else "down to the city"), [
				{"label": "Ride up" if up else "Ride down", "fn": func(): start_cable(up)},
				{"label": "Not now", "fn": func(): pass}])
		"wheel":
			g.ask("", "The Giradabo's gate: one euro, once round, a minute of the best view in Catalonia. Step into the next gondola?", [
				{"label": "Ride the wheel (€1)", "fn": func():
					if int(g.S.money) < 100:
						main.show_dialog("", ["One euro a ride, says the sign on the gate. Sandra hasn't got a euro."])
						return
					g.S.money -= 100
					main.ambience.sfx("coin")
					g.after(func(): start_wheel())},
				{"label": "Not now", "fn": func(): pass}])
		"telescope":
			if int(g.S.money) < 100:
				main.show_dialog("", ["A coin telescope: ONE EURO, says the plate by the slot. Sandra hasn't got a euro."])
				return
			g.S.money -= 100
			main.ambience.sfx("bell")
			main.toast("-€1: clunk, and the shutters open")
			start_scope()


const FUNI_STILL := 1.0           # (round 41) seconds the car stands at the platform once she's aboard, before it moves (then:
#                                   "half a second shorter… as long as it doesn't start before the fade ends": the fade back in ends 0.9 s after)
const FUNI_RAMP := 0.05           # the share of the ride spent getting up to speed (and slowing at the far end): 2 s of 40 (then the user:
#                                   "from the top to the bottom also starts too slow"; it was 0.08, 3.2 s)


func start_cable(up: bool) -> void:
	main.ambience.sfx("bell")
	main.toast("Your Amic del Park card: the turnstile clicks round")
	main.cutscene = true
	main.busy = true
	# (round 41, the user: "when she's getting in each way, have it fade to black and then fade back in again"; and
	# going down "could you avoid the flickering as she's getting in… maybe… the camera's jumping forward") the screen
	# goes black, she is aboard and the camera already round the car when it comes back
	var tw := main.create_tween()
	tw.tween_property(main.fade, "color:a", 1.0, 0.4)
	tw.tween_callback(func(): board_cable(up))
	tw.tween_interval(0.3)
	tw.tween_property(main.fade, "color:a", 0.0, 0.6)


func funi_ease(u: float) -> float:
	# (round 41, the user: "could the funicular start from stationary? So it briefly is stationary, then accelerates")
	# how far along the line after u of the ride's time: gathering speed over the first FUNI_RAMP, slowing over the last
	var v := 1.0 / (1.0 - FUNI_RAMP)
	if u < FUNI_RAMP:
		return v * u * u / (2.0 * FUNI_RAMP)
	if u > 1.0 - FUNI_RAMP:
		return 1.0 - v * (1.0 - u) * (1.0 - u) / (2.0 * FUNI_RAMP)
	return v * (u - FUNI_RAMP / 2.0)


func board_cable(up: bool) -> void:
	# (round 41, the user: "when it starts from the top, could it start quicker? So there's no wait… it's moving from the
	# moment the fade begins") going down: no standing, and already part way up to speed while the screen is dark
	ride = {"kind": "cable", "up": up, "t": 0.0 if up else FUNI_RAMP * 0.4, "wait": FUNI_STILL if up else 0.0, "t0": main.t + 1.0}
	cable_t = 0.0 if up else 1.0 - funi_ease(float(ride.t))
	place_cabins()
	main.ride_cam = true
	# (round 41, the user: "the camera follows the cable car up and you can't see her. She's just inside of it. But you
	# can move the camera around in circles as it's going up. That's it"; 03 #28a) she is hidden in the car and the
	# camera follows it, from the side of the line, the city below in view; the mouse and ← → take it round
	main.ride_inside = true
	main.ride_look = false
	main.model.visible = false
	# (on the line's west side, where the hill's trees stand back and the city opens out below)
	var a := cable_point(0.45, -1.0)
	var b := cable_point(0.5, -1.0)
	main.cam_yaw_node.rotation.y = atan2(b.x - a.x, b.z - a.z) + PI / 2.0
	main.cam_pitch_node.rotation.x = -0.3
	if not up:
		# (round 41, the user: "press e to come in and out, especially when you are arriving and leaving. We want to avoid
		# the cutting through objects") leaving the top, the car stands in the portal under the terrace's bank: from the
		# side the camera's arm met the bank and came in inside the station; it starts down the cutting instead,
		# looking up at the car as it comes out
		main.cam_yaw_node.rotation.y = 0.0
		main.cam_pitch_node.rotation.x = -0.15
	main.last_manual_cam = main.t
	put_her(cable_point(cable_t, -1.0) + Vector3(0, 0.55, 0))
	main.cam_root.global_position = main.player.global_position + Vector3(0, main.CAM_PIVOT_H + main.model.position.y, 0)
	main.arm.spring_length = main.cam_len * 1.6           # (already out round the car: no glide while it's dark)


# (round 41, the user: "If she can look out from the inside, that would also be amazing. As well as the third person
# where you can spin around"; "Then she can sit at the bottom and look around as if she's at the bottom seat") E on the
# funicular swaps between following the car and her own eyes on the bench at its bottom end, facing down the line
# (north_build.py FUNI_SEAT); the mouse and ← → look round either way
func seat_point() -> Vector3:
	var st: Array = N.cable.get("seat", [-2.4, 0.4])
	return (cabins[0] as Node3D).global_transform * Vector3(0.0, float(st[1]), -float(st[0]))


func ride_toggle() -> void:
	if ride.get("kind", "") != "cable":
		return
	main.ride_look = not main.ride_look
	main.last_manual_cam = main.t
	main.ambience.sfx("page")
	if main.ride_look:
		main.seat_eye = 0.0                       # (she is put at her eyes' own point: seat_point)
		main.seat_lean = 0.0
		main.cam_yaw_node.rotation.y = PI         # (looking down the line, +z: the camera looks along its -z)
		main.cam_pitch_node.rotation.x = -0.2       # (a little down: the tiers and the nose's frame in view)
		put_her(seat_point())
		main.cam_root.global_position = main.player.global_position
	else:
		main.seat_eye = -1.0
		main.seat_lean = main.SEAT_LEAN
		main.cam_pitch_node.rotation.x = -0.3
		put_her(cable_point(cable_t, -1.0) + Vector3(0, 0.55, 0))
		# (round 41: back out of her seat the camera kept looking down the line from the uphill side; near the top that is
		# inside the portal: there it goes down the cutting instead, looking up at the car; elsewhere out to the side)
		var a2 := cable_point(0.45, -1.0)
		var b2 := cable_point(0.5, -1.0)
		main.cam_yaw_node.rotation.y = 0.0 if cable_t > 0.8 else atan2(b2.x - a2.x, b2.z - a2.z) + PI / 2.0
		if cable_t > 0.8:
			main.cam_pitch_node.rotation.x = -0.15


func start_wheel() -> void:
	# the wheel slows to bring the gondola at the bottom right to the platform; she steps in
	var n: int = int(N.wheel.n)
	var best := 0
	var bd := INF
	for g in n:
		var a := fposmod(TAU * g / float(n) - PI / 2.0 + wheel_a + PI / 2.0, TAU)       # (0 = at the bottom)
		var ahead := fposmod(-a, TAU)                                                    # how far it still has to come
		if ahead < bd:
			bd = ahead
			best = g
	ride = {"kind": "wheel", "g": best, "phase": "arrive", "turned": 0.0, "need": bd}
	main.cutscene = true
	main.busy = true
	main.ride_cam = true
	# (round 23) the camera looks at her from out of the wheel's plane, over her shoulder towards the city: behind her
	# in the wheel's plane it ended up inside the next gondola
	# (round 41, the user: "once she pays for the Ferris she should be facing it, and so then when she jumps in, the
	# camera is facing the city still. By default") behind her, looking past her at the wheel and the city beyond it;
	# seated she faces the same way (+z)
	main.cam_yaw_node.rotation.y = PI
	main.cam_pitch_node.rotation.x = -0.22
	main.last_manual_cam = main.t


func ride_tick(dt: float) -> void:
	match String(ride.kind):
		"wheel":
			var drop: float = float(N.wheel.gondola_drop)
			if ride.phase == "arrive":
				# the gondola comes round to the platform, slowing; she waits at the gate
				var step := minf(wheel_speed * dt * 2.0, float(ride.need))
				wheel_a = fmod(wheel_a + step - wheel_speed * dt, TAU)              # (tick() already moved it on)
				ride.need = float(ride.need) - step
				if float(ride.need) <= 0.001:
					ride.phase = "board"
					ride.wait = 1.2
					main.ambience.sfx("open")
					seat_on_wheel(int(ride.g))
				place_wheel()
			elif ride.phase == "board":
				wheel_a = fmod(wheel_a - wheel_speed * dt, TAU)                     # (held still)
				place_wheel()
				ride.wait = float(ride.wait) - dt
				if float(ride.wait) <= 0.0:
					ride.phase = "round"
					main.ambience.sfx("close")
					main.toast("The door clicks shut. Once round, about a minute")
			elif ride.phase == "round":
				ride.turned = float(ride.turned) + wheel_speed * dt
				if float(ride.turned) >= TAU:
					wheel_a = fmod(wheel_a - (float(ride.turned) - TAU), TAU)
					place_wheel()
					ride.phase = "out"
					ride.wait = 1.0
					main.ambience.sfx("open")
			elif ride.phase == "out":
				wheel_a = fmod(wheel_a - wheel_speed * dt, TAU)
				place_wheel()
				ride.wait = float(ride.wait) - dt
				if float(ride.wait) <= 0.0:
					unseat()
					# (round 41, the user, last: "the same way she walked on, that she walks off… comes out of the gap, and
					# walks in the other direction") back in the lane she came along, facing back to its west steps
					var wo: Array = N.wheel.get("off", [N.wheel.board[0], N.wheel.board[1] + 1.6])
					end_ride(Vector3(wo[0], 0, wo[1]), -PI / 2.0)
					main.game.S.flags.wheelRidden = true
					main.game.check_achievements()
					return
			if ride.phase != "arrive" and not seat.is_empty():
				# (round 41) on the bench: the seat is the gondola's own, so she rides with it
				main.player.global_position = gondola_pos(int(ride.g)) + SEAT_AT
				main.model.position.y = 0.0
				main.model.rotation.y = 0.0                 # (as seat_on_wheel turned her: round 41, turned round again)
			elif ride.phase != "arrive":
				var gp := gondola_pos(int(ride.g)) - Vector3(0, drop, 0)
				put_her(gp)
			else:
				var wg_ := Vector3(N.wheel.gate[0], 0.0, N.wheel.gate[1])
				put_her(Vector3(wg_.x, maxf(float(N.fair.h), main.ground_at(wg_)), wg_.z))      # (on the platform)
				main.model.rotation.y = atan2(float(N.wheel.board[0]) - wg_.x, float(N.wheel.board[1]) - wg_.z)   # (facing the wheel)
		"cable":
			var up: bool = ride.up
			if float(ride.get("wait", 0.0)) > 0.0:
				ride.wait = float(ride.wait) - dt          # (standing at the platform a moment)
			else:
				ride.t = float(ride.t) + dt / float(N.cable.ride_s)
			var fp := funi_ease(clampf(float(ride.t), 0.0, 1.0))
			cable_t = fp if up else 1.0 - fp
			place_cabins()
			if main.ride_look and cabins[0]:
				put_her(seat_point())                 # (on the bench at the bottom end, her eyes there)
				# (round 41, the user: "limit it so you can only look 180 degrees… also test looking up and down. So it
				# should be bordered by the vehicle") half a turn either side of straight down the line; up to the
				# roof's edge, down to the floor before her
				# (then: "could we actually make it 360 in every direction? So it's just first person") all the way round,
				# and from the roof overhead down to the floor
				main.cam_pitch_node.rotation.x = clampf(main.cam_pitch_node.rotation.x, -PI / 2.0 + 0.1, PI / 2.0 - 0.1)
			else:
				put_her(cable_point(cable_t, -1.0) + Vector3(0, 0.55, 0))
				# (round 41, the user: "those walls are not treated as actual walls. So maybe the camera needs to be spun
				# around a bit more") over the ride's last fifth the following camera eases round behind the car, looking
				# up (or down) the open cutting into the station, instead of out at the side, where its arm met the
				# plateau's bank over the portal and snapped in — unless she has just turned it herself
				# (then: "as I go up the hill, when I move up or down, it keeps resetting": once the player has turned or
				# tipped the camera this ride, it is theirs: no easing back)
				if main.last_manual_cam > float(ride.get("t0", 0.0)) + 0.2:
					ride.touched = true
				if fp > 0.8 and not ride.get("touched", false):
					var want_yaw := 0.0 if up else PI
					main.cam_yaw_node.rotation.y = lerp_angle(main.cam_yaw_node.rotation.y, want_yaw, 1.0 - exp(-2.5 * smoothstep(0.8, 0.92, fp) * dt))
					main.cam_pitch_node.rotation.x = lerpf(main.cam_pitch_node.rotation.x, -0.22, 1.0 - exp(-1.5 * dt))
			# (round 41, the user: "when you're going up into the building, looks like it glitches a bit. Could you also
			# have a fade in and fade out?") arriving, each way: the screen darkens over the ride's last moments, she
			# steps out while it is dark, and it comes back with the camera already behind her
			var left := (1.0 - float(ride.t)) * float(N.cable.ride_s)
			# (then: "As soon as it touches the dark part as it goes up the hill, you should begin to fade to black")
			# going up, from the moment the car's nose meets the portal's dark, darkening right to its stop
			var nose_in := false
			if up:
				var pts_: Array = N.cable.pts
				nose_in = cable_point(cable_t, -1.0).z - float(N.cable.car[1]) < float(pts_[-1][1]) + 0.3
			if (nose_in or left < 1.3) and not ride.get("fading", false):
				ride.fading = true
				main.create_tween().tween_property(main.fade, "color:a", 1.0, clampf(left - 0.05, 0.3, 2.5))
			if float(ride.t) >= 1.0:
				var tw := main.create_tween()
				tw.tween_property(main.fade, "color:a", 1.0, 0.05)
				tw.tween_interval(0.3)
				tw.tween_property(main.fade, "color:a", 0.0, 0.6)
				cable_wait = 8.0
				cable_dir = -1.0 if up else 1.0
				var d: Array = N.cable.door_top if up else N.cable.door_low
				main.seat_eye = -1.0
				main.seat_lean = main.SEAT_LEAN
				# (round 23: at the top she steps well out onto the forecourt, so the camera behind her isn't inside the
				# station)
				end_ride(Vector3(d[0], 0, d[1] + (-4.5 if up else 1.2)), PI if up else 0.0)
				main.cam_root.global_position = main.player.global_position + Vector3(0, main.CAM_PIVOT_H + main.model.position.y, 0)
				main.arm.spring_length = main.cam_len          # (already behind her when it comes back from black)


# (round 41, the user: "ride the Ferris wheel and take pictures… make her body sit correctly on it": she stood in the
# tub with her legs through its bench, only her head over the rim) seated on the gondola's bench, as at the exam desk
# (exam_scene.gd, rider_pose.gd's seated reach): hips on the bench, thighs along it, shins hanging, hands in her lap,
# facing out of the wheel towards the city; the marks her feet and hands reach for hang from the gondola, so they ride
# with it. The seat (north_build.py): round, in the middle of the tub, its top 1.54 m under the gondola's pivot.
const SEAT_AT := Vector3(0.0, -1.54, -0.04)      # (round 41: on the round seat in the middle)
var seat := {}                   # {pose, marks: [nodes]} while she sits


func seat_on_wheel(g: int) -> void:
	unseat()
	var gn: Node3D = gondolas[g] if g < gondolas.size() else null
	if gn == null:
		return
	var sk: Dictionary = main.skins[main.skin_idx]
	var skel: Skeleton3D = sk.root.find_children("*", "Skeleton3D", true, false)[0]
	if sk.get("posture"):
		sk.posture.amount = 0.0
	main.player.global_position = gondola_pos(g) + SEAT_AT
	main.model.position.y = 0.0
	# (round 41, the user: "the chair and the Ferris wheel should be turned around the other way") she faces the
	# gondola's -z now, her hand-rail on that side (north_build.py); the marks below are laid as before and turned round
	# (then: "Sandra needs to be turned around the other way. The seat is in the right direction. She is not": she faces
	# +z again, the rail behind her like a chair's back, her hands on her knees)
	main.model.rotation.y = 0.0
	var bn := func(a: String) -> int:
		return skel.find_bone(main.street.bone(skel, "mixamorig:" + a))
	var gs := skel.global_transform
	var hips_at: Vector3 = main.model.to_local(gs * skel.get_bone_global_rest(bn.call("Hips")).origin)
	sk.root.position = Vector3(0, 0.05, 0) - hips_at
	var thigh: float = (gs * skel.get_bone_global_rest(bn.call("LeftUpLeg")).origin).distance_to(gs * skel.get_bone_global_rest(bn.call("LeftLeg")).origin)
	var shin: float = (gs * skel.get_bone_global_rest(bn.call("LeftLeg")).origin).distance_to(gs * skel.get_bone_global_rest(bn.call("LeftFoot")).origin)
	# the marks, in the gondola's own space (+z out of the wheel, the way she faces, so her left is +x: round 41, the user:
	# "Her arms still look wrong": laid as if she faced -z, as at the exam desk, her arms crossed in front of her chest)
	var hy := SEAT_AT.y + 0.05
	var z0 := SEAT_AT.z
	var marks := {}
	var nodes := []
	for pv in [["foot_l", Vector3(0.09, hy - shin * 0.93, z0 + thigh * 0.95 + 0.04)], ["foot_r", Vector3(-0.09, hy - shin * 0.93, z0 + thigh * 0.95 + 0.04)],
			["knee_l", Vector3(0.12, hy + 0.3, z0 + thigh + 0.5)], ["knee_r", Vector3(-0.12, hy + 0.3, z0 + thigh + 0.5)],
			# (round 41, the user: "She also doesn't have any arms in the gondola": tucked to her sides, the white sleeves
			# were lost against her shirt; her elbows go out now, her hands on her knees, so her arms read as arms)
			# (then: her hands on the little rail in front of her, north_build.py: 0.27 m out, 0.2 m over the seat, close
			# enough that her elbows bend; the elbows down and a little back and out, by her sides)
			["hand_l", Vector3(0.13, hy + 0.12, z0 + thigh * 0.75)], ["hand_r", Vector3(-0.13, hy + 0.12, z0 + thigh * 0.75)],
			["elbow_l", Vector3(0.36, hy + 0.25, z0 - 0.1)], ["elbow_r", Vector3(-0.36, hy + 0.25, z0 - 0.1)]]:
		var n := Node3D.new()
		gn.add_child(n)
		n.position = pv[1]
		marks[pv[0]] = n
		nodes.append(n)
	var pose := SkeletonModifier3D.new()
	pose.set_script(load("res://engine/rider_pose.gd"))
	skel.add_child(pose)
	var bones := {}
	for pair in [["hips", "Hips"], ["spine", "Spine"], ["spine1", "Spine1"], ["spine2", "Spine2"], ["neck", "Neck"], ["head", "Head"],
			["upleg_l", "LeftUpLeg"], ["leg_l", "LeftLeg"], ["foot_l", "LeftFoot"], ["upleg_r", "RightUpLeg"], ["leg_r", "RightLeg"], ["foot_r", "RightFoot"],
			["shoulder_l", "LeftShoulder"], ["shoulder_r", "RightShoulder"], ["arm_l", "LeftArm"], ["fore_l", "LeftForeArm"], ["hand_l", "LeftHand"], ["arm_r", "RightArm"], ["fore_r", "RightForeArm"], ["hand_r", "RightHand"]]:
		bones[pair[0]] = bn.call(pair[1])
	pose.setup(main.model, bones, marks)
	pose.lean = 0.02
	pose.head_down = 0.0
	pose.crank = 0.0
	pose.active = true
	seat = {"pose": pose, "marks": nodes, "root": sk.root}
	# the camera's centre at her eyes, sitting: the head over the hips as she stands, from the seat
	main.seat_eye = (gs * skel.get_bone_global_rest(bn.call("Head")).origin).y - (gs * skel.get_bone_global_rest(bn.call("Hips")).origin).y + 0.12


func unseat() -> void:
	if seat.is_empty():
		return
	if is_instance_valid(seat.pose):
		seat.pose.queue_free()
	for n in seat.marks:
		if is_instance_valid(n):
			n.queue_free()
	if is_instance_valid(seat.root):
		seat.root.position = Vector3.ZERO
	main.seat_eye = -1.0
	seat = {}


func put_her(at: Vector3) -> void:
	main.player.global_position = at
	main.model.position.y = 0.0


func end_ride(at: Vector3, facing: float) -> void:
	if main.vf_on:
		main.viewfinder(false)                   # (round 41c, the user: the camera put away at any change of place)
	ride = {}
	main.ride_look = false
	main.ride_inside = false
	main.model.visible = true
	main.player.global_position = Vector3(at.x, 0.0, at.z)
	main.model.rotation.y = facing
	main.model.position.y = main.ground_at(main.player.global_position)
	main.cutscene = false
	main.busy = false
	main.ride_cam = false
	refresh()


# ------------------------------------------------------------------ the coin telescope (round 25)
# The user: "a telescope at the amusement park for 1 euro… a fixed zoom that allows Sandra to look at the city… move
# slowly… consider real world tourist telescopes with the two eye holes". A minute's look through the binocular viewer
# at the plateau's edge: a narrow, fixed view framed by its two round eyepieces, turned slowly with the arrow keys
# (or WASD), E or Esc to step back. While she looks, the city is drawn as it would be that much nearer (the far-off
# detail the game usually leaves out comes back) and the haze is thinner; both are put back after.
const SCOPE_FOV := 9.0           # degrees (the game's camera: 60): about 7x
const SCOPE_TIME := 60.0         # seconds a euro buys
const SCOPE_TURN := 0.1          # radians a second, turning it
var scope: Dictionary = {}


func scope_active() -> bool:
	return not scope.is_empty()


func start_scope() -> void:
	var tl: Array = N.telescope
	var cam := Camera3D.new()
	cam.fov = SCOPE_FOV
	cam.near = 0.3
	cam.far = 4000.0
	main.outdoor.add_child(cam)
	var k := 60.0 / SCOPE_FOV
	var saved := []
	for n in main.outdoor.find_children("*", "GeometryInstance3D", true, false):
		var gi := n as GeometryInstance3D
		if gi.visibility_range_end > 0.0 or gi.visibility_range_begin > 0.0:
			saved.append([gi, gi.visibility_range_begin, gi.visibility_range_end])
			gi.visibility_range_begin *= k
			gi.visibility_range_end *= k
	var env: Environment = main.env_out
	var fog := [env.fog_depth_begin, env.fog_depth_end]
	env.fog_depth_begin *= k
	env.fog_depth_end *= k
	# the eyepieces: two round holes in the dark, overlapping a little, a soft rim inside them
	var layer := CanvasLayer.new()
	layer.layer = 0                      # (round 41, the user: "make the hud come up over the top of it… Then the money -1
	                                     # euro can be seen": over the view, under the HUD's own layer, 1)
	var rect := ColorRect.new()
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = """shader_type canvas_item;
uniform vec2 size = vec2(1280.0, 800.0);
void fragment() {
	// (round 41, the user: "The telescope lens should be in the middle of the screen. It is when it is small, but not
	// when it is enlarged": the screen's pixels and the window's size differ on a scaled screen — by the rect's own
	// UV, only the window's shape matters)
	vec2 p = (UV - vec2(0.5)) * vec2(size.x / size.y, 1.0);
	float r = 0.41;
	float d = min(length(p - vec2(-0.21, 0.0)), length(p - vec2(0.21, 0.0)));
	float out_ = smoothstep(r - 0.006, r + 0.004, d);
	float rim = smoothstep(r - 0.09, r, d) * 0.6;
	COLOR = vec4(0.02, 0.02, 0.025, max(out_, rim));
}"""
	var mat := ShaderMaterial.new()
	mat.shader = sh
	rect.material = mat
	layer.add_child(rect)
	var hint := Label.new()
	hint.text = "←  →  ↑  ↓  turn it slowly     E: step back"
	hint.add_theme_color_override("font_color", Color(0.85, 0.82, 0.74))
	hint.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	hint.position.y -= 40
	hint.position.x -= 160
	layer.add_child(hint)
	main.add_child(layer)
	# (round 35: tipped down at the city's middle to begin with; it was level, at the sea)
	scope = {"cam": cam, "yaw": float(tl[2]), "pitch": -0.2, "t": 0.0, "saved": saved, "fog": fog, "layer": layer, "mat": mat}
	main.cutscene = true
	main.busy = true
	place_scope()
	cam.current = true


func place_scope() -> void:
	var tl: Array = N.telescope
	var head := Vector3(tl[0], float(tl[3]) + 1.42, tl[1])
	var cam: Camera3D = scope.cam
	# (round 35, the everything-visit: 0.2 m behind its middle the eye was inside its green head, and the view was the
	# inside of the casing, all teal; out past the lenses, as the lenses see)
	cam.global_position = head + Vector3(sin(float(tl[2])), 0, cos(float(tl[2]))) * 0.45
	cam.rotation = Vector3(scope.pitch, scope.yaw + PI, 0.0)


func tick_scope(dt: float) -> void:
	scope.t += dt
	var dx := 0.0
	var dy := 0.0
	if main.held(KEY_LEFT) or main.held(KEY_A):
		dx += 1.0
	if main.held(KEY_RIGHT) or main.held(KEY_D):
		dx -= 1.0
	if main.held(KEY_UP) or main.held(KEY_W):
		dy += 1.0
	if main.held(KEY_DOWN) or main.held(KEY_S):
		dy -= 1.0
	var base := float(N.telescope[2])
	scope.yaw = clampf(float(scope.yaw) + dx * SCOPE_TURN * dt, base - 1.2, base + 1.2)      # (it turns on its post, so far)
	# (round 41, the user: "so that I can look down lower. The bottom should be the forest")
	scope.pitch = clampf(float(scope.pitch) + dy * SCOPE_TURN * 0.6 * dt, -0.62, 0.08)
	var vp := main.get_viewport().get_visible_rect().size
	(scope.mat as ShaderMaterial).set_shader_parameter("size", vp)
	place_scope()
	if float(scope.t) > SCOPE_TIME:
		main.toast("Clunk: the shutters close. That was the euro.")
		end_scope()


func end_scope() -> void:
	if scope.is_empty():
		return
	for e in scope.saved:
		if is_instance_valid(e[0]):
			(e[0] as GeometryInstance3D).visibility_range_begin = e[1]
			(e[0] as GeometryInstance3D).visibility_range_end = e[2]
	main.env_out.fog_depth_begin = scope.fog[0]
	main.env_out.fog_depth_end = scope.fog[1]
	(scope.layer as Node).queue_free()
	(scope.cam as Node).queue_free()
	main.cam.current = true
	main.cutscene = false
	main.busy = false
	scope = {}
