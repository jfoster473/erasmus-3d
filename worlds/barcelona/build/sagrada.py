# The Sagrada Família, set the way the real one is: its apse to the north (the mountain side), the
# unfinished Glory façade to the south (the sea side), the Nativity façade to the east and the Passion
# façade to the west. Only those two are open, as now: the Nativity's central portal and the Passion's
# doors are the ways in. The Glory front is still a building site behind hoardings, with cranes.
#
# Its eighteen towers as they stand in 2026 (the Glory's four apostles not yet built):
#   Jesus Christ   over the crossing, the tallest, crowned with its white four-armed cross (lit at night)
#   the Virgin Mary  over the apse, with its glass star (lit at night)
#   the four Evangelists  round the crossing, each crowned with its symbol's colours
#   eight Apostles  four over each open façade: spindle-shaped, pierced with spiralling louvres, with
#                  mosaic mitre pinnacles, a ball and a cross
# The Nativity front is crowded with carved, dripping stone and its green cypress with white doves; the
# Passion front is austere: six slanting bone-like columns hold up a deep canopy crowned with
# eighteen bone ribs and the crucifix. Fruit baskets top the nave's pinnacles.
# Exec'd from landmarks.py (it replaces the old landmark_sagrada), sharing its helpers.

SAG_CY = 3.0                   # the crossing, metres north of the block's middle


def carved_fn(base, dark):
    """Carved, weathered stone: rounded lumps (leaves, figures, drips) with dark crevices between them."""
    b, d = rgb(base), rgb(dark)
    rr = random.Random(77)
    blobs = [(rr.uniform(0, 128), rr.uniform(0, 128), rr.uniform(7, 16)) for _ in range(70)]

    def fn(x, y):
        best = 0.0
        for (bx, by, br) in blobs:
            dx = min(abs(x - bx), 128 - abs(x - bx))
            dy = min(abs(y - by), 128 - abs(y - by))
            q = 1.0 - (dx * dx + dy * dy) / (br * br)
            if q > best:
                best = q
        t = max(0.0, min(1.0, 0.25 + 0.85 * best ** 0.6 + rr.uniform(-0.04, 0.04)))
        return tuple(d[i] + (b[i] - d[i]) * t for i in range(3))
    return fn


def lathe(mb, base, prof, segs, m):
    """A smooth surface of revolution through (z, r) rings round a vertical axis at base."""
    rings = []
    for (z, r) in prof:
        rings.append([mb.bm.verts.new(base + Vector((math.cos(2 * math.pi * k / segs) * r, math.sin(2 * math.pi * k / segs) * r, z)))
                      for k in range(segs)])
    mi = mb.mi(m)
    for i in range(len(rings) - 1):
        for k in range(segs):
            f = mb.bm.faces.new([rings[i][k], rings[i][(k + 1) % segs], rings[i + 1][(k + 1) % segs], rings[i + 1][k]])
            f.material_index = mi
            f.smooth = True
            if mb.uv is not None:
                for loop, (kk, ii) in zip(f.loops, ((k, i), (k + 1, i), (k + 1, i + 1), (k, i + 1))):
                    loop[mb.uv].uv = (kk / segs * 3.0, prof[ii][0] / 2.5)
    if prof[-1][1] > 0.001:
        f = mb.bm.faces.new(list(reversed(rings[-1])))
        f.material_index = mi


def sag_mats():
    return dict(
        stone=mat('SagradaStone', '#d8c6a2', 0.92),
        old=mat('SagradaNativity', '#ffffff', 0.95, image=make_image('nativity_carved', 128, 128, carved_fn('#b9a682', '#6e6048'))),
        passion=mat('SagradaPassion', '#d9d0bc', 0.9),
        new=mat('SagradaNew', '#cfc8b8', 0.9),
        dark=mat('SagradaDark', '#4a4336', 0.95),
        glass=mat('SagradaGlass', '#33475a', 0.15),
        bronze=mat('SagradaBronze', '#4b3d26', 0.45, 0.6),
        cypress=mat('SagradaCypress', '#3f6b3a', 0.8),
        dove=mat('SagradaDove', '#f4f2ea', 0.7),
        mosaic=trencadis_mat('Trencadis_Sagrada', ['#c8322e', '#f0c23b', '#f2efe2', '#c8322e'], 11),
        mosaic2=trencadis_mat('Trencadis_Sagrada2', ['#f0c23b', '#f2efe2', '#d9a640', '#b8322e'], 12),
        cross=mat('SagradaCross', '#f6f4ee', 0.3),          # glows at night (main.gd)
        star=mat('SagradaStar', '#f6efd8', 0.1),            # glows at night (main.gd)
        scaffold=mat('Scaffold', '#c9c9c4', 0.5, 0.6),
        hoard=mat('Hoarding', '#2f6b5a', 0.8),
        hoard2=mat('HoardingWhite', '#efece4', 0.8),
        fruit=[mat('SagFruit%d' % i, c, 0.35) for i, c in enumerate(['#e8792f', '#c8322e', '#f2c84b', '#6fae3a', '#8a3a7a'])],
    )


def spire(mb, M, base, H, r0, kind, rng):
    """A tower: a cylinder rising into a parabolic spindle, pierced by a spiral of louvres, crowned
    according to kind ('apostle', 'jesus', 'mary', 'evangelist')."""
    knee, top = 0.24 * H, (0.8 if kind == 'apostle' else 0.86) * H

    def r_at(z):
        if z <= knee:
            return r0
        f = min(1.0, (z - knee) / (top - knee))
        return max(r0 * 0.22, r0 * (1.0 - f ** 1.8) ** 0.5)
    zs = [0, knee * 0.5, knee] + [knee + (top - knee) * k / 12 for k in range(1, 13)]
    body = M['stone'] if kind == 'apostle' else M['new']
    lathe(mb, base, [(z, r_at(z)) for z in zs], 16, body)
    # louvres in a spiral
    n = 18 if kind == 'apostle' else 26
    for j in range(n):
        z = 0.1 * H + j * (top - 0.14 * H) / n
        a = j * 0.83 + rng.uniform(-0.1, 0.1)
        r = r_at(z) + 0.02
        d = Vector((math.cos(a), math.sin(a), 0))
        mb.box(base + d * r + Vector((0, 0, z)), (-d.y, d.x), (d.x, d.y), 0.09 + 0.04 * r0, 0.06, 0.45 + 0.12 * r0, M['dark'])
    rt = r_at(top)
    if kind == 'apostle':
        # the mitre pinnacle: a stem, a mosaic bulb, a tall mosaic finial pierced with holes, the ball and cross
        mb.cone(Matrix.Translation(base + Vector((0, 0, top + 0.6))), 10, rt, rt * 0.75, 1.2, M['stone'])
        mb.sphere(Matrix.Translation(base + Vector((0, 0, top + 1.8))) @ Matrix.Diagonal((1, 1, 1.25, 1)), r0 * 0.55, M['mosaic'], (12, 8))
        mb.cone(Matrix.Translation(base + Vector((0, 0, top + 3.6))), 8, r0 * 0.5, r0 * 0.12, 2.6, M['mosaic2'])
        for k in range(6):
            a = k * math.pi / 3
            mb.sphere(Matrix.Translation(base + Vector((math.cos(a) * r0 * 0.42, math.sin(a) * r0 * 0.42, top + 3.0))), 0.16, M['dove'], (6, 4))
        mb.sphere(Matrix.Translation(base + Vector((0, 0, top + 5.1))), 0.28, M_GOLD, (8, 6))
        mb.box(base + Vector((0, 0, top + 5.8)), (1, 0), (0, 1), 0.05, 0.05, 0.45, M_GOLD)
        mb.box(base + Vector((0, 0, top + 5.95)), (1, 0), (0, 1), 0.28, 0.05, 0.05, M_GOLD)
    elif kind == 'jesus':
        # a ring of lantern windows, then the white four-armed cross, lit from within at night
        for k in range(8):
            a = k * math.pi / 4
            d = Vector((math.cos(a), math.sin(a), 0))
            mb.box(base + d * (rt + 0.05) + Vector((0, 0, top - 2.5)), (-d.y, d.x), (d.x, d.y), 0.3, 0.05, 1.4, M['glass'])
        mb.cone(Matrix.Translation(base + Vector((0, 0, top + 1.0))), 12, rt, rt * 0.6, 2.0, M['new'])
        c = base + Vector((0, 0, top + 5.0))
        mb.box(c, (1, 0), (0, 1), 0.55, 0.55, 3.2, M['cross'])
        for d in ((1, 0), (0, 1)):
            mb.box(c + Vector((0, 0, 0.8)), d, (-d[1], d[0]), 2.6, 0.5, 0.55, M['cross'])
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            mb.sphere(Matrix.Translation(c + Vector((dx * 2.7, dy * 2.7, 0.8))), 0.42, M['cross'], (8, 6))
        mb.sphere(Matrix.Translation(c + Vector((0, 0, 3.4))), 0.5, M['cross'], (8, 6))
    elif kind == 'mary':
        # the twelve-pointed star of glass, lit at night
        c = base + Vector((0, 0, top + 3.0))
        mb.cone(Matrix.Translation(base + Vector((0, 0, top + 0.8))), 10, rt, rt * 0.5, 1.6, M['new'])
        mb.ico(Matrix.Translation(c), 1.3, M['star'], 1)
        for k in range(12):
            a = k * math.pi / 6
            for el in (-0.5, 0.5):
                d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
                M_ = Matrix.Translation(c + d * 1.6) @ Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
                mb.cone(M_, 4, 0.35, 0.02, 1.2, M['star'], smooth=False)
    else:
        # an evangelist: the symbol's colours on a carved crown (angel, lion, ox, eagle)
        mb.cone(Matrix.Translation(base + Vector((0, 0, top + 0.7))), 10, rt, rt * 0.8, 1.4, M['new'])
        mb.sphere(Matrix.Translation(base + Vector((0, 0, top + 2.3))) @ Matrix.Diagonal((1, 1, 1.3, 1)), r0 * 0.5, M['mosaic2'], (12, 8))
        mb.cone(Matrix.Translation(base + Vector((0, 0, top + 4.2))), 8, r0 * 0.3, 0.05, 2.2, M_GOLD)


def landmark_sagrada(ox, oy, spec):
    rng = random.Random(1882)
    M = sag_mats()
    mb = MB(uv=True)
    sc = MB(uv=True)                                   # sculpture: the Nativity's carving, the Passion's bones
    c = B(ox + BS / 2, oy + BS / 2, KERB)
    CY = SAG_CY

    def P(x, y, z=0.0):
        return c + Vector((x, y, z))

    def roof(x0, x1, y0, y1, z, peak, along_x, m):
        """A pitched roof over a rectangle, its ridge along x or y."""
        if along_x:
            ym = (y0 + y1) / 2
            for ya, yb in ((y0, ym), (y1, ym)):
                mb.face([P(x0, ya, z), P(x1, ya, z), P(x1, yb, peak), P(x0, yb, peak)], m, normal=(0, ya - ym, 1))
            for xx in (x0, x1):
                mb.face([P(xx, y0, z), P(xx, y1, z), P(xx, ym, peak)], m, normal=(xx, 0, 0))
        else:
            xm = (x0 + x1) / 2
            for xa, xb in ((x0, xm), (x1, xm)):
                mb.face([P(xa, y0, z), P(xa, y1, z), P(xb, y1, peak), P(xb, y0, peak)], m, normal=(xa - xm, 0, 1))
            for yy in (y0, y1):
                mb.face([P(x0, yy, z), P(x1, yy, z), P(xm, yy, peak)], m, normal=(0, yy, 0))

    # ---------------------------------------------------------------- the body: a Latin cross
    NAVE_W, TR_W, TR_L, FRONT, APSE_C, APSE_R = 6.8, 4.5, 12.4, -12.8, CY + 5.6, 6.8
    mb.box(P(0, (FRONT + CY - TR_W) / 2, 5.0), (1, 0), (0, 1), NAVE_W, (CY - TR_W - FRONT) / 2, 5.0, M['stone'])        # nave and aisles
    mb.box(P(0, (FRONT + CY) / 2, 8.5), (1, 0), (0, 1), 3.6, (CY - FRONT) / 2, 8.5, M['stone'])                        # the high nave
    roof(-3.8, 3.8, FRONT, CY, 17.0, 22.0, False, M['new'])
    mb.box(P(0, CY, 5.0), (1, 0), (0, 1), TR_L, TR_W, 5.0, M['stone'])                                                 # transept
    mb.box(P(0, CY, 8.5), (1, 0), (0, 1), TR_L - 0.4, 2.6, 8.5, M['stone'])
    roof(-TR_L, TR_L, CY - 2.8, CY + 2.8, 17.0, 22.0, True, M['new'])
    mb.cone(Matrix.Translation(P(0, APSE_C, 6.5)), 16, APSE_R, APSE_R, 13.0, M['stone'])                                 # the apse
    mb.cone(Matrix.Translation(P(0, APSE_C, 15.0)), 16, APSE_R, 2.0, 4.0, M['new'])
    for k in range(9):                                                                                                  # its spiky pinnacles
        a = math.pi * k / 8
        p = P(math.cos(a) * (APSE_R + 0.2), APSE_C + math.sin(a) * (APSE_R + 0.2))
        mb.cone(Matrix.Translation(p + Vector((0, 0, 9.0))), 6, 0.55, 0.05, 18.0, M['stone'])
        mb.sphere(Matrix.Translation(p + Vector((0, 0, 12.0))), 0.4, M['dove'], (6, 4))
    # nave and transept windows: tall lancets of dark glass with a bright roundel
    for side in (-1, 1):
        for k in range(4):
            y = FRONT + 2.0 + k * 3.0
            for (x, z, hz) in ((side * (NAVE_W + 0.02), 4.5, 2.6), (side * 3.62, 13.0, 2.4)):
                mb.box(P(x, y, z), (0, 1), (1, 0), 0.6, 0.04, hz, M['glass'])
                mb.sphere(Matrix.Translation(P(x + side * 0.02, y, z + hz + 0.5)), 0.42, M['fruit'][(k + (side > 0)) % 4], (8, 6))
    # buttress pinnacles along the nave, crowned with baskets of fruit
    for side in (-1, 1):
        for k in range(5):
            p = P(side * (NAVE_W + 0.4), FRONT + 0.6 + k * 3.0)
            mb.cone(Matrix.Translation(p + Vector((0, 0, 6.5))), 6, 0.55, 0.3, 13.0, M['stone'])
            for j in range(4):
                a = j * math.pi / 2 + k
                mb.sphere(Matrix.Translation(p + Vector((math.cos(a) * 0.32, math.sin(a) * 0.32, 13.4 + (j % 2) * 0.25))), 0.34,
                          M['fruit'][(j + k) % 5], (8, 6))
            mb.sphere(Matrix.Translation(p + Vector((0, 0, 13.9))), 0.38, M['fruit'][k % 5], (8, 6))

    # ---------------------------------------------------------------- the towers
    spire(mb, M, P(0, CY), 62.0, 3.4, 'jesus', rng)
    spire(mb, M, P(0, APSE_C + 0.8), 50.0, 2.6, 'mary', rng)
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        spire(mb, M, P(sx * 4.6, CY + sy * 4.0), 46.0, 2.0, 'evangelist', rng)
    for side in (-1, 1):                                    # the apostles: east over the Nativity, west over the Passion
        for (dy, H) in ((-5.0, 34.0), (-1.75, 38.0), (1.75, 38.0), (5.0, 34.0)):
            spire(mb, M, P(side * 11.0, CY + dy), H + (2.0 if side < 0 else 0.0), 1.35, 'apostle', rng)

    # ---------------------------------------------------------------- the Nativity façade (east)
    E = TR_L
    # (round 19: the porches and the carving brought down nearer the door, so that standing back across the
    # street you see them, not a tall blank arch over the door)
    mb.box(P(E - 1.1, CY, 6.0), (1, 0), (0, 1), 1.1, 6.6, 6.0, M['old'])                  # the front, the towers rising behind it
    for (dy, w, hgt) in ((-4.2, 1.9, 6.6), (0.0, 2.6, 8.6), (4.2, 1.9, 6.6)):   # Faith, Charity (the door), Hope
        for s in (-1, 1):                                                        # its carved piers, each with a pinnacle
            mb.box(P(E + 0.5, CY + dy + s * (w + 0.35), hgt / 2), (1, 0), (0, 1), 0.55, 0.35, hgt / 2, M['old'])
            mb.cone(Matrix.Translation(P(E + 0.5, CY + dy + s * (w + 0.35), hgt + 1.0)), 6, 0.45, 0.05, 2.0, M['old'])
        # the deep shadow of the portal: a tall pointed arch
        mb.face([P(E + 0.03, CY + dy - w, 0), P(E + 0.03, CY + dy + w, 0), P(E + 0.03, CY + dy + w, hgt * 0.62),
                 P(E + 0.03, CY + dy, hgt * 0.95), P(E + 0.03, CY + dy - w, hgt * 0.62)], M['dark'], normal=(1, 0, 0))
        # its gable, steep and pointed, dripping with carved stone
        Mg = Matrix.Translation(P(E + 0.6, CY + dy, hgt + 2.6)) @ Matrix.Diagonal((0.35, 1.0, 1.0, 1)) @ Matrix.Rotation(math.pi / 4, 4, 'Z')
        mb.cone(Mg, 4, (w + 0.9) * 1.41, 0.1, 5.2, M['old'], smooth=False)
        for j in range(26):
            yy = dy + rng.uniform(-w - 0.6, w + 0.6)
            zz = hgt + rng.uniform(-0.4, 3.0) * (1 - abs(yy - dy) / (w + 1.2))
            sc.sphere(Matrix.Translation(P(E + 0.9 + rng.uniform(0, 0.4), CY + yy, zz)) @ Matrix.Diagonal((0.8, 0.8, 1.3, 1)),
                      rng.uniform(0.18, 0.4), M['old'], (8, 6))
        for j in range(10):                                                      # stalactites under it
            yy = dy + rng.uniform(-w, w)
            sc.cone(Matrix.Translation(P(E + 0.75, CY + yy, hgt - 0.4)) @ Matrix.Rotation(math.pi, 4, 'X'), 6, 0.16, 0.02,
                    rng.uniform(0.6, 1.3), M['old'])
    door = P(E + 0.04, CY, 0)
    mb.box(door + Vector((0, 0, 2.1)), (0, 1), (1, 0), 1.25, 0.03, 2.1, mat('NativityDoor', '#4f6a3a', 0.5, 0.4))     # bronze, leaves and insects
    for j in range(40):                                                          # the carved stone crowding the front
        yy = rng.uniform(-6.4, 6.4)
        zz = rng.uniform(8.6, 12.2)
        sc.sphere(Matrix.Translation(P(E + 0.05 + rng.uniform(0, 0.3), CY + yy, zz)), rng.uniform(0.2, 0.55), M['old'], (8, 6))
    # the cypress, with white doves, between the two middle towers
    cyp = P(E - 0.4, CY, 0)
    lathe(mb, cyp + Vector((0, 0, 13.5)), [(0, 0.6), (1.5, 1.5), (4.0, 1.25), (6.5, 0.7), (8.5, 0.2), (9.0, 0.0)], 12, M['cypress'])
    for j in range(14):
        a = rng.uniform(0, 6.28)
        z = rng.uniform(14.5, 21.0)
        r = 1.45 * (22.5 - z) / 9.0 + 0.15
        sc.sphere(Matrix.Translation(cyp + Vector((math.cos(a) * r, math.sin(a) * r, z))) @ Matrix.Diagonal((1.4, 0.7, 0.7, 1)), 0.22, M['dove'], (6, 4))
    sc.box(cyp + Vector((0, 0, 23.0)), (1, 0), (0, 1), 0.08, 0.08, 0.6, M['dove'])                                  # the Tau cross on top
    sc.box(cyp + Vector((0, 0, 23.5)), (0, 1), (1, 0), 0.35, 0.08, 0.08, M['dove'])
    F_e = Frame((door.x, door.y), (0, 1), (1, 0))
    entrance_at(spec, F_e, 0.0, 4.2, 2.5)

    # ---------------------------------------------------------------- the Passion façade (west)
    W = -TR_L
    # (round 19: the canopy, its ribs and frieze brought down, so less blank wall over the door)
    mb.box(P(W + 1.1, CY, 6.6), (1, 0), (0, 1), 1.1, 6.6, 6.6, M['passion'])
    mb.box(P(W - 1.0, CY, 7.3), (1, 0), (0, 1), 1.1, 6.4, 0.5, M['passion'])                     # the deep canopy
    for k in range(6):                                                                              # six slanting bone columns
        y = CY - 5.0 + k * 2.0
        lean = 0.5 if k % 2 else -0.3
        a, b = P(W - 1.5 + lean, y, 0), P(W - 1.4 - lean, y, 6.9)
        sc.tube(a, b, 0.32, M['passion'], 8)
        for t in (0.0, 0.5, 1.0):                                                                   # their knuckles
            sc.sphere(Matrix.Translation(a.lerp(b, t)), 0.42, M['passion'], (8, 6))
    for k in range(18):                                                                             # the eighteen bone ribs above
        y = CY - 6.0 + k * 12.0 / 17
        sc.tube(P(W - 1.0, y, 7.8), P(W - 1.0, y, 10.7 + 0.5 * math.sin(k * 0.7)), 0.17, M['passion'], 6)
        sc.sphere(Matrix.Translation(P(W - 1.0, y, 10.8 + 0.5 * math.sin(k * 0.7))), 0.24, M['passion'], (6, 4))
    mb.box(P(W - 0.8, CY, 11.9), (1, 0), (0, 1), 0.8, 6.0, 0.7, M['passion'])
    mb.box(P(W - 0.02, CY, 5.6), (0, 1), (1, 0), 0.06, 0.06, 1.2, M['dove'])                       # the crucifix over the door
    mb.box(P(W - 0.02, CY, 6.2), (0, 1), (1, 0), 0.6, 0.06, 0.06, M['dove'])
    door = P(W - 0.04, CY, 0)
    mb.box(door + Vector((0, 0, 2.1)), (0, 1), (1, 0), 1.25, 0.03, 2.1, M['bronze'])               # the bronze doors of the Gospel
    for j in range(8):
        mb.box(door + Vector((-0.02, -1.0 + j * 0.28, 2.6)), (0, 1), (1, 0), 0.06, 0.02, 1.2, M_GOLD)
    F_w = Frame((door.x, door.y), (0, -1), (-1, 0))
    entrance_at(spec, F_w, 0.0, 4.2, 2.5)
    ENTRANCES[-1]['room_side'] = 'top'                   # (inside, the Passion door is the top one: sagrada_inside.py)

    # ---------------------------------------------------------------- the Glory façade (south): still being built
    mb.box(P(0, FRONT - 0.3, 9.0), (1, 0), (0, 1), NAVE_W, 0.3, 9.0, M['new'])
    for k in range(5):                                                                              # its bronze doors, shut
        x = -4.8 + k * 2.4
        mb.box(P(x, FRONT - 0.62, 2.0), (1, 0), (0, 1), 0.85, 0.03, 2.0, M['bronze'])
    for sx in (-4.6, 4.6):                                                                          # two tower stumps, under scaffolding
        p = P(sx, FRONT + 1.2)
        mb.cone(Matrix.Translation(p + Vector((0, 0, 12.0))), 14, 1.6, 1.5, 24.0, M['new'])
        for k in range(8):
            for (dx, dy) in ((-2, -2), (2, -2), (2, 2), (-2, 2)):
                mb.tube(p + Vector((dx, dy, k * 3.0)), p + Vector((dx, dy, k * 3.0 + 3.0)), 0.05, M['scaffold'], 4)
            mb.box(p + Vector((0, 0, k * 3.0 + 3.0)), (1, 0), (0, 1), 2.1, 2.1, 0.05, M_WOODEN)
    for k in range(7):                                                                              # scaffolding over the front
        for j in range(5):
            mb.tube(P(-6.6 + k * 2.2, FRONT - 1.0, j * 3.6), P(-6.6 + k * 2.2, FRONT - 1.0, j * 3.6 + 3.6), 0.05, M['scaffold'], 4)
            mb.tube(P(-6.6, FRONT - 1.0, j * 3.6 + 3.6), P(6.6, FRONT - 1.0, j * 3.6 + 3.6), 0.04, M['scaffold'], 4)
    for k in range(8):                                                                              # the hoardings: no way in here
        x = -7.0 + k * 2.0
        mb.box(P(x + 1.0, FRONT - 1.6, 1.25), (1, 0), (0, 1), 0.98, 0.05, 1.25, M['hoard'] if k % 2 else M['hoard2'])
    # two tower cranes
    for (cx_, cy_, h, col, arm) in ((-9.5, FRONT + 3.0, 50.0, '#f0c23b', 0.6), (9.0, APSE_C + 1.0, 44.0, '#d9533f', 2.4)):
        cr = P(cx_, cy_)
        cm = mat('Crane' + col, col, 0.5, 0.3)
        mb.box(cr + Vector((0, 0, h / 2)), (1, 0), (0, 1), 0.4, 0.4, h / 2, cm)
        d = Vector((math.cos(arm), math.sin(arm), 0))
        mb.box(cr + d * 6.0 + Vector((0, 0, h + 0.5)), (d.x, d.y), (-d.y, d.x), 14.0, 0.5, 0.5, cm)
        mb.box(cr - d * 6.5 + Vector((0, 0, h - 0.4)), (d.x, d.y), (-d.y, d.x), 1.0, 1.0, 0.8, mat('Counterweight', '#7a7a76', 0.8))
        mb.box(cr + Vector((0, 0, h - 2.5)), (1, 0), (0, 1), 1.0, 1.0, 1.0, cm)

    city_objs.append(mb.finish('Landmark_sagrada'))
    city_objs.append(sc.finish('Landmark_sagrada_sculpture'))
    # what can't be walked through: the church, its façade blocks and porticos, the hoardings
    def rect(x0, y0, x1, y1):
        return [bl_m(P(x0, y0)), bl_m(P(x1, y0)), bl_m(P(x1, y1)), bl_m(P(x0, y1))]
    solids = [rect(-NAVE_W, FRONT, NAVE_W, CY), rect(-TR_L, CY - TR_W, TR_L, CY + TR_W),
              rect(E - 2.2, CY - 6.6, E, CY + 6.6), rect(W, CY - 6.6, W + 2.2, CY + 6.6),
              rect(-7.2, FRONT - 1.7, 7.2, FRONT), rect(-10.1, FRONT + 2.4, -8.9, FRONT + 3.6), rect(8.4, APSE_C + 0.4, 9.6, APSE_C + 1.6)]
    solids.append([bl_m(P(math.cos(a) * APSE_R, APSE_C + math.sin(a) * APSE_R)) for a in [math.pi * k / 8 for k in range(9)]])
    for dy in (-4.2, 0.0, 4.2):                                           # the Nativity's portal piers
        for s in (-1, 1):
            w = 2.6 if dy == 0 else 1.9
            y = CY + dy + s * (w + 0.35)
            solids.append(rect(E, y - 0.35, E + 1.05, y + 0.35))
    for k in range(6):                                                    # the Passion's columns, where they stand
        # (round 35, the second look: as they lean — the solid was only round the foot, and the camera, which these
        # also stop, went into a column's knuckles higher up; it now spans the foot to the head, and their 0.42 knuckles)
        y = CY - 5.0 + k * 2.0
        lean = 0.5 if k % 2 else -0.3
        xa, xb = W - 1.5 + lean, W - 1.4 - lean
        solids.append(rect(min(xa, xb) - 0.42, y - 0.42, max(xa, xb) + 0.42, y + 0.42))
    for blk in scene['blocks']:
        if blk['origin'] == [ox, oy]:
            blk['solids'] = solids
