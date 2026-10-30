# Round 22: the north's people, missions, items and rooms (Park Güell's mystery, Biel's ball, the workmen's level,
# the funfair moved up its hill, the cable car). exec'd by remap3d.py on `d` (the 3D game's data) before it is
# written. Positions out of doors are given in the engine's metres and turned into the 2D game's tiles here.
import sys as _sys, os as _os, math
_sys.path.insert(0, _os.path.join(HERE, '..', 'build'))
import north as NB


def at_m(x, z):
    return ['world', round(x / 3.3 + 54.5, 2), round(z / 3.3 + 44.5, 2)]


NP = d['NPCS']
# (round 40, --peoplewalls: Quima stood with her shoulder in the beach bar's counter) half a metre out from it
NP['quima']['at'] = ['world', 59.85, 88.12]
# (round 40, the user: "move the guy with the kite onto the pavement": he stood on the grass behind it; on the pavement
# along the hill's foot, his kite still up over the hill)
# (round 41, the user: "move the kite boy away from the light pole. Just shift him up the street a bit more": he stood
# 1.3 m from the lamp at x −120.45; now 11 m along, between it and the next one west)
NP['albert']['at'] = at_m(-131.4, -100.3)
G_ = NB.GUELL

# ---- the funfair's people move up the hill with it; Laia becomes Biel (Pol is taken: a student at the UPF)
NP['rosalia']['at'] = at_m(-50.5, -283.5)
NP['rosalia']['lines'] = ["Tibidabo is 512 metres high. On a very clear day you can see Montserrat's jagged outline far inland.",
                          "Biel would live up here if I let him. The wheel, the plane, the wheel again.",
                          "The Temple del Sagrat Cor took sixty years to build, from 1902 to 1961."]
NP.pop('laia', None)
NP['biel'] = {'name': 'Biel', 'at': at_m(-49.0, -284.8), 'r': 0, 'look': {'skin': '#f7d7bd', 'hair': '#5b3a24', 'hs': 'short',
              'top': '#3d8ae0', 'legs': '#2f3a4a', 'shoes': '#5a3d2e', 'kid': True},
              'intro': "I'm Biel and I'm SEVEN and I can kick a ball really, REALLY far. Too far, actually.",
              'lines': ["Did you know the big wheel goes round and round and you can see the SEA from the top? That's true.",
                        "The plane goes out over the edge! It doesn't fall. I checked.",
                        "The church up there has a big statue of Jesus on top with his arms open. Mama says he's hugging the whole city."]}
NP['arnau']['at'] = at_m(-55.0, -293.0)
NP['blanca']['at'] = at_m(-100.0, -292.5)
# (round 41, the user: the ticket booth "on the other side and have the man facing the customer… room inside for him
# to stand") inside the booth at the platform's west end (north_build.py), behind its counter, facing out west
NP['ramon'] = {'name': 'Ramon', 'at': at_m(-99.55, -279.6), 'r': 0, 'wheel': True, 'yaw': -1.5708, 'reach': 2.4,
               'look': {'skin': '#dca57c', 'hair': '#a9a39b', 'hs': 'short', 'top': '#2f6fb3', 'legs': '#2f2f36', 'shoes': '#5a3d2e',
                        'moustache': True},
               'lines': ["The Giradabo: one euro, once round, a minute of the best view in Catalonia.",
                         "Forty years I've worked this hill. I've seen the city grow right up to the woods.",
                         "Keep your hands inside the gondola. Seagulls think fingers are chips."]}
# the two workmen on the path
w1, w2 = NB.WORKMEN
# (round 40, the user: "One of the workmen should be on this side of the gate and can be spoken to and says it's closed.
# The other workmen should be on the other side of the barricade. And he's the one you talk to with the tool. If you talk
# to the one at the bottom a second time, he'll say, 'We've lost our tool, so it's taking a bit longer.'") Quim just below
# the barricade (north_build.py: 2.5 m up the path from WORK_L), Toni just above it, talked to across it
_w0x, _w0z, _qdx, _qdz = NB.path_at(NB.WORK_L)
_bcx, _bcz = _w0x + _qdx * 2.5, _w0z + _qdz * 2.5          # (the barricade's middle, as north_build.py puts it)
NP['quim'] = {'name': 'Quim', 'at': at_m(_bcx - _qdx * 1.9 - _qdz * 0.8, _bcz - _qdz * 1.9 + _qdx * 0.8), 'r': 0, 'workman': 1,
              'yaw': math.atan2(-_qdx, -_qdz),
              'look': {'skin': '#dca57c', 'hair': '#2b1d17', 'hs': 'short', 'top': '#f08a2a', 'legs': '#3a4a5a', 'shoes': '#5a3d2e',
                       'hat': 'hardhat', 'hatc': '#f2c84b', 'beard': True},
              'lines': ["Sorry, the path's closed. We're relaying the steps all the way up.",
                        "We've lost our tool, so it's taking a bit longer."]}
NP['toni'] = {'name': 'Toni', 'at': at_m(_bcx + _qdx * 1.6, _bcz + _qdz * 1.6), 'r': 0, 'workman': 2, 'reach': 3.2,
              'yaw': math.atan2(-_qdx, -_qdz),
              'look': {'skin': '#efc3a0', 'hair': '#5b3a24', 'hs': 'short', 'top': '#f08a2a', 'legs': '#3a4a5a', 'shoes': '#5a3d2e',
                       'hat': 'hardhat', 'hatc': '#f2c84b'},
              'lines': ["We've been laying these steps by eye all morning. Somebody walked off with our level, the big red one.",
                        "Without a level, every step's a little bit wonky. You'd notice. Your knees would notice.",
                        "Coming down from the top? Go carefully, it's steep off the path."]}
# Park Güell's people
# (round 40, the user: "move the guy who has the bike chain up into the second square in the new part. So not the lower
# square that's next to the main city, but the upper one that's surrounded by all the square buildings") in the Plaça de
# la Vila (north.py GRACIA_PLACA), by its west side, his cargo bike's round the corner
NP['genis']['at'] = at_m(NB.GRACIA_PLACA[0] + 5.5, (NB.GRACIA_PLACA[1] + NB.GRACIA_PLACA[3]) / 2 - 1.5)
NP['genis']['lines'] = ["Deliveries all over Gràcia, then up here to Park Güell. These hills are murder on a cargo bike.",
                        "My uncle's a customs officer at the port. You wouldn't believe what goes out of here in crates.",
                        "Everyone photographs the dragon. Nobody photographs the courier. Story of my life."]
NP['genis']['after_guell'] = "Pere, of all people. I can't believe one of the park's own staff was stealing."
# (round 32's play-through: he stood inside the gate's left pillar, more than 1.7 m, talking reach, from anywhere
# she could stand outside: nobody could buy a ticket. Then just inside the gateway, talked to across the gate.
# Round 38, 06 #97: the gates swing now, and the west leaf swept right through him. Then the user: "this man should be
# standing in front of the gates. Outwards and not leaning over": on the street side, on the pavement just in front of
# the east pillar (the main gate opens inwards, so no leaf comes near him; the way through is clear west of him), facing
# out to the street ('yaw' 0: south — the default, PI, had him face the wall), his head up over his neck ('upright',
# posture.gd: the old man's model pokes it forward); talked to from the pavement: 'reach', npcs.gd.)
NP['jaume'] = {'name': 'Jaume', 'at': at_m(G_['gate'][0] + 2.9, G_['gate'][1] + 1.1), 'r': 0, 'park_tickets': True, 'reach': 2.0,
               'yaw': 0.0, 'upright': True,
               'look': {'skin': '#efc3a0', 'hair': '#e6e1d8', 'hs': 'short', 'top': '#5a7a4a', 'legs': '#3a3a3a', 'shoes': '#5a3d2e',
                        'glasses': True, 'vest': '#8a6a3a'},
               # (round 40, the user: "all of the people in the park just say their very brief Catalan or Spanish
               # greetings, with the exception of the tourists"; rule 10 #6) — his ticket question stays
               'lines': ["Bon dia!", "Hola, bona tarda!", "Benvinguda al parc!"],
               'after_guell': "Pere? Always first in with his broom. I can't believe he'd be mixed up in something like that."}
# (round 40, the user: "Pierre should be a young person, not an old man"; "have Pierre walking at the top of the path
# I've marked in red at the top of the Austrian Gardens… he can walk around the Austrian Gardens… Just stays in that
# general area") young, dark-haired, no beard, in the gardener's green; his beat: the gardens' top walk, down the west
# walk, back along the middle one, up the east one (rule 10 #16b; the walks: north_build.py, austria x0 + 2 + 6 i,
# z0 + 2.25 + 7.5 j)
_AU_ = G_['austria']
NP['pere'] = {'name': 'Pere', 'at': at_m(_AU_[0] + 14.0, _AU_[1] + 2.25), 'r': 1, 'gardener': True,
              'walk_loop': [[_AU_[0] + 20.0, _AU_[1] + 2.25], [_AU_[0] + 2.0, _AU_[1] + 2.25], [_AU_[0] + 2.0, _AU_[1] + 9.75],
                       [_AU_[0] + 20.0, _AU_[1] + 9.75]],
              'look': {'skin': '#e8b48e', 'hair': '#3b2a1e', 'hs': 'short', 'top': '#4a6a3a', 'legs': '#4a4a3a', 'shoes': '#5a3d2e'},
              # (round 40, the user: the park's people only greet; once the mission is on: "sorry, I don't have time for
              # talking right now. I'm looking for something I've lost" — story.gd north_talk)
              'lines': ["Bon dia!", "Hola!", "Bona tarda!"],
              'busy': "Sorry, I don't have time for talking right now. I'm looking for something I've lost.",
              'searching': "I've been looking for something. That's none of your business."}
NP['marc'] = {'name': 'Marc', 'at': at_m(_AU_[0] + 8.0, _AU_[1] + 2.25), 'r': 1, 'hidden_until': 'pereGone',
              'look': {'skin': '#efc3a0', 'hair': '#2b1d17', 'hs': 'short', 'top': '#4a6a3a', 'legs': '#4a4a3a', 'shoes': '#5a3d2e'},
              'lines': ["Bon dia!", "¡Buenas!", "Adéu, maca!"]}
NP['fiona'] = {'name': 'Fiona', 'at': at_m(98.0, -179.0), 'r': 0,
               'look': {'skin': '#f7d7bd', 'hair': '#c46a3a', 'hs': 'long', 'top': '#6a5aa0', 'legs': '#3a4a6a', 'shoes': '#5a3d2e', 'bag': True},
               'lines': ["My cousin's in art insurance. She says smuggling gangs ship stolen pieces through ports like this one, hidden in crates of tiles.",
                         "From Glasgow. We've a Mackintosh or two, but nothing that bends like this bench.",
                         "This whole square was meant as a market place. Imagine buying your tomatoes up here."],
               'after_guell': "The gardener! I can't believe one of the park's own people was stealing."}
NP['kenji'] = {'name': 'Kenji', 'at': ['int_hypostyle', 5.0, 9.5], 'r': 0,
               'look': {'skin': '#efd2b0', 'hair': '#191315', 'hs': 'short', 'top': '#e8e2d2', 'legs': '#2f3a4a', 'shoes': '#5a3d2e',
                        'glasses': True, 'bag': True},
               'lines': ["At home in Japan, Gaudí is a hero. A sculptor from Fukuoka has carved the Sagrada's stone for forty years.",
                         "Eighty-six columns, and the outer ones lean, to take the weight. I have drawn every one of them.",
                         "Look up: the suns in the ceiling are by Jujol. Broken plates and bottles. Genius."]}
NP['merce'] = {'name': 'Mercè', 'at': ['int_gaudi_house', 8.0, 4.6], 'r': 0,
               'look': {'skin': '#efc3a0', 'hair': '#a4532c', 'hs': 'long', 'top': '#8a3a5a', 'legs': '#2f2f36', 'shoes': '#5a3d2e',
                        'glasses': True},
               'lines': ["Bon dia! Benvinguda a la Casa Museu.", "Hola, bona tarda!"]}

# ---- the bike's chain is now with Genís (in the Plaça de la Vila since round 40)
B = d['MISSIONS']['bike']
B['offer'] = B['offer'].replace("has it at the Tibidabo funicular station and he's stuck on his route up there",
                                "has it in Gràcia, in the Plaça de la Vila")
B['accept'] = "Genís is taking his break in the Plaça de la Vila, the square in the middle of Gràcia's upper streets. He has a cargo bike and a very loud whistle."
B['remind'] = "The new chain's with Genís, in the Plaça de la Vila up in Gràcia. Your bike's waiting for it."
B['obj']['fetch'] = "Fetch the new chain from Genís in the Plaça de la Vila, in Gràcia"
B['log']['need'] = "Jordi says my bike needs a new chain. Genís the courier has it for him, taking his break in the Plaça de la Vila, up in Gràcia."

# ---- the missions
M = d['MISSIONS']
M.pop('balloon', None)
M['guell'] = {
    'name': "Find the museum's missing salamander", 'giver': 'merce',
    # (round 40, the user: "Sandra's not talking to her, so it needs to say, I've just discovered that the Salamandretta,
    # the first model, blah, blah, blah, has disappeared. It was here last night. The science says it's gone for
    # restorations. But I never wrote that. Could you ask around the park? Maybe someone has seen something.")
    'offer': "I've just discovered that the Salamandreta has disappeared! The first model for the dragon on the stairs, made in "
             "Gaudí's own workshop. It was here last night. The sign says it's gone for restoration, but I never wrote that. "
             "Could you ask around the park? Maybe someone has seen something.",
    'yes': "I'll keep my eyes open.", 'no': "Not right now",
    'accept': "Thank you. I've told the director; he says it will turn up. Things don't just turn up.",
    'decline': "Of course. It's not your problem. It's barely anybody's problem, apparently.",
    'remind': "I can't believe it's missing. Maybe you should speak to the park's loyal gardener, Pere. He might have seen something.",
    'obj': {'look': "Find out where the Salamandreta went (Park Güell)", 'key': "Find what the brass key tagged T·S opens",
            'back': "Take the Salamandreta back to Mercè at the Casa Museu Gaudí"},
    'clue_key': "Half hidden under a bush by the Tres Creus: a brass key on a ring, tagged T·S. Somebody will be missing this.",
    'clue_door': "A low wooden door marked SOTERRANI: the cellar. Locked.",
    'clue_door_open': "The key fits perfectly. T·S: Trias, Soterrani.",
    'clue_crate': ["In a crate stencilled PORT DE BARCELONA, packed in straw: a small glazed dragon, green and gold. The Salamandreta.",
                   "Other crates, nailed shut, are stencilled for Rotterdam and Geneva. A clipboard lists pieces from museums in Lisbon, "
                   "Prague and Naples, each one signed for with the same initial: P. A pair of gardening gloves lies on the lid.",
                   "Sandra: P... The gardener. Pere. And this isn't only Barcelona. Mercè needs to see this."],
    'done': ["(Mercè holds the little dragon as if it might wake.) The Salamandreta. Oh, you clever, clever girl.",
             "Pere has the keys to every store in this park, and he waters the plants in this house every morning. The card was to buy "
             "him time until Monday's ship. I'm calling the Mossos.",
             "And for you: an Amic del Park card. The park's yours already, and the same foundation runs the funicular up the mountain, so "
             "that's free too. Use them as many times as you want: just like the Deutschland ticket you have in Germany! "
             "Go and see the city from the top. You've earned it."],
    'log': {'start': "Mercè at the Casa Museu Gaudí: the Salamandreta, a little glazed dragon from Gaudí's workshop, has vanished. "
                     "A card says 'removed for restoration', but she booked no restoration.",
            'key': "Found a brass key under a bush by the Tres Creus, tagged T·S. What does it open?",
            'got': "Under Casa Trias, in the cellar: the Salamandreta, packed for the port, and crates for half of Europe. Signed: P.",
            'done': "Took the Salamandreta back to Mercè. Pere the gardener was the ring's man in the park. I got an Amic del Park "
                    "card: free rides on the funicular up the mountain, as many times as I want."}}
M['ball'] = {
    'name': "Find Biel's lost ball", 'giver': 'rosalia',
    'offer': "Biel kicked his ball over the railing, down into the wood. I told him it's far too dangerous to go after it, "
             "it's steep as a roof down there. You haven't seen a red ball anywhere, have you?",
    'yes': "I'll have a look.", 'no': "Not right now",
    'accept': "Be careful. Truly. If it's gone, it's gone. (Biel, behind her, crosses his fingers.)",
    'decline': "No, quite right. Biel, what did I say about kicking near the railing?",
    'remind': "Any sign of it? It's red. Somewhere below the railing, Biel says, 'about a hundred metres down'.",
    'obj': {'find': "Find Biel's ball in the wood below the funfair", 'back': "Take the ball back to Biel at the funfair"},
    'got_text': "Deep among the holm oaks, a little uphill of a big trunk that stopped it rolling: a red ball.",
    'done': ["MY BALL! (He hugs it.) Mama! She got it! She went down the HILL!",
             "Rosalia: Gràcies. Honestly. And you came back up in one piece, which is more than I'd have managed.",
             "Biel: You can have this. I found it leaning on a wall down the path and I took it. Maybe someone needs it?"],
    'log': {'start': "Biel kicked his ball over the funfair's railing into the steep wood below. His mother Rosalia says it's too dangerous to fetch.",
            'got': "Found Biel's ball on a ledge in the wood. Back up the path to the funfair.",
            'done': "Gave Biel his ball. He gave me a big red spirit level he found 'leaning on a wall down the path'."}}
M['level'] = {
    'name': "Give the workmen back their level",
    'obj': {'find': "Find out who's missing a big red spirit level", 'give': "Give the level to Toni, at the path's first bend",
            'wait': "Let the workmen finish the path (go into a building and out again)"},
    'give': ["Our level! Where did you find that? A boy? Leaning on a wall? (He looks at the wall.) ...Fair enough.",
             "Right. With this, we'll have the steps done by this afternoon. Go and see the church at the top in the meantime, "
             "if you haven't already."],
    'finished': "The new steps are done all the way up: the path's open, both ways.",
    'log': {'start': "Biel gave me a big red spirit level he found 'leaning on a wall down the path'. Someone must be missing it.",
            'given': "Gave Toni the workman his level. They'll finish the path this afternoon.",
            'done': "The workmen have finished: the path up to the funfair is open."}}
d['OPEN_MISSIONS'] = [k for k in d['OPEN_MISSIONS'] if k != 'balloon'] + ['guell', 'ball', 'level']

# ---- items
I = d['ITEMS']
I['ball'] = {'name': "Biel's ball", 'kind': 'quest', 'icon': 'ball', 'desc': "A red ball, a little scuffed from its trip down the hill."}
I['spirit_level'] = {'name': 'Spirit level', 'kind': 'quest', 'icon': 'spirit_level',
                     'desc': "A big red builder's level with a bubble in a green window. Biel found it 'leaning on a wall down the path'."}
I['salamandreta'] = {'name': 'The Salamandreta', 'kind': 'quest', 'icon': 'salamandreta',
                     'desc': "A small glazed dragon in green and gold trencadís: the first model for the one on Park Güell's stairs."}
I['cellar_key'] = {'name': 'Brass key', 'kind': 'quest', 'icon': 'cellar_key', 'desc': "A brass key on a ring with a tag: T·S. Found under a bush by the Tres Creus in Park Güell."}
I['park_pass'] = {'name': 'Amic del Park card', 'kind': 'keep', 'icon': 'park_pass',
                  'desc': "A Friend of the Park card: free rides on the funicular up to Tibidabo, as many times as you want."}

# ---- achievements
A = d['ACHIEVEMENTS']
for a in A:
    if a['id'] == 'balloon':
        a.update({'id': 'ball', 'title': 'Back of the Net', 'desc': "Brought Biel's ball back up the hill."})
A[-1:-1] = [{'id': 'guell', 'title': 'Elementary, my dear Gaudí', 'desc': 'Found the Salamandreta and unmasked the park\'s smuggler.'},
            {'id': 'level', 'title': 'On the Level', 'desc': 'Got the mountain path open again.'},
            {'id': 'wheel', 'title': 'Round and Round', 'desc': 'Rode the Giradabo, once round, over the whole city.'},
            {'id': 'thief', 'title': 'Red-Handed', 'desc': 'Helped Agent Bofarull catch the Rambla pickpocket.'}]

# ---- the rooms
R = d['INTERIORS']
R['int_guarda'] = {'name': 'Casa del Guarda', 'w': 9, 'h': 7, 'exit': 4, 'floor': 'terracotta', 'wall': '#efe2c4', 'trim': '#2c5fa8', 'objs': [
    ['model', 4, 2, {'t': "A model of the park as Count Güell planned it: sixty houses, an English garden city on the bare hill. Two were sold."}],
    ['painting', 1.5, 0, {'art': 'portrait', 't': "Eusebi Güell, textile magnate, Gaudí's patron for thirty years. He lived in Casa Larrard, in the park, until 1918."}],
    ['painting', 6.5, 0, {'art': 'landscape', 't': "The Muntanya Pelada, the 'bald mountain', in 1900: no trees at all. Everything you see out there was planted."}],
    ['display', 1, 4, {'w': 2, 't': "Shards of plates, cups and bottles: trencadís, the broken-tile mosaic. Gaudí's workers collected them from factories' waste."}],
    ['window', 4, 0], ['plant', 7.5, 5.5]]}
R['int_gaudi_house'] = {'name': 'Casa Museu Gaudí', 'w': 12, 'h': 9, 'exit': 6, 'floor': 'hydraulic', 'fcol': ['#8a3a3a', '#efe4c8', '#5c8a4a'],
                        'wall': '#f2dcd6', 'trim': '#7a3a3a', 'objs': [
    ['plinth', 6, 3, {'clue': 'plinth', 't': "An empty marble plinth, and a printed card: REMOVED FOR RESTORATION."}],
    ['calvetchair', 2, 2, {'t': "Oak chairs Gaudí designed for Casa Calvet: they curve the way a back curves."}],
    ['calvetchair', 3, 2],
    ['bed', 10, 1, {'col': '#9aa0a8', 't': "Gaudí's iron bed, narrow as a monk's. He slept here until he moved into the Sagrada's workshop."}],
    ['painting', 4.5, 0, {'art': 'portrait', 't': "Antoni Gaudí, about 1910: white-bearded already, and already famous."}],
    ['display', 1, 5, {'w': 2, 't': "A dressing table from Casa Batlló, all curves, like something grown rather than made."}],
    ['window', 7.5, 0], ['plant', 1, 7.5], ['plant', 10.5, 7.5]]}
R['int_trias_cellar'] = {'name': 'Casa Trias — el soterrani', 'w': 10, 'h': 8, 'exit': 4, 'floor': 'stone', 'wall': '#a8977e', 'trim': '#5a4a3a', 'objs': [
    ['crate', 1, 2, {'n': 4}], ['crate', 1, 4, {'n': 3}], ['crate', 7.5, 2, {'n': 4}],
    ['crate', 6, 5, {'n': 1, 'open': True, 'clue': 'crate', 't': "An open crate, packed with straw."}],
    ['readtable', 3.5, 4.5, {'w': 2, 'clue': 'clipboard', 't': "A clipboard on a trestle."}],
    ['chest', 8, 6, {'t': "Coils of rope, a sack truck, a roll of stencils: PORT DE BARCELONA."}]]}
cols = []
for j in range(3):
    for i in range(7):
        cols.append(['column', 2.5 + i * 2.6, 2.4 + j * 2.8])
R['int_hypostyle'] = {'name': 'Sala Hipòstila', 'w': 22, 'h': 13, 'exit': 11, 'floor': 'stone', 'wall': '#e8e2d2', 'trim': '#2c5fa8',
                      'objs': cols + [
    ['palmceil', 5, 4, {'w': 2}], ['palmceil', 11, 4, {'w': 2}], ['palmceil', 16, 4, {'w': 2}],
    # (round 40, the user: "please get rid of the red dust" — the clue led nowhere)
    ['sign', 19, 0, {'w': 2, 't': "SALA HIPÒSTILA: eighty-six columns, built 1907–1909 to hold up the square above and shelter a market below."}]]}
# (round 26) the Sagrat Cor as the real one: two churches, each with its own door (the user: "Separate entrances"). Both
# rooms are built by build/sagrat_inside.py (their layout is there); here only their names and what E says about things.
R['int_sagrat_cor'] = {'name': 'Sagrat Cor: the crypt', 'w': 24, 'h': 16, 'exit': 11, 'floor': 'stone', 'wall': '#c6a073',
                       'trim': '#8a6a3e', 'sacred': True, 'objs': [
    ['altar', 12, 2, {'t': "The crypt's high altar, in a niche of gold mosaic. This lower church was built first, from 1902, in "
                           "stone from Montjuïc; the church above came after, and took sixty years."}],
    ['vault', 12, 8, {'t': "Over the middle aisle the vault is all gold mosaic: thousands of little tiles catching the candlelight."}],
    ['candles', 2, 13, {'t': "A rack of little candles, most of them lit. A coin box says VOLUNTAT: give what you like."}],
    ['column', 10, 10, {'t': "Short, thick columns with carved capitals, five aisles of them, holding up the whole church above."}],
    ['sign', 14, 15, {'t': "THE UPPER CHURCH is above this one: up the steps outside, onto the terrace, and in through its own doors."}]]}
R['int_sagrat_alta'] = {'name': 'Sagrat Cor: the upper church', 'w': 20, 'h': 20, 'exit': 9, 'floor': 'marble', 'wall': '#ece4d2',
                        'trim': '#8a6a3e', 'sacred': True, 'objs': [
    ['altar', 10, 1, {'t': "The high altar under the great crucifix. Up here, above the whole city, it is very quiet."}],
    ['apse', 8, 1, {'t': "The apse is gold mosaic, and in it the Sacred Heart, arms open, as on the tower outside."}],
    ['glass_east', 18, 12, {'t': "The east apse's stained glass, all blues and greens: in the morning the sun comes straight through it."}],
    ['glass_west', 2, 12, {'t': "The west apse's glass, reds and golds, for the evening sun."}],
    ['rose', 8, 18, {'t': "The rose window over the doors, the same one you see from the funfair, lit from outside."}],
    ['tower', 10, 9, {'t': "Eight columns hold up the tower, and its lantern lets the light down. Above that, a lift climbs to the "
                           "feet of the Christ. A notice on the door: closed today."}],
    ['leaflets', 12, 19, {'t': "A leaflet: begun in 1902 by Enric Sagnier, finished by his son in 1961. Saint John Bosco asked for "
                               "a church on the summit when he visited Barcelona in 1886."}]]}

# ---- the 2D street things up here: the funicular's sign becomes the cable car's, the funfair's moves with it
objs = []
for o in d['objects']:
    if o.get('type') == 'bench' and o.get('y') == 8:
        continue
    if o.get('type') == 'sign' and 'FUNICULAR' in o.get('text', ''):
        lx, lz = NB.CABLE_LOW
        o.update({'x': int(round(lx / 3.3 + 54.5 - 1.6)), 'y': int(round(lz / 3.3 + 44.5 + 1.8)),
                  'text': "FUNICULAR DEL TIBIDABO\nUp to the funfair and the Temple del Sagrat Cor at the summit: 1,130 m of track, climbing 275 m.\n"
                          "Ticket office closed. Amic del Park card holders, please use the turnstiles."})
    elif o.get('landmark') == 'tibidabo':
        # (on the funfair's terrace, by the path's arrival; round 40, the user: it faced out over the railing, unreadable,
        # and "that sign is in front of a bench, move it somewhere" — a tile in from the west wall, beside the path onto
        # the terrace, on the north side of where the path comes on, clear of the benches, its face south to the people
        # arriving; 'face_n' in world2d.py turns a sign round where it is wanted)
        o.update({'x': 23, 'y': -44})
    objs.append(o)
d['objects'] = objs
