# Writes bigfiles/originals/meshy/passerby.glb: Rosa's old Meshy model without the watering can it was made
# with (weighted to her right toe, standing beside her foot, brass-coloured), for the passers-by (godot/people.gd).
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P make_passerby.py
import bpy, bmesh, colorsys
from mathutils import Vector
import sys as _s
_s.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from paths import MESHY
D = MESHY + "/"
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=D + 'rosa.glb')
ob = bpy.data.objects['output_unwrapped']
arm = bpy.data.objects['target_character']
me = ob.data
img = next(n.image for n in me.materials[0].node_tree.nodes if n.type == 'TEX_IMAGE')
W, H = img.size
px = list(img.pixels)
uvl = me.uv_layers.active.data
vuv = {}
for poly in me.polygons:
    for li in poly.loop_indices:
        vuv[me.loops[li].vertex_index] = uvl[li].uv
gi = {ob.vertex_groups[n].index for n in ('mixamorig:RightToeBase', 'mixamorig:RightToe_End')}
doomed = set()
for v in me.vertices:
    if not v.groups:
        continue
    g = max(v.groups, key=lambda g: g.weight)
    if g.group not in gi:
        continue
    uv = vuv.get(v.index, (0, 0))
    x, y = int((uv[0] % 1) * (W - 1)), int((uv[1] % 1) * (H - 1))
    i = (y * W + x) * 4
    h, s, val = colorsys.rgb_to_hsv(px[i], px[i + 1], px[i + 2])
    beside = (ob.matrix_world @ v.co).x < -0.26          # out beside her right foot, not the sandal itself
    if beside or (22 <= h * 360 <= 60 and s >= 0.28):
        doomed.add(v.index)
ps = [ob.matrix_world @ me.vertices[i].co for i in doomed]
print('CAN verts', len(doomed), 'bbox', tuple(round(min(p[k] for p in ps), 2) for k in range(3)), tuple(round(max(p[k] for p in ps), 2) for k in range(3)))
# grow the selection to whole faces: a face goes if most of its corners are doomed
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
faces = [f for f in bm.faces if sum(1 for v in f.verts if v.index in doomed) >= 2]
print('CAN faces', len(faces))
bmesh.ops.delete(bm, geom=faces, context='FACES')
bm.to_mesh(me)
bm.free()
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.name == 'Icosphere':
        bpy.data.objects.remove(o)
for o in bpy.data.objects:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=D + 'passerby.glb', export_format='GLB', use_selection=True, export_animations=True,
                          export_skins=True, export_yup=True)
print('PASSERBY OK')
