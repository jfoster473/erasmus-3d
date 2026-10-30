"""Eye-level pictures along every path, both ways (round 35, docs/PATH_RULES.md review).

  python3 tools/walk_views.py <dir> [hill|park|all]     writes <dir>/v.json
  then: Godot --path . -- --views=<dir>/a --viewfile=<dir>/v.json --groundrel
  and:  python3 tools/sheet9.py <dir>/a <dir>/sheets <prefix>

The camera stands on the path's middle at her eye height (1.55 m over the ground) and looks 7 m ahead; the hill path
every 15 m, the park's paths (and the covered walk, the cellar track) every 7 m.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = json.load(open(os.path.join(HERE, '..', 'bigfiles', 'built', 'barcelona', 'scene.json')))
NORTH_TRAIL = SC['north']['park'].get('cellar_trail', [])


def dense(line, step=0.5):
    out = []
    for a, b in zip(line, line[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(L / step))
        out += [(a[0] + (b[0] - a[0]) * t / k, a[1] + (b[1] - a[1]) * t / k) for t in range(k)]
    out.append(tuple(line[-1][:2]))
    return out


def walk(name, line, every, V):
    d = dense([p[:2] for p in line])
    L = [0.0]
    for a, b in zip(d, d[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tot = L[-1]
    for way, pts in (('up', d), ('dn', d[::-1])):
        Ls = L if way == 'up' else [tot - l for l in L[::-1]]
        u = 0.0
        while u < tot - 2.0:
            i = min(range(len(pts)), key=lambda j: abs(Ls[j] - u))
            j = min(range(len(pts)), key=lambda j: abs(Ls[j] - (u + 7.0)))
            V['%s_%s_%03d' % (name, way, int(u))] = [pts[i][0], 1.55, pts[i][1], pts[j][0], 0.35, pts[j][1], 720, 300.0, 300.0, 66]
            u += every


if __name__ == '__main__':
    out, which = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'all')
    n = SC['north']
    V = {}
    if which in ('hill', 'all'):
        walk('hill', n['path'], 15.0, V)
    if which in ('park', 'all'):
        for k, pl in enumerate(n['park']['paths']):
            walk('park%02d' % (k + 1) if k < len(n['park']['paths']) - 1 else 'parkwalk', pl, 7.0, V)
        walk('cellar', NORTH_TRAIL, 2.0, V)
    os.makedirs(out, exist_ok=True)
    json.dump(V, open(os.path.join(out, 'v.json'), 'w'))
    print(len(V))
