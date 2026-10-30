# One-off (round 41): Meshy's Casa Batlló (image-to-3D from a Commons photo, bigfiles/originals/meshy/casa_batllo_dl/)
# came with everything in the photo: Casa Amatller to its left, the tall house to its right, the pavement, trees and
# people. This keeps only Casa Batlló — its front, its roof and a few metres of its body behind — lightens it to about
# 400,000 triangles (the build lightens it further) and writes bigfiles/originals/meshy/casa_batllo.glb, its front
# facing -Y as Meshy's do. The cut, in the raw model's units (front view: x across, z up; y back from the street),
# was read off its front and top views. (Round 41, the user: "It looks like it's sunken into the block… the walls are
# flush. And then the balconies need to be brought in a little bit more. They're a bit too large… higher res") its
# wall's own plane is found (the deeper side of the front's surface, the balconies and bones being the shallower), all
# that stands out in front of it is drawn in to 60% of its depth, and the model is kept at 600,000 triangles; it
# prints the wall's place for builder/build_assets.py MESHY_GAUDI_GROUND.
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/trim_meshy_batllo.py
import bpy, bmesh, os
from mathutils import Vector
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (round 41: the 4K repaint, Meshy's "Texture" on the same model with the same photo — the same shape, so the same cut;
#  of the three repaints the user chose the second, _b: green balcony eyes, warm shopfronts)
SRC = os.path.join(ROOT, os.environ.get('BATLLO_SRC', 'bigfiles/originals/meshy/casa_batllo_4k_b_dl/casa_batllo_meshy_4k_b.glb'))
OUT = os.path.join(ROOT, os.environ.get('BATLLO_OUT', 'bigfiles/originals/meshy/casa_batllo.glb'))   # (the other repaints
#   compared beside it: BATLLO_SRC=… BATLLO_OUT=… — only casa_batllo.glb goes into the game)
X0, X1 = -0.175, 0.515          # between Casa Amatller and the tall house on its right
Y0, Y1 = -0.185, 0.40           # from its balconies' fronts back into its body (the street and trees are in front)
Z0 = -0.735                     # just over the pavement
TARGET = 600000
PROUD = 0.6                     # (the balconies' and bones' depth in front of the wall, kept)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
ob = next(o for o in bpy.data.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = ob
bm = bmesh.new()
bm.from_mesh(ob.data)
M = ob.matrix_world
cut = []
for f in bm.faces:
    c = M @ f.calc_center_median()
    if not (X0 <= c.x <= X1 and Y0 <= c.y <= Y1 and c.z >= Z0):
        cut.append(f)
    elif c.x > 0.40 and c.z > 0.25 and (c.y > 0.12 or c.z > 0.45):     # (scraps of the right-hand house's roof)
        cut.append(f)
bmesh.ops.delete(bm, geom=cut, context='FACES')
loose = [v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context='VERTS')
bm.to_mesh(ob.data)
bm.free()
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
print('TRIM kept', tris, 'triangles')
if tris > TARGET:
    d = ob.modifiers.new('lighten', 'DECIMATE')
    d.ratio = TARGET / tris
    bpy.ops.object.modifier_apply(modifier=d.name)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
vs = ob.data.vertices
# the wall's plane: over the front, cell by cell, the front-most surface; the wall is the deeper three quarters' edge
cells = {}
for v in vs:
    c = v.co
    if X0 + 0.03 < c.x < X1 - 0.03 and -0.5 < c.z < 0.2 and c.y < 0.1:
        k = (int(c.x / 0.01), int(c.z / 0.01))
        cells[k] = min(cells.get(k, 9.0), c.y)
fronts = sorted(cells.values())
wall = fronts[int(len(fronts) * 0.75)]
for v in vs:                                            # (what stands proud of the wall, drawn in)
    if v.co.y < wall:
        v.co.y = wall + (v.co.y - wall) * PROUD
ob.data.update()
ws = [v.co for v in vs]
lo = [min(p[i] for p in ws) for i in range(3)]
hi = [max(p[i] for p in ws) for i in range(3)]
print('TRIM box', [round(v, 3) for v in lo], [round(v, 3) for v in hi])
print('TRIM wall y %.3f (front-most now %.3f): %.4f of the width behind the front' % (wall, lo[1], (wall - lo[1]) / (hi[0] - lo[0])))
# the painting kept at 4K; the shading maps beside it (metal, roughness, bumps) shrunk to 1K — they matter far less,
# and each 4K one would add as much to the city's file as the painting itself
base_imgs = set()
for m in ob.data.materials:
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m and m.node_tree else None
    for l in (bsdf.inputs['Base Color'].links if bsdf else []):
        if l.from_node.type == 'TEX_IMAGE':
            base_imgs.add(l.from_node.image.name)
for im in bpy.data.images:
    if im.size[0] > 1024 and im.name not in base_imgs:
        im.scale(1024, 1024)
        im.pack()
    print('TRIM image', im.name, im.size[:], 'painting' if im.name in base_imgs else 'shading')
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, use_selection=True, export_format='GLB')
print('TRIM wrote', OUT, os.path.getsize(OUT) // 1000000, 'MB')
