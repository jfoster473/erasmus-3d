# Builds the shared assets for the 3D engine tests (Three.js and Godot).
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P build_assets.py
#
# Writes city.glb and interior.glb, and scene.json (layout, collision, interactions), to the world's
# bigfiles/built/<world>/ (paths.OUT).
#
# Coordinates: the 2D game's tile grid (x east, y south). Outdoors one tile is
# T metres; indoors one tile is one metre. Blender is Z-up, so a tile (tx, ty)
# sits at Blender (tx*T, -ty*T). glTF/engines are Y-up: (x, y, z) = (tx*T, h, ty*T).

import bpy, bmesh, math, random, json, os
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
import sys as _sys0
_sys0.path.insert(0, HERE)
from paths import WORLD, BUILD, DATA, OUT, PROPS, MESHY, MESHY_CACHE
os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

T = 3.3                    # metres per street tile
S2 = math.sqrt(2)
BS, CUT = 9, 2             # block size and chamfer depth (tiles), as in the 2D game
COURT = 2.4                # building depth (tiles) before the inner courtyard
GROUND_H, FLOOR_H = 3.2, 2.7    # scaled to Sandra (~1.7 m), not to real Eixample storeys
KERB = 0.12

# The map is the 2D game's (from2d/data2d.json, written by from2d/extract.sh from the game itself), with
# the 3D game's own changes (from2d/remap3d.py -> data3d.json: La Rambla a block further west, the
# Sagrada Família and the university moved, doors on all sides of the blocks):
# its tile (X, Y) is our tile (X - OX, Y - OY), so Sandra's block, at 2D (55, 45), is our (0, 0).
W2 = json.load(open(os.path.join(DATA, 'data3d.json')))
OX, OY = 55, 45
COLS = [c - OX for c in W2['BCOLS']]                # block column origins: -43, -30, -13, 0, 13
ROWS = [r - OY for r in W2['BROWS']]                # block row origins: -26, -13, 0, 13, 26
WALK = dict(x0=-OX + 0.3, x1=W2['MW'] + 11 - OX - 0.3, y0=-OY + 0.3, y1=W2['MH'] - OY - 0.3)   # the whole map (round 23: and the wood beyond its east edge, up to where the ground rises too steeply)
NEAR = dict(x0=-99, x1=99, y0=-99, y1=99)          # every block is built in full detail
HOME = (0, 0)                                      # Sandra's block origin
H_STREETS = {h['y'] - OY: h['name'] for h in W2['HSTREETS']}
V_STREETS = {v['x'] - OX: v['name'] for v in W2['VSTREETS']}
V_WIDTH = {v['x'] - OX: v['w'] for v in W2['VSTREETS']}
CITY = [W2['CITY'][0] - OX, W2['CITY'][1] - OY, W2['CITY'][2] - OX, W2['CITY'][3] - OY]   # x0, y0, x1, y1: the city's streets
SEGMENT = {'Carrer de la Flor de Lliri': (-4, 9, 9, 13)}   # a named stretch of València: between Roger de Llúria and Girona
# (round 41, the user: "name the street to the correct name and change it everywhere" — its corner plaques too)
PROM = (W2['PASSEIG_Y1'] - 1 - OY, W2['PASSEIG_Y1'] + 1 - OY)   # the Passeig Marítim (tiles)

# ---- reading the 2D map (used by world2d.py, landmarks.py and interiors.py)
TN = {int(k): v for k, v in W2['tileNames'].items()}
MW2, MH2 = W2['MW'], W2['MH']
H_T = 7.0                                    # the Tibidabo terrace, metres up
STEPS = (34, 37, 9, 14)                       # the stone steps from its gate down to the foot of the mountain (2D tiles)


def tile(X, Y):
    """The 2D game's tile kind at (X, Y), or None off the map."""
    if 0 <= X < MW2 and 0 <= Y < MH2:
        return TN[W2['tiles'][Y][X]]
    return None


def curve(name, v):
    """One of the 2D game's natural boundaries (coast, beach, mount, river, forest) at v, sampled every half tile."""
    a = W2[name]
    i = max(0.0, min(len(a) - 1.001, v * 2))
    k = int(i)
    return a[k] + (a[k + 1] - a[k]) * (i - k)


def BT(X, Y, h=0.0):
    """A 2D tile coordinate as a Blender point."""
    return B(X - OX, Y - OY, h)


def mT(X, Y):
    """A 2D tile coordinate in engine metres [x, z]."""
    return [round((X - OX) * T, 3), round((Y - OY) * T, 3)]


def in_city(X, Y):
    return W2['CITY'][0] - 1 <= X < W2['CITY'][2] + 1 and W2['CITY'][1] - 1 <= Y < W2['CITY'][3] + 3

# palettes copied from the 2D game
FACADES = [(228, 182, 110), (240, 222, 184), (228, 156, 116), (235, 178, 145), (240, 206, 126), (224, 198, 152), (236, 196, 160)]
SHUTTERS = [(92, 138, 106), (70, 112, 86), (140, 92, 62), (96, 122, 140), (110, 140, 96)]
ROOFS = [(226, 132, 80), (216, 120, 72), (232, 146, 92), (210, 114, 70), (222, 138, 86)]
GREENS = [(64, 108, 56), (78, 124, 62), (92, 132, 60), (58, 98, 66), (104, 140, 70)]
AWNINGS = ['#b8423a', '#2f6b5a', '#c9a24a', '#3a5a8a', '#7a3a5a']
SANDRA_HOUSE = dict(facade='#efd9ad', shutter='#5d8a6a', door='#c46a45')

# ------------------------------------------------------------------ helpers

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)


def rgb(c):
    if isinstance(c, str):
        c = c.lstrip('#')
        return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return tuple(v / 255 for v in c)


def lin(c):
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb(c))


def hexof(c):
    return '#%02x%02x%02x' % tuple(round(v * 255) for v in rgb(c))


MATS = {}


def mat(name, col, rough=0.85, metal=0.0, image=None, alpha=False):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        outn = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None) or nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(bsdf.outputs[0], outn.inputs[0])
    bsdf.inputs['Base Color'].default_value = (*lin(col), 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if image is not None:
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = image
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        if alpha:
            nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    m.diffuse_color = (*lin(col), 1)
    MATS[name] = m
    return m


def make_image(name, w, h, fn):
    img = bpy.data.images.new(name, w, h, alpha=False)
    px = [0.0] * (w * h * 4)
    for y in range(h):
        for x in range(w):
            r, g, b = fn(x, y)
            i = (y * w + x) * 4
            px[i], px[i + 1], px[i + 2], px[i + 3] = min(1, max(0, r)), min(1, max(0, g)), min(1, max(0, b)), 1.0
    img.pixels.foreach_set(px)
    img.file_format = 'PNG'
    try:
        img.pack()
    except Exception:
        pass
    return img


class MB:
    """Collects faces into one bmesh, then becomes a mesh object."""

    def __init__(self, uv=False):
        self.bm = bmesh.new()
        self.mats, self.idx = [], {}
        self.uv = self.bm.loops.layers.uv.new('UVMap') if uv else None

    def mi(self, m):
        if m.name not in self.idx:
            self.idx[m.name] = len(self.mats)
            self.mats.append(m)
        return self.idx[m.name]

    def face(self, pts, m, normal=None, uvs=None, uvscale=1.0, smooth=False):
        pts = [Vector(p) for p in pts]
        if normal is not None:
            nrm = (pts[1] - pts[0]).cross(pts[2] - pts[0])
            if nrm.dot(Vector(normal)) < 0:
                pts.reverse()
                if uvs:
                    uvs = list(reversed(uvs))
        f = self.bm.faces.new([self.bm.verts.new(p) for p in pts])
        f.material_index = self.mi(m)
        f.smooth = smooth
        if self.uv is not None:
            if uvs is None:
                f.normal_update()
                n = f.normal
                if abs(n.z) > 0.7:
                    uvs = [(p.x / uvscale, p.y / uvscale) for p in pts]
                else:
                    t = Vector((-n.y, n.x, 0)).normalized()
                    uvs = [(p.dot(t) / uvscale, p.z / uvscale) for p in pts]
            for loop, uv in zip(f.loops, uvs):
                loop[self.uv].uv = uv
        return f

    def box(self, c, u, n, su, sn, sz, m):
        c = Vector(c)
        U = Vector((u[0], u[1], 0)) * su
        N = Vector((n[0], n[1], 0)) * sn
        Z = Vector((0, 0, sz))

        def P(a, b, z):
            return c + U * a + N * b + Z * z
        for (pts, nn) in (
            ([P(-1, -1, 1), P(1, -1, 1), P(1, 1, 1), P(-1, 1, 1)], Z),
            ([P(-1, -1, -1), P(1, -1, -1), P(1, 1, -1), P(-1, 1, -1)], -Z),
            ([P(-1, 1, -1), P(1, 1, -1), P(1, 1, 1), P(-1, 1, 1)], N),
            ([P(-1, -1, -1), P(1, -1, -1), P(1, -1, 1), P(-1, -1, 1)], -N),
            ([P(1, -1, -1), P(1, 1, -1), P(1, 1, 1), P(1, -1, 1)], U),
            ([P(-1, -1, -1), P(-1, 1, -1), P(-1, 1, 1), P(-1, -1, 1)], -U),
        ):
            self.face(pts, m, normal=nn if nn.length else None)

    def abox(self, x0, y0, z0, x1, y1, z1, m):
        """Axis-aligned box from Blender-space corners."""
        self.box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (1, 0), (0, 1),
                 abs(x1 - x0) / 2, abs(y1 - y0) / 2, abs(z1 - z0) / 2, m)

    def _tag(self, verts, m, smooth):
        faces = {f for v in verts for f in v.link_faces}
        for f in faces:
            f.material_index = self.mi(m)
            f.smooth = smooth
        return faces

    def stamp(self, op, M, **kw):
        """(round 26) A bmesh primitive (create_cone, _uvsphere, _icosphere) made in a little mesh of its own and copied
        in: run on the big mesh itself, each one cost time in proportion to all that was already in it (40 ms at
        400,000 vertices), and the balconies' thousands of iron bars took six minutes of the build. Returns its verts."""
        tmp = bmesh.new()
        tuv = tmp.loops.layers.uv.new('UVMap') if self.uv is not None else None
        op(tmp, matrix=M, **kw)
        tmp.verts.index_update()
        new = [self.bm.verts.new(v.co) for v in tmp.verts]
        for f in tmp.faces:
            nf = self.bm.faces.new([new[v.index] for v in f.verts])
            nf.normal_update()
            if tuv is not None:
                for l0, l1 in zip(f.loops, nf.loops):
                    l1[self.uv].uv = l0[tuv].uv
        tmp.free()
        return new

    def cone(self, M, segs, r1, r2, depth, m, smooth=True, caps=True, uvscale=None):
        vs = self.stamp(bmesh.ops.create_cone, M, cap_ends=caps, cap_tris=False, segments=segs,
                        radius1=r1, radius2=r2, depth=depth, calc_uvs=self.uv is not None)
        fs = self._tag(vs, m, smooth)
        if uvscale and self.uv is not None:
            # (round 29) world-scale texture repeats: the primitive's UVs span 0..1, so one tile stretched
            # round a fat column smears (the lodges' corner cylinders)
            ru = math.tau * (r1 + r2) / 2 / uvscale
            for f in fs:
                for lo in f.loops:
                    u_, v_ = lo[self.uv].uv
                    lo[self.uv].uv = (u_ * ru, v_ * depth / uvscale)

    def sphere(self, M, r, m, segs=(16, 10), smooth=True):
        vs = self.stamp(bmesh.ops.create_uvsphere, M, u_segments=segs[0], v_segments=segs[1], radius=r)
        self._tag(vs, m, smooth)

    def ico(self, M, r, m, sub=2, jitter=0.0, rng=None, smooth=True):
        res = {'verts': self.stamp(bmesh.ops.create_icosphere, M, subdivisions=sub, radius=r)}
        if jitter and rng:
            ctr = M.to_translation()
            for v in res['verts']:
                d = (v.co - ctr)
                if d.length:
                    v.co += d.normalized() * rng.uniform(-jitter, jitter)
        self._tag(res['verts'], m, smooth)

    def finish(self, name, coll=None):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(name, me)
        (coll or bpy.context.scene.collection).objects.link(ob)
        return ob


def text_obj(body, size, m, loc, rot_z, name):
    cu = bpy.data.curves.new(name + '_c', type='FONT')
    cu.body = body
    cu.size = size
    cu.extrude = 0.0
    cu.resolution_u = 3                     # letters with fewer curve steps: plenty for signs
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    tmp = bpy.data.objects.new(name + '_tmp', cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (math.pi / 2, 0, rot_z)
    ob.location = loc
    TEXT_OBJS.append(ob)
    return ob


TEXT_OBJS = []                              # (round 40: every sign's lettering, for the SIGN_FLOAT check)


def facing(n):
    """Rotation about Z that turns text (which faces -Y) to face Blender direction n."""
    return math.atan2(n[1], n[0]) + math.pi / 2


def B(tx, ty, h=0.0):
    return Vector((tx * T, -ty * T, h))


def octagon(ox, oy, off=0.0):
    a0, a1, b0, b1 = ox - off, ox + BS + off, oy - off, oy + BS + off
    c = CUT + off * (2 - S2)
    return [(a0 + c, b0), (a1 - c, b0), (a1, b0 + c), (a1, b1 - c), (a1 - c, b1), (a0 + c, b1), (a0, b1 - c), (a0, b0 + c)]


def lerp2(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def edge_frame(p0, p1):
    """Unit along-edge and outward-normal vectors, in Blender XY."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    dx, dy = dx / L, dy / L
    return (dx, -dy), (dy, dx), L          # tile (dx,dy) -> Blender (dx,-dy); outward (dy,-dx) -> (dy,dx)


def to_m(p):
    return [round(p[0] * T, 3), round(p[1] * T, 3)]


# ------------------------------------------------------------------ textures

rnd = random.Random(7)


def panot(x, y):
    tx, ty = x % 64, y % 64
    base = 0.73 + rnd.uniform(-0.02, 0.02)
    v = base
    if tx < 2 or ty < 2:
        v = 0.55
    else:
        for (cx, cy) in ((32 - 13, 32), (32 + 13, 32), (32, 32 - 13), (32, 32 + 13)):
            d = math.hypot(tx - cx, ty - cy)
            if d < 11:
                v = base - 0.06 + (0.05 if (tx - cx) + (ty - cy) < -6 else 0)
            elif d < 12.5:
                v = base - 0.1
    return (v * 1.0, v * 0.975, v * 0.93)


def asphalt(x, y):
    v = 0.33 + rnd.uniform(-0.035, 0.035)
    return (v, v * 1.02, v * 1.07)


def terrat_fn(col):
    r, g, b = rgb(col)

    def fn(x, y):
        if x % 16 == 0 or y % 16 == 0:
            k = 1.12
        else:
            k = 1.0 + rnd.uniform(-0.04, 0.04) + (0.03 if ((x // 16) + (y // 16)) % 3 == 0 else 0)
        return (r * k, g * k, b * k)
    return fn


FCOL = [rgb(c) for c in ('#c9674a', '#efe2c6', '#4f7f86')]   # Sandra's floor colourway (int_sandra.fcol)


def hydraulic(x, y):
    tx, ty = x % 64, y % 64
    if tx == 0 or ty == 0:
        return tuple(v * 0.8 for v in FCOL[1])
    cx, cy = tx - 32, ty - 32
    if math.hypot(tx if tx < 32 else 64 - tx, ty if ty < 32 else 64 - ty) < 15:
        c = FCOL[0]                                     # quarter circles at the corners
    elif abs(cx) + abs(cy) < 13:
        c = FCOL[2]                                     # centre diamond
    elif abs(cx) + abs(cy) < 16:
        c = FCOL[0]
    else:
        c = FCOL[1]
    k = 1 + rnd.uniform(-0.025, 0.025)
    return tuple(v * k for v in c)


def seascape(x, y):
    # Rosa's watercolour of the Barceloneta at dawn (64x48, y=0 is the bottom row)
    t = y / 47
    if t > 0.55:
        k = (t - 0.55) / 0.45
        return (0.98 - 0.25 * k, 0.78 - 0.05 * k, 0.62 + 0.25 * k)
    if t > 0.32:
        return (0.29, 0.52 + 0.1 * math.sin(x * 0.4 + y), 0.66)
    return (0.9, 0.8, 0.6)


IMG_PANOT = make_image('panot', 128, 128, panot)
IMG_ASPHALT = make_image('asphalt', 64, 64, asphalt)
IMG_FLOOR = make_image('rajola', 128, 128, hydraulic)
IMG_SEA = make_image('seascape', 64, 48, seascape)


# ------------------------------------------------------------------ foliage (leaf cards)

def foliage_image(name, size, layers, seed):
    """Paints a spray of leaves/flowers onto a transparent texture. layers: (count, colours, rmin, rmax, aspect, lobes)."""
    rng = random.Random(seed)
    W = H = size
    base = rgb(layers[0][1][0])
    px = [0.0] * (W * H * 4)
    for i in range(W * H):                       # leaf colour under the transparent pixels, so mipmaps don't go dark
        px[i * 4], px[i * 4 + 1], px[i * 4 + 2] = base
    for count, cols, rmin, rmax, asp, lobes in layers:
        for _ in range(count):
            a, rr = rng.uniform(0, 6.283), (rng.random() ** 0.6) * 0.4 * W
            cx, cy = W / 2 + math.cos(a) * rr, H / 2 + math.sin(a) * rr
            r, ang, col = rng.uniform(rmin, rmax), rng.uniform(0, 6.283), rgb(rng.choice(cols))
            ca, sa, R = math.cos(ang), math.sin(ang), int(r * 1.3) + 1
            for y in range(max(0, int(cy - R)), min(H, int(cy + R) + 1)):
                for x in range(max(0, int(cx - R)), min(W, int(cx + R) + 1)):
                    dx, dy = x - cx, y - cy
                    u, v = (dx * ca + dy * sa) / r, (-dx * sa + dy * ca) / (r * asp)
                    d = math.hypot(u, v)
                    if lobes:
                        d /= 0.74 + 0.26 * abs(math.cos(math.atan2(v, u) * lobes / 2))
                    if d < 1.0:
                        k = (0.78 + 0.3 * (1 - d) + 0.1 * u) * (0.88 if abs(v) < 0.05 else 1.0)
                        i = (y * W + x) * 4
                        px[i], px[i + 1], px[i + 2], px[i + 3] = min(1, col[0] * k), min(1, col[1] * k), min(1, col[2] * k), 1.0
    img = bpy.data.images.new(name, W, H, alpha=True)
    img.pixels.foreach_set(px)
    img.file_format = 'PNG'
    try:
        img.pack()
    except Exception:
        pass
    return img


PLANE_GREENS = ['#5f7f34', '#6e9140', '#7fa04a', '#4f6e2e', '#8aa851', '#93ad57']
IMG_PLANE = foliage_image('leaves_plane', 256, [(120, ['#4f6e2e', '#5a7a33'], 9, 14, 0.85, 0),
                                                (230, PLANE_GREENS, 8, 14, 0.85, 0)], 11)
IMG_SHRUB = foliage_image('leaves_shrub', 128, [(260, ['#3f6a2e', '#4d7a35', '#5d8a3c', '#6b9443'], 4, 7, 0.55, 0)], 12)
IMG_GERANIUM = foliage_image('geranium', 128, [(70, ['#4a7a34', '#5a8a3a', '#3e6c2e'], 6, 9, 0.95, 0),
                                               (150, ['#d8323a', '#e8454a', '#c2283a', '#f05a5a'], 2.5, 4, 1.0, 0)], 13)
IMG_BOUG = foliage_image('bougainvillea', 256, [(150, ['#3f6e2c', '#4e7d33', '#5b8a3a'], 6, 10, 0.6, 0),
                                                (300, ['#c2185b', '#d63384', '#b0175a', '#e04a9a', '#cf2f7a'], 4, 7, 0.85, 3)], 14)
M_PLANE_LEAVES = mat('LeavesPlane', '#ffffff', 0.8, image=IMG_PLANE, alpha=True)
M_SHRUB = mat('LeavesShrub', '#ffffff', 0.8, image=IMG_SHRUB, alpha=True)
M_GERANIUM_CARD = mat('LeavesGeranium', '#ffffff', 0.8, image=IMG_GERANIUM, alpha=True)
M_BOUG = mat('LeavesBougainvillea', '#ffffff', 0.8, image=IMG_BOUG, alpha=True)


class Cards:
    """Leaf cards: textured quads whose normals point out from the clump, so foliage shades as a soft volume."""

    def __init__(self):
        self.verts, self.faces, self.uvs, self.nrm, self.fmat, self.mats = [], [], [], [], [], []

    def card(self, c, size, rot, clump, m, roundness=0.75):
        if m not in self.mats:
            self.mats.append(m)
        fn = rot @ Vector((0, 0, 1))
        b = len(self.verts)
        for (a, bb), uv in zip(((-1, -1), (1, -1), (1, 1), (-1, 1)), ((0, 0), (1, 0), (1, 1), (0, 1))):
            p = c + rot @ Vector((a * size / 2, bb * size / 2, 0))
            out = p - clump
            n = (out.normalized() * roundness + fn * (1 - roundness)).normalized() if out.length else fn
            self.verts.append(p)
            self.nrm.append(n)
            self.uvs.append(uv)
        self.faces.append((b, b + 1, b + 2, b + 3))
        self.fmat.append(self.mats.index(m))

    def clump(self, centre, radii, count, size, m, rng, up_bias=0.0):
        for _ in range(count):
            while True:
                q = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
                if q.length <= 1:
                    break
            p = centre + Vector((q.x * radii[0], q.y * radii[1], q.z * radii[2]))
            rot = (Matrix.Rotation(rng.uniform(0, 6.283), 3, 'Z') @ Matrix.Rotation(rng.uniform(-1.2, 1.2) + up_bias, 3, 'X')
                   @ Matrix.Rotation(rng.uniform(0, 6.283), 3, 'Z'))
            self.card(p, size * rng.uniform(0.8, 1.2), rot, centre, m)

    def shell(self, centre, radii, count, size, m, rng, depth=(0.72, 1.0)):
        """Cards on the outside of a dome, facing outwards, so the clump reads as a soft round crown."""
        for _ in range(count):
            while True:
                d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)))
                if d.length > 1e-3:
                    break
            d.normalize()
            if d.z < -0.55:
                d.z = -d.z * 0.5                      # few cards on the underside
                d.normalize()
            p = centre + Vector((d.x * radii[0], d.y * radii[1], d.z * radii[2])) * rng.uniform(*depth)
            tilt = Vector((rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), 0))
            nrm = (d + tilt).normalized()
            rot = Vector((0, 0, 1)).rotation_difference(nrm).to_matrix() @ Matrix.Rotation(rng.uniform(0, 6.283), 3, 'Z')
            self.card(p, size * rng.uniform(0.85, 1.15), rot, centre, m, 0.9)

    def finish(self, name):
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in self.verts], [], self.faces)
        uvl = me.uv_layers.new(name='UVMap')
        for loop in me.loops:
            uvl.data[loop.index].uv = self.uvs[loop.vertex_index]
        for poly, fm in zip(me.polygons, self.fmat):
            poly.material_index = fm
            poly.use_smooth = True
        me.normals_split_custom_set([tuple(self.nrm[l.vertex_index]) for l in me.loops])
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob


def vertical(angle):
    """Rotation for an upright card facing direction angle (about Z)."""
    return Matrix.Rotation(angle, 3, 'Z') @ Matrix.Rotation(math.pi / 2, 3, 'X')

M_PANOT = mat('Pavement', '#ffffff', 0.9, image=IMG_PANOT)
M_ROAD = mat('Asphalt', '#ffffff', 0.95, image=IMG_ASPHALT)
M_KERB = mat('Kerb', '#9a958c', 0.8)
M_ZEBRA = mat('Zebra', '#ecebe4', 0.8)
M_STONE = mat('Stone', '#efe3cc', 0.8)
M_PLINTH = mat('Plinth', '#b9a88c', 0.85)
M_GLASS = mat('Glass', '#2c3a44', 0.15, 0.2)
M_GLASS_LIT = mat('GlassLit', '#2c3a44', 0.15, 0.2)    # engines make these glow at night
M_SHOPGLASS = mat('ShopGlass', '#34454e', 0.1, 0.3)
M_IRON = mat('Iron', '#2e2b2a', 0.6, 0.5)
M_WOOD_DOOR = mat('DoorWood', '#6b4a33', 0.7)
M_PARTY = mat('PartyWall', '#e8b48a', 0.9)
M_COURT_WALL = mat('CourtWall', '#e6d6bc', 0.9)
M_GARDEN = mat('Garden', '#7f9a5a', 0.95)
M_CHIMNEY = mat('Chimney', '#c98a62', 0.85)
M_HUT = mat('RoofHut', '#e9d8bd', 0.9)
M_TANK = mat('Tank', '#cfd2d2', 0.6)
M_POT = mat('Pot', '#b5623e', 0.9)
M_GERANIUM = mat('Geranium', '#d23a3a', 0.8)
M_LEAF_SMALL = mat('PotLeaf', '#4f7f3f', 0.9)
def bark(x, y):
    v = math.sin(x * 0.21 + math.sin(y * 0.13) * 2.2) + math.sin(y * 0.17 + math.sin(x * 0.11) * 2.6)
    if v > 0.9:
        return rgb('#d9d2b4')       # pale cream patches where the bark has flaked
    if v > -0.2:
        return rgb('#a59c7c')
    return rgb('#7d7a5c')


M_BARK = mat('Bark', '#ffffff', 0.9, image=make_image('bark', 128, 128, bark))
M_PIT = mat('TreePit', '#4f4438', 0.95)
M_LAMPPOST = mat('LampPost', '#3c4a44', 0.5, 0.4)
M_LAMPGLASS = mat('LampGlass', '#f3e6c4', 0.2)          # engines add emission at night
M_DOORLAMP = mat('DoorLamp', '#f3dcae', 0.2)
M_MARBLE = mat('Marble', '#f1eee6', 0.4)
M_PLAQUE_TEXT = mat('PlaqueText', '#26324a', 0.5)
M_BRASS = mat('Brass', '#b8903c', 0.35, 0.8)
M_BRASS_TEXT = mat('BrassText', '#3a2a16', 0.5)
M_DOOR_PANEL = mat('DoorPanel', '#5a3c28', 0.7)


def door_unit(mb, base, u, n, w, h, arch=0.0, wood=None, frame=None, fw=0.22, depth=0.3, lunette=True):
    """(round 33, the user: "make the glow line up with the doors properly… it is a glowing door… put the shaped frame
    in there so it looks like the door glows") a real door for a building that had only a flat panel or none: two wooden
    leaves with raised panels and brass knobs, square-topped or arched (arch: the height of the curved top, metres; the
    whole height for a parabolic arch), in a stone surround (frame; None for none), a step in front. base: the bottom
    middle of the doorway on the wall's face (Blender space); u along the wall, n out of it (2D). The leaves' face is
    0.07 m out from base: the game's glow goes there, the same size and shape (entrance 'size', 'arch', 'glow')."""
    wood = wood or M_WOOD_DOOR
    U = Vector((u[0], u[1], 0))
    N = Vector((n[0], n[1], 0))
    base = Vector(base)

    def top_at(x):                                   # the opening's top, x from its middle
        if arch <= 0.0:
            return h
        t = min(1.0, abs(x) / (w / 2))
        return h - arch + arch * math.sqrt(max(0.0, 1.0 - t * t))
    # the leaves, in upright strips that follow the top; a fanlight of glass in an arch's curve
    ns = 12
    for k in range(ns):
        x0, x1 = -w / 2 + w * k / ns, -w / 2 + w * (k + 1) / ns
        xm = (x0 + x1) / 2
        tp = min(top_at(x0), top_at(x1), top_at(xm)) if arch > 0 else h
        straight = h - arch if (arch > 0.35 and lunette and arch < h * 0.6) else tp
        straight = min(straight, tp)
        mb.box(base + U * xm + N * 0.03 + Vector((0, 0, straight / 2)), u, n, (x1 - x0) / 2 + 0.002, 0.04, straight / 2, wood)
        if tp > straight + 0.02:
            mb.box(base + U * xm + N * 0.02 + Vector((0, 0, (straight + tp) / 2)), u, n, (x1 - x0) / 2 + 0.002, 0.03,
                   (tp - straight) / 2, M_GLASS_LIT)
    leaf_top = h - arch if arch > 0.35 and lunette and arch < h * 0.6 else (h - arch * 0.8 if arch > 0 else h)
    mb.box(base + N * 0.075 + Vector((0, 0, leaf_top / 2)), u, n, 0.012, 0.008, leaf_top / 2 - 0.02, M_IRON)   # the meeting line
    for sd in (-1, 1):                               # raised panels, two to a leaf, and the knobs
        cx = sd * w / 4
        hw = w / 4 - 0.14
        for (z0, z1) in ((0.18, min(0.95, leaf_top * 0.4)), (min(1.1, leaf_top * 0.47), leaf_top - 0.22)):
            if z1 - z0 > 0.15 and hw > 0.05:
                mb.box(base + U * cx + N * 0.08 + Vector((0, 0, (z0 + z1) / 2)), u, n, hw, 0.012, (z1 - z0) / 2, M_DOOR_PANEL)
        mb.sphere(Matrix.Translation(base + U * (sd * 0.11) + N * 0.11 + Vector((0, 0, 1.05))), 0.04, M_BRASS, (8, 6))
    if frame is not None:                            # the surround: jambs and a lintel, or stones round the arch
        hj = h - arch if arch > 0 else h
        for sd in (-1, 1):
            mb.box(base + U * (sd * (w / 2 + fw / 2)) + N * (depth / 2 - 0.08) + Vector((0, 0, hj / 2)), u, n, fw / 2, depth / 2, hj / 2, frame)
        if arch > 0:
            # (round 35, the everything-visit: 13 square stones, each set square to the wall, made the arch a staircase of
            # steps; now one smooth band of stone round the curve, as thick and as deep as they were)
            nst = 20

            def AR(a, out, dn):
                rx, rz = w / 2 + fw * out, arch + fw * out
                return base + U * (math.cos(a) * rx) + N * dn + Vector((0, 0, h - arch + math.sin(a) * rz))
            d0, d1 = -0.08, depth - 0.08
            for k in range(nst):
                a0, a1 = math.pi * k / nst, math.pi * (k + 1) / nst
                am = (a0 + a1) / 2
                mb.face([AR(a0, 0, d1), AR(a1, 0, d1), AR(a1, 1, d1), AR(a0, 1, d1)], frame, normal=(n[0], n[1], 0))   # its face
                for out in (0, 1):                                                                                # under and over it
                    mb.face([AR(a0, out, d0), AR(a1, out, d0), AR(a1, out, d1), AR(a0, out, d1)], frame,
                            normal=tuple((AR(am, 1, 0) - AR(am, 0, 0)) * (1 if out else -1)))
            for sd in (-1, 1):                                                                                    # its ends' undersides
                a_ = 0.0 if sd > 0 else math.pi
                mb.face([AR(a_, 0, d0), AR(a_, 1, d0), AR(a_, 1, d1), AR(a_, 0, d1)], frame, normal=(0, 0, -1))
        else:
            mb.box(base + N * (depth / 2 - 0.08) + Vector((0, 0, h + fw / 2)), u, n, w / 2 + fw, depth / 2, fw / 2, frame)
        mb.box(base + N * 0.22 + Vector((0, 0, -0.03)), u, n, w / 2 + fw, 0.3, 0.06, frame)                    # the step
    return base + N * 0.1                             # where the glow goes (just proud of the leaves)

LEAVES = [mat('Leaves%d' % i, c, 0.9) for i, c in enumerate(GREENS)]
FACADE_M = [mat('Facade%d' % i, c, 0.92) for i, c in enumerate(FACADES)]
SHUTTER_M = [mat('Shutter%d' % i, c, 0.7) for i, c in enumerate(SHUTTERS)]
ROOF_M = [mat('Roof%d' % i, c, 0.9, image=make_image('terrat%d' % i, 64, 64, terrat_fn(c))) for i, c in enumerate(ROOFS)]
AWNING_M = [mat('Awning%d' % i, c, 0.9) for i, c in enumerate(AWNINGS)]
M_SANDRA_FACADE = mat('FacadeSandra', SANDRA_HOUSE['facade'], 0.92)
M_SANDRA_SHUTTER = mat('ShutterSandra', SANDRA_HOUSE['shutter'], 0.7)
M_SANDRA_DOOR = mat('DoorSandra', SANDRA_HOUSE['door'], 0.6)

M_RED = mat('PaintRed', '#c8322e', 0.6)
M_WHITE = mat('PaintWhite', '#f2efe8', 0.6)
M_GREEN = mat('PaintGreen', '#2f5a3e', 0.6)
M_GOLD = mat('Gilt', '#d4a640', 0.35, 0.8)
M_GREYSTONE = mat('GreyStone', '#b7b1a6', 0.9)
M_WOODEN = mat('BeachWood', '#a67c52', 0.85)

city_objs = []
scene = {'tile': T, 'units': 'metres; x east, y up, z south', 'kerb': KERB,
         'walk': {'x0': WALK['x0'] * T, 'x1': WALK['x1'] * T, 'z0': WALK['y0'] * T, 'z1': WALK['y1'] * T},
         'blocks': [], 'trees': [], 'lamps': [], 'plaques': [], 'obstacles': []}

# ------------------------------------------------------------------ ground

road = MB(uv=True)
road.face([B(CITY[0], CITY[1]), B(CITY[2], CITY[1]), B(CITY[2], CITY[3]), B(CITY[0], CITY[3])], M_ROAD, normal=(0, 0, 1), uvscale=4.0)
city_objs.append(road.finish('Road'))

pave = MB(uv=True)
kerb = MB()
for ox in COLS:
    for oy in ROWS:
        po = octagon(ox, oy, 1)
        pave.face([B(*p, KERB) for p in po], M_PANOT, normal=(0, 0, 1), uvscale=0.6)
        for i in range(8):
            p0, p1 = po[i], po[(i + 1) % 8]
            u, n, L = edge_frame(p0, p1)
            kerb.face([B(*p0, 0), B(*p1, 0), B(*p1, KERB), B(*p0, KERB)], M_KERB, normal=(n[0], n[1], 0))
        scene['blocks'].append({'origin': [ox, oy], 'poly': [to_m(p) for p in octagon(ox, oy)],
                                'pave': [to_m(p) for p in po]})
city_objs.append(pave.finish('Pavement'))
city_objs.append(kerb.finish('Kerbs'))

# zebra crossings beside every junction between the walkable blocks
zebra = MB()
CROSSINGS_X, CROSSINGS_Y = set(), set()
JX = sorted(V_STREETS)
JY = sorted(H_STREETS)


def near_block(ox, oy):
    return NEAR['x0'] <= ox <= NEAR['x1'] and NEAR['y0'] <= oy <= NEAR['y1']


for jx in JX:
    for jy in JY:
        for cx in (jx + V_WIDTH[jx] + 1.95, jx - 1.95):   # across the horizontal street
            if not any(near_block(ox, oy) and ox < cx < ox + BS and (oy + BS == jy or oy == jy + 4) for ox in COLS for oy in ROWS):
                continue
            CROSSINGS_X.add(cx)
            # (round 41, the user: "It's fine if they're crossing the street at crosswalks… as long as they stop, look
            # left and right, and then cross") each zebra for the people who cross: its two kerbs, where they wait, and
            # the way along the pavement away from the junction
            ou_ = 1.0 if cx > jx else -1.0
            scene.setdefault('zebras', []).append({'a': to_m((cx, jy + 0.8)), 'b': to_m((cx, jy + 3.2)),
                                                   'a2': to_m((cx + ou_ * 1.6, jy + 0.45)), 'b2': to_m((cx + ou_ * 1.6, jy + 3.55))})
            for k in range(6):
                y = jy + 1 + (k + 0.5) / 3
                zebra.abox(cx * T - 1.35, -y * T - 0.25, 0.005, cx * T + 1.35, -y * T + 0.25, 0.015, M_ZEBRA)
        for cy in (jy + 5.95, jy - 1.95):                 # across the vertical street (not La Rambla's)
            if V_WIDTH[jx] != 4 or not any(near_block(ox, oy) and oy < cy < oy + BS and (ox + BS == jx or ox == jx + 4) for ox in COLS for oy in ROWS):
                continue
            CROSSINGS_Y.add(cy)
            ou_ = 1.0 if cy > jy else -1.0
            scene.setdefault('zebras', []).append({'a': to_m((jx + 0.8, cy)), 'b': to_m((jx + 3.2, cy)),
                                                   'a2': to_m((jx + 0.45, cy + ou_ * 1.6)), 'b2': to_m((jx + 3.55, cy + ou_ * 1.6))})
            for k in range(6):
                x = jx + 1 + (k + 0.5) / 3
                zebra.abox(x * T - 0.25, -cy * T - 1.35, 0.005, x * T + 0.25, -cy * T + 1.35, 0.015, M_ZEBRA)
city_objs.append(zebra.finish('Zebras'))


def point_in(poly, p):
    """Is p inside the polygon (tiles)?"""
    inside = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < (x2 - x1) * (p[1] - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def crossing_clear(x, y, half=0.35):
    """(round 33, the user: "Check that there is nothing blocking walking paths or crosswalks where they meet the
    footpath… some benches are sitting in front of the crosswalks") clear of every zebra's landing — the pavement
    as wide as the crossing (2.7 m), plus 0.3 m, where people step off and on; half: the thing's own half-size
    (tiles). Every piece of street furniture asks this."""
    return all(abs(x - c) > 0.41 + 0.1 + half for c in CROSSINGS_X) and all(abs(y - c) > 0.41 + 0.1 + half for c in CROSSINGS_Y)


def kerb_side(x, y, d=0.2):
    """(round 33) a point on a city block's pavement, moved across it to d tiles in from the kerb (bins and signs
    from the 2D map stood in the middle of the pavement, in everyone's way); None when it isn't on one."""
    for ox_ in COLS:
        for oy_ in ROWS:
            po, pi_ = octagon(ox_, oy_, 1), octagon(ox_, oy_)
            if not (point_in(po, (x, y)) and not point_in(pi_, (x, y))):
                continue
            best = None
            for i in range(8):
                a, b = Vector(po[i]), Vector(po[(i + 1) % 8])
                ab = b - a
                t = max(0.0, min(1.0, (Vector((x, y)) - a).dot(ab) / ab.length_squared))
                q = a + ab * t
                dd = (Vector((x, y)) - q).length
                if best is None or dd < best[0]:
                    best = (dd, q, Vector((-ab.y, ab.x)).normalized())
            c = Vector(((po[0][0] + po[4][0]) / 2, (po[0][1] + po[4][1]) / 2))
            nin = best[2] if best[2].dot(c - best[1]) > 0 else -best[2]
            p = best[1] + nin * d
            return (p.x, p.y)
    return None

# ------------------------------------------------------------------ Meshy models

MESHY_DIR = MESHY


def meshy_file(f):
    return os.path.join(MESHY_DIR, f)


MESHY_MESH = {}
MESHY_TOP = {}

# The Meshy buildings, each set into one side of a block (build_kit_block in kit.py), measured from the
# models as fractions of their width:
#   wall   how far the front wall lies behind the front of the bounding box (balconies, steps and
#          awnings stick out further); the building is brought forward by this much so that its wall
#          stands on the street line like its neighbours'
#   body   half the width of the part of the front that stands on that line; beyond it the ends are
#          hidden by the corner houses, which wrap round to meet it
#   top    the height of its roof (after fix); it is sized so that this is level with the four-storey
#          corner houses either side (or by 'scale', against a 5-tile side)
#   fix    'forward': its top storey stood back behind a terrace, like a balcony; it is brought
#          forward onto the street line, flush with the front below
#          'flat': its pitched roof rose behind the parapet; it is replaced with a flat terrat
MESHY_BUILDINGS = {
    'building.glb': dict(wall=0.083, body=0.2685, top=0.805, fix=dict(kind='forward', z=0.6025, by=0.0795)),
    'building_yellow.glb': dict(wall=0.087, body=0.36, top=0.8125, fix=dict(kind='flat', z=0.8125)),
    'building_pink.glb': dict(wall=0.155, body=0.47, top=0.802, scale=0.62),     # a low two-storey palacete
}
MESHY_WING_UPPERS = 4
MESHY_TOP_H = GROUND_H + MESHY_WING_UPPERS * FLOOR_H - 0.08    # a hair under the corner houses, so roofs never fight
SIDE_M = (BS - 2 * CUT) * T                                     # a straight side of a block, metres
for _f, _M in MESHY_BUILDINGS.items():
    _M.setdefault('scale', MESHY_TOP_H / (_M['top'] * SIDE_M))
# where they stand: block origin -> (file, side). Sandra's building, the yellow café across Flor de
# Lliri, and the pink palacete further along it
MESHY_AT = {k: v for k, v in {HOME: ('building.glb', 4), (0, 26): ('building_yellow.glb', 0),
                              (13, 0): ('building_pink.glb', 4)}.items() if os.path.exists(meshy_file(v[0]))}
MESHY_HOME = HOME in MESHY_AT


# (round 41) Gaudí's houses from Meshy, each cut down to the house alone (tools/trim_meshy_batllo.py): landmarks.py
# gaudi_front sets it in the middle of its side, its wall on the street line, flush with its neighbours' (round 41, the
# user: "It looks like it's sunken into the block, so it needs to come out so the walls are flush");
# MESHY_GAUDI_GROUND: how far its wall stands behind the model's front-most part (its balconies), as a share of its
# width (tools/trim_meshy_batllo.py prints it); MESHY_GAUDI_TRIS: its detail ("the whole thing needs to be higher
# res… consider how much bigger that will create the file": 450,000 triangles, about 12 MB more than 150,000)
MESHY_GAUDI = {'casa_batllo': 'casa_batllo.glb'}
MESHY_GAUDI_GROUND = {'casa_batllo.glb': 0.1095}
MESHY_GAUDI_TRIS = 450000
# (round 41) where each model's own front door is, across its front from its left (as seen from the street), and its
# opening's width and height (metres, at the fitted size): our working door goes there
MESHY_GAUDI_DOOR = {'casa_batllo.glb': (0.865, 1.6, 2.4)}


def meshy_height(f):
    M = MESHY_BUILDINGS[f]
    return M['top'] * SIDE_M * M['scale']


def meshy_wing(f):
    """How much of the side (fraction) each wrapped-round corner bay takes: up to the Meshy building's
    main front, plus 5 cm of overlap so no daylight shows at the joint."""
    M = MESHY_BUILDINGS[f]
    return 0.5 - M['body'] * M['scale'] + 0.05 / SIDE_M


def fix_top(me, f):
    """Mends a Meshy building's top (MESHY_BUILDINGS[f]['fix']); the mesh is already normalised
    (width 1, front at y=0, going back along +y, bottom at z=0)."""
    M = MESHY_BUILDINGS.get(f, {})
    fix = M.get('fix')
    if not fix:
        return
    bm = bmesh.new()
    bm.from_mesh(me)
    z0 = fix['z']
    if fix['kind'] == 'forward':
        # the storey above the terrace comes forward onto the line of the wall below; the terrace's
        # balustrade, which would now be in the way, is tucked back inside it out of sight
        wall, half = M['wall'], M['body'] + 0.01
        for v in bm.verts:
            if v.co.z >= z0 and abs(v.co.x) <= half:
                if v.co.y >= wall + 0.035:
                    v.co.y -= fix['by']
                elif v.co.y >= wall - 0.013:
                    v.co.y += fix['by'] + 0.005
    elif fix['kind'] == 'flat':
        doomed = [fc for fc in bm.faces if fc.calc_center_median().z > z0 + 0.002]
        bmesh.ops.delete(bm, geom=doomed, context='FACES')
        near = [v.co for v in bm.verts if z0 - 0.04 < v.co.z <= z0 + 0.003]
        x0, x1 = min(c.x for c in near), max(c.x for c in near)
        y0, y1 = M['wall'] + 0.004, max(c.y for c in near)
        me.materials.append(ROOF_M[1])
        mi = len(me.materials) - 1
        uv = bm.loops.layers.uv.active
        face = bm.faces.new([bm.verts.new((x, y, z0)) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])
        face.material_index = mi
        face.normal_update()
        if face.normal.z < 0:
            face.normal_flip()
        if uv is not None:
            for lp in face.loops:
                lp[uv].uv = (lp.vert.co.x * 14, lp.vert.co.y * 14)
    bm.to_mesh(me)
    bm.free()


def meshy_mesh(f, target, fit, tex=0):
    """Imports a Meshy model once (per level of detail), lightens it to about `target` triangles and normalises it.
    fit='front': centred in x, front face (Meshy faces -Y here) at y=0, bottom at 0, unit width.
    fit='back':  the same, but with the back at y=0, so it sits against a wall and sticks out towards -Y.
    fit='base': centred in x and y, bottom at 0, unit height.
    tex: shrink its textures to this size (0 keeps them as they are)."""
    key = (f, target)
    if key in MESHY_MESH:
        return MESHY_MESH[key]
    cpath = meshy_cache_path(f, target, fit, tex)
    if os.path.exists(cpath) and os.path.getmtime(cpath) > os.path.getmtime(meshy_file(f)):
        with bpy.data.libraries.load(cpath) as (src, dst):
            dst.meshes = list(src.meshes)
        me = dst.meshes[0]
        for i, m in enumerate(me.materials):                   # (the build's own materials, e.g. a flattened roof's
            base = m.name.rsplit('.', 1)[0] if m else None      #  tiles, are the ones made this run, not copies)
            if base in MATS:
                me.materials[i] = MATS[base]
        hz = max(v.co.z for v in me.vertices)
        top = [v.co for v in me.vertices if v.co.z > 0.75 * hz]
        MESHY_TOP[f] = sum(top, Vector()) / max(1, len(top))
        MESHY_MESH[key] = me
        print('MESHY', f, len(me.polygons), 'faces (cached)')
        return me
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=meshy_file(f))
    new = [o for o in bpy.data.objects if o not in before]
    ob = next(o for o in new if o.type == 'MESH')
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    if tris > target:
        dec = ob.modifiers.new('lighten', 'DECIMATE')
        dec.ratio = target / tris
        bpy.ops.object.modifier_apply(modifier=dec.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    vs = [v.co.copy() for v in ob.data.vertices]
    xs, ys, zs = [v.x for v in vs], [v.y for v in vs], [v.z for v in vs]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    if fit in ('front', 'back'):
        k = 1 / (max(xs) - min(xs))
        ob.data.transform(Matrix.Translation((-cx, -(min(ys) if fit == 'front' else max(ys)), -min(zs))))
    else:
        k = 1 / (max(zs) - min(zs))
        ob.data.transform(Matrix.Translation((-cx, -cy, -min(zs))))
    ob.data.transform(Matrix.Diagonal((k, k, k, 1)))
    fix_top(ob.data, f)
    hz = max(v.co.z for v in ob.data.vertices)
    top = [v.co for v in ob.data.vertices if v.co.z > 0.75 * hz]
    MESHY_TOP[f] = sum(top, Vector()) / max(1, len(top))
    me = ob.data
    me.name = 'Meshy_' + os.path.splitext(os.path.basename(f))[0]
    if tex:
        for m in me.materials:
            if m.node_tree:
                for nd in m.node_tree.nodes:
                    if nd.type == 'TEX_IMAGE' and nd.image and nd.image.size[0] > tex:
                        nd.image.scale(tex, tex)
    for o in new:
        bpy.data.objects.remove(o)
    MESHY_MESH[key] = me
    # (round 26) kept for the next build: the slimming was two of its four minutes
    for m in me.materials:
        for nd in (m.node_tree.nodes if m and m.node_tree else []):
            if nd.type == 'TEX_IMAGE' and nd.image and nd.image.is_dirty:
                nd.image.pack()                                  # (shrunk above: keep it as shrunk)
    os.makedirs(os.path.dirname(cpath), exist_ok=True)
    bpy.data.libraries.write(cpath, {me}, fake_user=True, compress=True)
    print('MESHY', f, len(me.polygons), 'faces')
    return me


def meshy_cache_path(f, target, fit, tex):
    """(round 26) Where a Meshy model, slimmed and set straight, is kept between builds (bigfiles/cache/meshy/): named
    by everything that shapes it (the model, its triangle target, how it is fitted, its texture size, its MESHY_BUILDINGS
    entry), and remade when the model's file is newer. Delete the folder to remake them all."""
    import hashlib
    sig = repr((f, target, fit, tex, MESHY_BUILDINGS.get(f), 'v1'))
    name = os.path.splitext(f.replace(os.sep, '_'))[0]
    return os.path.join(MESHY_CACHE, '%s_%s.blend' % (name, hashlib.md5(sig.encode()).hexdigest()[:10]))


def meshy_place(f, target, fit, size, loc, rot_z, name, tex=0):
    """An instance of a Meshy model; repeated models share one mesh in the export."""
    ob = bpy.data.objects.new(name, meshy_mesh(f, target, fit, tex))
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (0, 0, rot_z)
    ob.scale = (size, size, size)
    city_objs.append(ob)
    if f == 'bench.glb':
        # (round 41, the user: "the benches should be solid… you can sit on them… For all the benches") where it
        # stands, the way its seat faces (the engine's x, z, and yaw: facing (sin, cos)) and its seat's height (the
        # model's seat 0.44 m over its base)
        scene.setdefault('benches', []).append([round(loc[0], 3), round(-loc[1], 3), round(rot_z, 4), round(loc[2] + 0.44, 3)])
    return ob


# ------------------------------------------------------------------ trees and lamps

trng = random.Random(42)


def in_walk(x, y, margin=0.0):
    return WALK['x0'] - margin <= x <= WALK['x1'] + margin and WALK['y0'] - margin <= y <= WALK['y1'] + margin


# (round 41, the user: "move the second tree, the one right in front of the building, out of the way") street trees
# left out, by where they stood (engine x, z): the one before Casa Batlló's middle
TREE_SKIP = [(-109.725, 58.035),
             (-45.375, -71.064),           # (round 41, the user: "on La Rambla, there's a tree in front of the front door")
             (-2.475, 99.877)]             # (round 41: the middle of a row of three, moved to Maria's door, below)


def plane_tree(tx, ty):
    trees = MB(uv=True)
    base = B(tx, ty, KERB)
    trees.abox(base.x - 0.5, base.y - 0.5, KERB + 0.002, base.x + 0.5, base.y + 0.5, KERB + 0.012, M_PIT)
    h = trng.uniform(2.9, 3.4)
    trees.cone(Matrix.Translation(base + Vector((0, 0, h / 2))), 8, 0.16, 0.12, h, M_BARK)
    for k in range(3):
        ang, tilt, L = trng.uniform(0, 6.28), trng.uniform(0.45, 0.75), trng.uniform(1.1, 1.6)
        M = Matrix.Translation(base + Vector((0, 0, h - 0.3))) @ Matrix.Rotation(ang, 4, 'Z') @ Matrix.Rotation(tilt, 4, 'X') @ Matrix.Translation((0, 0, L / 2))
        trees.cone(M, 6, 0.08, 0.04, L, M_BARK)
    canopy = Cards()
    top = base + Vector((0, 0, h + 1.35))
    canopy.clump(top, (1.3, 1.3, 0.8), 18, 1.0, M_PLANE_LEAVES, trng)          # filling, so it isn't see-through
    canopy.shell(top, (1.9, 1.9, 1.25), 85, 1.15, M_PLANE_LEAVES, trng)
    for k in range(5):                               # rounded lobes around the crown, like a cloud
        a = k * 1.2566 + trng.uniform(-0.3, 0.3)
        sub = top + Vector((math.cos(a) * 1.45, math.sin(a) * 1.45, trng.uniform(-0.35, 0.45)))
        canopy.shell(sub, (0.95, 0.95, 0.8), 24, 0.9, M_PLANE_LEAVES, trng)
    pm_ = to_m((tx, ty))
    if any(math.hypot(pm_[0] - q[0], pm_[1] - q[1]) < 0.6 for q in TREE_SKIP):
        return                                       # (made and dropped, so every later tree comes out as before)
    scene['trees'].append(pm_)
    idx = len(scene['trees']) - 1
    city_objs.append(trees.finish('Tree_%d' % idx))
    city_objs.append(canopy.finish('Leaves_%d' % idx))


MESHY_LAMP = os.path.exists(meshy_file('lamp.glb'))
lamps = MB()


def lamp_post(tx, ty, n):
    base = B(tx, ty, KERB)
    if MESHY_LAMP:
        h = 4.2
        meshy_mesh('lamp.glb', 4000, 'base')
        top = MESHY_TOP['lamp.glb']
        rot = math.atan2(n[1], n[0]) - math.atan2(top.y, top.x) if Vector((top.x, top.y)).length > 0.03 else 0.0
        meshy_place('lamp.glb', 4000, 'base', h, base, rot, 'MeshyLamp_%d' % len(scene['lamps']), 1024)
        lt = Matrix.Rotation(rot, 3, 'Z') @ (top * h) + base
        scene['lamps'].append({'pos': to_m((tx, ty)), 'light': [round(lt.x, 3), round(lt.z - 0.15, 3), round(-lt.y, 3)]})
        return
    lamps.abox(base.x - 0.15, base.y - 0.15, KERB, base.x + 0.15, base.y + 0.15, KERB + 0.4, M_LAMPPOST)
    lamps.cone(Matrix.Translation(base + Vector((0, 0, 1.9))), 8, 0.07, 0.045, 3.6, M_LAMPPOST)
    end = base + Vector((n[0] * 0.7, n[1] * 0.7, 3.75))
    lamps.box(Vector(((base.x + end.x) / 2, (base.y + end.y) / 2, end.z)), (n[0], n[1]), (-n[1], n[0]), 0.35, 0.025, 0.025, M_LAMPPOST)
    lamps.abox(end.x - 0.16, end.y - 0.16, end.z - 0.5, end.x + 0.16, end.y + 0.16, end.z - 0.1, M_LAMPGLASS)
    lamps.abox(end.x - 0.21, end.y - 0.21, end.z - 0.1, end.x + 0.21, end.y + 0.21, end.z - 0.02, M_LAMPPOST)
    scene['lamps'].append({'pos': to_m((tx, ty)), 'light': [round(end.x, 3), round(end.z - 0.35, 3), round(-end.y, 3)]})


# ------------------------------------------------------------------ the blocks

KEEP_CLEAR = []          # (x, y, r) in tiles: nothing else is put here (café terraces, bike stands, doorways)
SIGN_CHECK = []          # (round 37) every shop name: (its middle, outward normal, name), for the SIGNS check
DECO_DOORS = []          # every doorway in the kit's houses: (Blender point 0.8 m out, along the front), for the DOORS check
LIFE_BIKES = []          # bicycles parked about the streets (street_life.gd), each rideable
scene['people'] = []     # stretches of pavement or path where someone walks up and down: {'a', 'b'} (metres)


def clear_at(x, y, r=0.0):
    return all(math.hypot(x - a, y - b) > rr + r for a, b, rr in KEEP_CLEAR)


SIGN_FRONTS = []         # (round 37) (x, y, r) in tiles: the pavement in front of a shop's name (kit.py)


def sign_clear(x, y, r=0.0):
    """Clear of the doorways and of the pavement in front of every shop's name (for the low things: benches, planters,
    bins, bike stands, the corner's bougainvillea and lamp; not the street trees)."""
    return clear_at(x, y, r) and all(math.hypot(x - a, y - b) > rr + r for a, b, rr in SIGN_FRONTS)


def drop_since(n_objs, n_obs, n_bikes):
    """(round 37) Take away what was just placed (it stood in front of a sign). It is still made first, so the dice
    are thrown as before and nothing else in the city moves (the user: "It didn't mean remove EVERYTHING near it")."""
    for o in city_objs[n_objs:]:
        bpy.data.objects.remove(o, do_unlink=True)
    del city_objs[n_objs:]
    del scene['obstacles'][n_obs:]
    del LIFE_BIKES[n_bikes:]


# Sandra's door: the smaller portal on the right of her Meshy building (house number 4, kit.py)
o0, o1 = octagon(*HOME)[4], octagon(*HOME)[5]
du, dn, _ = edge_frame(o0, o1)
dm = lerp2(o0, o1, meshy_wing('building.glb') / 2) if MESHY_HOME else lerp2(o0, o1, 0.5)
KEEP_CLEAR += [(dm[0], dm[1], 0.75), (4.5, 9.0, 0.75)]          # her door, and the grand door beside it
for _x in (1.95, 7.15):
    KEEP_CLEAR.append((_x, 9.42, 0.3))                           # Montse's bench and its pair
# (round 23) Bicis Jordi, on the north side of Carrer de València (block (-30, 0), its west three bays: kit.py
# JORDI_HOUSE): the pavement in front of its west window is Jordi's and his bikes', a plane tree stands at the kerb in
# front of its west window (the bikes stand out in front of the east one: kit.py signs_and_wares), and a lamp across
# the street lights the shop
JORDI_SPOT = (-25.9, 9.55)                                        # (our tiles) where he stands, by his bikes
KEEP_CLEAR += [(JORDI_SPOT[0], JORDI_SPOT[1], 0.6), (-27.5, 9.82, 0.5), (-26.0, 12.25, 0.3)]

# every block, from the facade kit (kit.py), with the 2D game's buildings set into them (landmarks.py)
exec(open(os.path.join(HERE, 'kit.py')).read())
exec(open(os.path.join(BUILD, 'landmarks.py')).read())
SPECIALS = {}
OPEN_BLOCKS = set()
RELIEF_BLOCKS = set()
PLAQUE_CHECK = []                 # (centre, outward normal, street, block): each street plaque, to check it can be seen
for b2 in W2['BUILDINGS']:
    SPECIALS.setdefault((COLS[b2['block'][0]], ROWS[b2['block'][1]]), []).append(b2)
for ox in COLS:
    for oy in ROWS:
        specs = SPECIALS.get((ox, oy), [])
        if build_special_block(ox, oy, specs):
            continue
        m = MESHY_AT.get((ox, oy))
        meshy = dict(file=m[0], edge=m[1]) if m else None
        if (ox, oy) == HOME:
            build_kit_block(ox, oy, HOUSES, meshy=meshy, with_garden=True, sandra=True)
            continue
        houses = override_houses(ox, oy, gen_houses(ox, oy, skip=(m[1],) if m else ()))
        brng = random.Random(ox * 977 + oy)
        for sp in specs:
            edge = {'N': 0, 'E': 2, 'S': 4, 'W': 6}[sp['face']]
            if m and m[1] == edge:
                # a Meshy building is this side: its middle door is the way in
                o_ = octagon(ox, oy)
                u_, n_, L_ = edge_frame(o_[edge], o_[(edge + 1) % 8])
                entrance_at(sp, Frame((B(*o_[edge]).x, B(*o_[edge]).y), u_, n_), L_ * T / 2, 2.6, 1.6, arch=0.8)   # (its doors are arched)
            elif sp['type'] == 'shop':
                houses[edge] = [shop_house(sp)]
            elif sp['type'] == 'gaudi':
                houses[edge] = [dict(bays=5, uppers=4 if sp['id'] != 'casa_mila' else 5, facade='#e8d6b4', style='classic',
                                     ground=['shop'] * 5, balc=['iron'] * 5, shop=None, plants=['none'], seed=brng.randrange(99999),
                                     num=1, gaudi=sp['id'], entrance=sp, tribuna=[])]
                if sp['id'] in MESHY_GAUDI and os.path.exists(meshy_file(MESHY_GAUDI[sp['id']])):
                    # (round 41, the user: "do some of the Gaudí facades in Meshy, because it will look better… cut away the
                    # edges and fit it") Meshy's own house at its real proportions in the middle of the side, an ordinary
                    # house either side of it, as its neighbours stand on Passeig de Gràcia
                    houses[edge][0].update(bays=8, meshy=MESHY_GAUDI[sp['id']])
                    houses[edge] = [gen_house(brng, 2, False, 41), houses[edge][0], gen_house(brng, 2, False, 45)]
            elif sp['type'] == 'apt':
                houses[edge] = apt_houses(sp, brng)
        build_kit_block(ox, oy, houses, meshy=meshy)

# the yellow café across from Sandra's: its tables right outside, either side of the door
if (0, 26) in MESHY_AT and os.path.exists(meshy_file('cafe.glb')):
    _o0, _o1 = octagon(0, 26)[0], octagon(0, 26)[1]
    _u, _n, _ = edge_frame(_o0, _o1)
    cafe_terrace(Frame((B(*_o0).x, B(*_o0).y), _u, _n), SIDE_M / 2, 4, random.Random(5), 'MeshyCafe')

# ------------------------------------------------------------------ the pavements
# Each straight stretch of pavement gets a character of its own, so the streets aren't all the same:
#   trees   a full row of plane trees
#   sparse  two or three trees, wide apart
#   empty   nothing: people walk there instead
#   mixed   trees further apart, with a bench, a planter, recycling bins or a bike stand between them
# Sandra's block keeps its full rows. People are also put on some of the other stretches.

prng = random.Random(9)
BENCHES = os.path.exists(meshy_file('bench.glb'))
SPARE_BIKES = [('#b8423a', '#efe6d2', True), ('#3a5a8a', '#efe6d2', False), ('#e8dcc0', '#c9a24a', True),
               ('#2f2f35', '#c9ccd0', False), ('#6e8f4a', '#f2ead8', True), ('#c46a8a', '#fff3ea', True)]
FIXED_KIND = {(0, 26, 0): 'trees', (13, 0, 4): 'mixed'}


def tree_ok(x, y):
    return (in_walk(x, y) and all(abs(x - c) > 0.62 for c in CROSSINGS_X) and all(abs(y - c) > 0.62 for c in CROSSINGS_Y)
            and clear_at(x, y, 0.3))


def street_bench(x, y, n, name):
    """A Meshy bench by the house fronts, facing the road (n: outward, Blender)."""
    if not BENCHES:
        return
    meshy_place('bench.glb', 5000, 'base', 0.86, B(x, y, KERB), math.atan2(n[1], n[0]) + math.pi / 2, name, 1024)
    scene['obstacles'].append({'pos': to_m((x, y)), 'off': [0, 0], 'r': 0.75})


def planter(x, y, u):
    c = B(x, y, KERB)
    g = MB()
    g.box(c + Vector((0, 0, 0.28)), u, (-u[1], u[0]), 0.8, 0.3, 0.28, mat('Planter', '#b9ad9a', 0.9))
    cards = Cards()
    cards.clump(c + Vector((0, 0, 0.75)), (0.75, 0.3, 0.3), 26, 0.55, M_SHRUB, prng)
    cards.clump(c + Vector((0, 0, 0.8)), (0.6, 0.25, 0.2), 8, 0.45, prng.choice((M_GERANIUM_CARD, M_PINK, M_DAISY)), prng)
    k = len(scene['obstacles'])
    city_objs.append(g.finish('Planter_%d' % k))
    city_objs.append(cards.finish('PlanterLeaves_%d' % k))
    scene['obstacles'].append({'pos': to_m((x, y)), 'off': [0, 0], 'r': 0.85})


def bike_stand(x, y, u, count):
    """A steel hoop stand by the kerb with a bike or two locked to it (rideable)."""
    c = B(x, y, KERB)
    g = MB()
    U = Vector((u[0], u[1], 0))
    for k in range(count + 1):
        p = c + U * (k - count / 2) * 0.9
        N = Vector((-u[1], u[0], 0))
        for s in (-1, 1):
            g.cone(Matrix.Translation(p + N * s * 0.3 + Vector((0, 0, 0.4))), 6, 0.025, 0.025, 0.8, M_IRON)
        g.box(p + Vector((0, 0, 0.8)), (-u[1], u[0]), u, 0.32, 0.025, 0.025, M_IRON)
        # (round 33, the user: "She can run through the bike lock stands" — each hoop is solid now; the bikes locked
        # to them are solid in the game itself, street_life.gd add_bike)
        scene['obstacles'].append({'pos': to_m((p.x / T, -p.y / T)), 'off': [0, 0], 'r': 0.32})
    city_objs.append(g.finish('BikeStand_%d' % len(city_objs)))
    for k in range(count):
        if not SPARE_BIKES:
            break
        fc, gc, basket = SPARE_BIKES.pop()
        p = c + U * ((k + 0.5) - count / 2) * 0.9
        q = to_m((p.x / T, -p.y / T))
        dirv = (-u[1], -u[0])                       # across the pavement, front wheel towards the road
        LIFE_BIKES.append({'pos': q, 'yaw': round(math.atan2(-dirv[0], -dirv[1]), 3), 'frame': fc, 'guard': gc,
                           'basket': basket, 'flowers': basket and prng.random() < 0.5, 'rack': prng.random() < 0.6})


# (round 41, the user: "there's someone who's always pacing in front of the university. Could you just move them somewhere
# else in the city?") a walker whose stretch passes a door listed here walks instead along WALKER_ELSEWHERE: La Rambla's
# west pavement (metres; facing the east pavement's walker there)
WALKER_SKIP_DOORS = [(30.4, 100.65)]                       # (the Universitat Pompeu Fabra's door)
WALKER_ELSEWHERE = [([-67.815, 50.773], [-67.815, 64.727])]


def walker(p0, p1):
    """Someone walks up and down between two points (tiles)."""
    a_, b_ = to_m(p0), to_m(p1)
    for dx_, dz_ in WALKER_SKIP_DOORS:
        ux_, uz_ = b_[0] - a_[0], b_[1] - a_[1]
        L2_ = ux_ * ux_ + uz_ * uz_ or 1.0
        t_ = max(0.0, min(1.0, ((dx_ - a_[0]) * ux_ + (dz_ - a_[1]) * uz_) / L2_))
        if math.hypot(a_[0] + ux_ * t_ - dx_, a_[1] + uz_ * t_ - dz_) < 3.0 and WALKER_ELSEWHERE:
            a_, b_ = WALKER_ELSEWHERE.pop(0)
            break
    scene['people'].append({'a': a_, 'b': b_})


for ox in COLS:
    for oy in ROWS:
        if not near_block(ox, oy):
            continue
        po = octagon(ox, oy, 1)
        outer = octagon(ox, oy)
        brng = random.Random(ox * 31 + oy * 7)
        for i in range(8):
            p0, p1 = po[i], po[(i + 1) % 8]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            L = math.hypot(dx, dy)
            nx, ny = dy / L, -dx / L                    # outward, tile coords
            u = (dx / L, -dy / L)                       # along, Blender
            nB = (nx, -ny)                              # outward, Blender

            def at(s, d):                              # along the pavement s, in from the kerb d (tiles)
                return (p0[0] + dx / L * s - nx * d, p0[1] + dy / L * s - ny * d)
            if i % 2:
                # chamfered corner: a lamp, sometimes bougainvillea climbing the corner house; where the corner
                # house has its door on the corner, no bougainvillea, and the lamp stands to one side of it
                fm_ = lerp2(outer[i], outer[(i + 1) % 8], 0.5)
                door_here = not clear_at(fm_[0] + nx * 0.25, fm_[1] + ny * 0.25)
                sign_here = not sign_clear(fm_[0] + nx * 0.25, fm_[1] + ny * 0.25)   # (round 37: a shop's name over the corner)
                # (round 33: 0.5 m from the kerb, was 1.0 — out of the way; round 37, the user: "keep the lamp poles on the
                # pavement away from its edge" — its foot, 0.3 m round, hugged the kerb: now 0.83 m in)
                mx, my = at(L * (0.84 if sign_here else 0.5), 0.25)
                if in_walk(mx, my, 1.0):
                    lamp_post(mx, my, (nx, -ny))
                n0_ = (len(city_objs), len(scene['obstacles']), len(LIFE_BIKES))
                if (ox, oy) != HOME and not door_here and brng.random() < 0.4:
                    oo0, oo1 = outer[i], outer[(i + 1) % 8]
                    ue, ne, _ = edge_frame(oo0, oo1)
                    base = B(*lerp2(oo0, oo1, 0.5))
                    cards = Cards()
                    geo3 = MB()
                    geo3.box(base + Vector((ne[0] * 0.45, ne[1] * 0.45, KERB + 0.3)), ue, ne, 0.9, 0.3, 0.3, M_PLINTH)
                    # (round 35, the everything-visit: it spread to 1.5 m each way at the top, in a box square to the
                    # streets, so on the slanting corner it wrapped round onto both fronts, over shop names, awnings and
                    # the street plaques; now it stays on its own corner, thickening upwards)
                    for k in range(9):                   # a cascade: thin at the bottom, spilling wider at the top
                        hgt = 0.6 + k * 0.42
                        spread = 0.3 + 0.055 * k
                        c = base + Vector((ne[0] * 0.3, ne[1] * 0.3, KERB + hgt))
                        cards.clump(c, (spread * abs(ue[0]) + 0.18, spread * abs(ue[1]) + 0.18, 0.3), 5 + k, 0.75, M_BOUG, brng)
                    city_objs.append(cards.finish('Bougainvillea_%d_%d_%d' % (ox, oy, i)))
                    city_objs.append(geo3.finish('BougPlanter_%d_%d_%d' % (ox, oy, i)))
                    scene['obstacles'].append({'pos': to_m(lerp2(oo0, oo1, 0.5)), 'off': [round(ne[0] * 0.45, 3), round(-ne[1] * 0.45, 3)], 'r': 0.95})
                    if sign_here:
                        drop_since(*n0_)                 # (round 37: not in front of the shop's name)
                # the street name plaques on the corner house, one for each street
                oo0, oo1 = outer[i], outer[(i + 1) % 8]
                ue, ne, _ = edge_frame(oo0, oo1)
                sides = {0: ('H', oy - 4), 2: ('V', ox + 9), 4: ('H', oy + 9), 6: ('V', ox - 4)}
                for frac, side in ((0.27, (i - 1) % 8), (0.73, (i + 1) % 8)):
                    kind, at_ = sides[side]
                    name = (H_STREETS if kind == 'H' else V_STREETS).get(at_)
                    if not name:
                        continue
                    p = lerp2(oo0, oo1, frac)
                    if kind == 'H':
                        for sn_, (sx0_, sy0_, sx1_, sy1_) in SEGMENT.items():
                            if sx0_ + 4 < p[0] < sx1_ and sy0_ - 1.0 < p[1] < sy1_ + 1.0:
                                name = sn_                    # (on the named stretch its own name: rule 10 #51d)
                    w = 0.04 * len(name) + 0.1
                    g2 = MB()
                    # (on the university's brick front the plaque stands proud of its pilasters and window arches)
                    pout = 0.27 if (ox, oy) in RELIEF_BLOCKS else 0.0
                    p = (p[0] + ne[0] * pout / T, p[1] - ne[1] * pout / T)
                    if (ox, oy) in OPEN_BLOCKS:
                        # (round 35: its own post 0.6 m out from the block's edge — on the edge the plaque ran into the
                        # Sagrada Família's corner columns)
                        p = (p[0] + ne[0] * 0.6 / T, p[1] - ne[1] * 0.6 / T)
                    if pout:
                        g2.box(B(*p, 2.92) - Vector((ne[0] * pout / 2, ne[1] * pout / 2, 0)), ue, ne, 0.05, pout / 2, 0.05, M_LAMPPOST)   # its bracket
                    g2.box(B(*p, 2.92) + Vector((ne[0] * 0.03, ne[1] * 0.03, 0)), ue, ne, w, 0.03, 0.18, M_MARBLE)
                    if (ox, oy) in OPEN_BLOCKS:
                        # no corner house to hang on (a park, a landmark in its grounds): a slim post of its own
                        g2.cone(Matrix.Translation(B(*p, (KERB + 3.1) / 2) - Vector((ne[0] * 0.03, ne[1] * 0.03, 0))), 8, 0.045, 0.04,
                                3.1 - KERB, M_LAMPPOST)
                        scene['obstacles'].append({'pos': to_m(p), 'off': [0, 0], 'r': 0.18})   # (round 33: solid, as a lamp post is)
                    city_objs.append(g2.finish('Plaque_%d_%d_%d_%s' % (ox, oy, i, kind)))
                    city_objs.append(text_obj(name, 0.13, M_PLAQUE_TEXT, B(*p, 2.92) + Vector((ne[0] * 0.065, ne[1] * 0.065, 0)),
                                              facing(ne), 'PlaqueText_%d_%d_%d_%s' % (ox, oy, i, kind)))
                    scene['plaques'].append({'pos': to_m((p[0] + ne[0] * 0.25, p[1] - ne[1] * 0.25)), 'text': name})
                    PLAQUE_CHECK.append((B(*p, 2.92) + Vector((ne[0] * 0.07, ne[1] * 0.07, 0)), Vector((ne[0], ne[1], 0)), name, (ox, oy)))
                continue
            kind = 'trees' if (ox, oy) == HOME else FIXED_KIND.get((ox, oy, i)) or \
                prng.choices(['trees', 'sparse', 'empty', 'mixed'], [3, 2.5, 2, 2.5])[0]
            if kind == 'trees':
                s = 0.4 + trng.uniform(0, 0.25)
                while s < L - 0.45:
                    x, y = at(s, 0.25)
                    if tree_ok(x, y):
                        plane_tree(x, y)
                    s += trng.uniform(1.15, 1.45)
            elif kind == 'sparse':
                for s in sorted(prng.sample([1.2, 2.4, 3.6, 4.8, 6.0], prng.choice((2, 3)))):
                    x, y = at(min(s, L - 0.6), 0.25)
                    if tree_ok(x, y):
                        plane_tree(x, y)
            elif kind == 'mixed':
                s = 0.6 + prng.uniform(0, 0.4)
                k = 0
                while s < L - 0.6:
                    if k % 2 == 0:
                        x, y = at(s, 0.25)
                        if tree_ok(x, y):
                            plane_tree(x, y)
                    else:
                        what = prng.choices(['bench', 'planter', 'bins', 'bikes', 'nothing'], [4, 2.5, 1.5, 2, 1])[0]
                        if what == 'bench':
                            x, y = at(s, 0.58)
                            if clear_at(x, y, 0.3) and crossing_clear(x, y, 0.3) and sign_clear(x, y, 0.3):
                                street_bench(x, y, nB, 'StreetBench_%d' % len(city_objs))
                        elif what == 'planter':
                            x, y = at(s, 0.22)
                            if clear_at(x, y, 0.3) and crossing_clear(x, y, 0.3):
                                n0_ = (len(city_objs), len(scene['obstacles']), len(LIFE_BIKES))
                                planter(x, y, u)
                                if not sign_clear(x, y, 0.3):
                                    drop_since(*n0_)     # (round 37: not in front of a shop's name)
                        elif what == 'bins':
                            x, y = at(s, 0.25)
                            if clear_at(x, y, 0.4) and crossing_clear(x, y, 0.35):
                                n0_ = (len(city_objs), len(scene['obstacles']), len(LIFE_BIKES))
                                bmb, bcards = MB(uv=True), Cards()
                                bin_bay(bmb, bcards, B(x, y, KERB), u, nB, prng.choice([(1, 2), (0, 3), (4, 1)]), prng)
                                city_objs.append(bmb.finish('Bins_%d' % len(city_objs)))
                                city_objs.append(bcards.finish('Plants_bins_%d' % len(city_objs)))
                                for sx in (-0.29, 0.0, 0.29):
                                    scene['obstacles'].append({'pos': to_m((x + u[0] * sx, y - u[1] * sx)), 'off': [0, 0], 'r': 0.55})
                                if not sign_clear(x, y, 0.4):
                                    drop_since(*n0_)     # (round 37: not in front of a shop's name)
                        elif what == 'bikes':
                            x, y = at(s, 0.25)
                            if clear_at(x, y, 0.4) and crossing_clear(x, y, 0.45) and SPARE_BIKES:
                                n0_ = (len(city_objs), len(scene['obstacles']), len(LIFE_BIKES))
                                bike_stand(x, y, u, prng.choice((1, 2)))
                                if not sign_clear(x, y, 0.4):
                                    drop_since(*n0_)     # (round 37: not in front of a shop's name)
                    s += prng.uniform(1.2, 1.5)
                    k += 1
            # people: always on the empty stretches, often elsewhere
            if (ox, oy) != HOME and in_walk(*at(L / 2, 0.55)) and (kind == 'empty' or prng.random() < (0.45 if kind == 'sparse' else 0.25)):
                walker(at(0.8, 0.55), at(L - 0.8, 0.55))

# Sandra's street: planters between the trees, and the benches (Montse's and its pair), sized so the
# seat is 0.44 m up, low enough for Montse's short legs
for (ox, oy), i in ((HOME, 4),):
    po = octagon(ox, oy, 1)
    p0, p1 = po[i], po[(i + 1) % 8]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = dy / L, -dx / L
    for s in (0.25, 0.75):
        x, y = p0[0] + dx * s - nx * 0.22, p0[1] + dy * s - ny * 0.22
        if any(math.hypot(x * T - t[0], y * T - t[1]) < 1.8 for t in scene['trees']) or not clear_at(x, y, 0.4) \
                or not crossing_clear(x, y, 0.3):
            continue
        planter(x, y, (dx / L, -dy / L))
if BENCHES:
    # (round 33, the user: "Remove the bench from outside of her building" — the one by her door, at 7.15, is gone; the
    # other stands along the block towards the corner)
    for k, x in enumerate((1.95,)):
        # (round 33: it stood in front of a crossing; slid along the pavement towards the block's middle until clear)
        while not crossing_clear(x, 9.42, 0.3):
            x += 0.2 if x < BS / 2 else -0.2
        meshy_place('bench.glb', 5000, 'base', 0.86, B(x, 9.42, KERB), 0.0, 'MeshyBench_%d' % k, 1024)
        scene['obstacles'].append({'pos': to_m((x, 9.42)), 'off': [0, 0], 'r': 0.75})
mallorca_bins()

# the door record for the engines
door_m = to_m(dm)
out_n = [dn[0], -dn[1]]                                   # Blender XY -> engine XZ
scene['door'] = {
    'pos': door_m, 'normal': out_n, 'name': 'Flor de Lliri, 4',
    'plaque': "FLOR DE LLIRI, 4. The doorbell reads SANDRA & ROSA. Under it, a little paper German flag has been taped on, very slightly crooked. Home.",
    'lamp': [door_m[0] + out_n[0] * 0.3, 2.85, door_m[1] + out_n[1] * 0.3],
    'size': [1.24, 2.24], 'base': KERB,                   # the opening, for the glow round it
}
ENTRANCES.append(dict(scene['door'], id='apt_sandra', int='int_sandra'))

# ------------------------------------------------------------------ the park, the beach and the hills
plane_tree(-27.5, 9.82)                                          # (Bicis Jordi: the tree at the kerb, the lamp across)
# (round 41, the user: "Could you just move that across the road to in front of the Berlin Cafe? Just to the north of
# its door") the tree from before the door at La Rambla's north-east corner, on the café's pavement, north of its door
plane_tree(-66.825 / T, -72.6 / T)
# (round 41, the user: "Move a tree from somewhere else where there's three trees next to each other in front. And put
# it outside Maria's house. Somewhere pleasant") the middle of the three nearest her, on her pavement beside her door
plane_tree(18.05 / T, 75.075 / T)
lamp_post(-26.0, 12.25, (0, 1))          # (round 37: 0.83 m from the kerb, which is to its north; was 0.33)
exec(open(os.path.join(BUILD, 'world2d.py')).read())

city_objs.append(lamps.finish('Lamps'))
scene.setdefault('street_life', {})['bikes'] = LIFE_BIKES
# the names the banner shows, most particular first (places, then the named stretch, then the streets)
def rect_m(x0, y0, x1, y1):
    return [round(x0 * T, 3), round(y0 * T, 3), round(x1 * T, 3), round(y1 * T, 3)]


scene['streets'] = scene.get('north', {}).get('streets', []) + [{'name': "Jardí del Lliri", 'rect': rect_m(HOME[0] + COURT, HOME[1] + COURT, HOME[0] + BS - COURT, HOME[1] + BS - COURT)},
                    # (round 22: the north) the names shown as she walks into each place, in metres
                    {'name': 'Park Güell', 'rect': [min(p[0] for p in NORTH.PARK_WALL), min(p[1] for p in NORTH.PARK_WALL),
                                                    max(p[0] for p in NORTH.PARK_WALL), -146.0]},      # (round 25: its new wall)
                    {'name': 'Tibidabo', 'rect': [NORTH.FAIR[0] - 2, NORTH.FAIR[1] - 2, NORTH.FAIR[2] + 2, NORTH.FAIR[3] + 2]},
                    {'name': 'Gràcia', 'rect': [18.0, -160.0, 126.0, -100.5]},
                    {'name': 'Collserola', 'rect': [-240.0, -330.0, 18.0, -103.0]},
                    {'name': 'Parc de la Ciutadella', 'rect': rect_m(68 - OX, 71 - OY, 77 - OX, 80 - OY)},      # (round 21: a block down)
                    {'name': 'Platja de la Barceloneta', 'rect': rect_m(-80, W2['PASSEIG_Y1'] + 1 - OY, 120, 120)},
                    {'name': 'Passeig Marítim', 'rect': rect_m(-80, W2['PASSEIG_Y1'] - 1 - OY, 120, W2['PASSEIG_Y1'] + 1 - OY)},
                    {'name': 'El Bosc', 'rect': rect_m(W2['CITY'][2] + 1 - OX, -50, 120, W2['PASSEIG_Y1'] - 1 - OY)},
                    {'name': 'Riu Llobregat', 'rect': rect_m(-80, -50, W2['CITY'][0] - 1 - OX, W2['PASSEIG_Y1'] - 1 - OY)},
                    {'name': 'Collserola', 'rect': rect_m(-80, -80, 120, W2['CITY'][1] - 1 - OY)}]
for name, (x0, y0, x1, y1) in SEGMENT.items():
    scene['streets'].append({'name': name, 'rect': rect_m(x0, y0, x1, y1)})
for y, name in H_STREETS.items():
    scene['streets'].append({'name': name, 'rect': rect_m(CITY[0], y, CITY[2], y + 4)})
for x, name in V_STREETS.items():
    scene['streets'].append({'name': name, 'rect': rect_m(x, CITY[1], x + V_WIDTH[x], CITY[3])})
scene['spawn'] = {'pos': mT(W2['SPAWN']['x'] + 0.5, W2['SPAWN']['y'] + 0.5), 'facing': math.pi}


def export(objs, path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
        for ch in o.children_recursive:
            ch.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True)


# the brass plaques beside the doors: a small brass plate at eye height with the building's name engraved
_pl = MB()
_dg0 = bpy.context.evaluated_depsgraph_get()
for j, (foot, U_, N_, name, ent) in enumerate(DOOR_PLAQUES):
    c = foot + N_ * 0.04 + Vector((0, 0, KERB + 1.45))
    # where deep stonework (a Gaudí front, a portal, a portico) would swallow it, it stands on a little post
    # of its own a step out from the wall instead, and the game reads it there
    origin = c + N_ * 2.0 + Vector((0, 0, -0.6))
    hit, _l, _n, _i, ob, _m = bpy.context.scene.ray_cast(_dg0, origin, (c - origin).normalized(), distance=(c - origin).length - 0.02)
    if hit:
        c = foot + N_ * 1.2 + Vector((0, 0, KERB + 1.25))
        _pl.cone(Matrix.Translation(Vector((c.x, c.y, (KERB + c.z - 0.1) / 2))), 8, 0.035, 0.03, c.z - 0.1 - KERB, M_IRON)
        ent['plaque_pos'] = bl_m(c + N_ * 0.5)
        print('DOOR PLAQUE on a post:', name)
    _pl.box(c, (U_.x, U_.y), (N_.x, N_.y), 0.17, 0.012, 0.115, M_BRASS)
    _pl.box(c - N_ * 0.02, (U_.x, U_.y), (N_.x, N_.y), 0.19, 0.01, 0.135, M_IRON)          # its dark mount
    words = name.split()
    lines = [name] if len(name) <= 14 or len(words) < 2 else [' '.join(words[:len(words) // 2]), ' '.join(words[len(words) // 2:])]
    sz = min(0.05, 0.3 / (0.58 * max(len(l) for l in lines)))
    for k, ln in enumerate(lines):
        city_objs.append(text_obj(ln, sz, M_BRASS_TEXT, c + N_ * 0.014 + Vector((0, 0, (len(lines) - 1) * sz * 0.6 - k * sz * 1.2)),
                                  facing((N_.x, N_.y)), 'DoorPlaqueText_%d_%d' % (j, k)))
    PLAQUE_CHECK.append((c + N_ * 0.02, Vector((N_.x, N_.y, 0)), 'door: ' + name, None))
city_objs.append(_pl.finish('DoorPlaques'))

# (round 33, the user: "make the glow line up with the doors… Also have a sign outside") every way in that has no
# shop sign of its own gets a hanging sign: a painted board on an iron bracket out from the wall beside the door, high
# enough to walk under, its name on both faces, read from along the street. (The park's doors have signs on posts,
# north_build.py.)
M_HANGBOARD = mat('HangSignBoard', '#2f4a3a', 0.6)
M_HANGEDGE = mat('HangSignEdge', '#c9a24a', 0.4, 0.6)
_hs = MB()
_HANG_SKIP = {'cafe_berlin', 'carrefour', 'cafe_rambla', 'torro_mar', 'torro_joan', 'bookshop'}
_north_ids = set(scene.get('north', {}).get('doors', []))
for j, e in enumerate(scene['entrances']):
    if e['id'] in _HANG_SKIP or e['id'] in _north_ids:
        continue
    gx_, gz_ = e.get('glow', e['pos'])
    Nb = Vector((e['normal'][0], -e['normal'][1], 0)).normalized()
    Ub = Vector((Nb.y, -Nb.x, 0)) * -1.0 * e.get('sign_side', 1.0)   # (the side away from the brass plaque; -1: over it)
    w_, h_ = e['size']
    zt = e.get('base', KERB) + max(2.55, min(h_ + 0.35, 3.2))
    root = Vector((gx_, -gz_, zt)) + Ub * (w_ / 2 + 0.7)
    words = e['name']
    # (round 34, the user: "The signs should be smaller without the wood covering it") a small painted plate, no
    # framed board round it, its name filling it
    sz = 0.085
    hw = 0.06 + 0.024 * len(words)
    # (round 41, the user: "there's a green sign sticking out of the new Gaudí building": a Meshy front's stonework
    # stands proud of its wall, so its bracket reaches further out, the sign hanging clear of it: 'sign_out')
    so_ = e.get('sign_out', 0.0)
    mid = root + Nb * (0.2 + hw + so_)
    _hs.tube(root + Vector((0, 0, 0.2)), root + Nb * (0.3 + 2 * hw + so_) + Vector((0, 0, 0.2)), 0.014, M_IRON, 6)    # the bracket
    _hs.tube(root - Vector((0, 0, 0.05)), root + Nb * (0.22 + so_) + Vector((0, 0, 0.2)), 0.011, M_IRON, 6)
    for sx in (-1, 1):
        _hs.tube(mid + Nb * (sx * hw * 0.8) + Vector((0, 0, 0.2)), mid + Nb * (sx * hw * 0.8) + Vector((0, 0, 0.12)), 0.007, M_IRON, 4)
    _hs.box(mid, (Nb.x, Nb.y), (Ub.x, Ub.y), hw, 0.012, 0.085, M_HANGBOARD)
    for k, side in enumerate((1, -1)):
        city_objs.append(text_obj(words, sz, M_SIGN_TEXT, mid + Ub * (side * 0.016) - Vector((0, 0, sz * 0.3)),
                                  facing((Ub.x * side, Ub.y * side)), 'HangSignText_%d_%d' % (j, k)))
city_objs.append(_hs.finish('HangSigns'))

# every street plaque must be in plain view: look at it from a step out in the street (and a little to each side)
_dg = bpy.context.evaluated_depsgraph_get()
_hidden = 0
for (c, n, street, blk) in PLAQUE_CHECK:
    for side in (0.0, 0.25, -0.25):
        sv = Vector((-n.y, n.x, 0)) * side
        origin = c + n * 2.0 + sv + Vector((0, 0, -0.6))
        target = c + sv * 0.5
        hit, loc, nrm, idx, ob, mtx = bpy.context.scene.ray_cast(_dg, origin, (target - origin).normalized(), distance=(target - origin).length - 0.01)
        if hit and not ob.name.startswith(('Plaque', 'PlaqueText', 'DoorPlaque')):
            print('PLAQUE_HIDDEN', street, blk, 'behind', ob.name)
            _hidden += 1
            break
print('PLAQUES checked', len(PLAQUE_CHECK), 'hidden', _hidden)
# (round 37, the user: "All signs should be visible and have nothing blocking them") every sign — street plaques, door
# plaques, shop names — as Sandra sees it: from her eye height 3.5 m away on the pavement, straight on and from either
# side along it. The buildings' own stonework, balconies and awnings don't count (the PLAQUES check above is for
# those); anything put in front of a sign does: straight on nothing may be in the way, and not from both sides.
_hidden = 0
_signs = [(c, n, s) for (c, n, s, _b) in PLAQUE_CHECK] + SIGN_CHECK
_FABRIC = ('Plaque', 'PlaqueText', 'DoorPlaque', 'HangSign', 'Block_', 'Detail_', 'Ground', 'Gracia', 'Meshy', 'Landmark',
           'Sagrada', 'UPF', 'North')
for (c, n, what) in _signs:
    sv = Vector((-n.y, n.x, 0))
    bad = []
    for ang in (0.0, 0.6, -0.6):
        origin = c + (n * math.cos(ang) + sv * math.sin(ang)) * 3.5
        origin.z = c.z if what.startswith('door:') else c.z - 1.3          # (her eye, 1.5 m up, below a sign 2.8 m up)
        to = c - origin
        hit, loc, nrm, idx, ob, mtx = bpy.context.scene.ray_cast(_dg, origin, to.normalized(), distance=to.length - 0.25)
        if hit and not ob.name.startswith(_FABRIC):
            bad.append('%s%s' % ('straight:' if ang == 0.0 else 'side:', ob.name))
    if any(b.startswith('straight') for b in bad) or len(bad) >= 2:
        print('SIGN_HIDDEN', what, 'at', bl_m(c), 'h', round(c.z, 2), 'n', (round(n.x, 3), round(-n.y, 3)), 'by', ' '.join(bad))
        _hidden += 1
print('SIGNS checked', len(_signs), 'hidden', _hidden)
# (round 40, the user, at the park's fingerposts: "The words on this sign are sticking out. They're weird. Please check
# all the signs") every sign's lettering must lie on its board: behind its left end, middle and right end, a hand's
# breadth back at most, there is the board it is painted on (not air, not the lettering itself)
_float = 0
for ob_ in TEXT_OBJS:
    try:
        rz_ = ob_.rotation_euler[2]
        n_ = Vector((math.sin(rz_), -math.cos(rz_), 0.0))          # (the way the lettering faces)
        u_ = Vector((math.cos(rz_), math.sin(rz_), 0.0))           # (the way it reads)
        hw_ = ob_.dimensions.x / 2.0
    except ReferenceError:
        continue
    miss_ = []
    for f_ in (-0.9, 0.0, 0.9):
        o_ = ob_.location + u_ * (hw_ * f_) + n_ * 0.04
        left_ = 0.16
        got_ = False
        while left_ > 0.0:
            hit, loc, nrm, idx, hob, mtx = bpy.context.scene.ray_cast(_dg, o_, -n_, distance=left_)
            if not hit:
                break
            if hob is ob_ or hob.name.startswith(('SignText', 'HangSignText')) or hob in TEXT_OBJS:
                left_ -= (loc - o_).length + 0.002
                o_ = loc - n_ * 0.002
                continue
            got_ = True
            break
        if not got_:
            miss_.append({-0.9: 'left', 0.0: 'middle', 0.9: 'right'}[f_])
    if miss_:
        print('SIGN_FLOAT', ob_.name, repr(ob_.data.name[:-2] if False else ''), 'at', bl_m(ob_.location), 'nothing behind its', '/'.join(miss_))
        _float += 1
print('SIGN_FLOAT checked', len(TEXT_OBJS), 'floating', _float)

export(city_objs, os.path.join(OUT, 'city.glb'))

# ------------------------------------------------------------------ the interiors (interiors.py)
exec(open(os.path.join(BUILD, 'interiors.py')).read())

with open(os.path.join(OUT, 'scene.json'), 'w') as f:
    json.dump(scene, f, indent=1, ensure_ascii=False)

# (round 21) every doorway: is anything standing in front of it? (trees, lamps, benches, bins, planters)
_things = [(t[0], t[1], 0.5) for t in scene['trees']] + [(l['pos'][0], l['pos'][1], 0.3) for l in scene['lamps']] + \
    [(o['pos'][0] + o['off'][0], o['pos'][1] + o['off'][1], o['r']) for o in scene['obstacles']]
_blocked = []
for _p, _u in DECO_DOORS:
    _q = bl_m(_p)
    _near = [t for t in _things if math.hypot(t[0] - _q[0], t[1] - _q[1]) < t[2] + 0.55]
    if _near:
        _blocked.append((_q, [(round(t[0], 1), round(t[1], 1)) for t in _near]))
print('DOORS', len(DECO_DOORS), 'doorways,', len(_blocked), 'with something in front:', _blocked[:12])
print('BUILD OK', {k: len(v) for k, v in scene.items() if isinstance(v, list)})
for fn in sorted(os.listdir(OUT)):
    print(fn, round(os.path.getsize(os.path.join(OUT, fn)) / 1e6, 2), 'MB')
