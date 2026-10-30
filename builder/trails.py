# Worn paths through the woods (round 24): the ribbons of earth or gravel laid over the ground, used by the eastern
# wood (forest.py) and the path up the hill (north_build.py). exec'd into build_assets.py's globals (MB, mat, V-style
# points, numpy); everything here is in the engine's metres (x east, z south), with a height function for the ground.
#
# The user (round 24): "third from the top [round 23's option B, the ragged edge breaking into islands], but thinner,
# as if people have walked along it and worn it down over time, with a different texture, more like a normal path. The
# joins need small curved corners, because people don't walk at right angles. Two different options going in
# different directions. Then one gravel, a bit wider than the dirt path." Real paths (looked up): a footpath worn by
# feet is bare, compacted earth, narrow (well under a metre and a half), darkest and smoothest along the line feet
# actually take, fraying at its edges into tufts and bare patches; at junctions people cut the corners, wearing them
# round. A woodland gravel walk is fine crushed stone, compacted, a little crowned, about a metre to a metre and a half
# wide (two people pass), with a crisper edge and a few loose stones kicked out into the verge.
#   'D1'  a sunny, dusty track: pale ochre earth, a darker trodden line down its middle, small stones at its sides;
#         its edge breaks up into bare islands in the grass (round 23's B, finer)
#   'D2'  a shady woodland path: darker, damper brown earth, leaf litter drifting in from both sides, a root across it
#         now and then; its edge softened by litter
#   'G'   gravel: pale grey-beige crushed stone, a smooth crown, a crisp edge with a few stones scattered past it
import numpy as np

TRAIL_STYLES = {
    'D1': {'scale': 0.62, 'min': 0.7, 'out': 0.45, 'edge_in': 0.22, 'name': 'sunny worn track', 'elen': 12.0},
    'D2': {'scale': 0.56, 'min': 0.65, 'out': 0.4, 'edge_in': 0.22, 'name': 'shady woodland path'},
    'G': {'scale': 0.85, 'min': 0.95, 'out': 0.25, 'edge_in': 0.12, 'name': 'gravel walk'},
}
CORE_LEN = 8.0          # metres of path to one repeat of the core's picture (u along, v across)
EDGE_LEN = 4.0          # and of the edge's
FILLET_R = 0.85         # the curved corners where paths meet (metres)
JOIN_CALM = 3.0         # (round 40) metres round a join over which a path's width stops breathing: its edges there
                        # are the straight-sided ones the rounded corners are worked out from (no slivers, no hooks)
LOW_STEP = 0.012        # (round 40) a lesser path (another style) lies this much lower than the main one: below even
                        # the main path's ragged edge band (0.03), so the main path's own edge is the only edge seen
ARM_REACH = 9.0         # metres of each path's edge looked along to fit a rounded corner (acute joins need more)
if 'DRAWN_BUCKETS' not in globals():
    DRAWN_BUCKETS = {}  # (round 40) every ribbon laid, any world: points along its middle, each with its outer half width
KEEP_OFF = 0.3          # (round 40, PATH_RULES A5) planting stands at least this far off any path's drawn edge
REACH = {'G': 0.05, 'D1': 0.12, 'D2': 0.12}       # how far past its half width a path's own ground can show


def _noise(shape, seed, scale):
    """Smooth value noise (0..1), tiling, at roughly `scale` pixels to a blob."""
    h, w = shape
    r = np.random.default_rng(seed)
    gh, gw = max(2, int(h / scale)), max(2, int(w / scale))
    g = r.random((gh, gw))
    ys, xs = np.arange(h) * gh / h, np.arange(w) * gw / w
    y0, x0 = np.floor(ys).astype(int), np.floor(xs).astype(int)
    fy, fx = ys - y0, xs - x0
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = g[y0 % gh][:, x0 % gw]
    b = g[y0 % gh][:, (x0 + 1) % gw]
    c = g[(y0 + 1) % gh][:, x0 % gw]
    d = g[(y0 + 1) % gh][:, (x0 + 1) % gw]
    top = a * (1 - fx) + b * fx
    bot = c * (1 - fx) + d * fx
    return top * (1 - fy[:, None]) + bot * fy[:, None]


def _specks(shape, seed, density, size=1):
    r = np.random.default_rng(seed)
    m = r.random(shape) < density
    if size > 1:
        m = m | np.roll(m, 1, 1) | (np.roll(m, 1, 0) if size > 2 else m)
    return m


def _to_image(name, rgb, alpha=None):
    h, w = rgb.shape[:2]
    a = np.ones((h, w)) if alpha is None else alpha
    px = np.dstack([np.clip(rgb, 0, 1), a]).astype(np.float32)
    img = bpy.data.images.new(name, w, h, alpha=alpha is not None)
    img.pixels.foreach_set(px.ravel())
    img.file_format = 'PNG'
    try:
        img.pack()
    except Exception:
        pass
    return img


def core_image(style):
    """The path's own surface, u along (512 px = CORE_LEN), v across (128 px, one edge to the other)."""
    H, W = 128, 512
    v = (np.arange(H) + 0.5)[:, None] / H * np.ones((1, W))
    u = np.ones((H, 1)) * (np.arange(W) + 0.5)[None, :] / W
    n1, n2 = _noise((H, W), 11, 18), _noise((H, W), 12, 5)
    grain = np.random.default_rng(13).normal(0, 1, (H, W))
    mid = np.abs(v - 0.5) * 2                                       # 0 in the middle, 1 at the edges
    if style == 'D1':
        # the line feet take wanders a little; darker and smoother there, dusty and stony to the sides
        line = np.abs(v - 0.5 - 0.08 * np.sin(u * 2 * np.pi * 2 + 1.0)) * 2
        trod = np.clip(1 - line / 0.55, 0, 1) ** 1.5
        base = np.array([0.80, 0.68, 0.50])
        k = 1 + 0.07 * (n1 - 0.5) + 0.05 * (n2 - 0.5) + 0.025 * grain
        col = base[None, None, :] * (k * (1 - 0.18 * trod))[:, :, None]
        stones = _specks((H, W), 14, 0.012 + 0.03 * mid, 2) & (n2 > 0.35)
        col[stones] = col[stones] * 0.15 + np.array([0.86, 0.83, 0.76]) * 0.85
        crumbs = _specks((H, W), 15, 0.02 * mid)
        col[crumbs] *= 0.7
    elif style == 'D2':
        line = np.abs(v - 0.5 - 0.06 * np.sin(u * 2 * np.pi * 3 + 0.4)) * 2
        trod = np.clip(1 - line / 0.6, 0, 1)
        base = np.array([0.47, 0.40, 0.32])
        k = 1 + 0.1 * (n1 - 0.5) + 0.06 * (n2 - 0.5) + 0.03 * grain
        col = base[None, None, :] * (k * (1 - 0.12 * trod))[:, :, None]
        # leaf litter: little leaves, thicker towards the sides, a few across the middle
        r = np.random.default_rng(16)
        leafy = np.clip((mid - 0.35) / 0.65, 0, 1) ** 1.3 * 0.55 + 0.04
        cols = np.array([[0.62, 0.42, 0.20], [0.55, 0.47, 0.24], [0.44, 0.30, 0.16], [0.70, 0.55, 0.30]])
        for _ in range(2600):
            y, x = r.integers(0, H), r.integers(0, W)
            if r.random() > leafy[y, x]:
                continue
            c = cols[r.integers(0, 4)] * r.uniform(0.85, 1.1)
            ang = r.uniform(0, np.pi)
            for t in np.linspace(-3, 3, 9):
                yy, xx = int(y + t * np.sin(ang) * 0.6) % H, int(x + t * np.cos(ang) * 1.6) % W
                col[yy, xx] = c
        # two roots across it in the repeat, wandering, dark
        for (x0, slope, ph) in ((140, 0.9, 0.3), (395, -0.7, 1.9)):
            for y in range(H):
                xc = x0 + slope * (y - H / 2) * 0.6 + 6 * np.sin(y * 0.08 + ph)
                wdt = 5.5 - 2.5 * abs(y / H - 0.5)
                for x in range(int(xc - wdt), int(xc + wdt) + 1):
                    t = (x - xc) / (wdt + 0.5)                          # -1 .. 1 across the root
                    lit = 1.0 + 0.35 * max(0.0, 0.6 - abs(t + 0.35)) - 0.45 * max(0.0, t - 0.4)   # (lit along one side)
                    col[y, x % W] = np.array([0.45, 0.35, 0.25]) * lit
    else:
        # crushed stone: every pixel a stone, warm and cool greys, the crown in the middle smoother and lighter
        r = np.random.default_rng(17)
        tone = r.normal(0, 1, (H, W))
        base = np.array([0.69, 0.66, 0.59])
        k = 1 + 0.09 * tone + 0.05 * (n2 - 0.5) + 0.04 * (n1 - 0.5) + 0.05 * (1 - mid)
        col = base[None, None, :] * k[:, :, None]
        warm = r.random((H, W)) < 0.18
        col[warm] *= np.array([1.04, 0.98, 0.9])
        dark = _specks((H, W), 18, 0.05 + 0.05 * mid)
        col[dark] *= 0.62
        big = _specks((H, W), 19, 0.008 + 0.02 * mid, 3)
        col[big] = np.array([0.77, 0.75, 0.69]) * r.uniform(0.9, 1.05)
    return _to_image('trailcore_' + style, col)


def edge_image(style):
    """Where the path meets the grass: u along (256 px = EDGE_LEN), v across (64 px: 0 inside the path, 1 out in the
    grass). Alpha: the path's ground where there is some, nothing (the grass below shows) where there is not."""
    S = TRAIL_STYLES[style]
    # (round 25, the user: the hill's and the park's path edges were "too regular, there are regular boxes": D1's edge
    # now wanders by noise over 12 m before it repeats, and its bare islands are uneven blobs, not a grid of little
    # rectangles)
    H, W = (96, 768) if style == 'D1' else (64, 256)
    reach = S['edge_in'] + S['out']
    vm = (np.arange(H) + 0.5)[:, None] / H * reach - S['edge_in']        # metres past the path's edge (- inside)
    vm = vm * np.ones((1, W))
    xs = np.arange(W)[None, :] * np.ones((H, 1))
    tw = 2 * np.pi / W
    r = np.random.default_rng(ord(style[0]) * 7 + len(style))
    ph = r.uniform(0, 6.28, 4)
    n2 = _noise((H, W), 21, 4)
    grain = r.normal(0, 1, (H, W))
    if style == 'D1':
        wob = (0.2 * (_noise((1, W), 41, 40)[0] - 0.5) + 0.13 * (_noise((1, W), 42, 12)[0] - 0.5) +
               0.06 * (_noise((1, W), 43, 4)[0] - 0.5))[None, :] * np.ones((H, 1))
    elif style == 'G':
        wob = 0.025 * np.sin(xs * tw * 5 + ph[0]) + 0.015 * np.sin(xs * tw * 13 + ph[1])
    else:
        wob = 0.08 * np.sin(xs * tw * 3 + ph[0]) + 0.05 * np.sin(xs * tw * 7 + ph[1]) + 0.035 * np.sin(xs * tw * 17 + ph[2])
    d = wob - vm                                                           # metres inside the ragged edge
    a = (d > 0).astype(float)
    if style == 'D1':
        col = np.array([0.80, 0.68, 0.50])[None, None, :] * (1 + 0.05 * grain + 0.06 * (n2 - 0.5))[:, :, None]
        rim = (d > 0) & (d < 0.06)
        col[rim] *= 0.62                                                   # the sharp, darker lip where it cuts the turf
        # bare islands out in the grass, small, fewer further out, darker as they thin
        nb = 0.6 * _noise((H, W), 51, 6) + 0.3 * _noise((H, W), 52, 2.6) + 0.1 * r.random((H, W))
        isl = (d <= 0) & (nb > 0.78 - 0.3 * np.exp(d / 0.07) - 0.12 * (_noise((H, W), 53, 60) - 0.5))
        a[isl] = 1.0
        col[isl] = np.array([0.52, 0.42, 0.29]) * (1 + 0.06 * grain[isl])[:, None]
    elif style == 'D2':
        col = np.array([0.47, 0.40, 0.32])[None, None, :] * (1 + 0.06 * grain + 0.08 * (n2 - 0.5))[:, :, None]
        leaves = _specks((H, W), 22, 0.35, 2)
        lc = np.array([[0.58, 0.40, 0.19], [0.47, 0.43, 0.22], [0.40, 0.28, 0.15]])
        pick_ = np.random.default_rng(23).integers(0, 3, (H, W))
        col[leaves] = lc[pick_[leaves]]
        # litter drifts out over the grass's edge in soft scallops
        drift = (d <= 0) & (d > -0.18 * (0.5 + _noise((H, W), 24, 10))) & leaves
        a[drift] = 1.0
    else:
        col = np.array([0.69, 0.66, 0.59])[None, None, :] * (1 + 0.09 * grain + 0.05 * (n2 - 0.5))[:, :, None]
        col[(d > 0) & (d < 0.03)] *= 0.8                                   # (the stones' shadow along the verge)
        loose = (d <= 0) & _specks((H, W), 25, 0.06 * np.exp(np.minimum(d, 0) / 0.08), 2)
        a[loose] = 1.0
        col[loose] = np.array([0.74, 0.72, 0.66])
    # (round 41, the user: "a faint yellow line running through it. I think it's an artifact of the edge of the ground")
    # the picture repeats, so at its outer edge the filter blended in its inner rows — the path's own colour — and drew
    # a hairline along the ribbon's outer edge out in the grass: its last rows clear, and the strips map short of it
    a[-4:, :] = 0.0
    return _to_image('trailedge_' + style, col, a)


TRAIL_MATS = {}


def trail_mats(style):
    if style not in TRAIL_MATS:
        TRAIL_MATS[style] = (mat('TrailCore' + style, '#ffffff', 0.97 if style != 'G' else 0.92, image=core_image(style)),
                             mat('TrailEdge' + style, '#ffffff', 0.98, image=edge_image(style), alpha=True))
    return TRAIL_MATS[style]


def path_rows(pts, w, seed, taper=False, calm=()):
    """Rows along a path: (x, z, nx, nz, half width, u metres along), its width breathing a little as it goes —
    but not within JOIN_CALM of a join (calm: the joins' points), so the edges there are exactly where the
    rounded corners are fitted."""
    rows, u = [], 0.0
    r = random.Random(seed)
    ph = r.uniform(0, 6.28)
    for i in range(len(pts)):
        j0, j1 = max(0, i - 1), min(len(pts) - 1, i + 1)
        tx, tz = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
        L = math.hypot(tx, tz) or 1.0
        if i:
            u += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        b = 0.1 * math.sin(u * 0.45 + ph) + 0.06 * math.sin(u * 1.37 + 2 * ph)
        if calm:
            t = min(1.0, min(math.hypot(pts[i][0] - jx, pts[i][1] - jz) for (jx, jz) in calm) / JOIN_CALM)
            b *= t * t * (3 - 2 * t)
        hw = w / 2 * (1 + b)
        if taper:
            hw *= min(1.0, 0.5 + (len(pts) - 1 - i) * 0.025 * 3.3)          # (fuller where it leaves the path it joins)
        rows.append((pts[i][0], pts[i][1], -tz / L, tx / L, hw, u))
    return rows


def _strip(mb, rows, offs, zfn, lift, m, ulen, vs):
    """Quads between neighbouring rows across columns at offsets offs(hw) (metres from the middle), each point at the
    ground's height (zfn) plus lift, so the ribbon lies on the ground however it rises and falls."""
    prev = None
    for (x, z, nx, nz, hw, u) in rows:
        row = []
        for f in offs:
            o = f(hw)
            px, pz = x + nx * o, z + nz * o
            row.append(Vector((px, -pz, zfn(px, pz) + lift)))
        if prev is not None:
            for k in range(len(offs) - 1):
                q = [prev[0][k], prev[0][k + 1], row[k + 1], row[k]]
                uvs = [(prev[1] / ulen, vs[k]), (prev[1] / ulen, vs[k + 1]), (u / ulen, vs[k + 1]), (u / ulen, vs[k])]
                mb.face(q, m, normal=(0, 0, 1), uvs=uvs)
        prev = (row, u)


def chain_paths(paths, max_turn=1.1):
    """(round 40) Paths that run on from one another — one ends where the next begins (within 0.4 m), of the same
    style and width, turning less than max_turn (radians) there, no third path at that point — become one ribbon.
    Laid apart, their two square ends met at an angle and left a thin wedge of grass on the outside of the bend
    (Park Güell, map paths 2 -> 3 at (82, -183): the user's 'thin green wedge')."""
    P = [dict(p, pts=[tuple(q[:2]) for q in p['pts']]) for p in paths]

    def leave(pts, at_start):                       # the way a path goes from that end into itself
        a, b = (pts[0], pts[min(2, len(pts) - 1)]) if at_start else (pts[-1], pts[max(0, len(pts) - 3)])
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        return ((b[0] - a[0]) / L, (b[1] - a[1]) / L)

    def crowded(pt, skip):
        return any(k not in skip and any(math.hypot(q[0] - pt[0], q[1] - pt[1]) < Q['w'] * 0.9 for q in Q['pts'])
                   for k, Q in enumerate(P))
    again = True
    while again:
        again = False
        for i in range(len(P)):
            for j in range(len(P)):
                A, B = P[i], P[j]
                if (i == j or A.get('style') != B.get('style') or abs(A['w'] - B['w']) > 1e-6 or A.get('taper')
                        or B.get('taper') or A.get('round_end') or B.get('round_end') or len(A['pts']) < 2 or len(B['pts']) < 2):
                    continue
                for a_end in (True, False):
                    for b_start in (True, False):
                        pa = A['pts'][-1] if a_end else A['pts'][0]
                        pb = B['pts'][0] if b_start else B['pts'][-1]
                        if math.hypot(pa[0] - pb[0], pa[1] - pb[1]) > 0.4:
                            continue
                        da = leave(A['pts'], not a_end)
                        da = (-da[0], -da[1])               # (A's heading as it arrives)
                        db = leave(B['pts'], b_start)       # (B's heading as it leaves)
                        if math.acos(max(-1.0, min(1.0, da[0] * db[0] + da[1] * db[1]))) > max_turn or crowded(pa, {i, j}):
                            continue
                        ap = A['pts'] if a_end else A['pts'][::-1]
                        bp = B['pts'] if b_start else B['pts'][::-1]
                        P[i] = dict(A, pts=ap + bp[1:])
                        del P[j]
                        again = True
                        break
                    if again:
                        break
                if again:
                    break
            if again:
                break
    return P


def _seg_x(p, q, r, s):
    """Where segment p-q crosses segment r-s: (point, t along p-q) or None."""
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(d) < 1e-12:
        return None
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    v = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
    if 0 <= t <= 1 and 0 <= v <= 1:
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t), t
    return None


def _first_cross(A, B):
    """The first place (along A) polyline A crosses polyline B: (point, index in A, index in B) or None."""
    for ia in range(len(A) - 1):
        best = None
        for ib in range(len(B) - 1):
            h = _seg_x(A[ia], A[ia + 1], B[ib], B[ib + 1])
            if h and (best is None or h[1] < best[1]):
                best = (h[0], h[1], ib)
        if best:
            return best[0], ia, best[2]
    return None


def _foot(C, E):
    """The nearest point to C on polyline E, and the index of its segment."""
    best = (1e9, None, 0)
    for k in range(len(E) - 1):
        (ax, az), (bx, bz) = E[k], E[k + 1]
        dx, dz = bx - ax, bz - az
        L2 = dx * dx + dz * dz or 1e-12
        t = max(0.0, min(1.0, ((C[0] - ax) * dx + (C[1] - az) * dz) / L2))
        p = (ax + dx * t, az + dz * t)
        d = math.hypot(C[0] - p[0], C[1] - p[1])
        if d < best[0]:
            best = (d, p, k)
    return best[1], best[2]


def junction_fillets(built, junctions):
    """(round 40) The rounded corners where paths meet, fitted to the paths' real edges (curved or straight, at any
    angle): for each two neighbouring arms of a join, a circle of FILLET_R touching both edges (where the two edges,
    each pushed out by FILLET_R, cross), and the grass between the edges' crossing K and that circle filled.
    Returns [(K, polygon from K along one edge, round the arc, back along the other edge, arc points, style, low)]."""
    out = []
    for (jx, jz) in junctions:
        arms = []
        for B_ in built:
            rows = B_['rows']
            i = min(range(len(rows)), key=lambda k: (rows[k][0] - jx) ** 2 + (rows[k][1] - jz) ** 2)
            if math.hypot(rows[i][0] - jx, rows[i][1] - jz) > B_['w']:
                continue
            for step in (-1, 1):
                k, L = i, 0.0
                while 0 <= k + step < len(rows) and L < 2.5:
                    L += math.hypot(rows[k + step][0] - rows[k][0], rows[k + step][1] - rows[k][1])
                    k += step
                if L > 1.2:
                    dx, dz = rows[k][0] - jx, rows[k][1] - jz
                    n = math.hypot(dx, dz)
                    arms.append((math.atan2(dz, dx), dx / n, dz / n, B_, i, step))
        arms.sort(key=lambda a: a[0])
        for a, b in zip(arms, arms[1:] + arms[:1]):
            gap = (b[0] - a[0]) % (2 * math.pi)
            if not (0.08 < gap < 2.9) or a[3] is b[3] and a[5] == -b[5]:
                continue
            E, O = [], []
            for (ang, dx, dz, B_, i, step), toward in ((a, (-a[2], a[1])), (b, (b[2], -b[1]))):
                rows = B_['rows']
                side = 1 if rows[i][2] * toward[0] + rows[i][3] * toward[1] > 0 else -1
                e, o, k, L = [], [], i, 0.0
                while 0 <= k < len(rows) and L <= ARM_REACH:
                    x, z, nx, nz, hw, u = rows[k]
                    e.append((x + nx * hw * side, z + nz * hw * side))
                    o.append((x + nx * (hw + FILLET_R) * side, z + nz * (hw + FILLET_R) * side))
                    if 0 <= k + step < len(rows):
                        L += math.hypot(rows[k + step][0] - x, rows[k + step][1] - z)
                    k += step
                E.append(e)
                O.append(o)
            c = _first_cross(O[0], O[1])
            kx = _first_cross(E[0], E[1])
            if not c or not kx:
                continue
            C = c[0]
            Ta, ia = _foot(C, E[0])
            Tb, ib = _foot(C, E[1])
            K = kx[0]
            a0, a1 = math.atan2(Ta[1] - C[1], Ta[0] - C[0]), math.atan2(Tb[1] - C[1], Tb[0] - C[0])
            da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            n = max(4, int(abs(da) * FILLET_R / 0.15))
            arc = [(C[0] + FILLET_R * math.cos(a0 + da * s / n), C[1] + FILLET_R * math.sin(a0 + da * s / n)) for s in range(n + 1)]
            poly = [K] + E[0][kx[1] + 1:ia + 1] + arc + E[1][kx[2] + 1:ib + 1][::-1]
            lower = a[3] if a[3]['low'] >= b[3]['low'] else b[3]                 # (in the lesser path's ground)
            out.append((K, poly, arc, lower['st'], lower['low']))
    return out


def register_drawn(rows, reach, step=0.25):
    """(round 40) Note a laid ribbon for the planting: points every `step` metres along its middle with its outer
    half width (its half width there + how far its ground shows past it)."""
    for (x0, z0, _a, _b, h0, _u), (x1, z1, _c, _d, h1, _v) in zip(rows, rows[1:] + rows[-1:]):
        n = max(1, int(math.hypot(x1 - x0, z1 - z0) / step))
        for k in range(n):
            t = k / n
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            DRAWN_BUCKETS.setdefault((int(x // 2), int(z // 2)), []).append((x, z, h0 + (h1 - h0) * t + reach))


def path_edge_d(x, z):
    """(round 40) Metres from (x, z) to the drawn edge of the nearest path ribbon laid so far (negative: on it).
    Every planting asks this, so no plant stands on any path — the park's walks, gate paths and roads included."""
    best = 9.0
    bx, bz = int(x // 2), int(z // 2)
    for i in (bx - 1, bx, bx + 1):
        for j in (bz - 1, bz, bz + 1):
            for (px, pz, r) in DRAWN_BUCKETS.get((i, j), ()):
                d = math.hypot(x - px, z - pz) - r
                if d < best:
                    best = d
    return best


def round_end_rows(rows):
    """(Round 37, the user: "the path coming out of the forest should be rounded at the end") A path's rows shortened
    by its half width at the end, and the half circle that ends it there instead: (rows, (centre, along, half width)),
    the half circle's tip where the square end was."""
    hw = rows[-1][4]
    u_end = rows[-1][5]
    keep = [r for r in rows if r[5] <= u_end - hw] or rows[:1]
    if len(keep) < 2:
        keep = rows[:2]
    x, z, nx, nz, hw_, u = keep[-1]
    return keep, ((x, z), (nz, -nx), hw_, u)


def cap_rows(cap, ofs=0.0, n=8):
    """Rows round the half circle (centre, along, hw, u) for _strip: each from its centre, its 'across' pointing
    out along a radius, from the path's left edge round its tip to its right."""
    (cx, cz), (tx, tz), hw, u0 = cap
    rows = []
    for k in range(n + 1):
        a = math.pi / 2 - math.pi * k / n                  # +90° (left, the rows' +n side) through 0 (ahead) to -90°
        # the rows' n is (-tz, tx)
        dx, dz = tx * math.cos(a) - tz * math.sin(a), tz * math.cos(a) + tx * math.sin(a)
        rows.append((cx, cz, dx, dz, hw, u0 + hw * math.pi * k / n))
    return rows


def build_ribbons(paths, style, zfn, name, junctions=()):
    """Every path of `paths` ([{'pts': [(x, z)] metres, 'w': its width as built before round 24, 'taper': bool,
    'style': its own style, else `style`}]) as one object: first all their frayed edges (alpha), then all their cores on
    top, so where paths cross, a core always covers the other's edge; then the rounded corners where they meet (in
    `style`). (Round 25: paths of another style than `style` lie a few millimetres lower, so where a dirt spur
    leaves the gravel path the gravel is on top.)"""
    S0 = TRAIL_STYLES[style]
    mb = MB(uv=True)
    built = []
    paths = chain_paths(paths)                     # (round 40: paths that run on from one another are one ribbon)
    for pi, P in enumerate(paths):
        st = P.get('style', style)
        S = TRAIL_STYLES[st]
        w = max(S['min'], P['w'] * S['scale'])
        rows_ = path_rows(P['pts'], w, pi * 97 + 5, P.get('taper', False), calm=junctions)
        cap = None
        if P.get('round_end') and len(rows_) > 2:
            rows_, cap = round_end_rows(rows_)
        built.append(dict(P, w=w, st=st, low=0.0 if st == style else LOW_STEP, rows=rows_, cap=cap))
        register_drawn(rows_ + (cap_rows(cap) if cap else []), REACH[st])        # (round 40, A5: for the planting)
    for B_ in built:
        S = TRAIL_STYLES[B_['st']]
        ei, out = S['edge_in'], S['out']
        m_edge = trail_mats(B_['st'])[1]
        for sgn in (1, -1):
            _strip(mb, B_['rows'], [lambda hw: sgn * (hw - ei), lambda hw: sgn * (hw - ei + (ei + out) / 2), lambda hw: sgn * (hw + out)],
                   zfn, 0.03 - B_['low'], m_edge, S.get('elen', EDGE_LEN), [0.01, 0.5, 0.96])
        if B_['cap']:
            # the frayed edge on round the rounded end
            _strip(mb, cap_rows(B_['cap']), [lambda hw: hw - ei, lambda hw: hw - ei + (ei + out) / 2, lambda hw: hw + out],
                   zfn, 0.03 - B_['low'], m_edge, S.get('elen', EDGE_LEN), [0.01, 0.5, 0.96])
    m_core, m_edge = trail_mats(style)
    ei, out = S0['edge_in'], S0['out']
    fil = junction_fillets(built, junctions)
    for K, poly, arc, fst, flow in fil:
        # the corner's own frayed edge along its arc, outwards (away from K); (round 40) its ends sink in under the
        # paths' cores, so it fades into their own edges instead of ending as a hook in the grass
        Sf = TRAIL_STYLES[fst]
        ei_f, out_f = Sf['edge_in'], Sf['out']
        rows, u = [], 0.0
        for i, p in enumerate(arc):
            q0, q1 = arc[max(0, i - 1)], arc[min(len(arc) - 1, i + 1)]
            tx, tz = q1[0] - q0[0], q1[1] - q0[1]
            L = math.hypot(tx, tz) or 1.0
            nx, nz = -tz / L, tx / L
            if nx * (p[0] - K[0]) + nz * (p[1] - K[1]) < 0:
                nx, nz = -nx, -nz
            if i:
                u += math.hypot(p[0] - arc[i - 1][0], p[1] - arc[i - 1][1])
            rows.append((p[0], p[1], nx, nz, -(1.0 - math.sin(math.pi * i / (len(arc) - 1))) * (out_f + 0.12), u))
        _strip(mb, rows, [lambda hw: hw - ei_f, lambda hw: hw + out_f], zfn, 0.03 - flow, trail_mats(fst)[1],
               Sf.get('elen', EDGE_LEN), [0.01, 0.96])
        register_drawn([(p[0], p[1], 0, 0, 0.0, 0) for p in poly], REACH[fst])
    for B_ in sorted(built, key=lambda b: -b['low']):
        _strip(mb, B_['rows'], [lambda hw: -(hw - 0.08), lambda hw: -(hw - 0.08) / 2, lambda hw: 0.0, lambda hw: (hw - 0.08) / 2,
                                lambda hw: hw - 0.08], zfn, 0.04 - B_['low'], trail_mats(B_['st'])[0], CORE_LEN, [0.04, 0.27, 0.5, 0.73, 0.96])
        if B_['cap']:
            # the rounded end filled with the path's own ground: a fan from the last row's middle, its picture carried on
            (cx, cz), (tx, tz), hw, u0 = B_['cap']
            r_ = hw - 0.08
            lift = 0.04 - B_['low']

            def cpt(a):
                dx, dz = tx * math.cos(a) - tz * math.sin(a), tz * math.cos(a) + tx * math.sin(a)
                px, pz = cx + dx * r_, cz + dz * r_
                along, across = r_ * math.cos(a), r_ * math.sin(a)     # (across: + on the rows' n side, the core's v 0.96)
                return Vector((px, -pz, zfn(px, pz) + lift)), ((u0 + along) / CORE_LEN, 0.5 + across / r_ * 0.46)
            pc = Vector((cx, -cz, zfn(cx, cz) + lift))
            ring = [cpt(math.pi / 2 - math.pi * k / 10) for k in range(11)]
            for (p1, uv1), (p2, uv2) in zip(ring, ring[1:]):
                mb.face([pc, p1, p2], trail_mats(B_['st'])[0], normal=(0, 0, 1), uvs=[(u0 / CORE_LEN, 0.5), uv1, uv2])
    for K, poly, arc, fst, flow in fil:
        # (round 40) the corner filled with the lesser path's ground, from K along both real edges and round the arc
        mc_ = trail_mats(fst)[0]
        pK = Vector((K[0], -K[1], zfn(*K) + 0.04 - flow))
        for p, q in zip(poly[1:], poly[2:]):
            P1 = Vector((p[0], -p[1], zfn(*p) + 0.04 - flow))
            Q1 = Vector((q[0], -q[1], zfn(*q) + 0.04 - flow))
            mb.face([pK, P1, Q1], mc_, normal=(0, 0, 1),
                    uvs=[((K[0] + K[1]) / CORE_LEN, 0.2), ((p[0] + p[1]) / CORE_LEN, 0.05), ((q[0] + q[1]) / CORE_LEN, 0.05)])
    print('TRAILS %s %s: %d paths, %d rounded corners' % (name, style, len(built), len(fil)))
    return mb.finish(name)
