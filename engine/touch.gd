# On-screen controls for phones and tablets (round 20e), laid out like the 2D game's: a pad bottom left to
# walk, A (talk, look, pick up, use; confirm) and B (back: close a panel or the map, cancel a choice) bottom
# right, and a slim column of buttons down the right edge: BAG, MAP, LOG, BIKE, LOOK, DEBUG and ☰ (the menu).
# Held upright (portrait), the game fills the top of the screen and the controls sit on a very dark grey deck
# underneath, covering nothing: the buttons in a row along its top, the pad and A/B below them.
# LOOK switches looking round on: then a finger dragged anywhere else on the screen turns the camera, as the
# mouse does on a computer; LOOK again switches it off. Several fingers at once (walk with one, look with
# another). Shown when the device has a touch screen, or with --touch (a computer's mouse then acts as a
# finger, to try it). The pad and the buttons feed the game the same keys a keyboard would (main.gd).
extends Control

const LOOK_SENS := 0.0042          # radians per pixel dragged (a swipe across the screen: about a turn and a half)
const DPAD := ["up", "left", "right", "down"]
const PAD_KEY := {"up": KEY_W, "down": KEY_S, "left": KEY_A, "right": KEY_D}
const MENU_KEY := {"up": KEY_UP, "down": KEY_DOWN, "left": KEY_LEFT, "right": KEY_RIGHT}

var main: Node
var buttons := {}                  # id -> {rect, round, label, down, eater (a Control that swallows the mouse)}
var fingers := {}                  # touch index -> button id, or "look"
var look_on := false
var font: Font
var portrait := false
var deck := 0.0                    # the deck's height (portrait), else 0
var deck_eater: Control


func setup(m: Node) -> void:
	main = m
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	font = ThemeDB.fallback_font
	for id in DPAD + ["A", "B", "BAG", "MAP", "LOG", "BIKE", "LOOK"] + (["DEBUG"] if main.debug_on else []) + ["MENU"]:
		# (an invisible control on each button eats the mouse click a tap also makes, so it can't click
		# whatever lies under the button, a backpack slot say)
		var eater := Control.new()
		eater.mouse_filter = Control.MOUSE_FILTER_STOP
		add_child(eater)
		buttons[id] = {"rect": Rect2(), "round": id in ["A", "B"], "label": {"up": "▲", "down": "▼", "left": "◀", "right": "▶",
			"MENU": "☰"}.get(id, id), "down": false, "eater": eater}
	deck_eater = Control.new()
	deck_eater.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(deck_eater)
	move_child(deck_eater, 0)
	place()
	get_viewport().size_changed.connect(place)


func place() -> void:
	# (upright, the screen is laid out 800 wide, so the writing stays a readable size; on its side, 1280 x 800
	# as on a computer)
	var win := get_tree().root.size
	var upright := win.y > win.x * 1.05
	var base := Vector2i(800, 1280) if upright else Vector2i(1280, 800)
	if get_tree().root.content_scale_size != base:
		get_tree().root.content_scale_size = base
		place.call_deferred()                           # (once the new size has taken)
		return
	portrait = upright
	var vs := get_viewport().get_visible_rect().size
	var row := ["BAG", "MAP", "LOG", "BIKE", "LOOK"] + (["DEBUG"] if main.debug_on else []) + ["MENU"]     # (DEBUG only with --debug)
	var at: Dictionary
	if portrait:
		# the deck: the buttons in a row along its top, the pad bottom left, A and B bottom right
		deck = roundf(clampf(vs.y * 0.3, 380.0, 540.0))
		var top := vs.y - deck
		var gap := 8.0
		var w := (vs.x - 32.0 - gap * (row.size() - 1)) / row.size()
		for i in row.size():
			buttons[row[i]].rect = Rect2(16.0 + i * (w + gap), top + 14.0, w, 50.0)
		var b := minf(118.0, (deck - 64.0 - 40.0) / 3.0)
		var px := 24.0
		var py := vs.y - 24.0 - 3.0 * b
		at = {"up": Vector2(b, 0), "left": Vector2(0, b), "right": Vector2(2 * b, b), "down": Vector2(b, 2 * b)}
		for d in DPAD:
			buttons[d].rect = Rect2(Vector2(px, py) + at[d] + Vector2(3, 3), Vector2(b - 6, b - 6))
		var a := b * 1.3
		var bb := a * 0.8
		buttons.A.rect = Rect2(vs.x - 26.0 - a, py + b * 0.2, a, a)
		buttons.B.rect = Rect2(vs.x - 40.0 - a - bb, vs.y - 30.0 - bb, bb, bb)
	else:
		# on its side: the pad and A/B in the bottom corners, the column under the money, top right
		deck = 0.0
		var b := clampf(vs.y * 0.105, 64.0, 96.0)          # a pad button
		var px := 30.0
		var py := vs.y - 30.0 - 3.0 * b
		at = {"up": Vector2(b, 0), "left": Vector2(0, b), "right": Vector2(2 * b, b), "down": Vector2(b, 2 * b)}
		for d in DPAD:
			buttons[d].rect = Rect2(Vector2(px, py) + at[d] + Vector2(3, 3), Vector2(b - 6, b - 6))
		var a := b * 1.3
		var bb := a * 0.8
		buttons.A.rect = Rect2(vs.x - 34.0 - a, vs.y - 40.0 - bb * 0.6 - a, a, a)
		buttons.B.rect = Rect2(vs.x - 48.0 - a - bb, vs.y - 30.0 - bb, bb, bb)
		var w := 98.0
		var h := clampf(vs.y * 0.058, 40.0, 54.0)
		var y := 96.0                                   # (under the money)
		for id in row:
			buttons[id].rect = Rect2(vs.x - 18.0 - w, y, w, h)
			y += h + 8.0
	for id in buttons:
		var r: Rect2 = buttons[id].rect
		buttons[id].eater.position = r.position
		buttons[id].eater.size = r.size
	deck_eater.position = Vector2(0, vs.y - deck)       # (taps on the deck between buttons do nothing)
	deck_eater.size = Vector2(vs.x, deck)
	queue_redraw()


func left_inset() -> float:
	# (how much of the screen's left and right the controls take, so the talk box keeps clear of them; upright
	# they are all on the deck, below it)
	return 0.0 if portrait else (buttons.right.rect.end.x + 16.0 if buttons.has("right") else 0.0)


func modal() -> bool:
	return main.panels.is_open() or main.dlg_open or main.map_panel.visible


func hit(p: Vector2) -> String:
	for id in buttons:
		var r: Rect2 = buttons[id].rect
		if buttons[id].round:
			if p.distance_to(r.get_center()) <= r.size.x * 0.56:
				return id
		elif r.grow(4.0).has_point(p):
			return id
	return ""


func _input(e: InputEvent) -> void:
	if not visible:
		return
	if e is InputEventScreenTouch:
		if e.pressed:
			var id := hit(e.position)
			if id != "":
				fingers[e.index] = id
				press(id)
				get_viewport().set_input_as_handled()
			elif deck > 0.0 and e.position.y > get_viewport().get_visible_rect().size.y - deck:
				get_viewport().set_input_as_handled()       # (the deck between the buttons)
			elif look_on and not main.panels.is_open() and not main.map_panel.visible:
				fingers[e.index] = "look"
				get_viewport().set_input_as_handled()
		elif fingers.has(e.index):
			var id: String = fingers[e.index]
			fingers.erase(e.index)
			if id != "look":
				release(id)
			get_viewport().set_input_as_handled()
	elif e is InputEventScreenDrag and fingers.has(e.index):
		var id: String = fingers[e.index]
		if id == "look":
			main.turn_camera(-e.relative.x * LOOK_SENS, -e.relative.y * LOOK_SENS)
		elif id in DPAD:
			# sliding a thumb round the pad goes from one direction to the next
			var now := hit(e.position)
			if now in DPAD and now != id:
				release(id)
				fingers[e.index] = now
				press(now)
		get_viewport().set_input_as_handled()


func press(id: String) -> void:
	buttons[id].down = true
	queue_redraw()
	if id in DPAD:
		if modal():
			main.input_key(MENU_KEY[id])                # (in a panel, the talk box's choices or the map: a step)
		else:
			main.vkeys[PAD_KEY[id]] = true              # (walking: held as long as the finger stays)
		return
	match id:
		"A":
			main.input_key(KEY_ENTER if main.panels.is_open() else KEY_E)
		"B":
			if modal():
				main.input_key(KEY_ESCAPE)
		"BAG":
			main.input_key(KEY_I)
		"MAP":
			main.input_key(KEY_M)
		"LOG":
			main.input_key(KEY_J)
		"BIKE":
			main.input_key(KEY_B)
		"DEBUG":
			main.input_key(KEY_P)
		"MENU":
			main.input_key(KEY_ESCAPE)
		"LOOK":
			look_on = not look_on
			main.toast("Look around: drag on the screen  (LOOK again to stop)" if look_on else "Look around: off")


func release(id: String) -> void:
	buttons[id].down = false
	queue_redraw()
	if id in DPAD:
		main.vkeys.erase(PAD_KEY[id])


func release_all() -> void:
	for i in fingers.keys():
		if fingers[i] != "look":
			release(fingers[i])
	fingers.clear()


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT or what == NOTIFICATION_APPLICATION_PAUSED:
		release_all()                                     # (a phone call mustn't leave her walking)


func _draw() -> void:
	# the 2D game's look, on the HUD's dark backing: a warmer glow while pressed; LOOK stays lit while it is on
	if deck > 0.0:
		var vs := get_viewport().get_visible_rect().size
		draw_rect(Rect2(0, vs.y - deck, vs.x, deck), Color(0.085, 0.085, 0.09))          # the deck: very dark grey
		draw_line(Vector2(0, vs.y - deck), Vector2(vs.x, vs.y - deck), Color(1, 1, 1, 0.08), 2.0)
	for id in buttons:
		var B: Dictionary = buttons[id]
		var r: Rect2 = B.rect
		var lit: bool = B.down or (id == "LOOK" and look_on)
		# (on a dark, see-through backing like the HUD's cards, so the labels read over a sunlit wall too)
		var fill := Color(0.62, 0.38, 0.22, 0.62) if lit else Color(0.16, 0.1, 0.07, 0.38)
		var edge := Color(1.0, 0.86, 0.66, 0.95) if lit else Color(1.0, 0.92, 0.8, 0.5)
		var sb := StyleBoxFlat.new()
		sb.bg_color = fill
		sb.border_color = edge
		sb.set_border_width_all(2)
		sb.set_corner_radius_all(int(r.size.x / 2.0) if B.round else 12)
		sb.anti_aliasing = true
		draw_style_box(sb, r)
		var size := int(r.size.y * (0.36 if (B.round or id in DPAD) else 0.4))
		var label: String = B.label
		var tw := font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
		draw_string(font, Vector2(r.get_center().x - tw / 2.0, r.get_center().y + size * 0.36), label, HORIZONTAL_ALIGNMENT_LEFT, -1, size,
			Color(1.0, 0.97, 0.9, 0.92))
