# Reusable props, each exported to its own file in bigfiles/built/props/ so the game can place
# copies anywhere and vary them (colours, extras) without rebuilding the city.
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P build_props.py
#
# bicycle.glb  An old ladies' roadster sized for Sandra's chunky proportions. Its moving
#              parts are separate, named nodes (FrontWheel, RearWheel, Cranks, PedalL/R,
#              Steering) so the game can spin the wheels, turn the pedals and steer.
#              Recolourable materials: BikeFrame, BikeGuard, BikeSaddle, BikeBasket.
#              Optional parts the game can hide: Basket, BasketFlowers, Rack.
#
# Blender is Z-up; the bike points along +Y (glTF -Z... see export note), wheels on the ground.

import bpy, bmesh, math, os
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import PROPS as OUT
os.makedirs(OUT, exist_ok=True)

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)


def lin(hexc):
    h = hexc.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


MATS = {}


def mat(name, col, rough=0.6, metal=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*lin(col), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*lin(col), 1)
    MATS[name] = m
    return m


class Part:
    """One named node of the prop, built from smooth tubes, tori and boxes."""

    def __init__(self, name, origin=(0, 0, 0)):
        self.name, self.origin = name, Vector(origin)
        self.bm = bmesh.new()
        self.mats = []

    def mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _tag(self, geom, m, smooth=True):
        idx = self.mi(m)
        for f in {f for v in geom for f in v.link_faces}:
            f.material_index = idx
            f.smooth = smooth

    def tube(self, a, b, r, m, segs=10, r2=None):
        a, b = Vector(a) - self.origin, Vector(b) - self.origin
        d = b - a
        M = Matrix.Translation((a + b) / 2) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=segs,
                                    radius1=r, radius2=r if r2 is None else r2, depth=d.length, matrix=M)
        self._tag(res['verts'], m)
        # a ball at each end so bends look welded rather than cut
        for p in (a, b):
            s = bmesh.ops.create_uvsphere(self.bm, u_segments=segs, v_segments=6, radius=r * 1.02, matrix=Matrix.Translation(p))
            self._tag(s['verts'], m)

    def torus(self, centre, axis, R, r, m, segs=40, rsegs=10, arc=(0, 2 * math.pi)):
        """A ring (or part of one) around axis; arc in radians, measured from +Z after aligning axis."""
        c = Vector(centre) - self.origin
        rot = Vector((1, 0, 0)).rotation_difference(Vector(axis).normalized()).to_matrix()
        verts = []
        n = segs + (0 if arc[1] - arc[0] >= 2 * math.pi - 1e-6 else 1)
        closed = n == segs
        for i in range(n):
            a = arc[0] + (arc[1] - arc[0]) * i / segs
            ring = []
            cen = Vector((0, math.sin(a) * R, math.cos(a) * R))
            for j in range(rsegs):
                b = 2 * math.pi * j / rsegs
                p = cen + cen.normalized() * math.cos(b) * r + Vector((math.sin(b) * r, 0, 0))
                ring.append(self.bm.verts.new(c + rot @ p))
            verts.append(ring)
        idx = self.mi(m)
        for i in range(n if closed else n - 1):
            r0, r1 = verts[i], verts[(i + 1) % n]
            for j in range(rsegs):
                f = self.bm.faces.new((r0[j], r1[j], r1[(j + 1) % rsegs], r0[(j + 1) % rsegs]))
                f.material_index = idx
                f.smooth = True

    def box(self, centre, size, m, rot=None, bevel=0.0):
        c = Vector(centre) - self.origin
        M = Matrix.Translation(c) @ (rot.to_4x4() if rot else Matrix()) @ Matrix.Diagonal((*size, 1))
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)
        self._tag(res['verts'], m, smooth=False)

    def ball(self, centre, r, m, scale=(1, 1, 1)):
        c = Vector(centre) - self.origin
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=16, v_segments=10, radius=r,
                                        matrix=Matrix.Translation(c) @ Matrix.Diagonal((*scale, 1)))
        self._tag(res['verts'], m)

    def finish(self, parent=None):
        me = bpy.data.meshes.new(self.name)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(self.name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = self.origin
        if parent:
            ob.parent = parent
            ob.location = self.origin - parent.location
        return ob


def export(root, path):
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for ch in root.children_recursive:
        ch.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True)


# ------------------------------------------------------------------ bicycle
# Sized for Sandra (hips 0.47 m above the ground, arms about 0.35 m long): a chunky, toy-like
# roadster. y = forward, x = to the rider's right, z = up.

FRAME = mat('BikeFrame', '#2f6b5a', 0.35, 0.3)        # painted steel: recoloured per bike in the game
GUARD = mat('BikeGuard', '#efe6d2', 0.4, 0.1)        # mudguards and chain guard
CHROME = mat('BikeChrome', '#c9ccd0', 0.22, 0.9)
TYRE = mat('BikeTyre', '#2a2624', 0.85)
RIMS = mat('BikeRim', '#b9bcc0', 0.3, 0.85)
SADDLE = mat('BikeSaddle', '#6b4226', 0.55)
GRIPS = mat('BikeGrip', '#5a3a26', 0.6)
WICKER = mat('BikeBasket', '#b98a52', 0.8)
LAMP = mat('BikeLamp', '#f5e9c8', 0.25)
PETAL = [mat('BasketFlowerRed', '#d8423f', 0.7), mat('BasketFlowerPink', '#ef8fb0', 0.7),
         mat('BasketFlowerYellow', '#f3c94e', 0.7), mat('BasketLeaf', '#5f8a3f', 0.8)]

# A real city bike with a long, low step-through frame, so it looks like a proper bicycle next to the
# buildings, yet Sandra, whose chunky legs are only about 28 cm from hip to ankle, can still ride it: the
# saddle is as high as her legs allow above the pedals (nearly straight at the bottom of each stroke, as on
# a well set-up bike), the cranks short. Round 21 (the user: the wheels and pedals sat too close to the
# ground): wheels 0.64 m across instead of 0.5, the same distance apart, and the pedals, saddle and
# handlebars raised with them, so next to her it reads as an ordinary bike.
WR, TR = 0.285, 0.035                   # wheel (rim centre) radius and tyre thickness: 0.64 m across
AXLE = WR + TR                          # axle height
REAR, FRONT = Vector((0, -0.56, AXLE)), Vector((0, 0.54, AXLE))
LIFT = 0.09                             # (how much higher the pedals, saddle and bars are than before round 21)
BB = Vector((0, -0.02, 0.15 + LIFT))    # bottom bracket
SEAT = Vector((0, -0.09, 0.37 + LIFT))  # top of the seat post
HEAD_LO, HEAD_HI = Vector((0, 0.33, 0.43 + 0.2)), Vector((0, 0.29, 0.55 + 0.2))    # (clear of the bigger front tyre and its guard)
CRANK = 0.06

root = bpy.data.objects.new('Bicycle', None)
bpy.context.scene.collection.objects.link(root)

frame = Part('Frame')
# step-through frame: two curved low tubes from the head to the bottom bracket
for k, off in enumerate((0.0, 0.05)):
    a, b = HEAD_LO + Vector((0, -0.005, -off)), BB + Vector((0, 0.03, 0.02 + off * 0.6))
    mid = (a + b) / 2 + Vector((0, -0.02, -0.03))
    frame.tube(a, mid, 0.017, FRAME)
    frame.tube(mid, b, 0.017, FRAME)
frame.tube(BB, SEAT + Vector((0, 0.01, -0.03)), 0.018, FRAME)                 # seat tube
for s in (-1, 1):
    frame.tube(BB + Vector((s * 0.03, 0, 0)), REAR + Vector((s * 0.05, 0, 0)), 0.011, FRAME)           # chain stays
    frame.tube(SEAT + Vector((s * 0.02, 0.0, -0.05)), REAR + Vector((s * 0.05, 0, 0)), 0.01, FRAME)     # seat stays
frame.tube(HEAD_LO, HEAD_HI, 0.022, FRAME)                                    # head tube
frame.tube(BB + Vector((-0.045, 0, 0)), BB + Vector((0.045, 0, 0)), 0.026, CHROME)
# saddle on its post
frame.tube(SEAT + Vector((0, 0, -0.04)), SEAT + Vector((0, -0.01, 0.03)), 0.011, CHROME)
frame.ball(SEAT + Vector((0, 0.0, 0.055)), 0.07, SADDLE, (0.85, 1.35, 0.32))
frame.ball(SEAT + Vector((0, -0.05, 0.06)), 0.07, SADDLE, (1.25, 0.8, 0.35))
for s in (-1, 1):                                                              # saddle springs
    frame.tube(SEAT + Vector((s * 0.035, -0.06, 0.0)), SEAT + Vector((s * 0.035, -0.06, 0.04)), 0.008, CHROME)
# mudguards and the chain guard
frame.torus(REAR, (1, 0, 0), AXLE + 0.025, 0.02, GUARD, 36, 8, (-0.62 * math.pi, 0.12 * math.pi))
frame.box((0.055, (BB.y + REAR.y) / 2, (BB.z + REAR.z) / 2 + 0.01), (0.012, 0.5, 0.06), GUARD,
          Matrix.Rotation(math.atan2(REAR.z - BB.z, REAR.y - BB.y), 3, 'X'))
frame.ball((0.05, BB.y, BB.z), 0.075, GUARD, (0.18, 1.0, 1.0))                    # chainring cover
frame_ob = frame.finish(root)

rack = Part('Rack')
for s in (-1, 1):
    rack.tube(REAR + Vector((s * 0.06, 0, 0.02)), REAR + Vector((s * 0.06, -0.02, AXLE + 0.05)), 0.007, CHROME)
    rack.tube(SEAT + Vector((s * 0.03, -0.05, -0.06)), REAR + Vector((s * 0.06, 0.05, AXLE + 0.05)), 0.006, CHROME)
rack.box((0, REAR.y - 0.01, REAR.z + AXLE + 0.055), (0.13, 0.24, 0.012), CHROME)
rack.finish(root)


def wheel(name, centre):
    w = Part(name, centre)
    w.torus(centre, (1, 0, 0), WR, TR, TYRE, 44, 12)
    w.torus(centre, (1, 0, 0), WR - TR * 0.9, 0.012, RIMS, 44, 8)
    w.tube(centre + Vector((-0.04, 0, 0)), centre + Vector((0.04, 0, 0)), 0.022, CHROME)
    for k in range(20):                                                       # crossed spokes, alternately to each side
        a = 2 * math.pi * k / 20
        side = 0.032 if k % 2 else -0.032
        rim = centre + Vector((0, math.sin(a) * (WR - 0.02), math.cos(a) * (WR - 0.02)))
        w.tube(centre + Vector((side, 0, 0)), rim, 0.0028, CHROME, 5)
    return w.finish(root)


wheel('RearWheel', REAR)

# steering: fork, front wheel, mudguard, handlebars, basket and lamp turn together about the head tube
steer_axis_top = HEAD_HI + (HEAD_HI - HEAD_LO).normalized() * 0.08
steer = bpy.data.objects.new('Steering', None)
bpy.context.scene.collection.objects.link(steer)
steer.parent = root
steer.location = HEAD_LO
fork = Part('Fork', HEAD_LO)
crown = HEAD_LO + Vector((0, 0.0, -0.02))
for s in (-1, 1):
    fork.tube(crown + Vector((s * 0.04, 0, 0)), FRONT + Vector((s * 0.045, -0.005, 0)), 0.012, FRAME, 10, 0.009)
fork.tube(crown + Vector((-0.045, 0, 0)), crown + Vector((0.045, 0, 0)), 0.016, FRAME)
fork.tube(HEAD_HI, steer_axis_top, 0.012, CHROME)                            # stem
bar_c = steer_axis_top + Vector((0, 0.07, 0.01))                               # reaching forward, so her arms do too
fork.tube(steer_axis_top, bar_c, 0.012, CHROME)
for s in (-1, 1):                                                              # gently swept-back handlebars
    p1 = bar_c + Vector((s * 0.12, -0.01, 0.01))
    p2 = bar_c + Vector((s * 0.2, -0.06, 0.0))
    fork.tube(bar_c, p1, 0.01, CHROME)
    fork.tube(p1, p2, 0.01, CHROME)
    fork.tube(p2, p2 + Vector((s * 0.015, -0.07, -0.005)), 0.015, GRIPS)
fork.ball(bar_c + Vector((0.08, 0.02, 0.02)), 0.022, CHROME, (1, 1, 0.6))     # bell
fork.torus(FRONT, (1, 0, 0), AXLE + 0.025, 0.02, GUARD, 36, 8, (-0.15 * math.pi, 0.55 * math.pi))
fork.ball(HEAD_LO + Vector((0, 0.07, 0.05)), 0.035, LAMP, (1, 1.2, 1))         # dynamo lamp
fork_ob = fork.finish(steer)
GRIP_L = bar_c + Vector((-0.215, -0.095, -0.004))
GRIP_R = bar_c + Vector((0.215, -0.095, -0.004))

basket = Part('Basket', HEAD_LO)
bc = Vector((0, HEAD_HI.y + 0.17, FRONT.z + AXLE + 0.11))       # clear of the front tyre
for k in range(5):                                                             # woven sides
    z = bc.z - 0.07 + k * 0.03
    basket.torus(Vector((0, bc.y, z)), (0, 0, 1), 0.105 + k * 0.004, 0.009, WICKER, 26, 6)
basket.box((0, bc.y, bc.z - 0.085), (0.2, 0.2, 0.012), WICKER)
basket.tube(HEAD_HI + Vector((0, 0.02, 0)), Vector((0, bc.y - 0.1, bc.z - 0.06)), 0.007, CHROME)
basket.finish(steer)
# Sandra's own bike (round 22): a dog-sized wicker basket where Trufa rides (the game hides it on other bikes;
# DogSeat marks where her paws go). Round 23, the user: "move the basket to the back of the bike", so it sits on
# the rear rack, deep enough that she sits down in it rather than up on it.
dog = Part('DogBasket')
RACK_TOP = REAR.z + AXLE + 0.055 + 0.006
dc = Vector((0, REAR.y - 0.05, RACK_TOP + 0.004))                # the basket's floor centre, on the rack
DL, DW, DH = 0.44, 0.32, 0.22
for k in range(7):                                              # woven sides: rounded-rectangle rings
    z = dc.z + 0.01 + k * DH / 7
    for sx in (-1, 1):
        dog.tube(Vector((sx * DW / 2, dc.y - DL / 2 + 0.03, z)), Vector((sx * DW / 2, dc.y + DL / 2 - 0.03, z)), 0.011, WICKER, 6)
    for sy in (-1, 1):
        dog.tube(Vector((-DW / 2 + 0.03, dc.y + sy * DL / 2, z)), Vector((DW / 2 - 0.03, dc.y + sy * DL / 2, z)), 0.011, WICKER, 6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            dog.ball(Vector((sx * (DW / 2 - 0.015), dc.y + sy * (DL / 2 - 0.015), z)), 0.016, WICKER)
for sx in (-1, 1):                                              # the uprights at the corners
    for sy in (-1, 1):
        dog.tube(Vector((sx * (DW / 2 - 0.01), dc.y + sy * (DL / 2 - 0.01), dc.z)),
                 Vector((sx * (DW / 2 - 0.01), dc.y + sy * (DL / 2 - 0.01), dc.z + DH + 0.01)), 0.012, WICKER, 6)
dog.box((0, dc.y, dc.z), (DW, DL, 0.014), WICKER)
for sy in (-1, 1):                                              # a rolled rim front and back
    dog.tube(dc + Vector((-DW / 2 + 0.01, sy * (DL / 2 - 0.02), DH + 0.012)), dc + Vector((DW / 2 - 0.01, sy * (DL / 2 - 0.02), DH + 0.012)), 0.014, WICKER, 8)
for sx in (-1, 1):                                              # two straps round the rack
    dog.box((sx * 0.07, dc.y, RACK_TOP - 0.004), (0.025, 0.05, 0.03), SADDLE)
dog.finish(root)
e = bpy.data.objects.new('DogSeat', None)
bpy.context.scene.collection.objects.link(e)
e.parent = root
e.location = dc + Vector((0, 0.0, 0.008))
flowers = Part('BasketFlowers', HEAD_LO)
import random
fr = random.Random(4)
for k in range(9):
    a, rr = fr.uniform(0, 6.28), fr.uniform(0, 0.07)
    p = Vector((math.cos(a) * rr, bc.y + math.sin(a) * rr, bc.z + 0.05 + fr.uniform(0, 0.05)))
    flowers.ball(p, 0.03, PETAL[k % 3], (1, 1, 0.7))
    flowers.ball(p + Vector((fr.uniform(-0.03, 0.03), fr.uniform(-0.03, 0.03), -0.025)), 0.03, PETAL[3], (1.3, 0.8, 0.35))
flowers.finish(steer)
wheel_f = wheel('FrontWheel', FRONT)
wheel_f.parent = steer
wheel_f.location = FRONT - HEAD_LO

cranks = Part('Cranks', BB)
cranks.ball(BB, 0.06, CHROME, (0.12, 1, 1))
cranks.tube(BB + Vector((0.06, 0, 0)), BB + Vector((0.06, 0, -CRANK)), 0.01, CHROME)
cranks.tube(BB + Vector((-0.06, 0, 0)), BB + Vector((-0.06, 0, CRANK)), 0.01, CHROME)
cranks_ob = cranks.finish(root)
for nm, s, dz in (('PedalR', 1, -CRANK), ('PedalL', -1, CRANK)):
    pp = BB + Vector((s * 0.1, 0, dz))
    ped = Part(nm, pp)
    ped.box(pp, (0.06, 0.045, 0.014), mat('BikePedal', '#2b2b2b', 0.7))
    ped.finish(cranks_ob)

# markers the game uses to place Sandra: where she sits and where her hands and feet go
for nm, p, par in (('SeatPoint', SEAT + Vector((0, -0.02, 0.07)), root), ('GripL', GRIP_L, steer), ('GripR', GRIP_R, steer)):
    e = bpy.data.objects.new(nm, None)
    bpy.context.scene.collection.objects.link(e)
    e.parent = par
    e.location = p - (par.location if par is steer else Vector())

export(root, os.path.join(OUT, 'bicycle.glb'))
print('PROPS OK', sorted(os.listdir(OUT)))
