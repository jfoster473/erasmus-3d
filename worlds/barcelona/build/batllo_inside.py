# (round 26, the whole-game review: the rooms behind the famous doors were all the same box) Casa Batlló's noble floor,
# the Batlló family's salon on the Passeig de Gràcia, as the real one: the great oak bay window with its bone-like
# mullions and the discs of coloured glass in its upper lights; the whirlpool ceiling of plaster spiralling into the
# lamp; the mushroom-shaped fireplace nook with its two benches; the oak doors with their wavy tops; the parquet;
# and, through a door at the back, the light well tiled from deep blue at the top to pale at the bottom. Walked round
# freely (free_cam), as the Sagrat Cor's rooms. Exec'd from interiors.py; x runs across the room, y from the back
# (y = 1) to the street front (y = H), where the door is.
BT_W, BT_H = 18, 13
BT_WALL = 4.6
BT_DOOR = (14.6, 16.4)


def build_batllo_room(rid, R, k):
    ox = k * ROOM_GAP
    Pt, quad = _rooms_kit(ox)
    mb, glass, deco = MB(uv=True), MB(uv=True), MB(uv=True)
    W, H = BT_W, BT_H
    plaster = mat('BatlloPlaster', '#f1e9da', 0.9)
    plaster_d = mat('BatlloPlasterShade', '#e2d8c6', 0.9)
    oak = mat('BatlloOak', '#8a5a34', 0.55)
    oak_d = mat('BatlloOakDark', '#6b4326', 0.55)
    brass = mat('BatlloBrass', '#c9a24a', 0.35, 0.7)
    day = mat('DoorDaylight', '#fff4dc', 0.9)                           # (glows: the day outside)
    sky = mat('BatlloWindowDay', '#e9f3ff', 0.3)
    flame = mat('VaultLight', '#fff2c8', 0.2)
    velvet = mat('BatlloVelvet', '#7a3a3a', 0.85)
    hearth = mat('BatlloHearth', '#2a2622', 0.9)
    floor_m = floor_mat('parquet', None)
    # the light well's tiles: deep blue at the top, paler down each course (Gaudí's trick for an even light)
    def tiles_fn(x, y):
        t = y / 127.0                                                 # 0 at the bottom (pale), 1 at the top (deep)
        r_, g_, b_ = (0.78 - 0.62 * t, 0.86 - 0.5 * t, 0.92 - 0.3 * t)
        k_ = 0.82 if (x % 8 == 0 or y % 8 == 0) else 1.0 + random.Random(x // 8 * 131 + y // 8 * 7).uniform(-0.04, 0.04)
        return (r_ * k_, g_ * k_, b_ * k_)
    tiles = mat('BatlloWellTiles', '#ffffff', 0.35, image=make_image('batllo_tiles', 32, 128, tiles_fn))
    solids, posts, things = [], [], []
    rng = random.Random(1906)

    # ---------------------------------------------------------------- floor, ceiling, the four walls
    quad(mb, Pt(0.8, 0.8), Pt(W - 0.8, 0.8), Pt(W - 0.8, H + 0.2), Pt(0.8, H + 0.2), floor_m, (0, 0, 1))
    quad(mb, Pt(1, 1, BT_WALL), Pt(1, H, BT_WALL), Pt(W - 1, H, BT_WALL), Pt(W - 1, 1, BT_WALL), plaster, (0, 0, -1))
    d0, d1 = BT_DOOR
    WX0, WX1, WZ0, WZ1 = 2.2, 12.2, 0.95, 3.95                          # the great window in the front wall
    # the front wall (y = H): wall round the window and the door
    for (a, b, z0, z1) in ((1, WX0, 0, BT_WALL), (WX1, d0, 0, BT_WALL), (d1, W - 1, 0, BT_WALL), (WX0, WX1, 0, WZ0), (WX0, WX1, WZ1, BT_WALL),
                           (d0, d1, 2.6, BT_WALL)):
        quad(mb, Pt(b, H, z0), Pt(a, H, z0), Pt(a, H, z1), Pt(b, H, z1), plaster, (0, 1, 0))
    _doorway(mb, Pt, quad, d0, d1, H, 2.6, plaster_d, floor_m, oak)
    # the back wall (y = 1): the door to the light well, and a shut oak door with a wavy top
    LW0, LW1 = 11.2, 12.8                                               # the way into the light well
    for (a, b, z0, z1) in ((1, LW0, 0, BT_WALL), (LW1, W - 1, 0, BT_WALL), (LW0, LW1, 2.5, BT_WALL)):
        quad(mb, Pt(a, 1, z0), Pt(b, 1, z0), Pt(b, 1, z1), Pt(a, 1, z1), plaster, (0, -1, 0))
    # the side walls: the west one with the fireplace nook cut out, the east one whole
    NK0, NK1, NK_Z = 5.2, 8.2, 2.5                                      # the nook's opening along the west wall
    NKC, NKR = (NK0 + NK1) / 2, (NK1 - NK0) / 2
    def cap_z(t):
        """The opening's top edge: a mushroom cap, flat-ish in the middle, rounding down to the sides (t in -1..1)."""
        return NK_Z - 1.3 + 1.3 * math.sqrt(max(0.0, 1 - t * t)) ** 0.6
    for (a, b) in ((1, NK0), (NK1, H)):
        quad(mb, Pt(1, a, 0), Pt(1, b, 0), Pt(1, b, BT_WALL), Pt(1, a, BT_WALL), plaster, (1, 0, 0))
    arc = [(NK0 + (NK1 - NK0) * j / 16, cap_z(-1 + 2 * j / 16)) for j in range(17)]
    mb.face([Pt(1, NK0, BT_WALL), Pt(1, NK1, BT_WALL)] + [Pt(1, y_, z_) for (y_, z_) in reversed(arc)], plaster, normal=(1, 0, 0))
    quad(mb, Pt(W - 1, H), Pt(W - 1, 1), Pt(W - 1, 1, BT_WALL), Pt(W - 1, H, BT_WALL), plaster, (-1, 0, 0))
    # a skirting and a soft cornice all round (the walls of this house have no hard edges)
    for (p0, p1, nrm) in (((1, 1), (W - 1, 1), (0, -1, 0)), ((W - 1, 1), (W - 1, H), (-1, 0, 0)), ((W - 1, H), (1, H), (0, 1, 0)), ((1, H), (1, 1), (1, 0, 0))):
        ax, ay = p0
        bx, by = p1
        ux, uy = (bx - ax), (by - ay)
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        nx, ny = -nrm[0], nrm[1]                                        # (into the room, in room x, y)
        deco.box(Pt((ax + bx) / 2 + nx * 0.04, (ay + by) / 2 + ny * 0.04, 0.09), (ux, -uy), (nx, -ny), L / 2, 0.04, 0.09, oak_d)
        # the cornice: a smooth cove, a quarter circle from the wall up into the ceiling
        CV = 0.42
        for j in range(7):
            a0, a1 = math.pi / 2 * j / 7, math.pi / 2 * (j + 1) / 7
            o0, z0 = CV * (1 - math.cos(a0)), BT_WALL - CV + CV * math.sin(a0)
            o1, z1 = CV * (1 - math.cos(a1)), BT_WALL - CV + CV * math.sin(a1)
            o0e, o1e = o0 - 0.01, o1 - 0.01                             # (a hair into the wall, so the ends never gap)
            quad(deco, Pt(ax + nx * o0e - ux * 0.3, ay + ny * o0e - uy * 0.3, z0), Pt(bx + nx * o0e + ux * 0.3, by + ny * o0e + uy * 0.3, z0),
                 Pt(bx + nx * o1e + ux * 0.3, by + ny * o1e + uy * 0.3, z1), Pt(ax + nx * o1e - ux * 0.3, ay + ny * o1e - uy * 0.3, z1),
                 plaster, (nx * math.cos((a0 + a1) / 2), -ny * math.cos((a0 + a1) / 2), -math.sin((a0 + a1) / 2)))

    # ---------------------------------------------------------------- the great window: oak, bone mullions, coloured discs
    # a window seat along it, the frame, the panes (the day beyond them), three mullions like knuckled bones
    deco.box(Pt((WX0 + WX1) / 2, H - 0.3, 0.5), (1, 0), (0, 1), (WX1 - WX0) / 2 + 0.3, 0.3, 0.5, oak)               # the seat
    deco.box(Pt((WX0 + WX1) / 2, H - 0.3, 1.02), (1, 0), (0, 1), (WX1 - WX0) / 2 + 0.32, 0.32, 0.03, oak_d)
    solids.append([WX0 - 0.3, H - 0.65, WX1 + 0.3, H + 0.1])
    quad(glass, Pt(WX0, H - 0.02, WZ0), Pt(WX1, H - 0.02, WZ0), Pt(WX1, H - 0.02, WZ1), Pt(WX0, H - 0.02, WZ1), sky, (0, 1, 0))
    # (beyond the glass, the Passeig: the plane trees' green and the houses opposite, as a soft painted view)
    view_m = mat('BatlloView', '#ffffff', 0.9, image=make_image('batllo_view', 64, 32, lambda x, y: (
        (0.62, 0.72, 0.5) if y < 14 + 4 * math.sin(x * 0.5) else ((0.86, 0.8, 0.7) if y < 22 else (0.78, 0.86, 0.95)))))
    quad(glass, Pt(WX0 - 0.5, H + 0.4, WZ0 - 0.3), Pt(WX1 + 0.5, H + 0.4, WZ0 - 0.3), Pt(WX1 + 0.5, H + 0.4, WZ1 + 0.3), Pt(WX0 - 0.5, H + 0.4, WZ1 + 0.3),
         view_m, (0, 1, 0))
    for (z, hh) in ((WZ0, 0.06), (2.75, 0.09), (WZ1, 0.08)):           # the rails
        deco.box(Pt((WX0 + WX1) / 2, H - 0.06, z), (1, 0), (0, 1), (WX1 - WX0) / 2 + 0.1, 0.1, hh, oak)
    for xm in (WX0, WX0 + (WX1 - WX0) / 4, (WX0 + WX1) / 2, WX0 + 3 * (WX1 - WX0) / 4, WX1):
        # a mullion: a slim oak shaft that swells into a knuckle under the transom and spreads at its foot
        zm_ = (WZ0 + 2.75) / 2
        deco.cone(Matrix.Translation(Pt(xm, H - 0.1, zm_ - 0.45)) @ Matrix.Rotation(0.06, 4, 'Y'), 12, 0.13, 0.1, 0.95, oak)     # the shaft, bowing a little
        deco.cone(Matrix.Translation(Pt(xm + 0.03, H - 0.1, zm_ + 0.45)) @ Matrix.Rotation(-0.06, 4, 'Y'), 12, 0.1, 0.15, 0.95, oak)
        deco.sphere(Matrix.Translation(Pt(xm + 0.05, H - 0.1, 2.68)) @ Matrix.Diagonal((1.25, 0.9, 0.7, 1)), 0.19, oak, (12, 8))   # the knuckle
        deco.sphere(Matrix.Translation(Pt(xm, H - 0.1, WZ0 + 0.06)) @ Matrix.Diagonal((1.3, 0.9, 0.5, 1)), 0.18, oak, (12, 8))     # its foot
        deco.cone(Matrix.Translation(Pt(xm, H - 0.08, (2.75 + WZ1) / 2)), 8, 0.06, 0.06, WZ1 - 2.75, oak)
    # the upper lights: a row of round discs of coloured glass, blues, greens and amber, in oak surrounds
    cols = ['#4f8fd6', '#6fb7c9', '#7ec07a', '#e2b84a', '#4c7fc0', '#9bd0a8']
    n_d = 14
    for i in range(n_d):
        xd = WX0 + (WX1 - WX0) * (i + 0.5) / n_d
        zd = (2.75 + WZ1) / 2
        deco.cone(Matrix.Translation(Pt(xd, H - 0.05, zd)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), 18, 0.29, 0.29, 0.05, oak_d, caps=True)   # its oak ring
        glass.cone(Matrix.Translation(Pt(xd, H - 0.06, zd)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), 18, 0.22, 0.22, 0.02,
                   mat('BatlloDisc' + cols[i % len(cols)], cols[i % len(cols)], 0.25), caps=True)
    things.append(dict(kind='window', pos=[(WX0 + WX1) / 2, H - 1.2],
                       t="The great window onto the Passeig. The oak between the panes swells and bends like bones (the "
                         "neighbours called this the House of Bones), and the little discs of coloured glass up top throw "
                         "blue and amber onto the floor in the afternoon."))

    # ---------------------------------------------------------------- the whirlpool ceiling and its lamp
    cx, cy = W / 2, H / 2 + 0.3
    # the dish: the ceiling sinks a little towards the lamp (a shallow inverted cone of plaster)
    deco.cone(Matrix.Translation(Pt(cx, cy, BT_WALL + 0.16)), 36, 0.3, 3.6, 0.5, plaster, caps=True)
    # the swirl: one ridge spiralling out from the lamp, a little thicker each turn, as water going down a drain
    turns, steps = 5.5, 220
    prev = None
    for i in range(steps + 1):
        a = 2 * math.pi * turns * i / steps
        r_ = 0.35 + 3.1 * i / steps
        z_ = BT_WALL - 0.02 - 0.42 * (1 - r_ / 3.45)                     # (following the dish down to the lamp)
        p = Pt(cx + math.cos(a) * r_, cy + math.sin(a) * r_ * 0.9, z_)
        if prev is not None:
            deco.tube(prev, p, 0.035 + 0.03 * i / steps, plaster_d, 6)
        prev = p
    deco.tube(Pt(cx, cy, BT_WALL - 0.4), Pt(cx, cy, BT_WALL - 1.0), 0.025, brass, 6)                             # the lamp
    deco.cone(Matrix.Translation(Pt(cx, cy, BT_WALL - 1.08)), 12, 0.3, 0.42, 0.14, brass)
    deco.sphere(Matrix.Translation(Pt(cx, cy, BT_WALL - 1.3)) @ Matrix.Diagonal((1, 1, 0.75, 1)), 0.32, flame, (14, 10))
    things.append(dict(kind='ceiling', pos=[cx, cy + 1.2],
                       t="The ceiling swirls into the lamp like water going down a drain. Plaster, not stone, but it "
                         "makes you dizzy if you look too long."))

    # ---------------------------------------------------------------- the fireplace nook: a mushroom of oak panelling in the
    # west wall, a bench either side of the little hearth, the cap arching over
    NK_D = 1.3                                                          # how deep it goes into the wall
    nx0 = 1 - NK_D
    quad(mb, Pt(nx0, NK0), Pt(nx0, NK1), Pt(nx0, NK1, NK_Z), Pt(nx0, NK0, NK_Z), oak, (1, 0, 0))                    # its back
    quad(mb, Pt(nx0, NK0), Pt(1, NK0), Pt(1, NK0, NK_Z), Pt(nx0, NK0, NK_Z), oak, (0, -1, 0))
    quad(mb, Pt(1, NK1), Pt(nx0, NK1), Pt(nx0, NK1, NK_Z), Pt(1, NK1, NK_Z), oak, (0, 1, 0))
    quad(mb, Pt(nx0, NK0, 0.01), Pt(1, NK0, 0.01), Pt(1, NK1, 0.01), Pt(nx0, NK1, 0.01), floor_m, (0, 0, 1))
    # its ceiling follows the cap's curve down to the sides; the cap's rim comes out into the room, rounded, like the
    # edge of a mushroom, in oak
    for j in range(16):
        (y0, z0), (y1, z1) = arc[j], arc[j + 1]
        quad(mb, Pt(nx0, y0, z0), Pt(nx0, y1, z1), Pt(1.0, y1, z1), Pt(1.0, y0, z0), oak_d, (0, 0, -1))
        for k_ in range(5):                                             # the rim: a quarter round out from the edge
            b0, b1 = math.pi / 2 * k_ / 5, math.pi / 2 * (k_ + 1) / 5
            RR = 0.28
            def rim(y_, z_, b):
                return Pt(1.0 + RR * math.sin(b), y_, z_ + RR * (1 - math.cos(b)))
            quad(deco, rim(y0, z0, b0), rim(y1, z1, b0), rim(y1, z1, b1), rim(y0, z0, b1), oak,
                 (math.cos((b0 + b1) / 2), 0, -math.sin((b0 + b1) / 2)))
    # a band of oak round the rim's top, and panelling inside: raised panels on the back wall
    for yy in (NK0 + 0.5, NKC, NK1 - 0.5):
        deco.box(Pt(nx0 + 0.03, yy, 1.6), (1, 0), (0, 1), 0.02, 0.36, 0.35, oak_d)
    for yy in (NK0 + 0.55, NK1 - 0.55):                                  # the two benches, facing each other
        deco.box(Pt(nx0 + 0.45, yy, 0.42), (1, 0), (0, 1), 0.42, 0.42, 0.04, oak)
        deco.box(Pt(nx0 + 0.45, yy + (0.4 if yy < (NK0 + NK1) / 2 else -0.4), 0.7), (1, 0), (0, 1), 0.42, 0.04, 0.3, oak)
        deco.box(Pt(nx0 + 0.45, yy, 0.2), (1, 0), (0, 1), 0.38, 0.36, 0.2, oak_d)
        deco.box(Pt(nx0 + 0.45, yy, 0.47), (1, 0), (0, 1), 0.36, 0.36, 0.03, velvet)
    deco.box(Pt(nx0 + 0.02, (NK0 + NK1) / 2, 0.45), (1, 0), (0, 1), 0.02, 0.45, 0.45, hearth)                     # the hearth
    deco.box(Pt(nx0 + 0.08, (NK0 + NK1) / 2, 1.1), (1, 0), (0, 1), 0.08, 0.55, 0.2, brass)                        # its hood
    deco.sphere(Matrix.Translation(Pt(nx0 + 0.12, (NK0 + NK1) / 2, 0.25)) @ Matrix.Diagonal((1, 1.4, 1.2, 1)), 0.09, flame, (6, 5))
    things.append(dict(kind='fireplace', pos=[1.8, (NK0 + NK1) / 2],
                       t="A nook like a mushroom, panelled in oak, with a bench either side of the little fire: for two to "
                         "sit and warm their feet while the family talked in the salon. The housekeeper says the children "
                         "hid here."))

    # ---------------------------------------------------------------- the light well: a shaft beyond the little door, tiled
    # blue from deep to pale, the sky's light coming down it
    WD = 2.6                                                            # the shaft's depth beyond the back wall
    wx0, wx1 = LW0 - 0.6, LW1 + 0.6
    for (a, b, z0, z1) in ((LW0, LW1, 0, 2.5),):
        pass
    quad(mb, Pt(LW0, 1, 0.01), Pt(LW1, 1, 0.01), Pt(LW1, 1 - WD, 0.01), Pt(LW0, 1 - WD, 0.01), floor_m, (0, 0, 1))
    quad(mb, Pt(wx0, 1 - WD, 0.01), Pt(wx1, 1 - WD, 0.01), Pt(wx1, 1 - 0.3, 0.01), Pt(wx0, 1 - 0.3, 0.01), floor_m, (0, 0, 1))
    Z_WELL = 11.0
    for (p0, p1, nrm) in (((wx0, 1 - WD), (wx1, 1 - WD), (0, -1, 0)), ((wx1, 1 - WD), (wx1, 1 - 0.3), (-1, 0, 0)), ((wx0, 1 - 0.3), (wx0, 1 - WD), (1, 0, 0))):
        u_ = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        mb.face([Pt(*p0, 0), Pt(*p1, 0), Pt(*p1, Z_WELL), Pt(*p0, Z_WELL)], tiles, normal=nrm, uvs=[(0, 0), (u_ / 1.0, 0), (u_ / 1.0, 1), (0, 1)])
    for (a, b) in ((wx0, LW0), (LW1, wx1)):                              # the well's own side of the back wall, either side of the door
        mb.face([Pt(b, 1 - 0.3, 0), Pt(a, 1 - 0.3, 0), Pt(a, 1 - 0.3, Z_WELL), Pt(b, 1 - 0.3, Z_WELL)], tiles, normal=(0, 1, 0),
                uvs=[(0, 0), ((b - a) / 1.0, 0), ((b - a) / 1.0, 1), (0, 1)])
    mb.face([Pt(LW1, 1 - 0.3, 2.5), Pt(LW0, 1 - 0.3, 2.5), Pt(LW0, 1 - 0.3, Z_WELL), Pt(LW1, 1 - 0.3, Z_WELL)], tiles, normal=(0, 1, 0),
            uvs=[(0, 0.23), ((LW1 - LW0), 0.23), ((LW1 - LW0), 1), (0, 1)])
    for xs in (LW0, LW1):                                               # the door's reveal through the wall
        quad(mb, Pt(xs, 1, 0), Pt(xs, 1 - 0.3, 0), Pt(xs, 1 - 0.3, 2.5), Pt(xs, 1, 2.5), plaster_d, (1 if xs == LW0 else -1, 0, 0))
    quad(mb, Pt(LW0, 1, 2.5), Pt(LW1, 1, 2.5), Pt(LW1, 1 - 0.3, 2.5), Pt(LW0, 1 - 0.3, 2.5), plaster_d, (0, 0, -1))
    quad(deco, Pt(wx0, 1 - WD, Z_WELL), Pt(wx1, 1 - WD, Z_WELL), Pt(wx1, 1 - 0.3, Z_WELL), Pt(wx0, 1 - 0.3, Z_WELL), day, (0, 0, -1))  # the sky
    for zz in (3.2, 6.0, 8.8):                                          # the little windows of the flats above, looking in
        for xw in (wx0 + 0.9, wx1 - 0.9):
            deco.box(Pt(xw, 1 - WD + 0.03, zz), (1, 0), (0, 1), 0.3, 0.02, 0.45, oak_d)
            glass.box(Pt(xw, 1 - WD + 0.05, zz), (1, 0), (0, 1), 0.24, 0.01, 0.38, sky)
    deco.box(Pt((LW0 + LW1) / 2, 1 - 0.05, 2.55), (1, 0), (0, 1), (LW1 - LW0) / 2 + 0.12, 0.08, 0.06, oak)         # the door's oak surround
    for xs in (LW0 - 0.06, LW1 + 0.06):
        deco.box(Pt(xs, 1 - 0.05, 1.25), (1, 0), (0, 1), 0.06, 0.08, 1.3, oak)
    things.append(dict(kind='light well', pos=[(LW0 + LW1) / 2, 2.2],
                       t="The light well. The tiles are deep blue at the top and get paler as they come down, so the daylight "
                         "feels the same on every floor; the windows are bigger lower down for the same reason. Gaudí "
                         "thought of everything, Lluïsa says."))
    # a wavy-topped oak door, shut, on the back wall; another on the east wall
    def wavy_door(x, y, nrm_, wide=1.0):
        """A shut oak door whose top rises in a smooth wave to the middle, in a surround that follows it."""
        ux_, uy_ = ((1, 0) if nrm_[1] else (0, 1))
        def D(u, z, out=0.0):
            return Pt(x + ux_ * u + nrm_[0] * out, y + uy_ * u + nrm_[1] * out, z)
        def top(u, lift):
            return 2.1 + lift * (0.5 + 0.5 * math.cos(math.pi * u / wide))      # 2.1 at the edges, up to 2.1 + lift in the middle
        n_ = 14
        for (hw_, lift_, out_, m_) in ((wide + 0.1, 0.72, 0.03, oak_d), (wide, 0.62, 0.06, oak)):
            pts_ = [D(-hw_, 0, out_), D(hw_, 0, out_)] + [D(hw_ - 2 * hw_ * j / n_, top(hw_ - 2 * hw_ * j / n_, lift_), out_) for j in range(n_ + 1)]
            deco.face(pts_, m_, normal=(nrm_[0], -nrm_[1], 0))
        for zz in (0.5, 1.5):                                           # two raised panels
            deco.box(D(0, zz, 0.075), (ux_, -uy_), (nrm_[0], -nrm_[1]), wide * 0.6, 0.015, 0.35, oak_d)
        deco.box(D(wide * 0.65, 1.0, 0.09), (ux_, -uy_), (nrm_[0], -nrm_[1]), 0.03, 0.03, 0.08, brass)
    wavy_door(4.5, 1.03, (0, 1, 0))
    wavy_door(W - 1.03, 4.0, (-1, 0, 0))
    wavy_door(W - 1.03, 9.5, (-1, 0, 0))
    things.append(dict(kind='door', pos=[4.5, 2.0], t="An oak door whose top rises in a wave, like everything in this house. Locked: the family's rooms."))

    # ---------------------------------------------------------------- furniture: Gaudí's bench for two, his chairs, a table
    def batllo_chair(x, y, ang):
        u_, n_ = (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang))
        deco.box(Pt(x, y, 0.45), (u_[0], -u_[1]), (n_[0], -n_[1]), 0.24, 0.24, 0.035, oak)                    # a seat hollowed like a palm
        deco.box(Pt(x, y, 0.22), (u_[0], -u_[1]), (n_[0], -n_[1]), 0.2, 0.2, 0.22, oak_d)
        bx_, by_ = x - n_[0] * 0.22, y - n_[1] * 0.22
        deco.box(Pt(bx_, by_, 0.62), (u_[0], -u_[1]), (n_[0], -n_[1]), 0.03, 0.03, 0.16, oak)                  # the stem
        deco.box(Pt(bx_ - n_[0] * 0.03, by_ - n_[1] * 0.03, 0.95), (u_[0], -u_[1]), (n_[0], -n_[1]), 0.2, 0.025, 0.2, oak)    # the back, a rounded board
        deco.sphere(Matrix.Translation(Pt(bx_ - n_[0] * 0.03, by_ - n_[1] * 0.03, 1.15)) @ Matrix.Diagonal((1.0, 0.2, 0.35, 1)), 0.2, oak, (10, 6))
        solids.append([x - 0.3, y - 0.3, x + 0.3, y + 0.3])
    batllo_chair(6.0, 10.0, 0.5)
    batllo_chair(8.2, 9.6, -0.4)
    batllo_chair(10.4, 10.2, 0.2)
    # the bench for two: one piece of oak that curves round two sitters
    bx, by = 13.2, 5.0
    deco.box(Pt(bx, by, 0.44), (1, 0), (0, 1), 0.75, 0.26, 0.04, oak)
    deco.box(Pt(bx, by, 0.2), (1, 0), (0, 1), 0.7, 0.22, 0.2, oak_d)
    bk = [(bx + math.sin(a) * 0.82, by - 0.26 - (1 - math.cos(a)) * 0.22) for a in [-1.0 + 2.0 * j / 10 for j in range(11)]]
    for (p0_, p1_) in zip(bk, bk[1:]):                                  # the back: one board curving round the sitters
        quad(deco, Pt(*p0_, 0.5), Pt(*p1_, 0.5), Pt(*p1_, 1.0), Pt(*p0_, 1.0), oak, (0, 1, 0))
        quad(deco, Pt(*p1_, 0.5), Pt(*p0_, 0.5), Pt(*p0_, 1.0), Pt(*p1_, 1.0), oak_d, (0, -1, 0))
    deco.sphere(Matrix.Translation(Pt(bx, by - 0.3, 1.04)) @ Matrix.Diagonal((0.5, 0.3, 0.2, 1)), 0.6, oak, (12, 6))   # the hump of its top
    solids.append([bx - 0.85, by - 0.5, bx + 0.85, by + 0.35])
    things.append(dict(kind='bench', pos=[bx, by + 0.9], t="Gaudí's bench for two, carved from one piece of oak to fit two people exactly, side by side. "
                                                          "Try it: it fits."))
    # a round table with a vase of lilies, and a rug
    tx, ty = 8.5, 7.0
    deco.cone(Matrix.Translation(Pt(tx, ty, 0.72)), 16, 0.65, 0.65, 0.04, oak)
    deco.cone(Matrix.Translation(Pt(tx, ty, 0.36)), 8, 0.12, 0.2, 0.7, oak_d)
    deco.cone(Matrix.Translation(Pt(tx, ty, 0.92)), 10, 0.09, 0.12, 0.36, mat('BatlloVase', '#5f8fa8', 0.3))
    for j in range(5):
        a = 2 * math.pi * j / 5
        deco.sphere(Matrix.Translation(Pt(tx + math.cos(a) * 0.12, ty + math.sin(a) * 0.12, 1.22)) @ Matrix.Diagonal((1, 1, 1.6, 1)), 0.05,
                    mat('BatlloLily', '#f6f0e4', 0.7), (6, 5))
    solids.append([tx - 0.7, ty - 0.7, tx + 0.7, ty + 0.7])
    quad(deco, Pt(tx - 2.6, ty - 2.0, 0.006), Pt(tx + 2.6, ty - 2.0, 0.006), Pt(tx + 2.6, ty + 2.6, 0.006), Pt(tx - 2.6, ty + 2.6, 0.006),
         mat('BatlloRugEdge', '#d9c6a0', 0.95), (0, 0, 1))
    quad(deco, Pt(tx - 2.35, ty - 1.75, 0.009), Pt(tx + 2.35, ty - 1.75, 0.009), Pt(tx + 2.35, ty + 2.35, 0.009), Pt(tx - 2.35, ty + 2.35, 0.009),
         mat('BatlloRug', '#8e3a34', 0.95), (0, 0, 1))
    # oak panelling to waist height round the room, with raised panels (the walls above it plain cream)
    for (p0, p1, nrm) in (((1, 1), (LW0 - 0.1, 1), (0, -1, 0)), ((LW1 + 0.1, 1), (W - 1, 1), (0, -1, 0)), ((W - 1, 1), (W - 1, H), (-1, 0, 0)),
                          ((1, NK1 + 0.1), (1, H), (1, 0, 0)), ((1, 1), (1, NK0 - 0.1), (1, 0, 0)), ((WX1 + 0.3, H), (d0 - 0.1, H), (0, 1, 0)),
                          ((d1 + 0.1, H), (W - 1, H), (0, 1, 0)), ((1, H), (WX0 - 0.3, H), (0, 1, 0))):
        ax, ay = p0
        bx2, by2 = p1
        L = math.hypot(bx2 - ax, by2 - ay)
        if L < 0.6:
            continue
        ux, uy = (bx2 - ax) / L, (by2 - ay) / L
        nx, ny = -nrm[0], nrm[1]
        deco.box(Pt((ax + bx2) / 2 + nx * 0.025, (ay + by2) / 2 + ny * 0.025, 0.55), (ux, -uy), (nx, -ny), L / 2, 0.025, 0.55, oak)
        deco.box(Pt((ax + bx2) / 2 + nx * 0.05, (ay + by2) / 2 + ny * 0.05, 1.1), (ux, -uy), (nx, -ny), L / 2, 0.05, 0.03, oak_d)
        n_p = max(1, int(L / 0.9))
        for j in range(n_p):
            sc = (j + 0.5) * L / n_p
            deco.box(Pt(ax + ux * sc + nx * 0.055, ay + uy * sc + ny * 0.055, 0.6), (ux, -uy), (nx, -ny), 0.3, 0.012, 0.3, oak_d)
    # a tall mirror in an oak frame on the east wall, and a vase on a stand
    deco.box(Pt(W - 1.04, 7.0, 1.7), (1, 0), (0, 1), 0.05, 0.7, 1.1, oak)
    deco.box(Pt(W - 1.08, 7.0, 1.7), (1, 0), (0, 1), 0.02, 0.6, 1.0, mat('BatlloMirror', '#cfd8dc', 0.05, 0.9))

    room = mb.finish('Room_' + rid)
    dec = deco.finish('Deco_' + rid)
    root = bpy.data.objects.new('Interior_' + rid, None)
    bpy.context.scene.collection.objects.link(root)
    for ob in (room, glass.finish('Glass_' + rid), dec):
        ob.parent = root
    INT_ROOTS.append(root)
    npcs = [nid for nid, n in W2['NPCS'].items() if n['at'][0] == rid]
    tinted = [[ox + (LW0 + LW1) / 2, 3.0, 1 - 1.2, 0.55, 0.72, 1.0, 1.3, 7.0],                      # the blue of the well
              [ox + (WX0 + WX1) / 2, 2.6, H - 1.5, 1.0, 0.95, 0.85, 1.4, 9.0],                      # the day through the window
              [ox + 1.2, 1.2, (NK0 + NK1) / 2, 1.0, 0.7, 0.4, 0.8, 4.0]]                            # the fire
    return {'name': R['name'], 'offset': [ox, 0], 'w': W, 'h': H, 'floor': [1, 1, W - 1, H],
            'exit': [d0, d1], 'spawn': [(d0 + d1) / 2, H - 1.5], 'free_cam': True, 'solids': solids, 'posts': posts,
            'things': things, 'stairs': [], 'npcs': npcs, 'wall_h': BT_WALL - 0.5,
            'lights': {'ceiling': [ox + cx, BT_WALL - 1.1, cy], 'windows': [], 'lamps': [], 'tinted': tinted, 'beams': []},
            'shop': False, 'kind': 'gaudi'}
