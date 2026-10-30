# Trufa, Montse's little dog.
#   LOST        sniffs about where she ran off to, until Sandra calls her
#   FOLLOW      trots at Sandra's heels, round corners along the way Sandra walked
#   STAY        sits where she was told, until Sandra walks off; then she heads home
#   WAIT        (round 23) sits outside the building Sandra went into: she follows again if Sandra comes back to
#               her; once she knows the way home (the mission is done) she gives up after 30 s and runs to Montse
#   GOING_HOME  retraces her steps (taking short cuts where the way is clear) back to Montse
#   HOME        sits by Montse's feet, gets up now and then for a sniff and a stretch
# Until Sandra has called her by her name she is shy: if Sandra comes at her she skips out of the way, off to
# the side (round 20). Once she knows Sandra (round 22, the user's wish) she lets her come close: walking into
# her just nudges her along, her legs going as if she were walking. Following, she runs at Sandra's own
# pace, catching up and then trotting alongside her; when Sandra gets on her bike Trufa hops into its big
# front basket and rides sitting up, and hops out again when Sandra gets off.
# The model is a rigged Meshy dog with a walk cycle; dog_pose.gd adds sitting, the wagging
# tail and the sniffing nose on top.
extends Node3D

enum { LOST, HOME, FOLLOW, STAY, GOING_HOME, WAIT }

const FOLLOW_GAP := 1.5          # how close behind Sandra she trots
const STAY_RELEASE := 10.0       # walk this far from a sitting Trufa and she gives up and goes home
const TROT_SPEED := 6.2          # top speed; a little faster than Sandra so she can catch up
const WALK_ANIM_SPEED := 1.5     # m/s at which the walk animation looks right at normal speed
const BESIDE := 0.85             # following: how far to Sandra's side she trots
const NUDGE := 0.6               # walking into her (once she knows Sandra) pushes her to this far away
const HOP := 0.45                # seconds to pounce into or jump out of the basket
const SEAT_FWD := 0.15         # metres forward of the basket's middle (round 24, the user: her tail hung out the back
                               # and there was room at the front; not so far that her chest meets the front)
const SEAT_DROP := 0.2           # metres her feet go below the basket's floor marker (round 23: lower, the user: "sit lower into the basket")
const WAIT_HOME := 30.0          # (round 23) seconds she waits outside a building before going home (once she knows it)
const REJOIN := 3.0              # Sandra this close to a waiting Trufa: she follows again
const RUN_UP := 1.2              # (round 23) at most this long running up to the bike before she pounces

var state := LOST
var main: Node3D                 # main.gd: player, ground height, physics
var body: Node3D                 # turns to face where she's going
var ap: AnimationPlayer
var walk_anim := ""
var skel: Skeleton3D
var pose: SkeletonModifier3D
var home_pos := Vector3.ZERO     # her spot beside Montse
var home_yaw := 0.0
var lost_pos := Vector3.ZERO
var trail: Array = []            # Sandra's footsteps since Trufa started following
var been: Array = []             # Trufa's own path since she left home, to find her way back
var speed := 0.0
var heading := 0.0
var sit := 0.0                   # 0 standing, 1 sitting
var wag := 0.0
var wag_amt := 0.4
var sniff := 0.0                 # 0 head up, 1 nose to the ground
var idle_t := 0.0
var wander := Vector3.ZERO
var rng := RandomNumberGenerator.new()
var dodge := Vector3.ZERO        # skipping out of Sandra's way: which way...
var dodge_t := 0.0               # ...and for how much longer
var side := 1.0                  # which side of Sandra she trots on (+1 her left, -1 her right)
var in_basket := 0.0             # 0 on the ground, 1 sitting in the bike's basket (between: hopping)
var basket_in := false           # hopping in / riding (true) or hopping out (false)
var hop_a := Vector3.ZERO        # where the hop started
var hop_b := Vector3.ZERO        # where a hop out lands
var wait_t := 0.0                # how long she has been waiting outside
var run_up := -1.0               # running up to the bike (seconds so far), before the pounce; -1 not running up


func setup(m: Node3D, scene: Node3D, at: Vector3, yaw: float, hip_height: float) -> void:
	main = m
	position = at
	lost_pos = at
	heading = yaw
	rng.seed = 7
	body = Node3D.new()
	add_child(body)
	body.add_child(scene)
	for mi in scene.find_children("*", "MeshInstance3D", true, false):
		if mi.skin == null:
			mi.visible = false               # Meshy's stray helper sphere
		# (round 23, the user: "Trufa stays very bright during the night") Meshy gave her model a glow texture at full
		# strength and a doubled shine: lit only by the light round her now, like everyone else
		var mesh: Mesh = (mi as MeshInstance3D).mesh
		if mesh:
			for i in mesh.get_surface_count():
				var sm := mesh.surface_get_material(i) as StandardMaterial3D
				if sm:
					var c := sm.duplicate() as StandardMaterial3D
					c.emission_enabled = false
					c.metallic_specular = 0.4
					(mi as MeshInstance3D).set_surface_override_material(i, c)
	var aps := scene.find_children("*", "AnimationPlayer", true, false)
	if aps.size() > 0:
		ap = aps[0]
		walk_anim = ap.get_animation_list()[0]
		ap.get_animation(walk_anim).loop_mode = Animation.LOOP_LINEAR
		ap.play(walk_anim)
	skel = scene.find_children("*", "Skeleton3D", true, false)[0]
	pose = SkeletonModifier3D.new()
	pose.set_script(load("res://engine/dog_pose.gd"))
	skel.add_child(pose)
	pose.setup()
	# size and facing: measured from the skeleton, so it doesn't matter how the file was exported
	var xf := scene.global_transform.affine_inverse() * skel.global_transform
	var hip_world: float = (xf.basis * (pose.up * pose.height)).length()
	scene.scale = Vector3.ONE * (hip_height / maxf(hip_world, 0.0001))
	var f: Vector3 = xf.basis * pose.fwd
	scene.rotation.y = -atan2(f.x, f.z)       # nose along +z, like the other characters
	# feet on the ground
	var paw: Vector3 = (skel.global_transform * skel.get_bone_global_rest(pose.b.backleg2)).origin
	scene.position.y -= paw.y - global_position.y


# ------------------------------------------------------------------ commands from the dialogue

func follow() -> void:
	if state != FOLLOW and state != STAY and state != LOST:
		been = [home_pos]
	elif state == LOST:
		been = [position]
	state = FOLLOW
	trail.clear()


func stay() -> void:
	state = STAY


func wait_outside() -> void:
	state = WAIT
	wait_t = 0.0


func go_home() -> void:
	state = GOING_HOME


func settle_home() -> void:
	state = HOME
	position = home_pos
	been.clear()


# ------------------------------------------------------------------ every frame

func tick(dt: float) -> void:
	var sandra: Vector3 = main.player.global_position
	# riding with her: in the basket (hopping in or out over HOP seconds)
	var bk: Node3D = main.street.riding
	var seat: Node3D = bk.dog_seat if bk and bk.dog_seat and bk.dog_seat.is_visible_in_tree() else null
	var ride := state == FOLLOW and seat != null
	if get_parent() != main.outdoor and not (ride and get_parent() == seat):
		# (off the bike: back into the world, where she was, facing the way she faced)
		var g := global_transform
		var face_dir: Vector3 = body.global_transform.basis.z
		get_parent().remove_child(self)
		main.outdoor.add_child(self)
		global_position = g.origin
		rotation = Vector3.ZERO
		heading = atan2(face_dir.x, face_dir.z)
	if not ride:
		run_up = -1.0
	if ride and not basket_in:
		# (round 23, the user: "she should run up and pounce like a dog should"): first she runs to just behind the
		# bike, legs going, then springs up into the basket
		if run_to_bike(seat, dt):
			return
		basket_in = true
		hop_a = position
	elif not ride and basket_in:
		basket_in = false
		hop_a = position
		var f := Vector3(main.move_dir.x, 0, main.move_dir.y)
		hop_b = sandra + f * 0.5 + Vector3(f.z, 0, -f.x) * side * BESIDE
		hop_b.y = main.ground_at(hop_b)
		trail.clear()
	if basket_in or in_basket > 0.0:
		in_basket = clampf(in_basket + (dt if basket_in else -dt) / HOP, 0.0, 1.0)
		basket_tick(seat, dt)
		return
	var want_speed := 0.0
	var target := position
	var sitting := false
	match state:
		LOST:
			idle_t -= dt
			if idle_t <= 0.0:
				wander = lost_pos + Vector3(rng.randf_range(-2.5, 2.5), 0, rng.randf_range(-2.5, 2.5))
				idle_t = rng.randf_range(2.5, 5.0)
			target = wander
			want_speed = 1.2 if position.distance_to(wander) > 0.3 else 0.0
			sniff = move_toward(sniff, 1.0 if want_speed > 0.0 else 0.6, dt * 2.0)
		FOLLOW:
			record_trail(sandra)
			# her place: beside Sandra, on whichever side she is already on
			var fwd := Vector3(main.move_dir.x, 0, main.move_dir.y)
			var left := Vector3(fwd.z, 0, -fwd.x)
			var rel := position - sandra
			if absf(rel.dot(left)) > 0.4:
				side = signf(rel.dot(left))
			var spot := sandra + left * side * BESIDE - fwd * 0.15
			target = follow_target(spot)
			var gap := flat(position.distance_to(spot))
			# Sandra's own pace, a little more while she is behind, so she catches up and then keeps alongside
			var pace: float = absf(main.speed)
			want_speed = clampf(pace + (gap - 0.25) * 2.0, 0.0, maxf(pace * 1.3, 2.5)) if gap > 0.25 else pace
			if gap < 0.6 and pace > 0.3:
				heading = lerp_angle(heading, atan2(fwd.x, fwd.z), 1.0 - exp(-6.0 * dt))
			sniff = move_toward(sniff, 0.0, dt * 3.0)
			record_been()
		STAY:
			sitting = true
			want_speed = 0.0
			face(sandra, dt)
			if flat(position.distance_to(sandra)) > STAY_RELEASE and main.game.m_done("dog"):
				state = GOING_HOME
		WAIT:
			sitting = true
			want_speed = 0.0
			wait_t += dt
			if main.where == "out":
				face(sandra, dt)
				if flat(position.distance_to(sandra)) < REJOIN:
					follow()
			if state == WAIT and wait_t > WAIT_HOME and main.game.m_done("dog"):
				state = GOING_HOME
		GOING_HOME:
			target = home_step()
			want_speed = 3.8
			sniff = move_toward(sniff, 0.0, dt * 3.0)
			if flat(position.distance_to(home_pos)) < 0.25:
				settle_home()
		HOME:
			sitting = true
			var to_home := flat(position.distance_to(home_pos))
			if to_home > 0.2:
				target = home_pos
				want_speed = 1.5
				sitting = false
			else:
				heading = lerp_angle(heading, home_yaw, 1.0 - exp(-3.0 * dt))
	# out of Sandra's way, if she's coming at her: shy, before Sandra knows her name (LOST)...
	var rel := position - sandra
	rel.y = 0.0
	var reach := 1.5 if main.street.riding else 1.0
	var nudged := 0.0
	if state != LOST:
		# ...after it, she's just nudged along (her legs walking) when Sandra walks into her
		if rel.length() < NUDGE and main.where == "out":
			var away := rel.normalized() if rel.length() > 0.01 else Vector3(sin(heading), 0, cos(heading))
			var push := (NUDGE - rel.length())
			position += away * push
			nudged = push / maxf(dt, 0.001)
	elif dodge_t <= 0.0 and absf(main.speed) > 0.8 and rel.length() < reach and main.where == "out":
		var md := Vector3(main.move_dir.x, 0, main.move_dir.y)
		if rel.dot(md) > -0.2:
			var side := Vector3(-md.z, 0, md.x)
			if rel.dot(side) < 0.0:
				side = -side
			dodge = (side + md * 0.4).normalized()
			dodge_t = 0.5
	# move
	speed = move_toward(speed, want_speed, (14.0 if want_speed > speed else 18.0) * dt)
	var to := target - position
	to.y = 0.0
	if dodge_t > 0.0:
		dodge_t -= dt
		sitting = false
		speed = maxf(speed, 3.5)
		heading = lerp_angle(heading, atan2(dodge.x, dodge.z), 1.0 - exp(-14.0 * dt))
		position += dodge * 3.8 * dt
	elif to.length() > 0.05 and speed > 0.05:
		var dir := to.normalized()
		heading = lerp_angle(heading, atan2(dir.x, dir.z), 1.0 - exp(-10.0 * dt))
		var step := minf(speed * dt, to.length())
		position += Vector3(sin(heading), 0, cos(heading)) * step
	position.y = lerpf(position.y, main.ground_at(position), 1.0 - exp(-14.0 * dt))
	# animate
	if nudged > 0.2:
		sitting = false
		speed = maxf(speed, minf(nudged, 3.0))
	sit = move_toward(sit, 1.0 if (sitting and speed < 0.2) else 0.0, dt * 3.0)
	body.rotation.y = heading
	if ap:
		ap.speed_scale = clampf(speed / WALK_ANIM_SPEED, 0.0, 3.6)   # her legs keep up, even at Sandra's pace
	pose.still = move_toward(pose.still, 0.0 if speed > 0.15 else 1.0, dt * 4.0)
	pose.sit = sit
	pose.leap = 0.0
	pose.pitch = 0.0
	pose.grounded = true
	var happy := state == FOLLOW or (state == STAY and flat(position.distance_to(sandra)) < 3.0)
	wag_amt = lerpf(wag_amt, 0.7 if happy else 0.3, 1.0 - exp(-2.0 * dt))
	wag += dt * (14.0 if happy else 6.0)
	pose.wag = sin(wag) * wag_amt
	pose.sniff = sniff * (1.0 - sit)


func flat(d: float) -> float:
	return d


func face(p: Vector3, dt: float) -> void:
	var to := p - position
	heading = lerp_angle(heading, atan2(to.x, to.z), 1.0 - exp(-3.0 * dt))


func record_trail(sandra: Vector3) -> void:
	if trail.is_empty() or trail[-1].distance_to(sandra) > 0.4:
		trail.append(sandra)
	while trail.size() > 300:
		trail.pop_front()


func record_been() -> void:
	if been.is_empty() or been[-1].distance_to(position) > 0.5:
		been.append(position)
	while been.size() > 800:
		been.pop_front()


func clear_line(a: Vector3, b: Vector3) -> bool:
	var q := PhysicsRayQueryParameters3D.create(a + Vector3(0, 0.45, 0), b + Vector3(0, 0.45, 0), main.LAYER_BODY)
	return get_world_3d().direct_space_state.intersect_ray(q).is_empty()


func follow_target(sandra: Vector3) -> Vector3:
	# straight for her when the way is clear, otherwise along the way she walked
	if clear_line(position, sandra):
		while trail.size() > 1 and trail[0].distance_to(sandra) > 1.0:
			trail.pop_front()
		return sandra
	while trail.size() > 1 and position.distance_to(trail[0]) < 0.5:
		trail.pop_front()
	return trail[0] if not trail.is_empty() else sandra


func home_step() -> Vector3:
	if clear_line(position, home_pos):
		return home_pos
	# the furthest-back point on her own path that she can see from here
	var n := been.size()
	var stride := maxi(1, n / 40)
	for i in range(0, n, stride):
		if clear_line(position, been[i]):
			while been.size() > i + 1:
				been.pop_back()
			return been[i]
	return been[-1] if n > 0 else home_pos


func run_to_bike(seat: Node3D, dt: float) -> bool:
	# running up behind the bike; true while still on her way, false once it is time to jump
	if run_up < 0.0:
		run_up = 0.0
	run_up += dt
	var back: Vector3 = main.street.riding.global_transform.basis.z           # (the bike's nose is its -z)
	back.y = 0.0
	var launch: Vector3 = seat.global_position + back.normalized() * 0.8
	var to := launch - position
	to.y = 0.0
	if to.length() < 0.5 or run_up > 4.0:
		run_up = -1.0
		return false
	var dir := to.normalized()
	heading = lerp_angle(heading, atan2(dir.x, dir.z), 1.0 - exp(-12.0 * dt))
	speed = move_toward(speed, maxf(TROT_SPEED * 1.25, absf(main.speed) * 1.3), 20.0 * dt)
	position += dir * minf(speed * dt, to.length())
	position.y = lerpf(position.y, main.ground_at(position), 1.0 - exp(-14.0 * dt))
	body.rotation.y = heading
	if ap:
		ap.speed_scale = clampf(speed / WALK_ANIM_SPEED, 0.0, 3.6)
	sit = move_toward(sit, 0.0, dt * 6.0)
	pose.sit = sit
	pose.still = 0.0
	pose.leap = 0.0
	pose.pitch = 0.0
	wag += dt * 14.0
	pose.wag = sin(wag) * 0.5
	pose.sniff = 0.0
	return true


func basket_tick(seat: Node3D, dt: float) -> void:
	# sitting up in the bike's basket, facing where the bike goes; or hopping in from where she stood, or out
	# to the ground beside Sandra
	if basket_in and seat and in_basket >= 1.0:
		# riding: she goes with the basket itself (it turns with the handlebars), so she never lags behind it
		if get_parent() != seat:
			get_parent().remove_child(self)
			seat.add_child(self)
			transform = Transform3D(Basis(), Vector3(0, -SEAT_DROP, -SEAT_FWD))     # (the bike's nose is its -z)
			heading = PI
		body.rotation.y = PI
		sit = move_toward(sit, 1.0, dt * 6.0)
		pose.sit = sit
		pose.still = 1.0
		pose.leap = 0.0
		pose.pitch = 0.0
		pose.grounded = false
		pose.wag = move_toward(pose.wag, 0.0, dt * 3.0)       # (round 23, the user: no wagging in the basket)
		return
	var t := smoothstep(0.0, 1.0, in_basket if basket_in else 1.0 - in_basket)
	var end: Vector3 = hop_b
	if basket_in and seat:
		# (sitting, her rump stays at hip height and her body leans back: down and forward a little, so she sits
		# in the basket rather than on it)
		var fw: Vector3 = -main.street.riding.global_transform.basis.z
		end = seat.global_position + Vector3(0, -SEAT_DROP, 0) + fw * SEAT_FWD
	position = hop_a.lerp(end, t) + Vector3(0, sin(t * PI) * (0.35 if basket_in else 0.2), 0)
	pose.grounded = false
	# the pounce: front legs reach forward and the back legs push out behind, nose up as she rises, down as she lands
	pose.leap = sin(t * PI)
	pose.pitch = cos(t * PI) * 0.35
	if basket_in and seat:
		var nose: Vector3 = -main.street.riding.global_transform.basis.z
		heading = lerp_angle(heading, atan2(nose.x, nose.z), 1.0 - exp(-12.0 * dt))
	speed = 0.0
	sit = move_toward(sit, 1.0 if basket_in else 0.0, dt * 6.0)
	body.rotation.y = heading
	if ap:
		ap.speed_scale = 0.0
	pose.still = 1.0
	pose.sit = sit
	pose.wag = move_toward(pose.wag, 0.0, dt * 3.0)
	pose.sniff = 0.0
