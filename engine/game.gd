# The game itself, ported from the 2D game's GAME section (its data is from2d/data2d.json):
#   state       money, the backpack (20 slots), what's in every cupboard and shelf, missions and their
#               journal, flags, the clock, who has been talked to, what has been taken
#   missions    Getting home, the birthday gift, the eleven favours people ask once the party's over,
#               and the final exam; who gives them, what finishes them, the rewards, the study notes
#   people      what everyone says: their introduction, mission talk, their lines in turn, the Pfand
#               tip, shopkeepers' shops, Manolo the pickpocket and Agent Bofarull, bulk sales
#   things      bottles, shells and coins on the ground, wildflowers on the grass, the mission items,
#               bins (and their lucky finds), cupboards and shelves, the phone, Sandra's bed, the card
#   panels      the backpack, shops, cupboards, reading books and notes, the journal
# Dialogue goes through a queue (say / ask / after), like the 2D game's UI queue, so a conversation
# can run several pages and choices in order and then do something.
# The game is saved to user://save.json now and then, and loaded at start.
extends Node

const MAX_SLOTS := 20
# (the test runs keep their own save, so they never touch the player's game)
var SAVE_PATH := "user://test_save.json" if Array(OS.get_cmdline_user_args()).filter(func(a): return a != "--touch").size() > 0 else "user://save.json"
const T := 3.3
const OX := 55
const OY := 45

# a few lines the 2D game keeps outside its data
const BIN_REFUSE_BOOK := "Throw away a BOOK? In Barcelona? Sant Jordi would rise from the dead, dragon and all. Books go back on bookshelves."
const BIN_REFUSE_CLOTHES := "These clothes need a wash, not a funeral. They belong back in a cupboard."
const BIN_REFUSE_QUEST := "Better not — someone is counting on this."
const LIB_FLAVOR := "The library shelves hold the hush of somebody else's deadline. Somewhere, a pencil is being chewed."
const SHELF_STANDARDS := "Only books go on a bookshelf. This shelf has standards."
const CUPBOARD_NO_BOOKS := "Books don't belong shut in a cupboard — they belong upright, spine out, dignified. Put it on a bookshelf."
const VASE_EMPTY := "An empty glass vase on Alba's table. It has the patient look of something that has been waiting for flowers its whole life."
const VASE_FULL := "Alba's vase, overflowing with orange wildflowers. It looks, finally, like it knows what it was for."

var main: Node3D
var data: Dictionary
var S: Dictionary = {}
var q: Array = []                # the dialogue queue
var ground: Array = []           # ground items: {key, id, pos (Vector3), mission, node}
var save_t := 0.0
var rng := RandomNumberGenerator.new()
var fresh := false


func setup(m: Node3D, d: Dictionary) -> void:
	main = m
	data = d
	rng.randomize()
	if not load_game():
		S = default_state()
	build_ground()


func default_state() -> Dictionary:
	var cont := {}
	for k in data.CONTAINERS:
		cont[k] = []
		for id in data.CONTAINERS[k].items:
			cont[k].append({"id": id, "n": 1})
	return {"money": 0, "inv": [], "worn": {"outfit": null, "hat": null}, "cont": cont,
		"missions": {"home": {"st": "active", "num": 1}}, "counter": 3, "focus": "home", "log": [],
		"flags": {}, "talk": {}, "intro": {}, "taken": {}, "exits": 0, "plaques": {}, "shelf_seen": {},
		"bottles_returned": 0, "binned": 0, "bin_msg": 0, "eaten": {}, "stolen": [], "pending": null,
		"ach_seen": {}, "has_bike": false, "time": 6 * 60 + 40, "bin_cd": {}, "sold": {}, "trufa": "lost",
		"play_time": 0.0, "new": true}


# ------------------------------------------------------------------ saving

func save_game(exact := false) -> void:
	# (round 38, the user: "when you go continue game, it starts again from the beach. It should start from wherever she
	# was") where she is goes in the save too: main.gd save_spot / restore_spot (round 40: the autosave keeps the place of
	# her last interaction; `exact`, Export save, where she stands)
	if main.has_method("save_spot"):
		var at: Dictionary = main.save_spot(exact)
		if not at.is_empty():
			S.at = at
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f:
		S.new = false
		f.store_string(JSON.stringify(S))


func load_game() -> bool:
	if Engine.has_meta("fresh_start"):
		Engine.remove_meta("fresh_start")
		fresh = true                                        # (straight to the beach, no title)
		return false
	if "--new" in OS.get_cmdline_user_args() or not FileAccess.file_exists(SAVE_PATH):
		return false
	var v = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if not v is Dictionary:
		return false
	S = default_state()
	for k in v:
		S[k] = v[k]
	for k in S.missions.keys():
		if not data.MISSIONS.has(k):
			S.missions.erase(k)                       # (round 22: Laia's balloon became Biel's ball)
	S.inv = S.inv.filter(func(e): return data.ITEMS.has(e.id))
	return true


# ------------------------------------------------------------------ the dialogue queue

func say(who: String, text: String) -> void:
	q.append({"k": "page", "who": who, "t": text})
	pump.call_deferred()


func ask(who: String, text: String, options: Array, cancel := Callable()) -> void:
	# options: [{"label": String, "fn": Callable}]
	q.append({"k": "ask", "who": who, "t": text, "opts": options, "cancel": cancel})
	pump.call_deferred()


func after(fn: Callable) -> void:
	q.append({"k": "fn", "fn": fn})
	pump.call_deferred()


func pump() -> void:
	while not q.is_empty() and not main.dlg_open:
		var e: Dictionary = q.pop_front()
		match e.k:
			"fn":
				e.fn.call()
			"page":
				main.show_dialog(e.who, [e.t], [], Callable(), pump)
				return
			"ask":
				var labels := []
				for o in e.opts:
					labels.append(o.label)
				var opts: Array = e.opts
				var cancel: Callable = e.cancel
				main.show_dialog(e.who, [e.t], labels, func(i: int):
					opts[i].fn.call()
					pump(), func():
					if cancel.is_valid():
						cancel.call()
					pump())
				return


func toast(text: String, secs := 2.4) -> void:
	main.toast(text, secs)


# ------------------------------------------------------------------ items

func item(id: String) -> Dictionary:
	return data.ITEMS.get(id, {"name": id, "kind": "misc", "desc": ""})


func stackable(id: String) -> bool:
	var k: String = item(id).get("kind", "")
	return k == "food" or k == "collect" or id == "rye"


func count_item(id: String) -> int:
	var n := 0
	for e in S.inv:
		if e.id == id:
			n += int(e.n)
	return n


func has_item(id: String) -> bool:
	return count_item(id) > 0


func can_add(id: String) -> bool:
	return (stackable(id) and has_item(id)) or S.inv.size() < MAX_SLOTS


func add_item(id: String, n := 1) -> bool:
	if not data.ITEMS.has(id):
		return false
	if stackable(id):
		for e in S.inv:
			if e.id == id:
				e.n += n
				return true
	if S.inv.size() >= MAX_SLOTS:
		return false
	if stackable(id):
		S.inv.append({"id": id, "n": n})
	else:
		for i in n:
			if S.inv.size() >= MAX_SLOTS:
				return false
			S.inv.append({"id": id, "n": 1})
	return true


func remove_item(id: String, n := 1) -> bool:
	for i in range(S.inv.size() - 1, -1, -1):
		if n <= 0:
			break
		var e: Dictionary = S.inv[i]
		if e.id != id:
			continue
		var k := mini(n, int(e.n))
		e.n -= k
		n -= k
		if e.n <= 0:
			S.inv.remove_at(i)
	if S.worn.outfit and not has_item(S.worn.outfit):
		S.worn.outfit = null
	if S.worn.hat and not has_item(S.worn.hat):
		S.worn.hat = null
	return n == 0


func money(c: int) -> String:
	return "€%.2f" % (c / 100.0)


func is_book(id: String) -> bool:
	return item(id).get("kind", "") == "book"


func is_clothes(id: String) -> bool:
	return item(id).get("kind", "") == "clothes"


func m_active(k: String) -> bool:
	return S.missions.has(k) and S.missions[k].st == "active"


func m_done(k: String) -> bool:
	return S.missions.has(k) and S.missions[k].st == "done"


func is_quest_item(id: String) -> bool:
	var it := item(id)
	if it.get("kind", "") == "note" or id == "diploma":
		return true
	match id:
		"torro_joan": return m_active("gift")
		"torro_mar": return m_active("gift") or m_active("rivalry")
		"crema": return m_active("crema")
		"rye": return m_active("flour")
		"bike_chain": return m_active("bike")
		"brush": return m_active("brush")
		"ball": return m_active("ball")
		"spirit_level": return m_active("level")
		"cellar_key", "salamandreta": return m_active("guell")
		"park_pass": return true                  # (round 40, the user: "the ticket is obviously a quest item and can never be disposed of")
		"textbook": return m_active("profbook")
		"cap": return m_active("hat")
		"camera_marta": return m_active("camera")
		"bk_ghost": return m_active("grail")
		"flower": return m_active("grail") and not S.flags.get("albaTraded", false)
	return it.get("kind", "") == "quest"


# ------------------------------------------------------------------ missions

func mission_title(k: String) -> String:
	# (round 22: the mission's name alone, "Find Montse's lost dog"; it was "Mission 3 — The lost dog")
	return data.MISSIONS[k].name


func log_key(e: Dictionary) -> String:
	# which mission a journal entry belongs to ("" for the study notes): entries since round 22 carry it, older
	# ones only their title, "Mission 3 — The lost dog"
	if e.has("k"):
		return String(e.k)
	var t := String(e.t)
	for k in data.MISSIONS:
		var M: Dictionary = data.MISSIONS[k]
		if t.ends_with("— " + String(M.get("was", M.name))) or t == String(M.name):
			return k
	return ""


func journal(k: String, text: String) -> void:
	S.log.append({"t": mission_title(k), "k": k, "x": text, "at": S.time})
	toast("✎ Journal updated")


func start_mission(k: String) -> void:
	if S.missions.has(k):
		return
	var num: int = 1 if k == "home" else (2 if k == "gift" else (14 if k == "exam" else S.counter))
	if not k in ["home", "gift", "exam"]:
		S.counter += 1
	S.missions[k] = {"st": "active", "num": num}
	main.ambience.sfx("quest")
	S.focus = k
	journal(k, data.MISSIONS[k].log.start)
	if main.ambience.has_method("chime"):
		main.ambience.chime()


func complete_mission(k: String) -> void:
	if not S.missions.has(k) or S.missions[k].st == "done":
		return
	S.missions[k].st = "done"
	main.ambience.sfx("fanfare")
	journal(k, data.MISSIONS[k].log.done)
	if S.focus == k:
		S.focus = null
	save_game()


func current_mission() -> String:
	# the mission the HUD shows: the one last taken up, or else the newest still open ("" when none is)
	var act := []
	for k in S.missions:
		if m_active(k):
			act.append(k)
	if act.is_empty():
		return ""
	var k: String = S.focus if S.focus in act else act[0]
	for a in act:
		if S.missions[a].num > S.missions[k].num and not S.focus in act:
			k = a
	return k


func objective_text() -> String:
	var k := current_mission()
	if k == "":
		if S.flags.get("examPassed", false):
			return data.IDLE_LINES.post
		return data.IDLE_LINES.study if all_open_done() else data.IDLE_LINES.explore
	var o: Dictionary = data.MISSIONS[k].obj
	var s := ""
	match k:
		"home": s = o.go
		"gift": s = o.party if (has_item("torro_joan") or has_item("torro_mar")) else o.buy
		"dog": s = o.back if S.trufa == "following" else o.find
		"bike": s = o.back if has_item("bike_chain") else (o.fetch if S.flags.get("bikeNeed", false) else o.collect)
		"crema": s = o.back if has_item("crema") else o.buy
		"brush": s = o.back if has_item("brush") else o.find
		"profbook": s = o.back if has_item("textbook") else o.fetch
		"flour": s = o.back if has_item("rye") else o.buy
		"rivalry": s = o.back if has_item("torro_mar") else o.buy
		"hat": s = o.back if has_item("cap") else o.find
		"camera": s = o.back if has_item("camera_marta") else o.fetch
		"grail":
			if has_item("bk_ghost"):
				s = o.back
			elif S.flags.get("albaAsked", false):
				s = "%s (%d/5)" % [o.flowers, mini(5, count_item("flower"))]
			else:
				s = o.find
		"exam": s = o.sit
		"thief": s = o.lead
		"guell": s = o.back if has_item("salamandreta") else (o.key if has_item("cellar_key") else o.look)
		"ball": s = o.back if has_item("ball") else o.find
		"level": s = o.give if S.flags.get("workmenMet", false) else o.find
	return s                                      # (the step alone, one line: rule 10 #34; the name is in the journal)


func all_open_done() -> bool:
	for k in data.OPEN_MISSIONS:
		if not m_done(k):
			return false
	return true


func give_reward(cents: int, items := []) -> void:
	if cents:
		S.money += cents
		toast("+" + money(cents))
		main.ambience.sfx("coin")
	for id in items:
		if not add_item(id):
			S.money += 200
			toast("Bag full — took €2.00 instead")


func ach_earned(id: String) -> bool:
	match id:
		"all": return all_open_done()
		"plaques": return S.plaques.size() >= 10
		"pfand": return S.bottles_returned >= 15
		"binned": return S.binned >= 5
		"foodie": return S.eaten.size() >= 8
		"manolo": return S.flags.get("recovered", false)
		"exam": return S.flags.get("examPassed", false)
		"wheel": return S.flags.get("wheelRidden", false)
	return m_done(id)


func check_achievements() -> void:
	for a in data.ACHIEVEMENTS:
		if not S.ach_seen.has(a.id) and ach_earned(a.id):
			S.ach_seen[a.id] = true
			toast("★ Achievement: " + a.title, 3.4)


func npc_visible(id: String) -> bool:
	return party_on() if data.NPCS[id].get("party", false) else true


# ------------------------------------------------------------------ talking

func rotating(id: String, lines: Array) -> String:
	var i: int = int(S.talk.get(id, 0)) % lines.size()
	S.talk[id] = int(S.talk.get(id, 0)) + 1
	return lines[i]


func talk_to(id: String) -> void:
	var d: Dictionary = data.NPCS[id]
	var name: String = d.name
	main.npcs.face(id, main.player.global_position)
	if d.has("intro") and not S.intro.has(id):
		S.intro[id] = true
		# (round 23, the user: Montse asks after Trufa first thing; her introduction would come before it)
		if not (id == "montse" and m_done("gift") and not S.missions.has("dog")):
			say(name, d.intro)
	if mission_talk(id, name):
		return
	if id == "rosa" and not S.flags.get("note1", false):
		say(name, data.NOTE_GIVE.rosa)
		after(func(): give_note(1, name))
		return
	if id == "maria" and not S.flags.get("note2", false):
		say(name, data.NOTE_GIVE.maria)
		after(func(): give_note(2, name))
		return
	if north_talk(id, d, name):
		return
	if d.get("pickpocket", false):
		return manolo_talk(id, d)
	if d.get("officer", false):
		if S.flags.get("manoloGone", false):
			if not S.stolen.is_empty():
				return officer_return(name)
			return say(name, rotating("bofarull_thanks", d.thanks))
		if S.flags.get("manoloCaught", false):
			return say(name, data.MISSIONS.thief.after)
		if m_active("thief"):
			# (round 35: he goes back to his post when she leaves La Rambla; spoken to again, he comes with her again —
			# on La Rambla; off it, he keeps to his beat)
			var oq: Dictionary = main.npcs.outdoor.get(id, {})
			if not oq.is_empty() and String(oq.get("mode", "")) in ["back", "waiting"]:
				if main.street_name(main.player.global_position).contains(String(d.get("beat", ""))):
					say(name, "Right behind you again. Show me this charmer of yours.")
					after(func(): main.npcs.set_mode(id, "follow"))
				else:
					say(name, "I can't leave La Rambla, I'm afraid: it's my beat. Find me there and I'll come with you.")
				return
			return say(name, rotating("bofarull_tail", data.MISSIONS.thief.tailing))
		if not S.stolen.is_empty():
			return officer_report(name)
	if d.get("pfand", false):
		return pfand_offer(name)
	if d.get("shells", false) and count_item("shell") > 0:
		return bulk_sell(name, "shell", "seashells")
	if d.get("mushrooms", false) and count_item("red_mushroom") > 0:
		return mushroom_sell(name)
	if d.get("shop", false):
		return shop_talk(id, name)
	if d.get("guard", false):
		return say(name, rotating(id, d.lines))
	if main.where == "out" and m_active("gift") and not S.flags.get("pfandTip", false) and not (has_item("torro_joan") or has_item("torro_mar")):
		S.flags.pfandTip = true
		if data.has("MONEY_NOTE"):
			journal("gift", String(data.MONEY_NOTE))            # (round 41: she notes it)
		return say(name, data.PFAND_TIP)
	if d.has("party_lines") and party_on() and m_done("gift"):
		# (round 23, the user: she said her after-party lines with the guests still there)
		return say(name, moment(d, rotating(id + "_party", d.party_lines)))
	if d.has("birthday") and m_done("gift"):
		S.talk.bdayTurn = int(S.talk.get("bdayTurn", 0)) + 1
		if S.talk.bdayTurn % 3 != 0:
			return say(name, moment(d, rotating(id + "_bday", d.birthday)))
	var lines: Array = d.lines.duplicate()
	if d.has("after_dog") and m_done("dog"):
		lines.append(d.after_dog)
	# (round 41, the user: they thank Sandra "when she speaks to them again. And then after cycling through other things
	# that they say, they should come back to that") `after_mission` {mission: line}: said first, then in its turn
	var am: Dictionary = d.get("after_mission", {})
	for mk in am:
		if m_done(mk):
			if not S.talk.has(id + "_thanked_" + mk):
				S.talk[id + "_thanked_" + mk] = true
				return say(name, String(am[mk]))
			lines.append(String(am[mk]))
	if d.has("exam"):
		lines.append(exam_line(d))
	say(name, moment(d, rotating(id, lines)))


func moment(d: Dictionary, l: String) -> String:
	# (round 41, rule 10 #51b: a line that asks after something Sandra has since done is swapped for its after-line:
	# `once_done` {mission: [the line before, the line after]})
	var od: Dictionary = d.get("once_done", {})
	for k in od:
		if m_done(k) and l == String(od[k][0]):
			return String(od[k][1])
	return l


func offer_mission(k: String, name: String) -> void:
	# (round 23, the user: "don't give Sandra the ability to reject missions": she says yes)
	var M: Dictionary = data.MISSIONS[k]
	say(name, M.offer)                                 # (round 38: no yes from Sandra, rule 10 #52: the talk runs on)
	after(func():
		start_mission(k)
		say(name, M.accept)
		on_mission_start(k))


func on_mission_start(k: String) -> void:
	if k == "camera":
		var c: Array = S.cont.vicens_cupboard
		if not c.any(func(e): return e.id == "camera_marta"):
			c.append({"id": "camera_marta", "n": 1})
	if k in ["brush", "ball", "hat", "guell"]:
		refresh_ground()


# ------------------------------------------------------------------ shops

func shop_stock(shop_id: String) -> Array:
	return data.SHOPS[shop_id].items.filter(func(e): return not S.sold.has(e[0]))


func open_shop(shop_id: String) -> void:
	if not data.SHOPS.has(shop_id):
		return
	if main.panels and not main.dlg_open:
		main.panels.open_shop(shop_id)
		return
	shop_list(shop_id)


func shop_list(shop_id: String) -> void:
	# (the old list form of the counter, kept for the tests)
	var sh: Dictionary = data.SHOPS[shop_id]
	var opts := []
	for e in shop_stock(shop_id):
		var id: String = e[0]
		var price: int = e[1]
		opts.append({"label": "%s — %s" % [item(id).name, money(price)], "fn": func():
			buy_item(shop_id, id, price)
			after(func(): shop_list(shop_id))})
	opts.append({"label": "That's all, thanks", "fn": func(): pass})
	ask(sh.title, "You have %s. What would you like?" % money(S.money), opts)


func buy_item(shop_id: String, id: String, price: int) -> void:
	var sh: Dictionary = data.SHOPS[shop_id]
	if S.money < price:
		if (id == "torro_joan" or id == "torro_mar") and m_active("gift"):
			say(data.NPCS[sh.keeper].name, data.MISSIONS.gift.noMoney)
		else:
			toast("You need %s more" % money(price - S.money))
		return
	if not can_add(id):
		toast("Your backpack is full")
		return
	S.money -= price
	add_item(id)
	if sh.get("unique", false):
		S.sold[id] = true
	toast("Bought: %s (−%s)" % [item(id).name, money(price)])
	main.ambience.sfx("buy")
	if m_active("gift") and (id == "torro_joan" or id == "torro_mar") and not S.flags.get("torroBought", false):
		S.flags.torroBought = true
		S.log.append({"t": mission_title("gift"), "k": "gift", "x": data.MISSIONS.gift.log.bought, "at": S.time})
		toast("✎ Journal updated")
	save_game()


# ------------------------------------------------------------------ things on the ground

func spawn_at(kind: String) -> Array:
	return {"bottle": [[14, 88], [30, 87], [44, 89], [58, 89], [72, 88]], "shell": [[66, 89], [79, 88], [93, 88]],
		"coin": [[22.3, 48.6], [65.7, 35.4], [35.3, 76.2]]}[kind]
	# (round 41, the user: "move the coins away from the white crossing lines… I wanted the coins to stay on the
	# bitumen. Not necessarily right in the middle of the road. It can be a little random") on the road, half way
	# between corners, a little off the middle of their lane; the third off La Rambla's walk onto its road


# (round 23, the user: "move the wildflowers into the forest on the hill"; in metres: five among the first trees at the
# hill's foot, which she can reach before the path is open, and four beside the path on the way up)
const WILDFLOWERS := [[-175.0, -103.0], [-150.0, -102.5], [-122.0, -103.0], [-68.0, -103.0], [-40.0, -104.0],
	[-196.13, -145.13], [-167.33, -168.2], [-55.92, -198.92], [-162.63, -243.46]]


# (each 11–16 m from the nearest path, every line of sight from the paths within 30 m crossing a trunk; round 23, the
# user: the third, beside Guillem, moved away from him towards the beach)
const RED_MUSHROOMS := [[174.2, -23.4], [114.06, -20.78], [171.7, 42.8]]     # (round 38: the first and third where the user marked them, in the wood's east half)


func metres_pos(x: float, z: float) -> Vector3:
	var p := Vector3(x, 0.0, z)
	p.y = main.ground_at(p)
	return p


func world_pos(X: float, Y: float) -> Vector3:
	var p := Vector3((X + 0.5 - OX) * T, 0.0, (Y + 0.5 - OY) * T)
	p.y = main.ground_at(p)
	return p


func build_ground() -> void:
	for kind in ["bottle", "shell", "coin"]:
		var pts: Array = spawn_at(kind)
		for i in pts.size():
			ground.append({"key": kind + str(i), "id": kind, "pos": world_pos(pts[i][0], pts[i][1]), "mission": ""})
	# (round 24, the user: the five for Alba's vase "spread out along the path", beside it, easy to spot: north_build.py
	# puts them on the hill path's verge; WILDFLOWERS is only for a world built before that)
	var flowers: Array = main.D.get("north", {}).get("flowers", WILDFLOWERS)
	for i in flowers.size():
		ground.append({"key": "flower" + str(i), "id": "flower", "pos": metres_pos(flowers[i][0], flowers[i][1]), "mission": ""})
	# the forest's three rare red mushrooms (round 22, the user: deep in the wood, out of sight of the paths, far
	# apart; in metres). The little white ones are touches.gd's, only to look at.
	for i in RED_MUSHROOMS.size():
		var q: Array = RED_MUSHROOMS[i]
		ground.append({"key": "red_mushroom" + str(i), "id": "red_mushroom", "pos": metres_pos(q[0], q[1]), "mission": ""})
	var Nn: Dictionary = main.D.get("north", {})
	if not Nn.is_empty():
		# (round 25: where it lies in the wood, uphill of the tree that stopped it; older builds: by the ledge)
		var bp: Array = Nn.get("ball", [Nn.ledge[0] + 0.8, Nn.ledge[1] - 0.6])
		ground.append({"key": "ball", "id": "ball", "pos": metres_pos(bp[0], bp[1]), "mission": "ball"})
		ground.append({"key": "cellar_key", "id": "cellar_key", "pos": metres_pos(Nn.park.key[0], Nn.park.key[1]), "mission": "guell"})
	# (round 32's play-through: the brush still lay where the park was before round 21 moved it a block down, inside
	# a house on Carrer de Nàpols where nobody could reach it; now on the lawn just below the Cascada)
	# (round 41, the user: "move the fisherman's cap slightly closer to the forest. So it's sitting between some
	# undergrowth, but still visible") 3.5 m east, among the first bushes of the wood's edge
	# (round 41, the user: "please put the paintbrush on the gravel, not on the grass… a meter or so over, or 2 meters")
	# 2 m north, on the gravel walk between the lawn and the pool
	for e in [["brush", [75, 75.4], "brush"], ["cap", [90.25, 80.1], "hat"]]:
		ground.append({"key": e[0], "id": e[0], "pos": world_pos(e[1][0], e[1][1]), "mission": e[2]})
	for g in ground:
		g.node = make_ground_node(g)
		main.outdoor.add_child(g.node)
		g.node.position = g.pos
	refresh_ground()


var key_glow: OmniLight3D              # (round 40) the cellar key's faint glow, breathing slowly
var coin_glows: Array = []              # (round 41) the coins' glows, twinkling


func make_ground_node(g: Dictionary) -> Node3D:
	# small stand-ins: a green bottle, a pale shell, a gold coin, an orange wildflower, a sable brush,
	# a red balloon on its string, a navy cap
	var n := Node3D.new()
	var add := func(mesh: Mesh, col: Color, at: Vector3, rot := Vector3.ZERO):
		var mi := MeshInstance3D.new()
		mi.mesh = mesh
		var m := StandardMaterial3D.new()
		m.albedo_color = col
		m.roughness = 0.4
		mi.material_override = m
		mi.position = at
		mi.rotation = rot
		n.add_child(mi)
	match g.id:
		"bottle":
			var c := CylinderMesh.new()
			c.top_radius = 0.035
			c.bottom_radius = 0.05
			c.height = 0.28
			add.call(c, Color(0.2, 0.5, 0.3), Vector3(0, 0.05, 0), Vector3(0, 0, PI / 2))
		"shell":
			var s := SphereMesh.new()
			s.radius = 0.07
			s.height = 0.06
			add.call(s, Color(0.95, 0.88, 0.8), Vector3(0, 0.03, 0))
		"coin":
			var c2 := CylinderMesh.new()
			c2.top_radius = 0.05
			c2.bottom_radius = 0.05
			c2.height = 0.012
			add.call(c2, Color(0.95, 0.75, 0.25), Vector3(0, 0.01, 0))
			# (round 41, the user: "make them glow a little bit") a soft gold glow, twinkling slowly (tick), so a coin
			# catches the eye on the paving
			var cm: StandardMaterial3D = (n.get_child(0) as MeshInstance3D).material_override
			cm.emission_enabled = true
			cm.emission = Color(1.0, 0.8, 0.35)
			cm.emission_energy_multiplier = 0.35        # (round 41, the user: "make the money not glow as much": 0.8 → 0.35)
			var cg := OmniLight3D.new()
			cg.light_color = Color(1.0, 0.82, 0.45)
			cg.omni_range = 0.6
			cg.light_energy = 0.16
			cg.shadow_enabled = false
			cg.position = Vector3(0, 0.08, 0)
			n.add_child(cg)
			coin_glows.append(cg)
		"flower":
			# (round 25, the user: "one stem each") a single stem, a head of petals round a middle, leaves at the foot
			# (round 41, the user: "the flowers on the hill should be smaller… They are a bit too easy to spot and they stick
			# right up… leaning over a little bit… smaller in terms of the stem" — a short stem leaning over, about 0.28 m
			# tall; then: "make the flowers less glossy and less cartoony") matte; ten slim petals cupped round a darker
			# middle, a thin stem, three slender leaves: a marigold, not a toy daisy
			var hh := 0.2
			var lean := 0.32
			var stem := CylinderMesh.new()
			stem.top_radius = 0.0035
			stem.bottom_radius = 0.005
			stem.height = hh
			add.call(stem, Color(0.33, 0.5, 0.22), Vector3(0, hh / 2.0 * cos(lean), hh / 2.0 * sin(lean)), Vector3(lean, 0, 0.04))
			var top := Vector3(0.008, hh * cos(lean), hh * sin(lean))
			var petal := SphereMesh.new()
			petal.radius = 0.02
			petal.height = 0.007
			petal.radial_segments = 10
			petal.rings = 4
			for k in 10:
				var b := k * TAU / 10.0 + 0.1 * sin(k * 2.7)
				var pc := Color(0.93, 0.48, 0.1).lerp(Color(0.97, 0.63, 0.22), float(k % 3) * 0.4)
				add.call(petal, pc, top + Vector3(cos(b), 0.0, sin(b)) * 0.026 + Vector3(0, 0.004, 0), Vector3(0.0, -b, 0.28))
				n.get_child(n.get_child_count() - 1).scale = Vector3(1.5, 1.0, 0.5)
			var mid := SphereMesh.new()
			mid.radius = 0.011
			mid.height = 0.011
			add.call(mid, Color(0.5, 0.27, 0.08), top + Vector3(0, 0.009, 0))
			var leaf := SphereMesh.new()
			leaf.radius = 0.045
			leaf.height = 0.008
			for a in [0.5, 2.6, 4.4]:
				add.call(leaf, Color(0.3, 0.48, 0.2), Vector3(cos(a) * 0.04, 0.02, sin(a) * 0.04), Vector3(0.0, -a, 0.35))
				n.get_child(n.get_child_count() - 1).scale = Vector3(1.0, 1.0, 0.3)
			for c in n.get_children():
				if c is MeshInstance3D:
					(c.material_override as StandardMaterial3D).roughness = 0.9
					(c.material_override as StandardMaterial3D).metallic_specular = 0.2
			n.scale = Vector3.ONE * 1.45                        # (toy-sized, like the pigeons and cats; round 41: 1.7 → 1.45)
		"red_mushroom":
			# (round 38, the user: "Make it the ou de reig: orange-red, no spots, good to eat") Caesar's mushroom, rare and
			# bigger than the white ones: an orange-red cap with no spots over yellow gills, a yellow stem rising from its
			# white cup (the "egg" it is named for)
			var cup := CylinderMesh.new()
			cup.top_radius = 0.065
			cup.bottom_radius = 0.05
			cup.height = 0.06
			add.call(cup, Color(0.96, 0.95, 0.9), Vector3(0, 0.03, 0))
			var stem2 := CylinderMesh.new()
			stem2.top_radius = 0.03
			stem2.bottom_radius = 0.04
			stem2.height = 0.2
			add.call(stem2, Color(0.96, 0.8, 0.28), Vector3(0, 0.11, 0))
			var gills := CylinderMesh.new()
			gills.top_radius = 0.145
			gills.bottom_radius = 0.145
			gills.height = 0.012
			add.call(gills, Color(0.97, 0.76, 0.26), Vector3(0, 0.205, 0))
			var dome := SphereMesh.new()
			dome.radius = 0.16
			dome.height = 0.12
			dome.is_hemisphere = true
			add.call(dome, Color(0.9, 0.3, 0.06), Vector3(0, 0.21, 0))
		"brush":
			# (round 42, the user: "Where is the brush in the park? It is not there": a 22 cm dark stick lying flat in
			# dark grass, invisible at dusk) toy-sized like the key, a pale wooden handle with a brass ferrule and a
			# dark sable tip (no glow: the user)
			# (round 41, the user: "it looks like a pencil. Could you make it more brushy so there's a brush at the end?
			# Look up a paintbrush. The bristles should be not too long, but not too short") an artist's flat brush: a
			# handle tapering to its end, a silver ferrule pinched flat where it grips the hairs, and a flat tuft of
			# pale bristles a quarter of the handle's length, their tips dipped in blue paint
			var b := CylinderMesh.new()
			b.top_radius = 0.0055
			b.bottom_radius = 0.0105
			b.height = 0.18
			add.call(b, Color(0.78, 0.25, 0.18), Vector3(-0.03, 0.02, 0), Vector3(0, 0, PI / 2))     # (a red lacquered handle)
			var fer := CylinderMesh.new()
			fer.top_radius = 0.0115
			fer.bottom_radius = 0.0115
			fer.height = 0.035
			add.call(fer, Color(0.8, 0.8, 0.82), Vector3(0.0775, 0.02, 0), Vector3(0, 0, PI / 2))
			var pinch := BoxMesh.new()                         # (the ferrule flattened at its mouth)
			pinch.size = Vector3(0.016, 0.011, 0.03)
			add.call(pinch, Color(0.8, 0.8, 0.82), Vector3(0.1, 0.02, 0))
			var hair := BoxMesh.new()
			hair.size = Vector3(0.038, 0.008, 0.028)
			add.call(hair, Color(0.9, 0.82, 0.62), Vector3(0.126, 0.02, 0))
			var dip := BoxMesh.new()
			dip.size = Vector3(0.012, 0.0085, 0.0285)
			add.call(dip, Color(0.2, 0.42, 0.8), Vector3(0.149, 0.02, 0))
			n.scale = Vector3.ONE * 1.7                     # (the user: no glow on it)
		"ball":
			# Biel's ball: a simple red ball (round 26, the user)
			var s3 := SphereMesh.new()
			s3.radius = 0.11
			s3.height = 0.22
			add.call(s3, Color(0.78, 0.07, 0.05), Vector3(0, 0.11, 0))
		"cellar_key":
			var ring := TorusMesh.new()
			ring.inner_radius = 0.02
			ring.outer_radius = 0.03
			add.call(ring, Color(0.83, 0.65, 0.25), Vector3(0, 0.01, 0))
			var shaft := BoxMesh.new()
			shaft.size = Vector3(0.09, 0.012, 0.014)
			add.call(shaft, Color(0.83, 0.65, 0.25), Vector3(0.07, 0.01, 0))
			# (round 40, the user: "the key is just lying nearby under the scrub, but it is slighty glowing") toy-sized
			# like the other finds, its brass a little lit, and a faint warm light that slowly breathes (tick)
			n.scale = Vector3.ONE * 1.7
			for c in n.get_children():
				var km: StandardMaterial3D = (c as MeshInstance3D).material_override
				km.emission_enabled = true
				km.emission = Color(1.0, 0.78, 0.35)
				km.emission_energy_multiplier = 0.6
			key_glow = OmniLight3D.new()
			key_glow.light_color = Color(1.0, 0.8, 0.45)
			key_glow.omni_range = 0.9
			key_glow.light_energy = 0.5
			key_glow.shadow_enabled = false
			key_glow.position = Vector3(0.03, 0.12, 0)
			n.add_child(key_glow)
		"cap":
			var s4 := SphereMesh.new()
			s4.radius = 0.13
			s4.height = 0.13
			add.call(s4, Color(0.12, 0.16, 0.32), Vector3(0, 0.04, 0))
	return n


func ground_visible(g: Dictionary) -> bool:
	if S.taken.get(g.key, false):
		return false
	if g.mission != "":
		return m_active(g.mission) and not has_item(g.id)
	return true


func refresh_ground() -> void:
	for g in ground:
		g.node.visible = ground_visible(g)


func pick_up(g: Dictionary) -> void:
	if g.id == "coin":
		S.taken[g.key] = true
		S.money += 100
		toast("Found a coin! +€1.00")
		main.ambience.sfx("coin")
		refresh_ground()
		return
	if not add_item(g.id):
		toast("Your backpack is full")
		return
	S.taken[g.key] = true
	refresh_ground()
	if g.mission != "":
		say("Sandra", {"brush": "A sable brush lies on the gravel by the Cascada, C.F. scratched into its handle. Found it!",
			"ball": data.MISSIONS.ball.got_text, "cellar_key": data.MISSIONS.guell.clue_key,
			"cap": "Caught on a bush at the forest edge: a navy fisherman's cap with a brass anchor. That must be Tomàs's!"}[g.id])
		if g.id == "cellar_key":
			S.flags.keyFound = true
		S.log.append({"t": mission_title(g.mission), "k": g.mission, "x": data.MISSIONS[g.mission].log.get("key" if g.id == "cellar_key" else "got"), "at": S.time})
		toast("✎ Journal updated")
	else:
		toast("Picked up: " + item(g.id).name)
		main.ambience.sfx("pickup")


func on_enter(rid: String) -> void:
	if rid == "int_sandra" and m_active("home"):
		complete_mission("home")
		say("Rosa", "There you are! I was about to send a search party to the beach. Coffee's on the table — and there's a card on your desk. It came this morning.")
	save_game()


func on_exit_to_world() -> void:
	if main.room == "int_alessandra" and m_done("gift"):
		S.flags.partyOver = true
	# (round 22) once Sandra has been in and out of a building, the van has taken Manolo, and the agent is back
	# at his fountain
	if S.flags.get("manoloCaught", false) and not S.flags.get("manoloGone", false):
		S.flags.manoloGone = true
		main.npcs.set_gone("manolo", true)
		var oq: Dictionary = main.npcs.outdoor.get("bofarull", {})
		if not oq.is_empty():
			oq.holder.position = oq.home
			oq.target = oq.home
			oq.mode = ""
	# (round 22) things that happen while she's indoors: the Mossos take Pere away (round 41: the workmen finish the
	# path on the spot now, story.gd, rule 10 #16d)
	if m_done("guell") and not S.flags.get("pereGone", false):
		S.flags.pereGone = true
	refresh_people()
	if main.north:
		main.north.refresh()
	# what grows back: flowers, bottles and shells every second time (round 26, the user: the flowers "every 2 times
	# she goes in and then comes out")
	S.exits = int(S.exits) + 1
	if S.exits >= 2:
		S.exits = 0
		for g in ground:
			if g.id == "flower":
				S.taken[g.key] = false
		# (round 22, the user: bottles and mushrooms come back every second time, but only once the party is over,
		# so before it the torró's €6 has to come from the first ones found)
		var after_party: bool = S.flags.get("partyOver", false)
		for g in ground:
			if g.id == "shell" or (after_party and g.id in ["bottle", "red_mushroom"]):
				S.taken[g.key] = false
	refresh_ground()


# ------------------------------------------------------------------ bins, cupboards, the backpack

func open_bin(bid: String) -> void:
	var cd: float = float(S.bin_cd.get(bid, -1e9))
	if S.play_time - cd > 120.0:
		S.bin_cd[bid] = S.play_time
		if rng.randf() < 0.3:
			ask("Lucky find", "Something glints at the bottom of the bin: an empty deposit bottle, worth a euro at the Pfand desk. Somebody's loss... could it be your gain?", [
				{"label": "Take the bottle", "fn": func():
					if add_item("bottle"):
						say("", "Sandra retrieves the bottle with quiet German pride.")
					else:
						say("", "Your backpack is full — the bottle stays where it is.")
					after(func(): bin_panel())},
				{"label": "Leave it where it is", "fn": func(): after(func(): bin_panel())}])
			return
	bin_panel()


func bin_panel() -> void:
	main.panels.open_bin()


func bin_item(id: String) -> void:
	if is_book(id):
		return say("Sandra", BIN_REFUSE_BOOK)
	if is_clothes(id):
		return say("Sandra", BIN_REFUSE_CLOTHES)
	if is_quest_item(id) or item(id).get("kind", "") == "tool":
		return say("Sandra", BIN_REFUSE_QUEST)
	remove_item(id, 1)
	S.binned += 1
	main.ambience.sfx("bin")
	toast(data.BIN_MSGS[int(S.bin_msg) % data.BIN_MSGS.size()], 3.2)
	S.bin_msg = int(S.bin_msg) + 1


func open_container(cid: String) -> void:
	var C: Dictionary = data.CONTAINERS[cid]
	var flavor: String = LIB_FLAVOR if C.kind == "library" else C.get("flavor", "")
	if flavor != "" and not S.shelf_seen.has(cid):
		S.shelf_seen[cid] = true
		say("", flavor)
	if cid == "vicens_cupboard" and S.cont[cid].any(func(e): return e.id == "camera_marta") and not S.flags.get("cameraSeen", false):
		S.flags.cameraSeen = true
		say("", "Behind a folded jacket on the bottom shelf: a good camera in a leather case. This must be Marta's!")
	after(func(): container_panel(cid))


func container_panel(cid: String) -> void:
	main.panels.open_container(cid)                            # (the 2D game's two lists: the cupboard and the backpack)


func put_panel(cid: String) -> void:
	var opts := []
	for e in S.inv:
		var id: String = e.id
		opts.append({"label": item(id).name, "fn": func():
			move_to_container(cid, id)
			after(func(): container_panel(cid))})
	opts.append({"label": "Back", "fn": func(): container_panel(cid)})
	ask(data.CONTAINERS[cid].name, "Put what here?", opts)


func move_to_bag(cid: String, id: String) -> void:
	var C: Dictionary = data.CONTAINERS[cid]
	var list: Array = S.cont[cid]
	if C.kind == "library":
		say("Remei", "Read it here as long as you like, reina. But no book leaves this floor — not even for you.")
		return
	if not can_add(id):
		toast("Your backpack is full")
		return
	for i in list.size():
		if list[i].id == id:
			list[i].n -= 1
			if list[i].n <= 0:
				list.remove_at(i)
			break
	add_item(id, 1)
	if id == "camera_marta":
		S.log.append({"t": mission_title("camera"), "k": "camera", "x": data.MISSIONS.camera.log.got, "at": S.time})
		toast("✎ Journal updated")


func move_to_container(cid: String, id: String) -> void:
	var C: Dictionary = data.CONTAINERS[cid]
	if C.kind == "library":
		return say("Remei", "These shelves are catalogued. Your things stay with you, please.")
	if C.kind == "bookshelf" and not is_book(id):
		return say("", SHELF_STANDARDS)
	if C.kind != "bookshelf" and is_book(id):
		return say("", CUPBOARD_NO_BOOKS)
	var list: Array = S.cont[cid]
	var ex = null
	if stackable(id):
		for q2 in list:
			if q2.id == id:
				ex = q2
	if ex:
		ex.n += 1
	else:
		list.append({"id": id, "n": 1})
	remove_item(id, 1)


func open_reader(id: String, back := Callable()) -> void:
	var it := item(id)
	var pages := []
	var title: String = it.name
	var src = null
	if it.get("kind", "") == "book" and data.BOOKS.has(id):
		src = data.BOOKS[id]
		title = "%s — %s" % [src.title, src.author]
	elif data.NOTES.has(id):
		src = data.NOTES[id]
		title = src.get("title", title)
	var text = src.get("text", it.get("desc", "")) if src is Dictionary else it.get("desc", "")
	var whole: String = "\n\n".join(PackedStringArray((text if text is Array else [text]).map(func(x): return str(x))))
	pages = paginate(whole, 950)                           # (the 2D game's paragraphs, poured into pages that fill the reader)
	var author := ""
	if src is Dictionary:
		author = String(src.get("author", "The Rambla Guide to Economics" if data.NOTES.has(id) else ""))
		title = String(src.get("title", title))
	after(func(): main.panels.open_reader(title, author, pages, back))       # (the 2D game's reader page)


func paginate(text: String, most := 420) -> Array:
	# pages of up to ~420 letters (the reader's page holds about 950), broken between sentences
	var out := []
	var cur := ""
	for para in text.split("\n"):
		for sent in para.replace(". ", ".\u0001").replace("? ", "?\u0001").replace("! ", "!\u0001").split("\u0001"):
			if cur.length() + sent.length() > most and cur != "":
				out.append(cur.strip_edges())
				cur = ""
			cur += sent + " "
		cur += "\n"
	if cur.strip_edges() != "":
		out.append(cur.strip_edges())
	return out


func bag_panel() -> void:
	if main.dlg_open:
		return
	main.panels.open_bag()


func bag_list() -> void:
	# (the old list form of the backpack, kept for the tests)
	var opts := []
	for e in S.inv:
		var id: String = e.id
		var worn: bool = S.worn.outfit == id or S.worn.hat == id
		opts.append({"label": "%s%s%s" % [item(id).name, " ×%d" % e.n if e.n > 1 else "", " (wearing)" if worn else ""], "fn": func(): item_panel(id)})
	opts.append({"label": "Close", "fn": func(): pass})
	ask("Backpack — %s · %d/%d" % [money(S.money), S.inv.size(), MAX_SLOTS], "Your backpack is empty." if S.inv.is_empty() else "What would you like to look at?", opts)


func item_panel(id: String) -> void:
	var it := item(id)
	var opts := []
	match it.get("kind", ""):
		"food":
			opts.append({"label": "Eat it", "fn": func(): eat_item(id)})
		"book", "note":
			opts.append({"label": "Read it", "fn": func(): open_reader(id)})
		"clothes":
			opts.append({"label": "Take it off" if (S.worn.outfit == id or S.worn.hat == id) else "Wear it", "fn": func(): wear_item(id)})
		"tool":
			if id == "camera":
				opts.append({"label": "Take a photograph", "fn": func():
					if main.street.riding != null:         # (round 41, rule 10: on the bike, said with the backpack still up)
						main.toast("Get off the bike first to take a photo")
						main.ambience.sfx("nope")
						bag_list()
					else:
						photo_prompt()})
	opts.append({"label": "Back", "fn": func(): bag_list()})
	ask(it.name, it.get("desc", ""), opts)


func photo_prompt() -> void:
	# the old spare camera Marta gives her: a photograph of the view, kept in user://photos
	if not has_item("camera"):
		return
	if main.street.riding != null:                # (round 41, rule 10: on the bike it says so at once, before any question)
		main.viewfinder(true)                      # (which, on the bike, only says "Get off the bike first to take a photo")
		return
	# (round 41, rule 10, the user: "remove the confirmation with the camera. Once you click on it, it should go
	# straight to camera mode") straight into its viewfinder, no question
	main.viewfinder.call_deferred(true)


func eat_item(id: String) -> void:
	if id == "rye":
		return say("Sandra", "Raw rye flour? Even Oma would draw the line at that. It's for Ferran's bread.")
	if item(id).get("kind", "") != "food":
		return say("Sandra", "That isn't something you can eat.")
	if is_quest_item(id):
		return say("Sandra", "Better not — somebody is counting on this one. It's not for eating... yet.")
	remove_item(id, 1)
	S.eaten[id] = true
	main.ambience.sfx("eat")
	main.boost = 30.0                                 # (not added up: eating again starts the half minute afresh)
	main.boost_id = id
	say("Sandra", data.EAT_MSG.get(id, "Delicious. Sandra feels full of energy."))


func wear_item(id: String) -> void:
	var it := item(id)
	var slot: String = it.get("slot", "outfit")
	if S.worn[slot] == id:
		S.worn[slot] = null
		toast("Took off: " + it.name)
	else:
		S.worn[slot] = id
		toast("Wearing: " + it.name)
		main.ambience.sfx("cloth")
	main.dress_sandra()


func gathering_over() -> bool:
	# (round 38) a world's hook: whether its gathering (Barcelona: the birthday party) is over, so a host left alone
	# stands at her own spot (NPCS after_at)
	return false


func notebook_lines() -> Array:
	# (a world's hook) the heroine's own list of things to do, each [text, 0 not started / 1 going on / 2 done]: a page
	# of the journal, left of it
	return []


func journal_panel() -> void:
	if main.dlg_open:
		return
	main.panels.open_journal()


# ------------------------------------------------------------------ furniture and the street

func use_thing(t: Dictionary) -> void:
	# a thing in a room (interiors.py's "things") or in the street (world2d.py's "things2d")
	if t.has("clue"):
		return clue(String(t.clue), t)
	if t.has("c"):
		return open_container(t.c)
	if t.get("card", false):
		return read_card()
	if t.get("kind", "") == "phone":
		return use_phone()
	if t.get("vase", false):
		return say("", VASE_FULL if S.flags.get("vaseFull", false) else VASE_EMPTY)
	if t.get("sleep", false):
		return offer_sleep(t.get("t", ""))
	if t.get("kind", "") == "pfand":
		return pfand_offer("Anna")
	if t.get("kind", "") in ["counter", "libdesk"] and data.SHOPS.has(main.room):
		return open_shop(main.room)
	if t.get("type", "") == "bin":
		return open_bin(t.get("id", "bin"))
	if t.get("type", "") == "sign" and t.get("landmark", "") != "":
		S.plaques[t.landmark] = true
	if t.get("type", "") == "bench":                       # (as in the 2D game: one of three, the same for each bench)
		var lines := ["A wooden bench. Sandra sits for a moment, listening to the city hum, then carries on.",
			"A bench with a view. A pigeon at the other end eyes Sandra's pockets hopefully.",
			"A bench, warm from the sun. Someone has carved 'J + M 1992' into the armrest."]
		return say("", lines[absi(String(t.get("id", "")).hash()) % 3])
	if t.get("type", "") == "lampR":
		# (round 35, the everything-visit: these stand all along the seafront and the city's edges too, not only on the
		# Rambla, so the line no longer names it)
		return say("", "One of the city's old lamp posts, curly iron and old gold glass.")
	var text: String = t.get("t", t.get("text", ""))
	if text != "":
		return say("", text)
	say("", {"counter": "A counter, polished by a thousand elbows.", "libdesk": "The librarian's desk: date stamps, a bell, and a sign — SILENCI, SI US PLAU."}.get(t.get("kind", ""), "Nothing unusual."))


# ------------------------------------------------------------------ the north (round 22)


func unlocked(lock: String) -> bool:
	return lock == "cellar_key" and (has_item("cellar_key") or S.flags.get("cellarOpen", false))


func locked_door(lock: String) -> void:
	say("", data.MISSIONS.guell.clue_door)


func open_locked(lock: String) -> bool:
	# the first time a locked outdoor door is opened: the key turns (true: she stays put this press)
	if lock == "cellar_key" and not S.flags.get("cellarOpen", false):
		S.flags.cellarOpen = true
		say("", data.MISSIONS.guell.clue_door_open)
		return true
	return false


# ------------------------------------------------------------------ every frame

# game minutes per real second (round 23, the user: "slow down time by half"; was 1.0)
const CLOCK_RATE := 0.5


func tick(dt: float) -> void:
	S.play_time += dt
	if key_glow and key_glow.is_visible_in_tree():
		key_glow.light_energy = 0.35 + 0.3 * (0.5 + 0.5 * sin(float(S.play_time) * 1.6))
	for i in coin_glows.size():
		var cg: OmniLight3D = coin_glows[i]
		if is_instance_valid(cg) and cg.is_visible_in_tree():
			cg.light_energy = 0.1 + 0.12 * (0.5 + 0.5 * sin(float(S.play_time) * 2.3 + i * 2.1))     # (round 41: less than half)
	if not main.dlg_open:
		S.time = fmod(float(S.time) + dt * CLOCK_RATE, 1440.0)
	if S.pending != null:
		var p: Vector3 = main.player.global_position
		if Vector2(p.x - S.pending.x, p.z - S.pending.z).length() > 30.0 and not main.dlg_open:
			reveal_theft()
	save_t += dt
	if save_t > 30.0:
		save_t = 0.0
		check_achievements()
		save_game()

# ------------------------------------------------------------------ the world's story fills these in
# (worlds/<name>/game/story.gd extends this script and overrides them; these do nothing, so a world without a
# story still runs)

func give_note(n: int, who: String) -> void:
	pass


func party_on() -> bool:
	return false


func exam_line(d: Dictionary) -> String:
	return ""


func mission_talk(id: String, name: String) -> bool:
	return false


func manolo_talk(id: String, d: Dictionary) -> void:
	pass


func reveal_theft() -> void:
	pass


func officer_report(name: String) -> void:
	pass


func officer_return(name: String) -> void:
	pass


func pfand_offer(name: String) -> void:
	pass


func bulk_sell(name: String, id: String, label: String) -> void:
	pass


func mushroom_sell(name: String) -> void:
	pass


func shop_talk(id: String, name: String) -> void:
	pass


func refresh_people() -> void:
	pass


func clue(c: String, t: Dictionary) -> void:
	pass


func north_talk(id: String, d: Dictionary, name: String) -> bool:
	return false


func read_card() -> void:
	pass


func use_phone() -> void:
	pass


func offer_sleep(flavour: String) -> void:
	pass
