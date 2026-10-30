# Architecture

*Erasmus 3D* is a small open-world story game: Sandra, an Erasmus student, lives a semester in a city, runs errands
for its people, earns a little money, explores, and sits an exam at the end. It is a 3D remake of a 2D browser game
(`../2D version/`). The first world is **Barcelona**; the layout below is meant to let a second world (Valencia) be
added beside it without touching the first.

There are two programs:

- **The game** — Godot 4.7 (Forward+), GDScript. The Godot project is this folder (`project.godot` at the top).
- **The builder** — Python scripts run inside Blender 5.2, headless. They make every 3D model of a world (its ground,
  buildings, trees, rooms) from code and data, and write them as `.glb` files plus a `scene.json` that tells the game
  where everything is (doors, walls, trees, paths, people, streets…).

The game never builds geometry of its own beyond small things (people's accessories, butterflies, item models on the
ground); it loads what the builder made.

## The folders

| Folder | What is in it | Godot imports it? |
|---|---|---|
| `engine/` | The game's rules and machinery, the same for every world (see below) | yes |
| `shaders/` | Every `.gdshader` (sky, sea, foliage, forest floor, characters, sunbeams…) | yes |
| `worlds/<name>/game/` | The world's own scripts: its **story** (`story.gd`), its special places' behaviour (Barcelona: `north.gd` for the funfair, cable car, hill path and Park Güell; `touches.gd` for small set pieces; `exam_scene.gd`) | yes |
| `worlds/<name>/tests/` | The world's automated play tests (`tests.gd`) | yes |
| `worlds/<name>/map/` | The painted map shown with M (`world.png` + `world.json`) | yes |
| `worlds/<name>/icons/` | Item pictures for the backpack and shops | yes |
| `worlds/<name>/data/` | The world's **data**: people, their lines, missions, items, shops, rooms, the tile map (`data3d.json`), and the scripts that make it | no (`.gdignore`) |
| `worlds/<name>/build/` | The world's **builder scripts**: its ground, buildings, landmarks, woods, paths, rooms | no |
| `builder/` | The builder's shared machinery: mesh helpers, materials, the facade kit, worn paths, props, audio, previews, the map painter, `paths.py` | no |
| `docs/` | These documents, and `rules/` (every rule worlds are built to, by topic) | no |
| `tools/` | The launcher, the test runner and the picture and rule-checking tools | no |
| `bigfiles/` | **Off GitHub, handed over by Google Drive** (`bigfiles/README.md`): too big for GitHub, or made by the build | |
| `bigfiles/originals/meshy/` | Models every world shares, bought from Meshy: people, Trufa, furniture (`flat/`), houses, lamp, bench, café table, window | no |
| `bigfiles/cache/meshy/` | Those models slimmed and set straight, kept between builds | no |
| `bigfiles/built/<name>/` | What the builder made for a world: `city.glb`, `interior.glb`, `scene.json`, light maps, `build.log` | no |
| `bigfiles/built/props/` | The bicycle and the window pictures (made by the builder) | no |
| `bigfiles/built/audio/` | Music and sound effects (made by `builder/build_audio.py`) | yes |
| `workshop/` | **Kept on this computer only** (`workshop/README.md`): the journal (`journal/`: decisions, history, to-do list, the round-by-round state), `screenshots/`, `test-runs/`, `retired-tools/` | no |

The folders are named in one place each: `builder/paths.py` for the builder and tools, `engine/main.gd` (`big_dir`,
`out_dir`, `asset_path()`) for the game. `bigfiles/` sits inside the project because Godot loads only from inside it;
`.gitignore` keeps it and `workshop/` off GitHub.

Which world is played is set once, in `project.godot`:

```
[erasmus]
world="barcelona"
```

The game reads it (`engine/main.gd`, `world_name`, `world_res()`); the builder reads it too (`builder/paths.py`), or
the `WORLD` environment variable when building another world.

## The game (engine/)

`main.tscn` has one node with `engine/main.gd`. `main.gd` is the conductor: it loads the world, makes the physics, the
player, the camera, the light, the HUD and the map, and creates the other parts as child nodes with their scripts.

| Script | Job |
|---|---|
| `main.gd` | Loading (`scene.json`, the `.glb`s, `data3d.json`), physics and walls, Sandra (walking, steering, the bike), the camera, the light by the clock (sun, moon, sky, glare), doors and rooms, "E" interaction (`nearest()`, `interact()`), the HUD, the talk box, the map, frame-rate scaling. The longest file; its sections are marked `# ----`. |
| `game.gd` | The **rules**: the save, the talk queue (`say`, `ask`, `after`, `pump`), items and the backpack, missions' bookkeeping (start, complete, the journal, the HUD's objective), shops, things on the ground (picking up, regrowing), bins and cupboards, the reader, the clock (`tick`). It declares **hooks** — empty functions at its end (`mission_talk`, `shop_talk`, `north_talk`, `use_phone`…) — that a world's story overrides. |
| `panels.gd` | Every card-style panel: backpack, shop, journal, reader, cupboard, bin, debug menu. |
| `npcs.gd` | The named people: making them from Meshy models, their looks (hair, clothes, hats, accessories), where they stand, turning to talk, scene modes (follow, run to, hold, handcuffed). |
| `people.gd` | Passers-by walking the streets round obstacles. |
| `street_life.gd` | Street things that move or are used: bikes (parked and ridden), the dog Trufa (`dog.gd`). |
| `dog.gd`, `dog_pose.gd` | Trufa: following, waiting, riding in the basket; her pose. |
| `bike.gd`, `rider_pose.gd`, `posture.gd`, `cuff_pose.gd` | The bicycle; Sandra's riding/sitting pose (its own two-bone IK); her standing posture fix; handcuffed arms. |
| `wildlife.gd` | Pigeons, butterflies, fireflies, gulls. |
| `ambience.gd` | Music and sound effects. |
| `touch.gd` | On-screen controls for phones and tablets. |

A world's story script **extends** the engine's rules:

```
# worlds/barcelona/game/story.gd
extends "res://engine/game.gd"
func mission_talk(id: String, name: String) -> bool: …   # overrides the engine's empty hook
```

and `main.gd` loads it as the game script: `game.set_script(load(world_res("game/story.gd")))`.

### What happens each frame

`main._physics_process` → input → Sandra's movement (walls are `StaticBody3D` boxes; on hills her body stays at street
level and only her model is lifted to the ground's height, `ground_at()`/`terrain_at()`) → the world's own ticking
(`north.tick`), people, the dog, wildlife, `game.tick` (the clock: one game minute per two real seconds) → the camera →
the light (`light_from_clock`, every frame) → the HUD.

### Data the game reads

- `bigfiles/built/<name>/scene.json` — made by the builder: `entrances` (doors: where, which room, plaques), `blocked`
  (walls as rectangles), `solids` (walls as polygons: Gràcia's blocks), `flats` (level or ramped ground that says
  its own height: the park's terraces and stairs), `trees`, `terrain` (the ground's height grid), `streets` (names by area), `interiors` (rooms:
  their walls, furniture, stairs, lights), `forest_*`, `north` (the funfair, paths, railings, flowers, benches…).
- `worlds/<name>/data/data3d.json` — the world's people (`NPCS`: name, place, look, lines), `MISSIONS` (texts, steps,
  log lines), `ITEMS`, `SHOPS`, `INTERIORS`, the tile map. The story script and `game.gd` read it as `data`.
- `worlds/<name>/map/world.json` — where the map picture's edges are, for the "you are here" dot.

## The builder (builder/ + worlds/<name>/build/)

`builder/build_assets.py` is the entry point (run by Blender, ~30 min). In order:

1. `builder/paths.py` — where the world's folders are.
2. Helpers: `MB` (a mesh being built: faces, boxes, cones, spheres), `Cards` (leaf cards for foliage), `mat()`
   (materials), `make_image()` (procedural textures), coordinate helpers (`B`, `BT`, `mT`, `to_m`), `text_obj()`.
3. Reads `data3d.json` (`W2`).
4. `builder/kit.py` — the facade kit: Eixample houses (`build_kit_block`), modelled windows (`crisp_window`), balconies,
   awnings, shops, plants.
5. The world's `build/landmarks.py` (whole-block landmarks; it runs `sagrada.py`, `upf.py`).
6. The block loop, pavements, then the world's `build/world2d.py` — everything outside the street grid: the ground's
   height grid, the sea and beach, the river, the hills; it runs `build/forest.py` (the eastern wood; it uses
   `builder/trails.py` for worn paths) and `build/north_build.py` (the hill, the funfair, the cable car, Gràcia (its
   blocks rings of the kit's houses, `gracia_block()`), Park Güell, the Sagrat Cor; its layout and ground heights in `build/north.py`; the light on the hill wood's floor over
   the day in `build/hill_light.py`, plain numpy, as `forest.py`'s `forest_light()` for the eastern wood).
7. The world's `build/interiors.py` — every room (runs `sagrada_inside.py`, and `sagrat_inside.py` for the Sagrat Cor's
   crypt and upper church; textured stone from `builder/stone_tex.py`, shared with the church outside).
8. Writes `out/city.glb`, `out/interior.glb`, `out/scene.json`.

Everything is in **metres**, engine axes: x east, z south, h up. The 2D game's tiles are 3.3 m (`T`); a 2D tile
(X, Y) is metres ((X − 55)·3.3, (Y − 45)·3.3). Blender is Z-up with y north: Blender (x, −z, h).

Smaller tools in `builder/`: `preview.py` (one block, landmark or room, a minute), `preview_forest.py`, `preview_north.py`,
`trail_options.py` (path styles to try in the game), `build_props.py` (the bicycle), `build_audio.py`, `slim_meshy.py`,
`make_passerby.py`, `stylise_map.py` (paints the map from the game's photo from above), `mock_north.py`.

## The world's data (worlds/<name>/data/)

Barcelona's data comes from the 2D game: `extract.sh` runs the 2D game's own code (macOS JavaScriptCore) to dump its
data and generated world to `data2d.json`; `remap3d.py` turns that into the 3D game's layout and text
(`data3d.json`, `map3d.png`), then applies the later rounds' changes (`north_data.py`, `round23_data.py`). **To change
what someone says, or a mission's text, edit these Python files and rerun `remap3d.py`** — never `data3d.json` by hand.

## Where the rules end and the world begins (and what is not yet separated)

Separated now: the story's talk and missions (`story.gd`), the world's special places (`north.gd`, `touches.gd`), its
tests, data, map, icons, builder scripts and built files.

Still in the engine, though they are Barcelona's (the next things to move into the world, each behind a hook):

- `game.gd`: `build_ground()` (the world's things to pick up: bottles, shells, wildflowers, the three red mushrooms,
  the ball, the key; with `WILDFLOWERS`, `RED_MUSHROOMS`), `make_ground_node()` (their little models), `use_thing()`'s
  furniture and street things, `talk_to()`'s Barcelona special cases, `objective_text()`, `on_exit_to_world()`'s
  regrowing rules, `is_quest_item()`, `VASE_EMPTY`/`VASE_FULL`.
- `main.gd`: `debug_places()` (Barcelona's places), map label lists (`make_map_labels`), the Sagrada Família's
  sunbeam room special-casing, a few named materials lit at night (`set_emit` list).
- `npcs.gd`: some people's special looks by name.
- `builder/build_assets.py`: Barcelona's block list and street names after the helpers (the helpers should become
  `builder/lib.py`, with the block loop moving to `worlds/barcelona/build/`).

See `ADDING_A_WORLD.md` for the steps to add Valencia.
