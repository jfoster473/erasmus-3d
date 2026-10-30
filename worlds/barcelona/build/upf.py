# Universitat Pompeu Fabra, its Ciutadella campus: one institution round the whole block, not a row of
# flats. The old barracks' red brick in long, even ranges, stone pilasters between the bays, tall arched
# windows on the ground floor and plain ones above, a stone cornice and parapet; inside, a quiet green
# quad with trees. In the middle of the side the door is on (Carrer de Girona, facing the Ciutadella
# park across it) a taller entrance pavilion: four stone columns, the university's name across the
# frieze, a pediment with its clock, the flags on the roof, red UPF banners either side, wide low steps.
# (Round 19: no quad any more: it couldn't be reached and only showed on the map. A glass rooflight instead.)
# Exec'd from landmarks.py (it replaces the old landmark_upf), sharing its helpers.

def brick_fn(x, y):
    row = y // 8
    off = 8 if row % 2 else 0
    mortar = y % 8 == 0 or (x + off) % 16 == 0
    k = 1.0 + 0.08 * math.sin(x * 1.7 + row * 3.1) + 0.05 * math.sin(row * 7.3)
    if mortar:
        return (0.82, 0.76, 0.68)
    return (0.66 * k, 0.33 * k, 0.24 * k)


def landmark_upf(ox, oy, spec):
    rng = random.Random(1990)
    mb = MB(uv=True)
    fine = MB(uv=True)
    brick = mat('UpfBrickTex', '#ffffff', 0.9, image=make_image('upf_brick', 64, 64, brick_fn))
    stone = mat('UpfStone', '#e9dfca', 0.85)
    glass = mat('UpfGlass', '#3a4a58', 0.15)
    frame_m = mat('UpfFrame', '#f2ede2', 0.6)
    roof_m = mat('UpfRoof', '#8a8580', 0.9)
    door_m = mat('UpfDoor', '#5a3424', 0.6)
    red = mat('UpfRed', '#c8102e', 0.7)
    outer, inner = octagon(ox, oy), octagon(ox, oy, -COURT)
    H = GROUND_H + 3 * FLOOR_H                     # three storeys over a tall ground floor
    face_edge = {'N': 0, 'E': 2, 'S': 4, 'W': 6}[spec.get('face', 'S')]

    def arch_window(F_, s, z0, w, h, d=0.0):
        """A round-headed window: a stone surround, then the glass."""
        for (m, grow, dd) in ((stone, 0.14, 0.02), (glass, 0.0, 0.035)):
            r = w / 2 + grow
            pts = [F_.at(s - r, d + dd, z0 - grow), F_.at(s + r, d + dd, z0 - grow)]
            for k in range(9):
                a = math.pi * k / 8
                pts.append(F_.at(s + math.cos(a) * r, d + dd, z0 + h - w / 2 + math.sin(a) * r))
            mb.face(pts, m, normal=tuple(F_.N))
        F_.box(fine, s, d + 0.05, z0 + (h - w / 2) / 2, 0.025, 0.02, (h - w / 2) / 2, frame_m)          # glazing bars
        F_.box(fine, s, d + 0.05, z0 + h * 0.55, w / 2, 0.02, 0.025, frame_m)

    def plain_window(F_, s, z0, w, h, d=0.0):
        F_.box(mb, s, d + 0.02, z0 + h / 2, w / 2 + 0.12, 0.02, h / 2 + 0.12, stone)
        F_.box(mb, s, d + 0.035, z0 + h / 2, w / 2, 0.02, h / 2, glass)
        F_.box(fine, s, d + 0.05, z0 + h / 2, 0.025, 0.02, h / 2, frame_m)
        F_.box(fine, s, d + 0.05, z0 + h * 0.62, w / 2, 0.02, 0.025, frame_m)
        F_.box(mb, s, d + 0.12, z0 - 0.08, w / 2 + 0.2, 0.12, 0.06, stone)                              # the sill
        F_.box(mb, s, d + 0.08, z0 + h + 0.2, w / 2 + 0.2, 0.08, 0.1, stone)                            # the lintel

    for i in range(8):
        o0, o1 = outer[i], outer[(i + 1) % 8]
        u, n, Lt = edge_frame(o0, o1)
        L = Lt * T
        F_ = Frame((B(*o0).x, B(*o0).y), u, n)
        main_side = i == face_edge
        # the wall, its stone plinth, string course, cornice and parapet
        mb.face([F_.at(0, 0, 0), F_.at(L, 0, 0), F_.at(L, 0, H), F_.at(0, 0, H)], brick, normal=tuple(F_.N), uvscale=2.0)
        F_.box(mb, L / 2, 0.06, 0.55, L / 2, 0.06, 0.55, stone)
        F_.box(mb, L / 2, 0.08, GROUND_H + 0.05, L / 2, 0.08, 0.1, stone)
        F_.box(mb, L / 2, 0.18, H + 0.15, L / 2 + 0.1, 0.22, 0.15, stone)
        F_.box(mb, L / 2, 0.05, H + 0.75, L / 2, 0.08, 0.45, brick)
        F_.box(mb, L / 2, 0.08, H + 1.25, L / 2 + 0.05, 0.12, 0.06, stone)
        bays = max(2, int(round(L / 3.3)))
        bw = L / bays
        mid0, mid1 = L / 2 - 4.6, L / 2 + 4.6                            # (the entrance pavilion's stretch)
        for b in range(bays + 1):                                        # stone pilasters between the bays
            s = b * bw
            if main_side and mid0 - 0.3 < s < mid1 + 0.3:
                continue
            F_.box(mb, s, 0.1, H / 2, 0.22, 0.1, H / 2, stone)
        for b in range(bays):
            s = (b + 0.5) * bw
            if main_side and mid0 < s < mid1:
                continue
            arch_window(F_, s, 0.9, 1.25, GROUND_H - 1.25)
            for f in range(3):
                plain_window(F_, s, GROUND_H + 0.6 + f * FLOOR_H, 1.05, 1.55)
        # the roof: over the whole block (round 19: the quad that couldn't be reached is roofed over, so the
        # map and the street agree; a glass rooflight lights the hall under it)
        mb.face([B(*o0, H + 0.01), B(*o1, H + 0.01), B(ox + BS / 2, oy + BS / 2, H + 0.01)], roof_m, normal=(0, 0, 1), uvscale=3.0)
        if not main_side:
            continue
        # ------------------------------------------------ the entrance pavilion
        m = L / 2
        HP = H + 3.4
        F_.box(mb, m, 0.35, HP / 2, 4.6, 0.35, HP / 2, stone)                                     # its stone front
        for f in range(3):                                                                        # windows above the portico
            for k in (-1, 1):
                plain_window(F_, m + k * 2.6, GROUND_H + 0.6 + f * FLOOR_H, 1.0, 1.5, 0.7)
        plain_window(F_, m, GROUND_H + 0.6 + FLOOR_H, 1.4, 1.8, 0.7)
        for k in (-3.4, -1.25, 1.25, 3.4):                                                         # the four columns
            p = F_.at(m + k, 1.15, 0)
            mb.cone(Matrix.Translation(p + Vector((0, 0, 0.25))), 12, 0.48, 0.48, 0.5, stone)
            mb.cone(Matrix.Translation(p + Vector((0, 0, (GROUND_H + 1.0) / 2 + 0.5))), 16, 0.32, 0.28, GROUND_H + 1.0, stone)
            mb.box(p + Vector((0, 0, GROUND_H + 1.65)), u, n, 0.45, 0.45, 0.15, stone)
            scene['obstacles'].append({'pos': bl_m(p), 'off': [0, 0], 'r': 0.45})
        F_.box(mb, m, 1.0, GROUND_H + 2.15, 4.2, 0.6, 0.35, stone)                                  # the entablature
        city_objs.append(text_obj('UNIVERSITAT POMPEU FABRA', 0.36, mat('UpfLetters', '#7a2e22', 0.6), F_.at(m, 1.61, GROUND_H + 2.15),
                                  F_.rot, 'KitText_upf'))
        # the pediment, with the clock in it
        tri = [F_.at(m - 4.8, 0.72, HP), F_.at(m + 4.8, 0.72, HP), F_.at(m, 0.72, HP + 2.6)]
        mb.face(tri, stone, normal=tuple(F_.N))
        for (a, b2) in ((tri[0], tri[2]), (tri[2], tri[1])):
            mb.face([a, b2, b2 - F_.N * 0.72, a - F_.N * 0.72], roof_m, normal=(0, 0, 1))
        F_.box(mb, m, 0.36, HP - 0.1, 4.8, 0.36, 0.12, stone)
        F_.box(mb, m, 0.74, HP + 0.95, 0.66, 0.03, 0.66, stone)
        F_.box(mb, m, 0.77, HP + 0.95, 0.58, 0.02, 0.58, M_WHITE)                                  # the clock
        F_.box(fine, m, 0.8, HP + 1.1, 0.03, 0.02, 0.32, M_IRON)                                   # (ten past ten)
        F_.box(fine, m + 0.17, 0.8, HP + 1.02, 0.22, 0.02, 0.03, M_IRON)
        # the doors: tall, round-headed, panelled
        arch_window(F_, m, 0.15, 2.3, 3.6, 0.7)
        F_.box(mb, m, 0.76, 1.75, 1.1, 0.03, 1.6, door_m)
        F_.box(fine, m, 0.8, 1.75, 0.02, 0.02, 1.6, M_GOLD)
        # the steps (round 20d: they were the wrong way round, the outer one the tallest, a knee-high ledge she
        # walked through): two low steps up from the pavement to a landing the columns stand on, each a
        # little narrower than the one below; the game lifts her onto them (scene['raised'])
        for (d0, d1, hw, top) in ((0.7, 1.75, 4.2, KERB + 0.18), (1.75, 2.1, 4.4, KERB + 0.12), (2.1, 2.45, 4.6, KERB + 0.06)):
            F_.box(mb, m, (d0 + d1) / 2, top / 2, hw, (d1 - d0) / 2, top / 2, stone)
            a_, b_ = bl_m(F_.at(m - hw, d0, 0)), bl_m(F_.at(m + hw, d1, 0))
            scene.setdefault('raised', []).append([min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1]), round(top, 3)])
        # red banners down the front, either side
        for k in (-5.4, 5.4):
            F_.box(fine, m + k, 0.12, GROUND_H + FLOOR_H * 1.5, 0.55, 0.02, FLOOR_H * 1.3, red)
            city_objs.append(text_obj('UPF', 0.55, mat('BannerText', '#ffffff', 0.7), F_.at(m + k, 0.15, GROUND_H + FLOOR_H * 2.1),
                                      F_.rot, 'KitText_upf_banner_%d' % (k > 0)))
        # the flags on the roof: the senyera, Europe, the university's own
        for k, (cols, stars) in enumerate(((['#f0c23b', '#c8322e'] * 4 + ['#f0c23b'], False), (['#2c4fa0'], True), (['#c8102e'], False))):
            pole = F_.at(m - 2.0 + k * 2.0, 0.4, HP + 2.7 if k == 1 else HP)
            fine.tube(pole, pole + Vector((0, 0, 3.4)), 0.04, M_IRON, 5)
            fl = pole + Vector((0, 0, 2.9)) + F_.U * 0.65
            for j, col in enumerate(cols):
                hz = 0.38 / len(cols)
                fine.box(fl + Vector((0, 0, 0.38 - (2 * j + 1) * hz)), u, n, 0.6, 0.015, hz, mat('Flag' + col, col, 0.8))
            if stars:
                for j in range(12):
                    a = 2 * math.pi * j / 12
                    fine.box(fl + F_.U * (math.cos(a) * 0.24) + Vector((0, 0, math.sin(a) * 0.24)) + F_.N * 0.02, u, n, 0.03, 0.01, 0.03, M_GOLD)
        # a modern sign by the steps
        sp = F_.at(m + 6.6, 1.3, 0)
        fine.box(sp + Vector((0, 0, 0.9)), u, n, 0.5, 0.1, 0.9, red)
        city_objs.append(text_obj('UPF', 0.3, mat('BannerText', '#ffffff', 0.7), sp + F_.N * 0.11 + Vector((0, 0, 1.45)), F_.rot, 'KitText_upf_sign'))
        city_objs.append(text_obj('Campus de la Ciutadella', 0.075, mat('BannerText', '#ffffff', 0.7), sp + F_.N * 0.11 + Vector((0, 0, 1.15)),
                                  F_.rot, 'KitText_upf_sign2'))
        # under the logo, a small cream plaque set into the red (read with E)
        F_.box(fine, m + 6.6, 1.3 + 0.1, 0.72, 0.34, 0.012, 0.24, mat('SignFace', '#f4ead2', 0.7))
        for j, (ln, sz) in enumerate((('UNIVERSITAT', 0.06), ('POMPEU FABRA', 0.06), ('Facultat d\'Economia', 0.04), ('Visites: consergeria', 0.04))):
            city_objs.append(text_obj(ln, sz, mat('SignInk', '#22385a', 0.5), sp + F_.N * 0.115 + Vector((0, 0, 0.86 - j * 0.085 - (0.01 if j > 1 else 0))),
                                      F_.rot, 'KitText_upf_plaque%d' % j))
        scene.setdefault('things2d', []).append({'type': 'sign', 'pos': bl_m(sp + F_.N * 0.75), 'id': '', 'h': 0.12, 'landmark': '',
                                  'text': "UNIVERSITAT POMPEU FABRA — Campus de la Ciutadella. A public university founded in 1990. "
                                          "Its campus here took over the old barracks of the Ciutadella and the great brick water "
                                          "reservoir of 1874, which is now the library. Economics, business, politics and law are taught "
                                          "here. Visitors are welcome: ask at the porter's lodge inside the main door."})
        scene['obstacles'].append({'pos': bl_m(sp), 'off': [0, 0], 'r': 0.6})
        keep_clear(F_.at(m, 2.5, 0), 6.0)
        for k in (-4.0, -2.5, 2.5, 4.0):                                                             # (the pavilion is solid)
            scene['obstacles'].append({'pos': bl_m(F_.at(m + k, 0.3, 0)), 'off': [0, 0], 'r': 0.7})
        Fd = Frame((F_.at(0, 0.7, 0).x, F_.at(0, 0.7, 0).y), u, n)                                  # the doors, in the pavilion's face
        entrance_at(spec, Fd, m, 3.2, 2.2)
    # where the quad was: a long glass rooflight on a low brick upstand, ridged, with iron glazing bars
    cq = B(ox + BS / 2, oy + BS / 2, H)
    qr = (BS / 2 - COURT) * T - 1.0
    mb.box(cq + Vector((0, 0, 0.3)), (1, 0), (0, 1), qr, qr * 0.55, 0.3, brick)
    rl = mat('UpfRooflight', '#9fb4c0', 0.12, 0.3)
    for sgn in (-1, 1):
        mb.face([cq + Vector((-qr + 0.2, sgn * (qr * 0.55 - 0.2), 0.6)), cq + Vector((qr - 0.2, sgn * (qr * 0.55 - 0.2), 0.6)),
                 cq + Vector((qr - 0.2, 0, 1.8)), cq + Vector((-qr + 0.2, 0, 1.8))], rl, normal=(0, sgn, 1))
        for j in range(int(qr * 2 / 1.2) + 1):
            x = -qr + 0.2 + j * (2 * qr - 0.4) / int(qr * 2 / 1.2)
            fine.tube(cq + Vector((x, sgn * (qr * 0.55 - 0.2), 0.62)), cq + Vector((x, 0, 1.82)), 0.03, M_IRON, 4)
    for sgn in (-1, 1):
        mb.face([cq + Vector((sgn * (qr - 0.2), -(qr * 0.55 - 0.2), 0.6)), cq + Vector((sgn * (qr - 0.2), qr * 0.55 - 0.2, 0.6)),
                 cq + Vector((sgn * (qr - 0.2), 0, 1.8))], rl, normal=(sgn, 0, 0))
    city_objs.append(mb.finish('Landmark_upf'))
    city_objs.append(fine.finish('Detail_upf'))
