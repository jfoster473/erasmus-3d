# Every interior of the 2D game (its INTERIORS), built from its own furniture lists: the flats, the
# cafés and shops, the university and its library, the Sagrada Família, the MNAC, and Gaudí's houses.
# Run from build_assets.py (exec'd there, sharing its helpers). Writes interior.glb (paths.OUT), every room
# in it side by side (ROOM_GAP metres apart) under an empty named Interior_<id>, and scene.json
# "interiors": for each room its offset, size, the way out, what is solid, what can be looked at or
# opened, where its lights are and how high its walls are.
#
# Rooms are measured in 1 m tiles, as in the 2D game: x across, y from the back wall (row 0, where the
# windows and pictures hang) to the front (row h), whose wall is cut away low so the camera can look in;
# the way out is a gap in it at x = exit. Pieces the Meshy furniture covers (beds, drawers, shelves,
# wardrobes, plants, desks, chairs, the phone, lamps, sofas, little tables, the kitchen) use it.

ROOM_GAP = 40.0
PIERS = []
exec(open(os.path.join(BUILD, 'sagrada_inside.py')).read())
exec(open(os.path.join(BUILD, 'sagrat_inside.py')).read())     # (round 26: the Sagrat Cor's crypt and upper church)
# (The user's rule, 21 Oct 2026: houses keep their simple square rooms; only the churches are built fully in 3D.
#  batllo_inside.py stays on disk, unused.)
FLAT = os.path.join(MESHY_DIR, 'flat')
MESHY_FLAT = os.path.exists(os.path.join(FLAT, 'bed.glb'))
FACING = {'back': 0.0, 'east': math.pi / 2, 'west': -math.pi / 2, 'north': math.pi}
MESHY_FURN = {  # 2D kind -> (file, height m, width scale)
    'bed': ('bed.glb', 0.72, 0.8), 'drawer': ('drawers.glb', 0.95, 1.0), 'bookshelf': ('bookshelf.glb', 2.0, 1.0),
    'bookcase': ('bookshelf.glb', 2.0, 1.0), 'cupboard': ('wardrobe.glb', 2.05, 1.0), 'plant': ('plant.glb', 0.8, 0.8),
    'desk': ('desk.glb', 1.15, 1.0), 'chair': ('chair.glb', 0.95, 1.0), 'phone': ('phone.glb', 0.95, 1.0),
    'lamp': ('floor_lamp.glb', 1.7, 1.0), 'sofa': ('sofa.glb', 0.85, 1.0), 'rtable': ('side_table.glb', 0.6, 1.0),
    'kitchen': ('kitchen.glb', 1.25, 1.0)}
# Sandra's flat keeps its hand-placed furniture: (file, centre x, y, facing, height, width scale, kind)
SANDRA_FURN = [('bed.glb', 1.95, 2.05, 'back', 0.72, 0.8, 'bed'), ('drawers.glb', 3.35, 1.42, 'back', 0.95, 1.0, 'drawer'),
               ('bookshelf.glb', 4.45, 1.28, 'back', 2.0, 1.0, 'bookshelf'), ('wardrobe.glb', 8.65, 1.47, 'back', 2.05, 1.0, 'cupboard'),
               ('bed.glb', 12.05, 2.05, 'back', 0.72, 0.8, 'bed_rosa'), ('plant.glb', 12.4, 3.8, 'west', 0.8, 0.8, 'plant'),
               ('desk.glb', 1.48, 5.5, 'east', 1.15, 1.0, 'desk'), ('chair.glb', 2.45, 5.55, 'west', 0.95, 1.0, 'chair'),
               ('phone.glb', 1.3, 7.75, 'east', 0.95, 1.0, 'phone'), ('floor_lamp.glb', 1.55, 8.85, 'east', 1.7, 1.0, 'lamp'),
               ('sofa.glb', 6.5, 7.35, 'north', 0.85, 1.0, 'sofa'), ('side_table.glb', 6.5, 5.7, 'back', 0.6, 1.0, 'rtable'),
               ('kitchen.glb', 12.72, 5.45, 'west', 1.25, 1.0, 'kitchen')]
WALL_HEIGHT = {'int_sagrada': 9.0, 'int_mnac': 5.0, 'int_upf': 4.0, 'int_upf_lib': 4.6}

M_WALLTOP = mat('WallCut', '#7a5a40', 0.9)
M_WOOD = mat('Wood', '#8a5d3b', 0.6)
M_WOOD2 = mat('WoodLight', '#b88a5a', 0.6)
M_LINEN = mat('Linen', '#f4f0e8', 0.9)
M_SKY = mat('WindowSky', '#bfe0f2', 0.1)
M_SEA = mat('Seascape', '#ffffff', 0.8, image=IMG_SEA)
M_APPL = mat('Appliance', '#eceae4', 0.4)
M_TIN = mat('Tin', '#c8c8c4', 0.35, 0.8)
M_HOB = mat('Hob', '#222222', 0.4)
M_LAMPSHADE = mat('LampShade', '#f6e3b8', 0.6)
M_PHONERED = mat('PhoneRed', '#b8322e', 0.4)
M_CARD = mat('Card', '#f2a6b8', 0.7)
M_BOOKS = [mat('Book%d' % i, c, 0.8) for i, c in enumerate(['#8a3a32', '#2f5a7a', '#c9a24a', '#3e6b4a', '#6a4a7a', '#d8cbb0'])]
M_GOODS = [mat('Shelfgoods%d' % i, c, 0.6) for i, c in enumerate(['#d8342f', '#f2c84b', '#3a6aa8', '#5cb85c', '#f4f0e8', '#c98a4a', '#8a3a32'])]
M_BLACKBOARD = mat('Blackboard', '#2f3d33', 0.8)
M_CORK = mat('Cork', '#b98a52', 0.95)
M_BRASSY = M_BRASS
M_GLASSCASE = mat('GlassCase', '#bfd8e0', 0.05, 0.1)
M_STONECOL = mat('ColumnStone', '#e3d8c2', 0.9)
M_VELVET = mat('Velvet', '#7a2a3a', 0.9)
M_GILT = mat('Gilt', '#d4a640', 0.35, 0.8)


def floor_image(kind, cols):
    """A 1 m floor texture for each kind of floor (64 px)."""
    c = [rgb(x) for x in cols] if cols else None
    r = random.Random(kind)

    def fn(x, y):
        k = 1 + r.uniform(-0.03, 0.03)
        if kind == 'hydraulic':
            return tuple(v * k for v in hydraulic(x * 2, y * 2))
        if kind == 'wood':
            plank = (y // 10) % 2
            v = 0.55 + 0.05 * math.sin(x * 0.3 + y) + (0.05 if plank else 0)
            return (0.62 * v * k + (0.0 if x % 64 else -0.1), 0.42 * v * k, 0.26 * v * k)
        if kind == 'parquet':
            v = ((x // 8) + (y // 16)) % 2
            return ((0.6 if v else 0.52) * k, (0.4 if v else 0.34) * k, 0.24 * k)
        if kind == 'terracotta':
            if x % 32 < 1 or y % 32 < 1:
                return (0.7, 0.62, 0.52)
            return (0.72 * k, 0.4 * k, 0.28 * k)
        if kind == 'tile':
            if x % 16 < 1 or y % 16 < 1:
                return (0.72, 0.74, 0.74)
            return (0.9 * k, 0.91 * k, 0.9 * k)
        if kind == 'carpet':
            return (0.32 * k, 0.4 * k, 0.32 * k)
        if kind == 'stone':
            if x % 32 < 1 or y % 21 < 1:
                return (0.62, 0.58, 0.52)
            return (0.82 * k, 0.77 * k, 0.68 * k)
        if kind == 'marble':
            v = 0.9 + 0.06 * math.sin(x * 0.2 + math.sin(y * 0.15) * 3)
            return (v * k, v * k * 0.98, v * k * 0.95)
        if kind == 'brick':
            row = y // 8
            if y % 8 < 1 or (x + (8 if row % 2 else 0)) % 16 < 1:
                return (0.68, 0.6, 0.52)
            return (0.66 * k, 0.36 * k, 0.26 * k)
        return (0.7, 0.66, 0.6)
    return make_image('floor_' + kind, 64, 64, fn)


FLOOR_MATS = {}


def floor_mat(kind, cols):
    key = kind + str(cols)
    if key not in FLOOR_MATS:
        if kind == 'hydraulic' and cols:
            FCOL[:] = [rgb(x) for x in cols]                 # the tile pattern in this room's colours
        FLOOR_MATS[key] = mat('Floor_' + kind + str(len(FLOOR_MATS)), '#ffffff', 0.5 if kind in ('marble', 'tile') else 0.75,
                              image=floor_image(kind, cols))
    return FLOOR_MATS[key]


def build_room(rid, R, k):
    """Builds room rid (2D INTERIORS entry R) at offset k * ROOM_GAP along x. Returns its scene record."""
    if rid == 'int_sagrada':
        return build_sagrada_room(rid, R, k)                     # (sagrada_inside.py: the basilica, walked round freely)
    if rid == 'int_sagrat_cor':
        return build_crypt_room(rid, R, k)                       # (sagrat_inside.py: the Sagrat Cor's crypt, and above it
    if rid == 'int_sagrat_alta':
        return build_upper_room(rid, R, k)                       #  the upper church)
    w, h = int(R['w']), int(R['h'])
    ex = int(R['exit']) if R.get('exit') is not None else None
    ox = k * ROOM_GAP
    WH = WALL_HEIGHT.get(rid, 3.2 if R.get('gaudi') or R.get('shop') else 2.7)
    room, floor = MB(), MB(uv=True)
    objs = []

    def fbox(x0, y0, x1, y1, z0, z1, m, mb=None):
        (mb or room).abox(ox + x0, -y0, z0, ox + x1, -y1, z1, m)

    M_WALL = mat('RoomWall' + R['wall'], R['wall'], 0.95)
    M_TRIM = mat('RoomTrim' + R['trim'], R['trim'], 0.7)
    fm = floor_mat(R.get('floor', 'wood'), R.get('fcol'))
    floor.face([(ox + 1, -1, 0), (ox + w - 1, -1, 0), (ox + w - 1, -h, 0), (ox + 1, -h, 0)], fm, normal=(0, 0, 1), uvscale=1.0)
    fbox(0.8, 0.8, w - 0.8, 1.0, 0, WH, M_WALL)                       # back wall
    fbox(0.8, 1.0, 1.0, h + 0.2, 0, WH, M_WALL)                       # left
    fbox(w - 1.0, 1.0, w - 0.8, h + 0.2, 0, WH, M_WALL)               # right
    for (a, b, c_, d) in ((0.8, 0.8, w - 0.8, 1.0), (0.8, 1.0, 1.0, h + 0.2), (w - 1.0, 1.0, w - 0.8, h + 0.2)):
        fbox(a, b, c_, d, WH, WH + 0.02, M_WALLTOP)
    gaps = [(ex, ex + 1)] if ex is not None else []
    xs = [0.8] + [v for g in gaps for v in g] + [w - 0.8]
    for a, b in zip(xs[::2], xs[1::2]):                                # cut-away front wall, open at the way out
        fbox(a, h, b, h + 0.2, 0, 0.55, M_WALL)
        fbox(a, h, b, h + 0.2, 0.55, 0.57, M_WALLTOP)
    if ex is not None:
        fbox(ex, h, ex + 1, h + 0.2, 0, 0.01, M_TRIM)                  # threshold
    fbox(1.0, 1.0, w - 1.0, 1.04, 0, 0.12, M_TRIM)                    # skirting
    fbox(1.0, 1.0, 1.04, h, 0, 0.12, M_TRIM)
    fbox(w - 1.04, 1.0, w - 1.0, h, 0, 0.12, M_TRIM)
    ceil = MB()
    ceil.abox(ox + 0.8, -0.8, WH, ox + w - 0.8, -h - 0.2, WH + 0.1, M_WALLTOP)
    solids, things, stairs, windows, lamps = [], [], [], [], []
    PIERS.clear()
    rr = random.Random(rid)

    def meshy_furn(f, cx, cy, face, height, xs_, kind, text=None, extra=None):
        me = meshy_mesh(os.path.join('flat', f), 9000 if kind != 'plant' else 14000, 'base', 1024)
        if kind == 'bed_rosa':
            if 'RosaBed' not in bpy.data.meshes:
                m2 = me.copy()
                m2.name = 'RosaBed'
                mt = me.materials[0].copy()
                nt = mt.node_tree
                bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
                alb = next(l.from_node for l in nt.links if l.to_node == bsdf and l.to_socket.name == 'Base Color')
                alb.image = hue_swap(alb.image, 345 - 360, 22, 0.42, '#8fb3a0', 'rosa_blanket')
                m2.materials[0] = mt
            me = bpy.data.meshes['RosaBed']
        ob = bpy.data.objects.new('Furn_%s_%s' % (rid, kind), me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = (ox + cx, -cy, 0)
        ob.rotation_euler = (0, 0, FACING[face])
        ob.scale = (height * xs_, height, height)
        objs.append(ob)
        xs2 = [v.co.x for v in me.vertices]
        ys2 = [v.co.y for v in me.vertices]
        hw, hd = (max(xs2) - min(xs2)) / 2 * height * xs_, (max(ys2) - min(ys2)) / 2 * height
        if face in ('east', 'west'):
            hw, hd = hd, hw
        if kind not in ('lamp',):
            solids.append([round(cx - hw + 0.06, 3), round(cy - hd + 0.06, 3), round(cx + hw - 0.06, 3), round(cy + hd - 0.06, 3)])
        return hw, hd

    if rid == 'int_sandra' and MESHY_FLAT:
        for (f, cx, cy, face, height, xs_, kind) in SANDRA_FURN:
            meshy_furn(f, cx, cy, face, height, xs_, kind)
        fbox(7.1, 8.2, 7.9, 9.9, 0, 0.012, mat('Runner', '#3e6b6a', 0.95))          # a runner by the door
        fbox(7.15, 8.25, 7.85, 9.85, 0.012, 0.016, mat('RunnerInner', '#d9a35a', 0.95))
    for obj in R['objs']:
        kind, x, y = obj[0], float(obj[1]), float(obj[2])
        o = obj[3] if len(obj) > 3 else {}
        ow, oh = float(o.get('w', 1)), float(o.get('h', 2 if kind == 'bed' else 1))
        col = o.get('col')
        solid = True
        # where it stands against: the back wall, a side wall, or out in the room
        face = 'back' if y <= 1.5 else ('east' if x <= 1.5 else ('west' if x + ow >= w - 1.5 else 'back'))
        if rid == 'int_sandra' and MESHY_FLAT and kind in MESHY_FURN:
            solid = False                                              # (placed by hand above)
        elif kind == 'rtable' and (rid.startswith('int_cafe') or rid == 'int_berlin'):     # (both cafés: the Berlín's too)
            # (round 41, the user: "could you make the tables in side the cafe big enough to sit at? Currently, they're
            # very small") a café table, not a side table: a round marble top 0.76 m across at table height (0.76 m)
            # on an iron column and foot
            cx_, cy_ = x + ow / 2, y + oh / 2
            room.cone(Matrix.Translation((ox + cx_, -cy_, 0.02)), 16, 0.24, 0.26, 0.04, M_IRON)
            room.cone(Matrix.Translation((ox + cx_, -cy_, 0.38)), 8, 0.035, 0.035, 0.72, M_IRON)
            room.cone(Matrix.Translation((ox + cx_, -cy_, 0.745)), 24, 0.38, 0.38, 0.03, M_MARBLE)
            solids.append([round(cx_ - 0.38, 3), round(cy_ - 0.38, 3), round(cx_ + 0.38, 3), round(cy_ + 0.38, 3)])
            solid = False
        elif MESHY_FLAT and kind in MESHY_FURN:
            f, height, xs_ = MESHY_FURN[kind]
            if kind == 'bed':
                cx, cy = x + 0.5, y + 1.0
            else:
                cx, cy = x + ow / 2, y + oh / 2 if y > 1.5 else y + 0.42
            if face == 'east':
                cx = x + 0.45
            elif face == 'west':
                cx = x + ow - 0.45
            if kind == 'sofa' and 1.5 < y and x > 1.5 and x + ow < w - 1.5:
                face = 'north' if y > h / 2 else 'back'
            face = o.get('face', face)                                 # (round 24: the library's chairs face their table)
            meshy_furn(f, cx, cy, face, height, xs_, kind)
            solid = False                                              # (it added its own footprint)
        elif kind in ('window', 'gwin'):
            fbox(x - .05, 0.78, x + ow + .05, 1.02, 0.02, 2.5, M_WOOD)
            fbox(x + .04, 1.02, x + ow - .04, 1.03, 0.1, 2.42, M_SKY)
            fbox(x + ow / 2 - .02, 1.02, x + ow / 2 + .02, 1.05, 0.1, 2.42, M_WOOD)
            for zz in (0.75, 1.35, 1.9):
                fbox(x + .04, 1.02, x + ow - .04, 1.045, zz - .02, zz + .02, M_WOOD)
            if kind == 'gwin':                                         # Gaudí's: coloured glass roundels
                for j in range(4):
                    fbox(x + .15 + j * (ow - .3) / 4, 1.04, x + .15 + (j + 0.8) * (ow - .3) / 4, 1.05, 1.9, 2.3, M_GOODS[j % 7])
            else:
                for sx in (-0.48, ow + 0.03):
                    fbox(x + sx, 1.0, x + sx + .45, 1.04, 0.1, 2.38, M_WOOD2)
            fbox(x - .1, 1.0, x + ow + .1, 1.06, 2.5, 2.58, M_TRIM)
            windows.append([ox + x + ow / 2, 1.7, 1.7])
            solid = False
        elif kind == 'glass':                                          # stained glass, high on the wall
            cool = str(o.get('cool')) == 'True'
            pal = ['#2f6ab0', '#3aa0a0', '#5cb85c', '#2f4f8f'] if cool else ['#d9533f', '#f0a030', '#f2c84b', '#c8322e']
            for j in range(int(ow)):
                for zz in range(4):
                    fbox(x + j + 0.1, 1.0, x + j + 0.9, 1.03, 2.5 + zz * 1.4, 3.7 + zz * 1.4, mat('Stained' + pal[(j + zz) % 4], pal[(j + zz) % 4], 0.1))
            windows.append([ox + x + ow / 2, 4.0, 1.7])
            solid = False
        elif kind == 'painting':
            fbox(x + .1, 1.0, x + .9, 1.04, 1.25, 1.95, M_WOOD)
            if o.get('art') == 'portrait':
                fbox(x + .15, 1.04, x + .85, 1.045, 1.3, 1.9, mat('PortraitDark', '#3a3028', 0.8))
                fbox(x + .38, 1.045, x + .62, 1.05, 1.55, 1.8, mat('PortraitFace', '#e0c4a0', 0.8))
            elif o.get('art') == 'sea':
                floor.face([(ox + x + .15, -1.045, 1.3), (ox + x + .85, -1.045, 1.3), (ox + x + .85, -1.045, 1.9), (ox + x + .15, -1.045, 1.9)],
                           M_SEA, normal=(0, -1, 0), uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
            else:
                fbox(x + .15, 1.04, x + .85, 1.045, 1.3, 1.9, M_GOODS[rr.randrange(7)])
            solid = False
        elif kind in ('fresco', 'fresco2'):
            fbox(x + .1, 1.0, x + ow - .1, 1.04, 1.0, 3.2, mat('Fresco', '#c9a46a', 0.9))
            for j in range(5):
                fbox(x + .3 + j * (ow - .6) / 5, 1.04, x + .3 + (j + 0.7) * (ow - .6) / 5, 1.045, 1.3 + (j % 2) * 0.6, 2.4 + (j % 2) * 0.6, M_GOODS[(j * 3) % 7])
            solid = False
        elif kind in ('chalk', 'blackboard', 'notice', 'sign'):
            mm = M_CORK if kind == 'notice' else (M_BLACKBOARD if kind != 'sign' else mat('SignBoard', '#2f4f6f', 0.6))
            yy = 1.0 if y <= 1 else y + 0.45
            fbox(x + .1, yy, x + ow - .1, yy + .04, 1.2 if kind != 'sign' else 1.4, 2.2 if kind != 'sign' else 1.9, mm)
            if kind == 'notice':
                for j in range(5):
                    fbox(x + .2 + j * 0.3, 1.04, x + .4 + j * 0.3, 1.045, 1.4 + (j % 2) * 0.3, 1.7 + (j % 2) * 0.3, M_LINEN)
            solid = kind == 'sign'
        elif kind == 'rug':
            fbox(x + .1, y + .1, x + ow - .1, y + oh - .1, 0, .012, mat('Rug' + str(col), col or '#b8583a', 0.95))
            fbox(x + .35, y + .35, x + ow - .35, y + oh - .35, .012, .016, mat('RugInner', '#d98a5a', 0.95))
            solid = False
        elif kind == 'bed':
            fbox(x + .05, y + .02, x + ow - .05, y + 1.95, 0, .32, M_WOOD)
            fbox(x + .05, y, x + ow - .05, y + .08, 0, .95, M_WOOD)
            fbox(x + .08, y + .1, x + ow - .08, y + 1.9, .32, .48, M_LINEN)
            fbox(x + .06, y + .6, x + ow - .06, y + 1.93, .4, .54, mat('Blanket' + str(col), col or '#e9a38a', 0.95))
            oh = 2
        elif kind in ('shelf', 'deptshelf', 'aisle', 'libshelf', 'display'):
            dep = 0.5 if kind != 'aisle' else 0.8
            y0 = y if y > 1.5 else 1.0
            fbox(x + .05, y0, x + ow - .05, y0 + dep, 0, 0.06, M_WOOD)
            for side in (x + .05, x + ow - .1):
                fbox(side, y0, side + .05, y0 + dep, 0, 1.9, M_WOOD)
            for j in range(4):
                z = 0.35 + j * 0.45
                fbox(x + .05, y0, x + ow - .05, y0 + dep, z, z + .03, M_WOOD)
                bx = x + .15
                while bx < x + ow - .2:
                    if kind in ('libshelf', 'deptshelf'):                  # books
                        bw_ = rr.uniform(.06, .18)
                        fbox(bx, y0 + .05, bx + bw_, y0 + dep - .05, z + .03, z + .03 + rr.uniform(.18, .32), M_BOOKS[rr.randrange(6)])
                    else:
                        # groceries: a run of the same thing (tins, jars or packets), short and squat, in rows
                        # front to back, then a gap: not tall coloured spines like books
                        kind_ = rr.random()
                        m_ = M_GOODS[rr.randrange(7)]
                        n_ = rr.randint(2, 4)
                        for _ in range(n_):
                            if kind_ < 0.5:
                                r_ = rr.uniform(.045, .06)
                                bw_ = 2 * r_
                                hh = rr.choice((.09, .12, .16))
                                for yy in [y0 + .1 + j * .14 for j in range(int((dep - .1) / .14))]:
                                    room.cone(Matrix.Translation((ox + bx + r_, -yy, z + .03 + hh / 2)), 10, r_, r_, hh, M_TIN if kind_ < 0.25 else m_)
                            else:
                                bw_ = rr.uniform(.1, .14)
                                hh = rr.choice((.08, .12))
                                for yy in [y0 + .06 + j * .2 for j in range(int((dep - .06) / .2))]:
                                    fbox(bx, yy, bx + bw_, yy + .16, z + .03, z + .03 + hh, m_)
                            bx += bw_ + .015
                            if bx > x + ow - .2:
                                break
                        bx += rr.uniform(.06, .14)
                        continue
                    bx += bw_ + .02
            if kind == 'display':                                      # a glass top over the goods
                fbox(x + .05, y0, x + ow - .05, y0 + dep, 1.95, 1.98, M_GLASSCASE)
            oh = dep + (y0 - y)
        elif kind in ('counter', 'libdesk'):
            fbox(x + .05, y + .15, x + ow - .05, y + .85, 0, .95, M_WOOD2 if kind == 'counter' else M_WOOD)
            fbox(x, y + .1, x + ow, y + .9, .95, 1.0, M_STONE)
            if o.get('pastry'):
                fbox(x + .5, y + .2, x + 2.5, y + .8, 1.0, 1.35, M_GLASSCASE)
                for j in range(6):
                    room.sphere(Matrix.Translation((ox + x + .7 + j * .3, -(y + .5), 1.07)) @ Matrix.Diagonal((1, 1, 0.6, 1)), .1, M_GOODS[5], (8, 6))
            if o.get('till'):
                fbox(x + .3, y + .3, x + .7, y + .6, 1.0, 1.25, M_HOB)
            if o.get('torro'):
                for j in range(5):
                    fbox(x + .4 + j * .5, y + .3, x + .8 + j * .5, y + .6, 1.0, 1.08, mat('Torro', '#f2e2b8', 0.6))
        elif kind == 'coffee':
            fbox(x + .1, y + .2, x + .9, y + .7, 0, .9, M_WOOD)
            fbox(x + .15, y + .25, x + .85, y + .65, .9, 1.4, M_BRASSY)
        elif kind == 'oven':
            fbox(x + .05, y, x + ow - .05, y + .9, 0, 1.6, mat('OvenBrick', '#a0563a', 0.9))
            fbox(x + .3, y + .9, x + ow - .3, y + .92, .5, 1.0, M_HOB)
        elif kind == 'fridge':                                         # a tall white fridge, its door and handle
            fx0, fy0 = x + ow / 2 - .35, (y if y > 1.5 else 1.0) + .05
            fbox(fx0, fy0, fx0 + .7, fy0 + .65, 0, 1.8, M_APPL)
            fbox(fx0 + .02, fy0 + .65, fx0 + .68, fy0 + .67, 1.18, 1.2, M_HOB)
            fbox(fx0 + .56, fy0 + .67, fx0 + .6, fy0 + .71, 0.8, 1.1, M_STONE)
            fbox(fx0 + .56, fy0 + .67, fx0 + .6, fy0 + .71, 1.3, 1.6, M_STONE)
        elif kind == 'fridgeRow':
            fbox(x + .05, y, x + ow - .05, y + .7, 0, 1.9, M_APPL)
            fbox(x + .1, y + .7, x + ow - .1, y + .72, .2, 1.8, M_GLASSCASE)
            for j in range(int(ow * 3)):
                fbox(x + .15 + j * .32, y + .2, x + .4 + j * .32, y + .6, 1.0, 1.25, M_GOODS[j % 7])
        elif kind == 'pfand':
            # two bottle-return machines side by side against the wall: green cabinets with a white front,
            # a round dark bottle mouth, a small screen and a receipt slot
            green, white = mat('PfandGreen', '#3f7a3f', 0.6), mat('PfandFront', '#eef1ee', 0.5)
            mw = (ow - .3) / 2
            for j in range(2):
                a = x + .1 + j * (mw + .1)
                fbox(a, y + .02, a + mw, y + .72, 0, 1.85, green)
                fbox(a + .08, y + .72, a + mw - .08, y + .74, .25, 1.7, white)
                for (dy, r_, m_) in ((.75, .14, mat('PfandRim', '#c9ccd0', 0.4, 0.6)), (.77, .1, M_HOB)):   # the bottle mouth
                    room.cone(Matrix.Translation((ox + a + mw / 2, -(y + dy), 1.15)) @ Matrix.Rotation(math.pi / 2, 4, 'X'),
                              16, r_, r_, .03, m_)
                fbox(a + mw / 2 - .16, y + .74, a + mw / 2 + .16, y + .76, 1.42, 1.62, mat('PfandScreen', '#8fd8c0', 0.2))
                fbox(a + mw / 2 - .08, y + .74, a + mw / 2 + .08, y + .76, .72, .75, M_HOB)       # the receipt slot
        elif kind in ('table', 'readtable'):
            fbox(x + .05, y + .1, x + ow - .05, y + oh - .1, .72, .77, M_WOOD)
            for (lx, ly) in ((x + .1, y + .15), (x + ow - .15, y + .15), (x + .1, y + oh - .2), (x + ow - .15, y + oh - .2)):
                fbox(lx, ly, lx + .05, ly + .05, 0, .72, M_WOOD)
            if kind == 'readtable':
                for j in range(int(ow)):
                    room.cone(Matrix.Translation((ox + x + .5 + j, -(y + oh / 2), .95)), 8, .1, .14, .3, M_LAMPSHADE)
            if o.get('books'):
                # (round 24) a few books left on it: one open, a closed one or two, a little pile
                for j, (bx_, by_) in enumerate(((.55, .25), (ow - .9, oh - .55), (ow / 2 + .25, .3))):
                    m_ = M_BOOKS[(j * 2 + int(x)) % 6]
                    if j == 0:
                        for sd in (0, 1):                                  # open: two pages, a little tilted up
                            fbox(x + bx_ + sd * .17, y + by_, x + bx_ + .16 + sd * .17, y + by_ + .24, .77, .785, M_LINEN)
                        fbox(x + bx_ - .01, y + by_ - .01, x + bx_ + .35, y + by_ + .25, .77, .775, m_)
                    else:
                        for k in range(1 + j % 2):
                            fbox(x + bx_ + k * .02, y + by_ - k * .01, x + bx_ + .2 + k * .02, y + by_ + .28 - k * .01,
                                 .77 + k * .04, .81 + k * .04, M_BOOKS[(j + k + 3) % 6])
        elif kind in ('seats', 'pew', 'bench', 'calvetchair', 'armchair'):
            m_ = M_WOOD if kind != 'armchair' else M_VELVET
            fbox(x + .05, y + .2, x + ow - .05, y + .7, .42, .48, m_)
            fbox(x + .05, y + .62, x + ow - .05, y + .7, .48, .95 if kind != 'bench' else .5, m_)
            for lx in (x + .1, x + ow - .15):
                fbox(lx, y + .25, lx + .05, y + .65, 0, .42, m_)
            if kind == 'seats':
                # the fold-down desks (round 41: 0.27 m deep, not 0.15 — the exam scene's hands and paper reach past a
                # narrower one and curled over its edge)
                fbox(x + .05, y - .07, x + ow - .05, y + .2, .7, .74, M_WOOD2)
        elif kind == 'lectern':
            # (round 22, the user: lower, and its top sloping so he can rest his papers on it: low on the speaker's
            # side, towards the back wall, rising towards the room, with a little lip to stop them sliding)
            fbox(x + .32, y + .34, x + .68, y + .72, 0, .72, M_WOOD)
            fbox(x + .26, y + .28, x + .74, y + .78, 0, .05, M_WOOD)
            lo, hi, th = .74, .9, .04
            P_ = lambda xx, yy, zz: (ox + xx, -yy, zz)
            xa, xb, ya, yb = x + .16, x + .84, y + .18, y + .86
            T_ = [P_(xa, ya, lo), P_(xb, ya, lo), P_(xb, yb, hi), P_(xa, yb, hi)]
            U_ = [P_(xa, ya, lo - th), P_(xb, ya, lo - th), P_(xb, yb, hi - th), P_(xa, yb, hi - th)]
            room.face(T_, M_WOOD2, normal=(0, 0.6, 1))
            room.face(U_, M_WOOD2, normal=(0, -0.6, -1))
            for i_, nrm_ in ((0, (0, 1, 0)), (1, (1, 0, 0)), (2, (0, -1, 0)), (3, (-1, 0, 0))):
                j_ = (i_ + 1) % 4
                room.face([T_[i_], T_[j_], U_[j_], U_[i_]], M_WOOD2, normal=nrm_)
            fbox(xa, ya - .03, xb, ya + .01, lo - .01, lo + .045, M_WOOD)       # the lip on his side
        elif kind == 'chest':
            fbox(x + .1, y + .2, x + .9, y + .8, 0, .5, M_WOOD2)
            fbox(x + .08, y + .18, x + .92, y + .82, .5, .56, M_WOOD)
        elif kind == 'column':
            room.cone(Matrix.Translation((ox + x + .5, -(y + .5), WH / 2)), 12, .32, .28, WH, M_STONECOL)
            for z_ in (0.15, WH - 0.2):
                fbox(x + .1, y + .1, x + .9, y + .9, z_ - .15, z_ + .15, M_STONECOL)
        elif kind in ('altar', 'model', 'statue', 'restore', 'fireplace', 'fountain', 'organ'):
            if kind == 'altar':
                fbox(x + .2, y + .2, x + ow - .2, y + .9, 0, 1.0, M_MARBLE)
                room.cone(Matrix.Translation((ox + x + ow / 2, -(y + .5), WH - 2.0)), 16, 1.5, 1.0, 0.3, M_GILT)
            elif kind == 'model':
                fbox(x + .2, y + .2, x + .8, y + .8, 0, .8, M_WOOD)
                room.cone(Matrix.Translation((ox + x + .5, -(y + .5), 1.3)), 10, .2, .05, 1.0, M_LINEN)
            elif kind == 'statue':
                fbox(x + .2, y + .2, x + .8, y + .8, 0, .9, M_MARBLE)
                room.cone(Matrix.Translation((ox + x + .5, -(y + .5), 1.45)), 10, .2, .14, 1.1, M_MARBLE)
                room.sphere(Matrix.Translation((ox + x + .5, -(y + .5), 2.1)), .13, M_MARBLE, (10, 8))
            elif kind == 'restore':
                fbox(x + .1, y + .2, x + .9, y + .5, 0, 1.5, M_WOOD)
                fbox(x + .15, y + .5, x + .85, y + .55, .7, 1.4, mat('Canvas', '#c9a46a', 0.9))
            elif kind == 'fireplace':
                fbox(x + .05, y, x + ow - .05, y + .5, 0, 1.3, M_MARBLE)
                fbox(x + .3, y + .45, x + ow - .3, y + .52, .1, .8, M_HOB)     # (round 41: 2 cm proud, it flickered flush)
            elif kind == 'fountain':
                room.cone(Matrix.Translation((ox + x + ow / 2, -(y + oh / 2), .25)), 20, ow / 2, ow / 2, .5, M_MARBLE)
                room.cone(Matrix.Translation((ox + x + ow / 2, -(y + oh / 2), .5)), 20, ow / 2 - .1, ow / 2 - .1, .02, mat('FountainWater', '#6f9fa8', 0.05, 0.1))
            elif kind == 'organ':
                for j in range(int(ow * 4)):
                    room.cone(Matrix.Translation((ox + x + .15 + j * .25, -(y + .3), 1.5 + (j % 5) * .2)), 8, .07, .07, 3.0 + (j % 5) * .4, M_GILT)
        elif kind == 'crate':
            # (round 22, Casa Trias's cellar) wooden crates, stencilled, some stacked; one open, packed with straw
            for j_ in range(int(o.get('n', 2))):
                cx_, cy_ = x + .1 + (j_ % 2) * .55, y + .15 + (j_ // 2) * .55
                fbox(cx_, cy_, cx_ + .5, cy_ + .5, 0, .5, mat('CrateWood', '#a07a4e', 0.9))
                fbox(cx_ + .03, cy_ - .005, cx_ + .47, cy_ + .002, .15, .35, mat('CrateStencil', '#3a3a3a', 0.9))
            if o.get('open'):
                fbox(x + .1, y + .15, x + .6, y + .65, .5, .52, mat('Straw', '#d9c06a', 0.95))
        elif kind == 'plinth':
            # a marble plinth (the Casa Museu Gaudí's: empty until the Salamandreta comes home)
            fbox(x + .2, y + .2, x + .8, y + .8, 0, 1.0, M_MARBLE)
            fbox(x + .15, y + .15, x + .85, y + .85, 1.0, 1.06, M_MARBLE)
        elif kind == 'dust':
            # red clay dust on the floor, a trail scuffed along (a clue)
            for j_ in range(6):
                xx = x + j_ * ow / 6
                fbox(xx + .05, y + .3 + .08 * (j_ % 2), xx + ow / 6 - .02, y + .55 + .08 * (j_ % 2), 0, .006, mat('ClayDust', '#b5603a', 0.98))
            solid = False
        elif kind == 'cellardoor':
            # a low wooden door in the back wall, a stair down behind it (the game keeps it locked without the key)
            fbox(x + .15, .98, x + ow - .15, 1.06, 0, 1.7, M_WOOD2)
            fbox(x + .05, .95, x + ow - .05, 1.0, 1.7, 1.85, M_WOOD)
            fbox(x + ow - .35, .9, x + ow - .25, .98, .85, .95, M_GILT)
            stairs.append({'pos': [x + ow / 2, 1.6], 'to': o.get('to'), 'dir': o.get('dir'), 'lock': o.get('lock', '')})
            solid = False
        elif kind == 'scaffold':
            for (lx, ly) in ((x, y), (x + ow, y), (x, y + 1), (x + ow, y + 1)):
                room.cone(Matrix.Translation((ox + lx, -ly, WH / 2)), 4, .04, .04, WH, mat('Scaffold', '#c9c9c4', 0.5, 0.6))
            for z_ in (1.5, 3.0, 4.5):
                fbox(x, y, x + ow, y + 1, z_, z_ + .04, M_WOOD)
        elif kind == 'grandstair':
            # the university's grand stair: a wide flight rising to a landing, stone balustrades either side, and
            # the way on up to the library above the landing: an arch in the back wall, or (round 23, the stair in
            # the room's bottom right corner) in the right-hand wall beside a deeper landing. Walk up it.
            n_ = 12
            land = float(o.get('landing', 0.6))
            run = (oh - land) / n_
            for j in range(n_):
                y_ = y + oh - (j + 1) * run
                fbox(x + .1, y_, x + ow - .1, y_ + run + .02, 0, .2 * (j + 1), M_STONE)
            fbox(x + .1, y, x + ow - .1, y + land, 0, .2 * n_, M_STONE)                       # the landing
            sides = (x,) if o.get('arch') == 'right' else (x, x + ow - .1)
            for sx in sides:
                for j in range(9):                                                              # balusters, climbing
                    yy = y + oh - .2 - j * (oh - land) / 8
                    zb = .2 * n_ * min(1.0, (y + oh - yy) / (oh - land))
                    fbox(sx + .02, yy - .03, sx + .08, yy + .03, zb, zb + .9, M_LINEN)
                room.face([(ox + sx, -(y + oh), 1.0), (ox + sx + .1, -(y + oh), 1.0), (ox + sx + .1, -(y + land), 2.4 + 1.0), (ox + sx, -(y + land), 2.4 + 1.0)],
                          M_STONE, normal=(0, 0, 1))                                            # the handrail
            if o.get('arch') == 'right':
                fbox(w - .03, y + .15, w, y + land - .15, 2.4, 2.4 + 1.5, mat('StairArch', '#3a2a22', 0.9))   # the way on up
                fbox(w - .05, y + .05, w, y + land - .05, 2.4 + 1.5, 2.4 + 1.62, M_TRIM)
                solids.append([round(x + ow - .12, 3), round(y + land, 3), round(x + ow, 3), round(y + oh, 3)])   # (the wall side)
            else:
                fbox(x + .3, 1.0, x + ow - .3, 1.03, 2.4, 2.4 + 1.5, mat('StairArch', '#3a2a22', 0.9))   # the way on up, in shadow
                fbox(x + .15, 1.0, x + ow - .15, 1.05, 2.4 + 1.5, 2.4 + 1.62, M_TRIM)
            stairs.append({'pos': [x + ow / 2, y + oh - 0.8], 'to': o.get('to'), 'dir': o.get('dir'),
                           'rect': [x + .3, y + .2, x + ow - .3, y + oh - 0.35], 'go': [0, -1],
                           'arrive': [x + ow / 2, y + oh + 0.7], 'face': [0, 1]})
            solid = False
        elif kind == 'stairwell':
            # the top of the stair down (round 24, the user: "not such an eyesore"): a neat opening framed in wood, its
            # steps going down in warm wood, each a shade darker than the one above, a lighter nosing on each; a
            # turned-baluster balustrade with a handrail along its open side(s), newel posts with round caps. Walk
            # down it (towards the room's front).
            frame_m = M_WOOD2
            fbox(x, y, x + ow, y + oh, 0, .014, frame_m)
            n_ = max(4, int((oh - .3) / .42))
            for j in range(n_):
                t = j / max(1, n_ - 1)
                c_ = tuple(int(a_ * (1 - t) + b_ * t) for a_, b_ in ((0xb0, 0x3e), (0x86, 0x2e), (0x5c, 0x22)))
                sm = mat('StairStep%d' % j, '#%02x%02x%02x' % c_, 0.85)
                y0_ = y + .2 + j * (oh - .25) / n_
                y1_ = y + .2 + (j + 1) * (oh - .25) / n_
                fbox(x + .14, y0_, x + ow - .14, y1_, .014, .02, sm)
                fbox(x + .14, y0_, x + ow - .14, y0_ + .05, .02, .024, mat('StairNose%d' % j, '#%02x%02x%02x' % tuple(min(255, int(v * 1.25)) for v in c_), 0.8))
            sides = [x] + ([x + ow - .08] if x + ow < w - .4 else [])
            for sx_ in sides:
                fbox(sx_, y, sx_ + .08, y + oh, 0, .08, M_WOOD)                        # the bottom rail
                fbox(sx_ - .01, y, sx_ + .09, y + oh, .9, .96, M_WOOD)                 # the handrail
                yy_ = y + .2
                while yy_ < y + oh - .1:
                    room.cone(Matrix.Translation((ox + sx_ + .04, -yy_, .49)), 6, .022, .03, .82, M_WOOD)
                    room.sphere(Matrix.Translation((ox + sx_ + .04, -yy_, .3)), .04, M_WOOD, (6, 4))
                    yy_ += .22
                for ny_ in (y + .05, y + oh - .05):                                    # the newel posts
                    fbox(sx_ - .02, ny_ - .06, sx_ + .1, ny_ + .06, 0, 1.02, M_WOOD)
                    room.sphere(Matrix.Translation((ox + sx_ + .04, -ny_, 1.08)), .07, M_WOOD2, (8, 5))
            stairs.append({'pos': [x + ow / 2, y + 0.6], 'to': o.get('to'), 'dir': o.get('dir'),
                           'rect': [x + .3, y + .25, x + ow - .3, y + oh], 'go': [0, 1],
                           'arrive': [x + ow / 2, y - 0.7], 'face': [0, -1]})
            for sx_ in sides:
                solids.append([round(sx_ - .05, 3), round(y + .1, 3), round(sx_ + .13, 3), round(y + oh, 3)])
            solid = False
        elif kind == 'banner':
            # a long red banner of the university's, its letters in white
            bc = mat('Banner' + str(col), col or '#c8102e', 0.8)
            fbox(x + .1, 1.0, x + .9, 1.04, 1.2, 3.6, bc)
            ob = text_obj('UPF', 0.32, mat('BannerText', '#ffffff', 0.7), (ox + x + .5, -1.06, 3.0), 0.0, 'BannerText_%s_%d' % (rid, len(objs)))
            objs.append(ob)
            solid = False
        elif kind == 'vending':
            fbox(x + .1, y + .1, x + .95, y + .8, 0, 1.85, mat('Vending', '#7a1f1f', 0.5))
            fbox(x + .08, y + .2, x + .1, y + .7, .9, 1.7, mat('VendingGlass', '#f2e6c8', 0.2))
        elif kind == 'porter':
            fbox(x + .05, y + .15, x + ow - .05, y + .85, 0, 1.05, M_WOOD)
            fbox(x, y + .1, x + ow, y + .9, 1.05, 1.1, M_WOOD2)
            fbox(x + ow - .6, y + .3, x + ow - .2, y + .6, 1.1, 1.3, mat('Radio', '#3a3a3a', 0.5))
        elif kind == 'pier':
            # the reservoir's brick piers; arches join them (below, once every pier is placed)
            bm_ = mat('Brick', '#a8553a', 0.9)
            fbox(x - .3, y - .3, x + .3, y + .3, 0, WH, bm_)
            fbox(x - .38, y - .38, x + .38, y + .38, 0, .25, bm_)
            PIERS.append((x, y))
            ow, oh = 0.6, 0.6
            x, y = x - .3, y - .3
        elif kind == 'stairs':
            for j in range(6):
                fbox(x + .05, y + .85 - j * .15, x + .95, y + .95 - j * .15, 0, .1 + j * .17, M_STONE)
            stairs.append({'pos': [x + .5, y + .5], 'to': o.get('to'), 'dir': o.get('dir')})
            solid = False
        elif kind == 'arches':
            for j in range(int(ow)):
                for jj in range(10):
                    a = math.pi * jj / 9
                    fbox(x + j + .5 + math.cos(a) * .45 - .05, y + .4, x + j + .5 + math.cos(a) * .45 + .05, y + .6,
                         WH - 1.0 + math.sin(a) * .8, WH - .9 + math.sin(a) * .8, M_LINEN)
            solid = False
        elif kind in ('palmceil', 'dome'):
            room.cone(Matrix.Translation((ox + x + ow / 2, -(y + oh / 2), WH - .3)), 16, max(ow, oh) / 2, .2, .6, M_GILT if kind == 'palmceil' else M_STONE)
            solid = False
        elif kind == 'aisle':
            pass
        else:                                                          # anything else: a plain piece of furniture
            fbox(x + .1, y + .1, x + ow - .1, y + oh - .1, 0, .8, M_WOOD)
        if solid:
            pad = {'plant': .15, 'lamp': .25, 'chair': .2, 'rtable': .1, 'phone': .15, 'column': .15}.get(kind, .03)
            solids.append([round(x + pad, 3), round(y + (0 if y <= 1 else pad), 3), round(x + ow - pad, 3), round(y + oh - pad, 3)])
        if kind == 'lamp' or kind == 'readtable':
            lamps.append([ox + x + 0.5, 1.5, y + 0.5])
        info = {k_: v for k_, v in o.items() if k_ in ('t', 'c', 'sleep', 'card', 'party', 'vase', 'label', 'books', 'till', 'clue')}
        if info or kind in ('counter', 'pfand', 'phone', 'libdesk'):
            cy_ = y + (oh / 2 if y > 1 else 1.0)
            tx_ = x + ow / 2
            if rid == 'int_sandra' and MESHY_FLAT:
                # (round 23) Sandra's furniture stands where it was placed by hand, not on the 2D game's tiles: E finds
                # each piece where it is seen (the bed's used to sit by the bedside table, the table's by the shelves)
                k_ = 'bed_rosa' if kind == 'bed' and x > 6 else kind
                for (f_, fx, fy, *_r) in SANDRA_FURN:
                    if _r[-1] == k_:
                        tx_, cy_ = fx, fy
            things.append(dict(info, kind=kind, pos=[round(tx_, 3), round(cy_, 3)]))
    # brick arches between neighbouring piers (the library's reservoir), springing just under the ceiling
    for (px, py) in PIERS:
        for (qx, qy) in PIERS:
            if (qx - px, qy - py) in ((4.0, 0.0), (0.0, 3.4)):
                L = math.hypot(qx - px, qy - py)
                for j in range(12):
                    a0, a1 = math.pi * j / 12, math.pi * (j + 1) / 12
                    f0, f1 = (1 - math.cos(a0)) / 2, (1 - math.cos(a1)) / 2
                    z0_, z1_ = WH - 1.3 + math.sin(a0) * 1.1, WH - 1.3 + math.sin(a1) * 1.1
                    ax, ay = px + (qx - px) * f0, py + (qy - py) * f0
                    bx, by = px + (qx - px) * f1, py + (qy - py) * f1
                    hx, hy = (0.18, 0.0) if qx == px else (0.0, 0.18)
                    fbox(min(ax, bx) - hx, min(ay, by) - hy, max(ax, bx) + hx, max(ay, by) + hy, min(z0_, z1_) - .12, max(z0_, z1_) + .1,
                         mat('Brick', '#a8553a', 0.9))
    # the room's objects under one empty, so the game can show just the room Sandra is in
    root = bpy.data.objects.new('Interior_' + rid, None)
    bpy.context.scene.collection.objects.link(root)
    parts = [room.finish('Room_' + rid), floor.finish('Floor_' + rid), ceil.finish('Ceiling_' + rid)] + objs
    for ob in parts:
        ob.parent = root
    INT_ROOTS.append(root)
    npcs = [nid for nid, n in W2['NPCS'].items() if n['at'][0] == rid]
    return {'name': R['name'], 'offset': [ox, 0], 'w': w, 'h': h, 'floor': [1, 1, w - 1, h],
            'exit': [ex, ex + 1] if ex is not None else None, 'spawn': [ex + 0.5 if ex is not None else w / 2, h - 1.0],
            'solids': solids, 'things': things, 'stairs': stairs, 'npcs': npcs, 'wall_h': WH,
            'lights': {'ceiling': [ox + w / 2, WH - 0.25, h / 2 + 0.5], 'windows': windows, 'lamps': lamps},
            'shop': bool(R.get('shop')), 'kind': next((k_ for k_ in ('sacred', 'museum', 'gaudi', 'shop') if R.get(k_)), 'home')}


def hue_swap(img, h_lo, h_hi, min_sat, target, name):
    """A copy of a texture with one band of hues repainted in another colour (keeping the shading)."""
    import numpy as np
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(-1, 4)
    c = a[:, :3]
    mx, mn = c.max(1), c.min(1)
    d = mx - mn + 1e-6
    r, g, b = c[:, 0], c[:, 1], c[:, 2]
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    sat = d / (mx + 1e-6)
    inband = ((hue >= h_lo + 360) | (hue <= h_hi)) if h_lo < 0 else ((hue >= h_lo) & (hue <= h_hi))
    mask = inband & (sat > min_sat)
    lum = c @ np.array([0.3, 0.59, 0.11], dtype=np.float32)
    ref = np.median(lum[mask]) if mask.any() else 0.5
    t = np.array(rgb(target), dtype=np.float32)
    c[mask] = np.clip(t[None, :] * (lum / ref)[:, None], 0, 1)[mask]
    im2 = bpy.data.images.new(name, w, h, alpha=False)
    im2.pixels.foreach_set(a.ravel())
    im2.file_format = 'PNG'
    im2.pack()
    return im2


INT_ROOTS = []
scene['interiors'] = {}
for k_, (rid, R) in enumerate(W2['INTERIORS'].items()):
    scene['interiors'][rid] = build_room(rid, R, k_)
    print('ROOM', rid, len(scene['interiors'][rid]['things']), 'things')
scene['interior_gap'] = ROOM_GAP
export(INT_ROOTS, os.path.join(OUT, 'interior.glb'))
