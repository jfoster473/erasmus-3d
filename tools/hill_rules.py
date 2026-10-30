# The hill path's rules, checked on the build (round 35; workshop/journal/DECISIONS.md "Round 35", P1-P3, H1-H5):
#   python3 tools/hill_rules.py [map.png]
# Reads bigfiles/built/barcelona/scene.json (the path's points, its railing's segments) and the hillside (north.py), says
# each rule's breaches in plain words, and draws a map: the path, its railing (each run its own colour), breaches red.
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, '..', 'worlds', 'barcelona')
sys.path.insert(0, os.path.join(W, 'build'))
import north as N
s = json.load(open(os.path.join(HERE, '..', 'bigfiles', 'built', 'barcelona', 'scene.json')))
P = s['north']['path']
R = s['north']['rails']
GLADE_X = (-197.0, -147.0)


def nearest(x, z):
    best, bi = 1e9, 0
    for i, p in enumerate(P):
        d = (p[0] - x) ** 2 + (p[1] - z) ** 2
        if d < best:
            best, bi = d, i
    return bi, math.sqrt(best)


def normal(i):
    a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    return -(b[1] - a[1]) / L, (b[0] - a[0]) / L


SL = [0.0]
for i_ in range(1, len(P)):
    SL.append(SL[-1] + math.hypot(P[i_][0] - P[i_ - 1][0], P[i_][1] - P[i_ - 1][1]))


def at_dist(i, d):
    j = i
    while 0 < j < len(P) - 1 and abs(SL[j] - SL[i]) < abs(d):
        j += 1 if d > 0 else -1
    return j


def turn_at(i, d=9.0):
    """(as the build's bend_at: the turn over 9 m either side, and the outside)"""
    a, b, c = P[at_dist(i, -d)], P[i], P[at_dist(i, d)]
    t1 = (b[0] - a[0], b[1] - a[1]); t2 = (c[0] - b[0], c[1] - b[1])
    l1, l2 = math.hypot(*t1) or 1, math.hypot(*t2) or 1
    d = (t1[0] * t2[0] + t1[1] * t2[1]) / l1 / l2
    nx, nz = normal(i)
    inward = (t2[0] / l2 - t1[0] / l1) * nx + (t2[1] / l2 - t1[1] / l1) * nz
    return math.acos(max(-1, min(1, d))), (-1 if inward > 0 else 1)


# the railing's runs: segments joined end to end
runs = []
for seg in R:
    a, b = (seg[0], seg[1]), (seg[2], seg[3])
    if runs and math.hypot(runs[-1][-1][0] - a[0], runs[-1][-1][1] - a[1]) < 0.05:
        runs[-1].append(b)
    else:
        runs.append([a, b])
bad = []
hill_runs = []
for r in runs:
    if nearest(*r[len(r) // 2])[1] > 1.6:
        continue                                  # (the glade's end fence, down the slope between two legs)
    hill_runs.append(r)
    if len(r) < 6:
        bad.append(('H5 a short fence (%d posts)' % len(r), r[0]))
    for a, b in zip(r, r[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 2.6:
            bad.append(('H5 a post missing (%.1f m between posts)' % math.hypot(b[0] - a[0], b[1] - a[1]), a))
    for q in r:
        f_ = N.FAIR
        if f_[0] - 0.5 < q[0] < f_[2] + 0.5 and f_[1] - 0.5 < q[1] < f_[3] + 0.5:
            bad.append(('H4 a post on the funfair\'s paving', q))
        i, d = nearest(*q)
        if d > 1.6:
            continue                              # (H6: a railing's end turning off to the bank's foot)
        nx, nz = normal(i)
        sd = 1 if (q[0] - P[i][0]) * nx + (q[1] - P[i][1]) * nz > 0 else -1
        fall = (N.height(P[i][0] - nx * sd * 6, P[i][1] - nz * sd * 6) - N.height(P[i][0] + nx * sd * 6, P[i][1] + nz * sd * 6)) / 2
        turn, out = turn_at(i)
        if fall < -0.3 and not (turn > 0.6 and out == sd):           # (round a bend its outside: H2)
            bad.append(('H1 on the uphill side (the hill rises %.1f m over 6 m there)' % -fall, q))
# fences on both sides at once
sides = {}
for r in hill_runs:
    for q in r:
        i, d = nearest(*q)
        if d > 1.6:
            continue
        nx, nz = normal(i)
        sides.setdefault(i // 2, set()).add(1 if (q[0] - P[i][0]) * nx + (q[1] - P[i][1]) * nz > 0 else -1)
for k, v in sides.items():
    if len(v) == 2:
        bad.append(('H5 fences on both sides', (P[k * 2][0], P[k * 2][1])))
# P1: the ground against the path (each leg its own level)
worst = 0.0
for i, p in enumerate(P):
    g = N.ground(p[0], p[1])
    worst = max(worst, abs(g - p[2]))
    if abs(g - p[2]) > 0.3:
        bad.append(('P1 the ground %.1f m off the path\'s level' % (g - p[2]), (p[0], p[1])))
seen = {}
for what, q in bad:
    k = (what.split(' (')[0], round(q[0] / 6), round(q[1] / 6))
    if k not in seen:
        seen[k] = (what, q)
for what, q in seen.values():
    print('%-60s at %.0f, %.0f' % (what, q[0], q[1]))
print('HILL RULES: %d railing runs, %d breaches (%d places); ground off the path by %.2f m at worst' % (
    len(hill_runs), len(bad), len(seen), worst))
if len(sys.argv) > 1:
    from PIL import Image, ImageDraw
    x0, x1, z0, z1 = -225, -40, -300, -95
    k = 6
    im = Image.new('RGB', (int((x1 - x0) * k), int((z1 - z0) * k)), (236, 240, 228))
    d = ImageDraw.Draw(im)
    f = lambda x, z: ((x - x0) * k, (z - z0) * k)
    d.line([f(p[0], p[1]) for p in P], fill=(196, 160, 110), width=int(2.4 * k))
    cols = [(40, 90, 200), (20, 140, 70), (150, 60, 170), (200, 120, 20), (20, 150, 160)]
    for n, r in enumerate(runs):
        d.line([f(*q) for q in r], fill=cols[n % len(cols)], width=3)
        for q in r:
            x, y = f(*q); d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=cols[n % len(cols)])
    for what, q in seen.values():
        x, y = f(*q); d.ellipse([x - 12, y - 12, x + 12, y + 12], outline=(220, 30, 30), width=3)
    im.save(sys.argv[1])
