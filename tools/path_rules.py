"""Measure the hill path and Park Güell's paths against docs/PATH_RULES.md, on the world as built (round 35).

  python3 tools/path_rules.py [breaches.json]

Reads bigfiles/built/barcelona/scene.json (the ground grid the game walks, the paths, railings, solids, flats) and
north.py (the path's heights and sides). Prints each breach with its rule and place; writes them to the json for
tools/plan_maps.py to ring on the maps. What can't be measured (looks) is for the pictures.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'worlds', 'barcelona', 'build'))
import north as N                                                           # noqa: E402

SC = json.load(open(os.path.join(HERE, '..', 'bigfiles', 'built', 'barcelona', 'scene.json')))
T = SC['terrain']
NO = SC['north']
OUT = []


TFS = SC.get('terrain_fine', [])


def gz(x, z):
    """The ground as built (the grid the game walks, the finer one along the hill path where it has one), bilinear."""
    for TF in TFS:
        fi, fj = (x - TF['x0']) / TF['step'], (z - TF['z0']) / TF['step']
        if 0 <= fi < TF['nx'] - 1 and 0 <= fj < TF['nz'] - 1:
            i, j = int(fi), int(fj)
            a, b = fi - i, fj - j
            H = TF['h']
            return (H[j][i] * (1 - a) + H[j][i + 1] * a) * (1 - b) + (H[j + 1][i] * (1 - a) + H[j + 1][i + 1] * a) * b
    fi, fj = (x - T['x0']) / T['step'], (z - T['z0']) / T['step']
    i, j = int(math.floor(fi)), int(math.floor(fj))
    a, b = fi - i, fj - j
    H = T['h']
    return (H[j][i] * (1 - a) + H[j][i + 1] * a) * (1 - b) + (H[j + 1][i] * (1 - a) + H[j + 1][i + 1] * a) * b


def breach(rule, x, z, text):
    OUT.append({'rule': rule, 'x': round(x, 1), 'z': round(z, 1), 'text': text})


def seg_d(px, pz, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dz * dz or 1e-9
    t = max(0.0, min(1.0, ((px - a[0]) * dx + (pz - a[1]) * dz) / L2))
    return math.hypot(px - a[0] - dx * t, pz - a[1] - dz * t)


def line_d(px, pz, line):
    return min(seg_d(px, pz, a, b) for a, b in zip(line, line[1:]))


def poly_d(px, pz, poly):
    return min(seg_d(px, pz, a, b) for a, b in zip(poly, poly[1:] + poly[:1]))


def in_poly(px, pz, poly):
    ins = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, zi, xj, zj = poly[i][0], poly[i][1], poly[j][0], poly[j][1]
        if (zi > pz) != (zj > pz) and px < (xj - xi) * (pz - zi) / ((zj - zi) or 1e-9) + xi:
            ins = not ins
        j = i
    return ins


# ------------------------------------------------------------------ the hill path
pts, _ = N.path_points()
HALF = 1.1                                   # the drawn track's half width (the core and its frayed edge)


def normal(i):
    a, b = pts[max(0, i - 2)], pts[min(len(pts) - 1, i + 2)]
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    return -(b[1] - a[1]) / L, (b[0] - a[0]) / L


def turn(i, d=6):
    a, b, c = pts[max(0, i - d)], pts[i], pts[min(len(pts) - 1, i + d)]
    t1 = (b[0] - a[0], b[1] - a[1])
    t2 = (c[0] - b[0], c[1] - b[1])
    l1, l2 = math.hypot(*t1) or 1, math.hypot(*t2) or 1
    return math.acos(max(-1, min(1, (t1[0] * t2[0] + t1[1] * t2[1]) / (l1 * l2))))


def other_leg_near(i, R=9.0):
    x, z, _ = pts[i]
    return any(math.hypot(p[0] - x, p[1] - z) < R for k, p in enumerate(pts) if abs(k - i) > 25)


benches = N.bench_spots()
fair = N.FAIR
for i in range(2, len(pts) - 2):
    x, z, h = pts[i]
    if fair[0] - 1 < x < fair[2] + 1 and fair[1] - 1 < z < fair[3] + 1:
        continue
    nx, nz = normal(i)
    # A4 level across: the two edges of the track within 0.15 m of each other (the user: "relaxed slightly")
    hl, hr = gz(x + nx * HALF, z + nz * HALF), gz(x - nx * HALF, z - nz * HALF)
    if abs(hl - hr) > 0.15 and i % 3 == 0:
        breach('A4', x, z, 'hill path %.0f%% along: one edge %.2f m above the other' % (100 * i / len(pts), abs(hl - hr)))
    # A4 on the path, not in a trench or on a dyke: its middle within 0.15 m of the path's own level
    if abs(gz(x, z) - h) > 0.25 and i % 3 == 0:
        breach('A4', x, z, 'hill path: ground %.2f m off the path\'s level' % (gz(x, z) - h))
    # C3 the uphill side: a narrow green edge, then a bank she can't walk up
    if i % 4 == 0 and h > 2.5 and turn(i) < 0.5 and not other_leg_near(i, 7.0) and \
            all(math.hypot(b[0] - x, b[1] - z) > 4.0 for b in benches):
        us = N.up_side(i)
        if us:
            ux, uz = nx * us, nz * us
            g0 = gz(x + ux * 1.2, z + uz * 1.2)
            edge_rise = gz(x + ux * 2.0, z + uz * 2.0) - g0
            bank = (gz(x + ux * 4.0, z + uz * 4.0) - gz(x + ux * 2.0, z + uz * 2.0)) / 2.0
            if edge_rise > 0.35:
                breach('C3', x, z, 'uphill green edge rises %.2f m in 0.8 m' % edge_rise)
            if bank < 0.33:
                breach('C3', x, z, 'uphill bank only %.2f a metre (she could walk up it)' % bank)
            if gz(x + ux * 6.0, z + uz * 6.0) < gz(x + ux * 4.0, z + uz * 4.0) - 0.3:
                breach('C3', x, z, 'the ground falls again behind the uphill bank (a ridge)')

# A7 smooth to the eye: every quarter metre along the middle and both edges, the ground against the smooth climb
# (the path's own heights, interpolated along it) — no ripple over 3 cm
_sl = [0.0]
for a_, b_ in zip(pts, pts[1:]):
    _sl.append(_sl[-1] + math.hypot(b_[0] - a_[0], b_[1] - a_[1]))
A7_WORST = [0.0]
for i in range(3, len(pts) - 4):
    a_, b_ = pts[i], pts[i + 1]
    if fair[0] - 1 < a_[0] < fair[2] + 1 and fair[1] - 1 < a_[1] < fair[3] + 1:
        continue
    nx, nz = normal(i)
    L_ = _sl[i + 1] - _sl[i]
    for k_ in range(max(1, int(L_ / 0.25))):
        t_ = k_ * 0.25 / L_
        x = a_[0] + (b_[0] - a_[0]) * t_
        z = a_[1] + (b_[1] - a_[1]) * t_
        h = a_[2] + (b_[2] - a_[2]) * t_
        for off in (-0.9, 0.0, 0.9):
            dv = gz(x + nx * off, z + nz * off) - h
            if off == 0.0:
                A7_WORST[0] = max(A7_WORST[0], abs(dv))
            if abs(dv) > 0.03 and k_ == 0 and abs(off) < 0.5:
                breach('A7', x, z, 'hill path %.0f%% along: the ground %+.2f m off the smooth climb (%.1f m %s)' % (
                    100 * i / len(pts), dv, abs(off), 'from the middle' if off else 'in the middle'))
print('A7 worst along the middle: %.3f m' % A7_WORST[0])

# ------------------------------------------------------------------ the railings
rails = NO['rails']
runs, cur = [], []
for r in rails:
    if cur and math.hypot(cur[-1][2] - r[0], cur[-1][3] - r[1]) < 0.01:
        cur.append(r)
    else:
        if cur:
            runs.append(cur)
        cur = [r]
if cur:
    runs.append(cur)


def nearest_i(x, z):
    return min(range(len(pts)), key=lambda k: (pts[k][0] - x) ** 2 + (pts[k][1] - z) ** 2)


print('railing runs: %d' % len(runs))
for ri, run in enumerate(runs):
    posts = [(run[0][0], run[0][1])] + [(r[2], r[3]) for r in run]
    if len(posts) < 6:
        breach('D5', posts[0][0], posts[0][1], 'a run of only %d posts' % len(posts))
    for (a, b) in zip(posts, posts[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 1.9:
            breach('D5', a[0], a[1], 'posts %.1f m apart' % math.hypot(b[0] - a[0], b[1] - a[1]))
    for k in range(1, len(posts) - 1):
        a, b, c = posts[k - 1], posts[k], posts[k + 1]
        t1, t2 = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*t1) or 1, math.hypot(*t2) or 1
        ang = math.degrees(math.acos(max(-1, min(1, (t1[0] * t2[0] + t1[1] * t2[1]) / (l1 * l2)))))
        if ang > 40:
            breach('D4', b[0], b[1], 'the railing turns %.0f degrees at one post' % ang)
    for k, (px, pz) in enumerate(posts):
        i = nearest_i(px, pz)
        d = math.hypot(px - pts[i][0], pz - pts[i][1])
        if d > 1.6:
            continue                         # (an end turning off to its bank: D2/D3, judged at its end below)
        x, z, h = pts[i]
        ox, oz = (px - x) / (d or 1), (pz - z) / (d or 1)
        us = N.up_side(i)
        nx, nz = normal(i)
        if us and (ox * nx + oz * nz) * us > 0.5 and h > 2.5:
            breach('D1', px, pz, 'a post on the uphill side')
        drop = h - min(gz(x + ox * 3.5, z + oz * 3.5), gz(x + ox * 4.5, z + oz * 4.5))
        if drop < 0.6 and k % 2 == 0:
            breach('D1', px, pz, 'beside gentle ground (only %.2f m down within 4.5 m)' % drop)
        if abs(px - N.FUNI_BEND[0]) < 1.2 and -204.5 < pz < -191.0:
            breach('D6', px, pz, 'a post doubling the funicular\'s white fence')
        if h < 2.4:
            breach('D6', px, pz, 'a post at the hill\'s foot')
    for end in (posts[0], posts[-1]):
        # D2/D3/D5 every end against a bank she can't climb (or a wall): the ground rising steeply within 1 m of it
        rise = max((gz(end[0] + math.cos(a_) * 1.0, end[1] + math.sin(a_) * 1.0) - gz(*end)) for a_ in
                   [k * math.pi / 8 for k in range(16)])
        i = nearest_i(*end)
        x, z, h = pts[i]
        dd = math.hypot(end[0] - x, end[1] - z) or 1.0
        ox, oz = (end[0] - x) / dd, (end[1] - z) / dd
        drop = h - min(gz(x + ox * 3.5, z + oz * 3.5), gz(x + ox * 4.5, z + oz * 4.5))
        by_wall = any(poly_d(end[0], end[1], poly) < 1.0 for poly in SC['solids']
                      if abs(poly[0][0] - end[0]) < 60 and abs(poly[0][1] - end[1]) < 60)
        tn = max(turn(k_, 10) for k_ in range(max(0, i - 12), min(len(pts) - 1, i + 12)))
        glade = (-197.0 < end[0] < -146.0 and end[1] < -270.0) or h < 3.0          # (E3; D6: the foot)
        below = any(min(math.hypot(p[0] - end[0] - ox * r_, p[1] - end[1] - oz * r_) for r_ in (4, 8, 12)) < 4.0 and p[2] < h - 0.5
                    for kk, p in enumerate(pts) if abs(kk - i) > 25)                     # (H3: a leg just below)
        by_wall = by_wall or any(b[0] - 1 <= end[0] <= b[2] + 1 and b[1] - 1 <= end[1] <= b[3] + 1 for b in SC['blocked'])
        tn = max(tn, 1.0 if below else 0.0)
        if rise < 0.3 and not by_wall and not (dd < 1.7 and drop < 0.5):
            if tn > 0.6 or glade:
                print('   (an end at the inside of a bend or the glade, open by D3/E3: (%.1f, %.1f), drop %.2f)' % (end[0], end[1], drop))
            else:
                breach('D5', end[0], end[1], 'a railing end with a drop past it (%.2f m) and no bank or wall to end against' % drop)
# D1 never fences on both sides of the path
for i in range(0, len(pts), 3):
    x, z, h = pts[i]
    nx, nz = normal(i)
    sides = set()
    for r in rails:
        for (px, pz) in ((r[0], r[1]), (r[2], r[3])):
            if abs(px - x) < 2.5 and abs(pz - z) < 2.5 and math.hypot(px - x, pz - z) < 2.0:
                sides.add(1 if (px - x) * nx + (pz - z) * nz > 0 else -1)
    if len(sides) == 2:
        breach('D1', x, z, 'fences on both sides of the path')
# A5 nothing on the track
for poly in SC['solids']:
    for (px, pz) in poly:
        i = nearest_i(px, pz) if -240 < px < -40 and -300 < pz < -95 else None
        if i is not None and math.hypot(px - pts[i][0], pz - pts[i][1]) < HALF - 0.1:
            breach('A5', px, pz, 'something solid on the hill path')
            break

# ------------------------------------------------------------------ Park Güell
PP = N.PARK_PATHS
G = N.GUELL
flats = SC['flats']
for k, P in enumerate(PP):
    lab = 'park path %d' % (k + 1)
    dense = []
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / 1.0))
        dense += [(a[0] + (b[0] - a[0]) * t / n, a[1] + (b[1] - a[1]) * t / n, (b[0] - a[0]) / L, (b[1] - a[1]) / L) for t in range(n)]
    ends_on = [any(line_d(e[0], e[1], Q) < 1.0 for q, Q in enumerate(PP) if q != k) for e in (P[0], P[-1])]
    for j, (x, z, dx, dz) in enumerate(dense):
        nx, nz = -dz, dx
        if any(f[0] <= x <= f[2] and f[1] <= z <= f[3] for f in flats):
            continue                          # (on paving: the paving's own level)
        if (ends_on[0] and math.hypot(x - P[0][0], z - P[0][1]) < 1.6) or (ends_on[1] and math.hypot(x - P[-1][0], z - P[-1][1]) < 1.6):
            continue                          # (its end on another path: across it there lies the other path's climb)
        hl, hr = gz(x + nx * 1.4, z + nz * 1.4), gz(x - nx * 1.4, z - nz * 1.4)
        if abs(hl - hr) > 0.2 and j % 2 == 0:
            breach('A4', x, z, '%s: one edge %.2f m above the other' % (lab, abs(hl - hr)))
        if j + 1 < len(dense):
            gr = abs(gz(dense[j + 1][0], dense[j + 1][1]) - gz(x, z)) / (math.hypot(dense[j + 1][0] - x, dense[j + 1][1] - z) or 1)
            if gr > 0.33:
                breach('A4', x, z, '%s: %.2f a metre, steeper than she can walk' % (lab, gr))
    # A2/A3 each end on another path, the covered walk, paving, a gate or a door
    for e in (P[0], P[-1]):
        dmin = min([line_d(e[0], e[1], Q) for q, Q in enumerate(PP) if q != k] + [line_d(e[0], e[1], N.GALLERY['line'])])
        on_pave = any(f[0] - 0.5 <= e[0] <= f[2] + 0.5 and f[1] - 0.5 <= e[1] <= f[3] + 0.5 for f in flats)
        near_gate = min(math.hypot(e[0] - g[0], e[1] - g[1]) for g in list(G['side_gates'].values()) + [N.PARK_GATE]) < 4.0
        near_door = any(math.hypot(e[0] - d['pos'][0], e[1] - d['pos'][1]) < 2.5 for d in SC['entrances'])
        at_house = any(N.rect_d(e[0], e[1], G[r]) < 1.0 for r in ('museu_r', 'trias_r', 'larrard_r', 'austria'))
        on_pave = on_pave or any(in_poly(e[0], e[1], dk['p']) or poly_d(e[0], e[1], dk['p']) < 0.6 for dk in SC['decks'])
        at_calv = math.hypot(e[0] - G['calvari'][0], e[1] - G['calvari'][1]) < 9.5
        if dmin > 0.6 and not (on_pave or near_gate or near_door or at_house or at_calv):
            breach('A2', e[0], e[1], '%s: its end meets nothing (%.1f m from the next path)' % (lab, dmin))
        elif 0.6 < dmin < 2.5 and not (on_pave or near_gate or near_door):
            breach('A3', e[0], e[1], '%s: its end stops %.1f m short of the path it joins' % (lab, dmin))
# A5 nothing solid on the park's paths
for poly in SC['solids']:
    cx = sum(p[0] for p in poly) / len(poly)
    cz = sum(p[1] for p in poly) / len(poly)
    if not (40 < cx < 200 and -260 < cz < -130):
        continue
    for k, P in enumerate(PP):
        if line_d(cx, cz, P) < 1.25 and poly_d(cx, cz, poly) < 1.2:
            breach('A5', cx, cz, 'something solid on park path %d' % (k + 1))
# B2 no lip where the ground meets the paving: the ground just outside each paved rect level with its edge
for f in flats:
    x0, z0, x1, z1, h0, h1 = f[:6]
    if not (40 < x0 < 200 and -260 < z0 < -130):
        continue
    for t in [k / 12 for k in range(13)]:
        for (px, pz, ox, oz, hh) in ((x0 + (x1 - x0) * t, z0, 0, -1, None), (x0 + (x1 - x0) * t, z1, 0, 1, None),
                                     (x0, z0 + (z1 - z0) * t, -1, 0, None), (x1, z0 + (z1 - z0) * t, 1, 0, None)):
            hp = h0 if abs(h0 - h1) < 1e-6 else None
            if hp is None:
                continue
            qx, qz = px + ox * 0.4, pz + oz * 0.4
            if any(f2 is not f and f2[0] <= qx <= f2[2] and f2[1] <= qz <= f2[3] for f2 in flats):
                continue                       # (paving meets paving)
            if any(poly_d(qx, qz, poly) < 0.7 or in_poly(qx, qz, poly) for poly in SC['solids']
                   if abs(poly[0][0] - qx) < 40 and abs(poly[0][1] - qz) < 40):
                continue                       # (a wall there: a wall's foot, not a lip)
            g = gz(qx, qz)
            if -0.6 < g - hp < -0.08:
                breach('B2', px, pz, 'a lip %.2f m down from the paving to the ground' % (hp - g))
# F10 a path to every house door
for d in SC['entrances']:
    x, z = d['pos']
    if not (40 < x < 200 and -260 < z < -130):
        continue
    dp = min(line_d(x, z, P) for P in PP)
    on_pave = any(f[0] - 0.6 <= x <= f[2] + 0.6 and f[1] - 0.6 <= z <= f[3] + 0.6 for f in flats)
    if dp > 1.6 and not on_pave and d['id'] != 'trias_soterrani':
        breach('F10', x, z, 'the door of %s: the nearest path is %.1f m off' % (d['id'], dp))

# ------------------------------------------------------------------ the report
by = {}
for b in OUT:
    by.setdefault(b['rule'], []).append(b)
for r in sorted(by):
    print('%s: %d' % (r, len(by[r])))
    for b in by[r][:12]:
        print('   (%.1f, %.1f) %s' % (b['x'], b['z'], b['text']))
    if len(by[r]) > 12:
        print('   … and %d more' % (len(by[r]) - 12))
print('TOTAL %d' % len(OUT))
if len(sys.argv) > 1:
    json.dump(OUT, open(sys.argv[1], 'w'), indent=0)
