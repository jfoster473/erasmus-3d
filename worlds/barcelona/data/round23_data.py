# Round 23 (the user's third batch, 19 October 2026): words and places that changed. exec'd by remap3d.py with its
# `d` (the 3D game's data) after north_data.py.

# ---- Jordi has a shop now: BICIS JORDI on the north side of Carrer de València, between Passeig de Gràcia and La
# Rambla (kit.py JORDI_HOUSE); he stands outside it. His old pavement workshop on Aragó is gone.
d['objects'] = [o for o in d['objects'] if o.get('type') != 'bikestand']
J = d['NPCS']['jordi']
J['at'] = ['world', 28.6, 54.05]          # (build_assets.py JORDI_SPOT, by his bikes)
J['intro'] = ("Bon dia! Jordi, of Bicis Jordi. I've fixed this neighbourhood's bikes since before Bicing was a twinkle "
              "in the mayor's eye.")
J['lines'][2] = ("València runs dead straight for kilometres: Cerdà drew it with a ruler in 1859. Perfect for testing "
                 "brakes, terrible for testing patience.")
J['look'].pop('apron', None)          # (the user: his shirt was half blue, half brown: the brown is his trousers now)
J['look']['legs'] = '#5a4a3a'
B = d['MISSIONS']['bike']
STREET = "Carrer de València, between Passeig de Gràcia and La Rambla"
B['party'] = ["Oh, and Sandra, how is your bike going? You took it to Jordi for repairs, right? He's the one with the "
              "bike shop on Carrer de València.",
              "Sandra: My bike! With everything going on I'd completely forgotten. I'll go and pick it up from Jordi."]
B['obj']['collect'] = "Collect your bike from Bicis Jordi on " + STREET
B['obj']['back'] = "Take the chain to Jordi's bike shop on Carrer de València"
B['log']['start'] = ("At the party Alessandra asked about my bike: it's been in for repairs at Bicis Jordi, on " + STREET +
                     ". Time to go and collect it.")
B['log']['got'] = "Collected the chain from Genís. Back to Jordi's shop on Carrer de València."

# ---- Alessandra: her own lines during the party; the after-party ones only once it's over; the bike line for good
A = d['NPCS']['alessandra']
BIKE_LINE = ("How is your bike going? You took it to Jordi for repairs, right? He's the one on Carrer de València, "
             "between Passeig de Gràcia and La Rambla.")
A['party_lines'] = [
    "Have you tried the tortilla? Iker made it. Don't tell him it's the best thing here, he'll never stop.",
    "Twenty-four! I feel exactly the same as yesterday, only with more cava.",
    "Clara has taken a hundred photos already. Smile, she's pointing that thing at you again.",
    BIKE_LINE,
    "When the music stops we go out on the balcony. You can see the lamps all the way down the Passeig.",
]
A['party_hat'] = True
A['lines'].append(BIKE_LINE)
A['birthday'].append(BIKE_LINE)

# the guests talk in little groups (the user: "in groups of 3 and 2"), facing each other, instead of all facing the
# room's front: Alessandra, Bruno and Iker on the rug; Clara and Lucía by the window
GROUPS = {'alessandra': ([5.1, 4.45], [5.6, 4.2]), 'bruno': ([4.45, 3.35], [5.6, 4.2]), 'iker': ([5.75, 3.35], [5.6, 4.2]),
          'clara': ([9.25, 3.3], [10.3, 3.6]), 'lucia': ([10.35, 3.15], [10.3, 3.6])}
for k, ((x, y), f) in GROUPS.items():
    d['NPCS'][k]['at'] = ['int_alessandra', x, y]
    d['NPCS'][k]['face_to'] = f
d['NPCS']['bruno']['lines'][1] = "The birthday girl asked whether you were coming about eleven times. Now she can stop."

# ---- Montse asks after Trufa first thing; her thanks don't presume to know Sandra's business
M = d['MISSIONS']['dog']
M['offer'] = ("Hello, how are you, dear? I'm not so well, I'm afraid. My little Trufa slipped her lead chasing a squirrel "
              "and ran off east, all the way into the forest, and my knees won't carry me up there any more. Would you look "
              "for her? She's a scruffy little thing, brown and white, with a red collar.")
M['done'] = ["TRUFA! Oh, you bad, wonderful dog! (Trufa leaps into Montse's arms and licks her chin.)",
             "I can't thank you enough. Here, five euros, and don't you dare argue.",
             "And these: Trufa found them the other day and brought them home like a trophy. Maybe they will be of use to you.",
             "You are welcome to walk Trufa whenever you please. She is very loyal once she gets to know someone."]
M['log']['done'] = "Trufa is home! Montse gave me €5, and some chewed pages Trufa had found: Study Notes 3."
d['NPCS']['montse']['after_dog'] = "You are welcome to walk Trufa whenever you please. She is very loyal once she gets to know someone."

# ---- the park's lady: there's no parliament to see in this park
d['NPCS']['mireia']['lines'][0] = ("This was the city's first public park. A young student called Antoni Gaudí helped build the "
                                   "great cascade fountain at its far end.")

# ---- wildflowers: only for Alba's vase now, and they grow in the woods at the foot of the hill up to Tibidabo
FAIR_NAME = "the Parc d'Atraccions del Tibidabo"
d['ITEMS']['flower']['desc'] = ("A bright orange wildflower from beside the path up to Tibidabo. Lovely in a vase; "
                                "nobody buys them.")
R_ = d['NPCS']['roser']
R_.pop('flowers', None)
R_['lines'][1] = ("I walk through this forest every day, rain or shine. If it's wildflowers you want to see, they aren't here: "
                  "they grow along the path up the hill to " + FAIR_NAME + ", on the grass beside it.")
d['NPCS']['alba']['lines'][1] = ("They say wildflowers grow along the path up the hill to Tibidabo, here and there on the grass beside "
                                 "it, and that more come up after you pick them. I'll take their word for it.")
d['NPCS']['gloria']['lines'][1] = ("Wildflowers? Never on the pavement, maca! Try the path up the hill to Tibidabo: they "
                                   "grow on the grass all the way up to the funfair.")
d['NPCS']['albert']['lines'][1] = "From here you can see the woods at the foot of Tibidabo. The wildflowers grow along the path up through them."
G = d['MISSIONS']['grail']
# (round 37, the user: the girl who wants the flowers says "I hear that they grow on the mountain, but I'm not the hiking
# type" — the reason Sandra goes)
G['albaAsk'] = ("'The Bookseller's Ghost'? Mm, I have it — it's right there on my table. I don't need the book, but what I "
                "do need are some flowers to fill this empty vase. I hear that wildflowers grow on the mountain, along the "
                "path up to Tibidabo, but I'm not the hiking type. Bring me five and it's yours.")

# ---- the Rambla's sandy promenade stops at the Gran Via (the user: "remove the big yellow part next to the beach at
# the end of La Rambla; just make it like the rest of the promenade"): past the road, the Passeig Marítim's own paving,
# and the beach's sand where it ran out onto the beach
_ID = {v: int(k) for k, v in d['tileNames'].items()}
for _y in range(83, 88):
    for _x in range(d['RAMBLA_PROM'][0] - 1, d['RAMBLA_PROM'][1] + 2):
        if d['tiles'][_y][_x] == _ID['PROM']:
            d['tiles'][_y][_x] = _ID['PAVE'] if _y == 83 else (_ID['WALK'] if _y < 86 else _ID['SAND'])

# ---- people who don't know Sandra's business don't talk as if they did (the user: Montse's "these belong to you")
H_ = d['MISSIONS']['hat']
H_['done'] = [("And these pages blew into my fishing spot yesterday, the same wind that took my cap. 'Chapter 5: Comparative "
               "Advantage', it says. Fish and loaves. Maybe they're of more use to you than to an old fisherman.")
              if 'Comparative Advantage' in t else t for t in H_['done']]
