# 06 · Buildings, doors, interiors, landmarks and signs

How a world's buildings are made and dressed: city blocks from one facade kit, houses, corners, balconies, shops and
awnings, windows and roofs; blocks on slopes; landmarks; every door and what lies behind it; rooms; signs, plaques and
names; park walls and gates; and when and how Meshy models may be used. Each rule is stated for any city, with
Barcelona as a short example and its numbers (and the file or constant they live in) where the build uses them. Sources
are in brackets: the round (from `workshop/journal/DECISIONS.md`; the earliest rounds, before the numbered log, are cited by their
heading in `workshop/journal/HISTORY.md`, e.g. HISTORY "Sixth round"), with the user's words in quotes where they exist. **Later
rounds win**: where a rule was changed, the old one is marked *(reversed)* and the current one given. Placing things
in the street (lamps, trees, benches, café tables) is in `07_placing_things.md`; the ground, terraces and the
gradient rule in `08_terrain_walls_map.md`; paths and pavements in `05_streets_and_paths.md`.

## The city's blocks
1. **One kit builds every block.** Every ordinary city block is built from the same reusable, varied parts, so a
   change to a part (a window, a balcony, a cornice, how two houses meet) shows on every building at once. Barcelona:
   `builder/kit.py` `build_kit_block()`. (HISTORY "Tenth round": "One kit for every building".)
2. **The heroine's block is written by hand; every other block is made up from its own seed.** The home block's
   houses are a hand-written table (Barcelona `HOUSES` in kit.py, house by house); every other block gets a table of
   the same kind from a random seed per block (`gen_houses()`, seed `9000 + ox·131 + oy·17`), so the city is varied
   but rebuilds identically. (HISTORY "Sixth round", "Tenth round".)
3. **The block's shape follows the city's real plan, in tiles.** Barcelona's Eixample block is a chamfered octagon
   9 tiles across with 2-tile corner cuts, 3.3 m tiles (`build_assets.py` `BS, CUT = 9, 2`, `T = 3.3`), so a straight
   side is 16.5 m (`SIDE_M`) and a chamfer about 9.3 m; houses are 2.4 tiles (7.9 m) deep before the inner courtyard
   (`COURT`). A new city uses its own real block shape. (HISTORY "Sixth round", "Tenth round".)
4. **A block joins up all round.** No gaps, wedges or daylight between houses or at the corners: neighbouring parts
   overlap by a few centimetres, and a taller house next to a lower one shows a bare party wall, never a hole
   (`party_wall()`). (HISTORY "Seventh round": "The block joins up all round"; DECISIONS "The user and how to work
   with them": they notice gaps between buildings.)
5. **Each straight side holds two or three houses; each corner one house.** Barcelona: a side splits into bays as
   [3,2], [2,3], [2,1,2], [1,2,2], [2,2,1] or one 5-bay front; each chamfer is one three-bay corner house
   (`gen_houses()`). One bay is about 3.3 m wide (16.5 m ÷ 5); the window module is 1.25 m (`WIN_W`). (HISTORY
   "Tenth round".)
6. **The heroine's street is framed evenly and serves as the template.** Both corner houses on her street are the
   same height and her house's roofline sits level with theirs. (HISTORY "Eighth round": "Sandra's street front
   balanced… this block is the template for the others".)
7. **The inside of a block is closed unless it is meant to be walked.** Only a block whose courtyard is part of the
   game gets a garden and proper courtyard facades (Barcelona: Sandra's block's Jardí del Lliri, reached by a
   straight passage from the street); every other block's inside is roofed over low ("workshops"), seen only from the
   air (`build_kit_block(with_garden=…)`). A courtyard that can be seen but not reached is roofed (the university's
   quad, round 19). (HISTORY "Sixth round", "Eighth round"; DECISIONS round 19.)
8. **Blocks out of reach are built with less detail.** Beyond the walkable streets a block keeps its shape and
   colours but drops ironwork, plants, washing and signs (`KIT_DETAIL = 'far'`); windows further than about 40 m
   swap to a light copy and small parts stop being drawn at a distance (`FAR_RANGES` in `engine/main.gd`), fading,
   never popping. (HISTORY "Tenth round", "Fourteenth round": "Buildings no longer 'load' as you approach".)
9. **Every building is scaled to the heroine, not to real storeys.** Barcelona: ground floor 3.2 m, upper floors
   2.7 m, kerb 0.12 m, doors about 2.2 m, for a 1.7 m Sandra (`build_assets.py` `GROUND_H, FLOOR_H = 3.2, 2.7`,
   `KERB`). (HISTORY "Second round": "The world is scaled to Sandra".)
10. **Old-town blocks are lower than the planned grid's.** Barcelona's Eixample houses have 3–5 upper floors (corners
    4–5, `gen_house()`); Gràcia's village houses 2–4 over the shops (`gracia_block()` in
    `worlds/barcelona/build/north_build.py`). (Round 26.)
11. **A village block is a ring of closed boxes.** In an old quarter each house is a closed box: front, flat roof
    with chimneys, back and both side walls, so nothing shows through at the corners or where one house stands
    taller than the next; the block's inside is a low roof under every house's roof; the block's outline is one solid
    prism. Houses are split into 2–3-bay parts with no one-bay slivers. (Round 26, the user: plain boxes; "Think about
    usability, would people live here, does it follow good city design, does the direction flow to the right
    location"; `gracia_block()`.)
    **A block is one height all round** (**changed** in round 38 from houses of different heights in one block): every
    side of a square block — front, back and both sides — rises to the same height, so from any side, day or night,
    nothing is open behind a parapet. (The user: "some of the blocks have nothing behind it. For these buildings, as
    opposed to the octagonal ones, every side of the building should be the same height. They're a square block…
    The whole block should be one height. That's how blocks work.") (Round 38: the "one stands taller than the next" case no longer arises — one height all round.)
12. **A quarter people live in looks lived in.** A district added on the way to somewhere (Barcelona: Gràcia below
    Park Güell) is a real part of town: kit-faced blocks with shops, pavements with kerbs, a square, cafés, not plain
    boxes. (Round 27, the user: "an actual part of the town that people live in"; "This should be more of an area
    like the other".)

## Houses and facades
13. **A house is a small description, not a model.** Each house says: bays, upper floors, facade colour, trim,
    style (classic, simple, modernista), shutter colour, what each floor has (single iron balconies, one long balcony,
    window boxes, none), glazed bay windows (tribunas), the ground floor bay by bay (shop, the shop's own door, front
    door/portal, grand entrance, garage, window, garden passage), its plants and its house number (kit.py `HOUSES`,
    `gen_house()`). (HISTORY "Sixth round".)
14. **Colours come from a warm local palette.** Barcelona: 20 stucco colours (`FACADE_POOL`), four stone trims
    (`TRIMS`), shop frames and striped awning pairs in kit.py; walls in stucco above a rusticated ground floor, a stone
    plinth, string courses and end pilasters on all but the simple style, a cornice and parapet (classic: dentils and
    balusters; modernista: a curved crest). (HISTORY "Sixth round"; kit.py `build_house()`.)
15. **Balconies are stone slabs on corbels with wrought-iron railings.** Barcelona: single balconies 0.58 m deep,
    long ones 0.62 m, railings 0.95 m high (`railing()`); the top floor usually gets window boxes. A tribuna and a long
    balcony never share a floor. (HISTORY "Sixth round"; kit.py `gen_house()`.)
16. **Balconies carry life, scattered by each house's own seed.** Geraniums, daisies, herbs, trailing ivy,
    bougainvillea, a lemon tree or nothing; now and then a striped awning (about 18%), washing (12%), the local flag
    (8%, one per house), an air-conditioner (6%). (HISTORY "Sixth round", "Third round"; kit.py `build_house()`.)
17. **No half-lowered roller blinds** *(reversed: they were in the kit from HISTORY "Sixth round" and on round 24's
    modelled windows; current rule)*. The blinds once let down at random are gone; their dice are still thrown so the streets' other choices stay where they were. (Round 25, the
    user: "remove the rollershutters you add everywhere".)
18. **Windows are the picture window** *(reversed twice; current rule)*. The Meshy French window was first placed as a
    slimmed model; round 24 swapped every window for modelled ones (stone surround, wooden doors, blinds or shutters)
    because high windows looked "smashed up", without asking; round 25 went back to the old Meshy window, made sharp:
    one crisp picture of the full model laid flat on the wall, every window of a block in one object
    (`kit.py WIN_STYLE = 'picture'`, cached in `bigfiles/built/props/window_picture*.png`). Landmarks use the same window
    (`std_window()`). (Round 24: "smashed up"; round 25: the user picked option 4 of `round25/windows_close.png`.)
19. **Some windows are lit at night, not many.** About 30% of a front's windows have a lit version that glows after
    dark, few enough that you can't see into the rooms (`build_house()` `lit = rng.random() < 0.3`; main.gd
    `set_emit`). Shop windows and the pharmacy cross glow too. (HISTORY "Sixth round", "Tenth round".)
20. **Bay windows are hung on two brackets, never a cone.** A tribuna sits on two stone brackets at its ends; the old
    cone-shaped corbel in its middle hung down over the shop name below. (Round 23, the user: "Triangle above the
    'ORX…' sign on Carrer de Girona"; kit.py `tribuna()`.)
21. **Roofs are flat terraces with life.** A flat terrat with 1–3 chimneys, sometimes a stair hut, a water tank and a
    washing line (kit.py `roof()`); a Meshy building's pitched roof rising behind its parapet is replaced by a flat
    terrat with a balustrade (`fix_top()` 'flat'). (HISTORY "Tenth round".)
22. **Courtyard facades are plainer.** Where a courtyard is seen from inside, its walls have galleries, plain windows
    with shutters, washing lines on brackets, pots and a drainpipe (`rear_facade()`). (HISTORY "Sixth round".)
23. **Nothing flickers: no two faces at the same depth.** Any part laid on a facade (a fanlight, a door leaf, a
    shutter, glass in a frame) stands a few millimetres proud of what is behind it. (HISTORY "Eighth round":
    "Flicker: the stone base under the roller shutter was exactly level"; round 21: "The blue bar over doors
    flickered"; DECISIONS round 21: "Watch for equal front faces whenever adding parts to a facade".)
24. **Walls stay crisp close to.** Stucco, stone and Meshy textures get a fine grain so the wall beside a door never
    looks blurry (`add_grain()` in main.gd); textures are laid at real-world scale, never one tile stretched round a
    whole shape (round 29: the lodges' corner drums "smeared" their stone; now 1 m stone courses, `MB.cone` `uvscale`).
    (HISTORY "Tenth round"; round 29.)

## Corners
25. **Corners are proper chamfered corner buildings.** Each chamfer is its own corner house, a little taller than its
    neighbours, with shops round it (all three bays shops, or shop–portal–shop). (HISTORY "Sixth round", "Tenth
    round"; `gen_house(corner=True)`.)
26. **Corner houses wrap round to meet a set-in building.** Where a special building (a Meshy model, a landmark front)
    takes one side of a block, the corner houses either side wrap round onto that side by one bay and meet its main
    front exactly, 5 cm of overlap so no daylight shows (`meshy_wing()`, `MESHY_BODY_HALF`). (HISTORY "Seventh round",
    "Eighth round".)
27. **A corner may carry bougainvillea, but it stays on its corner.** On about 40% of corners without a corner door, a
    planter with bougainvillea climbing the chamfer, thin at the foot and wider at the top, never wrapping onto both
    fronts over shop names, awnings or street plaques; a corner whose house has its door on the chamfer gets none, and
    its lamp stands to one side. The planter is solid. (HISTORY "Third round"; round 21; round 35: "Corner
    bougainvillea spread 1.5 m each way… over shop names"; `build_assets.py` block loop.)

## Shops and awnings
28. **Shops are named in the local language, by trade.** Barcelona's names are Catalan: FORN DE PA, FLORISTERIA,
    FARMÀCIA, LLIBRERIA, FERRETERIA… often with an owner's surname (`SHOP_TRADES`, `OWNERS` in kit.py). (HISTORY
    "Sixth round", "Tenth round".)
29. **A shopfront is a frame, glass, a stall riser, a display shelf of goods in the trade's colours, a fascia with the
    name, and its door.** The fascia name is as big as the bay allows (up to 0.3 m letters, at kerb + 2.78 m;
    `build_house()`); the 2D game's fascia names were "big and bold". Some shops (15%, never bars) are shut with the
    roller shutter down. (HISTORY "Sixth round", "Tenth round"; kit.py `ground_floor()`.)
30. **Awnings are striped fabric on iron arms, over the shop windows.** Barcelona: 1.0 m out, 0.45 m drop, top at
    kerb + 2.95 m (`awning()`); on a corner house only over the middle bay. (HISTORY "Sixth round".)
31. **Each trade puts its wares outside, clear of its door.** Fruit crates, florist's buckets, book stalls, chalkboard
    A-frames (chalked both sides, read with E), café tables right outside the café either side of the door, bikes
    outside a bike shop; all of them solid and none in front of a doorway (`signs_and_wares()`, `clear_of_doors`,
    `free_spot`). (HISTORY "Sixth round", round 19 A-boards; round 21: doors blocked by plants; round 33: buckets and
    fruit stands solid.)
32. **Only shops face the main promenade, never flats.** (Round 17, the user's layout: "only shops face the Rambla,
    never flats".)
33. **A pharmacy has a proper pharmacy sign.** A white-edged green cross on a dark panel, both faces, on a bracket below
    the first-floor balconies, glowing softly at night (`build_house()` 'pharmacy'). (HISTORY "Seventh round",
    "Fourteenth round".)
34. **A shop the story needs can be set into the kit by hand, in the style of a named neighbour.** Barcelona: Bicis
    Jordi replaces a made-up shop, "in the style of the awning shops on the east side of Roger de Llúria", with bikes
    outside and one in the window; it is not enterable (`JORDI_HOUSE`, `HOUSE_OVERRIDES` in kit.py). (Round 23.)
35. **An enterable shop is a 5-bay house with its own door in the middle.** The shop's colours, its awning and its
    trade's wares; the middle bay is the glazed shop door (`landmarks.py` `shop_house()`, `SCHEMES`). (HISTORY
    "Eleventh round".)
36. **A friend's flat is a one-bay house with its own front door**, between two made-up houses, in its own colour
    (`apt_houses()`). (HISTORY "Eleventh round".)

## Blocks on slopes
37. **A house on a slope stands level, on a plinth down to the ground.** Its floor takes the level of the street at
    its front's uphill end (less 6 cm); the rest stands on a rustic stone plinth that reaches 0.8 m below the lowest
    ground at its foot (`gracia_block()`: `base = max(g0, g1) − 0.06`, `lo = min(g0, g1) − 0.8`). (Round 26.)
38. **Every building sits on its ground.** Nothing floats, sinks or tilts against the ground: sample the terrain under
    its footprint and level a platform or add a plinth; check the ground under each door and each building's base
    after a change. (Round 33, the user's park list: "buildings that don't sit right"; `workshop/journal/INSTRUCTIONS_round33.md`
    job 4.)
39. **Streets on a hill are level along their length; the climb is in ramps and steps.** Houses face level streets
    (terraces), so a pram could be pushed along them. (Round 26 walk review; CLAUDE.md, the user: "how would someone
    push a pram along it?". Details in `08_terrain_walls_map.md`.)
40. **A house whose foot meets steep ground gets a doorstep she can reach.** The few metres before any door are a
    doorstep where the slope rule does not stop her: from 0.5 m inside to 3.2 m out, the door's width plus 1 m either
    side (`worlds/barcelona/game/north.gd` `at_doorstep`). Better still, grade the ground to the door. (Round 32b: the
    Casa Museu's door was out of reach; round 33.)
41. **Built floors are exempt from the slope rule.** A portico, terrace or loggia floor is listed as level ground of
    its own (`scene.json` `flats`, `steps`, `raised`), so the ground beneath it never reads as a cliff. (Round 35b: "I
    walked right into the middle then could not go anywhere, just spin around".)

## Doors and entrances
42. **Every door is a real door.** A door that can be entered is modelled as a door: two wooden leaves in upright
    strips following a square or curved top, raised panels, brass knobs, a meeting line, a glass fanlight in an arch,
    a surround (jambs and lintel, or one smooth band of stones round an arch) and a step (`builder/build_assets.py`
    `door_unit()`). Never a flat panel or a bare glow. (Round 33, the user: "make the glow line up with the doors
    properly… it is a glowing door… put the shaped frame in there so it looks like the door glows"; CLAUDE.md: "a
    door looks like a door".)
43. **An arched surround is one smooth band, not stepped stones.** (Round 35: arched door surrounds "were 13 square
    stones in a staircase"; Palau Güell's arches "14 loose iron cubes"; `door_unit()` 20-piece band.)
44. **The door itself glows, in its own shape.** Every enterable door has a soft warm glow lying on the door's face,
    its own size, square or arched (entrance `size`, `arch`, `glow`; `shaders/door_glow.gdshader`), not a card in
    front of the wall. A door lying at a slope glows at its slope (`glow_c`, `lean`). (HISTORY "Ninth round": the glow
    added; round 33: "the glowing doors are flat squares standing in front of the buildings — the door itself should
    glow"; cellar: "the glow match their angle".)
45. **The glow is steady** *(reversed: it once breathed and brightened as she came near)*. (HISTORY "Ninth round":
    "It breathes slowly and brightens"; "Fourteenth round": "The door glow is steady (it shimmered)"; DECISIONS round
    18.)
46. **A door's measurements come from the door as built.** Where a door is on a model (a Meshy house), its place and
    size are measured off a straight-on picture or by rays, and the glow put on the real door (Barcelona: the Casa
    Museu's glow was 1.15 m left of its French door). Meshy-front doors get a 0.8 m arch. (Round 33.)
47. **Door sizes.** Barcelona: a house portal 1.24 × 2.24 m (`entrance_at()` defaults), a shop door 1.3 × 2.24, a grand
    arch 1.9 × 2.9, a Meshy front's door 1.6 × 2.6 with a 0.8 m arch, a park door 1.6 × 2.6 by default
    (`north_build.py` `door()`). (HISTORY "Second round": "Doors are 2.2 m"; landmarks.py, kit.py.)
48. **Doors face every way.** Buildings open onto whichever street they really face, not all one way; famous
    buildings open where the real ones do. Barcelona: cafés and the supermarket onto La Rambla, Casa Milà and Casa
    Batlló onto Passeig de Gràcia, the university onto Girona (`BUILDINGS[].face`). (Round 17, the user's layout.)
49. **Doorways are kept clear.** Nothing stands on the pavement in front of a door: no tree, bench, bins, planter,
    corner plant, wares or café table. A kit doorway reserves 0.7 m round a point 0.7 m out (`door_space()`); an
    entrance reserves out to the kerb (`entrance_at()`: radius max(2.5, w/2 + 1.5) m round a point 2.5 m out); street
    things slide up to 1.6 m along to the nearest clear spot. The build prints `DOORS n doorways, k with something in
    front` (k must be 0). (HISTORY "Twelfth round"; round 21, the user: doors "behind plants"; DECISIONS "The user":
    they notice "things in doorways".)
50. **Walking into a door takes her in; only right at it.** She goes in when she walks at the door within half a
    metre of it (sideways within its half-width + 0.15 m, moving towards it); E within about 1.3 m does the same.
    (HISTORY "Ninth round": "the door now only opens within half a metre"; round 32b; `engine/main.gd` doors loop.)
51. **Coming out, she stands clear of the door and the world shows at once.** She is put 1.8 m out, at her own
    height (on a hill too), with the camera keeping the angle the player had (at most a quarter turn, so forward does
    not walk her straight back in). (Round 21: "The camera through doors keeps the player's angle"; round 23: leaving
    puts her 1.8 m out, "coming out of a building the world shows at once"; round 35: she and the camera rose from
    street level after a door on a hill — now they start at her height.) (Round 38: the tip and zoom reset at the door, 03 #5; only the turn is kept.)
52. **A building may have more than one way in.** Two doors may lead to the same room (Barcelona: the Sagrada
    Família's Nativity and Passion doors), or two doors to two rooms of one building (the Sagrat Cor's crypt and upper
    church, "Separate entrances"). An unfinished or closed front has no door. (Round 17; round 26, the user's pick 3:
    "Separate entrances".)
53. **A locked door behaves the same however it is tried.** A door may carry a lock (`door(lock=…)`): without the key,
    E says it is locked and walking at it does the same (said once, not every frame); with the key, the first E or push
    turns it and the next goes in. Outdoor doors can be locked too. (Round 27: Casa Trias's cellar door; round 32b:
    "E at the Casa Trias cellar said locked, walking at it went in"; main.gd `door_said_t`.)
54. **A hidden or service way in is shaped as what it is.** Barcelona's cellar is a pair of planked doors sloping from
    0.85 m up the house's wall to a stone curb 1.3 m out, 1.7 m wide, battens, strap hinges, rings, on the side of the
    house with no path, reached by worn grass, solid. (Round 33, the user: "two wooden doors on the ground… the glow
    match their angle… on the side with no path"; PATH_RULES F11.)
55. **A path goes right to every door.** Each building's door is met by its path or paving at the doorstep, with no
    strip of grass between; where a door opens onto paving, the paving is the way. (Round 34: "Casa Museu: the path
    runs right up to its front door"; PATH_RULES F10, the user: "PLEASE make sure that the gravel path goes to the
    doors of the houses in the gaudi park".)
56. **Steps up to a door are real, walkable steps.** A landing and steps down, each recorded as raised ground she
    climbs (Barcelona: the university's landing and two steps, the MNAC's eight steps to a 1.2 m terrace with the door
    on the terrace). Never a knee-high ledge, never a door floating on the pavement. (Round 20d: "a strange knee-high
    ledge"; round 23: "MNAC door floats on the pavement: on the building, reachable; column in the way; stairs not
    climbable".)
57. **The heroine's own door is small and personal.** Barcelona: the smaller portal at the right of her building (no.
    4), with her lantern and a doorbell with a taped-on paper German flag, not the grand door in the middle. (HISTORY
    "Ninth round".)
58. **House numbers on portals.** Each portal has a brass number plate beside it (`ground_floor()` 'portal').
    (HISTORY "Sixth round".)
59. **Ordinary house doors are part of the facade, not ways in.** The kit's portals on every house are drawn as doors
    but only the buildings the story lists (Barcelona: the 2D game's 20 `BUILDINGS` plus the north's doors, 26
    entrances in all) can be entered, each with a room. (HISTORY "Eleventh round": "Every one of the 2D game's 19
    buildings has a door"; round 35 census: 26 doors.)

## Rooms
60. **Houses keep simple square rooms; only churches are built fully in 3D** *(reversed: round 26 built Casa Batlló's
    noble floor and the review proposed a room programme for every landmark)*. A house, shop, flat or museum room is one
    plain box with its furniture; a church (the Sagrada Família, the Sagrat Cor's crypt and upper church) is a full
    free-camera room. (Round 27, the user: "I do not want the houses to be done like that. Keep them squares. Only the
    churches should be a fully 3d world."; `batllo_inside.py` kept on disk, unused.)
61. **A room is measured in 1 m tiles, as the 2D game's.** x across, y from the back wall (row 0, where windows and
    pictures hang) to the front (row h); the front wall is cut away to 0.55 m high so the fixed camera can look in; the
    way out is a 1 m gap in it at x = exit, with a threshold (`worlds/barcelona/build/interiors.py` `build_room()`).
    (HISTORY "Eleventh round".)
62. **Room sizes.** Barcelona: flats 12 × 9 or 14 × 10 m; cafés and the bookshop 13 × 9; small shops 11 × 8; the
    supermarket 15 × 10; Gaudí houses 14 × 10; the university hall and library 20 × 14; the MNAC 20 × 12; the
    basilica 22 × 14; the Hypostyle Room 22 × 13; the crypt 24 × 16; the upper church 20 × 20; the park's lodge 9 × 7
    (`data3d.json` `INTERIORS`). (Rooms from the 2D game's lists, round 11; the north's, round 22b–26.)
63. **Wall heights.** 2.7 m in a flat, 3.2 m in a shop or Gaudí house, more for special rooms (MNAC 5, university 4,
    library 4.6, basilica 9, the upper church 12) (`interiors.py` `WALL_HEIGHT`). (HISTORY "Eleventh round"; round 26.)
64. **Rooms are built far away, side by side, and only the one she is in is shown and lit.** Barcelona: 40 m apart
    (`ROOM_GAP`), all in `interior.glb`; a room's points are world points (a thing placed as an offset from a parent
    already 400 m off ends up 400 m away: the party's bunting, the vase, the notebook and the salamander were all
    unseen until round 35). (HISTORY "Eleventh round"; round 35.)
65. **Indoor light is soft.** No sun indoors: ambient light, a ceiling light, soft daylight from the windows and a lamp,
    none casting hard shadows; ceilings drawn shadow-only so the camera sees in. Haze, bloom and a lower exposure only in
    sacred rooms. (HISTORY "Second round"; DECISIONS "Key design decisions"; "Traps": "Interior ceilings are drawn
    shadow-only".)
66. **The ordinary room camera is fixed and the keys are screen-relative**; the user likes the indoor controls as they
    are. Churches use the street camera (free camera) so she can look up into the vaults, with much sharper steering
    between columns (`ROOM_STEER`) and camera-only boxes across doorways so the camera never swings out into the dark.
    (Round 19: "the user likes the indoor controls as they are"; DECISIONS "Key design decisions"; see `03_camera.md`.)
67. **A room is furnished from its list.** Each room's furniture is a list `[kind, x, y, {options}]` in the world's
    data (Barcelona: `data3d.json` `INTERIORS`, written by `remap3d.py`); kinds the Meshy furniture covers (bed,
    drawers, bookshelf, wardrobe, plant, desk, chair, phone, floor lamp, sofa, side table, kitchen) use the Meshy
    pieces at set heights (`MESHY_FURN`), each solid by its footprint less 6 cm; pieces face the wall they stand
    against, or an override (`face`, e.g. chairs facing their table). (HISTORY "Sixth round", "Eleventh round"; round
    24.)
68. **The heroine's flat is placed by hand.** Barcelona: `SANDRA_FURN` (two beds, Rosa's with a green blanket, drawers,
    bookshelf, wardrobe, desk and chair, phone, floor lamp, sofa, side table, kitchen, a monstera), tall French windows
    with shutters, a runner by the door. (HISTORY "Sixth round".)
69. **Nothing blocks a window or a way round.** A cupboard never stands in front of a window; a library has aisles to
    walk round its shelves, reading tables with chairs at the front, its staircase in a corner, not an eyesore, lighter,
    no columns. (HISTORY "Seventeenth round": "the cupboard no longer stands in front of the window"; round 23: "long
    rows of shelves, no columns, stairs bottom-right, lighter"; round 24: "Library less cluttered: walk round the
    shelves; reading tables at the front… staircase in a corner".)
70. **Shop shelves hold the shop's goods** (jars, tins, packets), not books; a shopkeeper stands a step along the
    counter, not on the machine she needs to reach. (HISTORY "Eleventh round"; round 35: Empar "stood on" the espresso
    machine.)
71. **E picks what she is looking at.** Each piece of furniture has its own E spot, and a person only takes the prompt
    within about 1.2 m and when she faces them; two things never share one spot. (Round 23: "looking at the bed picks
    the bedside table"; round 35: the notebook "lay on the drawer's own spot"; people "come first only within about
    1.2 m".)
72. **Everything that can be looked at has something to say.** A reading table, a shelf, a machine: never "Nothing
    unusual." (Round 35: "The library's reading tables said only 'Nothing unusual.' They now have a line each".)
73. **Story things in rooms are arranged, not dropped.** A mission's reward in a room is made to look placed by a
    person (Barcelona: Alba's vase, an arranged dome of orange wildflowers, one tall, five round it, six lower, leaves
    and small white flowers between; the notebook on the chest; candle racks turned to face the room, 0.3 m off the
    walls by the door). (Round 35, the user: "make it look nice, not sloppy, the flowers should look like they were
    arranged"; the crypt's candles: "against the wall that faces her as she walks in from the door, with a little gap".)
74. **Stairs between floors are walked, not pressed.** A stair has a rect, the way to walk and where she arrives;
    walking into it takes her to the other floor (E also works). (DECISIONS "Key design decisions": "Stairs walk".)
75. **A church's doorway from inside shows daylight.** Its doors open onto a short corridor (3.5 m) with daylight (or
    night) at the end, the landing beyond the threshold 0.65 m out, so she is outside within a step. (HISTORY
    "Seventeenth round"; round 21.)
76. **A church's inside is built like the real one.** Barcelona: the basilica's tree columns, porphyry, hyperboloid
    vaults, stained glass cool on one side and warm on the other with sunbeams by the hour; the Sagrat Cor's crypt (five
    aisles, carved capitals, gold mosaic vault, side altars, candles; the camera kept under the arches, `wall_h` 2.9)
    and upper church (gold apse, altar rails where the walls stop her, rose window, dome) (`sagrada_inside.py`,
    `sagrat_inside.py`). (DECISIONS "Key design decisions"; round 26, the user: "Make the inside of the church if that
    was not already done.")

## Landmarks
77. **A landmark is built as the real one, stylised.** Look up the real building; orient it as it really stands;
    model its parts as they are in the game's year (Barcelona: the Sagrada Família's 14 towers as built in 2026, the
    Glory façade unfinished behind hoardings with no door, the Nativity east, the Passion west). (Round 17, DECISIONS
    "Key design decisions"; round 25, the user: "Make the church like the Temple of the Sacred Heart of Jesus in real
    life"; round 27: "can you follow real life, but stylised".)
78. **Landmarks are built in Blender from code, from photographs.** Barcelona: the Sagrada Família (`sagrada.py`), the
    university (`upf.py`), the Sagrat Cor (`north_build.py`, after the Meshy one "sat on a round plinth and looked
    nothing like it"). Meshy only where Blender cannot do it well (see "Models from Meshy"). (DECISIONS "The user":
    "they asked for the Sagrada Família to be built in Blender rather than Meshy"; round 25.)
78a. **A landmark's view is kept open as in real life.** The Sagrat Cor's crypt porch has only small statues on top and rises
    no higher than the terrace's floor: a small platform out from the terrace, a thin wall round three sides at the
    balustrades' height, its short sides meeting the balustrades, so from the upper church's doors you see over it.
    (Round 41, the user: "you can't see the city… because there's a big thing in front… There's no statues in real
    life"; "it shouldn't be that thick… make it like 3-sided rectangle… it still needs to connect to the fence"; then
    "put the statues back on the wall… Just make them smaller".)
79. **A landmark has texture, not plain paint.** Stone in courses at real scale, darker at the foot; flagstones on
    terraces; flat mosaic tiles; the user picks the textures from options. (Round 26, the user: "Put some textures on
    the church and base; it looks very plain"; picks: "B for brown bricks and C for white. Base is brown bricks";
    `builder/stone_tex.py`.)
80. **A whole-block landmark is one institution, not a row of houses.** It may reuse the kit for its walls but gets
    its own centrepiece (Barcelona: the university's clock tower, pediment with its name in letters, flags). (HISTORY
    "Twelfth round": "one institution like the 2D game's whole-block building, not a row of houses".)
81. **A landmark's solid is its footprint; the plazas round it are walkable.** (DECISIONS "Key design decisions": "Block
    `solids` are the church's footprint".) A landmark block has no corner houses, so its street plaques stand on posts
    (rule 99).
82. **Famous house fronts are five-bay fronts set into an ordinary block.** Barcelona's Gaudí houses (Batlló, Milà,
    Vicens, Calvet, Palau Güell) each take one side of a block (5 bays, 4 or 5 floors), with the kit's houses round
    them (`landmarks.py` `gaudi_front()`). A front standing proud of its block gets a camera screen 1 m out along its
    whole width so the camera never goes inside it. (HISTORY "Eleventh round"; round 35: "A Gaudí house front standing
    proud of its block (La Pedrera's waves) now stops it 1 m out".)
83. **A landmark set into a hill is held by just enough hill.** The hill behind rises no higher than needed to stop her;
    a walkable landing or terrace is a real one she can climb to. (Round 25, the user: "There is a small landing that
    you can walk up. Put it into the hill, but don't have the hill going up past it. Just enough hill so that Sandra
    can't walk up".)
84. **A landmark is seen from across the street.** Porches and canopies come down near the doors so they read from the
    far pavement. (HISTORY "Sixteenth round": "The Sagrada Família's porches and canopy come down nearer the doors".)
85. **Special buildings from the story's world stay stylised and tasteful, never boxy.** Anything that reads as
    "weird red and blue boxes" is removed or remade. (Round 27, the user: "Everything added should be tasteful".)
86. **A station sits on a pavement with a way in and out.** A station building stands at street level on a paved,
    kerbed forecourt with lamps, its forecourt meeting the footpath over shallow steps the full width of its front,
    never a bare lip; a closed ticket office shows the way is shut. (Round 26 walk review; round 28, the user: "an
    entrance where you can purportedly buy a ticket, but it is closed"; round 32: the forecourt's 22 cm lip; CLAUDE.md:
    "a station on a pavement, with a way in and out for what it serves".)
87. **Triangle budgets.** Barcelona's numbers: a Meshy building set into a city block 60,000 triangles (kit.py
    `build_kit_block`); a free-standing Meshy house in the park 150,000 (`north_build.py` `meshy_house()`; "50,000
    already cracks close to"); the Meshy window was 1,600 before the picture window; a lamp 4,000; a bench 5,000 (12,000
    in the garden); a café table 7,000; flat furniture 9,000 (a plant 14,000); a person about 30,000; Sandra about
    10,000 polygons. A street of blocks is about 2.7 million triangles at about 50 fps on the user's M1. (Round 25: the
    user saw `round25/slim_*.png`; HISTORY "Fourth round", "Tenth round", "Eleventh round".)

## Park buildings, walls and gates
88. **A park's houses stand where its real plan has them, and each has a path to its door.** Barcelona: Park Güell's
    plan from the user's aerial view; Casa Larrard (its door on its east bow, floor 9 m), Casa Museu Gaudí, Casa Trias
    up the hill, the Casa del Guarda (its east window was where the glow fell: now a door). (Round 34: "The user's
    aerial view (Google Maps) is the plan, stylised"; round 33; PATH_RULES F10.)
89. **A portico or loggia she can see into, she can walk into.** Its floor and steps are level ground; the house is
    solid behind and at its ends, the balustrade either side of the steps; a sign by the steps. (Round 33, the user:
    "she should be able to go into the portico of the building that has the cellar, with a sign at the entrance".)
90. **Nothing stands about outside a building for no reason.** No bench, railing or bit of wall that does nothing.
    (PATH_RULES F13, the user: "remove the random brick wall and the fence that is doing nothing outside that
    building".)
91. **A park's lodges are shaped, not boxes.** Rounded corners with stone in courses, caps, as the real "gingerbread
    houses". (Round 26 review item 7; round 29: the corner drums' stone; TODO round 26: "the lodges got their rounded
    corners and caps".)
92. **A park wall is one continuous wall.** Built as runs from gate pillar to gate pillar, both faces, a coping top,
    end faces, mitred corners; no single-sided walls; it meets the gate pillars; each pillar stands on its own stretch
    of wall; its top rides over dips while its faces reach the real ground; it is solid metre by metre so she can walk
    right up to it (`north_build.py` `wall_run()`). (Round 26, the user: "very sloppy… The outer walls don't join…
    Some walls are single"; round 27: "Wall gaps higher up; the wall sat OVER the hill"; round 34: the main gate's
    pillars.)
93. **Walls are solid things with depth, down to the ground.** Every wall has a top and two faces and goes into the
    ground, with no gap under it; where she walks on top of one its edge stops her; stair walls are wedge prisms.
    (PATH_RULES G2, the user: "this wall needs to go to the ground, it should also cover the stairs"; "this wall has no
    depth, she can currently fall down".)
94. **A wall meets the town with a footing and a footpath.** A stone footing along its foot both sides where it meets
    the town; a footpath at least 1.8 m wide along it so the road never touches the wall. (Round 34: "a stone footing
    along its foot both sides"; PATH_RULES H6.3.)
95. **Every wall stands on its own ground, between the two things it divides.** Barcelona: the park wall between the
    park's lawns and the wood; a drystone wall between the grass and the wood, each gap exactly one missing segment.
    (Round 31: "All walls reviewed"; `05_streets_and_paths.md`.)
96. **No invisible walls: a wall is what stops her.** Where ground must stay too steep to climb, a low stone wall stands
    along it. (PATH_RULES G1, the user: "they are annoying. make a rule removing these from the park unless there is an
    object like a wall". Details in `08_terrain_walls_map.md`. Round 40: the old flat-colour rule here is gone — the
    camera's walls are buildings only, `03_camera.md` #16.)
96a. **The funicular's stations** (round 40, the user: "make this a cohesive world"): no attendant; the station's sign,
    read with E, says the ticket office is closed and card holders use the turnstiles; at the station's front E reads her
    Amic del Park card and asks whether to ride (up below, down at the top) — yes or not now; without the card the
    turnstile stays shut. She runs right up to the station's walls (solid at the model's own walls, not its plot) and
    stands on its forecourt and steps, never sunk. The cars are solid to her on foot, built as the real ones are (96b;
    never tilted into a building), and she can reach
    them only by riding: the track is closed off — the user's lines on the plan (`round40/r3/plan_low_station.jpg`, their
    blue and purple): two black iron railings from the station's back corners, along the line of its sides, north to
    the foot of the steep hill (the east one to the solid platform), and at the hill's foot, on from each, an edge she
    is stopped at because the hill is too steep ("That is the invisible wall. But because of the steep hill"); the
    turnstile is the building's own front (E there), nothing added. The card is a quest item: never binned.
    The top station stands at the plaza's own level too: its stone base sunk all but a low lip she steps up on, the base's
    top walkable; she runs in beside the red car, under the green awning, right up to the turnstile in the arch, and
    presses E there to go down; solid only at the car, the walls and the turnstile (round 41, the user: "lower the
    funicular station at the top and then make it walkable so she can walk right up to the turnstile. The current stony
    base would need to be underground, mostly. It's fine to have the little lip… she needs to be able to run under that
    green awning and next to the red thing so that she can press E and go back down"). The terrace's railing and its
    kerb run right up to the station's sides, no gap of bare ground between ("You need the fence to continue all the way
    to the edges of the funicular station… It's perfect on the other side of the pole").
    The base's top in front of the station is laid with plain stone over the model's own painted green lines (round 41,
    the user: "there's green paint on the floor of the funicular station at the top… I don't think the same thing
    exists at the bottom": it does, buried there with the base), a solid slab down to the plaza framed on its open sides
    by a stone border, so it doesn't float ("could you also put a border around it? Because it's currently open, it looks
    like it's floating").
96b. **The funicular's cars are today's real ones, stylised: the red Cuca de Llum, upright at the stations** (round
    41, the user, with four photos of it: "Could you make something like this?"; earlier "the bottom part… against the
    rails", "it's sitting on an angle. It should be straight", "Do we need to have it stop on the hill"): one long
    capsule leaning with the line (floor and roof along it, pillars and ends upright), glossy red, a rounded bubble of
    black glass at each end, tall black windows between red pillars down each side, a round porthole behind each nose,
    a dark skirt with little bogies on the rails. **The glass is black from outside and clear from inside** ("from the
    outside, it should appear black, but from the inside, it should appear clear"); from inside a light smoky tint
    on it, so the window shows (round 41, the user: "add the window back in and make it a bit tinted… the world is too
    bright… So you can see that there's a window there"; then "I still don't see the tint from the inside. Could you just
    put a black thing up and then fade it by 80%?": a black layer 1.5 cm inside every pane, 60% black ("use dark", shown 20% and 60%), north_build.py
    FuniTint). The doors' two silver bars run from the floor's line up to the roof's edge ("make it go all the way to
    the roof so it's stretched out"); five benches inside, not two ("add more chairs. But not too many"); the red ribs
    in each glass nose show a little on the outside too, thin bands over the black, 3 cm wide ("so they're slightly visible from
    the outside of the black part, just a bit"; "make them slightly smaller"). **Its glow-worm hoops**: where each
    nose meets the body a hoop runs over the roof and down both sides — white by day, glowing pink-violet at night
    (softly: round 41, the user: "make the glow on the funicular about half as strong", 4.5 → 2.25), only there, not along the whole car ("I think it curves around the cabin, but not the entire cabin"; the real
    night photo). Built at the grade the line has at both stations, so standing at a platform it is upright, never
    tipped; the line's first stretch is no steeper than that (the track's limit, 46%). At the bottom it stops with the
    whole car on the climb. The lower station's platform is as the real one: a flight of level steps up beside the
    car, a hand's width from it, each step solid down into the ground (never a slab hanging over the grass), a canopy
    sloping with the line. The two cars pass halfway with a clear gap. The line's sign says, as an in-world fact, that
    today's cars, the Cuca de Llum ("glow-worm"), came in 2021, replacing those in service since 1958 ("You don't have
    to give information about what they look like").
    Inside, everything joins (posts floor to roof, the station canopy on its posts on the steps, following them);
    the nose keeps a flat bottom, the glass a dome on it (no dark points at its tip); a glowing frame round the inside
    of each hoop; her bench a few tiers back from the nose with another bench on the tier in front (round 41, the
    user: "move her down a few steps… So there's a chair on the next one down"; "make sure that everything joins up").
97. **A gated park: shut until she has the ticket, then always open to her.** Every gate, the main one too, is shut
    until she buys the ticket from the keeper at the main gate; the ticket is a status in the game, not an item in her
    bag. From then on the park is permanently open for her: a gate opens for her and closes slowly 6 s after she has
    gone through, never on her. The keeper stands beside the main opening where she can reach him; no bikes past the
    gates. (Round 22b: park gate + ticket; round 27: "someone inside who doesn't let you through"; round 32b: Jaume
    "inside the left pillar"; PATH_RULES F14; **changed** in round 38 from "gates posed open", the user: "The gate
    should be closed. The side gates should be closed. Until she buys a ticket, and then, like the rule currently
    says, they close 6 seconds after she leaves… once she has the ticket, the park is permanently open for her. The
    ticket is not an item, it is like a status of the game.")
    **Which way they swing** (round 39, the user: "make sure they don't open into the floor… the gates should open
    outwards, whereas the primary gate can open inwards because it's flat"): the main gate into the park, the side gates
    out to the street; each leaf opens 80°, never past 90°, its foot 5 cm over the highest ground its swing passes; a
    leaf never swings into her (it waits). The keeper stands on the street side in front of the main gate, facing out,
    upright (round 39, the user: "standing in front of the gates. Outwards and not leaning over"). (The 2.5 m talking reach was for a keeper inside the gate; in front of it, the usual reach.)
98. **A gateway is a way through, not a frame to walk through.** No decorative timber frame over a path's start; a
    path simply starts. (Round 28, the user: "Remove the square that you walk through… The path should start".)

## Signs and names
99. **Street names on marble plaques on every corner house, one per street.** Barcelona: a marble plate at 2.92 m,
    lettering 0.13 m, at 27% and 73% along each chamfer (`build_assets.py` block loop); on a landmark or park block
    with no corner house, on a slim solid post (r 0.18 m) 0.6 m out from the block's edge; on a deep-relief front, on a
    bracket 0.27 m proud. E reads them. (HISTORY "Sixth round": "street plaques sit above the corner shops";
    "Fourteenth round": "street-name signs stand on posts"; round 33: the posts solid; round 35: "ran into the Sagrada
    Família's corner columns. They now stand 0.6 m out".)
100. **Every plaque is in plain view, checked by the build.** The build looks at each street and door plaque from a
     step out in the street and prints `PLAQUES checked N hidden K`; K must be 0. (HISTORY "Fifteenth round": "Every
     street plaque in the city is checked automatically… all 190 can be seen".)
101. **Building names never float over doors** *(reversed: round 14 had floating names fading in)*. A building's name
     is on the map beside it, on a small brass plaque beside its door, and (for shops) on the fascia. (Round 18, the
     user didn't want floating names; HISTORY "Fifteenth round".)
101a. **Painted lettering lies on a board** (round 41, the user: fix the Museu d'Autòmats' name, which hung 12 cm off its
     front): a name on a wall is painted on its own board, flush on the wall, the board's colour standing off both the
     wall and the letters (cream letters on a cream wall can't be read). The build's SIGN_FLOAT check (every sign's
     lettering has its board behind its left end, middle and right end) must print `floating 0`.
102. **A brass plaque beside each enterable door, at eye height.** Barcelona: 0.34 × 0.23 m at kerb + 1.45 m, beside
     the door (half its width + 0.45 m to the side), the name engraved, E reads a short text; where deep stonework would
     swallow it, it stands on a little iron post 1.2 m out and the entrance records `plaque_pos` (`DOOR_PLAQUES`). (Round
     18; HISTORY "Fifteenth round".)
103. **A hanging sign beside every city door without a shop sign of its own.** A small painted plate on an iron bracket,
     no framed board round it, its name on both faces filling it, read from along the street, high enough to walk under
     (2.55–3.2 m), on the side away from the brass plaque; shops keep their fascia instead (`HangSigns`,
     `_HANG_SKIP`). (Round 33, the user: "Also have a sign outside"; round 34: "The signs should be smaller without the
     wood covering it"; "Just make a decision about the signs yourself".)
104. **In a park, a sign on a post beside each way in.** A tall dark post (2.3 m) with a round cap and a small plain
     cream board, the name alone in large dark letters (0.13 m), readable from the path, solid (`north_build.py`
     `post_sign()`). (Round 33; round 34, the user: "The sign post should be larger… it should be read".)
105. **A sign stands off the path, close to what it names.** (PATH_RULES F12, the user: "move the sign to the other
     side of the stairs and closer to the building"; A5: nothing on the walking width; round 35: the Hypostyle Room's
     sign and plaque "were behind the inner columns" — moved to the porch.)
106. **No sign at a secret way in** *(reversed: round 33 gave the cellar a SOTERRANI sign)*. (TODO round 34: "No sign at
     the cellar's trap doors".)
107. **Signs have cream faces and dark lettering, and E reads the whole sign.** The 2D game's signs: pale cream faces
     with their colour as a border, a heading in dark letters. (HISTORY "Fifteenth round": "the blue signs had blank
     faces; now they're pale cream with the blue as a border".)
107a. **A sign faces the people who read it.** Its face turns to where visitors stand and walk, never out over a
     railing or a drop where nobody can stand in front of it. (Round 40, the user, of the funfair's sign: "there's a
     sign that's facing out on the amusement park area. So it's not readable. It should be facing the other way or
     somewhere else"; then "that sign is in front of a bench, move it somewhere": never in front of a bench or
     another sitting place either.)
108. **Texts on plaques are true.** Dates and facts match the real place and each other. (Round 35: the university's
     plaque dated the reservoir to the 1880s; "It now says 1874–1880, as the library's sign does".)
109. **Places are named on the map and in the banner, not in the air.** Each entrance has a dot on the map coloured by
     its kind (landmark, shop or café, friends' flats, other), names on cream cards beside them, a leader line when
     a name can't sit by its dot; the street or place name shows in the banner as she walks in (`scene.streets`).
     (Round 18–19; HISTORY "Sixteenth round".)

## Models from Meshy
110. **Ask before every download, and before spending credits.** Each Meshy download is OK'd by the user; credits are
     never spent without asking. (DECISIONS "The user": "ask before downloading files"; round 25: "the user OK'd each
     download"; CLAUDE.md: "Never spend credits or download without asking".)
111. **The user logs in to Meshy themselves; never type a password.** (DECISIONS "The user": "never type passwords
     (they log in to Meshy themselves)".)
112. **Credits are scarce: be frugal, and build in Blender where it can be done well.** About 60 credits remained from
     round 25 on; the user will buy more if needed but wants them used frugally. (Round 25: "Credits are scarce: be
     frugal (the user)"; CLAUDE.md.)
113. **Downloads needed Meshy Pro for models made with Meshy 6 or 7** (the free plan: only Meshy 6 Lite models, 10 a
     month; HISTORY "Third round"). In round 41 (29 Oct 2026) a Meshy 7.1 model downloaded as GLB without asking for
     Pro: check each time, and say so before relying on it.
114. **How a download is done.** The browser pane can't save files: click Download, read the signed link from the page's
     "asset-url" reply in the network log, and fetch it with curl into `bigfiles/originals/meshy/`. Meshy's narrow layout hides the
     texture prompt; set its text box through JavaScript. (HISTORY "Fourth round"; round 25; DECISIONS "Traps".)
115. **Meshy's Text-to-3D retires on 31 October 2026**; its Agent replaces it at an unknown cost: ask before using it.
     (Round 25; TODO "Still open".)
116. **What Meshy has been used for.** Characters (Sandra, Rosa, the generic people, Trufa), three city buildings, the
     window, lamps, benches, café tables, the flat's furniture, and the park's houses and a station (Casa Larrard, Casa
     Museu Gaudí, Casa Trias, the funicular stations). Landmarks that must look like the real thing are built in
     Blender. (DECISIONS "What the project is"; round 25.)
117. **A Meshy building is fitted, not dropped in.** Slimmed to its triangle budget (rule 87), fitted to its footprint
     and a maximum height, its wall brought forward onto the street line by its measured depth (`MESHY_BUILDINGS`
     `wall`), its height level with its neighbours, its top mended where it stood back or rose behind the parapet
     (`fix_top()`), its pedestal buried where the model came on one (the station's by 2.3 m). (HISTORY "Seventh round",
     "Tenth round"; round 26.)
118. **Slimmed Meshy models are cached.** Each is kept in `bigfiles/cache/meshy/` by a hash of everything that shapes it
     and remade only when the model's file is newer (`meshy_cache_path()`); the build then takes about 80 s. (Round 26:
     "Review what can be done to make the game build run faster".)
119. **A Meshy model's flaws are mended in the game, not by regenerating.** Recolour by shader, fix bones and posture
     in code; no new Meshy generation for a fix that can be made in the game. (Round 19: "No Meshy re-generation
     needed"; DECISIONS "Traps".)
119a. **A real building from Meshy: the recipe** (round 41, Casa Batlló; the user: "document all of our conclusions
    around the use of Meshy, because we'll want to do some more designs… you want a picture that just has that
    building… do it in 4K… flush with the street and the balconies don't come out too wide"). What was learned:
    1. **The picture: the building alone, straight on, in daylight.** Meshy builds everything in the photo — the
       neighbours, the pavement, trees, lamps and people came with Casa Batlló — and its one painted picture (texture)
       is shared by all of it, so the house itself gets only part of it and looks soft. Crop the photo to the building
       before giving it to Meshy (or the user sends one). Commons photos are free to use (note the author and licence).
    2. **Settings: picture-to-3D, Meshy 7.1, texture on, 4K.** Texture off gives a grey shape (useless for a front).
       Prices seen (Oct 2026): picture-to-3D 25 credits, with its painting 35 (2K); a repaint of an existing model
       ("Texture", same photo, keeping the shape) about 10–15 at 4K. Read the price on screen before every click, and
       show it to the user when it differs from what they agreed.
    3. **Click a spend button once, then wait.** Meshy's buttons can look as if nothing happened; a second click
       starts a second job and spends again (round 41: two 4K repaints, 30 credits instead of 15). After one click,
       watch the credit count and the Assets list for the new job before doing anything else.
    4. **Download as GLB** (rule 114: the "asset-url" link, fetched with curl into its own new folder under
       `bigfiles/originals/meshy/`). The raw model is huge (Casa Batlló: 6.3 million triangles, 200 MB).
    5. **Cut it down to the building** in Blender (`tools/trim_meshy_batllo.py` is the pattern): delete everything
       outside the house's own box (read off front and top renders), and any scraps of the neighbours' roofs.
    6. **Find its real wall, not its balconies' tips.** Over the front, cell by cell, the front-most surface; the wall
       is the deeper three quarters' edge. Set that wall on the street line, flush with the neighbours (round 41: set
       by the balconies, it sat a metre back, "sunken into the block").
    7. **Draw in what stands proud** of the wall to about 60% of its depth: Meshy's balconies and bones come out too
       far ("They're a bit too large").
    8. **Fit it into the block at its real proportions** (`MESHY_GAUDI` in `builder/build_assets.py`, landmarks.py
       `gaudi_front`): the middle of its side, ordinary houses either side (as on Passeig de Gràcia), our own working
       door in its middle arch, the camera's screen out past its balconies.
    9. **Detail and size**: 450,000 triangles for a landmark front (about 8 MB more than 150,000); the 4K painting kept
       at 4K but its shading maps (metal, roughness, bumps) shrunk to 1K — together about 9 MB more than 2K. The city
       file is about 425 MB: weigh each. The slimmed model is cached (rule 118), so the game never re-makes it — only
       the first build after a change takes longer.
    10. **Our door goes in the model's own doorway**, where the real building's door is (`MESHY_GAUDI_DOOR`: its place
        across the front and its opening's size), never at a fixed middle: there a Meshy column stood through it. Its
        hanging sign on a longer bracket, clear of the stonework, on the house's own side (`sign_out`, `sign_side`);
        no flat boards stuck on Meshy's surface.
    11. **Back it with plain stone** (from the first floor up: lower, it hid the shops in the ground floor's arches). Meshy's surface has gaps (behind a thin column, under a ledge) where the sky and
        the houses beyond show through (round 41, the user: "I can see holes in the facade"): a plain stone wall 1 m
        behind its own wall, up to just under its roofline in strips, so a gap shows shadowed stone (landmarks.py
        `gaudi_front`). Of three 4K repaints the user chose the second (green balcony "eyes", warm shopfronts).
120. **A Meshy model that looks nothing like the real thing is replaced by a Blender build.** (Round 25: the Meshy Sagrat
     Cor "sat on a round plinth and looked nothing like it"; `bigfiles/originals/meshy/sagrat_cor.glb` no longer used.)

## How to work on buildings
121. **Show look options as game pictures and wait for a pick.** A new look for a building, a window, a texture or a
     sign is shown first; the build waits for an explicit choice. Bug fixes (floating, sunk, blocking, walk-through,
     mis-placed) go straight in. (Standing rule; round 25 lesson: round 24 "swapped every window without asking";
     CLAUDE.md.)
122. **"Magical" means deeper, not added extras; be subtle.** Don't invent features nobody asked for. (Round 25: "round
     24 added 'magical' features nobody asked for… Be subtle; ask before changing a look".)
123. **In a fixing round, move and change what is there; add nothing new.** (Round 35, the user: "don't add new things,
     just shift and modify existing things that are not correct or visuals that look wrong or jilted".)
124. **Look at every door and front as Sandra sees it.** After a building change: pictures of every door straight on and
     slanting (`--doorshots`), from the door's own pavement rather than along its normal (a camera 14–18 m out lands
     inside the next block), by day and by night; ask "is a door a door?". (Round 33; `workshop/journal/REVIEW_whole_game.md` §11;
     CLAUDE.md "Review the world as Sandra sees it".)
125. **Everything she might bump is solid.** Any object a builder adds to a front or a pavement writes its solid (a post
     or a box), or `--solidcheck` lists it; but nothing new may close a pavement or a doorway. (Round 33, the user: "She
     can run through the bike lock stands/bikes… review every single object like this".) Except a street workshop's own pavement (07 #14, round 38: Bicis Jordi).

## Unclear or not yet decided
- **Facade kit for a new city.** The kit is Barcelona's Eixample style (`docs/ADDING_A_WORLD.md`). For Valencia, should
  there be a new facade kit for its old town, or options on this one (colours, balconies, roofs)? Which real streets
  should it copy?
- **Which doors open.** Every house in the kit has portals and shop doors drawn as real doors, but only the story's
  buildings (26 in Barcelona) can be entered. Is that what "every door a real door" means — modelled like a door, not
  necessarily enterable — or should a new city have more enterable doors (say, every shop)?
- **Does "houses stay squares" cover museums and palaces?** Round 27 ruled only churches are built fully in 3D. Do the
  museum, palace and park-hall rooms (MNAC, Palau Güell, the Hypostyle Room) count as "houses" too? And should the unused
  Casa Batlló noble floor (`batllo_inside.py`) be kept or deleted?
- **Friends' flats.** Four friends' flats share one layout (bed, wardrobe, desk, sofa, plant). The review proposed making
  each one theirs (the florist's full of flowers, the artist's canvases…); was that ever wanted?
- **Room size against the front.** A 14 × 10 m flat sits behind a one-bay (3.3 m) front. Should rooms match the house's
  footprint, or is the 2D game's room size the rule?
- **Brass plaque and hanging sign both.** City doors now have a brass plaque (round 18) and a hanging sign (round 33)
  with the same name. Are both wanted on every door, or one of them?
- **Signs at secret or locked doors.** Round 34 removed the cellar's sign. Is the rule "no sign at any secret way in", or
  was that one door only?
- **Shop names' language.** Barcelona's shop names are Catalan. For Valencia, should they be Valencian, Spanish, or a
  mix as on real streets?
- **Building heights for a new city.** Floors are scaled to Sandra (3.2 m ground, 2.7 m upper). Keep those numbers in
  every world? How many storeys should a new city's ordinary and old-town houses have?
- **One walkable courtyard?** Only the heroine's block has a garden inside. Should a new city's home block also have one?
- **Meshy for a new city.** With Text-to-3D retiring on 31 October 2026 and about 60 credits left, which buildings (if
  any) may be made in Meshy for a new city, and what is the budget? Is the 150,000-triangle limit for free-standing
  houses and 60,000 for set-in fronts still right?
- **Blender or Meshy for small landmarks.** The rule is "Blender where it can be done well" — who decides the line, and
  should every case be put to the user (as the park lodges were in the review)?
- **The landmark park's trees.** The Ciutadella has no trees (they were planted at its rows before it moved, round 21);
  pictures were promised before changing the look. Should a landmark park have trees, and where?
- **The modelled ("crisp") windows.** Round 25 chose picture windows; the modelled-window code is kept (`WIN_STYLE`). Is it
  ever to be used again (e.g. close-up landmarks), or can it go?

## Shop names and café tables
- **A shop's name is never hidden by its awnings**: the awnings hang from just under the name board (2.55 m), not over
  it, and the name is lettered over the shop's own door when it has one (round 41, the user: "the sign on the block at
  the northeast end of La [Rambla] has the words moved off to the side": its middle was behind a window's awning;
  kit.py).
- **A café's tables are café tables**: round marble tops at table height (0.76 m, 0.76 m across) on an iron column, big
  enough to sit at (round 41, the user: "make the tables in side the cafe big enough to sit at… they're very small").
  Every café: the Cafè de la Rambla and the Cafè Berlín (`interiors.py`; the Berlín's were missed at first).

## Doors at their own level
- **A door is offered only to her standing at its own level** (within 2.5 m of its threshold's height), never from a
  terrace, porch or balcony over it. (Round 41, the user: "I can go into the crypt while standing on the balcony above
  it"; main.gd `nearest`.)

## Moving things
- **A moving thing goes the way it faces**: a ride's aeroplanes fly nose first, a car or a bike forwards. (Round 41,
  the user: "the aeroplane at the amusement park is going backwards. Change it the other direction"; north.gd `avio`.)
