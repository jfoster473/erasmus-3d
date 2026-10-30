# One bicycle (bigfiles/built/props/bicycle.glb), with its own colours and extras.
# Parked, it stands on its kickstand, leaning a little. Ridden, the wheels roll, the pedals
# turn and the handlebars follow the steering; main.gd seats Sandra on it.
extends Node3D

const WHEEL_R := 0.25            # tyre radius (build_props.py: WR + TR)
# Pedalling: a relaxed cadence that rises only a little with speed (the gears do the rest), about
# 30 turns a minute pulling away and 70 at full speed; the pedals stop when she freewheels.
const CADENCE_SLOW := 0.5        # turns a second
const CADENCE_FAST := 1.15

var root: Node3D
var front: Node3D
var rear: Node3D
var cranks: Node3D
var steering: Node3D
var dog_seat: Node3D             # where Trufa sits in the dog basket (Sandra's own bike only shows it)
var seat: Node3D
var grip_l: Node3D
var grip_r: Node3D
var pedal_l: Node3D
var pedal_r: Node3D
var foot_l: Node3D               # where her ankles go: just above and behind each pedal, kept level
var foot_r: Node3D
var hand_l: Node3D               # where her wrists go: just behind and above each grip
var hand_r: Node3D
var cadence := 0.0
var spin := 0.0
var pedal := 0.0
var steer := 0.0
var lean := 0.0
var ridden := false
var parked_yaw := 0.0


# variant: {"frame": Color, "guard": Color, "saddle": Color, "basket": bool, "flowers": bool, "rack": bool}
func setup(scene: Node3D, variant: Dictionary) -> void:
	root = scene
	add_child(root)
	front = root.find_child("FrontWheel", true, false)
	rear = root.find_child("RearWheel", true, false)
	cranks = root.find_child("Cranks", true, false)
	steering = root.find_child("Steering", true, false)
	seat = root.find_child("SeatPoint", true, false)
	grip_l = root.find_child("GripL", true, false)
	grip_r = root.find_child("GripR", true, false)
	pedal_l = root.find_child("PedalL", true, false)
	pedal_r = root.find_child("PedalR", true, false)
	foot_l = target(pedal_l, Vector3(0, 0.1, 0.035))
	foot_r = target(pedal_r, Vector3(0, 0.1, 0.035))
	hand_l = target(grip_l, Vector3(0, 0.025, 0.035))
	hand_r = target(grip_r, Vector3(0, 0.025, 0.035))
	var colours := {"BikeFrame": variant.get("frame"), "BikeGuard": variant.get("guard"), "BikeSaddle": variant.get("saddle"),
		"BikeBasket": variant.get("wicker")}
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		for i in mi.mesh.get_surface_count():
			var m = mi.mesh.surface_get_material(i)
			if m and colours.get(m.resource_name) != null:
				var c: StandardMaterial3D = m.duplicate()
				c.albedo_color = colours[m.resource_name]
				mi.set_surface_override_material(i, c)
	for part in [["Basket", "basket"], ["BasketFlowers", "flowers"], ["Rack", "rack"]]:
		var n := root.find_child(part[0], true, false)
		if n:
			n.visible = variant.get(part[1], true)
	var bf := root.find_child("BasketFlowers", true, false)
	if bf and not variant.get("basket", true):
		bf.visible = false
	# Sandra's own bike (round 22): the dog-sized basket Trufa rides in, instead of the small one
	var dog_basket: bool = variant.get("dog_basket", false)
	var db := root.find_child("DogBasket", true, false)
	if db:
		db.visible = dog_basket
	if dog_basket:
		for nm in ["Basket", "BasketFlowers"]:
			var n := root.find_child(nm, true, false)
			if n:
				n.visible = false
	dog_seat = root.find_child("DogSeat", true, false)
	park()


func target(parent: Node3D, at: Vector3) -> Node3D:
	# (the bike points along -z, so +z is backwards)
	var n := Node3D.new()
	if parent:
		parent.add_child(n)
		n.position = at
	return n


func park() -> void:
	ridden = false
	steer = 0.25                 # parked bikes have their front wheel turned a little
	lean = 0.12
	apply()


func tick(dt: float, speed: float, bars: float, pedalling: bool) -> void:
	# speed in m/s along the bike; bars: how far the handlebars are turned (radians, + to the right)
	spin += speed / WHEEL_R * dt
	var want := lerpf(CADENCE_SLOW, CADENCE_FAST, clampf(speed / 9.0, 0.0, 1.0)) * TAU if pedalling else 0.0
	cadence = lerpf(cadence, want, 1.0 - exp(-5.0 * dt))
	pedal += cadence * dt
	steer = lerpf(steer, clampf(bars, -0.45, 0.45), 1.0 - exp(-10.0 * dt))
	lean = lerpf(lean, 0.0, 1.0 - exp(-6.0 * dt))      # the rider's whole body leans the bike into turns
	apply()


func apply() -> void:
	# the bike faces -z: rolling forward is a negative turn about x
	if rear:
		rear.rotation.x = -spin
	if front:
		front.rotation.x = -spin
	if cranks:
		cranks.rotation.x = -pedal
		for p in [pedal_l, pedal_r]:
			if p:
				p.rotation.x = pedal        # pedals stay level as the cranks go round
	if steering:
		# turn about the head tube, which leans back towards the rider
		steering.basis = Basis(Vector3(0, 0.965, 0.263).normalized(), steer)
	root.rotation.z = lean
