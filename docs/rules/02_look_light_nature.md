# 02 — Look, light, colour and nature

What this file is for: every rule the user has given about how the world looks — the overall style, the light
through the day and night, shadows and flicker, colour, trees, the forest floor, grass and flowers, the beach and
water, the far land and skyline, the small life in the air, and the rule that no place may feel empty ("liminal").
The rules are written so a new city (Valencia, say) can be dressed from them alone; Barcelona appears only as a short
example. Where a rule was changed, the later round wins and the current rule is the one stated. Numbers are the
ones the Barcelona build uses, with the file or constant they live in; treat them as a tested starting point, not a
law, and show the user pictures before changing a look (rule 6).

Sources: `workshop/journal/DECISIONS.md` (by round), `workshop/journal/HISTORY.md`, `workshop/journal/TODO.md`, `docs/PATH_RULES.md`,
`workshop/journal/REVIEW_whole_game.md`, `CLAUDE.md`, the memory notes (forest-floor-look, confirm-before-building,
walk-review), `../ART-DIRECTION.md`, and the code named in each rule. 2D tiles are 3.3 m. Round numbers are
DECISIONS.md's; "HISTORY's round N" means the early rounds counted in `workshop/journal/HISTORY.md` before DECISIONS began
(its 14th–17th rounds are DECISIONS's 17–20).

## Overall style

1. The look is chunky, toy-like and stylised, but warm and romantic: the Reddit video's look (low warm sun,
   light through leaves, dense grass, chunky readable props) made into a stylised romantic city. (HISTORY's round 3–4 and
   the 11 Oct art-direction update; CLAUDE.md "The look".)
2. Follow real life, stylised: a real place's layout, landmarks and plants, simplified and slightly toy-scaled,
   never invented landmarks or features the real place lacks. (Round 27, the user: "It is actually 'Tibidabo
   Funicular', can you follow real life, but stylised"; round 25: three viaducts kept because the real park has
   three; round 27: "The pylons by the terrace removed (not in real life)".)
3. Not "too cosy": the cosy-game references (toon shading, painted clouds, tilt-shift) were tried in writing and
   rejected; the look is lit, detailed models with painted textures, not cel shading. (11 Oct 2026,
   ART-DIRECTION.md update: "the cosy references below came out too cosy".)
4. Lots of plants everywhere — trees, balcony flowers, climbers, planters, undergrowth — so the world feels green
   and lived in. (CLAUDE.md "The look": "Lots of plants"; HISTORY's round 3: geraniums, bougainvillea, planters.)
5. Never a "boxy video game": no plain boxes, nothing floating, flickering, popping in, poking through, upside
   down, or blocking a doorway; every scene judged as "is it lovely or a boxy video game?". (Round 24, the user:
   "is it lovely or a boxy video game?"; CLAUDE.md "They dislike…"; round 27: the boats removed as "weird red and
   blue boxes".)
5a. **No two faces in one plane.** A panel on a box (a fireplace's black opening, a label, a door's glass) stands at
   least 1 cm proud of the face it sits on, never flush with it: flush, the two fight and flicker (round 41, the
   user: "This is flickering inside": the fireplace's opening, interiors.py).
5a2. **No hairlines at a texture's edge**: a ribbon whose picture repeats is mapped short of its picture's edge, and
   that edge is clear, so the filter never blends the far side in (round 41, the user: "a faint yellow line running
   through it. I think it's an artifact of the edge of the ground": the path's frayed verge, `builder/trails.py`).
5b. **Thin things don't shimmer in motion**: temporal smoothing (TAA) on, so balcony railings and other thin bars hold
   steady as the camera moves (round 41, the user: "the railings on the building, funny flicker to them when I cycle
   along… could you do any sort of interlace blur?"). To the user's eye in play: kept unless it smears the leaves or
   leaves trails.
5c. **The picture's quality never jumps on screen at the start** (round 41, the user: "The loading screen now has
   buildings flickering"; measured: the render scale stepped 1.0 → 0.85 → 0.70 → 0.55 in the title's first 6 s, the
   whole city speckled at each step, `workshop/screenshots/round41/flicker/`): the game starts at the scale it settled
   on last time (remembered on the player's computer) and never changes it while the title shows — nor on a ride, a
   bench or through the camera (the user, on the Ferris wheel: "whole clumps of trees are jumping from one bright
   color to one dark color… it may have been the picture quality adjusting"). When it must come down in play, it
   waits for 3 s of slow frames and comes down in one step, not several in a row.
5d. **The upscaler: Apple's own on a Mac, AMD's elsewhere** (round 41, the user chose all three suggestions: "do your
   best for Windows"). On a Mac the lowered picture is scaled up by MetalFX (railings whole and steady, measured);
   elsewhere by AMD's FSR 2 — both smooth by themselves, so the separate smoothing (5b) is off with them. Not
   checkable here on Windows: what is seen there is the user's to judge.
5e. **Far railings are a flat picture** (round 41, the user: "swap the railings on far buildings for a flat picture of
   them"): balcony railings beyond a distance are drawn as a flat picture of themselves in the railing's plane, which
   the graphics card can blur smoothly, instead of thin bars that break up; near ones stay real bars. The swap must
   not be seen as a pop.
5f. **Speed, the user's picks** (round 41, the user: "Both options 1 and 2 please", after before-and-after pictures,
   `workshop/screenshots/round41/speed_options/`): (1) what is wholly hidden behind the city's blocks is not drawn
   (two solid boxes inside each block's walls; Sandra's block left out for its garden passage) — nothing seen changes,
   La Rambla ~19% faster. **The boxes go only where she can never be**: only blocks that are wall all through; a
   block she can go into — a landmark on its own square (the MNAC, the Sagrada Família), a park (the Ciutadella), a
   courtyard — gets none (round 41c, the user: "none of the scenery is there anymore", on the MNAC's terrace and then
   in the Ciutadella, and the MNAC's door didn't glow: the camera was inside the box, the glow behind its face); (2) no soft shade (SSAO) out of doors — corners a touch lighter, ~10–15% faster. Rooms keep
   theirs (#24 "ambient occlusion for soft shadows under furniture"). Not taken: the half-size shadow map.
6. Ask before changing a look: show options as game pictures from the same angle and wait for an explicit pick
   ("give me E" means show E, not build it); bug fixes need no pick. (Round 20, the user: "I didn't ask for
   anything. I am asking for options. Please confirm with me first"; memory confirm-before-building.)
7. "Magical" means deeper scenery, not gimmicks: be subtle, nothing overdone, nothing added that nobody asked for;
   suggest when unsure. (Round 25, after round 24's unasked sunbeams, glowing mushrooms, coloured butterflies,
   lanterns and "Stop and look at the view" were all cut or toned down.)
8. Everything added must be tasteful and balanced with what is around it; a review fixes things that look "wrong
   or jilted… sticking out or a poor balance based on what is around it" by moving or changing them, not by adding
   new things. (Round 27, the user: "Everything added should be tasteful"; round 35, the user's words quoted.)
9. Textures stay crisp close to: a fine grain over stucco, stone and Meshy textures so walls don't look blurry; no
   "smashed up" low-detail models (windows are a crisp picture, `kit.py` `WIN_STYLE = 'picture'`). (HISTORY's round 10:
   `add_grain()` in `engine/main.gd`; round 24, the user: high windows "smashed up"; round 25: picture windows
   picked, "Remove the rollershutters you add everywhere".)
10. No visible repetition or regular patterns: textures must not tile visibly, fall into rows, stripes or a grid of
    little squares; irregular "as long as the user doesn't notice". (Round 25, the user: path edges "too regular,
    there are regular boxes, it should be less regular, as long as the user doesn't notice it"; round 29: far hills
    read as striped fields; round 35: grass "zigzaggy".)
11. Details fade in and out gently with distance, never pop: each kind of small thing has a visible range and a
    14 m fade (`FAR_RANGES`, `FAR_FADE` in `engine/main.gd`, e.g. grass tufts to 55 m, undergrowth to 95 m, full
    trees to about 105 m, far tree tops beyond 95 m). (Round 17 (HISTORY's 14th): "Buildings no longer load as you approach";
    CLAUDE.md: the user notices pop-in.)
12. Small toy-like touches that read as the town's style may stay even if not strictly real (example: a bridge
    parapet's spaced, overhanging coping stones). (Round 32: "the parapet's spaced coping stones (the toy look)"
    walked and left alone.)
13. Saturation and contrast are lifted slightly over the whole image, with a filmic tone curve and gentle bloom
    (`engine/main.gd`: filmic, white 6.0, saturation 1.12, contrast 1.05, glow 0.6, bloom 0.08; indoors
    saturation 1.08). (HISTORY's round 3: "A filmic tone curve and a slight saturation boost finish the image.")

## Light through the day

14. The light follows the game clock, blended smoothly minute by minute through set looks: night until 06:00,
    red (orange) at sunrise 06:30, golden 07:00, day from 09:00 to 19:00, golden 21:00, red at sunset 21:30, night
    from 22:00 (`LOOK_KEYS`, `PRESETS` in `engine/main.gd`). Sunrise and sunset take about an hour each, with no
    cut. (HISTORY's round 12 and round 18 (15th in HISTORY): "Sunrise and sunset take an hour each".)
15. Time runs at half the 2D game's speed: a game minute every 2 real seconds (`CLOCK_RATE` 0.5 in
    `engine/game.gd`); a new game starts at 06:40, just after sunrise. (Round 23: "Time half speed"; round 21:
    "New games start at 06:40".)
16. The sun and moon move across the sky by the clock in their real directions: the sun rises east-north-east,
    stands south at 14:00 and sets west-north-west; the full moon rises in the east as the sun sets
    (`sky_positions()` in `engine/main.gd`). (Round 18. Conflict: the user once wrote "rises in the west"; kept east
    because it matches the real city — see "Unclear" Q1.)
17. Midday is toned down so pale stucco and stone never glare; no glaring whites anywhere, including windows by
    day (`PRESETS.day`: sun energy 1.7, exposure 0.9). (HISTORY's round 10, the user: midday too bright, whites glaring, the
    flat's windows glaring; CLAUDE.md: "never glaring whites".)
18. Shade is warm and lifted, not dark blue: shaded street about two-thirds as bright as sunlit street, warm grey
    (`fill`, `sky_mix` in the presets; a warm orange fill like sunlight bounced off façades). (HISTORY's round 4: "a soft
    orange fill light"; HISTORY's round 7: "Shaded street is now about two-thirds as bright… warm grey rather than dark
    blue".)
19. The golden hour is the default mood: the sun low and warm. (HISTORY's round 3: "The sun is low and warm"; the start time
    and the golden preset.)
20. Sunrise and sunset are orange and gold, never magenta: the sky runs warm horizon → creamy band → clear, slightly
    cyan blue; keep the warm horizon band. (Round 19 (16th in HISTORY): "the sunset is orange and gold, not
    magenta"; "The user likes the warm horizon band: keep it".)
21. At sunrise and sunset only the sun's own side of the horizon glows; the opposite side is a soft hazy blue.
    (Round 20e, the user's wish; `night_sky.gdshader` `sunward`.)
22. **Looking towards the sun brightens the sky, and only the sky**: round the sun a soft core, a broad halo and an even
    lift over the rest of the sky, strongest straight at it, gone when a building or hill hides it; no ball, no
    lens-flare rings; gentler and wider near the horizon. The sky comes out exactly as the old screen-wide veil made it
    look, but the trees, buildings, people and ground in front keep their own light and colour — only the sky seen
    between the leaves and past the rooftops shines. (Round 19 sun glare; round 20: "no explosion in the middle";
    round 23: "a screen-wide glare"; **changed** in round 38, the user: it "changes the brightness of all the
    objects… Make it so that only the sky gets really bright"; of the examples, "Before whole picture is good, but…
    the sky should look the same… It's just that you don't have the high saturation on all of the objects"; they
    picked option E, `workshop/screenshots/round38/glare2_spot0.jpg`; `night_sky.gdshader`, `update_glare()`.)
23. Distance haze only far away: the near city is clear (haze across the city read as pollution); fog begins at
    110 m and is full at 900 m (`fog_depth_begin`/`fog_depth_end` in `engine/main.gd`). (ART-DIRECTION.md: "The
    haze across the city, which read as pollution, is fixed"; round 26: fog to 900 m for the far country.)
24. Indoors there is no sun-like light: soft ambient, a ceiling light, daylight from the windows and lamps, none
    casting hard shadows; ambient occlusion for soft shadows under furniture; homes warm and a little dim.
    (HISTORY's round 2; HISTORY's round 4: "The flat: warmer and a little dimmer".)
25. Sacred rooms (churches) are the exception: haze, bloom, a lower exposure, coloured sunbeams through stained
    glass that follow the clock — cool glass on one side, warm on the other, gold at the altar end. (Round 17 (HISTORY's 14th)/17,
    the Sagrada Família; `light_beam.gdshader`, `update_sun_beams()`.)
26. Volumetric light shafts are a high-quality extra only (the single biggest cost); never add shafts as scenery
    in glades. (HISTORY's round 3: shafts only in the full look; round 25: "Removed: the glades' light shafts".)

## Night

27. Night is a full-moon night: dark, but everything can still be seen; warm and romantic, never harsh blue; an
    even cool fill so nothing drops into black. (HISTORY's round 6: "a full-moon night"; memory: "Night must feel like a full
    moon: dark but everything visible, warm and romantic"; CLAUDE.md: "never… harsh night blues".)
28. The night sky is plain dark blue with stars; no glowing band, purple blur or city glow along the horizon; don't
    darken it further without asking. (Round 20e, the user: "remove the purple blur… it should just be dark blue";
    option D of four picked.)
29. The moon is a pale disc with grey seas, not a yellow fuzzy ball or blazing light; stars come out as the last red
    goes. (Round 17 (HISTORY's 14th): "The moon is a pale disc with grey seas rather than a blazing light"; `night_sky.gdshader`.)
30. Lamps, lit windows and stars come in gradually as the light goes, never switched at once (`nk`, the night
    amount, in the presets). (Round 18.)
31. Street lamps are soft and warm, and light comes from the lantern's own glass (no glowing ball hung under it);
    pools of light join up (OmniLight energy 1.35, range 20 m, `engine/main.gd` `lamp_glass()`). (HISTORY's round 10: lamps
    "softer"; round 20e, the user: the ball "looks wrong close up".)
32. Few windows are lit at night, and softly, so no one can see into the rooms. (HISTORY's round 10, the user: "almost see
    into the apartment".)
33. Nothing glows by itself at night unless it would in life (no glowing mushrooms, no bright dog). (Round 23: the
    dog "too bright at night" — its Meshy glow texture turned off; round 25: the mushrooms' night glow removed.)
33a. **The Ferris wheel has no lights of its own**: dark at night against the lit plaza (round 41: rings of bulbs were
    tried, then a big light at its hub; the user, after pictures from the city with it on and off: "I think we will take
    the light off").
33b. **The funfair's plaza at night** (round 41, the user: "put some lamp poles up on the amusement park plaza in tasteful
    locations… lights, like fairy lights, hanging from a chain somewhere. Could you mock up something to show me?"; then
    "Could the fairy lights be put around the edges? Just slightly in from the fences? And then have the lamps… 3 sort
    of in the middle, then 2 on the edges a bit back… Place it where you think it's balanced and not too close to other
    things, but where it gives enough light that it all adds up. And there aren't any incredibly dark bits"):
    - **Fairy lights round the edges**, about a metre in from the railings, on thin posts, the chain sagging from post to
      post well over head height, small warm bulbs, each span giving a little soft light of its own after dark; over the
      hill path's way in; broken only where a building stands at the edge (the funicular station, the church, the museum).
    - **Five of the city's street lamps**: three through the middle (between the wheel and the churros kiosk, on the
      church door's line, beside the tall swing ride) and two at the sides set back (the west by the carousel, the east
      by the museum's bench); each clear of the rides' swing, the benches and the kiosks.
    - Checked from above at night: no patch left really dark.

34. Fireflies at night only where butterflies are by day (rule 105). (Round 25.)

## Shadows and flicker

35. Shadows are soft and not too dark: day opacity 0.8, sun size 0.4°, blur 3.0; at night 75% of the day's
    (`SHADOW_OPACITY`, `SUN_SIZE`, `SHADOW_BLUR` in `engine/main.gd`). Keep the sun's size small — at 1.6° the
    trees' dappled crown shadows smeared away. (Round 21, the user: "not as dark, edges somewhat fuzzy"; option B
    picked after comparing in town and in the wood.)
36. Dappled leaf shadows are a key beauty: every tree casts them, at every distance (no limit round Sandra:
    `LEAF_SHADOW_R` 0.0). (HISTORY's round 3: trees "cast dappled shadows"; round 25, the user: "Keep the leaf shadows as they
    are".)
36a. No edge where the shadows end: they reach far (85 m on the balanced setting, 100 m on high) and fade out over
    their last 45%, so no line slides along the ground with her; the fine shadow map near her still reaches past her
    (13.6 m balanced, 6 m high; round 26's flicker fix). (Round 37, the user: "shadow line that moves when she moves (see clearly on the
    bike)"; it had stopped 45 m ahead, fading over 11 m.)
37. Shadows glide with the sun, never jump: the sun is re-aimed every second frame (`SUN_EVERY` 2, the user's wish);
    the sky's own sun disc stays steady. (Round 22, the user: shadows "move with discrete jumps"; round 22b: sun
    every 2nd frame; round 26: `SKY_STEADY`.)
38. The moon casts faint soft shadows: 0.55 of the day's darkness, 1.2° soft, blur 4.5, aimed from at least 55° up
    so buildings don't plunge whole streets into shade (`MOON_SHADOW`, `MOON_SOFT`, `MOON_BLUR`). (Reversed: round 20
    "Moon: no shadows"; round 22 turned them on. Current: on, faint.)
39. Nothing may flicker: the leaves sway but their shadows hold still (`foliage.gdshader` `shadow_motion` 0); thin
    things (rope railings) cast no shadow; the render scale must not see-saw; no two faces flush at the same depth.
    (Round 26, the user: "the dappled light in the forest flickers from one moment to the next"; rounds 8 and 21:
    flush faces flickered; measured with `--flickermeter`.)
    Clothes, washing and towels too: no colour may sit on a threshold that flips as the camera moves (round 38, the
    user: the towels on the balconies and the boys' patterned shirts "flicker when you move"; a shirt half-recoloured
    shimmered — the whole shirt is recoloured now, `npcs.gd swaps_for`).
    A thing's near and far versions match in brightness and colour, so the cross-fade between them never shows: the
    far trees cast no shadow and came out ~17% brighter and yellower than the self-shaded near crowns, and on the
    Ferris wheel whole clumps in the swap band jumped "from one bright color to one dark color" from frame to frame
    (round 41, the user; measured with `--framerec=…,wheel` `--hide=`; the far leaves toned down, `foliage.gdshader`
    `tone`).
40. Tiny, flat or far things cast no shadow (window pictures, plaques, sign text, grass tufts, undergrowth chunks,
    far tree tops, ground layers) (`NO_SHADOW_PREFIX`, `NO_SHADOW` in `engine/main.gd`). (Rounds 10–26, frame rate
    and flicker.)

## Colour and materials

41. Colours are warm and natural, never neutral grey or harsh: sun-bleached ochre and cream façades, green
    shutters, terracotta, warm grey paving, plane-tree greens, bougainvillea magenta, Mediterranean blue.
    (ART-DIRECTION.md palette, still applying after the 11 Oct update: "The palette, foliage and lived-in-street
    points below still apply".)
42. Greens are natural, not acid or yellowed; in a dry Mediterranean garden they are toned down to about 60%
    saturation, same hue (Park Güell: `world2d.park_tone` sat 0.6; floor shader `sat` 0.6). (Round 34, the user:
    "tone down the saturation of the green. It doesn't need to be yellow".)
43. One bark colour per tree, trunk and branches alike (trees may differ from each other); a trunk looking two-toned
    at midday is light, not paint. (Round 20d; memory forest-floor-look: "one bark per tree".)
44. Sand colour only on paths and paved places, never as patches or squares on grass; a bank too steep to climb
    wears the middle wood-floor look, not bare sand. (PATH_RULES C1, C2; round 35b. Reversed: round 28 painted
    steep park banks bare sauló; dropped because it made sand squares. Current: C1/C2.)
45. Ground materials meet without square seams: lawn, forest floor and sand blend by a light map with noisy,
    ragged edges, never tile squares. (Round 20: "No square tile edges between floor, lawn and sand"; memory
    forest-floor-look.) Where an open lawn (a meadow, a park) meets a beach it runs into the sand the same way as the
    wood's floor beside it, so the line from lawn to sand is one continuous ragged edge with no step or corner where
    the wood begins. (Round 37, the user: "The grass at the beach has a square at the start of the forest… The grass
    should appear to be continuous." The meadow's last row of lawn by the sand is drawn with the wood's floor
    material: `forest.py meadow_shore()`.)
    A boulder or rock has no tile of its own: the ground round it is whatever is round it (round 38, the user: "The
    boulder in the forest… is on a square green tile. Its ground should match whatever is around it").
45a. **Rocks and boulders are stone-coloured** (warm brown-grey), never green. (Round 38, the user: "The boulder in the
    forest is green when it should be brown.")
46. Stone and brick textures follow the user's picks per building; a plain wall reads as unfinished (example: the
    hill church — brown blocks for the crypt base, pale white stone above). (Round 26, the user: "Put some textures
    on the church… it looks very plain"; "B for brown bricks and C for white. Base is brown bricks.")
47. Things that are one material must look one piece: curved stone (arches, drums) as smooth bands with even
    world-scale texture, never stepped cubes or a stretched, smeared texture. (Round 29: the lodges' smeared
    corners; round 35: arches of "13 square stones in a staircase".)

## Trees: kinds, shape and placing

48. Use the region's own trees. Barcelona's set (`forest.py` `SPECIES`): holm oak, Aleppo pine, stone (umbrella)
    pine, cork oak, cypress, olive, carob; plane trees in the streets; palms on the beach; for a new city choose its
    native and street trees the same way. (Round 15 (HISTORY "the forest, redone as a Mediterranean wood").)
49. Mix by zone: the wood's edge mostly olive, stone pine, carob, cypress and holm (`FRINGE_MIX` 3/2.5/2/1.5/1.5);
    the thick wood mostly holm oak, then Aleppo pine, cork, stone pine, a rare cypress (`WOOD_MIX`
    5.5/2.2/1.6/1.3/0.3). (Round 18 (HISTORY's 15th).)
50. Crowns are round and full, made of painted leaf cards that sway gently in the breeze and glow when backlit
    (`foliage.gdshader`: sway starts at 2.8 m, amplitude 0.12). Only a gentle breeze. (HISTORY's round 3; HISTORY's round 4: "round,
    fuller crowns, with only a gentle breeze".)
51. Trees are scaled to the toy city: branching at about 3 m (street lamps 3.75 m). (HISTORY's round 2.)
52. Simple trunks: 6 sides, branches 4, no hidden end caps; deep in a wood no twigs thinner than 10 cm (`forest.py`
    `TRUNK`, `TWIG_DEEP`). (Round 25, the user saw `round25/trunks.png`: B "looks the same".)
53. Every tree is made twice: a full version near, and far away only its bushy top (no trunk, about every fifth
    leaf card, each bigger), swapped in beyond about 100 m (`Both` in `forest.py`). Trees out of reach past a wood's
    edge rise are only tops on bare trunks, with enough smaller cards that no "green tent" floats. (Round 25, the
    user: far away "you don't need branches and stems, really just the bushy green tree tops"; round 26: smaller
    cards.)
54. The broad-crowned trees stand back from paths; only tall narrow ones (pines, cypresses) close beside a path, so
    no crown hangs at head height over the walk (wood: cypress/cork/carob replaced by holm within 0.7 tiles of a
    path; park: pines and cypresses from 2.2 m, others from 3.2 m). (Round 33: "an olive's or holm oak's crown hung at
    her head over the path"; PATH_RULES A5.)
55. Trees keep back from glades and path crossings so the sun gets in (0.9 tiles from glades, 0.85 from crossings,
    `forest.py`). (Round 20.)
56. Street trees stand in tree pits on pavements wide enough for them, clear of walls, their crowns never in a
    building; lamps at least 3 m from any tree, never under a crown. (CLAUDE.md "Everything sits where it would";
    round 26: Larrard's plane trees "used to pierce the walls"; round 36, the user: "the streetlights and the trees
    are too close together", PATH_RULES H6.8.)
57. Palms are scattered off their grid by random amounts, never in a straight row, and near the grass where the
    beach meets a wood. (Round 23, the user: "move the palm trees closer to the grass and don't have them in such a
    straight row"; `world2d.py` palm_rng.)
58. A few lone park trees in a meadow by the road give a park feel (Barcelona: seven, stone pine/olive/carob).
    (Round 19 (16th in HISTORY): "A few more trees stand in the meadow by the road, like a park".)
59. Lookouts keep their trees but low ones (holm, olive, cork at half size) so you peek over them; no big clearing
    below a viewpoint, and no tree in front of a bench's view. (Round 25, the user: "The look out points should not
    have big clearings below, the trees should simply be lower to allow Sandra to peek through"; REVIEW §10.)
60. A city park has trees (Barcelona's Ciutadella should; it currently plants none — see "Unclear" Q2). (Round 32b
    open item.)

## Woods: structure and density

61. A wood goes, from the town outwards: a meadow of grass in tufts and drifts with wild flowers and very few trees;
    a walkable fringe of scattered trees with grass under them; then the thick wood. (Round 18 (HISTORY's 15th): "From the road
    outwards: a meadow… then the wood's edge… then the thick wood".)
62. Tree spacing by zone, Barcelona's eastern wood (`forest.py` `plant_forest`, tiles of 3.3 m): meadow about 15 m
    apart (4.5 tiles); fringe about 7 m (2.2); edge band about 3.8 m (1.15); thick wood about 2.4 m (0.72); thinning
    to about 5 m (1.6) towards a beach. Hill wood about one tree every 2.9 m; a park's wood on a 2.2 m grid with 92%
    kept, its open lawns 18% (a few fine trees). (Rounds 15, 24, 33, 34.)
63. A wood feels like going in: beside the paths the trees arch over. (Round 17 (HISTORY's 14th): "beside the paths the trees arch
    over, so it feels like going in"; round 24: "Magical path to the forest?")
64. A hill wood is deep, and here and there you see through it and over treetops to the city and the sea.
    (Round 24, the user: "The forest up the hill should be deep. At parts you should be able to see through and then
    over some trees to see the city and beach".)
65. A wood is walkable anywhere between trunks; every trunk is solid; no invisible walls in a wood; pushed at a gap
    for 3 s she slips through. (Round 20: "The wood can be walked anywhere"; round 23: "Forest edge: an unclimbable
    slope, not an invisible wall".) (Round 39: thick bushes too, the park's steep-bit bushes included — the user: "Isn't brush walkable
    anyway?"; only trunks are solid, and a trunk lets her through after 3 s of pushing, 04 #74.)
66. Lamps only at each way into a wood, none inside it. (Round 18 (HISTORY's 15th): "a street lamp at each entrance (none inside the
    wood)".)
67. The edges of a world are thick wood (or rising wooded ground), never bare ground and invisible walls; a wood's
    edge rise is only as high as needed to stop her (Barcelona east: at most 3 m, `EAST_RISE_MAX`) so the wood seems
    to go on. (Round 27: "World edges: thick forest at the unwalkable edges, not bare invisible walls"; round 25.)
68. Planting never on the wrong ground: no bushes on pavements or paving, nothing on a railway bed, nothing on a
    path's walking width, nothing in front of a door. (Round 26, the user: "Bushes don't sit on the pavement";
    round 30: bushes on the ballast; round 21: doors "behind plants"; PATH_RULES A5.)

## Undergrowth

69. Undergrowth is thick in the wood, with a dense band along the fringe that hides where it can't be walked; low
    and sparse beside paths so they stay open; a little low green at path corners (`forest.py`: shrub chance about
    0.8–0.95 a half tile deep in, 0.35 beside paths, 0.1 at junctions). Shrubs: lentisk, rosemary, broom, strawberry
    tree. (Round 18 (HISTORY's 15th).)
70. On a hill path the undergrowth is thicker, shrubs about every 1.7 m, on the banks too, ferns and grass tufts
    within 30 m of the path; never a crown over the path. (Round 25: "Thicker undergrowth"; PATH_RULES A5.)
71. In a park's wood both edges of every path are planted thick — low plants at the edge, behind them shoulder-high
    shrubs — so the paths run between banks of green; beside an open lawn a looser edge. (Round 34, the user: "It is
    slightly more dryer with the paths quite closed in with plants. Look at the actual pictures"; round 25: "it feels
    very sparse"; PATH_RULES F4.)
72. Where a path comes down to meet a pavement, its foot is open grass, not foliage. (Round 30, the user: "the path up
    the hill should not have foliage at the bottom, but instead connect to the [street]".)
73. A short steep bit that must stop her can be closed by a thick shrub rather than an unseen wall. (Round 35b,
    PATH_RULES G1.)

## Forest floor

74. A wood's floor follows the sunlight: trace the sun's path through a day (and the open sky) through every crown
    and bush; light = 0.6 sun + 0.4 sky (`SUN_SHARE`); it must be computed, not guessed from tree counts. Do this for
    every wood (the hill and park woods too). (Round 20, the user's rule: "where the sun falls for most of the day it
    is green, shade all day brown, a mix between"; round 25, the user: "Did you do the sunlight thing to check where
    the ground of the hill forest should have the darker shades?")
75. Three steps by the light: lawn where light is high (`GREEN_AT` 0.3–0.6); in half shade small round clumps of
    lawn among the needles, about half each and a shade darker (`MID_AT` 0.05–0.12, the user's "option F"); golden
    needles, russet leaves, dry grass and earth only in the deepest shade, so the crowns show in the floor. (Round
    20d, the user: "it is just the part where the light doesn't reach, part grass and part needles"; moss, a flat
    olive and a patchy verge were turned down.)
76. The shaded floor is a magical wood's, never a dark or muddy brown: mossy and greenish with golden needles; let
    the trees' own shadows do the darkening. (Round 20c, the user: round 19's brown "yucky", wants "a magical
    forest… more green"; a 14% darker brown looked like "a pile of mud".)
77. Glades and path crossings are lawn (the anchor); trees on a sunny beach side stand on grass; the floor runs
    softly into sand near a beach, sandy there and drier/greener further in. (Round 20; round 19 (16th in HISTORY).)
78. Each step has its own ragged noise edge, never a smooth fade or a square; the litter is blended at two sizes so
    it doesn't repeat (`forest_floor.gdshader`). (Round 20/20c; memory: "patchy edges, not smooth fades".)
    Ragged wherever the edge falls: on hills, along banks and verges and at a light map's edge too, never a straight
    line (round 38, the user: "The intermediate texture for the forest floor ends as a straight line on the hills.
    Could you make it a bit more varying?").
79. Some places stay green whatever the light: a path's walkable green verge, glades, lookouts. (Round 25, the hill.)
80. A dry Mediterranean garden is drier than a wild wood: lawn only in the brightest openings, less half-shade grass,
    needles and leaves over most of its wood floor (Park Güell steps (0.9, 0.995)/(0.5, 0.75) in
    `north_build.py`); lawn kept within 3 m of open lawns so they meet without a seam. (Round 34, the user: "It is
    slightly more dryer". Conflict with rule 76's "more green": this is a place-by-place exception — see "Unclear"
    Q4.)
81. A thing meant to be found in deep wood lies where the floor is dark by the light map, with enough trees round it
    to keep it so, looking fallen not placed, and not hidden by ferns (no ferns within 2.2 m, no shrubs within 2.6 m).
    (Round 25, the user on the ball: "ensure the ball is in a deep part of the forest where the floor is dark… It
    shouldn't look placed, but should not be hidden by ferns".)

## Grass, tufts and flowers
- (Round 40, the user: "that entire hill should have foliage right along it… Currently, the ground is blank"; "Have
  some grass on the hill to the north of the city… Just a little bit of grass to break it up. The grasses that you had
  in the forest"; "bring the forest and foliage a bit lower to the funicular station") the hill's wood has shrubs and a
  fern or tuft under them everywhere, not only within sight of the path (sparser far from it); the open hill far from
  the path a scattering of the wood's tufts, patchy; the wood comes down to the funicular station's back corners.
- (Round 40) The hill between the funicular and Park Güell (plan `round40/r4/plan_forest_wall.jpg`, corrected by the user):
  no wall; along the line `north.WOOD_EDGE` — from the funicular's fence east 16 m above the pavement, curving up halfway
  to Gràcia's buildings, past their north-west corner, on to the park's wall — the hill's foot below it rises gently
  (0.2 a metre) so she can wander a little way into the wood, and above it a steep bank to a hill she can't climb
  ("this whole area should be a steeper hill that she can't walk up. The stone wall is not necessary").
  (Round 41, the user, on the plan `round41/hill_proposal.png`: "Make the unwalkable hill to the west of the Guell Park
  30 meters further up the hill… so that it joins with the wall to the park and the steeper hill further to the west.
  Also make it look more like a steeper hill. Also add foliage to the ground there"): above the town's top-left corner
  the line runs on up its west side and then straight across at z −192 to the park's wall; below it a gentle lawn she
  walks on, its trees solid, tufts, ferns and the odd shrub over it (none against the wall's foot); above it a hillside
  rising 0.8 a metre for 8 m, then on up, held by the park's wall to 1.6 m over the park's ground.
- (Round 40) The river no longer ends against the hill: it runs on west along the hill's foot, south of the wood, off
  the map's edge (`world2d RIVER_EXT`); its east bank, the grass strip between it and the city, has a few big pines
  and holm oaks here and there and scattered tufts ("just add some bigger trees there and some tufts of grass").

82. Grass grows in drifts and patches, not evenly: a slow wobble of more and less, thicker along path edges (×1.7),
    never on paths (`forest.py` `drift()`). (Round 18 (HISTORY's 15th): "a meadow of grass in tufts and drifts".)
83. Not too much: open meadow tufts at a chance of 0.26·drift² per 0.4 m cell, park lawns 0.16. (Reversed: round 28,
    the user: "less grass in the field" — meadow 0.42 → 0.26, park lawn 0.45 → 0.16. Current: the lower numbers.)
84. Blank grass next to nature is never left bare: tufts and the odd fern, thickest within about 6.5 m of a wood
    (chance 0.5), thinning across clearings (0.13), and patchy (×0.55–1.0); on a 2.6 m grid (`north_build.py`
    open-grass pass). (Round 30, the user: "Add bits of foliage or grass leafs on any blank grass that is next to
    nature, some is more sparse than others".)
85. The grass inside a path's bends (hairpin crooks) always gets its tussocks (patchiness floored at 0.75). (Round
    31, the user: "still plain grass up the hill at the turns. Looks very liminal".)
86. A meadow on the far side of town gets the same treatment as the near one: thick by the pavement and river banks
    (×1.9), sparse across the far field (×0.55). (Round 32: the west meadow "bare lawn from footpath to hills".)
87. The lawn texture is seamless noise at several sizes, gently swirled, wrapping at its edges; the same mean colour;
    no zigzags or visible repeat (`kit.py` `lawn_pixels`, a 512 px tile). (Round 35, the user: "The grass is
    zigzaggy… It should be a texture that does not appear to evidently repeat anything within it. So random, but
    matching the borders".)
88. Ground plants stand upright on the real ground height, never upside down or floating (`upright()`,
    `ground_z()`). (Round 20d: tufts and flowers "were upside down".)
89. Meadow wild flowers are small, only to look at: white, yellow, lilac and a few poppies, scattered rarely (about
    0.012 chance a cell). (Round 18 (HISTORY's 15th).)
90. In the shade: ferns in drifts (where the light map's green is under 0.45), little white and lilac/blue woodland
    flowers here and there; never on paths or in glades. (Round 20c: "ferns grow in the shade… white and blue
    woodland flowers".)
91. Pickable flowers for a mission: one stem each, exactly the number the mission needs, at random places along the
    route on the grass beside the path (never by a bench or in a glade), with other green things here and there so
    they don't look out of place, easy to spot, not behind trees. (Round 25: "Wildflowers one stem each"; round 26,
    the user: "There should only be 5 (the number for the mission)"; round 24: "beside it, not on it, not behind
    trees, easy to spot".)
92. Balconies and corners carry plants from each house's own list (geraniums, daisies, herbs, trailing ivy,
    bougainvillea, a lemon tree, or nothing); corner bougainvillea stays on its corner and never covers shop names,
    awnings or plaques, and none on a corner whose door is on the chamfer. (HISTORY's round 6; round 21; round 35: it "spread…
    wrapping round onto both fronts over shop names".)
93. A formal garden's flower beds are full and solid, joined by gravel walks; hedges soft and leafy, laid on the
    ground in short lengths, never boxes floating over the lawn. (Round 17 (HISTORY's 14th): "The park's hedges are soft and leafy,
    not boxes"; round 28: hedges "floating"; round 33: 110 flowers a bed, PATH_RULES F6.)
94. Worn grass (a little-used way) is paler, thinner grass with earth just showing, in patches with whole lawn
    between, edges fading — not a dirt track. (Round 35b, the user: "a part of the grass that gets walked over, but
    not too often, so it gets worn down without making a big trail… a bit more patchy instead"; PATH_RULES F11.)
95. Dirt is worn grass: a dirt path stops at paving or gravel, never lies on it. (Round 31, the user: "The dirt path
    never goes ONTO the road. It stops at it. Think about how dirt works, it is under grass".)
96. A town may keep a plain mown verge between a pavement and a wood; that is not "empty". (Round 32: "the mown verge
    between the north pavement and the hill wood (a town keeps such a strip)" walked and left.)

## Mushrooms

97. Only the few pickable mushrooms are red (orange-red, the ou de reig, since round 38); all decorative ones are brown or white. (Round 27, the user: only the
    pickable mushrooms are red; round 22: three red ones.)
    The pickable mushroom is named after the real local kind it looks like (round 38, the user: "it should be called
    whatever is a mushroom that looks similar to that and grows in Spain"); the rule is for this mushroom, not for
    every thing she picks up. Barcelona's is the **ou de reig** (Caesar's mushroom, Amanita caesarea): an orange-red cap
    with no spots, yellow gills and stem, rising from a white cup; prized, good to eat (round 38, the user: "Make it the
    ou de reig: orange-red, no spots, good to eat"; it was a white-spotted fly agaric, "never to eat").
98. Pickable red mushrooms are hidden deep in the wood, off the paths, where the user placed them (**changed** in round
    38 from "at least 75 m apart": the user moved the first and third to the wood's east half, `game.RED_MUSHROOMS`).
    (Round 22: 11–16 m off the paths, every sight line from a path within 30 m crossing a trunk.)
99. Decorative mushrooms are sparse: brown ones in ones and twos in the shade (halved in round 36), and small white
    round-topped clumps of 2–3 by the trunks, off the paths (38 clumps — **changed** in round 38 from 150, the user:
    "There should be a quarter as many"; `touches.gd` `SHROOM_CLUMPS`, fading at
    40 m). (Round 22: the user first said white common and pickable, then "white only to look at"; round 36, the
    user: "too many brown mushrooms".)

## Life in the air and on the ground

100. Wildlife only where the place would have it, and sparse; no gimmicks. (Round 25 lesson; rule 7.)
101. Pigeons on the main promenade (nine on La Rambla) that clatter up when she comes close and settle again.
     (HISTORY's round 13; `engine/wildlife.gd`.)
102. Gulls over the beach (six, wheeling in long ellipses). (HISTORY's round 13.)
103. Butterflies are proper butterflies (wings, body, feelers), never paper squares. (Round 20 (17th in HISTORY):
     "The butterflies are proper butterflies… not paper squares".)
104. Butterflies only along the woods' paths, a few in each: one white one at the mission's glade, three along the
     wood's main path, three along the hill path; white, yellow (brimstone) and blue; none in town or on the beach.
     (Round 25, the user: "Keep the white butterfly near the dog; otherwise they should be white, yellow and blue.
     Make the butterflies sparse, only a few in each forest along the paths". Reversed: round 24's coloured
     butterflies by every flower, bench and park.)
105. Fireflies at night at the butterflies' spots, three to each, small and soft, glowing on and off. (Round 25:
     "fireflies (smaller, softer)".)
106. Pollen: a few faint warm motes drifting in the glade she is in, by day only (26 motes, `touches.gd`).
     (Reversed: round 24 had 70 and light shafts; round 25, the user: "keep … but make it subtle". Current: 26,
     faint, no shafts.)
107. A few animals to look at, as the old game had (Barcelona: three cats — one asleep on the beach, one in a city
     park, one up the hill). (Round 20; round 35: the black cat moved out of a courtyard onto the park lawn.)
108. People sitting, walking and strolling at the beach and parks make places feel alive; no crowds. (Round 26: "a
     stroller at the water's edge", park strollers; round 36: a seated café customer; REVIEW §3: "no crowds".)

108a. Far hills grow out of the land: a far hill's rim comes down into the land under it, never hanging above it.
     (Round 37, the user: "hills appear to float"; `world2d.py hill_mesh(seat=True)`.)

## Beach, sea and river

109. The waterline is a smooth curve following the line of foam, never square tiles; the sand slopes on under the
     water from that curve. (Round 23, the user: "the beach is too square where the water meets the sand… it should
     be smooth, matching the white line of whitewash".)
110. Foam runs only along sand, starting where the sand starts; never a white line over open water or a river's
     mouth. (Round 36, the user: "a white line ran out over the river's mouth".)
111. The sea is a gentle rippling water with a line of foam coming and going (`sea.gdshader`, `foam.gdshader`).
     (HISTORY's round 10.)
112. A beach runs on straight at its far end and is closed by a rock breakwater of big boulders crossing it from the
     wood's edge out to sea, as on the real coast; no invented cove or cliffs. (Reversed: round 24 built a cove,
     headland and low cliffs; round 25, the user: "The whole thing looks bad. Just add a small rock break wall, like
     the actual Barcelona, going out into the ocean". Current: the breakwater.)
113. Groynes (breakwaters) cut out into the sea from the beach with lots of space between them, as on the real
     beach (Barcelona: three at tiles x 11, 45, 76.8, `world2d.ESPIGONS`, plus the big east one). (Round 27, the
     user: "have lots of space between them like the real barcelona beach"; round 36, the user's marks.) Every stone of
     a breakwater sits on the ground or seabed under it, sunk a little into it, never floating, and the stones are packed
     so that no daylight shows through the pile. (Round 37, the user: "rocks appear to float, There shouldnt be gaps
     through it"; `world2d.py`: each stone seated by `ground_z`.)
114. A beach is never empty sand: parasols in loose groups as bathers group (eleven, thinning towards the far end),
     towels lying on the sand under them and alone nearer the water, a volleyball net with its posts at its ends.
     (Round 26, the user: "make the world complete"; round 35: the net "floated between posts 10 m apart".)
115. Beach things belong to their place: a parasol only on dry sand above the waterline with a towel or lounger and
     sand behind it, never on the promenade or a path; towels only on sand, lying on its slope. (Round 33, the user:
     "There is an umbrella at the beach"; round 27: a towel on the paving; round 26: a flat towel "stuck out of the
     slope like a ramp".)
116. No boats as boxes; only tasteful beach dressing. (Round 27: the two beached boats removed, the user: "weird red
     and blue boxes"; "Everything added should be tasteful".)
117. The beach meets the promenade with paving like the rest of the promenade, no odd coloured patches (Barcelona: the
     big yellow patch at the Rambla's foot removed); lamps stand on the promenade, not in the sand or at its edge.
     (Round 23: "Remove the big yellow patch by the beach"; round 17 (HISTORY's 14th) and round 33: seafront lamps 1.3 tiles in.)
118. Where land meets the sea or a river mouth it flattens to the shore and slides under the water; never stepped
     green terraces into the sea. (Round 32: "the river mouth's stepped green terraces are gone".)
119. A river has banks that read as country, tufted and flowered (×1.9 by the banks); a road or bridge that crosses
     it lands on the bank and leads on as a worn track that fades out — "a road leads somewhere, even closed".
     (Round 32, the user: "review the parts where the city joins the nature… Does it look like the real world
     would?")
119a. **Smaller trees along both banks, not in rows**: small holm oaks with a cypress now and then, at uneven gaps
     (3.5–11 m) and uneven distances back from the water (about 2.5–7 m, always on dry bank, never in it), a lentisk or
     strawberry-tree bush by some; under some of them, on the north side where their shade falls, **a few small spots**
     of the half shade's ground (grass among needles), not big patches. Between the larger existing trees, which stay.
     (Round 41c, the user: "add some smaller trees and foliage along the river… so it feels less sparse"; "shouldn't
     be as orderly. Various distance between each other and then various distance from the water… patches of
     mid-texture ground underneath it to the north"; from three pictured mixes: "I think B, but move the trees slightly
     away from the water and then reduce the size of the middle texture grass. Just have a few small spots";
     north_build.py, the river's smaller trees.)
120. Don't mistake a light-map edge for water: a pale band at the edge of a light map is fixed by extending the map
     and lapping grass over the paving's edge, not by adding a stream or footbridge. (Round 31: "The 'stream' at the
     hill foot was never a stream".)

## Hills, far land and skyline

121. The land never ends at a void: a soft, rolling far skirt of country round the whole world, out to about 1.7 km,
     meeting the ground's edge at its own height, under the haze; below the horizon the sky keeps the haze's colour
     so land fades into sky (`world2d.py` FarLand; `cam.far` 2200). (Round 26, the user: "I see the river, then a
     plane, then an ocean. The distant land should not feel disjointed"; memory walk-review: "Does the far land go
     on, or end?")
121a. The world's edge sits well beyond anywhere she can run up to and see close; from up high looking away,
     everything simply fades into the distance, with no clear break where the built land meets the far land. Don't
     spend much effort on it beyond that: no clear break is enough. (Round 40, the user: "make sure that the world
     ends far enough away from what the user can run up and see … As long as there's not a clear break. But I don't
     want to waste too much compute on this.")
121b. Past the eastern wood the far land is the far hills' dark green, not the plain's paler green, so a glimpse of it
     reads as the forest going on (round 41, the user: "replace that with the dark green. Then it looks like the
     forest extends, and that helps if she ever catches a glimpse of it, and that should be enough… the dark green is
     just whatever is currently surrounding the field"; `world2d.py` FarLand, east of the grid → the wooded hills' `M_HILL`).
     Then all of the far land, every side, wooded the same way ("continue that texture further out… just in case
     there's a chance she sees it"); and the ground under the outermost trees too: 20 m past the furthest she can
     walk (east, north, and west north of the river), the green ground takes the same wooded look, while inside that
     margin the wood's own floor carries on, so she never sees the join and from above the wood seems to thicken ("the
     intermediate ground colour texture continues a little bit further past the point that she can walk to, so she
     doesn't ever see the join… it actually looks like the trees are getting thicker"; `world2d.py` `OUT_MARGIN`,
     `out_of_reach`). The meadow west of the river and the coast keep theirs. (The user called this one "a question of
     taste": shown before and after, `round41/wood_before_after.jpg`.) Kept for the north and east (the user: "the
     forest texture works for the north and the east").
121c. **The west is farmland** (round 41, the user: "for the west, I think fields would be better. Maybe what looks
     like some roads and some very low fidelity houses that look like farmhouses from the distance"; then "make them
     more green and then extend them almost to the river… still the variation"): the low plain west of the river, from
     10 m back from its west bank (the bank stays grass with its tufts) out across the far land, is a patchwork of
     fields, mostly greens of every shade with a few pale stubble ones, darker hedge lines between; long dusty roads
     across it; small farmhouses beside the roads, cream walls and terracotta gable roofs. The hills round it stay
     wooded. `world2d.py` `WEST_FIELDS` (False takes it out), `M_FIELDS`, `FIELD_BANK_X`; no meadow tufts on the fields
     (`forest.py`). Pictures `round41/west_fields_mock2.jpg`.
     Then (the user: "add trees along the riverbank on the other side… Not too many. You should be able to see
     through… The road across the river should be a proper bitumen road that then curves off into the little forest
     out of view… keep continuing off into the distance through the fields… the fields are naturally around it… the
     road should eventually disappear out of sight… add some trees along the edges of the fields"): a tree or a small
     group every 9–17 m along the far bank with gaps between (round 41, "just add more trees along the riverbank": 29); past the closed bridge a tarmac road, starting on the deck just past the barrier (no grass between: "make sure the
     road connects to the bridge"), bends through a
     small wood (not deep, thick enough from the bridge) and runs on due west along a hedge line of the fields, over the
     far hills into the haze; the side roads run along hedge lines too (the fields' picture repeats every 380 m, hedged
     round its edge, so the roads lie on hedges and the fields sit square to them); trees, whole (trunk and crown),
     along about half the fields' edges near the city. No worn track past the bridge now. The tarmac runs on past the
     round hill on its seaward side, then bends inland and climbs into the dip between the coastal ridge and the big
     mountain behind (far_h's valley, z about −190), on through the wood into the haze; the hills stay the barrier, the
     valley a dip between them, and the fields only a wedge in its mouth, narrowing to a point as the road climbs into
     the wood (the user: "the fields disappear to a point as the road goes over the valley… It's meant to be an
     illusion"; `world2d.py valley_field`). Farmhouses a little more detailed: a door to the road, dark windows, a
     chimney, now and then a barn ("make the houses ever so slightly more detailed"). (`north_build.py` "the far
     bank", `world2d.py ROADS_W`.) The build stayed at 157 s (was 156). Pictures `round41/road_bank_2.jpg`.
122. Far hills are named after the real ones round the city (Barcelona: Collserola north, the Garraf west, the
     Maresme east), faded by the haze. (Rounds 10, 26.)
123. Far textures are soft irregular patches, never rows or stripes (per-pixel hash, warped phases in `farland_fn`,
     `farhill_fn`, `hill_fn`). (Round 29: "The far hills read as striped fields".)
124. Low hills behind a wood stay low enough that nothing shows over the trees (`HillsEast`). (Round 25.)
125. The skyline never drops away beside a landmark: a ridge carries on past the hilltop church, and the church
     stands on the highest point with no hill rising past it. (Round 26 walk review; round 25, the user: "Put it into
     the hill, but don't have the hill going up past it".)
126. A hill visible from the city is wooded and green, not sandy or bare (Barcelona: the hill east of the park wooded
     to the grid's edge, far tops only past x 198). (Round 17 (HISTORY's 14th): "The mountain behind the city is green and wooded, not
     sandy"; round 28: "a bare striped hillside".)
127. A raised landmark sits where it reads well from the main street: Barcelona's funfair at 78 m so from La Rambla it
     is halfway between the treetops and the hilltop, the hill church on the skyline at the street's end, lit at
     night. (Round 22, the user's spec; REVIEW "The spine of the city works".)
128. The hill's own ground: a gentle green verge beside the path, then banks that look steep where she can't climb
     (rock, a wall, a bank or thick undergrowth), never a blue speckled "cliff" texture. (Round 25: "No cliff texture
     on the hill's banks (it was the blue speckled wall)"; round 33: ground that refuses her must look steep.)
     The wood's floor (hill, eastern wood, Park Güell) is never stretched up a slope: on steep ground its pictures and
     its patches are laid from the side too, the same size as on the flat (round 41, the user: "fix the grass on the
     steep bank", then of the before and after, "the bottom ones look better"; `forest_floor.gdshader`;
     `workshop/screenshots/round41/bank41/`).

128a. The funicular runs through the wood, not down a wide bare strip: a light fringe of trees and bushes either
     side of its track, clear of the cabins and the two stations; on the grass between, tufts, ferns and the odd low
     bush, thickest by the trees and thinning out to bare grass by the track. (Round 40, the user: "add a few more
     trees and a bit of foliage? Just extend the forest lightly around the funicular"; then "add a bit of foliage
     along the grass, now we don't want thicker, we want it actually to be thinning as it gets closer to it".)

## Never empty (no "liminal" places)

129. No liminal places: no stretch of bare lawn, sand or paving that just sits there between things; every open area
     gets what such a place has in real life (tufts and the odd fern by woods, trees and shrubs on a bare hill,
     beach life, booths and benches on a plaza). (Round 26, the user: the hill east of the park bare lawn, "a
     liminal space"; round 28: "no liminal space round the park"; round 31: "Looks very liminal"; round 36: "ensure
     that the grass above it is not liminal".)
130. A place nobody planned for gets planted with its neighbour's planting, using its own random numbers so nothing
     else moves (Barcelona: the lawn east of Gràcia, `north_build.east_lawn`). (Round 36.)
131. Bare plazas are furnished as their real counterparts are (ticket booths, kiosks, flags on poles, benches along the
     edge, queue rails); a ride or prop is dressed so it doesn't read as a plain shape (the carousel's stripes and
     fringe). (Round 26 walk review: "The carousel read as a plain gold flying saucer"; REVIEW §5.)
132. But not filled everywhere: town pavements vary on purpose — full rows of trees, a few trees far apart, empty
     stretches where people walk, or mixed furniture; never furniture on every pavement. (HISTORY's round 10, memory: "the user
     does not want furniture on every pavement, and wants some empty stretches with people instead".)
133. Nothing standing about for no reason (a stray wall, fence, bench or railing beside gentle ground is removed).
     (Round 35b, the user: "remove the random brick wall and the fence that is doing nothing outside that building";
     PATH_RULES F13.)
134. Fill emptiness by deepening what is there, not by gimmicks; in a review round, move or change existing things
     rather than add new ones. (Round 25 lesson; round 35, the user: "don't add new things, just shift and modify
     existing things".)

## The map's painted look

135. The map is the world itself photographed from straight above at midday (no fog, people hidden), then painted:
     fine detail evened out, colours warmed and strengthened, edges gently inked in brown, on a cream paper border;
     names written on top by the game, crisp (`builder/stylise_map.py`). (Round 15 (HISTORY "The map (M)").)
136. The map shows the city that she needs a map for; outlying areas appear as round painted pictures about a city
     block across at the ends of inked arrows, with their names (`R = 105`, `BAND = 400`). (Round 24, the user:
     "Make the map just a city map like it was (that was good), with arrows to the other sections"; round 25: the
     pictures a block across.)
137. Repaint the map once a round, when the layout is settled, not after every build. (Round 26, the user: "why do you
     have to repaint the map each time?"; memory pictures-not-tests.)

## How a look is judged

138. Judge looks at Sandra's eye level along routes, stopping where the scene changes, as a critic: does anything
     float, poke through, sit where it couldn't, look too plain, too big, too close; does the far land go on; is
     the light through the trees beautiful? Overhead pictures are allowed for layout. (Round 26, the user: "Look at
     the world the way that Sandra looks at the world…"; memory walk-review; CLAUDE.md "the light through the trees
     looked at and kept beautiful".)
139. Things right in front of the camera in a test picture (a butterfly by the lens) can look like faults; check
     before "fixing". (Round 26: "the 'orange curve on the sand' and a 'purple ball' turned out to be butterflies".)
140. Look changes are shown as pictures and judged by the user; don't run the whole test battery after each visual
     change. (Round 26, the user: "I need to see screenshots of what you have done and then give you guidance";
     memory pictures-not-tests.)

## Unclear or not yet decided

1. The sun rises in the east in the game, as in real life; the user once wrote "rises in the west". Should a new
   city's sun follow real directions, or did you mean something else?
2. Barcelona's city park (the Ciutadella) currently has no trees because of a stale planting list. Should every
   city park be well treed, and how thickly (pictures first)?
3. White decorative mushroom clumps (round 22) still grow alongside the brown toadstools; round 27 said "only the
   pickable mushrooms are red" and round 36 said "too many brown mushrooms". Do you want the white clumps kept, and
   what overall amount of decorative mushrooms is right for a new wood?
4. Park Güell's floor is "dryer" and its greens are at 60% saturation, while the wild wood's floor is "magical… more
   green". Is the dry, toned-down look only for that one garden, or a rule for every dry Mediterranean park or
   garden in a new city?
5. "Lots of plants" (the standing rule) against "less grass in the field" (round 28) and "don't add new things"
   (round 35): is there a density you want as the target for a new city's meadows and streets, or should each
   place be judged by pictures?
6. The near/far tree crossfade shows as a faint see-through sheet in still pictures at the wood's far rise. Is that
   acceptable in play, or should it be fixed?
7. The round-23 report of light flickering "on the paler trees" was never closed on its own; the round-26 flicker
   fixes may have covered it. Is it gone for you?
8. The shadow flicker on buildings and "the sun just behind her" when leaving the party (round 23) were never
   reproduced. Do you still see either?
9. The art-direction plan proposed a fixed palette of about 16 colours sampled from photos of the real city; it
   was never formally adopted. Should a new city start from such a palette?
10. Light shafts (volumetric haze) still show in the high-quality look in the streets; only the glade shafts were
    removed. Do you want shafts at all outside the churches?
11. Riverside planting (poplars and reeds along the bank, railings on the bridge) and a livelier Cascada were
    proposed in the round-26 review and never decided. Wanted?
12. The beach: the review also proposed sunbathers, a beach bar with tables and a lifeguard chair (some existed in
    early rounds). How busy should a beach be, and are any boats acceptable if they are done tastefully?
13. La Rambla's middle is a wide bare pavement; flower stalls, kiosks and benches down it were proposed and never
    decided. Should a city's main promenade be dressed like that?
14. Wildlife: the 2D game had butterflies on the beach and in town, which the 3D game removed. In a new city, are
    butterflies and fireflies for woods only, and are pigeons and gulls the only town and beach animals?
15. Night: the night sky's look was fixed by your pick (option D) and "don't darken further without asking". Should
    a new city use exactly the same night look, or be tuned to its own lights?
16. The stream's spring shows along the hill's foot (from the old 2D map) and was left as it is. Is a little water
    there wanted, or should it be grassed over?
