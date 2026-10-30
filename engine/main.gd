# Flor de Lliri — Godot vertical slice.
# Loads the shared Blender assets and scene.json, then builds physics, a third-person
# character controller, a follow camera, video-style lighting, wind in the foliage,
# the door into Sandra's flat, and Rosa inside.
#
# Run:  Godot --path godot                          (play)
#       Godot --path godot -- --shots=<folder>      (scripted screenshots, then quit)
extends Node3D

# ---- movement feel (see "Controls" in ../README.md) ----
const SPEED := 5.0               # one easy pace; there is no separate run
const ACCEL := 13.0              # m/s² towards full speed: quick but not instant
const DECEL := 16.0
const TURN_RATE := 7.0           # rad/s: turning round to where the keys point (setting off, about-turns, indoors)
const MODEL_TURN := 12.0         # how fast the body catches up with the direction of travel
const GRAVITY := 20.0

# ---- camera feel ----
const CAM_DIST := 5.0             # (round 40, the user: "move the camera a little bit further back from her"; was 4.3)
const CAM_PIVOT_H := 1.4
const CAM_PITCH := -0.30          # (round 27, the user: the horizon 23% from the top of the screen)
const CAM_FOV_OUT := 65.0         # (round 38, the user: "I want the world to be a bit wider when she's running around.
								  # Ever so slightly": 62 degrees in the great rooms, 65 outside)
const MOUSE_SENS := 0.0026
const PAD_SENS := 2.8
const RECENTER_DELAY := 1.8      # seconds after the player last turned the camera
const RECENTER_RATE := 1.3
const SWING_MAX := 1.5           # rad/s: the fastest the camera swings round behind her
const CATCH_UP := 2.4            # how much faster it swings when she's just going forwards
# Steering while she runs (steer_walk): left and right turn her, biting straight away and turning
# faster the longer they are held; the turn starts and stops smoothly, never past where it was going
const STEER_BITE := 1.2          # rad/s at once...
const STEER_GROW := 0.6          # ...plus this much for every second the key is held, slowly stronger...
const STEER_MAX := 3.0           # ...up to this, after three seconds (a 3.3 m circle at full pace)
const STEER_QUICK := 3.6         # (rounds 27–28, the user) just after setting off, a side key bites this hard instead,
const QUICK_HOLD := 0.9          # staying that sharp for the first stretch of a run (narrow places)...
const QUICK_FOR := 1.1           # ...then fading back to STEER_BITE over this many seconds
const STEER_EASE := 16.0         # rad/s²: how quickly a turn comes on and dies away
const ROOM_STEER := [3.0, 2.0, 5.0]   # in the basilica, among the columns: bite, growth and most, much sharper
const CAM_ACCEL := 2.6           # rad/s²: the camera's swing speeds up and slows down gently (no jolts)

const INTERIOR_OFFSET := Vector3(400, 0, 0)
# Meshy characters come out of rigging at different sizes; this puts them at the right height next to Sandra
const MODEL_SCALE := {"man.glb": 1.25, "man2.glb": 1.25, "oldman.glb": 1.2, "woman.glb": 1.2, "child.glb": 1.1,
	"workman.glb": 1.17, "man3.glb": 1.12, "woman2.glb": 1.02, "oldlady.glb": 0.94}
# (round 37: the workman's 1.70 m takes in his helmet; his body stands as tall as man2's. The new three: the young man
# 1.77 m, a little taller than the rest, as the user wanted then (1.81 m was "way too tall", 1.62 m the smallest adult);
# the young woman as tall as the other (1.74 m), the old lady as Montse (1.6 m))
# (round 39, the user, of the young man in the navy polo: "should be taller. Maybe a head taller than Sandra… he looks
# too small compared to the other characters" — his grown-up head is small beside the others' big ones) 2.26 m: his
# chin level with the top of Sandra's hair (she is 1.70 m, her head 0.6 m of it; the other men 1.74–1.81 m)
const ROSA_MODEL := "sandra_b.glb"
const ROSA_LOOK := [   # see character.gdshader: hair near-black, top sage green, jeans dark grey
	{"hue": [330, 40], "sat": [0.42, 1.0], "val": [0.0, 0.36], "h": [0.62, 2.0], "col": "#2a1c16", "ref": 0.16},
	{"hue": [0, 360], "sat": [0.0, 0.14], "val": [0.6, 1.0], "h": [0.42, 1.0], "col": "#6f9f7a", "ref": 0.85},
	{"hue": [180, 240], "sat": [0.2, 1.0], "val": [0.0, 1.0], "h": [0.05, 0.55], "col": "#3c3b45", "ref": 0.3}]
const R := 0.3
const ARM_K := 0.72               # (round 41) Sandra's arms: the length of her upper arms and forearms (the user chose C: 28% shorter)
const LAYER_BODY := 1
const LAYER_CAMERA := 2          # what the camera arm collides with (walls, not trees)
const LAYER_NOBIKE := 4          # where the bike can't go (the beach's sand, the rope round the thick of the wood): only while riding

var world_name := "barcelona"     # (the world the game plays: project.godot's erasmus/world; its files under worlds/<name>/)
var world_dir: String              # worlds/<name>/, on disk
var big_dir: String                # bigfiles/, on disk: the big files kept off GitHub (asset_path, out_dir)
var out_dir: String                # what its build made: scene.json, city.glb, interior.glb, light maps (bigfiles/built/<name>/)
var data_dir: String               # its data: data3d.json (people, missions, items, rooms…)
var D: Dictionary
var outdoor: Node3D
var indoor: Node3D
var world_env: WorldEnvironment
var env_out: Environment
var env_in: Environment
var sky_mat: ProceduralSkyMaterial
var night_sky: ShaderMaterial
var sky: Sky
var sun: DirectionalLight3D
var bounce: DirectionalLight3D   # warm light thrown back by the sunlit façades
var lamp_lights: Array = []
var lamp_glass_mat: ShaderMaterial  # the street lamps, their lanterns' glass glowing after dark (lamp_glass())
var lamp_mat: StandardMaterial3D    # (the lamps' own material, which carries it as its next pass after dark)
var door_light: OmniLight3D
var door_glows: Array = []       # the glow round each door Sandra can go in by
var sun_beams: Array = []            # shafts of sunlight through the Sagrada Família's glass: {mat, spot, side, k}            # the buildings' names over their doors, like the 2D game's map labels
var ceiling_lights: Array = []
var window_lights: Array = []
var room_lamps: Array = []
var mats := {}
var foliage_shader: Shader
var foliage_mats := {}
# (round 25) the woods' leaves cast shadows only this near Sandra (metres; 0: no limit, as before): the user to pick
# from round25/leaf_shadow_*.png. Whole chunks of leaves further off than that cast none at all (the saving); within,
# foliage.gdshader stops at the exact distance, feathered.
var LEAF_SHADOW_R := 0.0
var leaf_casters: Array = []        # [MeshInstance3D, its ground-plane rect (x0, z0, x1, z1)]
var leaf_shadow_t := 0.0
var leaf_shadow_last := 0.0
var crown_shader: Shader

var player: CharacterBody3D
var model: Node3D                # turns and leans; holds the character mesh
var skins: Array = []           # Meshy Sandras the player can switch between with C
var skin_idx := 0
var char_shader: Shader
var hair_offset := Vector3.ZERO
var ambience: Node
var street: Node                 # Montse, Trufa and the bicycles (street_life.gd)
var people: Node                 # passers-by (people.gd)
var npcs: Node                   # the 2D game's people (npcs.gd)
var wildlife: Node               # pigeons, butterflies, fireflies, gulls (wildlife.gd)
var touches: Node                # the party's decorations, Alba's vase, the cats (touches.gd)
var benches: Node                # (round 41) every bench: solid, and she sits on it (benches.gd)
var game: Node                   # the 2D game's state, missions and talk (game.gd)
var room := ""                   # the interior Sandra is in
var room_door: Dictionary = {}   # the entrance she came in by
var room_nodes := {}             # interior id -> its node in interior.glb
var room_lights := {}            # interior id -> a node holding its lights
var ground_cells := {}           # 10 m cells -> what raises the ground there (pavements, the bridge, steps)
var boost := 0.0                 # seconds of extra pace after eating something (BOOST_K)
const BOOST_K := 1.25            # (round 41, the user: "The food speed should be 25% and should also apply to the bike"; was +30%, walking only)
var boost_id := ""               # what she ate (its picture on the little card, bottom left)
var boost_panel: PanelContainer
var boost_icon: TextureRect
var boost_name: Label
var boost_left: Label
var guard_t := -99.0
var door_said_t := -99.0         # (when a locked door last told her so, walked at)
var turn_now := 0.0              # how fast Sandra's direction of travel is swinging (rad/s)
var stride := 0.0
var prev_vel := Vector3.ZERO
const MOVE_ANIM_SPEED := 4.0    # m/s at which the moving animation looks right at normal playback

var cam_root: Node3D
var cam_yaw_node: Node3D
var cam_pitch_node: Node3D
var arm: SpringArm3D
var cam: Camera3D
var room_cam: Camera3D

var where := "out"
var busy := false
var cutscene := false            # a scene plays (the exam, round 22): she is posed by it, nothing moves her
var ride_cam := false            # (round 22) riding the wheel or the funicular: the camera still follows, she can look round
var ride_look := false           # (round 26, the user) E in the cabin: her own eyes, looking out over the city
var ride_inside := false         # (round 41, 03 #28a) riding hidden inside (the funicular): the camera follows the car, no E
var seat_eye := -1.0             # (round 41) seated (the wheel's bench): her eyes' height over where she sits; -1 standing
const SEAT_LEAN := 0.55          # (round 41) looking out, seated: how far her eyes lean out towards the rim (the tub's inside is 0.9)
var seat_lean := SEAT_LEAN       # (round 41: on a bench, only a little)
var north: Node                  # the north's rides, gates and hillside (north.gd)
var entered_at := 0.0
var move_dir := Vector2(0, -1)
var speed := 0.0
var last_manual_cam := -99.0
var look_ahead := Vector3.ZERO
var cam_slide := Vector3.ZERO      # where the camera's pivot still lags her by after she steps off the bike (eases to nothing)
var lean := 0.0
const IDLE_TILT := 0.2           # posture.gd's correction when standing (faded to 0 as she walks)
var face_target := INF           # yaw Sandra turns to while talking
var keys := Vector2.ZERO         # the movement keys this frame (x right, y forward)
var prev_keys := Vector2.ZERO
var side_held := 0.0             # seconds a side key has been held (while it is steering her)
var debug_fast := false          # the debug menu's quick walking
var keys_held := 0.0             # seconds the movement keys have been held without a break
var back_dir := Vector2.ZERO     # turning round to run back towards the camera: the way she's turning to
var swing := 0.0                 # 0..1, eases the camera swing in
var turn_vel := 0.0              # rad/s her direction of travel is turning at
var side_first := false          # (round 27) a side key held from before forward: its steering is ignored until re-pressed
var cam_vel := 0.0               # rad/s the camera is swinging at
var bike_body: Array = []        # the bike's wheels, as extra collision shapes while she rides
var bike_pedalling := false
var bike_steer := 0.0            # -1..1: how far she is leaning the bike into a turn (+ right)
var swing_sign := 0.0            # which way round it is swinging (so it doesn't dither when exactly in front)
var vkeys := {}
var touch_on: bool = DisplayServer.is_touchscreen_available() or "--touch" in OS.get_cmdline_user_args()
var touch_pad: Control            # the on-screen controls on a touch screen (touch.gd), else null
var preset := "golden"
var clock_light := true          # the light follows the game clock (tests set a fixed look instead)
var light_t := 0.0
var high_quality := true
var P: Dictionary
var sun_dir := Vector3.UP
var t := 0.0

var banner_panel: PanelContainer
var banner: Label
var banner_timer := 0.0
var last_banner := ""
var stats: Label
var help: Label
var prompt: Label
var hud: Label                   # the current mission (top left)
var hud_root: Control            # the mission, the clock and the money together (hidden on the title screen)
var mission_panel: PanelContainer
var clock_panel: PanelContainer
var clock_label: Label           # bottom left
var money_panel: PanelContainer
var money_label: Label           # bottom right
var toast_label: Label
var toasts: Array = []
var toast_t := 0.0
var dlg_panel: PanelContainer
var dlg_who: Label
var dlg_text: Label
var dlg_pages: Array = []
var dlg_open := false
var panels: CanvasLayer          # the backpack and shop counter (panels.gd)
var dlg_choices: Array = []      # options offered after the last page
var dlg_choice := 0
var dlg_on_choice: Callable      # called with the chosen index
var dlg_on_close: Callable       # called when a dialogue without choices ends
var choice_box: VBoxContainer
var fade: ColorRect
var map_panel: Control            # Tab: the 2D game's map, with Sandra on it
var map_tex: TextureRect
var map_dot: Panel
var map_meta: Dictionary = {}     # map/world.json: where the map picture's edges are in the world
var map_labels: Array = []        # {node, spots, rot, kind, dot}: the names written on the map
var map_legend: PanelContainer
var map_dots: Array = []          # {node, pos}: a dot at every door that can be gone in by (round 19)
const DOT_COLS := {"landmark": Color("#c46a45"), "shop": Color("#2f7fa8"), "flat": Color("#3f6b52"), "other": Color("#6a5a4a")}

const PRESETS := {
	# the looks of the day, blended by the clock (LOOK_KEYS); where the sun (or moon) stands is worked out
	# from the clock separately (sky_positions). "fill": the light in the shade, mixed with the sky's blue by
	# "sky_mix"; "nk": how much of the night there is (lamps, lit windows, stars, the moon)
	"golden": {"sun": Color(1.0, 0.8, 0.56), "sun_e": 2.3,
		"top": Color(0.3, 0.52, 0.82), "hor": Color(1.0, 0.88, 0.68), "amb": 1.05, "nk": 0.0, "shafts": 0.003,
		"fill": Color(0.98, 0.84, 0.72), "sky_mix": 0.45, "exposure": 1.0, "glow_from": 1.0, "glow": Color(0.55, 0.32, 0.12)},
	# midday: the sun high and strong, but toned down so the pale stucco and stone don't glare
	"day": {"sun": Color(1.0, 0.96, 0.9), "sun_e": 1.7,
		"top": Color(0.28, 0.5, 0.86), "hor": Color(0.76, 0.85, 0.94), "amb": 0.8, "nk": 0.0, "shafts": 0.0012,
		"fill": Color(0.92, 0.88, 0.84), "sky_mix": 0.5, "exposure": 0.9, "glow_from": 1.4, "glow": Color(0.18, 0.14, 0.08)},
	# sunrise and sunset: the half hour when the low sun turns orange and amber, between the golden hour and
	# night. Kept orange, not rose: a pink sun on pink stucco under a violet sky read as magenta (round 19)
	"red": {"sun": Color(1.0, 0.6, 0.3), "sun_e": 1.6,
		"top": Color(0.16, 0.36, 0.62), "hor": Color(1.0, 0.74, 0.42), "amb": 0.62, "nk": 0.35, "shafts": 0.004,
		"fill": Color(0.74, 0.72, 0.76), "sky_mix": 0.35, "exposure": 1.0, "glow_from": 1.0, "glow": Color(0.95, 0.46, 0.12)},
	# a full moon: dark, but everything can still be seen; the lamps and windows keep it warm
	"night": {"sun": Color(0.7, 0.78, 1.0), "sun_e": 0.24,
		"top": Color(0.02, 0.04, 0.09), "hor": Color(0.07, 0.1, 0.17), "amb": 0.22, "nk": 1.0, "shafts": 0.002,
		"fill": Color(0.42, 0.5, 0.76), "sky_mix": 0.0, "exposure": 1.0, "glow_from": 1.0, "glow": Color(0.32, 0.2, 0.15)},
}
const ORDER := ["golden", "day", "night"]
# the day: night until six; from six to seven it goes red and then golden (sunrise is half past six); the
# golden morning turns to day by nine; a golden evening from seven; from nine to ten red, then night.
# (minute of the day, look); the light is blended smoothly between them
const LOOK_KEYS := [[0, "night"], [360, "night"], [390, "red"], [420, "golden"], [540, "day"], [1140, "day"],
	[1260, "golden"], [1290, "red"], [1320, "night"], [1440, "night"]]
const SUNRISE := 390.0           # 06:30
const SHADOW_OPACITY := 0.8      # the sun's shadows by day: how dark (1 = fully; round 21: lighter)
const SUN_SIZE := 0.4            # degrees: the sun's size, which softens the shadows' edges (0 = razor sharp; 1.6 smeared the crowns' shadows away)
const SHADOW_BLUR := 3.0         # and a little extra softening all round
const MOON_SHADOW := 0.55        # the moon's shadows: this much of the sun's darkness...
const MOON_SOFT := 1.2           # ...with softer edges (degrees)...
const MOON_BLUR := 4.5           # ...and softened all round
var shadow_day := SHADOW_OPACITY
var sun_size := SUN_SIZE
var shadow_blur := SHADOW_BLUR
const SUNSET := 1290.0           # 21:30
const PRESET_TIME := {"golden": 1230.0, "day": 780.0, "night": 1410.0, "red": 1290.0}
const T_STOPS := [420, 720, 1230, 1335]   # T moves the clock on to the next of these: morning, midday, evening, night


func _ready() -> void:
	world_name = String(ProjectSettings.get_setting("erasmus/world", "barcelona"))
	world_dir = ProjectSettings.globalize_path(world_res(""))
	big_dir = ProjectSettings.globalize_path("res://bigfiles")
	out_dir = big_dir.path_join("built").path_join(world_name)
	data_dir = world_dir.path_join("data")
	D = JSON.parse_string(FileAccess.get_file_as_string(out_dir.path_join("scene.json")))
	get_viewport().msaa_3d = Viewport.MSAA_2X
	foliage_shader = load("res://shaders/foliage.gdshader")
	crown_shader = Shader.new()
	crown_shader.code = foliage_shader.code.replace("render_mode cull_disabled, diffuse_burley;", "render_mode cull_disabled, diffuse_burley, shadows_disabled;\n#define CROWN")

	outdoor = Node3D.new()
	add_child(outdoor)
	indoor = Node3D.new()
	indoor.position = INTERIOR_OFFSET
	indoor.visible = false
	add_child(indoor)

	var city := load_glb("city.glb")
	outdoor.add_child(city)
	# every room of the 2D game, side by side (interiors.py); only the one Sandra is in is shown
	var rooms := load_glb("interior.glb")
	indoor.add_child(rooms)
	collect(city)
	collect(rooms)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--fartone="):
			var v := a.trim_prefix("--fartone=").split(",")
			FAR_LEAF_TONE = Vector3(float(v[0]), float(v[1]), float(v[2]))
	prepare_city(city)
	if "--interp" in OS.get_cmdline_user_args():
		get_tree().physics_interpolation = true
	if not "--noocclude" in OS.get_cmdline_user_args():     # (rule 02 #5f, the user's pick; tests: --noocclude)
		add_block_occluders()
	forest_floor(city)
	lamp_glass(city)
	for n in rooms.find_children("Ceiling_*", "MeshInstance3D", true, false):
		n.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
	for n in rooms.find_children("Interior_*", "", true, false):
		room_nodes[String(n.name).trim_prefix("Interior_")] = n
		n.visible = false
	char_shader = load("res://shaders/character.gdshader")

	ambience = Node.new()
	ambience.set_script(load("res://engine/ambience.gd"))
	add_child(ambience)
	build_ground_cells()
	build_physics()
	build_player()
	build_camera()
	setup_lights()
	build_door_glows()
	# the 2D game: its state, missions and talk (game.gd), and its people (npcs.gd)
	var data2d = JSON.parse_string(FileAccess.get_file_as_string(data_dir.path_join("data3d.json")))
	npcs = Node.new()
	npcs.set_script(load("res://engine/npcs.gd"))
	add_child(npcs)
	game = Node.new()
	game.set_script(load(world_res("game/story.gd")))     # (the world's story, extending the engine's rules)
	add_child(game)
	game.setup(self, data2d)
	panels = CanvasLayer.new()
	panels.set_script(load("res://engine/panels.gd"))
	add_child(panels)
	panels.setup(self)
	npcs.setup(self, data2d)
	game.restore_scenes()
	street = Node.new()
	street.set_script(load("res://engine/street_life.gd"))
	add_child(street)
	street.setup(self)
	people = Node.new()
	people.set_script(load("res://engine/people.gd"))
	add_child(people)
	people.setup(self)
	wildlife = Node.new()
	wildlife.set_script(load("res://engine/wildlife.gd"))
	add_child(wildlife)
	wildlife.setup(self)
	touches = Node.new()
	touches.set_script(load(world_res("game/touches.gd")))
	add_child(touches)
	touches.setup(self)
	benches = Node.new()
	benches.set_script(load("res://engine/benches.gd"))
	add_child(benches)
	benches.setup(self)
	north = Node.new()
	north.set_script(load(world_res("game/north.gd")))
	add_child(north)
	north.setup(self)
	make_ui()
	# on a phone or tablet (or with --touch, or from the debug menu, to try it with the mouse): the on-screen pad
	# and buttons (touch.gd)
	if touch_on:
		set_touch(true)
	light_from_clock()
	set_quality(false)                         # start smooth; Q switches to the full look
	load_render_scale()
	if testing:                                        # (not under the title: rule 08 #82d)
		show_banner(street_name(player.global_position))

	var args := OS.get_cmdline_user_args()
	if "--high" in args:
		set_quality(true)
	dress_sandra()
	if not testing:                                    # (no test run: with nothing, or only --touch)
		title_screen()
	else:
		ambience.call_deferred("begin", false)
		# scripted test runs (tests.gd)
		var tests := Node.new()
		tests.set_script(load(world_res("tests/tests.gd")))
		add_child(tests)
		tests.start(self, args)


# ------------------------------------------------------------------ assets

func add_block_occluders() -> void:
	# (round 41, the frame-rate review, rule 02 #5f: the user picked it) the city's blocks are solid: two crossed boxes inside each
	# block's walls tell the graphics card not to draw what is wholly hidden behind them (the next streets over).
	# Sandra's block is left out: its passage leads into her garden.
	var home := Vector2(float(D.door.pos[0]), float(D.door.pos[1]) - 3.0)
	for b in D.blocks:
		var poly := PackedVector2Array()
		for p in b.poly:
			poly.append(Vector2(float(p[0]), float(p[1])))
		if Geometry2D.is_point_in_polygon(home, poly):
			continue
		var lo := poly[0]
		var hi := poly[0]
		for p in poly:
			lo = lo.min(p)
			hi = hi.max(p)
		var cut := absf(poly[1].x - poly[2].x) + 0.6          # the chamfered corners, and a little in from the walls
		if not block_solid(b):
			continue
		for r in [Rect2(lo.x + 0.6, lo.y + cut, hi.x - lo.x - 1.2, hi.y - lo.y - 2.0 * cut),
				Rect2(lo.x + cut, lo.y + 0.6, hi.x - lo.x - 2.0 * cut, hi.y - lo.y - 1.2)]:
			var oc := OccluderInstance3D.new()
			var bx := BoxOccluder3D.new()
			bx.size = Vector3(r.size.x, 12.0, r.size.y)
			oc.occluder = bx
			outdoor.add_child(oc)
			oc.position = Vector3(r.get_center().x, 6.0, r.get_center().y)
	get_viewport().use_occlusion_culling = true


func block_solid(blk: Dictionary) -> bool:
	# (round 41c, the user: "none of the scenery is there anymore", on the MNAC's terrace, then in the Ciutadella) a
	# block's boxes only where she can never be: a block that is wall all through. One she can go into — a landmark on
	# its own square, a park, a courtyard — lists its own walls ('solids'; the whole block when it has none), and gets
	# none: with the camera inside a box, everything round about went (only the shadows stayed), and the doors set
	# back inside one lost their glow
	return not blk.has("solids") and not blk.has("court")


func asset_path(file: String) -> String:
	# the models every world shares: "meshy/…" bought from Meshy (bigfiles/originals/), "props/…" made by the build (bigfiles/built/)
	return big_dir.path_join(("originals/" if file.begins_with("meshy/") else "built/") + file)


func load_glb(file: String) -> Node3D:
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	var err := doc.append_from_file(asset_path(file) if file.begins_with("meshy/") or file.begins_with("props/") else out_dir.path_join(file), st)
	if err != OK:
		push_error("Could not load " + file)
	return doc.generate_scene(st) as Node3D


func collect(n: Node) -> void:
	if n is MeshInstance3D and n.mesh:
		for i in n.mesh.get_surface_count():
			var m = n.mesh.surface_get_material(i)
			if m is StandardMaterial3D:
				if not mats.has(m.resource_name):
					mats[m.resource_name] = []
				if not m in mats[m.resource_name]:
					mats[m.resource_name].append(m)
				if m.albedo_texture:
					m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	for c in n.get_children():
		collect(c)


# Small things stop being drawn at a distance, and distant windows are swapped for a light copy
# (build_assets.py makes both): name prefix -> [visible from, visible to] metres (0: no limit)
const FAR_RANGES := {"WinHi": [0.0, 48.0], "WinLo": [48.0, 0.0], "Detail_": [0.0, 95.0], "Wares_": [0.0, 75.0],
	"Plants_": [0.0, 95.0], "PlanterLeaves_": [0.0, 85.0], "Planter_": [0.0, 100.0], "KitText_": [0.0, 60.0],
	"PlaqueText_": [0.0, 30.0], "Plaque_": [0.0, 70.0], "Bins_": [0.0, 80.0], "BikeStand_": [0.0, 70.0],
	"KitCafe_": [0.0, 85.0], "MeshyCafe": [0.0, 110.0], "BeachCafe": [0.0, 110.0], "StreetBench_": [0.0, 85.0],
	"ParkBench_": [0.0, 85.0], "SeaBench_": [0.0, 85.0], "MeshyLamp_": [0.0, 110.0], "Bougainvillea_": [0.0, 120.0],
	"BougPlanter_": [0.0, 120.0], "BeachThings": [0.0, 160.0], "Grass_": [0.0, 55.0], "DoorPlaqueText_": [0.0, 30.0],
	"SignText_": [0.0, 70.0],
	# (round 41, rule 02 #5e) balcony railings: the iron bars close to, a flat picture of them further off, cross-faded
	"Rail_": [0.0, 16.0], "RailCard_": [16.0, 110.0],
	# the eastern wood: in full close to (with its undergrowth, "Plants_"), a light version further off
	"Leaves_forest_": [0.0, 105.0], "ForestTrunks_": [0.0, 110.0], "Leaves_far_": [95.0, 0.0], "ForestFar_": [100.0, 0.0]}
# (they fade out over the last FAR_FADE metres rather than vanishing all at once, and the near and far
# windows cross-fade, so the city doesn't visibly "load" as Sandra walks along)
const FAR_FADE := 14.0
# (round 41) the far stand-in trees' leaves, toned to match the near crowns where the two cross-fade (measured on the
# Ferris wheel at noon: the far ones ~17% brighter and yellower; tests: --fartone=r,g,b tries another)
var FAR_LEAF_TONE := Vector3(0.86, 0.90, 0.83)
# things too small or too flat against the walls for their shadows to be worth drawing
const NO_SHADOW_PREFIX := ["RailCard_", "WinHi", "WinLo", "WinPic_", "KitText_", "PlaqueText_", "Plaque_", "Wares_", "Plants_", "PlanterLeaves_", "Grass_",
	"DoorPlaque", "SignText_", "TowerText_", "Leaves_far_", "ForestFar_", "Leaves_wall_", "WallTrunks_"]
const NO_SHADOW := ["HillRope", "Trails", "Road", "RoadFar", "Pavement", "Zebras", "Kerbs", "Land", "Sea", "Foam", "Beach", "Park",
	"HillsNorth", "HillsWest", "HillsEast", "BeachEast", "Backdrop"]
var grain_tex: NoiseTexture2D


func lamp_glass(city: Node3D) -> void:
	# the street lamps (round 20e): the glass of each lantern glows after dark, where the light is, instead of
	# a glowing ball hung under it (lamp_glass.gdshader, added over the lamp's own material after dark)
	var lamps_ := city.find_children("MeshyLamp_*", "MeshInstance3D", true, false)
	if lamps_.is_empty():
		return
	var src := (lamps_[0] as MeshInstance3D).get_active_material(0) as StandardMaterial3D
	if src == null:
		return
	lamp_glass_mat = ShaderMaterial.new()
	lamp_glass_mat.shader = load("res://shaders/lamp_glass.gdshader")
	lamp_glass_mat.set_shader_parameter("albedo_tex", src.albedo_texture)
	lamp_mat = src.duplicate()
	for mi in lamps_:
		(mi as MeshInstance3D).material_override = lamp_mat


func forest_floor(city: Node3D) -> void:
	# the wood's floor (round 20b): needles, patchy grass (20d), the meadow's lawn or the beach's sand, by the light
	# each patch of it gets over the day (forest.py's light map; forest_floor.gdshader). Round 24: the hill's wood the
	# same way, from its own light map (north_build.py), on its own material (HillFloor).
	if not mats.has("ForestFloorLit") or not mats.has("ForestMid") or not mats.has("Lawn") or not mats.has("Sand"):
		return
	var fm := floor_material(D.get("forest_light", {}))
	var hm := floor_material(D.get("hill_light", {}))
	var pm := floor_material(D.get("park_light", {}))	# (round 33: Park Güell's wood, ParkFloor)
	if pm:
		pm.set_shader_parameter("sat", 0.6)				# (round 34: its green toned down, as its lawns and leaves)
	for n in city.find_children("*", "MeshInstance3D", true, false):
		for i in n.mesh.get_surface_count():
			var m = n.mesh.surface_get_material(i)
			if not m is StandardMaterial3D:
				continue
			if fm and m.resource_name in ["ForestFloorLit", "ForestMid"]:
				n.set_surface_override_material(i, fm)
			elif hm and m.resource_name == "HillFloor":
				n.set_surface_override_material(i, hm)
			elif pm and m.resource_name == "ParkFloor":
				n.set_surface_override_material(i, pm)


var shade_maps := []             # [info, Image]: the woods' light maps (blue = the light a patch gets over the day)


func wood_shade(p: Vector3) -> float:
	# (round 38) how deep in a wood she stands: 0 in the open, 1 in its shade (the light maps' blue, low under the crowns)
	for sm in shade_maps:
		var info: Dictionary = sm[0]
		var img: Image = sm[1]
		var u := (p.x - float(info.x0)) / float(info.w)
		var v := (p.z - float(info.z0)) / float(info.d)
		if u >= 0.0 and u < 1.0 and v >= 0.0 and v < 1.0:
			var c := img.get_pixel(int(u * img.get_width()), int(v * img.get_height()))
			return smoothstep(0.75, 0.35, c.b)
	return 0.0


func floor_material(info: Dictionary) -> ShaderMaterial:
	if info.is_empty():
		return null
	var img := Image.load_from_file(out_dir.path_join(String(info.file)))
	if img == null:
		return null
	shade_maps.append([info, img])                      # (round 38: the camera reads the shade from it too, wood_shade)
	var fm := ShaderMaterial.new()
	fm.shader = load("res://shaders/forest_floor.gdshader")
	fm.set_shader_parameter("litter_tex", mats["ForestFloorLit"][0].albedo_texture)
	fm.set_shader_parameter("mid_tex", mats["ForestMid"][0].albedo_texture)
	# (a test run can try another middle step: --midtex=<png>, 128 px to 3 m like the others)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--midtex="):
			var mi := Image.load_from_file(a.substr(9))
			if mi != null:
				mi.generate_mipmaps()
				fm.set_shader_parameter("mid_tex", ImageTexture.create_from_image(mi))
	fm.set_shader_parameter("lawn_tex", mats["Lawn"][0].albedo_texture)
	fm.set_shader_parameter("sand_tex", mats["Sand"][0].albedo_texture)
	fm.set_shader_parameter("light_map", ImageTexture.create_from_image(img))
	fm.set_shader_parameter("rect", Vector4(info.x0, info.z0, info.w, info.d))
	return fm


func prepare_city(city: Node3D) -> void:
	var grained := {}
	for n in city.get_children():
		if not n is MeshInstance3D:
			continue
		var nm := String(n.name)
		if nm in NO_SHADOW:
			n.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		for prefix in FAR_RANGES:
			if nm.begins_with(prefix):
				n.visibility_range_begin = FAR_RANGES[prefix][0]
				n.visibility_range_end = FAR_RANGES[prefix][1]
				n.visibility_range_begin_margin = FAR_FADE
				n.visibility_range_end_margin = FAR_FADE
				n.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
				# (round 41, rule 02 #39, the user on the Ferris wheel: "whole clumps of trees are jumping from one bright
				# color to one dark color") the woods' near and far trees swap without the speckled blend: with the camera
				# moving, the upscaler couldn't settle the speckle and whole clumps in the swap band flicked between the two
				# (measured: the biggest jump 18 → 9); the far ones toned to match, so the one clean swap doesn't show
				if prefix in ["Leaves_forest_", "ForestTrunks_", "Leaves_far_", "ForestFar_"] and not "--forestfade" in OS.get_cmdline_user_args():
					n.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
				break
		for prefix in NO_SHADOW_PREFIX:
			if nm.begins_with(prefix):
				n.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if nm == "Sea" or nm == "Foam":
			n.material_override = water_material(nm == "Sea")
		# a fine grain over the walls, so they stay crisp close to (the Meshy buildings' own
		# textures are stretched over the whole building)
		for i in n.mesh.get_surface_count():
			var m = n.mesh.surface_get_material(i)
			if m is StandardMaterial3D and not grained.has(m):
				var mn := String(m.resource_name)
				if mn.begins_with("Stucco") or mn.begins_with("Rustic") or (nm.begins_with("MeshyBuilding") and m.albedo_texture):
					add_grain(m)
					grained[m] = true
				elif mn.begins_with("WinPic"):         # (round 25) the picture windows: cut out sharply, never see-through
					m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
					m.alpha_scissor_threshold = 0.5
					grained[m] = true
		for prefix in ["Leaves_", "Plants_", "Bougainvillea_", "PlanterLeaves_", "Grass_"]:
			if nm.begins_with(prefix):
				use_foliage(n, prefix == "Leaves_")
		if nm.begins_with("Leaves_far_"):          # (rule 02 #39: the far trees matched to the near ones, measured)
			n.set_instance_shader_parameter("tone", FAR_LEAF_TONE)
		if nm.begins_with("RailCard_"):            # (the railings' far picture: see-through, blurring smoothly with distance)
			n.material_override = railcard_material(n.mesh.surface_get_material(0))


var railcard_mat: StandardMaterial3D


func railcard_material(from: Material) -> StandardMaterial3D:
	if railcard_mat == null:
		railcard_mat = StandardMaterial3D.new()
		railcard_mat.albedo_color = Color.WHITE
		if from is StandardMaterial3D:
			railcard_mat.albedo_texture = (from as StandardMaterial3D).albedo_texture
		railcard_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		railcard_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
		railcard_mat.roughness = 0.6
		railcard_mat.metallic = 0.5
		railcard_mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	return railcard_mat


func limit_leaf_shadows(dt: float) -> void:
	if leaf_casters.is_empty():
		for n in outdoor.find_children("Leaves_*", "MeshInstance3D", true, false):
			var mi := n as MeshInstance3D
			if mi.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF:
				continue
			var bb: AABB = mi.global_transform * mi.get_aabb()
			leaf_casters.append([mi, Rect2(bb.position.x, bb.position.z, bb.size.x, bb.size.z)])
	var her := player.global_position
	for key in foliage_mats:
		if key[1]:
			var sm: ShaderMaterial = foliage_mats[key]
			sm.set_shader_parameter("her_pos", her)
			sm.set_shader_parameter("shadow_r", LEAF_SHADOW_R)
	if LEAF_SHADOW_R <= 0.0 and leaf_shadow_last <= 0.0:
		return                          # (no limit, as before: the leaves left as they were made)
	leaf_shadow_t -= dt
	if leaf_shadow_t > 0.0 and LEAF_SHADOW_R == leaf_shadow_last:
		return
	leaf_shadow_t = 0.25
	leaf_shadow_last = LEAF_SHADOW_R
	for e in leaf_casters:
		var r: Rect2 = e[1]
		var dx := maxf(0.0, maxf(r.position.x - her.x, her.x - r.end.x))
		var dz := maxf(0.0, maxf(r.position.y - her.z, her.z - r.end.y))
		var on := LEAF_SHADOW_R <= 0.0 or Vector2(dx, dz).length() < LEAF_SHADOW_R + 1.0
		(e[0] as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if on else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


func add_grain(m: StandardMaterial3D) -> void:
	if grain_tex == null:
		var noise := FastNoiseLite.new()
		noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
		noise.frequency = 0.045
		noise.fractal_octaves = 4
		grain_tex = NoiseTexture2D.new()
		grain_tex.width = 256
		grain_tex.height = 256
		grain_tex.seamless = true
		grain_tex.noise = noise
		var g := Gradient.new()
		g.set_color(0, Color(0.84, 0.83, 0.81))
		g.set_color(1, Color(1.0, 1.0, 1.0))
		grain_tex.color_ramp = g
	m.detail_enabled = true
	m.detail_blend_mode = BaseMaterial3D.BLEND_MODE_MUL
	m.detail_albedo = grain_tex
	m.detail_uv_layer = BaseMaterial3D.DETAIL_UV_2
	m.uv2_triplanar = true
	m.uv2_world_triplanar = true
	m.uv2_scale = Vector3(0.55, 0.55, 0.55)


func water_material(sea: bool) -> ShaderMaterial:
	var sm := ShaderMaterial.new()
	sm.shader = load("res://shaders/sea.gdshader" if sea else "res://shaders/foam.gdshader")
	var noise := FastNoiseLite.new()
	noise.frequency = 0.03
	if sea:
		for k in 2:
			var nt := NoiseTexture2D.new()
			nt.seamless = true
			nt.as_normal_map = true
			nt.bump_strength = 6.0 if k == 0 else 3.0
			nt.noise = noise
			sm.set_shader_parameter("wave_a" if k == 0 else "wave_b", nt)
		sm.set_shader_parameter("shore_z", D.get("sea_z", 215.0))
	else:
		var nt := NoiseTexture2D.new()
		nt.seamless = true
		nt.noise = noise
		sm.set_shader_parameter("noise", nt)
	return sm


func use_foliage(mi: MeshInstance3D, is_tree: bool) -> void:
	for i in mi.mesh.get_surface_count():
		var src = mi.mesh.surface_get_material(i)
		if not src is StandardMaterial3D:
			continue
		# (round 23, the user: "the light on the lighter trees in the forest is flickering") a tree's crown doesn't take
		# the shadows of its own leaves: as the leaves sway and the sun turns, those speckles flickered all over the
		# sunlit crowns; measured: 70% less flicker, the crowns look the same. Grass, flowers and bushes keep them.
		var key: Array = [src, is_tree]
		if not foliage_mats.has(key):
			var sm := ShaderMaterial.new()
			sm.shader = crown_shader if is_tree else foliage_shader
			sm.set_shader_parameter("albedo_tex", src.albedo_texture)
			sm.set_shader_parameter("shadow_motion", 0.0)        # (round 26: the leaves' shadows hold still: no popping dapples)
			foliage_mats[key] = sm
		mi.set_surface_override_material(i, foliage_mats[key])
	mi.set_instance_shader_parameter("sway_base", 2.8 if is_tree else -100.0)
	mi.set_instance_shader_parameter("sway_amp", 0.035 if is_tree else 0.012)


func set_emit(mname: String, col: Color, energy: float) -> void:
	for m in mats.get(mname, []):
		m.emission_enabled = energy > 0.0
		m.emission = col
		m.emission_energy_multiplier = energy


func load_meshy_sandra(file: String, parent: Node3D = null, made: Node3D = null) -> Dictionary:
	if made == null and not FileAccess.file_exists(asset_path("meshy/" + file)):
		return {}
	var sc := made if made else load_glb("meshy/" + file)
	sc.scale *= MODEL_SCALE.get(file, 1.0)
	(parent if parent else model).add_child(sc)
	var ap: AnimationPlayer = null
	var players := sc.find_children("*", "AnimationPlayer", true, false)
	if players.size() > 0:
		ap = players[0]
	var anims := {"idle": "", "move": ""}
	if ap:
		for a in ap.get_animation_list():
			var l := String(a).to_lower()
			if anims.idle == "" and ("idle" in l or "stand" in l or "breath" in l):
				anims.idle = a
			if "run" in l or "jog" in l:
				anims.move = a
			elif anims.move == "" and "walk" in l:
				anims.move = a
		for key in anims:
			if anims[key] != "":
				ap.get_animation(anims[key]).loop_mode = Animation.LOOP_LINEAR
	var smats := []
	for mi in sc.find_children("*", "MeshInstance3D", true, false):
		if mi.skin == null:
			mi.visible = false                    # Meshy exports carry a stray helper sphere; only the skinned body is shown
			continue
		var masked := hair_mask(mi) if parent == null else false        # (only Sandra's hair sways)
		for i in mi.mesh.get_surface_count():
			var src = mi.mesh.surface_get_material(i)
			if not src is StandardMaterial3D:
				continue
			var sm := ShaderMaterial.new()
			sm.shader = char_shader
			sm.set_shader_parameter("hair_mask", masked)
			sm.set_shader_parameter("albedo_tex", src.albedo_texture)
			if src.roughness_texture:
				sm.set_shader_parameter("orm_tex", src.roughness_texture)
				sm.set_shader_parameter("has_orm", true)
			if src.normal_enabled and src.normal_texture:
				sm.set_shader_parameter("normal_tex", src.normal_texture)
				sm.set_shader_parameter("has_normal", true)
			mi.set_surface_override_material(i, sm)
			smats.append(sm)
	# standing up straight (posture.gd): her idle leans her back
	var posture: SkeletonModifier3D = null
	var skels := sc.find_children("*", "Skeleton3D", true, false)
	if skels.size() > 0:
		var skel: Skeleton3D = skels[0]
		posture = SkeletonModifier3D.new()
		posture.set_script(load("res://engine/posture.gd"))
		skel.add_child(posture)
		skel.move_child(posture, 0)
		posture.model = sc
		for bn in ["Spine", "Spine1", "Spine2"]:
			posture.bones.append(skel.find_bone(street_bone(skel, bn)))
		posture.hips = skel.find_bone(street_bone(skel, "Hips"))
		posture.neck = skel.find_bone(street_bone(skel, "Neck"))
		for bn in ["LeftUpLeg", "RightUpLeg"]:
			posture.legs.append(skel.find_bone(street_bone(skel, bn)))
		for bn in ["LeftFoot", "RightFoot"]:
			posture.feet.append(skel.find_bone(street_bone(skel, bn)))
		posture.amount = IDLE_TILT
		if parent == null:
			# (round 41, the user: "could you make Sandra's arms slightly shorter?") her upper arms and forearms drawn in
			# by ARM_K, at their rest: her animations don't move these bones' lengths, and the seated and riding poses
			# reach with the rest lengths, so her hands still find the grips, the desk and her knees
			var ak := ARM_K
			for a in OS.get_cmdline_user_args():          # (tests: --armk= tries other lengths)
				if a.begins_with("--armk="):
					ak = float(a.substr(7))
			if absf(ak - 1.0) > 0.001:
				for bn in ["LeftForeArm", "LeftHand", "RightForeArm", "RightHand"]:
					var bi := skel.find_bone(street_bone(skel, bn))
					print("ARMK %s %s -> bone %d" % [file, bn, bi])
					if bi >= 0:
						var rx := skel.get_bone_rest(bi)
						rx.origin *= ak
						skel.set_bone_rest(bi, rx)
						skel.reset_bone_pose(bi)
	return {"root": sc, "ap": ap, "anims": anims, "mats": smats, "posture": posture}


func hair_mask(mi: MeshInstance3D) -> bool:
	# Which of her points are hair, for the hair's sway (character.gdshader), worked out once here and kept in
	# the mesh's vertex colours (alpha). The shader used to decide by the colour under each point, but where the
	# model's texture is cut and joined the same point comes twice, with different texture positions: one copy
	# could sway while the other stayed, opening little see-through gaps in her hair as she moved (round 21).
	# Here each point is hair if any of its copies is, so they always move together.
	var mesh := mi.mesh as ArrayMesh
	if mesh == null:
		return false
	var out := ArrayMesh.new()
	for s in mesh.get_surface_count():
		var arrays := mesh.surface_get_arrays(s)
		var mat := mesh.surface_get_material(s)
		var tex: Texture2D = mat.albedo_texture if mat is StandardMaterial3D else null
		var img: Image = tex.get_image() if tex else null
		if img == null:
			return false
		if img.is_compressed():
			img.decompress()
		var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
		var w := img.get_width()
		var h := img.get_height()
		var hair := {}
		for i in verts.size():
			var c := img.get_pixel(clampi(int(uvs[i].x * w), 0, w - 1), clampi(int(uvs[i].y * h), 0, h - 1)).srgb_to_linear()
			var mx := maxf(c.r, maxf(c.g, c.b))
			var mn := minf(c.r, minf(c.g, c.b))
			var sat := (mx - mn) / mx if mx > 0.0 else 0.0
			var b := c.r >= c.g and c.g >= c.b * 0.9 and sat > 0.35 and mx > 0.12 and mx < 0.66
			if b:
				hair[verts[i].snapped(Vector3.ONE * 0.0001)] = true
		var cols := PackedColorArray()
		cols.resize(verts.size())
		for i in verts.size():
			cols[i] = Color(1, 1, 1, 1.0 if hair.has(verts[i].snapped(Vector3.ONE * 0.0001)) else 0.0)
		arrays[Mesh.ARRAY_COLOR] = cols
		if testing:
			print("HAIRMASK %s: %d points, %d places on her that are hair" % [mi.name, verts.size(), hair.size()])
		out.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {}, mesh.surface_get_format(s) & Mesh.ARRAY_FLAG_USE_8_BONE_WEIGHTS)
		out.surface_set_material(s, mat)
	mi.mesh = out
	return true


func street_bone(skel: Skeleton3D, tail: String) -> String:
	# (the importer may call "mixamorig:Spine" "mixamorig_Spine")
	for i in skel.get_bone_count():
		var n := skel.get_bone_name(i)
		if n == tail or n.ends_with("_" + tail) or n.ends_with(":" + tail):
			return n
	# (round 40: a cached model instanced again gains "_2" per copy — "mixamorig_Head_2_2_2" — so the people's posture
	# found none of their bones and never stood them up; matched with the copies' suffixes stripped)
	for i in skel.get_bone_count():
		var n := skel.get_bone_name(i)
		var base := n
		while base.ends_with("_2"):
			base = base.left(-2)
		if base == tail or base.ends_with("_" + tail) or base.ends_with(":" + tail):
			return n
	return tail


func apply_look(mats: Array, swaps: Array, hide_side := false) -> void:
	# dresses a Meshy character differently (character.gdshader's recolouring)
	for m in mats:
		m.set_shader_parameter("swaps", swaps.size())
		for i in swaps.size():
			var sw: Dictionary = swaps[i]
			m.set_shader_parameter("swap%d_band" % i, Vector4(sw.hue[0], sw.hue[1], sw.sat[0], sw.val[1]))
			m.set_shader_parameter("swap%d_limits" % i, Vector4(sw.sat[1], sw.val[0], sw.h[0], sw.h[1]))
			m.set_shader_parameter("swap%d_col" % i, Color(sw.col))
			m.set_shader_parameter("swap%d_ref" % i, sw.ref)
		m.set_shader_parameter("hide_side", hide_side)


func dress_sandra() -> void:
	# what she is wearing from her backpack, as the 2D game draws it: the outfit's colours on her top
	# (and her legs, in the sun dress), the barretina on her head
	var it: Dictionary = game.item(game.S.worn.outfit) if game.S.worn.outfit else {}
	var wear: Dictionary = it.get("wear", {})
	var swaps := []
	if wear.has("top"):
		var top: String = it.col if wear.top == "stripes" else wear.top            # (the Barça jersey: its claret)
		swaps.append({"hue": [0, 360], "sat": [0.0, 0.14], "val": [0.6, 1.0], "h": [0.42, 1.0], "col": top, "ref": 0.85})
	if wear.has("legs"):
		swaps.append({"hue": [180, 240], "sat": [0.2, 1.0], "val": [0.0, 1.0], "h": [0.05, 0.55], "col": wear.legs, "ref": 0.3})
	var hat = game.item(game.S.worn.hat).get("wear", {}).get("hat", "") if game.S.worn.hat else ""
	for sk in skins:
		apply_look(sk.mats, swaps)
		for mat in sk.mats:
			mat.set_shader_parameter("cap_on", false)
		sk.erase("cap")
		for old in sk.root.find_children("*", "BoneAttachment3D", true, false):
			if old.has_meta("accessory"):
				old.get_parent().remove_child(old)
				old.queue_free()
		if hat != "":
			npcs.accessories(model, sk, sk.file, {"hat": hat, "hatc": game.item(game.S.worn.hat).get("col", "#c2272d")}, {})


func show_skin(i: int) -> void:
	if skins.is_empty():
		return
	skin_idx = i % skins.size()
	for k in skins.size():
		skins[k].root.visible = k == skin_idx


func animate_skin(dt: float, spd: float) -> void:
	var sk: Dictionary = skins[skin_idx]
	npcs.follow_cap(model, sk)
	var ap: AnimationPlayer = sk.ap
	if ap and ((street and street.riding) or (benches and benches.seated())):
		if ap.is_playing():
			ap.stop()                             # on the bike (or a bench) her pose comes from rider_pose.gd, from her rest pose
			for skel in sk.root.find_children("*", "Skeleton3D", true, false):
				skel.reset_bone_poses()
	elif ap:
		var want: String = sk.anims.move if (spd > 0.4 and sk.anims.move != "") else sk.anims.idle
		if want != "" and ap.current_animation != want:
			ap.play(want, 0.25)
		ap.speed_scale = clampf(spd / MOVE_ANIM_SPEED, 0.7, 1.4) if want == sk.anims.move else 1.0
	if sk.get("posture"):
		var still := 0.0 if ((street and street.riding) or (benches and benches.seated())) else 1.0 - smoothstep(0.1, 1.2, spd)
		sk.posture.amount = lerpf(sk.posture.amount, IDLE_TILT * still, 1.0 - exp(-6.0 * dt))
	# hair trails a little behind her movement and settles when she stops
	var vel := player.get_real_velocity()
	vel.y = 0.0
	var accel := (vel - prev_vel) / maxf(dt, 0.001)
	prev_vel = vel
	var target := (-vel * 0.011 - accel * 0.003).limit_length(0.06)
	hair_offset = hair_offset.lerp(target, 1.0 - exp(-5.0 * dt))
	for m in sk.mats:
		m.set_shader_parameter("hair_offset", hair_offset)
		m.set_shader_parameter("ground_y", player.global_position.y + model.position.y)


# ------------------------------------------------------------------ physics

func static_body(layers: int) -> StaticBody3D:
	var b := StaticBody3D.new()
	b.collision_layer = layers
	b.collision_mask = 0
	add_child(b)
	return b


func add_box(b: StaticBody3D, centre: Vector3, size: Vector3) -> void:
	var cs := CollisionShape3D.new()
	var sh := BoxShape3D.new()
	sh.size = size
	cs.shape = sh
	cs.position = centre
	b.add_child(cs)


func add_post(b: StaticBody3D, x: float, z: float, r: float, h := 3.0) -> void:
	var cs := CollisionShape3D.new()
	var sh := CylinderShape3D.new()
	sh.radius = r
	sh.height = h
	cs.shape = sh
	cs.position = Vector3(x, h / 2.0, z)
	b.add_child(cs)


func build_physics() -> void:
	var ground := static_body(LAYER_BODY | LAYER_CAMERA)
	var gs := CollisionShape3D.new()
	gs.shape = WorldBoundaryShape3D.new()
	ground.add_child(gs)
	# (round 40, the user: "treat it like an actual camera that's moving. It cannot go through walls and magically see the
	# inside of a building but it can sit over the hedge under the ceiling"; rule 03 #16) the camera's walls are named,
	# never found by size: the city's buildings (the blocks), the buildings on the hills the build lists ('cam_buildings',
	# at their real height), a proud front's screen and a room's own walls. Everything else stops her, not the camera.
	var walls := static_body(LAYER_BODY | LAYER_CAMERA)
	for blk in D.blocks:
		# a block is one solid prism, unless it has a courtyard you can walk into (then a ring of pieces)
		for poly in blk.get("solids", [blk.poly]):
			var pts := PackedVector3Array()
			for p in poly:
				pts.append(Vector3(p[0], 0, p[1]))
				pts.append(Vector3(p[0], 18, p[1]))
			var cs := CollisionShape3D.new()
			var sh := ConvexPolygonShape3D.new()
			sh.points = pts
			cs.shape = sh
			walls.add_child(cs)
	var stops := static_body(LAYER_BODY)                 # (walls, hedges, columns, benches, rocks: her, not the camera)
	for poly in D.get("solids", []):
		var pts2 := PackedVector3Array()
		for p in poly:
			pts2.append(Vector3(p[0], 0, p[1]))
			pts2.append(Vector3(p[0], 4, p[1]))
		var cs2 := CollisionShape3D.new()
		var sh2 := ConvexPolygonShape3D.new()
		sh2.points = pts2
		cs2.shape = sh2
		stops.add_child(cs2)
	for r in D.get("blocked", []):
		add_box(stops, Vector3((r[0] + r[2]) / 2.0, 2, (r[1] + r[3]) / 2.0), Vector3(r[2] - r[0], 4, r[3] - r[1]))
	# the hills' buildings for the camera alone, where they really stand (her body is at street level there, the camera
	# up at her real height): the park's houses, the church, the funicular's stations
	var cam_bld := static_body(LAYER_CAMERA)
	for b in D.get("cam_buildings", []):
		var r: Array = b.r
		add_box(cam_bld, Vector3((r[0] + r[2]) / 2.0, (float(b.lo) + float(b.hi)) / 2.0, (r[1] + r[3]) / 2.0),
			Vector3(r[2] - r[0], float(b.hi) - float(b.lo), r[3] - r[1]))
	# roofs she walks under (the park's covered walk): their ceilings, by 4 m cell, for the camera to stay under
	for rf in D.get("cam_roofs", []):
		var poly := PackedVector2Array()
		for q in rf.p:
			poly.append(Vector2(q[0], q[1]))
		var bb := Rect2(poly[0], Vector2.ZERO)
		for q in poly:
			bb = bb.expand(q)
		var w := {"poly": poly, "ceil": float(rf.ceil), "top": float(rf.top)}
		for gx in range(floori(bb.position.x / 4.0), floori(bb.end.x / 4.0) + 1):
			for gz in range(floori(bb.position.y / 4.0), floori(bb.end.y / 4.0) + 1):
				if not cam_roofs.has(Vector2i(gx, gz)):
					cam_roofs[Vector2i(gx, gz)] = []
				cam_roofs[Vector2i(gx, gz)].append(w)
	# (round 23, the user: coming out of the university "you can't see anything") some fronts stand proud of their
	# block's outline (the university's portico, the MNAC's terrace): a camera-only screen at each door's own wall,
	# so the camera arm stops in front of the facade instead of inside it
	var door_screens := static_body(LAYER_CAMERA)
	for e in D.entrances:
		var nn := Vector3(e.normal[0], 0, e.normal[1])
		var cs3 := CollisionShape3D.new()
		var sh3 := BoxShape3D.new()
		sh3.size = Vector3(float(e.size[0]) + 3.0, 14.0, 0.3)
		cs3.shape = sh3
		cs3.transform = Transform3D(Basis(Vector3.UP, atan2(nn.x, nn.z)), Vector3(e.pos[0], 7.0, e.pos[1]) - nn * 0.15)
		if e.has("screen"):
			# (round 35: a Gaudí front standing proud along its whole length: [its middle x, z 1 m out, its width])
			var sc: Array = e.screen
			sh3.size = Vector3(float(sc[2]), 14.0, 0.3)
			cs3.transform = Transform3D(Basis(Vector3.UP, atan2(nn.x, nn.z)), Vector3(float(sc[0]), 7.0, float(sc[1])))
		door_screens.add_child(cs3)
	var W = D.walk
	var cx: float = (W.x0 + W.x1) / 2.0
	var cz: float = (W.z0 + W.z1) / 2.0
	add_box(stops, Vector3(cx, 2, W.z0 - 0.5), Vector3(W.x1 - W.x0 + 2, 4, 1))
	add_box(stops, Vector3(cx, 2, W.z1 + 0.5), Vector3(W.x1 - W.x0 + 2, 4, 1))
	add_box(stops, Vector3(W.x0 - 0.5, 2, cz), Vector3(1, 4, W.z1 - W.z0 + 2))
	add_box(stops, Vector3(W.x1 + 0.5, 2, cz), Vector3(1, 4, W.z1 - W.z0 + 2))
	# trees, lamps and planters stop Sandra but not the camera
	var props := static_body(LAYER_BODY)
	# (round 39, the user: "she can push against a tree and get out") the trunks in a body of their own, the one thing
	# she may go through (slip_trees)
	tree_body = static_body(LAYER_BODY)
	for p in D.trees:
		add_post(tree_body, p[0], p[1], 0.25)
	# (round 39, the user: "Isn't brush walkable anyway?") the thick bushes on short steep bits (scene 'plant_solids',
	# solid since round 35) are walked through like every other bush now: nothing to be trapped against
	# the wood (round 20): walked anywhere, only its trunks are solid (the leaves and shrubs are walked
	# through); remembered by 4 m cell so she can slip between two she is stuck against (slip_trees())
	for p in D.get("forest_trees", []):
		var key := Vector2i(floori(p[0] / 4.0), floori(p[1] / 4.0))
		if not forest_cells.has(key):
			forest_cells[key] = []
		forest_cells[key].append(Vector2(p[0], p[1]))
	for r in D.get("forest_blocked", []):
		add_box(props, Vector3((r[0] + r[2]) / 2.0, 2, (r[1] + r[3]) / 2.0), Vector3(r[2] - r[0], 4, r[3] - r[1]))
	# the beach's sand stops the bike dead (she walks there)
	var nob := static_body(LAYER_NOBIKE)
	for r in D.get("nobike", []):
		add_box(nob, Vector3((r[0] + r[2]) / 2.0, 2, (r[1] + r[3]) / 2.0), Vector3(r[2] - r[0], 4, r[3] - r[1]))
		var c0 := Vector2i(floori(r[0] / 8.0), floori(r[1] / 8.0))
		var c1 := Vector2i(floori(r[2] / 8.0), floori(r[3] / 8.0))
		for gx in range(c0.x, c1.x + 1):
			for gz in range(c0.y, c1.y + 1):
				var k2 := Vector2i(gx, gz)
				if not nobike_cells.has(k2):
					nobike_cells[k2] = []
				nobike_cells[k2].append(r)
	# (round 41, the user: "She also shouldn't be able to ride the bike down into the forest glade from the mountain path";
	# then "make sure you can't cycle through the forest. Glade coming down the hill. Any of the forest") on the hill the
	# bike keeps to its path: a thin wall along each side of it, the whole way up (only the bike: she walks off it) —
	# laid along the path's own offset line, two points at a time, and left out where that line runs back over the path
	# (the inside of a tight hairpin) and at the two ends (the pavement at its foot, the funfair's gateway)
	var pp: Array = D.get("north", {}).get("path", [])
	if pp.size() > 8:
		var gw := float(D.north.get("path_w", 2.4)) / 2.0 + 0.45
		var pv: Array[Vector2] = []
		for q in pp:
			pv.append(Vector2(q[0], q[1]))
		var off := func(i: int, sd: float) -> Vector2:
			var t := (pv[mini(i + 1, pv.size() - 1)] - pv[maxi(i - 1, 0)]).normalized()
			return pv[i] + t.orthogonal() * gw * sd
		var clear := func(c: Vector2) -> bool:
			for v in pv:
				if v.distance_to(c) < gw - 0.25:
					return false
			return true
		for sd in [-1.0, 1.0]:
			var k := 0
			while k < pv.size() - 2:
				var a: Vector2 = off.call(k, sd)
				var b: Vector2 = off.call(k + 2, sd)
				var mid := (a + b) / 2.0
				if pv[k].y < -107.0 and pv[k].distance_to(pv[pv.size() - 1]) > 3.0 and a.distance_to(b) > 0.05 \
						and clear.call(a) and clear.call(b) and clear.call(mid):
					var cs := CollisionShape3D.new()
					var sh := BoxShape3D.new()
					sh.size = Vector3(a.distance_to(b) + 0.25, 4.0, 0.1)
					cs.shape = sh
					cs.transform = Transform3D(Basis(Vector3.UP, -(b - a).angle()), Vector3(mid.x, float(pp[k + 1][2]) + 1.0, mid.y))
					nob.add_child(cs)
				k += 2
	# the thick of the wood (round 20e, the user's rule): a rope from trunk to trunk round its edge
	# (shared/bike_rope.py), each length of it a thin wall the bike stops at, so the only invisible wall is
	# between two trees; and a map of the ground it closes in, so she can't get on the bike in there
	var br: Dictionary = D.get("bike_rope", {})
	var rope := static_body(LAYER_NOBIKE)
	for r in br.get("ropes", []):
		var a := Vector2(r[0], r[1])
		var b := Vector2(r[2], r[3])
		var cs := CollisionShape3D.new()
		var sh := BoxShape3D.new()
		sh.size = Vector3(a.distance_to(b), 4.0, 0.1)
		cs.shape = sh
		var mid := (a + b) / 2.0
		cs.transform = Transform3D(Basis(Vector3.UP, -(b - a).angle()), Vector3(mid.x, 2.0, mid.y))
		rope.add_child(cs)
	if br.has("map"):
		rope_map = Image.load_from_file(out_dir.path_join(String(br.map)))
		rope_at = Vector3(br.x0, br.z0, br.cell)
	for l in D.lamps:
		add_post(props, l.pos[0], l.pos[1], 0.14)
	for o in D.obstacles:
		add_post(props, o.pos[0] + o.off[0], o.pos[1] + o.off[1], o.r * 0.75, 1.0)
	# the rooms: walls round the floor, with the way out a gap in the front wall, and their furniture
	var rb := static_body(LAYER_BODY | LAYER_CAMERA)
	var rb_cols := static_body(LAYER_BODY)
	for rid in D.interiors:
		var R: Dictionary = D.interiors[rid]
		var O := room_base(rid)
		var w: float = R.w
		var h: float = R.h
		var wh: float = maxf(2.8, R.get("wall_h", 2.8)) if R.get("free_cam", false) else 2.8
		if R.get("exit_top") == null:
			add_box(rb, O + Vector3(w / 2.0, wh / 2.0, 0.9), Vector3(w, wh, 0.2))
		else:
			var t0: float = R.exit_top[0]
			var t1: float = R.exit_top[1]
			add_box(rb, O + Vector3(t0 / 2.0, wh / 2.0, 0.9), Vector3(t0, wh, 0.2))
			add_box(rb, O + Vector3((t1 + w) / 2.0, wh / 2.0, 0.9), Vector3(w - t1, wh, 0.2))
			# the landing beyond (in the basilica, just past the threshold: its doors' corridors are only to look
			# down, she is outside as soon as she steps into one)
			add_box(rb, O + Vector3((t0 + t1) / 2.0, 1.4, 0.25 if R.get("free_cam", false) else -0.2), Vector3(t1 - t0 + 0.4, 2.8, 0.2))
		add_box(rb, O + Vector3(0.9, wh / 2.0, h / 2.0), Vector3(0.2, wh, h + 2.0))
		add_box(rb, O + Vector3(w - 0.9, wh / 2.0, h / 2.0), Vector3(0.2, wh, h + 2.0))
		if R.exit == null:
			add_box(rb, O + Vector3(w / 2.0, wh / 2.0, h + 0.1), Vector3(w, wh, 0.2))
		else:
			var e0: float = R.exit[0]
			var e1: float = R.exit[1]
			add_box(rb, O + Vector3(e0 / 2.0, wh / 2.0, h + 0.1), Vector3(e0, wh, 0.2))
			add_box(rb, O + Vector3((e1 + w) / 2.0, wh / 2.0, h + 0.1), Vector3(w - e1, wh, 0.2))
			add_box(rb, O + Vector3((e0 + e1) / 2.0, 1.4, h + (0.75 if R.get("free_cam", false) else 1.2)), Vector3(e1 - e0 + 0.4, 2.8, 0.2))   # the landing beyond
		if R.get("free_cam", false):
			add_box(rb, O + Vector3(w / 2.0, wh + 0.1, h / 2.0), Vector3(w, 0.2, h + 2.0))            # (a lid, for the camera)
			# the doorways stop the camera (not Sandra), so it never swings out into the dark beyond
			var camb := static_body(LAYER_CAMERA)
			for pair in [[R.exit, h + 0.1], [R.get("exit_top"), 0.9]]:
				var ex = pair[0]
				if ex != null:
					add_box(camb, O + Vector3((ex[0] + ex[1]) / 2.0, wh / 2.0, pair[1]), Vector3(ex[1] - ex[0], wh, 0.2))
		for sd in R.solids:
			# (round 40: a room's furniture stops her, not the camera — only its walls do, rule 03 #16)
			add_box(rb_cols, O + Vector3((sd[0] + sd[2]) / 2.0, 0.5, (sd[1] + sd[3]) / 2.0), Vector3(sd[2] - sd[0], 1.0, sd[3] - sd[1]))
		for pt in R.get("posts", []):
			# (round columns: she slides round them; round 40, the user: "Don't treat the columns as a wall. So when she
			# runs behind a column, the camera just keeps tracking her. As if the column is invisible", rule 03 #16a —
			# they stop her, not the camera)
			add_post(rb_cols, O.x + pt[0], O.z + pt[1], pt[2])


var forest_cells := {}            # 4 m cell -> the wood's trunks in it (Vector2, metres)
var cam_roofs := {}               # (round 40) 4 m cell -> the roofs she walks under ({poly, ceil, top}), for the camera
var nobike_said := -100.0       # when the bike last said why it stopped (riding into the trees or the sand)
var nobike_cells := {}            # 8 m cell -> the no-bike rectangles touching it
func in_bike_free_park(p: Vector3) -> bool:
	# (round 35, the user: "the bike is not allowed in the park") inside Park Güell's wall
	var w: Array = D.get("north", {}).get("park", {}).get("wall", [])
	if w.size() < 3:
		return false
	var inside := false
	var j := w.size() - 1
	for i in w.size():
		var a: Array = w[i]
		var b: Array = w[j]
		if (float(a[1]) > p.z) != (float(b[1]) > p.z) and p.x < (float(b[0]) - float(a[0])) * (p.z - float(a[1])) / (float(b[1]) - float(a[1])) + float(a[0]):
			inside = not inside
		j = i
	return inside


var rope_map: Image               # the ground the wood's rope closes in (white), a cell to a pixel
var rope_at := Vector3.ZERO        # that map's corner (x, z) and its cell size, metres
var stuck_t := 0.0               # seconds she has been pushing without getting anywhere
var slipping := false            # (round 39) she passes through what holds her, until she is clear of it
var slip_t := 0.0
var slip_from := Vector3.ZERO
var stuck_last := Vector3.ZERO
var tree_body: StaticBody3D       # (round 39) every tree trunk: what she may push through
var player_shape: CapsuleShape3D


func no_bike_at(p: Vector3) -> bool:
	for r in nobike_cells.get(Vector2i(floori(p.x / 8.0), floori(p.z / 8.0)), []):
		if p.x > r[0] and p.x < r[2] and p.z > r[1] and p.z < r[3]:
			return true
	if in_bike_free_park(p):
		return true
	# (round 41, the user: "She also shouldn't be able to ride the bike down into the forest glade from the mountain path")
	# in the ball's glade the bike keeps to the path: she walks down to the ball
	var gl: Array = D.get("north", {}).get("glade", [])
	if gl.size() == 4 and p.x > gl[0] and p.x < gl[2] and p.z > gl[1] and p.z < gl[3] and north and not north.on_path(p, 0.5):
		return true
	if on_hill_off_path(p):
		return true
	if rope_map:
		var i := floori((p.x - rope_at.x) / rope_at.z)
		var j := floori((p.z - rope_at.y) / rope_at.z)
		if i >= 0 and j >= 0 and i < rope_map.get_width() and j < rope_map.get_height() and rope_map.get_pixel(i, j).r > 0.5:
			return true
	return false


func on_hill_off_path(p: Vector3) -> bool:
	# (round 41, the user: "make sure you can't cycle through the forest… Any of the forest") the wooded hill below the
	# funfair, off its path
	if north == null or p.x > -14.0 or p.z > -106.0 or p.y < 1.5:
		return false
	var fr: Array = D.get("north", {}).get("fair", {}).get("rect", [0, 0, 0, 0])
	if p.x > fr[0] - 0.5 and p.x < fr[2] + 0.5 and p.z > fr[1] - 0.5 and p.z < fr[3] + 0.5:
		return false
	return not north.on_path(p, 0.5)


func near_trunk(p: Vector3, within: float) -> bool:
	var c := Vector2i(floori(p.x / 4.0), floori(p.z / 4.0))
	for dx in [-1, 0, 1]:
		for dz in [-1, 0, 1]:
			for tp in forest_cells.get(c + Vector2i(dx, dz), []):
				if Vector2(p.x, p.z).distance_to(tp) < within:
					return true
	return false


func slip_trees(inp: Vector2, real_speed: float, dt: float) -> void:
	# (round 39, the user, a rule made long ago and now kept everywhere: "she can push against a tree and get out…
	# There may be lots of places she falls down and she gets stuck between a tree and something else") pressing to go
	# somewhere for three seconds without getting anywhere, while touching a tree trunk, the trees stop holding her
	# until she is clear of them. Nothing else is ever passed through.
	if slipping:
		slip_t += dt
		if slip_t > 0.2 and touching([tree_body], R + 0.02) == 0:
			slip_done(false)
		elif slip_t > 2.5:
			slip_done(true)
		return
	var here := player.global_position
	var pushing := inp.length() > 0.3 and not busy and not dlg_open and not ride_cam
	# (got nowhere: measured from where she was, not frame by frame — on a slope she jitters to and fro)
	if not pushing or Vector2(here.x - stuck_last.x, here.z - stuck_last.z).length() > 0.4:
		stuck_last = here
		stuck_t = 0.0
		return
	stuck_t += dt
	if stuck_t > 3.0:
		stuck_t = 0.0
		stuck_last = here
		if touching([tree_body], R + 0.2) >= 1:
			slipping = true
			slip_t = 0.0
			slip_from = here
			player.add_collision_exception_with(tree_body)


func touching(bodies: Array, radius: float) -> int:
	# how many solid things (shapes) are within reach of her body at waist height: any (bodies empty) or only those
	var q := PhysicsShapeQueryParameters3D.new()
	var ball := SphereShape3D.new()
	ball.radius = radius
	q.shape = ball
	q.transform = Transform3D(Basis(), player.global_position + Vector3(0, 0.9, 0))
	q.collision_mask = LAYER_BODY
	q.exclude = [player.get_rid()]
	var n := 0
	for hit in get_world_3d().direct_space_state.intersect_shape(q, 16):
		if bodies.is_empty() or bodies.has(hit.collider):
			n += 1
	return n


func slip_done(back: bool) -> void:
	# solid again; still inside a small thing after 2.5 s, she is put back where she started
	if back:
		player.global_position = slip_from
		player.velocity = Vector3.ZERO
	player.remove_collision_exception_with(tree_body)
	slipping = false


func free_cam() -> bool:
	# the street camera, steered by the mouse: outdoors, and in the big rooms walked round freely (the
	# Sagrada Família), where the fixed camera over a cut-away wall wouldn't show the vaults
	return where == "out" or (where == "in" and room != "" and D.interiors[room].get("free_cam", false))


func room_base(rid: String) -> Vector3:
	# where a room's (0, 0) corner is in the world
	return INTERIOR_OFFSET + Vector3(D.interiors[rid].offset[0], 0, 0)


func build_player() -> void:
	player = CharacterBody3D.new()
	player.collision_layer = 0
	player.collision_mask = LAYER_BODY
	player.floor_snap_length = 0.3
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = R
	cap.height = 1.6
	cs.shape = cap
	player_shape = cap
	cs.position.y = 0.8
	player.add_child(cs)
	add_child(player)
	model = Node3D.new()
	player.add_child(model)
	char_shader = load("res://shaders/character.gdshader")
	for f in ["sandra_a.glb", "sandra_b.glb"]:
		var sk := load_meshy_sandra(f)
		if not sk.is_empty():
			sk.file = f
			skins.append(sk)
	show_skin(0)
	player.global_position = Vector3(D.spawn.pos[0], 0, D.spawn.pos[1])
	model.rotation.y = D.spawn.facing
	move_dir = Vector2(sin(model.rotation.y), cos(model.rotation.y))


func build_camera() -> void:
	cam_root = Node3D.new()
	cam_root.top_level = true
	add_child(cam_root)
	cam_yaw_node = Node3D.new()
	cam_root.add_child(cam_yaw_node)
	cam_pitch_node = Node3D.new()
	cam_pitch_node.rotation.x = CAM_PITCH
	cam_yaw_node.add_child(cam_pitch_node)
	arm = SpringArm3D.new()
	arm.spring_length = CAM_DIST
	arm.collision_mask = LAYER_CAMERA
	arm.margin = 0.25
	var probe := SphereShape3D.new()
	# (round 35, the play-through's pictures: 0.25, and against a front the camera went into the pilasters, sills and
	# shop boards standing proud of the block's outline, which is what it feels; it keeps 0.4 m off now)
	probe.radius = 0.4
	arm.shape = probe
	cam_pitch_node.add_child(arm)
	cam = Camera3D.new()
	cam.fov = 62.0
	cam.far = 2200.0                                 # (round 26: out to the far country's edge, world2d.py FarLand)
	arm.add_child(cam)
	cam_yaw_node.rotation.y = model.rotation.y + PI       # start behind her
	cam_root.global_position = player.global_position + Vector3(0, CAM_PIVOT_H, 0)
	room_cam = Camera3D.new()
	room_cam.fov = 42.0
	add_child(room_cam)
	cam.current = true


# ------------------------------------------------------------------ lighting

func setup_lights() -> void:
	sun = DirectionalLight3D.new()
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 70.0
	# (round 21, the user: shadows not as dark, their edges somewhat fuzzy: the sun given a size, so the
	# edges soften the further they fall from what casts them, and the shadows let some light through;
	# --shadows=opacity,size°,blur tries other values in a test picture)
	var sh := [SHADOW_OPACITY, SUN_SIZE, SHADOW_BLUR]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shadows="):
			var v := a.substr(10).split(",")
			for i in mini(v.size(), 3):
				sh[i] = float(v[i])
	shadow_day = sh[0]
	sun_size = sh[1]
	shadow_blur = sh[2]
	sun.light_angular_distance = sh[1]
	sun.shadow_blur = sh[2]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shadowbias="):               # (tests: bias, normal bias)
			var b := a.substr(13).split(",")
			sun.shadow_bias = float(b[0])
			sun.shadow_normal_bias = float(b[1])
		if a.begins_with("--shadowmap="):                # (tests: atlas size, filter quality 0-5)
			var v := a.substr(12).split(",")
			RenderingServer.directional_shadow_atlas_set_size(int(v[0]), true)
			if v.size() > 1:
				RenderingServer.directional_soft_shadow_filter_set_quality(int(v[1]) as RenderingServer.ShadowQuality)
	sun.light_volumetric_fog_energy = 1.6
	outdoor.add_child(sun)
	bounce = DirectionalLight3D.new()
	bounce.light_color = Color(1.0, 0.72, 0.5)
	bounce.light_specular = 0.0
	bounce.light_volumetric_fog_energy = 0.0
	outdoor.add_child(bounce)

	sky_mat = ProceduralSkyMaterial.new()
	night_sky = ShaderMaterial.new()
	night_sky.shader = load("res://shaders/night_sky.gdshader")
	sky = Sky.new()
	sky.sky_material = sky_mat
	# (round 26, the user: "The dappled light in the forest is flickering from one moment to the next", and Sandra's
	# shadow) the sky lights the whole scene (the soft fill in the shade), and it was being remade every second frame
	# as aim_sun() moved the sun in the sky's shader: that light shifted in little steps many times a second. The
	# sky's sun now moves only with the rest of its light, twice a second (apply_light); the sun's light and the
	# shadows still turn every second frame. Measured with --flickermeter --floor: 0.57% of the picture changing each
	# frame in the hill wood, 0.05% now. --skyold: as before.
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--skymode="):              # (for measuring: 0 automatic, 1 quality, 2 incremental, 3 realtime)
			sky.process_mode = int(a.trim_prefix("--skymode=")) as Sky.ProcessMode
	env_out = Environment.new()
	env_out.background_mode = Environment.BG_SKY
	env_out.sky = sky
	env_out.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env_out.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env_out.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env_out.tonemap_white = 6.0
	env_out.sdfgi_enabled = false            # G: light bouncing off the façades (costs ~10 fps on an M1)
	env_out.ssil_enabled = true              # cheaper bounce light from what's on screen
	env_out.ssil_intensity = 0.8
	env_out.sdfgi_cascades = 4
	# (round 41, rule 02 #5f, the user picked it for speed: "Both options 1 and 2") no soft shade out of doors — about
	# a tenth faster, corners a touch lighter; rooms keep theirs
	env_out.ssao_enabled = false
	env_out.ssao_radius = 1.0
	env_out.ssao_intensity = 1.8
	env_out.glow_enabled = true
	env_out.glow_intensity = 0.6
	env_out.glow_bloom = 0.08
	env_out.glow_hdr_threshold = 1.0
	env_out.adjustment_enabled = true
	env_out.adjustment_saturation = 1.12
	env_out.adjustment_contrast = 1.05
	# Distance fades to the sky; the streets themselves stay clear.
	env_out.fog_enabled = true
	env_out.fog_mode = Environment.FOG_MODE_DEPTH
	# (round 26: the far country past the ground grid, world2d.py FarLand, shows as soft hills in the haze before the
	# fog takes them: the fog reaches further, so the land fades out instead of ending)
	env_out.fog_depth_begin = 110.0
	env_out.fog_depth_end = 900.0
	env_out.fog_depth_curve = 1.3
	env_out.fog_density = 0.6
	env_out.fog_aerial_perspective = 0.75
	# A very thin haze that only shows where sunlight cuts through it (light shafts).
	env_out.volumetric_fog_enabled = true
	env_out.volumetric_fog_albedo = Color(1, 1, 1)
	env_out.volumetric_fog_anisotropy = 0.8
	env_out.volumetric_fog_length = 40.0

	env_in = Environment.new()
	env_in.background_mode = Environment.BG_COLOR
	env_in.background_color = Color(0.11, 0.085, 0.07)
	env_in.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env_in.ambient_light_color = Color(1.0, 0.88, 0.74)
	env_in.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env_in.ssao_enabled = true
	env_in.ssao_radius = 0.9
	env_in.ssao_intensity = 2.4
	env_in.ssil_enabled = true
	env_in.ssil_radius = 3.0
	env_in.glow_enabled = true
	env_in.glow_hdr_threshold = 1.1
	env_in.adjustment_enabled = true
	env_in.adjustment_saturation = 1.08

	world_env = WorldEnvironment.new()
	world_env.environment = env_out
	add_child(world_env)

	for l in D.lamps:
		var o := OmniLight3D.new()
		o.position = Vector3(l.light[0], l.light[1] + 0.14, l.light[2])     # (in the middle of the lantern's glass)
		o.light_color = Color(1.0, 0.8, 0.56)
		o.omni_range = 20.0                    # a long, soft reach, so the pools of light join up
		o.omni_attenuation = 1.1
		o.light_volumetric_fog_energy = 0.0
		o.distance_fade_enabled = true          # there are many; the far ones fade out
		o.distance_fade_begin = 70.0
		o.distance_fade_length = 25.0
		outdoor.add_child(o)
		lamp_lights.append(o)
	door_light = OmniLight3D.new()
	door_light.position = Vector3(D.door.lamp[0], D.door.lamp[1], D.door.lamp[2])
	door_light.light_color = Color(1.0, 0.74, 0.46)
	door_light.omni_range = 7.0
	door_light.light_volumetric_fog_energy = 0.0
	outdoor.add_child(door_light)

	# each room's lights, under a node of its own that is shown only while Sandra is in that room
	for rid in D.interiors:
		var R: Dictionary = D.interiors[rid]
		var IL: Dictionary = R.lights
		var holder := Node3D.new()
		holder.visible = false
		indoor.add_child(holder)
		room_lights[rid] = holder
		var cl := OmniLight3D.new()
		cl.position = Vector3(IL.ceiling[0], IL.ceiling[1], IL.ceiling[2])
		cl.light_color = Color(1.0, 0.86, 0.68)
		cl.omni_range = 12.0 * maxf(1.0, maxf(R.w / 14.0, R.h / 10.0)) * (1.6 if R.wall_h > 4.0 else 1.0)
		cl.omni_attenuation = 0.8
		holder.add_child(cl)
		ceiling_lights.append(cl)
		for wp in IL.windows:
			var wl := OmniLight3D.new()
			wl.position = Vector3(wp[0], wp[1], wp[2])
			wl.omni_range = 7.0
			wl.omni_attenuation = 1.2
			holder.add_child(wl)
			window_lights.append(wl)
		for tl in IL.get("tinted", []):
			# coloured light from the stained glass (the Sagrada Família): x, y, z, r, g, b, energy, range
			var ol := OmniLight3D.new()
			ol.position = Vector3(tl[0], tl[1], tl[2])
			ol.light_color = Color(tl[3], tl[4], tl[5])
			ol.light_energy = tl[6]
			ol.omni_range = tl[7]
			ol.omni_attenuation = 0.9
			holder.add_child(ol)
		var beam_shader := load("res://shaders/light_beam.gdshader") as Shader
		for bd in IL.get("beams", []):
			# a soft cone of light from the window, and (for the lower windows) a pool of coloured light where it lands
			var d := Vector3(bd.d[0], bd.d[1], bd.d[2]).normalized()
			var cyl := CylinderMesh.new()
			cyl.height = bd.len
			cyl.top_radius = bd.r0
			cyl.bottom_radius = bd.r1
			cyl.radial_segments = 16
			cyl.rings = 1
			cyl.cap_top = false
			cyl.cap_bottom = false
			var bm := ShaderMaterial.new()
			bm.shader = beam_shader
			bm.set_shader_parameter("colour", Color(bd.col[0], bd.col[1], bd.col[2]))
			var mi := MeshInstance3D.new()
			mi.mesh = cyl
			mi.material_override = bm
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			var yax := -d                                   # the cylinder's top (+y) at the window
			var xax := yax.cross(Vector3.FORWARD if absf(yax.z) < 0.9 else Vector3.RIGHT).normalized()
			mi.transform = Transform3D(Basis(xax, yax, xax.cross(yax)), Vector3(bd.p[0], bd.p[1], bd.p[2]) + d * bd.len / 2.0)
			holder.add_child(mi)
			var sp: SpotLight3D = null
			if bd.spot:
				sp = SpotLight3D.new()
				sp.position = Vector3(bd.p[0], bd.p[1], bd.p[2])
				sp.look_at_from_position(sp.position, sp.position + d, Vector3.UP if absf(d.y) < 0.95 else Vector3.RIGHT)
				sp.light_color = Color(bd.col[0], bd.col[1], bd.col[2])
				sp.spot_range = bd.len + 6.0
				sp.spot_angle = rad_to_deg(atan2(bd.r1 * 1.6, bd.len)) + 4.0
				sp.spot_attenuation = 0.6
				sp.spot_angle_attenuation = 1.6
				sp.light_volumetric_fog_energy = 0.0
				holder.add_child(sp)
			sun_beams.append({"mat": bm, "mesh": mi, "spot": sp, "side": bd.side})
		for lp in IL.lamps:
			var fl := OmniLight3D.new()
			fl.position = Vector3(lp[0], lp[1], lp[2])
			fl.light_color = Color(1.0, 0.8, 0.55)
			fl.omni_range = 6.0
			holder.add_child(fl)
			room_lamps.append(fl)


func build_door_glows() -> void:
	# a soft glow round every door that can be entered, so they stand out from the rest
	var shader := load("res://shaders/door_glow.gdshader") as Shader
	for d in D.get("entrances", [D.door]):
		var size: Array = d.get("size", [1.24, 2.24])
		var mat := ShaderMaterial.new()
		mat.shader = shader
		mat.set_shader_parameter("opening", Vector2(size[0], size[1]))
		# (round 33, the user: "the actual door should be glowing!!") a narrow halo, the door itself lit
		mat.set_shader_parameter("card", Vector2(size[0] + 0.6, size[1] + 0.6))
		mat.set_shader_parameter("reach", 0.12)
		mat.set_shader_parameter("arch", float(d.get("arch", 0.0)))      # (round 33: arched doors glow arched)
		var quad := QuadMesh.new()
		quad.size = Vector2(size[0] + 0.6, size[1] + 0.6)
		var mi := MeshInstance3D.new()
		mi.mesh = quad
		mi.material_override = mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		outdoor.add_child(mi)
		var n := Vector3(d.normal[0], 0, d.normal[1])
		# (round 33: on the wall itself where the build found it — 'glow' — else just proud of the door's point)
		var at: Array = d.get("glow", d.pos)
		mi.position = Vector3(at[0], d.get("base", 0.12) + size[1] / 2.0, at[1]) + n * (0.0 if d.has("glow") else 0.2)
		mi.rotation.y = atan2(n.x, n.z)
		if d.has("glow_c"):
			# (round 33, the user: the cellar's "two wooden doors on the ground… make the glow match their angle") a door
			# lying on a slope: the glow on its face, leaned back from upright by 'lean' (radians)
			mi.position = Vector3(d.glow_c[0], d.glow_c[1], d.glow_c[2])
			mi.rotation.x = -float(d.get("lean", 0.0))
		door_glows.append({"mat": mat, "pos": Vector3(d.pos[0], 0, d.pos[1]), "level": 0.0})
	# (the buildings' names are on the map, M, and on the brass plaque by each door, not floating in the street)


func update_door_glows(dt: float) -> void:
	# steady, brightening a little as Sandra comes near
	for g in door_glows:
		var near := clampf(1.0 - (g.pos.distance_to(player.global_position) - 2.0) / 10.0, 0.0, 1.0)
		g.level = lerpf(g.level, near, 1.0 - exp(-3.0 * dt))
		g.mat.set_shader_parameter("strength", (0.42 + 0.18 * g.level) if P.night else (0.5 + 0.25 * g.level))


func update_sun_beams() -> void:
	# the Nativity side's glass catches the morning sun, the Passion side's the evening's; the lantern
	# and the apse shine all day. Soft, so they glow rather than glare.
	var m: float = fmod(float(game.S.time), 1440.0) if game else 720.0
	var day := smoothstep(360.0, 480.0, m) * (1.0 - smoothstep(1170.0, 1260.0, m))
	var east := smoothstep(330.0, 450.0, m) * (1.0 - smoothstep(840.0, 960.0, m))
	var west := smoothstep(720.0, 840.0, m) * (1.0 - smoothstep(1170.0, 1260.0, m))
	for b in sun_beams:
		var k: float = day if b.side == "day" else 0.3 * day + 0.7 * (east if b.side == "east" else west)
		b.mat.set_shader_parameter("strength", 0.16 * k)
		b.mesh.visible = k > 0.02
		if b.spot:
			b.spot.light_energy = 2.4 * k
			b.spot.visible = k > 0.02


func set_quality(high: bool) -> void:
	# Q switches between the full look and a lighter one for smoother movement on the M1
	high_quality = high
	env_out.ssil_enabled = high
	env_out.volumetric_fog_enabled = high      # the light shafts are the single biggest cost (~100 fps on the M1)
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS if high else DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
	# (round 37, the user: "shadow line that moves when she moves (see clearly on the bike)": the shadows stopped 45 m
	# ahead, fading over their last 11 m, an edge that slid along the promenade with her; now they reach 85 m and fade
	# over the last 40, too gradual to see; measured: no frame-rate cost on the promenade)
	sun.directional_shadow_max_distance = 100.0 if high else 85.0
	# (round 23, the user: "the shadows flicker on the buildings") the shadow map's near and far parts blend into each
	# other instead of switching over at a line that moves with the camera
	sun.directional_shadow_blend_splits = true
	sun.directional_shadow_fade_start = 0.55
	# (round 26, the user: "Sandra's shadow is flickering") the fine map near the camera reached only 4.5 m (Godot's
	# 10% of 45 m), right where she stands with the camera 4.3 m behind her (6.5 m on the bike): her shadow kept
	# crossing between the fine map and the coarse one. Now the fine one reaches past her.
	sun.directional_shadow_split_1 = 0.06 if high else 0.16      # (round 37: the fine map near her still 6 m / 13.6 m)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--split1="):
			sun.directional_shadow_split_1 = float(a.trim_prefix("--split1="))
	sun.directional_shadow_split_2 = 0.2
	sun.directional_shadow_split_3 = 0.5
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shadowdist="):                 # (tests: max distance, fade start)
			var v := a.substr(13).split(",")
			sun.directional_shadow_max_distance = float(v[0])
			if v.size() > 1:
				sun.directional_shadow_fade_start = float(v[1])
	# (round 22: with the sun turning every frame, a softer edge hides the shadow map's little steps as a shadow
	# glides; the full look gets the finer map too, which costs about a third of the frame rate)
	if not Array(OS.get_cmdline_user_args()).any(func(a): return String(a).begins_with("--shadowmap=")):
		RenderingServer.directional_shadow_atlas_set_size(8192 if high else 4096, true)
		RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_SOFT_HIGH if high else RenderingServer.SHADOW_QUALITY_SOFT_MEDIUM)
	get_viewport().msaa_3d = Viewport.MSAA_2X if high else Viewport.MSAA_DISABLED
	get_viewport().screen_space_aa = Viewport.SCREEN_SPACE_AA_DISABLED if high else Viewport.SCREEN_SPACE_AA_FXAA
	# (round 41, the user: "the railings on the building, funny flicker to them when I cycle along… could you do any sort
	# of interlace blur?") temporal smoothing: each frame blended with the last, so thin iron bars no longer shimmer as
	# the camera moves; both looks (--notaa: without, to compare)
	get_viewport().use_taa = not "--notaa" in OS.get_cmdline_user_args()
	# (round 41, rule 02 #5d, the user chose it: "do your best for Windows") the lowered picture is scaled up by Apple's
	# MetalFX on a Mac (railings whole and steady, measured) and by AMD's FSR 2 elsewhere (not seen here: no Windows);
	# both smooth over time by themselves, so the separate smoothing and FXAA are off with them.
	# (tests: --upscaler=fsr|fsr2|mfx|mfxs tries another; --fixscale=<s> holds the render scale)
	var mac := OS.get_name() == "macOS" and RenderingServer.get_current_rendering_driver_name() == "metal"
	scale_mode = Viewport.SCALING_3D_MODE_METALFX_TEMPORAL if mac else Viewport.SCALING_3D_MODE_FSR2
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--upscaler="):
			scale_mode = {"fsr": Viewport.SCALING_3D_MODE_FSR, "fsr2": Viewport.SCALING_3D_MODE_FSR2,
				"mfx": Viewport.SCALING_3D_MODE_METALFX_TEMPORAL, "mfxs": Viewport.SCALING_3D_MODE_METALFX_SPATIAL}[a.substr(11)]
	var temporal := scale_mode in [Viewport.SCALING_3D_MODE_FSR2, Viewport.SCALING_3D_MODE_METALFX_TEMPORAL]
	if temporal:
		get_viewport().use_taa = false
		get_viewport().screen_space_aa = Viewport.SCREEN_SPACE_AA_DISABLED
	get_viewport().scaling_3d_mode = scale_mode
	# (FSR 2 without its extra sharpening: measured riding past balconies, its fine shimmer drops by a sixth)
	get_viewport().fsr_sharpness = 2.0 if scale_mode == Viewport.SCALING_3D_MODE_FSR2 else 0.2
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--fixscale="):
			get_viewport().scaling_3d_scale = float(a.substr(11))
		if a.begins_with("--fsrsharp="):
			get_viewport().fsr_sharpness = float(a.substr(11))


func apply_preset(pname: String) -> void:
	# a fixed look (the tests use these); the game's own light follows the clock
	clock_light = false
	preset = pname
	apply_light(look_at_time(PRESET_TIME[pname]), PRESET_TIME[pname])


func light_from_clock() -> void:
	var mm: float = fmod(float(game.S.time) if game else 460.0, 1440.0)
	apply_light(look_at_time(mm), mm)


func look_at_time(mm: float) -> Dictionary:
	for i in LOOK_KEYS.size() - 1:
		var a: Array = LOOK_KEYS[i]
		var b: Array = LOOK_KEYS[i + 1]
		if mm >= a[0] and mm <= b[0]:
			var k: float = (mm - a[0]) / maxf(1.0, b[0] - a[0])
			preset = b[1] if k > 0.5 else a[1]
			return blend_looks(PRESETS[a[1]], PRESETS[b[1]], smoothstep(0.0, 1.0, k))
	return PRESETS.night


func blend_looks(A: Dictionary, B: Dictionary, k: float) -> Dictionary:
	if A == B or k <= 0.0:
		return A.duplicate()
	var out := {}
	for key in A.keys() + B.keys():
		var a = A.get(key, B.get(key))
		var b = B.get(key, A.get(key))
		if a is Color:
			out[key] = a.lerp(b, k)
		elif a is float or a is int:
			out[key] = lerpf(a, b, k)
		else:
			out[key] = b if k > 0.5 else a
	return out


func compass(bearing: float, el: float) -> Vector3:
	# a direction in the sky from its compass bearing (0 north, 90 east) and height, in degrees
	var b := deg_to_rad(bearing)
	var e := deg_to_rad(el)
	return Vector3(cos(e) * sin(b), sin(e), -cos(e) * cos(b))


func sky_positions(mm: float) -> Dictionary:
	# a Barcelona summer day: the sun comes up over the sea in the east-north-east at half past six, stands
	# in the south at two, and goes down in the west-north-west at half past nine; then the full moon,
	# opposite, comes up in the east-south-east and crosses the south during the night
	var day_f := (mm - SUNRISE) / (SUNSET - SUNRISE)
	var night_len := 1440.0 - (SUNSET - SUNRISE)
	var night_f := fposmod(mm - SUNSET, 1440.0) / night_len
	var sun_el := 0.0
	var moon_el := 0.0
	if day_f >= 0.0 and day_f <= 1.0:
		sun_el = 62.0 * sin(PI * day_f)
		moon_el = -sun_el
	else:
		moon_el = 50.0 * sin(PI * night_f)
		sun_el = -moon_el
	var sun_b := 70.0 + 220.0 * clampf(day_f, -0.1, 1.1)
	var moon_b := 110.0 + 140.0 * clampf(night_f, -0.1, 1.1)
	return {"sun": compass(sun_b, sun_el), "sun_el": sun_el, "moon": compass(moon_b, moon_el), "moon_el": moon_el,
		"moon_b": moon_b}


var SKY_STEADY := not "--skyold" in OS.get_cmdline_user_args()
var SUN_EVERY: int = (func():
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--sunevery="):
			return int(a.trim_prefix("--sunevery="))
	return 2).call()                                 # frames between turns of the sun (the user's wish: every second frame)


func aim_sun(mm: float) -> void:
	# the light's direction, from the clock to the second (round 22, the user: shadows moved across the ground in
	# little jumps; the light was turned only twice a second, with the rest of the light; now every frame)
	var sp := sky_positions(mm)
	if sp.sun_el > 0.0:
		sun_dir = sp.sun
	else:
		sun_dir = compass(sp.moon_b, maxf(maxf(sp.moon_el, 0.0), 55.0))   # (moonlight from higher than the moon: short, soft shadows, not whole streets in shade)
	sun.transform = Transform3D(Basis.looking_at(-sun_dir, Vector3.UP), Vector3.ZERO)
	if not SKY_STEADY:                                 # (round 26: the sky's own sun and moon only with the rest of its light)
		night_sky.set_shader_parameter("sun_dir", sp.sun)
		night_sky.set_shader_parameter("moon_dir", sp.moon)


func apply_light(look: Dictionary, mm: float) -> void:
	P = look
	var nk: float = P.nk
	P.night = nk > 0.5
	var sp := sky_positions(mm)
	# one light: the sun by day, the moon by night; at sunrise and sunset, when either is on the horizon,
	# it has faded right down, so the swap from one to the other can't be seen
	var by_sun: bool = sp.sun_el > 0.0
	var el: float = sp.sun_el if by_sun else maxf(sp.moon_el, 0.0)
	var fade_in := smoothstep(0.0, 4.0, el)
	aim_sun(mm)
	# (before sunrise and after sunset it is the moon's pale light, coming in as the red goes)
	sun.light_color = P.sun if by_sun else PRESETS.night.sun
	sun.light_energy = (P.sun_e if by_sun else PRESETS.night.sun_e * smoothstep(0.4, 0.95, nk)) * fade_in
	sun.visible = fade_in > 0.01
	# (round 22, the user: soft moon shadows: the moon casts them too, fainter and with softer edges)
	sun.shadow_enabled = by_sun or not "--nomoonshadow" in OS.get_cmdline_user_args()
	sun.light_angular_distance = sun_size if by_sun else MOON_SOFT
	sun.shadow_blur = shadow_blur if by_sun else MOON_BLUR
	var opposite := Vector3(-sun_dir.x, 0.35, -sun_dir.z).normalized()
	bounce.transform = Transform3D(Basis.looking_at(-opposite, Vector3.UP), Vector3.ZERO)
	bounce.light_energy = P.sun_e * 0.22 * fade_in
	# the sky: one shader for day and night, blended (no cut at dusk)
	night_sky.set_shader_parameter("top_color", P.top)
	night_sky.set_shader_parameter("horizon_color", P.hor)
	night_sky.set_shader_parameter("glow_color", P.glow)
	night_sky.set_shader_parameter("sun_dir", sp.sun)
	night_sky.set_shader_parameter("sun_color", P.sun)
	night_sky.set_shader_parameter("moon_dir", sp.moon)
	night_sky.set_shader_parameter("night", nk)
	# (the distance haze: its own grey by day, the night horizon's dark blue by night; the grey over a night sky
	# washed it out to a dull grey-blue)
	sky.sky_material = night_sky
	env_out.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env_out.ambient_light_color = P.fill
	env_out.ambient_light_sky_contribution = P.sky_mix
	env_out.ambient_light_energy = P.amb
	env_out.tonemap_exposure = P.exposure
	env_out.glow_hdr_threshold = P.glow_from
	env_out.volumetric_fog_density = P.shafts
	sun.shadow_opacity = shadow_day if by_sun else MOON_SHADOW * shadow_day
	var lamps := smoothstep(0.15, 0.6, nk)            # the street lamps come on as the red light goes
	if nk > 0.5:
		# the lamps' warm glow thrown up onto the façades and under the balconies
		var up := Vector3(-sun_dir.x, -0.45, -sun_dir.z).normalized()
		bounce.transform = Transform3D(Basis.looking_at(-up, Vector3.UP), Vector3.ZERO)
		bounce.light_color = Color(1.0, 0.68, 0.42)
		bounce.light_energy = 0.07 * lamps
	else:
		bounce.light_color = Color(1.0, 0.72, 0.5)
	var night: bool = P.night
	# windows lit from inside at night: a soft, low glow behind curtains, not a bright view into the rooms
	set_emit("GlassLit", Color(1.0, 0.7, 0.42), 0.75 * lamps)
	set_emit("ShopGlass", Color(1.0, 0.72, 0.42), 0.28 * lamps)   # shop windows left lit after closing
	set_emit("PharmacyCross", Color(0.2, 1.0, 0.4), lerpf(0.35, 1.4, lamps))
	# the Sagrada Família: its cross and star lit at night; inside, the light through its glass and vaults
	set_emit("SagradaCross", Color(1.0, 0.98, 0.92), 1.2 * lamps)
	set_emit("SagradaStar", Color(1.0, 0.95, 0.8), lerpf(0.0, 1.1, lamps))
	set_emit("VaultLight", Color(1.0, 0.95, 0.82), 0.7 if night else 2.2)
	set_emit("DoorDaylight", Color(0.16, 0.2, 0.36) if night else Color(1.0, 0.95, 0.84), 0.6 if night else 2.4)   # (the day beyond its doors)
	update_sun_beams()
	for mn in mats:
		if String(mn).begins_with("Stained"):
			for m in mats[mn]:
				m.emission_enabled = true
				m.emission = m.albedo_color
				m.emission_energy_multiplier = 0.25 if night else 1.1
	for k in 4:
		set_emit("KitWindowLit%d" % k, Color(1.0, 0.78, 0.55), 0.8 * lamps)   # lamplight behind the glass
		set_emit("WinPicLit%d" % k, Color(1.0, 0.78, 0.55), 0.8 * lamps)
	set_emit("CrispGlassLit", Color(1.0, 0.76, 0.5), 0.7 * lamps)
	set_emit("LampGlass", Color(1.0, 0.88, 0.7), 2.6 * lamps)
	set_emit("HillLantern", Color(1.0, 0.8, 0.5), 3.2 * lamps)       # (round 24) the hill path's lanterns
	set_emit("FairyBulb", Color(1.0, 0.82, 0.52), 5.0 * lamps)         # (round 41) the fairy lights on the funfair's plaza
	set_emit("FuniGlowHoop", Color(0.86, 0.42, 1.0), lerpf(0.0, 2.25, lamps))   # (round 41) the funicular's glow-worm hoops (half as strong: the user, 4.5 → 2.25)
	set_emit("DoorLamp", Color(1.0, 0.82, 0.6), lerpf(0.2, 2.2, lamps))
	# the flat's windows: daylight outside, but not a glaring white
	set_emit("WindowSky", Color(0.1, 0.16, 0.3) if night else Color(0.85, 0.88, 0.9), 0.45 if night else 0.28)
	set_emit("LampShade", Color(1.0, 0.85, 0.63), 3.0 if night else 0.4)
	for o in lamp_lights:
		o.light_energy = 1.35 * lamps
		o.visible = lamps > 0.01
	if lamp_glass_mat:
		lamp_glass_mat.set_shader_parameter("glow", 3.0 * lamps)
		lamp_mat.next_pass = lamp_glass_mat if lamps > 0.01 else null
	for cl in ceiling_lights:
		cl.light_energy = 1.1 if night else 0.45
	for wl in window_lights:
		wl.light_color = Color(0.45, 0.55, 0.8) if night else Color(1.0, 0.93, 0.82)
		wl.light_energy = 0.15 if night else 0.5
	for fl in room_lamps:
		fl.light_energy = 1.8 if night else 0.9
	env_in.ambient_light_energy = 0.28 if night else 0.45


# ------------------------------------------------------------------ world queries

func poly_dist(poly: Array, x: float, z: float) -> float:
	var d := -INF
	var n := poly.size()
	for i in n:
		var a = poly[i]
		var b = poly[(i + 1) % n]
		var L := Vector2(b[0] - a[0], b[1] - a[1]).length()
		var nx: float = (b[1] - a[1]) / L
		var nz: float = -(b[0] - a[0]) / L
		d = maxf(d, (x - a[0]) * nx + (z - a[1]) * nz)
	return d


func build_ground_cells() -> void:
	# what raises the ground above the road, filed by 10 m cell so a lookup only checks what's near
	var add := func(x0: float, z0: float, x1: float, z1: float, e: Dictionary):
		for cx in range(floori(x0 / 10.0), floori(x1 / 10.0) + 1):
			for cz in range(floori(z0 / 10.0), floori(z1 / 10.0) + 1):
				var k := Vector2i(cx, cz)
				if not ground_cells.has(k):
					ground_cells[k] = []
				ground_cells[k].append(e)
	# (first, so they win over the pavement they stand on: the university's front steps, round 20d)
	for r in D.get("raised", []):
		add.call(r[0], r[1], r[2], r[3], {"k": "rect", "r": [r[0], r[1], r[2], r[3]], "h": r[4]})
	# (round 38, the user: the bike, Sandra, the passers-by and the café's customer sank into Gràcia's footpaths) paving
	# a world script lays over the hills on its own corners, 12 cm up for its kerb (north_build.py, scene 'paving': each
	# piece [x, z, h] x 4): stood on as it is drawn, not on the 1.65 m ground grid under it
	for q in D.get("paving", []):
		var qr := [minf(minf(q[0], q[3]), minf(q[6], q[9])), minf(minf(q[1], q[4]), minf(q[7], q[10])),
			maxf(maxf(q[0], q[3]), maxf(q[6], q[9])), maxf(maxf(q[1], q[4]), maxf(q[7], q[10]))]
		add.call(qr[0], qr[1], qr[2], qr[3], {"k": "quad", "q": q, "r": qr})
	for b in D.blocks:
		var x0 := INF
		var z0 := INF
		var x1 := -INF
		var z1 := -INF
		for q in b.pave:
			x0 = minf(x0, q[0])
			z0 = minf(z0, q[1])
			x1 = maxf(x1, q[0])
			z1 = maxf(z1, q[1])
		add.call(x0, z0, x1, z1, {"k": "poly", "poly": b.pave})
	for r in D.get("pave_rects", []):
		add.call(r[0], r[1], r[2], r[3], {"k": "rect", "r": r, "h": D.kerb})
	if D.has("bridge_rect"):
		var br: Array = D.bridge_rect
		add.call(br[0], br[1], br[2], br[3], {"k": "rect", "r": br, "h": 0.02})
	if D.has("steps"):
		var sr: Array = D.steps.rect
		add.call(sr[0], sr[1], sr[2], sr[3], {"k": "steps", "r": sr, "h": D.steps.top})


func ground_at(p: Vector3) -> float:
	if where != "out":
		return 0.0
	for e in ground_cells.get(Vector2i(floori(p.x / 10.0), floori(p.z / 10.0)), []):
		if e.k == "poly":
			if poly_dist(e.poly, p.x, p.z) < 0.0:
				return D.kerb
			continue
		var r: Array = e.r
		if p.x >= r[0] and p.x <= r[2] and p.z >= r[1] and p.z <= r[3]:
			if e.k == "quad":
				var hq := paving_h(e.q, p.x, p.z)
				if is_nan(hq):
					continue
				return hq
			return e.h if e.k == "rect" else e.h * (r[3] - p.z) / (r[3] - r[1])     # the steps climb northwards
	var cr: Array = D.get("city_rect", [-INF, -INF, INF, INF])
	if p.x >= cr[0] and p.x <= cr[2] and p.z >= cr[1] and p.z <= cr[3]:
		return 0.0
	return terrain_at(p.x, p.z)


func paving_h(q: Array, x: float, z: float) -> float:
	# a piece of paving's height (scene 'paving': [x, z, h] x 4, round it) at (x, z), NAN off it: the higher of its two
	# splits into triangles (it is drawn as one of them), so nothing stood on it is ever below its top
	var best := NAN
	for t in [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]]:
		var i0: int = t[0] * 3
		var i1: int = t[1] * 3
		var i2: int = t[2] * 3
		var bx: float = q[i1] - q[i0]
		var bz: float = q[i1 + 1] - q[i0 + 1]
		var cx: float = q[i2] - q[i0]
		var cz: float = q[i2 + 1] - q[i0 + 1]
		var det := bx * cz - bz * cx
		if absf(det) < 1e-6:
			continue
		var px: float = x - q[i0]
		var pz: float = z - q[i0 + 1]
		var u := (px * cz - pz * cx) / det
		var v := (bx * pz - bz * px) / det
		if u < -0.002 or v < -0.002 or u + v > 1.002:
			continue
		var h: float = q[i0 + 2] + u * (q[i1 + 2] - q[i0 + 2]) + v * (q[i2 + 2] - q[i0 + 2])
		if is_nan(best) or h > best:
			best = h
	return best


func bike_lift(p: Vector3) -> float:
	# (round 20) on the bike, a touch higher: the trodden paths, the meadow's paving and the grass stand a few
	# centimetres above the ground under them, and the tyres sank into them
	var cr: Array = D.get("city_rect", [-INF, -INF, INF, INF])
	return 0.02 if (p.x >= cr[0] and p.x <= cr[2] and p.z >= cr[1] and p.z <= cr[3]) else 0.055


func deck_at(x: float, z: float, cur: float) -> float:
	# (round 34) a roof she walks on with a walk under it — the covered walk's in Park Güell (scene 'decks': pieces of
	# paving, each a polygon and its height): she is on it if she is here and already up at its level (from the hill
	# behind it); under it, walking the lower walk, she isn't. NAN where there's none.
	if where != "out":
		return NAN
	for dk in D.get("decks", []):
		if cur > float(dk.h) - 1.2 and poly_dist(dk.p, x, z) < 0.0:
			return float(dk.h)
	return NAN


var _fit_q: PhysicsShapeQueryParameters3D


func person_fits(p: Vector3) -> bool:
	# (round 40, the user: "None of the people should be allowed to walk through walls"; rule 10 #16a) does a person, at
	# their full width (0.3 m round), stand clear of everything built here? Every move of anyone is checked with it.
	if _fit_q == null:
		_fit_q = PhysicsShapeQueryParameters3D.new()
		var sh := SphereShape3D.new()
		sh.radius = 0.3
		_fit_q.shape = sh
		_fit_q.collision_mask = LAYER_BODY
	_fit_q.transform = Transform3D(Basis(), Vector3(p.x, 0.6, p.z))
	for hit in get_world_3d().direct_space_state.intersect_shape(_fit_q, 8):
		# (people's own bodies, and moving things, are AnimatableBody3D — a kind of StaticBody3D, but not a wall)
		if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D and hit.collider != tree_body:
			return false
	return true


func deck_drops(x: float, z: float) -> bool:
	# (round 40, the calvary: "when you run to the side, you just fall off it as it's a normal object") a floor she may
	# step off, falling to the ground below, unlike the covered walk's roof
	for dk in D.get("decks", []):
		if dk.get("drop", false) and poly_dist(dk.p, x, z) < 0.6:
			return true
	return false


func rim_ahead(v: Vector2) -> bool:
	# (round 40, the calvary: "all the curved parts are solid") from the ground, a raised platform's side is a wall: the
	# part of her step that would take her in under its edge is lost, as against a wall; she goes up by its steps. True
	# when it changed her step (player.velocity is set here).
	if v.length() < 0.001:
		return false
	var pp := player.global_position
	for f in D.get("flats", []):
		if pp.x >= f[0] and pp.x <= f[2] and pp.z >= f[1] and pp.z <= f[3]:
			return false                              # (on its steps she walks up onto it)
	var vv := v
	for axis: Vector2 in [Vector2(1, 0), Vector2(0, 1)]:
		var part: Vector2 = axis * v.dot(axis)
		if part.length() < 0.001:
			continue
		var ahead: Vector2 = Vector2(pp.x, pp.z) + part.normalized() * 0.45
		for dk in D.get("decks", []):
			if dk.get("rim", false) and float(dk.h) - model.position.y > 0.5 and poly_dist(dk.p, ahead.x, ahead.y) < 0.0:
				vv -= part
				break
	if vv.is_equal_approx(v):
		return false
	player.velocity.x = vv.x
	player.velocity.z = vv.y
	return true


func terrain_at(x: float, z: float) -> float:
	# the hills, the beach and the forest floor: the height grid world2d.py made the ground from
	if not D.has("terrain"):
		return 0.0
	# (round 26, the user fell into the sand of Park Güell's square by its wall: the grid, 1.65 m apart, dips inside a
	# terrace's edge where the next sample is on the lawn below) the park's terraces, stairs and landings are level
	# or an even ramp, so they say their own height: [x0, z0, x1, z1, height at z0, height at z1]
	for f in D.get("flats", []):
		if x >= f[0] and x <= f[2] and z >= f[1] and z <= f[3]:
			return lerpf(f[4], f[5], (z - f[1]) / maxf(0.01, f[3] - f[1]))
	var tr: Dictionary = D.terrain
	# (round 35) along the hill path and the park's paths the ground is three times finer (world2d.py): a patch's own
	# grid, where there is one
	for tf in D.get("terrain_fine", []):
		var gx: float = (x - tf.x0) / tf.step
		var gz: float = (z - tf.z0) / tf.step
		if gx >= 0.0 and gz >= 0.0 and gx < float(tf.nx) - 1.0 and gz < float(tf.nz) - 1.0:
			tr = tf
			break
	var fx: float = (x - tr.x0) / tr.step
	var fz: float = (z - tr.z0) / tr.step
	var i := clampi(floori(fx), 0, int(tr.nx) - 2)
	var j := clampi(floori(fz), 0, int(tr.nz) - 2)
	var ax := clampf(fx - i, 0.0, 1.0)
	var az := clampf(fz - j, 0.0, 1.0)
	var H: Array = tr.h
	return lerpf(lerpf(H[j][i], H[j][i + 1], ax), lerpf(H[j + 1][i], H[j + 1][i + 1], ax), az)


func street_name(p: Vector3) -> String:
	for s in D.streets:
		var r = s.rect
		if p.x >= r[0] and p.x <= r[2] and p.z >= r[1] and p.z <= r[3]:
			return s.name
	return "L'Eixample"


# ------------------------------------------------------------------ UI

func panel_style(bg: Color, border: Color, left_only := false) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	if left_only:
		sb.border_width_left = 4
	else:
		sb.set_border_width_all(3)
		sb.set_corner_radius_all(8)
	sb.content_margin_left = 16
	sb.content_margin_right = 16
	sb.content_margin_top = 8
	sb.content_margin_bottom = 8
	return sb


var talk_fonts := {}


func talk_font(weight := 400) -> SystemFont:
	if not talk_fonts.has(weight):
		var f := SystemFont.new()
		f.font_names = PackedStringArray(["Helvetica Neue", "Helvetica", "Arial", "sans-serif"])
		f.font_weight = weight
		talk_fonts[weight] = f
	return talk_fonts[weight]


func make_label(size: int, col: Color) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	l.add_theme_constant_override("shadow_offset_y", 1)
	return l


var glare_k := 0.0               # how much the sun shines in, eased (eyes don't react in a single frame)
var glare_seen := 0.0            # whether the sun can be seen past the buildings, eased
var glare_mul := 1.0             # (round 38: the examples for the user, tests.gd run_glaremock)


func update_glare(dt: float) -> void:
	# looking towards the sun: its light floods the sky (night_sky.gdshader, round 38). Strongest straight at it, fading
	# over about 40 degrees; less as buildings, hills or trees cover it (five rays, so it fades as it slips
	# behind an edge rather than snapping off), none at night or indoors. High in the sky it is hard to look
	# at; low on the horizon it is dimmer and spread wide (round 20: it burst like an explosion at sunset)
	var want := 0.0
	var sd: Vector3 = night_sky.get_shader_parameter("sun_dir")
	sd = sd.normalized()
	var high := smoothstep(0.02, 0.45, sd.y)
	var c: Camera3D = get_viewport().get_camera_3d()
	if c and where == "out" and sd.y > -0.02 and float(P.get("nk", 0.0)) < 0.6:
		var fwd := -c.global_transform.basis.z
		var facing := smoothstep(0.5, 0.97, fwd.dot(sd))      # (round 23: a gentler, wider turn into the glare)
		if facing > 0.0:
			var side := sd.cross(Vector3.UP).normalized()
			var upv := side.cross(sd).normalized()
			var seen := 0.0
			for o: Vector2 in [Vector2.ZERO, Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]:
				var dir: Vector3 = (sd + (side * o.x + upv * o.y) * 0.035).normalized()
				var q := PhysicsRayQueryParameters3D.create(c.global_position, c.global_position + dir * 600.0, LAYER_BODY | LAYER_CAMERA)
				if get_world_3d().direct_space_state.intersect_ray(q).is_empty():
					seen += 0.2
			glare_seen = move_toward(glare_seen, seen, dt * 2.5)
			var low := smoothstep(-0.02, 0.06, sd.y)                       # (rising out of the sea, setting behind the hills)
			want = facing * glare_seen * low * lerpf(0.5, 1.0, high)
	glare_k = lerpf(glare_k, want, 1.0 - exp(-2.5 * dt))
	# (round 38: the sky shader draws it, on the sky alone; the trees and buildings in front are untouched)
	night_sky.set_shader_parameter("glare", glare_k * glare_mul if glare_k > 0.01 else 0.0)
	night_sky.set_shader_parameter("glare_high", high)
	var tint: Color = P.get("sun", Color(1, 0.92, 0.78))
	night_sky.set_shader_parameter("glare_tint", Vector3(lerpf(tint.r, 1.0, 0.3), lerpf(tint.g, 0.95, 0.3), lerpf(tint.b, 0.85, 0.3)))
	if c and glare_k > 0.01:
		var vs := get_viewport().get_visible_rect().size
		night_sky.set_shader_parameter("sun_uv", c.unproject_position(c.global_position + sd * 100.0) / vs)
		night_sky.set_shader_parameter("aspect", vs.x / vs.y)
		night_sky.set_shader_parameter("exposure", env_out.tonemap_exposure)
		night_sky.set_shader_parameter("white", env_out.tonemap_white)


func next_time_stop() -> void:
	# on to the next part of the day: morning, midday, evening, night (T, and the debug menu)
	var now: float = fmod(float(game.S.time), 1440.0)
	var next: float = T_STOPS[0] + 1440.0
	for st in T_STOPS:
		if st > now + 1.0:
			next = st
			break
	set_clock(fmod(next, 1440.0))
	last_banner = ""
	show_banner("%02d:%02d" % [int(game.S.time) / 60, int(game.S.time) % 60])


func toggle_music() -> void:
	last_banner = ""
	show_banner("♪  " + ambience.toggle_music())


func make_ui() -> void:
	var gl := CanvasLayer.new()                          # over the picture, under the HUD
	gl.layer = -1
	add_child(gl)
	var ui := CanvasLayer.new()
	add_child(ui)
	var cream := Color("#f6ecd8")
	banner_panel = PanelContainer.new()
	banner_panel.add_theme_stylebox_override("panel", panel_style(Color(0.16, 0.1, 0.07, 0.55), Color("#c46a45")))
	banner = make_label(19, cream)
	banner_panel.add_child(banner)
	ui.add_child(banner_panel)                        # the street's name, top middle
	stats = make_label(11, Color(1, 1, 1, 0.6))
	stats.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	ui.add_child(stats)
	help = make_label(16, Color(1, 1, 1, 0.88))
	help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	help.text = "WASD walk  ·  E talk / look / pick up  ·  I backpack  ·  J journal  ·  M map  ·  B bike  ·  H take me home  ·  Esc menu\n" + \
		"Click to steer with the mouse (click again or Esc frees it)  ·  wheel zoom" + ("  ·  P debug (outfit, music, time, quality…)" if debug_on else "")
	ui.add_child(help)
	prompt = make_label(19, cream)
	prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(prompt)
	hud_root = Control.new()
	hud_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(hud_root)
	var soft := panel_style(Color(0.16, 0.1, 0.07, 0.5), Color(0.77, 0.42, 0.27, 0.8))
	mission_panel = PanelContainer.new()
	mission_panel.add_theme_stylebox_override("panel", soft)
	hud = make_label(19, cream)
	mission_panel.add_child(hud)
	mission_panel.position = Vector2(18, 16)
	hud_root.add_child(mission_panel)
	clock_panel = PanelContainer.new()
	clock_panel.add_theme_stylebox_override("panel", soft)
	clock_label = make_label(19, cream)                # (the same size as the mission)
	clock_panel.add_child(clock_label)
	hud_root.add_child(clock_panel)
	money_panel = PanelContainer.new()
	money_panel.add_theme_stylebox_override("panel", soft)
	money_label = make_label(19, Color("#ffe6a8"))
	money_panel.add_child(money_label)
	hud_root.add_child(money_panel)
	# the 2D game's food card: small and quiet, faded beige and grey, the food's picture, its name, the time left
	boost_panel = PanelContainer.new()
	boost_panel.add_theme_stylebox_override("panel", panel_style(Color(0.12, 0.09, 0.07, 0.45), Color(0.6, 0.52, 0.44, 0.35)))
	boost_panel.modulate.a = 0.7
	var bh := HBoxContainer.new()
	bh.add_theme_constant_override("separation", 10)
	boost_icon = TextureRect.new()
	boost_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	boost_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	boost_icon.custom_minimum_size = Vector2(34, 34)
	bh.add_child(boost_icon)
	var bv := VBoxContainer.new()
	bv.add_theme_constant_override("separation", 0)
	boost_name = make_label(15, Color("#e8dcc8"))
	boost_left = make_label(13, Color("#bdb3a6"))
	bv.add_child(boost_name)
	bv.add_child(boost_left)
	bh.add_child(bv)
	boost_panel.add_child(bh)
	boost_panel.visible = false
	hud_root.add_child(boost_panel)
	toast_label = make_label(19, Color("#ffe6a8"))
	toast_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	toast_label.modulate.a = 0.0
	var top_layer := CanvasLayer.new()                   # (above the backpack and shop cards: "Bought: …" shows over them)
	top_layer.layer = 6
	add_child(top_layer)
	top_layer.add_child(toast_label)
	dlg_panel = PanelContainer.new()
	var dsb := panel_style(Color("#f6ecd8"), Color("#8a5d3b"))
	dsb.content_margin_left = 28
	dsb.content_margin_right = 28
	dsb.content_margin_top = 16
	dsb.content_margin_bottom = 18
	dsb.set_border_width_all(3)
	dlg_panel.add_theme_stylebox_override("panel", dsb)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	dlg_who = make_label(21, Color("#c46a45"))           # (bigger than the HUD on purpose; round 20: a little smaller)
	dlg_text = make_label(24, Color("#3b2a1e"))
	dlg_text.add_theme_font_override("font", talk_font())     # (an ordinary weight: the default face read as bold)
	dlg_who.add_theme_font_override("font", talk_font(600))
	dlg_text.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	dlg_who.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	dlg_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dlg_text.visible_characters_behavior = TextServer.VC_CHARS_AFTER_SHAPING     # (the box is its full size from the first letter)
	box.add_child(dlg_who)
	box.add_child(dlg_text)
	choice_box = VBoxContainer.new()
	choice_box.add_theme_constant_override("separation", 2)
	box.add_child(choice_box)
	dlg_panel.add_child(box)
	dlg_panel.visible = false
	ui.add_child(dlg_panel)
	# the map: the 2D game's own map picture (from2d/map3d.png, 8 pixels to a tile), Sandra a blinking dot
	map_panel = Control.new()
	map_panel.visible = false
	map_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var shade := ColorRect.new()
	shade.color = Color(0.1, 0.07, 0.05, 0.75)
	shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	map_panel.add_child(shade)
	map_tex = TextureRect.new()
	# the 3D world itself from above, painted up (tests.gd --mapshot, then shared/stylise_map.py); the
	# 2D game's pixel map only if that hasn't been made
	var img := Image.load_from_file(ProjectSettings.globalize_path(world_res("map/world.png")))
	if img and FileAccess.file_exists(world_res("map/world.json")):
		map_meta = JSON.parse_string(FileAccess.get_file_as_string(world_res("map/world.json")))
		map_tex.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		img.generate_mipmaps()
	else:
		img = Image.load_from_file(data_dir.path_join("map3d.png"))
		map_tex.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	if img:
		map_tex.texture = ImageTexture.create_from_image(img)
	map_tex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	map_panel.add_child(map_tex)
	if not map_meta.is_empty():
		make_map_labels()
	# the key, in a corner of the map
	map_legend = PanelContainer.new()
	var lsb := panel_style(Color(1.0, 0.973, 0.918, 0.94), Color("#8a5d3b"))
	lsb.content_margin_left = 12
	lsb.content_margin_right = 12
	lsb.content_margin_top = 8
	lsb.content_margin_bottom = 8
	map_legend.add_theme_stylebox_override("panel", lsb)
	var lv := VBoxContainer.new()
	lv.add_theme_constant_override("separation", 3)
	for row in [[Color(1.0, 0.2, 0.15), "You are here"], [DOT_COLS.landmark, "Landmark"], [DOT_COLS.shop, "Shop or café"],
			[DOT_COLS.flat, "Friends' flats"], [DOT_COLS.other, "Other doors"]]:
		var hb := HBoxContainer.new()
		hb.add_theme_constant_override("separation", 8)
		var sw := Panel.new()
		var ssb := StyleBoxFlat.new()
		ssb.bg_color = row[0]
		ssb.border_color = Color(1, 1, 1)
		ssb.set_border_width_all(2)
		ssb.set_corner_radius_all(16)
		sw.add_theme_stylebox_override("panel", ssb)
		sw.custom_minimum_size = Vector2(13, 13)
		sw.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		hb.add_child(sw)
		var ll := Label.new()
		ll.text = row[1]
		ll.add_theme_font_size_override("font_size", 14)
		ll.add_theme_color_override("font_color", Color("#3b2a1e"))
		hb.add_child(ll)
		lv.add_child(hb)
	map_legend.add_child(lv)
	map_panel.add_child(map_legend)
	map_dot = Panel.new()
	var dot_sb := StyleBoxFlat.new()
	dot_sb.bg_color = Color(1.0, 0.2, 0.15)
	dot_sb.border_color = Color(1, 1, 1)
	dot_sb.set_border_width_all(3)
	dot_sb.set_corner_radius_all(64)
	map_dot.add_theme_stylebox_override("panel", dot_sb)
	map_tex.add_child(map_dot)
	ui.add_child(map_panel)
	fade = ColorRect.new()
	fade.color = Color(0, 0, 0, 0)
	fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(fade)


func world_res(rel: String) -> String:
	# a file of the world being played, as a resource path: res://worlds/<name>/<rel>
	return "res://worlds/%s/%s" % [world_name, rel]


func map_px(x: float, z: float) -> Vector2:
	# a point of the world (metres) on the map picture (its pixels)
	if map_meta.is_empty():
		return Vector2(x / 3.3 + 55.0, z / 3.3 + 45.0) * 8.0
	# (round 24: the map is the city; up the hill or in Park Güell, she's in one of the round pictures above it)
	if z < float(map_meta.z0):
		for ins in map_meta.get("insets", []):
			var u := (x - float(ins.x0)) / float(ins.size_m)
			var v := (z - float(ins.z0)) / float(ins.size_m)
			if u >= 0.0 and u <= 1.0 and v >= 0.0 and v <= 1.0:
				var q := Vector2(u - 0.5, v - 0.5) * 2.0
				if q.length() > 0.92:
					q = q.normalized() * 0.92
				return Vector2(ins.cx, ins.cy) + q * float(ins.r)
	var off: Array = map_meta.get("off_px", [map_meta.border_px, map_meta.border_px])
	return Vector2(off[0] + (x - map_meta.x0) / map_meta.w_m * map_meta.map_px[0],
		off[1] + (clampf(z, map_meta.z0, INF) - map_meta.z0) / map_meta.h_m * map_meta.map_px[1])


func on_city_map(x: float, z: float) -> bool:
	# (round 24) inside the city's part of the map (not up the hill or in Gràcia: those are the round pictures)
	return map_meta.is_empty() or z >= float(map_meta.z0)


func make_map_labels() -> void:
	# the names on the map: every building that can be gone into (on its roof, by its door), the streets
	# along them, and the parts of town and country round about. Each has a few places it could go; the
	# first that doesn't cover a name already placed is used (place_map_labels), the most important first
	var T := 3.3
	for a in [["El Bosc", 97.0, 47.0], ["Platja de la Barceloneta", 30.0, 89.0],
			["Parc de la\nCiutadella", 72.5, 63.0], ["Passeig Marítim", 72.0, 85.6], ["Mar Mediterrània", 55.0, 94.0]]:
		var asp := [Vector2((a[1] - 55.0) * T, (a[2] - 45.0) * T)]
		for o in [Vector2(2.5, 1.5), Vector2(2.5, -1.5), Vector2(-1.5, 2.0), Vector2(3.0, 3.0)]:      # (a little way off, if need be)
			asp.append(asp[0] + o * T)
		add_map_label(a[0], asp, 0.0, "area")
	add_map_label("Riu Llobregat", [Vector2((2.0 - 55.0) * T, (40.0 - 45.0) * T)], -PI / 2.0, "area")
	add_street_labels(["Carrer de la Flor de Lliri", "La Rambla"], [])          # (her own street and the Rambla before the buildings' names)
	var seen := {}
	var doors := []
	for e in D.entrances:
		if not on_city_map(e.pos[0], e.pos[1]):
			continue                                      # (the round pictures are too small for names)
		var dk := door_kind(e)
		var dot := Panel.new()
		var dsb := StyleBoxFlat.new()
		dsb.bg_color = DOT_COLS[dk]
		dsb.border_color = Color(1, 1, 1)
		dsb.set_border_width_all(2)
		dsb.set_corner_radius_all(16)
		dot.add_theme_stylebox_override("panel", dsb)
		dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
		dot.size = Vector2(12, 12) if dk != "landmark" else Vector2(15, 15)
		map_tex.add_child(dot)
		map_dots.append({"node": dot, "pos": Vector2(e.pos[0], e.pos[1])})
		var key: String = e.get("id", e.name)
		if not seen.has(key):
			seen[key] = true
			doors.append(e)
	doors.sort_custom(func(a, b): return int(a.get("id", "") in MAP_LANDMARKS) > int(b.get("id", "") in MAP_LANDMARKS))
	for e in doors:
		var key: String = e.get("id", e.name)
		var n := Vector2(e.normal[0], e.normal[1])
		var side := Vector2(-n.y, n.x)
		var at := Vector2(e.pos[0], e.pos[1])
		var big: bool = key in ["sagrada", "mnac", "upf"]
		var spots := []
		for d in ([14.0, 9.0, 19.0] if big else [6.5, 3.5, 10.0]):
			for sd in [0.0, 6.0, -6.0]:
				spots.append(at - n * d + side * sd)
		for d in [5.0, 9.0, 14.0, 20.0, 27.0]:               # (and failing those, anywhere round its door)
			for a in 12:
				spots.append(at + Vector2(cos(a * TAU / 12.0), sin(a * TAU / 12.0)) * d)
		var nm: String = "Home" if key == "apt_sandra" else e.name
		# first choice: just above its dot, as in the 2D game's map; then the spots round about
		spots.push_front(at + Vector2(0, -7.0))
		spots.push_front(at + Vector2(0, -4.0))
		add_map_label(wrap_name(nm), spots, 0.0, "landmark" if key in MAP_LANDMARKS else "building", at)
	add_street_labels([], ["Carrer de la Flor de Lliri", "La Rambla"])


func door_kind(e: Dictionary) -> String:
	var id: String = e.get("id", "")
	if id in MAP_LANDMARKS and id != "apt_sandra":
		return "landmark"
	if id.begins_with("apt_"):
		return "flat"
	if game.data.SHOPS.has(e.get("int", "")) or id in ["cafe_berlin", "cafe_rambla", "carrefour", "torro_mar", "torro_joan", "bookshop"]:
		return "shop"
	return "other"


func add_street_labels(only: Array, skip: Array) -> void:
	for st in D.streets:
		if (not only.is_empty() and not st.name in only) or st.name in skip:
			continue
		if not on_city_map(st.rect[0], (st.rect[1] + st.rect[3]) / 2.0):
			continue                                      # (the round pictures are too small for names)
		var r: Array = st.rect
		var w: float = r[2] - r[0]
		var h: float = r[3] - r[1]
		var nm2: String = st.name
		if nm2 in ["El Bosc", "Platja de la Barceloneta", "Collserola", "Riu Llobregat", "Tibidabo", "Parc de la Ciutadella", "Passeig Marítim", "Jardí del Lliri"]:
			continue
		var spots2 := []
		for f in [0.5, 0.3, 0.7, 0.15, 0.85, 0.4, 0.6, 0.22, 0.78, 0.08, 0.92] if w < 60.0 or h < 60.0 and w < h else [0.22, 0.5, 0.78, 0.36, 0.64, 0.1, 0.9, 0.3, 0.7, 0.45, 0.55]:
			spots2.append(Vector2(r[0] + w * f, (r[1] + r[3]) / 2.0) if w > h else Vector2((r[0] + r[2]) / 2.0, r[1] + h * f))
		add_map_label(nm2, spots2, 0.0 if w > h else -PI / 2.0, "street")


const MAP_LANDMARKS := ["sagrada", "mnac", "upf", "casa_vicens", "casa_calvet", "palau_guell", "casa_mila", "casa_batllo", "apt_sandra"]


func wrap_name(nm: String) -> String:
	# long names on two lines, split at the space nearest the middle
	if nm.length() <= 14 or not " " in nm:
		return nm
	var best := -1
	for i in nm.length():
		if nm[i] == " " and (best < 0 or absi(i - nm.length() / 2) < absi(best - nm.length() / 2)):
			best = i
	return nm.substr(0, best) + "\n" + nm.substr(best + 1)


func add_map_label(text: String, spots: Array, rot: float, kind: String, dot = null) -> void:
	# names of buildings on a little cream card (clear against any roof or tree), streets in cream with a
	# dark outline along the road, the parts of the world in large italic
	var sizes := {"building": 15, "landmark": 17, "street": 13, "area": 21}
	var cols := {"building": Color("#3b2a1e"), "landmark": Color("#a8452f"), "street": Color("#fbf3e2"), "area": Color("#24402e")}
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", sizes[kind])
	l.add_theme_color_override("font_color", cols[kind])
	l.add_theme_constant_override("line_spacing", -3)
	if kind in ["building", "landmark"]:
		var chip := StyleBoxFlat.new()
		chip.bg_color = Color(1.0, 0.973, 0.918, 0.92)
		chip.border_color = Color(0.55, 0.36, 0.23, 0.55)
		chip.set_border_width_all(1)
		chip.set_corner_radius_all(5)
		chip.content_margin_left = 5
		chip.content_margin_right = 5
		chip.content_margin_top = 1
		chip.content_margin_bottom = 1
		l.add_theme_stylebox_override("normal", chip)
	else:
		l.add_theme_color_override("font_outline_color", Color("#2e2016") if kind == "street" else Color(0.98, 0.95, 0.88, 0.95))
		l.add_theme_constant_override("outline_size", 5 if kind == "street" else 7)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if kind in ["landmark", "area", "building"]:
		var f := SystemFont.new()
		f.font_names = PackedStringArray(["Georgia", "Times New Roman"]) if kind != "building" else PackedStringArray(["Helvetica Neue", "Arial"])
		f.font_weight = 700 if kind != "building" else 600
		f.font_italic = kind == "area"
		l.add_theme_font_override("font", f)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	map_tex.add_child(l)
	var lead: Line2D = null
	if dot != null:
		lead = Line2D.new()
		lead.width = 1.5
		lead.default_color = Color(0.36, 0.22, 0.13, 0.7)
		map_tex.add_child(lead)
		map_tex.move_child(lead, 0)
	map_labels.append({"node": l, "spots": spots, "rot": rot, "kind": kind, "dot": dot, "lead": lead})


var map_k := -1.0


func place_map_labels(k: float) -> void:
	# (again only when the map's size on screen changes)
	map_k = k
	var taken := []
	for d in map_dots:
		var dn: Panel = d.node
		var dc: Vector2 = map_px(d.pos.x, d.pos.y) * k
		dn.position = dc - dn.size / 2.0
		dn.move_to_front()
		taken.append(Rect2(dn.position, dn.size).grow(1.0))
	for ml in map_labels:
		var l: Label = ml.node
		l.size = l.get_combined_minimum_size()
		l.pivot_offset = l.size / 2.0
		l.rotation = ml.rot
		var ext: Vector2 = l.size if ml.rot == 0.0 else Vector2(l.size.y, l.size.x)
		var own: Vector2 = map_px(ml.dot.x, ml.dot.y) * k if ml.dot != null else Vector2(-9999, -9999)
		var chosen := -1
		for pass_ in 2:                                    # (second time round, it may sit over its own dot)
			for i in ml.spots.size():
				var c: Vector2 = map_px(ml.spots[i].x, ml.spots[i].y) * k
				var rc := Rect2(c - ext / 2.0, ext).grow(2.0)
				if not taken.any(func(o): return o.intersects(rc) and not (pass_ == 1 and o.has_point(own))):
					chosen = i
					break
			if chosen >= 0:
				break
		if chosen < 0 and testing:
			print("MAPLABEL no room: ", l.text.replace("\n", " "), " spots ", ml.spots.size())
		if chosen < 0 and ml.kind == "street":
			l.visible = false
			continue
		chosen = maxi(chosen, 0)
		var c2: Vector2 = map_px(ml.spots[chosen].x, ml.spots[chosen].y) * k
		l.visible = true
		l.position = c2 - l.size / 2.0
		taken.append(Rect2(c2 - ext / 2.0, ext).grow(2.0))
		if ml.lead != null:
			ml.lead.visible = true
			# a short line from the name to its door's dot, when it couldn't sit right by it
			var dp: Vector2 = map_px(ml.dot.x, ml.dot.y) * k
			var box := Rect2(l.position, l.size)
			var edge := Vector2(clampf(dp.x, box.position.x, box.end.x), clampf(dp.y, box.position.y, box.end.y))
			ml.lead.points = PackedVector2Array([dp, edge]) if dp.distance_to(edge) > 6.0 else PackedVector2Array()


func update_map() -> void:
	if not map_panel.visible or map_tex.texture == null:
		return
	var vs := play_area()
	map_panel.size = vs
	var ts: Vector2 = map_tex.texture.get_size()
	var k := minf((vs.x - 40.0) / ts.x, (vs.y - 40.0) / ts.y)
	map_tex.size = ts * k
	map_tex.position = (vs - map_tex.size) / 2.0
	map_legend.size = Vector2.ZERO
	var lw := map_legend.get_combined_minimum_size()
	if map_tex.position.x > lw.x + 24.0:
		map_legend.position = Vector2(map_tex.position.x - lw.x - 14.0, map_tex.position.y + map_tex.size.y - lw.y)     # (beside the map)
	else:
		map_legend.position = map_tex.position + Vector2(18.0, map_tex.size.y - lw.y - 18.0)
	if absf(k - map_k) > 0.0001:
		place_map_labels(k)
	# where she is (indoors: the door she came in by)
	var p := player.global_position
	if where == "in" and not room_door.is_empty():
		p = Vector3(room_door.pos[0], 0, room_door.pos[1])
	var r := 8.0 + 2.5 * sin(t * 5.0)                   # a gentle pulse
	map_dot.size = Vector2(r, r) * 2.0
	map_dot.position = map_px(p.x, p.z) * k - map_dot.size / 2.0
	map_dot.move_to_front()


func layout_ui() -> void:
	var vs := get_viewport().get_visible_rect().size
	stats.position = Vector2(vs.x - 420, 6)
	stats.size = Vector2(410, 30)
	help.position = Vector2(0, vs.y - 52)
	if touch_pad and touch_pad.deck > 0.0:
		help.position.y = -200.0                       # (upright there's no room for the help lines: the deck says it all)
		prompt.position = Vector2(0, vs.y - touch_pad.deck - 56)
	if touch_pad and not help.text.begins_with("Pad"):
		help.text = "Pad to walk  ·  A talk / look / pick up  ·  B back\nLOOK, then drag on the screen to look round  ·  BAG  MAP  LOG  BIKE  ☰ for the rest"
	help.size = Vector2(vs.x, 46)
	prompt.position = Vector2(0, vs.y - (54 if vf_on else 104))      # (in the viewfinder, below its frame, where the help was)
	prompt.size = Vector2(vs.x, 30)
	toast_label.position = Vector2(0, 120 if not panels.is_open() else 2)
	toast_label.size = Vector2(vs.x, 28)
	var maxw := minf(560.0, vs.x * 0.42) - 32.0
	hud.autowrap_mode = TextServer.AUTOWRAP_OFF
	hud.custom_minimum_size.x = 0.0
	if hud.get_combined_minimum_size().x > maxw:
		hud.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		hud.custom_minimum_size.x = maxw
	mission_panel.size = Vector2.ZERO
	clock_panel.size = Vector2.ZERO
	clock_panel.position = Vector2(18, vs.y - clock_panel.get_combined_minimum_size().y - 14)
	if touch_pad:
		clock_panel.position = Vector2(18, mission_panel.position.y + (mission_panel.get_combined_minimum_size().y + 10.0 if mission_panel.visible else 0.0))
	boost_panel.size = Vector2.ZERO
	boost_panel.position = Vector2(18, clock_panel.position.y - boost_panel.get_combined_minimum_size().y - 10)
	money_panel.size = Vector2.ZERO
	money_panel.position = Vector2(vs.x - money_panel.get_combined_minimum_size().x - 18, vs.y - money_panel.get_combined_minimum_size().y - 14)
	if touch_pad:
		money_panel.position = Vector2(vs.x - money_panel.get_combined_minimum_size().x - 18, 16 if touch_pad.deck > 0.0 else 44)
	banner_panel.size = Vector2.ZERO
	var bw := banner_panel.get_combined_minimum_size().x
	var bx := (vs.x - bw) / 2.0
	var mr := mission_panel.position.x + mission_panel.get_combined_minimum_size().x + 16.0
	if bx < mr:
		bx = minf(mr, vs.x - bw - 18.0)                   # (clear of a long mission line)
	banner_panel.position = Vector2(bx, 16 if bx >= mr or bx + bw < mission_panel.position.x else 16.0 + mission_panel.get_combined_minimum_size().y + 10.0)
	# the talk box: wide and low across the bottom, under the middle of the picture where Sandra is
	var w := minf(1040.0, vs.x * 0.82)
	if touch_pad:
		w = minf(w, vs.x - 2.0 * touch_pad.left_inset())          # (clear of the pad and A/B)
		if touch_pad.deck > 0.0:
			w = vs.x - 32.0                                     # (upright: the whole width, above the deck)
	dlg_text.custom_minimum_size.x = w - 56
	dlg_panel.size = Vector2(w, 0)
	dlg_panel.position = Vector2((vs.x - w) / 2.0, play_area().y - dlg_panel.size.y - 26)


func show_banner(text: String) -> void:
	if text == last_banner:
		return
	last_banner = text
	banner.text = text
	banner_panel.modulate.a = 1.0
	banner_timer = 3.5


func toast(text: String, secs := 2.4) -> void:
	# short notes at the top of the screen, one after another: money, things received, the journal
	# (round 41c, the user: five photos in quick succession, and "Photo saved to your Desktop" stayed up long after —
	# each had queued its own) the same note again only keeps the one showing up a little longer, never queues behind it
	if toast_t > 0.0 and toast_label.text == text:
		toast_t = maxf(toast_t, secs)
		return
	for e in toasts:
		if e[0] == text:
			return
	toasts.append([text, secs])


func update_toasts(dt: float) -> void:
	toast_t -= dt
	if toast_t <= 0.0:
		if toasts.is_empty():
			toast_label.modulate.a = move_toward(toast_label.modulate.a, 0.0, dt * 3.0)
			return
		var e: Array = toasts.pop_front()
		toast_label.text = e[0]
		toast_t = e[1]
	toast_label.modulate.a = move_toward(toast_label.modulate.a, 1.0, dt * 6.0)


func set_clock(minutes: float) -> void:
	game.S.time = minutes
	clock_light = true
	light_from_clock()


func show_dialog(who: String, pages: Array, choices: Array = [], on_choice := Callable(), on_close := Callable()) -> void:
	dlg_pages = pages.duplicate()
	dlg_choices = choices
	dlg_on_choice = on_choice
	dlg_on_close = on_close
	dlg_choice = 0
	dlg_who.text = who
	dlg_who.visible = who != ""
	dlg_text.text = dlg_pages[0]
	type_from_start()
	dlg_open = true
	dlg_panel.visible = true
	refresh_choices()


func refresh_choices() -> void:
	# the options appear under the last page; the selected one is marked
	for c in choice_box.get_children():
		c.queue_free()
	var show := dlg_pages.size() == 1 and not dlg_choices.is_empty()
	choice_box.visible = show
	if show:
		for i in dlg_choices.size():
			var l := make_label(22, Color("#c46a45") if i == dlg_choice else Color("#6b5240"))
			l.add_theme_font_override("font", talk_font(600 if i == dlg_choice else 400))
			l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
			l.text = ("▶  " if i == dlg_choice else "     ") + "%d. %s" % [i + 1, dlg_choices[i]]
			choice_box.add_child(l)
	dlg_panel.size = Vector2(dlg_panel.size.x, 0)


func move_choice(d: int) -> void:
	if choice_box.visible:
		ambience.sfx("tick")
		dlg_choice = wrapi(dlg_choice + d, 0, dlg_choices.size())
		refresh_choices()


func dialog_next() -> void:
	if choice_box.visible:
		ambience.sfx("select")
		var pick := dlg_choice
		var cb := dlg_on_choice
		close_dialog()
		if cb.is_valid():
			cb.call(pick)
		return
	if dlg_text.visible_characters >= 0:
		dlg_text.visible_characters = -1                  # (a press shows the whole line at once, as in the 2D game)
		return
	dlg_pages.pop_front()
	if dlg_pages.is_empty():
		var cb := dlg_on_close
		close_dialog()
		if cb.is_valid():
			cb.call()
	else:
		dlg_text.text = dlg_pages[0]
		type_from_start()
		refresh_choices()


func type_from_start() -> void:
	# the 2D game's typewriter: the words appear letter by letter (not in the tests, which press on at once)
	dlg_text.visible_characters = -1 if testing else 0
	type_t = 0.0


var type_t := 0.0
const TYPE_RATE := 60.0          # letters a second


func close_dialog() -> void:
	dlg_open = false
	dlg_panel.visible = false
	dlg_choices = []
	choice_box.visible = false
	face_target = INF


# ------------------------------------------------------------------ interaction and doors

func local_pos() -> Vector3:
	# in a room: from the room's own corner
	return player.global_position - (room_base(room) if where == "in" else Vector3.ZERO)


func nearest() -> Dictionary:
	var p := local_pos()
	var fwd := Vector2(sin(model.rotation.y), cos(model.rotation.y))
	var cands := []
	if where == "out" and street.riding:
		return {"x": p.x, "z": p.z, "r": 1.0, "label": "Get off the bike", "act": "dismount"}
	if where == "out":
		cands.append_array(street.candidates(p))
		cands.append_array(people.candidates(p))
		cands.append_array(npcs.candidates(p))
		cands.append_array(touches.candidates(p))
		cands.append_array(north.candidates(p))
		cands.append_array(benches.candidates(p))
		for e in D.entrances:
			# (round 41, the user: "I can go into the crypt while standing on the balcony above it") a door is offered
			# only to her standing at its own level, not on a terrace or porch over it
			if absf(model.position.y - float(e.get("base", model.position.y))) > 2.5:
				continue
			var n := Vector2(e.normal[0], e.normal[1])
			cands.append({"x": e.pos[0] + n.x * 0.4, "z": e.pos[1] + n.y * 0.4, "r": 1.3, "label": "Go into " + e.name, "act": "door", "e": e})
			if e.get("plaque", "") != "":
				var side: Vector2 = Vector2(-n.y, n.x) * (float(e.size[0]) / 2.0 + 0.45)
				var pp := Vector2(e.pos[0] + side.x + n.x * 0.3, e.pos[1] + side.y + n.y * 0.3)
				if e.has("plaque_pos"):
					pp = Vector2(e.plaque_pos[0], e.plaque_pos[1])          # (on its own post, out from deep stonework)
				cands.append({"x": pp.x, "z": pp.y, "r": 0.9, "label": "Read the plaque", "act": "plaque", "text": e.plaque, "bid": e.id})
		for pq in D.plaques:
			cands.append({"x": pq.pos[0], "z": pq.pos[1], "r": 1.5, "label": "Read the street sign", "act": "sign", "text": pq.text})
		for th in D.get("things2d", []):
			if th.type == "bench" and benches.near_bench(Vector2(th.pos[0], th.pos[1]), 1.6):
				continue                                   # (round 41: sat on, benches.gd)
			var label: String = {"bin": "Open the bin", "sign": "Read the sign", "fountain": "Look at the fountain", "terrace": "Look at the café",
				"bench": "Sit on the bench", "lampR": "Look at the lamp post"}.get(th.type, "Look")
			cands.append({"x": th.pos[0], "z": th.pos[1], "r": 1.6, "label": label, "act": "thing", "th": th})
		for g in game.ground:
			if g.node.visible:
				cands.append({"x": g.pos.x, "z": g.pos.z, "r": 1.2, "label": "Pick up: " + game.item(g.id).name, "act": "pick", "g": g})
	else:
		var R: Dictionary = D.interiors[room]
		var people_here: Array = npcs.candidates(p)
		var keeper_near := people_here.any(func(c): return Vector2(c.x - p.x, c.z - p.z).length() < c.r)
		# (round 42, the user: "I can't trigger the torró mission": a step back from Joan, E offered the counter, which
		# opens the shop and skips him) anywhere along a counter with its keeper behind it, E talks to the keeper
		var keeper := {}
		for c in people_here:
			if game.data.NPCS.get(c.who, {}).get("shop", false) or game.data.NPCS.get(c.who, {}).get("librarian", false):
				keeper = c
		for th in R.things:
			if keeper_near and th.kind in ["counter", "libdesk", "pfand"]:
				continue                                   # (talking to whoever is behind it does the same, and more)
			if not keeper.is_empty() and th.kind in ["counter", "libdesk"]:
				var reach_c: float = {"bed": 1.9, "desk": 1.75}.get(String(th.kind), 1.45)
				cands.append({"x": th.pos[0], "z": th.pos[1], "r": reach_c, "label": keeper.label, "act": "npc", "who": keeper.who})
				continue
			# (round 23: a bed or a desk is big; from in front of it, its middle is further off than a drawer's)
			var reach: float = {"bed": 1.9, "desk": 1.75, "kitchen": 1.7, "sofa": 1.7, "cupboard": 1.6}.get(String(th.kind), 1.45)
			cands.append({"x": th.pos[0], "z": th.pos[1], "r": reach, "label": thing_label(th), "act": "thing", "th": th})
		for st in R.stairs:
			cands.append({"x": st.pos[0], "z": st.pos[1], "r": 1.2, "label": "Go upstairs" if st.dir == "up" else "Go downstairs", "act": "stairs", "to": st.to,
				"lock": st.get("lock", "")})
		cands.append_array(people_here)
		cands.append_array(touches.room_candidates(room))
	var best := {}
	var bscore := INF
	for c in cands:
		var to := Vector2(c.x - p.x, c.z - p.z)
		var dd := to.length()
		if dd > c.r:
			continue
		# prefer what she is facing, so the prompt doesn't flicker between neighbours
		var score := dd - (fwd.dot(to.normalized()) * 0.6 if dd > 0.01 else 0.0)
		if c.act == "pick":
			score -= 0.8                               # things to pick up before the furniture (and counters)
		elif c.act == "npc":
			# people before the furniture — (round 35, the everything-visit) less so from further off: Ferran, 1.8 m away
			# behind his counter, took the prompt from Cafè Berlín's oven right in front of her, always
			# (and less when she isn't facing them: Empar beside her espresso machine took it as Sandra looked at it)
			var facing := fwd.dot(to.normalized()) if dd > 0.01 else 1.0
			score -= 0.8 * clampf((2.0 - dd) / 0.8, 0.0, 1.0) * (1.0 if facing > 0.5 else 0.3)
		if c.has("prio"):
			score -= float(c.prio)                    # (round 41c: a small thing at someone's feet, before them when faced)
		if c.act == "bike":
			# (round 32's play-through: hopped off beside Manolo, her own bike, right under her, won the prompt over
			# him — E rode away instead of talking. The parked bike gives way to whatever else is in reach.)
			score += 1.0
		if score < bscore:
			bscore = score
			best = c
	return best


func thing_label(th: Dictionary) -> String:
	if th.has("c"):
		return "Open the " + String(game.data.CONTAINERS[th.c].get("kind", "cupboard")).replace("bookshelf", "bookshelf").replace("library", "shelves")
	if th.get("sleep", false):
		return "Lie down"
	if th.get("card", false):
		return "Look at the desk"
	match th.kind:
		"phone": return "Use the phone"
		"pfand": return "Return bottles"
		"counter", "libdesk": return "At the counter"
	return "Look"


# (round 41, the user: "When she goes to take a picture… make it first person view so she can look around… a border
# around at the border of E, and outside of E, it's like 80% dark [then 70%]. And then in the middle… the little sort
# of circle with line through it that you get with cameras… in the corners… two lines that join up at a right angle…
# slightly in from the corner… the same light gray"; then "Z to zoom and E to take the picture… 50% in") the spare
# camera's viewfinder: at her eyes, as on a bench, the arrows and the mouse look round; E takes the photo, Z zooms,
# Esc puts the camera away.
const VF_ZOOM := 1.5             # Z: everything half as big again
const VF_DARK := 0.7             # outside the photo's frame
const VF_GREY := Color(1, 1, 1, 0.5)      # white at half strength (the user, after light grey)
const VF_LINE := 4.0             # every line the same thickness (the user: "the same thickness as… the angles"), px at 1280 wide
var vf_on := false
var vf_shutter := false         # (the shutter's own blackout, which mustn't put the camera away)
var vf_zoom := false
var vf_zoom_k := 0.0             # the zoom, eased
var vf_layer: CanvasLayer
var vf_cam: Camera3D             # the viewfinder's own camera, at her eyes
var vf_prev_cam: Camera3D        # the camera it took over from (the follow camera, a room's, a ride's), given back after
var vf_seen := true              # whether she was drawn before (on a bench her lap shows; in the funicular she's hidden)
var vf_yaw := 0.0
var vf_pitch := 0.0
const VF_EYE_UP := 0.1           # her eyes over her head bone's root
const VF_EYE_FWD := 0.12         # and in front of it (so her own face isn't in the way)


func viewfinder(on: bool) -> void:
	# (then: "add the camera feature on the rides and indoors… not on the bike… a warning message saying that I should get
	# off the bike first") its own camera at her eyes, wherever she is: on foot, on a bench, on a ride, in a room
	if on == vf_on:
		return
	if on and street and street.riding:
		toast("Get off the bike first to take a photo")
		ambience.sfx("nope")
		return
	vf_on = on
	vf_zoom = false
	if on:
		speed = 0.0
		# (round 41c, the user: "the photo in the gondola is weird": on a ride her body is parked at the car's floor or
		# its seat point and only the ride's camera sits at her eyes, so her head bone put the lens up in the roof)
		# on a ride, at her seat, her eyes where the ride's own first-person view has them (in the funicular, her
		# seat is taken first: following the car from outside, she is at its floor)
		if ride_cam and ride_inside and not ride_look and north and north.has_method("ride_toggle"):
			north.ride_toggle()
		vf_prev_cam = get_viewport().get_camera_3d()
		vf_seen = model.visible
		# looking where the view looked (the follow camera's way; from a room's corner camera, the way she faces), level
		var fwd := -vf_prev_cam.global_basis.z if vf_prev_cam == cam else Vector3(sin(model.global_rotation.y), 0, cos(model.global_rotation.y))
		vf_yaw = atan2(-fwd.x, -fwd.z)
		vf_pitch = 0.0
		# (round 41, rule 10) where her eyes are as she raises it, kept: the view doesn't bob with her head
		var eye0 := vf_eye()
		if ride_cam and seat_eye >= 0.0:
			eye0 = player.global_position + Vector3(0, seat_eye + model.position.y, 0)
		vf_rest_local = model.global_transform.affine_inverse() * eye0
		vf_rest_h = eye0.y - model.global_position.y
		vf_eye_y = eye0.y
		if vf_cam == null:
			vf_cam = Camera3D.new()
			vf_cam.near = 0.05
			add_child(vf_cam)
		vf_cam.environment = vf_prev_cam.environment if vf_prev_cam else null
		vf_cam.attributes = vf_prev_cam.attributes if vf_prev_cam else null
		vf_cam.cull_mask = vf_prev_cam.cull_mask if vf_prev_cam else vf_cam.cull_mask
		place_vf_cam()
		vf_cam.current = true
		model.visible = false
		if vf_layer == null:
			vf_layer = CanvasLayer.new()
			vf_layer.layer = 0                          # (over the picture, under the HUD: the clock and the purse stay bright)
			var c := Control.new()
			vf_draw = c
			c.set_anchors_preset(Control.PRESET_FULL_RECT)
			c.mouse_filter = Control.MOUSE_FILTER_IGNORE
			c.draw.connect(draw_viewfinder.bind(c))
			c.resized.connect(c.queue_redraw)
			vf_layer.add_child(c)
			add_child(vf_layer)
		vf_layer.visible = true
		# (round 41, rule 10: the mission, street name, clock and money boxes hidden while the camera is up)
		vf_hud_was = hud_root.visible
		hud_root.visible = false
		banner_panel.visible = false
		layout_ui()
		ambience.sfx("cloth")
		photo_view(true)
	else:
		photo_view(false)
		hud_root.visible = vf_hud_was
		banner_panel.visible = true
		# (round 41c, the user: "I walked outside and then I'm stuck in the tree": raised indoors and put away out of
		# doors, it gave the view back to the room's camera, left where the room was) back to the camera it came from
		# only if that is still the one for where she is now
		if is_instance_valid(vf_prev_cam) and not (vf_prev_cam == room_cam and where != "in"):
			vf_prev_cam.current = true
		else:
			cam.current = true
		model.visible = vf_seen
		if vf_layer:
			vf_layer.visible = false
		layout_ui()
		ambience.sfx("back")


var vf_draw: Control                 # (round 41) the viewfinder's drawing, redrawn each frame (its clock and zoom)
var vf_hud_was := true
var vf_marks: Control                # the same marks drawn into the photo's own view
var vf_sv: SubViewport               # (round 41) the photo's own view of the world, made ready as the camera comes up
var vf_sv_cam: Camera3D


func photo_view(on: bool) -> void:
	# made when the camera comes up and drawn once then, so a photo only has to draw one frame (made fresh at the
	# shutter it held the blackout for 0.8 s); gone when the camera is put away
	if on and vf_sv == null:
		vf_sv = SubViewport.new()
		vf_sv.size = get_viewport().get_visible_rect().size
		vf_sv.msaa_3d = get_viewport().msaa_3d
		vf_sv.render_target_update_mode = SubViewport.UPDATE_ONCE
		add_child(vf_sv)
		vf_sv_cam = vf_cam.duplicate(0) as Camera3D
		vf_sv.add_child(vf_sv_cam)
		vf_sv_cam.global_transform = vf_cam.global_transform
		vf_sv_cam.current = true
		vf_marks = Control.new()
		vf_marks.set_anchors_preset(Control.PRESET_FULL_RECT)
		vf_marks.draw.connect(func():
			var ssz := Vector2(vf_sv.size)
			draw_photo_marks(vf_marks, photo_frame(ssz), ssz.x / 1280.0))
		vf_sv.add_child(vf_marks)
	elif not on and vf_sv != null:
		vf_sv.queue_free()
		vf_sv = null
		vf_sv_cam = null


func vf_eye() -> Vector3:
	# her eyes: a little over and in front of her head bone (wherever her pose has put it: walking, seated, riding)
	var sk: Dictionary = skins[skin_idx]
	if not sk.has("vf_head"):
		var sks: Array = (sk.root as Node).find_children("*", "Skeleton3D", true, false)
		sk["vf_head"] = [sks[0], (sks[0] as Skeleton3D).find_bone(street_bone(sks[0], "Head"))] if sks.size() > 0 else [null, -1]
	var skel: Skeleton3D = sk.vf_head[0]
	var bi: int = sk.vf_head[1]
	if skel == null or bi < 0:
		return player.global_position + Vector3(0, model.position.y + CAM_PIVOT_H + FP_EYE, 0)
	var head := skel.global_transform * skel.get_bone_global_pose(bi).origin
	var face := Vector3(sin(model.global_rotation.y), 0, cos(model.global_rotation.y))
	return head + Vector3(0, VF_EYE_UP, 0) + face * VF_EYE_FWD


var vf_rest_local := Vector3.ZERO  # (round 41) her eyes as she raised the camera, in her own space
var vf_rest_h := 1.4               # and their height over her feet
var vf_eye_y := 0.0                # the height used, eased over kerbs and steps


func vf_steady_eye() -> Vector3:
	# (round 41, rule 10, the user: "the camera moves with her body. It should be stable") on foot: straight over her
	# feet at the height her eyes were as she raised it (she is hidden, so nothing of her is in the way), the height
	# eased over a kerb or a step; on a ride or a bench: that same place on her as the seat carries her
	if not vf_walking():
		return model.global_transform * vf_rest_local
	var base := model.global_position
	# (and carried on at her own speed between the game's 1/60 s steps, so walking glides instead of stepping)
	base += Vector3(player.velocity.x, 0.0, player.velocity.z) * Engine.get_physics_interpolation_fraction() / float(Engine.physics_ticks_per_second)
	var dt := get_process_delta_time()
	vf_eye_y = lerpf(vf_eye_y, base.y + vf_rest_h, 1.0 - exp(-10.0 * dt)) if absf(vf_eye_y - base.y - vf_rest_h) < 1.5 else base.y + vf_rest_h
	return Vector3(base.x, vf_eye_y, base.z)


var vf_turn := Vector2.ZERO        # (round 41) how fast the viewfinder is turning (yaw, pitch a second)


func vf_walk(inp: Vector2, dt: float) -> float:
	# (round 41, rule 10, the user: "keep WASD to move around in the camera mode") W forward where the viewfinder
	# looks, S back, A and D a step to the side; she keeps facing the view, so her eyes (the camera) stay put on her
	if inp.length() > 0.08:
		move_dir = (Vector2(cos(vf_yaw), -sin(vf_yaw)) * inp.x + Vector2(-sin(vf_yaw), -cos(vf_yaw)) * inp.y).normalized()
	speed = move_toward(speed, SPEED * inp.length(), (ACCEL if inp.length() > 0.08 else DECEL) * dt)
	return 0.0


func vf_look(dt: float) -> void:
	# (the viewfinder) the arrows or W A S D look round, ↑ up, the pad's right stick too; she stays where she is.
	# (round 41, the user: "the increments to move left and right are very static. It should be smoother") every
	# drawn frame, not the game's 1/60 s steps (at 20 fps those came in jumps of three), and easing in and out
	var vk := Vector2.ZERO if dlg_open else (look_keys() if vf_walking() else move_input())
	var want := Vector2(-vk.x * 1.6, vk.y * 0.9)
	var rx := pad_axis(JOY_AXIS_RIGHT_X)
	var ry := pad_axis(JOY_AXIS_RIGHT_Y)
	want += Vector2(-rx * PAD_SENS, -ry * PAD_SENS * 0.6)
	vf_turn = vf_turn.lerp(want, 1.0 - exp(-10.0 * dt))
	vf_yaw += vf_turn.x * dt
	vf_pitch = clampf(vf_pitch + vf_turn.y * dt, -1.45, 1.45)


func place_vf_cam() -> void:
	vf_cam.global_transform = Transform3D(Basis.from_euler(Vector3(vf_pitch, vf_yaw, 0.0)), vf_steady_eye())
	var base := cam_fov if vf_prev_cam == cam else 62.0
	fit_camera(vf_cam, rad_to_deg(2.0 * atan(tan(deg_to_rad(base) / 2.0) / lerpf(1.0, VF_ZOOM, vf_zoom_k))))


func draw_viewfinder(c: Control) -> void:
	# the frame the photo keeps (PHOTO_CROP, 3:2), everything outside it darkened; a grey line round it, a right angle
	# just inside each corner, the circle with a line through it in the middle (sized from the mock-up the user saw,
	# 1280 px wide)
	var sz := c.size
	var k := sz.x / 1280.0
	var r := photo_frame(sz)
	var pw := r.size.x
	var ph := r.size.y
	var dark := Color(0, 0, 0, VF_DARK)
	c.draw_rect(Rect2(0, 0, sz.x, r.position.y), dark)
	c.draw_rect(Rect2(0, r.end.y, sz.x, sz.y - r.end.y), dark)
	c.draw_rect(Rect2(0, r.position.y, r.position.x, ph), dark)
	c.draw_rect(Rect2(r.end.x, r.position.y, sz.x - r.end.x, ph), dark)
	c.draw_rect(r, VF_GREY, false, VF_LINE * k)
	var ins := 30.0 * k
	var ln := 74.0 * k
	for cn in [[r.position, 1, 1], [Vector2(r.end.x, r.position.y), -1, 1], [Vector2(r.position.x, r.end.y), 1, -1], [r.end, -1, -1]]:
		var a: Vector2 = cn[0] + Vector2(cn[1] * ins, cn[2] * ins)
		c.draw_polyline(PackedVector2Array([a + Vector2(0, cn[2] * ln), a, a + Vector2(cn[1] * ln, 0)]), VF_GREY, VF_LINE * k, true)
	var mid := sz / 2.0
	c.draw_arc(mid, 42.0 * k, 0.0, TAU, 64, VF_GREY, VF_LINE * k, true)
	c.draw_line(mid - Vector2(80.0 * k, 0), mid + Vector2(80.0 * k, 0), VF_GREY, VF_LINE * k, true)
	draw_photo_marks(c, r, k)


func photo_frame(sz: Vector2) -> Rect2:
	# the part of the screen the photo keeps: the middle PHOTO_CROP of its width, 3:2
	var pw := sz.x * PHOTO_CROP
	var ph := pw * 2.0 / 3.0
	if ph > sz.y:
		ph = sz.y
		pw = ph * 1.5
	return Rect2((sz.x - pw) / 2.0, (sz.y - ph) / 2.0, pw, ph)


# (round 41, rule 10, the user's picks) the camera's details inside the bottom corner angles: the game's date and time
# at the left, the Pentax and its settings at the right; the game keeps no calendar, so its first day is 15 Sep 2026
const PHOTO_DAY_ONE := {"year": 2026, "month": 9, "day": 15, "hour": 12, "minute": 0, "second": 0}
const MONTH_SHORT := ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


func photo_marks() -> PackedStringArray:
	var mins := int(game.S.time)
	var day := Time.get_datetime_dict_from_unix_time(Time.get_unix_time_from_datetime_dict(PHOTO_DAY_ONE) + (mins / 1440) * 86400)
	var when := "%d %s %d  ·  %02d:%02d" % [day.day, MONTH_SHORT[int(day.month) - 1], day.year, mins / 60 % 24, mins % 60]
	var cam_ := "PENTAX K1000  ·  %d mm  ·  f/8  ·  1/250 s  ·  ISO 200" % (75 if vf_zoom else 50)
	return PackedStringArray([when, cam_])


func draw_photo_marks(c: CanvasItem, r: Rect2, k: float) -> void:
	# just inside each bottom corner angle (30 in, 74 long), in the game's lettering, white at about 70%
	var f := talk_font()
	var fs := int(round(16.0 * k))
	var t := photo_marks()
	var y := r.end.y - 44.0 * k
	var lx := r.position.x + 44.0 * k
	var rx := r.end.x - 44.0 * k - f.get_string_size(t[1], HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	for pass_ in 2:
		var off := Vector2(k, k) if pass_ == 0 else Vector2.ZERO
		var col := Color(0, 0, 0, 0.43) if pass_ == 0 else Color(1, 1, 1, 0.72)
		c.draw_string(f, Vector2(lx, y) + off, t[0], HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
		c.draw_string(f, Vector2(rx, y) + off, t[1], HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)


const PHOTO_CROP := 0.75         # a photo keeps this much of the screen's width, 3:2 (round 41, the user's E)
var photo_on := false            # a photo is being taken: she stays hidden for it
const PHOTO_LIFT := 0.26         # rad: from her eyes the shot looks this much higher than the follow camera


func take_photo() -> void:
	# (round 41, rule 10, the user: "it should go darker, but you never leave the camera mode… like a shutter animation…
	# very quick") through the viewfinder: the click, the screen blinks dark, and the photo is drawn apart from the
	# screen (its own view of the world from the viewfinder's camera), so nothing on screen hides
	if vf_on and vf_cam:
		# (then: "It shouldn't be a flash. Because there's no flash. It should just be the snap of the shutter. Because
		# it's an SLR camera") as an SLR's mirror flips up: the view goes black for a moment with the click, the
		# photo is taken while it is (the moment the game takes over drawing it falls inside the blackout), and back
		ambience.sfx("shutter")
		vf_shutter = true
		fade.color = Color(0, 0, 0, 0.92)
		await RenderingServer.frame_post_draw
		if vf_sv == null:
			photo_view(true)
		vf_sv.size = get_viewport().get_visible_rect().size
		for prop in ["fov", "near", "far", "projection", "size", "frustum_offset", "keep_aspect", "h_offset", "v_offset"]:
			vf_sv_cam.set(prop, vf_cam.get(prop))
		vf_sv_cam.global_transform = vf_cam.global_transform
		vf_marks.size = Vector2(vf_sv.size)
		vf_marks.queue_redraw()
		vf_sv.render_target_update_mode = SubViewport.UPDATE_ONCE
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var pic := vf_sv.get_texture().get_image()
		var tw_ := create_tween()
		tw_.tween_property(fade, "color:a", 0.0, 0.1)
		tw_.tween_callback(func(): vf_shutter = false)
		save_photo(pic, false)
		return
	# a white flash, the view saved without the HUD, and a note of where it went
	var ui_layers := get_children().filter(func(c): return c is CanvasLayer)
	for c in ui_layers:
		c.visible = false
	# (round 41, the user: "could it be a first-person view? Because obviously she's not going to take a picture with
	# herself in it") the shot from her eyes, looking where the camera looks (lifted a touch: the follow camera looks
	# down at her), with her hidden; back to the follow camera after it. Already at her eyes (a ride's seat, a bench,
	# a porch), it stays where it is.
	var was_seen := model.visible
	var shot: Camera3D = null
	if free_cam() and cam.current and cam.global_position.distance_to(arm.global_position) > 0.4:
		var fwd := -cam.global_basis.z
		var yaw := atan2(-fwd.x, -fwd.z)
		var pitch := clampf(asin(clampf(fwd.y, -1.0, 1.0)) + PHOTO_LIFT, -1.2, 1.2)
		shot = cam.duplicate(0)
		add_child(shot)
		shot.global_transform = Transform3D(Basis.from_euler(Vector3(pitch, yaw, 0.0)), arm.global_position + Vector3(0, FP_EYE, 0))
		shot.current = true
	photo_on = true
	model.visible = false
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	if shot:
		shot.queue_free()
		cam.current = true
	model.visible = was_seen
	photo_on = false
	for c in ui_layers:
		c.visible = true
	save_photo(img, true)


# (round 41) the background saves: each one collected once it is done, and all waited for before the game closes —
# left uncollected, Godot crashed on its way out after a photo (macOS crash reports, a lock already taken apart)
var photo_jobs: Array[int] = []


func collect_photo_jobs(all: bool) -> void:
	for id in photo_jobs.duplicate():
		if all or WorkerThreadPool.is_task_completed(id):
			WorkerThreadPool.wait_for_task_completion(id)
			photo_jobs.erase(id)


func save_photo(img: Image, flash: bool) -> void:
	# (round 41, the user picked E: "more cropped… on the top as well as the sides, but keep that aspect ratio") the
	# middle three quarters of the screen, 3:2
	var pw := int(img.get_width() * PHOTO_CROP)
	var ph := int(pw * 2.0 / 3.0)
	if ph > img.get_height():
		ph = img.get_height()
		pw = int(ph * 1.5)
	img = img.get_region(Rect2i((img.get_width() - pw) / 2, (img.get_height() - ph) / 2, pw, ph))
	# (round 41, the user: "Is it possible for the game to save it on the desktop?") on the Desktop; if that can't be
	# written, the game's own photos folder as before
	var stamp := Time.get_datetime_string_from_system().replace(":", "-")
	var fname := "Barcelona photo %s.png" % stamp.replace("T", " ")
	var desk := OS.get_system_dir(OS.SYSTEM_DIR_DESKTOP)
	var where_ := "your Desktop"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--photodir="):           # (a test saves its photos elsewhere, not on the Desktop)
			desk = a.substr(11)
	if flash:
		ambience.sfx("shutter")
		fade.color = Color(1, 1, 1, 0.9)
		create_tween().tween_property(fade, "color:a", 0.0, 0.5)
	# (round 41) written in the background, so the game doesn't stop for it just after the shutter; the note comes
	# when it is written
	photo_jobs.append(WorkerThreadPool.add_task(func():
		if desk == "" or img.save_png(desk.path_join(fname)) != OK:
			DirAccess.make_dir_recursive_absolute("user://photos")
			img.save_png("user://photos/" + fname)
			where_ = ProjectSettings.globalize_path("user://photos")
		call_deferred("toast", "Click! Photo saved to %s" % where_, 3.0)))


var spot_ready := false           # (round 38) once she is in play, where she stands goes into each save
var last_spot := {}               # (round 40) out of doors, where she last did something: the autosave's place


func here_spot() -> Dictionary:
	var p := player.global_position
	return {"x": snappedf(p.x, 0.01), "z": snappedf(p.z, 0.01), "yaw": snappedf(model.rotation.y, 0.001)}


func note_spot() -> void:
	# (round 40, rule 08 #82b) she did something here — went out of a door, talked, picked up, looked: the autosave's place
	if spot_ready and where == "out" and not ride_cam:
		last_spot = here_spot()


func save_spot(exact := false) -> Dictionary:
	# (round 38) where she is, for the save: in a room, the room and the door she came in by; out of doors (round 40,
	# the user: "the autosave should be the most recent object interaction. The manual save should be whichever location
	# she was at") the place of her last interaction, or with `exact` (Export save, the manual save) where she stands.
	# Not before play starts (the title screen stands her on the beach) nor mid-ride: the last place is kept.
	if not spot_ready or ride_cam or busy:
		return {}
	if where == "in":
		return {"room": room, "door": String(room_door.get("id", ""))}
	return here_spot() if exact else last_spot.duplicate()


func restore_spot() -> void:
	# (round 38, the user: Continue "should start from wherever she was") back where the save left her
	var at: Dictionary = game.S.get("at", {})
	if at.is_empty():
		return
	if at.has("room") and D.interiors.has(String(at.room)):
		for e in D.entrances:
			if String(e.get("id", "")) == String(at.door) and e.has("int"):
				room_door = e
				break
		show_room(String(at.room), false)
	elif at.has("x"):
		teleport(Vector3(float(at.x), 0.0, float(at.z)), float(at.yaw))
		last_spot = at.duplicate()                     # (round 40: where the save left her, until she does something)


func _exit_tree() -> void:
	collect_photo_jobs(true)                           # (a photo still being written finishes before the game goes)


func _notification(what: int) -> void:
	# (round 38) closing the window saves too, so nothing since the last 30 s save is lost
	if what == NOTIFICATION_WM_CLOSE_REQUEST and spot_ready and game:
		game.save_game()


# (round 41, the user: "Could you instead have a picture looking at the city as if it's from a helicopter some very
# iconic angle?… the main title screen, it's actually an action shot of the world at that time. Sunrise, sunset, with
# people walking around if they happen to be there") the title's view: over Park Güell's terrace, the Sagrada Família in
# the middle, the sea behind (the user's pick, "H3a1_1 down 3": workshop/screenshots/round41/title_aerials) — the live
# world, at the game's own time
const TITLE_VIEW := [Vector3(130.0, 45.0, -205.0), Vector3(13.05, 11.77, -34.27), 43.0]   # (then: halfway between "two steps up" and the first cross-centred one)   # (then: "two steps up"; then further to the sky twice: "2 steps is perfect. That's it")
var title_cam: Camera3D


func title_view(on: bool) -> void:
	if on and title_cam == null:
		title_cam = Camera3D.new()
		title_cam.fov = TITLE_VIEW[2]
		outdoor.add_child(title_cam)
		title_cam.global_position = TITLE_VIEW[0]
		var at: Vector3 = TITLE_VIEW[1]
		for a in OS.get_cmdline_user_args():           # (tests: --titlelook= tries another height to look at)
			if a.begins_with("--titlelook="):
				at.y = float(a.substr(12))
			if a.begins_with("--titleat="):
				var v := a.substr(10).split(",")
				at = Vector3(float(v[0]), float(v[1]), float(v[2]))
		title_cam.look_at(at, Vector3.UP)
		title_cam.current = true
	elif not on and title_cam != null:
		title_cam.queue_free()
		title_cam = null
		cam.current = true


func title_screen() -> void:
	# as the 2D game opens: its title over the city, then Continue (if there's a saved game) or New game
	if game.fresh:
		spot_ready = true
		ambience.call_deferred("begin", false)   # (rule 08 #82d: no sound until the first picture)
		game.intro()
		return
	if Engine.has_meta("load_continue"):         # (Load game: straight into the copy just loaded, rule 08 #82)
		Engine.remove_meta("load_continue")
		spot_ready = true
		ambience.call_deferred("begin", false)
		restore_spot()
		return
	var box := VBoxContainer.new()
	box.anchor_left = 0.0
	box.anchor_right = 1.0
	# (round 41, the user: "move Erasmus in Barcelona up a little bit more…"; then, from the highest of three: "move
	# Sandra's adventure slightly up? And then Erasmus in Barcelona slightly down so they meet, but Sandra's adventure
	# goes up slightly more")
	box.offset_top = 18.0                          # (then the user changed their mind: the text where it was, the camera tilted up a little instead)
	box.add_theme_constant_override("separation", -12)          # (then: "Sandra's adventure slightly higher? Just a smidgen")
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--titlesub=") and a.find(",") > 0:
			box.add_theme_constant_override("separation", int(a.split(",")[1]))
	for a in OS.get_cmdline_user_args():           # (tests: --titletop= tries another height)
		if a.begins_with("--titletop="):
			box.offset_top = float(a.substr(11))
	box.offset_left = 0.0
	box.offset_right = 0.0
	var t1 := make_label(64, Color("#fff2d8"))
	t1.text = "ERASMUS IN BARCELONA"
	t1.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	t1.add_theme_constant_override("shadow_offset_x", 3)
	t1.add_theme_constant_override("shadow_offset_y", 4)
	t1.add_theme_color_override("font_shadow_color", Color(0.24, 0.08, 0.12, 0.5))
	# (round 41, the user: "lower and increase the size of the words Sandra's adventure")
	var t2size := 32                               # (the user chose A)
	for a in OS.get_cmdline_user_args():           # (tests: --titlesub=size,gap tries others)
		if a.begins_with("--titlesub="):
			t2size = int(a.substr(11).split(",")[0])
	var t2 := make_label(t2size, Color("#fbe6d0"))
	t2.add_theme_constant_override("shadow_offset_x", 2)
	t2.add_theme_constant_override("shadow_offset_y", 3)
	t2.add_theme_color_override("font_shadow_color", Color(0.24, 0.08, 0.12, 0.5))
	t2.text = "Sandra's Adventure"
	t2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(t1)
	box.add_child(t2)
	hud_root.get_parent().add_child(box)
	hud_root.visible = false
	title_view(true)
	banner_timer = 0.0                             # (no place name over the title: rule 08 #82d)
	banner_panel.modulate.a = 0.0
	last_banner = ""
	ambience.call_deferred("begin", true)          # (round 41, rule 08 #82d: after loading, the music and a far-off city hum)
	var go := func():
		box.queue_free()
		title_view(false)
		hud_root.visible = true
		spot_ready = true
		ambience.call_deferred("title_hush", false)   # (after she is put in her place: its own sounds fade in)
	title_go = go
	title_choices()


# (round 41, rule 08 #82, the user: "load game… Make it the second option and move new to the bottom")
var title_go: Callable


func title_choices() -> void:
	var opts := []
	if not game.S.get("new", true):
		opts.append({"label": "Continue", "fn": func():
			title_go.call()
			restore_spot()})
	opts.append({"label": "Load game", "fn": func(): load_menu(title_choices)})
	opts.append({"label": "New game", "fn": func():
		if game.S.get("new", true):
			title_go.call()
			game.S.erase("at")
			game.intro()
		else:
			new_game()})
	game.ask("", "Benvinguda a Barcelona!" if game.S.get("new", true) else "Welcome back, Sandra. (Saved at %02d:%02d, %s)" % [int(game.S.time) / 60 % 24, int(game.S.time) % 60, game.money(game.S.money)], opts)


const MONTHS := ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


func load_menu(back: Callable) -> void:
	# (round 41, rule 08 #82) the title's Load game: the copies Export save made, newest first — when each was saved
	# and her money — then Back. Picking one asks before it replaces the game, and the game starts where it left her.
	var files: Array = []
	var d := DirAccess.open("user://saves")
	if d:
		for f in d.get_files():
			if f.begins_with("erasmus-save-") and f.ends_with(".json"):
				files.append(f)
	files.sort()
	files.reverse()
	if files.is_empty():
		game.ask("", "There are no saved copies yet. Export save, in the Esc menu while playing, makes one.",
			[{"label": "Back", "fn": back}])
		return
	var opts := []
	for f in files.slice(0, 6):
		var v = JSON.parse_string(FileAccess.get_file_as_string("user://saves/" + f))
		if not v is Dictionary:
			continue
		var when := String(f).trim_prefix("erasmus-save-").trim_suffix(".json")     # 2026-10-29_20-35-38
		var dp := when.split("_")[0].split("-")
		var tp := when.split("_")[1].split("-") if when.contains("_") else PackedStringArray(["0", "0"])
		var label := "%d %s, %s:%s  ·  %s" % [int(dp[2]), MONTHS[clampi(int(dp[1]) - 1, 0, 11)], tp[0], tp[1],
			game.money(float(v.get("money", 0)))]
		opts.append({"label": label, "fn": func(): confirm_load(f, label, back)})
	opts.append({"label": "Back", "fn": back})
	game.ask("", "Which saved game?", opts)


func confirm_load(f: String, label: String, back: Callable) -> void:
	var load_it := func():
		DirAccess.copy_absolute("user://saves/" + f, game.SAVE_PATH)
		Engine.set_meta("load_continue", true)
		get_tree().reload_current_scene()
	if game.S.get("new", true):                        # (no game of hers to lose)
		load_it.call()
		return
	game.ask("", "Load the game saved %s? The game you were playing will be replaced by it." % label.split("  ·  ")[0], [
		{"label": "Yes, load it", "fn": load_it},
		{"label": "Back", "fn": func(): load_menu(back)}])


func new_game() -> void:
	# a completely fresh start: the save is set aside and everything is made again
	if FileAccess.file_exists(game.SAVE_PATH):
		DirAccess.rename_absolute(game.SAVE_PATH, game.SAVE_PATH + ".old")
	Engine.set_meta("fresh_start", true)
	get_tree().reload_current_scene()


func pause_menu() -> void:
	# the 2D game's pause menu
	game.ask("Paused", "The game waits for you. (Saved automatically as you play.)", [
		{"label": "Resume", "fn": func(): pass},
		{"label": "Journal", "fn": func(): game.journal_panel()},
		{"label": "Music: %s  (N)" % ("on" if ambience.get("music_on") != false else "off"), "fn": func():
			last_banner = ""
			show_banner("♪  " + ambience.toggle_music())},
		{"label": "Export save", "fn": func(): export_save()},
		{"label": "Import save", "fn": func(): import_save()},
		{"label": "New game…", "fn": func():
			game.ask("", "Start a completely new game? Your current progress will be replaced.", [
				{"label": "Yes, start again", "fn": func(): new_game()},
				{"label": "No, keep playing", "fn": func(): pass}])}])


func export_save() -> void:
	# the 2D game's Export save: a copy of the game as it is now, kept safe (to go back to, or to move to
	# another computer), in a "saves" folder beside the game's own save
	game.save_game(true)                               # (round 40: the manual save keeps her exact spot, 08 #82b)
	DirAccess.make_dir_recursive_absolute("user://saves")
	var name := "erasmus-save-%s.json" % Time.get_datetime_string_from_system().replace(":", "-").replace("T", "_")
	DirAccess.copy_absolute(game.SAVE_PATH, "user://saves/" + name)
	game.save_game()                                   # (and the game's own save goes back to the autosave's place)
	game.say("", "Saved a copy of your game: %s, in %s. Import save brings back the newest copy there." % [name, ProjectSettings.globalize_path("user://saves")])


func import_save() -> void:
	# the newest copy in the saves folder replaces the game being played (after asking)
	var d := DirAccess.open("user://saves")
	var files: Array = []
	if d:
		for f in d.get_files():
			if f.ends_with(".json"):
				files.append(f)
	if files.is_empty():
		game.say("", "There are no saved copies yet (Export save makes one), in %s." % ProjectSettings.globalize_path("user://saves"))
		return
	files.sort()
	var newest: String = files[-1]
	game.ask("", "Load %s? The game you're playing now will be replaced by it." % newest, [
		{"label": "Yes, load it", "fn": func():
			var v = JSON.parse_string(FileAccess.get_file_as_string("user://saves/" + newest))
			if not v is Dictionary:
				game.say("", "That copy can't be read, sorry.")
				return
			DirAccess.copy_absolute("user://saves/" + newest, game.SAVE_PATH)
			get_tree().reload_current_scene()},
		{"label": "No, keep playing", "fn": func(): pass}])


func bike_key() -> void:
	# B, as in the 2D game: once Jordi has given her the old bicycle, she hops on (or off) anywhere outdoors
	if street.riding:
		street.dismount()
		toast("Hopped off the bike")
		return
	if not game.S.get("has_bike", false):
		toast("You don't have a bike yet")
		ambience.sfx("nope")
		return
	if where != "out":
		toast("No riding indoors!")
		return
	if in_bike_free_park(player.global_position):
		toast("No bikes in Park Güell: you can ride again outside the gate")
		ambience.sfx("nope")
		return
	# (round 41, the user: getting back on inside the funfair "says it's too rough. Whereas it should have some text to do
	# with the fun fair") each place says its own reason
	var fr_: Array = D.get("north", {}).get("fair", {}).get("rect", [0, 0, 0, 0])
	var pq_ := player.global_position
	if pq_.x > fr_[0] - 0.5 and pq_.x < fr_[2] + 0.5 and pq_.z > fr_[1] - 0.5 and pq_.z < fr_[3] + 0.5:
		toast("No bikes in the funfair: wheel it out to the path to ride again")
		ambience.sfx("nope")
		return
	if no_bike_at(player.global_position):
		if on_hill_off_path(player.global_position):
			toast("No riding in the woods: wheel it back to the path")
		else:
			toast("Bikes and sand don't mix" if street_name(player.global_position).begins_with("Platja") or player.global_position.z > 120.0 else "Too rough for the bike here: back to a path or the grass")
		ambience.sfx("nope")
		return
	street.own_bike_here()
	ambience.sfx("bell")
	toast("On the bike! (%s to hop off)" % bike_word())


func interact() -> void:
	var n := nearest()
	if n.is_empty():
		return
	var p := local_pos()
	note_spot()                                        # (round 40: the autosave's place, 08 #82b)
	if not n.act in ["dismount", "bike", "door", "stairs"]:
		face_target = atan2(n.x - p.x, n.z - p.z)          # turn to whoever or whatever she's talking to
	match n.act:
		"door":
			var lk: String = n.e.get("lock", "")
			if lk != "" and not game.unlocked(lk):
				game.locked_door(lk)
			elif lk != "" and game.open_locked(lk):
				# (round 40, the user: "just press E on the door and then it says some like the key fits perfectly. And then
				# you simply enter") the line, then in as the talk box closes
				var e_: Dictionary = n.e
				game.after(func(): enter(e_))
			else:
				enter(n.e)
		"stairs":
			if n.get("lock", "") != "" and not game.unlocked(n.lock):
				game.locked_door(n.lock)
			else:
				enter_room(n.to, true)
		"plaque":
			ambience.sfx("page")
			if game.data.BUILDINGS.any(func(b): return b.id == n.get("bid", "") and b.get("landmark", false)):
				game.S.plaques[n.bid] = true                 # (the 2D game counts the landmarks' plaques read)
			show_dialog("", [n.text])
		"sign":
			show_dialog("", ["A corner plaque in white marble: %s." % n.text])
		"thing": game.use_thing(n.th)
		"pick": game.pick_up(n.g)
		"npc": game.talk_to(n.who)
		"dismount": street.dismount()
		"trufa", "bike", "bike_locked": street.act(n)
		"person": people.greet(n.who)
		"cat": show_dialog("", [n.text])
		"rosa_cat":                                    # (round 40: Rosa's cat, in their flat, not friendly)
			show_dialog("", [touches.ROSA_CAT_LINES[touches.rosa_cat_said % touches.ROSA_CAT_LINES.size()]])
			touches.rosa_cat_said += 1
		"notebook": game.read_notebook()
		"north": north.act(n.what)
		"bench": benches.sit(int(n.i))


func fade_then(fn: Callable) -> void:
	busy = true
	face_target = INF
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.3)
	tw.tween_callback(fn)
	tw.tween_property(fade, "color:a", 0.0, 0.35)
	tw.tween_callback(func(): busy = false)


var sleeping := false


func sleep(night: bool, done: Callable) -> void:
	# Sandra's bed (the 2D game's goToSleep): the screen fades out with a drifting "Z z z", the clock moves on
	# (to 07:00 at night, two hours for a nap) while it's dark, and it fades back in
	busy = true
	sleeping = true                                    # (no keys meanwhile)
	ambience.sfx("cloth")
	var z := make_label(46, Color(1, 0.97, 0.9))
	z.text = "Z z z …" if night else "z z …"
	z.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	z.set_anchors_preset(Control.PRESET_CENTER)
	z.size = Vector2(400, 60)
	z.position = get_viewport().get_visible_rect().size / 2.0 - Vector2(200, 30)
	z.modulate.a = 0.0
	fade.get_parent().add_child(z)
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.8)
	tw.parallel().tween_property(z, "modulate:a", 1.0, 0.8).set_delay(0.4)
	tw.tween_callback(func():
		var mm: int = int(game.S.time) % 1440
		set_clock(7 * 60 if night else (mm + 120) % 1440))
	tw.tween_property(z, "position:y", z.position.y - 40.0, 1.4)
	tw.parallel().tween_property(z, "modulate:a", 0.0, 1.4)
	tw.tween_property(fade, "color:a", 0.0, 0.9)
	tw.tween_callback(func():
		z.queue_free()
		busy = false
		sleeping = false
		done.call())


func enter(e: Dictionary) -> void:
	if busy or where == "in":
		return
	if street.riding != null:
		# (round 39, the user: going in on the bike, "Must get off first"; no message — "that's unnecessary") the door
		# simply stays shut until she hops off
		return
	ambience.sfx("door")
	street.on_enter()
	room_door = e
	keep_cam()
	fade_then(func(): enter_room(e.int, false))


var kept_cam := Vector2(0.0, CAM_PITCH)   # the camera through a door: turned from behind her (rad), tipped (rad)


func keep_cam() -> void:
	# (where the player has the camera: how far it is turned from behind her, and how it is tipped)
	kept_cam = Vector2(wrapf(cam_yaw_node.rotation.y - (model.rotation.y + PI), -PI, PI), cam_pitch_node.rotation.x)


func enter_room(rid: String, by_stairs: bool) -> void:
	# into a room by its door (at the front, facing in), or up or down the university's stairs
	if by_stairs:
		fade_then(func(): show_room(rid, true))
	else:
		show_room(rid, false)


func show_room(rid: String, by_stairs: bool) -> void:
	var R: Dictionary = D.interiors[rid]
	where = "in"
	if room_nodes.has(room):
		room_nodes[room].visible = false
		room_lights[room].visible = false
	room = rid
	room_nodes[rid].visible = true
	room_lights[rid].visible = true
	var at := Vector3(R.spawn[0], 0, R.spawn[1])
	var stair_face := Vector2(0, -1)
	if by_stairs and not R.stairs.is_empty():
		var st: Dictionary = R.stairs[0]
		if st.has("arrive"):
			at = Vector3(st.arrive[0], 0, st.arrive[1])        # at the other end of the stair, stepping off it
			stair_face = Vector2(st.face[0], st.face[1])
		else:
			at = Vector3(st.pos[0] - 1.2, 0, st.pos[1] - 0.6)
	var from_top: bool = not by_stairs and room_door.get("room_side", "bottom") == "top" and R.get("exit_top") != null
	if from_top:
		at = Vector3((R.exit_top[0] + R.exit_top[1]) / 2.0, 0, 1.6)
	player.global_position = room_base(rid) + at
	player.velocity = Vector3.ZERO
	speed = 0.0
	model.rotation.y = 0.0 if from_top else PI
	move_dir = Vector2(0, 1) if from_top else Vector2(0, -1)
	if by_stairs:
		move_dir = stair_face
		model.rotation.y = atan2(stair_face.x, stair_face.y)
	outdoor.visible = false
	indoor.visible = true
	world_env.environment = env_in
	ambience.set_outdoors(false)
	var sacred: bool = R.get("kind", "") == "sacred"
	env_in.fog_enabled = sacred                                  # a soft haze in the basilica, to catch the light
	env_in.fog_light_color = Color(0.95, 0.9, 0.82)
	env_in.fog_density = 0.0035
	env_in.fog_light_energy = 0.6
	env_in.ambient_light_energy = 0.55 if sacred else 1.0
	env_in.tonemap_exposure = 0.88 if sacred else 1.0
	env_in.fog_sky_affect = 0.0
	env_in.glow_intensity = 1.0 if sacred else 0.8
	env_in.glow_bloom = 0.12 if sacred else 0.0
	env_in.ambient_light_color = Color(0.95, 0.9, 0.84) if sacred else Color(1.0, 0.88, 0.74)
	update_sun_beams()
	if R.get("free_cam", false):
		# the street camera, where the player had it (round 21: it used to be put back behind her, tipped up)
		cam_yaw_node.rotation.y = (PI if from_top else 0.0) + kept_cam.x
		cam_pitch_node.rotation.x = CAM_PITCH            # (round 38: its height and zoom back to the usual at every door)
		cam_len = CAM_DIST
		cam_vel = 0.0
		cam_root.global_position = player.global_position + Vector3(0, CAM_PIVOT_H, 0)
		cam.current = true
	else:
		room_cam.current = true
	entered_at = t
	npcs.enter_room(rid, Vector3(R.offset[0], 0, 0))
	game.on_enter(rid)
	last_banner = ""
	show_banner(R.name)


func leave_by(side: String) -> void:
	# out by the door on this side of the room (the Sagrada Família has two: Nativity and Passion)
	for e in D.entrances:
		if e.get("int", "") == room and e.get("room_side", "bottom") == side:
			room_door = e
			break
	leave()


func leave() -> void:
	if busy or room_door.is_empty():
		return
	ambience.sfx("door")
	var was_free := free_cam()
	if was_free:
		keep_cam()                                   # (out of the basilica: as the player had it in there)
	fade_then(func():
		where = "out"
		room_nodes[room].visible = false
		room_lights[room].visible = false
		npcs.leave_room()
		game.on_exit_to_world()
		room = ""
		var d := room_door
		var n := Vector2(d.normal[0], d.normal[1])
		player.global_position = Vector3(d.pos[0] + n.x * 1.8, 0, d.pos[1] + n.y * 1.8)   # (round 23: room for the camera behind her)
		player.velocity = Vector3.ZERO
		speed = 0.0
		model.rotation.y = atan2(n.x, n.y)
		move_dir = n
		# the camera as the player had it before going in (round 21: it used to be turned to look back at the
		# door, whatever they'd done): turned the same way from her, tipped the same
		# (at most a quarter turn round: from in front of her, forward would walk her straight back in)
		cam_yaw_node.rotation.y = atan2(n.x, n.y) + PI + clampf(kept_cam.x, -1.6, 1.6)
		# (round 38, the user: the player can tip the camera "to something random. And then if you walk inside, then you
		# walk outside, it should reset again"; and the zoom too) its height and zoom back to the usual; the turn is kept
		cam_pitch_node.rotation.x = CAM_PITCH
		cam_len = CAM_DIST
		cam_vel = 0.0
		indoor.visible = false
		outdoor.visible = true
		world_env.environment = env_out
		ambience.set_outdoors(true)
		snap_height()
		cam.current = true
		note_spot()                                    # (round 40: out of a door, the autosave's place is just outside it)
		last_banner = ""
		show_banner(street_name(player.global_position)))


func take_me_home() -> void:
	# (round 40, the user: "create a new shortcut in the main shortcuts and have it say, take me home? And then if the
	# user presses it, there's a confirmation, take me home or stay here", rule 08 #82c) H: back to her own front door
	if busy or ride_cam or cutscene or sleeping:
		return
	var home := {}
	for e in D.entrances:
		if String(e.get("id", "")) == "apt_sandra":
			home = e
	if home.is_empty():
		return
	game.ask("", "Take me home?", [
		{"label": "Take me home", "fn": func():
			var n := Vector2(home.normal[0], home.normal[1])
			fade_then(func():
				teleport(Vector3(home.pos[0] + n.x * 2.0, 0, home.pos[1] + n.y * 2.0), atan2(-n.x, -n.y))
				if street and street.has_method("on_take_home"):
					street.on_take_home(player.global_position)     # (round 41c, 10 #26c: the dog home to her owner)
				note_spot())},
		{"label": "Stay here", "fn": func(): pass}])


func debug_places() -> Array:
	# the debug menu's places: where she wakes, every door (a step outside it, facing it), and a few others
	var out := [{"name": "The beach, where she wakes", "pos": Vector3(D.spawn.pos[0], 0, D.spawn.pos[1]), "facing": float(D.spawn.facing)}]
	var doors := []
	for e in D.entrances:
		var n := Vector2(e.normal[0], e.normal[1])
		var label: String = e.name
		if e.get("int", "") == "int_sagrada":
			label += "  (Passion door, west)" if e.get("room_side", "bottom") == "top" else "  (Nativity door, east)"
		doors.append({"name": label, "pos": Vector3(e.pos[0] + n.x * 2.0, 0, e.pos[1] + n.y * 2.0), "facing": atan2(-n.x, -n.y)})
	doors.sort_custom(func(a, b): return a.name < b.name)
	out.append_array(doors)
	var tile := func(x: float, y: float) -> Vector3: return Vector3((x - 55.0) * 3.3, 0, (y - 45.0) * 3.3)
	out.append({"name": "Trufa's glade, in the forest", "pos": tile.call(98.0, 50.0), "facing": 0.0})
	out.append({"name": "La Rambla, by Montse", "pos": npcs.outdoor.montse.holder.global_position + Vector3(0, 0, 2.5) if npcs.outdoor.has("montse") else tile.call(37.0, 60.0), "facing": PI})
	# (round 23) the north: the hill path, the funfair, the funicular, Gràcia, Park Güell
	var Nn: Dictionary = D.get("north", {})
	if not Nn.is_empty():
		out.append({"name": "The path up to Tibidabo (its foot, the workmen)", "pos": Vector3(Nn.workmen[0][0] + 2.0, 0, Nn.workmen[0][1] + 5.0), "facing": PI})
		out.append({"name": "Tibidabo funfair: the Ferris wheel", "pos": Vector3(Nn.wheel.board[0], 0, Nn.wheel.board[1] + 4.0), "facing": PI})
		out.append({"name": "Tibidabo funfair: the Sagrat Cor", "pos": Vector3(-63.0, 0, -292.0), "facing": PI})
		out.append({"name": "The funicular, bottom station", "pos": Vector3(Nn.cable.door_low[0], 0, Nn.cable.door_low[1] + 3.0), "facing": PI})
		var bp: Array = Nn.get("ball", Nn.ledge)
		out.append({"name": "The ball, in the wood on the hill", "pos": Vector3(bp[0], 0, bp[1] - 2.5), "facing": 0.0})
		out.append({"name": "Gràcia, the little square", "pos": Vector3(Nn.gracia_placa[0], 0, Nn.gracia_placa[1] + 4.0), "facing": PI})
		out.append({"name": "Park Güell, the gate", "pos": Vector3(Nn.park.gate[0], 0, Nn.park.gate[1] + 4.0), "facing": PI})
		out.append({"name": "Park Güell, the square", "pos": Vector3((Nn.park.square[0] + Nn.park.square[2]) / 2.0, 0, (Nn.park.square[1] + Nn.park.square[3]) / 2.0), "facing": PI})
	return out


func teleport(pos: Vector3, facing: float) -> void:
	# (the debug menu) straight there, out of doors
	if where == "in":
		room_nodes[room].visible = false
		room_lights[room].visible = false
		npcs.leave_room()
		game.on_exit_to_world()
		room = ""
		where = "out"
		indoor.visible = false
		outdoor.visible = true
		world_env.environment = env_out
		ambience.set_outdoors(true)
		cam.current = true
	if street.riding != null:
		bike_key()
	player.global_position = pos
	player.velocity = Vector3.ZERO
	speed = 0.0
	model.rotation.y = facing
	move_dir = Vector2(sin(facing), cos(facing))
	cam_yaw_node.rotation.y = facing + PI
	cam_pitch_node.rotation.x = clampf(cam_pitch_node.rotation.x, -1.15, 0.3)    # (out of a room's look up into its vaults)
	cam_vel = 0.0
	snap_height()
	last_banner = ""
	show_banner(street_name(pos))


var fp_since := 0.0               # (round 41) when she last came into a first-person place
var arm_tip := 0.0                # (round 35) the camera arm's extra tip down, rising over a slope behind her
var tip_goal := 0.0               # (round 39) the tip it is easing to, held until a lesser one has been clear for 0.5 s
var tip_clear_t := 0.0
func arm_blocked(tip: float) -> float:
	# how far back along the camera's arm, tipped down by `tip`, the ground or a roof's ceiling is in the way (INF:
	# nowhere) — the ground only a little above it, as on a slope, not a terrace far overhead (the Sagrat Cor's crypt
	# roof over its porch, which the camera is in front of, not inside). (Round 40: no walls or boxes any more, rule 03
	# #17; a roof she is under keeps the camera under its ceiling, #16b.)
	var adir: Vector3 = (cam_pitch_node.global_basis * Basis(Vector3.RIGHT, tip)).z
	var ao := arm.global_position
	var l := 0.6
	while l <= arm.spring_length:
		var q := ao + adir * l
		var th := terrain_at(q.x, q.z)
		# (round 41: riding the funicular, along its cutting the ground is the cutting's floor, not the hill's height
		# grid, which near the top stands 8 m over the line and pulled the camera into the car)
		if ride_inside and north and north.has_method("cutting_floor"):
			var cf: float = north.cutting_floor(q.x, q.z)
			if not is_nan(cf):
				th = cf
		# (round 41: riding the funicular nothing overhead is a terrace she is under — the plateau's mass above the
		# line's top is ground, and the camera comes in rather than into it)
		if q.y < th + 0.35 and (th - q.y < 2.5 or ride_inside):
			return l
		for rf in cam_roofs.get(Vector2i(floori(q.x / 4.0), floori(q.z / 4.0)), []):
			if q.y > float(rf.ceil) - 0.3 and q.y < float(rf.top) + 0.3 and Geometry2D.is_point_in_polygon(Vector2(q.x, q.z), rf.poly):
				return l
		l += 0.2                                   # (round 39: finer, so the arm's length doesn't step 40 cm at a time)
	return INF


func snap_height() -> void:
	# (round 35, the everything-visit: out of a door or put somewhere up a hill — the Sagrat Cor at 78 m, the park —
	# her model and the camera started at street level and rose to her through the hill for half a second, the view
	# from under the funfair upside down if the camera was tipped up; both start at her height now)
	var gh := ground_at(player.global_position)
	model.position.y = gh
	cam_root.global_position = player.global_position + Vector3(0, CAM_PIVOT_H + gh, 0)


# ------------------------------------------------------------------ input

func held(k: Key) -> bool:
	return (Input.is_physical_key_pressed(k) and not testing) or vkeys.has(k)


func pad_axis(a: JoyAxis) -> float:
	var v := Input.get_joy_axis(0, a)
	return 0.0 if absf(v) < 0.18 else (v - signf(v) * 0.18) / 0.82


func walk_keys() -> Vector2:
	# (round 41, the viewfinder) W A S D and the pad's left stick only: in the camera they walk, the arrows look
	var v := Vector2(pad_axis(JOY_AXIS_LEFT_X), -pad_axis(JOY_AXIS_LEFT_Y))
	if held(KEY_W): v.y += 1.0
	if held(KEY_S): v.y -= 1.0
	if held(KEY_A): v.x -= 1.0
	if held(KEY_D): v.x += 1.0
	return v.limit_length(1.0)


func look_keys() -> Vector2:
	var v := Vector2.ZERO
	if held(KEY_UP): v.y += 1.0
	if held(KEY_DOWN): v.y -= 1.0
	if held(KEY_LEFT): v.x -= 1.0
	if held(KEY_RIGHT): v.x += 1.0
	return v.limit_length(1.0)


func vf_walking() -> bool:
	# W A S D walk her in the viewfinder only where she could walk anyway (not on a bench, a ride or the bike)
	return vf_on and not ride_cam and not (benches and benches.seated()) and street.riding == null


func move_input() -> Vector2:
	var v := Vector2(pad_axis(JOY_AXIS_LEFT_X), -pad_axis(JOY_AXIS_LEFT_Y))
	if held(KEY_W) or held(KEY_UP): v.y += 1.0
	if held(KEY_S) or held(KEY_DOWN): v.y -= 1.0
	if held(KEY_A) or held(KEY_LEFT): v.x -= 1.0
	if held(KEY_D) or held(KEY_RIGHT): v.x += 1.0
	return v.limit_length(1.0)


func input_key(code: int) -> void:
	# (for the tests: a key press, as if typed)
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.pressed = true
	feeding = true
	_unhandled_input(ev)
	feeding = false


var testing: bool = Array(OS.get_cmdline_user_args()).filter(func(a): return a not in ["--touch", "--debug"]).size() > 0     # a test run: the real keyboard and mouse are ignored
var debug_on: bool = (testing and not "--nodebug" in OS.get_cmdline_user_args()) or "--debug" in OS.get_cmdline_user_args()     # the debug menu, hidden from players (rule 08 #84a; tests: --nodebug plays as a player)
var feeding := false                                      # (a key from the test itself)


func _unhandled_input(e: InputEvent) -> void:
	if testing and not feeding and (e is InputEventKey or e is InputEventMouseButton or e is InputEventMouseMotion):
		return                                            # (a test window that pops up mustn't catch the user's typing)
	if sleeping:
		return
	var confirm := false
	if panels and panels.is_open():
		if e is InputEventKey and e.pressed:
			panels.key(e.keycode)
		elif e is InputEventJoypadButton and e.pressed:
			panels.key({JOY_BUTTON_A: KEY_ENTER, JOY_BUTTON_B: KEY_ESCAPE, JOY_BUTTON_DPAD_UP: KEY_UP, JOY_BUTTON_DPAD_DOWN: KEY_DOWN,
				JOY_BUTTON_DPAD_LEFT: KEY_LEFT, JOY_BUTTON_DPAD_RIGHT: KEY_RIGHT}.get(e.button_index, KEY_NONE))
		return
	if e is InputEventKey and e.pressed and not e.echo:
		if vf_on and not dlg_open:
			# (round 41, the user: "have Z to zoom and E to take the picture") Esc (or Backspace) puts the camera away
			if e.keycode in [KEY_E, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE]:
				if not photo_on:
					take_photo()
			elif e.keycode == KEY_Z:
				vf_zoom = not vf_zoom
				ambience.sfx("page")
			elif e.keycode in [KEY_ESCAPE, KEY_BACKSPACE]:
				viewfinder(false)
			return
		if north and north.has_method("scope_active") and north.scope_active() and not dlg_open:
			if e.keycode in [KEY_E, KEY_ESCAPE, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE, KEY_BACKSPACE]:
				north.end_scope()                       # (round 25: stepping back from the telescope)
			return
		if map_panel.visible and e.keycode in [KEY_ESCAPE, KEY_ENTER, KEY_KP_ENTER, KEY_E, KEY_SPACE, KEY_BACKSPACE]:
			map_panel.visible = false                       # Esc or Enter puts the map away, as in the 2D game
			ambience.sfx("back")
			return
		confirm = e.keycode in [KEY_E, KEY_ENTER, KEY_KP_ENTER] or (dlg_open and e.keycode == KEY_SPACE)
		if dlg_open and not choice_box.visible and e.keycode in [KEY_ESCAPE, KEY_BACKSPACE]:
			confirm = true                                  # Esc, like Enter, moves a talk on (and closes the last page)
			if dlg_who.text == "Journal":
				# and closes the journal altogether
				game.q = game.q.filter(func(x): return not (x.k == "page" and x.who == "Journal"))
		if dlg_open and choice_box.visible:
			if e.keycode in [KEY_UP, KEY_W]:
				move_choice(-1)
			elif e.keycode in [KEY_DOWN, KEY_S]:
				move_choice(1)
			elif e.keycode >= KEY_1 and e.keycode < KEY_1 + dlg_choices.size():
				dlg_choice = e.keycode - KEY_1
				confirm = true
			elif e.keycode in [KEY_ESCAPE, KEY_BACKSPACE]:
				dlg_choice = dlg_choices.size() - 1        # backing out: the last option is always "no" / "close"…
				for i in dlg_choices.size():
					if String(dlg_choices[i]) == "Resume":
						dlg_choice = i                      # …except in the pause menu, where it is Resume (round 20e:
						break                               # backing out of it used to ask about a new game)
				confirm = true
		if not dlg_open:
			match e.keycode:
				KEY_T:
					next_time_stop()
				KEY_G:                                   # (G, V and Q only with the debug menu on: rule 08 #77a)
					if debug_on:
						env_out.sdfgi_enabled = not env_out.sdfgi_enabled
				KEY_V:
					if debug_on:
						env_out.volumetric_fog_enabled = not env_out.volumetric_fog_enabled
				KEY_Q:
					if debug_on:
						set_quality(not high_quality)
				KEY_C:
					show_skin(skin_idx + 1)
				KEY_I:
					game.bag_panel()
				KEY_TAB, KEY_M:                              # (M is the map, as in the 2D game)
					map_panel.visible = not map_panel.visible
					ambience.sfx("open" if map_panel.visible else "back")
				KEY_J:
					game.journal_panel()
				KEY_N:                                       # (N the music, as in the 2D game)
					toggle_music()
				KEY_B:
					bike_key()
				KEY_P:
					if debug_on:
						panels.open_debug()
				KEY_H:
					take_me_home()
				KEY_ESCAPE:
					if map_panel.visible:
						map_panel.visible = false
					elif Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
						Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
					else:
						pause_menu()
	elif e is InputEventJoypadButton and e.pressed:
		if vf_on and not dlg_open:
			if e.button_index == JOY_BUTTON_A and not photo_on:
				take_photo()
			elif e.button_index == JOY_BUTTON_X:
				vf_zoom = not vf_zoom
			elif e.button_index == JOY_BUTTON_B:
				viewfinder(false)
			return
		if e.button_index in [JOY_BUTTON_A, JOY_BUTTON_X]:
			confirm = true
		elif dlg_open and e.button_index == JOY_BUTTON_DPAD_UP:
			move_choice(-1)
		elif dlg_open and e.button_index == JOY_BUTTON_DPAD_DOWN:
			move_choice(1)
	elif touch_on and (e is InputEventMouseMotion or (e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT)):
		pass                                              # (on a touch screen a tap also comes as a click: it mustn't grab the mouse)
	elif e is InputEventMouseButton and e.pressed:
		if e.button_index == MOUSE_BUTTON_LEFT:
			# (round 38, the user: "clicking again doesn't unmove you. You have to press escape… You should be able to
			# click again and undo this") a click takes the mouse for steering, another click gives it back
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED else Input.MOUSE_MODE_CAPTURED
		elif e.button_index == MOUSE_BUTTON_WHEEL_UP:
			cam_len = clampf(cam_len * 0.9, 2.2, 9.0)
		elif e.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			cam_len = clampf(cam_len * 1.1, 2.2, 9.0)
	elif e is InputEventMouseMotion:
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED or (e.button_mask & MOUSE_BUTTON_MASK_RIGHT) != 0:
			if vf_on:
				vf_yaw -= e.relative.x * MOUSE_SENS
				vf_pitch = clampf(vf_pitch - e.relative.y * MOUSE_SENS, -1.45, 1.45)
			else:
				turn_camera(-e.relative.x * MOUSE_SENS, -e.relative.y * MOUSE_SENS)
	if confirm:
		if dlg_open:
			dialog_next()
		elif benches and benches.seated():
			benches.stand()                            # (round 41: E gets her up off the bench)
		elif ride_cam and ride_inside:
			# (round 41, the user: in the funicular "If she can look out from the inside… As well as the third person")
			# E: her seat inside, looking out, or back to following the car (the world's ride_toggle)
			if north and north.has_method("ride_toggle"):
				north.ride_toggle()
		elif ride_cam:
			# (round 26, the user: in the funicular "the only option E should be to look around, which makes it first
			# person") E swaps between her seat and her own eyes; the mouse looks out
			ride_look = not ride_look
			model.visible = not ride_look
			last_manual_cam = t
			ambience.sfx("page")
		elif not busy:
			interact()


func turn_camera(dyaw: float, dpitch: float) -> void:
	if not free_cam():
		return
	cam_yaw_node.rotation.y += dyaw
	if ride_cam and ride_inside and not ride_look:
		dpitch = -dpitch                               # (round 41, the user: following the funicular from outside, up and down "are opposite to what it looks like inside… inside is correct")
	if fp_on or (speed > 0.4 and keys.length() > 0.08 and street.riding == null):
		move_dir = move_dir.rotated(-dyaw)             # running, she steers with the camera (round 39: at her eyes, always)
	# (look up into the vaults; round 41: on a ride, looking out with her own eyes, up as well as round)
	var lo_ := -PI / 2.0 + 0.1 if ride_look else -1.15          # (round 41: at her eyes on a ride or a bench, straight up and down alike)
	cam_pitch_node.rotation.x = clampf(cam_pitch_node.rotation.x + dpitch, lo_, PI / 2.0 - 0.1 if ride_look else (0.3 if where == "out" and not fp_on else 0.95))
	last_manual_cam = t


# ------------------------------------------------------------------ movement

func steer_walk(inp: Vector2, dt: float) -> float:
	# Which way she goes on foot; returns how fast she is turning (rad/s).
	# - Setting off, the keys mean what the screen shows (and always indoors, where the camera is fixed).
	# - Running, left and right with forward (or back) held steer her: straight away, then faster the
	#   longer they are held.
	# - A side key on its own (no forward) turns her straight to that side of the screen, quickly, like the
	#   about-turn below; then she runs straight on that way (no slow curving, as if forward were held).
	# - Forward keeps her going straight on, however the camera is turned.
	# - Pressing back turns her round to run towards the camera, once, quickly; then she runs straight
	#   on while the camera swings round behind her.
	var cam_yaw := cam_yaw_node.rotation.y if free_cam() else 0.0
	var screen := Vector2(cos(cam_yaw), -sin(cam_yaw)) * inp.x + Vector2(-sin(cam_yaw), -cos(cam_yaw)) * inp.y
	var back_pressed := inp.y < -0.3 and prev_keys.y >= -0.3
	var side_only := absf(inp.x) > 0.3 and absf(inp.y) < 0.3
	var side_pressed := side_only and not (absf(prev_keys.x) > 0.3 and absf(prev_keys.y) < 0.3)
	prev_keys = inp
	if inp.length() < 0.08:
		side_held = 0.0
		keys_held = 0.0
		back_dir = Vector2.ZERO
		side_first = false
		turn_vel = move_toward(turn_vel, 0.0, STEER_EASE * dt)
		return 0.0
	if absf(inp.x) < 0.3:
		side_first = false                                # the side key is up again: steering is hers on the next press
	elif side_only:
		side_first = true                                 # side held with no forward: adding forward must not swing her
	keys_held += dt
	# setting off from standing, the keys mean the screen; held against a wall or a column she's still
	# "running", so left and right go on steering her away from it
	if speed < 0.4 and keys_held < 0.3:
		move_dir = screen.normalized()                    # setting off
		turn_vel = 0.0
		side_held = 0.0
		back_dir = Vector2.ZERO
		return 0.0
	if not free_cam() or back_pressed or side_pressed:
		back_dir = screen.normalized()
	if back_dir != Vector2.ZERO:
		# turning round to where the keys point on screen
		var ang := move_dir.angle_to(back_dir)
		var step: float = TURN_RATE * dt * (1.0 + absf(ang))
		var turn := clampf(ang, -step, step)
		move_dir = move_dir.rotated(turn)
		turn_vel = 0.0
		if absf(ang) > 2.5:
			speed *= 0.85                                 # a sharp about-turn costs a little speed
		if free_cam() and absf(ang) < 0.02:
			back_dir = Vector2.ZERO                       # round: from now on, straight on
		return turn / dt
	var side := clampf(inp.x * 1.42, -1.0, 1.0)
	var want := 0.0
	if absf(side) > 0.1 and not side_only and not side_first:
		side_held += dt
		if where == "in":
			want = side * minf(ROOM_STEER[2], ROOM_STEER[0] + ROOM_STEER[1] * side_held)
		else:
			# (round 27, the user: "if I start running and then press a side arrow key very quickly after, it
			# should turn quicker, in order to navigate narrow places") just after setting off the side keys
			# bite hard; once she has run for a bit, the usual gentle curve (holding still grows it)
			var fresh := clampf(1.0 - maxf(keys_held - QUICK_HOLD, 0.0) / QUICK_FOR, 0.0, 1.0)
			var bite := lerpf(STEER_BITE, STEER_QUICK, fresh)
			want = side * minf(STEER_MAX, maxf(bite, STEER_BITE + STEER_GROW * side_held))
	else:
		side_held = 0.0
	turn_vel = move_toward(turn_vel, want, STEER_EASE * (2.0 if where == "in" else 1.0) * dt)
	move_dir = move_dir.rotated(turn_vel * dt)
	return turn_vel


var soft_block_t := 0.0          # (round 27) how long she has been pressing against someone or her bike, going nowhere
var soft_pass_t := 0.0           # while this runs she slips through the soft thing in her way (never walls or buildings)


func keep_off_people(gap: float) -> void:
	# people (and her parked bike) are solid: their own bodies stop her when she walks at them; but pressed
	# against one for a few seconds and going nowhere, she slips through — so a person or the bike can never
	# pin her in a corner (the user's rule; it never applies to buildings, bins or walls)
	if soft_pass_t > 0.0:
		return
	var p := player.global_position
	var others: Array = []
	for id in npcs.current():
		var q: Dictionary = npcs.current()[id]
		if not q.is_empty() and q.holder.visible:
			others.append(q.holder.global_position)
	if where == "out":
		for w in people.people:
			if w.holder.visible:
				others.append(w.holder.global_position)
		if street.riding == null and street.own_bike != null and street.own_bike.visible:
			others.append(street.own_bike.global_position)
	var pushed := false
	for o in others:
		var d := Vector2(p.x - o.x, p.z - o.z)
		if d.length_squared() < gap * gap and absf(p.y + model.position.y - o.y) < 1.2:
			var n := d.normalized() if d.length() > 0.01 else -move_dir
			var out := Vector2(o.x, o.z) + n * gap
			player.global_position = Vector3(out.x, p.y, out.y)
			p = player.global_position
			pushed = true
	if pushed and keys.length() > 0.1 and speed < 0.35:
		soft_block_t += get_physics_process_delta_time()
		if soft_block_t > 2.2:
			soft_pass_t = 1.3
			soft_block_t = 0.0
	else:
		soft_block_t = maxf(0.0, soft_block_t - get_physics_process_delta_time() * 2.0)


func shove_people(dt: float) -> void:
	# (round 37, the user) walking or riding into someone, they give way at her pace (round 38: from the front a step
	# back and to the side, facing her; from behind they walk on forward, then turn to her); she slows (on foot to a walk; the bike keeps rolling, slowed, not stopped dead).
	# Only on contact and only what she is moving into — never from a distance, like the lost dog shying away. They
	# never step into a wall, a trunk or a solid thing: then sideways, or not at all (keep_off_people's slip-past
	# still frees her). Never while they are talking to her or playing a part in a scene.
	if keys.y < 0.1 or soft_pass_t > 0.0:
		return                                         # (pressing forward: held up against them, her speed may be nil)
	var on_bike: bool = street.riding != null
	var p := player.global_position
	var fwd := Vector3(move_dir.x, 0, move_dir.y)
	var gap: float = (0.85 if on_bike else R + 0.28) + 0.3      # (their bodies stop her a little before arm's length)
	var pace: float = clampf(speed, 0.9 if on_bike else 0.8, 3.0 if on_bike else 1.3)
	var all: Array = []
	for id in npcs.current():
		var q: Dictionary = npcs.current()[id]
		if not q.is_empty() and q.holder.visible and not q.talking and String(q.get("mode", "")) == "":
			all.append(q)
	if where == "out":
		for w in people.people:
			if w.holder.visible and float(w.get("talking", -1.0)) <= -1.0:
				all.append(w)
	var space := get_world_3d().direct_space_state
	var pushing := false
	for q in all:
		var o: Vector3 = q.holder.global_position
		var d := Vector3(o.x - p.x, 0, o.z - p.z)
		var dist := d.length()
		if dist > gap or dist < 0.01 or absf(p.y + model.position.y - o.y) > 1.2:
			continue
		var n := d / dist
		if n.dot(fwd) < 0.35:
			continue
		var side := Vector3(-n.z, 0, n.x) * (1.0 if Vector3(-n.z, 0, n.x).dot(fwd) < 0.0 else -1.0)   # (the side she isn't heading)
		var way := Vector3.ZERO
		var hemmed: bool = people.blocked_at(o, 0.25)     # (one who stands at a stall or a table is already within its reach)
		# (round 38, the user) run into from the front, they take a step back as they're pushed to the side, facing her;
		# from behind, they walk on forward out of her way, then turn to face her
		var qy: float = float(q.get("yaw", 0.0))
		var behind: bool = Vector3(sin(qy), 0, cos(qy)).dot(n) > 0.25
		var run: float = float(q.get("shove_run", 0.0)) if float(q.get("shoved_t", 0.0)) > 0.0 else 0.0
		var tries: Array
		if behind:
			tries = [(n + side * 0.5).normalized(), n, side, -side] if run < 1.2 else [(side + n * 0.4).normalized(), side, -side]
		else:
			tries = [(n * 0.9 + side).normalized(), side, n, -side]
		for c in tries:
			var to: Vector3 = o + c * 0.45
			if not hemmed and people.blocked_at(to, 0.25):
				continue
			var ray := PhysicsRayQueryParameters3D.create(o + Vector3(0, 0.6, 0), to + Vector3(0, 0.6, 0), LAYER_BODY)
			ray.exclude = [player.get_rid()] + ([q.body.get_rid()] if q.has("body") else [])
			# (round 40, rule 10 #16a: pushed, they never go into a wall — the whole of them, not a thin line)
			if space.intersect_ray(ray).is_empty() and person_fits(to):
				way = c
				break
		if way == Vector3.ZERO:
			continue
		var stepv: Vector3 = way * pace * dt
		q.holder.global_position += stepv
		q.shove = (q.get("shove", Vector3.ZERO) as Vector3) + stepv
		q.shove_run = run + stepv.length()
		q.shoved_t = 0.45
		if behind:
			q.shove_face = atan2(way.x, way.z)                               # (walking on, the way they're pushed)
			q.after_face = atan2(-n.x, -n.z)                                 # (then turning to her)
		else:
			q.shove_face = atan2(-n.x, -n.z)                                 # (facing her as they step back)
			q.erase("after_face")
		pushing = true
	if pushing:
		speed = minf(speed, pace)
		var hv := Vector2(player.velocity.x, player.velocity.z)
		if hv.length() > pace:
			hv = hv.normalized() * pace
			player.velocity.x = hv.x
			player.velocity.z = hv.y


func add_bike_body(bk: Node3D) -> void:
	# while she rides, the bike's wheels bump into things too, not just Sandra (they turn with the bike)
	remove_bike_body()
	for w in [bk.front, bk.rear]:
		if w == null:
			continue
		var cs := CollisionShape3D.new()
		var ball := SphereShape3D.new()
		ball.radius = 0.27
		cs.shape = ball
		var off := model.to_local(w.global_position)
		cs.set_meta("off", Vector3(off.x, 0.4, off.z))
		player.add_child(cs)
		bike_body.append(cs)
	place_bike_body()


func remove_bike_body() -> void:
	for cs in bike_body:
		cs.queue_free()
	bike_body.clear()


func place_bike_body() -> void:
	for cs in bike_body:
		cs.position = Basis(Vector3.UP, model.rotation.y) * cs.get_meta("off")


var bike_glide := 0.0              # (round 25) speed carried on from riding down a hill, wearing off (1 -> 0)
const BIKE_GLIDE_EASE := 0.7       # m/s each second it eases back to the usual speed after a hill


func ride(inp: Vector2, dt: float) -> float:
	# On the bike she rides it like a bike, not like walking: forward pedals, back brakes, and left and
	# right lean her into a turn, so she always goes where the front wheel points. It never turns on the
	# spot while moving or slides sideways; held back, it brakes, then rolls slowly backwards. The turn is
	# tight when slow and wide when fast. Stopped, the side keys turn the bike round on the spot, and the
	# camera stays put (so you can turn her to face it); it swings back behind her once she rides off.
	# Off the road (pavements, garden paths, grass) she goes 40% slower.
	# (the keys are read separately: forward and right together is full pedalling and full lean)
	var pedal := clampf(inp.y * 1.42, -1.0, 1.0)
	var rough := ground_at(player.global_position) > 0.01      # off the road: pavement, garden paths, grass
	var top: float = street.BIKE_SPEED * (street.BIKE_ROUGH if rough else 1.0) * (BOOST_K if boost > 0.0 else 1.0)   # (round 41: the food's boost too)
	var cornering := absf(bike_steer) > 0.35
	var downhill := false
	if where == "out":
		# (round 25, the user) up a hill she pedals 20% slower than she walks; down one she goes 30% faster than she
		# rides the streets, except round the bends, where it's the path's usual speed; and what she gathers coming
		# down wears off gradually, so she carries it on across the pavement and down the street
		# (round 27, the user: "she goes very fast on any downhill… make the speed multiplier based on the size
		# of the slope", and on the surface's own speed, not the road's)
		var here := player.global_position
		var rise := (terrain_at(here.x + move_dir.x * 0.8, here.z + move_dir.y * 0.8) - terrain_at(here.x, here.z)) / 0.8
		if rise > 0.02:
			top = lerpf(top, minf(top, SPEED * 0.8), clampf((rise - 0.02) / 0.10, 0.0, 1.0))
		elif rise < -0.03 and speed > 0.5 and not cornering:
			top = top * (1.0 + 0.8 * clampf((-rise - 0.03) / 0.19, 0.0, 1.0))     # (round 41, the user: "faster": +45% → +80%)
			bike_glide = 1.0
			downhill = true
	bike_glide = maxf(0.0, bike_glide - dt * 0.12)
	var target := 0.0
	if pedal > 0.1:
		target = top * pedal
	# (steering alone she stops pedalling; once stopped, the side keys turn the bike round on the spot)
	if speed > top + 0.1:
		if bike_glide > 0.0 and not cornering and pedal > -0.1:
			speed = move_toward(speed, top, BIKE_GLIDE_EASE * dt)       # (carried on from the hill)
		else:
			speed = move_toward(speed, top, street.BIKE_BRAKE * 0.5 * dt)    # bumping up onto the pavement; a bend
	elif pedal < -0.1:
		# back brakes; held on once stopped, she pushes the bike slowly backwards (to get away from a wall)
		speed = move_toward(speed, 0.0 if speed > 0.05 else -street.BIKE_BACK, (street.BIKE_BRAKE if speed > 0.05 else 3.0) * -pedal * dt)
	elif speed < target:
		speed = move_toward(speed, target, street.BIKE_ACCEL * (2.5 if downhill else 1.0) * dt)   # (the hill helps her down)
	else:
		speed = move_toward(speed, target, street.BIKE_COAST * dt)
	if inp.length() > 0.08:
		face_target = INF
	# leaning in and straightening up take a moment
	var want := clampf(inp.x * 1.42, -1.0, 1.0)
	bike_steer = move_toward(bike_steer, want, dt * (3.0 if absf(want) > absf(bike_steer) else 4.5))
	# the turn is tight when slow and wide when fast (and turns the other way when backing)
	var rate: float = bike_steer * (speed / (street.BIKE_MIN_RADIUS + absf(speed) * street.BIKE_RADIUS_GROW)
		+ street.BIKE_SPIN * (1.0 - clampf(absf(speed) / 0.8, 0.0, 1.0)))
	bike_pedalling = pedal > 0.1
	move_dir = move_dir.rotated(rate * dt)
	return rate


func _physics_process(dt: float) -> void:
	t += dt
	if cutscene:
		if ride_cam:
			# (a ride: the wheel or the funicular carries her; round 23: the ride itself has to go on being moved here,
			# it used to stop dead with the rest of the world)
			# (round 41, the user: on the wheel "the only option is to either go first person or third person. Third
			# person follows her and left and right move around, or first person gives her view and she can look
			# around") the arrows or W A S D: left and right take the camera round her (or turn her head, looking
			# out), up and down tilt it; the mouse as ever
			var rk := Vector2.ZERO if (dlg_open or vf_on) else move_input()
			if rk.length() > 0.05:
				# (round 41, the user: "Change the look around on the furnicular to not be inverted") following the car,
				# → turns the view to the right
				# (then, of every first-person view — her seat in the funicular, the wheel's gondola, a bench: "could you make
				# the up and down inverted? And also have up and down arrows… They should all be the same") at her own eyes
				# ↑ looks up and ↓ looks down, the same in all of them, and following a ride from outside too (then: "I thought
				# the up arrow should look up. That's the opposite of what you had")
				turn_camera((rk.x if ride_inside and not ride_look else -rk.x) * 1.6 * dt, rk.y * 0.9 * dt)
			if benches and benches.seated():
				benches.clamp_look()
				if street and street.trufa:
					street.trufa.tick(dt)             # (round 41c, 10 #26a: the dog comes and sits at her feet)
			update_camera(dt, 0.0)
			animate_skin(dt, 0.0)
			north.tick(dt)
			people.tick(dt)
			npcs.tick(dt)
			game.tick(dt)
		elif north.has_method("scope_active") and north.scope_active():
			# (round 35, the everything-visit: at the coin telescope nothing ticked it, so the arrows didn't turn it
			# and the euro's minute never ran out)
			north.tick(dt)
		return
	var inp := Vector2.ZERO if (busy or dlg_open or vf_on) else move_input()
	if vf_walking() and not busy and not dlg_open:
		inp = walk_keys()
	keys = inp
	var on_bike: bool = street.riding != null
	var turning := 0.0
	player.collision_mask = LAYER_BODY | (LAYER_NOBIKE if on_bike else 0)
	fp_check(on_bike)
	if on_bike:
		turning = ride(inp, dt)
	elif vf_on:
		turning = vf_walk(inp, dt)                      # (round 41) with the camera up: where the viewfinder looks
	elif fp_on:
		turning = fp_walk(inp, dt)                      # (round 39) a first-person place: forward, back, turn
	else:
		if inp.length() > 0.08 and not dlg_open:
			face_target = INF
		turning = steer_walk(inp, dt)
		speed = move_toward(speed, SPEED * (BOOST_K if boost > 0.0 else 1.0) * (2.4 if debug_fast else 1.0) * inp.length(), (ACCEL if inp.length() > 0.08 else DECEL) * dt)
	turn_now = turning
	player.velocity.x = move_dir.x * speed
	player.velocity.z = move_dir.y * speed
	var on_deck := deck_at(player.global_position.x, player.global_position.z, model.position.y)
	if not is_nan(on_deck):
		# (round 34) on the covered walk's roof: flat built ground (no slope rule), and she doesn't step off its open
		# edge — where the next step leaves the roof for ground well below it, that part of her step is lost
		var pp0 := player.global_position
		var vv := Vector2(player.velocity.x, player.velocity.z)
		for axis: Vector2 in [Vector2(1, 0), Vector2(0, 1)]:
			var part: Vector2 = axis * vv.dot(axis)
			if part.length() < 0.001:
				continue
			var ahead: Vector2 = Vector2(pp0.x, pp0.z) + part.normalized() * 0.45
			if is_nan(deck_at(ahead.x, ahead.y, model.position.y)) and ground_at(Vector3(ahead.x, 0.0, ahead.y)) < on_deck - 0.8 \
					and not deck_drops(pp0.x, pp0.z):
				vv -= part
		player.velocity.x = vv.x
		player.velocity.z = vv.y
	elif north:
		# (round 22) the hillside: never up anything steep off the path; sliding down the steepest of it
		var hv: Vector2 = north.steer_on_slope(Vector2(player.velocity.x, player.velocity.z), player.global_position, dt)
		player.velocity.x = hv.x
		player.velocity.z = hv.y
	if is_nan(on_deck):
		rim_ahead(Vector2(player.velocity.x, player.velocity.z))   # (round 40: a raised platform's side stops her)
	if on_bike:
		model.rotation.y = atan2(move_dir.x, move_dir.y)
		place_bike_body()
	if not player.is_on_floor():
		player.velocity.y -= GRAVITY * dt
	shove_people(dt)
	player.move_and_slide()
	soft_pass_t = maxf(0.0, soft_pass_t - dt)
	keep_off_people(0.85 if on_bike else R + 0.28)
	var rv := player.get_real_velocity()
	var real_speed := Vector2(rv.x, rv.z).length()
	if not on_bike and (slipping or not fp_on):        # (round 39: a slip never starts in a first-person place — its columns stay solid; one already on still ends)
		slip_trees(inp, real_speed, dt)
	if on_bike and player.is_on_wall():
		# riding into a wall stops the bike rather than letting it slide along; brushing past one doesn't
		var along := Vector2(rv.x, rv.z).dot(move_dir)
		if absf(along) < absf(speed) - 0.5:
			speed = along
		# the edge of the thick of the wood, or of the sand: say why (now and then), so it isn't an invisible wall
		for i in player.get_slide_collision_count():
			var col := player.get_slide_collision(i).get_collider()
			if col is CollisionObject3D and col.collision_layer == LAYER_NOBIKE and t > nobike_said + 6.0:
				nobike_said = t
				var p := player.global_position
				var near_park := false
				for gr in D.get("north", {}).get("park", {}).get("gate_rects", []):
					if Vector2(p.x - (gr[0] + gr[2]) / 2.0, p.z - (gr[1] + gr[3]) / 2.0).length() < 4.0:
						near_park = true
				var fr: Array = D.get("north", {}).get("fair", {}).get("rect", [0, 0, 0, 0])
				var near_fair: bool = p.x > fr[0] - 3.0 and p.x < fr[2] + 3.0 and p.z > fr[1] - 3.0 and p.z < fr[3] + 3.0
				if near_park:
					toast("No bikes in Park Güell: hop off (%s) and walk in" % bike_word())
				elif near_fair:
					toast("No bikes in the funfair: hop off (%s) to walk" % bike_word())
				else:
					toast(("The wheels sink in the sand: hop off (%s) to walk" if p.z > 120.0 or street_name(p).begins_with("Platja")
						else "Too many trees to ride through: hop off (%s) to walk, or keep to the paths") % bike_word())
				break
	elif player.is_on_wall() and real_speed < speed - 0.5:
		speed = maxf(real_speed, speed * 0.6)             # pushing into a wall: don't keep building speed

	# body: catch up with the direction of travel, lean into turns, or face what she's talking to
	if on_bike:
		model.rotation.y = atan2(move_dir.x, move_dir.y)   # a bike goes where it points: no drifting
	elif face_target != INF:
		model.rotation.y = lerp_angle(model.rotation.y, face_target, 1.0 - exp(-8.0 * dt))
	elif fp_on:
		model.rotation.y = atan2(move_dir.x, move_dir.y)   # (round 39: her eyes are the camera; her turn is already eased)
	elif vf_walking():
		model.rotation.y = vf_yaw + PI                      # (round 41: with the camera up she faces the view, stepping aside or back)
	elif speed > 0.1:
		model.rotation.y = lerp_angle(model.rotation.y, atan2(move_dir.x, move_dir.y), 1.0 - exp(-MODEL_TURN * dt))
	# on the bike she leans into the turn, further the faster she goes
	# (stopped, the bike tips a little onto her foot on the ground)
	# (round 36, the user: "She still leans too much on the bike. Make the lean a little less.")
	# (round 37, the user: "Please make the bike not lean as much when she turns." About half again: 7° at most)
	var lean_to := bike_steer * (0.05 + 0.08 * clampf(speed / street.BIKE_SPEED, 0.0, 1.0)) * clampf(speed / 1.5, 0.0, 1.0) \
		- 0.07 * smoothstep(0.0, 1.0, street.rider_foot) if on_bike else clampf(turning * speed * 0.012, -0.14, 0.14)
	lean = lerpf(lean, lean_to, 1.0 - exp(-8.0 * dt))
	model.rotation.z = lean
	# (on the bike, a touch higher: the trodden paths, the meadow's paving and the grass stand a few
	# centimetres above the ground under them, and the tyres sank into them; round 20)
	var lift := 0.0
	var gh := ground_at(player.global_position)
	if on_bike:
		lift = bike_lift(player.global_position)
		# (round 38, the user: "the bike should never sink into the ground anywhere") it rides level, so on a slope or
		# across a kerb it stands on the higher of the ground under its two wheels, 0.55 m ahead and behind
		var wheel_off := Vector3(sin(model.rotation.y), 0.0, cos(model.rotation.y)) * 0.55
		gh = maxf(gh, maxf(ground_at(player.global_position + wheel_off), ground_at(player.global_position - wheel_off)))
	var dh := deck_at(player.global_position.x, player.global_position.z, model.position.y)
	if not is_nan(dh):
		gh = dh                                     # (round 34: up on the covered walk's roof)
	model.position.y = lerpf(model.position.y, gh + lift, 1.0 - exp(-14.0 * dt))

	# doors are walked through
	var lp := local_pos()
	if where == "out" and inp.length() > 0.1 and not on_bike:
		# only right at a door: within its width, and no further than half a metre out from the wall
		for d in D.entrances:
			var n := Vector2(d.normal[0], d.normal[1])
			var rel := Vector2(lp.x - d.pos[0], lp.z - d.pos[1])
			var out := rel.dot(n)
			if absf(rel.dot(Vector2(n.y, -n.x))) < d.size[0] / 2.0 + 0.15 and out < 0.55 and out > -0.4 and move_dir.dot(n) < -0.5:
				# (round 32's play-through: a locked door let her walk straight through it — E said "locked", her feet
				# didn't. Walked at, it does what E does: locked without the key, the key turns the first time.)
				var lk: String = d.get("lock", "")
				if lk != "":
					# (round 40, the user: "You should always have to press E to enter it. You can't just walk in like the
					# other ones") a locked door is never walked through, key or no key: E opens it (use); without the key,
					# walking at it says it's locked
					if not game.unlocked(lk) and t - door_said_t > 3.0 and not dlg_open:
						game.locked_door(lk)
					door_said_t = t
					break
				enter(d)
				break
		# the bridge to València is closed: Sergi, the guard, says so
		if D.has("bridge_rect"):
			var br: Array = D.bridge_rect
			if lp.x < br[2] - 9.0 and lp.x > br[0] and lp.z > br[1] - 1.0 and lp.z < br[3] + 1.0 and t - guard_t > 8.0 and not dlg_open:
				guard_t = t
				game.guard_stop()
	elif where == "in":
		var R: Dictionary = D.interiors[room]
		if R.exit != null and lp.z > R.h + 0.15 and move_dir.y > 0.3 and inp.length() > 0.1 and t - entered_at > 0.6:
			leave_by("bottom")
		for st in R.stairs:
			# walking up (or down) a stair takes her to the other floor, as a door does
			if st.has("rect") and not busy and inp.length() > 0.1 and t - entered_at > 0.8:
				var rc: Array = st.rect
				if lp.x > rc[0] and lp.x < rc[2] and lp.z > rc[1] and lp.z < rc[3] and move_dir.dot(Vector2(st.go[0], st.go[1])) > 0.6:
					ambience.sfx("door")
					enter_room(st.to, true)
					break
		if R.get("exit_top") != null and lp.z < 0.85 and move_dir.y < -0.3 and inp.length() > 0.1 and t - entered_at > 0.6:
			leave_by("top")

	animate_skin(dt, 0.0 if on_bike else (real_speed if player.is_on_floor() else 0.0))
	street.tick(dt)
	people.tick(dt)
	npcs.tick(dt)
	wildlife.tick(dt)
	touches.tick(dt)
	north.tick(dt)
	game.tick(dt)
	boost = maxf(0.0, boost - dt)
	stride += 0.0 if on_bike else real_speed * dt
	if stride > 0.85:                                  # one footstep per stride
		stride = 0.0
		ambience.footstep(where == "out" and ground_at(player.global_position) == 0.0)
	if real_speed < 0.2:
		stride = 0.6
	update_camera(dt, real_speed)


var cam_len := CAM_DIST          # how far back the camera is on foot (the wheel changes it)
var wood_k := 0.0                # (round 38) how far the camera has come down for the wood's shade, eased
var cam_fov := 62.0              # (round 38) a touch wider out in the world (CAM_FOV_OUT), eased
const BIKE_CAM := 1.5            # on the bike it pulls back this much further, and stays there until she gets off

# (round 39, the user, on Casa Trias's porch: "when she does walk into here, it should become first person and the arrow
# keys just move forward and backwards. The camera doesn't work very well. It goes brown.") First-person places: a
# porch, a loggia — small built floors where the follow camera can only end up in a column or a wall. Walking in, the
# camera glides to her eyes and she is hidden (as on a ride, 03 #28); forward and back walk her forward and backwards,
# left and right turn her (and the view) on the spot, the mouse turns her too; walking out, the camera glides back
# behind her. Scene 'first_person': [x0, z0, x1, z1, floor height] (a world's build writes them).
const FP_WALK := 2.4             # m/s forward there: a stroll (it is a porch, not a street)
const FP_BACK := 1.5             # m/s backwards
const FP_TURN := 1.9             # rad/s: left and right turn her on the spot
const FP_TURN_EASE := 8.0        # rad/s²: her turn comes on and dies away (rule 04 #1: nothing snaps)
const FP_PITCH := -0.22          # her eyes look out a touch down, so a balustrade she stops at is in view
const FP_ARM := 0.22             # the camera this far behind her middle (her eyes, hidden): never nose-to-the-wall
const FP_EYE := -0.08            # and this much lower than the follow camera's pivot (her eyes, not her crown)
const FP_EASE := 2.5             # how quickly the camera goes to her eyes and back (with the arm's own glide, ~1 s)
var fp_on := false               # she is in a first-person place: the keys are forward, back and turn
var fp_k := 0.0                  # 0..1, how far the camera has gone to her eyes (eased both ways)
var fp_pitch_back := NAN         # the camera's tip as she came in, given back as she leaves


func fp_rects() -> Array:
	var rs: Array = D.get("first_person", [])
	if rs.is_empty() and D.get("north", {}).get("park", {}).has("steps"):
		# (round 39: until the build writes scene 'first_person' — REMOVE THEN) Casa Trias's loggia, as the Meshy
		# model has it: inside its walls, from its back wall to its front's plinth; its floor at 23.55 m
		rs = [[150.95, -228.85, 158.95, -222.55, 23.55]]
	return rs


func fp_check(on_bike: bool) -> void:
	# in a first-person place or not (a little apart going in and out, so its edge doesn't flicker), and what changes
	# as she crosses its edge
	var was := fp_on
	var inside := false
	if where == "out" and not on_bike and not ride_cam and not cutscene:
		var p := player.global_position
		var g := 0.25 if was else 0.0
		for r in fp_rects():
			if p.x > float(r[0]) - g and p.x < float(r[2]) + g and p.z > float(r[1]) - g and p.z < float(r[3]) + g \
					and model.position.y > float(r[4]) - 0.7:          # (up at its floor, not under it)
				inside = true
				break
	fp_on = inside
	if fp_on and not was:
		fp_since = t
		if is_nan(fp_pitch_back):
			fp_pitch_back = cam_pitch_node.rotation.x
		turn_vel = 0.0
	elif was and not fp_on:
		# walking out backwards, she turns round and walks on (as S does outside, 04 #15: towards the camera, which is
		# behind her as it comes out); every key she holds goes on meaning what it meant, with no lurch
		if speed < 0.0:
			move_dir = -move_dir
			speed = -speed
		turn_vel = 0.0
		keys_held = 1.0
		prev_keys = keys
		back_dir = Vector2.ZERO
		side_held = 0.0
		side_first = absf(keys.x) > 0.3 and absf(keys.y) < 0.3


func fp_walk(inp: Vector2, dt: float) -> float:
	# forward and back walk her forward and backwards; left and right turn her on the spot (and while walking)
	if inp.length() > 0.08 and not dlg_open:
		face_target = INF
	turn_vel = move_toward(turn_vel, clampf(inp.x, -1.0, 1.0) * FP_TURN, FP_TURN_EASE * dt)
	move_dir = move_dir.rotated(turn_vel * dt)
	var want := inp.y * (FP_WALK if inp.y > 0.0 else FP_BACK) if absf(inp.y) > 0.08 else 0.0
	speed = move_toward(speed, want, (ACCEL if absf(want) > absf(speed) and signf(want) == signf(speed) or speed == 0.0 else DECEL) * dt)
	prev_keys = inp
	keys_held = 1.0
	return turn_vel


func update_camera(dt: float, real_speed: float) -> void:
	if ride_look and not ride_cam:
		ride_look = false                              # (the ride ended while she was looking out)
		model.visible = true
	var want_len := (0.05 if ride_look else cam_len * (BIKE_CAM if street and street.riding else (1.6 if ride_inside else 1.0)))
	# (round 41: round the funicular's car, far enough out to frame all of it)
	# (round 39) in a first-person place the arm draws in to her eyes, and back out as she leaves, eased both ways
	fp_k = lerpf(fp_k, 1.0 if fp_on else 0.0, 1.0 - exp(-FP_EASE * dt))
	if not fp_on and fp_k < 0.002:
		fp_k = 0.0
	want_len = lerpf(want_len, FP_ARM, fp_k)
	arm.spring_length = lerpf(arm.spring_length, want_len, 1.0 - exp(-(9.0 if ride_look else (6.0 if fp_k > 0.0 else 2.5)) * dt))     # (a gentle glide out and back)
	# (round 35, the everything-visit: on a steep hillside, facing downhill, the camera behind her went into the slope
	# and the hill was seen from underneath. Where the ground is in the way, the camera first rises over it, tipping to
	# look down at her, smoothly; only if that isn't enough does it come in closer. Round 40: only the ground, and a
	# roof's ceiling she is under — no wall or box on the hill, rule 03 #17.)
	if fp_on:
		arm_tip = lerpf(arm_tip, 0.0, 1.0 - exp(-4.0 * dt))     # (round 39: at her eyes nothing is behind her to rise over)
		arm.rotation.x = arm_tip
	elif ride_cam and not ride_look:
		# (round 41, the user, on the funicular: "swing around so the camera is facing downhill… then immediately look to
		# the ground… it will pull you back down to neutral": the hill's rise-over-the-slope tip, eased in and out, moved
		# the view the player had just set) following a ride, the camera never tips by itself: only nearer, if the ground
		# is in the way
		arm_tip = 0.0
		arm.rotation.x = 0.0
		# (then: "could you make it so that the camera cannot move into the ground?": drawn in at once, not eased —
		# eased, it spent a third of the ride under the hillside as the view swung)
		var blr := arm_blocked(0.0)
		if not is_inf(blr):
			arm.spring_length = minf(arm.spring_length, maxf(0.6, blr - 0.3))
	elif where == "out" and not ride_look:
		# (round 40: under a roof, rising is no way out — the tip that leaves the arm longest wins when none is clear)
		var want_tip := 0.0
		var best_l := -1.0
		for tip in [0.0, -0.2, -0.4, -0.6]:
			var bl0 := arm_blocked(tip)
			if is_inf(bl0):
				want_tip = tip
				break
			if bl0 > best_l + 0.3:
				best_l = bl0
				want_tip = tip
		# (round 39, the user: "when I run up the stairs and the camera is over the edge a little bit, it starts jumping up
		# and down": it chose its tip afresh every frame and snapped the arm in, so on the stairs' edges it flicked between
		# tips — 10 jumps of up to 15 cm in 7 s, --stairscam) it tips down at once when it must, but only comes back up once
		# the lower tip has been clear for half a second; and the arm draws in quickly but smoothly, never in one frame
		if want_tip < tip_goal:
			tip_goal = want_tip
			tip_clear_t = 0.0
		elif want_tip > tip_goal:
			tip_clear_t += dt
			if tip_clear_t > 0.5:
				tip_goal = want_tip
				tip_clear_t = 0.0
		else:
			tip_clear_t = 0.0
		arm_tip = lerpf(arm_tip, tip_goal, 1.0 - exp(-4.0 * dt))
		arm.rotation.x = arm_tip
		var bl := arm_blocked(arm_tip)
		if not is_inf(bl):
			arm.spring_length = lerpf(arm.spring_length, maxf(0.6, bl - 0.3), 1.0 - exp(-6.0 * dt))
	elif arm_tip != 0.0:
		arm_tip = 0.0
		arm.rotation.x = 0.0
	# (round 38, the user: "When she runs into the forest, the camera should come down a little bit so that she can see
	# under the trees… This should be subtle.") in a wood's shade it eases down and looks a little more level, over a
	# few seconds; never where it is already rising over a slope
	wood_k = lerpf(wood_k, wood_shade(player.global_position) if where == "out" and not ride_look and not fp_on else 0.0, 1.0 - exp(-0.8 * dt))
	if wood_k > 0.002 and where == "out":
		arm.rotation.x = arm_tip + 0.07 * wood_k * clampf(1.0 + arm_tip / 0.2, 0.0, 1.0)
	# (round 35, the second look: the camera, which passes through people as through trees, ended up inside Agent
	# Bofarull's cap; anyone the camera is inside is not drawn while it is)
	# (round 36's play-through: in the Sagrada Família, walked round with the street camera, it came up right behind
	# Pau and his helmet filled a third of the screen; the rooms with that camera hide people too, and a little
	# further out: 0.8 m, was 0.6)
	if free_cam():
		var cp := cam.global_position
		var holders := []
		for q in (npcs.outdoor if where == "out" else npcs.indoor).values():
			if not q.is_empty() and not q.get("gone", false):
				holders.append(q.holder)
		if where == "out":
			for pp in people.people:
				if not pp.get("far", false):
					holders.append(pp.holder)
		for h in holders:
			if not is_instance_valid(h):
				continue
			var hp: Vector3 = (h as Node3D).global_position
			var inside := Vector2(cp.x - hp.x, cp.z - hp.z).length() < 0.8 and cp.y < hp.y + 2.0
			if inside and h.visible:
				h.visible = false
				h.set_meta("cam_hid", true)               # (only those hidden here are shown again here)
			elif not inside and h.has_meta("cam_hid"):
				h.visible = true
				h.remove_meta("cam_hid")
	# (round 35, the everything-visit: backed against a wall the camera's arm comes right in, into her hair; while it is
	# that close she isn't drawn, as in a first-person look, and comes back once it has room — a little apart, so it
	# doesn't flicker at the edge)
	if not ride_look and not ride_cam and not photo_on and not vf_on:
		var hl := arm.get_hit_length() if where == "out" or free_cam() else 9.0      # (a room's own camera: always drawn)
		# (round 39: going to her eyes in a first-person place, she goes before her head can fill the picture)
		var hide_at := 2.0 if fp_k > 0.0 else 1.0
		if model.visible and hl < hide_at:                # (her ponytail reaches back that far: round 35's second look)
			model.visible = false
		elif not model.visible and hl > hide_at + 0.15:
			model.visible = true
	if where == "in" and not free_cam():
		# from above the cut-away front wall, framing the room (bigger rooms: further back, following her more)
		var lp := local_pos()
		var R: Dictionary = D.interiors[room]
		var O := room_base(room)
		var sc := maxf(1.0, maxf(R.w / 14.0, R.h / 10.0))
		var cx: float = R.w / 2.0
		var cz: float = R.h / 2.0 + 0.5
		var follow := 0.25 + (sc - 1.0) * 0.4
		var pos := O + Vector3(cx + (lp.x - cx) * follow, 9.2 * sc, cz + 9.7 * sc + (lp.z - cz) * 0.2)
		var look := O + Vector3(cx + (lp.x - cx) * (follow + 0.05), 0.4, cz + 0.1 + (lp.z - cz) * 0.25)
		room_cam.global_position = room_cam.global_position.lerp(pos, minf(1.0, dt * 4.0)) if t - entered_at > 0.05 else pos
		room_cam.look_at(look, Vector3.UP)
		return
	var rx := pad_axis(JOY_AXIS_RIGHT_X)
	var ry := pad_axis(JOY_AXIS_RIGHT_Y)
	if (rx != 0.0 or ry != 0.0) and not vf_on:          # (in the viewfinder the stick turns it in _process: vf_look)
		turn_camera(-rx * PAD_SENS * dt, -ry * PAD_SENS * 0.6 * dt)
	# swing round behind her whichever way she is sent, unless the player has just turned the camera
	# themselves; the swing eases in, and is quicker when she's simply going forwards
	var on_bike: bool = street.riding != null
	# (on the bike only once she is riding forwards at a fair pace, so she can be turned round on the
	# spot to face the camera)
	var moving := (real_speed > 1.0 and keys.length() > 0.08) if not on_bike else (real_speed > 1.8 and speed > 0.0)
	if fp_on:
		# (round 39) at her eyes the view is where she faces: it comes round to her heading, gently while it is still
		# drawing in, then held to it (a lag at her eyes would swim); the mouse turns her with it (turn_camera)
		var face := atan2(move_dir.x, move_dir.y) + PI
		cam_yaw_node.rotation.y += wrapf(face - cam_yaw_node.rotation.y, -PI, PI) * (1.0 - exp(-lerpf(3.0, 30.0, fp_k * fp_k) * dt))
		swing = 0.0
		swing_sign = 0.0
		cam_vel = 0.0
		# it looks out nearly level as she comes in, and after that where the player tips it, held there (round 41, the
		# user: "it keeps resetting… all of the first person views": it used to ease back to level a moment later)
		if last_manual_cam < fp_since:
			cam_pitch_node.rotation.x = lerpf(cam_pitch_node.rotation.x, FP_PITCH, 1.0 - exp(-3.0 * dt))
	elif t - last_manual_cam > RECENTER_DELAY and moving:
		swing = move_toward(swing, 1.0, dt / 0.6)
		var behind := atan2(move_dir.x, move_dir.y) + PI
		var diff := wrapf(behind - cam_yaw_node.rotation.y, -PI, PI)
		if absf(diff) > 2.6 and swing_sign != 0.0 and signf(diff) != swing_sign:
			diff += swing_sign * TAU                  # nearly in front of her: keep going round the same way
		if absf(diff) > 0.05:
			swing_sign = signf(diff)
		var quick := CATCH_UP if (absf(keys.x) < 0.3 or on_bike) else 1.6      # quicker when she's going straight
		var pace := 1.0 if on_bike else real_speed / SPEED      # on the bike it keeps close behind her round turns
		var want_vel := diff * RECENTER_RATE * quick * pace * swing
		want_vel = clampf(want_vel, -SWING_MAX * quick, SWING_MAX * quick)
		var settle := sqrt(2.0 * CAM_ACCEL * absf(diff))          # slow down in time to stop right behind her
		want_vel = clampf(want_vel, -settle, settle)
		if absf(turn_now) < STEER_MAX + 0.5:
			want_vel -= turn_now * swing                          # and turn with her while she steers round
		# the swing speeds up and slows down smoothly, so the view never lurches
		cam_vel = move_toward(cam_vel, want_vel, CAM_ACCEL * dt)
		if signf(cam_vel) == signf(diff) and absf(cam_vel * dt) > absf(diff):
			cam_vel = diff / dt
		cam_yaw_node.rotation.y += cam_vel * dt
	else:
		swing = 0.0
		swing_sign = 0.0
		cam_vel = move_toward(cam_vel, 0.0, CAM_ACCEL * 2.0 * dt)
		if t - last_manual_cam > RECENTER_DELAY:
			cam_yaw_node.rotation.y += cam_vel * dt
	# a slightly lagging pivot that leads a little in the direction of travel
	var vel := player.get_real_velocity()
	look_ahead = look_ahead.lerp(Vector3(vel.x, 0, vel.z) * 0.18 * (1.0 - fp_k), 1.0 - exp(-3.0 * dt))   # (round 39: none at her eyes)
	if not fp_on and not is_nan(fp_pitch_back):
		# (round 39) out of a first-person place the camera tips back to where the player had it, eased
		if t - last_manual_cam < RECENTER_DELAY or absf(cam_pitch_node.rotation.x - fp_pitch_back) < 0.005:
			fp_pitch_back = NAN
		else:
			cam_pitch_node.rotation.x = lerpf(cam_pitch_node.rotation.x, fp_pitch_back, 1.0 - exp(-3.0 * dt))
	# (stepping off the bike, she moves half a step sideways at once: the camera follows her across at the pace it
	# zooms back in, so getting off is getting on in reverse rather than a jump)
	cam_slide = cam_slide.lerp(Vector3.ZERO, 1.0 - exp(-2.5 * dt))
	var ph := CAM_PIVOT_H if seat_eye < 0.0 else seat_eye     # (round 41: seated on a ride, at her own eyes)
	if ride_inside and not ride_look:
		ph += 0.8                                      # (round 41, the user: the funicular's outside view "pivot point a slightly bit more higher")
	var pivot := player.global_position + Vector3(0, ph + model.position.y - 0.3 * wood_k + FP_EYE * fp_k, 0) + look_ahead + cam_slide
	if ride_look and seat_eye >= 0.0:
		# (round 41, the user: "Can the first person view be a bit more forward, as if she's leaning forward… when you
		# turn left and right, you're sort of almost like spinning around the inside… closer to the edge, so you don't
		# have the orange at the bottom") her eyes leant out towards the rim the way she looks, so turning swings them
		# round the inside of the gondola
		var fwd := -cam_yaw_node.global_basis.z
		fwd.y = 0.0
		pivot += fwd.normalized() * seat_lean
	if ride_look and ride_inside:
		cam_root.global_position = pivot                # (round 41: on her seat in the moving funicular, no lag)
	else:
		cam_root.global_position = cam_root.global_position.lerp(pivot, 1.0 - exp(-10.0 * dt))


func set_touch(on: bool) -> void:
	# the on-screen controls on or off (touch.gd); on a computer the mouse then acts as a finger
	touch_on = on
	if on and touch_pad == null:
		var tl := CanvasLayer.new()
		tl.layer = 10                                   # (above the panels: the pad and A/B work them too)
		add_child(tl)
		touch_pad = Control.new()
		touch_pad.set_script(load("res://engine/touch.gd"))
		tl.add_child(touch_pad)
		touch_pad.setup(self)
		if not DisplayServer.is_touchscreen_available():
			Input.emulate_touch_from_mouse = true           # (the mouse acts as a finger)
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif not on and touch_pad:
		touch_pad.release_all()
		touch_pad.get_parent().queue_free()
		touch_pad = null
		Input.emulate_touch_from_mouse = false
		get_tree().root.content_scale_size = Vector2i(1280, 800)
		help.text = "WASD walk  ·  E talk / look / pick up  ·  I backpack  ·  J journal  ·  M map  ·  B bike  ·  H take me home  ·  Esc menu\n" + \
			"Click to steer with the mouse (click again or Esc frees it)  ·  wheel zoom" + ("  ·  P debug (outfit, music, time, quality…)" if debug_on else "")


func bike_word() -> String:
	# (the bike's key, as this device names it: B on a keyboard, BIKE on a touch screen, where B is "back")
	return "BIKE" if touch_pad else "B"


func play_area() -> Vector2:
	# the part of the screen the game shows in: all of it, except under the touch controls' deck when a phone
	# is held upright (touch.gd)
	var vs := get_viewport().get_visible_rect().size
	return Vector2(vs.x, vs.y - (touch_pad.deck if touch_pad else 0.0))


func fit_camera(c: Camera3D, fov: float) -> void:
	# upright, the picture is centred in the part above the deck, and shows a little more from top to bottom
	# there (the deck hides the bottom of the screen); otherwise an ordinary perspective
	var deck: float = touch_pad.deck if touch_pad else 0.0
	if deck <= 0.0:
		if c.projection != Camera3D.PROJECTION_PERSPECTIVE:
			c.projection = Camera3D.PROJECTION_PERSPECTIVE
		c.fov = fov
		return
	var vs := get_viewport().get_visible_rect().size
	var shown := vs.y - deck
	c.projection = Camera3D.PROJECTION_FRUSTUM
	c.keep_aspect = Camera3D.KEEP_HEIGHT
	c.size = 2.0 * c.near * tan(deg_to_rad(fov * 1.12) / 2.0) * vs.y / shown
	c.frustum_offset = Vector2(0.0, -(deck / 2.0) / vs.y * c.size)


# (round 23, the user: 18 fps in the wood) on a big Retina window there are four times the pixels to fill, and the
# wood's leaves fill most of them: the 3D view is drawn smaller and scaled up (FSR) while the frame rate is low, and
# back to full size when it recovers. The text and panels stay sharp.
const SCALE_MIN := 0.55
var scale_mode := Viewport.SCALING_3D_MODE_FSR
var scale_t := 0.0
var scale_frames := 0
var scale_good := 0               # (round 26) windows in a row with frames to spare
var scale_hold := 0.0             # seconds before it may go up again
var scale_low := 0                # (round 41) slow windows in a row


const SCALE_FILE := "user://display.cfg"


func load_render_scale() -> void:
	# (round 41, rule 02 #5c) start at the scale the last session settled on, so the title never steps down on screen
	if testing and not "--adaptive" in OS.get_cmdline_user_args():
		return
	var cf := ConfigFile.new()
	if cf.load(SCALE_FILE) == OK:
		get_viewport().scaling_3d_scale = clampf(float(cf.get_value("display", "render_scale", 1.0)), SCALE_MIN, 1.0)
		scale_hold = 8.0                  # (and it settles before going up again)


func adapt_render_scale(dt: float) -> void:
	if testing and not "--adaptive" in OS.get_cmdline_user_args():
		return
	# (rule 02 #5c: never while the title shows; then the user, on the Ferris wheel: "whole clumps of trees are jumping
	# from one bright color to one dark color… it may have been the picture quality adjusting" — nor on a ride, a
	# bench or through the camera, where the view is held and the eye is on it)
	if title_cam != null or ride_cam or vf_on or (benches and benches.seated()):
		scale_t = 0.0
		scale_frames = 0
		scale_low = 0
		return
	scale_t += dt
	scale_frames += 1
	if scale_t < 1.5:
		return
	var fps := scale_frames / scale_t
	scale_t = 0.0
	scale_frames = 0
	var vp := get_viewport()
	var s := vp.scaling_3d_scale
	# (round 26, the user: "flickering when I was on the bike with the small screen, but no longer when I made it
	# larger") it see-sawed: down below 40 fps, up again above 56, every 1.5 s, and each change made the whole picture
	# sharper or softer. Now it comes down as before, but only goes back up after 6 s in a row of plenty, by a little,
	# and never straight after coming down; and it stays FSR (no switch of how it scales at full size).
	# (round 41) down only after two slow windows in a row (3 s), and then in one step to about what should give
	# 50 fps, not three steps one after another (only part of a frame's cost shrinks with the picture: measured,
	# a step to the square root of the shortfall was too timid and it still came down three times)
	if fps < 40.0:
		scale_low += 1
		scale_good = 0
		if scale_low >= 2:
			s = minf(s - 0.08, s * fps / 50.0)
			scale_low = 0
			scale_hold = 8.0
	elif fps > 58.0:
		scale_low = 0
		scale_good += 1
		if scale_good >= 4 and scale_hold <= 0.0:
			s += 0.03
			scale_good = 0
	else:
		scale_good = 0
		scale_low = 0
	scale_hold -= 1.5
	s = clampf(s, SCALE_MIN, 1.0)
	if absf(s - vp.scaling_3d_scale) > 0.001:
		vp.scaling_3d_mode = scale_mode
		vp.scaling_3d_scale = s
		if not testing:
			var cf := ConfigFile.new()
			cf.set_value("display", "render_scale", s)
			cf.save(SCALE_FILE)


func _process(dt: float) -> void:
	if not photo_jobs.is_empty():
		collect_photo_jobs(false)
	adapt_render_scale(dt)
	limit_leaf_shadows(dt)
	update_door_glows(dt)
	cam_fov = lerpf(cam_fov, CAM_FOV_OUT if where == "out" else 62.0, 1.0 - exp(-3.0 * dt))
	vf_zoom_k = lerpf(vf_zoom_k, 1.0 if vf_on and vf_zoom else 0.0, 1.0 - exp(-8.0 * dt))
	fit_camera(cam, cam_fov)
	if vf_on and not vf_shutter and fade.color.a > 0.3:
		# (round 41c, the user: "when you transition, such as go into or out of a building or change on the gondola…
		# the camera mode should disappear") the screen going dark for a door, a ride's start or end, sleep: put away
		viewfinder(false)
	if vf_on:
		model.visible = false                         # (a ride or a bench may show her again: not into her own photo)
		vf_look(dt)
		place_vf_cam()
		if vf_draw:
			vf_draw.queue_redraw()                    # (the clock and the lens in its corner)
	fit_camera(room_cam, 42.0)
	door_light.light_energy = (0.9 + sin(t * 2.4) * 0.15) if P.night else (0.12 + sin(t * 2.4) * 0.04)
	if not busy and where == "out" and title_cam == null:
		show_banner(street_name(player.global_position))
	if banner_timer > 0.0:
		banner_timer -= dt
		if banner_timer <= 0.0:
			create_tween().tween_property(banner_panel, "modulate:a", 0.0, 0.6)
	var n := {} if (dlg_open or busy) else nearest()
	if vf_on and not dlg_open:
		var zl := "Zoom out" if vf_zoom else "Zoom in"      # (the user: "change it to zoom in and zoom out, depending…")
		prompt.text = ("[A]  Take the photo   ·   [X]  %s   ·   [B]  Put the camera away" % zl if touch_pad else
			("[E]  Take the photo   ·   [Z]  %s   ·   W A S D walk   ·   ← → ↑ ↓ look round   ·   [Esc]  Put the camera away" if vf_walking()
			else "[E]  Take the photo   ·   [Z]  %s   ·   ← → ↑ ↓ look round   ·   [Esc]  Put the camera away") % zl)
	elif benches and benches.seated() and not dlg_open:
		prompt.text = ("[A]  " if touch_pad else "[E]  ") + "Get up   ·   ← → ↑ ↓ look round"
	elif ride_cam and ride_inside and not dlg_open:
		prompt.text = ("[A]  " if touch_pad else "[E]  ") + ("View from outside" if ride_look else "View from inside") + "   ·   ← → ↑ ↓ look round"
	elif ride_cam and not dlg_open:
		prompt.text = ("[A]  " if touch_pad else "[E]  ") + ("Third person" if ride_look else "First person") + "   ·   ← → ↑ ↓ look round"
	else:
		prompt.text = "" if n.is_empty() else ("[A]  " if touch_pad else "[E]  ") + n.label
	var prims := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)
	stats.text = "%d fps · %s · %dk triangles" % [Engine.get_frames_per_second(), preset, prims / 1000]
	if debug_on:                                       # (the look's switches belong to the debug menu: rule 08 #77a)
		stats.text += "\n%s quality · bounce light %s · light shafts %s" % ["high" if high_quality else "balanced",
			"on" if env_out.sdfgi_enabled else "off", "on" if env_out.volumetric_fog_enabled else "off"]
	# (round 41c, the user: "in the binoculars mode, could you remove the normal text below so I can see the actual
	# options?") not while looking through the telescope either: its own keys are shown there
	help.visible = not dlg_open and not vf_on and not (north and not north.get("scope").is_empty())
	if dlg_panel.visible and dlg_text.visible_characters >= 0:
		type_t += dt * TYPE_RATE
		dlg_text.visible_characters = int(type_t)
		if dlg_text.visible_characters >= dlg_text.get_total_character_count():
			dlg_text.visible_characters = -1
	clock_panel.visible = not dlg_panel.visible           # (the big talk box spans the bottom corners)
	money_panel.visible = not dlg_panel.visible
	boost_panel.visible = boost > 0.0 and boost_id != "" and not dlg_panel.visible and not panels.is_open()
	if boost_panel.visible:
		boost_icon.texture = panels.icon(boost_id)
		boost_name.text = game.item(boost_id).name
		boost_left.text = "+%d%% speed · %ds" % [roundi((BOOST_K - 1.0) * 100.0), ceili(boost)]
	update_toasts(dt)
	update_glare(dt)
	update_map()
	ambience.sea_near(D.get("sea_z", 215.0) - player.global_position.z)
	light_t -= dt
	if clock_light and light_t <= 0.0:
		light_t = 0.5                                  # (the clock moves under a minute in that time)
		light_from_clock()
	elif clock_light and Engine.get_process_frames() % SUN_EVERY == 0 and not "--sunstep" in OS.get_cmdline_user_args():
		aim_sun(fmod(float(game.S.time), 1440.0))     # (the sun's direction every second frame: shadows glide, not step;
		                                             # every other frame halves the shadow map's redraws, the user's wish)
	var mins := int(game.S.time) % 1440
	hud.text = game.objective_text()
	mission_panel.visible = hud.text != ""
	clock_label.text = "%s %02d:%02d" % ["☾" if P.night else "☀", mins / 60, mins % 60]
	money_label.text = game.money(game.S.money)
	layout_ui()
