# (round 26) Stone in textures, for the Sagrat Cor outside (north_build.py) and in (sagrat_inside.py): coursed blocks
# with mortar, flagstones, little square mosaic tiles; and box UVs in metres so a texture keeps its size on every face.
# Exec'd into the build's globals (needs bpy, mat). The user's picks (round 26, from builder/church_options.py's
# pictures): "B for brown bricks and C for white. Base is brown bricks": the crypt (the base) in B's warm Montjuïc
# blocks, the upper church in C's pale stone.
import numpy as np


def st_noise(h, w, cells, seed):
    """Tileable value noise, h x w, with cells x cells random values, smoothly interpolated (0..1)."""
    r = np.random.RandomState(seed).rand(cells[0], cells[1])
    y = np.arange(h) * cells[0] / h
    x = np.arange(w) * cells[1] / w
    y0, x0 = np.floor(y).astype(int), np.floor(x).astype(int)
    fy, fx = y - y0, x - x0
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    y1, x1 = (y0 + 1) % cells[0], (x0 + 1) % cells[1]
    a = r[y0][:, x0] * (1 - fx) + r[y0][:, x1] * fx
    b = r[y1][:, x0] * (1 - fx) + r[y1][:, x1] * fx
    return a * (1 - fy)[:, None] + b * fy[:, None]


def st_blocks(W, H, ppm, course, length, mortar, base, mortar_col, var, edge, rough, weather, seed, stagger=0.5):
    """Coursed stone blocks, tiling, W x H metres at ppm pixels a metre (rows from the bottom, as Blender's images).
    course/length: (min, max) metres; mortar: the joint's width; var: how much one block differs from the next;
    edge: darker rounded block edges (0..1); rough: grain; weather: the foot darker (0..1, over its first metre)."""
    rnd = random.Random(seed)
    w, h = int(W * ppm), int(H * ppm)
    hs = []
    while sum(hs) < H - course[0]:
        hs.append(rnd.uniform(*course))
    hs = [x * H / sum(hs) for x in hs]
    tone = np.zeros((h, w))
    dist = np.full((h, w), 9.0)
    y_m = (np.arange(h) + 0.5) / ppm
    x_m = (np.arange(w) + 0.5) / ppm
    y0 = 0.0
    for ci, ch in enumerate(hs):
        rows = (y_m >= y0) & (y_m < y0 + ch)
        ls = []
        while sum(ls) < W - length[0]:
            ls.append(rnd.uniform(*length))
        ls = [x * W / sum(ls) for x in ls]
        off = rnd.uniform(0, W) if stagger is None else (ci * stagger * ls[0] + rnd.uniform(-0.2, 0.2)) % W
        xs = (x_m - off) % W
        k = np.searchsorted(np.cumsum(ls), xs, side='right')
        starts = np.concatenate([[0.0], np.cumsum(ls)])
        dx = np.minimum(xs - starts[k], starts[k + 1] - xs)
        dy = np.minimum(y_m[rows] - y0, y0 + ch - y_m[rows])
        tones = np.array([rnd.uniform(-1, 1) for _ in ls])
        tone[rows] = tones[k][None, :]
        dist[rows] = np.minimum(dx[None, :], dy[:, None])
        y0 += ch
    n1 = st_noise(h, w, (int(H * 3), int(W * 3)), seed + 1)
    n2 = st_noise(h, w, (int(H * 14), int(W * 14)), seed + 2)
    n3 = np.random.RandomState(seed + 3).rand(h, w)
    k = 1 + var * tone + rough * ((n1 - 0.5) * 0.6 + (n2 - 0.5) * 0.5 + (n3 - 0.5) * 0.25)
    if edge:
        e = np.clip(dist / 0.07, 0, 1)
        k *= 1 - edge * (1 - e) ** 2
    img = np.array(base)[None, None, :] * k[:, :, None]
    joint = dist < mortar / 2
    jn = 1 + 0.08 * (n2 - 0.5)
    img[joint] = np.array(mortar_col)[None, :] * jn[joint][:, None]
    if weather:
        f = 1 - weather * np.exp(-y_m / 0.7)[:, None] * (0.75 + 0.5 * n1)
        img *= f[:, :, None]
    return np.clip(img, 0, 1)


def st_tesserae(S, ppm, palette, grout, seed):
    """A flat mosaic of little square tiles (2.5 cm), S metres a side, tiling."""
    rnd = np.random.RandomState(seed)
    n = int(S / 0.025)
    w = int(S * ppm)
    cell = w / n
    yy, xx = np.mgrid[0:w, 0:w]
    iy = (yy / cell).astype(int) % n
    ix = ((xx + (iy % 2) * cell * 0.3) / cell).astype(int) % n
    pick = rnd.randint(0, len(palette), (n, n))
    shade = 1 + rnd.uniform(-0.08, 0.08, (n, n))
    col = np.array(palette)[pick[iy, ix]] * shade[iy, ix][:, :, None]
    fy = (yy / cell) % 1.0
    fx = ((xx + (iy % 2) * cell * 0.3) / cell) % 1.0
    col[(fy < 0.1) | (fx < 0.1)] = grout
    return col


def st_image(name, arr):
    h, w, _ = arr.shape
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.pixels.foreach_set(np.concatenate([arr, np.ones((h, w, 1))], axis=2).astype(np.float32).ravel())
    img.file_format = 'PNG'
    img.pack()
    return img


def st_hex(hx):
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))


# the pictures (made once a build): name -> (array, tile size x, y in metres)
_ST = {}


def st_pictures():
    if _ST:
        return _ST
    crypt = st_blocks(4.0, 12.0, 96, (0.32, 0.55), (0.55, 1.2), 0.025, st_hex('#c6a073'),
                      tuple(v * 0.8 for v in st_hex('#cdbfa6')), 0.1, 0.25, 0.22, 0.2, 11)              # B: the crypt
    upper = st_blocks(4.0, 4.0, 96, (0.4, 0.5), (0.8, 1.3), 0.016, st_hex('#ece4d2'),
                      tuple(v * 0.7 for v in st_hex('#ddd5c4')), 0.07, 0.15, 0.14, 0.0, 21)           # C: the church above
    flags = st_blocks(4.0, 4.0, 64, (0.8, 0.8), (0.8, 1.2), 0.02, st_hex('#e6dac2'), st_hex('#bdb19a'),
                      0.08, 0.05, 0.12, 0.0, 31)                                                     # the terrace
    gold = st_tesserae(0.5, 512, [st_hex(c) for c in ('#d7a640', '#c99a3a', '#e2b955', '#b8862e')], st_hex('#9c8a6a'), 41)
    blue = st_tesserae(0.5, 512, [st_hex(c) for c in ('#3f63a8', '#35579a', '#4d72b6', '#2e4c8c')], st_hex('#8a8f9a'), 42)
    _ST.update(crypt=(crypt, 4.0, 12.0), crypt_dark=(crypt * 0.86, 4.0, 12.0), upper=(upper, 4.0, 4.0),
               upper_dark=(upper * 0.9, 4.0, 4.0), flags=(flags, 4.0, 4.0), gold=(gold, 0.5, 0.5), blue=(blue, 0.5, 0.5))
    return _ST


ST_MATS = {}


def st_mat(key, rough=0.9, metal=0.0):
    """A material wearing one of the pictures (made once)."""
    if key not in ST_MATS:
        arr = st_pictures()[key][0]
        ST_MATS[key] = mat('Stone_' + key, '#ffffff', rough, metal, image=st_image('stone_' + key, arr))
    return ST_MATS[key]


def st_size(key):
    return st_pictures()[key][1:]


def box_uvs(ob, rules):
    """UVs in metres by each face's facing, for the faces wearing the materials named in rules:
    rules[material name] = (picture width, height in metres, the height its foot is at)."""
    me = ob.data
    uvl = me.uv_layers.active or me.uv_layers.new(name='UVMap')
    M = ob.matrix_world
    for poly in me.polygons:
        mn = me.materials[poly.material_index].name
        if mn not in rules:
            continue
        sx, sy, z0 = rules[mn]
        n = poly.normal
        for li in poly.loop_indices:
            p = M @ me.vertices[me.loops[li].vertex_index].co
            if abs(n.z) > 0.7:
                u, v = p.x / sx, p.y / sy
            else:
                t = Vector((-n.y, n.x, 0)).normalized()
                u, v = p.dot(t) / sx, (p.z - z0) / sy
            uvl.data[li].uv = (u, v)


def st_dress(ob, swaps):
    """Puts textured stone on an object built with plain materials: swaps[plain material name] = (picture key, the
    height its foot is at, roughness, metal). Box UVs first, then the swap."""
    rules = {}
    for mn, (key, z0, *_r) in swaps.items():
        rules[mn] = st_size(key) + (z0,)
    box_uvs(ob, rules)
    for i, m in enumerate(ob.data.materials):
        if m is not None and m.name in swaps:
            key, z0, *rm = swaps[m.name]
            ob.data.materials[i] = st_mat(key, *rm)
