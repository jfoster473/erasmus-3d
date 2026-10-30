# Facade kit: builds every block of the city from the same reusable, varied parts, so a change to a
# part (a window, a balcony, a cornice, how houses meet) shows up on every building.
# Run from build_assets.py (exec'd there, so it shares its helpers: B, MB, Cards, mat, ...).
#
# Sandra's block (HOME) is described by hand in HOUSES below; every other block gets its houses from
# gen_houses(), which makes up a table of the same kind from the block's own random seed (how many
# houses on each side, their colours, storeys, balconies, shops). build_kit_block() then builds any
# block from such a table, with one of the Meshy buildings set into one side if wanted
# (MESHY_BUILDINGS in build_assets.py): the corner houses either side wrap round to meet its front.
# Blocks outside the walkable streets are built with less detail (KIT_DETAIL = 'far').
#
# A house is described by a small dictionary (see HOUSES below): how many bays and floors,
# its colour, the shutter colour of its windows, what each floor has (iron balconies, one
# long balcony, window boxes or none), a glazed tribuna, and what is on the ground floor
# (shops with their sign and awning, a front door, a garage, the passage to the garden).
# Plants, blinds, striped awnings, washing and flags are scattered by each house's own
# random seed, so the same parts never repeat in quite the same way.
#
# Parts:
#   window      Meshy French window with shutters (window.glb), in four shutter colours,
#               each with a lit version whose glass glows at night (KitWindowLit*)
#   balcony     stone slab on corbels with a wrought-iron railing: single or full-width
#   tribuna     a glazed modernista bay window
#   flower box  for floors without balconies
#   plants      red / pink geraniums, daisies, herbs, trailing ivy, bougainvillea, lemon tree, none
#   awnings     striped fabric over balconies and shop windows (several colourways)
#   shopfront   frame, glass, door, sign; extras outside per trade (crates, buckets, terraces)
#   rear        courtyard facades with galleries, plain windows and washing lines
#   garden      the interior of the block: lawns, paths, a fountain, trees, benches, lamps

import numpy as np

KIT_SEED = 2026
WIN_W = 1.25                     # window module width (m)
WIN_DEPTH = 0.36                 # the Meshy window is deep; it's pressed flatter against the wall

# ------------------------------------------------------------------ the houses of Sandra's block
# Edges of the block octagon: 0 north (Carrer de Mallorca), 1 NE corner, 2 east (Carrer de Girona),
# 3 SE corner, 4 south (Flor de Lliri: Sandra's Meshy building), 5 SW corner, 6 west (La Rambla), 7 NW corner.
HOUSES = {
    0: [dict(bays=3, uppers=5, facade='#efd9b4', style='classic', shutter=1, num=12,
             balc=['long', 'iron', 'iron', 'iron', 'box'], ground=['shop', 'shop', 'portal'],
             shop=dict(name='LLIBRERIA PONÇ', frame='#2f4f3f', awning=None, kind='books'),
             plants=['geranium', 'pink', 'herbs', 'ivy', 'none', 'none'], seed=1),
        dict(bays=2, uppers=4, facade='#d99a7a', style='simple', shutter=0, num=14,
             balc=['iron', 'iron', 'box', 'none'], ground=['portal', 'garage'],
             plants=['geranium', 'boug', 'none', 'daisy'], seed=2)],
    1: [dict(bays=3, uppers=5, facade='#e6b47c', style='modernista', shutter=2, num=1, tribuna=[(1, 0), (1, 1)],
             balc=['iron', 'iron', 'iron', 'iron', 'box'], ground=['shop', 'shop', 'shop'],
             shop=dict(name='BAR XAMFRÀ', frame='#7a3a2a', awning=('#b8423a', '#f2e6cf'), kind='bar'),
             plants=['geranium', 'lemon', 'pink', 'none'], seed=3)],
    2: [dict(bays=2, uppers=4, facade='#bfc9cf', style='classic', shutter=3, num=3,
             balc=['iron', 'iron', 'iron', 'box'], ground=['shop', 'shop'],
             shop=dict(name='PAPERERIA', frame='#2f5a7a', awning=('#3a5a8a', '#efe6d2'), kind='books'),
             plants=['herbs', 'geranium', 'none', 'ivy'], seed=4),
        dict(bays=3, uppers=5, facade='#f0e2c8', style='classic', shutter=1, num=5,
             balc=['long', 'iron', 'iron', 'iron', 'iron'], ground=['shop', 'passage', 'portal'],
             shop=dict(name='FLORISTERIA', frame='#5a7a3a', awning=('#6e8f4a', '#f2ead8'), kind='flowers'),
             plants=['boug', 'geranium', 'pink', 'daisy', 'none'], seed=5)],
    3: [dict(bays=3, uppers=4, facade='#e9c99a', style='classic', shutter=0, num=2,
             balc=['long', 'iron', 'iron', 'box'], ground=['shop', 'shop', 'shop'],
             shop=dict(name='FARMÀCIA', frame='#2f6b5a', awning=None, kind='pharmacy'),
             plants=['geranium', 'none', 'herbs', 'pink'], seed=6)],
    5: [dict(bays=3, uppers=4, facade='#c9a3a0', style='modernista', shutter=2, num=1, tribuna=[(1, 0), (1, 1), (1, 2)],
             balc=['iron', 'iron', 'iron', 'iron', 'box'], ground=['shop', 'shop', 'shop'],
             shop=dict(name='GELATERIA', frame='#c46a8a', awning=('#e58fb0', '#fff3ea'), kind='ice'),
             plants=['pink', 'daisy', 'geranium', 'boug'], seed=7)],
    6: [dict(bays=3, uppers=5, facade='#e7bfa2', style='modernista', shutter=1, num=21, tribuna=[(1, 0)],
             balc=['iron', 'long', 'iron', 'iron', 'box'], ground=['shop', 'portal', 'shop'],
             shop=dict(name='FERRETERIA', frame='#6b4a33', awning=('#c9a24a', '#f5ecd6'), kind='hardware'),
             plants=['geranium', 'herbs', 'ivy', 'none', 'lemon'], seed=8),
        dict(bays=2, uppers=4, facade='#d8c2a0', style='simple', shutter=3, num=23,
             balc=['iron', 'iron', 'iron', 'box'], ground=['shop', 'shop'],
             shop=dict(name='FORN DE PA', frame='#8a5d3b', awning=('#b8423a', '#f5e9d3'), kind='bakery'),
             plants=['geranium', 'geranium', 'pink', 'none'], seed=9)],
    7: [dict(bays=3, uppers=4, facade='#e6c08a', style='classic', shutter=0, num=19,
             balc=['long', 'long', 'iron', 'box'], ground=['shop', 'shop', 'shop'],
             shop=dict(name='FRUITERIA', frame='#3e6b4a', awning=('#3e7a4a', '#f2ead8'), kind='fruit'),
             plants=['geranium', 'herbs', 'daisy', 'none'], seed=10)],
}

# ------------------------------------------------------------------ made-up houses for the other blocks

FACADE_POOL = ['#efd9b4', '#d99a7a', '#e6b47c', '#bfc9cf', '#f0e2c8', '#e9c99a', '#c9a3a0', '#e7bfa2', '#d8c2a0',
               '#e6c08a', '#e8c9a8', '#d4a383', '#c7b59a', '#e3b8a0', '#f2dcc0', '#d9b48f', '#b9c4b0', '#e2c4b4',
               '#cdb08c', '#f0d6a8']
TRIMS = ['#d9ccb2', '#cfc2a8', '#e2d6bf', '#c9b79a']
SHOP_TRADES = [('bakery', ['FORN DE PA', 'FORN', 'PASTISSERIA']), ('bar', ['BAR', 'CAFÈ', 'GRANJA', 'BODEGA']),
               ('books', ['LLIBRERIA']), ('flowers', ['FLORISTERIA']), ('fruit', ['FRUITERIA', 'QUEVIURES']),
               ('pharmacy', ['FARMÀCIA']), ('hardware', ['FERRETERIA', 'DROGUERIA']), ('ice', ['GELATERIA', 'ORXATERIA']),
               ('clothes', ['MODA', 'BOTIGA', 'MERCERIA']), ('shoes', ['SABATERIA']), ('deli', ['XARCUTERIA', 'FORMATGERIA', 'CELLER']),
               ('optics', ['ÒPTICA']), ('hair', ['PERRUQUERIA']), ('bar', ['CAFÈ', 'BAR'])]
OWNERS = ['MARTÍ', 'PUIG', 'ROCA', 'VIDAL', 'SOLER', 'FONT', 'COLL', 'PRAT', 'MAS', 'SERRA', 'FERRER', 'BOSCH',
          'CASALS', 'RIBAS', 'VILA', 'CLOS', 'SALA']
FRAMES = ['#2f4f3f', '#7a3a2a', '#2f5a7a', '#5a7a3a', '#2f6b5a', '#c46a8a', '#6b4a33', '#8a5d3b', '#3e6b4a',
          '#3a3a5a', '#7a2a3a', '#1f3a4a', '#a0522d']
AWNING_PAIRS = [('#b8423a', '#f2e6cf'), ('#3a5a8a', '#efe6d2'), ('#6e8f4a', '#f2ead8'), ('#e58fb0', '#fff3ea'),
                ('#c9a24a', '#f5ecd6'), ('#3e7a4a', '#f2ead8'), ('#2f6b5a', '#efe6d2'), ('#d9853b', '#f5ecd6'), None, None]


def gen_house(rng, bays, corner, num):
    """One made-up house, described like the ones in HOUSES."""
    style = rng.choice(['classic', 'classic', 'simple', 'simple', 'modernista'])
    uppers = rng.choice([4, 5, 5]) if corner else rng.choice([3, 4, 4, 4, 5])
    balc = []
    for f in range(uppers):
        if f == 0:
            k = rng.choice(['long', 'iron', 'iron']) if style != 'simple' else rng.choice(['iron', 'iron', 'box'])
        elif f == uppers - 1:
            k = rng.choice(['box', 'iron', 'none', 'box'])
        else:
            k = rng.choice(['iron'] * 5 + ['box', 'long', 'none'] if style != 'simple' else ['iron', 'iron', 'box', 'box', 'none'])
        balc.append(k)
    if corner:
        ground = rng.choice([['shop'] * 3, ['shop', 'portal', 'shop']])
    elif bays == 1:
        ground = ['portal'] if rng.random() < 0.6 else ['shop']
    else:
        door = rng.randrange(bays)
        ground = ['portal' if b == door else rng.choice(['shop', 'shop', 'shop', 'window', 'garage']) for b in range(bays)]
    shop = None
    if 'shop' in ground:
        trade, names = rng.choice(SHOP_TRADES)
        name = rng.choice(names)
        if rng.random() < 0.55:
            name += ' ' + rng.choice(OWNERS)
        shop = dict(name=name, frame=rng.choice(FRAMES), awning=rng.choice(AWNING_PAIRS), kind=trade,
                    wares=rng.random() < 0.55, closed=trade != 'bar' and rng.random() < 0.15)
    tribuna = []
    if style == 'modernista' and bays >= 3 and rng.random() < 0.6:
        tribuna = [(bays // 2, f) for f in range(rng.randint(1, 2))]
        for (_, f) in tribuna:
            balc[f] = 'iron'                             # a tribuna and a long balcony can't share a floor
    plants = rng.sample(['geranium', 'pink', 'herbs', 'ivy', 'daisy', 'boug', 'lemon', 'none', 'none', 'none'], 5)
    return dict(bays=bays, uppers=uppers, facade=rng.choice(FACADE_POOL), style=style, shutter=rng.randrange(4),
                num=num, balc=balc, ground=ground, shop=shop, plants=plants, seed=rng.randrange(1, 100000),
                tribuna=tribuna, trim=rng.choice(TRIMS))


# ------------------------------------------------------------------ hand-set houses on made-up blocks (round 23)
# Jordi's bike shop, BICIS JORDI (the user: "the shop with the awning on the north side of Carrer de València, between
# Passeig de Gràcia and La Rambla… in the style of the awning shops on the east side of Roger de Llúria", i.e. Sandra's
# block's west side, HOUSES[6]). It takes the places of the made-up SABATERIA FERRER and the one-bay house beside it.
JORDI_HOUSE = dict(HOUSES[6][0], num=31, seed=31,
                   shop=dict(name='BICIS JORDI', frame='#2f5a7a', awning=('#3a5a8a', '#efe6d2'), kind='bikes', wares=True))
HOUSE_OVERRIDES = {(-30, 0): {4: lambda hs: [hs[0], JORDI_HOUSE]}}


def override_houses(ox, oy, houses):
    for edge, fn in HOUSE_OVERRIDES.get((ox, oy), {}).items():
        if edge in houses:
            houses[edge] = fn(houses[edge])
    return houses


def gen_houses(ox, oy, skip=()):
    """A HOUSES-style table for block (ox, oy): two or three houses along each straight side, one
    three-bay corner house on each chamfer. Sides in skip are left out (a Meshy building stands there)."""
    rng = random.Random(9000 + ox * 131 + oy * 17)
    houses = {}
    num = 1 + 2 * rng.randrange(20)
    for i in range(8):
        if i in skip:
            continue
        parts = [3] if i % 2 else rng.choice([[3, 2], [2, 3], [2, 1, 2], [1, 2, 2], [2, 2, 1], [5], [3, 2], [2, 3]])
        houses[i] = []
        for bays in parts:
            houses[i].append(gen_house(rng, bays, i % 2 == 1, num))
            num += 2
    return houses


# ------------------------------------------------------------------ textures and materials

KIT_IMG = {}


def kit_image(name, w, h, fn):
    if name not in KIT_IMG:
        KIT_IMG[name] = make_image(name, w, h, fn)
    return KIT_IMG[name]


F = 2 * math.pi / 128


def stucco_mat(col):
    r, g, b = rgb(col)
    rr = random.Random(col)

    def fn(x, y):
        v = (1.0 + 0.03 * math.sin(x * F * 3 + 2.0 * math.sin(y * F * 2)) + 0.022 * math.sin(y * F * 5 + x * F)
             + rr.uniform(-0.028, 0.028))
        v *= 1.0 - 0.05 * max(0.0, math.sin(x * F * 7 + y * F * 1)) ** 8        # faint rain streaks
        return (r * v, g * v, b * v)
    return mat('Stucco' + hexof(col), '#ffffff', 0.93, image=kit_image('stucco' + hexof(col), 128, 128, fn))


def rustic_mat(col):
    """Ground-floor stonework: courses 0.4 m high with staggered joints (texture = 1.2 m)."""
    r, g, b = rgb(col)
    rr = random.Random(col + 'r')

    def fn(x, y):
        v = 1.0 + rr.uniform(-0.035, 0.035)
        row = y // 40
        if y % 40 < 3:
            v *= 0.7
        elif (x + (30 if row % 2 else 0)) % 60 < 2:
            v *= 0.78
        elif y % 40 < 6:
            v *= 1.06                                  # light catching the top of each course
        return (r * v, g * v, b * v)
    return mat('Rustic' + hexof(col), '#ffffff', 0.9, image=kit_image('rustic' + hexof(col), 120, 120, fn))


def stripes_mat(a, b):
    ca, cb = rgb(a), rgb(b)
    return mat('Stripes' + hexof(a) + hexof(b), '#ffffff', 0.85,
               image=kit_image('stripes' + hexof(a) + hexof(b), 64, 8, lambda x, y: ca if (x // 8) % 2 == 0 else cb))


def shade(col, k):
    r, g, b = rgb(col)
    return '#%02x%02x%02x' % tuple(min(255, int(v * k * 255)) for v in (r, g, b))


M_SENYERA = mat('Senyera', '#ffffff', 0.8, image=kit_image('senyera', 8, 18,
                lambda x, y: rgb('#d8342f') if (y // 2) % 2 == 1 and 1 < y < 17 else rgb('#f2c84b')))
M_SLATS = mat('BlindSlats', '#ffffff', 0.8, image=kit_image('slats', 16, 64,
              lambda x, y: tuple(v * (0.8 if y % 6 == 0 else 1.0) for v in rgb('#5d7f58'))))
M_SHUTTER_DOOR = mat('RollerShutter', '#ffffff', 0.6, 0.3, image=kit_image('roller', 16, 64,
                     lambda x, y: tuple(v * (0.75 if y % 5 == 0 else 1.0) for v in rgb('#9aa0a2'))))
def lawn_pixels(N=512, seed=35):
    """(round 35, the user: "The grass is zigzaggy… It should be a texture that does not appear to evidently repeat
    anything within it. So random, but matching the borders") gradient noise at six sizes that wraps round the tile
    (its edges meet), gently swirled by more of it so nothing lines up; lighter patches a touch yellower, darker a
    touch bluer; the same mean colour as the old lawn. An N x N array of (r, g, b)."""
    import numpy as np
    rng = np.random.default_rng(seed)

    def perlin(n_cells):
        ang = rng.uniform(0, 2 * np.pi, (n_cells, n_cells))
        gx, gy = np.cos(ang), np.sin(ang)

        def f(px, py):
            x, y = (px % 1.0) * n_cells, (py % 1.0) * n_cells
            x0, y0 = np.floor(x).astype(int) % n_cells, np.floor(y).astype(int) % n_cells
            fx, fy = x - np.floor(x), y - np.floor(y)
            x1, y1 = (x0 + 1) % n_cells, (y0 + 1) % n_cells
            u = fx ** 3 * (fx * (fx * 6 - 15) + 10)
            v = fy ** 3 * (fy * (fy * 6 - 15) + 10)
            a_ = (gx[y0, x0] * fx + gy[y0, x0] * fy) * (1 - u) + (gx[y0, x1] * (fx - 1) + gy[y0, x1] * fy) * u
            b_ = (gx[y1, x0] * fx + gy[y1, x0] * (fy - 1)) * (1 - u) + (gx[y1, x1] * (fx - 1) + gy[y1, x1] * (fy - 1)) * u
            return (a_ * (1 - v) + b_ * v) / 0.5
        return f
    t = np.arange(N) / N
    PX, PY = np.meshgrid(t, t)
    wx, wy = perlin(4), perlin(4)
    SX = PX + 0.035 * wx(PX, PY)
    SY = PY + 0.035 * wy(PX + 0.37, PY + 0.61)
    k = np.zeros((N, N))
    for cells, amp in ((4, 0.035), (8, 0.04), (16, 0.035), (32, 0.03), (64, 0.03), (128, 0.025)):
        k += amp * perlin(cells)(SX, SY)
    k += rng.uniform(-0.03, 0.03, (N, N))
    k = 1 + k - k.mean()
    hue = 0.04 * perlin(6)(SX, SY)
    return np.stack([0.34 * k * (1 + hue), 0.5 * k, 0.22 * k * (1 - hue)], -1)


_LAWN = lawn_pixels()


def lawn(x, y):
    return tuple(_LAWN[y % 512, x % 512])


M_GRASS = mat('Lawn', '#ffffff', 0.95, image=kit_image('lawn', 512, 512, lawn))
M_GRAVEL = mat('Gravel', '#ffffff', 0.97, image=kit_image('gravel', 128, 128, lambda x, y: tuple(
    v * (1 + random.Random(x * 997 + y * 7).uniform(-0.09, 0.09)) for v in rgb('#d9c7a3'))))
M_WATER = mat('FountainWater', '#6f9fa8', 0.05, 0.1)
M_WOODFRAME = {}
M_FRAME_TRIB = mat('TribunaFrame', '#efe6d2', 0.6)
M_SIGN_TEXT = mat('SignText', '#f6e7c1', 0.4, 0.3)
M_CROSS = mat('PharmacyCross', '#2fbf5a', 0.4)               # glows (main.gd)
M_WHITE_TRIM = mat('PharmacyTrim', '#f4f2ea', 0.5)
M_AC = mat('AirCon', '#dcdcd6', 0.5)
M_TERRACOTTA = mat('Terracotta', '#b9663e', 0.9)
M_CLOTH = [mat('Cloth%d' % i, c, 0.95) for i, c in enumerate(['#f4f0e8', '#8fb3d9', '#e8a0a8', '#f2d27a', '#7fb58a', '#d95f4a'])]
M_FRUIT = [mat('Fruit%d' % i, c, 0.6) for i, c in enumerate(['#f29a2e', '#d8322f', '#f3d24a', '#7fb03a', '#7a3a6a'])]
M_CRATE = mat('Crate', '#c79a5e', 0.85)
M_TOOLBOX = mat('Toolbox', '#b8423a', 0.5)
M_BUCKET = mat('Bucket', '#8a9aa6', 0.4, 0.6)
M_BINS = [mat('Bin%d' % i, c, 0.6) for i, c in enumerate(['#3f7a3f', '#e5c33a', '#3a6aa8', '#6b6b6b', '#8a5a3a'])]

GREENS_FOL = ['#4a7a34', '#5a8a3a', '#3e6c2e']
IMG_PINK = foliage_image('geranium_pink', 128, [(70, GREENS_FOL, 6, 9, 0.95, 0),
                                                (150, ['#e86a9a', '#f28ab0', '#d94f86', '#f7a1c0'], 2.5, 4, 1.0, 0)], 21)
IMG_DAISY = foliage_image('daisies', 128, [(70, GREENS_FOL, 5, 8, 0.6, 0),
                                           (110, ['#f7f4ea', '#ffffff', '#efe9d6'], 2.5, 3.5, 1.0, 5),
                                           (50, ['#f2c84b'], 0.9, 1.3, 1.0, 0)], 22)
IMG_IVY = foliage_image('ivy', 128, [(230, ['#2f5a2a', '#3c6b33', '#4a7a3a', '#2a4f26'], 4, 7, 0.8, 3)], 23)
IMG_CITRUS = foliage_image('citrus', 256, [(320, ['#2f5a2a', '#3b6a30', '#467a36'], 7, 11, 0.5, 0),
                                           (32, ['#f29a2e', '#f5b13a'], 4, 5.5, 1.0, 0)], 24)
M_PINK = mat('LeavesPinkGeranium', '#ffffff', 0.8, image=IMG_PINK, alpha=True)
M_DAISY = mat('LeavesDaisy', '#ffffff', 0.8, image=IMG_DAISY, alpha=True)
M_IVY = mat('LeavesIvy', '#ffffff', 0.8, image=IMG_IVY, alpha=True)
M_CITRUS = mat('LeavesCitrus', '#ffffff', 0.8, image=IMG_CITRUS, alpha=True)
PLANT_MAT = {'geranium': M_GERANIUM_CARD, 'pink': M_PINK, 'daisy': M_DAISY, 'herbs': M_SHRUB}


def frame_mat(col):
    if col not in M_WOODFRAME:
        M_WOODFRAME[col] = mat('ShopFrame' + hexof(col), col, 0.55)
    return M_WOODFRAME[col]


def _tube(self, a, b, r, m, segs=6):
    a, b = Vector(a), Vector(b)
    d = b - a
    if d.length < 1e-5:
        return
    M = Matrix.Translation((a + b) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    vs = self.stamp(bmesh.ops.create_cone, M, cap_ends=False, cap_tris=False, segments=segs, radius1=r, radius2=r,
                    depth=d.length, calc_uvs=self.uv is not None)         # (round 26: stamped, see MB.stamp)
    self._tag(vs, m, True)


MB.tube = _tube

# ------------------------------------------------------------------ the Meshy window, in colour variants

SHUTTER_COLS = [None, '#2f5a42', '#55728c', '#7a5236']       # as made (sage), bottle green, slate blue, walnut
KIT_WIN = {}


def recolour(img, target, name, emit=False, alpha=False):
    """Shutters (the green parts of the texture) in a new colour; or, with emit, a glow map of the glass."""
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(-1, 4)
    c = a[:, :3]
    mx, mn = c.max(1), c.min(1)
    d = mx - mn + 1e-6
    r, g, b = c[:, 0], c[:, 1], c[:, 2]
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    sat = d / (mx + 1e-6)
    lum = c @ np.array([0.3, 0.59, 0.11], dtype=np.float32)
    if emit:
        k = np.clip((0.24 - mx) / 0.1, 0, 1)[:, None]               # the dark glass panes
        out = np.zeros_like(a)
        out[:, :3] = k * np.array(rgb('#ffcf8a'), dtype=np.float32)
        out[:, 3] = 1
    else:
        mask = (hue > 62) & (hue < 175) & (sat > 0.1) & (mx > 0.1)
        ref = np.median(lum[mask]) if mask.any() else 0.5
        t = np.array(rgb(target), dtype=np.float32)
        tl = float(t @ np.array([0.3, 0.59, 0.11], dtype=np.float32))
        new = np.clip(t[None, :] * (lum / ref)[:, None] * (tl / max(tl, 1e-3)), 0, 1)
        c[mask] = new[mask]
        out = a
    im2 = bpy.data.images.new(name, w, h, alpha=alpha)
    im2.pixels.foreach_set(out.ravel())
    im2.file_format = 'PNG'
    im2.pack()
    return im2


# Round 25: the window style. 'meshy': the Meshy window as a model (the look of rounds 17-23; WIN_TRIS triangles, its
# picture WIN_TEX pixels square); 'picture': the same Meshy window photographed straight on (window_picture) and laid on
# the wall as one flat picture with a relief map, all of a block's in one object (the lightest to draw); 'crisp':
# round 24's modelled windows (crisp_window; the user preferred the old look: DECISIONS.md, round 25).
WIN_STYLE = os.environ.get('WIN_STYLE', 'picture')        # (round 25: the user's pick, 4 of round25/windows_close.png)
WIN_TRIS = int(os.environ.get('WIN_TRIS', '1600'))
WIN_TEX = int(os.environ.get('WIN_TEX', '1024'))
WIN_PIC_W = 1024                 # the picture window's width in pixels (its height follows the model's shape)
CRISP_ALL = WIN_STYLE == 'crisp'
WINPIC = None                    # (the block's picture windows, while it is built)
CRISP_BLOCKS = set()           # (round 23's trial block of modelled windows, (-13, 0), is gone with them)
CRISP = False
WOOD_COLS = ['#c47a35', '#b56b2e', '#cf8a45', '#a9622c']       # the warm varnished doors of the old Meshy window


def slat_mat(col, kind):
    """(round 24) a roller blind's slats ('blind', every 6 cm) or a louvred shutter's slats ('louvre', every 11 cm, each
    with a shadow under it), as a picture on one flat piece instead of dozens of little boxes: 1 m to the picture."""
    c = rgb(col)
    if kind == 'blind':
        fn = lambda x, y: tuple(v * (0.72 if y % 4 == 0 else (1.04 if y % 4 == 1 else 1.0)) for v in c)
        return mat('Blind' + hexof(col), '#ffffff', 0.75, image=kit_image('blind' + hexof(col), 16, 64, fn))
    fn = lambda x, y: tuple(v * (0.62 if y % 7 == 0 else (0.82 if y % 7 == 1 else (1.08 if y % 7 == 6 else 1.0))) for v in c)
    return mat('Louvre' + hexof(col), '#ffffff', 0.75, image=kit_image('louvre' + hexof(col), 16, 64, fn))


def crisp_window(mb, F_, s, z, variant, lit, rng, fine_mb=None, warm=True, lo=False):
    """An Eixample balcony door, modelled rather than textured, so it stays sharp close to: a stone
    surround (jambs, lintel, cornice, keystone, little consoles), a pair of glazed doors, and either the
    wooden roller blind (persiana) let down part of the way, its rolled top in a box under the lintel, or
    the folding louvred shutters (mallorquines) opened back against the wall either side.
    warm (round 24, everywhere): varnished wooden doors and coloured shutters like the old Meshy window;
    otherwise the first trial's pale frames. lo: the few big parts only, for blocks seen from afar.
    The big parts go in `mb` (the blind's and the shutters' slats a picture on them: slat_mat); glazing bars, panels
    and handles in `fine_mb` (drawn only nearer)."""
    sh = SHUTTER_COLS[variant] or '#7f9e78'
    shutter = mat('CrispShutter%d' % variant, sh, 0.7)
    shutter_d = mat('CrispShutterDark%d' % variant, '#%02x%02x%02x' % tuple(round(c * 0.72 * 255) for c in rgb(sh)), 0.75)
    wood_c = WOOD_COLS[variant % len(WOOD_COLS)] if warm else '#f1ece2'
    frame = mat('CrispWood%s' % wood_c[1:] if warm else 'CrispFrame', wood_c, 0.5)
    glass = mat('CrispGlassLit' if lit else 'CrispGlass', '#f3c98a' if lit else '#2f3d4a', 0.12)
    reveal = mat('CrispReveal', '#5a4a3c', 0.9)
    fine_ = fine_mb or fine() or mb
    if warm:      # its own dice, from where it is, so the street's other choices (plants, awnings) stay as they were
        P_ = F_.at(s, 0, z)
        rng = random.Random(round(P_.x * 100) * 92821 + round(P_.y * 100) * 68917 + round(z * 10))
    W2_, Hh = 0.54, 2.25                                         # half the opening's width; its height
    z0 = z + 0.16
    zt = z0 + Hh
    # the stone surround
    for side in (-1, 1):
        F_.box(mb, s + side * (W2_ + 0.08), 0.05, z0 + Hh / 2, 0.08, 0.05, Hh / 2 + 0.04, M_STONE)
    F_.box(mb, s, 0.06, zt + 0.12, W2_ + 0.2, 0.06, 0.1, M_STONE)                       # the lintel
    F_.box(mb, s, 0.11, zt + 0.26, W2_ + 0.28, 0.11, 0.035, M_STONE)                    # its cornice
    F_.box(mb, s, 0.09, zt + 0.12, 0.1, 0.09, 0.13, M_STONE)                            # the keystone
    if lo:
        F_.box(mb, s, 0.01, z0 + Hh / 2, W2_, 0.01, Hh / 2, glass if lit else reveal)
        F_.box(mb, s, 0.06, zt - 0.3, W2_, 0.05, 0.3, shutter)
        return
    F_.box(mb, s, 0.005, z0 + Hh / 2, W2_, 0.005, Hh / 2, reveal)                        # the opening's shadow
    for side in (-1, 1):                                                                 # consoles under the cornice
        F_.box(mb, s + side * (W2_ + 0.2), 0.09, zt + 0.17, 0.05, 0.08, 0.07, M_STONE)
    # the doors: two leaves, each a wooden frame with two tall panes over a wooden panel
    for side in (-1, 1):
        cx = s + side * W2_ / 2
        F_.box(mb, cx, 0.022, z0 + Hh / 2, W2_ / 2 - 0.01, 0.012, Hh / 2 - 0.01, frame)
        pz0, pz1 = z0 + 0.62, zt - 0.08
        F_.box(mb, cx, 0.036, (pz0 + pz1) / 2, W2_ / 2 - 0.08, 0.004, (pz1 - pz0) / 2, glass)
        F_.box(fine_, cx, 0.04, z0 + 0.33, W2_ / 2 - 0.1, 0.012, 0.2, frame)              # the raised panel
        F_.box(fine_, cx, 0.042, (pz0 + pz1) / 2, 0.015, 0.006, (pz1 - pz0) / 2, frame)    # glazing bars
        for zz in (pz0 + (pz1 - pz0) * k for k in (0.34, 0.67)):
            F_.box(fine_, cx, 0.042, zz, W2_ / 2 - 0.08, 0.006, 0.013, frame)
        F_.box(fine_, cx + side * -0.06, 0.06, z0 + 1.0, 0.012, 0.012, 0.07, M_BRASS)     # the handles
    if rng.random() < 0.5:
        # the roller blind: some of the way down (never right down: the doors are the point), slats as lines
        down = rng.choice((0.12, 0.2, 0.3, 0.4, 0.55))
        bottom = zt - 0.08 - (Hh - 0.1) * down
        F_.box(mb, s, 0.1, zt - 0.04, W2_ + 0.02, 0.06, 0.1, shutter_d)                 # the box it rolls into
        F_.box(mb, s, 0.07, (bottom + zt - 0.14) / 2, W2_ - 0.01, 0.012, (zt - 0.14 - bottom) / 2, slat_mat(sh, 'blind'))
        F_.box(fine_, s, 0.088, bottom + 0.02, W2_ - 0.01, 0.015, 0.02, shutter_d)       # its bottom rail
        if rng.random() < 0.5:                                                           # pushed out on its arms
            F_.box(fine_, s, 0.2, bottom - 0.01, W2_ - 0.01, 0.12, 0.012, shutter_d)
    else:
        # the louvred shutters, folded back against the wall either side (one leaf a little ajar now and then)
        for side in (-1, 1):
            lc = s + side * (W2_ + 0.32)
            ajar = 0.06 if rng.random() < 0.3 else 0.0
            F_.box(mb, lc, 0.03 + ajar, z0 + Hh / 2, 0.15, 0.015, Hh / 2 - 0.02, slat_mat(sh, 'louvre'))


def window_mesh(variant, lit, lo=False):
    """The Meshy window in one of the shutter colours, lit or not; lo: a much lighter copy for windows
    further away (the game shows it beyond about 40 m), sharing the same material."""
    key = (variant, lit, lo)
    if key in KIT_WIN:
        return KIT_WIN[key]
    if lo:
        hi = window_mesh(variant, lit)
        me = meshy_mesh('window.glb', max(260, WIN_TRIS // 6), 'back', WIN_TEX).copy()
        me.name = 'KitWindowLo%d%s' % (variant, 'Lit' if lit else '')
        me.materials[0] = hi.materials[0]
        KIT_WIN[key] = me
        return me
    base = meshy_mesh('window.glb', WIN_TRIS, 'back', WIN_TEX)
    me = base.copy()
    me.name = 'KitWindow%d%s' % (variant, 'Lit' if lit else '')
    m = base.materials[0].copy()
    m.name = 'KitWindow%s%d' % ('Lit' if lit else '', variant)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    albedo = next(l.from_node for l in nt.links if l.to_node == bsdf and l.to_socket.name == 'Base Color')
    if SHUTTER_COLS[variant]:
        albedo.image = recolour(albedo.image, SHUTTER_COLS[variant], 'kitwin_%d' % variant)
    if lit:
        src = KIT_WIN.get(('glow',))
        if src is None:
            src = recolour(base_albedo_image(base), None, 'kitwin_glow', emit=True)
            src.scale(512, 512)
            KIT_WIN[('glow',)] = src
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = src
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 1.0
    me.materials[0] = m
    KIT_WIN[key] = me
    return me


def base_albedo_image(me):
    nt = me.materials[0].node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    return next(l.from_node for l in nt.links if l.to_node == bsdf and l.to_socket.name == 'Base Color').image


def window_picture():
    """(round 25) The Meshy window photographed straight on: rays from in front onto the whole, unslimmed model give, for
    each pixel, its colour (from the model's own picture) and which way the surface faces there (a relief map, so the
    game's light still catches the mouldings). Kept in bigfiles/built/props/ once made (remade if WIN_PIC_W changes). Returns
    (colour image with the see-through parts clear, relief image, height over width)."""
    if 'pic' in KIT_WIN:
        return KIT_WIN['pic']
    cdir = PROPS
    cpath, npath = os.path.join(cdir, 'window_picture.png'), os.path.join(cdir, 'window_picture_relief.png')
    if os.path.exists(cpath) and os.path.exists(npath):
        ci, ni = bpy.data.images.load(cpath), bpy.data.images.load(npath)
        if ci.size[0] == WIN_PIC_W:
            ni.colorspace_settings.name = 'Non-Color'
            ci.pack(); ni.pack()
            KIT_WIN['pic'] = (ci, ni, ci.size[1] / ci.size[0])
            return KIT_WIN['pic']
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    base = meshy_mesh('window.glb', 10 ** 9, 'back', 0)
    bm = bmesh.new()
    bm.from_mesh(base)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.faces.ensure_lookup_table()
    uvl = bm.loops.layers.uv.active
    tree = BVHTree.FromBMesh(bm)
    xs = [v.co.x for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    y0 = min(v.co.y for v in bm.verts) - 1.0
    x0, x1, z1 = min(xs), max(xs), max(zs)
    W = WIN_PIC_W
    H = int(round(W * z1 / (x1 - x0)))
    src = base_albedo_image(base)
    aw, ah = src.size
    alb = np.empty(aw * ah * 4, dtype=np.float32)
    src.pixels.foreach_get(alb)
    alb = alb.reshape(ah, aw, 4)
    col = np.zeros((H, W, 4), dtype=np.float32)
    nrm = np.zeros((H, W, 4), dtype=np.float32)
    nrm[:, :] = (0.5, 0.5, 1.0, 1.0)
    idx, uvs = [], []
    ray = Vector((0, 1, 0))
    for j in range(H):
        z = (j + 0.5) / H * z1
        for i in range(W):
            loc, _n, fi, _d = tree.ray_cast(Vector((x0 + (i + 0.5) / W * (x1 - x0), y0, z)), ray)
            if loc is None:
                continue
            L = bm.faces[fi].loops
            a, b, c = L[0], L[1], L[2]
            uv = barycentric_transform(loc, a.vert.co, b.vert.co, c.vert.co,
                                       a[uvl].uv.to_3d(), b[uvl].uv.to_3d(), c[uvl].uv.to_3d())
            n = barycentric_transform(loc, a.vert.co, b.vert.co, c.vert.co, a.vert.normal, b.vert.normal, c.vert.normal)
            n.normalize()
            if n.y > -0.05:                     # (facing away: as if square on)
                n = Vector((n.x, -0.05, n.z)).normalized()
            idx.append((j, i))
            uvs.append((uv.x, uv.y))
            nrm[j, i, :3] = (n.x * 0.5 + 0.5, n.z * 0.5 + 0.5, -n.y * 0.5 + 0.5)
    bm.free()
    idx = np.array(idx)
    uvs = np.array(uvs, dtype=np.float32) % 1.0
    # bilinear from the model's picture
    fx, fy = uvs[:, 0] * aw - 0.5, uvs[:, 1] * ah - 0.5
    ix, iy = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = (fx - ix)[:, None], (fy - iy)[:, None]
    g = lambda yy, xx: alb[np.clip(yy, 0, ah - 1), np.clip(xx, 0, aw - 1), :3]
    rgb_ = (g(iy, ix) * (1 - tx) * (1 - ty) + g(iy, ix + 1) * tx * (1 - ty) + g(iy + 1, ix) * (1 - tx) * ty
            + g(iy + 1, ix + 1) * tx * ty)
    col[idx[:, 0], idx[:, 1], :3] = rgb_
    col[idx[:, 0], idx[:, 1], 3] = 1.0
    # (the clear parts take the colour of the nearest solid pixel, so no dark fringe shows at the cut edge)
    solid = col[:, :, 3] > 0
    for _ in range(4):
        grow = np.zeros_like(solid)
        acc = np.zeros((H, W, 3), dtype=np.float32)
        cnt = np.zeros((H, W), dtype=np.float32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            sh = np.roll(np.roll(solid, dy, 0), dx, 1)
            shc = np.roll(np.roll(col[:, :, :3], dy, 0), dx, 1)
            acc += shc * sh[:, :, None]
            cnt += sh
        grow = (~solid) & (cnt > 0)
        col[grow, :3] = acc[grow] / cnt[grow][:, None]
        solid = solid | grow
    ci = bpy.data.images.new('window_picture', W, H, alpha=True)
    ci.pixels.foreach_set(col.ravel())
    ni = bpy.data.images.new('window_picture_relief', W, H, alpha=False)
    ni.pixels.foreach_set(nrm.ravel())
    os.makedirs(cdir, exist_ok=True)
    for im, pth in ((ci, cpath), (ni, npath)):
        im.filepath_raw = pth
        im.file_format = 'PNG'
        im.save()
        im.pack()
    ni.colorspace_settings.name = 'Non-Color'
    print('WINDOW PICTURE', W, 'x', H, 'from', len(idx), 'hits')
    KIT_WIN['pic'] = (ci, ni, H / W)
    return KIT_WIN['pic']


def window_picture_mat(variant, lit):
    """The picture window's material, in one of the shutter colours, lit or not (lamplight in the dark panes)."""
    key = ('picmat', variant, lit)
    if key in KIT_WIN:
        return KIT_WIN[key]
    ci, ni, _k = window_picture()
    img = recolour(ci, SHUTTER_COLS[variant], 'winpic_%d' % variant, alpha=True) if SHUTTER_COLS[variant] else ci
    m = bpy.data.materials.new('WinPic%s%d' % ('Lit' if lit else '', variant))
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.6
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    rnd = nt.nodes.new('ShaderNodeMath')           # (a sharp cut-out: the export reads "round" as alpha clipping)
    rnd.operation = 'ROUND'
    nt.links.new(tex.outputs['Alpha'], rnd.inputs[0])
    nt.links.new(rnd.outputs[0], bsdf.inputs['Alpha'])
    ntex = nt.nodes.new('ShaderNodeTexImage')
    ntex.image = ni
    nmap = nt.nodes.new('ShaderNodeNormalMap')
    nt.links.new(ntex.outputs['Color'], nmap.inputs['Color'])
    nt.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    if lit:
        src = KIT_WIN.get(('picglow',))
        if src is None:
            src = recolour(ci, None, 'winpic_glow', emit=True)
            src.scale(512, int(512 * ci.size[1] / ci.size[0]))
            KIT_WIN[('picglow',)] = src
        et = nt.nodes.new('ShaderNodeTexImage')
        et.image = src
        nt.links.new(et.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 1.0
    KIT_WIN[key] = m
    return m


def std_window(mb, F_, s, z, variant, lit, rng, far=False, fine_mb=None):
    """(round 25) A balcony window in the city's style (WIN_STYLE): the picture (into the block's WINPIC, or `mb` for a
    landmark's front), the Meshy model (a near and a far copy), or round 24's modelled one."""
    if WIN_STYLE == 'picture':
        picture_window(WINPIC if WINPIC is not None else mb, F_, s, z, variant, lit)
    elif WIN_STYLE == 'crisp':
        crisp_window(mb, F_, s, z, variant, lit, rng, fine_mb=fine_mb, warm=True, lo=far)
    else:
        if not far:
            place_obj(window_mesh(variant, lit), 'WinHi', F_.at(s, 0.01, z + 0.12), F_.rot, (WIN_W, WIN_W * WIN_DEPTH, WIN_W))
        place_obj(window_mesh(variant, lit, True), 'WinLo', F_.at(s, 0.01, z + 0.12), F_.rot, (WIN_W, WIN_W * WIN_DEPTH, WIN_W))


def picture_window(mb, F_, s, z, variant, lit, d=0.03):
    """(round 25) The Meshy window as one flat picture on the wall, where the model would stand."""
    _ci, _ni, k = window_picture()
    m = window_picture_mat(variant, lit)
    # (which way along the wall the picture's left-to-right runs: the model's +x, turned as place_obj turns it)
    ux = Vector((math.cos(F_.rot), math.sin(F_.rot), 0))
    flip = ux.dot(Vector((F_.u[0], F_.u[1], 0))) < 0
    a, b = (s + WIN_W / 2, s - WIN_W / 2) if flip else (s - WIN_W / 2, s + WIN_W / 2)
    z0 = z + 0.12
    z1 = z0 + WIN_W * k
    mb.face([F_.at(a, d, z0), F_.at(b, d, z0), F_.at(b, d, z1), F_.at(a, d, z1)], m,
            normal=tuple(F_.n) + (0,) if len(F_.n) == 2 else F_.n, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])


def place_obj(me, name, loc, rot, scale):
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (0, 0, rot)
    ob.scale = scale
    city_objs.append(ob)
    return ob


# ------------------------------------------------------------------ parts

KIT_DETAIL = 'full'      # 'far': blocks seen only from a distance (no railings' ironwork, plants, washing, signs)
FINE = None              # the mesh small parts go into (railings, plants' pots, awnings, goods): the game
                         # stops drawing it beyond a certain distance


def fine():
    return FINE


# (round 41, rule 02 #5e, the user: "swap the railings on far buildings for a flat picture of them") a balcony's iron
# bars are 1.4 cm thick: past ~15 m each is under a pixel and they break up and flicker. So the bars go into RAILS
# (drawn close to) and a flat picture of the same railing, in its own planes, into RAILCARDS (drawn further off; the
# game cross-fades them). One tile of the picture is 0.48 m wide (four bars, two curls) and the railing's full height.
RAILS = None
RAILCARDS = None
RAIL_TILE = 0.48
RAIL_H = 0.95


def railcard_image():
    W, H = 128, 256
    iron = rgb('#2e2b2a')
    a = [0.0] * (W * H)
    mpx = W / RAIL_TILE                              # pixels a metre across
    mpy = H / (RAIL_H + 0.04)                        # and up (the picture runs from 0.02 below to 0.02 above)

    def ink(x0, x1, y0, y1):
        for y in range(max(0, int(y0)), min(H, int(math.ceil(y1)))):
            for x in range(int(math.floor(x0)), int(math.ceil(x1))):
                cover = max(0.0, min(x1, x + 1) - max(x0, x)) * max(0.0, min(y1, y + 1) - max(y0, y))
                i = y * W + (x % W)
                a[i] = min(1.0, a[i] + cover)

    def zy(z):                                       # metres above the balcony floor → picture row (0 at the bottom)
        return (z + 0.02) * mpy
    # (each line a little bolder than the real iron: seen from afar the real bars still read dark, so the blurred
    # picture is drawn heavier to match them)
    for zz, r in ((RAIL_H, 0.026), (0.13, 0.016)):    # the top and bottom rails
        ink(0, W, zy(zz - r), zy(zz + r))
    for k in range(4):                               # the bars, 0.12 m apart
        cx = (k + 0.5) * W / 4
        ink(cx - 0.011 * mpx, cx + 0.011 * mpx, zy(0.13), zy(RAIL_H))
    for k in range(2):                               # the curls half way up
        cx, cz = (k + 0.5) * W / 2 + W / 8, zy(RAIL_H * 0.56)
        R, t = 0.065 * mpx, 0.009 * mpx * 2
        for y in range(int(cz - R - t), int(cz + R + t) + 1):
            for x in range(int(cx - R - t), int(cx + R + t) + 1):
                d = math.hypot(x + 0.5 - cx, (y + 0.5 - cz) * mpx / mpy)
                if abs(d - R) < t / 2 + 0.5:
                    i = y * W + (x % W)
                    a[i] = min(1.0, max(a[i], 1.0 - max(0.0, abs(d - R) - t / 2)))
    px = [0.0] * (W * H * 4)
    for i in range(W * H):                           # iron colour everywhere, so the blur of the far picture stays iron
        px[i * 4], px[i * 4 + 1], px[i * 4 + 2], px[i * 4 + 3] = iron[0], iron[1], iron[2], a[i]
    img = bpy.data.images.new('railcard', W, H, alpha=True)
    img.pixels.foreach_set(px)
    img.file_format = 'PNG'
    try:
        img.pack()
    except Exception:
        pass
    return img


M_RAILCARD = mat('RailCard', '#ffffff', 0.6, image=railcard_image(), alpha=True)


def rails_begin():
    global RAILS, RAILCARDS
    RAILS, RAILCARDS = MB(uv=True), MB(uv=True)


def rails_finish(tag, objs):
    global RAILS, RAILCARDS
    for mb, name in ((RAILS, 'Rail_'), (RAILCARDS, 'RailCard_')):
        if mb is not None and mb.bm.faces:
            objs.append(mb.finish(name + tag))
        elif mb is not None:
            mb.bm.free()
    RAILS = RAILCARDS = None


def railcard(F_, s0, s1, d0, d1, z, h):
    """The picture of a railing on one side: from (s0, d0) to (s1, d1) along the front, floor z."""
    if RAILCARDS is None:
        return
    p0, p1 = F_.at(s0, d0, z - 0.02), F_.at(s1, d1, z - 0.02)
    L = (p1 - p0).length
    up = Vector((0, 0, h + 0.04))
    RAILCARDS.face([p0, p1, p1 + up, p0 + up], M_RAILCARD, uvs=[(0, 0), (L / RAIL_TILE, 0), (L / RAIL_TILE, 1), (0, 1)])


class Frame:
    """A house front: s along the street from P0, d out from the wall, z up (metres, Blender space)."""

    def __init__(self, p0, u, n):
        self.p0 = Vector((p0[0], p0[1], 0))
        self.U = Vector((u[0], u[1], 0))
        self.N = Vector((n[0], n[1], 0))
        self.u, self.n = u, n
        self.rot = math.atan2(n[1], n[0]) + math.pi / 2         # for parts whose front faces -Y
        self.ang = math.atan2(n[1], n[0])

    def at(self, s, d, z):
        return self.p0 + self.U * s + self.N * d + Vector((0, 0, z))

    def box(self, mb, s, d, z, hs, hd, hz, m):
        mb.box(self.at(s, d, z), self.u, self.n, hs, hd, hz, m)


def railing(mb, F_, s, w, z, dp, rng, h=0.95):
    """Wrought iron round a balcony of half-width w and depth dp (wall at d=0)."""
    I = M_IRON
    if RAILS is not None and h == RAIL_H:           # (the bars close to, their picture further off: RAILS above)
        mb = RAILS
        railcard(F_, s - w, s + w, dp, dp, z, h)
        railcard(F_, s - w, s - w, 0.04, dp, z, h)
        railcard(F_, s + w, s + w, dp, 0.04, z, h)
    corners = [(s - w, dp), (s + w, dp)]
    for (cs, cd) in corners:
        mb.tube(F_.at(cs, cd, z), F_.at(cs, cd, z + h), 0.02, I)
    for zz, r in ((h, 0.02), (0.13, 0.012)):
        mb.tube(F_.at(s - w, dp, z + zz), F_.at(s + w, dp, z + zz), r, I)
        for cs in (s - w, s + w):
            mb.tube(F_.at(cs, 0.04, z + zz), F_.at(cs, dp, z + zz), r, I)
    n = max(2, int(2 * w / 0.12))
    for k in range(1, n):
        x = s - w + 2 * w * k / n
        mb.tube(F_.at(x, dp, z + 0.13), F_.at(x, dp, z + h), 0.007, I, 5)
    for cs in (s - w, s + w):
        for k in range(1, max(2, int(dp / 0.13))):
            dd = dp * k / max(2, int(dp / 0.13))
            mb.tube(F_.at(cs, dd, z + 0.13), F_.at(cs, dd, z + h), 0.007, I, 5)
    # a row of little rings half way up: the curls of the ironwork
    m = max(1, int(2 * w / 0.26))
    for k in range(m):
        cx = s - w + 2 * w * (k + 0.5) / m
        c = F_.at(cx, dp + 0.005, z + h * 0.56)
        pts = [c + F_.U * math.cos(a) * 0.065 + Vector((0, 0, math.sin(a) * 0.065)) for a in [i * math.pi / 3 for i in range(7)]]
        for p, q in zip(pts, pts[1:]):
            mb.tube(p, q, 0.006, I, 3)


def plants(cards, mb, F_, s, w, z, dp, kind, rng):
    """Whatever grows on one balcony (or window box): s centre, w half width, z floor level, dp front."""
    if kind == 'none':
        return
    if kind in PLANT_MAT:
        n = max(1, int(2 * w / 0.55))
        picks = [k for k in range(n) if rng.random() < 0.75] or [0]
        for k in picks:
            x = s - w + 2 * w * (k + 0.5) / n + rng.uniform(-0.08, 0.08)
            pot = F_.at(x, dp - 0.14, z + 0.12)
            mb.box(pot, F_.u, F_.n, 0.11, 0.09, 0.11, M_POT if rng.random() < 0.7 else M_TERRACOTTA)
            for j in range(3):
                cards.card(pot + Vector((0, 0, 0.3 if kind != 'herbs' else 0.24)), 0.55 if kind != 'herbs' else 0.45,
                           vertical(F_.ang + j * 1.05 + rng.uniform(-0.2, 0.2)), pot, PLANT_MAT[kind], 0.6)
        if kind == 'geranium' and rng.random() < 0.4:                 # some spill over the railing
            cards.clump(F_.at(s + rng.uniform(-w, w) * 0.6, dp + 0.06, z + 0.75), (0.35, 0.08, 0.25), 6, 0.45, M_GERANIUM_CARD, rng)
    elif kind == 'ivy':
        for k in range(2):
            x = s + rng.uniform(-w, w) * 0.7
            cards.clump(F_.at(x, dp + 0.07, z + 0.35), (0.32, 0.06, 0.55), 10, 0.45, M_IVY, rng)
        mb.box(F_.at(s, dp - 0.14, z + 0.12), F_.u, F_.n, min(w, 0.5), 0.09, 0.1, M_TERRACOTTA)
    elif kind == 'boug':
        x = s + rng.choice((-1, 1)) * w * 0.55
        mb.box(F_.at(x, dp - 0.2, z + 0.2), F_.u, F_.n, 0.18, 0.15, 0.2, M_TERRACOTTA)
        cards.clump(F_.at(x, dp - 0.05, z + 0.85), (0.55, 0.3, 0.45), 16, 0.6, M_BOUG, rng)
        cards.clump(F_.at(x + rng.uniform(-0.3, 0.3), 0.15, z + 1.7), (0.45, 0.12, 0.6), 12, 0.55, M_BOUG, rng)
    elif kind == 'lemon':
        x = s + rng.choice((-1, 1)) * (w - 0.3)
        c = F_.at(x, dp * 0.5, z)
        mb.cone(Matrix.Translation(c + Vector((0, 0, 0.18))), 10, 0.17, 0.13, 0.36, M_TERRACOTTA, smooth=False)
        mb.cone(Matrix.Translation(c + Vector((0, 0, 0.6))), 5, 0.025, 0.02, 0.5, M_BARK)
        cards.shell(c + Vector((0, 0, 1.0)), (0.33, 0.33, 0.3), 26, 0.4, M_CITRUS, rng)


def awning(mb, F_, s, w, ztop, out, drop, a, b, name):
    """A striped fabric awning sloping out from the wall, with a short valance at the front."""
    m = stripes_mat(a, b)
    rep = 2 * w / 1.76
    p = [F_.at(s - w, 0.02, ztop), F_.at(s + w, 0.02, ztop), F_.at(s + w, out, ztop - drop), F_.at(s - w, out, ztop - drop)]
    mb.face(p, m, normal=tuple(F_.N * 0.5 + Vector((0, 0, 1))), uvs=[(0, 0), (rep, 0), (rep, 1), (0, 1)])
    mb.face([p[3], p[2], p[2] - Vector((0, 0, 0.2)), p[3] - Vector((0, 0, 0.2))], m, normal=tuple(F_.N),
            uvs=[(0, 0), (rep, 0), (rep, 0.25), (0, 0.25)])
    for cs in (s - w, s + w):                                       # the iron arms
        mb.tube(F_.at(cs, 0.02, ztop - drop - 0.3), F_.at(cs, out, ztop - drop), 0.012, M_IRON, 5)


def tribuna(mb, F_, s, z, rng, col):
    """A glazed bay window, the modernista kind, one storey tall."""
    w, dp = 1.0, 0.8
    stone = M_STONE
    F_.box(mb, s, dp / 2, z + 0.08, w + 0.12, dp / 2 + 0.06, 0.1, stone)            # floor slab
    # two stone brackets under its ends (round 23: a cone-shaped corbel in the middle hung down over the shop's name
    # below, the user's "triangle thing above the sign ORX… on Carrer de Girona")
    for side in (-1, 1):
        F_.box(mb, s + side * (w - 0.12), dp * 0.3, z - 0.1, 0.07, dp * 0.3, 0.12, stone)
    F_.box(mb, s, dp / 2, z + 2.45, w + 0.15, dp / 2 + 0.1, 0.09, stone)            # roof slab
    F_.box(mb, s, dp / 2, z + 2.6, w + 0.05, dp / 2 + 0.02, 0.06, M_TERRACOTTA)
    F_.box(mb, s, dp, z + 0.45, w, 0.04, 0.33, mat('TribunaPanel' + hexof(col), shade(col, 0.85), 0.8))
    for side in (-1, 1):
        F_.box(mb, s + side * w, dp / 2, z + 0.45, 0.04, dp / 2, 0.33, mat('TribunaPanel' + hexof(col), shade(col, 0.85), 0.8))
    glass = M_GLASS_LIT if rng.random() < 0.6 else M_GLASS
    F_.box(mb, s, dp - 0.01, z + 1.55, w - 0.02, 0.015, 0.75, glass)
    for side in (-1, 1):
        F_.box(mb, s + side * (w - 0.01), dp / 2, z + 1.55, 0.015, dp / 2 - 0.02, 0.75, glass)
    fr = M_FRAME_TRIB
    for k in range(5):                                              # mullions and transoms
        x = s - w + 2 * w * k / 4
        F_.box(mb, x, dp + 0.01, z + 1.5, 0.035, 0.03, 0.82, fr)
    for zz in (0.8, 1.95, 2.32):
        F_.box(mb, s, dp + 0.01, z + zz, w + 0.02, 0.035, 0.03, fr)
        for side in (-1, 1):
            F_.box(mb, s + side * (w + 0.01), dp / 2, z + zz, 0.035, dp / 2, 0.03, fr)


def flower_box(mb, cards, F_, s, z, kind, rng):
    F_.box(mb, s, 0.16, z + 0.16, 0.62, 0.13, 0.1, M_TERRACOTTA)
    if kind != 'none':
        k2 = kind if kind in PLANT_MAT else 'geranium'
        for x in (-0.4, 0.0, 0.4):
            c = F_.at(s + x, 0.16, z + 0.4)
            for j in range(2):
                cards.card(c, 0.48, vertical(F_.ang + j * 1.5 + rng.uniform(-0.3, 0.3)), c - Vector((0, 0, 0.15)), PLANT_MAT[k2], 0.6)
        if kind == 'ivy':
            cards.clump(F_.at(s, 0.3, z - 0.1), (0.45, 0.06, 0.4), 8, 0.45, M_IVY, rng)


def washing(mb, F_, s, w, z, dp, rng):
    """Towels and a shirt drying over the railing."""
    for k in range(rng.randint(2, 4)):
        x = s - w + 0.25 + rng.uniform(0, 2 * w - 0.5)
        # (round 38, the user: the towels "flicker when you move" — overlapping towels shared one plane; each hangs at
        # its own depth now, the fronts 1.8 cm apart, all in front of the rail and the flag, rule 02 #39)
        F_.box(mb, x, dp + 0.04 + 0.018 * k, z + 0.72, rng.uniform(0.15, 0.24), 0.006, rng.uniform(0.18, 0.3), rng.choice(M_CLOTH))


# ------------------------------------------------------------------ one house front

def door_space(F_, s):
    """A doorway (round 21, the user: doors blocked by plants): nothing is put on the pavement in front of
    it (no tree, bench, bins or corner planter), and it is noted for the build's check (DOORS)."""
    keep_clear(F_.at(s, 0.7, 0), 0.7)
    DECO_DOORS.append((F_.at(s, 0.8, 0), Vector((F_.u[0], F_.u[1], 0))))


def ground_floor(mb, cards, F_, house, b, s, bw, rng, extras):
    kind = house['ground'][b]
    z0 = KERB
    if kind in ('portal', 'shopdoor', 'grand', 'passage'):
        door_space(F_, s)
    trim = house.get('trim', '#d9ccb2')
    if kind == 'shop':
        sh = house['shop']
        fm = frame_mat(sh['frame'])
        gw = bw / 2 - 0.42
        if sh.get('closed'):
            # shut for the afternoon: the roller shutter down over the window
            F_.box(mb, s, 0.07, z0 + 1.3, gw + 0.12, 0.04, 1.2, M_SHUTTER_DOOR)
            F_.box(mb, s, 0.05, z0 + 2.5, gw + 0.12, 0.05, 0.06, fm)
            return
        F_.box(mb, s, 0.03, z0 + 1.35, gw, 0.03, 1.12, M_SHOPGLASS)
        for side in (-1, 1):
            F_.box(mb, s + side * (gw + 0.06), 0.05, z0 + 1.35, 0.07, 0.05, 1.2, fm)
        F_.box(mb, s, 0.05, z0 + 0.2, gw + 0.12, 0.05, 0.2, fm)                 # stall riser
        # the window display: a shelf with goods in the trade's colours
        F_.box(mb, s, 0.06, z0 + 0.62, gw, 0.03, 0.02, fm)
        goods = {'books': ['#8a3a32', '#2f5a7a', '#c9a24a', '#3e6b4a', '#d8cbb0'], 'bar': ['#3a6b3a', '#7a2a2a', '#d8cbb0', '#c9a24a'],
                 'bikes': ['#b8423a', '#3a5a8a', '#2f2f35', '#e8dcc0'], 'flowers': ['#d8323a', '#f28ab0', '#f7f4ea', '#5a8a3a'],
                 'pharmacy': ['#f4f0e8', '#2fbf5a', '#8fb3d9', '#f4f0e8'], 'ice': ['#f7a1c0', '#f3e6c4', '#8a5a3a', '#b8e0c8'],
                 'hardware': ['#c9a24a', '#6b6b6b', '#3a5a8a', '#b8423a'], 'bakery': ['#c98a4a', '#e8c48a', '#8a5a3a', '#f3e6c4'],
                 'fruit': ['#f29a2e', '#d8322f', '#7fb03a', '#f3d24a'], 'clothes': ['#d95f4a', '#f4f0e8', '#3a5a8a', '#e8a0a8'],
                 'shoes': ['#6b4226', '#2f2f35', '#b8423a', '#c9a24a'], 'deli': ['#8a3a32', '#e8c48a', '#3a6b3a', '#c98a4a'],
                 'optics': ['#2f2f35', '#c9ccd0', '#3a5a8a', '#f4f0e8'], 'hair': ['#f2c6d6', '#f4f0e8', '#8fb3d9', '#c9ccd0']}.get(sh['kind'], ['#c9a24a', '#8a3a32'])
        x = s - gw + 0.12
        if sh['kind'] == 'bikes' and KIT_DETAIL != 'far':
            # (round 23, the user: Jordi's shop has "bikes outside and in the window") a bicycle stood side on behind
            # the glass: two wheels, the frame, saddle and bars
            x = s + gw                                                       # (no shelf of goods)
            nrm = Vector((F_.n[0], F_.n[1], 0)).normalized()
            rot = Vector((0, 0, 1)).rotation_difference(nrm).to_matrix().to_4x4()
            fcol = mat('WinBike' + sh['frame'].lstrip('#'), ['#b8423a', '#3a5a8a', '#2f6b5a'][int(abs(s) * 10) % 3], 0.5)
            tyre = mat('WinBikeTyre', '#2a2a2a', 0.8)
            wz = z0 + 0.64 + 0.27
            for dx in (-0.36, 0.36):
                c_ = F_.at(s + dx, 0.12, wz)
                fine().cone(Matrix.Translation(c_) @ rot, 16, 0.27, 0.27, 0.025, tyre)
                fine().cone(Matrix.Translation(c_ + nrm * 0.004) @ rot, 16, 0.22, 0.22, 0.025, mat('WinBikeRim', '#c9ccd0', 0.3, 0.6))
                fine().cone(Matrix.Translation(c_ + nrm * 0.008) @ rot, 12, 0.19, 0.19, 0.025, M_SHOPGLASS)
            for (a0, a1) in (((-0.36, wz), (0.0, wz + 0.02)), ((0.0, wz + 0.02), (-0.12, wz + 0.36)), ((-0.36, wz), (-0.12, wz + 0.36)),
                             ((-0.12, wz + 0.36), (0.26, wz + 0.36)), ((0.0, wz + 0.02), (0.26, wz + 0.36)), ((0.26, wz + 0.36), (0.36, wz))):
                p0, p1 = F_.at(s + a0[0], 0.135, a0[1]), F_.at(s + a1[0], 0.135, a1[1])
                fine().cone(Matrix.Translation((p0 + p1) / 2) @ Vector((0, 0, 1)).rotation_difference((p1 - p0).normalized()).to_matrix().to_4x4(),
                            6, 0.018, 0.018, (p1 - p0).length, fcol)
            F_.box(fine(), s - 0.13, 0.135, wz + 0.42, 0.08, 0.03, 0.02, mat('WinBikeSaddle', '#5a3b28', 0.6))
            F_.box(fine(), s + 0.27, 0.135, wz + 0.45, 0.02, 0.12, 0.012, fcol)
        while x < s + gw - 0.12 and KIT_DETAIL != 'far':
            hw, hh = rng.uniform(0.05, 0.12), rng.uniform(0.08, 0.22)
            F_.box(fine(), x + hw, 0.075, z0 + 0.64 + hh, hw, 0.02, hh, mat('Goods' + goods[int(x * 7) % len(goods)].lstrip('#'),
                   goods[int(x * 7) % len(goods)], 0.6))
            x += 2 * hw + rng.uniform(0.04, 0.12)
        F_.box(mb, s, 0.05, z0 + 2.5, gw + 0.12, 0.05, 0.06, fm)
        if b == house['ground'].index('shop') and 'shopdoor' not in house['ground']:
            # a door in the first shop bay: a darker panel with a brass handle
            F_.box(mb, s - gw * 0.45, 0.065, z0 + 1.1, 0.45, 0.015, 1.05, fm)
            F_.box(mb, s - gw * 0.45, 0.077, z0 + 1.35, 0.33, 0.012, 0.7, M_SHOPGLASS)
            F_.box(mb, s - gw * 0.45 + 0.35, 0.09, z0 + 1.05, 0.02, 0.02, 0.12, M_BRASS)
            door_space(F_, s - gw * 0.45)
        if sh.get('awning') and (not house.get('corner') or b == 1):
            # (round 41: at 2.95 m the awnings reached up over the shop's name board, hiding its name — the user: "the
            # words moved off to the side"; now they hang from just under the board)
            awning(fine() or mb, F_, s, gw + 0.15, z0 + 2.55, 1.0, 0.4, sh['awning'][0], sh['awning'][1], 'shop')
    elif kind == 'portal':
        F_.box(mb, s, 0.05, z0 + 1.38, 0.82, 0.06, 1.38, M_STONE)
        F_.box(mb, s, 0.1, z0 + 1.12, 0.62, 0.04, 1.12, frame_mat('#5a3b28'))
        F_.box(mb, s, 0.145, z0 + 1.1, 0.012, 0.01, 1.1, M_IRON)
        for side in (-1, 1):
            for zz in (0.55, 1.6):
                F_.box(mb, s + side * 0.33, 0.14, z0 + zz, 0.2, 0.01, 0.27, frame_mat('#6b4a33'))
            F_.box(mb, s + side * 0.09, 0.16, z0 + 1.0, 0.025, 0.025, 0.025, M_BRASS)
        F_.box(mb, s, 0.095, z0 + 2.42, 0.62, 0.03, 0.14, M_GLASS_LIT)          # (in front of the stone: round 21, it was flush and flickered)
        if house.get('entrance'):
            entrance_at(house['entrance'], F_, s)
        F_.box(mb, s + 1.0, 0.03, z0 + 1.5, 0.13, 0.015, 0.09, M_BRASS)            # number plate
        if KIT_DETAIL != 'far':
            extras.append(('text', F_, F_.at(s + 1.0, 0.05, z0 + 1.5), str(house['num']), 0.1, M_BRASS_TEXT))
    elif kind == 'shopdoor':
        # the shop's own door, glazed, in its frame, with the shop's colours: the way in
        fm = frame_mat(house['shop']['frame'])
        F_.box(mb, s, 0.05, z0 + 1.3, 0.85, 0.05, 1.3, fm)
        F_.box(mb, s, 0.085, z0 + 1.15, 0.65, 0.02, 1.12, M_SHOPGLASS)            # (proud of the frame, not flush with it)
        F_.box(mb, s, 0.11, z0 + 1.15, 0.015, 0.015, 1.12, fm)
        for side in (-1, 1):
            F_.box(mb, s + side * 0.12, 0.11, z0 + 1.1, 0.015, 0.03, 0.12, M_BRASS)
            F_.box(mb, s + side * (bw / 2 - 0.25), 0.05, z0 + 1.35, 0.14, 0.05, 1.2, fm)
        F_.box(mb, s, 0.05, z0 + 2.5, 0.85, 0.05, 0.06, fm)
        if house.get('entrance'):
            entrance_at(house['entrance'], F_, s, 2.24, 1.3)
    elif kind == 'grand':
        # a grand entrance: a tall stone arch with double doors
        F_.box(mb, s, 0.08, z0 + 1.7, 1.25, 0.1, 1.7, M_STONE)
        F_.box(mb, s, 0.15, z0 + 1.45, 0.95, 0.04, 1.45, M_WOOD_DOOR)            # (proud of the arch's stone, not flush)
        F_.box(mb, s, 0.15, z0 + 3.05, 1.0, 0.05, 0.12, M_GLASS_LIT)
        if house.get('entrance'):
            entrance_at(house['entrance'], F_, s, 2.9, 1.9)
    elif kind == 'window':
        F_.box(mb, s, 0.03, z0 + 1.55, 0.55, 0.03, 0.8, M_GLASS)
        F_.box(mb, s, 0.07, z0 + 0.7, 0.68, 0.08, 0.05, M_STONE)
        F_.box(mb, s, 0.06, z0 + 2.42, 0.66, 0.06, 0.06, M_STONE)
        if fine():
            for k in range(6):
                F_.box(fine(), s - 0.5 + k * 0.2, 0.1, z0 + 1.55, 0.012, 0.012, 0.8, M_IRON)
            F_.box(fine(), s, 0.1, z0 + 1.55, 0.55, 0.012, 0.012, M_IRON)
    elif kind == 'garage':
        F_.box(mb, s, 0.07, z0 + 1.2, bw / 2 - 0.45, 0.04, 1.2, M_SHUTTER_DOOR)
        F_.box(mb, s, 0.06, z0 + 2.48, bw / 2 - 0.4, 0.05, 0.08, M_STONE)
        F_.box(mb, s + bw / 2 - 0.3, 0.04, z0 + 1.7, 0.12, 0.01, 0.12, mat('Gual', '#2c5aa0', 0.5))   # "no parking" sign
    elif kind == 'passage':
        # arched opening into the garden; the tunnel itself is built by passage()
        for side in (-1, 1):
            F_.box(mb, s + side * (bw / 2 - 0.25), 0.05, z0 + 1.5, 0.25, 0.08, 1.5, M_STONE)
        F_.box(mb, s, 0.05, z0 + 2.95, bw / 2, 0.08, 0.22, M_STONE)
        F_.box(mb, s, 0.1, z0 + 2.95, 0.18, 0.05, 0.2, M_STONE)                 # keystone
        F_.box(mb, s + bw / 2 - 0.12, 0.14, z0 + 1.7, 0.25, 0.01, 0.13, M_MARBLE)
        extras.append(('text', F_, F_.at(s + bw / 2 - 0.12, 0.16, z0 + 1.72), "JARDÍ", 0.07, M_PLAQUE_TEXT))
        extras.append(('text', F_, F_.at(s + bw / 2 - 0.12, 0.16, z0 + 1.63), "DEL LLIRI", 0.05, M_PLAQUE_TEXT))


def build_house(mb, cards, F_, s0, width, house, H, rng, extras):
    if house.get('gaudi'):
        gaudi_front(mb, cards, F_, s0, width, house, H, rng, extras)
        return
    bays = house['bays']
    bw = width / bays
    col = house['facade']
    style = house['style']
    wall = stucco_mat(col)
    base = rustic_mat(house.get('trim', '#d9ccb2') if style != 'simple' else shade(col, 0.92))
    # wall surfaces: rusticated ground floor (with the passage left open) and stucco above
    for b in range(bays):
        if house['ground'][b] == 'passage':
            continue
        a0, a1 = s0 + b * bw, s0 + (b + 1) * bw
        mb.face([F_.at(a0, 0, 0), F_.at(a1, 0, 0), F_.at(a1, 0, GROUND_H), F_.at(a0, 0, GROUND_H)], base,
                normal=tuple(F_.N), uvscale=1.2)
    mb.face([F_.at(s0, 0, GROUND_H), F_.at(s0 + width, 0, GROUND_H), F_.at(s0 + width, 0, H), F_.at(s0, 0, H)], wall,
            normal=tuple(F_.N), uvscale=1.6)
    if any(g == 'passage' for g in house['ground']):
        b = house['ground'].index('passage')
        mb.face([F_.at(s0 + b * bw, 0, 3.0), F_.at(s0 + (b + 1) * bw, 0, 3.0), F_.at(s0 + (b + 1) * bw, 0, GROUND_H),
                 F_.at(s0 + b * bw, 0, GROUND_H)], base, normal=tuple(F_.N), uvscale=1.2)
    # plinth, string courses, pilasters at both ends
    for b in range(bays):
        if house['ground'][b] != 'passage':
            F_.box(mb, s0 + (b + 0.5) * bw, 0.03, 0.26, bw / 2, 0.04, 0.26, M_PLINTH)
    F_.box(mb, s0 + width / 2, 0.06, GROUND_H, width / 2, 0.08, 0.1, M_STONE)
    if style != 'simple':
        for f in range(1, house['uppers']):
            F_.box(mb, s0 + width / 2, 0.03, GROUND_H + f * FLOOR_H, width / 2, 0.035, 0.045, M_STONE)
    for e in (s0 + 0.14, s0 + width - 0.14):
        F_.box(mb, e, 0.04, (GROUND_H + H) / 2, 0.14, 0.05, (H - GROUND_H) / 2, M_STONE if style != 'simple' else wall)
    # cornice and parapet
    F_.box(mb, s0 + width / 2, 0.15, H - 0.12, width / 2 + 0.02, 0.18, 0.13, M_STONE)
    if style == 'classic':
        for k in range(int(width / 0.3)):
            F_.box(mb, s0 + 0.15 + k * 0.3, 0.06, H - 0.32, 0.05, 0.08, 0.06, M_STONE)        # dentils
        F_.box(mb, s0 + width / 2, -0.05, H + 0.06, width / 2, 0.18, 0.06, M_STONE)
        n = int(width / 0.22)
        for k in range(n):
            mb.cone(Matrix.Translation(F_.at(s0 + (k + 0.5) * width / n, -0.04, H + 0.42)), 6, 0.05, 0.035, 0.6, M_STONE)
        F_.box(mb, s0 + width / 2, -0.04, H + 0.78, width / 2, 0.14, 0.06, M_STONE)
    else:
        F_.box(mb, s0 + width / 2, -0.12, H + 0.38, width / 2, 0.12, 0.38, wall)
        F_.box(mb, s0 + width / 2, -0.12, H + 0.79, width / 2 + 0.02, 0.15, 0.04, M_STONE)
        if style == 'modernista':                                    # a curved crest over the middle
            for k in range(7):
                a = math.pi * k / 6
                F_.box(mb, s0 + width / 2 + math.cos(a) * 1.4, -0.1, H + 0.85 + math.sin(a) * 0.5, 0.2, 0.1, 0.1, wall)
    # upper floors
    trib = set(house.get('tribuna', []))
    flagged = False
    for f in range(house['uppers']):
        z = GROUND_H + f * FLOOR_H
        kind = house['balc'][f]
        if kind == 'long':
            w = width / 2 - 0.35
            F_.box(mb, s0 + width / 2, 0.32, z + 0.07, w, 0.32, 0.07, M_STONE)
            F_.box(mb, s0 + width / 2, 0.64, z + 0.04, w + 0.02, 0.03, 0.05, M_STONE)
            for k in range(bays * 2):
                F_.box(mb, s0 + (k + 0.5) * width / (bays * 2), 0.16, z - 0.12, 0.05, 0.15, 0.1, M_STONE)
            if KIT_DETAIL == 'far':
                F_.box(mb, s0 + width / 2, 0.62, z + 0.6, w, 0.012, 0.42, M_IRON)
            else:
                railing(fine(), F_, s0 + width / 2, w, z + 0.14, 0.62, rng)
        for b in range(bays):
            s = s0 + (b + 0.5) * bw
            if (b, f) in trib:
                tribuna(mb, F_, s, z, rng, col)
                continue
            lit = rng.random() < 0.3
            v = house['shutter']
            # the full window close to, a light copy further away (the game swaps them over at a distance)
            if CRISP:
                crisp_window(mb, F_, s, z, v, lit, rng, warm=False, lo=KIT_DETAIL == 'far')
            else:
                std_window(mb, F_, s, z, v, lit, rng, far=KIT_DETAIL == 'far')
            plant = rng.choice(house['plants'])
            if KIT_DETAIL == 'far':
                if kind in ('iron', 'long'):
                    F_.box(mb, s, 0.3, z + 0.07, 0.86, 0.3, 0.07, M_STONE)
                    F_.box(mb, s, 0.6, z + 0.6, 0.86, 0.012, 0.42, M_IRON)       # the railing, as one dark panel
                continue
            if kind == 'iron':
                F_.box(mb, s, 0.3, z + 0.07, 0.86, 0.3, 0.07, M_STONE)
                F_.box(mb, s, 0.6, z + 0.04, 0.88, 0.03, 0.05, M_STONE)
                for side in (-1, 1):
                    F_.box(mb, s + side * 0.6, 0.15, z - 0.1, 0.05, 0.14, 0.09, M_STONE)
                railing(fine(), F_, s, 0.84, z + 0.14, 0.58, rng)
                plants(cards, fine(), F_, s, 0.75, z + 0.14, 0.56, plant, rng)
                dp = 0.58
            elif kind == 'long':
                plants(cards, fine(), F_, s, bw / 2 - 0.2, z + 0.14, 0.6, plant, rng)
                dp = 0.62
            elif kind == 'box':
                flower_box(mb, cards, F_, s, z + 0.1, plant, rng)
                dp = 0
            else:
                dp = 0
            # now and then: an awning, a half-lowered blind, washing, the senyera, an air conditioner
            r = rng.random()
            if dp and r < 0.18:
                stripes = rng.choice([('#2f6b5a', '#efe6d2'), ('#d9853b', '#f5ecd6'), ('#b8423a', '#f2e6cf'), ('#3a5a8a', '#efe6d2')])
                awning(fine(), F_, s, 0.8, z + 2.42, dp + 0.05, 0.55, stripes[0], stripes[1], 'balcony')
            elif r < 0.3:
                # (round 25, the user: "remove the rollershutters you add everywhere": the half-lowered blind is gone;
                # its dice are still thrown, so the street's other choices stay as they were)
                rng.uniform(0, 0.5), rng.uniform(0.2, 0.45)
            if dp and rng.random() < 0.12:
                washing(fine(), F_, s, 0.8, z + 0.14, dp, rng)
            if dp and not flagged and rng.random() < 0.08:
                flagged = True
                p = [F_.at(s - 0.35, dp + 0.03, z + 1.06), F_.at(s + 0.35, dp + 0.03, z + 1.06),
                     F_.at(s + 0.35, dp + 0.03, z + 0.36), F_.at(s - 0.35, dp + 0.03, z + 0.36)]
                mb.face(p, M_SENYERA, normal=tuple(F_.N), uvs=[(0, 1), (1, 1), (1, 0), (0, 0)])
            if rng.random() < 0.06:
                F_.box(fine(), s + 0.95, 0.15, z + 0.6, 0.32, 0.14, 0.24, M_AC)
    # ground floor
    for b in range(bays):
        ground_floor(mb, cards, F_, house, b, s0 + (b + 0.5) * bw, bw, rng, extras)
    if house.get('sign') and KIT_DETAIL != 'far':
        F_.box(mb, s0 + width / 2, 0.09, GROUND_H - 0.35, 3.6, 0.04, 0.22, M_STONE)
        extras.append(('text', F_, F_.at(s0 + width / 2, 0.14, GROUND_H - 0.35), house['sign'], 0.2, M_PLAQUE_TEXT))
    if house.get('shop'):
        sh = house['shop']
        shop_bays = [b for b in range(bays) if house['ground'][b] in ('shop', 'shopdoor')]
        if house.get('corner'):
            shop_bays = [1]                            # the street name plaques go either side
        a0, a1 = s0 + shop_bays[0] * bw + 0.3, s0 + (shop_bays[-1] + 1) * bw - 0.3
        F_.box(mb, (a0 + a1) / 2, 0.07, KERB + 2.78, (a1 - a0) / 2, 0.06, 0.2, frame_mat(sh['frame']))
        # (round 37, the user: "All signs should be visible and have nothing blocking them") nothing is put on the
        # pavement right in front of the shop's name (no planter, bench, bins, bikes or corner bougainvillea; the corner
        # lamp to one side), as for a doorway; the street trees stay (their crowns are above it, their trunks thin)
        k_ = max(1, int(round((a1 - a0) / 1.5)))
        for q in range(k_):
            p_ = F_.at(a0 + (a1 - a0) * (q + 0.5) / k_, 0.7, 0)
            SIGN_FRONTS.append((p_.x / T, -p_.y / T, 0.9 / T))
        if KIT_DETAIL == 'far':
            return
        SIGN_CHECK.append((F_.at((a0 + a1) / 2, 0.2, KERB + 2.78), Vector((F_.n[0], F_.n[1], 0)), 'shop: ' + sh['name']))
        # as big as the door bay between the awnings allows (the 2D game's fascia names are big and bold)
        size = min(0.3, (bw - 0.45) / (0.62 * len(sh['name'])))
        # (round 41: over the shop's own door when it has one, between the awnings, where it was sized to fit)
        dbs_ = [b for b in shop_bays if house['ground'][b] == 'shopdoor']
        nx_ = s0 + (dbs_[0] + 0.5) * bw if dbs_ else (a0 + a1) / 2
        extras.append(('text', F_, F_.at(nx_, 0.135, KERB + 2.78), sh['name'], size, M_SIGN_TEXT))
        if sh['kind'] == 'pharmacy':
            # the green cross on its bracket, sticking out over the pavement below the first-floor balconies
            c = F_.at(a1 + 0.05, 0.62, KERB + 2.5)
            F_.box(mb, a1 + 0.05, 0.3, KERB + 2.85, 0.02, 0.3, 0.02, M_IRON)
            F_.box(mb, a1 + 0.05, 0.62, KERB + 2.83, 0.015, 0.015, 0.03, M_IRON)
            # a proper pharmacy sign: a dark square panel with the green cross on both faces, outlined in white
            # (on its own, the cross read as a plain green square from along the street)
            mb.box(c, F_.n, (-F_.u[0], -F_.u[1]), 0.36, 0.025, 0.36, M_IRON)
            for side in (-1, 1):
                cc = c + Vector((-F_.u[0], -F_.u[1], 0)) * (side * 0.03)
                for (hs, hz) in ((0.3, 0.11), (0.11, 0.3)):
                    mb.box(cc, F_.n, (-F_.u[0], -F_.u[1]), hs, 0.008, hz, M_WHITE_TRIM)
                cc = c + Vector((-F_.u[0], -F_.u[1], 0)) * (side * 0.04)
                for (hs, hz) in ((0.26, 0.075), (0.075, 0.26)):
                    mb.box(cc, F_.n, (-F_.u[0], -F_.u[1]), hs, 0.008, hz, M_CROSS)
        extras.append(('wares', F_, house, s0, s0 + width))


def rear_facade(mb, cards, Q0, Q1, H, house, rng, tag, opening=None, cheap=False):
    """The courtyard side: plainer, with galleries, windows and washing. cheap: just the wall and its
    windows (blocks whose insides are only seen from the air)."""
    u, n, L = edge_frame(Q0, Q1)
    n = (-n[0], -n[1])                                               # facing into the courtyard
    p0 = B(*Q1)
    F_ = Frame((p0.x, p0.y), (-u[0], -u[1]), n)
    width = L * T
    col = shade(house['facade'], 1.04) if house else '#eadbc2'
    wall = stucco_mat(col)
    cuts = [(0, width, 0)] if not opening else [(0, opening[0], 0), (opening[1], width, 0), (opening[0], opening[1], 3.0)]
    for (a, b, z0) in cuts:
        mb.face([F_.at(a, 0, z0), F_.at(b, 0, z0), F_.at(b, 0, H), F_.at(a, 0, H)], wall, normal=tuple(F_.N), uvscale=1.6)
    F_.box(mb, width / 2, -0.1, H + 0.35, width / 2, 0.1, 0.35, wall)
    nb = max(1, round(width / 2.6))
    bw = width / nb
    uppers = int(round((H - GROUND_H) / FLOOR_H))
    if cheap:
        for f in range(uppers):
            for b in range(nb):
                F_.box(mb, (b + 0.5) * bw, 0.02, GROUND_H + f * FLOOR_H + 1.25, 0.45, 0.03, 0.75,
                       M_GLASS_LIT if rng.random() < 0.25 else M_GLASS)
        return
    for f in range(-1, uppers):
        z = (KERB if f < 0 else GROUND_H + f * FLOOR_H)
        gallery = f >= 0 and rng.random() < 0.35
        if gallery and width > 2.5:
            w = width / 2 - 0.5
            F_.box(mb, width / 2, 0.55, z + 0.08, w, 0.55, 0.08, M_STONE)
            F_.box(mb, width / 2, 1.08, z + 0.5, w, 0.03, 0.4, wall)
            F_.box(mb, width / 2, 1.07, z + 1.5, w - 0.02, 0.015, 0.6, M_GLASS_LIT if rng.random() < 0.5 else M_GLASS)
            for k in range(int(2 * w / 0.6) + 1):
                F_.box(mb, width / 2 - w + k * 0.6, 1.1, z + 1.5, 0.025, 0.03, 0.62, M_FRAME_TRIB)
            F_.box(mb, width / 2, 0.55, z + 2.18, w, 0.55, 0.05, M_STONE)
            for side in (-1, 1):
                F_.box(mb, width / 2 + side * w, 0.55, z + 1.1, 0.03, 0.55, 1.05, wall)
            continue
        for b in range(nb):
            s = (b + 0.5) * bw
            if opening and f < 0 and opening[0] <= s <= opening[1]:
                continue
            glass = M_GLASS_LIT if rng.random() < 0.4 else M_GLASS
            hz = 0.75 if f >= 0 else 0.6
            F_.box(mb, s, 0.02, z + 1.25, 0.45, 0.03, hz, glass)
            F_.box(mb, s, 0.06, z + 1.25 - hz - 0.04, 0.55, 0.07, 0.04, M_STONE)
            for side in (-1, 1):
                F_.box(mb, s + side * 0.68, 0.04, z + 1.25, 0.22, 0.025, hz, rng.choice(SHUTTER_M))
            if f >= 0 and rng.random() < 0.25:                          # a washing line on brackets
                a, b2 = F_.at(s - 0.7, 0.6, z + 1.0), F_.at(s + 0.7, 0.6, z + 1.0)
                mb.tube(F_.at(s - 0.7, 0.0, z + 1.0), a, 0.01, M_IRON, 4)
                mb.tube(F_.at(s + 0.7, 0.0, z + 1.0), b2, 0.01, M_IRON, 4)
                mb.tube(a, b2, 0.004, M_IRON, 3)
                for k in range(rng.randint(2, 4)):
                    x = s - 0.55 + k * 0.35
                    F_.box(mb, x, 0.6, z + 0.78, rng.uniform(0.1, 0.16), 0.008, rng.uniform(0.15, 0.24), rng.choice(M_CLOTH))
            if f >= 0 and rng.random() < 0.2:
                F_.box(mb, s, 0.18, z + 0.55, 0.5, 0.12, 0.09, M_TERRACOTTA)
                c = F_.at(s, 0.18, z + 0.75)
                cards.clump(c, (0.45, 0.12, 0.2), 6, 0.4, rng.choice((M_GERANIUM_CARD, M_SHRUB, M_PINK)), rng)
    # a drainpipe
    mb.tube(F_.at(0.25, 0.1, 0), F_.at(0.25, 0.1, H), 0.05, M_IRON, 6)


def roof(mb, P0, P1, Q0, Q1, H, rng, roofmat):
    mb.face([B(*P0, H), B(*P1, H), B(*Q1, H), B(*Q0, H)], roofmat, normal=(0, 0, 1), uvscale=1.2)
    u, n, _ = edge_frame(P0, P1)
    mid = lerp2(lerp2(P0, P1, 0.5), lerp2(Q0, Q1, 0.5), 0.5)
    for k in range(rng.randint(1, 3)):
        r = lerp2(lerp2(P0, P1, rng.uniform(0.2, 0.8)), lerp2(Q0, Q1, rng.uniform(0.2, 0.8)), rng.uniform(0.3, 0.7))
        mb.box(B(*r, H + 0.6), u, n, 0.22, 0.22, 0.6, M_CHIMNEY)
        mb.box(B(*r, H + 1.25), u, n, 0.28, 0.28, 0.05, M_CHIMNEY)
    if rng.random() < 0.5:
        mb.box(B(*mid, H + 1.1), u, n, 0.8, 0.7, 1.1, M_HUT)
    if rng.random() < 0.5:
        r = lerp2(mid, lerp2(Q0, Q1, 0.5), 0.5)
        mb.box(B(*r, H + 0.5), u, n, 0.45, 0.45, 0.5, M_TANK)
    if rng.random() < 0.6:                                        # washing on the terrat
        a = B(*lerp2(mid, lerp2(P0, P1, 0.2), 0.5), H)
        b = B(*lerp2(mid, lerp2(P0, P1, 0.8), 0.5), H)
        for p in (a, b):
            mb.tube(p, p + Vector((0, 0, 1.5)), 0.02, M_IRON, 4)
        mb.tube(a + Vector((0, 0, 1.5)), b + Vector((0, 0, 1.5)), 0.005, M_IRON, 3)
        d = b - a
        for k in range(rng.randint(3, 6)):
            p = a + d * rng.uniform(0.1, 0.9) + Vector((0, 0, 1.25)) + Vector((n[0], n[1], 0)) * (0.018 * k - 0.045)   # (round 38: each at its own depth, no two in one plane)
            mb.box(p, (d.x / d.length, d.y / d.length), n, rng.uniform(0.12, 0.25), 0.008, rng.uniform(0.15, 0.3), rng.choice(M_CLOTH))


def party_wall(mb, P, Q, h_lo, h_hi, towards):
    """Bare side wall where a taller house stands next to a lower one."""
    a, b = B(*P), B(*Q)
    radial = b - a
    nrm = Vector((-radial.y, radial.x, 0)).normalized()
    if nrm.dot(towards - a) < 0:
        nrm = -nrm
    mb.face([a + Vector((0, 0, h_lo)), b + Vector((0, 0, h_lo)), b + Vector((0, 0, h_hi)), a + Vector((0, 0, h_hi))], M_PARTY, normal=nrm)


# ------------------------------------------------------------------ the block

def straight_back(o0, o1, i0, i1, P):
    """The point on the courtyard side (i0-i1) straight behind P on the street side (o0-o1)."""
    u, _, L = edge_frame(o0, o1)
    along = lambda q: (q[0] - o0[0]) * u[0] - (q[1] - o0[1]) * u[1]          # tile units along the street
    a0, a1 = along(i0), along(i1)
    return lerp2(i0, i1, (along(P) - a0) / (a1 - a0))


def build_kit_block(ox, oy, houses, meshy=None, with_garden=False, detail='full', sandra=False):
    """Builds block (ox, oy) from a HOUSES-style table.
    meshy: {'file', 'edge'}: a Meshy building (MESHY_BUILDINGS) set into that side. The corner houses
           either side wrap round onto that side by one bay, as Eixample corner buildings do, and meet
           its main front exactly (overlapping it by a few centimetres, so no daylight shows at the joint).
    with_garden: the inside of the block is a garden you can walk into (Sandra's block), with proper
           courtyard façades; otherwise it is roofed over low (workshops), seen only from the air.
    detail: 'full' near the walkable streets, 'far' beyond them.
    sandra: Sandra's own block (her door's lantern and doorbell, Montse, Trufa, the bins)."""
    global KIT_DETAIL, FINE, CRISP, WINPIC
    KIT_DETAIL = detail
    WINPIC = MB(uv=True) if WIN_STYLE == 'picture' else None
    CRISP = (ox, oy) in CRISP_BLOCKS
    outer, inner = octagon(ox, oy), octagon(ox, oy, -COURT)
    rng = random.Random(KIT_SEED + ox * 7919 + oy * 104729)
    kit = MB(uv=True)
    FINE = MB(uv=True) if detail != 'far' else None
    if detail != 'far':
        rails_begin()
    cards = Cards()
    extras = []
    spans = {}            # edge -> list of (t0, t1, H)
    medge = meshy['edge'] if meshy else None
    for i in range(8):
        if i == medge:
            continue
        bays_total = sum(h['bays'] for h in houses[i])
        t = 0.0
        spans[i] = []
        for h in houses[i]:
            t1 = t + h['bays'] / bays_total
            spans[i].append((t, t1, GROUND_H + h['uppers'] * FLOOR_H))
            t = t1
    if meshy:
        M = MESHY_BUILDINGS[meshy['file']]
        front_m = (BS - 2 * CUT) * T * M['scale']
        wing = meshy_wing(meshy['file'])
        Hw = GROUND_H + MESHY_WING_UPPERS * FLOOR_H                # the wrapped-round corner bays: level with it
        spans[medge] = [(0.0, wing, Hw), (wing, 1.0 - wing, meshy_height(meshy['file'])), (1.0 - wing, 1.0, Hw)]
    passage = None
    for i in range(8):
        o0, o1 = outer[i], outer[(i + 1) % 8]
        i0, i1 = inner[i], inner[(i + 1) % 8]
        u, n, L = edge_frame(o0, o1)
        width_total = L * T
        F_ = Frame((B(*o0).x, B(*o0).y), u, n)
        if i == medge:
            Hm = spans[i][1][2]
            # the Meshy building itself, its wall brought forward onto the street line
            fwd = M['wall'] * front_m
            mid = B(*lerp2(o0, o1, 0.5), KERB) + F_.N * fwd
            meshy_place(meshy['file'], 60000, 'front', front_m, mid, F_.rot, 'MeshyBuilding_%d_%d_%d' % (ox, oy, i))
            if M.get('fix', {}).get('kind') == 'flat':
                # its new flat roof gets a balustrade along the street line, like the classic houses'
                a0, a1 = spans[i][0][1] * width_total, spans[i][2][0] * width_total
                c, w2 = (a0 + a1) / 2, (a1 - a0) / 2
                F_.box(kit, c, -0.1, Hm + 0.06, w2, 0.14, 0.06, M_STONE)
                nb_ = int((a1 - a0) / 0.22)
                for k in range(nb_):
                    kit.cone(Matrix.Translation(F_.at(a0 + (k + 0.5) * (a1 - a0) / nb_, -0.08, Hm + 0.42)), 6, 0.05, 0.035, 0.6, M_STONE)
                F_.box(kit, c, -0.1, Hm + 0.78, w2, 0.16, 0.06, M_STONE)
            scene.setdefault('fronts', []).append({'name': 'meshy_%d_%d' % (ox, oy), 'pos': to_m(lerp2(o0, o1, 0.5)),
                                                   'normal': [round(n[0], 3), round(-n[1], 3)]})
            # its courtyard side, and a strip of roof over the gap between its back and the courtyard
            # wall, kept just below its roof so the two never fight
            rear_facade(kit, cards, i0, i1, Hm, None, rng, 'r%d' % i, cheap=not with_garden)
            q0, q1 = lerp2(i0, o0, 0.45), lerp2(i1, o1, 0.45)
            roof(kit, q0, q1, i0, i1, Hm - 0.3, random.Random(44 + ox + oy), ROOF_M[2])
            prev_house, next_house = houses[(i - 1) % 8][-1], houses[(i + 1) % 8][0]
            for (t0, t1, H), corner, num in ((spans[i][0], prev_house, 4 if sandra else prev_house['num'] + 2),
                                             (spans[i][2], next_house, 6 if sandra else next_house['num'] - 2)):
                w = dict(corner, bays=1, ground=['portal'], tribuna=[], shop=None, num=num, seed=corner['seed'] + 50,
                         corner=False, uppers=MESHY_WING_UPPERS)
                hr = random.Random(w['seed'] * 101 + KIT_SEED)
                build_house(kit, cards, F_, t0 * width_total, (t1 - t0) * width_total, w, H, hr, extras)
                if sandra and num == 4:
                    # Sandra's door: a lantern over it, and the doorbell with the little paper German flag
                    s = (t0 + t1) / 2 * width_total
                    F_.box(kit, s, 0.3, 3.0, 0.1, 0.1, 0.13, M_DOORLAMP)
                    F_.box(kit, s, 0.3, 3.15, 0.13, 0.13, 0.025, M_IRON)
                    F_.box(kit, s, 0.15, 3.15, 0.02, 0.15, 0.02, M_IRON)
                    F_.box(kit, s - 1.0, 0.04, KERB + 1.12, 0.1, 0.015, 0.14, M_BRASS)
                    for k, col in enumerate(('#1d1d1d', '#d8342f', '#f2c84b')):
                        F_.box(kit, s - 1.0, 0.06, KERB + 0.9 - k * 0.022, 0.055, 0.005, 0.011, mat('Flag%d' % k, col, 0.8))
                P0, P1 = lerp2(o0, o1, t0), lerp2(o0, o1, t1)
                # back corners: the inner corner of the block, and straight back from the joint with the Meshy building
                joint = P1 if t0 == 0.0 else P0
                back = straight_back(o0, o1, i0, i1, joint)
                poly = [P0, P1, back, i0] if t0 == 0.0 else [P0, P1, i1, back]
                kit.face([B(*p, H) for p in poly], ROOF_M[corner['seed'] % len(ROOF_M)], normal=(0, 0, 1), uvscale=1.2)
                # its side wall against the Meshy building, full height so no daylight shows between them
                party_wall(kit, joint, back, 0.0, H, B(*lerp2(o0, o1, 0.5)))
                c = B(*lerp2(lerp2(P0, P1, 0.5), lerp2(back, i0 if t0 == 0.0 else i1, 0.5), 0.4))
                kit.box(c + Vector((0, 0, H + 0.6)), u, n, 0.22, 0.22, 0.6, M_CHIMNEY)
                kit.box(c + Vector((0, 0, H + 1.25)), u, n, 0.28, 0.28, 0.05, M_CHIMNEY)
            # where the first wrapped-round bay meets the corner house before it, if they differ in height
            Hp = spans[(i - 1) % 8][-1][2]
            if abs(Hp - Hw) > 0.01:
                party_wall(kit, o0, i0, min(Hw, Hp), max(Hw, Hp), B(*lerp2(o0, i0, 0.5)) + F_.U * (1 if Hw < Hp else -1))
            continue
        for hi, house in enumerate(houses[i]):
            house['corner'] = i % 2 == 1
            t0, t1, H = spans[i][hi]
            hr = random.Random(house['seed'] * 101 + KIT_SEED)
            build_house(kit, cards, F_, t0 * width_total, (t1 - t0) * width_total, house, H, hr, extras)
            P0, P1 = lerp2(o0, o1, t0), lerp2(o0, o1, t1)
            Q0, Q1 = lerp2(i0, i1, t0), lerp2(i0, i1, t1)
            opening = None
            if 'passage' in house['ground']:
                b = house['ground'].index('passage')
                ta = t0 + (t1 - t0) * (b + 0.12) / house['bays']
                tb = t0 + (t1 - t0) * (b + 0.88) / house['bays']
                passage = (i, ta, tb)
                # it runs straight in from the street, square to the front
                Qa, Qb = straight_back(o0, o1, i0, i1, lerp2(o0, o1, ta)), straight_back(o0, o1, i0, i1, lerp2(o0, o1, tb))
                opening = (math.dist(Q1, Qb) * T, math.dist(Q1, Qa) * T)     # the rear frame runs the other way
            rear_facade(kit, cards, Q0, Q1, H, house, hr, 'r%d' % i, opening, cheap=not with_garden)
            roof(kit, P0, P1, Q0, Q1, H, hr, ROOF_M[(house['seed']) % len(ROOF_M)])
        # party walls between neighbouring houses of different heights (including round the corners)
        for hi in range(len(spans[i])):
            t0, t1, H = spans[i][hi]
            if hi > 0:
                Hp = spans[i][hi - 1][2]
            else:
                Hp = spans[(i - 1) % 8][-1][2]
            if abs(Hp - H) > 0.01:
                P, Q = lerp2(o0, o1, t0), lerp2(i0, i1, t0)
                towards = B(*lerp2(P, Q, 0.5)) + (F_.U * (1 if H < Hp else -1))
                party_wall(kit, P, Q, min(H, Hp), max(H, Hp), towards)
    # the passage tunnel from Carrer de Girona into the garden
    if passage:
        i, ta, tb = passage
        o0, o1 = outer[i], outer[(i + 1) % 8]
        i0, i1 = inner[i], inner[(i + 1) % 8]
        Pa, Pb = lerp2(o0, o1, ta), lerp2(o0, o1, tb)
        Qa, Qb = straight_back(o0, o1, i0, i1, Pa), straight_back(o0, o1, i0, i1, Pb)
        hz = 3.0
        for (P, Q, other) in ((Pa, Qa, Pb), (Pb, Qb, Pa)):
            towards = B(*other)
            a, b = B(*P), B(*Q)
            radial = b - a
            nrm = Vector((-radial.y, radial.x, 0)).normalized()
            if nrm.dot(towards - a) < 0:
                nrm = -nrm
            kit.face([a, b, b + Vector((0, 0, hz)), a + Vector((0, 0, hz))], rustic_mat('#d9ccb2'), normal=nrm, uvscale=1.2)
        kit.face([B(*Pa, hz), B(*Pb, hz), B(*Qb, hz), B(*Qa, hz)], M_HUT, normal=(0, 0, -1))
        u, n, _ = edge_frame(o0, o1)
        for t in (0.25, 0.5, 0.75):                                        # lamps along the vault
            c = B(*lerp2(lerp2(Pa, Pb, 0.5), lerp2(Qa, Qb, 0.5), t), hz - 0.18)
            kit.box(c, u, n, 0.12, 0.12, 0.12, M_DOORLAMP)
        # the gates, swung open against the tunnel walls
        for (P, Q, s) in ((Pa, Qa, 1), (Pb, Qb, -1)):
            a = B(*lerp2(P, Q, 0.03))
            b = B(*lerp2(P, Q, 0.2))
            inward = (B(*lerp2(Pa, Pb, 0.5)) - B(*P)).normalized() * 0.08
            for k in range(9):
                p = a + (b - a) * k / 8 + inward
                kit.tube(p + Vector((0, 0, 0.1)), p + Vector((0, 0, 2.4)), 0.012, M_IRON, 5)
            for zz in (0.15, 1.2, 2.4):
                kit.tube(a + inward + Vector((0, 0, zz)), b + inward + Vector((0, 0, zz)), 0.016, M_IRON, 5)
        scene['passage'] = {'outer': [to_m(Pa), to_m(Pb)], 'inner': [to_m(Qa), to_m(Qb)]}
    tag = '%d_%d' % (ox, oy)
    if with_garden:
        garden_mb = MB(uv=True)
        garden(cards, garden_mb, inner, rng)
        city_objs.append(garden_mb.finish('Garden_' + tag))
    else:
        # the inside of the block: low workshop roofs, as in most Eixample blocks
        kit.face([B(*p, GROUND_H + 0.4) for p in inner], ROOF_M[(ox + oy) % len(ROOF_M)], normal=(0, 0, 1), uvscale=1.2)
    wares = MB(uv=True)
    signs_and_wares(extras, wares, cards, rng, sandra)
    city_objs.append(kit.finish('Block_' + tag))
    if WINPIC is not None:
        if WINPIC.bm.faces:
            city_objs.append(WINPIC.finish('WinPic_' + tag))
        else:
            WINPIC.bm.free()
        WINPIC = None
    if FINE is not None and FINE.bm.faces:
        city_objs.append(FINE.finish('Detail_' + tag))
    rails_finish(tag, city_objs)
    if wares.bm.faces:
        city_objs.append(wares.finish('Wares_' + tag))
    else:
        wares.bm.free()
    if cards.faces:
        city_objs.append(cards.finish('Plants_' + tag))
    FINE = None
    KIT_DETAIL = 'full'
    # collision: a garden block is a ring of houses, open where the passage runs through
    if with_garden:
        pieces = []
        for i in range(8):
            o0, o1 = outer[i], outer[(i + 1) % 8]
            i0, i1 = inner[i], inner[(i + 1) % 8]
            if passage and passage[0] == i:
                _, ta, tb = passage
                Pa, Pb = lerp2(o0, o1, ta), lerp2(o0, o1, tb)
                Qa, Qb = straight_back(o0, o1, i0, i1, Pa), straight_back(o0, o1, i0, i1, Pb)
                pieces.append([to_m(o0), to_m(Pa), to_m(Qa), to_m(i0)])
                pieces.append([to_m(Pb), to_m(o1), to_m(i1), to_m(Qb)])
            else:
                pieces.append([to_m(o0), to_m(o1), to_m(i1), to_m(i0)])
        for blk in scene['blocks']:
            if blk['origin'] == [ox, oy]:
                blk['solids'] = pieces
                blk['court'] = [to_m(p) for p in inner]


def bin_bay(mb, cards, c, u, n, cols, rng):
    """Two recycling containers side by side, with a planter of flowers at each end so they sit in
    the row of street trees like part of it. c: centre on the pavement (Blender), u along the street,
    n towards the road; cols: two indices into M_BINS (0 glass, 1 packaging, 2 paper, 3 general, 4 organic)."""
    U, N, Z = Vector((u[0], u[1], 0)), Vector((n[0], n[1], 0)), Vector((0, 0, 1))
    at = lambda s, d, z: c + U * s + N * d + Z * z
    for j, s in enumerate((-0.5, 0.5)):
        m = M_BINS[cols[j]]
        mb.box(at(s, 0, 0.56), u, n, 0.46, 0.35, 0.47, m)                        # body
        mb.box(at(s, 0, 1.05), u, n, 0.48, 0.37, 0.04, m)                        # lid
        mb.box(at(s, -0.355, 0.86), u, n, 0.24, 0.01, 0.05, M_IRON)              # the slot, on the pavement side
        mb.box(at(s, -0.355, 0.62), u, n, 0.16, 0.008, 0.1, M_SIGN_TEXT)          # a pale label
        mb.box(at(s, 0, 0.1), u, n, 0.4, 0.3, 0.02, M_IRON)                      # base frame
        for fs in (-0.36, 0.36):
            for fd in (-0.25, 0.25):
                mb.cone(Matrix.Translation(at(s + fs, fd, 0.0)), 6, 0.04, 0.04, 0.09, M_IRON)
        mb.box(at(s, -0.36, 0.14), u, n, 0.12, 0.04, 0.02, M_IRON)               # the foot pedal
    for s in (-1.2, 1.2):                                                         # planters either end
        mb.box(at(s, 0, 0.27), u, n, 0.17, 0.3, 0.27, M_TERRACOTTA)
        mb.box(at(s, 0, 0.55), u, n, 0.19, 0.32, 0.025, M_STONE)
        cards.clump(at(s, 0, 0.78), (0.2, 0.32, 0.22), 7, 0.36, rng.choice((M_GERANIUM_CARD, M_PINK, M_DAISY)), rng)


def bl_m(p):
    """Blender point -> engine metres [x, z]."""
    return [round(p.x, 3), round(-p.y, 3)]


def keep_clear(p, r):
    """Nothing else (trees, benches) goes within r metres of Blender point p on the pavement."""
    KEEP_CLEAR.append((p.x / T, -p.y / T, r / T))


def clear_of_doors(p, r):
    """(round 21) Is Blender point p at least r metres clear of every doorway's pavement? (DECO_DOORS)"""
    return all((p - d[0]).xy.length > r + 0.6 for d in DECO_DOORS)


def free_spot(F_, xs, d, r):
    """The first of the places xs along the front (d out from it) that is clear of the doors, or None."""
    for x in xs:
        if clear_of_doors(F_.at(x, d, 0), r):
            return x
    return None


def cafe_terrace(F_, mid, count, rng, name):
    """Tables and chairs set out close in front of a café, side by side, ready for people to sit down
    (the entrance in the middle is left clear)."""
    # either side of the door, which is left clear: 1.5 m out from it, then every 2 m
    xs = [mid - 1.5 - 2.0 * k for k in range((count + 1) // 2)] + [mid + 1.5 + 2.0 * k for k in range(count // 2)]
    for j, x in enumerate(xs):
        x = free_spot(F_, (x, x + (0.9 if x > mid else -0.9)), 1.25, 0.9)
        if x is None:
            continue                                # (no room for this table: it would stand in a doorway)
        p = F_.at(x, 1.25, KERB)
        if not crossing_clear(p.x / T, -p.y / T, 0.45):
            continue                                # (round 33: not set out in front of a crossing)
        meshy_place('cafe.glb', 7000, 'base', 2.4, p, F_.ang + rng.uniform(-0.25, 0.25), '%s_%d' % (name, j), 1024)
        scene['obstacles'].append({'pos': bl_m(p), 'off': [0, 0], 'r': 1.0})
        keep_clear(p, 1.6)


ABOARD_WORDS = {'books': ('LLIBRES', 'second-hand books', "A chalkboard: 'LLIBRES — second-hand books, new arrivals every week. Come in and browse!'"),
                'bakery': ('FORN DE PA', 'croissants · cafè', "A chalkboard: 'FORN DE PA — fresh croissants, coca de vidre and coffee from seven.'"),
                'ice': ('GELATS', 'turrón · xocolata', "A chalkboard: 'GELATS ARTESANS — today: turrón, dark chocolate, lemon sorbet.'")}


def aboard(mb, F_, s0, d0, kind):
    """A folding chalkboard sign: two wooden-framed boards leaning together, chalk lettering on both faces."""
    wood, chalk, ink = mat('AboardWood', '#7a5236', 0.8), mat('AboardSlate', '#28332d', 0.9), mat('ChalkInk', '#f1ede2', 0.95)
    hw, H, spread, top = 0.27, 0.86, 0.22, 0.03
    tilt = math.atan2(spread - top, H)
    N2 = Vector((F_.n[0], F_.n[1], 0))
    U2 = Vector((F_.u[0], F_.u[1], 0))
    for side in (1, -1):
        def P(a, z, off=0.0, inset=0.0):
            d = d0 + side * (spread - (spread - top) * z / H)
            return F_.at(s0, d, KERB + z) + U2 * a + (N2 * side * math.cos(tilt) + Vector((0, 0, math.sin(tilt)))) * off
        nrm = N2 * side * math.cos(tilt) + Vector((0, 0, math.sin(tilt)))
        mb.face([P(-hw, 0.02), P(hw, 0.02), P(hw, H), P(-hw, H)], wood, normal=tuple(nrm))
        mb.face([P(-hw, 0.02, -0.02), P(-hw, H, -0.02), P(hw, H, -0.02), P(hw, 0.02, -0.02)], wood, normal=tuple(-nrm))
        mb.face([P(-hw + 0.035, 0.12, 0.004), P(hw - 0.035, 0.12, 0.004), P(hw - 0.035, H - 0.035, 0.004), P(-hw + 0.035, H - 0.035, 0.004)],
                chalk, normal=tuple(nrm))
        rz = facing((F_.n[0] * side, F_.n[1] * side))
        for (txt, z, size) in ((ABOARD_WORDS[kind][0], 0.66, 0.075), (ABOARD_WORDS[kind][1], 0.47, 0.045)):
            ob = text_obj(txt, size, ink, P(0, z, 0.008), rz, 'SignText_aboard_%d' % len(city_objs))
            ob.rotation_euler = (math.pi / 2 - tilt, 0, rz)
            city_objs.append(ob)
    mb.box(F_.at(s0, d0, KERB + H + 0.02), F_.u, F_.n, hw, top + 0.02, 0.025, wood)        # the hinge rail on top
    p = F_.at(s0, d0, 0)
    scene['obstacles'].append({'pos': bl_m(p), 'off': [0, 0], 'r': 0.35})
    scene.setdefault('things2d', []).append({'type': 'sign', 'pos': bl_m(p), 'text': ABOARD_WORDS[kind][2], 'id': '', 'h': 0.12,
                                             'landmark': ''})


def signs_and_wares(extras, mb, cards, rng, sandra=False):
    """Shop signs and house numbers, and what each trade puts out on the pavement (not every shop
    does: house['shop']['wares'])."""
    bikes = []
    for k, e in enumerate(extras):
        if e[0] == 'text':
            _, F_, p, text, size, m = e
            city_objs.append(text_obj(text, size, m, p, facing(F_.n), 'KitText_%d' % len(city_objs)))
            continue
        _, F_, house, a, b = e
        kind = house['shop']['kind']
        if house['shop'].get('closed'):
            continue
        mid = (a + b) / 2
        if kind == 'bar' and os.path.exists(meshy_file('cafe.glb')):
            cafe_terrace(F_, mid, 2 if house.get('corner') else rng.choice((2, 3)), rng, 'KitCafe_%d' % len(city_objs))
            continue
        if not house['shop'].get('wares', True):
            continue
        if kind == 'bikes':
            # (round 38, the user: "the two bikes in front of his shop are overlapping each other. There's more than
            # enough space away from the door under the awnings… place something… like a small workbench… up against
            # the wall. And then maybe the two bikes are facing the wall… make it look like he's doing something on the
            # pavement outside") a workbench with its tools against the wall, then the bikes side by side, their front
            # wheels to the wall, under the awning and clear of the door; the pavement there is his (rule 07 #14)
            n_ = F_.n
            yaw = math.atan2(n_[0], -n_[1])                     # (facing the wall)
            bench = free_spot(F_, [a + 0.75 + 0.1 * k for k in range(int((b - a) * 10))], 0.35, 0.75)
            x_ = a + 0.2
            if bench is not None:
                F_.box(mb, bench, 0.32, KERB + 0.84, 0.65, 0.3, 0.03, M_CRATE)                 # its top
                F_.box(mb, bench, 0.32, KERB + 0.25, 0.6, 0.27, 0.02, M_CRATE)                 # the shelf under it
                for (ls, ld) in ((-0.6, 0.06), (0.6, 0.06), (-0.6, 0.58), (0.6, 0.58)):
                    F_.box(mb, bench + ls, ld, KERB + 0.41, 0.03, 0.03, 0.41, M_IRON)           # its legs
                F_.box(mb, bench - 0.45, 0.4, KERB + 0.93, 0.07, 0.09, 0.06, M_IRON)           # a vice
                F_.box(mb, bench + 0.3, 0.3, KERB + 0.95, 0.2, 0.11, 0.08, M_TOOLBOX)          # the red toolbox
                F_.box(mb, bench - 0.1, 0.45, KERB + 0.88, 0.12, 0.02, 0.01, M_IRON)           # a spanner on the top
                F_.box(mb, bench, 0.025, KERB + 1.45, 0.62, 0.012, 0.3, M_CRATE)               # the tool board on the wall
                for k in range(5):
                    F_.box(mb, bench - 0.45 + k * 0.22, 0.045, KERB + 1.42 + (k % 2) * 0.06, 0.012, 0.012, 0.16, M_IRON)
                F_.box(mb, bench + 0.15, 0.32, KERB + 0.4, 0.22, 0.2, 0.13, M_CRATE)           # a crate of parts on the shelf
                for ds in (-0.35, 0.35):
                    scene['obstacles'].append({'pos': bl_m(F_.at(bench + ds, 0.32, 0)), 'off': [0, 0], 'r': 0.42})
                keep_clear(F_.at(bench, 0.35, 0), 0.8)
                x_ = bench + 0.65 + 0.45
            cols = [('#e8dcc0', '#c9a24a', True), ('#3a5a8a', '#efe6d2', False)]      # (the user's "two bikes")
            j = 0
            while j < len(cols) and x_ < b - 0.2:
                p = F_.at(x_, 1.0, 0)
                if clear_of_doors(p, 0.9) and clear_of_doors(F_.at(x_, 0.3, 0), 0.9):          # (well clear of the door)
                    fc, gc, basket = cols[j]
                    keep_clear(p, 0.5)
                    bikes.append({'pos': bl_m(p), 'yaw': round(yaw, 3), 'frame': fc, 'guard': gc,
                                  'basket': basket, 'flowers': basket, 'rack': True})
                    j += 1
                    x_ += 1.15                                  # (side by side, a clear gap between them)
                else:
                    x_ += 0.1
        elif kind == 'flowers':
            for j in range(5):
                x = a + 0.5 + j * 0.42
                p = F_.at(x, 0.45 + (j % 2) * 0.25, KERB + 0.2)
                if not clear_of_doors(F_.at(x, 0.45 + (j % 2) * 0.25, 0), 0.25):
                    continue                        # (the buckets of flowers stand clear of the doors: round 21)
                mb.cone(Matrix.Translation(p), 10, 0.15, 0.12, 0.4, M_BUCKET)
                cards.clump(p + Vector((0, 0, 0.45)), (0.25, 0.25, 0.25), 7, 0.4, [M_GERANIUM_CARD, M_PINK, M_DAISY, M_BOUG, M_PINK][j], rng)
                # (round 33, the user: nothing she runs through — one solid spot for the stall used to stand at its
                # middle, and only when that was clear of the doors: buckets beside a door were walked through)
                scene['obstacles'].append({'pos': bl_m(F_.at(x, 0.45 + (j % 2) * 0.25, 0)), 'off': [0, 0], 'r': 0.3})
        elif kind == 'fruit':
            mid = free_spot(F_, (a + (b - a) * 0.78, a + (b - a) * 0.22), 0.55, 1.4)   # in front of a window, not a doorway
            if mid is None:
                continue
            x0 = mid - 1.3
            F_.box(mb, mid, 0.55, KERB + 0.35, 1.35, 0.35, 0.35, M_CRATE)
            for j in range(6):
                cx = x0 + 0.22 + j * 0.44
                F_.box(mb, cx, 0.55, KERB + 0.76, 0.2, 0.3, 0.06, M_CRATE)
                fm = M_FRUIT[j % len(M_FRUIT)]
                for q in range(7):
                    mb.sphere(Matrix.Translation(F_.at(cx + rng.uniform(-0.13, 0.13), 0.55 + rng.uniform(-0.2, 0.2), KERB + 0.86)),
                              0.05, fm, (8, 6))
            for dx_ in (-0.9, 0.0, 0.9):                  # (round 33: the whole 2.7 m stand, not just its middle)
                scene['obstacles'].append({'pos': bl_m(F_.at(mid + dx_, 0.55, 0)), 'off': [0, 0], 'r': 0.7})
        elif kind in ('books', 'bakery', 'ice'):
            # a chalkboard A-frame on the pavement, chalked on both sides, solid, and read with E
            ab = free_spot(F_, (mid + 1.4, mid - 1.4, mid + 2.2), 0.9, 0.4)
            if ab is not None:
                aboard(mb, F_, ab, 0.9, kind)
            if kind == 'books' and clear_of_doors(F_.at(mid - 1.0, 0.45, 0), 0.7):
                F_.box(mb, mid - 1.0, 0.45, KERB + 0.4, 0.55, 0.28, 0.4, frame_mat('#6b4a33'))
                for j in range(9):
                    F_.box(mb, mid - 1.45 + j * 0.11, 0.45, KERB + 0.92, 0.045, 0.2, rng.uniform(0.1, 0.14),
                           mat('Book%d' % (j % 6), ['#8a3a32', '#2f5a7a', '#c9a24a', '#3e6b4a', '#6a4a7a', '#d8cbb0'][j % 6], 0.8))
                scene['obstacles'].append({'pos': bl_m(F_.at(mid - 1.0, 0.45, 0)), 'off': [0, 0], 'r': 0.6})
    LIFE_BIKES.extend(bikes)
    if not sandra:
        return
    life = scene.setdefault('street_life', {})
    LIFE_BIKES.insert(0, {'pos': [12.4, 31.5], 'yaw': 1.45, 'frame': '#2f6b5a'})
    life['montse'] = [23.39, 31.6, 0.0]                               # on the bench outside Sandra's building, well onto the seat
    c = (HOME[0] + BS / 2 + 1.0, HOME[1] + BS / 2 + 0.35)
    life['trufa_lost'] = to_m(c)                                       # sniffing about in the courtyard garden



def mallorca_bins():
    """Recycling bins on Carrer de Mallorca, along Sandra's block: a bay of two in each gap between the
    street trees (run after the trees are planted)."""
    mb, cards = MB(uv=True), Cards()
    trees = sorted(t[0] for t in scene['trees'] if abs(t[1] - (-0.75 * T)) < 0.4 and 0 < t[0] < BS * T)
    pairs = [(1, 2), (0, 3), (4, 1)]                  # packaging + paper, glass + general, organic + packaging
    for k, (a, b) in enumerate(zip(trees, trees[1:])):
        if b - a < 3.9:
            continue
        x = (a + b) / 2
        bin_bay(mb, cards, Vector((x, 0.75 * T, KERB)), (1, 0), (0, 1), pairs[k % len(pairs)], random.Random(k))
        for sx in (-0.95, 0.0, 0.95):
            scene['obstacles'].append({'pos': [round(x + sx, 3), -0.75 * T], 'off': [0, 0], 'r': 0.55})
    city_objs.append(mb.finish('HomeBins'))
    city_objs.append(cards.finish('Plants_bins'))


def garden(cards, mb, inner, rng):
    """The interior of the block: gravel paths, four lawns, a fountain, trees, benches and lamps."""
    ox, oy = HOME
    c = (ox + BS / 2, oy + BS / 2)
    z = KERB + 0.015
    mb.face([B(*p, z) for p in inner], M_GRAVEL, normal=(0, 0, 1), uvscale=2.5)
    lo, hi = ox + COURT + 0.32, ox + BS - COURT - 0.32
    gap = 0.46                                                        # half width of the cross paths (tiles)
    for (x0, x1) in ((lo, c[0] - gap), (c[0] + gap, hi)):
        for (y0, y1) in ((lo, c[1] - gap), (c[1] + gap, hi)):
            mb.face([B(x0, y0, z + 0.02), B(x1, y0, z + 0.02), B(x1, y1, z + 0.02), B(x0, y1, z + 0.02)], M_GRASS, normal=(0, 0, 1), uvscale=3.0)
            for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
                pa, pb = B(*a, z + 0.06), B(*b, z + 0.06)
                d = pb - pa
                mb.box((pa + pb) / 2, (d.x / d.length, d.y / d.length), (-d.y / d.length, d.x / d.length), d.length / 2, 0.05, 0.06, M_STONE)
            # flowers along the inner corner of each lawn
            fc = B(x0 + (x1 - x0) * (0.85 if x0 > c[0] - 1 else 0.15), y0 + (y1 - y0) * (0.85 if y0 > c[1] - 1 else 0.15), z + 0.3)
            cards.clump(fc, (0.7, 0.7, 0.2), 12, 0.5, rng.choice((M_GERANIUM_CARD, M_PINK, M_DAISY)), rng)
    # fountain
    fc = B(*c)
    mb.cone(Matrix.Translation(fc + Vector((0, 0, z + 0.22))), 28, 1.15, 1.1, 0.44, M_STONE)
    mb.cone(Matrix.Translation(fc + Vector((0, 0, z + 0.405))), 28, 1.0, 1.0, 0.02, M_WATER)
    mb.cone(Matrix.Translation(fc + Vector((0, 0, z + 0.85))), 10, 0.12, 0.16, 0.9, M_STONE)
    mb.cone(Matrix.Translation(fc + Vector((0, 0, z + 1.32))), 18, 0.45, 0.18, 0.12, M_STONE)
    mb.cone(Matrix.Translation(fc + Vector((0, 0, z + 1.37))), 18, 0.4, 0.4, 0.015, M_WATER)
    scene['obstacles'].append({'pos': to_m(c), 'off': [0, 0], 'r': 1.5})
    scene['fountain'] = to_m(c)
    # trees: two plane trees and two orange trees
    plane_tree(c[0] + 1.15, c[1] - 1.15)
    plane_tree(c[0] - 1.15, c[1] + 1.15)
    for (tx, ty) in ((c[0] - 1.15, c[1] - 1.15), (c[0] + 1.15, c[1] + 1.15)):
        base = B(tx, ty, KERB)
        mb.cone(Matrix.Translation(base + Vector((0, 0, 0.9))), 7, 0.1, 0.07, 1.8, M_BARK)
        crown = Cards()
        crown.clump(base + Vector((0, 0, 2.3)), (0.8, 0.8, 0.6), 14, 0.7, M_CITRUS, rng)
        crown.shell(base + Vector((0, 0, 2.3)), (1.15, 1.15, 0.95), 60, 0.75, M_CITRUS, rng)
        city_objs.append(crown.finish('Leaves_orange_%d' % len(scene['trees'])))
        scene['trees'].append(to_m((tx, ty)))
    # benches facing the fountain, lamps in two corners
    if os.path.exists(meshy_file('bench.glb')):
        for (bx, by, rot) in ((c[0], c[1] - 0.82, 0.0), (c[0] - 0.82, c[1], math.pi / 2), (c[0] + 0.82, c[1], -math.pi / 2)):
            meshy_place('bench.glb', 12000, 'base', 1.05, B(bx, by, z), rot, 'GardenBench', 1024)
            scene['obstacles'].append({'pos': to_m((bx, by)), 'off': [0, 0], 'r': 0.7})
    for (lx, ly) in ((lo + 0.15, lo + 0.15), (hi - 0.15, hi - 0.15)):
        d = (c[0] - lx, c[1] - ly)
        L = math.hypot(*d)
        lamp_post(lx, ly, (d[0] / L, -d[1] / L))
    # shrubs along the foot of the walls
    for k in range(len(inner)):
        a, b = inner[k], inner[(k + 1) % len(inner)]
        L = math.dist(a, b)
        if L < 1.0:
            continue
        u, n, _ = edge_frame(a, b)
        for s in [x / 4 for x in range(1, int(L * 4))]:
            if rng.random() < 0.35:
                p = lerp2(a, b, s / L)
                cards.clump(B(*p, KERB + 0.45) - Vector((n[0], n[1], 0)) * 0.45, (0.55, 0.55, 0.42), 12, 0.55, rng.choice((M_SHRUB, M_SHRUB, M_IVY)), rng)
