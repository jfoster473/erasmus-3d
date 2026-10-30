# The backpack and the shop counter, drawn like the 2D game's panels: a cream card with the 2D game's own
# item pictures (icons/<id>.png, painted by its paintIcon()).
#   backpack  a grid of 20 pockets (picture, name, ×count, "worn", ♦ for things someone is counting on),
#             and a box under it with the chosen thing's name, description and what can be done with it.
#             Arrows choose; Enter uses it (eat, read, wear, photograph); E eats, R reads, W wears; I or Esc closes.
#   shop      the shop's title with "Esc to leave" at the top, its goods with their pictures and prices,
#             and your purse. Arrows choose, Enter buys (and the counter stays open), Esc leaves.
#   journal   J: as in the 2D game, the journal's entries (scrolling, opened at the newest) and the
#             achievements on a second page; left/right turn the page, up/down scroll, J or Esc closes.
#             (Round 37) the heroine's notebook, her list of things to do (game.notebook_lines()), is the page to
#             the journal's left.
#   reader    a book or study note, a page at a time, like the 2D game's reader (Space or → on, ← back, Esc closes)
#   container a cupboard or shelf beside the backpack, two lists (← → between them, Enter takes or puts, R reads)
#   bin       a street bin: the backpack's things, Enter throws one away
#   debug     P: a list for trying things out: go anywhere, money, the bike, the time of day, quick walking.
#             Arrows choose, Enter does it, Esc goes back (or closes).
extends CanvasLayer

const CREAM := Color("#f6ecd8")
const INK := Color("#3b2a1e")
const INK2 := Color("#6b5240")
const TERRA := Color("#c46a45")
const TERRA_D := Color("#a8452f")
const GOLD := Color("#e0a93b")
const BORDER := Color("#8a5d3b")

var main: Node
var game: Node
var kind := ""                 # "", "bag", "shop", "journal" or "debug"
var journal_page := 0          # which of journal_pages() is open
var reader := {}               # {title, author, pages, page, back}: a book or note open to read
var cid := ""                  # the cupboard or shelf open
var col := 0                   # 0: its side, 1: the backpack's
var journal_scroll := 0.0
var journal_max := 0.0
var debug_page := "main"
var debug_rows: Array = []     # [label, callable] for the debug page showing
var sel := 0
var shop_id := ""
var cols := 5
var icons := {}
var root: Control


func setup(m: Node) -> void:
	main = m
	game = m.game
	layer = 5


func is_open() -> bool:
	return kind != ""


func icon(id: String) -> Texture2D:
	if icons.has(id):
		return icons[id]
	var img := Image.load_from_file(ProjectSettings.globalize_path(main.world_res("icons/%s.png" % id)))
	var tex: Texture2D = ImageTexture.create_from_image(img) if img else null
	icons[id] = tex
	return tex


func box_style(bg: Color, border: Color, width := 2, radius := 10) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(width)
	sb.set_corner_radius_all(radius)
	return sb


func label(text: String, size: int, col: Color, bold := false) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	if bold:
		var f := SystemFont.new()
		f.font_names = PackedStringArray(["Georgia", "Times New Roman"])
		f.font_weight = 700
		l.add_theme_font_override("font", f)
	return l


func open_bag(at := 0) -> void:
	kind = "bag"
	sel = clampi(at, 0, game.MAX_SLOTS - 1)
	main.dlg_open = true
	main.ambience.sfx("open")
	redraw()


func open_shop(id: String) -> void:
	kind = "shop"
	shop_id = id
	sel = 0
	main.dlg_open = true
	main.ambience.sfx("open")
	redraw()


func journal_pages() -> Array:
	# the journal's pages, left to right: her notebook (if the world has one), the journal, the achievements (if any)
	var out := []
	if not game.notebook_lines().is_empty():
		out.append("notebook")
	out.append("journal")
	if not game.data.ACHIEVEMENTS.is_empty():
		out.append("achievements")
	return out


func open_journal(page := "journal") -> void:
	kind = "journal"
	journal_page = maxi(0, journal_pages().find(page))
	journal_scroll = -1.0                # (opened at the mission being done now)
	main.dlg_open = true
	main.ambience.sfx("open")
	redraw()


func open_reader(title: String, author: String, pages: Array, back := Callable()) -> void:
	kind = "reader"
	reader = {"title": title, "author": author, "pages": pages, "page": 0, "back": back}
	main.dlg_open = true
	main.ambience.sfx("page")
	redraw()


func open_container(id: String) -> void:
	kind = "container"
	cid = id
	col = 0
	sel = 0
	main.dlg_open = true
	main.ambience.sfx("open")
	redraw()


func open_bin() -> void:
	kind = "bin"
	sel = 0
	main.dlg_open = true
	main.ambience.sfx("open")
	redraw()


func open_debug(page := "main") -> void:
	kind = "debug"
	debug_page = page
	sel = 0
	main.dlg_open = true
	main.ambience.sfx("open")
	redraw()


func close(sound := true) -> void:
	kind = ""
	if root:
		root.queue_free()
		root = null
	main.dlg_open = false
	if sound:
		main.ambience.sfx("back")
	game.pump.call_deferred()


# ------------------------------------------------------------------ drawing

func card(w: float, h: float, title: String, hint: String) -> Control:
	if root:
		root.queue_free()
	root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	var vp: Vector2 = main.play_area()
	w = minf(w, vp.x - 32)
	h = minf(h, vp.y - 32)
	var p := Panel.new()
	var sb := box_style(CREAM, BORDER, 3, 12)
	sb.shadow_color = Color(0.24, 0.12, 0.08, 0.35)
	sb.shadow_size = 12
	p.add_theme_stylebox_override("panel", sb)
	p.position = ((vp - Vector2(w, h)) / 2.0).floor()
	p.size = Vector2(w, h)
	root.add_child(p)
	var t := label(title, 20, TERRA_D, true)
	t.position = Vector2(24, 14)
	p.add_child(t)
	var hl := label(hint, 13, INK2)
	hl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	hl.position = Vector2(w - 324, 20)
	hl.size = Vector2(300, 20)
	p.add_child(hl)
	return p


func redraw() -> void:
	if kind == "bag":
		draw_bag()
	elif kind == "shop":
		draw_shop()
	elif kind == "journal":
		draw_journal()
	elif kind == "reader":
		draw_reader()
	elif kind == "container":
		draw_container()
	elif kind == "bin":
		draw_bin()
	elif kind == "debug":
		draw_debug()


func hint_of(keys: String, touch: String) -> String:
	# (help in the words of this device's controls: keys on a computer, the pad, A and B on a touch screen)
	return touch if main.touch_pad else keys


func page_size() -> Vector2:
	# the backpack and the journal: the same card, most of the screen with a clear border round it
	var vp0: Vector2 = main.play_area()
	return Vector2(minf(960.0, vp0.x - 160.0), maxf(420.0, vp0.y - 150.0))


func draw_bag() -> void:
	# most of the screen, like the journal: the 20 pockets, with the chosen thing described underneath
	var S: Dictionary = game.S
	var ps := page_size()
	var p := card(ps.x, ps.y, "SANDRA'S BACKPACK", "%d/%d slots · %s" % [S.inv.size(), game.MAX_SLOTS, game.money(S.money)])
	var w: float = p.size.x
	cols = 5 if w >= 600 else 4
	var rows := int(ceil(game.MAX_SLOTS / float(cols)))
	var gap := 10.0
	var dh := clampf(p.size.y * 0.24, 130.0, 210.0)                 # the detail box
	var sw := floorf((w - 48.0 - (cols - 1) * gap) / cols)
	var sh := floorf((p.size.y - 62.0 - dh - 14.0 - 40.0 - (rows - 1) * gap) / rows)
	var ic := clampf(minf(sh - 34.0, sw - 24.0), 28.0, 110.0)
	var fs := int(clampf(sh * 0.14, 12.0, 18.0))
	var gx := (w - (cols * sw + (cols - 1) * gap)) / 2.0
	var gy := 62.0
	for i in game.MAX_SLOTS:
		var slot := Panel.new()
		var chosen: bool = i == sel
		slot.add_theme_stylebox_override("panel", box_style(Color(0.88, 0.66, 0.23, 0.35) if chosen else Color(0.47, 0.31, 0.2, 0.08),
			GOLD if chosen else Color(0.55, 0.31, 0.2, 0.25), 3 if chosen else 1, 10))
		slot.position = Vector2(gx + (i % cols) * (sw + gap), gy + (i / cols) * (sh + gap))
		slot.size = Vector2(sw, sh)
		slot.mouse_filter = Control.MOUSE_FILTER_STOP
		slot.gui_input.connect(func(ev): click_slot(ev, i))
		p.add_child(slot)
		if i >= S.inv.size():
			continue
		var e: Dictionary = S.inv[i]
		var tr := TextureRect.new()
		tr.texture = icon(e.id)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.position = Vector2(sw / 2.0 - ic / 2.0, maxf(4.0, (sh - fs - 10.0 - ic) / 2.0))
		tr.size = Vector2(ic, ic)
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		slot.add_child(tr)
		var nm := label(game.item(e.id).name, fs, INK)
		nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		nm.clip_text = true
		nm.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		nm.position = Vector2(4, sh - fs - 10.0)
		nm.size = Vector2(sw - 8, fs + 4)
		slot.add_child(nm)
		if int(e.get("n", 1)) > 1:
			var n := label("×%d" % int(e.n), fs + 2, TERRA, true)
			n.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			n.position = Vector2(sw - 60, 4)
			n.size = Vector2(52, fs + 6)
			slot.add_child(n)
		if S.worn.get("outfit") == e.id or S.worn.get("hat") == e.id:
			var badge := Panel.new()
			badge.add_theme_stylebox_override("panel", box_style(TERRA, TERRA, 0, 5))
			badge.position = Vector2(6, 6)
			badge.size = Vector2(fs * 3.2, fs + 6)
			slot.add_child(badge)
			var wl := label("worn", fs - 1, Color("#fbeede"))
			wl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			wl.size = badge.size
			badge.add_child(wl)
		if game.is_quest_item(e.id):
			var q := label("♦", fs + 2, GOLD)
			q.position = Vector2(sw - fs - 8, sh - fs - 12)
			slot.add_child(q)
	# the detail box
	var dy := gy + rows * (sh + gap) + 4.0
	var det := Panel.new()
	det.add_theme_stylebox_override("panel", box_style(Color(1, 0.98, 0.94, 0.8), Color(0.55, 0.31, 0.2, 0.3), 1, 10))
	det.position = Vector2(24, dy)
	det.size = Vector2(w - 48, dh)
	p.add_child(det)
	var foot := label(hint_of("Arrows choose · Enter uses · E eat · R read · W wear · I or Esc close", "Pad chooses · A uses · B closes"), 15, INK2)
	foot.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	foot.position = Vector2(0, p.size.y - 32)
	foot.size = Vector2(w, 20)
	p.add_child(foot)
	if sel >= S.inv.size():
		var empty := label("An empty pocket. Plenty of room for adventures.", 19, INK2)
		empty.position = Vector2(22, 20)
		det.add_child(empty)
		return
	var id: String = S.inv[sel].id
	var it: Dictionary = game.item(id)
	var books: Dictionary = game.data.get("BOOKS", {})
	var bi := minf(dh - 28.0, 120.0)
	var big := TextureRect.new()
	big.texture = icon(id)
	big.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	big.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	big.position = Vector2(16, (dh - bi) / 2.0)
	big.size = Vector2(bi, bi)
	det.add_child(big)
	var tx := bi + 36.0
	var tl := label(it.name + (" — " + books[id].author if books.has(id) and books[id] is Dictionary and books[id].has("author") else ""), 22, INK, true)
	tl.position = Vector2(tx, 12)
	det.add_child(tl)
	var dl := label(it.get("desc", ""), 18, INK2)
	dl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dl.position = Vector2(tx, 46)
	dl.size = Vector2(det.size.x - tx - 20, dh - 84)
	det.add_child(dl)
	var hint := ""
	match it.get("kind", ""):
		"note":
			hint = hint_of("♦ Press Enter to read it — this will be useful for the exam!", "♦ Press A to read it — this will be useful for the exam!")
		"food":
			hint = "♦ Someone is counting on this — not for eating yet" if game.is_quest_item(id) else hint_of("Enter (or E) to eat", "A to eat")
		"book":
			hint = hint_of("Enter (or R) to read", "A to read")
		"clothes":
			var on: bool = S.worn.get(it.get("slot", "outfit")) == id
			hint = hint_of("Enter (or W) to take off", "A to take off") if on else hint_of("Enter (or W) to wear", "A to wear")
		_:
			if id == "camera":
				hint = hint_of("Enter to take a photograph", "A to take a photograph")
			elif game.is_quest_item(id):
				hint = "♦ Quest item"
	var hl := label(hint, 17, TERRA)
	hl.position = Vector2(tx, dh - 34)
	det.add_child(hl)


func draw_journal() -> void:
	# as in the 2D game: page 1 the journal, page 2 the achievements in two columns. The entries grouped under
	# their missions, a dot point each (see below). Left and right turn the page, up and
	# down scroll, J or Esc closes.
	var S: Dictionary = game.S
	var ps := page_size()
	var w := ps.x
	var h := ps.y
	var p: Control
	var pages := journal_pages()
	journal_page = clampi(journal_page, 0, pages.size() - 1)
	var page_no := "Page %d of %d" % [journal_page + 1, pages.size()] if pages.size() > 1 else ""
	if pages[journal_page] == "notebook":
		# (round 37, the user: "She can just check it in the journal menu") her list, as in the book by her bed
		p = card(w, h, "SANDRA'S NOTEBOOK", page_no)
		var nclip := Control.new()
		nclip.clip_contents = true
		nclip.position = Vector2(14, 56)
		nclip.size = Vector2(w - 28, h - 56 - 46)
		p.add_child(nclip)
		var ncol := VBoxContainer.new()
		ncol.add_theme_constant_override("separation", 2)
		ncol.position = Vector2(20, 0)
		ncol.size = Vector2(nclip.size.x - 40, 0)
		nclip.add_child(ncol)
		# (round 37, the user: "make the text larger so it fills the screen without having to scroll") the size that
		# fills the page with all her lines
		var nlines: Array = game.notebook_lines()
		var fs := clampi(int((nclip.size.y - 30.0) / ((nlines.size() + 1.6) * 1.2)), 17, 30)
		var sub := label("Things I want to do in Barcelona (written on the train from Giessen)", fs, INK2)
		sub.add_theme_font_override("font", main.talk_font(400))
		ncol.add_child(sub)
		var ngap := Control.new()
		ngap.custom_minimum_size.y = 6
		ncol.add_child(ngap)
		for l in nlines:
			# (round 37, the user) plain until it starts, bold while it is going on, ticked and grey once done
			var nl := label(("☑  " if l[1] == 2 else "☐  ") + String(l[0]), fs, Color(0.5, 0.46, 0.42, 0.85) if l[1] == 2 else INK)
			var nf: Font = main.talk_font(400)
			if l[1] == 1:
				var fv := FontVariation.new()            # (the system font's weight 700 drew no bolder here)
				fv.base_font = nf
				fv.variation_embolden = 0.9
				nf = fv
			nl.add_theme_font_override("font", nf)
			nl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			nl.custom_minimum_size.x = nclip.size.x - 50
			ncol.add_child(nl)
		var ntotal: float = ncol.get_combined_minimum_size().y
		var nmax := maxf(0.0, ntotal - nclip.size.y + 10.0)
		journal_scroll = clampf(journal_scroll, 0.0, nmax)
		ncol.position.y = 6.0 - journal_scroll
		if nmax > 0.0:
			var nup := label("▲ ↑ scroll up" if journal_scroll > 0.0 else "", 13, INK2)
			nup.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			nup.position = Vector2(w - 240, 40)
			nup.size = Vector2(220, 16)
			p.add_child(nup)
			var ndn := label("▼ ↓ scroll down" if journal_scroll < nmax else "", 13, INK2)
			ndn.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			ndn.position = Vector2(w - 240, h - 50)
			ndn.size = Vector2(220, 16)
			p.add_child(ndn)
		journal_max = nmax
	elif pages[journal_page] == "journal":
		p = card(w, h, "SANDRA'S JOURNAL", page_no)
		var clip := Control.new()
		clip.clip_contents = true
		clip.position = Vector2(14, 56)
		clip.size = Vector2(w - 28, h - 56 - 46)
		p.add_child(clip)
		var col := VBoxContainer.new()
		col.add_theme_constant_override("separation", 4)
		col.position = Vector2(20, 0)
		col.size = Vector2(clip.size.x - 40, 0)
		clip.add_child(col)
		var now: String = game.current_mission()
		var grey := Color(0.5, 0.46, 0.42, 0.75)
		# the groups (round 22, the user's wish): each mission under its name, in the order they were taken up, the
		# finished ones at the bottom;
		# its steps one under another, the ones already behind her greyed, the one she is on in ink; once the whole
		# mission is done, its name and its last line grey too. Then the study notes.
		var groups := {}
		var keys := {}
		var order := []
		for e in S.log:
			var k: String = game.log_key(e)
			var key: String = String(game.mission_title(k)) if k != "" else String(e.t)
			if key.begins_with("Study Notes"):
				key = "Study notes"
			if not groups.has(key):
				groups[key] = []
				keys[key] = k
				order.append(key)
			groups[key].append(String(e.x))
		# (round 37, the user: "could the order of the things be the order in which you trigger them?": finished
		# missions stay in their place; before, they went to the bottom)
		if order.is_empty():
			col.add_child(label("Nothing written yet.", 18, INK2))
		var top_of_now := 0.0
		for key in order:
			var k: String = keys[key]
			var done: bool = k != "" and game.m_done(k)
			if k != "" and k == now:
				top_of_now = col.get_combined_minimum_size().y
			var head := label(key + ("   ✓" if done else ""), 19, grey if done else INK, true)
			if col.get_child_count() > 0:
				var gap := Control.new()
				gap.custom_minimum_size.y = 8
				col.add_child(gap)
			col.add_child(head)
			var lines: Array = groups[key]
			for i in lines.size():
				var last: bool = i == lines.size() - 1
				var b := label("•  " + String(lines[i]), 17, INK if (last and not done) or k == "" else grey)
				b.add_theme_font_override("font", main.talk_font(400))     # (lighter than the panels' own font)
				b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				b.custom_minimum_size.x = clip.size.x - 60
				var m := MarginContainer.new()
				m.add_theme_constant_override("margin_left", 14)
				m.add_child(b)
				col.add_child(m)
		var total: float = col.get_combined_minimum_size().y
		var max_scroll := maxf(0.0, total - clip.size.y + 10.0)
		if journal_scroll < 0.0:
			journal_scroll = top_of_now - 6.0 if now != "" else max_scroll
		journal_scroll = clampf(journal_scroll, 0.0, max_scroll)
		col.position.y = 6.0 - journal_scroll
		if max_scroll > 0.0:
			var up := label("▲ ↑ scroll up" if journal_scroll > 0.0 else "", 13, INK2)
			up.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			up.position = Vector2(w - 240, 40)
			up.size = Vector2(220, 16)
			p.add_child(up)
			var dn := label("▼ ↓ scroll down" if journal_scroll < max_scroll else "", 13, INK2)
			dn.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			dn.position = Vector2(w - 240, h - 50)
			dn.size = Vector2(220, 16)
			p.add_child(dn)
		journal_max = max_scroll
	else:
		var earned: Array = game.data.ACHIEVEMENTS.filter(func(a): return game.ach_earned(a.id))
		p = card(w, h, "ACHIEVEMENTS  %d/%d" % [earned.size(), game.data.ACHIEVEMENTS.size()], page_no)
		if earned.is_empty():
			var none := label("Your achievements will appear here as you earn them.", 19, INK2)
			none.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			none.position = Vector2(0, h / 2.0 - 12)
			none.size = Vector2(w, 24)
			p.add_child(none)
		var ncol := 2 if w >= 680 else 1
		var per := int(ceil(game.data.ACHIEVEMENTS.size() / float(ncol)))
		var top := 60.0
		var row_h := clampf((h - top - 46.0) / per, 40.0, 64.0)
		var col_w := (w - 40.0) / ncol
		for i in earned.size():
			var a: Dictionary = earned[i]
			var ax := 20.0 + (i / per) * col_w
			var ay := top + (i % per) * row_h
			var bg := Panel.new()
			bg.add_theme_stylebox_override("panel", box_style(Color(0.88, 0.66, 0.23, 0.14), Color(0, 0, 0, 0), 0, 8))
			bg.position = Vector2(ax, ay)
			bg.size = Vector2(col_w - 16, row_h - 6)
			p.add_child(bg)
			var star := Panel.new()
			star.add_theme_stylebox_override("panel", box_style(GOLD, GOLD, 0, 64))
			star.position = Vector2(8, (row_h - 6) / 2.0 - 14)
			star.size = Vector2(28, 28)
			bg.add_child(star)
			var sl := label("★", 16, Color("#fff8e0"), true)
			sl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			sl.size = Vector2(28, 28)
			star.add_child(sl)
			var at := label(String(a.title), 17, INK, true)
			at.position = Vector2(46, 4)
			at.clip_text = true
			at.size = Vector2(col_w - 70, 22)
			bg.add_child(at)
			var ad := label(String(a.desc), 14, INK2)
			ad.position = Vector2(46, 26)
			ad.clip_text = true
			ad.size = Vector2(col_w - 70, 18)
			ad.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
			bg.add_child(ad)
	# the neighbouring pages either side ("◀ NOTEBOOK", "JOURNAL ▶"), then scrolling and closing
	var turn := []
	if journal_page > 0:
		turn.append("◀ " + String(pages[journal_page - 1]).to_upper())
	if journal_page < pages.size() - 1:
		turn.append(String(pages[journal_page + 1]).to_upper() + " ▶")
	var tail: String = hint_of("↑ ↓ scroll · J or Esc to close", "▲ ▼ scroll · B to close") if journal_max > 0.0 \
		else hint_of("J or Esc to close", "B to close")
	var foot := label(("   ".join(PackedStringArray(turn)) + "   ·   " if not turn.is_empty() else "") + tail, 15, INK2)
	foot.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	foot.position = Vector2(0, h - 32)
	foot.size = Vector2(w, 20)
	p.add_child(foot)


func draw_reader() -> void:
	# a cream page, its title and author at the top, the text in a book face, the page number at the bottom
	var vp0: Vector2 = main.play_area()
	var w := minf(820.0, vp0.x - 80)
	var h := minf(620.0, vp0.y - 60)
	var p := card(w, h, "", "")
	var sb := box_style(Color("#fbf4e2"), Color(0.55, 0.36, 0.2, 0.5), 2, 6)
	sb.shadow_color = Color(0.12, 0.06, 0.04, 0.5)
	sb.shadow_size = 24
	p.add_theme_stylebox_override("panel", sb)
	var t := label(String(reader.title), 18, TERRA_D, true)
	t.position = Vector2(36, 24)
	t.clip_text = true
	t.size = Vector2(w * 0.55 - 36, 24)
	p.add_child(t)
	var a := label(String(reader.author), 16, INK2)
	a.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	a.position = Vector2(w * 0.55, 26)
	a.clip_text = true
	a.size = Vector2(w * 0.45 - 36, 22)
	p.add_child(a)
	var rule := ColorRect.new()
	rule.color = Color(0.72, 0.35, 0.23, 0.3)
	rule.position = Vector2(36, 56)
	rule.size = Vector2(w - 72, 1)
	p.add_child(rule)
	var f := SystemFont.new()
	f.font_names = PackedStringArray(["Georgia", "Times New Roman"])
	var body := label(String(reader.pages[reader.page]), 20, INK)
	body.add_theme_font_override("font", f)
	body.add_theme_constant_override("line_spacing", 6)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.position = Vector2(36, 76)
	body.size = Vector2(w - 72, h - 140)
	p.add_child(body)
	var pg := label("Page %d/%d" % [reader.page + 1, reader.pages.size()], 15, INK2)
	pg.position = Vector2(36, h - 40)
	p.add_child(pg)
	var hint := label(hint_of("Space or → next page · ← back · Esc close", "▶ next page · ◀ back · B close"), 15, INK2)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	hint.position = Vector2(w - 436, h - 40)
	hint.size = Vector2(400, 20)
	p.add_child(hint)


func list_pane(p: Control, x: float, y: float, w: float, rows: int, list: Array, chosen: int, active: bool, title: String, mark := Callable()) -> void:
	# the 2D game's list: a heading, then a row a thing (its picture, name, ×count, and a note on the right)
	var hd := label(title, 18, TERRA_D if active else INK2, true)
	hd.position = Vector2(x + 8, y - 30)
	p.add_child(hd)
	var bg := Panel.new()
	bg.add_theme_stylebox_override("panel", box_style(Color(0.88, 0.66, 0.23, 0.1) if active else Color(0.47, 0.31, 0.2, 0.06), Color(0, 0, 0, 0), 0, 8))
	bg.position = Vector2(x, y)
	bg.size = Vector2(w, rows * 36 + 10)
	p.add_child(bg)
	var first := clampi(chosen - rows / 2, 0, maxi(0, list.size() - rows))
	if list.is_empty():
		var em := label("(empty)", 16, INK2)
		em.position = Vector2(x + 14, y + 12)
		p.add_child(em)
	for r in mini(rows, list.size() - first):
		var i := first + r
		var e: Dictionary = list[i]
		var yy := y + 5 + r * 36
		if active and i == chosen:
			var hl := Panel.new()
			hl.add_theme_stylebox_override("panel", box_style(Color(0.88, 0.66, 0.23, 0.35), GOLD, 2, 7))
			hl.position = Vector2(x + 4, yy)
			hl.size = Vector2(w - 8, 34)
			p.add_child(hl)
		var tr := TextureRect.new()
		tr.texture = icon(e.id)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.position = Vector2(x + 10, yy + 3)
		tr.size = Vector2(28, 28)
		p.add_child(tr)
		var mk: String = mark.call(e.id) if mark.is_valid() else ""
		var nm := label(game.item(e.id).name + (" ×%d" % int(e.n) if int(e.get("n", 1)) > 1 else ""), 17, INK, active and i == chosen)
		nm.position = Vector2(x + 46, yy + 5)
		# (round 35, the everything-visit: book titles were cut off mid-word — "…Adam Smi" — 100 px short of the row's end
		# with nothing there; the whole row now unless a mark stands at its end, and a … where it must stop)
		nm.clip_text = true
		nm.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		nm.size = Vector2(w - (160 if mk != "" else 56), 24)
		p.add_child(nm)
		if mk != "":
			var ml := label(mk, 14, TERRA)
			ml.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			ml.position = Vector2(x + w - 150, yy + 7)
			ml.size = Vector2(140, 20)
			p.add_child(ml)


func draw_container() -> void:
	var C: Dictionary = game.data.CONTAINERS[cid]
	var vp0: Vector2 = main.play_area()
	var lib: bool = C.kind == "library"
	var p := card(minf(1000.0, vp0.x - 60), minf(640.0, vp0.y - 60), String(C.get("label", C.name)),
		"Read here — no book leaves this floor" if lib else "")
	var w: float = p.size.x
	var h: float = p.size.y
	var pw := floorf((w - 72.0) / 2.0)
	var rows := clampi(int((h - 92.0 - 120.0) / 36.0), 5, 12)
	var lists: Array = [game.S.cont[cid], game.S.inv]
	sel = clampi(sel, 0, maxi(0, lists[col].size() - 1))
	var worn := func(id): return "worn" if game.S.worn.get("outfit") == id or game.S.worn.get("hat") == id else ""
	list_pane(p, 24, 92, pw, rows, lists[0], sel if col == 0 else -1, col == 0, String(C.name))
	list_pane(p, w - 24 - pw, 92, pw, rows, lists[1], sel if col == 1 else -1, col == 1, "Backpack (%d/%d)" % [game.S.inv.size(), game.MAX_SLOTS], worn)
	var dy := 92.0 + rows * 36 + 22
	if sel < lists[col].size():
		var d := label(game.item(lists[col][sel].id).get("desc", ""), 16, INK2)
		d.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		d.position = Vector2(26, dy)
		d.size = Vector2(w - 52, 46)
		p.add_child(d)
	var foot := label(hint_of("← → switch side · ↑ ↓ choose · Enter %s · R read · Esc close", "◀ ▶ switch side · ▲ ▼ choose · A %s · B close") % ("take" if col == 0 else "put"), 15, INK2)
	foot.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	foot.position = Vector2(0, h - 32)
	foot.size = Vector2(w, 20)
	p.add_child(foot)


func draw_bin() -> void:
	var vp0: Vector2 = main.play_area()
	var rows := clampi(int((vp0.y - 260.0) / 36.0), 5, 12)
	var p := card(560, 92 + rows * 36 + 70, "Public rubbish bin", "Keep Barcelona tidy")
	sel = clampi(sel, 0, maxi(0, game.S.inv.size() - 1))
	var mark := func(id):
		if game.is_book(id) or game.is_clothes(id):
			return "(too precious)"
		if game.is_quest_item(id):
			return "(needed)"
		return "(keep)" if game.item(id).get("kind", "") == "tool" else ""
	list_pane(p, 24, 92, p.size.x - 48, rows, game.S.inv, sel, true, "Backpack", mark)
	var foot := label(hint_of("Enter throw away · Esc close", "A throw away · B close"), 15, INK2)
	foot.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	foot.position = Vector2(0, p.size.y - 32)
	foot.size = Vector2(p.size.x, 20)
	p.add_child(foot)


func after_message(reopen: Callable) -> void:
	# a thing that answers back (the librarian, a refusal): let it speak, then come back to the panel
	if not game.q.is_empty():
		close(false)
		game.after(reopen)
	else:
		redraw()


func draw_shop() -> void:
	var sh: Dictionary = game.data.SHOPS[shop_id]
	var stock: Array = game.shop_stock(shop_id)
	var n := maxi(1, stock.size())
	var row_h := 40.0
	var p := card(520, 136 + n * row_h, sh.title, hint_of("Esc to leave", "B to leave"))
	var w: float = p.size.x
	var sub := label("New and second-hand books, sold (never bought)." if sh.get("unique", false) else "What would you like?", 14, INK2)
	sub.position = Vector2(24, 48)
	p.add_child(sub)
	var rule := ColorRect.new()
	rule.color = Color(0.72, 0.35, 0.23, 0.3)
	rule.position = Vector2(20, 76)
	rule.size = Vector2(w - 40, 1)
	p.add_child(rule)
	var ly := 88.0
	if stock.is_empty():
		var so := label("Sold out — and the shopkeeper looks delighted about it.", 14, INK2)
		so.position = Vector2(30, ly + 6)
		p.add_child(so)
	sel = clampi(sel, 0, maxi(0, stock.size() - 1))
	for i in stock.size():
		var id: String = stock[i][0]
		var price: int = stock[i][1]
		var row := Panel.new()
		var chosen: bool = i == sel
		row.add_theme_stylebox_override("panel", box_style(Color(0.88, 0.66, 0.23, 0.3) if chosen else Color(0, 0, 0, 0),
			Color(0, 0, 0, 0), 0, 7))
		row.position = Vector2(16, ly + i * row_h)
		row.size = Vector2(w - 32, row_h - 4)
		row.mouse_filter = Control.MOUSE_FILTER_STOP
		row.gui_input.connect(func(ev): click_row(ev, i))
		p.add_child(row)
		var tr := TextureRect.new()
		tr.texture = icon(id)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.position = Vector2(10, 3)
		tr.size = Vector2(row_h - 10, row_h - 10)
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(tr)
		var nm := label(game.item(id).name, 16, INK, chosen)
		nm.position = Vector2(50, 7)
		# (round 35, the everything-visit: a long title ran on under its price; clipped first, or the size is held to the
		# whole title's width)
		nm.clip_text = true
		nm.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		nm.size = Vector2(w - 32 - 50 - 110, 22)
		row.add_child(nm)
		var pr := label(game.money(price), 16, TERRA_D if price > 500 else INK, true)
		pr.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		pr.position = Vector2(w - 32 - 130, 7)
		pr.size = Vector2(116, 22)
		row.add_child(pr)
	var fy := ly + n * row_h + 14.0
	var purse := label("Your purse: %s" % game.money(game.S.money), 14, INK2)
	purse.position = Vector2(24, fy)
	p.add_child(purse)
	var foot := label(hint_of("Enter buys · Esc leaves", "A buys · B leaves"), 13, INK2)
	foot.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	foot.position = Vector2(w - 224, fy)
	foot.size = Vector2(200, 18)
	p.add_child(foot)


func debug_list() -> Array:
	# what the debug page offers: [label, what it does]
	var rows := []
	match debug_page:
		"main":
			rows.append(["Go to a place…", func(): open_debug("go")])
			rows.append(["Set the time…", func(): open_debug("time")])
			rows.append(["+ €50", func(): debug_money(5000)])
			rows.append(["+ €500", func(): debug_money(50000)])
			rows.append(["Get the bicycle" + (("  (she has it: %s to ride)" % main.bike_word()) if game.S.get("has_bike", false) else ""), func():
				game.S.has_bike = true
				game.toast("The bicycle is yours: %s to hop on" % main.bike_word())])
			if game.data.ITEMS.has("park_pass"):
				# (round 26, the user: "Put the park and lift pass into the debug screen") the Amic del Park card: Park
				# Güell's gates and the funicular's turnstile
				rows.append(["Get the park & funicular pass" + ("  (she has it)" if game.has_item("park_pass") else ""), func():
					if not game.has_item("park_pass") and game.add_item("park_pass"):
						game.toast("The Amic del Park card: Park Güell's gates and the funicular")
					game.S.flags["parkTicket"] = true          # (round 38: the park's ticket is a status, 06 #97)
					if main.get("north") != null and main.north.has_method("refresh"):
						main.north.refresh()
					redraw()])
			rows.append(["Next time of day  (T)", func():
				close(false)
				main.next_time_stop()])
			rows.append(["Change Sandra's outfit  (C)", func():
				main.show_skin(main.skin_idx + 1)
				redraw()])
			rows.append(["Music on / off  (N)", func():
				main.toggle_music()
				redraw()])
			rows.append(["Quality: " + ("high" if main.high_quality else "balanced") + "  (Q)", func():
				main.set_quality(not main.high_quality)
				redraw()])
			rows.append(["Bounce light: " + ("on" if main.env_out.sdfgi_enabled else "off") + "  (G)", func():
				main.env_out.sdfgi_enabled = not main.env_out.sdfgi_enabled
				redraw()])
			rows.append(["Light shafts: " + ("on" if main.env_out.volumetric_fog_enabled else "off") + "  (V)", func():
				main.env_out.volumetric_fog_enabled = not main.env_out.volumetric_fog_enabled
				redraw()])
			rows.append(["Quick walking: " + ("on" if main.debug_fast else "off"), func():
				main.debug_fast = not main.debug_fast
				redraw()])
			rows.append(["Touch controls: " + ("on" if main.touch_pad else "off") + "  (the mouse is a finger)", func():
				main.set_touch(main.touch_pad == null)
				redraw()])
			rows.append(["Close", func(): close()])
		"go":
			for pl in main.debug_places():
				var place: Dictionary = pl
				rows.append([place.name, func():
					close(false)
					main.teleport(place.pos, place.facing)])
		"time":
			for tm in [[390, "06:30  sunrise"], [480, "08:00  morning"], [720, "12:00  midday"], [1140, "19:00  evening"],
					[1260, "21:00  golden hour"], [1290, "21:30  sunset"], [1335, "22:15  night"], [120, "02:00  deep night"]]:
				var mm: int = tm[0]
				rows.append([tm[1], func():
					main.set_clock(mm)
					close(false)])
	return rows


func debug_money(c: int) -> void:
	game.S.money += c
	main.ambience.sfx("coin")
	redraw()


func draw_debug() -> void:
	debug_rows = debug_list()
	var titles := {"main": "DEBUG", "go": "GO TO A PLACE", "time": "SET THE TIME"}
	var shown := mini(debug_rows.size(), 12)
	var row_h := 34.0
	var p := card(460, 96 + shown * row_h + 30, titles[debug_page], hint_of("Esc back", "B back") if debug_page != "main" else hint_of("Esc closes", "B closes"))
	var w: float = p.size.x
	sel = clampi(sel, 0, debug_rows.size() - 1)
	var first := clampi(sel - shown / 2, 0, maxi(0, debug_rows.size() - shown))
	var ly := 60.0
	for j in shown:
		var i := first + j
		var chosen: bool = i == sel
		var row := Panel.new()
		row.add_theme_stylebox_override("panel", box_style(Color(0.88, 0.66, 0.23, 0.3) if chosen else Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 7))
		row.position = Vector2(16, ly + j * row_h)
		row.size = Vector2(w - 32, row_h - 4)
		p.add_child(row)
		var nm := label(debug_rows[i][0], 16, INK, chosen)
		nm.position = Vector2(14, 4)
		row.add_child(nm)
	var foot := label(hint_of("↑↓ choose · Enter · %d/%d", "▲▼ choose · A · %d/%d") % [sel + 1, debug_rows.size()], 13, INK2)
	foot.position = Vector2(24, ly + shown * row_h + 8)
	p.add_child(foot)


# ------------------------------------------------------------------ input (main.gd passes keys here while a panel is open)

func key(code: int) -> void:
	if kind == "bag":
		match code:
			KEY_LEFT, KEY_A:
				move(-1)
			KEY_RIGHT, KEY_D:
				move(1)
			KEY_UP:
				move(-cols)
			KEY_DOWN, KEY_S:
				move(cols)
			KEY_ENTER, KEY_KP_ENTER, KEY_SPACE:
				use_selected("")
			KEY_E:
				use_selected("eat")
			KEY_R:
				use_selected("read")
			KEY_W:
				use_selected("wear")
			KEY_I, KEY_ESCAPE, KEY_BACKSPACE:
				close()
	elif kind == "shop":
		var n: int = game.shop_stock(shop_id).size()
		match code:
			KEY_UP, KEY_W:
				if n > 0:
					sel = wrapi(sel - 1, 0, n)
					main.ambience.sfx("tick")
					redraw()
			KEY_DOWN, KEY_S:
				if n > 0:
					sel = wrapi(sel + 1, 0, n)
					main.ambience.sfx("tick")
					redraw()
			KEY_ENTER, KEY_KP_ENTER, KEY_E:
				buy_selected()
			KEY_ESCAPE, KEY_SPACE, KEY_BACKSPACE:
				close()
	elif kind == "reader":
		match code:
			KEY_SPACE, KEY_RIGHT, KEY_DOWN, KEY_ENTER, KEY_KP_ENTER, KEY_E, KEY_D, KEY_S:
				if reader.page < reader.pages.size() - 1:
					reader.page += 1
					main.ambience.sfx("page")
					redraw()
				elif code in [KEY_SPACE, KEY_ENTER, KEY_KP_ENTER, KEY_E]:
					close_reader()
			KEY_LEFT, KEY_UP, KEY_A, KEY_W:
				if reader.page > 0:
					reader.page -= 1
					main.ambience.sfx("page")
					redraw()
			KEY_ESCAPE, KEY_BACKSPACE:
				close_reader()
	elif kind == "container":
		var lists: Array = [game.S.cont[cid], game.S.inv]
		match code:
			KEY_LEFT, KEY_RIGHT, KEY_A, KEY_D:
				col = 0 if code in [KEY_LEFT, KEY_A] else 1
				sel = mini(sel, maxi(0, lists[col].size() - 1))
				main.ambience.sfx("tick")
				redraw()
			KEY_UP, KEY_W:
				sel = maxi(0, sel - 1)
				redraw()
			KEY_DOWN, KEY_S:
				sel = mini(maxi(0, lists[col].size() - 1), sel + 1)
				redraw()
			KEY_ENTER, KEY_KP_ENTER, KEY_E, KEY_SPACE:
				if sel < lists[col].size():
					var id: String = lists[col][sel].id
					var here := cid
					if col == 0:
						game.move_to_bag(cid, id)
					else:
						game.move_to_container(cid, id)
					main.ambience.sfx("pick" if col == 0 else "drop")
					after_message(func(): open_container(here))
			KEY_R:
				if sel < lists[col].size() and game.item(lists[col][sel].id).get("kind", "") in ["book", "note"]:
					var id2: String = lists[col][sel].id
					var here2 := cid
					var c2 := col
					var s2 := sel
					close(false)
					game.open_reader(id2, func():
						open_container(here2)
						col = c2
						sel = s2
						redraw())
			KEY_ESCAPE, KEY_BACKSPACE:
				close()
	elif kind == "bin":
		match code:
			KEY_UP, KEY_W:
				sel = maxi(0, sel - 1)
				redraw()
			KEY_DOWN, KEY_S:
				sel = mini(maxi(0, game.S.inv.size() - 1), sel + 1)
				redraw()
			KEY_ENTER, KEY_KP_ENTER, KEY_E, KEY_SPACE:
				if sel < game.S.inv.size():
					var s3 := sel
					game.bin_item(game.S.inv[sel].id)
					after_message(func():
						open_bin()
						sel = s3
						redraw())
			KEY_ESCAPE, KEY_BACKSPACE:
				close()
	elif kind == "journal":
		match code:
			KEY_LEFT, KEY_RIGHT, KEY_A, KEY_D:
				var to := journal_page + (-1 if code in [KEY_LEFT, KEY_A] else 1)
				if to < 0 or to >= journal_pages().size():
					return
				journal_page = to
				journal_scroll = -1.0 if journal_pages()[to] == "journal" else 0.0
				main.ambience.sfx("page")
				redraw()
			KEY_UP, KEY_W:
				journal_scroll = maxf(0.0, minf(journal_scroll, journal_max) - 80.0)
				redraw()
			KEY_DOWN, KEY_S:
				journal_scroll = minf(journal_max, journal_scroll + 80.0)
				redraw()
			KEY_J, KEY_ESCAPE, KEY_BACKSPACE, KEY_SPACE, KEY_ENTER, KEY_KP_ENTER, KEY_E:
				close()
	elif kind == "debug":
		var n := debug_rows.size()
		match code:
			KEY_UP, KEY_W:
				sel = wrapi(sel - 1, 0, n)
				main.ambience.sfx("tick")
				redraw()
			KEY_DOWN, KEY_S:
				sel = wrapi(sel + 1, 0, n)
				main.ambience.sfx("tick")
				redraw()
			KEY_ENTER, KEY_KP_ENTER, KEY_E:
				if n > 0:
					debug_rows[sel][1].call()
			KEY_ESCAPE, KEY_BACKSPACE, KEY_P:
				if debug_page != "main" and code != KEY_P:
					open_debug("main")
				else:
					close()


func close_reader() -> void:
	var back: Callable = reader.get("back", Callable())
	close()
	if back.is_valid():
		back.call()


func move(d: int) -> void:
	sel = wrapi(sel + d, 0, game.MAX_SLOTS)
	main.ambience.sfx("tick")
	redraw()


func click_slot(ev: InputEvent, i: int) -> void:
	if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		if ev.double_click and i == sel:
			use_selected("")
		else:
			sel = i
			main.ambience.sfx("tick")
			redraw.call_deferred()


func click_row(ev: InputEvent, i: int) -> void:
	if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		if i == sel:
			buy_selected()
		else:
			sel = i
			main.ambience.sfx("tick")
			redraw.call_deferred()


func buy_selected() -> void:
	var stock: Array = game.shop_stock(shop_id)
	if stock.is_empty():
		return
	var e: Array = stock[clampi(sel, 0, stock.size() - 1)]
	var before: int = game.S.money
	game.buy_item(shop_id, e[0], e[1])
	if game.S.money == before:
		main.ambience.sfx("nope")
	if not game.q.is_empty():
		# the shopkeeper has something to say (not enough money for the birthday torró): let them say it
		close(false)
		game.after(func(): open_shop(shop_id))
		return
	redraw()


func use_selected(how: String) -> void:
	var S: Dictionary = game.S
	if sel >= S.inv.size():
		return
	var id: String = S.inv[sel].id
	var it: Dictionary = game.item(id)
	var k: String = it.get("kind", "")
	if how == "":
		how = {"food": "eat", "book": "read", "note": "read", "clothes": "wear"}.get(k, "photo" if id == "camera" else "")
	var back := sel
	match how:
		"eat":
			if k != "food":
				return
			close(false)
			game.eat_item(id)
			game.after(func(): open_bag(back))
		"read":
			if k != "book" and k != "note":
				return
			close(false)
			game.open_reader(id, func(): open_bag(back))
		"wear":
			if k != "clothes":
				return
			game.wear_item(id)
			redraw()
		"photo":
			if main.street.riding != null:              # (round 41, rule 10: on the bike, said over the open backpack)
				main.toast("Get off the bike first to take a photo")
				main.ambience.sfx("nope")
				return
			close(false)
			game.photo_prompt()
