# The land round the city, laid out exactly as in the 2D game (its tile map, from2d/data2d.json):
#   the mountains along the north, with the Tibidabo terrace on a shelf, its rides and the Temple del
#   Sagrat Cor, the steps down and the funicular station; the Llobregat along the west with the closed
#   bridge at the end of Carrer de Mallorca; the thick forest in the east with its paths; the
#   Passeig Marítim, the beach and the sea in the south; and, beyond them all, far hills.
# Also the city's own edge (the footpath round it, the Rambla's promenade) and the street things the
# 2D game places (benches, lamps, the kiosk, the flower stall, the Canaletes fountain, Miró's mosaic,
# bins, umbrellas, signs). Run from build_assets.py (exec'd there, sharing its helpers).
#
# Heights: everything natural is one ground mesh, a grid of heights every half tile, which scene.json
# also carries ("terrain") so the game puts Sandra and everyone else on it. What can't be walked
# through (rock, water, the forest's trees, rails, hedges, rides) goes into "blocked", as rectangles.

nrng = random.Random(2024)


# ------------------------------------------------------------------ textures and materials

def sand_fn(x, y):
    v = 1.0 + nrng.uniform(-0.05, 0.05) + 0.03 * math.sin(x * 0.35 + math.sin(y * 0.2) * 2)
    return (0.93 * v, 0.84 * v, 0.66 * v)


def hill_fn(x, y):
    # Collserola's wooded hills: pine and holm oak all over, a few paler clearings
    v = math.sin(x * 0.11 + math.sin(y * 0.07) * 3) + math.sin(y * 0.13 + math.sin(x * 0.05) * 2)
    k = 1.0 + nrng.uniform(-0.08, 0.08)
    if v > 1.55:
        return (0.36 * k, 0.43 * k, 0.27 * k)        # clearings
    # (round 29: (x*7 + y*13) % 7 depends only on y, so the "tree dots" fell in straight rows that read as
    # striped fields on the big hill faces seen from the park's east gates; a per-pixel hash scatters them)
    if random.Random(x * 977 + y * 419).random() < 0.4:
        return (0.15 * k, 0.26 * k, 0.13 * k)        # trees, as dark dots
    return (0.25 * k, 0.37 * k, 0.19 * k)


def rock_fn(x, y):
    # the mountain behind the city: green scrub and grass under its trees, with a little grey rock showing
    v = 0.5 + 0.25 * math.sin(x * 0.4 + math.sin(y * 0.3) * 2) + 0.25 * math.sin(y * 0.23 + x * 0.1)
    k = 0.85 + 0.3 * v + nrng.uniform(-0.06, 0.06)
    if (x // 9 + y // 7) % 7 == 0 and v > 0.6:
        return (0.5 * k, 0.48 * k, 0.43 * k)        # a rocky outcrop
    if nrng.random() < 0.18:
        return (0.2 * k, 0.3 * k, 0.15 * k)          # dark scrub
    return (0.3 * k, 0.42 * k, 0.22 * k)


def cliff_fn(x, y):
    # (round 24) the headland's cliffs: warm grey and ochre rock in blotches, dark cracks, a little green in the ledges
    v = 0.5 + 0.3 * math.sin(x * 0.31 + math.sin(y * 0.27) * 2.5) + 0.2 * math.sin(y * 0.5 + x * 0.13)
    k = 0.9 + 0.2 * v + nrng.uniform(-0.05, 0.05)
    if (x * 7 + y * 3) % 23 < 1 or (x - y * 2) % 31 < 1:
        return (0.32 * k, 0.29 * k, 0.25 * k)        # a crack
    if nrng.random() < 0.06:
        return (0.36 * k, 0.45 * k, 0.26 * k)        # a tuft in a ledge
    if v > 0.62:
        return (0.74 * k, 0.62 * k, 0.45 * k)        # ochre
    return (0.62 * k, 0.6 * k, 0.55 * k)              # grey


def forest_floor(x, y):
    k = 1 + 0.08 * math.sin(x * 0.3 + math.sin(y * 0.2) * 3) + random.Random(x * 131 + y * 7).uniform(-0.14, 0.14)
    if random.Random(x * 17 + y * 31).random() < 0.08:
        return (0.42 * k, 0.33 * k, 0.2 * k)          # fallen needles
    return (0.25 * k, 0.36 * k, 0.17 * k)


def path_fn(x, y):
    k = 1 + random.Random(x * 997 + y * 7).uniform(-0.1, 0.1)
    return (0.62 * k, 0.53 * k, 0.4 * k)


def terrace_fn(x, y):
    if x % 32 < 1 or y % 32 < 1:
        return (0.62, 0.58, 0.52)
    k = 1 + random.Random(x * 7 + y * 131).uniform(-0.04, 0.04) + (0.04 if ((x // 32) + (y // 32)) % 2 else 0)
    return (0.83 * k, 0.78 * k, 0.7 * k)


def palm_image():
    """A palm frond: a rib down the middle with narrow leaflets either side (alpha cut out)."""
    W, H = 128, 32
    px = [0.0] * (W * H * 4)
    for i in range(W * H):
        px[i * 4:i * 4 + 3] = (0.24, 0.38, 0.16)
    for y in range(H):
        for x in range(W):
            t = x / (W - 1)
            half = 15.0 * (math.sin(math.pi * min(1.0, t * 1.15)) ** 0.7) if t < 0.95 else 0
            d = abs(y - 15.5)
            if d < half and ((x + d * 1.4) % 5 > 1.2 or d < 1.2):
                k = 0.85 + 0.25 * (1 - d / max(half, 1)) + nrng.uniform(-0.06, 0.06)
                i = (y * W + x) * 4
                px[i], px[i + 1], px[i + 2], px[i + 3] = 0.3 * k, 0.48 * k, 0.2 * k, 1.0
    img = bpy.data.images.new('palm_frond', W, H, alpha=True)
    img.pixels.foreach_set(px)
    img.file_format = 'PNG'
    img.pack()
    return img


M_SAND = mat('Sand', '#ffffff', 0.95, image=make_image('sand', 64, 64, sand_fn))
M_SEA = mat('Sea', '#3f8fa8', 0.12)                   # the game gives it gentle waves
M_RIVER = mat('River', '#4f8a86', 0.12)               # the same, greener and calmer
M_FOAM = mat('Foam', '#f4f6f2', 0.6)
M_HILL = mat('Hills', '#ffffff', 1.0, image=make_image('hills', 128, 128, hill_fn))
M_ROCK = mat('Rock', '#ffffff', 0.95, image=make_image('rock', 128, 128, rock_fn))
M_CLIFF = mat('Cliff', '#ffffff', 0.95, image=make_image('cliff', 128, 128, cliff_fn))
M_FLOOR = mat('ForestFloor', '#ffffff', 0.97, image=make_image('forestfloor', 128, 128, forest_floor))
M_PATH = mat('DirtPath', '#ffffff', 0.97, image=make_image('dirtpath', 64, 64, path_fn))
M_TERRACE = mat('TerracePaving', '#ffffff', 0.9, image=make_image('terrace', 128, 128, terrace_fn))


def setts_fn(x, y):
    # (round 26) granite setts for Gràcia's streets: little grey-blue blocks in staggered rows, dark joints between
    row = y // 8
    xx = (x + (row % 2) * 4) % 8
    yy = y % 8
    if xx == 0 or yy == 0:
        return (0.3, 0.3, 0.31)
    rr = random.Random(row * 977 + ((x + (row % 2) * 4) // 8) * 131)
    k = rr.uniform(0.82, 1.1)
    bl = rr.uniform(-0.02, 0.03)
    return (0.5 * k, 0.5 * k, (0.52 + bl) * k)


M_SETTS = mat('Setts', '#ffffff', 0.85, image=make_image('setts', 64, 64, setts_fn))
M_BED = mat('RiverBed', '#6b6450', 0.95)
M_PINE = mat('LeavesPine', '#ffffff', 0.8, image=foliage_image('pine', 128, [
    (300, ['#3d5a2a', '#4a6b30', '#2f4a24', '#56763a'], 4, 7, 0.22, 0)], 31), alpha=True)
M_OAK = mat('LeavesOak', '#ffffff', 0.8, image=foliage_image('holm_oak', 128, [
    (240, ['#3a5228', '#455f2e', '#2f4422', '#52693a'], 4, 6, 0.6, 0)], 32), alpha=True)
M_PALM = mat('LeavesPalm', '#ffffff', 0.8, image=palm_image(), alpha=True)
M_PALM_TRUNK = mat('PalmTrunk', '#8a7458', 0.95)
M_WOODEN = mat('BeachWood', '#a67c52', 0.85)
M_UMBRELLA_RIB = mat('UmbrellaRib', '#e8e2d2', 0.7)
M_RED = mat('PaintRed', '#c8322e', 0.6)
M_WHITE = mat('PaintWhite', '#f2efe8', 0.6)
M_GREEN = mat('PaintGreen', '#2f5a3e', 0.6)
M_GOLD = mat('Gilt', '#d4a640', 0.35, 0.8)
M_GREYSTONE = mat('GreyStone', '#b7b1a6', 0.9)

# ------------------------------------------------------------------ the ground: one grid of heights


def rock_height(X, Y):
    """The mountain: rising steeply north of its foot (the 2D game's mountain line), with bumps."""
    foot = curve('mount', X)
    up = max(0.0, foot + 0.6 - Y)
    h = 0.05 + up * 2.3 + (1.4 * math.sin(X * 0.37 + Y * 0.21) + 1.0 * math.sin(X * 0.13 - Y * 0.47)) * min(1.0, up / 3)
    if 22 <= X <= 48 and Y <= 9.6:
        h = max(h, H_T + (9.6 - Y) * 1.8 if Y < 1.6 or X < 23.4 or X > 47.6 else H_T)   # the rock round the terrace
    return h


def sand_height(X, Y):
    d = curve('coast', X) - Y                        # tiles above the waterline
    return max(-0.9, min(0.1, -0.05 + d * 0.07))


# ------------------------------------------------------------------ the north (round 22): north.py's ground
import sys as _sys
_sys.path.insert(0, BUILD)
import north as NORTH
import importlib as _il
_il.reload(NORTH)


def in_north(X, Y):
    """A tile (2D game's) north of the city whose ground north.py shapes: the funfair's hill, Gràcia, Park Güell
    (not the eastern wood's own tiles, which keep theirs)."""
    if Y < 14 and not (X >= 86 and Y >= 9):
        return True
    x, z = north_xz(X + 0.5, Y + 0.5)
    for gzn in (NORTH.GRACIA_ZONE, NORTH.GRACIA_EXT):  # (round 26: Gràcia's east blocks reach into that corner;
        if gzn[0] - 1.0 < x < gzn[2] + 1.0 and gzn[1] < z < gzn[3] + 1.0:   # round 27: and its quarter south of the Diagonal)
            return True
    return False


def north_xz(X, Y):
    return (X - OX) * T, (Y - OY) * T


def north_ground(x, z):
    h = NORTH.ground(x, z)
    # the grid's west and east edges: the hills fall away gently instead of ending in a wall
    if x < -232.0:
        h *= 1.0 - 0.7 * min(1.0, (-232.0 - x) / 28.0)
    if x > 214.0:
        h *= 1.0 - 0.12 * min(1.0, (x - 214.0) / 27.0)       # (round 27: barely falls: the wood goes on east)
    return h


EAST_RISE_AT = 6                                     # tiles past the map's east edge


# ------------------------------------------------------------------ the east end of the beach (round 25)
# Round 24's cove and wooded headland are gone (the user: "The land curves around at the east end of the beach. The
# whole thing looks bad. Just add a small rock break wall, like the actual Barcelona, going out into the ocean"). The
# beach runs on straight; a breakwater of big boulders crosses it, from the wood's edge out into the sea, and stops her
# (she can't climb it). In the wood the ground past the map's edge rises, just enough to stop her (too steep to climb)
# and no higher, so from the beach the wood seems simply to go on.
EAST_RISE_MAX = 3.0                                  # metres
BW_X = MW2 + EAST_RISE_AT + 0.5                      # (2D tiles) the breakwater's line, where the wood's rise begins
BW_Y0 = 82.4                                         # its landward end, in the wood's edge (the rise beside it)
BW_OUT = 7.0                                         # how far past the waterline it runs, tiles


def east_rise_from(y):
    """(2D tiles) where the wood's ground starts to climb past the map's east edge (1.6 m a tile, to EAST_RISE_MAX;
    main's slope rule: north.gd steer_on_slope; round 23, the user: "a slope that cannot be climbed, not an invisible
    wall")."""
    return MW2 + EAST_RISE_AT


def tile_height(X, Y):
    """The height a tile's middle should be (metres)."""
    if in_north(X, Y):
        return north_ground(*north_xz(X + 0.5, Y + 0.5))
    k = tile(X, Y)
    if k is None and X >= MW2 and 0 <= Y < 85:
        return 0.05 + min(EAST_RISE_MAX, max(0.0, X + 0.5 - east_rise_from(Y + 0.5)) * 1.6)
    if k is None and X >= MW2 and Y >= 85:          # (the beach and the sea go straight on past the map's edge)
        return tile_height(MW2 - 1, Y)
    if k is None:                                    # off the map: the land carries on (north mountains, sea south)
        if Y < 0:
            return rock_height(max(0, min(MW2 - 1, X)), Y) + max(0, -X) * 0.4
        if Y >= MH2:
            return -1.5
        if X < 0:
            if Y >= 88:
                return -1.5
            if Y > 84:
                # (round 32: the meadow slides gently under the sea — its rising ground used to run straight
                # into the water as stepped green terraces at the river's mouth)
                return max(-0.9, 0.05 - (Y - 84) * 0.35)
            # (round 32: the rise flattens out towards the shore, the way land does meeting the sea)
            return 0.05 + min(6.0, -X * 0.25) * min(1.0, max(0.0, (82.0 - Y) / 6.0))
        return 0.05 if Y < 88 else -1.5
    if k in ('ROCK', 'BOULDER'):
        return rock_height(X + 0.5, Y + 0.5)
    if k in ('TERRACE', 'RAIL', 'RIDE', 'WHEEL', 'TEMPLE'):
        return H_T
    if k == 'PATH' and STEPS[0] <= X < STEPS[1] and STEPS[2] <= Y < STEPS[3]:
        return H_T * (STEPS[3] - (Y + 0.5)) / (STEPS[3] - STEPS[2])
    if k in ('SAND', 'PALM'):
        return sand_height(X + 0.5, Y + 0.5)
    if k == 'SEA':
        # (round 23, the user: "the beach is too square where the water meets the sand… it should be smooth, matching
        # the white line of whitewash": the sand slopes on under the water from the coast's own curve, the one the foam
        # follows, so the waterline is that curve and not the tiles' edges)
        return sand_height(X + 0.5, Y + 0.5) if curve('coast', X + 0.5) - (Y + 0.5) > -6 else -1.2
    if k in ('RIVER', 'BRIDGE', 'BARRIER'):
        return -1.3
    if k == 'PATH':
        return 0.06
    return 0.05                                      # grass, forest floor, and the city's edge


def tile_kind(X, Y):
    k = tile(X, Y)
    if k is None and X >= MW2 and Y >= 85:
        return tile_kind(MW2 - 1, Y)
    if k is None:
        if Y >= MH2 or (Y >= 88 and X < 0):
            return 'SEA'
        if Y < 0:
            return 'ROCK'
        return 'FFLOOR' if X >= MW2 else 'GRASS'
    return k


GROUND_MAT = {'GRASS': M_GRASS, 'FFLOOR': M_FLOOR, 'TREE': M_FLOOR, 'PATH': M_PATH, 'SAND': M_SAND, 'PALM': M_SAND,
              'SEA': M_SAND, 'RIVER': M_BED, 'BRIDGE': M_BED, 'BARRIER': M_BED, 'ROCK': M_ROCK, 'BOULDER': M_ROCK,
              'TERRACE': M_TERRACE, 'RAIL': M_TERRACE, 'RIDE': M_TERRACE, 'WHEEL': M_TERRACE, 'TEMPLE': M_TERRACE,
              'STATION': M_PATH}
CITY_KINDS = {'ROAD', 'PAVE', 'WALK', 'PROM', 'BLDG', 'COURT', 'SPECIAL', 'DOOR', 'LAWN', 'HEDGE', 'FOUNT', 'GRAVEL'}

# the eastern wood's paths and fringe (forest.py), which the ground needs to know about
exec(open(os.path.join(BUILD, 'forest.py')).read())
forest_layout()
# (round 36: a 2D boulder tile sat on the long gravel path where it turns into the Travessera's wall gap — a rock
# on the path, raised ground and a blocked tile. Where a wood's path crosses one, the tile is forest floor.)
# (Round 36, the user: "remove the rectangle" — the 2D map's mountain edge, its row 9, lay between the hill's lawn
# and the wood east of Gràcia as two raised, blocked strips of rock: that row is grass, like the lawn above it.)
_tid = {n: i for i, n in TN.items()}
for Y in range(MH2):
    for X in range(MW2):
        if tile(X, Y) == 'BOULDER' and X >= FOREST_X0 and path_dist(X + 0.5, Y + 0.5)[0] < 0.6:
            W2['tiles'][Y][X] = _tid['FFLOOR']
        elif Y == 9 and X >= 86 and tile(X, Y) in ('ROCK', 'BOULDER') and not in_north(X, Y):
            W2['tiles'][Y][X] = _tid['GRASS']
        # (round 40, the user, on the pavement by the funicular's low station: "fix this. Make it like the rest of the
        # path") four squares of the 2D map's beach promenade lay in the town's pavement row there: panot, as the rest
        elif Y == 15 and 30 <= X <= 45 and tile(X, Y) == 'PROM':
            W2['tiles'][Y][X] = _tid['PAVE']

# vertex heights every half tile over the map (and a margin round it), each the mean of the tiles round it
TX0, TY0, TX1, TY1 = -24, -100, MW2 + 24, MH2 + 20      # (round 22: north to the hilltop behind the funfair)
STEP = 0.5
NXV, NYV = int((TX1 - TX0) / STEP) + 1, int((TY1 - TY0) / STEP) + 1
TH = {}


def th(X, Y):
    key = (X, Y)
    if key not in TH:
        TH[key] = tile_height(X, Y)
    return TH[key]


VH = []
for j in range(NYV):
    row = []
    Y = TY0 + j * STEP
    for i in range(NXV):
        X = TX0 + i * STEP
        if X == int(X) and Y == int(Y):              # a tile corner: the four tiles round it
            h = (th(int(X) - 1, int(Y) - 1) + th(int(X), int(Y) - 1) + th(int(X) - 1, int(Y)) + th(int(X), int(Y))) / 4
        elif X == int(X):                            # middle of a vertical tile edge
            h = (th(int(X) - 1, int(math.floor(Y))) + th(int(X), int(math.floor(Y)))) / 2
        elif Y == int(Y):
            h = (th(int(math.floor(X)), int(Y) - 1) + th(int(math.floor(X)), int(Y))) / 2
        else:                                        # a tile's middle
            h = th(int(math.floor(X)), int(math.floor(Y)))
        if in_north(math.floor(X - 0.01), math.floor(Y - 0.01)) and in_north(math.floor(X), math.floor(Y)):
            h = north_ground(*north_xz(X, Y))
        row.append(round(h, 3))
    VH.append(row)

# (round 40, the user: "this river just ends. It shouldn't. If necessary, it curves around the mountain. Out of sight";
# then, on the plan round40/r4/plan_river.jpg: "The river seems good… The river should just curve out around the existing
# trees") from where it met the hill's foot it turns and runs on west along the foot's flat ground, south of the wood,
# off the map's western edge behind the far hills: a bed lowered into the grid, its banks sloping up 0.55 a metre
RIVER_EXT = [(-176.5, -102.0), (-180.0, -105.5), (-188.0, -107.3), (-198.0, -107.0), (-210.0, -106.0), (-222.0, -106.5),
             (-235.0, -107.4), (-248.0, -106.5), (-262.0, -105.5)]
RIVER_EXT_W = 7.0


def _seg_d(px, pz, line):
    best = 1e9
    for (ax, az), (bx, bz) in zip(line, line[1:]):
        dx, dz = bx - ax, bz - az
        t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / (dx * dx + dz * dz)))
        best = min(best, math.hypot(px - ax - dx * t, pz - az - dz * t))
    return best


for j in range(NYV):
    for i in range(NXV):
        x_, z_ = north_xz(TX0 + i * STEP, TY0 + j * STEP)
        if not (-266.0 < x_ < -170.0 and -116.0 < z_ < -96.0):
            continue
        d_ = _seg_d(x_, z_, RIVER_EXT)
        if d_ < RIVER_EXT_W / 2 + 4.5:
            VH[j][i] = round(min(VH[j][i], -1.0 + 0.55 * max(0.0, d_ - (RIVER_EXT_W / 2 - 0.6))), 3)

# (round 41, the user, at the hill path's banks: "This is really jagged here… It's not too bad that it's steep, it just
# shouldn't be so jagged. It should be more rounded"; then "the hairpins' banks… more rounded") the hillside round the
# path, away from it, is rounded off: the banks' folds and peaks — where two legs' banks meet in a crease, drawn by the
# grid as tall sharp triangles — smoothed in three passes over the points round each, eased in from 5.5 m off the path
# (the path, its edge and the bank's foot keep their heights) to 9 m; not on the funfair, the funicular's bed, the park
_HR = NORTH.HILL_R
_SM_W = {}
_BAYS = [b_[:2] for b_ in NORTH.bench_spots()] + [w_[:2] for w_ in NORTH.WORK_SITE]
for j in range(1, NYV - 1):
    for i in range(1, NXV - 1):
        X_, Y_ = TX0 + i * STEP, TY0 + j * STEP
        x_, z_ = north_xz(X_, Y_)
        if not (_HR[0] < x_ < _HR[2] and _HR[1] < z_ < NORTH.FOOT_Z - 3.0):
            continue
        if not in_north(math.floor(X_ - 0.01), math.floor(Y_ - 0.01)):
            continue
        f_ = NORTH.FAIR
        if f_[0] - 8.0 < x_ < f_[2] + 8.0 and f_[1] - 8.0 < z_ < f_[3] + 8.0:
            continue
        if abs(x_ - NORTH.CABLE_LOW[0]) < 10.0 or NORTH.park_r(x_, z_) < 1.2:
            continue
        if any(math.hypot(x_ - b_[0], z_ - b_[1]) < 5.0 for b_ in _BAYS):
            continue                                   # (the benches' and the work site's level bays, C4)
        w_ = NORTH.smooth(5.5, 9.0, NORTH.path_near(x_, z_)[0])
        if w_ > 0.0:
            _SM_W[(i, j)] = w_
for _pass in range(3):
    _new = {}
    for (i, j), w_ in _SM_W.items():
        acc_ = 4.0 * VH[j][i] + 2.0 * (VH[j][i - 1] + VH[j][i + 1] + VH[j - 1][i] + VH[j + 1][i]) + \
            (VH[j - 1][i - 1] + VH[j - 1][i + 1] + VH[j + 1][i - 1] + VH[j + 1][i + 1])
        _new[(i, j)] = VH[j][i] + (acc_ / 16.0 - VH[j][i]) * w_
    for (i, j), h_ in _new.items():
        VH[j][i] = round(h_, 3)
print('HILL banks rounded: %d points' % len(_SM_W))

# (round 35, PATH_RULES A4/C3: the grid's 1.65 m squares could neither hold the hill path level across nor show a
# narrow green edge and a bank right beside it — the path tilted up to 0.28 m, the bank smeared over the edge; the park's
# paths tilted up to 0.7 m beside its banks) along the hill path and Park Güell's paths the ground is three times
# finer: the squares near a path's middle are laid as 3 x 3 pieces whose inner points take the ground's own height; on
# the edges such a square shares with a coarse one its points lie on the coarse edge, so nothing cracks. The game walks
# the same finer heights (scene 'terrain_fine', a patch for each place).
GF_K = 3
GF_CELLS = set()
GF_WALL_N = 0                               # (round 40: the squares the park's wall crosses, away from the paths)
_PK_FLATS = [NORTH.GUELL[k] for k in ('plaza', 'porch', 'stairs_r', 'square_r')] + list(NORTH.GUELL['side_stairs'])
for j in range(NYV - 1):
    for i in range(NXV - 1):
        X, Y = TX0 + (i + 0.5) * STEP, TY0 + (j + 0.5) * STEP
        if not in_north(int(math.floor(X)), int(math.floor(Y))):
            continue
        cx_, cz_ = north_xz(X, Y)
        if cz_ < NORTH.FOOT_Z + 4 and NORTH.HILL_R[0] < cx_ < NORTH.HILL_R[2] and NORTH.path_near(cx_, cz_)[0] < 6.0:
            GF_CELLS.add((i, j))
        elif NORTH.park_r(cx_, cz_) < 1.06 and min(NORTH._seg_near(cx_, cz_, P_)[0] for P_ in NORTH.PARK_PATHS) < 3.6 \
                and not any(r_[0] - 0.9 < cx_ < r_[2] + 0.9 and r_[1] - 0.9 < cz_ < r_[3] + 0.9 for r_ in _PK_FLATS) \
                and max(NORTH.park_r(*north_xz(X + a_ * STEP, Y + b_ * STEP)) for a_ in (-0.5, 0.5) for b_ in (-0.5, 0.5)) < 1.15:
            GF_CELLS.add((i, j))                     # (a square the wall crosses too: its pieces are cut along it)
        elif min(prs_w := [NORTH.park_r(*north_xz(X + a_ * STEP, Y + b_ * STEP)) for a_ in (-0.5, 0.5) for b_ in (-0.5, 0.5)]) < 1.0 <= max(prs_w) \
                and not any(r_[0] - 0.9 < cx_ < r_[2] + 0.9 and r_[1] - 0.9 < cz_ < r_[3] + 0.9 for r_ in _PK_FLATS):
            # (round 40, the user: "There should not be a drop into the fence where you can get stuck"; PATH_RULES G5)
            # every square the park's wall crosses, path or no path: on the coarse squares the ground sagged from the
            # park's level down to the street's across the whole square, a ditch up to 1.5 m deep inside the wall that
            # she slid into and couldn't climb out of (Casa Larrard's west corner, --trapsim); finer, the park's ground
            # stays level to within half a metre of the wall, under the wall itself
            GF_CELLS.add((i, j))
            GF_WALL_N += 1
        elif NORTH.rect_d(cx_, cz_, NORTH.aus_plane()[:4]) < 5.0 and NORTH.park_r(cx_, cz_) < 1.0:
            GF_CELLS.add((i, j))                     # (round 40, PATH_RULES F6: the Austria Gardens' walks level, crisp)
GF_V = {}                                   # (fine column, fine row) -> height, for every corner of a finer piece


def _coarse(ci, cj):
    ii, jj = min(int(math.floor(ci)), NXV - 2), min(int(math.floor(cj)), NYV - 2)
    a_, b_ = ci - ii, cj - jj
    return (VH[jj][ii] * (1 - a_) + VH[jj][ii + 1] * a_) * (1 - b_) + (VH[jj + 1][ii] * (1 - a_) + VH[jj + 1][ii + 1] * a_) * b_


for (i, j) in GF_CELLS:
    for b_ in range(GF_K + 1):
        for a_ in range(GF_K + 1):
            key = (i * GF_K + a_, j * GF_K + b_)
            if key in GF_V:
                continue
            ci, cj = key[0] / GF_K, key[1] / GF_K
            i0, j0 = int(math.floor(ci)), int(math.floor(cj))
            touch = {(i0 + di, j0 + dj) for di in ((-1, 0) if key[0] % GF_K == 0 else (0,))
                     for dj in ((-1, 0) if key[1] % GF_K == 0 else (0,))}
            if all(t in GF_CELLS for t in touch):
                GF_V[key] = round(north_ground(*north_xz(TX0 + ci * STEP, TY0 + cj * STEP)), 3)
            else:
                GF_V[key] = round(_coarse(ci, cj), 3)
print('FINE ground along the paths: %d squares (%d of them under the park wall), %d points' % (len(GF_CELLS), GF_WALL_N, len(GF_V)))


def gf_at(X, Y):
    """The finer ground's height at (X, Y) tiles, or None outside its squares."""
    ci, cj = (X - TX0) / STEP, (Y - TY0) / STEP
    if (int(math.floor(ci)), int(math.floor(cj))) not in GF_CELLS:
        return None
    fi, fj = ci * GF_K, cj * GF_K
    i, j = int(math.floor(fi)), int(math.floor(fj))
    a, b = fi - i, fj - j
    return (GF_V[(i, j)] * (1 - a) + GF_V[(i + 1, j)] * a) * (1 - b) + (GF_V[(i, j + 1)] * (1 - a) + GF_V[(i + 1, j + 1)] * a) * b

def park_tone(m, sat=0.6, val=0.97):
    """(round 34, the user: "the layout is not as green as you have made it… I just mean for you to tone down the
    saturation of the green. It doesn't need to be yellow") Park Güell's own copy of a material: its picture with
    the colour toned down towards grey (sat of it kept), the same hue; made once, by name."""
    nm_ = m.name + 'Park'
    if nm_ in MATS:
        return MATS[nm_]
    img = next((n_.image for n_ in m.node_tree.nodes if n_.type == 'TEX_IMAGE' and n_.image is not None), None) if m.node_tree else None
    alpha_ = any(l_.to_socket.name == 'Alpha' for l_ in m.node_tree.links) if m.node_tree else False
    bsdf_ = next((n_ for n_ in m.node_tree.nodes if n_.type == 'BSDF_PRINCIPLED'), None) if m.node_tree else None
    rough_ = bsdf_.inputs['Roughness'].default_value if bsdf_ else 0.85
    if img is None:
        c_ = m.diffuse_color
        l_ = 0.3 * c_[0] + 0.59 * c_[1] + 0.11 * c_[2]
        col_ = [l_ + (c_[i] - l_) * sat for i in range(3)]
        out = mat(nm_, '#%02x%02x%02x' % tuple(int(255 * min(1, max(0, v)) ** (1 / 2.2)) for v in col_), rough_)
        return out
    import numpy as _np
    w_, h_ = img.size
    px_ = _np.empty(w_ * h_ * 4, _np.float32)
    img.pixels.foreach_get(px_)
    px_ = px_.reshape(-1, 4)
    lum_ = px_[:, 0] * 0.3 + px_[:, 1] * 0.59 + px_[:, 2] * 0.11
    for i in range(3):
        px_[:, i] = _np.clip((lum_ + (px_[:, i] - lum_) * sat) * val, 0.0, 1.0)
    im2 = bpy.data.images.new(nm_, w_, h_, alpha=alpha_)
    im2.pixels.foreach_set(px_.reshape(-1))
    im2.file_format = 'PNG'
    try:
        im2.pack()
    except Exception:
        pass
    return mat(nm_, '#ffffff', rough_, image=im2, alpha=alpha_)


M_PARKLAWN = park_tone(M_GRASS, 0.62)


def north_mat(x, z):
    f = NORTH.FAIR
    if f[0] <= x <= f[2] and f[1] <= z <= f[3]:
        return M_TERRACE
    # (round 41, the user: "For the workman's area here, could you make the ground like dirt?") the workmen's earth
    # patch is no longer the ground's squares (they showed as steps: "should be more rounded at the edges"):
    # north_build.py lays it as its own rounded sheet on the grass
    pr = NORTH.park_r(x, z)
    if pr < 1.0:
        G = NORTH.GUELL
        if 102.5 < x < 109.5 and -143.5 < z < -139.5:
            return M_PATH                              # (round 27: the gateway itself, sand, no grass strip)
        # (round 35, PATH_RULES C1: sand colour only on paths and paving — a ground square takes the sand only when it
        # lies wholly under the paving, so none shows past the paving's edge as a square)
        for r in (G['plaza'], G['porch'], G['stairs_r']) + tuple(G['side_stairs']):
            if r[0] + 0.83 <= x <= r[2] - 0.83 and r[1] + 0.83 <= z <= r[3] - 0.83:
                return M_PATH                          # (round 26: sand under the stairs too, not lawn)
        # (round 35, PATH_RULES C1/C2: round 28's bare sauló on banks too steep for grass is gone — it showed as sand
        # squares on the grass; a bank wears the wood floor's half-shade look instead, park_light)
        s_g, t_g, be_g, fl_g = NORTH.gallery_where(x, z)
        if -NORTH.GALLERY['out'] + 0.83 < s_g < NORTH.GALLERY['wall'] - 0.83 and be_g < -0.83:
            return M_PATH                              # (round 34) the covered walk's floor, under its own paving
        if NORTH.park_wood(x, z):
            return M_PARKFLOOR                         # (round 33: the park's wood has a wood's floor, by its light)
        return M_PARKLAWN                              # (round 34: its open lawns, the green toned down)
    for gzn in (NORTH.GRACIA_ZONE, NORTH.GRACIA_EXT):
        if gzn[0] < x < gzn[2] and gzn[1] < z < gzn[3]:
            # (round 26) Gràcia: granite setts on its streets, the squares and the gate's forecourt paved (the
            # pavements round its blocks are north_build.py's, with kerbs)
            # (round 36, H6.2: the gate's forecourt is the road's cobbles now, its footpaths north_build.py's)
            for r in (NORTH.GRACIA_PLACA, NORTH.GRACIA_SOL):
                if r[0] <= x <= r[2] and r[1] <= z <= r[3]:
                    return M_PANOT
            # (round 36, H3/H4, replacing round 31's verge at x 124: the setts run to the bounding footpath
            # at x 128.7 — the footpath itself and Provença's far pavement are north_build.py's panot on top —
            # and east of it grass carries to the wall and the wood's one gravel path. South of Provença's
            # street the town ends in grass the same way.)
            if x > NORTH.GRACIA_FOOT_X[0]:
                return M_GRASS
            if z > -48.8 and x > 86.0:
                return M_GRASS
            return M_SETTS
    if z > -100.0:
        return M_GRASS                                 # (round 31: the last strip by the city's pavement is plain
                                                       # grass — the floor there sat at the light map's very edge
                                                       # and shaded as a pale blue band)
    return M_HILLFLOOR                                 # (round 24: the wood's floor, not bare rock; main.gd shades it by
                                                       # north_build's light map, as the eastern wood's)


M_HILLFLOOR = mat('HillFloor', '#ffffff', 0.97, image=bpy.data.images.get('midshade'))
M_PARKFLOOR = mat('ParkFloor', '#ffffff', 0.97, image=bpy.data.images.get('midshade'))


def wall_split(i, j, X, Y):
    """(round 35, the user: "there are still squares coming out of the wall next to them") a ground square the park's
    wall crosses, cut exactly along the wall's line (its nearest stretch): each side's polygon takes its own side's
    ground, so the change runs straight under the wall, not in steps. False if no single stretch crosses it."""
    cx_, cz_ = north_xz(X + STEP / 2, Y + STEP / 2)
    W_ = NORTH.PARK_WALL
    segs_ = list(zip(W_, W_[1:] + W_[:1]))

    def sd(a, b, x, z):                      # distance from the line, signed (+ the line's left)
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-9
        return ((b[0] - a[0]) * (z - a[1]) - (b[1] - a[1]) * (x - a[0])) / L

    def segd(a, b, x, z):
        dx, dz = b[0] - a[0], b[1] - a[1]
        t = max(0.0, min(1.0, ((x - a[0]) * dx + (z - a[1]) * dz) / (dx * dx + dz * dz)))
        return math.hypot(x - a[0] - dx * t, z - a[1] - dz * t)
    a, b = min(segs_, key=lambda ab: segd(ab[0], ab[1], cx_, cz_))
    corners = [(0, 0), (1, 0), (1, 1), (0, 1)]
    hts = {(0, 0): VH[j][i], (1, 0): VH[j][i + 1], (1, 1): VH[j + 1][i + 1], (0, 1): VH[j + 1][i]}
    pts_ = [(fa, fb, sd(a, b, *north_xz(X + fa * STEP, Y + fb * STEP))) for fa, fb in corners]
    if all(p_[2] > 0 for p_ in pts_) or all(p_[2] < 0 for p_ in pts_):
        return False
    sides = {1: [], -1: []}
    for k in range(4):
        p0, p1 = pts_[k], pts_[(k + 1) % 4]
        sides[1 if p0[2] >= 0 else -1].append((p0[0], p0[1]))
        if (p0[2] >= 0) != (p1[2] >= 0):
            t = p0[2] / (p0[2] - p1[2])
            q = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
            sides[1].append(q)
            sides[-1].append(q)

    def hb_(fa, fb):
        return (hts[(0, 0)] * (1 - fa) + hts[(1, 0)] * fa) * (1 - fb) + (hts[(0, 1)] * (1 - fa) + hts[(1, 1)] * fa) * fb
    for sg, poly in sides.items():
        if len(poly) < 3:
            continue
        mfa = sum(p_[0] for p_ in poly) / len(poly)
        mfb = sum(p_[1] for p_ in poly) / len(poly)
        # (its ground by a point well inside that side, 0.6 m from the line, not by the polygon's middle on the wall)
        mx_, mz_ = north_xz(X + mfa * STEP, Y + mfb * STEP)
        off = sd(a, b, mx_, mz_)
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-9
        nx_, nz_ = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
        push = (0.6 * sg - off)
        m = north_mat(mx_ + nx_ * push, mz_ + nz_ * push)
        sc = {M_CLIFF: 4.0, M_ROCK: 6.0, M_TERRACE: 3.3, M_PANOT: 2.0, M_PATH: 2.5, M_SETTS: 1.0}.get(m, 3.0)
        q = [BT(X + fa * STEP, Y + fb * STEP, hb_(fa, fb)) for fa, fb in poly]
        ground.face(q, m, normal=(0, 0, 1), uvs=[(p.x / sc, p.y / sc) for p in q], smooth=True)
    return True


def piece_split(X, Y, S, hts):
    """(round 35) wall_split for one finer piece (S tiles a side, corner heights hts[(0|1, 0|1)]): cut along the park
    wall's nearest stretch if it crosses, each side painted by a point 0.6 m inside it. False if it doesn't cross."""
    W_ = NORTH.PARK_WALL
    segs_ = list(zip(W_, W_[1:] + W_[:1]))
    cx_, cz_ = north_xz(X + S / 2, Y + S / 2)

    def sd(a, b, x, z):
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-9
        return ((b[0] - a[0]) * (z - a[1]) - (b[1] - a[1]) * (x - a[0])) / L

    def segd(a, b, x, z):
        dx, dz = b[0] - a[0], b[1] - a[1]
        t = max(0.0, min(1.0, ((x - a[0]) * dx + (z - a[1]) * dz) / (dx * dx + dz * dz)))
        return math.hypot(x - a[0] - dx * t, z - a[1] - dz * t)
    a, b = min(segs_, key=lambda ab: segd(ab[0], ab[1], cx_, cz_))
    corners = [(0, 0), (1, 0), (1, 1), (0, 1)]
    pts_ = [(fa, fb, sd(a, b, *north_xz(X + fa * S, Y + fb * S))) for fa, fb in corners]
    if all(p_[2] > 0 for p_ in pts_) or all(p_[2] < 0 for p_ in pts_):
        return False
    sides = {1: [], -1: []}
    for k in range(4):
        p0, p1 = pts_[k], pts_[(k + 1) % 4]
        sides[1 if p0[2] >= 0 else -1].append((p0[0], p0[1]))
        if (p0[2] >= 0) != (p1[2] >= 0):
            t = p0[2] / (p0[2] - p1[2])
            q = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
            sides[1].append(q)
            sides[-1].append(q)

    def hb_(fa, fb):
        return (hts[(0, 0)] * (1 - fa) + hts[(1, 0)] * fa) * (1 - fb) + (hts[(0, 1)] * (1 - fa) + hts[(1, 1)] * fa) * fb
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-9
    nx_, nz_ = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    for sg, poly in sides.items():
        if len(poly) < 3:
            continue
        mx_, mz_ = north_xz(X + sum(p_[0] for p_ in poly) / len(poly) * S, Y + sum(p_[1] for p_ in poly) / len(poly) * S)
        push = (0.6 * sg - sd(a, b, mx_, mz_))
        m = north_mat(mx_ + nx_ * push, mz_ + nz_ * push)
        sc = {M_CLIFF: 4.0, M_ROCK: 6.0, M_TERRACE: 3.3, M_PANOT: 2.0, M_PATH: 2.5, M_SETTS: 1.0}.get(m, 3.0)
        q = [BT(X + fa * S, Y + fb * S, hb_(fa, fb)) for fa, fb in poly]
        ground.face(q, m, normal=(0, 0, 1), uvs=[(p.x / sc, p.y / sc) for p in q], smooth=True)
    return True


# (round 41, the user: "for the west, I think fields would be better. Maybe what looks like some roads and some very low
# fidelity houses that look like farmhouses from the distance. Could you mock something up") the Llobregat's farm plain
# west of the ground grid: a patchwork of fields, a few dusty country roads, scattered farmhouses with terracotta roofs.
# Only on the low plain (under 45 m); the Garraf's hills further west and Collserola to the north stay wooded.
# WEST_FIELDS = False takes it all out again.
WEST_FIELDS = True
_FR = random.Random(4141)
# (then: "make them more green… it sticks out being a bit brown looking at it from the top. So a little bit more greeny.
# But still the variation") mostly greens of every shade, two pale stubble fields among them, no brown ploughland
_FCOLS = [rgb(c) for c in ('#7a9a4e', '#6c8f45', '#86a456', '#5f8a42', '#93a85c', '#7f9c50', '#6f9a52', '#9fae66',
                           '#a9a764', '#b3ad72')]
_FW = 256
_FIELD = [[None] * _FW for _ in range(_FW)]


_PLOTS = []                                     # (each field's rectangle in the picture's pixels: trees go on some edges)


def _plots(x0, y0, x1, y1, d):
    if d > 5 or (x1 - x0) * (y1 - y0) < 900 and d > 2:
        _PLOTS.append((x0, y0, x1, y1))
        col = _FR.choice(_FCOLS)
        stripes = _FR.random() < 0.35
        for y in range(y0, y1):
            for x in range(x0, x1):
                edge = x in (x0, x1 - 1) or y in (y0, y1 - 1)
                k = 1.0 + (0.06 if stripes and ((x + y) // 3) % 2 else 0.0)
                _FIELD[y][x] = tuple(v * (0.62 if edge else k) for v in col)
        return
    if (x1 - x0) >= (y1 - y0):
        c = x0 + int((x1 - x0) * _FR.uniform(0.35, 0.65))
        _plots(x0, y0, c, y1, d + 1)
        _plots(c, y0, x1, y1, d + 1)
    else:
        c = y0 + int((y1 - y0) * _FR.uniform(0.35, 0.65))
        _plots(x0, y0, x1, c, d + 1)
        _plots(x0, c, x1, y1, d + 1)


_plots(0, 0, _FW, _FW, 0)
M_FIELDS = mat('FarFields', '#ffffff', 1.0, image=make_image('farfields', _FW, _FW, lambda x, y: _FIELD[y][x]))


# (and "extend them almost to the river"): the meadow west of the river is field too, from 10 m back from the water
# (the bank stays grass, with its tufts), south of the river's bend by the hill and down to the shore
FIELD_BANK_X = -181.5 - 10.0


def west_field_ground(x, z):
    return WEST_FIELDS and x < FIELD_BANK_X and z > -100.0


# (round 41, the user: "that forest texture can continue a little bit further under the trees. But… the intermediate
# ground… continues a little bit further past the point that she can walk to, so she doesn't ever see the join. Then if
# she looks from the top, it actually looks like the trees are getting thicker") past the edges she can walk to (the
# walk box as north_build.py widens it: x −232…197, z −330 north) by OUT_MARGIN, the ground's green under the outer
# trees is the far hills' wooded look (M_HILL, at the far land's scale, so it runs on into it without a seam); inside
# the margin the wood's own floor carries on. The south is the sea; west of the river (south of z −118) the meadow stays.
OUT_MARGIN = 20.0
_W_ = scene.get('walk', {})
OUT_X0, OUT_X1 = min(_W_.get('x0', -232.0), -232.0) - OUT_MARGIN, _W_.get('x1', 197.0) + OUT_MARGIN
OUT_Z0 = min(_W_.get('z0', -330.0), -330.0) - OUT_MARGIN
GREENS_ = (M_GRASS, M_FLOOR, M_HILLFLOOR, M_PARKFLOOR, M_PARKLAWN)


def out_of_reach(x, z):
    return x > OUT_X1 or z < OUT_Z0 or (x < OUT_X0 and z < -118.0)


def ground_face(q, m, x, z, sc):
    if m in GREENS_ and west_field_ground(x, z):
        ground.face(q, M_FIELDS, normal=(0, 0, 1), uvs=[(p.x / 380.0, p.y / 380.0) for p in q], smooth=True)
        return
    # (the eastern wood's own floors, forest.py's, count as green too)
    if (m in GREENS_ or m in (GROUND_MAT.get('FOREST'), GROUND_MAT.get('FORESTMID'))) and out_of_reach(x, z):
        ground.face(q, M_HILL, normal=(0, 0, 1), uvs=[(p.x / 60.0, p.y / 60.0) for p in q], smooth=True)
    else:
        ground.face(q, m, normal=(0, 0, 1), uvs=[(p.x / sc, p.y / sc) for p in q], smooth=True)


def gf_edge_h(i, j, fa, fb, h):
    """(round 41, the user: "a faint yellow line running through it. I think it's an artifact of the edge of the
    ground") a finer square's point on its outer edge, where the square beside it is a plain one: on that one's straight
    edge between its corners — the finer heights there left a hairline crack along the grid line, the far land showing
    through it from low down"""
    if fa == 0.0 and (i - 1, j) not in GF_CELLS and 0.0 < fb < 1.0:
        return VH[j][i] * (1 - fb) + VH[j + 1][i] * fb
    if fa == 1.0 and (i + 1, j) not in GF_CELLS and 0.0 < fb < 1.0:
        return VH[j][i + 1] * (1 - fb) + VH[j + 1][i + 1] * fb
    if fb == 0.0 and (i, j - 1) not in GF_CELLS and 0.0 < fa < 1.0:
        return VH[j][i] * (1 - fa) + VH[j][i + 1] * fa
    if fb == 1.0 and (i, j + 1) not in GF_CELLS and 0.0 < fa < 1.0:
        return VH[j + 1][i] * (1 - fa) + VH[j + 1][i + 1] * fa
    return h


ground = MB(uv=True)
for j in range(NYV - 1):
    for i in range(NXV - 1):
        X, Y = TX0 + i * STEP, TY0 + j * STEP
        k = tile_kind(int(math.floor(X)), int(math.floor(Y)))
        if in_north(int(math.floor(X)), int(math.floor(Y))):
            # (round 34, the user: "the ground has squares coming out from under the outside wall": each square takes one
            # material, so those the park's wall crosses showed the park's grass or sand on the street side. Those are
            # laid in 4 x 4 pieces now, each by its own middle, so the change falls under the wall and its footing.)
            prs_ = [NORTH.park_r(*north_xz(X + a_ * STEP, Y + b_ * STEP)) for a_ in (0, 1) for b_ in (0, 1)]
            if (i, j) in GF_CELLS:
                # (round 35) along the paths: 3 x 3 pieces on the finer ground, each painted by its own middle (cut
                # along the park wall where it crosses one)
                bi_, bj_ = i * GF_K, j * GF_K
                fs_ = STEP / GF_K
                for sb_ in range(GF_K):
                    for sa_ in range(GF_K):
                        x0_, y0_ = X + sa_ * fs_, Y + sb_ * fs_
                        hts_ = {(u, v): gf_edge_h(i, j, (sa_ + u) / GF_K, (sb_ + v) / GF_K, GF_V[(bi_ + sa_ + u, bj_ + sb_ + v)])
                                for u in (0, 1) for v in (0, 1)}
                        if min(prs_) < 1.0 <= max(prs_) and piece_split(x0_, y0_, fs_, hts_):
                            continue
                        q = [BT(x0_, y0_, hts_[(0, 0)]), BT(x0_ + fs_, y0_, hts_[(1, 0)]),
                             BT(x0_ + fs_, y0_ + fs_, hts_[(1, 1)]), BT(x0_, y0_ + fs_, hts_[(0, 1)])]
                        m = north_mat(*north_xz(x0_ + fs_ / 2, y0_ + fs_ / 2))
                        sc = {M_CLIFF: 4.0, M_ROCK: 6.0, M_TERRACE: 3.3, M_PANOT: 2.0, M_PATH: 2.5, M_SETTS: 1.0}.get(m, 3.0)
                        ground.face(q, m, normal=(0, 0, 1), uvs=[(p.x / sc, p.y / sc) for p in q], smooth=True)
                continue
            if min(prs_) < 1.0 <= max(prs_) and wall_split(i, j, X, Y):
                continue
            if min(prs_) < 1.0 <= max(prs_):
                for sa_ in range(4):
                    for sb_ in range(4):
                        def hb_(fa, fb):
                            return (VH[j][i] * (1 - fa) + VH[j][i + 1] * fa) * (1 - fb) + (VH[j + 1][i] * (1 - fa) + VH[j + 1][i + 1] * fa) * fb
                        fa0, fa1, fb0, fb1 = sa_ / 4, (sa_ + 1) / 4, sb_ / 4, (sb_ + 1) / 4
                        q = [BT(X + fa0 * STEP, Y + fb0 * STEP, hb_(fa0, fb0)), BT(X + fa1 * STEP, Y + fb0 * STEP, hb_(fa1, fb0)),
                             BT(X + fa1 * STEP, Y + fb1 * STEP, hb_(fa1, fb1)), BT(X + fa0 * STEP, Y + fb1 * STEP, hb_(fa0, fb1))]
                        m = north_mat(*north_xz(X + (fa0 + fa1) / 2 * STEP, Y + (fb0 + fb1) / 2 * STEP))
                        sc = {M_CLIFF: 4.0, M_ROCK: 6.0, M_TERRACE: 3.3, M_PANOT: 2.0, M_PATH: 2.5, M_SETTS: 1.0}.get(m, 3.0)
                        ground.face(q, m, normal=(0, 0, 1), uvs=[(p.x / sc, p.y / sc) for p in q], smooth=True)
                continue
            q = [BT(X, Y, VH[j][i]), BT(X + STEP, Y, VH[j][i + 1]), BT(X + STEP, Y + STEP, VH[j + 1][i + 1]), BT(X, Y + STEP, VH[j + 1][i])]
            m = north_mat(*north_xz(X + STEP / 2, Y + STEP / 2))
            # (round 25: no bare "cliff" on the hill's steep banks any more (it showed as a blue-grey speckled wall):
            # the wood's floor runs over them, shaded by the light map, with shrubs and ferns on them)
            sc = {M_CLIFF: 4.0, M_ROCK: 6.0, M_TERRACE: 3.3, M_PANOT: 2.0, M_PATH: 2.5, M_SETTS: 1.0}.get(m, 3.0)
            ground_face(q, m, *north_xz(X + STEP / 2, Y + STEP / 2), sc)
            continue
        if k in CITY_KINDS or (k == 'ROAD'):
            continue
        if X >= FOREST_X0:
            k = forest_ground(X, Y, k)
        if k == 'GRASS' and meadow_shore(int(math.floor(X)), int(math.floor(Y))):
            k = 'FOREST'                            # (round 37: the meadow's lawn runs into the sand as the wood's floor does)
        q = [BT(X, Y, VH[j][i]), BT(X + STEP, Y, VH[j][i + 1]), BT(X + STEP, Y + STEP, VH[j + 1][i + 1]), BT(X, Y + STEP, VH[j + 1][i])]
        m = GROUND_MAT.get(k, M_GRASS)
        sc = {M_SAND: 2.5, M_ROCK: 6.0, M_CLIFF: 4.0, M_TERRACE: 3.3, M_FLOOR: 4.0, M_PATH: 2.5}.get(m, 3.0)
        ground_face(q, m, *north_xz(X + STEP / 2, Y + STEP / 2), sc)
# (round 41, the user, of the hill path's banks: "This is really jagged… It doesn't look like an actual forest. It's not
# too bad that it's steep, it just shouldn't be so jagged. It should be more rounded") every square was laid with corners
# of its own, so "smooth" shading had nothing to share and each triangle showed flat: the ground's coinciding corners
# joined, so the light rolls over the slopes (each corner keeps its own UVs)
bmesh.ops.remove_doubles(ground.bm, verts=ground.bm.verts[:], dist=0.002)
city_objs.append(ground.finish('Ground'))


scene['terrain'] = {'x0': round((TX0 - OX) * T, 3), 'z0': round((TY0 - OY) * T, 3), 'step': round(STEP * T, 4),
                    'nx': NXV, 'nz': NYV, 'h': VH}
# (the finer ground for the game: a patch round each place — the hill path, the park — its points outside the finer
# squares on the coarse ground, so the patch is the ground everywhere inside it)
scene['terrain_fine'] = []
for _cells in ([c for c in GF_CELLS if north_xz(TX0 + c[0] * STEP, 0)[0] < 0.0],
               [c for c in GF_CELLS if north_xz(TX0 + c[0] * STEP, 0)[0] >= 0.0]):
    if not _cells:
        continue
    _i0, _j0 = min(c[0] for c in _cells) * GF_K, min(c[1] for c in _cells) * GF_K
    _i1, _j1 = (max(c[0] for c in _cells) + 1) * GF_K, (max(c[1] for c in _cells) + 1) * GF_K
    _h = [[GF_V.get((fi, fj), round(_coarse(fi / GF_K, fj / GF_K), 3)) for fi in range(_i0, _i1 + 1)] for fj in range(_j0, _j1 + 1)]
    scene['terrain_fine'].append({'x0': round((TX0 + _i0 / GF_K * STEP - OX) * T, 3), 'z0': round((TY0 + _j0 / GF_K * STEP - OY) * T, 3),
                                  'step': round(STEP / GF_K * T, 4), 'nx': _i1 - _i0 + 1, 'nz': _j1 - _j0 + 1, 'h': _h})
scene['city_rect'] = [round((W2['CITY'][0] - 1 - OX) * T, 3), round((W2['CITY'][1] - 1 - OY) * T, 3),
                      round((W2['CITY'][2] + 1 - OX) * T, 3), round((W2['CITY'][3] + 1 - OY) * T, 3)]

# water: the sea, and the river (with a line of foam along the shore)
water = MB(uv=True)
water.face([BT(-520, 80, -0.05), BT(640, 80, -0.05), BT(640, 620, -0.05), BT(-520, 620, -0.05)], M_SEA, normal=(0, 0, 1),
           uvs=[(-50, -20), (80, -20), (80, -100), (-50, -100)])
city_objs.append(water.finish('Sea'))

# (round 26, the user: from the hill "I see the river, then a plane, then an ocean. The distant land should not feel
# disjointed") the land goes on past the ground grid: a far, soft skirt of country all round it (the Llobregat's plain
# and the Garraf hills to the west, the Collserola ridge going on northwards, the Maresme's hills to the east), smooth
# and untextured, rising towards the horizon under the haze; it meets the grid's own edge at the grid's own height.
far = MB(uv=True)


def farland_fn(x, y):
    # (round 29: the sin's straight rows read as striped fields on the far faces seen from the park's east
    # gates; the phase is bent hard so the shading falls in soft irregular patches instead of rows)
    r_ = random.Random(x // 4 * 977 + y // 4 * 131)
    k_ = 1.0 + 0.05 * math.sin(x * 0.2945 + y * 0.3927 + math.sin(x * 0.0982 - y * 0.1963) * 3.0) + r_.uniform(-0.04, 0.04)
    return tuple(v * k_ for v in rgb('#6e8352'))


def farhill_fn(x, y):
    r_ = random.Random(x // 4 * 313 + y // 4 * 71)
    k_ = 1.0 + 0.06 * math.sin(x * 0.3927 - y * 0.2945 + math.sin(x * 0.1963 + y * 0.0982) * 3.0) + r_.uniform(-0.05, 0.05)
    return tuple(v * k_ for v in rgb('#55703f'))


M_FARLAND = mat('FarLand', '#ffffff', 1.0, image=make_image('farland', 64, 64, farland_fn))
M_FARHILL = mat('FarHill', '#ffffff', 1.0, image=make_image('farhill', 64, 64, farhill_fn))
GX0, GZ0 = (TX0 - OX) * T, (TY0 - OY) * T
GX1, GZ1 = GX0 + (NXV - 1) * STEP * T, GZ0 + (NYV - 1) * STEP * T


def grid_edge_h(x, z):
    """The grid's height at the point of its edge nearest (x, z)."""
    i = int(round((min(max(x, GX0), GX1) - GX0) / (STEP * T)))
    j = int(round((min(max(z, GZ0), GZ1) - GZ0) / (STEP * T)))
    return VH[min(NYV - 1, j)][min(NXV - 1, i)]


def far_h(x, z):
    n1 = math.sin(x * 0.0071 + 1.3) * math.cos(z * 0.0063 - 0.4) + 0.5 * math.sin(x * 0.019 - z * 0.011)
    h = 4.0 + 6.0 * (n1 + 1.0)                                                         # the plain, gently rolling
    north = max(0.0, -478.0 - z)
    h += min(140.0, north * 0.22) + 45.0 * (0.5 + 0.5 * math.sin(x * 0.0052 + 0.7)) * min(1.0, north / 250.0)   # Collserola going on
    west = max(0.0, -600.0 - x)
    h += min(220.0, west * 0.32) * (0.6 + 0.4 * math.sin(z * 0.0083))                   # the Garraf, far west
    east = max(0.0, x - 560.0)
    h += min(130.0, east * 0.2) * (0.6 + 0.4 * math.sin(z * 0.0091 + 2.0))               # the Maresme's hills, east
    # down to the coast, by z 115 under the sea; (round 41, the user, of the Garraf seen from the beach: "FIX" — a sheer
    # pointed edge stood over the sea: the far land stopped at z 100, still 60 m up) the higher the ground, the further
    # back its fall to the shore begins, so a hill comes down to the water as a slope
    zc = 60.0 - min(160.0, 0.7 * max(0.0, h - 10.0))
    if z > zc:
        f = min(1.0, (z - zc) / (115.0 - zc))
        h = h * (1.0 - f) - 2.0 * f
    return h


FAR_R, FAR_C = 1700.0, 50.0
fx0, fz0 = -FAR_R, -FAR_R
nfx, nfz = int(2 * FAR_R / FAR_C) + 1, int((150.0 + FAR_R) / FAR_C) + 1      # (round 41: on past the shore, z 150)
FH_ = {}
for j in range(nfz):
    for i in range(nfx):
        x, z = fx0 + i * FAR_C, fz0 + j * FAR_C
        inside = GX0 + 1.0 < x < GX1 - 1.0 and GZ0 + 1.0 < z < GZ1 - 1.0
        d_edge = max(GX0 - x, x - GX1, GZ0 - z, z - GZ1)                                   # (how far outside the grid)
        if d_edge < 0:
            h = grid_edge_h(x, z) if inside else grid_edge_h(x, z)
        else:
            k = min(1.0, d_edge / 140.0)
            h = grid_edge_h(x, z) * (1 - k) + far_h(x, z) * k
        FH_[(i, j)] = h
def far_corner_h(i, j, x, z):
    """(round 38) the far land's height at (x, z) in its square (i, j): on the grid's edge the grid's own height (they
    meet without a step), elsewhere as the square's corners."""
    if GX0 <= x <= GX1 and GZ0 <= z <= GZ1:
        return grid_edge_h(x, z)
    a, b = (x - fx0) / FAR_C - i, (z - fz0) / FAR_C - j
    return (FH_[(i, j)] * (1 - a) + FH_[(i + 1, j)] * a) * (1 - b) + (FH_[(i, j + 1)] * (1 - a) + FH_[(i + 1, j + 1)] * a) * b


def west_plain(x, z, h):
    return WEST_FIELDS and x < GX0 - 0.5 and h < 45.0 and z < 60.0


# (round 41, the user: "The second mountain along the ocean, behind it, there's a valley, and then it goes up to
# another big mountain. Could that valley have the road go through it with a few of the farm fields continuing?") the
# valley behind the Garraf's coastal ridge (far_h's low line, z about −190), west of the round hill: fields along its
# floor, laid square to the road there (their picture shifted so a hedge runs along z −190)
VALLEY_Z = -190.0


def valley_field(x, z, h):
    # (then: "the fields disappear to a point as the road goes over the valley. The valley and the landscaping was
    # correct before. It's meant to be an illusion") only a wedge of fields in the valley's mouth, narrowing to a point
    # 300 m in; past it the valley is wooded as before and the road runs on through the wood into the haze
    if not WEST_FIELDS or x > -945.0 or x < -1245.0 or h > 90.0:
        return False
    return abs(z - VALLEY_Z) < 95.0 * (x + 1245.0) / 300.0


# (round 38, the user: "The intermediate texture for the forest floor ends as a straight line on the hills": the far
# land's 50 m squares that straddle the grid's edge were laid whole over the grid's own ground — a pale strip from
# x 200 to the edge at 240.9 over the eastern wood, flush with it at x 200. Such a square is cut at the grid's edge now.)
for j in range(nfz - 1):
    for i in range(nfx - 1):
        x, z = fx0 + i * FAR_C, fz0 + j * FAR_C
        xs = [x] + [e for e in (GX0, GX1) if x < e < x + FAR_C] + [x + FAR_C]
        zs = [z] + [e for e in (GZ0, GZ1) if z < e < z + FAR_C] + [z + FAR_C]
        for xa, xb in zip(xs, xs[1:]):
            for za, zb in zip(zs, zs[1:]):
                if GX0 - 0.5 <= xa and xb <= GX1 + 0.5 and GZ0 - 0.5 <= za and zb <= GZ1 + 0.5:
                    continue                                                            # (under the grid itself)
                q = [Vector((xa, -za, far_corner_h(i, j, xa, za))), Vector((xb, -za, far_corner_h(i, j, xb, za))),
                     Vector((xb, -zb, far_corner_h(i, j, xb, zb))), Vector((xa, -zb, far_corner_h(i, j, xa, zb)))]
                hm = sum(p.z for p in q) / 4
                # (round 41, the user: the pale field glimpsed past the eastern wood — "replace that with the dark
                # green… Then it looks like the forest extends… the dark green is just whatever is currently surrounding
                # the field": east of the ground grid the far land is wooded like the hills round it, M_HILL; the far
                # hills' own plain green, tried first, still read as a field)
                # (and then, the user: "continue that texture further out… just in case there's a chance she sees it":
                # all of the far land, every side)
                if valley_field((xa + xb) / 2, (za + zb) / 2, hm):
                    far.face(q, M_FIELDS, normal=(0, 0, 1), smooth=True, uvs=[(p.x / 380.0, (p.y + VALLEY_Z) / 380.0) for p in q])
                elif west_plain((xa + xb) / 2, (za + zb) / 2, hm):
                    far.face(q, M_FIELDS, normal=(0, 0, 1), smooth=True, uvs=[(p.x / 380.0, p.y / 380.0) for p in q])
                else:
                    far.face(q, M_HILL, normal=(0, 0, 1), smooth=True, uvs=[(p.x / 60.0, p.y / 60.0) for p in q])
city_objs.append(far.finish('FarLand'))


def far_height(x, z):
    i, j = int((x - fx0) // FAR_C), int((z - fz0) // FAR_C)
    i, j = max(0, min(nfx - 2, i)), max(0, min(nfz - 2, j))
    return far_corner_h(i, j, x, z)


if WEST_FIELDS:
    # the roads: a few long dusty ones across the plain, and the farmhouses along them, side on to the road
    farms = MB(uv=True)
    M_FROAD = mat('FarRoad', '#b9ad94', 0.95)
    M_FWALLS = [mat('FarmWall%d' % i, c, 0.9) for i, c in enumerate(('#e8dcc2', '#efe6d2', '#e2cfae'))]
    M_FROOFS = [mat('FarmRoof%d' % i, c, 0.85) for i, c in enumerate(('#b5573a', '#a84e34', '#bf6744'))]
    M_FDOOR = mat('FarmDoor', '#6b4a33', 0.8)
    M_FWIN = mat('FarmWindow', '#3a3530', 0.6)
    M_FBARN = mat('FarmBarn', '#c9b48e', 0.9)
    # (then the user: "That road will have to keep continuing off into the distance through the fields. And it must
    # look like the fields are naturally around it… the road should eventually disappear out of sight") the road from
    # the bridge (north_build.py) runs on due west along z 0, and the side roads north and south along x −380, −760,
    # −1140: the fields' picture repeats every 380 m with a hedge round its edge, so these lines are hedge lines and
    # the fields lie square along the roads. The main road carries on over the far hills into the haze.
    # (then: "continue the bitumen road into the fields. Currently it ends. It should continue past the mountain…
    # the valley… the road go through it") the main road is tarmac all the way, as from the bridge: west along z 0 past
    # the round hill on its seaward side, then bending inland behind the coastal ridge and on up the valley into the haze
    ROADS_W = [NORTH.catmull([(-262.0, 0.0), (-420.0, 0.0), (-560.0, 0.0), (-700.0, -4.0), (-840.0, -30.0), (-960.0, -100.0),
                          (-1060.0, -172.0), (-1200.0, VALLEY_Z), (-1450.0, VALLEY_Z), (-1700.0, VALLEY_Z)], 4),
               [(-380.0, 55.0), (-380.0, -330.0)],
               [(-760.0, 55.0), (-760.0, -330.0)],
               [(-1140.0, 55.0), (-1140.0, -330.0)]]
    MAIN_ROAD_W = ROADS_W[0]
    nhouse = 0
    for rd in ROADS_W:
        for a, b in zip(rd, rd[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            ux, uz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            nx_, nz_ = -uz, ux
            n_ = max(1, int(L / 20.0))
            hw_ = 3.5 if rd is MAIN_ROAD_W else 3.0
            for k in range(n_):
                p0 = (a[0] + ux * L * k / n_, a[1] + uz * L * k / n_)
                p1 = (a[0] + ux * L * (k + 1) / n_, a[1] + uz * L * (k + 1) / n_)
                h0, h1 = far_height(*p0), far_height(*p1)
                if rd is not MAIN_ROAD_W and not (west_plain(p0[0], p0[1], h0) and west_plain(p1[0], p1[1], h1)):
                    continue
                q = [Vector((p0[0] + nx_ * hw_, -(p0[1] + nz_ * hw_), h0 + 0.5)), Vector((p1[0] + nx_ * hw_, -(p1[1] + nz_ * hw_), h1 + 0.5)),
                     Vector((p1[0] - nx_ * hw_, -(p1[1] - nz_ * hw_), h1 + 0.5)), Vector((p0[0] - nx_ * hw_, -(p0[1] - nz_ * hw_), h0 + 0.5))]
                if rd is MAIN_ROAD_W:
                    farms.face(q, M_ROAD, normal=(0, 0, 1), uvscale=4.0)
                else:
                    farms.face(q, M_FROAD, normal=(0, 0, 1))
            # farmhouses: every 50-130 m along the road, 14-30 m off it, either side
            t_ = _FR.uniform(20.0, 70.0)
            while t_ < L:
                sd_ = _FR.choice((-1, 1)) * _FR.uniform(14.0, 30.0)
                hx, hz = a[0] + ux * t_ + nx_ * sd_, a[1] + uz * t_ + nz_ * sd_
                # (round 41, the user: "one of the houses is on the mountain. Could you move it over so it's more in the
                # middle of the field somewhere? But at the edge?") a house whose ground falls more than 6 m across it (up a hillside,
                # not the plain's gentle roll)
                # moves along its road (and to its other side) to the nearest level field's edge
                def fh_slope_(x_, z_):
                    hs_ = [far_height(x_ + ux * du_ + nx_ * dn_, z_ + uz * du_ + nz_ * dn_) for du_ in (-8.0, 8.0) for dn_ in (-6.0, 6.0)]
                    return max(hs_) - min(hs_)
                sl0_ = fh_slope_(hx, hz)
                if sl0_ > 6.0:
                    for dt_ in (12.0, -12.0, 24.0, -24.0, 36.0, -36.0, 50.0, -50.0, 70.0, -70.0, 90.0, -90.0):
                        for s2_ in (sd_, -sd_):
                            qx_, qz_ = a[0] + ux * (t_ + dt_) + nx_ * s2_, a[1] + uz * (t_ + dt_) + nz_ * s2_
                            if fh_slope_(qx_, qz_) <= 3.0 and (west_plain(qx_, qz_, far_height(qx_, qz_)) or valley_field(qx_, qz_, far_height(qx_, qz_))):
                                print('FARMHOUSE moved off a slope (%.1f m): %.1f, %.1f -> %.1f, %.1f' % (sl0_, hx, hz, qx_, qz_))
                                hx, hz, sd_ = qx_, qz_, s2_
                                break
                        else:
                            continue
                        break
                    else:
                        print('FARMHOUSE on a slope (%.1f m) left out: %.1f, %.1f' % (sl0_, hx, hz))
                        hx = GX0                                         # (fails the test below: no house)
                hh = far_height(hx, hz)
                if (west_plain(hx, hz, hh) or valley_field(hx, hz, hh)) and hx < GX0 - 15:
                    w_, d_, tall_ = _FR.uniform(4.0, 7.0), _FR.uniform(3.0, 4.5), _FR.uniform(2.6, 3.6)
                    c_ = Vector((hx, -hz, hh - 1.0 + tall_))
                    farms.box(c_, (ux, -uz), (nx_, -nz_), w_, d_, tall_, _FR.choice(M_FWALLS))
                    # the roof: a low gable along the house, overhanging a little
                    rf_ = _FR.choice(M_FROOFS)
                    U_, N_ = Vector((ux, -uz, 0)) * (w_ + 0.5), Vector((nx_, -nz_, 0)) * (d_ + 0.5)
                    top_ = Vector((hx, -hz, hh - 1.0 + 2 * tall_))
                    ridge_ = Vector((0, 0, d_ * 0.55))
                    e1, e2, e3, e4 = top_ - U_ - N_, top_ + U_ - N_, top_ + U_ + N_, top_ - U_ + N_
                    r1, r2 = top_ - U_ + ridge_, top_ + U_ + ridge_
                    farms.face([e1, e2, r2, r1], rf_)
                    farms.face([e3, e4, r1, r2], rf_)
                    farms.face([e2, e3, r2], rf_)
                    farms.face([e4, e1, r1], rf_)
                    # (round 41, the user: "make the houses ever so slightly more detailed") a door on the road side, two
                    # dark windows each long side, a chimney, and now and then a lower barn along one end
                    U1, N1 = Vector((ux, -uz, 0)), Vector((nx_, -nz_, 0))
                    road_side_ = -1.0 if sd_ > 0 else 1.0                   # (the face towards the road)
                    farms.box(c_ + N1 * (d_ + 0.02) * road_side_ + Vector((0, 0, -tall_ + 1.1)), (ux, -uz), (nx_, -nz_), 0.6, 0.03, 1.1, M_FDOOR)
                    for side_ in (-1, 1):
                        for wf_ in (-0.55, 0.55):
                            farms.box(c_ + N1 * (d_ + 0.02) * side_ + U1 * (w_ * wf_) + Vector((0, 0, tall_ * 0.3)), (ux, -uz), (nx_, -nz_),
                                      0.45, 0.03, 0.5, M_FWIN)
                    ch_ = top_ + U_ * 0.55 + Vector((0, 0, d_ * 0.35))
                    farms.box(ch_, (ux, -uz), (nx_, -nz_), 0.35, 0.35, 0.8, _FR.choice(M_FWALLS))
                    if _FR.random() < 0.45:
                        bw_, bt_ = _FR.uniform(2.5, 4.0), tall_ * 0.75
                        bc_ = Vector((hx, -hz, hh - 1.0 + bt_)) + U1 * (w_ + bw_)
                        farms.box(bc_, (ux, -uz), (nx_, -nz_), bw_, d_ * 0.85, bt_, M_FBARN)
                        farms.box(bc_ + Vector((0, 0, bt_ + 0.08)), (ux, -uz), (nx_, -nz_), bw_ + 0.2, d_ * 0.85 + 0.25, 0.08, rf_)
                    nhouse += 1
                    if nhouse <= 3:
                        print('FARMHOUSE at %.1f, %.1f' % (hx, hz))
                t_ += _FR.uniform(50.0, 130.0)
    city_objs.append(farms.finish('FarFarms'))
    print('WEST fields: %d farmhouses' % nhouse)
scene['sea_z'] = round((curve('coast', 50) - OY) * T, 3)
river = MB(uv=True)
for Y in range(11, 89):                             # (round 22: from its spring at the foot of the hill)
    xc = curve('river', max(0, min(MH2 - 1, Y)))
    q = [BT(-6, Y, -0.35), BT(xc + 1.4, Y, -0.35), BT(xc + 1.4, Y + 1, -0.35), BT(-6, Y + 1, -0.35)]
    river.face(q, M_RIVER, normal=(0, 0, 1), uvs=[(p.x / 4, p.y / 4) for p in q])
# (round 40) the water on along RIVER_EXT, a ribbon a little wider than its bed, tucked under the banks; walled to her
for (ax_, az_), (bx_, bz_) in zip(RIVER_EXT, RIVER_EXT[1:]):
    L_ = math.hypot(bx_ - ax_, bz_ - az_)
    nx_, nz_ = -(bz_ - az_) / L_, (bx_ - ax_) / L_
    hw_ = RIVER_EXT_W / 2 + 1.0
    q = [Vector((ax_ + nx_ * hw_, -(az_ + nz_ * hw_), -0.35)), Vector((bx_ + nx_ * hw_, -(bz_ + nz_ * hw_), -0.35)),
         Vector((bx_ - nx_ * hw_, -(bz_ - nz_ * hw_), -0.35)), Vector((ax_ - nx_ * hw_, -(az_ - nz_ * hw_), -0.35))]
    river.face(q, M_RIVER, normal=(0, 0, 1), uvs=[(p.x / 4, p.y / 4) for p in q])
    ww_ = RIVER_EXT_W / 2 - 0.4
    scene.setdefault('solids', []).append([[round(ax_ + nx_ * ww_, 2), round(az_ + nz_ * ww_, 2)], [round(bx_ + nx_ * ww_, 2), round(bz_ + nz_ * ww_, 2)],
                                           [round(bx_ - nx_ * ww_, 2), round(bz_ - nz_ * ww_, 2)], [round(ax_ - nx_ * ww_, 2), round(az_ - nz_ * ww_, 2)]])
city_objs.append(river.finish('River'))
foam = MB(uv=True)
# (round 36, the user: a white line ran out over the river's mouth — the foam began 11 tiles west of the sand, on
# open water. It begins where the sand does now, at the river's east bank)
FOAM_X0 = curve('river', MH2 - 1) + 1.4
for X in range(int(FOAM_X0), TX1 + 90):             # (round 25: straight on past the map's edge, under the breakwater)
    xa = max(float(X), FOAM_X0)
    y0, y1 = curve('coast', xa) - 0.15, curve('coast', X + 1) - 0.15
    q = [BT(xa, y0 - 0.25, -0.03), BT(X + 1, y1 - 0.25, -0.03), BT(X + 1, y1 + 0.2, -0.03), BT(xa, y0 + 0.2, -0.03)]
    foam.face(q, M_FOAM, normal=(0, 0, 1), uvs=[(xa / 4, 0), ((X + 1) / 4, 0), ((X + 1) / 4, 1), (xa / 4, 1)])
city_objs.append(foam.finish('Foam'))

# the far hills, faded by the haze
def land_h(xm, zm):
    """(round 37) The far land's height (metres, FarLand's own grid FH_) under the point (xm, zm) metres."""
    fi, fj = (xm - fx0) / FAR_C, (zm - fz0) / FAR_C
    i, j = max(0, min(nfx - 2, int(fi))), max(0, min(nfz - 2, int(fj)))
    a, b = min(1.0, max(0.0, fi - i)), min(1.0, max(0.0, fj - j))
    return (FH_[(i, j)] * (1 - a) + FH_[(i + 1, j)] * a) * (1 - b) + (FH_[(i, j + 1)] * (1 - a) + FH_[(i + 1, j + 1)] * a) * b


def hill_mesh(name, x0, x1, y0, y1, nx, ny, height, seat=False):
    """A grid of ground between tile corners (x0, y0) and (x1, y1), lifted by height(u, v) metres (u, v in 0..1).
    seat: (round 37, the user: "hills appear to float") its rim plunges 6 m under the land below it (or under its own
    edge, if that is lower), easing in over the outer eighth, so the hill grows out of the ground instead of hanging its
    ragged skirt over it."""
    mb = MB(uv=True)

    def z_(i, j):
        u, v = i / nx, j / ny
        h = height(u, v)
        if not seat:
            return h
        xt, yt = x0 + (x1 - x0) * u, y0 + (y1 - y0) * v
        base = min(h, land_h((xt - OX) * T, (yt - OY) * T) - 1.0) - 6.0     # (the rim plunges well under, always buried)
        f = min(1.0, 8.0 * min(u, 1 - u, v, 1 - v))
        f = f * f * (3 - 2 * f)
        return base + (h - base) * f
    P = [[B(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, z_(i, j)) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            q = [P[i][j], P[i + 1][j], P[i + 1][j + 1], P[i][j + 1]]
            mb.face(q, M_HILL, normal=(0, 0, 1), uvs=[(p.x / 60, p.y / 60) for p in q], smooth=True)
    city_objs.append(mb.finish(name))


def ridge(u, v):
    crest = 95 + 40 * math.sin(u * 9.0) + 25 * math.sin(u * 23.0 + 1.3) + 12 * math.sin(u * 51.0)
    return max(0.0, crest * math.sin(math.pi * v) ** 1.3) + 25 - 0.5


def west_hill(u, v):
    d = math.hypot(u - 0.5, (v - 0.5) * 1.3)
    return max(0.0, 70 * math.cos(min(1.0, d * 2.0) * math.pi / 2) ** 1.5 + 6 * math.sin(u * 20) * math.sin(v * 17)) + 4


hill_mesh('HillsNorth', -320, 360, -260, -132, 64, 16, ridge, seat=True)      # (round 22: further back, behind the new hilltop)
hill_mesh('HillsWest', -230, -110, -50, 40, 20, 18, west_hill, seat=True)


# (round 24, lowered in round 25) east of the ground's edge the wooded land goes on, low (no higher than the wood's
# rise, then barely climbing), so nothing shows over the trees from the beach; and the beach goes on, straight
HE_X0, HE_X1, HE_Y0, HE_Y1 = TX1 - OX - 0.5, TX1 - OX + 90, -134.0, 85 - OY


def east_hills(u, v):
    Y2 = HE_Y0 + (HE_Y1 - HE_Y0) * v + OY                      # (2D tiles)
    edge = tile_height(TX1 - 1, int(min(max(Y2, TY0), TY1 - 1)))
    k = min(1.0, u / 0.25)
    k = k * k * (3 - 2 * k)
    high = EAST_RISE_MAX + 7 * u ** 1.3 + 1.5 * math.sin(u * 17) * math.sin(v * 13)
    if Y2 < 0:                                                   # (the north: the hills behind the funfair carry on)
        high = max(high, edge)
    return edge * (1 - k) + high * k


hill_mesh('HillsEast', HE_X0, HE_X1, HE_Y0, HE_Y1, 36, 48, east_hills)
beach_e = MB(uv=True)
for Y_ in range(84, 106):
    for X_ in range(TX1 - 1, TX1 + 90, 2):
        q = [BT(X_, Y_, tile_height(MW2 - 1, Y_)), BT(X_ + 2, Y_, tile_height(MW2 - 1, Y_)),
             BT(X_ + 2, Y_ + 1, tile_height(MW2 - 1, Y_ + 1)), BT(X_, Y_ + 1, tile_height(MW2 - 1, Y_ + 1))]
        beach_e.face(q, M_SAND if Y_ > 85 else M_HILL, normal=(0, 0, 1), uvs=[(p.x / 2.5, p.y / 2.5) for p in q], smooth=True)
city_objs.append(beach_e.finish('BeachEast'))

# (round 25) the breakwater: big rounded boulders, two rows and a few on top, from the wood's edge across the sand and
# out into the sea, lower towards its end (like the real ones off the Barcelona beaches); she can't climb it
def bw_stone_fn(x, y):
    n = 0.5 + 0.25 * math.sin(x * 0.41 + math.sin(y * 0.23) * 3) + 0.25 * math.sin(y * 0.37 + x * 0.11)
    k = 0.86 + 0.2 * n + random.Random(x * 977 + y * 131).uniform(-0.05, 0.05)
    return (0.69 * k, 0.65 * k, 0.58 * k)                  # (a warm grey granite, weathered paler on top)


M_BW = mat('BreakwaterStone', '#ffffff', 0.9, image=make_image('breakwater', 64, 64, bw_stone_fn))
bw_mb = MB(uv=True)
_bw = random.Random(2510)
bw_end = curve('coast', BW_X) + BW_OUT
yb = BW_Y0
while yb < bw_end:
    out_ = max(0.0, yb - curve('coast', BW_X)) / BW_OUT        # (0 on the sand, 1 at its end)
    for row, dx in ((0, -0.42), (1, 0.42), (2, 0.0), (3, 0.0)):
        if row == 3 and _bw.random() < 0.5:
            continue
        r = _bw.uniform(0.95, 1.4) * (1.0 - 0.15 * out_) * (0.85 if row >= 2 else 1.0)
        x_ = BW_X + dx + _bw.uniform(-0.1, 0.1)
        y_ = yb + _bw.uniform(-0.2, 0.2)
        # (round 37, the user: "rocks appear to float, There shouldnt be gaps through it") seated on the ground or the
        # seabed under each stone itself, sunk a little into it
        g_ = max(-0.6, ground_z(x_, y_))                       # (out in the sea, a bed of stones under them at -0.6)
        zc = g_ + r * 0.15 + (r * 0.75 if row == 2 else (r * 1.2 if row == 3 else 0.0))
        M = Matrix.Translation(BT(x_, y_, zc)) @ Matrix.Rotation(_bw.uniform(0, 6.3), 4, 'Z') @ Matrix.Diagonal(
            (_bw.uniform(1.0, 1.3), _bw.uniform(0.85, 1.1), _bw.uniform(0.65, 0.85), 1))
        bw_mb.ico(M, r, M_BW, 1, r * 0.16, _bw)
    yb += _bw.uniform(0.36, 0.46)                           # (round 37: packed closer, no daylight between)
# (round 27, the user: "Add the breakwaters cutting out into the ocean from the beach… have lots of space
# between them like the real barcelona beach") more espigons, from the waterline out into the sea
# (round 36, the user marked them on the map: three, the far west one near the beach's west end; the big
# breakwater at the east end stays where it is)
ESPIGONS = (11.0, 45.0, 76.8)
for gx_ in ESPIGONS:
    yg = curve('coast', gx_) - 1.0
    g_end = curve('coast', gx_) + 11.0
    while yg < g_end:
        out_ = max(0.0, yg - curve('coast', gx_)) / 11.0
        for row, dx in ((0, -0.4), (1, 0.4), (2, 0.0)):
            r = _bw.uniform(0.95, 1.3) * (1.0 - 0.18 * out_)        # (round 37: the top row always, so no gaps)
            x_ = gx_ + dx + _bw.uniform(-0.1, 0.1)
            y_ = yg + _bw.uniform(-0.2, 0.2)
            g2_ = max(-0.6, ground_z(x_, y_))                       # (round 37: on the sand or seabed under it, not floating)
            zc = g2_ + r * 0.15 + (r * 0.7 if row == 2 else 0.0)
            M = Matrix.Translation(BT(x_, y_, zc)) @ Matrix.Rotation(_bw.uniform(0, 6.3), 4, 'Z') @ Matrix.Diagonal(
                (_bw.uniform(1.0, 1.3), _bw.uniform(0.85, 1.1), _bw.uniform(0.65, 0.85), 1))
            bw_mb.ico(M, r, M_BW, 1, r * 0.16, _bw)
        yg += _bw.uniform(0.36, 0.46)
city_objs.append(bw_mb.finish('Breakwater'))
scene['breakwater'] = [round((BW_X - OX) * T, 2), round((BW_Y0 - OY) * T, 2), round((bw_end - OY) * T, 2)]

# ------------------------------------------------------------------ what can't be walked through

BLOCKING = {'ROCK', 'RIVER', 'BOULDER', 'RAIL', 'HEDGE', 'FOUNT', 'STATION', 'WHEEL', 'TEMPLE', 'RIDE', 'BARRIER'}   # (the sea: below)
runs = {}
for Y in range(MH2):
    X = 0
    while X < MW2:
        if tile(X, Y) in BLOCKING and not in_north(X, Y):
            X1 = X
            while X1 < MW2 and tile(X1, Y) in BLOCKING and not in_north(X1, Y):
                X1 += 1
            runs.setdefault((X, X1), []).append(Y)
            X = X1
        else:
            X += 1
blocked = []
for (X0, X1), ys in runs.items():
    ys.sort()
    start = prev = ys[0]
    for Y in ys[1:] + [None]:
        if Y is not None and Y == prev + 1:
            prev = Y
            continue
        blocked.append([(X0 - OX) * T, (start - OY) * T, (X1 - OX) * T, (prev + 1 - OY) * T])
        if Y is not None:
            start = prev = Y
# the sea stops her at the waterline itself (round 23: it follows the coast's curve, half a tile at a time, not the tiles)
for i_ in range(-12, 2 * MW2 + 24):
    X_ = i_ / 2
    yc = min(curve('coast', max(0.0, X_)), curve('coast', max(0.0, X_ + 0.5))) + 0.06
    blocked.append([(X_ - OX) * T, (yc - OY) * T, (X_ + 0.5 - OX) * T, (MH2 + 20 - OY) * T])
blocked.append([(BW_X - 0.95 - OX) * T, (BW_Y0 - 0.6 - OY) * T, (BW_X + 0.95 - OX) * T, (bw_end + 0.5 - OY) * T])   # (the breakwater)
for gx_ in ESPIGONS:                                                 # (round 27: the espigons)
    blocked.append([(gx_ - 0.9 - OX) * T, (curve('coast', gx_) - 1.3 - OY) * T, (gx_ + 0.9 - OX) * T, (curve('coast', gx_) + 11.5 - OY) * T])
scene['blocked'] = [[round(v, 3) for v in r] for r in blocked]

# ------------------------------------------------------------------ the forest: a tree on every tree tile

CHUNK = 12
fchunks = {}


M_FBARK = mat('ForestBark', '#4f3d2e', 0.95)                  # the forest's own darker bark (the city's plane trees are pale)
M_PINEBARK = mat('PineBark', '#6e4630', 0.95)


def forest_tree(X, Y, collide, spread=0.3, shift=(0.0, 0.0), ground=None):
    x, y = X + 0.5 + shift[0] + nrng.uniform(-spread, spread), Y + 0.5 + shift[1] + nrng.uniform(-spread, spread)
    key = (int(x // CHUNK), int(y // CHUNK))
    if key not in fchunks:
        fchunks[key] = (MB(uv=True), Cards())
    trunks, crowns = fchunks[key]
    base = BT(x, y, 0.04 if ground is None else ground(x, y) - 0.15)
    r = nrng.random()
    if r < 0.25:
        # umbrella pine: a tall bare trunk, leaning a little, a wide flat crown
        h = nrng.uniform(4.5, 6.5)
        lean = Vector((nrng.uniform(-0.6, 0.6), nrng.uniform(-0.6, 0.6), 0))
        top = base + lean + Vector((0, 0, h))
        d = top - base
        M = Matrix.Translation((base + top) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        trunks.cone(M, 6, 0.17, 0.1, d.length, M_PINEBARK)
        rr = nrng.uniform(2.2, 3.0)
        crowns.clump(top + Vector((0, 0, 0.45)), (rr * 0.7, rr * 0.7, 0.35), 8, 1.3, M_PINE, nrng)
        crowns.shell(top + Vector((0, 0, 0.35)), (rr, rr, 0.85), 30, 1.4, M_PINE, nrng)
    elif r < 0.75:
        # holm oak (the most common: their round crowns fill the forest at eye level): short trunk, round dark crown
        h = nrng.uniform(1.8, 2.8)
        trunks.cone(Matrix.Translation(base + Vector((0, 0, h / 2))), 6, 0.2, 0.13, h, M_FBARK)
        rr = nrng.uniform(1.8, 2.6)
        c = base + Vector((0, 0, h + rr * 0.75))
        crowns.clump(c, (rr * 0.6, rr * 0.6, rr * 0.5), 7, 1.1, M_OAK, nrng)
        crowns.shell(c, (rr, rr, rr * 0.85), 28, 1.15, M_OAK, nrng)
    else:
        # a tall broadleaf (poplar, plane) where the forest is thickest
        h = nrng.uniform(1.8, 2.8)
        trunks.cone(Matrix.Translation(base + Vector((0, 0, h / 2))), 6, 0.16, 0.1, h, M_FBARK)
        c = base + Vector((0, 0, h + 1.5))
        crowns.shell(c, (1.8, 1.8, 2.0), 30, 1.2, M_PLANE_LEAVES, nrng)
    if collide:
        scene['trees'].append(mT(x, y))


# the eastern wood: its trees, undergrowth, trodden paths, meadow, lamps and walls (forest.py)
plant_forest()


# where the bike can't go: the beach's sand (she walks there, the bike stops dead). (The thick of the wood is
# roped off in the game, from trunk to trunk round its edge: main.gd, forest_ropes(), round 20e.)
def nobike_at(x, y):
    return tile_kind(int(math.floor(x)), int(math.floor(y))) in ('SAND', 'PALM')


scene['nobike'] = nobike_rects(nobike_at, -2.0, MW2 + 14.0, 4.0, MH2 + 2.0)
print('NOBIKE', len(scene['nobike']), 'rectangles')

# the thick of the wood, roped off from the bike from trunk to trunk round its edge (bike_rope.py): the ropes
# (the game makes each one a thin wall on the no-bike layer) and a map of what they close in (so she can't
# get on the bike in there), a quarter-metre cell to a pixel
def _rope_map():
    import sys, zlib, struct
    import mathutils.geometry as mg
    sys.path.insert(0, BUILD)
    from bike_rope import bike_rope, CELL

    def triangulate(P):
        r = mg.delaunay_2d_cdt([Vector((float(x), float(z))) for x, z in P], [], [], 0, 1e-6)
        return [[r[3][k][0] for k in f] for f in r[2] if len(f) == 3]
    ropes, mask, x0, z0 = bike_rope(scene['forest_trees'], scene['forest_paths'], triangulate)
    nz, nx = mask.shape
    raw = b''.join(b'\x00' + (mask[j] * 255).astype('uint8').tobytes() for j in range(nz))

    def chunk_(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    with open(os.path.join(OUT, 'forest_nobike.png'), 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk_(b'IHDR', struct.pack('>IIBBBBB', nx, nz, 8, 0, 0, 0, 0)) +
                chunk_(b'IDAT', zlib.compress(raw, 9)) + chunk_(b'IEND', b''))
    scene['bike_rope'] = {'ropes': ropes, 'map': 'forest_nobike.png', 'x0': round(x0, 3), 'z0': round(z0, 3), 'cell': CELL}


_rope_map()

# the mountain behind the city: wooded, like Collserola (its slopes are walled off by the map anyway)
TIB_CLEAR = [(21, 49, -1, 10.6), (38, 44, 9, 13.5), (33, 38, 8, 14.5)]     # the terrace, the funicular station, the steps
for Y in range(-8, MH2):
    for X in range(-6, MW2 + 6):
        k = tile(X, Y)
        if not (k in ('ROCK', 'BOULDER') or (k is None and Y < 0)) or in_north(X, Y):
            continue
        if any(a <= X <= b and c <= Y <= d for a, b, c, d in TIB_CLEAR):
            continue
        for _ in range(2):
            if nrng.random() < 0.5:
                forest_tree(X, Y, False, 0.45, ground=lambda gx, gy: rock_height(min(max(gx, 0.0), MW2 - 0.01), gy) + max(0.0, -gx) * 0.4)
for k, (trunks, crowns) in enumerate(fchunks.values()):
    city_objs.append(trunks.finish('ForestTrunks_%d' % k))
    city_objs.append(crowns.finish('Leaves_forest_%d' % k))
# undergrowth and boulders
def boulder_fn(x, y):
    # (round 38, the user: the forest's boulder "should be brown") a warm brown-grey stone, weathered in patches
    n = 0.5 + 0.25 * math.sin(x * 0.37 + math.sin(y * 0.29) * 3) + 0.25 * math.sin(y * 0.41 + x * 0.13)
    k = 0.8 + 0.3 * n + random.Random(x * 613 + y * 389).uniform(-0.05, 0.05)
    return (0.56 * k, 0.47 * k, 0.38 * k)


M_BOULDER = mat('BoulderStone', '#ffffff', 0.92, image=make_image('boulder', 64, 64, boulder_fn))
bush = Cards()
rocks = MB(uv=True)
for Y in range(MH2):
    for X in range(MW2):
        k = tile(X, Y)
        if k == 'BOULDER' and not in_north(X, Y):
            # (round 26: the 2D map's boulders fell on Gràcia's new streets: a "bush" stood on the crossing)
            c = BT(X + 0.5, Y + 0.5, tile_height(X, Y) + 0.4)
            # (round 38, the user: "The boulder in the forest is green when it should be brown": brown stone, not
            # the mountain's green scrub)
            rocks.ico(Matrix.Translation(c) @ Matrix.Diagonal((1.3, 1.0, 0.8, 1)), 1.1, M_BOULDER, 1, 0.25, nrng)
        elif k == 'GRASS' and nrng.random() < 0.025 and not in_city(X, Y) and X < 80 and not in_north(X, Y):
            c = BT(X + nrng.random(), Y + nrng.random(), 0.3)
            bush.clump(c, (0.7, 0.7, 0.4), 6, 0.6, M_SHRUB, nrng)
city_objs.append(bush.finish('Plants_undergrowth'))
city_objs.append(rocks.finish('Boulders'))

# ------------------------------------------------------------------ the city's edge: its footpath, the Rambla's promenade

def in_block_pave(x, y):
    """Is tile point (x, y) (our tiles) within a block's pavement ring? The blocks lay their own cut-corner
    pavements, so the 2D map's square corner tiles there are left as road (they made odd square nubs)."""
    return any(ox - 1 <= x <= ox + BS + 1 and oy - 1 <= y <= oy + BS + 1 for ox in COLS for oy in ROWS)


edge = MB(uv=True)
prom = MB(uv=True)
kerbs = MB()
pave_rects = []
# (round 36, the user: "the footpath crosses the road. The road should continue so that the cobblestones in this
# district join the bitumen in the eixample district… There are other examples… please fix them") where a street of
# Gràcia meets the city, the city's edge pavement no longer runs across its end: the street's cobbles go on to the
# city's asphalt, kerbs along the cut. (x0, z0, x1, z1) metres, and the side that meets the asphalt.
# (round 41, the user: "here there is cobblestone cutting across the footpath… The buildings should be surrounded by
# footpath": the Travessera's and Provença's mouths each had a second piece running sideways along the city's edge
# pavement past the corner — gone: the street meets the asphalt, the corner's footpath goes round unbroken)
MOUTHS = [((44.8, -101.5, 47.2, -95.7), 'z1'), ((72.8, -101.5, 75.2, -95.7), 'z1'),        # Carrer de l'Or, Verdi
          ((82.5, -98.2, 89.1, -92.8), 'x0'),                                               # Travessera de Dalt
          ((82.5, -53.2, 89.1, -49.5), 'x0')]                                               # Provença


def in_mouth(x, z):
    return any(r[0] < x < r[2] and r[1] < z < r[3] for r, _ in MOUTHS)


def rect_minus(r, m):
    """Rectangle r less rectangle m (both x0, z0, x1, z1): the pieces left."""
    if m[0] >= r[2] or m[2] <= r[0] or m[1] >= r[3] or m[3] <= r[1]:
        return [r]
    out = []
    if m[1] > r[1]:
        out.append((r[0], r[1], r[2], m[1]))
    if m[3] < r[3]:
        out.append((r[0], m[3], r[2], r[3]))
    za, zb = max(r[1], m[1]), min(r[3], m[3])
    if m[0] > r[0]:
        out.append((r[0], za, m[0], zb))
    if m[2] < r[2]:
        out.append((m[2], za, r[2], zb))
    return [q for q in out if q[2] - q[0] > 1e-3 and q[3] - q[1] > 1e-3]


def mB(x, z, h):
    return BT(x / T + OX, z / T + OY, h)
M_PROM = mat('Promenade', '#ffffff', 0.92, image=make_image('promenade', 64, 64, lambda x, y: tuple(
    v * (1 + random.Random(x * 13 + y * 7).uniform(-0.05, 0.05)) * (0.92 if (x % 16 == 0 or y % 16 == 0) else 1) for v in rgb('#d8c9a8'))))
for Y in range(MH2):
    for X in range(MW2):
        k = tile(X, Y)
        if k not in ('PAVE', 'WALK', 'PROM'):
            continue
        cx, cy = X + 0.5 - OX, Y + 0.5 - OY
        if k != 'PROM' and in_block_pave(cx, cy):
            continue
        h = KERB - 0.003
        r0_ = tuple(mT(X, Y)) + tuple(mT(X + 1, Y + 1))
        pcs_ = [r0_]
        for (m_, _) in MOUTHS:
            pcs_ = [q_ for p_ in pcs_ for q_ in rect_minus(p_, m_)]
        if pcs_ != [r0_]:
            for (a0, b0, a1, b1) in pcs_:                                    # (a pavement tile cut by a street's end)
                edge.face([mB(a0, b0, h), mB(a1, b0, h), mB(a1, b1, h), mB(a0, b1, h)], M_PANOT, normal=(0, 0, 1), uvscale=0.6)
                pave_rects.append((a0, b0, a1, b1))
                for (p0, p1, ox_, oz_, nb_) in (((a0, b0), (a1, b0), 0, -1, (0, -1)), ((a1, b0), (a1, b1), 1, 0, (1, 0)),
                                                ((a1, b1), (a0, b1), 0, 1, (0, 1)), ((a0, b1), (a0, b0), -1, 0, (-1, 0))):
                    mx_, mz_ = (p0[0] + p1[0]) / 2 + ox_ * 0.05, (p0[1] + p1[1]) / 2 + oz_ * 0.05
                    if in_mouth(mx_, mz_):
                        kerbs.face([mB(*p0, 0), mB(*p1, 0), mB(*p1, KERB), mB(*p0, KERB)], M_KERB, normal=(ox_, -oz_, 0))
            continue
        q = [BT(X, Y, h), BT(X + 1, Y, h), BT(X + 1, Y + 1, h), BT(X, Y + 1, h)]
        (prom if k == 'PROM' else edge).face(q, M_PROM if k == 'PROM' else M_PANOT, normal=(0, 0, 1), uvscale=0.6)
        pave_rects.append(mT(X, Y) + mT(X + 1, Y + 1))
        # a kerb wherever it meets the road or nature
        for (dx, dy, a, b) in ((0, -1, (X, Y), (X + 1, Y)), (1, 0, (X + 1, Y), (X + 1, Y + 1)),
                               (0, 1, (X + 1, Y + 1), (X, Y + 1)), (-1, 0, (X, Y + 1), (X, Y))):
            nk = tile(X + dx, Y + dy)
            if in_mouth((X + 0.5 + dx * 0.52 - OX) * T, (Y + 0.5 + dy * 0.52 - OY) * T):
                kerbs.face([BT(*a, 0), BT(*b, 0), BT(*b, KERB), BT(*a, KERB)], M_KERB, normal=(dx, -dy, 0))
                continue                                             # (round 36: onto a street's end)
            if nk in ('PAVE', 'WALK', 'PROM', 'BLDG', 'COURT', 'SPECIAL', 'DOOR') or nk is None:
                continue
            if nk not in ('ROAD', 'BRIDGE') and in_block_pave(X + dx + 0.5 - OX, Y + dy + 0.5 - OY):
                continue
            kerbs.face([BT(*a, 0), BT(*b, 0), BT(*b, KERB), BT(*a, KERB)], M_KERB, normal=(dx, -dy, 0))
# the streets' cobbles on through their ends, over the ground there, easing down onto the asphalt at its edge
mouths_ = MB(uv=True)
for (m_, lip_) in MOUTHS:
    xs_ = [m_[0] + (m_[2] - m_[0]) * i / max(1, int(math.ceil((m_[2] - m_[0]) / 0.5))) for i in range(int(math.ceil((m_[2] - m_[0]) / 0.5)) + 1)]
    zs_ = [m_[1] + (m_[3] - m_[1]) * i / max(1, int(math.ceil((m_[3] - m_[1]) / 0.5))) for i in range(int(math.ceil((m_[3] - m_[1]) / 0.5)) + 1)]

    def mh_(x, z, m_=m_, lip_=lip_):
        if (lip_ == 'x0' and abs(x - m_[0]) < 1e-6) or (lip_ == 'z1' and abs(z - m_[3]) < 1e-6):
            return 0.005
        return max(NORTH.ground(x, z), 0.05) + 0.015
    for xa_, xb_ in zip(xs_, xs_[1:]):
        for za_, zb_ in zip(zs_, zs_[1:]):
            mouths_.face([mB(xa_, za_, mh_(xa_, za_)), mB(xb_, za_, mh_(xb_, za_)), mB(xb_, zb_, mh_(xb_, zb_)),
                          mB(xa_, zb_, mh_(xa_, zb_))], M_SETTS, normal=(0, 0, 1), uvscale=1.0)
city_objs.append(mouths_.finish('StreetMouths'))
city_objs.append(edge.finish('PavementEdge'))
city_objs.append(prom.finish('Promenade'))
city_objs.append(kerbs.finish('KerbsEdge'))
# merge the pavement squares into rows, for the game's ground heights
rows_ = {}
for r in pave_rects:
    rows_.setdefault((r[1], r[3]), []).append((r[0], r[2]))
scene['pave_rects'] = []
for (z0, z1), xs in rows_.items():
    xs.sort()
    a, b = xs[0]
    for (c, d) in xs[1:] + [(None, None)]:
        if c is not None and abs(c - b) < 0.01:
            b = d
            continue
        scene['pave_rects'].append([a, z0, b, z1])
        if c is not None:
            a, b = c, d
# roads outside the city's rectangle (Mallorca running out to the bridge)
xroad = MB(uv=True)
for Y in range(MH2):
    for X in range(MW2):
        if tile(X, Y) == 'ROAD' and not (W2['CITY'][0] <= X < W2['CITY'][2] and W2['CITY'][1] <= Y < W2['CITY'][3]):
            xroad.face([BT(X, Y, 0), BT(X + 1, Y, 0), BT(X + 1, Y + 1, 0), BT(X, Y + 1, 0)], M_ROAD, normal=(0, 0, 1), uvscale=4.0)
city_objs.append(xroad.finish('RoadOut'))

# the Rambla's plane trees, along both edges of its promenade (clear of its benches, kiosk and stalls)
busy = {(o['x'], o['y']) for o in W2['objects'] if o['type'] in ('bench', 'kiosk', 'stall', 'fountain', 'mosaic', 'lampR')}
for X in (W2['RAMBLA_PROM'][0], W2['RAMBLA_PROM'][1]):
    for Y in range(W2['CITY'][1] + 2, W2['CITY'][3] - 1, 1):
        if Y % 2 or tile(X, Y) != 'PROM' or (X, Y) in busy or (X, Y + 1) in busy or (X, Y - 1) in busy:
            continue
        if any(abs(Y - (h['y'] + 1.5)) < 2.6 for h in W2['HSTREETS']):
            continue                                   # not across the junctions
        plane_tree(X + 0.5 - OX + (-0.12 if X == W2['RAMBLA_PROM'][0] else 0.12), Y + 0.5 - OY)

# ------------------------------------------------------------------ the beach's life (round 26, the user: "make the
# world complete": the sand was empty from the promenade to the breakwater): parasols in loose rows with towels under
# them, lone towels, a volleyball net, two beached boats near the breakwater; thinning out eastwards
bl_rng = random.Random(1888)
blife = MB(uv=True)
PARASOL_COLS = ['#d9534f', '#3a7bd5', '#f2c84b', '#3caa7a', '#e87a2f', '#7a5fb5']


def towel(x, y, hw, hl, m):
    """A towel lying ON the sand: a little quad whose corners each sit on the sand's own height."""
    if tile_kind(int(math.floor(x)), int(math.floor(y))) != 'SAND':
        return                                        # (round 27: one lay on the promenade's paving)
    a_ = bl_rng.uniform(0, math.pi)
    u_ = (math.cos(a_), math.sin(a_))
    n_ = (-math.sin(a_), math.cos(a_))
    q = []
    for (su, sn) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        tx_, ty_ = x + u_[0] * su * hw + n_[0] * sn * hl, y + u_[1] * su * hw + n_[1] * sn * hl
        q.append(BT(tx_, ty_, sand_height(tx_, ty_) + 0.02))
    blife.face(q, m, normal=(0, 0, 1))


def parasol(x, y, col):
    h0 = sand_height(x, y)
    c = BT(x, y, h0)
    a_ = bl_rng.uniform(0, math.pi)
    blife.cone(Matrix.Translation(c + Vector((0, 0, 1.0))) @ Matrix.Rotation(bl_rng.uniform(-0.08, 0.08), 4, 'X'), 6, 0.03, 0.03, 2.0, M_IRON)
    blife.cone(Matrix.Translation(c + Vector((0, 0, 1.95))), 10, 1.15, 0.05, 0.45, mat('Parasol' + col, col, 0.85))
    for j in range(bl_rng.randint(1, 2)):
        ta = a_ + j * 2.2
        towel(x + math.cos(ta) * 0.34, y + math.sin(ta) * 0.34, 0.07, 0.14,
              mat('TowelB%d' % ((j + int(x)) % 4), ['#f4f0e8', '#e94e3c', '#3a7bd5', '#f2d27a'][(j + int(x)) % 4], 0.95))
    scene['obstacles'].append({'pos': bl_m(c), 'off': [0, 0], 'r': 0.5})


n_par = 0
# (eleven spots, loosely grouped as bathers group, thinning towards the breakwater; jittered, never in the water)
for (xt, back) in ((39.5, 5.8), (41.2, 3.2), (43.0, 5.0), (49.5, 3.4), (52.0, 6.2), (56.5, 4.2), (60.2, 3.0),
                   (63.0, 5.5), (67.5, 3.6), (72.0, 5.2), (74.4, 4.0)):   # (round 36: clear of the moved espigons)
    x = xt + bl_rng.uniform(-0.5, 0.5)
    y = curve('coast', x) - back                                             # (dry sand, so far back from the water)
    # (round 33, the user: "There is an umbrella at the beach" — where the beach is narrow, so far back put two on the
    # promenade's paving, alone, their towels refused: down the beach until on sand with a stride of sand behind it)
    while tile_kind(int(math.floor(x)), int(math.floor(y - 0.6))) != 'SAND' and y < curve('coast', x) - 1.5:
        y += 0.25
    parasol(x, y, PARASOL_COLS[n_par % len(PARASOL_COLS)])
    n_par += 1
print('BEACH parasols %d' % n_par)
# lone towels nearer the water
for k in range(7):
    x = bl_rng.uniform(42, 74)
    y = curve('coast', x) - bl_rng.uniform(2.2, 3.0)
    towel(x, y, 0.07, 0.14, mat('TowelL%d' % (k % 4), ['#e94e3c', '#3caa7a', '#f4f0e8', '#3a7bd5'][k % 4], 0.95))
# a volleyball net
vx, vy = 57.0, 90.5
vh = sand_height(vx, vy)
# (round 35: the posts at the net's ends — they stood 1.6 tiles out, 10 m apart, the 3.2 m net floating between them)
vs_ = 1.65 / 3.3
for sd in (-vs_, vs_):
    blife.cone(Matrix.Translation(BT(vx + sd, vy, vh + 1.1)), 6, 0.04, 0.04, 2.2, M_WOODEN)
blife.box(BT(vx, vy, vh + 1.75), (1, 0), (0, 1), 1.6, 0.012, 0.35, mat('BeachNet', '#f4f0e8', 0.9))
scene['obstacles'].append({'pos': bl_m(BT(vx - vs_, vy, 0)), 'off': [0, 0], 'r': 0.3})
scene['obstacles'].append({'pos': bl_m(BT(vx + vs_, vy, 0)), 'off': [0, 0], 'r': 0.3})
city_objs.append(blife.finish('BeachLife'))
# a stroll along the water's edge
scene['people'].append({'a': [round((44 - OX) * T, 1), round((curve('coast', 44) - 4.0 - OY) * T, 1)],
                        'b': [round((72 - OX) * T, 1), round((curve('coast', 72) - 4.0 - OY) * T, 1)]})

# (round 27 added a city bus, three little cars and four bus stops here; round 33, the user: "Get rid of the
# cars/bus and bus stops. Revert the game to what was there before." — gone, with engine/traffic.gd)

# ------------------------------------------------------------------ the bridge over the Llobregat (closed)

br = MB(uv=True)
bys = [Y for Y in range(MH2) if any(tile(X, Y) == 'BRIDGE' for X in range(10))]
by0, by1 = min(bys), max(bys) + 1
bx0, bx1 = -1.05, 5.2                                  # (round 32: the deck used to run on 2 tiles past the west
#                                                        bank, a bare stone slab with the rising grass cutting
#                                                        through it; it lands on the bank now, and a worn track
#                                                        carries the way on up the meadow)
br.face([BT(bx0, by0, 0.02), BT(bx1, by0, 0.02), BT(bx1, by1, 0.02), BT(bx0, by1, 0.02)], M_GREYSTONE, normal=(0, 0, 1), uvscale=2.0)
for (yy, side) in ((by0 - 0.15, -1), (by1 + 0.15, 1)):
    br.box(BT((bx0 + bx1) / 2, yy, 0.55), (1, 0), (0, 1), (bx1 - bx0) / 2 * T, 0.15 * T, 0.55, M_GREYSTONE)      # parapets
    for X in range(int(bx0), int(bx1)):
        # (round 32's tests: the coping stones used to overhang the deck's walking line by 6 cm at head
        # height — Sandra sliding along the parapet caught her head on one and stood pinned until she
        # side-stepped. Each row sits a hand further out now; the outward overhang stays.)
        br.box(BT(X + 0.5, yy + side * 0.025, 1.12), (1, 0), (0, 1), 0.2, 0.17 * T, 0.04, M_STONE)
for X in (0.0, 2.6):                                   # the arches' piers, down in the water
    br.box(BT(X, (by0 + by1) / 2, -0.8), (1, 0), (0, 1), 0.5, (by1 - by0 + 0.3) / 2 * T, 0.85, M_GREYSTONE)
# the barrier: a red and white pole across, on posts, with a no-entry sign
for k in range(8):
    br.box(BT(0.6, by0 + 0.2 + k * (by1 - by0 - 0.4) / 8 + (by1 - by0 - 0.4) / 16, 1.0), (1, 0), (0, 1), 0.06,
           (by1 - by0 - 0.4) / 16 * T, 0.06, M_RED if k % 2 else M_WHITE)
for yy in (by0 + 0.15, by1 - 0.15):
    br.box(BT(0.6, yy, 0.5), (1, 0), (0, 1), 0.07, 0.07, 0.5, M_WHITE)
br.cone(Matrix.Translation(BT(0.6, (by0 + by1) / 2, 1.6)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'), 20, 0.3, 0.3, 0.03, M_RED)
br.box(BT(0.62, (by0 + by1) / 2, 1.6), (0, 1), (1, 0), 0.2, 0.025, 0.05, M_WHITE)
# (round 32) past the bridge the way goes on as a worn track up the meadow, dying out over the rise — a road
# should lead somewhere, even a closed one. The track lies on the terrain grid's own surface (mimicked here:
# its points are tile-centre heights, averaged at tile edges), a hair above it.


def west_bank_h(px):
    def th2_(Xt):
        return 0.05 + min(6.0, -Xt * 0.25) if Xt < 0 else 0.05

    def pt_(p):
        if abs(p - round(p)) < 1e-6:
            return (th2_(round(p) - 1) + th2_(round(p))) / 2
        return th2_(math.floor(p))
    p0 = math.floor(px * 2) / 2
    a = (px - p0) * 2
    return pt_(p0) * (1 - a) + pt_(p0 + 0.5) * a


track_y = (by0 + by1) / 2
# (round 41: with the farmland, the way past the bridge is a proper road, north_build.py; no worn track)
tw_ = [] if WEST_FIELDS else [(-1.0 - 0.45 * k, 0.36 * (1.0 - k / 16.0) + 0.03) for k in range(17)]
for ((xa_, wa_), (xb_, wb_)) in zip(tw_, tw_[1:]):
    ha_, hb_ = west_bank_h(xa_) + 0.03, west_bank_h(xb_) + 0.03
    br.face([BT(xa_, track_y - wa_, ha_), BT(xb_, track_y - wb_, hb_), BT(xb_, track_y + wb_, hb_), BT(xa_, track_y + wa_, ha_)],
            M_PATH, normal=(0, 0, 1), uvscale=2.5)
city_objs.append(br.finish('Bridge'))
scene['bridge_rect'] = [round((bx0 - OX) * T, 3), round((by0 - OY) * T, 3), round((bx1 - OX) * T, 3), round((by1 - OY) * T, 3)]

# ------------------------------------------------------------------ the north (round 22): the funfair up its hill, the
# cable car, the path, Gràcia, Park Güell (north_build.py); the old terrace, its steps and the funicular are gone
exec(open(os.path.join(BUILD, 'north_build.py')).read())

# ------------------------------------------------------------------ the beach: palms on the planted row, the lifeguard tower

palms_mb, fronds = MB(uv=True), Cards()


def frond(cards, base, ang, droop, length, width, m):
    """One palm frond: a long card hanging out from the crown."""
    if m not in cards.mats:
        cards.mats.append(m)
    d = Vector((math.cos(ang) * math.cos(droop), math.sin(ang) * math.cos(droop), -math.sin(droop)))
    side = Vector((-math.sin(ang), math.cos(ang), 0)) * width / 2
    mid = base + d * length * 0.5 + Vector((0, 0, -length * 0.12))       # curving down towards the tip
    tip = base + d * length + Vector((0, 0, -length * 0.35))
    up = d.cross(side).normalized()
    if up.z < 0:
        up = -up
    for (p0, p1, u0, u1) in ((base, mid, 0.0, 0.5), (mid, tip, 0.5, 1.0)):
        b = len(cards.verts)
        for p, uv in ((p0 - side, (u0, 0)), (p1 - side, (u1, 0)), (p1 + side, (u1, 1)), (p0 + side, (u0, 1))):
            cards.verts.append(p)
            cards.nrm.append(up)
            cards.uvs.append(uv)
        cards.faces.append((b, b + 1, b + 2, b + 3))
        cards.fmat.append(cards.mats.index(m))


def palm(X, Y, h0):
    base = BT(X, Y, h0)
    h = nrng.uniform(6.0, 8.5)
    bend = Vector((nrng.uniform(-0.5, 0.5), nrng.uniform(-0.5, 0.5), 0))
    prev = base
    for k in range(1, 6):
        t = k / 5
        p = base + bend * t * t + Vector((0, 0, h * t))
        d = p - prev
        M = Matrix.Translation((p + prev) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        palms_mb.cone(M, 7, 0.19 - 0.04 * t, 0.17 - 0.04 * t, d.length + 0.05, M_PALM_TRUNK)
        prev = p
    palms_mb.sphere(Matrix.Translation(prev), 0.28, M_PALM_TRUNK, (8, 6))
    for k in range(13):
        frond(fronds, prev + Vector((0, 0, 0.1)), k * 2 * math.pi / 13 + nrng.uniform(-0.2, 0.2), nrng.uniform(0.0, 0.5),
              nrng.uniform(2.4, 3.0), 0.75, M_PALM)
    scene['trees'].append(mT(X, Y))


# (round 23, the user: "move the palm trees closer to the grass and don't have them in such a straight row"): each
# palm off its tile's centre by its own random amount; by the wood, drawn back up the beach towards the grass
palm_rng = random.Random(23)
for Y in range(MH2):
    for X in range(MW2):
        if tile(X, Y) == 'PALM':
            px, py = X + 0.5 + palm_rng.uniform(-0.4, 0.4), Y + 0.5 + palm_rng.uniform(-0.15, 0.45)
            if X >= 84:
                first_sand = next((yy for yy in range(80, Y + 1) if tile(X, yy) in ('SAND', 'PALM')), Y)
                py = first_sand + palm_rng.uniform(0.2, 0.75)
            palm(px, py, sand_height(px, py))
city_objs.append(palms_mb.finish('Palms'))
city_objs.append(fronds.finish('Leaves_palms'))

# ------------------------------------------------------------------ the things the 2D game sets about the streets

M_SIGNBOARD = mat('SignBoard', '#2f4f6f', 0.6)
M_SIGNFACE = mat('SignFace', '#f4ead2', 0.7)
M_SIGNINK = mat('SignInk', '#22385a', 0.5)


def sign_heading(text):
    """The heading painted on a sign: its first line, or up to its first full stop or dash, in at most
    two short lines (the whole text is read with E)."""
    head = text.split('\n')[0]
    for cut in ('. ', ' — '):
        if cut in head:
            head = head.split(cut)[0]
    head = ' '.join(head.strip().rstrip('.').split())
    words = head.split()
    if len(head) <= 16 or len(words) < 2:
        return [head]
    # two lines, as even as can be
    best = min(range(1, len(words)), key=lambda k: max(len(' '.join(words[:k])), len(' '.join(words[k:]))))
    lines = [' '.join(words[:best]), ' '.join(words[best:])]
    return lines


things = MB(uv=True)
scene.setdefault('things2d', [])
lamp_seen = set()
BENCH_ROT = {}
# (moving La Rambla a block west put four of its benches on the very tiles of its lamp posts: a bench that
# shares a lamp's tile slides half a tile along the promenade, between the lamps)
LAMP_TILES = {(o['x'], o['y']) for o in W2['objects'] if o['type'] == 'lampR'}
CAFE_OBS = [o_ for o_ in scene['obstacles'] if o_['r'] >= 0.9]          # (the kit's café terraces, placed already)
for o in W2['objects']:
    X, Y, typ = o['x'], o['y'], o['type']
    x, y = X + 0.5 - OX, Y + 0.5 - OY
    k = tile(X, Y)
    h = KERB if k in ('PAVE', 'WALK', 'PROM') else (H_T if k in ('TERRACE',) else tile_height(X, Y))
    c = BT(X + 0.5, Y + 0.5, h)
    if typ == 'lamp':
        continue                                     # the corner lamps and their street plaques come with the blocks
    if typ in ('bin', 'sign', 'bench', 'bikestand', 'terrace'):
        # (round 21) not in front of a doorway: slid along the pavement to the nearest place clear of every door
        if typ in ('bin', 'sign', 'terrace') and k in ('PAVE', 'WALK'):
            # (round 33: the 2D map put them on the tile's middle — the middle of the pavement, in everyone's way;
            # bins and signs stand by the kerb now, a café's tables on the kerb side, the walkway along the fronts)
            kq = kerb_side(c.x / T, -c.y / T, 0.38 if typ == 'terrace' else 0.2)
            if kq is not None:
                c = B(kq[0], kq[1], h)

        def _clear(q, trees=True):
            if not all(Vector((q.x - _d.x, q.y - _d.y)).length >= 1.5 for _d, _u in DECO_DOORS):
                return False
            if not crossing_clear(q.x / T, -q.y / T, 0.65 if typ == 'terrace' else 0.35):
                return False                         # (round 33: nor in front of a crossing — a café's table by its spread)
            if k in ('PAVE', 'WALK') and kerb_side(q.x / T, -q.y / T) is None and kerb_side(c.x / T, -c.y / T) is not None:
                return False                         # (and still on the pavement it started on, not slid into the road)
            # (round 23, the user: a bin stood in a café table on La Rambla) clear of the shops' café terraces too
            qm = bl_m(q)
            # (round 35, the everything-visit: a bin stood in a rack of parked bikes, under them) clear of those too
            # (round 41, the user: "the bin east of the Cascada Park is right next to the bikes, and so it's blocking the
            # footpath. Move it somewhere else": a bin keeps 2.6 m from them, so the way past stays open)
            if any(math.hypot(qm[0] - b_['pos'][0], qm[1] - b_['pos'][1]) < (2.6 if typ == 'bin' else 1.4) for b_ in LIFE_BIKES):
                return False
            # (round 35, the second look: a café table's umbrella pole stood up through a street tree's trunk)
            if trees and typ == 'terrace' and any(math.hypot(qm[0] - t_[0], qm[1] - t_[1]) < 1.5 for t_ in scene['trees']):
                return False
            return all(math.hypot(qm[0] - o_['pos'][0], qm[1] - o_['pos'][1]) >= o_['r'] + 0.7 for o_ in CAFE_OBS)
        # (round 35: clear of the street trees too if it can be; where it can't, a café keeps its place as before —
        # the user: change what is there, take nothing away)
        for _trees in ((True, False) if typ == 'terrace' else (True,)):
            if _clear(c, _trees):
                break
            _d, _u = min(DECO_DOORS, key=lambda du: Vector((c.x - du[0].x, c.y - du[0].y)).length)
            # (along the house fronts first; round 33: then along either street axis, so one standing in a
            # crossing's landing at a corner still finds a clear place)
            _done = False
            for _dir in (_u, Vector((1, 0, 0)), Vector((0, 1, 0))):
                for _s in (0.8, -0.8, 1.6, -1.6, 2.4, -2.4, 3.2, -3.2, 4.0, -4.0):
                    if _clear(c + _dir * _s, _trees):
                        c = c + _dir * _s
                        _done = True
                        break
                if _done:
                    break
            if _done:
                break
        if typ == 'terrace' and not _clear(c, False):
            continue                                 # (round 33: no clear place for its tables: none, rather than on a crossing)
    if typ == 'lampR':
        n_kerb = None
        if o.get('edge') and Y > 80:
            Y, y, h = Y - 1, y - 1.3, KERB      # the beach's lamps stand on the Passeig's pavement, not in the sand
            #                                     (round 33: 1 m further in — at y − 1 their feet stood on the sand's edge)
        elif o.get('edge'):
            # the others stand on the city's edge footpath, at its grass side, never across a way into the
            # meadow (round 20: they stood on the grass, one right on a footpath to the wood)
            if X > 78:
                x = 81.78 - OX
            elif X < 10 and Y > 15:
                x = 7.22 - OX
            if Y < 16:
                y = 14.22 - OY
                if NORTH.GRACIA_ZONE[0] < x * T < NORTH.GRACIA_ZONE[2]:
                    # (round 35, the everything-visit: here Gràcia's houses stand on that path since round 26 and the
                    # lamp was inside them; at the kerb of the pavement in front of them instead)
                    y = -96.4 / T
                    n_kerb = (0, 1)                         # (and its arm over the road to the south, as at a kerb)
            h = KERB
            for py in [P_['pts'][0][1] for P_ in PATHS if P_['kind'] == 'meadow'] if X > 78 else []:
                if abs(y + OY - py) < 1.2:
                    y = py - OY + (1.5 if y + OY >= py else -1.5)
        n = n_kerb or ((0, 1) if Y > 80 else ((0, -1) if Y < 16 else ((1, 0) if X < 10 else ((-1, 0) if X > 78 else (1 if X <= W2['RAMBLA_PROM'][1] else -1, 0)))))
        if any(math.hypot(x * T - lx_, y * T - lz_) < 7.0 for (lx_, lz_) in NORTH.SOL_LAMPS):
            continue                            # (round 36, the user: "just too close to the others" — the Plaça del Sol's
            #                                     own corner lamps light that corner)
        lamp_post(x, y, n)
        scene['things2d'].append({'type': 'lampR', 'pos': mT(x + OX, y + OY), 'text': '', 'id': '', 'h': round(h, 3)})
        continue
    if typ == 'bench':
        if (X, Y) in LAMP_TILES:
            dy = 0.5 if (X, Y + 1) not in LAMP_TILES else -0.5
            c = BT(X + 0.5, Y + 0.5 + dy, h)
            Y = Y + dy                                   # (a half tile: the 2D tile it came from stays its id)
        if BENCHES:
            if W2['RAMBLA_PROM'][0] <= X <= W2['RAMBLA_PROM'][1]:
                rot = -math.pi / 2 if X == W2['RAMBLA_PROM'][0] else math.pi / 2   # facing across the promenade
            else:
                rot = math.pi if Y < 12 else 0.0                                 # on the terrace, facing the view
            meshy_place('bench.glb', 5000, 'base', 0.86, c, rot, 'StreetBench_2d_%d_%d' % (X, Y), 1024)
            scene['obstacles'].append({'pos': mT(X + 0.5, Y + 0.5), 'off': [0, 0], 'r': 0.75})
        scene['things2d'].append({'type': 'bench', 'pos': mT(X + 0.5, Y + 0.5), 'text': '', 'id': '%d_%d' % (X, Y), 'h': round(h, 3)})
        continue
    if typ == 'kiosk':
        things.box(c + Vector((0, 0, 1.3)), (1, 0), (0, 1), 1.2, 1.0, 1.3, M_GREEN)
        things.cone(Matrix.Translation(c + Vector((0, 0, 2.85))) @ Matrix.Rotation(math.pi / 4, 4, 'Z'), 4, 2.0, 0.3, 0.5, M_GREEN, smooth=False)
        for sx in (-1, 1):
            things.box(c + Vector((sx * 0.9, -1.03, 1.2)), (1, 0), (0, 1), 0.25, 0.02, 0.35, rng_col := mat('Postcards', '#e8c96a', 0.7))
        things.box(c + Vector((0, -1.04, 1.2)), (1, 0), (0, 1), 0.55, 0.02, 0.45, mat('Newspapers', '#efeae0', 0.8))
    elif typ == 'stall':
        things.box(c + Vector((0, 0, 0.45)), (1, 0), (0, 1), 1.0, 0.7, 0.45, M_WOODEN)
        things.box(c + Vector((0, 0, 2.3)), (1, 0), (0, 1), 1.2, 0.9, 0.05, stripes_mat('#3e7a4a', '#f2ead8'))
        for sx in (-1, 1):
            for sy in (-1, 1):
                things.cone(Matrix.Translation(c + Vector((sx * 1.1, sy * 0.8, 1.15))), 5, 0.03, 0.03, 2.3, M_IRON)
        fl = Cards()
        for j in range(6):
            p = c + Vector((-0.7 + j * 0.28, -0.3 + (j % 2) * 0.35, 1.05))
            things.cone(Matrix.Translation(p - Vector((0, 0, 0.12))), 8, 0.13, 0.11, 0.25, M_BUCKET)
            fl.clump(p + Vector((0, 0, 0.15)), (0.18, 0.18, 0.18), 5, 0.35, [M_GERANIUM_CARD, M_PINK, M_DAISY][j % 3], nrng)
        city_objs.append(fl.finish('Plants_stall'))
    elif typ == 'fountain':
        # the Font de Canaletes: a cast-iron column with four taps and a lantern on top
        things.cone(Matrix.Translation(c + Vector((0, 0, 0.15))), 12, 0.7, 0.75, 0.3, M_GREYSTONE)
        things.cone(Matrix.Translation(c + Vector((0, 0, 1.4))), 10, 0.22, 0.3, 2.4, M_GREEN)
        for k in range(4):
            a = k * math.pi / 2
            things.box(c + Vector((math.cos(a) * 0.32, math.sin(a) * 0.32, 0.95)), (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a)), 0.12, 0.03, 0.03, M_BRASS)
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            things.cone(Matrix.Translation(c + Vector((math.cos(a) * 0.4, math.sin(a) * 0.4, 3.0))), 8, 0.12, 0.12, 0.35, M_LAMPGLASS)
        things.cone(Matrix.Translation(c + Vector((0, 0, 2.7))), 10, 0.5, 0.1, 0.2, M_GREEN)
    elif typ == 'mosaic':
        # Miró's mosaic, set into the pavement: bold circles of red, blue and yellow
        for j, (dx, dy, rr, col) in enumerate(((0, 0, 1.3, '#f2ede0'), (-0.4, 0.3, 0.45, '#d8342f'), (0.5, -0.2, 0.4, '#2f5aa8'),
                                               (0.1, 0.6, 0.3, '#f2c84b'), (0.55, 0.5, 0.2, '#1d1d1d'), (-0.6, -0.5, 0.25, '#f2c84b'))):
            things.cone(Matrix.Translation(c + Vector((dx, dy, 0.003 + j * 0.002))), 24, rr, rr, 0.004, mat('Miro%d' % j, col, 0.7))
    elif typ == 'terrace':
        if os.path.exists(meshy_file('cafe.glb')):
            meshy_place('cafe.glb', 7000, 'base', 2.4, c, nrng.uniform(0, 1), 'MeshyCafe_2d_%d' % X, 1024)
    elif typ == 'bikestand':
        # Jordi's workshop on the pavement: a repair stand with a bike up on it, a crate of inner tubes
        things.cone(Matrix.Translation(c + Vector((0, 0, 0.6))), 6, 0.04, 0.04, 1.2, M_IRON)
        things.box(c + Vector((0, 0, 1.2)), (1, 0), (0, 1), 0.3, 0.05, 0.05, M_IRON)
        things.box(c + Vector((0.9, 0.3, 0.25)), (1, 0), (0, 1), 0.3, 0.25, 0.25, M_CRATE)
        things.box(c + Vector((-0.8, 0.4, 0.2)), (1, 0), (0, 1), 0.18, 0.12, 0.1, mat('Radio', '#7a3a2a', 0.6))
    elif typ == 'bin':
        things.cone(Matrix.Translation(c + Vector((0, 0, 0.45))), 12, 0.28, 0.24, 0.9, M_GREEN)
        things.cone(Matrix.Translation(c + Vector((0, 0, 0.92))), 12, 0.3, 0.3, 0.04, M_IRON)
    elif typ == 'tower':
        for sx in (-0.5, 0.5):
            for sy in (-0.5, 0.5):
                things.cone(Matrix.Translation(c + Vector((sx, sy, 1.2))), 6, 0.06, 0.06, 2.4, M_WHITE)
        things.box(c + Vector((0, 0, 2.5)), (1, 0), (0, 1), 0.8, 0.8, 0.08, M_WOODEN)
        things.box(c + Vector((0, 0, 3.2)), (1, 0), (0, 1), 0.75, 0.75, 0.6, M_RED)
        city_objs.append(text_obj('SOCORRISME', 0.16, M_WHITE, c + Vector((0, -0.76, 3.25)), 0.0, 'TowerText_%d_%d' % (X, Y)))
        things.box(c + Vector((0, 0, 3.9)), (1, 0), (0, 1), 0.9, 0.9, 0.08, M_WHITE)
        things.cone(Matrix.Translation(c + Vector((0.6, 0.6, 4.6))), 5, 0.02, 0.02, 1.4, M_IRON)
        things.box(c + Vector((0.85, 0.6, 5.1)), (1, 0), (0, 1), 0.25, 0.01, 0.15, mat('FlagGreen', '#3caa4a', 0.7))
    elif typ == 'umbrella':
        things.cone(Matrix.Translation(c + Vector((0, 0, 1.1))), 6, 0.025, 0.025, 2.2, M_IRON)
        things.cone(Matrix.Translation(c + Vector((0, 0, 2.05))), 10, 1.05, 0.04, 0.35, mat('Umbrella' + o['col'], o['col'], 0.8))
        for j in range(2):
            ang = nrng.uniform(0, math.pi)
            tc = c + Vector((math.cos(ang) * 1.2, math.sin(ang) * 1.2, 0.005))
            things.box(tc, (math.cos(ang + 1.2), math.sin(ang + 1.2)), (-math.sin(ang + 1.2), math.cos(ang + 1.2)), 0.42, 0.85, 0.008,
                       mat('Towel%d' % j, ['#e94e3c', '#3a7bd5'][j], 0.95))
    elif typ == 'sign':
        # a board on a post: blue all round (and on the back), its face a pale cream panel with the
        # heading in dark blue letters; E reads the whole of it
        # (round 40, rule 06 #107a: a sign faces its readers — 'face_n' turns it round, its face to the north)
        fs_ = -1.0 if o.get('face_n') else 1.0
        things.cone(Matrix.Translation(c + Vector((0, 0, 1.0))), 6, 0.05, 0.05, 2.0, M_IRON)
        things.box(c + Vector((0, -0.06 * fs_, 1.8)), (1, 0), (0, 1), 0.7, 0.03, 0.35, M_SIGNBOARD)
        things.box(c + Vector((0, -0.093 * fs_, 1.8)), (1, 0), (0, 1), 0.62, 0.004, 0.27, M_SIGNFACE)
        things.box(c + Vector((0, -0.06 * fs_, 2.19)), (1, 0), (0, 1), 0.08, 0.03, 0.04, M_SIGNBOARD)     # (a little crest on top)
        lines = sign_heading(o.get('text', ''))
        size = min(0.13, 1.1 / max(6, max(len(l) for l in lines)) * 1.6)
        for j, ln in enumerate(lines):
            zt = 1.8 + (len(lines) - 1) * size * 0.62 - j * size * 1.25
            city_objs.append(text_obj(ln, size, M_SIGNINK, c + Vector((0, -0.1 * fs_, zt)), 0.0 if fs_ > 0 else math.pi,
                                      'SignText_%d_%d_%d' % (X, Y, j)))
    scene['things2d'].append({'type': typ, 'pos': bl_m(c), 'text': o.get('text', ''), 'id': o.get('id', ''),
                              'h': round(h, 3), 'landmark': o.get('landmark', '')})
    if typ == 'kiosk':
        # (round 35, the everything-visit: a round post in the middle let the camera into the box — all green; its own
        # footprint, which the camera stops at as at a wall)
        kx_, kz_ = bl_m(c)
        scene.setdefault('solids', []).append([[round(kx_ + dx_, 2), round(kz_ + dz_, 2)] for dx_, dz_ in
                                               ((-1.15, -0.95), (1.15, -0.95), (1.15, 0.95), (-1.15, 0.95))])
    elif o.get('solid', True) and typ not in ('mosaic',):
        scene['obstacles'].append({'pos': bl_m(c), 'off': [0, 0], 'r': 0.6 if typ in ('bin', 'sign', 'umbrella') else 1.0})
city_objs.append(things.finish('StreetThings'))
