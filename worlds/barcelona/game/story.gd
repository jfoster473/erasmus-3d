# Barcelona's story (the restructure, 20 October 2026): who says what, and how each mission turns; the pickpocket,
# the exam, the north's mysteries (Park Güell, the ball, the spirit level), Sandra's notebook, her phone. It extends
# the engine's rules (res://engine/game.gd: state, saving, the talk queue, items, missions' bookkeeping, shops, things on
# the ground, bins and cupboards, the backpack, the clock), overriding its hooks. The words themselves are in
# worlds/barcelona/data/data3d.json (made by data/remap3d.py from the 2D game's data and the round files).
extends "res://engine/game.gd"

const NOTE_FULL := "Your bag is full — I'll have it sent round to your flat. It'll be waiting in your cupboard at Flor de Lliri."


func load_game() -> bool:
	# (round 38, 06 #97) the park's ticket is a status for good: a save from before (the ticket used up as she left) that
	# shows she has been in the park — Mercè's mission, or the Amic del Park card — keeps it
	if not super.load_game():
		return false
	if has_item("park_pass") or S.missions.has("guell"):
		S.flags.parkTicket = true
	return true


func notes_all() -> bool:
	for n in range(1, 6):
		if not S.flags.get("note%d" % n, false):
			return false
	return true


func give_note(n: int, who: String) -> void:
	var id := "note%d" % n
	if S.flags.get(id, false):
		return
	S.flags[id] = true
	if add_item(id):
		toast("Received " + item(id).name)
	else:
		S.cont.sandra_cupboard.append({"id": id, "n": 1})
		say(who, NOTE_FULL)
	var from := " from Rosa" if n == 1 else (" from Maria" if n == 2 else "")
	S.log.append({"t": "Study Notes %d" % n, "x": "Received %s%s. Chapter %d of the Rambla Guide to Economics — open it in my backpack (I) to read it." % [item(id).name, from, n], "at": S.time})


func gathering_over() -> bool:
	return S.flags.get("partyOver", false)


func party_on() -> bool:
	return S.missions.has("gift") and not S.flags.get("partyOver", false)


func exam_line(d: Dictionary) -> String:
	if S.flags.get("examPassed", false):
		return d.exam[2]
	return d.exam[1] if all_open_done() else d.exam[0]


func mission_talk(id: String, name: String) -> bool:
	var open := m_done("gift")
	var giver := ""
	for k in data.OPEN_MISSIONS:
		if data.MISSIONS[k].get("giver", "") == id:
			giver = k
	# --- the birthday party ---
	if id == "alessandra" and m_active("gift"):
		var tid := "torro_joan" if has_item("torro_joan") else ("torro_mar" if has_item("torro_mar") else "")
		if tid == "":
			say(name, data.MISSIONS.gift.arrive)
			return true
		for l in data.MISSIONS.gift.give:
			say(name, l)
		after(func():
			remove_item(tid)
			complete_mission("gift"))
		if not S.missions.has("bike"):
			# (round 20) she asks after Sandra's bike, in for a service with Jordi: that starts its mission
			for l in data.MISSIONS.bike.party:
				say(name, String(l))                     # (round 38: hers alone; Sandra has no line here)
			after(func(): start_mission("bike"))
		return true
	# --- helpers who hand over mission items ---
	if id == "genis" and m_active("bike") and S.flags.get("bikeNeed", false) and not has_item("bike_chain") and not S.flags.get("chainGiven", false):
		say(name, data.MISSIONS.bike.handoff)
		after(func():
			if add_item("bike_chain"):
				S.flags.chainGiven = true
				S.log.append({"t": mission_title("bike"), "k": "bike", "x": data.MISSIONS.bike.log.got, "at": S.time})
				toast("Received: Bicycle chain")
			else:
				say(name, "Your bag's stuffed! Make some room and come back."))
		return true
	if id == "alice" and m_active("profbook") and not has_item("textbook") and not S.flags.get("bookGiven", false):
		say(name, data.MISSIONS.profbook.handoff)
		after(func():
			if add_item("textbook"):
				S.flags.bookGiven = true
				S.log.append({"t": mission_title("profbook"), "k": "profbook", "x": data.MISSIONS.profbook.log.got, "at": S.time})
				toast("Received: Principles of Economics")
			else:
				say(name, "Your bag is full — make some room first."))
		return true
	if id == "alba" and m_active("grail") and not S.flags.get("albaTraded", false):
		if not S.flags.get("albaAsked", false):
			S.flags.albaAsked = true
			say(name, data.MISSIONS.grail.albaAsk)
			S.log.append({"t": mission_title("grail"), "k": "grail", "x": data.MISSIONS.grail.log.ask, "at": S.time})
			toast("✎ Journal updated")
			return true
		if count_item("flower") >= 5:
			for l in data.MISSIONS.grail.albaGive:
				say(name, l)
			after(func():
				remove_item("flower", 5)
				S.flags.vaseFull = true
				S.flags.albaTraded = true
				add_item("bk_ghost")
				S.log.append({"t": mission_title("grail"), "k": "grail", "x": data.MISSIONS.grail.log.got, "at": S.time})
				toast("Received: The Bookseller's Ghost"))
			return true
		say(name, "Five wildflowers for the vase, and the book is yours. You have %d so far. They grow on the slopes above the city, along the path up to Tibidabo — I'm not much of a hiker, which is why I asked you." % count_item("flower"))
		return true
	if id == "nuria" and m_active("hat") and has_item("cap"):
		say(name, data.MISSIONS.hat.giveHint)
		return true
	if id == "tomas" and m_active("hat") and has_item("cap"):
		for l in data.MISSIONS.hat.done:
			say(name, l)
		after(func():
			remove_item("cap")
			give_reward(500)
			if not add_item("shell", 3):
				S.money += 300
			complete_mission("hat")
			main.npcs.redress("tomas")           # (round 27: he puts his cap straight back on)
			give_note(5, name))
		return true
	if id == "biel" and m_active("ball") and has_item("ball"):
		finish_ball(name)
		return true
	if id == "toni" and m_active("level") and has_item("spirit_level"):
		# (round 41, rule 10 #16d) she hands it over; the screen fades to black and back, the barriers stand pushed
		# aside, and he thanks her in the user's words: the path is open
		for l in data.MISSIONS.level.give:
			say(name, l)
		after(func():
			remove_item("spirit_level")
			S.flags.levelGiven = true
			main.fade_then(func():
				S.flags.pathOpen = true
				journal("level", data.MISSIONS.level.log.done)
				complete_mission("level")
				refresh_people()
				if main.north:
					main.north.refresh())
			get_tree().create_timer(0.8).timeout.connect(func(): say(name, data.MISSIONS.level.open)))
		return true
	# --- the exam ---
	if id == "oriol" and open:
		if not S.missions.has("profbook"):
			offer_mission("profbook", name)
			return true
		if m_active("profbook"):
			if has_item("textbook"):
				for l in data.MISSIONS.profbook.done:
					say(name, l)
				after(func():
					remove_item("textbook")
					give_reward(500)
					complete_mission("profbook"))
			else:
				say(name, data.MISSIONS.profbook.remind)
			return true
		return oriol_exam(name)
	if id == "jordi" and not S.missions.has("bike"):
		# (round 38, the user: before the bike mission he just says he's still on it)
		say(name, String(data.NPCS.jordi.get("waiting", "")))
		return true
	# (round 41, the user: "Talking to biel didn't trigger the mission") Biel, beside his mother, starts it too: he
	# blurts it out, she explains — the mission given as from her (rule 10 #51c)
	if id == "biel" and open and "ball" in data.OPEN_MISSIONS and not S.missions.has("ball"):
		say(name, "My ball went over the railing! Down there, in the trees! Mama, tell her!")
		offer_mission("ball", String(data.NPCS.rosalia.name))
		return true
	if id == "biel" and m_active("ball") and not has_item("ball"):
		say(name, "It's RED. And it went really far down. About a hundred metres, I think. Maybe a thousand.")
		return true
	if giver == "" or not open:
		return false
	var k := giver
	var M: Dictionary = data.MISSIONS[k]
	if k == "bike":
		# Sandra's own bike: in for a service with Jordi, who needs a new chain before it's ready
		if not S.missions.has("bike"):
			start_mission("bike")                      # (a game from before round 20: no party question)
		if m_active("bike") and not S.flags.get("bikeNeed", false):
			S.flags.bikeNeed = true
			say(name, M.offer)
			say(name, M.accept)
			after(func():
				S.log.append({"t": mission_title("bike"), "k": "bike", "x": M.log.need, "at": S.time})
				toast("✎ Journal updated"))
			return true
	if not S.missions.has(k):
		offer_mission(k, name)
		return true
	if m_done(k):
		return false
	var finish := func(fn: Callable) -> bool:
		for l in M.done:
			var sp := speaker(String(l), name)
			say(sp[0], sp[1])
		after(fn)
		return true
	match k:
		"ball":
			if has_item("ball"):
				finish_ball(name)
				return true
		"guell":
			if has_item("salamandreta"):
				return finish.call(func():
					remove_item("salamandreta")
					add_item("park_pass")
					S.flags.guellBack = true
					S.flags.parkTicket = true                 # (06 #97: the park's open to her for good, card or not)
					complete_mission("guell")
					main.north.refresh()
					main.touches.refresh()
					toast("Received: Amic del Park card", 3.0))
		"dog":
			if S.trufa == "following":
				return finish.call(func():
					S.trufa = "home"
					main.street.trufa_home()
					give_reward(500)
					complete_mission("dog")
					give_note(3, name))
		"bike":
			if has_item("bike_chain"):
				return finish.call(func():
					remove_item("bike_chain")
					S.has_bike = true
					complete_mission("bike"))
		"crema":
			if has_item("crema"):
				return finish.call(func():
					remove_item("crema")
					give_reward(2000)
					complete_mission("crema"))
		"brush":
			if has_item("brush"):
				for l in M.done:
					say(name, l)
				after(func():
					remove_item("brush")
					if S.inv.size() <= MAX_SLOTS - 2:
						add_item("cafe_llet")
						add_item("croissant")
						toast("Received: Cafè amb llet & croissant")
					else:
						say(name, M.doneFull)
						give_reward(400)
					complete_mission("brush"))
				return true
		"flour":
			if has_item("rye"):
				return finish.call(func():
					remove_item("rye")
					give_reward(1400)
					if not add_item("vollkorn"):
						say(name, M.doneFull)
						S.money += 250
					else:
						toast("Received: Vollkornbrot")
					complete_mission("flour"))
		"rivalry":
			if has_item("torro_mar"):
				return finish.call(func():
					remove_item("torro_mar")
					give_reward(1800)
					if not add_item("torro_joan"):
						say(name, M.doneFull)
						S.money += TORRO_PRICE
					else:
						toast("Received: Torró de Casa Joan")
					complete_mission("rivalry"))
			if has_item("torro_joan"):
				say(name, M.ownTorro)
				return true
		"camera":
			if has_item("camera_marta"):
				return finish.call(func():
					remove_item("camera_marta")
					give_reward(1000)
					if not add_item("camera"):
						S.cont.sandra_cupboard.append({"id": "camera", "n": 1})
						say(name, "Your bag's full — I'll drop the spare camera at your flat. It'll be in your cupboard.")
					else:
						toast("Received: Marta's old spare camera, a Pentax K1000")   # (round 41, the user's words, rule 10)
					complete_mission("camera"))
		"grail":
			if has_item("bk_ghost"):
				return finish.call(func():
					remove_item("bk_ghost")
					complete_mission("grail")
					give_note(4, name))
	say(name, M.remind)
	if data.NPCS[id].get("shop", false):
		after(func(): open_shop(main.room))
	return true


func oriol_exam(name: String) -> bool:
	if S.flags.get("examPassed", false):
		say(name, data.ORIOL_STATES.after)
		return true
	if not all_open_done():
		say(name, data.ORIOL_STATES.wait)
		return true
	if not notes_all():
		say(name, data.ORIOL_STATES.study)
		return true
	if not S.missions.has("exam"):
		start_mission("exam")
	say(name, data.ORIOL_STATES.ready)
	ask(name, "Sit the exam now?", [{"label": "Sit the exam now", "fn": func(): run_exam(name)},
		{"label": "Come back later", "fn": func(): say(name, "Very well. The exam will wait for you. It is patient; I am less so.")}])
	return true


func run_exam(name: String) -> void:
	# round 22, the user: no quiz any more: a montage of the exam (exam_scene.gd), then he tells her she has passed
	say(name, data.ORIOL_STATES.begin)
	after(func():
		var sc := Node.new()
		sc.set_script(load(main.world_res("game/exam_scene.gd")))
		main.add_child(sc)
		sc.play(main, func():
			sc.queue_free()
			main.npcs.face("oriol", main.player.global_position)
			for l in data.ORIOL_STATES.passed:
				say(name, l)
			after(func():
				S.flags.examPassed = true
				if not add_item("diploma"):
					S.cont.sandra_cupboard.append({"id": "diploma", "n": 1})
				complete_mission("exam")
				toast("Received: UPF Diploma of Economics", 3.0))))


func talk_trufa() -> void:
	if m_active("dog") and S.trufa == "lost":
		say("", "Brown and white, a red collar, and a stick three times her size: this must be Montse's dog. \"Trufa?\" Her ears shoot up at her name. She drops the stick, sniffs Sandra's hand, and decides Sandra is her new favourite person. She trots along at Sandra's heels.")
		after(func():
			S.trufa = "following"
			main.ambience.sfx("bark")
			main.street.trufa_follow()
			S.log.append({"t": mission_title("dog"), "k": "dog", "x": data.MISSIONS.dog.log.found, "at": S.time})
			toast("✎ Journal updated"))
	elif S.trufa == "lost":
		# (her name is only known once Montse has asked for help: the collar has nothing on it)
		say("", "A scruffy brown-and-white dog with a red collar is gnawing a stick, deep among the trees. There's no tag on the collar, no name, nothing. She wags politely but won't leave her stick, or come with a stranger. Perhaps someone is looking for her.")
	else:
		main.street.talk_trufa()


func manolo_talk(id: String, d: Dictionary) -> void:
	if S.flags.get("manoloCaught", false):
		return say(d.name, data.MISSIONS.thief.manolo_cuffed)
	if m_active("thief"):
		# (round 22) with the agent close behind her, this is the moment; otherwise just his patter, no more thieving
		var off: Dictionary = main.npcs.outdoor.get("bofarull", {})
		if not off.is_empty() and off.holder.global_position.distance_to(main.player.global_position) < 30.0:
			return catch_manolo()
		return say(d.name, rotating(id, d.lines))
	var eligible: Array = S.inv.filter(func(e): return not is_quest_item(e.id) and not is_book(e.id) and not is_clothes(e.id))
	if eligible.is_empty() or S.pending != null:
		return say(d.name, rotating(id, d.lines))
	# (round 41, rule 10 #51b: the chat in which he robs her is the one in which he warns her about pickpockets, so the
	# theft's "the one who warned her" is always true)
	say(d.name, String(d.get("warn", rotating(id, d.lines))))
	var e: Dictionary = eligible[rng.randi() % eligible.size()]
	remove_item(e.id, 1)
	S.stolen.append(e.id)
	var p: Vector3 = main.player.global_position
	S.pending = {"id": e.id, "x": p.x, "z": p.z}


func catch_manolo() -> void:
	# round 22: Manolo starts his patter; Agent Bofarull runs up behind Sandra, handcuffs him, and the talk goes on
	var lines: Array = data.MISSIONS.thief.catch
	var mq: Dictionary = main.npcs.outdoor.manolo
	var oq: Dictionary = main.npcs.outdoor.bofarull
	main.npcs.set_mode("manolo", "hold", {"look_at": main.player.global_position})
	say(lines[0][0], lines[0][1])
	after(func():
		var spot := officer_spot(mq.holder.position, oq.holder.position)
		main.npcs.set_mode("bofarull", "run_to", {"goal": spot, "on_arrive": func():
			S.flags.manoloCaught = true
			main.npcs.set_mode("bofarull", "hold", {"look_at": mq.holder.position})
			main.npcs.cuff("manolo", true)
			# (round 41, the user: "as soon as he is arrested, the thief should be standing facing away from the
			# policeman… his hands are behind his back… regardless of which direction he started with")
			main.npcs.set_mode("manolo", "hold", {"look_at": mq.holder.position * 2.0 - oq.holder.position})
			main.ambience.sfx("pickup")
			for i in range(1, lines.size()):
				say(lines[i][0], lines[i][1])
			after(func():
				give_back("Agent Bofarull")
				after(func(): complete_mission("thief")))}))


func officer_spot(mp: Vector3, op: Vector3) -> Vector3:
	# (round 41: the play-through found him stopping on Sandra's side of Manolo, boxing her in between them; he
	# stands at Manolo's shoulder instead, square to the line from Sandra, on whichever side he came from)
	var d: Vector3 = main.player.global_position - mp
	d.y = 0.0
	d = d.normalized() if d.length() > 0.1 else Vector3(0, 0, 1)
	var side := Vector3(-d.z, 0, d.x)
	if side.dot(op - mp) < 0.0:
		side = -side
	var spot := mp + side * 0.85
	spot.y = main.ground_at(spot)
	return spot


func give_back(name: String) -> void:
	var back := []
	while not S.stolen.is_empty() and can_add(S.stolen[0]):
		var id: String = S.stolen.pop_front()
		add_item(id)
		back.append(item(id).name)
	S.flags.recovered = true
	if not back.is_empty():
		say(name, "These are yours: %s. %s" % [", ".join(back), "The rest won't fit in your bag: they'll wait for you with me, come back for them." if not S.stolen.is_empty() else "Keep your bag closer next time, eh?"])
	else:
		say(name, "Your bag is too full to take anything back. Make some room and come and see me: it'll all be waiting.")


func restore_scenes() -> void:
	# (a saved game in the middle of, or after, the pickpocket's arrest: put everyone back where the story left them)
	var npcs: Node = main.npcs
	if S.flags.get("manoloGone", false):
		npcs.set_gone("manolo", true)
	elif S.flags.get("manoloCaught", false):
		var mq: Dictionary = npcs.outdoor.get("manolo", {})
		if not mq.is_empty():
			npcs.cuff("manolo", true)
			var oq: Dictionary = npcs.outdoor.get("bofarull", {})
			if not oq.is_empty():
				oq.holder.position = officer_spot(mq.holder.position, mq.holder.position + Vector3(0.85, 0, 0))
				npcs.set_mode("bofarull", "hold", {"look_at": mq.holder.position})
				npcs.set_mode("manolo", "hold", {"look_at": mq.holder.position * 2.0 - oq.holder.position})   # (his back to him)
	elif m_active("thief"):
		npcs.set_mode("bofarull", "follow")
	refresh_people()


func reveal_theft() -> void:
	var it := item(S.pending.id)
	S.pending = null
	say("", "Hmm? Sandra's backpack feels lighter. She checks... %s — gone! That charming man on the Rambla — the one who warned her about pickpockets. Oh, of course. Maybe the Guàrdia Urbana can help: Agent Bofarull patrols by the Canaletes fountain." % it.name)


func officer_report(name: String) -> void:
	# round 22: no longer the items back on the spot; he follows Sandra back to Manolo and catches him at it
	# (round 23: no turning missions down) she tells him straight away
	# (round 38: Sandra has no lines; he reads it in her face)
	say(name, "You look like someone who's just had her pocket picked. On La Rambla, I'd bet.")
	for l in data.MISSIONS.thief.report:
		say(name, l)
	after(func():
		start_mission("thief")
		main.npcs.set_mode("bofarull", "follow"))


func officer_return(name: String) -> void:
	# (things that didn't fit in her bag when he gave them back)
	say(name, "Ah, Sandra: the rest of your things, from Manolo's pockets.")
	after(func(): give_back(name))


func pfand_offer(name: String) -> void:
	var n := count_item("bottle")
	if n == 0:
		return say(name, rotating("anna", data.NPCS.anna.lines))
	ask(name, "Deposit bottles! I'll take all of them — just like the Pfand back in Germany, no?", [
		{"label": "Return %d bottle%s (+%s)" % [n, "s" if n > 1 else "", money(n * 100)], "fn": func():
			remove_item("bottle", n)
			S.money += n * 100
			S.bottles_returned += n
			toast("+%s — Pfand refunded" % money(n * 100))
			main.ambience.sfx("coin")
			save_game()},
		{"label": "Not now", "fn": func(): pass}])


func bulk_sell(name: String, id: String, label: String) -> void:
	var n := count_item(id)
	# (only seashells now: wildflowers are for Alba's vase alone and nobody buys them; rounds 23, 37)
	var intro := "Seashells! Let's see... good ones. I'll take the lot."
	var who := "salva"
	ask(name, intro, [
		{"label": "Sell %d %s (+%s)" % [n, label if n > 1 else label.trim_suffix("s"), money(n * 100)], "fn": func():
			remove_item(id, n)
			S.money += n * 100
			toast("+" + money(n * 100))
			save_game()},
		{"label": "Keep them", "fn": func(): say(name, rotating(who, data.NPCS[who].lines))}])


func mushroom_sell(name: String) -> void:
	# Guillem buys the forest's rare ous de reig at €5 each (round 22; the ou de reig since round 38)
	var r := count_item("red_mushroom")
	ask(name, "Ostres! An ou de reig! Do you know how long I've looked for those this year? Five euros each, gladly.", [
		{"label": "Sell %d %s (+%s)" % [r, "ous de reig" if r > 1 else "ou de reig", money(r * 500)], "fn": func():
			remove_item("red_mushroom", r)
			S.money += r * 500
			toast("+" + money(r * 500))
			main.ambience.sfx("coin")
			save_game()},
		{"label": "Keep them", "fn": func(): say(name, rotating("guillem", data.NPCS.guillem.lines))}])


const TORRO_PRICE := 600          # (cents; round 22: €6, set in remap3d.py: the round 23 review found two checks still at €12)


func shop_talk(id: String, name: String) -> void:
	if (id == "joan" or id == "neus") and m_active("gift") and not (has_item("torro_joan") or has_item("torro_mar")) and S.money < TORRO_PRICE:
		say(name, data.MISSIONS.gift.noMoney)
	elif id == "ponc" and S.inv.any(func(e): return is_book(e.id)):
		say(name, "We sell stories. We do not buy them back. If you want to read for free, the university library at UPF is up the big staircase.")
	elif id == "empar":
		say(name, "Bon dia, maca! Coffee? A croissant? Or... the finest crema catalana in Barcelona, sugar torched to order?")
	elif id == "ferran":
		say(name, "Bon dia! Guten Morgen! Something from the oven? The Vollkornbrot is a novelty here — but a good one.")
	else:
		say(name, rotating(id, data.NPCS[id].lines))
	after(func(): open_shop(main.room))


func intro() -> void:
	# a new game: waking on the beach
	if not S.get("new", false):
		return
	for p in data.INTRO_TEXT:
		# (the 2D game's keyboard lines on a computer; its TOUCH line on a phone, as there; round 20e)
		var touch_line := String(p).begins_with("TOUCH")
		if main.touch_pad:
			if touch_line:
				say("", String(p).trim_prefix("TOUCH: ").replace("Walk with the pad.", "Walk with the pad; LOOK, then drag on the screen, to look round."))
			elif not "ARROW KEYS" in String(p):
				say("", String(p).replace("SPACE or ENTER", "A").replace(", M the map", "").replace(" In choices, ENTER confirms and SPACE backs out.", ""))
		elif not touch_line:
			say("", String(p).replace("SPACE or ENTER", "E").replace(", M the map", "").replace(" In choices, ENTER confirms and SPACE backs out.", ""))
	after(func():
		S.new = false
		S.log.append({"t": mission_title("home"), "k": "home", "x": data.MISSIONS.home.log.start, "at": S.time}))


# Sandra's notebook (round 22): what she wanted to do here, each item where a mission starts; ticked once it has
# (round 23, the user: on the bedside table, more general, "Visit" before the places, all on one page)
# (round 37, the user: "just make all of it things that a normal Erasmus student would want… Just don't turn every
# single one into a big story"): short notes from the journey; one line per mission, in the order a player does them,
# the exams last.
const NOTEBOOK_ITEMS := [
	["Alessandra's birthday: find her a present", ["gift"]],
	["Say hello to people on La Rambla", ["dog"]],
	["Cycle through the city on my bike", ["bike"]],
	["Visit the Sagrada Família", ["crema"]],
	["Visit the MNAC, Catalonia's great art museum", ["brush"]],
	["Meet my professor at the university", ["profbook"]],
	["Find a German bakery", ["flour"]],
	["Try torró from the torró shops", ["rivalry"]],
	["Spend an afternoon on the beach", ["hat"]],
	["See Casa Batlló, Gaudí's house on Passeig de Gràcia", ["camera"]],      # (the user: name the house)
	["Be careful of pickpockets on La Rambla", ["thief"]],
	["Visit Park Güell", ["guell"]],
	["Go to the funfair on Tibidabo", ["ball"]],
	["Walk the path through the woods on Tibidabo", ["level"]],
	["Find a second-hand bookshop", ["grail"]],                # (its flowers grow past the workmen's barrier)
	["Pass my exams!", ["exam"]],
]


func speaker(line: String, name: String) -> Array:
	# a line that starts with someone's name ("Biel: ...") is theirs; otherwise the one talking says it
	for who in ["Rosalia", "Laia", "Sandra", "Mercè"]:
		if line.begins_with(who + ": "):
			return [who, line.trim_prefix(who + ": ")]
	return [name, line]


func finish_ball(name: String) -> void:
	for l in data.MISSIONS.ball.done:
		var sp := speaker(String(l), name)
		say(sp[0], sp[1])
	after(func():
		remove_item("ball")
		complete_mission("ball")
		if add_item("spirit_level"):
			toast("Received: Spirit level")
			start_mission("level")
		else:
			S.cont.sandra_cupboard.append({"id": "spirit_level", "n": 1})
			start_mission("level"))


func refresh_people() -> void:
	# who is out and about, by the story: Pere until the Mossos take him (Marc after), the workmen until the path opens
	var np: Node = main.npcs
	np.set_gone("pere", S.flags.get("pereGone", false))
	np.set_gone("marc", not S.flags.get("pereGone", false))
	# (round 41, rule 10 #16d: the workmen stay by the path once it is open, and thank her)


func clue(c: String, t: Dictionary) -> void:
	var G: Dictionary = data.MISSIONS.guell
	match c:
		"plinth":
			if S.flags.get("guellBack", false):
				return say("", "The Salamandreta, green and gold, back on its marble plinth. The card has gone.")
			return say("", String(t.get("t", "")))
		"cellardoor":
			if unlocked("cellar_key"):
				if not S.flags.get("cellarOpen", false):
					S.flags.cellarOpen = true
					return say("", G.clue_door_open)
				return say("", "The cellar door, unlocked now. Stairs lead down into the cool and the dark.")
			return say("", G.clue_door)
		"crate":
			if m_active("guell") and not has_item("salamandreta"):
				for l in G.clue_crate:
					var sp := speaker(String(l), "")
					say(sp[0], sp[1])
				after(func():
					if add_item("salamandreta"):
						remove_item("cellar_key")
						S.log.append({"t": mission_title("guell"), "k": "guell", "x": G.log.got, "at": S.time})
						toast("Received: The Salamandreta")
					else:
						say("", "Sandra's bag is too full to carry it. She'll have to make room."))
				return
			return say("", "An open crate, packed with straw. Empty now.")
		"clipboard":
			if m_active("guell") or m_done("guell"):
				return say("", "The clipboard: PORT DE BARCELONA, crates for Rotterdam and Geneva, pieces from Lisbon, Prague and Naples, every line signed P.")
			return say("", String(t.get("t", "")))
	say("", String(t.get("t", "Nothing unusual.")))


func north_talk(id: String, d: Dictionary, name: String) -> bool:
	# the north's people: their own business before their ordinary lines
	if d.has("after_guell") and m_done("guell"):
		say(name, d.after_guell)
		return true
	if d.get("gardener", false) and (has_item("cellar_key") or S.flags.get("keyFound", false)):
		say(name, d.searching)                       # (and nothing to give him: the key isn't his to have back)
		return true
	if d.get("gardener", false) and m_active("guell") and d.has("busy"):
		say(name, d.busy)                            # (round 40, the user: from the mission's start, he's looking for it)
		return true
	if d.get("park_tickets", false):
		if has_item("park_pass"):
			say(name, "Amic del Park! Straight in, and welcome back. " + rotating(id, d.lines))
		elif S.flags.get("parkTicket", false):
			say(name, "You've got your ticket: come and go by any gate you like, as often as you like. " + rotating(id, d.lines))
		else:
			ask(name, "Park Güell: three euros, and it's yours to come and go as you please. In you go?", [
				{"label": "Buy a ticket (€3)", "fn": func():
					if S.money < 300:
						say(name, "Three euros, I'm afraid. Come back when you have them; it'll still be here. It's been here since 1914.")
						return
					S.money -= 300
					S.flags.parkTicket = true
					main.ambience.sfx("coin")
					toast("−€3.00 · Park Güell: open to you now, by any gate")
					main.north.refresh()
					main.north.open_gate(0)                   # (round 38: the main gate swings open for her)
					say(name, rotating(id, d.lines))},
				{"label": "Not now", "fn": func(): say(name, rotating(id, d.lines))}])
		return true
	if d.get("wheel", false):
		ask(name, "The Giradabo: one euro, once round, a minute of the best view in Catalonia. Hop in?", [
			{"label": "Ride the wheel (€1)", "fn": func():
				if S.money < 100:
					say(name, "One euro, I'm afraid. Even the view isn't free.")
					return
				S.money -= 100
				main.ambience.sfx("coin")
				say(name, "In you go. Hands inside, and wave at the city.")
				after(func(): main.north.start_wheel())},
			{"label": "Not now", "fn": func(): say(name, rotating(id, d.lines))}])
		return true
	if d.has("workman"):
		S.flags.workmenMet = true
		if S.flags.get("pathOpen", false):
			say(name, rotating(id + "_thanks", data.MISSIONS.level.thanks))     # (round 41: they stay, and thank her)
			return true
		say(name, rotating(id, d.lines))
		return true
	return false


func notebook_lines() -> Array:
	# her list, each line [text, 0 not started / 1 going on / 2 done] (the journal's notebook page and the book by her bed)
	var out := []
	for it in NOTEBOOK_ITEMS:
		var ks: Array = it[1]
		out.append([String(it[0]), 2 if ks.any(func(k): return m_done(k)) else (1 if ks.any(func(k): return m_active(k)) else 0)])
	return out


func read_notebook() -> void:
	# (round 37) the book by her bed opens at the journal's notebook page: the same list, on one page
	main.panels.open_journal("notebook")


func read_card() -> void:
	say("Birthday card", data.MISSIONS.gift.card)
	if not S.missions.has("gift") and m_done("home"):
		say("", data.MISSIONS.gift.think)              # (round 38: the narrator's, not a line of hers)
		after(func():
			start_mission("gift")
			# (round 22, the user: "the friend tells her the two ways to make money": Rosa, from across the flat)
			if not S.flags.get("pfandTip", false):
				S.flags.pfandTip = true
				say("Rosa", "I heard that sigh. " + String(data.PFAND_TIP))
				journal("gift", String(data.get("MONEY_NOTE", ""))))       # (round 41: she notes it)


func use_phone() -> void:
	main.ambience.sfx("ring")
	say("", data.PHONE.intro)
	ask("", "Call home to Giessen?", [
		{"label": "Call Mama", "fn": func():
			say("Mama", String(data.PHONE.hello).trim_prefix("Mama: "))
			say("Mama", phone_hint())
			say("Mama", String(data.PHONE.bye).trim_prefix("Mama: "))},
		{"label": "Hang up", "fn": func(): pass}])


func phone_hint() -> String:
	if m_active("gift") and not (has_item("torro_joan") or has_item("torro_mar")):
		# (round 38, the user: Mama says nothing about money)
		return "Have you found a present for your friend yet? Something sweet from Barcelona, Schatz. Your friends there will know what to get." if S.money < 600 else "A torró is a proper present. Buy it and go to that party — and dance, for goodness' sake."
	if m_active("gift"):
		return "Take the torró to your friend's party on the Passeig de Gràcia! Don't stay on the phone with your mother, go!"
	var act: Array = S.missions.keys().filter(func(k): return m_active(k))
	if not act.is_empty():
		return "And your little jobs for people? \"%s\" — very good. Your father says finish one thing at a time." % objective_text()
	if all_open_done() and not S.flags.get("examPassed", false):
		return "You have all your notes? Then go and sit that exam. Papa and I will have our fingers crossed — half of Giessen will, too." if notes_all() else "You've helped half of Barcelona, I hear. Now the exam — do you have all your study notes? Friends, neighbours, strangers... ask around."
	if S.flags.get("examPassed", false):
		return "You PASSED? Papa is telling the whole street. The bakery lady cried. We are so proud of you."
	return "Tell me about the people you've met. Is anyone asking for help? You were always good at helping, Schatz."


func offer_sleep(flavour: String) -> void:
	# only Sandra's own bed (the others just get a comment): at night she sleeps till 07:00, by day a nap
	var mm: int = int(S.time) % 1440
	var night := mm >= 22 * 60 or mm < 7 * 60
	ask("", flavour + (" It is late. Go to sleep?" if night else " Lie down for a siesta?"), [
		{"label": "Sleep until morning" if night else "Nap for two hours", "fn": func():
			main.sleep(night, func():
				say("", "Sandra sleeps soundly under the high Eixample ceiling. 07:00 — a new day in Barcelona, and the smell of Rosa's coffee drifting in." if night else "A proper Mediterranean siesta. Sandra wakes at %02d:%02d, rested and only slightly creased." % [int(S.time) / 60, int(S.time) % 60])
				save_game())},
		{"label": "Not now", "fn": func(): pass}])


func guard_stop() -> void:
	main.npcs.face("sergi", main.player.global_position)
	say("Sergi", "Ho sento — sorry! The bridge to València is closed. Permanently, they tell me. Maybe one day... but not today.")
