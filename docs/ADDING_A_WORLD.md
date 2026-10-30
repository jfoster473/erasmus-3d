# Adding a world (Valencia)

**Design first:** `docs/rules/` holds the rules every world is built to (the user's, rounds 1–36), and
`docs/rules/11_new_world_recipe.md` the order to work in. This file is the mechanics: folders, files and commands.

A world is a folder `worlds/<name>/` with the same parts as Barcelona's. The engine (`engine/`, `shaders/`, the sound in `bigfiles/built/audio/`)
and the builder's machinery (`builder/`) are shared; everything about a place — its streets, buildings, people,
missions, map — lives in its folder.

## The parts a world needs

```
worlds/valencia/
  data/        data3d.json and the scripts that make it        (people, missions, items, shops, rooms, tiles)
  build/       its Blender scripts                               (ground, buildings, landmarks, rooms)
  game/        story.gd (extends res://engine/game.gd), and any special places' scripts
  tests/       tests.gd (its play tests)
  map/         world.png + world.json (painted from a photo from above)
  icons/       <item id>.png for each item
```

What its build makes goes to `bigfiles/built/valencia/` (city.glb, interior.glb, scene.json …), off GitHub.

## Step by step

1. **Copy Barcelona's folder** as a starting point: `cp -R worlds/barcelona worlds/valencia`, then delete
   `map/*` (it is repainted); the build makes `bigfiles/built/valencia/`.
2. **The data** (`data/`). `data3d.json` holds (see Barcelona's for the shapes):
   - `tiles`, `tileNames`, `MW`, `MH` — the ground plan on a grid of 3.3 m tiles (roads, pavements, blocks, beach,
     sea, park, forest…). Barcelona's came from the 2D game; a new world can write its grid with a script.
   - `BUILDINGS` — every enterable building: its block, which side its door faces, its room (`int`), its name.
   - `INTERIORS` — every room: size, floor, walls, and its furniture list `[kind, x, y, {options}]` (kinds are drawn by
     `build/interiors.py`).
   - `NPCS` — every person: name, where they stand (`at`: `['world', x, y]` in tiles or `['int_x', x, y]` in a room),
     their look (skin, hair, clothes, hat…), their lines, and flags the story reads.
   - `MISSIONS` — each mission's texts: its name, the offer, the steps (`obj`), the journal lines (`log`), the
     rewards. `ITEMS`, `SHOPS` likewise.
   Write it with a Python script (like `remap3d.py`) so changes can be remade, never by hand.
3. **The story** (`game/story.gd`). It starts `extends "res://engine/game.gd"` and overrides the engine's hooks (the
   empty functions at the end of `engine/game.gd`): `mission_talk(id, name)` (what people say about missions, and
   what happens), `shop_talk`, `use_phone`, `read_card`, … A world without some of them just doesn't override them.
   Barcelona's `story.gd` is the example. Special places with moving parts (rides, gates) get their own script like
   Barcelona's `north.gd`; `engine/main.gd` currently loads `game/north.gd` and `game/touches.gd` by name: give the new
   world files of those names (they may be nearly empty), or make `main.gd` load them only if they exist.
4. **The builder scripts** (`build/`). The build runs, in order, from `builder/build_assets.py`: the shared helpers and
   facade kit, then the world's `build/landmarks.py`, the block loop (still in `build_assets.py`: see below),
   `build/world2d.py` (the ground and everything off the street grid) and `build/interiors.py`. A new world's
   versions decide what it looks like: Valencia's `world2d.py` would make the Turia gardens, the beach at Malvarrosa,
   the City of Arts and Sciences as a landmark…
5. **Build** (`WORLD=valencia` before the Blender command; see `BUILDING.md`), then set `world="valencia"` in
   `project.godot` and run the game.
6. **The map**: `--mapshot` then `builder/stylise_map.py` (its `WAYS` list — the arrows to places off the city
   map — is Barcelona's: give the new world its own).
7. **Tests**: copy Barcelona's `tests.gd` and change the places it visits.

## What still assumes Barcelona (to fix before or while adding Valencia)

These are in shared code and should move behind hooks or into world files:

- `engine/game.gd`: `build_ground()` (the things to pick up and where), `make_ground_node()` (their models),
  `use_thing()` (furniture and street things), parts of `talk_to()`, `objective_text()`, `on_exit_to_world()`
  (regrowing), `is_quest_item()`, `WILDFLOWERS`, `RED_MUSHROOMS`, `VASE_*`.
- `engine/main.gd`: `debug_places()`, the map's area names (`make_map_labels`), the Sagrada Família's room
  special case, the list of named materials lit at night, the city's edges (`city_rect` comes from `scene.json`,
  fine), loading `game/north.gd` and `game/touches.gd` by name.
- `engine/npcs.gd`: a few people's looks by name.
- `builder/build_assets.py`: after its helpers, Barcelona's block loop, street names and special spots (Jordi's
  shop, the corner plaques). Split it into `builder/lib.py` (helpers: `MB`, `Cards`, `mat`, `make_image`, coordinate
  helpers, `meshy_mesh`, lamps, trees) and `worlds/barcelona/build/city.py` (the block loop), with `build_assets.py`
  just running the two.
- `builder/kit.py`: the Eixample house kit is Barcelona's style; Valencia would want its own facade kit (or kit
  options) for its old town.
- `builder/stylise_map.py`: `WAYS`.

The coordinates (3.3 m tiles, the origin at tile (55, 45)) are Barcelona's 2D game's; a world made from scratch can
use the same convention with its own origin.
