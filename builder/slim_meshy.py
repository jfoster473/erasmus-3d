# Slims a Meshy character to about 30,000 triangles, like the others the game uses (Meshy's 7.1 models
# come out ten times heavier). The full one is kept as <name>_full.glb.
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P slim_meshy.py -- man oldman
import bpy, sys, os
import sys as _s
_s.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from paths import MESHY
D = MESHY + "/"
TARGET = 30000
for name in sys.argv[sys.argv.index('--') + 1:]:
    src, full = D + name + '.glb', D + name + '_full.glb'
    if not os.path.exists(full):
        os.rename(src, full)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    bpy.ops.import_scene.gltf(filepath=full)
    for o in list(bpy.data.objects):
        if o.name.startswith('Icosphere'):
            bpy.data.objects.remove(o)
    for ob in [o for o in bpy.data.objects if o.type == 'MESH']:
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        if tris <= TARGET * 1.2:
            continue
        bpy.context.view_layer.objects.active = ob
        m = ob.modifiers.new('slim', 'DECIMATE')
        m.ratio = TARGET / tris
        m.use_collapse_triangulate = True
        while ob.modifiers[0] != m:
            bpy.ops.object.modifier_move_up(modifier='slim')
        bpy.ops.object.modifier_apply(modifier='slim')
        print('SLIM', name, ob.name, tris, '->', sum(len(p.vertices) - 2 for p in ob.data.polygons))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=src, export_format='GLB', use_selection=True, export_animations=True,
                              export_skins=True, export_yup=True)
    print('SLIM OK', name)
