# Tools

| Tool | What it does |
|---|---|
| `Play the game.app` | Starts the game (Godot 4.7 must be in /Applications). |
| `sheet.py` | Contact sheets of test pictures: `python3 sheet.py out.png <tile width> <columns> a.png b.png …` |
| `glbcmp.py` | Compares two builds' `.glb` models by content (every shape, material, texture and placement): `python3 tools/glbcmp.py old.glb new.glb`. The bytes differ from build to build (the exporter's order), so a plain file comparison can't tell. |
| `migrate.py`, `split_game.py`, `old_docs.py` | Retired (24 October 2026) to `workshop/retired-tools/`, kept on this computer only: how this folder was made from the old one, `../3D tests/` (20 October 2026). **Never run them again**; `NO_MIGRATE` here stops them (they would copy the old files over the work). |
