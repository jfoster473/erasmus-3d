# The north (round 22): built from north.py's layout. exec'd by world2d.py once the ground is made (and by
# preview_north.py on its own), sharing build_assets.py's helpers (MB, Cards, mat, make_image, text_obj, the M_*
# materials). Everything here is in the engine's metres: V(x, z, h) is a point (x east, z south, h up).
#   the funfair     on its terrace 78 m up: the Temple del Sagrat Cor (crypt, upper church, four corner towers,
#                   the tall central one with Christ on top), the Giradabo (a wheel the game turns: WheelRim, its
#                   gondolas WheelGondola_*), the Talaia, the Avió (AvioArm, turned by the game), the Carrusel
#                   (CarruselTop), the Museu d'Autòmats, railings, a retaining wall where the slope falls away
#   the cable car   its two stations, pylons, cables and two cabins (CableCabin_0/1, moved by the game)
#   the path        a trodden ribbon on its bench, the workmen's barrier and their work site (PathWorks_*)
#   Gràcia          small blocks of terraced houses, a square with a plane tree, the street up to the park
#   Park Güell      its wall and gate, the two lodges, the dragon stairs, the Hypostyle Room's colonnade, the
#                   Nature Square and its wavy bench, the Pòrtic de la Bugadera, the Casa Museu Gaudí, Casa Trias
# It appends to city_objs, scene['blocked'] (solid rectangles), scene['north'] (what the game needs) and
# scene['entrances'] (the new doors).
import math, random, sys
from mathutils import Vector, Matrix

sys.path.insert(0, BUILD)
import north as N
importlib_reload = __import__('importlib').reload
importlib_reload(N)

nr = random.Random(2222)


def V(x, z, h=0.0):
    return Vector((x, -z, h))


def hz(x, z):
    """The ground's height here (the grid world2d made, if there is one; else north.py's own)."""
    return north_ground(x, z) if 'north_ground' in globals() else N.ground(x, z)


def finish_at(mb, name, pivot):
    """A part the game moves: its origin at the pivot (engine metres), not at the world's."""
    ob = mb.finish(name)
    pv = Vector((pivot[0], -pivot[1], pivot[2]))
    for v in ob.data.vertices:
        v.co -= pv
    ob.location = pv
    return ob


def solid(x0, z0, x1, z1):
    scene['blocked'].append([round(min(x0, x1), 3), round(min(z0, z1), 3), round(max(x0, x1), 3), round(max(z0, z1), 3)])


def cam_building(x0, z0, x1, z1, lo, hi):
    """(round 40, rule 03 #16) a building on the hills, for the camera alone, where it really stands: lo to hi metres. The
    camera's walls are named, never found by size: only what is listed here (and the city's blocks) brings it in."""
    scene.setdefault('cam_buildings', []).append({'r': [round(min(x0, x1), 2), round(min(z0, z1), 2), round(max(x0, x1), 2),
                                                        round(max(z0, z1), 2)], 'lo': round(lo, 2), 'hi': round(hi, 2)})


def solid_box(cx, cz, w, d, ang=0.0):
    # (a turned box as the rectangle round it, made smaller so it doesn't stand out past the walls much)
    c, s = abs(math.cos(ang)), abs(math.sin(ang))
    hw, hd = (w * c + d * s) / 2 * 0.92, (w * s + d * c) / 2 * 0.92
    solid(cx - hw, cz - hd, cx + hw, cz + hd)


# ------------------------------------------------------------------ materials

def trencadis_fn(palette, grout=(0.86, 0.84, 0.78), n=70, seed=5):
    r = random.Random(seed)
    pts = [(r.uniform(0, 128), r.uniform(0, 128), palette[r.randrange(len(palette))]) for _ in range(n)]

    def fn(x, y):
        best, second, col = 1e9, 1e9, None
        for (px, py, c) in pts:
            dx = min(abs(x - px), 128 - abs(x - px))
            dy = min(abs(y - py), 128 - abs(y - py))
            d = dx * dx + dy * dy
            if d < best:
                second, best, col = best, d, c
            elif d < second:
                second = d
        if math.sqrt(second) - math.sqrt(best) < 1.6:
            return grout
        k = 1.0 + (hash((int(x) // 3, int(y) // 3)) % 7 - 3) * 0.012
        return (col[0] * k, col[1] * k, col[2] * k)
    return fn


def hexrgb(h):
    return (int(h[1:3], 16) / 255, int(h[3:5], 16) / 255, int(h[5:7], 16) / 255)


T_MULTI = [hexrgb(c) for c in ('#2f6fb3', '#e8c53a', '#d9472b', '#3f9a5a', '#f2efe6', '#8a4aa0', '#f08a2a', '#58b6c9')]
M_TRENC = mat('Trencadis', '#ffffff', 0.35, image=make_image('trencadis', 128, 128, trencadis_fn(T_MULTI)))
M_TRENC_BW = mat('TrencadisBlueWhite', '#ffffff', 0.35, image=make_image('trencadis_bw', 128, 128,
                 trencadis_fn([hexrgb('#2c5fa8'), hexrgb('#f3f1ea'), hexrgb('#f3f1ea'), hexrgb('#4a7cc0')], seed=9)))
M_TRENC_DRAGON = mat('TrencadisDragon', '#ffffff', 0.35, image=make_image('trencadis_dragon', 128, 128,
                     trencadis_fn([hexrgb('#3f9a5a'), hexrgb('#e8c53a'), hexrgb('#f08a2a'), hexrgb('#2f6fb3'), hexrgb('#7cc06a')], n=90, seed=12)))
M_TRENC_BROWN = mat('TrencadisBrown', '#ffffff', 0.4, image=make_image('trencadis_brown', 128, 128,
                    trencadis_fn([hexrgb('#8a5a3a'), hexrgb('#e9dcc0'), hexrgb('#b07a4a'), hexrgb('#f3efe6')], seed=3)))


def rubble_fn(x, y):
    k = 1.0 + 0.12 * math.sin(x * 0.9 + math.sin(y * 0.7) * 2) + random.Random(x * 31 + y * 7).uniform(-0.08, 0.08)
    if (y % 16 < 1) or ((x + (y // 16) * 9) % 22 < 1):
        return (0.42, 0.36, 0.3)
    return (0.66 * k, 0.55 * k, 0.42 * k)


M_RUBBLE = mat('RubbleStone', '#ffffff', 0.95, image=make_image('rubble', 64, 64, rubble_fn))


def footing_fn(x, y):
    """(round 34) the park wall's footing: bigger blocks than the wall's rubble, darker, weathered."""
    k = 1.0 + 0.1 * math.sin(x * 0.5 + y * 0.3) + random.Random(x // 3 * 17 + y // 3 * 5).uniform(-0.1, 0.1)
    if (y % 32 < 2) or ((x + (y // 32) * 13) % 28 < 2):
        return (0.3, 0.26, 0.22)
    return (0.5 * k, 0.43 * k, 0.34 * k)


M_WALLFOOT = mat('ParkWallFooting', '#ffffff', 0.95, image=make_image('wall_footing', 64, 64, footing_fn))
M_SANDSTONE = mat('MontjuicStone', '#c6a073', 0.9)              # the crypt: the warm sandstone of Montjuïc
M_CHURCH = mat('ChurchStone', '#ece4d2', 0.85)                  # the upper church: pale and neo-Gothic
M_CHURCH_DARK = mat('ChurchStoneShade', '#cfc4ad', 0.9)
M_BRONZE = mat('Bronze', '#8a6a3e', 0.35, 0.85)
M_SLATE = mat('SlateGrey', '#5c6670', 0.7)
M_PINK = mat('GaudiHousePink', '#e8a5a0', 0.85)
M_OCHRE = mat('LodgeOchre', '#d7a660', 0.9)
M_CREAM = mat('TriasCream', '#efe2c4', 0.85)
M_ROOF_TILE = mat('RoofTiles', '#b85c3a', 0.8)
M_SHUT_GREEN = mat('ShutterGreen', '#3f6b4f', 0.7)
M_SHUT_BROWN = mat('ShutterBrown', '#7a5236', 0.7)
M_WHEEL_W = mat('WheelWhite', '#f4f2ec', 0.45, 0.2)
M_CABLE = mat('CableSteel', '#3a3d42', 0.4, 0.8)
M_PLANE_RED = mat('AvioRed', '#c8322e', 0.4, 0.2)
def square_sand_fn(x, y):
    # (round 24) the Nature Square's sauló: pale sandy gravel, little stones, the faint scuffs of many feet
    r = random.Random(x * 7919 + y * 104729 + 7)
    k = 1 + 0.05 * math.sin(x * 0.21 + math.sin(y * 0.13) * 2) + 0.04 * math.sin(y * 0.33 + x * 0.05) + r.uniform(-0.05, 0.05)
    if r.random() < 0.05:
        return (0.93 * k, 0.9 * k, 0.83 * k)
    if r.random() < 0.05:
        return (0.7 * k, 0.6 * k, 0.45 * k)
    return (0.89 * k, 0.8 * k, 0.62 * k)


M_SAND_SQ = mat('SquareSand', '#ffffff', 0.95, image=make_image('squaresand', 128, 128, square_sand_fn))
GONDOLA_COLS = ['#d9472b', '#2f6fb3', '#e8c53a', '#3f9a5a', '#8a4aa0', '#f08a2a']
M_GONDOLA = [mat('Gondola%d' % i, c, 0.45) for i, c in enumerate(GONDOLA_COLS)]
HOUSE_COLS = ['#e9c79a', '#e6b8a6', '#dcd1a8', '#cfd8c6', '#efd9b5', '#e8c0a0', '#d9c3d6']
M_HOUSE = [mat('GraciaWall%d' % i, c, 0.9) for i, c in enumerate(HOUSE_COLS)]

north = scene.setdefault('north', {})
new_doors = []
_n_post_signs = [0]
PS_MB = MB(uv=True)                      # (the park's signs on posts, finished at the end)


M_PSIGN_BOARD = mat('ParkSignBoard', '#efe6cf', 0.6)
M_PSIGN_TEXT = mat('ParkSignText', '#2f4a3a', 0.6)
M_PSIGN_POST = mat('ParkSignPost', '#4a3626', 0.8)


def post_sign(x, z, nx, nz, title, sub=''):
    """(round 33, the user: "Also have a sign outside") a park sign beside a way in, facing (nx, nz) (engine).
    (round 34, the user: "The signs should be smaller without the wood covering it… The sign post should be larger…
    it should be read") a tall dark post with a round cap, and on it a small plain painted board — no wooden frame —
    with just the name in large dark letters on cream, readable from the path; solid (a post)."""
    g_ = hz(x, z)
    nb_ = Vector((nx, -nz)).normalized()
    ub_ = (nb_.y, -nb_.x)
    sz_ = 0.13
    hw_ = 0.08 + 0.034 * len(title)
    top_ = g_ + 2.25
    PS_MB.cone(Matrix.Translation(V(x, z, g_ + 1.1)), 10, 0.065, 0.055, 2.3, M_PSIGN_POST)
    PS_MB.ico(Matrix.Translation(V(x, z, g_ + 2.28)), 0.085, M_PSIGN_POST, 1)
    bc_ = V(x, z, top_ - 0.3) + Vector((nb_.x, nb_.y, 0)) * 0.07
    PS_MB.box(bc_, ub_, (nb_.x, nb_.y), hw_, 0.02, 0.15, M_PSIGN_BOARD)
    k_ = _n_post_signs[0]
    _n_post_signs[0] += 1
    city_objs.append(text_obj(title, sz_, M_PSIGN_TEXT, bc_ + Vector((nb_.x, nb_.y, 0)) * 0.025 - Vector((0, 0, sz_ * 0.08)),
                              facing((nb_.x, nb_.y)), 'SignText_post%d' % k_))
    solid(x - 0.12, z - 0.12, x + 0.12, z + 0.12)


def door(id_, name, int_, x, z, nx, nz, w=1.6, plaque='', lock='', h=2.6, base=None, arch=0.0, glow=None, **more):
    """A way in: as the city's entrances (scene['entrances']), in engine metres. (round 33) h, arch: the door's own
    height and curved top, for its glow; base: its sill; glow: where its face is ([x, z]; else found by looking back
    from the door point); more: anything else for the game (a door lying on a slope: glow_c, lean)."""
    d_ = {'id': id_, 'int': int_, 'name': name, 'pos': [round(x, 3), round(z, 3)], 'normal': [nx, nz],
          'size': [w, h], 'base': round(hz(x + nx * 0.6, z + nz * 0.6) if base is None else base, 3), 'plaque': plaque}
    if lock:
        d_['lock'] = lock
    if arch > 0:
        d_['arch'] = round(arch, 3)
    if glow is not None:
        d_['glow'] = [round(glow[0], 3), round(glow[1], 3)]
    d_.update(more)
    new_doors.append(d_)


# ------------------------------------------------------------------ the funfair

FH = N.FAIR_H
fx0, fz0, fx1, fz1 = N.FAIR
fair = MB(uv=True)
fair_solid = []

# the retaining wall where the slope falls away from the terrace, and the railing along its top
edge = [(fx0, fz1, fx1, fz1, (0, 1)), (fx1, fz1, fx1, fz0, (1, 0)), (fx0, fz0, fx0, fz1, (-1, 0))]
# (round 41, the user: "the railing should come in a bit more so the fence can come up against it. Otherwise, it looks
# like someone could fall down") the wall and its railing run right up to the path's sides, 0.35 m clear of its edge
PATH_GAP = (N.PATH_CTRL[-1][1] - N.PATH_W / 2 - 0.35, N.PATH_CTRL[-1][1] + N.PATH_W / 2 + 0.35)   # (in on the west side)
# (round 41, the user: "You need the fence to continue all the way to the edges of the funicular station… It just looks
# funny where the fences end. It's perfect on the other side of the pole") the railing and its kerb run right up to the
# station's own sides (the model is 5.3 m wide), the last piece each side cut short to meet it
CABLE_GAP = (N.CABLE_TOP[0] - 2.6, N.CABLE_TOP[0] + 2.6)                 # (the top station on the south side)
for (ax, az, bx, bz, nrm) in edge:
    L = math.hypot(bx - ax, bz - az)
    n = int(L / 2.0)
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        x0, z0 = ax + (bx - ax) * t0, az + (bz - az) * t0
        x1, z1 = ax + (bx - ax) * t1, az + (bz - az) * t1
        if nrm == (0, 1):                   # (the south edge runs west to east: cut at the station's sides)
            if x0 < CABLE_GAP[0] < x1:
                x1 = CABLE_GAP[0]
            elif x0 < CABLE_GAP[1] < x1:
                x0 = CABLE_GAP[1]
        if nrm == (-1, 0):                  # (the west edge runs south to north, z rising: cut at the path's sides)
            if z0 < PATH_GAP[0] < z1:
                z1 = PATH_GAP[0]
            elif z0 < PATH_GAP[1] < z1:
                z0 = PATH_GAP[1]
        # (round 34: the plateau level again, the ground drops right at its edge: the wall is 1.8 m thick, its face out
        # beyond the ground's slope down from the edge, a stone top to it)
        WT_ = 1.8
        if nrm == (0, 1) and abs((x0 + x1) / 2 - N.CABLE_TOP[0]) < 21.5:
            WT_ = 0.0                       # (over the funicular's portal the terraced masonry is its face)
        lo0 = min(hz(x0 + nrm[0] * 3.6, z0 + nrm[1] * 3.6), FH - 0.3) - 1.0
        lo1 = min(hz(x1 + nrm[0] * 3.6, z1 + nrm[1] * 3.6), FH - 0.3) - 1.0
        ox0, oz0, ox1, oz1 = x0 + nrm[0] * WT_, z0 + nrm[1] * WT_, x1 + nrm[0] * WT_, z1 + nrm[1] * WT_
        mid = ((x0 + x1) / 2, (z0 + z1) / 2)
        gap = (nrm == (-1, 0) and PATH_GAP[0] < mid[1] < PATH_GAP[1]) or (nrm == (0, 1) and CABLE_GAP[0] < mid[0] < CABLE_GAP[1])
        if gap and nrm == (-1, 0):
            continue            # (round 35, PATH_RULES B1/B2: the path's gateway — no wall top or face across it)
        fair.face([V(ox0, oz0, lo0), V(ox1, oz1, lo1), V(ox1, oz1, FH + 0.05), V(ox0, oz0, FH + 0.05)], M_RUBBLE,
                  normal=(nrm[0], -nrm[1], 0))
        fair.face([V(x0, z0, FH + 0.05), V(x1, z1, FH + 0.05), V(ox1, oz1, FH + 0.05), V(ox0, oz0, FH + 0.05)], M_STONE,
                  normal=(0, 0, 1))
        # (round 41, the user: "This gaps between the pavement and the fence slash railing where you could fall down on
        # the left and there's grass on the right": the paving is laid in whole ground squares, so it stopped up to
        # 0.75 m short of the edge) a band of the wall's stone in from the edge, over the paving's ragged end
        if not gap:
            ix0, iz0, ix1, iz1 = x0 - nrm[0] * 0.9, z0 - nrm[1] * 0.9, x1 - nrm[0] * 0.9, z1 - nrm[1] * 0.9
            fair.face([V(ix0, iz0, FH + 0.045), V(ix1, iz1, FH + 0.045), V(x1, z1, FH + 0.045), V(x0, z0, FH + 0.045)],
                      M_STONE, normal=(0, 0, 1))
        if nrm == (-1, 0):
            # (the wall's end beside the gateway closed with a face of its own)
            for (ex_, ez_, eox_, eoz_, elo_, sg_) in ((x0, z0, ox0, oz0, lo0, -1), (x1, z1, ox1, oz1, lo1, 1)):
                if min(abs(ez_ - PATH_GAP[0]), abs(ez_ - PATH_GAP[1])) < 1e-6:     # (round 41: cut at the path's sides)
                    fair.face([V(ex_, ez_, elo_), V(eox_, eoz_, elo_), V(eox_, eoz_, FH + 0.05), V(ex_, ez_, FH + 0.05)],
                              M_RUBBLE, normal=(0, sg_ if z1 < z0 else -sg_, 0))
        if gap:
            continue
        # a stone kerb with iron railings on it
        c = V(mid[0], mid[1], FH)
        u = (bx - ax) / L, -(bz - az) / L
        sl_ = math.hypot(x1 - x0, z1 - z0)
        fair.box(c + Vector((0, 0, 0.15)), u, (nrm[0], -nrm[1]), sl_ / 2, 0.22, 0.15, M_STONE)
        fair.box(c + Vector((0, 0, 1.05)), u, (nrm[0], -nrm[1]), sl_ / 2, 0.04, 0.04, M_IRON)
        nb_ = max(2, round(4 * sl_ / 2.0))
        for j in range(nb_):
            off = (j + 0.5) / nb_ - 0.5
            fair.box(c + Vector((u[0] * off * sl_, u[1] * off * sl_, 0.65)), u, (nrm[0], -nrm[1]), 0.02, 0.02, 0.4, M_IRON)
        fair_solid.append((min(x0, x1) - 0.25 * abs(nrm[0]), min(z0, z1) - 0.25 * abs(nrm[1]), max(x0, x1) + 0.25 * abs(nrm[0]),
                           max(z0, z1) + 0.25 * abs(nrm[1])))
# (round 41, the user marked the path's end at the paving: ragged) a stone threshold across the gateway, as the band
# along the edge either side, the path's end tucked under it
fair.face([V(fx0 + 0.9, PATH_GAP[0], FH + 0.045), V(fx0 + 0.9, PATH_GAP[1], FH + 0.045), V(fx0 - 0.15, PATH_GAP[1], FH + 0.045),
           V(fx0 - 0.15, PATH_GAP[0], FH + 0.045)], M_STONE, normal=(0, 0, 1))
# (round 41c, the user: "the paved ground should be on top of the dirt") its outer edge a little kerb face down into the
# ground, the path's end tucked under the stone (the ribbon stops 0.3 m in under it)
fair.face([V(fx0 - 0.15, PATH_GAP[0], FH - 0.08), V(fx0 - 0.15, PATH_GAP[1], FH - 0.08), V(fx0 - 0.15, PATH_GAP[1], FH + 0.045),
           V(fx0 - 0.15, PATH_GAP[0], FH + 0.045)], M_STONE, normal=(-1, 0, 0))
# (round 35, the user: "a gap in the ground at the tibidabo which someone could fall through") where the south wall
# meets the east and west ones, each wall's 1.8 m thickness stood out along its own side only and left an open
# square at the corner down to the hillside: filled, its top stone and its two outer faces
WT_C = 1.8
for (cx_, cz_, sx_c) in ((fx1, fz1, 1), (fx0, fz1, -1)):
    xo_ = cx_ + sx_c * WT_C
    zo_ = cz_ + WT_C
    lo_ = min(hz(cx_ + sx_c * 3.6, cz_ + 3.6), FH - 0.3) - 1.0
    fair.face([V(cx_, cz_, FH + 0.05), V(xo_, cz_, FH + 0.05), V(xo_, zo_, FH + 0.05), V(cx_, zo_, FH + 0.05)], M_STONE,
              normal=(0, 0, 1))
    fair.face([V(xo_, cz_, lo_), V(xo_, zo_, lo_), V(xo_, zo_, FH + 0.05), V(xo_, cz_, FH + 0.05)], M_RUBBLE,
              normal=(sx_c, 0, 0))
    fair.face([V(cx_, zo_, lo_), V(xo_, zo_, lo_), V(xo_, zo_, FH + 0.05), V(cx_, zo_, FH + 0.05)], M_RUBBLE,
              normal=(0, -1, 0))
    fair_solid.append((min(cx_, xo_), cz_, max(cx_, xo_), zo_))
# the north side backs onto the hill: a low wall along it
fair.box(V((fx0 + fx1) / 2, fz0 - 0.3, FH + 0.6), (1, 0), (0, 1), (fx1 - fx0) / 2, 0.3, 0.6, M_GREYSTONE)
fair_solid.append((fx0, fz0 - 0.6, fx1, fz0 + 0.2))

def meshy_house(f, rect, h0, name, target=150000, tex=2048, max_h=None, rot=0.0):
    """(round 25) A Meshy building (bigfiles/originals/meshy/<f>), its front to the south (rot: turned, radians), scaled to fit the
    footprint `rect` (x0, z0, x1, z1 metres) on ground h0 high; False if the file isn't there (the caller builds a
    stand-in). (150,000 triangles: the user saw round25/slim_*.png; 50,000 already cracks close to.)"""
    if not os.path.exists(meshy_file(f)):
        return False
    me = meshy_mesh(f, target, 'base', tex)
    xs, ys = [v.co.x for v in me.vertices], [v.co.y for v in me.vertices]
    wx, wy = max(xs) - min(xs), max(ys) - min(ys)
    if abs(math.sin(rot)) > 0.7:
        wx, wy = wy, wx
    k = min((rect[2] - rect[0]) / wx, (rect[3] - rect[1]) / wy, max_h or 1e9)
    cx, cz = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
    meshy_place(f, target, 'base', k, V(cx, cz, h0 - 0.05), rot, name, tex)
    return k


# --- the Temple del Sagrat Cor (round 25, the user: "Make the church like the Temple of the Sacred Heart of Jesus in real
# life. There is a small landing that you can walk up. Put it into the hill, but don't have the hill going up past it.
# Just enough hill so that Sandra can't walk up"). As the real one (looked up): Sagnier's crypt below, in rough, warm
# Montjuïc stone, a great round-arched porch in its front with a gold mosaic in the arch, a round turret at each front
# corner; a flight of steps up each side, along the crypt's walls, to its roof: a terrace with a stone balustrade (the
# landing she may walk up to); on it the upper church, pale and neo-Gothic: three pointed doors under a rose window and
# a steep gable, slim spired towers at its four corners, pinnacles all round, and rising out of its middle the tall
# tiered tower with the bronze Christ, arms open over the city. Its back is set into the hill (north.py: the bank
# behind the funfair rises no higher than the crypt's roof). Built here, not from Meshy (the Meshy one, round 25's
# first try, sat on a round plinth and looked nothing like it).
M_SANDSTONE_DARK = mat('MontjuicStoneShade', '#a8845c', 0.92)
M_MOSAIC = mat('CryptMosaic', '#c99a3a', 0.4, 0.55)
M_MOSAIC_BLUE = mat('CryptMosaicBlue', '#3f63a8', 0.5)
CH = N.SAGRAT                                      # (centre x, z: its front faces south, onto the funfair)
cx, cz = CH
CW, CD, CRYPT_H = 26.0, 20.0, 7.5                  # the crypt: wide and deep; its roof is the terrace
front = cz + CD / 2                                # the crypt's south face
TB = FH + CRYPT_H                                  # the terrace's floor
church = MB(uv=True)
church_solid = []
raised = scene.setdefault('raised', [])


def ch_disc(x, z, h, r, m, segs=24, t=0.06):
    """A round thing flat on the south face (an arch's ring, a rose window), z its face."""
    church.cone(Matrix.Translation(V(x, z, h)) @ Matrix.Rotation(math.pi / 2, 4, 'X'), segs, r, r, t, m)


def balustrade(x0, z0, x1, z1, h):
    """A stone balustrade from (x0, z0) to (x1, z1) on a floor h high: a plinth, balusters, a rail."""
    L = math.hypot(x1 - x0, z1 - z0)
    u = ((x1 - x0) / L, -(z1 - z0) / L)
    nrm = (-u[1], u[0])
    mid = V((x0 + x1) / 2, (z0 + z1) / 2, h)
    church.box(mid + Vector((0, 0, 0.1)), u, nrm, L / 2, 0.2, 0.1, M_CHURCH_DARK)
    church.box(mid + Vector((0, 0, 0.92)), u, nrm, L / 2 + 0.1, 0.2, 0.07, M_CHURCH_DARK)
    n = max(1, int(L / 0.42))
    for k in range(n):
        t = (k + 0.5) / n
        church.cone(Matrix.Translation(V(x0 + (x1 - x0) * t, z0 + (z1 - z0) * t, h + 0.53)), 6, 0.08, 0.06, 0.66, M_CHURCH)


# the crypt: courses of rough stone (a darker joint every course), a cornice, the terrace's paving on its roof
church.box(V(cx, cz, FH + CRYPT_H / 2), (1, 0), (0, 1), CW / 2, CD / 2, CRYPT_H / 2, M_SANDSTONE)
for k in range(1, 8):
    church.box(V(cx, cz, FH + k * 0.92), (1, 0), (0, 1), CW / 2 + 0.03, CD / 2 + 0.03, 0.03, M_SANDSTONE_DARK)
church.box(V(cx, cz, TB - 0.2), (1, 0), (0, 1), CW / 2 + 0.3, CD / 2 + 0.3, 0.2, M_SANDSTONE_DARK)      # its cornice
church.box(V(cx, cz, TB + 0.02), (1, 0), (0, 1), CW / 2, CD / 2, 0.03, M_STONE)                       # the terrace
# the porch: a deep block out from the crypt's front, its great round arch with the gold mosaic in it over the doors;
# (round 41, the user: "you can't see the city from up above the park when you're standing on the porch of the
# church because there's a big thing in front… the concrete part that you have built is too high"; "lower the middle
# block. And remove the statues. There's no statues in real life") its top a solid parapet at the balustrades' height
# either side, so from the upper church's doors the city is seen over it
PW, PD = 5.2, 2.6                                  # its half width, depth
pf = front + PD                                    # its face
# (round 41, the user: "She should be able to see over the wall… it shouldn't be that thick… make it like 3-sided
# rectangle where the sides are very, very small, just to push it out a little bit and create a little bit of a
# platform… it still needs to connect to the fence to the sides") the porch's block rises only to the terrace's floor,
# its top a little platform out from the terrace, walked on; round it a thin parapet on three sides, the balustrades'
# height, its short sides meeting the balustrades either side
PT_ = TB + 0.95                                    # (the parapet's top: the balustrades' rail, balustrade() below)
PPW_ = 0.25                                        # (the parapet's thickness)
church.box(V(cx, front + PD / 2, (FH + TB) / 2), (1, 0), (0, 1), PW, PD / 2, (TB - FH) / 2, M_SANDSTONE)
church.box(V(cx, front + PD / 2, TB + 0.02), (1, 0), (0, 1), PW, PD / 2, 0.03, M_STONE)              # (its paving)
for (x0_, z0_, x1_, z1_) in ((cx - PW, pf - PPW_, cx + PW, pf), (cx - PW, front - 0.25, cx - PW + PPW_, pf - PPW_),
                             (cx + PW - PPW_, front - 0.25, cx + PW, pf - PPW_)):
    church.box(V((x0_ + x1_) / 2, (z0_ + z1_) / 2, (TB + PT_) / 2), (1, 0), (0, 1), (x1_ - x0_) / 2, (z1_ - z0_) / 2,
               (PT_ - TB) / 2, M_SANDSTONE)
    church.box(V((x0_ + x1_) / 2, (z0_ + z1_) / 2, PT_ + 0.05), (1, 0), (0, 1), (x1_ - x0_) / 2 + 0.06, (z1_ - z0_) / 2 + 0.06,
               0.05, M_SANDSTONE_DARK)
    church_solid.append((x0_, z0_, x1_, z1_))
raised.append([round(cx - PW, 3), round(front - 0.05, 3), round(cx + PW, 3), round(pf, 3), round(TB, 3)])   # (walked on)
# (round 41, the user: "Could you put the statues back on the wall at the church? Just make them smaller") five small
# figures along the front wall's top
for k in range(5):
    p = V(cx + (k - 2) * 2.0, pf - PPW_ / 2, PT_ + 0.1)
    church.cone(Matrix.Translation(p + Vector((0, 0, 0.32))), 8, 0.14, 0.1, 0.64, M_CHURCH)
    church.sphere(Matrix.Translation(p + Vector((0, 0, 0.74))), 0.1, M_CHURCH, (8, 6))
AR, AS = 3.3, FH + 3.7                             # the arch's radius, the height it springs from
ch_disc(cx, pf + 0.03, AS, AR + 0.55, M_SANDSTONE_DARK, 28)                                  # its ring of voussoirs
ch_disc(cx, pf + 0.07, AS, AR, M_MOSAIC_BLUE, 28)                                             # the mosaic: blue round
ch_disc(cx, pf + 0.1, AS + 0.15, AR - 0.45, M_MOSAIC, 28)                                     # gold within
church.box(V(cx, pf + 0.12, FH + (AS - FH) / 2), (1, 0), (0, 1), AR + 0.6, 0.06, (AS - FH) / 2, M_SANDSTONE)   # the jambs
church.box(V(cx, pf + 0.16, FH + 1.6), (1, 0), (0, 1), 1.5, 0.04, 1.6, M_WOOD_DOOR)            # the doors
church.box(V(cx, pf + 0.17, FH + 3.3), (1, 0), (0, 1), 1.6, 0.05, 0.1, M_SANDSTONE_DARK)        # their lintel
for sx in (-1, 1):                                 # a column either side of the doors
    church.cone(Matrix.Translation(V(cx + sx * 2.1, pf + 0.3, FH + 1.75)), 10, 0.22, 0.22, 3.5, M_CHURCH)
    church.box(V(cx + sx * 2.1, pf + 0.3, FH + 3.6), (1, 0), (0, 1), 0.32, 0.32, 0.12, M_CHURCH_DARK)
for sx in (-8.6, 8.6):                             # a round-arched window either side, in the crypt's face
    ch_disc(cx + sx, front + 0.03, FH + 4.3, 1.25, M_SANDSTONE_DARK, 16)
    ch_disc(cx + sx, front + 0.06, FH + 4.3, 0.85, M_GLASS_LIT, 16)
    church.box(V(cx + sx, front + 0.05, FH + 3.4), (1, 0), (0, 1), 0.85, 0.03, 0.9, M_GLASS_LIT)
    church.box(V(cx + sx, front + 0.04, FH + 3.0), (1, 0), (0, 1), 1.25, 0.03, 1.3, M_SANDSTONE_DARK)
# the round turrets at the crypt's front corners: up past the terrace, a cornice, a little dome, a lantern on it
TR_ = 1.9
for sx in (-1, 1):
    tx, tz = cx + sx * (CW / 2 - 1.2), front - 1.2
    church.cone(Matrix.Translation(V(tx, tz, FH + (CRYPT_H + 4.0) / 2)), 20, TR_, TR_, CRYPT_H + 4.0, M_SANDSTONE)
    church.cone(Matrix.Translation(V(tx, tz, FH + CRYPT_H + 4.1)), 20, TR_ + 0.25, TR_ + 0.25, 0.3, M_SANDSTONE_DARK)
    church.sphere(Matrix.Translation(V(tx, tz, FH + CRYPT_H + 4.2)) @ Matrix.Diagonal((1, 1, 0.75, 1)), TR_ * 0.95, M_SANDSTONE, (16, 10))
    church.cone(Matrix.Translation(V(tx, tz, FH + CRYPT_H + 6.2)), 8, 0.35, 0.3, 1.2, M_SANDSTONE)
    church.sphere(Matrix.Translation(V(tx, tz, FH + CRYPT_H + 7.0)), 0.3, M_SANDSTONE_DARK, (8, 6))
    for k in range(3):                             # narrow slit windows round it
        a = math.pi / 2 * (k - 1) + (0 if sx > 0 else math.pi)
        church.box(V(tx + math.sin(a) * (TR_ + 0.01), tz + math.cos(a) * (TR_ + 0.01), FH + CRYPT_H + 1.8),
                   (math.cos(a), math.sin(a)), (math.sin(a), -math.cos(a)), 0.18, 0.03, 0.7, M_GLASS_LIT)
    church_solid.append((tx - TR_, tz - TR_, tx + TR_, tz + TR_))
# the two flights of steps up the crypt's sides to the terrace, from beside the turrets northwards, each with its stone
# parapet on the outside; a landing at the top opening onto the terrace. Walkable (scene['raised']).
NST, SW = 25, 3.0                                  # steps, the flights' width
RISE, RUN = CRYPT_H / NST, 0.46
z_bot = front - 3.4                                # the first step's front edge
z_top = z_bot - NST * RUN                          # the last's back edge
z_land = z_top - 3.4                               # the landing's back
for sx in (-1, 1):
    xi, xo = cx + sx * CW / 2, cx + sx * (CW / 2 + SW)
    xa, xb = min(xi, xo), max(xi, xo)
    for k in range(NST):
        top = RISE * (k + 1)
        za, zb = z_bot - (k + 1) * RUN, z_bot - k * RUN
        church.box(V((xa + xb) / 2, (za + zb) / 2, FH + top / 2), (1, 0), (0, 1), SW / 2, RUN / 2, top / 2, M_SANDSTONE)
        church.box(V((xa + xb) / 2, zb - 0.03, FH + top - 0.015), (1, 0), (0, 1), SW / 2, 0.035, 0.02, M_SANDSTONE_DARK)   # its nosing
        # the parapet beside it, a step at a time
        church.box(V(xo + sx * 0.15, (za + zb) / 2, FH + (top + 1.0) / 2), (1, 0), (0, 1), 0.15, RUN / 2, (top + 1.0) / 2, M_SANDSTONE)
        raised.append([round(xa, 3), round(za, 3), round(xb, 3), round(zb, 3), round(FH + top, 3)])
    church.box(V((xa + xb) / 2, (z_top + z_land) / 2, FH + CRYPT_H / 2), (1, 0), (0, 1), SW / 2, (z_top - z_land) / 2, CRYPT_H / 2, M_SANDSTONE)
    church.box(V((xa + xb) / 2, (z_top + z_land) / 2, TB + 0.02), (1, 0), (0, 1), SW / 2, (z_top - z_land) / 2, 0.03, M_STONE)
    church.box(V(xo + sx * 0.15, (z_top + z_land) / 2, TB + 0.5), (1, 0), (0, 1), 0.15, (z_top - z_land) / 2, 0.5, M_SANDSTONE)
    church.box(V((xa + xb) / 2 + sx * 0.15, z_land - 0.15, TB + 0.5), (1, 0), (0, 1), SW / 2 + 0.15, 0.15, 0.5, M_SANDSTONE)
    raised.append([round(xa, 3), round(z_land, 3), round(xb, 3), round(z_top, 3), round(TB, 3)])
    church_solid.append((min(xo, xo + sx * 0.35), z_land - 0.3, max(xo, xo + sx * 0.35), z_bot))      # the parapet
    church_solid.append((xa, z_land - 0.35, xb, z_land))                                             # the landing's back
    # the crypt's side wall: no stepping off the flight onto the terrace (or in from the ground), but open from the landing
    church_solid.append((min(xi, xi - sx * 0.35), z_top + 0.2, max(xi, xi - sx * 0.35), front))
    church_solid.append((min(xi, xi - sx * 0.35), cz - CD / 2, max(xi, xi - sx * 0.35), z_land + 0.2))
# the terrace: walkable, its balustrade along the front (either side of the porch) and the back; the sides open onto
# the landings, and the balustrade on along the side walls beyond them
raised.append([round(cx - CW / 2, 3), round(cz - CD / 2, 3), round(cx + CW / 2, 3), round(front, 3), round(TB, 3)])
for (a, b) in ((cx - CW / 2 + 2.6, cx - PW), (cx + PW, cx + CW / 2 - 2.6)):
    balustrade(a, front - 0.25, b, front - 0.25, TB)
balustrade(cx - CW / 2 + 0.25, cz - CD / 2 + 0.25, cx + CW / 2 - 0.25, cz - CD / 2 + 0.25, TB)
for sx in (-1, 1):
    xs_ = cx + sx * (CW / 2 - 0.25)
    balustrade(xs_, front - 2.6, xs_, z_top + 0.2, TB)
    balustrade(xs_, z_land + 0.2, xs_, cz - CD / 2 + 0.25, TB)
church_solid.append((cx - CW / 2, front - 0.45, cx - PW, front))                         # (the front: the crypt's face,
church_solid.append((cx + PW, front - 0.45, cx + CW / 2, front))                         # open onto the porch's platform)
church_solid.append((cx - CW / 2, cz - CD / 2, cx + CW / 2, cz - CD / 2 + 0.45))          # (the back)

# the upper church, set back on the terrace: pale stone, neo-Gothic
UB = TB + 0.05                                     # its floor
UW, UD, UH = 15.0, 11.5, 12.0
zf = front - 6.0                                   # its front (the landing before it six metres deep)
uz = zf - UD / 2
church.box(V(cx, uz, UB + UH / 2), (1, 0), (0, 1), UW / 2, UD / 2, UH / 2, M_CHURCH)
church.box(V(cx, uz, UB + 0.3), (1, 0), (0, 1), UW / 2 + 0.15, UD / 2 + 0.15, 0.3, M_CHURCH_DARK)     # its plinth
for sx in (-1, 1):                                 # buttresses down its sides, each with a pinnacle; tall lancets between
    for k in range(4):
        y = zf - 1.6 - k * 2.8
        church.box(V(cx + sx * (UW / 2 + 0.35), y, UB + UH * 0.47), (1, 0), (0, 1), 0.35, 0.4, UH * 0.47, M_CHURCH)
        church.cone(Matrix.Translation(V(cx + sx * (UW / 2 + 0.35), y, UB + UH * 0.94 + 1.5)), 8, 0.36, 0.03, 3.0, M_CHURCH)
        if k < 3:
            church.box(V(cx + sx * (UW / 2 + 0.02), y - 1.4, UB + 5.6), (1, 0), (0, 1), 0.04, 0.5, 3.0, M_GLASS_LIT)
            church.face([V(cx + sx * (UW / 2 + 0.03), y - 1.4 + 0.5, UB + 8.6), V(cx + sx * (UW / 2 + 0.03), y - 1.4 - 0.5, UB + 8.6),
                         V(cx + sx * (UW / 2 + 0.03), y - 1.4, UB + 9.5)], M_GLASS_LIT, normal=(sx, 0, 0))
# the front: three pointed doorways (the middle one tallest), the rose window over them, the steep gable, pinnacles
for sx, hw, hh in ((-4.0, 0.9, 3.4), (0.0, 1.3, 4.4), (4.0, 0.9, 3.4)):
    church.box(V(cx + sx, zf + 0.25, UB + hh / 2), (1, 0), (0, 1), hw + 0.35, 0.25, hh / 2, M_CHURCH_DARK)
    church.face([V(cx + sx - hw - 0.35, zf + 0.5, UB + hh), V(cx + sx + hw + 0.35, zf + 0.5, UB + hh),
                 V(cx + sx, zf + 0.5, UB + hh + hw * 1.6 + 0.6)], M_CHURCH_DARK, normal=(0, -1, 0))
    church.box(V(cx + sx, zf + 0.52, UB + hh * 0.45), (1, 0), (0, 1), hw, 0.03, hh * 0.45, M_WOOD_DOOR)
    church.face([V(cx + sx - hw, zf + 0.55, UB + hh * 0.9), V(cx + sx + hw, zf + 0.55, UB + hh * 0.9),
                 V(cx + sx, zf + 0.55, UB + hh * 0.9 + hw * 1.5)], M_GLASS_LIT, normal=(0, -1, 0))
ch_disc(cx, zf + 0.04, UB + 8.4, 2.5, M_CHURCH_DARK, 24, 0.1)
ch_disc(cx, zf + 0.1, UB + 8.4, 2.1, mat('RoseGlass', '#5a7fbf', 0.2), 24, 0.06)
ch_disc(cx, zf + 0.14, UB + 8.4, 1.25, M_CHURCH, 16, 0.04)        # the rose's tracery: rings
ch_disc(cx, zf + 0.17, UB + 8.4, 1.0, mat('RoseGlass', '#5a7fbf', 0.2), 16, 0.04)
ch_disc(cx, zf + 0.2, UB + 8.4, 0.35, M_CHURCH, 12, 0.04)
church.face([V(cx - UW / 2, zf + 0.02, UB + UH), V(cx + UW / 2, zf + 0.02, UB + UH), V(cx, zf + 0.02, UB + UH + 7.0)], M_CHURCH, normal=(0, -1, 0))
church.face([V(cx - UW / 2, zf - UD, UB + UH), V(cx + UW / 2, zf - UD, UB + UH), V(cx, zf - UD, UB + UH + 7.0)], M_CHURCH, normal=(0, 1, 0))
for sx in (-1, 1):                                 # the roof's two pitches
    church.face([V(cx + sx * (UW / 2 + 0.3), zf + 0.3, UB + UH - 0.1), V(cx + sx * (UW / 2 + 0.3), zf - UD - 0.3, UB + UH - 0.1),
                 V(cx, zf - UD - 0.3, UB + UH + 7.1), V(cx, zf + 0.3, UB + UH + 7.1)], M_SLATE, normal=(sx, 0, 1))
for k in range(1, 6):                              # crockets up the gable's edges, a cross-flower at its top
    t = k / 6
    for sx in (-1, 1):
        church.cone(Matrix.Translation(V(cx + sx * UW / 2 * (1 - t), zf + 0.1, UB + UH + 7.0 * t + 0.45)), 6, 0.2, 0.02, 0.9, M_CHURCH)
church.cone(Matrix.Translation(V(cx, zf + 0.1, UB + UH + 7.9)), 8, 0.3, 0.02, 1.8, M_CHURCH)
# slim towers at the four corners: square, a gallery of tall lancets, a spire with pinnacles round its foot (the front
# two a little taller)
for sx in (-1, 1):
    for sz in (1, -1):
        tx, tz = cx + sx * (UW / 2 + 0.3), (zf + 0.3) if sz > 0 else (zf - UD - 0.3)
        TH = 19.0 if sz > 0 else 17.0
        church.box(V(tx, tz, UB + TH / 2), (1, 0), (0, 1), 1.4, 1.4, TH / 2, M_CHURCH)
        church.box(V(tx, tz, UB + TH + 0.15), (1, 0), (0, 1), 1.6, 1.6, 0.15, M_CHURCH_DARK)
        for a in range(4):
            aa = math.pi / 2 * a
            church.box(V(tx + math.sin(aa) * 1.42, tz + math.cos(aa) * 1.42, UB + TH - 3.0), (math.cos(aa), -math.sin(aa)),
                       (math.sin(aa), math.cos(aa)), 0.3, 0.03, 1.8, M_GLASS_LIT)
        church.cone(Matrix.Translation(V(tx, tz, UB + TH + 0.3 + 3.8)) @ Matrix.Rotation(math.pi / 8, 4, 'Z'), 8, 1.25, 0.06, 7.6, M_CHURCH)
        for ox in (-1, 1):
            for oz in (-1, 1):
                church.cone(Matrix.Translation(V(tx + ox * 1.35, tz + oz * 1.35, UB + TH + 1.3)), 6, 0.2, 0.02, 2.0, M_CHURCH)
# (round 26: a notch in front of the middle door, so she can walk up to it: it is the upper church's own way in)
church_solid.append((cx - UW / 2 - 1.7, zf - UD - 1.7, cx + UW / 2 + 1.7, zf + 0.55))
church_solid.append((cx - UW / 2 - 1.7, zf + 0.55, cx - 1.5, zf + 1.7))
church_solid.append((cx + 1.5, zf + 0.55, cx + UW / 2 + 1.7, zf + 1.7))
cam_building(cx - CW / 2, cz - CD / 2, cx + CW / 2, front, FH - 0.5, TB - 0.1)      # the crypt, under the terrace
cam_building(cx - UW / 2, zf - UD, cx + UW / 2, zf, UB - 0.3, UB + UH + 7.0)          # the upper church
# (round 41, the user: "the church on tibidabo needs to be treated as having walls that move the camera in. Here I can't
# see the view"; coming out of the crypt the camera was inside the porch) its turrets, porch and towers too
for sx in (-1, 1):
    cam_building(cx + sx * (CW / 2 - 1.2) - TR_, front - 1.2 - TR_, cx + sx * (CW / 2 - 1.2) + TR_, front - 1.2 + TR_,
                 FH - 0.5, FH + CRYPT_H + 5.5)                                         # the crypt's two round turrets
    for sz in (1, -1):
        tx_c, tz_c = cx + sx * (UW / 2 + 0.3), (zf + 0.3) if sz > 0 else (zf - UD - 0.3)
        cam_building(tx_c - 1.4, tz_c - 1.4, tx_c + 1.4, tz_c + 1.4, UB - 0.3, UB + 27.0)   # the four corner towers
cam_building(cx - PW, front - 0.1, cx + PW, pf, FH - 0.5, TB + 2.6)                   # the crypt's porch
cam_building(cx - 3.4, zf - UD * 0.42 - 3.4, cx + 3.4, zf - UD * 0.42 + 3.4, UB + UH, UB + UH + 30.0)   # the tower
# the tall central tower, out of the roof behind the gable: a square base, then three octagonal stages, each narrower,
# lancets all round and a ring of pinnacles at each stage's top; on the last, the pedestal and the bronze Christ
tcz = zf - UD * 0.42
T0 = UB + UH
church.box(V(cx, tcz, T0 + 2.5), (1, 0), (0, 1), 3.4, 3.4, 3.5, M_CHURCH)
church.box(V(cx, tcz, T0 + 6.1), (1, 0), (0, 1), 3.6, 3.6, 0.15, M_CHURCH_DARK)
h_ = T0 + 6.25
for (r_, hh_) in ((3.1, 7.5), (2.45, 6.0), (1.8, 4.5)):
    church.cone(Matrix.Translation(V(cx, tcz, h_ + hh_ / 2)) @ Matrix.Rotation(math.pi / 8, 4, 'Z'), 8, r_, r_ * 0.94, hh_, M_CHURCH)
    for k in range(8):
        a = 2 * math.pi * k / 8
        ri = r_ * 0.93
        church.box(V(cx + math.sin(a) * ri, tcz + math.cos(a) * ri, h_ + hh_ * 0.5), (math.cos(a), math.sin(a)),
                   (math.sin(a), -math.cos(a)), 0.3, 0.04, hh_ * 0.3, M_GLASS_LIT)
        b = a + math.pi / 8
        church.cone(Matrix.Translation(V(cx + math.sin(b) * r_ * 0.98, tcz + math.cos(b) * r_ * 0.98, h_ + hh_ + 0.9)), 6, 0.22, 0.02,
                    1.8, M_CHURCH)
    church.cone(Matrix.Translation(V(cx, tcz, h_ + hh_ + 0.12)) @ Matrix.Rotation(math.pi / 8, 4, 'Z'), 8, r_ + 0.15, r_ + 0.15, 0.24,
                M_CHURCH_DARK)
    h_ += hh_ + 0.24
church.cone(Matrix.Translation(V(cx, tcz, h_ + 0.9)), 12, 1.15, 0.95, 1.8, M_CHURCH_DARK)     # the pedestal
base = h_ + 0.9                                    # (the statue's robe stands on the pedestal's top)
north['christ'] = [cx, base + 3.6, tcz]
statue = MB(uv=True)
statue.cone(Matrix.Translation(V(cx, tcz, base + 2.6)), 12, 0.95, 0.55, 3.4, M_BRONZE)          # robe
statue.cone(Matrix.Translation(V(cx, tcz, base + 4.7)), 10, 0.55, 0.45, 1.0, M_BRONZE)           # chest
statue.sphere(Matrix.Translation(V(cx, tcz, base + 5.6)), 0.42, M_BRONZE, (10, 8))               # head
for sx in (-1, 1):                                                                              # arms open, embracing the city
    a = V(cx + sx * 0.45, tcz, base + 4.85)
    b = V(cx + sx * 2.1, tcz + 0.35, base + 4.35)
    d = b - a
    M_ = Matrix.Translation((a + b) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    statue.cone(M_, 8, 0.3, 0.2, d.length, M_BRONZE)
_church_ob = church.finish('SagratCor')
# (round 26, the user: "Put some textures on the church and base; it looks very plain" … "B for brown bricks and C for
# white. Base is brown bricks"): the crypt, its steps, porch and turrets in warm Montjuïc blocks (darker at the foot),
# the upper church in pale stone, the terrace in flagstones, the porch's arch a flat mosaic of little tiles (it was a
# shiny gold half-ball). builder/stone_tex.py; the options compared: builder/church_options.py, round26/church_textures_*.
exec(open(os.path.join(HERE, 'stone_tex.py')).read())
st_dress(_church_ob, {'MontjuicStone': ('crypt', FH), 'MontjuicStoneShade': ('crypt_dark', FH), 'ChurchStone': ('upper', UB),
                      'ChurchStoneShade': ('upper_dark', UB), 'Stone': ('flags', 0.0),
                      'CryptMosaic': ('gold', 0.0, 0.45), 'CryptMosaicBlue': ('blue', 0.0, 0.5)})
city_objs.append(_church_ob)
city_objs.append(statue.finish('SagratCorChrist'))
fair_solid.extend(church_solid)
post_sign(cx + 3.4, pf + 2.2, 0.0, 1.0, 'SAGRAT COR', 'la cripta · obert')
door('sagrat_cor', 'Temple del Sagrat Cor', 'int_sagrat_cor', cx, pf + 0.25, 0.0, 1.0, 3.0,
     "TEMPLE EXPIATORI DEL SAGRAT COR. Begun in 1902 by Enric Sagnier and finished by his son in 1961: a Romanesque crypt in "
     "Montjuïc stone, a neo-Gothic church above it, and on its tower a bronze Christ with open arms over the whole city.")
# (round 26, the user: "Separate entrances") the upper church's own way in: its middle door, up the steps on the terrace
door('sagrat_cor_alta', 'Temple del Sagrat Cor: the upper church', 'int_sagrat_alta', cx, zf + 0.8, 0.0, 1.0, 2.4,
     "TEMPLE EXPIATORI DEL SAGRAT COR. The upper church: neo-Gothic, consecrated in 1961.")
new_doors[-1]['base'] = round(UB, 3)

# --- the Giradabo: a bigger wheel (the user: "slightly bigger"), its rim and spokes turned by the game about the
# hub; its gondolas hang level from the rim; a boarding platform with a gate at the bottom
WH = N.WHEEL
wx, wz, WR, NG = WH['x'], WH['z'], WH['r'], WH['n']
hub = (wx, wz, FH + WH['hub'])
stand = MB(uv=True)
for sz in (-1, 1):                                  # two A-frames either side of the rim
    for sx in (-1, 1):
        a = V(wx + sx * 5.2, wz + sz * 1.6, FH)
        b = V(wx, wz + sz * 1.6, hub[2])
        d = b - a
        stand.cone(Matrix.Translation((a + b) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4(), 8, 0.32, 0.22,
                   d.length, M_WHEEL_W)
stand.cone(Matrix.Translation(V(wx, wz, hub[2])) @ Matrix.Rotation(math.pi / 2, 4, 'X'), 12, 0.55, 0.55, 3.4, M_IRON)
# (round 41: rings of bulbs on the rim, then a big light on the hub, were tried; then the user: "I think we will take the
# light off": the wheel has no lights of its own, rule 02 #33a)
# (round 41, the user, on the plan round41/wheel_plan/2_wheel_proposed.png: "that concrete platform next to the Ferris
# wheel should be on the other side. And the fence should be on top of it. So that it sort of guides you from left to
# right. So you come by the ticket, you come around, you get on, then you get off on the east side"; "Yes, that was
# right") the boarding platform on the plaza's side of the wheel, where she comes in from the path, between the frame's
# feet: steps up at its west end, beside the booth, into a lane between the railing along its far side and a rail
# down its middle; a gap in that rail at the middle, where the gondolas come down; off along the wheel's side of it and
# down the steps at its east end. She stands on it (scene 'raised').
PL_X, PL_Z0, PL_Z1 = 4.8, wz - 4.4, wz - 1.0                                   # (half its length; its far and near edges)
LANE_Z = wz - 2.9                                                             # (the rail down its middle; round 41, the user: "move one of the railings slightly closer to the Ferris wheel" — 1.8 m clear of the cabins, room to step off and walk to the east steps past the frame's foot)
stand.box(V(wx, (PL_Z0 + PL_Z1) / 2, FH + 0.25), (1, 0), (0, 1), PL_X, (PL_Z1 - PL_Z0) / 2, 0.25, M_STONE)
stand.box(V(wx - PL_X - 0.3, (PL_Z0 + LANE_Z) / 2, FH + 0.125), (1, 0), (0, 1), 0.3, (LANE_Z - PL_Z0) / 2, 0.125, M_STONE)   # west step
# (round 41, the user: "she should get off on the [same] side of the railing. So that it's the same way she walked on…
# She walks on, then goes through the gap, and then comes out of the gap, and walks in the other direction") no east
# step: out of the gondola back through the gap into the lane she came along, and back down the west steps
# (then: "the steps are missing from the little stand… take the steps on the other side and continue them so that you
# could theoretically walk forward, up, keep walking, then walk down") the same step at the lane's east end too
stand.box(V(wx + PL_X + 0.3, (PL_Z0 + LANE_Z) / 2, FH + 0.125), (1, 0), (0, 1), 0.3, (LANE_Z - PL_Z0) / 2, 0.125, M_STONE)   # east step
scene.setdefault('raised', []).append([round(wx - PL_X, 3), round(PL_Z0, 3), round(wx + PL_X, 3), round(PL_Z1, 3), round(FH + 0.5, 3)])
scene['raised'].append([round(wx - PL_X - 0.6, 3), round(PL_Z0, 3), round(wx - PL_X, 3), round(LANE_Z, 3), round(FH + 0.25, 3)])
scene['raised'].append([round(wx + PL_X, 3), round(PL_Z0, 3), round(wx + PL_X + 0.6, 3), round(LANE_Z, 3), round(FH + 0.25, 3)])
# its rails: iron posts and a top rail, along the far side, and down the middle either side of the boarding gap
for (xa_, xb_, zr_) in ((wx - PL_X + 0.1, wx + PL_X - 0.1, PL_Z0 + 0.1), (wx - PL_X + 0.1, wx - 1.4, LANE_Z), (wx + 1.4, wx + PL_X - 0.1, LANE_Z)):
    stand.box(V((xa_ + xb_) / 2, zr_, FH + 1.5), (1, 0), (0, 1), (xb_ - xa_) / 2, 0.03, 0.03, M_IRON)
    stand.box(V((xa_ + xb_) / 2, zr_, FH + 1.05), (1, 0), (0, 1), (xb_ - xa_) / 2, 0.015, 0.015, M_IRON)
    nps_ = max(2, int(math.ceil((xb_ - xa_) / 1.6)) + 1)
    for k_ in range(nps_):
        xp_ = xa_ + (xb_ - xa_) * k_ / (nps_ - 1)
        stand.cone(Matrix.Translation(V(xp_, zr_, FH + 1.0)), 6, 0.03, 0.03, 1.0, M_IRON)
    fair_solid.append((xa_ - 0.05, zr_ - 0.08, xb_ + 0.05, zr_ + 0.08))
# (round 41, the user: "when she goes to the ticket counter, make the ticket counter more detailed, and she shouldn't
# be able to walk into it"; then "have it on the other side and have the man facing the customer and make sure that
# there is room inside for him to stand. Currently, it's a box that he is standing in, and it looks like he doesn't have
# legs") the booth by the platform's other front corner, clear of it, its window out to the terrace: hollow, thin
# walls and a floor, the counter at waist height with a white ledge out in front, the window open above it, white
# corner posts, a red and white awning, the name board, a door at the side; Ramon inside behind the counter, facing
# the customer (north_data.py). Solid from outside (fair_solid).
# (the terrace drops away a metre or two south of the platform: the booth stands by the platform's west end, its window
# west onto the open terrace, where people come from)
bx_, bz_ = wx - 4.4, wz + 3.9                                                                       # its middle (round 41, the user: "move the ticket booth back to where it was")
FN_, AL_ = (-1.0, 0.0), (0.0, 1.0)                                                                  # out of its window; along it
BW_, BD_ = 1.0, 0.8                                                                                  # (half its width along the window, half its depth)


def bp_(f, a, h=0.0):
    """A point of the booth: f out of the window (+) or back, a along its front, h up."""
    return V(bx_ + FN_[0] * f + AL_[0] * a, bz_ + FN_[1] * f + AL_[1] * a, FH + h)


AX_A, AX_F = (AL_[0], -AL_[1]), (FN_[0], -FN_[1])                                                   # (the box's axes, as Blender's)
stand.box(bp_(0, 0, 0.02), AX_A, AX_F, BW_, BD_, 0.02, M_WOODEN)                                     # the floor
stand.box(bp_(BD_, 0, 0.52), AX_A, AX_F, BW_, 0.03, 0.52, M_GONDOLA[1])                              # the front, to the counter
stand.box(bp_(-BD_, 0, 0.52), AX_A, AX_F, BW_, 0.03, 0.52, M_GONDOLA[1])                             # the back
stand.box(bp_(0, -BW_, 0.52), AX_A, AX_F, 0.03, BD_, 0.52, M_GONDOLA[1])                             # one side
stand.box(bp_(0.3, BW_, 0.52), AX_A, AX_F, 0.03, BD_ - 0.3, 0.52, M_GONDOLA[1])                      # the other, with the door
stand.box(bp_(-BD_ + 0.25, BW_, 1.6), AX_A, AX_F, 0.03, 0.25, 0.56, M_GONDOLA[1])
stand.box(bp_(-0.25, BW_ + 0.01, 0.98), AX_A, AX_F, 0.015, 0.25, 0.97, M_WOOD_DOOR)                  # the door
stand.box(bp_(BD_ + 0.12, 0, 1.06), AX_A, AX_F, BW_ + 0.05, 0.16, 0.03, M_WHEEL_W)                    # the counter's ledge
stand.box(bp_(BD_ - 0.12, 0, 1.0), AX_A, AX_F, BW_ - 0.05, 0.12, 0.03, M_WHEEL_W)                     # and inside
stand.box(bp_(-BD_, 0, 1.6), AX_A, AX_F, BW_, 0.03, 0.56, M_GONDOLA[1])                              # the back wall, upper
stand.box(bp_(0, -BW_, 1.6), AX_A, AX_F, 0.03, BD_, 0.56, M_GONDOLA[1])                              # the far side, upper
for sf_ in (-1, 1):
    for sa_ in (-1, 1):
        stand.box(bp_(sf_ * (BD_ - 0.03), sa_ * (BW_ - 0.03), 1.6), AX_A, AX_F, 0.045, 0.045, 0.6, M_WHEEL_W)   # posts
stand.box(bp_(0, 0, 2.22), AX_A, AX_F, BW_ + 0.15, BD_ + 0.15, 0.06, M_WHEEL_W)                        # the roof
for k_ in range(8):                                                                                  # the awning
    a0_, a1_ = -BW_ - 0.1 + k_ * (2 * BW_ + 0.2) / 8, -BW_ - 0.1 + (k_ + 1) * (2 * BW_ + 0.2) / 8
    stand.face([bp_(BD_ + 0.15, a0_, 2.16), bp_(BD_ + 0.15, a1_, 2.16), bp_(BD_ + 0.7, a1_, 1.9), bp_(BD_ + 0.7, a0_, 1.9)],
               M_GONDOLA[0] if k_ % 2 == 0 else M_WHEEL_W, normal=(FN_[0] * 0.4, -FN_[1] * 0.4, 1))
stand.box(bp_(BD_, 0, 2.58), AX_A, AX_F, BW_, 0.03, 0.3, M_GONDOLA[1])                               # the name board
stand.box(bp_(BD_ + 0.04, -0.42, 0.6), AX_A, AX_F, 0.46, 0.015, 0.16, M_WHEEL_W)                     # the price plate
SIGN_ROT_ = math.atan2(FN_[0], FN_[1])                                                               # (lettering facing out)
city_objs.append(text_obj('GIRADABO', 0.26, M_SIGN_TEXT, bp_(BD_ + 0.04, 0, 2.63), SIGN_ROT_, 'WheelBoothSign'))
city_objs.append(text_obj('1 € · UNA VOLTA', 0.09, M_GONDOLA[1], bp_(BD_ + 0.065, -0.42, 0.6), SIGN_ROT_, 'WheelBoothPrice'))
fair_solid.append((bx_ - BD_ - 0.3, bz_ - BW_ - 0.05, bx_ + BD_ + 0.05, bz_ + BW_ + 0.05))
city_objs.append(stand.finish('WheelStand'))
rim = MB(uv=True)
for k in range(48):
    a0, a1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 1) / 48
    for sz in (-0.9, 0.9):
        p0 = V(wx + math.cos(a0) * WR, wz + sz, hub[2] + math.sin(a0) * WR)
        p1 = V(wx + math.cos(a1) * WR, wz + sz, hub[2] + math.sin(a1) * WR)
        rim.tube(p0, p1, 0.11, M_WHEEL_W, 6)
        if k % 2 == 0:
            rim.tube(V(wx, wz + sz * 1.4, hub[2]), p0, 0.035, M_WHEEL_W, 4)
    if k % 4 == 0:
        p = V(wx + math.cos(a0) * WR, wz, hub[2] + math.sin(a0) * WR)
        rim.tube(p + Vector((0, -0.9, 0)), p + Vector((0, 0.9, 0)), 0.06, M_WHEEL_W, 5)
city_objs.append(finish_at(rim, 'WheelRim', hub))
for g in range(NG):
    a = 2 * math.pi * g / NG - math.pi / 2              # gondola 0 at the bottom
    hang = (wx + math.cos(a) * WR, wz, hub[2] + math.sin(a) * WR)
    gm = MB(uv=True)
    p = V(*[hang[0], hang[1], 0]) + Vector((0, 0, hang[2]))
    body = p + Vector((0, 0, -1.55))
    # (round 41, the user: "there's a bar going through her head. Could you sit her a bit more in the middle") it hangs by
    # a short rod onto its roof, the posts carry the roof; no arms slanting down through the cabin
    gm.tube(p, body + Vector((0, 0, 1.36)), 0.045, M_IRON, 6)
    col = M_GONDOLA[g % len(M_GONDOLA)]
    # (round 26, the user: "the Ferris wheel is just a box. Fix it") a rounded tub hanging from two arms, a bench inside,
    # a little domed roof on four slim posts
    # (round 41, the user: "it looks like she's just sitting in the middle and there's not actually space for her to
    # sit, then her head is hitting the roof… more like a donut with a bottom. And the top needs to be flattened") open
    # inside: the tub's wall seen from outside and from in, a white ring of a rim, a floor; the bench across its back
    # with a low back, so she sits facing out with room for her legs; a flatter roof, higher
    # (round 41, the user: "the tub should be hollow": its rounded bottom bulged up inside to near the rim) a bowl under
    # the floor now, nothing above it
    gm.cone(Matrix.Translation(body + Vector((0, 0, -0.48))), 14, 0.35, 0.95, 0.26, col)                             # the tub's bottom
    # (round 41, the user: "She also doesn't have any arms in the gondola": the rim came to her shoulders and hid them;
    # its sides are lower now, to her lap, so she sits in it with her arms on her knees in view)
    gm.cone(Matrix.Translation(body + Vector((0, 0, -0.13))), 14, 1.0, 0.95, 0.44, col, caps=False)                  # its sides, outside
    RI_, NS_ = 0.9, 14
    for k_ in range(NS_):
        a0_, a1_ = 2 * math.pi * k_ / NS_, 2 * math.pi * (k_ + 1) / NS_
        c0_, c1_ = Vector((math.cos(a0_), math.sin(a0_), 0)), Vector((math.cos(a1_), math.sin(a1_), 0))
        mid_ = (c0_ + c1_).normalized()
        gm.face([body + c0_ * RI_ + Vector((0, 0, -0.33)), body + c1_ * RI_ + Vector((0, 0, -0.33)),
                 body + c1_ * RI_ + Vector((0, 0, 0.1)), body + c0_ * RI_ + Vector((0, 0, 0.1))], col, normal=-mid_)  # inside
        gm.face([body + c0_ * RI_ + Vector((0, 0, 0.1)), body + c1_ * RI_ + Vector((0, 0, 0.1)),
                 body + c1_ * 1.03 + Vector((0, 0, 0.1)), body + c0_ * 1.03 + Vector((0, 0, 0.1))], M_WHEEL_W, normal=(0, 0, 1))  # the rim
        gm.face([body + c0_ * 1.03 + Vector((0, 0, 0.04)), body + c1_ * 1.03 + Vector((0, 0, 0.04)),
                 body + c1_ * 1.03 + Vector((0, 0, 0.1)), body + c0_ * 1.03 + Vector((0, 0, 0.1))], M_WHEEL_W, normal=mid_)   # its edge
        gm.face([body + Vector((0, 0, -0.33)), body + c0_ * RI_ + Vector((0, 0, -0.33)), body + c1_ * RI_ + Vector((0, 0, -0.33))],
                M_WOODEN, normal=(0, 0, 1))                                                                         # the floor
    # a round seat in the middle: she sits at the centre, the city all round her
    gm.cone(Matrix.Translation(body + Vector((0, 0, -0.16))), 16, 0.24, 0.24, 0.34, M_WOODEN)                       # its stem
    gm.cone(Matrix.Translation(body + Vector((0, 0, -0.005))), 16, 0.3, 0.3, 0.03, M_WOODEN)                       # its top
    # (the user: "She also doesn't have any arms in the gondola") a little curved hand-rail in front of her, as in a
    # teacup ride, that she holds: her forearms and hands show over the rim (north.gd's marks hold it)
    # (round 41, the user: "the chair and the Ferris wheel should be turned around the other way": the rail on the
    # gondola's other side, as she faces it now, north.gd)
    rail_pts_ = [body + Vector((math.sin(a_) * 0.27, 0.04 + math.cos(a_) * 0.27, 0.21)) for a_ in [(-1.0 + 2.0 * k_ / 8) for k_ in range(9)]]
    for r0_, r1_ in zip(rail_pts_, rail_pts_[1:]):
        gm.tube(r0_, r1_, 0.018, M_WHEEL_W, 6)
    for r_ in (rail_pts_[0], rail_pts_[-1]):
        gm.tube(r_, r_ + Vector((0, 0, -0.54)), 0.016, M_WHEEL_W, 6)                                              # its legs
    # (round 41, the user: "go back to 4 bars and make them white. If they're not in the picture at every time, that's
    # fine") the roof's four posts, white like the wheel
    # (then: "make sure that the white bars… reach both the walls of the gondola and the roof. There are currently
    # small gaps") on the rim's ring, from its top up into the roof
    for kq_ in range(4):
        aq_ = math.pi / 4 + kq_ * math.pi / 2
        gm.cone(Matrix.Translation(body + Vector((math.cos(aq_) * 0.96, math.sin(aq_) * 0.96, 0.7))), 6, 0.025, 0.025, 1.24, M_WHEEL_W)
    gm.ico(Matrix.Translation(body + Vector((0, 0, 1.3))) @ Matrix.Diagonal((1.15, 1.08, 0.1, 1)), 1.0, col, 2)     # its flat roof
    city_objs.append(finish_at(gm, 'WheelGondola_%d' % g, hang))
north['wheel'] = {'hub': [round(v, 3) for v in hub], 'r': WR, 'n': NG, 'board': [wx, wz - 2.6], 'gate': [wx - 0.6, wz - 3.6],
                  'off': [wx + 0.4, (PL_Z0 + LANE_Z) / 2], 'gondola_drop': 1.55 + 0.55}     # (round 41: back in the lane she came by)
# (round 41: the platform on the north side now, against the wheel's own footprint; the frame's two north feet, outside
# the platform's ends, each their own)
fair_solid.append((wx - 5.6, wz - 0.9, wx + 5.6, wz + 2.0))
for sx_ in (-1, 1):
    fair_solid.append((wx + sx_ * 5.2 - 0.4, wz - 2.0, wx + sx_ * 5.2 + 0.4, wz - 1.2))

# --- the Talaia (1921): a mast with a long arm that lifts its cabin out over the edge (round 27: the arm its own
# object, TalaiaArm, pivoted on the mast: the game swings it slowly out over the drop and back)
tx, tz = N.TALAIA
tal = MB(uv=True)
tal.box(V(tx, tz, FH + 2.0), (1, 0), (0, 1), 1.6, 1.6, 2.0, M_RED)
tal.cone(Matrix.Translation(V(tx, tz, FH + 11.0)), 8, 0.55, 0.35, 18.0, M_RED)
city_objs.append(tal.finish('Talaia'))
tala = MB(uv=True)
arm_a = V(tx, tz, FH + 19.0)
arm_b = V(tx + 9.0, tz + 4.0, FH + 26.0)
tala.tube(arm_a, arm_b, 0.25, M_RED, 6)
tala.tube(V(tx, tz, FH + 21.5), arm_b, 0.08, M_IRON, 4)
tala.box(arm_b + Vector((0, 0, -1.6)), (1, 0), (0, 1), 1.1, 1.1, 0.9, M_WHEEL_W)
tala.box(arm_b + Vector((0, 0, -0.55)), (1, 0), (0, 1), 1.25, 1.25, 0.12, M_RED)
city_objs.append(finish_at(tala, 'TalaiaArm', arm_a))
fair_solid.append((tx - 1.8, tz - 1.8, tx + 1.8, tz + 1.8))

# --- (round 25) a coin telescope at the plateau's edge, looking out over the city: the classic tourist binocular viewer
# (a painted head with two eyepieces under a hood, two lenses in front, a coin box, on a post); the game lets her look
M_SCOPE = mat('ScopeGreen', '#2f6e5e', 0.45, 0.35)
# (round 35, the everything-visit: it stood on the terrace bench at (-52, -270), inside it, and 5 m back from the edge
# the parapet hid the city from its lenses; now at the railing, in the flower boxes' gap, the bench behind it)
# (round 41, the user: "Could it also be moved closer to the railing (but not up against it) so that I can look down
# lower") 0.6 m behind it (was a metre)
SCOPE = (-52.0, N.FAIR[3] - 0.6)            # (on the level, behind the plateau's edge railing; its lenses 0.25 m short of it)
scope_yaw = math.atan2(0.0 - SCOPE[0], 40.0 - SCOPE[1])             # (towards the middle of the city)
f_ = Vector((math.sin(scope_yaw), math.cos(scope_yaw)))
r_ = Vector((math.cos(scope_yaw), -math.sin(scope_yaw)))
sc_ = MB(uv=True)
gh_ = FH                                      # (on the funfair's own terrace floor, not the hill under it)


def SP(fw, rt, up):
    return V(SCOPE[0] + f_.x * fw + r_.x * rt, SCOPE[1] + f_.y * fw + r_.y * rt, gh_ + up)


U_, F2_ = (r_.x, -r_.y), (f_.x, -f_.y)
sc_.cone(Matrix.Translation(SP(0, 0, 0.06)), 12, 0.32, 0.26, 0.12, M_GREYSTONE)             # its foot
sc_.cone(Matrix.Translation(SP(0, 0, 0.62)), 10, 0.08, 0.07, 1.0, M_SCOPE)                  # the post
sc_.box(SP(0, 0, 1.18), U_, F2_, 0.1, 0.06, 0.08, M_SCOPE)                                  # the yoke
sc_.box(SP(0.02, 0, 1.38), U_, F2_, 0.27, 0.19, 0.15, M_SCOPE)                              # the head
sc_.box(SP(-0.17, 0, 1.47), U_, F2_, 0.25, 0.05, 0.07, M_SCOPE)                             # the hood over the eyes
for sd in (-0.11, 0.11):
    d3 = SP(0.32, sd, 1.4) - SP(0.2, sd, 1.4)
    sc_.cone(Matrix.Translation(SP(0.27, sd, 1.4)) @ Vector((0, 0, 1)).rotation_difference(d3.normalized()).to_matrix().to_4x4(),
             12, 0.075, 0.085, 0.16, M_SCOPE)                                                # the lenses' barrels
    sc_.cone(Matrix.Translation(SP(0.355, sd, 1.4)) @ Vector((0, 0, 1)).rotation_difference(d3.normalized()).to_matrix().to_4x4(),
             12, 0.06, 0.06, 0.012, M_GLASS)
    sc_.cone(Matrix.Translation(SP(-0.2, sd, 1.4)) @ Vector((0, 0, 1)).rotation_difference(d3.normalized()).to_matrix().to_4x4(),
             10, 0.04, 0.045, 0.09, M_IRON)                                                  # the eyepieces
sc_.box(SP(0.0, 0.3, 1.3), U_, F2_, 0.05, 0.1, 0.09, M_GREYSTONE)                           # the coin box
city_objs.append(sc_.finish('FunfairTelescope'))
solid(SCOPE[0] - 0.35, SCOPE[1] - 0.35, SCOPE[0] + 0.35, SCOPE[1] + 0.35)
north['telescope'] = [SCOPE[0], SCOPE[1], round(scope_yaw, 4), round(gh_, 3)]

# --- the Avió (1928): a red monoplane on an arm, circling out over the drop; the game turns AvioArm
ax_, az_ = N.AVIO
av = MB(uv=True)
av.cone(Matrix.Translation(V(ax_, az_, FH + 4.5)), 8, 0.7, 0.5, 9.0, M_GREYSTONE)
city_objs.append(av.finish('AvioPylon'))
arm = MB(uv=True)
pivot = (ax_, az_, FH + 9.0)
arm.tube(V(ax_, az_, FH + 9.0), V(ax_ + 7.0, az_, FH + 8.4), 0.12, M_IRON, 5)
pl = V(ax_ + 7.6, az_, FH + 7.6)
arm.tube(pl + Vector((0, 0, 0.8)), pl + Vector((0, 0, 0.2)), 0.04, M_IRON, 4)
arm.cone(Matrix.Translation(pl) @ Matrix.Rotation(math.pi / 2, 4, 'X'), 10, 0.5, 0.25, 3.6, M_PLANE_RED)       # fuselage
arm.box(pl + Vector((0, 0.3, 0.05)), (1, 0), (0, 1), 2.8, 0.45, 0.06, M_PLANE_RED)                               # wings
arm.box(pl + Vector((0, -1.6, 0.4)), (1, 0), (0, 1), 0.05, 0.35, 0.45, M_PLANE_RED)                              # tail fin
arm.box(pl + Vector((0, -1.6, 0.05)), (1, 0), (0, 1), 0.9, 0.3, 0.05, M_PLANE_RED)
arm.cone(Matrix.Translation(pl + Vector((0, 1.85, 0))) @ Matrix.Rotation(math.pi / 2, 4, 'X'), 8, 0.08, 0.08, 0.2, M_IRON)
city_objs.append(finish_at(arm, 'AvioArm', pivot))
fair_solid.append((ax_ - 1.0, az_ - 1.0, ax_ + 1.0, az_ + 1.0))

# --- the Carrusel (1928): horses under a striped roof, turned by the game (CarruselTop)
cx2, cz2 = N.CARRUSEL
car = MB(uv=True)
car.cone(Matrix.Translation(V(cx2, cz2, FH + 0.25)), 32, 5.0, 5.0, 0.5, M_GOLD)
city_objs.append(car.finish('CarruselBase'))
# (round 41, the user: "make the merry-go-round solid, so you can't run into it") its round base, a little outside it
scene.setdefault('solids', []).append([[round(cx2 + 5.1 * math.cos(a_), 2), round(cz2 + 5.1 * math.sin(a_), 2)]
                                       for a_ in [2 * math.pi * k_ / 20 for k_ in range(20)]])
top = MB(uv=True)
top.cone(Matrix.Translation(V(cx2, cz2, FH + 2.6)), 12, 0.45, 0.45, 4.6, M_GOLD)
top.cone(Matrix.Translation(V(cx2, cz2, FH + 5.3)), 32, 5.45, 0.3, 2.0, stripes_mat('#d9534f', '#f5ecd6'))
# (round 26: from the terrace the canopy read as a plain gold flying saucer: its rim striped like the roof, its
# underside cream, and a scalloped edge hanging from the rim)
top.cone(Matrix.Translation(V(cx2, cz2, FH + 4.4)), 32, 5.42, 5.42, 0.6, stripes_mat('#d9534f', '#f5ecd6'))
top.cone(Matrix.Translation(V(cx2, cz2, FH + 4.07)), 32, 5.3, 5.3, 0.06, mat('CarruselCeil', '#f5ecd6', 0.8))
for k in range(16):
    a_ = 2 * math.pi * (k + 0.5) / 16
    top.ico(Matrix.Translation(V(cx2 + math.cos(a_) * 5.42, cz2 + math.sin(a_) * 5.42, FH + 4.05)) @ Matrix.Diagonal((0.55, 0.55, 0.3, 1)),
            1.0, mat('CarruselFringe', '#d9534f', 0.8), 1)
for k in range(12):
    a = 2 * math.pi * k / 12
    p = V(cx2 + math.cos(a) * 3.8, cz2 + math.sin(a) * 3.8, FH + 0.5)
    top.tube(p, p + Vector((0, 0, 3.6)), 0.04, M_GOLD, 5)
    horse = p + Vector((0, 0, 1.25 + 0.25 * (k % 2)))
    hd = Vector((-math.sin(a), -math.cos(a), 0))
    top.box(horse, (hd.x, hd.y), (math.cos(a), -math.sin(a)), 0.55, 0.17, 0.22, M_WHITE)
    top.box(horse + hd * 0.55 + Vector((0, 0, 0.3)), (hd.x, hd.y), (math.cos(a), -math.sin(a)), 0.14, 0.12, 0.28, M_WHITE)
city_objs.append(finish_at(top, 'CarruselTop', (cx2, cz2, FH)))
fair_solid.append((cx2 - 4.0, cz2 - 4.0, cx2 + 4.0, cz2 + 4.0))

# --- the Museu d'Autòmats: the old theatre of 1909, a modernista front
mx, mz = N.AUTOMATA
mus = MB(uv=True)
mus.box(V(mx, mz, FH + 3.2), (1, 0), (0, 1), 6.0, 4.0, 3.2, M_CREAM)
mus.box(V(mx, mz + 4.02, FH + 1.4), (1, 0), (0, 1), 1.0, 0.04, 1.4, M_WOOD_DOOR)
for sx in (-3.6, 3.6):
    mus.box(V(mx + sx, mz + 4.02, FH + 3.0), (1, 0), (0, 1), 0.6, 0.04, 1.0, M_GLASS)
mus.face([V(mx - 6.0, mz + 4.0, FH + 6.4), V(mx + 6.0, mz + 4.0, FH + 6.4), V(mx + 3.0, mz + 4.0, FH + 8.6), V(mx - 3.0, mz + 4.0, FH + 8.6)],
         M_CREAM, normal=(0, -1, 0))
mus.box(V(mx, mz + 4.05, FH + 7.2), (1, 0), (0, 1), 3.0, 0.03, 0.45, M_TRENC)
mus.box(V(mx, mz, FH + 6.5), (1, 0), (0, 1), 6.1, 4.1, 0.12, M_ROOF_TILE)
# (round 41, the user: fix the floating name: cream letters 12 cm off a cream front read as hanging in the air; now a
# dark green name board on the front, the letters on it)
mus.box(V(mx, mz + 4.03, FH + 5.4), (1, 0), (0, 1), 1.6, 0.03, 0.26, M_SHUT_GREEN)
city_objs.append(mus.finish('MuseuAutomats'))
city_objs.append(text_obj("MUSEU D'AUTÒMATS", 0.22, M_SIGN_TEXT, V(mx, mz + 4.075, FH + 5.4), 0.0, 'AutomataSign'))
fair_solid.append((mx - 6.0, mz - 4.0, mx + 6.0, mz + 4.0))
cam_building(mx - 6.0, mz - 4.0, mx + 6.0, mz + 4.0, FH - 0.3, FH + 7.0)            # (the automata museum)

# --- the top station of the funicular, at the terrace's south edge (the track arrives beneath it, through the portal)
sx_, sz_ = N.CABLE_TOP
# (round 25) from Meshy: a little modernist station, its brick arch and clock to the funfair (the track comes in below)
# (round 41, the user: "lower the funicular station at the top and then make it walkable so she can walk right up to the
# turnstile. The current stony base would need to be underground, mostly. It's fine to have the little lip… she needs to
# be able to run under that green awning and next to the red thing so that she can press E and go back down") its stone
# base (1.3 m of the model as fitted here) sunk all but a 0.17 m lip; on the base's top she walks in beside the red car,
# under the green awning, to the turnstile in the arch. Measured from the model (fitted 5.3 x 7.2 m, its middle at
# ST_O): the car x -2.0..-0.4, z -3.2..-1.6 of it; the arch's piers at z -1.4; the turnstile just inside, x -0.4..0.4,
# z -1.2..-0.6; the awning over x 1.2..2.2 (rule 06 #96a)
ST_SINK = 1.08
ST_O = (sx_, sz_ + 1.0)
ST_LIP = FH + 1.30 - 0.05 - ST_SINK
st_meshy = meshy_house('cable_station.glb', (sx_ - 4.5, sz_ - 2.6, sx_ + 4.5, sz_ + 4.6), FH - ST_SINK, 'MeshyBuilding_cabletop', max_h=10.0, rot=math.pi)
if not st_meshy:
    stt = MB(uv=True)
    stt.box(V(sx_, sz_ + 1.0, FH + 2.4), (1, 0), (0, 1), 4.5, 3.6, 2.4, M_CREAM)
    stt.box(V(sx_, sz_ + 1.0, FH + 4.95), (1, 0), (0, 1), 4.9, 4.0, 0.15, M_RED)
    stt.box(V(sx_, sz_ + 4.62, FH + 2.0), (1, 0), (0, 1), 2.2, 0.03, 2.0, M_GLASS)
    city_objs.append(stt.finish('CableTopStation'))
    city_objs.append(text_obj('FUNICULAR', 0.4, M_SIGN_TEXT, V(sx_, sz_ - 2.7, FH + 4.15), math.pi, 'FuniTopSign'))   # (round 40: the stand-in's only)
if st_meshy:
    ox_, oz_ = ST_O
    scene.setdefault('flats', []).append([round(ox_ - 2.64, 2), round(oz_ - 3.47, 2), round(ox_ + 2.64, 2), round(oz_ + 3.33, 2),
                                          round(ST_LIP + 0.012, 3), round(ST_LIP + 0.012, 3)])    # (the base's top, walked on)
    fair_solid.append((ox_ - 2.5, oz_ - 1.25, ox_ + 2.5, oz_ + 3.35))      # the building behind the arch, the turnstile in it
    fair_solid.append((ox_ - 2.1, oz_ - 3.25, ox_ - 0.35, oz_ - 1.25))     # the red car
    fair_solid.append((ox_ + 1.2, oz_ - 1.65, ox_ + 2.5, oz_ - 1.25))      # the arch's east pier, under the awning
    cam_building(ox_ - 2.5, oz_ - 1.25, ox_ + 2.5, oz_ + 3.35, FH - 1.2, FH + 8.0)    # (the funicular's top station)
    cam_building(ox_ - 2.1, oz_ - 3.25, ox_ - 0.35, oz_ - 1.25, FH, FH + 2.5)
    # (round 41, the user: "there's green paint on the floor of the funicular station at the top… Can anything be done
    # about that?": the model's own painted lines, buried with its base at the bottom station) plain stone laid over the
    # base's top in front of the arch, the car standing on it
    # (then: "could you also put a border around it? Because it's currently open, it looks like it's floating") a solid
    # slab down to the plaza, framed on its three open sides by a grey stone border standing just proud of it
    stt2 = MB(uv=True)
    stt2.abox(ox_ - 2.5, -(oz_ - 1.25), FH - 0.02, ox_ + 2.5, -(oz_ - 3.33), ST_LIP + 0.012, M_STONE)
    BD2_ = 0.14
    for (x0b_, z0b_, x1b_, z1b_) in ((ox_ - 2.5 - BD2_, oz_ - 3.33 - BD2_, ox_ + 2.5 + BD2_, oz_ - 3.33),      # its front
                                     (ox_ - 2.5 - BD2_, oz_ - 3.33, ox_ - 2.5, oz_ - 1.25),                  # its sides
                                     (ox_ + 2.5, oz_ - 3.33, ox_ + 2.5 + BD2_, oz_ - 1.25)):
        stt2.abox(x0b_, -z0b_, FH - 0.02, x1b_, -z1b_, ST_LIP + 0.035, M_GREYSTONE)
    city_objs.append(stt2.finish('CableTopFloor'))
    st_door = (round(ox_ + 0.3, 2), round(oz_ - 2.0, 2))                 # (E: in front of the turnstile)
else:
    fair_solid.append((sx_ - 4.5, sz_ - 2.6, sx_ - 1.6, sz_ + 4.6))
    fair_solid.append((sx_ + 1.6, sz_ - 2.6, sx_ + 4.5, sz_ + 4.6))
    cam_building(sx_ - 4.5, sz_ - 2.6, sx_ + 4.5, sz_ + 4.6, FH - 0.3, FH + 8.0)         # (the funicular's top station)
    st_door = (sx_, sz_ - 3.0)

# (round 26) the funfair's plaza furnished: a striped ticket booth by the wheel, a churros kiosk, pennant flags on
# white poles, queue rails at the wheel's platform
fb_x, fb_z = WH['x'] + 7.5, WH['z'] + 3.0
fair.box(V(fb_x, fb_z, FH + 1.3), (1, 0), (0, 1), 1.1, 1.1, 1.3, stripes_mat('#d9534f', '#f5ecd6'))
fair.box(V(fb_x, fb_z, FH + 2.75), (1, 0), (0, 1), 1.35, 1.35, 0.14, M_RED)
fair.cone(Matrix.Translation(V(fb_x, fb_z, FH + 3.3)), 4, 1.3, 0.1, 0.8, M_RED)
fair.box(V(fb_x, fb_z + 1.12, FH + 1.6), (1, 0), (0, 1), 0.55, 0.03, 0.35, M_GLASS)
city_objs.append(text_obj('TIQUETS', 0.16, M_SIGN_TEXT, V(fb_x, fb_z + 1.16, FH + 2.5), 0.0, 'FairTicketSign'))
solid(fb_x - 1.2, fb_z - 1.2, fb_x + 1.2, fb_z + 1.2)
ck_x, ck_z = -87.0, -296.5                    # (round 35: by the path's arrival, under the wheel)
fair.box(V(ck_x, ck_z, FH + 1.25), (1, 0), (0, 1), 1.5, 1.0, 1.25, mat('KioskCream', '#f5ecd6', 0.85))
fair.box(V(ck_x, ck_z, FH + 2.7), (1, 0), (0, 1), 1.75, 1.25, 0.12, stripes_mat('#e87a2f', '#f5ecd6'))
fair.box(V(ck_x, ck_z + 1.02, FH + 1.5), (1, 0), (0, 1), 0.8, 0.03, 0.4, M_GLASS)
city_objs.append(text_obj('XURRERIA', 0.15, M_SIGN_TEXT, V(ck_x, ck_z + 1.06, FH + 2.35), 0.0, 'FairChurrosSign'))
solid(ck_x - 1.6, ck_z - 1.1, ck_x + 1.6, ck_z + 1.1)
f_rng = random.Random(1901)
# (round 35: re-spaced with the smaller plateau, PATH_RULES E4)
POLES_ = [(WH['x'] - 8.0, WH['z'] + 5.5), (N.CARRUSEL[0] + 7.0, N.CARRUSEL[1] - 3.0), (-48.0, -288.0), (-58.0, -283.0)]
for (px2, pz2) in POLES_:
    fair.cone(Matrix.Translation(V(px2, pz2, FH + 2.6)), 6, 0.05, 0.07, 5.2, M_WHEEL_W)
    for j in range(3):
        a_ = f_rng.uniform(0, 6.28)
        fair.box(V(px2 + math.cos(a_) * 0.35, pz2 + math.sin(a_) * 0.35, FH + 4.6 - j * 0.5), (math.cos(a_ + 1.57), math.sin(a_ + 1.57)),
                 (math.cos(a_), -math.sin(a_)), 0.3, 0.015, 0.12, mat('Pennant%d' % (j % 3), ['#d9534f', '#f2c84b', '#3a7bd5'][j % 3], 0.85))
    solid(px2 - 0.15, pz2 - 0.15, px2 + 0.15, pz2 + 0.15)
# (round 41: the queue rails are on the platform now, its own railings)
# (round 27, from the 2D game) bunting strung across the plaza between the pennant poles, swinging low in the middle
b_rng = random.Random(1902)
done_ = set()
for i_, (ax_, az_) in enumerate(POLES_):
    j_, (bx2_, bz2_) = min(((j2, p2) for j2, p2 in enumerate(POLES_) if j2 != i_ and (j2, i_) not in done_),
                           key=lambda t: math.hypot(t[1][0] - ax_, t[1][1] - az_), default=(None, (0, 0)))
    if j_ is None or math.hypot(bx2_ - ax_, bz2_ - az_) > 46.0:
        continue
    done_.add((i_, j_))
    segs_ = 14
    dd_ = math.hypot(bx2_ - ax_, bz2_ - az_)
    for k_ in range(segs_):
        t0_, t1_ = k_ / segs_, (k_ + 1) / segs_
        p0_ = V(ax_ + (bx2_ - ax_) * t0_, az_ + (bz2_ - az_) * t0_, FH + 5.1 - math.sin(math.pi * t0_) * dd_ * 0.055)
        p1_ = V(ax_ + (bx2_ - ax_) * t1_, az_ + (bz2_ - az_) * t1_, FH + 5.1 - math.sin(math.pi * t1_) * dd_ * 0.055)
        fair.tube(p0_, p1_, 0.012, M_IRON, 4)
        fm_ = (p0_ + p1_) / 2
        ub_ = ((bx2_ - ax_) / dd_, -(bz2_ - az_) / dd_)
        fair.box(fm_ + Vector((0, 0, -0.14)), ub_, (-ub_[1], ub_[0]), 0.11, 0.008, 0.14,
                 mat('Pennant%d' % (k_ % 3), ['#d9534f', '#f2c84b', '#3a7bd5'][k_ % 3], 0.85))
# and flower boxes of geraniums along the edge wall, where the whole city lies below
M_GERL = mat('GeraniumLeaf', '#3f6e2e', 0.9)
M_GERF = mat('GeraniumRed', '#c93b3b', 0.8)
FBZ_ = N.FAIR[3] - 1.3
for fx_ in range(-100, -33, 9):
    if -73 <= fx_ <= -58 or -55 <= fx_ <= -49 or abs(fx_ - WH['x'] - 1.4) < 2.0:   # (not the station, the telescope, the queue)
        continue
    fair.box(V(fx_, FBZ_, FH + 0.22), (1, 0), (0, 1), 0.62, 0.21, 0.22, M_STONE)
    fair.ico(Matrix.Translation(V(fx_, FBZ_, FH + 0.52)) @ Matrix.Diagonal((0.6, 0.2, 0.14, 1)), 1.0, M_GERL, 1)
    for gk_ in range(3):
        fair.ico(Matrix.Translation(V(fx_ - 0.4 + gk_ * 0.4, FBZ_ + b_rng.uniform(-0.08, 0.08), FH + 0.62)) @
                 Matrix.Diagonal((0.1, 0.1, 0.08, 1)), 1.0, M_GERF, 1)
    solid(fx_ - 0.72, FBZ_ - 0.25, fx_ + 0.72, FBZ_ + 0.25)
# benches and lamps round the terrace
for (bx, bz, ang) in ((-104.0, -279.5, 0.0), (-47.5, -279.5, 0.0), (-33.5, -298.0, math.pi / 2), (-84.0, -300.5, math.pi)):
    fair.box(V(bx, bz, FH + 0.45), (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang)), 0.9, 0.22, 0.05, M_WOODEN)
    fair.box(V(bx, bz, FH + 0.22), (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang)), 0.8, 0.18, 0.22, M_IRON)
# (round 41, the user: "put some lamp poles up on the amusement park plaza in tasteful locations… lights, like fairy
# lights, hanging from a chain somewhere"; then "Could the fairy lights be put around the edges? Just slightly in from
# the fences?… the lamps… 3 sort of in the middle, then 2 on the edges a bit back… balanced and not too close to other
# things… enough light that it all adds up. And there aren't any incredibly dark bits") (rule 02 #33b)
# the city's lamp: three through the middle (between the wheel and the churros kiosk; on the church door's line;
# beside the Talaia, clear of the Avió's swing overhead), two at the sides set back (by the carousel; by the museum's
# bench)
FAIR_LAMPS = [(-86.0, -289.0), (-63.0, -289.5), (-43.0, -287.5), (-101.5, -301.0), (-34.5, -300.8)]
for i3_, (lx3_, lz3_) in enumerate(FAIR_LAMPS):
    base_ = V(lx3_, lz3_, FH)
    if MESHY_LAMP:
        meshy_mesh('lamp.glb', 4000, 'base')
        meshy_place('lamp.glb', 4000, 'base', 4.2, base_, 0.0, 'MeshyLamp_fair%d' % i3_, 1024)
        ltp_ = MESHY_TOP['lamp.glb'] * 4.2 + base_
        scene['lamps'].append({'pos': [lx3_, lz3_], 'light': [round(ltp_.x, 3), round(ltp_.z - 0.15, 3), round(-ltp_.y, 3)]})
    else:
        fair.cone(Matrix.Translation(base_ + Vector((0, 0, 1.9))), 8, 0.07, 0.045, 3.6, M_IRON)
        fair.abox(base_.x - 0.16, base_.y - 0.16, base_.z + 3.3, base_.x + 0.16, base_.y + 0.16, base_.z + 3.7, mat('LampGlow', '#f6e2b8', 0.3))
        scene['lamps'].append({'pos': [lx3_, lz3_], 'light': [round(base_.x, 3), round(base_.z + 3.4, 3), round(-base_.y, 3)]})
    solid(lx3_ - 0.2, lz3_ - 0.2, lx3_ + 0.2, lz3_ + 0.2)
# the fairy lights: round the edges about a metre in from the railings, on thin posts (and on the pennant pole where the
# line meets it), across the hill path's way in; broken where a building stands at the edge (the funicular station, the
# church, the museum). The posts stand between the flower boxes, clear of the booths, benches and the telescope.
FE_S, FE_W, FE_E, FE_N = N.FAIR[3] - 1.0, N.FAIR[0] + 1.2, N.FAIR[2] - 1.2, N.FAIR[1] + 1.2
FAIRY_RUNS = [
    # from the church's west corner round the north-west, down the west side over the path's way in, along the south
    [(-80.5, FE_N), (-90.0, FE_N), (-99.0, FE_N), (FE_W, FE_N), (FE_W, -309.5), (FE_W, -300.5), (FE_W, -292.8),
     (FE_W, -284.0), (FE_W, FE_S), (-103.0, FE_S), (-97.0, FE_S), (-88.0, FE_S), (-79.5, FE_S), (-69.3, FE_S)],
    # from the funicular station's east side along the south, up the east side to the museum
    [(-62.7, FE_S), (-56.0, FE_S), (-49.5, FE_S), (-41.5, FE_S), (FE_E, FE_S), (FE_E, -288.0), (FE_E, -295.0), (FE_E, -301.8)],
    # behind the museum to the church's east corner
    [(FE_E, -312.2), (FE_E, FE_N), (-38.5, FE_N), (-45.5, FE_N)]]
M_FAIRY = mat('FairyBulb', '#ffe2a8', 0.3)
POLE_AT = [(round(px2, 1), round(pz2, 1)) for (px2, pz2) in POLES_]
TIE_H = 3.25
for run_ in FAIRY_RUNS:
    tops_ = []
    for (fx2_, fz2_) in run_:
        if (round(fx2_, 1), round(fz2_, 1)) not in POLE_AT:                # (the pennant pole carries it there)
            fair.cone(Matrix.Translation(V(fx2_, fz2_, FH + 1.7)), 6, 0.045, 0.035, 3.4, M_IRON)
            fair.sphere(Matrix.Translation(V(fx2_, fz2_, FH + 3.43)), 0.06, M_IRON, (6, 4))
            solid(fx2_ - 0.12, fz2_ - 0.12, fx2_ + 0.12, fz2_ + 0.12)
        tops_.append(V(fx2_, fz2_, FH + TIE_H))
    for pa_, pb_ in zip(tops_, tops_[1:]):
        span_ = (pb_ - pa_).length
        sag_ = 0.04 * span_
        nseg_ = max(8, int(span_ * 2))
        pts_ = [pa_.lerp(pb_, t_ / nseg_) - Vector((0, 0, sag_ * math.sin(math.pi * t_ / nseg_))) for t_ in range(nseg_ + 1)]
        for q0_, q1_ in zip(pts_, pts_[1:]):
            fair.tube(q0_, q1_, 0.01, M_IRON, 4)
        nb_ = int(span_ / 0.55)
        for kb_ in range(1, nb_):
            t_ = kb_ / nb_
            fair.sphere(Matrix.Translation(pa_.lerp(pb_, t_) - Vector((0, 0, sag_ * math.sin(math.pi * t_) + 0.06))), 0.045, M_FAIRY, (6, 4))
        mid_ = (pa_ + pb_) / 2 - Vector((0, 0, sag_ + 0.3))
        north.setdefault('fairy', []).append([round(mid_.x, 2), round(mid_.z, 2), round(-mid_.y, 2)])   # (x, h, z): a soft light under each span
city_objs.append(fair.finish('FunfairTerrace'))
for r in fair_solid:
    solid(*r)
north['fair'] = {'rect': list(N.FAIR), 'h': FH, 'path_gap': list(PATH_GAP)}
# (round 41, the user: "She also shouldn't be able to ride the bike down into the forest glade from the mountain path")
north['glade'] = list(N.GLADE_R)
# (round 27, the user: "Make sure she cannot ride the bike in the amusement park")
scene.setdefault('nobike', []).append([N.FAIR[0], N.FAIR[1], N.FAIR[2], N.FAIR[3]])

# ------------------------------------------------------------------ the Funicular del Tibidabo (round 27)
# (the user: "It is actually 'Tibidabo Funicular', can you follow real life, but stylised like the rest of the game")
# The cable car is gone. As on the real hill, a funicular climbs the flank: a single track on ballast with a passing
# loop halfway, sleepers, rails and the haul cable between them; at the top the track slips through a stone portal
# under the plateau's edge into the upper station. Two counterbalanced cars (CableCabin_0/1, moved by the game) in
# Tramvia blue and cream. (round 30, the user: no level crossings — the walking path keeps west of the line, and
# where it bends up against it a white lineside fence is the barrier.)
lx, lz = N.CABLE_LOW
hl = hz(lx, lz)
cab = MB(uv=True)
# (round 26, the user: the station sat on its pedestal in a field) a paved forecourt under and round the station, level
# with the ground pad (north.py), its model buried to its platform so the arch opens at street level
cab.face([V(lx - 6.5, lz - 6.0, hl + 0.04), V(lx + 6.5, lz - 6.0, hl + 0.04), V(lx + 6.5, lz + 4.4, hl + 0.04), V(lx - 6.5, lz + 4.4, hl + 0.04)],
         M_PANOT, normal=(0, 0, 1), uvscale=2.0)
for (q0, q1, nrm_) in (((lx - 6.5, lz - 6.0), (lx + 6.5, lz - 6.0), (0, -1, 0)), ((lx + 6.5, lz - 6.0), (lx + 6.5, lz + 4.4), (1, 0, 0)),
                       ((lx + 6.5, lz + 4.4), (lx - 6.5, lz + 4.4), (0, 1, 0)), ((lx - 6.5, lz + 4.4), (lx - 6.5, lz - 6.0), (-1, 0, 0))):
    cab.face([V(q0[0], q0[1], hl - 0.5), V(q1[0], q1[1], hl - 0.5), V(q1[0], q1[1], hl + 0.04), V(q0[0], q0[1], hl + 0.04)], M_KERB, normal=nrm_)
# (round 32, the user: "no parts jutting out" where footpaths meet the grass — the forecourt's front ended on the
# town's footpath as one bare 22 cm kerb face, a slab lip across the pavement. Two shallow steps along the whole
# front now, the way a station forecourt meets the street.)
st_h1 = hl + 0.04 - 0.11
cab.face([V(lx - 6.5, lz + 4.4, st_h1), V(lx + 6.5, lz + 4.4, st_h1), V(lx + 6.5, lz + 4.75, st_h1), V(lx - 6.5, lz + 4.75, st_h1)],
         M_PANOT, normal=(0, 0, 1), uvscale=2.0)
cab.face([V(lx + 6.5, lz + 4.75, 0.114), V(lx - 6.5, lz + 4.75, 0.114), V(lx - 6.5, lz + 4.75, st_h1), V(lx + 6.5, lz + 4.75, st_h1)],
         M_KERB, normal=(0, 1, 0))
# (round 34, the play-through: this loop's name was the top station's own, sx_ — the funicular's top door, and where she
# stepped off at the top, went to x 6.5, out on the hillside 72 m east of the station and the funfair)
for ck_ in (-6.5, 6.5):                                                    # the step's little end cheeks
    cab.face([V(lx + ck_, lz + 4.4, 0.114), V(lx + ck_, lz + 4.75, 0.114),
              V(lx + ck_, lz + 4.75, st_h1), V(lx + ck_, lz + 4.4, st_h1)], M_KERB, normal=(ck_, 0, 0))
scene.setdefault('flats', []).append([lx - 6.5, lz - 6.0, lx + 6.5, lz + 4.4, round(hl + 0.04, 3), round(hl + 0.04, 3)])
for lx2_ in (lx - 5.8, lx + 5.8):                                                               # a lamp either side of the apron
    base_ = V(lx2_, lz + 3.6, hl + 0.04)
    if MESHY_LAMP:
        meshy_mesh('lamp.glb', 4000, 'base')
        meshy_place('lamp.glb', 4000, 'base', 4.2, base_, 0.0, 'MeshyLamp_cable%d' % int(lx2_), 1024)
        ltp_ = MESHY_TOP['lamp.glb'] * 4.2 + base_
        scene['lamps'].append({'pos': [round(lx2_, 3), round(lz + 3.6, 3)], 'light': [round(ltp_.x, 3), round(ltp_.z - 0.15, 3), round(-ltp_.y, 3)]})
    solid(lx2_ - 0.2, lz + 3.4, lx2_ + 0.2, lz + 3.8)
# (round 25) from Meshy, the same little station as at the top, its arch and clock to the city
# (round 26, the user: "Bring the bottom cable car down so it's sitting on the pavement": the model's own stone
# pedestal is buried, so its platform and arch open at street level onto the paved apron)
if not meshy_house('cable_station.glb', (lx - 5.0, lz - 4.0, lx + 5.0, lz + 4.0), hl - 2.3, 'MeshyBuilding_cablelow', max_h=10.0):
    cab.box(V(lx, lz, hl + 2.6), (1, 0), (0, 1), 5.0, 4.0, 2.6, M_CREAM)
    cab.box(V(lx, lz, hl + 5.35), (1, 0), (0, 1), 5.4, 4.4, 0.15, M_RED)
    cab.box(V(lx, lz + 4.03, hl + 1.2), (1, 0), (0, 1), 1.0, 0.03, 1.2, M_WOOD_DOOR)
    cab.box(V(lx + 2.7, lz + 4.03, hl + 1.5), (1, 0), (0, 1), 0.9, 0.03, 0.6, M_SHUT_BROWN)          # the shuttered ticket window
    city_objs.append(text_obj('TAQUILLA TANCADA', 0.13, M_SIGN_TEXT, V(lx + 2.7, lz + 4.08, hl + 2.35), 0.0, 'CableClosedSign'))
    # (round 40, the user: "Just make it not be floating text": its name was placed for this stand-in's front, and
    # beside the Meshy station it hung in the air — only the stand-in carries it)
    city_objs.append(text_obj('FUNICULAR DEL TIBIDABO', 0.34, M_PLAQUE_TEXT, V(lx, lz + 4.12, hl + 4.3), 0.0, 'FuniLowSign'))
# (round 28, the user: the station should plainly have a ticket entrance that is shut — you only board with the
# Amic del Park card) a little wooden ticket booth against the station's wall, its shutter down, a worn ledge,
# TAQUILLA painted over the window and a hand-written TANCAT card pinned to the shutter
tq_x, tq_z = lx - 4.1, lz + 2.9
tq = MB(uv=True)
tq.box(V(tq_x, tq_z, hl + 1.2), (1, 0), (0, 1), 0.72, 0.6, 1.2, M_CREAM)                   # the booth
tq.box(V(tq_x, tq_z, hl + 2.49), (1, 0), (0, 1), 0.86, 0.74, 0.09, M_RED)                  # its flat tile cap
tq.box(V(tq_x, tq_z + 0.61, hl + 1.5), (1, 0), (0, 1), 0.4, 0.015, 0.38, M_SHUT_BROWN)     # the shutter, down
tq.box(V(tq_x, tq_z + 0.64, hl + 1.07), (1, 0), (0, 1), 0.48, 0.07, 0.04, M_WOODEN)        # the ledge
tq.box(V(tq_x, tq_z + 0.615, hl + 2.14), (1, 0), (0, 1), 0.5, 0.012, 0.14, mat('TaquillaBoard', '#2e4a3a', 0.8))   # the name board
city_objs.append(tq.finish('FuniTaquilla'))
city_objs.append(text_obj('TAQUILLA', 0.12, M_PLAQUE_TEXT, V(tq_x, tq_z + 0.64, hl + 2.14), 0.0, 'FuniTaquillaSign'))
city_objs.append(text_obj('TANCAT', 0.09, M_PLAQUE_TEXT, V(tq_x, tq_z + 0.63, hl + 1.52), 0.0, 'FuniTancatSign'))
solid(tq_x - 0.75, tq_z - 0.62, tq_x + 0.75, tq_z + 0.62)
# (round 41: the play-through's camera ended up inside it at night; part of the station, so a camera wall, 03 #16)
cam_building(tq_x - 0.86, tq_z - 0.74, tq_x + 0.86, tq_z + 0.74, hl, hl + 2.6)
city_objs.append(cab.finish('FuniLowStation'))
def model_outline(prefix, z0, z1):
    """(round 40) the outline round a model's walls between two heights (Blender z): the convex hull of its vertices
    there, in engine metres — so what stops her is the building, not the plot it was fitted into."""
    pts_ = []
    dg_ = bpy.context.evaluated_depsgraph_get()
    for ob_ in bpy.context.scene.objects:
        if ob_.type != 'MESH' or not ob_.name.startswith(prefix):
            continue
        me_ = ob_.evaluated_get(dg_).to_mesh()
        mw_ = ob_.matrix_world
        for v_ in me_.vertices:
            w_ = mw_ @ v_.co
            if z0 <= w_.z <= z1:
                pts_.append((round(w_.x, 2), round(-w_.y, 2)))
        ob_.evaluated_get(dg_).to_mesh_clear()
    pts_ = sorted(set(pts_))
    if len(pts_) < 3:
        return None
    def cr_(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo_, hi_ = [], []
    for p_ in pts_:
        while len(lo_) >= 2 and cr_(lo_[-2], lo_[-1], p_) <= 0:
            lo_.pop()
        lo_.append(p_)
    for p_ in reversed(pts_):
        while len(hi_) >= 2 and cr_(hi_[-2], hi_[-1], p_) <= 0:
            hi_.pop()
        hi_.append(p_)
    return lo_[:-1] + hi_[:-1]


# (round 40, the user: "I should be able to run right up to it… there's all of these invisible walls around the station")
# it stopped her at the 10 x 8 m plot the Meshy model was fitted into: now at the model's own walls, at waist height
_lso = model_outline('MeshyBuilding_cablelow', hl + 0.3, hl + 2.0)
if _lso:
    scene.setdefault('solids', []).append([[round(a_, 2), round(b_, 2)] for a_, b_ in _lso])
    print('PARK funicular low station: outline of %d points, %.1f x %.1f m' % (len(_lso), max(q[0] for q in _lso) - min(q[0] for q in _lso),
                                                                          max(q[1] for q in _lso) - min(q[1] for q in _lso)))
else:
    solid(lx - 5.0, lz - 4.0, lx + 5.0, lz + 4.0)
cam_building(lx - 5.0, lz - 4.0, lx + 5.0, lz + 4.0, hl - 0.3, hl + 7.0)              # (the funicular's low station)
# (round 40, the user: "her feet sink into the ground around the cable car station. Because it's elevated") she
# stands on the forecourt's front steps too, not on the ground under them
scene['flats'].append([lx - 6.5, lz + 4.4, lx + 6.5, lz + 4.75, round(st_h1, 3), round(st_h1, 3)])
door_low = (lx - 2.2, lz + 4.6)

M_FUNI = mat('FuniBlue', '#2b5d9e', 0.5, 0.1)
M_FUNI_LAMP = mat('FuniLamp', '#f6e2b8', 0.3)
M_DARKIN = mat('PortalDark', '#141210', 1.0)
FZ0, FZ1 = N.FUNI_Z0, N.FUNI_Z1


def funi_off(z):
    """The passing loop: how far each track swings out from the line at z (0 beyond the loop)."""
    t = (z - FZ0) / (FZ1 - FZ0)
    return 1.05 * (N.smooth(0.34, 0.42, t) - N.smooth(0.58, 0.66, t))


# (round 41, the user: "the railway track now looks very simple… a bit more cartoonish. Could you make it a bit more
# realistic?… maybe less chunky, maybe the gray needs to be a gravel texture. And the beams… More detailed") the track
# as a real one: stony ballast heaped to the sleepers' tops with sloping shoulders; timber sleepers 0.75 m apart, lying
# on the slope; flat-bottomed rails (foot, web, a bright worn head) on steel base plates; the haul cable, thin, running
# over little rollers between the rails. The rails' tops stay where the cars ride (profile + 0.115).


def _ballast_px():
    rr_ = random.Random(1158)
    C_, M_ = 9, 28                                    # (9-pixel stones, 28 across: the 252-pixel picture)
    pts_ = {(i, j): (i * C_ + rr_.uniform(0, C_), j * C_ + rr_.uniform(0, C_), rr_.uniform(0.72, 1.08),
                     rr_.choice(((0.56, 0.54, 0.51), (0.62, 0.58, 0.52), (0.5, 0.5, 0.5), (0.66, 0.63, 0.58), (0.47, 0.44, 0.4))))
            for i in range(M_) for j in range(M_)}

    def fn(x, y):
        ci, cj = x // C_, y // C_
        d1, d2, best = 1e9, 1e9, None
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                gi, gj = ci + di, cj + dj
                q = pts_[(gi % M_, gj % M_)]
                dx_ = x - (q[0] + (gi - gi % M_) * C_)          # (the cells repeat every M_, so the picture tiles)
                dy_ = y - (q[1] + (gj - gj % M_) * C_)
                d = dx_ * dx_ + dy_ * dy_
                if d < d1:
                    d2, d1, best = d1, d, q
                elif d < d2:
                    d2 = d
        edge = math.sqrt(d2) - math.sqrt(d1)
        k = best[2] * (0.3 + 0.7 * min(1.0, edge / 2.0) ** 0.7) * (1.0 + rr_.uniform(-0.05, 0.05))   # (dark gaps between)
        return tuple(c * k for c in best[3])
    return fn


M_BALLAST = mat('Ballast', '#ffffff', 0.95, image=kit_image('ballast', 252, 252, _ballast_px()))
M_SLEEPER = mat('Sleeper', '#ffffff', 0.9, image=kit_image('sleeper', 64, 128, lambda x, y: tuple(
    c * (0.82 + 0.1 * math.sin(x * 0.9 + 3.0 * math.sin(y * 0.05)) + random.Random(x * 131 + y).uniform(-0.06, 0.06))
    for c in rgb('#5b4a3c'))))
M_RAIL = mat('RailSteel', '#5a4a40', 0.75, 0.6)
M_RAILHEAD = mat('RailHead', '#b9b7b2', 0.3, 0.9)
M_RAILPLATE = mat('RailPlate', '#2f2c2a', 0.7, 0.5)
# a rail's cross-section (x across from its middle, h up from its foot), round anticlockwise; the top edge is the head
FUNI_RAIL_PROF = [(-0.065, 0.0), (0.065, 0.0), (0.065, 0.012), (0.012, 0.022), (0.01, 0.085), (0.032, 0.097), (0.032, 0.125),
                  (-0.032, 0.125), (-0.032, 0.097), (-0.01, 0.085), (-0.012, 0.022), (-0.065, 0.012)]


def funi_extrude(mb, xa, za, ha, xb, zb_, hb, prof, m, m_top=None):
    """A cross-section (x, h offsets) swept straight from (xa, za, ha) to (xb, zb_, hb), engine metres; its ends open."""
    for i_ in range(len(prof)):
        p_, q_ = prof[i_], prof[(i_ + 1) % len(prof)]
        nx_, nh_ = q_[1] - p_[1], -(q_[0] - p_[0])
        top_ = m_top is not None and p_[1] == q_[1] == max(c[1] for c in prof)
        mb.face([V(xa + p_[0], za, ha + p_[1]), V(xa + q_[0], za, ha + q_[1]), V(xb + q_[0], zb_, hb + q_[1]), V(xb + p_[0], zb_, hb + p_[1])],
                m_top if top_ else m, normal=(nx_, 0.0, nh_))


def funi_block(mb, xc, z0, z1, hw, hlo, hhi, m, uvscale=1.0):
    """A box lying on the line's slope: x xc ± hw, from z0 to z1, hlo to hhi over the line's profile there."""
    p0, p1 = N.funi_profile(z0), N.funi_profile(z1)
    c_ = {(sx, sz, sh): V(xc + sx * hw, z0 if sz < 0 else z1, (p0 if sz < 0 else p1) + (hlo if sh < 0 else hhi))
          for sx in (-1, 1) for sz in (-1, 1) for sh in (-1, 1)}
    for (ks_, nrm_) in (((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)), (0, 0, 1)), \
            (((-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)), (-1, 0, 0)), \
            (((1, -1, -1), (1, -1, 1), (1, 1, 1), (1, 1, -1)), (1, 0, 0)), \
            (((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)), (0, 1, 0)), \
            (((-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)), (0, -1, 0)):
        mb.face([c_[k] for k in ks_], m, normal=nrm_, uvscale=uvscale)


fun = MB(uv=True)
RAIL_TOP = 0.115                                 # (over the line's profile: where the cars' wheels ride, as before)
zb = FZ0
while zb > FZ1 + 0.01:
    z2 = max(FZ1, zb - 3.0)
    pa_, pb_ = N.funi_profile(zb), N.funi_profile(z2)
    o0_, o1_ = funi_off(zb), funi_off(z2)
    g_ = (pb_ - pa_) / (zb - z2)
    nrm_ = Vector((0.0, g_, 1.0)).normalized()
    # the ballast: a flat top to the sleepers' ends, shoulders sloping down and out into the carved ground
    # (round 41, the user: "could you make the gravel on either side of the tracks slightly thinner?… It looks very
    # thick. Both close up and from a distance": the shoulders out to 1.75 m, not 2.2)
    for (xi0, xi1, hi0, hi1, ww) in ((-1.1, 1.1, -0.05, -0.05, 'top'), (-1.75, -1.1, -0.3, -0.05, 'l'), (1.1, 1.75, -0.05, -0.3, 'r')):
        def bx_(x_, o_):
            return lx + x_ + (o_ if x_ > 0 else -o_)
        fun.face([V(bx_(xi0, o0_), zb, pa_ + hi0), V(bx_(xi1, o0_), zb, pa_ + hi1), V(bx_(xi1, o1_), z2, pb_ + hi1), V(bx_(xi0, o1_), z2, pb_ + hi0)],
                 M_BALLAST, normal=(nrm_.x, nrm_.y, nrm_.z), uvscale=1.8)          # (stones about 6 cm; round 41, the user: "possibly the hottest thing I've ever seen")
    for (sgn, always) in ((-1, True), (1, False)):
        o0, o1 = funi_off(zb) * sgn, funi_off(z2) * sgn
        if not always and max(abs(o0), abs(o1)) < 0.06:
            continue
        for rr in (-0.5, 0.5):                                             # the two rails
            funi_extrude(fun, lx + o0 + rr, zb, pa_ + RAIL_TOP - 0.125, lx + o1 + rr, z2, pb_ + RAIL_TOP - 0.125,
                         FUNI_RAIL_PROF, M_RAIL, M_RAILHEAD)
        # the haul cable, low between the rails, on a roller every 3 m
        fun.tube(V(lx + o0, zb, pa_ + 0.04), V(lx + o1, z2, pb_ + 0.04), 0.011, M_CABLE, 4)
        zr_ = zb - 1.5
        orr_ = o0 + (o1 - o0) * 0.5
        funi_block(fun, lx + orr_, zr_ - 0.07, zr_ + 0.07, 0.11, -0.04, 0.0, M_RAILPLATE)          # its frame
        fun.cone(Matrix.Translation(V(lx + orr_, zr_, N.funi_profile(zr_) + 0.03)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'),
                 8, 0.035, 0.035, 0.16, M_RAILHEAD)                                                # the roller
        ns_ = 4
        for ks_ in range(ns_):                                             # sleepers, 0.75 m apart, on the slope
            tt = (ks_ + 0.5) / ns_
            zs_, os_ = zb + (z2 - zb) * tt, o0 + (o1 - o0) * tt
            funi_block(fun, lx + os_, zs_ - 0.12, zs_ + 0.12, 0.85, RAIL_TOP - 0.125 - 0.14, RAIL_TOP - 0.125, M_SLEEPER, 0.5)
            for rr in (-0.5, 0.5):                                         # a base plate under each rail
                funi_block(fun, lx + os_ + rr, zs_ - 0.1, zs_ + 0.1, 0.1, RAIL_TOP - 0.125, RAIL_TOP - 0.125 + 0.012, M_RAILPLATE)
    zb = z2
# (round 30, the user: no level crossings — the path never steps over the line. Where its hairpin bends up against
# the funicular, the line's own barrier stands along the cutting's lip: a white post-and-double-rail fence the
# path curves at, a small FUNICULAR plate on it, the viewpoint bench looking out over the line to the city)
# (round 35, the full test: at the round hairpin the straight fence touched the path only at its tip; either side of it
# the bank fell 1–4 m to the fence, and she slid down there and couldn't climb back. PATH_RULES D2/D6: the white
# lineside fence follows the outside of the bend along the path's edge, from where the leg's rope ends, round the tip,
# to where the ground beside the path stops falling; the rope ends against its first post.)
_bp, _ = N.path_points()
BF_LINE = []
for _i in range(1, len(_bp) - 1):
    _x, _z, _h = _bp[_i]
    # (round 41, the user: "This white fence should continue as well, because I could slip through and now I'm on the
    # tracks, which is dangerous") on 3 m further along each leg, then turned out to the cutting's edge (below)
    if not (_x > -78.6 and -204.5 < _z < -190.5):
        continue
    _a, _b = _bp[_i - 1], _bp[_i + 1]
    _L = math.hypot(_b[0] - _a[0], _b[1] - _a[1]) or 1.0
    _nx, _nz = -(_b[1] - _a[1]) / _L, (_b[0] - _a[0]) / _L
    if _nx < 0:
        _nx, _nz = -_nx, -_nz                                              # (the outside: towards the line, east)
    BF_LINE.append((_x + _nx * 1.6, _z + _nz * 1.6))
_BF_OUT = []
for _e in (0, -1):                                                         # each end turned out towards the line
    _q, _qn = BF_LINE[_e], BF_LINE[1 if _e == 0 else -2]
    _L = math.hypot(_q[0] - _qn[0], _q[1] - _qn[1]) or 1.0
    _tx, _tz = (_q[0] - _qn[0]) / _L, (_q[1] - _qn[1]) / _L                # on along the fence
    _BF_OUT.append([(_q[0] + _tx * 0.8 + 0.6, _q[1] + _tz * 0.8), (_q[0] + _tx * 1.0 + 1.6, _q[1] + _tz * 1.0)])
BF_LINE = list(reversed(_BF_OUT[0])) + BF_LINE + _BF_OUT[1]


def _dense03(line):
    out_ = [line[0]]
    for a_, b_ in zip(line, line[1:]):
        k_ = max(1, math.ceil(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) / 0.3))
        out_ += [(a_[0] + (b_[0] - a_[0]) * t / k_, a_[1] + (b_[1] - a_[1]) * t / k_) for t in range(1, k_ + 1)]
    return out_


BF_LINE = _dense03([BF_LINE[0]] + [((BF_LINE[k - 1][0] + BF_LINE[k][0] + BF_LINE[k + 1][0]) / 3, (BF_LINE[k - 1][1] + BF_LINE[k][1] + BF_LINE[k + 1][1]) / 3)
                 for k in range(1, len(BF_LINE) - 1)] + [BF_LINE[-1]])
_bfp, _acc = [BF_LINE[0]], 0.0
for _q0, _q1 in zip(BF_LINE, BF_LINE[1:]):
    _acc += math.hypot(_q1[0] - _q0[0], _q1[1] - _q0[1])
    if _acc >= 1.6:
        _bfp.append(_q1)
        _acc = 0.0
if math.hypot(_bfp[-1][0] - BF_LINE[-1][0], _bfp[-1][1] - BF_LINE[-1][1]) > 0.4:
    _bfp.append(BF_LINE[-1])
N.FUNI_FENCE_ENDS = [_bfp[0], _bfp[-1]]
bf_hs = [hz(fx_, fz_) for (fx_, fz_) in _bfp]
for _ in range(2):
    bf_hs = [bf_hs[0]] + [(bf_hs[k_ - 1] + bf_hs[k_] + bf_hs[k_ + 1]) / 3 for k_ in range(1, len(bf_hs) - 1)] + [bf_hs[-1]]
for (fx_, fz_), fh_ in zip(_bfp, bf_hs):
    fun.box(V(fx_, fz_, fh_ + 0.34), (0, 1), (1, 0), 0.05, 0.05, 0.66, M_WHEEL_W)
for ((fxa_, fza_), fha_), ((fxb_, fzb_), fhb_) in zip(list(zip(_bfp, bf_hs)), list(zip(_bfp, bf_hs))[1:]):
    for rl_ in (0.95, 0.52):
        fun.tube(V(fxa_, fza_, fha_ + rl_), V(fxb_, fzb_, fhb_ + rl_), 0.035, M_WHEEL_W, 6)
    _L = math.hypot(fxb_ - fxa_, fzb_ - fza_) or 1.0
    _ox, _oz = -(fzb_ - fza_) / _L * 0.12, (fxb_ - fxa_) / _L * 0.12
    scene.setdefault('solids', []).append([[round(fxa_ - _ox, 2), round(fza_ - _oz, 2)], [round(fxb_ - _ox, 2), round(fzb_ - _oz, 2)],
                                           [round(fxb_ + _ox, 2), round(fzb_ + _oz, 2)], [round(fxa_ + _ox, 2), round(fza_ + _oz, 2)]])
_tip = max(_bfp, key=lambda q: q[0])
# (round 40, SIGN_FLOAT: the name hung between the rails with nothing behind it) a small white plate on the end post
# (round 41, the user: "It looks like there's a white sign on that fence, but I can't read anything on it. Maybe there
# can be something about the funicular, some history. Therefore, make it slightly larger and have like wiggly text so it
# looks like there's a paragraph") a board on the end post: the name over a paragraph of little lines of "words", the
# text itself read with E (scene things2d, a sign); dark plaque ink (the old name was cream on the white plate: unreadable)
_sh_ = hz(*_tip)
fun.box(V(_tip[0] - 0.06, _tip[1], _sh_ + 0.86), (0, 1), (1, 0), 0.5, 0.014, 0.3, M_WHEEL_W)
city_objs.append(text_obj('FUNICULAR DEL TIBIDABO', 0.085, M_PLAQUE_TEXT, V(_tip[0] - 0.08, _tip[1], _sh_ + 1.08),
                          facing((-1, 0)), 'FuniBendSign'))
_wr_ = random.Random(4141)
for _ln in range(7):                                       # the paragraph: rows of short dark "words", a little uneven
    _zz = _tip[1] - 0.42
    _row_end = _tip[1] + (0.42 if _ln < 6 else 0.05)
    _hh = _sh_ + 0.97 - _ln * 0.065
    while _zz < _row_end - 0.04:
        _wl = min(_wr_.uniform(0.03, 0.11), _row_end - _zz)
        fun.box(V(_tip[0] - 0.076, _zz + _wl / 2, _hh + _wr_.uniform(-0.004, 0.004)), (0, 1), (1, 0), _wl / 2, 0.002, 0.011,
                M_PLAQUE_TEXT)
        _zz += _wl + 0.025
scene.setdefault('things2d', []).append({'type': 'sign', 'pos': [round(_tip[0] - 0.7, 2), round(_tip[1], 2)], 'id': '',
    'h': round(_sh_, 3), 'landmark': '', 'text':
    "FUNICULAR DEL TIBIDABO. Opened in 1901, the first funicular in Spain: built for Dr Salvador Andreu, who was "
    "turning the mountain into a resort, with the Avinguda del Tibidabo and its blue tram running up to the station at "
    "the bottom. Two cars on one line, tied to each other by a cable over a wheel at the top, pass halfway on a loop. "
    "1,130 m of track, 275 m of climb. The cars running today, the Cuca de Llum ('glow-worm'), were installed "
    "in 2021, replacing the ones in service since 1958."})
# (the platform beside the track at the foot: after the cars, where they stop is known — FuniPlatform below)
# (round 40, the user's blue and purple lines on the plan: "blue… for where the iron fences should go… purple to indicate
# where the steep hill should stop her") the platform is solid, and two iron railings close the track off behind the
# station: from its back corners, along the line of its sides, north to where the hill turns too steep to climb — the
# east one to the platform, which carries the line on; outside them she walks round the back and watches the cars
M_RAILING = mat('IronRailing', '#1d1f1e', 0.5, 0.4)
solid(lx + 0.95, -116.4, lx + 3.0, lz - 4.0)   # (the platform, from the car's side (0.9), on to the track's own edge, -116: no gap behind it)
fen_ = MB(uv=True)


def rail_ground(x_, z_):
    """(round 40, the user: "The black railings you made look good, but they do sink into the ground") what is really
    underfoot: the station's raised forecourt where it reaches, else the ground as drawn (the higher of a square's two
    triangles), never the bare height under them."""
    if lx - 6.5 <= x_ <= lx + 6.5 and lz - 6.0 <= z_ <= lz + 4.4:
        return hl + 0.04
    return max(gz_top(x_, z_), hz(x_, z_))


def iron_railing(mb_, x_, za_, zb_):
    """A black iron railing along x_ from za_ to zb_ (engine z): posts every metre or so, a rail top and bottom, bars
    between with little spear tips, standing on the ground all along; solid to her."""
    hz = rail_ground                               # (round 40: on what is really there)
    n_ = max(1, int(abs(zb_ - za_) / 1.1 + 0.5))
    for k_ in range(n_ + 1):
        z_ = za_ + (zb_ - za_) * k_ / n_
        g_ = hz(x_, z_)
        mb_.box(V(x_, z_, g_ + 0.62), (1, 0), (0, 1), 0.035, 0.035, 0.66, M_RAILING)
        mb_.cone(Matrix.Translation(V(x_, z_, g_ + 1.32)), 6, 0.05, 0.0, 0.12, M_RAILING)
    nb_ = max(2, int(abs(zb_ - za_) / 0.13))
    for k_ in range(nb_):
        z_ = za_ + (zb_ - za_) * (k_ + 0.5) / nb_
        g_ = hz(x_, z_)
        mb_.box(V(x_, z_, g_ + 0.58), (1, 0), (0, 1), 0.011, 0.011, 0.56, M_RAILING)
        mb_.cone(Matrix.Translation(V(x_, z_, g_ + 1.18)), 4, 0.025, 0.0, 0.07, M_RAILING)
    for zr_ in (0.12, 1.08):
        for k_ in range(n_):
            z0_, z1_ = za_ + (zb_ - za_) * k_ / n_, za_ + (zb_ - za_) * (k_ + 1) / n_
            ga_, gb_ = hz(x_, z0_), hz(x_, z1_)
            mb_.face([V(x_ - 0.02, z0_, ga_ + zr_), V(x_ - 0.02, z1_, gb_ + zr_), V(x_ - 0.02, z1_, gb_ + zr_ + 0.04),
                      V(x_ - 0.02, z0_, ga_ + zr_ + 0.04)], M_RAILING, normal=(-1, 0, 0))
            mb_.face([V(x_ + 0.02, z1_, gb_ + zr_), V(x_ + 0.02, z0_, ga_ + zr_), V(x_ + 0.02, z0_, ga_ + zr_ + 0.04),
                      V(x_ + 0.02, z1_, gb_ + zr_ + 0.04)], M_RAILING, normal=(1, 0, 0))
    solid(x_ - 0.08, min(za_, zb_), x_ + 0.08, max(za_, zb_))


# (the user's purple line: "where the steep hill should stop her… That is the invisible wall. But because of the steep
# hill") at the hill's foot, on from each railing's end: walking along the slope she could otherwise have slipped round
for (xa_, xb_, z_) in ((lx - 11.6, lx - 2.85, -111.9), (lx + 3.0, lx + 12.6, -111.6)):
    scene.setdefault('solids', []).append([[round(xa_, 2), round(z_ - 0.1, 2)], [round(xb_, 2), round(z_ - 0.1, 2)],
                                           [round(xb_, 2), round(z_ + 0.1, 2)], [round(xa_, 2), round(z_ + 0.1, 2)]])
# the portal: a stone arch where the track slips under the plateau's edge, dark inside
pph_ = N.funi_profile(FZ1)
for sx_f in (-1, 1):
    fun.box(V(lx + sx_f * 2.5, FZ1 - 0.6, pph_ + 1.9), (1, 0), (0, 1), 0.55, 0.8, 2.2, M_RUBBLE)
fun.box(V(lx, FZ1 - 0.6, pph_ + 4.35), (1, 0), (0, 1), 3.05, 0.8, 0.55, M_RUBBLE)              # the lintel
fun.box(V(lx, FZ1 - 0.6, pph_ + 5.0), (1, 0), (0, 1), 3.3, 0.9, 0.18, M_STONE)                 # its coping
for sx_f in (-1, 1):                                                                            # low wing walls
    fun.box(V(lx + sx_f * 3.9, FZ1 + 1.0, pph_ + 1.1), (1, sx_f * 0.55), (-sx_f * 0.55, 1), 1.6, 0.3, 1.3, M_RUBBLE)
# (round 35, the user: the hillside's grass showed inside the tunnel's mouth, in front of its dark: the dark now just
# inside the arch's face, in front of the slope)
fun.face([V(lx - 1.95, FZ1 + 0.05, pph_ - 0.3), V(lx + 1.95, FZ1 + 0.05, pph_ - 0.3),
          V(lx + 1.95, FZ1 + 0.05, pph_ + 3.9), V(lx - 1.95, FZ1 + 0.05, pph_ + 3.9)], M_DARKIN, normal=(0, 1, 0))
# the plateau's bank over the portal dressed as terraced masonry, as on a real hill railway: the bare cut would
# otherwise stare down the whole track
rv1_ = FH + 0.2
nt_ = 4
for kt_ in range(nt_):
    tb_ = pph_ - 0.4 + (rv1_ - pph_ + 0.4) * kt_ / nt_
    tt_ = pph_ - 0.4 + (rv1_ - pph_ + 0.4) * (kt_ + 1) / nt_
    tz2_ = FZ1 - 0.35 - 0.15 * kt_
    hw_ = 20.0 - kt_ * 1.6
    if tb_ < pph_ + 4.6:                                                   # (round the portal's mouth, not across it)
        for (xa2_, xb2_) in ((lx - hw_, lx - 2.6), (lx + 2.6, lx + hw_)):
            fun.box(V((xa2_ + xb2_) / 2, tz2_, (tb_ + min(tt_, pph_ + 4.6)) / 2), (1, 0), (0, 1),
                    (xb2_ - xa2_) / 2, 0.4, (min(tt_, pph_ + 4.6) - tb_) / 2 + 0.03, M_RUBBLE)
        if tt_ > pph_ + 4.6:
            fun.box(V(lx, tz2_, (pph_ + 4.6 + tt_) / 2), (1, 0), (0, 1), hw_, 0.4, (tt_ - pph_ - 4.6) / 2 + 0.03, M_RUBBLE)
    else:
        fun.box(V(lx, tz2_, (tb_ + tt_) / 2), (1, 0), (0, 1), hw_, 0.4, (tt_ - tb_) / 2 + 0.03, M_RUBBLE)
    # its coping, round the portal's mouth too (round 41, the user: "there is a bar through the middle of the black part
    # that you go into at the top… Just remove that")
    if tt_ < pph_ + 4.6:
        for (xa2_, xb2_) in ((lx - hw_ - 0.1, lx - 2.6), (lx + 2.6, lx + hw_ + 0.1)):
            fun.box(V((xa2_ + xb2_) / 2, tz2_ - 0.05, tt_ + 0.05), (1, 0), (0, 1), (xb2_ - xa2_) / 2, 0.48, 0.07, M_STONE)
    else:
        fun.box(V(lx, tz2_ - 0.05, tt_ + 0.05), (1, 0), (0, 1), hw_ + 0.1, 0.48, 0.07, M_STONE)
city_objs.append(fun.finish('Funicular'))
# she may not stand on the track where the cars sweep by: one unbroken strip (round 30: no crossings to leave open)
scene.setdefault('solids', []).append([[lx - 2.2, -116.0], [lx + 2.2, -116.0], [lx + 2.2, FZ1], [lx - 2.2, FZ1]])

# the two cars, the Cuca de Llum ("glow-worm") that run today: the game slides them along the track
# (round 40, the user: "It has vertical walls… it doesn't hit the building"; round 41: "the bottom part of it is flat on
# the ground… there's no gap at the bottom… against the rails"; then, with four photos of the real one: "Could you make
# something like this? If she can look out from the inside, that would also be amazing"; "from the outside, it should
# appear black, but from the inside, it should appear clear") as the 2021 cars: one long capsule leaning with the line,
# glossy red, a big rounded bubble of black glass at each end, tall black windows between red pillars down each side
# with a round porthole behind each nose, a thin white line tracing the side, little bogies on the rails under a dark
# skirt. The glass is one-sided (FuniGlassOut, north.gd sets its back faces unseen): black from outside, from inside
# nothing, so she looks straight out. Inside: red, the floor in level tiers, a bench at the bottom end facing down the
# line, where she sits to look out (north.gd ride_toggle). Built at the grade the line has at both stations (0.46,
# FUNI_CAP), so standing at a platform it is upright, never tipped; on the way it leans to the rails under it
FUNI_G = N.FUNI_CAP / 2.0                                                  # (the line's grade at the stations)
FUNI_CW, FUNI_CL = 0.9, 3.9                                                # half width, half length (along the track)
FUNI_FLOOR = 0.6                                                           # (its tiers' floors, over the rails mid-tier)
FUNI_NOSE = 1.0                                                            # (each glass nose's length)
M_FUNI_RED = mat('FuniRed', '#c41f1f', 0.22, 0.15)
M_FUNI_GLASS_OUT = mat('FuniGlassOut', '#0b0e11', 0.06, 0.35)
M_FUNI_SKIRT = mat('FuniSkirt', '#2a2a2c', 0.6, 0.3)
M_FUNI_FLOORING = mat('FuniFloor', '#6f6863', 0.85)
M_FUNI_SILVER = mat('FuniSilver', '#d6d9dc', 0.35, 0.6)
M_FUNI_GLOW = mat('FuniGlowHoop', '#f3e8f0', 0.3)
# (round 41, the user: "I still don't see the tint from the inside. Could you just put a black thing up and then fade it
# by 80%?") a black layer just inside every pane, seen through from inside at a fifth (north.gd makes it see-through)
M_FUNI_TINT = mat('FuniTint', '#000000', 1.0)
# its cross-section (half; x out, z up over the rails' line, the material of the stretch after each point)
_FUNI_SEC = [(0.0, 0.2, 'k'), (FUNI_CW - 0.25, 0.2, 'k'), (FUNI_CW - 0.05, 0.32, 'k'), (FUNI_CW, 0.5, 'r'),
             (FUNI_CW, 0.62, 'w'), (FUNI_CW, 2.3, 'r'), (FUNI_CW - 0.03, 2.48, 'r'), (FUNI_CW - 0.12, 2.72, 'r'),
             (FUNI_CW - 0.28, 2.88, 'r'), (FUNI_CW - 0.5, 2.96, 'r'), (0.0, 2.99, None)]
_FUNI_RING = _FUNI_SEC + [(-x_, z_, m_) for (x_, z_, m_) in reversed(_FUNI_SEC[:-1])]
_FUNI_RING_K = [p_[2] for p_ in _FUNI_SEC[:-1]] + [p_[2] for p_ in reversed(_FUNI_SEC[:-1])]
_FUNI_ZC = 1.55                                                            # (the nose rounds in towards this height)


_FUNI_ZB = 0.2                                                             # (its keel: the nose keeps its bottom flat)


def funi_ring(y_, sx_=1.0, sz_=1.0, grow_=0.0):
    # (round 41, the user: "what's the two spiky things… the black part? It looks funny": rounded in towards its middle,
    # the nose's dark foot rose to two points at its tip; now towards its keel, the bottom flat, the glass a dome on it)
    return [Vector((x_ * sx_ * (1 + grow_), y_, _FUNI_ZB + (z_ - _FUNI_ZB) * sz_ * (1 + grow_) + y_ * FUNI_G))
            for (x_, z_, _) in _FUNI_RING]


def funi_loft(cb_, rings_, mats_, smooth_=True):
    for ra_, rb_ in zip(rings_, rings_[1:]):
        for k_ in range(len(ra_) - 1):
            q_ = [ra_[k_], ra_[k_ + 1], rb_[k_ + 1], rb_[k_]]
            c_ = sum(q_, Vector()) / 4
            cb_.face(q_, mats_[k_], normal=(c_.x, 0, c_.z - _FUNI_ZC - c_.y * FUNI_G), smooth=smooth_)


for i in range(2):
    cb = MB(uv=True)
    CW, CL = FUNI_CW, FUNI_CL
    yb_ = CL - FUNI_NOSE                                                    # (where the straight body meets each nose)
    yp_ = yb_ - 0.6                                                         # (the solid panel with the porthole)
    body_m_ = {'k': M_FUNI_SKIRT, 'r': M_FUNI_RED, 'w': M_FUNI_GLASS_OUT}
    panel_m_ = {'k': M_FUNI_SKIRT, 'r': M_FUNI_RED, 'w': M_FUNI_RED}
    nose_m_ = {'k': M_FUNI_SKIRT, 'r': M_FUNI_GLASS_OUT, 'w': M_FUNI_GLASS_OUT}
    funi_loft(cb, [funi_ring(-yp_), funi_ring(yp_)], [body_m_[k_] for k_ in _FUNI_RING_K])

    def funi_tint(rings_, kinds_):
        # the tint: the glass stretches again, 1.5 cm inside, facing in
        for ra_, rb_ in zip(rings_, rings_[1:]):
            for k_ in range(len(ra_) - 1):
                if kinds_[k_]:
                    q_ = [ra_[k_], ra_[k_ + 1], rb_[k_ + 1], rb_[k_]]
                    c_ = sum(q_, Vector()) / 4
                    cb.face(q_, M_FUNI_TINT, normal=(-c_.x, 0, -(c_.z - _FUNI_ZC - c_.y * FUNI_G)))
    funi_tint([funi_ring(-yp_, 1, 1, -0.017), funi_ring(yp_, 1, 1, -0.017)], [k_ == 'w' for k_ in _FUNI_RING_K])
    for sy_ in (-1, 1):
        funi_loft(cb, [funi_ring(sy_ * yp_), funi_ring(sy_ * yb_)], [panel_m_[k_] for k_ in _FUNI_RING_K])
        # the nose: a bubble of black glass, its foot dark
        ts_ = [0.0, 0.3, 0.55, 0.75, 0.88, 0.96, 1.0]
        rings_ = []
        for t_ in ts_:
            s_ = max(0.12, math.sqrt(max(0.0, 1.0 - t_ * t_)))
            rings_.append(funi_ring(sy_ * (yb_ + FUNI_NOSE * t_), s_, 0.45 + 0.55 * s_))
        funi_loft(cb, rings_, [nose_m_[k_] for k_ in _FUNI_RING_K])
        cb.face(rings_[-1][:-1], M_FUNI_GLASS_OUT, normal=(0, sy_, 0))
        funi_tint([funi_ring(sy_ * (yb_ + FUNI_NOSE * t_) - sy_ * 0.015, max(0.12, math.sqrt(max(0.0, 1.0 - t_ * t_))) * 0.982,
                             (0.45 + 0.55 * max(0.12, math.sqrt(max(0.0, 1.0 - t_ * t_)))) * 0.982) for t_ in ts_],
                  [k_ in ('r', 'w') for k_ in _FUNI_RING_K])
        # (round 41, the user: "make sure the car still has the glowworm features… I think it curves around the cabin,
        # but not the entire cabin"; the night photo, looked up: a hoop of light where each glass nose meets the red
        # body, over the roof and down both sides) the hoop, white by day, glowing pink-violet at night (FuniGlowHoop,
        # main.gd); then the porthole in the red panel behind it
        hoop_k_ = [k_ if k_ != 'k' else None for k_ in _FUNI_RING_K]
        hoop_r_ = [funi_ring(sy_ * (yb_ - 0.075), 1, 1, 0.016), funi_ring(sy_ * (yb_ + 0.075), 1, 1, 0.016)]
        rim_o_ = funi_ring(sy_ * yb_, 1, 1, 0.016)
        mid_ = Vector((0, sy_ * yb_, _FUNI_ZC + sy_ * yb_ * FUNI_G))
        rim_i_ = [mid_ + (q_ - mid_) * 0.95 for q_ in rim_o_]     # (round 41: "halfway between": a slimmer frame)
        for k_ in range(len(_FUNI_RING_K)):
            if hoop_k_[k_]:                                                  # (not under the skirt)
                q_ = [hoop_r_[0][k_], hoop_r_[0][k_ + 1], hoop_r_[1][k_ + 1], hoop_r_[1][k_]]
                c_ = sum(q_, Vector()) / 4
                cb.face(q_, M_FUNI_GLOW, normal=(c_.x, 0, c_.z - _FUNI_ZC - c_.y * FUNI_G), smooth=True)
                # (round 41, the user: "the glowing hoop should be slightly more visible") a frame of it inward too,
                # framing the view from inside
                cb.face([rim_o_[k_], rim_o_[k_ + 1], rim_i_[k_ + 1], rim_i_[k_]], M_FUNI_GLOW, normal=(0, sy_, 0))
        for sdx in (-1, 1):
            yc_ = sy_ * (yp_ + 0.3)
            pts_ = [Vector((sdx * (CW + 0.006), yc_ + 0.26 * math.cos(a_ * math.pi / 8),
                            1.5 + 0.26 * math.sin(a_ * math.pi / 8) + yc_ * FUNI_G)) for a_ in range(16)]
            cb.face(pts_, M_FUNI_GLASS_OUT, normal=(sdx, 0, 0))
    for sdx in (-1, 1):
        x_ = sdx * (CW + 0.006)
        for (z0_, z1_) in ((0.6, 0.645), (2.28, 2.325)):                     # (the white line along the side)
            cb.face([Vector((x_, -yb_, z0_ - yb_ * FUNI_G)), Vector((x_, yb_, z0_ + yb_ * FUNI_G)),
                     Vector((x_, yb_, z1_ + yb_ * FUNI_G)), Vector((x_, -yb_, z1_ - yb_ * FUNI_G))], M_WHITE, normal=(sdx, 0, 0))
        # (round 41, the user: "make it a little bit longer? And then have doors on it. Currently the black strips are too
        # narrow to get into"; "Those black strips should turn into doors and windows, like in the picture… Maybe
        # another 30% longer") six wide glass panes down each side between slim red pillars: the second and fifth
        # sliding doors (a thin silver line down the middle, a silver grab bar on each leaf), the rest windows (a red
        # rail across at hip height)
        n_ = 6
        for k_ in range(n_ + 1):
            y_ = -yp_ + 2 * yp_ * k_ / n_
            cb.box(Vector((sdx * (CW - 0.02), y_, 1.46 + y_ * FUNI_G)), (1, 0), (0, 1), 0.035, 0.045, 0.86, M_FUNI_RED)
        for k_ in range(n_):
            y_ = -yp_ + 2 * yp_ * (k_ + 0.5) / n_
            hw_ = yp_ / n_ - 0.045
            if k_ in (1, 4):
                cb.box(Vector((sdx * (CW + 0.01), y_, 1.44 + y_ * FUNI_G)), (1, 0), (0, 1), 0.006, 0.012, 0.8, M_FUNI_SILVER)
                # (round 41, the user: "the white things on the doors that separate the two doors… make it go all the way
                # to the roof so it's stretched out") each leaf's bar from the floor's line up to the roof's edge
                for sg_ in (-1, 1):
                    cb.box(Vector((sdx * (CW + 0.014), y_ + sg_ * 0.1, 1.46 + (y_ + sg_ * 0.1) * FUNI_G)), (1, 0), (0, 1),
                           0.008, 0.014, 0.83, M_FUNI_SILVER)
            else:
                cb.face([Vector((sdx * (CW + 0.008), y_ - hw_, 1.02 + (y_ - hw_) * FUNI_G)),
                         Vector((sdx * (CW + 0.008), y_ + hw_, 1.02 + (y_ + hw_) * FUNI_G)),
                         Vector((sdx * (CW + 0.008), y_ + hw_, 1.1 + (y_ + hw_) * FUNI_G)),
                         Vector((sdx * (CW + 0.008), y_ - hw_, 1.1 + (y_ - hw_) * FUNI_G))], M_FUNI_RED, normal=(sdx, 0, 0))
    # inside: the floor in level tiers, red risers, a red bench at the bottom end facing down the line
    nt_ = 8
    ty0_ = -CL + 0.35
    tl_ = (2 * CL - 0.7) / nt_
    for k_ in range(nt_):
        y0_, y1_ = ty0_ + k_ * tl_, ty0_ + (k_ + 1) * tl_
        f_ = FUNI_FLOOR + (y0_ + y1_) / 2 * FUNI_G
        lo_ = 0.24 + y1_ * FUNI_G                     # (its foot above the skirt's line all along: none shows below it)
        cb.box(Vector((0, (y0_ + y1_) / 2, (f_ + lo_) / 2)), (1, 0), (0, 1), CW - 0.03, tl_ / 2, (f_ - lo_) / 2, M_FUNI_FLOORING)
    # (round 41: her seat back from the glass nose, so the glowing hoop, the red ribs in the glass and the tiers below
    # frame the view down the line, as in the user's photo from inside: "either you can see part of the vehicle or you
    # can't see any of it")
    # (round 41, the user: "move her down a few steps? So there's a chair on the next one down. And then she can look
    # around a bit more") her bench a few tiers further down, and another on the tier in front of her
    def funi_tier_floor(y_):
        k2_ = max(0, min(nt_ - 1, int((y_ - ty0_) / tl_)))
        return FUNI_FLOOR + (ty0_ + (k2_ + 0.5) * tl_) * FUNI_G

    ys_ = -yb_ + 1.55
    fb_ = funi_tier_floor(ys_)
    # (round 41, the user: "add more chairs. But not too many") three more, up the car, clear of the doors
    for yb2_ in (ys_, ys_ - tl_, ty0_ + 3.5 * tl_, ty0_ + 4.5 * tl_, ty0_ + 6.5 * tl_):
        f2_ = funi_tier_floor(yb2_)
        cb.box(Vector((0, yb2_, f2_ + 0.22)), (1, 0), (0, 1), CW - 0.12, 0.2, 0.22, M_FUNI_RED)          # (a bench)
        cb.box(Vector((0, yb2_ + 0.2, f2_ + 0.62)), (1, 0), (0, 1), CW - 0.12, 0.04, 0.2, M_FUNI_RED)    # (its back)
    FUNI_SEAT = (ys_, fb_ + 0.44 + 0.7)                                    # (her eyes, sitting there: along, up)
    for sy_ in (-1, 1):
        for t_ in (0.35, 0.68):                                             # (red ribs inside the glass nose, seen from in)
            s_ = math.sqrt(1.0 - t_ * t_)
            ra_ = funi_ring(sy_ * (yb_ + FUNI_NOSE * t_ - 0.03), s_ * 0.94, (0.45 + 0.55 * s_) * 0.94)     # (well inside
            rb_ = funi_ring(sy_ * (yb_ + FUNI_NOSE * t_ + 0.03), s_ * 0.94, (0.45 + 0.55 * s_) * 0.94)     #  the glass)
            for k_ in range(len(_FUNI_RING_K)):
                if _FUNI_RING_K[k_] != 'k':
                    q_ = [ra_[k_], ra_[k_ + 1], rb_[k_ + 1], rb_[k_]]
                    c_ = sum(q_, Vector()) / 4
                    cb.face(q_, M_FUNI_RED, normal=(-c_.x, 0, -(c_.z - _FUNI_ZC - c_.y * FUNI_G)), smooth=True)
            # (round 41, the user: "the red sort of bars… around the ends… add them to the outside a little bit… so
            # they're slightly visible from the outside of the black part, just a bit") a thin red band over the glass
            # (then: "make them slightly smaller": 3 cm wide, 0.4% proud, not 5 cm and 0.6%)
            oa_ = funi_ring(sy_ * (yb_ + FUNI_NOSE * t_ - 0.015), s_, 0.45 + 0.55 * s_, 0.004)
            ob_ = funi_ring(sy_ * (yb_ + FUNI_NOSE * t_ + 0.015), s_, 0.45 + 0.55 * s_, 0.004)
            for k_ in range(len(_FUNI_RING_K)):
                if _FUNI_RING_K[k_] not in ('k', None):
                    q_ = [oa_[k_], oa_[k_ + 1], ob_[k_ + 1], ob_[k_]]
                    c_ = sum(q_, Vector()) / 4
                    cb.face(q_, M_FUNI_RED, normal=(c_.x, 0, c_.z - _FUNI_ZC - c_.y * FUNI_G), smooth=True)
        for sdx in (-1, 1):                                                 # (red grab posts at the nose's joint,
            yq_ = sy_ * (yb_ - 0.15)                                          #  from its tier's floor up into the roof)
            fq_ = funi_tier_floor(yq_) - 0.02
            tq_ = 2.92 + yq_ * FUNI_G
            cb.cone(Matrix.Translation(Vector((sdx * 0.55, yq_, (fq_ + tq_) / 2))), 8, 0.03, 0.03, tq_ - fq_, M_FUNI_RED)
    for wy_ in (-CL + 0.7, CL - 0.7):                                        # (the bogies on the rails)
        for sdx in (-1, 1):
            cb.box(Vector((sdx * 0.58, wy_, 0.13 + wy_ * FUNI_G)), (1, 0), (0, 1), 0.06, 0.24, 0.13, M_IRON)
        cb.box(Vector((0, wy_, 0.2 + wy_ * FUNI_G)), (1, 0), (0, 1), 0.6, 0.35, 0.05, M_IRON)
    city_objs.append(cb.finish('CableCabin_%d' % i))
FUNI_CLEAR = FUNI_CL + 0.4                                                 # (how far up the line the cars stop at the foot: north.gd)
fpts = []
zz_ = FZ0
while zz_ > FZ1 + 0.01:
    fpts.append([round(lx, 2), round(zz_, 2), round(N.funi_profile(zz_) + 0.11, 3)])
    zz_ = max(FZ1, zz_ - 3.0)
fpts.append([round(lx, 2), round(FZ1, 2), round(N.funi_profile(FZ1) + 0.11, 3)])
north['cable'] = {'pts': fpts, 'loop': 1.05, 'loop_t': [0.34, 0.42, 0.58, 0.66], 'car': [FUNI_CW, FUNI_CL], 'grade': round(FUNI_G, 4), 'clear': FUNI_CLEAR,
                  'seat': [round(FUNI_SEAT[0], 3), round(FUNI_SEAT[1], 3)],
                  'door_low': [door_low[0], door_low[1]], 'door_top': [st_door[0], st_door[1]], 'ride_s': 40.0}

# ------------------------------------------------------------------ the path: its ribbon, the barrier and the work site
pts, PL = N.path_points()
north['path'] = [[round(p[0], 2), round(p[1], 2), round(p[2], 2)] for p in pts]
north['path_w'] = N.PATH_W


def gz(x, z):
    """The ground's height as built (the terrain grid, between its points: what the game walks her on), metres."""
    return ground_z(x / T + OX, z / T + OY)


def gz_top(x, z):
    """(round 24) the highest the drawn ground can be here: each grid square is drawn as two triangles, split along one
    diagonal or the other, and on a hillside either can rise above the smooth average (gz) by a few centimetres, enough
    for the grass to poke up through a path laid at gz. Paths are laid on this instead."""
    fi, fj = (x / T + OX - TX0) / STEP, (z / T + OY - TY0) / STEP
    i, j = max(0, min(len(VH[0]) - 2, int(fi))), max(0, min(len(VH) - 2, int(fj)))
    a, b = min(1.0, max(0.0, fi - i)), min(1.0, max(0.0, fj - j))
    h00, h10, h01, h11 = VH[j][i], VH[j][i + 1], VH[j + 1][i], VH[j + 1][i + 1]
    if (i, j) in GF_CELLS:                                  # (round 35: the finer ground along the paths, world2d.py)
        fi, fj = fi * GF_K, fj * GF_K
        i, j = int(math.floor(fi)), int(math.floor(fj))
        a, b = fi - i, fj - j
        h00, h10, h01, h11 = GF_V[(i, j)], GF_V[(i + 1, j)], GF_V[(i, j + 1)], GF_V[(i + 1, j + 1)]
    d1 = h00 + a * (h10 - h00) + b * (h11 - h10) if a >= b else h00 + b * (h01 - h00) + a * (h11 - h01)
    d2 = h00 + a * (h10 - h00) + b * (h01 - h00) if a + b <= 1 else h11 + (1 - a) * (h01 - h11) + (1 - b) * (h10 - h11)
    return max(d1, d2, gz(x, z)) + 0.02


# (round 40: the funicular's iron railings, here where the ground as drawn is known, rail_ground)
iron_railing(fen_, lx - 2.85, -108.1, -111.9)                                   # (west: to the steep hill)
city_objs.append(fen_.finish('FuniRailing'))

# (round 41, the user: "if you could fix up the funicular station" — the platform was one level slab that hung out over
# the grass at its foot and sank into the slope at its head, a metre off the car) the platform is built where the car
# stops (north.gd cable_point at FUNI_CLEAR: the whole car on the line's climb, past the foot's bend): as at
# the real lower station, a flight of steps running up beside the car, each step level and solid down into the ground,
# a hand's width from the car, the car's tiers along it; the canopy over it slopes with the line
_L = sum(math.sqrt((b_[1] - a_[1]) ** 2 + (b_[2] - a_[2]) ** 2) for a_, b_ in zip(fpts, fpts[1:]))
_f = FUNI_CLEAR / _L * (len(fpts) - 1)
_i = int(_f)
car_z_ = fpts[_i][1] + (fpts[_i + 1][1] - fpts[_i][1]) * (_f - _i)


def funi_rail_h(z_):
    # the rails' height at z_ (engine), as the game lays the cars on them (north['cable'] pts)
    for a_, b_ in zip(fpts, fpts[1:]):
        if b_[1] <= z_ <= a_[1]:
            return a_[2] + (b_[2] - a_[2]) * (a_[1] - z_) / (a_[1] - b_[1])
    return fpts[0][2] if z_ > fpts[0][1] else fpts[-1][2]


pf_ = MB(uv=True)
# (round 41, the user: "could you also make the funicular platform and roof also more detailed? Like what you did with
# the funicular road… So that it has a comparable quality") speckled granite treads with dark non-slip nosings and a
# yellow safety line along the track side; an iron handrail along the outer edge; the roof ribbed red metal on top, a
# cream fascia round it, warm timber slats underneath, its posts on base plates with brackets up to the roof and a
# lamp fitting under every other one
M_PLAT_STONE = mat('PlatGranite', '#ffffff', 0.85, image=kit_image('plat_granite', 128, 128, lambda x, y: tuple(
    c * (0.93 + random.Random(x * 7919 + y * 104729).uniform(-0.1, 0.07)
         - (0.18 if random.Random(x * 31 + y * 17).random() < 0.04 else 0.0)) for c in rgb('#d3cbbf'))))
M_NOSING = mat('PlatNosing', '#4a4846', 0.9)
M_SAFETY = mat('PlatSafety', '#e2b82a', 0.7)
M_SLATS = mat('RoofSlats', '#ffffff', 0.85, image=kit_image('roof_slats', 64, 64, lambda x, y: tuple(
    c * ((0.55 if y % 16 in (0, 15) else 0.95 + 0.05 * math.sin(x * 0.4 + (y // 16) * 1.7))
         + random.Random(x * 13 + y * 7).uniform(-0.03, 0.03)) for c in rgb('#b07a4a'))))
M_FASCIA = mat('RoofFascia', '#efe6d2', 0.7)
M_RIB = mat('RoofRib', '#a8261e', 0.6)
PX0_, PX1_ = lx + FUNI_CW + 0.12, lx + 2.85
ZBK_ = lz - 4.0                                         # (the station's back wall)
FUNI_ZTOP_ = car_z_ - FUNI_CL - 0.3                          # (a little past the car's upper end)
funi_nst_ = max(4, int(round((ZBK_ - FUNI_ZTOP_) / 0.3)))
ftr_ = (ZBK_ - FUNI_ZTOP_) / funi_nst_
funi_steps_ = []
for k_ in range(funi_nst_):
    z1_, z0_ = ZBK_ - ftr_ * k_, ZBK_ - ftr_ * (k_ + 1)    # (z0_ < z1_: this step, from the foot up)
    top_ = max(hl + 0.04, funi_rail_h((z0_ + z1_) / 2) + FUNI_FLOOR - 0.05)
    lo_ = min(gz(x_, z_) for x_ in (PX0_, PX1_) for z_ in (z0_, z1_)) - 0.3
    pf_.box(V((PX0_ + PX1_) / 2, (z0_ + z1_) / 2, (top_ + lo_) / 2), (1, 0), (0, 1), (PX1_ - PX0_) / 2, ftr_ / 2,
            (top_ - lo_) / 2, M_PLAT_STONE)
    pf_.box(V((PX0_ + PX1_) / 2, z1_ - 0.025, top_ + 0.003), (1, 0), (0, 1), (PX1_ - PX0_) / 2, 0.025, 0.004, M_NOSING)
    pf_.box(V(PX0_ + 0.1, (z0_ + z1_) / 2, top_ + 0.004), (1, 0), (0, 1), 0.05, ftr_ / 2, 0.004, M_SAFETY)
    funi_steps_.append(((z0_ + z1_) / 2, top_))
# the handrail along the outer edge: a post every fourth step, the rail from post top to post top, up with the steps
_hr = [funi_steps_[j_] for j_ in range(2, len(funi_steps_), 4)] + [funi_steps_[-1]]
for (pz_, b_) in _hr:
    pf_.cone(Matrix.Translation(V(PX1_ - 0.04, pz_, b_ + 0.475)), 6, 0.022, 0.022, 0.95, M_IRON)
for (za_, ba_), (zb_, bb_) in zip(_hr, _hr[1:]):
    pf_.tube(V(PX1_ - 0.04, za_, ba_ + 0.95), V(PX1_ - 0.04, zb_, bb_ + 0.95), 0.025, M_IRON, 6)
    pf_.tube(V(PX1_ - 0.04, za_, ba_ + 0.5), V(PX1_ - 0.04, zb_, bb_ + 0.5), 0.012, M_IRON, 4)
# the canopy: a red roof over the steps, 2.45 m over each, from the station's back wall to the top; (round 41, the user:
# "the red ceiling for the funicular station at the bottom is not aligned and is not attached with the platform": it
# was one straight slab while the steps bend where they leave the station, and its posts stood half in the steps)
# laid along the steps' own line, on iron posts that stand on the steps and reach it
def funi_canopy_h(z_):
    return max(hl + 0.04, funi_rail_h(z_) + FUNI_FLOOR - 0.05) + 2.45


RX0_, RX1_ = PX0_ - 0.05, PX1_ + 0.12
czs_ = [ZBK_ - (ZBK_ - FUNI_ZTOP_) * k_ / 14 for k_ in range(15)]
for za_, zb_ in zip(czs_, czs_[1:]):
    ha_, hb_ = funi_canopy_h(za_), funi_canopy_h(zb_)
    for (pts_, nrm_, m_) in (
            ([V(RX0_, za_, ha_ + 0.12), V(RX1_, za_, ha_ + 0.12), V(RX1_, zb_, hb_ + 0.12), V(RX0_, zb_, hb_ + 0.12)], (0, 0, 1), M_RED),
            ([V(RX0_, za_, ha_), V(RX1_, za_, ha_), V(RX1_, zb_, hb_), V(RX0_, zb_, hb_)], (0, 0, -1), M_SLATS),
            ([V(RX1_, za_, ha_ - 0.1), V(RX1_, zb_, hb_ - 0.1), V(RX1_, zb_, hb_ + 0.15), V(RX1_, za_, ha_ + 0.15)], (1, 0, 0), M_FASCIA),
            ([V(RX0_, za_, ha_ - 0.1), V(RX0_, zb_, hb_ - 0.1), V(RX0_, zb_, hb_ + 0.15), V(RX0_, za_, ha_ + 0.15)], (-1, 0, 0), M_FASCIA)):
        pf_.face(pts_, m_, normal=nrm_, uvscale=1.2)
    for rx_ in [RX0_ + 0.14 + 0.24 * i_ for i_ in range(int((RX1_ - RX0_ - 0.2) / 0.24) + 1)]:      # (the ribs, down the slope)
        pf_.tube(V(rx_, za_, ha_ + 0.135), V(rx_, zb_, hb_ + 0.135), 0.016, M_RIB, 4)
    # (round 41, the user: "The funicular building should be treated as hard walls, so the camera moves in") the roof
    # for the camera: under it, it stays under its ceiling, coming in rather than going up through it (03 #16b)
    scene.setdefault('cam_roofs', []).append({'p': [[round(RX0_, 3), round(zb_, 3)], [round(RX1_, 3), round(zb_, 3)],
                                                    [round(RX1_, 3), round(za_, 3)], [round(RX0_, 3), round(za_, 3)]],
                                              'ceil': round(min(ha_, hb_), 3), 'top': round(max(ha_, hb_) + 0.12, 3)})
for (zz_, hh_, nrm_) in ((czs_[0], funi_canopy_h(czs_[0]), (0, -1, 0)), (czs_[-1], funi_canopy_h(czs_[-1]), (0, 1, 0))):
    pf_.face([V(RX0_, zz_, hh_ - 0.1), V(RX1_, zz_, hh_ - 0.1), V(RX1_, zz_, hh_ + 0.15), V(RX0_, zz_, hh_ + 0.15)], M_FASCIA, normal=nrm_)
for n_, j_ in enumerate(range(1, len(funi_steps_), 5)):      # (a post every five steps, on the step, up into the roof)
    pz_, b_ = funi_steps_[j_]
    t_ = funi_canopy_h(pz_) + 0.02
    pf_.cone(Matrix.Translation(V(PX1_ - 0.12, pz_, (b_ + t_) / 2)), 8, 0.045, 0.05, t_ - b_, M_IRON)
    pf_.box(V(PX1_ - 0.12, pz_, b_ + 0.012), (1, 0), (0, 1), 0.09, 0.09, 0.012, M_IRON)                   # (its base plate)
    pf_.tube(V(PX1_ - 0.12, pz_, t_ - 0.55), V(PX1_ - 0.72, pz_, t_ - 0.03), 0.018, M_IRON, 5)            # (a bracket)
    if n_ % 2 == 0:
        pf_.box(V((PX0_ + PX1_) / 2, pz_, t_ - 0.06), (1, 0), (0, 1), 0.2, 0.06, 0.03, M_FUNI_LAMP)        # (a lamp)
city_objs.append(pf_.finish('FuniPlatform'))
print('FUNI platform: car stops at z %.2f; %d steps from %.2f to %.2f m' % (car_z_, funi_nst_, funi_steps_[0][1], funi_steps_[-1][1]))


def dense(line, step=0.5):
    """A line's points every `step` metres (so a ribbon laid on the ground follows it closely)."""
    out = [line[0][:2]]
    for a_, b_ in zip(line, line[1:]):
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        k_ = max(1, math.ceil(L_ / step - 1e-6))           # (round 35: no piece longer than step — int() let 3.4 m by)
        for t in range(1, k_ + 1):
            out.append((a_[0] + (b_[0] - a_[0]) * t / k_, a_[1] + (b_[1] - a_[1]) * t / k_))
    return out


# (round 24, the user: "Make sure that the path is a continuous path like the one in the forest and is not jagged due to
# the level changing") the same worn ribbon as the wood's (trails.py), laid on the ground as built, so it neither sinks
# into the hillside nor floats over it where the grid can't follow the path's bench
HILL_TRAIL = 'D1'           # (round 25: the sunny worn track on the hill and in the park; the wood's main path is gravel)
# (round 35: the track is drawn on the path's own middle line again — nudged 0.3 m away from the railing's side, it
# swung across at every change of side, and made the bends wobble; the posts stand 0.25 m past its edge)
RAIL_OFF = 1.35                                  # (the railing's distance from the path's middle)
PATH_NUDGE = 0.0


# ------------------------------------------------------------------ (round 35) the hill path's railing side, by rule
# (workshop/journal/DECISIONS.md "Round 35", the hill path's rules H1–H5; the comments at the railing below say each one)
_SL = [0.0]
for i_ in range(1, len(pts)):
    _SL.append(_SL[-1] + math.hypot(pts[i_][0] - pts[i_ - 1][0], pts[i_][1] - pts[i_ - 1][1]))


def _at_dist(i, d):
    """The path point about d metres along from point i (d < 0: back)."""
    j = i
    while 0 < j < len(pts) - 1 and abs(_SL[j] - _SL[i]) < abs(d):
        j += 1 if d > 0 else -1
    return j


def _normal(i):
    a_, b_ = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
    L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1]) or 1.0
    return -(b_[1] - a_[1]) / L_, (b_[0] - a_[0]) / L_


def fall_side(x, z, nx, nz):
    """How much the hillside falls towards (nx, nz), per metre (+: downhill that way): the smooth hillside laid round
    the path, with the funfair's plateau (N.height: not the cut banks beside each post, which flip from side to side)."""
    return (N.height(x - nx * 6.0, z - nz * 6.0) - N.height(x + nx * 6.0, z + nz * 6.0)) / 12.0


def bend_at(i, d=9.0):
    """(turn in radians over d metres either side of point i, which side (+1: the left normal's) is the bend's outside)."""
    a_, b_, c_ = pts[_at_dist(i, -d)], pts[i], pts[_at_dist(i, d)]
    t1 = Vector((b_[0] - a_[0], b_[1] - a_[1]))
    t2 = Vector((c_[0] - b_[0], c_[1] - b_[1]))
    if t1.length < 1e-6 or t2.length < 1e-6:
        return 0.0, 0
    t1.normalize()
    t2.normalize()
    nx_, nz_ = _normal(i)
    return math.acos(max(-1.0, min(1.0, t1.dot(t2)))), (-1 if (t2 - t1).dot(Vector((nx_, nz_))) > 0 else 1)


def leg_below(i, sd):
    """Another stretch of the path just below on that side (within 8 m out)?"""
    nx_, nz_ = _normal(i)
    for d_ in (4.0, 6.0, 8.0):
        dd_, ph_ = N.path_near(pts[i][0] + nx_ * sd * d_, pts[i][1] + nz_ * sd * d_)
        if dd_ < N.EDGE + 0.5 and ph_ < pts[i][2] - 0.5:
            return True
    return False


TIGHT = 1.0
_FALL = []
for i_ in range(len(pts)):
    nx_, nz_ = _normal(i_)
    _FALL.append(fall_side(pts[i_][0], pts[i_][1], nx_, nz_))
RAIL_RAW = []                                     # H1/H2: the side the railing belongs on, every point
for i_ in range(len(pts)):
    j0, j1 = _at_dist(i_, -9.0), _at_dist(i_, 9.0)
    f_ = sum(_FALL[j0:j1 + 1])
    sd_ = 1 if f_ > 0 else -1                     # H1: the side the hillside falls to
    turn_, out_ = bend_at(i_)
    if turn_ > TIGHT:
        sd_ = out_                                # H2: round a tight bend, its outside
    RAIL_RAW.append(sd_)
for i_ in range(1, len(pts) - 1):                 # H5: a flip shorter than 4 m is the run's
    j1 = _at_dist(i_, 4.0)
    if RAIL_RAW[i_] != RAIL_RAW[i_ - 1] and j1 < len(pts) and RAIL_RAW[j1] == RAIL_RAW[i_ - 1]:
        for m_ in range(i_, j1):
            RAIL_RAW[m_] = RAIL_RAW[i_ - 1]


def _hard_stop(i):
    x_, z_ = pts[i][0], pts[i][1]
    f_ = N.FAIR
    # (D5: it runs on to the funfair's wall; round 41c, the user: "could the final pole… be on the grass… Not too into the
    # brick": on the west, where the path comes in, the wall is 1.8 m thick, so it stops 2.1 m out, its last post on
    # the grass just before the wall's face, not up on its top)
    at_fair = f_[0] - 2.1 < x_ < f_[2] + 0.6 and f_[1] - 0.6 < z_ < f_[3] + 0.6
    # D6: not on the paving at the foot; round the funicular bend's tip, where its white fence is the barrier
    at_funi = x_ > -78.8 and -207.0 < z_ < -190.0          # (round 41: as far as the white fence now runs)
    return pts[i][2] < 2.5 or at_funi or at_fair


RAIL_WANT = []
for i_ in range(len(pts)):
    sd_ = RAIL_RAW[i_]
    nx_, nz_ = _normal(i_)
    turn_, out_ = bend_at(i_)
    ok_ = i_ >= 3 and not _hard_stop(i_)
    if ok_ and turn_ > TIGHT * 0.6 and sd_ != out_:
        ok_ = False                               # H3: the inside of a bend
    if ok_ and turn_ <= TIGHT and leg_below(i_, sd_):
        ok_ = False                               # H3: a leg just below that side
    RAIL_WANT.append(sd_ if ok_ else 0)
for i_ in range(1, len(pts) - 1):                 # H5: a gap shorter than 4 m inside a run is filled
    if RAIL_WANT[i_] == 0 and RAIL_WANT[i_ - 1] != 0 and not _hard_stop(i_):
        j1 = _at_dist(i_, 4.0)
        if j1 < len(pts) and RAIL_WANT[j1] == RAIL_WANT[i_ - 1] and not any(_hard_stop(m_) for m_ in range(i_, j1)):
            for m_ in range(i_, j1):
                RAIL_WANT[m_] = RAIL_WANT[i_ - 1]


def low_dir(x, z, nx, nz):
    """+1 if the railing's side (the lower) is along (nx, nz), -1 the other, 0 both (a spur, a bend's tip)."""
    h0, hl, hr = gz(x, z), gz(x + nx * 2.5, z + nz * 2.5), gz(x - nx * 2.5, z - nz * 2.5)
    if hl < h0 - 0.4 and hr < h0 - 0.4:
        return 0
    return 1 if hl < hr else -1


ribbon_pts = [(p_[0], p_[1]) for p_ in pts]
if PATH_NUDGE:
    _sh = []
    for i_, p_ in enumerate(pts):
        a_, b_ = pts[max(0, i_ - 1)], pts[min(len(pts) - 1, i_ + 1)]
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1]) or 1.0
        nx_, nz_ = -(b_[1] - a_[1]) / L_, (b_[0] - a_[0]) / L_
        _sh.append((nx_, nz_, -RAIL_RAW[i_]))           # (round 35: away from the rules' railing side, H1/H2)
    ribbon_pts = []
    for i_, p_ in enumerate(pts):
        w_ = [_sh[j_][2] for j_ in range(max(0, i_ - 6), min(len(pts), i_ + 7))]
        v_ = sum(w_) / len(w_) * min(1.0, i_ / 6.0, (len(pts) - 1 - i_) / 6.0)       # (smoothed; none at the two ends)
        ribbon_pts.append((p_[0] + _sh[i_][0] * v_ * PATH_NUDGE, p_[1] + _sh[i_][1] * v_ * PATH_NUDGE))
# (round 35, the user: "The path up the hill also stops and starts … It looks like squares") its points were ~3 m
# apart, and where the hill bulges the straight piece between two sank under the grass: every half metre now. And
# it stops at the funfair's paving (it ran on 3 m over the flags as a patch of dirt)
# (round 35, PATH_RULES B1: the track ends exactly where the funfair's paving starts — the paving is laid by whole
# ground squares, so its edge is the edge of the first square whose middle is on the plateau, not the plateau's line:
# stopping at the line left a strip of grass between)
_TG = scene['terrain']


def on_fair_paving(x, z):
    cx_ = _TG['x0'] + (math.floor((x - _TG['x0']) / _TG['step']) + 0.5) * _TG['step']
    cz_ = _TG['z0'] + (math.floor((z - _TG['z0']) / _TG['step']) + 0.5) * _TG['step']
    return N.FAIR[0] <= cx_ <= N.FAIR[2] and N.FAIR[1] <= cz_ <= N.FAIR[3]


# (round 41c, the user: "the path goes over the top of the paved ground… the paved ground should be on top of the
# dirt") and at the west gateway it stops 0.3 m in under the stone threshold (fx0 - 0.15 out), not out over it
def _past_threshold(x_, z_):
    return x_ > N.FAIR[0] + 0.15 and abs(z_ - N.PATH_CTRL[-1][1]) < N.PATH_W / 2 + 1.0


ribbon_pts = [q_ for q_ in dense(ribbon_pts, 0.1) if not on_fair_paving(*q_) and not _past_threshold(*q_)][::5] + \
    [q_ for q_ in dense(ribbon_pts, 0.1) if not on_fair_paving(*q_) and not _past_threshold(*q_)][-1:]
# (round 40, the user at the path's foot: it came to a point at the pavement) its last half metre straight at the
# pavement's edge, so it arrives at its full width, square on
_f0 = ribbon_pts[0]
ribbon_pts = [(_f0[0], -102.35), (_f0[0], -102.85)] + [q_ for q_ in ribbon_pts if q_[1] < -103.2]
# (round 30: one unbroken ribbon again — the path no longer crosses the funicular, so nothing cuts it)
# (round 40, the user: "It should look similar to how it is, but without the blocks of dirt to either side, and there
# should be no strip of green grass. It should just come up like it is already, but flush with the footpath") over its
# last 0.8 m the path itself rises to the pavement's top, 0.12, so it meets the paving's edge level, nothing between
def footpath_z(x_, z_):
    g_ = gz_top(x_, z_)
    if z_ > -103.15 and -88.0 < x_ < -84.0:
        k_ = min(1.0, max(0.0, (z_ + 103.15) / 0.8))
        return g_ + (max(g_, 0.124) - g_) * k_          # (a hair over the grass lip it lies across)
    return g_


city_objs.append(build_ribbons([{'pts': ribbon_pts, 'w': 2.2}], HILL_TRAIL, footpath_z, 'MountainPath'))
# (round 31: what read as a stream at the paving's edge was the last tile rows shading as a pale blue band where
# the bank meets the town — no water there at all. A grass apron laps from the bank down over the paving's edge,
# as turf over flags does, and the dirt path simply ends where the paving begins.)
# (round 40, the user: "put the path back here. So it should just be a line and not have the jagged squares. Just make
# the path continue right along") the apron came 1.75 m down over the pavement between the path's foot and the station,
# a notch in its edge: gone — the pavement runs on to one straight edge, as either side of it
# (round 40, the user: "could you fix up that ditch right along between the paved footpath and the hill?") the pavement
# stands 12 cm up on a kerb face all round, and behind it, against the hill, that face showed as a pale strip — a dark
# trough in the evening — with the grass meeting it lower down. A narrow lip of grass from the pavement's top edge down
# onto the ground 0.6 m behind it, all along, so they meet flush; never over the pavement, its edge straight
fap_ = MB(uv=True)
_PX0, _PX1, _PZ = -158.4, 42.9, -102.3
# (the station's forecourt; at the hill path's foot the lip runs on under the path, which rises over it, footpath_z)
_gaps = [(-72.6, -59.4)]
xk_ = _PX0
while xk_ < _PX1 - 0.01:
    xk2_ = min(_PX1, xk_ + 1.2)
    xm_ = (xk_ + xk2_) / 2
    if not any(g0 <= xm_ <= g1 for g0, g1 in _gaps):
        for g0_, g1_ in _gaps:
            if xk_ < g0_ < xk2_:
                xk2_ = g0_
        fap_.face([V(xk_, _PZ, 0.121), V(xk2_, _PZ, 0.121),
                   V(xk2_, _PZ - 0.6, max(0.06, gz(xk2_, _PZ - 0.6)) + 0.025), V(xk_, _PZ - 0.6, max(0.06, gz(xk_, _PZ - 0.6)) + 0.025)],
                  M_GRASS, normal=(0, 0.3, 1))
    xk_ = xk2_
city_objs.append(fap_.finish('FootGrassLip'))

# ------------------------------------------------------------------ the railing (round 24, the user: "a railing to stop you
# from going down, and this frames it a bit better with the gate at the bottom: on one side there is a steep hill and on
# the other is the railing. Then there is no railing for the top part, so that you can run down and get the ball. Make
# the railing wooden with ropes hung between it.") Wooden posts every few metres with a rope slung between their tops,
# on every side of the path that isn't a bank too steep to climb (so both sides at the foot, where it's gentle, and round
# the outside of the hairpins); none along the top leg above the ball's glade, which is fenced off at either end
# instead. Each stretch is also a wall for the game (north['rails']: segments, thin walls).
M_POST = mat('RailPost', '#7d6248', 0.9)
M_ROPE = mat('RailRope', '#c4ab7c', 0.95)
GATE_OFF = 1.35                                  # (the gateway's posts at the path's foot, from its middle)
RAIL_STEP = 1.8                                  # between posts (close enough to follow the tightest hairpin)
GLADE_X = (-197.0, -147.0)                       # the ball's glade, below the top leg (x range)
TOP_LEG_I = next(i for i, p in enumerate(pts) if i > 400 and p[0] > N.SLIDE[0][0] - 40 and p[1] < -268.0)
rail_mb = MB(uv=True)
rope_mb = MB(uv=True)          # (round 26: the ropes on their own, casting no shadow: thinner than the shadow map can hold,
                               #  their shadows shimmered as the sun turned; main.gd NO_SHADOW 'HillRope')
north['rails'] = []


def bank(x, z, nx, nz):
    """How much the ground rises over 2.6 m that side of the path (a bank she can't climb: no railing needed)."""
    return gz(x + nx * 2.6, z + nz * 2.6) - gz(x, z)


def rope(a, b, sag=0.13, r=0.022):
    pts_ = [a.lerp(b, k / 6) - Vector((0, 0, sag * 4 * (k / 6) * (1 - k / 6))) for k in range(7)]
    for q0, q1 in zip(pts_, pts_[1:]):
        d = q1 - q0
        rope_mb.cone(Matrix.Translation((q0 + q1) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4(),
                     5, r, r, d.length + 0.01, M_ROPE)


def post(x, z, h=1.0):
    g = gz(x, z)
    lean = Vector((nr.uniform(-0.03, 0.03), nr.uniform(-0.03, 0.03), 0))
    rail_mb.cone(Matrix.Translation(V(x, z, g + h / 2 - 0.1)) @ Matrix.Rotation(lean.x, 4, 'X') @ Matrix.Rotation(lean.y, 4, 'Y'),
                 7, 0.075, 0.065, h + 0.2, M_POST)
    rail_mb.cone(Matrix.Translation(V(x, z, g + h + 0.02)), 7, 0.08, 0.05, 0.06, M_POST)          # (its weathered top)
    return V(x, z, g + h - 0.08)


M_LANTERN = mat('HillLantern', '#f6e2b8', 0.3)          # (main.gd lights it after dark: set_emit)
LANTERN_EVERY = 0           # posts between lanterns (round 24: 18; round 25, the user: "remove the lanterns from the hill path")
lantern_n = [0]


def lantern(top):
    """A little iron lantern hung from a post's top on a short bracket; its glass glows warm at night."""
    arm = top + Vector((0, 0, 0.14))
    rail_mb.box(arm + Vector((0.2, 0, 0)), (1, 0), (0, 1), 0.21, 0.018, 0.018, M_IRON)
    c = arm + Vector((0.38, 0, -0.26))
    rail_mb.box(c, (1, 0), (0, 1), 0.1, 0.1, 0.14, M_LANTERN)
    for dz in (0.15, -0.15):
        rail_mb.box(c + Vector((0, 0, dz)), (1, 0), (0, 1), 0.12, 0.12, 0.015, M_IRON)
    rail_mb.cone(Matrix.Translation(c + Vector((0, 0, 0.23))), 4, 0.12, 0.0, 0.13, M_IRON)
    north.setdefault('lanterns', []).append([round(c.x, 2), round(c.z, 2), round(-c.y, 2)])   # (x, h, z) for its light


def fence(line, name_end=True, first_post=True):
    """Posts along a line of (x, z) points, a rope between each two; and the game's thin walls along it. Now and then
    a lantern (round 24: the path was very dark at night). first_post False: it starts at another fence's end post."""
    # (round 41c, the user: "could the final pole for the railing here be on the grass? … Not too into the brick") no
    # post on the funfair's west wall's top (its 1.8 m thickness out from the plateau's edge): a line running onto it
    # ends where it meets the grass just before the wall's face
    wx0_, wx1_ = N.FAIR[0] - 1.95, N.FAIR[0] + 0.5
    on_wall = lambda q_: wx0_ < q_[0] < wx1_ and N.FAIR[1] - 2.0 < q_[1] < N.FAIR[3] + 2.0
    if any(on_wall(q_) for q_ in line):
        kept_ = []
        for k_, q_ in enumerate(line):
            if not on_wall(q_):
                kept_.append(q_)
                continue
            for nb_ in (line[k_ - 1] if k_ > 0 else None, line[k_ + 1] if k_ + 1 < len(line) else None):
                if nb_ is not None and not on_wall(nb_) and abs(q_[0] - nb_[0]) > 1e-6:
                    t_ = (wx0_ - 0.05 - nb_[0]) / (q_[0] - nb_[0])
                    if 0.0 <= t_ <= 1.0:
                        e_ = (nb_[0] + (q_[0] - nb_[0]) * t_, nb_[1] + (q_[1] - nb_[1]) * t_)
                        if math.hypot(e_[0] - nb_[0], e_[1] - nb_[1]) > 0.35:
                            kept_.append(e_)
        line = kept_
        if len(line) < 2:
            return
    tops = [post(x, z) if (k_ or first_post) else V(x, z, gz(x, z) + 1.0 - 0.08) for k_, (x, z) in enumerate(line)]
    for t_ in tops:
        lantern_n[0] += 1
        if LANTERN_EVERY and lantern_n[0] % LANTERN_EVERY == 0:
            lantern(t_)
    for a_, b_ in zip(tops, tops[1:]):
        rope(a_, b_)
    for (x0, z0), (x1, z1) in zip(line, line[1:]):
        north['rails'].append([round(x0, 2), round(z0, 2), round(x1, 2), round(z1, 2)])


# sample the path every RAIL_STEP, both sides; runs of posts where that side needs a railing
samples, acc_, next_ = [], 0.0, 0.0
for i in range(len(pts)):
    if i:
        acc_ += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
    if acc_ + 1e-6 < next_:
        continue
    next_ += RAIL_STEP
    a0, b0 = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
    dx, dz = b0[0] - a0[0], b0[1] - a0[1]
    L_ = math.hypot(dx, dz) or 1.0
    samples.append((i, pts[i][0], pts[i][1], -dz / L_, dx / L_))
n_rails = 0
rail_ends = []                                   # (round 25: where each stretch of railing starts and stops)
top_posts = []                                   # (the top leg's last posts either side of the glade)


def inside_bend(i, nx, nz, k=4, turn=0.8):
    """(round 26) Is (nx, nz) the inside of a tight bend at path point i (turning more than `turn` radians over
    k points either side)?"""
    a_, b_, c_ = pts[max(0, i - k)], pts[i], pts[min(len(pts) - 1, i + k)]
    t1 = Vector((b_[0] - a_[0], b_[1] - a_[1]))
    t2 = Vector((c_[0] - b_[0], c_[1] - b_[1]))
    if t1.length < 1e-6 or t2.length < 1e-6:
        return False
    t1.normalize()
    t2.normalize()
    if math.acos(max(-1.0, min(1.0, t1.dot(t2)))) < turn:
        return False
    return (t2 - t1).dot(Vector((nx, nz))) > 0


def low_side(x, z, nx, nz):
    """(round 25) Is this side of the path a lower one? The lower of the two, or either where the ground falls away
    from the path on both sides (on a spur, round a bend's tip). (Round 35: no longer the railing's rule — see H1 —
    but the wildflowers still look for the level side with it.)"""
    d_ = N.EDGE + 1.6
    g_ = gz(x + nx * d_, z + nz * d_)
    return g_ < gz(x - nx * d_, z - nz * d_) or g_ < gz(x, z) - 0.4


# (round 35, the user: "The fence is now on the upper side … random small fences … parts of the fences with poles
# missing … one weird point where there are fences on both sides. The fences don't continue around the corner anymore")
# The railing follows written rules now (workshop/journal/DECISIONS.md "Round 35", the hill path's rules), not the bumps of the
# ground beside each post. Per post sample, one side or none:
#   H1  the side the hillside itself falls away to (its raw slope, before the path was cut, smoothed along ±9 m), so
#       a fence never flips to the uphill side over a local hump;
#   H2  round a tight bend, the outside of the bend, so the fence carries on round the corner;
#   H3  none on the inside of a bend, nor where another leg of the path lies just below that side (she may slip
#       down to it: "you can be liberal on the inside of the bends");
#   H4  none at the foot (the path under 2.5 m), at the funicular's bend (its white fence is the barrier), or on the
#       glade side of the top leg (so she can run down to the ball);
#   H5  one or two odd samples between two of a run are the run's (no missing posts); runs under 6 posts are
#       dropped (no short fences); the uphill side never has a fence (a green verge, then the bank).
def drop_beside(i, sd):
    """(PATH_RULES D1) how far the ground falls on side sd of path point i, past the flat strip the posts stand on,
    within 4.5 m of the middle (the ground as built)."""
    nx_, nz_ = _normal(i)
    x_, z_, h_ = pts[i]
    return h_ - min(gz(x_ + nx_ * sd * d_, z_ + nz_ * sd * d_) for d_ in (3.5, 4.5))


want_ = []
for (i, x, z, nx, nz) in samples:
    sd = RAIL_WANT[i]
    if i >= TOP_LEG_I and GLADE_X[0] + 1.0 < x < GLADE_X[1] - 1.0 and nz * sd > 0:
        sd = 0                                    # H4: the glade side of the top leg (she may run down to the ball)
    want_.append(sd)
# D1/D5: a fence starts only where the drop is plain (0.9 m), and runs on while there is still a drop (0.4 m), so it
# ends where the drop has died away
_drop = [drop_beside(smp[0], w_) if w_ else 0.0 for smp, w_ in zip(samples, want_)]
_keep = [w_ if (w_ and _drop[k] >= 0.9) else 0 for k, w_ in enumerate(want_)]
for _pass in range(2):
    rng_ = range(1, len(want_)) if _pass == 0 else range(len(want_) - 2, -1, -1)
    for k in rng_:
        nb_ = k - 1 if _pass == 0 else k + 1
        if not _keep[k] and _keep[nb_] and want_[k] == _keep[nb_] and _drop[k] >= 0.4:
            _keep[k] = want_[k]
want_ = _keep
for j_ in range(1, len(want_) - 1):               # D5: a gap of one or two samples inside a run is the run's
    if want_[j_] == 0 and want_[j_ - 1] != 0:
        for k_ in (1, 2):
            if j_ + k_ < len(want_) and want_[j_ + k_] == want_[j_ - 1] and \
                    not any(_hard_stop(samples[m_][0]) for m_ in range(j_, j_ + k_)):
                for m_ in range(j_, j_ + k_):
                    want_[m_] = want_[j_ - 1]
                break
# (round 41, the user at two hairpins: "this fence should continue where I've marked it in red" — round the outside of
# the tip and on along the next leg; "Again extend the fence"; PATH_RULES D2a) at every hairpin (the path turned more
# than 125° within 11 m either side) the rope on its outside carries on round the tip and 9 m along the leg it turns into,
# whatever the drop there, before it turns off to the bank (H6)
_BENCHES = N.bench_spots()
_HP_ENDS = []                                          # (pts index, side) where a hairpin's A rope ends
def _by_bench(j_):
    # which side of the path a bench's bay lies on beside sample j_ (0: none within 3.6 m, right in front of it)
    for (bx_, bz_, _, _) in _BENCHES:
        al_ = abs((bx_ - samples[j_][1]) * samples[j_][4] - (bz_ - samples[j_][2]) * samples[j_][3])   # (along the path)
        if math.hypot(bx_ - samples[j_][1], bz_ - samples[j_][2]) < 3.6 and al_ < 1.6:
            return 1 if samples[j_][3] * (bx_ - samples[j_][1]) + samples[j_][4] * (bz_ - samples[j_][2]) > 0 else -1
    return 0
_hp_tips = []
for j_ in range(6, len(samples) - 6):                   # (turned more than 125° within 11 m either side)
    a_ = samples[j_ - 6]
    ha_ = math.atan2(samples[j_ - 5][2] - a_[2], samples[j_ - 5][1] - a_[1])
    hb_ = math.atan2(samples[j_ + 6][2] - samples[j_ + 5][2], samples[j_ + 6][1] - samples[j_ + 5][1])
    if abs((hb_ - ha_ + math.pi) % math.tau - math.pi) > 2.2:
        _hp_tips.append(j_)
_hp_groups = []
for j_ in _hp_tips:
    if _hp_groups and j_ - _hp_groups[-1][-1] <= 2:
        _hp_groups[-1].append(j_)
    else:
        _hp_groups.append([j_])
for grp_ in _hp_groups:
    jt_ = grp_[len(grp_) // 2]
    if _hard_stop(samples[jt_][0]):
        continue                                       # (the funicular bend: its white fence; the foot; the funfair)
    m_ = ((samples[jt_ - 5][1] + samples[jt_ + 5][1]) / 2, (samples[jt_ - 5][2] + samples[jt_ + 5][2]) / 2)
    o_ = (samples[jt_][1] - m_[0], samples[jt_][2] - m_[1])
    sd_o = 1 if samples[jt_][3] * o_[0] + samples[jt_][4] * o_[1] > 0 else -1
    # which leg already has the outside rope coming in (the lower one, the drop's side): carry it round and on
    # (then the user, on the plan: "you can also just pull the fence a little bit back… Even if you drop back one, that's
    # still fine. But the fence ends way too far up and there's a big slope": round the tip and 5.4 m on, A; and the
    # rope between the legs, on the higher leg's downhill side, carried on down to 5.4 m short of the tip, B — "extend
    # this fence too. This is just behind the other")
    up_after = pts[samples[min(len(samples) - 1, jt_ + 6)][0]][2] > pts[samples[max(0, jt_ - 6)][0]][2]
    st_ = 1 if up_after else -1                         # (towards the higher leg, along the samples)
    # (then the user: "It should meet up with the hill before the bench. Currently it's blocking the bench": A stops
    # short of a bench's bay on the leg it turns into, and turns into the bank there; D2a)
    # (then, on the pictures: "the rope doesn't turn into the bank… It just needs to continue almost straight until it
    # hits the wall… the hill"; "once it comes around the bend, then it just goes into the wall… Now you've got it
    # running along the hill. 1, 2, 3, 4, 5, 6 poles can be removed": A goes round the tip and one post on, no further;
    # its end then runs on almost straight into the hill, below)
    # (where the bend's outside falls away — the bench's hairpin, above the railway — the hill is ahead, past the tip:
    # round one post further, then on into it)
    jq_ = samples[jt_][0]
    ox_, oz_ = pts[jq_][0] + samples[jt_][3] * sd_o * RAIL_OFF, pts[jq_][1] + samples[jt_][4] * sd_o * RAIL_OFF
    rise_ = max(gz(ox_ + samples[jt_][3] * sd_o * r_, oz_ + samples[jt_][4] * sd_o * r_) for r_ in (1.0, 2.0, 3.0, 4.0)) - gz(ox_, oz_)
    a_end_ = 0 if rise_ > 0.6 else 1
    for d_ in range(-4, a_end_ + 1):                    # A: from the lower leg, round the tip
        k_ = jt_ + d_ * st_
        if 0 <= k_ < len(want_) and not _hard_stop(samples[k_][0]):
            want_[k_] = sd_o
    for d_ in range(a_end_ + 1, 16):                    # (no rope on along the leg past it: "6 poles can be removed")
        k_ = jt_ + d_ * st_
        if not (0 <= k_ < len(want_)) or want_[k_] != sd_o:
            break
        want_[k_] = 0
    _HP_ENDS.append((samples[max(0, min(len(samples) - 1, jt_ + a_end_ * st_))][0], sd_o))
    for d_ in range(4, 18):                             # B: the higher leg's inside, on from where A stops
        k_ = jt_ + d_ * st_
        if not (0 <= k_ < len(want_)) or _hard_stop(samples[k_][0]):
            break
        if want_[k_] == -sd_o and d_ > 6:
            break                                       # (it meets the rope already there: one line)
        want_[k_] = -sd_o
    print('NORTH hairpin at (%.1f, %.1f): its outside rope carried round the tip; st %d sd_o %d' % (samples[jt_][1], samples[jt_][2], st_, sd_o))
for j_ in range(len(want_)):                           # D2a: a rope never runs between a bench and its path
    if want_[j_] != 0 and want_[j_] == _by_bench(j_):
        want_[j_] = 0
# runs: (first sample, last sample, side); each laid along the path's own fine line, offset to its side, and the posts
# spaced along that offset line (H5) — (round 35, the play-through: posts 1.8 m apart along the centre, their rope cut
# straight across the inside of a tight hairpin's tip, over the path, and she could not get past)
runs_, cur_ = [], None
for j, smp in enumerate(samples + [None]):
    sd = want_[j] if smp is not None else 0
    if cur_ is not None and sd == cur_[2]:
        cur_[1] = j
        continue
    if cur_ is not None:
        runs_.append(cur_)
    cur_ = [j, j, sd] if sd != 0 else None
for (j0, j1, sd) in runs_:
    i0, i1 = samples[j0][0], samples[j1][0]
    line_ = []
    for i_ in range(i0, i1 + 1):
        nx_, nz_ = _normal(i_)
        q_ = (pts[i_][0] + nx_ * sd * RAIL_OFF, pts[i_][1] + nz_ * sd * RAIL_OFF)
        if not line_ or math.hypot(q_[0] - line_[-1][0][0], q_[1] - line_[-1][0][1]) > 0.05:
            line_.append((q_, i_))
    # posts along the offset line, no more than RAIL_STEP apart (and every bend of it followed: dense at 0.3 first)
    fine_ = []
    for (a_, ia_), (b_, ib_) in zip(line_, line_[1:]):
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        k_ = max(1, math.ceil(L_ / 0.3))
        for t_ in range(k_):
            fine_.append(((a_[0] + (b_[0] - a_[0]) * t_ / k_, a_[1] + (b_[1] - a_[1]) * t_ / k_), ia_))
    if line_:
        fine_.append(line_[-1])
    run = [fine_[0]] if fine_ else []
    acc_, hd0_ = 0.0, None
    for (q_, iq_), (q0_, _) in zip(fine_[1:], fine_):
        sl_ = math.hypot(q_[0] - q0_[0], q_[1] - q0_[1])
        acc_ += sl_
        hd_ = math.atan2(q_[1] - q0_[1], q_[0] - q0_[0]) if sl_ > 1e-6 else hd0_
        if hd0_ is None:
            hd0_ = hd_
        bent_ = abs((hd_ - hd0_ + math.pi) % math.tau - math.pi) if hd_ is not None else 0.0
        # (PATH_RULES D5: never more than 1.8 m apart; D4: round a tight tip closer, so the rope turns smoothly)
        if acc_ >= RAIL_STEP - 0.3 or (bent_ > 0.4 and acc_ > 0.9):
            run.append((q_, iq_))
            acc_, hd0_ = 0.0, hd_
    if fine_ and run[-1] is not fine_[-1]:
        run.append(fine_[-1])
    if len(run) < 6:                                          # H5: long lines only
        continue
    # H6 (round 35, the user: "The fences can leave the path, when they go around the outer curve, in order to get
    # sufficiently close to the hill. The final pole can be right against its base. Then an 'invisible wall' makes
    # sense"): each end of a railing turns off the path to the foot of the nearest bank she can't climb, its last post
    # right against the bank's base, so there is no way round the end — the bank itself is the wall from there
    for end_ in (0, -1):
        q_, iq_ = run[end_]
        qp_ = run[1 if end_ == 0 else -2][0]
        tl_ = math.hypot(q_[0] - qp_[0], q_[1] - qp_[1]) or 1.0
        t_ = ((q_[0] - qp_[0]) / tl_, (q_[1] - qp_[1]) / tl_)              # on along the railing's line
        nx_, nz_ = _normal(iq_)
        n_ = (nx_ * sd, nz_ * sd)                                         # away from the path, the railing's side
        # (round 35, PATH_RULES D2–D4: the shortest way to the bank's foot, but turning only as much as it must, in a
        # curve that leaves the railing's own line without a corner)
        best_ = None
        hp_end_ = any(abs(iq_ - hi_) <= 2 and hs_ == sd for (hi_, hs_) in _HP_ENDS)
        if hp_end_:
            # (D2a: past a hairpin's tip, on along the rope's own line — turning out only as little as it must, away
            # from the path and from any bench — to the foot of the hill, up to 12 m; its last post against it)
            # (out of the bend into the hill, not along the leg; where the bend's outside falls away, on straight ahead
            # to the hill instead — the bench's hairpin: "continue almost straight until it hits the wall")
            for w_ in (0.35, 0.5, 0.65, 0.8, 0.95, 0.2, 0.1, 0.0):
                dx_, dz_ = t_[0] * (1 - w_) + n_[0] * w_, t_[1] * (1 - w_) + n_[1] * w_
                dl_ = math.hypot(dx_, dz_) or 1.0
                dx_, dz_ = dx_ / dl_, dz_ / dl_
                r_ = 0.4
                ok_ = None
                d0_ = N.path_near(q_[0], q_[1])[0]
                while r_ < 12.0:
                    qx_, qz_ = q_[0] + dx_ * r_, q_[1] + dz_ * r_
                    if N.path_near(qx_, qz_)[0] < min(d0_, N.EDGE + 0.4) - 0.15 or \
                            any(math.hypot(qx_ - bb_[0], qz_ - bb_[1]) < 1.4 for bb_ in _BENCHES):
                        break
                    if (gz(qx_ + dx_ * 0.5, qz_ + dz_ * 0.5) - gz(qx_, qz_)) / 0.5 > 0.4 and r_ > 0.9:
                        ok_ = (r_ + 0.3, (qx_ + dx_ * 0.3, qz_ + dz_ * 0.3))
                        break
                    r_ += 0.2
                if ok_ is not None:
                    best_ = (0.0, ok_[0], ok_[1])
                    break
        for ka_ in (range(9) if best_ is None else ()):
            w_ = ka_ / 8.0
            dx_, dz_ = n_[0] * (1 - w_) + t_[0] * w_, n_[1] * (1 - w_) + t_[1] * w_
            dl_ = math.hypot(dx_, dz_) or 1.0
            dx_, dz_ = dx_ / dl_, dz_ / dl_
            r_ = 0.4
            while r_ < 4.0:                          # (D2: the shortest way — a bank close by, or none)
                qx_, qz_ = q_[0] + dx_ * r_, q_[1] + dz_ * r_
                if r_ > 1.6 and N.path_near(qx_, qz_)[0] < N.EDGE + 0.3:
                    break                                         # (never across a path; its own edge is where it starts)
                if (gz(qx_ + dx_ * 0.5, qz_ + dz_ * 0.5) - gz(qx_, qz_)) / 0.5 > 0.4:
                    ang_ = math.acos(max(-1.0, min(1.0, dx_ * t_[0] + dz_ * t_[1])))
                    sc_ = r_ + 2.0 * ang_
                    if r_ > 0.6 * ang_ * 1.5 and (best_ is None or sc_ < best_[0]):   # (D4: a curve, not a corner)
                        best_ = (sc_, r_, (qx_, qz_))
                    break
                r_ += 0.2
        if N.rect_d(q_[0], q_[1], N.FAIR) < 2.2:
            continue                                              # (D5: it ends against the funfair's wall)
        # (D6: by the funicular bend, the rope on the bend's outside ends against the white fence's end post)
        for fe_ in N.FUNI_FENCE_ENDS:
            r2_ = math.hypot(fe_[0] - q_[0], fe_[1] - q_[1])
            if r2_ < 7.0:
                cl_ = all(N.path_near(q_[0] + (fe_[0] - q_[0]) * u_, q_[1] + (fe_[1] - q_[1]) * u_)[0] > N.EDGE
                          for u_ in [k / 10.0 for k in range(1, 11)])
                if cl_:
                    best_ = (0.0, r2_, fe_)
        if best_ is None:
            continue                                              # (no bank near: open ground, H3)
        _, r_, b_ = best_
        c1_ = (q_[0] + t_[0] * r_ * 0.55, q_[1] + t_[1] * r_ * 0.55)        # (a quadratic curve: leaves along the line)
        if hp_end_:
            c1_ = ((q_[0] + b_[0]) / 2, (q_[1] + b_[1]) / 2)                  # (a hairpin's: straight on)
        crv_ = [((1 - u_) ** 2 * q_[0] + 2 * (1 - u_) * u_ * c1_[0] + u_ * u_ * b_[0],
                 (1 - u_) ** 2 * q_[1] + 2 * (1 - u_) * u_ * c1_[1] + u_ * u_ * b_[1]) for u_ in [k / 40.0 for k in range(41)]]
        ext_, acc_ = [], 0.0
        for a2_, b2_ in zip(crv_, crv_[1:]):
            acc_ += math.hypot(b2_[0] - a2_[0], b2_[1] - a2_[1])
            if acc_ >= RAIL_STEP * 0.95:
                ext_.append((b2_, iq_))
                acc_ = 0.0
        if not ext_ or math.hypot(ext_[-1][0][0] - b_[0], ext_[-1][0][1] - b_[1]) > 0.3:
            ext_.append((b_, iq_))
        if end_ == 0:
            run = list(reversed(ext_)) + run
        else:
            run = run + ext_
        if hp_end_ and len(run) >= 5:
            # (the user, on the pictures: "you've sort of curved it around and then it sort of kinks up. Could you just
            # straighten that out… You could even get rid of the last pole"; "the second last pole comes in a little bit…
            # so the four poles are roughly in line") from the fourth post from the end straight to the end, the posts
            # between laid evenly on that line — unless the line would cut over the path's edge
            # (then: "there's still a little kink in it. Could you straighten out that kink?": the line starts a post
            # further back where it can, so it leaves the bend's curve without a kink)
            sq_ = run if end_ != 0 else list(reversed(run))
            for back_ in ((5, 4) if len(sq_) >= 6 else (4,)):
                a2_, e2_ = sq_[-back_][0], sq_[-1][0]
                L2_ = math.hypot(e2_[0] - a2_[0], e2_[1] - a2_[1])
                n2_ = max(1, int(math.ceil(L2_ / RAIL_STEP - 1e-6)))
                new_ = [((a2_[0] + (e2_[0] - a2_[0]) * k2_ / n2_, a2_[1] + (e2_[1] - a2_[1]) * k2_ / n2_), sq_[-1][1]) for k2_ in range(1, n2_ + 1)]
                if all(N.path_near(q2_[0], q2_[1])[0] > RAIL_OFF - 0.1 for (q2_, _) in new_):   # (never nearer the path than the rope runs)
                    sq_ = sq_[:-(back_ - 1)] + new_
                    run = sq_ if end_ != 0 else list(reversed(sq_))
                    break
    # (round 41c, the user: "extend the rope fence so that it covers here and you can't fall down", agreed on the plan
    # round41/fence_gap_plan.png: on the bend's lower leg the rope stopped 1.5 m short of the white lineside fence) a run
    # that ends within 3 m of the white fence's end runs on to just beside its end post (D6)
    for fe_ in N.FUNI_FENCE_ENDS:
        for end_q in (0, -1):
            eq_ = run[end_q][0]
            gd_ = math.hypot(fe_[0] - eq_[0], fe_[1] - eq_[1])
            if 0.35 < gd_ < 3.0:
                k3_ = (gd_ - 0.15) / gd_
                q3_ = ((eq_[0] + (fe_[0] - eq_[0]) * k3_, eq_[1] + (fe_[1] - eq_[1]) * k3_), run[end_q][1])
                run = run + [q3_] if end_q == -1 else [q3_] + run
                print('NORTH rope carried on %.1f m to the white fence at (%.1f, %.1f)' % (gd_ - 0.15, fe_[0], fe_[1]))
    for (q_, iq_) in run:
        nx_, nz_ = _normal(iq_)
        if iq_ >= TOP_LEG_I and nz_ * sd > 0:
            top_posts.append(q_)
    fence([q_ for (q_, _) in run])
    n_rails += 1
    rail_ends.extend([run[0][0], run[-1][0]])
print('NORTH hill railing: %d stretches, on the downhill side and round the bends' % n_rails)

# the glade's two ends: a fence from the top leg's railing, where it stops, down the slope to the leg below's edge
LOWER_LEG = [p for p in pts[380:TOP_LEG_I - 8]]
# (round 35: the west end no more — the hairpin there closes the glade itself, its railing round the outside; a
# fence across the inside of the bend too was the "fences on both sides" the user saw)
for gx_ in ():                # (round 35, PATH_RULES D1: no fence across open grass — the glade is open)
    up_ = min(top_posts, key=lambda q: abs(q[0] - gx_))
    lo_ = min(LOWER_LEG, key=lambda q: abs(q[0] - up_[0]))
    lo_ = (lo_[0], lo_[1] - RAIL_OFF)                                     # (its uphill edge: she may step onto the path)
    k_ = max(2, int(math.hypot(up_[0] - lo_[0], up_[1] - lo_[1]) / RAIL_STEP))
    fence([(up_[0] + (lo_[0] - up_[0]) * t / k_, up_[1] + (lo_[1] - up_[1]) * t / k_) for t in range(k_ + 1)])

# (round 39, the user: "The stone wall needs to have the rope fence (from the hill) starting at the stone path and
# going up around the hill and then sealing off the top at the gate… so Sandra can't get into that area") the hill
# path's rope fence closes the hill east of Gràcia (N.gracia_hill): from against the drystone wall's north end, up
# the wood-side footpath's east edge (on the wall's line), round onto the Carretera del Carmel's outer, downhill side
# 3 m from its middle (past the gravel's frayed edge, on its level shoulder), up the whole road past the Glòria gate,
# and across the road's top just past the Carmel gate, its last post against the park wall beside the gateway's north
# pillar (D5: every end against something solid; D6: never across a gateway). Curves, never corners (D4): the line
# averaged over 3.6 m either way, its ends held. Posts evenly spaced, at most RAIL_STEP apart; solid all along
# (north['rails'], north.gd), so neither she nor the bike gets through.
GH_OFF = 3.0
GH_TOP_Z = -232.0                                     # (where it turns across the road's top, 3.4 m past the gravel's end)
_ghR = dense(N.CARMEL_ROAD, 0.5)
_ghl = []
for k_, (x_, z_) in enumerate(_ghR):
    a_, b_ = _ghR[max(0, k_ - 1)], _ghR[min(len(_ghR) - 1, k_ + 1)]
    L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1]) or 1.0
    nx_, nz_ = -(b_[1] - a_[1]) / L_, (b_[0] - a_[0]) / L_
    if N._seg_near(x_ + nx_ * 3.0, z_ + nz_ * 3.0, N.CARMEL_ROAD)[2] < 0:
        nx_, nz_ = -nx_, -nz_                         # (the side away from the park's wall)
    q_ = (x_ + nx_ * GH_OFF, z_ + nz_ * GH_OFF)
    if q_[0] > N.GRACIA_WALL_X + 0.5 and q_[1] > GH_TOP_Z:
        _ghl.append(q_)
_ghw = (GH_TOP_Z - 0.2 + 233.0) / 23.0                # (the park wall from (168, -233) to (181, -210): its outer face)
_ghe = (168.0 + 13.0 * _ghw + 23.0 / math.hypot(13.0, 23.0) * 0.47, GH_TOP_Z - 0.2 - 13.0 / math.hypot(13.0, 23.0) * 0.47)
_ghl = dense([(N.GRACIA_WALL_X, -121.15), (N.GRACIA_WALL_X, _ghl[0][1] - 0.3)] + _ghl + [_ghe], 0.3)
for _ in range(2):
    _ghl = [_ghl[0]] + [(sum(q[0] for q in _ghl[max(0, i - 12):i + 13]) / len(_ghl[max(0, i - 12):i + 13]),
                         sum(q[1] for q in _ghl[max(0, i - 12):i + 13]) / len(_ghl[max(0, i - 12):i + 13]))
                        for i in range(1, len(_ghl) - 1)] + [_ghl[-1]]
_ghL = sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(_ghl, _ghl[1:]))
_ghn = max(6, math.ceil(_ghL / RAIL_STEP))
_ghp, _gha, _ghk = [_ghl[0]], 0.0, 1
for a_, b_ in zip(_ghl, _ghl[1:]):
    s_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
    while _ghk < _ghn and _gha + s_ >= _ghL * _ghk / _ghn - 1e-9:
        u_ = (_ghL * _ghk / _ghn - _gha) / s_
        _ghp.append((a_[0] + (b_[0] - a_[0]) * u_, a_[1] + (b_[1] - a_[1]) * u_))
        _ghk += 1
    _gha += s_
_ghp.append(_ghl[-1])
fence(_ghp)
print('NORTH Gràcia hill fence: %d posts, %.0f m' % (len(_ghp), _ghL))

# (round 40, the user's picture: "put a rope fence here"; "She's stuck here" — PATH_RULES D7) in Park Güell, the bank
# between the Casa Museu path's hairpin (PARK_PATHS[4]) and the east side stairs' outer wall drops 0.6 m in under a
# metre to the wall's foot: she slid down it and could not climb back. A rope along the outside of the hairpin's upper
# leg and round its turn (D2), 1.8 m out from the path's middle (its edge is 1.5), then the shortest way to the
# stairs' wall at its foot (D5: its last post against it). Curves, never corners (D4); posts at most RAIL_STEP apart.
# (the user, after two wrong tries: "Go back to my red line… take it down lower. You only build half of it… my red
# line corresponds to where there's a steep slope that she might slide down"; agreed on round40/fence_proposal_map.jpg)
# round the outside of the hairpin: from a few metres along the upper leg (the dip at the stairs' foot), round the turn,
# and along the lower leg's downhill side (the ground falls 2 m to the porch), to the end of the low wall below the path.


def side_line(P_, side, off, keep):
    """The line `off` metres to one side of a path (side 1: its left as it runs, -1: its right), where keep(x, z)."""
    d_ = dense(P_, 0.3)
    out_ = []
    for k_, (x_, z_) in enumerate(d_):
        a_, b_ = d_[max(0, k_ - 1)], d_[min(len(d_) - 1, k_ + 1)]
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1]) or 1.0
        dx_, dz_ = (b_[0] - a_[0]) / L_, (b_[1] - a_[1]) / L_
        q_ = (x_ - dz_ * off * side, z_ + dx_ * off * side)
        if keep(*q_):
            out_.append(q_)
    return out_


def rope_line(line_, label, first_post=True):
    """Smoothed (D4: curves, never corners; its ends held), posts evenly at most RAIL_STEP apart, and built."""
    l_ = dense(line_, 0.3)
    for _ in range(2):
        l_ = [l_[0]] + [(sum(q[0] for q in l_[max(0, i - 4):i + 5]) / len(l_[max(0, i - 4):i + 5]),
                         sum(q[1] for q in l_[max(0, i - 4):i + 5]) / len(l_[max(0, i - 4):i + 5]))
                        for i in range(1, len(l_) - 1)] + [l_[-1]]
    L_ = sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(l_, l_[1:]))
    n_ = max(3, math.ceil(L_ / RAIL_STEP))
    p_, acc_, k_ = [l_[0]], 0.0, 1
    for a_, b_ in zip(l_, l_[1:]):
        s_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        while k_ < n_ and acc_ + s_ >= L_ * k_ / n_ - 1e-9:
            u_ = (L_ * k_ / n_ - acc_) / s_
            p_.append((a_[0] + (b_[0] - a_[0]) * u_, a_[1] + (b_[1] - a_[1]) * u_))
            k_ += 1
        acc_ += s_
    p_.append(l_[-1])
    fence(p_, first_post=first_post)
    print('NORTH %s fence: %d posts, %.0f m, from %s to %s' % (label, len(p_), L_, p_[0], p_[-1]))


rope_line(side_line([(133.5, -169.6), (130.0, -167.8), (130.2, -165.0), (134.0, -163.2), (141.5, -162.0)], 1, 1.8,
                    lambda x_, z_: not (z_ < -167.0 and x_ > 132.0) and not (z_ > -165.0 and x_ > 139.0))
          + [(139.4, -159.5)], 'east stairs hairpin')
# (round 40, the user's red line on the covered walk's roof, agreed on a plan first — round40/plan_east_rope.jpg:
# "Yes, build both as drawn on the plans") from the end of the roof's end wall, where the walk opens onto the paths,
# along the downhill edge of the hairpin's upper leg, between it and the bank down to the lower walk
rope_line([(154.1, -200.4), (156.47, -202.08), (160.43, -204.46), (165.93, -207.76)], 'covered walk east end')
# (round 40, the user's red line at the hill path's foot, on the plan round40/r3/plan_path_foot.jpg — "That all sounds
# like a perfect plan": "the fence should continue down where I've marked in red. It should be a continuation of the
# upper fence") from where the path's rope begins, at the barricade, on down the path's downhill (south) edge to just
# above its last bend — past the barricade, which stands free of it
_hp_, _ = N.path_points()
_hr_ = []
_hl_ = 0.0
for a_, b_ in zip(_hp_, _hp_[1:]):
    _hl_ += math.hypot(b_[0] - a_[0], b_[1] - a_[1])
    if _hl_ > N.WORK_L + 4.0:
        break                                      # (only the foot's own stretch, below the barricade)
    dx_, dz_ = b_[0] - a_[0], b_[1] - a_[1]
    L_ = math.hypot(dx_, dz_) or 1.0
    nx_, nz_ = -dz_ / L_, dx_ / L_
    if nz_ < 0:
        nx_, nz_ = -nx_, -nz_
    q_ = (b_[0] + nx_ * 1.35, b_[1] + nz_ * 1.35)
    if -110.74 <= q_[0] <= -96.5:
        _hr_.append(q_)
_hr_ = sorted(_hr_, key=lambda q: q[0])
# (round 41, the user: "That fence should be continuous down the hill" — it ran on 4 m beside the path's railing,
# two ropes side by side above the barricade; PATH_RULES D5) it starts at the railing's own end post there, one line
_hj_ = min(rail_ends, key=lambda q: math.hypot(q[0] + 110.74, q[1] + 110.99))
assert math.hypot(_hj_[0] + 110.74, _hj_[1] + 110.99) < 6.0, _hj_
rope_line([_hj_] + [q for q in _hr_ if q[0] > _hj_[0] + 0.9], 'hill path foot', first_post=False)

# (round 28, the user: "Remove the square that you walk through when going up the hill" — no gateway frame
# any more: the path simply starts off the pavement and climbs)
city_objs.append(rail_mb.finish('HillRail'))
city_objs.append(rope_mb.finish('HillRope'))
print('NORTH rail: %d stretches, %d wall pieces' % (n_rails, len(north['rails'])))
# the workmen's barrier across its foot, and the work site at the first bend (both go once the path is open)
w1x, w1z = N.WORKMEN[0]
_, _, wdx, wdz = N.path_at(N.WORK_L)
d = Vector((wdx, wdz)).normalized()
nn = Vector((-d.y, d.x))
bc = (w1x + d.x * 2.5, w1z + d.y * 2.5)
bar = MB(uv=True)
# (round 25: on across the green strip beside the path too, to the bank, so she can't walk round it)
BAR_W = N.EDGE + N.VERGE + 0.6
# (round 40, the user: "change the barricade to be a movable temporary one. It currently looks like it's a permanent one…
# The color that it has is fine"; "it should look temporary, so it shouldn't impact the rope fence, which continues")
# three free-standing works barriers side by side across the path and its verges: each a frame of thin tube on two
# flat rubber feet, two red-and-white boards between its legs — nothing set into the ground
M_FOOT = mat('BarrierFoot', '#2e2e2e', 0.9)
NPAN = 3
BAR_S0 = -1.22                                   # (its downhill end stops at the rope fence, which carries on past it)
pw_ = (BAR_W - BAR_S0) / NPAN
for k in range(NPAN):
    s0_ = BAR_S0 + k * pw_
    for leg_ in (s0_ + 0.08, s0_ + pw_ - 0.08):
        q_ = (bc[0] + nn.x * leg_, bc[1] + nn.y * leg_)
        g_ = hz(*q_)
        bar.box(V(q_[0], q_[1], g_ + 0.6), (1, 0), (0, 1), 0.022, 0.022, 0.58, M_IRON)              # (a leg)
        bar.box(V(q_[0], q_[1], g_ + 0.035), (d.x, -d.y), (nn.x, -nn.y), 0.32, 0.06, 0.035, M_FOOT)  # (its foot)
    mq_ = (bc[0] + nn.x * (s0_ + pw_ / 2), bc[1] + nn.y * (s0_ + pw_ / 2))
    gm_ = hz(*mq_)
    bar.box(V(mq_[0], mq_[1], gm_ + 1.17), (nn.x, -nn.y), (d.x, -d.y), pw_ / 2 - 0.06, 0.018, 0.018, M_IRON)   # (its top tube)
    for zb_ in (0.55, 0.95):
        nseg_ = 4
        for j_ in range(nseg_):
            t_ = s0_ + 0.1 + (pw_ - 0.2) * (j_ + 0.5) / nseg_
            q_ = (bc[0] + nn.x * t_, bc[1] + nn.y * t_)
            bar.box(V(q_[0], q_[1], hz(*q_) + zb_), (nn.x, -nn.y), (d.x, -d.y), (pw_ - 0.2) / nseg_ / 2, 0.012, 0.09,
                    M_RED if (j_ + k) % 2 == 0 else M_WHITE)
# (round 40, SIGN_FLOAT) the notice, a white board clipped to the middle barrier's top, the words on it
bar.box(V(bc[0], bc[1], hz(*bc) + 1.3) + Vector((d.x * 0.03, d.y * 0.03, 0)), (-d.y, d.x), (d.x, d.y), 0.75, 0.012, 0.13, M_WHITE)
city_objs.append(bar.finish('PathWorks_Barrier'))
# (round 41, rule 10 #16d) the same three barriers once the work is done, pushed aside: stood in a line along the
# uphill verge by the bank, beside where they blocked the path (the game shows them once the path is open)
bar2 = MB(uv=True)
SA_ = N.EDGE + N.VERGE * 0.6                     # (on the verge, clear of the track, short of the bank)
for k in range(NPAN):
    a0_ = (k - NPAN / 2) * pw_
    for leg_ in (a0_ + 0.08, a0_ + pw_ - 0.08):
        q_ = (bc[0] + nn.x * SA_ + d.x * leg_, bc[1] + nn.y * SA_ + d.y * leg_)
        g_ = hz(*q_)
        bar2.box(V(q_[0], q_[1], g_ + 0.6), (1, 0), (0, 1), 0.022, 0.022, 0.58, M_IRON)
        bar2.box(V(q_[0], q_[1], g_ + 0.035), (nn.x, -nn.y), (d.x, -d.y), 0.32, 0.06, 0.035, M_FOOT)
    mq_ = (bc[0] + nn.x * SA_ + d.x * (a0_ + pw_ / 2), bc[1] + nn.y * SA_ + d.y * (a0_ + pw_ / 2))
    bar2.box(V(mq_[0], mq_[1], hz(*mq_) + 1.17), (d.x, -d.y), (nn.x, -nn.y), pw_ / 2 - 0.06, 0.018, 0.018, M_IRON)
    for zb_ in (0.55, 0.95):
        nseg_ = 4
        for j_ in range(nseg_):
            t_ = a0_ + 0.1 + (pw_ - 0.2) * (j_ + 0.5) / nseg_
            q_ = (bc[0] + nn.x * SA_ + d.x * t_, bc[1] + nn.y * SA_ + d.y * t_)
            bar2.box(V(q_[0], q_[1], hz(*q_) + zb_), (d.x, -d.y), (nn.x, -nn.y), (pw_ - 0.2) / nseg_ / 2, 0.012, 0.09,
                     M_RED if (j_ + k) % 2 == 0 else M_WHITE)
city_objs.append(bar2.finish('PathWorks_Aside'))
_ba_ = [(bc[0] + nn.x * SA_ + d.x * s_, bc[1] + nn.y * SA_ + d.y * s_) for s_ in (-NPAN / 2 * pw_, NPAN / 2 * pw_)]
north['barrier_aside'] = [round(min(q[0] for q in _ba_) - 0.25, 2), round(min(q[1] for q in _ba_) - 0.25, 2),
                          round(max(q[0] for q in _ba_) + 0.25, 2), round(max(q[1] for q in _ba_) + 0.25, 2)]
city_objs.append(text_obj('CAMÍ TANCAT PER OBRES', 0.11, M_SIGN_TEXT, V(bc[0], bc[1], hz(*bc) + 1.3) + Vector((d.x * 0.05, d.y * 0.05, 0)),
                          math.atan2(d.x, -d.y), 'PathWorks_Sign'))
# what stops her: the barriers' own line (a thin box round it), so Toni can stand just behind it and be talked to
_be_ = [(bc[0] + nn.x * s_, bc[1] + nn.y * s_) for s_ in (BAR_S0, BAR_W)]
north['barrier'] = [round(min(q[0] for q in _be_) - 0.3, 2), round(min(q[1] for q in _be_) - 0.3, 2),
                    round(max(q[0] for q in _be_) + 0.3, 2), round(max(q[1] for q in _be_) + 0.3, 2)]
# (round 41, the user: "She should be able to move closer to the barricades (there is an invisible wall when she is
# cycling down the hill…)": the box round a slanting line stood up to a metre out from it) the lines themselves, for
# the game's thin bodies along them; the boxes above stay for the tests' maps
north['barrier_line'] = [round(c, 3) for q in _be_ for c in q]
north['barrier_aside_line'] = [round(c, 3) for q in _ba_ for c in q]
w2x, w2z = N.WORKMEN[1]
site = MB(uv=True)
for k in range(5):                                  # traffic cones, a sand heap, a stack of new step-boards
    a = 2 * math.pi * k / 5
    c = V(w2x + math.cos(a) * 1.9, w2z + math.sin(a) * 1.9, hz(w2x, w2z))
    site.cone(Matrix.Translation(c + Vector((0, 0, 0.3))), 8, 0.18, 0.03, 0.6, mat('ConeOrange', '#f07a2a', 0.6))
site.cone(Matrix.Translation(V(w2x - 1.0, w2z - 1.2, hz(w2x, w2z) + 0.3)), 10, 1.0, 0.2, 0.6, M_SAND)
for k in range(4):
    site.box(V(w2x + 1.2, w2z - 1.0, hz(w2x, w2z) + 0.08 + k * 0.1), (1, 0), (0, 1), 0.9, 0.12, 0.05, M_FBARK)
city_objs.append(site.finish('PathWorks_Site'))
# (round 41, the user: "a patch of dirt like they've dug up the grass"; then "the workman's site should be more rounded
# at the edges") the bare earth, a sheet laid just over the grass in a round, uneven outline — the ground's own squares
# stepped at its edge
dirt_ = MB(uv=True)
NA_, NR_ = 72, 8
def _dirt_r(a_):
    return 2.9 + 0.45 * math.sin(a_ * 3.0 + 1.0) + 0.18 * math.sin(a_ * 7.0 + 2.0)
_DIRT_H0 = gz_top(w2x, w2z)
_DIRT_RK = {}
def _dirt_reach(k_):
    # (on the bay's level ground only: the outline drawn in where the bank starts to rise)
    if k_ % NA_ not in _DIRT_RK:
        a_ = math.tau * k_ / NA_
        r_ = _dirt_r(a_)
        while r_ > 1.4 and abs(gz_top(w2x + math.cos(a_) * r_, w2z + math.sin(a_) * r_) - _DIRT_H0) > 0.3:
            r_ -= 0.1
        _DIRT_RK[k_ % NA_] = r_
    return _DIRT_RK[k_ % NA_]
def _dirt_p(k_, r_):
    a_ = math.tau * k_ / NA_
    rr_ = (_dirt_reach(k_ - 1) + 2.0 * _dirt_reach(k_) + _dirt_reach(k_ + 1)) / 4.0
    q_ = (w2x + math.cos(a_) * rr_ * r_ / NR_, w2z + math.sin(a_) * rr_ * r_ / NR_)
    return V(q_[0], q_[1], gz_top(*q_) + 0.02)
for r_ in range(NR_):
    for k_ in range(NA_):
        if r_ == 0:
            dirt_.face([V(w2x, w2z, gz_top(w2x, w2z) + 0.02), _dirt_p(k_, 1), _dirt_p(k_ + 1, 1)], M_PATH,
                       normal=(0, 0, 1), uvscale=2.0)
        else:
            dirt_.face([_dirt_p(k_, r_), _dirt_p(k_, r_ + 1), _dirt_p(k_ + 1, r_ + 1), _dirt_p(k_ + 1, r_)], M_PATH,
                       normal=(0, 0, 1), uvscale=2.0)
city_objs.append(dirt_.finish('PathWorks_Earth'))
north['workmen'] = [list(w) for w in N.WORKMEN]
north['ledge'] = list(N.BALL_LEDGE)
north['slide'] = [list(p) for p in N.SLIDE]

# (round 25) the ball lies in the wood on the slope, just uphill of the tree that stopped it (rolled back off it a little):
# the tree a holm oak 0.85 m downhill of it, a hand to one side (planted with the wood below; no ledge, no fallen log)
north['ball'] = list(N.BALL)
_bx, _bz = N.BALL
_gx, _gz = hz(_bx + 0.5, _bz) - hz(_bx - 0.5, _bz), hz(_bx, _bz + 0.5) - hz(_bx, _bz - 0.5)
_gl = math.hypot(_gx, _gz) or 1.0
BALL_TREE = (_bx - _gx / _gl * 0.85 + _gz / _gl * 0.15, _bz - _gz / _gl * 0.85 - _gx / _gl * 0.15)

def plane_tree_at(x, z, h0, pit=False):
    """The city's plane tree (build_assets.py plane_tree), standing at (x, z) metres on ground h0 high.
    pit: on paving, a round pit of earth with a stone ring (no tree grows straight out of panot)."""
    trees_ = MB(uv=True)
    if pit:
        trees_.cone(Matrix.Translation(Vector((x, -z, h0 + 0.015))) @ Matrix.Rotation(0, 4, 'Z'), 14, 0.75, 0.75, 0.05, mat('TreePitEarth', '#5e4a36', 0.98))
        trees_.cone(Matrix.Translation(Vector((x, -z, h0 + 0.03))), 14, 0.88, 0.88, 0.07, M_KERB, caps=False)
    base = V(x, z, h0)
    h = trng.uniform(2.9, 3.4)
    trees_.cone(Matrix.Translation(base + Vector((0, 0, h / 2))), 8, 0.16, 0.12, h, M_BARK)
    for k in range(3):
        ang, tilt, L = trng.uniform(0, 6.28), trng.uniform(0.45, 0.75), trng.uniform(1.1, 1.6)
        M = Matrix.Translation(base + Vector((0, 0, h - 0.3))) @ Matrix.Rotation(ang, 4, 'Z') @ Matrix.Rotation(tilt, 4, 'X') @ Matrix.Translation((0, 0, L / 2))
        trees_.cone(M, 6, 0.08, 0.04, L, M_BARK)
    canopy = Cards()
    top = base + Vector((0, 0, h + 1.35))
    canopy.clump(top, (1.3, 1.3, 0.8), 18, 1.0, M_PLANE_LEAVES, trng)
    canopy.shell(top, (1.9, 1.9, 1.25), 85, 1.15, M_PLANE_LEAVES, trng)
    for k in range(5):
        a = k * 1.2566 + trng.uniform(-0.3, 0.3)
        sub = top + Vector((math.cos(a) * 1.45, math.sin(a) * 1.45, trng.uniform(-0.35, 0.45)))
        canopy.shell(sub, (0.95, 0.95, 0.8), 24, 0.9, M_PLANE_LEAVES, trng)
    scene['trees'].append([round(x, 3), round(z, 3)])
    idx = len(scene['trees']) - 1
    city_objs.append(trees_.finish('Tree_%d' % idx))
    city_objs.append(canopy.finish('Leaves_%d' % idx))



# ------------------------------------------------------------------ Gràcia (round 26: rebuilt with the city kit)
# (the user: "The buildings in the adjacent suburb are plain, why don't they have the same facades as the rest… You need
# to redo the neighbourhood too. Think about usability, would people live here, does it follow good city design, does the
# direction flow to the right location") Every block is a ring of the kit's houses (kit.py build_house), as the
# Eixample's are, each on its own level of the hill with a stone plinth below (the door at its uphill end); pavements
# with kerbs round every block; granite setts on the streets (world2d.py); Carrer de Larrard climbing straight to the
# park's gate with plane trees and lamps; the square paved, with its trees, benches, fountain and the cafés' tables.
gr = MB(uv=True)                         # pavements, kerbs, the square's furniture
gw = Cards()
GR_PW = 1.8                              # the pavements' width
GR_PAVING = scene.setdefault('paving', [])


def pave_face(pts):
    """(Round 38, the user: the bike, Sandra and the walkers sank into Gràcia's footpaths) a piece of panot, drawn and
    given to the game as drawn (scene 'paving': its four corners [x, z, h], engine metres): main.gd ground_at stands
    everyone on it, kerb and all, not on the 1.65 m ground grid 12 cm and more below."""
    gr.face(pts, M_PANOT, normal=(0, 0, 1), uvscale=2.0)
    GR_PAVING.append([round(c, 3) for p in pts for c in (p.x, -p.y, p.z)])


def gr_inner(poly, depth):
    """The polygon depth metres inside poly (mitred corners); poly's corners are (x, z) metres."""
    n = len(poly)
    cx_ = sum(p[0] for p in poly) / n
    cz_ = sum(p[1] for p in poly) / n
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        d0, d1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((-d0.y, d0.x)), Vector((-d1.y, d1.x))
        if n0.dot(Vector((cx_, cz_)) - p1) < 0:
            n0 = -n0
        if n1.dot(Vector((cx_, cz_)) - p1) < 0:
            n1 = -n1
        bis = n0 + n1
        if bis.length < 1e-6:
            out.append((p1 + n0 * depth))
            continue
        bis.normalize()
        out.append(p1 + bis * (depth / max(0.4, bis.dot(n0))))
    return out


def gracia_block(bi, poly):
    """One block of Gràcia: a ring of the kit's houses round poly (corners (x, z) metres), closed boxes each, the whole
    block one height all round (round 38, rule 06 #11): every house's cornice and roof on the block's one roof line, so
    no side wall or open parapet stands against the sky."""
    global FINE, WINPIC, KIT_DETAIL, FLOOR_H
    KIT_DETAIL = 'full'
    FINE = MB(uv=True)
    WINPIC = MB(uv=True) if WIN_STYLE == 'picture' else None
    rails_begin()                                  # (round 41, rule 02 #5e: near bars, a far picture of them)
    kit = MB(uv=True)
    cards = Cards()
    extras = []
    rng = random.Random(2600 + bi * 17)
    n = len(poly)
    cx_ = sum(p[0] for p in poly) / n
    cz_ = sum(p[1] for p in poly) / n
    ext = min(max(p[0] for p in poly) - min(p[0] for p in poly), max(p[1] for p in poly) - min(p[1] for p in poly))
    inner = gr_inner(poly, min(7.0, ext / 2 - 0.6))
    num = 1 + 2 * rng.randrange(30)
    low_top = 1e9
    # (round 38, the user: "The whole block should be one height. That's how blocks work.") the block's one roof line:
    # its highest front's level plus the block's own count of upper floors (drawn per block, so blocks still differ);
    # a house lower down the hill reaches it with more floors, each stretched to fill it (never under 2.6 m)
    g_hi = max(hz(*Vector(poly[i]).lerp(Vector(poly[(i + 1) % n]), k / 16.0)) for i in range(n) for k in range(17))
    blk_up = random.Random(2650 + bi).choice([2, 3, 3, 4])
    blk_top = g_hi - 0.06 + GROUND_H + blk_up * FLOOR_H
    FLOOR_KIT = FLOOR_H
    for i in range(n):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        ia, ib = inner[i], inner[(i + 1) % n]
        L = (b - a).length
        u = (b - a) / L
        nrm = Vector((-u.y, u.x))
        if nrm.dot(Vector((cx_, cz_)) - a) > 0:
            nrm = -nrm                                           # (out of the block, onto the street)
        ub, nb_ = (u.x, -u.y), (nrm.x, -nrm.y)                   # (Blender's y is engine -z)
        F_ = Frame((a.x, -a.y), ub, nb_)
        nbays = max(2, int(round(L / 3.3)))
        bw = L / nbays
        parts, left = [], nbays
        while left > 0:
            k = min(left, rng.choice([2, 3, 3, 2] if left > 3 else [left]))
            if left - k == 1:
                k = left                                         # (no one-bay slivers)
            parts.append(k)
            left -= k
        t = 0
        for bays in parts:
            s0, width = t * bw, bays * bw
            t += bays
            house = gen_house(rng, bays, False, num)
            num += 2
            rng.choice([2, 3, 3, 4])                              # (round 38: its floors come from the block's roof line,
                                                                  #  below; the dice still thrown, so the rest stays as was)
            house['corner'] = False
            # its level: the street at its front's uphill end; the rest stands on a stone plinth down to the ground
            g0, g1 = hz(*(a + u * s0)), hz(*(a + u * (s0 + width)))
            base = max(g0, g1) - 0.06
            lo = min(g0, g1) - 0.8
            F_.p0 = Vector((a.x, -a.y, base))
            H = blk_top - base                                    # (up to the block's one roof line)
            house['uppers'] = max(1, int((H - GROUND_H) / 2.6))
            house['balc'] = (house['balc'] + ['iron'] * 5)[:house['uppers']]
            house['tribuna'] = [tb for tb in house.get('tribuna', []) if tb[1] < house['uppers']]
            FLOOR_H = (H - GROUND_H) / house['uppers']           # (the kit's storey, stretched to fill it)
            hr = random.Random(house['seed'] * 101 + KIT_SEED)
            build_house(kit, cards, F_, s0, width, house, H, hr, extras)
            FLOOR_H = FLOOR_KIT
            # (round 38, the user: the café's chairs on the steep street "are up in the air… maybe they just get
            # removed") what a shop puts out stands on its own pavement: a frame of its own at the pavement's height
            # (F_ is shared along the side, its height the last house's); on a sloping front, nothing — laid level, it
            # would float over the pavement's lower end
            gw_ = [hz(*(a + u * s_ + nrm * d_)) for s_ in (s0, s0 + width) for d_ in (0.0, 1.8)]
            Fw_ = Frame((a.x, -a.y), ub, nb_)
            Fw_.p0 = Vector((a.x, -a.y, max(gw_)))
            extras[:] = [e_ for e_ in extras if not (e_[0] == 'wares' and e_[2] is house and max(gw_) - min(gw_) > 0.15)]
            extras[:] = [('wares', Fw_) + tuple(e_[2:]) if e_[0] == 'wares' and e_[2] is house else e_ for e_ in extras]
            kit.face([F_.at(s0, 0.02, lo - base), F_.at(s0 + width, 0.02, lo - base), F_.at(s0 + width, 0.02, 0.0), F_.at(s0, 0.02, 0.0)],
                     rustic_mat('#b9a88c'), normal=tuple(F_.N), uvscale=1.2)
            # its flat roof (a terrat with its chimneys), its back and its two sides: a closed box
            P0, P1 = a + u * s0, a + u * (s0 + width)
            Q0, Q1 = ia + (ib - ia) * (s0 / L), ia + (ib - ia) * ((s0 + width) / L)
            top = base + H
            low_top = min(low_top, top)
            kit.face([V(P0.x, P0.y, top), V(P1.x, P1.y, top), V(Q1.x, Q1.y, top), V(Q0.x, Q0.y, top)],
                     ROOF_M[house['seed'] % len(ROOF_M)], normal=(0, 0, 1), uvscale=1.2)
            for _kq in range(hr.randint(1, 2)):
                c = (P0 + P1) / 2 + ((Q0 + Q1) - (P0 + P1)) / 2 * hr.uniform(0.3, 0.7) + u * hr.uniform(-width * 0.3, width * 0.3)
                kit.box(V(c.x, c.y, top + 0.6), ub, nb_, 0.22, 0.22, 0.6, M_CHIMNEY)
                kit.box(V(c.x, c.y, top + 1.25), ub, nb_, 0.28, 0.28, 0.05, M_CHIMNEY)
            kit.face([V(Q0.x, Q0.y, lo), V(Q1.x, Q1.y, lo), V(Q1.x, Q1.y, top), V(Q0.x, Q0.y, top)], M_PARTY, normal=(-nrm.x, nrm.y, 0))
            for (Pe, Qe, sgn) in ((P0, Q0, -1), (P1, Q1, 1)):
                kit.face([V(Pe.x, Pe.y, lo), V(Qe.x, Qe.y, lo), V(Qe.x, Qe.y, top), V(Pe.x, Pe.y, top)], M_PARTY, normal=(u.x * sgn, -u.y * sgn, 0))
    # the block's inside: a low roof (workshops), under every house's roof
    kit.face([V(q.x, q.y, low_top - 0.5) for q in inner], ROOF_M[bi % len(ROOF_M)], normal=(0, 0, 1), uvscale=1.2)
    wares = MB(uv=True)
    signs_and_wares(extras, wares, cards, rng)
    city_objs.append(kit.finish('Block_gr%d' % bi))
    if WINPIC is not None:
        if WINPIC.bm.faces:
            city_objs.append(WINPIC.finish('WinPic_gr%d' % bi))
        else:
            WINPIC.bm.free()
        WINPIC = None
    if FINE.bm.faces:
        city_objs.append(FINE.finish('Detail_gr%d' % bi))
    rails_finish('gr%d' % bi, city_objs)
    FINE = None
    if wares.bm.faces:
        city_objs.append(wares.finish('Wares_gr%d' % bi))
    else:
        wares.bm.free()
    if cards.faces:
        city_objs.append(cards.finish('Plants_gr%d' % bi))
    scene.setdefault('solids', []).append([[round(p[0], 3), round(p[1], 3)] for p in poly])


def on_larrard(a, b, nrm):
    """Does this block face look onto Carrer de Larrard or its continuation, Torrent de l'Olla (the street to the
    gate)? (Round 27: the street narrowed, its east row at x 103; the extra block's west face at 104.)"""
    mx_ = (a.x + b.x) / 2
    return (88.0 < mx_ < 98.0 and nrm.x > 0.5) or (99.0 < mx_ < 107.0 and nrm.x < -0.5)


def gr_pavement(poly, width=GR_PW):
    """A pavement round a block: panot on top, a kerb along its street edge, following the ground (3 m wide along
    Carrer de Larrard, for its trees and lamps; 1.8 m along the lanes)."""
    n = len(poly)
    cx_ = sum(p[0] for p in poly) / n
    cz_ = sum(p[1] for p in poly) / n
    edges = []
    for i in range(n):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        L = (b - a).length
        u = (b - a) / L
        nrm = Vector((-u.y, u.x))
        if nrm.dot(Vector((cx_, cz_)) - a) > 0:
            nrm = -nrm
        edges.append((a, b, L, u, nrm, 3.0 if on_larrard(a, b, nrm) else GR_PW))
    for i, (a, b, L, u, nrm, width) in enumerate(edges):
        # (round 36, the user: "the footpaths at the corners of the building are wrong" — each side ran on round
        # the corner by its OWN width, so a 3 m side poked a square out past the 1.8 m side beside it. The corner
        # is now exactly as deep as the pavement before it: one seamless ring round the block.)
        wprev = edges[i - 1][5]
        a2 = a - u * wprev                                       # (round the corner before it)
        L2 = L + wprev
        k = max(1, int(L2 / 2.5))
        for j in range(k):
            p0, p1 = a2 + u * (L2 * j / k), a2 + u * (L2 * (j + 1) / k)
            q0, q1 = p0 + nrm * width, p1 + nrm * width
            h = [hz(*p) + KERB for p in (p0, p1, q1, q0)]
            pave_face([V(p0.x, p0.y, h[0]), V(p1.x, p1.y, h[1]), V(q1.x, q1.y, h[2]), V(q0.x, q0.y, h[3])])
            # (round 38, rule 05 #7: round 29's gap in the kerb across the gate forecourt is gone — the forecourt is the
            # road's cobbles since round 36, so the corner block's pavement stood flush on them; every pavement edge
            # by a road now has the same 12 cm kerb)
            gr.face([V(q0.x, q0.y, h[3] - KERB - 0.3), V(q1.x, q1.y, h[2] - KERB - 0.3), V(q1.x, q1.y, h[2]), V(q0.x, q0.y, h[3])],
                    M_KERB, normal=(nrm.x, -nrm.y, 0))
            if j == 0:                                            # (the kerb round the corner)
                gr.face([V(p0.x, p0.y, h[0] - KERB - 0.3), V(q0.x, q0.y, h[3] - KERB - 0.3), V(q0.x, q0.y, h[3]), V(p0.x, p0.y, h[0])],
                        M_KERB, normal=(-u.x, u.y, 0))


# (round 38, the user, on the plan workshop/screenshots/round38/plans/gracia_lamps_v3.png: "In that whole area,
# there's too many lamps") the ten they picked come out, and four move: the Plaça de la Vila's three to its corners,
# and one to the pavement facing the square's top edge, where the user marked it
GR_LAMP_OUT = {(96.6, -79.7), (104.0, -47.9), (122.0, -98.55), (58.0, -137.45), (74.0, -120.55), (74.0, -141.55),
               (55.3, -121.4), (58.0, -116.45), (129.9, -106.0), (129.9, -66.0)}
GR_LAMP_MOVE = {(55.3, -136.6): (48.2, -136.8), (64.7, -136.6): (71.8, -136.8), (64.7, -121.4): (71.8, -121.2),
                (104.2, -111.25): (59.0, -142.0)}
# (round 38, the user: "Did you check all of the streetlights in the new district and that they are not sitting right
# at the edge of the pavement? We already did this rule" — rule 07 #33, round 37: every lamp's centre at least 0.8 m in
# from the kerb; Gràcia's still stood 0.35 m in, Larrard's 0.7) each moved in to 0.8 m from its kerb
GR_LAMP_KERB = {(26.0, -116.45): (26.0, -116.0), (42.0, -120.55): (42.0, -121.0), (90.0, -116.45): (90.0, -116.0),
                (26.0, -137.45): (26.0, -137.0), (42.0, -141.55): (42.0, -142.0), (90.0, -137.45): (90.0, -137.0),
                (108.5, -98.55): (108.5, -99.0), (104.2, -127.5): (104.3, -127.5), (104.2, -80.5): (104.3, -80.5),
                (104.2, -58.5): (104.3, -58.5)}


def gr_lamp(x, z, nx, nz):
    """A street lamp on Gràcia's pavement (the city's Meshy lamp), at the ground's own height."""
    key = (round(x, 2), round(z, 2))
    if key in GR_LAMP_OUT:
        return
    if key in GR_LAMP_MOVE:
        x, z = GR_LAMP_MOVE[key]
    elif key in GR_LAMP_KERB:
        x, z = GR_LAMP_KERB[key]
    base = V(x, z, top_ph(x, z) if 'top_ph' in globals() else hz(x, z) + KERB)
    if MESHY_LAMP:
        h = 4.2
        meshy_mesh('lamp.glb', 4000, 'base')
        top = MESHY_TOP['lamp.glb']
        rot = math.atan2(-nz, nx) - math.atan2(top.y, top.x) if Vector((top.x, top.y)).length > 0.03 else 0.0
        meshy_place('lamp.glb', 4000, 'base', h, base, rot, 'MeshyLamp_gr%d' % len(scene['lamps']), 1024)
        lt = Matrix.Rotation(rot, 3, 'Z') @ (top * h) + base
        scene['lamps'].append({'pos': [round(x, 3), round(z, 3)], 'light': [round(lt.x, 3), round(lt.z - 0.15, 3), round(-lt.y, 3)]})
    else:
        gr.cone(Matrix.Translation(base + Vector((0, 0, 1.9))), 8, 0.07, 0.045, 3.6, M_IRON)
        gr.abox(base.x - 0.16, base.y - 0.16, base.z + 3.3, base.x + 0.16, base.y + 0.16, base.z + 3.7, mat('LampGlow', '#f6e2b8', 0.3))
        scene['lamps'].append({'pos': [round(x, 3), round(z, 3)], 'light': [round(base.x, 3), round(base.z + 3.4, 3), round(-base.y, 3)]})
    solid(x - 0.2, z - 0.2, x + 0.2, z + 0.2)


def gr_bench(x, z, ang):
    """A wooden bench on iron feet, facing ang (radians, engine: 0 east, pi/2 south)."""
    hb_ = hz(x, z) + KERB
    u_, n_ = (math.cos(ang + math.pi / 2), -math.sin(ang + math.pi / 2)), (math.cos(ang), -math.sin(ang))
    gr.box(V(x, z, hb_ + 0.45), u_, n_, 0.85, 0.22, 0.03, M_WOODEN)
    gr.box(V(x - n_[0] * 0.2, z + n_[1] * 0.2, hb_ + 0.75), u_, n_, 0.85, 0.03, 0.2, M_WOODEN)
    for sd in (-0.7, 0.7):
        gr.box(V(x + u_[0] * sd, z - u_[1] * sd, hb_ + 0.22), u_, n_, 0.03, 0.2, 0.22, M_IRON)
    solid(x - 0.9, z - 0.9, x + 0.9, z + 0.9)


for bi, blk in enumerate(N.GRACIA_BLOCKS):
    gracia_block(bi, blk)
    if max(p_[0] for p_ in blk) == 96.5:
        continue                                  # (round 36, H2/H3: the closing house stands in the square's own paving)
    if min(p_[1] for p_ in blk) < -149.0:
        continue                                  # (round 36, H6.1: the top row stands in the top edge's one footpath)
    gr_pavement(blk)
# (round 36, H6.7, the user: the square "should feel a bit more open") no longer a sunken terrace with steps and
# walls: one footpath floor from road to road on the ground's own slope (the top edge's paving, below)
pq = N.GRACIA_PLACA
GR_STEPS = []                                                       # (the square's steps: none now; north.gd on_steps)
# the square: six plane trees round its edges, the fountain in the open middle on a level stone step, benches under
# the trees facing it (round 36, H6.7)
pqx, pqz = (pq[0] + pq[2]) / 2, (pq[1] + pq[3]) / 2
for (tx_, tz_) in ((pq[0] + 1.6, pq[1] + 1.4), (pqx, pq[1] + 1.4), (pq[2] - 1.6, pq[1] + 1.4),
                   (pq[0] + 1.6, pq[3] - 1.4), (pqx, pq[3] - 1.4), (pq[2] - 1.6, pq[3] - 1.4)):
    plane_tree_at(tx_, tz_, hz(tx_, tz_) + KERB, pit=True)
ph_lo, ph = min(hz(pqx + ox_, pqz + oz_) for ox_ in (-1.4, 1.4) for oz_ in (-1.4, 1.4)) + KERB, \
    max(hz(pqx + ox_, pqz + oz_) for ox_ in (-1.4, 1.4) for oz_ in (-1.4, 1.4)) + KERB
gr.box(V(pqx, pqz, (ph_lo + ph) / 2 + 0.06), (1, 0), (0, 1), 1.4, 1.4, (ph - ph_lo) / 2 + 0.07, M_STONE)   # its level step
ph += 0.13
gr.cone(Matrix.Translation(V(pqx, pqz, ph + 0.35)), 12, 0.9, 0.8, 0.7, M_STONE)               # the fountain's basin
gr.cone(Matrix.Translation(V(pqx, pqz, ph + 1.1)), 8, 0.18, 0.14, 1.2, M_STONE)
gr.ico(Matrix.Translation(V(pqx, pqz, ph + 1.8)) @ Matrix.Diagonal((0.28, 0.28, 0.2, 1)), 1.0, M_STONE, 1)
solid(pqx - 1.45, pqz - 1.45, pqx + 1.45, pqz + 1.45)
for (bx_, bz_, ba_) in ((pqx - 4.7, pqz - 3.2, 0.0), (pqx + 4.7, pqz - 3.2, math.pi),
                        (pqx - 4.7, pqz + 3.2, 0.0), (pqx + 4.7, pqz + 3.2, math.pi)):
    gr_bench(bx_, bz_, ba_)
# (round 36, the user: "the streetlights and the trees are too close together") along the north and south kerbs,
# between the trees
for (lx_, lz_) in ((pqx - 4.7, pq[1] - 0.6), (pqx + 4.7, pq[1] - 0.6), (pqx - 4.7, pq[3] + 0.6), (pqx + 4.7, pq[3] + 0.6)):
    gr_lamp(lx_, lz_, 1.0, 0.0)
# Carrer de Larrard: plane trees along the west pavement and lamps along the east, each placed from the house fronts
# they stand before (2.3 m out on the 3 m pavement: clear of the walls, by the kerb), people walking it
_, LARR, LW = N.GRACIA_STREETS['larrard']
for blk in N.GRACIA_BLOCKS:
    n_ = len(blk)
    cxb = sum(p[0] for p in blk) / n_
    czb = sum(p[1] for p in blk) / n_
    for i in range(n_):
        a, b = Vector(blk[i]), Vector(blk[(i + 1) % n_])
        L = (b - a).length
        u = (b - a) / L
        nrm = Vector((-u.y, u.x))
        if nrm.dot(Vector((cxb, czb)) - a) > 0:
            nrm = -nrm
        if not on_larrard(a, b, nrm):
            continue
        if cxb > 87.0 and cxb < 98.0 and czb > -70.0:
            continue                                                # (round 36: the closing house fronts the square, not the street)
        west = nrm.x > 0                                            # (the west side's fronts face east)
        k = max(1, int(L / 7.0))
        for j in range(k):
            s_ = L * (j + 0.5) / k
            q = a + u * s_ + nrm * 2.3
            if west:
                plane_tree_at(q.x, q.y, hz(q.x, q.y) + KERB, pit=True)
            elif czb < -46.0 and czb > -96.0:                       # (round 36: the quarter's blocks get a tree and a lamp each)
                if j % 2 == 0:
                    plane_tree_at(q.x, q.y, hz(q.x, q.y) + KERB, pit=True)
                else:
                    gr_lamp(q.x, q.y, -nrm.x, -nrm.y)
            elif j % 2 == 0:
                gr_lamp(q.x, q.y, -nrm.x, -nrm.y)
for (ls_, lw_) in (('sant_salvador', 7.0), ('tres_senyores', 7.0)):
    _, pts_, w_ = N.GRACIA_STREETS[ls_]
    for xk in range(int(pts_[0][0]) + 8, int(pts_[-1][0]) - 4, 16):
        # (round 33: 0.35 m in from the kerb — 1 m out from the fronts was the middle of the 1.8 m pavement)
        gr_lamp(xk, pts_[0][1] + (w_ / 2 - GR_PW + 0.35) * (1 if (xk // 16) % 2 else -1), 0.0, 1.0)
for key_, (name_, pts_, w_) in N.GRACIA_STREETS.items():
    xs_, zs_ = [p[0] for p in pts_], [p[1] for p in pts_]
    north.setdefault('streets', []).append({'name': name_, 'rect': [round(min(xs_) - w_ / 2, 2), round(min(zs_) - w_ / 2, 2),
                                                     round(max(xs_) + w_ / 2, 2), round(max(zs_) + w_ / 2, 2)]})
north['streets'].append({'name': 'Plaça de la Vila de Gràcia', 'rect': list(pq)})
# (round 36, H6, the user's approved mock-up: "just have the cobblestone roads as roads. Have everything else as a
# footpath… the wall should have the footpath along it… a cobblestone road that's continuous around the buildings")
# The top edge: ONE panot footpath over everything paved between the park's wall (or the town's north edge) and the
# road's north kerb, the top row's blocks standing in it, the lanes' cobbles running up into it to their ends; the
# wedge between the road's south kerb and the gate-side block east of Larrard; and the Plaça de la Vila's open floor.
# Laid in columns at most 1 m wide and 2 m long, each corner at the ground's own height plus the kerb's; kerb faces
# only where it meets a carriageway (and round its outer edges onto the grass).
def top_ph(x, z):
    """(Round 38, the user, of the corner by the park's entrance: "still has the mistake") the top edge's footpath east
    of the café is held at the terrace's level, but the road beside it climbs towards the gate and rose to the
    footpath's height and above it (x 88-100, 126-128): no kerb, and the road's ground poked through the paving. The
    footpath's height there: never under the road beside it, plus the kerb."""
    h = hz(x, z) + KERB
    if 82.0 <= x <= N.GRACIA_FOOT_X[0] and z <= N.line_z(N.GRACIA_TOP_ROAD_N, x) + 0.05:
        zr = N.line_z(N.GRACIA_TOP_ROAD_N, x)
        h = max(h, hz(x, zr + 0.3) + KERB, hz(x, zr + 0.8) + KERB)
        if 'GX0' in globals() and x > 94.6:              # (not on the café's terrace, held level: gracia_top_h)
            # (and east of x 94.6 the ground under it climbs to the gate between the grid's 1.65 m points: the paving's
            # flat pieces dipped under the ground's ridges and a notch of it showed through) clear of the ground's
            # highest point round it
            st_ = STEP * T
            i_, j_ = math.floor((x - GX0) / st_), math.floor((z - GZ0) / st_)
            h = max(h, max(hz(GX0 + (i_ + a_) * st_, GZ0 + (j_ + b_) * st_) for a_ in (0, 1) for b_ in (0, 1)) + 0.04)
    elif 106.0 <= x <= 126.0 and z >= N.line_z(N.GRACIA_TOP_ROAD_SE[2:5], x) - 0.05:
        # (the same across the road: the paving east of Larrard's mouth, south of the road to the gate, stood only 2-5 cm
        # over it) never under the road beside it, plus the kerb
        zr = N.line_z(N.GRACIA_TOP_ROAD_SE[2:5], x)
        if x > 123.3:
            # (round 41: round the corner into the lane, the road beside it is the one out from the corner's middle)
            dx_, dz_ = x - 123.3, z + 134.86
            dl_ = math.hypot(dx_, dz_) or 1.0
            px_, pz_ = 123.3 + dx_ / dl_ * 2.5, -134.86 + dz_ / dl_ * 2.5
            return max(h, hz(px_ + dx_ / dl_ * 0.3, pz_ + dz_ / dl_ * 0.3) + KERB, hz(px_ + dx_ / dl_ * 0.8, pz_ + dz_ / dl_ * 0.8) + KERB)
        h = max(h, hz(x, zr - 0.3) + KERB, hz(x, zr - 0.8) + KERB)
    return h


def top_pave(x0, x1, ztop, zbot, kerb_top=False, kerb_bot=False):
    """Panot between ztop(x) (north) and zbot(x) (south) for x0..x1."""
    xs_ = [x0]
    while xs_[-1] < x1 - 1e-6:
        xs_.append(min(x1, xs_[-1] + 1.0))
    for xa_, xb_ in zip(xs_, xs_[1:]):
        ta_, tb_, ba_, bb_ = ztop(xa_), ztop(xb_), zbot(xa_), zbot(xb_)
        if ba_ - ta_ < 0.05 and bb_ - tb_ < 0.05:
            continue
        n_ = max(1, int(math.ceil(max(ba_ - ta_, bb_ - tb_) / 2.0)))
        for k_ in range(n_):
            za0, za1 = ta_ + (ba_ - ta_) * k_ / n_, ta_ + (ba_ - ta_) * (k_ + 1) / n_
            zb0, zb1 = tb_ + (bb_ - tb_) * k_ / n_, tb_ + (bb_ - tb_) * (k_ + 1) / n_
            pave_face([V(xa_, za0, top_ph(xa_, za0)), V(xb_, zb0, top_ph(xb_, zb0)),
                     V(xb_, zb1, top_ph(xb_, zb1)), V(xa_, za1, top_ph(xa_, za1))])
        for (on_, za_, zb_, sgn_) in ((kerb_top, ta_, tb_, -1.0), (kerb_bot, ba_, bb_, 1.0)):
            if on_:
                ha_, hb_ = top_ph(xa_, za_), top_ph(xb_, zb_)
                gr.face([V(xa_, za_, hz(xa_, za_) - 0.3), V(xb_, zb_, hz(xb_, zb_) - 0.3), V(xb_, zb_, hb_), V(xa_, za_, ha_)],
                        M_KERB, normal=(0, -sgn_, 0))


def kerb_x(x_, za_, zb_, nx_):
    """A kerb face down the line x = x_ from za_ to zb_, facing nx_ (onto a lane's cobbles)."""
    z_ = za_
    while z_ < zb_ - 1e-6:
        z2_ = min(zb_, z_ + 2.0)
        h0_, h1_ = hz(x_, z_) + KERB, hz(x_, z2_) + KERB
        gr.face([V(x_, z_, h0_ - KERB - 0.3), V(x_, z2_, h1_ - KERB - 0.3), V(x_, z2_, h1_), V(x_, z_, h0_)], M_KERB,
                normal=(nx_, 0, 0))
        z_ = z2_


_wallz = lambda x_: N.line_z(N.GRACIA_TOP_WALL, x_) if x_ >= N.GRACIA_TOP_WALL[0][0] else -160.0
_roadn = lambda x_: N.line_z(N.GRACIA_TOP_ROAD_N, x_)
_cnorth = lambda x_: -151.5 + (x_ - 66.0) * 0.125                   # the top-left block's north face
_lanes = {(l_[0], l_[1]): l_[2] for l_ in N.GRACIA_TOP_LANES}
_spans = [(18.0, 20.0, None), (20.0, 43.0, -156.0), (43.0, 44.8, None), (44.8, 47.2, 'lane'), (47.2, 49.0, None),
          (49.0, 59.0, -155.0), (59.0, 60.8, None), (60.8, 64.2, 'lane'), (64.2, 66.0, None), (66.0, 82.0, 'c'),
          (82.0, N.GRACIA_FOOT_X[0], None)]
for (x0_, x1_, kind_) in _spans:
    if kind_ is None:                                               # open: wall to road
        top_pave(x0_, x1_, _wallz, _roadn, kerb_bot=True)
    elif kind_ == 'lane':                                           # a lane: footpath only past its top end
        lt_ = _lanes[(x0_, x1_)]
        top_pave(x0_, x1_, _wallz, lambda x_, lt_=lt_: lt_, kerb_bot=True)
        kerb_x(x0_, lt_, _roadn(x0_), 1.0)
        kerb_x(x1_, lt_, _roadn(x1_), -1.0)
    else:                                                           # a block: north of it, and its strip to the road
        nf_ = _cnorth if kind_ == 'c' else (lambda x_, z_=kind_: z_)
        top_pave(x0_, x1_, _wallz, nf_)
        top_pave(x0_, x1_, lambda x_: -143.0, _roadn, kerb_bot=True)
kerb_x(18.0, -160.0, _roadn(18.0), -1.0)                            # (its west end onto the grass)
top_pave(18.0, 61.2, lambda x_: -160.4, lambda x_: -160.0, kerb_top=True)  # (its north edge onto the grass)
# the wedge between the road's south kerb and the gate-side block's pavement, east of Larrard
# (round 41, the user, at the corner where the road to the gate turns down the lane by the wood: "fix this" — the
# footpath came to a sharp point between the two roads) its corner rounded as a street corner is, 2.5 m round,
# meeting the lane's kerb square
_SE_R = 2.5
_SE_ZC = N.line_z(N.GRACIA_TOP_ROAD_SE[2:5], 125.8 - _SE_R) + _SE_R
def _roadse(x_):
    if x_ > 125.8 - _SE_R:
        dx_ = min(_SE_R, x_ - (125.8 - _SE_R))
        return min(-134.8, _SE_ZC - math.sqrt(max(0.0, _SE_R * _SE_R - dx_ * dx_)))
    return N.line_z(N.GRACIA_TOP_ROAD_SE[2:5], x_)
top_pave(106.5, 125.8 - _SE_R, _roadse, lambda x_: -134.8, kerb_top=True)
_xs = [125.8 - _SE_R + _SE_R * k_ / 8.0 for k_ in range(9)]
for xa_, xb_ in zip(_xs, _xs[1:]):                                   # (the round corner, in narrow strips)
    top_pave(xa_, xb_, _roadse, lambda x_: -134.8, kerb_top=True)
if _roadse(125.8) < -134.85:
    kerb_x(125.8, _roadse(125.8), -134.8, 1.0)
# (round 41, the user: "the cobblestone goes right to the end, whereas there should be a footpath sealing it off before
# the grass") the two streets' west ends, where their setts ran straight onto the grass past the blocks' pavements:
# footpath across them, the blocks' own pavement line, a kerb onto the setts and one onto the grass
for (za_, zb_) in ((-120.2, -116.8), (-141.2, -137.8)):
    top_pave(18.2, 20.0, lambda x_, z_=za_: z_, lambda x_, z_=zb_: z_)
    kerb_x(20.0, za_, zb_, 1.0)
    kerb_x(18.2, za_, zb_, -1.0)
# the Plaça de la Vila's floor, road to road (H6.7)
top_pave(47.2, 72.8, lambda x_: -137.8, lambda x_: -120.2, kerb_top=True, kerb_bot=True)
kerb_x(47.2, -137.8, -120.2, -1.0)
kerb_x(72.8, -137.8, -120.2, 1.0)
# before the gate (round 36, H6.2: the forecourt's paving is the road and the footpaths now): the plane tree on the
# corner block's pavement; the east lamp at the kerb of the block's pavement (the user: "must be moved closer to the
# building"); the old west lamp, the second tree and the bench stood in the road, and are gone
fc = N.GRACIA_FORECOURT
plane_tree_at(fc[0] + 3.0, fc[3] - 2.5, hz(fc[0] + 3.0, fc[3] - 2.5) + KERB, pit=True)
gr_lamp(N.PARK_GATE[0] + 6.0, -134.45, 0.0, 1.0)
# (round 27) the quarter south of the Diagonal: the Plaça del Sol, dressed as a town square people live round —
# plane trees in pits, benches, its little astrolabe column (as the real square's), a café's tables under parasols
# on its east side — and the new streets' lamps; the town ends eastward at a low drystone wall along the wood,
# with two gaps where dirt paths slip in between the trees.
SOL = N.GRACIA_SOL
solx, solz = (SOL[0] + SOL[2]) / 2, (SOL[1] + SOL[3]) / 2
# (round 36: every thing in the square laid out as before, then spread out over the floor, N.sol_spread)
for (tx_, tz_) in ((SOL[0] + 1.9, SOL[1] + 2.2), (SOL[2] - 1.9, SOL[1] + 2.2), (SOL[0] + 1.9, SOL[3] - 2.2), (SOL[2] - 1.9, SOL[3] - 2.2)):
    tx_, tz_ = N.sol_spread(tx_, tz_)
    plane_tree_at(tx_, tz_, hz(tx_, tz_) + KERB, pit=True)
# (round 36, H1–H3) the square, the closing house and ONE footpath round both: the whole GRACIA_SQUARE rect is
# paved as one seamless panot surface at kerb height (the house's plinth stands on it), kerbs on its outer edges
# only — so the cobbles stop on the footpath all round and no seam or wall crosses it.
sq_ = N.GRACIA_SQUARE
_sz = sq_[1]
while _sz < sq_[3] - 0.01:
    _sz2 = min(sq_[3], _sz + 2.5)
    _sx = sq_[0]
    while _sx < sq_[2] - 0.01:
        _sx2 = min(sq_[2], _sx + 2.5)
        pave_face([V(_sx, _sz, hz(_sx, _sz) + KERB), V(_sx2, _sz, hz(_sx2, _sz) + KERB),
                 V(_sx2, _sz2, hz(_sx2, _sz2) + KERB), V(_sx, _sz2, hz(_sx, _sz2) + KERB)])
        _sx = _sx2
    _sz = _sz2
for (_ex, _nx) in ((sq_[0], -1.0), (sq_[2], 1.0)):                       # the kerb down its west and east edges
    _sz = sq_[1]
    while _sz < sq_[3] - 0.01:
        _sz2 = min(sq_[3], _sz + 2.5)
        h0_, h1_ = hz(_ex, _sz) + KERB, hz(_ex, _sz2) + KERB
        gr.face([V(_ex, _sz, h0_ - KERB - 0.3), V(_ex, _sz2, h1_ - KERB - 0.3), V(_ex, _sz2, h1_), V(_ex, _sz, h0_)],
                M_KERB, normal=(_nx, 0, 0))
        _sz = _sz2
for (_ez, _nz) in ((sq_[1], 1.0), (sq_[3], -1.0)):                       # and along its north and south edges
    _sx = sq_[0]
    while _sx < sq_[2] - 0.01:
        _sx2 = min(sq_[2], _sx + 2.5)
        h0_, h1_ = hz(_sx, _ez) + KERB, hz(_sx2, _ez) + KERB
        gr.face([V(_sx, _ez, h0_ - KERB - 0.3), V(_sx2, _ez, h1_ - KERB - 0.3), V(_sx2, _ez, h1_), V(_sx, _ez, h0_)],
                M_KERB, normal=(0, -_nz, 0))
        _sx = _sx2
ax_, az_ = N.sol_spread(solx, solz)
sh_ = hz(ax_, az_) + KERB
gr.cone(Matrix.Translation(V(ax_, az_, sh_ + 0.22)), 10, 0.75, 0.62, 0.44, M_STONE)          # the astrolabe's base
gr.cone(Matrix.Translation(V(ax_, az_, sh_ + 1.35)), 8, 0.16, 0.12, 1.9, M_STONE)            # its column
BRONZE_ = mat('SolBronze', '#7a6a3e', 0.45, 0.6)
gr.ico(Matrix.Translation(V(ax_, az_, sh_ + 2.5)) @ Matrix.Diagonal((0.32, 0.32, 0.32, 1)), 1.0, BRONZE_, 1)
gr.box(V(ax_, az_, sh_ + 2.5), (0.7, 0.7), (-0.7, 0.7), 0.5, 0.02, 0.02, BRONZE_)            # the gnomon through it
solid(ax_ - 0.85, az_ - 0.85, ax_ + 0.85, az_ + 0.85)
for (bx_, bz_, ba_) in ((SOL[0] + 2.6, solz - 1.8, 0.0), (SOL[2] - 2.6, solz + 1.8, math.pi),
                        (solx - 2.0, SOL[1] + 1.6, math.pi / 2), (solx + 2.0, SOL[3] - 1.6, -math.pi / 2)):
    gr_bench(*N.sol_spread(bx_, bz_), ba_)
for (lx_, lz_) in N.SOL_LAMPS:
    gr_lamp(lx_, lz_, 1.0, 0.0)


def cafe_table(cx_, cz_, rng_, chairs=None):
    """A little café table on the paving: round top, two chairs (at the angles given, else at random), a parasol in
    warm stripes over it."""
    th_ = top_ph(cx_, cz_)                              # (round 38: on the footpath as drawn)
    gr.cone(Matrix.Translation(V(cx_, cz_, th_ + 0.36)), 6, 0.035, 0.03, 0.72, M_IRON)
    gr.cone(Matrix.Translation(V(cx_, cz_, th_ + 0.74)), 10, 0.42, 0.42, 0.04, M_WOODEN)
    for ca_ in (chairs or (rng_.uniform(0, 2.0), rng_.uniform(2.6, 4.6))):
        chx_, chz_ = cx_ + math.cos(ca_) * 0.72, cz_ + math.sin(ca_) * 0.72
        gr.box(V(chx_, chz_, th_ + 0.23), (math.cos(ca_), -math.sin(ca_)), (math.sin(ca_), math.cos(ca_)), 0.2, 0.2, 0.02, M_WOODEN)
        for (ox_, oz_) in ((-0.15, -0.15), (0.15, -0.15), (-0.15, 0.15), (0.15, 0.15)):
            gr.box(V(chx_ + ox_, chz_ + oz_, th_ + 0.11), (1, 0), (0, 1), 0.015, 0.015, 0.11, M_IRON)
        bk_ = Vector((chx_ - cx_, chz_ - cz_)).normalized() * 0.17
        gr.box(V(chx_ + bk_.x, chz_ + bk_.y, th_ + 0.46), (math.cos(ca_), -math.sin(ca_)), (math.sin(ca_), math.cos(ca_)),
               0.02, 0.2, 0.21, M_WOODEN)                      # (round 38: across the chair, so it faces the table)
    gr.cone(Matrix.Translation(V(cx_, cz_, th_ + 1.35)), 6, 0.025, 0.02, 1.25, M_IRON)
    gr.cone(Matrix.Translation(V(cx_, cz_, th_ + 1.98)), 8, 1.0, 0.06, 0.42, stripes_mat('#e0b64f', '#f5ecd6'))
    solid(cx_ - 0.5, cz_ - 0.5, cx_ + 0.5, cz_ + 0.5)


crng_ = random.Random(2701)
for cz_ in (-78.0, -82.0, -86.0):
    cafe_table(*N.sol_spread(95.1, cz_), crng_)
# (the user: "Is there a cafe on the park?" — round 36, H6.5, the user: "an alfresco dining area… a restaurant on the
# side of that building, like with awnings… someone sitting there… move that up the hill a little bit": the Cafè del
# Parc moved up from Larrard's top, where its tables stood in the road, to the level terrace by the top-left block)
for i_, (cx_, cz_) in enumerate(N.GRACIA_CAFE):
    cafe_table(cx_, cz_, crng_, (0.0, math.pi) if i_ == 1 else None)
scene.setdefault('sitters', []).append({'pos': [round(N.GRACIA_CAFE[1][0] - 0.72, 3), N.GRACIA_CAFE[1][1]],
                                         'yaw': round(math.pi / 2, 4)})                     # (at the table, facing it)
mh_ = hz(83.6, -142.4) + KERB
gr.box(V(83.6, -142.4, mh_ + 0.4), (1, 0), (0, 1), 0.3, 0.025, 0.4, M_WOODEN)                # its menu board, to the road
city_objs.append(text_obj('CAFÈ DEL PARC', 0.09, M_SIGN_TEXT, V(83.6, -142.36, mh_ + 0.62), 0.0, 'CafeParcSign'))
# its front on the block's east side: a striped awning the face's length, its name over it
_cb = [b_ for b_ in N.GRACIA_BLOCKS if min(p_[1] for p_ in b_) < -149.0 and max(p_[0] for p_ in b_) == 82][0]
_ca, _cbb = Vector(_cb[1]), Vector(_cb[2])                          # (82, -143) .. (82, -149.5)
_cu = (_cbb - _ca).normalized()
_cg = max(hz(_ca.x + 0.5, _ca.y), hz(_cbb.x + 0.5, _cbb.y)) - 0.06
CF_ = Frame((_ca.x, -_ca.y), (_cu.x, -_cu.y), (1.0, 0.0))
CF_.p0 = Vector((_ca.x, -_ca.y, _cg))
awning(gr, CF_, (_cbb - _ca).length / 2, (_cbb - _ca).length / 2 - 0.25, 3.05, 1.7, 0.55, '#c4342e', '#f2ead8', 'cafe')
city_objs.append(text_obj('CAFÈ DEL PARC', 0.28, M_SIGN_TEXT, V(_ca.x + 0.05, (_ca.y + _cbb.y) / 2 - 0.6, _cg + 3.27), math.pi / 2,
                          'CafeParcFascia'))
gr_lamp(87.6, -148.2, 0.63, 0.78)                                   # (the user: "another street lamp up against the wall")
for xk in range(90, 126, 14):                                              # Provença's lamps, on its far pavement
    gr_lamp(xk, -47.9, 0.0, -1.0)
# (round 36, the user: "keep some trees around there") plane trees in pits along the Travessera, as before the
# quarter was relaid — in the street band, clear of the junction's mouth and the square's kerb
# (the user: the one above the square "is fine"; east of the Torrent de l'Olla, "the three on the right should only be
# one", on the road's northern side)
# (then, the Plaça del Sol spread out: "trees too close together, remove one" — the one above the square stood in the
# Travessera's mouth, right behind the square's corner tree; only the one on the north side east of the Olla now)
for (tx_, tz_) in ((115.25, -97.4),):
    plane_tree_at(tx_, tz_, hz(tx_, tz_), pit=True)
gr_lamp(129.9, -66.0, -1.0, 0.0)                                           # (round 36: on the wood-side footpath)
gr_lamp(129.9, -86.0, -1.0, 0.0)
gr_lamp(129.9, -106.0, -1.0, 0.0)                                          # (round 36, the user's lamp plan: on up the footpath
gr_lamp(129.9, -126.0, -1.0, 0.0)                                          #  to the road, every 20 m)
gr_lamp(108.5, -98.55, 0.0, 1.0)                                           # (and the Travessera's, on its north pavement,
gr_lamp(122.0, -98.55, 0.0, 1.0)                                           #  either side of its tree; the bar's tables opposite)
# (round 36, H3/H4, replacing round 31's footpath at x 126.4) the cobbles are bounded by a continuous panot
# footpath along the wood (x 128.7..130.5, kerbs both sides): at every street's end the footpath runs through
# unbroken and the setts stop on it. East of it the drystone wall (gaps only at the streets' ends), grass, and
# the wood's ONE gravel path (forest.py's long path, with short gravel spurs through the gaps).
FP_X0, FP_X1 = N.GRACIA_FOOT_X
# (round 36, the user: "make the footpath continue up to the path up the top". Round 39 reverses round 36's "That new
# path should go under the gravel, not over" — the user: "The gravel should go under the footpath when it joins it":
# it climbs at kerb height all the way to the park's wall, kerbed both sides, and the Carretera del Carmel's gravel
# starts under its east kerb (the road's ribbon, below). It ends 0.3 m into the wall — the wall's line is z -144.95
# at x 128.7 and -145.5 at x 130.5 — so no sliver shows between them.)
FP_Z_N = -145.2


def fp_h(x, z):
    """The footpath's top at (x, z): a kerb over the ground at its middle; from z -137 on, where the road's shoulder
    lifts the ground under its east edge, never less than a kerb over the ground's higher split under each corner
    (gz_top), so neither the grass nor the gravel's tucked-in end shows through it."""
    if z > -137.0 + 1e-6:
        return hz((FP_X0 + FP_X1) / 2, z) + KERB
    return max(hz((FP_X0 + FP_X1) / 2, z), gz_top(x, z) - 0.02) + KERB


fpz_ = -47.0
while fpz_ > FP_Z_N + 0.01:
    z2_ = max(FP_Z_N, fpz_ - (2.5 if fpz_ > -137.0 + 0.01 else 0.5))        # (short pieces where it meets the road)
    pave_face([V(FP_X0, fpz_, fp_h(FP_X0, fpz_)), V(FP_X1, fpz_, fp_h(FP_X1, fpz_)), V(FP_X1, z2_, fp_h(FP_X1, z2_)),
             V(FP_X0, z2_, fp_h(FP_X0, z2_))])
    for (sx_, snx_) in ((FP_X0, -1.0), (FP_X1, 1.0)):
        h0_, h1_ = fp_h(sx_, fpz_), fp_h(sx_, z2_)
        gr.face([V(sx_, fpz_, h0_ - KERB - 0.3), V(sx_, z2_, h1_ - KERB - 0.3),
                 V(sx_, z2_, h1_), V(sx_, fpz_, h0_)], M_KERB, normal=(snx_, 0, 0))
    fpz_ = z2_
# Provença's far pavement, the town's south edge, joining the footpath at the corner. (Round 36: its kerb at z
# -49.5, where the setts' last tile row ends — at -48.8 a thin strip of grass showed between them.)
PV_N = -49.5
fpx_ = 86.0
while fpx_ < FP_X0 - 0.01:
    x2_ = min(FP_X0, fpx_ + 2.5)
    h0_, h1_ = hz(fpx_, -47.9) + KERB, hz(x2_, -47.9) + KERB
    pave_face([V(fpx_, PV_N, h0_), V(x2_, PV_N, h1_), V(x2_, -47.0, h1_), V(fpx_, -47.0, h0_)])
    gr.face([V(fpx_, PV_N, h0_ - KERB - 0.3), V(x2_, PV_N, h1_ - KERB - 0.3),
             V(x2_, PV_N, h1_), V(fpx_, PV_N, h0_)], M_KERB, normal=(0, 1, 0))
    gr.face([V(fpx_, -47.0, h0_ - KERB - 0.3), V(x2_, -47.0, h1_ - KERB - 0.3),
             V(x2_, -47.0, h1_), V(fpx_, -47.0, h0_)], M_KERB, normal=(0, -1, 0))
    fpx_ = x2_
_h0 = hz(86.0, -48.25) + KERB                                   # (round 36: its west end, onto Provença's cobbles)
gr.face([V(86.0, PV_N, _h0 - KERB - 0.3), V(86.0, -47.0, _h0 - KERB - 0.3), V(86.0, -47.0, _h0), V(86.0, PV_N, _h0)],
        M_KERB, normal=(-1, 0, 0))
# the wall: long runs of drystone, solid, open where a street's end meets the wood's path (H4)
wrng_ = random.Random(2702)
WG_ = sorted(N.GRACIA_WALL_GAPS)
_wseg = []
_zw = -121.0
for (ga_, gb_) in WG_ + [(-48.0, -47.0)]:
    if ga_ - _zw > 2.0:
        _wseg.append((_zw, ga_))
    _zw = gb_
for (za_, zb_) in _wseg:
    wz_ = za_
    while wz_ < zb_ - 0.6:
        seg_l = min(2.5, zb_ - wz_)
        seg_h = wrng_.uniform(0.62, 0.8)
        gz_ = hz(N.GRACIA_WALL_X, wz_ + seg_l / 2)
        # (round 39, the user: "The wall should not have a gap under it. Just make it go into the ground more") the ground
        # falls away east of it and along it, up the slope to the top road (gaps of up to 0.3 m showed under each piece's
        # lower end): each piece's foot reaches 0.4 m below the lowest drawn ground under its corners and middle (08 #37),
        # its top as before
        _wlo = min([gz(N.GRACIA_WALL_X + _ws, wz_ + _wt) for _ws in (-0.34, 0.34) for _wt in (-0.04, seg_l / 2, seg_l + 0.04)]
                   + [gz_]) - 0.4
        gr.box(V(N.GRACIA_WALL_X, wz_ + seg_l / 2, (_wlo + gz_ + seg_h) / 2), (1, 0), (0, 1), 0.28, seg_l / 2 + 0.04,
               (gz_ + seg_h - _wlo) / 2, M_RUBBLE)
        wz_ += seg_l
    scene.setdefault('solids', []).append([[N.GRACIA_WALL_X - 0.3, za_], [N.GRACIA_WALL_X + 0.3, za_],
                                           [N.GRACIA_WALL_X + 0.3, zb_], [N.GRACIA_WALL_X - 0.3, zb_]])
north['streets'].append({'name': 'Plaça del Sol', 'rect': list(SOL)})
# (round 30, the user: a dirt path is made by people, so it connects to the adjoining footpath — each spur ends
# at the wood's long gravel path. Round 31, the user: "The dirt path never goes ONTO the road. It stops at it.
# Think about how dirt works, it is under grass" — so each stops at the gravel's edge, not over it.)
# (Round 36: those two dirt spurs, at z -70.7 and -80.7, are gone — the footpath and the wall's gaps took their
# place, and their ends lay as tan patches on the setts.)

# people about the streets: along Carrer de Larrard's pavements (round 27: narrower now), across the square,
# down Torrent de l'Olla and over the Plaça del Sol
for (pa_, pb_) in (((97.0, -103.0), (97.0, -132.0)), ((105.0, -103.0), (105.0, -130.0)),
                   ((pq[0] + 2.0, pq[1] + 3.0), (pq[2] - 2.0, pq[3] - 3.0)), ((22.0, -120.5), (92.0, -120.5)),
                   ((102.3, -58.0), (102.3, -90.0)), ((89.5, -75.0), (95.0, -88.5)), ((87.0, -51.0), (126.0, -51.0))):
    scene['people'].append({'a': [pa_[0], pa_[1]], 'b': [pb_[0], pb_[1]]})
city_objs.append(gr.finish('Gracia'))
city_objs.append(gw.finish('Gracia_plants'))
north['gracia_placa'] = [pqx, pqz]

# ------------------------------------------------------------------ Park Güell
G = N.GUELL
pg = MB(uv=True)
pgw = Cards()
# its wall: rubble stone, a coping of trencadís, the gates' palm-leaf iron gates (the game opens them). (Round 25: the
# wall follows N.PARK_WALL, with the main gate and three side gates, Larrard, Carmel and Glòria, as in reality.)
gate = Vector(N.PARK_GATE)
GATES_ALL = [('main', gate)] + [(k, Vector(v)) for k, v in G['side_gates'].items()]
WALLP = N.PARK_WALL + [N.PARK_WALL[0]]
wc_ = Vector(N.PARK_C)
north['park'] = {'c': list(N.PARK_C), 'gate': [gate.x, gate.y], 'wall': [list(p) for p in N.PARK_WALL],
                 'inner': [[round(N.PARK_C[0] + (p[0] - N.PARK_C[0]) * 0.94, 2), round(N.PARK_C[1] + (p[1] - N.PARK_C[1]) * 0.94, 2)]
                           for p in N.PARK_WALL], 'gate_rects': [], 'gate_leaves': []}
# (round 26, the user: "The outer walls don't join… Some walls are single") the wall is one continuous run from pillar
# to pillar now: both its faces, its coping and its ends, mitred round the corners; and the game's solid parts hug it
WALL_T, WALL_H = 0.35, 2.6
GATE_HALF = {g: (2.6 if g == 'main' else 1.9) for g, _ in GATES_ALL}
dense_w = []
for (pa, pb) in zip(WALLP, WALLP[1:]):
    pa, pb = Vector(pa), Vector(pb)
    n_ = max(1, int((pb - pa).length / 1.0))
    for k in range(n_):
        dense_w.append(pa + (pb - pa) * (k / n_))


def gate_reach(p):
    return any((p - gv).length < GATE_HALF[g] + 0.45 for g, gv in GATES_ALL)


keep_w = [not gate_reach(p) for p in dense_w]
start_w = next(i for i in range(len(dense_w)) if not keep_w[i])
wall_runs, cur_ = [], []
for i in [(i + start_w) % len(dense_w) for i in range(len(dense_w))]:
    if keep_w[i]:
        cur_.append(dense_w[i])
    elif cur_:
        wall_runs.append(cur_)
        cur_ = []
if cur_:
    wall_runs.append(cur_)
for run in wall_runs:                                   # each run's ends right against the pillars
    for end, other in ((0, 1), (-1, -2)):
        g, gv = min(GATES_ALL, key=lambda t: (t[1] - run[end]).length)
        run[end] = gv + (run[other] - gv).normalized() * (GATE_HALF[g] + 0.45)


def wall_run(mb, run, half, h_, m_side, m_top, cope=0.1, seg0=0):
    pts = []
    for i, p in enumerate(run):
        d0 = (p - run[i - 1]).normalized() if i > 0 else (run[1] - p).normalized()
        d1 = (run[i + 1] - p).normalized() if i < len(run) - 1 else d0
        n0, n1 = Vector((-d0.y, d0.x)), Vector((-d1.y, d1.x))
        bis = n0 + n1
        bis = bis.normalized() if bis.length > 1e-6 else n0
        k = 1.0 / max(0.4, abs(bis.dot(n0)))
        if bis.dot(p - wc_) < 0:
            bis = -bis                                   # (out of the park)
        g_ = hz(p.x, p.y)
        if 58.0 <= p.x <= 95.0 and -162.0 < p.y < -140.0:
            # (round 36, H6.5: the town's ground is lowered to the terrace's level up to the wall's line and under it;
            # the wall's top keeps to the park's ground, so it stands taller over the terrace)
            q_ = p - bis.normalized() * 2.6
            g_ = max(g_, hz(q_.x, q_.y))
        pts.append((p, bis * k, g_))
    # (round 27, the user: "The wall to the south east of the gaudi park is in a ditch. Raise it.") the wall's top
    # rides over dips in the ground instead of diving into them: each point's base is lifted towards the highest
    # ground within a few metres (the base still reaches 0.4 m down, so no gap opens beneath)
    gs_ = [g for (_p, _m, g) in pts]
    for i_ in range(len(pts)):
        lo_, hi_ = max(0, i_ - 3), min(len(gs_), i_ + 4)
        pts[i_] = (pts[i_][0], pts[i_][1], max(gs_[i_], max(gs_[lo_:hi_]) - 0.25))
    for si, ((p0, m0, g0), (p1, m1, g1)) in enumerate(zip(pts, pts[1:])):
        b0_, b1_ = min(g0, gs_[si]) - 0.4, min(g1, gs_[si + 1]) - 0.4       # (down to the real ground in a dip)
        for s_ in (1, -1):                               # the two faces
            q0, q1 = p0 + m0 * half * s_, p1 + m1 * half * s_
            # (round 34: down to the ground on each side — the road outside the east wall lies lower than the wall's
            # own line now, and a gap showed under its face)
            b0_ = min(b0_, hz(*(p0 + m0 * (half + 0.6) * s_)) - 0.4)
            b1_ = min(b1_, hz(*(p1 + m1 * (half + 0.6) * s_)) - 0.4)
            mb.face([V(q0.x, q0.y, b0_), V(q1.x, q1.y, b1_), V(q1.x, q1.y, g1 + h_), V(q0.x, q0.y, g0 + h_)], m_side,
                    normal=(m0.x * s_, -m0.y * s_, 0))
            # (round 34, the user: "how the walls… meet the ground. It should look like it would join like in the real
            # world") a footing of bigger, darker stones along each face's foot, a hand proud of it, its top sloped
            # back into the wall; it follows the ground on its own side (the street's paving or the park's lawn)
            f0, f1 = p0 + m0 * (half + 0.09) * s_, p1 + m1 * (half + 0.09) * s_
            e0_ = hz(*(p0 + m0 * (half + 0.6) * s_)) + 0.42
            e1_ = hz(*(p1 + m1 * (half + 0.6) * s_)) + 0.42
            mb.face([V(f0.x, f0.y, b0_), V(f1.x, f1.y, b1_), V(f1.x, f1.y, e1_), V(f0.x, f0.y, e0_)], M_WALLFOOT,
                    normal=(m0.x * s_, -m0.y * s_, 0))
            mb.face([V(f0.x, f0.y, e0_), V(f1.x, f1.y, e1_), V(q1.x, q1.y, e1_ + 0.1), V(q0.x, q0.y, e0_ + 0.1)], M_WALLFOOT,
                    normal=(m0.x * s_, -m0.y * s_, 1.0))
        c0a, c0b, c1a, c1b = p0 + m0 * (half + cope), p0 - m0 * (half + cope), p1 + m1 * (half + cope), p1 - m1 * (half + cope)
        t0, t1 = g0 + h_ + 0.08, g1 + h_ + 0.08
        mb.face([V(c0b.x, c0b.y, t0), V(c1b.x, c1b.y, t1), V(c1a.x, c1a.y, t1), V(c0a.x, c0a.y, t0)], m_top, normal=(0, 0, 1))
        for (ca0, ca1, s_) in ((c0a, c1a, 1), (c0b, c1b, -1)):
            mb.face([V(ca0.x, ca0.y, g0 + h_ - 0.1), V(ca1.x, ca1.y, g1 + h_ - 0.1), V(ca1.x, ca1.y, t1), V(ca0.x, ca0.y, t0)], m_top,
                    normal=(m0.x * s_, -m0.y * s_, 0))
            qa0, qa1 = p0 + m0 * half * s_, p1 + m1 * half * s_
            mb.face([V(qa0.x, qa0.y, g0 + h_ - 0.1), V(qa1.x, qa1.y, g1 + h_ - 0.1), V(ca1.x, ca1.y, g1 + h_ - 0.1), V(ca0.x, ca0.y, g0 + h_ - 0.1)],
                    m_top, normal=(0, 0, -1))
        if (si + seg0) % 18 == 9:                        # the round medallions: 'Park' 'Güell'
            mm_ = (p0 + p1) / 2 + m0 * (half + 0.03)
            mb.cone(Matrix.Translation(V(mm_.x, mm_.y, (g0 + g1) / 2 + 1.7))
                    @ Vector((0, 0, 1)).rotation_difference(V(m0.x, m0.y, 0).normalized()).to_matrix().to_4x4(), 16, 0.55, 0.55, 0.06, M_TRENC_BW)
        cs = [p0 + m0 * half, p0 - m0 * half, p1 + m1 * half, p1 - m1 * half]
        solid(min(c.x for c in cs), min(c.y for c in cs), max(c.x for c in cs), max(c.y for c in cs))
    for (p, m, g), other in ((pts[0], pts[1]), (pts[-1], pts[-2])):     # its ends, against the pillars
        d = (p - other[0]).normalized()
        qa, qb = p + m * (half + cope), p - m * (half + cope)
        mb.face([V(qa.x, qa.y, g - 0.4), V(qb.x, qb.y, g - 0.4), V(qb.x, qb.y, g + h_ + 0.08), V(qa.x, qa.y, g + h_ + 0.08)], m_side,
                normal=(d.x, -d.y, 0))


seg_acc = 0
for run in wall_runs:
    wall_run(pg, run, WALL_T, WALL_H, M_RUBBLE, M_TRENC, seg0=seg_acc)
    seg_acc += len(run)
GATE_GAP = 0.15                         # (round 38) the most the ground under a leaf's swing may rise over its shut line
GATE_PAVE = [q for q in GR_PAVING if any(math.hypot(q[0] - gv_.x, q[1] - gv_.y) < 12.0 for _g, gv_ in GATES_ALL)]


def pave_top(q, x, z):
    """A piece of paving's height at (x, z) — the higher of its two triangles, as main.gd paving_h — or None off it."""
    best = None
    for t in ((0, 1, 2), (0, 2, 3), (0, 1, 3), (1, 2, 3)):
        i0, i1, i2 = t[0] * 3, t[1] * 3, t[2] * 3
        bx, bz, cx, cz = q[i1] - q[i0], q[i1 + 1] - q[i0 + 1], q[i2] - q[i0], q[i2 + 1] - q[i0 + 1]
        det = bx * cz - bz * cx
        if abs(det) < 1e-6:
            continue
        px, pz = x - q[i0], z - q[i0 + 1]
        u, v = (px * cz - pz * cx) / det, (bx * pz - bz * px) / det
        if u < -0.002 or v < -0.002 or u + v > 1.002:
            continue
        h = q[i0 + 2] + u * (q[i1 + 2] - q[i0 + 2]) + v * (q[i2 + 2] - q[i0 + 2])
        best = h if best is None else max(best, h)
    return best


def gate_ground(x, z):
    """(round 38) the ground as drawn under a gate's leaf: the grid's higher triangle, or the paving laid over it."""
    h = gz_top(x, z)
    for q in GATE_PAVE:
        p_ = pave_top(q, x, z)
        if p_ is not None:
            h = max(h, p_)
    return h


# each gate: two pillars, the iron gates (palm leaves in the ironwork)
for gname, gv in GATES_ALL:
    wi = min(range(len(WALLP) - 1), key=lambda i: (Vector(WALLP[i]) + (Vector(WALLP[i + 1]) - Vector(WALLP[i])) * max(0.0, min(1.0,
             (gv - Vector(WALLP[i])).dot(Vector(WALLP[i + 1]) - Vector(WALLP[i])) / (Vector(WALLP[i + 1]) - Vector(WALLP[i])).length_squared)) - gv).length)
    ud = (Vector(WALLP[wi + 1]) - Vector(WALLP[wi])).normalized()          # (along the wall there)
    half = 2.6 if gname == 'main' else 1.9
    gh = hz(gv.x, gv.y)
    nn_g = Vector((-ud.y, ud.x))
    if nn_g.dot(wc_ - gv) < 0:
        nn_g = -nn_g                                                        # (into the park)
    # (round 34, the user: "when you approach the main entrance from the west there is a gap in the gate and the
    # wall": the main gate stands where the wall turns, and both pillars were set along the east stretch's line — the
    # west one a metre forward of the west wall's end. Each pillar now stands on its own stretch's line, at its end.)
    ends_ = sorted([r_[0] for r_ in wall_runs] + [r_[-1] for r_ in wall_runs], key=lambda e_: (e_ - gv).length)[:2]
    leaves_ = []
    for e_ in ends_:
        du_ = (e_ - gv).normalized()
        s_ = 1 if du_.dot(ud) > 0 else -1
        pc = gv + du_ * half
        pg.box(V(pc.x, pc.y, gh + 1.6), (du_.x, -du_.y), (-du_.y, -du_.x), 0.45, 0.45, 1.6, M_RUBBLE)
        pg.box(V(pc.x, pc.y, gh + 3.3), (du_.x, -du_.y), (-du_.y, -du_.x), 0.5, 0.5, 0.12, M_TRENC)
        solid(pc.x - 0.5, pc.y - 0.5, pc.x + 0.5, pc.y + 0.5)
        # (round 38, 06 #97: shut until she has the ticket) each leaf its own object, built shut across the opening,
        # its origin on its hinge: the game swings it open (GuellGate_<gate>_<n>; 'gate_leaves' says how far). The
        # open leaf's solid is the game's too (north.gd), only while it stands open — no 'blocked' box here.
        # (round 38, the user: "make sure they don't open into the floor… the gates should open outwards, whereas the
        # primary gate can open inwards because it's flat") the main gate swings into the park, the side gates out to
        # the street, 80° (never past 90°: the hinge is at the pillar's face), less, down to 40°, where the ground under
        # the swing rises more than GATE_GAP over the ground under the shut leaf. Each bar's foot stands 5 cm over the
        # highest ground its swing passes (raked on a slope), so no leaf ever passes through the ground; its top is
        # level, 2.4 m over its lowest foot (and at least 1.2 m over its highest).
        hinge = gv + du_ * (half - 0.45)
        uc = -du_                                                           # shut: from the hinge to the middle
        leaf = half - 0.47                                                  # (the two leaves meet in the middle)
        a_shut = math.atan2(uc.x, uc.y)
        side_ = 1
        for sg_ in (1, -1):
            into_ = math.sin(a_shut + sg_ * 1.4) * nn_g.x + math.cos(a_shut + sg_ * 1.4) * nn_g.y > 0
            if into_ == (gname == 'main'):
                side_ = sg_
        nb = int(leaf / 0.32) + 1
        bar_r = [0.14 + k * (leaf - 0.2) / (nb - 1) for k in range(nb)]

        def swing_ground(r, deg):
            hs_ = []
            for rr in (max(0.1, r - 0.16), r, min(leaf, r + 0.16)):
                for t in range(0, deg + 1, 5):
                    a_ = a_shut + side_ * math.radians(t)
                    hs_.append(gate_ground(hinge.x + math.sin(a_) * rr, hinge.y + math.cos(a_) * rr))
            return max(hs_)

        shut_g = [swing_ground(r, 0) for r in bar_r]
        deg_ = 80
        while deg_ > 40 and max(swing_ground(r, deg_) - g0 for r, g0 in zip(bar_r, shut_g)) > GATE_GAP:
            deg_ -= 5
        feet_ = [swing_ground(r, deg_) + 0.05 - gh for r in bar_r]          # (above the pivot, gh)
        ltop_ = max(min(feet_) + 2.4, max(feet_) + 1.2)
        lm = MB(uv=True)
        for rb_, fb_ in zip(bar_r, feet_):                                       # (bars right out to the meeting stile)
            q = hinge + uc * rb_
            lm.box(V(q.x, q.y, gh + (fb_ + ltop_) / 2), (uc.x, -uc.y), (-uc.y, -uc.x), 0.02, 0.02, (ltop_ - fb_) / 2, M_IRON)
        for z_ in (ltop_ - 0.1, max(ltop_ - 1.2, max(feet_) + 0.3)):            # the top and middle rails, level
            q = hinge + uc * leaf / 2
            lm.box(V(q.x, q.y, gh + z_), (uc.x, -uc.y), (-uc.y, -uc.x), leaf / 2, 0.02, 0.02, M_IRON)
        rk_ = [(0.0, feet_[0])] + list(zip(bar_r, feet_)) + [(leaf, feet_[-1])]
        for (r0_, f0_), (r1_, f1_) in zip(rk_, rk_[1:]):                    # the bottom rail, raked with the feet
            q0_, q1_ = hinge + uc * r0_, hinge + uc * r1_
            lm.tube(V(q0_.x, q0_.y, gh + f0_ + 0.15), V(q1_.x, q1_.y, gh + f1_ + 0.15), 0.022, M_IRON, 4)
        for k in range(max(2, nb // 2)):                                    # palm leaves
            q = hinge + uc * (0.35 + k * 0.45)
            lm.cone(Matrix.Translation(V(q.x, q.y, gh + ltop_ - 0.7)) @ Matrix.Rotation(0.4 * s_, 4, 'Y'), 4, 0.12, 0.0, 0.8, M_IRON)
        nm_ = 'GuellGate_%d_%d' % (len(north['park']['gate_rects']), len(leaves_))
        city_objs.append(finish_at(lm, nm_, (hinge.x, hinge.y, gh)))
        sw_ = side_ * math.radians(deg_)                                    # the swing about the upright (Godot rotation.y)
        print('NORTH gate leaf %s: opens %s %d°, feet %.2f..%.2f m over the pivot, rise under the swing %.2f m' % (
            nm_, 'in' if gname == 'main' else 'out', deg_, min(feet_), max(feet_),
            max(swing_ground(r, deg_) - g0 for r, g0 in zip(bar_r, shut_g))))
        leaves_.append({'name': nm_, 'hinge': [round(hinge.x, 3), round(hinge.y, 3)], 'len': round(leaf, 3),
                        'open': round(sw_, 4), 'open_dir': [round(math.sin(a_shut + sw_), 4), round(math.cos(a_shut + sw_), 4)],
                        'foot': [[round(rb_, 3), round(fb_, 3)] for rb_, fb_ in zip(bar_r, feet_)]})
    nn_ = Vector((-ud.y, ud.x))
    c0, c1 = gv - ud * (half - 0.4) - nn_ * 0.4, gv + ud * (half - 0.4) + nn_ * 0.4
    north['park']['gate_rects'].append([round(min(c0.x, c1.x), 2), round(min(c0.y, c1.y), 2), round(max(c0.x, c1.x), 2), round(max(c0.y, c1.y), 2)])
    north['park']['gate_leaves'].append(leaves_)
north['park']['gate_rect'] = north['park']['gate_rects'][0]
# (round 35, PATH_RULES F14, the user: "make a rule that the bike is not allowed in the park") each gateway stops the
# bike (a no-bike box across it, a metre deep); inside the wall she can't get on (main.gd, the park's outline)
for gr_ in north['park']['gate_rects']:
    cxg_, czg_ = (gr_[0] + gr_[2]) / 2, (gr_[1] + gr_[3]) / 2
    hx_, hz_ = max(0.6, (gr_[2] - gr_[0]) / 2 + 0.2), max(0.6, (gr_[3] - gr_[1]) / 2 + 0.2)
    scene.setdefault('nobike', []).append([round(cxg_ - hx_, 2), round(czg_ - hz_, 2), round(cxg_ + hx_, 2), round(czg_ + hz_, 2)])

# the two lodges: Casa del Guarda (west) with its blue-and-white cap; the other (east) with its tower and cross
for key, roof_m, tower in (('guarda', M_TRENC_BW, False), ('lodge', M_TRENC_BROWN, True)):
    lx_, lz_ = G[key]
    h0 = hz(lx_, lz_) - 0.2
    # (round 26: rounded corners, as the real lodges have: a cylinder of stone at each corner, the walls between)
    pg.box(V(lx_, lz_, h0 + 2.3), (1, 0), (0, 1), 2.7, 3.2, 2.3, M_RUBBLE)
    pg.box(V(lx_, lz_, h0 + 2.3), (1, 0), (0, 1), 3.6, 2.3, 2.3, M_RUBBLE)
    for cxr in (-2.7, 2.7):
        for czr in (-2.3, 2.3):
            pg.cone(Matrix.Translation(V(lx_ + cxr, lz_ + czr, h0 + 2.3)), 14, 0.9, 0.9, 4.6, M_RUBBLE, uvscale=1.0)
    pg.box(V(lx_, lz_, h0 + 4.9), (1, 0), (0, 1), 3.4, 3.0, 0.4, M_OCHRE)
    pg.box(V(lx_, lz_, h0 + 5.35), (1, 0), (0, 1), 3.5, 3.1, 0.12, M_TRENC)
    for (wx_, wz_, u_, n_) in ((lx_ - 3.62, lz_ + 0.2, (0, 1), (1, 0)), (lx_, lz_ - 3.22, (1, 0), (0, 1)), (lx_ + 3.62, lz_ - 0.6, (0, 1), (1, 0))):
        if key == 'guarda' and wx_ > lx_ + 3.0:
            continue                                     # (round 33: the guard's door is here, not a window)
        pg.box(V(wx_, wz_, h0 + 2.5), u_, n_, 0.62, 0.05, 0.9, M_WHITE)                          # a window on each other side
        pg.box(V(wx_, wz_, h0 + 2.5), u_, n_, 0.48, 0.06, 0.74, M_GLASS)
        pg.box(V(wx_, wz_, h0 + 3.5), u_, n_, 0.75, 0.08, 0.1, M_TRENC)
    pg.ico(Matrix.Translation(V(lx_, lz_, h0 + 5.4)) @ Matrix.Diagonal((3.4, 3.0, 2.6, 1)), 1.0, roof_m, 2)
    pg.cone(Matrix.Translation(V(lx_ + 1.2, lz_ - 0.8, h0 + 8.2)), 10, 0.35, 0.3, 1.4, M_WHITE)        # the toadstool chimney
    pg.ico(Matrix.Translation(V(lx_ + 1.2, lz_ - 0.8, h0 + 9.0)) @ Matrix.Diagonal((0.85, 0.85, 0.45, 1)), 1.0, M_RED if tower else M_WHITE, 2)
    for sx in (-1.6, 1.6):
        pg.box(V(lx_ + sx, lz_ + 3.22, h0 + 2.6), (1, 0), (0, 1), 0.6, 0.04, 0.9, M_WHITE)
        pg.box(V(lx_ + sx, lz_ + 3.25, h0 + 2.6), (1, 0), (0, 1), 0.45, 0.03, 0.75, M_GLASS)
        pg.box(V(lx_ + sx, lz_ + 3.24, h0 + 3.55), (1, 0), (0, 1), 0.7, 0.06, 0.12, M_TRENC)
    pg.cone(Matrix.Translation(V(lx_ - 2.4, lz_ + 1.5, h0 + 6.0)), 10, 0.3, 0.26, 1.2, M_WHITE)                   # a second little chimney
    pg.ico(Matrix.Translation(V(lx_ - 2.4, lz_ + 1.5, h0 + 6.7)) @ Matrix.Diagonal((0.7, 0.7, 0.4, 1)), 1.0, M_TRENC_BW, 2)
    if tower:                                                               # a slim tower with Gaudí's four-armed cross
        pg.cone(Matrix.Translation(V(lx_ - 1.8, lz_ - 1.0, h0 + 8.0)), 12, 0.95, 0.7, 9.0, M_TRENC_BW)
        for ax_d in ((1, 0), (0, 1)):
            pg.box(V(lx_ - 1.8, lz_ - 1.0, h0 + 13.0), (ax_d[0], ax_d[1]), (-ax_d[1], ax_d[0]), 0.55, 0.12, 0.12, M_WHITE)
        pg.box(V(lx_ - 1.8, lz_ - 1.0, h0 + 13.1), (1, 0), (0, 1), 0.12, 0.12, 0.55, M_WHITE)
    solid(lx_ - 3.6, lz_ - 3.2, lx_ + 3.6, lz_ + 3.2)
    cam_building(lx_ - 3.6, lz_ - 3.2, lx_ + 3.6, lz_ + 3.2, h0 - 0.3, h0 + 9.0)          # (a gate lodge)
# (round 33, the user: the glow on a bare wall under a window — "the actual door should be glowing"): its door, in
# a white surround with the lodges' trencadís over it, the glow on it
_gx, _gz = G['guarda']
_gd = hz(_gx + 4.3, _gz - 0.6)
door_unit(pg, V(_gx + 3.6, _gz - 0.6, _gd), (0, 1), (1, 0), 1.3, 2.3, 0.0, M_WOOD_DOOR, M_WHITE, fw=0.16, depth=0.24)
pg.box(V(_gx + 3.66, _gz - 0.6, _gd + 2.62), (0, 1), (1, 0), 0.9, 0.08, 0.1, M_TRENC)
post_sign(_gx + 4.5, _gz - 2.5, 1.0, 0.0, 'CASA DEL GUARDA', 'museu del parc')
door('guarda', 'Casa del Guarda', 'int_guarda', _gx + 3.72, _gz - 0.6, 1.0, 0.0, 1.3, h=2.3, base=_gd, glow=(_gx + 3.7, _gz - 0.6),
     plaque=
     "CASA DEL GUARDA. The porter's lodge, 1904, with its cap of blue and white trencadís. Today a little museum of the park's story.")


def wedge_wall(mb, x, za, zb, lo_a, lo_b, hi_a, hi_b, half, m):
    """(round 26) A wall along z from za to zb on the line x, its foot at lo_a..lo_b and its top at hi_a..hi_b: both
    faces, its top and its ends, so it is a wall from every side."""
    for sx, nx in ((x - half, -1), (x + half, 1)):
        mb.face([V(sx, za, lo_a), V(sx, zb, lo_b), V(sx, zb, hi_b), V(sx, za, hi_a)], m, normal=(nx, 0, 0))
    mb.face([V(x - half, za, hi_a), V(x + half, za, hi_a), V(x + half, zb, hi_b), V(x - half, zb, hi_b)], m, normal=(0, 0, 1))
    for zz, hlo, hhi in ((za, lo_a, hi_a), (zb, lo_b, hi_b)):
        out = 1 if zz == max(za, zb) else -1              # (engine +z is Blender -y)
        mb.face([V(x - half, zz, hlo), V(x + half, zz, hlo), V(x + half, zz, hhi), V(x - half, zz, hhi)], m, normal=(0, -out, 0))


# the dragon stairs: a double flight with walls of trencadís, the salamander on the middle landing, a grotto fountain
x0s, z0s, x1s, z1s = G['stairs_r']
nst = 14
for k in range(nst):
    z = z1s - (z1s - z0s) * (k + 0.5) / nst
    h_ = 6.0 + 3.0 * (k + 0.5) / nst
    for lane in ((x0s, x0s + 2.6), (x1s - 2.6, x1s)):
        pg.box(V((lane[0] + lane[1]) / 2, z, h_ - 0.5), (1, 0), (0, 1), (lane[1] - lane[0]) / 2, (z1s - z0s) / nst / 2, 0.5 + 0.05, M_STONE)
mid_x = (x0s + x1s) / 2
# (round 33, the user: "There are colour items sitting on the stairs") the three trencadís planters down the middle,
# with agaves, gone: one low stone divider up the middle instead, a trencadís coping, the salamander on its landing
for k in range(nst):
    z = z1s - (z1s - z0s) * (k + 0.5) / nst
    h_ = 6.0 + 3.0 * (k + 0.5) / nst
    if abs(z - (z1s - 8.0)) < 1.6:
        continue                                                            # (the salamander's landing)
    pg.box(V(mid_x, z, h_ + 0.15), (1, 0), (0, 1), 0.75, (z1s - z0s) / nst / 2 + 0.01, 0.3, M_RUBBLE)
    pg.box(V(mid_x, z, h_ + 0.48), (1, 0), (0, 1), 0.82, (z1s - z0s) / nst / 2 + 0.01, 0.04, M_TRENC)
pg.box(V(mid_x, z1s - 8.0, 7.6 - 0.1), (1, 0), (0, 1), 0.95, 1.6, 0.55, M_RUBBLE)   # the salamander's plinth
sal = V(mid_x, z1s - 8.0, 8.3)                                              # the salamander, 'el drac'
pg.ico(Matrix.Translation(sal) @ Matrix.Diagonal((0.55, 1.2, 0.35, 1)), 1.0, M_TRENC_DRAGON, 2)
pg.ico(Matrix.Translation(sal + Vector((0, 1.25, 0.15))) @ Matrix.Diagonal((0.3, 0.42, 0.24, 1)), 1.0, M_TRENC_DRAGON, 2)
pg.cone(Matrix.Translation(sal + Vector((0, -1.5, 0.0))) @ Matrix.Rotation(math.pi / 2, 4, 'X'), 6, 0.22, 0.02, 1.2, M_TRENC_DRAGON)
for sx in (-1, 1):
    for sy in (-0.6, 0.6):
        pg.cone(Matrix.Translation(sal + Vector((sx * 0.55, sy, -0.2))) @ Matrix.Rotation(sx * 0.9, 4, 'Y'), 5, 0.09, 0.06, 0.5, M_TRENC_DRAGON)
for sx in (x0s - 0.25, x1s + 0.25):                                         # the stair walls
    wedge_wall(pg, sx, z1s, z0s, 5.6, 8.6, 7.0, 9.9, 0.25, M_TRENC)
    solid(sx - 0.28, z0s, sx + 0.28, z1s)
solid(mid_x - 0.95, z0s + 1.0, mid_x + 0.95, z1s - 1.0)

# the Hypostyle Room's colonnade: two rows of Doric columns under the square's edge (its entablature carries the
# wavy bench), the dim hall behind, its doorway
hx0, hz0, hx1, hz1 = G['hypostyle']
cz_ = G['colonnade_z']
hb = 9.0
for k in range(9):
    x = hx0 + 1.4 + k * (hx1 - hx0 - 2.8) / 8
    pg.cone(Matrix.Translation(V(x, cz_, hb + 2.8)), 16, 0.62, 0.5, 5.6, M_WHITE)
    pg.cone(Matrix.Translation(V(x, cz_, hb + 0.4)), 16, 0.72, 0.72, 0.8, M_TRENC_BW)                    # their trencadís feet
    pg.box(V(x, cz_, hb + 5.75), (1, 0), (0, 1), 0.75, 0.75, 0.15, M_WHITE)
    solid(x - 0.5, cz_ - 0.5, x + 0.5, cz_ + 0.5)
for k in range(8):                                                          # the second row, in the shade
    x = hx0 + 2.6 + k * (hx1 - hx0 - 5.2) / 7
    pg.cone(Matrix.Translation(V(x, cz_ - 2.3, hb + 2.8)), 12, 0.55, 0.45, 5.6, mat('ColumnShade', '#d8d1c4', 0.9))
    solid(x - 0.45, cz_ - 2.75, x + 0.45, cz_ - 1.85)
pg.box(V((hx0 + hx1) / 2, cz_, hb + 6.15), (1, 0), (0, 1), (hx1 - hx0) / 2, 0.85, 0.25, M_WHITE)           # the entablature
pg.box(V((hx0 + hx1) / 2, (cz_ + G['square_r'][3]) / 2 - 0.3, hb + 6.2), (1, 0), (0, 1), (hx1 - hx0) / 2,
       (cz_ - G['square_r'][3]) / 2 + 0.5, 0.18, mat('HypostyleCeil', '#efe9de', 0.9))                    # the square's edge over them
pg.box(V((hx0 + hx1) / 2, hz1 + 0.05, hb + 3.0), (1, 0), (0, 1), (hx1 - hx0) / 2, 0.1, 3.0, mat('HypostyleShade', '#5e5649', 0.95))   # the hall's front
# (round 33: a flat panel; now the hall's door, arched, in a white surround, and the glow on it)
door_unit(pg, V((hx0 + hx1) / 2, hz1 + 0.15, hb), (1, 0), (0, -1), 2.4, 3.0, 1.2, M_WOOD_DOOR, M_WHITE, fw=0.2, depth=0.26)
for sx in (hx0, hx1):                                                       # its ends, closing the porch at the sides
    pg.box(V(sx, (cz_ + hz1) / 2, hb + 3.0), (1, 0), (0, 1), 0.3, (cz_ - hz1) / 2 + 0.5, 3.1, M_RUBBLE)
    solid(sx - 0.35, hz1, sx + 0.35, cz_ + 0.5)
# (round 35, the everything-visit: the whole hall was solid, and solids stand at every height — it walled off the
# square's southern 8 m above it, the wavy bench and Fiona by it out of reach; only its front wall now, the hall itself
# being the room behind the door)
solid(hx0, hz1 - 0.3, hx1, hz1 + 0.3)
# (round 35, the everything-visit: it stood behind the inner row of columns, and the plaque's reading place by the door
# was behind one — she could reach neither; on the porch now, just east of the dragon stairs' top, where the plaque
# is read too)
HYPO_SIGN = (111.2, cz_ + 1.7)
post_sign(HYPO_SIGN[0], HYPO_SIGN[1], 0.0, 1.0, 'SALA HIPÒSTILA')
door('hypostyle', 'the Hypostyle Room', 'int_hypostyle', (hx0 + hx1) / 2, hz1 + 0.6, 0.0, 1.0, 2.4, h=3.0, arch=1.2, base=hb,
     glow=((hx0 + hx1) / 2, hz1 + 0.25), plaque_pos=[HYPO_SIGN[0], HYPO_SIGN[1] + 0.6], plaque=
     "SALA HIPÒSTILA. Eighty-six Doric columns, meant to shelter a market for the estate that was never built; "
     "Josep Maria Jujol set the trencadís suns in its ceiling.")

# the Nature Square: sandy, the wavy bench of trencadís all along its open edge (it is also its parapet)
sx0, sz0, sx1, sz1 = G['square_r']
sqh = G['square_h']
pg.face([V(sx0, sz0, sqh + 0.04), V(sx1, sz0, sqh + 0.04), V(sx1, sz1, sqh + 0.04), V(sx0, sz1, sqh + 0.04)], M_SAND_SQ, normal=(0, 0, 1),
        uvs=[(sx0 / 2.5, sz0 / 2.5), (sx1 / 2.5, sz0 / 2.5), (sx1 / 2.5, sz1 / 2.5), (sx0 / 2.5, sz1 / 2.5)])
bench_pts = []
x = sx0
while x <= sx1 + 0.01:
    t = (x - sx0) / (sx1 - sx0)
    bench_pts.append((x, sz1 - 0.3 - 1.25 * abs(math.sin(t * math.pi * 7.0))))
    x += 0.7
for a, b in zip(bench_pts, bench_pts[1:]):
    d = Vector((b[0] - a[0], b[1] - a[1]))
    nn_ = Vector((-d.y, d.x)).normalized()
    for off, h0, h1, mm in ((0.0, 0.0, 0.45, M_TRENC), (0.3, 0.45, 0.95, M_TRENC)):
        pg.face([V(a[0] + nn_.x * off, a[1] + nn_.y * off, sqh + h0), V(b[0] + nn_.x * off, b[1] + nn_.y * off, sqh + h0),
                 V(b[0] + nn_.x * off, b[1] + nn_.y * off, sqh + h1), V(a[0] + nn_.x * off, a[1] + nn_.y * off, sqh + h1)], mm)
    pg.face([V(a[0], a[1], sqh + 0.45), V(b[0], b[1], sqh + 0.45), V(b[0] + nn_.x * 0.3, b[1] + nn_.y * 0.3, sqh + 0.45),
             V(a[0] + nn_.x * 0.3, a[1] + nn_.y * 0.3, sqh + 0.45)], M_TRENC, normal=(0, 0, 1))
    # the back of the bench, down to the terrace edge, so nothing opens over the hill
    pg.face([V(b[0] + nn_.x * 0.3, b[1] + nn_.y * 0.3, sqh + 0.95), V(a[0] + nn_.x * 0.3, a[1] + nn_.y * 0.3, sqh + 0.95),
             V(a[0], sz1 + 0.02, sqh + 0.95), V(b[0], sz1 + 0.02, sqh + 0.95)], M_TRENC, normal=(0, 0, 1))
    # (round 27, the user: "an invisible wall in the terrace") the solid follows the bench itself, every segment
    scene.setdefault('solids', []).append([[round(a[0], 2), round(a[1], 2)], [round(b[0], 2), round(b[1], 2)],
                                           [round(b[0], 2), round(sz1 + 0.3, 2)], [round(a[0], 2), round(sz1 + 0.3, 2)]])
# (round 25) its other three sides: a rubble retaining wall from the lawn up, with a low parapet, all round but where
# the side stairs arrive and where the paths come in at its own level (G['square_ways']: no way in at the back)
ways_ = G['square_ways']


def open_at(side, z):
    return any(w_[0] == side and w_[1] <= z <= w_[2] for w_ in ways_)


for side, sx in (('w', sx0), ('e', sx1)):
    z = sz1
    while z > sz0 + 0.01:
        z2 = max(sz0, z - 1.0)
        zm = (z + z2) / 2
        if not open_at(side, zm):
            out_ = -0.6 if side == 'w' else 0.6
            lo = min(hz(sx + out_, z), hz(sx + out_, z2), hz(sx + out_, zm), sqh) - 0.6
            pg.box(V(sx, zm, (lo + sqh + 0.9) / 2), (1, 0), (0, 1), 0.3, (z - z2) / 2, (sqh + 0.9 - lo) / 2, M_RUBBLE)
            pg.box(V(sx, zm, sqh + 0.93), (1, 0), (0, 1), 0.36, (z - z2) / 2, 0.05, M_TRENC)
            solid(sx - 0.35, z2, sx + 0.35, z)
        z = z2
# (round 34: the back has no wall now — the covered walk's columns stand along it, north.py GALLERY)
# the side stairs: from the porch's ends up to the square, between rubble walls, as in the real park
for (a0, b0, a1, b1) in G['side_stairs']:
    nstp = 22
    bl, b0 = b0, G['stairs_top_z']                                          # (the landing above is level ground)
    for k in range(nstp):
        z_ = b1 - (b1 - b0) * (k + 0.5) / nstp
        h_ = 9.0 + (sqh - 9.0) * (k + 0.5) / nstp
        pg.box(V((a0 + a1) / 2, z_, h_ - 0.6), (1, 0), (0, 1), (a1 - a0) / 2, (b1 - b0) / nstp / 2, 0.6 + 0.04, M_STONE)
    for xw in (a0 - 0.2, a1 + 0.2):
        if sx0 - 0.5 < xw < sx1 + 0.5:
            # (the square's own wall is that side, under the square; in front of it, a wall of the stairs' own)
            # (round 32's play-through: it came right down to the porch's parapet, the lamp stood in the 0.8 m left
            # between them, and nobody could get from the porch onto the stairs, so not up to the square or the upper
            # park at all. It starts 1.5 m up the flight now: the first steps open onto the porch.)
            zz0 = sz1
            hh0 = 9.0 + (sqh - 9.0) * min(1.0, (b1 - zz0) / (b1 - b0))
            zf = b1 - 1.5
            ff = (b1 - zf) / (b1 - zz0)
            wedge_wall(pg, xw, zf, zz0, 8.4 + (hh0 - 0.6 - 8.4) * ff, hh0 - 0.6, 9.9 + (hh0 + 0.9 - 9.9) * ff, hh0 + 0.9, 0.2, M_RUBBLE)
            solid(xw - 0.22, zz0, xw + 0.22, zf)
            continue
        # (round 35, PATH_RULES G2, the user: "this wall needs to go to the ground, it should also cover the stairs") the
        # outer wall in metre lengths, each down into the lower of the ground outside and the steps (was a wedge whose
        # foot ran 0.6 m under the steps, so where the lawn outside lies lower the steps showed under it)
        out_s = -1.0 if xw < a0 else 1.0
        def _st_h(zq_):
            return 9.0 + (sqh - 9.0) * min(1.0, max(0.0, (b1 - zq_) / (b1 - b0)))
        # (round 40, PATH_RULES G5: the whole-park walk check) it runs on to the porch's front parapet: the 0.8 m left at
        # the corner between them was too narrow to pass, but the slope beside it read the steps below as a cliff, and she
        # was slid into the corner and held there
        zk_ = G['porch'][3] - 0.2
        while zk_ > bl + 0.01:
            zk2_ = max(bl, zk_ - 1.0)
            lo_ = min(_st_h(zk_) - 0.6, _st_h(zk2_) - 0.6, min(hz(xw + out_s * 0.4, zq_) for zq_ in (zk_, (zk_ + zk2_) / 2, zk2_)) - 0.4)
            # (its top slopes with the flight, one even line; down into the ground along its whole length)
            wedge_wall(pg, xw, zk_, zk2_, lo_, lo_, _st_h(zk_) + 0.9, _st_h(zk2_) + 0.9, 0.2, M_RUBBLE)
            zk_ = zk2_
        solid(xw - 0.25, bl, xw + 0.25, G['porch'][3] - 0.2)
    pg.box(V((a0 + a1) / 2, bl, sqh + 0.15), (1, 0), (0, 1), (a1 - a0) / 2 + 0.25, 0.25, 0.75, M_RUBBLE)
    solid(a0 - 0.25, bl - 0.25, a1 + 0.25, bl + 0.25)
    pg.face([V(a0, bl, sqh + 0.04), V(a1, bl, sqh + 0.04), V(a1, b0, sqh + 0.04), V(a0, b0, sqh + 0.04)], M_STONE, normal=(0, 0, 1), uvscale=1.0)
    # (round 26) the game walks the steps and the landing at their own heights (engine/main.gd terrain_at, scene 'flats')
    scene.setdefault('flats', []).append([a0, b0, a1, b1, round(sqh + 0.04, 3), 9.0])
    scene['flats'].append([a0, bl, a1, b0, round(sqh + 0.04, 3), round(sqh + 0.04, 3)])
north['park']['steps'] = [list(r) for r in G['side_stairs']] + GR_STEPS
# (round 26, the user fell through the square's sand by its wall, and "the grass covers the stairs") the square, the
# porch, the gate plaza and the dragon stairs are level ground or an even ramp to the game, whatever the height grid
# does at their edges; the porch and the plaza get a paved plane of their own, with a kerb, and the porch's terrace a
# retaining wall along its front either side of the stairs
scene['flats'].append([sx0, sz0, sx1, sz1, round(sqh + 0.04, 3), round(sqh + 0.04, 3)])
scene['flats'].append([x0s, z0s, x1s, z1s, 9.0, 6.0])

def _wall_z(x):
    """(round 34) the park wall's line past the gate plaza's west corner, (92, -145.5) to the gate (106, -141), 0.3 m
    in from its middle: the plaza's paving stops there."""
    return -145.5 + (x - 92.0) * 4.5 / 14.0 - 0.3


for (r_, h_) in ((G['plaza'], 6.0), (G['porch'], 9.0)):
    # (round 34, the user: "how the walls meet the ground… It should look like it would join like in the real world")
    # the plaza's rectangle ran 1.3 m out through the wall west of the gate: its paving and its west kerb poked out on
    # the street side as a white slab at the wall's foot. Its paving now stops at the wall's line.
    zc0_ = _wall_z(r_[0]) if r_ is G['plaza'] else r_[3]
    xc_ = 92.0 + (r_[3] + 0.3 + 145.5) * 14.0 / 4.5 if r_ is G['plaza'] else r_[0]
    quads_ = [[(r_[0], r_[1]), (r_[2], r_[1]), (r_[2], zc0_), (r_[0], zc0_)]]
    if r_ is G['plaza']:
        quads_.append([(r_[0], zc0_), (r_[2], zc0_), (r_[2], r_[3]), (xc_, r_[3])])
    for q_ in quads_:
        pg.face([V(a_, b_, h_ + 0.03) for a_, b_ in q_], M_SAND_SQ, normal=(0, 0, 1), uvs=[(a_ / 2.5, b_ / 2.5) for a_, b_ in q_])
    scene['flats'].append([r_[0], r_[1], r_[2], r_[3], h_ + 0.03, h_ + 0.03])
    for (q0, q1, nrm_) in (((r_[0], r_[1]), (r_[2], r_[1]), (0, -1, 0)), ((r_[2], r_[1]), (r_[2], r_[3]), (1, 0, 0)),
                           ((r_[2], r_[3]), (xc_, r_[3]), (0, 1, 0)), ((r_[0], zc0_), (r_[0], r_[1]), (-1, 0, 0))):
        pg.face([V(q0[0], q0[1], h_ - 0.6), V(q1[0], q1[1], h_ - 0.6), V(q1[0], q1[1], h_ + 0.03), V(q0[0], q0[1], h_ + 0.03)],
                M_STONE, normal=nrm_)                                       # (a skirt: no slit where the lawn dips below it)
    # (round 40, the user at the gate: "then there's a white brick there": the plaza's side kerbs stood inside the two
    # lodges, a stub showing at each; the paths come onto it at both corners (B2): no kerb down the plaza's sides)
    for xk, zk_ in (() if r_ is G['plaza'] else ((r_[0], zc0_), (r_[2], r_[3]))):                 # a stone kerb down its sides
        # (round 35, PATH_RULES B2: no kerb across a path where it comes onto the paving — it lay as a white slab
        # across the west walk and the switchbacks at the plaza's two corners)
        cuts_ = sorted(pz_ for P_ in N.PARK_PATHS for (pa_, pb_) in zip(P_, P_[1:])
                       if (pa_[0] - xk) * (pb_[0] - xk) < 0
                       for pz_ in [pa_[1] + (pb_[1] - pa_[1]) * (xk - pa_[0]) / (pb_[0] - pa_[0])] if r_[1] < pz_ < zk_)
        spans_, z_a = [], r_[1]
        for cz_ in cuts_:
            spans_.append((z_a, cz_ - 1.7))
            z_a = cz_ + 1.7
        spans_.append((z_a, zk_))
        for (za_, zb_) in spans_:
            if zb_ - za_ > 0.3:
                pg.box(V(xk, (za_ + zb_) / 2, h_ + 0.06), (1, 0), (0, 1), 0.12, (zb_ - za_) / 2, 0.12, M_STONE)
pr_ = G['porch']
for (xa_, xb_) in ((pr_[0], x0s - 0.25), (x1s + 0.25, pr_[2])):
    pg.box(V((xa_ + xb_) / 2, pr_[3] + 0.15, 7.4), (1, 0), (0, 1), (xb_ - xa_) / 2, 0.3, 1.85, M_RUBBLE)      # 5.55 .. 9.25
    pg.box(V((xa_ + xb_) / 2, pr_[3] + 0.15, 9.28), (1, 0), (0, 1), (xb_ - xa_) / 2, 0.36, 0.05, M_TRENC)
    solid(xa_, pr_[3] - 0.2, xb_, pr_[3] + 0.5)
north['park']['square'] = [sx0, sz0, sx1, sz1, sqh]

# (round 33, the user: "You have squished things together") the Pòrtic de la Bugadera's arc of twelve leaning columns
# wrapped the square's west way, where the path from the Austria Gardens arrives: taken out; then (the user: "they
# actually represent a curved path") built again as a covered walk on that path, after the viaducts below.

# (round 25) Casa Larrard: Count Güell's own house, by the Larrard gate, now a school (not open to visitors); from Meshy
lr_ = G['larrard_r']
lh_ = G['larrard_h']
if not meshy_house('casa_larrard.glb', lr_, lh_, 'MeshyBuilding_larrard', max_h=13.0):
    pg.box(V((lr_[0] + lr_[2]) / 2, (lr_[1] + lr_[3]) / 2, lh_ + 4.5), (1, 0), (0, 1), (lr_[2] - lr_[0]) / 2, (lr_[3] - lr_[1]) / 2, 4.5, M_CREAM)
    pg.box(V((lr_[0] + lr_[2]) / 2, (lr_[1] + lr_[3]) / 2, lh_ + 9.2), (1, 0), (0, 1), (lr_[2] - lr_[0]) / 2 + 0.3, (lr_[3] - lr_[1]) / 2 + 0.3, 0.2, M_ROOF_TILE)
solid(lr_[0], lr_[1], lr_[2], lr_[3])
cam_building(lr_[0], lr_[1], lr_[2], lr_[3], lh_ - 0.3, lh_ + 9.5)                   # (Casa Larrard)
# (round 40, SIGN_FLOAT: placed for the stand-in's front, it hung 0.35 m out in front of the Meshy house's real wall) on
# the wall itself, found by looking at it from the path
_dgl_ = bpy.context.evaluated_depsgraph_get()
_o_ = V((lr_[0] + lr_[2]) / 2, lr_[3] + 6.0, lh_ + 2.6)
_lz_ = lr_[3] + 0.35
for _k_ in range(12):                                  # (past anything in front: only the house's own wall counts)
    _hl_ = bpy.context.scene.ray_cast(_dgl_, _o_, Vector((0, 1, 0)), distance=9.0)
    if not _hl_[0]:
        break
    if _hl_[4].name.startswith('MeshyBuilding_larrard'):
        _lz_ = -_hl_[1].y + 0.03
        break
    _o_ = _hl_[1] + Vector((0, 0.01, 0))
city_objs.append(text_obj('ESCOLA BALDIRI REIXAC', 0.16, M_SIGN_TEXT, V((lr_[0] + lr_[2]) / 2, _lz_, lh_ + 2.6), 0.0, 'SignText_larrard'))

# (round 25) the Austria Gardens: lawns and beds of flowers in rows, edged with clipped box, benches, young trees round
aus = G['austria']
M_BOX = mat('BoxHedge', '#3f6b34', 0.85)
gard = Cards()
grng2 = random.Random(1912)
AUS_I, AUS_J = 3, 3                                  # (round 33: three beds across, moved west off the side stairs)
for i in range(AUS_I):
    for j in range(AUS_J):
        bx0, bz0 = aus[0] + 3.0 + i * 6.0, aus[1] + 3.5 + j * 7.5
        cxb, czb = bx0 + 2.0, bz0 + 2.5
        # (round 28: each hedge laid on the ground in short lengths, following the lawn's slope — the single
        # straight boxes floated clear of the grass at one end and sank at the other, a grid of frames from above)
        for (ex_, ez_, hw_, hd_) in ((cxb, bz0, 2.1, 0.12), (cxb, bz0 + 5.0, 2.1, 0.12), (bx0, czb, 0.12, 2.6), (bx0 + 4.0, czb, 0.12, 2.6)):
            segs_ = 4
            for ks_ in range(segs_):
                if hw_ > hd_:
                    mx_ = ex_ - hw_ + hw_ * (2 * ks_ + 1) / segs_
                    pg.box(V(mx_, ez_, gz(mx_, ez_) + 0.1), (1, 0), (0, 1), hw_ / segs_ + 0.03, hd_, 0.3, M_BOX)
                else:
                    mz_ = ez_ - hd_ + hd_ * (2 * ks_ + 1) / segs_
                    pg.box(V(ex_, mz_, gz(ex_, mz_) + 0.1), (1, 0), (0, 1), hw_, hd_ / segs_ + 0.03, 0.3, M_BOX)
        # (round 35, the user: "The austrian gardens are not solid") each bed, its box hedge round it, is solid: she
        # walks the gravel walks between them, as a visitor does
        solid(bx0 - 0.12, bz0 - 0.12, bx0 + 4.12, bz0 + 5.12)
        fm_ = M_FLOWERS[(i + j) % len(M_FLOWERS)]
        for k in range(110):                         # (round 33: beds full of flowers, not lawn with a few)
            fx, fz = grng2.uniform(bx0 + 0.3, bx0 + 3.7), grng2.uniform(bz0 + 0.3, bz0 + 4.7)
            c = V(fx, fz, gz(fx, fz) + 0.2)
            a0 = grng2.uniform(0, 3.14)
            for jj in range(3):
                rot = vertical(a0 + jj * 1.0472)
                gard.card(c, 0.32, rot, c - Vector((0, 0, 0.32)), fm_, 0.35)
for (bxb, bzb) in ((aus[0] + 11.0, aus[3] - 0.4), (aus[0] + 11.0, aus[1] + 1.1)):          # (on the outer walks' far side)
    hb_ = gz(bxb, bzb)
    pg.box(V(bxb, bzb, hb_ + 0.45), (1, 0), (0, 1), 0.8, 0.2, 0.03, M_BENCHWOOD if 'M_BENCHWOOD' in globals() else M_FBARK)
    pg.box(V(bxb, bzb, hb_ + 0.22), (1, 0), (0, 1), 0.7, 0.15, 0.22, M_RUBBLE)
    solid(bxb - 0.8, bzb - 0.25, bxb + 0.8, bzb + 0.25)
city_objs.append(gard.finish('Grass_austria'))
# (round 33, the user: the park's layout and landscaping — "Look at it from a birds eye view") the beds lay loose on the
# lawn like frames; a formal garden has its walks: gravel all round the beds and between them, meeting the paths
_ax = [aus[0] + 2.0 + i * 6.0 for i in range(AUS_I + 1)]             # between the bed columns and round them
_az = [aus[1] + 2.25 + j * 7.5 for j in range(AUS_J + 1)]
_aw = [[(x_, _az[0]), (x_, _az[-1])] for x_ in _ax] + [[(_ax[0], z_), (_ax[-1], z_)] for z_ in _az]
# (round 40: the north walk out to the path up from Larrard is laid with the park's paths (ParkPaths), so its join
# with that path is rounded like the others)
city_objs.append(build_ribbons([{'pts': dense(w_, 1.0), 'w': 1.6} for w_ in _aw], 'G', gz_top, 'AustriaWalks'))
north['park']['austria'] = list(aus)


# the Casa Museu Gaudí: pink, a slender spire with a cross, green shutters
mx_, mz_ = G['museu']
mh = G['museu_h']
MESHY_MUSEU = meshy_house('casa_museu_gaudi.glb', (mx_ - 6.2, mz_ - 5.4, mx_ + 6.2, mz_ + 5.4), mh, 'MeshyBuilding_museu', max_h=21.0)
if not MESHY_MUSEU:      # (the stand-in: the round 22 house)
    pg.box(V(mx_, mz_, mh + 3.6), (1, 0), (0, 1), 5.0, 4.4, 3.6, M_PINK)
    pg.face([V(mx_ - 5.2, mz_ + 4.6, mh + 7.2), V(mx_ + 5.2, mz_ + 4.6, mh + 7.2), V(mx_ + 5.2, mz_, mh + 9.4), V(mx_ - 5.2, mz_, mh + 9.4)], M_ROOF_TILE, normal=(0, -1, 1))
    pg.face([V(mx_ - 5.2, mz_ - 4.6, mh + 7.2), V(mx_ + 5.2, mz_ - 4.6, mh + 7.2), V(mx_ + 5.2, mz_, mh + 9.4), V(mx_ - 5.2, mz_, mh + 9.4)], M_ROOF_TILE, normal=(0, 1, 1))
    pg.cone(Matrix.Translation(V(mx_ - 3.0, mz_ + 2.2, mh + 8.5)), 12, 0.95, 0.75, 3.0, M_PINK)
    pg.cone(Matrix.Translation(V(mx_ - 3.0, mz_ + 2.2, mh + 13.0)), 12, 0.8, 0.05, 6.0, M_TRENC)
    pg.box(V(mx_ - 3.0, mz_ + 2.2, mh + 16.3), (1, 0), (0, 1), 0.06, 0.06, 0.4, M_IRON)
    pg.box(V(mx_ - 3.0, mz_ + 2.2, mh + 16.45), (1, 0), (0, 1), 0.25, 0.05, 0.05, M_IRON)
    for fl in (0, 1):
        for sx in (-3.0, 0.0, 3.0):
            if fl == 0 and sx == 0.0:
                continue
            pg.box(V(mx_ + sx, mz_ + 4.42, mh + 1.7 + fl * 3.3), (1, 0), (0, 1), 0.5, 0.03, 0.8, M_GLASS)
            for sd in (-1, 1):
                pg.box(V(mx_ + sx + sd * 0.68, mz_ + 4.44, mh + 1.7 + fl * 3.3), (1, 0), (0, 1), 0.18, 0.03, 0.82, M_SHUT_GREEN)
    pg.box(V(mx_, mz_ + 4.43, mh + 1.2), (1, 0), (0, 1), 0.7, 0.04, 1.2, M_WOOD_DOOR)
solid(mx_ - 6.2, mz_ - 5.4, mx_ + 6.2, mz_ + 5.4)
cam_building(mx_ - 6.2, mz_ - 5.4, mx_ + 6.2, mz_ + 5.4, mh - 0.3, mh + 10.0)        # (the Casa Museu Gaudí)
# (round 33: the glow stood on the wall left of the house's real door: measured off a straight-on picture of the Meshy
# house, its arched French door is 1.15 m east of the middle, 1.05 m wide, its sill at 13.1 m, 2.1 m high)
post_sign(mx_ + 2.9, mz_ + 6.9, 0.0, 1.0, 'CASA MUSEU GAUDÍ', 'obert · open')
door('casa_museu', 'Casa Museu Gaudí', 'int_gaudi_house', mx_ + 1.15, mz_ + 5.9, 0.0, 1.0, 1.05, h=2.1, arch=0.52, base=13.1,
     plaque=
     "CASA MUSEU GAUDÍ. The show house of the estate, by Francesc Berenguer, 1904. Gaudí bought it and lived here from 1906 to 1925, "
     "with his father and his niece. Now a museum of his furniture.")

# Casa Trias: a plain cream villa (Juli Batllevell, 1905), here the park's offices and stores
tx_, tz_ = G['trias']
th_ = G['trias_h']
if not meshy_house('casa_trias.glb', (tx_ - 5.6, tz_ - 4.6, tx_ + 5.6, tz_ + 4.6), th_, 'MeshyBuilding_trias', max_h=12.0):
    pg.box(V(tx_, tz_, th_ + 3.3), (1, 0), (0, 1), 5.6, 4.6, 3.3, M_CREAM)
    pg.box(V(tx_, tz_, th_ + 6.75), (1, 0), (0, 1), 5.9, 4.9, 0.15, M_ROOF_TILE)
    pg.face([V(tx_ - 5.9, tz_ + 4.9, th_ + 6.9), V(tx_ + 5.9, tz_ + 4.9, th_ + 6.9), V(tx_, tz_, th_ + 9.2)], M_ROOF_TILE, normal=(0, -1, 1))
    pg.face([V(tx_ - 5.9, tz_ - 4.9, th_ + 6.9), V(tx_ + 5.9, tz_ - 4.9, th_ + 6.9), V(tx_, tz_, th_ + 9.2)], M_ROOF_TILE, normal=(0, 1, 1))
    pg.face([V(tx_ - 5.9, tz_ + 4.9, th_ + 6.9), V(tx_ - 5.9, tz_ - 4.9, th_ + 6.9), V(tx_, tz_, th_ + 9.2)], M_ROOF_TILE, normal=(-1, 0, 1))
    pg.face([V(tx_ + 5.9, tz_ + 4.9, th_ + 6.9), V(tx_ + 5.9, tz_ - 4.9, th_ + 6.9), V(tx_, tz_, th_ + 9.2)], M_ROOF_TILE, normal=(1, 0, 1))
    for fl in (0, 1):
        for sx in (-3.4, 3.4):
            pg.box(V(tx_ + sx, tz_ + 4.62, th_ + 1.7 + fl * 3.1), (1, 0), (0, 1), 0.5, 0.03, 0.8, M_GLASS)
            for sd in (-1, 1):
                pg.box(V(tx_ + sx + sd * 0.68, tz_ + 4.64, th_ + 1.7 + fl * 3.1), (1, 0), (0, 1), 0.18, 0.03, 0.82, M_SHUT_BROWN)
    pg.box(V(tx_, tz_ + 4.63, th_ + 1.2), (1, 0), (0, 1), 0.7, 0.04, 1.2, M_WOOD_DOOR)
# (round 33, the user: "she should be able to go into the portico of the building that has the cellar, with a sign at
# the entrance") the house's loggia, measured off the Meshy model itself (rays at a standing body's height): its floor,
# its back wall, its front edge; the house solid behind it and at its ends, a low wall along its balustrade, open at
# its steps; the game walks its floor and its steps at their own heights ('flats')
bpy.context.view_layer.update()
_dgt = bpy.context.evaluated_depsgraph_get()


def _ray(o_, d_, far=12.0):
    hit_, loc_, _n, _i, ob_, _m = bpy.context.scene.ray_cast(_dgt, o_, d_, distance=far)
    return loc_ if hit_ else None


_backs = []
for _k in range(17):
    _x = tx_ - 4.4 + _k * 0.4
    _l = _ray(V(_x, tz_ + 9.0, th_ + 1.9), Vector((0, 1, 0)), 14.0)
    if _l is not None and -_l.y < tz_ + 4.4:
        _backs.append(-_l.y)
_lf = _ray(V(tx_, tz_ + 9.0, th_ + 0.5), Vector((0, 1, 0)), 14.0)
TR_FRONT = -_lf.y if _lf is not None else tz_ + 3.75                 # (the plinth's face)
# (the loggia's back wall: the rays' middle value — through the door's or a window's glass one runs on into the house)
TR_BACK = sorted(_backs)[len(_backs) // 2] if _backs else TR_FRONT - 1.8
TR_BACK = max(TR_BACK, TR_FRONT - 7.0)        # (round 39: the loggia is the whole ground floor, back wall at -228.97)
_lfl = _ray(V(tx_ - 2.4, (TR_BACK + TR_FRONT) / 2, th_ + 1.9), Vector((0, 0, -1)), 3.0)
TR_FLOOR = _lfl.z if _lfl is not None else th_ + 1.0
TR_X0, TR_X1 = tx_ - 4.05, tx_ + 3.95                               # (round 39: its inside walls' faces, the oculus's bay is open inside)
TR_FACE = tz_ + 3.45                                                # (round 39: the plinth's face, -222.55; TR_FRONT hit the steps' riser)
TR_STEP = (tx_ - 0.9, tx_ + 1.1)
print('PARK Casa Trias loggia: front %.2f back %.2f floor %.2f (rays %s)' % (TR_FRONT, TR_BACK, TR_FLOOR, ' '.join('%.2f' % b_ for b_ in _backs)))
solid(tx_ - 5.6, tz_ - 4.6, tx_ + 5.6, TR_BACK + 0.12)                # the back wall (shutters stand ~0.1 proud)
solid(tx_ - 5.6, TR_BACK + 0.12, TR_X0, tz_ + 4.6)                    # its west wall
solid(TR_X1, TR_BACK + 0.12, tx_ + 5.6, tz_ + 4.6)                    # its east wall
solid(tx_ + 2.25, TR_FACE - 0.6, TR_X1, tz_ + 4.6)                    # the oculus bay's front wall
# (round 39, the user: "These should be solid. She should not be able to walk through them.") the balustrade on its
# own line, from the plinth's face 0.6 m in, open between the two columns either side of the steps; those two round
solid(TR_X0, TR_FACE - 0.6, tx_ - 1.05, TR_FACE)
solid(tx_ + 0.95, TR_FACE - 0.6, tx_ + 2.25, TR_FACE)
for r_ in ((tx_ - 5.6, tz_ - 4.6, tx_ + 5.6, TR_BACK + 0.12), (tx_ - 5.6, TR_BACK + 0.12, TR_X0, tz_ + 4.6),
           (TR_X1, TR_BACK + 0.12, tx_ + 5.6, tz_ + 4.6), (tx_ + 2.25, TR_FACE - 0.6, TR_X1, tz_ + 4.6)):
    cam_building(*r_, th_ - 0.3, th_ + 9.0)                                             # (Casa Trias: its walls, not the loggia)
for cx_ in (tx_ - 0.85, tx_ + 0.75):
    scene['obstacles'].append({'pos': [round(cx_, 2), round(TR_FACE - 0.35, 2)], 'off': [0, 0], 'r': 0.3})   # (main.gd: a 0.225 m post)
scene.setdefault('flats', []).append([TR_X0, TR_BACK, TR_X1, TR_FACE, round(TR_FLOOR + 0.02, 3), round(TR_FLOOR + 0.02, 3)])
scene['flats'].append([tx_ - 1.05, TR_FACE, tx_ + 1.0, TR_FACE + 0.75, round(TR_FLOOR + 0.02, 3), round(th_ + 0.02, 3)])   # (the steps as the model has them)
TR_STEPS_R = [round(tx_ - 1.05, 2), round(TR_FACE - 0.3, 2), round(tx_ + 1.0, 2), round(TR_FACE + 0.75, 2)]
# (round 39) a first-person place: in here the camera goes to her eyes (main.gd fp_rects)
scene.setdefault('first_person', []).append([round(TR_X0, 2), round(TR_BACK + 0.12, 2), round(TR_X1, 2), round(TR_FACE, 2), round(TR_FLOOR + 0.02, 3)])
north['park']['steps'].append(TR_STEPS_R)                             # (stairs: not held to the slope rule)
# its sign at the foot of the steps: a board on a post, as the park's fingerposts
post_sign(TR_STEP[1] + 1.5, TR_FRONT + 0.55, 0.0, 1.0, 'CASA TRIAS', 'el pòrtic · obert')   # (round 35, F12: east of the steps, by the house)

# (round 33, the user: "make the basement be two wooden doors on the ground and make the glow match their angle… so
# they slope up. Put them on the side with no path to them") the cellar's way in: a pair of sloping wooden doors against
# the house's west side (no path comes there), in a low stone curb, planked, with iron rings and strap hinges; the
# glow lies on them, at their slope. The old low door in the front's plinth is gone.
_lw = _ray(V(tx_ - 9.0, tz_, th_ + 0.4), Vector((1, 0, 0)), 9.0)
CW_X = _lw.x if _lw is not None else tx_ - 5.0                       # (the plinth's west face)
CW_Z, CW_W, CW_L = tz_ + 0.6, 1.7, 1.3                                # (middle, width along the wall, how far out)
_cg = max(hz(CW_X - CW_L, CW_Z - 1.0), hz(CW_X - CW_L, CW_Z + 1.0))
CW_HI, CW_LO = _cg + 0.85, _cg + 0.22                                 # (top at the wall, foot at the curb)
M_CELLAR_WOOD = mat('CellarDoorWood', '#7a5434', 0.85)
M_CELLAR_GAP = mat('CellarDoorGap', '#2a2018', 0.95)


CW_N = Vector((-(CW_HI - CW_LO), CW_L)).normalized()                  # (their face's normal: out (engine x), up)


def _cp(s_, t_, up_=0.0):
    """On the doors: s_ across (along the wall, metres from the middle), t_ down the slope (0 at the wall, 1 at the
    curb), up_ off their face."""
    return V(CW_X - CW_L * t_ + CW_N.x * up_, CW_Z + s_, CW_HI + (CW_LO - CW_HI) * t_ + CW_N.y * up_)


# the curb: two stone cheeks (wedges) and a sill along the foot
for sd_ in (-1, 1):
    zc_ = CW_Z + sd_ * (CW_W / 2 + 0.12)
    for (zz_, nzz_) in ((zc_ - 0.12, -1), (zc_ + 0.12, 1)):
        pg.face([V(CW_X, zz_, _cg - 0.1), V(CW_X - CW_L - 0.1, zz_, _cg - 0.1), V(CW_X - CW_L - 0.1, zz_, CW_LO + 0.06),
                 V(CW_X, zz_, CW_HI + 0.06)], M_RUBBLE, normal=(0, -nzz_, 0))
    pg.face([V(CW_X, zc_ - 0.12, CW_HI + 0.06), V(CW_X - CW_L - 0.1, zc_ - 0.12, CW_LO + 0.06),
             V(CW_X - CW_L - 0.1, zc_ + 0.12, CW_LO + 0.06), V(CW_X, zc_ + 0.12, CW_HI + 0.06)], M_RUBBLE, normal=(-0.5, 0, 1))
    pg.face([V(CW_X - CW_L - 0.1, zc_ - 0.12, _cg - 0.1), V(CW_X - CW_L - 0.1, zc_ + 0.12, _cg - 0.1),
             V(CW_X - CW_L - 0.1, zc_ + 0.12, CW_LO + 0.06), V(CW_X - CW_L - 0.1, zc_ - 0.12, CW_LO + 0.06)], M_RUBBLE, normal=(-1, 0, 0))
pg.box(V(CW_X - CW_L - 0.05, CW_Z, (_cg - 0.1 + CW_LO) / 2), (0, 1), (1, 0), CW_W / 2 + 0.24, 0.1, (CW_LO - _cg + 0.1) / 2, M_RUBBLE)
pg.box(V(CW_X - 0.08, CW_Z, CW_HI + 0.12), (0, 1), (1, 0), CW_W / 2 + 0.24, 0.12, 0.08, M_RUBBLE)          # the header on the wall
# the doors: a dark underlay, then the planks of each leaf running down the slope, two battens across, the seam
pg.face([_cp(-CW_W / 2, 0, 0.01), _cp(-CW_W / 2, 1, 0.01), _cp(CW_W / 2, 1, 0.01), _cp(CW_W / 2, 0, 0.01)], M_CELLAR_GAP, normal=(-0.5, 0, 1))
_np = 5
for lf_ in (-1, 1):
    for k_ in range(_np):
        s0_ = lf_ * (0.02 + (CW_W / 2 - 0.02) * k_ / _np)
        s1_ = lf_ * (0.02 + (CW_W / 2 - 0.02) * (k_ + 1) / _np - 0.012)
        a_, b_ = min(s0_, s1_), max(s0_, s1_)
        pg.face([_cp(a_, 0.02, 0.035), _cp(a_, 0.98, 0.035), _cp(b_, 0.98, 0.035), _cp(b_, 0.02, 0.035)], M_CELLAR_WOOD, normal=(-0.5, 0, 1))
    for t_ in (0.18, 0.78):                                              # battens
        a_, b_ = sorted((lf_ * 0.06, lf_ * (CW_W / 2 - 0.06)))
        pg.face([_cp(a_, t_ - 0.04, 0.055), _cp(a_, t_ + 0.04, 0.055), _cp(b_, t_ + 0.04, 0.055), _cp(b_, t_ - 0.04, 0.055)], M_CELLAR_WOOD, normal=(-0.5, 0, 1))
    for t_ in (0.12, 0.88):                                              # strap hinges at the outer edges
        a_, b_ = sorted((lf_ * (CW_W / 2 - 0.45), lf_ * (CW_W / 2 - 0.03)))
        pg.face([_cp(a_, t_ - 0.02, 0.06), _cp(a_, t_ + 0.02, 0.06), _cp(b_, t_ + 0.02, 0.06), _cp(b_, t_ - 0.02, 0.06)], M_IRON, normal=(-0.5, 0, 1))
    pg.ico(Matrix.Translation(_cp(lf_ * 0.12, 0.55, 0.08)) @ Matrix.Diagonal((0.07, 0.07, 0.03, 1)), 1.0, M_IRON, 1)   # its ring
solid(CW_X - CW_L - 0.15, CW_Z - CW_W / 2 - 0.25, CW_X, CW_Z + CW_W / 2 + 0.25)
# (round 34, the user: "There should be no sign at the trap door")
# (round 35, PATH_RULES F11, the user: "a part of the grass that gets walked over, but not too often, so it gets worn
# down without making a big trail. Also make it curve around a little bit at the cellar door so it approaches it from
# front on") worn grass: a band a little paler and thinner than the lawn, earth just showing here and there, its edges
# fading into the lawn and fainter in places along it; from the portico's gravel, along the front, round the west
# corner, swinging out so its last metres come straight at the doors
CELLAR_TRACK = [(TR_STEP[0] + 0.5, TR_FRONT + 2.4), (TR_STEP[0] - 0.4, TR_FRONT + 2.0),   # (from under the gravel's edge)
                (TR_STEP[0] - 2.6, TR_FRONT + 2.2), (CW_X - 1.2, TR_FRONT + 1.8),
                (CW_X - 2.4, TR_FRONT + 0.3), (CW_X - 3.1, CW_Z + 1.2), (CW_X - 2.6, CW_Z + 0.1), (CW_X - CW_L - 0.35, CW_Z)]


def _worn_grass_image():
    H, W = 64, 512                                       # v across (0..1 edge to edge), u along (6 m)
    v = (np.arange(H) + 0.5)[:, None] / H * np.ones((1, W))
    n1, n2, n3 = _noise((H, W), 61, 22), _noise((H, W), 62, 6), _noise((1, W), 63, 70)[0][None, :] * np.ones((H, 1))
    grain = np.random.default_rng(64).normal(0, 1, (H, W))
    base = np.array([0.53, 0.55, 0.37])                  # (the lawn's green, paler and yellower where trodden)
    col = base[None, None, :] * (1 + 0.06 * (n1 - 0.5) + 0.05 * (n2 - 0.5) + 0.04 * grain)[:, :, None]
    earth = _specks((H, W), 65, 0.05, 2) & (n2 > 0.55) & (np.abs(v - 0.5) < 0.22)
    col[earth] = np.array([0.55, 0.47, 0.35]) * (1 + 0.05 * grain[earth])[:, None]
    blades = _specks((H, W), 66, 0.10)
    col[blades] *= np.array([0.86, 0.95, 0.80])          # (blades of grass still standing in it)
    mid = np.abs(v - 0.5) * 2                            # 0 in the middle, 1 at the edges
    edge = 0.62 + 0.25 * (n2 - 0.5) + 0.15 * (n1 - 0.5)  # (a ragged, soft edge)
    a = np.clip((edge - mid) / 0.3, 0, 1) * (0.7 + 0.3 * np.clip((n3 - 0.25) / 0.4, 0, 1))   # (fainter in places)
    # (round 35, the user: "a bit more patchy instead") worn patches, whole lawn between them
    patch = 0.65 * _noise((H, W), 67, 30) + 0.35 * _noise((H, W), 68, 11)
    a = a * np.clip((patch - 0.40) / 0.1, 0, 1)
    return _to_image('worn_grass', col, a)


M_WORNGRASS = mat('WornGrass', '#ffffff', 0.98, image=_worn_grass_image(), alpha=True)
_wmb = MB(uv=True)
_wrows = path_rows(N.catmull(CELLAR_TRACK, 6), 1.05, 1905)
_strip(_wmb, _wrows, [lambda hw: -0.55, lambda hw: 0.0, lambda hw: 0.55], gz_top, 0.025, M_WORNGRASS, 6.0, [0.0, 0.5, 1.0])
city_objs.append(_wmb.finish('CellarWornGrass'))
north['park']['cellar_trail'] = [[round(a, 2), round(b, 2)] for a, b in CELLAR_TRACK]
_slope = math.hypot(CW_L, CW_HI - CW_LO)
_gc = _cp(0.0, 0.5, 0.075)
door('trias_soterrani', 'Casa Trias — el soterrani', 'int_trias_cellar', CW_X - CW_L - 0.15, CW_Z, -1.0, 0.0, CW_W,
     h=round(_slope, 3), base=round(CW_LO, 3), glow_c=[round(_gc.x, 3), round(_gc.z, 3), round(-_gc.y, 3)],
     lean=round(math.atan2(CW_L, CW_HI - CW_LO), 4),
     plaque="CASA TRIAS. Built in 1905 by Juli Batllevell for the lawyer Martí Trias, one of only two houses ever sold on the estate. "
     "Today the park's offices and stores. The sloping doors at its side go down to the gardeners' cellar.", lock='cellar_key')
# (round 35, PATH_RULES F13, the user: "remove the random brick wall and the fence that is doing nothing outside that
# building"): the lookout's iron railing (beside gentle ground) and its stone bench are gone

# (round 24) the park's sandy paths (north.py PARK_PATHS), worn like the woods' but pale sauló
PJ_ = []                                                        # (round 25) where one path meets another
for i_, P_ in enumerate(N.PARK_PATHS):
    for e_ in (P_[0], P_[-1]):
        if any(min(math.hypot(e_[0] - q[0], e_[1] - q[1]) for q in dense(Q_, 1.0)) < 1.6
               for j_, Q_ in enumerate(N.PARK_PATHS) if j_ != i_):
            PJ_.append(e_)
# (round 35, PATH_RULES F9, the user: "make the paths in the garden gravel, not dirt") gravel, as the wood's walks


def park_ribbon_z(x, z):
    """(round 40, PATH_RULES B1/B2, the user at the gate plaza: "the gravel path goes on top of it when it would have to
    go underneath the paving") a park path's ribbon on its ground, but over its last 1.5 m before a paved floor it eases
    down so its top meets the paving's top at the edge; under the paving it runs on 5 cm below it."""
    h = gz_top(x, z)
    for r_, ph_ in ((G['plaza'], 6.03), (G['porch'], 9.03), (G['square_r'], G['square_h'] + 0.04)):
        # (round 39, the pictures: eased down outside the paving it sank under its own grass, a green strip between the
        # plaza and the gravel) under the paving it runs on below it; outside, it lies on its ground as everywhere
        if N.rect_d(x, z, r_) == 0.0:
            h = min(h, ph_ - 0.095)
    return h


PJ_.append((82.0, _az[-1]))                     # (round 40: the Austria north walk's T onto the path up from Larrard)
city_objs.append(build_ribbons([{'pts': dense(P_), 'w': 3.0} for P_ in N.PARK_PATHS] +
                               [{'pts': dense([(_ax[-1], _az[-1]), (82.0, _az[-1])], 1.0), 'w': 1.6}],
                               'G', park_ribbon_z, 'ParkPaths', junctions=PJ_))
north['park']['paths'] = [[list(p) for p in P_] for P_ in N.PARK_PATHS] + [[list(p) for p in N.GALLERY['line']]]   # (round 34: and the covered walk's lower walk)
# (round 29: the road's tan ribbon began inside the gate forecourt, its raised edge lying across the paving
# slabs; the drawn ribbon now starts where the paving ends — CARMEL_ROAD itself, and the grading along it, unchanged)
north['park']['road'] = [list(p) for p in N.CARMEL_ROAD]
# (round 33: they stopped short of the gates, a strip of grass between: now through the gateways to the paths inside)
# (round 34, the walk round: laid apart from the road, the gate paths' grassy edges lay across the road's gravel where
# they met it — a green patch on the road outside the Glòria gate. Laid with the road now, meeting it at junctions.)
# (round 36, H6.4, the user: "the gravel path shouldn't come as far": it starts on the line where the town ends,
# x 128.7, over the ends of the wall's and the wood's footpaths, never over the cobbles)
# (round 39, the user: "The gravel should go under the footpath when it joins it": it starts under the wood-side
# footpath's east kerb now — the ribbon's square end, slanted 13° across the road, lies wholly under the paving,
# x 129.3..130.4 — and the footpath stays on top, kerbed (fp_h))
_rx0 = N.GRACIA_FOOT_X[1] - 0.7
_rz0 = N.CARMEL_ROAD[0][1] + (N.CARMEL_ROAD[1][1] - N.CARMEL_ROAD[0][1]) * (_rx0 - N.CARMEL_ROAD[0][0]) / \
    (N.CARMEL_ROAD[1][0] - N.CARMEL_ROAD[0][0])
_road_pts = [(_rx0, _rz0)] + [p_ for p_ in dense(N.CARMEL_ROAD) if p_[0] > N.GRACIA_FOOT_X[1] - 0.1 and p_[1] > -228.6]
city_objs.append(build_ribbons([{'pts': _road_pts, 'w': N.ROAD_W / 0.85},
                                {'pts': dense([(178.6, -188.3), (180.8, -188.3), (183.6, -186.2), (185.8, -183.0)], 0.8), 'w': 2.6},
                                {'pts': dense([(170.2, -226.4), (172.0, -227.3), (174.5, -227.6), (176.6, -228.1)], 0.8), 'w': 2.6}],
                               'G', gz_top, 'CarmelRoad', junctions=[(185.8, -183.0), (176.6, -228.1)]))

# the new covered walk (as the Pòrtic de la Bugadera, its twin in spirit): leaning columns of rough stone either side
# of the path, a rubble vault over it, stone planters of agaves along its top; she walks through it
M_AGAVE = mat('Agave', '#7fa598', 0.7)
M_AGAVE_D = mat('AgaveDark', '#5f857a', 0.75)


def agave(mb, x, z, h0, s=1.0, rng=None):
    """A rosette of thick, pointed, blue-green leaves."""
    rng = rng or nr
    n_ = rng.randint(11, 15)
    for k in range(n_):
        a = 2 * math.pi * k / n_ + rng.uniform(-0.15, 0.15)
        up = rng.uniform(0.35, 1.15)
        L = rng.uniform(0.55, 0.85) * s
        d = Vector((math.cos(a) * math.cos(up), -math.sin(a) * math.cos(up), math.sin(up)))
        base = V(x, z, h0 + 0.05)
        mb.cone(Matrix.Translation(base + d * L / 2) @ Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4(), 3,
                0.07 * s, 0.0, L, M_AGAVE if k % 3 else M_AGAVE_D)


# (round 25) the three viaducts (all real: Gaudí's Pont de Baix, del Mig and de Dalt), each carrying a stretch of path
# along the hillside, the ground falling away below it (north.py park_height); each different, as the real ones are:
#   baix  leaning columns of rough stone, a vault from them to the path's edge, planters of agaves along its parapet
#   mig   two rows of columns, the inner upright, the outer leaning, round arches between, stone balls on its parapet
#   dalt  upright columns with round arches between, a great stone urn on the parapet over each, planted
M_URN = mat('ViaductUrn', '#b49a78', 0.9)


def via_side(line, x, z, nx, nz):
    """Which way is downhill from the path at (x, z): +1 along (nx, nz), -1 against it."""
    return 1 if N.park_lawn(x + nx * 4, z + nz * 4) < N.park_lawn(x - nx * 4, z - nz * 4) else -1


for vname, line in N.VIADUCTS.items():
    pts_v = []
    for (a_, b_) in zip(line, line[1:]):
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        n_ = max(1, int(L_ / 2.6))
        for k in range(n_):
            t = (k + 0.5) / n_
            pts_v.append((a_[0] + (b_[0] - a_[0]) * t, a_[1] + (b_[1] - a_[1]) * t, (b_[0] - a_[0]) / L_, (b_[1] - a_[1]) / L_, L_ / n_))
    for i_, (x, z, dx, dz, step) in enumerate(pts_v):
        nx_, nz_ = -dz, dx
        sd = via_side(line, x, z, nx_, nz_)
        ox, oz = nx_ * sd, nz_ * sd                                        # (out, downhill)
        lev = gz(x, z)
        ex, ez = x + ox * 2.45, z + oz * 2.45                              # the path's outer edge
        if vname == 'dalt':
            # (round 33: its road runs 5 m inside the park wall — a parapet there stood a metre off the wall, two walls
            # side by side; the planted urns stand on the verge on low plinths, every third step)
            if i_ % 3 == 1:
                ux_, uz_ = x + ox * 2.2, z + oz * 2.2
                ug_ = gz(ux_, uz_)
                pg.box(V(ux_, uz_, ug_ + 0.2), (dx, -dz), (ox, -oz), 0.4, 0.4, 0.25, M_RUBBLE)
                urn = V(ux_, uz_, ug_ + 0.5)
                pg.cone(Matrix.Translation(urn + Vector((0, 0, 0.1))), 10, 0.22, 0.42, 0.25, M_URN)
                pg.ico(Matrix.Translation(urn + Vector((0, 0, 0.55))) @ Matrix.Diagonal((0.55, 0.55, 0.45, 1)), 1.0, M_URN, 2)
                pgw.clump(urn + Vector((0, 0, 1.05)), (0.5, 0.5, 0.35), 9, 0.45, M_ROSEMARY, nr)
                solid(ux_ - 0.45, uz_ - 0.45, ux_ + 0.45, uz_ + 0.45)
            continue
        if vname == 'mig':
            # (round 35, PATH_RULES F8: a parapet only where there is a steep drop — beside the Pont del Mig the ground
            # falls 0.55 m in 4.5 m: its stone balls on low plinths along the verge instead, every other step, as the
            # Pont de Dalt's urns)
            if i_ % 2 == 0:
                bx_, bz_ = x + ox * 2.2, z + oz * 2.2
                bg_ = gz(bx_, bz_)
                pg.box(V(bx_, bz_, bg_ + 0.22), (dx, -dz), (ox, -oz), 0.32, 0.32, 0.26, M_RUBBLE)
                pg.ico(Matrix.Translation(V(bx_, bz_, bg_ + 0.74)), 0.26, M_RUBBLE, 1)
                solid(bx_ - 0.36, bz_ - 0.36, bx_ + 0.36, bz_ + 0.36)
            continue
        # the parapet, a coping, and the game's wall along it
        pg.box(V(ex, ez, lev + 0.45), (dx, -dz), (ox, -oz), step / 2 + 0.02, 0.2, 0.45, M_RUBBLE)
        pg.box(V(ex, ez, lev + 0.93), (dx, -dz), (ox, -oz), step / 2 + 0.02, 0.26, 0.05, M_TRENC if vname == 'baix' else M_RUBBLE)
        solid(ex - 0.6, ez - 0.6, ex + 0.6, ez + 0.6)
        # (round 33, the user: the park "in shambles" — the trench dug beside these roads for the viaducts' columns left
        # sloping wedges and stub columns; the roads lie on the hillside now, a parapet along their open side, and on
        # it the Pont del Mig's stone balls and the Pont de Dalt's planted urns)
        if vname == 'mig':
            pg.ico(Matrix.Translation(V(ex, ez, lev + 1.2)), 0.26, M_RUBBLE, 1)                  # a stone ball
        elif vname == 'dalt':
            urn = V(ex, ez, lev + 1.0)                                     # the urn (jardinera), planted
            pg.cone(Matrix.Translation(urn + Vector((0, 0, 0.1))), 10, 0.22, 0.42, 0.25, M_URN)
            pg.ico(Matrix.Translation(urn + Vector((0, 0, 0.55))) @ Matrix.Diagonal((0.55, 0.55, 0.45, 1)), 1.0, M_URN, 2)
            pgw.clump(urn + Vector((0, 0, 1.05)), (0.5, 0.5, 0.35), 9, 0.45, M_ROSEMARY, nr)
north['park']['viaducts'] = {k: [list(p) for p in v] for k, v in N.VIADUCTS.items()}

# (round 34, the user: "The Pòrtic de la Bugadera is good, but looks a bit 'blocky'… make it look more gaudi. It also is
# actually on the other side… It has a wall on the other side and you can walk on the top… The most prominent one is
# between casa museu and the higher up casa"; and the aerial view) the covered walk, north.py GALLERY: round the back of
# the Nature Square and on east above the Casa Museu. As the real porticoes: rough stone columns like palm trunks on its
# open side, swelling into knobbly capitals, ribs springing from them across the vault like fronds to the hill's
# retaining wall (its face ribbed with leaning half-columns: the wave); on top a roof of sauló paving level with the hill
# behind, stone planters of agaves and rosemary along its edge. Behind the square the outer row leans in hard (the
# Bugadera's wave) and one column is the washerwoman with her basket on her head; past the square they stand straighter,
# and a low wall runs between them above the bank down to the Casa Museu. The game walks the roof (scene 'decks').
GL = N.GALLERY
G_OUT, G_WALL, G_ROOF, G_DIN = GL['out'], GL['wall'], GL['roof'], GL['deck_in']
M_BEDEARTH = mat('RoofBedEarth', '#7d6248', 0.97)
GLINE = GL['line']
GLEN = sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(GLINE, GLINE[1:]))
grng = random.Random(1906)


def gal_pt(u):
    u = max(0.0, min(GLEN, u))
    acc = 0.0
    for a_, b_ in zip(GLINE, GLINE[1:]):
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        if u <= acc + L_ + 1e-6:
            t_ = (u - acc) / L_
            return a_[0] + (b_[0] - a_[0]) * t_, a_[1] + (b_[1] - a_[1]) * t_
        acc += L_
    return GLINE[-1]


def gal_frame(u):
    """At u metres along the lower walk's line: (x, z, direction, normal into the hill, floor, the outer row's lean)."""
    x_, z_ = gal_pt(u)
    pa, pb = gal_pt(u - 0.9), gal_pt(u + 0.9)
    f_ = Vector((pb[0] - pa[0], pb[1] - pa[1])).normalized()
    n_ = Vector((f_.y, -f_.x))
    fl_ = N.gallery_where(x_, z_)[3]
    lean_ = 0.8 if x_ < GL['flat_to'] else 0.3
    return x_, z_, f_, n_, fl_, lean_


def gP(fr, s, h):
    """A point on the section at frame fr: s across (+ into the hill), h above its floor (Blender coordinates)."""
    return V(fr[0] + fr[3].x * s, fr[1] + fr[3].y * s, fr[4] + h)


def vault_h(s, lean_):
    """The vault's underside across the walk: from the capitals' heads up to its crown, down to the wall."""
    s0 = -1.95 + lean_
    k = (s - s0) / (G_WALL - s0)
    return 3.55 + (3.45 - 3.55) * k + 0.5 * math.sin(math.pi * max(0.0, min(1.0, k)))


# the continuous parts: the floor, the hill's wall, the vault, the roof and its parapet
nstep = max(2, int(GLEN / 0.7))
frames = [gal_frame(GLEN * i / nstep) for i in range(nstep + 1)]
for F0, F1 in zip(frames, frames[1:]):
    pg.face([gP(F0, -G_OUT, 0.04), gP(F1, -G_OUT, 0.04), gP(F1, G_WALL, 0.04), gP(F0, G_WALL, 0.04)], M_SAND_SQ, normal=(0, 0, 1))
    pg.face([gP(F0, G_WALL, -0.5), gP(F1, G_WALL, -0.5), gP(F1, G_WALL, G_ROOF), gP(F0, G_WALL, G_ROOF)], M_RUBBLE,
            normal=(-F0[3].x, F0[3].y, 0))
    ss0 = [-G_OUT] + [-1.95 + F0[5] + (G_WALL + 1.95 - F0[5]) * j / 6 for j in range(7)]
    ss1 = [-G_OUT] + [-1.95 + F1[5] + (G_WALL + 1.95 - F1[5]) * j / 6 for j in range(7)]
    for j in range(len(ss0) - 1):
        h00 = 3.55 if j == 0 else vault_h(ss0[j], F0[5])
        h01 = vault_h(ss0[j + 1], F0[5])
        h10 = 3.55 if j == 0 else vault_h(ss1[j], F1[5])
        h11 = vault_h(ss1[j + 1], F1[5])
        pg.face([gP(F0, ss0[j], h00), gP(F1, ss1[j], h10), gP(F1, ss1[j + 1], h11), gP(F0, ss0[j + 1], h01)], M_RUBBLE,
                normal=(0, 0, -1), smooth=True)
    # the roof: paving from the open edge to over the hill's edge; its fascia on the open side
    pg.face([gP(F0, -G_OUT, G_ROOF), gP(F1, -G_OUT, G_ROOF), gP(F1, G_DIN, G_ROOF), gP(F0, G_DIN, G_ROOF)], M_SAND_SQ, normal=(0, 0, 1))
    pg.face([gP(F0, -G_OUT, 3.4), gP(F1, -G_OUT, 3.4), gP(F1, -G_OUT, G_ROOF + 0.05), gP(F0, -G_OUT, G_ROOF + 0.05)], M_RUBBLE,
            normal=(-F0[3].x, F0[3].y, 0))
    pg.face([gP(F0, G_DIN, G_ROOF - 0.8), gP(F1, G_DIN, G_ROOF - 0.8), gP(F1, G_DIN, G_ROOF), gP(F0, G_DIN, G_ROOF)], M_RUBBLE,
            normal=(F0[3].x, -F0[3].y, 0))
    # the bed over the vault: earth a hand below the kerb, a rubble kerb along the wall's line; the wall solid there
    pg.face([gP(F0, -G_OUT + 0.36, G_ROOF + 0.22), gP(F1, -G_OUT + 0.36, G_ROOF + 0.22), gP(F1, G_WALL, G_ROOF + 0.22),
             gP(F0, G_WALL, G_ROOF + 0.22)], M_BEDEARTH, normal=(0, 0, 1))
    for (s_k, nn_) in ((G_WALL, 1.0), (G_WALL - 0.3, -1.0)):
        pg.face([gP(F0, s_k, G_ROOF), gP(F1, s_k, G_ROOF), gP(F1, s_k, G_ROOF + 0.38), gP(F0, s_k, G_ROOF + 0.38)], M_RUBBLE,
                normal=(F0[3].x * nn_, -F0[3].y * nn_, 0))
    pg.face([gP(F0, G_WALL - 0.3, G_ROOF + 0.38), gP(F1, G_WALL - 0.3, G_ROOF + 0.38), gP(F1, G_WALL, G_ROOF + 0.38),
             gP(F0, G_WALL, G_ROOF + 0.38)], M_RUBBLE, normal=(0, 0, 1))
    wq_ = [(Fq[0] + Fq[3].x * s_, Fq[1] + Fq[3].y * s_) for (Fq, s_) in ((F0, G_WALL - 0.15), (F1, G_WALL - 0.15), (F1, G_WALL + 0.2), (F0, G_WALL + 0.2))]
    scene.setdefault('solids', []).append([[round(a_, 2), round(b_, 2)] for a_, b_ in wq_])
    # the parapet along the roof's open edge: rubble, waist-low, rounded on top
    for (s_a, s_b, h_a, h_b) in ((-G_OUT, -G_OUT + 0.36, G_ROOF, G_ROOF + 0.55),):
        pg.face([gP(F0, s_a, h_a), gP(F1, s_a, h_a), gP(F1, s_a, h_b), gP(F0, s_a, h_b)], M_RUBBLE, normal=(-F0[3].x, F0[3].y, 0))
        pg.face([gP(F0, s_b, h_a), gP(F1, s_b, h_a), gP(F1, s_b, h_b), gP(F0, s_b, h_b)], M_RUBBLE, normal=(F0[3].x, -F0[3].y, 0))
        pg.face([gP(F0, s_a, h_b), gP(F1, s_a, h_b), gP(F1, s_b, h_b), gP(F0, s_b, h_b)], M_RUBBLE, normal=(0, 0, 1))
# its ends: the roof's end face and the wall's return into the hill
def _path_at(Fe, s_):
    q_ = gP(Fe, s_, 0.0)
    return min(N._seg_near(q_.x, -q_.y, P_)[0] for P_ in N.PARK_PATHS) < 1.7


for u_e, sg_ in ((0.0, -1.0), (GLEN, 1.0)):
    Fe = gal_frame(u_e)
    nrm_ = (Fe[2].x * sg_, -Fe[2].y * sg_, 0)
    # (round 35, PATH_RULES B2/A5: the roof's end stood 0.55 m above its paving right across the walk, and the return's
    # top 0.3 m above the hill, both across the paths that come onto the roof there: the end is a parapet only over the
    # open lower walk and where no path comes on; the return's top is level with the roof)
    # (round 35, PATH_RULES G2, the user: "this wall has no depth, she can currently fall down") the end is a parapet
    # with depth (0.4 m, a top), from the open edge to where the path comes on; behind the hill wall's line it is solid,
    # so she can't step off the roof where the ground past the end lies 4 m below; open only where a path comes on
    ks_ = 24
    s_open = G_DIN
    for k_ in range(ks_):
        sm_ = G_WALL + (G_DIN - G_WALL) * (k_ + 0.5) / ks_
        if _path_at(Fe, sm_):
            s_open = min(s_open, G_WALL + (G_DIN - G_WALL) * k_ / ks_)
    s_open = max(s_open, G_WALL + 1.2)
    sm_ = (-G_OUT + s_open) / 2
    hm_ = (3.4 + G_ROOF + 0.55) / 2
    pg.box(gP(Fe, sm_, hm_) + Vector((Fe[2].x * sg_ * -0.2, -Fe[2].y * sg_ * -0.2, 0)), (Fe[3].x, -Fe[3].y), (Fe[2].x, -Fe[2].y),
           (s_open + G_OUT) / 2, 0.2, (G_ROOF + 0.55 - 3.4) / 2, M_RUBBLE)
    pg.box(gP(Fe, sm_, G_ROOF + 0.58) + Vector((Fe[2].x * sg_ * -0.2, -Fe[2].y * sg_ * -0.2, 0)), (Fe[3].x, -Fe[3].y),
           (Fe[2].x, -Fe[2].y), (s_open + G_OUT) / 2 + 0.03, 0.24, 0.04, M_STONE)
    _q = [gP(Fe, G_WALL - 0.1, 0) + Vector((Fe[2].x * sg_ * o_, -Fe[2].y * sg_ * o_, 0)) for o_ in (-0.45, 0.05)] + \
         [gP(Fe, s_open, 0) + Vector((Fe[2].x * sg_ * o_, -Fe[2].y * sg_ * o_, 0)) for o_ in (0.05, -0.45)]
    scene['solids'].append([[round(v_.x, 2), round(-v_.y, 2)] for v_ in _q])
    # (round 34, the walk round: the return carried on 3 m further into the hill, holding its edge)
    pg.face([gP(Fe, G_WALL, -0.5), gP(Fe, G_DIN + 3.0, -0.5), gP(Fe, G_DIN + 3.0, 3.4), gP(Fe, G_WALL, 3.4)], M_RUBBLE, normal=nrm_)
    pg.face([gP(Fe, G_DIN, 3.4), gP(Fe, G_DIN + 3.0, 3.4), gP(Fe, G_DIN + 3.0, G_ROOF), gP(Fe, G_DIN, G_ROOF)], M_RUBBLE, normal=nrm_)

# (round 34, the walk round: the landing of paving past each end lay tilted on the eased bank there, a pale wedge:
# gone — the paths step onto the roof inside its ends)

# the columns, a bay apart
GBAY = 2.15
nb_ = int((GLEN - 1.6) / GBAY) + 1
u0_ = (GLEN - (nb_ - 1) * GBAY) / 2
wash_k = min(range(nb_), key=lambda k: abs(gal_frame(u0_ + k * GBAY)[0] - 95.5))       # (the washerwoman, by the west corner)
n_cols = 0
for k in range(nb_):
    u = u0_ + k * GBAY
    F = gal_frame(u)
    x, z, f_, n_, fl_, lean_ = F
    bx_, bz_ = x - n_.x * 1.95, z - n_.y * 1.95
    hb_ = min(fl_, hz(bx_, bz_)) - 0.15
    b3 = V(bx_, bz_, hb_)
    t3 = gP(F, -1.95 + lean_, 3.2)
    d3 = t3 - b3
    rot_ = Vector((0, 0, 1)).rotation_difference(d3.normalized()).to_matrix().to_4x4()
    side_ = Vector((f_.x, -f_.y, 0))
    if k == wash_k:
        # the washerwoman: her skirt on a short drum, her body, her head, the basket of washing on it, one arm up to it;
        # the column's capital on the basket
        foot_ = b3 + Vector((0, 0, fl_ - hb_))
        wp = lambda h: foot_ + d3.normalized() * (h / d3.normalized().z)
        pg.cone(Matrix.Translation(wp(0.3)) @ rot_, 10, 0.44, 0.4, 0.6 + (fl_ - hb_), M_RUBBLE, uvscale=0.9)
        pg.cone(Matrix.Translation(wp(1.15)) @ rot_, 12, 0.4, 0.25, 1.1, M_RUBBLE, uvscale=0.9)                # skirt
        pg.cone(Matrix.Translation(wp(1.95)) @ rot_, 10, 0.24, 0.19, 0.55, M_RUBBLE, uvscale=0.9)              # body
        pg.ico(Matrix.Translation(wp(2.38)), 0.16, M_RUBBLE, 2, smooth=True)                                     # head
        pg.cone(Matrix.Translation(wp(2.68)) @ rot_, 12, 0.3, 0.42, 0.32, M_RUBBLE, uvscale=0.9)               # the basket
        pg.ico(Matrix.Translation(wp(2.86)) @ Matrix.Diagonal((1.0, 1.0, 0.35, 1)), 0.38, M_RUBBLE, 2, jitter=0.04, rng=grng)
        pg.tube(wp(2.12) + side_ * 0.2, wp(2.72) + side_ * 0.36, 0.06, M_RUBBLE, 6)                             # her arm
        pg.cone(Matrix.Translation(wp(3.05)) @ rot_, 9, 0.3, 0.36, 0.35, M_RUBBLE, uvscale=0.9)
    else:
        # the trunk: rough drums, each a little fatter or thinner, knobs of stone breaking its outline
        nd_ = 5
        for q_ in range(nd_):
            ra_ = 0.35 + 0.04 * math.sin(q_ * 1.9 + k * 0.7) + grng.uniform(-0.025, 0.025)
            pg.cone(Matrix.Translation(b3 + d3 * (q_ + 0.5) / nd_) @ rot_, 10, ra_, ra_ - 0.02, d3.length / nd_ + 0.03,
                    M_RUBBLE, uvscale=0.9)
            if grng.random() < 0.8:
                a_ = grng.uniform(0, math.tau)
                rad_ = Vector((math.cos(a_), math.sin(a_), 0))
                pg.ico(Matrix.Translation(b3 + d3 * (q_ + grng.uniform(0.2, 0.8)) / nd_ + rad_ * ra_ * 0.85),
                       grng.uniform(0.11, 0.17), M_RUBBLE, 1, jitter=0.03, rng=grng)
        pg.ico(Matrix.Translation(b3 + Vector((0, 0, fl_ - hb_ + 0.12))) @ Matrix.Diagonal((1.0, 1.0, 0.45, 1)), 0.52, M_RUBBLE, 1,
               jitter=0.05, rng=grng)                                                                           # its foot
    # the capital: flaring out like a palm's crown, a knobbly cushion on top, and ribs springing from it across the
    # vault, a frond to the wall and one to each side
    cap_ = t3
    pg.cone(Matrix.Translation(cap_ + Vector((0, 0, 0.2))), 10, 0.36, 0.66, 0.42, M_RUBBLE, uvscale=0.9)
    pg.ico(Matrix.Translation(cap_ + Vector((0, 0, 0.42))) @ Matrix.Diagonal((1.0, 1.0, 0.4, 1)), 0.72, M_RUBBLE, 2,
           jitter=0.07, rng=grng)
    for (du_, s_to) in ((0.0, G_WALL - 0.05), (-GBAY * 0.5, G_WALL - 0.05), (GBAY * 0.5, G_WALL - 0.05), (-GBAY * 0.5, -1.95 + lean_), (GBAY * 0.5, -1.95 + lean_)):
        Ft = gal_frame(u + du_)
        if s_to < 0:
            if not (0.0 < u + du_ < GLEN):
                continue
            end_ = gP(Ft, s_to, 3.6)
        else:
            end_ = gP(Ft, s_to, 3.45)
        mid_ = (cap_ + Vector((0, 0, 0.45)) + end_) / 2 + Vector((0, 0, 0.18))
        pg.tube(cap_ + Vector((0, 0, 0.45)), mid_, 0.1, M_RUBBLE, 6)
        pg.tube(mid_, end_, 0.09, M_RUBBLE, 6)
    solid(bx_ - 0.36, bz_ - 0.36, bx_ + 0.36, bz_ + 0.36)
    # the half-column in the wall facing it, leaning out over the walk at its top: the wave
    wb = gP(F, G_WALL - 0.12, -0.3)
    wt = gP(F, G_WALL - 0.5, 3.35)
    dw = wt - wb
    pg.cone(Matrix.Translation((wb + wt) / 2) @ Vector((0, 0, 1)).rotation_difference(dw.normalized()).to_matrix().to_4x4(),
            9, 0.3, 0.22, dw.length, M_RUBBLE, uvscale=0.9)
    # past the square, a low rubble wall between the columns, above the bank down to the Casa Museu
    if x >= GL['flat_to'] + 1.0 and k < nb_ - 1:
        Fn = gal_frame(u + GBAY)
        for (sa_, sb_) in ((-2.08, -1.82),):
            pa_ = (x - n_.x * 1.95, z - n_.y * 1.95)
            pb_ = (Fn[0] - Fn[3].x * 1.95, Fn[1] - Fn[3].y * 1.95)
            mx_, mz_ = (pa_[0] + pb_[0]) / 2, (pa_[1] + pb_[1]) / 2
            dd_ = Vector((pb_[0] - pa_[0], pb_[1] - pa_[1]))
            lo_ = min(hz(mx_, mz_), fl_) - 0.4
            pg.box(V(mx_, mz_, (lo_ + fl_ + 0.65) / 2), (dd_.x / dd_.length, -dd_.y / dd_.length), (n_.x, -n_.y), dd_.length / 2,
                   0.16, (fl_ + 0.65 - lo_) / 2, M_RUBBLE)
            scene.setdefault('solids', []).append([[round(pa_[0], 2), round(pa_[1], 2)], [round(pb_[0], 2), round(pb_[1], 2)],
                                                   [round(pb_[0] - n_.x * 0.3, 2), round(pb_[1] - n_.y * 0.3, 2)],
                                                   [round(pa_[0] - n_.x * 0.3, 2), round(pa_[1] - n_.y * 0.3, 2)]])
    # on the roof's parapet, every other bay: a planter of agave, rosemary or lentisk
    if k % 2 == 0:
        pc_ = gP(F, -G_OUT + 0.18, G_ROOF + 0.55)
        pg.box(pc_ + Vector((0, 0, 0.14)), (f_.x, -f_.y), (n_.x, -n_.y), 0.55, 0.3, 0.14, M_RUBBLE)
        if k % 4 == 0:
            pcx, pcz = x + n_.x * (-G_OUT + 0.18), z + n_.y * (-G_OUT + 0.18)
            agave(pg, pcx, pcz, fl_ + G_ROOF + 0.75, 0.75, grng)
        else:
            pgw.clump(pc_ + Vector((0, 0, 0.55)), (0.55, 0.4, 0.35), 8, 0.5, M_ROSEMARY if k % 3 else M_LENTISK, grng)
    n_cols += 1
# the bed's planting: rosemary, lentisk and broom in a low hedge, an agave now and then, flowers between
u_ = 0.6
while u_ < GLEN - 0.6:
    Fb = gal_frame(u_)
    sb_ = grng.uniform(-1.2, 1.0)
    bx2_, bz2_ = Fb[0] + Fb[3].x * sb_, Fb[1] + Fb[3].y * sb_
    ht_ = Fb[4] + G_ROOF + 0.22
    r_ = grng.random()
    if r_ < 0.12:
        agave(pg, bx2_, bz2_, ht_ - 0.05, 0.8, grng)
    elif r_ < 0.3:
        fm_ = M_FLOWERS[grng.randrange(len(M_FLOWERS))]
        for _f in range(3):
            c_ = V(bx2_ + grng.uniform(-0.3, 0.3), bz2_ + grng.uniform(-0.3, 0.3), ht_ + 0.2)
            a0_ = grng.uniform(0, 3.14)
            for jj in range(3):
                pgw.card(c_, 0.28, vertical(a0_ + jj * 1.0472), c_ - Vector((0, 0, 0.28)), fm_, 0.35)
    else:
        rr_ = grng.uniform(0.4, 0.6)
        pgw.clump(V(bx2_, bz2_, ht_ + rr_ * 0.6), (rr_, rr_, rr_ * 0.75), 7, 0.6,
                  park_tone(pick([(M_ROSEMARY, 2), (M_LENTISK, 2), (M_BROOM, 1)], grng)), grng)
    u_ += grng.uniform(0.7, 1.1)

# the roof is walked on (engine/main.gd): its paving behind the wall's line, in pieces, each at its own height; in front
# of it, over the vault, the roof is a planted bed behind the parapet (round 34, the play-through: the walls are solid
# at every height to the game, so the hill's wall is the walk's edge on the roof too — a kerb, the bed beyond it)
decks = scene.setdefault('decks', [])
for F0, F1 in zip(frames[::3], frames[3::3] + ([frames[-1]] if (len(frames) - 1) % 3 else [])):
    poly_ = []
    for (Fq, s_) in ((F0, G_DIN), (F1, G_DIN), (F1, G_WALL + 0.2), (F0, G_WALL + 0.2)):     # (wound as poly_dist wants)
        poly_.append([round(Fq[0] + Fq[3].x * s_, 3), round(Fq[1] + Fq[3].y * s_, 3)])
    decks.append({'p': poly_, 'h': round((F0[4] + F1[4]) / 2 + G_ROOF, 3)})
# (round 40, the user: "when you're running through the covered area, with the columns in the park, the camera should be
# sitting only up to the ceiling… treat it like an actual camera"; rule 03 #16b) the vault over the lower walk, for the
# camera to stay under: its underside (vault_h: 3.45 m at the wall, more over the walk) and its top
for F0, F1 in zip(frames[::3], frames[3::3] + ([frames[-1]] if (len(frames) - 1) % 3 else [])):
    poly_ = [[round(Fq[0] + Fq[3].x * s_, 3), round(Fq[1] + Fq[3].y * s_, 3)]
             for (Fq, s_) in ((F0, -G_OUT - 0.3), (F1, -G_OUT - 0.3), (F1, G_WALL), (F0, G_WALL))]
    fl_ = min(F0[4], F1[4])
    scene.setdefault('cam_roofs', []).append({'p': poly_, 'ceil': round(fl_ + 3.45, 3), 'top': round(max(F0[4], F1[4]) + G_ROOF + 0.6, 3)})
north['park']['gallery'] = [list(p) for p in GLINE]
print('PARK the covered walk: %.0f m, %d columns, %d roof pieces' % (GLEN, n_cols, len(decks)))

# the calvary: a rough stone platform on the rise's top, steps up to it, a cairn with the three crosses (the tallest
# with Gaudí's four-armed cross, pointing to the four winds)
cvx, cvz = N.GUELL['calvari']
ch_ = gz(cvx, cvz)
pg.cone(Matrix.Translation(V(cvx, cvz, ch_ + 0.2)), 18, 4.2, 3.9, 0.55, M_RUBBLE)
# (round 40, the user: "this is floating… fix it, review it, fix it and review it again") the platform sat level with
# the rise's top, its south rim 0.9 m clear of the falling ground, its three steps hanging in the air short of it: a
# skirt of the same rubble from under the rim down into the ground all round, and the flight carried down to the
# ground at the path's end (PARK_PATHS[3]), each step a block down into the ground
CV_TOP = ch_ + 0.475
rim_ = [gz(cvx + 4.2 * math.cos(a_ * math.pi / 18), cvz + 4.2 * math.sin(a_ * math.pi / 18)) for a_ in range(36)]
sk_lo = min(rim_) - 0.3
pg.cone(Matrix.Translation(V(cvx, cvz, (sk_lo + ch_ - 0.05) / 2)), 18, 4.2, 4.2, ch_ - 0.05 - sk_lo, M_RUBBLE)
CV_Z0, CV_Z1 = cvz + 4.0, N.PARK_PATHS[3][-1][1]                            # (the flight: from under the rim to the path)
n_cv = max(3, round((CV_Z1 - CV_Z0) / 0.32))
tr_cv = (CV_Z1 - CV_Z0) / n_cv
g_foot = max(gz(cvx + dx_, CV_Z1 + 0.1) for dx_ in (-1.2, 0.0, 1.2))
ri_cv = (CV_TOP - g_foot) / (n_cv + 1)
for k in range(n_cv):                                                       # (steps up its south side; on the north the
    zc_ = CV_Z0 + (k + 0.5) * tr_cv                                         # hill meets its rim)
    top_ = CV_TOP - (k + 1) * ri_cv
    lo_ = min(gz(cvx + dx_, zc_ + dz_) for dx_ in (-1.2, 1.2) for dz_ in (-tr_cv / 2, tr_cv / 2)) - 0.3
    pg.box(V(cvx, zc_, (lo_ + top_) / 2), (1, 0), (0, 1), 1.2, tr_cv / 2 + 0.01, (top_ - lo_) / 2, M_RUBBLE)
# (round 40, the user: "It should just be a normal object. So it's physical, you can walk up onto it via the stairs, run
# around it… without bumping into the crosses… and then when you run to the side, you just fall off it… But all the
# curved parts are solid") the flight is a ramp she walks ('flats'), the platform's top a floor she walks on, its round
# side a wall from below and a drop from above ('decks' with rim and drop, main.gd); the cairn and crosses solid
scene.setdefault('flats', []).append([round(cvx - 1.2, 3), round(CV_Z0 - 0.1, 3), round(cvx + 1.2, 3), round(CV_Z1, 3),
                                      round(CV_TOP, 3), round(g_foot, 3)])
_cvp = [[round(cvx + 4.2 * math.cos(-a_ * math.pi / 12), 3), round(cvz + 4.2 * math.sin(-a_ * math.pi / 12), 3)] for a_ in range(24)]
def _poly_dist(poly_, x_, z_):
    # (main.gd poly_dist: the greatest distance out past an edge — negative inside, when wound its way)
    return max(((x_ - a_[0]) * (b_[1] - a_[1]) - (z_ - a_[1]) * (b_[0] - a_[0])) / math.hypot(b_[0] - a_[0], b_[1] - a_[1])
               for a_, b_ in zip(poly_, poly_[1:] + poly_[:1]))


if _poly_dist(_cvp, cvx, cvz) > 0:
    _cvp.reverse()                                     # (wound as main.gd poly_dist wants: the centre inside, negative)
scene.setdefault('decks', []).append({'p': _cvp, 'h': round(CV_TOP, 3), 'rim': True, 'drop': True})
print('PARK the calvary: top %.2f, skirt down to %.2f, %d steps of %.2f m up from %.2f' % (CV_TOP, sk_lo, n_cv, ri_cv, g_foot))
pg.cone(Matrix.Translation(V(cvx, cvz - 1.2, ch_ + 1.4)), 10, 1.5, 0.9, 2.0, M_RUBBLE)
for (ox_, oz_, hh_, four) in ((0.0, -1.2, 3.6, True), (-1.9, -0.3, 2.4, False), (1.9, -0.3, 2.4, False)):
    bxp, bzp = cvx + ox_, cvz + oz_
    base_h = ch_ + (2.4 if four else 0.55)
    pg.box(V(bxp, bzp, base_h + hh_ / 2), (1, 0), (0, 1), 0.12, 0.12, hh_ / 2, M_GREYSTONE)
    if four:
        for ax_d in ((1, 0), (0, 1)):
            pg.box(V(bxp, bzp, base_h + hh_ - 0.5), (ax_d[0], ax_d[1]), (-ax_d[1], ax_d[0]), 0.55, 0.11, 0.11, M_GREYSTONE)
        pg.cone(Matrix.Translation(V(bxp, bzp, base_h + hh_ + 0.25)), 4, 0.16, 0.0, 0.5, M_GREYSTONE)
    else:
        pg.box(V(bxp, bzp, base_h + hh_ - 0.55), (1, 0), (0, 1), 0.5, 0.11, 0.11, M_GREYSTONE)
# (round 39, the user, standing inside its stone: "this should be a solid object") the whole platform is solid, its
# round edge covered by three overlapping boxes, not only the cairn and the crosses
solid(cvx - 1.15, cvz - 2.35, cvx + 1.15, cvz - 0.05)                       # (the cairn, with the tall cross)
for ox_ in (-1.9, 1.9):
    solid(cvx + ox_ - 0.16, cvz - 0.46, cvx + ox_ + 0.16, cvz - 0.14)          # (the two crosses)
north['park']['calvari'] = [cvx, cvz]

# the Nature Square (round 34: no plane trees or benches along its back now — the covered walk's columns stand there)
sx0, sz0, sx1, sz1 = G['square_r']
# (round 33: the trencadís pots at the plaza's and the porch's corners, by the stairs' feet, gone — "colour items")
# ------------------------------------------------------------------ (round 26, the user: "make it somewhere that a
# player would want to explore. The beauty is in the small detail") the park's small things: low plants along every
# path's edge (rosemary, broom in flower, lentisk, the park's wildflowers), stone benches along the walks with a bin
# here and there, agaves in the dragon stairs' planters, lamps at the plaza, the porch and the square, fingerposts at
# the junctions, and people strolling the paths
prk2 = random.Random(1914)


def pk_clear(x, z, pad=1.5):
    """Is (x, z) on or by one of the park's built things (the terraces, stairs, houses, lodges, gates)?"""
    for r in (G['plaza'], G['porch'], G['stairs_r'], G['hypostyle'], G['square_r'], G['museu_r'], G['trias_r'], G['larrard_r']) + tuple(G['side_stairs']):
        if r[0] - pad <= x <= r[2] + pad and r[1] - pad <= z <= r[3] + pad:
            return True
    for (lx2_, lz2_) in (G['guarda'], G['lodge']):
        if abs(x - lx2_) < 5.0 + pad and abs(z - lz2_) < 4.5 + pad:
            return True
    if any(math.hypot(x - gv_.x, z - gv_.y) < 5.0 + pad for _g, gv_ in GATES_ALL):
        return True
    s_, t_, be_, fl_ = N.gallery_where(x, z)
    if -N.GALLERY['out'] - pad < s_ < N.GALLERY['deck_in'] + pad and be_ < pad + 0.5:
        return True                                      # (round 34: the covered walk and its roof)
    return math.hypot(x - G['calvari'][0], z - G['calvari'][1]) < 5.0 + pad


n_edge = 0
# (round 34, the user: "It is slightly more dryer with the paths quite closed in with plants. Look at the actual
# pictures") in the wood both edges of every path are planted thick: low plants at the edge, and behind them a row of
# shrubs as high as her shoulder (lentisk, strawberry tree, rosemary, broom), so the paths run between banks of green;
# by the open lawns, a looser edge as before. All the park's green toned down (world2d.py park_tone).
for P_ in N.PARK_PATHS:
    for (px_, pz_) in dense(P_, 1.4):
        i_ = min(range(len(P_) - 1), key=lambda k: math.hypot(px_ - P_[k][0], pz_ - P_[k][1]))
        dv_ = Vector((P_[i_ + 1][0] - P_[i_][0], P_[i_ + 1][1] - P_[i_][1])).normalized()
        for side_ in (-1, 1):
            nv_ = Vector((-dv_.y, dv_.x)) * side_
            wood_ = N.park_wood(px_ + nv_.x * 2.8, pz_ + nv_.y * 2.8)
            for row_ in (((1.75, 2.3), (2.6, 3.4)) if wood_ else ((1.75, 2.3),)):
                if prk2.random() > (0.85 if wood_ else 0.45):
                    continue
                off_ = prk2.uniform(*row_)
                ex_, ez_ = px_ + nv_.x * off_ + prk2.uniform(-0.2, 0.2), pz_ + nv_.y * off_ + prk2.uniform(-0.2, 0.2)
                # (round 40, A5, the user: "The palm tree and foliage is in the path"): its own size plus KEEP_OFF off the
                # drawn edge of every path laid (the Austria walks, the gate paths, the road too) — a front-row clump up to
                # 0.42 m, a shrub behind up to 0.85 m — pushed out along the normal if short of it, dropped if still short
                pk_need_ = (0.85 if row_[0] > 2.0 else 0.42) + KEEP_OFF
                pk_d_ = path_edge_d(ex_, ez_)
                if pk_d_ < pk_need_:
                    ex_, ez_ = ex_ + nv_.x * (pk_need_ - pk_d_), ez_ + nv_.y * (pk_need_ - pk_d_)
                if pk_clear(ex_, ez_, 0.6) or path_edge_d(ex_, ez_) < pk_need_ - 0.02 \
                        or N._seg_near(ex_, ez_, CELLAR_TRACK)[0] < 1.3:
                    continue                                  # (round 35, A5: nor on the cellar's track)
                hg_ = gz(ex_, ez_)
                if row_[0] > 2.0:
                    rr_ = prk2.uniform(0.5, 0.85)
                    pgw.clump(V(ex_, ez_, hg_ + rr_ * 0.75), (rr_, rr_, rr_ * 0.95), 8, 0.75,
                              park_tone(pick([(M_LENTISK, 3), (M_ARBUTUS, 2), (M_ROSEMARY, 1), (M_BROOM, 1)], prk2)), prk2)
                    n_edge += 1
                    continue
                roll_ = prk2.random()
                if roll_ < 0.3:
                    rr_ = prk2.uniform(0.22, 0.4)
                    pgw.clump(V(ex_, ez_, hg_ + rr_ * 0.35), (rr_, rr_, rr_ * 0.6), 6, 0.7, park_tone(M_ROSEMARY), prk2)
                elif roll_ < 0.45:
                    rr_ = prk2.uniform(0.25, 0.4)
                    pgw.clump(V(ex_, ez_, hg_ + rr_ * 0.35), (rr_, rr_, rr_ * 0.7), 6, 0.7, park_tone(M_BROOM), prk2)
                elif roll_ < 0.66:
                    rr_ = prk2.uniform(0.25, 0.42)
                    pgw.clump(V(ex_, ez_, hg_ + rr_ * 0.35), (rr_, rr_, rr_ * 0.6), 6, 0.7, park_tone(M_LENTISK), prk2)
                elif roll_ < 0.8:
                    fm_ = M_FLOWERS[prk2.randrange(len(M_FLOWERS))]
                    for _f in range(prk2.randint(2, 4)):
                        fx_, fz_ = ex_ + prk2.uniform(-0.35, 0.35), ez_ + prk2.uniform(-0.35, 0.35)
                        c_ = V(fx_, fz_, gz(fx_, fz_) + 0.18)
                        a0_ = prk2.uniform(0, 3.14)
                        for jj in range(3):
                            rot_ = vertical(a0_ + jj * 1.0472)
                            pgw.card(c_, 0.28, rot_, c_ - Vector((0, 0, 0.28)), fm_, 0.35)
                else:
                    # (round 33: these were pale stones, which read as litter strewn on the lawns: low lentisk instead)
                    rr_ = prk2.uniform(0.2, 0.3)
                    pgw.clump(V(ex_, ez_, hg_ + rr_ * 0.35), (rr_, rr_, rr_ * 0.5), 5, 0.7, park_tone(M_LENTISK), prk2)
                n_edge += 1
# (round 34, the aerial view's terraces below the Casa Museu; the user: "Should there be a few flowers in the garden")
# the switchbacks climb between terraced beds: a dry-stone wall along the uphill side of each leg, holding up the bed
# above it, and the beds planted with flowers in drifts, rosemary and lavender-blue, a few clipped shrubs
P4_ = N.PARK_PATHS[4]
n_tw = n_tf = 0
# (round 35, PATH_RULES D5 in spirit — "random small fences": the walls stood as loose blocks a metre or two long) each
# side's wall is laid in long runs only: a gap of two pieces or less is the run's, runs under five pieces are left out
_tw_pts = dense(P4_, 0.9)[2:-3]
for side_ in (-1, 1):
    want_w = []
    for (px_, pz_) in _tw_pts:
        i_ = min(range(len(P4_) - 1), key=lambda k: math.hypot(px_ - P4_[k][0], pz_ - P4_[k][1]))
        dv_ = Vector((P4_[i_ + 1][0] - P4_[i_][0], P4_[i_ + 1][1] - P4_[i_][1])).normalized()
        nv_ = Vector((-dv_.y, dv_.x)) * side_
        wx_, wz_ = px_ + nv_.x * 1.75, pz_ + nv_.y * 1.75
        hp_ = gz(px_, pz_)
        up_ = gz(px_ + nv_.x * 2.6, pz_ + nv_.y * 2.6)
        ok_ = not (up_ < hp_ + 0.25 or N.rect_d(wx_, wz_, N.PARK_TERRACES) > 1.0 or pk_clear(wx_, wz_, 0.2)
                   or min(N._seg_near(wx_, wz_, Q_)[0] for Q_ in N.PARK_PATHS) < 1.55)
        want_w.append((ok_, wx_, wz_, hp_, up_, dv_, nv_))
    flags_ = [w[0] for w in want_w]
    for k in range(1, len(flags_) - 1):
        if not flags_[k] and flags_[k - 1]:
            for g_ in (1, 2):
                if k + g_ < len(flags_) and flags_[k + g_] and all(min(N._seg_near(want_w[m][1], want_w[m][2], Q_)[0]
                                                                     for Q_ in N.PARK_PATHS) >= 1.55 for m in range(k, k + g_)):
                    for m in range(k, k + g_):
                        flags_[m] = True
                    break
    k = 0
    while k < len(flags_):
        if not flags_[k]:
            k += 1
            continue
        m = k
        while m < len(flags_) and flags_[m]:
            m += 1
        if m - k >= 8:                                    # (a wall 7 m long at the least)
            for q in range(k, m):
                _, wx_, wz_, hp_, up_, dv_, nv_ = want_w[q]
                top_ = min(max(up_, hp_ + 0.35) + 0.12, hp_ + 1.3)
                pg.box(V(wx_, wz_, (hp_ - 0.3 + top_) / 2), (dv_.x, -dv_.y), (nv_.x, -nv_.y), 0.5, 0.2, (top_ - hp_ + 0.3) / 2, M_RUBBLE)
                n_tw += 1
        k = m
tz_r = random.Random(1926)
ter_ = N.PARK_TERRACES
fz_ = ter_[1] + 0.6
while fz_ < ter_[3]:
    fx_ = ter_[0] + 0.6
    while fx_ < ter_[2]:
        x_, z_ = fx_ + tz_r.uniform(-0.3, 0.3), fz_ + tz_r.uniform(-0.3, 0.3)
        fx_ += 1.1
        if min(N._seg_near(x_, z_, Q_)[0] for Q_ in N.PARK_PATHS) < 2.4 or pk_clear(x_, z_, 0.3) or tz_r.random() < 0.3:
            continue
        g_ = gz(x_, z_)
        drift_ = int((x_ * 0.13 + z_ * 0.07) * 3) % 5                       # (flowers in drifts, not salt and pepper)
        if drift_ < 3:
            fm_ = M_FLOWERS[(drift_ * 2 + int(z_ / 6)) % len(M_FLOWERS)]
            for _f in range(tz_r.randint(3, 5)):
                cx_, cz_ = x_ + tz_r.uniform(-0.4, 0.4), z_ + tz_r.uniform(-0.4, 0.4)
                c_ = V(cx_, cz_, gz(cx_, cz_) + 0.2)
                a0_ = tz_r.uniform(0, 3.14)
                for jj in range(3):
                    pgw.card(c_, 0.3, vertical(a0_ + jj * 1.0472), c_ - Vector((0, 0, 0.3)), fm_, 0.35)
        elif drift_ == 3:
            rr_ = tz_r.uniform(0.3, 0.45)
            pgw.clump(V(x_, z_, g_ + rr_ * 0.5), (rr_, rr_, rr_ * 0.7), 7, 0.6, park_tone(M_ROSEMARY), tz_r)
        else:
            rr_ = tz_r.uniform(0.35, 0.5)
            pgw.clump(V(x_, z_, g_ + rr_ * 0.6), (rr_, rr_, rr_ * 0.8), 8, 0.6, park_tone(M_LENTISK), tz_r)
        n_tf += 1
    fz_ += 1.1
print('PARK the terraces: %d m of dry-stone wall, %d bed plantings' % (n_tw, n_tf))

# (round 35, PATH_RULES G1, the user: "here is another invisible wall in the park… make a rule removing these from the
# park unless there is an object like a wall"; "when it does get too steep, put a small stone wall at the top") inside
# the park she climbs anything up to SLOPE_LIM (north.gd: what she wouldn't slide down); where the ground is steeper,
# a low dry-stone wall stands along the foot of the bank, so the wall is what stops her. Found on the ground as built.
SLOPE_LIM = 0.55
_SW = 0.5
_sx0, _sz0, _sx1, _sz1 = 44.0, -256.0, 192.0, -136.0
_pk_flats = [f for f in scene['flats'] if 40 < f[0] < 200 and -260 < f[1] < -130]
_pk_sol = [q for q in scene.get('solids', []) if all(40 < v[0] < 200 and -262 < v[1] < -128 for v in q)]


def _sgrad(x, z):
    return ((gz(x + 0.5, z) - gz(x - 0.5, z)), (gz(x, z + 0.5) - gz(x, z - 0.5)))


def _near_solid(x, z, r):
    for q in _pk_sol:
        if abs(q[0][0] - x) > 25 or abs(q[0][1] - z) > 25:
            continue
        xs_, zs_ = [v[0] for v in q], [v[1] for v in q]
        if min(xs_) - r <= x <= max(xs_) + r and min(zs_) - r <= z <= max(zs_) + r:
            return True
    return False


_foot = {}
for _j in range(int((_sz1 - _sz0) / _SW)):
    for _i in range(int((_sx1 - _sx0) / _SW)):
        x_, z_ = _sx0 + _i * _SW, _sz0 + _j * _SW
        if N.park_r(x_, z_) > 0.94 or any(f[0] - 0.3 <= x_ <= f[2] + 0.3 and f[1] - 0.3 <= z_ <= f[3] + 0.3 for f in _pk_flats):
            continue
        if math.hypot(*_sgrad(x_, z_)) > SLOPE_LIM:
            continue
        h0_ = gz(x_, z_)
        best_ = None
        for a_ in range(8):
            dx_, dz_ = math.cos(a_ * math.pi / 4) * 0.6, math.sin(a_ * math.pi / 4) * 0.6
            h1_ = gz(x_ + dx_, z_ + dz_)
            if (h1_ - h0_) / 0.6 > SLOPE_LIM * 0.8 and math.hypot(*_sgrad(x_ + dx_, z_ + dz_)) > SLOPE_LIM:
                if best_ is None or h1_ > best_[0]:
                    best_ = (h1_, dx_ / 0.6, dz_ / 0.6)
        if best_ is None or _near_solid(x_, z_, 0.8):
            continue
        if min(N._seg_near(x_, z_, P_)[0] for P_ in N.PARK_PATHS) < 1.3:
            continue                                   # (on a path she climbs what the path climbs)
        _foot[(_i, _j)] = (x_, z_, best_[1], best_[2])
# lines of them: neighbours joined, each line walked end to end
_seen, _lines = set(), []
for c_ in list(_foot):
    if c_ in _seen:
        continue
    st_, comp_ = [c_], []
    _seen.add(c_)
    while st_:
        q_ = st_.pop()
        comp_.append(q_)
        for di_ in (-1, 0, 1):
            for dj_ in (-1, 0, 1):
                n_ = (q_[0] + di_, q_[1] + dj_)
                if n_ in _foot and n_ not in _seen:
                    _seen.add(n_)
                    st_.append(n_)
    cx_ = sum(q[0] for q in comp_) / len(comp_)
    cz_ = sum(q[1] for q in comp_) / len(comp_)
    cur_ = max(comp_, key=lambda q: (q[0] - cx_) ** 2 + (q[1] - cz_) ** 2)
    left_, order_ = set(comp_), []
    while left_:
        order_.append(cur_)
        left_.discard(cur_)
        if not left_:
            break
        nxt_ = min(left_, key=lambda q: (q[0] - cur_[0]) ** 2 + (q[1] - cur_[1]) ** 2)
        if (nxt_[0] - cur_[0]) ** 2 + (nxt_[1] - cur_[1]) ** 2 > 9:
            break                                      # (the rest is another stretch: left for the edge pass)
        cur_ = nxt_
    _lines.append([_foot[q] for q in order_])
M_DRYSTONE = M_RUBBLE
_sw_mb = MB(uv=True)
n_sw = 0
for line_ in _lines:
    # smoothed, and set 0.2 m into the bank (its face at the foot)
    pts_ = []
    for k_ in range(len(line_)):
        w_ = line_[max(0, k_ - 2):k_ + 3]
        x_ = sum(q[0] for q in w_) / len(w_)
        z_ = sum(q[1] for q in w_) / len(w_)
        ux_ = sum(q[2] for q in w_) / len(w_)
        uz_ = sum(q[3] for q in w_) / len(w_)
        L_ = math.hypot(ux_, uz_) or 1.0
        pts_.append((x_ + ux_ / L_ * 0.2, z_ + uz_ / L_ * 0.2))
    pts_ = dense(pts_, 0.9) if len(pts_) > 1 else pts_
    by_stairs_ = sum(1 for q_ in pts_ if any(N.rect_d(q_[0], q_[1], r_) < 2.2 for r_ in G['side_stairs'])) > len(pts_) / 2
    if len(pts_) < 6 or by_stairs_:
        # (beside the side stairs' wall: a planted strip at its foot, not a second wall beside it)
        # (a short steep bit: a stub of wall would be "random small walls" (D5) — a thick shrub stands there instead,
        # solid, the thing that stops her)
        for (qx_, qz_) in pts_[::2]:
            rr_ = 0.75
            pgw.clump(V(qx_, qz_, gz(qx_, qz_) + rr_ * 0.6), (rr_, rr_, rr_ * 0.8), 9, 0.7,
                      park_tone(pick([(M_LENTISK, 3), (M_ARBUTUS, 2)], prk2)), prk2)
            # (round 39, the user: "Isn't brush walkable anyway?" — walked through like any bush; listed, not solid)
            scene.setdefault('plant_solids', []).append([round(qx_ - 0.55, 3), round(qz_ - 0.55, 3), round(qx_ + 0.55, 3), round(qz_ + 0.55, 3)])
        continue
    # (round 40, the user: "any brick wall that is sitting at the bottom of a slope needs to be removed"; then, on the
    # map of them: "For all the red ones, could you make them walk through"; PATH_RULES G5) the wall stays as it looks,
    # but it is no longer solid: sliding down the bank she landed between it and the bank and could get out neither
    # way; now she walks through it
    # (round 40, the user on the Austria Gardens: "a brick wall going straight through the garden… remove the ones that I
    # originally flagged") none at all in the gardens
    if N.rect_d(pts_[len(pts_) // 2][0], pts_[len(pts_) // 2][1], G['austria']) < 1.0:
        continue
    # (round 40, the calvary's review: a lone 2 m stub beside its new steps) no stubs: under 4 m, or by the calvary,
    # whose own skirt is its edge, nothing
    if sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(pts_, pts_[1:])) < 4.0 or \
            math.hypot(pts_[len(pts_) // 2][0] - G['calvari'][0], pts_[len(pts_) // 2][1] - G['calvari'][1]) < 9.0:
        continue
    for (a_, b_) in zip(pts_, pts_[1:]):
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        if L_ < 0.05 or L_ > 2.0:
            continue
        mx_, mz_ = (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2
        ux_, uz_ = (b_[0] - a_[0]) / L_, (b_[1] - a_[1]) / L_
        lo_ = min(gz(a_[0], a_[1]), gz(b_[0], b_[1]), gz(mx_ - uz_ * 0.3, mz_ + ux_ * 0.3), gz(mx_ + uz_ * 0.3, mz_ - ux_ * 0.3))
        top_ = lo_ + 0.62
        _sw_mb.box(V(mx_, mz_, (lo_ - 0.35 + top_) / 2), (ux_, -uz_), (-uz_, -ux_), L_ / 2 + 0.06, 0.2, (top_ - lo_ + 0.35) / 2, M_DRYSTONE)
        _sw_mb.box(V(mx_, mz_, top_ + 0.04), (ux_, -uz_), (-uz_, -ux_), L_ / 2 + 0.08, 0.23, 0.04, M_STONE)
    n_sw += 1
city_objs.append(_sw_mb.finish('ParkSlopeWalls'))
north['park']['slope_walls'] = [[[round(a, 2), round(b, 2)] for a, b in dense(l_, 0.9)] for l_ in
                                [[(q[0], q[1]) for q in line_] for line_ in _lines]]
print('PARK slope walls: %d, walked through (round 40), %d foot cells' % (n_sw, len(_foot)))

# (round 35's G3 brick wall beside the roof walk's west path, and round 40's join to it from the walk's end wall: all
# gone — the user: "replace this piece of wall that is not doing anything"; PATH_RULES G3; the path is back, the end
# wall opens where it comes on)
# stone benches along the walks (the real park's are rubble with a flat top), every 28 m or so, on the open side
n_bench = 0
for P_ in N.PARK_PATHS[4:]:
    dp_ = dense(P_, 1.0)
    for k_ in range(14, len(dp_) - 6, 28):
        px_, pz_ = dp_[k_]
        a_, b_ = dp_[k_ - 2], dp_[k_ + 2]
        dv_ = Vector((b_[0] - a_[0], b_[1] - a_[1])).normalized()
        nv_ = Vector((-dv_.y, dv_.x))
        side_ = 1 if gz(px_ + nv_.x * 4, pz_ + nv_.y * 4) <= gz(px_ - nv_.x * 4, pz_ - nv_.y * 4) else -1   # (the view side)
        bx_, bz_ = px_ + nv_.x * side_ * 2.4, pz_ + nv_.y * side_ * 2.4
        if pk_clear(bx_, bz_, 1.5) or any(math.hypot(bx_ - j[0], bz_ - j[1]) < 7.0 for j in PJ_):
            continue
        hb_ = gz(bx_, bz_)
        U_, F_ = (dv_.x, -dv_.y), (-nv_.x * side_, nv_.y * side_)
        pg.box(V(bx_, bz_, hb_ + 0.12), U_, F_, 0.85, 0.26, 0.24, M_RUBBLE)        # (sunk a little: no floating feet on a slope)
        pg.box(V(bx_, bz_, hb_ + 0.38), U_, F_, 0.95, 0.32, 0.04, M_STONE)
        solid(bx_ - 1.0, bz_ - 1.0, bx_ + 1.0, bz_ + 1.0)
        north.setdefault('benches', []).append([round(bx_, 2), round(bz_, 2), round(math.atan2(F_[0], -F_[1]), 3)])
        scene.setdefault('benches', []).append([round(bx_, 2), round(bz_, 2), round(math.atan2(F_[0], -F_[1]), 3), round(hb_ + 0.42, 3)])
        if n_bench % 2 == 0:                                                     # a bin beside every other one
            pg.cone(Matrix.Translation(V(bx_ + dv_.x * 1.3, bz_ + dv_.y * 1.3, hb_ + 0.4)), 10, 0.2, 0.17, 0.8, M_IRON)
            solid(bx_ + dv_.x * 1.3 - 0.25, bz_ + dv_.y * 1.3 - 0.25, bx_ + dv_.x * 1.3 + 0.25, bz_ + dv_.y * 1.3 + 0.25)
        n_bench += 1
# agaves in the dragon stairs' planters; lamps at the plaza, the porch and the square
for (lx2, lz2) in ((G['plaza'][0] + 2.0, G['plaza'][3] - 1.6), (G['plaza'][2] - 2.0, G['plaza'][3] - 1.6),
                   (G['porch'][0] + 8.5, G['porch'][3] - 2.6), (G['porch'][2] - 8.5, G['porch'][3] - 2.6),   # (round 32: off the way to the stairs)
                   (sx0 + 2.0, sz0 + 1.5), (sx1 - 2.0, sz0 + 1.5)):
    gr_lamp(lx2, lz2, 0.0, 1.0)
# fingerposts at the junctions
M_POSTWOOD = mat('FingerpostWood', '#6b4a2e', 0.85)
def _toward(fx_, fz_, tx2, tz2):
    return math.atan2(tz2 - fz_, tx2 - fx_)


# (round 33: at the new junctions, beside the paths rather than on them)
for ((fx_, fz_), _zz, arms) in (((81.0, -152.8), 0, [("Jardins d'Àustria", _toward(81.0, -152.8, 83.5, -160.5)),
                                                     ("Casa Larrard · Porta de Larrard", _toward(81.0, -152.8, 65.5, -157.2))]),
                         ((159.6, -195.6), 0, [("Casa Museu Gaudí", _toward(159.6, -195.6, 156.6, -191.0)),
                                               ("Plaça de la Natura", _toward(159.6, -195.6, 150.0, -196.4))]),
                         # (round 40, the user: "there is a sign pole sticking out of the object with the crosses": the
                         # calvary's platform is a solid floor now; the post stands beside the carriage road, off it)
                         ((74.4, -221.4), 0, [("Turó de les Tres Creus", _toward(74.4, -221.4, 70.0, -217.0)),
                                              ("Pont del Mig", _toward(74.4, -221.4, 112.0, -228.0))])):
    hp_ = gz(fx_, fz_)
    pg.cone(Matrix.Translation(V(fx_, fz_, hp_ + 1.1)), 8, 0.06, 0.07, 2.2, M_POSTWOOD)
    for j, (txt_, ang_) in enumerate(arms):
        zz_ = hp_ + 1.9 - j * 0.28
        ux_, uz_ = math.cos(ang_), math.sin(ang_)
        pg.box(V(fx_ + ux_ * 0.55, fz_ + uz_ * 0.55, zz_), (ux_, -uz_), (-uz_, -ux_), 0.6, 0.02, 0.11, M_POSTWOOD)
        # (round 40, the user: "The words on this sign are sticking out. They're weird": the lettering stood a quarter
        # turn out from the arm, edge on; now painted flat on both of its faces, centred on it, reading along it)
        for sd_ in (1.0, -1.0):
            nrm_e = (-uz_ * sd_, ux_ * sd_)                                       # (the face's outward way, engine)
            city_objs.append(text_obj(txt_, 0.07, M_SIGN_TEXT,
                                      V(fx_ + ux_ * 0.55 + nrm_e[0] * 0.024, fz_ + uz_ * 0.55 + nrm_e[1] * 0.024, zz_ - 0.02),
                                      facing((nrm_e[0], -nrm_e[1])), 'SignText_park_%d_%d_%d' % (int(fx_), j, int(sd_ > 0))))
    solid(fx_ - 0.15, fz_ - 0.15, fx_ + 0.15, fz_ + 0.15)
# (round 39: the park's people walk its paths bend by bend, placed by the game itself — north.gd park_people)
print('PARK small things: %d edge plants, %d benches' % (n_edge, n_bench))
city_objs.append(pg.finish('ParkGuell'))
# (round 40, the user: "the key is just lying nearby under the scrub") a scrub bush over it, the key at its edge (walked
# through like every bush)
_kx, _kz = G['key']
for (ox_, oz_, rr_) in ((-0.55, -0.45, 0.62), (-0.1, -0.85, 0.48)):
    pgw.clump(V(_kx + ox_, _kz + oz_, gz(_kx + ox_, _kz + oz_) + rr_ * 0.55), (rr_, rr_, rr_ * 0.8), 9, 0.7,
              park_tone(M_LENTISK), random.Random(4040))
city_objs.append(pgw.finish('ParkGuell_plants'))
north['park']['key'] = list(G['key'])

# ------------------------------------------------------------------ the woods (round 24, the user: "The forest up the hill
# should be deep. At parts you should be able to see through and then over some trees to see the city and beach…
# the hill forest should be inaccessible outside of the ball part, which is more open"): the eastern wood's own trees
# (forest.py's species: holm oaks, Aleppo and stone pines, cork oaks, the odd cypress), scattered at random rather than
# one to a tile, close together; shrubs between them; nothing within reach of the path but the verge (the railing and
# the banks keep her on it). Five viewpoints where the slope below the path is left to low scrub, so from the bench
# there you see over the treetops to the city and the sea. Each tree is made twice, in full and as a light far
# version (as in the eastern wood), in chunks, so the game draws the full ones only near; the slopes nobody walks
# (behind the funfair, the hilltop) have only far versions.
lx_c, lz_lo, lz_hi = N.CABLE_LOW[0], N.CABLE_TOP[1], N.CABLE_LOW[1]
GR_ZONE = N.GRACIA_ZONE
# (x, z) on the path, and the way to look (towards La Rambla and the sea)
VIEWPOINTS = N.VIEWPOINTS          # (round 35: in north.py, whose ground makes a bay for each bench — PATH_RULES C4)
VIEW_DIR = Vector(N.VIEW_DIR).normalized()
VIEW_HALF, VIEW_R = math.radians(34), 48.0


def in_view(x, z):
    for (vx, vz) in VIEWPOINTS:
        d = Vector((x - vx, z - vz))
        if d.length < VIEW_R and d.length > 0.01 and d.normalized().dot(VIEW_DIR) > math.cos(VIEW_HALF):
            return True
    return False


def near_bench(x, z):
    # (round 35, PATH_RULES C4: the bench itself, in its bay, and the view in front of it kept clear — the funicular
    # bend's bench, on the hairpin's inside, sat in a thicket)
    if any(math.hypot(x - vx, z - vz) < 2.5 for (vx, vz) in VIEWPOINTS):
        return True
    if N.WORK_SITE and math.hypot(x - N.WORK_SITE[0][0], z - N.WORK_SITE[0][1]) < 4.2:
        return True                                    # (the workmen's site's bay: clear, C4)
    for (bx, bz, _, fw) in N.bench_spots():
        dx, dz = x - bx, z - bz
        if math.hypot(dx, dz) < 3.0:
            return True
        ahead = dx * fw[0] + dz * fw[1]
        if 0.0 < ahead < 9.0 and abs(dx * fw[1] - dz * fw[0]) < 1.5 + ahead * 0.5:
            return True
    return False


def in_glade(x, z):
    """The ball's glade: below the top leg, above the leg below, between its two fences."""
    if not (GLADE_X[0] < x < GLADE_X[1]):
        return False
    up = min((p for p in pts[TOP_LEG_I:]), key=lambda p: abs(p[0] - x))
    lo = min(LOWER_LEG, key=lambda p: abs(p[0] - x))
    return lo[1] - 1.0 > z > up[1] + 1.0


def east_lawn(x, z):
    """(Round 36, the user: the grass above the old rock strip should not be "liminal") the band of lawn between the
    hill's wood and the eastern wood's edge, east of Gràcia's wood-side footpath and its wall: neither planted it."""
    return x > N.GRACIA_WALL_X + 2.4 and -130.0 <= z < -118.8


def wood_density(x, z):
    f = N.FAIR
    if f[0] - 4 <= x <= f[2] + 4 and f[1] - 4 <= z <= f[3] + 4:
        return 0.0
    if z > N.FOOT_Z - 2:
        return 0.0
    if GR_ZONE[0] < x < GR_ZONE[2] and GR_ZONE[1] < z < GR_ZONE[3]:
        return 0.0
    pr = N.park_r(x, z)
    if pr < 1.08:
        return 0.0
    # (round 40, the user: "bring the forest and foliage a bit lower to the funicular station") the clear ride either side of
    # the line narrows near the station, the wood coming down to its back corners
    if abs(x - lx_c) < (8.0 if z < lz_hi - 18.0 else 5.6) and lz_lo - 4 < z < lz_hi + 6:
        return 0.0
    if x > 80 and z > -130:
        return 0.0                                      # (the eastern wood's own ground)
    if 100.0 < x < 195.0 and -240.0 < z < -132.0 and N.road_level(x, z)[0] < N.ROAD_W / 2 + 1.5:
        return 0.0                                      # (round 25: the Carretera del Carmel)
    d, ph = N.path_near(x, z)
    if d < (N.EDGE + N.VERGE + 0.9 if N.height(x, z) > ph else 2.6):
        return 0.0                                      # (round 25: the green strip on the uphill side stays open)
    if near_bench(x, z):
        return 0.0
    if math.hypot(x - N.BALL[0], z - N.BALL[1]) < 2.4:
        return 0.0                                      # (round 25: room round the ball; its own tree is planted apart)
    if pr < 1.6:
        return 0.4                                      # the thinner wood round the park
    return 1.0


HILL_BLOBS = []         # (round 25) every crown and bush on the hill, as rough ellipsoids, for the floor's light (hill_light.py)


class HillBoth:
    """A tree made in full (near) and as the eastern wood's far version (far); near may be None (far only)."""
    def __init__(self, near, far, k):
        self.near, self.far, self.k = near, far, k

    def shell(self, c, radii, count, size, m, rng, depth=(0.72, 1.0)):
        HILL_BLOBS.append((c.copy(), radii, size, m.name))
        if self.near is not None:
            self.near.shell(c, radii, count, size * self.k, m, rng, depth)
        self.far.shell(c, radii, max(3, count // 5), size * 2.1, m, random.Random(int(c.x * 97 + c.y * 31)), depth)

    def clump(self, c, radii, count, size, m, rng, up_bias=0.0):
        HILL_BLOBS.append((c.copy(), radii, size, m.name))
        if self.near is not None:
            self.near.clump(c, radii, count, size * self.k, m, rng, up_bias)

    def cone(self, M, segs, r1, r2, depth, m, smooth=True, caps=True):
        if self.near is not None:            # (round 25: the far versions are the bushy tops only)
            self.near.cone(M, segs, r1, r2, depth, m, smooth, caps)


hill_chunks = {}


class ParkBoth(HillBoth):
    """(round 34) a Park Güell tree: as HillBoth, its leaves toned down (world2d.py park_tone); the light map still
    reads each crown by its own kind's name."""
    def shell(self, c, radii, count, size, m, rng, depth=(0.72, 1.0)):
        HILL_BLOBS.append((c.copy(), radii, size, m.name))
        m2 = park_tone(m)
        if self.near is not None:
            self.near.shell(c, radii, count, size * self.k, m2, rng, depth)
        self.far.shell(c, radii, max(3, count // 5), size * 2.1, m2, random.Random(int(c.x * 97 + c.y * 31)), depth)

    def clump(self, c, radii, count, size, m, rng, up_bias=0.0):
        HILL_BLOBS.append((c.copy(), radii, size, m.name))
        if self.near is not None:
            self.near.clump(c, radii, count, size * self.k, park_tone(m), rng, up_bias)


_NO_PLANTS = Cards() if 'Cards' in globals() else None      # (where a plant may not stand: built, never kept)


def hchunk(x, z, kind):
    # (round 41, the user: "this plant's growing out of the pavement") no plant on the funfair's paving or its edge wall
    if kind == 'plants' and _NO_PLANTS is not None and N.rect_d(x, z, N.FAIR) < 1.9:
        return _NO_PLANTS
    # (round 41, the user: "it should not have a bush halfway through it") nothing growing in a bench
    if kind == 'plants' and _NO_PLANTS is not None and any(math.hypot(x - b_[0], z - b_[1]) < 1.6 for b_ in N.bench_spots()):
        return _NO_PLANTS
    # ("And remove the bushes from that building site")
    if kind == 'plants' and _NO_PLANTS is not None and N.WORK_SITE and \
            math.hypot(x - N.WORK_SITE[0][0], z - N.WORK_SITE[0][1]) < 4.6:
        return _NO_PLANTS
    key = (int(math.floor(x / 36.0)), int(math.floor(z / 36.0)), kind)
    if key not in hill_chunks:
        hill_chunks[key] = MB(uv=True) if kind in ('trunks', 'fartrunks', 'onlyfartrunks') else Cards()
    return hill_chunks[key]


HILL_MIX = [('holm', 5.0), ('aleppo', 3.0), ('stone_pine', 1.6), ('cork', 1.3), ('cypress', 0.5)]
HILL_SHRUBS = [(M_LENTISK, 3), (M_ARBUTUS, 2), (M_BROOM, 1.5), (M_ROSEMARY, 1.2)]
hr = random.Random(2424)
tree_pts = []
n_full = n_far = n_shrub = 0


def reach_d(x, z):
    """How far from anywhere she can stand (the path, the glade): trees further off are made lighter."""
    d, _ = N.path_near(x, z)
    return d


def west_wood(x, z):
    """(Round 41c, 02 #128b, the user: "the area to the west of the amusement park has no trees once you run past the first
    part… Just pad it out") the wood west of the funfair, uphill of the path's top leg, out to the walk box's edge: she
    can run into it, but past the fair's first 30 m its trees were the far version only (tops, no trunks) or the light
    one, and past z -300 nothing grew under them. Now whole trees and the glade's undergrowth (planted after the hill's
    own pass, with their own random numbers, 02 #130)."""
    if not (-236.0 < x < N.FAIR[0] and -334.0 < z < -262.0):
        return False
    up = min(pts[TOP_LEG_I:], key=lambda p: abs(p[0] - x))
    return z < -280.0 if x < -207.0 else z < up[1] - 1.0          # (west of the hairpin: above its bend)


TOP_VIEW = [v_ for v_ in VIEWPOINTS if v_[1] < -270.0]


def top_lookout(x, z):
    """(Round 41c, 02 #59 changed, the user from the Ferris wheel: "it looks like a low-level forest. Could you make a full
    forest like the other ones?… There should be a canopy") the slope below the top bend's lookout, between the top leg
    and the leg below: she walks into it from the glade and from the bench, so its trees are full size, not the
    lookouts' low ones (the bench's own clearing stays, near_bench)."""
    for (vx, vz) in TOP_VIEW:
        d = Vector((x - vx, z - vz))
        if 0.01 < d.length < VIEW_R and d.normalized().dot(VIEW_DIR) > math.cos(VIEW_HALF):
            return True
    return False


west_trees = []         # (x, z, kind, size): the trees west_wood makes whole, in the hill pass's own places
_WEST_SINK = (Cards(), MB(uv=True)) if 'SPECIES' in globals() else None     # (their old light versions: built, never kept)


if 'SPECIES' in globals():
    STEP_ = 1.6
    zi = -345.0
    while zi < -100.0:
        xi = -246.0
        while xi < 238.0:                                   # (round 26: the hill east of the park was bare lawn;
                                                            #  round 28: on to the grid's east edge — the slope above the
                                                            #  Carmel road showed as a bare striped hill from the gates)
            x, z = xi + hr.uniform(0, STEP_), zi + hr.uniform(0, STEP_)
            xi += STEP_
            Xt, Yt = x / T + OX, z / T + OY
            if not in_north(int(math.floor(Xt)), int(math.floor(Yt))):
                continue
            dens = wood_density(x, z)
            # (a tree every 2.9 m or so: deep; the candidates are every 1.6 m)
            if dens <= 0.0 or hr.random() > dens * (STEP_ * STEP_) / (2.9 * 2.9):
                continue
            g_ = gz(x, z)
            sp = pick(HILL_MIX, hr)
            s_ = hr.uniform(0.9, 1.3)
            if in_view(x, z):
                # (round 25, the user: "The look out points should not have big clearings below, the trees should simply
                # be lower to allow Sandra to peek through") low, round trees below the viewpoints
                sp = hr.choice(('holm', 'holm', 'olive', 'cork'))
                s_ = hr.uniform(0.5, 0.68)
            glade_ = in_glade(x, z)
            if glade_ and math.hypot(x - N.BALL[0], z - N.BALL[1]) < 14.0 and hr.random() < 0.8:
                sp = 'holm'                                 # (round 25: dark holm oaks round the ball, its floor in shade)
            base = V(x, z, g_ - 0.05)
            far_only = z < -300.0 or (x > 0.0 and z < -280.0) or (x > 198.0 and z < -150.0)
            # (round 41, the user at the funfair's edges: "It looks like there's leaves with no tree trunks, and also there
            # should be tree trunks up around the back of it too… so that she can't see what's past there": the wood
            # behind and beside it was the far version only, drawn faint and without trunks close to — in full there)
            if N.rect_d(x, z, N.FAIR) < 30.0:
                far_only = False
            if far_only:
                DET[0] = 0.4
                leaves = HillBoth(None, hchunk(x, z, 'onlyfar'), 1.0)
                trunks = HillBoth(None, hchunk(x, z, 'onlyfartrunks'), 1.0)
                n_far += 1
            else:
                rd = reach_d(x, z)
                prk = N.park_r(x, z)
                DET[0] = 1.0 if (rd < 14.0 or prk < 1.3) else (0.6 if (rd < 35.0 or prk < 1.8) else 0.4)
                kk = 1.0 / math.sqrt(DET[0]) if DET[0] < 1.0 else 1.0
                leaves = HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), kk)
                trunks = HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0)
                n_full += 1
            look_ = in_view(x, z) and top_lookout(x, z)
            redo_ = ((far_only or DET[0] < 1.0) and west_wood(x, z)) or look_
            if redo_:
                # (02 #128b: made whole below; the light version still built, into nothing, so the random numbers
                # run on as before and every other tree on the hill stays where it was, 02 #130)
                leaves = HillBoth(None if far_only else _WEST_SINK[0], _WEST_SINK[0], leaves.k)
                trunks = HillBoth(None if far_only else _WEST_SINK[1], _WEST_SINK[1], 1.0)
                nb_ = len(HILL_BLOBS)
            SPECIES[sp](trunks, leaves, base, hr, s_)
            if redo_:
                del HILL_BLOBS[nb_:]
                west_trees.append((x, z, None if look_ else sp, s_))
            tree_pts.append((x, z))
            # (where she may walk off the path: the trunks are solid; round 41, the user: "The trees in the forest are also
            # I can cycle through them… Aren't they meant to be solid?" — every trunk within 12 m of the path too, where
            # she or the bike can get to)
            # (and round 41: on the hill's walkable foot, below the wood's edge line — the new lawn west of the park)
            if redo_:
                pass                                      # (its trunk made solid with the whole tree, below)
            elif glade_ or (not far_only and N.path_near(x, z)[0] < 12.0) or \
                    (-61.0 < x < 60.0 and z < -102.0 and N.park_r(x, z) >= 1.0 and N.wood_edge_side(x, z) < 1.0):
                scene['trees'].append([round(x, 3), round(z, 3)])
                scene.setdefault('forest_trees', []).append([round(x, 3), round(z, 3)])
        zi += STEP_
    # (round 36) the lawn east of Gràcia's footpath (east_lawn): park trees standing loose, in twos and threes, and
    # low shrubs between — its own random numbers, so the hill's trees and shrubs stay exactly where they were
    lrng_ = random.Random(3636)
    DET[0] = 1.0
    zi = -130.0
    while zi < -118.8:
        xi = N.GRACIA_WALL_X + 2.4
        while xi < 200.0:
            x, z = xi + lrng_.uniform(0, 4.2), zi + lrng_.uniform(0, 4.2)
            xi += 4.2
            if not east_lawn(x, z) or lrng_.random() > 0.55:
                continue
            sp = pick([('stone_pine', 2.0), ('holm', 2.0), ('olive', 1.5), ('carob', 1.0), ('aleppo', 1.0)], lrng_)
            SPECIES[sp](HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0),
                        HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), 1.0),
                        V(x, z, gz(x, z) - 0.05), lrng_, lrng_.uniform(0.85, 1.2))
            tree_pts.append((x, z))
            scene['trees'].append([round(x, 3), round(z, 3)])
            n_full += 1
        zi += 4.2
    zi = -130.0
    while zi < -118.8:
        xi = N.GRACIA_WALL_X + 2.4
        while xi < 200.0:
            x, z = xi + lrng_.uniform(0, 2.2), zi + lrng_.uniform(0, 2.2)
            xi += 2.2
            if not east_lawn(x, z) or lrng_.random() > 0.3 or any(math.hypot(x - tx_, z - tz_) < 1.6 for tx_, tz_ in tree_pts[-60:]):
                continue
            rr = lrng_.uniform(0.45, 0.9)
            hchunk(x, z, 'plants').clump(V(x, z, gz(x, z) + 0.1 + rr * 0.35), (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7,
                                         pick(HILL_SHRUBS, lrng_), lrng_)
        zi += 2.2
    # (round 41, the user: "put foliage on the ground around the trees that are right next to the amusement park area.
    # It's very plain underneath the trees") low shrubs round the feet of the trees within 25 m of the funfair, clear of
    # the fair itself, the paths, the funicular's line and every built floor — its own random numbers
    frng_ = random.Random(4141)
    _fcab = [(p_[0], p_[1]) for p_ in north['cable']['pts']]
    n_fu = 0
    for (tx_, tz_) in list(tree_pts):
        fd_ = N.rect_d(tx_, tz_, N.FAIR)
        if fd_ < 1.0 or fd_ > 25.0:
            continue
        for k_ in range(3):
            a_, r_ = frng_.uniform(0.0, 2.0 * math.pi), frng_.uniform(0.6, 2.4)
            x, z = tx_ + math.cos(a_) * r_, tz_ + math.sin(a_) * r_
            rr = frng_.uniform(0.35, 0.8)
            sh_ = pick(HILL_SHRUBS, frng_)
            if N.rect_d(x, z, N.FAIR) < 1.5 or N.path_near(x, z)[0] < 2.2 or \
                    any(math.hypot(x - cx_, z - cz_) < 4.0 for cx_, cz_ in _fcab) or \
                    any(f_[0] - 0.5 <= x <= f_[2] + 0.5 and f_[1] - 0.5 <= z <= f_[3] + 0.5 for f_ in scene.get('flats', [])):
                continue
            hchunk(x, z, 'plants').clump(V(x, z, gz(x, z) + 0.1 + rr * 0.35), (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, sh_, frng_)
            n_fu += 1
    print('NORTH fair understory: %d clumps' % n_fu)
    # (round 39, the user: "make the forest around it like the one further down the hill, also with the process where
    # you look at how the sun moves and use that as the shadows") the closed hill east of Gràcia (N.gracia_hill) as
    # thick as the eastern wood below it: trees topped up to one every 2.6 m or so wherever the hill's own pass left it
    # thin (0.4 within 24 m of the park's wall, nothing on the old east lawn) — none within 2 m of a tree already there
    # — and thick undergrowth between, clear of the fences and the wood's edge. Its own random numbers, so nothing else
    # on the hill moves (02 #130). Every crown and bush goes into HILL_BLOBS, so the floor's light map below
    # (hill_light.py: the sun across the day and the open sky) shades it — lawn in the sun, tufts in the half shade,
    # needles deep under the holm oaks (02 #74, #75).
    ghr_ = random.Random(3939)

    def gh_reach(x_, z_):
        """How far from where she can stand: the footpath's fence, the road's fence, the eastern wood's edge."""
        d_ = N._seg_near(x_, z_, N.CARMEL_ROAD)[0] - 3.0
        if z_ > -146.0:
            d_ = min(d_, x_ - N.GRACIA_WALL_X)
        return min(d_, N.GH_EDGE_Z - z_)
    _gb = {}
    for (tx_, tz_) in tree_pts:
        if N.gracia_hill(tx_, tz_):
            _gb.setdefault((int(tx_ // 2), int(tz_ // 2)), []).append((tx_, tz_))
    zi = -232.0
    while zi < N.GH_EDGE_Z:
        xi = N.GRACIA_WALL_X + 0.6
        while xi < 241.0:
            x, z = xi + ghr_.uniform(0, 1.6), zi + ghr_.uniform(0, 1.6)
            xi += 1.6
            if not N.gracia_hill(x, z) or ghr_.random() > (1.6 * 1.6) / (2.6 * 2.6) or gh_reach(x, z) < 1.4:
                continue
            bx_, bz_ = int(x // 2), int(z // 2)
            if any(math.hypot(x - tx_, z - tz_) < 2.0 for i_ in (-1, 0, 1) for j_ in (-1, 0, 1)
                   for tx_, tz_ in _gb.get((bx_ + i_, bz_ + j_), ())):
                continue
            _gb.setdefault((bx_, bz_), []).append((x, z))
            if x > 198.0 and z < -150.0:                     # (as the hill's own pass: far only, out past the rise)
                DET[0] = 0.4
                leaves = HillBoth(None, hchunk(x, z, 'onlyfar'), 1.0)
                trunks = HillBoth(None, hchunk(x, z, 'onlyfartrunks'), 1.0)
                n_far += 1
            else:
                DET[0] = 1.0 if gh_reach(x, z) < 14.0 else 0.6
                kk = 1.0 / math.sqrt(DET[0]) if DET[0] < 1.0 else 1.0
                leaves = HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), kk)
                trunks = HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0)
                n_full += 1
            SPECIES[pick(HILL_MIX, ghr_)](trunks, leaves, V(x, z, gz(x, z) - 0.05), ghr_, ghr_.uniform(0.9, 1.3))
            tree_pts.append((x, z))
        zi += 1.6
    zi = -232.0
    while zi < N.GH_EDGE_Z:
        xi = N.GRACIA_WALL_X + 0.6
        while xi < 205.0:                                    # (past x 198 the far-only wood: nobody sees under it)
            x, z = xi + ghr_.uniform(0, 1.7), zi + ghr_.uniform(0, 1.7)
            xi += 1.7
            if not N.gracia_hill(x, z) or ghr_.random() > 0.85:
                continue
            rr = min(ghr_.uniform(0.6, 1.15), gh_reach(x, z) - 0.3)     # (never over a fence or the wood's edge)
            if rr < 0.35:
                continue
            c = V(x, z, gz(x, z) + 0.1 + rr * 0.35)
            hchunk(x, z, 'plants').clump(c, (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, pick(HILL_SHRUBS, ghr_), ghr_)
            HILL_BLOBS.append((c.copy(), (rr, rr, rr * 0.6), 0.7, 'bush'))
            n_shrub += 1
        zi += 1.7
    # (round 40, the user: "add a few more trees and a bit of foliage? Just extend the forest lightly around the
    # funicular", rule 02 #128a) the wood keeps 8 m clear either side of the track (wood_density); a light fringe now
    # stands in the outer part of that strip, 5.8–8 m out (clear of the cabins), smaller trees with bushes between,
    # not by the two stations, the path or a bench. Its own random numbers, so nothing else on the hill moves (02 #130).
    frng_ = random.Random(4040)
    FR_Z0, FR_Z1 = N.FUNI_Z1 + 8.0, N.FUNI_Z0 - 12.0            # (from below the portal to above the lower station)

    def fringe_ok(x_, z_, near_):
        if not (FR_Z0 < z_ < FR_Z1) or not (near_ <= abs(x_ - lx_c) < 8.0):
            return False
        d_, ph_ = N.path_near(x_, z_)
        if d_ < (N.EDGE + N.VERGE + 0.9 if N.height(x_, z_) > ph_ else 2.6):
            return False
        return not (near_bench(x_, z_) or in_view(x_, z_))
    fr_trees = []
    zi = FR_Z0
    while zi < FR_Z1:
        for sd_ in (-1, 1):
            x, z = lx_c + sd_ * frng_.uniform(5.8, 7.6), zi + frng_.uniform(0, 4.5)
            if not fringe_ok(x, z, 5.8) or frng_.random() > 0.55:
                continue
            rd = reach_d(x, z)
            DET[0] = 1.0 if rd < 14.0 else (0.6 if rd < 35.0 else 0.4)
            kk = 1.0 / math.sqrt(DET[0]) if DET[0] < 1.0 else 1.0
            SPECIES[pick(HILL_MIX, frng_)](HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0),
                                           HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), kk),
                                           V(x, z, gz(x, z) - 0.05), frng_, frng_.uniform(0.75, 1.0))
            tree_pts.append((x, z))
            fr_trees.append((x, z))
            scene['trees'].append([round(x, 3), round(z, 3)])
            n_full += 1
        zi += 4.5
    DET[0] = 1.0
    zi = FR_Z0
    while zi < FR_Z1:
        for sd_ in (-1, 1):
            x, z = lx_c + sd_ * frng_.uniform(4.9, 7.8), zi + frng_.uniform(0, 2.4)
            if not fringe_ok(x, z, 4.9) or frng_.random() > 0.4 or \
                    any(math.hypot(x - tx_, z - tz_) < 1.5 for tx_, tz_ in fr_trees[-12:]):
                continue
            rr = frng_.uniform(0.4, 0.8)
            c = V(x, z, gz(x, z) + 0.1 + rr * 0.35)
            hchunk(x, z, 'plants').clump(c, (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, pick(HILL_SHRUBS, frng_), frng_)
            HILL_BLOBS.append((c.copy(), (rr, rr, rr * 0.6), 0.7, 'bush'))
            n_shrub += 1
        zi += 2.4
    print('NORTH funicular fringe: %d trees' % len(fr_trees))
    # the holm oak that stopped the ball, a big old one
    DET[0] = 1.0
    x, z = BALL_TREE
    SPECIES['holm'](HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0),
                    HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), 1.0), V(x, z, gz(x, z) - 0.05), random.Random(31), 1.3)
    tree_pts.append((x, z))
    scene['trees'].append([round(x, 3), round(z, 3)])
    scene.setdefault('forest_trees', []).append([round(x, 3), round(z, 3)])
    # (round 40, the user: "on the river bank that goes south between the river and the city, just add some bigger trees
    # there and some tufts of grass just to give it a bit more detail") the grass strip between the river and the city's
    # western pavement (x -171.5 to -158.5), from the hill's foot to the sand: a big pine or holm oak here and there,
    # never on the bridge's way, and tufts scattered between; their own random numbers (02 #130)
    brng_ = random.Random(4044)
    zb_ = -92.0
    n_bank = 0
    while zb_ < 132.0:
        if not (-16.0 < zb_ < 4.0):                                     # (the bridge across, z -9.9 to -3.3)
            xb_ = brng_.uniform(-167.5, -163.0)
            # (round 40, the user: "by large tree, I didn't mean the tallest, I meant generally the largest… trees that
            # give a lot of shade… Not the tall ones that look like palm trees") broad, low-crowned holm oaks and carobs
            sp_ = 'holm' if brng_.random() < 0.6 else 'carob'
            SPECIES[sp_](HillBoth(hchunk(xb_, zb_, 'trunks'), hchunk(xb_, zb_, 'fartrunks'), 1.0),
                         HillBoth(hchunk(xb_, zb_, 'leaves'), hchunk(xb_, zb_, 'farleaves'), 1.0),
                         V(xb_, zb_, gz(xb_, zb_) - 0.05), random.Random(4100 + n_bank), brng_.uniform(1.6, 1.9))
            tree_pts.append((xb_, zb_))
            scene['trees'].append([round(xb_, 3), round(zb_, 3)])
            n_bank += 1
        zb_ += brng_.uniform(12.0, 20.0)
    n_btuft = 0
    for _k in range(520):
        xt_, zt_ = brng_.uniform(-171.0, -159.2), brng_.uniform(-95.0, 136.0)
        if -11.0 < zt_ < -2.0:
            continue
        size = brng_.uniform(0.2, 0.34)
        c0 = V(xt_, zt_, gz(xt_, zt_) + size * 0.45)
        a0 = brng_.uniform(0, 3.14)
        for kf in range(3):
            rot = vertical(a0 + kf * 1.0472) @ Matrix.Rotation(brng_.uniform(-0.15, 0.15), 3, 'X')
            hchunk(xt_, zt_, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT, 0.35)
        n_btuft += 1
    print('NORTH river bank: %d big trees, %d tufts' % (n_bank, n_btuft))
    # (round 41c, 02 #119a, the user: "add some smaller trees and foliage along the river? On both sides? Just so it feels
    # less sparse"; then: "the ones I want you to add shouldn't be as orderly. Various distance between each other and
    # then various distance from the water… patches of mid-texture ground underneath it to the north"; from three
    # pictured mixes: "I think B, but move the trees slightly away from the water and then reduce the size of the
    # middle texture grass. Just have a few small spots") along both banks, between the big trees: small holm oaks with
    # a cypress now and then, at uneven gaps and uneven distances back from the water, a lentisk or strawberry tree by
    # some; under some, north of the trunk where their shade falls, a few small spots of the half shade's ground
    if True:
        mrng_ = random.Random(4171)
        n_mock = 0
        patch_mb = MB(uv=True)
        # (its own copy of the half shade's ground: the game turns ForestMid itself into the eastern wood's lit floor,
        # which out here paints lawn)
        M_RIVERSHADE = mat('RiverShadeMid', '#ffffff', 0.98, image=make_image('midshade_river', 128, 128, mid_fn))
        dry = lambda x, z, o: gz(x, z) > 0.0 and gz(x - o * 1.0, z) > -0.15      # (on the bank, a step clear of the water at -0.35)

        def mock_tree(x, z, sp, size):
            SPECIES[sp](HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0),
                        HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), 1.0),
                        V(x, z, gz(x, z) - 0.05), random.Random(int(x * 97 + z * 13)), size)
            tree_pts.append((x, z))
            scene['trees'].append([round(x, 3), round(z, 3)])

        def mock_bush(x, z, rr, m):
            if gz(x, z) < -0.05:
                return                                                        # (never in the water)
            c = V(x, z, gz(x, z) + 0.1 + rr * 0.35)
            hchunk(x, z, 'plants').clump(c, (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, m, mrng_)
            HILL_BLOBS.append((c.copy(), (rr, rr, rr * 0.6), 0.7, 'bush'))

        def mock_patch(cx, cz, rx, rz):
            # a ragged blob laid over the grass (a ring and a half ring, so it follows the bank's slope), 3 cm up
            n_ = 18
            ph_ = [mrng_.uniform(0, 6.28) for _ in range(3)]
            rim_ = []
            for k_ in range(n_):
                a_ = 6.2832 * k_ / n_
                w_ = 1.0 + 0.16 * math.sin(3 * a_ + ph_[0]) + 0.1 * math.sin(5 * a_ + ph_[1]) + 0.07 * math.sin(8 * a_ + ph_[2])
                rim_.append((cx + math.cos(a_) * rx * w_, cz + math.sin(a_) * rz * w_))
            mid_ = [((cx + px_) / 2, (cz + pz_) / 2) for px_, pz_ in rim_]
            P = lambda q_: V(q_[0], q_[1], gz_top(q_[0], q_[1]) + 0.04)
            U = lambda q_: (q_[0] / 3.0, q_[1] / 3.0)
            for k_ in range(n_):
                a0, a1 = rim_[k_], rim_[(k_ + 1) % n_]
                m0, m1 = mid_[k_], mid_[(k_ + 1) % n_]
                patch_mb.face([P((cx, cz)), P(m1), P(m0)], M_RIVERSHADE, normal=(0, 0, 1), uvs=[U((cx, cz)), U(m1), U(m0)])
                patch_mb.face([P(m0), P(m1), P(a1), P(a0)], M_RIVERSHADE, normal=(0, 0, 1), uvs=[U(m0), U(m1), U(a1), U(a0)])

        MIXES = [(-94.0, -17.0, [('holm', 3.0), ('cypress', 0.8)], [(M_LENTISK, 2), (M_ARBUTUS, 1.2)]),     # (not the bridge's way)
                 (5.0, 128.0, [('holm', 3.0), ('cypress', 0.8)], [(M_LENTISK, 2), (M_ARBUTUS, 1.2)])]
        for (za_, zb2_, tmix_, bmix_) in MIXES:
            for (edge_, out_) in ((-171.5, 1.0), (-181.5, -1.0)):           # (each bank: the water's edge, landward)
                z_ = za_ + mrng_.uniform(0.0, 4.0)
                while z_ <= zb2_:
                    x_ = edge_ + out_ * mrng_.uniform(2.5, 7.0)               # (a little back from the water, or well back)
                    while not dry(x_, z_, out_) and abs(x_ - edge_) < 9.0:
                        x_ += out_ * 0.5                                      # (where the river bends wider, further back)
                    if dry(x_, z_, out_) and min((math.hypot(x_ - px_, z_ - pz_) for px_, pz_ in tree_pts[-400:]), default=99.0) > 2.6:
                        sz_ = mrng_.uniform(0.55, 0.95)
                        mock_tree(x_, z_, pick(tmix_, mrng_), sz_)
                        if mrng_.random() < 0.6:                                 # (a few small spots, north of it)
                            for _sp in range(mrng_.randint(1, 3)):
                                rs_ = mrng_.uniform(0.35, 0.75)
                                mock_patch(x_ + mrng_.uniform(-1.3, 1.3), z_ - mrng_.uniform(0.5, 2.2), rs_, rs_ * mrng_.uniform(0.6, 0.9))
                        for _b in range(mrng_.choice([0, 1, 1, 2])):
                            mock_bush(x_ + mrng_.uniform(-2.0, 2.0), z_ + mrng_.uniform(-2.0, 2.0), mrng_.uniform(0.35, 0.6),
                                      pick(bmix_, mrng_))
                        n_mock += 1
                    if mrng_.random() < 0.3:                                 # (now and then a lone bush in a gap)
                        mock_bush(edge_ + out_ * mrng_.uniform(1.0, 5.0), z_ + mrng_.uniform(2.0, 4.0), mrng_.uniform(0.3, 0.55),
                                  pick(bmix_, mrng_))
                    z_ += mrng_.uniform(3.5, 11.0)
        city_objs.append(patch_mb.finish('RiverShadePatches'))
        print('NORTH river smaller trees: %d' % n_mock)
    if WEST_FIELDS:
        # (round 41, the user: "add trees along the riverbank on the other side of the river? Not too many. You should
        # be able to see through, but it should really look like there's a bit of nature there… The road across the
        # river should be a proper bitumen road that then curves off into the little forest out of view… the forest
        # isn't that deep… Then add some trees along the edges of the fields in various places") all far from where
        # she can go, so seen from across the river at the nearest: their own random numbers
        wrng_ = random.Random(4145)

        def wtree(x, z, sp, size, near):
            base = V(x, z, (gz(x, z) if x > GX0 + 1.0 else far_height(x, z)) - 0.05)
            if near:
                DET[0] = 0.6
                lv = HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), 1.0 / math.sqrt(0.6))
                tk = HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0)
            else:
                # (light, but whole: a lone tree's far version alone is the crown without its trunk, which showed as
                # leaves hanging in the sky over the fields)
                DET[0] = 0.4
                lv = HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), 1.0 / math.sqrt(0.4))
                tk = HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0)
            SPECIES[sp](tk, lv, base, random.Random(int(x * 131 + z * 17)), size)

        # the far bank: the grass strip between the water (x -181.5) and the fields, a tree or a small group now and then,
        # with gaps to see the fields through
        RIVER_W_MIX = [('holm', 2.0), ('aleppo', 1.5), ('stone_pine', 1.2), ('carob', 1.0)]
        n_wb = 0
        zb_ = -96.0
        while zb_ < 128.0:
            if not (-16.0 < zb_ < 3.0):                                 # (the bridge and the road's way)
                for _g in range(1 if wrng_.random() < 0.45 else wrng_.randint(2, 3)):
                    xw_, zw_ = wrng_.uniform(-190.0, -184.5), zb_ + wrng_.uniform(-4.0, 4.0)
                    wtree(xw_, zw_, pick(RIVER_W_MIX, wrng_), wrng_.uniform(1.2, 1.7), True)
                    n_wb += 1
            zb_ += wrng_.uniform(9.0, 17.0)             # (round 41, the user: "just add more trees along the riverbank")
        # the road: on from the bridge's west end as tarmac, then curving north into a small wood that hides it
        # (then: "keep continuing off into the distance through the fields": it bends through the little wood and comes
        # out onto z 0, where world2d.py's road runs on west)
        # (the user: "make sure the road connects to the bridge. Currently, there's a bit of grass there": it starts on
        # the deck just past the barrier, over the bank's grass where it lips onto the deck's end, and on up the bank)
        _rd = N.catmull([(-180.3, -6.6), (-184.0, -6.6), (-190.0, -6.6), (-198.0, -6.6), (-210.0, -3.5), (-222.0, 3.5), (-236.0, 6.0), (-250.0, 3.0),
                         (-262.0, 0.0), (-268.0, 0.0)], 6)
        road_w = MB(uv=True)
        for (ax_, az_), (bx_, bz_) in zip(_rd, _rd[1:]):
            L_ = math.hypot(bx_ - ax_, bz_ - az_) or 1e-6
            nx_, nz_ = -(bz_ - az_) / L_ * 3.0, (bx_ - ax_) / L_ * 3.0
            ha_, hb_ = max(gz_top(ax_, az_), 0.02) + 0.06, max(gz_top(bx_, bz_), 0.02) + 0.06
            road_w.face([V(ax_ + nx_, az_ + nz_, ha_), V(bx_ + nx_, bz_ + nz_, hb_), V(bx_ - nx_, bz_ - nz_, hb_),
                         V(ax_ - nx_, az_ - nz_, ha_)], M_ROAD, normal=(0, 0, 1), uvscale=4.0)
        city_objs.append(road_w.finish('WestRoad'))
        # the little wood the road turns into: not deep, but thick enough, seen from the bridge, to hide where it goes
        n_cp = 0
        _cp_pts = []
        for _k in range(140):
            xc_, zc_ = wrng_.uniform(-258.0, -208.0), wrng_.uniform(-24.0, 30.0)
            if math.hypot((xc_ + 234.0) * 0.8, zc_ - 3.0) > 22.0 + 5.0 * math.sin(xc_ * 0.2):
                continue
            if min(math.hypot(xc_ - px_, zc_ - pz_) for px_, pz_ in _rd) < 5.0:
                continue                                                # (clear of the road)
            if any(math.hypot(xc_ - a_, zc_ - b_) < 3.2 for a_, b_ in _cp_pts):
                continue                                                # (not trunk in trunk)
            _cp_pts.append((xc_, zc_))
            wtree(xc_, zc_, pick([('holm', 2.0), ('aleppo', 1.5), ('cork', 1.0), ('stone_pine', 1.0)], wrng_),
                  wrng_.uniform(1.1, 1.6), True)
            n_cp += 1
        # trees along some of the fields' edges (the patchwork's own rectangles, as laid on the ground), far-only
        n_fe = 0
        for (px0, py0, px1, py1) in _PLOTS:
            for (ex0, ey0, ex1, ey1) in ((px0, py0, px1, py0), (px0, py0, px0, py1)):
                if wrng_.random() > 0.5:
                    continue
                for ti in range(-3, 1):                                 # (the picture repeats every 380 m)
                    for tj in range(-1, 2):
                        ax_, bx_ = (ex0 / 256.0 + ti) * 380.0, (ex1 / 256.0 + ti) * 380.0
                        az_, bz_ = -(ey0 / 256.0 + tj) * 380.0, -(ey1 / 256.0 + tj) * 380.0
                        L_ = math.hypot(bx_ - ax_, bz_ - az_)
                        t_ = wrng_.uniform(0.0, 12.0)
                        while t_ < L_:
                            x_ = ax_ + (bx_ - ax_) * t_ / L_
                            z_ = az_ + (bz_ - az_) * t_ / L_
                            ok_ = (x_ < FIELD_BANK_X - 6.0 and -95.0 < z_ < 130.0 and west_field_ground(x_, z_)) if x_ > GX0 + 1.0 \
                                else (x_ > -1150.0 and west_plain(x_, z_, far_height(x_, z_)) and abs(z_) > 6.0
                                      and abs(x_ - 380.0 * round(x_ / 380.0)) > 6.0)          # (off the roads)
                            if ok_ and wrng_.random() < 0.8:
                                wtree(x_, z_, pick([('holm', 2.0), ('cypress', 1.5), ('stone_pine', 1.2), ('olive', 1.0)], wrng_),
                                      wrng_.uniform(1.2, 1.6), False)
                                n_fe += 1
                            t_ += wrng_.uniform(10.0, 18.0)
        DET[0] = 1.0
        print('WEST bank: %d trees, road wood %d, field edges %d' % (n_wb, n_cp, n_fe))
    # shrubs between the trees, thick (the wood's floor is never bare), lower and sparser in the viewpoints' scrub
    # (round 25, the user: "Put thicker undergrowth in the forest in the hills… thick undergrowth so you are present and
    # not far away", like the eastern wood: closer shrubs, on the banks too; ferns and grass tufts on the floor by the
    # light; the green strip along the path's uphill side kept open)
    grng_ = random.Random(2525)
    farng_ = random.Random(4042)          # (round 40: the far hill's own, so nothing planted before moves, 02 #130)
    n_fern = n_tuft = n_far = 0
    zi = -300.0
    SH_ = 1.7
    while zi < -100.0:
        xi = -246.0
        while xi < 205.0:
            x, z = xi + hr.uniform(0, SH_), zi + hr.uniform(0, SH_)
            xi += SH_
            if not in_north(int(math.floor(x / T + OX)), int(math.floor(z / T + OY))):
                continue
            d, ph = N.path_near(x, z)
            if d > 60.0:
                # (round 40, the user: "that entire hill should have foliage right along it. North of the [Eixample]…
                # Currently, the ground is blank") beyond sight of the path the wood's floor was bare under its trees:
                # shrubs there too, sparser, and a fern or a tuft at each
                if wood_density(x, z) <= 0.0 or farng_.random() > 0.38 * wood_density(x, z):
                    continue
                rr = farng_.uniform(0.6, 1.2)
                c = V(x, z, gz(x, z) + 0.1 + rr * 0.35)
                hchunk(x, z, 'plants').clump(c, (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, pick(HILL_SHRUBS, farng_), farng_)
                HILL_BLOBS.append((c.copy(), (rr, rr, rr * 0.6), 0.7, 'bush'))
                fx, fz = x + farng_.uniform(-1.0, 1.0), z + farng_.uniform(-1.0, 1.0)
                g0 = gz(fx, fz)
                if farng_.random() < 0.5:
                    a0 = farng_.uniform(0, 6.28)
                    size = farng_.uniform(0.45, 0.7)
                    for kf in range(farng_.randint(5, 7)):
                        rot = vertical(a0 + kf * 1.0 + farng_.uniform(-0.25, 0.25)) @ Matrix.Rotation(farng_.uniform(0.55, 0.95), 3, 'X')
                        hchunk(fx, fz, 'plants').card(V(fx, fz, g0) + rot @ Vector((0, size / 2, 0)), size * farng_.uniform(0.85, 1.1), rot,
                                                      V(fx, fz, g0) - Vector((0, 0, size * 0.5)), M_FERN, 0.35)
                else:
                    size = farng_.uniform(0.22, 0.34)
                    c0 = V(fx, fz, g0 + size * 0.45)
                    a0 = farng_.uniform(0, 3.14)
                    for kf in range(3):
                        rot = vertical(a0 + kf * 1.0472) @ Matrix.Rotation(farng_.uniform(-0.15, 0.15), 3, 'X')
                        hchunk(fx, fz, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT, 0.35)
                n_far += 1
                continue
            up_ = N.height(x, z) > ph
            if d < (N.EDGE + N.VERGE + 0.2 if up_ else 1.9):
                continue
            if abs(x - lx_c) < 4.6 and lz_lo - 4 < z < lz_hi + 6:
                continue                    # (round 30: the viewpoint's cone sweeps across the funicular now —
                                            #  never a bush on the line's bed or its ballast shoulders)
            view = in_view(x, z)
            glade = False                   # (round 25: the ball's glade is wood now, its undergrowth as thick)
            if math.hypot(x - N.BALL[0], z - N.BALL[1]) < 2.6:
                continue                    # (nothing to hide the ball)
            if near_bench(x, z) or (wood_density(x, z) <= 0.0 and not (view or glade)):
                # (but the bank above the strip: shrubs on it — round 30, the user: not at the path's foot,
                # which stays open grass where the path comes down to join the pavement)
                if not (up_ and d < N.EDGE + N.VERGE + 2.5 and z < N.FOOT_Z - 4.0):
                    continue
            if hr.random() > (0.3 if glade else (0.5 if view else 0.95)):
                continue
            rr = hr.uniform(0.35, 0.6) if (view or glade) else hr.uniform(0.7, 1.35)
            rr = min(rr, (d - 1.5) / 1.15)                    # (round 35, PATH_RULES A5: its crown never over the path)
            if rr < 0.3:
                continue
            c = V(x, z, gz(x, z) + 0.1 + rr * 0.35)
            hchunk(x, z, 'plants').clump(c, (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, pick(HILL_SHRUBS, hr), hr)
            HILL_BLOBS.append((c.copy(), (rr, rr, rr * 0.6), 0.7, 'bush'))
            n_shrub += 1
            # the floor round it, within sight of the path: a fern or two in the shade, tufts of grass where it's lighter
            if d < 30.0 and not glade:
                for _k in range(2):
                    fx, fz = x + grng_.uniform(-0.9, 0.9), z + grng_.uniform(-0.9, 0.9)
                    if N.path_near(fx, fz)[0] < (N.EDGE + N.VERGE + 0.2 if up_ else 1.9):
                        continue
                    if math.hypot(fx - N.BALL[0], fz - N.BALL[1]) < 2.2:
                        continue
                    g0 = gz(fx, fz)
                    if grng_.random() < 0.6:
                        a0 = grng_.uniform(0, 6.28)
                        size = grng_.uniform(0.45, 0.7)
                        for kf in range(grng_.randint(5, 7)):
                            rot = vertical(a0 + kf * 1.0 + grng_.uniform(-0.25, 0.25)) @ Matrix.Rotation(grng_.uniform(0.55, 0.95), 3, 'X')
                            c0 = V(fx, fz, g0)
                            hchunk(fx, fz, 'plants').card(c0 + rot @ Vector((0, size / 2, 0)), size * grng_.uniform(0.85, 1.1), rot,
                                                          c0 - Vector((0, 0, size * 0.5)), M_FERN, 0.35)
                        n_fern += 1
                    else:
                        size = grng_.uniform(0.22, 0.34)
                        c0 = V(fx, fz, g0 + size * 0.45)
                        a0 = grng_.uniform(0, 3.14)
                        for kf in range(3):
                            rot = vertical(a0 + kf * 1.0472) @ Matrix.Rotation(grng_.uniform(-0.15, 0.15), 3, 'X')
                            hchunk(fx, fz, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT, 0.35)
                        n_tuft += 1
        zi += SH_
    print('NORTH floor: %d ferns, %d tufts; far from the path: %d shrubs with their floor' % (n_fern, n_tuft, n_far))
    # (round 41c, 02 #128b) the wood west of the funfair made whole: its trees where the hill's pass put them, in full,
    # their trunks solid (she can run in there), and undergrowth as thick as the glade's — a shrub every 2 m or so
    # with a fern or a tuft or two at its foot, clear of the trunks and the path's own planting. Its own random numbers.
    wwr_ = random.Random(4143)
    DET[0] = 1.0
    _wt = {}
    for (x, z, sp_, s_) in west_trees:
        if sp_ is None:                                 # (below the top lookout: the hill's own mix, full size)
            sp_, s_ = pick(HILL_MIX, wwr_), wwr_.uniform(0.9, 1.3)
        SPECIES[sp_](HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0),
                     HillBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), 1.0), V(x, z, gz(x, z) - 0.05), wwr_, s_)
        scene['trees'].append([round(x, 3), round(z, 3)])
        scene.setdefault('forest_trees', []).append([round(x, 3), round(z, 3)])
        _wt.setdefault((int(x // 2), int(z // 2)), []).append((x, z))
    n_ws = 0
    zi = -334.0
    while zi < -228.0:
        xi = -236.0
        while xi < -70.0:
            x, z = xi + wwr_.uniform(0, SH_), zi + wwr_.uniform(0, SH_)
            xi += SH_
            look_ = top_lookout(x, z)
            if not (west_wood(x, z) or look_) or wood_density(x, z) <= 0.0 or wwr_.random() > (0.55 if look_ else 0.8):
                continue
            if N.path_near(x, z)[0] < 9.0:
                continue                                # (the path's own verges and banks are planted already)
            if any(math.hypot(x - tx_, z - tz_) < 0.9 for i_ in (-1, 0, 1) for j_ in (-1, 0, 1)
                   for tx_, tz_ in _wt.get((int(x // 2) + i_, int(z // 2) + j_), ())):
                continue                                # (not in a trunk)
            rr = wwr_.uniform(0.35, 0.6) if (in_view(x, z) and not look_) else wwr_.uniform(0.7, 1.3)
            c = V(x, z, gz(x, z) + 0.1 + rr * 0.35)
            hchunk(x, z, 'plants').clump(c, (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, pick(HILL_SHRUBS, wwr_), wwr_)
            HILL_BLOBS.append((c.copy(), (rr, rr, rr * 0.6), 0.7, 'bush'))
            n_ws += 1
            for _k in range(2):
                fx, fz = x + wwr_.uniform(-1.0, 1.0), z + wwr_.uniform(-1.0, 1.0)
                g0 = gz(fx, fz)
                if wwr_.random() < 0.6:
                    a0 = wwr_.uniform(0, 6.28)
                    size = wwr_.uniform(0.45, 0.7)
                    for kf in range(wwr_.randint(5, 7)):
                        rot = vertical(a0 + kf * 1.0 + wwr_.uniform(-0.25, 0.25)) @ Matrix.Rotation(wwr_.uniform(0.55, 0.95), 3, 'X')
                        c0 = V(fx, fz, g0)
                        hchunk(fx, fz, 'plants').card(c0 + rot @ Vector((0, size / 2, 0)), size * wwr_.uniform(0.85, 1.1), rot,
                                                      c0 - Vector((0, 0, size * 0.5)), M_FERN, 0.35)
                else:
                    size = wwr_.uniform(0.22, 0.34)
                    c0 = V(fx, fz, g0 + size * 0.45)
                    a0 = wwr_.uniform(0, 3.14)
                    for kf in range(3):
                        rot = vertical(a0 + kf * 1.0472) @ Matrix.Rotation(wwr_.uniform(-0.15, 0.15), 3, 'X')
                        hchunk(fx, fz, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT, 0.35)
        zi += SH_
    _WEST_SINK[1].bm.free()
    print('NORTH west wood: %d trees made whole (%d below the top lookout), %d shrubs' %
          (len(west_trees), sum(1 for w_ in west_trees if w_[2] is None), n_ws))
    # (round 41, the user: "add foliage to the ground there… it looks bare") the lawn between the wood and the park's west
    # wall, above the town's top corner, which neither the wood (it stops 3 m short of the wall) nor the park planted:
    # tufts all over, patchy, ferns and the odd shrub towards the trees, nothing against the wall's foot
    wlr_ = random.Random(4141)
    n_wl = 0
    zi = -194.0
    while zi < -156.0:
        xi = 14.0
        while xi < 64.0:
            x, z = xi + wlr_.uniform(0, 1.1), zi + wlr_.uniform(0, 1.1)
            xi += 1.1
            pr_ = N.park_r(x, z)
            if pr_ < 1.0 + 0.9 / 40.0 or pr_ > 1.3 or N.wood_edge_side(x, z) > 0.5:
                continue
            if GR_ZONE[0] < x < GR_ZONE[2] and GR_ZONE[1] < z < GR_ZONE[3]:
                continue
            pk_ = 0.55 + 0.45 * math.sin(x * 0.13 + z * 0.09)
            if wlr_.random() > 0.85 * pk_:
                continue
            g0 = gz(x, z)
            r_ = wlr_.random()
            if r_ < 0.16 and pr_ > 1.0 + 2.0 / 40.0:
                rr = wlr_.uniform(0.45, 0.8)
                c = V(x, z, g0 + 0.1 + rr * 0.35)
                hchunk(x, z, 'plants').clump(c, (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, pick(HILL_SHRUBS, wlr_), wlr_)
                HILL_BLOBS.append((c.copy(), (rr, rr, rr * 0.6), 0.7, 'bush'))
            elif r_ < 0.28:
                a0 = wlr_.uniform(0, 6.28)
                size = wlr_.uniform(0.45, 0.65)
                for kf in range(wlr_.randint(5, 7)):
                    rot = vertical(a0 + kf * 1.0 + wlr_.uniform(-0.25, 0.25)) @ Matrix.Rotation(wlr_.uniform(0.55, 0.95), 3, 'X')
                    c0 = V(x, z, g0)
                    hchunk(x, z, 'plants').card(c0 + rot @ Vector((0, size / 2, 0)), size * wlr_.uniform(0.85, 1.1), rot,
                                                c0 - Vector((0, 0, size * 0.5)), M_FERN, 0.35)
            else:
                size = wlr_.uniform(0.2, 0.34)
                c0 = V(x, z, g0 + size * 0.45)
                a0 = wlr_.uniform(0, 3.14)
                for kf in range(3):
                    rot = vertical(a0 + kf * 1.0472) @ Matrix.Rotation(wlr_.uniform(-0.15, 0.15), 3, 'X')
                    hchunk(x, z, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT if wlr_.random() < 0.75 else M_TUFT2, 0.35)
            n_wl += 1
        zi += 1.1
    print('NORTH west lawn: %d plants' % n_wl)

    # (round 30, the user: "Add bits of foliage or grass leafs on any blank grass that is next to nature, some is
    # more sparse than others") the hill's open grass — the strips along the path, the viewpoints' fans, the
    # hairpins' knuckles, the bank at the foot — gets scattered grass tufts and the odd fern: thickest where a
    # wood stands a few metres off, thinning across the clearings, and patchy, so no lawn runs blank to the trees
    orng_ = random.Random(3030)
    ogr_ = random.Random(4043)            # (round 40: the far open hill's tufts)
    n_open = 0
    OT_ = 2.6
    zi = -300.0
    while zi < -94.0:
        xi = -246.0
        while xi < 205.0:
            x, z = xi + orng_.uniform(0, OT_), zi + orng_.uniform(0, OT_)
            xi += OT_
            if not in_north(int(math.floor(x / T + OX)), int(math.floor(z / T + OY))):
                continue
            f_ = N.FAIR
            if f_[0] - 4 <= x <= f_[2] + 4 and f_[1] - 4 <= z <= f_[3] + 4:
                continue
            if GR_ZONE[0] < x < GR_ZONE[2] and GR_ZONE[1] < z < GR_ZONE[3]:
                continue
            if N.park_r(x, z) < 1.6 or (x > 80 and z > -130):              # (the park and the eastern wood plant their own)
                continue
            if 100.0 < x < 195.0 and -240.0 < z < -132.0 and N.road_level(x, z)[0] < N.ROAD_W / 2 + 2.0:
                continue
            if abs(x - N.CABLE_LOW[0]) < 4.6 and N.FUNI_Z1 - 2.0 < z < N.FUNI_Z0 + 8.0:
                continue                                                   # (the funicular's bed and station)
            if wood_density(x, z) > 0.0:
                continue                                                   # (the wood's own floor is planted above)
            d, ph = N.path_near(x, z)
            # (the grassy ride the trees keep clear along the funicular borders wood on both sides for its whole
            # length, so it gets tufts too, even far from the walking path)
            on_funi_green = 4.6 <= abs(x - N.CABLE_LOW[0]) < 9.5 and N.FUNI_Z1 - 2.0 < z < N.FUNI_Z0 + 8.0
            if d < N.EDGE + 0.3:
                continue
            if d > 60.0 and not on_funi_green:
                # (round 40, the user: "Have some grass on the hill to the north of the city. It looks very plain. Just a
                # little bit of grass to break it up. The grasses that you had in the forest") the open hill far from the
                # path: a scattering of the wood's tufts, patchy; its own random numbers (02 #130)
                if ogr_.random() < 0.16 * (0.55 + 0.45 * math.sin(x * 0.11 + z * 0.07)):
                    size = ogr_.uniform(0.2, 0.34)
                    c0 = V(x, z, gz(x, z) + size * 0.45)
                    a0 = ogr_.uniform(0, 3.14)
                    for kf in range(3):
                        rot = vertical(a0 + kf * 1.0472) @ Matrix.Rotation(ogr_.uniform(-0.15, 0.15), 3, 'X')
                        hchunk(x, z, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT if ogr_.random() < 0.75 else M_TUFT2, 0.35)
                    n_open += 1
                continue
            if near_bench(x, z) or math.hypot(x - N.BALL[0], z - N.BALL[1]) < 2.4:
                continue
            near_wood = any(wood_density(x + ox_, z + oz_) > 0.0
                            for (ox_, oz_) in ((6.5, 0.0), (-6.5, 0.0), (0.0, 6.5), (0.0, -6.5)))
            # (round 31, the user: "still plain grass up the hill at the turns. Looks very liminal" — the grass
            # held in a hairpin's crook, with the path round two or three of its sides, grows its tussocks)
            knuckle = len(N.path_runs_near(x, z, 11.0)) >= 2
            pk_ = 0.55 + 0.45 * math.sin(x * 0.11 + z * 0.07)              # some patches sparser than others
            if knuckle:
                pk_ = max(pk_, 0.75)                                       # (round 31: a turn never lands in a
                                                                           #  sparse patch — the crooks stay broken up)
            p_ = (0.5 if near_wood else (0.45 if knuckle else 0.13)) * pk_
            if orng_.random() > p_:
                continue
            g0 = gz(x, z)
            if near_wood and orng_.random() < 0.12:                        # the odd fern right by the trees
                a0 = orng_.uniform(0, 6.28)
                size = orng_.uniform(0.45, 0.65)
                for kf in range(orng_.randint(5, 7)):
                    rot = vertical(a0 + kf * 1.0 + orng_.uniform(-0.25, 0.25)) @ Matrix.Rotation(orng_.uniform(0.55, 0.95), 3, 'X')
                    c0 = V(x, z, g0)
                    hchunk(x, z, 'plants').card(c0 + rot @ Vector((0, size / 2, 0)), size * orng_.uniform(0.85, 1.1), rot,
                                                c0 - Vector((0, 0, size * 0.5)), M_FERN, 0.35)
            else:
                size = orng_.uniform(0.2, 0.34)
                c0 = V(x, z, g0 + size * 0.45)
                a0 = orng_.uniform(0, 3.14)
                for kf in range(3):
                    rot = vertical(a0 + kf * 1.0472) @ Matrix.Rotation(orng_.uniform(-0.15, 0.15), 3, 'X')
                    hchunk(x, z, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT, 0.35)
            n_open += 1
        zi += OT_
    print('NORTH open grass: %d clumps' % n_open)
    # (round 40, the user: "add a bit of foliage along the grass … thinning as it gets closer to it", rule 02 #128a)
    # the grass either side of the funicular: tufts, the odd fern and low bush, thick by the wood's edge and thinning
    # out to bare grass by the track bed. Its own random numbers, so nothing else moves (02 #130).
    furng_ = random.Random(4041)
    n_funi = 0
    zi = N.FUNI_Z1 + 5.0
    while zi < N.FUNI_Z0 - 10.0:
        for sd_ in (-1, 1):
            for _k in range(6):
                dx_ = furng_.uniform(3.9, 8.6)
                x, z = lx_c + sd_ * dx_, zi + furng_.uniform(0, 1.2)
                t_ = min(1.0, (dx_ - 3.9) / 4.0)
                if furng_.random() > 0.8 * t_ * t_ * (3 - 2 * t_):        # (none at the bed, most at the wood's edge)
                    continue
                d_, ph_ = N.path_near(x, z)
                if d_ < N.EDGE + 0.3 or near_bench(x, z):
                    continue
                g0 = gz(x, z)
                r_ = furng_.random()
                if dx_ > 6.3 and r_ < 0.07:                                # a low bush, only out by the trees
                    rr = furng_.uniform(0.25, 0.45)
                    c = V(x, z, g0 + 0.05 + rr * 0.35)
                    hchunk(x, z, 'plants').clump(c, (rr, rr, rr * 0.6), 6, 0.6, pick(HILL_SHRUBS, furng_), furng_)
                    HILL_BLOBS.append((c.copy(), (rr, rr, rr * 0.6), 0.6, 'bush'))
                elif dx_ > 5.5 and r_ < 0.2:                               # the odd fern
                    a0 = furng_.uniform(0, 6.28)
                    size = furng_.uniform(0.4, 0.6)
                    c0 = V(x, z, g0)
                    for kf in range(furng_.randint(5, 7)):
                        rot = vertical(a0 + kf * 1.0 + furng_.uniform(-0.25, 0.25)) @ Matrix.Rotation(furng_.uniform(0.55, 0.95), 3, 'X')
                        hchunk(x, z, 'plants').card(c0 + rot @ Vector((0, size / 2, 0)), size * furng_.uniform(0.85, 1.1), rot,
                                                    c0 - Vector((0, 0, size * 0.5)), M_FERN, 0.35)
                else:                                                      # grass tufts
                    size = furng_.uniform(0.18, 0.32)
                    c0 = V(x, z, g0 + size * 0.45)
                    a0 = furng_.uniform(0, 3.14)
                    for kf in range(3):
                        rot = vertical(a0 + kf * 1.0472) @ Matrix.Rotation(furng_.uniform(-0.15, 0.15), 3, 'X')
                        hchunk(x, z, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT, 0.35)
                n_funi += 1
        zi += 1.2
    print('NORTH funicular grass: %d clumps' % n_funi)
    # (round 25: the ball's glade is wood now: no wildflower lawn, no lone pines)

    # (round 24) Park Güell planted as the real one is: stone pines, carobs and olives over its lawns, date palms along
    # its paths, bougainvillea against its wall, rosemary and lentisk, clumps of agave on the slopes, grass in tufts
    G_ = N.GUELL
    prng = random.Random(1906)
    ppts = []
    for P_ in N.PARK_PATHS:
        for (a_, b_) in zip(P_, P_[1:]):
            L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
            for k in range(int(L_) + 1):
                ppts.append((a_[0] + (b_[0] - a_[0]) * k / max(1, int(L_)), a_[1] + (b_[1] - a_[1]) * k / max(1, int(L_))))

    def park_pd(x, z):
        return min(math.hypot(x - px_, z - pz_) for (px_, pz_) in ppts)

    def park_clear(x, z, pad=1.5):
        for r in (G_['plaza'], G_['porch'], G_['stairs_r'], G_['hypostyle'], G_['square_r'], G_['museu_r'], G_['trias_r']):
            if r[0] - pad <= x <= r[2] + pad and r[1] - pad <= z <= r[3] + pad:
                return True
        for (lx_, lz_) in (G_['guarda'], G_['lodge']):
            if abs(x - lx_) < 5.0 and abs(z - lz_) < 4.5:
                return True
        if math.hypot(x - G_['calvari'][0], z - G_['calvari'][1]) < 5.5 or math.hypot(x - N.PARK_GATE[0], z - N.PARK_GATE[1]) < 6.0:
            return True
        # (round 25) the side stairs, Casa Larrard, the gardens' beds, the gates, the viaducts and the walks below them
        for r in list(G_['side_stairs']) + [G_['larrard_r'], G_['austria']]:
            if r[0] - pad <= x <= r[2] + pad and r[1] - pad <= z <= r[3] + pad:
                return True
        if any(math.hypot(x - gx_, z - gz_) < 5.0 for gx_, gz_ in G_['side_gates'].values()):
            return True
        if any(N._seg_near(x, z, line)[0] < 6.5 for line in N.VIADUCTS.values()):
            return True
        s_, t_, be_, fl_ = N.gallery_where(x, z)
        if -N.GALLERY['out'] - 3.2 < s_ < N.GALLERY['deck_in'] + 2.0 and be_ < 3.0:
            return True                                  # (round 34: the covered walk, its vault and its roof)
        # (round 34, the walk round: trees grew at the side stairs' tops, filling the view onto the square)
        if 83.0 <= x <= 129.0 and -199.0 <= z <= -174.0:
            return True
        # (round 33: the porch's face, its colonnade and the side stairs' feet seen from below, not through trunks)
        if G_['porch'][0] - 6.0 <= x <= G_['porch'][2] + 6.0 and G_['porch'][3] - 1.0 <= z <= G_['porch'][3] + 8.0:
            return True
        return False

    def pr_(x, z):
        return N.park_r(x, z)

    park_wood = N.park_wood

    PK_X0, PK_X1 = min(p[0] for p in N.PARK_WALL), max(p[0] for p in N.PARK_WALL)
    PK_Z0, PK_Z1 = min(p[1] for p in N.PARK_WALL), max(p[1] for p in N.PARK_WALL)

    PARK_MIX = [('stone_pine', 3.0), ('carob', 2.0), ('olive', 1.5), ('holm', 1.0), ('cypress', 0.6)]
    n_pt = n_pp = n_ps = n_pa = n_pg = 0
    zz_ = PK_Z0
    while zz_ < PK_Z1:
        xx_ = PK_X0
        while xx_ < PK_X1:
            # (round 34, the user's aerial view: the park under one canopy, the paths seen only in glimpses: closer set)
            x, z = xx_ + prng.uniform(0, 2.2), zz_ + prng.uniform(0, 2.2)
            xx_ += 2.2
            # (round 25, the user: "it feels very sparse": the woods between the paths fuller, as in the real park)
            # (round 33, the user: the whole park in shambles, the landscaping: one even scatter over a mown lawn.
            # Two kinds of ground now: the wood — the upper park round the carriage roads and a belt along the wall —
            # close-set, and the open lawns round the plaza, the porch, the square and the houses, a few fine trees)
            wd_ = park_wood(x, z)
            sp = pick(PARK_MIX, prng)
            # (round 33: an olive's or a holm oak's crown hung over the paths at her head's height: only the tall
            # pines and cypresses stand close to a path in the wood)
            near_ = 2.2 if (wd_ and sp in ('stone_pine', 'cypress')) else 3.2
            # (round 40, A5: from the drawn edge of every path, the Austria walks too — near_ was from a 3 m path's middle)
            if pr_(x, z) > 0.95 or park_clear(x, z) or path_edge_d(x, z) < near_ - 1.5 or prng.random() > (0.92 if wd_ else 0.18):
                continue
            DET[0] = 1.0
            leaves = ParkBoth(hchunk(x, z, 'leaves'), hchunk(x, z, 'farleaves'), 1.0)
            trunks = HillBoth(hchunk(x, z, 'trunks'), hchunk(x, z, 'fartrunks'), 1.0)
            SPECIES[sp](trunks, leaves, V(x, z, gz(x, z) - 0.05), prng, prng.uniform(1.0, 1.4))
            scene['trees'].append([round(x, 3), round(z, 3)])
            n_pt += 1
        zz_ += 2.2
    # date palms along the paths, now one side, now the other
    palm_mb, palm_fr = MB(uv=True), Cards()
    for pi_, P_ in enumerate(N.PARK_PATHS[:3]):
        acc_p, nxt = 0.0, 4.0
        for (a_, b_) in zip(P_, P_[1:]):
            L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
            while nxt < acc_p + L_:
                t = (nxt - acc_p) / L_
                dx_, dz_ = (b_[0] - a_[0]) / L_, (b_[1] - a_[1]) / L_
                sd = 1 if int(nxt / 9) % 2 else -1
                x, z = a_[0] + (b_[0] - a_[0]) * t - dz_ * sd * 2.6, a_[1] + (b_[1] - a_[1]) * t + dx_ * sd * 2.6
                nxt += prng.uniform(8.0, 12.0)
                if park_clear(x, z, 0.5) or pr_(x, z) > 0.92 or path_edge_d(x, z) < 0.6:     # (round 40: one stood on the Austria walk)
                    continue
                base = V(x, z, gz(x, z) - 0.05)
                h = prng.uniform(5.5, 8.0)
                bend = Vector((prng.uniform(-0.5, 0.5), prng.uniform(-0.5, 0.5), 0))
                prev = base
                for k in range(1, 6):
                    tt = k / 5
                    p3 = base + bend * tt * tt + Vector((0, 0, h * tt))
                    d3 = p3 - prev
                    palm_mb.cone(Matrix.Translation((p3 + prev) / 2) @ Vector((0, 0, 1)).rotation_difference(d3.normalized()).to_matrix().to_4x4(),
                                 7, 0.22 - 0.05 * tt, 0.2 - 0.05 * tt, d3.length + 0.05, M_PALM_TRUNK)
                    prev = p3
                palm_mb.sphere(Matrix.Translation(prev), 0.3, M_PALM_TRUNK, (8, 6))
                for k in range(13):
                    ang = k * 2 * math.pi / 13 + prng.uniform(-0.2, 0.2)
                    droop, length, width = prng.uniform(0.0, 0.5), prng.uniform(2.4, 3.0), 0.75
                    if M_PALM not in palm_fr.mats:
                        palm_fr.mats.append(M_PALM)
                    dd = Vector((math.cos(ang) * math.cos(droop), math.sin(ang) * math.cos(droop), -math.sin(droop)))
                    side = Vector((-math.sin(ang), math.cos(ang), 0)) * width / 2
                    b0_ = prev + Vector((0, 0, 0.1))
                    mid = b0_ + dd * length * 0.5 + Vector((0, 0, -length * 0.12))
                    tip = b0_ + dd * length + Vector((0, 0, -length * 0.35))
                    upv = dd.cross(side).normalized()
                    if upv.z < 0:
                        upv = -upv
                    for (q0, q1, u0, u1) in ((b0_, mid, 0.0, 0.5), (mid, tip, 0.5, 1.0)):
                        bi = len(palm_fr.verts)
                        for q, uv in ((q0 - side, (u0, 0)), (q1 - side, (u1, 0)), (q1 + side, (u1, 1)), (q0 + side, (u0, 1))):
                            palm_fr.verts.append(q)
                            palm_fr.nrm.append(upv)
                            palm_fr.uvs.append(uv)
                        palm_fr.faces.append((bi, bi + 1, bi + 2, bi + 3))
                        palm_fr.fmat.append(palm_fr.mats.index(M_PALM))
                scene['trees'].append([round(x, 3), round(z, 3)])
                n_pp += 1
            acc_p += L_
    city_objs.append(palm_mb.finish('ParkPalms'))
    city_objs.append(palm_fr.finish('Leaves_parkpalms'))
    # shrubs on the lawns and bougainvillea along the wall; agaves on the slopes; grass in tufts everywhere else
    pgrass = {}
    ag_mb = MB(uv=True)
    zz_ = PK_Z0
    while zz_ < PK_Z1:
        xx_ = PK_X0
        while xx_ < PK_X1:
            x, z = xx_ + prng.uniform(0, 1.2), zz_ + prng.uniform(0, 1.2)
            xx_ += 1.2
            r_ = pr_(x, z)
            if r_ > 0.95 or park_clear(x, z, 0.3):
                continue
            # (round 40, A5, the user: "The palm tree and foliage is in the path"): measured from the drawn edge of every
            # path laid (the Austria Gardens' walks, the gate paths and the road too, not only PARK_PATHS), each plant
            # kept its own size plus a margin off it
            pe_ = path_edge_d(x, z)
            if pe_ < 0.25:
                continue
            pd_ = pe_ + 1.25                             # (the thresholds below were from a 3 m path's middle)
            hg = gz(x, z)
            roll = prng.random()
            if r_ > 0.86 and roll < 0.12 and pe_ > 1.2:
                c = V(x, z, hg + 0.9)
                hchunk(x, z, 'plants').clump(c, (0.9, 0.9, 1.0), 14, 0.65, M_BOUG, prng)
                n_ps += 1
            elif pd_ > 2.4 and (roll < 0.075 or (roll < 0.3 and park_wood(x, z))):   # (round 33: thick under the wood)
                rr = prng.uniform(0.45, 0.85)
                hchunk(x, z, 'plants').clump(V(x, z, hg + 0.1 + rr * 0.35), (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7,
                                             park_tone(pick([(M_ROSEMARY, 2), (M_LENTISK, 2), (M_BROOM, 1)], prng)), prng)
                n_ps += 1
            elif pd_ > 3.2 and 0.075 <= roll < 0.085:
                for k in range(prng.randint(1, 3)):
                    agave(ag_mb, x + prng.uniform(-0.8, 0.8), z + prng.uniform(-0.8, 0.8), hg - 0.05, prng.uniform(0.8, 1.2), prng)
                    n_pa += 1
            elif roll < 0.16:                            # (round 28, the user: "less grass in the field")
                c = V(x, z, hg + 0.1)
                a0 = prng.uniform(0, 3.14)
                sz_ = prng.uniform(0.2, 0.34)
                gk = (int(math.floor(x / 20.0)), int(math.floor(z / 20.0)))
                if gk not in pgrass:
                    pgrass[gk] = Cards()
                for k in range(3):
                    rot = vertical(a0 + k * 1.0472) @ Matrix.Rotation(prng.uniform(-0.15, 0.15), 3, 'X')
                    pgrass[gk].card(c, sz_, rot, c - Vector((0, 0, sz_)), park_tone(M_TUFT if prng.random() < 0.75 else M_TUFT2), 0.35)
                n_pg += 1
        zz_ += 1.2
    city_objs.append(ag_mb.finish('Detail_parkagaves'))
    for (gx_, gz_), gc in pgrass.items():
        city_objs.append(gc.finish('Grass_park_%d_%d' % (gx_ + 50, gz_ + 50)))
    print('PARK trees %d, palms %d, shrubs %d, agaves %d, tufts %d' % (n_pt, n_pp, n_ps, n_pa, n_pg))
    fchunks.clear()
    for k, (trunks, crowns) in enumerate(fchunks.values()):
        city_objs.append(trunks.finish('ForestTrunks_np%d' % k))
        city_objs.append(crowns.finish('Leaves_forest_np%d' % k))
    names = {'trunks': 'ForestTrunks_n%d_%d', 'leaves': 'Leaves_forest_n%d_%d', 'farleaves': 'Leaves_far_n%d_%d',
             'fartrunks': 'ForestFar_n%d_%d', 'onlyfar': 'Leaves_hillfar_%d_%d', 'onlyfartrunks': 'HillFarTrunks_%d_%d',
             'plants': 'Plants_hill_%d_%d'}
    for (kx, kz, kind), ob in hill_chunks.items():
        if kind in ('fartrunks', 'onlyfartrunks'):
            ob.bm.free()
            continue
        city_objs.append(ob.finish(names[kind] % (kx + 50, kz + 50)))
print('NORTH woods: %d trees, %d far-only, %d shrubs' % (n_full, n_far, n_shrub))

# viewpoints: a bench on the path's uphill side, facing out over the city
M_BENCHWOOD = mat('HillBenchWood', '#8a6748', 0.85)
bench_mb = MB(uv=True)
for (bx, bz, _, fw_) in N.bench_spots():
    # (round 35, PATH_RULES C4: north.py places them — the uphill side, or a hairpin's inside — in a level bay)
    h_ = gz(bx, bz)
    fwd = Vector(fw_)                                   # (the way it faces: back over the path to the view)
    dv = Vector((fwd.y, -fwd.x))
    U_, F_ = (dv.x, -dv.y), (fwd.x, -fwd.y)
    c_ = V(bx, bz, h_ + 0.45)
    bench_mb.box(c_, U_, F_, 0.8, 0.2, 0.03, M_BENCHWOOD)                                       # the seat
    bench_mb.box(c_ + Vector((-fwd.x * 0.2, fwd.y * 0.2, 0.3)), U_, F_, 0.8, 0.025, 0.12, M_BENCHWOOD)   # the back
    for sd in (-0.65, 0.65):
        for fb in (-0.15, 0.15):
            bench_mb.box(V(bx + dv.x * sd + fwd.x * fb, bz + dv.y * sd + fwd.y * fb, h_ + 0.2), U_, F_, 0.04, 0.04, 0.25, M_BENCHWOOD)
        # (round 41c, the user: "this bench doesn't have anything holding up the backboard") an upright at each end of
        # the back, from the seat up through the board, just behind it
        bench_mb.box(V(bx + dv.x * sd - fwd.x * 0.235, bz + dv.y * sd - fwd.y * 0.235, h_ + 0.655), U_, F_, 0.035, 0.022, 0.225,
                     M_BENCHWOOD)
    north.setdefault('benches', []).append([round(bx, 2), round(bz, 2), round(math.atan2(fwd.x, fwd.y), 3)])
    scene.setdefault('benches', []).append([round(bx, 2), round(bz, 2), round(math.atan2(fwd.x, fwd.y), 3), round(h_ + 0.48, 3)])
city_objs.append(bench_mb.finish('HillBenches'))

# the five wildflowers for Alba's vase (round 26, the user: "There should only be 5 (the number for the mission). They
# should be spread across the entire path on the grass. Add other foliage here and there to the side of the path on the
# green, so that the flowers don't seem out of place"): one in each fifth of the path, at a random place in it, on the
# grass beside the path (the uphill strip; inside the railing where both sides fall); they grow back every second time
# she goes in and out (engine/game.gd). Above the workmen they can only be picked once the path is open (the user's pick).
fl_rng = random.Random(2626)
north['flowers'] = []
seg_ = PL / 5.0
for k_ in range(5):
    for _try in range(40):
        L_want = seg_ * k_ + fl_rng.uniform(0.12, 0.88) * seg_
        acc_ = 0.0
        for i in range(1, len(pts)):
            acc_ += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
            if acc_ >= L_want:
                break
        a0, b0 = pts[i - 1], pts[min(len(pts) - 1, i + 1)]
        dv = Vector((b0[0] - a0[0], b0[1] - a0[1])).normalized()
        nv = Vector((-dv.y, dv.x))
        lo_p, lo_m = low_side(pts[i][0], pts[i][1], nv.x, nv.y), low_side(pts[i][0], pts[i][1], -nv.x, -nv.y)
        side = -1 if lo_p else 1
        off_ = 0.95 if (lo_p and lo_m) else fl_rng.uniform(1.4, 1.9)
        # (round 34, the play-through: one lay 1.8 m off on what was really the falling side, past the railing, out of
        # her reach. Now just off the path's edge, on ground level with the path; else the other side; else inside
        # the path's own edge)
        hp_ = gz(pts[i][0], pts[i][1])
        for sd_try, off_try in ((side, off_), (-side, off_), (side, 0.95)):
            fx, fz = pts[i][0] + nv.x * sd_try * off_try, pts[i][1] + nv.y * sd_try * off_try
            if abs(gz(fx, fz) - hp_) < 0.35 and not low_side(pts[i][0], pts[i][1], nv.x * sd_try, nv.y * sd_try) or off_try < 1.0:
                break
        if N.path_near(fx, fz)[0] < 0.9 or near_bench(fx, fz) or (i >= TOP_LEG_I and GLADE_X[0] < fx < GLADE_X[1]):
            continue
        north['flowers'].append([round(fx, 2), round(fz, 2)])
        break
# low green things here and there on the grass beside the path (no flowers among them: only Alba's five are flowers)
verge_n = 0
for i in range(0, len(pts), 2):
    if fl_rng.random() > 0.3:
        continue
    a0, b0 = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
    dv = Vector((b0[0] - a0[0], b0[1] - a0[1])).normalized()
    nv = Vector((-dv.y, dv.x))
    side = -1 if low_side(pts[i][0], pts[i][1], nv.x, nv.y) else 1
    off_ = fl_rng.uniform(1.6, N.EDGE + N.VERGE - 0.5)
    fx, fz = pts[i][0] + nv.x * side * off_, pts[i][1] + nv.y * side * off_
    if N.path_near(fx, fz)[0] < 1.4 or near_bench(fx, fz) or any(math.hypot(fx - q[0], fz - q[1]) < 1.2 for q in north['flowers']):
        continue
    g0 = gz(fx, fz)
    kind_ = fl_rng.random()
    if kind_ < 0.45:                                 # a tuft of grass
        size = fl_rng.uniform(0.2, 0.32)
        c0 = V(fx, fz, g0 + size * 0.45)
        a_ = fl_rng.uniform(0, 3.14)
        for kf in range(3):
            rot = vertical(a_ + kf * 1.0472) @ Matrix.Rotation(fl_rng.uniform(-0.15, 0.15), 3, 'X')
            hchunk(fx, fz, 'plants').card(c0, size, rot, c0 - Vector((0, 0, size)), M_TUFT, 0.35)
    elif kind_ < 0.75:                               # a little fern
        a_ = fl_rng.uniform(0, 6.28)
        size = fl_rng.uniform(0.3, 0.45)
        for kf in range(5):
            rot = vertical(a_ + kf * 1.25) @ Matrix.Rotation(fl_rng.uniform(0.6, 0.95), 3, 'X')
            c0 = V(fx, fz, g0)
            hchunk(fx, fz, 'plants').card(c0 + rot @ Vector((0, size / 2, 0)), size, rot, c0 - Vector((0, 0, size * 0.5)), M_FERN, 0.35)
    else:                                            # a low clump of rosemary or lentisk
        rr = fl_rng.uniform(0.22, 0.38)
        c = V(fx, fz, g0 + rr * 0.3)
        hchunk(fx, fz, 'plants').clump(c, (rr, rr, rr * 0.6), 5, 0.7, M_ROSEMARY if fl_rng.random() < 0.5 else M_LENTISK, fl_rng)
    verge_n += 1
print('NORTH flowers: %d, verge plants %d' % (len(north['flowers']), verge_n))

# the floor's light map (as the eastern wood's, forest_light; round 25: by the sun across the day and the open sky
# through every crown and bush, hill_light.py, no longer by how many trees stand near): the lawn where the light is
# good, the half shade's moss, needles and leaves deep under the trees; and grass along the path's verges, in the glade
# and the viewpoints' scrub whatever the light. 1 m to a pixel.
# (round 31: d 250 → 256 — the map used to end at z -98, the hill foot's own ground, and the floor beyond its
# edge shaded wrong: a pale blue band along the pavement where the bushes used to hide it)
HL = {'x0': -262.0, 'z0': -480.0, 'w': 504, 'd': 388}     # (round 38: all of HillFloor, x -260.7…240.9, z -478.5…-100.7; it was stretched from the map's edge beyond x 32 and z -348 as straight streaks)
try:
    import numpy as _np, zlib as _zl, struct as _st
    import hill_light as HLT
    W_, D_ = HL['w'], HL['d']
    G0_ = _np.array([[gz(HL['x0'] + i + 0.5, HL['z0'] + j + 0.5) for i in range(W_)] for j in range(D_)], _np.float32)
    light = HLT.floor_light([(c.x, -c.y, c.z, r[0], r[1], r[2], sz, nm) for (c, r, sz, nm) in HILL_BLOBS + list(globals().get('BLOBS', []))], G0_, HL['x0'], HL['z0'])
    Gl_, Ml_ = HLT.steps(light, HL['x0'], HL['z0'])
    pd = _np.full((D_, W_), 99.0)
    for (x, z, _h) in pts:
        i0, j0 = int(x - HL['x0']), int(z - HL['z0'])
        for dj in range(-6, 7):
            for di in range(-6, 7):
                if 0 <= i0 + di < W_ and 0 <= j0 + dj < D_:
                    pd[j0 + dj, i0 + di] = min(pd[j0 + dj, i0 + di], math.hypot(di, dj))
    open_ = _np.zeros((D_, W_))
    for j in range(D_):
        for i in range(W_):
            x, z = HL['x0'] + i + 0.5, HL['z0'] + j + 0.5
            if pd[j, i] < VIEW_R and in_view(x, z):         # (round 25: not the ball's glade: wood now)
                open_[j, i] = 1.0
    # (round 25) green along the path's uphill side as far as the strip she may walk on, and just to the railing below
    reach_ = _np.full((D_, W_), 1.6)
    for j, i in zip(*_np.nonzero(pd < N.EDGE + N.VERGE + 2.0)):
        x, z = HL['x0'] + i + 0.5, HL['z0'] + j + 0.5
        if N.height(x, z) > N.path_near(x, z)[1]:
            reach_[j, i] = N.EDGE + N.VERGE
    verge = _np.clip(1.0 - (pd - reach_) / 2.0, 0, 1)
    green = _np.clip(_np.maximum(_np.maximum(Gl_, verge), open_ * 0.95), 0, 1)
    mid = _np.clip(_np.maximum(Ml_, verge), 0, 1)
    # (round 35, PATH_RULES C2, the user: "'hills' should be the mid-ground texture (even though it is in the shade)")
    # the banks beside the path she can't walk up: the half shade's grass among the needles, whatever the light
    _gy, _gx = _np.gradient(G0_)
    # (soft-edged, so its edge follows the bank's own shape and never shows the map's square metres)
    bank_ = _np.clip((_np.hypot(_gx, _gy) - 0.3) / 0.15, 0, 1) * _np.clip((6.5 - pd) / 1.5, 0, 1) * _np.clip((pd - reach_) / 0.6, 0, 1)
    green = green * (1.0 - bank_)
    mid = _np.maximum(mid, bank_)
    # (round 39, 08 #29) the closed hill's bank above the eastern wood (north.py ground(), N.GH_EDGE_Z) wears the half
    # shade's look too, whatever the light
    _ghx = HL['x0'] + _np.arange(W_) + 0.5
    _ghz = HL['z0'] + _np.arange(D_) + 0.5
    _ghb = ((_ghz[:, None] > N.GH_EDGE_Z - 8.0) & (_ghz[:, None] < N.GH_EDGE_Z) & (_ghx[None, :] > N.GRACIA_WALL_X) &
            (_ghx[None, :] < 192.0)) * _np.clip((_np.hypot(_gx, _gy) - 0.3) / 0.15, 0, 1)
    green = green * (1.0 - _ghb)
    mid = _np.maximum(mid, _ghb)
    wood_ = (pd > 4.0) & (open_ < 0.5)
    _bi, _bj = int(N.BALL[0] - HL['x0']), int(N.BALL[1] - HL['z0'])
    print('NORTH LIGHT at the ball: %.3f (lawn %.2f, moss %.2f)' % (float(light[_bj, _bi]), float(green[_bj, _bi]), float(mid[_bj, _bi])))
    print('NORTH LIGHT %d blobs; the wood off the path: light 10/25/50/75/90%%: %s, lawn %.0f%%, moss %.0f%%, needles %.0f%%' % (
        len(HILL_BLOBS), ' '.join('%.2f' % v for v in _np.percentile(light[wood_], [10, 25, 50, 75, 90])),
        100 * float((green[wood_] >= 0.5).mean()), 100 * float(((mid[wood_] >= 0.5) & (green[wood_] < 0.5)).mean()),
        100 * float((mid[wood_] < 0.5).mean())))
    rgba = _np.dstack([green, _np.zeros_like(green), light, mid])
    raw = b''.join(b'\x00' + (rgba[j] * 255).astype('uint8').tobytes() for j in range(D_))

    def _chunk(tag, data):
        return _st.pack('>I', len(data)) + tag + data + _st.pack('>I', _zl.crc32(tag + data) & 0xffffffff)
    with open(os.path.join(OUT, 'hill_light.png'), 'wb') as f_:
        f_.write(b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', _st.pack('>IIBBBBB', W_, D_, 8, 6, 0, 0, 0)) +
                 _chunk(b'IDAT', _zl.compress(raw, 9)) + _chunk(b'IEND', b''))
    scene['hill_light'] = dict(HL, file='hill_light.png')
except Exception as e_:
    print('NORTH hill light map failed:', e_)

# (round 33) Park Güell's wood floor by the same light: lawn where the sun reaches, the half shade's moss and the
# needles under the pines; lawn always within 3 m of the open lawns (the floor meets the Lawn quads without a seam)
# and along the paths' verges
PKL = {'x0': 44.0, 'z0': -254.0, 'w': 140, 'd': 116}
try:
    import numpy as _np
    import hill_light as HLT
    W_, D_ = PKL['w'], PKL['d']
    G0_ = _np.array([[gz(PKL['x0'] + i + 0.5, PKL['z0'] + j + 0.5) for i in range(W_)] for j in range(D_)], _np.float32)
    inb_ = [b for b in HILL_BLOBS if PKL['x0'] - 20 < b[0].x < PKL['x0'] + W_ + 20 and PKL['z0'] - 20 < -b[0].y < PKL['z0'] + D_ + 20]
    light = HLT.floor_light([(c.x, -c.y, c.z, r[0], r[1], r[2], sz, nm) for (c, r, sz, nm) in inb_], G0_, PKL['x0'], PKL['z0'])
    # (round 34, the user: "It is slightly more dryer": the lawn only in the brightest openings, the half shade's patchy
    # grass less, the dry floor of needles and leaves most of the wood)
    Gl_, Ml_ = HLT.steps(light, PKL['x0'], PKL['z0'], (0.9, 0.995), (0.5, 0.75))
    wd_ = _np.array([[1.0 if N.park_wood(PKL['x0'] + i + 0.5, PKL['z0'] + j + 0.5) else 0.0 for i in range(W_)] for j in range(D_)])
    edge_ = _np.zeros((D_, W_))
    for j in range(D_):
        for i in range(W_):
            if wd_[j, i] > 0.5:
                j0, j1, i0, i1 = max(0, j - 3), min(D_, j + 4), max(0, i - 3), min(W_, i + 4)
                if wd_[j0:j1, i0:i1].min() < 0.5:
                    edge_[j, i] = 1.0
                elif N.park_r(PKL['x0'] + i + 0.5, PKL['z0'] + j + 0.5) <= 0.9:
                    x_, z_ = PKL['x0'] + i + 0.5, PKL['z0'] + j + 0.5
                    edge_[j, i] = max(0.0, min(1.0, 1.0 - (min(N._seg_near(x_, z_, P_)[0] for P_ in N.PARK_PATHS) - 1.6) / 1.0))
    green = _np.clip(_np.maximum(Gl_, edge_), 0, 1)
    mid = _np.clip(_np.maximum(Ml_, edge_), 0, 1)
    # (round 35, PATH_RULES C2) the park's banks she can't walk up: the half shade's look (world2d north_mat gives
    # them the wood's floor; they were bare sand squares)
    _gy, _gx = _np.gradient(G0_)
    bank_ = _np.clip((_np.hypot(_gx, _gy) - 0.3) / 0.15, 0, 1)          # (soft-edged: no square metres)
    green = green * (1.0 - bank_)
    mid = _np.maximum(mid, bank_)
    print('PARK LIGHT %d blobs; the wood: lawn %.0f%%, moss %.0f%%, needles %.0f%%' % (len(inb_),
        100 * float((green[wd_ > 0.5] >= 0.5).mean()), 100 * float(((mid[wd_ > 0.5] >= 0.5) & (green[wd_ > 0.5] < 0.5)).mean()),
        100 * float((mid[wd_ > 0.5] < 0.5).mean())))
    rgba = _np.dstack([green, _np.zeros_like(green), light, mid])
    raw = b''.join(b'\x00' + (rgba[j] * 255).astype('uint8').tobytes() for j in range(D_))
    with open(os.path.join(OUT, 'park_light.png'), 'wb') as f_:
        f_.write(b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', _st.pack('>IIBBBBB', W_, D_, 8, 6, 0, 0, 0)) +
                 _chunk(b'IDAT', _zl.compress(raw, 9)) + _chunk(b'IEND', b''))
    scene['park_light'] = dict(PKL, file='park_light.png')
except Exception as e_:
    print('PARK light map failed:', e_)

# the walkable world grows north and west to take in the hill (and the river's west bank stays out of reach)
w_ = scene.get('walk')
if w_:
    w_['z0'] = min(w_['z0'], -330.0)
    w_['x0'] = min(w_['x0'], -232.0)
    solid(-240.0, -118.0, -184.0, 400.0)

city_objs.append(PS_MB.finish('ParkSigns'))

# (round 33, the user: "The glowing doors are just squares in front of the building (the actual door should be
# glowing!!)") a door's point is where she walks in, often out in front of the house (its model's real wall stands
# back inside its footprint): the glow goes on the wall itself, found by looking back from the door at waist height
_dg = bpy.context.evaluated_depsgraph_get()
for e in new_doors:
    if 'glow' in e or 'glow_c' in e:                     # (round 33: its own door, built here: the glow is where it says)
        scene['entrances'].append(e)
        continue
    ex_, ez_ = e['pos']
    nx_, nz_ = e['normal']
    o_ = V(ex_ + nx_ * 1.0, ez_ + nz_ * 1.0, e['base'] + 1.2)
    hit_, loc_, nrm_, _i, ob_, _m = bpy.context.scene.ray_cast(_dg, o_, Vector((-nx_, nz_, 0.0)), distance=4.0)
    if hit_ and ob_ is not None and not ob_.name.startswith(('Leaves', 'Plants', 'Grass', 'Trail', 'ParkPaths', 'Terrain')):
        e['glow'] = [round(loc_.x + nx_ * 0.03, 3), round(-loc_.y + nz_ * 0.03, 3)]
        print('DOOR GLOW %s on %s, %.2f m behind its point' % (e['id'], ob_.name, math.hypot(loc_.x - ex_, -loc_.y - ez_)))
    scene['entrances'].append(e)
north['doors'] = [e['id'] for e in new_doors]
print('NORTH built: %d doors, path %.0f m, %d blocked' % (len(new_doors), PL, len(scene['blocked'])))
