# Erasmus 3D

Sandra's Erasmus semester in a stylised, romantic city, in 3D: walk and cycle its streets, meet its people, run
their errands, earn a little money, explore beyond the city (the woods, the beach, the hill up to the funfair, Park
Güell), and sit the exam at the end. The first city is **Barcelona** (a 3D remake of the 2D browser game in
`../2D version/`); the project is laid out so that a second city — Valencia — can sit beside it.

**The documents:** this README is for people (what it is, how to run it, the controls). `CLAUDE.md` is for an AI
coder continuing the work. `docs/` explains the design in depth:

| Document | For |
|---|---|
| `docs/ARCHITECTURE.md` | How the game and the builder are put together, folder by folder |
| `docs/BUILDING.md` | Making a world's 3D models (Blender), its data, its map |
| `docs/TESTING.md` | The automated play tests, and which must pass |
| `docs/ADDING_A_WORLD.md` | Adding Valencia, step by step, and what still assumes Barcelona |
| `docs/rules/` | Every rule the worlds are built to, by topic (the user's, rounds 1–36) |

## Folder

Three parts, so the game can be handed over: **the code and the rules go to GitHub**, **the big files go by Google
Drive** (`bigfiles/`), and **the workshop stays on this computer** (`workshop/`). `.gitignore` keeps the last two off
GitHub.

| Path | What it is |
|---|---|
| `project.godot`, `main.tscn` | The Godot project (this folder is it) |
| `engine/` | The game's rules and machinery, the same for every city |
| `shaders/` | The look (sky, sea, foliage, people…) |
| `worlds/barcelona/` | Everything Barcelona: its story and special places (`game/`), data (`data/`), Blender scripts (`build/`), map, item pictures, tests |
| `builder/` | The Blender build's shared machinery and tools (`paths.py` says where every folder is) |
| `docs/` | The documents above and the rules (`docs/rules/`) |
| `tools/` | `Play the game.app`, the test runner and the picture tools |
| `bigfiles/` | **Off GitHub, by Google Drive.** The Meshy models (bought: can't be remade) and what the build makes: the built city, the bicycle, the sound. `bigfiles/README.md` says which is which |
| `workshop/` | **Kept on this computer.** The journal (every round's decisions, history and to-do list), the screenshots, the test runs, the retired tools (`workshop/README.md`) |

## Getting started (downloaded from GitHub)

GitHub holds the code, the data and the rules, but not the 3D models: those are too big for GitHub and come
separately, by Google Drive. To play you need three things, then one command.

**1. Godot 4.7** (the free game engine the game runs in): download the standard version, not the ".NET" one, from
[godotengine.org/download](https://godotengine.org/download) (it was made with 4.7.2). On a Mac, put `Godot.app` in
`Applications`. Nothing else needs installing to play (Blender and Python are only for rebuilding the city).

**2. The big files** (`bigfiles/`): ask the game's owner for the Google Drive link, download the folder and put it
**inside this folder**, named exactly `bigfiles`, next to `project.godot`. To play, about 720 MB is all it takes:

```
Erasmus 3D/
  project.godot
  engine/  shaders/  worlds/  builder/  docs/  tools/
  bigfiles/                  <- from Google Drive
    built/                   (the built city, the bicycle, the sound: 546 MB — needed to play)
    originals/meshy/         (only these 14 models are needed to play, 172 MB: the people and the dog —
                              child, man, man2, man3, montse, oldlady, oldman, passerby, sandra_a, sandra_b,
                              trufa, woman, woman2, workman, each .glb)
```

The rest of the owner's `bigfiles/` (the houses and furniture as bought, which the build has already baked into the
city, and `cache/`) is only needed to rebuild the city in Blender.

**3. Once, the first time: let Godot prepare its files** (seconds to a minute; it prints a few lines and stops by itself).
In a terminal, from this folder:

```bash
/Applications/Godot.app/Contents/MacOS/Godot --headless --path . --import
```

**Then play:** double-click `tools/Play the game.app` (Mac). If the Mac says it's from an unidentified developer,
right-click it, choose **Open**, then **Open** again (only the first time). Or start it from a terminal, from this
folder:

```bash
/Applications/Godot.app/Contents/MacOS/Godot --path .
```

On Windows or Linux use the same commands with the path to your Godot program instead, for example
`"C:\Godot\Godot_v4.7.2-stable_win64.exe" --path .` (Windows) or `./Godot_v4.7.2-stable_linux.x86_64 --path .`
(Linux). The game was made and tested on a Mac (Apple M1); on Windows it uses AMD's upscaler instead of Apple's, untested.

**If something's wrong:** a grey or empty world, or "Could not load" messages, means `bigfiles/` is missing, misnamed
or in the wrong place (it must be `bigfiles/built/barcelona/scene.json` from this folder). Missing pictures or a crash at
the start usually means step 3 wasn't run.

### For an AI assistant (Claude Code) setting it up

Do these in order, from this folder, and stop to ask the user where any step fails:
1. Check Godot: `/Applications/Godot.app/Contents/MacOS/Godot --version` should print `4.7…` (on other systems, ask
   the user where Godot is). If it isn't installed, tell the user to install Godot 4.7 (standard, not .NET) from
   godotengine.org — don't download it yourself without asking.
2. Check the big files: `bigfiles/built/barcelona/scene.json` and `bigfiles/originals/meshy/sandra_a.glb` must exist. If not, ask
   the user for the Google Drive folder (only they have the link) and to put it here as `bigfiles/`.
3. First time only: `/Applications/Godot.app/Contents/MacOS/Godot --headless --path . --import`
4. Optional check that it works, silently, about 2 minutes (prints `MISSIONS ok`):
   `/Applications/Godot.app/Contents/MacOS/Godot --path . -- --missions`
5. Play: `open "tools/Play the game.app"` (Mac) or `/Applications/Godot.app/Contents/MacOS/Godot --path .`

`CLAUDE.md` is for continuing the game's development; to just run it, the steps above are all that's needed.

## Running (on this computer)

Double-click `tools/Play the game.app`, or:

```bash
/Applications/Godot.app/Contents/MacOS/Godot --path "Erasmus 3D"
```

### The debug menu (hidden from players)

The debug menu is in the game but switched off, so players can't open it. To use it yourself, start the game with
`--debug` on the end (after a lone `--`):

```bash
/Applications/Godot.app/Contents/MacOS/Godot --path "Erasmus 3D" -- --debug
```

Then **P** opens it (and the touch controls show a **DEBUG** button). It has: go to any place, set the time, + €50 /
+ €500, get the bicycle, get the park & funicular pass, next time of day, Sandra's outfit, music on/off, quality,
bounce light, light shafts, quick walking, and touch controls on/off. The top-right corner then also shows the
quality, bounce light and light shafts (players see only the frame rate, the light's name and the triangles). Started the normal way (or with `tools/Play the game.app`), P does nothing.
Tests switch it on by themselves; add `--nodebug` to a test to play it as a player would.

To rebuild the city after changing its Blender scripts or data, see `docs/BUILDING.md` (about 2½ minutes, Blender 5.2).

## Controls

| Key | Action |
|---|---|
| WASD / arrows | Walk. Forward + left/right steers, turning faster the longer it's held (much sharper inside the Sagrada Família, among its columns); left or right on its own turns her straight that way; down turns her back |
| Mouse (click to capture) / right drag / pad right stick | Turn the camera |
| Mouse wheel | Zoom (on the bike the camera pulls back further, until she gets off) |
| E / Enter | Talk, look, read, pick up, open; get off the bike |
| Walk into a door or a stair | Go in or out, up or down |
| On a bench, the Ferris wheel or the funicular | E sits down or gets up, or switches between her own eyes and following her; the arrows or the mouse look round |
| The Pentax K1000, Marta's spare camera (backpack → pick it) | Straight into its viewfinder at her eyes: W A S D walk, the arrows or the mouse look round, E takes the photo (a click and a shutter's blink; saved on the Desktop, 3:2, with the date, time and lens in its corners), Z zooms in or out, Esc puts it away. Not on the bike; on a ride it's at her seat; it puts itself away at any door, ride's end or sleep |
| Title screen | Continue, Load game (a copy made by Export save in the Esc menu), New game |
| At the funfair's coin telescope | E: pay €1 to look over the city for a minute (arrows turn it slowly; E or Esc to step back) |
| I / J | Backpack, filling nearly the whole screen (arrows choose; Enter uses; E eat, R read, W wear) / journal, as in the 2D game: one page of entries (no achievements since round 25: only the missions are counted; ↑ ↓ scroll) |
| M / Tab | The map (Esc or Enter puts it away) |
| B | Hop on or off her bicycle (once Jordi has given it to her) |
| N | Music on/off (also in the debug menu) |
| T | Move the clock on: morning → midday → evening → night (the light follows the clock: a game minute every second; also in the debug menu) |
| Esc | Free the mouse; then the pause menu (with Export save / Import save, as in the 2D game); in a question, "no thanks"; moves talk on like Enter, and closes the journal |
| P | The debug menu, hidden from players: only when the game is started with `-- --debug` (or in a test). Go to any place, + €50 / + €500, get the bicycle, set the time, next time of day (T), Sandra's outfit (C), music (N), quality (Q), quick walking |
| C | Switch between the two Sandras (also in the debug menu) |
| Q | Full / balanced quality (only with the debug menu on; also in it) |
| G / V | Bounce light / light shafts (only with the debug menu on; also in it) |

**On a phone or tablet** (or on a computer: `-- --touch`, or debug menu → Touch controls, and the mouse acts as a finger), on-screen
controls laid out like the 2D game's: a **pad** to walk, **A** (talk, look, read, pick up, open; confirm) and
**B** (back: close a panel or the map, cancel a choice, leave the pause menu), and **BAG, MAP, LOG, BIKE, LOOK
and ☰** (the menu; DEBUG too with `--debug`). **LOOK** switches looking round on: drag a finger anywhere else on the screen to turn
the camera (with the other thumb still on the pad, if you like); LOOK again switches it off. Held sideways, the
pad and A/B sit in the bottom corners and the buttons down the right edge; held upright, the game fills the top of
the screen and the controls sit on a very dark grey deck underneath, as in the 2D game. Help lines name the pad,
A and B instead of keys.

