# The 3D game's own layout, made from the 2D game's (data2d.json, map2d.png) with the user's changes:
#   La Rambla one block west: it now runs between the second and third block columns, where Carrer de
#     Roger de Llúria was; that block column moves east to fill the gap, and Roger de Llúria now runs
#     between it and Sandra's column. Everything on those columns (the tiles, the street things, the
#     people) moves with them.
#   The Sagrada Família one block down: it swaps with Torrons Casa Joan, so it has a block on all sides.
#   The university back in the 2D game's block, next to the beach (round 17 had moved it up a block, swapping
#     with Maria's; round 21, the user: "move the park and the uni down one block"), its door on Carrer de
#     Girona, facing the Ciutadella park across the street: the park moved down a block too, swapping with the
#     plain block below it (its paths, its sign and the people in it go with it).
#   Doors on all sides of the blocks, not all on the south; only shops open onto La Rambla.
#   Torró costs €6 (five deposit bottles on the beach, game.gd, and the forest's mushrooms).
#   The missions' names (round 22).
# Writes data3d.json and map3d.png, which the builder and the game read.
#   python3 remap3d.py
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'data2d.json')))
TN = {int(k): v for k, v in d['tileNames'].items()}
G = {v: k for k, v in TN.items()}
MW, MH = d['MW'], d['MH']
ROW0, ROW1 = 14, 85            # the city's rows (the street grid, its edge, the Rambla down to the Passeig)


def src_col(X):
    """The old column that new column X comes from (city rows only)."""
    if 34 <= X <= 41:
        return X + 13          # La Rambla (old 47..54)
    if 42 <= X <= 50:
        return X - 4           # the block column (old 38..46)
    if 51 <= X <= 54:
        return X - 17          # Carrer de Roger de Llúria (old 34..37)
    return X


def new_x(x, y):
    """Where an old position (tile units, may be fractional) goes."""
    if not (ROW0 <= y <= ROW1 + 0.999):
        return x
    k = int(x // 1)
    if 34 <= k <= 37:
        return x + 17
    if 38 <= k <= 46:
        return x + 4
    if 47 <= k <= 54:
        return x - 13
    return x


# the Sagrada Família and Torrons Casa Joan swap blocks
SAG_X0, SAG_X1 = 55, 63
A0, B0 = 19, 32                # the two blocks' top rows (9 rows each)


def swap_y(x, y):
    if SAG_X0 <= x < SAG_X1 + 1:
        if A0 <= y < A0 + 9:
            return y + 13
        if B0 <= y < B0 + 9:
            return y - 13
    return y


# ---- tiles
old = d['tiles']
tiles = [row[:] for row in old]
for Y in range(ROW0, ROW1 + 1):
    for X in range(MW):
        tiles[Y][X] = old[Y][src_col(X)]
# the Passeig's crossing to the beach, row 86
tiles[86][49:53] = [G['SAND']] * 4
tiles[86][51] = G['PALM']
tiles[86][36:40] = [G['PROM']] * 4
blkA = [tiles[Y][SAG_X0:SAG_X1 + 1] for Y in range(A0, A0 + 9)]
blkB = [tiles[Y][SAG_X0:SAG_X1 + 1] for Y in range(B0, B0 + 9)]
for i in range(9):
    tiles[A0 + i][SAG_X0:SAG_X1 + 1] = blkB[i]
    tiles[B0 + i][SAG_X0:SAG_X1 + 1] = blkA[i]
# the Ciutadella park and the plain block below it swap (round 21)
PARK_X0, PARK_X1 = 68, 76
P0, Q0 = 58, 71
blkP = [tiles[Y][PARK_X0:PARK_X1 + 1] for Y in range(P0, P0 + 9)]
blkQ = [tiles[Y][PARK_X0:PARK_X1 + 1] for Y in range(Q0, Q0 + 9)]
for i in range(9):
    tiles[Q0 + i][PARK_X0:PARK_X1 + 1] = blkP[i]
    tiles[P0 + i][PARK_X0:PARK_X1 + 1] = blkQ[i]
d['tiles'] = tiles


def in_park(x, y):
    # (the park's block, from its first row down to the street below it: the sign stands on its edge)
    return PARK_X0 <= x < PARK_X1 + 1 and P0 <= y < P0 + 10

# ---- the layout's numbers
d['BCOLS'] = [12, 25, 42, 55, 68]
for v in d['VSTREETS']:
    if v.get('rambla'):
        v['x'] = 34
    elif v['x'] == 34:
        v['x'] = 51
d['VSTREETS'].sort(key=lambda v: v['x'])
d['RAMBLA_PROM'] = [36, 39]
d['SPAWN']['x'] = new_x(d['SPAWN']['x'], 85)       # Sandra wakes on the beach at the foot of La Rambla

# ---- things and people
SWAP_NAMES = {'La Rambla': 'Carrer de Roger de Llúria', 'Carrer de Roger de Llúria': 'La Rambla'}
for o in d['objects']:
    x0 = o['x']
    o['x'] = new_x(o['x'], o['y'])
    if o['type'] == 'lamp' and o.get('text') and x0 in (33, 38, 46, 55):
        # the corner plaques beside the two streets that changed places
        a, b = o['text'].split('\n')
        o['text'] = a + '\n' + SWAP_NAMES.get(b, b)
for b in d['BUILDINGS']:
    if b['block'][0] == 2:
        for k in ('x0', 'fx'):
            b[k] += 4
        for k in ('door', 'front', 'plaqueAt'):
            if k in b:
                b[k]['x'] += 4
    if b['id'] in ('sagrada', 'torro_joan'):
        dy = 13 if b['id'] == 'sagrada' else -13
        b['block'][1] += 1 if dy > 0 else -1
        for k in ('y0', 'fy'):
            b[k] += dy
        for k in ('door', 'front', 'plaqueAt'):
            if k in b:
                b[k]['y'] += dy
for b in d['BUILDINGS']:
    if b['id'] == 'ciutadella':
        b['block'][1] += 1
        for k in ('y0', 'fy'):
            b[k] += 13
        for k in ('door', 'front', 'plaqueAt'):
            if b.get(k):
                b[k]['y'] += 13
for o in d['objects']:
    if o['type'] != 'lamp' and in_park(o['x'], o['y']):     # (not the corner lamps: they stay on the corners)
        o['y'] += 13
# which side of its block each building's door is on (the 2D game has them all south, but two west)
FACES = {'cafe_rambla': 'W', 'cafe_berlin': 'E', 'carrefour': 'E',      # the shops onto La Rambla
         'casa_mila': 'W', 'casa_batllo': 'E',                          # both onto Passeig de Gràcia, as they really are
         'bookshop': 'W', 'upf': 'E'}                                   # onto Girona (the university facing the park)
for b in d['BUILDINGS']:
    if b['id'] in FACES:
        b['face'] = FACES[b['id']]
for n in d['NPCS'].values():
    a = n.get('at')
    if a and a[0] == 'world':
        a[1] = new_x(a[1], a[2])
        if in_park(a[1], a[2]):
            a[2] += 13                                         # (the people in the park go with it)

# ---- Trufa: in a little glade among the trees, two tiles off the forest path (world2d.py clears it)
d['TRUFA']['at'] = ['world', 98, 50]

# ---- inside the Sagrada Família, rebuilt (sagrada_inside.py): Pau by the scaffolding at the Glory end,
# Mercè at the crossing, under the great lantern
d['NPCS']['pau']['at'] = ['int_sagrada', 5, 19]
# (round 42, the user couldn't find the camera mission: Marta stood at a corner of Carrer d'Aragó, 20 m from the house;
# "She should be inside!") Marta inside Casa Batlló, by the big windows of the noble floor; the words say so
d['NPCS']['marta']['at'] = ['int_batllo', 10, 3]
d['NPCS']['marta']['intro'] = "Hi! Marta — photographer, from Seville, and I've been staring at these windows for an hour like they owe me money."
d['MISSIONS']['camera']['obj']['back'] = "Return the camera to Marta inside Casa Batlló"
d['MISSIONS']['camera']['log']['start'] = "Marta, a photographer in Casa Batlló, left her camera in a cupboard at Casa Vicens. Return it to her."
# (round 37) the Sagrada Família's builders in blue overalls, the hill path's in orange (Quim, Toni: north_data.py)
d['NPCS']['pau']['look']['top'] = '#3a62a8'
d['NPCS']['merce']['at'] = ['int_sagrada', 21, 13]

# ---- the university's two floors, laid out afresh (interiors.py builds the new pieces):
#   ground floor: the entrance hall, with a grand stair up to the library at the back, the lecture corner
#     (Prof. Oriol at his lectern), the porter's desk, the department's shelves, the noticeboard, the
#     lost-and-found box, a coffee machine, Pompeu Fabra's portrait and the university's red banners
#   first floor: the library in the old brick water reservoir (the Dipòsit de les Aigües): brick piers
#     and arches, long reading tables under green lamps, the shelves round the walls, the stairwell down
I = d['INTERIORS']
lib_shelves = [o for o in I['int_upf_lib']['objs'] if o[0] == 'libshelf']
old_upf = {o[0]: o for o in I['int_upf']['objs']}
I['int_upf'].update(w=20, h=14, exit=10, floor='marble', wall='#efe6d6', trim='#7a2e2e', name='UPF — Edifici Jaume I')
# (round 23, the user: the stairs in the bottom right corner, a row of windows along the back of the ground floor,
# the room rearranged to suit; the library long rows of shelves, no columns, the stairs bottom right, and lighter)
I['int_upf']['objs'] = [
    ['grandstair', 15.8, 7.8, {'w': 3.8, 'h': 4.8, 'to': 'int_upf_lib', 'dir': 'up', 'arch': 'right', 'landing': 1.4}],
    ['blackboard', 1, 0, {'w': 4, 't': old_upf['blackboard'][3]['t']}],
    ['notice', 5.2, 0, {'w': 1.2, 't': old_upf['notice'][3]['t']}],
    ['banner', 6.6, 0, {'col': '#c8102e'}],
] + [['window', 7.9 + k * 1.75, 0, {'w': 1.2}] for k in range(4)] + [
    ['painting', 15.0, 0, {'art': 'portrait', 't': "Pompeu Fabra (1868–1948), the engineer who gave Catalan its modern grammar and dictionary. "
                                                      "The university is named after him. He looks faintly disappointed by everyone's spelling."}],
    ['deptshelf', 16.4, 1, {'w': 3, 't': old_upf['deptshelf'][3]['t']}],
    ['lectern', 3, 2],
    ['seats', 1.5, 4.6, {'w': 5}], ['seats', 1.5, 6.6, {'w': 5}], ['seats', 1.5, 8.6, {'w': 5}],
    ['chest', 18, 4, {'c': 'upf_lost', 'label': 'Lost & found box'}],
    ['vending', 18.4, 5.7, {'t': "The coffee machine: €0.80 for something brown and hot. Someone has taped a note to it: 'NOT the exam answers. Stop asking.'"}],
    ['porter', 11.6, 10.4, {'w': 2.8, 't': "Consergeria — the porter's desk. A radio murmurs the football, keys hang on numbered hooks, and a sign says "
                                            "'Library ▲ first floor · Aula 10.1 ◀ · Toilets ▶'."}],
    ['sign', 14.4, 7.0, {'t': 'UNIVERSITY LIBRARY — UPSTAIRS ▲\nBiblioteca de la UPF, in the old water reservoir. Reading room open to all. Silence, please.'}],
    ['bench', 9.6, 4.4, {'w': 2}],
    ['plant', 1.2, 11.6], ['plant', 7.6, 11.6],
]
RESERVOIR = ("The library fills the Dipòsit de les Aigües, the park's old water reservoir (Josep Fontserè, 1874–1880): "
             "it once held up a lake on its roof. Now it holds up the reading room.")
I['int_upf_lib'].update(w=20, h=14, exit=None, floor='parquet', wall='#ead6b8', trim='#7a5a3a', name='Biblioteca UPF — the Dipòsit de les Aigües')
# (round 24, the user: "less cluttered. You should be able to walk around the shelves and the tables should be at the
# front with chairs ready for people to read the books. Move the staircase into a corner and make it not such an
# eyesore.") Shelves along the back wall, two free-standing rows with wide aisles all round them; three long reading
# tables across the front, chairs set out either side, books left open on them; the stair down tucked into the
# front-right corner with a wooden balustrade; the librarian's desk beside it.
LIB_TABLES = [2.0, 7.0, 12.0]
I['int_upf_lib']['objs'] = (
    [['stairwell', 17.2, 10.0, {'w': 2.6, 'h': 4.0, 'to': 'int_upf', 'dir': 'down'}]]
    # the ten shelves with their own books first: six along the back wall, four in the first free-standing row
    + [['libshelf', 1 + i * 2.0, 1, dict(lib_shelves[i][3], w=2.0)] for i in range(6)]
    + [['libshelf', 3 + i * 2.0, 4.0, dict(lib_shelves[6 + i][3], w=2.0)] for i in range(4)]
    + [['libshelf', 3 + i * 2.0, 6.6, {'w': 2.0}] for i in range(4)]
    + [['window', 14.3, 0, {'w': 1.4}], ['window', 17.0, 0, {'w': 1.4}]]
    # (round 35, the everything-visit: E at a reading table said only "Nothing unusual.")
    + [['readtable', x, 9.2, {'w': 3, 'h': 1.2, 'books': True,
                              't': ["A long reading table: green lamps, open books, and someone's coat saving a seat since breakfast.",
                                    "A reading table. Under one lamp, a pile of economics past papers, annotated in three colours of pen.",
                                    "A reading table by the window. A pencil case shaped like a croissant has been left behind."][i % 3]}]
       for i, x in enumerate(LIB_TABLES)]
    + [['chair', x + dx - 0.3 + (0.06 if k % 2 else -0.04), y_, {'w': 0.6, 'h': 0.6, 'face': f_}]
       for x in LIB_TABLES for k, dx in enumerate((0.8, 2.2)) for (y_, f_) in ((8.5 - 0.05 * k, 'back'), (10.5 + 0.07 * k, 'north'))]
    + [['libdesk', 13.0, 12.1, {'w': 2.6}],
       ['sign', 16.3, 9.3, {'t': "1st FLOOR — BIBLIOTECA UPF\n▼ Down to the entrance hall.\nNO BOOK LEAVES THIS FLOOR.\n\n" + RESERVOIR}],
       ['plant', 1.0, 12.6], ['plant', 18.6, 1.6]])
d['NPCS']['oriol']['at'] = ['int_upf', 4.6, 3.4]
d['NPCS']['pol']['at'] = ['int_upf', 12.6, 6.6]
d['NPCS']['remei']['at'] = ['int_upf_lib', 14.3, 13.2]
d['NPCS']['cesc']['at'] = ['int_upf_lib', 5.4, 5.4]
# Carrefour: the bottle-return machine stands against the back wall, in the gap between the fridges and the
# shelves (in the 2D game it was a desk with Anna behind it); Anna works the shop floor beside it
for o in I['int_carrefour']['objs']:
    if o[0] == 'pfand':
        o[1], o[2], o[3]['w'] = 8.2, 1, 2.6
d['NPCS']['anna']['at'] = ['int_carrefour', 11.2, 3.6]
# (round 35, the everything-visit: the university's plaque said the reservoir was of the 1880s; the library's own sign
# and the street sign say 1874–1880)
for b_ in d['BUILDINGS']:
    if 'an 1880s reservoir' in b_.get('plaque', ''):
        b_['plaque'] = b_['plaque'].replace('an 1880s reservoir', 'a reservoir of 1874–1880')
# (round 35, the everything-visit: Empar stood on the espresso machine's own spot, so E there was always her; a step
# along her counter, still in reach of anyone at the counter's front)
d['NPCS']['empar']['at'] = ['int_cafe_rambla', 5.6, 2.3]
# (round 35, the user: "The policeman shouldn't follow her away from la rambla") the street he keeps to
d['NPCS']['bofarull']['beat'] = 'Rambla'

# ---- Alice's flat: the window moves left, clear of her wardrobe (round 20: the wardrobe stood in front of it)
for o in I['int_alice']['objs']:
    if o[0] == 'window':
        o[1] = 6

# ---- Sandra's own bicycle (round 20, the user's story): it has been in for a service with Jordi; at the party
# Alessandra asks after it, which starts the mission; Jordi then needs a new chain from Genís before he can
# finish it, and she rides her own bike home
B = d['MISSIONS']['bike']
B.update({
    'name': "Sandra's bicycle",
    'party': ["Oh, and Sandra, how's your bike? Didn't you leave it with Jordi for a service, the mechanic with the stand on Carrer d'Aragó, "
              "just off Passeig de Gràcia? You can't cycle home from parties if your bike's in pieces!",
              "Sandra: My bike! With everything going on I'd completely forgotten. I'll go and pick it up from Jordi."],
    'offer': "Sandra! Your bike, yes, yes, she's here. Tyres pumped, brakes adjusted, gears oiled... and then I lifted off the old chain "
             "and it came apart in my hands. Rust and sand: a beach bike's life. I've ordered a new one, but Genís the courier has it at the "
             "Tibidabo funicular station and he's stuck on his route up there. Could you fetch it? Bring me the chain and she's ready to ride.",
    'accept': "The funicular station is north, past the Diagonal, at the foot of the mountain path. Genís has a cargo bike and a very loud whistle.",
    'remind': "The new chain's with Genís at the funicular station, north of the Diagonal. Your bike's waiting for it.",
    'handoff': "Ah, the chain for Jordi! Here, wrapped in its paper. So it's YOUR bike he's been fussing over all week? Tell him he owes me a coffee. He always owes me a coffee.",
    'obj': {'collect': "Collect your bike from Jordi's repair stand on Carrer d'Aragó (just off Passeig de Gràcia)",
            'fetch': "Fetch the new chain from Genís at the Tibidabo funicular station",
            'back': "Take the chain to Jordi on Carrer d'Aragó"},
    'done': ["That's the one! Give me two minutes... (clink, clack, whirr) ...there.",
             "Your bike, running sweeter than the day you bought her. Press B to hop on. Three times faster than walking, but not indoors, "
             "and not on the sand or in among the trees: keep to the paths and the grass."],
    'log': {'start': "At the party Alessandra asked about my bike: it's been in for a service with Jordi, the mechanic on Carrer d'Aragó "
                     "just off Passeig de Gràcia. Time to go and collect it.",
            'need': "Jordi says my bike needs a new chain. Genís the courier has it for him at the Tibidabo funicular station.",
            'got': "Collected the chain from Genís. Back to Jordi on Carrer d'Aragó.",
            'done': "Jordi fitted the new chain: my bike is back on the road! Press B to ride."},
})
for a in d['ACHIEVEMENTS']:
    if a['id'] == 'bike':
        a['desc'] = "Got your own bike back on the road."
d['ITEMS']['bike_chain']['desc'] = "A new bicycle chain in an oily paper wrap, collected from Genís. Jordi needs it to finish Sandra's bike."
d['NPCS']['jordi']['lines'][1] = "With a bike you're three times faster, but no riding on the sand, the chain hates it, none in among the trees, and none indoors."

# ---- torró for €6 (round 22: €5 until then, the beach's five bottles exactly; now she needs a mushroom too)
for sh in d['SHOPS'].values():
    sh['items'] = [[i, 600 if i in ('torro_joan', 'torro_mar') else p] for i, p in sh['items']]

# ---- the missions' names (round 22, the user: "give the missions names like 'Find x's lost dog'"); `was` is
# the old name, which journals saved before then carry
NAMES = {'home': "Find your way home", 'gift': "Buy Alessandra a birthday present", 'dog': "Find Montse's lost dog",
         'bike': "Get your bike back from Jordi", 'crema': "Bring Pau a crema catalana", 'brush': "Find Carme's lost brush",
         'profbook': "Fetch Prof. Oriol's book", 'flour': "Bring Ferran a sack of rye flour",
         'rivalry': "Buy Joan his rival's torró", 'hat': "Find Tomàs's lost cap", 'camera': "Fetch Marta's forgotten camera",
         'grail': "Find Ponç's long-lost book", 'exam': "Pass Prof. Oriol's final exam"}
for k, n in NAMES.items():  # (thief, guell: new in round 22, named below)
    d['MISSIONS'][k]['was'] = d['MISSIONS'][k]['name']
    d['MISSIONS'][k]['name'] = n

# ---- two ways to earn money (round 22): Rosa's tip names both, the bottles and the forest's three rare red
# mushrooms, which Guillem buys (€5). The little white mushrooms all through the wood are only to look at.
d['PFAND_TIP'] = ("Short of money? Two secrets. One: those empty bottles on the beach are worth a euro each at the Pfand desk "
                  "in Carrefour Express, on the Gran Via. Very German, very useful. Two: somewhere deep in the forest, well away "
                  "from the paths, grow rare red mushrooms, and Guillem, the mushroom hunter by the forest path, pays five euros "
                  "for every one.")
d['ITEMS']['red_mushroom'] = {'name': 'Red mushroom', 'kind': 'collect', 'icon': 'red_mushroom',
                              'desc': 'A rare red mushroom, white-spotted, from deep in the forest. Lovely to look at, never to eat. Guillem pays €5 for one.'}
G_ = d['NPCS']['guillem']
G_['mushrooms'] = True
G_['lines'][1] = ("The little white ones are everywhere, and not worth the basket. The red ones are rare: three spots I know of, "
                  "deep in, well off the paths. Bring me one and I'll pay five euros.")

# ---- catching the pickpocket (round 22, the user: after Manolo has picked her pocket, Agent Bofarull follows her at a
# distance; she talks to Manolo again; the agent runs over, handcuffs him and gives her things back. Once she has
# been in and out of a building, Manolo is gone and the agent is back at his fountain, grateful)
d['MISSIONS']['thief'] = {
    'name': "Catch the Rambla pickpocket",
    'obj': {'lead': "Talk to Manolo on La Rambla as if nothing had happened: Agent Bofarull is following"},
    'report': ["Let me guess: dark jacket, big smile, calls everyone 'guapa', warned you about pickpockets? (He sighs.) Manolo. "
               "I know Manolo extremely well. We have a... long relationship.",
               "The trouble with Manolo is that by the time anyone reports him, he's emptied his pockets. So we do it the other way round. "
               "Go back and talk to him, nice and friendly, as if you hadn't noticed a thing. I'll follow, a little way behind. "
               "Don't look round at me: he notices everything."],
    'tailing': ["Keep walking, keep walking. Don't look at me. I'm just a man admiring a lamp post.",
                "La Rambla, the man in the dark jacket. Go on, I'm right behind you."],
    'catch': [["Manolo", "Guapa! You came back! Nobody ever comes back. What can I do for my favourite visitor: a tip, a shortcut, "
                         "a little... (his eyes slide past her shoulder, and the smile goes stiff)"],
              # (round 41, the user: "there's a text that says agent [Bofarull] covers the last [few metres]… This is not
              # necessary. That can be seen")
              ["Agent Bofarull", "Manolo Ferrer. Again. Hands behind your back, you know how this goes."],
              ["Manolo", "Agent! What a coincidence. I was just recommending the Boqueria to this young lady."],
              ["Agent Bofarull", "Were you. Inside pocket, the left one. Slowly."],
              ["", "Out of Manolo's jacket come Sandra's things, one after another, and a great many of other people's besides: wallets, "
                   "two phones, a hotel key and a guide to the Sagrada Família in Japanese."],
              ["Agent Bofarull", "Busy morning, Manolo."],
              ["Manolo", "Tourism is up this year. Everybody says so."],
              ["Agent Bofarull", "The van will be along in a minute, and you can tell the judge all about tourism. (To Sandra) "
                                 "And thank you. You kept very calm. Most people march up and shout at him, and he's three streets away "
                                 "before they've finished."]],
    'after': "The van's on its way. Go on, enjoy your day: I'll keep an eye on our friend here.",
    'manolo_cuffed': "(Manolo, in handcuffs, gives Sandra a wounded look.) Guapa. And I thought we were friends.",
    'log': {'start': "Manolo, the charming man on La Rambla, picked my pocket. Agent Bofarull wants to catch him with my things on "
                     "him: I'm to talk to Manolo again, as if nothing had happened, while he follows at a distance.",
            'done': "Agent Bofarull caught Manolo red-handed on La Rambla and handcuffed him. I got my things back, and a thank-you."},
}
d['NPCS']['bofarull']['thanks'] = [
    "The people and the tourists of Barcelona are grateful for your help. Manolo is having a long talk with a judge.",
    "Twelve wallets went home this week thanks to you. The people and the tourists of Barcelona are grateful for your help."]

# ---- the final exam (round 22, the user: no quiz; the screen fades, a montage of Sandra writing at a desk in front
# of the professor, dark again, and he tells her she has passed). It waits for every mission, the north's too.
d['MISSIONS']['exam']['log']['start'] = "Prof. Oriol says it is time for my final exam on the Rambla Guide to Economics."
d['ORIOL_STATES']['ready'] = "It is time for your final exam, Sandra. One paper, one hour, everything from the Rambla Guide."
d['ORIOL_STATES']['begin'] = "Take a seat in the front row. You may turn over your paper... now."
d['ORIOL_STATES']['passed'] = ["Pencils down.",
                               "(Prof. Oriol reads her paper through at the lectern, slowly. Halfway down the second page his eyebrows go up, and they stay up.)",
                               "Sandra. You have passed, and handsomely. The Universitat Pompeu Fabra Diploma of Economics is yours."]

# ---- the north, round 22 (north_data.py): its people, missions, items and rooms
exec(open(os.path.join(HERE, 'north_data.py')).read())

# ---- round 23: Jordi's shop, the party, Montse, the wildflowers and other words (round23_data.py)
exec(open(os.path.join(HERE, 'round23_data.py')).read())

# ---- (round 25, the user: "Remove the achievements. I don't want everything to become a competition. Only the missions
# are counted like that.") none: the journal has just its one page, and nothing pops up
d['ACHIEVEMENTS'] = []

# ---- round 38, the user's words on the talk: Sandra has no lines in a conversation (rule 10 #52) — her yes to a mission
# is gone (game.gd offer_mission), the party's bike question needs no answer, her thoughts are the narrator's; Jordi
# talks less ("I fixed X and Y, but I still need to wait for the new chain… you already paid when you dropped it off");
# Rosa's tip is shorter, with a bin for a bottle now and then ("Sometimes you also find one in a trash can")
B38 = d['MISSIONS']['bike']
B38['party'] = ["Oh, and Sandra, how's your bike? You left it with Jordi for a service, didn't you, at Bicis Jordi on Carrer de "
                "València? Don't forget to pick it up!"]
B38['offer'] = "Sandra! I've fixed the brakes and the gears, but I still need to wait for the new chain."
# (round 40, the user: "move the guy who has the bike chain up into the second square in the new part… the upper one
# that's surrounded by all the square buildings": Genís waits in the Plaça de la Vila now, north_data.py)
B38['accept'] = ("Genís the courier has it. He takes his break in the Plaça de la Vila, the square in the middle of Gràcia's "
                 "upper streets. If you fetch it and bring it back to me, your bike will be ready a lot faster.")
B38['remind'] = "The new chain's with Genís, in the Plaça de la Vila up in Gràcia. Bring it back and your bike's ready."
B38['done'] = ["That's the one! (clink, clack, whirr)",
               "You already paid when you dropped it off, so now you're ready to go. Press B to hop on."]
d['NPCS']['jordi']['waiting'] = "Hello, Sandra! I'm still working on your bike. Check back with me later."
d['MISSIONS']['gift']['think'] = "Alessandra loves torró. The torró shops sell it for €6... and Sandra's purse is empty."
d['PFAND_TIP'] = ("Short of money? Take the empty bottles from the beach back to Carrefour Express on the Gran Via: a euro "
                  "each. Sometimes there's one in a paperera, a bin, too. And Guillem, by the forest path, pays five euros "
                  "for the rare red mushrooms deep in the wood.")
d['MISSIONS']['guell']['clue_crate'][2] = "The initial P, and a gardener's gloves. Mercè will want to see this."

# (round 38, the user: after the party Alessandra stands in the middle of the room, facing you: npcs.gd enter_room)
d['NPCS']['alessandra']['after_at'] = [6.0, 4.1]

# (round 38, the user: "Make it the ou de reig: orange-red, no spots, good to eat") the pickable mushroom is Catalonia's
# prized Caesar's mushroom, not a fly agaric; Guillem buys them because they're worth eating
d['ITEMS']['red_mushroom']['name'] = 'Ou de reig'
d['ITEMS']['red_mushroom']['desc'] = ("An ou de reig, the \"king's egg\": a rare orange-red mushroom with yellow gills, from deep in "
                                      "the forest. Prized in Catalonia, and very good to eat. Guillem pays €5 for one.")
# (round 41, the user: "It should be really short and she should just note it. You can collect bottles on the beach and
# return them for the Pfand. So-and-so on the beach buys seashells… so-and-so in the forest is known to buy rare
# mushrooms. It should just be simple like that") — and Sandra writes it in her journal (story.gd read_card, MONEY_NOTE)
d['PFAND_TIP'] = ("Short of money? Collect the bottles on the beach and take them back to Carrefour Express for the Pfand. "
                  "Salva on the beach buys seashells. And Guillem, by the forest path, buys rare mushrooms. Sometimes you "
                  "also find lost coins in the street, which you're allowed to keep.")
d['MONEY_NOTE'] = ("Money: bottles from the beach back to Carrefour Express for the Pfand. Seashells to Salva, on the beach. "
                   "Rare mushrooms to Guillem, by the forest path. Lost coins in the street: mine to keep.")
d['NPCS']['guillem']['lines'][1] = ("The little white ones are everywhere, and not worth the basket. But the ou de reig, the "
                                    "king's egg, orange-red and gold underneath: that's a prize. Three spots I know of, deep in, "
                                    "well off the paths. Bring me one and I'll pay five euros.")

# ---- (round 39, the user: "why are they all wearing hats. Get rid of the hats. No one wears these ridiculous hats
# anymore.") no one wears a hat for the sake of it: only the hats that go with a job — the police and the guard's caps,
# the workmen's hard hats (part of their own model). Tomàs's cap (once Sandra brings it back) and the birthday girl's
# party hat are put on by the game itself (npcs.gd), and Sandra's own hats are things she wears.
KEEP_HATS = ('police', 'guard', 'hardhat')
for _id, _n in d['NPCS'].items():
    _lk = _n.get('look', {})
    if _lk.get('hat') and _lk['hat'] not in KEEP_HATS:
        _lk.pop('hat')
        _lk.pop('hatc', None)

# ---- (round 41, the user: "give all the different people different colored clothes… some of the people are wearing the
# same color. You can mix and match all you please") every named person a top of their own, chosen far apart in how the
# eye sees colour (CIE Lab), with trousers that stand off it; the uniforms keep theirs (the police, the guard, the two
# workmen's crews, the statue, Rosa in her own model). The passers-by deal from the next colours in the same spread
# (WALKER_LOOKS, people.gd), so no one in the street matches anyone else either.
import colorsys, random as _rnd


def _lab(hx):
    c = [int(hx[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    r, g, b = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    X, Y, Z = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, 0.2126 * r + 0.7152 * g + 0.0722 * b, \
        (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    return (116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z)))


def _de(a, b):
    return sum((x - y) ** 2 for x, y in zip(_lab(a), _lab(b))) ** 0.5


def _hex(h, s, v):
    return '#%02x%02x%02x' % tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(h, s, v))


KEEP_CLOTHES = ['pau', 'bofarull', 'sergi', 'quim', 'toni', 'iu', 'rosa']
SKINS = ['#dca57c', '#efc3a0', '#b97f55', '#f7d7bd', '#e8b48e', '#efd2b0', '#8d5a3b']
# (round 41, the user, of a man in bright purple: "I also don't like his shirt. Can it be a more pastel color?" — every top
# from soft, pale colours now, with a few deeper muted ones; no strong, saturated colour)
# (then: "there are too many people especially around the university in purple shirts… Just some normal pastel colors…
# a sort of dry green, dry brown, even a white, dry blue, dry aqua") only those families: dusty greens, sandy and
# earthy browns, blues and aquas, soft and dry (low colour), and whites and greys — no purples, pinks or reds
_SV = ((0.12, 0.90), (0.18, 0.84), (0.24, 0.78), (0.30, 0.70), (0.26, 0.60), (0.22, 0.50))
_FAMILIES = [(range(70, 150, 4), _SV),                    # dry greens
             (range(22, 46, 3), _SV),                     # dry browns and sand
             (range(165, 197, 4), _SV),                   # dry aquas
             (range(198, 230, 4), _SV)]                   # dry blues
_cand = [_hex(hh / 360.0, s_, v_) for (hs_, sv_) in _FAMILIES for hh in hs_ for (s_, v_) in sv_]
_cand += ['#f2efe8', '#d9d6cf', '#a6a39e', '#6e6c69', '#3a3937', '#1f1f22']
_cand = [c for c in _cand if min(_de(c, k) for k in SKINS) > 14]              # (never a top that reads as bare skin)
_taken = [d['NPCS'][k]['look']['top'] for k in KEEP_CLOTHES if d['NPCS'].get(k, {}).get('look', {}).get('top')]
_dress = sorted(k for k, n in d['NPCS'].items() if n.get('look', {}).get('top') and k not in KEEP_CLOTHES)
_picks = []
while len(_picks) < len(_dress) + 48:                     # (48: more than the street ever holds at once)
    _best = max(_cand, key=lambda c: min(_de(c, t) for t in _taken + _picks) if _taken + _picks else 999)
    _picks.append(_best)
    _cand.remove(_best)
LEGS_ALL = ['#1f2a44', '#2f3a5a', '#3e4b6b', '#4a6a8a', '#2d2a2a', '#3c3b45', '#5a5a62', '#8a8378', '#c8b98f', '#e8dccb',
            '#6b4226', '#4a3a2a', '#556b2f', '#7a2a3a', '#f2efe8', '#2b4a3a']
_r = _rnd.Random(41)
_mine = _picks[:len(_dress)]
_r.shuffle(_mine)                                        # (so neighbours in the alphabet aren't neighbours in colour)


def _legs_for(top, i):
    ok = [l for l in LEGS_ALL if _de(l, top) > 28]
    return ok[(i * 7) % len(ok)]


for _i, _k in enumerate(_dress):
    _lk = d['NPCS'][_k]['look']
    # (which of a body's two models someone gets is chosen from their old colours, npcs.gd variant(): kept, so the
    # story's people keep their faces — Mercè her red bun and glasses)
    _lk['vkey'] = _lk.get('top', '') + _lk.get('hair', '') + _lk.get('legs', '') + _lk.get('hs', '')
    # (the user, of the shopkeepers' painted aprons: "You can just get rid of them and have their shirts and pants")
    if _lk.pop('apron', None) is not None:
        _lk['settled'] = True                            # (an apron made a man the older, stouter one: still him)
    _lk['top'] = _mine[_i]
    _lk['legs'] = _legs_for(_lk['top'], _i)
# (the user, of three women in the lineup: "The shirts are just a bit too bright. Make them a bit more normal") each
# a muted shade near her own hue, the one standing furthest from everyone else's
for _k in ('empar', 'alba', 'nuria'):
    _lk = d['NPCS'][_k]['look']
    _h = colorsys.rgb_to_hsv(*[int(_lk['top'][i:i + 2], 16) / 255.0 for i in (1, 3, 5)])[0]
    _others = [d['NPCS'][k]['look']['top'] for k in _dress if k != _k] + _taken
    _opts = [_hex((_h + dh / 360.0) % 1.0, s_, v_) for dh in range(-24, 25, 4) for s_ in (0.22, 0.3, 0.38)
             for v_ in (0.5, 0.58, 0.66, 0.74)
             if any(int(round(((_h + dh / 360.0) % 1.0) * 360)) in hs_ or hs_.start <= ((_h + dh / 360.0) % 1.0) * 360 <= hs_.stop
                    for (hs_, _) in _FAMILIES)]          # (round 41: within the dry families still)
    _lk['top'] = max(_opts, key=lambda c: min(_de(c, o) for o in _others))
    _lk['legs'] = _legs_for(_lk['top'], _dress.index(_k))
# the street's colours: none near anyone named (refilled from what's left)
_named = [d['NPCS'][k]['look']['top'] for k in _dress] + _taken
_street = [c for c in _picks[len(_dress):] if min(_de(c, o) for o in _named) >= 12]
while len(_street) < 48:
    _best = max(_cand, key=lambda c: min(_de(c, t) for t in _named + _street))
    _street.append(_best)
    _cand.remove(_best)
d['WALKER_LOOKS'] = [[t, _legs_for(t, i + 3)] for i, t in enumerate(_street)]
_all = [d['NPCS'][k]['look']['top'] for k in _dress] + [w[0] for w in d['WALKER_LOOKS']]
print('clothes: %d people dressed, %d street colours, closest pair %.1f apart' % (len(_dress), len(d['WALKER_LOOKS']),
      min(_de(a, b) for i, a in enumerate(_all) for b in _all[i + 1:] + _taken)))

# (round 41, the user: "Could you remove the glasses from the people? They look creepy") the two rings drawn round the
# eyes are gone from everyone; glasses that are part of a model's own head (the older men, the older lady) stay
for _n in d['NPCS'].values():
    _n.get('look', {}).pop('glasses', None)

# ---- (round 41, the play-through's review of the world, the user's answers point by point; rule 10 #51–51c) words
# that disagreed with the world, with each other or with the real Barcelona. Each swap asserts its old words are
# there, so a later change to them shows up here instead of being silently missed.
def _swap(holder, key, old, new):
    assert old in holder[key], (key, old)
    holder[key] = holder[key].replace(old, new)


_N, _M, _I = d['NPCS'], d['MISSIONS'], d['ITEMS']
# 1. the café is east of La Rambla (its block is the next column east; its door faces La Rambla)
_swap(_M['crema'], 'accept', "just west of the Rambla on València", "on València, just east of the Rambla")
# 2. Alba's flat is two blocks up from the Ciutadella, not across from it (the park moved down a block, round 21)
_swap(next(b for b in d['BUILDINGS'] if b['id'] == 'apt_alba'), 'plaque', "across from the Ciutadella",
      "two blocks up from the Ciutadella")
_swap(_N['alba'], 'intro', "I live across from the Ciutadella so I can pretend the whole park is my garden",
      "I live two blocks up from the Ciutadella, close enough to pretend the whole park is my garden")
_G = _M['grail']
_swap(_G, 'offer', "a student who lives by the Ciutadella", "a student who lives near the Ciutadella")
_swap(_G, 'accept', "By the Ciutadella, on València.", "On València, two blocks up from the Ciutadella.")
_swap(_G, 'remind', "The student by the Ciutadella.", "The student near the Ciutadella, on València.")
_swap(_G['obj'], 'find', "the student by the Ciutadella", "the student near the Ciutadella")
_swap(_G['log'], 'start', "A student by the Ciutadella", "A student near the Ciutadella")
# (round 41, the user: "the bookseller talks about a young girl who's got one and she trades in flowers. Don't say that.
# That's preempting the rest of the mission. Just say, can you visit her, convince her to sell"; "He mentions flowers
# twice. Don't") no word of flowers before Sandra meets her
_swap(_G, 'offer', " \u2014 a young woman who, they say, trades in flowers, not euros. If you could persuade her, I would give you "
      "something rare in return.", ". Could you visit her, and persuade her to sell it? I would give you something rare in return.")
_swap(_G, 'remind', "She trades in flowers.", "Visit her, persuade her to sell.")
_swap(_G, 'accept', " Flowers, remember \u2014 not euros.", "")
_swap(_G['log'], 'start', " \u2014 and trades in flowers.", ": I'm to visit her and persuade her to sell.")
# 3. Manolo's top since the round-41 recolouring: (the user: "the pickpocket has a light green shirt. Could you make it
# slightly darker? And then the policeman refers to [an] old purple shirt") a muted mid green, and the words say so
d['NPCS']['manolo']['look']['top'] = '#b5c48c'
_swap(_M['thief']['report'], 0, "dark jacket", "green shirt")
_swap(_M['thief']['tailing'], 1, "the man in the dark jacket", "the man in the green shirt")
# (round 41, the user: "he should be facing the water, almost all the time. But not too close to it, so his feet are
# getting wet. But the rod should be over the water") Tomàs a little up the sand from the water's edge (there the coast
# curve's z 147.2), facing it (yaw 0: south); after a chat he turns back to it (npcs.gd home_yaw)
_N['tomas']['at'] = ['world', 23, 88.75]          # (then: "closer to the water": 1.1 m from it)
_N['tomas']['yaw'] = 0.0
# 4. the chat in which he robs her is his warning (story.gd manolo_talk)
_N['manolo']['warn'] = _N['manolo']['lines'][1]
assert 'pickpockets' in _N['manolo']['warn']
# 5. her street is two streets east of La Rambla, past Roger de Llúria (people.gd: the Born line is gone too)
_swap(d['INTRO_TEXT'], 4, "Your street, Flor del Iliri, is just east of it.",
      "Your street, Flor del Iliri, is just east of it, past Carrer de Roger de Llúria.")
# 6. Genís takes his break in the Plaça de la Vila (round 40), not at Park Güell
_swap(_N['genis']['lines'], 0, "Deliveries all over Gràcia, then up here to Park Güell.",
      "Deliveries all over Gràcia, and my break here in the Plaça de la Vila.")
_swap(_N['genis']['lines'], 2, "Everyone photographs the dragon.", "Everyone photographs the dragon up in Park Güell.")
# 7. once the bike is back, Alessandra asks how she likes it (game.gd moment())
_BQ = "How is your bike going? You took it to Jordi for repairs, right? He's the one on Carrer de València, between Passeig de Gràcia and La Rambla."
assert _BQ in _N['alessandra']['lines']
_N['alessandra']['once_done'] = {'bike': [_BQ, "How are you enjoying the bike? Barcelona's twice the size on two wheels "
                                                "— and every hill twice as steep."]}
# 8. the ball lay in the forest (rule 43: no ledge)
_swap(_M['ball']['log'], 'got', "on a ledge in the wood", "in the forest")
# 10. why Sandra fetches the flowers, in the user's words (rule 10 #44)
_G['albaAsk'] = ("'The Bookseller's Ghost'? Mm, I have it — it's right there on my table. I don't need the book, but what I "
                 "do need are some flowers to fill this empty vase. They grow on the slopes above the city, along the path "
                 "up to Tibidabo, but I'm not much of a hiker. Bring me five and it's yours.")
# the spirit level (rule 10 #16d, the user: "find the workman who had lost their tool… she gives the tool back. Then it
# fades to black and then fades back and the barrier has been pushed to the side then they say…"): no waiting indoors
_L = _M['level']
_L['obj'] = {'find': "Find the workmen who lost their spirit level",
             'give': "Give the level to Toni, at the workmen's barrier at the foot of the path"}
assert _L['give'][0].startswith("Our level!")
_L['give'] = [_L['give'][0]]
_L['open'] = "Thank you. We were able to finish the work with this tool. You are free to go through."
_L['thanks'] = ["Thanks again for our level, Sandra. Every step up there is dead straight now.",
                "You're the one who brought our level back! The path's all yours. Mind the steep bits."]
_L['log'] = {'start': _L['log']['start'],
             'done': "Gave the workmen back their level. They finished the steps, and the path up the hill is open."}
_L.pop('finished', None)
# 11. small slips
_swap(_M['gift'], 'noMoney', "Que bonic", "Què bonic")
_swap(_I['vollkorn'], 'desc', "eleven hundred miles south", "eleven hundred kilometres south")
_swap(_N['oriol']['lines'], 0, "which makes it a teenager among universities", "which makes it a youngster among universities")
_I.pop('balloon')                                   # (Laia and her mission went in round 22; her balloon with them)
# no season (rule 10 #51a; the user: "Nothing should refer to a season. It should just be exam complete")
_swap(d['EAT_MSG'], 'torro_joan', "Christmas in a single bite, three months early.", "Christmas in a single bite.")
_swap(d['IDLE_LINES'], 'post', "Semester complete!", "Exam complete!")
# (round 41, rule 10 #34a, the user: "keep things on one line… use the term people. Not folks")
_swap(d['IDLE_LINES'], 'explore', "Explore Barcelona — plenty of folk could use a helping hand",
      "Explore Barcelona — there's lots to see and do")
_swap(d['IDLE_LINES'], 'study', "You have seen most of the city. Time to study — Prof. Oriol is at UPF",
      "Time to take the exam. See Professor Oriol at UPF.")     # (the user: "make it more clear")
_swap(_M['exam']['log'], 'done', "Semester complete", "Exam complete")
# the rest of the review (the user: "work through them")
_swap(_N['joan'], 'intro', "on this very spot when the Rambla still had horses", "on this very spot when the streets still had horses")
_swap(_N['xavi']['lines'], 2, "below it the city tumbles down towards the old districts and the sea",
      "below it there's only the promenade, the beach and the sea")
_swap(_N['ramon']['lines'], 1, "Forty years I've worked this hill.", "Thirty-five years I've worked this hill.")
_swap(_N['guillem']['lines'], 2, "I've hunted for forty years and I still carry the book.",
      "I've hunted since I was a boy and I still carry the book.")
_swap(_N['quima']['lines'], 1, "Bottles wash up on the western half of the beach and shells on the eastern.",
      "Bottles and shells wash up all along this beach.")
_swap(_N['mireia']['lines'], 0, "the great cascade fountain at its far end", "the great cascade fountain, just there")
_swap(_N['roser']['lines'], 0, "Collserola is home to", "These woods are home to")
_swap(_N['fiona']['lines'], 2, "This whole square was meant as a market place. Imagine buying your tomatoes up here.",
      "The hall of columns under this square was built for a market. Imagine buying your tomatoes down there.")
_swap(_M['profbook'], 'handoff', "I've put a get-well card in it as a bookmark. Tell him it's a thank-you.",
      "I've kept his place with one of my get-well cards. Tell him thank you for the loan.")
_swap(_M['profbook']['done'], 0, "And annotated with...", "And bookmarked with...")
_swap(d['INTERIORS']['int_mnac']['objs'][5][3], 't', "and a very empty brush-shaped space", "and a rack of fine sable brushes")

# (round 41, the user: "The mother and Biel should thank Sandra for finding the ball when she speaks to them again. And
# then after cycling through other things that they say, they should come back to that") a thank-you, said first the
# next time, then in their turn (game.gd `after_mission`)
_N['rosalia']['after_mission'] = {'ball': "Thank you again for the ball. He hasn't let go of it since — he sleeps with it."}
_N['biel']['after_mission'] = {'ball': "You got my BALL! From all the way down the HILL! You're the best at finding things."}

# (round 41, the user: "the workmen should be strolling around a bit. Not just facing downhill. Sort of pacing") a little
# wander each: Quim about the site, Toni by his barrier
_N['quim']['r'] = 0.9
_N['toni']['r'] = 0.45

# ---- words that no longer fit
# (round 41, the user: "instead of calling it old spare camera, could you actually call it the model name? It's fine
# that she calls it her old spare camera. And then you find out what it is when you go look at it in your backpack")
_I['camera']['name'] = 'Pentax K1000'
# (then: "You don't have to say Marta's old spare camera once it's in the backpack… it's Pentax K1000. And then
# there's just some text about it")
# (then, with the camera's 1.5× zoom: "Do option one" — a Pentax zoom lens of the time, 28–80 mm, which reads 50 mm
# and 75 mm zoomed)
_I['camera']['desc'] = ("A sturdy all-metal film camera with a 28–80 mm zoom lens and a light-meter needle in the "
                        "viewfinder. With it on you, you can take a picture anytime.")

# ---- the top-left step, one line each (rule 10 #34; round 41c, the user: "make it as long as it can be without going
# on to the next line… You don't need the brackets"; each measured at under ~505 px in the game's font at size 19)
ONE_LINE_STEPS = {
    'home': {'go': "Find your flat on Flor de Lliri"},
    'gift': {'buy': "Buy torró for Alessandra's birthday",
             'party': "Take the torró to Alessandra's on Passeig de Gràcia"},
    'dog': {'find': "Find Trufa in the eastern forest",
            'back': "Bring Trufa back to Montse on La Rambla"},
    'bike': {'collect': "Collect your bike from Bicis Jordi on Carrer de València",
             'fetch': "Fetch the new chain from Genís in the Plaça de la Vila",
             'back': "Take the chain to Jordi's shop on Carrer de València"},
    'crema': {'buy': "Buy a crema catalana at Cafè de la Rambla",
              'back': "Take the crema catalana to Pau at the Sagrada Família"},
    'brush': {'find': "Find Carme's brush near the Cascada in the Ciutadella",
              'back': "Return the brush to Carme at the MNAC"},
    'profbook': {'fetch': "Collect Prof. Oriol's book from Alice on Carrer Balmes",
                 'back': "Return the textbook to Prof. Oriol at UPF"},
    'flour': {'buy': "Buy rye flour at Carrefour Express on the Gran Via",
              'back': "Deliver the rye flour to Ferran at Cafè Berlín"},
    'rivalry': {'buy': "Buy a bar of torró at Torrons del Mar",
                'back': "Bring the rival torró to Joan at Casa Joan"},
    'hat': {'find': "Find Tomàs's cap at the eastern forest edge",
            'back': "Return the cap to Tomàs on the beach"},
    'camera': {'fetch': "Fetch Marta's camera from a cupboard in Casa Vicens",
               'back': "Return the camera to Marta inside Casa Batlló"},
    'grail': {'find': "Find the student near the Ciutadella with Ponç's book",
              'flowers': "Bring Alba five wildflowers",           # (the game adds the count, "(2/5)")
              'back': "Take 'The Bookseller's Ghost' to Ponç at El Drac"},
    'exam': {'sit': "Sit the economics exam with Prof. Oriol at UPF"},
    'thief': {'lead': "Talk to Manolo on La Rambla as if nothing happened"},
    'guell': {'look': "Find out where the Salamandreta went in Park Güell",
              'key': "Find what the brass key tagged T·S opens",
              'back': "Take the Salamandreta to Mercè at Casa Museu Gaudí"},
    'ball': {'find': "Find Biel's ball in the wood below the funfair",
             'back': "Take the ball back to Biel at the funfair"},
    'level': {'find': "Find the workmen who lost their spirit level",
              'give': "Give the level to Toni at the barrier by the path's foot"},
}
# (round 41c, the user: the brush lies on the gravel now, so her journal says so too)
assert d['MISSIONS']['brush']['log']['got'] == "Found Carme's brush in the grass by the Cascada. Back to the MNAC."
d['MISSIONS']['brush']['log']['got'] = "Found Carme's brush on the gravel by the Cascada. Back to the MNAC."
# (then: "Could you change her hints? Just say that she left it somewhere in the park") Carme doesn't know where it fell
_B = d['MISSIONS']['brush']
assert _B['offer'].startswith("I've lost my best sable brush — the tiny one") and 'rolled into the grass' in _B['offer']
_B['offer'] = ("I've lost my best sable brush — the one with C.F. scratched on the handle. I was sketching the Cascada "
               "in the Ciutadella yesterday and I must have left it somewhere in the park. I can't restore a halo with a "
               "broom. Would you look for it?")
assert _B['remind'] == "Any luck with my brush? It'll be somewhere in the grass near the Cascada, in the Ciutadella."
_B['remind'] = "Any luck with my brush? I must have left it somewhere in the Ciutadella, where I was sketching the Cascada."
# (round 41c, the user: "why is this person golden and stuck next to the tree?") Iu, the Rambla's living statue, stood
# 0.4 m from a plane tree's trunk on the promenade's east row; now in its middle, 3.7 m clear of the trees and 4.7 m
# from Miró's mosaic
assert d['NPCS']['iu']['at'] == ['world', 39, 62]
d['NPCS']['iu']['at'] = ['world', 38.0, 62]
for _k, _steps in ONE_LINE_STEPS.items():
    assert set(_steps) == set(d['MISSIONS'][_k]['obj']), (_k, sorted(d['MISSIONS'][_k]['obj']))
    d['MISSIONS'][_k]['obj'].update(_steps)
assert set(ONE_LINE_STEPS) == set(d['MISSIONS'])

# (round 41c, the user: "Change the child to a girl. Is Biel a girl's name?" — it isn't: Catalan for Gabriel; she is
# Laia again, as before round 22, the user's pick) the name everywhere, and he/him/his to she/her where they mean her —
# only in the lines about her (her own lines keep the statue's "his arms open… he's hugging")
import re as _re


def _to_laia(t_, pron=True):
    t_ = t_.replace('Biel', 'Laia')
    if pron:
        for a_, b_ in (('He', 'She'), ('he', 'she'), ('Him', 'Her'), ('him', 'her'), ('His', 'Her'), ('his', 'her')):
            t_ = _re.sub(r'\b%s\b' % a_, b_, t_)
    return t_


def _walk(o_, pron=True):
    if isinstance(o_, str):
        return _to_laia(o_, pron)
    if isinstance(o_, list):
        return [_walk(v_, pron) for v_ in o_]
    if isinstance(o_, dict):
        return {k_: _walk(v_, pron) for k_, v_ in o_.items()}
    return o_


_L = d['NPCS']['biel']
_L['name'] = 'Laia'
_L['intro'] = _to_laia(_L['intro'], False)
_L['after_mission'] = _walk(_L['after_mission'], False)
_R = d['NPCS']['rosalia']
assert _R['lines'][1].startswith('Biel would live up here if I let him')
_R['lines'][1] = _to_laia(_R['lines'][1])
_R['after_mission'] = _walk(_R['after_mission'])
d['MISSIONS']['ball'] = _walk(d['MISSIONS']['ball'])
d['MISSIONS']['level']['log'] = _walk(d['MISSIONS']['level']['log'])
for _k in ('ball', 'spirit_level'):
    d['ITEMS'][_k] = _walk(d['ITEMS'][_k])
assert d['MISSIONS']['ball']['done'][0].startswith('MY BALL! (She hugs it.)')
d['MISSIONS']['ball']['done'][0] = d['MISSIONS']['ball']['done'][0].replace('(She hugs it.)', '(Laia hugs it.)')   # (not Sandra)
# (then the user's pick of three for Toni, who left it there himself)
d['MISSIONS']['level']['give'] = ["Our level! A little girl found it leaning on a wall down the path? (Toni scratches his head.) "
                                  "...That's exactly where we left it."]
assert 'Biel' not in json.dumps(d, ensure_ascii=False), 'Biel left somewhere'

s = json.dumps(d, ensure_ascii=False)
for a, b in (('€12', '€6'), ('twelve euros', 'six euros'), ('€12 a bar', '€6 a bar')):
    s = s.replace(a, b)
s = s.replace('Find your flat on Flor del Iliri (just east of La Rambla)',
              'Find your flat on Flor del Iliri (east of La Rambla, just past Roger de Llúria)')
s = s.replace('Our little street is just off La Rambla', 'Our little street is a short walk from La Rambla')
# the street's real name (rule 10 #51d): Carrer de la Flor de Lliri, in the Born, named after a 1444 inn
s = s.replace("Flor del Iliri means 'lily flower'. Our little street is a short walk from La Rambla",
              "Flor de Lliri means 'lily flower'. The name's borrowed from an old street in the Born, where an inn with a "
              "big painted lily on its sign opened in 1444. Ours is a short walk from La Rambla")
assert "Flor de Lliri means" in s
s = s.replace('Flor del Iliri', 'Flor de Lliri').replace('FLOR DEL ILIRI', 'FLOR DE LLIRI')
assert 'Iliri' not in s and 'ILIRI' not in s
open(os.path.join(HERE, 'data3d.json'), 'w').write(s)

# ---- the map picture (8 pixels to a tile)
im = Image.open(os.path.join(HERE, 'map2d.png')).convert('RGB')
out = im.copy()
P = 8
for X in range(MW):
    sx = src_col(X)
    if sx != X:
        out.paste(im.crop((sx * P, ROW0 * P, sx * P + P, (ROW1 + 1) * P)), (X * P, ROW0 * P))
out.paste(im.crop((49 * P, 86 * P, 53 * P, 87 * P)), (36 * P, 86 * P))
out.paste(im.crop((44 * P, 86 * P, 48 * P, 87 * P)), (49 * P, 86 * P))
for (x0, x1, r0, r1) in ((SAG_X0, SAG_X1, A0, B0), (PARK_X0, PARK_X1, P0, Q0)):
    a = out.crop((x0 * P, r0 * P, (x1 + 1) * P, (r0 + 9) * P))
    b = out.crop((x0 * P, r1 * P, (x1 + 1) * P, (r1 + 9) * P))
    out.paste(b, (x0 * P, r0 * P))
    out.paste(a, (x0 * P, r1 * P))
out.save(os.path.join(HERE, 'map3d.png'))
print('wrote data3d.json and map3d.png')
