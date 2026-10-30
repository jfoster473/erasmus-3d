# Builds one whole-block landmark on its own and renders it from a few sides, for checking it quickly
# without the whole city (about a minute instead of seventeen).
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P preview.py -- sagrada <out dir>
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:]
WHICH, OUTDIR = args[0], args[1]
src = open(os.path.join(HERE, 'build_assets.py')).read()
src = src[:src.index("SPECIALS = {}")]                 # helpers, materials, ground, kit and landmarks; no blocks yet
g = {'__file__': os.path.join(HERE, 'build_assets.py'), '__name__': 'preview'}
exec(compile(src, 'build_assets.py', 'exec'), g)
g.setdefault('RELIEF_BLOCKS', set())                 # (defined after the cut in build_assets.py)
ROOM = WHICH.startswith('int_')
if ROOM:
    # one room: (an interior's x, y are Blender x, -y; it is built at offset 0)
    isrc = open(os.path.join(g['BUILD'], 'interiors.py')).read()
    isrc = isrc[:isrc.index('INT_ROOTS = []')] + 'INT_ROOTS = []\n'
    exec(compile(isrc, 'interiors.py', 'exec'), g)
    rec = g['build_room'](WHICH, g['W2']['INTERIORS'][WHICH], 0)
    for ob in bpy.data.objects:
        if ob.name.startswith('Ceiling_') or not (ob.name.startswith(('Room_', 'Floor_', 'Furn_', 'Glass_', 'Deco_', 'BannerText', 'Interior_'))
                                                    or ob.parent is not None):
            ob.hide_render = True                    # (the game shows ceilings only as shadows; the city isn't there)
    print('ROOMREC', rec['w'], rec['h'], len(rec['solids']), 'solids', len(rec['things']), 'things')
    c = Vector((0, 0, 0))
elif WHICH.startswith('block'):
    # an ordinary block, as the city builds it: block_-13_0
    ox, oy = [int(v) for v in WHICH.split('_')[1:3]]
    houses = g['override_houses'](ox, oy, g['gen_houses'](ox, oy, skip=()))
    for b2 in g['W2']['BUILDINGS']:
        if (g['COLS'][b2['block'][0]], g['ROWS'][b2['block'][1]]) == (ox, oy) and b2['type'] == 'shop':
            houses[{'N': 0, 'E': 2, 'S': 4, 'W': 6}[b2['face']]] = [g['shop_house'](b2)]
    g['build_kit_block'](ox, oy, houses)
    c = g['B'](ox + g['BS'] / 2, oy + g['BS'] / 2, 0)
else:
    spec = next(b for b in g['W2']['BUILDINGS'] if b['id'] == WHICH)
    ox, oy = g['COLS'][spec['block'][0]], g['ROWS'][spec['block'][1]]
    g['OPEN_BLOCKS'] = set()
    g['build_special_block'](ox, oy, [spec])
    c = g['B'](ox + g['BS'] / 2, oy + g['BS'] / 2, 0)

scn = bpy.context.scene
scn.render.engine = 'BLENDER_EEVEE'
scn.render.resolution_x, scn.render.resolution_y = 1280, 800
world = bpy.data.worlds.new('w')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.62, 0.74, 0.9, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.9
scn.world = world
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0, math.radians(-130))
scn.collection.objects.link(sun)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.lens = 24
scn.collection.objects.link(cam)
scn.camera = cam
views = {'se': (40, -55, 22, 0, 0, 22), 'upf_front': (34, 6, 3.0, 10, 0, 8), 'close_e': (19, -3, 4.5, 14, -1, 6.5), 'close_s': (2, -19, 5.5, 0, -14.5, 7), 'east': (52, 3, 6, 0, 3, 20), 'west': (-52, 3, 6, 0, 3, 20), 'nw': (-45, 50, 30, 0, 0, 20),
         'east_door': (24, 3, 2.2, 12, 3, 5), 'west_door': (-24, 3, 2.2, -12, 3, 5), 'air': (60, -70, 90, 0, 0, 10)}
if ROOM:
    # from Sandra's height and a little above, inside, looking along the nave and up into the vault
    w_, h_ = rec['w'], rec['h']
    views = {'door': (22, -(h_ - 2.0), 2.0, 22, -12, 9), 'nave': (27, -12, 3.0, 2, -12, 9), 'up': (10, -12, 1.6, 12, -11, 21),
             'apse': (12, -12, 3.0, 33, -12, 8), 'cross': (22, -20, 2.0, 22, -12, 26)}
    if not rec.get('free_cam'):
        # as the game's room camera sees it: from above the cut-away front wall
        sc_ = max(1.0, w_ / 14.0, h_ / 10.0)
        views = {'game': (w_ / 2, -(h_ / 2 + 0.5 + 9.7 * sc_), 9.2 * sc_, w_ / 2, -(h_ / 2 + 0.6), 0.4),
                 'low': (w_ / 2 + 3, -(h_ - 1.5), 1.7, w_ / 2, -3, 1.8)}
    sun.data.energy = 0.0
    for (x, y, z, e) in ((w_ / 2, -h_ / 2, 16, 40000), (8, -12, 8, 15000), (28, -12, 8, 15000)):
        pl = bpy.data.objects.new('pl', bpy.data.lights.new('pl', 'POINT'))
        pl.data.energy = e
        pl.location = (x, y, z)
        scn.collection.objects.link(pl)
if os.environ.get('PREVIEW_VIEW'):                    # (one view of your own: name:x,y,z,tx,ty,tz from the block's centre)
    nm_, vals_ = os.environ['PREVIEW_VIEW'].split(':')
    views = {nm_: tuple(float(v) for v in vals_.split(','))}
os.makedirs(OUTDIR, exist_ok=True)
for name, (x, y, z, tx, ty, tz) in views.items():
    cam.location = c + Vector((x, y, z))
    d = (c + Vector((tx, ty, tz))) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scn.render.filepath = os.path.join(OUTDIR, '%s_%s.png' % (WHICH, name))
    bpy.ops.render.render(write_still=True)
    print('PREVIEW', scn.render.filepath)
