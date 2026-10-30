# (round 41, the user: "the guy with the kite should have his arm out and the string of the kite going to his arm")
# His right arm held out in front and up, nearly straight, towards the kite, as if holding the line; on top of whatever
# the animation does (his idle, his walk). Turned as cuff_pose.gd turns the handcuffed arms, from the character's own
# directions (holder: +z forward, +y up). `amount` eases it in.
extends SkeletonModifier3D

var model: Node3D                # the character's holder
var arm := -1                    # RightArm
var fore := -1                   # RightForeArm
var hand := -1                   # RightHand
var hand_at := Vector3.ZERO      # where his hand is once the arm is posed (world): the line starts here (npcs.gd)
var amount := 0.0
var target := Vector3.ZERO       # where the kite flies (world): the arm reaches towards it
var low := 0.0                   # (round 41, the user: "his hand's missing in one of them") 0: reaching up to the kite;
                                 # 1: talking, the line held at his chest in front of him, the hand in view


func _process_modification() -> void:
	var sk := get_skeleton()
	if sk == null or model == null or amount < 0.001 or arm < 0 or fore < 0:
		return
	var to_skel: Basis = (model.global_basis.inverse() * sk.global_basis).inverse()
	var side: Vector3 = (to_skel * Vector3(1, 0, 0)).normalized()        # the character's left
	var fwd: Vector3 = (to_skel * Vector3(0, 0, 1)).normalized()
	var up: Vector3 = (to_skel * Vector3(0, 1, 0)).normalized()
	# towards the kite, whichever way he has turned (to talk to Sandra, say); never back over his shoulder: at most
	# out to his side
	var sh: Vector3 = sk.get_bone_global_pose(arm).origin
	var to: Vector3 = (sk.global_transform.affine_inverse() * target - sh).normalized()
	var flat := to - up * to.dot(up)
	if flat.dot(fwd) < -0.1 * flat.length():
		flat = (flat - fwd * (flat.dot(fwd) + 0.1 * flat.length())).normalized() * flat.length()
	to = (flat + up * maxf(to.dot(up), 0.5)).normalized()
	var arm_up: Vector3 = (to * 0.8 - up * 0.25 - side * 0.25).normalized()   # the upper arm: a little lower and out
	var arm_low: Vector3 = (fwd * 0.45 - up * 0.85 - side * 0.2).normalized()   # by his side, the elbow a touch forward
	var fore_low: Vector3 = (fwd * 0.9 + up * 0.25 - side * 0.05).normalized()  # the forearm out in front, hand at his chest
	aim(sk, arm, arm_up.slerp(arm_low, low).normalized())
	aim(sk, fore, to.slerp(fore_low, low).normalized())                       # up: the forearm and hand along the line
	# (read back here: outside, the skeleton still gives the hand where the animation alone puts it, by his hip, and the
	# line started there)
	if hand >= 0:
		var hp := sk.get_bone_global_pose(hand)
		hand_at = sk.global_transform * (hp.origin + hp.basis * Vector3(0, 0.06 / maxf(sk.global_basis.get_scale().y, 0.001), 0))


func aim(sk: Skeleton3D, i: int, dir: Vector3) -> void:
	# turn bone i (and so everything below it) until it points along dir, by `amount` of the way
	var g := sk.get_bone_global_pose(i)
	var child := -1
	for c in sk.get_bone_children(i):
		child = c
		break
	var along: Vector3 = (g.basis * Vector3.UP).normalized()
	if child >= 0:
		var cp := sk.get_bone_global_pose(child).origin - g.origin
		if cp.length() > 0.0001:
			along = cp.normalized()
	var turn := Quaternion(along, along.slerp(dir, amount).normalized()) if absf(along.dot(dir)) < 0.9999 else Quaternion()
	g.basis = Basis(turn) * g.basis
	sk.set_bone_global_pose(i, g)
