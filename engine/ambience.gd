# Sound: the street soundscape (muffled indoors), the music (outdoor and indoor tunes),
# Sandra's footsteps, the sea (louder the nearer the shore, swelling, as in the 2D game), and the 2D
# game's little sound effects (sfx(): coin, pickup, door, page, bell, fanfare...). The audio is rendered by shared/build_audio.py into godot/audio/.
extends Node

# Music follows where Sandra is: Rumba on the street, a soft Passeig at home. M turns it off and on.
const MUSIC_OUT := -15.0
const MUSIC_IN := -17.0

var street: AudioStreamPlayer
var street_in: AudioStreamPlayer
var music_out: AudioStreamPlayer
var music_in: AudioStreamPlayer
var steps: AudioStreamPlayer
var step_pavement: Array = []
var step_tiles: Array = []
var music_on := true
var music_tw: Tween
var outdoors := true
var rng := RandomNumberGenerator.new()
var sea: AudioStreamPlayer
var hush := false                # the title screen: no sea or street from where she stands, a far-off city hum
var amb_tw: Tween
const BEGIN_FADE := 0.45         # (the user: "make the fade in 70% quicker", from 1.5 s)
var begin_ms := -1               # when begin() started the opening fade (real milliseconds), -1 when done
var started := false             # begin() has started the sounds (after loading)
var wake := 1.0                  # after the title: the sea comes up from nothing over a couple of seconds
# (round 41, the user chose "music plus a soft city hum on the title"): the muffled street, quietly, under the music
const TITLE_HUM := -26.0
var fx := {}                     # name -> AudioStreamWAV
var fx_players: Array = []
var fx_next := 0


func _ready() -> void:
	street = make_player("street.wav", -14.0)
	street_in = make_player("street_indoors.wav", -80.0)
	music_out = make_player("music_rumba.wav", MUSIC_OUT)
	music_in = make_player("music_passeig_soft.wav", -80.0)
	steps = AudioStreamPlayer.new()
	steps.volume_db = -26.0                     # soft: you notice them, you don't hear them
	steps.max_polyphony = 3
	add_child(steps)
	for i in 6:
		step_pavement.append(load_wav("step_pavement_%d.wav" % i, false))
		step_tiles.append(load_wav("step_tiles_%d.wav" % i, false))
	sea = make_player("sea.wav", -80.0)
	for f in DirAccess.get_files_at("res://bigfiles/built/audio"):
		if f.begins_with("sfx_") and f.ends_with(".wav"):
			fx[f.trim_prefix("sfx_").trim_suffix(".wav")] = load_wav(f, false)
	for i in 6:
		var p := AudioStreamPlayer.new()
		p.volume_db = -8.0
		add_child(p)
		fx_players.append(p)
	# (round 41, rule 08 #82d) nothing plays while the city loads behind the Godot screen: begin() starts it all


func load_wav(file: String, loop: bool) -> AudioStreamWAV:
	var w := AudioStreamWAV.load_from_file(ProjectSettings.globalize_path("res://bigfiles/built/audio/" + file))
	if loop:
		w.loop_mode = AudioStreamWAV.LOOP_FORWARD
		w.loop_begin = 0
		w.loop_end = w.data.size() / 4          # 16-bit stereo frames
	return w


func make_player(file: String, db: float) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.stream = load_wav(file, true)
	p.volume_db = db
	add_child(p)
	return p


func toggle_music() -> String:
	music_on = not music_on
	fade_music()
	return "Music on" if music_on else "Music off"


func fade_music() -> void:
	# the tune for where she is fades in from the start; the other fades out and stops
	var now := music_out if outdoors else music_in
	var other := music_in if outdoors else music_out
	if music_tw:
		music_tw.kill()
	var tw := create_tween().set_parallel(true)
	music_tw = tw
	if music_on:
		if not now.playing:
			now.volume_db = -40.0
			now.play()
		tw.tween_property(now, "volume_db", MUSIC_OUT if outdoors else MUSIC_IN, 1.2)
	else:
		tw.tween_property(now, "volume_db", -80.0, 0.8)
	tw.tween_property(other, "volume_db", -80.0, 0.8)
	tw.chain().tween_callback(func():
		if other.volume_db <= -79.0:
			other.stop()
		if not music_on:
			now.stop())


func set_outdoors(out: bool, secs := 0.6) -> void:
	outdoors = out
	if not hush:                                # (on the title the hum stays until she starts)
		if amb_tw:
			amb_tw.kill()
		amb_tw = create_tween().set_parallel(true)
		amb_tw.tween_property(street, "volume_db", -14.0 if out else -80.0, secs)
		amb_tw.tween_property(street_in, "volume_db", -80.0 if out else -22.0, secs)
	fade_music()


func begin(title: bool) -> void:
	# the first picture is up: the music, with the title's far-off hum (title) or her place's own sounds, fades in.
	# The fade is the whole game's volume on the real clock: the first frames after loading are slow, and the game's
	# own clock (and every tween) crawls through them — a half-second fade took two and a half
	if title:
		title_hush(true)
	if not started:
		started = true
		AudioServer.set_bus_volume_db(0, -80.0)
		begin_ms = Time.get_ticks_msec()
		if not title:
			street.volume_db = -14.0 if outdoors else -80.0
			street_in.volume_db = -80.0 if outdoors else -22.0
		street.play()
		street_in.play()
		sea.play()
		var now := music_out if outdoors else music_in
		if music_on:
			now.volume_db = MUSIC_OUT if outdoors else MUSIC_IN
			now.play()


func _process(_dt: float) -> void:
	if begin_ms >= 0:
		var k := clampf((Time.get_ticks_msec() - begin_ms) / (BEGIN_FADE * 1000.0), 0.0, 1.0)
		AudioServer.set_bus_volume_db(0, linear_to_db(maxf(k, 0.0001)))
		if k >= 1.0:
			begin_ms = -1


func title_hush(on: bool) -> void:
	# (round 41, rule 08 #82d) the title sounds like the view over the city, not the beach she stands on behind it;
	# once she is in her place, its own sounds fade in (the sea rises by itself in sea_near)
	hush = on
	if on:
		if amb_tw:
			amb_tw.kill()
		street.volume_db = -80.0
		street_in.volume_db = TITLE_HUM
		sea.volume_db = -80.0
	else:
		street.volume_db = maxf(street.volume_db, -40.0)   # (from just under hearing, so the fade is heard through)
		set_outdoors(outdoors, 1.8)
		wake = 0.0
		create_tween().tween_property(self, "wake", 1.0, 2.0)


# (round 23, the user: "make the mission dings quieter: mission notifications, getting on the bike, etc."): dB
# under the other effects
const FX_TRIM := {"quest": -10.0, "fanfare": -9.0, "bell": -10.0, "coin": -6.0, "pickup": -6.0, "buy": -5.0, "page": -4.0,
	"open": -4.0, "select": -4.0, "tick": -4.0}


func sfx(name: String) -> void:
	if not fx.has(name):
		return
	var p: AudioStreamPlayer = fx_players[fx_next]
	fx_next = (fx_next + 1) % fx_players.size()
	p.stream = fx[name]
	p.volume_db = -8.0 + float(FX_TRIM.get(name, 0.0))
	p.play()


func sea_near(dist: float) -> void:
	# metres from the water's edge: heard from about 40 m away, louder as she comes down the beach
	var v := clampf(1.0 - dist / 40.0, 0.0, 1.0) if outdoors and not hush else 0.0
	sea.volume_db = lerpf(sea.volume_db, linear_to_db(maxf(0.0001, v * 0.5 * wake)), 0.05)


func footstep(on_road: bool) -> void:
	var pool := step_tiles if not outdoors else step_pavement
	steps.stream = pool[rng.randi() % pool.size()]
	steps.pitch_scale = rng.randf_range(0.9, 1.08) * (0.9 if on_road else 1.0)
	steps.volume_db = -26.0 + rng.randf_range(-2.0, 1.0)
	steps.play()
