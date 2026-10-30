# Sandra's whole pose on the bicycle, worked out every frame from her rest pose (her walk and idle
# animations are stopped while she rides; see main.animate_skin):
#   - sitting, leaning forward from the hips: upright when slow, further over the bars when fast, with
#     a small sway of the hips with each pedal stroke and the shoulders swaying against it
#   - head up, looking along the street
#   - legs: feet on the pedals, knees forward and a little out; arms: hands on the grips, elbows
#     relaxed, a little out and back (each limb is a two-bone reach, solved here directly)
#   - feet nearly level on the pedals, the toes dipping a little at the bottom of each stroke
#   - stopped, her left foot comes off its pedal and down onto the ground beside the bike
# Directions come from the model the skeleton belongs to (forward +z, up +y), so they don't depend on
# how the file was exported. Everything is computed from the rest pose without asking the skeleton
# for its current pose, so nothing depends on what else has run this frame.
extends SkeletonModifier3D

var model: Node3D                # Sandra's model node: its +z is the way the bike points
var b := {}                      # bone indices
var targets := {}                # foot_l/r, hand_l/r: nodes on the bike; knee_l/r, elbow_l/r: pole nodes
var lean := 0.1                  # radians the body leans forward from upright
var crank := 0.0                 # crank angle (radians)
var effort := 0.0                # 0..1: how hard she is pedalling (more sway)
var foot_down := 0.0             # 0..1: her left foot on its pedal .. on the ground
var ground_foot := Vector3.ZERO  # where it goes on the ground (world space)
var head_down := 0.0             # radians: her head bowed (at the exam desk, round 22, looking at her paper)
var hide_head := false           # (round 41, sitting on a bench in her own view) her head shrunk away: the camera is at her eyes
var loc := {}                    # working bone transforms (parent space)


func setup(m: Node3D, bones: Dictionary, t: Dictionary) -> void:
	model = m
	b = bones
	targets = t


func rest_xf(i: int) -> Transform3D:
	return get_skeleton().get_bone_rest(i)


func gxf(i: int) -> Transform3D:
	var p := get_skeleton().get_bone_parent(i)
	return (gxf(p) if p >= 0 else Transform3D()) * loc.get(i, rest_xf(i))


func rotate_global(i: int, r: Basis) -> void:
	# turns bone i about its own joint by r (given in skeleton space); its children follow
	if i < 0:
		return
	var p := get_skeleton().get_bone_parent(i)
	var pg := gxf(p).basis if p >= 0 else Basis()
	var cur: Transform3D = loc.get(i, rest_xf(i))
	loc[i] = Transform3D(pg.inverse() * r * gxf(i).basis, cur.origin)


func set_bone_basis(i: int, want: Basis) -> void:
	var p := get_skeleton().get_bone_parent(i)
	var pg := gxf(p).basis if p >= 0 else Basis()
	loc[i] = Transform3D(pg.inverse() * want, rest_xf(i).origin)


func arc(from: Vector3, to: Vector3) -> Basis:
	if from.length() < 1e-5 or to.length() < 1e-5:
		return Basis()
	return Basis(Quaternion(from.normalized(), to.normalized()))


func reach(root: int, mid: int, end: int, target: Vector3, pole: Vector3) -> void:
	# a two-bone limb: the end joint to the target, the middle joint bending towards the pole
	if root < 0 or mid < 0 or end < 0:
		return
	var a := gxf(root).origin
	var l1 := a.distance_to(gxf(mid).origin)
	var l2 := gxf(mid).origin.distance_to(gxf(end).origin)
	var to := target - a
	var d := clampf(to.length(), 0.02, (l1 + l2) * 0.999)
	var n := to.normalized()
	var q := (pole - a) - n * (pole - a).dot(n)
	q = q.normalized() if q.length() > 1e-4 else n.cross(Vector3.RIGHT).normalized()
	var ca := clampf((l1 * l1 + d * d - l2 * l2) / (2.0 * l1 * d), -1.0, 1.0)
	var knee := a + n * (l1 * ca) + q * (l1 * sqrt(1.0 - ca * ca))
	rotate_global(root, arc(gxf(mid).origin - a, knee - a))
	var m := gxf(mid).origin
	rotate_global(mid, arc(gxf(end).origin - m, a + n * d - m))


var runs := 0                     # (how many times it has posed her: tests)


func _process_modification() -> void:
	runs += 1
	var sk := get_skeleton()
	if sk == null or model == null or b.is_empty() or targets.is_empty():
		return
	loc.clear()
	var to_sk := sk.global_transform.affine_inverse()
	var mb := (to_sk * model.global_transform).basis
	var up := (mb * Vector3.UP).normalized()
	var fwd := (mb * Vector3(0, 0, 1)).normalized()
	var pitch := up.cross(fwd).normalized()      # turning about this tips the top forwards
	var sway := sin(crank) * (0.025 + 0.03 * effort)
	# (round 23, the user: "her legs are weirdly shifted to the side when she cycles") the standing animation that plays
	# under this carries her hips a few centimetres to one side; on the saddle they go back over its middle (where the
	# seat was measured from, the rest pose), keeping only the animation's height and forward position
	var hp := sk.get_bone_pose_position(b.hips)
	var hr := sk.get_bone_rest(b.hips).origin
	var across := (mb * Vector3.RIGHT).normalized()
	var hpar := sk.get_bone_parent(b.hips)
	var pb: Basis = sk.get_bone_global_pose(hpar).basis if hpar >= 0 else Basis()
	var off := pb * (hp - hr)                      # (the animation's shift, in the skeleton's space)
	sk.set_bone_pose_position(b.hips, hp - pb.inverse() * (across * off.dot(across)))
	# lean forward: a little from the pelvis, the rest spread up the spine
	rotate_global(b.hips, Basis(pitch, lean * 0.3) * Basis(fwd, sway))
	rotate_global(b.spine, Basis(pitch, lean * 0.25))
	rotate_global(b.spine1, Basis(pitch, lean * 0.25) * Basis(fwd, -sway * 1.6))
	rotate_global(b.spine2, Basis(pitch, lean * 0.2))
	# shoulders rounding a little as she gets down; head comes forward with them but stays up,
	# looking along the street
	rotate_global(b.shoulder_l, Basis(pitch, lean * 0.25))
	rotate_global(b.shoulder_r, Basis(pitch, lean * 0.25))
	rotate_global(b.neck, Basis(pitch, -lean * 0.3 + head_down * 0.45))
	rotate_global(b.head, Basis(pitch, -lean * 0.3 - 0.04 + head_down * 0.55))
	# legs and arms
	for s in ["l", "r"]:
		var foot: Vector3 = targets["foot_" + s].global_position
		if s == "l":
			foot = foot.lerp(ground_foot, foot_down)
		reach(b["upleg_" + s], b["leg_" + s], b["foot_" + s], to_sk * foot, to_sk * targets["knee_" + s].global_position)
		reach(b["arm_" + s], b["fore_" + s], b["hand_" + s], to_sk * targets["hand_" + s].global_position,
			to_sk * targets["elbow_" + s].global_position)
	# feet nearly level, toes dipping a little at the bottom of each stroke
	for side in [["l", crank], ["r", crank + PI]]:
		var f: int = b["foot_" + side[0]]
		if f >= 0:
			var dip := 0.12 + 0.12 * sin(side[1] - 0.6)
			if side[0] == "l":
				dip *= 1.0 - foot_down                # flat on the ground when it's down
			set_bone_basis(f, Basis(pitch, dip) * Basis(sk.get_bone_global_rest(f).basis.get_rotation_quaternion()))
	for i in loc:
		sk.set_bone_pose_rotation(i, loc[i].basis.get_rotation_quaternion())
	sk.set_bone_pose_scale(b.head, Vector3.ONE * (0.01 if hide_head else 1.0))

