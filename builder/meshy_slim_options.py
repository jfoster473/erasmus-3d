# (round 25) A Meshy model at a few levels of detail, for the user to pick before it goes in: each version to its own glb
# (its size on disk is what it adds to the game's file), and all of them side by side on the beach in one glb for the
# game's pictures (tests.gd --addglb=<file>).
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P meshy_slim_options.py -- <out dir> <model.glb> <height m>
import bpy, sys, os, json
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index('--') + 1:]
OUT, SRC, HEIGHT = args[0], args[1], float(args[2])
LEVELS = [('full', 0), ('150k', 150000), ('50k', 50000), ('15k', 15000)]
os.makedirs(OUT, exist_ok=True)
name = os.path.splitext(os.path.basename(SRC))[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
src = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.data.objects):
    if o is not src:
        bpy.data.objects.remove(o)
vs = [v.co for v in src.data.vertices]
zmin, zmax = min(v.z for v in vs), max(v.z for v in vs)
cx, cy = (min(v.x for v in vs) + max(v.x for v in vs)) / 2, (min(v.y for v in vs) + max(v.y for v in vs)) / 2
k = HEIGHT / (zmax - zmin)
src.data.transform(Matrix.Translation((-cx, -cy, -zmin)))
src.data.transform(Matrix.Diagonal((k, k, k, 1)))
full_tris = sum(len(p.vertices) - 2 for p in src.data.polygons)
info = {}
objs = []
for i, (lvl, target) in enumerate(LEVELS):
    ob = src.copy()
    ob.data = src.data.copy()
    bpy.context.scene.collection.objects.link(ob)
    ob.name = '%s_%s' % (name, lvl)
    if target and target < full_tris:
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        dec = ob.modifiers.new('slim', 'DECIMATE')
        dec.ratio = target / full_tris
        bpy.ops.object.modifier_apply(modifier=dec.name)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    # its own file, alone at the origin, to weigh it
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    f = os.path.join(OUT, '%s_%s.glb' % (name, lvl))
    bpy.ops.export_scene.gltf(filepath=f, export_format='GLB', use_selection=True, export_yup=True)
    info[lvl] = {'tris': tris, 'mb': round(os.path.getsize(f) / 1e6, 1)}
    # then out on the beach in a row, 40 m apart, for the pictures (Blender x, -z: engine z 146)
    ob.location = (-150.0 + i * 40.0, -146.0, 0.05)
    objs.append(ob)
    print('SLIM', name, lvl, info[lvl])
bpy.data.objects.remove(src)
bpy.ops.object.select_all(action='DESELECT')
for o in objs:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, '%s_row.glb' % name), export_format='GLB', use_selection=True, export_yup=True)
json.dump(info, open(os.path.join(OUT, '%s.json' % name), 'w'), indent=1)
