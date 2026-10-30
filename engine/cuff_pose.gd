# Hands behind the back, for Manolo once Agent Bofarull has handcuffed him (round 22). On top of whatever the
# animation does (his idle): each upper arm swung down and back, each forearm folded in behind him, so the
# wrists meet at the small of his back. `amount` eases it in. The bones are turned in the skeleton's own space,
# from the directions of the character (holder: +z forward, +y up).
extends SkeletonModifier3D

var model: Node3D                # the character's holder
var arms: Array = []             # [LeftArm, LeftForeArm, RightArm, RightForeArm]
var amount := 0.0


func _process_modification() -> void:
	var sk := get_skeleton()
	if sk == null or model == null or amount < 0.001 or arms.size() < 4 or -1 in arms:
		return
	var to_skel: Basis = (model.global_basis.inverse() * sk.global_basis).inverse()
	var side: Vector3 = (to_skel * Vector3(1, 0, 0)).normalized()        # the character's left
	var fwd: Vector3 = (to_skel * Vector3(0, 0, 1)).normalized()
	var up: Vector3 = (to_skel * Vector3(0, 1, 0)).normalized()
	for k in 2:
		var s := 1.0 if k == 0 else -1.0                                  # left arm, then right
		aim(sk, arms[k * 2], (-up * 0.82 - fwd * 0.5 + side * s * 0.12).normalized())
		aim(sk, arms[k * 2 + 1], (-side * s * 0.8 - fwd * 0.42 + up * 0.3).normalized())


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
