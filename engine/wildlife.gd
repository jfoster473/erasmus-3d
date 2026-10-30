# The 2D game's wildlife, in the same places (its pigeons, bflies and gulls):
#   pigeons     nine on the Rambla, pecking about; they clatter up when Sandra comes close, circle off,
#               and come back down to their spot once she has gone by
#   butterflies a few, by day, in the woods along the paths (round 25: the white one by Trufa's glade; the others
#               white, yellow or blue), drifting in slow loops with their wings beating: with
#               a proper butterfly's wings (a big rounded forewing with a grey tip, a smaller hindwing
#               behind), a slim dark body and two feelers (round 20: they were flat paper squares)
#   fireflies   at night, three to each of those spots, small and soft, glowing on and off
#   gulls       six over the beach, wheeling in long ellipses
extends Node

const T := 3.3
const OX := 55
const OY := 45
const BFLY_AT_DOG := [97, 50]   # (the 2D game's butterfly by Trufa's glade; its others, on the beach and in town, are gone)

var main: Node3D
var pigeons: Array = []
var bflies: Array = []
var flies: Array = []
var gulls: Array = []
var rng := RandomNumberGenerator.new()
var t := 0.0
var px0 := 49.3             # the promenade's edges (tiles), where the pigeons keep to
var px1 := 52.7


func setup(m: Node3D) -> void:
	main = m
	rng.seed = 1714
	var prom: Array = main.game.data.RAMBLA_PROM
	px0 = prom[0] + 0.3
	px1 = prom[1] + 0.7
	for i in 9:
		var home := w(prom[0] + 0.5 + rng.randf() * 3.0 - 0.5, 38.0 + i * 4.3 + rng.randf() - 0.5)    # (on the Rambla's promenade)
		var p := {"node": pigeon(), "home": home, "pos": home, "vel": Vector3.ZERO, "st": "ground", "t": rng.randf() * 5.0, "yaw": rng.randf() * TAU}
		main.outdoor.add_child(p.node)
		p.node.scale = Vector3.ONE * 1.6                    # (toy-sized, like everything here)
		pigeons.append(p)
	# (round 25, the user: "Keep the white butterfly near the dog; otherwise they should be white, yellow and blue. Make
	# the butterflies sparse, only a few in each forest along the paths") the white one by Trufa's glade, three along the
	# wood's main path and three along the hill path; fireflies at the same spots after dark, three to each
	var spots := [[w(BFLY_AT_DOG[0], BFLY_AT_DOG[1]), WING_WHITE]]
	var cols := [WING_COLS[0], WING_COLS[1], WING_COLS[2]]
	for fp in main.D.get("forest_paths", []):
		if fp.get("kind", "") == "trunk":
			var pts: Array = fp.pts
			for k in 3:
				spots.append([beside(pts, (k + 0.6) / 3.6), cols[k]])
	var Nn: Dictionary = main.D.get("north", {})
	if Nn.has("path"):
		var hp: Array = []
		for q in Nn.path:
			hp.append([q[0], q[1]])
		for k in 3:
			spots.append([beside(hp, (k + 0.5) / 5.0), cols[(k + 1) % 3]])
	for sp in spots:
		var at: Vector3 = sp[0]
		at.y = main.ground_at(at)
		var b := {"node": butterfly(sp[1]), "at": at, "ph": rng.randf() * 9.0, "r": 0.5}
		main.outdoor.add_child(b.node)
		b.node.scale = Vector3.ONE * 2.2
		bflies.append(b)
		for k in 3:
			var f := {"node": firefly(), "at": at, "k": k, "ph": rng.randf() * 9.0, "r": 0.5}
			main.outdoor.add_child(f.node)
			flies.append(f)
	for i in 6:
		var g := {"node": gull(), "c": w(12 + i * 15 + rng.randf() * 6, 90 + rng.randf() * 3), "r": (2.0 + rng.randf() * 2.5) * T,
			"sp": (0.25 + rng.randf() * 0.25) * (1.0 if i % 2 else -1.0), "ph": rng.randf() * 7.0, "h": 7.0 + rng.randf() * 5.0}
		main.outdoor.add_child(g.node)
		g.node.scale = Vector3.ONE * 1.8
		gulls.append(g)


func w(X: float, Y: float) -> Vector3:
	var p := Vector3((X + 0.5 - OX) * T, 0.0, (Y + 0.5 - OY) * T)
	p.y = main.ground_at(p)
	return p


func mat(col: Color, glow := 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = 0.8
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	if glow > 0.0:
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.emission_enabled = true
		m.emission = col
		m.emission_energy_multiplier = glow
	return m


func add(n: Node3D, mesh: Mesh, m: Material, at: Vector3, sc := Vector3.ONE) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = m
	mi.position = at
	mi.scale = sc
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	n.add_child(mi)
	return mi


func pigeon() -> Node3D:
	# a plump grey-blue body, a darker head with a little beak, and two wings that open when it flies
	var n := Node3D.new()
	var grey := mat(Color(0.55, 0.58, 0.66))
	var body := SphereMesh.new()
	body.radius = 0.11
	body.height = 0.2
	add(n, body, grey, Vector3(0, 0.13, 0), Vector3(1, 0.9, 1.5))
	var head := SphereMesh.new()
	head.radius = 0.055
	head.height = 0.11
	add(n, head, mat(Color(0.38, 0.42, 0.52)), Vector3(0, 0.25, 0.14)).name = "Head"
	var beak := BoxMesh.new()
	beak.size = Vector3(0.02, 0.02, 0.05)
	add(n, beak, mat(Color(0.9, 0.7, 0.4)), Vector3(0, 0.25, 0.2))
	var wing := BoxMesh.new()
	wing.size = Vector3(0.22, 0.01, 0.14)
	for sx in [-1, 1]:
		var piv := Node3D.new()
		piv.name = "WingL" if sx < 0 else "WingR"
		piv.position = Vector3(sx * 0.06, 0.18, 0)
		n.add_child(piv)
		add(piv, wing, grey, Vector3(sx * 0.11, 0, 0))
	return n




const WING_COLS := [Color(0.98, 0.92, 0.42), Color(0.55, 0.68, 0.96), Color(0.97, 0.96, 0.92)]   # brimstone, blue, white
const WING_WHITE := Color(0.97, 0.96, 0.92)
var wing_mats := {}


func wing_texture(base := Color(0.97, 0.96, 0.92)) -> ImageTexture:
	# one side's pair of wings, seen from above: x from the body (0) out to the tip, y from the front (0) back
	var S := 64
	var img := Image.create(S, S, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for y in S:
		for x in S:
			var u := (x + 0.5) / S
			var v := (y + 0.5) / S
			# the forewing: a rounded blade sweeping forwards and out; the hindwing: a smaller round lobe behind
			var fore := pow((u - 0.5) / 0.5, 2.0) + pow((v - 0.3 + 0.18 * u) / 0.28, 2.0) < 1.0
			var hind := pow((u - 0.33) / 0.33, 2.0) + pow((v - 0.68) / 0.27, 2.0) < 1.0
			if not (fore or hind) or u < 0.03:
				continue
			var c := base
			if fore and u > 0.72 and v < 0.32 + 0.1 * u:
				c = Color(0.36, 0.35, 0.34)                         # the grey-black tip
			elif fore and absf(u - 0.58) < 0.07 and absf(v - 0.32) < 0.06:
				c = Color(0.4, 0.4, 0.4)                            # a spot
			elif u < 0.14:
				c = base.darkened(0.1)                              # dusted near the body
			var vein := absf(sin(atan2(v - 0.45, u) * 7.0)) < 0.08 and u > 0.2
			if vein:
				c = c.darkened(0.12)
			img.set_pixel(x, y, c)
	return ImageTexture.create_from_image(img)


func butterfly(col := Color(0.97, 0.96, 0.92)) -> Node3D:
	var n := Node3D.new()
	if not wing_mats.has(col):
		var wm := StandardMaterial3D.new()
		wm.albedo_texture = wing_texture(col)
		wm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
		wm.alpha_scissor_threshold = 0.5
		wm.cull_mode = BaseMaterial3D.CULL_DISABLED
		wm.roughness = 0.75
		wm.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR
		wing_mats[col] = wm
	var wing_mat: StandardMaterial3D = wing_mats[col]
	var wing := QuadMesh.new()
	wing.size = Vector2(0.1, 0.1)
	for sx in [-1, 1]:
		var piv := Node3D.new()
		piv.name = "WingL" if sx < 0 else "WingR"
		n.add_child(piv)
		# (flat, the hinge along the body; the left one mirrored)
		var w := add(piv, wing, wing_mat, Vector3(sx * 0.05, 0, 0.004), Vector3(sx, 1, 1))
		w.rotation.x = PI / 2.0                                 # (the wings' front edge forwards, +z)
	var dark := mat(Color(0.2, 0.19, 0.18))
	var body := CapsuleMesh.new()
	body.radius = 0.006
	body.height = 0.075
	add(n, body, dark, Vector3(0, 0.002, 0.004)).rotation.x = PI / 2.0
	var feeler := CylinderMesh.new()
	feeler.top_radius = 0.0012
	feeler.bottom_radius = 0.0012
	feeler.height = 0.04
	for sx in [-1, 1]:
		var f := add(n, feeler, dark, Vector3(sx * 0.007, 0.008, 0.05))
		f.rotation = Vector3(1.1, 0, -sx * 0.35)
	return n


func beside(pts: Array, f: float) -> Vector3:
	# a point a little to the side of a path (a list of [x, z]), a fraction f of the way along it
	var L := 0.0
	for i in pts.size() - 1:
		L += Vector2(pts[i][0], pts[i][1]).distance_to(Vector2(pts[i + 1][0], pts[i + 1][1]))
	var want := L * f
	for i in pts.size() - 1:
		var a := Vector2(pts[i][0], pts[i][1])
		var b := Vector2(pts[i + 1][0], pts[i + 1][1])
		var d := a.distance_to(b)
		if want <= d and d > 0.0:
			var p := a.lerp(b, want / d)
			var side := (b - a).normalized().orthogonal() * 1.8
			return Vector3(p.x + side.x, 0, p.y + side.y)
		want -= d
	return Vector3(pts[-1][0], 0, pts[-1][1])


func firefly() -> Node3D:
	# (round 25: smaller and softer, "subtle")
	var n := Node3D.new()
	var s := SphereMesh.new()
	s.radius = 0.035
	s.height = 0.07
	add(n, s, mat(Color(0.86, 1.0, 0.55), 3.0), Vector3.ZERO)
	return n


func gull() -> Node3D:
	# white wings in a shallow V
	var n := Node3D.new()
	var wing := BoxMesh.new()
	wing.size = Vector3(0.45, 0.015, 0.14)
	var white := mat(Color(0.98, 0.98, 0.96))
	for sx in [-1, 1]:
		var piv := Node3D.new()
		piv.name = "WingL" if sx < 0 else "WingR"
		n.add_child(piv)
		add(piv, wing, white, Vector3(sx * 0.22, 0, 0))
	var body := SphereMesh.new()
	body.radius = 0.06
	body.height = 0.12
	add(n, body, white, Vector3.ZERO, Vector3(1, 1, 2.6))
	return n


func flap(n: Node3D, a: float) -> void:
	n.get_node("WingL").rotation.z = a
	n.get_node("WingR").rotation.z = -a


func tick(dt: float) -> void:
	t += dt
	var outside: bool = main.where == "out"
	var night: bool = main.P.get("night", false)
	var sandra: Vector3 = main.player.global_position
	for p in pigeons:
		p.t += dt
		var n: Node3D = p.node
		var d := Vector2(p.pos.x - sandra.x, p.pos.z - sandra.z).length()
		match p.st:
			"ground":
				if d < 1.8 * T and outside:
					p.st = "fly"                                   # off they go, away from her
					var a := atan2(p.pos.z - sandra.z, p.pos.x - sandra.x) + rng.randf_range(-0.5, 0.5)
					p.vel = Vector3(cos(a), 0, sin(a)) * 5.0 * T / 3.0
					p.t = 0.0
				elif rng.randf() < dt * 0.4:
					var hop := Vector3(rng.randf_range(-0.3, 0.3), 0, rng.randf_range(-0.3, 0.3))
					p.pos = p.pos + hop
					p.pos.x = clampf(p.pos.x, (px0 - OX) * T, (px1 - OX) * T)          # they stay on the promenade
					p.yaw = atan2(hop.x, hop.z)
				p.pos.y = main.ground_at(p.pos)
				flap(n, 0.0)
				n.get_node("Head").position.y = 0.25 - 0.05 * maxf(0.0, sin(p.t * 6.0))   # pecking
			"fly":
				p.pos = p.pos + p.vel * dt
				p.pos.y = minf(p.pos.y + dt * 3.0, main.ground_at(p.pos) + 4.0)
				p.yaw = atan2(p.vel.x, p.vel.z)
				flap(n, sin(t * 28.0) * 0.9)
				if p.t > 2.2:
					p.st = "land"
					p.t = 0.0
			"land":
				var to: Vector3 = p.home + Vector3(sin(p.home.z) * 0.8, 0, 0)
				to.x = clampf(to.x, (px0 - OX) * T, (px1 - OX) * T)
				var g: float = main.ground_at(to)
				p.pos.x = lerpf(p.pos.x, to.x, dt * 1.2)
				p.pos.z = lerpf(p.pos.z, to.z, dt * 1.2)
				p.pos.y = maxf(g, p.pos.y - dt * 1.5)
				p.yaw = lerp_angle(p.yaw, atan2(to.x - p.pos.x, to.z - p.pos.z), dt * 4.0)
				flap(n, sin(t * 20.0) * 0.6)
				if p.pos.y <= g + 0.01 and d > 2.5 * T:
					p.st = "ground"
		n.position = p.pos
		n.rotation.y = p.yaw
		# (round 36's play-through: one flew off from her straight into the camera and filled half the screen grey; a
		# bird that close to the lens isn't drawn, as people the camera is inside aren't)
		n.visible = main.cam.global_position.distance_to(p.pos + Vector3(0, 0.25, 0)) > 1.0
	for b in bflies:
		var n: Node3D = b.node
		n.visible = outside and not night
		if not n.visible:
			continue
		var rr: float = b.get("r", 1.0)
		var at: Vector3 = b.at + Vector3(sin(t * 0.5 + b.ph) * 1.5 * T * rr, 0.0, cos(t * 0.37 + b.ph) * 1.2 * T * rr)
		at.y = main.ground_at(at) + 0.7 + 0.25 * sin(t * 1.3 + b.ph)       # (round 24: over the ground under it, on a hill too)
		n.rotation.y = atan2(at.x - n.position.x, at.z - n.position.z)
		n.position = at
		flap(n, absf(sin(t * 12.0 + b.ph)) * 1.2)
	for f in flies:
		var n: Node3D = f.node
		n.visible = outside and night
		if not n.visible:
			continue
		var fr: float = f.get("r", 1.0)
		var fp: Vector3 = f.at + Vector3(sin(t * 0.3 + f.k * 2.0 + f.ph) * 2.5 * T * fr, 0.0, cos(t * 0.23 + f.k) * 2.0 * T * fr)
		fp.y = main.ground_at(fp) + 0.9 + 0.3 * sin(t * 0.7 + f.ph)
		n.position = fp
		n.scale = Vector3.ONE * maxf(0.05, sin(t * 2.0 + f.k * 1.7 + f.ph))       # glowing on and off
	for g in gulls:
		var n: Node3D = g.node
		var a: float = t * g.sp + g.ph
		var at: Vector3 = g.c + Vector3(cos(a) * g.r * 1.6, g.h, sin(a) * g.r * 0.6)
		n.rotation.y = atan2(at.x - n.position.x, at.z - n.position.z)
		n.position = at
		flap(n, 0.25 + sin(t * 7.0 + g.ph) * 0.35)
