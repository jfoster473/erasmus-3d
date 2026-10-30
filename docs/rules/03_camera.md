# 03 · The camera

How the game's camera behaves, in every world: outdoors, on the bike, through doors, in rooms, on rides and at
viewpoints, and how it keeps out of walls, slopes and people. **This file is for the user's review** (24 Oct 2026:
"One of them… that I want to review are the rules about the camera movements specifically"). Numbers are the ones the
game uses now (`engine/main.gd`, top of file and `update_camera()`); each rule says where it came from. Questions the
rules leave open are at the end.

## The street camera: where it sits
1. **A follow camera behind and above her.** It turns about a point 1.4 m above her feet (`CAM_PIVOT_H`), 5 m back
   (`CAM_DIST`), with a 62° field of view. (Round 1: 4.3 m; round 40, the user: "move the camera a little bit further
   back from her".)
   Out in the world the view is a touch wider than that, ever so slightly (round 38, the user: "I want the world to be
   a bit wider when she's running around. Ever so slightly").
2. **It looks gently down the street, not at the pavement:** tipped down 0.30 rad (`CAM_PITCH`), so the horizon sits
   about 23% from the top of the screen. (Round 4, the user: "slightly lower, looking down the street rather than at
   the pavement"; round 27, the user: the horizon at 23% from the top.)
2a. **In a wood the camera comes down a little** so you can see under the crowns: it eases down over a few seconds as
   she goes in and back up as she comes out. Subtle. (Round 38, the user: "When she runs into the forest, the camera
   should come down a little bit so that she can see under the trees… This should be subtle.")
3. **It sees to the edge of the world**: nothing is clipped before 2.2 km, so the far country and skyline always
   show. (Round 26.)
4. **Its centre leads her a little and lags a little**: the point it turns about follows her smoothly (it catches up
   at a rate of 10 per second) and runs about a fifth of a second ahead in the direction she is moving, so the view
   opens up ahead of her rather than jerking with each step.

## Distance and zoom
5. **The player can zoom** with the mouse wheel, from 2.2 m to 9 m (each click ×0.9 or ×1.1). The chosen distance is
   kept until changed.
   Going in or out of a building the zoom and the camera's height go back to the usual (round 38, the user: the player
   can change the height "to something random. And then if you walk inside, then you walk outside, it should reset
   again"; "Cameras through doors, resetting the zoom"). Or until she goes through a door (round 38).
6. **On the bike it pulls back half as far again** (×1.5, `BIKE_CAM`) and stays there until she gets off, gliding out
   and back in (it eases at 2.5 a second), never jumping. (Round 19.)
7. **Getting off the bike is getting on in reverse**: she steps half a step sideways off the bike, and the camera
   glides across with her at the zoom's pace instead of jumping (`cam_slide`). (Round 20.)

## Swinging round behind her
8. **It comes round behind her by itself** when she moves: after the player last turned it by hand, it waits 1.8 s
   (`RECENTER_DELAY`), then swings round behind her direction of travel. (Round 2: 1.5 s; round 3: 1.8 s.)
9. **The swing never lurches.** It eases in over 0.6 s, speeds up and slows down at no more than 2.6 rad/s²
   (`CAM_ACCEL`), and slows in time to stop exactly behind her. Its speed is in proportion to how far round it has
   to go (`RECENTER_RATE` 1.3), at most 1.5 rad/s (`SWING_MAX`), and 2.4 times quicker when she is simply going
   straight on (`CATCH_UP`). (Round 3 on, "fluid controls"; the user notices any lurch or jolt.)
10. **On foot it only swings while she is moving** (faster than 1 m/s with a key held); standing still, the view
    stays where it is. **On the bike only once she rides forwards at a fair pace** (over 1.8 m/s), so that stopped, she
    can turn the bike round on the spot to face the camera. (Round 9.)
11. **It turns with her while she steers round a curve**, so a long curve doesn't leave it behind.
12. **Running back towards the camera doesn't send it spinning**: when she turns to come back towards it (it is
    nearly in front of her), it keeps going round the same way it started rather than flip-flopping. Strafing never
    sends it spinning. (Round 3.)
13. **The keys mean what the screen shows only when she sets off.** Setting off, forward is "into the screen". While
    the camera is swinging round behind her, her direction is held, so sent sideways she runs straight on while the
    camera comes round; then a held side key steers her. Turning the camera by hand while she runs steers her with it.
    (Rounds 9–17, user-approved; the full steering rules are in `04_character_movement.md`.)

## Turning it by hand
14. **Mouse**: click to take the mouse (Esc gives it back), or hold the right button and drag; 0.0026 rad per pixel.
    **Gamepad**: the right stick, 2.8 rad/s across and 60% of that up and down. **Touch**: the LOOK button turns
    dragging on the screen into looking, 0.0042 rad per pixel (a swipe across the screen is about a turn and a half). (Round 38: click again, or Esc, gives it back — 04 #26.)
15. **How far it tips**: outdoors from 1.15 rad down (looking down on her) to 0.3 rad up; in a free-camera room up to
    0.95 rad up, to look up into the vaults.

## Keeping out of things
(Round 40, the user, replacing everything this section said before: "treat it like an actual camera that's moving. It
cannot go through walls and magically see the inside of a building but it can sit over the hedge under the ceiling…
make sure that there is a clear amount of space between her and it [and it] doesn't automatically come in zoom in on her
simply because there is a hedge behind her"; "by saying walls, I've confused you. My wall here that makes the camera
come in, a walls of buildings… where we have a column, where we have a brick wall, even on the side of a staircase or
we have the hedge, the camera is not going to go into it"; and of the flat colour: "That approach has completely
failed… strip it out of the game".)

16. **The camera is a real camera: only buildings bring it in.** It can't pass through the walls of a building, so it
    never looks into anyone's rooms: where one is in the way it comes in closer to her, keeping 0.4 m off the wall
    (its probe's radius, so pilasters, sills and shop boards don't catch it). These, and nothing else, are its walls —
    named, never found by size:
    - the city's buildings (every block's houses, shops and landmarks);
    - the houses in a park (Barcelona: Casa Larrard, the Casa Museu Gaudí, Casa Trias, the two gate lodges), at their
      real height on the hill;
    - churches, stations and other buildings standing on their own (Barcelona: the Sagrat Cor — every part of it, its
      crypt, porch, round turrets, upper church, corner towers and central tower (round 41, the user: "the church on
      tibidabo needs to be treated as having walls that move the camera in") —, the funicular's two stations and the
      bottom one's ticket booth (round 41), the funfair's buildings — not its rides, kiosks or booths);
    - indoors, in the rooms walked round with this camera, the room's own walls as they are built: it never sees the
      dark beyond them (round 41, the user: "You should not be able to see through walls. pillars are ok");
    - a building front standing proud of its block (a wavy Gaudí front, a portico): a camera-only screen 1 m out
      along its whole width, so it stays outside the carving;
    - indoors, a room's own walls (never its furniture).
    A new kind of building is a camera wall only once it is added to this list (`scene cam_buildings`, the builder).
    **A hard rule, on foot and on the bike** (round 41, the play-through caught it dipping into a building while she
    rode along the Diagonal; the user: "could it be that the camera comes closer instead of dipping inside a building?
    I thought we had made a very hard rule about that. Again, only for building walls"). Trees, lamps and the rest
    may still pass across the view (16a: "They are objects, not walls").
16a. **Everything else it ignores**: it keeps its distance and follows her, and sits over, beside or beyond them as a
    real camera on a pole would — hedges and beds, garden, park, retaining and stair walls, parapets, terraces,
    columns and pillars, the calvary, fences and ropes, benches, rocks, kiosks, stalls, awnings, the funfair's rides,
    lamps, trees, people, a room's furniture. A column simply passes across the view, solid. (Round 40: "Don't treat
    the columns as a wall… As if the column is invisible. But obviously you can't see through the column.")
16b. **Under a roof she walks under, it stays under the ceiling.** It follows her along under it at its usual distance
    and never rises through the roof; where the roof's back wall (into the hill) is behind her, it comes in rather
    than into it. Barcelona: the park's covered walk (the Pòrtic de la Bugadera), its columns ignored (16a). Each such
    roof is named in the builder (`scene cam_roofs`).
    (Round 41, the user: "The funicular building should be treated as hard walls, so the camera moves in": the low
    station's platform roof, in 14 pieces along its steps, is one such roof; the station itself a camera wall, #16.)
16c. **A tree's leaves are never a wall in front of the camera** (round 41, the user: "make the trees not be like walls.
    The camera shouldn't come in"): leaves within about 2.5 m of the camera aren't drawn (the edge speckled, not a
    line), so under a street tree's crown it still sees her; their shade stays. Trees never bring it in (#16a).
    Barcelona: `foliage.gdshader` `CROWN`, the street trees' crowns.
17. **On a slope behind her it rises first, then comes closer.** Where the hillside's own ground is in the way, the
    camera first lifts and tips down to look at her (up to 0.6 rad, eased at 4 a second); only if that isn't enough
    does it come in closer (to no less than 0.6 m). It never shows a hill from underneath. Only the ground does this —
    no wall, box or bench on the hill. (Round 35; round 40: walls and boxes no longer.)
18. **No flat colour, no veil.** Nothing ever fades the picture to a wall's colour; there is no such code. (Round 40,
    replacing round 35's G4.)
19. **Too close to her, she isn't drawn.** Backed against a building, when the camera comes within 1 m of her (her
    ponytail's reach) she disappears, as in a first-person view, and comes back once it is 1.15 m away. (Round 35.)
20. **It passes through people as through trees, and anyone it is inside isn't drawn** while it is there — anyone
    within 0.8 m of it across the ground, outdoors and in the free-camera rooms alike; the same for a bird within 1 m
    of the lens. (Round 35; round 36's play-through.)
21. **It always starts at her height.** After a door, a move up a hill or a jump to a place, both she and the camera
    start where she stands, never at street level rising through the hill. (Round 35.)

## Doors and rooms
25. **Through a door the camera keeps the player's angle**: how far it was turned from behind her and how far it was
    tipped are kept going in and coming out. Coming out it is turned at most a quarter turn from behind her (else
    pressing forward would walk her straight back in), and she is put 1.8 m out from the door, room for the camera
    behind her. (Round 21: it used to be reset, turned to look back at the door.)
   (Round 38: its height — how far it is tipped — and the zoom are no longer kept: they go back to the usual through
   every door, rule 5. The turn is kept as before.) **Round 38 overrides the first sentence: only the turn is kept; the tip and the zoom go back to the usual.**
26. **Ordinary rooms have a fixed camera** over the cut-away front wall, framing the whole room from above (42° view,
    9.2 m up for a room of up to 14 × 10 m, higher and further back for bigger rooms), following her a little sideways
    (a quarter of her movement, more in bigger rooms), gliding rather than jumping. In these rooms the keys mean the
    screen's directions. (Round 1; round 19, the user likes the indoor controls as they are.)
27. **Great interiors are free-camera rooms**: the street camera works inside (a basilica, where the fixed camera over
    a cut-away wall wouldn't show the vaults), steering is sharper there to weave between columns, and camera-only
    screens across its doorways stop the camera swinging out into the dark beyond. Leaving one, the camera stays
    behind her. (Rounds 17–18.)
27a. **First-person places** (Casa Trias's loggia): walking in, the camera glides to her eyes and she is hidden; walking
    out it glides back behind her, to the tip it had; no wall veil there. (Round 39, the user: "when she does walk into
    here, it should become first person… The camera doesn't work very well. It goes brown"; scene `first_person`,
    `main.gd fp_rects`.)

## Rides, viewpoints and special views
28. **On a ride** (a Ferris wheel, a funicular, a cable car) the camera still follows and she can look round; E
    switches to **her own eyes** (the camera glides to her head and she is hidden; the mouse looks out), and E again
    steps back. (Round 22: following on rides; round 26: her own eyes.)
28a. **The funicular: the camera follows the car, she is inside it, unseen**, turning about a point 0.8 m above the
    usual (the user: "move the outside of the funicular view central pivot point a slightly bit more higher"). Riding up or down she is hidden in the
    car; the camera follows the car from beside the line, far enough out to frame all of it, and the player can take
    it round in circles (the mouse, ← →) as it climbs; E: her seat inside (28b). (Round 41, the user,
    after a first-person try and a mock-up of a bigger car were stopped: "Let's just make it the camera follows the
    cable car up and you can't see her. She's just inside of it. But you can move the camera around in circles as it's
    going up. That's it." The car stays as it is — a bigger one would need the passing loop's tracks widened; "If she
    doesn't fit and it looks weird, the windows can be boarded up".)
28b. **The funicular's seat view** (round 41, the user, with the new glass-ended car: "If she can look out from the
    inside, that would also be amazing. As well as the third person where you can spin around"; "Then she can sit at
    the bottom and look around as if she's at the bottom seat"): E swaps between following the car (28a) and her own
    eyes on a bench at the car's lower end, facing down the line; the mouse and ← → look round either way. **The view
    is framed by the car** ("either you can see part of the vehicle or you can't see any of it"): the bench sits back
    from the glass nose, so the glowing hoop, red ribs in the glass, grab posts, pillars and the floor's steps border
    it; she looks all the way round, and up and down (CHANGED, round 41, the user: "could we actually make it 360 in every
    direction? So it's just first person"; it was a quarter-turn either side, "limit it so you can only look 180
    degrees"); her body is not drawn.
    E reads "View from inside" / "View from outside" (round 41, the user: "Could you make the E text view from
    inside/view from outside?"). **Getting in and getting out, the screen fades to black and back** (each way; arriving it darkens over the ride's last moments — going up, from the moment the car's nose meets the portal's dark: "As soon as it touches the dark part… begin to fade to black" —: the user, "when you're going up into the building, looks like it glitches a bit. Could you also have a fade in and fade out?"), she is aboard and the
    camera already round the car when it returns, so nothing jumps or flickers; going up the car stands a moment (1 s: just past the end of the fade; the user: "half a second shorter"), then; going down from the top it is already moving as the picture fades back in, no wait ("it's moving from the moment the fade begins"), and
    gathers speed (over 2 s: "starts too slow"), and slows into the far platform (round 41, the user: "could the funicular start from stationary?
    So it briefly is stationary, then accelerates"; north.gd `start_cable`, `funi_ease`). Following the car, over the ride's last fifth the camera eases round behind it,
    looking along the open cutting into the station, so its arm never meets the plateau's bank over the portal (the
    user: "those walls are not treated as actual walls. So maybe the camera needs to be spun around a bit more") —
    only if the player hasn't turned or tipped it this ride ("when I move up or down, it keeps resetting"). Following a
    ride the camera never tips by itself (rule 17's rise over a slope is for walking): where the ground is in the way it
    only comes nearer ("it will pull you back down to neutral").
29. **At a viewpoint** (a bench with a view, a calvary) "Stop and look at the view" gives an over-the-shoulder look
    out; **a coin telescope** gives a fixed zoom, turned slowly with the arrow keys for a minute, framed like a real
    binocular viewer. (Round 25, the user: "a telescope… for 1 euro… a fixed zoom… move slowly… consider real world
    tourist telescopes with the two eye holes".) Through it only its own keys show at the bottom, not the usual key
    lines (round 41c, the user: "remove the normal text below so I can see the actual options").
30. **On a phone held upright**, the picture is centred in the part of the screen above the touch controls, showing a
    little more from top to bottom (the view widened by 12%). (Round 20e.)
31. **The map picture is not the game camera**: the painted map comes from a straight-down picture at midday, no fog,
    people hidden (`--mapshot`). (See `08_terrain_walls_map.md`.)

## The camera and the light
32. **Her shadow must not flicker under the camera**: the finest shadow detail is kept where she stands, 4.3 m in
    front of the camera (6.5 m on the bike). (Round 26, the user: "Sandra's shadow is flickering".)
33. **Facing the sun brightens the sky alone** (02 #22): soft, not a hard disc, fading as the sun is hidden; it
    doesn't change as the camera moves about; what stands in front of the sky is untouched. (Rounds 16, 20; round 38.)

## Unclear or not yet decided (for the user)
- When she stands still, should the camera ever come round behind her by itself (now it never does)?
- The 1.8 s wait before it swings back after you turn it by hand, and the swing's top speed: right as they are?
- Zoom: is 2.2–9 m the right range, and should the zoom be remembered between sessions?
- On touch screens, should looking by dragging be always on, without the LOOK button (noted as a maybe in round 20e)?
- Is the 23% horizon right on a phone held upright as well as on a computer?
- On the bike: is half as far back again right, at speed and on hills?
- Should a new world's interiors default to the fixed camera over a cut-away wall, with only great interiors free?

28c. **Every first-person view looks round the same way** (her seat in the funicular, the Ferris wheel's gondola, a
    bench; and following the funicular from outside, its up and down turned so it feels the same as inside: "the camera
    movements up and down when I'm outside of the funicular are opposite to what it looks like inside… inside is
    correct"): ← → turn, ↑ looks up and ↓ looks down (the user: "I thought the up arrow should look up"; a flight stick's
    inversion, tried first, was the opposite), from straight up to straight down;
    the prompt shows "← → ↑ ↓ look round" (round 41, the user: "could you make the up and down inverted? And also have up
    and down arrows. And also check that the other first persons are the same. They should all be the same"; main.gd
    `turn_camera`; check: `--fpkeys`). **Nothing tips it back**: once the player has tipped or turned a first-person
    view it stays where they left it — a ride, a bench, or a first-person place walked into (the user: "it keeps
    resetting… all of the first person views").

33. **The title screen is the live world from over Park Güell** — the terrace and its gatehouses in front, the
    Sagrada Família in the middle, the sea behind — at the game's own time, with whoever is about; "ERASMUS IN BARCELONA"
    near the top with "Sandra's Adventure" close under it, the steeple's tip just below (round 41, the user: "a picture
    looking at the city as if it's from a helicopter… an action shot of the world at that time. Sunrise, sunset, with
    people walking around"; the view chosen in steps, workshop/screenshots/round41/title_aerials; main.gd `TITLE_VIEW`).
