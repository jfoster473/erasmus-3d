# Where the bike can't go in the wood (round 20e, the user's rule): "nail a rope to the trees on the edge,
# and that is the area you cannot cycle into", so the only invisible wall is between two trees.
# Every pair of neighbouring trunks (a Delaunay triangulation of them) no further apart than ROPE_MAX is
# tied together, unless the rope would cross a path; each triangle of three tied trunks is the thick of the
# wood, and the rope is the edge of all of them together. Any ground the rope closes in on every side (a
# gap among the trees the bike couldn't reach anyway) is filled in, so the rope only runs round the outside.
# The user picked 7.5 m (option E, from pictures of 3.5, 4.5, 5, 6 and 7.5 m), marked trees on the edge
# to leave out of it (so they can be cycled round) and a gap to close (TIE).
# Pure Python and numpy: world2d.py runs it in the build (with Blender's triangulation); a test can run it
# with scipy's. Metres, the engine's x and z.
import math
from collections import deque

import numpy as np

ROPE_MAX = 7.5      # two trunks further apart than this are not tied together
PATH_CLEAR = 0.5    # a rope keeps this far from a path's edge (so it never crosses one)
CELL = 0.25         # the no-bike map's cells (metres)
# the user's marks on the round-20e map (14 October 2026): trunks at the tips of spikes in the rope, left
# out of it so the bike can ride round them (they are still solid trunks)
LEAVE_OUT = [(116.79, -107.98), (116.92, -112.65), (119.18, -107.46), (141.42, -114.08), (158.4, -110.52),
             (166.18, -111.92), (107.61, -5.35), (107.39, -6.28), (108.35, 37.66), (155.42, 121.11),
             (165.68, 121.92), (177.2, 123.85), (201.18, 122.99), (199.74, 122.03)]
# and a gap to close: the mouth of a pocket west of the long path, north of its first crossing (the pocket is
# now planted with trees: forest.py's POCKETS)
TIE = [((124.33, -55.66), (131.61, -59.55))]


def seg_dist(p, q, A, B):
    """The distances from segment p-q to each of the segments A[i]-B[i] (arrays of points)."""
    def pt_seg(x, a, b):
        ab = b - a
        t = np.clip(((x - a) * ab).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-9), 0.0, 1.0)
        return np.hypot(*(a + t[..., None] * ab - x).T)

    def cross(o, a, b):
        return (a[..., 0] - o[..., 0]) * (b[..., 1] - o[..., 1]) - (a[..., 1] - o[..., 1]) * (b[..., 0] - o[..., 0])
    P_, Q_ = np.broadcast_to(p, A.shape), np.broadcast_to(q, A.shape)
    d = np.minimum.reduce([pt_seg(P_, A, B), pt_seg(Q_, A, B), pt_seg(A, P_, Q_), pt_seg(B, P_, Q_)])
    hit = (cross(A, B, P_) * cross(A, B, Q_) < 0) & (cross(P_, Q_, A) * cross(P_, Q_, B) < 0)
    return np.where(hit, 0.0, d)


def bike_rope(trunks, paths, triangulate):
    """trunks: [(x, z)]; paths: [{'w': metres wide, 'pts': [(x, z)]}]; triangulate(points) -> [(i, j, k)].
    Returns the ropes ([[x0, z0, x1, z1]], trunk to trunk), and the no-bike map: a bool array (rows z,
    columns x) of CELL-metre cells, with its corner (x0, z0)."""
    P = np.array([p for p in trunks if min(math.hypot(p[0] - a, p[1] - b) for a, b in LEAVE_OUT) > 0.05], float)
    A, B, HW = [], [], []
    for path in paths:
        for a, b in zip(path['pts'], path['pts'][1:]):
            A.append(a), B.append(b), HW.append(path['w'] / 2 + PATH_CLEAR)
    A, B, HW = np.array(A, float), np.array(B, float), np.array(HW)
    tied = {}

    def tie(i, j):
        k = (min(i, j), max(i, j))
        if k not in tied:
            p, q = P[i], P[j]
            ok = math.hypot(*(p - q)) <= ROPE_MAX
            if ok:
                near = (np.minimum(A[:, 0], B[:, 0]) < max(p[0], q[0]) + 3) & (np.maximum(A[:, 0], B[:, 0]) > min(p[0], q[0]) - 3) & \
                       (np.minimum(A[:, 1], B[:, 1]) < max(p[1], q[1]) + 3) & (np.maximum(A[:, 1], B[:, 1]) > min(p[1], q[1]) - 3)
                if near.any():
                    ok = bool((seg_dist(p, q, A[near], B[near]) >= HW[near]).all())
            tied[k] = ok
        return tied[k]
    tris = [t for t in triangulate(P) if tie(t[0], t[1]) and tie(t[1], t[2]) and tie(t[0], t[2])]
    edges = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2])):
            k = (min(a, b), max(a, b))
            edges[k] = edges.get(k, 0) + 1
    near_trunk = lambda q: int(np.argmin(np.hypot(P[:, 0] - q[0], P[:, 1] - q[1])))
    ties = [tuple(sorted((near_trunk(a), near_trunk(b)))) for a, b in TIE]
    rope = [e for e, n in edges.items() if n == 1] + ties

    # the map: the triangles and the ropes drawn in, then everything the open ground outside can't reach
    x0, z0 = P[:, 0].min() - 10, P[:, 1].min() - 10
    nx, nz = int((P[:, 0].max() + 10 - x0) / CELL) + 1, int((P[:, 1].max() + 10 - z0) / CELL) + 1
    blocked = np.zeros((nz, nx), bool)
    cx = x0 + (np.arange(nx) + 0.5) * CELL
    cz = z0 + (np.arange(nz) + 0.5) * CELL
    for t in tris:
        a, b, c = P[t[0]], P[t[1]], P[t[2]]
        i0, i1 = int((min(a[0], b[0], c[0]) - x0) / CELL), int((max(a[0], b[0], c[0]) - x0) / CELL) + 1
        j0, j1 = int((min(a[1], b[1], c[1]) - z0) / CELL), int((max(a[1], b[1], c[1]) - z0) / CELL) + 1
        X, Z = np.meshgrid(cx[i0:i1 + 1], cz[j0:j1 + 1])
        s = [(v[0] - u[0]) * (Z - u[1]) - (v[1] - u[1]) * (X - u[0]) for u, v in ((a, b), (b, c), (c, a))]
        inside = ((s[0] >= 0) & (s[1] >= 0) & (s[2] >= 0)) | ((s[0] <= 0) & (s[1] <= 0) & (s[2] <= 0))
        blocked[j0:j1 + 1, i0:i1 + 1] |= inside
    for (i, j) in rope:
        n = int(math.hypot(*(P[j] - P[i])) / (CELL * 0.4)) + 2
        for f in np.linspace(0.0, 1.0, n):
            q = P[i] + (P[j] - P[i]) * f
            blocked[int((q[1] - z0) / CELL), int((q[0] - x0) / CELL)] = True
    seen = np.zeros_like(blocked)
    todo = deque()
    for j in range(nz):
        for i in (0, nx - 1):
            if not blocked[j, i] and not seen[j, i]:
                seen[j, i] = True
                todo.append((j, i))
    for i in range(nx):
        for j in (0, nz - 1):
            if not blocked[j, i] and not seen[j, i]:
                seen[j, i] = True
                todo.append((j, i))
    while todo:
        j, i = todo.popleft()
        for (jj, ii) in ((j + 1, i), (j - 1, i), (j, i + 1), (j, i - 1)):
            if 0 <= jj < nz and 0 <= ii < nx and not blocked[jj, ii] and not seen[jj, ii]:
                seen[jj, ii] = True
                todo.append((jj, ii))
    hole = ~blocked & ~seen

    def in_hole(q):
        i, j = int((q[0] - x0) / CELL), int((q[1] - z0) / CELL)
        return 0 <= i < nx and 0 <= j < nz and hole[j, i]
    out = []
    for (i, j) in rope:
        m, d = (P[i] + P[j]) / 2, P[j] - P[i]
        nrm = np.array([-d[1], d[0]]) / max(1e-6, math.hypot(*d)) * 0.6
        if (i, j) in ties or not (in_hole(m + nrm) or in_hole(m - nrm)):
            out.append([round(float(v), 3) for v in (P[i][0], P[i][1], P[j][0], P[j][1])])
    print('BIKEROPE %d trunks (%d left out), %d triangles, %d ropes, %.0f m of rope, %.0f m2 roped off (%.0f m2 of it gaps filled in)' % (
        len(P), len(trunks) - len(P), len(tris), len(out), sum(math.hypot(r[2] - r[0], r[3] - r[1]) for r in out),
        (blocked | hole).sum() * CELL * CELL, hole.sum() * CELL * CELL))
    return out, blocked | hole, float(x0), float(z0)
