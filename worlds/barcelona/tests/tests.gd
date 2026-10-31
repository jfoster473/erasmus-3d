# Scripted test runs: Godot --path godot -- --<mode>[=<folder for screenshots>]
# Each drives the real game the way a player would (keys held, things pressed) and prints numbers
# and/or saves screenshots, then quits. See "Test modes" in ../README.md. m is main.gd.
extends Node

const MODES := {
	"--high": "set_quality",
	"--shots=": "run_shots",
	"--pose=": "run_pose",
	"--night=": "run_night",
	"--dog=": "run_dog",
	"--block=": "run_block",
	"--aerial=": "run_aerial",
	"--bike=": "run_bike",
	"--elev=": "run_elev",
	"--flicker=": "run_flicker",
	"--rider=": "run_rider",
	"--corners=": "run_corners",
	"--ride=": "run_ride",
	"--moves": "run_moves",
	"--veer=": "run_veer",
	"--fronts=": "run_fronts",
	"--cast=": "run_cast",
	"--tour=": "run_tour",
	"--walkers=": "run_walkers",
	"--perf": "run_perf",
	"--rooms=": "run_rooms",
	"--talk": "run_talk",
	"--missions": "run_missions",
	"--map=": "run_map",
	"--mapscreen=": "run_mapscreen",
	"--look=": "run_look",
	"--views=": "run_views",
	"--flat=": "run_flat",
	"--north=": "run_north",
	"--facadeflicker": "run_facadeflicker",
	"--partyout=": "run_partyout",
	"--gfxperf": "run_gfxperf",
	"--exitview=": "run_exitview",
	"--day=": "run_day",
	"--accs=": "run_accs",
	"--front=": "run_frontend",
	"--wear=": "run_wear",
	"--wild=": "run_wild",
	"--bag=": "run_bag",
	"--church=": "run_church",
	"--sagratcor=": "run_sagratcor",
	"--roompic=": "run_roompic",
	"--closeup=": "run_closeup",
	"--hilltour=": "run_hilltour",
	"--storybits": "run_storybits",
	"--pathgrid": "run_pathgrid",
	"--flickermeter": "run_flickermeter",
	"--stairs": "run_stairs",
	"--stuck=": "run_stuck",
	"--seams": "run_seams",
	"--seamprobe": "run_seamprobe",
	"--playthrough=": "run_playthrough",
	"--visit=": "run_visit",
	"--nobus=": "run_nobus",
	"--solidcheck=": "run_solidcheck",
	"--solidwalk=": "run_solidwalk",
	"--roofwalk=": "run_roofwalk",
	"--walkline=": "run_walkline",
	"--peoplewalls": "run_peoplewalls",
	"--npcpose=": "run_npcpose",
	"--kitetalk=": "run_kitetalk",
	"--wheelride=": "run_wheelride",
	"--wheelseat=": "run_wheelseat",
	"--wheelpeak=": "run_wheelpeak",
	"--wallescape": "run_wallescape",
	"--traps=": "run_traps",
	"--trapsim=": "run_trapsim",
	"--roomwalk=": "run_roomwalk",
	"--heights=": "run_heights",
	"--bikeline=": "run_bikeline",
	"--funiride=": "run_funiride",
	"--keyseq=": "run_keyseq",
	"--gridprobe=": "run_gridprobe",
	"--placecheck=": "run_placecheck",
	"--slopemap=": "run_slopemap",
	"--parktour=": "run_parktour",
	"--spotshots=": "run_spotshots",
	"--pocket": "run_pocket",
	"--caps=": "run_caps",
	"--hatwalk=": "run_hatwalk",
	"--hatlive=": "run_hatlive",
	"--bump": "run_bump",
	"--talkstay": "run_talkstay",
	"--ui=": "run_ui",
	"--glare=": "run_glare",
	"--glaremock=": "run_glaremock",
	"--spotsave": "run_spotsave",
	"--unstick=": "run_unstick",
	"--stairscam=": "run_stairscam",
	"--gateshots=": "run_gateshots",
	"--besides=": "run_besides",
	"--touchprobe=": "run_touchprobe",
	"--mapshot=": "run_mapshot",
	"--clearance": "run_clearance",
	"--camprobe": "run_camprobe",
	"--stationcam=": "run_stationcam",
	"--fpkeys": "run_fpkeys",
	"--funijolt": "run_funijolt",
	"--funiside": "run_funiside",
	"--funiground": "run_funiground",
	"--phototest": "run_phototest",
	"--occlprobe=": "run_occlprobe",
	"--groundshot=": "run_groundshot",
	"--looktest=": "run_looktest",
	"--vfride=": "run_vfride",
	"--bielball=": "run_bielball",
	"--vfchain=": "run_vfchain",
	"--lookstate": "run_lookstate",
	"--dogsettle=": "run_dogsettle",
	"--doghome": "run_doghome",
	"--vftest=": "run_vftest",
	"--vfplaces=": "run_vfplaces",
	"--cryptprobe": "run_cryptprobe",
	"--funiwatch=": "run_funiwatch",
	"--titleshots=": "run_titleshots",
	"--titlesound": "run_titlesound",
	"--framerec=": "run_framerec",
	"--perfopts": "run_perfopts",
	"--lookopts=": "run_lookopts",
	"--fpstour": "run_fpstour",
	"--rideperf": "run_rideperf",
	"--wheelfps=": "run_wheelfps",
	"--ridelook=": "run_ridelook",
	"--titleload=": "run_titleload",
	"--bagitem=": "run_bagitem",
	"--idleline=": "run_idleline",
	"--funitilt": "run_funitilt",
	"--funicar=": "run_funicar",
	"--funitoggle=": "run_funitoggle",
	"--armshots=": "run_armshots",
	"--funiquick=": "run_funiquick",
	"--camprobe=fair": "run_camprobe",
	"--debugmenu": "run_debugmenu",
	"--forestbike": "run_forestbike",
	"--bikecam=": "run_bikecam",
	"--porch=": "run_porch",
	"--rope": "run_rope",
	"--touchtest=": "run_touchtest",
	"--touchtoggle": "run_touchtoggle",
	"--lean=": "run_lean",
	"--hairmove=": "run_hairmove",
	"--doorcam": "run_doorcam",
	"--doorshots=": "run_doorshots",
	"--bikesize=": "run_bikesize",
	"--churchdoor=": "run_churchdoor",
	"--dogride=": "run_dogride",
	"--thief=": "run_thief",
	"--shadowcrawl=": "run_shadowcrawl",
	"--journal=": "run_journal",
	"--shove=": "run_shove",
	"--models": "run_models",
	"--exam=": "run_exam",
	"--swaycost": "run_swaycost",
	"--hillescape": "run_hillescape",
	"--flowers=": "run_flowers",
	"--benchview=": "run_benchview",
	"--cove": "run_cove",
	"--telescope=": "run_telescope",
	"--hillbike": "run_hillbike",
	"--foliagecost": "run_foliagecost",
	"--churchsteps=": "run_churchsteps",
	"--leafshadow=": "run_leafshadow",
	"--ballwalk=": "run_ballwalk",
	"--quick": "run_quick",
	"--probejoan": "run_probejoan",
	"--probebrush": "run_probebrush",
	"--probemarta": "run_probemarta",
	"--full=": "run_full",
	"--rosalily=": "run_rosalily",
	"--armprobe": "run_armprobe",
	"--turnprobe": "run_turnprobe",
	"--roadprobe": "run_roadprobe",
	"--benchsit=": "run_benchsit",
	"--wallscan=": "run_wallscan",
}

# (round 26, the user: the tests took too long; "a speed run with one launch and a quick set") a suite runs several
# tests in the one launch of the game, each printing its lines as before; a test ends with end_test(), which quits
# the game only when it runs alone. The game is started fresh (the test save deleted) and the tests that need a new
# game come first.
var suite := false
const QUICK := [["--missions", ""], ["--stairs", ""], ["--north=", "quick_north"], ["--sagratcor=", "quick_sagratcor"],
	["--debugmenu", ""], ["--seams", ""]]
const FULL := [["--missions", ""], ["--stairs", ""], ["--north=", "north"], ["--flowers=", "flowers"], ["--debugmenu", ""],
	["--sagratcor=", "sagratcor"], ["--churchsteps=", "churchsteps"], ["--hillescape", ""], ["--rooms=", "rooms"],
	["--seams", ""], ["--perf", ""]]


func end_test() -> void:
	if not suite:
		get_tree().quit()


func run_suite(tests: Array, dir: String) -> void:
	suite = true
	var t0 := Time.get_ticks_msec()
	for t in tests:
		var key: String = t[0]
		var t1 := Time.get_ticks_msec()
		printerr("=== %s" % key.trim_prefix("--").trim_suffix("="))
		if m.where == "in":                             # (the last test may have ended indoors: every test starts outside)
			await go_out()
		if key == "--hillescape":
			Engine.time_scale = 2.0                    # (walking up to the railing 246 times: twice as fast, same answers)
		if key.ends_with("="):
			await call(MODES[key], dir.path_join(t[1]))
		else:
			await call(MODES[key])
		Engine.time_scale = 1.0
		m.set_clock(660.0)
		for c in m.get_children():
			if c is CanvasLayer:
				c.visible = true
		printerr("=== %s took %d s" % [key.trim_prefix("--").trim_suffix("="), (Time.get_ticks_msec() - t1) / 1000])
	printerr("=== SUITE done in %d s" % ((Time.get_ticks_msec() - t0) / 1000))
	get_tree().quit()


func run_quick() -> void:
	await run_suite(QUICK, OS.get_environment("HOME").path_join("Library/Application Support/Godot/app_userdata/Flor de Lliri - Godot test/quick"))


func run_full(dir: String) -> void:
	await run_suite(FULL, dir)

const Main := preload("res://engine/main.gd")

var m: Main


var drawn_last := -1


func _process(_dt: float) -> void:
	# (with the screen asleep or locked, or the window hidden, macOS draws nothing and every picture a test takes is
	# the same stale one: draw the frame ourselves when the engine didn't)
	var n := Engine.get_frames_drawn()
	if n == drawn_last:
		RenderingServer.force_draw(false)
	drawn_last = Engine.get_frames_drawn()


var args_all: Array = []


func start(main: Main, args: Array) -> void:
	m = main
	args_all = args
	# (round 26, the user: "stop the sound in the tests") a test run is silent
	AudioServer.set_bus_mute(AudioServer.get_bus_index("Master"), true)
	# (a test window that opens behind other windows is never drawn on macOS: every picture would be the same one)
	DisplayServer.window_move_to_foreground()
	for a in args:
		if a.begins_with("--trailglb="):
			swap_trails(a.trim_prefix("--trailglb="))
		if a.begins_with("--blockglb="):
			swap_block(a.trim_prefix("--blockglb="))
		if a == "--lanternmock":
			lantern_mock()
		if a == "--noleafshadow":              # (round 25: the woods' leaves casting no shadows)
			for n in m.outdoor.find_children("Leaves_*", "GeometryInstance3D", true, false):
				(n as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if a == "--nofar":                     # (round 25: everything drawn at any distance, as a telescope would need)
			for n in m.outdoor.find_children("*", "GeometryInstance3D", true, false):
				var gi := n as GeometryInstance3D
				if gi.visibility_range_end > 0.0 or gi.visibility_range_begin > 0.0:
					gi.visible = gi.visibility_range_begin == 0.0          # (the far stand-ins go; the near ones stay)
					gi.visibility_range_end = 0.0
		if a.begins_with("--hide="):          # (round 26) built objects by exact name (comma-separated), e.g. SagratCor
			for nm in a.trim_prefix("--hide=").split(","):
				for n in m.outdoor.find_children(nm, "", true, false):
					(n as Node3D).visible = false
		if a.begins_with("--addglb="):
			add_glb(a.trim_prefix("--addglb="))
	for a in args:
		for key in MODES:
			if key.ends_with("="):
				if a.begins_with(key):
					call(MODES[key], a.substr(key.length()))
			elif a == key:
				call(MODES[key])


func swap_trails(file: String) -> void:
	# (round 23) the wood's path ribbons from another file (shared/trail_options.py), in place of the built ones
	for n in m.outdoor.find_children("Trails*", "", true, false):
		n.visible = false
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	doc.append_from_file(file, st)
	var sc := doc.generate_scene(st) as Node3D
	m.outdoor.add_child(sc)
	for mi in sc.find_children("*", "MeshInstance3D", true, false):
		(mi as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


func swap_block(spec: String) -> void:
	# (round 25) one block from another file (builder/window_options.py), in place of the built one: <file>:<tag>
	var file := spec.rsplit(":", true, 1)[0]
	var tag := spec.rsplit(":", true, 1)[1]
	var box := AABB()
	for n in m.outdoor.find_children("*", "MeshInstance3D", true, false):
		var nm := String(n.name)
		if nm == "Block_" + tag or nm == "Detail_" + tag or nm == "WinPic_" + tag:
			box = (n as MeshInstance3D).global_transform * (n as MeshInstance3D).get_aabb() if box.size == Vector3.ZERO else box.merge((n as MeshInstance3D).global_transform * (n as MeshInstance3D).get_aabb())
			n.visible = false
	for n in m.outdoor.find_children("Win*", "MeshInstance3D", true, false):
		if box.has_point((n as MeshInstance3D).global_position):
			n.visible = false
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	doc.append_from_file(file, st)
	var sc := doc.generate_scene(st) as Node3D
	m.outdoor.add_child(sc)
	m.prepare_city(sc)
	print("BLOCKGLB %s in place of %s (%s)" % [file.get_file(), tag, box])


func add_glb(spec: String) -> void:
	# (round 25) a glb added to the city as it stands (builder/trunk_options.py…); <file>[:<name part to hide>]
	var parts := spec.split(":")
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	doc.append_from_file(parts[0], st)
	var sc := doc.generate_scene(st) as Node3D
	m.outdoor.add_child(sc)
	m.prepare_city(sc)
	if parts.size() > 1:
		for n in sc.find_children("*" + parts[1] + "*", "", true, false):
			n.visible = false


func lantern_mock() -> void:
	# (round 25) the hill rail's lanterns as the next build would make them (a bigger lantern on every 18th post, with a
	# soft light under it), for pictures before building
	var rails: Array = m.D.get("north", {}).get("rails", [])
	var glass := StandardMaterial3D.new()
	glass.albedo_color = Color(0.96, 0.88, 0.72)
	glass.emission_enabled = true
	glass.emission = Color(1.0, 0.78, 0.5)
	glass.emission_energy_multiplier = 2.5
	var iron := StandardMaterial3D.new()
	iron.albedo_color = Color(0.12, 0.11, 0.1)
	for i in range(0, rails.size(), 18):
		var r: Array = rails[i]
		var h: float = m.terrain_at(r[0], r[1])
		var c := Vector3(r[0], h + 1.05, r[1])
		var bm := BoxMesh.new()
		bm.size = Vector3(0.2, 0.28, 0.2)
		var g := MeshInstance3D.new()
		g.mesh = bm
		g.material_override = glass
		g.position = c
		m.outdoor.add_child(g)
		for dy in [0.16, -0.16]:
			var cap := MeshInstance3D.new()
			var cb := BoxMesh.new()
			cb.size = Vector3(0.25, 0.035, 0.25)
			cap.mesh = cb
			cap.material_override = iron
			cap.position = c + Vector3(0, dy, 0)
			m.outdoor.add_child(cap)
		var ol := OmniLight3D.new()
		ol.position = c - Vector3(0, 0.1, 0)
		ol.light_color = Color(1.0, 0.78, 0.5)
		ol.omni_range = 7.0
		ol.omni_attenuation = 1.4
		ol.light_energy = 1.3
		m.outdoor.add_child(ol)
	print("LANTERNMOCK %d" % ceili(rails.size() / 18.0))


func place(x: float, z: float, heading: float, yaw := INF) -> void:
	m.player.global_position = Vector3(x, 0, z)
	m.player.velocity = Vector3.ZERO
	m.speed = 0.0
	m.turn_vel = 0.0
	m.cam_vel = 0.0
	m.model.rotation.y = heading
	m.move_dir = Vector2(sin(heading), cos(heading))
	m.cam_yaw_node.rotation.y = heading + PI if yaw == INF else yaw
	m.cam_root.global_position = m.player.global_position + Vector3(0, m.CAM_PIVOT_H, 0)


func hold(k: Key, secs: float) -> void:
	m.vkeys[k] = true
	await get_tree().create_timer(secs).timeout
	m.vkeys.erase(k)
	await get_tree().create_timer(0.15).timeout


func shot(dir: String, sname: String) -> void:
	await get_tree().create_timer(2.0).timeout
	await get_tree().process_frame
	await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join(sname + ".png"))
	print("SHOT %s  fps=%d" % [sname, Engine.get_frames_per_second()])


func run_shots(dir: String) -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	await shot(dir, "01_start")
	var d = m.D.door
	place(11.0, 36.3, 2.4)
	await shot(dir, "02_street_behind")
	place(d.pos[0], 36.3, -PI / 2.0)
	await shot(dir, "03_towards_sun")
	# walk east, then the camera should swing round behind her
	place(d.pos[0], d.pos[1] + 7.0, PI)
	await hold(KEY_D, 2.5)
	print("TURN  cam_yaw=%.2f  heading=%.2f" % [m.cam_yaw_node.rotation.y, m.model.rotation.y])
	await shot(dir, "04_after_turn")
	m.apply_preset("night")
	await shot(dir, "05_night")
	m.apply_preset("golden")
	place(d.pos[0], d.pos[1] + 3.0, PI)
	await hold(KEY_W, 1.8)
	await get_tree().create_timer(0.8).timeout
	print("WALK into door -> ", m.where)
	await shot(dir, "06_interior")
	# Rosa, then out again
	var rosa: Dictionary = m.npcs.indoor.get("rosa", {})
	if not rosa.is_empty():
		m.player.global_position = rosa.holder.global_position + Vector3(0, 0, 1.2)
		await get_tree().create_timer(0.3).timeout
		m.interact()
		await get_tree().create_timer(0.1).timeout
		print("ROSA dialog open=", m.dlg_open, " who=", m.dlg_who.text)
		await shot(dir, "07_rosa")
		while m.dlg_open:
			m.dialog_next()
			await get_tree().create_timer(0.05).timeout
	var R: Dictionary = m.D.interiors[m.room]
	m.player.global_position = m.room_base(m.room) + Vector3(R.exit[0] + 0.5, 0, R.h - 1.0)
	await get_tree().create_timer(0.2).timeout
	await hold(KEY_S, 1.2)
	await get_tree().create_timer(0.8).timeout
	print("WALK out -> ", m.where)
	await shot(dir, "08_back_outside")
	m.show_skin(m.skin_idx + 1)
	await shot(dir, "09_other_sandra")
	end_test()


func run_night(dir: String) -> void:
	# the street after dark from several spots, including the darkest stretches between lamps
	DirAccess.make_dir_recursive_absolute(dir)
	m.apply_preset("night")
	await get_tree().create_timer(3.0).timeout
	var d = m.D.door
	place(d.pos[0], d.pos[1] + 2.5, PI / 2.0)
	await shot(dir, "n1_door")
	place(4.5 * 3.3, 11.0 * 3.3, -PI / 2.0)
	await shot(dir, "n2_flor_west")
	place(11.0 * 3.3, 4.5 * 3.3, PI)
	await shot(dir, "n3_girona")
	place(-2.0 * 3.3, 4.5 * 3.3, 0.0)
	await shot(dir, "n4_rambla")
	place(4.5 * 3.3, -2.0 * 3.3, PI / 2.0)
	await shot(dir, "n5_mallorca")
	place(d.pos[0], d.pos[1] + 2.5, 0.0, PI)
	m.arm.spring_length = 7.0
	m.cam_pitch_node.rotation.x = 0.05
	await shot(dir, "n6_sky")
	end_test()


func run_block(dir: String) -> void:
	# a walk round Sandra's block: each side, the corners, the passage and the garden; then at night
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var T := 3.3
	var views := [
		["b1_girona_face", Vector3(36.5, 0, 14.0), -PI / 2.0, PI / 2.0],
		["b2_ne_corner", Vector3(35.0, 0, -5.0), -PI * 0.25, PI * 0.75],
		["b3_mallorca_face", Vector3(12.0, 0, -8.5), 0.0, PI],
		["b4_passage", Vector3(33.5, 0, 18.2), -PI / 2.0, PI / 2.0],
		["b5_garden", Vector3(20.5, 0, 18.2), -PI / 2.0, PI / 2.0],
		["b6_garden2", Vector3(10.0, 0, 10.0), PI * 0.25, -PI * 0.75],
		["b7_se_corner", Vector3(35.0, 0, 35.0), -PI * 0.75, PI * 0.25],
		["b8_rambla_face", Vector3(-8.5, 0, 16.0), PI / 2.0, -PI / 2.0],
		["b9_sw_corner", Vector3(-5.0, 0, 35.0), PI * 0.75, -PI * 0.25],
		["b10_nw_corner", Vector3(-5.0, 0, -5.0), PI * 0.25, -PI * 0.75],
		["b11_home_left", Vector3(9.5, 0, 34.0), PI * 0.8, -PI * 0.2],
		["b12_home_right", Vector3(20.5, 0, 34.0), -PI * 0.8, PI * 0.2],
		["b13_pharmacy", Vector3(18.5, 0, 32.4), PI * 0.62, PI * 1.62],
		["b14_joint_west", Vector3(10.5, 0, 30.9), PI * 1.15, PI * 0.15],
		["b15_joint_east", Vector3(19.2, 0, 30.9), PI * 0.85, -PI * 0.15],
		["b16_alley_in", Vector3(31.8, 0, 18.15), -PI / 2.0, PI / 2.0],
	]
	for v in views:
		place(v[1].x, v[1].z, v[2], v[3])
		m.cam_pitch_node.rotation.x = -0.05
		m.arm.spring_length = 5.5
		await shot(dir, v[0])
	m.apply_preset("night")
	for v in [views[1], views[3], views[4], views[6]]:
		place(v[1].x, v[1].z, v[2], v[3])
		m.cam_pitch_node.rotation.x = -0.05
		m.arm.spring_length = 5.5
		await shot(dir, v[0] + "_night")
	end_test()


func run_bike(dir: String) -> void:
	# walk up to a bike from the side and press E, as a player would; ride on with W, steer, get off with E
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	for bi in [0, 2]:
		var bk: Node3D = m.street.bikes[bi]
		var side := bk.global_transform.basis.x
		place(bk.position.x + side.x * 0.8, bk.position.z + side.z * 0.8, atan2(-side.x, -side.z))
		await get_tree().create_timer(0.6).timeout
		m.interact()
		await get_tree().create_timer(0.3).timeout
		await shot(dir, "k%d_1_on" % bi)
		m.vkeys[KEY_W] = true
		for i in 8:
			await get_tree().create_timer(0.25).timeout
			if i == 4:
				m.vkeys[KEY_D] = true
			report_bike("ride %d" % i)
		await shot(dir, "k%d_2_riding" % bi)
		m.vkeys.clear()
		await get_tree().create_timer(1.6).timeout
		m.interact()
		await get_tree().physics_frame
		report_bike("off")
		m.vkeys[KEY_W] = true
		for i in 3:
			await get_tree().create_timer(0.3).timeout
			report_bike("walk %d" % i)
		await shot(dir, "k%d_3_walking" % bi)
		m.vkeys.clear()
	end_test()


func report_bike(what: String) -> void:
	var v := m.player.get_real_velocity()
	var f := Vector3(sin(m.model.rotation.y), 0, cos(m.model.rotation.y))
	var ang := rad_to_deg(f.signed_angle_to(Vector3(v.x, 0, v.z), Vector3.UP)) if Vector2(v.x, v.z).length() > 0.2 else 0.0
	print("%s  speed=%.1f  facing-vs-moving=%.0f deg  riding=%s  at (%.1f, %.1f) wall=%s" % [what, Vector2(v.x, v.z).length(), ang, m.street.riding != null, m.player.global_position.x, m.player.global_position.z, m.player.is_on_wall()])


func run_flicker(dir: String) -> void:
	# each view twice, the second with the camera moved by 2 mm: surfaces fighting for the same
	# depth show up as speckle in the difference (see the flicker check in the README)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	place(-20.0, -20.0, 0.0)
	var cam := Camera3D.new()
	add_child(cam)
	cam.far = 300.0
	cam.current = true
	var oct := [Vector2(2, 0), Vector2(7, 0), Vector2(9, 2), Vector2(9, 7), Vector2(7, 9), Vector2(2, 9), Vector2(0, 7), Vector2(0, 2)]
	var k := 0
	for i in 8:
		var p0: Vector2 = oct[i] * 3.3
		var p1: Vector2 = oct[(i + 1) % 8] * 3.3
		var d := (p1 - p0).normalized()
		var out := Vector2(d.y, -d.x)
		var mid := (p0 + p1) / 2.0
		for v in [[out * 9.0, 1.6, 4.0], [out * 6.0 - d * 9.0, 1.6, 3.0], [out * 18.0 + d * 6.0, 1.6, 6.0]]:
			var from := Vector3(mid.x + v[0].x, v[1], mid.y + v[0].y)
			for rep in 2:
				cam.global_position = from + (Vector3(0.002, 0.0015, 0.002) if rep == 1 else Vector3.ZERO)
				cam.look_at(Vector3(mid.x, v[2], mid.y), Vector3.UP)
				await get_tree().create_timer(0.4 if rep == 1 else 1.2).timeout
				await get_tree().process_frame
				get_viewport().get_texture().get_image().save_png(dir.path_join("f%02d_%d.png" % [k, rep]))
			k += 1
	end_test()


func run_elev(dir: String) -> void:
	# straight-on (orthographic) elevations of each side of Sandra's block, with the street trees
	# and lamps clipped away, to check that the houses line up
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	place(-20.0, -20.0, 0.0)
	var cam := Camera3D.new()
	add_child(cam)
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 21.0
	cam.far = 80.0
	cam.current = true
	var oct := [Vector2(2, 0), Vector2(7, 0), Vector2(9, 2), Vector2(9, 7), Vector2(7, 9), Vector2(2, 9), Vector2(0, 7), Vector2(0, 2)]
	for i in 8:
		var p0: Vector2 = oct[i] * 3.3
		var p1: Vector2 = oct[(i + 1) % 8] * 3.3
		var d := (p1 - p0).normalized()
		var out := Vector2(d.y, -d.x)
		var mid := (p0 + p1) / 2.0
		var at := Vector3(mid.x, 9.0, mid.y)
		cam.near = 30.0 - 2.4
		cam.global_position = at + Vector3(out.x, 0, out.y) * 30.0
		cam.look_at(at, Vector3.UP)
		await shot(dir, "e%d" % i)
	end_test()


func run_aerial(dir: String) -> void:
	# Sandra's block seen from the air, to check that the houses join up
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	place(16.0, 34.5, 0.0, 0.0)
	var cam := Camera3D.new()
	add_child(cam)
	cam.far = 600.0
	cam.current = true
	var c := Vector3(14.85, 5.0, 14.85)
	var views := [
		["a1_top", Vector3(14.85, 60.0, 15.3)],
		["a2_se", Vector3(40.0, 22.0, 40.0)],
		["a3_nw", Vector3(-10.0, 22.0, -10.0)],
		["a4_ne", Vector3(40.0, 22.0, -10.0)],
		["a5_sw", Vector3(-10.0, 22.0, 40.0)],
		["a6_s", Vector3(14.85, 16.0, 46.0)],
		["a7_n", Vector3(14.85, 16.0, -16.0)],
		["a8_e", Vector3(46.0, 16.0, 14.85)],
		["a9_w", Vector3(-16.0, 16.0, 14.85)],
	]
	views.append_array([
		["a10_across", Vector3(14.85, 12.0, 30.0), Vector3(14.85, 6.0, 52.0)],
		["a11_east_block", Vector3(38.0, 14.0, 38.0), Vector3(57.75, 6.0, 26.0)],
		["a12_west_block", Vector3(-8.0, 14.0, 38.0), Vector3(-27.9, 6.0, 26.0)],
		["a13_pharmacy", Vector3(22.0, 2.4, 32.6), Vector3(26.5, 2.8, 27.6)],
		["a14_home_front", Vector3(6.0, 3.0, 33.5), Vector3(16.0, 3.0, 29.0)],
	])
	for v in views:
		cam.global_position = v[1]
		cam.look_at(v[2] if v.size() > 2 else c, Vector3.FORWARD if v[0] == "a1_top" else Vector3.UP)
		await shot(dir, v[0])
	end_test()


func run_dog(dir: String) -> void:
	# close-ups of Trufa: standing, trotting beside Sandra, sitting
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var tr: Node3D = m.street.trufa
	var p0 := Vector3(16.0, 0, 34.5)
	tr.position = p0 + Vector3(0, m.D.kerb * 0.0, 0)
	tr.lost_pos = tr.position
	tr.heading = PI / 2.0
	tr.state = tr.STAY
	place(p0.x + 1.2, p0.z + 0.3, -PI / 2.0, 0.0)
	m.cam_pitch_node.rotation.x = -0.3
	m.arm.spring_length = 2.4
	await get_tree().create_timer(0.5).timeout
	await shot(dir, "d1_sitting")

	tr.state = tr.FOLLOW
	tr.trail.clear()
	m.vkeys[KEY_D] = true
	await get_tree().create_timer(1.6).timeout
	m.last_manual_cam = m.t
	m.cam_yaw_node.rotation.y = 0.0
	await shot(dir, "d2_trotting")
	m.vkeys.clear()
	await get_tree().create_timer(1.2).timeout
	await shot(dir, "d3_standing")
	end_test()


func run_pose(dir: String) -> void:
	# side views of Sandra standing and running, to check her posture
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var d = m.D.door
	place(d.pos[0] - 4.0, d.pos[1] + 6.5, PI / 2.0, 0.0)
	m.arm.spring_length = 3.2
	await shot(dir, "pose_idle")
	m.vkeys[KEY_D] = true
	await get_tree().create_timer(0.9).timeout
	m.last_manual_cam = m.t
	await shot(dir, "pose_run")
	m.vkeys.erase(KEY_D)
	end_test()


func run_ride(dir: String) -> void:
	# riding the bike: pedal, lean into turns, a held turn, braking, steering from a standstill.
	# Prints speed, how fast she turns and how big a circle that makes, and how far the bike's facing
	# and its movement disagree (it should never slide)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var c := Vector2(-2.0 * 3.3, 11.0 * 3.3)
	var bk: Node3D = m.street.bikes[0]
	bk.position = Vector3(c.x, 0, c.y + 4.0)
	bk.rotation.y = -PI / 4.0 if "--wall" in OS.get_cmdline_user_args() else 0.0   # nose north, or at the corner
	place(c.x + 0.8, c.y + 4.0, -PI / 2.0, bk.rotation.y if "--wall" in OS.get_cmdline_user_args() else 0.0)
	await get_tree().create_timer(0.4).timeout
	m.interact()
	await get_tree().create_timer(0.4).timeout
	var free := "--free" in OS.get_cmdline_user_args()
	if free:
		m.player.collision_mask = 0
	var plan := [[[KEY_W], 1.0, ""], [[KEY_W, KEY_D], 1.2, "r1_turning"], [[KEY_W], 0.6, ""], [[KEY_A], 2.0, "r2_gentle_left"],
		[[KEY_S], 1.2, ""], [[KEY_S], 0.6, "r3_braked"], [[KEY_D], 1.6, "r4_from_standstill"], [[], 1.0, ""]]
	if free:
		plan = [[[KEY_W], 2.0, ""], [[KEY_W, KEY_D], 3.0, ""], [[KEY_D], 4.0, ""], [[KEY_S], 1.5, ""], [[KEY_A], 3.0, ""]]
	if "--spin" in OS.get_cmdline_user_args():
		# stopped: turn her round on the spot to face the camera (it stays put), then ride off (it follows)
		plan = [[[KEY_D], 1.6, "r8_facing_camera"], [[], 0.6, ""], [[KEY_W], 2.4, "r9_rode_off"], [[KEY_W, KEY_A], 1.5, ""], [[], 2.5, "r10_coasting"]]
	if "--wall" in OS.get_cmdline_user_args():
		# straight into the building on the corner, then back away from it and ride off
		plan = [[[KEY_W], 2.4, "r5_at_wall"], [[KEY_W, KEY_D], 0.6, ""], [[KEY_S], 2.0, "r6_backing"], [[KEY_W, KEY_D], 1.5, "r7_away"]]
	var last_h := atan2(m.move_dir.x, m.move_dir.y)
	for st in plan:
		m.vkeys.clear()
		for k in st[0]:
			m.vkeys[k] = true
		var n := maxi(1, int(st[1] / 0.3))
		for i in n:
			await get_tree().create_timer(st[1] / n).timeout
			var h := atan2(m.move_dir.x, m.move_dir.y)
			var w: float = wrapf(h - last_h, -PI, PI) / (st[1] / n)
			last_h = h
			var v := m.player.get_real_velocity()
			var f := Vector3(sin(m.model.rotation.y), 0, cos(m.model.rotation.y))
			var slide := rad_to_deg(f.signed_angle_to(Vector3(v.x, 0, v.z), Vector3.UP)) if Vector2(v.x, v.z).length() > 0.3 else 0.0
			print("  keys=%-6s speed=%4.1f  turning=%5.2f rad/s  circle=%5s m across  lean=%5.1f deg  slide=%3.0f deg  camera-behind=%4.0f deg" % [
				"".join(st[0].map(func(k): return OS.get_keycode_string(k))), m.speed, w,
				("%.1f" % (2.0 * m.speed / absf(w))) if absf(w) > 0.05 else "-", rad_to_deg(m.lean), slide,
				rad_to_deg(wrapf(m.cam_yaw_node.rotation.y - (h + PI), -PI, PI))])
		if st[2] != "":
			get_viewport().get_texture().get_image().save_png(dir.path_join(st[2] + ".png"))
	end_test()


func run_forestbike() -> void:
	# round 20: the bike keeps to the paths and the green; the litter under the trees and the sand stop it
	await get_tree().create_timer(3.0).timeout
	var bk: Node3D = m.street.bikes[0]
	var cases := [["off the long path east, into the wood", Vector2(95.6, 53.0), PI / 2.0],
		["down the long path onto the beach", Vector2(95.6, 82.0), 0.0],
		["north across the fringe grass", Vector2(86.0, 40.0), PI],
		["round a crossing's corner", Vector2(93.5, 42.6), PI / 2.0],
		["south out of Trufa's glade", Vector2(98.5, 50.3), 0.0],
		["west out of Trufa's glade", Vector2(98.3, 50.8), -PI / 2.0]]
	for c in cases:
		var p := Vector3((c[1].x - 55.0) * 3.3, 0, (c[1].y - 45.0) * 3.3)
		if m.street.riding:
			m.street.dismount()
			await get_tree().create_timer(0.3).timeout
		bk.position = p + Vector3(0.8, 0, 0)
		bk.rotation.y = 0.0
		place(p.x, p.z, -PI / 2.0)
		await get_tree().create_timer(0.3).timeout
		m.street.mount(bk)
		await get_tree().create_timer(0.4).timeout
		place(m.player.global_position.x, m.player.global_position.z, c[2])
		var keys := [KEY_W] if c[0].find("corner") < 0 else [KEY_W, KEY_D]
		var start := m.player.global_position
		m.vkeys.clear()
		for k in keys:
			m.vkeys[k] = true
		for i in (8 if c[0].find("corner") < 0 else 5):
			await get_tree().create_timer(0.5).timeout
			var q := m.player.global_position
			var hit := ""
			for j in m.player.get_slide_collision_count():
				var col := m.player.get_slide_collision(j).get_collider()
				hit += " " + (String(col.name) + "/layer%d" % col.collision_layer if col else "?")
			print("   t=%.1f tile (%.2f, %.2f) speed %.1f  no-bike here=%s ahead1m=%s  hits:%s" % [(i + 1) * 0.5, q.x / 3.3 + 55.0, q.z / 3.3 + 45.0,
				m.speed, m.no_bike_at(q), m.no_bike_at(q + Vector3(m.move_dir.x, 0, m.move_dir.y)), hit])
		m.vkeys.clear()
		var e := m.player.global_position
		print("FORESTBIKE %-40s on bike=%s  rode %5.1f m  speed now %4.1f  stopped by no-bike ground ahead=%s  at tile (%.1f, %.1f)" % [
			c[0], m.street.riding != null, Vector2(e.x - start.x, e.z - start.z).length(), m.speed,
			m.no_bike_at(e + Vector3(m.move_dir.x, 0, m.move_dir.y) * 0.6), e.x / 3.3 + 55.0, e.z / 3.3 + 45.0])
	end_test()


func run_corners(dir: String) -> void:
	# getting the bike out of awkward spots, as a player would: creep round, back up, try again.
	# Also: the turn from a standstill, full speed on the road, the slower pavement, and the lean.
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var bk: Node3D = m.street.bikes[0]
	var spots := [
		# name, bike position, nose yaw (bike rotation), keys
		["open: right from a standstill (turns on the spot)", Vector2(-6.6, 36.3), 0.0, [[[KEY_D], 1.6]]],
		["open: full speed, then right (shot from behind)", Vector2(-6.6, 60.0), 0.0, [[[KEY_W], 2.0], [[KEY_W, KEY_D], 0.9, "c_lean_right"], [[KEY_W, KEY_A], 1.6, "c_lean_left"]]],
		["pavement: full pedal", Vector2(10.0, 31.4), PI / 2.0, [[[KEY_W], 2.5]]],
		["nose against the building", Vector2(10.0, 30.6), 0.0, [[[KEY_D], 1.55], [[KEY_W], 1.2, "c_wall_out"]]],
		["wedged between the building and Montse's bench", Vector2(21.9, 30.45), -PI / 2.0, [[[KEY_D], 0.8], [[KEY_W], 1.2, "c_bench_out"]]],
		["turning round in the alley", Vector2(24.5, 18.15), PI / 2.0, [[[KEY_A], 1.55], [[KEY_W], 1.2, "c_alley_out"]]],
	]
	for sp in spots:
		if m.street.riding:
			m.street.dismount()
		m.vkeys.clear()
		await get_tree().create_timer(0.3).timeout
		bk.position = Vector3(sp[1].x, m.ground_at(Vector3(sp[1].x, 0, sp[1].y)), sp[1].y)
		bk.rotation.y = sp[2]
		var side: Vector3 = bk.global_transform.basis.x
		place(sp[1].x + side.x * 0.8, sp[1].y + side.z * 0.8, sp[2] + PI, sp[2])
		await get_tree().create_timer(0.3).timeout
		m.interact()
		await get_tree().create_timer(0.3).timeout
		var p0 := m.player.global_position
		var h0 := atan2(m.move_dir.x, m.move_dir.y)
		var path := 0.0
		var prev := p0
		print("---- ", sp[0], "  riding=", m.street.riding != null)
		for st in sp[3]:
			m.vkeys.clear()
			for k in st[0]:
				m.vkeys[k] = true
			var n := maxi(1, int(st[1] / 0.5))
			for i in n:
				await get_tree().create_timer(st[1] / n).timeout
				path += prev.distance_to(m.player.global_position)
				prev = m.player.global_position
				print("  keys=%-3s speed=%4.1f  at (%5.1f,%5.1f)  turned=%4.0f deg  lean=%5.1f deg  wall=%s" % ["".join(st[0].map(func(k): return OS.get_keycode_string(k))),
					m.speed, m.player.global_position.x, m.player.global_position.z, rad_to_deg(wrapf(atan2(m.move_dir.x, m.move_dir.y) - h0, -PI, PI)), rad_to_deg(m.lean), m.player.is_on_wall()])
			if st.size() > 2:
				get_viewport().get_texture().get_image().save_png(dir.path_join(st[2] + ".png"))
		print("  => moved %.1f m from the start, %.1f m ridden" % [p0.distance_to(m.player.global_position), path])
	end_test()


func run_rider(dir: String) -> void:
	# Sandra on the bike from the side and the front: stopped, riding slowly and at full speed.
	# Prints where her joints are against the saddle, pedals and handlebars (in the bike's own frame:
	# forward is +z, as for her)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	# (round 23: her own bike, as the player rides it, B)
	m.game.S.has_bike = true
	place(-6.6, 60.0, PI, 0.0)
	await get_tree().create_timer(0.3).timeout
	m.bike_key()
	var bk: Node3D = m.street.riding
	m.player.collision_mask = 0
	await get_tree().create_timer(0.5).timeout
	var sk: Skeleton3D = m.skins[m.skin_idx].root.find_children("*", "Skeleton3D", true, false)[0]
	for b in ["Hips", "Spine2", "Head", "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftArm", "LeftForeArm", "LeftHand"]:
		var i := sk.find_bone(m.street.bone(sk, "mixamorig:" + b))
		var g := m.model.to_local(sk.global_transform * sk.get_bone_global_pose(i).origin)
		var r := m.model.to_local(sk.global_transform * sk.get_bone_global_rest(i).origin)
		print("BONE %-10s pose (%.2f, %.2f, %.2f)   rest (%.2f, %.2f, %.2f)" % [b, g.x, g.y, g.z, r.x, r.y, r.z])
	for nm in ["seat", "pedal_l", "pedal_r", "grip_l", "grip_r", "front", "rear"]:
		var n: Node3D = bk.get(nm)
		var q := m.model.to_local(n.global_position)
		print("BIKE %-8s (%.2f, %.2f, %.2f)" % [nm, q.x, q.y, q.z])
	var cc := Camera3D.new()
	m.model.add_child(cc)
	cc.fov = 35.0
	cc.current = true
	for v in [["stopped", 0.0], ["slow", 0.5], ["fast", 1.0]]:
		m.vkeys.clear()
		if v[1] > 0.0:
			m.vkeys[KEY_W] = true
		var want: float = m.street.BIKE_SPEED * v[1]
		for k in 120:
			await get_tree().physics_frame
			if m.speed > want:
				m.speed = want
		for side in [["side", Vector3(-3.6, 0.65, 0.0)], ["front", Vector3(-2.0, 0.9, 3.0)], ["back", Vector3(1.6, 1.3, -3.0)], ["three_quarter", Vector3(-2.4, 1.0, 1.6)]]:
			cc.position = side[1]
			cc.look_at(m.model.global_transform * Vector3(0, 0.62, 0.0), Vector3.UP)
			await get_tree().process_frame
			await get_tree().process_frame
			get_viewport().get_texture().get_image().save_png(dir.path_join("%s_%s.png" % [v[0], side[0]]))
		print("SHOT %s speed=%.1f" % [v[0], m.speed])
	end_test()


func run_veer(dir: String) -> void:
	# running forward and veering left and right, as a player would: prints, every tenth of a second,
	# how fast her direction and the camera are turning, and the biggest jolt in each
	DirAccess.make_dir_recursive_absolute(dir)
	printerr("veer: start")
	await get_tree().create_timer(3.0).timeout
	printerr("veer: placed")
	m.player.collision_mask = 0
	place(-6.6, 60.0, PI, 0.0)
	await get_tree().create_timer(0.3).timeout
	var plan := [[[KEY_W], 1.5], [[KEY_W, KEY_D], 0.5], [[KEY_W], 0.8], [[KEY_W, KEY_A], 0.5], [[KEY_W], 0.8],
		[[KEY_W, KEY_D], 0.25], [[KEY_W, KEY_A], 0.25], [[KEY_W, KEY_D], 0.25], [[KEY_W, KEY_A], 0.25], [[KEY_W], 1.0],
		[[KEY_W, KEY_D], 2.0], [[KEY_W], 1.5]]
	var last_h := atan2(m.move_dir.x, m.move_dir.y)
	var last_c := m.cam_yaw_node.rotation.y
	var last_hw := 0.0
	var last_cw := 0.0
	var worst := {"heading_rate": 0.0, "heading_jolt": 0.0, "camera_rate": 0.0, "camera_jolt": 0.0}
	var shot_k := 0
	for st in plan:
		m.vkeys.clear()
		for k in st[0]:
			m.vkeys[k] = true
		var frames := int(st[1] * 60.0)
		for f in frames:
			await get_tree().physics_frame
			var dt := 1.0 / 60.0
			var h := atan2(m.move_dir.x, m.move_dir.y)
			var c := m.cam_yaw_node.rotation.y
			var hw := wrapf(h - last_h, -PI, PI) / dt
			var cw := wrapf(c - last_c, -PI, PI) / dt
			worst.heading_rate = maxf(worst.heading_rate, absf(hw))
			worst.camera_rate = maxf(worst.camera_rate, absf(cw))
			worst.heading_jolt = maxf(worst.heading_jolt, absf(hw - last_hw) / dt)
			worst.camera_jolt = maxf(worst.camera_jolt, absf(cw - last_cw) / dt)
			last_h = h
			last_c = c
			last_hw = hw
			last_cw = cw
			if f % 6 == 0:
				printerr("  keys=%-3s heading=%5.0f deg  turning=%5.2f rad/s  camera turning=%5.2f rad/s  camera off=%4.0f deg" % [
					"".join(st[0].map(func(k): return OS.get_keycode_string(k))), rad_to_deg(h), hw, cw,
					rad_to_deg(wrapf(c - (h + PI), -PI, PI))])
		get_viewport().get_texture().get_image().save_png(dir.path_join("v%02d.png" % shot_k))
		shot_k += 1
	printerr("WORST ", worst)
	end_test()


func run_fronts(dir: String) -> void:
	# each Meshy building and its neighbours, straight on and from along the street, to check that the
	# fronts and rooflines line up (scene.json "fronts": centre, outward normal)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	place(-200.0, -200.0, 0.0)
	var cc := Camera3D.new()
	add_child(cc)
	cc.far = 400.0
	cc.fov = 60.0
	cc.current = true
	var fronts: Array = m.D.get("fronts", [])
	for k in fronts.size():
		var f = fronts[k]
		var c := Vector3(f.pos[0], 7.0, f.pos[1])
		var n := Vector3(f.normal[0], 0, f.normal[1])
		var u := Vector3(-n.z, 0, n.x)
		for v in [["front", n * 11.5 + Vector3(0, -5.3, 0)], ["high", n * 12.0 + Vector3(0, 9.0, 0)], ["along", n * 9.0 + u * 22.0], ["along2", n * 9.0 - u * 22.0]]:
			cc.global_position = c + v[1]
			cc.fov = 80.0 if v[0] == "front" else 60.0
			cc.look_at(c + (Vector3(0, 1.0, 0) if v[0] == "front" else Vector3.ZERO), Vector3.UP)
			await get_tree().create_timer(0.6).timeout
			await get_tree().process_frame
			get_viewport().get_texture().get_image().save_png(dir.path_join("%s_%s.png" % [f.name, v[0]]))
	# a section through the middle of each: an orthographic camera looking along the street with
	# everything in front of the centre line clipped away, so the profile of the front shows
	cc.projection = Camera3D.PROJECTION_ORTHOGONAL
	cc.size = 22.0
	for k in fronts.size():
		var f = fronts[k]
		var n := Vector3(f.normal[0], 0, f.normal[1])
		var u := Vector3(-n.z, 0, n.x)
		for off in [0.0, 5.5]:
			var c: Vector3 = Vector3(f.pos[0], 8.0, f.pos[1]) + u * off
			cc.global_position = c + u * 40.0 + n * 3.0
			cc.near = 40.0
			cc.look_at(c + n * 3.0, Vector3.UP)
			await get_tree().create_timer(0.5).timeout
			await get_tree().process_frame
			get_viewport().get_texture().get_image().save_png(dir.path_join("%s_section%d.png" % [f.name, int(off)]))
	printerr("fronts done ", fronts.size())
	end_test()


func run_cast(dir: String) -> void:
	# everyone side by side in the street, front and back: Sandra (both), Rosa, Montse, and the passers-by
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var at := Vector3(m.D.spawn.pos[0], 0.0, m.D.spawn.pos[1] - 6.0)        # on the beach, in the open
	at.y = m.ground_at(at)
	place(at.x - 30.0, at.z, 0.0)
	var files := ["sandra_a.glb", "man.glb", "oldman.glb", "woman.glb", "man2.glb", "montse.glb"]
	var k := 0
	for f in files:
		var h := Node3D.new()
		m.outdoor.add_child(h)
		h.position = at + Vector3(k * 1.1 - 2.75, 0, 0)
		h.position.y = m.ground_at(h.position)
		var m := m.load_meshy_sandra(f, h)
		if not m.is_empty() and m.ap:
			m.ap.play("Walking" if "--walk" in OS.get_cmdline_user_args() else "Idle_4")
		k += 1
	for j in 7:
		var id: String = ["empar", "anna", "lucia", "laia", "ferran", "bofarull", "manolo"][j]
		var q: Dictionary = m.npcs.make_person(id, m.game.data.NPCS[id], m.outdoor, at + Vector3(j * 1.1 - 3.3, 0, -2.2))
		if not q.is_empty():
			q.holder.rotation.y = 0.0
			q.holder.position.y = m.ground_at(q.holder.position)
	if m.street.has_method("cast_for_test"):
		m.street.cast_for_test(at + Vector3(0, 0, -2.0))
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 40.0
	cc.current = true
	for v in [["front", Vector3(0, 1.0, 7.0)], ["back", Vector3(0, 1.0, -9.0)]]:
		cc.global_position = at + v[1]
		cc.look_at(at + Vector3(0, 0.75, -1.0 if v[0] == "back" else 0.0), Vector3.UP)
		await get_tree().create_timer(1.0).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("cast_%s.png" % v[0]))
	printerr("cast done")
	end_test()


func run_tour(dir: String) -> void:
	# Sandra's eye view round the 2D game's map: the beach where she wakes, the Rambla, her street,
	# the landmarks, the forest, the river and its bridge, Tibidabo, the park; some again at night
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var views := []
	var sp: Array = m.D.spawn.pos
	views.append(["t01_beach_wake", Vector2(sp[0], sp[1]), PI, "golden"])
	for id in ["apt_sandra", "cafe_rambla", "sagrada", "casa_batllo", "upf", "mnac", "carrefour", "torro_joan"]:
		for e in m.D.entrances:
			if e.id == id:
				var n := Vector2(e.normal[0], e.normal[1])
				views.append(["t_" + id, Vector2(e.pos[0], e.pos[1]) + n * 7.0, atan2(-n.x, -n.y), "day" if views.size() % 2 else "golden"])
	var w := func(X: float, Y: float) -> Vector2: return Vector2((X + 0.5 - 55) * 3.3, (Y + 0.5 - 45) * 3.3)
	var D2: Dictionary = m.game.data
	views.append(["t_montse_rambla", w.call(D2.NPCS.montse.at[1], D2.NPCS.montse.at[2] + 2), PI, "golden"])
	views.append(["t_rambla_north", w.call(D2.NPCS.montse.at[1], D2.NPCS.montse.at[2] + 20), PI, "day"])
	views.append(["t_forest_trufa", w.call(D2.TRUFA.at[1] - 4, D2.TRUFA.at[2]), PI / 2.0, "golden"])
	views.append(["t_forest_deep", w.call(D2.TRUFA.at[1] + 6, D2.TRUFA.at[2] + 10), PI, "day"])
	views.append(["t_bridge_guard", w.call(D2.NPCS.sergi.at[1] + 3, D2.NPCS.sergi.at[2]), -PI / 2.0, "golden"])
	var st: Array = m.D.steps.rect
	views.append(["t_tibidabo_steps", Vector2((st[0] + st[2]) / 2.0, st[3] + 4.0), PI, "golden"])
	views.append(["t_tibidabo_top", Vector2((st[0] + st[2]) / 2.0, st[1] - 3.0), PI, "day"])
	for s2 in m.D.streets:
		if s2.name == "Parc de la Ciutadella":
			views.append(["t_ciutadella", Vector2((s2.rect[0] + s2.rect[2]) / 2.0, (s2.rect[1] + s2.rect[3]) / 2.0), PI, "golden"])
	views.append(["n_beach", Vector2(sp[0], sp[1]), PI, "night"])
	views.append(["n_rambla", w.call(D2.NPCS.montse.at[1], D2.NPCS.montse.at[2] + 2), PI, "night"])
	for v in views:
		m.apply_preset(v[3])
		place(v[1].x, v[1].y, v[2])
		m.cam_pitch_node.rotation.x = m.CAM_PITCH
		m.arm.spring_length = m.CAM_DIST
		await get_tree().create_timer(0.4).timeout
		printerr("%-20s ground %.2f  %s" % [v[0], m.ground_at(m.player.global_position), m.street_name(m.player.global_position)])
		await shot(dir, v[0])
	end_test()

func run_walkers(dir: String) -> void:
	# close-ups of a few passers-by, side on, walking and standing
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 40.0
	cc.current = true
	for k in mini(6, m.people.people.size()):
		var p: Dictionary = m.people.people[k]
		place(p.holder.position.x + 20.0, p.holder.position.z + 20.0, 0.0)
		for f in 30:
			await get_tree().process_frame
			var h: Node3D = p.holder
			var side := h.global_transform.basis.z
			cc.global_position = h.global_position + side * 3.6 + Vector3(0, 1.0, 0)
			cc.look_at(h.global_position + Vector3(0, 0.65, 0), Vector3.UP)
		var ap: AnimationPlayer = p.m.ap
		printerr("walker %d anim=%s moving=%.1f pos=%s" % [k, ap.current_animation if ap else "-", p.moving, p.holder.position])
		get_viewport().get_texture().get_image().save_png(dir.path_join("w%d.png" % k))
	end_test()


func run_perf() -> void:
	# what costs most on Sandra's street: the triangles drawn with everything, then with each kind of
	# thing hidden in turn
	await get_tree().create_timer(3.0).timeout
	var city := m.outdoor.get_child(0)
	var groups := {"windows near": ["WinHi"], "windows far": ["WinLo"], "detail": ["Detail_"], "plants": ["Plants_", "PlanterLeaves_", "Bougainvillea_"],
		"trees": ["Tree_", "Leaves_"], "lamps": ["MeshyLamp_"], "meshy buildings": ["MeshyBuilding"], "blocks": ["Block_"],
		"cafes+benches": ["KitCafe", "MeshyCafe", "StreetBench", "MeshyBench", "ParkBench", "SeaBench", "BeachCafe"], "text": ["KitText_", "PlaqueText_"],
		"wares": ["Wares_", "Bins_", "BikeStand_"], "backdrop+hills": ["Backdrop", "Hills"], "forest": ["ForestTrunks_", "Leaves_forest_"],
		"forest far": ["Leaves_far_", "ForestFar_"], "forest plants": ["Plants_forest", "Grass_", "Detail_toadstools"],
		"hill woods": ["ForestTrunks_n", "Leaves_forest_n", "HillFarTrees"], "north": ["North", "Fair", "Guell", "Gracia", "Cable", "Wheel", "Path"]}
	var spots := [["home street", Vector2(1.0, 11.4), PI * 0.5], ["girona", Vector2(11.0, 2.0), 0.0], ["forest path", Vector2(40.5, 5.0), 0.0],
			["meadow", Vector2(28.5, -2.5), PI * 0.5]]
	if "--forestperf" in OS.get_cmdline_user_args():
		spots = [["forest path", Vector2(40.5, 5.0), 0.0], ["forest north", Vector2(40.9, -6.0), 0.0], ["forest south", Vector2(41.0, 25.0), PI],
			["forest glade", Vector2(43.0, 1.5), PI * 0.5], ["forest east", Vector2(48.0, 10.0), PI * 0.5]]
	for v in spots:
		place(v[1].x * 3.3, v[1].y * 3.3, v[2])
		await get_tree().create_timer(1.5).timeout
		var base := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)
		var calls := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)
		printerr("PERF %s: %dk triangles, %d draw calls, %d fps" % [v[0], base / 1000, calls, Engine.get_frames_per_second()])
		m.sun.shadow_enabled = false
		await get_tree().create_timer(1.0).timeout
		printerr("   (no sun shadows: %d fps, %dk triangles)" % [Engine.get_frames_per_second(), RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME) / 1000])
		m.sun.shadow_enabled = true
		await get_tree().create_timer(0.5).timeout
		for g in groups:
			var hidden := []
			for n in city.get_children():
				for pre in groups[g]:
					if String(n.name).begins_with(pre) and n.visible:
						n.visible = false
						hidden.append(n)
			for k in 4:
				await get_tree().process_frame
			var tri := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)
			var dc := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)
			printerr("   %-16s %5dk triangles  %4d draw calls  (%d objects)" % [g, (base - tri) / 1000, calls - dc, hidden.size()])
			for n in hidden:
				n.visible = true
	end_test()


func run_moves() -> void:
	# lots of ways of moving her, as a player would, on open ground; for each: how far she turned in the
	# first fifth of a second, her fastest turn, how often her turning flipped direction (zig-zags), where
	# she ended up heading and how far the camera is from behind her
	await get_tree().create_timer(3.0).timeout
	m.player.collision_mask = 0
	var plans := [
		["forward, then forward+right held", [[[KEY_W], 1.2], [[KEY_W, KEY_D], 3.0]]],
		["forward, tap right", [[[KEY_W], 1.2], [[KEY_W, KEY_D], 0.2], [[KEY_W], 1.5]]],
		["forward, forward+left 1 s, let go", [[[KEY_W], 1.2], [[KEY_W, KEY_A], 1.0], [[KEY_W], 2.0]]],
		["forward, then down (run back)", [[[KEY_W], 1.5], [[KEY_S], 3.0]]],
		["forward, down, then forward again", [[[KEY_W], 1.5], [[KEY_S], 1.5], [[KEY_W], 1.5]]],
		["down from standing", [[[KEY_S], 3.0]]],
		["right from standing, held", [[[KEY_D], 5.0]]],
		["right from standing, then forward", [[[KEY_D], 1.5], [[KEY_W], 2.0]]],
		["zig-zag taps", [[[KEY_W], 1.0], [[KEY_W, KEY_D], 0.3], [[KEY_W, KEY_A], 0.3], [[KEY_W, KEY_D], 0.3], [[KEY_W, KEY_A], 0.3], [[KEY_W], 1.0]]],
		["down+right while running", [[[KEY_W], 1.5], [[KEY_S, KEY_D], 2.0]]],
		["stop and go", [[[KEY_W], 1.0], [[], 0.6], [[KEY_W], 1.0]]],
		["forward, mouse turns right", [[[KEY_W], 1.0], [[KEY_W], 1.5, "mouse"]]],
	]
	for pl in plans:
		m.vkeys.clear()
		place(0.0, 150.0, PI, 0.0)                  # facing north, camera behind
		await get_tree().create_timer(0.3).timeout
		var last_h := atan2(m.move_dir.x, m.move_dir.y)
		var flips := 0
		var last_sign := 0.0
		var max_rate := 0.0
		var first_turn := INF
		var since_turn := 0.0
		var trace := []
		for st in pl[1]:
			m.vkeys.clear()
			for k in st[0]:
				m.vkeys[k] = true
			var frames := int(st[1] * 60.0)
			var h_at_start := atan2(m.move_dir.x, m.move_dir.y)
			for f in frames:
				if st.size() > 2:
					m.turn_camera(-0.9 / 60.0, 0.0)
				await get_tree().physics_frame
				var h := atan2(m.move_dir.x, m.move_dir.y)
				var w := wrapf(h - last_h, -PI, PI) * 60.0
				last_h = h
				max_rate = maxf(max_rate, absf(w))
				if absf(w) > 0.3:
					if last_sign != 0.0 and signf(w) != last_sign:
						flips += 1
					last_sign = signf(w)
				if f == 12 and st[0].size() > 1:
					first_turn = rad_to_deg(absf(wrapf(h - h_at_start, -PI, PI)))
				if f % 30 == 29:
					trace.append("%d" % roundi(rad_to_deg(wrapf(-h + PI, -PI, PI))))
		var cam_off := rad_to_deg(wrapf(m.cam_yaw_node.rotation.y - (atan2(m.move_dir.x, m.move_dir.y) + PI), -PI, PI))
		printerr("%-38s bite(0.2s)=%s  fastest=%.1f rad/s  zig-zags=%d  heading every 0.5s: %s  camera off her back=%d" % [
			pl[0], ("%.0f deg" % first_turn) if first_turn != INF else "-", max_rate, flips, " ".join(trace), roundi(cam_off)])
	m.vkeys.clear()
	end_test()


func talk_through(choice = 0, log := false) -> int:
	# reads a whole conversation, answering every question with the given option (or a list of options
	# in turn, then always the last, "no thanks" one); returns the pages read
	var pages := 0
	var picks: Array = choice.duplicate() if choice is Array else []
	for i in 400:
		await get_tree().process_frame
		if not m.dlg_open:
			await get_tree().process_frame
			if not m.dlg_open:
				break
			continue
		if m.panels.is_open():
			# the shop counter: buy the chosen thing (if a choice was given), then leave
			var c2: int = (picks.pop_front() if not picks.is_empty() else -1) if choice is Array else -1
			if m.panels.kind == "shop" and c2 >= 0:
				m.panels.sel = c2
				m.panels.buy_selected()
				if log:
					printerr("    [shop] bought choice %d" % c2)
				await get_tree().process_frame
			if m.panels.is_open():
				if log:
					printerr("    [%s panel] -> leave" % m.panels.kind)
				m.panels.close(false)
			continue
		pages += 1
		if log:
			printerr("    %s: %s" % [m.dlg_who.text, m.dlg_text.text.left(110)])
		if m.choice_box.visible:
			var c: int = (picks.pop_front() if not picks.is_empty() else -1) if choice is Array else choice
			m.dlg_choice = m.dlg_choices.size() - 1 if c < 0 else mini(c, m.dlg_choices.size() - 1)
			if log:
				printerr("    -> ", m.dlg_choices[m.dlg_choice])
		m.dialog_next()
	return pages


func run_wallscan(dir: String) -> void:
	# (round 41, the user: "You should not be able to see through walls. pillars are ok") in each walked-round room
	# (the street camera indoors), Sandra stood on a grid over its floor, the camera turned all the way round her at
	# three tilts: any view with much of the black beyond the room's walls in it is counted, and the worst saved
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var rooms := ["int_sagrat_cor", "int_sagrat_alta", "int_sagrada"]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--rooms="):
			rooms = Array(a.substr(8).split(","))
	for rid in rooms:
		m.enter_room(rid, true)
		await get_tree().create_timer(1.5).timeout
		var R: Dictionary = m.D.interiors[rid]
		var O: Vector3 = m.room_base(rid)
		var bad := 0
		var views := 0
		var saved := 0
		var y := 1.6
		while y < float(R.h) - 0.5:
			var x := 1.6
			while x < float(R.w) - 1.5:
				var blocked := false
				for sd in R.solids:
					if x > sd[0] - 0.3 and x < sd[2] + 0.3 and y > sd[1] - 0.3 and y < sd[3] + 0.3:
						blocked = true
				for pt in R.get("posts", []):
					if Vector2(x - pt[0], y - pt[1]).length() < float(pt[2]) + 0.4:
						blocked = true
				if not blocked:
					m.player.global_position = O + Vector3(x, 0, y)
					m.player.velocity = Vector3.ZERO
					await get_tree().physics_frame
					for pitch in [m.CAM_PITCH, -0.75, 0.15]:
						for k in 8:
							m.cam_yaw_node.rotation.y = k * PI / 4.0
							m.cam_pitch_node.rotation.x = pitch
							m.last_manual_cam = m.t
							await get_tree().process_frame
							await get_tree().process_frame
							await RenderingServer.frame_post_draw
							var img := get_viewport().get_texture().get_image()
							img.resize(160, 100)
							var dark := 0
							for py in range(0, 100, 2):
								for px in range(0, 160, 2):
									var c := img.get_pixel(px, py)
									if c.r + c.g + c.b < 0.04:
										dark += 1
							var f := float(dark) / 4000.0
							views += 1
							if f > 0.06:
								bad += 1
								printerr("WALLSCAN %s at (%.1f, %.1f) yaw %d pitch %.2f: %.0f%% dark" % [rid, x, y, k * 45, pitch, f * 100.0])
								if saved < 12:
									saved += 1
									get_viewport().get_texture().get_image().save_png(dir.path_join("%s_%02d.png" % [rid, saved]))
				x += 2.0
			y += 2.0
		printerr("WALLSCAN %s: %d of %d views see the dark" % [rid, bad, views])
		m.leave()
		await get_tree().create_timer(2.0).timeout
	end_test()


func run_benchsit(dir: String) -> void:
	# (round 41) sitting on benches: for a hill bench and a city one, standing before it, what E offers; sat, the view
	# ahead and turned left; then E again, standing (benches.gd)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var bl: Array = m.benches.list
	printerr("BENCHSIT %d benches" % bl.size())
	var picks := []
	for i in bl.size():
		if picks.size() == 0 and (bl[i][0] as Vector2).y < -150.0:
			picks.append(i)
	for i in bl.size():
		if (bl[i][0] as Vector2).y > -60.0:
			picks.append(i)
			break
	for i in picks:
		var b: Array = bl[i]
		var fr: Vector2 = b[0] + b[1] * 0.75
		place(fr.x, fr.y, atan2(-b[1].x, -b[1].y))
		await get_tree().create_timer(1.5).timeout
		var n: Dictionary = m.nearest()
		printerr("BENCHSIT %d at (%.1f,%.1f) offers: %s" % [i, b[0].x, b[0].y, n.get("label", "NOTHING")])
		shot(dir, "b%d_0_standing" % i)
		m.interact()
		await get_tree().create_timer(1.5).timeout
		printerr("BENCHSIT sat %s prompt '%s'" % [m.benches.seated(), m.prompt.text])
		shot(dir, "b%d_1_sat_ahead" % i)
		m.turn_camera(0.9, 0.0)
		await get_tree().create_timer(1.0).timeout
		shot(dir, "b%d_2_sat_left" % i)
		# (round 41: her body sitting) looking down at her lap; then from outside, her head shown for the picture
		m.turn_camera(-0.9, 0.0)
		m.cam_pitch_node.rotation.x = -1.0
		await get_tree().create_timer(0.8).timeout
		shot(dir, "b%d_4_sat_down" % i)
		m.benches.pose.hide_head = false
		m.ride_look = false
		m.cam_pitch_node.rotation.x = -0.25
		m.turn_camera(2.4, 0.0)
		await get_tree().create_timer(2.0).timeout
		shot(dir, "b%d_5_sat_outside" % i)
		m.ride_look = true
		m.benches.pose.hide_head = true
		m.benches.stand()
		await get_tree().create_timer(1.5).timeout
		var p: Vector3 = m.local_pos()
		printerr("BENCHSIT stood at (%.2f,%.2f) seated %s" % [p.x, p.z, m.benches.seated()])
		shot(dir, "b%d_3_stood" % i)
	end_test()


func run_roadprobe() -> void:
	# (round 41, the user: "this NPC is just standing in the street") every walker's way, sampled along its middle line:
	# where it lies on a road (the ground's own height, not a pavement's kerb) in the city
	await get_tree().create_timer(3.0).timeout
	var ppl: Array = m.people.people
	for i in ppl.size():
		var w: Dictionary = ppl[i]
		var bad := []
		for k in 51:
			var fr: Array = m.people.frame(w.pts, w.cum, float(k) / 50.0 * float(w.L))
			var q: Vector3 = fr[0]
			for off in [0.0, -0.75, 0.75]:
				var qq: Vector3 = q + (fr[1] as Vector3) * off
				var g: float = m.ground_at(qq)
				if q.z > -104.0 and g < 0.02:
					bad.append("t%.2f off%+.2f (%.1f,%.1f) g%.3f" % [float(k) / 50.0, off, qq.x, qq.z, g])
		if not bad.is_empty():
			printerr("ROADPROBE walker %d a(%.1f,%.1f) b(%.1f,%.1f): %d on the road: %s" % [i, w.a.x, w.a.z, w.b.x, w.b.z, bad.size(), ", ".join(bad.slice(0, 6))])
	printerr("ROADPROBE done, %d walkers" % ppl.size())
	end_test()


func run_turnprobe() -> void:
	# (round 41, the user: "If I run too close to the turnstiles I can't press E") what E offers, standing at points
	# round each funicular station's turnstile, after she has walked there (so the walls stop her where they do)
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["amicCard"] = true
	for st in ["door_low", "door_top"]:
		var d: Array = m.D.north.cable[st]
		for dz in [3.0, 1.5, 0.0, -1.0, -2.0, -3.0]:
			for dx in [-1.5, 0.0, 1.5]:
				place(d[0] + dx, d[1] + dz + (2.5 if dz < 0 else 0.0), PI if dz < 0 else 0.0)
				await get_tree().create_timer(0.15).timeout
				if dz < 0:                                  # (walk in towards the turnstile for a moment)
					Input.action_press("ui_up")
					await get_tree().create_timer(0.8).timeout
					Input.action_release("ui_up")
					await get_tree().create_timer(0.2).timeout
				var p: Vector3 = m.local_pos()
				var n: Dictionary = m.nearest()
				printerr("TURNPROBE %s want(%+.1f,%+.1f) at (%.2f,%.2f) off(%.2f,%.2f) -> %s" % [st, dx, dz, p.x, p.z, p.x - d[0], p.z - d[1], n.get("label", "NOTHING")])
	end_test()


func run_armprobe() -> void:
	# (round 41, the user: "Their hands are going backwards… do a proper full analysis on the body") each person's arm
	# joints measured standing, in their own frame (x their left, y up, z forward), with and without posture.gd's arms:
	# upper arm and forearm angles forward of straight down, the elbow's bend, the wrist's bend (+: the hand forward of
	# the forearm's line), the palm's facing, and the wrist's place against the hip joint
	await get_tree().create_timer(3.0).timeout
	var at := Vector3(m.D.spawn.pos[0], 0.0, m.D.spawn.pos[1] - 6.0)
	place(at.x - 40.0, at.z, 0.0)
	var ids := ["quim", "toni", "bofarull", "sergi", "pau", "pere", "vicenc", "dolors", "quima", "maria", "oscar", "silvia", "albert", "tomas", "ferran", "empar", "merce"]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--ids="):
			ids = Array(a.substr(6).split(","))
	var qs := []
	for j in ids.size():
		var p := at + Vector3(j * 1.6, 0, 0)
		p.y = m.ground_at(p)
		var q: Dictionary = m.npcs.make_person(ids[j], m.game.data.NPCS[ids[j]], m.outdoor, p)
		q.holder.rotation.y = 0.0
		qs.append(q)
	var bn := ["Hips", "Spine", "Spine2", "Neck", "Head", "LeftShoulder", "RightShoulder", "LeftArm", "LeftForeArm", "LeftHand", "LeftHandMiddle1", "LeftHandMiddle3", "LeftHandMiddle4",
		"RightHandMiddle3", "RightArm", "RightForeArm", "RightHand", "RightHandMiddle1", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightFoot"]
	for q in qs:
		q.m.posture.probe = bn
	for mode in ["off", "on"]:
		for q in qs:
			q.m.posture.arms_w = 0.0 if mode == "off" else 1.0
		await get_tree().create_timer(1.5).timeout
		for q in qs:
			var P: Dictionary = q.m.posture.probed
			if not P.has("Head") or not P.has("LeftUpLeg"):
				printerr("ARMPROBE %s missing %s" % [q.id, P.keys()])
				continue
			var hip: Vector3 = (P.LeftUpLeg + P.RightUpLeg) / 2.0
			var foot: Vector3 = (P.LeftFoot + P.RightFoot) / 2.0
			var s := 1.7 / maxf(0.1, P.Head.y - foot.y)            # (in cm of a 1.7 m-tall person, eye to sole)
			var z := func(k: String) -> String: return "%+.0f" % ((P[k].z - hip.z) * 100.0 * s) if P.has(k) else "?"
			var line := "%-9s %-3s fwd of hip (cm): foot %+.0f neck %s head %s shoulderL %s shoulderR %s elbowL %s wristL %s wristR %s fingersL %s fingersR %s" % [
				q.id, mode, (foot.z - hip.z) * 100.0 * s, z.call("Neck"), z.call("Head"), z.call("LeftArm"), z.call("RightArm"),
				z.call("LeftForeArm"), z.call("LeftHand"), z.call("RightHand"), z.call("LeftHandMiddle1"), z.call("RightHandMiddle1")]
			var ua: Vector3 = P.LeftForeArm - P.LeftArm
			var fa: Vector3 = P.LeftHand - P.LeftForeArm
			line += " | L upperarm %+.0f° forearm %+.0f° elbow %.0f° out %.0f° | wrist height %.0f%% of hip" % [
				rad_to_deg(atan2(ua.z, -ua.y)), rad_to_deg(atan2(fa.z, -fa.y)), rad_to_deg(ua.angle_to(fa)),
				rad_to_deg(atan2(absf(ua.x), -ua.y)), (P.LeftHand.y - foot.y) / maxf(0.01, hip.y - foot.y) * 100.0]
			# (round 41, "their shoulders are very high") the collarbone's rise and the shoulder joint against the neck
			for sd2 in ["Left", "Right"]:
				if P.has(sd2 + "Shoulder"):
					var cl: Vector3 = P[sd2 + "Arm"] - P[sd2 + "Shoulder"]
					var ua2: Vector3 = P[sd2 + "ForeArm"] - P[sd2 + "Arm"]
					line += " | %s collarbone rise %+.0f° shoulder above neck %+.1fcm arm out %.0f° shoulder width %.0fcm" % [sd2[0],
						rad_to_deg(atan2(cl.y, Vector2(cl.x, cl.z).length())), (P[sd2 + "Arm"].y - P.Neck.y) * 100.0 * s,
						rad_to_deg(atan2(ua2.x * (1.0 if sd2 == "Left" else -1.0), -ua2.y)), absf(P.LeftArm.x - P.RightArm.x) * 100.0 * s]
			for sd3 in ["Left", "Right"]:
				if P.has(sd3 + "HandMiddle3"):
					var fa3: Vector3 = P[sd3 + "Hand"] - P[sd3 + "ForeArm"]
					var pa3: Vector3 = P[sd3 + "HandMiddle1"] - P[sd3 + "Hand"]
					var fi3: Vector3 = P[sd3 + "HandMiddle3"] - P[sd3 + "HandMiddle1"]
					line += " | %s forearm %+.0f° palm %+.0f° fingers %+.0f°" % [sd3[0], rad_to_deg(atan2(fa3.z, -fa3.y)),
						rad_to_deg(atan2(pa3.z, -pa3.y)), rad_to_deg(atan2(fi3.z, -fi3.y))]
			printerr("ARMPROBE ", line)
	end_test()


func run_rosalily(dir: String) -> void:
	# (round 41, the street's real name, rule 10 #51d) Rosa at home, talked to until she explains Flor de Lliri; then
	# the line at the top once the exam is passed ("Exam complete!", no season, #51a)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var e: Dictionary = entrance("int_sandra")                  # outside her door: the street's name at the top
	place(e.pos[0] + 1.4, e.pos[1] + 2.2, PI)
	await get_tree().create_timer(2.5).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("0a_outside_her_door.png"))
	place(e.pos[0] - 1.07, e.pos[1] + 0.9, PI)                  # (the brass plaque beside it, read)
	await get_tree().create_timer(0.5).timeout
	m.interact()
	await get_tree().create_timer(3.0).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("0b_door_plaque_read.png"))
	printerr("ROSALILY plaque: ", m.dlg_text.text)
	await talk_through([])
	await go_in(e)
	var q: Dictionary = m.npcs.current().get("rosa", {})
	var p: Vector3 = q.holder.global_position
	place(p.x, p.z + 1.1, PI)
	var seen := false
	for talk in 16:
		await get_tree().create_timer(0.3).timeout
		m.game.talk_to("rosa")
		for i in 400:
			await get_tree().process_frame
			if not m.dlg_open:
				break
			if m.dlg_text.text.contains("Lliri means"):
				await get_tree().create_timer(4.0).timeout
				get_viewport().get_texture().get_image().save_png(dir.path_join("1_rosa_lily_line.png"))
				printerr("ROSALILY ", m.dlg_text.text)
				seen = true
			if m.choice_box.visible:
				m.dlg_choice = m.dlg_choices.size() - 1
			m.dialog_next()
		if seen:
			break
	printerr("ROSALILY seen=", seen)
	await go_out()
	m.game.S.flags.examPassed = true
	for k in m.game.data.MISSIONS:
		m.game.S.missions[k] = {"st": "done", "num": 0}
	await get_tree().create_timer(1.5).timeout
	printerr("ROSALILY top line: ", m.game.objective_text())
	get_viewport().get_texture().get_image().save_png(dir.path_join("2_exam_complete.png"))
	end_test()


func go_in(e: Dictionary) -> void:
	var n := Vector2(e.normal[0], e.normal[1])
	place(e.pos[0] + n.x * 2.0, e.pos[1] + n.y * 2.0, atan2(-n.x, -n.y))
	await get_tree().create_timer(0.2).timeout
	m.enter(e)
	await get_tree().create_timer(1.0).timeout


func go_out() -> void:
	m.leave()
	await get_tree().create_timer(1.0).timeout


func entrance(int_id: String) -> Dictionary:
	for en in m.D.entrances:
		if en.int == int_id:
			return en
	return {}


func run_rooms(dir: String) -> void:
	# every building: in by its door, a picture of the room, who is there, out again by walking
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var bad := 0
	for e in m.D.entrances:
		await go_in(e)
		var ok: bool = m.where == "in" and m.room == e.int
		await shot(dir, "room_" + e.int)
		printerr("%-16s %-16s in=%s people=%s things=%d" % [e.id, e.int, ok, m.npcs.indoor.keys(), m.D.interiors[e.int].things.size()])
		# (round 26) a greeting on the way in (Rosa's, while the "home" mission is on in the test save) is read through first
		var lines := 0
		while m.dlg_open and lines < 30:
			m.dialog_next()
			lines += 1
			await get_tree().create_timer(0.3).timeout
		if e.int == "int_upf":
			var st: Dictionary = m.D.interiors.int_upf.stairs[0]
			m.enter_room(st.to, true)
			await get_tree().create_timer(1.2).timeout
			printerr("  upstairs: ", m.room, " people=", m.npcs.indoor.keys())
			await shot(dir, "room_int_upf_lib")
			var st2: Dictionary = m.D.interiors.int_upf_lib.stairs[0]
			m.enter_room(st2.to, true)
			await get_tree().create_timer(1.2).timeout
			printerr("  downstairs: ", m.room)
		var R: Dictionary = m.D.interiors[m.room]
		if R.get("free_cam", false):
			# (the street camera indoors: walk forward out of the door she came in by)
			var top: bool = e.get("room_side", "bottom") == "top"
			var ex: Array = R.exit_top if top else R.exit
			m.player.global_position = m.room_base(m.room) + Vector3((ex[0] + ex[1]) / 2.0, 0, 1.8 if top else R.h - 0.8)
			m.cam_yaw_node.rotation.y = 0.0 if top else PI
			m.last_manual_cam = m.t
			await hold(KEY_W, 1.0)
		else:
			m.player.global_position = m.room_base(m.room) + Vector3(R.exit[0] + 0.5, 0, R.h - 0.8)
			m.move_dir = Vector2(0, 1)
			await hold(KEY_S, 1.0)
		await get_tree().create_timer(1.0).timeout
		var back: bool = m.where == "out" and m.player.global_position.distance_to(Vector3(e.pos[0], 0, e.pos[1])) < 3.0
		printerr("  out=%s" % back)
		if not ok or not back:
			bad += 1
	printerr("ROOMS bad=", bad)
	end_test()


func run_talk() -> void:
	# every one of the 2D game's people: found where they should be, and talked to
	await get_tree().create_timer(3.0).timeout
	m.game.S.missions["gift"] = {"st": "active", "num": 2}          # the party only happens during the gift mission
	var by_room := {}
	for id in m.game.data.NPCS:
		var at: String = m.game.data.NPCS[id].at[0]
		by_room[at] = by_room.get(at, []) + [id]
	var missing := []
	var silent := []
	for rid in by_room:
		if rid == "int_upf_lib":
			await go_in(entrance("int_upf"))
			m.enter_room("int_upf_lib", true)
			await get_tree().create_timer(1.2).timeout
		elif rid != "world":
			await go_in(entrance(rid))
		for id in by_room[rid]:
			var q: Dictionary = m.npcs.current().get(id, {})
			if q.is_empty():
				missing.append(id)
				continue
			var p: Vector3 = q.holder.global_position
			m.player.global_position = Vector3(p.x, 0, p.z) + Vector3(0, 0, 1.1)
			m.model.rotation.y = PI
			await get_tree().create_timer(0.15).timeout
			var n: Dictionary = m.nearest()
			if n.get("who", "") != id:
				printerr("  nearest to %s is %s" % [id, n.get("label", "nothing")])
			m.game.talk_to(id)
			var pages: int = await talk_through([])            # (every question: the last, "no thanks" answer)
			printerr("%-10s %-15s %d pages" % [id, rid, pages])
			if pages == 0:
				silent.append(id)
		if rid == "int_upf_lib":
			m.enter_room("int_upf", true)
			await get_tree().create_timer(1.2).timeout
		if rid != "world":
			await go_out()
	printerr("TALK missing=", missing, " silent=", silent)
	end_test()


func talk(id: String, choice = 0) -> void:
	m.game.talk_to(id)
	await talk_through(choice, true)


func run_missions() -> void:
	# the start of the story, played through: home, the birthday card and gift, Montse's dog
	await get_tree().create_timer(3.0).timeout
	var g := m.game
	printerr("objective: ", g.objective_text())
	await go_in(entrance("int_sandra"))
	await talk_through(0, true)
	printerr("home done=", g.m_done("home"), " objective: ", g.objective_text())
	for th in m.D.interiors.int_sandra.things:
		if th.get("card", false):
			g.use_thing(th)
	await talk_through(0, true)
	printerr("gift active=", g.m_active("gift"), " objective: ", g.objective_text())
	await talk("rosa")
	printerr("note1=", g.has_item("note1"))
	await go_out()
	for gi in g.ground:
		if gi.id in ["bottle", "coin"] and gi.node.visible:
			g.pick_up(gi)
	await talk_through(0, true)
	printerr("bottles=", g.count_item("bottle"), " money=", g.money(g.S.money))
	g.S.money = 600                                    # (exactly the torró's €6: round 23 found the shop still asking for €12)
	await go_in(entrance("int_torro_joan"))
	await talk("joan", [0])
	printerr("torro_joan=", g.has_item("torro_joan"), " money=", g.money(g.S.money))
	await go_out()
	await go_in(entrance("int_alessandra"))
	printerr("party people: ", m.npcs.indoor.keys())
	await talk("alessandra")
	printerr("gift done=", g.m_done("gift"), " objective: ", g.objective_text())
	await go_out()
	var mp: Vector3 = m.npcs.outdoor.montse.holder.global_position
	place(mp.x, mp.z + 1.2, PI)
	await talk("montse")
	printerr("dog active=", g.m_active("dog"))
	var tr: Node3D = m.street.trufa
	place(tr.position.x + 1.0, tr.position.z, -PI / 2.0)
	await get_tree().create_timer(0.3).timeout
	var n: Dictionary = m.nearest()
	printerr("near Trufa: ", n.get("label", "nothing"))
	g.talk_trufa()
	await talk_through(0, true)
	printerr("trufa=", g.S.trufa, " state=", tr.state)
	place(mp.x, mp.z + 1.2, PI)
	tr.position = m.player.global_position + Vector3(1, 0, 1)
	await get_tree().create_timer(0.5).timeout
	await talk("montse")
	printerr("dog done=", g.m_done("dog"), " note3=", g.has_item("note3"), " money=", g.money(g.S.money))
	# Sandra's own bike (round 20): Alessandra asked after it at the party; Jordi needs a chain from Genís
	printerr("bike active=", g.m_active("bike"), " num=", g.S.missions.get("bike", {}).get("num", -1), " objective: ", g.objective_text())
	for who in ["jordi", "genis", "jordi"]:
		var hp: Vector3 = m.npcs.outdoor[who].holder.global_position
		place(hp.x, hp.z + 1.2, PI)
		await get_tree().create_timer(0.3).timeout
		await talk(who)
		printerr("  after %s: need=%s chain=%s has_bike=%s objective: %s" % [who, g.S.flags.get("bikeNeed", false), g.has_item("bike_chain"), g.S.has_bike, g.objective_text()])
	printerr("bike done=", g.m_done("bike"))
	g.bag_panel()
	await talk_through(0, true)
	g.journal_panel()
	await talk_through(0, true)
	printerr("MISSIONS ok")
	end_test()


func run_map(path: String) -> void:
	# the whole map from straight above, framed like the 2D game's map (104 x 96 tiles), to compare
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("day")
	m.env_out.fog_enabled = false
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.projection = Camera3D.PROJECTION_ORTHOGONAL
	cc.keep_aspect = Camera3D.KEEP_HEIGHT
	var T := 3.3
	var cx := (52.0 - 55.0) * T
	var cz := (48.0 - 45.0) * T
	var focus := "--zoom" in OS.get_cmdline_user_args()
	cc.size = 96.0 * T if not focus else 40.0 * T
	for a2 in OS.get_cmdline_user_args():
		if a2.begins_with("--tiles="):
			cc.size = float(a2.trim_prefix("--tiles=")) * T
	cc.far = 2000.0
	var at := Vector3(cx, 600.0, cz)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--at="):
			var xy = a.trim_prefix("--at=").split(",")
			at = Vector3((float(xy[0]) - 55.0) * T, 600.0, (float(xy[1]) - 45.0) * T)
	cc.global_position = at
	cc.rotation = Vector3(-PI / 2.0, 0, 0)
	cc.current = true
	m.player.global_position = at - Vector3(0, 600, 0)
	await get_tree().create_timer(2.5).timeout
	get_viewport().get_texture().get_image().save_png(path)
	printerr("map saved")
	end_test()


func run_mapscreen(path: String) -> void:
	# the Tab map, with Sandra on the Rambla by Montse
	await get_tree().create_timer(3.0).timeout
	var mp: Vector3 = m.npcs.outdoor.montse.holder.global_position
	place(mp.x, mp.z + 2.0, PI)
	m.map_panel.visible = true
	await get_tree().create_timer(1.0).timeout
	get_viewport().get_texture().get_image().save_png(path)
	# (round 24) and up the hill, by the funfair: her dot in the round picture of Tibidabo
	m.map_panel.visible = false
	place(-90.0, -284.0, PI)
	await get_tree().create_timer(0.6).timeout
	m.map_panel.visible = true
	await get_tree().create_timer(1.0).timeout
	get_viewport().get_texture().get_image().save_png(path.get_basename() + "_hill.png")
	end_test()


func run_look(path: String) -> void:
	# one picture from a chosen spot: --from=X,Y,height (2D tiles, metres) --to=X,Y,height
	await get_tree().create_timer(3.0).timeout
	var T := 3.3
	var from := Vector3.ZERO
	var to := Vector3.ZERO
	for a in OS.get_cmdline_user_args():
		for key in ["--from=", "--to="]:
			if a.begins_with(key):
				var v = a.trim_prefix(key).split(",")
				var p := Vector3((float(v[0]) - 55.0) * T, float(v[2]), (float(v[1]) - 45.0) * T)
				if key == "--from=":
					from = p
				else:
					to = p
	var preset := "golden"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--preset="):
			preset = a.trim_prefix("--preset=")
	m.apply_preset(preset)
	if "--showrope" in OS.get_cmdline_user_args():
		# (the bike's rope round the wood, drawn as a yellow cord at waist height, for pictures only)
		var cord := StandardMaterial3D.new()
		cord.albedo_color = Color(1.0, 0.85, 0.1)
		cord.emission_enabled = true
		cord.emission = Color(0.6, 0.45, 0.0)
		for r in m.D.get("bike_rope", {}).get("ropes", []):
			var a := Vector3(r[0], 0.9, r[1])
			var b := Vector3(r[2], 0.9, r[3])
			var mi := MeshInstance3D.new()
			var bm := BoxMesh.new()
			bm.size = Vector3(a.distance_to(b), 0.05, 0.05)
			bm.material = cord
			mi.mesh = bm
			add_child(mi)
			mi.global_transform = Transform3D(Basis(Vector3.UP, -Vector2(b.x - a.x, b.z - a.z).angle()), (a + b) / 2.0)
	m.player.global_position = Vector3(to.x, 0, to.z)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--player="):              # (Sandra somewhere else: X,Y in tiles)
			var v = a.trim_prefix("--player=").split(",")
			m.player.global_position = Vector3((float(v[0]) - 55.0) * T, 0, (float(v[1]) - 45.0) * T)
			m.player.global_position.y = m.ground_at(m.player.global_position)
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 55.0
	cc.far = 1500.0
	cc.current = true
	cc.global_position = from
	cc.look_at(to, Vector3.UP)
	for i in 150:                                  # (the game's own camera takes over after the intro's fade)
		cc.current = true
		for c in m.get_children():
			if c is CanvasLayer:
				c.visible = false
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(path)
	end_test()


func run_exitview(dir: String) -> void:
	# (round 23, the user: coming out of the library "you can't see anything") the first moments back outside
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(600.0)
	await go_in(entrance("int_upf"))
	m.enter_room("int_upf_lib", true)
	await get_tree().create_timer(2.0).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("0_library.png"))
	m.enter_room("int_upf", true)
	await get_tree().create_timer(1.5).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("1_hall.png"))
	m.leave()
	var t0 := Time.get_ticks_msec()
	for k in [0.3, 0.5, 0.7, 1.0, 1.5, 2.5, 4.0]:
		while Time.get_ticks_msec() - t0 < k * 1000.0:
			await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png(dir.path_join("2_out_%.1f.png" % k))
		print("EXIT %.1f s fps=%d cam=%s player=%s kept=%s pitch=%.2f cur=%s" % [k, Engine.get_frames_per_second(), get_viewport().get_camera_3d().global_position,
			m.player.global_position, m.kept_cam, m.cam_pitch_node.rotation.x, get_viewport().get_camera_3d().name])
	end_test()


func run_gfxperf() -> void:
	# (round 23: 18 fps in the wood on the user's screen) the frame rate at a forest spot with one costly effect off at a time
	await get_tree().create_timer(3.0).timeout
	place(40.5 * 3.3, 5.0 * 3.3, 0.0)
	var vp := get_viewport()
	var env: Environment = m.env_out
	var tests := [
		["everything", func(): pass, func(): pass],
		["no MSAA", func(): vp.msaa_3d = Viewport.MSAA_DISABLED, func(): vp.msaa_3d = Viewport.MSAA_2X],
		["no SSIL", func(): env.ssil_enabled = false, func(): env.ssil_enabled = true],
		["no SSAO", func(): env.ssao_enabled = false, func(): env.ssao_enabled = true],
		["no vol. fog", func(): env.volumetric_fog_enabled = false, func(): env.volumetric_fog_enabled = true],
		["no glow", func(): env.glow_enabled = false, func(): env.glow_enabled = true],
		["no sun shadow", func(): m.sun.shadow_enabled = false, func(): m.sun.shadow_enabled = true],
		["3D at 75% (FSR)", func():
			vp.scaling_3d_mode = Viewport.SCALING_3D_MODE_FSR
			vp.scaling_3d_scale = 0.75, func(): vp.scaling_3d_scale = 1.0],
		["3D at 75%, no MSAA, no SSIL", func():
			vp.scaling_3d_mode = Viewport.SCALING_3D_MODE_FSR
			vp.scaling_3d_scale = 0.75
			vp.msaa_3d = Viewport.MSAA_DISABLED
			env.ssil_enabled = false, func():
			vp.scaling_3d_scale = 1.0
			vp.msaa_3d = Viewport.MSAA_2X
			env.ssil_enabled = true],
	]
	var rid := vp.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	if "--gfxdrift" in OS.get_cmdline_user_args():
		tests = [tests[0], tests[0], tests[0], tests[0], tests[0], tests[0]]
	for t in tests + [tests[0]]:
		t[1].call()
		await get_tree().create_timer(1.5).timeout
		var gpu := 0.0
		for k in 60:
			await get_tree().process_frame
			gpu += RenderingServer.viewport_get_measured_render_time_gpu(rid)
		printerr("GFX %-30s %d fps  (frames drawn %d, process frames %d, people %d)" % [t[0], Engine.get_frames_per_second(), Engine.get_frames_drawn(),
			Engine.get_process_frames(), m.people.get_child_count() if m.people else -1])
		t[2].call()
		await get_tree().create_timer(0.5).timeout
	end_test()


func run_partyout(dir: String) -> void:
	# (round 23, the user: leaving the party, in the shade of the buildings, "the sun is just behind her") the
	# evening light outside Alessandra's door, walking off along the Passeig both ways, the camera behind her
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	for mins in [1170, 1230, 1260, 1275]:
		m.set_clock(mins)
		for h in [["west", -PI / 2.0], ["north", PI], ["south", 0.0]]:
			place(-100.8, 14.85, h[1])
			m.cam_pitch_node.rotation.x = -0.13
			await get_tree().create_timer(1.2).timeout
			printerr("PARTYOUT %d %s glare=%.2f seen=%.2f" % [mins, h[0], m.glare_k, m.glare_seen])
			get_viewport().get_texture().get_image().save_png(dir.path_join("out_%d_%s.png" % [mins, h[0]]))
	end_test()


func run_facadeflicker() -> void:
	# (round 23, the user: "the shadows flicker on the buildings") a sunny front with balconies, 4 s of the clock
	# running: pixels that change from one frame to the next, and how many of those flip back the next frame (flicker,
	# rather than a shadow gliding on)
	await get_tree().create_timer(3.0).timeout
	m.game.S.time = 13 * 60
	m.light_from_clock()
	var d = m.D.door
	place(d.pos[0] + 30.0, d.pos[1] + 30.0, 0.0)
	m.model.visible = false
	var leaves := "--leaves" in OS.get_cmdline_user_args()
	if "--nosway" in OS.get_cmdline_user_args():
		for k in m.foliage_mats:
			(m.foliage_mats[k] as ShaderMaterial).set_shader_parameter("flutter_amp", 0.0)
		for n in m.outdoor.find_children("Leaves_*", "GeometryInstance3D", true, false):
			(n as GeometryInstance3D).set_instance_shader_parameter("sway_amp", 0.0)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--flutter="):
			for k in m.foliage_mats:
				(m.foliage_mats[k] as ShaderMaterial).set_shader_parameter("flutter_amp", float(a.trim_prefix("--flutter=")))
	if "--leafnoshadow" in OS.get_cmdline_user_args() or "--leafhalfsway" in OS.get_cmdline_user_args():
		var code := FileAccess.get_file_as_string("res://shaders/foliage.gdshader")
		if "--leafnoshadow" in OS.get_cmdline_user_args():
			code = code.replace("render_mode cull_disabled, diffuse_burley;", "render_mode cull_disabled, diffuse_burley, shadows_disabled;")
		var sh2 := Shader.new()
		sh2.code = code
		for k in m.foliage_mats:
			(m.foliage_mats[k] as ShaderMaterial).shader = sh2
		if "--leafhalfsway" in OS.get_cmdline_user_args():
			for n in m.outdoor.find_children("Leaves_*", "GeometryInstance3D", true, false):
				var g := n as GeometryInstance3D
				var v = g.get_instance_shader_parameter("sway_amp")
				g.set_instance_shader_parameter("sway_amp", (0.12 if v == null else float(v)) * 0.5)
	if "--stillsun" in OS.get_cmdline_user_args():
		m.clock_light = false
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 50.0
	cc.global_position = Vector3(d.pos[0] + 4.0, 1.7, d.pos[1] + 9.0)
	cc.look_at(Vector3(d.pos[0] + 4.0, 7.0, d.pos[1]), Vector3.UP)
	if leaves:                                         # (a glade in the wood, looking up at the crowns round it)
		place(141.9, 16.5, 0.0)
		cc.global_position = Vector3(141.9, 1.6, 16.5)
		cc.look_at(Vector3(150.0, 4.0, 10.0), Vector3.UP)
	cc.current = true
	for i in 30:
		await get_tree().process_frame
	var p2: Image = null
	var p1: Image = null
	var changed := 0
	var flips := 0
	var heat := Image.create(320, 200, false, Image.FORMAT_RGB8)
	for i in 240:
		await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		img.resize(320, 200, Image.INTERPOLATE_BILINEAR)
		if p1 and p2:
			for y in range(0, 200, 2):
				for x in range(0, 320, 2):
					var a0 := p2.get_pixel(x, y).get_luminance()
					var a1 := p1.get_pixel(x, y).get_luminance()
					var a2 := img.get_pixel(x, y).get_luminance()
					if absf(a2 - a1) > 0.02:
						changed += 1
						if absf(a2 - a0) < 0.01:
							flips += 1
							var hc := heat.get_pixel(x, y)
							heat.set_pixel(x, y, Color(minf(1.0, hc.r + 0.1), hc.g, hc.b))
		p2 = p1
		p1 = img
		if i == 100:
			for a in OS.get_cmdline_user_args():
				if a.begins_with("--out="):
					get_viewport().get_texture().get_image().save_png(a.trim_prefix("--out="))
	printerr("FACADE changed %d pixel-frames, %d of them flipped straight back (flicker)" % [changed, flips])
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			heat.save_png(a.trim_prefix("--out=").replace(".png", "_heat.png"))
	end_test()


func npc_near(id: String) -> void:
	# Sandra a step in front of someone outdoors, facing them
	var q: Dictionary = m.npcs.outdoor.get(id, {})
	if q.is_empty():
		printerr("NORTH  (no %s outdoors)" % id)
		return
	var p: Vector3 = q.holder.global_position
	place(p.x, p.z + 1.1, PI)
	m.player.global_position.y = m.ground_at(m.player.global_position)
	await get_tree().create_timer(0.3).timeout


func north_snap(dir: String, name: String) -> void:
	await get_tree().create_timer(0.6).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join(name + ".png"))


func room_thing(rid: String, clue: String) -> Dictionary:
	for th in m.D.interiors[rid].things:
		if th.get("clue", "") == clue or th.get("kind", "") == clue:
			return th
	return {}


func run_north(dir: String) -> void:
	# (round 23) the north end to end: the hill's slope rule, the path's barrier, Park Güell's gate and ticket, the
	# mystery of the Salamandreta, the cable car, the Giradabo, Biel's ball, the workmen's level and the path opening
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var g = m.game
	var N: Dictionary = m.D.north
	g.S.money = 3000
	g.S.missions["gift"] = {"st": "done", "num": 2}
	g.S.flags.partyOver = true
	m.set_clock(600.0)
	# 1. the slope: at the hill's foot, off the path, walking straight up it
	place(-150.0, -101.5, PI)
	await get_tree().create_timer(0.3).timeout
	var z0: float = m.player.global_position.z
	await hold(KEY_W, 2.5)
	printerr("NORTH slope: walked up from z %.1f to %.1f (ground %.1f m up): %s" % [z0, m.player.global_position.z,
		m.ground_at(m.player.global_position), "HELD BACK" if m.player.global_position.z > z0 - 6.0 else "CLIMBED (bad)"])
	await north_snap(dir, "01_slope")
	# ... and high on the hillside, off the path: she slides down
	place(-130.0, -150.0, 0.0)
	await get_tree().create_timer(0.2).timeout
	var h0 := m.ground_at(m.player.global_position)
	await get_tree().create_timer(2.0).timeout
	printerr("NORTH slide: from %.1f m to %.1f m up" % [h0, m.ground_at(m.player.global_position)])
	# 2. the workmen's barrier at the path's foot
	var w0: Array = N.workmen[0]
	place(w0[0] + 0.5, w0[1] + 6.0, PI)
	await get_tree().create_timer(0.3).timeout
	await hold(KEY_W, 3.0)
	var b: Array = N.barrier
	printerr("NORTH barrier: stopped at z %.1f (barrier %.1f..%.1f): %s" % [m.player.global_position.z, b[1], b[3],
		"STOPPED" if m.player.global_position.z > b[1] else "THROUGH (bad)"])
	await north_snap(dir, "02_barrier")
	# 3. Park Güell's gates (round 38, 06 #97): shut and solid without the ticket; bought, the main gate opens for her
	# and she walks in; out again, it shuts 6 s after she has gone; E opens it again (the ticket is a status, for good)
	var gt: Array = N.park.gate
	var pg0: Dictionary = m.north.gates[0]
	place(gt[0], gt[1] + 5.0, PI)
	await get_tree().create_timer(0.3).timeout
	await hold(KEY_W, 3.0)
	printerr("NORTH gate, no ticket: inside=%s shut=%s" % [m.north.park_inside(m.player.global_position), pg0.f == 0.0])
	await npc_near("jaume")
	g.talk_to("jaume")
	await talk_through([0])
	printerr("NORTH ticket bought=%s money=%d bag=%s" % [m.north.park_open(), g.S.money, g.S.inv.map(func(e): return e.id)])
	place(gt[0], gt[1] + 5.0, PI)
	await get_tree().create_timer(0.3).timeout
	await hold(KEY_W, 6.0)
	printerr("NORTH gate, with ticket: inside=%s at z %.1f" % [m.north.park_inside(m.player.global_position), m.player.global_position.z])
	place(gt[0], gt[1] + 8.0, 0.0)
	await get_tree().create_timer(12.0).timeout
	printerr("NORTH gate shut again after she left: %s (f %.2f)" % [pg0.f == 0.0, pg0.f])
	place(gt[0], gt[1] + 1.6, PI)
	await get_tree().create_timer(0.4).timeout
	printerr("NORTH gate: E offers %s" % m.nearest().get("label", "nothing"))
	m.input_key(KEY_E)
	await get_tree().create_timer(2.5).timeout
	await hold(KEY_W, 4.0)
	printerr("NORTH gate, opened with E: inside=%s at z %.1f" % [m.north.park_inside(m.player.global_position), m.player.global_position.z])
	await north_snap(dir, "03_park")
	# (round 26, the user fell through the square's sand by its wall) the park's terraces: she stands on the square's
	# sand right up to its walls, on the landings, the stairs, the porch and the plaza (scene 'flats')
	for spot in [["square east", 121.4, -185.0, 15.44], ["square west", 90.6, -190.0, 15.44], ["square back", 100.0, -197.4, 15.44],
			["landing east", 124.0, -184.0, 15.44], ["side stairs", 124.0, -175.0, 12.43], ["porch end", 92.0, -170.0, 9.03],
			["dragon stairs", 106.0, -158.0, 7.0], ["plaza", 97.0, -150.0, 6.03]]:
		place(spot[1], spot[2], 0.0)
		await get_tree().create_timer(0.3).timeout
		var gh: float = m.ground_at(m.player.global_position)
		printerr("NORTH terrace %s: ground %.2f (want %.2f) %s" % [spot[0], gh, spot[3], "OK" if absf(gh - spot[3]) < 0.12 else "OFF (bad)"])
	# ... and the wall: she runs right up to it (the user: "I should be able to run up to the edge of the barriers")
	place(186.0, -198.0, -PI / 2.0)
	await get_tree().create_timer(0.3).timeout
	await hold(KEY_W, 3.0)
	printerr("NORTH wall: stopped %.2f m from the wall's face (x %.2f): %s" % [m.player.global_position.x - 180.75, m.player.global_position.x,
		# (round 34: 0.8, was 0.7 — the park's ground is higher than the road behind the east wall now, and the ground's
		# 1.65 m height samples slope up to it just outside the wall's face; lowering it under the wall dug a gully
		# along the wall's inner foot)
		"CLOSE" if m.player.global_position.x - 180.75 < 0.8 else "HELD OFF (bad)"])
	# 4. the mystery: Mercè, the key on the path, the cellar door, the crate, back to Mercè
	await go_in(entrance("int_gaudi_house"))
	g.talk_to("merce")
	await talk_through()
	printerr("NORTH guell started=%s (active %s)" % [g.S.missions.has("guell"), g.m_active("guell")])
	await go_out()
	var key: Dictionary = {}
	for gr in g.ground:
		if gr.id == "cellar_key":
			key = gr
	if key.is_empty():
		printerr("NORTH key: none on the ground (bad)")
	else:
		printerr("NORTH key visible=%s" % key.node.visible)
		place(key.pos.x, key.pos.z + 0.6, PI)
		await get_tree().create_timer(0.4).timeout
		var near: Dictionary = m.nearest()
		printerr("NORTH key: E offers %s" % near.get("label", "nothing"))
		g.pick_up(key)
		await talk_through()
	printerr("NORTH has key=%s, cellar unlocked=%s" % [g.has_item("cellar_key"), g.unlocked("cellar_key")])
	# (round 27: Casa Trias is an outdoor house; the cellar's own low door, locked with the brass key)
	await go_in(entrance("int_trias_cellar"))             # (the soterrani door at the house's base)
	if m.where != "in":
		await go_in(entrance("int_trias_cellar"))
	printerr("NORTH cellar entered=%s" % (m.where == "in"))
	await north_snap(dir, "04_cellar")
	g.use_thing(room_thing("int_trias_cellar", "crate"))
	await talk_through()
	printerr("NORTH salamandreta=%s" % g.has_item("salamandreta"))
	await go_out()
	await go_in(entrance("int_gaudi_house"))
	g.talk_to("merce")
	await talk_through()
	printerr("NORTH guell done=%s pass=%s" % [g.m_done("guell"), g.has_item("park_pass")])
	await north_snap(dir, "05_plinth")
	await go_out()
	printerr("NORTH after: pereGone=%s, Jaume says: (below)" % g.S.flags.get("pereGone", false))
	# 5. the cable car up (the pass)
	var dl: Array = N.cable.door_low
	place(dl[0], dl[1] + 1.0, PI)
	await get_tree().create_timer(0.3).timeout
	m.north.act("cable_up")
	await talk_through([0])                             # (round 41: the turnstile asks first, then the screen fades)
	Engine.time_scale = 6.0
	var t0 := Time.get_ticks_msec()
	while m.north.ride.is_empty() and Time.get_ticks_msec() - t0 < 10000:
		await get_tree().process_frame
	await get_tree().create_timer(3.0).timeout
	await north_snap(dir, "06_cable")
	while not m.north.ride.is_empty() and Time.get_ticks_msec() - t0 < 60000:
		await get_tree().process_frame
	Engine.time_scale = 1.0
	printerr("NORTH cable: arrived at (%.1f, %.1f), %.1f m up, in %.1f s (x6)" % [m.player.global_position.x, m.player.global_position.z,
		m.ground_at(m.player.global_position), (Time.get_ticks_msec() - t0) / 1000.0])
	await north_snap(dir, "07_top")
	# 6. the Giradabo
	# (round 41: paid at the wheel's gate, E there, not by talking to Ramon)
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(0.5).timeout
	var money0: int = g.S.money
	m.north.act("wheel")
	await talk_through([0])
	Engine.time_scale = 6.0
	t0 = Time.get_ticks_msec()
	while m.north.ride.is_empty() and Time.get_ticks_msec() - t0 < 10000:
		await get_tree().process_frame
	await get_tree().create_timer(4.0).timeout
	await north_snap(dir, "08_wheel")
	while not m.north.ride.is_empty() and Time.get_ticks_msec() - t0 < 90000:
		await get_tree().process_frame
	Engine.time_scale = 1.0
	printerr("NORTH wheel: paid %d, off at (%.1f, %.1f) after %.1f s (x6)" % [money0 - g.S.money, m.player.global_position.x, m.player.global_position.z,
		(Time.get_ticks_msec() - t0) / 1000.0])
	# 7. Biel's ball: his mother asks, the ball on the ledge, back to Biel; the level to Toni; the path opens
	await npc_near("rosalia")
	g.talk_to("rosalia")
	await talk_through()
	printerr("NORTH ball started=%s" % g.m_active("ball"))
	var ball: Dictionary = {}
	for gr in g.ground:
		if gr.id == "ball":
			ball = gr
	if not ball.is_empty():
		place(ball.pos.x, ball.pos.z - 0.8, 0.0)          # (round 25: uphill of it; its tree is just below it)
		await get_tree().create_timer(0.4).timeout
		await north_snap(dir, "09_ledge")
		g.pick_up(ball)
		await talk_through()
	printerr("NORTH has ball=%s" % g.has_item("ball"))
	await npc_near("biel")
	g.talk_to("biel")
	await talk_through()
	printerr("NORTH ball done=%s, level=%s (mission %s)" % [g.m_done("ball"), g.has_item("spirit_level"), g.m_active("level")])
	await npc_near("toni")
	g.talk_to("toni")
	await talk_through()
	printerr("NORTH level given=%s" % g.S.flags.get("levelGiven", false))
	# (round 41, rule 10 #16d) the fade, the barriers pushed aside, his thanks — no going indoors
	await get_tree().create_timer(1.6).timeout
	printerr("NORTH after the fade: %s: %s" % [m.dlg_who.text, m.dlg_text.text.left(100)])
	await talk_through()
	printerr("NORTH path open=%s, level done=%s, barrier aside shown=%s" % [g.S.flags.get("pathOpen", false), g.m_done("level"),
		m.north.aside != null and m.north.aside.visible])
	await north_snap(dir, "09b_barrier_aside")
	g.talk_to("toni")
	await get_tree().process_frame
	await get_tree().process_frame
	printerr("NORTH Toni again: %s" % m.dlg_text.text.left(100))
	await talk_through()
	# up the path itself now (it sets off west-north-west from the foot)
	var pth: Array = N.path
	var dir2 := Vector2(pth[12][0] - pth[0][0], pth[12][1] - pth[0][1]).normalized()
	place(pth[0][0] - dir2.x * 3.0, pth[0][1] - dir2.y * 3.0, atan2(dir2.x, dir2.y))
	await get_tree().create_timer(0.3).timeout
	await hold(KEY_W, 3.0)
	var walked := Vector2(m.player.global_position.x - pth[0][0], m.player.global_position.z - pth[0][1]).dot(dir2)
	printerr("NORTH path after: %.1f m up the path past its foot (the barrier was there): %s" % [walked, "THROUGH" if walked > 3.0 else "STILL STOPPED (bad)"])
	await north_snap(dir, "10_path_open")
	end_test()


func run_flat(dir: String) -> void:
	# (round 23) Sandra's flat: what E offers in front of each piece of furniture (the user: looking at the bed picked the
	# bedside table, the table the bookshelf), the notebook on the bedside table; then the party in Alessandra's flat
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.new = false
	await go_in(entrance("int_sandra"))
	await talk_through()
	var O: Vector3 = m.room_base("int_sandra")
	# (spot to stand, facing): in front of the bed, the bedside table, the bookshelf, the wardrobe, the desk, the table
	for t in [["bed", Vector2(1.95, 3.6), PI], ["bedside table", Vector2(3.35, 2.6), PI], ["bookshelf", Vector2(4.45, 2.5), PI],
			["wardrobe", Vector2(8.65, 2.7), PI], ["desk", Vector2(2.7, 5.5), -PI / 2.0], ["round table", Vector2(6.5, 6.6), PI],
			["Rosa's bed", Vector2(12.05, 3.6), PI]]:
		m.player.global_position = O + Vector3(t[1].x, 0, t[1].y)
		m.model.rotation.y = t[2]
		m.move_dir = Vector2(sin(t[2]), cos(t[2]))
		await get_tree().create_timer(0.3).timeout
		printerr("FLAT at the %s: E offers \"%s\"" % [t[0], m.nearest().get("label", "nothing")])
	m.player.global_position = O + Vector3(3.35, 0, 2.6)
	await get_tree().create_timer(0.5).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("flat.png"))
	m.game.read_notebook()
	await get_tree().create_timer(0.8).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("notebook.png"))
	m.panels.close(false)
	await go_out()
	# the party
	m.game.S.missions["gift"] = {"st": "active", "num": 2}
	m.game.S.flags.partyOver = false
	await go_in(entrance("int_alessandra"))
	await talk_through()
	await get_tree().create_timer(1.0).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("party.png"))
	end_test()


func run_views(dir: String) -> void:
	# many pictures in one run (round 23): --viewfile=<json> {name: [from x, h, z, to x, h, z, (minutes), (player x, z)]}
	# in metres; a free camera, the HUD hidden, Sandra at the "to" point unless given
	DirAccess.make_dir_recursive_absolute(dir)
	var views: Dictionary = {}
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--viewfile="):
			views = JSON.parse_string(FileAccess.get_file_as_string(a.trim_prefix("--viewfile=")))
	await get_tree().create_timer(3.0).timeout
	swap_textures()
	if "--ballactive" in OS.get_cmdline_user_args():    # (round 25: Biel's ball lying in the wood, for its pictures)
		m.game.S.missions["ball"] = {"st": "active", "num": 99}
		m.game.S.taken.erase("ball")
		m.game.refresh_ground()
		for gr in m.game.ground:
			if gr.id == "ball":
				print("BALL node at %s visible=%s in tree=%s" % [gr.node.global_position, gr.node.visible, gr.node.is_inside_tree()])
	if "--brushactive" in OS.get_cmdline_user_args():   # (round 41: the painter's brush by the Cascada)
		m.game.S.missions["brush"] = {"st": "active", "num": 99}
		m.game.S.taken.erase("brush")
		m.game.refresh_ground()
		for gr in m.game.ground:
			if gr.id == "brush":
				print("BRUSH node at %s visible=%s" % [gr.node.global_position, gr.node.is_visible_in_tree()])
	if "--hatactive" in OS.get_cmdline_user_args():     # (round 41: Tomàs's cap lying at the wood's edge)
		m.game.S.missions["hat"] = {"st": "active", "num": 99}
		m.game.refresh_ground()
	if "--grailactive" in OS.get_cmdline_user_args():   # (round 41: the wildflowers on the hill, for their pictures)
		m.game.S.missions["grail"] = {"st": "active", "num": 99}
		m.game.refresh_ground()
	if "--guellactive" in OS.get_cmdline_user_args():   # (round 40: the cellar key lying in the park, for its pictures)
		m.game.S.missions["guell"] = {"st": "active", "num": 99}
		m.game.S.taken.erase("cellar_key")
		m.game.refresh_ground()
		for gr in m.game.ground:
			if gr.id == "cellar_key":
				print("KEY node at %s visible=%s" % [gr.node.global_position, gr.node.visible])
	for a in OS.get_cmdline_user_args():                # (round 41: the funicular's cars parked partway, --cablet=<0..1>)
		if a.begins_with("--cablet="):
			m.north.cable_t = float(a.trim_prefix("--cablet="))
			m.north.cable_wait = 999.0
			m.north.place_cabins()
	if "--hidetrees" in OS.get_cmdline_user_args():     # (round 33: to measure a house's front, the trees out of the way)
		for n in m.find_children("*", "MeshInstance3D", true, false):
			var nm := String(n.name)
			if nm.begins_with("Leaves") or nm.begins_with("Forest") or nm.begins_with("Plants") or nm.begins_with("Hill") \
					or nm.begins_with("Grass") or nm.contains("Trunk"):
				n.visible = false
	if "--maptrees" in OS.get_cmdline_user_args():      # (round 35: plan views — trees and plants out, the hill's railing kept)
		for n in m.find_children("*", "MeshInstance3D", true, false):
			var nm := String(n.name)
			if nm.begins_with("Leaves") or nm.begins_with("Forest") or nm.begins_with("Plants") or nm.begins_with("Grass_") \
					or nm.contains("Palms") or nm.contains("_plants") or nm.begins_with("PlanterLeaves") or nm.contains("Trunk"):
				n.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 60.0
	cc.far = 2000.0
	for vname in views:
		var v: Array = views[vname]
		var from := Vector3(v[0], v[1], v[2])
		var to := Vector3(v[3], v[4], v[5])
		if "--groundrel" in OS.get_cmdline_user_args():     # (round 34: heights as metres above the game's own ground)
			from.y += m.ground_at(from)
			to.y += m.ground_at(to)
		m.set_clock(float(v[6]) if v.size() > 6 else 600.0)
		var pp := Vector3(v[7], 0, v[8]) if v.size() > 8 else Vector3(to.x, 0, to.z)
		place(pp.x, pp.z, 0.0)                      # (her body stays at street level; the hill lifts only her model)
		# (round 26: a view from where she stands is her own eyes: her model would fill it)
		m.model.visible = Vector2(pp.x - from.x, pp.z - from.z).length() > 2.5
		cc.global_position = from
		if v.size() > 10 and float(v[10]) > 0.0:
			# (round 35: a plan — straight down, north at the top, v[10] metres from the picture's top to its bottom)
			cc.projection = Camera3D.PROJECTION_ORTHOGONAL
			cc.size = float(v[10])
			cc.rotation = Vector3(-PI / 2.0, 0.0, 0.0)
		else:
			cc.projection = Camera3D.PROJECTION_PERSPECTIVE
			cc.look_at(to, Vector3.UP)
		cc.fov = float(v[9]) if v.size() > 9 else 60.0          # (round 25: a telescope's narrow view)
		for i in 60:
			cc.current = true
			for c in m.get_children():
				if c is CanvasLayer:
					c.visible = false
			await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png(dir.path_join(vname + ".png"))
		print("VIEW %s fps=%d" % [vname, Engine.get_frames_per_second()])
	end_test()


func run_day(dir: String) -> void:
	# the light through the day, following the clock: from the beach, looking east and then west
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var only := []
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--times="):
			for v in a.trim_prefix("--times=").split(","):
				only.append(int(v))
	var times: Array = only if not only.is_empty() else [330, 375, 390, 405, 420, 480, 720, 1140, 1230, 1265, 1290, 1305, 1320, 1410]
	for mins in times:
		for v in [["east", PI / 2.0], ["west", -PI / 2.0], ["street", -PI / 2.0]]:
			m.set_clock(mins)
			if v[0] == "street":
				place(m.D.spawn.pos[0], m.D.spawn.pos[1], v[1])        # (in the city, the low sun down the street)
			else:
				place(10.0, 138.0, v[1])
			m.cam_pitch_node.rotation.x = 0.12
			m.last_manual_cam = m.t + 100.0
			await get_tree().create_timer(1.2).timeout
			printerr("%02d:%02d %s look=%s night=%s sun_e=%.2f" % [mins / 60, mins % 60, v[0], m.preset, m.P.night, m.sun.light_energy])
			get_viewport().get_texture().get_image().save_png(dir.path_join("day_%04d_%s.png" % [mins, v[0]]))
	end_test()


func run_accs(dir: String) -> void:
	# people with their hats, aprons, lanyards, glasses, bags, guitar, kite, rod and trolley, front and side
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("golden")
	var at := Vector3(m.D.spawn.pos[0], 0.0, m.D.spawn.pos[1] - 6.0)
	place(at.x - 40.0, at.z, 0.0)
	var ids := ["bofarull", "sergi", "pau", "pere", "vicenc", "dolors", "quima", "ferran", "empar", "merce", "maria", "oscar", "silvia", "albert", "tomas"]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--ids="):                     # (round 37: a lineup of chosen people, e.g. the workmen)
			ids = Array(a.substr(6).split(","))
	for j in ids.size():
		var id: String = ids[j]
		var p := at + Vector3(j * 1.15 - ids.size() * 0.575, 0, 0)
		p.y = m.ground_at(p)
		var q: Dictionary = m.npcs.make_person(id, m.game.data.NPCS[id], m.outdoor, p)
		if not q.is_empty():
			q.holder.rotation.y = 0.0
			if "--profile" in OS.get_cmdline_user_args():   # (round 41: side-on, to see where their arms hang)
				q.holder.rotation.y = -PI / 2.0
			if "--bodyoff" in OS.get_cmdline_user_args():  # (round 41: as the Meshy idle stands them, for a before picture)
				q.m.posture.arms_w = 0.0
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 50.0
	cc.current = true
	var views := [["front", Vector3(0, 1.4, 11.0), Vector3(0, 0.9, 0)], ["side", Vector3(-12.0, 2.2, 6.0), Vector3(0, 1.4, 0)],
			["close", Vector3(-6.0, 1.3, 3.2), Vector3(-6.0, 1.1, 0)]]
	if ids.size() <= 6:
		# (round 37) a small lineup: the camera close in front of them, at full sharpness, and one beside each pair
		var w := ids.size() * 1.15
		views = [["front", Vector3(0, 1.1, w * 0.95 + 1.2), Vector3(0, 0.85, 0)]]
	for v in views:
		cc.global_position = at + v[1]
		cc.look_at(at + v[2], Vector3.UP)
		await get_tree().create_timer(1.2).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("accs_%s.png" % v[0]))
	end_test()


func run_frontend(dir: String) -> void:
	# the title screen, the pause menu, and the bike rules (locked bikes; B once Jordi has given her one)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.new = false
	m.title_screen()
	await get_tree().create_timer(0.6).timeout
	await shot(dir, "f1_title")
	m.dialog_next()                                         # Continue
	await get_tree().create_timer(0.3).timeout
	m.pause_menu()
	await get_tree().create_timer(0.3).timeout
	await shot(dir, "f2_pause")
	m.dlg_choice = 0
	m.dialog_next()
	await get_tree().create_timer(0.3).timeout
	# bikes: a parked one is someone else's
	var bk: Node3D = m.street.bikes[0]
	place(bk.position.x + 1.0, bk.position.z, -PI / 2.0)
	await get_tree().create_timer(0.3).timeout
	var n: Dictionary = m.nearest()
	printerr("near a parked bike: ", n.get("label", "nothing"))
	m.interact()
	await get_tree().create_timer(0.2).timeout
	printerr("  says: ", m.dlg_text.text.left(70))
	while m.dlg_open:
		m.dialog_next()
		await get_tree().create_timer(0.05).timeout
	m.game.S.has_bike = false
	m.bike_key()
	printerr("B without a bike: riding=", m.street.riding != null, " toast=", m.toasts.back()[0] if not m.toasts.is_empty() else "")
	m.game.S.has_bike = true
	var mp: Vector3 = m.npcs.outdoor.montse.holder.global_position
	place(mp.x + 3.0, mp.z + 6.0, PI)
	await get_tree().create_timer(0.3).timeout
	m.bike_key()
	await get_tree().create_timer(0.3).timeout
	printerr("B with her bike: riding=", m.street.riding != null)
	await hold(KEY_W, 2.0)
	printerr("  rode %.1f m" % m.player.global_position.distance_to(Vector3(mp.x + 3.0, 0, mp.z + 6.0)))
	await shot(dir, "f3_riding")
	m.bike_key()
	await get_tree().create_timer(0.3).timeout
	printerr("B again: riding=", m.street.riding != null)
	var sp: Array = m.D.spawn.pos
	place(sp[0], sp[1], PI)
	m.bike_key()
	printerr("B on the sand: riding=", m.street.riding != null, " toast=", m.toasts.back()[0])
	end_test()


func run_wear(dir: String) -> void:
	# Sandra in each of the 2D game's clothes, from the front
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("golden")
	var g := m.game
	for id in ["sundress", "sailor", "jersey", "festshirt", "barretina"]:
		g.add_item(id)
	var mp: Vector3 = m.npcs.outdoor.montse.holder.global_position
	place(mp.x + 3.0, mp.z + 6.0, 0.0, PI)
	m.model.rotation.y = 0.0
	m.cam_yaw_node.rotation.y = 0.0                          # in front of her, looking back at her
	m.arm.spring_length = 3.0
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	for set in [["none"], ["sundress"], ["sailor", "barretina"], ["jersey"], ["festshirt", "barretina"]]:
		g.S.worn.outfit = null
		g.S.worn.hat = null
		for id in set:
			if id != "none":
				g.wear_item(id)
		m.dress_sandra()
		await get_tree().process_frame
		for sk in m.skins:
			printerr(set, " ", sk.file, " hats=", sk.root.find_children("*", "BoneAttachment3D", true, false).filter(func(b): return b.has_meta("accessory")).size())
		m.last_manual_cam = m.t + 100.0
		await get_tree().create_timer(1.0).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("wear_%s.png" % "_".join(set)))
	end_test()


func run_wild(dir: String) -> void:
	# the Rambla's pigeons (and Sandra walking into them), a butterfly by day, fireflies at night, the gulls
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("golden")
	var wl = m.wildlife
	var p0: Vector3 = wl.pigeons[2].pos
	place(p0.x, p0.z + 5.0, PI)
	m.arm.spring_length = 3.0
	m.cam_pitch_node.rotation.x = -0.3
	await get_tree().create_timer(0.8).timeout
	await shot(dir, "w1_pigeons")
	await hold(KEY_W, 1.2)
	printerr("pigeons flying: ", wl.pigeons.filter(func(p): return p.st != "ground").size())
	await shot(dir, "w2_flutter")
	await get_tree().create_timer(6.0).timeout
	printerr("after: on the ground ", wl.pigeons.filter(func(p): return p.st == "ground").size(), " landing ", wl.pigeons.filter(func(p): return p.st == "land").size())
	var b: Dictionary = wl.bflies[5]
	var bp: Vector3 = b.node.position
	place(bp.x, bp.z + 2.5, PI)
	m.arm.spring_length = 2.0
	await shot(dir, "w3_butterfly")
	m.apply_preset("night")
	await shot(dir, "w4_fireflies")
	m.apply_preset("day")
	var g: Dictionary = wl.gulls[2]
	place(g.c.x, g.c.z - 8.0, 0.0)
	m.cam_pitch_node.rotation.x = 0.25
	await shot(dir, "w5_gulls")
	end_test()


func run_bag(dir: String) -> void:
	# the backpack and a shop counter, as in the 2D game: pictures, names, counts, worn, the detail box;
	# then using things from it (eat, wear, read) and buying, checking each did what it should
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var g = m.game
	g.S.money = 3000
	for id in ["apple", "croissant", "camera", "sundress", "bk_gaudi", "note1", "bottle", "bottle", "bottle", "bread"]:
		g.add_item(id)
	await get_tree().process_frame
	m.input_key(KEY_I)
	await get_tree().create_timer(0.5).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("bag_1.png"))
	printerr("bag open=%s slots=%d" % [m.panels.is_open(), g.S.inv.size()])
	for k in [KEY_RIGHT, KEY_RIGHT, KEY_RIGHT]:
		m.input_key(k)
	await get_tree().create_timer(0.3).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("bag_2_shades.png"))
	m.input_key(KEY_W)
	await get_tree().create_timer(0.3).timeout
	printerr("wear: worn=%s" % [g.S.worn])
	get_viewport().get_texture().get_image().save_png(dir.path_join("bag_3_worn.png"))
	m.input_key(KEY_LEFT)
	m.input_key(KEY_LEFT)
	m.input_key(KEY_LEFT)
	var n0: int = g.S.inv.size()
	m.input_key(KEY_E)
	await get_tree().create_timer(0.3).timeout
	printerr("eat apple: panel=%s dialog=%s text=%s" % [m.panels.is_open(), m.dlg_open, m.dlg_text.text.left(60)])
	while m.dlg_open and not m.panels.is_open():
		m.dialog_next()
		await get_tree().create_timer(0.2).timeout
	printerr("after eating: back in bag=%s items %d -> %d" % [m.panels.is_open(), n0, g.S.inv.size()])
	m.input_key(KEY_ESCAPE)
	await get_tree().create_timer(0.3).timeout
	printerr("closed=%s dlg_open=%s" % [not m.panels.is_open(), m.dlg_open])
	g.open_shop("int_torro_joan")
	await get_tree().create_timer(0.5).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("shop_1.png"))
	var before: int = g.S.money
	m.input_key(KEY_ENTER)
	await get_tree().create_timer(0.4).timeout
	printerr("bought: money %d -> %d, still open=%s" % [before, g.S.money, m.panels.is_open()])
	get_viewport().get_texture().get_image().save_png(dir.path_join("shop_2.png"))
	m.input_key(KEY_ESCAPE)
	await get_tree().create_timer(0.3).timeout
	printerr("shop closed=%s" % [not m.panels.is_open()])
	end_test()


func run_church(dir: String) -> void:
	# into the Sagrada Família by the Nativity door, morning and evening: looking along the nave, up into
	# the vaults, across to the rose window; then out again by the Passion door
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var e: Dictionary = {}
	for d in m.D.entrances:
		if d.get("int", "") == "int_sagrada" and d.get("room_side", "bottom") == "bottom":
			e = d
	await go_in(e)
	printerr("in: where=%s room=%s free_cam=%s" % [m.where, m.room, m.free_cam()])
	var O0: Vector3 = m.room_base("int_sagrada")
	place(O0.x + 22.0, O0.z + 16.5, PI)
	await get_tree().create_timer(0.5).timeout
	for mins in [570, 1050]:
		m.set_clock(mins)
		for v in [["nave", -PI / 2.0, 0.25], ["up", -PI / 2.0, 0.8], ["apse", PI / 2.0, 0.3], ["rose", PI, 0.45], ["crossing", 0.0, 0.7]]:
			m.cam_yaw_node.rotation.y = v[1]
			m.cam_pitch_node.rotation.x = v[2]
			m.last_manual_cam = m.t
			await get_tree().create_timer(0.8).timeout
			get_viewport().get_texture().get_image().save_png(dir.path_join("church_%d_%s.png" % [mins, v[0]]))
	# out through the Passion door (the top of the room)
	var R: Dictionary = m.D.interiors["int_sagrada"]
	var O: Vector3 = m.room_base("int_sagrada")
	place(O.x + (R.exit_top[0] + R.exit_top[1]) / 2.0, O.z + 2.5, PI)
	m.vkeys[KEY_W] = true
	m.cam_yaw_node.rotation.y = 0.0
	for i in 8:
		await get_tree().create_timer(0.3).timeout
		printerr("  walking: lp=%s dir=%s yaw=%.2f where=%s" % [m.local_pos(), m.move_dir, m.cam_yaw_node.rotation.y, m.where])
	m.vkeys.erase(KEY_W)
	await get_tree().create_timer(1.5).timeout
	printerr("out by the Passion door: where=%s at %s (door %s)" % [m.where, m.player.global_position, m.room_door.get("pos")])
	end_test()


func run_flickermeter() -> void:
	# (round 26, the user: the dappled light flickers, and Sandra's shadow) Sandra stands still at four spots (two deep
	# in the woods, the hill path, a street) with the game's own camera; for 3 s, frame by frame, how many pixels change
	# (the panels hidden). Nothing moves but the sun, the wind and her idling, so this is the flicker. Options:
	# --shadowmotion=<0..1> (the leaves' sway in their shadows; 1 = as before round 26), --sunevery=<frames>.
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--flutter="):
			for key in m.foliage_mats:
				(m.foliage_mats[key] as ShaderMaterial).set_shader_parameter("flutter_amp", float(a.trim_prefix("--flutter=")))
		if a == "--noropeshadow":
			for nd in m.outdoor.find_children("HillRail*", "GeometryInstance3D", true, false):
				(nd as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if a.begins_with("--shadowmotion="):
			for key in m.foliage_mats:
				(m.foliage_mats[key] as ShaderMaterial).set_shader_parameter("shadow_motion", float(a.trim_prefix("--shadowmotion=")))
	var spots := [["hill_deep", Vector2(-130.0, -170.0), -PI / 2.0], ["wood_a", Vector2(164.0, 12.0), PI / 2.0],
		["hill_path", Vector2(-133.6, -223.0), 0.3], ["street", Vector2(-4.0, 33.0), 0.0]]
	var total := 0.0
	if "--long" in OS.get_cmdline_user_args():
		spots = [spots[1], spots[1], spots[1], spots[0], spots[0], spots[0]]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--spot="):
			spots = spots.filter(func(q): return q[0] == a.trim_prefix("--spot="))
	for v in spots:
		place(v[1].x, v[1].y, v[2])
		m.cam_yaw_node.rotation.y = v[2] + PI
		m.cam_pitch_node.rotation.x = -0.9 if "--floor" in OS.get_cmdline_user_args() else (0.6 if "--canopy" in OS.get_cmdline_user_args() else -0.2)
		m.model.visible = not "--floor" in OS.get_cmdline_user_args()
		m.last_manual_cam = m.t
		await get_tree().create_timer(2.0).timeout
		var prev: Image = null
		var acc := 0.0
		var frames := 0
		var per := []
		var scales := {}
		var heat := Image.create(160, 100, false, Image.FORMAT_RGB8)
		var cam_prev := Vector3.ZERO
		var cam_jumps := 0
		var cam_max := 0.0
		var first: Image = null
		var t0 := Time.get_ticks_usec()
		while Time.get_ticks_usec() - t0 < 3000000:
			await get_tree().process_frame
			var img := get_viewport().get_texture().get_image()
			img.resize(320, 200, Image.INTERPOLATE_BILINEAR)
			if prev:
				var n := 0
				for y in range(0, 200, 2):
					for x in range(0, 320, 2):
						if absf(img.get_pixel(x, y).get_luminance() - prev.get_pixel(x, y).get_luminance()) > 0.03:
							n += 1
							var hc := heat.get_pixel(x / 2, y / 2)
							heat.set_pixel(x / 2, y / 2, Color(minf(1.0, hc.r + 0.1), 0, 0))
				acc += n / 16000.0 * 100.0
				per.append(n / 16000.0 * 100.0)
				frames += 1
			scales[snappedf(get_viewport().scaling_3d_scale, 0.01)] = true
			var cp := get_viewport().get_camera_3d().global_position
			if cam_prev != Vector3.ZERO:
				var dd := cp.distance_to(cam_prev)
				cam_max = maxf(cam_max, dd)
				if dd > 0.01:
					cam_jumps += 1
			cam_prev = cp
			if first == null:
				first = img
			prev = img
		for a in OS.get_cmdline_user_args():
			if a.begins_with("--heat="):
				heat.save_png(a.trim_prefix("--heat=") + "_%s_heat.png" % v[0])
				first.save_png(a.trim_prefix("--heat=") + "_%s.png" % v[0])
		per.sort()
		var med: float = per[per.size() / 2] if per.size() else 0.0
		var pops := per.filter(func(q): return q > maxf(3.0 * med, 1.0)).size()
		print("FLICKER %-10s %.2f%% of the picture changes per frame (%d frames), %d pops, render scales %s, camera moved in %d frames (most %.3f m)" % [v[0], acc / maxf(1, frames),
			frames, pops, scales.keys(), cam_jumps, cam_max])
		total += acc / maxf(1, frames)
	print("FLICKER mean %.2f%%" % (total / spots.size()))
	end_test()


func run_roompic(arg: String) -> void:
	# (round 26) pictures inside one room, straight in by the debug route (no walking): --roompic=<rid>:<dir>[:<viewfile>]
	# The views: a JSON list of [name, x, y, yaw, pitch] in the room's own metres (yaw 0 looks to the back wall, PI to
	# the door wall, PI/2 east); without a file, four stock views.
	var parts := arg.split(":")
	var rid := parts[0]
	var dir := parts[1]
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(840)
	var R: Dictionary = m.D.interiors[rid]
	var views := [["in", R.w / 2.0, R.h - 1.5, 0.0, 0.2], ["back", R.w / 2.0, 3.0, PI, 0.2], ["east", 2.5, R.h / 2.0, PI / 2.0, 0.15],
		["west", R.w - 2.5, R.h / 2.0, -PI / 2.0, 0.15], ["up", R.w / 2.0, R.h / 2.0, 0.0, 1.1]]
	if parts.size() > 2:
		views = JSON.parse_string(FileAccess.get_file_as_string(parts[2]))
	var e: Dictionary = entrance(rid)
	await go_in(e)
	await get_tree().create_timer(1.0).timeout
	var O: Vector3 = m.room_base(rid)
	m.model.visible = false                            # (the room, not the back of her head)
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	for v in views:
		place(O.x + v[1], O.z + v[2], v[3] + PI)
		m.cam_yaw_node.rotation.y = v[3]
		m.cam_pitch_node.rotation.x = v[4]
		m.last_manual_cam = m.t
		await get_tree().create_timer(1.0).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("%s_%s.png" % [rid, v[0]]))
	printerr("ROOMPIC %s: %d pictures" % [rid, views.size()])
	get_tree().quit()


func run_pathgrid() -> void:
	# (round 35) can a player walk the whole hill path? The play-through's own map of where she fits (and where the
	# slope lets her), checked along the path's points from the funfair down: each point's cell, and whether it joins
	# the top. Prints the first places it breaks.
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["pathOpen"] = true
	m.north.refresh()
	var pt := Node.new()
	pt.set_script(load(m.world_res("tests/playthrough.gd")))
	add_child(pt)
	pt.tst = self
	pt.m = m
	pt.g = m.game
	await pt.build_grids()
	for d in pt.dyn:
		for c in d[1]:
			pt.grid.set_point_solid(c, (d[0] as StaticBody3D).collision_layer != 0)
	var P: Array = m.D.north.path
	var top: Vector2i = pt.free_near(pt.grid, pt.cell_of(Vector2(P[-1][0], P[-1][1])))
	var bad := 0
	var i := P.size() - 1
	while i >= 0:
		var c: Vector2i = pt.cell_of(Vector2(P[i][0], P[i][1]))
		var solid: bool = pt.grid.is_point_solid(c)
		var joined: bool = not solid and not pt.grid.get_id_path(top, c).is_empty()
		if not joined:
			bad += 1
			if bad <= 12:
				var near := []
				for dz in range(-3, 4):
					var row := ""
					for dx in range(-3, 4):
						row += "#" if pt.grid.is_point_solid(c + Vector2i(dx, dz)) else "."
					near.append(row)
				print("PATHGRID breaks at path point %d (%.1f, %.1f, h %.1f): %s; round it %s" % [i, P[i][0], P[i][1], P[i][2],
					"no room to stand" if solid else "not joined to the top", " / ".join(near)])
		i -= 4
	print("PATHGRID %d of %d checked points not joined to the funfair" % [bad, (P.size() + 3) / 4])
	end_test()


func run_storybits() -> void:
	# (round 35, the user's checks, kept as a test) the policeman goes back to his post when Sandra leaves La Rambla and
	# comes with her again when she speaks to him there; no dog on the funicular (before the dog mission is done she
	# can't ride with Trufa; after, Trufa goes home); and every decoration of the rooms lies inside its own room
	await get_tree().create_timer(3.0).timeout
	var ok := true
	var g = m.game
	var oq: Dictionary = m.npcs.outdoor.get("bofarull", {})
	g.S.missions["thief"] = {"st": "active", "num": 13}
	m.npcs.set_mode("bofarull", "follow")
	var home: Vector3 = oq.home
	place(home.x + 2.0, home.z + 3.0, 0.0)
	await get_tree().create_timer(1.0).timeout
	place(-12.0, 14.0, 0.0)                                  # (Carrer de València, off La Rambla)
	await get_tree().create_timer(5.0).timeout
	var mode1: String = oq.get("mode", "")
	print("STORY policeman, she off La Rambla 5 s: %s (want back or waiting)" % mode1)
	ok = ok and mode1 in ["back", "waiting"]
	var off_beat: float = Vector2(oq.holder.position.x - home.x, oq.holder.position.z - home.z).length()
	print("STORY he stayed on La Rambla: %.1f m from his post when he turned back (want under 12)" % off_beat)
	ok = ok and off_beat < 12.0
	for i in 40:
		await get_tree().create_timer(0.5).timeout
		if String(oq.get("mode", "")) == "waiting":
			break
	var at_home: float = Vector2(oq.holder.position.x - home.x, oq.holder.position.z - home.z).length()
	print("STORY policeman back at his post: %s, %.1f m off it" % [oq.get("mode", ""), at_home])
	ok = ok and at_home < 1.0
	place(home.x + 1.2, home.z + 0.4, -PI / 2.0)
	await get_tree().create_timer(0.6).timeout
	g.talk_to("bofarull")
	for i in 20:
		await get_tree().create_timer(0.3).timeout
		if m.dlg_open:
			m.input_key(KEY_E)
	await get_tree().create_timer(1.0).timeout
	print("STORY spoken to on La Rambla: %s (want follow)" % oq.get("mode", ""))
	ok = ok and String(oq.get("mode", "")) == "follow"
	# the dog and the funicular
	g.S.missions.erase("thief")
	m.npcs.set_mode("bofarull", "")
	g.S["inv"].append({"id": "park_pass", "n": 1})
	var dl: Array = m.D.north.cable.door_low
	var tr = m.street.trufa
	g.S.missions["dog"] = {"st": "active", "num": 3}
	tr.follow()
	place(dl[0], dl[1] + 1.0, PI)
	m.north.act("cable_up")
	await get_tree().create_timer(0.5).timeout
	var refused: bool = m.north.ride.is_empty()
	print("STORY funicular with Trufa, dog mission under way: %s" % ("refused (want)" if refused else "RODE"))
	ok = ok and refused
	while m.dlg_open:
		m.input_key(KEY_E)
		await get_tree().create_timer(0.2).timeout
	g.S.missions["dog"] = {"st": "done", "num": 3}
	tr.follow()
	m.north.act("cable_up")
	await get_tree().create_timer(0.5).timeout
	# (round 41: since round 40 the turnstile asks "Ride up?" first; answer it as a player would)
	for i in 12:
		if not m.dlg_open:
			break
		if m.choice_box.visible:
			m.dlg_choice = 0
		m.dialog_next()
		await get_tree().create_timer(0.3).timeout
	print("STORY funicular with Trufa, dog mission done: rides %s, Trufa %s (want true, going home)" % [not m.north.ride.is_empty(),
		"going home" if tr.state == tr.GOING_HOME else str(tr.state)])
	ok = ok and not m.north.ride.is_empty() and tr.state == tr.GOING_HOME
	while m.dlg_open:
		m.input_key(KEY_E)
		await get_tree().create_timer(0.2).timeout
	# the rooms' decorations, each inside its room (round 35: four of them had lain 400 m off, never seen)
	var T: Node = m.touches
	for pair in [["int_alessandra", T.party], ["int_alba", T.vase_flowers], ["int_gaudi_house", T.salamandreta]]:
		var rid: String = pair[0]
		var n: Node3D = pair[1]
		if n == null:
			continue
		var R: Dictionary = m.D.interiors[rid]
		var c := Vector3.ZERO
		var cnt := 0
		for mi in n.find_children("*", "MeshInstance3D", true, false) + ([n] if n is MeshInstance3D else []):
			c += (mi as Node3D).global_position
			cnt += 1
		if cnt == 0:
			c = n.global_position
		else:
			c /= cnt
		var lp: Vector3 = c - m.room_base(rid)
		var inside: bool = lp.x > 0.0 and lp.x < R.w and lp.z > 0.0 and lp.z < R.h and lp.y > 0.0 and lp.y < 3.0
		print("STORY %s's decoration at (%.1f, %.1f, %.1f) in the room: %s" % [rid, lp.x, lp.y, lp.z, inside])
		ok = ok and inside
	print("STORY %s" % ("ALL OK" if ok else "SOMETHING WRONG"))
	end_test()


func swap_textures() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--swaptex="):
			# (round 35: a look to choose, without a build) --swaptex=<material name part>:<png>: every material whose
			# name has that in it draws that picture instead
			var sw := a.trim_prefix("--swaptex=").split(":")
			var tex := ImageTexture.create_from_image(Image.load_from_file(sw[1]))
			var nsw := 0
			for mi in m.outdoor.find_children("*", "MeshInstance3D", true, false):
				var mesh: Mesh = (mi as MeshInstance3D).mesh
				if mesh == null:
					continue
				for si in mesh.get_surface_count():
					var mt := mesh.surface_get_material(si)
					if mt is BaseMaterial3D and String(mt.resource_name).contains(sw[0]):
						(mt as BaseMaterial3D).albedo_texture = tex
						nsw += 1
			print("SWAPTEX %s: %d surfaces" % [sw[0], nsw])


func run_hilltour(dir: String) -> void:
	# (round 35, the user: "There is a big hill in the path down the mountain … The path up the hill also stops and
	# starts … It looks like squares. At one point the path and fence go down the hill … take pictures of the entire hill
	# path") the hill path from its foot to the funfair: every 15 m a picture as Sandra sees it, up the path and down it;
	# and every metre the game's own ground against the path's even climb, on its line and 0.9 m to each side —
	# index.txt lists where they part by more than 0.25 m (a hump, a dip, a step)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.flags["pathOpen"] = true
	m.north.refresh()
	swap_textures()
	var P: Array = m.D.north.path
	var idx := FileAccess.open(dir.path_join("index.txt"), FileAccess.WRITE)
	var along := 0.0
	var worst := 0.0
	for i in P.size():
		if i > 0:
			along += Vector2(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]).length()
		var j := mini(i + 1, P.size() - 1)
		var k := maxi(i - 1, 0)
		var d := Vector2(P[j][0] - P[k][0], P[j][1] - P[k][1]).normalized()
		var side := Vector2(-d.y, d.x)
		var notes := []
		for o in [-0.9, 0.0, 0.9]:
			var q: Vector2 = Vector2(P[i][0], P[i][1]) + side * float(o)
			var gh: float = m.terrain_at(q.x, q.y)
			var diff: float = gh - float(P[i][2])
			if absf(diff) > 0.25:
				notes.append("%s %+.2f" % ["left" if o < 0 else ("right" if o > 0 else "middle"), diff])
			worst = maxf(worst, absf(diff))
		if not notes.is_empty():
			idx.store_line("ground\t%.0f m\t%.1f,%.1f\t%s" % [along, P[i][0], P[i][1], ", ".join(notes)])
	idx.store_line("ground: the worst parting %.2f m along %.0f m of path" % [worst, along])
	var n := 0
	var next_at := 0.0
	along = 0.0
	for i in P.size():
		if i > 0:
			along += Vector2(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]).length()
		if along < next_at:
			continue
		next_at += 15.0
		var j := mini(i + 2, P.size() - 1)
		var k := maxi(i - 2, 0)
		var d := Vector2(P[j][0] - P[k][0], P[j][1] - P[k][1]).normalized()
		for up in [true, false]:
			var hd := atan2(d.x, d.y) if up else atan2(-d.x, -d.y)
			place(P[i][0], P[i][1], hd)
			m.model.position.y = m.ground_at(m.player.global_position)
			m.snap_height()
			n += 1
			await shot(dir, "%03d_%s" % [n, "up" if up else "down"])
			idx.store_line("%03d\t%.0f m\t%.1f,%.1f\t%s" % [n, along, P[i][0], P[i][1], "looking up the path" if up else "looking down"])
	idx.close()
	print("HILLTOUR %d pictures, %.0f m of path, the ground parts from it by %.2f m at worst" % [n, along, worst])
	end_test()


func run_closeup(arg: String) -> void:
	# (round 35) a close look at one thing in a room, from a camera of its own: --closeup=<rid>:<x>:<z>:<h>:<file>[:<flag>]
	# looks at room point (x, z) at height h from four sides 0.9 m off (or [:<dist>]) and a little above; <flag> set first
	# (vaseFull; m=gift: that mission under way)
	var p := arg.split(":")
	var rid := p[0]
	var at := Vector3(float(p[1]), float(p[3]), float(p[2]))
	if p.size() > 5:
		if p[5].begins_with("m="):
			m.game.S.missions[p[5].trim_prefix("m=")] = {"st": "active", "num": 2}      # (a mission under way: m=gift)
		else:
			m.game.S.flags[p[5]] = true
	await get_tree().create_timer(3.0).timeout
	m.set_clock(840)
	m.touches.refresh()
	await go_in(entrance(rid))
	await get_tree().create_timer(1.0).timeout
	var O: Vector3 = m.room_base(rid)
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cam := Camera3D.new()
	cam.fov = 40.0
	m.indoor.add_child(cam)
	var shots := []
	for k in 4:
		var a := PI + k * PI / 2.0
		var dist := float(p[6]) if p.size() > 6 else 0.9
		cam.global_position = O + at + Vector3(sin(a) * dist, 0.35 * dist / 0.9, cos(a) * dist)
		cam.look_at(O + at, Vector3.UP)
		cam.current = true
		await get_tree().create_timer(0.6).timeout
		await RenderingServer.frame_post_draw
		shots.append(get_viewport().get_texture().get_image())
	var w: int = shots[0].get_width() / 2
	var h: int = shots[0].get_height() / 2
	var sheet := Image.create(w * 2, h * 2, false, shots[0].get_format())
	for k in 4:
		shots[k].save_png(p[4].get_basename() + "_%d.png" % k)     # (round 41: each full size too, to send one by one)
		shots[k].resize(w, h)
		sheet.blit_rect(shots[k], Rect2i(0, 0, w, h), Vector2i((k % 2) * w, (k / 2) * h))
	sheet.save_png(p[4])
	printerr("CLOSEUP %s saved (party shown %s, at %s)" % [p[4], m.touches.party.visible if m.touches.party else "-",
		m.touches.party.get_child(m.touches.party.get_child_count() - 1).global_position if m.touches.party else "-"])
	get_tree().quit()


func run_sagratcor(dir: String) -> void:
	# (round 26) the Sagrat Cor's two churches, each by its own door: walked into from outside (the crypt from the
	# funfair, the upper church from the terrace), pictures inside, walked out again
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660)
	var views := {
		"int_sagrat_cor": [["aisle", 12.0, 14.5, 0.0, 0.2], ["vault", 12.0, 12.0, 0.0, 0.75], ["candles", 6.5, 12.0, -1.96, 0.25],
			["across", 3.0, 8.5, PI / 2.0, 0.2], ["altar", 12.0, 6.0, 0.0, 0.1]],
		"int_sagrat_alta": [["nave", 10.0, 18.5, 0.0, 0.25], ["dome", 10.0, 11.5, 0.0, 1.05], ["east", 13.0, 12.5, PI / 2.0, 0.3],
			["west", 7.0, 12.5, -PI / 2.0, 0.3], ["rose", 10.0, 7.0, PI, 0.45], ["altar", 10.0, 4.5, 0.0, 0.3]]}
	for rid in ["int_sagrat_cor", "int_sagrat_alta"]:
		var e: Dictionary = entrance(rid)
		var n := Vector2(e.normal[0], e.normal[1])
		# walk up to the door from 2.5 m out
		place(e.pos[0] + n.x * 2.5, e.pos[1] + n.y * 2.5, atan2(-n.x, -n.y))
		m.cam_yaw_node.rotation.y = atan2(-n.x, -n.y) + PI
		await get_tree().create_timer(0.3).timeout
		m.vkeys[KEY_W] = true
		for i in 20:
			await get_tree().create_timer(0.2).timeout
			if m.where == "in":
				break
		m.vkeys.clear()
		await get_tree().create_timer(1.2).timeout
		printerr("SAGRATCOR walked in at %s: where=%s room=%s" % [e.id, m.where, m.room])
		if m.room != rid:
			continue
		var O: Vector3 = m.room_base(rid)
		for v in views[rid]:
			place(O.x + v[1], O.z + v[2], v[3] + PI)        # (facing the way the camera looks, from behind her)
			m.cam_yaw_node.rotation.y = v[3]
			m.cam_pitch_node.rotation.x = v[4]
			m.last_manual_cam = m.t
			await get_tree().create_timer(1.0).timeout
			get_viewport().get_texture().get_image().save_png(dir.path_join("%s_%s.png" % [rid, v[0]]))
		var R: Dictionary = m.D.interiors[rid]
		place(O.x + (R.exit[0] + R.exit[1]) / 2.0, O.z + R.h - 1.0, 0.0)
		m.cam_yaw_node.rotation.y = PI
		await get_tree().create_timer(0.3).timeout
		m.vkeys[KEY_W] = true
		await get_tree().create_timer(1.5).timeout
		m.vkeys.clear()
		await get_tree().create_timer(1.5).timeout
		printerr("SAGRATCOR out of %s: where=%s, %.1f m from its door" % [rid, m.where,
			Vector2(m.player.global_position.x - e.pos[0], m.player.global_position.z - e.pos[1]).length()])
	end_test()


func run_stairs() -> void:
	# the university: walk up the grand stair to the library, then back down the stairwell
	await get_tree().create_timer(3.0).timeout
	var e: Dictionary = {}
	for d in m.D.entrances:
		if d.get("int", "") == "int_upf":
			e = d
	await go_in(e)
	var R: Dictionary = m.D.interiors["int_upf"]
	var O: Vector3 = m.room_base("int_upf")
	var st: Dictionary = R.stairs[0]
	place(O.x + st.arrive[0], O.z + st.arrive[1] + 0.5, PI)
	m.vkeys[KEY_W] = true
	await get_tree().create_timer(2.5).timeout
	m.vkeys.erase(KEY_W)
	await get_tree().create_timer(1.2).timeout
	printerr("walked up: room=%s" % m.room)
	m.vkeys[KEY_S] = true
	await get_tree().create_timer(2.5).timeout
	m.vkeys.erase(KEY_S)
	await get_tree().create_timer(1.2).timeout
	printerr("walked down: room=%s" % m.room)
	end_test()


func run_stuck(which: String) -> void:
	# looks for pockets Sandra can walk into but not out of: from every free spot on a half-metre grid she
	# tries the eight directions for a sixth of a second each; a spot where she gets nowhere in any of them
	# (or where she ends up inside something) is reported
	await get_tree().create_timer(3.0).timeout
	var area: Array = [-6.0, -50.0, 36.0, -6.0]          # round the Sagrada Família block
	var base := Vector3.ZERO
	if which == "church":
		var e: Dictionary = entrance("int_sagrada")
		await go_in(e)
		var R: Dictionary = m.D.interiors["int_sagrada"]
		base = m.room_base("int_sagrada")
		area = [0.5, 0.5, R.w - 0.5, R.h - 0.5]
	m.set_physics_process(false)
	await get_tree().physics_frame
	var pl := m.player
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	var space := pl.get_world_3d().direct_space_state
	var dt := 1.0 / 60.0
	var bad := []
	var free_n := 0
	var x: float = area[0]
	while x <= area[2]:
		var z: float = area[1]
		while z <= area[3]:
			var p := base + Vector3(x, 0.02, z)
			q.transform = Transform3D(Basis(), p + Vector3(0, 0.8, 0))
			if space.intersect_shape(q, 1).is_empty():
				free_n += 1
				var best := 0.0
				for k in 8:
					var a := k * PI / 4.0
					pl.global_position = p
					pl.velocity = Vector3(sin(a), 0, cos(a)) * 5.0
					for i in 10:
						pl.velocity.x = sin(a) * 5.0
						pl.velocity.z = cos(a) * 5.0
						pl.velocity.y = 0.0
						pl.move_and_slide()
					best = maxf(best, Vector2(pl.global_position.x - p.x, pl.global_position.z - p.z).length())
				if best < 0.2:
					bad.append([snappedf(x, 0.1), snappedf(z, 0.1), snappedf(best, 0.01)])
			z += 0.5
		x += 0.5
	printerr("stuck scan %s: %d free spots, %d stuck: %s" % [which, free_n, bad.size(), str(bad.slice(0, 60))])
	end_test()


func run_pocket() -> void:
	# the user's stuck spot: between the column by the scaffolding and Pau the builder; push into the column,
	# then try each key combination and see how far she gets in a second
	await get_tree().create_timer(3.0).timeout
	await go_in(entrance("int_sagrada"))
	var O: Vector3 = m.room_base("int_sagrada")
	for start in [[4.75, 19.3, -PI / 2.0], [4.6, 19.9, -2.4], [8.0, 16.7, PI], [12.6, 8.3, -2.2]]:
		for combo in [[KEY_W, KEY_A], [KEY_W, KEY_D], [KEY_A], [KEY_D], [KEY_S]]:
			place(O.x + start[0], O.z + start[1], start[2])
			m.vkeys[KEY_W] = true
			await get_tree().create_timer(0.8).timeout
			m.vkeys.clear()
			var p0 := m.player.global_position
			for k in combo:
				m.vkeys[k] = true
			await get_tree().create_timer(1.0).timeout
			m.vkeys.clear()
			var p1 := m.player.global_position
			printerr("pocket start %s keys %s: pushed to %s, then moved %.2f m to %s" % [str(start), str(combo), str(p0 - O), (p1 - p0).length(), str(p1 - O)])
			await get_tree().create_timer(0.3).timeout
	end_test()


func run_solidcheck(path: String) -> void:
	# (round 33, the user: "She can run through the bike lock stands/bikes… review every single object like this")
	# every object standing on the ground out of doors (a mesh 0.35 m to 6 m across and at least 0.35 m tall, its foot
	# at the ground): its footprint sampled every 0.2 m, and at each sample, does her body fit? A thing she fits
	# inside is a thing she runs through. Written to <path> (a table) and summed up by kind.
	await get_tree().create_timer(3.0).timeout
	var pl := m.player
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = [pl.get_rid()]
	var space := pl.get_world_3d().direct_space_state
	var skip := ["Leaves", "Plants", "Grass", "Tuft", "Flower", "Shadow", "Path", "Trail", "Road", "Kerb", "Pave", "Ground",
		"Terrain", "Water", "Sea", "Win", "Sand", "Lawn", "Fern", "Moss", "Verge", "Light", "Glow", "Sky", "Cloud", "Far",
		"Trunks"]                                                  # (the wood's trunks are merged by the dozen; each is solid by the trees list)
	var kinds := {}
	var rows := ["kind\tname\tx\tz\twide\tdeep\ttall\tfits"]
	var all: Array = m.outdoor.find_children("*", "MeshInstance3D", true, false)
	for b in m.street.bikes:
		all.append(b)                                             # (the parked bikes: judged whole, not by part)
	for n in all:
		var nm := String(n.name)
		if skip.any(func(w): return w in nm):
			continue
		# (not things to bump into: people, who let her slip past after a moment by design; the door glows, flat cards;
		# what she picks up — the ground's flowers, bottles, the ball…; her own model)
		if n is MeshInstance3D and ((n as MeshInstance3D).material_override is ShaderMaterial or m.model.is_ancestor_of(n)):
			continue
		if m.game.ground.any(func(gi): return gi.node == n or gi.node.is_ancestor_of(n)):
			continue
		var person := false
		for who in [m.npcs.outdoor, m.npcs.indoor]:
			for id in who:
				if not who[id].is_empty() and who[id].holder.is_ancestor_of(n):
					person = true
		for w in m.people.people:
			if w.holder.is_ancestor_of(n):
				person = true
		if person:
			continue
		var parts: Array = []
		if n is MeshInstance3D:
			if not (n as MeshInstance3D).is_visible_in_tree() or (n as MeshInstance3D).mesh == null:
				continue
			parts = [n]
		else:
			parts = (n as Node).find_children("*", "MeshInstance3D", true, false)
			nm = "ParkedBike"
		var box := AABB()
		for mi in parts:
			var bb: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
			box = bb if box.size == Vector3.ZERO else box.merge(bb)
		if maxf(box.size.x, box.size.z) > 6.0 or box.size.y < 0.35:
			continue
		# (what she would bump into: only the part of it below 1.2 m over the ground — a lamp's arms and a tree's crown
		# are overhead)
		var g0: float = m.ground_at(Vector3(box.get_center().x, 0, box.get_center().z))
		var low := AABB()
		for mi in parts:
			var mesh: Mesh = (mi as MeshInstance3D).mesh
			var xf: Transform3D = (mi as MeshInstance3D).global_transform
			for si in mesh.get_surface_count():
				var verts: PackedVector3Array = mesh.surface_get_arrays(si)[Mesh.ARRAY_VERTEX]
				for v in verts:
					var w: Vector3 = xf * v
					if w.y < g0 + 1.2 and w.y > g0 + 0.25:      # (not a tree pit's kerb ring, which she steps on)
						low = AABB(w, Vector3.ZERO) if low.size == Vector3.ZERO and low.position == Vector3.ZERO else low.expand(w)
		if low.size == Vector3.ZERO:
			continue
		box = AABB(low.position, Vector3(low.size.x, box.size.y, low.size.z))
		var c := box.get_center()
		if box.position.y > g0 + 0.4:
			continue                                              # (overhead: awnings, lanterns, crowns)
		var fits := 0
		var total := 0
		var x := box.position.x
		while x <= box.end.x + 0.001:
			var z := box.position.z
			while z <= box.end.z + 0.001:
				total += 1
				q.transform = Transform3D(Basis(), Vector3(x, 0.82, z))
				if space.intersect_shape(q, 1).is_empty():
					fits += 1
				z += 0.2
			x += 0.2
		var kind := nm.rstrip("0123456789").trim_suffix("_")
		if not kinds.has(kind):
			kinds[kind] = [0, 0, []]
		kinds[kind][0] += 1
		var share := float(fits) / maxf(1.0, total)
		if share > 0.5:
			kinds[kind][1] += 1
			if kinds[kind][2].size() < 3:
				kinds[kind][2].append("(%.0f, %.0f)" % [c.x, c.z])
		rows.append("%s\t%s\t%.1f\t%.1f\t%.2f\t%.2f\t%.2f\t%.2f\t%s" % [kind, nm, c.x, c.z, box.size.x, box.size.z, box.size.y, share,
			String(n.get_parent().name) + "/" + String(n.get_parent().get_parent().name) if n.get_parent() and n.get_parent().get_parent() else ""])
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string("\n".join(PackedStringArray(rows)) + "\n")
	var names := kinds.keys()
	names.sort_custom(func(a, b2): return kinds[a][1] > kinds[b2][1])
	for k in names:
		if kinds[k][1] > 0:
			printerr("SOLID %-28s %4d of %4d she runs through, e.g. %s" % [k, kinds[k][1], kinds[k][0], ", ".join(kinds[k][2])])
	var held := names.filter(func(k): return kinds[k][1] == 0)
	printerr("SOLID solid already: %s" % ", ".join(held))
	end_test()


func run_parktour(dir: String) -> void:
	# (round 33, the user: "Walk through every corner of the gaudi park and approach it from every gate… pictures…
	# look at it from a birds eye view as well as from the ground") the park through the game's own camera: from above
	# (straight down, and slanting in from eight sides), from outside and just inside each gate, along every footpath
	# a picture every 25 m (five seconds' walk) facing the way she walks and back from each end, before every door,
	# at the foot and the top of every stair. index.txt says where each was taken.
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.flags["parkTicket"] = true
	m.north.refresh()
	var P: Dictionary = m.D.north.park
	var C := Vector3(114.0, 14.0, -196.0)
	var idx := FileAccess.open(dir.path_join("index.txt"), FileAccess.WRITE)
	var cnt := [0]                                                # (a lambda copies plain numbers: this one it shares)
	# from above
	var cam := Camera3D.new()
	add_child(cam)
	cam.far = 900.0
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 150.0
	cam.global_position = C + Vector3(0, 200, 0)
	cam.look_at(C, Vector3.FORWARD)
	cam.current = true
	m.player.visible = false
	cnt[0] += 1
	await shot(dir, "%03d_above" % cnt[0])
	idx.store_line("%03d\tfrom above, straight down, the whole park (north at the top)" % cnt[0])
	cam.projection = Camera3D.PROJECTION_PERSPECTIVE
	cam.fov = 60.0
	for k in 8:
		var a := k * TAU / 8.0
		var names := ["south", "south-west", "west", "north-west", "north", "north-east", "east", "south-east"]
		cam.global_position = C + Vector3(sin(a) * 85.0, 55.0, cos(a) * 85.0)
		cam.look_at(C, Vector3.UP)
		cnt[0] += 1
		await shot(dir, "%03d_above_%s" % [cnt[0], names[k]])
		idx.store_line("%03d\tfrom above, from the %s" % [cnt[0], names[k]])
	cam.current = false
	cam.queue_free()
	m.player.visible = true
	m.cam.current = true
	var pl := m.player
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = [pl.get_rid()]
	var space := pl.get_world_3d().direct_space_state
	var stand := func(at: Vector2, face: Vector2) -> Vector2:
		# (on clear ground at or near the spot)
		for r in [0.0, 0.8, 1.6, 2.4]:
			for k2 in 8:
				var tryp: Vector2 = at + Vector2(cos(k2 * TAU / 8.0), sin(k2 * TAU / 8.0)) * r
				q.transform = Transform3D(Basis(), Vector3(tryp.x, 0.82, tryp.y))
				if space.intersect_shape(q, 1).is_empty():
					return tryp
				if r == 0.0:
					break
		return at
	var snap := func(name: String, at: Vector2, face: Vector2, words: String) -> void:
		var p2: Vector2 = stand.call(at, face)
		place(p2.x, p2.y, atan2(face.x, face.y))
		m.cam_pitch_node.rotation.x = -0.28
		cnt[0] += 1
		await shot(dir, "%03d_%s" % [cnt[0], name])
		idx.store_line("%03d\t%s (%.0f, %.0f)" % [cnt[0], words, p2.x, p2.y])
	# the gates
	var gate_names := ["main gate (Carrer d'Olot)", "Larrard gate", "Carmel gate", "Glòria gate"]
	var grs: Array = P.gate_rects
	for i in grs.size():
		var r: Array = grs[i]
		var gc := Vector2((r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0)
		var inn := (Vector2(C.x, C.z) - gc).normalized()
		await snap.call("gate%d_outside" % (i + 1), gc - inn * 7.0, inn, "outside the " + gate_names[i] + ", looking in")
		await snap.call("gate%d_inside" % (i + 1), gc + inn * 4.0, inn, "just inside the " + gate_names[i])
	# the footpaths
	var paths: Array = P.paths
	for i in paths.size():
		var line: Array = paths[i]
		var pts := []
		for pnt in line:
			pts.append(Vector2(pnt[0], pnt[1]))
		var total := 0.0
		for j in range(1, pts.size()):
			total += (pts[j] as Vector2).distance_to(pts[j - 1])
		var along := 0.0
		while along <= total + 0.1:
			# the point and direction at 'along'
			var acc := 0.0
			var here := pts[0] as Vector2
			var dirv := ((pts[1] as Vector2) - (pts[0] as Vector2)).normalized()
			for j in range(1, pts.size()):
				var seg: float = (pts[j] as Vector2).distance_to(pts[j - 1])
				if acc + seg >= along:
					dirv = ((pts[j] as Vector2) - (pts[j - 1] as Vector2)).normalized()
					here = (pts[j - 1] as Vector2) + dirv * (along - acc)
					break
				acc += seg
			await snap.call("path%d_%03dm" % [i, int(along)], here, dirv, "footpath %d, %d m along" % [i, int(along)])
			along += 25.0
		var last: Vector2 = pts[pts.size() - 1]
		await snap.call("path%d_end_back" % i, last, ((pts[pts.size() - 2] as Vector2) - last).normalized(), "footpath %d, from its end looking back" % i)
	# the doors
	for e in m.D.entrances:
		var ep := Vector2(e.pos[0], e.pos[1])
		if ep.distance_to(Vector2(C.x, C.z)) > 80.0:
			continue
		var nn := Vector2(e.normal[0], e.normal[1])
		await snap.call("door_%s" % e.id, ep + nn * 6.0, -nn, "before the door of " + String(e.name))
	# the stairs
	var steps: Array = P.steps
	for i in steps.size():
		var r: Array = steps[i]
		var sc := Vector2((r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0)
		var up := Vector2(0, -1) if (r[3] - r[1]) > (r[2] - r[0]) else Vector2(1, 0)
		var half := maxf(r[3] - r[1], r[2] - r[0]) / 2.0
		await snap.call("stairs%d_foot" % i, sc - up * (half + 3.0), up, "at the foot of stairs %d" % i)
		await snap.call("stairs%d_top" % i, sc + up * (half + 2.0), -up, "at the top of stairs %d, looking down" % i)
	idx.close()
	printerr("PARKTOUR %d pictures in %s" % [cnt[0], dir])
	end_test()


func run_doorshots(dir: String) -> void:
	# (round 33, the user: "make the glow line up with the doors properly… so it looks like the door glows. Also have a
	# sign outside") every door that can be entered, straight on from 5 m with Sandra beside the way in, and slanting
	# from 7 m: index.txt names each one
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.flags["parkTicket"] = true
	m.north.refresh()
	var idx := FileAccess.open(dir.path_join("index.txt"), FileAccess.WRITE)
	var cam := Camera3D.new()
	add_child(cam)
	cam.fov = 50.0
	var n := 0
	var seen := {}
	for e in m.D.entrances:
		var key := "%s_%d" % [e.id, int(e.pos[0])]
		if seen.has(key):
			continue
		seen[key] = true
		var ep := Vector2(e.pos[0], e.pos[1])
		var nn := Vector2(e.normal[0], e.normal[1])
		var side := Vector2(-nn.y, nn.x)
		var base: float = e.get("base", 0.12)
		var gh: float = m.ground_at(Vector3(ep.x + nn.x * 3.0, 0, ep.y + nn.y * 3.0))
		place(ep.x + nn.x * 3.0 + side.x * 1.6, ep.y + nn.y * 3.0 + side.y * 1.6, atan2(-nn.x, -nn.y))
		var size: Array = e.get("size", [1.24, 2.24])
		var look := Vector3(ep.x, base + size[1] * 0.55, ep.y)
		var fd := 1.7 if String(e.id) == "hypostyle" else 5.0          # (the hall's door: inside its colonnade)
		for v in [["front", fd, 0.0], ["slant", 6.5 if fd > 2.0 else 1.9, 4.5 if fd > 2.0 else 1.4]]:
			var off: Vector2 = nn * float(v[1]) + side * float(v[2])
			cam.global_position = Vector3(ep.x + off.x, maxf(gh, base) + 1.7, ep.y + off.y)
			cam.look_at(look, Vector3.UP)
			cam.current = true
			n += 1
			await shot(dir, "%03d_%s_%s" % [n, e.id, v[0]])
			idx.store_line("%03d\t%s, %s (%.0f, %.0f)" % [n, String(e.name), v[0], ep.x, ep.y])
	idx.close()
	printerr("DOORSHOTS %d pictures in %s" % [n, dir])
	end_test()


func run_slopemap(path: String) -> void:
	# (round 33, the user: "Non walkable hills must be steeper… a consistency based on the gradient") every half metre
	# out of town: how steep (north.gd gradient(), as the game reads it), whether the game lets her walk up it, and what
	# is built there. A picture from above (<path>), coloured by steepness, and counts by area (printed).
	await get_tree().create_timer(3.0).timeout
	var W: Dictionary = m.D.walk
	var cs := 0.5
	var nx := int((W.x1 - W.x0) / cs) + 1
	var nz := int((W.z1 - W.z0) / cs) + 1
	var img := Image.create(nx, nz, false, Image.FORMAT_RGB8)
	var pl := m.player
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = [pl.get_rid()]
	var space := pl.get_world_3d().direct_space_state
	var cr: Array = m.D.city_rect
	var bands := [0.15, 0.22, 0.30, 0.40, 0.55, INF]
	var cols := [Color("#7cc96b"), Color("#c6e27a"), Color("#f2e05a"), Color("#f2a43c"), Color("#d9453a"), Color("#7a1f1a")]
	# areas: by eye on the map (metres)
	var areas := {"Park Güell": Rect2(45, -255, 140, 115), "Tibidabo and its wood": Rect2(-232, -330, 280, 228),
		"Gràcia": Rect2(18, -160, 115, 60), "the east rise and wood": Rect2(86, -100, 111, 267), "the west meadow": Rect2(-232, -102, 74, 269),
		"the beach": Rect2(-158, 129, 244, 38)}
	var counts := {}
	for a in areas:
		counts[a] = [0, 0, 0, 0, 0, 0, 0]                        # per band, then: walkable-looking ground she can't climb
	for iz in nz:
		for ix in nx:
			var x: float = W.x0 + ix * cs
			var z: float = W.z0 + iz * cs
			var p := Vector3(x, 0, z)
			if x > cr[0] and x < cr[2] and z > cr[1] and z < cr[3]:
				img.set_pixel(ix, iz, Color(0.96, 0.96, 0.96))
				continue
			q.transform = Transform3D(Basis(), Vector3(x, 0.82, z))
			if not space.intersect_shape(q, 1).is_empty():
				img.set_pixel(ix, iz, Color(0.45, 0.45, 0.48))      # (walls, houses, trunks, water's edge…)
				continue
			if m.ground_at(p) < -0.3:
				img.set_pixel(ix, iz, Color(0.35, 0.55, 0.85))      # (water)
				continue
			var s: float = m.north.gradient(p).length()
			var climb: bool = m.north.on_path(p) or m.north.on_steps(p) or m.north.at_doorstep(p)
			var b := 0
			while s > bands[b]:
				b += 1
			var c: Color = cols[b]
			if climb:
				c = c.lerp(Color(0.25, 0.35, 0.9), 0.55)            # (the paths and steps, which she may climb however steep)
			img.set_pixel(ix, iz, c)
			if not climb:
				for a in areas:
					if (areas[a] as Rect2).has_point(Vector2(x, z)):
						counts[a][b] += 1
						break
		if iz % 50 == 0:
			await get_tree().process_frame
	img.save_png(path)
	printerr("SLOPE map: %s (%d x %d, half a metre a pixel)" % [path, nx, nz])
	printerr("SLOPE off the paths, square metres by steepness:   <0.15  0.15-0.22  0.22-0.30  0.30-0.40  0.40-0.55  >0.55")
	for a in areas:
		var c2: Array = counts[a]
		printerr("SLOPE %-24s %8d %8d %8d %8d %8d %8d" % [a, c2[0] / 4, c2[1] / 4, c2[2] / 4, c2[3] / 4, c2[4] / 4, c2[5] / 4])
	end_test()


func run_spotshots(spec: String) -> void:
	# (round 33) pictures of listed places as a player sees them: <dir>:<list file>, the file's lines "name x z";
	# Sandra stands 4.5 m off (south first, else east, north, west — wherever she fits), facing the spot, and the
	# game's own camera takes it from behind her
	var dir := spec.split(":")[0]
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	var pl := m.player
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = [pl.get_rid()]
	var space := pl.get_world_3d().direct_space_state
	for line in FileAccess.get_file_as_string(spec.split(":")[1]).split("\n"):
		var w := line.strip_edges().split(" ")
		if w.size() < 3:
			continue
		var c := Vector2(float(w[1]), float(w[2]))
		var from := c + Vector2(0, 4.5)
		for d in [Vector2(0, 4.5), Vector2(4.5, 0), Vector2(0, -4.5), Vector2(-4.5, 0)]:
			q.transform = Transform3D(Basis(), Vector3(c.x + d.x, 0.82, c.y + d.y))
			if space.intersect_shape(q, 1).is_empty():
				from = c + d
				break
		place(from.x, from.y, atan2(c.x - from.x, c.y - from.y))
		m.cam_pitch_node.rotation.x = -0.32
		await shot(dir, w[0])
	end_test()


func run_placecheck(path: String) -> void:
	# (round 33, the user: street lamps on a pavement and out of the way, nothing blocking a walking path or where a
	# crossing meets the pavement, benches not in front of crossings, the beach's umbrella) every placed thing: what
	# it stands on, how far from the kerb and from the house fronts, how near a zebra crossing. Breaches are printed
	# by kind; the whole table goes to <path>.
	await get_tree().create_timer(3.0).timeout
	# the crossings, read off the painted stripes: each stripe a 2.7 x 0.5 m box; stripes within 1.2 m are one crossing
	var stripes := []
	for z in m.outdoor.find_children("Zebras", "MeshInstance3D", true, false):
		var mesh: Mesh = (z as MeshInstance3D).mesh
		var xf: Transform3D = (z as MeshInstance3D).global_transform
		for si in mesh.get_surface_count():
			var vs: PackedVector3Array = mesh.surface_get_arrays(si)[Mesh.ARRAY_VERTEX]
			var idx = mesh.surface_get_arrays(si)[Mesh.ARRAY_INDEX]
			# (boxes of 8 corners, 24 or 8 vertices each: gather by blocks of the box's own size)
			var pts := []
			for v in vs:
				pts.append(xf * v)
			var step := 24 if pts.size() % 24 == 0 else 8
			for i in range(0, pts.size(), step):
				var bb := AABB(pts[i], Vector3.ZERO)
				for j in range(i, mini(i + step, pts.size())):
					bb = bb.expand(pts[j])
				stripes.append(Rect2(bb.position.x, bb.position.z, bb.size.x, bb.size.z))
	var crossings := []
	var ways := []                                               # (per crossing: true when its stripes are wide in x)
	for st0 in stripes:
		var st: Rect2 = st0
		var merged := false
		var stripe_x := st.size.x > st.size.y
		for k in crossings.size():
			# (only stripes lying the same way: at a corner two crossings meet, and must stay two)
			if ways[k] == stripe_x and (crossings[k] as Rect2).grow(1.2).intersects(st):
				crossings[k] = (crossings[k] as Rect2).merge(st)
				merged = true
				break
		if not merged:
			crossings.append(st)
			ways.append(stripe_x)
	printerr("PLACE %d zebra crossings" % crossings.size())
	# the city blocks' pavements: between the house fronts (poly) and the kerb (pave)
	var blocks := []
	for b in m.D.blocks:
		var poly := PackedVector2Array()
		var pave := PackedVector2Array()
		for q in b.poly:
			poly.append(Vector2(q[0], q[1]))
		for q in b.pave:
			pave.append(Vector2(q[0], q[1]))
		blocks.append([poly, pave])
	var edge_dist := func(pg: PackedVector2Array, p: Vector2) -> float:
		var best := INF
		for i in pg.size():
			best = minf(best, p.distance_to(Geometry2D.get_closest_point_to_segment(p, pg[i], pg[(i + 1) % pg.size()])))
		return best
	# what each thing is: the named mesh nearest it
	var named := []
	for n in m.outdoor.find_children("*", "MeshInstance3D", true, false):
		var nm := String(n.name)
		for pre in ["StreetBench", "MeshyBench", "GardenBench", "Planter", "Bins", "BikeStand", "Wares", "KitCafe", "MeshyCafe",
				"Plaque_", "BougPlanter", "Kiosk", "Stall", "Umbrella", "Bench", "Fountain", "Sign"]:
			if nm.begins_with(pre):
				var bb: AABB = (n as MeshInstance3D).global_transform * (n as MeshInstance3D).get_aabb()
				if maxf(bb.size.x, bb.size.z) < 8.0:
					named.append([pre.trim_suffix("_"), Vector2(bb.get_center().x, bb.get_center().z)])
				break
	var items := []
	for l in m.D.lamps:
		items.append(["street lamp", Vector2(l.pos[0], l.pos[1]), 0.15])
	var cr: Array = m.D.city_rect
	for t in m.D.trees:
		if t[0] > cr[0] and t[0] < cr[2] and t[1] > cr[1] and t[1] < cr[3]:
			items.append(["street tree", Vector2(t[0], t[1]), 0.25])
	for o in m.D.obstacles:
		var p := Vector2(o.pos[0] + o.off[0], o.pos[1] + o.off[1])
		var kind := "thing"
		var bd := 2.5
		for nn in named:
			var d: float = (nn[1] as Vector2).distance_to(p)
			if d < bd:
				bd = d
				kind = nn[0]
		items.append([kind, p, float(o.r) * 0.75])
	for th in m.D.get("things2d", []):
		if th.type in ["bench", "bin", "umbrella", "kiosk", "stall", "terrace", "sign"]:
			items.append(["2D " + String(th.type), Vector2(th.pos[0], th.pos[1]), 0.4])
	var rows := ["kind\tx\tz\tground\tfrom kerb\tfrom fronts\tto crossing\tbreach"]
	var breaches := {}
	for it in items:
		var p: Vector2 = it[1]
		var r: float = it[2]
		var ground := "other"
		var dk := -1.0
		var df := -1.0
		for bl in blocks:
			if Geometry2D.is_point_in_polygon(p, bl[1]) and not Geometry2D.is_point_in_polygon(p, bl[0]):
				ground = "pavement"
				dk = edge_dist.call(bl[1], p)
				df = edge_dist.call(bl[0], p)
				break
		var inside_cr: bool = p.x > cr[0] and p.x < cr[2] and p.y > cr[1] and p.y < cr[3]
		if ground == "other" and inside_cr:
			var g: float = m.ground_at(Vector3(p.x, 0, p.y))
			ground = "road" if g < 0.01 else "raised (Rambla, park, square)"
		elif ground == "other":
			ground = "out of town"
		# (in front of a crossing: in its landing — the strip of pavement as wide as the crossing, 2.5 m on from either
		# end, where people step off and on; beside it is fine)
		var dc := INF
		var in_front := false
		for ci in crossings.size():
			var cc: Rect2 = crossings[ci]
			var q := Vector2(clampf(p.x, cc.position.x, cc.end.x), clampf(p.y, cc.position.y, cc.end.y))
			dc = minf(dc, q.distance_to(p) - r)
			# (x-wide stripes: the crossing is walked along z, so its landings lie beyond its z ends)
			var land: Rect2 = cc.grow_individual(0.3, 2.5, 0.3, 2.5) if ways[ci] else cc.grow_individual(2.5, 0.3, 2.5, 0.3)
			if land.grow(r).has_point(p) and not cc.has_point(p):
				in_front = true
		var why := []
		if in_front:
			why.append("in front of a crossing (%.1f m)" % maxf(dc, 0.0))
		if ground == "road":
			why.append("on the road")
		# (round 37: its foot clear of the kerb edge, 0.75 m in at least, and still at the kerb side, 1.0 m at most)
		if it[0] == "street lamp" and ground == "pavement" and (dk > 1.0 or dk < 0.75):
			why.append("lamp %.2f m in from the kerb" % dk)
		if it[0] != "street lamp" and it[0] != "street tree" and ground == "pavement" and dk - r > 0.9 and df - r > 0.9:
			why.append("in the walking line (%.1f m to the kerb, %.1f m to the fronts)" % [dk - r, df - r])
		if ground != "pavement" and it[0] == "street lamp":
			# (out of the city blocks: how far from the nearest wall — the house fronts — by rays at waist height)
			var space2 := m.player.get_world_3d().direct_space_state
			df = INF
			for k2 in 16:
				var a2 := k2 * TAU / 16.0
				var o3 := Vector3(p.x, 1.0, p.y) + Vector3(sin(a2), 0, cos(a2)) * 0.3
				var hit := space2.intersect_ray(PhysicsRayQueryParameters3D.create(o3, o3 + Vector3(sin(a2), 0, cos(a2)) * 6.0, m.LAYER_BODY))
				if not hit.is_empty() and hit.collider.get_child_count() > 0:
					df = minf(df, Vector2(hit.position.x - p.x, hit.position.z - p.y).length())
		rows.append("%s\t%.1f\t%.1f\t%s\t%.2f\t%.2f\t%.2f\t%s" % [it[0], p.x, p.y, ground, dk, df, dc, "; ".join(why)])
		if not why.is_empty():
			if not breaches.has(it[0]):
				breaches[it[0]] = []
			breaches[it[0]].append("(%.0f, %.0f) %s" % [p.x, p.y, "; ".join(why)])
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string("\n".join(PackedStringArray(rows)) + "\n")
	for k in breaches:
		printerr("PLACE %-14s %3d: %s" % [k, breaches[k].size(), " | ".join(breaches[k].slice(0, 6))])
	printerr("PLACE %d things checked, %d breaches" % [items.size(), breaches.values().reduce(func(a, b2): return a + b2.size(), 0)])
	end_test()


func run_walkline(spec: String) -> void:
	# (round 34) a probe: --walkline=x0,z0,x1,z1,secs — she is put at the first point facing the second and walks
	# there with W for so many seconds; her place, height and what she pressed against every half second
	await get_tree().create_timer(3.0).timeout
	var v := spec.split(",")
	var a := Vector2(float(v[0]), float(v[1]))
	var b := Vector2(float(v[2]), float(v[3]))
	var d := (b - a).normalized()
	await old_walls()
	place(a.x, a.y, atan2(d.x, d.y))
	m.model.position.y = m.ground_at(m.player.global_position)
	await get_tree().create_timer(0.4).timeout
	m.vkeys[KEY_W] = true
	var t0 := 0.0
	while t0 < float(v[4]):
		await get_tree().create_timer(0.5).timeout
		t0 += 0.5
		var pp := m.player.global_position
		var hit := ""
		for i in m.player.get_slide_collision_count():
			hit += " " + str(m.player.get_slide_collision(i).get_collider())
		var gr: Vector2 = m.north.gradient(pp) if m.north else Vector2.ZERO
		print("WALK t=%.1f x=%.2f z=%.2f h=%.2f ground=%.2f terrain=%.2f slope=(%.2f, %.2f) stuck=%.1f slip=%s%s" % [t0, pp.x, pp.z,
			m.model.position.y, m.ground_at(pp), m.terrain_at(pp.x, pp.z), gr.x, gr.y, m.stuck_t, m.slipping, hit])
		# (round 40) and the camera: the arm's length, its tip, the wood's dip, first person
		print("  CAM arm=%.2f hit=%.2f tip=%.2f blocked=%.2f wood=%.2f fp=%s fpk=%.2f" % [m.arm.spring_length, m.arm.get_hit_length(),
			m.arm_tip, m.arm_blocked(m.arm_tip), m.wood_k, m.fp_on, m.fp_k])
	m.vkeys.erase(KEY_W)
	end_test()


func run_heights(spec: String) -> void:
	# (round 40) --heights=x0,z0,x1,z1,step — the ground's height on a grid (rows north to south), '#' where something
	# solid stands at her waist; and whether the park's no-invisible-walls rule holds there
	await get_tree().create_timer(3.0).timeout
	var v := spec.split(",")
	var stp := float(v[4])
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = m.player.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = [m.player.get_rid()]
	var space := m.player.get_world_3d().direct_space_state
	var z := float(v[1])
	while z <= float(v[3]) + 0.001:
		var row := "H z=%7.2f " % z
		var x := float(v[0])
		while x <= float(v[2]) + 0.001:
			q.transform = Transform3D(Basis(), Vector3(x, 0.82, z))
			row += ("   #  " if not space.intersect_shape(q, 1).is_empty() else "%6.2f" % m.terrain_at(x, z))
			x += stp
		print(row)
		z += stp
	end_test()


func run_roomwalk(spec: String) -> void:
	# (round 40) --roomwalk=<rid>:x0,z0,x1,z1,secs — in through its door, then put at (x0, z0) in the room's own
	# metres facing (x1, z1) and walked there with W; her place and the camera's arm every half second
	await get_tree().create_timer(3.0).timeout
	var parts := spec.split(":")
	await go_in(entrance(parts[0]))
	await get_tree().create_timer(1.0).timeout
	var O: Vector3 = m.room_base(parts[0])
	var v := parts[1].split(",")
	var a := Vector2(float(v[0]), float(v[1]))
	var b := Vector2(float(v[2]), float(v[3]))
	var d := (b - a).normalized()
	place(O.x + a.x, O.z + a.y, atan2(d.x, d.y))
	await get_tree().create_timer(0.6).timeout
	m.vkeys[KEY_W] = true
	var t0 := 0.0
	while t0 < float(v[4]):
		await get_tree().create_timer(0.5).timeout
		t0 += 0.5
		var lp: Vector3 = m.local_pos()
		var hc = m.arm.get_hit_length()
		print("ROOM t=%.1f x=%.2f z=%.2f arm=%.2f hit=%.2f want=%.2f free=%s fp=%s wood=%.2f seen=%s" % [t0, lp.x, lp.z,
			m.arm.spring_length, hc, m.cam_len, m.free_cam(), m.fp_on, m.wood_k, m.model.visible])
	m.vkeys.erase(KEY_W)
	end_test()


func run_gridprobe(spec: String) -> void:
	# (round 35) --gridprobe=x0,z0,x1,z1: the play-through's map of where she fits — is (x1, z1) reached from (x0, z0),
	# and the map round (x1, z1), 24 m each way ('#' blocked, '.' free, 'A'/'B' the two ends, '*' the route)
	await get_tree().create_timer(3.0).timeout
	var pt := Node.new()
	pt.set_script(load(m.world_res("tests/playthrough.gd")))
	add_child(pt)
	pt.tst = self
	pt.m = m
	pt.g = m.game
	await pt.build_grids()
	for d in pt.dyn:
		for c in d[1]:
			pt.grid.set_point_solid(c, (d[0] as StaticBody3D).collision_layer != 0)
	var v := spec.split(",")
	var a: Vector2i = pt.free_near(pt.grid, pt.cell_of(Vector2(float(v[0]), float(v[1]))))
	var b: Vector2i = pt.free_near(pt.grid, pt.cell_of(Vector2(float(v[2]), float(v[3]))))
	var route: Array = pt.grid.get_id_path(a, b)
	print("GRIDPROBE from %s to %s: %s (%d cells)" % [a, b, "joined" if not route.is_empty() else "NOT joined", route.size()])
	var on := {}
	for c in route:
		on[c] = true
	var cb: Vector2i = pt.cell_of(Vector2(float(v[2]), float(v[3])))
	var R := int(24.0 / pt.CELL)
	for dz in range(-R, R + 1, 2):
		var row := ""
		for dx in range(-R, R + 1, 2):
			var c := cb + Vector2i(dx, dz)
			row += "A" if c == a else ("B" if c == b else ("*" if on.has(c) else ("#" if pt.grid.is_in_boundsv(c) and pt.grid.is_point_solid(c) else ".")))
		print("GRID " + row)
	end_test()


func run_keyseq(spec: String) -> void:
	# (round 35) --keyseq=x,z,yaw:W2,A1,WA1.5,S1 — she is put at (x, z) facing yaw (radians), then the keys are held
	# as a player would (letters held together, for so many seconds each); her place, facing and speed every 0.25 s
	await get_tree().create_timer(3.0).timeout
	var parts := spec.split(":")
	var a := parts[0].split(",")
	place(float(a[0]), float(a[1]), float(a[2]))
	m.model.position.y = m.ground_at(m.player.global_position)
	await get_tree().create_timer(0.6).timeout
	var codes := {"W": KEY_W, "A": KEY_A, "S": KEY_S, "D": KEY_D}
	for step in parts[1].split(","):
		var letters := ""
		var num := ""
		for ch in step:
			if ch in codes:
				letters += ch
			else:
				num += ch
		for ch in letters:
			m.vkeys[codes[ch]] = true
		var t0 := 0.0
		while t0 < float(num):
			await get_tree().create_timer(0.25).timeout
			t0 += 0.25
			var pp := m.player.global_position
			var hit := ""
			for i in m.player.get_slide_collision_count():
				hit += " " + str(m.player.get_slide_collision(i).get_collider())
			print("KEYS %s t=%.2f x=%.2f z=%.2f face=%.2f speed=%.2f h=%.2f veil=%.2f%s" % [letters, t0, pp.x, pp.z, m.model.rotation.y, m.speed, m.model.position.y, m.veil_a, hit])
		for ch in letters:
			m.vkeys.erase(codes[ch])
		await get_tree().create_timer(0.3).timeout
	if parts.size() > 2:
		# (a third part: a picture at the end, to that file)
		for c in m.get_children():
			if c is CanvasLayer and c.layer > 0:
				c.visible = false
		await get_tree().create_timer(0.4).timeout
		get_viewport().get_texture().get_image().save_png(parts[2])
	end_test()


func run_funiride(dir: String) -> void:
	# (round 41, 03 #28a) --funiride=<dir>: the funicular up and down from her eyes in the car, a picture every 3 s of
	# the ride (at double speed), and one once she is off at each end
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var N: Dictionary = m.D.north
	for leg in ["up", "down"]:
		var d: Array = N.cable.door_low if leg == "up" else N.cable.door_top
		place(d[0], d[1] + (1.0 if leg == "up" else -1.0), PI if leg == "up" else 0.0)
		await get_tree().create_timer(0.5).timeout
		Engine.time_scale = 2.0
		m.north.start_cable(leg == "up")
		var k := 0
		while not m.north.ride.is_empty() and k < 40:
			await get_tree().create_timer(3.0 * 2.0).timeout
			k += 1
			var cp := get_viewport().get_camera_3d().global_position
			printerr("FUNI %s %d cam=(%.1f, %.1f, %.1f) look=%s inside=%s model=%s prompt=%s" % [leg, k, cp.x, cp.y, cp.z, m.ride_look,
				m.ride_inside, m.model.visible, m.prompt.text])
			get_viewport().get_texture().get_image().save_jpg(dir.path_join("%s_%02d.jpg" % [leg, k]), 0.85)
			# (the user: "test what it looks like if she's looking out towards the city, and also looking up the hill.
			# Sideways is not enough") the camera taken round a quarter at a time, as the player would with ← →
			var yaw0: float = m.cam_yaw_node.rotation.y
			for qi in [1, 2, 3]:
				m.cam_yaw_node.rotation.y = yaw0 + qi * PI / 2.0
				m.last_manual_cam = m.t
				await get_tree().create_timer(0.25 * 2.0).timeout
				get_viewport().get_texture().get_image().save_jpg(dir.path_join("%s_%02d_q%d.jpg" % [leg, k, qi]), 0.85)
			m.cam_yaw_node.rotation.y = yaw0
		Engine.time_scale = 1.0
		await get_tree().create_timer(1.5).timeout
		printerr("FUNI %s off: at (%.1f, %.1f) look=%s model=%s" % [leg, m.player.global_position.x, m.player.global_position.z,
			m.ride_look, m.model.visible])
		get_viewport().get_texture().get_image().save_jpg(dir.path_join("%s_off.jpg" % leg), 0.85)
	end_test()


func run_bikeline(spec: String) -> void:
	# (round 35, PATH_RULES F14) --bikeline=x0,z0,x1,z1,secs: as --walkline, but on the bike first (she owns one); then
	# off it at the end and on again where she stands — printing where she got to and what the game said
	await get_tree().create_timer(3.0).timeout
	m.game.S["has_bike"] = true
	var v := spec.split(",")
	var a := Vector2(float(v[0]), float(v[1]))
	var b := Vector2(float(v[2]), float(v[3]))
	var d := (b - a).normalized()
	place(a.x, a.y, atan2(d.x, d.y))
	await get_tree().create_timer(0.4).timeout
	m.bike_key()
	print("BIKE on=%s toasts=%s" % [(m.street.riding != null), m.toasts])
	await get_tree().create_timer(0.3).timeout
	m.vkeys[KEY_W] = true
	var t0 := 0.0
	# (round 41) a sixth value, a folder: a picture every half second, as the player sees it, and where the camera is
	var shots_dir := v[5] if v.size() > 5 else ""
	if shots_dir != "":
		DirAccess.make_dir_recursive_absolute(shots_dir)
	while t0 < float(v[4]):
		await get_tree().create_timer(0.5).timeout
		t0 += 0.5
		var pp := m.player.global_position
		print("BIKE t=%.1f x=%.2f z=%.2f on=%s park=%s" % [t0, pp.x, pp.z, (m.street.riding != null), m.in_bike_free_park(pp)])
		if shots_dir != "":
			var cp := get_viewport().get_camera_3d().global_position
			print("BIKECAM t=%.1f cam=(%.2f, %.2f, %.2f) arm=%.2f" % [t0, cp.x, cp.y, cp.z, m.arm.get_hit_length()])
			get_viewport().get_texture().get_image().save_jpg(shots_dir.path_join("bike_%03d.jpg" % int(t0 * 2)), 0.85)
	m.vkeys.erase(KEY_W)
	print("BIKE said %s" % [m.toasts])
	end_test()


func run_roofwalk(dir: String) -> void:
	# (round 34) Park Güell's covered walk: from the hill up onto its roof and along it, then at its open edge (she
	# must stay up), then the lower walk under it and from the square in to its back wall (she must stay down);
	# her height and place every half second, and a picture at the end of each
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var legs := [
		["onto_roof", Vector2(155.5, -203.6), Vector2(140.0, -199.5), 4.0],
		["along_roof", Vector2(-1, -1), Vector2(-1.0, 0.0), 4.0],
		["off_edge", Vector2(-1, -1), Vector2(0.0, 1.0), 2.5],
		["lower_walk", Vector2(100.0, -199.9), Vector2(120.0, -199.9), 4.0],
		["square_to_wall", Vector2(107.1, -192.0), Vector2(107.1, -206.0), 4.0],
	]
	for leg in legs:
		var a: Vector2 = leg[1]
		var b: Vector2 = leg[2]
		var dirv: Vector2
		if a.x == -1:                       # (carry on from where she is, turned that way)
			var here := m.player.global_position
			dirv = b
			place(here.x, here.z, atan2(dirv.x, dirv.y))
		else:
			dirv = (b - a).normalized()
			place(a.x, a.y, atan2(dirv.x, dirv.y))
			m.model.position.y = m.ground_at(m.player.global_position)
		await get_tree().create_timer(0.4).timeout
		m.vkeys[KEY_W] = true
		var t0 := 0.0
		while t0 < float(leg[3]):
			await get_tree().create_timer(0.5).timeout
			t0 += 0.5
			var pp := m.player.global_position
			print("ROOF %s t=%.1f x=%.2f z=%.2f h=%.2f" % [leg[0], t0, pp.x, pp.z, m.model.position.y])
		m.vkeys.erase(KEY_W)
		await shot(dir, leg[0])
	end_test()


func run_solidwalk(dir: String) -> void:
	# (round 33) a parked bike at a stand and a flower stall: walked straight at from each side, and ridden at; how close
	# she gets (her middle to its middle) and a picture of the closest, as the player sees it
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.has_bike = true
	var targets := []
	for b in m.street.bikes:
		if b != m.street.own_bike:
			targets.append(["parked bike", b.global_position])
			break
	for n in m.outdoor.find_children("BikeStand_*", "MeshInstance3D", true, false):
		var bb: AABB = (n as MeshInstance3D).global_transform * (n as MeshInstance3D).get_aabb()
		targets.append(["bike stand", bb.get_center()])
		break
	for t in targets:
		var c: Vector3 = t[1]
		var best := INF
		for side in 4:
			var a := side * PI / 2.0
			var from := c + Vector3(sin(a), 0, cos(a)) * 4.0
			place(from.x, from.z, a + PI)
			await get_tree().create_timer(0.3).timeout
			await hold(KEY_W, 2.0)
			var d := Vector2(m.player.global_position.x - c.x, m.player.global_position.z - c.z).length()
			best = minf(best, d)
			if side == 0:
				await shot(dir, "solid_%s" % String(t[0]).replace(" ", "_"))
		# and on the bike, from the first side
		place(c.x + 6.0, c.z, -PI / 2.0)
		m.input_key(KEY_B)
		await get_tree().create_timer(0.5).timeout
		await hold(KEY_W, 2.5)
		var dr := Vector2(m.player.global_position.x - c.x, m.player.global_position.z - c.z).length()
		await shot(dir, "solid_%s_bike" % String(t[0]).replace(" ", "_"))
		m.input_key(KEY_B)
		await get_tree().create_timer(0.5).timeout
		printerr("SOLIDWALK %s at (%.1f, %.1f): on foot never nearer than %.2f m, on the bike %.2f m" % [t[0], c.x, c.z, best, dr])
	end_test()


func run_nobus(dir: String) -> void:
	# (round 33, the user: "Get rid of the cars/bus and bus stops") nothing of the round-27 traffic is left: no bus,
	# no cars, no stop poles; pictures where the four stops stood, as a player sees them; a ride down the old route
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var left := []
	for nm in ["Bus", "Car_*", "BusStops", "BusStopSign*"]:
		for n in m.outdoor.find_children(nm, "", true, false):
			left.append(String(n.name))
	printerr("NOBUS left in the world: %s" % (str(left) if not left.is_empty() else "nothing"))
	var stops := [[-30.0, 126.4], [86.5, 50.0], [-60.0, -97.2], [-155.8, 33.0]]
	for i in stops.size():
		var sp: Array = stops[i]
		place(sp[0] + 4.0, sp[1] + 4.0, atan2(-4.0, -4.0))      # (a few steps off, facing the old stop)
		await shot(dir, "stop_%d" % (i + 1))
	m.game.S.has_bike = true
	place(-140.0, 122.1, PI / 2)                                  # the old bus ring: Gran Via, eastbound
	m.input_key(KEY_B)
	await get_tree().create_timer(0.5).timeout
	var p0: Vector3 = m.player.global_position
	await hold(KEY_W, 6.0)
	var p1: Vector3 = m.player.global_position
	printerr("NOBUS ride along the old bus route: %.0f m in 6 s, riding=%s" % [p0.distance_to(p1), m.street.riding != null])
	await shot(dir, "ride")
	end_test()


func run_playthrough(dir: String) -> void:
	# (round 32, the user) every mission played from a fresh game, the way a player does, with the picture tour:
	# playthrough.gd; --from=<mission> starts at that mission's saved state instead of on the beach
	var from := ""
	for a in args_all:
		if String(a).begins_with("--from="):
			from = String(a).trim_prefix("--from=")
	var pt := Node.new()
	pt.set_script(load(m.world_res("tests/playthrough.gd")))
	add_child(pt)
	await pt.run(self, m, dir, from)


func run_visit(dir: String) -> void:
	# (round 35, the user) everything she can talk to, read or use, visited with the keys, read and pictured: visit.gd
	var part := "census"
	for a in args_all:
		if String(a).begins_with("--part="):
			part = String(a).trim_prefix("--part=")
	var vt := Node.new()
	vt.set_script(load(m.world_res("tests/visit.gd")))
	add_child(vt)
	await vt.run(self, m, dir, part)


func seam_walk(sname: String, x: float, z: float, heading: float, secs: float) -> Vector3:
	# one walk as a player would make it: W held from a spot, a line each second, where she ended.
	# A talk box that opens on the way (Sergi stopping her at the bridge) is clicked away, as a player would.
	place(x, z, heading)
	await get_tree().create_timer(0.5).timeout
	while m.dlg_open:
		m.dialog_next()
		await get_tree().create_timer(0.05).timeout
	var p0 := m.player.global_position
	m.vkeys[KEY_W] = true
	for i in int(secs):
		await get_tree().create_timer(1.0).timeout
		while m.dlg_open:
			m.dialog_next()
			await get_tree().create_timer(0.05).timeout
		var p := m.player.global_position
		var hit := ""
		for j in m.player.get_slide_collision_count():
			var col := m.player.get_slide_collision(j).get_collider()
			hit += " " + (String(col.name) if col else "?")
		# (the body rides at y 0 — outdoor physics is flat; the eye's height is ground_at's answer)
		printerr("   %-16s t=%2d  at (%6.1f, %6.1f) h=%5.2f  speed %3.1f  wall=%s%s" % [sname, i + 1, p.x, p.z, m.ground_at(p), m.speed, m.player.is_on_wall(), hit])
	var frac := secs - float(int(secs))
	if frac > 0.01:
		await get_tree().create_timer(frac).timeout
	m.vkeys.clear()
	await get_tree().create_timer(0.3).timeout
	var p1 := m.player.global_position
	printerr("SEAMWALK %-16s went %5.1f m from (%6.1f, %6.1f)" % [sname, Vector2(p1.x - p0.x, p1.z - p0.z).length(), p0.x, p0.z])
	return p1


func stuck_scan(sname: String, area: Array) -> void:
	# (round 32) run_stuck's sweep, away from the flat city: each spot is taken on the walked surface itself
	# (found with a ray from above — the hill, the forecourt pad, the bridge deck), and water is left out
	m.set_physics_process(false)
	await get_tree().physics_frame
	var pl := m.player
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = [pl.get_rid()]
	var space := pl.get_world_3d().direct_space_state
	var bad := []
	var free_n := 0
	var x: float = area[0]
	while x <= area[2]:
		var z: float = area[1]
		while z <= area[3]:
			var g := m.ground_at(Vector3(x, 0, z))
			if g < -0.3:                                                   # the river, the sea
				z += 0.5
				continue
			var ray := PhysicsRayQueryParameters3D.create(Vector3(x, g + 2.4, z), Vector3(x, g - 2.0, z), m.LAYER_BODY, [pl.get_rid()])
			var hit := space.intersect_ray(ray)
			var py := g
			if not hit.is_empty():
				py = hit.position.y
			var p := Vector3(x, py + 0.03, z)
			q.transform = Transform3D(Basis(), p + Vector3(0, 0.8, 0))
			if space.intersect_shape(q, 1).is_empty():
				free_n += 1
				var best := 0.0
				for k in 8:
					var a := k * PI / 4.0
					pl.global_position = p
					pl.velocity = Vector3(sin(a), 0, cos(a)) * 5.0
					for i in 10:
						pl.velocity.x = sin(a) * 5.0
						pl.velocity.z = cos(a) * 5.0
						pl.velocity.y = 0.0
						pl.move_and_slide()
					best = maxf(best, Vector2(pl.global_position.x - p.x, pl.global_position.z - p.z).length())
				if best < 0.2:
					bad.append([snappedf(x, 0.1), snappedf(z, 0.1)])
			z += 0.5
		x += 0.5
	m.set_physics_process(true)
	printerr("seam scan %-9s: %d free spots, %d stuck: %s" % [sname, free_n, bad.size(), str(bad.slice(0, 40))])


func run_seamprobe() -> void:
	# what exactly stands in the way at the deck's south-east corner: rays east through the stuck spot
	await get_tree().create_timer(3.0).timeout
	var space := m.player.get_world_3d().direct_space_state
	for y in [0.2, 0.6, 1.0, 1.08, 1.14, 1.3, 1.5]:
		var ray := PhysicsRayQueryParameters3D.create(Vector3(-168.5, y, -3.6), Vector3(-160.0, y, -3.6), m.LAYER_BODY, [m.player.get_rid()])
		var hit := space.intersect_ray(ray)
		if hit.is_empty():
			printerr("probe east y=%.2f: nothing" % y)
		else:
			printerr("probe east y=%.2f: hit x=%.2f z=%.2f  n=(%.2f,%.2f,%.2f)  %s" % [y, hit.position.x, hit.position.z, hit.normal.x, hit.normal.y, hit.normal.z, hit.collider.name])
	for z in [-3.4, -3.6, -3.9, -4.3]:
		var ray2 := PhysicsRayQueryParameters3D.create(Vector3(-168.5, 1.0, z), Vector3(-160.0, 1.0, z), m.LAYER_BODY, [m.player.get_rid()])
		var hit2 := space.intersect_ray(ray2)
		if hit2.is_empty():
			printerr("probe east z=%.1f: nothing" % z)
		else:
			printerr("probe east z=%.1f: hit x=%.2f  n=(%.2f,%.2f,%.2f)  %s" % [z, hit2.position.x, hit2.normal.x, hit2.normal.y, hit2.normal.z, hit2.collider.name])
	# the same walk that parks, sampled densely: what does the game think it is doing?
	place(-170.0, -3.6, PI / 2.0)
	await get_tree().create_timer(0.5).timeout
	while m.dlg_open:
		m.dialog_next()
		await get_tree().create_timer(0.05).timeout
	m.vkeys[KEY_W] = true
	for i in 20:
		await get_tree().create_timer(0.2).timeout
		var p := m.player.global_position
		var v := m.player.get_real_velocity()
		var cons := ""
		for j in m.player.get_slide_collision_count():
			var sc := m.player.get_slide_collision(j)
			cons += "  [%s at (%.2f, %.2f, %.2f) n=(%.2f, %.2f, %.2f)]" % [sc.get_collider().name, sc.get_position().x, sc.get_position().y, sc.get_position().z, sc.get_normal().x, sc.get_normal().y, sc.get_normal().z]
		printerr("probe walk t=%4.1f at (%7.2f, %6.2f) dlg=%s busy=%s speed=%4.1f dir=(%5.2f,%5.2f) v=(%5.2f,%5.2f) wall=%s%s" % [
			(i + 1) * 0.2, p.x, p.z, m.dlg_open, m.busy, m.speed, m.move_dir.x, m.move_dir.y, v.x, v.z, m.player.is_on_wall(), cons])
	m.vkeys.clear()
	end_test()


func run_seams() -> void:
	# (round 32, the user: new tests for the new areas — "Make sure that Sandra can't get stuck anywhere,
	# especially around walls.") The places round 32 touched: the funicular forecourt's new steps, the Alzina
	# footpath's mended ends, and the bridge's shortened deck. First walked as a player would (up the steps and
	# back down, the footpath end to end, onto the deck and shoving along the barrier by either parapet), then
	# each area is swept for stuck pockets on a half-metre grid.
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("day")
	# the forecourt steps: across both treads to the station's wall (which rightly stops her — nothing else
	# may, the steps are drawn, not solid), and back down to the footpath
	var e := await seam_walk("steps_up", -63.5, -98.0, PI, 2.0)
	printerr("SEAMS steps up: z=%.1f h=%.2f %s" % [e.z, m.ground_at(e), "(crossed the steps to the wall)" if e.z < -100.0 else "(STOPPED BEFORE THE STEPS)"])
	e = await seam_walk("steps_down", -63.5, -100.2, 0.0, 2.5)
	printerr("SEAMS steps down: h=%.2f z=%.1f %s" % [m.ground_at(e), e.z, "(on the footpath)" if m.ground_at(e) < 0.2 and e.z > -99.7 else "(STUCK ABOVE)"])
	# the Alzina footpath end to end: from the block's pavement north to the setts street, and back
	e = await seam_walk("alzina_north", 129.6, -58.9, PI, 10.0)
	printerr("SEAMS alzina north: z=%.1f %s" % [e.z, "(reached the street)" if e.z < -95.0 else "(STOPPED SHORT)"])
	e = await seam_walk("alzina_south", 129.6, -97.3, 0.0, 10.0)
	printerr("SEAMS alzina south: z=%.1f %s" % [e.z, "(back at the block)" if e.z > -62.0 else "(STOPPED SHORT)"])
	# the closed bridge: Sergi's talk is only words (clicked away, she can keep pressing on), so what must
	# really hold her is the barrier pole at x -179.5. Straight down the deck first, then pressed into the
	# gap by either parapet — if she slips past the pole she is out on the closed west bank.
	e = await seam_walk("bridge_west", -157.0, -6.6, -PI / 2.0, 10.0)
	printerr("SEAMS bridge: stopped at x=%.1f %s" % [e.x, "(the barrier holds)" if e.x > -180.5 else "(PAST THE BARRIER)"])
	e = await seam_walk("bridge_hug_north", -177.0, -9.0, -PI / 2.0 - 0.3, 4.0)
	printerr("SEAMS bridge north gap: x=%.1f z=%.1f %s" % [e.x, e.z, "(held)" if e.x > -180.5 else "(SLIPPED PAST)"])
	e = await seam_walk("bridge_hug_south", -177.0, -4.2, -PI / 2.0 + 0.3, 4.0)
	printerr("SEAMS bridge south gap: x=%.1f z=%.1f %s" % [e.x, e.z, "(held)" if e.x > -180.5 else "(SLIPPED PAST)"])
	e = await seam_walk("bridge_back", m.player.global_position.x, m.player.global_position.z, PI / 2.0, 4.0)
	printerr("SEAMS bridge back: x=%.1f %s" % [e.x, "(walked off again)" if e.x > -165.0 else "(STUCK ON THE DECK)"])
	# the sweeps: every free half-metre spot tries the eight ways out, at the walked surface's own height
	await stuck_scan("funicular", [-74.0, -112.0, -58.0, -98.0])
	await stuck_scan("alzina", [122.5, -97.5, 130.4, -58.0])
	await stuck_scan("bridge", [-196.0, -10.2, -154.0, -3.0])
	end_test()


func run_caps(dir: String) -> void:
	# everyone who wears a hat, close up from the front, the side and behind (hair poking through?)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("day")
	var at := Vector3(m.D.spawn.pos[0], 0.0, m.D.spawn.pos[1] - 6.0)
	place(at.x - 40.0, at.z, 0.0)
	var ids := ["pau", "joaquim", "bofarull", "pere", "dolors", "vicenc", "quima", "roser", "arnau", "sergi"]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--ids="):                     # (round 26: just these people, e.g. the workmen)
			ids = Array(a.trim_prefix("--ids=").split(","))
	for j in ids.size():
		var p := at + Vector3(j * 1.0 - ids.size() * 0.5, 0, 0)
		p.y = m.ground_at(p)
		var q: Dictionary = m.npcs.make_person(ids[j], m.game.data.NPCS[ids[j]], m.outdoor, p)
		if not q.is_empty():
			q.holder.rotation.y = 0.0
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 40.0
	cc.current = true
	for v in [["front", Vector3(0, 1.9, 6.0), Vector3(0, 1.5, 0)], ["back", Vector3(0, 1.9, -6.0), Vector3(0, 1.5, 0)],
			["side", Vector3(-9.0, 2.0, 2.5), Vector3(-2.0, 1.5, 0)]]:
		cc.global_position = at + v[1]
		cc.look_at(at + v[2], Vector3.UP)
		await get_tree().create_timer(1.2).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("caps_%s.png" % v[0]))
	end_test()


func run_hatwalk(dir: String) -> void:
	# people with hats, walking on the spot (and then idling), filmed close up: does the hat stay on the head?
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("day")
	var at := Vector3(m.D.spawn.pos[0], 0.0, m.D.spawn.pos[1] - 6.0)
	place(at.x - 40.0, at.z, 0.0)
	var ids := ["pau", "joaquim", "pere", "dolors", "vicenc", "arnau"]
	var qs := []
	for j in ids.size():
		var p := at + Vector3(j * 1.1 - ids.size() * 0.55, 0, 0)
		p.y = m.ground_at(p)
		var q: Dictionary = m.npcs.make_person(ids[j], m.game.data.NPCS[ids[j]], m.outdoor, p)
		if not q.is_empty():
			q.holder.rotation.y = PI / 2
			qs.append(q)
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 34.0
	cc.current = true
	cc.global_position = at + Vector3(0, 1.6, 6.5)
	cc.look_at(at + Vector3(0, 1.2, 0), Vector3.UP)
	# each animation sampled at 8 points through its length, frozen there (so we see its whole range)
	for anim in ["Walking", "idle"]:
		for f in 8:
			for q in qs:
				var ap: AnimationPlayer = q.m.ap
				var an: String = "Walking" if anim == "Walking" else q.m.anims.idle
				ap.play(an)
				ap.seek(ap.get_animation(an).length * f / 8.0, true)
				ap.pause()
			await get_tree().create_timer(0.15).timeout
			get_viewport().get_texture().get_image().save_png(dir.path_join("hat_%s_%d.png" % [anim, f]))
		cc.global_position = at + Vector3(-7.0, 1.6, 0.0)
		cc.look_at(at + Vector3(-2.0, 1.2, 0), Vector3.UP)
	end_test()


func run_hatlive(dir: String) -> void:
	# the real people with hats going about their day, filmed close up for a few seconds each
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("day")
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 30.0
	cc.current = true
	for id in ["dolors", "vicenc", "sergi", "pere"]:
		var q: Dictionary = m.npcs.outdoor.get(id, {})
		if q.is_empty():
			continue
		var h: Node3D = q.holder
		place(h.position.x + 3.0, h.position.z + 3.0, 0.0)
		for f in 16:
			await get_tree().create_timer(0.12).timeout
			var head := h.global_position + Vector3(0, 1.2, 0)
			cc.global_position = head + Vector3(2.2, 0.4, 2.2)
			cc.look_at(head, Vector3.UP)
			await get_tree().process_frame
			get_viewport().get_texture().get_image().save_png(dir.path_join("live_%s_%02d.png" % [id, f]))
	end_test()


func run_talkstay() -> void:
	# talking to someone who wanders: do they turn to Sandra and stay put until the talk box closes?
	await get_tree().create_timer(3.0).timeout
	for id in ["dolors", "pere", "marta"]:
		var q: Dictionary = m.npcs.outdoor.get(id, {})
		if q.is_empty():
			continue
		var h: Node3D = q.holder
		place(h.position.x + 1.4, h.position.z + 0.6, 0.0)
		await get_tree().process_frame
		m.game.talk_to(id)
		await get_tree().create_timer(0.3).timeout
		var p0 := h.position
		await get_tree().create_timer(3.0).timeout
		var to := m.player.global_position - h.global_position
		var facing := rad_to_deg(absf(angle_difference(h.rotation.y, atan2(to.x, to.z))))
		printerr("talk %s: dialog=%s moved %.2f m while talking, facing Sandra within %.0f deg" % [id, m.dlg_open, h.position.distance_to(p0), facing])
		while m.dlg_open:
			m.dialog_next()
			await get_tree().create_timer(0.1).timeout
		await get_tree().create_timer(0.5).timeout
	end_test()


func run_bump() -> void:
	# walk Sandra straight at people (standing ones and passers-by): how close does she get?
	await get_tree().create_timer(3.0).timeout
	var ids := []
	for id in m.npcs.outdoor:
		if not m.npcs.outdoor[id].is_empty():
			ids.append(id)
	var worst := 9.0
	for id in ids.slice(0, 10):
		var h: Node3D = m.npcs.outdoor[id].holder
		var tgt := h.global_position
		var yaw := 0.0
		place(tgt.x, tgt.z + 3.0, PI)
		m.vkeys[KEY_W] = true
		var dmin := 9.0
		for f in 40:
			await get_tree().create_timer(0.05).timeout
			var d := Vector2(m.player.global_position.x - h.global_position.x, m.player.global_position.z - h.global_position.z).length()
			dmin = minf(dmin, d)
		m.vkeys.clear()
		worst = minf(worst, dmin)
		printerr("bump %s: closest %.2f m" % [id, dmin])
		await get_tree().create_timer(0.3).timeout
	# passers-by
	var pb: Array = m.people.walkers if "walkers" in m.people else []
	printerr("bump worst %.2f m (bodies are 0.28 + Sandra's)" % worst)
	end_test()


func run_ui(dir: String) -> void:
	# the screen's text and panels at two window sizes: the HUD, the talk box, the journal (both pages),
	# the backpack and a shop
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var g = m.game
	for e in [["Welcome to Barcelona", "Rosa met me at the door with a key and a plant. The flat is small but the light is lovely."],
			["Alessandra's birthday", "Find a present for Alessandra. She loves torró — the shop on Girona sells it for five euros."],
			["Study Notes 1", "Received Chapter 1 of the Rambla Guide to Economics. Open it in my backpack (I) to read it."]]:
		g.S.log.append({"t": e[0], "x": e[1], "at": g.S.time})
	for id in ["apple", "croissant", "camera", "sundress", "bk_gaudi", "note1", "bottle", "bottle"]:
		g.add_item(id)
	for sz in [Vector2i(1280, 800), Vector2i(1920, 1080)]:
		get_window().size = sz
		await get_tree().create_timer(0.8).timeout
		var tag := "%d" % sz.x
		get_viewport().get_texture().get_image().save_png(dir.path_join("ui_%s_hud.png" % tag))
		m.show_dialog("Rosa", ["Benvinguda! This is your flat now — the key sticks a little, so jiggle it. The bakery downstairs opens at seven, and the woman who runs it will know your name by Friday."],
			["Thank you, Rosa!", "Where is the beach?", "Bye"])
		await get_tree().create_timer(0.4).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("ui_%s_talk.png" % tag))
		m.dlg_panel.visible = false
		m.dlg_open = false
		m.panels.open_journal()
		await get_tree().create_timer(0.4).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("ui_%s_journal.png" % tag))
		m.panels.key(KEY_RIGHT)
		await get_tree().create_timer(0.3).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("ui_%s_achievements.png" % tag))
		m.panels.close(false)
		m.panels.open_bag(2)
		await get_tree().create_timer(0.4).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("ui_%s_bag.png" % tag))
		m.panels.close(false)
		g.open_reader("note1")
		await get_tree().create_timer(0.4).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("ui_%s_reader.png" % tag))
		printerr("reader open=%s kind=%s pages=%d" % [m.panels.is_open(), m.panels.kind, m.panels.reader.get("pages", []).size()])
		m.panels.close(false)
		m.panels.open_container("vicens_cupboard")
		await get_tree().create_timer(0.4).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("ui_%s_cupboard.png" % tag))
		var n0: int = g.S.inv.size()
		m.panels.key(KEY_ENTER)
		await get_tree().create_timer(0.3).timeout
		printerr("cupboard take: bag %d -> %d" % [n0, g.S.inv.size()])
		m.panels.close(false)
		m.panels.open_bin()
		await get_tree().create_timer(0.4).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("ui_%s_bin.png" % tag))
		m.panels.close(false)
	end_test()


func run_glare(dir: String) -> void:
	# looking at the sun: midday (looking up), late afternoon, sunset; straight at it and 30 degrees off
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var times := [1000, 1240, 1285]
	var offs := [0.0, 0.5]
	if "--morning" in OS.get_cmdline_user_args():
		times = [460]                                  # (round 23, the user: an hour after sunrise)
		offs = [0.0, 0.15, 0.3, 0.5, 0.75]
	for mins in times:
		m.set_clock(mins)
		await get_tree().create_timer(0.6).timeout
		var sd: Vector3 = m.night_sky.get_shader_parameter("sun_dir")
		var yaw := atan2(sd.x, sd.z)
		for off in offs:
			place(10.0, 138.0, yaw)
			m.cam_yaw_node.rotation.y = yaw + PI + off
			m.cam_pitch_node.rotation.x = clampf(asin(sd.y) * 0.9 - 0.1, -1.1, 0.3)
			m.last_manual_cam = m.t + 100.0
			await get_tree().create_timer(1.5).timeout
			printerr("glare %d off %.1f k=%.2f seen=%.2f" % [mins, off, m.glare_k, m.glare_seen])
			get_viewport().get_texture().get_image().save_png(dir.path_join("glare_%04d_%02d.png" % [mins, int(off * 100)]))
	end_test()


func run_glaremock(dir: String) -> void:
	# (round 38) the sun's glare, the ways it could be, for the user to choose: "before" (the old veil over the whole
	# view, sun_glare.gdshader on top of the picture), and over the sky alone at three strengths
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var veil := ColorRect.new()
	veil.set_anchors_preset(Control.PRESET_FULL_RECT)
	veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var vm := ShaderMaterial.new()
	vm.shader = load("res://shaders/sun_glare.gdshader")
	veil.material = vm
	var cl := CanvasLayer.new()
	cl.layer = -1
	add_child(cl)
	cl.add_child(veil)
	# where: the promenade, a street, in the eastern wood looking out (time, x, z)
	var spots := [[1240, 10.0, 138.0], [470, 150.0, -20.0], [560, 165.0, 30.0]]
	# style: [the sky's glare (x the old veil), the old veil over everything (x), extra bloom]
	var styles := {"a_before": [0.0, 1.0, 0.0], "e_sky_as_before": [1.0, 0.0, 0.0], "f_sky_light_haze": [0.75, 0.25, 0.0],
		"g_sky_light_through": [1.0, 0.0, 0.5], "h_sky_stronger": [1.4, 0.0, 0.0]}
	var glow0: float = m.env_out.glow_intensity
	for si in spots.size():
		var sp: Array = spots[si]
		m.set_clock(float(sp[0]))
		await get_tree().create_timer(0.6).timeout
		var sd: Vector3 = m.night_sky.get_shader_parameter("sun_dir")
		var yaw := atan2(sd.x, sd.z)
		for st in styles:
			var k: Array = styles[st]
			m.glare_mul = float(k[0])
			veil.visible = float(k[1]) > 0.0
			place(float(sp[1]), float(sp[2]), yaw)
			m.cam_yaw_node.rotation.y = yaw + PI + 0.12
			m.cam_pitch_node.rotation.x = clampf(asin(sd.y) * 1.2 - 0.05, -1.1, 0.6)
			m.last_manual_cam = m.t + 100.0
			await get_tree().create_timer(1.8).timeout
			m.env_out.glow_intensity = glow0 + float(k[2]) * m.glare_k
			if veil.visible:
				var vs := get_viewport().get_visible_rect().size
				var c: Camera3D = get_viewport().get_camera_3d()
				vm.set_shader_parameter("sun_uv", c.unproject_position(c.global_position + sd * 100.0) / vs)
				vm.set_shader_parameter("strength", m.glare_k * float(k[1]))
				vm.set_shader_parameter("high", smoothstep(0.02, 0.45, sd.y))
				vm.set_shader_parameter("aspect", vs.x / vs.y)
			await get_tree().process_frame
			await get_tree().process_frame
			await get_tree().process_frame
			printerr("glaremock %d %s k=%.2f" % [si, st, m.glare_k])
			get_viewport().get_texture().get_image().save_png(dir.path_join("spot%d_%s.png" % [si, st]))
			m.env_out.glow_intensity = glow0
	end_test()


func run_spotsave() -> void:
	# (round 38, the user: Continue started her on the beach again) a save remembers where she is: out of doors, and in
	# a room; reading it back puts her there
	await get_tree().create_timer(3.0).timeout
	m.spot_ready = true
	m.teleport(Vector3(52.0, 0, -118.0), 1.0)
	await get_tree().create_timer(0.3).timeout
	# (round 40, rule 08 #82b) she does something here, then wanders off and gets stuck: the autosave keeps the place
	# where she did something, Export save (exact) the place she stands
	m.note_spot()
	m.teleport(Vector3(127.4, 0, -168.0), 1.0)
	await get_tree().create_timer(0.3).timeout
	m.game.save_game(true)
	var exact: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(m.game.SAVE_PATH)).get("at", {})
	printerr("SPOTSAVE manual (exact): %s %s" % [exact, "OK" if Vector2(float(exact.x) - 127.4, float(exact.z) + 168.0).length() < 0.2 else "WRONG"])
	m.game.save_game()
	var saved: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(m.game.SAVE_PATH)).get("at", {})
	m.teleport(Vector3(m.D.spawn.pos[0], 0, m.D.spawn.pos[1]), 0.0)
	await get_tree().create_timer(0.3).timeout
	m.game.S.at = saved
	m.restore_spot()
	await get_tree().create_timer(0.3).timeout
	var p: Vector3 = m.player.global_position
	printerr("SPOTSAVE out: saved %s, back at (%.2f, %.2f) %s" % [saved, p.x, p.z, "OK" if Vector2(p.x - 52.0, p.z + 118.0).length() < 0.2 else "WRONG"])
	var e: Dictionary = {}
	for en in m.D.entrances:
		if en.has("int") and String(en.get("id", "")) != "":
			e = en
			break
	m.enter(e)
	await get_tree().create_timer(2.0).timeout
	m.game.save_game()
	saved = JSON.parse_string(FileAccess.get_file_as_string(m.game.SAVE_PATH)).get("at", {})
	m.teleport(Vector3(m.D.spawn.pos[0], 0, m.D.spawn.pos[1]), 0.0)
	await get_tree().create_timer(0.3).timeout
	m.game.S.at = saved
	m.restore_spot()
	await get_tree().create_timer(1.0).timeout
	printerr("SPOTSAVE room: saved %s, now where=%s room=%s %s" % [saved, m.where, m.room, "OK" if m.where == "in" and m.room == String(e.int) else "WRONG"])
	# and out of the door: the autosave's place is just outside it
	m.leave()
	await get_tree().create_timer(2.0).timeout
	m.game.save_game()
	saved = JSON.parse_string(FileAccess.get_file_as_string(m.game.SAVE_PATH)).get("at", {})
	var dn := Vector2(e.normal[0], e.normal[1])
	var outside := Vector2(e.pos[0], e.pos[1]) + dn * 1.8
	printerr("SPOTSAVE out of the door: saved %s, door step (%.2f, %.2f) %s" % [saved, outside.x, outside.y,
		"OK" if saved.has("x") and Vector2(float(saved.x) - outside.x, float(saved.z) - outside.y).length() < 1.0 else "WRONG"])
	end_test()


func run_unstick(dir: String) -> void:
	# (round 39, the user: stuck against a tree or a wall, after 3 s of running she goes through) she is put just short
	# of a trunk in the eastern wood, of a thin wall and of a thick one, faces it and holds W for 5 s: how far she got
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.new = false
	var cases := []
	var best := INF
	var tree := Vector2.ZERO
	for t in m.D.get("forest_trees", []):
		var d := Vector2(t[0] - 150.0, t[1] - 0.0).length()
		if d < best:
			best = d
			tree = Vector2(t[0], t[1])
	cases.append(["tree", Vector3(tree.x, 0, tree.y + 0.6), PI])
	var thin := []
	var thick := []
	for r in m.D.blocked:
		var w: float = r[2] - r[0]
		var d2: float = r[3] - r[1]
		if r[1] < -150.0 and r[1] > -260.0 and thin.is_empty() and w > 3.0 and d2 < 0.8:
			thin = r
		if r[1] < -150.0 and r[1] > -260.0 and thick.is_empty() and w > 3.0 and d2 > 4.0:
			thick = r
	if not thin.is_empty():
		cases.append(["thin wall", Vector3((thin[0] + thin[2]) / 2.0, 0, thin[3] + 0.5), PI])
	if not thick.is_empty():
		cases.append(["thick wall", Vector3((thick[0] + thick[2]) / 2.0, 0, thick[3] + 0.5), PI])
	for c in cases:
		place(c[1].x, c[1].z, c[2])
		await get_tree().create_timer(0.5).timeout
		var s0: Vector3 = m.player.global_position
		m.vkeys[KEY_W] = true
		var passed := -1.0
		for f in 60:
			await get_tree().create_timer(0.1).timeout
			if passed < 0.0 and m.slipping:
				passed = f * 0.1
		m.vkeys.erase(KEY_W)
		await get_tree().create_timer(0.3).timeout
		var s1: Vector3 = m.player.global_position
		get_viewport().get_texture().get_image().save_png(dir.path_join("unstick_%s.png" % String(c[0]).replace(" ", "_")))
		printerr("UNSTICK %s at %s: slipped after %.1f s, went %.2f m, solid again %s" % [c[0], c[1], passed,
			Vector2(s1.x - s0.x, s1.z - s0.z).length(), not m.slipping])
	end_test()


func run_stairscam(spec: String) -> void:
	# (round 39, the user: "when I run up the stairs and the camera is over the edge a little bit, it starts jumping up
	# and down") --stairscam=<turn> : she runs up Park Güell's west side stairs with the camera turned <turn> rad off her
	# back; the camera's height every frame, and how often it jumps (a change of over 4 cm in one frame, or a reversal)
	await get_tree().create_timer(3.0).timeout
	m.game.S.new = false
	var turn := float(spec) if spec != "" else 0.6
	place(87.75, -166.6, PI)
	await get_tree().create_timer(0.8).timeout
	m.vkeys[KEY_W] = true
	var ys := []
	var tips := []
	var hits := []
	for f in 420:
		m.cam_yaw_node.rotation.y = m.model.rotation.y + PI + turn
		m.last_manual_cam = m.t + 10.0
		await get_tree().physics_frame
		ys.append(m.cam.global_position.y)
		tips.append(m.arm_tip)
		hits.append([m.arm.get_hit_length(), m.arm.spring_length, m.model.position.y, m.cam_root.global_position.y])
	m.vkeys.erase(KEY_W)
	var jumps := 0
	var revs := 0
	var biggest := 0.0
	for i in range(2, ys.size()):
		var d1: float = ys[i] - ys[i - 1]
		var d0: float = ys[i - 1] - ys[i - 2]
		biggest = maxf(biggest, absf(d1))
		if absf(d1 - d0) > 0.03:                      # (a jolt: its climb changed by over 3 cm in one frame)
			jumps += 1
			printerr("  jolt f%d dy %.3f->%.3f tip %.2f hit %.2f len %.2f model %.2f root %.2f | before: hit %.2f len %.2f model %.2f root %.2f" % [i, d0, d1, tips[i], hits[i][0], hits[i][1], hits[i][2], hits[i][3], hits[i-1][0], hits[i-1][1], hits[i-1][2], hits[i-1][3]])
		if d1 * d0 < 0.0 and absf(d1) > 0.01 and absf(d0) > 0.01:
			revs += 1
	var p: Vector3 = m.player.global_position
	printerr("STAIRSCAM turn %.2f: ended at (%.1f, %.1f), camera jolts %d, reversals %d, biggest step %.3f m, tip %.2f..%.2f" % [
		turn, p.x, p.z, jumps, revs, biggest, tips.min(), tips.max()])
	end_test()


func run_gateshots(dir: String) -> void:
	# (round 39) every Park Güell gate shut, then opening and open, from the street side, with the ticket
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.new = false
	m.game.S.flags["parkTicket"] = true
	var cc := Camera3D.new()
	add_child(cc)
	var views := [[Vector3(106.0, 0, -132.5), Vector3(106.0, 0, -142.0)], [Vector3(57.0, 0, -157.0), Vector3(63.0, 0, -157.0)],
		[Vector3(178.0, 0, -227.0), Vector3(171.0, 0, -227.2)], [Vector3(187.0, 0, -188.5), Vector3(180.0, 0, -188.4)]]
	for gi in m.north.gates.size():
		var v: Array = views[gi]
		var from: Vector3 = v[0]
		var to: Vector3 = v[1]
		place(from.x, from.z, 0.0)
		await get_tree().create_timer(0.5).timeout
		from.y = m.ground_at(from) + 1.7
		to.y = m.ground_at(to) + 1.0
		cc.global_position = from
		cc.look_at(to, Vector3.UP)
		cc.current = true
		for c in m.get_children():
			if c is CanvasLayer:
				c.visible = false
		await get_tree().create_timer(0.6).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("gate%d_a_shut.png" % gi))
		m.north.open_gate(gi)
		await get_tree().create_timer(1.2).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("gate%d_b_opening.png" % gi))
		await get_tree().create_timer(2.5).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("gate%d_c_open.png" % gi))
		printerr("GATESHOT %d f=%.2f" % [gi, float(m.north.gates[gi].f)])
	end_test()


func run_besides(dir: String) -> void:
	# (round 39) Sandra beside chosen people (--ids=a,b), side by side, to compare heights and see faces close up
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("golden")
	var ids := ["marc", "fiona"]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--ids="):
			ids = Array(a.substr(6).split(","))
	var at := Vector3(m.D.spawn.pos[0] - 40.0, 0.0, m.D.spawn.pos[1] - 6.0)
	place(at.x, at.z, 0.0)
	m.model.rotation.y = 0.0
	for j in ids.size():
		var p := at + Vector3((j + 1) * 0.9, 0, 0)
		p.y = m.ground_at(p)
		var q: Dictionary = m.npcs.make_person(String(ids[j]), m.game.data.NPCS[String(ids[j])], m.outdoor, p)
		if not q.is_empty():
			q.holder.rotation.y = 0.0
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 40.0
	cc.current = true
	var mid := at + Vector3(ids.size() * 0.45, 0, 0)
	for v in [["row", Vector3(0, 1.2, 4.2), Vector3(0, 1.0, 0)], ["faces", Vector3(0, 1.6, 2.2), Vector3(0, 1.5, 0)]]:
		cc.global_position = mid + v[1]
		cc.look_at(mid + v[2], Vector3.UP)
		await get_tree().create_timer(1.5).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("besides_%s.png" % v[0]))
	end_test()


func run_touchprobe(spec: String) -> void:
	# (round 39) --touchprobe=x,z : what solid shapes are within 0.6 m of her there (body, shape, where, size)
	await get_tree().create_timer(3.0).timeout
	var v := spec.split(",")
	place(float(v[0]), float(v[1]), 0.0)
	await get_tree().create_timer(0.3).timeout
	var q := PhysicsShapeQueryParameters3D.new()
	var ball := SphereShape3D.new()
	ball.radius = 0.6
	q.shape = ball
	q.transform = Transform3D(Basis(), m.player.global_position + Vector3(0, 0.9, 0))
	q.collision_mask = m.LAYER_BODY
	q.exclude = [m.player.get_rid()]
	for hit in m.get_world_3d().direct_space_state.intersect_shape(q, 16):
		var body: Object = hit.collider
		var cs: CollisionShape3D = body.shape_owner_get_owner(body.shape_find_owner(hit.shape))
		var what := "tree_body" if body == m.tree_body else str(body)
		var sz := ""
		if cs.shape is BoxShape3D:
			sz = str((cs.shape as BoxShape3D).size)
		elif cs.shape is CylinderShape3D:
			sz = "post r %.2f" % (cs.shape as CylinderShape3D).radius
		else:
			sz = cs.shape.get_class()
		printerr("TOUCH %s at %s %s" % [what, cs.global_position, sz])
	end_test()


func run_mapshot(path: String) -> void:
	# the whole world from straight above at midday, for the map (M): an orthographic picture of the
	# walkable map (scene.json "walk"), 12 pixels to the metre; tools/stylise_map.py then paints it up
	await get_tree().create_timer(4.0).timeout
	m.set_clock(780)
	m.clock_light = false
	var W: Dictionary = m.D.walk
	var wm: float = W.x1 - W.x0
	var hm: float = W.z1 - W.z0
	var px := 12.0
	var vp := SubViewport.new()
	vp.size = Vector2i(int(wm * px), int(hm * px))
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.msaa_3d = Viewport.MSAA_4X
	if "--mapnomsaa" in OS.get_cmdline_user_args():
		vp.msaa_3d = Viewport.MSAA_DISABLED       # (round 41: the walk grew to ~31 million pixels; with 4× smoothing the GPU timed out)
	add_child(vp)
	var cc := Camera3D.new()
	cc.projection = Camera3D.PROJECTION_ORTHOGONAL
	cc.size = hm
	cc.near = 1.0
	cc.far = 700.0
	vp.add_child(cc)
	cc.global_position = Vector3((W.x0 + W.x1) / 2.0, 320.0, (W.z0 + W.z1) / 2.0)
	cc.look_at(cc.global_position + Vector3(0, -1, 0), Vector3(0, 0, -1))
	cc.current = true
	# a clean picture: no haze, people or glows; long shadows switched for short, soft ones
	m.env_out.fog_enabled = false
	m.env_out.volumetric_fog_enabled = false
	m.sun.directional_shadow_max_distance = 520.0
	m.sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	m.model.visible = false
	for n in [m.people, m.npcs, m.wildlife, m.street]:
		for c in n.get_children():
			if c is Node3D:
				c.visible = false
	for p in m.people.people:
		p.holder.visible = false
	for id in m.npcs.outdoor:
		if not m.npcs.outdoor[id].is_empty():
			m.npcs.outdoor[id].holder.visible = false
	for g in m.door_glows:
		g.mat.set_shader_parameter("strength", 0.0)
	for i in 90:
		await get_tree().process_frame
		for g in m.door_glows:
			g.mat.set_shader_parameter("strength", 0.0)
		for p in m.people.people:
			p.holder.visible = false
		for id in m.npcs.outdoor:
			if not m.npcs.outdoor[id].is_empty():
				m.npcs.outdoor[id].holder.visible = false
	vp.get_texture().get_image().save_png(path)
	var meta := FileAccess.open(path.get_basename() + ".json", FileAccess.WRITE)
	meta.store_string(JSON.stringify({"x0": W.x0, "z0": W.z0, "w_m": wm, "h_m": hm}))
	meta.close()
	printerr("mapshot %s: %dx%d px, %.1f x %.1f m from (%.2f, %.2f)" % [path, vp.size.x, vp.size.y, wm, hm, W.x0, W.z0])
	end_test()


func run_clearance() -> void:
	# passers-by: do they keep clear of café tables, benches, trees and lamps? Every one of them, all along
	# their way (stepped through, not waited for): the closest each comes to anything solid
	await get_tree().create_timer(3.0).timeout
	var worst := []
	var through := 0
	for p in m.people.people:
		var closest := 99.0
		var what := Vector3.ZERO
		for i in 400:
			p.t = i / 399.0
			m.people.place(p)
			var q: Vector3 = p.holder.position
			for bl in m.people.blockers:
				var dd: float = Vector2(bl.x - q.x, bl.y - q.z).length() - bl.z
				if dd < closest:
					closest = dd
					what = bl
		if closest < 0.15:
			through += 1
			printerr("  brushes the thing at (%.1f, %.1f) r %.2f, walking %s -> %s" % [what.x, what.y, what.z, str(p.a), str(p.b)])
		worst.append(snappedf(closest, 0.01))
	worst.sort()
	printerr("clearance: %d walkers, %d brush through something; closest approaches %s" % [worst.size(), through, str(worst.slice(0, 14))])
	end_test()


func run_debugmenu() -> void:
	# P: the debug menu; money, the bike, a time, and a trip to the Sagrada Família
	await get_tree().create_timer(3.0).timeout
	var money0: int = m.game.S.money
	m.input_key(KEY_P)
	await get_tree().process_frame
	printerr("debug open=%s rows=%s" % [m.panels.kind, str(m.panels.debug_rows.map(func(r): return r[0]))])
	m.panels.sel = 2
	m.input_key(KEY_ENTER)
	m.panels.sel = 4
	m.input_key(KEY_ENTER)
	m.panels.sel = 1
	m.input_key(KEY_ENTER)
	await get_tree().process_frame
	m.panels.sel = 5
	m.input_key(KEY_ENTER)
	await get_tree().process_frame
	printerr("money +%d, bike=%s, clock=%d" % [m.game.S.money - money0, m.game.S.has_bike, int(m.game.S.time)])
	m.input_key(KEY_P)
	m.panels.sel = 0
	m.input_key(KEY_ENTER)
	await get_tree().process_frame
	var rows: Array = m.panels.debug_rows
	for i in rows.size():
		if String(rows[i][0]).begins_with("Sagrada"):
			m.panels.sel = i
			break
	m.input_key(KEY_ENTER)
	await get_tree().create_timer(1.0).timeout
	printerr("teleported to %s (%s), panel=%s" % [m.player.global_position, m.street_name(m.player.global_position), m.panels.kind])
	end_test()


func run_bikecam(dir: String) -> void:
	# round 20e: the camera as she gets on a bike and off it again, a line every tenth of a second
	# (how far back it is, where it is, and how far it moved since the last line), to compare the two
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var bk: Node3D = m.street.bikes[0]
	bk.position = Vector3(99.0, 0.0, -16.5)          # (on the meadow, clear of walls)
	bk.rotation.y = 0.0
	var side := bk.global_transform.basis.x
	place(bk.position.x + side.x * 0.8, bk.position.z + side.z * 0.8, atan2(-side.x, -side.z))
	await get_tree().create_timer(1.5).timeout
	for what in ["on", "off"]:
		if what == "off":
			m.vkeys[KEY_W] = true
			await get_tree().create_timer(2.0).timeout
			m.vkeys.clear()
			await get_tree().create_timer(2.5).timeout
		var last := m.cam.global_position
		if what == "on":
			print("BIKECAM paused=%s busy=%s dlg=%s" % [get_tree().paused, m.busy, m.dlg_open])
			m.street.mount(bk)
		else:
			m.street.dismount()
		for i in 25:
			if i % 3 == 0:
				get_viewport().get_texture().get_image().save_png(dir.path_join("%s_%02d.png" % [what, i]))
			var c := get_viewport().get_camera_3d().global_position
			print("BIKECAM %s t=%.1f  back %.2f  yaw %.0f  cam (%.2f, %.2f, %.2f)  moved %.2f  her (%.2f, %.2f)" % [what, i * 0.1, m.arm.spring_length,
				rad_to_deg(m.cam_yaw_node.rotation.y), c.x, c.y, c.z, c.distance_to(last), m.player.global_position.x, m.player.global_position.z])
			last = c
			await get_tree().create_timer(0.1).timeout
		await get_tree().create_timer(1.0).timeout
	end_test()


func run_rope() -> void:
	# round 20e: ride at the rope round the thick of the wood from outside, at every eighth length of it, and
	# see where the bike stops: it should be at the rope (between the two trees), not before it
	await get_tree().create_timer(3.0).timeout
	var bk: Node3D = m.street.bikes[0]
	var ropes: Array = m.D.get("bike_rope", {}).get("ropes", [])
	var at_rope := 0
	var early := 0
	var through := 0
	var tried := 0
	for k in range(0, ropes.size(), 8):
		var r: Array = ropes[k]
		var a := Vector2(r[0], r[1])
		var b := Vector2(r[2], r[3])
		var mid := (a + b) / 2.0
		var nrm := (b - a).orthogonal().normalized()
		if m.no_bike_at(Vector3(mid.x + nrm.x * 1.5, 0, mid.y + nrm.y * 1.5)):
			nrm = -nrm
		var s0 := mid + nrm * 4.0
		if m.no_bike_at(Vector3(s0.x, 0, s0.y)) or m.near_trunk(Vector3(s0.x, 0, s0.y), 1.2):
			continue
		tried += 1
		if m.street.riding:
			m.street.dismount()
			await get_tree().create_timer(0.2).timeout
		bk.position = Vector3(s0.x, 0, s0.y)
		bk.rotation.y = 0.0
		place(s0.x, s0.y, 0.0)
		await get_tree().physics_frame
		m.street.mount(bk)
		await get_tree().physics_frame
		place(s0.x, s0.y, atan2(-nrm.x, -nrm.y))
		m.vkeys[KEY_W] = true
		await get_tree().create_timer(3.0).timeout
		m.vkeys.clear()
		var e := Vector2(m.player.global_position.x, m.player.global_position.z)
		var past := (e - mid).dot(-nrm)              # how far past the rope's line (negative: short of it)
		var hit := ""
		for j in m.player.get_slide_collision_count():
			var col := m.player.get_slide_collision(j).get_collider()
			hit += " layer%d" % col.collision_layer if col else ""
		var verdict := "AT ROPE" if past > -1.6 and past < 0.3 else ("THROUGH" if past >= 0.3 else "EARLY")
		match verdict:
			"AT ROPE": at_rope += 1
			"THROUGH": through += 1
			_: early += 1
		print("ROPE %3d  gap %.1f m  stopped %.2f m %s the rope  %s  hits:%s  at tile (%.1f, %.1f)" % [k, a.distance_to(b), absf(past),
			"past" if past > 0 else "short of", verdict, hit, e.x / 3.3 + 55.0, e.y / 3.3 + 45.0])
	print("ROPE SUMMARY tried %d: at the rope %d, short of it %d, through it %d" % [tried, at_rope, early, through])
	# the closed-off pocket west of the long path, and the trees the user left out of the rope
	for c in [["the pocket", Vector2(123.0, -60.2)], ["left out (north-west spike)", Vector2(117.0, -110.0)], ["left out (south edge)", Vector2(177.2, 125.5)]]:
		print("ROPE no-bike at %s: %s" % [c[0], m.no_bike_at(Vector3(c[1].x, 0, c[1].y))])
	end_test()


func to_window(p: Vector2) -> Vector2:
	# (a point on the game's laid-out screen, as the window's own pixels: what a real finger reports)
	return get_tree().root.get_final_transform() * p


func finger(i: int, p: Vector2, down: bool) -> void:
	var e := InputEventScreenTouch.new()
	e.index = i
	e.position = to_window(p)
	e.pressed = down
	Input.parse_input_event(e)


func drag(i: int, from: Vector2, by: Vector2, steps := 10) -> void:
	for k in steps:
		var e := InputEventScreenDrag.new()
		e.index = i
		e.relative = get_tree().root.get_final_transform().basis_xform(by / steps)
		e.position = to_window(from + by * (k + 1) / steps)
		Input.parse_input_event(e)
		await get_tree().process_frame


func tap(id: String) -> void:
	var p: Vector2 = m.touch_pad.buttons[id].rect.get_center()
	finger(0, p, true)
	await get_tree().create_timer(0.12).timeout
	finger(0, p, false)
	await get_tree().create_timer(0.5).timeout


func run_touchtest(dir: String) -> void:
	# round 20e: the on-screen controls, pressed with (pretend) fingers as a player on a phone would
	# (run with --touch)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	if m.touch_pad == null:
		print("TOUCH no on-screen controls (run with --touch)")
		end_test()
		return
	place(m.D.spawn.pos[0], m.D.spawn.pos[1] - 6.0, PI)
	await get_tree().create_timer(1.0).timeout
	print("TOUCH window %s  laid out %s  upright=%s deck=%.0f  BAG at %s  up at %s" % [get_tree().root.size, get_viewport().get_visible_rect().size,
		m.touch_pad.portrait, m.touch_pad.deck, m.touch_pad.buttons.BAG.rect, m.touch_pad.buttons.up.rect])
	await shot(dir, "layout")
	var B: Dictionary = m.touch_pad.buttons
	# walk: hold the pad's up
	var p0 := m.player.global_position
	finger(0, B.up.rect.get_center(), true)
	await get_tree().create_timer(1.5).timeout
	finger(0, B.up.rect.get_center(), false)
	await get_tree().create_timer(0.4).timeout
	print("TOUCH pad up 1.5 s: walked %.1f m" % p0.distance_to(m.player.global_position))
	# look round: off, a drag does nothing; LOOK on, it turns the camera; LOOK off again
	var mid := get_viewport().get_visible_rect().size * Vector2(0.5, 0.45)
	var y0: float = m.cam_yaw_node.rotation.y
	finger(1, mid, true)
	await drag(1, mid, Vector2(220, 0))
	finger(1, mid + Vector2(220, 0), false)
	print("TOUCH drag with LOOK off: camera turned %.0f deg" % rad_to_deg(m.cam_yaw_node.rotation.y - y0))
	await tap("LOOK")
	y0 = m.cam_yaw_node.rotation.y
	var pitch0: float = m.cam_pitch_node.rotation.x
	finger(1, mid, true)
	await drag(1, mid, Vector2(220, 60))
	finger(1, mid + Vector2(220, 60), false)
	print("TOUCH drag with LOOK on: camera turned %.0f deg, tilted %.0f deg  (look_on=%s)" % [rad_to_deg(m.cam_yaw_node.rotation.y - y0),
		rad_to_deg(m.cam_pitch_node.rotation.x - pitch0), m.touch_pad.look_on])
	await shot(dir, "look_on")
	# walk and look at once: one thumb on the pad, the other dragging
	p0 = m.player.global_position
	y0 = m.cam_yaw_node.rotation.y
	finger(0, B.up.rect.get_center(), true)
	finger(1, mid, true)
	await drag(1, mid, Vector2(-160, 0), 30)
	await get_tree().create_timer(0.8).timeout
	finger(1, mid + Vector2(-160, 0), false)
	finger(0, B.up.rect.get_center(), false)
	await get_tree().create_timer(0.3).timeout
	print("TOUCH walk + look together: walked %.1f m, camera turned %.0f deg" % [p0.distance_to(m.player.global_position), rad_to_deg(m.cam_yaw_node.rotation.y - y0)])
	await tap("LOOK")
	print("TOUCH LOOK again: look_on=%s" % m.touch_pad.look_on)
	# the buttons
	await tap("MAP")
	print("TOUCH MAP: map open=%s" % m.map_panel.visible)
	await shot(dir, "map")
	await tap("B")
	print("TOUCH B: map open=%s" % m.map_panel.visible)
	await tap("BAG")
	print("TOUCH BAG: panel open=%s (%s)" % [m.panels.is_open(), m.panels.kind])
	await tap("right")
	await shot(dir, "bag")
	await tap("B")
	print("TOUCH B: panel open=%s" % m.panels.is_open())
	await tap("LOG")
	print("TOUCH LOG: journal open=%s %s" % [m.panels.is_open(), m.panels.kind])
	await tap("B")
	await tap("DEBUG")
	print("TOUCH DEBUG: panel open=%s (%s)" % [m.panels.is_open(), m.panels.kind])
	await shot(dir, "debug")
	await tap("down")
	await tap("B")
	print("TOUCH B: panel open=%s" % m.panels.is_open())
	await tap("MENU")
	print("TOUCH MENU: talk box open=%s  %s" % [m.dlg_open, m.dlg_who.text])
	await shot(dir, "menu")
	await tap("down")
	await tap("B")
	print("TOUCH B: talk box open=%s" % m.dlg_open)
	await tap("BIKE")
	print("TOUCH BIKE: riding=%s" % (m.street.riding != null))
	# talking: walk up to someone and press A
	end_test()


func run_touchtoggle() -> void:
	# the debug menu's switch: touch controls on, then off again
	await get_tree().create_timer(3.0).timeout
	m.set_touch(true)
	await get_tree().create_timer(0.5).timeout
	print("TOGGLE on: pad=%s emulate=%s" % [m.touch_pad != null, Input.emulate_touch_from_mouse])
	m.set_touch(false)
	await get_tree().create_timer(0.5).timeout
	print("TOGGLE off: pad=%s emulate=%s scale=%s" % [m.touch_pad != null, Input.emulate_touch_from_mouse, get_tree().root.content_scale_size])
	end_test()


func run_lean(dir: String) -> void:
	# round 21: how far Sandra leans (her neck against her hips, seen from the side: + forward) as she stands,
	# a line every fifth of a second, and side-on pictures at the most leaning-back and most upright moments
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	place(m.D.spawn.pos[0], m.D.spawn.pos[1] - 6.0, PI / 2.0, 0.0)
	await get_tree().create_timer(2.0).timeout
	var cc := Camera3D.new()                          # (side on, from her left, at her height)
	add_child(cc)
	cc.fov = 30.0
	var at := m.player.global_position
	var fwd := m.model.global_basis.z.normalized()
	var left := fwd.cross(Vector3.UP).normalized()
	cc.global_position = at + left * 6.5 + Vector3(0, 0.6, 0)
	cc.look_at(at + Vector3(0, 0.6, 0), Vector3.UP)
	var sk: Skeleton3D = m.model.find_children("*", "Skeleton3D", true, false)[0]
	var hips := sk.find_bone(m.street_bone(sk, "Hips"))
	var neck := sk.find_bone(m.street_bone(sk, "Neck"))
	var feet := [sk.find_bone(m.street_bone(sk, "LeftFoot")), sk.find_bone(m.street_bone(sk, "RightFoot"))]
	var vals := []
	var whole := []
	for i in 40:
		cc.current = true
		var h := sk.global_transform * sk.get_bone_global_pose(hips).origin
		var n := sk.global_transform * sk.get_bone_global_pose(neck).origin
		var f: Vector3 = (sk.global_transform * sk.get_bone_global_pose(feet[0]).origin + sk.global_transform * sk.get_bone_global_pose(feet[1]).origin) / 2.0
		var d := n - h
		vals.append(rad_to_deg(atan2(d.dot(fwd), d.y)))
		var e := n - f
		whole.append(rad_to_deg(atan2(e.dot(fwd), e.y)))
		if i % 5 == 0:
			get_viewport().get_texture().get_image().save_png(dir.path_join("lean_%02d.png" % i))
		await get_tree().create_timer(0.2).timeout
	print("LEAN standing, 8 s, + forward: back (hips to neck) %s" % [vals.map(func(v): return snappedf(v, 0.1))])
	print("LEAN whole (feet to neck) %s" % [whole.map(func(v): return snappedf(v, 0.1))])
	end_test()


func run_hairmove(dir: String) -> void:
	# round 21: her hair close up from behind and the side as she sets off running, turns and stops (when it
	# sways most), to look for see-through specks
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	place(m.D.spawn.pos[0], m.D.spawn.pos[1] - 4.0, PI)
	m.cam_len = 2.2
	await get_tree().create_timer(1.0).timeout
	m.vkeys[KEY_W] = true
	for i in 6:
		await get_tree().create_timer(0.25).timeout
		if i == 3:
			m.vkeys[KEY_D] = true
		get_viewport().get_texture().get_image().save_png(dir.path_join("hair_%d.png" % i))
	m.vkeys.clear()
	await get_tree().create_timer(0.15).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("hair_stop.png"))
	print("HAIRMOVE offset %s" % m.hair_offset)
	end_test()


func run_doorcam() -> void:
	# round 21: the camera through a door keeps the player's angle. Turn it 60 degrees round and tip it, walk
	# into a shop and out again, and into the basilica and out
	await get_tree().create_timer(3.0).timeout
	for want in ["Carrefour Express", "Sagrada"]:
		var e: Dictionary = {}
		for d in m.D.entrances:
			if String(d.name).begins_with(want):
				e = d
				break
		var n := Vector2(e.normal[0], e.normal[1])
		place(e.pos[0] + n.x * 2.5, e.pos[1] + n.y * 2.5, atan2(-n.x, -n.y))
		await get_tree().create_timer(0.5).timeout
		m.turn_camera(deg_to_rad(60.0), -0.25)
		var before := Vector2(rad_to_deg(wrapf(m.cam_yaw_node.rotation.y - (m.model.rotation.y + PI), -PI, PI)), m.cam_pitch_node.rotation.x)
		m.enter(e)                                    # (as walking into the door does)
		await get_tree().create_timer(1.5).timeout
		var inside := Vector2(rad_to_deg(wrapf(m.cam_yaw_node.rotation.y - (m.model.rotation.y + PI), -PI, PI)), m.cam_pitch_node.rotation.x)
		m.leave()
		await get_tree().create_timer(1.5).timeout
		var after := Vector2(rad_to_deg(wrapf(m.cam_yaw_node.rotation.y - (m.model.rotation.y + PI), -PI, PI)), m.cam_pitch_node.rotation.x)
		print("DOORCAM %s: before (turn %.0f deg, tip %.2f)  inside (%.0f, %.2f, free camera=%s)  after (%.0f, %.2f)" % [want, before.x, before.y,
			inside.x, inside.y, m.free_cam() if m.where == "in" else "-", after.x, after.y])
	end_test()


func side_cam(at: Vector3, fwd: Vector3, dist := 7.5, h := 0.6) -> Camera3D:
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 34.0
	var left := fwd.cross(Vector3.UP).normalized()
	cc.global_position = at + left * dist + Vector3(0, h, 0)
	cc.look_at(at + Vector3(0, h, 0), Vector3.UP)
	cc.current = true
	return cc


func run_bikesize(dir: String) -> void:
	# round 21: the bike against Sandra, side on: standing beside her own bike, then riding it, then stopped on it
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.has_bike = true
	var p := Vector3(m.D.spawn.pos[0], 0, m.D.spawn.pos[1] - 8.0)
	place(p.x, p.z, PI / 2.0)
	await get_tree().create_timer(0.5).timeout
	m.bike_key()                                       # on
	await get_tree().create_timer(0.5).timeout
	m.bike_key()                                       # and off: she steps off beside it
	await get_tree().create_timer(1.0).timeout
	var fwd := Vector3(1, 0, 0)
	var cc := side_cam(m.player.global_position, fwd)
	for i in 30:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("beside.png"))
	m.bike_key()
	await get_tree().create_timer(0.6).timeout
	m.vkeys[KEY_W] = true
	await get_tree().create_timer(0.9).timeout
	var left := fwd.cross(Vector3.UP).normalized()
	for i in 8:
		cc.global_position = m.player.global_position + left * 7.5 + Vector3(0, 0.6, 0)
		cc.look_at(m.player.global_position + Vector3(0, 0.6, 0), Vector3.UP)
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("riding.png"))
	m.vkeys.clear()
	await get_tree().create_timer(2.0).timeout
	cc.queue_free()
	cc = side_cam(m.player.global_position, fwd)
	for i in 30:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("stopped.png"))
	print("BIKESIZE done, riding=%s" % (m.street.riding != null))
	end_test()


func run_churchdoor(dir: String) -> void:
	# round 21: from inside the basilica, the corridor out of each door with the light at its end; walk into it
	# and note how far in she is when she comes out into the street
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	for side in ["bottom", "top"]:
		var e: Dictionary = {}
		for d in m.D.entrances:
			if d.get("int", "") == "int_sagrada" and d.get("room_side", "bottom") == side:
				e = d
		await go_in(e)
		var R: Dictionary = m.D.interiors["int_sagrada"]
		var O: Vector3 = m.room_base("int_sagrada")
		var mid: float = (R.exit[0] + R.exit[1]) / 2.0
		var z0: float = R.h - 6.0 if side == "bottom" else 7.0
		var face := 0.0 if side == "bottom" else PI
		place(O.x + mid, O.z + z0, face)
		m.cam_pitch_node.rotation.x = -0.1
		await get_tree().create_timer(1.0).timeout
		get_viewport().get_texture().get_image().save_png(dir.path_join("corridor_%s.png" % side))
		m.vkeys[KEY_W] = true
		var deepest := -99.0
		for i in 300:
			await get_tree().physics_frame
			if m.where != "in":
				break
			var lz: float = m.player.global_position.z - O.z
			deepest = maxf(deepest, (lz - R.h) if side == "bottom" else (1.0 - lz))
		m.vkeys.clear()
		var lp: Vector3 = m.player.global_position - O
		print("CHURCHDOOR %s: out=%s, she was at most %.2f m past the threshold (now at x %.2f z %.2f; door %s, h %s)" % [side, m.where == "out", deepest, lp.x, lp.z, R.exit, R.h])
		await get_tree().create_timer(1.5).timeout
	end_test()


func run_dogride(dir: String) -> void:
	# round 22: Trufa, once she knows Sandra: left 7 m behind, she catches up and trots alongside (gap and side
	# printed every half second); Sandra walks into her and nudges her along; then the bike: Trufa hops into
	# its basket, rides, and hops out again. Side-on pictures of each.
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.has_bike = true
	var tr: Node3D = m.street.trufa
	var p := Vector3(1.0 * 3.3 - 20.0, 0, 11.4 * 3.3)   # (round 24: Sandra's street; the old spot by the beach is sand now)
	place(p.x, p.z, PI / 2.0)                          # facing +x along the street
	tr.position = Vector3(p.x - 7.0, m.ground_at(p), p.z + 0.5)
	tr.state = tr.FOLLOW
	tr.trail.clear()
	await get_tree().create_timer(0.3).timeout
	m.vkeys[KEY_W] = true
	for i in 8:
		await get_tree().create_timer(0.5).timeout
		var rel: Vector3 = tr.position - m.player.global_position
		print("DOGRIDE walk t=%.1f gap=%.2f ahead=%.2f side=%.2f her=%.2f sandra=%.2f" % [(i + 1) * 0.5, Vector2(rel.x, rel.z).length(),
			rel.x, rel.z, tr.speed, absf(m.speed)])
	var cc := side_cam(m.player.global_position, Vector3(1, 0, 0))
	cc.global_position = m.player.global_position + Vector3(0.0, 1.4, -4.5)
	cc.look_at(m.player.global_position + Vector3(0, 0.5, 0), Vector3.UP)
	for i in 3:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("1_alongside.png"))
	m.vkeys.clear()
	cc.queue_free()
	await get_tree().create_timer(1.5).timeout
	# walk into her: stand her right ahead of Sandra
	var f := Vector3(sin(m.model.rotation.y), 0, cos(m.model.rotation.y))
	tr.state = tr.STAY
	tr.position = m.player.global_position + f * 1.2
	await get_tree().create_timer(0.5).timeout
	var before: Vector3 = tr.position
	m.vkeys[KEY_W] = true
	await get_tree().create_timer(1.0).timeout
	var rel2: Vector3 = tr.position - m.player.global_position
	print("DOGRIDE nudge: moved %.2f m, now %.2f m from Sandra" % [before.distance_to(tr.position), Vector2(rel2.x, rel2.z).length()])
	cc = side_cam(m.player.global_position, f)
	for i in 3:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("2_nudged.png"))
	m.vkeys.clear()
	cc.queue_free()
	place(p.x, p.z, PI / 2.0)                          # (back where the bike test knows she can ride)
	tr.position = Vector3(p.x - 1.0, m.ground_at(p), p.z + 0.8)
	tr.state = tr.FOLLOW
	tr.trail.clear()
	await get_tree().create_timer(1.5).timeout
	# (round 23) she sits when told to stay: side on, low, to see her legs against the ground
	tr.state = tr.STAY
	await get_tree().create_timer(1.2).timeout
	f = Vector3(sin(m.model.rotation.y), 0, cos(m.model.rotation.y))
	cc = Camera3D.new()
	add_child(cc)
	var tp: Vector3 = tr.global_position
	for i in 6:
		cc.global_position = tp + f.cross(Vector3.UP).normalized() * 1.6 + Vector3(0, 0.25, 0)
		cc.look_at(tp + Vector3(0, 0.2, 0), Vector3.UP)
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("2b_sitting.png"))
	print("DOGRIDE sitting: body %.3f above the ground" % [tr.position.y - m.ground_at(tr.position)])
	cc.queue_free()
	tr.state = tr.FOLLOW
	await get_tree().create_timer(1.0).timeout
	m.bike_key()
	# (round 23) the run-up and the pounce: a picture every 0.15 s, from the side
	f = Vector3(sin(m.model.rotation.y), 0, cos(m.model.rotation.y))
	cc = Camera3D.new()
	add_child(cc)
	for k in 10:
		for j in 5:                                    # (a picture every 5 physics frames, ~0.08 s of her run)
			cc.global_position = m.player.global_position + f.cross(Vector3.UP).normalized() * 3.2 + Vector3(0, 0.9, 0) - f * 0.4
			cc.look_at(m.player.global_position + Vector3(0, 0.6, 0) - f * 0.4, Vector3.UP)
			cc.current = true
			await get_tree().physics_frame
		await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png(dir.path_join("3_pounce_%d.png" % k))
		print("DOGRIDE pounce %d: run_up=%.2f basket_in=%s in_basket=%.2f state=%d speed=%.1f h=%.2f d_seat=%.2f riding=%s" % [k, tr.run_up, tr.basket_in, tr.in_basket,
			tr.state, tr.speed, tr.global_position.y, tr.global_position.distance_to(m.street.riding.dog_seat.global_position) if m.street.riding else -1.0,
			m.street.riding != null])
	cc.queue_free()
	await get_tree().create_timer(0.8).timeout
	print("DOGRIDE in basket=%.2f, %.2f m from the seat" % [tr.in_basket, tr.global_position.distance_to(m.street.riding.dog_seat.global_position) - 0.139])
	f = Vector3(sin(m.model.rotation.y), 0, cos(m.model.rotation.y))
	cc = side_cam(m.player.global_position, f)
	for i in 20:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("3_basket.png"))
	cc.queue_free()
	m.vkeys[KEY_W] = true
	await get_tree().create_timer(1.6).timeout
	print("DOGRIDE riding: %.2f m from the seat at %.1f m/s" % [tr.position.distance_to(m.street.riding.dog_seat.global_position), absf(m.speed)])
	var left := f.cross(Vector3.UP).normalized()
	cc = Camera3D.new()
	add_child(cc)
	for i in 6:
		cc.global_position = m.player.global_position - left * 3.5 + Vector3(0, 1.0, 0) + f * 0.6
		cc.look_at(m.player.global_position + Vector3(0, 0.8, 0) + f * 0.6, Vector3.UP)
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("4_riding.png"))
	cc.queue_free()
	m.vkeys.clear()
	await get_tree().create_timer(2.0).timeout
	m.bike_key()
	await get_tree().create_timer(1.0).timeout
	var rel3: Vector3 = tr.position - m.player.global_position
	print("DOGRIDE off: in basket=%.2f, %.2f m from Sandra, height above ground %.2f" % [tr.in_basket, Vector2(rel3.x, rel3.z).length(),
		tr.position.y - m.ground_at(tr.position)])
	f = Vector3(sin(m.model.rotation.y), 0, cos(m.model.rotation.y))
	cc = side_cam(m.player.global_position, f)
	for i in 20:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("5_off.png"))
	end_test()


func walk_to(target: Vector3, speed := 3.0) -> void:
	# (Sandra walks there in a straight line, as if steered: for scenes where someone follows her)
	var p: Vector3 = m.player.global_position
	var n := int(p.distance_to(target) / speed * 30.0)
	for i in n:
		var q := p.lerp(target, float(i + 1) / n)
		q.y = m.ground_at(q)
		m.player.global_position = q
		m.model.rotation.y = atan2(target.x - p.x, target.z - p.z)
		m.speed = speed
		await get_tree().physics_frame
		await get_tree().physics_frame
	m.speed = 0.0


func run_thief(dir: String) -> void:
	# round 22: the pickpocket's arrest, played through: robbed, report it, Agent Bofarull follows, talk to Manolo,
	# the agent runs over and handcuffs him, things back; in and out of a building: Manolo gone, the agent home
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var g := m.game
	for f in ["manoloCaught", "manoloGone"]:
		g.S.flags.erase(f)
	g.S.missions.erase("thief")
	g.S.stolen.clear()
	g.add_item("apple")
	var mq: Dictionary = m.npcs.outdoor.manolo
	var oq: Dictionary = m.npcs.outdoor.bofarull
	var mp: Vector3 = mq.holder.position
	place(mp.x, mp.z - 1.4, 0.0)
	await talk("manolo")
	printerr("THIEF stolen=", g.S.stolen, " pending=", g.S.pending != null)
	place(mp.x, mp.z - 36.0, PI)
	for i in 30:
		await get_tree().process_frame
	await talk_through(0, true)
	var op: Vector3 = oq.holder.position
	place(op.x, op.z + 1.4, PI)
	await talk("bofarull", 0)
	printerr("THIEF mission active=", g.m_active("thief"), " officer mode=", oq.get("mode", ""), " objective: ", g.objective_text())
	var to := mp + (op - mp).normalized() * 1.4
	await walk_to(mp.lerp(op, 0.5))
	printerr("THIEF halfway: officer %.1f m behind" % oq.holder.position.distance_to(m.player.global_position))
	var cc := Camera3D.new()
	add_child(cc)
	var back: Vector3 = (op - mp).normalized()
	cc.global_position = m.player.global_position + back * 3.5 + Vector3(2.5, 2.6, 0)
	cc.look_at(m.player.global_position.lerp(oq.holder.position, 0.5) + Vector3(0, 0.9, 0), Vector3.UP)
	for i in 4:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("1_following.png"))
	cc.current = false
	await walk_to(to)
	printerr("THIEF at Manolo: officer %.1f m behind" % oq.holder.position.distance_to(m.player.global_position))
	m.game.talk_to("manolo")
	for k in 12:
		await talk_through(0, true)
		if g.m_done("thief"):
			break
		await get_tree().create_timer(0.5).timeout
	printerr("THIEF done=", g.m_done("thief"), " caught=", g.S.flags.get("manoloCaught", false), " apple back=", g.has_item("apple"), " stolen=", g.S.stolen)
	await get_tree().create_timer(1.5).timeout
	var side := Vector3(1, 0, 0)
	cc.global_position = mq.holder.position - side * 2.6 + Vector3(0, 1.3, -1.2)
	cc.look_at(mq.holder.position + Vector3(0, 0.9, 0), Vector3.UP)
	for i in 4:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("2_cuffed.png"))
	cc.global_position = mq.holder.position + Vector3(0, 1.2, -2.4) * Vector3(1, 1, -1)
	cc.look_at(mq.holder.position + Vector3(0, 0.9, 0), Vector3.UP)
	cc.global_position = mq.holder.position - Vector3(sin(mq.holder.rotation.y), 0, cos(mq.holder.rotation.y)) * 2.2 + Vector3(0, 1.3, 0)
	cc.look_at(mq.holder.position + Vector3(0, 0.95, 0), Vector3.UP)
	for i in 4:
		cc.current = true
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("3_behind.png"))
	cc.queue_free()
	await talk("manolo")
	await talk("bofarull")
	await go_in(entrance("int_sandra"))
	await talk_through(0, false)
	await go_out()
	printerr("THIEF after: manolo gone=", mq.get("gone", false), " officer home=%.2f m" % oq.holder.position.distance_to(oq.home))
	place(oq.home.x, oq.home.z + 1.4, PI)
	await talk("bofarull")
	await talk("bofarull")
	end_test()


func run_shadowcrawl(path: String) -> void:
	# round 22: how a building's shadow moves over the pavement as the clock runs (a minute a second): looks down at
	# a shadow's edge for 4 s and counts, frame by frame, the pixels that changed. Steps show as bursts with
	# nothing between; a glide as a steady trickle. --sunstep: the old way (the light turned twice a second).
	await get_tree().create_timer(3.0).timeout
	m.game.S.time = 8 * 60 + 30
	m.light_from_clock()
	var d = m.D.door
	place(d.pos[0] + 30.0, d.pos[1] + 30.0, 0.0)
	m.model.visible = false
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 40.0
	cc.global_position = Vector3(d.pos[0], 7.0, d.pos[1] + 9.0)
	cc.look_at(Vector3(d.pos[0], 0.0, d.pos[1] + 3.0), Vector3.UP)
	cc.current = true
	for i in 30:
		await get_tree().process_frame
	var prev: Image = null
	var counts := []
	var heat := Image.create(320, 200, false, Image.FORMAT_RGB8)
	var acc := PackedFloat32Array()
	acc.resize(320 * 200)
	for i in 240:
		await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		img.resize(320, 200, Image.INTERPOLATE_BILINEAR)
		if prev:
			var n := 0
			for y in range(0, 200, 2):
				for x in range(0, 320, 2):
					var dl := absf(img.get_pixel(x, y).get_luminance() - prev.get_pixel(x, y).get_luminance())
					acc[y * 320 + x] += dl
					if dl > 0.02:
						n += 1
			counts.append(n)
		prev = img
		if i == 120:
			img.save_png(path)
	for y in range(0, 200, 2):
		for x in range(0, 320, 2):
			var v := clampf(acc[y * 320 + x] * 2.0, 0.0, 1.0)
			heat.fill_rect(Rect2i(x, y, 2, 2), Color(v, v, v))
	heat.save_png(path.get_basename() + "_heat.png")
	var busy := counts.filter(func(c): return c > 0).size()
	var big: int = counts.max()
	var tot := 0
	for c in counts:
		tot += c
	print("SHADOWCRAWL frames %d, frames with change %d, biggest %d, total %d" % [counts.size(), busy, big, tot])
	print("SHADOWCRAWL ", counts.slice(0, 90))
	end_test()


func run_journal(path: String) -> void:
	# round 22: the journal page: missions under their names in the order taken up, done ones greyed (name and last
	# line), steps behind her greyed, the step she is on in ink; one entry in the old "Mission 3 — The lost dog" form
	await get_tree().create_timer(3.0).timeout
	var g = m.game
	var M: Dictionary = g.data.MISSIONS
	g.S.missions = {"home": {"st": "done", "num": 1}, "gift": {"st": "done", "num": 2}, "dog": {"st": "active", "num": 3},
		"thief": {"st": "done", "num": 4}, "brush": {"st": "active", "num": 5}}
	g.S.focus = "dog"
	g.S.log = [{"t": "x", "k": "home", "x": M.home.log.start}, {"t": "x", "k": "home", "x": M.home.log.done},
		{"t": "x", "k": "gift", "x": M.gift.log.start}, {"t": "x", "k": "gift", "x": M.gift.log.bought},
		{"t": "Mission 3 — The lost dog", "x": M.dog.log.start}, {"t": "x", "k": "gift", "x": M.gift.log.done},
		{"t": "x", "k": "thief", "x": M.thief.log.start}, {"t": "x", "k": "dog", "x": M.dog.log.found},
		{"t": "x", "k": "thief", "x": M.thief.log.done}, {"t": "Study Notes 1", "x": "Received Chapter 1 of the Rambla Guide."},
		{"t": "x", "k": "brush", "x": M.brush.log.start}]
	m.panels.open_journal()
	m.panels.journal_scroll = 0.0
	m.panels.open_journal()
	await get_tree().create_timer(0.5).timeout
	get_viewport().get_texture().get_image().save_png(path)
	# (round 37) ◀ turns to her notebook, ▶ back to the journal
	m.panels.key(KEY_LEFT)
	await get_tree().create_timer(0.5).timeout
	printerr("JOURNAL ◀ shows the %s page" % m.panels.journal_pages()[m.panels.journal_page])
	get_viewport().get_texture().get_image().save_png(path.get_basename() + "_notebook.png")
	m.panels.key(KEY_RIGHT)
	await get_tree().create_timer(0.3).timeout
	printerr("JOURNAL ▶ shows the %s page" % m.panels.journal_pages()[m.panels.journal_page])
	m.panels.close(false)
	await get_tree().create_timer(0.3).timeout
	get_viewport().get_texture().get_image().save_png(path.get_basename() + "_hud.png")
	end_test()


func run_exam(dir: String) -> void:
	# round 22: the exam as a montage: everything done, sit it, a picture every 1.2 s through the scene and after
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var g = m.game
	for k in g.data.OPEN_MISSIONS + ["home", "gift"]:
		g.S.missions[k] = {"st": "done", "num": 5}
	for n in range(1, 6):
		g.S.flags["note%d" % n] = true
	g.S.flags.erase("examPassed")
	g.S.missions.erase("exam")
	await go_in(entrance("int_upf"))
	await talk_through(0, true)
	printerr("EXAM in %s; all done=%s notes=%s profbook=%s" % [m.room, g.all_open_done(), g.notes_all(), g.S.missions.get("profbook", {})])
	m.game.talk_to("oriol")
	printerr("EXAM talking: dlg=%s" % m.dlg_open)
	var shots := 0
	for i in 400:
		await get_tree().process_frame
		if m.dlg_open and not m.cutscene:
			if m.choice_box.visible:
				m.dlg_choice = 0
			m.dialog_next()
			await get_tree().create_timer(0.3).timeout
			continue
		if m.cutscene:
			break
	var t0 := Time.get_ticks_msec()
	while m.cutscene or m.dlg_open:
		await get_tree().create_timer(1.2).timeout
		shots += 1
		printerr("EXAMSHOT %d cutscene=%s dlg=%s drawn=%d cam=%s" % [shots, m.cutscene, m.dlg_open, Engine.get_frames_drawn(), get_viewport().get_camera_3d().global_position])
		get_viewport().get_texture().get_image().save_png(dir.path_join("exam_%02d.png" % shots))
		if not m.cutscene and m.dlg_open:
			printerr("    %s: %s" % [m.dlg_who.text, m.dlg_text.text.left(110)])
			m.dialog_next()
		if Time.get_ticks_msec() - t0 > 60000:
			break
	await get_tree().create_timer(1.0).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("exam_after.png"))
	printerr("EXAM passed=", g.S.flags.get("examPassed", false), " done=", g.m_done("exam"), " diploma=", g.has_item("diploma"))
	end_test()


func run_swaycost() -> void:
	# (round 24, the user: "can the grass not move, and only a bit of the foliage and leaves? Does that improve it?")
	# the frame rate in the wood with everything swaying, with the grass and plants still (their shader without its
	# vertex movement), and with everything still; 4 s each, the average frames per second
	await get_tree().create_timer(3.0).timeout
	var still := Shader.new()
	var code := FileAccess.get_file_as_string("res://shaders/foliage.gdshader")
	var a := code.find("void vertex()")
	var b := code.find("void fragment()")
	still.code = code.substr(0, a) + "varying float shade;\nvoid vertex() {\n\tvec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;\n\tshade = fract(sin(dot(floor(wp * 0.9), vec3(12.9898, 78.233, 37.719))) * 43758.5453);\n}\n\n" + code.substr(b)
	still.code = still.code.replace("varying float shade;\n\nvarying float shade;", "varying float shade;")
	var crown_still := Shader.new()
	crown_still.code = still.code.replace("render_mode cull_disabled, diffuse_burley;", "render_mode cull_disabled, diffuse_burley, shadows_disabled;")
	var spots := [["forest path", Vector2(40.5, 5.0), 0.0], ["forest glade", Vector2(43.0, 1.5), PI * 0.5], ["meadow", Vector2(28.5, -2.5), PI * 0.5]]
	for v in spots:
		place(v[1].x * 3.3, v[1].y * 3.3, v[2])
		var res := []
		for mode in ["all moving", "grass still", "all still"]:
			for k in m.foliage_mats:
				var tree: bool = k[1]
				var sh: Shader = (m.crown_shader if tree else m.foliage_shader)
				if mode == "all still" or (mode == "grass still" and not tree):
					sh = crown_still if tree else still
				(m.foliage_mats[k] as ShaderMaterial).shader = sh
			await get_tree().create_timer(1.5).timeout
			var n := 0
			var t0 := Time.get_ticks_usec()
			while Time.get_ticks_usec() - t0 < 4000000:
				await get_tree().process_frame
				n += 1
			res.append("%s %.1f fps" % [mode, n / ((Time.get_ticks_usec() - t0) / 1000000.0)])
		printerr("SWAY %s: %s" % [v[0], ", ".join(res)])
	end_test()


func run_hillescape() -> void:
	# (round 24) the hill path's railing and banks: from every few metres along the path, Sandra tries to leave it on
	# each side (walking straight off for 1.6 s); anywhere she ends up more than 2.6 m from the path, outside the ball's
	# glade, is an escape. Then, in the glade, she runs west and east for 6 s each: its fences must hold.
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["pathOpen"] = true
	m.north.refresh()
	var pts: Array = m.north.path_pts
	var esc := 0
	var tried := 0
	var acc := 0.0
	var nxt := 4.0
	for i in range(1, pts.size() - 2):
		acc += Vector2(pts[i].x - pts[i - 1].x, pts[i].z - pts[i - 1].z).length()
		if acc < nxt:
			continue
		nxt += float(OS.get_environment("ESC_STEP")) if OS.get_environment("ESC_STEP") != "" else 6.0
		var d := Vector2(pts[i + 1].x - pts[i - 1].x, pts[i + 1].z - pts[i - 1].z).normalized()
		for sd: float in [1.0, -1.0]:
			var n: Vector2 = Vector2(-d.y, d.x) * sd
			place(pts[i].x, pts[i].z, atan2(n.x, n.y))
			m.cam_yaw_node.rotation.y = atan2(n.x, n.y) + PI
			await get_tree().physics_frame
			m.vkeys[KEY_W] = true
			await get_tree().create_timer(1.6).timeout
			m.vkeys.clear()
			await get_tree().create_timer(0.1).timeout
			var p: Vector3 = m.player.global_position
			var best := 1e9
			for q in pts:
				best = minf(best, Vector2(q.x - p.x, q.z - p.z).length())
			tried += 1
			var glade: bool = p.x > -197.0 and p.x < -147.0 and p.z < -240.0 and p.z > -280.0
			# (round 25: on the path's uphill side a strip of green is hers, 3 m past the path's edge: off the path by more
			# than 2.6 m is an escape only below the path, or past the strip)
			var bq: Vector3 = pts[0]
			for q in pts:
				if Vector2(q.x - p.x, q.z - p.z).length() < Vector2(bq.x - p.x, bq.z - p.z).length():
					bq = q
			var below: bool = m.ground_at(p) < bq.y - 0.3
			if ((best > 2.6 and below) or best > 5.3) and not glade:
				esc += 1
				print("ESCAPE at path %.0f m (%.1f, %.1f) side %d: now %.1f m off, at (%.1f, %.1f)" % [acc, pts[i].x, pts[i].z, int(sd), best, p.x, p.z])
	print("HILLESCAPE %d tries, %d escapes" % [tried, esc])
	for gx in [-195.0, -149.0]:
		place(-172.2, -258.0, PI / 2.0 if gx > -172.0 else -PI / 2.0)
		m.cam_yaw_node.rotation.y = m.model.rotation.y + PI
		await get_tree().physics_frame
		m.vkeys[KEY_W] = true
		await get_tree().create_timer(6.0).timeout
		m.vkeys.clear()
		var p2: Vector3 = m.player.global_position
		# (round 35, PATH_RULES E3: the glade is open at its ends — running out of it is fine if she hasn't fallen;
		# a fall is more than 2 m below where she set off)
		var fell: bool = m.ground_at(p2) < m.ground_at(Vector3(-172.2, 0, -258.0)) - 2.0
		var inside: bool = p2.x > -199.0 and p2.x < -145.0
		print("GLADE run towards x=%.0f: stopped at (%.1f, %.1f) %s" % [gx, p2.x, p2.z, "HELD" if inside else ("FELL" if fell else "OPEN (level ground)")])
	end_test()


func run_flowers(dir: String) -> void:
	# (round 24) Alba's five wildflowers along the hill path: each seen from the path (a picture), E offers it, picked;
	# then Alba takes the five for the book
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var g = m.game
	if not g.m_active("grail"):
		g.start_mission("grail")
		await talk_through()
	g.refresh_ground()
	var n := 0
	var pts: Array = m.north.path_pts
	for gr in g.ground:
		if gr.id != "flower":
			continue
		var best: Vector3 = pts[0]
		for q in pts:
			if Vector2(q.x - gr.pos.x, q.z - gr.pos.z).length() < Vector2(best.x - gr.pos.x, best.z - gr.pos.z).length():
				best = q
		var to := Vector2(gr.pos.x - best.x, gr.pos.z - best.z)
		var st := Vector2(best.x, best.z) + to.normalized() * maxf(0.0, to.length() - 1.0)   # (a step towards it)
		place(st.x, st.y, atan2(to.x, to.y))
		await get_tree().create_timer(0.6).timeout
		if n == 0:
			var cc := Camera3D.new()
			add_child(cc)
			var fp: Vector3 = gr.pos
			cc.global_position = Vector3(best.x, m.ground_at(best) + 1.9, best.z) - Vector3(to.x, 0, to.y).normalized() * 3.0
			cc.look_at(fp + Vector3(0, 0.3, 0), Vector3.UP)
			for i in 30:
				cc.current = true
				await get_tree().process_frame
			get_viewport().get_texture().get_image().save_png(dir.path_join("flower.png"))
			cc.queue_free()
		var near: Dictionary = m.nearest()
		print("FLOWER %d at (%.1f, %.1f), %.1f m from the path's middle: visible=%s, E offers %s" % [n, gr.pos.x, gr.pos.z,
			to.length(), gr.node.visible if gr.has("node") and gr.node else false, near.get("label", "nothing")])
		m.interact()
		await talk_through()
		n += 1
	print("FLOWERS picked: %d (has %d)" % [n, g.count_item("flower")])
	for k in 2:                                       # (the first time she asks for them, the second she takes them)
		g.talk_to("alba")
		await talk_through()
	print("FLOWERS after Alba: traded=%s, flowers left %d" % [g.S.flags.get("albaTraded", false), g.count_item("flower")])
	end_test()


func run_benchview(dir: String) -> void:
	# (round 24) at each viewpoint's bench, looking out over the view (round 25: no "Stop and look at the view" any more:
	# E should offer nothing there); a picture of what she sees
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(1110.0)
	var bn: Array = m.D.north.get("benches", [])
	for k in bn.size():
		place(bn[k][0] + sin(bn[k][2]) * 0.9, bn[k][1] + cos(bn[k][2]) * 0.9, bn[k][2])
		await get_tree().create_timer(1.5).timeout
		var near: Dictionary = m.nearest()
		print("BENCH %d: E offers %s" % [k, near.get("label", "nothing")])
		get_viewport().get_texture().get_image().save_png(dir.path_join("bench_%d.png" % k))
	end_test()


func run_cove() -> void:
	# (round 25) the east end of the beach: the breakwater (scene breakwater: x, z from, z to) stops her walking east along
	# the sand, at the water's edge and in the wood's edge beside it; and the wood's rise stops her further north. Each
	# walk 5 s; she must end west of the breakwater (or, in the wood, no more than a metre up the rise).
	await get_tree().create_timer(3.0).timeout
	var bw: Array = m.D.get("breakwater", [181.0, 123.0, 170.0])
	var bx: float = bw[0]
	for v in [["along the sand", bx - 14.0, 140.0, PI / 2.0], ["by the water", bx - 14.0, float(bw[2]) - 26.0, PI / 2.0],
			["the wood's edge", bx - 12.0, float(bw[1]) + 1.0, PI / 2.0], ["in the wood", bx - 12.0, 60.0, PI / 2.0],
			["round its end, through the sea", bx - 6.0, float(bw[2]) - 18.0, PI * 0.25]]:
		place(v[1], v[2], v[3])
		m.cam_yaw_node.rotation.y = v[3] + PI
		await get_tree().physics_frame
		var h0: float = m.ground_at(m.player.global_position)
		var hmax := h0
		m.vkeys[KEY_W] = true
		for i in 50:
			await get_tree().create_timer(0.1).timeout
			hmax = maxf(hmax, m.ground_at(m.player.global_position))
		m.vkeys.clear()
		var p: Vector3 = m.player.global_position
		var ok: bool = (p.x < bx - 0.5 or v[0] == "in the wood") and hmax < h0 + 1.2      # (in the wood: the rise holds her)
		print("COVE %s: from (%.1f, %.1f) to (%.1f, %.1f), highest %.1f m: %s" % [v[0], v[1], v[2], p.x, p.z, hmax, "OK" if ok else "BAD"])
	end_test()


func run_telescope(dir: String) -> void:
	# (round 25) the coin telescope at the funfair: she pays a euro, looks (pictures), turns it, steps back; the city's
	# far-off detail and the haze are put back as they were
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	var tl: Array = m.D.north.get("telescope", [])
	if tl.is_empty():
		print("TELESCOPE none in this build")
		end_test()
		return
	m.set_clock(660.0)
	place(tl[0] - sin(tl[2]) * 1.1, tl[1] - cos(tl[2]) * 1.1, tl[2])
	m.game.S.money = 500
	await get_tree().create_timer(0.6).timeout
	print("TELESCOPE E offers: %s" % m.nearest().get("label", "nothing"))
	var pp: Vector3 = m.local_pos()
	for c in m.north.candidates(pp):
		print("TELESCOPE candidate %s at (%.1f, %.1f), she at (%.1f, %.1f) where=%s" % [c.label, c.x, c.z, pp.x, pp.z, m.where])
	var fog0: float = m.env_out.fog_depth_end
	m.north.act("telescope")
	await get_tree().create_timer(2.0).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("scope_1.png"))
	print("TELESCOPE looking=%s money=%d fps=%d" % [m.north.scope_active(), m.game.S.money, Engine.get_frames_per_second()])
	m.vkeys[KEY_LEFT] = true
	await get_tree().create_timer(4.0).timeout
	m.vkeys.clear()
	m.vkeys[KEY_DOWN] = true
	await get_tree().create_timer(2.0).timeout
	m.vkeys.clear()
	await get_tree().create_timer(0.5).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("scope_2.png"))
	m.vkeys[KEY_RIGHT] = true
	await get_tree().create_timer(9.0).timeout
	m.vkeys.clear()
	await get_tree().create_timer(0.5).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("scope_3.png"))
	print("TELESCOPE fps while looking=%d" % Engine.get_frames_per_second())
	m.north.end_scope()
	await get_tree().create_timer(1.0).timeout
	get_viewport().get_texture().get_image().save_png(dir.path_join("scope_after.png"))
	print("TELESCOPE after: looking=%s fog back=%s busy=%s" % [m.north.scope_active(), is_equal_approx(m.env_out.fog_depth_end, fog0), m.busy])
	end_test()


func run_hillbike() -> void:
	# (round 25) the bike on the hill path: up a long straight stretch (20% slower than she walks), down it (30% faster
	# than on the streets), and the speed carried on afterwards on the flat, easing off
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["pathOpen"] = true
	m.north.refresh()
	m.game.S.has_bike = true
	var pts: Array = m.north.path_pts
	var i := 330
	var a: Vector3 = pts[i]
	var b: Vector3 = pts[i + 14]
	var down := (b - a) if b.y < a.y else (a - b)
	var hd := atan2(down.x, down.z)
	var lo: Vector3 = b if b.y < a.y else a
	var hi: Vector3 = a if b.y < a.y else b
	for v in [["down", hi, hd], ["up", lo, hd + PI]]:
		place(v[1].x, v[1].z, v[2])
		await get_tree().create_timer(0.3).timeout
		if m.street.riding == null:
			m.bike_key()
		await get_tree().create_timer(0.4).timeout
		m.model.rotation.y = v[2]
		m.move_dir = Vector2(sin(v[2]), cos(v[2]))
		m.vkeys[KEY_W] = true
		var top := 0.0
		for k in 30:
			await get_tree().create_timer(0.1).timeout
			top = maxf(top, m.speed)
		m.vkeys.clear()
		print("HILLBIKE %s: top %.1f m/s (walking %.1f, street bike %.1f)" % [v[0], top, m.SPEED, m.street.BIKE_SPEED])
		m.speed = 0.0
	# carried on: as if just down the hill, on to the flat street
	place(-6.6, 60.0, PI, 0.0)
	await get_tree().create_timer(0.4).timeout
	m.speed = m.street.BIKE_SPEED * 1.3
	m.bike_glide = 1.0
	m.vkeys[KEY_W] = true
	var log := []
	for k in 8:
		await get_tree().create_timer(1.0).timeout
		log.append("%.1f" % m.speed)
	m.vkeys.clear()
	print("HILLBIKE after the hill, each second: %s" % ", ".join(log))
	end_test()


func run_foliagecost() -> void:
	# (round 25, the user: "Consider reducing some movement if it saves frame rates… Analyse this") what else the woods'
	# leaves cost: the frame rate as built; with the leaves casting no shadows; with the trees' simpler far version taking
	# over at 60 m instead of about 100; both. 4 s each, at three places (the wood, the hill path, the park).
	await get_tree().create_timer(3.0).timeout
	var leaves: Array = []
	for n in m.outdoor.find_children("Leaves_*", "GeometryInstance3D", true, false):
		leaves.append([n, (n as GeometryInstance3D).cast_shadow, (n as GeometryInstance3D).visibility_range_begin, (n as GeometryInstance3D).visibility_range_end])
	var spots := [["forest path", Vector3(40.5 * 3.3, 0, 5.0 * 3.3), 0.0]]
	var pts: Array = m.north.path_pts
	spots.append(["hill path", pts[200], PI])
	spots.append(["park", Vector3(110.0, 0, -205.0), PI])
	for v in spots:
		place(v[1].x, v[1].z, v[2])
		var res := []
		for mode in ["as built", "no leaf shadows", "far version from 60 m", "both"]:
			for e in leaves:
				var gi: GeometryInstance3D = e[0]
				gi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF if mode in ["no leaf shadows", "both"] else e[1]
				var near_far: bool = mode in ["far version from 60 m", "both"]
				if String(gi.name).begins_with("Leaves_forest_"):
					gi.visibility_range_end = 60.0 if near_far else e[3]
				elif String(gi.name).begins_with("Leaves_far_"):
					gi.visibility_range_begin = 55.0 if near_far else e[2]
			await get_tree().create_timer(1.5).timeout
			var n := 0
			var t0 := Time.get_ticks_usec()
			while Time.get_ticks_usec() - t0 < 4000000:
				await get_tree().process_frame
				n += 1
			res.append("%s %.1f fps" % [mode, n / ((Time.get_ticks_usec() - t0) / 1000000.0)])
		print("FOLIAGE %s: %s" % [v[0], ", ".join(res)])
	end_test()



func run_churchsteps(dir: String) -> void:
	# (round 25) the Sagrat Cor as the real one: up the east flight of steps to the landing, across the terrace to the
	# front, the balustrade holding her there; from the square the porch stops her; the hill behind the funfair holds
	# her too. Pictures on the way (dir).
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	var cx := -63.0
	var front := -299.0
	var walks := [
		["up the east steps", Vector2(cx + 14.5, front - 2.6), PI, 8.0, "steps"],
		["onto the terrace", Vector2(), -PI / 2.0, 2.5, "side"],
		["along to the front", Vector2(), 0.0, 6.0, "front_side"],
		["to the middle", Vector2(), -PI / 2.0, 3.0, "landing"],
		["off the front edge", Vector2(), 0.0, 3.0, "edge"],
		["up the bank behind the funfair", Vector2(-28.0, -316.0), PI, 5.0, "bank"],
		["up the west steps", Vector2(cx - 14.5, front - 2.6), PI, 8.0, "steps_w"],
		["from the square into the porch (in through the door)", Vector2(cx, front + 7.0), PI, 4.0, "porch"],
	]
	for v in walks:
		var at: Vector2 = v[1] if v[1] != Vector2() else Vector2(m.player.global_position.x, m.player.global_position.z)
		place(at.x, at.y, v[2])
		await get_tree().physics_frame
		var p0: Vector3 = m.player.global_position
		var hmax: float = m.ground_at(p0)
		m.vkeys[KEY_W] = true
		var t := 0.0
		while t < v[3]:
			await get_tree().create_timer(0.1).timeout
			t += 0.1
			hmax = maxf(hmax, m.ground_at(m.player.global_position))
		m.vkeys.clear()
		await get_tree().create_timer(0.6).timeout
		var p: Vector3 = m.player.global_position
		print("CHURCH %s: (%.1f, %.1f) -> (%.1f, %.1f), ground %.1f m (highest %.1f)" % [v[0], p0.x, p0.z, p.x, p.z, m.ground_at(p), hmax])
		get_viewport().get_texture().get_image().save_png(dir.path_join("%s.png" % v[4]))
	end_test()


func run_leafshadow(dir: String) -> void:
	# (round 25, the user: "Do a leaf shadows test with the 25m, 50m, 10m, and show it side by side with current") deep in
	# the hill wood (by the ball, and elsewhere) and in the eastern wood: the frame rate and a picture with the leaves'
	# shadows as now and only within 50, 25, 10 m of her (main.gd LEAF_SHADOW_R)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.missions["ball"] = {"st": "active", "num": 99}      # (so the ball lies there)
	m.game.S.taken.erase("ball")
	m.game.refresh_ground()
	var bp: Array = m.D.north.get("ball", m.D.north.ledge)
	var spots := [["hill_ball", Vector2(bp[0] + 2.2, bp[1] - 2.6), atan2(-2.2, 2.6)], ["hill_deep", Vector2(-130.0, -170.0), -PI / 2.0],
		["wood_a", Vector2(164.0, 12.0), PI / 2.0], ["wood_b", Vector2(168.0, 80.0), -PI / 2.0]]
	for v in spots:
		place(v[1].x, v[1].y, v[2])
		await get_tree().create_timer(1.0).timeout
		var res := []
		for r in [0.0, 50.0, 25.0, 10.0]:
			m.LEAF_SHADOW_R = r
			await get_tree().create_timer(2.0).timeout
			var n := 0
			var t0 := Time.get_ticks_usec()
			while Time.get_ticks_usec() - t0 < 3000000:
				await get_tree().process_frame
				n += 1
			var fps := n / ((Time.get_ticks_usec() - t0) / 1000000.0)
			res.append("%s %.1f fps" % ["as now" if r == 0.0 else "%d m" % int(r), fps])
			get_viewport().get_texture().get_image().save_png(dir.path_join("%s_%d.png" % [v[0], int(r)]))
		m.LEAF_SHADOW_R = 0.0
		print("LEAFSHADOW %s at (%.1f, %.1f): %s" % [v[0], m.player.global_position.x, m.player.global_position.z, ", ".join(res)])
	end_test()


func run_ballwalk(dir: String) -> void:
	# (round 25) the ball in the wood: from the path's top leg above it, down through the trees to it; E offers it
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.missions["ball"] = {"st": "active", "num": 99}      # (so the ball lies there)
	m.game.S.taken.erase("ball")
	m.game.refresh_ground()
	var bp: Array = m.D.north.get("ball", m.D.north.ledge)
	var best := Vector3.ZERO
	for q in m.north.path_pts:
		var pq: Vector3 = q
		if pq.z < bp[1] - 4.0 and (best == Vector3.ZERO or Vector2(pq.x - bp[0], pq.z - bp[1]).length() < Vector2(best.x - bp[0], best.z - bp[1]).length()):
			best = pq
	var head := atan2(bp[0] - best.x, bp[1] - best.z)
	place(best.x, best.z, head)
	await get_tree().create_timer(0.5).timeout
	m.vkeys[KEY_W] = true
	var t := 0.0
	while t < 12.0 and Vector2(m.player.global_position.x - bp[0], m.player.global_position.z - bp[1]).length() > 1.2:
		await get_tree().create_timer(0.1).timeout
		t += 0.1
	m.vkeys.clear()
	await get_tree().create_timer(0.8).timeout
	var p: Vector3 = m.player.global_position
	print("BALL from the path (%.1f, %.1f) to (%.1f, %.1f) in %.1f s, %.1f m from the ball; E offers: %s" % [best.x, best.z, p.x, p.z, t,
		Vector2(p.x - bp[0], p.z - bp[1]).length(), m.nearest().get("label", "nothing")])
	get_viewport().get_texture().get_image().save_png(dir.path_join("ball_reached.png"))
	end_test()


func run_shove(dir: String) -> void:
	# (round 37, the user: people pushed into give way, on foot and on the bike) someone standing at a post: Sandra walks
	# into them for 4.5 s, then rides into them; how far they were pushed, how far Sandra got, and whether they drift back
	# to their post once she has gone
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.new = false
	var who := "lluis"                                   # (standing in the open on La Rambla; --who= another)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--who="):
			who = a.substr(6)
	var q: Dictionary = m.npcs.current().get(who, {})
	if q.is_empty():
		printerr("SHOVE nobody to push")
		end_test()
		return
	for ride in [false, true]:
		var o: Vector3 = q.holder.global_position
		var post := o
		if ride:
			m.game.S.has_bike = true                            # (her own bike, as the player gets on it: B)
			place(o.x, o.z - 7.0, 0.0)
			await get_tree().create_timer(0.3).timeout
			m.bike_key()
			await get_tree().create_timer(0.6).timeout
			place(o.x, o.z - 7.0, 0.0)
			await get_tree().create_timer(0.3).timeout
			printerr("SHOVE bike start %s, Glòria %s, riding %s" % [m.player.global_position, o, m.street.riding != null])
		else:
			place(o.x, o.z - 2.0, 0.0)                          # (from the north, the open side; facing south, at her)
		await get_tree().create_timer(0.4).timeout
		var s0: Vector3 = m.player.global_position
		m.vkeys[KEY_W] = true
		for f in 45:
			await get_tree().create_timer(0.1).timeout
			if OS.get_cmdline_user_args().has("--shovedebug"):
				var pp: Vector3 = m.player.global_position
				printerr("SHOVET %.1f her (%.2f, %.2f) them (%.2f, %.2f) speed %.2f vel %s wall %s soft %.2f" % [f * 0.1, pp.x, pp.z,
					q.holder.global_position.x, q.holder.global_position.z, m.speed, m.player.velocity, m.player.is_on_wall(), m.soft_block_t])
		m.vkeys.erase(KEY_W)
		await get_tree().create_timer(0.15).timeout
		var o1: Vector3 = q.holder.global_position
		var s1: Vector3 = m.player.global_position
		get_viewport().get_texture().get_image().save_png(dir.path_join("shove_%s.png" % ("bike" if ride else "foot")))
		printerr("SHOVE %s: pushed %.2f m, Sandra went %.2f m, gap now %.2f m, speed %.2f" % [
			"bike" if ride else "foot", Vector2(o1.x - o.x, o1.z - o.z).length(), Vector2(s1.x - s0.x, s1.z - s0.z).length(),
			Vector2(s1.x - o1.x, s1.z - o1.z).length(), m.speed])
		if m.street.riding:
			m.street.dismount()
		place(post.x, post.z - 12.0, 0.0)
		await get_tree().create_timer(4.0).timeout
		var o2: Vector3 = q.holder.global_position
		printerr("SHOVE back at their post after 4 s: %.2f m off" % Vector2(o2.x - post.x, o2.z - post.z).length())
	end_test()


func run_models() -> void:
	# (round 37) which Meshy body each named person gets, and how many share each
	await get_tree().create_timer(2.0).timeout
	var counts := {}
	var who := {}
	for id in m.game.data.NPCS:
		var look: Dictionary = m.game.data.NPCS[id].get("look", {}).duplicate()
		look.shop = m.game.data.NPCS[id].get("shop", false)
		look.id = id
		var f: String = m.ROSA_MODEL if id == "rosa" else m.npcs.model_for(look)
		counts[f] = counts.get(f, 0) + 1
		who[f] = who.get(f, []) + [String(m.game.data.NPCS[id].get("name", id))]
	for f in counts:
		printerr("MODELS %s %d: %s" % [f, counts[f], ", ".join(PackedStringArray(who[f]))])
	end_test()


func run_porch(dir: String) -> void:
	# (round 39, the user on Casa Trias's porch: "These should be solid… when she does walk into here, it should become
	# first person and the arrow keys just move forward and backwards… You need to run around there and test the whole
	# thing with pictures.") Up the steps (the camera goes to her eyes), round the porch, into a column, against the
	# balustrade, out backwards and forwards, in at a slant; a picture every 0.5 s (<dir>/<leg>_<n>.jpg) and a line every
	# 0.25 s (place, height, the arm, her model shown, the veil). --porchsim stands round 39's proposed build (solid
	# columns and balustrade, the whole loggia walkable) in first, so it can be tried before the build has it.
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	if "--porchsim" in OS.get_cmdline_user_args():
		porch_sim()
	var mins := 660.0
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--porchclock="):
			mins = float(a.trim_prefix("--porchclock="))
	m.set_clock(mins)
	var N := PI
	var E := PI / 2.0
	var S := 0.0
	var W := -PI / 2.0
	# [name, place (x, z, heading) or null to carry on, keys, seconds]
	var legs := [
		["01_up_steps", [154.95, -216.5, N], "W", 2.4],
		["02_turn_left", null, "A", 0.6],
		["03_walk_west", null, "W", 2.2],
		["04_turn_left", null, "A", 0.6],
		["05_into_balustrade_w", null, "W", 1.6],
		["06_turn_left", null, "A", 0.6],
		["07_along_front", [152.0, -223.6, E], "W", 3.0],
		["08_into_column", [154.15, -224.6, S], "W", 1.6],
		["09_into_balustrade", [153.0, -224.6, S], "W", 1.6],
		["10_to_back_wall", [156.5, -224.0, N], "W", 3.0],
		["11_back_out", [154.95, -224.3, N], "S", 3.0],
		["12_walk_out", [154.95, -225.5, S], "W", 3.0],
		["13_in_at_slant", [151.5, -217.5, N - 0.6], "W", 3.0],
	]
	var codes := {"W": KEY_W, "A": KEY_A, "S": KEY_S, "D": KEY_D}
	var veil_max := 0.0
	for leg in legs:
		if leg[1] != null:
			var pl: Array = leg[1]
			place(pl[0], pl[1], pl[2])
			m.snap_height()
			await get_tree().create_timer(1.5).timeout
		for ch in String(leg[2]):
			m.vkeys[codes[ch]] = true
		var t0 := 0.0
		var n := 0
		while t0 < float(leg[3]) + 1.0:                   # (and a second after the keys are let go)
			if t0 >= float(leg[3]):
				for ch in String(leg[2]):
					m.vkeys.erase(codes[ch])
			await get_tree().create_timer(0.25).timeout
			t0 += 0.25
			var pp := m.player.global_position
			veil_max = maxf(veil_max, m.veil_a)
			print("PORCH %s t=%.2f x=%.2f z=%.2f h=%.2f face=%.2f speed=%.2f fp=%s k=%.2f arm=%.2f shown=%s veil=%.2f pitch=%.2f yaw-face=%.2f" % [
				leg[0], t0, pp.x, pp.z, m.model.position.y, m.model.rotation.y, m.speed, m.fp_on, m.fp_k, m.arm.spring_length,
				m.model.visible, m.veil_a, m.cam_pitch_node.rotation.x, wrapf(m.cam_yaw_node.rotation.y - m.model.rotation.y - PI, -PI, PI)])
			if int(t0 * 4.0) % 2 == 0:
				var img := get_viewport().get_texture().get_image()
				img.resize(640, 400)
				img.save_jpg(dir.path_join("%s_%02d.jpg" % [leg[0], n]), 0.85)
				n += 1
	print("PORCH done: the veil at most %.2f" % veil_max)
	end_test()


func porch_sim() -> void:
	# (round 39) Casa Trias's porch as the proposed build would leave it: the old boxes (the house behind a 3 m porch,
	# the balustrade standing out in front of the real one) out; the walls at the Meshy model's own faces, the
	# balustrade on its line with the steps' bay open, the two columns by the steps round posts; the whole loggia's
	# floor and the steps where the model has them
	var old := [[149.4, -230.6, 160.6, -225.141], [149.4, -225.141, 150.2, -221.4], [157.3, -225.141, 160.6, -221.4],
		[150.2, -222.391, 154.1, -222.091], [156.1, -222.391, 157.3, -222.091]]
	var new := [[149.4, -230.6, 160.6, -228.85], [149.4, -228.85, 150.95, -221.4], [158.95, -228.85, 160.6, -221.4],
		[157.25, -223.15, 158.95, -221.4], [150.95, -223.15, 153.95, -222.55], [155.95, -223.15, 157.25, -222.55]]
	var off := 0
	for cs in m.find_children("*", "CollisionShape3D", true, false):
		var bs = (cs as CollisionShape3D).shape
		if not bs is BoxShape3D:
			continue
		var gp: Vector3 = (cs as CollisionShape3D).global_position
		for r in old:
			if absf(gp.x - (r[0] + r[2]) / 2.0) < 0.01 and absf(gp.z - (r[1] + r[3]) / 2.0) < 0.01 \
					and absf((bs as BoxShape3D).size.x - (r[2] - r[0])) < 0.01:
				(cs as CollisionShape3D).disabled = true
				off += 1
	var b: StaticBody3D = m.static_body(m.LAYER_BODY)
	for r in new:
		m.add_box(b, Vector3((r[0] + r[2]) / 2.0, 2, (r[1] + r[3]) / 2.0), Vector3(r[2] - r[0], 4, r[3] - r[1]))
	var pb: StaticBody3D = m.static_body(m.LAYER_BODY)
	for c in [[154.15, -222.9], [155.75, -222.9]]:
		m.add_post(pb, c[0], c[1], 0.225, 1.0)
	m.D.flats = m.D.flats.filter(func(f): return not (absf(f[0] - 150.2) < 0.01 or absf(f[0] - 154.1) < 0.01))
	m.D.flats.push_front([153.95, -222.55, 156.0, -221.8, 23.55, 22.5])
	m.D.flats.push_front([150.95, -228.85, 158.95, -222.55, 23.55, 23.55])
	for st in m.D.north.park.steps:
		if absf(float(st[0]) - 154.1) < 0.01:
			st.assign([153.95, -222.85, 156.0, -221.8])
	print("PORCHSIM %d old boxes off, %d new, flats now %d" % [off, new.size(), m.D.flats.size()])


func run_wallescape() -> void:
	# (round 40, the user by Casa Larrard: "It's a trap where I can never escape from… check the other walls") each of
	# the park's slope walls (north.park.slope_walls) long enough to be built as a wall: she is put 0.7 m on its uphill
	# side, at its middle, and walks along it each way and away from it for 5 s; out if she ends 2.5 m clear of it
	await get_tree().create_timer(3.0).timeout
	var lines: Array = m.D.get("north", {}).get("park", {}).get("slope_walls", [])
	var trapped := 0
	for i in lines.size():
		var l: Array = lines[i]
		if l.size() < 6:
			continue
		var a := Vector2(l[l.size() / 2 - 1][0], l[l.size() / 2 - 1][1])
		var b := Vector2(l[l.size() / 2 + 1][0], l[l.size() / 2 + 1][1])
		var mid := (a + b) / 2.0
		var u := (b - a).normalized()
		var n := Vector2(-u.y, u.x)
		if m.terrain_at(mid.x - n.x, mid.y - n.y) > m.terrain_at(mid.x + n.x, mid.y + n.y):
			n = -n                                          # (uphill)
		var st := mid + n * 0.7
		var outs := []
		for d in [u, -u, n, (n + u).normalized(), (n - u).normalized()]:
			place(st.x, st.y, atan2(d.x, d.y))
			m.model.position.y = m.ground_at(m.player.global_position)
			await get_tree().create_timer(0.3).timeout
			m.vkeys[KEY_W] = true
			await get_tree().create_timer(5.0).timeout
			m.vkeys.erase(KEY_W)
			var pp := Vector2(m.player.global_position.x, m.player.global_position.z)
			var dmin := INF
			for q in l:
				dmin = minf(dmin, pp.distance_to(Vector2(q[0], q[1])))
			outs.append("%.1f" % dmin)
			if dmin > 2.5:
				break
		var ok := false
		for o in outs:
			if float(o) > 2.5:
				ok = true
		if not ok:
			trapped += 1
		print("WALLESC %d len=%d at (%.1f, %.1f) %s  %s" % [i, l.size(), mid.x, mid.y, "out" if ok else "TRAPPED", " ".join(outs)])
	print("WALLESC trapped %d" % trapped)
	get_tree().quit()


func run_traps(spec: String) -> void:
	# (round 40, the user: "There are these death traps all around the pink area… You need to have a test to review the
	# entire park. Find every single place that there is a death trap that she can't get out of") --traps=<png>[:x0,z0,x1,z1]
	# every half metre of the park (or the given rectangle): where she can stand (her own shape clear of anything built;
	# tree trunks she slips through), and each step to a neighbour she can take by the game's own rules — nothing built
	# across it, and no climb steeper than she may walk (north.gd steer_on_slope: SLIDE_AT inside the park, MAX_UP out,
	# paths, steps and doorsteps up to 1.2, built floors any). From the gate plaza: where she can get to, and from where
	# she can get back. A place she can get to but not back from is a trap. The map: traps red, the rest by how far
	# round she must go; the traps listed as patches, biggest first.
	var parts := spec.split(":")
	var path: String = parts[0]
	var R := Rect2(44.0, -258.0, 150.0, 124.0)
	if parts.size() > 1:
		var v := parts[1].split(",")
		R = Rect2(float(v[0]), float(v[1]), float(v[2]) - float(v[0]), float(v[3]) - float(v[1]))
	await get_tree().create_timer(3.0).timeout
	await old_walls()
	var cs := 0.5
	var nx := int(R.size.x / cs)
	var nz := int(R.size.y / cs)
	var pl := m.player
	var space := pl.get_world_3d().direct_space_state
	var ex: Array[RID] = [pl.get_rid(), m.tree_body.get_rid()]
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = ex
	var stand := PackedByteArray()
	stand.resize(nx * nz)
	var h := PackedFloat32Array()
	h.resize(nx * nz)
	var climb := PackedByteArray()
	climb.resize(nx * nz)
	var flat := PackedByteArray()
	flat.resize(nx * nz)
	var inside := PackedByteArray()
	inside.resize(nx * nz)
	var flats: Array = m.D.get("flats", [])
	for iz in nz:
		for ix in nx:
			var i := iz * nx + ix
			var x: float = R.position.x + (ix + 0.5) * cs
			var z: float = R.position.y + (iz + 0.5) * cs
			var p := Vector3(x, 0, z)
			q.transform = Transform3D(Basis(), Vector3(x, 0.82, z))
			var ok := true
			for hit in space.intersect_shape(q, 4):
				if hit.collider is StaticBody3D:
					ok = false
			stand[i] = 1 if ok else 0
			if not ok:
				continue
			h[i] = m.terrain_at(x, z)
			climb[i] = 1 if (m.north.on_path(p) or m.north.on_steps(p) or m.north.at_doorstep(p)) else 0
			inside[i] = 1 if m.north.park_inside(p) else 0
			for f in flats:
				if x >= f[0] and x <= f[2] and z >= f[1] and z <= f[3]:
					flat[i] = 1
					break
		if iz % 40 == 0:
			await get_tree().process_frame
	var DX := [1, 1, 0, -1, -1, -1, 0, 1]
	var DZ := [0, 1, 1, 1, 0, -1, -1, -1]
	var out := PackedByteArray()                   # per cell: which of the 8 steps she can take from it
	out.resize(nx * nz)
	for iz in nz:
		for ix in nx:
			var i := iz * nx + ix
			if stand[i] == 0:
				continue
			var a := Vector3(R.position.x + (ix + 0.5) * cs, 0.5, R.position.y + (iz + 0.5) * cs)
			var mask := 0
			for k in 8:
				var jx: int = ix + DX[k]
				var jz: int = iz + DZ[k]
				if jx < 0 or jz < 0 or jx >= nx or jz >= nz:
					continue
				var j := jz * nx + jx
				if stand[j] == 0:
					continue
				var d := cs * (1.4142 if (k % 2) == 1 else 1.0)
				var rise: float = (h[j] - h[i]) / d
				var lim: float = 0.55 if inside[i] == 1 else 0.30
				if climb[i] == 1:
					lim = 1.2
				if flat[i] == 1 or flat[j] == 1:
					lim = INF
				if rise > lim:
					continue
				var b := Vector3(R.position.x + (jx + 0.5) * cs, 0.5, R.position.y + (jz + 0.5) * cs)
				var rq := PhysicsRayQueryParameters3D.create(a, b, m.LAYER_BODY, ex)
				var hit2 := space.intersect_ray(rq)
				if not hit2.is_empty() and hit2.collider is StaticBody3D:
					continue
				mask |= 1 << k
			out[i] = mask
		if iz % 20 == 0:
			await get_tree().process_frame
	# the gate plaza: the nearest place she can stand to its middle
	var hub := -1
	var best := INF
	var hp := Vector2(106.0, -146.0)
	for i in nx * nz:
		if stand[i] == 1:
			var c := Vector2(R.position.x + (i % nx + 0.5) * cs, R.position.y + (i / nx + 0.5) * cs)
			if c.distance_to(hp) < best and R.has_point(hp):
				best = c.distance_to(hp)
				hub = i
	if hub < 0:
		hub = nx * nz / 2
	var fwd := PackedInt32Array()
	fwd.resize(nx * nz)
	fwd.fill(-1)
	var back := PackedByteArray()
	back.resize(nx * nz)
	var qq := PackedInt32Array([hub])
	fwd[hub] = 0
	var qi := 0
	while qi < qq.size():
		var i: int = qq[qi]
		qi += 1
		for k in 8:
			if out[i] & (1 << k):
				var j: int = i + DZ[k] * nx + DX[k]
				if fwd[j] < 0:
					fwd[j] = fwd[i] + 1
					qq.append(j)
	qq = PackedInt32Array([hub])
	back[hub] = 1
	qi = 0
	while qi < qq.size():
		var j: int = qq[qi]
		qi += 1
		var jx := j % nx
		var jz := j / nx
		for k in 8:
			var ix: int = jx - DX[k]
			var iz: int = jz - DZ[k]
			if ix < 0 or iz < 0 or ix >= nx or iz >= nz:
				continue
			var i := iz * nx + ix
			if back[i] == 0 and (out[i] & (1 << k)):
				back[i] = 1
				qq.append(i)
	var img := Image.create(nx, nz, false, Image.FORMAT_RGB8)
	var trap := PackedByteArray()
	trap.resize(nx * nz)
	var n_trap := 0
	for i in nx * nz:
		var c := Color(0.2, 0.2, 0.22)
		if stand[i] == 0:
			c = Color(0.05, 0.05, 0.05)
		elif fwd[i] >= 0 and back[i] == 0:
			c = Color(0.95, 0.1, 0.1)
			trap[i] = 1
			n_trap += 1
		elif fwd[i] >= 0:
			c = Color(0.75, 0.85, 0.7) if climb[i] == 0 else Color(0.85, 0.82, 0.7)
		elif back[i] == 1:
			c = Color(0.45, 0.55, 0.8)                 # (she could leave it, but never gets there)
		img.set_pixel(i % nx, i / nx, c)
	img.save_png(path)
	# the traps as patches
	var seen := PackedByteArray()
	seen.resize(nx * nz)
	var patches := []
	for i in nx * nz:
		if trap[i] == 0 or seen[i] == 1:
			continue
		var st := [i]
		seen[i] = 1
		var n := 0
		var sx := 0.0
		var sz := 0.0
		var lo := Vector2(INF, INF)
		var hi := Vector2(-INF, -INF)
		while not st.is_empty():
			var c: int = st.pop_back()
			n += 1
			var cx: float = R.position.x + (c % nx + 0.5) * cs
			var cz: float = R.position.y + (c / nx + 0.5) * cs
			sx += cx
			sz += cz
			lo = Vector2(minf(lo.x, cx), minf(lo.y, cz))
			hi = Vector2(maxf(hi.x, cx), maxf(hi.y, cz))
			for k in 8:
				var jx: int = c % nx + DX[k]
				var jz: int = c / nx + DZ[k]
				if jx < 0 or jz < 0 or jx >= nx or jz >= nz:
					continue
				var j := jz * nx + jx
				if trap[j] == 1 and seen[j] == 0:
					seen[j] = 1
					st.append(j)
		patches.append([n, sx / n, sz / n, lo, hi])
	patches.sort_custom(func(a, b): return a[0] > b[0])
	printerr("TRAPS map %s (%d x %d, %.1f m a pixel, from x %.1f z %.1f): %d m2 of trap in %d patches" % [path, nx, nz, cs,
		R.position.x, R.position.y, n_trap / 4, patches.size()])
	for pt in patches:
		printerr("TRAP %5.1f m2 at (%.1f, %.1f)  from (%.1f, %.1f) to (%.1f, %.1f)" % [pt[0] / 4.0, pt[1], pt[2], pt[3].x, pt[3].y, pt[4].x, pt[4].y])
	end_test()


func old_walls() -> void:
	# (round 40, --oldwalls: to check the trap test itself) the park's slope walls as they were before round 40, solid
	if not "--oldwalls" in OS.get_cmdline_user_args():
		return
	var ob: StaticBody3D = m.static_body(m.LAYER_BODY)
	for l in m.D.get("north", {}).get("park", {}).get("slope_walls", []):
		if l.size() < 6:
			continue
		for k in l.size() - 1:
			var a := Vector3(l[k][0], 1.0, l[k][1])
			var b := Vector3(l[k + 1][0], 1.0, l[k + 1][1])
			var cs0 := CollisionShape3D.new()
			var bx := BoxShape3D.new()
			bx.size = Vector3(0.4, 2.0, a.distance_to(b) + 0.1)
			cs0.shape = bx
			cs0.transform = Transform3D(Basis(Vector3.UP, atan2(b.x - a.x, b.z - a.z)), (a + b) / 2.0)
			ob.add_child(cs0)
	await get_tree().physics_frame
	await get_tree().physics_frame


func run_npcpose(id: String) -> void:
	# (round 40) a story character's posture modifier, as the game has it: is it there, on, and turning the head?
	await get_tree().create_timer(3.0).timeout
	var q: Dictionary = m.npcs.outdoor.get(id, {})
	if q.is_empty():
		printerr("NPCPOSE no %s outdoors" % id)
		end_test()
		return
	place(q.holder.global_position.x + 3.0, q.holder.global_position.z, -PI / 2.0)
	await get_tree().create_timer(1.0).timeout
	var pst = q.m.get("posture")
	if pst == null:
		printerr("NPCPOSE %s: no posture modifier" % id)
	else:
		var sk: Skeleton3D = pst.get_skeleton()
		printerr("NPCPOSE %s: active=%s amount=%.2f head=%d neck=%d hips=%d legs=%s feet=%s straight=%s aim=%.2f model=%s skel=%s" % [id,
			pst.active, pst.amount, pst.head, pst.neck, pst.hips, str(pst.legs), str(pst.feet), pst.straight_head, pst.head_aim,
			pst.model != null, sk != null])
		if sk:
			var names := []
			for bi in mini(sk.get_bone_count(), 40):
				names.append(sk.get_bone_name(bi))
			printerr("NPCPOSE bones: %s" % ", ".join(names))
		if sk and pst.head >= 0:
			printerr("NPCPOSE head bone %s, neck %s" % [sk.get_bone_name(pst.head), sk.get_bone_name(pst.neck) if pst.neck >= 0 else "-"])
	end_test()


func run_peoplewalls() -> void:
	# (round 40, the user: "None of the people should be allowed to walk through walls"; rule 10 #16a) every story
	# character out of doors: is it clear of walls where it stands, and after Sandra runs into it from four sides; then
	# every passer-by, once a second for a minute. Any that stands in a wall is listed.
	await get_tree().create_timer(3.0).timeout
	var bad := 0
	var n := 0
	for id in m.npcs.outdoor.keys():
		var q: Dictionary = m.npcs.outdoor[id]
		if q.is_empty() or q.get("gone", false):
			continue
		var h0: Vector3 = q.holder.global_position
		place(h0.x + 3.0, h0.z, -PI / 2.0)                    # (near enough that they are awake)
		for f in 20:
			await get_tree().physics_frame
		if not q.holder.visible:
			continue
		n += 1
		var h: Vector3 = q.holder.global_position
		if not m.person_fits(h):
			bad += 1
			printerr("PEOPLEWALL %s stands in a wall at (%.1f, %.1f): %s" % [id, h.x, h.z, what_at(h)])
			continue
		for k in 4:
			var a := k * PI / 2.0
			var from := h + Vector3(sin(a), 0, cos(a)) * 2.2
			place(from.x, from.z, a + PI)
			m.model.position.y = m.ground_at(m.player.global_position)
			m.vkeys[KEY_W] = true
			for f in 90:
				await get_tree().physics_frame
			m.vkeys.erase(KEY_W)
			for f in 30:
				await get_tree().physics_frame
			var h2: Vector3 = q.holder.global_position
			if not m.person_fits(h2):
				bad += 1
				printerr("PEOPLEWALL %s pushed into a wall at (%.1f, %.1f), run into from side %d: %s" % [id, h2.x, h2.z, k, what_at(h2)])
				break
	printerr("PEOPLEWALLS story characters: %d checked" % n)
	place(m.player.global_position.x, m.player.global_position.z, 0.0)
	var seen := {}
	for t in 60:
		await get_tree().create_timer(1.0).timeout
		for i in m.people.people.size():
			var w: Dictionary = m.people.people[i]
			var pp: Vector3 = w.holder.global_position
			if w.holder.visible and not m.person_fits(pp) and not seen.has(i):
				seen[i] = true
				bad += 1
				printerr("PEOPLEWALL walker %d in a wall at (%.1f, %.1f)" % [i, pp.x, pp.z])
	printerr("PEOPLEWALLS %d in walls (story characters %d, walkers %d)" % [bad, n, m.people.people.size()])
	end_test()


func what_at(p: Vector3) -> String:
	# what a person standing here touches: each solid thing's node name and its box's centre
	var q := PhysicsShapeQueryParameters3D.new()
	var sh := SphereShape3D.new()
	sh.radius = 0.3
	q.shape = sh
	q.collision_mask = m.LAYER_BODY
	q.transform = Transform3D(Basis(), Vector3(p.x, 0.6, p.z))
	var out := []
	for hit in m.get_world_3d().direct_space_state.intersect_shape(q, 8):
		if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D:
			var o: Object = hit.collider
			var cs = (o as Node).get_child(hit.shape) if hit.shape < (o as Node).get_child_count() else null
			out.append("%s%s" % [(o as Node).name, (" box at (%.1f, %.1f)" % [cs.global_position.x, cs.global_position.z]) if cs is Node3D else ""])
	return ", ".join(out)


func run_trapsim(spec: String) -> void:
	# (round 40, the user: "review any dead spots around the house… There are random places where I got stuck when I
	# ran around it. You should be able to run around the whole area, specifically up against the fence")
	# --trapsim=<png>:x0,z0,x1,z1[,cell] — the trap test by her own walking, nothing assumed: on every spot of a grid
	# she is put down and really walks a step each of eight ways (the game's own physics, slopes, slides and walls);
	# where she ends is a step she can take. Out = the area's edge, or the gate plaza; a spot from which no chain of
	# steps reaches out is a trap. Run it with --fixed-fps 60 so it goes as fast as the machine can.
	var parts := spec.split(":")
	var path: String = parts[0]
	var v := parts[1].split(",")
	var R := Rect2(float(v[0]), float(v[1]), float(v[2]) - float(v[0]), float(v[3]) - float(v[1]))
	var cs: float = float(v[4]) if v.size() > 4 else 1.0
	await old_walls()
	await get_tree().create_timer(3.0).timeout
	var nx := int(R.size.x / cs)
	var nz := int(R.size.y / cs)
	var pl := m.player
	var space := pl.get_world_3d().direct_space_state
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = pl.get_child(0).shape
	q.collision_mask = m.LAYER_BODY
	q.exclude = [pl.get_rid(), m.tree_body.get_rid()]
	var stand := PackedByteArray()
	stand.resize(nx * nz)
	for i in nx * nz:
		var x: float = R.position.x + (i % nx + 0.5) * cs
		var z: float = R.position.y + (i / nx + 0.5) * cs
		q.transform = Transform3D(Basis(), Vector3(x, 0.82, z))
		var ok := true
		for hit in space.intersect_shape(q, 4):
			if hit.collider is StaticBody3D:
				ok = false
		stand[i] = 1 if ok else 0
	# (",smart": open, gentle ground with nothing built within 1.5 m is simply open to its eight neighbours; she is
	# walked only where there is a slope or something built near — the whole park in a fraction of the time)
	var smart := v.size() > 5 and v[5] == "smart"
	var qn := PhysicsShapeQueryParameters3D.new()
	var sph := SphereShape3D.new()
	sph.radius = 1.5
	qn.shape = sph
	qn.collision_mask = m.LAYER_BODY
	qn.exclude = [pl.get_rid(), m.tree_body.get_rid()]
	var edges := []
	edges.resize(nx * nz)
	var t0 := Time.get_ticks_msec()
	var done := 0
	var easy_n := 0
	var froze := 0
	for i in nx * nz:
		edges[i] = PackedInt32Array()
		if stand[i] == 0:
			continue
		var x: float = R.position.x + (i % nx + 0.5) * cs
		var z: float = R.position.y + (i / nx + 0.5) * cs
		if smart:
			var easy := true
			qn.transform = Transform3D(Basis(), Vector3(x, 2.4, z))     # (above the floor: the first run hit it everywhere)
			for hit in space.intersect_shape(qn, 4):
				if hit.collider is StaticBody3D:
					easy = false
			if easy:
				for o in [Vector3(0, 0, 0), Vector3(cs, 0, 0), Vector3(-cs, 0, 0), Vector3(0, 0, cs), Vector3(0, 0, -cs)]:
					if m.north.gradient(Vector3(x, 0, z) + o).length() > 0.3:
						easy = false
			if easy:
				easy_n += 1
				for k in 8:
					var jx: int = i % nx + [1, 1, 0, -1, -1, -1, 0, 1][k]
					var jz: int = i / nx + [0, 1, 1, 1, 0, -1, -1, -1][k]
					if jx < 0 or jz < 0 or jx >= nx or jz >= nz:
						edges[i].append(-2)
					elif stand[jz * nx + jx] == 1:
						edges[i].append(jz * nx + jx)
				continue
		for k in 8:
			var a := k * PI / 4.0
			place(x, z, a)
			m.model.position.y = m.ground_at(m.player.global_position)
			var on_roof := m.deck_at(x, z, INF)
			if not is_nan(on_roof):
				m.model.position.y = on_roof              # (the covered walk's roof: she is up on it, as she gets there
				#  from the hill behind; under it is no place she can be — the first run put her there)
			m.vkeys[KEY_W] = true
			for f in 27:
				await get_tree().physics_frame
			m.vkeys.erase(KEY_W)
			var pp := m.player.global_position
			if m.where != "out" or m.dlg_open or m.busy or m.cutscene:
				# (the first whole-park run: a step took her in by a door and she stayed inside for the rest, so every
				# spot after it read as a trap. A door, a talk or a scene is no way out of a pit: no step that way)
				froze += 1
				if m.where != "out":
					m.leave()
					await get_tree().create_timer(1.0).timeout
				if m.dlg_open:
					m.close_dialog()
				m.busy = false
				m.cutscene = false
				m.fp_on = false
				continue
			var jx := floori((pp.x - R.position.x) / cs)
			var jz := floori((pp.z - R.position.y) / cs)
			var j := -2                                   # (-2: out of the area)
			if jx >= 0 and jz >= 0 and jx < nx and jz < nz:
				j = jz * nx + jx
			if j != i:
				edges[i].append(j)
		done += 1
		if done % 50 == 0:
			printerr("TRAPSIM %d spots, %.0f s" % [done, (Time.get_ticks_msec() - t0) / 1000.0])
	# (round 40, the user: "check all of the ways she can walk to the railway lines. Because she should not be able to
	# access it from anywhere") --reachfrom=x,z --forbid=x0,z0,x1,z1[;...]: instead of traps, where she can get to from
	# one spot by her own walking, and every such spot inside a forbidden strip (the funicular's track)
	var reach_from := ""
	var forbid := []
	for ua in OS.get_cmdline_user_args():
		if ua.begins_with("--reachfrom="):
			reach_from = ua.trim_prefix("--reachfrom=")
		elif ua.begins_with("--forbid="):
			for fr in ua.trim_prefix("--forbid=").split(";"):
				var fv := fr.split(",")
				forbid.append(Rect2(float(fv[0]), float(fv[1]), float(fv[2]) - float(fv[0]), float(fv[3]) - float(fv[1])))
	if reach_from != "":
		var rf := reach_from.split(",")
		var si := clampi(int((float(rf[1]) - R.position.y) / cs), 0, nz - 1) * nx + clampi(int((float(rf[0]) - R.position.x) / cs), 0, nx - 1)
		var seen := PackedByteArray()
		seen.resize(nx * nz)
		seen[si] = 1
		var todo := [si]
		var edge_out := false
		while not todo.is_empty():
			var c: int = todo.pop_back()
			for j in edges[c]:
				if j == -2:
					edge_out = true
				elif j >= 0 and seen[j] == 0 and stand[j] == 1:
					seen[j] = 1
					todo.append(j)
		var img2 := Image.create(nx, nz, false, Image.FORMAT_RGB8)
		var hits := 0
		for i in nx * nz:
			var c0 := Vector2(R.position.x + (i % nx + 0.5) * cs, R.position.y + (i / nx + 0.5) * cs)
			var bad_spot := false
			for fr in forbid:
				if (fr as Rect2).has_point(c0):
					bad_spot = true
			var col := Color(0.05, 0.05, 0.05)
			if stand[i] == 1:
				col = Color(0.75, 0.85, 0.7) if seen[i] == 1 else Color(0.55, 0.55, 0.6)
				if bad_spot:
					col = Color(0.95, 0.1, 0.1) if seen[i] == 1 else Color(0.95, 0.75, 0.2)
			img2.set_pixel(i % nx, i / nx, col)
			if seen[i] == 1 and bad_spot:
				hits += 1
				printerr("REACHED forbidden at (%.1f, %.1f)" % [c0.x, c0.y])
		img2.save_png(path)
		printerr("REACH map %s: from (%s), %d forbidden spots reached; the area's edge %s; %.0f s" % [path, reach_from, hits,
			"reached" if edge_out else "not reached", (Time.get_ticks_msec() - t0) / 1000.0])
		end_test()
		return
	# out: off the area, or the gate plaza's middle
	var good := PackedByteArray()
	good.resize(nx * nz)
	for i in nx * nz:
		var c0 := Vector2(R.position.x + (i % nx + 0.5) * cs, R.position.y + (i / nx + 0.5) * cs)
		if stand[i] == 1 and c0.distance_to(Vector2(106.0, -146.0)) < 3.0:
			good[i] = 1                                   # (the gate plaza: the park's way out)
	var changed := true
	while changed:
		changed = false
		for i in nx * nz:
			if good[i] == 1 or stand[i] == 0:
				continue
			for j in edges[i]:
				if j == -2 or (j >= 0 and good[j] == 1):
					good[i] = 1
					changed = true
					break
	var img := Image.create(nx, nz, false, Image.FORMAT_RGB8)
	var bad := []
	for i in nx * nz:
		var c := Color(0.05, 0.05, 0.05)
		if stand[i] == 1:
			c = Color(0.75, 0.85, 0.7) if good[i] == 1 else Color(0.95, 0.1, 0.1)
			if good[i] == 0:
				bad.append(Vector2(R.position.x + (i % nx + 0.5) * cs, R.position.y + (i / nx + 0.5) * cs))
		img.set_pixel(i % nx, i / nx, c)
	img.save_png(path)
	printerr("TRAPSIM map %s (%d x %d, %.1f m a pixel, from x %.1f z %.1f): %d trapped spots; %d walked, %d open ground, %d steps through a door or into a talk, %.0f s" % [path, nx, nz, cs,
		R.position.x, R.position.y, bad.size(), done, easy_n, froze, (Time.get_ticks_msec() - t0) / 1000.0])
	for b in bad:
		printerr("TRAPPED at (%.1f, %.1f)" % [b.x, b.y])
	end_test()


func run_kitetalk(dir: String) -> void:
	# (round 41) the kite flyer: from the side and from in front while he flies it (arm up, the line from his hand to
	# the kite), then while Sandra talks to him (his head down to her, the kite still up)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660)
	var q: Dictionary = m.npcs.outdoor.get("albert", {})
	if q.is_empty():
		printerr("KITETALK no albert")
		end_test()
		return
	var h: Node3D = q.holder
	var f := Basis(Vector3.UP, h.rotation.y) * Vector3(0, 0, 1)            # the way he faces
	var sd := f.cross(Vector3.UP)
	place(h.global_position.x - f.x * 6.0, h.global_position.z - f.z * 6.0, 0.0)
	q.target = h.position
	q.wait = 100.0
	var cam := Camera3D.new()
	add_child(cam)
	cam.far = 300.0
	cam.current = true
	var p0 := h.global_position
	for v in [["side", sd * 7.0 + Vector3(0, 2.2, 0) - f * 1.0, p0 + Vector3(0, 3.2, 0) + f * 1.8],
			["front", f * 5.5 + sd * 1.5 + Vector3(0, 1.6, 0), p0 + Vector3(0, 1.4, 0)],
			["sky", -f * 4.0 + sd * 2.0 + Vector3(0, 1.4, 0), p0 + Vector3(0, 5.5, 0) + f * 4.0]]:
		cam.global_position = p0 + v[1]
		cam.look_at(v[2], Vector3.UP)
		await shot(dir, "kite_" + v[0])
	# Sandra beside him, talking
	var me: Vector3 = p0 + sd * 1.6 + f * 0.6
	place(me.x, me.z, 0.0)
	m.npcs.face("albert", m.player.global_position)
	await get_tree().create_timer(2.5).timeout
	var to := (me - p0).normalized()
	cam.global_position = p0 + to * 2.2 + to.cross(Vector3.UP) * 2.4 + Vector3(0, 1.5, 0)
	cam.look_at((p0 + me) / 2.0 + Vector3(0, 1.0, 0), Vector3.UP)
	await shot(dir, "kite_talk")
	cam.global_position = p0 + to * 4.0 - to.cross(Vector3.UP) * 3.5 + Vector3(0, 2.4, 0)
	cam.look_at(p0 + Vector3(0, 3.0, 0) + f * 1.5, Vector3.UP)
	await shot(dir, "kite_talk_wide")
	# close in on him from three sides while he talks: the hand on the line in view
	var sdt := to.cross(Vector3.UP)
	for c in [["near_a", to * 2.4 + sdt * 0.6], ["near_b", to * 1.2 - sdt * 2.2], ["near_c", -to * 0.4 + sdt * 2.4]]:
		cam.global_position = p0 + c[1] + Vector3(0, 1.3, 0)
		cam.look_at(p0 + Vector3(0, 1.0, 0), Vector3.UP)
		await shot(dir, "kite_talk_" + c[0])
	# and up close while he flies it, from in front and his right
	m.player.global_position = p0 - f * 8.0
	m.npcs.outdoor.albert.talking = false
	await get_tree().create_timer(2.5).timeout
	for c in [["fly_front", f * 2.6 - sd * 1.0], ["fly_right", -sd * 2.6 + f * 0.6]]:
		cam.global_position = p0 + c[1] + Vector3(0, 1.4, 0)
		cam.look_at(p0 + Vector3(0, 1.3, 0), Vector3.UP)
		await shot(dir, "kite_" + c[0])
	printerr("KITETALK head_aim=%.2f talking=%s" % [float(q.m.posture.head_aim), q.talking])
	end_test()


func run_wheelride(dir: String) -> void:
	# (round 41, the user: "ride the Ferris wheel and take pictures… make her body sit correctly on it") once round the
	# Giradabo: the game's own camera, and a camera close beside her gondola, at the boarding, a quarter up, the top, a
	# quarter down and getting out
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660)
	var W: Dictionary = m.D.north.wheel
	# (round 41) as a player: walk up to the gate, E, pay
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	var money0: int = m.game.S.money
	m.north.act("wheel")
	await talk_through([0])
	printerr("WHEELRIDE gate: paid %d, riding=%s" % [money0 - m.game.S.money, not m.north.ride.is_empty()])
	var own: Camera3D = get_viewport().get_camera_3d()
	var cam := Camera3D.new()
	add_child(cam)
	cam.far = 600.0
	var marks := {"1_board": "board", "2_quarter": 0.25, "3_top": 0.5, "4_down": 0.75, "5_out": "out"}
	var t0 := Time.get_ticks_msec()
	for k in marks.keys():
		var want = marks[k]
		while Time.get_ticks_msec() - t0 < 120000:
			var r: Dictionary = m.north.ride
			if r.is_empty():
				break
			if want is String and String(r.get("phase", "")) == want:
				break
			if not (want is String) and String(r.get("phase", "")) == "round" and float(r.get("turned", 0.0)) >= TAU * float(want):
				break
			await get_tree().process_frame
		var spd: float = m.north.wheel_speed
		m.north.wheel_speed = 0.0                       # (held still for the pictures)
		own.current = true
		await shot(dir, k + "_game")
		var her: Vector3 = m.player.global_position
		if m.north.ride.is_empty():
			her = m.model.global_position
		cam.global_position = her + Vector3(0.5, 0.75, 2.4)
		cam.look_at(her + Vector3(0, 0.45, 0), Vector3.UP)
		cam.current = true
		await shot(dir, k + "_front")
		cam.global_position = her + Vector3(2.3, 0.7, 0.7)
		cam.look_at(her + Vector3(0, 0.4, 0.1), Vector3.UP)
		await shot(dir, k + "_side")
		own.current = true
		if k == "3_top":
			# first person at the top (E), then the camera taken round her with the right arrow, back in third person
			m.ride_look = true
			m.model.visible = false
			for qa in 4:                                 # (looking out every way, a quarter at a time)
				m.cam_yaw_node.rotation.y = PI + qa * PI / 2.0
				m.cam_pitch_node.rotation.x = -0.15
				m.last_manual_cam = m.t
				await shot(dir, k + "_firstperson%d" % qa)
			m.ride_look = false
			m.model.visible = true
			for qa in 4:                                 # (the camera taken round her, a quarter at a time)
				m.cam_yaw_node.rotation.y = PI + qa * PI / 2.0
				m.last_manual_cam = m.t
				await shot(dir, k + "_round%d" % qa)
		m.north.wheel_speed = spd
		printerr("WHEELRIDE %s phase=%s turned=%.2f her=%s model_y=%.2f" % [k, m.north.ride.get("phase", "-"), float(m.north.ride.get("turned", 0.0)), her, m.model.position.y])
	end_test()


func run_wheelseat(dir: String) -> void:
	# (round 41) her seated pose in the bottom gondola, close, from six sides and from above, the gondola's roof and tub
	# hidden in the second set so her limbs show
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660)
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.start_wheel()
	while not m.north.ride.is_empty() and String(m.north.ride.get("phase", "")) != "board":
		await get_tree().process_frame
	m.north.wheel_speed = 0.0
	await get_tree().create_timer(1.5).timeout
	var cam := Camera3D.new()
	add_child(cam)
	cam.far = 300.0
	var her: Vector3 = m.player.global_position
	var g: Node3D = m.north.gondolas[int(m.north.ride.g)]
	# where her arm joints are, in the gondola's own space (x across, y up, z the way she faces)
	var skel: Skeleton3D = m.skins[m.skin_idx].root.find_children("*", "Skeleton3D", true, false)[0]
	for i in skel.get_bone_count():
		var nm := skel.get_bone_name(i)
		if "Left" in nm and ("Shoulder" in nm or "Arm" in nm or "Hand" in nm) or "Hips" in nm or "Head" in nm and not "Top" in nm:
			print("SEATBONE %s %s" % [nm, g.to_local(skel.global_transform * m.north.seat.pose.gxf(i).origin)])
	for pass_ in 2:
		if pass_ == 1:
			g.visible = false
		for v in [["front", Vector3(0, 0.3, 1.6)], ["side", Vector3(1.6, 0.3, 0.2)], ["back", Vector3(0, 0.6, -1.8)], ["above", Vector3(0.2, 1.6, 0.5)]]:
			cam.global_position = her + v[1]
			cam.look_at(her + Vector3(0, 0.3, 0), Vector3.UP)
			cam.current = true
			await shot(dir, "%s_%s" % ["gondola" if pass_ == 0 else "bare", v[0]])
	end_test()


func run_wheelpeak(dir: String) -> void:
	# (round 41, the user: "take some pictures looking out from the gondola at night, as well as day… More pictures in
	# different angles, right at the peak") at the top of the wheel, held there: by day and at night, her own eyes every
	# eighth of a turn (and one looking down), and the camera behind her from four sides
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660)
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.start_wheel()
	while not m.north.ride.is_empty() and not (String(m.north.ride.get("phase", "")) == "round" and float(m.north.ride.get("turned", 0.0)) >= PI):
		await get_tree().process_frame
	m.north.wheel_speed = 0.0
	for tm in [["day", 660], ["night", 1350]]:
		m.set_clock(tm[1])
		await get_tree().create_timer(1.5).timeout
		m.ride_look = true
		m.model.visible = false
		for qa in 8:
			m.cam_yaw_node.rotation.y = PI + qa * PI / 4.0
			m.cam_pitch_node.rotation.x = -0.12
			m.last_manual_cam = m.t
			await shot(dir, "%s_eyes_%d" % [tm[0], qa * 45])
		for wa in [250, 265, 280, 295]:                 # (round 41: towards the valley in the west, closer steps)
			m.cam_yaw_node.rotation.y = PI + deg_to_rad(wa)
			m.cam_pitch_node.rotation.x = -0.1
			await shot(dir, "%s_eyes_w%d" % [tm[0], wa])
		m.cam_yaw_node.rotation.y = PI
		m.cam_pitch_node.rotation.x = -0.9
		await shot(dir, "%s_eyes_down" % tm[0])
		m.ride_look = false
		m.model.visible = true
		for qa in 4:
			m.cam_yaw_node.rotation.y = PI + qa * PI / 2.0
			m.cam_pitch_node.rotation.x = -0.25
			m.last_manual_cam = m.t
			await shot(dir, "%s_behind_%d" % [tm[0], qa * 90])
	end_test()


func run_camprobe() -> void:
	# (round 41, the user: "make the trees not be like walls"; "Lamp posts should also not be treated as hard walls")
	# a street lamp or tree 1 m behind her, the camera's arm reaching back through it: how long the arm is (and, as a
	# control, 4 m further on along the same line, nothing behind)
	await get_tree().create_timer(3.0).timeout
	var things := []
	var fair := "--camprobe=fair" in OS.get_cmdline_user_args()
	for l in (m.D.lamps.filter(func(q): return float(q.pos[1]) < -200.0) if fair else m.D.lamps.slice(0, 40, 6)):
		things.append(["lamp", Vector2(l.pos[0], l.pos[1])])
	for t in ([] if fair else m.D.trees.slice(0, 60, 9)):
		things.append(["tree", Vector2(t[0], t[1])])
	for th in things:
		var c: Vector2 = th[1]
		for a in [0.0, PI / 2.0, PI, -PI / 2.0]:
			var d := Vector2(sin(a), cos(a))
			var res := []
			for extra in [1.0, 5.0]:
				var p: Vector2 = c + d * extra
				place(p.x, p.y, a)
				await get_tree().create_timer(1.2).timeout
				res.append("%.2f/%.2f" % [m.arm.get_hit_length(), m.arm.spring_length])
			printerr("CAMPROBE %s (%.1f,%.1f) dir %.2f: behind %s  clear %s" % [th[0], c.x, c.y, a, res[0], res[1]])
	end_test()


func run_funiquick(dir: String) -> void:
	# (round 41) boarding the funicular at dusk: the fade, the car standing a moment then gathering speed (where it is,
	# every quarter second), the view round the car, her seat inside with the tinted glass, by night and by day
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	m.set_clock(1290.0)
	var down := "--funidown" in OS.get_cmdline_user_args()
	var d: Array = m.D.north.cable.door_top if down else m.D.north.cable.door_low
	place(d[0], d[1] + (-1.0 if down else 1.0), 0.0 if down else PI)
	await get_tree().create_timer(0.5).timeout
	m.north.start_cable(not down)
	for k in 26:
		await get_tree().create_timer(0.25).timeout
		printerr("FUNIQ t=%.2f black=%.2f ride_t=%.4f cable_t=%.4f prompt=%s" % [(k + 1) * 0.25, m.fade.color.a,
			float(m.north.ride.get("t", -1.0)), m.north.cable_t, m.prompt.text])
		if k == 2:
			shot(dir, "0_dark")
		if k == 11:
			shot(dir, "1_outside_standing")
	await get_tree().create_timer(2.0).timeout
	await shot(dir, "2_outside_moving")
	m.north.ride_toggle()
	await get_tree().create_timer(1.0).timeout
	await shot(dir, "3_inside_dusk")
	printerr("FUNIQ inside prompt=%s" % m.prompt.text)
	m.set_clock(660.0)
	await get_tree().create_timer(1.0).timeout
	await shot(dir, "4_inside_day")
	m.cam_yaw_node.rotation.y = PI - 1.2
	m.last_manual_cam = m.t
	await shot(dir, "5_inside_day_side")
	m.cam_yaw_node.rotation.y = 0.0
	m.cam_pitch_node.rotation.x = 0.1
	m.last_manual_cam = m.t
	await shot(dir, "6_inside_looking_back")
	end_test()


func run_probejoan() -> void:
	# (round 42, the user: "I can't trigger the torró mission") with the test save a copy of the live one: walk into
	# Casa Joan, what E offers, talk to Joan, and whether the mission starts
	await get_tree().create_timer(3.0).timeout
	var g := m.game
	printerr("PROBE gift done=%s rivalry=%s open=%s" % [g.m_done("gift"), g.S.missions.get("rivalry", "none"), g.m_done("gift")])
	await go_in(entrance("int_torro_joan"))
	await get_tree().create_timer(0.5).timeout
	printerr("PROBE in room=%s offers=%s" % [m.room, m.nearest().get("label", "nothing")])
	var j = m.npcs.room_people().get("joan") if m.npcs.has_method("room_people") else null
	printerr("PROBE joan present=%s" % [j != null])
	for k in ["W", "W", "W"]:
		await hold(KEY_W, 0.5)
		printerr("PROBE at %s offers=%s" % [m.player.global_position, m.nearest().get("label", "nothing")])
	await talk("joan")
	printerr("PROBE after talk: rivalry=%s objective=%s" % [g.S.missions.get("rivalry", "none"), g.objective_text()])
	end_test()


func run_armshots(dir: String) -> void:
	# (round 41, the user: "could you make Sandra's arms slightly shorter? Give me some examples… sitting at her desk
	# doing the exam. As well as sitting on the bike. And any other places") with --armk=: standing, from the front and
	# the side, on the street before Maria's; on the bike there, from the side; sitting on the nearest bench, from the
	# front (the exam: --exam=)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.apply_preset("day")
	var sp := Vector2(10.0, 81.5)
	place(sp.x, sp.y, PI / 2.0, PI / 2.0)                 # (facing east along the street; the camera before her)
	m.cam_len = 3.0
	await get_tree().create_timer(1.5).timeout
	await shot(dir, "1_standing_front")
	m.cam_yaw_node.rotation.y = 0.0
	await shot(dir, "2_standing_side")
	m.game.S["has_bike"] = true
	m.bike_key()
	await get_tree().create_timer(1.5).timeout
	m.cam_yaw_node.rotation.y = 0.0
	m.last_manual_cam = m.t
	await shot(dir, "3_bike_side")
	m.cam_yaw_node.rotation.y = 0.6
	m.last_manual_cam = m.t
	await shot(dir, "4_bike_front")
	m.bike_key()
	await get_tree().create_timer(1.0).timeout
	var best := -1
	var bd := INF
	for i in m.benches.list.size():
		var dd: float = (m.benches.list[i][0] as Vector2).distance_to(sp)
		if dd < bd:
			bd = dd
			best = i
	var b: Array = m.benches.list[best]
	var fr: Vector2 = b[0] + b[1] * 0.75
	place(fr.x, fr.y, atan2(-b[1].x, -b[1].y))
	await get_tree().create_timer(1.0).timeout
	m.benches.sit(best)
	await get_tree().create_timer(1.0).timeout
	var skx: Skeleton3D = m.skins[m.skin_idx].root.find_children("*", "Skeleton3D", true, false)[0]
	for bn in ["Hips", "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftHand"]:
		var bi := skx.find_bone(m.street_bone(skx, bn))
		var gp: Vector3 = skx.global_transform * skx.get_bone_global_pose(bi).origin
		printerr("BENCHPOSE %s at (%.2f, %.2f, %.2f)" % [bn, gp.x, gp.y, gp.z])
	var pz: SkeletonModifier3D = m.benches.pose
	printerr("BENCHPOSE pose active=%s runs=%d parent=%s skel=%s bones=%s" % [pz.active, pz.runs, pz.get_parent().name, skx.name, pz.b])
	printerr("BENCHPOSE seat h %.2f bench at (%.2f, %.2f) faces (%.2f, %.2f) player y %.2f model y %.2f" % [float(b[2]), b[0].x, b[0].y, b[1].x, b[1].y,
		m.player.global_position.y, m.model.global_position.y])
	for k in m.benches.marks.size():
		var mk: Node3D = m.benches.marks[k]
		printerr("BENCHPOSE mark %d at (%.2f, %.2f, %.2f)" % [k, mk.global_position.x, mk.global_position.y, mk.global_position.z])
	m.benches.pose.hide_head = false
	m.ride_look = false
	m.cam_yaw_node.rotation.y = atan2(b[1].x, b[1].y) + 0.5
	m.cam_pitch_node.rotation.x = -0.2
	await shot(dir, "5_bench_front")
	m.ride_look = true
	m.benches.pose.hide_head = true
	m.cam_yaw_node.rotation.y = atan2(b[1].x, b[1].y) + PI
	m.cam_pitch_node.rotation.x = -1.0
	await shot(dir, "6_bench_looking_down")
	m.ride_look = false
	m.benches.pose.hide_head = false
	var f3 := Vector3(b[1].x, 0.0, b[1].y)
	var sd3 := Vector3(-f3.z, 0.0, f3.x)
	var mid3 := Vector3(b[0].x, float(b[2]), b[0].y)
	var cam3 := Camera3D.new()
	cam3.fov = 45.0
	m.add_child(cam3)
	cam3.global_position = mid3 + sd3 * 2.0 + f3 * 0.35 + Vector3(0, 0.45, 0)
	cam3.look_at(mid3 + f3 * 0.15 + Vector3(0, -0.05, 0), Vector3.UP)
	cam3.current = true
	await shot(dir, "7_bench_side")
	cam3.global_position = mid3 + f3 * 1.6 + sd3 * 0.5 + Vector3(0, 0.2, 0)
	cam3.look_at(mid3 + Vector3(0, -0.05, 0), Vector3.UP)
	await shot(dir, "8_bench_front_low")
	cam3.fov = 35.0
	cam3.global_position = mid3 + sd3 * 2.6 + f3 * 0.25 + Vector3(0, 0.25, 0)
	cam3.look_at(mid3 + f3 * 0.25 + Vector3(0, 0.25, 0), Vector3.UP)
	await shot(dir, "9_bench_profile")
	end_test()

func run_probebrush() -> void:
	# (the user: "Where is the brush in the park? It is not there") with the live save copied in
	await get_tree().create_timer(3.0).timeout
	var g := m.game
	printerr("PROBE brush mission=%s has=%s taken=%s" % [g.S.missions.get("brush", "none"), g.has_item("brush"), g.S.get("taken", [])])
	for gr in g.ground:
		if gr.id == "brush":
			printerr("PROBE brush node at %s visible=%s ground there %.2f" % [gr.node.global_position, gr.node.visible, m.ground_at(gr.pos)])
			place(gr.pos.x - 1.0, gr.pos.z, -PI / 2.0)
			await get_tree().create_timer(0.4).timeout
			printerr("PROBE beside it: E offers %s" % m.nearest().get("label", "nothing"))
			get_viewport().get_texture().get_image().save_png("/tmp/brush_probe.png")
	end_test()


func run_probemarta() -> void:
	# (the user: the camera mission "I can't start it") with the live save copied in: where Marta is, what E offers
	await get_tree().create_timer(3.0).timeout
	var g := m.game
	printerr("PROBE camera=%s gift done=%s" % [g.S.missions.get("camera", "none"), g.m_done("gift")])
	await go_in(entrance("int_batllo"))
	await get_tree().create_timer(0.5).timeout
	printerr("PROBE in %s, E offers %s" % [m.room, m.nearest().get("label", "nothing")])
	for id in m.npcs.current():
		var qq: Dictionary = m.npcs.current()[id]
		if not qq.is_empty():
			printerr("PROBE %s at %s visible=%s" % [id, qq.holder.global_position - m.room_base(m.room), qq.holder.visible])
	get_viewport().get_texture().get_image().save_png("/tmp/marta_probe.png")
	await talk("marta")
	printerr("PROBE after talk: camera=%s objective=%s" % [g.S.missions.get("camera", "none"), g.objective_text()])
	end_test()


func cam_inside() -> String:
	# where the camera is, against what it shouldn't be in: the ground under it, a building the build lists for the camera
	var cp := get_viewport().get_camera_3d().global_position
	var out := ""
	var th: float = m.terrain_at(cp.x, cp.z)
	var cf: float = m.north.cutting_floor(cp.x, cp.z)
	if not is_nan(cf):
		th = cf                                         # (along the funicular's cutting its floor is the ground)
	if cp.y < th + 0.1:
		out += " UNDERGROUND(%.2f)" % (th - cp.y)
	for b in m.D.get("cam_buildings", []):
		var r: Array = b.r
		if cp.x > r[0] and cp.x < r[2] and cp.z > r[1] and cp.z < r[3] and cp.y > float(b.lo) and cp.y < float(b.hi):
			out += " IN_BUILDING%s" % [r]
	return out


func run_funitoggle(dir: String) -> void:
	# (round 41, the user: "Try riding the [funicular] a few times, and press e to come in and out, especially when you
	# are arriving and leaving. We want to avoid the cutting through objects") up and down twice, E pressed at set
	# moments (leaving, mid-way, the last seconds of arriving); at each: a picture, where the camera is, and whether
	# it is inside the ground or a building
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	m.set_clock(660.0)
	var N: Dictionary = m.D.north
	var ride_s := float(N.cable.ride_s)
	var bad := 0
	for run in 2:
		for leg in ["up", "down"]:
			var d: Array = N.cable.door_low if leg == "up" else N.cable.door_top
			place(d[0], d[1] + (1.0 if leg == "up" else -1.0), PI if leg == "up" else 0.0)
			await get_tree().create_timer(0.6).timeout
			m.north.start_cable(leg == "up")
			while m.north.ride.is_empty():                   # (aboard once the screen has gone dark)
				await get_tree().process_frame
			var marks := [1.5, 3.0, ride_s * 0.5] if run == 0 else [2.2, ride_s * 0.8]
			marks += [ride_s - 3.0, ride_s - 2.0, ride_s - 1.2, ride_s - 0.6]
			var t0 := m.t
			var k := 0
			for mk in marks:
				while m.t - t0 < float(mk) and not m.north.ride.is_empty():
					await get_tree().process_frame
				if m.north.ride.is_empty():
					break
				m.north.ride_toggle()                       # (E, as the player presses it)
				for f in 12:
					await get_tree().process_frame
					var bad_s := cam_inside()
					if bad_s != "":
						bad += 1
						printerr("FUNIT run%d %s t=%.2f look=%s frame %d%s" % [run, leg, m.t - t0, m.ride_look, f, bad_s])
				var cp := get_viewport().get_camera_3d().global_position
				printerr("FUNIT run%d %s t=%.2f look=%s cam=(%.1f,%.1f,%.1f) arm=%.2f black=%.2f%s" % [run, leg, m.t - t0, m.ride_look,
					cp.x, cp.y, cp.z, m.arm.get_hit_length(), m.fade.color.a, cam_inside()])
				get_viewport().get_texture().get_image().save_jpg(dir.path_join("r%d_%s_%02d_%s.jpg" % [run, leg, k, "in" if m.ride_look else "out"]), 0.85)
				k += 1
			while not m.north.ride.is_empty():
				await get_tree().process_frame
				var bad_e := cam_inside()
				if bad_e != "" and m.fade.color.a < 0.95:
					bad += 1
					printerr("FUNIT run%d %s arriving t=%.2f look=%s black=%.2f%s" % [run, leg, m.t - t0, m.ride_look, m.fade.color.a, bad_e])
			for f in 40:
				await get_tree().process_frame
				var bad_o := cam_inside()
				if bad_o != "" and m.fade.color.a < 0.95:
					bad += 1
					printerr("FUNIT run%d %s off frame %d black=%.2f%s" % [run, leg, f, m.fade.color.a, bad_o])
			await get_tree().create_timer(1.0).timeout
			get_viewport().get_texture().get_image().save_jpg(dir.path_join("r%d_%s_off.jpg" % [run, leg]), 0.85)
			printerr("FUNIT run%d %s off at (%.1f,%.1f) model=%s" % [run, leg, m.player.global_position.x, m.player.global_position.z, m.model.visible])
	printerr("FUNIT done: %d bad camera frames (visible, not under black)" % bad)
	end_test()


func run_funicar(dir: String) -> void:
	# (round 41) the car parked partway up, pictured from cameras of its own placed in its frame: both glass noses with
	# their red bands, a side with its doors, and inside (up the car over the benches; out of a window, the tint)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.north.cable_t = 0.3
	m.north.cable_wait = 999.0
	m.north.place_cabins()
	var cab: Node3D = m.north.cabins[0]
	place(cab.global_position.x + 6.0, cab.global_position.z, 0.0)
	await get_tree().create_timer(1.5).timeout
	var cam := Camera3D.new()
	cam.fov = 50.0
	m.add_child(cam)
	cam.current = true
	# (the car's own frame: up the car is -z, and its floor and roof rise 0.46 m for every metre up it)
	var gr := 0.46
	for v in [["2_nose_upper", Vector3(-2.2, 8.5, -8.0), Vector3(0, 1.6 + 3.6 * gr, -3.6)],
			["4_inside_up_car", Vector3.INF, Vector3(0, 1.3 + 3.0 * gr, -3.0)]]:
		m.north.place_cabins()
		var at: Vector3 = m.north.seat_point() + Vector3(0, 0.1, 0) if v[1] == Vector3.INF else cab.global_transform * (v[1] as Vector3)
		cam.global_position = at
		cam.look_at(cab.global_transform * (v[2] as Vector3), Vector3.UP)
		await shot(dir, v[0])
	end_test()


func run_fpkeys() -> void:
	# (round 41, the user: "make the up and down inverted… They should all be the same") in each first-person view, ↑
	# held for half a second: which way the view tips (down: inverted), and ← (which way it turns)
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var b: Array = m.benches.list[0]
	var fr: Vector2 = b[0] + b[1] * 0.75
	place(fr.x, fr.y, 0.0)
	await get_tree().create_timer(0.5).timeout
	m.benches.sit(0)
	await get_tree().create_timer(0.8).timeout
	await fp_probe("bench")
	m.benches.stand()
	var d: Array = m.D.north.cable.door_low
	place(d[0], d[1] + 1.0, PI)
	await get_tree().create_timer(0.5).timeout
	m.north.start_cable(true)
	await get_tree().create_timer(2.5).timeout
	m.north.ride_toggle()
	await get_tree().create_timer(0.8).timeout
	await fp_probe("funicular")
	end_test()


func fp_probe(what: String) -> void:
	var p0: float = m.cam_pitch_node.rotation.x
	await hold(KEY_UP, 0.5)
	var p1: float = m.cam_pitch_node.rotation.x
	var y0: float = m.cam_yaw_node.rotation.y
	await hold(KEY_LEFT, 0.5)
	var y1: float = m.cam_yaw_node.rotation.y
	printerr("FPKEYS %s: up -> pitch %+.2f (%s), left -> yaw %+.2f, prompt '%s'" % [what, p1 - p0, "looks down" if p1 < p0 else "looks UP",
		wrapf(y1 - y0, -PI, PI), m.prompt.text])


func run_stationcam(dir: String) -> void:
	# (round 41, the user: "make the walls of the funicular building actual walls that the camera doesn't go into, but
	# pushes closer to her") at each station, standing by a wall facing away from it (the camera behind her, against
	# it): the camera's arm, where the camera is, whether it is inside the building, a picture
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	var spots := [["low_door", -68.2, -98.6, 0.0], ["low_east", -60.2, -104.5, PI / 2.0], ["low_west", -71.8, -104.5, -PI / 2.0],
		["low_platform", -64.0, -110.0, PI], ["low_back_corner", -61.2, -109.2, PI * 0.75],
		["top_front", -65.7, -279.4, 0.0], ["top_front_east", -63.0, -279.6, 0.4], ["top_east", -61.8, -276.0, PI / 2.0],
		["top_west", -70.2, -276.0, -PI / 2.0]]
	for sp in spots:
		place(float(sp[1]), float(sp[2]), float(sp[3]))
		m.snap_height()
		m.cam_len = 4.5
		await get_tree().create_timer(2.5).timeout
		var cp := get_viewport().get_camera_3d().global_position
		printerr("STATIONCAM %s: arm %.2f of %.2f cam (%.1f, %.1f, %.1f) her y %.2f%s" % [sp[0], m.arm.get_hit_length(), m.arm.spring_length,
			cp.x, cp.y, cp.z, m.model.position.y, cam_inside()])
		await shot(dir, String(sp[0]))
	end_test()


func run_funitilt() -> void:
	# (round 41, the user: "as I go up the hill, when I move up or down, it keeps resetting") riding up, in each view:
	# tip the view with ↑ / ↓, then watch where it goes over the next 3 s
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var d: Array = m.D.north.cable.door_low
	place(d[0], d[1] + 1.0, PI)
	await get_tree().create_timer(0.5).timeout
	m.north.start_cable(true)
	await get_tree().create_timer(24.0).timeout                # (past the middle: both views tried before it arrives)
	for mode in ["outside", "inside"]:
		if mode == "inside":
			m.north.ride_toggle()
			await get_tree().create_timer(2.5).timeout           # (after the toggle's fade)
		for k in [KEY_UP, KEY_DOWN]:
			await hold(k, 0.4)
			var line := ""
			for i in 12:
				line += " %.2f" % m.cam_pitch_node.rotation.x
				await get_tree().create_timer(0.25).timeout
			printerr("FUNITILT %s after %s: pitch%s  (arm x %.2f)" % [mode, "UP" if k == KEY_UP else "DOWN", line, m.arm.rotation.x])
	end_test()


func run_titleshots(dir: String) -> void:
	# (round 41) the title screen as the player sees it — the live view over Park Güell, the title and its choices — at
	# several times of day
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.game.fresh = false
	m.game.S["new"] = false
	m.title_screen()
	var only := "--titleonce" in OS.get_cmdline_user_args()
	for tm in ([[400, "1_sunrise"]] if only else [[400, "1_sunrise"], [600, "2_morning"], [900, "3_afternoon"], [1275, "4_sunset"], [1350, "5_night"]]):
		m.set_clock(float(tm[0]))
		await get_tree().create_timer(2.5).timeout
		await shot(dir, tm[1])
	end_test()


func run_titlesound() -> void:
	# (round 41, rule 08 #82d) the title: the music and a far-off hum, no sea, no place name; after Continue her own
	# place's sounds fade in — saved in the city, then saved on the beach. First: nothing plays while it loads.
	var a = m.ambience
	printerr("TITLESOUND loading: street %s hum %s sea %s music %s" % [a.street.playing, a.street_in.playing, a.sea.playing,
		a.music_out.playing])
	var t0 := Time.get_ticks_msec()
	for i in 8:
		await get_tree().create_timer(0.1).timeout
		printerr("TITLESOUND opening t=%.2f: whole volume %.0f, street %.0f music %.0f" % [(Time.get_ticks_msec() - t0) / 1000.0,
			AudioServer.get_bus_volume_db(0), a.street.volume_db, a.music_out.volume_db])
	await get_tree().create_timer(4.5).timeout
	var beach := m.player.global_position
	for case in [["city", Vector3(-97.8, 0, -109.5)], ["beach", beach]]:
		m.game.fresh = false
		m.game.S["new"] = false
		m.game.S["at"] = {"x": case[1].x, "z": case[1].z, "yaw": 0.0}
		m.teleport(beach, 0.0)                         # (behind the title she stands on the beach, as at start)
		await get_tree().create_timer(1.0).timeout
		m.title_screen()
		for i in 4:
			await get_tree().create_timer(0.5).timeout
			printerr("TITLESOUND %s title t=%.1f street %.0f hum %.0f sea %.0f music %.0f name %s" % [case[0], i * 0.5,
				a.street.volume_db, a.street_in.volume_db, a.sea.volume_db, a.music_out.volume_db,
				("'" + m.banner.text + "'") if m.banner_panel.modulate.a > 0.05 and m.banner_timer > 0.0 else "none"])
		m.dlg_choice = 0
		m.dialog_next()                                # Continue
		for i in 10:
			await get_tree().create_timer(0.4).timeout
			printerr("TITLESOUND %s play t=%.1f street %.0f hum %.0f sea %.0f music %.0f name %s" % [case[0], i * 0.4,
				a.street.volume_db, a.street_in.volume_db, a.sea.volume_db, a.music_out.volume_db,
				("'" + m.banner.text + "'") if m.banner_panel.modulate.a > 0.05 and m.banner_timer > 0.0 else "none"])
	end_test()


func run_framerec(spec: String) -> void:
	# (round 41, the user: "The loading screen now has buildings flickering… check the flickering from one frame to the
	# next on the railings of the buildings… her shadow when she's stationary and cycling") every frame kept, as the
	# player sees it (the panels hidden), then saved as PNGs for comparing frame with frame.
	# --framerec=<dir>,<mode>,<secs>[,…]: title (from the very first frame, as the game opens), titlelate (after 12 s),
	# stand,x,z,heading · bike,x0,z0,x1,z1 (riding from a to b) · bikestill,x,z,heading (sat on the bike, stopped)
	var v := spec.split(",")
	var dir := v[0]
	var mode := v[1]
	var secs := float(v[2])
	DirAccess.make_dir_recursive_absolute(dir)
	m.set_clock(660.0)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--clock="):
			m.set_clock(float(a.trim_prefix("--clock=")))
	if mode == "vfshot" or mode == "vfturn" or mode == "vfwalk" or mode == "vfclean":     # (the viewfinder at the top of La Rambla: a photo taken, or turning right)
		await get_tree().create_timer(3.0).timeout
		place(-46.0, -30.0, PI)
		m.snap_height()
		await get_tree().create_timer(1.5).timeout
		m.viewfinder(true)
		await get_tree().create_timer(1.5).timeout
	elif mode == "wheel":                          # (on the Ferris wheel, once it is going round: v[3] how far round)
		await get_tree().create_timer(3.0).timeout
		m.game.S.money = maxi(int(m.game.S.money), 1000)
		var W: Dictionary = m.D.north.wheel
		place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
		await get_tree().create_timer(1.0).timeout
		m.north.act("wheel")
		await talk_through([0])
		var far_round := float(v[3]) if v.size() > 3 else 0.3
		var tw := Time.get_ticks_msec()
		while Time.get_ticks_msec() - tw < 90000 and not m.north.ride.is_empty() and not (String(m.north.ride.get("phase", "")) == "round"
				and float(m.north.ride.get("turned", 0.0)) >= TAU * far_round):
			await get_tree().process_frame
	elif mode.begins_with("title"):
		m.game.fresh = false
		m.game.S["new"] = false
		m.title_screen()
		if mode == "titlelate":
			await get_tree().create_timer(12.0).timeout
	else:
		await get_tree().create_timer(3.0).timeout
		m.game.S["has_bike"] = true
		var a := Vector2(float(v[3]), float(v[4]))
		var hd := float(v[5]) if mode != "bike" else 0.0
		if mode == "bike":
			var b := Vector2(float(v[5]), float(v[6]))
			hd = atan2((b - a).x, (b - a).y)
		place(a.x, a.y, hd)
		await get_tree().create_timer(0.6).timeout
		if mode.begins_with("bike"):
			m.bike_key()
			await get_tree().create_timer(0.4).timeout
		if mode == "bike":
			m.vkeys[KEY_W] = true
		await get_tree().create_timer(2.5).timeout
	# (tests of the forest flicker on the wheel: --flutter=<amp> the leaves' sway; --nofade=<prefix,…> those objects switch
	# at their distance without the cross-fade)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--flutter="):
			for key in m.foliage_mats:
				(m.foliage_mats[key] as ShaderMaterial).set_shader_parameter("flutter_amp", float(a.trim_prefix("--flutter=")))
		if a == "--nosun":
			m.sun.shadow_enabled = false
		if a == "--noleafshadow":
			for n in m.outdoor.find_children("Leaves_*", "GeometryInstance3D", true, false):
				(n as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if a.begins_with("--hide="):
			for pre in a.trim_prefix("--hide=").split(","):
				for n in m.outdoor.find_children(pre + "*", "GeometryInstance3D", true, false):
					(n as GeometryInstance3D).visible = false
		if a.begins_with("--nofade="):
			for pre in a.trim_prefix("--nofade=").split(","):
				for n in m.outdoor.find_children(pre + "*", "GeometryInstance3D", true, false):
					(n as GeometryInstance3D).visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	if mode == "vfclean":                       # (a mock-up: the viewfinder without the mission, street, clock and money boxes)
		m.hud_root.visible = false
		m.banner_panel.visible = false
		await get_tree().create_timer(0.5).timeout
	if not mode.begins_with("vf"):              # (the viewfinder's own pictures keep what is on screen)
		for c in m.get_children():
			if c is CanvasLayer:
				c.visible = false
	var frames := []
	var info := []
	var t0 := Time.get_ticks_msec()
	var small := "--recsmall" in OS.get_cmdline_user_args()      # (long recordings: each frame kept at 320 × 200)
	var fi := 0
	while Time.get_ticks_msec() - t0 < secs * 1000.0:
		await get_tree().process_frame
		fi += 1
		if mode == "vfshot" and (fi == 8 or fi == 30):
			m.take_photo()
		if mode == "vfturn":
			if fi == 5:
				m.vkeys[KEY_RIGHT] = true
			if fi == 40:
				m.vkeys.erase(KEY_RIGHT)
		if mode == "vfwalk":                       # (W for a second, then D, then the right arrow while walking on)
			if fi == 5:
				m.vkeys[KEY_W] = true
			if fi == 35:
				m.vkeys.erase(KEY_W)
				m.vkeys[KEY_D] = true
			if fi == 55:
				m.vkeys.erase(KEY_D)
				m.vkeys[KEY_W] = true
				m.vkeys[KEY_RIGHT] = true
			if fi == 80:
				m.vkeys.erase(KEY_W)
				m.vkeys.erase(KEY_RIGHT)
		var fimg := get_viewport().get_texture().get_image()
		if small:
			fimg.resize(320, 200, Image.INTERPOLATE_BILINEAR)
		frames.append(fimg)
		var cp := get_viewport().get_camera_3d().get_global_transform_interpolated().origin
		var pp := m.player.global_position
		info.append("%d %.3f %.3f %.3f %.3f %.2f %.4f %.3f %.3f %s" % [Time.get_ticks_msec() - t0, get_viewport().scaling_3d_scale, cp.x, cp.y,
			cp.z, m.game.S.time, m.vf_yaw, pp.x, pp.z, m.prompt.text.replace(" ", "_")])
	m.vkeys.erase(KEY_W)
	for i in frames.size():
		(frames[i] as Image).save_png(dir.path_join("f%03d.png" % i))
	var f := FileAccess.open(dir.path_join("frames.txt"), FileAccess.WRITE)
	f.store_string("\n".join(info))
	f.close()
	printerr("FRAMEREC %s: %d frames in %.1f s" % [mode, frames.size(), secs])
	end_test()


func run_perfopts() -> void:
	# (round 41, the user: "review the frame rate… see what you could do to make it run faster? Give me options") at
	# each place, the graphics chip's and the processor's time for a frame (ms, averaged over 40 frames), first as
	# the game is, then with one thing at a time turned down. Lower is faster; 50 ms = 20 fps, 33 ms = 30 fps.
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	var vp := get_viewport()
	RenderingServer.viewport_set_measure_render_time(vp.get_viewport_rid(), true)
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var spots := [["home street", Vector2(3.3, 37.6), PI * 0.5], ["la rambla", Vector2(-56.0, 60.0), PI],
		["park guell", Vector2(107.1, -192.0), PI], ["east wood", Vector2(164.0, 12.0), PI / 2.0],
		["hill path", Vector2(-133.6, -223.0), 0.3], ["title view", Vector2.ZERO, 0.0]]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--spot="):
			spots = spots.filter(func(q): return q[0].replace(" ", "_") == a.trim_prefix("--spot="))
	var measure := func() -> Array:
		for k in 30:                               # (let any new shader versions compile first)
			await get_tree().process_frame
		var t0 := Time.get_ticks_usec()
		for k in 60:
			await get_tree().process_frame
		var ms := (Time.get_ticks_usec() - t0) / 60000.0
		var c := RenderingServer.viewport_get_measured_render_time_cpu(vp.get_viewport_rid()) + RenderingServer.get_frame_setup_time_cpu()
		return [ms, c, 0.0]
	var leaves := m.outdoor.find_children("Leaves_*", "GeometryInstance3D", true, false).filter(
		func(n): return n.cast_shadow != GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
	var ranged := m.outdoor.find_children("*", "GeometryInstance3D", true, false).filter(func(n): return n.visibility_range_end > 0.0)
	var opts := [
		["as it is", func(): pass, func(): pass],
		["render 75%", func(): vp.scaling_3d_scale = 0.75, func(): vp.scaling_3d_scale = 1.0],
		["render 55%", func(): vp.scaling_3d_scale = 0.55, func(): vp.scaling_3d_scale = 1.0],
		["soft shade (SSAO) back on", func(): m.env_out.ssao_enabled = true, func(): m.env_out.ssao_enabled = false],
		["no glow", func(): m.env_out.glow_enabled = false, func(): m.env_out.glow_enabled = true],
		["no sun shadows", func(): m.sun.shadow_enabled = false, func(): m.sun.shadow_enabled = true],
		["shadows to 50 m", func(): m.sun.directional_shadow_max_distance = 50.0, func(): m.sun.directional_shadow_max_distance = 85.0],
		["shadow map half size", func(): RenderingServer.directional_shadow_atlas_set_size(2048, true),
			func(): RenderingServer.directional_shadow_atlas_set_size(4096, true)],
		["hard shadow edges", func(): RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_HARD),
			func(): RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_SOFT_MEDIUM)],
		["no leaf shadows", func(): perf_shadows(leaves, false), func(): perf_shadows(leaves, true)],
		["details drawn 30% nearer", func(): perf_ranges(ranged, 0.7), func(): perf_ranges(ranged, 1.0 / 0.7)],
		["old upscaler (FSR 1) at 75%", func(): perf_fsr1(true), func(): perf_fsr1(false)],
	]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--perfonly="):                 # (only the options named, by number: 0 = as it is)
			var keep := Array(a.trim_prefix("--perfonly=").split(",")).map(func(q): return int(q))
			opts = range(opts.size()).filter(func(i): return i in keep).map(func(i): return opts[i])
	for v in spots:
		if v[0] == "title view":
			m.title_view(true)
		else:
			place(v[1].x, v[1].y, v[2])
			m.cam_yaw_node.rotation.y = v[2] + PI
			m.last_manual_cam = m.t
		await get_tree().create_timer(2.5).timeout
		var tri := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)
		var dc := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)
		printerr("PERFOPT == %s: %dk triangles, %d draw calls" % [v[0], tri / 1000, dc])
		for o in opts:
			o[1].call()
			var r: Array = await measure.call()
			o[2].call()
			printerr("PERFOPT %-12s %-30s %5.1f ms a frame (%4.1f fps)   drawing setup %4.1f ms" % [v[0], o[0], r[0], 1000.0 / r[0], r[1]])
		if v[0] == "title view":
			m.title_view(false)
	end_test()


func run_lookopts(dir: String) -> void:
	# (round 41, the user: "give me pictures of before and after of 1, 2, and 3. All against the current as a
	# baseline") the game's own view, the world held still (people, leaves), as it is and with each speed option:
	# 1 hiding what is behind the blocks (on in the game since: the baseline turns it off), 2 soft shading (SSAO, off in
	# the game since), 3 a half-size shadow map
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	var vp := get_viewport()
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	var spots := [["la_rambla", Vector2(-56.0, 60.0), PI, -0.2], ["east_wood", Vector2(164.0, 12.0), PI / 2.0, -0.25],
		["park_guell", Vector2(107.1, -192.0), PI, -0.2]]
	for v in spots:
		Engine.time_scale = 1.0
		place(v[1].x, v[1].y, v[2])
		m.cam_yaw_node.rotation.y = v[2] + PI
		m.cam_pitch_node.rotation.x = v[3]
		m.last_manual_cam = m.t
		await get_tree().create_timer(2.5).timeout
		Engine.time_scale = 0.002                # (all but held still, so only the option differs between the pictures; 0 breaks the camera)
		var opts := [["0_as_it_is", func(): vp.use_occlusion_culling = false, func(): pass],
			["1_hiding", func(): vp.use_occlusion_culling = true, func(): vp.use_occlusion_culling = false],
			["2_soft_shade_back_on", func(): m.env_out.ssao_enabled = true, func(): m.env_out.ssao_enabled = false],
			["3_half_shadow_map", func(): RenderingServer.directional_shadow_atlas_set_size(2048, true),
				func(): RenderingServer.directional_shadow_atlas_set_size(4096, true)]]
		for o in opts:
			o[1].call()
			for k in 45:
				await get_tree().process_frame
			vp.get_texture().get_image().save_png(dir.path_join("%s_%s.png" % [v[0], o[0]]))
			o[2].call()
	Engine.time_scale = 1.0
	end_test()


func run_wheelfps(png: String) -> void:
	# (round 41c, the user tried the woods' far trees from 50 m instead of 100 m on the wheel: 38 → 40 fps, no change
	# to see; put back to 100 m at their word) once round the wheel at noon: the frame rate for the first 18 s, a picture near the top, then the rest of the ride
	await get_tree().create_timer(3.0).timeout
	m.set_clock(720.0)
	m.game.S.money = maxi(int(m.game.S.money), 1000)
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.act("wheel")
	await talk_through([0])
	await get_tree().create_timer(2.0).timeout
	await fps_window("wheel, rising", 18.0, func(): return m.north.ride.is_empty())
	get_viewport().get_texture().get_image().save_png(png)
	await fps_window("wheel, over the top and down", 30.0, func(): return m.north.ride.is_empty())
	end_test()


func fps_window(label: String, secs: float, until := Callable()) -> void:
	# the frame rate over a stretch of play: the average, and the slowest frames (the worst 1 in 20)
	var times := []
	var t0 := Time.get_ticks_usec()
	var last := t0
	while (Time.get_ticks_usec() - t0) / 1000000.0 < secs:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		times.append((now - last) / 1000.0)
		last = now
		if until.is_valid() and until.call():
			break
	if times.size() > 3:
		times = times.slice(2)                      # (the first frames after a change can stutter once)
	var total := 0.0
	for x in times:
		total += x
	var sorted := times.duplicate()
	sorted.sort()
	var slow: float = sorted[int(sorted.size() * 0.95)]
	printerr("FPSTOUR %-34s %5.1f fps on average, slowest frames %5.1f fps  (%d frames, %.0f s)" % [label,
		times.size() / (total / 1000.0), 1000.0 / slow, times.size(), total / 1000.0])


func ride_opts() -> Array:
	# (round 41) ride-only ways to a better frame rate: each [name, on, off]
	var vp := get_viewport()
	var near_trees := m.outdoor.find_children("Leaves_forest_*", "GeometryInstance3D", true, false) + m.outdoor.find_children("ForestTrunks_*", "GeometryInstance3D", true, false)
	var far_trees := m.outdoor.find_children("Leaves_far_*", "GeometryInstance3D", true, false) + m.outdoor.find_children("ForestFar_*", "GeometryInstance3D", true, false)
	var small := []
	for pre in ["Detail_", "Plants_", "PlanterLeaves_", "Planter_", "Grass_", "Wares_", "Bins_", "BikeStand_", "KitText_", "SignText_", "Rail_", "RailCard_", "StreetBench_", "ParkBench_"]:
		small += m.outdoor.find_children(pre + "*", "GeometryInstance3D", true, false)
	var leaves := m.outdoor.find_children("Leaves_*", "GeometryInstance3D", true, false).filter(
		func(n): return n.cast_shadow != GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
	return [
		["as it is", func(): pass, func(): pass],
		["picture quality 75%", func(): vp.scaling_3d_scale = 0.75, func(): vp.scaling_3d_scale = 1.0],
		["trees swap to far at 60 m", func(): perf_swap(near_trees, far_trees, 60.0), func(): perf_swap(near_trees, far_trees, 105.0)],
		["small details half as far", func(): perf_ranges(small, 0.5), func(): perf_ranges(small, 2.0)],
		["shadows to 40 m", func(): m.sun.directional_shadow_max_distance = 40.0, func(): m.sun.directional_shadow_max_distance = 85.0],
		["no leaf shadows", func(): perf_shadows(leaves, false), func(): perf_shadows(leaves, true)],
		["as it is (again)", func(): pass, func(): pass],
	]


func perf_swap(near: Array, far: Array, d: float) -> void:
	for n in near:
		(n as GeometryInstance3D).visibility_range_end = d
	for n in far:
		(n as GeometryInstance3D).visibility_range_begin = d - 10.0


func run_ridelook(dir: String) -> void:
	# (round 41, the user: "Could you do a before and after with them? On the funicular… And the… Ferris wheel") the
	# ride all but held still, as it is and with each ride-only option, from the same spot
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(709.0)
	m.game.S.money = maxi(int(m.game.S.money), 1000)
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var opts := ride_opts()
	opts.pop_back()
	var shoot := func(ride: String) -> void:
		Engine.time_scale = 0.002
		for k in opts.size():
			opts[k][1].call()
			for f in 50:
				await get_tree().process_frame
			get_viewport().get_texture().get_image().save_png(dir.path_join("%s_%d_%s.png" % [ride, k, String(opts[k][0]).replace(" ", "_").replace("%", "")]))
			opts[k][2].call()
		Engine.time_scale = 1.0
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.act("wheel")
	await talk_through([0])
	var tw := Time.get_ticks_msec()
	while Time.get_ticks_msec() - tw < 90000 and not (String(m.north.ride.get("phase", "")) == "round" and float(m.north.ride.get("turned", 0.0)) >= TAU * 0.2):
		await get_tree().process_frame
	await shoot.call("wheel")
	while not m.north.ride.is_empty():
		await get_tree().create_timer(0.5).timeout
	var d: Array = m.D.north.cable.door_low
	place(d[0], d[1] + 1.0, PI)
	await get_tree().create_timer(0.8).timeout
	m.north.start_cable(true)
	await get_tree().create_timer(16.0).timeout
	await shoot.call("funicular")
	end_test()


func run_idleline(spec: String) -> void:
	# (round 41, rule 10 #34a) the top-left line with nothing on ("Explore Barcelona — …"), as the player sees it: this
	# save has every open mission done, so its idle line (the study one) is swapped for the explore one in memory
	# (--idleline=<png>[,study]: the study line as it is, rather than the explore one)
	var png := spec.split(",")[0]
	await get_tree().create_timer(3.0).timeout
	if spec.ends_with(",study"):
		m.game.data.IDLE_LINES.explore = m.game.data.IDLE_LINES.study
	else:
		m.game.data.IDLE_LINES.study = m.game.data.IDLE_LINES.explore
	m.game.S.missions = {}                                # (the test save only: nothing on, so the idle line shows)
	if spec.ends_with(",steps"):
		# (round 41c, rule 10 #34) every mission step in the box, each on one line? then the picture with the dog's on
		var wrapped := 0
		for k in m.game.data.MISSIONS:
			for st in m.game.data.MISSIONS[k].obj:
				var t: String = m.game.data.MISSIONS[k].obj[st] + (" (5/5)" if st == "flowers" else "")
				m.hud.text = t
				m.layout_ui()
				await get_tree().process_frame
				if m.hud.get_line_count() > 1:
					wrapped += 1
					printerr("  WRAPS: ", t)
		printerr("STEPS: %d wrap onto a second line" % wrapped)
		m.game.S.missions = {"dog": {"st": "active", "num": 3}}
		m.game.S.focus = "dog"
	place(-56.0, 60.0, PI)
	await get_tree().create_timer(1.5).timeout
	printerr("IDLELINE '%s', %d line(s)" % [m.hud.text, m.hud.get_line_count()])
	get_viewport().get_texture().get_image().save_png(png)
	end_test()


func run_bagitem(spec: String) -> void:
	# --bagitem=<id>,<png>: the backpack open with that thing picked, as the player sees it (its name and description)
	# (a third value "bike": on the bike first, and Enter pressed on it — the camera's answer there)
	var v := spec.split(",")
	await get_tree().create_timer(3.0).timeout
	if not m.game.has_item(v[0]):
		m.game.add_item(v[0])
	if v.size() > 2 and v[2] == "bike":
		m.game.S["has_bike"] = true
		place(-56.0, 60.0, PI)
		await get_tree().create_timer(0.5).timeout
		m.bike_key()
		await get_tree().create_timer(3.5).timeout       # (riding a while: the "On the bike!" note has gone)
	await get_tree().process_frame
	m.input_key(KEY_I)
	await get_tree().create_timer(0.5).timeout
	var at := -1
	for i in m.game.S.inv.size():
		if String(m.game.S.inv[i].id) == v[0]:
			at = i
			break
	for k in at:
		m.input_key(KEY_RIGHT)
	await get_tree().create_timer(0.5).timeout
	if v.size() > 2 and (v[2] == "bike" or v[2] == "use"):
		m.input_key(KEY_ENTER)
		for fr in 8:
			await get_tree().process_frame
			printerr("BAGITEM frame %d: note '%s' shown %.2f, time left %.2f, paused %s, panel open %s" % [fr, m.toast_label.text,
				m.toast_label.modulate.a, m.toast_t, get_tree().paused, m.panels.is_open()])
		await get_tree().create_timer(0.4 if m.toasts.is_empty() else 2.8).timeout
		printerr("BAGITEM " + v[2] + ", Enter: question open %s, viewfinder %s, toasts %s, says '%s' (shown %.2f, visible %s, at %s)" % [m.dlg_open, m.vf_on,
			m.toasts, m.toast_label.text, m.toast_label.modulate.a, m.toast_label.is_visible_in_tree(), m.toast_label.global_position])
	get_viewport().get_texture().get_image().save_png(v[1])
	printerr("BAGITEM %s at slot %d" % [v[0], at])
	end_test()


func run_titleload(dir: String) -> void:
	# (round 41, rule 08 #82) the title's Continue · Load game · New game: pictures of the title, the list of saved
	# copies, Back to the title, a copy's question; then Yes, and after the game restarts, where it put her
	DirAccess.make_dir_recursive_absolute(dir)
	if Engine.has_meta("load_continue"):
		await get_tree().create_timer(2.0).timeout
		m.title_screen()
		await get_tree().create_timer(1.5).timeout
		var p := m.player.global_position
		printerr("TITLELOAD loaded: at (%.1f, %.1f) in %s, money %s, title shown %s" % [p.x, p.z, m.where, m.game.money(m.game.S.money), m.title_cam != null])
		await shot(dir, "5_after_loading")
		end_test()
		return
	await get_tree().create_timer(3.0).timeout
	m.game.fresh = false
	m.game.S["new"] = false
	m.title_screen()
	await get_tree().create_timer(1.2).timeout
	printerr("TITLELOAD title: ", m.dlg_text.text.left(60))
	await shot(dir, "1_title")
	m.dlg_choice = 1                                      # Load game
	m.dialog_next()
	await get_tree().create_timer(0.8).timeout
	printerr("TITLELOAD list: ", m.dlg_text.text.left(60))
	await shot(dir, "2_load_list")
	m.dlg_choice = m.choice_box.get_child_count() - 1     # Back, the last
	m.dialog_next()
	await get_tree().create_timer(0.8).timeout
	printerr("TITLELOAD back: ", m.dlg_text.text.left(60))
	await shot(dir, "3_back_to_title")
	m.dlg_choice = 1
	m.dialog_next()
	await get_tree().create_timer(0.8).timeout
	m.dlg_choice = 0                                      # the newest copy
	m.dialog_next()
	await get_tree().create_timer(0.8).timeout
	printerr("TITLELOAD ask: ", m.dlg_text.text.left(80))
	await shot(dir, "4_are_you_sure")
	m.dlg_choice = 0                                      # Yes, load it (the game restarts and this test with it)
	m.dialog_next()


func run_rideperf() -> void:
	# (round 41, the user: "the Ferris wheel, the funicular up and the funicular down… suggest something we could do") on
	# each ride, the frame rate with each ride-only option for 2.5 s in turn (the ride moves on meanwhile, so "as it is"
	# is measured first and last)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.money = maxi(int(m.game.S.money), 1000)
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var opts := ride_opts()
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.act("wheel")
	await talk_through([0])
	var tw := Time.get_ticks_msec()
	while Time.get_ticks_msec() - tw < 60000 and String(m.north.ride.get("phase", "")) != "round":
		await get_tree().process_frame
	for o in opts:
		o[1].call()
		await get_tree().create_timer(0.6).timeout
		await fps_window("wheel: " + o[0], 2.5)
		o[2].call()
	while not m.north.ride.is_empty():
		await get_tree().create_timer(0.5).timeout
	for leg in ["up", "down"]:
		var d: Array = m.D.north.cable.door_low if leg == "up" else m.D.north.cable.door_top
		place(d[0], d[1] + (1.0 if leg == "up" else -1.0), PI if leg == "up" else 0.0)
		await get_tree().create_timer(0.8).timeout
		m.north.start_cable(leg == "up")
		await get_tree().create_timer(4.0).timeout
		for o in opts:
			o[1].call()
			await get_tree().create_timer(0.6).timeout
			await fps_window("funicular %s: %s" % [leg, o[0]], 2.5)
			o[2].call()
		while not m.north.ride.is_empty():
			await get_tree().create_timer(0.5).timeout
		await get_tree().create_timer(1.0).timeout
	end_test()


func run_fpstour() -> void:
	# (round 41, the user: "what is the frame rate in different places, also doing different activities, cycling
	# through the forest, up on the ferris wheel, funicular") the game as played (its own camera, the panels shown),
	# at full picture quality in the test window: walking, cycling, the rides, a room, the title view
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S["has_bike"] = true
	m.game.S.money = maxi(int(m.game.S.money), 1000)
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var walk := func(label: String, a: Vector2, b: Vector2, secs: float, bike: bool) -> void:
		place(a.x, a.y, atan2((b - a).x, (b - a).y))
		m.cam_yaw_node.rotation.y = atan2((b - a).x, (b - a).y) + PI
		await get_tree().create_timer(1.0).timeout
		if bike:
			m.bike_key()
			await get_tree().create_timer(0.5).timeout
		m.vkeys[KEY_W] = true
		await get_tree().create_timer(1.0).timeout
		await fps_window(label, secs)
		m.vkeys.erase(KEY_W)
		if bike and m.street.riding != null:
			m.bike_key()
		await get_tree().create_timer(0.5).timeout
	await walk.call("walking: her street", Vector2(-30.0, 36.5), Vector2(60.0, 36.5), 6.0, false)
	await walk.call("walking: La Rambla", Vector2(-56.0, 100.0), Vector2(-56.0, -80.0), 6.0, false)
	await walk.call("cycling: Carrer de Mallorca", Vector2(-140.0, -6.5), Vector2(70.0, -6.5), 6.0, true)
	await walk.call("cycling: La Rambla", Vector2(-56.0, 110.0), Vector2(-56.0, -90.0), 6.0, true)
	await walk.call("cycling: through the eastern wood", Vector2(134.3, -82.0), Vector2(134.6, -40.0), 6.0, true)
	await walk.call("walking: the beach", Vector2(-100.0, 175.0), Vector2(100.0, 175.0), 6.0, false)
	await walk.call("walking: up the hill path", Vector2(-133.6, -223.0), Vector2(-120.0, -260.0), 6.0, false)
	await walk.call("walking: Park Güell", Vector2(107.1, -185.0), Vector2(107.1, -205.0), 5.0, false)
	# (round 41c, 02 #128b) the ball's glade, and the wood west of the funfair made whole
	await walk.call("walking: the ball's glade", Vector2(-188.0, -258.0), Vector2(-150.0, -258.0), 5.0, false)
	await walk.call("walking: the wood west of the funfair", Vector2(-112.0, -302.0), Vector2(-190.0, -316.0), 6.0, false)
	await walk.call("walking: below the top lookout", Vector2(-146.0, -262.0), Vector2(-104.0, -256.0), 6.0, false)
	# a room
	m.show_room("int_berlin", false)
	await get_tree().create_timer(1.5).timeout
	await fps_window("in a room: the Cafè Berlín", 4.0)
	m.teleport(Vector3(-56.0, 0.0, 60.0), 0.0)
	await get_tree().create_timer(1.5).timeout
	# the Ferris wheel, once round
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.act("wheel")
	await talk_through([0])
	await get_tree().create_timer(2.0).timeout
	await fps_window("riding the Ferris wheel", 40.0, func(): return m.north.ride.is_empty())
	await get_tree().create_timer(3.0).timeout
	# the funicular, up then down
	for leg in ["up", "down"]:
		var d: Array = m.D.north.cable.door_low if leg == "up" else m.D.north.cable.door_top
		place(d[0], d[1] + (1.0 if leg == "up" else -1.0), PI if leg == "up" else 0.0)
		await get_tree().create_timer(0.8).timeout
		m.north.start_cable(leg == "up")
		await get_tree().create_timer(1.0).timeout
		await fps_window("riding the funicular " + leg, 60.0, func(): return m.north.ride.is_empty())
		await get_tree().create_timer(2.0).timeout
	# the title view
	for c in m.get_children():
		if c is CanvasLayer:
			c.visible = false
	m.title_view(true)
	await get_tree().create_timer(1.5).timeout
	await fps_window("the title view", 5.0)
	m.title_view(false)
	end_test()


func perf_shadows(ns: Array, on: bool) -> void:
	for n in ns:
		(n as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if on else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


func perf_ranges(ns: Array, k: float) -> void:
	for n in ns:
		(n as GeometryInstance3D).visibility_range_end *= k


func perf_fsr1(on: bool) -> void:
	var vp := get_viewport()
	vp.scaling_3d_mode = Viewport.SCALING_3D_MODE_FSR if on else m.scale_mode
	vp.use_taa = on
	vp.scaling_3d_scale = 0.75 if on else 1.0


func run_funijolt() -> void:
	# (round 41, the user: "when I am going up and I look slightly to the ground, there's some jump… then I'm looking
	# back at the ceiling again… just at the start when I'm going down the hill and up the hill") each way, at her seat
	# and outside: at the start, ↓ held a moment, then the tilt every tenth of a second for 4 s
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	for leg in ["up", "down"]:
		for inside in [true, false]:
			var d: Array = m.D.north.cable.door_low if leg == "up" else m.D.north.cable.door_top
			place(d[0], d[1] + (1.0 if leg == "up" else -1.0), PI if leg == "up" else 0.0)
			await get_tree().create_timer(0.5).timeout
			m.north.start_cable(leg == "up")
			while m.north.ride.is_empty():
				await get_tree().process_frame
			if inside:
				m.north.ride_toggle()
			await get_tree().create_timer(0.2).timeout
			await hold(KEY_DOWN, 0.35)
			var line := ""
			for i in 40:
				var cpz := get_viewport().get_camera_3d().global_position
				line += " %.2f/%.2f/%.2f" % [m.cam_pitch_node.rotation.x, m.arm.get_hit_length(), cpz.y]
				await get_tree().create_timer(0.1).timeout
			printerr("FUNIJOLT %s %s: %s" % [leg, "inside" if inside else "outside", line])
			while not m.north.ride.is_empty():
				await get_tree().process_frame
			await get_tree().create_timer(1.0).timeout
	end_test()


func run_funiside() -> void:
	# (round 41, the user: "when I was coming down… I spun the camera around, so I was looking at the city just sideways…
	# then I went down to look more at the ground, and then I got pulled back… looking back at the sky. It does it quite
	# consistently") outside the car, coming down: sideways, ↓ held, then the tilt, the arm's tip and the camera's height
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var d: Array = m.D.north.cable.door_top
	place(d[0], d[1] - 1.0, 0.0)
	await get_tree().create_timer(0.5).timeout
	m.north.start_cable(false)
	await get_tree().create_timer(6.0).timeout
	for side in [PI / 2.0, -PI / 2.0]:
		m.cam_yaw_node.rotation.y = side
		m.last_manual_cam = m.t
		for k in [KEY_DOWN, KEY_UP]:
			await hold(k, 0.8)
			var line := ""
			for i in 30:
				var cp := get_viewport().get_camera_3d().global_position
				line += " %.2f|%.2f|%.1f" % [m.cam_pitch_node.rotation.x, m.arm.rotation.x, cp.y - m.player.global_position.y]
				await get_tree().create_timer(0.1).timeout
			printerr("FUNISIDE yaw %.2f after %s: pitch|armtip|camHeight %s" % [side, "DOWN" if k == KEY_DOWN else "UP", line])
	end_test()


func run_funiwatch(arg: String) -> void:
	# --funiwatch=down|up[,inside]: the whole ride, the view turned sideways towards the city and tipped down at the
	# start; every frame, any change of tilt, turn or arm the player didn't make is printed
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var down := arg.begins_with("down")
	var d: Array = m.D.north.cable.door_top if down else m.D.north.cable.door_low
	place(d[0], d[1] + (-1.0 if down else 1.0), 0.0 if down else PI)
	await get_tree().create_timer(0.5).timeout
	m.north.start_cable(not down)
	while m.north.ride.is_empty():
		await get_tree().process_frame
	if arg.ends_with("inside"):
		m.north.ride_toggle()
	# (the user: "as soon as it starts, swing around so the camera is facing downhill… all the way around 180 degrees,
	# and then immediately look to the ground… both of those movements immediately") as the screen clears: ← held for a
	# half turn, then ↓ straight away
	while m.fade.color.a > 0.3:
		await get_tree().process_frame
	await hold(KEY_LEFT, PI / 1.6)
	await hold(KEY_UP if arg.find("up2") >= 0 else KEY_DOWN, 0.2)      # (then: "I only went slightly")
	var p0: float = m.cam_pitch_node.rotation.x
	var y0: float = m.cam_yaw_node.rotation.y
	var a0: float = m.arm.rotation.x
	var h0: float = m.arm.get_hit_length()
	var n := 0
	while not m.north.ride.is_empty():
		await get_tree().process_frame
		var p1: float = m.cam_pitch_node.rotation.x
		var y1: float = m.cam_yaw_node.rotation.y
		var a1: float = m.arm.rotation.x
		var h1: float = m.arm.get_hit_length()
		if absf(p1 - p0) > 0.01 or absf(wrapf(y1 - y0, -PI, PI)) > 0.01 or absf(a1 - a0) > 0.03 or absf(h1 - h0) > 0.5:
			n += 1
			if n < 40:
				printerr("FUNIWATCH t=%.2f cable_t=%.3f pitch %.2f->%.2f yaw %.2f->%.2f armtip %.2f->%.2f arm %.2f->%.2f" % [
					float(m.north.ride.get("t", -1.0)), m.north.cable_t, p0, p1, y0, y1, a0, a1, h0, h1])
		p0 = p1
		y0 = y1
		a0 = a1
		h0 = h1
	printerr("FUNIWATCH done, %d changes" % n)
	end_test()


func run_funiground() -> void:
	# (round 41, the user: "with the funicular, could you make it so that the camera cannot move into the ground?") up
	# and down, following the car from outside, the camera tipped as low as it goes and taken round in a circle: every
	# frame the camera is under the ground (or the cutting's floor) is counted, with the worst
	await get_tree().create_timer(3.0).timeout
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	for leg in ["up", "down"]:
		var d: Array = m.D.north.cable.door_low if leg == "up" else m.D.north.cable.door_top
		place(d[0], d[1] + (1.0 if leg == "up" else -1.0), PI if leg == "up" else 0.0)
		await get_tree().create_timer(0.5).timeout
		m.north.start_cable(leg == "up")
		while m.north.ride.is_empty():
			await get_tree().process_frame
		var bad := 0
		var worst := 0.0
		var at := ""
		var n := 0
		while not m.north.ride.is_empty():
			m.cam_yaw_node.rotation.y += 0.02
			m.turn_camera(0.0, 0.05 if m.ride_look else -0.05)       # (pushed to the camera's lowest)
			await get_tree().process_frame
			n += 1
			var cp := get_viewport().get_camera_3d().global_position
			var th: float = m.terrain_at(cp.x, cp.z)
			var cf: float = m.north.cutting_floor(cp.x, cp.z)
			if not is_nan(cf):
				th = cf
			if cp.y < th + 0.05 and m.fade.color.a < 0.9:
				bad += 1
				if th - cp.y > worst:
					worst = th - cp.y
					at = "(%.1f, %.1f) cable_t %.2f pitch %.2f" % [cp.x, cp.z, m.north.cable_t, m.cam_pitch_node.rotation.x]
		printerr("FUNIGROUND %s: %d of %d frames under the ground, worst %.2f m at %s" % [leg, bad, n, worst, at])
		await get_tree().create_timer(1.0).timeout
	end_test()


func run_cryptprobe() -> void:
	# (round 41, the user: "I can go into the crypt while standing on the balcony above it") what E offers on the
	# terrace over the crypt's door, and down at the door itself
	await get_tree().create_timer(3.0).timeout
	for sp in [["terrace_above", -63.0, -300.6], ["terrace_edge", -63.0, -299.4], ["at_crypt_door", -63.0, -295.0]]:
		place(float(sp[1]), float(sp[2]), 0.0)
		m.snap_height()
		await get_tree().create_timer(0.6).timeout
		var n: Dictionary = m.nearest()
		printerr("CRYPTPROBE %s: her height %.2f, E offers %s" % [sp[0], m.model.position.y, n.get("label", "nothing")])
	end_test()


func run_vfplaces(dir: String) -> void:
	# (round 41, the user: "add the camera feature on the rides and indoors… on the bike… get off the bike first") the
	# viewfinder on the bike (refused, with a word), on the Ferris wheel near the top, and in the Cafè Berlín
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(720.0)
	# on the bike
	m.game.S["has_bike"] = true
	place(-46.0, -30.0, PI)
	m.snap_height()
	await get_tree().create_timer(0.5).timeout
	m.bike_key()
	await get_tree().create_timer(1.5).timeout
	m.viewfinder(true)
	await get_tree().create_timer(0.3).timeout
	printerr("VFPLACES bike: riding %s, viewfinder %s, toasts %s" % [m.street.riding != null, m.vf_on, m.toast_label.text])
	m.bike_key()
	await get_tree().create_timer(1.5).timeout
	# on the wheel
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.act("wheel")
	await talk_through([0])
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < 90000:
		var r: Dictionary = m.north.ride
		if String(r.get("phase", "")) == "round" and float(r.get("turned", 0.0)) >= TAU * 0.4:
			break
		await get_tree().process_frame
	m.viewfinder(true)
	await hold(KEY_LEFT, 0.5)
	await shot(dir, "1_wheel_viewfinder")
	await m.take_photo()
	printerr("VFPLACES wheel: viewfinder %s, eye %s, her seen %s" % [m.vf_on, m.vf_cam.global_position, m.model.visible])
	m.viewfinder(false)
	await get_tree().create_timer(1.0).timeout
	await shot(dir, "2_wheel_after")
	while not m.north.ride.is_empty() and Time.get_ticks_msec() - t0 < 150000:
		await get_tree().process_frame
	# in a room
	await go_in(entrance("int_berlin"))
	await get_tree().create_timer(1.5).timeout
	m.viewfinder(true)
	await shot(dir, "3_room_viewfinder")
	await m.take_photo()
	printerr("VFPLACES room: viewfinder %s, eye %s" % [m.vf_on, m.vf_cam.global_position])
	m.viewfinder(false)
	await get_tree().create_timer(1.0).timeout
	await shot(dir, "4_room_after")
	printerr("VFPLACES end: her seen %s, camera back %s" % [m.model.visible, get_viewport().get_camera_3d() != m.vf_cam])
	end_test()


func run_vftest(dir: String) -> void:
	# (round 41) the spare camera's viewfinder: at the top of La Rambla looking up to Tibidabo, as the player sees it,
	# zoomed, and the photo each way (saved to <dir>, not the Desktop: run with --photodir=<dir>)
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(720.0)
	place(-46.0, -30.0, PI)
	m.snap_height()
	await get_tree().create_timer(1.5).timeout
	m.viewfinder(true)
	await hold(KEY_LEFT, 0.12)
	await get_tree().create_timer(1.5).timeout
	await shot(dir, "1_viewfinder")
	await m.take_photo()
	await get_tree().create_timer(1.0).timeout
	m.vf_zoom = true
	await get_tree().create_timer(1.2).timeout
	await shot(dir, "2_viewfinder_zoomed")
	await m.take_photo()
	await get_tree().create_timer(1.0).timeout
	m.viewfinder(false)
	await get_tree().create_timer(1.5).timeout
	await shot(dir, "3_put_away")
	printerr("VFTEST toasts: %s; her model seen %s, vf %s" % [m.toasts, m.model.visible, m.vf_on])
	end_test()


func run_phototest() -> void:
	# (round 41) the spare camera's photograph: where it is saved, and what the game says
	await get_tree().create_timer(3.0).timeout
	for a in OS.get_cmdline_user_args():                # (the follow camera's view beside it, to compare)
		if a.begins_with("--photodir="):
			await RenderingServer.frame_post_draw
			m.get_viewport().get_texture().get_image().save_png(a.substr(11).path_join("follow_view.png"))
	await m.take_photo()
	printerr("PHOTOTEST toasts: %s" % [m.toasts])
	end_test()


func run_occlprobe(spec: String) -> void:
	# (round 41c, the user: "none of the scenery is there anymore… Is it something to do with the photo?") the follow view
	# at a spot, then the camera up, a photo, the camera down, and the follow view again, to compare
	# (--occlprobe=<dir>,x,z,heading)
	var v := spec.split(",")
	var dir := v[0]
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	place(float(v[1]), float(v[2]), float(v[3]))
	await shot(dir, "1_before")
	m.viewfinder(true)
	await get_tree().create_timer(1.0).timeout
	await m.take_photo()
	await get_tree().create_timer(1.0).timeout
	m.viewfinder(false)
	await shot(dir, "2_after_photo")
	place(float(v[1]), float(v[2]) + 0.01, float(v[3]))
	await shot(dir, "3_after_again")
	end_test()


func run_groundshot(spec: String) -> void:
	# (round 41c, the user: "I can't see the brush") a mission's thing lying in the world, as she walks up to it: its
	# mission started, Sandra 3 m off it looking at it (--groundshot=<dir>,<id>,<mission>)
	var v := spec.split(",")
	DirAccess.make_dir_recursive_absolute(v[0])
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.missions.erase(v[2])
	m.game.start_mission(v[2])
	for g in m.game.ground:
		if g.id == v[1]:
			m.game.S.taken.erase(g.key)
			m.game.refresh_ground()
			var p: Vector3 = g.node.global_position
			printerr("GROUND %s at (%.1f, %.1f) seen=%s" % [v[1], p.x, p.z, g.node.visible])
			place(p.x, p.z + 3.0, PI)
			await shot(v[0], v[1])
			place(p.x - 2.5, p.z + 0.5, PI / 2)                    # (and from above, close: a camera of its own)
			var c := Camera3D.new()
			add_child(c)
			c.fov = 50.0
			c.global_position = p + Vector3(0.0, 1.9, 2.0)
			c.look_at(p, Vector3.UP)
			c.current = true
			await shot(v[0], v[1] + "_close")
			c.queue_free()
			break
	end_test()


func look_check(dir: String, what: String) -> void:
	# ↑ held, then ↓ held: where the view points after each (its height, -1 the ground … +1 the sky), and a picture
	var fy := func() -> float: return -get_viewport().get_camera_3d().global_basis.z.y
	await get_tree().create_timer(1.0).timeout
	var y0: float = fy.call()
	m.vkeys[KEY_UP] = true
	await get_tree().create_timer(0.9).timeout
	m.vkeys.erase(KEY_UP)
	await get_tree().create_timer(0.4).timeout
	var yu: float = fy.call()
	get_viewport().get_texture().get_image().save_png(dir.path_join(what + "_1_up.png"))
	m.vkeys[KEY_DOWN] = true
	await get_tree().create_timer(1.8).timeout
	m.vkeys.erase(KEY_DOWN)
	await get_tree().create_timer(0.4).timeout
	var yd: float = fy.call()
	get_viewport().get_texture().get_image().save_png(dir.path_join(what + "_2_down.png"))
	printerr("LOOK %-11s start %+.2f  after up %+.2f (%s)  after down %+.2f (%s)" % [what, y0, yu,
		"UP ok" if yu > y0 + 0.05 else "WRONG", yd, "DOWN ok" if yd < yu - 0.05 else "WRONG"])


func run_looktest(spec: String) -> void:
	# (round 41c, the user: "check down direction when she's sitting down on the bench… Pressing up should go to the sky.
	# And down to the ground. Check all first persons") every view at her own eyes: a bench, the viewfinder, the wheel's
	# gondola, the funicular's seat, the telescope (--looktest=<dir>[,part,part…]: only those)
	var dir := spec.split(",")[0]
	var parts := Array(spec.split(",")).slice(1)
	if parts.is_empty():
		parts = ["bench", "viewfinder", "wheel", "funicular", "telescope"]
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.money = maxi(int(m.game.S.money), 1000)
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	for a in OS.get_cmdline_user_args():                # (--skin=1: in her other outfit)
		if a.begins_with("--skin="):
			m.show_skin(int(a.substr(7)))
			await get_tree().create_timer(1.0).timeout
	# a bench in the city
	for b in (m.benches.list if ("bench" in parts or "hillbench" in parts) else []):
		if ((b[0] as Vector2).y < -100.0 and (b[0] as Vector2).x < -40.0) if "hillbench" in parts else ((b[0] as Vector2).y > -60.0):
			var fr: Vector2 = b[0] + b[1] * 0.75
			place(fr.x, fr.y, atan2(-b[1].x, -b[1].y))
			await get_tree().create_timer(1.2).timeout
			m.interact()
			await get_tree().create_timer(1.5).timeout
			if m.benches.seated():
				await get_tree().create_timer(0.6).timeout
				get_viewport().get_texture().get_image().save_png(dir.path_join("bench_0_sat.png"))
				await look_check(dir, "bench")
				m.input_key(KEY_E)                           # (E gets her up, as a player does)
				await get_tree().create_timer(1.2).timeout
				printerr("LOOK bench: got up=%s" % (not m.benches.seated()))
			else:
				printerr("LOOK bench: couldn't sit")
			break
	await get_tree().create_timer(1.5).timeout
	# the viewfinder, standing
	if "viewfinder" in parts:
		m.viewfinder(true)
		await look_check(dir, "viewfinder")
		m.viewfinder(false)
		await get_tree().create_timer(1.0).timeout
	if "wheel" in parts:
		await look_wheel(dir)
	if "funicular" in parts:
		await look_funicular(dir)
	if "telescope" in parts:
		await look_telescope(dir)
	end_test()


func look_wheel(dir: String) -> void:
	# the wheel's gondola, at her eyes
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.act("wheel")
	await talk_through([0])
	var tw := Time.get_ticks_msec()
	while Time.get_ticks_msec() - tw < 60000 and String(m.north.ride.get("phase", "")) != "round":
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join("wheel_0_seated.png"))
	printerr("LOOK wheel: sitting=%s" % (not m.north.seat.is_empty()))
	m.input_key(KEY_E)
	await get_tree().create_timer(0.5).timeout
	printerr("LOOK wheel: at her eyes=%s" % m.ride_look)
	await look_check(dir, "wheel")
	while not m.north.ride.is_empty():
		await get_tree().create_timer(0.5).timeout
	await get_tree().create_timer(1.0).timeout


func look_funicular(dir: String) -> void:
	# the funicular's seat, going up
	var d: Array = m.D.north.cable.door_low
	place(d[0], d[1] + 1.0, PI)
	await get_tree().create_timer(0.8).timeout
	m.north.start_cable(true)
	await get_tree().create_timer(4.0).timeout
	m.north.ride_toggle()
	printerr("LOOK funicular: at her eyes=%s" % m.ride_look)
	await look_check(dir, "funicular")
	while not m.north.ride.is_empty():
		await get_tree().create_timer(0.5).timeout
	await get_tree().create_timer(1.0).timeout


func look_telescope(dir: String) -> void:
	# the telescope
	var tl: Array = m.D.north.get("telescope", [])
	if tl.size() >= 3:
		place(tl[0] - sin(tl[2]) * 0.9, tl[1] - cos(tl[2]) * 0.9, tl[2])
		await get_tree().create_timer(1.0).timeout
		m.north.act("telescope")
		await talk_through([0])
		await get_tree().create_timer(1.0).timeout
		printerr("LOOK telescope: on=%s" % (not m.north.scope.is_empty()))
		await look_check(dir, "telescope")


func run_vfride(dir: String) -> void:
	# (round 41c, the user: "the photo in the gondola is weird… when you transition… the camera mode should disappear")
	# the camera raised in the funicular following the car (a photo, saved on the Desktop as ever), then left up till
	# the ride's end; then raised by a door, and the door gone through
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	var d: Array = m.D.north.cable.door_low
	place(d[0], d[1] + 1.0, PI)
	await get_tree().create_timer(0.8).timeout
	m.north.start_cable(true)
	await get_tree().create_timer(6.0).timeout
	printerr("VFRIDE in the car: at her seat=%s" % m.ride_look)
	m.viewfinder(true)
	await get_tree().create_timer(1.0).timeout
	printerr("VFRIDE camera up: at her seat=%s eye %.2f m over the seat point" % [m.ride_look,
		m.vf_cam.global_position.y - m.north.seat_point().y])
	get_viewport().get_texture().get_image().save_png(dir.path_join("1_viewfinder_in_car.png"))
	await m.take_photo()
	await get_tree().create_timer(1.0).timeout
	printerr("VFRIDE after the photo: camera still up=%s" % m.vf_on)
	while not m.north.ride.is_empty():
		await get_tree().process_frame
	await get_tree().create_timer(1.0).timeout
	printerr("VFRIDE ride over: camera up=%s (should be false)" % m.vf_on)
	# a door: the camera up beside one, then in
	var e: Dictionary = {}
	for en in m.D.entrances:
		if String(en.get("int", "")) != "" and en.id == "cafe_rambla":
			e = en
	if not e.is_empty():
		var n := Vector2(e.normal[0], e.normal[1])
		place(e.pos[0] + n.x * 1.2, e.pos[1] + n.y * 1.2, atan2(-n.x, -n.y))
		await get_tree().create_timer(1.0).timeout
		m.viewfinder(true)
		await get_tree().create_timer(0.8).timeout
		m.enter(e)
		await get_tree().create_timer(2.0).timeout
		printerr("VFRIDE through the door: inside=%s camera up=%s (should be false)" % [m.where == "in", m.vf_on])
		get_viewport().get_texture().get_image().save_png(dir.path_join("2_after_door.png"))
		# (round 41c, the user: "walk in and out of rooms while the camera is going on… I'm stuck in the tree") raised
		# inside, then out of the door
		m.viewfinder(true)
		await get_tree().create_timer(0.8).timeout
		m.leave()
		await get_tree().create_timer(2.5).timeout
		printerr("VFRIDE out of the door: outside=%s camera up=%s view from the street camera=%s" % [m.where == "out", m.vf_on,
			get_viewport().get_camera_3d() == m.cam])
		get_viewport().get_texture().get_image().save_png(dir.path_join("3_after_leaving.png"))
	end_test()


func run_bielball(dir: String) -> void:
	# (round 41c, the user: the ball at Biel's feet once given back, only to look at) the mission done, Biel's spot from
	# Sandra's side, and what E offers there
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.missions["ball"] = {"st": "done", "num": 9}
	m.touches.refresh()
	var b: Node3D = m.touches.biel_ball
	var q: Dictionary = m.npcs.outdoor.biel
	printerr("BIELBALL shown=%s at (%.2f, %.2f), Biel at (%.2f, %.2f) facing %.2f" % [b.visible, b.position.x, b.position.z,
		q.home.x, q.home.z, q.home_yaw])
	var fwd := Vector3(sin(q.home_yaw), 0, cos(q.home_yaw))
	var at: Vector3 = b.position + fwd * 1.0 + Vector3(fwd.z, 0, -fwd.x) * 0.6
	place(at.x, at.z, atan2(b.position.x - at.x, b.position.z - at.z))
	await get_tree().create_timer(2.5).timeout
	printerr("BIELBALL E offers: %s" % m.nearest().get("label", "NOTHING"))
	place(at.x + fwd.x * 2.5, at.z + fwd.z * 2.5, atan2(b.position.x - at.x - fwd.x * 2.5, b.position.z - at.z - fwd.z * 2.5))
	await shot(dir, "biel_ball")
	end_test()


func vf_state(dir: String, tag: String) -> void:
	var c := get_viewport().get_camera_3d()
	var view := "street camera" if c == m.cam else ("room camera" if c == m.room_cam else ("viewfinder" if c == m.vf_cam else "other: " + str(c)))
	printerr("VFCHAIN %-24s camera up=%-5s view=%-14s Sandra shown=%-5s boxes shown=%-5s where=%s seated=%s riding=%s" % [tag, m.vf_on,
		view, m.model.visible, m.hud_root.visible, m.where, m.benches.seated(), not m.north.ride.is_empty()])
	get_viewport().get_texture().get_image().save_png(dir.path_join(tag.replace(" ", "_") + ".png"))


func run_vfchain(dir: String) -> void:
	# (round 41c, the user: "check what the camera does when you go into a room, out of a room, then use the funicular
	# or if you're on the funicular, then you get off… on a chair… the Ferris wheel… when you get off the Ferris wheel and
	# the camera is activated") each with the camera up, and what's left after: the camera put away, the right view,
	# Sandra and the boxes back
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.money = maxi(int(m.game.S.money), 1000)
	m.game.S.flags["guellBack"] = true
	m.game.add_item("park_pass")
	# a room, in and out
	var e: Dictionary = {}
	for en in m.D.entrances:
		if en.id == "cafe_rambla":
			e = en
	var n := Vector2(e.normal[0], e.normal[1])
	place(e.pos[0] + n.x * 1.2, e.pos[1] + n.y * 1.2, atan2(-n.x, -n.y))
	await get_tree().create_timer(1.0).timeout
	m.viewfinder(true)
	await get_tree().create_timer(0.8).timeout
	m.enter(e)
	await get_tree().create_timer(2.5).timeout
	await vf_state(dir, "1 into a room")
	m.viewfinder(true)
	await get_tree().create_timer(0.8).timeout
	m.leave()
	await get_tree().create_timer(2.5).timeout
	await vf_state(dir, "2 out of the room")
	# the funicular: up as she boards, then up in the car till the end
	var d: Array = m.D.north.cable.door_low
	place(d[0], d[1] + 1.0, PI)
	await get_tree().create_timer(1.0).timeout
	m.viewfinder(true)
	await get_tree().create_timer(0.8).timeout
	m.north.start_cable(true)
	await get_tree().create_timer(3.0).timeout
	await vf_state(dir, "3 boarding the funicular")
	m.viewfinder(true)
	await get_tree().create_timer(1.0).timeout
	await vf_state(dir, "4 camera up in the car")
	while not m.north.ride.is_empty():
		await get_tree().process_frame
	await get_tree().create_timer(1.5).timeout
	await vf_state(dir, "5 off the funicular")
	# a bench: sat, camera up, E (a photo), Esc, E
	for b in m.benches.list:
		if (b[0] as Vector2).y > -60.0:
			var fr: Vector2 = b[0] + b[1] * 0.75
			place(fr.x, fr.y, atan2(-b[1].x, -b[1].y))
			await get_tree().create_timer(1.2).timeout
			m.input_key(KEY_E)
			await get_tree().create_timer(1.5).timeout
			m.viewfinder(true)
			await get_tree().create_timer(1.0).timeout
			m.input_key(KEY_E)
			await get_tree().create_timer(1.5).timeout
			await vf_state(dir, "6 bench E with camera")
			m.input_key(KEY_ESCAPE)
			await get_tree().create_timer(1.0).timeout
			await vf_state(dir, "7 bench Esc")
			m.input_key(KEY_E)
			await get_tree().create_timer(1.5).timeout
			await vf_state(dir, "8 bench E again")
			break
	# the wheel: camera up till the ride ends
	var W: Dictionary = m.D.north.wheel
	place(float(W.gate[0]), float(W.gate[1]) + 0.8, PI)
	await get_tree().create_timer(1.0).timeout
	m.north.act("wheel")
	await talk_through([0])
	var tw := Time.get_ticks_msec()
	while Time.get_ticks_msec() - tw < 60000 and String(m.north.ride.get("phase", "")) != "round":
		await get_tree().process_frame
	m.viewfinder(true)
	await get_tree().create_timer(1.0).timeout
	await vf_state(dir, "9 camera up on the wheel")
	while not m.north.ride.is_empty():
		await get_tree().process_frame
	await get_tree().create_timer(1.5).timeout
	await vf_state(dir, "10 off the wheel")
	end_test()


func run_lookstate() -> void:
	# (round 41c, the user: "by removing them, you've switched them on. Could you review") the look's switches as the
	# game starts, outdoors and in a room
	await get_tree().create_timer(4.0).timeout
	var pr := func(where: String) -> void:
		printerr("LOOKSTATE %s: full look=%s light shafts=%s bounce light=%s soft bounce=%s debug menu=%s corner='%s'" % [where,
			m.high_quality, m.env_out.volumetric_fog_enabled, m.env_out.sdfgi_enabled, m.env_out.ssil_enabled, m.debug_on,
			m.stats.text.replace("\n", " / ")])
	pr.call("outdoors")
	for en in m.D.entrances:
		if en.id == "cafe_rambla":
			var n := Vector2(en.normal[0], en.normal[1])
			place(en.pos[0] + n.x * 1.2, en.pos[1] + n.y * 1.2, atan2(-n.x, -n.y))
			await get_tree().create_timer(0.8).timeout
			m.enter(en)
			await get_tree().create_timer(2.5).timeout
			var env: Environment = m.world_env.environment
			printerr("LOOKSTATE in a room: light shafts=%s bounce light=%s" % [env.volumetric_fog_enabled, env.sdfgi_enabled])
	end_test()


func dog_report(dir: String, tag: String, look_at: Vector3, from_dir: Vector3) -> void:
	# her state, and how far her lowest paw is from the ground (below 0: sunk in); a picture from the side
	var tr: Node3D = m.street.trufa
	var low := INF
	for bn in ["backleg2", "R_backleg2", "frontleg1", "R_frontleg1"]:
		var bi: int = tr.skel.find_bone(bn)
		if bi >= 0:
			low = minf(low, (tr.skel.global_transform * tr.skel.get_bone_global_pose(bi)).origin.y)
	printerr("DOGSETTLE   at (%.2f, %.2f) local (%.2f, %.2f), Sandra (%.2f, %.2f), state %d, still_t %.1f, parent %s" % [tr.global_position.x, tr.global_position.z,
		tr.position.x, tr.position.z, m.player.global_position.x, m.player.global_position.z, tr.state, tr.still_t, tr.get_parent().name])
	printerr("DOGSETTLE %-18s speed %.2f sit %.2f legs-going %.2f lowest paw %+.3f m over the ground  E offers: %s" % [tag, tr.speed,
		tr.sit, tr.ap.speed_scale if tr.ap else 0.0, low - m.ground_at(tr.global_position), m.nearest().get("label", "nothing")])
	var cc := Camera3D.new()
	add_child(cc)
	cc.fov = 45.0
	cc.global_position = look_at + from_dir.normalized() * 3.2 + Vector3(0, 1.1, 0)
	cc.look_at(look_at + Vector3(0, 0.35, 0), Vector3.UP)
	cc.current = true
	for i in 3:
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(dir.path_join(tag.replace(" ", "_") + ".png"))
	cc.queue_free()
	m.cam.current = true


func run_dogsettle(dir: String) -> void:
	# (round 41c, 10 #26a/#26b) Trufa following: walking, stopped 1 s and 4 s, then on a city bench and a hill bench;
	# what E offers with her beside Sandra
	DirAccess.make_dir_recursive_absolute(dir)
	await get_tree().create_timer(3.0).timeout
	m.set_clock(660.0)
	m.game.S.missions["dog"] = {"st": "done", "num": 3}
	var tr: Node3D = m.street.trufa
	for bi in [0, 1]:
		var pick: Array = []
		for b in m.benches.list:
			var ok: bool = (b[0] as Vector2).y > -60.0 if bi == 0 else ((b[0] as Vector2).y < -100.0 and (b[0] as Vector2).x < -40.0)
			if ok:
				pick = b
				break
		var fr: Vector2 = pick[0] + pick[1] * 4.0
		place(fr.x, fr.y, atan2(-pick[1].x, -pick[1].y))
		tr.global_position = Vector3(fr.x + 1.0, m.ground_at(Vector3(fr.x, 0, fr.y)), fr.y + 1.0)
		tr.state = tr.FOLLOW
		tr.trail.clear()
		await get_tree().create_timer(1.0).timeout
		# walk up to the bench, stop in front of it
		m.vkeys[KEY_W] = true
		await get_tree().create_timer(1.0).timeout
		m.vkeys.clear()
		var tag := "city" if bi == 0 else "hill"
		await get_tree().create_timer(1.0).timeout
		var side := Vector3(-pick[1].y, 0, pick[1].x)
		await dog_report(dir, tag + " stopped 1s", tr.global_position, side)
		await get_tree().create_timer(3.0).timeout
		await dog_report(dir, tag + " stopped 4s", tr.global_position, side)
		var fr2: Vector2 = pick[0] + pick[1] * 0.75
		place(fr2.x, fr2.y, atan2(-pick[1].x, -pick[1].y))
		await get_tree().create_timer(0.8).timeout
		printerr("DOGSETTLE %s before the bench, E offers: %s" % [tag, m.nearest().get("label", "nothing")])
		m.input_key(KEY_E)
		await get_tree().create_timer(4.0).timeout
		var bp := Vector3(pick[0].x, m.ground_at(Vector3(pick[0].x, 0, pick[0].y)), pick[0].y)
		await dog_report(dir, tag + " on the bench", bp + Vector3(pick[1].x, 0, pick[1].y) * 0.6, side * 1.0 + Vector3(pick[1].x, 0, pick[1].y) * 0.8)
		m.input_key(KEY_E)
		await get_tree().create_timer(2.0).timeout
		printerr("DOGSETTLE %s got up: seated=%s, Trufa following=%s" % [tag, m.benches.seated(), tr.state == tr.FOLLOW])
	# by her own bike, Trufa beside: E offers the bike
	m.game.S.has_bike = true
	var bk: Node3D = m.street.own_bike
	if bk:
		place(bk.position.x + 0.9, bk.position.z, -PI / 2.0)
		tr.global_position = bk.position + Vector3(1.3, 0, 0.6)
		await get_tree().create_timer(1.0).timeout
		printerr("DOGSETTLE by the bike with Trufa beside: E offers %s" % m.nearest().get("label", "nothing"))
	# staying put: she comes first
	tr.state = tr.STAY
	await get_tree().create_timer(0.5).timeout
	printerr("DOGSETTLE Trufa told to stay, by the bike: E offers %s" % m.nearest().get("label", "nothing"))
	end_test()


func run_doghome() -> void:
	# (round 41c, 10 #26c) H with Trufa following: once her mission is done she's back at Montse's feet; before, she
	# comes home with Sandra
	await get_tree().create_timer(3.0).timeout
	var tr: Node3D = m.street.trufa
	for done in [true, false]:
		if done:
			m.game.S.missions["dog"] = {"st": "done", "num": 3}
		else:
			m.game.S.missions["dog"] = {"st": "active", "num": 3}
		place(30.0, 50.0, 0.0)
		tr.position = Vector3(31.0, m.ground_at(Vector3(31, 0, 50)), 50.5)
		tr.follow()
		await get_tree().create_timer(1.0).timeout
		m.take_me_home()
		await talk_through([0])
		await get_tree().create_timer(2.5).timeout
		var p: Vector3 = m.player.global_position
		printerr("DOGHOME mission done=%s: state %d (home %d, following %d), %.1f m from her owner's spot, %.1f m from Sandra" % [done,
			tr.state, tr.HOME, tr.FOLLOW, Vector2(tr.position.x - tr.home_pos.x, tr.position.z - tr.home_pos.z).length(),
			Vector2(tr.position.x - p.x, tr.position.z - p.z).length()])
	end_test()
