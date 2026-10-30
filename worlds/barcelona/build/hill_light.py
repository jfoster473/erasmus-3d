# (round 25) The light on the hill wood's floor over a day, as the eastern wood's (forest.py, forest_light()), for the
# hill's light map (north_build.py). The user (round 20): "the breaks in the trees where the sun comes through get
# light, so turn green, and the other part is brown"; (round 25) "Did you do the sunlight thing to check where the
# ground of the hill forest should have the darker shades?". Until now the hill's floor was shaded only by how many
# trees stood near; now, as in the eastern wood, the sun is followed across the game's day (and the open sky), through
# every crown and bush, down to each square metre of the floor. Unlike the eastern wood the ground here is a steep
# hillside, so the leaves are kept by their height above sea level, and the hill itself can stand in the sun's way.
# Pure numpy (no Blender), so it can be tried on its own.
import math
import numpy as np

SUN_SHARE = 0.6           # the sun's part of the light (the rest is the open sky's), as forest.py
# how thick each kind of leaf is (light lost a metre through it), as forest.py's LEAF_DENSITY
LEAF_DENSITY = {'LeavesHolm': 0.45, 'LeavesHolmB': 0.45, 'LeavesCarob': 0.42, 'LeavesCypress': 0.5,
                'LeavesStonePine': 0.38, 'LeavesCork': 0.32, 'LeavesAleppo': 0.2, 'LeavesOlive': 0.22, 'bush': 0.3}


def floor_light(blobs, G0, x0, z0, top=30.0, reach=70.0):
    """blobs: the crowns and bushes as rough ellipsoids, (x, z, h, rx, rz, rh, card size, material name) in the engine's
    metres; G0[j, i]: the ground's height at (x0 + i + 0.5, z0 + j + 0.5), a metre to a cell. Returns the share of the
    day's light (0..1) reaching each cell's floor. Rays are followed until they are `top` metres above where they
    started or `reach` metres away across."""
    D, W = G0.shape
    hmin = math.floor(float(G0.min())) - 1.0
    NL = int(math.ceil(float(G0.max()) + top - hmin)) + 2
    rho = np.zeros((NL, D, W), np.float32)
    gx = x0 + np.arange(W) + 0.5
    gzz = z0 + np.arange(D) + 0.5
    gh = hmin + np.arange(NL) + 0.5
    for (bx, bz, bh, rx, rz, rh, size, name) in blobs:
        k = LEAF_DENSITY.get(name, 0.4)
        pad = 0.2 * size                                   # (the leaf cards reach out past the crown's line)
        rx, rz, rh = rx + pad, rz + pad, rh + pad * 0.6
        i0, i1 = max(0, int(bx - rx - x0)), min(W, int(bx + rx - x0) + 2)
        j0, j1 = max(0, int(bz - rz - z0)), min(D, int(bz + rz - z0) + 2)
        l0, l1 = max(0, int(bh - rh - hmin)), min(NL, int(bh + rh - hmin) + 2)
        if i0 >= i1 or j0 >= j1 or l0 >= l1:
            continue
        q = (((gh[l0:l1] - bh) / rh) ** 2)[:, None, None] + (((gzz[j0:j1] - bz) / rz) ** 2)[None, :, None] + \
            (((gx[i0:i1] - bx) / rx) ** 2)[None, None, :]
        rho[l0:l1, j0:j1, i0:i1] += k * np.clip((1.0 - q) * 2.5, 0.0, 1.0)
    J, I = np.mgrid[0:D, 0:W]
    X, Z = gx[I], gzz[J]
    H = G0 + 0.3

    def through(e_deg, b_deg):
        e, b = math.radians(e_deg), math.radians(b_deg)
        de, ds, up = math.cos(e) * math.sin(b), -math.cos(e) * math.cos(b), math.sin(e)     # east, south, up
        tau = np.zeros((D, W), np.float32)
        smax = min(top / up, reach / max(math.cos(e), 1e-3))
        s = 0.5
        while s < smax:
            ii = np.floor(X + de * s - x0).astype(np.int32)
            jj = np.floor(Z + ds * s - z0).astype(np.int32)
            ph = H + up * s
            inb = (ii >= 0) & (ii < W) & (jj >= 0) & (jj < D)
            ii, jj = np.clip(ii, 0, W - 1), np.clip(jj, 0, D - 1)
            ll = np.clip(np.floor(ph - hmin).astype(np.int32), 0, NL - 1)
            add = np.where(ph < G0[jj, ii], 4.0, rho[ll, jj, ii])            # (the hillside itself in the way)
            tau += np.where(inb, add, 0.0).astype(np.float32)
            s += 1.0
        return np.exp(-tau)

    sun = np.zeros((D, W), np.float32)
    wsum = 0.0
    for i in range(24):                                    # the sun across the game's day (as main.gd's sky_positions())
        f = (i + 0.5) / 24
        el = 62.0 * math.sin(math.pi * f)
        w = min(1.0, max(0.0, el / 14.0)) ** 1.5             # (the low sun, at either end of the day, is weak)
        if w > 0.01:
            sun += w * through(el, 70.0 + 220.0 * f)
            wsum += w
    sun /= wsum
    sky = np.zeros((D, W), np.float32)
    patches = [(30.0, b) for b in range(0, 360, 45)] + [(58.0, b + 22.5) for b in range(0, 360, 45)] + [(85.0, 0.0)]
    for el, b in patches:
        sky += through(el, b)
    sky /= len(patches)
    return SUN_SHARE * sun + (1 - SUN_SHARE) * sky


def steps(L, x0, z0, green_at=(0.3, 0.6), mid_at=(0.05, 0.12)):
    """From the light, as forest.py: how green (lawn) and how mossy (the half shade's green) each cell is, their edges
    wandering a little."""
    D, W = L.shape
    X, Z = np.meshgrid(x0 + np.arange(W) + 0.5, z0 + np.arange(D) + 0.5)
    wob = 0.55 * np.sin(X * 0.4 + 0.8 * np.sin(Z * 0.28)) + 0.45 * np.sin(Z * 0.54 - X * 0.19)
    t = np.clip((L + 0.05 * wob - green_at[0]) / (green_at[1] - green_at[0]), 0.0, 1.0)
    G = t * t * (3 - 2 * t)
    t = np.clip((L + 0.03 * wob - mid_at[0]) / (mid_at[1] - mid_at[0]), 0.0, 1.0)
    M = np.maximum(t * t * (3 - 2 * t), G)
    return G, M
