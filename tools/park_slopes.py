"""Invisible walls in Park Güell (docs/PATH_RULES.md G1): every half metre inside the park wall, the ground as the game
walks it (scene.json: flats, the finer and the coarse ground grid), its slope as north.gd measures it; where it is
steeper than she may walk up (north.gd MAX_UP) and nothing she can see stands there (a solid within 0.8 m, stairs, a
flat, a deck, a path she may climb on), it is an invisible wall.

  python3 tools/park_slopes.py [breaches.json]       prints the clusters; writes them for tools/plan_maps.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = json.load(open(os.path.join(HERE, '..', 'bigfiles', 'built', 'barcelona', 'scene.json')))
T, TFS = SC['terrain'], SC.get('terrain_fine', [])
P = SC['north']['park']
MAX_UP = float(os.environ.get("MAX_UP", "0.30"))


def grid_h(G, x, z):
    fi, fj = (x - G['x0']) / G['step'], (z - G['z0']) / G['step']
    i, j = int(fi), int(fj)
    a, b = fi - i, fj - j
    H = G['h']
    return (H[j][i] * (1 - a) + H[j][i + 1] * a) * (1 - b) + (H[j + 1][i] * (1 - a) + H[j + 1][i + 1] * a) * b


def terrain(x, z):
    for f in SC['flats']:
        if f[0] <= x <= f[2] and f[1] <= z <= f[3]:
            return f[4] + (f[5] - f[4]) * (z - f[1]) / max(0.01, f[3] - f[1])
    for G in TFS:
        if 0 <= (x - G['x0']) / G['step'] < G['nx'] - 1 and 0 <= (z - G['z0']) / G['step'] < G['nz'] - 1:
            return grid_h(G, x, z)
    return grid_h(T, x, z)


def in_poly(x, z, poly):
    ins, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, zi, xj, zj = poly[i][0], poly[i][1], poly[j][0], poly[j][1]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / ((zj - zi) or 1e-9) + xi:
            ins = not ins
        j = i
    return ins


def seg_d(px, pz, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dz * dz or 1e-9
    t = max(0.0, min(1.0, ((px - a[0]) * dx + (pz - a[1]) * dz) / L2))
    return math.hypot(px - a[0] - dx * t, pz - a[1] - dz * t)


def poly_d(x, z, poly):
    return min(seg_d(x, z, a, b) for a, b in zip(poly, poly[1:] + poly[:1]))


wall = P['wall']
solids = [s for s in SC['solids'] if all(40 < q[0] < 195 and -260 < q[1] < -130 for q in s)]
solids += [[[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]] for r in SC['blocked'] if 40 < r[0] < 195 and -260 < r[1] < -130]   # (posts, columns, shrubs' boxes)
paths = P['paths']
steps = P.get('steps', [])
decks = [d['p'] for d in SC.get('decks', [])]


def visible_stop(x, z):
    if any(poly_d(x, z, s) < 0.8 or in_poly(x, z, s) for s in solids if abs(s[0][0] - x) < 30 and abs(s[0][1] - z) < 30):
        return True
    if poly_d(x, z, wall) < 1.2:
        return True
    if any(r[0] - 0.5 <= x <= r[2] + 0.5 and r[1] - 0.5 <= z <= r[3] + 0.5 for r in steps):
        return True
    if any(in_poly(x, z, d) or poly_d(x, z, d) < 0.6 for d in decks):
        return True
    return False


def on_path(x, z):
    return any(seg_d(x, z, a, b) < 1.6 for pl in paths for a, b in zip(pl, pl[1:]))


hits = []
# (round 35: at the park's own limit, north.gd — she climbs anything she wouldn't slide down) where she is stopped:
# walkable ground whose next step uphill is too steep, with nothing she can see there
LIM = float(os.environ.get("MAX_UP", "0.55"))


def grad(x, z):
    e = 0.5
    return ((terrain(x + e, z) - terrain(x - e, z)) / (2 * e), (terrain(x, z + e) - terrain(x, z - e)) / (2 * e))


x0, z0, x1, z1 = 44.0, -256.0, 192.0, -136.0
z = z0
while z < z1:
    x = x0
    while x < x1:
        if in_poly(x, z, wall) and poly_d(x, z, wall) > 1.2 and not any(f[0] <= x <= f[2] and f[1] <= z <= f[3] for f in SC['flats']):
            g0 = math.hypot(*grad(x, z))
            if g0 <= LIM:
                h0 = terrain(x, z)
                for a in range(8):
                    dx, dz = math.cos(a * math.pi / 4) * 0.6, math.sin(a * math.pi / 4) * 0.6
                    if (terrain(x + dx, z + dz) - h0) / 0.6 > LIM * 0.8 and math.hypot(*grad(x + dx, z + dz)) > LIM:
                        if not visible_stop(x, z) and not on_path(x, z):
                            hits.append((x, z, g0, False))
                        break
        x += 0.5
    z += 0.5

# clusters (cells within 1.2 m join)
cl = []
for h in hits:
    for c in cl:
        if any(abs(h[0] - q[0]) <= 1.0 and abs(h[1] - q[1]) <= 1.0 for q in c[-30:]):
            c.append(h)
            break
    else:
        cl.append([h])
cl.sort(key=lambda c: -len(c))
out = []
for c in cl:
    cx = sum(q[0] for q in c) / len(c)
    cz = sum(q[1] for q in c) / len(c)
    gmax = max(q[2] for q in c)
    near = sum(1 for q in c if q[3])
    out.append({'rule': 'G1', 'x': round(cx, 1), 'z': round(cz, 1), 'n': len(c), 'text': '%d cells, steepest %.2f, %d by a path' % (len(c), gmax, near)})
print('G1 invisible stops: %d in %d places' % (len(hits), len(cl)))
for o in out[:40]:
    print('   (%.1f, %.1f) %s' % (o['x'], o['z'], o['text']))
if len(sys.argv) > 1:
    json.dump(out, open(sys.argv[1], 'w'), indent=0)
