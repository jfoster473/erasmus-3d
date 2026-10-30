# The 2D game's people (from2d/data2d.json NPCS): each where the 2D game puts them, in the street or
# in a room, dressed in their own colours. Each is one of a few Meshy characters (a young man, an older
# man, the Sandra models, Rosa's old look, Montse's), recoloured through character.gdshader's swaps.
# Outdoors they potter about within r tiles of home (r = 0: they stay put: shopkeepers, the guard, the
# statue), turn to face Sandra when she talks to them, and step aside if she walks into them.
# Indoors, a room's people are made when Sandra goes in and cleared when she leaves.
# What they say is game.gd's business; this only places and moves them.
extends Node

const T := 3.3
const OX := 55
const OY := 45
const WANDER_SPEED := 1.0
const GREY := ["#a9a39b", "#e6e1d8"]

var main: Node3D
var data: Dictionary
var outdoor: Dictionary = {}     # id -> person
var indoor: Dictionary = {}
var states := {}                 # file -> [GLTFDocument, GLTFState]
var rng := RandomNumberGenerator.new()


func setup(m: Node3D, d: Dictionary) -> void:
	main = m
	data = d
	rng.seed = 99
	for id in data.NPCS:
		var n: Dictionary = data.NPCS[id]
		if n.at[0] == "world":
			outdoor[id] = make_person(id, n, main.outdoor, world_pos(n.at[1], n.at[2]))


func world_pos(X: float, Y: float) -> Vector3:
	var p := Vector3((X + 0.5 - OX) * T, 0.0, (Y + 0.5 - OY) * T)
	p.y = main.ground_at(p)
	return p


func variant(look: Dictionary) -> int:
	# (round 37, the user: "replace some of the duplicated people… we just reduce the duplication") which of a body's two
	# Meshy versions someone gets: fixed by their own look, so the same person is always the same, and about half each
	# (round 41: the clothes were recoloured; 'vkey' is the old colours, so everyone keeps the model they had)
	var key: String = String(look.get("vkey", String(look.get("top", "")) + String(look.get("hair", "")) + String(look.get("legs", "")) + String(look.get("hs", ""))))
	return absi(hash(key)) % 2


# (round 39, the user: "only use the tall guy to replace all of the other random young men when Sandra is also changed
# to the tall version") off until Sandra has a taller model; then every ordinary young man is him, not half of them
const USE_MAN3 := false


func model_for(look: Dictionary) -> String:
	var hs: String = look.get("hs", "short")
	var grey: bool = String(look.get("hair", "")).to_lower() in GREY
	var male: bool = hs in ["short", "spiky", "bald"] or look.get("beard", false) or look.get("moustache", false) \
		or (hs == "curly" and not look.get("skirt", false))
	if look.get("kid", false):
		return "child.glb" if has_model("child.glb") else "passerby.glb"
	if look.get("hat", "") == "hardhat" and has_model("workman.glb"):
		# (round 37, the user: "the whole point of going back to meshy is to give them proper hats") the workmen are
		# their own Meshy model, the hard hat part of it; each crew's overalls in its own colour (swaps_for)
		return "workman.glb"
	if look.get("statue", false) or male:
		if grey and has_model("oldman.glb"):
			return "oldman.glb"
		# shopkeepers, uniforms, beards and moustaches: the stouter, older man; the rest the young one
		var settled: bool = look.get("beard", false) or look.get("moustache", false) or look.has("apron") or look.get("settled", false) \
			or look.get("grin", false) \
			or look.get("shop", false) or look.get("hat", "") in ["police", "guard", "hardhat"]
		if settled and has_model("man2.glb"):
			return "man2.glb"
		# (round 39, the user: "Please get rid of the thin man. He doesn't fit. Just keep in in the background of the code")
		# the bearded young man in the polo shirt (round 37, man3.glb) is no longer handed out; his model and settings
		# stay, should he come back (USE_MAN3)
		if USE_MAN3 and has_model("man3.glb"):
			return "man3.glb"
		return "man.glb" if has_model("man.glb") else "sandra_a.glb"
	if grey:
		# (round 37) Montse keeps her own model (she sits on her bench); other grey-haired women half the new old lady
		if look.get("id", "") != "montse" and variant(look) == 1 and has_model("oldlady.glb"):
			return "oldlady.glb"
		return "montse.glb"
	if variant(look) == 1 and has_model("woman2.glb"):
		return "woman2.glb"                         # (round 37: the young woman with the bob)
	if has_model("woman.glb"):
		return "woman.glb"                  # (the Sandra models are kept for Sandra, so no one looks like her twin)
	return {"curly": "passerby.glb", "long": "sandra_b.glb"}.get(hs, "sandra_a.glb")


func has_model(f: String) -> bool:
	return FileAccess.file_exists(main.asset_path("meshy/" + f))


func scene_for(file: String) -> Node3D:
	if not states.has(file):
		var doc := GLTFDocument.new()
		var st := GLTFState.new()
		if doc.append_from_file(main.asset_path("meshy/" + file), st) != OK:
			return null
		states[file] = [doc, st]
	return states[file][0].generate_scene(states[file][1]) as Node3D


func swaps_for(file: String, look: Dictionary) -> Array:
	# which parts of each model take the person's own colours (character.gdshader)
	var top: String = look.get("top", "#888888")
	var legs: String = look.get("legs", "#444444")
	var hair: String = look.get("hair", "#2b1d17")
	if look.get("statue", false):
		return [{"hue": [0, 360], "sat": [0.0, 1.0], "val": [0.0, 1.0], "h": [0.0, 3.0], "col": "#b08a3e", "ref": 0.45}]
	match file:
		"man3.glb":
			# (round 37, the user: "the people in the mock-up images… looked really nice… Dropping each of these into the
			# game would be amazing") he wears his own clothes and hair, exactly as drawn — no recolouring
			return []
		"woman2.glb":
			# (round 41, the user: "give all the different people different colored clothes": every woman with the bob wore
			# the same yellow top and green skirt) linear light: the top golden yellow, sat 0.82+, 0.44 bright (the skin
			# is the same hue but paler); the skirt very dark green, 0.045. Her hair, face and sandals keep their own.
			return [{"hue": [18, 42], "sat": [0.8, 1.0], "val": [0.5, 1.0], "h": [0.4, 1.7], "col": top, "ref": 0.44},
				{"hue": [95, 185], "sat": [0.3, 1.0], "val": [0.0, 0.12], "h": [0.1, 1.0], "col": legs, "ref": 0.045}]
		"oldlady.glb":
			# (round 41, as above) linear light: her pale blue blouse, 0.39 bright; her charcoal skirt, 0.067
			return [{"hue": [195, 240], "sat": [0.25, 0.65], "val": [0.3, 0.7], "h": [0.4, 1.2], "col": top, "ref": 0.39},
				{"hue": [0, 360], "sat": [0.0, 0.35], "val": [0.02, 0.13], "h": [0.1, 0.65], "col": legs, "ref": 0.067}]
		"workman.glb":
			# (round 37) his blue overalls take the crew's colour (look.top): in linear light, mid blue, 0.078 bright
			return [{"hue": [188, 252], "sat": [0.3, 1.0], "val": [0.0, 1.0], "h": [0.0, 1.55], "col": top, "ref": 0.078}]
		"man.glb":
			# (round 38, the user: the patterned shirts flickered — "just make the pattern shirts plain… different colors to
			# differentiate the different people". His white shirt sits at 0.45–0.55 bright in linear light, right on the old
			# 0.55 edge, so half of it took the colour and half stayed white, and the halves swapped as he moved: the whole
			# shirt now, from 0.25 up, its own colour at its usual brightness)
			return [{"hue": [0, 360], "sat": [0.0, 0.25], "val": [0.25, 1.0], "h": [0.5, 1.15], "col": top, "ref": 0.52},
				{"hue": [180, 245], "sat": [0.18, 1.0], "val": [0.0, 1.0], "h": [0.05, 0.75], "col": legs, "ref": 0.32},
				{"hue": [0, 60], "sat": [0.25, 1.0], "val": [0.0, 0.3], "h": [1.15, 3.0], "col": hair, "ref": 0.12}]
		"man2.glb":
			# (linear light: light blue shirt, dark brown trousers, dark brown hair and moustache)
			return [{"hue": [195, 240], "sat": [0.3, 1.0], "val": [0.2, 1.0], "h": [0.6, 1.6], "col": top, "ref": 0.29},
				{"hue": [5, 35], "sat": [0.5, 1.0], "val": [0.0, 0.09], "h": [0.13, 0.75], "col": legs, "ref": 0.023},
				{"hue": [5, 35], "sat": [0.4, 1.0], "val": [0.0, 0.1], "h": [1.45, 3.0], "col": hair, "ref": 0.03}]
		"oldman.glb":
			return [{"hue": [10, 45], "sat": [0.3, 1.0], "val": [0.15, 0.7], "h": [0.45, 1.2], "col": top, "ref": 0.3},
				{"hue": [0, 360], "sat": [0.0, 0.18], "val": [0.12, 0.5], "h": [0.08, 0.6], "col": legs, "ref": 0.3}]
		"woman.glb":
			# (the texture is read in linear light: her navy trousers and dark hair are very dark there)
			return [{"hue": [150, 210], "sat": [0.12, 1.0], "val": [0.1, 1.0], "h": [0.45, 1.15], "col": top, "ref": 0.26},
				{"hue": [190, 250], "sat": [0.3, 1.0], "val": [0.0, 0.1], "h": [0.03, 0.7], "col": legs, "ref": 0.009},
				{"hue": [0, 45], "sat": [0.2, 1.0], "val": [0.0, 0.12], "h": [1.1, 3.0], "col": hair, "ref": 0.012}]
		"montse.glb":
			return [{"hue": [280, 345], "sat": [0.25, 1.0], "val": [0.0, 1.0], "h": [0.3, 1.2], "col": top, "ref": 0.17}]
		"child.glb":
			# (linear light, as the shader reads the texture: blue trousers, pink top, ginger ponytail)
			return [{"hue": [195, 235], "sat": [0.5, 1.0], "val": [0.03, 0.6], "h": [0.02, 0.42], "col": legs, "ref": 0.054},
				{"hue": [318, 356], "sat": [0.25, 1.0], "val": [0.3, 1.0], "h": [0.38, 0.8], "col": top, "ref": 0.37},
				{"hue": [5, 30], "sat": [0.75, 1.0], "val": [0.04, 0.6], "h": [0.62, 1.4], "col": hair, "ref": 0.1}]
		"passerby.glb":
			return [{"hue": [355, 28], "sat": [0.5, 1.0], "val": [0.15, 0.62], "h": [0.12, 0.62], "col": legs, "ref": 0.3}]
		_:
			return [{"hue": [330, 40], "sat": [0.42, 1.0], "val": [0.0, 0.36], "h": [0.62, 2.0], "col": hair, "ref": 0.16},
				{"hue": [0, 360], "sat": [0.0, 0.14], "val": [0.6, 1.0], "h": [0.42, 1.0], "col": top, "ref": 0.85},
				{"hue": [180, 240], "sat": [0.2, 1.0], "val": [0.0, 1.0], "h": [0.05, 0.55], "col": legs, "ref": 0.3}]


# (round 39, the user, of a red-haired woman: "The red-haired girl has red eyes. Her face should be like everyone else,
# not red") the eyes, brows and mouth are painted in the same dark brown as the hair, so a new hair colour took them
# too. Each recoloured model's face, measured on the model (its own units, before MODEL_SCALE): from the chin to just
# under the fringe, and how far out to each side the eyes and brows go, the hair framing the face kept outside it.
# Nothing there facing forwards is recoloured (character.gdshader face_*).
# (round 41, the user, of the bun-haired women: dark marks "like their extra eyebrows": the fringe's lower edge lay in
# the face and kept the model's own dark brown; option 3 picked: the face stops under the brows, so the fringe and the
# brows take the hair's colour, the eyes stay dark)
const FACE := {"man.glb": [1.03, 1.25, 0.16], "man2.glb": [1.27, 1.375, 0.14], "woman.glb": [1.055, 1.10, 0.13],
	"child.glb": [0.66, 0.775, 0.13]}


func keep_face(file: String, mats: Array, k: float) -> void:
	var f: Array = FACE.get(file, []).duplicate()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--facetop=") and not f.is_empty():          # (to try a lower top: --facetop=<model units>)
			f[1] = float(a.trim_prefix("--facetop="))
	for mat in mats:
		mat.set_shader_parameter("face_on", not f.is_empty())
		if not f.is_empty():
			mat.set_shader_parameter("face_y", Vector2(f[0], f[1]) * k)
			mat.set_shader_parameter("face_w", f[2])


func make_person(id: String, n: Dictionary, parent: Node3D, pos: Vector3) -> Dictionary:
	var look: Dictionary = n.get("look", {}).duplicate()
	if id == "tomas" and main.game and main.game.m_done("hat"):
		look.hat = "cap"                     # (round 27, from the 2D game: once his cap is returned, he wears it again)
		look.hatc = "#4a6e8a"
	look.shop = n.get("shop", false)
	look.id = id
	var file: String = main.ROSA_MODEL if id == "rosa" else model_for(look)     # Rosa: the second Meshy Sandra, in her own colours
	var holder := Node3D.new()
	parent.add_child(holder)
	holder.position = pos
	var sc := scene_for(file)
	var mm: Dictionary = main.load_meshy_sandra(file, holder, sc) if sc else {}
	if mm.is_empty():
		holder.queue_free()
		return {}
	if look.get("kid", false) and file != "child.glb":
		sc.scale *= 0.72
	main.apply_look(mm.mats, main.ROSA_LOOK if id == "rosa" else swaps_for(file, look))
	keep_face(file, mm.mats, sc.scale.y)
	for mat in mm.mats:
		mat.set_shader_parameter("ground_y", holder.global_position.y)
	var ap: AnimationPlayer = mm.ap
	if ap:
		for an in ["Walking", "Idle_4"]:
			if ap.has_animation(an):
				ap.get_animation(an).loop_mode = Animation.LOOP_LINEAR
		if ap.has_animation("Idle_4"):
			mm.anims.idle = "Idle_4"
		ap.play(mm.anims.idle)
		ap.seek(rng.randf() * 2.0, true)
	accessories(holder, mm, file, look, n)
	var body := AnimatableBody3D.new()
	body.sync_to_physics = false             # (round 37: so it follows them when they are pushed aside, not stays behind)
	body.collision_layer = main.LAYER_BODY
	body.collision_mask = 0
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.28
	cap.height = 1.3
	cs.shape = cap
	cs.position.y = 0.65
	body.add_child(cs)
	holder.add_child(body)
	# facing the 2D sprites' way (PI) unless the data says which way they stand ('yaw', radians: 0 faces +z, south)
	var yaw0: float = float(n.get("yaw", PI))
	holder.rotation.y = yaw0
	# (round 38, the user, of Jaume: "not leaning over"; round 40, of everyone: "can you give the people better
	# posture?") the head brought up over the neck, for every person (posture.gd)
	stand_tall(mm, file)
	# (round 40, the user: "The guy with the kite should be looking up at it") his head tipped back towards it
	if n.get("kite", false) and mm.get("posture") != null:
		mm.posture.head_aim = KITE_LOOK
	var q := {"id": id, "d": n, "holder": holder, "m": mm, "home": pos, "target": pos, "wait": rng.randf_range(1.0, 4.0),
		"moving": 0.0, "yaw": yaw0, "home_yaw": yaw0, "talking": false, "file": file, "nudge": 0.0, "body": body}
	if n.get("kite", false):
		add_kite(q)
	return q


# (round 41, the user: "the guy with the kite should have his arm out and the string of the kite going to his arm…
# when Sandra talks to him, he looks at her and is not looking up") the kite flies on its own, high in front of where
# he stands (so it stays in the sky when he turns to talk), his right arm is held up (kite_pose.gd), and each frame the
# line runs from his hand to the kite; while they talk his head comes down to her.
const KITE_LOOK := -0.75         # his head tipped back, at the kite


func add_kite(q: Dictionary) -> void:
	var h: Node3D = q.holder
	var skel: Skeleton3D = q.m.root.find_children("*", "Skeleton3D", true, false)[0]
	var kp := SkeletonModifier3D.new()
	kp.set_script(load("res://engine/kite_pose.gd"))
	skel.add_child(kp)
	kp.model = q.m.root
	kp.arm = find_bone(skel, "RightArm")
	kp.fore = find_bone(skel, "RightForeArm")
	kp.hand = find_bone(skel, "RightHand")
	kp.amount = 1.0
	var kite := PrismMesh.new()
	kite.size = Vector3(1.0, 1.2, 0.02)
	var km := part(kite, Color(0.9, 0.25, 0.3), 0.6)
	main.outdoor.add_child(km)
	var at: Vector3 = h.global_position + Basis(Vector3.UP, float(q.yaw)) * Vector3(0, 7.5, 4.5)
	km.global_transform = Transform3D(Basis(Vector3.UP, float(q.yaw)) * Basis(Vector3.BACK, PI / 4).rotated(Vector3.RIGHT, -0.3), at)
	var line := CylinderMesh.new()
	line.top_radius = 0.007
	line.bottom_radius = 0.007
	line.height = 1.0
	line.radial_segments = 4
	var lm := part(line, Color(0.95, 0.95, 0.95), 0.5)
	main.outdoor.add_child(lm)
	# (the line ties on at the kite's lower point, the bridle)
	q.kite = {"pose": kp, "skel": skel, "hand": find_bone(skel, "RightHand"), "kite": km, "line": lm,
		"tie": at + Vector3(0, -0.55, 0)}
	kp.target = at + Vector3(0, -0.55, 0)


func place_kite(q: Dictionary) -> void:
	var k: Dictionary = q.kite
	var skel: Skeleton3D = k.skel
	var a: Vector3 = k.pose.hand_at
	if a == Vector3.ZERO:
		a = (skel.global_transform * skel.get_bone_global_pose(int(k.hand))).origin
	var b: Vector3 = k.tie
	var L := maxf(a.distance_to(b), 0.01)
	var y := (b - a) / L
	var x := y.cross(Vector3.UP).normalized() if absf(y.dot(Vector3.UP)) < 0.99 else Vector3.RIGHT
	var ln: MeshInstance3D = k.line
	# (stretched along its own length: Basis.scaled() stretches along the world's up, which only suits a level piece)
	ln.global_transform = Transform3D(Basis(x, y * L, x.cross(y)), (a + b) / 2.0)
	ln.visible = q.holder.visible
	k.kite.visible = q.holder.visible
	k.pose.low = move_toward(float(k.pose.low), 1.0 if q.talking else 0.0, get_process_delta_time() * 1.5)
	var pst = q.m.get("posture")
	if pst != null:
		pst.head_aim = move_toward(float(pst.head_aim), pst.HEAD_UP if q.talking else KITE_LOOK, get_process_delta_time() * 2.0)


# (round 41, the user: "the workman's hands are still going back… the workmen's shoulders are still a little too high")
# per model: [hand turned palm-in about the forearm, hand tipped forward, shoulder drop below the neck (share of
# height), arm out from the side, wrist forward of the hip joint (share of height)] (posture.gd hand_roll, hand_fwd,
# sh_drop, arm_out, wrist_fwd; radians)
const BODY_FIX := {"workman.glb": [0.0, 0.3, 0.03, 0.26, 0.0]}
# (round 41, the user: "the robber and the policeman both have their necks right back. Could you make their posture more
# correct?") the stouter man's head bone points further back than his face: brought up straight by it, he looked at the
# sky. Per model, radians forward
const HEAD_FIX := {"man2.glb": 0.35}


func stand_tall(mm: Dictionary, file := "") -> void:
	# (round 40, the user: "can you give the people better posture?") the head up over the neck and the back upright,
	# as Jaume's (round 38): the Meshy people all poke their heads forward (posture.gd)
	var pst = mm.get("posture")
	if pst == null:
		return
	var skel: Skeleton3D = pst.get_skeleton()
	if skel:
		pst.head = skel.find_bone(main.street_bone(skel, "Head"))
		if pst.neck < 0:
			pst.neck = skel.find_bone(main.street_bone(skel, "Neck"))
		pst.straight_head = true
		pst.head_fix = float(HEAD_FIX.get(file, 0.0))
		for a in OS.get_cmdline_user_args():          # (tests: --headfix= tries another on that model)
			if a.begins_with("--headfix=") and HEAD_FIX.has(file):
				pst.head_fix = float(a.substr(10))
		pst.head_only = true                       # (the head; and standing, the whole body, posture.gd stand_body)
		pst.arms = []                          # (round 41: the body stood as a person stands, posture.gd stand_body)
		for bn in ["LeftArm", "LeftForeArm", "LeftHand", "LeftHandMiddle1", "RightArm", "RightForeArm", "RightHand", "RightHandMiddle1"]:
			pst.arms.append(find_bone(skel, bn))
		pst.clav = [find_bone(skel, "LeftShoulder"), find_bone(skel, "RightShoulder")]
		var bf: Array = BODY_FIX.get(file, [0.0, 0.0, pst.SH_DROP, pst.ARM_OUT, pst.WRIST_FWD])
		for a in OS.get_cmdline_user_args():          # (tests: --bodyfix=roll,fwd,drop,out tries other values on that model)
			if a.begins_with("--bodyfix=") and BODY_FIX.has(file):
				bf = Array(a.substr(10).split(",")).map(func(x): return float(x))
		pst.hand_roll = bf[0]
		pst.hand_fwd = bf[1]
		pst.sh_drop = bf[2]
		pst.arm_out = bf[3]
		pst.wrist_fwd = bf[4]
		for a in OS.get_cmdline_user_args():          # (tests: --shdrop= on everyone else)
			if a.begins_with("--shdrop=") and not BODY_FIX.has(file):
				pst.sh_drop = float(a.substr(9))
		if pst.amount < 0.05:
			pst.amount = 0.2                       # (on, as standing: main.IDLE_TILT)


func redress(id: String) -> void:
	# (round 27) one person rebuilt where they stand, their look having changed (Tomàs putting his cap back on)
	var q: Dictionary = outdoor.get(id, {})
	if q.is_empty() or not q.has("holder"):
		return
	var pos: Vector3 = q.holder.position
	var parent: Node3D = q.holder.get_parent()
	q.holder.queue_free()
	var n: Dictionary = q.d
	outdoor[id] = make_person(id, n, parent, pos)


func enter_room(rid: String, offset: Vector3) -> void:
	leave_room()
	for id in data.NPCS:
		var n: Dictionary = data.NPCS[id]
		if n.at[0] != rid or not main.game.npc_visible(id):
			continue
		var p := offset + Vector3(float(n.at[1]) + 0.5, 0.0, float(n.at[2]) + 0.5)
		var nn := n
		if n.get("party_hat", false) and main.game.party_on():
			nn = n.duplicate(true)                                 # (round 23: the birthday girl's hat, during the party)
			nn.look.hat = "party"
			nn.look.hatc = "#e0457b"
		# (round 38, the user: "the party girl after the party has ended should be standing in the middle of the room
		# facing you") a host left alone after the gathering: her own spot, facing the front, no group to turn back to
		var alone: bool = n.has("after_at") and main.game.gathering_over()
		if alone:
			p = offset + Vector3(float(n.after_at[0]) + 0.5, 0.0, float(n.after_at[1]) + 0.5)
		indoor[id] = make_person(id, nn, main.indoor, p)
		if not indoor[id].is_empty():
			var yaw := 0.0                                         # facing the front of the room, towards the camera
			if n.has("face_to") and not alone:
				# (round 23: the party's guests talk in little groups, facing one another)
				var to := offset + Vector3(float(n.face_to[0]), 0.0, float(n.face_to[1])) - p
				yaw = atan2(to.x, to.z)
			indoor[id].holder.rotation.y = yaw
			indoor[id].yaw = yaw
			indoor[id].home_yaw = yaw
			if n.has("face_to") and not alone:
				indoor[id].group_yaw = yaw


func leave_room() -> void:
	for id in indoor:
		if not indoor[id].is_empty():
			indoor[id].holder.queue_free()
	indoor.clear()


func current() -> Dictionary:
	return indoor if main.where == "in" else outdoor


func candidates(p: Vector3) -> Array:
	var out := []
	var all := current()
	for id in all:
		var q: Dictionary = all[id]
		if q.is_empty() or q.get("gone", false):
			continue
		var at: Vector3 = q.holder.global_position - (main.room_base(main.room) if main.where == "in" else Vector3.ZERO)
		# ('reach': someone served across a gate, round 32: Jaume at Park Güell's)
		out.append({"x": at.x, "z": at.z, "r": float(q.d.get("reach", 1.7 if main.where == "out" else 2.2)), "label": "Talk to " + q.d.name, "act": "npc", "who": id})
	return out


func face(id: String, target: Vector3) -> void:
	var q: Dictionary = current().get(id, {})
	if q.is_empty():
		return
	var to: Vector3 = target - q.holder.global_position
	q.yaw = atan2(to.x, to.z)
	q.talking = true
	q.talk_t = 0.6                                           # (the talk box may open a frame or two later)
	q.target = q.holder.position                            # stay put: they don't walk off mid-sentence
	q.wait = 4.0


func tick(dt: float) -> void:
	var sandra: Vector3 = main.player.global_position
	var all := current()
	for id in all:
		var q: Dictionary = all[id]
		if q.is_empty():
			continue
		var h: Node3D = q.holder
		var far: bool = main.where == "out" and h.position.distance_squared_to(sandra) > 90.0 * 90.0
		if far != (q.get("far", false) as bool):
			# out of sight: stop drawing and animating them until Sandra comes back
			q.far = far
			# (round 39, the user: two gardeners "walk into each other" — Marc, who takes Pere's place only after the
			# Mossos take Pere, stood beside him as a ghost: coming back into sight showed whoever had left the story)
			h.visible = not far and not q.get("gone", false)
			if q.m.ap:
				if far:
					q.m.ap.pause()
				else:
					q.m.ap.play()
		if far and not String(q.get("mode", "")) in ["follow", "back"]:
			continue
		if q.get("gone", false):
			continue
		var r: float = float(q.d.get("r", 0)) * T * 0.6
		var go := false
		var spd := 0.0
		if String(q.get("mode", "")) != "" and main.where == "out":
			# a part in a scene (round 22: Agent Bofarull and Manolo): no pottering about
			spd = scene_move(q, dt, sandra)
			go = spd > 0.05
			r = 0.0
		if q.talking:
			# turned to Sandra and staying put until the talk box closes; then back to their day
			q.talk_t = float(q.get("talk_t", 0.0)) - dt
			if not main.dlg_open and q.talk_t <= 0.0:
				# (round 38, the user: "People should stay facing Sandra after she finishes talking to them… turn back to
				# people once Sandra walks away, but not while she's standing there")
				var ts := sandra - h.global_position
				ts.y = 0.0
				if ts.length() > 2.5:
					q.talking = false
					q.wait = rng.randf_range(1.0, 3.0)
					if q.has("group_yaw"):
						q.yaw = q.group_yaw                          # (back to their group)
					elif float(q.d.get("r", 0)) <= 0.0 and String(q.get("mode", "")) == "":
						q.yaw = float(q.get("home_yaw", q.yaw))      # (someone at a post: back to the way they stood)
				elif ts.length() > 0.2:
					q.yaw = atan2(ts.x, ts.z)
		if not q.talking and r > 0.0 and main.where == "out" and String(q.get("mode", "")) == "":
			q.wait -= dt
			if q.wait <= 0.0 and q.d.has("walk_loop"):
				# (round 40, rule 10 #16b: Pere along the top of the Austria Gardens and round its walks, "Just stays in
				# that general area") a beat: from point to point of a loop on the paths, a pause now and then
				var bt: Array = q.d.walk_loop
				var bi: int = int(q.get("beat_i", 0))
				var bp := Vector3(float(bt[bi][0]), 0.0, float(bt[bi][1]))
				if Vector2(bp.x - h.position.x, bp.z - h.position.z).length() < 0.3:
					bi = (bi + 1) % bt.size()
					q.beat_i = bi
					bp = Vector3(float(bt[bi][0]), 0.0, float(bt[bi][1]))
					q.wait = rng.randf_range(1.5, 5.0) if rng.randf() < 0.6 else 0.2
				else:
					q.wait = 0.4
				bp.y = main.ground_at(bp)
				q.target = bp
			elif q.wait <= 0.0:
				# a few steps somewhere near home
				var a := rng.randf() * TAU
				var t2: Vector3 = q.home + Vector3(cos(a), 0, sin(a)) * rng.randf_range(0.3, 1.0) * r
				if main.ground_at(t2) <= main.ground_at(q.home) + 0.2 and clear(h.position, t2) and main.person_fits(t2) \
						and not main.people.blocked_at(t2, 0.45) and not off_kerb(h.position, t2):
					q.target = t2
				q.wait = rng.randf_range(3.0, 8.0)
			var to: Vector3 = q.target - h.position
			to.y = 0
			if to.length() > 0.15:
				# don't walk into Sandra
				var ts := sandra - h.position
				ts.y = 0
				var nxt: Vector3 = h.position + to.normalized() * minf(WANDER_SPEED * dt, to.length())
				var tn := sandra - nxt
				tn.y = 0
				if not main.person_fits(nxt):
					q.target = h.position                # (round 40, rule 10 #16a: never a step into a wall — stop, try elsewhere)
					q.wait = minf(float(q.wait), 0.5)
				elif not (ts.length() < 1.2 and ts.normalized().dot(to.normalized()) > 0.3) and tn.length() > 0.75:
					go = true
					h.position = nxt
					q.yaw = atan2(to.x, to.z)
		# (round 37) pushed by her (main.gd shove_people): stepping back, facing her; once she has gone (2.5 m), someone
		# who stands at a post drifts back to it
		if float(q.get("shoved_t", 0.0)) > 0.0:
			q.shoved_t -= dt
			go = true
			spd = 1.0
			q.yaw = q.shove_face
			q.target = h.position
			if q.shoved_t <= 0.0 and q.has("after_face"):
				q.yaw = q.after_face                     # (round 38: pushed from behind, they turn to face her)
				q.erase("after_face")
				q.wait = maxf(float(q.get("wait", 0.0)), 1.5)
		elif q.has("shove") and r <= 0.0 and not q.talking and String(q.get("mode", "")) == "":
			var sv: Vector3 = q.shove
			if sv.length() > 0.02 and Vector2(sandra.x - h.position.x, sandra.z - h.position.z).length() > 2.5:
				var back := -sv.normalized() * minf(0.6 * dt, sv.length())
				if main.person_fits(h.position + back):
					h.position += back
					q.shove = sv + back
					go = true
					spd = 0.6
					q.yaw = atan2(back.x, back.z)
				else:
					q.shove = Vector3.ZERO                   # (round 40: back to the post only through open ground)
		# Sandra bumping into someone who wanders: they step aside, off her line
		if r > 0.0 and not q.talking and main.where == "out":
			var ts2 := sandra - h.position
			ts2.y = 0
			if ts2.length() < 0.7 and main.speed > 1.0:
				q.nudge += dt
				if q.nudge > 0.4:
					var side := Vector3(-ts2.z, 0, ts2.x).normalized() * 1.2
					q.target = h.position + side
					q.nudge = 0.0
			else:
				q.nudge = 0.0
		q.moving = move_toward(q.moving, 1.0 if go else 0.0, dt * 4.0)
		if q.m.get("posture") != null:
			q.m.posture.arms_w = 1.0 - q.moving             # (their arms forward standing, their own swing walking)
		if main.where == "out":
			h.position.y = main.ground_at(h.position)
		h.rotation.y = lerp_angle(h.rotation.y, q.yaw, 1.0 - exp(-6.0 * dt))
		var ap: AnimationPlayer = q.m.ap
		if ap:
			var want: String = "Walking" if q.moving > 0.4 and ap.has_animation("Walking") else q.m.anims.idle
			if want == "Walking" and spd > 3.0 and ap.has_animation("Running"):
				want = "Running"
			if want != "" and ap.current_animation != want:
				ap.play(want, 0.3)
			ap.speed_scale = clampf(spd / (4.2 if want == "Running" else 1.4), 0.8, 1.3) if spd > 0.05 else 1.0
		if q.has("cuffs"):
			place_cuffs(q)
		if q.has("kite"):
			place_kite(q)
		for mat in q.m.mats:
			mat.set_shader_parameter("ground_y", h.position.y)
		follow_cap(h, q.m)


# ------------------------------------------------------------------ scenes (round 22: catching the pickpocket)
# A person's `mode`: "follow" (keeps a few metres behind Sandra, along the way she walked, walking, or running
# when she's far ahead), "run_to" (runs to `goal`, then calls `on_arrive`), "hold" (stands, facing `look_at`).

const TAIL_GAP := 7.0            # following: how far back he keeps
const WALK := 1.7
const RUN := 4.2


func set_mode(id: String, mode: String, extra := {}) -> void:
	var q: Dictionary = outdoor.get(id, {})
	if q.is_empty():
		return
	q.mode = mode
	q.trail = []
	q.merge(extra, true)
	q.talking = false


func scene_move(q: Dictionary, dt: float, sandra: Vector3) -> float:
	var h: Node3D = q.holder
	var goal := h.position
	var spd := 0.0
	match String(q.mode):
		"follow":
			# (round 35, the user: "The policeman shouldn't follow her away from la rambla. If she leaves he should
			# walk back to his place … and wait until she speaks to him again") a few seconds off his beat and he
			# turns back; she can still talk to him on his way
			if q.d.get("beat", "") != "":
				q.off_t = 0.0 if main.street_name(sandra).contains(String(q.d.beat)) else float(q.get("off_t", 0.0)) + dt
				if float(q.off_t) > 3.0:
					q.mode = "back"
					q.trail = []
					return 0.0
				if float(q.off_t) > 0.0:
					return 0.0                         # (he stops where La Rambla ends, and watches her go)
			var tr: Array = q.trail
			if tr.is_empty() or tr[-1].distance_to(sandra) > 0.6:
				tr.append(sandra)
			while tr.size() > 400:
				tr.pop_front()
			var gap := Vector2(sandra.x - h.position.x, sandra.z - h.position.z).length()
			if gap > 45.0:
				# (she has got right away, on the bike say: he catches up out of sight, on the way she went)
				while tr.size() > 2 and Vector2(sandra.x - tr[0].x, sandra.z - tr[0].z).length() > 14.0:
					tr.pop_front()
				h.position = tr[0]
				gap = 14.0
			while tr.size() > 1 and Vector2(tr[0].x - h.position.x, tr[0].z - h.position.z).length() < 0.5:
				tr.pop_front()
			if gap > TAIL_GAP and not tr.is_empty():
				goal = tr[0] if not clear(h.position, sandra) else sandra
				spd = RUN if gap > TAIL_GAP * 1.6 else WALK * clampf((gap - TAIL_GAP) / 1.5 + 0.5, 0.5, 1.2)
			else:
				var ts := sandra - h.position
				q.yaw = lerp_angle(float(q.yaw), atan2(ts.x, ts.z), 1.0 - exp(-2.0 * dt))
		"run_to":
			goal = q.goal
			spd = RUN
			if Vector2(goal.x - h.position.x, goal.z - h.position.z).length() < 0.35:
				q.mode = "hold"
				spd = 0.0
				if q.has("on_arrive"):
					var f: Callable = q.on_arrive
					q.erase("on_arrive")
					f.call()
		"back":
			goal = q.home
			spd = WALK
			if Vector2(goal.x - h.position.x, goal.z - h.position.z).length() < 0.35:
				q.mode = "waiting"                     # (at his place: until she speaks to him again)
				q.yaw = PI
				spd = 0.0
		"hold":
			if q.has("look_at"):
				var tl: Vector3 = q.look_at - h.position
				q.yaw = atan2(tl.x, tl.z)
	var to := goal - h.position
	to.y = 0.0
	if spd > 0.0 and to.length() > 0.05:
		h.position += to.normalized() * minf(spd * dt, to.length())
		q.yaw = atan2(to.x, to.z)
		return spd
	return 0.0


func cuff(id: String, on: bool) -> void:
	# hands behind the back (cuff_pose.gd) and a pair of steel cuffs at the wrists
	var q: Dictionary = outdoor.get(id, {})
	if q.is_empty():
		return
	var skel: Skeleton3D = q.m.root.find_children("*", "Skeleton3D", true, false)[0]
	if on and not q.has("cuffs"):
		var cp := SkeletonModifier3D.new()
		cp.set_script(load("res://engine/cuff_pose.gd"))
		skel.add_child(cp)
		cp.model = q.m.root
		for bn in ["LeftArm", "LeftForeArm", "RightArm", "RightForeArm"]:
			cp.arms.append(find_bone(skel, bn))
		var steel := Color(0.72, 0.74, 0.78)
		var parts := []
		for k in 2:
			var ring := TorusMesh.new()
			ring.inner_radius = 0.032
			ring.outer_radius = 0.045
			var mi := part(ring, steel, 0.25)
			(mi.material_override as StandardMaterial3D).metallic = 0.9
			main.outdoor.add_child(mi)
			parts.append(mi)
		var chain := CylinderMesh.new()
		chain.top_radius = 0.006
		chain.bottom_radius = 0.006
		chain.height = 1.0
		var cm := part(chain, steel, 0.25)
		main.outdoor.add_child(cm)
		parts.append(cm)
		q.cuffs = {"pose": cp, "parts": parts, "skel": skel, "hands": [find_bone(skel, "LeftHand"), find_bone(skel, "RightHand")]}
	elif not on and q.has("cuffs"):
		q.cuffs.pose.queue_free()
		for mi in q.cuffs.parts:
			mi.queue_free()
		q.erase("cuffs")


func place_cuffs(q: Dictionary) -> void:
	var c: Dictionary = q.cuffs
	c.pose.amount = move_toward(float(c.pose.amount), 1.0, get_process_delta_time() * 2.5)
	var skel: Skeleton3D = c.skel
	var w := []
	for k in 2:
		var hb: int = c.hands[k]
		var t: Transform3D = skel.global_transform * skel.get_bone_global_pose(hb)
		w.append(t.origin)
		var mi: MeshInstance3D = c.parts[k]
		mi.global_transform = Transform3D(t.basis.orthonormalized(), t.origin)
		mi.visible = q.holder.visible
	var cm: MeshInstance3D = c.parts[2]
	var a: Vector3 = w[0]
	var b: Vector3 = w[1]
	var L := maxf(a.distance_to(b), 0.01)
	var y := (b - a) / L
	var x := y.cross(Vector3.UP).normalized() if absf(y.dot(Vector3.UP)) < 0.99 else Vector3.RIGHT
	cm.global_transform = Transform3D(Basis(x, y, x.cross(y)).scaled(Vector3(1, L, 1)), (a + b) / 2.0)
	cm.visible = q.holder.visible


func set_gone(id: String, gone: bool) -> void:
	# (someone who has left the scene: not drawn, not solid, not talked to)
	var q: Dictionary = outdoor.get(id, {})
	if q.is_empty():
		return
	q.gone = gone
	q.holder.visible = not gone
	for b in q.holder.find_children("*", "AnimatableBody3D", true, false):
		(b as AnimatableBody3D).collision_layer = 0 if gone else main.LAYER_BODY
	if gone:
		cuff(id, false)


func off_kerb(a: Vector3, b: Vector3) -> bool:
	# (round 41, the user: "this NPC is just standing in the street") pottering about near home, never a step down off a
	# kerb into the road: a drop of more than 8 cm between two points a quarter of a metre apart on the way
	var n := maxi(2, int(a.distance_to(b) / 0.25))
	var h0: float = main.ground_at(a)
	for k in range(1, n + 1):
		var h1: float = main.ground_at(a.lerp(b, float(k) / n))
		if h0 - h1 > 0.08:
			return true
		h0 = h1
	return false


func clear(a: Vector3, b: Vector3) -> bool:
	var q := PhysicsRayQueryParameters3D.create(a + Vector3(0, 0.5, 0), b + Vector3(0, 0.5, 0), main.LAYER_BODY)
	return main.get_world_3d().direct_space_state.intersect_ray(q).is_empty()


# ------------------------------------------------------------------ what they wear and carry

var shapes := {}                 # file -> the body's measurements (model space, before scaling)


func measure(file: String, mm: Dictionary) -> Dictionary:
	# from the mesh itself: how tall, where the head starts, its radius and front, the chest's front and width
	if shapes.has(file):
		return shapes[file]
	var mi: MeshInstance3D = null
	for c in mm.root.find_children("*", "MeshInstance3D", true, false):
		if c.skin != null:
			mi = c
	var v: PackedVector3Array = mi.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	var top := -INF
	for p in v:
		top = maxf(top, p.y)
	var head_from := top * 0.7
	var hx := 0.0
	var hz := -INF
	var cz := -INF
	var bz := INF
	var cw := 0.0
	for p in v:
		if p.y > head_from:
			hx = maxf(hx, absf(p.x))
			hz = maxf(hz, p.z)
		elif p.y > top * 0.42 and p.y < top * 0.62 and absf(p.x) < top * 0.2:
			cz = maxf(cz, p.z)
			bz = minf(bz, p.z)
			cw = maxf(cw, absf(p.x))
	shapes[file] = {"top": top, "head_r": hx, "head_front": hz, "head_mid": (top + head_from) / 2.0,
		"chest_front": cz, "chest_back": bz, "chest_w": cw, "xf": mi.transform}
	return shapes[file]


func part(mesh: Mesh, col: Color, rough := 0.7) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	var m := StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = rough
	mi.material_override = m
	return mi


func find_bone(skel: Skeleton3D, bone: String) -> int:
	# (the importer may write "mixamorig_Head" for "mixamorig:Head", and adds "_2" each time a model is made again:
	# "mixamorig_Head_2_2_2", which once left every hat hanging from the body while the head moved under it)
	var tail := RegEx.create_from_string("(_\\d+)+$")
	for i in skel.get_bone_count():
		var bn := tail.sub(skel.get_bone_name(i), "")
		if bn == bone or bn.ends_with(":" + bone) or bn.ends_with("_" + bone):
			return i
	return -1


func follow_cap(holder: Node3D, mm: Dictionary) -> void:
	# the hair tuck under a hat (character.gdshader) is a shape fixed in the model; the head moves with the
	# animation, so move the shape with it each frame (by how far the head is from where it was measured)
	var cap: Dictionary = mm.get("cap", {})
	if cap.is_empty() or not holder.visible:
		return
	var skel: Skeleton3D = cap.skel
	var d: Vector3 = skel.get_bone_global_pose(cap.idx).origin - skel.get_bone_global_rest(cap.idx).origin
	var dh: Vector3 = holder.global_transform.basis.inverse() * (skel.global_transform.basis * d)
	var c: Vector3 = (cap.c + dh) / cap.k
	for mat in mm.mats:
		mat.set_shader_parameter("cap_c", c)


func attach(holder: Node3D, mm: Dictionary, bone: String, parts: Array) -> void:
	# parts: [MeshInstance3D, Transform3D in the person's own space (y up, +z forward, feet at 0)]
	# They follow the bone (head, chest, hand) as it moves; with no bone they stay with the person.
	var target: Node3D = holder
	var to_local := Transform3D()
	if bone != "":
		var skel: Skeleton3D = mm.root.find_children("*", "Skeleton3D", true, false)[0]
		var idx := find_bone(skel, bone)
		if idx >= 0:
			var ba := BoneAttachment3D.new()
			ba.name = "Accessory"
			ba.set_meta("accessory", true)
			skel.add_child(ba)
			ba.bone_name = skel.get_bone_name(idx)
			target = ba
			# (from the bone's REST pose, the pose the head was measured in: from its pose at this moment, the
			# hat came out skewed by whatever the animation happened to be doing, a different way for each person)
			to_local = (skel.global_transform * skel.get_bone_global_rest(idx)).affine_inverse() * holder.global_transform
	for pr in parts:
		var mi: MeshInstance3D = pr[0]
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF if bone == "Head" else GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		target.add_child(mi)
		mi.transform = to_local * pr[1]


# (round 26) how far up a builder's helmet sits, in head radii from where other hats sit (`top`); --hhlift= to try
var HH_LIFT: float = (func():
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--hhlift="):
			return float(a.trim_prefix("--hhlift="))
	return 0.12).call()                              # (the user: still "weird" at 0.35: it hovered; now it sits on the head)


func accessories(holder: Node3D, mm: Dictionary, file: String, look: Dictionary, n: Dictionary) -> void:
	var sh := measure(file, mm)
	var k: float = mm.root.scale.y                       # the model's own scale (MODEL_SCALE, kids)
	var top: float = sh.top * k - sh.head_r * k * 0.6     # where a hat sits: down onto the hair, not on its tips
	var R: float = sh.head_r * k * 0.92                 # (the widest point takes in the ears and the hair)
	var hm: float = sh.head_mid * k
	var face: float = sh.head_front * k
	var chest: float = sh.chest_front * k
	var back: float = sh.chest_back * k
	var cw: float = sh.chest_w * k
	var hatc := Color(look.get("hatc", "#3a3a40"))
	var hat: String = look.get("hat", "")
	if hat == "hardhat" and file == "workman.glb":
		hat = ""                                   # (round 37: his own modelled helmet; the drawn one is gone)
	var head := []
	if hat != "":
		var dome := SphereMesh.new()
		dome.radius = R * 1.04
		dome.height = R * 1.1
		dome.is_hemisphere = true
		match hat:
			"cap", "flatcap":
				head.append([part(dome, hatc), Transform3D(Basis().scaled(Vector3(1, 0.75 if hat == "cap" else 0.45, 1)), Vector3(0, top - R * 0.42, 0))])
				var brim := BoxMesh.new()
				brim.size = Vector3(R * 1.2, 0.025, R * 0.6)
				head.append([part(brim, hatc.darkened(0.15)), Transform3D(Basis(Vector3.RIGHT, -0.15), Vector3(0, top - R * 0.4, R * 0.95))])
			"police", "guard":
				# (round 41, the user: "The policeman's hat is comically large and covers his face. Could you make it
				# smaller and just sit on his head?") a smaller cap set on the crown, its visor over the brow, not the eyes
				var cyl := CylinderMesh.new()
				cyl.top_radius = R * 0.8
				cyl.bottom_radius = R * 0.72
				cyl.height = R * 0.42
				head.append([part(cyl, hatc), Transform3D(Basis(), Vector3(0, top + R * 0.36, 0))])
				var visor := BoxMesh.new()
				visor.size = Vector3(R * 0.85, 0.02, R * 0.36)
				head.append([part(visor, Color(0.08, 0.08, 0.1), 0.3), Transform3D(Basis(Vector3.RIGHT, -0.2), Vector3(0, top + R * 0.17, R * 0.78))])
				var badge := SphereMesh.new()
				badge.radius = R * 0.1
				badge.height = R * 0.1
				head.append([part(badge, Color(0.85, 0.68, 0.25), 0.3), Transform3D(Basis(), Vector3(0, top + R * 0.4, R * 0.78))])
			"hardhat":
				# (round 26, the user: "Redo the workmen hats, all of them across the game. They look like plastic bowls.
				# They should be proper helmets where you can see their faces") a builder's helmet: a domed shell sitting
				# on the crown of the head, a raised ridge from front to back, a short peak over the eyes, a narrow rim
				# round the sides and back, a dark band inside it
				var hb := top + R * HH_LIFT                       # its rim
				var shell := SphereMesh.new()
				shell.radius = R * 1.06
				shell.height = R * 1.06
				shell.is_hemisphere = true
				shell.radial_segments = 24
				# (the crown a quarter taller than a bowl, the rim narrow, the peak out over the brow: a helmet's profile,
				# not a saucer's, from the side)
				head.append([part(shell, hatc, 0.35), Transform3D(Basis().scaled(Vector3(1.0, 1.28, 1.08)), Vector3(0, hb, 0))])
				var ridge := BoxMesh.new()
				ridge.size = Vector3(R * 0.2, R * 0.12, R * 1.6)
				head.append([part(ridge, hatc.lightened(0.08), 0.35), Transform3D(Basis(), Vector3(0, hb + R * 1.2, -R * 0.05))])
				var rim := CylinderMesh.new()
				rim.top_radius = R * 1.1
				rim.bottom_radius = R * 1.14
				rim.height = R * 0.05
				rim.radial_segments = 24
				head.append([part(rim, hatc, 0.35), Transform3D(Basis().scaled(Vector3(1.0, 1.0, 1.08)), Vector3(0, hb + R * 0.02, 0))])
				var peak := BoxMesh.new()
				peak.size = Vector3(R * 1.1, R * 0.05, R * 0.6)
				head.append([part(peak, hatc, 0.35), Transform3D(Basis(Vector3.RIGHT, 0.22), Vector3(0, hb + R * 0.02, R * 1.2))])
				var band := CylinderMesh.new()
				band.top_radius = R * 0.97
				band.bottom_radius = R * 0.97
				band.height = R * 0.1
				head.append([part(band, Color(0.15, 0.14, 0.13), 0.8), Transform3D(Basis().scaled(Vector3(1.0, 1.0, 1.08)), Vector3(0, hb + R * 0.03, 0))])
			"barretina":                                             # the Catalan cap: a soft red bag flopping back
				var bag := CylinderMesh.new()
				var r2 := R * 0.78                                   # (her hair makes the head look wider than it is)
				bag.top_radius = r2 * 0.25
				bag.bottom_radius = r2 * 0.9
				bag.height = r2 * 1.3
				head.append([part(bag, hatc, 0.9), Transform3D(Basis(Vector3.RIGHT, -1.0), Vector3(0, top + r2 * 0.75, -r2 * 0.35))])
				var band := CylinderMesh.new()
				band.top_radius = r2 * 0.97
				band.bottom_radius = r2 * 0.97
				band.height = r2 * 0.16
				head.append([part(band, Color(0.12, 0.1, 0.1), 0.8), Transform3D(Basis(), Vector3(0, top + r2 * 0.35, 0))])
			"party":                                                 # (round 23) the birthday girl's paper cone, worn on top
				var cone := CylinderMesh.new()
				cone.top_radius = 0.0
				cone.bottom_radius = R * 0.42
				cone.height = R * 1.15
				cone.radial_segments = 16
				var tilt := Basis(Vector3.FORWARD, 0.22) * Basis(Vector3.RIGHT, -0.12)
				head.append([part(cone, hatc, 0.7), Transform3D(tilt, Vector3(-R * 0.12, top + R * 0.62, -R * 0.05))])
				var pom := SphereMesh.new()
				pom.radius = R * 0.12
				pom.height = R * 0.24
				head.append([part(pom, Color("#f6e27a"), 0.8), Transform3D(Basis(), Vector3(-R * 0.12, top + R * 0.62, -R * 0.05) + tilt * Vector3(0, R * 0.6, 0))])
				for j in 3:                                          # gold stripes round it
					var ring := CylinderMesh.new()
					var f := 0.22 + j * 0.25
					ring.top_radius = R * 0.42 * (1.0 - f) + 0.004
					ring.bottom_radius = R * 0.42 * (1.0 - f) + 0.004
					ring.height = R * 0.06
					ring.radial_segments = 16
					head.append([part(ring, Color("#f6e27a"), 0.6), Transform3D(tilt, Vector3(-R * 0.12, top + R * 0.62, -R * 0.05) + tilt * Vector3(0, -R * 0.575 + f * R * 1.15, 0))])
			_:                                                       # straw hats and sun hats: a crown and a wide brim
				head.append([part(dome, hatc, 0.9), Transform3D(Basis().scaled(Vector3(1, 0.7, 1)), Vector3(0, top - R * 0.4, 0))])
				var brim2 := CylinderMesh.new()
				brim2.top_radius = R * 1.75
				brim2.bottom_radius = R * 1.8
				brim2.height = 0.025
				head.append([part(brim2, hatc, 0.9), Transform3D(Basis(), Vector3(0, top - R * 0.4, 0))])
	if hat != "" and hat != "party":
		# tuck the hair in under the hat (character.gdshader): where its rim sits and how far it reaches,
		# in the model's own units
		var base := top - R * 0.4
		var rr := R * 1.0
		var ry := R * 0.55 * 0.7                       # (a hemisphere R × 1.1 "tall" is 0.55 R high, then squashed)
		match hat:
			"cap":
				base = top - R * 0.42
				ry = R * 0.55 * 0.75
			"flatcap":
				base = top - R * 0.42
				ry = R * 0.55 * 0.45
			"hardhat":
				base = top + R * HH_LIFT
				rr = R * 1.08
				ry = R * 1.1
			"police", "guard":
				base = top + R * 0.15
				rr = R * 0.75
				ry = R * 0.42
			"barretina":
				base = top + R * 0.78 * 0.27
				rr = R * 0.78 * 0.95
				ry = R * 0.78
		for mat in mm.mats:
			mat.set_shader_parameter("cap_on", true)
			mat.set_shader_parameter("cap_c", Vector3(0.0, base, 0.0) / k)
			mat.set_shader_parameter("cap_r", Vector3(rr, ry, rr) / k)
		var skel: Skeleton3D = mm.root.find_children("*", "Skeleton3D", true, false)[0]
		var hi := find_bone(skel, "Head")
		mm.cap = {} if hi < 0 else {"skel": skel, "idx": hi, "c": Vector3(0.0, base, 0.0), "k": k}
	if look.get("glasses", false) and file in ["man.glb", "man2.glb", "woman.glb", "sandra_a.glb", "sandra_b.glb", "passerby.glb"]:
		# (round 41, the user: "The redhead girl's glasses are sitting too high") the middle of the head takes in the
		# hair piled on top, so they sat on the brow; where the face is measured (FACE: chin to fringe), on the eyes
		var f: Array = FACE.get(file, [])
		var eye: float = hm - R * 0.05 if f.is_empty() else lerpf(f[0], f[1], 0.5) * k
		for sx in [-1.0, 1.0]:
			var ring := TorusMesh.new()
			ring.inner_radius = R * 0.15
			ring.outer_radius = R * 0.2
			head.append([part(ring, Color(0.15, 0.1, 0.08), 0.4), Transform3D(Basis(Vector3.RIGHT, PI / 2), Vector3(sx * R * 0.33, eye, face - R * 0.02))])
	if not head.is_empty():
		attach(holder, mm, "Head", head)
	var body := []
	var tall: float = sh.top * k
	if look.has("apron"):
		# painted onto the front of their own clothes, so it follows the body (character.gdshader)
		for mat in mm.mats:
			mat.set_shader_parameter("apron_on", true)
			mat.set_shader_parameter("apron_col", Color(look.apron))
			mat.set_shader_parameter("apron_zone", Vector2(tall * 0.2, tall * 0.6))
			mat.set_shader_parameter("apron_w", sh.chest_w * 0.95)
	if look.get("lanyard", false):
		var card := BoxMesh.new()
		card.size = Vector3(0.09 * k, 0.12 * k, 0.01)
		body.append([part(card, Color(0.95, 0.95, 0.92), 0.5), Transform3D(Basis(), Vector3(0, tall * 0.5, chest + 0.03))])
		var cord := BoxMesh.new()
		cord.size = Vector3(0.012, tall * 0.12, 0.012)
		for sx in [-1.0, 1.0]:
			body.append([part(cord, Color(0.75, 0.15, 0.15)), Transform3D(Basis(Vector3.BACK, sx * 0.35), Vector3(sx * cw * 0.3, tall * 0.57, chest + 0.02))])
	if look.get("guitar", false):
		var gb := CylinderMesh.new()
		gb.top_radius = tall * 0.13
		gb.bottom_radius = tall * 0.15
		gb.height = 0.08
		body.append([part(gb, Color(0.62, 0.38, 0.18), 0.5), Transform3D(Basis(Vector3.RIGHT, PI / 2).rotated(Vector3.BACK, 0.5), Vector3(-cw * 0.2, tall * 0.45, back - 0.06))])
		var neck := BoxMesh.new()
		neck.size = Vector3(0.05, tall * 0.4, 0.03)
		body.append([part(neck, Color(0.3, 0.18, 0.1), 0.5), Transform3D(Basis(Vector3.BACK, 0.5), Vector3(cw * 0.35, tall * 0.66, back - 0.06))])
	if not body.is_empty():
		attach(holder, mm, "Spine2", body)
	var loose := []                                          # things that go with them but aren't worn
	# (round 39, the user: "there's a floating object next to her. Remove it.") the handbag ('bag') and the basket
	# ('basket') hung in the air beside them, held by no hand: no longer drawn
	# (round 41, the user: "There is an old lady with a red bag floating with her. Remove it and remove any others") her
	# shopping trolley ('trolley') likewise: no longer drawn; nothing carried is drawn unless a hand holds it
	var rod_marks := {}
	if look.get("rod", false):
		# (round 41, the user: "the man with the fishing rod doesn't look like he's holding it. His arm needs to be doing
		# something. Both of them sort of out in front of him, but low around his waist. So his hands are holding it.
		# Maybe one hand is lower than the other one… the rod should be over the water, so the line goes into the
		# water") held in both hands at his waist, the right low on the butt, the left a forearm further up the rod,
		# which leans out 63° from upright; the line straight down from its tip, the float on the water. His arms reach
		# for his hands' places (rider_pose.gd, as she sits on the wheel), his feet stay where they stand.
		var rdir := Vector3(0.0, cos(1.1), sin(1.1))
		var rl := 3.0
		var hand_r := Vector3(-0.06, tall * 0.5, 0.26)
		var hand_l := hand_r + rdir * 0.42 + Vector3(0.1, 0.0, 0.0)
		var butt := hand_r - rdir * 0.14
		var rod := CylinderMesh.new()
		rod.top_radius = 0.008
		rod.bottom_radius = 0.02
		rod.height = rl
		loose.append([part(rod, Color(0.25, 0.2, 0.15), 0.5), Transform3D(Basis(Vector3.RIGHT, 1.1), butt + rdir * rl / 2.0)])
		# (round 27, from the 2D game) the line down from the rod's tip, and the little red float at its end
		var tip := butt + rdir * rl
		var fline := BoxMesh.new()
		fline.size = Vector3(0.005, tip.y, 0.005)
		loose.append([part(fline, Color(0.92, 0.92, 0.92), 0.4), Transform3D(Basis(), Vector3(tip.x, tip.y / 2.0, tip.z))])
		var flo := SphereMesh.new()
		flo.radius = 0.05
		flo.height = 0.12
		loose.append([part(flo, Color(0.85, 0.2, 0.15), 0.6), Transform3D(Basis(), Vector3(tip.x, 0.02, tip.z))])
		rod_marks = {"hand_r": hand_r, "hand_l": hand_l, "elbow_r": Vector3(-0.32, tall * 0.42, -0.2), "elbow_l": Vector3(0.34, tall * 0.48, -0.1),
			"foot_l": Vector3(0.11, tall * 0.045, 0.03), "foot_r": Vector3(-0.11, tall * 0.045, -0.03),
			"knee_l": Vector3(0.13, tall * 0.3, 1.0), "knee_r": Vector3(-0.13, tall * 0.3, 1.0)}
	if not loose.is_empty():
		attach(holder, mm, "", loose)
	if not rod_marks.is_empty():
		var rsk: Skeleton3D = mm.root.find_children("*", "Skeleton3D", true, false)[0]
		var tg := {}
		for k2 in rod_marks:
			var mk := Node3D.new()
			holder.add_child(mk)
			mk.position = rod_marks[k2]
			tg[k2] = mk
		var hp := SkeletonModifier3D.new()
		hp.set_script(load("res://engine/rider_pose.gd"))
		rsk.add_child(hp)
		var rb := {}
		for pair in [["hips", "Hips"], ["spine", "Spine"], ["spine1", "Spine1"], ["spine2", "Spine2"], ["neck", "Neck"], ["head", "Head"],
				["upleg_l", "LeftUpLeg"], ["leg_l", "LeftLeg"], ["foot_l", "LeftFoot"], ["upleg_r", "RightUpLeg"], ["leg_r", "RightLeg"], ["foot_r", "RightFoot"],
				["shoulder_l", "LeftShoulder"], ["shoulder_r", "RightShoulder"], ["arm_l", "LeftArm"], ["fore_l", "LeftForeArm"], ["hand_l", "LeftHand"], ["arm_r", "RightArm"], ["fore_r", "RightForeArm"], ["hand_r", "RightHand"]]:
			rb[pair[0]] = find_bone(rsk, pair[1])
		hp.setup(mm.root, rb, tg)
		hp.lean = 0.1
		hp.head_down = 0.25                  # (watching his float)
		hp.crank = 0.0
		hp.active = true
