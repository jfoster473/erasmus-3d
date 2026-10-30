# The buildings the 2D game names (its BUILDINGS list), in the places it puts them:
#   whole-block landmarks   the Sagrada Família, the MNAC (the Palau Nacional), Universitat Pompeu
#                           Fabra, and the Parc de la Ciutadella with its Cascada
#   Gaudí houses            Casa Batlló, Casa Milà (La Pedrera), Casa Vicens, Casa Calvet, Palau Güell:
#                           each a five-bay front of its own along one side of a block
#   shops                   Cafè Berlín, Llibreria El Drac, Torrons Casa Joan, Cafè de la Rambla,
#                           Carrefour Express, Torrons del Mar: the kit's houses, with the shop's own
#                           sign, colours and door
#   friends' flats          Alba's, Maria's, Alice's and Alessandra's: a house with its own front door
# Each enterable one gets an entrance (scene.json "entrances") leading to its interior.
# Run from build_assets.py, after kit.py (exec'd there, sharing its helpers).

SCHEMES = {  # frame, awning (two stripes), facade, trade (for the window display and what goes outside)
    'berlin': ('#3a3a5a', ('#2f2f35', '#efe6d2'), '#e8d9bf', 'bakery'),
    'drac': ('#2f4f3f', ('#7a2a3a', '#efe6d2'), '#d9c3a0', 'books'),
    'joan': ('#8c2f2a', ('#8c2f2a', '#f5ecd6'), '#efd9b4', 'torro'),
    'rambla': ('#2f6b5a', ('#2f6b5a', '#efe6d2'), '#e6c08a', 'bar'),
    'carrefour': ('#2c5aa0', ('#2c5aa0', '#ffffff'), '#e2e2dc', 'fruit'),
    'mar': ('#2f5d8a', ('#2f5d8a', '#f2ead8'), '#f0e2c8', 'torro'),
}
ENTRANCES = scene.setdefault('entrances', [])
DOOR_PLAQUES = []            # (foot of the wall beside the door, along, out, name): built after the blocks
nrng = random.Random(2024)


def entrance_at(spec, F_, s, h=2.24, w=1.24, base=KERB, arch=0.0, glow=None):
    """Records the door of a building: s metres along its front (frame F_), its sill at base (a terrace's top).
    (round 33) arch: the door's curved top (metres; door_unit), glow: where the door's face is (Blender space), when
    it isn't on the front's line — the game draws the glow there, the door's own size and shape."""
    p = F_.at(s, 0, base - KERB)
    keep_clear(F_.at(s, 2.5, 0), max(2.5, w / 2 + 1.5))       # no tree, bench or bins in front of the door, out to the kerb
    ENTRANCES.append({'id': spec['id'], 'int': spec.get('int'), 'name': spec['name'], 'pos': bl_m(p),
                      'normal': [round(F_.n[0], 3), round(-F_.n[1], 3)], 'size': [w, h], 'base': base,
                      'plaque': spec.get('plaque', '')})
    if arch > 0:
        ENTRANCES[-1]['arch'] = round(arch, 3)
    if glow is not None:
        ENTRANCES[-1]['glow'] = bl_m(glow)
    # a small brass plaque on the wall beside the door, where the game offers "Read the plaque"
    if spec.get('plaque'):
        side = Vector((F_.n[1], -F_.n[0], 0)) * (w / 2 + 0.45)
        DOOR_PLAQUES.append((p + side + F_.N * 0.0, F_.U, F_.N, spec['name'], ENTRANCES[-1]))


def shop_house(spec):
    frame, awn, facade, trade = SCHEMES.get(spec.get('scheme'), ('#5a3b28', None, '#e8d2b0', 'bakery'))
    rng = random.Random(spec['id'])
    return dict(bays=5, uppers=4, facade=facade, style='classic', shutter=rng.randrange(4), num=rng.randrange(2, 90),
                balc=['long', 'iron', 'iron', 'box'], ground=['shop', 'shop', 'shopdoor', 'shop', 'shop'],
                shop=dict(name=spec['name'].upper(), frame=frame, awning=awn, kind=trade, wares=spec.get('scheme') not in ('rambla',)),
                plants=['geranium', 'pink', 'herbs', 'none'], seed=rng.randrange(1, 99999), entrance=spec)


def apt_houses(spec, rng):
    """A side of a block with a friend's house in the middle: their own front door."""
    look = W2['NPCS'].get(spec['id'].replace('apt_', ''), {}).get('look', {})
    mine = dict(gen_house(rng, 1, False, rng.randrange(2, 90)), ground=['portal'], shop=None, tribuna=[],
                facade=rng.choice(['#e8c9a8', '#f2dcc0', '#e3b8a0', '#d9e0d8']), entrance=spec)
    return [gen_house(rng, 2, False, mine['num'] - 2), mine, gen_house(rng, 2, False, mine['num'] + 2)]


# ------------------------------------------------------------------ Gaudí's houses (five-bay fronts)

def trencadis_mat(name, cols, seed):
    """Broken-tile mosaic: irregular chips of colour with pale grout."""
    rr = random.Random(seed)
    pal = [rgb(c) for c in cols]

    def fn(x, y):
        cx, cy = x // 6, y // 6
        r2 = random.Random(cx * 7919 + cy * 104729 + seed)
        if (x % 6 == 0) or (y % 6 == 0) or ((x + y) % 11 == 0 and r2.random() < 0.3):
            return (0.86, 0.84, 0.8)
        c = pal[r2.randrange(len(pal))]
        k = 0.92 + r2.random() * 0.16
        return (c[0] * k, c[1] * k, c[2] * k)
    return mat(name, '#ffffff', 0.45, image=kit_image(name, 96, 96, fn))


def gaudi_front(mb, cards, F_, s0, width, house, H, rng, extras):
    g = house['gaudi']
    bays = 5
    bw = width / bays
    stone = M_STONE
    mf = house.get('meshy')
    if mf:
        # (round 41) Meshy's house, its width the side's share, its wall on the street line (its balconies out over
        # the pavement, as the real ones), standing on the pavement
        d_ = MESHY_GAUDI_GROUND.get(mf, 0.0) * width
        bk_rot = math.atan2(F_.N[1], F_.N[0]) + math.pi / 2
        bk_ob = meshy_place(mf, MESHY_GAUDI_TRIS, 'front', width, F_.at(s0 + width / 2, d_, KERB - 0.02),
                            bk_rot, 'MeshyGaudi_' + g, 4096)   # (its 4K painting kept)
        # (round 41, the user: "I can see holes in the facade") where Meshy's surface has gaps (behind a column, under a
        # ledge) the sky and the houses beyond showed through: a plain stone backing 1 m behind its wall, up to just
        # under its own roofline in 16 strips, so a gap shows shadowed stone
        bk_wall = MESHY_GAUDI_GROUND.get(mf, 0.0)
        bk_tops = [0.0] * 16
        for v in bk_ob.data.vertices:
            if v.co.y < bk_wall + 0.15:
                k_ = min(15, max(0, int((v.co.x + 0.5) * 16)))
                bk_tops[k_] = max(bk_tops[k_], v.co.z)
        bk_sg = 1.0 if math.cos(bk_rot) * F_.U[0] + math.sin(bk_rot) * F_.U[1] > 0 else -1.0
        bk_m = mat('MeshyBacking', '#bdb2a6', 0.95)
        for k_ in range(16):
            h_ = KERB + bk_tops[k_] * width - 0.6
            if h_ > KERB + 4.4:
                sa_ = s0 + width / 2 + bk_sg * (k_ / 16 - 0.5) * width
                sb_ = s0 + width / 2 + bk_sg * ((k_ + 1) / 16 - 0.5) * width
                # (from the first floor up: lower down it hid the shops in the ground floor's arches)
                mb.face([F_.at(sa_, -1.0, KERB + 3.4), F_.at(sb_, -1.0, KERB + 3.4), F_.at(sb_, -1.0, h_), F_.at(sa_, -1.0, h_)], bk_m,
                        normal=tuple(F_.N))
    elif g == 'casa_batllo':
        wall = trencadis_mat('Trencadis_Batllo', ['#7fb6c8', '#5a9ab5', '#a8d0c8', '#d9a8c0', '#e8d8a0', '#88b8a0'], 3)
        mb.face([F_.at(s0, 0, GROUND_H + 2.6), F_.at(s0 + width, 0, GROUND_H + 2.6), F_.at(s0 + width, 0, H), F_.at(s0, 0, H)], wall,
                normal=tuple(F_.N), uvscale=2.5)
        # the "bones": a stone ground and first floor with big rounded openings and bony columns
        mb.face([F_.at(s0, 0, 0), F_.at(s0 + width, 0, 0), F_.at(s0 + width, 0, GROUND_H + 2.6), F_.at(s0, 0, GROUND_H + 2.6)],
                mat('BoneStone', '#e8dcc4', 0.85), normal=tuple(F_.N), uvscale=2.0)
        for b in range(bays + 1):
            s = s0 + b * bw
            for z0 in (0.2, GROUND_H + 0.2):
                mb.cone(Matrix.Translation(F_.at(s, 0.25, z0 + 1.2)), 8, 0.22, 0.12, 2.4, mat('Bone', '#efe6d2', 0.6))
        for b in range(bays):
            s = s0 + (b + 0.5) * bw
            if b != 2:                                                  # (round 33: the middle bay is the door)
                F_.box(mb, s, 0.03, GROUND_H + 1.3, bw / 2 - 0.35, 0.03, 1.1, M_SHOPGLASS)
            for f in range(2, house['uppers']):
                z = GROUND_H + f * FLOOR_H
                std_window(mb, F_, s, z, 1, rng.random() < 0.3, rng, fine_mb=mb)
                # the "masks": little white balconies like carnival masks
                mb.sphere(Matrix.Translation(F_.at(s, 0.35, z + 0.75)) @ Matrix.Diagonal((0.9, 0.35, 0.45, 1)), 0.8, mat('MaskWhite', '#f2efe8', 0.4), (12, 6))
        # the dragon's back: a scaly hump of a roof, and the tower with its cross
        for k in range(12):
            t = (k + 0.5) / 12
            ss = s0 + t * width
            hz = H + 0.6 + 1.6 * math.sin(math.pi * t)
            mb.sphere(Matrix.Translation(F_.at(ss, -1.0, hz)) @ Matrix.Diagonal((1.0, 1.6, 0.6, 1)), 0.75,
                      [mat('Scale%d' % j, c, 0.35) for j, c in enumerate(['#4f8a6a', '#8a5a9a', '#d98a3a', '#3a7a9a'])][k % 4], (10, 6))
        mb.cone(Matrix.Translation(F_.at(s0 + 1.6, -0.6, H + 2.4)), 10, 0.55, 0.45, 4.8, mat('BoneStone', '#e8dcc4', 0.85))
        mb.sphere(Matrix.Translation(F_.at(s0 + 1.6, -0.6, H + 5.2)), 0.6, M_GOLD, (12, 8))
        for k in range(2):
            F_.box(mb, s0 + 1.6, -0.6, H + 6.2, 0.4 if k else 0.08, 0.08, 0.08 if k else 0.4, M_GOLD)
    elif g == 'casa_mila':
        # La Pedrera: rippling cream stone, every storey a wave, with tangled iron balconies
        cream = mat('PedreraStone', '#e9dfcb', 0.9)
        for f in range(house['uppers'] + 1):
            z0 = 0 if f == 0 else GROUND_H + (f - 1) * FLOOR_H
            z1 = GROUND_H + f * FLOOR_H
            n = 24
            for k in range(n):
                a0, a1 = s0 + width * k / n, s0 + width * (k + 1) / n
                d0 = 0.35 * math.sin(k / n * math.pi * 3 + f)
                d1 = 0.35 * math.sin((k + 1) / n * math.pi * 3 + f)
                mb.face([F_.at(a0, d0, z0), F_.at(a1, d1, z0), F_.at(a1, d1, z1), F_.at(a0, d0, z1)], cream, normal=tuple(F_.N), uvscale=2.0)
                mb.face([F_.at(a0, d0, z1), F_.at(a1, d1, z1), F_.at(a1, d1 - 0.5, z1), F_.at(a0, d0 - 0.5, z1)], cream, normal=(0, 0, 1))
            if f == 0:
                continue
            for b in range(bays):
                s = s0 + (b + 0.5) * bw
                d = 0.35 * math.sin((s - s0) / width * math.pi * 3 + f)
                F_.box(mb, s, d + 0.03, z0 + 1.2, 0.8, 0.03, 0.9, M_GLASS_LIT if rng.random() < 0.25 else M_GLASS)
                for k in range(9):                                     # seaweed ironwork
                    x = s - 0.8 + k * 0.2
                    mb.tube(F_.at(x, d + 0.5, z0 + 0.15), F_.at(x + rng.uniform(-0.25, 0.25), d + 0.55, z0 + 1.0), 0.03, M_IRON, 4)
        # the warriors on the roof: chimneys like helmeted soldiers
        for k in range(6):
            p = F_.at(s0 + 1.5 + k * (width - 3) / 5, -2.5 - (k % 2) * 1.5, H)
            mb.cone(Matrix.Translation(p + Vector((0, 0, 1.1))), 8, 0.4, 0.25, 2.2, cream)
            mb.sphere(Matrix.Translation(p + Vector((0, 0, 2.4))), 0.38, trencadis_mat('Trencadis_Pedrera', ['#9a8a6a', '#c8b88a', '#6a7a5a'], 5), (10, 6))
        for f in range(1, house['uppers']):                            # no ordinary windows: they're in the waves
            pass
    elif g == 'casa_vicens':
        # red brick and rows of green-and-white tiles, little turrets at the top
        brick = mat('VicensBrick', '#b0583a', 0.9)
        tiles_ = kit_image('vicens_tiles', 32, 32, lambda x, y: rgb('#2f7a4a') if ((x // 8) + (y // 8)) % 2 == 0 else rgb('#f2efe2'))
        tm = mat('VicensTiles', '#ffffff', 0.4, image=tiles_)
        mb.face([F_.at(s0, 0, 0), F_.at(s0 + width, 0, 0), F_.at(s0 + width, 0, H), F_.at(s0, 0, H)], brick, normal=tuple(F_.N), uvscale=1.0)
        for f in range(house['uppers'] + 1):
            z = GROUND_H + f * FLOOR_H - 0.3
            F_.box(mb, s0 + width / 2, 0.05, z, width / 2, 0.05, 0.25, tm)
        for b in range(bays):
            s = s0 + (b + 0.5) * bw
            for f in range(house['uppers']):
                z = GROUND_H + f * FLOOR_H
                std_window(mb, F_, s, z, 1, rng.random() < 0.3, rng, fine_mb=mb)
                railing(fine() or mb, F_, s, 0.7, z + 0.14, 0.45, rng)
            if b != 2:                                                  # (round 33: the middle bay is the door)
                F_.box(mb, s, 0.04, 1.4, 0.6, 0.03, 1.0, M_GLASS)
        for s in (s0 + 0.8, s0 + width / 2, s0 + width - 0.8):
            mb.cone(Matrix.Translation(F_.at(s, -0.5, H + 1.0)), 8, 0.7, 0.7, 2.0, tm)
            mb.cone(Matrix.Translation(F_.at(s, -0.5, H + 2.5)), 8, 0.8, 0.05, 1.0, brick)
    elif g == 'casa_calvet':
        # baroque cream stone, a curved gable at the top, an oriel over the door
        stonem = mat('CalvetStone', '#e8d6b4', 0.9)
        mb.face([F_.at(s0, 0, 0), F_.at(s0 + width, 0, 0), F_.at(s0 + width, 0, H), F_.at(s0, 0, H)], stonem, normal=tuple(F_.N), uvscale=1.6)
        for b in range(bays):
            s = s0 + (b + 0.5) * bw
            for f in range(house['uppers']):
                z = GROUND_H + f * FLOOR_H
                if b == 2 and f == 0:
                    F_.box(mb, s, 0.5, z + 1.2, 1.1, 0.5, 1.1, stonem)                                   # the oriel
                    F_.box(mb, s, 1.0, z + 1.3, 0.9, 0.02, 0.7, M_GLASS)
                    continue
                std_window(mb, F_, s, z, 2, rng.random() < 0.3, rng, fine_mb=mb)
                F_.box(mb, s, 0.3, z + 0.07, 0.8, 0.3, 0.07, stonem)
                railing(fine() or mb, F_, s, 0.78, z + 0.14, 0.55, rng)
        for k in range(13):                                                 # the double-curved gable
            t = k / 12
            hz = H + 0.4 + 2.4 * math.sin(math.pi * t) ** 0.6
            F_.box(mb, s0 + 2 + t * (width - 4), 0.0, hz / 2, (width - 4) / 24 + 0.05, 0.15, hz / 2, stonem)
        for s in (s0 + 3, s0 + width - 3):
            mb.sphere(Matrix.Translation(F_.at(s, 0.1, H + 2.6)), 0.35, stonem, (10, 6))
    elif g == 'palau_guell':
        # grey stone, two great parabolic arches for doors, colourful chimneys behind
        grey = mat('GuellStone', '#bdb5a6', 0.9)
        mb.face([F_.at(s0, 0, 0), F_.at(s0 + width, 0, 0), F_.at(s0 + width, 0, H), F_.at(s0, 0, H)], grey, normal=tuple(F_.N), uvscale=1.6)
        iron_g = mat('GuellIron', '#2e2b2a', 0.5, 0.5)
        for sx in (-2.8, 2.8):
            c = s0 + width / 2 + sx
            # (round 35, the everything-visit: the arch was 14 separate iron cubes standing off the wall, which read as
            # loose black blocks; now one band of iron round the same parabola, as the real gates' frames are)
            def AP(a, dr, d):
                return F_.at(c + math.cos(a) * (1.3 + dr), d, 0.2 + math.sin(a) * (3.4 + dr))
            for k in range(24):
                a0, a1 = math.pi * k / 24, math.pi * (k + 1) / 24
                mb.face([AP(a0, 0.14, 0.2), AP(a1, 0.14, 0.2), AP(a1, -0.14, 0.2), AP(a0, -0.14, 0.2)], iron_g, normal=tuple(F_.N))
                am = (a0 + a1) / 2
                for dr in (0.14, -0.14):
                    mb.face([AP(a0, dr, 0.0), AP(a1, dr, 0.0), AP(a1, dr, 0.2), AP(a0, dr, 0.2)], iron_g,
                            normal=tuple(Vector(AP(am, dr, 0.1)) - Vector(AP(am, 0.0, 0.1))))      # (out from the band, either side)
            # (round 33: real doors in the two parabolic arches; the right-hand one is the way in)
            door_unit(mb, F_.at(c, 0.0, KERB), F_.u, F_.n, 2.3, 3.3, 3.1, M_WOOD_DOOR, None)
        for b in range(bays):
            s = s0 + (b + 0.5) * bw
            for f in range(1, house['uppers']):
                z = GROUND_H + f * FLOOR_H
                std_window(mb, F_, s, z, 3, rng.random() < 0.3, rng, fine_mb=mb)
        F_.box(mb, s0 + width / 2, 0.4, GROUND_H + 1.3, width / 2 - 1.0, 0.4, 1.1, grey)                     # the long tribune
        for k in range(10):
            F_.box(mb, s0 + 1.5 + k * (width - 3) / 9, 0.82, GROUND_H + 1.3, 0.08, 0.02, 1.0, grey)
        mb.cone(Matrix.Translation(F_.at(s0 + width / 2, -3.0, H + 4.0)), 10, 0.7, 0.2, 8.0, grey)              # the central spire
        for k in range(8):
            p = F_.at(s0 + 1.5 + k * (width - 3) / 7, -1.5 - (k % 3) * 1.4, H)
            mb.cone(Matrix.Translation(p + Vector((0, 0, 1.2))), 8, 0.35, 0.3, 2.4,
                    trencadis_mat('Trencadis_Guell%d' % (k % 3), [['#d9534f', '#f0ad4e', '#f2efe2'], ['#3a7bd5', '#5bc0de', '#f2efe2'], ['#5cb85c', '#f0c23b', '#f2efe2']][k % 3], 7 + k % 3))
    # cornice, plaque, and the door everyone walks in by (the middle bay)
    if g not in ('casa_calvet', 'casa_mila') and not mf:
        F_.box(mb, s0 + width / 2, 0.15, H - 0.12, width / 2 + 0.02, 0.18, 0.13, stone)
    # (round 33, the user: the door glowed on a bare wall, "the actual door should be glowing") a real door in each
    # front, shaped as Gaudí would — Batlló's in its bony arch, La Pedrera's rounded in the wave, Vicens's and Calvet's
    # square in a surround — and the glow on it, the same shape
    dw, dh, da, dd, dfr, ds = {
        'casa_batllo': (1.8, 2.6, 0.9, 0.0, mat('BoneStone', '#e8dcc4', 0.85), 0.0),
        'casa_mila': (2.0, 2.7, 0.7, -0.35, mat('PedreraStone', '#e9dfcb', 0.9), 0.0),
        'casa_vicens': (1.6, 2.5, 0.0, 0.0, mat('VicensTiles', '#ffffff', 0.4), 0.0),
        'casa_calvet': (1.6, 2.7, 0.0, 0.15, mat('CalvetStone', '#e8d6b4', 0.9), 0.0),     # (on the gable's piers' face)
        'palau_guell': (2.3, 3.3, 3.1, 0.0, None, 2.8)}[g]
    if mf and mf in MESHY_GAUDI_DOOR:
        # (round 41: the door in the middle stood through one of Meshy's bony columns) the way in where the real one
        # is, in the model's own doorway: its place across the front from the model's left, as Meshy painted it
        frac_, dw, dh = MESHY_GAUDI_DOOR[mf]
        rz_ = math.atan2(F_.N[1], F_.N[0]) + math.pi / 2
        ds = ds + (frac_ - 0.5) * width * Vector((math.cos(rz_), math.sin(rz_), 0)).dot(F_.U)
    if g != 'palau_guell':
        door_unit(mb, F_.at(s0 + width / 2 + ds, dd, KERB), F_.u, F_.n, dw, dh, da, M_WOOD_DOOR, dfr)
    if not mf:
        F_.box(mb, s0 + width / 2 + ds + dw / 2 + 0.9, 0.03, KERB + 1.6, 0.35, 0.015, 0.18, M_MARBLE)
    entrance_at(house['entrance'], F_, s0 + width / 2 + ds, dh, dw, arch=da, glow=F_.at(s0 + width / 2 + ds, dd + 0.1, 0))
    # (round 35, the second look: La Pedrera's waves and balconies, Batlló's masks and Güell's tribune stand up to 0.9 m
    # proud of the block's outline, where the camera stops, and it went inside them; the game's camera screen spans
    # the whole front, 1 m out: [its middle x, z, its width])
    ENTRANCES[-1]['screen'] = bl_m(F_.at(s0 + width / 2, 1.0 + (MESHY_GAUDI_GROUND.get(mf, 0.0) * width if mf else 0.0), 0)) + [round(width + 1.0, 2)]
    if mf:
        ENTRANCES[-1]['sign_out'] = 0.7                    # (round 41: its hanging sign clear of the Meshy stonework)
        if mf in MESHY_GAUDI_DOOR:
            ENTRANCES[-1]['sign_side'] = -1.0              # (its door at the end of its front: the sign on its own side)


# ------------------------------------------------------------------ whole-block landmarks

def landmark_sagrada(ox, oy, spec):
    """The Sagrada Família: the nave, its Nativity-style front with three portals, eight bell towers
    in two groups of four, and the tall central tower with its golden star. Unfinished: scaffolding
    and a crane."""
    mb = MB(uv=True)
    sandst = mat('SagradaStone', '#d6c4a0', 0.92)
    dark = mat('SagradaDark', '#8a7a62', 0.95)
    c = B(ox + BS / 2, oy + BS / 2, KERB)
    o = octagon(ox, oy)
    # the nave and the apse
    mb.box(c + Vector((0, 2.0, 9.0)), (1, 0), (0, 1), 7.5, 9.5, 9.0, sandst)
    mb.box(c + Vector((0, 2.0, 18.5)), (1, 0), (0, 1), 6.0, 8.5, 0.6, dark)
    for k in range(8):                                                  # buttress pinnacles along the nave
        for sx in (-1, 1):
            p = c + Vector((sx * 7.8, -6.0 + k * 2.4, 0))
            mb.cone(Matrix.Translation(p + Vector((0, 0, 10.0))), 6, 0.6, 0.15, 20.0, sandst)
    # the front: three portals with pointed arches, the main door in the middle
    front_y = -BS / 2 * T + 1.0
    for sx, w in ((-4.5, 1.6), (0, 2.4), (4.5, 1.6)):
        mb.box(c + Vector((sx, front_y + 0.4, 5.5)), (1, 0), (0, 1), w + 0.8, 0.8, 5.5, sandst)
        mb.box(c + Vector((sx, front_y - 0.02, 2.8)), (1, 0), (0, 1), w, 0.05, 2.8, mat('SagradaDoor', '#5a6a3a', 0.6))
        mb.cone(Matrix.Translation(c + Vector((sx, front_y + 0.4, 12.5))), 4, w + 1.2, 0.1, 3.0, sandst, smooth=False)
    # eight bell towers: tall, tapering, pierced, with coloured pinnacles
    for gy, xs in ((front_y + 2.0, (-6.5, -2.4, 2.4, 6.5)), (front_y + 20.0, (-6.0, -2.2, 2.2, 6.0))):
        for k, sx in enumerate(xs):
            hgt = 34.0 + (4.0 if k in (1, 2) else 0.0) + (-4.0 if gy > front_y + 10 else 0.0)
            p = c + Vector((sx, gy, 0))
            mb.cone(Matrix.Translation(p + Vector((0, 0, hgt / 2))), 12, 1.6, 0.6, hgt, sandst)
            for j in range(8):                                      # the spiral of openings
                a = j * 0.9
                mb.box(p + Vector((math.cos(a) * (1.45 - j * 0.1), math.sin(a) * (1.45 - j * 0.1), 6 + j * 3.4)), (math.cos(a), math.sin(a)),
                       (-math.sin(a), math.cos(a)), 0.05, 0.25, 0.9, dark)
            mb.sphere(Matrix.Translation(p + Vector((0, 0, hgt + 0.9))), 0.9, trencadis_mat('Trencadis_Sagrada', ['#c8322e', '#f0c23b', '#f2efe2', '#3a7a4a'], 11), (12, 8))
            mb.cone(Matrix.Translation(p + Vector((0, 0, hgt + 2.4))), 8, 0.25, 0.05, 1.6, M_GOLD)
    # the central tower (Jesus Christ), tallest, with the golden star the 2D game gives it
    mb.cone(Matrix.Translation(c + Vector((0, 4.0, 27.0))), 16, 3.6, 1.2, 54.0, sandst)
    for k in range(6):
        a = k * math.pi / 3
        mb.box(c + Vector((math.cos(a) * 1.5, 4.0 + math.sin(a) * 1.5, 56.0)), (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a)), 0.15, 1.6, 0.4, M_GOLD)
    mb.sphere(Matrix.Translation(c + Vector((0, 4.0, 56.0))), 1.0, M_GOLD, (12, 8))
    # scaffolding up one tower, and a tower crane
    sc = c + Vector((7.0, front_y + 20.0, 0))
    for k in range(10):
        for sx in (-2.2, 2.2):
            for sy in (-2.2, 2.2):
                mb.tube(sc + Vector((sx, sy, k * 3.0)), sc + Vector((sx, sy, k * 3.0 + 3.0)), 0.05, mat('Scaffold', '#c9c9c4', 0.5, 0.6), 4)
        mb.box(sc + Vector((0, 0, k * 3.0 + 3.0)), (1, 0), (0, 1), 2.3, 2.3, 0.05, M_WOODEN)
    cr = c + Vector((-9.5, 7.0, 0))
    yellow = mat('CraneYellow', '#f0c23b', 0.5, 0.3)
    mb.box(cr + Vector((0, 0, 30.0)), (1, 0), (0, 1), 0.6, 0.6, 30.0, yellow)
    mb.box(cr + Vector((6.0, 0, 60.5)), (1, 0), (0, 1), 14.0, 0.5, 0.5, yellow)
    mb.box(cr + Vector((-6.5, 0, 59.6)), (1, 0), (0, 1), 1.0, 1.0, 0.8, mat('Counterweight', '#7a7a76', 0.8))
    city_objs.append(mb.finish('Landmark_sagrada'))
    F_ = Frame((B(*o[4]).x, B(*o[4]).y), *edge_frame(o[4], o[5])[:2])
    entrance_at(spec, F_, edge_frame(o[4], o[5])[2] * T / 2, 5.0, 4.0)


def landmark_mnac(ox, oy, spec):
    """The Palau Nacional (MNAC): a grand palace with a central dome and four corner towers, on a terrace. Round 23 (the
    user: the door hovered on the pavement, a column stood in front of it and the steps couldn't be climbed): as on the
    real one, a broad flight of steps rises from the square to the terrace, and the way in is the great doorway in the
    middle of the columned front, under the dome. The steps and the terrace are walkable (scene['raised']); the palace
    and the terrace's sides are solid."""
    mb = MB(uv=True)
    stone = mat('MnacStone', '#e2d2b0', 0.9)
    roofm = mat('MnacDome', '#8a9a9a', 0.5, 0.4)
    c = B(ox + BS / 2, oy + BS / 2, KERB)
    TT, NST, RUN = 1.2, 8, 0.42                                                                # terrace height, steps
    TY0 = -8.0                                                                                 # the terrace's front edge
    mb.box(c + Vector((0, (TY0 + 12.0) / 2, TT / 2)), (1, 0), (0, 1), 13.0, (12.0 - TY0) / 2, TT / 2, stone)   # the terrace
    for sx in (-1, 1):                                                                         # its balustrade, either side of the steps
        for k in range(14):
            x = sx * (4.6 + k * 0.62)
            mb.cone(Matrix.Translation(c + Vector((x, TY0 + 0.15, TT + 0.35))), 8, 0.09, 0.07, 0.7, stone)
        mb.box(c + Vector((sx * 8.8, TY0 + 0.15, TT + 0.75)), (1, 0), (0, 1), 4.3, 0.18, 0.06, stone)
    raised = scene.setdefault('raised', [])
    for k in range(NST):                                                                       # the steps up to it
        top = TT * (NST - k) / NST
        y0, y1 = TY0 - k * RUN, TY0 - (k + 1) * RUN
        mb.box(c + Vector((0, (y0 + y1) / 2, top / 2)), (1, 0), (0, 1), 4.0, RUN / 2, top / 2, stone)
        a_, b_ = bl_m(c + Vector((-4.0, y0, 0))), bl_m(c + Vector((4.0, y1, 0)))
        raised.append([min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1]), round(KERB + top, 3)])
    a_, b_ = bl_m(c + Vector((-13.0, TY0, 0))), bl_m(c + Vector((13.0, -3.9, 0)))
    raised.append([min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1]), round(KERB + TT, 3)])
    mb.box(c + Vector((0, 3.0, TT + 6.0)), (1, 0), (0, 1), 12.0, 7.0, 6.0, stone)               # the palace
    for k in range(9):                                                                         # the colonnade, open in the middle
        if k == 4:
            continue
        mb.cone(Matrix.Translation(c + Vector((-8 + k * 2, -4.6, TT + 3.5))), 12, 0.4, 0.4, 7.0, stone)
    mb.box(c + Vector((0, -4.6, TT + 7.4)), (1, 0), (0, 1), 9.0, 0.6, 0.6, stone)
    mb.cone(Matrix.Translation(c + Vector((0, 3.0, TT + 14.0))), 24, 5.0, 5.0, 4.0, stone)       # the drum
    mb.sphere(Matrix.Translation(c + Vector((0, 3.0, TT + 16.0))) @ Matrix.Diagonal((1, 1, 0.8, 1)), 5.0, roofm, (24, 12))
    mb.cone(Matrix.Translation(c + Vector((0, 3.0, TT + 21.0))), 10, 0.8, 0.5, 2.0, stone)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = c + Vector((sx * 10.5, 3.0 + sy * 5.0, TT))
            mb.box(p + Vector((0, 0, 7.8)), (1, 0), (0, 1), 1.3, 1.3, 7.8, stone)
            mb.cone(Matrix.Translation(p + Vector((0, 0, 17.0))), 8, 1.4, 0.2, 3.0, roofm)
    for k in range(5):                                                                         # windows along the front
        for sx in (-1, 1):
            mb.box(c + Vector((sx * (3.5 + k * 1.6), -4.05, TT + 4.5)), (1, 0), (0, 1), 0.45, 0.05, 1.2, M_GLASS)
    # the great doorway: a deep stone surround, the wooden doors set back in it, a lunette over them
    mb.box(c + Vector((0, -4.08, TT + 1.9)), (1, 0), (0, 1), 1.75, 0.08, 1.9, stone)
    door_unit(mb, c + Vector((0, -4.16, TT)), (1, 0), (0, -1), 2.4, 3.0, 0.0, M_WOOD_DOOR, None)       # (round 33)
    mb.box(c + Vector((0, -4.13, TT + 3.45)), (1, 0), (0, 1), 1.1, 0.04, 0.2, M_GLASS)
    city_objs.append(mb.finish('Landmark_mnac'))
    # what can't be walked through: the palace, and the terrace's sides and front except the steps
    solids = []
    for (x0, y0, x1, y1) in ((-12.2, -4.05, 12.2, 12.0), (-13.0, TY0, -4.0, TY0 + 0.3), (4.0, TY0, 13.0, TY0 + 0.3),
                             (-13.3, TY0, -13.0, 12.0), (13.0, TY0, 13.3, 12.0)):
        a_, b_ = bl_m(c + Vector((x0, y0, 0))), bl_m(c + Vector((x1, y1, 0)))
        solids.append([[a_[0], a_[1]], [b_[0], a_[1]], [b_[0], b_[1]], [a_[0], b_[1]]])
    for blk in scene['blocks']:
        if blk['origin'] == [ox, oy]:
            blk['solids'] = solids
    o = octagon(ox, oy)
    u, n, L = edge_frame(o[4], o[5])
    door = c + Vector((0, -4.2, 0))
    F_ = Frame((door.x - u[0] * 1.2, door.y - u[1] * 1.2), u, n)
    entrance_at(spec, F_, 1.2, 3.0, 2.4, base=KERB + TT, glow=c + Vector((0, -4.27, 0)))


def landmark_ciutadella(ox, oy, spec):
    """The Parc de la Ciutadella: hedges, lawns and gravel walks (from the 2D tiles), and the Cascada:
    a monumental fountain with a triumphal arch and the golden Quadriga de l'Aurora on top."""
    mb = MB(uv=True)
    cards = Cards()
    hedge_m = mat('HedgeLeaves', '#3e6a34', 0.95)
    for Y in range(oy + OY, oy + OY + BS):
        for X in range(ox + OX, ox + OX + BS):
            k = tile(X, Y)
            q = [BT(X, Y, KERB + 0.02), BT(X + 1, Y, KERB + 0.02), BT(X + 1, Y + 1, KERB + 0.02), BT(X, Y + 1, KERB + 0.02)]
            if k == 'LAWN':
                mb.face(q, M_GRASS, normal=(0, 0, 1), uvscale=3.0)
            elif k == 'GRAVEL':
                mb.face(q, M_GRAVEL, normal=(0, 0, 1), uvscale=2.5)
            elif k == 'HEDGE':
                mb.face(q, M_GRAVEL, normal=(0, 0, 1), uvscale=2.5)
                # a soft, leafy hedge rather than a box: a dark core, hidden under a rounded coat of leaves that
                # runs on into the next hedge tile, so the rows read as one long clipped hedge
                mb.box(BT(X + 0.5, Y + 0.5, KERB + 0.32), (1, 0), (0, 1), T / 2 - 0.75, T / 2 - 0.75, 0.3, hedge_m)
                cards.shell(BT(X + 0.5, Y + 0.5, KERB + 0.55), (T / 2 + 0.1, T / 2 + 0.1, 0.62), 50, 0.95, M_SHRUB, nrng, (0.85, 1.0))
                cards.clump(BT(X + 0.5, Y + 0.5, KERB + 0.3), (T / 2 - 0.15, T / 2 - 0.15, 0.25), 16, 0.85, M_SHRUB, nrng)
                cards.clump(BT(X + 0.5, Y + 0.5, KERB + 0.8), (T / 2 - 0.45, T / 2 - 0.45, 0.3), 10, 0.8, M_SHRUB, nrng)
            elif k == 'FOUNT':
                mb.face(q, M_GRAVEL, normal=(0, 0, 1), uvscale=2.5)
    fx = [X for Y in range(MH2) for X in range(MW2) if tile(X, Y) == 'FOUNT']
    fy = [Y for Y in range(MH2) for X in range(MW2) if tile(X, Y) == 'FOUNT']
    x0, x1, y0, y1 = min(fx), max(fx) + 1, min(fy), max(fy) + 1
    c = BT((x0 + x1) / 2, (y0 + y1) / 2, KERB)
    w2, d2 = (x1 - x0) / 2 * T, (y1 - y0) / 2 * T
    stone = mat('CascadaStone', '#d9c8a6', 0.9)
    # the pool: the FOUNT tiles' rectangle, a low stone rim round water you can see
    water = mat('FountainWater', '#5f97a3', 0.05, 0.1)
    mb.face([BT(x0, y0, KERB + 0.3), BT(x1, y0, KERB + 0.3), BT(x1, y1, KERB + 0.3), BT(x0, y1, KERB + 0.3)], water, normal=(0, 0, 1),
            uvscale=2.0)
    for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
        mid = BT((ax + bx) / 2, (ay + by) / 2, KERB + 0.25)
        hx = max(abs(bx - ax) * T / 2, 0.2)
        hy = max(abs(by - ay) * T / 2, 0.2)
        mb.box(mid, (1, 0), (0, 1), hx + 0.2, hy + 0.2 if hy > 0.2 else 0.2, 0.25, stone)
    for k in range(4):                                                                                    # the cascade
        mb.box(c + Vector((0, d2 * 0.1 + k * 0.6, 1.0 + k * 0.9)), (1, 0), (0, 1), 3.0 - k * 0.3, 0.4, 0.5 + k * 0.45, stone)
        mb.box(c + Vector((0, d2 * 0.1 + k * 0.6 - 0.42, 1.2 + k * 0.9)), (1, 0), (0, 1), 2.6 - k * 0.3, 0.02, 0.4, mat('FountainWater', '#6f9fa8', 0.05, 0.1))
    arch_y = d2 * 0.75
    for sx in (-1, 1):
        mb.box(c + Vector((sx * 4.2, arch_y, 4.5)), (1, 0), (0, 1), 0.9, 0.9, 4.5, stone)
        mb.cone(Matrix.Translation(c + Vector((sx * 2.8, arch_y - 1.0, 3.5))), 10, 0.35, 0.35, 7.0, stone)
    mb.box(c + Vector((0, arch_y, 9.6)), (1, 0), (0, 1), 5.2, 1.0, 0.7, stone)
    mb.box(c + Vector((0, arch_y, 10.9)), (1, 0), (0, 1), 1.8, 0.8, 0.6, M_GOLD)                           # the Quadriga
    for k in range(4):
        mb.box(c + Vector((-1.2 + k * 0.8, arch_y - 0.6, 11.6)), (0, 1), (1, 0), 0.6, 0.15, 0.35, M_GOLD)
    city_objs.append(mb.finish('Landmark_ciutadella'))
    city_objs.append(cards.finish('Plants_ciutadella'))
    # a few trees on the lawns, benches by the walks
    for (X, Y) in ((69.5, 63.5), (75.5, 63.5), (69.5, 60.5), (75.5, 60.5)):
        if tile(int(X), int(Y)) == 'LAWN':
            plane_tree(X - OX, Y - OY)
    for blk in scene['blocks']:
        if blk['origin'] == [ox, oy]:
            blk['solids'] = []                                                                             # walk in


def landmark_upf(ox, oy, spec):
    """Universitat Pompeu Fabra: the Ciutadella campus's old brick-and-stone buildings round the whole
    block, a grand entrance in the middle of the south side with the university's name over it."""
    rng = random.Random(4242)
    houses = {}
    for i in range(8):
        bays = 3 if i % 2 else 5
        houses[i] = [dict(bays=bays, uppers=4, facade='#b9694e', style='classic', shutter=3, num=100 + i, trim='#d9ccb2',
                          balc=['long', 'iron', 'iron', 'box'], ground=['window'] * bays, shop=None,
                          plants=['none', 'none', 'herbs'], seed=900 + i, tribuna=[])]
    houses[4][0]['ground'] = ['window', 'window', 'grand', 'window', 'window']
    houses[4][0]['entrance'] = spec
    houses[4][0]['sign'] = 'UNIVERSITAT POMPEU FABRA'
    build_kit_block(ox, oy, houses)
    # one institution, not a row of houses: a clock tower over the grand entrance, and the senyera flying
    o = octagon(ox, oy)
    u, n, L = edge_frame(o[4], o[5])
    F_ = Frame((B(*o[4]).x, B(*o[4]).y), u, n)
    mb = MB(uv=True)
    brick = mat('UpfBrick', '#b9694e', 0.9)
    stone = mat('UpfStone', '#e3d6bd', 0.85)
    H = GROUND_H + 4 * FLOOR_H
    mid = L * T / 2
    F_.box(mb, mid, -0.9, H + 0.9, 4.2, 0.9, 0.9, stone)                                   # the pediment over the entrance bays
    city_objs.append(text_obj('UNIVERSITAT POMPEU FABRA', 0.42, mat('UpfLetters', '#7a3b26', 0.6), F_.at(mid, 0.03, H + 0.7),
                              F_.rot, 'KitText_upf'))
    F_.box(mb, mid, -2.2, H + 4.0, 2.0, 2.0, 4.0, brick)                                   # the tower
    for z in (H + 0.3, H + 8.0):
        F_.box(mb, mid, -2.2, z, 2.15, 2.15, 0.15, stone)                                  # its cornices
    F_.box(mb, mid, -0.17, H + 5.6, 1.15, 0.04, 1.15, M_WHITE)                             # the clock
    F_.box(mb, mid, -0.12, H + 5.95, 0.06, 0.03, 0.4, M_IRON)                              # (ten past ten)
    F_.box(mb, mid + 0.3, -0.12, H + 5.65, 0.3, 0.03, 0.05, M_IRON)
    mb.cone(Matrix.Translation(F_.at(mid, -2.2, H + 9.6)) @ Matrix.Rotation(math.pi / 4, 4, 'Z'), 4, 2.9, 0.1, 3.0,
            mat('UpfRoof', '#5a6668', 0.6, 0.3), smooth=False)                             # the pyramid roof
    top = F_.at(mid, -2.2, H + 11.1)
    mb.tube(top, top + Vector((0, 0, 3.2)), 0.05, M_IRON, 5)                               # the flagpole
    for k in range(9):                                                                     # the senyera: four red bars on gold
        mb.box(top + Vector((0, 0, 3.1 - k * 0.1)) + F_.U * 0.75, u, n, 0.7, 0.02, 0.05, M_RED if k % 2 else M_GOLD)
    city_objs.append(mb.finish('Landmark_upf'))


def build_special_block(ox, oy, specs):
    """Returns True if it built the whole block (a landmark)."""
    for sp in specs:
        if sp.get('size') == 'block':
            {'sagrada': landmark_sagrada, 'mnac': landmark_mnac, 'ciutadella': landmark_ciutadella, 'upf': landmark_upf}[sp['id']](ox, oy, sp)
            if sp['id'] != 'upf':
                OPEN_BLOCKS.add((ox, oy))          # no corner houses: the street plaques go on posts
            else:
                RELIEF_BLOCKS.add((ox, oy))        # a deep-relief front: the plaques stand out from it
            return True
    return False


# the Sagrada Família, rebuilt facing the way the real one does (sagrada.py replaces landmark_sagrada above)
exec(open(os.path.join(BUILD, 'sagrada.py')).read())
# the university, as one institution round its block (upf.py replaces landmark_upf above)
exec(open(os.path.join(BUILD, 'upf.py')).read())
