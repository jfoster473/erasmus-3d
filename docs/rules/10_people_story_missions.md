# 10 — People, story characters, the dog, missions, dialogue, the exam and the save

Purpose: who lives in a city and how they behave — the passers-by, the story characters (NPCs), people sitting,
the dog — and how the story is built from missions: their parts, steps, items, money and flags, the tone of what
people say, the final exam, the save, and what makes a mission completable, with the play-through as the proof. In
Barcelona much of this came from the old 2D game ("as in the 2D game"); a new city (for example Valencia) has no 2D
game, so it writes its people and missions as data by script and follows these rules. Barcelona appears only as the
example. Numbers are those the game uses now, with the file or constant they live in. Where a rule was changed later,
the later round wins and the change is marked **(changed)**. Where objects stand is in `07_placing_things.md`.

## A. Passers-by

1. **Where they walk.** Passers-by walk up and down stretches of pavement, park paths and the promenade that the
   build leaves for them (`scene people`, each a stretch from a to b), pause at the ends and turn back. A stretch of
   pavement left empty of furniture always gets a walker ("people walk there instead"); a sparse one often (45%),
   others sometimes (25%); they walk 0.55 tile (1.8 m) in from the kerb (`builder/build_assets.py walker`; HISTORY
   tenth round). On a narrow street they walk on the pavements, not the road (round 28: Carrer de Larrard's walkers).
   On a raised footpath they walk on its surface, never sunk into it (round 38, the user: "all the people walking on
   the footpath in the new district are sinking into it").
   In Park Güell people walk its paths bend by bend, keeping right, never across verges or through walls; walkers give
   way to each other (step right and pass, walk round someone standing, wait or turn back), and people are spread
   round the park in sensible places, one or two on the Nature Square (round 39, the user: "These people walk into
   each other… Spread people out around the park more… NPCs should (generally) stick to paths and not walk through
   walls"; `north.gd park_people`, `people.gd`).
   **Not crowded:** five in the whole park (one up past the gardens and round the covered walk, one on the switchbacks,
   one on the middle carriage road, one by Casa Trias, one across the square); the seven taken out walk the city's
   streets instead, 37 walkers there (round 40, the user: "there are way too many people in the park. Cut them down by
   over half. And move them around the city."; `people.gd MAX_PEOPLE`).
2. **How many.** Up to 30 at once (`engine/people.gd MAX_PEOPLE`; round 20: busier streets). People further than 90 m
   away are not drawn or moved.
3. **They walk round things**: café tables, benches, trees, lamps, bins, kiosks, stalls, fountains, A-boards and parked
   bikes — the same solid list as Sandra's (`engine/people.gd blockers`; sizes in `THING_R`, trees 0.35, lamps 0.2,
   parked bikes 0.55). A walk that would end on a thing ends short of it (`clear_end`, 0.8 m short). (HISTORY
   fifteenth round: "People walk round café tables and chairs, benches, trees and lamps instead of through them"; round
   35: "Passers-by walked through parked bikes".)
4. **They give way to Sandra**: they wait if she is in their way (HISTORY tenth round) and never step within 0.75 m of
   her (`engine/npcs.gd`).
5. **They are solid.** She can't walk through anyone, standing, walking or sitting: she is held at arm's length, 0.58 m
   centre to centre on foot (her radius 0.3 + 0.28), 0.85 m on the bike (`engine/main.gd keep_off_people`), on the
   hills too (round 27). Pressed against someone for 2.2 s going nowhere, she slips past for 1.3 s, so a person can
   never pin her in a corner (round 27). (HISTORY sixteenth round / round 19: "People are solid"; round 27, the user:
   "You can run through Genis".)
6. **Saying hello.** E offers "Say hello" within 1.4 m; the passer-by stops, turns to her and stays until the talk box
   closes, then goes on. They say one short line from a rotating list — a local greeting, a nod, humming, half a phone
   call, a tourist's question (`engine/people.gd HELLOS`). They are strangers: small talk only, nothing about her
   missions (rule 46). (Round 38: it keeps facing her until she walks away — rule 15.)
   **In a park, greetings only** (round 40, the user: "all of the people in the park just say their very brief Catalan
   or Spanish greetings, with the exception of the tourists"): a park's walkers and its staff who aren't busy with the
   story say a short local greeting or nod (`people.gd PARK_HELLOS`); tourists keep their own chat.
   **The seven who walk the city instead of the park talk properly** (round 40, the user: "need to have proper dialogue
   about the world and Barcelona and Spain. The world specifically that the game is set in"): each has three lines of
   their own, rotating — about Sandra's world (a German Erasmus student at Pompeu Fabra, living on Flor de Lliri) and
   the city and country round her (`people.gd CITY_TALK`); the rest of the city's walkers keep the short greetings.
6a. **They stand up straight** (round 40, the user: "can you give the people better posture?"): every person's head is
   brought up over the neck (`posture.gd`, head only: their own walk and stance are left alone; Sandra keeps her full
   correction); the kite flyer's tipped back, looking up at his kite ("The guy with the kite should be looking up at
   it"), and he stands on the pavement, clear of the lamp posts (round 41, the user: "move the kite boy away from the
   light pole").
   **They stand as a relaxed person stands** (round 41, the user: "Their arms are sitting back. They should be if
   anything, arms slightly forward"; then "Their hands are going backwards… Please do a proper full analysis on the
   body. And think about what a human body would look like"): standing, ear, shoulder, hip joint and ankle on one
   plumb line (the Meshy idles had the chest turned, one shoulder up to 17 cm behind the other, and the shoulders
   leaning back behind the hips), the shoulders square and level, the arms hanging loose with the elbows softly bent
   (about 12°), each wrist beside the thigh a touch (3 cm) in front of the hip joint, the hand going on in the
   forearm's line, palm to the thigh, never bent back at the wrist (`posture.gd stand_body`; measured by
   `--armprobe`). It fades out as they walk, so their walk keeps its own swing; the kite flyer's raised arm and the
   pickpocket's cuffed arms are posed after it and win. This replaces "head only" for everyone but Sandra.
   **Shoulders down and relaxed, never raised** (round 41, the user: "It still looks like they're raising their
   shoulders… they're tense… the person in the purple shirt probably looks the best… the workmen… Their shoulders are
   very high"): the idles held the collarbones 11–21° up, one side higher than the other, and the arms out from the
   sides at uneven angles; now both collarbones lie nearly level (a few degrees up), the same each side, each shoulder
   joint at least 5% of their height below the base of the neck (as the man in the pink-purple shirt the user named as
   the right posture), and both arms hang the same small way out from the body (7°). A figure built differently gets
   its own fit, checked by eye in pictures (`npcs.gd BODY_FIX`): the workmen (round 41, "the workman's hands are still
   going back… the workmen's shoulders are still a little too high") have a round belly and open, palm-out hands, so
   their arms hang 15° out round the belly, the hands beside the hip rather than in front, tipped forward into a soft
   curl.
6b. **The kite flyer holds his kite** (round 41, the user: "the guy with the kite should have his arm out and the string
   of the kite going to his arm. And also make sure that when Sandra talks to him, he looks at her and is not looking
   up"; then "his hand's missing in one of them"): the kite flies on its own, high in front of where he stands, and
   stays there when he turns; his right arm reaches up towards it and the line runs from his hand to the kite, every
   frame (`kite_pose.gd`, `npcs.gd add_kite`/`place_kite`). While Sandra talks to him his head comes level, to her,
   and he holds the line in front of his chest, his hand in view; once she leaves, arm and eyes go back up to the kite.
   Check: `--kitetalk=<dir>` (pictures from every side, flying and talking).
7. **How they look.** Generic models (a man, a woman, an older man, an older woman, a child); about a quarter older, a
   few children. Nobody looks like Sandra (rule 20). **No two people wear the same colours** (**changed** in round 41
   from colours picked at random; the user: "give all the different people different colored clothes… some of the
   people are wearing the same color. You can mix and match all you please"): the world's data step gives every
   named person a top of their own, chosen far apart as the eye sees colour, with trousers or a skirt that stand off
   it, and deals the passers-by the next colours of the same spread in turn (`remap3d.py` "clothes",
   `WALKER_LOOKS`; `people.gd next_clothes`). Only uniforms are shared: the police, the guard, each workmen's crew.
   The colours are soft: pastels and a few deeper muted ones, never strong saturated colour (round 41, the user: "I
   also don't like his shirt. Can it be a more pastel color?"). A recoloured garment is plain: no weave or print shows
   through, so nothing shimmers as she moves ("the other guy's shirt is flickering… It can't be a pattern").
   Everyday colours, not paint: no shirt too bright (round 41, the user, of three: "The shirts are just a bit too
   bright. Make them a bit more normal" — Empar, Alba and Núria took muted shades of their own hue).
   Hair keeps its palette (`HAIR`, `GREY`).

## B. People sitting

8. **Seated people** are listed in the world's data (`scene sitters`: where, and which way they face) and drawn with
   the model that sits by default (in Barcelona Montse's), still, in colours of their own, with a solid body
   (`engine/people.gd add_sitter`). (Round 36, the user at the café terrace: "maybe have someone sitting there".)
9. **A character who sits** sits properly on a real seat: Montse's bench seat is 0.44 m high and she sits back on it,
   leaning slightly (round 9, `SEAT_TILT` in `engine/street_life.gd`). The exam's seated pose uses the riding pose with
   the head down, legs dangling (round 22b).

## C. Story characters (NPCs)

10. **Each person is one data record** (`NPCS` in `data3d.json`): name; where they are (`at`: in the world in tiles,
    or in a room); how far they potter (`r`, in tiles: 0 stays put — shopkeepers, guards, a statue); their look; an
    introduction; their lines; and the flags the story reads (`reach`, `beat`, `face_to`, `party_hat`, `after_dog`,
    `exam`…). Barcelona has 65 (36 outdoors, 29 in rooms). The data is written by a script and remade, never by hand
    (`docs/ADDING_A_WORLD.md`). **(Conflict)** In round 32b Jaume's place and reach were patched into `data3d.json`
    by hand as well as in `north_data.py`, because the script was not re-run; the rule stands (by script), and the
    next run of `remap3d.py` must agree with the hand patch.
11. **Place each person where a player can reach them and stand facing them.** Never inside a pillar or a wall
    (round 32b: Jaume stood in the gate's pillar, so no ticket could be bought); never on the thing they work at (round
    35: Empar stood on her espresso machine — now a step along her counter); never so near a usable thing that they
    take its prompt (round 35: Ferran 1.8 m away took the oven's); on ground she can get to, level (round 35b: Toni's
    work site 1.4 m up a bank now has a level bay; round 34: Rosalia was out of reach on the sunken funfair). A
    shopkeeper stands behind their counter and is talked to across it (round 32b).
12. **When a place moves, its people move with it** — and so do the items and texts tied to them (round 17: people
    move with La Rambla's columns; round 21: Òscar and Mireia with the park; round 33: Pere and Marc kept beside the
    moved key; round 35b: the funfair's five people with its rides; rounds 27–28: Genís to Gràcia's street).
13. **Talking reach.** She can talk to someone from 1.7 m outdoors and 2.2 m in rooms (`engine/npcs.gd candidates`);
    a person served across a gate or counter may have their own `reach` (Jaume 2.5 m, round 32b). (Round 39: Jaume now stands in front of the main gate, not served across it — 06 #97.)
14. **Which prompt wins.** Things to pick up first; then people, but only within about 1.2 m and when she faces them
    (round 35); her own parked bike gives way to anything else in reach (round 32b: it stole "talk" from the person
    beside her). (`engine/main.gd nearest`.)
15. **Talking stops them.** Whoever she talks to turns to face her and stays where they are until the talk box closes.
    Then they keep facing her while she stands there; only once she walks away do they go back to their day — walk
    on, potter, or turn back to their group or counter — never while she is still standing with them. They never
    walk off mid-sentence. (Round 19: "they stay put and face her until the talk box closes"; `engine/npcs.gd face`;
    **changed** in round 38, the user: "People should stay facing Sandra after she finishes talking to them. They can
    then go and do their own thing, keep walking, or turn back to people once Sandra walks away, but not while she's
    standing there.") Someone walking in a story scene can be talked to as he walks (round 35: Agent Bofarull).
16. **Pottering.** Outdoors a person wanders a few steps within r tiles (× 0.6) of home every 3–8 s, only to ground no
    more than 0.2 m above home and clear of things, never towards Sandra, and gives way if she bumps into them (04 #67a)
    (`engine/npcs.gd tick`).
16-1. **No one pottering about steps off a kerb into the road** (round 41, the user: "this NPC is just standing in the
    street"): a drop of more than 8 cm along the few steps is refused (`npcs.gd off_kerb`). **People cross only at the
    zebras, and look first** ("It's fine if they're crossing the street at crosswalks… as long as they stop, look left
    and right, and then cross"): six walkers' ways run along a pavement, over a zebra and on along the far pavement; at
    the kerb, about to step off, each stops, looks left, then right, then crosses (`people.gd CROSSERS`, scene 'zebras').
16a. **No one ever walks through a wall, by any move** (round 40, the user: "he should not be able to walk through
    walls. I already told you about this. None of the people should be allowed to walk through walls"): every step any
    person takes — pottering, walking a route, stepping aside for Sandra, stepping back when she pushes them — is
    checked at their full width (0.3 m round them) against everything solid; a step that would put them in a wall is not
    taken. Checked by `--peoplewalls` (every story character pushed and bumped, every walker run: no one inside a wall).
16c. **The path workmen** (round 40, the user): Quim stands just below the barricade and says the path is closed; spoken
    to again: "We've lost our tool, so it's taking a bit longer." Toni stands just beyond it — the one the level goes
    to — talked to across it (`reach` 3.2).
16d. **Giving the workmen their level back** (round 41, the user: "once you get the tool off the boy, there's another
    mission that says find the workman who had lost their tool, and then it's just intuitive that she walks down the
    hill. And then when she gets down there, she gives the tool back. Then it fades to black and then fades back and
    the barrier has been pushed to the side then they say, 'Thank you. We were able to finish the work with this tool.
    You are free to go through.' Then if she talks to them again, they thank her"): the mission's first step reads
    "Find the workmen who lost their spirit level"; at Toni she hands it over, the screen fades to black and back, the
    barrier stands pushed aside along the uphill verge (its notice gone; the work site's cones, sand heap and boards stay — round 41, the user: "can you keep the items there after the mission has ended?"), Toni says the user's words,
    and the path is open. No going into a building and out again (**changed** from round 22's "the workmen finish the
    path while she's indoors"). The workmen stay by the path and thank her when spoken to again.
16b. **A story character may walk a beat** (round 40: Pere along the top of the Austria Gardens and round its walks, "Just
    stays in that general area"): a `walk_loop` in the data, a loop of points on paths, walked as the passers-by walk, pausing
    now and then; spoken to, they stop and face her as rule 15. Indoors a room's people are made when she comes in and cleared when she leaves; they face
    the front of the room unless grouped.
17. **Groups face each other.** People at a gathering stand in little groups facing one another, not all facing the
    room's front (round 23, the user: "in groups of 3 and 2"; `face_to`).
18. **People follow the story.** Whether someone is there depends on flags (`engine/game.gd npc_visible`): the party's
    guests are gone after the party (round 20); the pickpocket is gone after Sandra's next visit indoors once caught
    (round 22); the park's gardener leaves after a building once the park mission is done (round 22b). Story changes to
    the world happen while she is out of sight — when she goes in and out of a door (`on_exit_to_world`).
    A host left alone after her party stands in the middle of the room facing the player (round 38, the user: "the
    party girl after the party has ended should be standing in the middle of the room facing you").
19. **Story scenes.** A person can be given a part: follow Sandra (at a distance, `TAIL_GAP` 7 m, walking or running
    to keep up), run to a place, hold and face something, be handcuffed (arms behind the back), be gone
    (`engine/npcs.gd set_mode`, `cuff`, `set_gone`; round 22, the pickpocket). A scene's state is put back when a save
    is loaded (`restore_scenes`). A character with a beat keeps to it: the policeman follows her only along La Rambla;
    when she leaves it he stops at its end, walks back to his post and waits; spoken to there he comes again; asked
    off it he says he can't leave his beat (round 35, the user's words). Neither the policeman nor the dog rides the
    funicular (round 35).
20. **How people look.** As their old 2D sprites in Barcelona; in a new city, as their data's look: skin, hair and
    hairstyle, top, legs, shoes, skirt, hat, beard, apron, accessories. A few shared models are recoloured by the
    character shader; the model is chosen from the look (`engine/npcs.gd model_for`: children → the child; grey-haired
    men → the older man; beards, aprons, shopkeepers and uniforms → the stouter man; other men → the young man;
    grey-haired women → the older woman; other women → the woman). **The Sandra models are kept for Sandra** (and her
    flatmate Rosa, recoloured: `ROSA_LOOK`), so nobody looks like her twin (HISTORY eleventh round).
21. **Clothes read as clothes.** A shirt is one colour; brown trousers are trousers (round 23, the user on Jordi: "shirt
    one colour, brown only the trousers"); **no aprons** (**changed** in round 41, the user: "The aprons look really
    bad… You can just get rid of them and have their shirts and pants"; a man who wore one is still the stouter man,
    `settled`); accessories are
    sized from each model's own head and chest: caps, flat caps, police and guard caps, hard hats, straw and sun hats,
    glasses, lanyards, shoulder bags, a guitar, a kite, a fishing rod with its line and float, a shopping trolley, a
    basket (HISTORY eleventh round; round 27).
    A Meshy man whose shirt is a printed or patchy texture wears it plain, in his own colour, so the people stand
    apart by colour (round 38, the user: "Just make the pattern shirts plain. Make them different colors to
    differentiate the different people").
    A face is never recoloured: eyes, brows and mouth keep their own colour whatever the hair's colour (round 39, the
    user: "The red-haired girl has red eyes. Her face should be like everyone else"). (Round 39: of the hats only the role and story ones remain — rule 22.)
    **No drawn-on glasses** (**changed** in round 41, the user: "Could you remove the glasses from the people? They look
    creepy"; first "The redhead girl's glasses are sitting too high"): only glasses that are part of a model's own head
    remain (the older men, the older lady). Should drawn glasses ever come back, they sit on the eyes, half way from
    chin to fringe where the face is measured (`npcs.gd FACE`).
    The face kept from recolouring stops under the eyebrows: the fringe and the brows take the hair's colour, the eyes
    stay dark (round 41, the user, of dark marks on the bun-haired women's fringe "like their extra eyebrows"; option 3
    of `round41/face_options.jpg`: `FACE` woman.glb top 1.10; `--facetop=` tries another).
22. **Hats sit on heads.** A hat hangs from the head bone (bone names matched with their number suffix stripped), its
    offset from the rest pose, with the hair tucked under it by the shader, for everyone and Sandra (round 19). Hard
    hats are domed shells on the crown, faces clear (round 26: lifted 0.1 head radii; 0.35 hovered). A party hat is
    worn by the birthday girl only during the party (round 23). A lost hat goes back on its owner's head the moment its
    mission ends (round 27: Tomàs, `npcs.redress`). (CLAUDE.md: "hats sit on heads".)
    **No casual hats** (**changed** in round 39, the user: "why are they all wearing hats. Get rid of the hats. No one wears
    these ridiculous hats anymore"): only hats that belong to a role or the story — police and guard caps, the workmen's
    hard hats, Tomàs's cap once returned, the party hat. A bag, basket or shopping trolley is drawn only if a hand
    holds it (round 39: a handbag floated beside its owner; round 41, the user: "There is an old lady with a red bag
    floating with her. Remove it and remove any others": her trolley).
23. **New character models only with the user's OK, and frugally**; prefer recolouring the existing ones. Models are
    slimmed to about 30,000 triangles (HISTORY eleventh round; rounds 25–27: Meshy credits are scarce). (CHANGED, round
    37: the user asked for new Meshy people — "Use up tokens to create more Catalan people so there is less repetition
    with the people… a new person in swim wear on the beach" — and "Lets do as many as we can before credits run out".)
23b. **Fewer look-alikes.** Each common body has a second Meshy version, and who gets which is fixed by their own look
    (about half each): the young woman (`woman.glb` / `woman2.glb`), the young man (`man.glb` / `man3.glb`), the
    grey-haired woman (`montse.glb` / `oldlady.glb`; Montse herself keeps hers). The new ones keep their own hair and
    faces exactly as drawn (the user: the pictures "looked really nice… Dropping each of these into the
    game would be amazing", and recoloured all over they looked "terrible"), but their top and skirt take the person's
    own plain colours (**changed** in round 41: every young woman with the bob wore the same yellow top and green skirt;
    rule 7). Who gets which body stays as it was before the clothes were recoloured (the look's `vkey`, its old
    colours), so the story's people keep their faces; the young man stands taller than the rest, 1.90 m (**changed** in round 39 from 1.77 m — the user first said "Maybe a head
    taller than Sandra", then, offered 2.26 m or 1.96 m: "Make it 190"; the user: "this guy should be taller. Maybe a head taller than
    Sandra… he looks too small compared to the other characters"; round 37 had called 1.81 m "way too tall"). (Round 37, the user: "replace some of the
    duplicated people… Maybe not every person is unique, but we just reduce the duplication… the other people shouldn't
    necessarily have very tanned skin"; `npcs.gd variant()`, `--models` lists who plays whom.) A new model may still take a plain shirt colour of its own, as the workmen's crews do (round 39, the user: "Yes").
    (**Round 39**: the young man in the polo shirt is out of play, his model and settings kept, the user: "Please get rid
    of the thin man. He doesn't fit. Just keep in in the background of the code… only use the tall guy to replace all of
    the other random young men when Sandra is also changed to the tall version"; `npcs.gd USE_MAN3`.)
23a. **Workmen are real workmen, modelled with their hard hats on.** A workman is his own Meshy model wearing a proper
    hard hat as part of the model (never the game's drawn helmet, which the user calls "garbage": round 37, "Add the
    hat… That is why you are doing the workmen"). (How a new person is made, round 37: an existing person's own Meshy
    picture is the style guide for a new picture of a different person — new face, hair, plain one-colour clothes,
    ordinary skin tones, not tanned — shown to the user; then a painted model (Standard detail), skeleton and Idle 4,
    slimmed to ~30,000 triangles, sized to the body it shares parts with; every step's credits stated first.)
    One model serves every crew, each crew in its own shirt colour: the
    Sagrada Família's builders one colour, the hill path's another, so the two crews are told apart at a glance (round
    37: "The two types: sagrada familia and outdoor path should have different coloured shirt").
24. **Names are the user's to choose.** (Round 22b: Pilar became Pere, "a man, renamed by the user's choice"; Laia
    became Biel; Pol is a university student. Round 41c, the user: "Change the child to a girl" — Biel is a boy's name,
    so she is Laia again, her mother's lines and the ball's mission she/her; data/remap3d.py `_to_laia`; the game's id
    stays `biel`.)

## D. Animals

25. **The dog of the lost-dog mission (Trufa in Barcelona).** Lost, she waits in a glade off a wood's path, reached by a
    short trail (round 17); her collar has no name, so only after her owner asks for help does Sandra know her name and
    can call her (HISTORY fourteenth round); until her name is said she shies away (round 22).
26. **After she is found** she comes close and is nudged 0.6 m when walked into; she follows beside Sandra (0.85 m to
    her side) at Sandra's pace, catching up at up to 1.3×; she follows everywhere until she is taken home (round 23).
    The dog's options ("Come on", "Go home", "stay") appear only once the mission is done (round 23, the user: "the dog
    options should only trigger once the mission is complete"). Told to stay, she sits; if Sandra walks 10 m off, she
    trots home. Outside a building Sandra goes into, she waits; if Sandra leaves by another door she stays put; after
    30 s she goes home; she rejoins within 3 m (`engine/dog.gd STAY_RELEASE`, `WAIT_HOME`, `REJOIN`).
27. **The dog on the bike** rides in a basket on the back of Sandra's own bike: she runs up and pounces in (at most
    1.2 s run, 0.45 s hop), sits low and forward with her tail out of the back and space at the front, and doesn't wag
    in the basket; other bikes keep their small basket (rounds 22–24; `dog.gd SEAT_FWD 0.15`, `SEAT_DROP 0.2`).
28. **The dog looks right**: not too bright at night, never floating, legs never through the ground when sitting (round
    23). No dogs on the funicular: before the mission is done Sandra can't ride with her; after, the dog goes home to
    her owner at the turnstile (round 35).
29. **Other animals** are for looking at: two cats out of doors and Rosa's at home (round 40, the user: "Move the cat on
    the hill to Sandra's apartment. The cat belongs to her housemate and it's not very friendly if you speak to it": on
    the rug on Rosa's side of the flat, three grumpy lines in turn, `touches.gd ROSA_CAT`), looked at with E, pigeons
    on the promenade that clatter up when she comes close, gulls over the beach (HISTORY eleventh round). Butterflies
    are few, only along the woods' and the hill's paths, none in town or on the beach; fireflies faint (round 25).

## E. Missions: how one is made

30. **A mission is one data record** (`MISSIONS`): its name (what Sandra must do, e.g. "Find Montse's lost dog", round
    22), its giver, the offer, Sandra's yes, the giver's accept, a reminder, the steps (`obj`, one line per state),
    the lines when it is done, the journal lines (`log`), and `was` (its old name, so old saves still group: round 22).
    The 2D fields `no` and `decline` are no longer used (rule 32). Barcelona has 17. (Round 38: there is no "Sandra's yes" — the offer is taken up without a line from her, rule 52.)
31. **A mission starts by talking to its giver**, who offers it in their own words (`engine/game.gd offer_mission`).
32. **Sandra can't refuse a mission.** She always says yes. (Round 23, the user: "don't give Sandra the ability to
    reject missions"; **changed** from the 2D game, where Esc said no.) (Round 38: she can't refuse, and says nothing: an offer is simply taken up.)
33. **The story's order.** An opening first (find your way home, buy the birthday present, the birthday party); the
    other missions only after the party (HISTORY fifteenth round: "Missions start only after the birthday party, as in
    the 2D game"). One mission may start from another's event: the bike mission is started by a question at the party,
    then the bike shop needs a chain (`bikeNeed`), and the chain's seller hands it over only after that (round 20).
34a. **The top-left lines stay on one line each** unless it is absolutely necessary, in plain words: "people", never
    "folk" (round 41, the user: "We want to keep things on one line unless it's absolutely necessary… use the term
    people. Not folks"; the idle line is "Explore Barcelona — there's lots to see and do" (the user's words); once only the exam is left, "Time to take the exam. See Professor Oriol at UPF.", `data/remap3d.py`).
34. **Steps are always shown.** The screen's top left shows the current step alone, on one line (CHANGED, round 41c,
    30 Oct 2026: it showed the mission's name above the step; the user: "I want to just have the main mission in the
    top left-hand corner", then "update it to the one-line step"); the step follows the flags and what she carries
    (`objective_text`; round 22). Each step is as long as fits one line on a computer screen (about 505 px at size 19)
    with nothing in brackets: no prices, no "between X and Y" directions (the user: "make it as long as it can be
    without going on to the next line… You don't need the brackets"); a running count like Alba's flowers (2/5)
    stays. The mission's name lives in the journal. Barcelona's lines: `data/remap3d.py` `ONE_LINE_STEPS`. The journal lists missions under their
    names in the order they were triggered, finished ones staying in their place; steps behind her grey, the current
    step in ink; a finished mission's name and last line grey with a tick (round 22). (CHANGED, round 37: finished
    missions went last; the user: "for the journal, could the order of the things be the order in which you trigger
    them?")
35. **Items.** Every item is a record (`ITEMS`: name, description, a picture `<id>.png`), whether sold in a shop or
    part of a mission. A mission's own item appears on the ground when the mission starts (`on_mission_start →
    refresh_ground`). Someone may hand an item over (the chain seller, the textbook, the ghost book).
36. **Money** is counted in cents (`give_reward(cents, items)`). A mission's price must be reachable from what the world
    offers, and someone tells Sandra how to earn: Rosa names the beach's deposit bottles and the wood's rare red
    mushrooms (round 22). Barcelona's prices: torró €6 (`TORRO_PRICE` in `story.gd`, also set in `remap3d.py`; round 23
    found two checks still at €12 — keep a price in one place); deposit bottles €1 each; red mushrooms €5 each from
    one buyer; a big-wheel ride and the coin telescope €1 for a minute (round 22b, round 25).
    Rosa's tip says this in a few short words; family calls never talk about money (round 38, the user: "[Mama]
    shouldn't say anything about money… could you just make [Rosa's] point more concise"). Round 41, shorter still,
    one line for each of the three ways, and Sandra notes it in her journal (the user: "It should be really short and
    she should just note it… just be simple like that": bottles from the beach back for the Pfand, seashells to Salva on
    the beach, rare mushrooms to Guillem by the forest path, and, last, "Sometimes you also find lost coins in the
    street, which you're allowed to keep"; `remap3d.py PFAND_TIP`, `MONEY_NOTE`).
37. **Things that come back.** Bottles and red mushrooms grow back every second time Sandra leaves a building, but only
    after the party; wildflowers likewise (round 22, round 26; `S.exits`).
38. **Flags hold the story.** Every story fact is a flag in the save (for example partyOver, bikeNeed, manoloCaught,
    manoloGone, levelGiven, pathOpen, examPassed, vaseFull, cellarOpen, note1–note5). A story wall (a workmen's
    barrier, a park gate) opens from its flag.
39. **Locks.** A door may be locked by an item; walking at it does exactly what E does — "locked" without the key, the
    key turns the first time, the next push goes in (round 32b: walking at the cellar went in without the key).
40. **No achievements, no competition.** (Round 25, the user: "I don't want everything to become a competition"; the
    2D game's achievements were removed; the journal is one page.)
41. **A notebook of things to do** sits in Sandra's room and lists general things to do in the city (visit a bookshop,
    cycle round the city, visit the landmarks, meet the professor), one page, nothing below (rounds 22b, 23).
    (CHANGED, round 37.) It is her own wish list, written on the way to Barcelona before she knew what would happen:
    the ordinary things a student wants to do there, as short plain notes ("Visit Park Güell", "Be careful of
    pickpockets on La Rambla"), not little stories and never a hint of what will happen. One line per mission, every
    mission on it and nothing else (no lines without a mission; the first mission, waking on the beach, isn't on it:
    she never planned that), in the order a player does them: the bookshop second last (its flowers grow past the
    workmen's barrier, rule 58), the exams last. A line is plain until its mission
    starts, bold while it is going on, ticked and greyed once done (it was ticked on starting it before round 37).
    (Round 37, the user: "make them bold once they've been triggered and tick them off and gray them out once they've
    been completed… remove the ones that don't have anything attached… in the order that they should be done… pass
    the exams should definitely be at the bottom… Just don't turn every single one into a big story.") The book stays on her
    bedside table as the real copy (E there opens the journal at the notebook page, so the list is always one page and
    the same), and the same list is a page of the journal: J opens the journal, ◀ turns to the
    notebook, ▶ back — one button for both. (Round 37, the user: "Her Barcelona wish list should largely already be
    written in the notebook that was next to her bed. Keep it there as a physical copy. She can just check it in the
    journal menu"; "Word it like she would. Don't just repeat what I'm doing.")
42. **Quiet notices.** Mission and getting-on-the-bike sounds are soft (round 23: "Quieter dings").

## F. Things lying about (story items on the ground)

43. **Where a story item lies matches its text, and it is reachable.** The cellar key lies half under a scrub bush by
    the calvary, just off its path, glowing faintly so a sharp eye finds it (round 40, the user's yellow mark: "the key is
    just lying nearby under the scrub, but it is slighty glowing"; it was under the path's gravel, unseen); the ball's find text no longer mentions a ledge and log that were removed (round 26). When
    the layout moves, every ground item's place is checked again (round 32b: a lost brush lay inside a house because
    its old tile was never moved with the park).
44. **Each kind has a placing rule that makes it findable, or hidden, on purpose**:
    - wildflowers (Barcelona: five for a friend's vase): beside the hill path, not on it, not behind trees, easy to
      spot; one in each fifth of the path, 1.4–1.9 m off its edge, on ground level with the path, never past a railing,
      by a bench or in a glade; one stem each; only for that mission, not sellable: nobody in the game buys them (rounds 23, 24, 26, 34;
      checked again round 37, the user: "make sure that you cannot sell flowers to anyone"). The friend who wants them
      gives the reason Sandra fetches them: she has heard they grow on the mountain, but she is not the hiking type
      (round 37, the user's words; round 41: "the flowers grow on the slopes above the city, but she's not much of a
      hiker" — never "where the path starts");
    - rare red mushrooms (three to sell; the ou de reig, good to eat, since round 38): 11–16 m off the paths, every sight line from the paths within 30 m blocked by
      a trunk, where the user placed them (round 38); the white mushrooms (a quarter as many since round 38) are scenery only, and decorative toadstools brown, so only
      the pickable ones are red (round 22; round 27);
    - a lost ball: in deep shady wood where the floor is dark, among enough trees; it should look as if it rolled down
      and was stopped by a tree, then rolled back a little (0.85 m downhill of a big holm oak); not hidden by ferns (no
      shrubs within 2.6 m, no ferns within 2.2 m); a simple red ball (round 25, the user: "It shouldn't look placed,
      but should not be hidden by ferns"; round 26: "a simple red ball"). **Once it is given back it lies at Laia's
      feet**, just in front of where Laia stands facing when left alone, for good; E only looks at it — it can't be
      picked up or moved (round 41c, the user: "once the girl gets the ball back, could you put it at her feet… And
      then the only option is to look at it"; touches.gd `biel_ball`).
    (Round 38: the first and third red mushrooms moved to where the user marked them; the 75 m spacing is dropped,
    02 #98. The red mushroom is named after the real Spanish kind it looks like, 02 #97.)

## G. What people say

45. **People who don't know Sandra's business don't talk as if they did.** (Round 23, the user, on Montse's "these
    belong to you": now "Trufa found them the other day… Maybe they will be of use to you"; a fisherman's found pages:
    "Maybe they're of more use to you than to an old fisherman".)
46. **Strangers and passers-by keep to small talk**; only those in a mission speak of it (rule 6).
47. **Lines are not "basic".** Each character speaks with their own voice, warmth and a real local fact or two (round
    23: "Review texts: less 'basic'").
48. **Someone in trouble opens with it, kindly.** (Round 23, Montse's first line, the user's words: "Hello, how are you
    dear? I am not so well… my little Trufa… scruffy… collar".)
49. **Lines follow the moment.** A host has her own lines during the party and others after it; a new line is added
    once a mission is done (`party_lines`, `after_dog`); repeated talk rotates through a person's lines (round 23).
50. **The user's own words are used as given** when they supply a line (round 35b, Mercè on the park card: "Use them as
    many times as you want: just like the Deutschland ticket you have in Germany!").
51. **Words match the world.** When the world changes, every text that names it changes (round 17: lines that said "just
    off La Rambla" reworded after it moved; round 27: "funicular" everywhere once the cable car went; round 23: a park
    lady no longer mentions a parliament the park doesn't have, the wildflower lines point to the hill path). A line
    used in many places stays general (round 35: the lamp posts' line named La Rambla on the seafront too — now "one
    of the city's old lamp posts"). Facts agree between signs (round 35: the reservoir's dates). Directions name the
    street (round 23: "on Carrer de València, between Passeig de Gràcia and La Rambla").
51a. **No season.** Nothing says what time of year it is in the game: no summer school, no "three months early", no
    term or semester (round 41, the user, after a first pass had made it summer: "Nothing should refer to a season.
    It should just be exam complete"). The end of the course is "Exam complete". General facts about the city's
    year stay (orxata in summer, mushrooms in autumn, the beach in September) as long as they don't say when *now* is.
    The time of day is not matched in lines (round 41: the user chose to leave greetings as they are), nor the keys
    named on a phone.
51d. **Real names are spelt as in reality.** Sandra's street is **Flor de Lliri** (round 41, the user: "name the
    street to the correct name and change it everywhere"): the real Carrer de la Flor de Lliri is in the Born,
    named after an inn opened there in 1444 whose sign was a painted lily; her street in the game is in the Eixample,
    so Rosa says the name was borrowed from the old Born street. Her block's garden is the Jardí del Lliri.
51b. **Lines follow what Sandra has done, before and after** (round 41): a friend asks how the repair is going until
    Sandra has her bike back, then how she is enjoying it; the pickpocket warns her about pickpockets in the very chat
    in which he robs her, so the later "the one who warned her" is true; a place is described where it is in this
    city (round 41: the café east of La Rambla, Alba two blocks up from the Ciutadella, the man in purple).
51c. **A mission is always given first.** Even when Sandra already carries what it needs (the wildflowers picked on the
    way), the giver sets the mission when first spoken to, and the next talk straight after recognises what she has
    and finishes it (round 41, the user on Alba: "the mission still gets given, even if she has the flowers on her").
52. **Shape of the talk.** English with local greetings and names; long talks run as several pages and questions in
    order; long titles are cut with "…" to fit (HISTORY eleventh round; round 35). **Sandra has no lines in a
    conversation**: the talk flows from the other person alone, and she never says yes to a mission or repeats what
    she has just been told (**changed** in round 38 from "Sandra answers in her own voice where she agrees", the user:
    "Could you rewrite it so Sandra doesn't have any lines, but everything still flows?"). She still speaks for
    herself where nobody else could: refusing (to throw away a book or clothes, to eat the rye flour), and finding a
    mission's thing (the brush, the ball, the cellar key, the cap) — the user: "It's okay for her to refuse to throw away
    books or to eat the flour… And when she finds the brush, the ball, the cellar key, and the cap, that's okay." The player's own choices stay (buying, selling, the ticket, calling home, New game or
    Continue): the player is Sandra, so those are not lines of hers to read (round 39, the user: "It's just when Sandra
    has dialogue when she's talking to other people. You're Sandra.").
52a. **Mission talk is short.** Each page says what has happened and what she does next, without extra detail (how a
    thing broke). (Round 38, the user on Jordi: "he's talking too much. Just say, I fixed X and Y, but I still need to
    wait for the new chain. (don't say it fell apart)… you already paid when you dropped it off, so now you're ready
    to go.")

## H. The exam

53. **The exam closes the story.** The professor sets it only when every open mission is done (`OPEN_MISSIONS`, 13 in
    Barcelona: all except the opening's, the exam itself and the pickpocket scene) and all five study notes have been
    found (`story.gd oriol_exam`: "wait", "study", "ready"). People give the notes as rewards along the way. (Round
    22b: "exam waits for the new missions".)
54. **The exam is a short montage, not a quiz** (**changed** in round 22b from the 2D game's questions): she sits it at
    a lectern, head down, and the professor tells her she has passed (`examPassed`). She may say "Come back later".
    Her family's phone line reminds her once all is done.

## I. The save

55. **The game saves every 30 s and whenever a mission is finished** (`engine/game.gd tick`, `complete_mission`), to
    the player's save file. The title screen offers Continue (with the saved time and money) or New game; a new game
    sets the old save aside rather than deleting it; the pause menu can export and import saves (rounds 11, 20). A new
    game starts at 06:40 on the beach with the intro (round 21). (Round 38: also on entering a building, buying and closing the window; Continue starts where she was — 08 #82a.)
56. **Tests never touch the player's save**; they keep their own (HISTORY fifteenth round: test runs had saved into the
    player's game). A renamed mission keeps its old name in `was` so saves still group (round 22).

## J. What a mission needs to be completable

57. **Every target is reachable**: every person, door, counter, cupboard, clue and item the mission uses has a spot she
    can stand on where the game offers it, joined to the start (memory "play-through approach"; rounds 32b–35b found
    people in pillars, a flower past a railing, a door behind a too-steep doorstep, a key off its path).
58. **Every gate opens in the player's order.** Whatever opens a barrier must be obtainable before the things behind it
    are needed. All five wildflowers grow past the workmen's barrier, which opens only after the spirit-level mission,
    so the book mission comes after it (round 32b; settled round 37, the user: "the bookshop should be the second last
    one. Because you need to walk through the woods before you can complete that one").
59. **The player can afford it** from the money the world offers (rule 36), and can always earn more.
60. **The player can never be shut in or pinned**: a gate never shuts on her (06 #97: it closes 6 s after she has gone
    through); people and the dog can't pin her (rule 5).
61. **Story removals happen after their part**: a character leaves, or a scene ends, only once its mission no longer
    needs them (rule 18).

## K. The proof: the play-through

62. **The play-through test** plays a fresh game through every mission in the player's order to the exam, with the
    keys, as a player does it, driven from the mission data; a stop is said in plain words, its cause fixed, and play
    resumed from a state saved at the start of each mission; a picture every 10 s through the game's own camera (round
    32b, `worlds/barcelona/tests/playthrough.gd`).
63. **Do it in this order** (round 32b, the user stopped the full run: "You keep running into issues in the park"):
    first a reach check of every mission target with no walking; then each mission's last stretches on their own; the
    whole run last, mainly for the pictures. When it stops, probe the game at that spot (a short key-driven walk, the
    raw contacts, the slope rule's verdict) before changing the game or the test — most stops were the test's own
    steering. After two or three stops in one place, report and ask.
64. **The everything-visit** (round 35, the user): talk to every person, use every object, read everything that can be
    read, walk into or past every item, a picture every 10 s; read the pictures back and fix, twice; then the
    play-through; then the full battery — "don't add new things, just shift and modify existing things".
65. **The current proof**: from a fresh start the whole game plays through, all 17 missions and the exam, 45 minutes of
    play (round 35b, `run35g`). It is not in the full test set (it adds about 55 minutes).
66. **When to run it**: after each change, pictures of what changed and the one test for it; ask before the quick set;
    the full set only once the user says all is right (round 26 testing rule); and, from round 35b, no play-throughs
    or test runs until the user is happy with the paths.

## Unclear or not yet decided

1. **The book and the wildflowers**: settled in round 37: the book mission comes after the spirit-level mission
   (rule 58).
2. **The play-through in the full test set**: add it (about 55 more minutes), or keep it separate?
3. **Passers-by and doorways**: one stood in Carrefour's doorway (round 34; the test steps round it). Should walkers
   keep out of doorways?
4. **More people sitting**: only one seated café customer exists; the review suggested a few sitters on benches (the
   beach, squares, lookouts). Wanted?
5. **Hand edits to the data**: Jaume's place was patched into `data3d.json` by hand. Should `remap3d.py` be re-run now
   so the script and the data agree?
6. **A new city's story frame**: should every city keep the same shape — an opening (home, a present, a party), open
   missions only after it, five study notes and a final exam as a montage, a pickpocket-and-policeman scene, a lost
   dog — or is that Barcelona's story only?
7. **Language for a new city**: Barcelona mixes English with Catalan greetings. For Valencia, Valencian greetings? And
   does Sandra stay a German Erasmus student?
8. **Money balance**: is there a target for how much a player can earn against what the missions cost?
9. **Talking reach**: are 1.7 m outdoors and 2.2 m in rooms right for every city?
10. **Old ground items**: the coins' places from the 2D map were never checked against the remapped city (round 32b).
11. **The kite** is static (the 2D game flew it). Leave it?
12. **Other dogs**: the review suggested dogs other than Trufa in the streets. Wanted?

## The pickpocket's arrest and the policeman (round 41)
- **The officer's cap sits on his head**, small, its visor over the brow and his face clear (the user: "The policeman's
  hat is comically large and covers his face. Could you make it smaller and just sit on his head?"; npcs.gd).
- **Heads level, not tipped back**: the stouter man's model (shopkeepers, the officer, Manolo) had his head bone leaning
  back of his face, so brought "upright" he looked at the sky (the user: "the robber and the policeman both have their
  necks right back"); per model, a forward correction (npcs.gd `HEAD_FIX`).
- **No narration of what can be seen**: the line saying the officer covers the last metres at a run is gone (the user:
  "This is not necessary. That can be seen").
- **Cuffed, Manolo turns his back to the officer**, his hands behind it, at once, whichever way he faced talking to
  Sandra (the user: "as soon as he is arrested, the thief should be standing facing away from the policeman").
- **Manolo's shirt is a muted green**, a little darker than the pale green he had, and the officer's words say "green
  shirt" (the user: "make it slightly darker… the policeman refers to [an] old purple shirt").
- **Tomàs fishes facing the sea**, 1.1 m up the sand from the water's edge (the user, then: "closer to the water"), the rod in both hands at his waist (the
  right low on the butt, the left a forearm further up), out over the water, the line straight down into it; after a
  chat he turns back to the sea (round 41, the user: "the man with the fishing rod doesn't look like he's holding it…
  he should be facing the water, almost all the time. But not too close… the rod should be over the water").
- **The bookseller never mentions flowers**: Ponç sends Sandra to the student to persuade her to sell; the flowers are
  Alba's to ask for (round 41, the user: "Don't say that. That's preempting the rest of the mission"; "He mentions
  flowers twice. Don't").
- **Wildflowers on the hill are small and lean**: a short stem leaning over, a head a touch smaller, about 0.28 m tall
  (not 0.65); Alba's vase holds a fuller bouquet, its heads half as big again (round 41, the user: "the flowers on the
  hill should be smaller… They are a bit too easy to spot and they stick right up… the flowers on the desk slightly
  bigger so it looks a bit more like a bouquet").
- **Clothes are dry, ordinary colours**: dusty greens, sandy and earthy browns, dry blues and aquas, whites and greys —
  no purple, pink or red tops (round 41, the user: "there are too many people especially around the university in
  purple shirts… Just some normal pastel colors. I thought we talked about this. So just a sort of dry green, dry
  brown, even a white, dry blue, dry aqua"; remap3d.py `_FAMILIES`).
- **Marta's spare camera is a Pentax K1000** (round 41, the user: "Use the Pentax"; the icon, their pick "icon 2":
  chrome top plate and prism hump, brown leatherette, the lens with its focus ring — `icons/camera.png`, the old
  brown compact kept as `workshop/set-aside/icons/camera_old.png`; options `workshop/screenshots/round41/pentax_icon/`).
  It has a 28–80 mm zoom lens (the user chose it, so the 1.5× zoom is true to life: 50 mm, 75 mm zoomed; f/8, 1/250 s
  and ISO 200 stay as they are, a lens set to f/8 staying there as it zooms).
  In the backpack it is called "Pentax K1000", with a few words about the camera itself (not "Marta's old spare
  camera"); Marta and the journal still say her "old spare camera"; the note as she hands it over says "Received: Marta's old
  spare camera, a Pentax K1000" (the user: "something like 'received Marta's old spare camera, a Pentax, etc'") (the user: "call it the model name? It's fine that she calls it her old spare camera. And then
  you find out what it is when you go look at it in your backpack"; `data/remap3d.py`).
- **Marta's spare camera saves its photographs on the Desktop** ("Barcelona photo <date> <time>.png"; the game's own
  photos folder only if the Desktop can't be written), and says so (round 41, the user: "Is it possible for the game to
  save it on the desktop?"; main.gd `take_photo`; check: `--phototest`).
  The photograph is taken from her eyes, without her in it, looking where the camera looks, and keeps the middle of
  the screen in 3:2, three quarters of its width (round 41, the user picked E: "more cropped… on the top as well as
  the sides, but keep that aspect ratio"; "could it be a first-person view? Because obviously she's not going to take a
  picture with herself in it"; main.gd `PHOTO_CROP`, `PHOTO_LIFT`; `--phototest --photodir=<dir>` saves elsewhere).
  **Taking a photo opens the camera's viewfinder** (round 41, the user's design): her own eyes, as on a bench, the arrows
  and the mouse look round; the photo's frame (E) drawn in white at 50% opacity (first light grey; then "white, but then 50% opacity"), everything outside it 70% dark, a
  right angle just inside each corner and a circle with a line through it in the middle, every line the same
  thickness; E takes the photo (the viewfinder stays up for the next), Z zooms the picture 1.5× (the viewfinder stays
  put; its key reads "Zoom in" or "Zoom out" as it is), Esc puts the camera away. Its keys sit in the dark bar at the bottom and the usual help line goes while it is
  up. It works anywhere she isn't riding the bike: on foot, on a bench, on the wheel or the funicular, in a room (its
  own camera at her eyes, `vf_cam`). On the bike it says "Get off the bike first to take a photo" (the user: "add the
  camera feature on the rides and indoors… If she tries to use the camera when she's on the bike… a warning message"). It says so
  the moment the camera is picked in the backpack, before any question, and the backpack stays open under it (the
  user: "as soon as you click on it, it comes up"; then "The inventory screen should be up when that comes up"). Picking
  the camera goes straight into the viewfinder, with no "Would you like to take a photograph?" first (the user:
  "remove the confirmation with the camera. Once you click on it, it should go straight to camera mode").
  (main.gd `viewfinder`, `draw_viewfinder`, `vf_eye`, `VF_*`; check: `--vftest=<dir> --photodir=<dir>`,
  `--vfplaces=<dir> --photodir=<dir>`; mock-ups and game pictures
  `workshop/screenshots/round41/viewfinder/`.)
  **Taking the photo** (round 41, the user: "make the camera sound more of a click… the whole camera overlay
  disappears… it should go darker, but you never leave the camera mode. So it's like a shutter animation… very
  quick… the increments to move left and right are very static. It should be smoother"): a camera's click (two
  quick clicks, shutter open and shut); the screen blinks dark for a moment, the viewfinder never leaving it (the
  photo is drawn apart from the screen, so nothing on screen hides); looking round with the keys eases in and out
  and moves every frame, not in steps. **She can walk with the camera up** (the user: "keep WASD to move around in
  the camera mode? And then we can use the arrow keys to look around. That way she can move and take a photo"):
  W A S D walk her (forward where the viewfinder looks, back, and a step to either side), the arrows, the mouse and
  the pad's right stick look round, the pad's left stick walks; on a bench or a ride the keys only look. The bar
  reads "W A S D walk · ← → ↑ ↓ look round". **The camera is held steady** (the user: "the camera moves with her body.
  It should be stable"): at her eye height, taken once as she raises it, not at her moving head — walking or standing
  it neither bobs nor sways; a kerb or a step is eased over a moment; on a ride or a bench it rides steady with her
  seat.
  **The watermark** (the user's picks, round 41, mock-ups `workshop/screenshots/round41/pentax_watermark*/`): white at
  about 70%, the game's lettering a touch larger than small print, inside the bottom corner angles — bottom left the
  game's date and time ("15 Sep 2026 · 11:03": the game keeps no calendar, so Sandra's first day is 15 September 2026
  and each game day after it), bottom right "PENTAX K1000 · 50 mm · f/8 · 1/250 s · ISO 200" (75 mm zoomed). The same
  in the viewfinder, live, and on the saved photo. **While the camera is up the mission, street name, clock and money
  boxes are hidden** (the user: "a version that doesn't have these four boxes"); only the keys' bar and the notes stay.
  **The camera is put away at any change of place or view**: whenever the screen goes dark (a door in or out, a
  ride's start or end, sleep) and when a ride ends (round 41c, the user: "when you transition, such as go into or out
  of a building or change on the gondola… the camera mode should disappear"; main.gd `_process`, `vf_shutter` keeps
  the shutter's own blink from counting). **On a ride the lens is at her eyes on her seat**, where the ride's own
  first-person view has them; following the funicular from outside, raising the camera takes her seat first (the
  user: "the photo in the gondola is weird" — it was taken from up in the car's roof).
