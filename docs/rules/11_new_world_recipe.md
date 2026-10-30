# 11 · Making a new world from these rules

The order to work in when a new prompt asks for a new city (say Valencia), with its own layout and missions, built to
the same standard as Barcelona. The mechanics — which folders, which files, which commands — are in
`docs/ADDING_A_WORLD.md`; this file is the design recipe. Every step applies the rule files in this folder.

## 0. What carries over and what doesn't
- **Carries over unchanged**: the engine (walking, the bike, the camera, doors, rooms, talk boxes, panels, the map
  screen, the clock and light, people and NPC machinery, saves), the shaders, the builder's machinery (mesh helpers,
  materials, the worn-path ribbons, the facade kit's parts, trees and planting functions), the shared Meshy models
  (people, the bicycle, lamps, benches, café tables), and **all the rules in this folder**.
- **Made new for the world**: its ground plan, districts, blocks and landmarks, its facade style options, its woods,
  hills, beach or river, its people, story, missions, items and shops, its map labels, its tests.
- **Barcelona-specific rules** (`docs/PATH_RULES.md` sections E–H: the hill path, Park Güell, Gràcia) are worked
  examples, not rules for the new world; the general forms are in `05_streets_and_paths.md`.

## 1. The brief
1. Write the brief back to the user in plain words: the city's character, its districts (a modern grid, an old
   quarter, a seafront, a park, a hill, a river…), its landmarks, who Sandra meets and what she does, how big the
   playable area is. Ask only what can't be decided from the rules.
2. **Mock up the layout first** (`01_working_with_the_user.md` rules 4–5): a plan from above, districts and streets
   drawn, the landmarks placed, for the user to mark and approve before anything is built.

## 2. The ground plan
3. **Lay each district on one grid** (`05` rules 1–3): blocks square-ish and evenly spaced, streets of the right
   width for what uses them, everything on shared lines.
4. **Decide each district's surfaces**: asphalt with zebra crossings in a modern grid, cobbled carriageways and panot
   footpaths in an old quarter (`05` rule 4), gravel walks in parks, worn dirt on hill paths, sand on the beach.
5. **Join the districts properly**: every street end on a district's edge carries its road on into the next district
   (`05` rule 10); a park's wall has a footpath along it and gates with small forecourts (`05` rules 13, 15); the town
   meets nature with a kerbed footpath, then grass (`05` rule 14).
6. **Heights** (`08_terrain_walls_map.md`): streets level along their length, the climb taken by ramps and steps
   between them; one gradient rule for what she can walk (30%); slopes she can't climb visibly steeper, with a wall
   where they must stop her; no invisible walls.
7. **The edges of the world go on**: hills and far land continue on every side, the sea to the horizon, the skyline
   seen to its end (`02_look_light_nature.md`).

## 3. Buildings
8. **Blocks from the facade kit** (`06_buildings_doors_interiors.md`): rows of houses in varied widths and heights on
   the block's edges, shops on the ground floor, balconies, awnings, closed boxes with no gaps; on slopes, a plinth. (Round 38: a square old-quarter block is one height all round — 06 #11.)
9. **Landmarks modelled to their real shape**, in Blender where it can be done well; Meshy only for what can't be,
   and only with the user's say-so (credits).
10. **Every door a real door**; enterable buildings have rooms behind them, entered by walking through.

## 4. Furnishing the streets and nature
11. **Place every thing where it would stand in the real world** (`07_placing_things.md`): lamps at the kerb, trees
    in pits on pavements wide enough, café tables clear of the walking line, nothing on a crossing or in a doorway,
    lamps clear of trees, everything solid, squares filled in proportion with an empty edge strip.
12. **Plant generously** and never leave bare, lifeless ground ("liminal"): woods with three-step floors by the light,
    meadows with scattered trees, verges with tufts and flowers (`02`).

## 5. People and the story
13. **Passers-by on pavements and paths, NPCs where the story needs them**, reachable, facing the way they should, not
    walking off mid-talk; a few sitting at cafés (`10_people_story_missions.md`).
14. **Missions** as steps the player can complete from a fresh game, each target reachable; the story's tone rules
    (people who don't know Sandra's business don't talk as if they did).

## 6. Movement and camera
15. **No changes needed** unless the world asks for something new (a ride, a free-camera interior, a viewpoint):
    follow `03_camera.md` and `04_character_movement.md`.

## 7. Review, prove, record
16. **Walk it as Sandra and look from above** (`09_review_and_testing.md`), fix, look again; send pictures.
17. **Prove it plays**: the reach check, each mission's last stretches, then the whole play-through.
18. **Paint the map once the layout settles**; record the round (`01` rule 16).

## Unclear or not yet decided (for the user)
- Should a new world keep Sandra (as a new semester somewhere else) or have a new hero?
- Should a new world be generated from a 2D tile map as Barcelona was, or planned directly in 3D from the mock-up?
- Which districts every world must have (a park, a hill, a beach, a wood), and which are optional?
