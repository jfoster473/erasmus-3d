# A quick 3D mock-up of round 22's north (north.py) for the user to agree before anything is built: the city as
# plain blocks (from scene.json), the Rambla's trees, the eastern wood, and the new hill with its funfair,
# winding path, cable car, Gràcia and Park Güell as simple shapes. Rendered from the game's own viewpoints.
#   Blender -b --factory-startup -P mock_north.py -- <out dir>
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import BUILD, OUT as WORLD_OUT
sys.path.insert(0, BUILD)
import north as N

OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else '/tmp/mock'
os.makedirs(OUT, exist_ok=True)
S = json.load(open(os.path.join(WORLD_OUT, 'scene.json')))
rng = random.Random(22)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene


def B(x, h, z):
    """engine (x, h, z) -> Blender"""
    return Vector((x, -z, h))


def mat(name, hexc, rough=0.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    c = tuple(int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    c = tuple(v ** 2.2 for v in c)
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*c, 1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = rough
    return m


M = {k: mat(k, v) for k, v in {
    'grass': '#7fa65a', 'hill': '#6f9a50', 'wood': '#3f6e3a', 'wood2': '#4d7d3f', 'path': '#d9c39a', 'stone': '#d8cbb0',
    'block': '#e2b07c', 'roof': '#c8673f', 'street': '#77737a', 'pave': '#cfc7ba', 'rambla': '#e7d8b8', 'trunk': '#6b4a35',
    'tree': '#5f9a45', 'sea': '#5fb4c0', 'sand': '#ecd9a6', 'red': '#c8392f', 'white': '#f4f1ea', 'orange': '#f08a2a',
    'pink': '#e8a6a0', 'cream': '#efe0bf', 'blue': '#4f8fc4', 'green2': '#58a06a', 'park': '#e3cfa4', 'gwall': '#c98a5e',
    'h1': '#e9c79a', 'h2': '#e6b8a6', 'h3': '#d9d0a8', 'h4': '#c9d3c4', 'h5': '#efd9b5', 'metal': '#555a60'}.items()}


class Mesh:
    def __init__(self, name):
        self.bm = bmesh.new()
        self.name = name
        self.mats = []

    def mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def face(self, pts, m):
        vs = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(vs)
        f.material_index = self.mi(m)
        return f

    def box(self, c, size, m, rot=0.0):
        hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
        cs, sn = math.cos(rot), math.sin(rot)
        P = []
        for dz in (-hz, hz):
            for dx, dy in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)):
                P.append(Vector((c[0] + dx * cs - dy * sn, c[1] + dx * sn + dy * cs, c[2] + dz)))
        for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.face([P[i] for i in q], m)

    def cyl(self, a, b, r, m, n=10, r2=None):
        a, b = Vector(a), Vector(b)
        ax = (b - a).normalized()
        t = ax.cross(Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))).normalized()
        u = ax.cross(t)
        r2 = r if r2 is None else r2
        ring = lambda c, rr: [c + (t * math.cos(2 * math.pi * k / n) + u * math.sin(2 * math.pi * k / n)) * rr for k in range(n)]
        A, Bv = ring(a, r), ring(b, r2)
        for k in range(n):
            self.face([A[k], A[(k + 1) % n], Bv[(k + 1) % n], Bv[k]], m)
        self.face(list(reversed(A)), m)
        self.face(Bv, m)

    def ball(self, c, r, m, sq=1.0, n=10):
        c = Vector(c)
        rings = []
        for j in range(n // 2 + 1):
            th = math.pi * j / (n // 2)
            rings.append([c + Vector((r * math.sin(th) * math.cos(2 * math.pi * k / n), r * math.sin(th) * math.sin(2 * math.pi * k / n),
                                      r * sq * math.cos(th))) for k in range(n)])
        for j in range(len(rings) - 1):
            for k in range(n):
                self.face([rings[j][k], rings[j + 1][k], rings[j + 1][(k + 1) % n], rings[j][(k + 1) % n]], m)

    def finish(self):
        me = bpy.data.meshes.new(self.name)
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=0.0005)
        self.bm.to_mesh(me)
        for m in self.mats:
            me.materials.append(m)
        for p in me.polygons:
            p.use_smooth = False
        ob = bpy.data.objects.new(self.name, me)
        scn.collection.objects.link(ob)
        return ob


# ------------------------------------------------------------------ the city, plainly
city = Mesh('City')
cr = S['city_rect']
city.face([B(cr[0], 0, cr[1]), B(cr[2], 0, cr[1]), B(cr[2], 0, cr[3]), B(cr[0], 0, cr[3])][::-1], M['street'])
for bl in S['blocks']:
    pave = [B(p[0], 0.15, p[1]) for p in bl['pave']]
    city.face(pave[::-1], M['pave'])
    poly = bl['poly']
    lo = [B(p[0], 0.15, p[1]) for p in poly]
    hi = [B(p[0], 19.0, p[1]) for p in poly]
    city.face(hi[::-1], M['roof'])
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        city.face([lo[i], lo[j], hi[j], hi[i]][::-1], M['block'])
# the Rambla's promenade and the ground round the city
xr0, xr1 = (34 - 55) * 3.3 + 2.0, (42 - 55) * 3.3 - 2.0
city.face([B(xr0, 0.2, cr[1]), B(xr1, 0.2, cr[1]), B(xr1, 0.2, cr[3]), B(xr0, 0.2, cr[3])][::-1], M['rambla'])
city.face([B(-260, -0.05, -95), B(220, -0.05, -95), B(220, -0.05, 140), B(-260, -0.05, 140)][::-1], M['grass'])
city.face([B(-260, -0.3, 140), B(220, -0.3, 140), B(220, -0.3, 420), B(-260, -0.3, 420)][::-1], M['sea'])
city.face([B(-260, -0.02, 128), B(220, -0.02, 128), B(220, -0.02, 150), B(-260, -0.02, 150)][::-1], M['sand'])
city.finish()

trees = Mesh('CityTrees')
for p in S['trees']:
    x, z = p[0], p[1]
    if cr[0] < x < cr[2] and cr[1] < z < cr[3]:
        trees.cyl(B(x, 0, z), B(x, 3.2, z), 0.18, M['trunk'], 6)
        trees.ball(B(x, 5.0, z), 2.3, M['tree'], 0.75, 8)
trees.finish()

wood = Mesh('Wood')
for i, p in enumerate(S['forest_trees']):
    if i % 3:
        continue
    x, z = p[0], p[1]
    wood.ball(B(x, 6.0, z), 3.0 + (i % 5) * 0.3, M['wood'] if i % 2 else M['wood2'], 0.9, 8)
wood.finish()

# ------------------------------------------------------------------ the new hill
X0, X1, Z0, Z1, ST = -240.0, 210.0, -470.0, -94.0, 3.0
nx, nz = int((X1 - X0) / ST), int((Z1 - Z0) / ST)
pts, L = N.path_points()


def near_path(x, z, r):
    return any((x - p[0]) ** 2 + (z - p[1]) ** 2 < r * r for p in pts[::3])


def near_line(x, z, line, r):
    for a, b in zip(line, line[1:]):
        ab = Vector((b[0] - a[0], b[1] - a[1]))
        t = max(0.0, min(1.0, (Vector((x - a[0], z - a[1])).dot(ab)) / ab.length_squared))
        if (Vector((x - a[0], z - a[1])) - ab * t).length < r:
            return True
    return False


def in_park(x, z, k=1.0):
    return ((x - N.PARK_C[0]) / N.PARK_R[0]) ** 2 + ((z - N.PARK_C[1]) / N.PARK_R[1]) ** 2 < k * k


def in_gracia(x, z):
    return 18 < x < 100 and -160 < z < -95 and not in_park(x, z)


def in_fair(x, z, m=0.0):
    f = N.FAIR
    return f[0] - m < x < f[2] + m and f[1] - m < z < f[3] + m


hill = Mesh('Hill')
H = [[N.height(X0 + i * ST, Z0 + j * ST) for i in range(nx + 1)] for j in range(nz + 1)]
for j in range(nz):
    for i in range(nx):
        x, z = X0 + (i + 0.5) * ST, Z0 + (j + 0.5) * ST
        q = [B(X0 + i * ST, H[j][i], Z0 + j * ST), B(X0 + (i + 1) * ST, H[j][i + 1], Z0 + j * ST),
             B(X0 + (i + 1) * ST, H[j + 1][i + 1], Z0 + (j + 1) * ST), B(X0 + i * ST, H[j + 1][i], Z0 + (j + 1) * ST)]
        m = M['stone'] if in_fair(x, z) else M['park'] if in_park(x, z, 0.92) else M['grass'] if in_gracia(x, z) else M['hill']
        hill.face(q, m)
hill.finish()

# the path, a ribbon on the ground
path = Mesh('Path')
for a, b in zip(pts, pts[1:]):
    d = Vector((b[0] - a[0], b[1] - a[1]))
    if d.length < 1e-4:
        continue
    n = Vector((-d.y, d.x)).normalized() * N.PATH_W / 2
    path.face([B(a[0] + n.x, a[2] + 0.25, a[1] + n.y), B(a[0] - n.x, a[2] + 0.25, a[1] - n.y),
               B(b[0] - n.x, b[2] + 0.25, b[1] - n.y), B(b[0] + n.x, b[2] + 0.25, b[1] + n.y)], M['path'])
path.finish()

# the wood on the hill: thick on the funfair's slopes, thin round the park
hw = Mesh('HillWood')
for k in range(9000):
    x, z = rng.uniform(X0, X1), rng.uniform(Z0, N.FOOT_Z - 4)
    if in_fair(x, z, 4) or near_path(x, z, 3.2) or abs(x - N.CABLE_LOW[0]) < 4 or in_gracia(x, z):
        continue
    if math.hypot(x - N.BALL_LEDGE[0], z - N.BALL_LEDGE[1]) < 6.5 or near_line(x, z, N.SLIDE, 2.6) or (N.LOOKOUT and math.hypot(x - N.LOOKOUT[0], z - N.LOOKOUT[1]) < 5):
        continue
    if in_park(x, z, 0.95):
        continue
    sparse = x > N.EAST_X[0] + 10 and z > -300
    if sparse and rng.random() > (0.25 if in_park(x, z, 1.5) else 0.45):
        continue
    h = N.height(x, z)
    r = rng.uniform(2.2, 3.4)
    hw.ball(B(x, h + r * 1.1, z), r, M['wood'] if rng.random() < 0.6 else M['wood2'], 0.95, 8)
hw.finish()

# the funfair, up on its plateau
F = Mesh('Funfair')
fh = N.FAIR_H
F.cyl(B(-92, fh, -282), B(-92, fh + 16, -282), 0.4, M['metal'], 6)
for k in range(24):                                              # the Ferris wheel
    a1, a2 = 2 * math.pi * k / 24, 2 * math.pi * (k + 1) / 24
    p1 = B(-92 + 7 * math.cos(a1), fh + 9 + 7 * math.sin(a1), -282)
    p2 = B(-92 + 7 * math.cos(a2), fh + 9 + 7 * math.sin(a2), -282)
    F.cyl(p1, p2, 0.25, M['red'], 6)
    if k % 3 == 0:
        F.box(p1 - Vector((0, 0, 1.0)), (1.4, 1.4, 1.4), [M['blue'], M['orange'], M['white']][k % 3 // 1 % 3])
F.box(B(-62, fh + 7, -292), (16, 12, 14), M['white'])          # the Temple del Sagrat Cor
F.cyl(B(-62, fh + 14, -292), B(-62, fh + 30, -292), 3.0, M['white'], 10, 2.2)
F.cyl(B(-62, fh + 30, -292), B(-62, fh + 35, -292), 0.6, M['cream'], 6)
F.ball(B(-62, fh + 36.5, -292), 1.4, M['cream'])
F.cyl(B(-38, fh, -277), B(-38, fh + 2.5, -277), 4.5, M['red'], 16)  # the carousel
F.cyl(B(-38, fh + 2.5, -277), B(-38, fh + 5.5, -277), 4.8, M['white'], 16, 0.3)
F.cyl(B(-48, fh, -290), B(-48, fh + 22, -290), 0.6, M['metal'], 6)   # the Talaia's mast
F.cyl(B(-48, fh + 22, -290), B(-36, fh + 24, -286), 0.3, M['metal'], 6)
F.box(B(-36, fh + 22.5, -286), (2.2, 2.2, 2.2), M['red'])
F.cyl(B(-76, fh, -272), B(-76, fh + 9, -272), 0.4, M['metal'], 6)     # the Avió
F.box(B(-70, fh + 8, -272), (5, 1.2, 1.2), M['red'])
for x in range(-106, -22, 4):                                    # a railing along the edge
    F.box(B(x, fh + 0.5, -262.3), (4, 0.15, 1.0), M['white'])
F.finish()

# the cable car
C = Mesh('CableCar')
lo, hi = N.CABLE_LOW, N.CABLE_TOP
hlo, hhi = N.height(*lo), N.FAIR_H
C.box(B(lo[0], hlo + 3, lo[1]), (9, 8, 6), M['cream'])
C.box(B(lo[0], hlo + 6.3, lo[1]), (10, 9, 0.6), M['roof'])
C.box(B(hi[0], hhi + 3, hi[1]), (9, 8, 6), M['cream'])
C.box(B(hi[0], hhi + 6.3, hi[1]), (10, 9, 0.6), M['roof'])
top_lo, top_hi = hlo + 9, hhi + 9
for s in (-1.2, 1.2):
    C.cyl(B(lo[0] + s, top_lo, lo[1]), B(hi[0] + s, top_hi, hi[1]), 0.06, M['metal'], 4)
for px, pz in N.CABLE_PYLONS:
    t = (pz - lo[1]) / (hi[1] - lo[1])
    ch = top_lo + (top_hi - top_lo) * t
    C.cyl(B(px, N.height(px, pz), pz), B(px, ch + 0.5, pz), 0.5, M['metal'], 6)
    C.box(B(px, ch + 0.6, pz), (4, 0.6, 0.6), M['metal'])
for t in (0.3, 0.68):
    x, z = lo[0] + 1.2, lo[1] + (hi[1] - lo[1]) * t
    C.box(B(x, top_lo + (top_hi - top_lo) * t - 2.2, z), (2.4, 2.4, 2.4), M['red'])
C.finish()

# the workmen, their barrier, the ball and its ledge
W = Mesh('Scene')
for (x, z) in N.WORKMEN:
    h = N.height(x, z)
    W.cyl(B(x, h, z), B(x, h + 1.8, z), 0.45, M['orange'], 8)
    W.ball(B(x, h + 2.1, z), 0.35, M['white'])
x, z = N.WORKMEN[0]
for s in (-1.6, 1.6):
    W.box(B(x + 2.5, N.height(x, z) + 0.6, z + s), (0.3, 0.3, 1.2), M['red'])
W.box(B(x + 2.5, N.height(x, z) + 1.0, z), (0.25, 3.4, 0.35), M['white'])
for a, b in zip(N.SLIDE, N.SLIDE[1:]):
    for k in range(12):
        t0, t1 = k / 12, (k + 1) / 12
        p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
        p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
        d = Vector((p1[0] - p0[0], p1[1] - p0[1]))
        n = Vector((-d.y, d.x)).normalized() * 0.9
        W.face([B(p0[0] + n.x, N.height(*p0) + 0.2, p0[1] + n.y), B(p0[0] - n.x, N.height(*p0) + 0.2, p0[1] - n.y),
                B(p1[0] - n.x, N.height(*p1) + 0.2, p1[1] - n.y), B(p1[0] + n.x, N.height(*p1) + 0.2, p1[1] + n.y)], M['sand'])
if N.LOOKOUT:                                                    # a little lookout with a bench, off the bend
    lx, lz = N.LOOKOUT
    lh = N.height(lx, lz)
    W.cyl(B(lx, lh - 0.5, lz), B(lx, lh + 0.3, lz), 3.2, M['stone'], 12)
    W.box(B(lx + 1.5, lh + 0.7, lz), (0.5, 2.2, 0.5), M['trunk'])
bx, bz = N.BALL_LEDGE
bh = N.height(bx, bz)
W.cyl(B(bx, bh - 0.5, bz), B(bx, bh + 0.35, bz), 4.0, M['path'], 14)
W.ball(B(bx, bh + 0.75, bz), 0.4, M['white'])
W.finish()

# Gràcia: small blocks of terraced houses, a square, the street up to the park
G = Mesh('Gracia')
cols = ['h1', 'h2', 'h3', 'h4', 'h5']
for blk in N.GRACIA_BLOCKS:
    n = len(blk)
    for i in range(n):
        a, b = Vector(blk[i]), Vector(blk[(i + 1) % n])
        d = b - a
        L_ = d.length
        k = max(1, int(L_ / 6.0))
        inward = Vector((-d.y, d.x)).normalized()
        cx = sum(p[0] for p in blk) / n
        cz = sum(p[1] for p in blk) / n
        if inward.dot(Vector((cx, cz)) - a) < 0:
            inward = -inward
        for j in range(k):                       # a terrace of narrow houses along each side
            c = a + d * ((j + 0.5) / k) + inward * 4.0
            h = N.height(c.x, c.y)
            ht = rng.choice([8.5, 10.0, 11.5])
            rot = math.atan2(-d.y, d.x)
            G.box(B(c.x, h + ht / 2 - 1, c.y), (L_ / k + 0.05, 8.0, ht), M[cols[(i * 3 + j) % 5]], rot)
            G.box(B(c.x, h + ht - 0.6, c.y), (L_ / k + 0.3, 8.6, 0.5), M['roof'], rot)
px, pz, pr = N.GRACIA_PLACA
for k in range(16):
    a1, a2 = 2 * math.pi * k / 16, 2 * math.pi * (k + 1) / 16
    G.face([B(px, N.height(px, pz) + 0.25, pz), B(px + pr * math.cos(a1), N.height(px, pz) + 0.25, pz + pr * math.sin(a1)),
            B(px + pr * math.cos(a2), N.height(px, pz) + 0.25, pz + pr * math.sin(a2))], M['pave'])
G.ball(B(px, N.height(px, pz) + 3.5, pz), 3.0, M['tree'], 0.8)
line = N.catmull(N.GRACIA_UP, 6)
for a, b in zip(line, line[1:]):
    d = Vector((b[0] - a[0], b[1] - a[1]))
    if d.length < 1e-4:
        continue
    n = Vector((-d.y, d.x)).normalized() * 3.5
    G.face([B(a[0] + n.x, N.height(*a) + 0.2, a[1] + n.y), B(a[0] - n.x, N.height(*a) + 0.2, a[1] - n.y),
            B(b[0] - n.x, N.height(*b) + 0.2, b[1] - n.y), B(b[0] + n.x, N.height(*b) + 0.2, b[1] + n.y)], M['street'])
G.finish()

# Park Güell
P = Mesh('Guell')
ring = N.park_ring()
for a, b in zip(ring, ring[1:]):                                 # the ring of winding paths
    d = Vector((b[0] - a[0], b[1] - a[1]))
    n = Vector((-d.y, d.x)).normalized() * 2.2
    P.face([B(a[0] + n.x, N.height(*a) + 0.3, a[1] + n.y), B(a[0] - n.x, N.height(*a) + 0.3, a[1] - n.y),
            B(b[0] - n.x, N.height(*b) + 0.3, b[1] - n.y), B(b[0] + n.x, N.height(*b) + 0.3, b[1] + n.y)], M['path'])
for k in range(48):                                              # its outer wall, broken for the gate
    a = 2 * math.pi * k / 48
    x, z = N.PARK_C[0] + N.PARK_R[0] * math.cos(a), N.PARK_C[1] + N.PARK_R[1] * math.sin(a)
    if math.hypot(x - N.PARK_GATE[0], z - N.PARK_GATE[1]) < 8:
        continue
    P.box(B(x, N.height(x, z) + 0.9, z), (7.0, 0.8, 1.8), M['gwall'], math.atan2(-math.cos(a) * N.PARK_R[1], -math.sin(a) * N.PARK_R[0]) + math.pi / 2)
g = N.GUELL
for key, col in (('guarda', 'h5'), ('lodge', 'h5')):                # the lodges, with their mushroom roofs
    x, z = g[key]
    h = N.height(x, z)
    P.box(B(x, h + 2.5, z), (7, 7, 5), M[col])
    P.ball(B(x, h + 5.5, z), 3.6, M['white'] if key == 'guarda' else M['blue'], 0.9)
    P.cyl(B(x, h + 8, z), B(x, h + 11, z), 0.5, M['red'], 6)
(sx, sz0), (_, sz1) = g['stairs']
for k in range(10):                                              # the dragon stairs
    z = sz0 + (sz1 - sz0) * k / 10
    P.box(B(sx, N.height(sx, z) + 0.3 + k * 0.45, z), (7, 1.6, 0.6), M['stone'])
P.box(B(sx, N.height(sx, -158) + 3.2, -158), (1.5, 2.5, 1.0), M['green2'])
hx, hz, hwid, hdep = g['hypostyle']
hb = N.height(hx, hz)
for i in range(7):
    for j in range(4):
        P.cyl(B(hx - hwid / 2 + 2 + i * (hwid - 4) / 6, hb, hz - hdep / 2 + 2 + j * (hdep - 4) / 3),
              B(hx - hwid / 2 + 2 + i * (hwid - 4) / 6, hb + 6, hz - hdep / 2 + 2 + j * (hdep - 4) / 3), 0.6, M['white'], 8)
sx2, sz2, sw, sd = g['square']
sq = hb + 6.2
P.box(B(sx2, sq - 0.3, sz2), (sw, sd, 0.6), M['park'])
for k in range(30):                                              # the wavy bench along its edge
    t = k / 30
    x = sx2 - sw / 2 + sw * t
    P.box(B(x, sq + 0.4, sz2 + sd / 2 - 1.2 + 1.2 * math.sin(t * math.pi * 6)), (sw / 30 + 0.2, 0.7, 0.8), M['blue'] if k % 2 else M['orange'])
bx2, bz2, br = g['bugadera']
for k in range(9):                                               # the portico's leaning columns
    a = math.pi * (0.25 + 0.5 * k / 8)
    x, z = bx2 + br * math.cos(a + math.pi / 2), bz2 + br * math.sin(a + math.pi / 2) * 0.7
    h = N.height(x, z)
    P.cyl(B(x, h, z), B(x + 1.2, h + 4.5, z - 0.6), 0.55, M['gwall'], 6)
x, z = g['museu']
h = N.height(x, z)
P.box(B(x, h + 5, z), (9, 9, 10), M['pink'])
P.cyl(B(x, h + 10, z), B(x, h + 17, z), 1.6, M['pink'], 8, 0.1)
x, z = g['trias']
h = N.height(x, z)
P.box(B(x, h + 4, z), (11, 9, 8), M['cream'])
P.box(B(x, h + 8.4, z), (11.6, 9.6, 0.8), M['roof'])
P.finish()

# ------------------------------------------------------------------ light, sky, cameras
sun = bpy.data.lights.new('Sun', 'SUN')
sun.energy = 3.2
sun.angle = math.radians(1.5)
so = bpy.data.objects.new('Sun', sun)
scn.collection.objects.link(so)
so.rotation_euler = (math.radians(42), 0, math.radians(30))
world = bpy.data.worlds.new('W')
scn.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.42, 0.62, 0.9, 1)
bg.inputs['Strength'].default_value = 0.9
scn.render.engine = 'BLENDER_EEVEE'
scn.render.resolution_x, scn.render.resolution_y = 1280, 800
scn.view_settings.view_transform = 'Standard'
scn.render.film_transparent = False


ONLY = [x for x in os.environ.get('MOCK_ONLY', '').split(',') if x]


def shoot(name, frm, to, fov=55.0, ortho=0.0, res=(1280, 800)):
    if ONLY and name not in ONLY:
        return
    cam = bpy.data.cameras.new(name)
    cam.sensor_fit = 'VERTICAL'
    cam.clip_end = 3000
    if ortho:
        cam.type = 'ORTHO'
        cam.ortho_scale = ortho
    else:
        cam.angle = math.radians(fov)
    ob = bpy.data.objects.new(name, cam)
    scn.collection.objects.link(ob)
    ob.location = frm
    d = to - frm
    ob.rotation_euler = (0, 0, 0) if ortho else d.to_track_quat('-Z', 'Y').to_euler()
    scn.camera = ob
    scn.render.resolution_x, scn.render.resolution_y = res
    scn.render.filepath = os.path.join(OUT, name + '.png')
    bpy.ops.render.render(write_still=True)


T = 3.3
shoot('rambla', B((40 - 55) * T, 1.7, (70 - 45) * T), B((36 - 55) * T, 14, (4 - 45) * T))
shoot('aerial', B(150, 130, 70), B(-20, 30, -200), 50)
shoot('gracia', B(97, 3.5, -96), B(104, 9, -150), 60)
shoot('path', B(-40, 150, -90), B(-130, 45, -210), 55)
shoot('hillplan', B(-110, 400, -200), B(-110, 0, -199.9), ortho=240, res=(1280, 1280))
shoot('ledge', B(45, 85, -185), B(-2, 50, -218), 45)
shoot('plan', B(-15, 400, -275), B(-15, 0, -274.9), ortho=460, res=(1280, 1280))
print('MOCK OK', OUT)
