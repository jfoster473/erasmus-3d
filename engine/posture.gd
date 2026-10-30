# Sandra's standing posture. Meshy's only idle for her (Idle_4) has her feet out in front of her, so that
# seen from the side her whole body slants back (about 8°, swaying between 4° and 9° as the idle breathes:
# "leaning back, then straight", round 21). Each frame this measures the pose the animation gives and
# puts it right: her legs swing back until her feet are under her hips (her feet turned to stay flat on the
# ground), and her back is brought upright over her hips (a touch forward, UPRIGHT), the bend spread along
# the spine so it looks natural. main.animate_skin fades it out as she walks (her walk and run have their
# own lean) and while she rides.
extends SkeletonModifier3D

const UPRIGHT := 0.03            # radians: her back, a touch forward of straight up

var model: Node3D                # her model: +z forward, +y up
var bones: Array = []            # Spine, Spine1, Spine2
var hips := -1
var neck := -1
var legs: Array = []             # LeftUpLeg, RightUpLeg
var feet: Array = []             # LeftFoot, RightFoot
var amount := 0.0                # how much of the correction to apply: 0 to 0.2 (main.IDLE_TILT) when standing
# (round 38, the user, of Jaume at Park Güell's gate: "not leaning over") someone whose model pokes its head forward
# (the old man's head sits 17° forward of his neck, the young man's 11°) can have it brought up too: opt-in, per person
const HEAD_UP := 0.10            # radians: the head, a touch forward of straight over the neck
var head := -1                   # Head (only used when straight_head)
var straight_head := false
var head_aim := HEAD_UP          # (round 40) where the head points: a touch forward; looking up at a kite, back (negative)
var head_fix := 0.0               # (round 41) per model: how far its head bone leans back of where its face looks (npcs.gd HEAD_FIX)
var head_only := false           # (round 40) the other people: their head brought up, their own walk and stance left alone
# (round 41, the user: "Their hands are going backwards, which is weird. Please do a proper full analysis on the
# body. And think about what a human body would look like") measured (tests --armprobe): the Meshy idles stand the
# people with their chest turned (the left shoulder 7–17 cm behind the right, in a 1.7 m person), their shoulders
# 3–10 cm behind their hip joints, and their hands bent back at the wrist — so a hand hung behind the body. Standing,
# a relaxed person has ear, shoulder, hip and ankle on one plumb line, the shoulders level and square, the arms hanging
# loose with the elbows softly bent, the hands beside the thighs a touch in front of the hip joint, each hand going on
# in the forearm's line, palm to the thigh. stand_body() poses them so, in that order.
const STACK := 0.02              # radians: the shoulders a touch forward of straight over the hip joints
const ELBOW := 0.21              # radians: the elbow's soft bend (12°)
const WRIST_FWD := 0.02          # the wrist in front of the hip joint, as a share of their height (3 cm in 1.7 m)
const HAND_CURL := 0.09          # radians: the hand a touch forward of the forearm's line (5°), never bent back
var arms: Array = []             # [LeftArm, LeftForeArm, LeftHand, LeftHandMiddle1, the same Right] (head_only people)
# (round 41, the user: "It still looks like they're raising their shoulders… they're tense") the idles held the
# collarbones 11–21° up, one side higher, and the arms out at uneven angles: both brought to a relaxed, even line
const CLAV_RISE := 0.06          # radians: the collarbone, neck to shoulder, a few degrees up from level (3.5°)
const ARM_OUT := 0.12            # radians: the upper arm out from the side, the same both sides (7°)
var clav: Array = []             # [LeftShoulder, RightShoulder]
# (round 41, the user: "the workmen's shoulders are still a little too high"; "the purple-haired guy seems to have the
# right body posture") each shoulder joint at least SH_DROP of their height below the base of the neck, as his are
const SH_DROP := 0.05            # of their height, sole to head (8.5 cm in a 1.7 m person)
# (round 41, the user: "the workman's hands are still going back") a model whose hand is shaped open and palm-out, the
# fingers trailing back (workman.glb), is turned palm-in about the forearm and tipped forward (npcs.gd HAND_FIX)
var sh_drop := SH_DROP           # (per model: npcs.gd BODY_FIX)
var arm_out := ARM_OUT           # (per model: a broad body hangs its arms further out)
var wrist_fwd := WRIST_FWD       # (per model: a round belly keeps the hands back beside it)
var hand_roll := 0.0             # radians about the forearm, palm towards the thigh
var hand_fwd := 0.0              # radians more forward than HAND_CURL
var arms_w := 1.0                # 1 standing, faded to 0 as they walk (npcs.gd, people.gd), so the walk keeps its swing


var probe: Array = []            # (tests: bone names to measure after the correction, posture_probe())
var probed := {}                 # name -> position in the model's frame (x left, y up, z forward), after the correction


func _process_modification() -> void:
	_correct()
	if not probe.is_empty():
		var sk := get_skeleton()
		var to_model: Transform3D = model.global_transform.affine_inverse() * sk.global_transform
		for bn in probe:
			var i := -1
			for k in sk.get_bone_count():
				var nm := sk.get_bone_name(k)
				if nm.contains("_" + bn + "_") or nm.ends_with("_" + bn) or nm.contains(":" + bn):
					i = k
					break
			if i >= 0:
				probed[bn] = to_model * sk.get_bone_global_pose(i).origin


func _correct() -> void:
	var sk := get_skeleton()
	if sk == null or model == null or absf(amount) < 0.001:
		return
	var w := clampf(amount / 0.2, 0.0, 1.0)
	# her left-right axis and her forward, in the skeleton's space
	var to_skel: Basis = (model.global_basis.inverse() * sk.global_basis).inverse()
	var side: Vector3 = (to_skel * Vector3(1, 0, 0)).normalized()
	var fwd: Vector3 = (to_skel * Vector3(0, 0, 1)).normalized()
	var up: Vector3 = (to_skel * Vector3(0, 1, 0)).normalized()
	if head_only:
		stand_body(sk, side, fwd, up, w * arms_w)
		# (round 41, the user, of a man walking: "looking at the sky in a weird way" — held upright against his walk's own
		# lean his head tipped back: walking, his walk carries his head, the correction fading out as for his arms)
		head_up(sk, side, fwd, up, w * (0.25 + 0.75 * arms_w))
		return
	if hips < 0 or neck < 0 or legs.size() < 2 or feet.size() < 2 or -1 in legs or -1 in feet:
		turn(sk, bones, side, amount / maxf(1.0, bones.size()))       # (the bones weren't found: a fixed tilt)
		head_up(sk, side, fwd, up, w)                                 # (round 40: the head still, for everyone)
		return
	var h := sk.get_bone_global_pose(hips).origin
	var n := sk.get_bone_global_pose(neck).origin
	var f := (sk.get_bone_global_pose(feet[0]).origin + sk.get_bone_global_pose(feet[1]).origin) / 2.0
	# the legs: how far the feet are in front of the hips (negative: the hips are behind them)
	var hl := h - f
	var legs_lean := atan2(hl.dot(fwd), hl.dot(up))
	turn(sk, legs, side, -legs_lean * w)
	turn(sk, feet, side, legs_lean * w)
	# the back: upright over the hips
	var nb := n - h
	var back := atan2(nb.dot(fwd), nb.dot(up))
	turn(sk, bones, side, (UPRIGHT - back) * w / maxf(1.0, bones.size()))
	head_up(sk, side, fwd, up, w)


func head_up(sk: Skeleton3D, side: Vector3, fwd: Vector3, up: Vector3, w: float) -> void:
	# the head: up over the neck (only for those who stoop, straight_head; round 40, everyone but Sandra), or back,
	# looking up (head_aim < 0: the kite flyer)
	if straight_head and head >= 0 and neck >= 0:
		var hd := sk.get_bone_global_pose(head).origin - sk.get_bone_global_pose(neck).origin
		var tip := atan2(hd.dot(fwd), hd.dot(up))
		turn(sk, [neck], side, (head_aim + head_fix - tip) * w)


func at(sk: Skeleton3D, i: int) -> Vector3:
	return sk.get_bone_global_pose(i).origin


func fwd_angle(v: Vector3, fwd: Vector3, up: Vector3) -> float:
	# how far a downward-hanging line points forward of straight down (radians, +: forward)
	return atan2(v.dot(fwd), -v.dot(up))


func stand_body(sk: Skeleton3D, side: Vector3, fwd: Vector3, up: Vector3, w: float) -> void:
	if w < 0.01 or arms.size() < 8 or legs.size() < 2 or -1 in legs or feet.size() < 2 or -1 in feet or neck < 0:
		return
	for k in [0, 1, 2, 4, 5, 6]:
		if arms[k] < 0:
			return
	var n_sp := maxf(1.0, bones.size())
	# 1. the shoulders square to the way they face: the chest turned about the upright, spread along the spine
	var d := at(sk, arms[4]) - at(sk, arms[0])                       # left shoulder to right
	var twist := atan2(d.dot(fwd), absf(d.dot(side)))                  # +: the right shoulder ahead of the left
	turn(sk, bones, up, -twist * w / n_sp)
	# 2. the shoulders stacked over the hip joints (a touch forward), the bend spread along the spine
	# (the spine bends from above the hip joints, so it takes a few goes to bring the shoulders right over them)
	var hj := (at(sk, legs[0]) + at(sk, legs[1])) / 2.0
	for _go in 3:
		var sm := (at(sk, arms[0]) + at(sk, arms[4])) / 2.0 - hj
		turn(sk, bones, side, (STACK - atan2(sm.dot(fwd), sm.dot(up))) * w / n_sp)
	# 3. the shoulders let down: each collarbone turned about the forward axis to CLAV_RISE, the same both sides, and
	# lower still where the shoulder joint would sit less than SH_DROP below the neck
	var foot := (at(sk, feet[0]) + at(sk, feet[1])) / 2.0
	var tall := maxf(0.1, (at(sk, neck) - foot).dot(up))
	var height := maxf(0.1, (at(sk, head if head >= 0 else neck) - foot).dot(up))
	if clav.size() == 2 and not -1 in clav:
		for k in 2:
			var cl := at(sk, arms[k * 4]) - at(sk, clav[k])
			var lat := cl.dot(side)                                    # (+ on her left)
			var hl := Vector2(lat, cl.dot(fwd)).length()
			var rise := atan2(cl.dot(up), hl)
			var sgn := 1.0 if lat > 0.0 else -1.0
			turn(sk, [clav[k]], fwd, (CLAV_RISE - rise) * sgn * w)
			var dh := (at(sk, arms[k * 4]) - at(sk, neck)).dot(up) + sh_drop * height
			if dh > 0.0:
				turn(sk, [clav[k]], fwd, -clampf(dh / maxf(0.02, hl), 0.0, 0.4) * sgn * w)
	hj = (at(sk, legs[0]) + at(sk, legs[1])) / 2.0
	for k in [0, 4]:
		var sh: int = arms[k]
		var el: int = arms[k + 1]
		var wr: int = arms[k + 2]
		var tip: int = arms[k + 3]
		# 4. the upper arm hung ARM_OUT from the side (turned about the forward axis), the same both sides
		var ua0 := at(sk, el) - at(sk, sh)
		var sgo := 1.0 if k == 0 else -1.0                         # (her left arm's outside is +side, her right's -side)
		var out := atan2(ua0.dot(side) * sgo, -ua0.dot(up))         # (signed: an arm leaning in across the body is < 0)
		turn(sk, [sh], fwd, (arm_out - out) * sgo * w)
		# 5. the elbow softly bent (the forearm ELBOW forward of the upper arm's line)
		var bend := fwd_angle(at(sk, wr) - at(sk, el), fwd, up) - fwd_angle(at(sk, el) - at(sk, sh), fwd, up)
		turn(sk, [el], side, -(ELBOW - bend) * w)
		# 6. the upper arm swung until the wrist hangs WRIST_FWD in front of the hip joint
		var v := at(sk, wr) - at(sk, sh)
		var want_f := (hj - at(sk, sh)).dot(fwd) + wrist_fwd * tall
		var swing := atan2(want_f, -v.dot(up)) - fwd_angle(v, fwd, up)
		turn(sk, [sh], side, -clampf(swing, -0.6, 0.6) * w)
		# 7. the hand on in the forearm's line, curled a touch forward, never bent back
		if tip < 0:
			continue
		var hand_a := fwd_angle(at(sk, tip) - at(sk, wr), fwd, up)
		var fore_a := fwd_angle(at(sk, wr) - at(sk, el), fwd, up)
		turn(sk, [wr], side, -(fore_a + HAND_CURL + hand_fwd - hand_a) * w)
		if absf(hand_roll) > 0.001:
			turn(sk, [wr], (at(sk, wr) - at(sk, el)).normalized(), hand_roll * (1.0 if k == 0 else -1.0) * w)


func turn(sk: Skeleton3D, which: Array, side: Vector3, each: float) -> void:
	# each bone turned by `each` radians about her left-right axis (+: the bone's far end goes forward)
	for i in which:
		if i < 0:
			continue
		var p := sk.get_bone_parent(i)
		var pb: Basis = sk.get_bone_global_pose(p).basis.orthonormalized() if p >= 0 else Basis()
		var axis: Vector3 = (pb.inverse() * side).normalized()
		sk.set_bone_pose_rotation(i, Quaternion(axis, each) * sk.get_bone_pose_rotation(i))
