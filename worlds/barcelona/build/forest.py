# The forest in the east, as a Mediterranean wood on the edge of Barcelona (round 18). Exec'd from
# world2d.py in two parts: forest_layout() before the ground is made (the ground needs to know where the
# trodden paths and the grassy fringe are), and plant_forest() where the old forest was planted.
#
# From the city outwards:
#   the meadow    the grass between the city's footpath and the trees: tufts of grass and small wild
#                 flowers (not picked: only looked at), a very few olives, stone pines and carobs
#   the fringe    the wood's first few metres: grass under scattered trees (olive, carob, stone pine,
#                 cypress, holm oak); walkable, the trunks are solid
#   the wood      thick: holm oak, Aleppo pine, cork oak and stone pine over lentisk, rosemary, broom and
#                 strawberry trees; walled off (forest_blocked) except along its paths and clearings
# The paths are worn into the earth by people walking: a band of packed ochre soil, paler down the middle,
# with frayed edges, winding a little, never straight, always heading on its way. They follow the 2D
# game's paths: a long one north to south, four across from the meadow, short trails to the clearings
# where someone (or Trufa) waits, and they come out onto the meadow, where a street lamp stands by each
# entrance. Nothing is lit inside the wood.
# Round 19 (the user's changes): across the meadow the ways in are proper footpaths, paved like the city's
# but narrower (no grass on them), ending just past each lamp, where the paving breaks up into the trodden
# earth path; paths join where they meet; the trees stop a little short of the beach and the forest floor
# runs on down to the sand (sandy near the beach, drier and greener further in); a few more trees in the
# meadow by the road, for a park feel.
# Round 20 (the user's changes): the wood can be walked anywhere: only the tree trunks are solid (shrubs and
# leaves are walked through), and the game lets Sandra slip between two trunks she has pushed at for a few
# seconds. The bike keeps out of the thick of the wood (round 20e: a rope from trunk to trunk round its edge,
# worked out in the game, main.gd's forest_ropes(); before, a grid of squares that stood out past the trees). Where paths meet, the corners are grassy and open (JUNCTIONS, FILLET)
# so she can ride round them; the paths' cores are drawn over every path's frayed edge, so crossings join. Under the trees the floor is dark litter (less light); out from under
# them (the fringe, the glades, the corners, the strip down to the beach) it is grass.
# Round 20b: the floor follows the light. forest_light() follows the sun across the game's summer day (and
# the open sky's softer light) through every tree's crown and every bush, and gives each patch of floor how
# much light it gets: where the sun reaches for most of the day it is grass, in the shade all day it is leaf
# litter, and between the two the grass comes and goes in patches. So the glades and the paths' crossings
# are green, the trees on the beach side (lit from the south, under their crowns) stand on grass, and deep
# under the holm oaks it is brown. The ground there is one material, ForestFloorLit, that the game draws
# from that light map (godot/forest_floor.gdshader: litter, the meadow's lawn, and the beach's sand, which
# it runs into softly instead of in squares). The bike goes where it is green.
# Round 20d: three steps by the light, so the trees' shade shows in the floor: the meadow's lawn where the
# light is good (GREEN_AT), tufts of grass among the needles in the half shade (MID_AT: the user's pick
# from test pictures, "option F": about half grass, a shade darker), and golden needles, russet
# leaves, dry grass and earth only in the darkest shade (under the thick holm oaks). Two textures and two
# materials, ForestMid and ForestFloorLit (the needles); the light is 60% sun, 40% open sky.
# Round 20e: the bike is kept out of the thick of the wood by a rope from trunk to trunk round its edge
# (bike_rope.py, 7.5 m at most between two trunks, never across a path, the gaps it closes in filled), the
# user's pick from maps of it; a pocket west of the long path is closed off, planted and given the half
# shade's floor (POCKETS).

import math, random

frng = random.Random(1888)
FOREST_X0 = 84                 # (2D tiles) the wood never reaches further west than this
FRINGE = 1.5                   # tiles of open, walkable fringe inside the wood's edge
FOREST_TILES = ('FFLOOR', 'TREE', 'PATH', 'BOULDER')


def tree_end(x):
    """(2D tiles) how far south the trees reach: a little short of the beach, along an uneven line"""
    return 83.0 + 0.45 * math.sin(x * 0.9) + 0.3 * math.sin(x * 2.3 + 1.0)


_shore = {}


def meadow_shore(X, Y):
    """(2D tiles, whole) The meadow's lawn by the beach (round 37, the user: "The grass at the beach has a square at the
    start of the forest… The grass should appear to be continuous"): its last two rows above the sand, from the city's
    footpath to the wood. They are drawn with the wood's floor (by the light map), which runs into the sand on a
    ragged edge, as the wood's floor does beside them, instead of meeting it on the tiles' straight line."""
    if (X, Y) not in _shore:
        _shore[(X, Y)] = X >= FOREST_X0 - 2 and tile(X, Y) == 'GRASS' and \
            any(tile(X + dx, Y + dy) in ('SAND', 'PALM') for dx in (-1, 0, 1) for dy in (1, 2))
    return _shore[(X, Y)]


def east_wood(x, y):
    """(Round 24's wooded headland past the cove; round 25: gone, with the cove)"""
    return False


def past_rise(x, y):
    """(Round 25) out of her reach, behind the first trees on the wood's rise past the map's east edge: there the trees
    are only their bushy tops (the user: "these do not need to be proper trees")."""
    return 'east_rise_from' in globals() and y < tree_end(x) - 4.0 and x > east_rise_from(y) + 2.0   # (not by the beach: seen from it)


def is_wood(X, Y):
    """Is 2D tile (X, Y) part of the wood (off the map to the east it carries on)?"""
    if X >= MW2 and 6 <= Y <= 85:
        return True
    if east_wood(X + 0.5, Y + 0.5):
        return True
    return X >= FOREST_X0 and tile(X, Y) in FOREST_TILES


# ------------------------------------------------------------------ the paths' lines

def smooth(pts, k=3):
    out = []
    for i in range(len(pts)):
        a, b = max(0, i - k), min(len(pts), i + k + 1)
        out.append((sum(p[0] for p in pts[a:b]) / (b - a), sum(p[1] for p in pts[a:b]) / (b - a)))
    return out


def resample(pts, step=0.25):
    """Evenly spaced points along a polyline (tiles)."""
    out = [pts[0]]
    carry = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        d = step - carry
        while d <= L:
            out.append((ax + (bx - ax) * d / L, ay + (by - ay) * d / L))
            d += step
        carry = L - (d - step)
    if math.hypot(out[-1][0] - pts[-1][0], out[-1][1] - pts[-1][1]) > step * 0.3:
        out.append(pts[-1])
    return out


def wander(pts, amp, seed, pin_start=True, pin_end=True):
    """A trodden path never runs dead straight: it drifts a little to one side and back, unevenly, the way
    feet go round a root or a puddle, but keeps its heading. amp: tiles."""
    r = random.Random(seed)
    f1, f2, f3 = r.uniform(0.55, 0.8), r.uniform(1.3, 1.9), r.uniform(2.9, 3.6)
    p1, p2, p3 = r.uniform(0, 6.28), r.uniform(0, 6.28), r.uniform(0, 6.28)
    pts = resample(pts, 0.25)
    n = len(pts)
    s = 0.0
    out = []
    for i, (x, y) in enumerate(pts):
        if i:
            s += math.hypot(x - pts[i - 1][0], y - pts[i - 1][1])
        j0, j1 = max(0, i - 2), min(n - 1, i + 2)
        tx, ty = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / L, tx / L
        off = amp * (0.6 * math.sin(s * f1 / 3.3 * 2.2 + p1) + 0.3 * math.sin(s * f2 / 3.3 * 2.2 + p2) + 0.1 * math.sin(s * f3 / 3.3 * 2.2 + p3))
        k = 1.0
        if pin_start:
            k = min(k, s / 1.5)
        if pin_end:
            k = min(k, (len(pts) - 1 - i) * 0.25 / 1.5)
        k = max(0.0, min(1.0, k))
        out.append((x + nx * off * k, y + ny * off * k))
    return out


def trunk_line():
    """The long path north to south: through the middle of the 2D game's path tiles, row by row."""
    pts = []
    for Y in range(18, 84):
        xs = [X for X in range(91, 100) if tile(X, Y) == 'PATH']
        if xs:
            near = [X for X in xs if abs(X - (pts[-1][0] if pts else 95.5)) < 2.5] or xs
            pts.append((sum(near) / len(near) + 0.5, Y + 0.5))
    pts = smooth(pts, 4)
    # (round 36, H4/A9) in the north it runs straight on up the wood's edge to Gràcia's wall gap at the
    # Travessera, no longer bending west over the quarter's ground; in the south it stops where the sand
    # begins — gravel never lies over sand.
    north = [(94.62, 16.06), (95.05, 16.12), (95.35, 16.5), (95.45, 17.7)]   # its end curves in through the wall's gap
    by_ = curve('beach', pts[-1][0])              # the beach's visible back edge, not the map's buried sand tiles
    south = [p for p in [(pts[-1][0], 84.2), (pts[-1][0] + 0.15, 84.9), (pts[-1][0] + 0.25, 85.8)] if p[1] < by_ - 0.3]
    return north + [p for p in pts if p[1] > 18.6] + south


PATHS = []          # {'pts': [(x, y)], 'w': metres wide, 'kind': 'trunk'|'branch'|'trail'|'meadow'}
CLEARINGS = []      # (x, y, r) tiles: open glades
ENTRANCES_F = []    # (x, y, dx, dy): where a path leaves the meadow for the wood, and its heading in
JUNCTIONS = []      # (x, y) tiles: where a path meets another (grassy, open corners round them)
FILLET = 1.15       # tiles: how far round a junction the corners are open grass


def forest_layout():
    trunk = wander(trunk_line(), 0.2, 11, pin_start=False, pin_end=False)
    PATHS.append({'pts': trunk, 'w': 2.0, 'kind': 'trunk', 'round_end': True})     # (round 37: its end on the beach rounded)
    tx_at = lambda yy: min(trunk, key=lambda p: abs(p[1] - yy))[0]
    for k, yy in enumerate((29, 42, 55, 68)):
        y = yy + 0.5
        xs = [X for X in range(FOREST_X0, MW2) if tile(X, yy) == 'PATH']
        x_in = min(xs) + 0.2                                      # where the 2D path meets the meadow
        if yy == 29:
            # (round 36, H4) this row is Gràcia's south edge now: the branch begins at the town's wall gap,
            # east of the bounding footpath, and there is no meadow strip over the quarter's paving
            x_in = 94.58
        else:
            # across the meadow: a fainter line in the grass from the city's footpath to the wood
            # a paved footpath like the city's, narrower, from the city's footpath to just past the lamp
            PATHS.append({'pts': resample([(81.95, y), (x_in - 0.2, y)], 0.25), 'w': 1.4, 'kind': 'meadow'})
        # then the trodden path, from under the paving's broken end, into the wood, across the long path, on
        # east to a glade at the far side
        east = [(x_in - 0.75, y), (x_in, y), (tx_at(y), y), (101.2, y + frng.uniform(-0.4, 0.4))]
        if yy == 29:
            east = [(x_in, y), (tx_at(y), y), (101.2, y + frng.uniform(-0.4, 0.4))]
        pts_ = wander(east, 0.22, 20 + k)
        # (round 25) in two: the way in, gravel like the long path ('branch'), as far as the long path; then a dirt
        # path on east ('spur') that stops where the glade starts ("stopping at the start")
        cut = min(range(len(pts_)), key=lambda i: abs(pts_[i][0] - tx_at(y)) + abs(pts_[i][1] - y))
        gx_, gy_, gr_ = 101.6, east[-1][1], 1.3
        PATHS.append({'pts': pts_[:cut + 1], 'w': 1.7, 'kind': 'branch'})
        # (round 40, A8: from the gravel's middle line, lying under it (trails.py LOW_STEP), so no strip of grass
        # between the gravel and the dirt — it began 1.2 m off the middle, past the gravel's edge)
        PATHS.append({'pts': [q for q in pts_[cut:] if math.hypot(q[0] - gx_, q[1] - gy_) > gr_], 'w': 1.7, 'kind': 'spur',
                      'round_end': True})
        CLEARINGS.append((gx_, gy_, gr_))
        if yy != 29:
            ENTRANCES_F.append((x_in, y, 1.0, 0.0))
        JUNCTIONS.append((tx_at(y), y))
    # (round 36, H4) short gravel stubs from Gràcia's wall gaps to the long path: the Travessera's end and
    # Carrer de la Perla's (the row-29 branch is Provença's)
    for yy_ in (22.88,):                       # (the Travessera's end is the long path's own north end above)
        sx_ = tx_at(yy_)
        PATHS.append({'pts': resample([(94.58, yy_), (sx_ - 0.1, yy_)], 0.25), 'w': 1.7, 'kind': 'branch'})
        JUNCTIONS.append((sx_, yy_))
    print('JUNCTIONS', [(round(a, 2), round(b, 2)) for a, b in JUNCTIONS])
    # the little trails to the glades where people wait (and Trufa hides)
    for (cx, cy, r) in [(93.5, 36.5, 1.2), (97.5, 62.5, 1.2), (98.5, 50.5, 1.1), (89.5, 81.5, 1.2)]:
        CLEARINGS.append((cx, cy, r))
        if cx < 91:
            continue                                              # (the one in the south-west opens off the fringe)
        sx = tx_at(cy)
        JUNCTIONS.append((sx, cy - 0.4))
        # (round 23, the user: "the path should not go too far into the glade": it stops at the glade's edge)
        dx_, dy_ = cx - (sx - 0.2), cy - (cy - 0.4)
        L_ = math.hypot(dx_, dy_)
        ex, ey = cx - dx_ / L_ * r, cy - dy_ / L_ * r             # (round 25: at the glade's edge, not into it)
        tr_ = wander([(sx - 0.2, cy - 0.4), ((sx + ex) / 2, (cy - 0.4 + ey) / 2 + 0.2), (ex, ey)], 0.1, int(cx * cy))
        # (round 40, A8: the trail starts under the gravel, from its middle, not 1.2 m off it — a strip of grass showed)
        PATHS.append({'pts': tr_, 'w': 1.0, 'kind': 'trail'})
    # where the paths run, for quick distance tests: path samples bucketed by tile
    for pi, P in enumerate(PATHS):
        for (x, y) in P['pts']:
            PATH_BUCKETS.setdefault((int(x), int(y)), []).append((x, y, P['w'] / T / 2, pi))
    # how deep into the wood each point is: the distance (tiles) to the nearest open tile
    for Y in range(4, 92):
        for X in range(FOREST_X0 - 2, MW2 + 4):
            if not is_wood(X, Y) and any(is_wood(X + dx, Y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                if tile(X, Y) is not None and tile(X, Y) not in ('SAND', 'SEA', 'PALM'):     # (the wood runs on to the beach)
                    EDGE_PTS.append((X + 0.5, Y + 0.5))


PATH_BUCKETS = {}
EDGE_PTS = []
_depth_cache = {}


def path_dist(x, y):
    """(distance from the nearest path's middle, minus its half width) in tiles, and which path."""
    best, which = 9.0, -1
    for bx in (int(x) - 1, int(x), int(x) + 1):
        for by in (int(y) - 1, int(y), int(y) + 1):
            for (px, py, hw, pi) in PATH_BUCKETS.get((bx, by), ()):
                d = math.hypot(x - px, y - py) - hw
                if d < best:
                    best, which = d, pi
    return best, which


def depth(x, y):
    """How far into the wood (tiles); 0 outside it."""
    if not is_wood(int(math.floor(x)), int(math.floor(y))):
        return 0.0
    key = (round(x * 4), round(y * 4))
    if key not in _depth_cache:
        _depth_cache[key] = min((math.hypot(x - ex, y - ey) for ex, ey in EDGE_PTS), default=9.0) - 0.5
    return _depth_cache[key]


def ground_z(x, y):
    """The ground's height (metres) at (x, y) tiles: world2d's terrain grid (VH), between its points; 0.05,
    the wood's floor, where there is none (the preview)."""
    g = globals()
    if 'VH' not in g or not g['VH']:
        return 0.05
    if g.get('GF_CELLS'):
        f_ = gf_at(x, y)                          # (round 35: the finer ground along the hill path, world2d.py)
        if f_ is not None:
            return f_
    fi, fj = (x - TX0) / STEP, (y - TY0) / STEP
    i, j = max(0, min(len(VH[0]) - 2, int(fi))), max(0, min(len(VH) - 2, int(fj)))
    a, b = min(1.0, max(0.0, fi - i)), min(1.0, max(0.0, fj - j))
    return (VH[j][i] * (1 - a) + VH[j][i + 1] * a) * (1 - b) + (VH[j + 1][i] * (1 - a) + VH[j + 1][i + 1] * a) * b


def in_clearing(x, y, pad=0.0):
    return any(math.hypot(x - cx, y - cy) < r + pad for cx, cy, r in CLEARINGS)


def forest_ground(X, Y, k):
    """The ground's kind under half-tile (X, Y) (2D tiles), for world2d's ground: the paths are drawn on
    top (so their tiles are forest floor underneath), and the fringe is grassy."""
    if k not in FOREST_TILES or X < FOREST_X0:
        return k
    # (round 38, the user: the boulder "is on a square green tile. Its ground should match whatever is around it":
    # under a boulder the wood's own floor, as round it)
    # (needles, tufts among needles, grass or sand by the light in the game: forest_light(); here, a first
    # guess, so both materials are in the ground: tufts by the paths, needles away from them)
    return 'FORESTMID' if path_dist(X + 0.25, Y + 0.25)[0] < 1.2 else 'FOREST'


def near_junction(x, y, pad=0.0):
    return any(math.hypot(x - jx, y - jy) < FILLET + pad for jx, jy in JUNCTIONS)


def open_ground(x, y):
    """Grass, not litter or sand: where the light lets it grow (forest_light())."""
    g, sd = light_at(x, y)
    return g >= 0.5 and sd < 0.5


TRUNKS = {}         # tile -> the trunks standing in it (tiles)
# (2D tiles) ground the user asked to be wood (round 20e): a pocket of open floor west of the long path, north
# of its first crossing, that the bike's rope (bike_rope.py's TIE) now closes off; planted with trees like the
# wood round it, and its floor the half shade's (grass clumps among the needles), whatever the light
POCKETS = [[(90.4, 25.6), (91.6, 25.4), (93.1, 25.6), (94.0, 26.2), (94.7, 26.9), (94.4, 27.2), (92.6, 28.2), (91.0, 28.0)]]


def in_pocket(x, y, pad=0.0):
    """How far (tiles) inside one of the POCKETS (x, y) is, less pad; negative outside."""
    best = -9.0
    for poly in POCKETS:
        inside, d = False, 9.0
        for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                inside = not inside
            t = max(0.0, min(1.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
            d = min(d, math.hypot(x - ax - t * (bx - ax), y - ay - t * (by - ay)))
        best = max(best, (d if inside else -d) - pad)
    return best


# ------------------------------------------------------------------ the light on the forest floor

LIGHT = {}          # the light map (forest_light()): its cells' greenness and sandiness, and where it lies
BLOBS = []          # every crown's and bush's leaves, as rough ellipsoids: (centre, radii, card size, material)
# how thick each kind of leaf is (light lost a metre through it): the holm oaks, carobs and cypresses dark
# and dense, the pines and cork oaks thinner, the olives and Aleppo pines airy; the bushes low and thin
# (a crown is a shell of leaf cards with gaps between them, so even the holm oak lets some light through)
LEAF_DENSITY = {'LeavesHolm': 0.45, 'LeavesHolmB': 0.45, 'LeavesCarob': 0.42, 'LeavesCypress': 0.5,
                'LeavesStonePine': 0.38, 'LeavesCork': 0.32, 'LeavesAleppo': 0.2, 'LeavesOlive': 0.22, 'bush': 0.3}
SUN_SHARE = 0.6     # the sun's part of the light (the rest is the open sky's)
GREEN_AT = (0.3, 0.6)    # light from which grass starts to show, and above which it is all grass
MID_AT = (0.05, 0.12)    # light from which the half shade's tufts start to show over the needles, and above which it is all


def forest_light():
    """How much light reaches each patch of the wood's floor over a day, and so what grows there.
    The crowns and bushes (BLOBS) are made into a block of leaf thickness (cells a quarter tile across,
    half a metre high); then, for the sun at 24 times through the game's day (as main.gd's sky_positions():
    up in the east-north-east, highest in the south, down in the west-north-west) and for 17 patches of
    open sky, the light left after passing through the leaves on its way down to each cell. Sunlight from
    low in the sky counts for less."""
    import numpy as np
    C = 0.25
    X0, Y0, X1, Y1 = FOREST_X0 - 4, 2.0, MW2 + 25, 92.0         # (round 38: to past the grid's east edge, TX1 = MW2 + 24: no clamped edge)
    nx, ny, DZ, nz = int((X1 - X0) / C), int((Y1 - Y0) / C), 0.5, 28
    gx = X0 + (np.arange(nx) + 0.5) * C
    gy = Y0 + (np.arange(ny) + 0.5) * C
    zc = (np.arange(nz) + 0.5) * DZ
    rho = np.zeros((nz, ny, nx), np.float32)
    for (c, radii, size, name) in BLOBS:
        k = LEAF_DENSITY.get(name, 0.7)
        cx, cy, cz = c.x / T + OX, -c.y / T + OY, c.z
        pad = 0.2 * size                                    # (the leaf cards reach out past the crown's line)
        rx, ry, rz = radii[0] + pad, radii[1] + pad, radii[2] + pad * 0.6
        i0, i1 = max(0, int((cx - rx / T - X0) / C)), min(nx, int((cx + rx / T - X0) / C) + 2)
        j0, j1 = max(0, int((cy - ry / T - Y0) / C)), min(ny, int((cy + ry / T - Y0) / C) + 2)
        l0, l1 = max(0, int((cz - rz) / DZ)), min(nz, int((cz + rz) / DZ) + 2)
        if i0 >= i1 or j0 >= j1 or l0 >= l1:
            continue
        q = (((zc[l0:l1] - cz) / rz) ** 2)[:, None, None] + (((gy[j0:j1] - cy) * T / ry) ** 2)[None, :, None] + \
            (((gx[i0:i1] - cx) * T / rx) ** 2)[None, None, :]
        rho[l0:l1, j0:j1, i0:i1] += k * np.clip((1.0 - q) * 2.5, 0.0, 1.0)

    def shifted(a, ox, oy):
        # a[j + oy, i + ox] (cells, fractional: blended between the four nearest), nothing beyond the edge
        ix, iy = int(math.floor(ox)), int(math.floor(oy))
        fx, fy = ox - ix, oy - iy
        out = np.zeros_like(a)
        for ddx, ddy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
            sx, sy = ix + ddx, iy + ddy
            if w < 1e-4 or abs(sx) >= nx or abs(sy) >= ny:
                continue
            dst = out[max(0, -sy):ny - max(0, sy), max(0, -sx):nx - max(0, sx)]
            dst += w * a[max(0, sy):ny + min(0, sy), max(0, sx):nx + min(0, sx)]
        return out

    def through(e_deg, b_deg):
        e, b = math.radians(e_deg), math.radians(b_deg)
        de, ds, up = math.cos(e) * math.sin(b), -math.cos(e) * math.cos(b), math.sin(e)    # east, south, up
        tau = np.zeros((ny, nx), np.float32)
        for l in range(nz):
            run = zc[l] / up                                # (metres along the ray to this height)
            tau += shifted(rho[l], de * run / (C * T), ds * run / (C * T)) * (DZ / up)
        return np.exp(-tau)

    sun = np.zeros((ny, nx), np.float32)
    wsum = 0.0
    for i in range(24):
        f = (i + 0.5) / 24
        el = 62.0 * math.sin(math.pi * f)
        w = min(1.0, max(0.0, el / 14.0)) ** 1.5             # (the low sun, at either end of the day, is weak)
        if w > 0.01:
            sun += w * through(el, 70.0 + 220.0 * f)
            wsum += w
    sun /= wsum
    sky = np.zeros((ny, nx), np.float32)
    patches = [(30.0, b) for b in range(0, 360, 45)] + [(58.0, b + 22.5) for b in range(0, 360, 45)] + [(85.0, 0.0)]
    for el, b in patches:
        sky += through(el, b)
    sky /= len(patches)
    L = SUN_SHARE * sun + (1 - SUN_SHARE) * sky

    # what grows: grass where the light is good (its edge wandering a little), litter where it isn't; where
    # the floor meets the meadow's lawn it is lawn, and where it meets the beach it turns to sand
    X2, Y2 = np.meshgrid(gx, gy)
    wob = 0.55 * np.sin(X2 * 1.31 + 0.8 * np.sin(Y2 * 0.93)) + 0.45 * np.sin(Y2 * 1.77 - X2 * 0.62)
    t = np.clip((L + 0.05 * wob - GREEN_AT[0]) / (GREEN_AT[1] - GREEN_AT[0]), 0.0, 1.0)
    G = t * t * (3 - 2 * t)
    t = np.clip((L + 0.03 * wob - MID_AT[0]) / (MID_AT[1] - MID_AT[0]), 0.0, 1.0)
    M = t * t * (3 - 2 * t)
    floor_ = np.zeros((ny, nx), bool)
    grass_d = np.full((ny, nx), 99.0, np.float32)
    sand_d = np.full((ny, nx), 99.0, np.float32)
    kinds = {}
    for j in range(ny):
        for i in range(nx):
            X, Y = int(math.floor(gx[i])), int(math.floor(gy[j]))
            if (X, Y) not in kinds:
                k = tile(X, Y)
                if k is None and X >= MW2 and 85 <= Y < MH2:
                    k = tile(MW2 - 1, Y)                        # (as world2d's tile_kind(): the beach carries on east)
                if k is None:
                    k = 'SEA' if Y >= MH2 else ('FFLOOR' if X >= MW2 else 'GRASS')
                kinds[(X, Y)] = 'floor' if (X >= FOREST_X0 and k in FOREST_TILES and k != 'BOULDER') else \
                    ('sand' if k in ('SAND', 'PALM', 'SEA') else ('grass' if k == 'GRASS' else 'other'))
            floor_[j, i] = kinds[(X, Y)] == 'floor'
    for name, dist in (('grass', grass_d), ('sand', sand_d)):
        for j in range(ny):
            for i in range(nx):
                X, Y = int(math.floor(gx[i])), int(math.floor(gy[j]))
                if kinds[(X, Y)] != name:
                    continue
                if not any(kinds.get((X + dx, Y + dy)) == 'floor' or meadow_shore(X + dx, Y + dy)
                           for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)):
                    continue
                a0, a1, b0, b1 = max(0, i - 8), min(nx, i + 9), max(0, j - 8), min(ny, j + 9)
                d = np.hypot(X2[b0:b1, a0:a1] - gx[i], Y2[b0:b1, a0:a1] - gy[j]) - C
                np.minimum(dist[b0:b1, a0:a1], np.maximum(d, 0.0), out=dist[b0:b1, a0:a1])
    wob2 = 0.55 * np.sin(X2 * 2.3 + 1.0 + 0.8 * np.sin(Y2 * 1.4)) + 0.45 * np.sin(Y2 * 2.9 - X2 * 1.1 + 2.0)
    G = np.maximum(G, np.clip(1.0 - grass_d * (1 + 0.5 * wob) / 1.1, 0.0, 1.0))      # (lawn at the meadow's edge)
    S = np.clip(1.0 - sand_d * (1 + 0.5 * wob2) / 0.9, 0.0, 1.0)                    # (sand at the beach's)
    M = np.maximum(M, G)
    for poly in POCKETS:                                         # (the pocket: half shade, its edge soft)
        i0, i1 = int((min(p[0] for p in poly) - 0.6 - X0) / C), int((max(p[0] for p in poly) + 0.6 - X0) / C) + 1
        j0, j1 = int((min(p[1] for p in poly) - 0.6 - Y0) / C), int((max(p[1] for p in poly) + 0.6 - Y0) / C) + 1
        for j in range(max(0, j0), min(ny, j1)):
            for i in range(max(0, i0), min(nx, i1)):
                w_ = min(1.0, max(0.0, (in_pocket(gx[i], gy[j]) + 0.3) / 0.6))
                G[j, i] *= 1.0 - w_
                M[j, i] = max(M[j, i], w_)
    LIGHT.update(G=G, S=S, L=L, M=M, x0=X0, y0=Y0, c=C, nx=nx, ny=ny)
    # the game's copy: a small picture (red: grass, green: sand, blue: the light itself, alpha: the half shade), and
    # where it lies
    import zlib, struct
    px = np.stack([G, S, L, M], -1)
    raw = b''.join(b'\x00' + (np.clip(px[j], 0, 1) * 255 + 0.5).astype(np.uint8).tobytes() for j in range(ny))

    def chunk_(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk_(b'IHDR', struct.pack('>IIBBBBB', nx, ny, 8, 6, 0, 0, 0)) + \
        chunk_(b'IDAT', zlib.compress(raw, 9)) + chunk_(b'IEND', b'')
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'forest_light.png'), 'wb') as f:
        f.write(png)
    scene['forest_light'] = {'file': 'forest_light.png', 'x0': round((X0 - OX) * T, 3), 'z0': round((Y0 - OY) * T, 3),
                             'w': round(nx * C * T, 3), 'd': round(ny * C * T, 3)}
    # (round 24) the glades, in metres, for the game's sunbeams through the canopy (touches.gd)
    scene['forest_glades'] = [[round((cx - OX) * T, 2), round((cy - OY) * T, 2), round(r * T, 2)] for cx, cy, r in CLEARINGS]
    for nm, pts in (('glades', [(cx, cy) for cx, cy, _ in CLEARINGS]), ('crossings', JUNCTIONS)):
        print('LIGHT', nm, [round(float(L[int((py - Y0) / C), int((px_ - X0) / C)]), 2) for px_, py in pts])
    fl = L[floor_]
    print('LIGHT floor: %d cells, light 10/25/50/75/90%%: %.2f %.2f %.2f %.2f %.2f, grass %.0f%%, half shade %.0f%%, needles %.0f%%, sand %.0f%%' % (
        fl.size, *np.percentile(fl, [10, 25, 50, 75, 90]), 100 * float((G[floor_] >= 0.5).mean()),
        100 * float(((M[floor_] >= 0.5) & (G[floor_] < 0.5)).mean()), 100 * float((M[floor_] < 0.5).mean()),
        100 * float((S[floor_] >= 0.5).mean())))
    # (by the paths, within 1.5 tiles, and under the holm oaks' crowns)
    near = np.zeros((ny, nx), bool)
    for j in range(0, ny, 2):
        for i in range(0, nx, 2):
            if floor_[j, i] and path_dist(gx[i], gy[j])[0] < 1.5:
                near[j:j + 2, i:i + 2] = True
    near &= floor_
    holm = np.zeros((ny, nx), bool)
    for (c, radii, size, name) in BLOBS:
        if name.startswith('LeavesHolm'):
            cx, cy = c.x / T + OX, -c.y / T + OY
            holm |= np.hypot((X2 - cx) * T / radii[0], (Y2 - cy) * T / radii[1]) < 0.7
    holm &= floor_
    beach = floor_ & (Y2 >= 76)
    for nm, sel in (('by the paths', near), ('under holm oaks', holm), ('beach side', beach)):
        if sel.any():
            print('LIGHT %s: %d cells, light 25/50/75%%: %.2f %.2f %.2f, grass %.0f%%, half shade %.0f%%, needles %.0f%%' % (
                nm, sel.sum(), *np.percentile(L[sel], [25, 50, 75]), 100 * float((G[sel] >= 0.5).mean()),
                100 * float(((M[sel] >= 0.5) & (G[sel] < 0.5)).mean()), 100 * float((M[sel] < 0.5).mean())))


def light_at(x, y):
    """(greenness, sandiness) 0..1 of the wood's floor at (x, y) tiles, from the light map."""
    if not LIGHT:
        return 1.0, 0.0
    fx = (x - LIGHT['x0']) / LIGHT['c'] - 0.5
    fy = (y - LIGHT['y0']) / LIGHT['c'] - 0.5
    i, j = int(math.floor(fx)), int(math.floor(fy))
    if i < 0 or j < 0 or i >= LIGHT['nx'] - 1 or j >= LIGHT['ny'] - 1:
        return 1.0, 0.0
    ax, ay = fx - i, fy - j
    out = []
    for A in (LIGHT['G'], LIGHT['S']):
        out.append(float(A[j, i] * (1 - ax) * (1 - ay) + A[j, i + 1] * ax * (1 - ay) + A[j + 1, i] * (1 - ax) * ay + A[j + 1, i + 1] * ax * ay))
    return out[0], out[1]


def nobike_rects(blocked_at, X0, X1, Y0, Y1, cell=0.25):
    """Cells (tiles) where blocked_at(x, y) is true, merged into strips and the strips into rectangles
    (engine metres [x0, z0, x1, z1])."""
    runs = {}
    yy = Y0
    while yy < Y1:
        xx = X0
        start = None
        while xx < X1 + 1e-6:
            b = xx < X1 and blocked_at(xx + cell / 2, yy + cell / 2)
            if b and start is None:
                start = xx
            if not b and start is not None:
                runs.setdefault((round(start, 4), round(xx, 4)), []).append(round(yy, 4))
                start = None
            xx += cell
        yy += cell
    out = []
    for (x0, x1), ys in runs.items():
        ys.sort()
        s0 = prev = ys[0]
        for v in ys[1:] + [None]:
            if v is not None and abs(v - (prev + cell)) < 1e-3:
                prev = v
                continue
            out.append([round((x0 - OX) * T, 3), round((s0 - OY) * T, 3), round((x1 - OX) * T, 3), round((prev + cell - OY) * T, 3)])
            if v is not None:
                s0 = prev = v
    return out


# ------------------------------------------------------------------ materials

def upright(px, W, H):
    """The rows turned over: these pictures are drawn top row first, but a Blender image's first row is its
    bottom (round 20d: drawn as they were, every tuft, flower and fern stood on its head, roots in the air)."""
    out = []
    for yy in range(H - 1, -1, -1):
        out.extend(px[yy * W * 4:(yy + 1) * W * 4])
    return out


def blade_image(name, cols, seed, flowers=None):
    """A tuft of grass blades fanning up from the bottom of the card (and flowers on stems, if given)."""
    rng = random.Random(seed)
    W = H = 64
    px = [0.0] * (W * H * 4)
    base = rgb(cols[0])
    for i in range(W * H):
        px[i * 4], px[i * 4 + 1], px[i * 4 + 2] = base

    def dot(x, y, r, col):
        for yy in range(max(0, int(y - r) - 1), min(H, int(y + r) + 2)):
            for xx in range(max(0, int(x - r) - 1), min(W, int(x + r) + 2)):
                if (xx - x) ** 2 + (yy - y) ** 2 <= r * r:
                    i = (yy * W + xx) * 4
                    px[i], px[i + 1], px[i + 2], px[i + 3] = col[0], col[1], col[2], 1.0
    for _ in range(28):
        x0 = W / 2 + rng.uniform(-11, 11)
        ang = rng.uniform(-0.65, 0.65)
        L = rng.uniform(26, 58)
        col = rgb(rng.choice(cols))
        bend = rng.uniform(-0.25, 0.25)
        steps = int(L)
        for s in range(steps):
            f = s / steps
            a = ang + bend * f * f
            x = x0 + math.sin(a) * s
            y = H - 1 - math.cos(a) * s
            w = 1.3 * (1 - f) + 0.35
            k = 0.8 + 0.35 * f
            dot(x, y, w, (min(1, col[0] * k), min(1, col[1] * k), min(1, col[2] * k)))
    for (fc, n) in (flowers or []):
        for _ in range(n):
            x0 = W / 2 + rng.uniform(-14, 14)
            L = rng.uniform(30, 52)
            ang = rng.uniform(-0.3, 0.3)
            for s in range(int(L)):
                dot(x0 + math.sin(ang) * s, H - 1 - math.cos(ang) * s, 0.7, rgb('#4f7a32'))
            tx, ty = x0 + math.sin(ang) * L, H - 1 - math.cos(ang) * L
            for p in range(5):
                a = p * 1.2566 + rng.uniform(-0.2, 0.2)
                dot(tx + math.cos(a) * 2.2, ty + math.sin(a) * 2.2, 1.7, rgb(fc))
            dot(tx, ty, 1.3, rgb('#f2c53d') if fc != '#f2c53d' else rgb('#c07a20'))
    img = bpy.data.images.new(name, W, H, alpha=True)
    img.pixels.foreach_set(upright(px, W, H))
    img.file_format = 'PNG'
    try:
        img.pack()
    except Exception:
        pass
    return img


def trail_fn(x, y):
    # packed ochre earth, worn paler, with small stones and a few pine needles blown across
    r = random.Random(x * 7919 + y * 104729)
    k = 1 + 0.06 * math.sin(x * 0.4 + math.sin(y * 0.25) * 2) + r.uniform(-0.07, 0.07)
    if r.random() < 0.035:
        return (0.78 * k, 0.74 * k, 0.66 * k)        # a pebble
    if r.random() < 0.05:
        return (0.48 * k, 0.36 * k, 0.24 * k)        # needles, a dark crumb of earth
    return (0.74 * k, 0.6 * k, 0.42 * k)


def trail_edge_fn(x, y):
    # the frayed edge: earth going over into needles, leaves and moss (round 20c: lighter, no muddy band)
    r = random.Random(x * 15485863 + y * 32452843)
    k = 1 + r.uniform(-0.1, 0.1)
    if r.random() < 0.4:
        return (0.56 * k, 0.47 * k, 0.31 * k)
    if r.random() < 0.3:
        return (0.4 * k, 0.5 * k, 0.26 * k)
    return (0.63 * k, 0.53 * k, 0.37 * k)


M_TRAIL = mat('TrailEarth', '#ffffff', 0.97, image=make_image('trail', 128, 128, trail_fn))
M_TRAIL_EDGE = mat('TrailEdge', '#ffffff', 0.98, image=make_image('trailedge', 128, 128, trail_edge_fn))
def moss_drift(x, y):
    # slow, organic drifts (they repeat with the 128-pixel, 3 m tile): 0..1
    t = math.tau / 128
    return 0.5 + 0.2 * math.sin(2 * t * x + 1.7 * math.sin(3 * t * y + 0.4) + 0.5) + 0.17 * math.sin(3 * t * y + 1.3 * math.sin(2 * t * x + 1.9) + 2.0) \
        + 0.1 * math.sin(5 * t * (x + y) + 1.0 + 0.9 * math.sin(4 * t * y)) + 0.08 * math.sin(7 * t * x - 4 * t * y + 2.6)


MID_MASK = []


def mid_fn(x, y):
    # the half shade (round 20d, the user's pick from test pictures, "option F"): small round clumps of the
    # meadow's grass, 15-25 cm across, on the needles, about half and half, all a shade darker (x 0.85).
    # The clumps sit on a jittered 16 x 16 grid (so it repeats), their edges a little ragged.
    if not MID_MASK:
        import numpy as np
        yy, xx = np.mgrid[0:128, 0:128]
        noise = np.random.default_rng(5).uniform(-0.25, 0.25, (128, 128))
        r = np.random.default_rng(31)
        best = np.zeros((128, 128))
        for j in range(16):
            for i in range(16):
                if r.random() < 0.62:
                    continue
                cx, cy, rad = (i + r.uniform(.2, .8)) * 8, (j + r.uniform(.2, .8)) * 8, r.uniform(3.0, 5.5)
                dx, dy = (xx - cx + 64) % 128 - 64, (yy - cy + 64) % 128 - 64
                best = np.maximum(best, 1 - (dx * dx + dy * dy) / rad ** 2)
        MID_MASK.append((best + noise) > 0.1)
    if MID_MASK[0][127 - y, x]:
        c = lawn(x * 4, y * 4)                                 # (the meadow's lawn, kit.py's lawn(); round 35: no zigzag)
    else:
        c = litter_dry_fn(x, y)
    return (c[0] * 0.85, c[1] * 0.85, c[2] * 0.85)


def litter_dry_fn(x, y):
    # the deepest shade (round 20d: no moss, the half shade has its own step): golden needles, russet leaves,
    # dry grass and a little soft earth, in drifts. Light and warm, never muddy (the user's round-20 feedback).
    t = math.tau / 128
    r = random.Random(x * 2654435761 + y * 40503 + 17)
    d = moss_drift(x, y)
    k = 1 + 0.06 * math.sin(2 * t * x + math.sin(3 * t * y) * 2.5) + r.uniform(-0.09, 0.09)
    v = r.random() * 0.75 + (1 - d) * 0.35
    if v < 0.35:
        return (0.63 * k, 0.53 * k, 0.32 * k)                  # golden needles
    if v < 0.6:
        return (0.57 * k, 0.42 * k, 0.26 * k)                  # russet oak leaves
    if v < 0.82:
        return (0.58 * k, 0.55 * k, 0.34 * k)                  # dry grass
    return (0.5 * k, 0.43 * k, 0.3 * k)                        # soft earth


# the wood's floor: needles and the half shade's tufts as made here (tufts by the paths, needles away), but
# the game draws both from the light map (forest_light()), with the meadow's lawn where it is light and
# the beach's sand where it meets the beach
M_LITTER_DRY = mat('ForestFloorLit', '#ffffff', 0.98, image=make_image('litterdry', 128, 128, litter_dry_fn))
M_MID = mat('ForestMid', '#ffffff', 0.98, image=make_image('midshade', 128, 128, mid_fn))
GROUND_MAT['FOREST'] = M_LITTER_DRY
GROUND_MAT['FORESTMID'] = M_MID


def paving_fade_image():
    """The paving's broken end: the city's panot (four tiles across, 1.2 m) with its pieces thinning out along
    the path, so the footpath gives way to the earth path softly (an alpha mask, in 4-pixel pieces)."""
    W = 256
    px = [0.0] * (W * W * 4)
    for yy in range(W):
        for xx in range(W):
            r_, g_, b_ = panot(xx, yy)
            cx, cy = xx // 6, yy // 6
            h = random.Random(cx * 7919 + cy * 104729).random()
            keep = (1.0 - xx / W) ** 1.3 * 1.15 - 0.1
            i = (yy * W + xx) * 4
            px[i], px[i + 1], px[i + 2], px[i + 3] = r_, g_, b_, (1.0 if h < keep else 0.0)
    img = bpy.data.images.new('panot_fade', W, W, alpha=True)
    img.pixels.foreach_set(px)
    img.file_format = 'PNG'
    try:
        img.pack()
    except Exception:
        pass
    return img


M_PAVE_FADE = mat('PavementFade', '#ffffff', 0.9, image=paving_fade_image(), alpha=True)



M_ALEPPO = mat('LeavesAleppo', '#ffffff', 0.8, image=foliage_image('aleppo', 128, [
    (260, ['#6f8a3a', '#7d9846', '#5f7a31', '#8aa452'], 3, 6, 0.2, 0)], 41), alpha=True)
M_STONEPINE = mat('LeavesStonePine', '#ffffff', 0.8, image=foliage_image('stonepine', 128, [
    (300, ['#3f5f2c', '#4c6e33', '#355226', '#5a7c3c'], 3, 6, 0.22, 0)], 42), alpha=True)
M_HOLM = mat('LeavesHolm', '#ffffff', 0.8, image=foliage_image('holm2', 128, [
    (250, ['#34492a', '#3e5631', '#2b3e23', '#4a6338'], 4, 6, 0.62, 0)], 43), alpha=True)
M_HOLM2 = mat('LeavesHolmB', '#ffffff', 0.8, image=foliage_image('holm3', 128, [
    (250, ['#3c5530', '#476336', '#33492a', '#56713e'], 4, 6, 0.62, 0)], 44), alpha=True)
M_CORKLEAF = mat('LeavesCork', '#ffffff', 0.8, image=foliage_image('cork', 128, [
    (240, ['#4f6638', '#5b7442', '#455a31', '#677f4b'], 4, 7, 0.6, 0)], 45), alpha=True)
M_OLIVE = mat('LeavesOlive', '#ffffff', 0.8, image=foliage_image('olive', 128, [
    (280, ['#7d8a66', '#8e9a76', '#6b7858', '#a3ad8c'], 3, 5, 0.3, 0)], 46), alpha=True)
M_CYPRESS = mat('LeavesCypress', '#ffffff', 0.8, image=foliage_image('cypress', 128, [
    (320, ['#26402a', '#2f4b30', '#203826', '#375636'], 3, 5, 0.5, 0)], 47), alpha=True)
M_CAROB = mat('LeavesCarob', '#ffffff', 0.8, image=foliage_image('carob', 128, [
    (220, ['#2f5228', '#3a6030', '#284722', '#467038'], 5, 8, 0.7, 0)], 48), alpha=True)
M_LENTISK = mat('LeavesLentisk', '#ffffff', 0.8, image=foliage_image('lentisk', 128, [
    (260, ['#3a5a2a', '#466a32', '#324e25'], 3, 5, 0.55, 0), (40, ['#a03a2a', '#c04a32'], 1.5, 2.2, 1.0, 0)], 49), alpha=True)
M_ROSEMARY = mat('LeavesRosemary', '#ffffff', 0.8, image=foliage_image('rosemary', 128, [
    (300, ['#5d7258', '#6a8063', '#51664d'], 3, 6, 0.18, 0), (60, ['#9a8ad0', '#b0a2e0', '#8576c0'], 1.6, 2.4, 1.0, 0)], 50), alpha=True)
M_BROOM = mat('LeavesBroom', '#ffffff', 0.8, image=foliage_image('broom', 128, [
    (220, ['#4f7232', '#5c8238', '#46662c'], 3, 6, 0.2, 0), (110, ['#f2c533', '#e8b520', '#f7d65a'], 2, 3, 0.9, 0)], 51), alpha=True)
M_ARBUTUS = mat('LeavesArbutus', '#ffffff', 0.8, image=foliage_image('arbutus', 128, [
    (220, ['#355c2a', '#406a31', '#2e5024'], 4, 7, 0.55, 0), (36, ['#d8452a', '#e86a2a', '#c23a26'], 1.8, 2.6, 1.0, 0)], 52), alpha=True)
M_TUFT = mat('GrassTuft', '#ffffff', 0.85, image=blade_image('tuft', ['#5f8a3a', '#6e9a42', '#7aa64a', '#557d33', '#8db054'], 61), alpha=True)
M_TUFT2 = mat('GrassTuftDry', '#ffffff', 0.85, image=blade_image('tuft2', ['#8a9a4a', '#9aa656', '#7a8c42', '#a8ac62'], 62), alpha=True)
M_FLOWERS = [mat('Wildflowers%d' % i, '#ffffff', 0.85, image=blade_image('wildfl%d' % i, ['#5f8a3a', '#6e9a42', '#557d33'], 70 + i,
                                                                        flowers=[(c, n)]), alpha=True)
             for i, (c, n) in enumerate((('#f6f2e6', 5), ('#f2c53d', 4), ('#b49ad8', 4), ('#d8443a', 2)))]
def fern_image(name, cols, seed):
    """A fern's frond: a curving stalk up the card with leaflets either side, longest a third of the way up."""
    rng = random.Random(seed)
    W = H = 64
    px = [0.0] * (W * H * 4)
    base = rgb(cols[0])
    for i in range(W * H):
        px[i * 4], px[i * 4 + 1], px[i * 4 + 2] = base

    def dot(x, y, r, col):
        for yy in range(max(0, int(y - r) - 1), min(H, int(y + r) + 2)):
            for xx in range(max(0, int(x - r) - 1), min(W, int(x + r) + 2)):
                if (xx - x) ** 2 + (yy - y) ** 2 <= r * r:
                    i = (yy * W + xx) * 4
                    px[i], px[i + 1], px[i + 2], px[i + 3] = col[0], col[1], col[2], 1.0
    L, bend = 60, 0.35
    for s in range(L):
        f = s / L
        a = bend * f * f
        x, y = W / 2 + math.sin(a) * s * 0.6, H - 1 - math.cos(a) * s
        dot(x, y, 1.1 * (1 - f) + 0.5, rgb(cols[1]))
        if s > 4 and s % 3 == 0:
            ux, uy = math.sin(a), -math.cos(a)
            half = 15 * math.sin(math.pi * min(1.0, f * 1.15)) ** 0.7 * (1 - 0.35 * f)
            col = rgb(rng.choice(cols[1:]))
            for side in (1, -1):
                nx, ny = -uy * side, ux * side
                dx, dy = nx * 0.82 + ux * 0.55, ny * 0.82 + uy * 0.55
                for q in range(int(half)):
                    g = q / max(1.0, half)
                    k = 0.85 + 0.35 * g
                    dot(x + dx * q, y + dy * q, 1.5 * (1 - g) + 0.6, (min(1, col[0] * k), min(1, col[1] * k), min(1, col[2] * k)))
    img = bpy.data.images.new(name, W, H, alpha=True)
    img.pixels.foreach_set(upright(px, W, H))
    img.file_format = 'PNG'
    try:
        img.pack()
    except Exception:
        pass
    return img


M_FERN = mat('Fern', '#ffffff', 0.8, image=fern_image('fern', ['#4f7a34', '#4a7531', '#5a8838', '#689a42', '#77a84c'], 63), alpha=True)
M_TOADCAP = mat('ToadstoolCap', '#d43a2a', 0.45)
M_CEPCAP = mat('MushroomCap', '#9a6438', 0.6)
M_TOADSTEM = mat('ToadstoolStem', '#efe7d4', 0.7)
M_TOADSPOT = mat('ToadstoolSpots', '#fbf6ea', 0.6)
M_OLIVEBARK = mat('OliveBark', '#6f685c', 0.95)
M_CORKBARK = mat('CorkBark', '#67483a', 0.95)    # (round 20d: the whole tree, one warm brown)
M_PINEBARK2 = mat('PineBarkGrey', '#5f4b3c', 0.95)


# ------------------------------------------------------------------ the trees

DET = [1.0]           # fewer leaf cards for the trees deep in the wood, seen only from afar


def NCARDS(count):
    # (round 24: was N(), which north_build.py's `import north as N` overwrote when the hill used these trees)
    return max(4, int(count * DET[0]))


# (round 25) how trunks are drawn, to make the woods lighter: sides of a trunk and of a branch, whether their ends are
# closed (never seen: in the ground, inside the next piece or the leaves), and the thinnest branch drawn (0: all)
TRUNK = {'sides': 6, 'branch_sides': 4, 'caps': False, 'min_branch': 0.0}     # (the user's B: round25/trunks.png)
TWIG_DEEP = 0.1          # deep in the wood (fewer leaf cards there, DET < 1): no branches thinner than this (C)


def limb(mb, p0, p1, r0, r1, m, segs=10):
    d = p1 - p0
    if d.length < 1e-3:
        return
    if r0 < TRUNK['min_branch'] or (DET[0] < 1.0 and r0 < TWIG_DEEP):
        return
    segs = TRUNK['sides'] if segs == 10 else (TRUNK['branch_sides'] or segs)
    M = Matrix.Translation((p0 + p1) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    mb.cone(M, segs, r0, r1, d.length, m, caps=TRUNK['caps'])


def stem(mb, base, h, lean, r0, r1, m, rng, bends=3, wobble=0.25):
    """A trunk in a few bent pieces; returns its top."""
    pts = [base]
    for i in range(1, bends + 1):
        f = i / bends
        pts.append(base + lean * (f ** 1.4) + Vector((rng.uniform(-wobble, wobble), rng.uniform(-wobble, wobble), h * f)))
    for i in range(bends):
        limb(mb, pts[i], pts[i + 1], r0 + (r1 - r0) * i / bends, r0 + (r1 - r0) * (i + 1) / bends, m)
    return pts[-1]


def rnd_dir(rng):
    a = rng.uniform(0, 6.283)
    return Vector((math.cos(a), math.sin(a), 0))


def tree_stone_pine(tr, cr, base, rng, s):
    # the umbrella pine of the Mediterranean coast: a tall bare trunk, often leaning, a wide flat crown
    h = rng.uniform(5.5, 8.0) * s
    top = stem(tr, base, h, rnd_dir(rng) * rng.uniform(0.3, 1.4) * s, 0.2 * s, 0.11 * s, M_PINEBARK, rng)
    rr = rng.uniform(2.2, 3.1) * s
    for k in range(rng.randint(3, 5)):
        d = rnd_dir(rng)
        tip = top + d * rr * rng.uniform(0.45, 0.7) + Vector((0, 0, rng.uniform(0.1, 0.6)))
        limb(tr, top - Vector((0, 0, 0.9)), tip, 0.09 * s, 0.04 * s, M_PINEBARK, 5)
        cr.shell(tip + Vector((0, 0, 0.3)), (rr * 0.55, rr * 0.55, 0.45 * s), NCARDS(12), 1.2 * s, M_STONEPINE, rng)
    cr.shell(top + Vector((0, 0, 0.5)), (rr, rr, 0.7 * s), NCARDS(26), 1.35 * s, M_STONEPINE, rng)
    cr.clump(top + Vector((0, 0, 0.35)), (rr * 0.6, rr * 0.6, 0.3), NCARDS(6), 1.2 * s, M_STONEPINE, rng)


def tree_aleppo(tr, cr, base, rng, s):
    # Aleppo pine: a sinuous, leaning trunk and an airy, uneven crown in tufts, a lighter yellow-green
    h = rng.uniform(5.0, 7.0) * s
    lean = rnd_dir(rng) * rng.uniform(0.6, 1.8) * s
    top = stem(tr, base, h, lean, 0.17 * s, 0.08 * s, M_PINEBARK2, rng, 4, 0.35)
    for k in range(rng.randint(5, 7)):
        f = rng.uniform(0.5, 1.0)
        on = base + lean * (f ** 1.4) + Vector((0, 0, h * f))
        tip = on + rnd_dir(rng) * rng.uniform(0.5, 1.5) * s + Vector((0, 0, rng.uniform(0.2, 0.8)))
        limb(tr, on, tip, 0.06 * s, 0.03 * s, M_PINEBARK2, 5)
        r = rng.uniform(0.8, 1.3) * s
        cr.shell(tip, (r, r, r * 0.6), NCARDS(11), 0.95 * s, M_ALEPPO, rng)
    cr.shell(top + Vector((0, 0, 0.3)), (1.1 * s, 1.1 * s, 0.8 * s), NCARDS(12), 1.0 * s, M_ALEPPO, rng)


def tree_holm(tr, cr, base, rng, s):
    # holm oak, the commonest tree of the wood: a short trunk splitting low, a dense, round, dark crown
    h = rng.uniform(1.3, 2.1) * s
    top = stem(tr, base, h, rnd_dir(rng) * 0.3, 0.22 * s, 0.17 * s, M_FBARK, rng, 2, 0.12)
    m = M_HOLM if rng.random() < 0.55 else M_HOLM2
    lobes = []
    for k in range(rng.randint(2, 4)):
        tip = top + rnd_dir(rng) * rng.uniform(0.6, 1.3) * s + Vector((0, 0, rng.uniform(0.9, 1.8) * s))
        limb(tr, top, tip, 0.14 * s, 0.07 * s, M_FBARK, 6)
        lobes.append(tip)
    for tip in lobes:
        r = rng.uniform(1.2, 1.8) * s
        cr.shell(tip + Vector((0, 0, 0.4 * s)), (r, r, r * 0.8), NCARDS(18), 1.05 * s, m, rng)
    c = sum(lobes, Vector()) / len(lobes) + Vector((0, 0, 0.7 * s))
    cr.shell(c, (2.0 * s, 2.0 * s, 1.5 * s), NCARDS(16), 1.15 * s, m, rng)
    cr.clump(c, (1.2 * s, 1.2 * s, 0.9 * s), NCARDS(6), 1.1 * s, m, rng)


def tree_cork(tr, cr, base, rng, s):
    # cork oak: a stout, gnarled trunk, a broad spreading crown; one warm brown bark, trunk and branches alike
    # (round 20d, the user: one colour to a tree; it was rust red below, as stripped cork, dark brown above)
    h = rng.uniform(1.6, 2.3) * s
    mid = base + Vector((rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), h * 0.55))
    limb(tr, base, mid, 0.3 * s, 0.26 * s, M_CORKBARK)
    top = mid + Vector((rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), h * 0.45))
    limb(tr, mid, top, 0.26 * s, 0.2 * s, M_CORKBARK)
    tips = []
    for k in range(rng.randint(3, 4)):
        tip = top + rnd_dir(rng) * rng.uniform(1.4, 2.3) * s + Vector((0, 0, rng.uniform(0.6, 1.3) * s))
        bend = (top + tip) / 2 + Vector((0, 0, 0.35))
        limb(tr, top, bend, 0.15 * s, 0.11 * s, M_CORKBARK, 6)
        limb(tr, bend, tip, 0.11 * s, 0.06 * s, M_CORKBARK, 6)
        tips.append(tip)
    for tip in tips:
        r = rng.uniform(1.4, 2.0) * s
        cr.shell(tip + Vector((0, 0, 0.3)), (r, r, r * 0.6), NCARDS(18), 1.1 * s, M_CORKLEAF, rng)


def tree_cypress(tr, cr, base, rng, s):
    # Italian cypress: a dark green flame
    h = rng.uniform(5.5, 7.5) * s
    limb(tr, base, base + Vector((0, 0, 1.0)), 0.13 * s, 0.1 * s, M_FBARK, 6)
    w = rng.uniform(0.55, 0.75) * s
    c = base + Vector((0, 0, 0.6 + h / 2))
    cr.shell(c, (w, w, h / 2), NCARDS(44), 0.8 * s, M_CYPRESS, rng, (0.8, 1.0))
    cr.shell(c + Vector((0, 0, h * 0.32)), (w * 0.55, w * 0.55, h * 0.22), NCARDS(12), 0.6 * s, M_CYPRESS, rng)
    cr.clump(c, (w * 0.5, w * 0.5, h * 0.4), NCARDS(8), 0.8 * s, M_CYPRESS, rng)


def tree_olive(tr, cr, base, rng, s):
    # olive: a short, twisted trunk forking low, a light silvery crown
    h = rng.uniform(0.8, 1.2) * s
    top = stem(tr, base, h, rnd_dir(rng) * 0.25, 0.2 * s, 0.17 * s, M_OLIVEBARK, rng, 2, 0.15)
    for k in range(rng.randint(2, 3)):
        tip = top + rnd_dir(rng) * rng.uniform(0.6, 1.1) * s + Vector((0, 0, rng.uniform(1.0, 1.6) * s))
        limb(tr, top, tip, 0.13 * s, 0.06 * s, M_OLIVEBARK, 6)
        for j in range(2):
            r = rng.uniform(0.8, 1.2) * s
            cr.shell(tip + Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(0.0, 0.6))), (r, r, r * 0.7), NCARDS(12), 0.85 * s, M_OLIVE, rng)


def tree_carob(tr, cr, base, rng, s):
    # carob: a broad dome of glossy dark leaves on a short trunk, often wider than it is tall
    h = rng.uniform(1.2, 1.6) * s
    top = stem(tr, base, h, rnd_dir(rng) * 0.2, 0.22 * s, 0.18 * s, M_FBARK, rng, 2, 0.1)
    r = rng.uniform(2.2, 2.8) * s
    c = top + Vector((0, 0, 1.2 * s))
    for k in range(3):
        limb(tr, top, c + rnd_dir(rng) * r * 0.5, 0.12 * s, 0.06 * s, M_FBARK, 6)
    cr.shell(c, (r, r, 1.5 * s), NCARDS(34), 1.2 * s, M_CAROB, rng)
    cr.clump(c, (r * 0.6, r * 0.6, 0.8 * s), NCARDS(8), 1.2 * s, M_CAROB, rng)


SPECIES = {'stone_pine': tree_stone_pine, 'aleppo': tree_aleppo, 'holm': tree_holm, 'cork': tree_cork,
           'cypress': tree_cypress, 'olive': tree_olive, 'carob': tree_carob}
FRINGE_MIX = [('olive', 3), ('stone_pine', 2.5), ('carob', 2), ('cypress', 1.5), ('holm', 1.5)]
WOOD_MIX = [('holm', 5.5), ('aleppo', 2.2), ('stone_pine', 1.3), ('cork', 1.6), ('cypress', 0.3)]
SHRUBS = [(M_LENTISK, 3), (M_ROSEMARY, 1.5), (M_BROOM, 1.5), (M_ARBUTUS, 1.5), (M_SHRUB, 1)]


def pick(mix, rng):
    return rng.choices([a for a, _ in mix], [w for _, w in mix])[0]


# ------------------------------------------------------------------ planting

# ------------------------------------------------------------------ the earth paths' ribbons
# Round 23, the user: "the edges of it are just darker, whereas it should get sharply darker where it irregularly
# fades or cuts into the green grass. Please give me some options". TRAIL_STYLE picks one:
#   'current'  (round 20) a frayed band of darker litter-earth round a paler core
#   'A'        a sharp, irregular cut: the earth runs right up to a jagged edge, with a thin dark lip where it meets
#              the grass
#   'B'        worn ragged: the edge breaks up into tongues and islands of earth in the grass, darker as they thin
#   'C'        sunken: the path is trodden down into the ground, a wider dark band along each side under the grass
#              (crisp, gently wavy)
TRAIL_STYLE = os.environ.get('TRAIL_STYLE', 'G')     # (round 25, the user: "Option 3 (gravel) for the main path")
GLADE_TRAIL = 'D2'                                   # ("and option 2 (dirt) into the glades, but then stopping at the start")
EDGE_OUT = {'A': 0.35, 'B': 0.6, 'C': 0.3}          # how far (m) past the path's half width the edge strip reaches
EDGE_IN = 0.25                                       # and how far inside it


def edge_image(style):
    """The path's edge, u along (256 px = 4 m), v across (64 px: v=0 inside the path, v=1 out in the grass), with an
    alpha mask: earth where the path is, nothing (the grass of the floor below shows) past its edge."""
    W, H = 256, 64
    rr = random.Random(ord(style) * 31)
    ph = [rr.uniform(0, 6.28) for _ in range(6)]
    px = [0.0] * (W * H * 4)
    tw = math.tau / W
    reach = (EDGE_IN + EDGE_OUT[style])
    for xx in range(W):
        # where the edge lies across the strip, wandering along it (repeats every 4 m)
        n = (math.sin(xx * tw * 3 + ph[0]) * 0.5 + math.sin(xx * tw * 7 + ph[1]) * 0.3 + math.sin(xx * tw * 17 + ph[2]) * 0.2)
        if style == 'C':
            n = math.sin(xx * tw * 2 + ph[0]) * 0.6 + math.sin(xx * tw * 5 + ph[1]) * 0.4
        jag = rr.uniform(-1, 1) * (0.05 if style == 'A' else 0.02)
        edge = (EDGE_IN + (0.12 if style == 'B' else 0.1) * n + jag) / reach        # (as a share of v)
        for yy in range(H):
            v = (yy + 0.5) / H
            d = (edge - v) * reach                                                    # metres inside the edge
            k = 1 + 0.06 * math.sin(xx * 0.9 + yy * 0.4) + random.Random(xx * 7919 + yy * 104729).uniform(-0.06, 0.06)
            col = (0.74 * k, 0.6 * k, 0.42 * k)                                       # the path's own earth
            a = 1.0 if d > 0 else 0.0
            if style == 'A':
                if 0 < d < 0.07:
                    col = (0.36 * k, 0.27 * k, 0.17 * k)                              # the dark lip
                elif 0.07 <= d < 0.12:
                    col = (0.55 * k, 0.43 * k, 0.29 * k)
            elif style == 'B':
                if d <= 0:
                    # islands and tongues of bare earth out into the grass, fewer further out
                    cx, cy = xx // 5, yy // 4
                    h = random.Random(cx * 131 + cy * 977 + 5).random()
                    if h < 0.55 * math.exp(d / 0.12):
                        a, col = 1.0, (0.45 * k, 0.35 * k, 0.23 * k)
                elif d < 0.1:
                    col = (0.5 * k, 0.39 * k, 0.26 * k)
            elif style == 'C':
                if 0 < d < 0.16:
                    t = d / 0.16
                    col = tuple(c * (0.42 + 0.4 * t) for c in (0.74 * k, 0.6 * k, 0.42 * k))   # shade under the bank
            i = (yy * W + xx) * 4
            px[i], px[i + 1], px[i + 2], px[i + 3] = min(1, col[0]), min(1, col[1]), min(1, col[2]), a
    img = bpy.data.images.new('trailedge_' + style, W, H, alpha=True)
    img.pixels.foreach_set(px)
    img.file_format = 'PNG'
    try:
        img.pack()
    except Exception:
        pass
    return img


exec(open(os.path.join(HERE, 'trails.py')).read())          # (round 24: the new worn paths, D1 / D2 / G)


def forest_ribbon_paths():
    """The wood's paths (not the meadow's paved ones) in metres, for trails.py."""
    return [{'pts': [((x - OX) * T, (y - OY) * T) for (x, y) in P['pts']], 'w': P['w'], 'taper': P['kind'] == 'trail',
             'style': GLADE_TRAIL if P['kind'] in ('spur', 'trail') else TRAIL_STYLE, 'round_end': P.get('round_end', False)}
            for P in PATHS if P['kind'] != 'meadow' and len(P['pts']) > 1]


def build_trails(style, name='Trails'):
    if style in TRAIL_STYLES:
        return build_ribbons(forest_ribbon_paths(), style, lambda x, z: ground_z(x / T + OX, z / T + OY), name,
                             [((jx - OX) * T, (jy - OY) * T) for (jx, jy) in JUNCTIONS])
    trail = MB(uv=True)
    # each path's rows (its middle, sideways, half width and frayed edges), then drawn in two layers over
    # all the paths at once: the frayed edges, and the trodden cores on top, so where two
    # paths cross their cores run into each other (an edge never cuts across another path)
    rows_of = []
    for pi, P in enumerate(PATHS):
        if P['kind'] == 'meadow':
            continue
        pts = P['pts']
        hw = P['w'] / 2
        r = random.Random(pi * 97)
        rows = []
        u = 0.0
        for i in range(len(pts)):
            j0, j1 = max(0, i - 1), min(len(pts) - 1, i + 1)
            tx, ty = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
            L = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / L, tx / L
            w = hw * (1 + 0.14 * math.sin(i * 0.37 + pi) + 0.08 * math.sin(i * 1.13))
            if P['kind'] == 'trail':
                w *= min(1.0, 0.45 + (len(pts) - 1 - i) * 0.08)              # (full width where it leaves the long path)
            if i:
                u += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) * T
            rows.append((pts[i][0], pts[i][1], nx, ny, w, r.uniform(0.15, 0.5), r.uniform(0.15, 0.5), u))
        rows_of.append(rows)

    def strip(rows, cols, z, m, uv):
        # cols: [(offset (m) from a row's (w, fl, fr), v)], drawn as quads between neighbouring columns
        prev = None
        for (x, y, nx, ny, w, fl, fr, u) in rows:
            row = [(BT(x + nx * f(w, fl, fr) / T, y + ny * f(w, fl, fr) / T, z), v) for f, v in cols]
            if prev is not None:
                for k in range(len(cols) - 1):
                    q = [prev[0][k][0], prev[0][k + 1][0], row[k + 1][0], row[k][0]]
                    if uv == 'world':
                        uvs = [(p_.x / 1.6, p_.y / 1.6) for p_ in q]
                    else:
                        uvs = [(prev[1] / 4.0, prev[0][k][1]), (prev[1] / 4.0, prev[0][k + 1][1]), (u / 4.0, row[k + 1][1]), (u / 4.0, row[k][1])]
                    trail.face(q, m, normal=(0, 0, 1), uvs=uvs)
            prev = (row, u)
    if style == 'current':
        for rows in rows_of:
            strip(rows, [(lambda w, fl, fr: -(w + fl), 0), (lambda w, fl, fr: w + fr, 0)], 0.077, M_TRAIL_EDGE, 'world')
        for rows in rows_of:
            strip(rows, [(lambda w, fl, fr: -w * 0.62, 0), (lambda w, fl, fr: w * 0.62, 0)], 0.087, M_TRAIL, 'world')
        return trail.finish(name)
    m_edge = mat('TrailEdge' + style, '#ffffff', 0.97, image=edge_image(style), alpha=True)
    out = EDGE_OUT[style]
    # every path's edges first, then every path's earth on top, reaching nearly to the edge, so where two paths
    # cross, one's edge never draws a line across the other (u along at 4 m, v from inside to out)
    for rows in rows_of:
        strip(rows, [(lambda w, fl, fr: w - EDGE_IN, 0.0), (lambda w, fl, fr: w + out, 1.0)], 0.083, m_edge, 'strip')
        strip(rows, [(lambda w, fl, fr: -(w - EDGE_IN), 0.0), (lambda w, fl, fr: -(w + out), 1.0)], 0.083, m_edge, 'strip')
    for rows in rows_of:
        strip(rows, [(lambda w, fl, fr: -(w - 0.18), 0), (lambda w, fl, fr: w - 0.18, 0)], 0.087, M_TRAIL, 'world')
    return trail.finish(name)


def plant_forest():
    chunks = {}

    def chunk(x, y, kind):
        key = (int(x // 12), int(y // 12), kind)
        if key not in chunks:
            chunks[key] = MB(uv=True) if kind in ('trunks', 'fartrunks', 'walltrunks') else Cards()
        return chunks[key]

    class Both:
        """Each tree is made twice: in full (seen close to), and as a far version a fraction of the cost
        (every fifth leaf card, each much bigger; round 25: no trunk at all, just the bushy tops), which the game
        swaps in beyond about a hundred metres."""
        def __init__(self, near, far, k, leaves=False):
            self.near, self.far, self.k, self.leaves = near, far, k, leaves

        def shell(self, c, radii, count, size, m, rng, depth=(0.72, 1.0)):
            if self.leaves:
                BLOBS.append((c.copy(), radii, size, m.name))            # (for the light on the floor)
            self.near.shell(c, radii, count, size * self.k, m, rng, depth)
            self.far.shell(c, radii, max(3, count // 5), size * 2.1, m, random.Random(int(c.x * 97 + c.y * 31)), depth)

        def clump(self, c, radii, count, size, m, rng, up_bias=0.0):
            if self.leaves:
                BLOBS.append((c.copy(), radii, size, m.name))
            self.near.clump(c, radii, count, size * self.k, m, rng, up_bias)

        def cone(self, M, segs, r1, r2, depth, m, smooth=True, caps=True):
            # (round 25, the user: far away "you don't need branches and stems, really just the bushy green tree tops")
            self.near.cone(M, segs, r1, r2, depth, m, smooth, caps)

    class Cheap:
        """(round 25) a tree out of reach past the wood's rise: its bushy top, a few big leaf cards, on a bare four-sided
        trunk (its main pieces only: nothing floats)"""
        def __init__(self, cards, mb=None):
            self.cards, self.mb = cards, mb

        def shell(self, c, radii, count, size, m, rng, depth=(0.72, 1.0)):
            # (round 26: the few huge cards read as a green tent floating over the far wood; more, smaller)
            BLOBS.append((c.copy(), radii, size, m.name))        # (round 38: their shade on the floor too — the floor past the rise was all lawn, a straight line at x 188)
            self.cards.shell(c, radii, max(5, count // 3), size * 1.25, m, random.Random(int(c.x * 97 + c.y * 31)), depth)

        def clump(self, *a, **k):
            pass

        def cone(self, M, segs, r1, r2, depth, m, smooth=True, caps=True):
            if self.mb is not None and r1 >= 0.13:
                self.mb.cone(M, 4, r1, r2, depth, m, smooth, False)

    def plant(x, y, sp, solid, s=None):
        xm_, zm_ = mT(x, y)
        for gzn in (NORTH.GRACIA_ZONE, NORTH.GRACIA_EXT):   # (round 26: not in Gràcia's streets and blocks)
            if gzn[0] - 1.0 < xm_ < gzn[2] + 1.0 and gzn[1] - 1.0 < zm_ < gzn[3] + 1.0:
                return
        base = BT(x, y, ground_z(x, y) - 0.01)          # (round 24: on the ground, where it rises past the wood's end)
        s = s or frng.uniform(0.8, 1.15)
        if past_rise(x, y):
            SPECIES[sp](Cheap(None, chunk(x, y, 'walltrunks')), Cheap(chunk(x, y, 'wallleaves')), base, frng, s)
            return
        k = 1.0 / math.sqrt(DET[0]) if DET[0] < 1.0 else 1.0
        leaves = Both(chunk(x, y, 'leaves'), chunk(x, y, 'farleaves'), k, True)
        trunks = Both(chunk(x, y, 'trunks'), chunk(x, y, 'fartrunks'), 1.0)
        SPECIES[sp](trunks, leaves, base, frng, s)
        if solid:
            TRUNKS.setdefault((int(x), int(y)), []).append((x, y))
            scene['trees'].append(mT(x, y))
            scene.setdefault('forest_trees', []).append(mT(x, y))       # (the ones she may slip between)

    def shrub(x, y, rr, m=None):
        xm_, zm_ = mT(x, y)
        for gzn in (NORTH.GRACIA_ZONE, NORTH.GRACIA_EXT):   # (round 26, the user: "Bushes don't sit on the pavement")
            if gzn[0] - 1.0 < xm_ < gzn[2] + 1.0 and gzn[1] - 1.0 < zm_ < gzn[3] + 1.0:
                return
        m = m or pick(SHRUBS, frng)
        c = BT(x, y, ground_z(x, y) + 0.15 + rr * 0.35)
        BLOBS.append((c, (rr, rr, rr * 0.6), 0.7, 'bush'))
        chunk(x, y, 'plants').clump(c, (rr, rr, rr * 0.6), 7 + int(rr * 4), 0.7, m, frng)

    # trees: on a jittered grid, closer together the deeper into the wood; never on a path or in a glade
    placed = 0
    for Y4 in range(4 * 6, 4 * 110):
        for X4 in range(4 * (FOREST_X0 - 4), 4 * (MW2 + 22)):
            if Y4 >= 4 * 86 and X4 < 4 * 105:
                continue
            x, y = X4 / 4 + frng.uniform(0, 0.25), Y4 / 4 + frng.uniform(0, 0.25)
            X, Y = int(math.floor(x)), int(math.floor(y))
            dpt = depth(x, y)
            wood = is_wood(X, Y)
            if wood:
                if y > tree_end(x) and not east_wood(x, y):
                    continue                                    # (the trees stop short of the beach)
                spacing = 2.2 if dpt < FRINGE else (1.15 if dpt < FRINGE + 1.2 else 0.72)
                if y > tree_end(x) - 2.5:
                    spacing = max(spacing, 1.6)                 # thinning out towards the sand
                if past_rise(x, y):
                    spacing = 1.25                              # (round 25: bigger tops, fewer of them)
                if east_wood(x, y) and y > tree_end(x) - 2.5:
                    spacing = 1.0                               # (round 24: the headland, wooded to its cliffs)
            elif tile(X, Y) == 'GRASS' and x >= 83.2 and Y < 85:
                spacing = 4.5                                   # the meadow: a very few trees, far apart
            else:
                continue
            if frng.random() > 1.0 / (spacing * spacing * 16.0):     # (16 candidates to a tile)
                continue
            pd, _ = path_dist(x, y)
            if pd < 0.32 or in_clearing(x, y, 0.9) or any(math.hypot(x - ex, y - ey) < 1.2 for ex, ey, _, _ in ENTRANCES_F):
                continue
            if near_junction(x, y, 0.85):
                continue                                        # (the corners where paths meet stay open)
            if wood and tile(X, Y) == 'BOULDER':
                continue
            walk = True                                         # (every trunk is solid; the wood itself can be walked)
            sp = pick(FRINGE_MIX if (not wood or dpt < FRINGE + 0.6) else WOOD_MIX, frng)
            if pd < 0.7 and sp in ('cypress', 'cork', 'carob'):
                sp = 'holm'                                     # (the broad ones stand back from the path)
            DET[0] = 1.0 if (pd < 2.5 or dpt < FRINGE + 2.5 or not wood) else (0.55 if X < MW2 else 0.4)
            plant(x, y, sp, walk)
            placed += 1
    # a few more trees in the meadow near the road, standing on their own, for a park's feel
    prk = random.Random(77)
    for yy in (12.6, 21.5, 35.8, 48.7, 61.9, 75.4, 81.2):
        for _ in range(12):
            x, y = prk.uniform(82.7, 84.2), yy + prk.uniform(-1.2, 1.2)
            if path_dist(x, y)[0] > 0.9 and tile(int(x), int(y)) == 'GRASS' and \
                    all(math.hypot(x - ex, y - ey) > 2.0 for ex, ey, _, _ in ENTRANCES_F):
                plant(x, y, prk.choice(('stone_pine', 'olive', 'carob', 'olive')), True, prk.uniform(0.9, 1.15))
                placed += 1
                break
    # the pocket (POCKETS): trees like the wood's round it, a little over three metres apart
    keep_ = frng.getstate()
    pkr = random.Random(2020)
    for poly in POCKETS:
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        Y4 = min(ys)
        while Y4 < max(ys):
            X4 = min(xs)
            while X4 < max(xs):
                x, y = X4 + pkr.uniform(0.15, 0.85), Y4 + pkr.uniform(0.15, 0.85)
                if in_pocket(x, y, 0.15) > 0 and path_dist(x, y)[0] > 0.5 and not near_junction(x, y, 0.85) and \
                        all(math.hypot(x - tx, y - ty) > 0.6 for b in ((int(x) + i, int(y) + j) for i in (-1, 0, 1) for j in (-1, 0, 1))
                            for tx, ty in TRUNKS.get(b, ())):
                    DET[0] = 1.0
                    plant(x, y, pick(WOOD_MIX, pkr), True, pkr.uniform(0.85, 1.1))
                    placed += 1
                X4 += 1.0
            Y4 += 1.0
    frng.setstate(keep_)
    # undergrowth: thick in the wood (a dense band along the fringe hides where it can't be walked);
    # low and sparse beside the paths, so they stay open
    for Y2 in range(2 * 6, 2 * 110):
        for X2 in range(2 * FOREST_X0, 2 * (MW2 + 18)):
            if Y2 >= 2 * 86 and X2 < 2 * 105:
                continue
            x, y = X2 / 2 + frng.uniform(0, 0.5), Y2 / 2 + frng.uniform(0, 0.5)
            if past_rise(x, y):
                continue                                        # (round 25: nobody sees under those trees)
            if not is_wood(int(x), int(y)) or in_clearing(x, y, 0.4) or (y > tree_end(x) + 0.2 and not east_wood(x, y)):
                continue
            dpt = depth(x, y)
            if east_wood(x, y) and y > tree_end(x) - 1.5:
                if frng.random() < 0.35:                         # (round 24: the headland's scrub, to the cliff tops)
                    shrub(x, y, frng.uniform(0.5, 0.9))
                continue
            if y > tree_end(x) - 1.5:
                if frng.random() < 0.06:
                    shrub(x, y, frng.uniform(0.3, 0.55), pick([(M_ROSEMARY, 2), (M_BROOM, 1)], frng))
                continue
            pd, _ = path_dist(x, y)
            if pd < 0.12:
                continue
            if near_junction(x, y):
                if frng.random() < 0.1:                         # (a little low green at the corners, ridden past)
                    shrub(x, y, frng.uniform(0.25, 0.4), pick([(M_ROSEMARY, 2), (M_LENTISK, 1)], frng))
                continue
            if dpt < FRINGE - 0.3:
                if frng.random() < 0.08:
                    shrub(x, y, frng.uniform(0.35, 0.6), pick([(M_ROSEMARY, 2), (M_BROOM, 2)], frng))
                continue
            if pd < 0.45:
                if frng.random() < 0.35:
                    shrub(x, y, frng.uniform(0.3, 0.5))
                continue
            band = dpt < FRINGE + 0.8
            if frng.random() < (0.95 if band else 0.8):
                shrub(x, y, frng.uniform(0.7, 1.2) if band else frng.uniform(0.6, 1.15))
    for (kx, ky, kind), obj in chunks.items():
        if kind == 'fartrunks':
            obj.bm.free()
            continue
        name = {'trunks': 'ForestTrunks_m%d_%d', 'leaves': 'Leaves_forest_m%d_%d', 'plants': 'Plants_forest_%d_%d',
                'farleaves': 'Leaves_far_%d_%d', 'fartrunks': 'ForestFar_%d_%d', 'wallleaves': 'Leaves_wall_%d_%d', 'walltrunks': 'WallTrunks_%d_%d'}[kind] % (kx, ky)
        city_objs.append(obj.finish(name))
    print('FOREST trees', placed, 'paths', len(PATHS), 'glades', len(CLEARINGS))
    forest_light()                                               # (what grows on the floor, by the light)

    # ---------------------------------------------------------------- the paths, worn into the earth
    trail = MB(uv=True)
    paved = MB(uv=True)
    for pi, P in enumerate(PATHS):
        if P['kind'] != 'meadow':
            continue
        # the footpath across the meadow: the city's panot, narrower, with a stone edging either side; its
        # last metre and a bit breaks up (an alpha-masked copy of the paving) onto the earth path under it
        pts = P['pts']
        hw = P['w'] / 2 / T
        (ax, ay), (bx, by) = pts[0], pts[-1]
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        nx, ny = -uy, ux
        z = 0.1
        fade = 1.2 / T
        cut = L - fade
        q = [BT(ax + nx * hw, ay + ny * hw, z), BT(ax + ux * cut + nx * hw, ay + uy * cut + ny * hw, z),
             BT(ax + ux * cut - nx * hw, ay + uy * cut - ny * hw, z), BT(ax - nx * hw, ay - ny * hw, z)]
        paved.face(q, M_PANOT, normal=(0, 0, 1), uvs=[(p_.x / 0.6, p_.y / 0.6) for p_ in q])
        e = 0.09 / T
        for sgn in (1, -1):
            o0, o1 = hw * sgn, (hw + e) * sgn
            q = [BT(ax + nx * o0, ay + ny * o0, z + 0.025), BT(ax + ux * cut + nx * o0, ay + uy * cut + ny * o0, z + 0.025),
                 BT(ax + ux * cut + nx * o1, ay + uy * cut + ny * o1, z + 0.025), BT(ax + nx * o1, ay + ny * o1, z + 0.025)]
            paved.face(q, M_KERB, normal=(0, 0, 1))
        c0, c1 = cut, L
        q = [BT(ax + ux * c0 + nx * hw, ay + uy * c0 + ny * hw, z), BT(ax + ux * c1 + nx * hw, ay + uy * c1 + ny * hw, z),
             BT(ax + ux * c1 - nx * hw, ay + uy * c1 - ny * hw, z), BT(ax + ux * c0 - nx * hw, ay + uy * c0 - ny * hw, z)]
        paved.face(q, M_PAVE_FADE, normal=(0, 0, 1), uvs=[(0, 1), (1, 1), (1, 0), (0, 0)])
    city_objs.append(paved.finish('MeadowFootpaths'))
    city_objs.append(build_trails(TRAIL_STYLE))

    # ---------------------------------------------------------------- the meadow: grass tufts and wild flowers
    grass = {}

    def gchunk(x, y):
        key = (int(x // 10), int(y // 10))
        if key not in grass:
            grass[key] = Cards()
        return grass[key]

    def tuft(x, y, size, m):
        c = BT(x, y, ground_z(x, y) + size * 0.45)            # (its foot a hair under the ground)
        a = frng.uniform(0, 3.14)
        g = gchunk(x, y)
        for k in range(3):
            rot = vertical(a + k * 1.0472) @ Matrix.Rotation(frng.uniform(-0.15, 0.15), 3, 'X')
            g.card(c, size, rot, c - Vector((0, 0, size)), m, 0.35)

    n_t = n_f = 0

    def drift(x, y):
        # grass grows in drifts and patches, not evenly: a slow wobble of more and less
        return 0.5 + 0.28 * math.sin(x * 1.7 + math.sin(y * 0.9) * 2.0) + 0.22 * math.sin(y * 1.3 + x * 0.6)
    for Y8 in range(8 * 8, 8 * 86):
        for X8 in range(8 * 81, 8 * (MW2 + 2)):
            x, y = X8 / 8 + frng.uniform(0, 0.125), Y8 / 8 + frng.uniform(0, 0.125)
            X, Y = int(math.floor(x)), int(math.floor(y))
            k = tile(X, Y)
            if is_wood(X, Y):
                g_, s_ = light_at(x, y)
                lit = g_ * (1.0 - s_)                                     # (in the wood, as much as the light lets grow)
                grassy = lit > 0.3 and frng.random() < lit
            else:
                grassy = k == 'GRASS' and x >= 82.05
            pd, which = path_dist(x, y)
            if not grassy or in_north(X, Y):
                continue                                                  # (round 26: not on Gràcia's paving)
            if pd < 0.06:                                                 # (round 40, rule 82: no tuft or flower on any path's drawn edge)
                continue                                                  # (nothing grows on the footpaths)
            dr = drift(x, y) * (1.7 if 0 < pd < 0.2 else 1.0)              # (thicker along the paths' edges)
            if frng.random() < 0.26 * dr * dr:          # (round 28, the user: "less grass in the field")
                tuft(x, y, frng.uniform(0.2, 0.36), M_TUFT if frng.random() < 0.75 else M_TUFT2)
                n_t += 1
            elif frng.random() < 0.012 * (1.0 + math.sin(x * 0.9 + y * 2.3)) ** 2:
                fm = M_FLOWERS[int(abs(math.sin(x * 0.31) + math.cos(y * 0.23)) * 2.2) % len(M_FLOWERS)]
                tuft(x, y, frng.uniform(0.22, 0.32), fm)
                n_f += 1
    # (round 32, the user: "review the parts where the city joins the nature" — the west meadow was bare lawn
    # from the footpath to the hills. Tufts and wild flowers there too: thicker by the pavement and along the
    # river's banks, thinning across the far field; its own random numbers, so nothing else replants.)
    wrng = random.Random(3203)
    for Y8 in range(8 * 14, 8 * 84):
        for X8 in range(8 * -7, 8 * 7):
            x, y = X8 / 8 + wrng.uniform(0, 0.125), Y8 / 8 + wrng.uniform(0, 0.125)
            X, Y = int(math.floor(x)), int(math.floor(y))
            if X >= 0 and tile(X, Y) != 'GRASS':
                continue                                              # (the river, the road out and the bridge keep clear)
            if X < 0 and abs(y - 43.0) < 1.3 and x > -9.5:
                continue                                              # (not on the worn track past the bridge)
            if WEST_FIELDS and x < -3.0 and y > 14.6:
                continue                                              # (round 41: farm fields there now, world2d.py)
            dr = drift(x, y)
            p_ = 0.16 * dr * dr
            if x > 5.1 or -2.2 < x < 0.3:
                p_ *= 1.9                                             # (thicker by the footpath and the banks)
            elif x < -2.2:
                p_ *= 0.55                                            # (the far field, sparser)
            if wrng.random() < p_:
                tuft(x, y, wrng.uniform(0.2, 0.36), M_TUFT if wrng.random() < 0.75 else M_TUFT2)
                n_t += 1
            elif wrng.random() < 0.01 * (1.0 + math.sin(x * 1.1 + y * 2.1)) ** 2:
                fm = M_FLOWERS[int(abs(math.sin(x * 0.37) + math.cos(y * 0.27)) * 2.2) % len(M_FLOWERS)]
                tuft(x, y, wrng.uniform(0.22, 0.3), fm)
                n_f += 1
    # ---------------------------------------------------------------- in the shade: ferns, toadstools, woodland flowers
    # (round 20c, a magical wood: where the light is poor, the floor is mossy and ferns grow in drifts, with
    # little red-capped toadstools and brown mushrooms in twos and threes, and white and blue flowers here and
    # there; never on the paths or in the glades. Their own random numbers, so the wood's planting is unchanged.)
    srng = random.Random(2020)
    shrooms = {}

    def schunk(x, y):
        key = (int(x // 12), int(y // 12))
        if key not in shrooms:
            shrooms[key] = MB()
        return shrooms[key]

    def fern(x, y, size):
        c0 = BT(x, y, ground_z(x, y))
        a0 = srng.uniform(0, 6.28)
        g = gchunk(x, y)
        for k in range(srng.randint(5, 7)):
            rot = vertical(a0 + k * 1.0 + srng.uniform(-0.25, 0.25)) @ Matrix.Rotation(srng.uniform(0.55, 0.95), 3, 'X')
            c = c0 + rot @ Vector((0, size / 2, 0))
            g.card(c, size * srng.uniform(0.85, 1.1), rot, c0 - Vector((0, 0, size * 0.5)), M_FERN, 0.35)

    def toadstool(x, y, h, red):
        mb = schunk(x, y)
        base = BT(x, y, ground_z(x, y) - 0.01)
        lean = Vector((srng.uniform(-0.06, 0.06), srng.uniform(-0.06, 0.06), 0))
        top = base + Vector((0, 0, h)) + lean * h
        limb(mb, base, top, 0.055 * h / 0.22, 0.04 * h / 0.22, M_TOADSTEM, 7)
        R = h * srng.uniform(0.6, 0.8)
        mb.sphere(Matrix.Translation(top) @ Matrix.Diagonal((R, R, R * 0.55, 1.0)), 1.0, M_TOADCAP if red else M_CEPCAP, (10, 6))
        if red:
            for k in range(5):
                a, e = srng.uniform(0, 6.28), srng.uniform(0.35, 1.2)
                d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e) * 0.55))
                mb.sphere(Matrix.Translation(top + Vector((d.x * R, d.y * R, d.z * R))), R * 0.13, M_TOADSPOT, (6, 3))

    n_fern = n_shroom = n_wf = 0
    for Y2 in range(2 * 6, 2 * 85):
        for X2 in range(2 * FOREST_X0, 2 * (MW2 + 12)):
            x, y = X2 / 2 + srng.uniform(0, 0.5), Y2 / 2 + srng.uniform(0, 0.5)
            if not is_wood(int(x), int(y)) or y > tree_end(x) or in_clearing(x, y, 0.2):
                continue
            g_, s_ = light_at(x, y)
            if g_ > 0.45 or s_ > 0.2 or path_dist(x, y)[0] < 0.12:
                continue
            if any((tx - x) ** 2 + (ty - y) ** 2 < 0.12 ** 2 for tx, ty in TRUNKS.get((int(x), int(y)), ())):
                continue
            shade = 1.0 - g_ / 0.45
            drift_ = max(0.0, 0.5 + 0.5 * math.sin(x * 1.13 + math.sin(y * 0.71) * 2.0) * math.cos(y * 0.83 - x * 0.37))
            roll = srng.random()
            if roll < 0.32 * shade * drift_ * drift_ * 2.2:
                fern(x, y, srng.uniform(0.45, 0.75))
                n_fern += 1
            elif roll > 0.9935:                  # (round 36, the user: "too many brown mushrooms" — about half as many)
                red = False                      # (round 27, the user: only the pickable mushrooms are red)
                for k in range(srng.randint(1, 2)):
                    toadstool(x + srng.uniform(-0.12, 0.12), y + srng.uniform(-0.12, 0.12), srng.uniform(0.14, 0.26), red)
                    n_shroom += 1
            elif roll > 0.955:
                tuft(x, y, srng.uniform(0.16, 0.24), M_FLOWERS[0] if srng.random() < 0.55 else M_FLOWERS[2])
                n_wf += 1
    for (kx, ky), g in grass.items():
        city_objs.append(g.finish('Grass_meadow_%d_%d' % (kx, ky)))
    for (kx, ky), mb in shrooms.items():
        city_objs.append(mb.finish('Detail_toadstools_%d_%d' % (kx, ky)))
    print('MEADOW tufts', n_t, 'flowers', n_f)
    print('SHADE ferns', n_fern, 'toadstools', n_shroom, 'woodland flowers', n_wf)

    # ---------------------------------------------------------------- a lamp by each way into the wood
    for (x, y, dx, dy) in ENTRANCES_F:
        L = math.hypot(dx, dy)
        sx, sy = -dy / L, dx / L
        lx, ly = x - dx / L * 0.5 + sx * 0.75, y - dy / L * 0.5 + sy * 0.75
        lamp_post(lx - OX, ly - OY, (-sx, sy))

    # ---------------------------------------------------------------- where it can't be walked: nowhere now
    # (only the trunks are solid; the game ropes off the thick of the wood from the bike: main.gd, forest_ropes(),
    # from the trunks and these paths, with their widths in metres)
    scene['forest_blocked'] = []
    scene['forest_paths'] = [{'kind': P['kind'], 'w': P['w'], 'pts': [mT(x, y) for (x, y) in P['pts'][::4]]} for P in PATHS]
