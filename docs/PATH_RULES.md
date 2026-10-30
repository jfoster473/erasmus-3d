# Path rules: the hill path and Park Güell

The user (23 Oct 2026): "I have kept asking you to fix the paths down the hill and the paths through the gaudi park.
You have not succeeded… tell me what the rules are… there should be overlapping rules for paths." Then they gave
changes to the first draft: "I want you to be clear about these rules and then use them when we proceed."

**Whenever the user says anything about the paths, these rules are updated first (and any clashes with the other
rules found and settled) before anything is built.** (The user: "If I tell you anything, you have to update these
rules before implementing it and review any clashes.")

**I review the paths myself; the user does not mark maps** (the user: "I don't want to have to mark it on the
map"). Each review: the plan maps from above, and pictures as she walks every path both ways, each picture read
against every rule below, plus the measured checks (`tools/path_rules.py`).

**These rules are the test for every path change on the hill and in the park. Each fix names the rule it serves;
each review checks every rule on the user's marked maps. No play-throughs and no test runs until the user says they
are 100% happy with the paths.**

## Round 39 overrides (read with the items below)
- **A8**: the lesser path runs on *under* the greater to its middle line; only the greater's edge shows (05 #18).
- **H3 / H6.4**: the footpath stays on top at kerb height to the park wall; the Carmel road's gravel starts under its east
  kerb (05 #16, #17).
- **D1**: a fence also closes off a wood she is not to enter (05 #31): the rope from the stone wall up the Carmel road's
  outer edge to the park wall beside the top gate (the user: "Yes").
- **H6.7**: the Plaça de la Vila has three lamps, at its top-left, top-right and bottom-right corners (07 #33, #51).
- **H6.1**: kerbs on every true outer edge (05 #7), not only by a carriageway.

## The maps to draw on
`workshop/screenshots/round35/path_maps/`: for each area an overview (`*_0_overview.png`, the four quarters boxed) and
four quarters (`hill_1..4.png`, `park_1..4.png`: 1 top left, 2 top right, 3 bottom left, 4 bottom right). Straight
down from the game itself, trees and plants hidden, north at the top, 10 m squares lettered across and numbered down
(a quarter shares one square with its neighbour). Yellow line: a path's middle (the hill path marked every 50 m from
the bottom; the park's paths numbered 1–14 and "walk", the covered walk). Red line with dots: rope railing and its
posts. Magenta: anything she can't walk through. Dark red: the park wall. Orange: the road outside it.
Remake: `python3 tools/plan_maps.py views <dir>`, the game's `--views=<dir>/tiles --viewfile=<dir>/views.json
--maptrees`, then `python3 tools/plan_maps.py sheets <dir>` (about a minute). Park path numbers on the map are one
more than in the code (map 1 = `PARK_PATHS[0]`).

## A. Every path (hill and park)
- **A1 One piece.** A path is one unbroken surface from end to end: no gaps, no squares, never sinking under grass.
- **A2 It goes somewhere.** Each end meets another path, a gate, a door, stairs or paving (dead ends only in the
  hill wood's glades).
- **A3 Joins look like one path.** Where two paths meet, their surfaces run into each other at the same height, their
  middle lines meet, with no step, seam, wedge of grass or anything jutting out.
- **A4 Even underfoot.** Level from side to side and an even climb along, with no bumps, dips, trenches or dykes.
  It may give a little where it must (the user: "can be relaxed slightly if necessary, but not by much"): no more than
  about 10 cm lower on one edge than the other, and the climb changing no more than gently. Never steeper than she
  can walk.
- **A7 Smooth to the eye.** (The user, 23 Oct: "The hill path used to be smooth, but now it looks bumpy.") The
  surface, and the ground along its edges, follows the path's even climb in one smooth line: no ripples, steps or
  lumps you can see along it, however fine the ground under it is drawn. Measured every quarter metre along the
  middle and both edges: no rise or fall of more than 3 cm against the smooth climb, no kink. (Clashes checked: A4
  allows a little tilt across, not bumps along — they agree; the finer ground along the path (made for A4/C3) must
  not bring back the path's own unevenness — the ground beside it may be rougher, the path never.)
- **A5 Nothing in the way.** No post, fence, bench, tree, bush or sign on the walking width.
- **A6 Walkable both ways.** She can walk the whole path up and down without being stopped, and can't leave it where
  there is a drop.

- **A8 Clean joins.** (The user, 24 Oct, on the forest's junctions: "the paths in the forest ... still have some
  weird joins". ) Where two paths meet they join end-on, one surface flowing into the other: no stray slivers,
  no overshooting ribbon ends, no second edge showing through. The lesser path ends at the greater one's edge
  (as the dirt rule of round 31: it stops at the road, never lies over it). This holds at every join in the
  forest and on the hill.
- **A9 A surface keeps to its ground.** (The user, 24 Oct: "Gravel can never go over sand.") A gravel path ends
  where the sand begins — at the beach it stops at the sand's edge, and the sand itself is the way on. The same
  sense everywhere: dirt stops at paving (B1), gravel stops at sand, nothing lies over the ground that replaces it.

## B. Where a path meets paving ("concrete": the town's pavement, the funfair, the park's plaza, porch, square, covered walk)
- **B1 The path ends exactly where the paving starts**: no gap of grass between, and the path never lies on top of
  the paving.
- **B2 No lips.** The path and the ground beside it meet the paving's edge smoothly, at its height: no step, no ridge,
  no kerb-like edge.

## C. The ground beside the paths
- **C1 Sand colour only on paths and paved places**, never as patches or squares on the grass.
- **C2 A bank she can't walk up wears the middle of the three wood-floor looks** (small clumps of grass among the
  needles), even where it lies in shade. Not lawn, not bare sand, not the darkest needles. (Settles C2 against C1 and the "no squares" rule: on Park Güell's open lawns a bank stays lawn — the ground's
  material changes in whole pieces of ground, so swapping it on a bank drew blocky patches; in the wood and on the
  hill the floor's own light map gives the bank the middle look, with a soft edge.)
- **C4 A bench — and the workmen's site by the path — sits on the grass beside the path, never on it, in a small level
  bay** (the full play-through: with the hill brought in close, Toni stood on the bank, out of her reach) — the bank stepped back round
  it — on the uphill side, or at a hairpin on the inside of the bend, facing back over the path to the view. (Settles
  C3 against the benches: with the hill brought in close there is no flat grass for a bench without a bay.) No tree
  or bush in the bay or in the view in front of the bench.
- **C3a The hillside is rounded, never folded** (round 41, the user: "This is really jagged here… It's not too bad that
  it's steep, it just shouldn't be so jagged. It should be more rounded"): away from the path (from 5.5 m off it,
  fully by 9 m) the banks' creases and peaks are smoothed, so no tall sharp triangles; the path, its edge, the bank's
  foot and the benches' and work site's bays keep their own shapes. The work site's bare earth has a round, uneven
  outline, not the ground's squares ("should be more rounded at the edges").
- **C3 Uphill on the hill path: a narrow green edge, then the hill brought in close.** (The user: the 2 m strip "is
  too wide… you can just bring out the hill.") Going up from the path's edge, across to the next leg above:
  1. a narrow green edge, about 0.8 m (the same as the flat strip the fence posts stand on, downhill);
  2. a bank steep enough that she can't walk up it — just past her limit, not a cliff;
  3. behind it, ground she never reaches or sees, rising gently;
  4. a short steeper rise up to the flat strip under the next leg's fence.
  Not steep, flat, steep: one bank she can't climb, a gentle slope, a brief steeper rise. Where no leg lies above,
  the gentle slope runs on into the hillside.

## D. Fences (the hill path's rope railing; any park railing)
- **D1 Only beside a steep drop, on that side.** A fence stands only where the ground falls away steeply beside the
  path (hill and park alike), on the side it falls to. Never on the uphill side, never beside gentle ground, and
  **never fences on both sides of the path** at the same place.
- **D2 Round the outside of a bend.** At a bend whose outside is the drop, the fence carries on round the outside of
  the curve, and then, from its end, **takes the shortest way to the foot of the bank she can't climb**, its last
  post against that bank. So there is no gap she could walk round.
- **D2a At a hairpin the rope goes all the way round.** (Round 41, the user at two hairpins: "this fence should continue
  where I've marked it in red… there shouldn't be a double fence there"; "Again extend the fence".) The rope on the
  outside of a hairpin carries on round its tip and about 5 m along the leg it turns into ("you can also just pull the
  fence a little bit back… But the fence ends way too far up and there's a big slope") — there the outside is the
  leg's uphill side, which D1 otherwise keeps clear: at a hairpin's tip D2a wins — then turns off to the bank as D2.
  One line, no doubled posts at its end. **A bench comes first** (round 41, the user: "That fence… comes too far
  around the hill. It should meet up with the hill before the bench. Currently it's blocking the bench"): where a
  bench's bay lies along the leg, the rope stops short of the bay and turns into the bank there; a rope never runs
  between a bench and its path. (Then: "It just needs to continue almost straight until it hits the wall [the hill]… once it comes around the
  bend, then it just goes into the wall… Now you've got it running along the hill. 1, 2, 3, 4, 5, 6 poles can be
  removed. And then just move the other one out a little bit and it's up against the hill": the rope goes round the
  tip and one post on, no further along the leg; from there it runs on almost straight, away from the path and well
  clear of any bench, to the hill's foot, its last post against it.) (Not at the funicular bend, where the white fence is the barrier: D6, and that
  fence runs 3 m further along each leg and turns out to the cutting's edge, round 41.)
- **D2b …and the rope between the legs comes down to it.** (Round 41, the user: "extend this fence too. This is just
  behind the other"; "the fence should continue much further down… right to where she currently is"; "I can cycle up
  it".) On the higher leg the rope along its downhill side, between the two legs, runs on down to where D2a's rope
  stops, so the bank between the legs is closed off. This replaces D3 and H3 at a hairpin; elsewhere they stand.
- **D3 The inside of a bend stays open.** A fence arriving at the inside of a bend **turns just enough to close the
  gap where the hill could be walked up** — a short, gentle turn, no more than the job needs — then stops, leaving
  the bend open, so the fence of one leg and the fence of the next never stand facing each other across the path.
- **D4 Curves, never corners.** A fence turns in a smooth curve. **No right-angle turns**, no sharp corners.
- **D5 Long lines only.** No short loose pieces, no gaps, no missing posts; posts evenly spaced, at most 1.8 m apart.
  Every end finishes against something solid (a bank, a wall, a building), or where the drop beside the path has
  died away so there is nothing left to fall from (the inside of a bend, the foot, the glade's edge). A fence runs on
  while there is still a drop beside it, and starts only where the drop is plain. (Settles D5 against D3 and E3: at
  the inside of a bend and at the open glade there is no bank to end against.)
  **Where one fence meets another they join into one line**: the next fence starts at the last one's end post, never
  running on beside it (round 41, the user, on the two ropes side by side above the workmen's barrier: "That fence
  should be continuous down the hill").
- **D6 No fence** at the hill path's foot (the first 2.5 m of its climb, where the bank beside it is low: the user,
  round 31, "Remove the fence at the bottom of the hill"), round the funicular bend's tip (its white lineside fence is the barrier there: the rope on the bend's outside
  runs to the white fence's end and stops against it, never doubling it), in the funfair's gateway (the rope ends
  against the funfair's wall beside it), or on the glade side of the top leg (so she can run down for the ball).

- **D7 Park Güell, the hairpin by the east side stairs** (round 40, the user's red line: "put a rope fence here";
  "She's stuck here"; "my red line corresponds to where there's a steep slope that she might slide down"): a rope
  round the outside of the Casa Museu path's hairpin — from a few metres along the upper leg (the dip at the stairs'
  foot, where she slid down and couldn't climb back), round the turn, and along the lower leg's downhill side (the
  ground falls 2 m towards the porch), ending against the low stone wall below the path (D5). Only that: agreed on a
  map first (round40/fence_proposal_map.jpg); the knoll fences of a wrong try were removed ("You need to remove all
  the fences you just made"). Mark a fence on a map for the user before building it.

## E. The hill path itself
- **E1 One steady climb from the town's paving to the funfair's paving**; each leg keeps its own level, even where
  another leg passes close above or below.
- **E3 The ball's glade is open** below the top leg, down to the leg below (she runs down for the ball): no fence
  across the grass at its ends (D1 — the 40 m straight fence from the top leg down to the leg below is gone). And
  from the leg below, the glade's ground rises gently into the wood: no uphill bank there (C3 gives way to E3 — the
  full play-through found the new bank had shut the glade off from the path below, and the ball with it).
- **E4 The funfair sits back on its hill** (the user, 23 Oct: "rearrange the funfair so that it doesn't come out too
  far into the hill… There is a sharp drop, it should be smaller… There was too much space up there. It shouldn't feel
  cramped, just not the wide open space as much"): its plateau 76 x 43 m (was 90 x 55), pulled back 12 m from the
  south and 12 m from the east; the carousel in its empty north-west corner, beside the church (the user: "Move the
  ferris wheel into the empty corner… Sorry, I meant the merry go round. Ferris wheel stays"); below its edge a low terrace wall (2.5 m) and a bank that eases into the hillside, not
  a sheer face; the rides, the station, the telescope and the people re-spaced on it, the church where it is. (Clashes
  checked: B1/B2 — the hill path still arrives on its west side, where the plateau is unchanged, and ends at its paving;
  D5/D6 — the rope still ends against its west wall beside the gateway; the funicular's portal and top station move
  north with the edge, the track running on into the hill, so no path rule meets it.)
- **E2 Tibidabo's top:** the ground rises from the top leg to a flat wood, closed by a steep rise she can't climb,
  which runs round to meet the rope at the first bend.
- **E1a The foot and the works** (round 40, the user): the path rises evenly straight out of the pavement — no dip
  ("Please fix this so that the path doesn't go down then come back up"), and comes down to it in one easy sweep, not a
  hook ("It should simply curve around to where it joins… you can move the end of it a bit to the right": its foot
  7 m further east); no ditch anywhere between the pavement and the hill along the city's edge ("could you fix up that
  ditch right along between the paved footpath and the hill?"); the pavement's back edge runs straight past
  the foot to the funicular station ("it should just be a line and not have the jagged squares"). The works barricade
  is temporary — free-standing red-and-white barriers on feet, nothing set in the ground, the rope fence carrying on
  past it ("change the barricade to be a movable temporary one… The color that it has is fine"); one workman this side
  of it, one just beyond it, talked to across it (rule 10, the workmen).

## F. Park Güell
- **F1 One network after the user's aerial view:** every path starts and ends on another path, a gate, a door, the
  square's ways in or the covered walk.
- **F2 Each footpath is an even climb between its two ends**; the two carriage roads over the viaducts follow the
  hill's own lie.
- **F3 The covered walk's floor is level with the Nature Square**; the paths at its two ends meet it at its height
  and width (B1, B2); its roof is walkable, level with the hill behind.
- **F4 In the wood both edges of a path are planted**; beside an open lawn, a looser edge.
- **F5 The switchbacks climb between terraced beds**, held by dry-stone walls only where a bed stands above the path
  along at least 7 m (never loose blocks a metre or two long: D5's "long lines only" for walls too).
- **F6 The Austria Gardens' beds are solid**, with gravel walks round them. The walks are level from side to side and
  slope only as the hill does, down to the south (round 40, the user, on the east walk riding up the bank below the
  covered walk: "The paths around the part should be relatively flat, just sloping down the hill. So the green part
  needs to be steeper, so that it is like a normal gravel walkway around the gardens"): the whole garden, walks and beds,
  lies on the garden's own even fall; where the hill rises beside it, the bank starts at the outer walk's edge and takes
  the climb, steeper, never the walk (A4). The ground there is laid three times finer so the walk's edge stays crisp.
  (Clashes checked: G5 — the bank is the garden's edge, not a pocket: she walks away along the walk; G1 — no wall at
  its foot.)
- **F7 The gate paths run through the gateways** onto the road.
- **F8 Railings and parapets in the park only where there is a steep drop** beside the path (D1–D5 apply).
- **F9 Park Güell's paths are gravel, not dirt** (the user, 23 Oct: "Please make the paths in the garden gravel, not
  dirt" — all of the park's paths, they confirmed): pale crushed stone with a crisp edge, as the wood's gravel walks,
  the carriage roads and the gate paths too. The hill path stays a worn dirt track. (Replaces round 24's "pale sauló"
  park paths. Checked against the other rules: gravel is a path surface, so C1 holds; the joins (A3) and the edges
  where the paths meet paving (B1, B2) are unchanged by it; the park's paths stay wider than the hill path.)
- **F10 A gravel path goes right to the door of every house in the park** (and the user, for the Casa Museu: "make the
  path run a bit under casa museu gaudi so that it runs to the door" — the gravel reaches the house's wall at its door,
  no strip of grass between) (the user: "PLEASE make sure that the
  gravel path goes to the doors of the houses in the gaudi park"): Casa del Guarda, Casa Larrard, the Casa Museu,
  Casa Trias (its portico steps), each path ending at the doorstep or the steps' foot (B1, B2). Where a door opens on
  paving (the Hypostyle Room's, off the porch), the paving is the way to it.
- **F11 The cellar's way: worn grass from the front** (the user, 23 Oct: "the direction… is good, but… I am trying to
  describe a part of the grass that gets walked over, but not too often, so it gets worn down without making a big
  trail. Also make it curve around a little bit at the cellar door so it approaches it from front on"): not dirt and not
  patches — a band of grass, a little paler and thinner where feet go, earth just showing through here and there, its
  edges fading into the lawn, fainter in places along it. Patchy (the user: "a bit more patchy instead"): worn
  patches of grass with whole lawn between, not one band; it joins the gravel path, starting under its edge. From the gravel path at Casa Trias's portico steps, along the
  front, round the west corner, swinging out a little so the last metres come straight at the cellar doors. (Clashes
  checked: A1 "one unbroken surface" is for paths — this is worn lawn, not a path; C1 — no sand or dirt colour on the
  grass; A5 — nothing planted on it.)
- **F12 Casa Trias's sign on the east side of its steps, close to the house** (the user: "move the sign to the other
  side of the stairs and closer to the building"), off the path's width (A5).
- **F14 No bikes in the park** (the user, 23 Oct: "make a rule that the bike is not allowed in the park"): she can't
  ride in through any gate, can't get on her bike inside the wall, and is told why at the gate ("No bikes in Park
  Güell"). The Carretera del Carmel outside the wall and Gràcia's streets stay rideable. (Clashes checked: none with the
  path rules; it matches the funfair, already no-bike.)
- **F13 Nothing standing about for no reason** (the user: "remove the random brick wall and the fence that is doing
  nothing outside that building"): the stone bench and the iron lookout railing in front of Casa Trias are gone — the
  railing stood beside gentle ground (F8, D1).
- (Dropped: round 28's "a bank too steep for grass is painted bare sand" — it broke C1 and made the sand squares by
  the covered walk. C2 replaces it.)

## G. Walls, slopes and invisible walls in Park Güell (the user, 23 Oct, on pictures)
- **G1 No invisible walls in the park** ("they are annoying. make a rule removing these from the park unless there is an
  object like a wall"): wherever she is stopped, there is something she can see stopping her — a wall, a building, a
  fence, a stair's side, a bed's edging. Ground she can't walk up is regraded so she can, as far as it reasonably can
  be; where it really must stay too steep, **a small stone wall stands along the top of the walkable ground**, so the
  wall is what stops her ("remove the invisible wall immediately in front of her, when it does get too steep, put a
  small stone wall at the top"). Those walls in long runs (D5), their ends against something.
  How: inside the park she may walk up anything she wouldn't slide down (0.55 rise a metre, the slide's own limit;
  elsewhere 0.30 as before — this changes round 33's "one gradient rule everywhere" for the park only).
  *(Changed round 40: the low dry-stone walls built along the **foot** of each too-steep bank in round 35 trapped her —
  all 32 are walked through now, kept for their look — the user: "any brick wall that is sitting at the bottom of a
  slope needs to be removed", then on the map of them: "For all the red ones, could you make them walk through, for the
  orange one keep it" (the orange one, G3's, later taken out too). A solid wall goes only along the top,
  and only where G5's test asks for one.)*
- **G2 Walls are solid things**: every wall has depth (a top and two faces), goes down into the ground (no gap under it
  showing the sky or what is behind — "this wall needs to go to the ground, it should also cover the stairs"), and
  where she walks on top of one, its edge stops her ("this wall has no depth, she can currently fall down").
- **G3 The covered walk's west end, down to the Austria Gardens** (round 40, latest word first): the path from the
  roof walk's west end is back — "you removed the path that went down to the gardens from this point. Please put it
  back. It should be lightly sloping and then curving around" — curving gently down (about 1 m over 13 m) to the path
  at the gardens' north-east corner; the roof's end wall stands across the roof except where the path comes on, so
  there is no gap to fall through. No brick wall along it: the last piece of round 35's G3 wall, standing alone on the
  bank, is gone ("replace this piece of wall that is not doing anything"), as were its lengths through the gardens and
  over the path before it ("remove the ones that I originally flagged"). The bank between the path and the gardens is
  grass, graded so it reads as a path down a slope, not gravel climbing the hill (round 40, earlier: "The hill should
  just be green").
- **G3a The covered walk's east end** (round 40, plan `round40/plan_east_rope.jpg`): a rope from the end of the roof's
  end wall along the downhill edge of the hairpin's upper leg, above the bank down to the lower walk, no gap at the
  wall.
- **G4 The camera in the park** (round 40, replacing round 35's flat colour — "That approach has completely failed"):
  the park's walls, hedges, beds, terraces, stair walls, columns and the calvary are nothing to the camera; only its
  houses (Casa Larrard, the Casa Museu, Casa Trias, the gate lodges) bring it in, and under the covered walk's roof it
  stays under the ceiling (`03_camera.md` #16, #16a, #16b).
- **G5 No death traps: she can walk away from anywhere she can get to** (round 40, the user: "There are these death
  traps all around the pink area. You need to smooth everything so that she can walk away from any place that she is.
  You need to have a test to review the entire park. Find every single place that there is a death trap that she can't
  get out of, and then change it so that it's not there. Some of the fences will need to be removed."; on Casa
  Larrard's bank: "It's a trap where I can never escape from"). Checked by the whole-park walk test (`tests.gd
  --trapsim=<png>:44,-258,194,-134,1,smart`, about an hour with `--fixed-fps 60`): on every metre of the park she is
  set down and really walks a step eight ways; every spot must have a chain of steps out to the gate plaza or the
  park's edge. (The first, static `--traps` test was too lenient: it missed the known traps.) A trap is
  fixed by, in this order: taking away the wall or fence that closes it; smoothing the ground so she can walk out; if
  the bank really must stay too steep, a wall along its *top* (G1 as the user said it), so she never gets down into it.
  A wall never stands at the foot of a bank she could slide down. The test runs after every change to the park's
  ground, walls or fences, and must find nothing.
  *Why there were traps:* G1's "How" put the low stone walls along the *foot* of each too-steep bank (round 35), not
  the top as the user said; sliding down the bank she landed between the wall and the bank and could get out neither
  way.
  *What the walk test found after that, and how each was fixed (round 40):* Casa Larrard's west corner — the lane's
  levelling outside the gate reached 2 m into the park and dug a ditch (`gracia_top_h` stops at the wall); the park's
  outer wall, north-east and east — where the land outside is lower, the last 3 m inside sagged into a ditch along its
  foot (`north.height`: inside the wall the ground never sinks below the park's own); the east side stairs — a metre-
  wide slot between their outer wall and the switchback path's rail, 1.5 m under the path (filled to the path's level),
  and a 0.8 m gap where their outer walls met the porch parapet, too narrow to pass but read as a cliff by the slope
  rule, so she was slid into the corner and held (both stairs' outer walls now run on to the parapet). A corner between
  two walls is closed or left at least 1.2 m wide, never in between.
- (Clashes checked: G1's walls are at the top of slopes she can't climb, F8/D1's railings at the edge of drops — the
  two never stand at the same place; G1 against C2 — a bank behind its wall keeps the wood-floor look; G3 is a wall at
  a drop beside a path, so D1–D5 apply to it as to a railing: long, with ends against something.)

## H. Gràcia's south quarter (round 36, built to the user's mock-up picks)
- **H1 One grid.** The quarter sits on shared lines: the two house blocks (x 106.5–124, z −91..−77 and −69..−55),
  their pavements (west 3 m to x 103.5, elsewhere 1.8 m), the square (footpath ring x 86–98.5, z −92.8..−70.8,
  floor x 88–96.5, z −90.8..−72.8), the house closing its south side (x 88–96.5, z −69..−55, pavement ring to
  x 86/98.5 and z −70.8/−53.2), the gate street (setts x 98.5–103.5), the streets at z −98.2..−92.8,
  −75.2..−70.8 and −53.2..−48.8, the lane (setts x 125.8–128.8) and the wood-side footpath (x 128.8–130.6).
  Everything lines up; no jogs, no slivers of leftover ground.
- **H2 Sidewalks are seamless.** A sidewalk wraps its building's corners as ONE surface; sidewalks that share a
  line are one continuous run (the user: "there had better not be the very narrow gaps between the sidewalks I
  currently see"). Edge lines (kerbs) only on a sidewalk's true outer edge. At a corner where a wide side meets a
  narrow one, the corner square is exactly as deep as each side's own pavement — nothing pokes out past the
  narrower side (the user: "the footpaths at the corners of the building are wrong. It should be simple to make a
  footpath"). Where a sidewalk meets the cobbles, they touch: no strip of grass between them.
- **H3 The cobbles are bounded by footpath, and the footpath runs under them.** Panot footpath along the quarter's
  west (the city street's own pavement line), south (Provença's far side, x 86–128.8 at z −49.5..−47) and east
  (x 128.8–130.6, the wood side, z −140..−47: the user, round 36, "make the footpath continue up to the path up
  the top" — it climbs the lawn with the ground and runs on UNDER the Carretera del Carmel's gravel: "That new
  path should go under the gravel, not over"; its last 2.5 m sink from kerb height to the ground, no end kerb). At every street's end the footpath runs through unbroken and the
  setts stop on it. No pavement across a street's mouth (no crosswalk look); street setts flow straight into the
  quarter's setts.
- **H4 One gravel path in the forest.** East of the footpath: the drystone wall (gaps only at the streets' ends:
  z −97.2..−93.8, −75.6..−70.4, and the south corner), grass, then ONE gravel path running north, with short
  gravel spurs through the wall gaps at z ≈ −95.5, −73 and −47.9. The old parallel paths, dirt spurs and the
  panot strip at x 126.4 are gone. At the south corner the junction with the wood's east–west path is clean (A8).
- **H5 The square keeps its life.** The floor (its current paving look, no wall around it), the astrolabe column
  at its centre, four plane trees at its corners, benches, the café tables along its east side, lamps. The town's
  south edge past the footpath is grass to the city's street.

## H6. Gràcia's top edge, under Park Güell's wall (round 36, the user's approved mock-up `round36/gracia_top_mockup3.jpg`)
- **H6.1 Roads are roads, everything else is footpath** (the user: "just have the cobblestone roads as roads. Have
  everything else as a footpath"). Cobbles only on the carriageways, each at its own width; every other paved
  surface is panot footpath, one seamless piece (H2), kerbs only where it meets a carriageway.
- **H6.2 One continuous road round the blocks.** Carrer de les Tres Senyores (cobbles z −141.2..−137.8) runs on east
  past Larrard's top as the road in front of the gate and down the lane by the wood (x 125.8–128.7). Its north kerb
  (the user's purple line): straight past the café terrace (z −141.0), curving down round the gate's entrance to
  −138.6 (a small forecourt of footpath before the gate), back up past the east lodge, then 1.8 m off the wall to the
  gravel — so the footpath along the top keeps a steady width. No paving across Larrard's mouth.
- **H6.2a Corners are rounded, never pointed** (round 41, the user, at the corner where the gate road turns down the
  lane by the wood: "fix this"): the footpath between the two roads ends in a 2.5 m round street corner. The two streets'
  west ends, where their setts met the grass, are closed by footpath ("there should be a footpath sealing it off
  before the grass"); setts meeting the city's asphalt are fine ("It's fine for the cobbled streets to meet bitumen").
- **H6.3 The wall has a footpath along it**, ≥1.8 m (1.2 m at the west lodge, which stands out from the wall): the
  cobbles never touch the wall. Where a block stands closer to the wall than a road needs (the top-left block, x
  66–82), footpath fills the whole gap, block to wall. The lanes (Carrer de l'Or, Baixada de la Glòria) end on it.
- **H6.4 The gravel ends at the town.** The Carretera del Carmel's gravel starts on a clean line at x 128.7, over the
  ends of the wall footpath and the wood-side footpath (both run on under it, A9 spirit: gravel never over cobbles).
  (Round 39, the user: the gravel goes UNDER the footpath where they join: it starts under the wood-side footpath's east
  kerb; the footpath climbs at kerb height to the park wall — 05 #16, #17.)
- **H6.5 The café corner**: the footpath between the top-left block and the west lodge is a level terrace at the
  road's height (the wall standing taller over it), the Cafè del Parc on the block's east side with striped
  awnings, its tables under parasols on the terrace (moved up from Larrard's top, where they stood in the road), a
  lamp against the wall, someone sitting at a table.
- **H6.6 The steep footpath behind the block** climbs from the terrace (5.6 m) to the Glòria gate's level (7.0 m)
  between the block and the wall (the user: "a steep street that goes up… between the wall and the building to bring
  up the level… for the next gate"), steepest in its middle, never over what she can walk (30%, `north.gd` `MAX_UP`); Baixada de la
  Glòria ramps up to the same level at its top. The park's path stops at the gate on the footpath (A8).
- **H6.7 The Plaça de la Vila is open**: one footpath floor road to road, no walls, no steps, the ground's own gentle
  slope between the two streets; six plane trees round its edges, the fountain in the open middle, benches, four
  lamps along its north and south edges between the trees.
- **H6.8 Lamps stand clear of trees** (the user: "the streetlights and the trees are too close together"): ≥3 m
  apart, never under a crown. The Plaça del Sol's things are spread out (×1.3 from the floor's middle, an empty strip
  ≥1.2 m round its edges) and its lamps stand at the middle of each side.

## Widths (settled)
- The hill path is a little narrower than the park's paths (the user: "No. The hill path should be a little
  narrower"): 2.4 m on the hill, 3 m in the park, as they are.

## Work list (in the order to do it)
1. **The funicular bend** (the user: "It is choppy, it should be smooth, but a bench somewhere suitable (on grass so
   not blocking the path) would be nice too"): the path round the bend one smooth curve (A1, A4); a bench on the
   grass beside it, off the path (A5), facing the view, with the bend's fences kept to D1–D6.
2. **The hill's uphill side** reshaped to C3, the whole way up, and the banks painted to C2.
3. **The fences** on the hill and in the park put to D1–D6 and F8.
4. **The park's gravel (F9), the paths to every house door (F10) and the cellar track (F11).**
5. **The paving edges** to B1–B2 (the town's pavement, the funfair, the park's paved places, the covered walk).
6. **The review**: maps from above and walking pictures, each against every rule; fix; again.

## Work list, round 36 (the Gràcia quarter and the forest)
1. H1–H5: the quarter rebuilt on the grid (north.py, north_build.py, world2d.py).
2. A8 at every forest join; A9 where the wood's path meets the beach (forest.py).
3. Not path rules, same round: the bike's lean eased a little; fewer brown mushrooms in the forest.
4. Pictures from above against the user's approved mock-up, and at eye level along the new streets and the forest
   joins; review against H1–H5, A8–A9; fix; look again.
5. Found on the walk (round 36): block corners poking out (H2); a grass strip between Provença's cobbles and its
   far pavement (H2); two old dirt spurs' ends lying as tan patches on the setts by the footpath (A1/H3: gone);
   a boulder on the gravel path in the Travessera gap (A8: a path's tile is never rock). The Travessera's trees
   (the user): the one above the square stays; east of the Torrent de l'Olla just one, on the road's north side.

## The plan
1. Build the work list above, each change named by the rule it serves.
2. Measure every rule that can be measured (`tools/path_rules.py`): fix until it reports nothing.
3. Pictures: the plan maps from above, and walking pictures along every path both ways (`--hilltour`, `--parktour`).
   Read each against every rule; list what breaks which rule; fix; take them again.
4. Show the user the maps and the walking pictures with the list of what was found and fixed.
5. Only after the user says they are 100% happy: the play-through and the full set.
