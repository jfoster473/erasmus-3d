# (round 26) Inside the Temple del Sagrat Cor, as the real one: two churches, one on top of the other, each with its own
# door (the user: "Make the inside of the church" … "Separate entrances"; the plan they saw: round26/church_inside_plan.png).
#   the crypt (int_sagrat_cor), in from the porch on the funfair: low and warm, in Montjuïc stone; five aisles between
#     four rows of short thick columns with round arches, barrel vaults over them, the middle one all gold mosaic, blue
#     mosaic bands across the others; the high altar in a gold niche, a side altar at the end of each aisle, racks of
#     candles, hanging lamps; pews in the second and fourth aisles
#   the upper church (int_sagrat_alta), in by its own doors on the terrace: tall, pale and bright; a gold mosaic apse
#     behind the high altar and the great crucifix, a smaller apse either side with stained glass (cool to the east,
#     warm to the west), tall lancets, the rose window over the doors, eight columns under the tower holding up its
#     drum and dome with the light coming down from its lantern, mosaic panels of Jesus' life, pews
# Both walked round with the street camera (free_cam), as the Sagrada Família. Exec'd from interiors.py; the room's
# x runs across it (west to east), y from the altar (y = 1) to the doors (y = h).
if 'st_dress' not in globals():
    exec(open(os.path.join(HERE, 'stone_tex.py')).read())

CR_W, CR_H = 24, 16                         # the crypt, metres
CR_COLS_X = (5.4, 9.8, 14.2, 18.6)          # its four rows of columns (between the five aisles)
CR_COLS_Y = (4.0, 7.0, 10.0, 13.0)
CR_SPRING, CR_TOP = 2.8, 4.4                # the arches spring from the capitals; the vaults from their tops
CR_DOOR = (11.0, 13.0)
UP_W, UP_H = 20, 20                         # the upper church
UP_WALL = 12.0
UP_OCT = (10.0, 9.0, 3.4)                   # the octagon of columns under the tower: centre x, y, radius
UP_DOOR = (9.0, 11.0)


def _rooms_kit(ox):
    """What both rooms share: points, quads, the daylight at the end of a doorway."""
    def Pt(x, y, z=0.0):
        return Vector((ox + x, -y, z))

    def quad(mb, a, b, c_, d, m, nrm):
        mb.face([a, b, c_, d], m, normal=nrm)
    return Pt, quad


def _doorway(mb, Pt, quad, d0, d1, yw, top, stone, floor_m, frame):
    """A short corridor out through the front wall at room y = yw to the day beyond (DoorDaylight glows; dusk blue at
    night), as the Sagrada Família's: only to look down, she is outside as soon as she steps into it."""
    day_m = mat('DoorDaylight', '#fff4dc', 0.9)
    yb = yw + 3.0
    quad(mb, Pt(d0, yw, 0), Pt(d0, yb, 0), Pt(d0, yb, top), Pt(d0, yw, top), stone, (1, 0, 0))
    quad(mb, Pt(d1, yb, 0), Pt(d1, yw, 0), Pt(d1, yw, top), Pt(d1, yb, top), stone, (-1, 0, 0))
    quad(mb, Pt(d0, yw, top), Pt(d1, yw, top), Pt(d1, yb, top), Pt(d0, yb, top), stone, (0, 0, -1))
    quad(mb, Pt(d0, yw, 0.01), Pt(d1, yw, 0.01), Pt(d1, yb, 0.01), Pt(d0, yb, 0.01), floor_m, (0, 0, 1))
    quad(mb, Pt(d0, yb, 0), Pt(d1, yb, 0), Pt(d1, yb, top), Pt(d0, yb, top), day_m, (0, 1, 0))
    for xs in (d0, d1):
        mb.box(Pt(xs, yw, top / 2), (1, 0), (0, 1), 0.1, 0.14, top / 2, frame)


def _arc_wall(mb, Pt, x, ya, yb, z_spring, z_top, half_t, m, segs=10):
    """A wall along the room's y at x, from ya to yb, between z_spring and z_top, with a round arch cut out of it
    (springing at z_spring): an arcade's arch, its faces both sides and its soffit."""
    r = (yb - ya) / 2
    ym = (ya + yb) / 2
    for j in range(segs):
        a0, a1 = math.pi * j / segs, math.pi * (j + 1) / segs
        y0, z0 = ym - r * math.cos(a0), z_spring + r * math.sin(a0)
        y1, z1 = ym - r * math.cos(a1), z_spring + r * math.sin(a1)
        for sd in (-1, 1):
            xx = x + sd * half_t
            mb.face([Pt(xx, y0, z0), Pt(xx, y1, z1), Pt(xx, y1, z_top), Pt(xx, y0, z_top)], m, normal=(sd, 0, 0))
        am = (a0 + a1) / 2
        mb.face([Pt(x - half_t, y0, z0), Pt(x + half_t, y0, z0), Pt(x + half_t, y1, z1), Pt(x - half_t, y1, z1)], m,
                normal=(0, -math.cos(am), -math.sin(am)))


def _barrel(mb, Pt, x0, x1, y0, y1, z_spring, m, segs=12, inset=0.0):
    """A round barrel vault over x0..x1, running along the room's y from y0 to y1, its faces looking down."""
    r = (x1 - x0) / 2 - inset
    xc = (x0 + x1) / 2
    for j in range(segs):
        a0, a1 = math.pi * j / segs, math.pi * (j + 1) / segs
        p0 = (xc - r * math.cos(a0), z_spring + r * math.sin(a0))
        p1 = (xc - r * math.cos(a1), z_spring + r * math.sin(a1))
        nx, nz = -(math.cos(a0) + math.cos(a1)) / 2, -(math.sin(a0) + math.sin(a1)) / 2
        mb.face([Pt(p0[0], y0, p0[1]), Pt(p1[0], y0, p1[1]), Pt(p1[0], y1, p1[1]), Pt(p0[0], y1, p0[1])], m, normal=(-nx, 0, nz))


def _candles(deco, Pt, x, y, n, rows, flame, wax, iron, face=1, side=False):
    """A votive stand: n little candles in stepped rows (their flames glow: VaultLight). (x, y) the back row's middle;
    the rows step down towards `face` (+1/-1) along y — or, side=True, along x (a rack against a side wall)."""
    def at(a, b, z):                                       # a: along the rack, b: back to front
        return Pt(x + b, y + a, z) if side else Pt(x + a, y + b, z)
    ax, nx = ((0, 1), (1, 0)) if side else ((1, 0), (0, 1))
    for rw in range(rows):
        z = 0.75 + rw * 0.16
        bb = face * rw * 0.14
        deco.box(at(0, bb, z - 0.03), ax, nx, n * 0.07 + 0.05, 0.07, 0.02, iron)
        for i in range(n):
            ca = -n * 0.07 + 0.07 + i * 0.14
            deco.cone(Matrix.Translation(at(ca, bb, z + 0.04)), 6, 0.025, 0.025, 0.08, wax)
            deco.sphere(Matrix.Translation(at(ca, bb, z + 0.11)) @ Matrix.Diagonal((1, 1, 1.8, 1)), 0.014, flame, (5, 4))
    deco.box(at(0, face * (rows - 1) * 0.07, 0.36), ax, nx, n * 0.07 + 0.03, rows * 0.07 + 0.02, 0.36, iron)


def build_crypt_room(rid, R, k):
    ox = k * ROOM_GAP
    Pt, quad = _rooms_kit(ox)
    rng = random.Random(1902)
    mb, glass, deco = MB(uv=True), MB(uv=True), MB(uv=True)
    W, H = CR_W, CR_H
    wall_m = mat('CryptWallPlain', '#c6a073', 0.9)                 # (dressed in the crypt's Montjuïc blocks below)
    floor_m = mat('CryptFloorPlain', '#e6dac2', 0.8)               # (flagstones)
    gold_m = mat('CryptGoldPlain', '#d7a640', 0.45)                # (gold mosaic)
    blue_m = mat('CryptBluePlain', '#3f63a8', 0.5)                 # (blue mosaic)
    col_m = mat('CryptAlabaster', '#eadfca', 0.55)
    cap_m = mat('CryptCapital', '#d9c49c', 0.7)
    vault_m = mat('CryptVault', '#eee2c8', 0.85)
    wood = mat('SgPew', '#8a5d3b', 0.6)
    flame = mat('VaultLight', '#fff2c8', 0.2)
    wax = mat('CandleWax', '#f4ecd8', 0.6)
    iron = M_IRON
    cloth = mat('AltarCloth', '#f4f0e8', 0.8)
    solids, posts = [], []

    # ---------------------------------------------------------------- floor, walls (the vaults spring from the side walls)
    quad(mb, Pt(0.8, 0.8), Pt(W - 0.8, 0.8), Pt(W - 0.8, H + 0.2), Pt(0.8, H + 0.2), floor_m, (0, 0, 1))
    crown = CR_TOP + (CR_COLS_X[0] - 1) / 2 + 0.2
    quad(mb, Pt(1, 1), Pt(W - 1, 1), Pt(W - 1, 1, crown), Pt(1, 1, crown), wall_m, (0, -1, 0))                 # the altar end
    quad(mb, Pt(1, H), Pt(1, 1), Pt(1, 1, CR_TOP), Pt(1, H, CR_TOP), wall_m, (1, 0, 0))
    quad(mb, Pt(W - 1, 1), Pt(W - 1, H), Pt(W - 1, H, CR_TOP), Pt(W - 1, 1, CR_TOP), wall_m, (-1, 0, 0))
    d0, d1 = CR_DOOR
    DT = 3.0
    for (a, b) in ((1, d0), (d1, W - 1)):                                                                      # the door end
        quad(mb, Pt(b, H), Pt(a, H), Pt(a, H, crown), Pt(b, H, crown), wall_m, (0, 1, 0))
    quad(mb, Pt(d1, H, DT), Pt(d0, H, DT), Pt(d0, H, crown), Pt(d1, H, crown), wall_m, (0, 1, 0))
    _doorway(mb, Pt, quad, d0, d1, H, DT, wall_m, floor_m, cap_m)
    for j in range(12):                                                                                        # a round arch over the door
        a0, a1 = math.pi * j / 12, math.pi * (j + 1) / 12
        c = ((d0 + d1) / 2, DT)
        rr = (d1 - d0) / 2 + 0.25
        deco.face([Pt(c[0] - math.cos(a0) * rr, H - 0.03, c[1] + math.sin(a0) * rr), Pt(c[0] - math.cos(a1) * rr, H - 0.03, c[1] + math.sin(a1) * rr),
                   Pt(c[0] - math.cos(a1) * (rr + 0.3), H - 0.03, c[1] + math.sin(a1) * (rr + 0.3)),
                   Pt(c[0] - math.cos(a0) * (rr + 0.3), H - 0.03, c[1] + math.sin(a0) * (rr + 0.3))], cap_m, normal=(0, 1, 0))
    # the two round windows of the crypt's front (outside, either side of the porch), their glass glowing
    pal = ['#d9533f', '#f0a030', '#f2c84b', '#2f6ab0', '#3aa0a0']
    for wx in (3.4, W - 3.4):
        for j in range(3):
            for i in range(2):
                m = mat('Stained' + pal[(i + j * 2) % 5], pal[(i + j * 2) % 5], 0.1)
                quad(glass, Pt(wx - 0.6 + i * 0.6 + 0.03, H - 0.04, 2.2 + j * 0.5), Pt(wx + i * 0.6 - 0.03, H - 0.04, 2.2 + j * 0.5),
                     Pt(wx + i * 0.6 - 0.03, H - 0.04, 2.66 + j * 0.5), Pt(wx - 0.6 + i * 0.6 + 0.03, H - 0.04, 2.66 + j * 0.5), m, (0, 1, 0))

    # ---------------------------------------------------------------- the five aisles: columns, arches, vaults
    xs = [1.0] + list(CR_COLS_X) + [W - 1.0]
    ys = [1.0] + list(CR_COLS_Y) + [float(H)]
    for x in CR_COLS_X:
        for (ya, yb) in zip(ys, ys[1:]):
            _arc_wall(mb, Pt, x, ya, yb, CR_SPRING, CR_TOP, 0.26, wall_m)
        for y in CR_COLS_Y:
            mb.box(Pt(x, y, 0.12), (1, 0), (0, 1), 0.42, 0.42, 0.12, cap_m)                                    # its base
            mb.cone(Matrix.Translation(Pt(x, y, 1.35)), 12, 0.31, 0.29, 2.3, col_m)                             # the shaft
            mb.cone(Matrix.Translation(Pt(x, y, 2.62)), 12, 0.3, 0.44, 0.24, cap_m)                             # the capital
            mb.box(Pt(x, y, 2.77), (1, 0), (0, 1), 0.34, 0.46, 0.04, cap_m)                                     # its abacus
            for j in range(4):                                                                                  # carved leaves
                a = math.pi / 4 + j * math.pi / 2
                deco.sphere(Matrix.Translation(Pt(x + math.cos(a) * 0.36, y + math.sin(a) * 0.36, 2.6)) @ Matrix.Diagonal((1, 1, 1.4, 1)),
                            0.07, gold_m, (6, 4))
            posts.append([x, y, 0.44])
    for i, (x0, x1) in enumerate(zip(xs, xs[1:])):
        middle = i == 2
        _barrel(mb, Pt, x0 + (0 if i == 0 else 0.26), x1 - (0 if i == 4 else 0.26), 1.0, float(H), CR_TOP,
                gold_m if middle else vault_m)
        if not middle:                                                  # blue mosaic bands across, over each column
            for y in CR_COLS_Y:
                _barrel(deco, Pt, x0 + (0 if i == 0 else 0.26), x1 - (0 if i == 4 else 0.26), y - 0.2, y + 0.2, CR_TOP, blue_m,
                        inset=0.03)

    # ---------------------------------------------------------------- the altars: the high altar in its gold niche,
    # a small one at the end of every other aisle with a mosaic over it, candles
    ac = (xs[2] + xs[3]) / 2
    mb.box(Pt(ac, 2.2, 0.12), (1, 0), (0, 1), 2.0, 1.2, 0.12, cap_m)                                      # the steps
    mb.box(Pt(ac, 1.9, 0.3), (1, 0), (0, 1), 1.6, 0.9, 0.06, cap_m)
    mb.box(Pt(ac, 1.75, 0.82), (1, 0), (0, 1), 1.1, 0.4, 0.46, col_m)                                     # the altar
    mb.box(Pt(ac, 1.75, 1.3), (1, 0), (0, 1), 1.18, 0.46, 0.02, cloth)
    deco.box(Pt(ac, 1.38, 0.75), (1, 0), (0, 1), 0.9, 0.02, 0.3, gold_m)                                  # its front
    for j in range(16):                                                                                    # the niche
        a0, a1 = math.pi * j / 16, math.pi * (j + 1) / 16
        rr = 1.6
        deco.face([Pt(ac - math.cos(a0) * rr, 1.03, 3.2 + math.sin(a0) * rr), Pt(ac - math.cos(a1) * rr, 1.03, 3.2 + math.sin(a1) * rr),
                   Pt(ac, 1.03, 3.2)], gold_m, normal=(0, -1, 0))
    quad(deco, Pt(ac - 1.6, 1.03, 1.5), Pt(ac + 1.6, 1.03, 1.5), Pt(ac + 1.6, 1.03, 3.2), Pt(ac - 1.6, 1.03, 3.2), gold_m, (0, -1, 0))
    deco.box(Pt(ac, 1.08, 2.7), (1, 0), (0, 1), 0.05, 0.03, 0.75, mat('CrossWood', '#6a4a30', 0.6))      # the cross on it
    deco.box(Pt(ac, 1.08, 3.05), (1, 0), (0, 1), 0.42, 0.03, 0.05, mat('CrossWood', '#6a4a30', 0.6))
    for sx in (-0.8, 0.8):
        deco.cone(Matrix.Translation(Pt(ac + sx, 1.75, 1.55)), 6, 0.03, 0.03, 0.45, M_GILT)
        deco.sphere(Matrix.Translation(Pt(ac + sx, 1.75, 1.82)) @ Matrix.Diagonal((1, 1, 1.8, 1)), 0.02, flame, (5, 4))
    solids.append([ac - 2.0, 1.0, ac + 2.0, 3.0])
    tinted = [[ox + ac, 2.0, 2.4, 1.0, 0.78, 0.42, 1.4, 7.0]]
    side_t = ["A side altar under a mosaic of the Virgin of Montserrat, dark-faced, the child on her knee.",
              "A side altar to Saint Joseph, his carpenter's square in the mosaic beside him.",
              "A side altar: Saint George and the dragon, in little tiles of green and gold.",
              "A side altar to Saint John Bosco, who came to Barcelona in 1886 and asked for a church up here."]
    for i, j_ in enumerate((0, 1, 3, 4)):
        sx_ = (xs[j_] + xs[j_ + 1]) / 2
        mb.box(Pt(sx_, 1.5, 0.5), (1, 0), (0, 1), 0.7, 0.32, 0.5, col_m)
        mb.box(Pt(sx_, 1.5, 1.02), (1, 0), (0, 1), 0.76, 0.36, 0.02, cloth)
        quad(deco, Pt(sx_ - 0.9, 1.03, 1.4), Pt(sx_ + 0.9, 1.03, 1.4), Pt(sx_ + 0.9, 1.03, 3.1), Pt(sx_ - 0.9, 1.03, 3.1), blue_m, (0, -1, 0))
        quad(deco, Pt(sx_ - 0.35, 1.04, 1.7), Pt(sx_ + 0.35, 1.04, 1.7), Pt(sx_ + 0.35, 1.04, 2.8), Pt(sx_ - 0.35, 1.04, 2.8), gold_m, (0, -1, 0))
        deco.sphere(Matrix.Translation(Pt(sx_, 1.06, 2.55)), 0.13, mat('MosaicFace', '#c9a27a', 0.6), (8, 6))   # the saint
        quad(deco, Pt(sx_ - 0.22, 1.055, 1.75), Pt(sx_ + 0.22, 1.055, 1.75), Pt(sx_ + 0.16, 1.055, 2.4), Pt(sx_ - 0.16, 1.055, 2.4),
             mat('MosaicRobe' + str(i), ['#7a2a3a', '#3e6b4a', '#c8322e', '#2f4f8f'][i], 0.6), (0, -1, 0))
        for sx2 in (-0.5, 0.5):
            deco.cone(Matrix.Translation(Pt(sx_ + sx2, 1.5, 1.2)), 6, 0.025, 0.025, 0.3, wax)
            deco.sphere(Matrix.Translation(Pt(sx_ + sx2, 1.5, 1.38)) @ Matrix.Diagonal((1, 1, 1.8, 1)), 0.016, flame, (5, 4))
        solids.append([sx_ - 0.8, 1.0, sx_ + 0.8, 1.9])
        tinted.append([ox + sx_, 1.4, 2.0, 1.0, 0.7, 0.4, 0.7, 4.5])
    # racks of candles by the side walls, near the door — (round 35, the user: "more against the wall facing the user
    # as they walk to them from the door. But not all the way up against the wall") turned to face the room, their
    # backs 0.3 m off the side wall (its face at x 1.0 and W - 1.0); the rows climb towards the wall, the lowest in front
    for (x_, face) in ((1.0 + 0.65, -1), (W - 1.0 - 0.65, 1)):
        _candles(deco, Pt, x_, 13.2, 7, 3, flame, wax, iron, face, side=True)
        xb = x_ + face * 0.28
        solids.append([round(min(x_, xb) - 0.12, 3), 12.65, round(max(x_, xb) + 0.12, 3), 13.75])
        tinted.append([ox + x_ - face * 0.3, 1.1, 13.2, 1.0, 0.62, 0.3, 1.1, 5.0])
    # hanging lamps down the middle aisle
    lamps = []
    for y in (4.5, 8.5, 12.5):
        top = CR_TOP + (xs[3] - xs[2]) / 2 - 0.3
        deco.tube(Pt(ac, y, top), Pt(ac, y, 3.9), 0.01, iron, 4)
        deco.cone(Matrix.Translation(Pt(ac, y, 3.8)), 8, 0.05, 0.25, 0.22, M_GILT)
        deco.sphere(Matrix.Translation(Pt(ac, y, 3.66)), 0.09, flame, (8, 6))
        lamps.append([ox + ac, 3.5, y])
    # pews in the second and fourth aisles, facing the altars
    for (x0, x1) in ((xs[1] + 0.5, xs[2] - 0.5), (xs[3] + 0.5, xs[4] - 0.5)):
        for y in [4.6 + j * 1.05 for j in range(8)]:
            xm = (x0 + x1) / 2
            mb.box(Pt(xm, y, 0.42), (1, 0), (0, 1), (x1 - x0) / 2, 0.2, 0.04, wood)
            mb.box(Pt(xm, y + 0.24, 0.7), (1, 0), (0, 1), (x1 - x0) / 2, 0.04, 0.3, wood)
            for xx in (x0 + 0.05, x1 - 0.05):
                mb.box(Pt(xx, y + 0.05, 0.21), (1, 0), (0, 1), 0.04, 0.22, 0.21, wood)
            solids.append([round(x0, 3), round(y - 0.22, 3), round(x1, 3), round(y + 0.3, 3)])
    # a sign by the door: the church above
    deco.box(Pt(d1 + 1.2, H - 0.06, 1.55), (1, 0), (0, 1), 0.4, 0.02, 0.28, mat('SignBoard', '#2f4f6f', 0.6))

    room = mb.finish('Room_' + rid)
    st_dress(room, {'CryptWallPlain': ('crypt', 0.0), 'CryptFloorPlain': ('flags', 0.0), 'CryptGoldPlain': ('gold', 0.0, 0.45),
                    'CryptBluePlain': ('blue', 0.0, 0.5)})
    dec = deco.finish('Deco_' + rid)
    st_dress(dec, {'CryptWallPlain': ('crypt', 0.0), 'CryptGoldPlain': ('gold', 0.0, 0.45), 'CryptBluePlain': ('blue', 0.0, 0.5)})
    root = bpy.data.objects.new('Interior_' + rid, None)
    bpy.context.scene.collection.objects.link(root)
    for ob in (room, glass.finish('Glass_' + rid), dec):
        ob.parent = root
    INT_ROOTS.append(root)

    T = {o[0]: o[3]['t'] for o in R['objs'] if len(o) > 3 and 't' in o[3]}
    things = [dict(kind='altar', t=T['altar'], pos=[ac, 3.4]),
              dict(kind='vault', t=T['vault'], pos=[ac, 8.0]),
              dict(kind='candles', t=T['candles'], pos=[2.25, 13.2]),
              dict(kind='candles', t=T['candles'], pos=[W - 2.25, 13.2]),
              dict(kind='column', t=T['column'], pos=[CR_COLS_X[1] + 0.7, 10.0]),
              dict(kind='sign', t=T['sign'], pos=[d1 + 1.2, H - 0.7])]
    for i, j_ in enumerate((0, 1, 3, 4)):
        things.append(dict(kind='sidealtar', t=side_t[i], pos=[(xs[j_] + xs[j_ + 1]) / 2, 2.4]))
    npcs = [nid for nid, n in W2['NPCS'].items() if n['at'][0] == rid]
    return {'name': R['name'], 'offset': [ox, 0], 'w': W, 'h': H, 'floor': [1, 1, W - 1, H],
            'exit': [d0, d1], 'spawn': [(d0 + d1) / 2, H - 1.5], 'free_cam': True, 'solids': solids, 'posts': posts,
            'things': things, 'stairs': [], 'npcs': npcs, 'wall_h': CR_SPRING + 0.1,
            'lights': {'ceiling': [ox + W / 2, CR_TOP - 0.6, H / 2], 'windows': [], 'lamps': lamps, 'tinted': tinted, 'beams': []},
            'shop': False, 'kind': 'sacred'}


def build_upper_room(rid, R, k):
    ox = k * ROOM_GAP
    Pt, quad = _rooms_kit(ox)
    mb, glass, deco = MB(uv=True), MB(uv=True), MB(uv=True)
    W, H = UP_W, UP_H
    wall_m = mat('UpperWallPlain', '#ece4d2', 0.85)                 # (dressed in the upper church's pale stone)
    gold_m = mat('CryptGoldPlain', '#d7a640', 0.45)
    blue_m = mat('CryptBluePlain', '#3f63a8', 0.5)
    shade_m = mat('UpperStoneShade', '#d8cfbc', 0.85)
    col_m = mat('UpperColumn', '#e4dccb', 0.6)
    ceil_m = mat('UpperVault', '#f2ece0', 0.85)
    rib_m = mat('UpperRib', '#cfc4ad', 0.85)
    floor_m = mat('UpperFloor', '#ffffff', 0.35, image=make_image('upper_floor', 64, 64, lambda x, y: (
        (0.9, 0.86, 0.8) if ((x // 16 + y // 16) % 2) else (0.66, 0.6, 0.58))))
    wood = mat('SgPew', '#8a5d3b', 0.6)
    door_wood = mat('UpperDoorWood', '#6a4a30', 0.6)
    flame = mat('VaultLight', '#fff2c8', 0.2)
    cloth = mat('AltarCloth', '#f4f0e8', 0.8)
    solids, posts = [], []
    COOL = ['#2f6ab0', '#3aa0a0', '#5cb85c', '#2f4f8f', '#7ac8d8']
    WARM = ['#d9533f', '#f0a030', '#f2c84b', '#c8322e', '#e87a2f']
    GOLD = ['#f2c84b', '#f0e0a0', '#e8a83a', '#fff0c0']
    rng = random.Random(1961)

    def pane(x0, y0, x1, y1, z0, z1, pal, nrm):
        m = mat('Stained' + pal[rng.randrange(len(pal))], pal[rng.randrange(len(pal))], 0.1)
        quad(glass, Pt(x0, y0, z0), Pt(x1, y1, z0), Pt(x1, y1, z1), Pt(x0, y0, z1), m, nrm)

    def lancet_x(x, yc, w, z0, z1, pal, nrm):
        """A tall pointed window in a side wall (x), centred at room y yc."""
        dx = 0.04 * nrm[0]
        for i in range(2):
            for j in range(6):
                a, b = yc - w / 2 + w * i / 2, yc - w / 2 + w * (i + 1) / 2
                c_, d_ = z0 + (z1 - z0) * j / 6, z0 + (z1 - z0) * (j + 1) / 6
                pane(x + dx, a + 0.03, x + dx, b - 0.03, c_ + 0.03, d_ - 0.03, pal, nrm)
        glass.face([Pt(x + dx, yc - w / 2, z1), Pt(x + dx, yc + w / 2, z1), Pt(x + dx, yc, z1 + w * 0.9)],
                   mat('Stained' + pal[0], pal[0], 0.1), normal=nrm)
        deco.box(Pt(x + dx * 0.5, yc, (z0 + z1) / 2), (1, 0), (0, 1), 0.05, 0.04, (z1 - z0) / 2, shade_m)       # the mullion

    # ---------------------------------------------------------------- floor, walls with the apses' openings, the doors
    quad(mb, Pt(0.8, 0.8), Pt(W - 0.8, 0.8), Pt(W - 0.8, H + 0.2), Pt(0.8, H + 0.2), floor_m, (0, 0, 1))
    AP_R, AP_X = 4.0, W / 2                                         # the main apse, behind the altar rail (y < 1)
    SA_R, SA_Y = 3.0, 12.5                                          # the side apses, east and west
    Z_AP, Z_SA = 9.0, 7.0                                           # the apses' walls (their half-domes above)

    def wall_with_arch(p0, p1, along, a0, a1, z_spring, nrm, m):
        """A wall from p0 to p1 (room x, y) UP_WALL high, with a pointed arch open from a0 to a1 (along its length)."""
        def P(t, z):
            return Pt(p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, z)
        Lw = along
        t0, t1 = a0 / Lw, a1 / Lw
        quad(mb, P(0, 0), P(t0, 0), P(t0, UP_WALL), P(0, UP_WALL), m, nrm)
        quad(mb, P(t1, 0), P(1, 0), P(1, UP_WALL), P(t1, UP_WALL), m, nrm)
        r = (a1 - a0) / 2
        segs = 10
        for j in range(segs):                                       # a pointed arch: two arcs meeting at the top
            for side in (0, 1):
                f0, f1 = j / segs, (j + 1) / segs
                ang0, ang1 = f0 * math.pi / 3, f1 * math.pi / 3
                if side == 0:
                    u0, u1 = a0 + 2 * r * (1 - math.cos(ang0)), a0 + 2 * r * (1 - math.cos(ang1))
                else:
                    u0, u1 = a1 - 2 * r * (1 - math.cos(ang0)), a1 - 2 * r * (1 - math.cos(ang1))
                z0_, z1_ = z_spring + 2 * r * math.sin(ang0), z_spring + 2 * r * math.sin(ang1)
                quad(mb, P(u0 / Lw, z0_), P(u1 / Lw, z1_), P(u1 / Lw, UP_WALL), P(u0 / Lw, UP_WALL), m, nrm)
        return P

    wall_with_arch((1, 1), (W - 1, 1), W - 2, AP_X - AP_R - 1, AP_X + AP_R - 1, 4.5, (0, -1, 0), wall_m)     # the altar end
    wall_with_arch((1, H), (1, 1), H - 1, H - SA_Y - SA_R, H - SA_Y + SA_R, 4.6, (1, 0, 0), wall_m)        # west
    wall_with_arch((W - 1, 1), (W - 1, H), H - 1, SA_Y - SA_R - 1, SA_Y + SA_R - 1, 4.6, (-1, 0, 0), wall_m)  # east
    d0, d1 = UP_DOOR
    DT = 4.4
    for (a, b) in ((1, d0), (d1, W - 1)):                                                                  # the door end
        quad(mb, Pt(b, H), Pt(a, H), Pt(a, H, UP_WALL), Pt(b, H, UP_WALL), wall_m, (0, 1, 0))
    quad(mb, Pt(d1, H, DT), Pt(d0, H, DT), Pt(d0, H, UP_WALL), Pt(d1, H, UP_WALL), wall_m, (0, 1, 0))
    _doorway(mb, Pt, quad, d0, d1, H, DT, wall_m, floor_m, shade_m)
    for sx in (-4.0, 4.0):                                                                                  # the side doors, shut
        quad(deco, Pt(W / 2 + sx + 0.9, H - 0.03, 0), Pt(W / 2 + sx - 0.9, H - 0.03, 0), Pt(W / 2 + sx - 0.9, H - 0.03, 3.4),
             Pt(W / 2 + sx + 0.9, H - 0.03, 3.4), door_wood, (0, 1, 0))
        deco.face([Pt(W / 2 + sx + 0.9, H - 0.03, 3.4), Pt(W / 2 + sx - 0.9, H - 0.03, 3.4), Pt(W / 2 + sx, H - 0.03, 4.6)],
                  door_wood, normal=(0, 1, 0))
    # the rose window over the doors: a ring of coloured panes round a blue heart
    rc, rz, rR = W / 2, 8.4, 2.1
    for ring, (r0, r1, n) in enumerate(((0.35, 1.0, 8), (1.05, 2.1, 16))):
        for j in range(n):
            a0, a1 = 2 * math.pi * j / n + 0.02, 2 * math.pi * (j + 1) / n - 0.02
            pal = COOL if (j + ring) % 2 else WARM
            m = mat('Stained' + pal[j % len(pal)], pal[j % len(pal)], 0.1)
            glass.face([Pt(rc + math.cos(a0) * r0, H - 0.05, rz + math.sin(a0) * r0), Pt(rc + math.cos(a1) * r0, H - 0.05, rz + math.sin(a1) * r0),
                        Pt(rc + math.cos(a1) * r1, H - 0.05, rz + math.sin(a1) * r1), Pt(rc + math.cos(a0) * r1, H - 0.05, rz + math.sin(a0) * r1)],
                       m, normal=(0, 1, 0))
    deco.cone(Matrix.Translation(Pt(rc, H - 0.08, rz)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), 24, rR + 0.3, rR + 0.3, 0.06, shade_m, caps=False)
    # tall lancets down the sides, either side of the side apses
    for y in (4.6, H - 2.6):
        lancet_x(1.0, y, 1.4, 3.0, 8.6, WARM, (1, 0, 0))
        lancet_x(W - 1.0, y, 1.4, 3.0, 8.6, COOL, (-1, 0, 0))

    # ---------------------------------------------------------------- the apses: walls round, half-domes of mosaic
    def apse(cx, cy, r, z_wall, dir_, dome_m, pal, n_win):
        """A half-round apse opening off the wall at (cx, cy), bulging out along dir_ (unit x, y in the room)."""
        dx, dy = dir_
        px, py = -dy, dx                                            # along the wall
        segs = 16
        for j in range(segs):
            a0, a1 = math.pi * j / segs, math.pi * (j + 1) / segs
            p0 = (cx + px * math.cos(a0) * r + dx * math.sin(a0) * r, cy + py * math.cos(a0) * r + dy * math.sin(a0) * r)
            p1 = (cx + px * math.cos(a1) * r + dx * math.sin(a1) * r, cy + py * math.cos(a1) * r + dy * math.sin(a1) * r)
            nrm = (-(dx * math.sin((a0 + a1) / 2) + px * math.cos((a0 + a1) / 2)),
                   (dy * math.sin((a0 + a1) / 2) + py * math.cos((a0 + a1) / 2)), 0)
            quad(mb, Pt(*p0, 0), Pt(*p1, 0), Pt(*p1, z_wall), Pt(*p0, z_wall), wall_m, nrm)
            mb.face([Pt(*p0, 0.005), Pt(*p1, 0.005), Pt(cx, cy, 0.005)], floor_m, normal=(0, 0, 1))
            for i in range(6):                                      # the half-dome, a quarter sphere
                b0, b1 = math.pi / 2 * i / 6, math.pi / 2 * (i + 1) / 6

                def S(a, b):
                    rr = r * math.cos(b)
                    return Pt(cx + px * math.cos(a) * rr + dx * math.sin(a) * rr, cy + py * math.cos(a) * rr + dy * math.sin(a) * rr,
                              z_wall + r * math.sin(b))
                deco.face([S(a0, b0), S(a1, b0), S(a1, b1), S(a0, b1)], dome_m, normal=(-dx * 0.5, dy * 0.5, -1))
            if n_win and j % (segs // n_win) == segs // n_win // 2:
                am = (a0 + a1) / 2
                wx_ = cx + px * math.cos(am) * (r - 0.05) + dx * math.sin(am) * (r - 0.05)
                wy_ = cy + py * math.cos(am) * (r - 0.05) + dy * math.sin(am) * (r - 0.05)
                tx, ty = (px * -math.sin(am) + dx * math.cos(am)), (py * -math.sin(am) + dy * math.cos(am))
                for jj in range(5):
                    c_ = pal[(j + jj) % len(pal)]
                    z0_ = 2.4 + jj * 0.9
                    quad(glass, Pt(wx_ - tx * 0.32, wy_ - ty * 0.32, z0_), Pt(wx_ + tx * 0.32, wy_ + ty * 0.32, z0_),
                         Pt(wx_ + tx * 0.32, wy_ + ty * 0.32, z0_ + 0.84), Pt(wx_ - tx * 0.32, wy_ - ty * 0.32, z0_ + 0.84),
                         mat('Stained' + c_, c_, 0.1), nrm)
    apse(AP_X, 1.0, AP_R, Z_AP, (0, -1), gold_m, GOLD, 0)
    apse(1.0, SA_Y, SA_R, Z_SA, (-1, 0), blue_m, WARM, 3)
    apse(W - 1.0, SA_Y, SA_R, Z_SA, (1, 0), blue_m, COOL, 3)
    # the high altar, up three steps in the main apse, and the great crucifix hanging over it
    for s_ in range(3):
        mb.box(Pt(AP_X, -0.9 + s_ * 0.25, 0.08 + s_ * 0.16), (1, 0), (0, 1), 2.6 - s_ * 0.4, 1.9 - s_ * 0.25, 0.08 + s_ * 0.16, shade_m)
    mb.box(Pt(AP_X, -0.9, 1.0), (1, 0), (0, 1), 1.3, 0.45, 0.48, col_m)
    mb.box(Pt(AP_X, -0.9, 1.5), (1, 0), (0, 1), 1.36, 0.5, 0.02, cloth)
    deco.box(Pt(AP_X, -0.43, 1.0), (1, 0), (0, 1), 1.0, 0.02, 0.32, gold_m)
    cr = Pt(AP_X, -0.4, 5.4)
    cw_ = mat('CrossWood', '#6a4a30', 0.6)
    deco.box(cr, (1, 0), (0, 1), 0.07, 0.07, 1.5, cw_)
    deco.box(cr + Vector((0, 0, 0.8)), (1, 0), (0, 1), 1.0, 0.07, 0.07, cw_)
    deco.box(cr + Vector((0, -0.08, 0.1)), (1, 0), (0, 1), 0.14, 0.04, 0.6, mat('Figure', '#e8d8b8', 0.6))
    deco.box(cr + Vector((0, -0.08, 0.72)), (1, 0), (0, 1), 0.8, 0.04, 0.05, mat('Figure', '#e8d8b8', 0.6))
    deco.tube(cr + Vector((0, 0, 1.5)), cr + Vector((0, 0, Z_AP + 2.0 - 5.4)), 0.01, M_IRON, 4)
    for sx in (-1.0, -0.5, 0.5, 1.0):
        deco.cone(Matrix.Translation(Pt(AP_X + sx, -0.9, 1.75)), 6, 0.03, 0.03, 0.45, M_GILT)
        deco.sphere(Matrix.Translation(Pt(AP_X + sx, -0.9, 2.02)) @ Matrix.Diagonal((1, 1, 1.8, 1)), 0.02, flame, (5, 4))
    # the Sacred Heart in the apse's mosaic: a white figure, arms open, on the gold of the half-dome
    fig = mat('MosaicRobeWhite', '#f2ece0', 0.6)
    deco.face([Pt(AP_X - 0.9, -2.9, 9.2), Pt(AP_X + 0.9, -2.9, 9.2), Pt(AP_X + 0.5, -2.42, 10.9), Pt(AP_X - 0.5, -2.42, 10.9)], fig,
              normal=(0, -1, -0.3))
    deco.face([Pt(AP_X - 1.5, -2.55, 10.55), Pt(AP_X + 1.5, -2.55, 10.55), Pt(AP_X + 1.5, -2.48, 10.8), Pt(AP_X - 1.5, -2.48, 10.8)], fig,
              normal=(0, -1, -0.3))
    deco.sphere(Matrix.Translation(Pt(AP_X, -2.1, 11.25)), 0.28, mat('MosaicFace', '#c9a27a', 0.6), (8, 6))
    deco.sphere(Matrix.Translation(Pt(AP_X, -2.55, 10.25)), 0.12, mat('MosaicRobe2', '#c8322e', 0.6), (6, 4))
    # altar rails across the three apses (where the room's walls stop her)
    for (a, b) in (((AP_X - AP_R, 1.15), (AP_X + AP_R, 1.15)), ((1.15, SA_Y - SA_R), (1.15, SA_Y + SA_R)),
                   ((W - 1.15, SA_Y - SA_R), (W - 1.15, SA_Y + SA_R))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n_ = int(L / 0.25)
        for i in range(n_ + 1):
            t = i / n_
            deco.cone(Matrix.Translation(Pt(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.45)), 6, 0.04, 0.05, 0.9, col_m)
        deco.box(Pt((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.93), (1, 0), (0, 1), max(0.08, abs(b[0] - a[0]) / 2 + 0.05),
                 max(0.08, abs(b[1] - a[1]) / 2 + 0.05), 0.04, M_GILT)

    # ---------------------------------------------------------------- the octagon under the tower: eight columns, pointed
    # arches, the drum above with its windows, the dome and its lantern; a mosaic star on the floor between them
    ocx, ocy, orr = UP_OCT
    Z_COL, Z_RING, Z_DRUM, Z_DOME = 8.0, 11.0, 15.0, 18.0
    pts = [(ocx + math.cos(math.pi / 8 + j * math.pi / 4) * orr, ocy + math.sin(math.pi / 8 + j * math.pi / 4) * orr) for j in range(8)]
    for (x, y) in pts:
        mb.cone(Matrix.Translation(Pt(x, y, Z_COL / 2)), 12, 0.32, 0.3, Z_COL, col_m)
        for j in range(4):                                          # its four slim shafts
            a = j * math.pi / 2 + math.pi / 4
            mb.cone(Matrix.Translation(Pt(x + math.cos(a) * 0.3, y + math.sin(a) * 0.3, Z_COL / 2)), 6, 0.08, 0.08, Z_COL, col_m)
        mb.box(Pt(x, y, 0.15), (1, 0), (0, 1), 0.5, 0.5, 0.15, shade_m)
        mb.cone(Matrix.Translation(Pt(x, y, Z_COL + 0.2)), 8, 0.36, 0.52, 0.4, shade_m)
        posts.append([round(x, 3), round(y, 3), 0.5])
    for j in range(8):                                              # the arches between them, and the ring of wall above
        (x0, y0), (x1, y1) = pts[j], pts[(j + 1) % 8]
        nx_, ny_ = (x0 + x1) / 2 - ocx, (y0 + y1) / 2 - ocy
        Ln = math.hypot(nx_, ny_)
        nrm_in = (-nx_ / Ln, ny_ / Ln, 0)
        nrm_out = (nx_ / Ln, -ny_ / Ln, 0)
        for (nrm, sh) in ((nrm_in, -0.2), (nrm_out, 0.2)):
            ox_, oy_ = nx_ / Ln * sh, ny_ / Ln * sh
            segs = 8
            ch_ = math.hypot(x1 - x0, y1 - y0)

            def AP(u, z):
                return Pt(x0 + (x1 - x0) * u + ox_, y0 + (y1 - y0) * u + oy_, z)
            for i in range(segs):
                for side in (0, 1):
                    a0, a1 = math.pi / 3 * i / segs, math.pi / 3 * (i + 1) / segs
                    u0, u1 = 1 - math.cos(a0), 1 - math.cos(a1)
                    if side:
                        u0, u1 = 1 - u0, 1 - u1
                    quad(mb, AP(u0, Z_COL + 0.4 + ch_ * math.sin(a0)), AP(u1, Z_COL + 0.4 + ch_ * math.sin(a1)),
                         AP(u1, Z_RING), AP(u0, Z_RING), shade_m, nrm)
        # the drum: up from the ring to the dome, a lancet of glass in each face
        a_, b_ = Pt(x0, y0, Z_RING), Pt(x1, y1, Z_RING)
        quad(mb, a_, b_, Pt(x1, y1, Z_DRUM), Pt(x0, y0, Z_DRUM), wall_m, nrm_in)
        mx_, my_ = (x0 + x1) / 2 - nx_ / Ln * 0.04, (y0 + y1) / 2 - ny_ / Ln * 0.04
        tx_, ty_ = (x1 - x0) / math.hypot(x1 - x0, y1 - y0), (y1 - y0) / math.hypot(x1 - x0, y1 - y0)
        pal = COOL if mx_ > ocx else WARM
        c_ = pal[j % len(pal)]
        quad(glass, Pt(mx_ - tx_ * 0.4, my_ - ty_ * 0.4, Z_RING + 1.0), Pt(mx_ + tx_ * 0.4, my_ + ty_ * 0.4, Z_RING + 1.0),
             Pt(mx_ + tx_ * 0.4, my_ + ty_ * 0.4, Z_DRUM - 0.8), Pt(mx_ - tx_ * 0.4, my_ - ty_ * 0.4, Z_DRUM - 0.8), mat('Stained' + c_, c_, 0.1), nrm_in)
        # the dome: eight curved panels up to the lantern, with ribs
        for i in range(6):
            b0, b1 = math.pi / 2 * i / 6, math.pi / 2 * (i + 1) / 6
            r0, r1 = math.cos(b0), math.cos(b1)
            z0_, z1_ = Z_DRUM + (Z_DOME - Z_DRUM) * math.sin(b0), Z_DRUM + (Z_DOME - Z_DRUM) * math.sin(b1)
            if r1 < 0.15:
                r1, z1_ = 0.15, Z_DOME
            quad(deco, Pt(ocx + (x0 - ocx) * r0, ocy + (y0 - ocy) * r0, z0_), Pt(ocx + (x1 - ocx) * r0, ocy + (y1 - ocy) * r0, z0_),
                 Pt(ocx + (x1 - ocx) * r1, ocy + (y1 - ocy) * r1, z1_), Pt(ocx + (x0 - ocx) * r1, ocy + (y0 - ocy) * r1, z1_),
                 blue_m if i < 5 else gold_m, (0, 0, -1))
            deco.tube(Pt(ocx + (x0 - ocx) * r0, ocy + (y0 - ocy) * r0, z0_ - 0.05), Pt(ocx + (x0 - ocx) * r1, ocy + (y0 - ocy) * r1, z1_ - 0.05),
                      0.08, rib_m, 4)
    quad(deco, Pt(ocx - 0.5, ocy - 0.5, Z_DOME + 0.4), Pt(ocx + 0.5, ocy - 0.5, Z_DOME + 0.4), Pt(ocx + 0.5, ocy + 0.5, Z_DOME + 0.4),
         Pt(ocx - 0.5, ocy + 0.5, Z_DOME + 0.4), flame, (0, 0, -1))                                         # the lantern's light
    for j in range(16):                                                                                     # the floor's star
        a0, a1 = 2 * math.pi * j / 16, 2 * math.pi * (j + 1) / 16
        rr0 = 2.2 if j % 2 else 1.4
        deco.face([Pt(ocx, ocy, 0.012), Pt(ocx + math.cos(a0) * rr0, ocy + math.sin(a0) * rr0, 0.012),
                   Pt(ocx + math.cos(a1) * (3.6 - rr0), ocy + math.sin(a1) * (3.6 - rr0), 0.012)],
                  gold_m if j % 2 else blue_m, normal=(0, 0, 1))

    # ---------------------------------------------------------------- the ceiling: rib vaults round the tower's opening
    hs = orr + 0.2
    oct_ = [(ocx + math.cos(math.pi / 8 + j * math.pi / 4) * orr / math.cos(math.pi / 8), ocy + math.sin(math.pi / 8 + j * math.pi / 4) * orr / math.cos(math.pi / 8)) for j in range(8)]
    corners = [(1, 1), (W - 1, 1), (W - 1, H), (1, H)]
    # each wall corner of the room joins the two nearest corners of the octagon (eight-ish fan): the ceiling, flat at
    # UP_WALL, with an octagonal hole for the drum
    ring = oct_
    outer = []
    for j in range(8):
        a = math.pi / 8 + j * math.pi / 4
        # the room's edge straight out from this octagon corner
        dx, dy = math.cos(a), math.sin(a)
        ts = []
        for (lim, d_, base) in ((1, dx, ocx), (W - 1, dx, ocx), (1, dy, ocy), (H, dy, ocy)):
            if abs(d_) > 1e-6:
                t = (lim - base) / d_
                if t > 0:
                    ts.append(t)
        t = min(ts)
        outer.append((ocx + dx * t, ocy + dy * t))
    for j in range(8):
        a0, a1 = ring[j], ring[(j + 1) % 8]
        b0, b1 = outer[j], outer[(j + 1) % 8]
        quad(mb, Pt(*a0, UP_WALL), Pt(*a1, UP_WALL), Pt(*b1, UP_WALL), Pt(*b0, UP_WALL), ceil_m, (0, 0, -1))
        deco.tube(Pt(*a0, UP_WALL - 0.1), Pt(*b0, UP_WALL - 0.1), 0.1, rib_m, 4)
    for c in corners:                                               # the corners left: a flat piece from each corner
        near = sorted(range(8), key=lambda j: math.hypot(outer[j][0] - c[0], outer[j][1] - c[1]))[:2]
        p_, q_ = outer[near[0]], outer[near[1]]
        mb.face([Pt(*c, UP_WALL), Pt(*p_, UP_WALL), Pt(*q_, UP_WALL)], ceil_m, normal=(0, 0, -1))
    for j in range(8):                                              # the drum's skirt between ceiling and ring
        a0, a1 = ring[j], ring[(j + 1) % 8]
        p0, p1 = pts[j], pts[(j + 1) % 8]
        quad(mb, Pt(*p0, Z_RING), Pt(*p1, Z_RING), Pt(*a1, UP_WALL), Pt(*a0, UP_WALL), shade_m, (0, 0, -1))

    # ---------------------------------------------------------------- mosaics of Jesus' life along the walls
    scenes = [("the Nativity", '#2f4f8f'), ("the Baptism in the Jordan", '#3aa0a0'), ("the Sermon on the Mount", '#5cb85c'),
              ("the Last Supper", '#7a2a3a')]
    panels = []
    for i, (yc, xw, nrm) in enumerate(((2.6, 1.0, (1, 0, 0)), (2.6, W - 1.0, (-1, 0, 0)), (7.0, 1.0, (1, 0, 0)), (7.0, W - 1.0, (-1, 0, 0)))):
        dx = 0.03 * nrm[0]
        name, bg = scenes[i]
        quad(deco, Pt(xw + dx, yc - 0.95, 1.4), Pt(xw + dx, yc + 0.95, 1.4), Pt(xw + dx, yc + 0.95, 2.9), Pt(xw + dx, yc - 0.95, 2.9), gold_m, nrm)
        quad(deco, Pt(xw + dx * 1.3, yc - 0.82, 1.52), Pt(xw + dx * 1.3, yc + 0.82, 1.52), Pt(xw + dx * 1.3, yc + 0.82, 2.78),
             Pt(xw + dx * 1.3, yc - 0.82, 2.78), mat('MosaicGround' + bg, bg, 0.6), nrm)
        for f_ in range(3):                                         # the figures
            fy = yc - 0.5 + f_ * 0.5
            robe = ['#f2ece0', '#c8322e', '#d7a640'][(f_ + i) % 3]
            quad(deco, Pt(xw + dx * 1.6, fy - 0.12, 1.6), Pt(xw + dx * 1.6, fy + 0.12, 1.6), Pt(xw + dx * 1.6, fy + 0.08, 2.3),
                 Pt(xw + dx * 1.6, fy - 0.08, 2.3), mat('MosaicRobe' + robe, robe, 0.6), nrm)
            deco.sphere(Matrix.Translation(Pt(xw + dx * 1.6, fy, 2.42)), 0.08, mat('MosaicFace', '#c9a27a', 0.6), (6, 4))
        panels.append((name, xw + nrm[0] * 0.8, yc))

    # ---------------------------------------------------------------- pews, in front of the octagon, a gangway down the middle
    for (x0, x1) in ((2.6, d0 - 0.4), (d1 + 0.4, W - 2.6)):
        for y in [13.7 + j * 1.0 for j in range(6)]:
            xm = (x0 + x1) / 2
            mb.box(Pt(xm, y, 0.42), (1, 0), (0, 1), (x1 - x0) / 2, 0.2, 0.04, wood)
            mb.box(Pt(xm, y + 0.24, 0.7), (1, 0), (0, 1), (x1 - x0) / 2, 0.04, 0.3, wood)
            for xx in (x0 + 0.05, x1 - 0.05):
                mb.box(Pt(xx, y + 0.05, 0.21), (1, 0), (0, 1), 0.04, 0.22, 0.21, wood)
            solids.append([round(x0, 3), round(y - 0.22, 3), round(x1, 3), round(y + 0.3, 3)])
    # a stand of leaflets by the door
    deco.box(Pt(d1 + 1.5, H - 0.5, 0.55), (1, 0), (0, 1), 0.3, 0.2, 0.55, wood)
    deco.box(Pt(d1 + 1.5, H - 0.55, 1.12), (1, 0), (0, 1), 0.26, 0.15, 0.02, cloth)
    solids.append([d1 + 1.2, H - 0.75, d1 + 1.8, H - 0.25])

    room = mb.finish('Room_' + rid)
    st_dress(room, {'UpperWallPlain': ('upper', 0.0), 'CryptGoldPlain': ('gold', 0.0, 0.45), 'CryptBluePlain': ('blue', 0.0, 0.5)})
    dec = deco.finish('Deco_' + rid)
    st_dress(dec, {'UpperWallPlain': ('upper', 0.0), 'CryptGoldPlain': ('gold', 0.0, 0.45), 'CryptBluePlain': ('blue', 0.0, 0.5)})
    root = bpy.data.objects.new('Interior_' + rid, None)
    bpy.context.scene.collection.objects.link(root)
    for ob in (room, glass.finish('Glass_' + rid), dec):
        ob.parent = root
    INT_ROOTS.append(root)

    T = {o[0]: o[3]['t'] for o in R['objs'] if len(o) > 3 and 't' in o[3]}
    things = [dict(kind='altar', t=T['altar'], pos=[AP_X, 1.9]),
              dict(kind='apse', t=T['apse'], pos=[AP_X - 2.6, 1.9]),
              dict(kind='glass', t=T['glass_east'], pos=[W - 2.0, SA_Y]),
              dict(kind='glass', t=T['glass_west'], pos=[2.0, SA_Y]),
              dict(kind='rose', t=T['rose'], pos=[W / 2 - 2.0, H - 1.6]),
              dict(kind='tower', t=T['tower'], pos=[ocx, ocy]),
              dict(kind='leaflets', t=T['leaflets'], pos=[d1 + 1.5, H - 1.3])]
    for (name, x, y) in panels:
        things.append(dict(kind='mosaic', t="A mosaic of %s, in little tiles of glass and gold: one of the scenes from Jesus' life "
                           "along the walls." % name, pos=[x, y]))
    npcs = [nid for nid, n in W2['NPCS'].items() if n['at'][0] == rid]
    tinted = [[ox + W - 3.0, 4.0, SA_Y, 0.45, 0.7, 1.0, 1.4, 10.0], [ox + 3.0, 4.0, SA_Y, 1.0, 0.6, 0.35, 1.4, 10.0],
              [ox + AP_X, 6.0, 1.5, 1.0, 0.85, 0.5, 1.6, 10.0], [ox + ocx, Z_RING, ocy, 1.0, 0.93, 0.75, 2.0, 14.0],
              [ox + W / 2, 7.0, H - 2.0, 0.6, 0.7, 1.0, 1.0, 9.0]]
    return {'name': R['name'], 'offset': [ox, 0], 'w': W, 'h': H, 'floor': [1, 1, W - 1, H],
            'exit': [d0, d1], 'spawn': [(d0 + d1) / 2, H - 1.5], 'free_cam': True, 'solids': solids, 'posts': posts,
            'things': things, 'stairs': [], 'npcs': npcs, 'wall_h': UP_WALL - 0.6,
            'lights': {'ceiling': [ox + W / 2, UP_WALL - 2.0, H / 2], 'windows': [], 'lamps': [], 'tinted': tinted, 'beams': []},
            'shop': False, 'kind': 'sacred'}
