# 04 · Character movement and controls

How Sandra walks, turns, cycles, climbs, bumps into things, gets unstuck and goes through doors, and how the player
drives all of it from a keyboard, mouse, gamepad or touch screen — for any world. The user notices every lurch, jolt,
veer and snap, so this file gives the numbers the build uses and where they live (most in `engine/main.gd`, the bike's
in `engine/street_life.gd`, the hillside's in the world's own script, for Barcelona `worlds/barcelona/game/north.gd`).
Barcelona appears only as the example. The camera has its own file (`03_camera.md`); here it is mentioned only where
it and movement act on each other. The ground's shape (what is steep, where walls stand) is in `08_terrain_walls_map.md`;
this file says how she meets it. Later rounds win: where a rule was changed, the old one is marked and the current one
given.

## What "fluid" means
1. **Nothing snaps, jumps or lurches.** Every change of speed, heading, lean or height eases in and out; nothing turns
   or moves in a single frame unless the player asked for exactly that (an about-turn). (The user's standing rule:
   "Controls must feel fluid… they notice any lurch, jolt or veer", DECISIONS "The user and how to work with them";
   rounds 3, 10, 11.)
2. **"Fluid" in numbers.** Speed rises at 13 m/s² and falls at 16 m/s² (`ACCEL`, `DECEL`: about 0.4 s to full pace,
   0.3 s to a stop); a turn's rate comes on and dies away at no more than 16 rad/s² (`STEER_EASE`); her body catches
   up with her heading at rate 12 (`MODEL_TURN`); her height follows the ground at rate 14 a second, never in a step.
   Round 10's measure is the standard: the sharpest change in her turning fell from over 1 000 to 9 rad/s², the
   camera's from 65 to 2.6. (main.gd constants at the top; HISTORY rounds 3 and 10.)
3. **Every movement change is checked by its own test before it is shown**: `--moves` (twelve key sequences: the
   bite, the fastest turn, zig-zags, her heading every half second) and `--veer` (turning smoothness); on the bike
   `--ride`, `--corners`, `--bikeline`; held keys as a player presses them `--keyseq`. (CLAUDE.md "Controls must feel
   fluid"; DECISIONS "Building and testing".) Only the test for the thing changed is run, not the whole battery
   (see `09_review_and_testing.md`).

## Pace, starting and stopping
4. **One easy pace, no separate run and no jump.** She moves at 5 m/s (`SPEED`). (Round 4. REVERSED: round 3 had a
   run button and a jump on Space with grace at kerb edges; round 4 dropped both. Current: one pace, no jump.)
5. **Small extras only:** eating something gives +25% pace for a while, walking or on the bike (CHANGED round 41, the user: "The food speed should be 25% and should also apply to the bike"; was +30%, walking only), as in the 2D game (`boost`, a card by the
   clock shows the time left); the debug menu's "quick walking" is ×2.4 (`debug_fast`), for testing only. (Round 20;
   main.gd `_physics_process`.)
6. **No movement while talking, in a panel, in a fade or in a scene.** Keys do nothing while a talk box, panel or fade
   is up (`busy`, `dlg_open`) or a cutscene plays; the world keeps ticking. (main.gd `_physics_process`.)
7. **Pushing into a wall doesn't build speed**: if she is held against something, her speed drops to what she is
   really doing (at least 60% kept), so she moves off smoothly when it clears. (main.gd `_physics_process`.)
8. **A footstep sound every 0.85 m**, soft, different on road and pavement; none on the bike. (Round 4; main.gd,
   `ambience.footstep`.)

## Steering on foot (outdoors, with the free camera)
9. **Setting off, the keys mean the screen.** From standing (speed under 0.4 m/s, keys down less than 0.3 s) she
   turns straight to the direction pressed relative to the camera. (Round 11; DECISIONS "Steering (final,
   user-approved)"; `steer_walk`.) Where movement meets the camera: this is the only moment the camera decides her
   direction on foot.
10. **Running, forward keeps her straight on, however the camera is turned**; forward or back alone never curve her.
    (Round 9, kept in rounds 11 and 17.)
11. **Forward with a side key steers: a bite at once, then a little tighter the longer it is held.** Bite 1.2 rad/s
    (`STEER_BITE`), growing 0.6 rad/s per second held (`STEER_GROW`) up to 3.0 rad/s after about three seconds
    (`STEER_MAX`, about a 3.3 m circle at full pace). (Round 11. REVERSED: round 9 held her straight while the camera
    swung round and let a side key in slowly; round 10 made it a smooth veer up to 2.2 rad/s; round 11's bite-and-grow
    replaced both. The user: "Don't revert to plain camera-relative steering.")
12. **The quick turn just after setting off.** In the first 0.9 s of a run a side key bites at 3.6 rad/s (`QUICK_HOLD`,
    `STEER_QUICK`), fading back to the usual bite over the next 1.1 s (`QUICK_FOR`), so narrow places can be threaded.
    (Round 27, the user: "if I start running and then press a side arrow key very quickly after, it should turn
    quicker, in order to navigate narrow places"; round 28: it must work when the side key comes "a moment into the
    run" — CHANGED from 3.2 rad/s fading at once to 3.6 held 0.9 s.)
13. **A side key on its own turns her straight to that side of the screen**, quickly, like an about-turn, then she runs
    straight on that way: no slow curving. (Round 14/17, the user; DECISIONS "Steering (final, user-approved)".)
14. **The side-then-forward latch.** A side key held from before forward is pressed is ignored for steering until it is
    released and pressed again, so adding forward never swings her. (Round 27, `side_first`.)
15. **Back is one clean about-turn** to run towards the camera — once, quickly (turn rate 7 rad/s, faster the further
    she has to go round, `TURN_RATE`) — then straight on while the camera swings round behind her. No zig-zag. A sharp
    about-turn (over about 140°) costs 15% of her speed. (Rounds 3 and 11; `steer_walk`.)
16. **Held against a wall or column, the side keys keep steering her away from it.** The "keys mean the screen" rule
    applies only in the first 0.3 s, so pushing into something and pressing left or right turns her off it rather
    than back into it. (Round 15/17: "pushed up against something, left and right still steer her away"; `keys_held`;
    test `--pocket`.)
17. **Turning the camera by hand while running steers her with it** (on foot only, not on the bike). (main.gd
    `turn_camera`.) Movement and camera meet here: dragging the mouse is a steering input while she runs.

## Steering indoors
18. **Ordinary rooms (fixed camera): the keys are the screen's directions**, always; she turns to them at the
    about-turn rate. The user likes these indoor controls as they are. (Round 19.)
19. **Big walk-round rooms with the free camera (a cathedral) steer much more sharply** than outdoors, so she can weave
    between columns: bite 3.0, growth 2.0, most 5.0 rad/s (`ROOM_STEER`), the turn easing twice as fast. (Round 15.)
20. **Columns are round** (as wide as their feet) so she slides round them; square ones caught her on their corners.
    (Round 15; room `posts`.)

## Her body as she moves
21. **She leans into turns, not out of them**, on foot by up to 0.14 rad (turn × speed × 0.012). (Rounds 3 and 14;
    main.gd `lean_to`.)
22. **She stands up straight.** The standing animation's lean is corrected every frame (feet under the hips, back
    upright, `UPRIGHT` 0.03 rad in `engine/posture.gd`), fading out as she walks; it is off while she rides. (Rounds 5,
    14, 21: "leaning back then straight".)
23. **The walk animation plays at her real speed** (its natural pace is 4 m/s, `MOVE_ANIM_SPEED`), and stops when she
    is held still. (main.gd `animate_skin`.)
24. **She faces whatever she talks to or uses**, turning smoothly (rate 8), and keys break it off. (Round 3;
    `face_target`.)

## Keyboard, mouse and gamepad
25. **Keys (as in the 2D game):** W A S D or the arrows to move; E talk, read, pick up, use, confirm; B the bike;
    M (or Tab) the map; I backpack; J journal; N music; T next part of the day; C her outfit; P the debug menu (only with `--debug`, rule 08 #84a); Esc
    frees the mouse, then opens the pause menu, and closes the map. Quality keys Q (balanced or full look), G and V
    (extra light effects), only with the debug menu on (rule 08 #77a). Space only moves a talk on. (Rounds 12–13; main.gd `_unhandled_input`.)
26. **Mouse:** click to capture it and steer the camera; click again, or Esc, frees it (round 38, the user: "clicking again doesn't unmove you… You should be able to click again and undo this"); the wheel zooms the camera (2.2–9 m); with the
    mouse free, a right-button drag also turns the camera. (Round 3; main.gd.)
26a. **In a first-person place** up/W walk forward and down/S walk backwards; left/right turn her on the spot; the mouse
    turns her too; at a stroll (2.4 m/s forward, 1.5 back). Walking out backwards she turns round and walks on. (Round
    39, the user: "it should become first person and the arrow keys just move forward and backwards"; `main.gd fp_walk`.)
27. **Gamepad:** left stick moves (a dead zone of 0.18, scaled after it), right stick turns the camera, A or X
    confirms, the D-pad moves through choices and panels. (Round 3; `pad_axis`.) Never tested on a real pad recently.
28. **In a panel or a talk box the keys belong to it**: W/S or ↑/↓ choose, E or Enter confirm, number keys pick
    directly, Esc backs out (the last option is always the "no / close" one, except in the pause menu, where Esc means
    Resume). (Rounds 6, 15, 20e: "backing out of it used to ask about a new game".)
29. **Tests never read the real keyboard or mouse**: a test window that pops up must not catch the user's typing.
    (Round 19, after an Esc opened the pause menu mid-test; `testing`.)

## Touch controls (phones and tablets)
30. **Laid out like the 2D game's**: a pad bottom left (it sends W A S D; the arrow keys while a panel, the map or a
    talk box is open), A (E, or Enter in a panel) and B (back: Esc, only when something is open) bottom right, and a
    column of buttons: BAG, MAP, LOG, BIKE, LOOK, ☰ (DEBUG too, only with `--debug`). (Round 20e, the user: "mobile compatible, similar to the 2D
    version"; `engine/touch.gd`.)
31. **LOOK is a toggle**: on, a finger dragged anywhere else turns the camera at 0.0042 rad per pixel (`LOOK_SENS`, a
    swipe across the screen ≈ a turn and a half). Several fingers at once; a thumb may slide round the pad. Each button
    swallows the click a tap also makes, so nothing under it is clicked. (Round 20e.)
32. **Held upright, the controls sit on a very dark grey deck below the picture** (30% of the height, 380–540 px),
    covering nothing; text is laid out for an 800 × 1280 screen; the talk box, panels and map stay above the deck.
    (Round 20e.)
33. **Words follow the device**: on touch the bike button is "BIKE" (B means back there), and every panel's help line
    names the touch buttons. (Round 20e; `bike_word`, `hint_of`.)
34. **Shown when the device has a touch screen**, with `--touch`, or from the debug menu when it's on (the mouse then acts as a
    finger). Not yet tried on a real phone; phones use Godot's Mobile renderer, so the look and frame rate there are
    untested, and exporting needs downloads the user must approve first. (Round 20e.)

## The bike: getting on and off
35. **Her own bike, anywhere outdoors, once the story gives it to her.** B puts her on it where she stands (it appears
    under her, facing her way) and B again hops her off; E beside her parked bike also rides it, and E while riding
    gets off. Other people's bikes are locked: E only says so (no "B to hop on" offered for them). (Round 13: "as in
    the 2D game"; round 23: looking at a locked bike gives no rider's hint. REVERSED: round 6 let E ride any bike.)
36. **Not indoors, not on sand, not in the thick of a wood, not in a no-bike place** (a walled park, a funfair): B there
    says why in a short line and does nothing. (Rounds 13, 20, 27, 35b; main.gd `bike_key`, `no_bike_at`.)
37. **Getting on, she takes the bike as it stands**, facing where it points; she never turns towards where it was parked
    or rides sideways. (Round 7.) A banner reminds the keys: "W pedal · S brake · A D lean · E get off".
38. **Getting off, she steps 0.7 m to the side** (the clear side, kerb side first), keeps facing the way she rode, and
    walks on normally; the camera glides across with her at its zoom pace instead of jumping. (Rounds 7 and 20e;
    `street_life.dismount`, `cam_slide`.) Movement meets the camera here.
39. **Going through a door gets her off first**; the dog in the basket hops out beside her. (street_life `on_enter`;
    round 22.) (**Changed** in round 39, the user: going in on the bike, "Must get off first": the door simply stays shut, with no
    message ("that's unnecessary"), until she gets off — rule 77; `main.gd enter`.)

## The bike: riding
40. **It is ridden like a bike, not pointed like walking.** W pedals up to speed, S brakes and, once stopped, pushes the
    bike slowly backwards (1.2 m/s, to get away from a wall); A and D lean her into a turn. It always goes where its
    front wheel points: it never slides, drifts or turns on the spot while moving. (Round 9; main.gd `ride`.)
41. **Speeds**: 9 m/s on the road (`BIKE_SPEED`, about 1.8× walking); 70% of that on pavements, paths, gravel and grass
    (`BIKE_ROUGH` 0.7). Pedalling up at 7 m/s², coasting down at 2.5, braking at 11. (CHANGED: round 9 had 40% slower
    off the road; round 27, the user: "slightly faster on footpaths and gravel trails" → 0.7.)
42. **The turn is tight when slow and wide when fast**: radius 0.8 m plus 0.5 m per m/s (about 3 m across creeping,
    11 m at full speed). Stopped, the side keys turn the bike round where it stands (2 rad/s, her foot down) and the
    camera stays put until she rides off at a fair pace. (Round 9; street_life.gd `BIKE_MIN_RADIUS`,
    `BIKE_RADIUS_GROW`, `BIKE_SPIN`.)
43. **Leaning in and straightening up take a moment** (the steer eases at 3 per second in, 4.5 back). (main.gd `ride`.)
44. **She leans with the bike, more the faster she goes, but only a little.** Current lean: the steer × (0.05 + 0.08 ×
    her share of top speed), at most 0.13 rad (about 7°), faded in below 1.5 m/s; stopped, the bike tips a little onto
    her foot. (CHANGED: round 27 cut the cap from 0.68 to 0.40 rad; round 36, the user: "She still leans too much on the
    bike. Make the lean a little less." (0.24 rad); round 37, the user: "Please make the bike not lean as much when she
    turns." — about half of round 36's.)
45. **Her riding pose follows the speed**: upright pulling away, over the bars at speed (forward lean 0.06 → 0.4 rad, eased),
    feet on the pedals, hands on the grips, a relaxed cadence (about 30 turns a minute pulling away to 70 at speed);
    stopped, her left foot comes down to the ground. Her hips stay over the saddle's middle. (Rounds 9, 27; round 23,
    the user: "her legs are weirdly shifted to the side when she cycles"; `engine/rider_pose.gd`, street_life `tick`.)
46. **The bike fits her**: wheels 0.64 m across, pedals and saddle high enough to clear the ground, her legs nearly
    straight at the bottom of a stroke. (Rounds 9, 10, 21: "wheels and pedals too close to the ground".)
47. **While she rides, the bike's wheels bump into things too** (a 0.27 m ball at each wheel), so its front can't poke
    into a wall. (Round 9; `add_bike_body`.)

## The bike on slopes and surfaces
48. **Uphill she pedals slower than she walks**: the top speed blends down to 80% of walking pace (4 m/s) as the rise
    goes from 2% to 12%. (CHANGED: round 22b, "a little slower than running", 0.9×; round 25, the user: "20% slower
    than walking" → 0.8; round 27 blends it in from 2%.)
49. **Downhill she goes faster by the slope**: on the surface's own top speed, up to +80% at a 22% fall, starting from a
    3% fall; never while leaning into a bend; the hill also helps her get going (pedalling up 2.5× quicker). (CHANGED:
    round 25 "30% faster than on the streets"; round 27, the user: "she goes very fast on any downhill… make the speed
    multiplier based on the size of the slope" (+45%); round 41, the user: "Make the downhill speed on the bike
    faster" → +80%.)
50. **Speed gathered on a hill wears off gradually** (0.7 m/s each second, `BIKE_GLIDE_EASE`), so she carries it across
    the pavement and on down the street. (Round 25.)
51. **The bike never sinks into the ground**, anywhere: riding, stopped, parked, or as she gets on or off; its height
    always comes from the ground under each wheel. On paths, paved meadow ways and grass it rides a few centimetres
    higher (2 cm in town, 5.5 cm outside). (Round 20; main.gd `lift`; round 38, the user: "just outside one of the
    park's gates, the bike sinks into the ground when I get off it, or maybe before. Please review this across all
    similar terrain. The bike should never sink into the ground like this.")

## The bike: where she may not ride, and bumping
52. **The bike stops only at something with a reason to see**: sand, the thick of a wood, a walled park's gateways, a
    funfair. Shade alone never stops it. (Round 20, the user: "the bike should just not work where there are trees…
    separate from the shadowed ground"; no invisible walls.)
53. **In a wood, the bike's limit is a rope tied from trunk to trunk round the thick of it**, so the only invisible wall
    is between two trees: a rope wherever two edge trees are no more than 7.5 m apart (`ROPE_MAX`), never across a path;
    she can't get on inside it. (Round 20e, the user: "nail a rope to the trees on the edge… the only invisible wall will
    be between two trees"; the user chose 7.5 m from maps of 3.5–7.5 m, and marked trees to leave outside.
    REVERSED: round 20's no-bike rectangles stood metres out from the trees. Barcelona: `bike_rope.py`, `LAYER_NOBIKE`.)
53a. **On the hill the bike keeps to its path** (round 41, the user: "make sure you can't cycle through the forest.
    Glade coming down the hill. Any of the forest"): a thin bike-only wall along each side of the hill path the whole
    way up (not at its foot by the pavement, nor at the funfair's gateway, nor across the inside of a tight hairpin),
    and off the path on the wooded hill she can't get on ("No riding in the woods: wheel it back to the path").
    `main.gd on_hill_off_path`.
54. **When the bike is stopped it says why**, a short line at most every 6 s: "Too many trees to ride through: hop off
    (B) to walk, or keep to the paths", "The wheels sink in the sand…", "No bikes in Park Güell: hop off… and walk in",
    "No bikes in the funfair…". The user wants this line kept. (Rounds 20e, 35b; main.gd `nobike_said`.)
55. **No-bike walls exist only while she rides**; on foot she walks onto the sand, into the wood and through the gates.
    (Round 20; the player's collision mask.)
56. **Riding into a wall stops the bike** rather than sliding it along; brushing past doesn't. Riding at a solid thing
    (a stand, a parked bike) she pulls up against it. (Round 9; round 33 `--solidwalk`.)
57. **No crashes and no hurt.** Nothing knocks her off. (REVERSED: round 27 added a bus that knocked her off the bike;
    round 28, the user: "Remove the whelp, the bike should just disappear. It shouldn't seem to hurt"; round 33 removed
    all traffic: "Get rid of the cars/bus and bus stops". Current: no traffic, no knock-offs.)

## Slopes on foot (the numbers of the ground are in 08)
58. **She walks up anything no steeper than the walking limit; steeper, the uphill part of her step is simply lost** —
    she can still walk along it or down it, never pushed back in a jolt. Current limit 0.30 rise per metre outside a
    walled park (`MAX_UP`), sampled half a metre either side of her (`gradient`). (Round 22b: 0.27; CHANGED round 33 to
    0.30 so the park's lawns, at most 0.28, could be walked; whether to raise it to 0.40 is still the user's choice —
    see "Unclear". Barcelona: north.gd `steer_on_slope`.)
    **At no angle either** (round 40, the walk check of the funicular's track: on a hill just too steep to climb she
    climbed it slantwise, the rise across it under the limit, and zig-zagged up the whole hillside to the track — the
    user: "she should not be able to access it from anywhere"): off the paths, on ground steeper than the limit any
    uphill part of her step is lost; she can walk along such a slope or down it (`north.gd steer_on_slope`).
59. **Steeper than 0.55, off a path, she slides down** (up to 3.2 m/s, more the steeper it is: `SLIDE_AT`,
    `SLIDE_SPEED`). Going down a hill through the wood is allowed; climbing off the path is not. (Round 22b, the user:
    "can't leave the path going up, can go down through the wood… slipping down allowed".)
60. **Inside a walled park she climbs anything she wouldn't slide down** (limit 0.55 there), and where ground must stay
    steeper a low wall she can see stops her instead. (Round 35b, PATH_RULES G1, the user: "no invisible walls in the
    park… they are annoying". This CHANGED round 33's "one gradient rule everywhere" for the park only.)
61. **On a path or steps she climbs what the path climbs**, never a wall (a rise over 1.2 per metre stops her even on a
    path). A path counts as its own width plus 0.4 m; steps count 0.7 m round them, since the slope is read half a
    metre either side and the steps' own edge read as a cliff at 0.3. (Rounds 22b, 32b, 34; `on_path`, `on_steps`.)
62. **The slope rule never applies on built level ground**: the town, a bridge deck (and 1.7 m round it), a door's
    doorstep (0.5 m inside to 3.2 m out, door width + 1 m each side), built floors and ramps (terraces, porches,
    landings), roofs she walks on. Each exemption came from a place where buried or neighbouring ground read as a cliff
    and pinned her. (Rounds 32 (bridge: "she stood… with W held… moving nowhere"), 32b (Casa Museu door), 35b (Casa
    Trias portico: "I walked right into the middle then could not go anywhere, just spin around"); `at_doorstep`,
    `flats`.)

## Steps, stairs, kerbs and roofs
63. **Kerbs and low steps need no jump**: her body stays at street level and only her model rises to the ground's
    height (a kerb is 0.12 m), eased, never in a jolt. A walkable flight of steps is recorded as a ramp or a series of
    raised rectangles so she glides up it. (Round 1's "kerb step"; round 20d: the university's front steps were "a
    knee-high ledge" — now a landing and two low steps; CLAUDE.md "Coordinates".)
64. **Indoors, walking into a staircase takes her to the other floor**, as a door does (she must be walking the stair's
    way; E on it works too), arriving at the far end facing on. (Round 14; room `stairs` with `rect`, `go`, `arrive`,
    `face`.)
65. **On a roof walk** she stays on it while she is on its outline and at its height; a step off its open edge onto
    ground far below (over 0.8 m) is refused. (Round 34; `deck_at`.)
66. **Starting at the right height**: after a door or a move she and the camera start at her ground's height, never
    rising up through a hill from street level. (Round 35's second look; `snap_height`.)

## Solid people and things
67. **People are solid, standing or walking**; she stops at arm's length (0.58 m centre to centre on foot, 0.85 m on the
    bike), on hills too (her lifted height is compared). Passers-by won't step within 0.75 m of her. (Round 16: "Sandra
    can no longer walk through people"; round 27, the user: "You can run through Genis"; `keep_off_people`.)
67a. **Pushed into, people give way.** Only on contact — when she walks or rides into someone, never from a distance
    (not like the lost dog shying away). Run into from the front, they take a step back as they are pushed to the
    side, out of her way, still facing her. Run into from behind, they start walking forward out of her way, then
    turn to face her. Either way at her pace but slower (on foot she slows to about a walk, on the bike she keeps
    rolling, slowed, instead of stopping dead); they never step into a wall, a trunk or a solid thing (then they step
    sideways, or hold, and rule 5's slip-past still applies); a person who stands at a post drifts back to it once
    she has gone. Never while they talk to her. (Round 37, the user: "as if you're pushing them out of the way and
    they're stepping away at the same time… they should be pushed back"; **changed** in round 38, the user: "if she
    runs into them from the front, they take a step back as they get pushed to the side… if they get pushed from the
    back, they start walking forward. And then they turn to face her"; `main.gd shove_people`.) (Round 39: "rule 5's slip-past" means 73.)
68. **Whoever she talks to faces her and stays put until the talk box closes**, then carries on. (Round 16.) (Round 39: after the talk they keep facing her until she walks away — 10 #15.)
69. **Everything that looks solid is solid**, on foot and on the bike: posts, lamps (radius 0.14 m), trees (0.25 m),
    bins, benches, planters, bike stands (a post per hoop), every parked bike (a 0.32 × 1.1 × 1.75 m box), flower
    buckets, stall ends, name posts. Not solid: grass, flowers, leaves overhead, painted lines, low kerbs. A thing is
    solid only if the builder writes it as one, so any new street object must. (Round 33, the user: "She can run through
    the bike lock stands/bikes. This should not be possible… review every single object like this"; `--solidcheck`.)
70. **Her own parked bike is softer than others'**: it blocks her but she can slip past it (rule 73); it also gives way
    to anything else when E is pressed beside it. (Rounds 27, 32b.)
71. **The dog stays out from under her feet**: lost, it dodges; once known, it is nudged along (0.6 m) and walks beside
    her (0.85 m off); it never stands inside her. (Rounds 20, 22, 35b; `engine/dog.gd`.)

72a. **A barrier stops her at itself**, never at a box round it: a slanting line of barriers is a thin wall along the
    line, as deep as their feet (round 41, the user: "She should be able to move closer to the barricades (there is
    an invisible wall when she is cycling down the hill and gets too close)": the hill path's works barriers, and
    the same barriers pushed aside on the verge, had square boxes reaching up to a metre out; `north.gd line_body`).
## Walls and invisible walls
72. **An invisible wall only where there is a clear reason to see** — a steep bank, a wall, a rope between two trees, a
    fence end against a bank. Ground she can't climb must look steep; anything else that stops her must be visible. The
    world's edge is closed by things she can see (thick wood, a bank), not a bare wall in the open. (CLAUDE.md
    "Playable"; round 20e; round 23: "Forest edge: an unclimbable slope, not an invisible wall"; round 27 "World edges";
    round 35b G1. The world's outer box, `walk`, stays as the last backstop.)

## Getting stuck and unsticking
73. **Nothing small can pin her.** Pressed for 2.2 s against a person or her own bike while going nowhere, she slips
    through it for 1.3 s (for walls and trees, rule 74). (Round 27, the user;
    `soft_block_t`, `soft_pass_t`.) (Round 39: for trees, rule 74.)
74. **Push against a tree for three seconds and she goes through it.** Pressing to go somewhere for three seconds
    without getting anywhere (no more than 40 cm) while touching a tree's trunk, the trees stop holding her until she
    is clear of them; if she is still inside after 2.5 s she is put back where she started. Nothing else is ever
    passed through — walls, buildings, rocks, posts and the map's edge stay solid — and no other unsticking is layered
    on top. Bushes are walked through anyway (02 #65). (Round 20; **changed** in round 39, the user: "she can push
    against a tree and get out. I made this rule before and it wasn't followed. It needs to be followed now… it needs
    to be her pushing, but not moving for 3 seconds… that should overrule any of the other changes you made. I don't
    want all these things layered on top of each other"; tried at the user's spot below Casa Trias: `--walkline`;
    `main.gd slip_trees`, `tree_body`.)
75. **She is never stuck, especially round walls**: every place is swept on a half-metre grid at the walked height for
    pockets she couldn't leave, and every new area gets its own sweep and walks. (Round 32, the user: "Make sure that
    Sandra can't get stuck anywhere, especially around walls"; `--stuck`, `--seams`.)
76. **Before blaming the game for a stop, probe it there** (the raw contacts, the slope rule's verdict on her step):
    most play-test stops were the test's own steering. (Round 32b; memory "Play-through approach".)

## Doors: going in and coming out
77. **Doors are walked through**: walking at a door (within its width + 0.15 m, no further than 0.55 m out, heading into
    it) takes her in with a short fade; E within 1.3 m does the same. On the bike she must get off first. (Rounds 1, 9:
    the door "used to open… even on Carrer de Mallorca"; now only within half a metre of it.)
78. **Walking at a locked door does what E does**: it says it is locked (at most every 3 s), the key turns the first
    time, the next push goes in. (Round 32b: "the locked cellar opened to anyone who simply walked at it".)
79. **Coming out, she stands 1.8 m out from the door, facing away from it**, and the camera is put back as the player
    had it, at most a quarter turn off her back, so pressing forward never walks her straight back in. (Rounds 15, 21,
    23; main.gd `leave`, `kept_cam`.) Movement meets the camera here. (Round 38: the camera's height and zoom go back to the usual, 03 #5.)
80. **Leaving a room is walking out of its open front** (or a second door at its back), after 0.6 s inside so she can't
    bounce straight out. A cathedral's doors open onto a short corridor and she is outside as soon as she steps in.
    (Rounds 14, 21.)
81. **Nothing stands in a doorway**: the pavement in front of every door is kept clear (0.7 m round a point 0.7 m out).
    (Round 21; see 05/08 for placing things.)
82. **A gate never shuts on her**: after she walks out of a gated place it closes 6 s after she has gone. Before she
    has the ticket every gate is shut; with it the place is hers for good (rule 06 #97). A person who sells the ticket
    stands beside the opening, reachable from outside (talk reach up to 2.5 m there). (Rounds 27, 32b; north.gd
    `tick_gates`; round 38.) (Round 39: the keeper stands on the street side in front of the main gate, facing out — 06 #97.)

## Other ways she moves
82a. **She sits on any bench** (round 41, the user: "the benches should be solid. And it would be nice if you can sit
    on them, then have a first-person view where you can look around. Or press E to get up again. For all the benches.
    Both the ones on the hill and the ones in the city"): every bench is solid; E in front of one, "Sit on the bench",
    sits her on its seat facing the way it faces, the view at her eyes; the arrows or the mouse look round; E, "Get
    up", stands her a step in front of it. The build lists every bench (scene 'benches'); `engine/benches.gd`.
    **Her body sits there too** (round 41, the user: "add her body sitting down when sitting on the bench"): the
    wheel's seated pose (#83a): hips forward on the seat, thighs along it, knees out past its front edge, shins hanging
    from there a little forward ("bending her knees, and her knees are coming off the edge, and then her legs are
    down"), hands resting on her thighs; her
    head alone shrunk away, as the camera is at her eyes, so looking down she sees her own lap and shoes.
    Seated, she looks round at most a quarter turn either side of the way the bench faces, and from straight up to
    straight down (round 41, the user: "you should only be able to look… 180 degrees, both up and down").
83. **On a ride (a wheel, a funicular) she is carried**; the world keeps moving; E swaps between her seat and her own
    eyes, the mouse looking out. (Rounds 22b, 23, 26: "the only option E should be to look around, which makes it first
    person".)
83a. **On the Ferris wheel she sits** on the gondola's bench, facing out of the wheel towards the city: hips on the
    bench, thighs along it, shins hanging, hands in her lap, head and shoulders above the rim; she sits as she steps in
    and stands to step out (round 41, the user: "ride the Ferris wheel and take pictures. I think that it will look a
    bit silly unless you plan it… make her body sit correctly on it": she had stood in the tub, legs through the bench,
    only her head showing). She sits on the round seat in the middle, facing away from the little rail, which is behind
    her like a chair's back, her hands on her knees (round 41, the user, last: "Sandra needs to be turned around the
    other way. The seat is in the right direction. She is not"). (Before that she held the rail in front of her, each hand on its own side, her elbows down and a little back by her sides
    (round 41, the user: "Her arms still look wrong": facing out of the wheel her left is the gondola's +x, and the
    marks had been laid as if she faced the other way, so her arms crossed over in front of her chest; her feet and
    knees too).) The seated pose is the exam desk's (`rider_pose.gd`); the marks her feet and hands reach
    for hang from the gondola (`north.gd seat_on_wheel`). Check: `--wheelride=<dir>`.
    The gondola is open inside, like a ring with a floor: the tub's wall inside and out, a white ring of a rim, a
    wooden floor over a bowl (nothing bulging up inside: "the tub should be hollow"), its sides to her lap so her arms
    show ("She also doesn't have any arms in the gondola"), a round seat in the middle with a little curved hand-rail in
    front that she holds, four white posts from the rim's top up into the roof ("go back to 4 bars and make them white";
    "make sure that the white bars… reach both the walls of the gondola and the roof"), a flat roof well over her head, hung from the wheel by a short rod onto
    the roof, nothing slanting through the cabin (round 41, the user: "there's not actually space for her to sit, then
    her head is hitting the roof… more like a donut with a bottom. And the top needs to be flattened"; then "there's a
    bar going through her head. Could you sit her a bit more in the middle? And then when she spins around, she's sort
    of in the middle of it"). The wheel stands high enough that its lowest gondola clears the boarding platform ("She
    cuts into the ground now… lift up the Ferris wheel a little bit": hub 13.6 m, was 12). Once round takes a minute (`WHEEL_TURN`), plus the wait for her gondola to come round.
83b2. **The wheel's boarding platform is on the plaza's side** (round 41, the user, on the plan
    `round41/wheel_plan/2_wheel_proposed.png`: "that concrete platform next to the Ferris wheel should be on the other
    side. And the fence should be on top of it. So that it sort of guides you from left to right… you get on, then you
    get off on the east side"; "Yes, that was right"): a solid stone box between the frame's feet on the side she comes
    from, steps up at its west end (Ramon's booth stays where it was, on the city side: "move the ticket booth back to where it was"; she walks round the wheel from it), a lane between the railing along its far side and a rail down
    its middle (1.8 m clear of the cabins: "move one of the railings slightly closer"), a gap in that rail where the gondolas come down; **she gets off the way she got on**: back out through the gap
    into the lane she came along, facing back the way she came, and down the same west steps; the lane has steps at both
    ends, so it can be walked through, up, along and down (the user: "take the steps on the other side and continue them
    so that you could theoretically walk forward, up, keep walking, then walk down") (CHANGED,
    round 41, the user: "she should get off on the [same] side of the railing. So that it's the same way she walked on…
    She walks on, then goes through the gap, and then comes out of the gap, and walks in the other direction"; the east
    step had stood half under the frame's foot). No queue rails on the ground. **The merry-go-round is solid** (round
    41, the user: "make the merry-go-round solid, so you can't run into it"): its round base, 5.1 m.
83c. **She boards the wheel at its gate**, and once she has paid she stands facing the wheel, the camera behind her
    looking past her at it and the city beyond, and so it still looks when she is in her seat, facing the city (round
    41, the user: "once she pays for the Ferris she should be facing it, and so then when she jumps in, the camera is
    facing the city still. By default"): E there, "Ride the wheel (€1)", pay, and she steps into whichever gondola
    comes round next, any colour; all twelve are alike but for their colour (round 41, the user: "she just walks up to
    it, goes up to the gate or whatever, presses E, pays for it, and then gets into the next one, whatever color it
    is"; `north.gd candidates`, act "wheel"). Ramon, the operator, still sells a ride too, from his ticket booth at the
    platform's west end: hollow, a floor and thin walls to the counter, the window open above it facing the open terrace
    (south of the platform the terrace drops away), a white ledge, a red and white awning, the GIRADABO board, a price
    plate, a door at the side; he stands inside facing the customer; she can't walk into it (the user: "make the ticket
    counter more detailed, and she shouldn't be able to walk into it… have it on the other side and have the man
    facing the customer and make sure that there is room inside for him to stand").
83b. **On a ride, E is first or third person, nothing else** (round 41, the user: "the only option is to either go
    first person or third person. Third person follows her and left and right move around, or first person gives her
    view and she can look around"): the arrows or W A S D take the camera round her (third person) or turn her view
    (first person; up as well as round, "she can look around in every direction"), up and down tilt it, and the mouse
    as ever; seated, the camera's centre is at her own eyes, and looking out her eyes lean towards the rim the way
    she looks (0.55 m, `SEAT_LEAN`), so turning swings round the inside and the tub's orange isn't filling the bottom
    of the view ("as if she's leaning forward… almost like spinning around the inside")
    (`main.gd seat_eye`). The prompt says "[E] First person / Third person · ← → look round".
84. **At a coin telescope** the arrows or W A S D turn the view slowly; E or Esc steps back. (Round 25; round 35: it had
    to keep ticking while she looked.)
85. **In a scene (the exam) she is posed by it** and nothing moves her. (Round 22b.)

## Unclear or not yet decided (for the user)
- The walking limit outside the park: keep 0.30 (choice A) or raise it to 0.40 (choice B: most of the hill climbable,
  the workmen's barrier then checked and fenced) — asked in round 33 (`workshop/screenshots/round33/slopes_choice.jpg`), never
  answered.
- Touch: should LOOK be always on (dragging anywhere turns the camera) instead of a button? Should the game be tried on
  a real phone (it needs Godot's export downloads, an Android or Apple toolchain, and the Mobile renderer's look checked)?
- Is the gamepad still wanted? It is supported but has not been checked for many rounds.
- One pace, no run and no jump since round 4: does that hold for a new city too?
- Other people's parked bikes are solid with no slip-past: if one ever pins her in a corner, should they get the same
  2.2 s slip as her own bike and people?
- Should riding up to a door hop her off and take her in, or must she always get off first (as now)?
- On stairs and steep paths she walks at full pace: should she slow on steps or steep climbs?
- The bike's numbers (9 m/s, 0.7 off road, +80% at 22% down (round 41; +45% before), 80% of walking uphill) were reported in round 27 but never
  explicitly approved: are they final?

- **Sandra's arms are 28% shorter than her model's** (upper arms and forearms, at their rest, so every pose that reaches
  — the bike's grips, the exam's paper, the wheel's knees — reaches with them; round 41, the user, shown three lengths:
  "go with C"; main.gd `ARM_K`). At the exam her hands are out on the desk in front of her (the paper in the desk's
  middle, the writing on it), her elbows well out to her sides and forward ("fix up the hands at the desk because they
  go into her body"; "make it come out a bit further at the shoulder… so her hand's more in front of her"; bringing
  the paper nearer her, tried first, pushed them further in).
