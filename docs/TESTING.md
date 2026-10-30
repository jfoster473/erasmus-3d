# Testing

The game tests itself: run Godot with a test flag and `worlds/<name>/tests/tests.gd` takes over — it places Sandra,
presses keys (never the real keyboard: `main.testing` ignores it), talks, rides, takes pictures, prints results and
quits. Tests keep their own save (`user://test_save.json`); the player's `save.json` is never touched. A test run
is silent (round 26, the user: the master bus is muted in `start()`; `--audio-driver Dummy` before `--path` keeps
Godot off the speakers altogether).

```
perl -e 'alarm 600; exec @ARGV' /Applications/Godot.app/Contents/MacOS/Godot --path . -- [--new] --<mode>
```

(`perl … alarm` is a time limit: macOS has no `timeout`.) `--new` starts a fresh game; on its first run it reloads the
scene and the test is lost, so either run it twice or delete the test save
(`~/Library/Application Support/Godot/app_userdata/Flor de Lliri - Godot test/test_save.json`) and run without it.

Check a script without running the game: `Godot --headless --path . --check-only --script res://engine/main.gd`.

## Three kinds of test run (round 26, the user's rule)
1. **The part that changed** — always, after every build: pictures of the place that was worked on (`--views=` with a
   view file; the round's view files are kept in `workshop/screenshots/round<N>/`) and the one test that covers it.
2. **The quick set, one launch** — when asked: `tools/run_tests.sh quick` (about 2½ minutes, silent): missions, stairs,
   the north end to end, the Sagrat Cor's rooms, the debug menu, all in one game started fresh. The log is
   `workshop/test-runs/barcelona/quick/log.txt`.
3. **The full run** — when the user is happy with how everything sits: `tools/run_tests.sh full` (about 15 minutes):
   the quick set, then the flowers, the church steps, the hill escapes, every room (with its picture), and the
   frame-rate check. Log and pictures in `workshop/test-runs/barcelona/full/`.
Do 1 without asking; ask before 2 and 3. A suite runs several tests in the one launch (`tests.gd` `run_suite`: each
test ends with `end_test()`, which only quits the game when the test runs alone; every test starts out of doors).

## The tests that must pass before a change is finished

| Test | What it checks | Passing looks like |
|---|---|---|
| `--missions` | The first missions end to end (card, torró with exactly €6, Trufa, the bike) | `MISSIONS ok` |
| `--talk` | Every person answers; the party guests leave after the party | no `BAD` lines |
| `--rooms=<dir>` | Every door in and out, a picture of every room | `ROOMS bad=0` |
| `--stairs` | Walking up and down every stair | `walked up` / `walked down` |
| `--north=<dir>` | The north end to end: slope, barrier, park gate and ticket, the park's terraces and stairs at their heights, how close she gets to the wall, the Park Güell mystery, cable car, wheel, ball, spirit level, path open | every line as expected; `NORTH terrace … OK` ×8, `NORTH wall: stopped` under 0.8 m |
| `--hillescape` | The hill path's railing and banks from every few metres, both sides; the glade's fences | `0 escapes`, both `HELD` |
| `--flowers=<dir>` | The five wildflowers: each offered, picked; Alba trades | `traded=true` |
| `--cove` | The east end (round 25): the breakwater, the sea round its end and the wood's rise stop her | every line `OK` |
| `--thief=<dir>` | The pickpocket story | as in the log |
| `--exam=<dir>` | The exam montage | pictures |
| `--moves`, `--veer=<dir>` | Steering feel (turns, zig-zags) — the user notices any lurch | unchanged numbers |
| `--perf` | Frame rate and what costs most at four places | ~50 fps at 1280×800 |

## Pictures for looking (no pass/fail: look at them)

| Test | Pictures |
|---|---|
| `--views=<dir> --viewfile=<json>` | Many camera views in one run. The JSON: `{name: [from x, h, z, to x, h, z, (minutes of the day), (Sandra x, z)]}`, metres. |
| `--look=<png> --from=X,Y,h --to=X,Y,h` | One view (2D tiles). |
| `--day=<dir>` | The light through the day. |
| `--benchview=<dir>` | A picture from each viewpoint's bench (round 25: E should offer nothing there). |
| `--blockglb=<file>:<tag>` | (with `--views=`) one block from `builder/window_options.py` in place of the built one. |
| `--addglb=<file>[:<hide>]` | (with `--views=`) a glb added to the city, e.g. `builder/trunk_options.py`'s trees on the beach. |
| `--telescope=<dir>` | The coin telescope: pays, looks (pictures), turns it, steps back; haze and detail put back. |
| `--leafshadow=<dir>` | Leaf shadows as now and within 50, 25, 10 m of her, at four deep spots in the woods: pictures and frame rates. |
| `--ballwalk=<dir>` | Down from the hill path's top leg through the wood to Laia's ball; E offers it (start with `--new`: in an old save the ball may be taken). |
| `--ballactive` | With `--views=`: Laia's ball lying in the wood for the pictures (use with `--new`). |
| `--sagratcor=<dir>` | (round 26) The Sagrat Cor's two churches: walked into by their own doors (the crypt from the funfair, the upper church from the terrace), pictures inside, walked out again. |
| `--hide=<names>` | (with `--views=`) built objects hidden by exact name, e.g. `SagratCor`, to put an option from `--addglb=` in their place. |
| `--churchsteps=<dir>` | The Sagrat Cor: up each flight of steps to the terrace, across to the front, held by the balustrade; the porch and the hill behind the funfair hold her (pictures). |
| `--hillbike` | The bike up and down a straight of the hill path, and the speed carried on after. |
| `--nofar` | (with `--views=`) everything drawn at any distance. |
| `--lanternmock` | (with `--views=`) the bigger hill-rail lanterns, mocked up, for pictures. |
| `--mapscreen=<png>` | The map (M) in town and up the hill. |
| `--dogride=<dir>` | Trufa: alongside, sitting, the pounce into the basket, riding. |
| `--ui=<dir>` | The HUD and panels at two window sizes. |

`--trailglb=<file>` (on any test run) swaps the wood's path ribbons for a `.glb` from `builder/trail_options.py`, to see
a path style in place without a build.

## All the modes

`--high --shots= --pose= --night= --dog= --block= --aerial= --bike= --elev= --flicker= --rider= --corners= --ride=
--moves --veer= --fronts= --cast= --tour= --walkers= --perf --rooms= --talk --missions --map= --mapscreen= --look=
--views= --flat= --north= --facadeflicker --partyout= --gfxperf --exitview= --day= --accs= --front= --wear= --wild=
--bag= --church= --stairs --stuck= --pocket --caps= --hatwalk= --hatlive= --bump --talkstay --ui= --glare=
--occlprobe=<dir>,x,z,heading (the view there before and after a photo) --groundshot=<dir>,<id>,<mission> (a mission's thing lying there, two views) --looktest=<dir>[,bench,viewfinder,wheel,funicular,telescope] (↑ looks up, ↓ down, at her eyes) --idleline=<png>[,study|,steps] (,steps: every mission step's line count) --mapshot= --clearance --debugmenu (with --nodebug: as a player, P does nothing) --forestbike --bikecam= --rope --touchtest= --touchtoggle --lean= --hairmove=
--doorcam --bikesize= --churchdoor= --dogride= --thief= --shadowcrawl= --journal= --exam= --swaycost --hillescape
--flowers= --benchview= --cove --sagratcor=`

Added in round 41 (each says what it checks in its comment): the funicular `--funiride= --funiquick= --funitoggle=
--funicar= --funiwatch= --funitilt --funijolt --funiside --funiground --stationcam= --camprobe[=fair] --fpkeys`; the
wheel `--wheelride= --wheelseat= --wheelpeak=`; `--benchsit --cryptprobe --armshots= --titleshots= --titlesound --kitetalk=`; every frame kept for comparing `--framerec=<dir>,<mode>,<secs>,…` (with `--adaptive` as in play; `--upscaler=fsr|fsr2|mfx|mfxs`, `--fixscale=<s>`); the frame time with each costly thing turned down in turn `--perfopts` (`--perfonly=0,3`; `--noocclude` draws what is hidden behind the blocks again, to compare; `--lookopts=<dir>` pictures the options; `--titleload=<dir>` the title's Load game; `--fpstour` the frame rate walking, cycling, on the rides, in a room; `--framerec=<dir>,wheel,<secs>,<round>` on the Ferris wheel, with `--recsmall` `--clock=` `--hide=` `--nofade=` `--fartone=` `--forestfade` `--interp`);
Marta's camera `--phototest --vftest= --vfplaces=` (their photos land on the user's Desktop, as the user wants; `--photodir=<dir>` exists but isn't used);
the map shot takes `--mapnomsaa` (needed since the walk box grew: with 4× smoothing the picture came out black).

Each is a `run_<name>` function in `tests.gd` with a comment saying what it does. A new test: add it to `MODES` at the
top and write its `run_` function; print one line per result in capitals (`NAME …: OK/BAD`).
