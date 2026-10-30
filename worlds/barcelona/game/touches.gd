# Small things from the 2D game that make the world feel lived in (round 20, the user's review of the 2D
# game's features, each kept for what it was for):
#   party       Alessandra's flat while her party is on: bunting along the back wall, balloons bobbing,
#               a birthday cake with flickering candles on the party table; gone once the party is over
#               (it shows the party has happened and ended, as the 2D game's decorations did)
#   vase        Alba's empty glass vase on her table; once she has traded the book for five wildflowers it
#               is full of orange flowers, for good (the trade's visible, lasting reward)
#   cats        three cats, as in the 2D game: a ginger one asleep on the beach, a black one sitting up in
#               the Ciutadella, flicking its tail, a pale one asleep in the grass under the mountains; E to
#               look at them; she walks round them
#   mushrooms   little white mushrooms all through the wood, round-topped, in clumps of two or three by the
#               trunks, off the paths (round 22, the user's wish; only to look at: the three rare red ones,
#               game.gd's RED_MUSHROOMS, are the ones she can pick)
#   pollen      a few faint motes drifting in the glade she is in, by day (round 24; round 25: the shafts of light
#               that came with them are gone, and the motes are fewer and fainter: "keep … but make it subtle")
extends Node

const T := 3.3
const OX := 55
const OY := 45
const CATS := [
	{"at": [58.4, 87.6], "col": "#e0913a", "sleep": true, "yaw": 0.6,
		"t": "A ginger cat asleep on the warm sand, curled into a perfect circle. One ear twitches at the sound of the waves; the rest of her doesn't bother."},
	# (round 35, the everything-visit: at the 2D map's park, now a block of houses — the cat sat shut in its courtyard; on
	# the Ciutadella's lawn by the pool instead, facing the water)
	{"at": [74.8, 73.8], "col": "#3a3434", "sleep": false, "yaw": -1.57,
		"t": "A black cat sitting very upright in the park, watching the ducks with professional interest. The tip of its tail flicks, just once, as Sandra passes."},
	# (round 40, the user: "Move the cat on the hill to Sandra's apartment. The cat belongs to her housemate and it's not
	# very friendly if you speak to it": the pale grey one is Rosa's now, ROSA_CAT)
]
# (round 40) Rosa's cat, sitting up on the rug on Rosa's side of the flat (room metres: x, row, height, which way it faces)
const ROSA_CAT := [8.4, 4.7, 0.03, -1.9]
const ROSA_CAT_LINES := ["Rosa's cat looks up from the rug, flattens her ears and gives a low, rumbling growl. Rosa insists she's a sweetheart. Rosa is lying.",
	"Sandra crouches and holds out a hand. The cat stares at it, then at Sandra, then turns her back and washes a paw. Message received.",
	"A flick of the tail, a narrow green look. The cat would like it known that this is her flat, and Sandra is merely staying in it."]
var rosa_cat: Node3D
var rosa_cat_said := 0

var main: Node3D
var t := 0.0
var party: Node3D                # in Alessandra's flat
var balloons: Array = []
var flames: Array = []
var vase_flowers: Node3D         # in Alba's flat
var cats: Array = []             # {node, d, tail, body}
var salamandreta: Node3D         # (round 22/23) Park Güell's little dragon, back on its plinth once she brings it
var biel_ball: Node3D            # (round 41c) the red ball at Biel's feet once it is given back
const BIEL_BALL_TEXT := "Laia's red ball, back where it belongs, right at Laia's feet. Every so often a small foot nudges it, just to check it's real, then stops it again before it can go anywhere near the hill."
var motes: GPUParticles3D
var glades: Array = []           # [Vector3 centre (on the ground), radius]


func setup(m: Node3D) -> void:
	main = m
	build_party()
	build_vase()
	build_mushrooms()
	build_notebook()
	build_rosa_cat()
	build_salamandreta()
	build_biel_ball()
	build_pollen()
	var posts: StaticBody3D = main.static_body(main.LAYER_BODY)
	for c in CATS:
		var p := Vector3((c.at[0] + 0.5 - OX) * T, 0.0, (c.at[1] + 0.5 - OY) * T)
		p.y = main.ground_at(p)
		var n := cat(Color(c.col), c.sleep)
		n.position = p
		n.rotation.y = c.yaw
		n.scale = Vector3.ONE * 1.5                          # (toy-sized, like the pigeons)
		main.outdoor.add_child(n)
		cats.append({"node": n, "d": c, "pos": p})
		main.add_post(posts, p.x, p.z, 0.32, 0.6)
	refresh()


func build_pollen() -> void:
	for g in main.D.get("forest_glades", []):
		glades.append([Vector3(g[0], 0, g[1]), float(g[2])])
	var Nn: Dictionary = main.D.get("north", {})
	if Nn.has("ledge") and not Nn.has("ball"):          # (round 25: the ball lies in deep wood now, no glade)
		glades.append([Vector3(Nn.ledge[0] + 4.0, 0, Nn.ledge[1] + 1.0), 7.0])
	if Nn.has("park") and Nn.park.has("calvari"):
		glades.append([Vector3(Nn.park.calvari[0] + 6.0, 0, Nn.park.calvari[1] + 6.0), 6.0])
	for gl in glades:
		var c: Vector3 = gl[0]
		c.y = main.ground_at(c)
		gl[0] = c
	# pollen: tiny warm specks drifting in the light, moved to whichever glade she's in
	motes = GPUParticles3D.new()
	motes.amount = 26
	motes.lifetime = 9.0
	motes.preprocess = 9.0
	motes.visibility_aabb = AABB(Vector3(-10, -2, -10), Vector3(20, 10, 20))
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = Vector3(6.0, 1.8, 6.0)
	pm.direction = Vector3(0.3, 0.2, 0.1)
	pm.spread = 180.0
	pm.initial_velocity_min = 0.03
	pm.initial_velocity_max = 0.12
	pm.gravity = Vector3(0, 0.01, 0)
	pm.turbulence_enabled = true
	pm.turbulence_noise_strength = 0.4
	pm.turbulence_noise_speed_random = 0.3
	var fade := Gradient.new()
	fade.set_color(0, Color(1, 1, 1, 0))
	fade.add_point(0.25, Color(1, 1, 1, 1))
	fade.add_point(0.75, Color(1, 1, 1, 1))
	fade.set_color(fade.get_point_count() - 1, Color(1, 1, 1, 0))
	var gt := GradientTexture1D.new()
	gt.gradient = fade
	pm.color_ramp = gt
	motes.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(0.026, 0.026)
	var qm := StandardMaterial3D.new()
	qm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	qm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	qm.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	qm.vertex_color_use_as_albedo = true
	qm.albedo_color = Color(0.55, 0.5, 0.36)
	qm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	q.material = qm
	motes.draw_pass_1 = q
	motes.emitting = false
	motes.visible = false
	main.outdoor.add_child(motes)


func update_pollen() -> void:
	var night: float = float(main.P.get("nk", 0.0))                 # (how far into the night, 0..1)
	var sandra: Vector3 = main.player.global_position
	# the pollen, in the glade she's in, while the sun is up
	var best := -1
	for i in glades.size():
		var c: Vector3 = glades[i][0]
		if Vector2(c.x - sandra.x, c.z - sandra.z).length() < float(glades[i][1]) + 6.0:
			best = i
	motes.visible = best >= 0 and night < 0.5 and main.where == "out"
	motes.emitting = motes.visible
	if best >= 0:
		motes.global_position = glades[best][0] + Vector3(0, 1.6, 0)


func mat(col: Color, rough := 0.8) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = rough
	return m


func part(n: Node3D, mesh: Mesh, m: Material, at: Vector3, sc := Vector3.ONE, rot := Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = m
	mi.position = at
	mi.scale = sc
	mi.rotation = rot
	n.add_child(mi)
	return mi


func sphere(r: float) -> SphereMesh:
	var s := SphereMesh.new()
	s.radius = r
	s.height = r * 2.0
	s.radial_segments = 16
	s.rings = 8
	return s


func room_point(rid: String, x: float, y: float, h: float) -> Vector3:
	return main.room_base(rid) + Vector3(x, h, y)


func room_node(rid: String) -> Node3D:
	return main.room_nodes.get(rid, main.indoor)


# ------------------------------------------------------------------ the party

func build_party() -> void:
	var rid := "int_alessandra"
	if not main.D.interiors.has(rid):
		return
	var R: Dictionary = main.D.interiors[rid]
	party = Node3D.new()
	main.indoor.add_child(party)
	party.global_transform = Transform3D.IDENTITY        # (round 35: room points are world points; the rooms' parent is 400 m off)
	var cols := ["#e0342f", "#f2c84b", "#3d8ae0", "#4fb08a", "#f28aa8"]
	# bunting: little flags hanging from a string in swags along the back wall
	var flag := PrismMesh.new()
	flag.size = Vector3(0.22, 0.26, 0.01)
	var string_m := mat(Color(0.35, 0.25, 0.18))
	var w: float = R.w
	var k := 0
	var x := 1.4
	while x < w - 1.4:
		var sag := 0.12 * sin(PI * fmod(x - 1.4, 2.0) / 2.0)
		var fl := part(party, flag, mat(Color(cols[k % cols.size()]), 0.7), room_point(rid, x, 1.06, 2.28 - sag), Vector3.ONE, Vector3(0, 0, PI))
		fl.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		k += 1
		x += 0.34
	var cord := BoxMesh.new()
	cord.size = Vector3(w - 2.8, 0.012, 0.012)
	part(party, cord, string_m, room_point(rid, w / 2.0, 1.05, 2.42))
	# balloons in the corners, on strings, bobbing
	for b in [[2.0, 1.6, "#e0342f"], [2.5, 1.9, "#f2c84b"], [w - 2.0, 1.6, "#3d8ae0"], [w - 2.6, 2.0, "#f28aa8"]]:
		var bn := Node3D.new()
		party.add_child(bn)
		bn.position = room_point(rid, b[0], b[1], 1.75)
		var bm := mat(Color(b[2]), 0.25)
		part(bn, sphere(0.2), bm, Vector3.ZERO, Vector3(1, 1.2, 1))
		var st := CylinderMesh.new()
		st.top_radius = 0.004
		st.bottom_radius = 0.004
		st.height = 1.4
		part(bn, st, mat(Color(0.9, 0.9, 0.88)), Vector3(0, -0.92, 0))
		balloons.append({"node": bn, "y": bn.position.y, "ph": b[0] * 1.7})
	# the cake on the party table, three candles
	var tb = null
	for th in R.things:
		if th.get("party", false):
			tb = th
	if tb != null:
		var c := room_point(rid, tb.pos[0] + 0.45, tb.pos[1], 0.77)
		var cake := CylinderMesh.new()
		cake.top_radius = 0.17
		cake.bottom_radius = 0.17
		cake.height = 0.14
		part(party, cake, mat(Color("#f7e8d4"), 0.6), c + Vector3(0, 0.07, 0))
		var icing := CylinderMesh.new()
		icing.top_radius = 0.175
		icing.bottom_radius = 0.175
		icing.height = 0.03
		part(party, icing, mat(Color("#f28aa8"), 0.4), c + Vector3(0, 0.13, 0))
		for i in 3:
			var a := i * TAU / 3.0
			var cp := c + Vector3(cos(a) * 0.08, 0.2, sin(a) * 0.08)
			var cd := CylinderMesh.new()
			cd.top_radius = 0.008
			cd.bottom_radius = 0.008
			cd.height = 0.1
			part(party, cd, mat(Color("#f4efe4")), cp)
			var fm := StandardMaterial3D.new()
			fm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			fm.albedo_color = Color(1.0, 0.8, 0.4)
			fm.emission_enabled = true
			fm.emission = Color(1.0, 0.75, 0.35)
			fm.emission_energy_multiplier = 3.0
			var f := part(party, sphere(0.014), fm, cp + Vector3(0, 0.065, 0), Vector3(1, 1.8, 1))
			flames.append(f)
		var glow := OmniLight3D.new()
		glow.light_color = Color(1.0, 0.75, 0.45)
		glow.light_energy = 0.5
		glow.omni_range = 1.6
		glow.position = c + Vector3(0, 0.35, 0)
		party.add_child(glow)
		flames.append(glow)


# ------------------------------------------------------------------ Alba's vase

func build_vase() -> void:
	var rid := "int_alba"
	if not main.D.interiors.has(rid):
		return
	var tb = null
	for th in main.D.interiors[rid].things:
		if th.get("vase", false):
			tb = th
	if tb == null:
		return
	# (round 35, the user: "make it look nice, not sloppy, the flowers should look like they were arranged") a round
	# glass vase with water in it on the table top (0.77 m), and in it a dome of Alba's orange wildflowers: one tall
	# in the middle, five round it, six lower and further out, sprigs of leaves between, a few small white flowers
	var c := room_point(rid, tb.pos[0] + 0.2, tb.pos[1], 0.77)
	var holder := Node3D.new()
	main.indoor.add_child(holder)
	holder.global_transform = Transform3D.IDENTITY       # (round 35: room points are world points; the rooms' parent isn't at 0)
	var glass := StandardMaterial3D.new()
	glass.albedo_color = Color(0.78, 0.92, 0.94, 0.5)
	glass.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glass.roughness = 0.05
	glass.metallic_specular = 0.9
	glass.rim_enabled = true
	glass.rim = 0.6
	var water := StandardMaterial3D.new()
	water.albedo_color = Color(0.62, 0.82, 0.8, 0.45)
	water.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	water.roughness = 0.1
	part(holder, sphere(0.075), glass, c + Vector3(0, 0.066, 0), Vector3(1, 0.88, 1))                 # the round body
	var neck := CylinderMesh.new()
	neck.top_radius = 0.034
	neck.bottom_radius = 0.042
	neck.height = 0.06
	part(holder, neck, glass, c + Vector3(0, 0.15, 0))
	var lip := TorusMesh.new()
	lip.inner_radius = 0.03
	lip.outer_radius = 0.04
	part(holder, lip, glass, c + Vector3(0, 0.18, 0))
	var foot := CylinderMesh.new()
	foot.top_radius = 0.045
	foot.bottom_radius = 0.05
	foot.height = 0.012
	part(holder, foot, glass, c + Vector3(0, 0.006, 0))
	vase_flowers = Node3D.new()
	holder.add_child(vase_flowers)
	var wl := CylinderMesh.new()                                                                       # the water
	wl.top_radius = 0.066
	wl.bottom_radius = 0.05
	wl.height = 0.07
	part(vase_flowers, wl, water, c + Vector3(0, 0.05, 0))
	var stem_m := mat(Color("#4f8a3c"))
	var leaf_m := mat(Color("#5d9a44"), 0.7)
	var petal_ms := [mat(Color("#f28a2a"), 0.9), mat(Color("#f5a14a"), 0.9), mat(Color("#ee7a24"), 0.9)]     # (round 41: matte, "less glossy")
	var middle := mat(Color("#7a4a1e"), 0.7)
	var white := mat(Color("#f7f3ea"), 0.7)
	var neck_at := c + Vector3(0, 0.17, 0)
	# [tilt from upright, turn round, length]
	# (round 41, the user: "make the flowers on the desk slightly bigger so it looks a bit more like a bouquet") the heads
	# half as big again (FH), on stems a little longer, spread a little wider
	var FH := 1.5
	var flowers := [[0.0, 0.0, 0.3]]
	for i in 5:
		flowers.append([0.42, i * TAU / 5.0, 0.27])
	for i in 6:
		flowers.append([0.85, i * TAU / 6.0 + TAU / 12.0, 0.21])
	for k in flowers.size():
		var f: Array = flowers[k]
		var dir := Vector3(sin(f[0]) * sin(f[1]), cos(f[0]), sin(f[0]) * cos(f[1]))
		var b := basis_along(dir)
		var stem := CylinderMesh.new()
		stem.top_radius = 0.0035
		stem.bottom_radius = 0.0045
		stem.height = f[2]
		var sm := part(vase_flowers, stem, stem_m, neck_at - dir * 0.05 + dir * f[2] / 2.0)
		sm.basis = b
		var head: Vector3 = neck_at - dir * 0.05 + dir * f[2]
		# (round 41, the user: "The flowers in the forest look beautiful now. Could you have a similar flower in the flower
		# pot?") the hill's marigold: ten slim petals cupped round a dark middle
		for j in 10:
			var a := j * TAU / 10.0 + k * 0.4
			var out := b.x * cos(a) + b.z * sin(a)
			var pt := part(vase_flowers, sphere(0.014 * FH), petal_ms[(k + j) % 3], head + out * 0.02 * FH + dir * 0.004 * FH)
			pt.basis = Basis(out.cross(dir).normalized(), dir, out).rotated(out.cross(dir).normalized(), -0.3) * Basis.from_scale(Vector3(0.5, 0.25, 1.5))
		part(vase_flowers, sphere(0.010 * FH), middle, head + dir * 0.008 * FH)
	for i in 6:                                                                      # leaves between the low ring
		var dir2 := Vector3(sin(1.05) * sin(i * TAU / 6.0), cos(1.05), sin(1.05) * cos(i * TAU / 6.0))
		var lf := part(vase_flowers, sphere(0.02), leaf_m, neck_at + dir2 * 0.07)
		lf.basis = basis_along(dir2) * Basis.from_scale(Vector3(0.7, 3.2, 0.25))
	for i in 5:                                                                      # small white flowers between the rings
		var a2 := i * TAU / 5.0 + TAU / 10.0
		var dir3 := Vector3(sin(0.6) * sin(a2), cos(0.6), sin(0.6) * cos(a2))
		for j in 3:
			part(vase_flowers, sphere(0.008), white, neck_at - dir3 * 0.05 + dir3 * (0.2 + j * 0.008) + Vector3(0.008 * (j - 1), 0, 0.006 * (1 - j)))


func basis_along(dir: Vector3) -> Basis:
	# a basis whose y runs along dir (for a stem, a leaf, a flower head facing out)
	var y := dir.normalized()
	var x := y.cross(Vector3.FORWARD if absf(y.dot(Vector3.FORWARD)) < 0.9 else Vector3.RIGHT).normalized()
	return Basis(x, y, x.cross(y))


# ------------------------------------------------------------------ cats

func cat(col: Color, asleep: bool) -> Node3D:
	# chunky and round, like everything here: asleep, a curled loaf with its tail round its nose; awake,
	# sitting up straight, ears pricked, its tail curled round its paws, the tip flicking now and then
	var n := Node3D.new()
	var fur := mat(col, 0.9)
	var pink := mat(Color("#e8a0a0"))
	var dark := mat(col.darkened(0.45))
	var ear := PrismMesh.new()
	ear.size = Vector3(0.07, 0.08, 0.03)
	var tail := Node3D.new()
	tail.name = "Tail"
	n.add_child(tail)
	if asleep:
		var body := part(n, sphere(0.16), fur, Vector3(0, 0.09, 0), Vector3(1.2, 0.6, 1.0))
		body.name = "Body"
		part(n, sphere(0.085), fur, Vector3(0.13, 0.1, 0.07))
		for s in [-1, 1]:
			part(n, ear, fur, Vector3(0.15 + 0.03 * s, 0.18, 0.07 + 0.04 * s), Vector3.ONE, Vector3(0, 0.6, 0.3 * s))
		for k in 6:
			var a := -0.4 + k * 0.42
			part(tail, sphere(0.04 - k * 0.002), fur if k < 5 else dark, Vector3(cos(a) * 0.2, 0.05, sin(a) * 0.17), Vector3(1, 0.8, 1))
	else:
		var body := part(n, sphere(0.14), fur, Vector3(0, 0.15, 0), Vector3(0.9, 1.15, 1.0))
		body.name = "Body"
		part(n, sphere(0.1), fur, Vector3(0, 0.36, 0.05))
		for s in [-1, 1]:
			part(n, ear, fur, Vector3(0.055 * s, 0.46, 0.04), Vector3.ONE, Vector3(-0.1, 0, -0.25 * s))
			part(n, sphere(0.014), mat(Color("#d8c040"), 0.3), Vector3(0.04 * s, 0.38, 0.14))
			part(n, sphere(0.035), fur, Vector3(0.05 * s, 0.03, 0.11), Vector3(1, 0.6, 1.4))          # front paws
		part(n, sphere(0.012), pink, Vector3(0, 0.35, 0.15))
		for k in 7:
			var a := PI * 0.55 + k * 0.32
			part(tail, sphere(0.035), fur if k < 6 else dark, Vector3(cos(a) * 0.17, 0.03 + k * 0.004, sin(a) * 0.17), Vector3(1, 0.8, 1))
	return n


# ------------------------------------------------------------------ Sandra's notebook (round 22)
# On her desk, beside the birthday card: the things she wanted to do in Barcelona, written before she came. Each
# is where one of the city's missions starts; nothing points her to it (the user: "she can just find it").
# (round 35, the everything-visit: in the middle of the chest, where the drawer is opened from, so E gave either at
# random; at its left end now, the drawer from in front of its middle. It had never been seen: placed 400 m off, and
# 0.15 m above the chest's top)
const NOTEBOOK := [3.15, 1.5, 0.8]       # room x, y (row), height: on the bedside table (round 23; was on the desk)


func build_rosa_cat() -> void:
	if not main.D.interiors.has("int_sandra"):
		return
	rosa_cat = cat(Color("#d8d0c4"), false)
	main.indoor.add_child(rosa_cat)
	rosa_cat.global_position = room_point("int_sandra", ROSA_CAT[0], ROSA_CAT[1], ROSA_CAT[2])
	rosa_cat.rotation.y = ROSA_CAT[3]
	rosa_cat.scale = Vector3.ONE * 1.5


func build_notebook() -> void:
	var rid := "int_sandra"
	if not main.D.interiors.has(rid):
		return
	var nb := Node3D.new()
	main.indoor.add_child(nb)
	nb.global_position = room_point(rid, NOTEBOOK[0], NOTEBOOK[1], NOTEBOOK[2])      # (round 35: was .position, 400 m off)
	nb.rotation.y = 0.35
	var cover := BoxMesh.new()
	cover.size = Vector3(0.15, 0.018, 0.21)
	part(nb, cover, mat(Color("#2f5a46"), 0.6), Vector3(0, 0.009, 0))
	var pages := BoxMesh.new()
	pages.size = Vector3(0.142, 0.012, 0.2)
	part(nb, pages, mat(Color("#f3ecd8"), 0.9), Vector3(0.006, 0.009, 0))
	var band := BoxMesh.new()
	band.size = Vector3(0.152, 0.02, 0.008)
	part(nb, band, mat(Color("#8a2a2a"), 0.7), Vector3(0, 0.0095, 0.07))


func build_salamandreta() -> void:
	# a small trencadís salamander, green and gold like the dragon on the park's stairs, curled on the plinth in Gaudí's
	# house (interiors.py "plinth": a marble column, its top 1.06 m up) once Sandra has brought it back
	var rid := "int_gaudi_house"
	if not main.D.interiors.has(rid):
		return
	var at := Vector2.ZERO
	for th in main.D.interiors[rid].things:
		if th.get("kind", "") == "plinth":
			at = Vector2(th.pos[0], th.pos[1])
	if at == Vector2.ZERO:
		return
	salamandreta = Node3D.new()
	room_node(rid).add_child(salamandreta)
	salamandreta.global_position = room_point(rid, at.x, at.y, 1.06)                # (round 35: was .position)
	salamandreta.rotation.y = 0.5
	var green := mat(Color("#3f8f4a"), 0.35)
	var gold := mat(Color("#d9a640"), 0.35)
	var blue := mat(Color("#3a6fb0"), 0.35)
	for k in 5:                                        # the body, in a gentle S, the tail curling round
		var a := float(k) / 4.0
		part(salamandreta, sphere(0.055 - a * 0.025), green if k % 2 == 0 else gold,
			Vector3(-0.09 + a * 0.2, 0.05, sin(a * 3.0) * 0.05), Vector3(1.4, 0.8, 1.0))
	part(salamandreta, sphere(0.05), green, Vector3(0.15, 0.06, 0.02), Vector3(1.3, 0.8, 1.0))      # the head
	for sx in [-1.0, 1.0]:
		part(salamandreta, sphere(0.012), blue, Vector3(0.18, 0.09, 0.02 + sx * 0.025))              # eyes
		for fx in [-0.04, 0.08]:
			part(salamandreta, sphere(0.018), gold, Vector3(fx, 0.02, sx * 0.06), Vector3(1.0, 0.6, 1.6))   # feet
	part(salamandreta, sphere(0.03), gold, Vector3(-0.17, 0.035, -0.05), Vector3(1.6, 0.6, 1.0))     # the tail's tip


func build_biel_ball() -> void:
	# (round 41c, the user: "once the girl gets the ball back, could you put it at her feet where I've put it, where she
	# always turns back to face once she's done talking to you? And then the only option is to look at it. You can't
	# move it") just in front of where Biel stands facing when left alone, a touch to one side; a small post of its own
	var q: Dictionary = main.npcs.outdoor.get("biel", {})
	if q.is_empty():
		return
	var yaw: float = float(q.home_yaw)
	var fwd := Vector3(sin(yaw), 0.0, cos(yaw))
	var side := Vector3(fwd.z, 0.0, -fwd.x)
	var p: Vector3 = q.home + fwd * 0.5 + side * 0.18
	p.y = main.ground_at(p)
	biel_ball = Node3D.new()
	var s := SphereMesh.new()
	s.radius = 0.11
	s.height = 0.22
	part(biel_ball, s, mat(Color(0.78, 0.07, 0.05), 0.55), Vector3(0, 0.11, 0))     # (as the one she found: game.gd)
	biel_ball.position = p
	main.outdoor.add_child(biel_ball)
	main.add_post(main.static_body(main.LAYER_BODY), p.x, p.z, 0.13, 0.25)


func room_candidates(rid: String) -> Array:
	# things of ours to look at in a room (room metres, as the room's own things)
	if rid == "int_sandra":
		return [{"x": NOTEBOOK[0], "z": NOTEBOOK[1], "r": 1.3, "label": "Look at the notebook", "act": "notebook"},
			{"x": ROSA_CAT[0], "z": ROSA_CAT[1], "r": 1.4, "label": "Say hello to the cat", "act": "rosa_cat"}]
	return []


func candidates(p: Vector3) -> Array:
	var out := []
	for c in cats:
		out.append({"x": c.pos.x, "z": c.pos.z, "r": 1.6, "label": "Look at the cat", "act": "cat", "text": c.d.t})
	if biel_ball and biel_ball.visible:
		out.append({"x": biel_ball.position.x, "z": biel_ball.position.z, "r": 1.3, "label": "Look at the ball", "act": "cat",
			"text": BIEL_BALL_TEXT, "prio": 0.9})
	return out


# ------------------------------------------------------------------ every frame

func refresh() -> void:
	# what the story says should be there
	var S: Dictionary = main.game.S
	if party:
		party.visible = main.game.party_on() and main.game.S.missions.has("gift")
	if vase_flowers:
		vase_flowers.visible = S.flags.get("vaseFull", false)
	if salamandreta:
		salamandreta.visible = S.flags.get("guellBack", false)
	if biel_ball:
		biel_ball.visible = main.game.m_done("ball")


func tick(dt: float) -> void:
	t += dt
	if main.where == "in":
		refresh()
		if party and party.visible:
			for b in balloons:
				b.node.position.y = b.y + sin(t * 1.3 + b.ph) * 0.05
				b.node.rotation.z = sin(t * 0.9 + b.ph) * 0.06
			for f in flames:
				if f is MeshInstance3D:
					f.scale.y = 1.8 + sin(t * 17.0 + f.position.x * 40.0) * 0.4
				else:
					f.light_energy = 0.45 + sin(t * 13.0) * 0.08
		return
	update_pollen()
	for c in cats:
		var n: Node3D = c.node
		var body: Node3D = n.get_node("Body")
		if c.d.sleep:
			body.scale.y = 0.6 * (1.0 + 0.05 * sin(t * 1.6 + c.pos.x))                 # breathing
		else:
			var flick := maxf(0.0, sin(t * 0.7 + c.pos.z)) ** 8.0
			n.get_node("Tail").rotation.y = 0.35 * flick * sin(t * 9.0)


const SHROOM_CLUMPS := 38           # (round 38, the user: "There should be a quarter as many"; was 150)
const SHROOM_CHUNK := 32.0        # metres: each square of the wood is drawn, or not, by its distance


func build_mushrooms() -> void:
	var trunks: Array = main.D.get("forest_trees", [])
	if trunks.is_empty():
		return
	var segs := []                 # the paths' stretches: [a, b, half width]
	for path in main.D.get("forest_paths", []):
		var pts: Array = path.pts
		for i in pts.size() - 1:
			segs.append([Vector2(pts[i][0], pts[i][1]), Vector2(pts[i + 1][0], pts[i + 1][1]), float(path.get("w", 2.0)) / 2.0])
	var rng := RandomNumberGenerator.new()
	rng.seed = 2210
	var shrooms := {}              # chunk -> [Transform3D]
	var placed := 0
	var tries := 0
	while placed < SHROOM_CLUMPS and tries < 20000:
		tries += 1
		# beside a trunk, on the side away from nothing in particular
		var t: Array = trunks[rng.randi() % trunks.size()]
		var a := rng.randf() * TAU
		var r := rng.randf_range(0.55, 1.6)
		var c := Vector2(t[0] + cos(a) * r, t[1] + sin(a) * r)
		if c.x > 155.0 or c.y > 100.0:
			continue               # (past the map's edge, or down by the beach)
		var clear := true
		for sg in segs:
			var q: Vector2 = Geometry2D.get_closest_point_to_segment(c, sg[0], sg[1])
			if q.distance_to(c) < sg[2] + 1.2:
				clear = false
				break
		if not clear:
			continue
		placed += 1
		var n := 2 + int(rng.randf() < 0.5)
		for k in n:
			var o := Vector2(cos(k * 2.3 + a), sin(k * 2.3 + a)) * rng.randf_range(0.05, 0.13)
			var p := Vector3(c.x + o.x, 0.0, c.y + o.y)
			p.y = main.ground_at(p)
			var s := rng.randf_range(0.7, 1.15) * (1.0 if k == 0 else 0.8)
			var tf := Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3(s, s, s)), p)
			var key := Vector2i(floori(p.x / SHROOM_CHUNK), floori(p.z / SHROOM_CHUNK))
			if not shrooms.has(key):
				shrooms[key] = []
			shrooms[key].append(tf)
	# one mushroom: a pale stem 7 cm tall, a round white cap 9 cm across
	var stem := CylinderMesh.new()
	stem.top_radius = 0.012
	stem.bottom_radius = 0.016
	stem.height = 0.07
	stem.radial_segments = 8
	stem.rings = 1
	var cap := SphereMesh.new()
	cap.radius = 0.045
	cap.height = 0.045
	cap.is_hemisphere = true
	cap.radial_segments = 12
	cap.rings = 4
	var stem_m := StandardMaterial3D.new()
	stem_m.albedo_color = Color(0.9, 0.87, 0.8)
	stem_m.roughness = 0.8
	var cap_m := StandardMaterial3D.new()
	cap_m.albedo_color = Color(0.97, 0.95, 0.9)
	cap_m.roughness = 0.6
	for key in shrooms:
		var tfs: Array = shrooms[key]
		for part in [[stem, stem_m, Vector3(0, 0.035, 0)], [cap, cap_m, Vector3(0, 0.068, 0)]]:
			var mm := MultiMesh.new()
			mm.transform_format = MultiMesh.TRANSFORM_3D
			mm.mesh = part[0]
			mm.instance_count = tfs.size()
			for i in tfs.size():
				var tf: Transform3D = tfs[i]
				mm.set_instance_transform(i, tf.translated_local(part[2]))
			var mi := MultiMeshInstance3D.new()
			mi.multimesh = mm
			mi.material_override = part[1]
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			mi.visibility_range_end = 40.0
			mi.visibility_range_end_margin = 6.0
			mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
			main.outdoor.add_child(mi)
	print("SHROOMS %d clumps in %d squares (%d tries)" % [placed, shrooms.size(), tries])
