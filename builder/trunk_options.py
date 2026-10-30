# (round 25) The wood's trees with their trunks drawn more and more simply (forest.py TRUNK), five kinds side by side
# for each, to one glb, so the game can show them on the beach (tests.gd --addglb=<file>) without the whole build.
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P trunk_options.py -- <out.glb>
import bpy, sys, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:]
OUT = args[0]
src = open(os.path.join(HERE, 'build_assets.py')).read()
src = src[:src.index("SPECIALS = {}")]
g = {'__file__': os.path.join(HERE, 'build_assets.py'), '__name__': 'preview'}
exec(compile(src, 'build_assets.py', 'exec'), g)
w2 = open(os.path.join(g['BUILD'], 'world2d.py')).read()
exec(compile(w2[:w2.index("M_SAND = mat(")], 'world2d.py', 'exec'), g)
g['GROUND_MAT'] = {}
exec(compile(open(os.path.join(g['BUILD'], 'forest.py')).read(), 'forest.py', 'exec'), g)
exec(compile(w2[w2.index('M_FBARK = mat('):w2.index('def forest_tree(')], 'world2d.py', 'exec'), g)
V = g['Vector']
VARIANTS = [('A', {'sides': 10, 'branch_sides': None, 'caps': True, 'min_branch': 0.0}),
            ('B', {'sides': 6, 'branch_sides': 4, 'caps': False, 'min_branch': 0.0}),
            ('C', {'sides': 6, 'branch_sides': 4, 'caps': False, 'min_branch': 0.1}),
            ('D', {'sides': 5, 'branch_sides': 4, 'caps': False, 'min_branch': 0.16})]
KINDS = ['holm', 'cork', 'aleppo', 'stone_pine', 'holm']
objs = []
for vi, (name, t) in enumerate(VARIANTS):
    g['TRUNK'].update(t)
    tr, cr = g['MB'](uv=True), g['Cards']()
    for k, sp in enumerate(KINDS):
        x = -86.0 + vi * 19.0 + k * 3.6                 # (engine metres, on the beach east of where she wakes)
        z = 146.0 + (k % 2) * 2.5
        g['SPECIES'][sp](tr, cr, V((x, -z, 0.0)), random.Random(100 + k), 1.0)
    tris = sum(len(f.verts) - 2 for f in tr.bm.faces)
    objs.append(tr.finish('TrunkOpt_' + name))
    objs.append(cr.finish('Leaves_opt_' + name))
    print('TRUNKOPT', name, t, tris, 'trunk triangles for', len(KINDS), 'trees')
bpy.ops.object.select_all(action='DESELECT')
for o in objs:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True)
