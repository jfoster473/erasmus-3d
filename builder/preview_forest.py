# The eastern wood on its own (forest.py), with its ground, rendered from a few spots: a minute or two
# instead of the whole build.
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P preview_forest.py -- <out dir>
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = sys.argv[sys.argv.index('--') + 1]
src = open(os.path.join(HERE, 'build_assets.py')).read()
src = src[:src.index("SPECIALS = {}")]
g = {'__file__': os.path.join(HERE, 'build_assets.py'), '__name__': 'preview'}
exec(compile(src, 'build_assets.py', 'exec'), g)
# world2d's own pieces the wood needs, then the wood
w2 = open(os.path.join(g['BUILD'], 'world2d.py')).read()
head = w2[:w2.index("M_SAND = mat(")]                      # its textures' functions
exec(compile(head, 'world2d.py', 'exec'), g)
exec(compile("M_FBARK = mat('ForestBark', '#4f3d2e', 0.95)\nM_PINEBARK = mat('PineBark', '#6e4630', 0.95)\n"
             "M_FLOOR = mat('ForestFloor', '#ffffff', 0.97, image=make_image('forestfloor', 128, 128, forest_floor))\n", 'x', 'exec'), g)
g['GROUND_MAT'] = {}
exec(compile("M_SANDP = mat('SandPreview', '#e8d4a6', 0.95)\n", 'x', 'exec'), g)
exec(compile(open(os.path.join(g['BUILD'], 'forest.py')).read(), 'forest.py', 'exec'), g)
g['forest_layout']()
# the ground: grass, or forest floor, as the build lays it
mb = g['MB'](uv=True)
for j in range(2 * 8, 2 * 90):
    for i in range(2 * 80, 2 * 106):
        X, Y = i / 2, j / 2
        k = g['tile'](int(X), int(Y)) or ('FFLOOR' if X >= g['MW2'] else 'GRASS')
        if k in ('PAVE', 'WALK', 'ROAD', 'PROM'):
            continue
        k = g['forest_ground'](X, Y, k) if X >= g['FOREST_X0'] else k
        m = {'GRASS': g['M_GRASS'], 'FFLOOR': g['M_FLOOR'], 'FOREST': g['M_LITTER_DRY'], 'FORESTMID': g['M_MID'],
             'SAND': g['M_SANDP']}.get(k, g['M_FLOOR'])
        q = [g['BT'](X, Y, 0.05), g['BT'](X + 0.5, Y, 0.05), g['BT'](X + 0.5, Y + 0.5, 0.05), g['BT'](X, Y + 0.5, 0.05)]
        mb.face(q, m, normal=(0, 0, 1), uvs=[(p.x / 3, p.y / 3) for p in q])
mb.finish('Ground')
g['plant_forest']()
g['lamps'].finish('Lamps')
print('SCENE', len(g['scene']['forest_blocked']), 'walls,', len(g['scene']['trees']), 'solid trees')

scn = bpy.context.scene
scn.render.engine = 'BLENDER_EEVEE'
scn.render.resolution_x, scn.render.resolution_y = 1280, 800
world = bpy.data.worlds.new('w')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.62, 0.74, 0.9, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.0
scn.world = world
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(45), 0, math.radians(-140))
scn.collection.objects.link(sun)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.lens = 22
scn.collection.objects.link(cam)
scn.camera = cam
BT = g['BT']
views = {
    'meadow_entrance': ((83.0, 42.5, 1.7), (88.0, 42.5, 1.4)),        # from the city's footpath across the meadow, into the wood
    'trunk_path': ((95.6, 46.0, 1.7), (95.4, 52.0, 1.3)),             # walking the long path south
    'branch_in': ((88.5, 55.3, 1.7), (93.0, 55.5, 1.3)),
    'trufa_trail': ((95.5, 50.3, 1.7), (98.5, 50.5, 1.0)),
    'meadow_wide': ((82.5, 60.0, 3.5), (90.0, 52.0, 0.5)),
    'air': ((84.0, 64.0, 40.0), (95.0, 50.0, 0.0)),
    'footpath': ((81.6, 41.0, 1.7), (88.0, 42.6, 0.6)),
    'beach_end': ((95.0, 89.0, 2.2), (95.0, 80.0, 1.0)),
    'south_air': ((86.0, 92.0, 25.0), (94.0, 80.0, 0.0)),
    'junction': ((93.0, 45.0, 5.0), (95.5, 42.5, 0.0)),
    'trail_join': ((95.5, 47.5, 5.0), (97.5, 50.5, 0.0)),
    'junction_air': ((95.0, 46.5, 14.0), (95.2, 42.5, 0.0)),
}
os.makedirs(OUTDIR, exist_ok=True)
for name, (a, b) in [(k, v) for k, v in views.items() if len(sys.argv) <= sys.argv.index('--') + 2 or k in sys.argv[sys.argv.index('--') + 2].split(',')]:
    cam.location = BT(*a)
    d = BT(*b) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scn.render.filepath = os.path.join(OUTDIR, 'forest_%s.png' % name)
    bpy.ops.render.render(write_still=True)
    print('PREVIEW', scn.render.filepath)
