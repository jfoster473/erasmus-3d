# (round 25) One ordinary block built in each window style (kit.py WIN_STYLE), each to its own glb, so the game can
# show them in place (tests.gd --blockglb=<file>) without the whole build.
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P window_options.py -- <out dir> [block] [styles]
# styles: comma-separated name=style[:tris[:texture]], e.g. crisp=crisp,old=meshy:1600:1024,sharp=meshy:6000:2048,pic=picture
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:]
OUTDIR = args[0]
BLOCK = args[1] if len(args) > 1 else '-13_0'
STYLES = (args[2] if len(args) > 2 else 'crisp=crisp,old=meshy:1600:1024,sharp=meshy:6000:2048,pic=picture').split(',')
src = open(os.path.join(HERE, 'build_assets.py')).read()
src = src[:src.index("SPECIALS = {}")]
g = {'__file__': os.path.join(HERE, 'build_assets.py'), '__name__': 'preview'}
exec(compile(src, 'build_assets.py', 'exec'), g)
ox, oy = [int(v) for v in BLOCK.split('_')]
os.makedirs(OUTDIR, exist_ok=True)
for spec in STYLES:
    name, st = spec.split('=')
    parts = st.split(':')
    g['WIN_STYLE'] = parts[0]
    g['CRISP_ALL'] = parts[0] == 'crisp'
    if len(parts) > 1:
        g['WIN_TRIS'] = int(parts[1])
    if len(parts) > 2:
        g['WIN_TEX'] = int(parts[2])
    for k in [k for k in g['KIT_WIN'] if k != 'pic']:
        del g['KIT_WIN'][k]
    n0 = len(g['city_objs'])
    houses = g['override_houses'](ox, oy, g['gen_houses'](ox, oy, skip=()))
    for b2 in g['W2']['BUILDINGS']:
        if (g['COLS'][b2['block'][0]], g['ROWS'][b2['block'][1]]) == (ox, oy) and b2['type'] == 'shop':
            houses[{'N': 0, 'E': 2, 'S': 4, 'W': 6}[b2['face']]] = [g['shop_house'](b2)]
    g['build_kit_block'](ox, oy, houses)
    new = [o for o in g['city_objs'][n0:] if o.name.startswith(('Block_', 'Detail_', 'WinHi', 'WinLo', 'WinPic_'))]
    bpy.ops.object.select_all(action='DESELECT')
    for o in new:
        o.select_set(True)
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in new)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUTDIR, 'block_%s.glb' % name), export_format='GLB',
                              use_selection=True, export_yup=True)
    print('WINOPT', name, st, len(new), 'objects', tris, 'triangles')
    for o in g['city_objs'][n0:]:
        bpy.data.objects.remove(o)
    del g['city_objs'][n0:]
