# Inside the Sagrada Família: a forest of stone. Walked round with the street camera (free_cam), so
# Sandra can look up into it. Laid out as the real basilica, seen from the Nativity door:
#   the room's x runs along the nave: the Glory end (south, its bronze doors shut) on the left, the
#   apse (north) on the right, where the altar stands under its hanging canopy;
#   the room's y runs across the transept: the Passion door (west) at the top, the Nativity door (east,
#   where Sandra comes in) at the bottom. Both are ways in and out, as outside.
#   - Gaudí's tree columns: star-shaped trunks that twist two ways as they rise until they are round,
#     a knot, then branches spreading up to hold the vault; the four great columns of red porphyry at
#     the crossing, under the tower of Jesus
#   - the vaults: hyperboloids like leaves or palm crowns, their centres open to the light
#   - the stained glass: cool blues and greens on the Nativity side (morning), warm reds and oranges on
#     the Passion side (evening), golds in the apse
#   - the nave twice as high as the aisles, the crossing higher still, as in the real one (scaled down)
# Exec'd from interiors.py; build_sagrada_room() replaces the 2D room for int_sagrada.

SG_W, SG_H = 34, 24                  # metres: along the nave, across the transept
SG_NAVE = (8.5, 15.5)                # the nave's column rows (room y)
SG_AISLE = (4.8, 19.2)               # the aisles' column rows
SG_CROSS = (18.5, 25.5)              # the crossing (room x)
SG_DOOR = (20.5, 23.5)               # both doors, in the middle of the transept ends
Z_AISLE, Z_NAVE, Z_CROSS = 13.0, 21.0, 29.0


def build_sagrada_room(rid, R, k):
    ox = k * ROOM_GAP
    rng = random.Random(1926)
    mb, glass, deco = MB(uv=True), MB(uv=True), MB(uv=True)
    W, H = SG_W, SG_H
    stone = mat('SgStone', '#e9e1d0', 0.85)
    stone2 = mat('SgStoneWarm', '#ddd0b4', 0.85)
    knot_m = mat('SgKnot', '#cdb98a', 0.6, 0.15)
    basalt = mat('SgBasalt', '#5c5a58', 0.5)
    porphyry = mat('SgPorphyry', '#8a3a30', 0.35)
    vault_m = mat('SgVault', '#f2ece0', 0.8)
    leaf_m = trencadis_mat('SgVaultLeaf', ['#9fbf6a', '#d8c070', '#f4f0e0', '#7aa860'], 31)
    light_m = mat('VaultLight', '#fff2c8', 0.2)          # glows (main.gd)
    floor_m = mat('SgFloor', '#ffffff', 0.35, image=make_image('sg_floor', 64, 64, lambda x, y: (
        (0.86, 0.82, 0.74) if ((x // 16 + y // 16) % 2) else (0.8, 0.76, 0.68))))
    wood = mat('SgPew', '#8a5d3b', 0.6)
    bronze = mat('SagradaBronze', '#4b3d26', 0.45, 0.6)
    gilt = mat('Gilt', '#d4a640', 0.35, 0.8)
    COOL = ['#2f6ab0', '#3aa0a0', '#5cb85c', '#2f4f8f', '#7ac8d8', '#1f8a6a']
    WARM = ['#d9533f', '#f0a030', '#f2c84b', '#c8322e', '#e87a2f', '#b8322e']
    GOLD = ['#f2c84b', '#f0e0a0', '#e8a83a', '#fff0c0']

    def Pt(x, y, z=0.0):
        return Vector((ox + x, -y, z))

    def quad(a, b, c_, d, m, nrm, to=None):
        (to or mb).face([a, b, c_, d], m, normal=nrm)

    # ---------------------------------------------------------------- floor, walls, ceilings
    quad(Pt(0.8, 0.8), Pt(W - 0.8, 0.8), Pt(W - 0.8, H + 0.2), Pt(0.8, H + 0.2), floor_m, (0, 0, 1))
    walls = [(Pt(1, 1), Pt(W - 1, 1), (0, -1, 0)), (Pt(W - 1, H), Pt(1, H), (0, 1, 0)),
             (Pt(1, H), Pt(1, 1), (1, 0, 0)), (Pt(W - 1, 1), Pt(W - 1, H), (-1, 0, 0))]
    for (a, b, nrm) in walls:
        top = Z_NAVE
        if a.y == b.y:                                           # the two transept ends: open at the doors
            x0, x1 = min(a.x, b.x) - ox, max(a.x, b.x) - ox
            y = -a.y
            for (s0, s1) in ((x0, SG_DOOR[0]), (SG_DOOR[1], x1)):
                quad(Pt(s0, y, 0), Pt(s1, y, 0), Pt(s1, y, top), Pt(s0, y, top), stone, nrm)
            quad(Pt(SG_DOOR[0], y, 5.0), Pt(SG_DOOR[1], y, 5.0), Pt(SG_DOOR[1], y, top), Pt(SG_DOOR[0], y, top), stone, nrm)
        else:
            quad(a, b, b + Vector((0, 0, top)), a + Vector((0, 0, top)), stone, nrm)

    # the doorways (round 20: from inside they were black holes): a corridor out to a bright opening, the
    # day outside (DoorDaylight glows; main.gd turns it to dusk blue at night). Round 21, the user: a small
    # corridor with the light at its end, never a space she walks into: it is 3.5 m deep to look down, but she
    # is outside as soon as she steps over the threshold (main.gd stops her just past it)
    day_m = mat('DoorDaylight', '#fff4dc', 0.9)
    d0, d1 = SG_DOOR
    for (yw, out, nrm) in ((1.0, -1.0, (0, -1, 0)), (H, 1.0, (0, 1, 0))):
        yb = yw + out * 3.5
        quad(Pt(d0, yw, 0), Pt(d0, yb, 0), Pt(d0, yb, 5.0), Pt(d0, yw, 5.0), stone, (1, 0, 0))
        quad(Pt(d1, yb, 0), Pt(d1, yw, 0), Pt(d1, yw, 5.0), Pt(d1, yb, 5.0), stone, (-1, 0, 0))
        quad(Pt(d0, yw, 5.0), Pt(d1, yw, 5.0), Pt(d1, yb, 5.0), Pt(d0, yb, 5.0), stone, (0, 0, -1))
        quad(Pt(d0, yw, 0.01), Pt(d1, yw, 0.01), Pt(d1, yb, 0.01), Pt(d0, yb, 0.01), floor_m, (0, 0, 1))
        quad(Pt(d0, yb, 0), Pt(d1, yb, 0), Pt(d1, yb, 5.0), Pt(d0, yb, 5.0), day_m, nrm)
        for xs in (d0, d1):                                       # bronze door frames
            mb.box(Pt(xs, yw, 2.5), (1, 0), (0, 1), 0.08, 0.12, 2.5, bronze)

    def ceiling(x0, y0, x1, y1, z):
        quad(Pt(x0, y0, z), Pt(x1, y0, z), Pt(x1, y1, z), Pt(x0, y1, z), vault_m, (0, 0, -1))

    def screen(x0, y0, x1, y1, z0, z1, nrm):
        quad(Pt(x0, y0, z0), Pt(x1, y1, z0), Pt(x1, y1, z1), Pt(x0, y0, z1), stone, nrm)
    n0, n1 = SG_NAVE
    c0, c1 = SG_CROSS
    for (y0, y1) in ((1, n0), (n1, H)):                         # the aisles, low; the transept arms, high
        ceiling(1, y0, c0, y1, Z_AISLE)
        ceiling(c1, y0, W - 1, y1, Z_AISLE)
        ceiling(c0, y0, c1, y1, Z_NAVE)
        screen(c0, y0, c0, y1, Z_AISLE, Z_NAVE, (1, 0, 0))
        screen(c1, y1, c1, y0, Z_AISLE, Z_NAVE, (-1, 0, 0))
    ceiling(1, n0, c0, n1, Z_NAVE)                              # the nave and the apse, high
    ceiling(c1, n0, W - 1, n1, Z_NAVE)
    ceiling(c0, n0, c1, n1, Z_CROSS)                            # the crossing, under Jesus's tower, highest
    for (x0, x1) in ((1, c0), (c1, W - 1)):                    # the clerestory walls over the aisles
        screen(x0, n0, x1, n0, Z_AISLE, Z_NAVE, (0, -1, 0))
        screen(x1, n1, x0, n1, Z_AISLE, Z_NAVE, (0, 1, 0))
    screen(c0, n0, c1, n0, Z_NAVE, Z_CROSS, (0, -1, 0))        # the lantern round the crossing
    screen(c1, n1, c0, n1, Z_NAVE, Z_CROSS, (0, 1, 0))
    screen(c0, n1, c0, n0, Z_NAVE, Z_CROSS, (1, 0, 0))
    screen(c1, n0, c1, n1, Z_NAVE, Z_CROSS, (-1, 0, 0))

    # ---------------------------------------------------------------- stained glass (glowing panes)
    def window(x0, x1, y, z0, z1, pal, inward, cells=(3, 8)):
        """A tall window of coloured panes in the wall at room y (inward: +1 if the room is at larger y)."""
        nx, nz = cells
        d = 0.04 * inward
        for i in range(nx):
            for j in range(nz):
                a0, a1 = x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx
                b0, b1 = z0 + (z1 - z0) * j / nz, z0 + (z1 - z0) * (j + 1) / nz
                m = mat('Stained' + pal[(i * 3 + j * 5 + rng.randrange(2)) % len(pal)], pal[(i * 3 + j * 5) % len(pal)], 0.1)
                quad(Pt(a0 + 0.04, y + d, b0 + 0.04), Pt(a1 - 0.04, y + d, b0 + 0.04), Pt(a1 - 0.04, y + d, b1 - 0.04),
                     Pt(a0 + 0.04, y + d, b1 - 0.04), m, (0, -inward, 0), glass)
        # a pointed head of stone tracery over it
        quad(Pt(x0 - 0.15, y + d * 1.5, z1), Pt(x1 + 0.15, y + d * 1.5, z1), Pt((x0 + x1) / 2, y + d * 1.5, z1 + (x1 - x0) * 0.7),
             Pt((x0 + x1) / 2, y + d * 1.5, z1 + (x1 - x0) * 0.7), stone2, (0, -inward, 0), deco)

    def rose(cx, y, cz, r, pal, inward):
        d = 0.05 * inward
        for ring in range(4):
            r0, r1 = r * ring / 4, r * (ring + 1) / 4
            n = 6 + ring * 6
            for i in range(n):
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 0.86) / n
                m = mat('Stained' + pal[(i + ring) % len(pal)], pal[(i + ring) % len(pal)], 0.1)
                pts = [Pt(cx + math.cos(a0) * r0, y + d, cz + math.sin(a0) * r0), Pt(cx + math.cos(a0) * r1, y + d, cz + math.sin(a0) * r1),
                       Pt(cx + math.cos(a1) * r1, y + d, cz + math.sin(a1) * r1), Pt(cx + math.cos(a1) * r0, y + d, cz + math.sin(a1) * r0)]
                glass.face(pts, m, normal=(0, -inward, 0))
    for x in [3.0, 7.0, 11.0, 15.0, 28.0, 31.0]:
        window(x - 0.8, x + 0.8, 1.0, 2.5, 10.0, WARM, +1)              # the Passion side (west): sunset
        window(x - 0.8, x + 0.8, H, 2.5, 10.0, COOL, -1)                # the Nativity side (east): dawn
        window(x - 0.7, x + 0.7, n0, Z_AISLE + 1.0, Z_NAVE - 2.6, WARM, +1, (2, 5))
        window(x - 0.7, x + 0.7, n1, Z_AISLE + 1.0, Z_NAVE - 2.6, COOL, -1, (2, 5))
    for x in (c0 + 1.5, c1 - 1.5):
        window(x - 0.8, x + 0.8, 1.0, 5.6, 9.5, WARM, +1, (2, 4))
        window(x - 0.8, x + 0.8, H, 5.6, 9.5, COOL, -1, (2, 4))
    rose((c0 + c1) / 2, 1.0, 13.5, 3.0, WARM, +1)                   # the rose windows over both doors
    rose((c0 + c1) / 2, H, 13.5, 3.0, COOL, -1)
    for y in (6.0, 10.0, 14.0, 18.0):                                # the apse: gold
        for (a, b) in ((y - 0.8, y + 0.8),):
            for j in range(8):
                m = mat('Stained' + GOLD[j % 4], GOLD[j % 4], 0.1)
                quad(Pt(W - 1.04, a, 3 + j * 1.6), Pt(W - 1.04, b, 3 + j * 1.6), Pt(W - 1.04, b, 4.5 + j * 1.6), Pt(W - 1.04, a, 4.5 + j * 1.6),
                     m, (-1, 0, 0), glass)

    # ---------------------------------------------------------------- the tree columns
    def oriented(a, b):
        d = b - a
        return Matrix.Translation((a + b) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4(), d.length

    def tree_column(x, y, knee, r0, m, branches, reach, top, points=8):
        base = Pt(x, y)
        mb.cone(Matrix.Translation(base + Vector((0, 0, 0.2))), 16, r0 * 1.45, r0 * 1.25, 0.4, basalt)   # the basalt foot
        rings = []
        segs = 32
        nz = 14
        for j in range(nz + 1):
            z = 0.4 + (knee - 0.4) * j / nz
            f = j / nz
            amp = 0.2 * (1 - f) ** 0.8                        # the star softens into a round shaft as it rises
            tw = f * math.pi / points                           # twisting both ways at once (Gaudí's double twist)
            ring = []
            for i in range(segs):
                th = 2 * math.pi * i / segs
                rr = r0 * (1 - 0.12 * f) * (1 + amp * max(math.cos(points * (th + tw)), math.cos(points * (th - tw))))
                ring.append(mb.bm.verts.new(base + Vector((math.cos(th) * rr, math.sin(th) * rr, z))))
            rings.append(ring)
        mi = mb.mi(m)
        for j in range(nz):
            for i in range(segs):
                f = mb.bm.faces.new([rings[j][i], rings[j][(i + 1) % segs], rings[j + 1][(i + 1) % segs], rings[j + 1][i]])
                f.material_index = mi
                f.smooth = True
        # the knot, where it branches
        kz = knee + r0 * 0.9
        mb.sphere(Matrix.Translation(base + Vector((0, 0, kz))) @ Matrix.Diagonal((1, 1, 1.35, 1)), r0 * 1.25, knot_m, (16, 10))
        for b in range(branches):
            a = 2 * math.pi * b / branches + math.pi / 4
            tip = base + Vector((math.cos(a) * reach, math.sin(a) * reach, top - 0.6))
            M_, L = oriented(base + Vector((0, 0, kz + r0 * 0.6)), tip)
            mb.cone(M_, 12, r0 * 0.55, r0 * 0.32, L, m)
            mb.sphere(Matrix.Translation(tip), r0 * 0.42, knot_m, (10, 6))
        # a central shaft carries on up to the vault
        M_, L = oriented(base + Vector((0, 0, kz + r0 * 1.0)), base + Vector((0, 0, top)))
        mb.cone(M_, 12, r0 * 0.6, r0 * 0.45, L, m)

    solids = []
    posts = []                                                       # the columns: round, as wide as their basalt feet
    nave_x = [4.0, 8.0, 12.0, 16.0, 28.0, 31.0]
    for x in nave_x:
        for y in (n0, n1):
            tree_column(x, y, 9.0, 0.42, stone2, 4, 1.7, Z_NAVE, 8)
            posts.append([x, y, 0.42 * 1.45])
        for y in SG_AISLE:
            tree_column(x, y, 6.0, 0.32, stone, 4, 1.3, Z_AISLE, 6)
            posts.append([x, y, 0.32 * 1.45])
    for x in (c0, c1):                                               # the crossing: red porphyry, the largest
        for y in (n0, n1):
            tree_column(x, y, 12.0, 0.7, porphyry, 6, 2.6, Z_NAVE, 12)
            posts.append([x, y, 0.7 * 1.45])
    for x in (c0 + 1.2, c1 - 1.2):                                  # and up the transept arms
        for y in (SG_AISLE[0], SG_AISLE[1]):
            tree_column(x, y, 9.0, 0.42, stone2, 4, 1.7, Z_NAVE, 8)
            posts.append([x, y, 0.42 * 1.45])

    # ---------------------------------------------------------------- the vaults: hyperboloids open to the light
    def hyperboloid(x, y, z, r, rim=None):
        base = Pt(x, y, z)
        prof = [(0.0, r), (-0.35 * r, r * 0.62), (-0.6 * r, r * 0.38), (-0.68 * r, r * 0.27)]
        rings = []
        segs = 20
        for (dz, rr) in prof:
            rings.append([deco.bm.verts.new(base + Vector((math.cos(2 * math.pi * i / segs) * rr, math.sin(2 * math.pi * i / segs) * rr, dz)))
                          for i in range(segs)])
        mi = deco.mi(leaf_m)
        for j in range(len(rings) - 1):
            for i in range(segs):
                f = deco.bm.faces.new([rings[j][i], rings[j + 1][i], rings[j + 1][(i + 1) % segs], rings[j][(i + 1) % segs]])
                f.material_index = mi
                f.smooth = True
                for loop, (uu, vv) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                    loop[deco.uv].uv = (uu / segs * 2.0, vv / 3.0)
        # the light at its heart
        deco.cone(Matrix.Translation(base + Vector((0, 0, -0.68 * r + 0.01))), segs, r * 0.27, r * 0.27, 0.02, light_m)
    for x in (2.2, 6.0, 10.0, 14.0, 29.5, 32.0):
        hyperboloid(x, (n0 + n1) / 2, Z_NAVE, 2.0)
        for y in ((1 + n0) / 2 + 0.6, (n1 + H) / 2 - 0.6):
            hyperboloid(x, y, Z_AISLE, 1.3)
        for y in (n0 + 1.0, n1 - 1.0):
            hyperboloid(x, y, Z_NAVE, 0.9)
    for y in ((1 + n0) / 2, (n1 + H) / 2):
        hyperboloid((c0 + c1) / 2, y, Z_NAVE, 2.0)
    hyperboloid((c0 + c1) / 2, (n0 + n1) / 2, Z_CROSS, 3.2)         # under Jesus's tower: the great lantern
    for (dx, dy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        hyperboloid((c0 + c1) / 2 + dx * 2.4, (n0 + n1) / 2 + dy * 2.4, Z_CROSS, 1.0)

    # ---------------------------------------------------------------- the apse: the altar, its canopy, the organ
    ax, ay = 29.5, (n0 + n1) / 2
    mb.box(Pt(ax, ay, 0.15), (1, 0), (0, 1), 1.6, 2.6, 0.15, stone2)                        # the step
    mb.box(Pt(ax, ay, 0.75), (1, 0), (0, 1), 0.7, 1.3, 0.45, porphyry)                      # the altar
    mb.box(Pt(ax, ay, 1.22), (1, 0), (0, 1), 0.78, 1.4, 0.03, mat('AltarCloth', '#f4f0e8', 0.8))
    solids.append([ax - 1.0, ay - 1.6, ax + 1.0, ay + 1.6])
    can = Pt(ax, ay, 8.5)                                                                  # the heptagonal canopy
    mb.cone(Matrix.Translation(can), 7, 2.4, 2.0, 0.6, mat('Baldachin', '#e8e0c8', 0.6))
    for i in range(7):
        a = 2 * math.pi * i / 7
        mb.tube(can + Vector((math.cos(a) * 1.4, math.sin(a) * 1.4, 0.3)), can + Vector((0, 0, Z_NAVE - 8.8)), 0.03, M_IRON, 4)
        for j in range(3):                                                                  # its hanging lamps and grapes
            p = can + Vector((math.cos(a) * 2.2, math.sin(a) * 2.2, -0.6 - j * 0.35))
            deco.sphere(Matrix.Translation(p), 0.09, light_m if j == 2 else mat('Grapes', '#5a2a5a', 0.4), (6, 4))
        deco.tube(can + Vector((math.cos(a) * 2.2, math.sin(a) * 2.2, -0.3)), can + Vector((math.cos(a) * 2.2, math.sin(a) * 2.2, -1.3)), 0.01, M_IRON, 3)
    cr = Pt(ax, ay, 5.6)                                                                   # the crucifix hanging beneath
    deco.box(cr, (1, 0), (0, 1), 0.05, 0.05, 1.1, mat('CrossWood', '#6a4a30', 0.6))
    deco.box(cr + Vector((0, 0, 0.55)), (0, 1), (1, 0), 0.75, 0.05, 0.05, mat('CrossWood', '#6a4a30', 0.6))
    deco.box(cr + Vector((0.07, 0, 0.0)), (0, 1), (1, 0), 0.12, 0.05, 0.5, mat('Figure', '#e8d8b8', 0.6))
    for j in range(20):                                                                    # the organ, round the apse
        x = 26.6 + j * 0.3
        for y in (1.4, H - 0.4):
            deco.cone(Matrix.Translation(Pt(x, y, 7.0 + (j % 5) * 0.4)), 8, 0.08, 0.08, 4.0 + (j % 5) * 0.8, gilt)

    # ---------------------------------------------------------------- the Glory end: its bronze doors, shut
    for (y0, y1) in ((n0 + 0.6, (n0 + n1) / 2 - 0.1), ((n0 + n1) / 2 + 0.1, n1 - 0.6)):
        quad(Pt(1.03, y1, 0), Pt(1.03, y0, 0), Pt(1.03, y0, 6.0), Pt(1.03, y1, 6.0), bronze, (1, 0, 0), deco)
        for j in range(16):                                                                # the Lord's Prayer, in fifty languages
            z = 0.6 + j * 0.33
            quad(Pt(1.05, y1 - 0.2, z), Pt(1.05, y0 + 0.2, z), Pt(1.05, y0 + 0.2, z + 0.06), Pt(1.05, y1 - 0.2, z + 0.06), gilt, (1, 0, 0), deco)
    # scaffolding, and Gaudí's hanging-chain model, by the Glory end
    for (lx, ly) in ((2.0, 20.0), (4.0, 20.0), (2.0, 22.0), (4.0, 22.0)):
        mb.tube(Pt(lx, ly, 0), Pt(lx, ly, 9.0), 0.05, mat('Scaffold', '#c9c9c4', 0.5, 0.6), 4)
    for z in (2.5, 5.0, 7.5):
        mb.box(Pt(3.0, 21.0, z), (1, 0), (0, 1), 1.1, 1.1, 0.04, M_WOOD)
    solids.append([1.6, 19.6, 4.4, 22.4])
    mb.box(Pt(3.0, 3.0, 0.5), (1, 0), (0, 1), 0.6, 0.6, 0.5, M_WOOD)                         # the model's table
    for j in range(9):
        a = j * 0.7
        deco.tube(Pt(3.0 + math.cos(a) * 0.4, 3.0 + math.sin(a) * 0.4, 1.0), Pt(3.0, 3.0, 2.3), 0.012, mat('ModelPlaster', '#f2eee4', 0.8), 3)
    solids.append([2.3, 2.3, 3.7, 3.7])

    # ---------------------------------------------------------------- pews down the nave
    for x in [3.0 + i * 1.25 for i in range(11)]:
        if any(abs(x - cx) < 0.7 for cx in nave_x):
            continue
        for (y0, y1) in ((n0 + 1.0, 11.4), (12.6, n1 - 1.0)):
            mb.box(Pt(x, (y0 + y1) / 2, 0.42), (1, 0), (0, 1), 0.22, (y1 - y0) / 2, 0.04, wood)
            mb.box(Pt(x + 0.24, (y0 + y1) / 2, 0.7), (1, 0), (0, 1), 0.04, (y1 - y0) / 2, 0.3, wood)
            for yy in (y0 + 0.05, y1 - 0.05):
                mb.box(Pt(x, yy, 0.21), (1, 0), (0, 1), 0.22, 0.04, 0.21, wood)
            solids.append([x - 0.25, y0, x + 0.3, y1])

    root = bpy.data.objects.new('Interior_' + rid, None)
    bpy.context.scene.collection.objects.link(root)
    parts = [mb.finish('Room_' + rid), glass.finish('Glass_' + rid), deco.finish('Deco_' + rid)]
    for ob in parts:
        ob.parent = root
    INT_ROOTS.append(root)

    # what can be looked at: the 2D game's words where it has them, and a few more
    objs = {o[0]: (o[3] if len(o) > 3 else {}) for o in R['objs']}
    glass_t = [o[3]['t'] for o in R['objs'] if o[0] == 'glass']
    things = [
        dict(kind='glass', t=glass_t[0], pos=[11.0, H - 1.0]),
        dict(kind='glass', t=glass_t[1], pos=[11.0, 2.0]),
        dict(kind='altar', t=objs['altar']['t'], pos=[ax - 1.3, ay]),
        dict(kind='model', t=objs['model']['t'], pos=[3.0, 4.0]),
        dict(kind='scaffold', t=objs['scaffold']['t'], pos=[4.8, 21.0]),
        dict(kind='glorydoor', t="The Glory doors, cast in bronze and shut for now: the Lord's Prayer runs across them in fifty languages, "
             "with 'Give us this day our daily bread' picked out in Catalan. One day they'll open onto the great stair down to Carrer de Mallorca.",
             pos=[1.8, (n0 + n1) / 2]),
        dict(kind='porphyry', t="One of the four great columns of red porphyry at the crossing, holding up the towers of the evangelists. "
             "Each column here is a different stone: the harder the stone, the more it has to carry.", pos=[c0 + 1.2, n1 + 0.9]),
        dict(kind='treecol', t="The columns rise like trees: star-shaped at the foot, twisting both ways at once as they climb until they are round, "
             "then branching out to hold up a canopy of stone. Gaudí wanted you to feel you were standing in a forest.", pos=[8.0 + 0.9, n1 + 0.9]),
    ]
    npcs = [nid for nid, n in W2['NPCS'].items() if n['at'][0] == rid]
    tinted = []
    for x in (5.0, 12.0, 29.0):
        tinted.append([ox + x, 6.0, H - 2.0, 0.45, 0.7, 1.0, 1.4, 11.0])        # dawn blues on the Nativity side
        tinted.append([ox + x, 6.0, 2.5, 1.0, 0.6, 0.35, 1.4, 11.0])           # sunset oranges on the Passion side
    tinted.append([ox + (c0 + c1) / 2, Z_CROSS - 3.0, (n0 + n1) / 2, 1.0, 0.93, 0.75, 2.5, 26.0])   # the light from the lantern
    tinted.append([ox + W - 3.0, 9.0, ay, 1.0, 0.85, 0.5, 1.5, 12.0])                                # the golden apse
    # sunbeams through the glass (the game draws them as soft shafts with a pool of coloured light where
    # they land, and brings each side's out at its time of day): p, d (engine x, up, z), r0, r1, length
    beams = []

    def beam(p, d, r0, r1, L, col, side, spot):
        n_ = math.sqrt(sum(c * c for c in d))
        beams.append({'p': [round(v, 3) for v in p], 'd': [round(c / n_, 4) for c in d], 'r0': r0, 'r1': r1, 'len': L,
                      'col': col, 'side': side, 'spot': spot})
    warm_cols = [[1.0, 0.55, 0.28], [1.0, 0.72, 0.32], [0.95, 0.42, 0.3]]
    cool_cols = [[0.42, 0.68, 1.0], [0.4, 0.9, 0.72], [0.5, 0.62, 1.0]]
    for j, x in enumerate([3.0, 7.0, 11.0, 15.0, 28.0, 31.0]):
        beam([ox + x, 6.6, 1.3], [0.3, -0.62, 0.72], 0.75, 1.7, 12.0, warm_cols[j % 3], 'west', True)
        beam([ox + x, 6.6, H - 0.3], [0.3, -0.62, -0.72], 0.75, 1.7, 12.0, cool_cols[j % 3], 'east', True)
        beam([ox + x, 16.5, n0 + 0.2], [0.25, -0.78, 0.55], 0.6, 1.5, 15.0, warm_cols[(j + 1) % 3], 'west', False)
        beam([ox + x, 16.5, n1 - 0.2], [0.25, -0.78, -0.55], 0.6, 1.5, 15.0, cool_cols[(j + 1) % 3], 'east', False)
    beam([ox + (c0 + c1) / 2, 13.5, 1.3], [0.2, -0.45, 0.85], 2.4, 3.6, 13.0, [1.0, 0.6, 0.35], 'west', True)        # the rose windows
    beam([ox + (c0 + c1) / 2, 13.5, H - 0.3], [0.2, -0.45, -0.85], 2.4, 3.6, 13.0, [0.45, 0.72, 1.0], 'east', True)
    beam([ox + (c0 + c1) / 2, Z_CROSS - 2.2, (n0 + n1) / 2], [0.0, -1.0, 0.0], 0.9, 2.8, 27.0, [1.0, 0.92, 0.72], 'day', True)   # the lantern
    for y in (6.0, 10.0, 14.0, 18.0):
        beam([ox + W - 1.3, 9.0, y], [-0.75, -0.62, 0.0], 0.7, 1.5, 9.0, [1.0, 0.82, 0.45], 'day', y in (10.0, 14.0))   # the apse's gold
    return {'name': R['name'], 'offset': [ox, 0], 'w': W, 'h': H, 'floor': [1, 1, W - 1, H],
            'exit': [SG_DOOR[0], SG_DOOR[1]], 'exit_top': [SG_DOOR[0], SG_DOOR[1]], 'spawn': [(c0 + c1) / 2, H - 1.5],
            'free_cam': True, 'solids': solids, 'posts': posts, 'things': things, 'stairs': [], 'npcs': npcs, 'wall_h': Z_NAVE,
            'lights': {'ceiling': [ox + W / 2, Z_NAVE - 4.0, H / 2], 'windows': [], 'lamps': [], 'tinted': tinted, 'beams': beams},
            'shop': False, 'kind': 'sacred'}
