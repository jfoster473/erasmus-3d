# Building a world

Everything a world shows is made by Python scripts run inside Blender, headless. You need **Blender 5.2**
(`/Applications/Blender.app`) and **Godot 4.7** (`/Applications/Godot.app`). Python 3 with Pillow is needed for the
map painter; numpy comes with Blender.

All commands below are run from the project folder (`Erasmus 3D/`). `B` stands for
`/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P`.

## 1. The data (only when a world's people, texts, missions or rooms change)

```
cd worlds/barcelona/data
sh extract.sh            # only if the 2D game itself changed: dumps its data to data2d.json
python3 remap3d.py       # data2d.json + north_data.py + round23_data.py -> data3d.json, map3d.png
```

Texts are changed in the Python files (`remap3d.py`, `north_data.py`, `round23_data.py`), never in `data3d.json`.

## 2. The full build (about 1½ minutes since round 26; the first after a Meshy model changes, about 3½)

```
B builder/build_assets.py > bigfiles/built/barcelona/build.log 2>&1 &
```

Or, the same build with a stopwatch (every line stamped with its second, and a table at the end of where the time
went): `B builder/time_build.py > bigfiles/built/barcelona/build.log 2>&1 &`. Round 26's table: the city's blocks about
65 s, the hill (`north_build.py`) 67 s, the rooms 66 s; within those, slimming the 22 Meshy models down every build
took 119 s and reading them in 24 s, and writing the two game files 16 s.

**The Meshy cache** (round 26): each Meshy model, once slimmed and set straight, is kept in `bigfiles/cache/meshy/`
(`.blend` files, one per model and size; Godot ignores the folder). The next build reads it in a tenth of a second
instead of slimming again. It is remade by itself when the model's `.glb` is newer, or when its size or its fitting
(`MESHY_BUILDINGS`) changes; delete the folder to remake them all.

Keep the Mac awake while it runs (`caffeinate -i -w <pid>`): asleep, it crawls. Its output (Python's `print`) arrives
in bursts. When it ends, check the log:

- no `Traceback`;
- 26 `ROOM` lines (one per room);
- `FOREST trees …`, `NORTH woods: …`, `NORTH rail: …`, `PARK trees …`, `NORTH built: …`.

It writes `bigfiles/built/barcelona/city.glb`, `interior.glb`, `scene.json`, `forest_light.png`, `forest_nobike.png`,
`hill_light.png`. The game reads them at start; nothing in Godot needs re-importing.

**Trap:** the build reads the world's scripts as it reaches them (`world2d.py`, `north_build.py`, `interiors.py`
late), so a file edited while it runs may or may not be in it. Rebuild after editing.

To build another world: `WORLD=valencia B builder/build_assets.py` (or set `erasmus/world` in `project.godot`).

## 3. The map (after any build that changes what is seen from above)

```
/Applications/Godot.app/Contents/MacOS/Godot --path . -- --mapshot=/tmp/mapshot.png
python3 builder/stylise_map.py /tmp/mapshot.png worlds/barcelona/map
```

The first is the world from straight above (5000+ px); the second paints it and draws the paper band with the arrows
to the places off the city map (`WAYS` in `stylise_map.py`).

## Quicker looks (seconds to a few minutes)

| Command | Shows |
|---|---|
| `B builder/preview.py -- <what> <out dir>` | One landmark (`sagrada`, `upf`, `mnac`…), room (`int_upf_lib`…) or block (`block_-30_0`) rendered from a few sides. `PREVIEW_VIEW="name:x,y,z,tx,ty,tz"` for your own view (from the thing's centre). |
| `B builder/preview_forest.py -- <out dir>` | The eastern wood alone. |
| `B builder/trail_options.py -- <out dir> D1,D2,G` | The wood's path ribbons in each style, as `.glb`s the game can show in place (`--trailglb=<file>` on any test run). |
| `B builder/build_props.py` | The bicycle (`bigfiles/built/props/bicycle.glb`). |
| `python3 builder/build_audio.py bigfiles/built/audio [--sfx]` | Music and sound effects. |

## Where to change what

| To change | Edit |
|---|---|
| A house front, windows, balconies, shops | `builder/kit.py` (`build_kit_block`, `crisp_window`, `ground_floor`) |
| A landmark | `worlds/barcelona/build/landmarks.py` (or `sagrada.py`, `upf.py`) |
| The ground, sea, beach, cove, far hills | `worlds/barcelona/build/world2d.py` |
| The eastern wood, its paths' layout | `worlds/barcelona/build/forest.py` |
| How worn paths look (all worlds) | `builder/trails.py` |
| The hill, funfair, cable car, Gràcia, Park Güell | `worlds/barcelona/build/north.py` (layout, ground height) and `north_build.py` (models) |
| A room's furniture | `worlds/barcelona/data/remap3d.py` (lists) and `worlds/barcelona/build/interiors.py` (how each kind is drawn) |
| Who stands where, what they say, missions | `worlds/barcelona/data/*.py`, then `remap3d.py` |

## Coordinates

- Engine metres: x east, z south, h up. Blender: (x, −z, h).
- Barcelona's 2D tiles are 3.3 m: tile (X, Y) → metres ((X − 55)·3.3, (Y − 45)·3.3).
- Rooms are built 40 m apart far from the city; a room's (x, y) in metres from its back-left corner.
