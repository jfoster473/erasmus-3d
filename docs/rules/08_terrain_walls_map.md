# 08 · Terrain, slopes, walls, and the map and screen

How the ground of a world is shaped so it reads true and plays fairly — level streets, terraces, ramps and steps, the
one gradient rule, banks, retaining walls, fences, ditches, cliffs, water's edges and the world's edge — how the game
works out the height she walks at (and the traps in it), and then the things on screen: the map, the HUD, the talk box,
the menus, the debug menu and sound. Written for any world; Barcelona is the example. Path surfaces and how paths join
paving are in `05_streets_and_paths.md` (rule numbers there); how Sandra moves on the ground is in
`04_character_movement.md`; the camera is in `03_camera.md`. Barcelona's place-by-place rules are `docs/PATH_RULES.md`
(codes in brackets). Later rounds win: where a rule was changed, the old one is marked and the current one given.

## How the game knows the height of the ground
1. **Her body stays at street level; only her model is lifted to the ground's height.** Outdoor physics is flat: walls
   and solid things are boxes standing from street level (0–4 m, blocks 18 m) anywhere, even on a hill; the height
   she is drawn at comes from one lookup. So a wall up a hill is still a box at street level, and tests place her
   without a height. (CLAUDE.md "Coordinates"; round 32's traps; main.gd `ground_at`.)
2. **The ground answers in this order**: raised pieces first (steps, landings, terraces as rectangles with a top
   height), then the pavements (the kerb height, 0.12 m), then the town's level (0), then built level or ramped floors
   ("flats": a rectangle with a height at each end), then the finer ground along paths, then the height grid.
   (main.gd `build_ground_cells`, `ground_at`, `terrain_at`; rounds 11, 20d, 26, 35b.)
3. **The height grid is 1.65 m apart** (half a 3.3 m Barcelona tile; `world2d.py` `STEP`), and **three times finer
   (0.55 m) along the hill path and the park's paths**, because the coarse grid could neither keep a path level across
   nor show a narrow edge and a bank beside it. (Round 35b; world2d `GF_CELLS`, `GF_K` 3; scene `terrain_fine`.)
4. **One height per place**: where something is walked both on and under (a roof walk over a covered walk), the roof is
   listed as its own pieces with their height, and she is on it only when she is inside it and already near its height.
   (Round 34; scene `decks`, main.gd `deck_at`.)

## The grid's traps (each fallen into once)
5. **A level terrace sinks inside its edge** where the next grid sample is the lawn below (she fell into a square's
   sand by its wall). Every level or evenly ramped built floor states its own height (a "flat"), and its drawn plane
   covers the grid; the levelled ground under it sits about 0.3 m below the plane, which has skirts. (Round 26, the
   user: "I fell down the hole in the picture"; CLAUDE.md "Traps".)
6. **A slope must start hidden at least 1.8 m behind a wall or a terrace's edge**: the grid's samples are 1.65 m apart,
   so a level shelf that stops at the wall's foot leaves a slope showing in front of it. (Rounds 34 (the covered walk:
   "the hill's slope must start hidden behind the wall"), 36 (the café terrace reaching 1.8 m under the park wall).)
7. **Lay a path or ribbon on the higher of the two triangles** of each ground square, not on the smooth average, or it
   sinks below one of them on slopes. (CLAUDE.md "Traps"; `gz_top`.)
8. **Take a path's height along the line between its points, never from its nearest point**: from the nearest point the
   ground stepped a few centimetres at each point, drawn as shallow stairs across the track once the ground was fine.
   (Round 35b, the user: "The hill path used to be smooth, but now it looks bumpy"; `_on_line`; PATH_RULES A7.)
9. **Anything laid on a stepped piece of ground must copy the grid**, not the smooth formula (on Barcelona's off-map
   rise, stepped per tile, a smooth plane buried or floated by up to 12 cm). (Round 32; `west_bank_h`.)
10. **Built ground hides real ground under it that can read as a cliff**: under a bridge deck the riverbed's bank, behind
    a portico the ground under the house, beside steps their own edge. The game's slope rule must skip built floors,
    decks, doorsteps and steps (see 04 rule 62). (Rounds 32, 32b, 35b.)
11. **Don't blend a level in over the last few metres**: it makes a bank. Grade the whole approach instead (a gate
    approach that blended a 1.5 m difference at the end was a 40–50% bank that held her at the gate; graded at 13.5%
    through the quarter, it walks). (Round 26; north.py `hill_east`.)
12. **Where a level meets a wall or a road, check the seam**: a level cut beside a wall left a 2 m slot she fell into;
    a road's end taken from a plaza's level sank a gateway and left a 0.33 m lip; a 0.26 m step at a flat's edge walled
    her out; ground squares a wall crosses must be laid in small pieces, each at its own height. (Rounds 27, 34.)
13. **Steps stand on ground below them**: the ground under a flight is kept below the treads (0.45 m in the park) so
    no grass shows through the stairs. (Round 26, the user: "The grass covers the stairs".)

## Level streets, terraces, ramps and steps
14. **A street is level along its length; the climb is taken by ramps and steps between the level stretches.** Ask of
    every street: "how would someone push a pram along it?" (CLAUDE.md "Everything sits where it would in the real
    world", the user, 20 Oct 2026 (round 26); see also 05 rule 11.)
15. **On a hillside town, streets along the hill are level, the lanes up it ramp evenly, and a square between two
    levels is a terrace with broad steps** — or, where the user asks for it open, one floor on the ground's own gentle
    slope. Barcelona's Gràcia: level streets at 0, 2.6, 5.6, 6.4 m (`GRACIA_LEVELS`), a gate street climbing evenly
    (13.5%, under 25% everywhere). (Round 26, the walk review: "no more pavements you couldn't push a pram along".
    CHANGED for one square: round 26 made the Plaça de la Vila a terrace at 4.1 m with steps and walls; round 36
    (PATH_RULES H6.7) opened it: "no sunken terrace, steps or walls; one floor on the ground's own slope".)
16. **A steep footpath may climb where a street can't**, steepest in its middle and never over her walking limit
    (Barcelona: 1.4 m over the path behind the café block, 20%, to a gate's level). (Round 36, the user: "a steep
    street that goes up… between the wall and the building to bring up the level… for the next gate"; H6.6.)
16a. **Where she walks, she walks on what is drawn**: the height she is walked at and the surface drawn there agree
    within a few centimetres, checked along every steep path and step, so she never sinks into it or floats over it.
    (Round 38, the user: "She also sinks into the ground, walking down the steep path between the Gaudi Park and the
    building.")
17. **A terrace or café corner is levelled at the road's height**, the wall behind standing taller over it. (Round 36,
    H6.5.)
18. **A raised pad meets a footpath over shallow steps the full width of its front**, never as one bare face across the
    pavement (a station forecourt 22 cm up meets the street over two steps). (Round 32, the user: "There should be no
    parts jutting out".)
19. **Front steps go up, not down**: a landing and low steps (Barcelona's university: 0.06, 0.12 and a landing at kerb
    + 0.18), each walkable; a monument's terrace with its flight of steps all walkable. (Rounds 20d ("a strange
    knee-high ledge"), 23 (MNAC: "stairs not climbable"), 25 (the Sagrat Cor: "a small landing that you can walk up").)
20. **Things in a square stand on level steps where the floor slopes** (a fountain on a level step). (Round 36.)

## The one gradient rule
21. **Ground she can walk up and ground she can't must look different**: no "looks gentle, refuses her" and no "looks
    steep, lets her up". (Round 33, job 2: "ground she can't climb clearly steeper; one rule by gradient everywhere".)
22. **The rule as proposed and built**: walkable ground at most about 0.22 rise per metre; ground meant to stop her at
    least about 0.40 and looking it (a bank, rock, a wall, thick undergrowth); nothing between the two off the paths,
    except built steps and ramps. The game's limit sits in the gap (0.30, `MAX_UP`). **Reshape the ground, not the
    rule**: ease what is meant to be walked, steepen what is meant to stop her, and give it a look that says so.
    (Round 33, INSTRUCTIONS_round33.md §2.)
23. **Survey before changing**: colour every half metre by gradient (bands under 0.15, 0.15–0.27, 0.27–0.40, 0.40–0.55,
    over 0.55), paths, steps and doors drawn over it, and count the area in the unclear 0.2–0.4 band per area. Show it
    in plain words: "red you can't climb, green you can; the yellow is the unclear band". (Round 33; `--slopemap`.)
24. **Footpaths are graded evenly end to end** between their ends' heights, the ground blending to them 1.6–4 m out, and
    count as paths for the slope rule; a house's raised base gets a graded apron (0.2) down to its lawn so its door can be
    reached. (Round 33: "The hill below the Casa Museu walkable"; north.py `park_height`.)
25. **CHANGED in a walled park: no invisible walls.** There she may walk up anything she wouldn't slide down (0.55);
    where the ground must stay steeper, a low dry-stone wall with a coping stands along the foot of the bank (or a thick
    shrub for a short steep bit), so something she can see stops her. Elsewhere the 0.30 rule stands. (Round 35b,
    PATH_RULES G1, the user: "make a rule removing these from the park unless there is an object like a wall… when it
    does get too steep, put a small stone wall at the top"; `tools/park_slopes.py`: 8 100 half-metre spots stopped with
    nothing to see before, 5 after.)
26. **A big hill may not fit the rule**: Tibidabo's flank averages 0.39 from foot to funfair, so about 12 600 of its
    13 200 m² sit in the unclear band whatever the banks do. Then the choice is the limit's number, and it is the
    user's (still open: see below). (Round 33.)

## Banks
27. **Beside a hill path, uphill: a narrow green edge, then a bank just too steep to climb, then gentle ground behind.**
    The edge about 0.8 m (`VERGE` 0.5 past the path's edge); the bank 0.6 rise per metre over 2.2 m (about 1.3 m high:
    "past her limit, not a cliff", `UP_BANK`); behind it ground she never reaches, rising gently; a short steeper rise
    to the flat strip under the next leg's fence. Not steep, flat, steep. (CHANGED: round 25 had a 3 m walkable strip,
    round 35 2 m ("too much empty grass next to the path… should come closer"), round 35b the narrow edge ("you can just
    bring out the hill"); PATH_RULES C3; north.py.)
28. **Downhill: a level lip, then the bank down.** The lip 0.8 m of level ground past the path's edge, carrying the
    fence posts (`LIP`; round 26: the posts "sit on the slope, then need to just be moved a few inches up the hill so
    they are on the flat part"); then a bank of 1.3 per metre over 1.6 m (about 2 m, `BANK`, `BANK_W`). (Rounds 25, 26.)
29. **A bank she can't walk up wears the middle of the three wood-floor looks** (small clumps of grass among the
    needles), even in shade; on an open lawn a bank stays lawn. Never a "cliff" texture, never stretched lawn on a
    near-vertical face, never sand squares. (PATH_RULES C2. REVERSED: round 25 removed the blue speckled cliff texture;
    round 28 painted steep park banks bare sand; round 35b dropped that rule because it drew sand squares.)
30. **A bench or a work site beside a hill path sits in a small level bay**, the bank stepped back round it, so it can
    be reached and is never on the bank. (Round 35b, PATH_RULES C4: a workman "stood 1.4 m up the bank, out of reach".)
31. **Where she must get down a slope (to fetch something), there is one even slope she can walk** (about 0.22),
    blended in over 6 m at its edges, with no bank across it. (Round 35b, PATH_RULES E3: the new bank "shut the glade
    off from the path below, and the ball with it".)
32. **Ease every edge into the land**: a levelled place (a fair's plateau, a house's terrace, a square's back) eases into
    the hill over several metres (16 m below a fair's wall; 15 m behind a square; 6 m round a terrace), never a sharp
    step or a ridge with a hollow behind. (Rounds 34, 35 ("a 2 m ridge with a hollow behind"), 35b ("behind the top-left
    hairpin a broad hilltop, no ridge").)

## Hills: what stops her and what may be come down
33. **On a wooded hill she can't leave the path going up, but may come down through the wood**, sliding where it is
    steepest. (Round 22, the user: "steep wood: can't leave the path going up, can go down through the wood"; round 22b:
    "slipping down allowed".) Except the closed hill east of Gràcia, fenced from the Carmel road (round 39).
34. **A hill is only as high as it needs to be to stop her**, and must not rise above the thing it holds (a hilltop
    church: "Just enough hill so that Sandra can't walk up… don't have the hill going up past it"; the bank behind a
    plateau a few metres high, `CREST_H` 6 m; a closing rise "over 3 m: no walking up it", `TOP_HILL_RISE` 4.5).
    (Rounds 24, 25, 35.)
35. **The top of a hill is closed by a steep rise she can't climb**, running round to meet the end of the path's fence,
    so there is no way round. (Round 35, PATH_RULES E2.)
36. **A hill never drops off at the side** where it can be seen: the walk review asks of every picture "does a hill drop
    off at the side?" (CLAUDE.md "Review the world as Sandra sees it".)

## Retaining walls, park and garden walls
37. **Walls are solid things**: depth, a top and two faces, ends; they go down into the ground (no gap under them
    showing the sky); where she walks on top of one, its edge stops her. No single-sided walls. (Round 26, the user:
    "Some walls are single"; PATH_RULES G2, the user: "this wall needs to go to the ground… this wall has no depth, she
    can currently fall down".) (Round 39, the user: "The wall should not have a gap under it. Just make it go into the ground more": Gràcia's
    drystone wall reaches 0.4 m below the lowest ground under each piece.)
38. **A long wall is one continuous run** from pillar to pillar (or end to end), mitred at corners; its top rides over
    dips while its faces reach the real ground; it is solid metre by metre so she can walk right up to it (stopped
    within about 0.8 m). (Round 26: "The outer walls don't join… I should be able to run up to the edge of the barriers";
    round 27: "the wall sat OVER the hill"; north_build `wall_run`.)
39. **A wall sits on its own ground, between the two grounds it divides** (a park wall between its lawns and the wood;
    a drystone wall between the town's grass and the wood), never on a cobbled apron or over a path. Each gap is exactly
    one missing piece of wall, where a path passes. (Round 31, the user: "the wall stood on a cobbled apron, a dirt path
    ran under a wall segment"; all walls reviewed.)
40. **A retaining wall at a plateau's edge is low** (2.5 m), with a bank easing into the hill below — never a sheer drop.
    (CHANGED: round 34 had a 1.8 m thick, ~4 m terrace wall instead of "a sheer drop of up to 28 m"; round 35b, the
    user: "There is a sharp drop, it should be smaller" → 2.5 m and a 0.6 bank over 16 m; PATH_RULES E4.)
41. **Terraced beds are held by dry-stone walls only where a bed stands above the path along at least 7 m**; never
    loose blocks a metre or two long ("long lines only" for walls too). (PATH_RULES F5.)
42. **A small wall keeps a path off a drop to a garden** (brick, not bright, a coping, down into the ground). (Round 35b,
    G3: "small brick wall on the right of this path creating some distance from the austrian gardens".)
43. **Side and back walls of built pieces reach the lowest ground near them** (Barcelona: 0.6 m below it), so no foot
    floats. (Round 27.)
44. **No second wall beside a wall**, and **nothing standing about for no reason**: a parapet a metre from the park wall
    was removed; a railing and bench guarding nothing were removed. (Round 33 ("a second wall a metre from it"); round 35b
    F13: "remove the random brick wall and the fence that is doing nothing".)
45. **Walls on the ground are nothing to the camera** — only buildings are (`03_camera.md` #16). The flat colour the
    picture faded to behind a wall is gone from the game (round 40, the user: "That approach has completely failed…
    strip it out of the game"); the build no longer records walls' tops and colours.

## Fences and ropes
46. **A fence only beside a steep drop, on the side it falls to**: it starts where the drop is plain (0.9 m) and runs on
    while there is still a drop (0.4 m). Never on the uphill side, never beside gentle ground, never on both sides of a
    path. (Round 24, the user: "a railing to stop you from going down… on one side there is a steep hill and on the
    other is the railing"; round 35: "fences on both sides"; PATH_RULES D1; north_build `_drop`.) (Round 39: also where a wood is closed off — 05 #31.)
47. **The downhill side is the side the hillside itself falls to** (its slope before the path was cut, smoothed over
    ±9 m), not the bumps beside a post. (Round 35, H1: "The fence is now on the upper side".)
48. **Round the outside of a bend the fence carries on, then takes the shortest way to the foot of the bank she can't
    climb**, its last post against the bank's base, so there is no gap to walk round. **The inside of a bend stays open**;
    a fence arriving there turns just enough to close where the hill could be walked, then stops. (Rounds 25 ("continue…
    around the outer circle"), 26 ("You can be liberal on the inside of the bends"), 35 ("The fences can leave the path,
    when they go around the outer curve… The final pole can be right against its base. Then an 'invisible wall' makes
    sense"); PATH_RULES D2, D3.)
49. **Curves, never corners**; the rope follows the curve (posts placed along a finely traced line; at a tight tip a
    rope between posts cut across the path and closed it). (PATH_RULES D4; round 35.)
50. **Long lines only**: at least six posts a run, posts evenly spaced at most 1.8 m apart (`RAIL_STEP`), no gaps, no
    missing posts; every end against something solid or where the drop has died away. (Round 31, the user: "There should
    not be any places where there are two poles with a rope between. Not even 3… the fences should only be long lines to
    block people from falling"; PATH_RULES D5.)
51. **Posts stand on the flat beside the path** (Barcelona: 1.35 m from the path's middle, `RAIL_OFF`, on the level lip).
    (Round 26: "on the flat part".)
52. **No fence where there is nothing to fall from or another barrier already stands**: none at a hill path's foot (the
    first stretch, where the bank is low), none doubling another barrier (a railway's own lineside fence), none across a
    gateway (it ends against the wall beside it), none on a side left open on purpose (to run down for something).
    (Round 31: "Remove the fence at the bottom of the hill"; rounds 30, 24; PATH_RULES D6.)
53. **No path crosses a railway on the level**: the path bends up against the line's own fence (white post-and-double-
    rail along the cutting's lip, posts reaching into dips, tops smoothed). (Round 30, the user: "There should be no
    crossing. The path could curve at the furnicular but just comes up against its barrier".)
54. **Railings and parapets in a park follow the same rules** (only at a steep drop; long; ends against something).
    (PATH_RULES F8, G3.)
55. **Fence ropes cast no shadow** (their thin shadows flickered). (Round 26; `HillRope` in `NO_SHADOW`.)

## Ditches, trenches and cliffs
56. **No path in a trench or on a dyke**: the ground beside a path follows its even climb. (Round 22: "a regular
    gradient"; round 24: "not jagged due to the level changing"; PATH_RULES P1/A4.)
57. **No ditch along a wall or road**: a road follows the hill (Barcelona: smoothed over ±12 m, grade at most 0.16,
    rounded at the crests) and the verge between it and a wall is never below it; a sunken walk that dug a ditch under a
    wall was removed. (Rounds 28 (the SE wall's ditch), 34 (the road "rode up to 4 m above it in the middle, a ditch").)
58. **A viaduct needs ground that falls away under it** (3 m, `VIA_DROP`), but no trench dug beside it and no stranded
    columns. (Rounds 25, 28 ("random line of pylons"), 33.)
59. **No gaps someone could fall through**: every corner where ground meets a wall is looked at from above, not only its
    faces. (Round 35, the user: "a gap in the ground at Tibidabo that someone could fall through" — open squares at a
    wall's corners.)
60. **Cliffs only where they belong.** (REVERSED: round 24 curved the beach's end into a cove with low cliffs; round 25
    removed it: the beach runs straight and a boulder breakwater crosses it from the wood's edge out to sea; the wood's
    rise there at most 3 m, `EAST_RISE_MAX`.)

## Water's edges and the beach
61. **The shoreline is smooth, following the foam line**, the sand sloping into the sea from the coast's curve; she is
    stopped at the waterline (blocked per half tile), not by a sand wall. (Rounds 23, 24: "no sand wall".)
62. **Land slides under the water, it doesn't cliff into it**: a rise near the sea flattens to nothing over the last
    tiles, and a meadow runs under the water (to −0.9 m) rather than stopping in stepped terraces. (Round 32.)
63. **The beach carries on past the map's edge** rather than ending in squares. (Round 20.)
64. **Things on a beach sit on the sand**: towels each corner at the sand's own height, sunshades on sand with sand
    behind them and never in the water, nothing gravel or paved laid over sand (a path stops at the sand's edge).
    (Rounds 26, 33; PATH_RULES A9, the user: "Gravel can never go over sand".)
65. **Probe before adding water**: a pale band at a hill's foot looked like a stream and was the paving shading at a
    light map's edge; a footbridge was built and dropped. (Round 31.)
66. **A closed bridge's deck lands on the far bank and a worn track carries on**, so the old road plainly goes somewhere;
    it is closed by a guard's word and a real barrier. (Round 32.)

## The world's edge
67. **Nothing ends in a void**: the far land rolls on round the whole map (Barcelona: a soft green skirt to 1.7 km,
    meeting the grid's edge at its own height) under a haze reaching 900 m, the sky below the horizon the haze's colour.
    (Round 26, the walk review: "Does the far land go on, or end?") Round 40, the user: the edge sits well beyond
    anywhere she can run up to; from up high it just fades into the distance, with no clear break; cheap, not
    perfect (02 #121a).
68. **Unwalkable edges are thick wood or banks she can see**, not bare open ground with an invisible wall; trees out of
    reach are drawn as their tops only; far hills stay low enough that nothing shows over the trees. (Rounds 25, 27.)

## The map
69. **The map is the world itself, photographed straight down and painted**: the game takes an orthographic picture at
    midday with no fog and the people hidden (`--mapshot`), and `builder/stylise_map.py` paints it (detail evened out,
    colours warmed and strengthened, edges gently inked) on a cream paper border. (Round 15. REVERSED: round 12 showed the
    2D game's pixel map.)
70. **The map is the town; outlying parts are round pictures at the end of arrows.** The town fills the map; on the
    paper above it, an inked dashed arrow runs from where each way out leaves town to a round picture of where it goes,
    painted the same way, with its name (Barcelona: Tibidabo; Gràcia & Park Güell). Each round picture is a city block
    across (radius 105 px; the band 400 px). (Round 24, the user: "Make the map just a city map like it was (that was
    good), with arrows to the other sections, with the names at the end of the arrow. Maybe those sections can be
    stylised at the end of the arrows, but the city is what she needs a map for"; round 25 sizes.)
71. **"You are here" is a gently pulsing dot**; up in an outlying part it sits in that round picture; indoors it is at
    the door she went in by. (Rounds 12, 24; main.gd `map_px`, `world.json` `insets`.)
72. **Names are written by the game, not painted**, crisp at any size: a dot at every door that can be gone in by,
    coloured by kind (landmark, shop or café, friends' flats, other); names on little cream cards beside them, dots
    placed first, names avoiding them, a short leader line when a name sits away from its dot; streets and districts
    named; a key beside the map; the most important names placed first. (Rounds 15, 19.)
73. **Building names live on the map and on a small plaque beside each door, never floating over doors.** (Round 15.
    REVERSED: round 14 floated names over doors.)
74. **Repaint the map once a round, when the layout is settled**, not after every build. (CHANGED: round 19, the user
    asked for it after any change seen from above; the user, 20 Oct 2026: "repaint the map once a round"; CLAUDE.md
    "Pictures, not tests".)
75. **Opening and closing**: M (or Tab, or the touch MAP button) opens it, fitted to the play area; Esc, Enter, E or
    Space puts it away. (Rounds 12, 13, 15: "Esc and Enter close the map".)

## The screen: HUD, talk box, panels and menus
76. **The screen scales with the window** (Barcelona: laid out for 1280 × 800, or 800 × 1280 upright). (Round 19.)
77. **HUD places**: the mission's current step top left (one line, rule 10 #34), the clock bottom left, the money bottom
    right, the same size as the mission; the controls in two short lines along the bottom (hidden when upright); the
    frame rate small at the top right; the street or place name as a banner top middle, moving clear of a long mission
    line; small notices ("toasts") above everything. (Rounds 15, 18, 19, 22.)
77a. **The top-right line, for players: frame rate · the light's name (night, red, golden, day) · triangles.** The
    quality, bounce light and light shafts belong to the debug menu: shown there (a second line in the corner and rows
    in the menu) only when the debug menu is on (#84a), and their keys Q, G and V do nothing without it. (Round 41c,
    30 Oct 2026, the user: "balance quality, bounce light off, and light shafts should be part of the debug menu, and
    if the debug menu is not there, then they should not be there either. Frames per second, day, and triangles is
    fine.")
78. **The talk box is wide and low across the bottom**, under the middle of the picture where Sandra is (at most 1 040 px
    or 82% of the width; the whole width upright), the speaker's name in terracotta, the words in dark ink, normal
    weight, not bold. The clock and money hide while it shows. (CHANGED: round 19 made it about twice as big (24/28 px,
    up to 1 180 wide); round 20 "a little smaller", normal weight; now 21/24 px.)
79. **Words appear letter by letter at 60 a second**, as in the 2D game; a press shows the whole line; Esc moves talk on
    like Enter; in tests it is instant. The game clock stops while a talk box is open. (Rounds 12, 19; `TYPE_RATE`;
    engine/game.gd `tick`.)
80. **Choices**: W/S or ↑/↓, E to confirm, or the number; backing out picks the last ("no") option. Missions can't be
    refused: an offer is always taken up. (Rounds 6, 23: "No rejecting missions".)
81. **Panels are drawn like the 2D game's cards**: the backpack nearly full screen, the journal the same size; the
    journal groups entries under their missions, the current mission in ink, the rest grey, finished ones last with a
    tick, one page. Long titles are cut with "…" before the label is sized. (Rounds 16, 20, 22, 35. REVERSED: an
    achievements page existed until round 25, the user: "I don't want everything to become a competition".)
82. **Title screen and pause menu as in the 2D game**: the game's name, then Continue (with the saved time and money),
    Load game, and New game last (the old save set aside). (Round 41, the user: "The title screen needs to have load
    game as a third option… Make it the second option and move new to the bottom".) Load game lists the copies Export
    save made, newest first (when saved, and her money), with Back; picking one asks before replacing the game, then
    starts it where that copy left her. Esc with the mouse free opens the pause menu: Resume, Journal, Music, Export and
    Import save, New game… (with a confirmation); backing out of it resumes. (Rounds 13, 20, 20e.)
82a. **Continue puts her back where she was**: every save keeps where she stands (out of doors, her place and which way
    she faces; in a room, the room and the door she came in by), and Continue starts her there, not on the beach. The
    game saves every 30 s of play, on going into a building, on buying something, on finishing a mission, and on
    closing the window. (Round 38, the user: "when you go continue game, it starts again from the beach. It should
    start from wherever she was"; `main.gd save_spot`, `restore_spot`; `--spotsave`.)
82b. **CHANGED (round 40): the autosave keeps the spot of her last interaction; Export save keeps exactly where she
    is.** The game still saves her progress all the time (every 30 s, on buying, on missions, on closing), but the
    place it keeps is where she last did something — went through a door (coming out, just outside it), talked to
    someone, picked something up, looked at something, bought something — so Continue never puts her back somewhere
    she wandered into and got stuck. Export save (the pause menu) is the manual save: it keeps her exact spot, and
    Import save brings her back there. (Round 40, the user: "the autosave should be the most recent object
    interaction. The manual save should be whichever location she was at. So if I were to restart it, and go back to
    the autosave, after being stuck in this location, it should take me back up to the door"; "export, save is the
    manual save".)
82c. **H: "Take me home".** A key of its own, shown on the controls line: it asks "Take me home?" with Take me home /
    Stay here; Take me home puts her outside her own front door, facing it. Not while talking, riding a ride or in a
    scene. (Round 40, the user: "create a new shortcut in the main shortcuts and have it say, take me home? And then if
    the user presses it, there's a confirmation, take me home or stay here".)
82d. **The title screen sounds like the view, not like where she stands**: the music, with a soft, far-off city hum
    under it, and no sea or street from her own spot. No place name at the top while the title shows. Once Continue
    or New game puts her in her place, that place's sounds (the sea, the street, a room) fade in over a second or two
    and its name comes up as usual. (Round 41, the user: the title had "the music and the ocean… Is that because
    behind the scenes, Sandra is still at the beach"; they chose "music plus a soft city hum on the title, then her
    place's sounds fade in once she starts. And the place name only once she's playing".) **Silence while it loads**:
    nothing plays behind the Godot loading screen; the music and the hum fade in with the title's first picture (or,
    with no title — a fresh start — her place's sounds with the first picture). (The user: "when the game is
    loading, when we have the Godot screen… have no sound during that point".) That first fade-in is quick, about half
    a second (then the user: "make the fade in 70% quicker" — 1.5 s to 0.45 s).
83. **Tests keep their own save**; the player's save is never touched by a test. (Round 15.)

## The debug menu
84. **P opens a debug menu drawn as a panel**: go to a place, set the time, +€50 / +€500, get the bicycle, get a pass
    for gated places, next time of day, outfit, music, quality, bounce light, light shafts, quick walking, touch
    controls on or off. A world supplies
    its own list of places. (Rounds 17, 20, 26: "Put the park and lift pass into the debug screen"; panels.gd
    `debug_list`; `main.debug_places()` still holds Barcelona's places, to move into the world.)
84a. **Hidden from players**: P does nothing, the touch controls have no DEBUG button and the help line doesn't name
    it. The menu is still in the game, untouched: start Godot with `-- --debug` (or any test run) and P and the DEBUG
    button come back. (Round 41c, 30 Oct 2026, the user: "hide it. Just take it out from the options so it can't be
    used, but keep it there in the background"; main.gd `debug_on`.)

## Sound
85. **Tests are silent**: the master sound is muted when a test starts, and the battery runs with no audio driver.
    (Round 26, the user: "stop the sound in the tests"; tests.gd `start()`.)
86. **Soft and quiet, nothing that sounds like pain**: footsteps "you notice, you don't hear" (−26 dB); notice dings
    turned down (round 23: "Quieter dings"); no yelp or tumble sound ever (round 28: "Remove the whelp… It shouldn't
    seem to hurt"). (ambience.gd `FX_TRIM`.)
87. **The town sounds like a town**: a looping street soundscape outdoors, muffled indoors, the sea louder towards the
    beach; background car and scooter passes stay even with no traffic on the streets. Music follows her (a street tune
    outside, a softer one at home); N turns it off and on. All sound is made by the builder (`builder/build_audio.py`).
    (Rounds 4–6, 13, 33.)

## Unclear or not yet decided (for the user)
- The walking limit outside walled parks: keep 0.30 (A) or raise it to 0.40 (B)? Asked in round 33
  (`workshop/screenshots/round33/slopes_choice.jpg`); never answered. With A, most of a big hill like Tibidabo's flank stays in the
  "unclear" 0.22–0.40 band, which the one-rule idea says should not exist off the paths: is that accepted?
- Should the park rule (climb anything she wouldn't slide down, low walls where it's steeper) apply to other gardens and
  parks in a new city, or only to a walled park?
- Is there a number for "a street someone could push a pram along"? Barcelona's gate street climbs 13.5% and the
  footpath behind the café block 20%; the game's walking limit is 30%.
- Where a ramp must become steps: is there a gradient above which a footpath should be stairs instead?
- When should a slope be held by a retaining wall and when by a bank outside parks (the hill uses banks, the park walls)?
- A fence's end turning to the bank: round 35b says within 4 m, round 35's rule within 7 m. Which?
- Can she ever go into the water (paddle at the edge), or is the waterline always a stop?
- For a new city's map: which outlying parts get a round picture, and how many fit on the paper band?
- Map labels' order and the list of districts are still written for Barcelona in the engine: should each world list its
  own most-important names?
