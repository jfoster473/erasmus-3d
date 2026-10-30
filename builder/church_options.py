# (round 26) The Sagrat Cor with textured stone, for the user to compare in the game before anything is built: "Put some
# textures on the church and base; it looks very plain." Builds the church alone (north_build.py's church section),
# gives it a texture style, and writes one .glb per style; the game shows each in place of the built church:
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P builder/church_options.py -- <out dir> [A B C]
#   Godot ... -- --hide=SagratCor --addglb=<out dir>/church_A.glb --views=<dir> --viewfile=<json>
import bpy, sys, os, math, random
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:]
OUTDIR = args[0]
STYLES = args[1:] or ['A', 'B', 'C']
src = open(os.path.join(HERE, 'build_assets.py')).read()
src = src[:src.index("SPECIALS = {}")]
g = {'__file__': os.path.join(HERE, 'build_assets.py'), '__name__': 'preview'}
exec(compile(src, 'build_assets.py', 'exec'), g)
sys.path.insert(0, g['BUILD'])
mat = g['mat']
for k, v in (('M_FBARK', ('ForestBark', '#4f3d2e')), ('M_WOODEN', ('BeachWood', '#a67c52')), ('M_SAND', ('Sand', '#e8d4a0')),
             ('M_PATH', ('DirtPath', '#a88c66')), ('M_GREYSTONE', ('GreyStone', '#b7b1a6')), ('M_RED', ('PaintRed', '#c8322e')),
             ('M_WHITE', ('PaintWhite', '#f2efe8')), ('M_GOLD', ('Gilt', '#d4a640'))):
    g.setdefault(k, mat(*v))
g['scene'] = {'blocked': [], 'entrances': []}
g['city_objs'] = []
nb = open(os.path.join(g['BUILD'], 'north_build.py')).read()
nb = nb[:nb.index('# --- the Giradabo')]          # everything up to and including the church
exec(compile(nb, 'north_build.py', 'exec'), g)
FH, UB = g['FH'], g['UB']
church = bpy.data.objects['SagratCor']
os.makedirs(OUTDIR, exist_ok=True)


# ---------------------------------------------------------------- textures (numpy; rows from the bottom, as Blender's)

def vnoise(h, w, cells, seed):
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


def stones(W, H, ppm, course, length, mortar, base, mortar_col, var, edge, rough, weather, seed, stagger=0.5):
    """Coursed stone blocks, tiling, W x H metres at ppm pixels a metre. course/length: (min, max) metres;
    mortar: joint width (m); var: how much one block differs from the next; edge: darker rounded block edges (0..1);
    rough: grain; weather: the foot darker (0..1, over its first metre or so)."""
    rnd = random.Random(seed)
    w, h = int(W * ppm), int(H * ppm)
    hs = []
    while sum(hs) < H - course[0]:
        hs.append(rnd.uniform(*course))
    hs = [x * H / sum(hs) for x in hs]
    img = np.zeros((h, w, 3))
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
        edges = np.cumsum([0.0] + ls) + off
        xs = (x_m - off) % W
        k = np.searchsorted(np.cumsum(ls), xs, side='right')
        starts = np.concatenate([[0.0], np.cumsum(ls)])
        dx = np.minimum(xs - starts[k], starts[k + 1] - xs)
        dy = np.minimum(y_m[rows] - y0, y0 + ch - y_m[rows])
        tones = np.array([rnd.uniform(-1, 1) for _ in ls])
        tone[rows] = tones[k][None, :]
        dist[rows] = np.minimum(dx[None, :], dy[:, None])
        y0 += ch
    n1 = vnoise(h, w, (int(H * 3), int(W * 3)), seed + 1)
    n2 = vnoise(h, w, (int(H * 14), int(W * 14)), seed + 2)
    n3 = np.random.RandomState(seed + 3).rand(h, w)
    k = 1 + var * tone + rough * ((n1 - 0.5) * 0.6 + (n2 - 0.5) * 0.5 + (n3 - 0.5) * 0.25)
    if edge:
        e = np.clip(dist / 0.07, 0, 1)
        k *= 1 - edge * (1 - e) ** 2
    img = np.array(base)[None, None, :] * k[:, :, None]
    joint = dist < mortar / 2
    jn = 1 + 0.08 * (n2 - 0.5)
    img[joint] = (np.array(mortar_col)[None, :] * jn[joint][:, None])
    if weather:
        f = 1 - weather * np.exp(-y_m / 0.7)[:, None] * (0.75 + 0.5 * n1)
        img *= f[:, :, None]
    return np.clip(img, 0, 1)


def tesserae(S, ppm, palette, grout, seed):
    """A flat mosaic of little square tiles, S metres a side, tiling."""
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
    fx = ((xx + (iy % 2) * cell * 0.3) / cell) % 1
    gap = (fy < 0.1) | (fx < 0.1)
    col[gap] = grout
    return col


def to_image(name, arr):
    h, w, _ = arr.shape
    img = bpy.data.images.new(name, w, h, alpha=False)
    rgba = np.concatenate([arr, np.ones((h, w, 1))], axis=2).astype(np.float32)
    img.pixels.foreach_set(rgba.ravel())
    img.file_format = 'PNG'
    img.pack()
    return img


def hexc(hx):
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))


# the styles: A subtle, B stone blocks, C rough and weathered
STYLE = {
    'A': dict(crypt=dict(course=(0.42, 0.55), length=(0.8, 1.3), mortar=0.012, var=0.05, edge=0.0, rough=0.12, weather=0.0),
              upper=dict(course=(0.45, 0.45), length=(1.0, 1.4), mortar=0.008, var=0.025, edge=0.0, rough=0.06, weather=0.0),
              mortar_k=0.92, flag=0.04),
    'B': dict(crypt=dict(course=(0.32, 0.55), length=(0.55, 1.2), mortar=0.025, var=0.1, edge=0.25, rough=0.22, weather=0.2),
              upper=dict(course=(0.42, 0.48), length=(0.9, 1.4), mortar=0.012, var=0.05, edge=0.08, rough=0.1, weather=0.08),
              mortar_k=0.8, flag=0.08),
    'C': dict(crypt=dict(course=(0.28, 0.6), length=(0.45, 1.1), mortar=0.035, var=0.16, edge=0.5, rough=0.35, weather=0.35,
                         stagger=None),
              upper=dict(course=(0.4, 0.5), length=(0.8, 1.3), mortar=0.016, var=0.07, edge=0.15, rough=0.14, weather=0.15),
              mortar_k=0.7, flag=0.12),
}
SAND = hexc('#c6a073')
PALE = hexc('#ece4d2')
TILE = {'crypt': (4.0, 12.0), 'upper': (4.0, 4.0), 'flag': (4.0, 4.0), 'mosaic': (0.5, 0.5)}


def box_uvs(ob, rules):
    """UVs in metres by each face's facing, per material: rules[name] = (size x, size y, height the texture's foot is at)."""
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


def textured(name, arr, rough=0.9, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = to_image(name, arr)
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    return m


slots0 = [m for m in church.data.materials]
for st in STYLES:
    P = STYLE[st]
    c = P['crypt']
    crypt = stones(*TILE['crypt'], 96, c['course'], c['length'], c['mortar'], SAND,
                   tuple(v * P['mortar_k'] for v in hexc('#cdbfa6')), c['var'], c['edge'], c['rough'], c['weather'], 11,
                   **({'stagger': c['stagger']} if 'stagger' in c else {}))
    u = P['upper']
    upper = stones(*TILE['upper'], 96, u['course'], u['length'], u['mortar'], PALE,
                   tuple(v * P['mortar_k'] for v in hexc('#ddd5c4')), u['var'], u['edge'], u['rough'], 0.0, 21)
    flag = stones(*TILE['flag'], 64, (0.8, 0.8), (0.8, 1.2), 0.02, hexc('#e6dac2'), hexc('#bdb19a'), P['flag'], 0.05, 0.12, 0, 31,
                  stagger=0.5)
    gold = tesserae(0.5, 512, [hexc('#d7a640'), hexc('#c99a3a'), hexc('#e2b955'), hexc('#b8862e')], hexc('#9c8a6a'), 41)
    blue = tesserae(0.5, 512, [hexc('#3f63a8'), hexc('#35579a'), hexc('#4d72b6'), hexc('#2e4c8c')], hexc('#8a8f9a'), 42)
    new = {
        'MontjuicStone': (textured('MontjuicStone_' + st, crypt), TILE['crypt'] + (FH,)),
        'MontjuicStoneShade': (textured('MontjuicStoneShade_' + st, crypt * 0.86), TILE['crypt'] + (FH,)),
        'ChurchStone': (textured('ChurchStone_' + st, upper), TILE['upper'] + (UB,)),
        'ChurchStoneShade': (textured('ChurchStoneShade_' + st, upper * 0.9), TILE['upper'] + (UB,)),
        'Stone': (textured('TerraceFlags_' + st, flag), TILE['flag'] + (0.0,)),
        'CryptMosaic': (textured('CryptMosaic_' + st, gold, 0.45), TILE['mosaic'] + (0.0,)),
        'CryptMosaicBlue': (textured('CryptMosaicBlue_' + st, blue, 0.5), TILE['mosaic'] + (0.0,)),
    }
    for i, m in enumerate(slots0):
        church.data.materials[i] = m
    box_uvs(church, {k: v[1] for k, v in new.items()})
    for i, m in enumerate(slots0):
        if m.name in new:
            church.data.materials[i] = new[m.name][0]
    church.name = 'ChurchOption_' + st
    bpy.ops.object.select_all(action='DESELECT')
    church.select_set(True)
    out = os.path.join(OUTDIR, 'church_%s.glb' % st)
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_yup=True)
    for nm, arr in (('crypt', crypt), ('upper', upper)):
        to_image('swatch_%s_%s' % (st, nm), arr).save_render(os.path.join(OUTDIR, 'swatch_%s_%s.png' % (st, nm)))
    print('CHURCH OPTION', st, out)
