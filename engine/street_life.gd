# Things in the street that move with Sandra, kept apart from main.gd:
#   Trufa, Montse's dog: lost in the forest until the dog mission (game.gd) finds her. Then she
#   follows Sandra, sits when told to stay, and goes home to Montse on the Rambla when sent back.
#   Bicycles: each one its own colours and extras; Sandra can ride any of them.
# Where the bicycles stand comes from scene.json ("street_life"), written by build_assets.py.
extends Node

const Dog = preload("res://engine/dog.gd")

const BIKE_SPEED := 9.0
const BIKE_ACCEL := 7.0          # pedalling up to speed, m/s²
const BIKE_COAST := 2.5          # slowing down when she stops pedalling
const BIKE_BRAKE := 11.0
const BIKE_BACK := 1.2           # pushing the bike backwards, m/s
const BIKE_SPIN := 2.0           # rad/s: stopped, the side keys turn the bike round on the spot
const HIPS_ABOVE_SEAT := 0.05    # her hip joint above the top of the saddle (she sinks into it a little)
const BIKE_MIN_RADIUS := 0.8     # the turn's radius (metres) at a standstill...
const BIKE_RADIUS_GROW := 0.5    # ...plus this much per m/s: about 3 m across creeping, 11 m at full speed
const BIKE_ROUGH := 0.7          # top speed on pavements, paths and grass, as a share of the road's (round 27,
                                 # the user: "slightly faster on footpaths and gravel trails")

var main: Node3D
var trufa: Node3D
var bikes: Array = []
var riding: Node3D = null
var own_bike: Node3D = null      # the old roadster Jordi gives her (the bike mission); the others are locked up
var ik_skin := -1
var poles: Array = []
var rider: SkeletonModifier3D        # her riding pose (rider_pose.gd)
var rider_lean := 0.06
var rider_foot := 0.0            # 0..1: stopped, her left foot goes down to the ground
var bike_glb: GLTFState
var bike_doc: GLTFDocument

func setup(m: Node3D) -> void:
	main = m
	var L: Dictionary = main.D.get("street_life", {})
	# Trufa: lost in the forest, as in the 2D game; home is at Montse's feet on the Rambla (npcs.gd)
	var dog_file: String = main.asset_path("meshy/trufa.glb")
	if FileAccess.file_exists(dog_file):
		var tl: Array = main.game.data.TRUFA.at
		var lost: Vector3 = main.npcs.world_pos(tl[1], tl[2])
		trufa = Node3D.new()
		trufa.set_script(load("res://engine/dog.gd"))
		main.outdoor.add_child(trufa)
		trufa.setup(main, main.load_glb("meshy/trufa.glb"), lost, 0.6, 0.36)
		var ma: Array = main.game.data.NPCS.montse.at
		var home: Vector3 = main.npcs.world_pos(ma[1], ma[2]) + Vector3(-0.7, 0, 0.6)
		trufa.home_pos = Vector3(home.x, main.ground_at(home), home.z)
		trufa.home_yaw = PI
		match main.game.S.trufa:
			"home": trufa.settle_home()
			"following":
				trufa.position = main.player.global_position + Vector3(1, 0, 1)
				trufa.follow()
	# bicycles
	bike_doc = GLTFDocument.new()
	bike_glb = GLTFState.new()
	if bike_doc.append_from_file(main.asset_path("props/bicycle.glb"), bike_glb) == OK:
		for v in L.get("bikes", [{"pos": [12.4, 31.5], "yaw": 1.45, "frame": "#2f6b5a"}]):
			add_bike(v)


func add_bike(v: Dictionary, solid := true) -> void:
	var bk := Node3D.new()
	bk.set_script(load("res://engine/bike.gd"))
	main.outdoor.add_child(bk)
	var variant := {"basket": v.get("basket", true), "flowers": v.get("flowers", true), "rack": v.get("rack", true),
		"dog_basket": v.get("dog_basket", false)}
	for key in ["frame", "guard", "saddle", "wicker"]:
		if v.has(key):
			variant[key] = Color(v[key])
	bk.setup(bike_doc.generate_scene(bike_glb) as Node3D, variant)
	bk.position = Vector3(v.pos[0], main.ground_at(Vector3(v.pos[0], 0, v.pos[1])), v.pos[1])
	bk.rotation.y = v.yaw
	settle(bk)
	bk.parked_yaw = v.yaw
	bikes.append(bk)
	if solid:
		# (round 33, the user: "She can run through the bike lock stands/bikes") somebody else's bike, locked where it
		# stands: a box the size of it, on foot or on her own bike (her own bike, ridden away, has none)
		var body := StaticBody3D.new()
		body.collision_layer = main.LAYER_BODY
		body.collision_mask = 0
		var cs := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(0.32, 1.1, 1.75)
		cs.shape = box
		cs.position.y = 0.55
		body.add_child(cs)
		bk.add_child(body)


# ------------------------------------------------------------------ what Sandra can do here

func candidates(p: Vector3) -> Array:
	var out := []
	if riding:
		return out
	if trufa and trufa.in_basket == 0.0:
		var tp := trufa.global_position
		var known: bool = main.game.m_active("dog") or main.game.m_done("dog")     # (Montse has told her the dog's name)
		var label := ("Call Trufa" if known else "Look at the dog") if trufa.state == Dog.LOST else "Talk to Trufa"
		# (round 41c, 10 #26b, the user: "If there are two options and one of them is Trufa should be the secondary one…
		# only when Trufa is following me. When Trufa's just staying where they are, Trufa is the first thing to talk to")
		var prio := -3.0 if trufa.state == Dog.FOLLOW else 1.0
		out.append({"x": tp.x, "z": tp.z, "r": 1.5, "label": label, "act": "trufa", "prio": prio})
	for bk in bikes:
		if bk == own_bike:
			out.append({"x": bk.position.x, "z": bk.position.z, "r": 1.3, "label": "Ride your bike", "act": "bike", "bike": bk})
		else:
			# (round 35, the everything-visit: 1.1 m, and a bike in a rack between hoops and its neighbour is 1.2 m from
			# anywhere she fits, so it was never offered)
			out.append({"x": bk.position.x, "z": bk.position.z, "r": 1.5, "label": "Look at the bike", "act": "bike_locked", "bike": bk})
	return out


func act(n: Dictionary) -> void:
	match n.act:
		"trufa": main.game.talk_trufa()
		"bike": mount(n.bike)
		"bike_locked":
			# (round 23, the user: no Jordi, no "B to hop on": it isn't hers to ride)
			main.show_dialog("", ["Somebody's bike, locked to the stand with a heavy chain."])


func own_bike_here() -> void:
	# her bike, under her wherever she is (as in the 2D game, where B simply puts her on it)
	if own_bike == null:
		add_bike({"pos": [0, 0], "yaw": 0.0, "frame": "#2f5a3e", "guard": "#e8dcc0", "saddle": "#5a3b28", "wicker": "#b08850",
			"basket": true, "flowers": false, "rack": true, "dog_basket": true}, false)
		own_bike = bikes.back()
	var p: Vector3 = main.player.global_position
	own_bike.visible = true
	own_bike.position = Vector3(p.x, main.ground_at(p), p.z)
	own_bike.rotation = Vector3(0, main.model.rotation.y + PI, 0)          # (a bike's nose is its -z)
	own_bike.parked_yaw = own_bike.rotation.y
	mount(own_bike)


func trufa_follow() -> void:
	if trufa:
		trufa.follow()


func trufa_home() -> void:
	# the dog mission is done: she goes back to Montse's feet
	if trufa:
		trufa.state = Dog.HOME
		trufa.been.clear()


func talk_trufa() -> void:
	# (round 23, the user: "the dog options should only trigger once the mission is complete": until then she just
	# goes everywhere with Sandra)
	if not main.game.m_done("dog"):
		if trufa.state != Dog.FOLLOW:
			trufa.follow()
		main.show_dialog("", ["(Trufa wags her whole back end and presses against your legs. She isn't letting you out of her sight.)"])
		return
	match trufa.state:
		Dog.FOLLOW:
			main.show_dialog("", ["(Trufa looks up at you, tongue out, ready for anything.)"],
				["Stay, Trufa.", "Go home to Montse.", "Good girl! (keep walking)"], trufa_following_choice)
		Dog.STAY, Dog.WAIT:
			main.show_dialog("", ["(Trufa is sitting exactly where you left her, very proud of herself.)"],
				["Come on, Trufa!", "Go home to Montse.", "(Leave her sitting)"], trufa_staying_choice)
		_:
			main.show_dialog("", ["(Trufa thumps her tail on the pavement.)"],
				["Come for a walk, Trufa!", "(Give her a scratch behind the ears)"], trufa_home_choice)


func trufa_following_choice(i: int) -> void:
	if i == 0:
		trufa.stay()
	elif i == 1:
		send_home()


func trufa_staying_choice(i: int) -> void:
	if i == 0:
		trufa.follow()
	elif i == 1:
		send_home()


func trufa_home_choice(i: int) -> void:
	if i == 0:
		trufa.follow()
	else:
		main.show_dialog("", ["(She leans her whole weight into your hand and sighs.)"])


func send_home() -> void:
	if main.game.m_done("dog"):
		trufa.go_home()
	else:
		trufa.stay()
		main.show_dialog("", ["(Trufa sits down and looks at you. She doesn't know the way home from here. Better walk her back to Montse yourself.)"])


func on_take_home(at: Vector3) -> void:
	# (round 41c, 10 #26c, the user: "Take me home: She should go back to her owner") H: a dog out with Sandra is back
	# at her owner's feet; before her mission is done she comes home with Sandra instead, so it isn't skipped
	if not trufa or not trufa.state in [Dog.FOLLOW, Dog.STAY, Dog.WAIT, Dog.GOING_HOME]:
		return
	if trufa.get_parent() != main.outdoor:              # (riding in the basket: back on the ground first)
		trufa.get_parent().remove_child(trufa)
		main.outdoor.add_child(trufa)
		trufa.rotation = Vector3.ZERO
	trufa.in_basket = 0.0
	trufa.basket_in = false
	if main.game.m_done("dog"):
		trufa.settle_home()
		trufa.heading = trufa.home_yaw
	else:
		var p := at + Vector3(0.9, 0.0, 0.4)
		p.y = main.ground_at(p)
		trufa.position = p
		trufa.trail.clear()
		trufa.follow()


func on_enter() -> void:
	# Sandra goes indoors: a following Trufa waits outside the door (round 23; dog.gd WAIT)
	if trufa and trufa.state == Dog.FOLLOW:
		trufa.wait_outside()
	if riding:
		dismount()


# ------------------------------------------------------------------ riding

func mount(bk: Node3D) -> void:
	riding = bk
	var skin_root: Node3D = main.skins[main.skin_idx].root if not main.skins.is_empty() else null
	# Sandra takes the bike as it stands: she turns to face where it points (its nose is its -z)
	var nose: Vector3 = -bk.global_transform.basis.z
	var yaw := atan2(nose.x, nose.z)
	main.face_target = INF
	main.model.rotation.y = yaw
	main.move_dir = Vector2(sin(yaw), cos(yaw))
	bk.get_parent().remove_child(bk)
	main.model.add_child(bk)
	bk.transform = Transform3D(Basis(Vector3.UP, PI), Vector3.ZERO)      # the bike faces -z, Sandra faces +z
	bk.ridden = true
	main.player.global_position = Vector3(bk.global_position.x, main.player.global_position.y, bk.global_position.z)
	if skin_root:
		# sit her on the saddle: her hips just above it
		skin_root.position = Vector3.ZERO
		var skel: Skeleton3D = skin_root.find_children("*", "Skeleton3D", true, false)[0]
		var hips := skel.find_bone(bone(skel, "mixamorig:Hips"))
		var hips_at: Vector3 = main.model.to_local(skel.global_transform * skel.get_bone_global_rest(hips).origin)
		var seat_local: Vector3 = main.model.to_local(bk.seat.global_position)
		skin_root.position = seat_local + Vector3(0, HIPS_ABOVE_SEAT, -0.06) - hips_at   # (+z is forwards)
		setup_rider(skin_root, bk)
	main.speed = 0.0
	main.bike_steer = 0.0
	main.add_bike_body(bk)
	main.show_banner("On the bike: W pedal · S brake · A D lean · E get off")


func dismount() -> void:
	if not riding:
		return
	var bk := riding
	riding = null
	var g := bk.global_transform
	main.model.remove_child(bk)
	main.outdoor.add_child(bk)
	bk.global_transform = g
	bk.rotation = Vector3(0, bk.rotation.y, 0)
	settle(bk)
	bk.park()
	# Sandra steps off on the kerb side if there's room, else the other side; she keeps facing the way she rode
	var yaw: float = main.model.rotation.y
	var left := Vector3(cos(yaw), 0, -sin(yaw))
	var from: Vector3 = main.player.global_position
	var step := left * 0.7
	for s in [left * 0.7, -left * 0.7]:
		var q := PhysicsRayQueryParameters3D.create(from + Vector3(0, 0.5, 0), from + s * 1.6 + Vector3(0, 0.5, 0), main.LAYER_BODY)
		q.exclude = [main.player.get_rid()]
		if main.get_world_3d().direct_space_state.intersect_ray(q).is_empty():
			step = s
			break
	main.player.global_position = from + step
	main.cam_slide = -step                     # (the camera glides across to her: main.update_camera())
	main.face_target = INF
	main.move_dir = Vector2(sin(yaw), cos(yaw))
	for sk in main.skins:
		sk.root.position = Vector3.ZERO
	if rider:
		rider.active = false
	main.speed = 0.0
	main.bike_steer = 0.0
	main.remove_bike_body()


func setup_rider(skin_root: Node3D, bk: Node3D) -> void:
	# her riding pose (rider_pose.gd): seated, feet on the pedals, hands on the grips
	var skel: Skeleton3D = skin_root.find_children("*", "Skeleton3D", true, false)[0]
	for p in poles:
		p.queue_free()
	poles.clear()
	# which way knees and elbows point: knees forward and up, a little out; elbows out, back and down
	# (in the bike's own space, where forward is -z, so they turn with it)
	var targets := {"foot_l": bk.foot_l, "foot_r": bk.foot_r, "hand_l": bk.hand_l, "hand_r": bk.hand_r}
	for pv in [["knee_l", Vector3(-0.15, 0.6, -0.7)], ["knee_r", Vector3(0.15, 0.6, -0.7)],
			["elbow_l", Vector3(-0.5, -0.2, 0.4)], ["elbow_r", Vector3(0.5, -0.2, 0.4)]]:
		var pole := Node3D.new()
		bk.add_child(pole)
		pole.position = pv[1]
		poles.append(pole)
		targets[pv[0]] = pole
	if rider == null or rider.get_parent() != skel:
		if rider:
			rider.queue_free()
		rider = SkeletonModifier3D.new()
		rider.set_script(load("res://engine/rider_pose.gd"))
		skel.add_child(rider)
	var bones := {}
	for pair in [["hips", "Hips"], ["spine", "Spine"], ["spine1", "Spine1"], ["spine2", "Spine2"], ["neck", "Neck"], ["head", "Head"],
			["upleg_l", "LeftUpLeg"], ["leg_l", "LeftLeg"], ["foot_l", "LeftFoot"], ["upleg_r", "RightUpLeg"], ["leg_r", "RightLeg"], ["foot_r", "RightFoot"],
			["shoulder_l", "LeftShoulder"], ["shoulder_r", "RightShoulder"], ["arm_l", "LeftArm"], ["fore_l", "LeftForeArm"], ["hand_l", "LeftHand"], ["arm_r", "RightArm"], ["fore_r", "RightForeArm"], ["hand_r", "RightHand"]]:
		bones[pair[0]] = skel.find_bone(bone(skel, "mixamorig:" + pair[1]))
	rider.setup(main.model, bones, targets)
	rider.active = true
	rider_lean = 0.06
	rider_foot = 1.0


func bone(skel: Skeleton3D, want: String) -> String:
	# the importer may rename "mixamorig:LeftLeg" to "mixamorig_LeftLeg"
	var tail := want.get_slice(":", 1)
	for i in skel.get_bone_count():
		var n := skel.get_bone_name(i)
		if n == want or n.ends_with("_" + tail) or n.ends_with(":" + tail) or n == tail:
			return n
	# (round 41c, the user: on a bench in her other outfit "her body is distorted": a cached model instanced again gains
	# "_2" per copy, "mixamorig_Hips_2", so no bone was found and the sitting pose bent her anyhow) the copies' suffixes
	# stripped, as main.gd street_bone does
	for i in skel.get_bone_count():
		var n := skel.get_bone_name(i)
		var base := n
		while base.ends_with("_2"):
			base = base.left(-2)
		if base != n and (base == want or base.ends_with("_" + tail) or base.ends_with(":" + tail) or base == tail):
			return n
	return want


func tick(dt: float) -> void:
	if trufa:
		trufa.tick(dt)
	for bk in bikes:
		if bk == riding:
			bk.tick(dt, main.speed, main.bike_steer * lerpf(0.45, 0.15, clampf(main.speed / BIKE_SPEED, 0.0, 1.0)), main.bike_pedalling)
	if riding and rider:
		# upright when slow, further over the bars when fast, changing smoothly
		var f := smoothstep(0.0, BIKE_SPEED, absf(main.speed))
		rider_lean = lerpf(rider_lean, lerpf(0.06, 0.4, f), 1.0 - exp(-2.0 * dt))   # (round 27, the user: less lean)
		rider.lean = rider_lean
		rider.crank = riding.pedal
		rider.effort = clampf(riding.cadence / (BIKE_SPEED * 0.8), 0.0, 1.0)
		# stopped (or turning the bike round on the spot), her left foot goes down; it comes up quickly
		# when she pedals off
		var stopped: bool = absf(main.speed) < 0.3 and not main.bike_pedalling
		rider_foot = move_toward(rider_foot, 1.0 if stopped else 0.0, dt * (2.5 if stopped else 5.0))
		rider.foot_down = smoothstep(0.0, 1.0, rider_foot)
		var g: Vector3 = main.model.global_transform * Vector3(0.27, 0, 0.02)
		rider.ground_foot = Vector3(g.x, main.model.global_position.y + 0.12, g.z)


func settle(bk: Node3D) -> void:
	# (round 38, the user: "the bike should never sink into the ground anywhere") a parked bike stands on the ground under
	# its two wheels (0.55 m ahead and behind its middle; its nose is its -z), tipped to the slope between them, and as
	# far up off the hills' paths as when ridden (main.bike_lift)
	var nose := Vector3(-sin(bk.rotation.y), 0.0, -cos(bk.rotation.y)) * 0.55
	var gf: float = main.ground_at(bk.position + nose)
	var gb: float = main.ground_at(bk.position - nose)
	bk.position.y = (gf + gb) / 2.0 + main.bike_lift(bk.position)
	bk.rotation.x = atan2(gf - gb, 1.1)
