# 05 · Streets, pavements and paths

How streets, pavements, squares and paths are laid out and how they meet, in any world. Barcelona's full, place-by-
place path rules (the hill path, Park Güell, Gràcia's quarters) are in `docs/PATH_RULES.md`; this file states them
generally, with that file's rule codes in brackets so each can be traced. **Whenever the user says anything about
paths or streets, this file (and PATH_RULES for Barcelona) is updated first, clashes settled, then it is built.**

## A district is laid out on one grid
1. **One grid of shared lines.** Blocks, their pavements, the carriageways and squares sit on the same lines; a
   block's pavement edge is the next street's kerb. Everything lines up: no jogs, no slivers of leftover ground, no
   odd-sized gaps. (H1; the user, round 36: "Most of my problems are with its proportionality… things not lining up
   and weird gaps".)
2. **Blocks are square-ish and evenly spaced**, gaps between them a normal street's width; a block never sticks out
   past its row. (Round 36.)
3. **A street's width fits what uses it.** Main streets (with trees and lamps on their pavements) about 5 m of
   carriageway between 3 m pavements; lanes about 2.4–3.4 m of carriageway between 1.8 m pavements. A street keeps
   its width along its length: rows on both sides face it straight, so it never tapers. (Round 28: "is still
   narrowing".)

## Carriageways, pavements and kerbs
4. **Roads are roads; everything else paved is footpath.** In an old quarter, cobbles (setts) only on the
   carriageways, each at its own width; every other paved surface is one panot footpath. (H6.1, the user, round 36:
   "just have the cobblestone roads as roads. Have everything else as a footpath".)
5. **One road continuous round the blocks.** A carriageway doesn't stop in a square of paving; it carries on round the
   blocks and bends with what it passes (a wall, a gate) rather than ending. (H6.2.)
6. **Pavements are seamless.** A pavement wraps its building's corners as one surface; where pavements of different
   widths meet at a corner, the corner is exactly as deep as each side's pavement — nothing pokes out. Pavements that
   share a line are one continuous run, no narrow gaps between them. (H2, round 36: "the footpaths at the corners of
   the building are wrong. It should be simple to make a footpath"; "there had better not be the very narrow gaps".)
7. **Kerbs only on true outer edges**: where footpath meets a carriageway, grass or open ground. No kerb lines inside
   one paved surface. (H2.) Every footpath beside a carriageway stands one kerb above it with the same little raised
   lip all along, in every district — never flush with the road in one street and kerbed in the next (round 38, the
   user, of Gràcia by the park: "All of these footpaths in this district should be slightly raised with the little
   lip… You just have to be more consistent with them").
8. **Pavement and road touch.** No strip of grass or bare ground between a carriageway and its pavement. (Round 36.)
9. **Where a street ends against a footpath, the footpath runs through and the cobbles stop on it** — no paving laid
   across the street's mouth like a crosswalk; the street's cobbles flow straight into the next street's. (H3, round 36:
   "remove these footpaths so that the cobblestone lines up with the main roads, no need for a crosswalk here".)
10. **Where one district meets another, the road carries on.** A pavement never runs across the end of a road: the
    old quarter's cobbles go on until they meet the other district's asphalt. Check every street end on the district's
    edge. (Round 36: "the footpath crosses the road. The road should continue so that the cobblestones in this
    district join the bitumen in the eixample district… There are other examples".) Only the road itself carries on:
    its cobbles never run sideways along the other district's pavement past a corner — the buildings on either side
    keep their footpath all the way round (round 41, the user: "here there is cobblestone cutting across the footpath…
    The buildings should be surrounded by footpath").
11. **A street is level along its length**; the climb is taken by ramps and steps between level streets ("how would
    someone push a pram along it?", 20 Oct). A street may be steep only where it is meant to be a climb (a steep
    footpath up to a gate, round 36), never steeper than she can walk (30%, `MAX_UP`; inside a walled park 55%).
12. **No traffic.** The streets have no cars, buses or bus stops; bicycles parked and ridden, people walking.
    (Round 33: "take out the cars, bus and stops".)

## Edges of a town
13. **A footpath runs along a park's or town's boundary wall**, at least 1.8 m wide, so the cobbles never touch the
    wall (1.2 m where a lodge stands out from the wall). Where a block stands closer to the wall than a road needs,
    footpath fills the gap from block to wall. (H6.3.)
14. **The town's edge against nature** is a kerbed footpath, then grass; a low drystone wall may stand on the grass
    with gaps only where a street's end meets a path into the wood. (H3, H4.)
15. **A gate has a small forecourt of footpath the width of its gateway**; the road's kerb eases round it in a gentle
    curve and back, the footpath along the wall keeping a steady width either side. (Round 36, the user's purple line:
    "straight and then… it curves around the entrance".)

## Surfaces and how they meet
16. **Each surface keeps to its ground.** Dirt is worn grass: it stops at paving or gravel, never lies over it.
    Gravel stops where sand begins; gravel never lies over cobbles. Where a footpath meets a gravel road the footpath stays
    on top, kerbed like any footpath by a road (#7), and the gravel's end tucks under its edge (**REVERSED** in round
    39, the user: "The gravel should go under the footpath when it joins it"; round 36 had it "under the gravel"). The footpath runs *under* the cobbles at a street's end. (A8, A9, B1; round 31: "The dirt path never
    goes ONTO the road… it is under grass"; round 36: "Gravel can never go over sand", "That new path should go under
    the gravel, not over".)
17. **A gravel road starts where the town ends**, on a clean line, its end tucked under the footpaths' edges there (round 39) — never over
    the cobbles. (H6.4.)
18. **Joins look like one path.** Where two paths meet, the lesser runs on *under* the greater to its middle line, a
    little lower, so the greater path's own ragged edge is the only edge seen — never a strip of grass between, never
    its edge over the gravel; no slivers, overshooting ends, wedges of grass or second edges showing through. Every
    inner corner is rounded (about 0.85 m) at any angle, fitted to the real edges; a path that runs on into another is
    one surface round the bend; its width doesn't breathe within 3 m of a join. The Austria Gardens' formal crossings
    stay square for now. (A3, A8; **round 39**, the user: "Check the paths in the forest and where they cross. I have
    asked you again and again and it is still not fixed. They should look natural without the jagged bugs";
    `builder/trails.py junction_fillets`, `chain_paths`; checked by `junction_check.py` in the build's review.)
19. **No lips where a path meets paving**: no step, ridge or kerb-like edge; the path ends exactly where the paving
    starts, with no gap of grass. (B1, B2.)
20. **Sand colour only on paths and paved places**, never as patches or squares on grass. (C1.)

## Paths through nature
21. **A path is one piece and goes somewhere**: one unbroken surface end to end; each end meets another path, a gate,
    a door, stairs or paving (dead ends only in a wood's glades). (A1, A2.) Where a path stops in the open (on a beach,
    at a glade) its end is rounded off, a half circle as wide as the path, never cut square; the rounded tip ends
    where the square end did, so it never reaches over the sand. (Round 37, the user: "the path coming out of the forest
    should be rounded at the end"; `builder/trails.py` `round_end`.)
22. **Even underfoot and smooth to the eye**: level from side to side (at most ~10 cm lower on one edge), an even
    climb along, no ripples or lumps (measured every quarter metre: no more than 3 cm off the smooth climb). Never
    steeper than she can walk. (A4, A7.)
23. **Nothing on the walking width**: no post, fence, bench, tree, bush or sign. Measured from the drawn edge of every
    path, walk, gate path and road, each plant is kept off by its own spread plus 0.3 m; the low edge plants start 0.3 m
    off the gravel; no tuft or flower on a path's drawn edge. (A5; round 39, the user: "The palm tree and foliage is in
    the path"; `trails.path_edge_d`.)
23a. **Paving is never broken through**: a path's ground and gravel never rise through a paved floor (a plaza, a
    porch, a square); under it they run on below it, and the gravel's end meets the paving's edge; no kerb stub where a
    building or a path's mouth covers it; no bare earth showing at a join. (B1; round 39, the user, inside the main
    gate: "There's this brown stuff there, and the gravel path goes on top of it when it would have to go underneath
    the paving. And then there's a white brick there.")
24. **Walkable both ways**, without being stopped, and no leaving it where there is a drop. (A6.)
25. **One path, not two side by side.** Never two parallel paths where one would do. (Round 36: "there should only be
    one".)
26. **Path materials by kind**: a hill path is a worn dirt track; a park's or a wood's main walks are gravel (pale
    crushed stone, crisp edge); spurs into a wood are gravel or dirt; a little-used way to a door is patches of worn
    grass, not a path. (F9, F11.)
27. **A path goes right to the door of every house it serves**, ending at the doorstep or the steps' foot, no strip of
    grass between. (F10.)
28. **Uphill beside a hill path**: a narrow green edge (~0.8 m), then a bank just too steep to climb, then gentle
    ground she never reaches. Not a 2 m flat strip. (C3.)
29. **A bench beside a path sits on the grass in a small level bay**, facing back over the path to the view, nothing
    planted in front of it. (C4.)
30. **No bikes in a walled park**; she is told why at the gate. (F14.)

## Fences and walls by paths
31. **A fence only beside a steep drop, on that side**; never on the uphill side, never both sides at once. (D1.) A rope fence also closes off a wood she is not to enter, along the footpath or road beside it (round 39, the
    user: "the rope fence (from the hill) starting at the stone path and going up around the hill and then sealing off
    the top at the gate… so Sandra can't get into that area"). (So: beside a steep drop, or closing off a wood — round 39.)
32. **Fences curve round the outside of a bend** and end against the bank; the inside of a bend stays open; no right
    angles; long even runs (posts at most 1.8 m apart), never short loose pieces; every end against something solid.
    (D2–D5.) Two fences that meet join into one continuous line, never two ropes side by side (round 41: "That
    fence should be continuous down the hill").
33. **No invisible walls.** Wherever she is stopped, something she can see stops her: a wall, a building, a fence, a
    stair's side. Ground too steep to walk is regraded where it reasonably can be; otherwise a small stone wall stands
    along the top of the walkable ground. (G1.)
34. **Walls are solid things** with depth, down into the ground, and stop her at their edge when she walks on top.
    (G2.) Walls run in long lines, never loose blocks a metre or two long (F5, D5).
35. **Nothing standing about for no reason**: a fence or wall that guards nothing is removed. (F13.)

## Squares
36. **A square is open**: one floor from road to road, no walls round it, no steps across it unless the ground forces
    them (and then full-width and shallow); if it lies on a slope, it follows the ground's own gentle slope. (H6.7, the
    user: "It should feel a bit more open".)
37. **Things in a square fill it in proportion, with an empty strip round the edge**: trees, benches, the fountain or
    monument and café tables spread over the floor, nothing hard against its edges. (Round 36: "spread out the things…
    so that it fills the square more fully, but still have a strip around the ends where there is nothing".)
38. **A square's floor is flat or evenly sloped**, its furniture on level steps where needed (a fountain on a level
    stone step on a sloping square).
39. **A square keeps its life**: trees, benches, a centrepiece, café tables along one side, lamps. (H5.)

## Unclear or not yet decided (for the user)
- Asphalt or cobbles where an old quarter's street meets a modern district: should the cobbles always run to the
  district's edge, or stop at the old quarter's own boundary line?
- Crosswalks: the city's asphalt streets have zebra crossings; should an old quarter ever have them?
- Minimum and maximum widths for a new world's main streets and lanes — are Barcelona's numbers the standard?
- How steep may a deliberately steep footpath be (Barcelona's is 20%, under the 30% she can walk)?
