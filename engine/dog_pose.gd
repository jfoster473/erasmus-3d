# Adjusts Trufa's skeleton after her walk animation has been applied:
#   still   0..1  eases her from the walk cycle back to her standing pose
#   sit     0..1  rump down, hind legs folded, front legs straight, chest up
#   wag     radians, already oscillating; swings the tail from side to side
#   sniff   0..1  nose down towards the ground
# Directions are worked out from the skeleton itself, so they don't depend on how the
# model was exported.
extends SkeletonModifier3D

var still := 1.0
var sit := 0.0
var wag := 0.0
var sniff := 0.0
var look := 0.0                  # radians, head turned to the side
var leap := 0.0                  # 0..1 (round 23) mid-pounce: front legs reaching forward, back legs pushing out behind
var pitch := 0.0                 # radians, the whole body nose-up (+) or nose-down (-)
var grounded := true             # (round 23) keep her lowest foot on the ground (not in the basket)
# how far each joint turns when fully sitting (radians); tuned by eye
var k_tilt := 0.65
var k_thigh := 1.35
var k_shin := -1.25
var k_paw := 0.5
var k_reach := 1.0               # (the pounce)
var k_push := 0.9

var b := {}
var up := Vector3.UP
var fwd := Vector3.FORWARD
var right := Vector3.RIGHT
var height := 0.5


func setup() -> void:
	var sk := get_skeleton()
	for name in ["Hips", "tail", "tailstart", "tail1", "tail2", "tail3", "chest", "head",
			"backleg", "backleg0", "backleg1", "backleg2", "R_backleg", "R_backleg0", "R_backleg1", "R_backleg2",
			"frontleg", "frontleg0", "frontleg1", "R_frontleg", "R_frontleg0", "R_frontleg1"]:
		b[name] = sk.find_bone(name)
	var hips := rest_pos(b.Hips)
	var head := rest_pos(b.head)
	var paw := (rest_pos(b.backleg2) + rest_pos(b.R_backleg2)) / 2.0
	up = (hips - paw).normalized()
	fwd = (head - hips)
	fwd = (fwd - up * fwd.dot(up)).normalized()
	right = fwd.cross(up).normalized()
	height = (hips - paw).length()


func rest_pos(i: int) -> Vector3:
	return get_skeleton().get_bone_global_rest(i).origin


func turn(i: int, axis: Vector3, angle: float) -> void:
	# rotates bone i about an axis given in skeleton space, keeping its children attached
	if i < 0 or absf(angle) < 0.0001:
		return
	var sk := get_skeleton()
	var g := sk.get_bone_global_pose(i)
	var p := sk.get_bone_parent(i)
	var pg := sk.get_bone_global_pose(p) if p >= 0 else Transform3D()
	var nb := Basis(axis.normalized(), angle) * g.basis
	sk.set_bone_pose_rotation(i, (pg.basis.inverse() * nb).get_rotation_quaternion())


func _process_modification() -> void:
	var sk := get_skeleton()
	if sk == null or b.is_empty():
		return
	# back towards the standing pose when she isn't walking
	if still > 0.001:
		for i in sk.get_bone_count():
			var rest := sk.get_bone_rest(i)
			sk.set_bone_pose_rotation(i, sk.get_bone_pose_rotation(i).slerp(rest.basis.get_rotation_quaternion(), still))
			sk.set_bone_pose_position(i, sk.get_bone_pose_position(i).lerp(rest.origin, still))
	# a pounce: legs stretched out front and back, the body pitched
	if leap > 0.001:
		for leg in ["frontleg", "R_frontleg"]:
			turn(b[leg], right, k_reach * leap)
		for leg in ["backleg0", "R_backleg0"]:
			turn(b[leg], right, -k_push * leap)
	if absf(pitch) > 0.001:
		turn(b.Hips, right, pitch)
	# sitting: tilt the whole body back about the hips, fold the hind legs, keep the front legs upright
	if sit > 0.001:
		var tilt := k_tilt * sit
		turn(b.Hips, right, tilt)
		for leg in ["backleg0", "R_backleg0"]:
			turn(b[leg], right, k_thigh * sit)
		for leg in ["backleg1", "R_backleg1"]:
			turn(b[leg], right, k_shin * sit)
		for leg in ["backleg2", "R_backleg2"]:
			turn(b[leg], right, k_paw * sit)
		for leg in ["frontleg", "R_frontleg"]:
			turn(b[leg], right, -tilt * 0.9)
		turn(b.head, right, -tilt * 0.6)
		var hp := sk.get_bone_pose_position(b.Hips)
		sk.set_bone_pose_position(b.Hips, hp - sk.get_bone_rest(b.Hips).basis.inverse() * up * 0.0)
	# (round 23, the user: sitting at home she floated, told to stay her legs went through the ground) the sitting pose
	# tips her body back about the hips, which lifts her front paws and can push her folded hind feet down: the whole
	# dog is moved up or down so the lowest of her four feet is back on the ground, as it is standing
	if sit > 0.001 and grounded:
		var drop := INF
		for nm in ["backleg2", "R_backleg2", "frontleg1", "R_frontleg1"]:
			var bi: int = b.get(nm, -1)
			if bi >= 0:
				drop = minf(drop, (sk.get_bone_global_pose(bi).origin - rest_pos(bi)).dot(up))
		if drop != INF and absf(drop) > 0.0005:
			var par := sk.get_bone_parent(b.Hips)
			var pb: Basis = sk.get_bone_global_pose(par).basis if par >= 0 else Basis()
			sk.set_bone_pose_position(b.Hips, sk.get_bone_pose_position(b.Hips) - pb.inverse() * (up * drop * sit))
	# tail wag
	for i in [b.tailstart, b.tail1, b.tail2]:
		turn(i, up, wag * 0.45)
	# head: nose down to sniff, or turned to look
	turn(b.head, right, sniff * 0.6)
	turn(b.head, up, look)
