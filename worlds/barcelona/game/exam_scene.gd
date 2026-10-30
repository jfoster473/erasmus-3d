# The final exam (round 22, the user: "no quiz: the screen fades dark, a montage of Sandra at a desk in front of
# the professor, writing, then dark again, and he says she has passed"). In the UPF's lecture room: she sits in
# the front row (rider_pose.gd's seated reach: hips on the bench, feet on the floor, her left hand holding the
# paper, her right hand writing, head bowed), Prof. Oriol at the lectern. Four slow shots with dips to black
# between them, the clock moving on an hour, "An hour later…", then back to the game, Oriol reads her paper and
# tells her she has passed. game.run_exam() calls play().
extends Node

const ROW := Vector3(4.0, 0.0, 4.98)      # her seat on the front bench, towards its front edge (room metres: x across, z from the back wall)
const SEAT_H := 0.48
const DESK := Vector3(4.0, 0.745, 4.665)  # the fold-down desk in front of her (its middle: it runs z 4.53-4.80, top 0.74)
# (round 41, the user chose her arms 28% shorter, then: "fix up the hands at the desk because they go into her body maybe,
# or go invisible") her paper and her hands 4 cm nearer her, still on the desk, her elbows out at her sides, not behind
const NEAR := Vector3.ZERO      # (tried 4 cm nearer her: the hands went into her body; on the desk's middle instead)
const LECTERN := Vector3(3.5, 0.0, 1.85)  # where he stands: behind the lectern (its stand is at 3.3-3.7, 2.3-2.7), facing the room

var main: Node3D
var O := Vector3.ZERO                     # the room's corner
var cam: Camera3D
var props: Array = []
var marks := {}                           # rider_pose targets
var pose: SkeletonModifier3D
var pencil: MeshInstance3D
var writing := false
var t := 0.0
var hid: Array = []
var oriol_was := {}
var layer: CanvasLayer           # our own: the black and the words, above everything
var black: ColorRect


func play(m: Node3D, done: Callable) -> void:
	main = m
	O = main.room_base("int_upf")
	main.busy = true
	main.cutscene = true
	layer = CanvasLayer.new()
	layer.layer = 100
	main.add_child(layer)
	black = ColorRect.new()
	black.color = Color(0, 0, 0, 0)
	black.set_anchors_preset(Control.PRESET_FULL_RECT)
	black.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(black)
	await dip(1.0, 0.9)
	set_up()
	# 1 the room: from the blackboard's side, Sandra writing in the front row, Oriol at his lectern
	await shot(Vector3(7.2, 2.1, 2.2), Vector3(6.5, 1.85, 2.6), Vector3(3.75, 0.95, 3.6), Vector3(3.75, 1.0, 3.75), 4.4, "The final exam · Universitat Pompeu Fabra")
	await dip(1.0, 0.45)
	# 2 her paper and her hands, from across the desk, her head bowed over it
	await shot(Vector3(4.75, 1.75, 3.85), Vector3(4.6, 1.62, 3.95), DESK + Vector3(-0.02, 0.05, 0.12), DESK + Vector3(0.0, 0.08, 0.14), 3.8)
	await dip(1.0, 0.45)
	# 3 Oriol watching, from beside her
	await shot(Vector3(4.75, 1.3, 4.55), Vector3(4.6, 1.35, 4.25), Vector3(3.35, 1.55, 2.85), Vector3(3.35, 1.62, 2.85), 3.6)
	await dip(1.0, 0.45)
	# 4 low, in front of her: still writing, the light moving as the hour goes by
	await shot(Vector3(5.3, 0.95, 3.75), Vector3(5.05, 1.0, 3.9), Vector3(4.0, 0.95, 4.95), Vector3(4.0, 0.95, 4.95), 4.2, "", 45.0)
	await dip(1.0, 0.9)
	var later := caption("An hour later…", 34, true)
	var tw := create_tween()
	tw.tween_property(later, "modulate:a", 1.0, 0.6)
	tw.tween_interval(1.2)
	tw.tween_property(later, "modulate:a", 0.0, 0.6)
	await tw.finished
	later.queue_free()
	tear_down()
	await dip(0.0, 0.9)
	layer.queue_free()
	main.busy = false
	main.cutscene = false
	done.call()


func dip(to: float, secs: float) -> void:
	var tw := create_tween()
	tw.tween_property(black, "color:a", to, secs)
	await tw.finished


func caption(text: String, size: int, centre := false) -> Label:
	var l: Label = main.make_label(size, Color(1, 0.97, 0.9))
	l.text = text
	l.modulate.a = 0.0
	var vs: Vector2 = main.play_area()
	if centre:
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.size = Vector2(vs.x, 60)
		l.position = Vector2(0, vs.y / 2.0 - 30)
	else:
		l.position = Vector2(48, vs.y - 90)
	layer.add_child(l)
	return l


func shot(p0: Vector3, p1: Vector3, l0: Vector3, l1: Vector3, secs: float, words := "", clock_mins := 0.0) -> void:
	# one slow camera move (room metres), while the screen comes up from black; words along the bottom if given
	cam.current = true
	var lab: Label = caption(words, 22) if words != "" else null
	var start_time: float = float(main.game.S.time)
	var tw := create_tween().set_parallel(true)
	tw.tween_method(func(k: float):
		var e := k * k * (3.0 - 2.0 * k)
		cam.global_position = O + p0.lerp(p1, e)
		cam.look_at(O + l0.lerp(l1, e), Vector3.UP)
		if clock_mins > 0.0:
			main.game.S.time = fmod(start_time + clock_mins * k, 1440.0), 0.0, 1.0, secs)
	tw.tween_property(black, "color:a", 0.0, 0.5)
	if lab:
		tw.tween_property(lab, "modulate:a", 1.0, 0.8).set_delay(0.4)
		tw.tween_property(lab, "modulate:a", 0.0, 0.6).set_delay(secs - 0.9)
	await tw.finished
	if lab:
		lab.queue_free()


func set_up() -> void:
	# the room as it is, the HUD hidden, a camera of our own
	for c in main.get_children():
		if c is CanvasLayer and c != layer and c.visible:
			hid.append(c)
			c.visible = false
	cam = Camera3D.new()
	cam.fov = 42.0
	cam.far = 200.0
	main.add_child(cam)
	# the paper, two sheets, a few lines of her writing; and her pencil
	var paper := StandardMaterial3D.new()
	paper.albedo_color = Color(0.97, 0.96, 0.92)
	paper.roughness = 0.9
	for k in 2:
		var sheet := MeshInstance3D.new()
		var pm := BoxMesh.new()
		pm.size = Vector3(0.21, 0.002, 0.15)
		sheet.mesh = pm
		sheet.material_override = paper
		main.add_child(sheet)
		sheet.global_position = O + DESK + NEAR + Vector3(-0.06 + k * 0.19, 0.002 + k * 0.001, 0.0)
		sheet.rotation.y = 0.06 - k * 0.1
		props.append(sheet)
	var ink := StandardMaterial3D.new()
	ink.albedo_color = Color(0.25, 0.27, 0.38)
	for k in 6:
		var line := MeshInstance3D.new()
		var lm := BoxMesh.new()
		lm.size = Vector3(0.15 - (k % 3) * 0.025, 0.001, 0.004)
		line.mesh = lm
		line.material_override = ink
		main.add_child(line)
		line.global_position = O + DESK + NEAR + Vector3(-0.07 + (0.15 - lm.size.x) / 2.0 * -1.0, 0.0035, -0.055 + k * 0.016)
		props.append(line)
	pencil = MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.0045
	cyl.bottom_radius = 0.001
	cyl.height = 0.15
	pencil.mesh = cyl
	var pmat := StandardMaterial3D.new()
	pmat.albedo_color = Color(0.95, 0.75, 0.2)
	pencil.material_override = pmat
	main.add_child(pencil)
	props.append(pencil)
	# Sandra on the bench, facing the blackboard (-z), her pose from rider_pose.gd
	main.player.global_position = O + ROW
	main.model.rotation.y = PI
	var sk: Dictionary = main.skins[main.skin_idx]
	if sk.ap:
		sk.ap.stop()
	var skel: Skeleton3D = sk.root.find_children("*", "Skeleton3D", true, false)[0]
	skel.reset_bone_poses()
	if sk.get("posture"):
		sk.posture.amount = 0.0
	var hips := skel.find_bone(main.street.bone(skel, "mixamorig:Hips"))
	var hips_at: Vector3 = main.model.to_local(skel.global_transform * skel.get_bone_global_rest(hips).origin)
	var seat_local: Vector3 = main.model.to_local(O + Vector3(ROW.x, SEAT_H, ROW.z))
	sk.root.position = seat_local + Vector3(0, 0.05, 0) - hips_at
	# her legs are too short for the bench to reach the floor (the user saw them go straight down through it): the
	# thighs along the seat, the shins hanging from the knees, measured from her own leg bones
	var gs := skel.global_transform
	var bl := func(a: String, b: String) -> float:
		var ia := skel.find_bone(main.street.bone(skel, "mixamorig:" + a))
		var ib := skel.find_bone(main.street.bone(skel, "mixamorig:" + b))
		return (gs * skel.get_bone_global_rest(ia).origin).distance_to(gs * skel.get_bone_global_rest(ib).origin)
	var thigh: float = bl.call("LeftUpLeg", "LeftLeg")
	var shin: float = bl.call("LeftLeg", "LeftFoot")
	var hip_y := SEAT_H + 0.05
	var feet := []
	for sx in [-0.085, 0.085]:
		feet.append(Vector3(ROW.x + sx, hip_y - shin * 0.93, ROW.z - thigh * 0.95 + 0.04))
	for pv in [["foot_l", feet[0]], ["foot_r", feet[1]],
			["knee_l", Vector3(ROW.x - 0.12, hip_y + 0.3, ROW.z - thigh - 0.5)], ["knee_r", Vector3(ROW.x + 0.12, hip_y + 0.3, ROW.z - thigh - 0.5)],
			# (round 41, the user: "Her hand is going inside of her body. Maybe you need to make it come out a bit further at
			# the shoulder. And then move it around a bit more so her hand's more in front of her") her left hand out on the
			# desk in front of her, holding the paper's corner, its elbow well out to her side and forward
			["hand_l", DESK + Vector3(-0.15, 0.095, 0.02)], ["hand_r", DESK + Vector3(0.05, 0.095, 0.0)],
			["elbow_l", Vector3(3.25, 0.95, 4.75)], ["elbow_r", Vector3(4.75, 0.95, 4.75)]]:
		var n := Node3D.new()
		main.add_child(n)
		n.global_position = O + pv[1]
		marks[pv[0]] = n
		props.append(n)
	pose = SkeletonModifier3D.new()
	pose.set_script(load("res://engine/rider_pose.gd"))
	skel.add_child(pose)
	var bones := {}
	for pair in [["hips", "Hips"], ["spine", "Spine"], ["spine1", "Spine1"], ["spine2", "Spine2"], ["neck", "Neck"], ["head", "Head"],
			["upleg_l", "LeftUpLeg"], ["leg_l", "LeftLeg"], ["foot_l", "LeftFoot"], ["upleg_r", "RightUpLeg"], ["leg_r", "RightLeg"], ["foot_r", "RightFoot"],
			["shoulder_l", "LeftShoulder"], ["shoulder_r", "RightShoulder"], ["arm_l", "LeftArm"], ["fore_l", "LeftForeArm"], ["hand_l", "LeftHand"], ["arm_r", "RightArm"], ["fore_r", "RightForeArm"], ["hand_r", "RightHand"]]:
		bones[pair[0]] = skel.find_bone(main.street.bone(skel, "mixamorig:" + pair[1]))
	pose.setup(main.model, bones, marks)
	pose.lean = 0.38
	pose.head_down = 0.85
	pose.crank = 0.0
	pose.active = true
	# Prof. Oriol at the lectern, facing the room
	var q: Dictionary = main.npcs.indoor.get("oriol", {})
	if not q.is_empty():
		oriol_was = {"pos": q.holder.global_position, "yaw": q.yaw}
		q.holder.global_position = O + LECTERN
		q.holder.rotation.y = 0.0
		q.yaw = 0.0
		q.target = q.holder.position
		q.talking = false
	writing = true


func _process(dt: float) -> void:
	if not writing:
		return
	t += dt
	# her right hand writes along a line, small loops as she goes, a new line every few seconds
	var line := floorf(t / 2.6)
	var along := fmod(t, 2.6) / 2.6
	var base: Vector3 = O + DESK + NEAR + Vector3(-0.02 + along * 0.13, 0.095, -0.02 + fmod(line, 4.0) * 0.012)   # (on the paper, out in front of her)
	var hr: Node3D = marks.hand_r
	hr.global_position = base + Vector3(sin(t * 15.0) * 0.004, absf(sin(t * 7.5)) * 0.004, cos(t * 15.0) * 0.003)
	# the pencil: its point on the paper just ahead of her fingers, leaning back towards her elbow
	var tip := hr.global_position + Vector3(-0.015, -0.08, -0.09)      # (round 41: her hand 4.5 cm higher, over the desk, not in it)
	var top := hr.global_position + Vector3(0.03, 0.035, 0.0)
	# (the cylinder's axis is its y, the point at its foot: a proper right-handed basis, unscaled; a sheared one
	# once froze the whole picture)
	var y := (top - tip).normalized()
	var x := y.cross(Vector3.UP)
	x = x.normalized() if x.length() > 0.01 else Vector3.RIGHT
	var z := x.cross(y).normalized()
	pencil.global_transform = Transform3D(Basis(x, y, z), (tip + top) / 2.0)


func tear_down() -> void:
	writing = false
	if pose:
		pose.queue_free()
	for p in props:
		p.queue_free()
	props.clear()
	var sk: Dictionary = main.skins[main.skin_idx]
	sk.root.position = Vector3.ZERO
	# standing in front of the lectern, her paper handed in
	main.player.global_position = O + Vector3(3.6, 0.0, 3.75)
	main.model.rotation.y = PI
	var q: Dictionary = main.npcs.indoor.get("oriol", {})
	if not q.is_empty():
		q.holder.global_position = O + LECTERN + Vector3(0, 0, 0.1)
		q.yaw = 0.0
	for c in hid:
		c.visible = true
	hid.clear()
	main.room_cam.current = true
	cam.queue_free()
