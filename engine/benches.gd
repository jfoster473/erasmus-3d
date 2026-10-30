# Benches (round 41, the user: "the benches should be solid. And it would be nice if you can sit on them, then have a
# first-person view where you can look around. Or press E to get up again. For all the benches. Both the ones on the
# hill and the ones in the city."): every bench the build lists (scene 'benches': [x, z, yaw, seat height] — yaw the
# way its seat faces, (sin, cos); the seat's top, metres) stands solid, and E in front of one sits her down on it: the
# view goes to her own eyes, the arrows or the mouse look round, and E gets her up again, a step in front of it.
extends Node

const REACH := 1.3               # how far from the bench's front she can be to sit
const FRONT := 0.75              # where she stands, in front of the seat's middle
const EYE := 0.78                # her eyes over the seat, sitting (round 41: up and forward a little, so looking down she sees her lap past her chest)
const LEAN := 0.2                # leaning a little forward to look round

var main: Node
var list := []                   # [Vector2 pos, Vector2 face, seat height]
var at := -1                     # the bench she sits on (-1: none)
const THIGH_R := 0.075           # (round 41) her thigh's thickness under its bone: how far her hip joints sit over the seat
const SEAT_FRONT := 0.24         # how far the seat's front edge is in front of the bench's middle (the Meshy bench)
var pose: SkeletonModifier3D     # (round 41) her sitting pose (rider_pose.gd's reach), while she sits
var marks: Array = []            # its targets: feet, knees, hands, elbows


func setup(m: Node) -> void:
	main = m
	var body: StaticBody3D = main.static_body(main.LAYER_BODY)
	for b in main.D.get("benches", []):
		var p := Vector2(float(b[0]), float(b[1]))
		var f := Vector2(sin(float(b[2])), cos(float(b[2])))
		list.append([p, f, float(b[3])])
		var side := f.orthogonal()
		for s in [-0.45, 0.45]:                           # (solid: two posts along it, a little behind the seat's front)
			var q: Vector2 = p + side * s - f * 0.05
			main.add_post(body, q.x, q.y, 0.32)


func seated() -> bool:
	return at >= 0


func candidates(p: Vector3) -> Array:
	var out := []
	if seated():
		return out
	for i in list.size():
		var b: Array = list[i]
		var fr: Vector2 = b[0] + b[1] * FRONT
		if absf(fr.x - p.x) < 4.0 and absf(fr.y - p.z) < 4.0:
			out.append({"x": fr.x, "z": fr.y, "r": REACH, "label": "Sit on the bench", "act": "bench", "i": i})
	return out


func near_bench(p: Vector2, within: float) -> bool:
	for b in list:
		if (b[0] as Vector2).distance_to(p) < within:
			return true
	return false


func sit(i: int) -> void:
	if seated() or i < 0 or i >= list.size():
		return
	var b: Array = list[i]
	at = i
	main.face_target = INF
	main.speed = 0.0
	main.ambience.sfx("cloth")
	main.player.global_position = Vector3(b[0].x + b[1].x * 0.05, float(b[2]), b[0].y + b[1].y * 0.05)
	main.model.position.y = 0.0
	main.model.rotation.y = atan2(b[1].x, b[1].y)
	main.cutscene = true
	main.ride_cam = true
	main.ride_look = true
	sit_pose(b)
	main.seat_eye = EYE
	main.seat_lean = LEAN
	main.cam_yaw_node.rotation.y = atan2(b[1].x, b[1].y) + PI      # (the camera looks along its -z: the way she faces)
	main.cam_pitch_node.rotation.x = -0.08
	main.last_manual_cam = main.t


func stand() -> void:
	if not seated():
		return
	var b: Array = list[at]
	at = -1
	var fr: Vector2 = b[0] + b[1] * FRONT
	main.ride_look = false
	main.ride_cam = false
	main.cutscene = false
	if pose:
		pose.queue_free()
		pose = null
	for n in marks:
		n.queue_free()
	marks.clear()
	main.skins[main.skin_idx].root.position = Vector3.ZERO
	main.seat_eye = -1.0
	main.seat_lean = main.SEAT_LEAN
	main.player.global_position = Vector3(fr.x, 0.0, fr.y)
	main.model.rotation.y = atan2(b[1].x, b[1].y)
	main.model.position.y = main.ground_at(main.player.global_position)
	main.cam_pitch_node.rotation.x = main.CAM_PITCH
	main.ambience.sfx("cloth")


func sit_pose(b: Array) -> void:
	# (round 41, the user: "add her body sitting down when sitting on the bench") as at the exam's bench
	# (exam_scene.gd): her hips on the seat, thighs along it, shins hanging, hands resting on her thighs; her head
	# shrunk away, since the camera is at her eyes — looking down she sees her own lap and shoes
	var sk: Dictionary = main.skins[main.skin_idx]
	if sk.ap:
		sk.ap.stop()
	var skel: Skeleton3D = sk.root.find_children("*", "Skeleton3D", true, false)[0]
	skel.reset_bone_poses()
	if sk.get("posture"):
		sk.posture.amount = 0.0
	var bn := func(n: String) -> int:
		return skel.find_bone(main.street.bone(skel, "mixamorig:" + n))
	# (round 41, the user: "You should not be able to see her legs going through the seat… her thigh should be at right
	# angles with her body, and then her legs should be hanging down at right angles from her thigh… Down, right angle,
	# right angle again, down. Also, her posture has her stomach coming out. She should be sitting up straight")
	# Laid out from her own hip joints: they sit a thigh's thickness over the seat (THIGH_R), so the thighs rest ON it,
	# set back from its front edge by a thigh's length less a little, so the knees come just past it; each thigh runs
	# level, straight ahead; each foot is a shin's length straight below its knee — two right angles; her back upright.
	sk.root.position = Vector3.ZERO
	var gs := skel.global_transform
	var rest_at := func(n: String) -> Vector3:
		return gs * skel.get_bone_global_rest(bn.call(n)).origin
	var upl: Vector3 = rest_at.call("LeftUpLeg")
	var upr: Vector3 = rest_at.call("RightUpLeg")
	var thigh: float = upl.distance_to(rest_at.call("LeftLeg"))
	var shin: float = (rest_at.call("LeftLeg") as Vector3).distance_to(rest_at.call("LeftFoot"))
	var f := Vector3(b[1].x, 0.0, b[1].y)
	var up := Vector3.UP
	var lft: Vector3 = main.model.global_basis.x.normalized()     # (her left: the model faces +z)
	var joints := (upl + upr) / 2.0
	var want := Vector3(b[0].x, float(b[2]) + THIGH_R, b[0].y) + f * (SEAT_FRONT - thigh + 0.03)
	var off := want - joints
	off.y = want.y - joints.y
	sk.root.position = main.model.global_transform.basis.inverse() * off
	upl += off
	upr += off
	var pts := {}
	for sd in [["l", 1.0, upl], ["r", -1.0, upr]]:
		var sx: float = sd[1]
		var j: Vector3 = sd[2]
		var knee := j + f * thigh                                  # (level with the hip: the first right angle)
		pts["foot_" + sd[0]] = knee - up * shin                     # (straight down from the knee: the second)
		pts["knee_" + sd[0]] = j + f * (thigh + 0.8) + up * 0.8      # (the knee bends forward and up, to there)
		pts["hand_" + sd[0]] = j + f * (thigh * 0.6) + up * (THIGH_R + 0.035) - lft * (0.01 * sx)
		pts["elbow_" + sd[0]] = j + lft * (0.28 * sx) - f * 0.05 + up * 0.3
	var tg := {}
	for k in pts:
		var n := Node3D.new()
		main.add_child(n)
		n.global_position = pts[k]
		tg[k] = n
		marks.append(n)
	pose = SkeletonModifier3D.new()
	pose.set_script(load("res://engine/rider_pose.gd"))
	skel.add_child(pose)
	var bones := {}
	for pair in [["hips", "Hips"], ["spine", "Spine"], ["spine1", "Spine1"], ["spine2", "Spine2"], ["neck", "Neck"], ["head", "Head"],
			["upleg_l", "LeftUpLeg"], ["leg_l", "LeftLeg"], ["foot_l", "LeftFoot"], ["upleg_r", "RightUpLeg"], ["leg_r", "RightLeg"], ["foot_r", "RightFoot"],
			["shoulder_l", "LeftShoulder"], ["shoulder_r", "RightShoulder"], ["arm_l", "LeftArm"], ["fore_l", "LeftForeArm"], ["hand_l", "LeftHand"], ["arm_r", "RightArm"], ["fore_r", "RightForeArm"], ["hand_r", "RightHand"]]:
		bones[pair[0]] = bn.call(pair[1])
	pose.setup(main.model, bones, tg)
	pose.lean = 0.0                     # (upright: "sitting up straight", not leaning back with her stomach out)
	pose.head_down = 0.0
	pose.crank = 0.0
	pose.hide_head = true
	pose.active = true


func clamp_look() -> void:
	# (round 41, the user: "with the bench sitting, you should only be able to look… 180 degrees, both up and down") a
	# quarter turn either side of the way the bench faces, and from the sky overhead to her own lap
	if not seated() or not main.ride_look:
		return
	var b: Array = list[at]
	var ahead := atan2(b[1].x, b[1].y) + PI                        # (the camera looks along its -z: the way she faces)
	var dy := clampf(wrapf(main.cam_yaw_node.rotation.y - ahead, -PI, PI), -PI / 2.0, PI / 2.0)
	main.cam_yaw_node.rotation.y = ahead + dy
	main.cam_pitch_node.rotation.x = clampf(main.cam_pitch_node.rotation.x, -PI / 2.0 + 0.1, PI / 2.0 - 0.1)
