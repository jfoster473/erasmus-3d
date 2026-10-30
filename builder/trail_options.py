# The wood's path ribbons alone, in each TRAIL_STYLE (forest.py build_trails), each to its own glb, so the game can
# show them in place (tests.gd --trailglb=<file>) without the whole build.
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P trail_options.py -- <out dir> [styles]
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:]
OUTDIR, STYLES = args[0], (args[1].split(',') if len(args) > 1 else ['current', 'A', 'B', 'C'])
src = open(os.path.join(HERE, 'build_assets.py')).read()
src = src[:src.index("SPECIALS = {}")]
g = {'__file__': os.path.join(HERE, 'build_assets.py'), '__name__': 'preview'}
exec(compile(src, 'build_assets.py', 'exec'), g)
w2 = open(os.path.join(g['BUILD'], 'world2d.py')).read()
exec(compile(w2[:w2.index("M_SAND = mat(")], 'world2d.py', 'exec'), g)
g['GROUND_MAT'] = {}
exec(compile(open(os.path.join(g['BUILD'], 'forest.py')).read(), 'forest.py', 'exec'), g)
g['forest_layout']()
os.makedirs(OUTDIR, exist_ok=True)
for st in STYLES:
    ob = g['build_trails'](st, 'Trails')
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUTDIR, 'trails_%s.glb' % st), export_format='GLB', use_selection=True, export_yup=True)
    bpy.data.objects.remove(ob)
    print('TRAILS', st)
