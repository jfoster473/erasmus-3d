# 09 · Reviewing and testing a world

How to check a world before showing it, and how to prove the game still plays. These are the user's rules for the
review itself (rounds 20–36); the test commands are in `docs/TESTING.md`.

## Look at it as Sandra sees it
1. **Review at her eye level, along her routes.** The camera on a path or pavement at about 1.6 m, looking along it —
   never from under the ground, up in a tree or inside a column. Walk a route, take a picture where the scene changes
   (or every 5 seconds of walking), and read each picture as a critic would. (The user, 20 Oct: "Look at the world the
   way that Sandra looks at the world… Is there anything that sticks out of the image?")
2. **The critic's questions**, for every picture: does anything float, poke through, stand upside down or sit where
   it couldn't (a bush on paving, a station in a field, a tree in the road)? Is it too big, too small, too plain, too
   close, too far? Does a hill drop off at the side? Does the far land go on, or end? Is a door a door? Do two paths
   join as paths do? Do the proportions line up, or are there odd gaps and slivers? Is anywhere bare and lifeless
   ("liminal")?
3. **Then look from above.** Straight-down pictures of the area (the game's own camera, trees hidden if needed) show
   layout, alignment, corners, joins and stray pieces that eye level misses. Sweep every corner and every street end.
   (21 Oct: overview pictures are allowed for layout; round 36: "check that there are no stray weird pieces or random
   squares on the corners".)
4. **Fix, then look again** at the same places before reporting. Name the rule each fix serves.
5. **Before and after**: when something changes, show the same view before and after, side by side, labelled.

## Measure what can be measured
6. **Rules with numbers are measured**, not judged by eye: path smoothness and tilt (`tools/path_rules.py`), slope
   limits (`tools/park_slopes.py`), the hill path (`tools/hill_rules.py`), walls and gaps (`--hillescape`,
   `--seams`, stuck scans), solid objects (`--solidcheck`), object placement (`--placecheck`).
7. **Probe before blaming the game.** When something stops her in a test, run a short key-driven walk at that exact
   spot (`--keyseq`) and read what she touched before changing either the game or the test.

## Proving it plays
8. **The full play-through is the proof**: every mission from a fresh game with the keys, as a player. Do it in this
   order: (1) a no-walking reach check of every person, door, counter and item the missions use; (2) each mission's
   last stretches on their own; (3) the whole run last. After two or three stops in one place, report and ask.
   (Round 32: "You keep running into issues in the park".)
9. **Tests are silent** and use their own save; they never touch the player's save or the speakers.
10. **No long test runs during visual work**: the quick set and the full run only at a round's end, when the user is
    happy (paths: "100% happy"), and only after asking.

## Unclear or not yet decided (for the user)
- Is a picture every 5 seconds of walking the standard for every review, or only for new areas?
- Should every review include a play-through from a fresh game, or only the round's last one?

- **Test photos go on the user's Desktop**, never hidden in a test folder (the user, 30 Oct 2026: "also save any test
  photos on my desktop. I'll just delete them if you hide them away. I miss them"): run the camera's checks without
  `--photodir=`.
