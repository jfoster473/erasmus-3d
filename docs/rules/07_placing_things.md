# 07 — Placing things in the world

Purpose: how every object that stands in the streets, squares, parks and on the beach is placed — street lamps,
street trees, benches, café tables and parasols, bins, planters, bike stands, signs and plaques, shop wares, stalls,
kiosks, fountains, beach sunshades and towels — so that a new city (for example Valencia, with its own layout) can be
furnished from these rules alone. The one idea behind all of them is the user's: **everything sits where it would in
the real world**, and nothing she can see is something she can walk through. Barcelona appears only as the example.
Numbers are the ones the build uses now, with the file or constant they live in. Where a rule was changed later, the
later round wins and the change is marked **(changed)**. Distances in the city builder are often in 3.3 m tiles;
they are given here in metres too. Paths, kerbs, fences and slopes have their own rules (`docs/PATH_RULES.md`);
people and story items are in `10_people_story_missions.md`.

## A. The test every object must pass

1. **Everything sits where it would in the real world.** Lamps stand at the kerb, never in a wall; trees stand on
   pavements wide enough for them, clear of the walls, their crowns never in a building; benches stand on the ground;
   bushes grow on earth, not on paving; a station stands on a pavement with a way in and out; hats sit on heads.
   (The user, round 26, 20 Oct: "Everything sits where it would in the real world"; CLAUDE.md "The user and how to
   work with them".)
2. **Before any picture goes to the user, ask of every object in it: does its placement make sense?** Does it float,
   poke through, sit where it couldn't (a bush on a pavement, a station in a field), look too big or too small, too
   close or too far from its neighbours, off balance with what is around it? (The user, round 26, the walk review;
   round 35: "things sticking out or a poor balance based on what is around it".)
3. **Nothing stands about for no reason.** A wall, fence, bench or railing that serves nothing is removed. (Round 35b,
   PATH_RULES F13, the user: "remove the random brick wall and the fence that is doing nothing outside that
   building" — Casa Trias's stone bench and lookout railing went.)
4. **Don't add things nobody asked for; whatever is added must be tasteful and subtle.** Round 24 added "magical"
   extras (glade sunbeams, glowing mushrooms, lanterns on the hill rail, "Stop and look at the view") and round 25
   took most of them out: "magical" meant deeper scenery, not gadgets. When fixing, move or change what is there
   rather than add. (Round 25 lesson; round 27, the user on the beached boats: "Everything added should be
   tasteful"; round 35: "don't add new things, just shift and modify existing things that are not correct".)
5. **A misplaced thing is a bug; a new look is a choice.** Floating, sunk, blocking, walk-through or mis-placed
   objects may be fixed straight away and then shown; a change of look is shown as game pictures first and built only
   after the user picks. (INSTRUCTIONS_round33 standing rules; memory "confirm before building".)
6. **Fix the rule at its source, not one object at a time.** When a kind of object is wrong in one place it is wrong
   by its placing rule; every piece of furniture asks the same shared checks (the crossing check, the door check, the
   keep-clear circles), so the next object can't forget. (INSTRUCTIONS_round33 job 5 step 4; round 33 `crossing_clear`
   in `builder/build_assets.py`.)

## B. On the ground, on the right surface, inside nothing

7. **Nothing floats and nothing is sunk.** An object's base sits on the ground under it, within about 3 cm
   (INSTRUCTIONS_round33 job 5). Something lying flat takes the ground's height at each of its corners (beach towels:
   `world2d.py towel()`, round 26 — a flat box had stuck out of the slope "like a ramp"). On hills, everything stands
   on the ground's own height function, not a fixed height (round 20d: tufts and ferns on `ground_z`; round 24: trees
   had been buried where the ground rose). Hedges are laid in short lengths at the lawn's own height, not as long
   floating frames (round 28).
8. **Each kind of thing stands on its own kind of ground.** Street lamps, street trees (in pits), benches, bins and
   café tables on pavement; bushes and shrubs on earth or lawn, never on paving; beach sunshades and towels only on
   sand (towels refuse any tile that isn't sand: `world2d.py towel()`, round 27); boulders never on a street or a path
   (round 26: the 2D map's boulders fell on Gràcia's new streets, "a bush on the crossing"; round 36: a boulder tile on
   a gravel path became forest floor).
9. **Nothing stands inside anything else** — not in a wall, a house, a tree trunk, a bench, a café table or a rack of
   bikes. Found and fixed: a lamp halfway inside a house and trees piercing walls on Carrer de Larrard (round 26: trees
   now 2.3 m out from the fronts on a 3 m pavement); two lamps inside Gràcia's houses (round 35: moved to the kerb in
   front); the coin telescope standing in a bench (round 35); a bin inside a café table on La Rambla (round 23); a bin
   under a rack of parked bikes (round 35); a café parasol's pole up through a street tree (round 35).
10. **Nothing overlaps another object.** When a layout change puts two things on one spot, one slides aside. (Round 19:
    four Rambla benches landed on lamp-post tiles and now slide half a tile, `world2d.py LAMP_TILES`: "nothing else in
    the city overlaps".)
11. **Nothing stands on stairs or steps.** Pots, planters, agaves and coloured pieces are cleared off every flight and
    porch. (Round 33, the user: "coloured items sitting on the stairs"; the dragon stairs, porch and side stairs
    cleared.)
12. **Anything she is meant to use stands where she can get to it and see it.** A cat to look at sat in a closed
    courtyard (round 35: moved to the park lawn by the pool); a sign and plaque stood behind columns (round 35: moved
    to the porch); four room decorations were placed 400 m away because a room's points are world points, not offsets
    (round 35, checked by `--storybits`). Every street plaque is checked to be visible when the world is built (the
    build prints `PLAQUES checked N hidden K`).
13. **Each thing that answers E has its own spot.** Two usable things on one spot make E pick either (round 35: the
    notebook lay on the drawer's spot; moved to the chest's left end). In rooms, a thing must not be the one chosen
    when she looks at its neighbour (round 23: looking at the bed picked the bedside table).

## C. Pavements: the walking line, the kerb side, doorways and crossings

14. **Keep the walking line clear.** Nothing stands in the 1.5 m walking line along a pavement, footpath or park path;
    street things go to the kerb side and the walkway runs along the house fronts. (INSTRUCTIONS_round33 job 5, the
    user: "nothing blocking walking paths"; round 33 `kerb_side()` in `builder/build_assets.py`: the 2D map's bins and
    signs "stood in the middle of the pavement, in everyone's way".)
    **The exception: a workshop that works on the street.** Bicis Jordi works on its pavement: its bikes stand in a row
    under the awnings facing the wall, either side of the door and well clear of it, never overlapping, with a small
    solid workbench and tools against the wall; people can't walk along the footpath there (round 38, the user: "I'm
    happy for [Jordi's] shop to be an exception to the rule and make people unable to walk along the footpath… make it
    look like he's doing something on the pavement outside"). On a narrow pavement (Gràcia's 1.8 m) the walking line gives way to the lamps' 0.8 m from the kerb: it may be
    narrower there (round 39, the user: of the two, the walking line gives).
15. **How far in from the kerb each thing stands** (city pavements 3.3 m wide; `builder/build_assets.py`, the
    pavement loop's `at(s, d)` with d in tiles): street trees 0.25 tile (0.8 m); planters 0.22 tile (0.7 m); bin bays
    and bike stands 0.25 tile (0.8 m); 2D-map bins and signs 0.2 tile (0.66 m, `kerb_side(x, y, 0.2)`); 2D-map café
    tables 0.38 tile (1.25 m, the tables on the kerb side, the walkway along the fronts); corner lamps 0.15 tile
    (0.5 m). Benches are the exception: 0.58 tile (1.9 m) in, by the house fronts, facing the road (`street_bench`). (Round 37/38: corner lamps 0.83 m in, every lamp at least 0.8 m — rule 33.)
15a. **A landmark's front is not hidden behind a street tree** (round 41, the user: "move the second tree, the one
    right in front of the building, out of the way": the tree before Casa Batlló's middle). Such trees are left out
    by where they stood (`build_assets.py TREE_SKIP`), made and dropped so every other tree comes out as before.
    Nor a doorway (#16): the tree before the door at La Rambla's north-east corner went across the road to the Cafè
    Berlín's pavement, just north of its door (round 41, the user: "there's a tree in front of the front door. Could
    you just move that across the road to in front of the Berlin Cafe? Just to the north of its door").
16. **Doorways are kept clear.** Nothing — no tree, bench, bin, planter, café table, bucket, A-board or sign — stands
    on the pavement in front of a door. Every doorway reserves a circle of 0.7 m round a point 0.7 m out from it
    (`builder/kit.py door_space()` → `keep_clear`); shop wares check `clear_of_doors` (their own radius + 0.6 m); the
    2D map's things keep at least 1.5 m from every doorway point and slide along the front in 0.8 m steps (up to 4 m)
    to the nearest clear place (`world2d.py _clear`). A corner whose house has its door on the corner gets no
    bougainvillea and its lamp to one side (at 0.84 of the corner's length instead of the middle). The build prints
    `DOORS n doorways, k with something in front`; k must be 0. (Round 21, the user: doors "behind plants" right of
    Carrefour and on a block's corner.)
17. **Crossings are kept clear.** Nothing stands on a zebra crossing or in its landing — the strip of pavement as wide
    as the crossing (2.7 m) plus 0.3 m, where people step off and on. The check is `crossing_clear(x, y, half)`
    (`builder/build_assets.py`): clear by 0.41 + 0.1 tiles (1.35 m + 0.33 m) plus the object's own half-size from
    every crossing's line. Every bench, planter, bin bay, bike stand and café table asks it, and so do the 2D map's
    things (café terraces by their spread, 0.65 tile). Street trees keep 0.62 tile (about 2 m) from a crossing's line
    (`tree_ok`). (Round 33, the user: "Some [benches] are sitting in front of the cross walks"; "there are flower boxes
    there now".) Note: the round-33 instructions first proposed "nothing within 2 m of either end of a crossing"; the
    built rule is the landing above, and `--placecheck` tests a landing 2.5 m on from each end. The built rule is
    current.
18. **A thing that doesn't fit slides; it doesn't jump.** It moves along the house fronts first, then along either
    street axis, and must stay on the pavement it started on — never slid into the road (`world2d.py _clear`, round 33).
    Sandra's own street's bench slides 0.2 tile at a time towards the block's middle until clear of the crossing
    (round 33).
19. **If there is no clear place, leave it out rather than block a crossing or a door** (round 33: a café terrace with
    no clear spot is left out). **Exception (changed in round 35):** a café terrace that can't find a spot 1.5 m from
    the street trees keeps its old place, because "taking them away was not wanted". So: doors and crossings always
    win; spacing from trees gives way.
20. **Keep-clear circles.** Some things reserve room around them so nothing else is put there (`KEEP_CLEAR` in
    `builder/build_assets.py`, checked by `clear_at(x, y, r)`): a café table 1.6 m, a bike shop's display bikes 0.9 m,
    a shopkeeper's standing spot 0.6 m, the player's front door 0.75 m, a bench 0.3 m. Every new placed thing checks
    them.

## D. Spacing between things

21. **Lamps stand at least 3 m from trees and never under a crown.** (Round 36, PATH_RULES H6.8, the user: "the
    streetlights and the trees are too close together".)
22. **Lamps are not crowded together.** A lamp too near another place's lamps is dropped (round 36: the city's edge
    lamp beside the Plaça del Sol, "just too close to the others" — `world2d.py` skips edge lamps within 7 m of
    `north.SOL_LAMPS`). Spacing in use: Gràcia's long streets one lamp every 16 m, alternating sides
    (`north_build.py`); a footpath up beside the wood one every 20 m (round 36, the user's lamp plan); Carrer de Larrard
    one lamp per ~7 m of front alternating with trees (`north_build.py`, `int(L / 7.0)`).
23. **Street trees in a row** stand 1.15–1.45 tiles (3.8–4.8 m) apart (`builder/build_assets.py`, the "trees" kind);
    a "sparse" stretch has two or three, wide apart. Two trees must not stand right behind one another (round 36, the
    user: "trees too close together, remove one").
24. **Other spacings in use**: planters at least 1.8 m from a tree's trunk (Sandra's street, `build_assets.py`); café
    tables 1.5 m from street trees where they can be (round 35, `world2d.py _clear`); bins and other 2D things at
    least 1.4 m from parked bikes (round 35) and clear of café tables by the table's radius + 0.7 m (round 23, the
    user: "a bin stood in a café table on La Rambla").

## E. Solid: nothing she runs through

25. **Anything that looks solid stops her, on foot and on the bike.** (Round 33, the user: "She can run through the
    bike lock stands/bikes. This should not be possible… review every single object like this".)
26. **How a thing is made solid.** A thing is solid only if the builder writes it as an obstacle post (`scene
    obstacles`, a radius; the game makes a post of radius r × 0.75, 1 m tall: `engine/main.gd add_post`), a box
    (`blocked` / `solids`), a tree or lamp entry (posts of 0.25 m and 0.14 m), or gives it a body of its own. **Any new
    street object must write one of these in the builder**, or `--solidcheck` will list it. (Round 33; CLAUDE.md
    round 33 notes.)
27. **The sizes in use** (radius before the game's ×0.75): bench 0.75; planter 0.85; bin bay three posts of 0.55 along
    it; bike-stand hoop 0.32 each; parked bike a 0.32 × 1.1 × 1.75 m box (`engine/street_life.gd add_bike`); flower
    bucket 0.3 each; fruit stand three posts of 0.7 along its 2.7 m; café table 1.0 (Gràcia's: a 1 × 1 m box); A-board
    0.35; corner bougainvillea planter 0.95; a street-plaque post 0.18; 2D-map bins, signs and umbrellas 0.6, other 2D
    things 1.0; beach sunshade 0.5; volleyball posts 0.3; a kiosk a solid box its own size (`world2d.py`).
28. **What is not solid**: grass tufts, flowers, leaves overhead, shadows, painted lines and low kerbs she steps over
    (INSTRUCTIONS_round33 job 3). People and her own parked bike are solid but "soft": pressed against one for 2.2 s
    going nowhere, she slips through for 1.3 s; this never applies to buildings, bins, walls or anything else (round
    27, `engine/main.gd keep_off_people`, `soft_pass_t`). (Round 39: trees are the one exception — pushed for 3 s, 04 #74.)
29. **Making things solid must not close a way.** After adding bodies, no new pockets and every pavement still
    passable: re-run the stuck sweeps and `--seams` (round 33: obstacles 199 → 261, 0 new stuck spots).
30. **Passers-by walk round the same solid things** (their list in `engine/people.gd`; see file 10).
31. **Solid to Sandra, never to the camera.** Placed things — kiosks, stalls, booths, benches, planters, walls — stop
    her, not the camera; the camera's walls are buildings only (`03_camera.md` #16, round 40: "treat it like an actual
    camera… it doesn't automatically come in zoom in on her simply because there is a hedge behind her"). (Replaces
    round 35's "a kiosk's footprint stops the camera".)
32. **How it is checked**: `--solidcheck=<file>` tries her body at every 0.2 m of every ground-standing object's
    footprint, judged by its shape 0.25–1.2 m above the ground, and lists what she fits inside, by kind; it must be
    empty. `--solidwalk=<dir>` shows her stopping (on foot she stops touching a bike, 0.46 m centre to centre; on the
    bike she pulls up at a stand).

## F. Each kind of thing

33. **Street lamps** stand on the pavement at its kerb side, never mid-pavement, on the road, on grass or sand,
    against or in a house. City corners: a lamp at each chamfered corner, 0.83 m from the kerb (**changed** in round
    33 from 1.0 m in: "out of the way"; **changed** again in round 37 from 0.5 m, where its 0.3 m foot hugged the kerb
    edge — the user: "keep the lamp poles on the pavement away from its edge"). Every street lamp's foot stays clear of
    the kerb edge: its centre at least 0.8 m in (`--placecheck` "from kerb"). Narrow pavements (Gràcia, 1.8 m): 0.8 m in from the kerb like everywhere
    (**changed** in round 38 from 0.35 m, set in round 33 when they had stood mid-pavement or hugging the houses — the
    user: "Did you check all of the streetlights in the new district and that they are not sitting right at the edge of
    the pavement? We already did this rule"). The seafront: on the promenade, 1.3 tiles back from
    the sand (round 33: their feet stood on the sand's edge). The city's edge: on the edge footpath at its grass side,
    never across a way into the meadow — at least 1.5 m from a footpath into it (round 20). A gate's lamp at the
    block's kerb (round 36). Lamps never at the foot of a stair where they block it (rounds 27 and 32b: a porch lamp
    stood in the only gap to the side stairs). A lamp may stand against a wall where the user asks for it (round 36:
    "another street lamp up against the wall" at the café terrace).
    Not too many: in Gràcia (round 38, the user's picks on the plan) ten lamps came out — 128, 133, 140, 123, 119,
    124, 110, 118, 137, 135 on `workshop/screenshots/round38/plans/gracia_lamps_v3.png` — and the Plaça de la Vila
    keeps three, at its top-left, top-right and bottom-right corners (round 38, the user: "There are also a lot of
    lamps in that square… In that whole area, there's too many lamps").
34. **Exception: lamps by the woods.** Lamps at the wood's entrances and on the grass by the footpaths beside the
    forest are fine where they are (round 33, the user called "the park's lamps by the forest" fine). Note the
    history: round 20 put the meadow's lamps on the pavement; round 31 moved the Alzina lane's lamps onto the grass by
    its footpath; round 36 replaced that lane and its lamps now stand on the wood-side footpath, every 20 m. Current:
    on the footpath.
35. **Street trees** stand in tree pits on pavements wide enough for them, at the kerb side, clear of the walls (on a
    3 m pavement, 2.3 m out from the fronts), their crowns never in a building, never in a crossing's landing or a
    doorway (rounds 21, 26, 33). A street may carry a full row, a few trees far apart, none (people walk there
    instead), or trees with benches, planters, bins or bike stands between them, so the streets aren't all the same
    (HISTORY tenth round, the pavement planner). Keep trees the user marked (round 36: the Travessera's trees, the
    user: "keep some trees around there… the three on the right should only be one").
36. **Trees beside paths in a wood or park**: within 2.2 m of a path only narrow-crowned kinds (stone pines,
    cypresses), others at least 3.2 m off, because a spreading crown hung at head height over the path (round 33,
    `north.py park_wood`). No trees at a stair's foot, on a porch's face or inside a covered walk (round 33). Trees keep
    8 m clear of a railway line (round 30). In the woods trees keep back from glades and path crossings so the sun gets
    in (round 20: 0.9 and 0.85 tiles).
37. **Benches**: in the city, by the house fronts facing the road (rule 15); on a promenade, facing across it; on a
    terrace or lookout, facing the view (`world2d.py`). On a path, never on its surface: in a level bay beside it,
    2.1 m from the path's centre line (**changed** in round 30 from 1.25 m, which left one on the path's sand at a tight
    bend; round 35b put them in level bays with their view kept clear). A park's benches come with bins (round 26).
    A bench seat for a seated character is 0.44 m (round 9, Montse's bench). The bench beside the player's own front
    door was removed (round 33, the user: "Remove the bench from outside of her building"). A bench faces what a
    person would sit to look at (REVIEW_whole_game: the forecourt bench faced the wrong way).
38. **Café tables and parasols**: right outside the café, either side of its door, the door left clear — 1.5 m out
    along the front from the door, then every 2 m, 1.25 m out from the front (`builder/kit.py cafe_terrace`), turned a
    little at random, close together, ready for people to sit at; on a wider street, on the kerb side with the walkway
    along the fronts (rule 15). A parasol stands only over a café table (or a beach towel: rule 44). Never in the road
    (round 36: the Cafè del Parc's tables stood in the road and moved to a level terrace). A café may have a seated
    customer (round 36, `scene sitters`; file 10).
    Each chair faces its table, tucked in or a little drawn back; a seated customer sits on a chair at its seat
    height, never sunk into the ground (round 38, the user: "The chairs in the alfresco dining area are not facing the
    tables, and the lady is sinking into the ground").
    No café tables or chairs on a sloping street: where they would stand in the air they are taken away (round 38, the
    user: "the chairs in this area on that steeper street are up in the air… it might be problematic having them where
    they are. So maybe they just get removed").
38a. **Built things she can't walk into are solid all round** — a platform, a cairn, a porch's columns and balustrade —
    leaving its steps' openings free. (Round 39, the user, of the three crosses' platform: "this should be a solid
    object"; of Casa Trias's porch: "These should be solid. She should not be able to walk through them.")
39. **Bins**: a bin bay (two containers with a planter at each end) stands in a gap between the street trees, in the
    line of the trees, so the pavement stays clear (HISTORY seventh round; `builder/kit.py bin_bay`); single bins at
    the kerb side (rule 15).
40. **Planters and flower boxes** at the kerb side, never where a crossing meets the pavement (round 33).
41. **Bike stands**: steel hoops 0.9 m apart at the kerb side with one or two bikes locked to them, front wheel
    towards the road (`bike_stand()`); each hoop solid and each bike a solid box; other things keep 1.4 m from the
    bikes (rules 24, 27).
42. **Shop wares** go out only from open shops and not every shop puts them out: florists' buckets (each solid), fruit
    crates (solid along their length), book stalls, chalkboard A-boards (solid, chalked both sides, read with E), a bike
    shop's bikes in front of its window; all clear of the doors (rule 16; rounds 19, 21, 23, 33). A closed shop has its
    shutter down and nothing outside (`builder/kit.py signs_and_wares`).
43. **Signs, plaques and names**:
    - Street-name plaques on the corner houses, one for each street, 2.92 m up; where there is no corner house (a park,
      a landmark in its grounds), on a slim post of its own 0.6 m out from the block's edge, solid (round 35: on the
      edge they ran into the Sagrada Família's corner columns). Every plaque must be visible (rule 12).
    - **Every sign can be seen, with nothing in front of it**: street plaques, shop names, door plates, brass plaques
      and park boards. No planter, climber, bench, bin or bike stand stands on the pavement right in front of a sign,
      and on a corner the lamp stands to one side of a shop's name, not in front of it. **Only what blocks the sign is
      taken away or moved; nothing else near it changes** (the street trees stay, their crowns above the names; the
      corner lamp moves along the corner, it is never removed; the city's other placings stay exactly where they were).
      The build checks each sign from Sandra's eye height, straight on and from either side along the
      pavement, and prints `SIGNS checked N hidden K` (K must be 0). (Round 37, the user: "there's a plant box and a
      plant in front of the sign on the block across from the university on the corner… All signs should be visible
      and have nothing blocking them." It was a corner bougainvillea and the corner lamp in front of a gelateria's
      name. The first fix also shifted a street tree and other things along the street, and the user objected: "I just
      wanted nothing blocking it. It didn't mean remove EVERYTHING near it.")
    - Building names are not floated over doors (round 18, the user didn't want that); they go on the map and on a
      small brass plaque beside each door, on a post where stonework would swallow it (round 18).
    - In the city, a small painted plate hanging on an iron bracket beside every door that has no shop sign of its
      own, 2.55–3.2 m up, the name on both sides; shops keep their fascia names (round 33; round 34 settled it: "a small
      painted plate on the bracket, no edged board").
    - In a park, a tall dark post with a small plain cream board and the name alone in large dark letters, beside each
      way in, solid (round 34, the user: "Just make a decision about the signs yourself"); placed off the path's width,
      close to the house it names (round 35b, F12: "move the sign to the other side of the stairs and closer to the
      building").
    - **(changed)** The cellar's trap doors got a SOTERRANI sign in round 33; round 34 removed it ("No sign at the
      cellar's trap doors"). Current: no sign there.
    - Fingerposts point at their real targets (round 27). The 2D map's signs are boards on posts, blue with a cream
      face and the heading in dark letters, read with E (round 15).
44. **Beach**: sunshades only where people sit — on the sand above the waterline, with a towel or two under them,
    never in the water, on the promenade or on a path (round 33, the user: "There is an umbrella at the beach"; two had
    landed alone on the promenade and were moved down onto the sand, with sand behind them). They stand in loose
    groups as bathers group, thinning towards the ends, never on a breakwater (round 26; round 36 moved them off the
    moved breakwaters). Lone towels lie nearer the water (2.2–3 tiles back). A volleyball net's posts are at its ends
    (round 35: they stood 10 m apart with the net floating between). No boats on the sand (round 27, the user: "weird
    red and blue boxes"). (`world2d.py`, the beach's life.)
45. **Kiosks, stalls and booths** stand on paving, solid to her (rule 31; not to the camera). A closed ticket office may
    stand against its station's wall to show it is shut (round 28: the TAQUILLA booth, "an entrance where you can
    purportedly buy a ticket, but it is closed"). A funfair's booths, kiosks, poles, benches and flower boxes are
    re-spaced with the funfair when it changes size (round 35b).
46. **Fountains and centrepieces** stand in the open middle of a square, a fountain on a level step (round 36, the
    Plaça de la Vila).
47. **Corner climbers** (bougainvillea): on some corners (about 4 in 10), never on a corner with a door, and kept to
    their own corner, thickening upwards — never spreading over shop names, awnings or plaques (round 35).
48. **Coin-operated lookouts** (a telescope) stand at the railing where the view is, in a gap of the flower boxes, not
    in a bench and not set back from the edge (round 35).
49. **Story items lying on the ground** (wildflowers, mushrooms, a ball, a key) follow their own rules in file 10
    (section "Things lying about").

## G. Squares

50. **A square is furnished from its middle outwards, with an empty strip round its edges.** Its things fill the floor
    but keep a strip of at least 1.2 m clear round the edges; its lamps stand 1.5 m or more in from the edges. (Round
    36, the user: "spread out the things… so that it fills the square more fully, but still have a strip around the
    ends where there is nothing… in the current proportion"; `north.py sol_spread`, everything ×1.3 from the floor's
    middle; PATH_RULES H6.8.)
51. **What a square holds** (both Gràcia squares as the examples): a centrepiece in the open middle (an astrolabe
    column; a fountain on a level step); trees at its corners or round its edges (four at the corners; six round the
    edges); benches; café tables along one side; lamps at the middle of each side or along two edges between the
    trees (the Plaça de la Vila: three, at its corners — round 38), always 3 m from the trees (round 36, PATH_RULES H5, H6.7, H6.8; `north.SOL_LAMPS`).
52. **A square is one open floor** — no walls round it, no sunken terraces or steps unless the ground needs them
    (round 36: the Plaça de la Vila opened up). Its life is kept when it is re-laid (H5: "The square keeps its life").
53. **A forecourt before a gate or station** is paved, with a way in and out for what it serves; nothing in it stands
    in the road (round 26 gave the park gate's forecourt trees, lamps and a bench; round 36 removed the tree, lamp and
    bench that stood in the road).

## H. In rooms

54. **Furniture comes from the room's list and stands where a person could use it**: not in front of a window (round
    20: a cupboard in front of Alice's window), with room to walk round shelves (round 24: the library), a staircase in
    a corner, "not an eyesore" (round 24), candle racks facing the room with their backs 0.3 m off the wall (round 35),
    everything inside its own room (rule 12).
55. **Everything she can look at says something of its own** — no thing answers only "Nothing unusual" (round 35: the
    library's reading tables). Big furniture is reached from further off (bed 1.9 m, desk 1.75 m, kitchen and sofa
    1.7 m, cupboard 1.6 m, else 1.45 m: `engine/main.gd nearest`, round 23).

## I. How placement is checked

56. **Look as Sandra sees it.** Walk the routes at her eye level, stop where the scene changes, read each picture as a
    critic would (rule 2); overhead pictures are allowed for layout. (Memory "walk review", round 26.)
57. **Measure.** `--placecheck=<file>` lists every lamp, tree, obstacle and 2D-map thing with the ground under it,
    its distance to the kerb and to the fronts, and whether it stands in a crossing's landing (round 33: 133 breaches,
    3 left that were looked at and kept: a sign flat on the university's wall at a corner, a tree beside its crossing).
    `--spotshots=<dir>:<list>` takes game pictures of listed spots. The build prints the DOORS and PLAQUES counts.
    `--visit` (round 35) walks up to every one of the 410 outdoor things and 154 room things, uses it and walks into it.
58. **Repaint the map** once a round when placement changes are visible from above (CLAUDE.md).

## Unclear or not yet decided

1. **Benches by the house fronts**: city benches stand about 1.9 m in from the kerb on a 3.3 m pavement, by the
   fronts. Does that keep the 1.5 m walking line clear, or should the walking line be along the fronts and benches go
   to the kerb side like everything else?
2. **The crossing distance**: the round-33 proposal was "nothing within 2 m of either end of a crossing"; the build
   keeps the crossing's landing (its width + 0.3 m) clear and the check looks 2.5 m on. Which should be the rule for a
   new city?
3. **Café terraces that can't be 1.5 m from the street trees** keep their place (round 35). Is that the rule
   everywhere, or should they move to another stretch of pavement?
4. **Lamps on grass**: allowed only beside the woods (the user's "park next to the forest"). Are lamps on grass
   acceptable in parks generally, or only there?
5. **Things on hill and park paths**: `--placecheck` knows only the city's pavements. Does the 1.5 m walking line rule
   apply to park paths and the hill path in the same way?
6. **One lamp spacing**: lamps are 16 m, 20 m or one per ~7 m of front in different places, and 7 m was "too close" by
   the Plaça del Sol. Should a new city have one minimum and one usual spacing for lamps?
7. **Beach sunshades** were meant to need "a towel or lounger"; only towels are built. Should there be loungers?
8. **Sign styles for a new city**: are the city's hanging plates, the parks' post signs and the 2D-style blue boards
   the defaults for every city, or should each city choose its own?
9. **The 3 cm ground tolerance and the 1.5 m walking line** were written in the round-33 instructions as proposals
   ("check with the user if one seems off") and never explicitly confirmed. Are they the user's numbers?
10. **The Parc de la Ciutadella has no trees** (its trees are planted at its old rows): open since round 32b, pictures
    first.
11. **Sitters on benches**: the whole-game review suggested a few people sitting on benches (beach, squares, lookouts);
    only one café customer exists. Wanted?

## Things to find on the ground (round 41)
- **Coins lie on the road's surface**, a little off the middle of a lane, never on a crossing's white lines, and glow
  softly, twinkling, so they can be spotted (the user: "move the coins away from the white crossing lines and make them
  glow a little bit… I wanted the coins to stay on the bitumen. Not necessarily right in the middle of the road. It can
  be a little random"; `game.gd spawn_at`, the coin's glow in `make_ground_node`). The glow faint, under half what it
  was (round 41, the user: "make the money not glow as much").

- **A bin keeps 2.6 m from a rack of parked bikes**, so the way past them stays open (round 41, the user: "the bin east
  of the Cascada Park is right next to the bikes, and so it's blocking the footpath. Move it somewhere else";
  world2d.py). Tomàs's cap lies among the first bushes at the wood's edge, still in sight (the user: "move the
  fisherman's cap slightly closer to the forest. So it's sitting between some undergrowth, but still visible").
- **Nobody paces in front of a landmark's door**: a walker whose stretch passes the university's door walks on La
  Rambla's west pavement instead (round 41, the user: "there's someone who's always pacing in front of the
  university. Could you just move them somewhere else in the city?"; build_assets.py `WALKER_SKIP_DOORS`).
