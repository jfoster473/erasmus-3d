# The north (north_build.py) on its own, on a ground made from north.py, rendered from a few spots: for checking it
# without the 17-minute build.
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P preview_north.py -- <out dir> [view ...]
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:]
OUTDIR = args[0]
ONLY = args[1:]
src = open(os.path.join(HERE, 'build_assets.py')).read()
src = src[:src.index("SPECIALS = {}")]
g = {'__file__': os.path.join(HERE, 'build_assets.py'), '__name__': 'preview'}
exec(compile(src, 'build_assets.py', 'exec'), g)
sys.path.insert(0, g['BUILD'])
import north as N
mat = g['mat']
g['M_FBARK'] = mat('ForestBark', '#4f3d2e', 0.95)
g['M_WOODEN'] = mat('BeachWood', '#a67c52', 0.85)
g['M_SAND'] = mat('Sand', '#e8d4a0', 0.95)
g['M_PATH'] = mat('DirtPath', '#a88c66', 0.97)
g['M_GREYSTONE'] = mat('GreyStone', '#b7b1a6', 0.9)
g['M_RED'] = mat('PaintRed', '#c8322e', 0.6)
g['M_WHITE'] = mat('PaintWhite', '#f2efe8', 0.6)
g['M_GOLD'] = mat('Gilt', '#d4a640', 0.35, 0.8)
g['scene'] = {'blocked': [], 'entrances': []}
g['city_objs'] = []
MB = g['MB']
# the ground
grass = mat('HillGround', '#6f9150', 0.95)
terr = mat('Terrace', '#d9cfbc', 0.9)
X0, X1, Z0, Z1, ST = -240.0, 200.0, -330.0, -90.0, 1.5
mb = MB(uv=True)
nx, nz = int((X1 - X0) / ST), int((Z1 - Z0) / ST)
H = [[N.ground(X0 + i * ST, Z0 + j * ST) for i in range(nx + 1)] for j in range(nz + 1)]
for j in range(nz):
    for i in range(nx):
        x, z = X0 + (i + 0.5) * ST, Z0 + (j + 0.5) * ST
        f = N.FAIR
        m = terr if (f[0] <= x <= f[2] and f[1] <= z <= f[3]) else grass
        mb.face([Vector((X0 + i * ST, -(Z0 + j * ST), H[j][i])), Vector((X0 + (i + 1) * ST, -(Z0 + j * ST), H[j][i + 1])),
                 Vector((X0 + (i + 1) * ST, -(Z0 + (j + 1) * ST), H[j + 1][i + 1])), Vector((X0 + i * ST, -(Z0 + (j + 1) * ST), H[j + 1][i]))],
                m, normal=(0, 0, 1))
mb.finish('PreviewGround')
mb2 = MB(uv=True)
mb2.face([Vector((-260, 95, -0.05)), Vector((220, 95, -0.05)), Vector((220, -400, -0.05)), Vector((-260, -400, -0.05))], mat('City', '#b8b0a4', 0.9),
         normal=(0, 0, 1))
mb2.finish('PreviewCity')
exec(compile(open(os.path.join(HERE, 'trails.py')).read(), 'trails.py', 'exec'), g)     # (round 26: north_build lays its paths with it)
exec(compile(open(os.path.join(g['BUILD'], 'north_build.py')).read(), 'north_build.py', 'exec'), g)

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
sun.rotation_euler = (math.radians(50), 0, math.radians(-150))
scn.collection.objects.link(sun)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.lens = 26
cam.data.clip_end = 2000
scn.collection.objects.link(cam)
scn.camera = cam


def E(x, z, h):
    return Vector((x, -z, h))


views = {
    'fair': (E(-40, -235, 100), E(-65, -285, 82)),
    'church': (E(-63, -255, 84), E(-63, -293, 100)),
    'wheel': (E(-80, -262, 80), E(-94, -281, 88)),
    'rambla': (E(-49.5, 82.5, 1.7), E(-62.7, -135.3, 14)),
    'cable': (E(-40, -120, 20), E(-66, -200, 45)),
    'gate': (E(106, -118, 9), E(106, -150, 9)),
    'stairs': (E(106, -146, 9.5), E(106, -175, 13)),
    'square': (E(70, -205, 22), E(106, -175, 15)),
    'park_air': (E(110, -100, 70), E(110, -190, 10)),
    'gracia': (E(60, -96, 2.5), E(62, -140, 6)),
    'path_air': (E(-120, -150, 130), E(-140, -215, 40)),
    'path_low': (E(-150, -150, 32), E(-185, -175, 22)),
    'path_top': (E(-70, -236, 75), E(-160, -250, 58)),
    'plan': (E(-130, -200, 300), E(-130, -199.99, 0)),
    'ledge': (E(-160, -248, 66), E(-172, -261, 62)),
    'bugadera': (E(85, -165, 12), E(73, -184, 12)),
    'museu': (E(141, -160, 17), E(141, -181, 17)),
}
os.makedirs(OUTDIR, exist_ok=True)
for name, (frm, to) in views.items():
    if ONLY and name not in ONLY:
        continue
    cam.location = frm
    cam.rotation_euler = (to - frm).to_track_quat('-Z', 'Y').to_euler()
    scn.render.filepath = os.path.join(OUTDIR, name + '.png')
    bpy.ops.render.render(write_still=True)
print('PREVIEW NORTH OK', len(g['scene']['blocked']), 'blocked', len(g['scene']['entrances']), 'doors')
