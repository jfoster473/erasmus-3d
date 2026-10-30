# The north of the map, round 22 (the user's plan): the funfair moved up the hill (same place across, so its
# Ferris wheel shows high at the end of La Rambla), reached by a cable car and by a long, irregular winding path
# through a steep wood; Gràcia, a quarter of small streets, between the Eixample and Park Güell, which sits on a
# gentle rise north of the eastern wood, round like the real one.
# Pure Python: the layout and the ground's height, in the engine's metres (x east, z south, so north is -z; h up).
# The mock-up (mock_north.py) and, once the user has agreed it, the build read it.
import math

# (round 26, the user: "The issue was with the EXISTING fences. They sit on the slope, then need to just be moved a few
# inches up the hill so they are on the flat part. Then the road is moved a few inches over to match… There are also
# random fences. You can be liberal on the inside of the bends"; mock-up 2 of round26/fence_mockups.png, "Continue with
# the ropes"): the railing 30 cm nearer the path, the path drawn 30 cm the other way, and the level ground beside the
# path carried 0.6 m further out, so the posts stand on the flat even as the ground is drawn (in 1.65 m squares); the
# stray bits of fence gone (north_build.py)
TIDY_FENCES = True
LIP = 0.8                # level ground past the path's edge before the bank down (was 0.2: the posts stood on the slope)

# ------------------------------------------------------------------ the ground

FOOT_Z = -106.0          # where the hill starts, just north of the city's edge
FAIR_H = 78.0            # the funfair's plateau, metres up (the user: from La Rambla it shows halfway between the
                         # street trees' tops and the top of the hill)
FAIR = (-108.0, -320.0, -30.0, -277.0)      # the plateau (x0, z0, x1, z1): cut back into the hill (the user: a wider forecourt)
# (round 35, PATH_RULES E4, the user: "it doesn't come out too far into the hill… too much space up there": was
# (-108, -320, -18, -265), 90 x 55 m; now 76 x 43, back 12 m from the south and the east)
TOP_Z = -305.0                               # where the slope reaches the funfair's height
RIDGE_Z, RIDGE_H = -430.0, 150.0            # (the hilltop behind it, until round 25)
CREST_H = 6.0                               # (round 25) the bank behind the funfair: how far it rises above it
EAST_X = (-14.0, 16.0)                      # west of this the big hill, east of it the gentle rise (blended; round 26:
                                            # the blend west of Gràcia, so the village sits on the gentle rise alone)
PARK_C = (114.0, -196.0)                    # Park Güell's middle, roughly (round 25: its wall is PARK_WALL)
PARK_H = 9.0                                # its middle, metres up ("just a little bit of elevation")


def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def bumps(x, z):
    return 1.6 * math.sin(x * 0.071 + z * 0.043) + 1.1 * math.sin(x * 0.023 - z * 0.061 + 1.7) + 0.6 * math.sin(x * 0.19 + z * 0.13)


def hill_west(x, z):
    """The funfair's hill: an even steep slope from its foot up to the funfair's level (reached at the plateau's back,
    FAIR z0), then on up to the hilltop; the plateau a flat terrace on it, with a retaining wall where the slope
    falls away below it (its south side: the ball goes over the railing there)."""
    if z > FOOT_Z:
        return 0.05
    d = FOOT_Z - z                                          # metres north of the foot
    to_top = FOOT_Z - TOP_Z                                 # 199 m
    if d <= to_top:
        h = FAIR_H * d / to_top
    else:
        # (round 25, the user: the church "into the hill, but don't have the hill going up past it. Just enough hill so
        # that Sandra can't walk up": the summit is the funfair's; behind it a steep bank up to just below the crypt's
        # roof, a low rounded top, and then the land falls away northwards, out of sight)
        h = FAIR_H + CREST_H * smooth(FAIR[1], FAIR[1] - 9.0, z) - 14.0 * smooth(-385.0, -450.0, z)
    fx = max(FAIR[0] - x, 0.0, x - FAIR[2])
    fz = max(FAIR[1] - z, 0.0, z - FAIR[3])
    k = 1.0 - smooth(0.0, 2.5, math.hypot(fx, fz))        # (a terrace wall: steep, 2.5 m)
    h = FAIR_H if fx == 0 and fz == 0 else h * (1 - k) + FAIR_H * k     # (round 25: the plateau flat right to its back)
    return h + bumps(x, z) * smooth(0, 20, d) * (1 - k) * (0.35 if z < FAIR[1] + 4 else 1.0)


# (round 25) the park's wall, no longer an oval: as laid out in reality, round the hill, its south side kept clear of
# Gràcia's top blocks (the Larrard gate at its south-west corner opens onto the lane between them). (x, z) metres.
PARK_WALL = [(63.0, -157.0), (52.0, -175.0), (47.0, -200.0), (54.0, -225.0), (74.0, -244.0), (105.0, -251.0),
             (140.0, -247.0), (168.0, -233.0), (181.0, -210.0), (180.0, -186.0), (167.0, -164.0), (146.0, -150.0),
             (122.0, -143.0), (106.0, -141.0), (92.0, -145.5), (84.0, -152.0), (70.0, -155.0)]


def _in_wall(x, z):
    inside = False
    P = PARK_WALL
    for (x0, z0), (x1, z1) in zip(P, P[1:] + P[:1]):
        if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0):
            inside = not inside
    return inside


def park_r(x, z):
    """How far (x, z) is from the park's wall, as the old oval's radius was: under 1 inside (0.9 is 4 m in), 1 on the
    wall, over 1 outside (1.25 is 10 m out)."""
    best = 1e9
    P = PARK_WALL
    for (x0, z0), (x1, z1) in zip(P, P[1:] + P[:1]):
        dx, dz = x1 - x0, z1 - z0
        t = max(0.0, min(1.0, ((x - x0) * dx + (z - z0) * dz) / (dx * dx + dz * dz)))
        best = min(best, math.hypot(x - x0 - dx * t, z - z0 - dz * t))
    return max(0.0, 1.0 - best / 40.0) if _in_wall(x, z) else 1.0 + best / 40.0


def rect_d(x, z, r):
    """How far (x, z) is outside the rectangle r = (x0, z0, x1, z1) (0 inside)."""
    return math.hypot(max(r[0] - x, 0.0, x - r[2]), max(r[1] - z, 0.0, z - r[3]))


# (round 40, F6) the Austria Gardens' even fall: its walks' outer edges + 0.3 m (north_build.py lays the walks at
# austria x0 + 2 + 6 i and z0 + 2.25 + 7.5 j, 1.6 m wide), and its height at the north and south edges — the south
# half's own fall (0.22 a metre) carried on north
def aus_plane():
    a_ = GUELL['austria']
    return (a_[0] + 0.9, a_[1] + 1.15, a_[0] + 21.1, a_[1] + 25.85, 18.15, 12.72)


_CV_CAP = [None]                                       # (the calvary's centre ground, worked out once: park_height)


def park_height(x, z):
    """(round 33) the park's ground with its footpaths graded: each path climbs evenly from one end to the other
    (its ends where the ground has them, or where the path it starts from has them), the ground beside it blending to
    it over a couple of metres — the user: the slope below the Casa Museu must be walkable; the path up to it rose
    0.75 at the house's foot. The viaducts' carriage roads (the last two) keep their own levels."""
    h = park_height_raw(x, z)
    # (near a junction two paths' grades meet: their heights are averaged by nearness, not laid one over the other)
    wsum, hsum, kmax = 0.0, 0.0, 0.0
    for prof in _park_profiles():
        d, t, _ = _seg_near(x, z, prof[0])
        if d > 4.0:
            continue
        k = 1.0 - smooth(1.6, 4.0, d)
        w = k / (0.1 + d) ** 3                        # (round 35, PATH_RULES A4: a path's own level holds across its
        wsum += w                                     #  width, a neighbour's barely reaches it — was 1 / (0.3 + d))
        hsum += w * prof_h(prof, t)
        kmax = max(kmax, k)
    if wsum > 0.0:
        h = h * (1 - kmax) + (hsum / wsum) * kmax
    # (round 34: the paths' grading never lifts the covered walk's floor; round 35, A4: but off its ends the paths keep
    # their own even climb — the floor's easing past an end made the last metres of path 2 too steep to walk)
    hg_ = gallery_ground(x, z, h, floor_only=True)
    h = hg_ + (h - hg_) * kmax
    s_, t_, be_, fl_ = gallery_where(x, z)
    if -GALLERY['out'] - 0.3 < s_ < GALLERY['deck_in'] + 0.3 and be_ < 0.3:
        h = min(h, fl_ + GALLERY['roof'] - 0.2)        # (round 34, first look: nor lifts the hill through its roof's paving)
    # (round 40, the calvary's review from above: the rise, and path 9's grade to its rim, came up through its platform
    # in a ragged green line) under the platform the ground stays 0.15 m under its top (0.475 above the centre's
    # ground, north_build.py), and outside it a gentle cut (0.45 a metre) back to the rise's own lie
    d_cv = math.hypot(x - GUELL['calvari'][0], z - GUELL['calvari'][1])
    if d_cv < 7.5 and _CV_CAP[0] != 'busy':
        if _CV_CAP[0] is None:
            _CV_CAP[0] = 'busy'
            _CV_CAP[0] = ground(*GUELL['calvari'])
        h = min(h, _CV_CAP[0] + 0.325 + 0.45 * max(0.0, d_cv - 4.4))
    # (the dragon stairs and the side stairs stand on their own ground, as before)
    G = GUELL
    for sr in [G['stairs_r']] + list(G['side_stairs']):
        if sr[0] <= x <= sr[2] and sr[1] <= z <= sr[3]:
            return park_height_raw(x, z)
    # (round 39, the user, of the side stairs: "fix the gaps in these stairs": the hillside's grass showed above the step
    # ends by the square's wall, and earth at the top landing) under a side flight, its landing and a little either
    # side, the ground stays just below the steps
    for (a0_, b0_, a1_, b1_) in G['side_stairs']:
        if a0_ - 1.7 <= x <= a1_ + 1.7 and b0_ - 0.3 <= z <= b1_:      # (a whole grid step either side: the ground's
                                                                      #  triangles reach from point to point, 1.65 m)
            top_ = G['stairs_top_z']
            prof_ = 9.0 + (G['square_h'] - 9.0) * min(1.0, max(0.0, (b1_ - z) / (b1_ - top_)))
            h = min(h, prof_ - 0.15)
    # (round 40, PATH_RULES B1, the user at the gate plaza: "there's this brown stuff there, and the gravel path goes on
    # top of it when it would have to go underneath the paving") a path's grading never lifts the ground through a
    # paved floor: under the plaza, the porch and the square the ground keeps its own level, just under the paving
    for r_ in (G['plaza'], G['porch'], G['square_r']):
        if r_[0] <= x <= r_[2] and r_[1] <= z <= r_[3]:
            return min(h, park_height_raw(x, z))
    # (round 39, the user: the gravel at the plaza's east corner "doesn't go all the way and then under the paving": the
    # lawn rising just outside the plaza came up through its paving's edge as a strip of grass, over the gravel's start)
    # round the plaza the ground eases down to its level over the last 2 m
    pd_ = rect_d(x, z, G['plaza'])
    if 0.0 < pd_ < 2.0:
        h = min(h, 6.03 - 0.16 + 0.2 * pd_)                # (its edge 13 cm under the paving's top, so the gravel
                                                         #  laid on it starts below the paving, not beside a grass lip)
    return h


_PP = []


def prof_h(prof, t):
    """A path's level t of the way along it (0..1), from its profile's evenly spaced heights."""
    hs = prof[1]
    f = max(0.0, min(1.0, t)) * (len(hs) - 1)
    i = min(int(f), len(hs) - 2)
    return hs[i] + (hs[i + 1] - hs[i]) * (f - i)


def _park_profiles():
    """[(path points, its heights evenly along it)] for the park's paths, worked out once: a footpath an even climb
    between its ends; (round 35, PATH_RULES A4) the two carriage roads level across too, following the hill's own lie
    along them (smoothed over 12 m, no steeper than 0.25), their ends on the paths they meet."""
    if _PP:
        return _PP

    def end_h(e):
        G_ = GUELL
        # (round 35, PATH_RULES B2: a path that ends on paving meets it at the paving's own level, no lip)
        for r_, ph_ in ((G_['plaza'], 6.03), (G_['porch'], 9.03), (G_['square_r'], G_['square_h'] + 0.04)):
            if r_[0] - 0.05 <= e[0] <= r_[2] + 0.05 and r_[1] - 0.05 <= e[1] <= r_[3] + 0.05:
                return ph_
        hh = park_height_raw(*e)
        for prof in _PP:                                   # (starting on a path already laid: its height there)
            d, t, _ = _seg_near(e[0], e[1], prof[0])
            if d < 2.0:
                return prof_h(prof, t)
        return hh
    def on_laid(e):
        return any(_seg_near(e[0], e[1], prof[0])[0] < 2.0 for prof in _PP)
    for i_ in GRADED_PATHS:
        P_ = PARK_PATHS[i_]
        # (round 35, PATH_RULES A3/A4: where it leaves another path, it keeps that path's level for its first 2.5 m — a
        # landing — so the path it leaves stays level across at the join; then the even climb)
        L_ = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(P_, P_[1:]))
        h0, h1 = end_h(P_[0]), end_h(P_[-1])
        l0 = min(2.5, L_ * 0.25) if on_laid(P_[0]) else 0.0
        l1 = min(2.5, L_ * 0.25) if on_laid(P_[-1]) else 0.0
        n_ = max(2, int(L_ * 2))
        hs = []
        for k in range(n_ + 1):
            u = L_ * k / n_
            f = 0.0 if u <= l0 else (1.0 if u >= L_ - l1 else (u - l0) / max(1e-6, L_ - l0 - l1))
            hs.append(h0 + (h1 - h0) * f)
        _PP.append((P_, hs))
    for i_ in [k for k in range(len(PARK_PATHS)) if k not in GRADED_PATHS]:
        P_ = PARK_PATHS[i_]
        L_ = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(P_, P_[1:]))
        n_ = max(2, int(L_))
        pts_ = []
        for k in range(n_ + 1):
            u = L_ * k / n_
            acc = 0.0
            for a, b in zip(P_, P_[1:]):
                s_ = math.hypot(b[0] - a[0], b[1] - a[1])
                if acc + s_ >= u - 1e-9:
                    f = (u - acc) / s_ if s_ else 0.0
                    pts_.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
                    break
                acc += s_
            else:
                pts_.append(P_[-1])
        raw = [park_height_raw(*q) for q in pts_]
        hs = [sum(raw[max(0, k - 6):k + 7]) / len(raw[max(0, k - 6):k + 7]) for k in range(len(raw))]
        hs[0], hs[-1] = end_h(P_[0]), end_h(P_[-1])
        step = L_ / n_
        for _ in range(3):
            for k in range(1, len(hs) - 1):
                hs[k] = min(max(hs[k], hs[k - 1] - 0.25 * step), hs[k - 1] + 0.25 * step)
            for k in range(len(hs) - 2, 0, -1):
                hs[k] = min(max(hs[k], hs[k + 1] - 0.25 * step), hs[k + 1] + 0.25 * step)
        _PP.append((P_, hs))
    return _PP


def park_height_raw(x, z):
    """Park Güell's ground, three levels a visitor walks between: the gate plaza (6 m), the porch in front of the
    Hypostyle Room at the top of the dragon stairs (9 m), the Nature Square on its roof (15.4 m); between and round
    them, lawns rising gently northwards (never steeper than she can walk)."""
    G = GUELL
    h = park_lawn(x, z)                                                             # the lawns
    # (round 33, the user: "The hill below 'Casa Museu Gaudí' should be walkable") where the lawn lies lower than the
    # house's level, the ground falls away from it at an even 0.2, a graded apron, until it meets the lawn — kept east of
    # the porch and its side stairs (x 127), whose paving stands on its own ground
    G = GUELL
    dm = rect_d(x, z, G['museu_r'])
    if dm > 0.0:
        h = h + smooth(127.0, 142.0, x) * max(0.0, G['museu_h'] - 0.2 * dm - h)
    # (round 26: the plaza, the porch and the square wear drawn planes with skirts (north_build), and the game walks
    # their 'flats': the terrain under them sits 0.3 lower, so it can never poke up through the sand)
    for r, top, edge in ((G['plaza'], 5.7, 4.0), (G['porch'], 8.7, 1.5), (G['square_r'], G['square_h'] - 0.3, 1.0),
                         (G['museu_r'], G['museu_h'], 12.0), (G['trias_r'], G['trias_h'], 7.0)):
        if r == G['museu_r'] and h <= top:
            edge = 1.0                     # (round 33: below the house the graded apron already meets its level)
        # (round 34, the play-through: beside the side stairs, outside the porch's ends, its level cut a 2 m slot along
        # the stairs' walls that she fell into and couldn't climb out of: the lawn runs to those walls at its own level)
        if r == G['porch'] and (x < G['side_stairs'][0][0] - 0.2 or x > G['side_stairs'][1][2] + 0.2) and \
                z < G['side_stairs'][0][3]:
            continue
        rd_ = rect_d(x, z, r)
        if r in (G['plaza'], G['porch'], G['square_r']):
            # (round 35, PATH_RULES B2: no lips where the ground meets the paving: 0.3 m under its plane inside, but
            # rising to just under the plane's edge at the edge itself, so the ground outside meets the paving flush)
            top = top + 0.27 * smooth(-1.65, 0.0, rd_)
        k = 1.0 - smooth(0.0, edge, rd_)
        h = h * (1 - k) + top * k
    # (round 24) the Turó de les Tres Creus, the calvary: a low rise in the park's north-west, gentle enough to walk up
    # anywhere, its top a lookout over the park, the city and the sea
    cx_, cz_ = G['calvari']
    h += 3.5 * (1.0 - smooth(3.5, 26.0, math.hypot(x - cx_, z - cz_)))
    # (round 25) Casa Larrard on a level of its own
    k = 1.0 - smooth(0.0, 6.0, rect_d(x, z, G['larrard_r']))         # (round 34: over 6 m, not 3: a bare bank)
    h = h * (1 - k) + G['larrard_h'] * k
    # the viaducts: the path on each level along it, from the lawn at one end to the lawn at the other; on its downhill
    # side the ground drops away below the columns, to a lower walk, until the hillside itself is lower
    for line in VIADUCTS.values():
        d, t, sd = _seg_near(x, z, line)
        if d > 9.0:
            continue
        l0 = park_lawn(*line[0])
        l1 = park_lawn(*line[-1])
        lev = l0 + (l1 - l0) * t
        k = 1.0 - smooth(2.4, 3.4, d)
        h = h * (1 - k) + lev * k
        # (round 33: no trench any more beside the viaducts' roads — it left wedges and stubs: north_build.py)
    h = gallery_ground(x, z, h)
    # (round 40, PATH_RULES F6, the user: "The paths around the part should be relatively flat, just sloping down the
    # hill. So the green part needs to be steeper") the Austria Gardens, walks and beds, on their own even fall to the
    # south — their east walk climbed 1.5 m across its width onto the bank below the covered walk, their north-west
    # corner tilted up to the calvary's rise; the ground round them meets that fall over 4 m, a steeper bank
    # (laid before the paths are graded, so a path passing by keeps its own even climb, park_height)
    ap_ = aus_plane()
    d_au = rect_d(x, z, ap_[:4])
    if d_au < 4.0:
        pl_ = ap_[4] + (ap_[5] - ap_[4]) * (z - ap_[1]) / (ap_[3] - ap_[1])
        h = pl_ + (h - pl_) * smooth(0.0, 4.0, d_au)
    # the dragon stairs: from the plaza up to the porch
    sr = G['stairs_r']
    # (round 26, the user: "The grass covers the stairs": the ground is a little under the steps, which stand on it; the
    # game walks the steps themselves, scene 'flats', north_build.py)
    if sr[0] <= x <= sr[2] and sr[1] <= z <= sr[3]:
        h = 6.0 + 3.0 * (sr[3] - z) / (sr[3] - sr[1]) - 0.45
    # (round 25) the side stairs: from the porch's ends (9 m) up to the square (its height)
    for sr in G['side_stairs']:
        if sr[0] <= x <= sr[2] and sr[1] <= z <= sr[3]:
            h = 9.0 + (G['square_h'] - 9.0) * min(1.0, (sr[3] - z) / (sr[3] - G['stairs_top_z'])) - 0.45
    return h


def park_lawn(x, z):
    """The park's lawns alone, before anything is levelled for its buildings and paths: rising gently northwards.
    (round 34, the user's aerial view: the square backs onto the hill — behind it, and behind the Casa Museu, the
    ground rises 4 m at once to the covered walk's roof, then on up to Casa Trias; not west of the square, over the
    Austria Gardens and the calvary, and not right by the wall, where the gates and the road outside keep their level.)"""
    h = 6.0 + 10.0 * smooth(-146.0, -200.0, z) + 4.0 * smooth(-200.0, -236.0, z)
    if z < -196.0 and x > 78.0:
        extra = 4.5 * smooth(-198.0, -206.0, z) + 3.5 * smooth(-206.0, -240.0, z) - 4.0 * smooth(-200.0, -236.0, z)
        # (round 34, the walk round: it fell back the 4 m within 5 m of the wall, a bare cliff above the top road —
        # eased away over 15 m now)
        h += extra * smooth(80.0, 88.0, x) * (1.0 - smooth(0.52, 0.9, park_r(x, z)))
    return h


def gallery_ground(x, z, h, floor_only=False):
    """(round 34) the covered walk's ground: its floor level along the lower walk (to just behind its wall's line, so
    the height grid's slope up to the hill is hidden behind the wall); behind it the hill at the roof's level, out to
    the roof walk's far side, then easing back to the hill's own lie. Past its ends the hill eases back over 4 m."""
    s, t, beyond, fl = gallery_where(x, z)
    if s < -GALLERY['out'] - 2.0 or s > 16.0 or beyond > 6.0:
        return h
    wl = 1.0 - smooth(0.0, 9.0, beyond)                 # (round 34, first look: a bare bank at its ends — eased over 9 m)
    if s <= GALLERY['wall'] + 1.8:                    # (the height grid's samples are 1.65 m apart)
        # (round 34, the play-through: she was stopped at its west end along the wall — the floor eased into the hill
        # there. Level a metre past each end now, then easing over 3 m to the path that carries on)
        k = (1.0 - smooth(-GALLERY['out'] - 0.3, -GALLERY['out'] - 1.5, s)) * (1.0 - smooth(1.0, 4.0, beyond))
        return h * (1 - k) + fl * k
    if floor_only:
        return h
    top = fl + GALLERY['roof']
    # (level with the roof for 3 m behind it, cut or filled, so she steps straight off it onto the hill)
    hb = top if s < GALLERY['deck_in'] + 3.0 else top + (h - top) * smooth(GALLERY['deck_in'] + 3.0, 14.0, s)
    if beyond > 0.0:
        # (round 34, the walk round: past its ends the hill rose straight up beside the paths, a bare sand cliff;
        # there it steps back from the path as it goes on, and climbs to the roof's level over 6 m, a grassy bank)
        s0 = GALLERY['wall'] + 1.8 + beyond * 0.8
        r_ = smooth(0.0, 5.0, beyond)                    # (and eases down to that over 5 m: no cliff along its end)
        hb = hb * (1 - r_) + min(hb, fl + (top - fl) * smooth(s0, s0 + 6.0, s)) * r_
    return h * (1 - wl) + hb * wl


def hill_east(x, z):
    """Gràcia and Park Güell: a gentle rise (Gràcia), the park on its low hill, a steeper one behind."""
    z0 = FOOT_Z + 6
    if z > z0:
        return 0.05
    d = z0 - z
    # (round 26: a little steeper through Gràcia, 13.5%, so Carrer de Larrard arrives at the gate plaza's level without a
    # bank across the forecourt (the plaza is 6 m up; she can't walk up more than 27%))
    gzn = GRACIA_ZONE
    flat = (1.0 - smooth(0.0, 8.0, rect_d(x, z, gzn)))
    h = 0.11 * d * smooth(0, 30, d)                          # the gentle rise round the village
    if flat > 0.0:
        # (round 26, the user: "Once you get up to the top, the pavement should be flat… How would someone push a pram
        # along it?") the village is terraced: its two streets along the hill are level, and so is the square (a
        # sunken terrace between them, with steps up and down); the lanes and Carrer de Larrard take the climb in
        # ramps between, level again where they cross the streets
        # (round 36, H6.7: the Plaça de la Vila is no longer a sunken terrace with walls and steps: an open square on
        # the ground's own slope between the two streets, as the lanes beside it)
        hv = gracia_profile(z)
        h = h * (1 - flat) + hv * flat
    r = park_r(x, z)
    w = 1.0 - smooth(0.92, 1.25, r)                          # inside the park's wall: its own ground
    ph_ = park_height(x, z)
    h = h * (1 - w) + ph_ * w
    # (round 40, PATH_RULES G5: the whole-park walk check found her stuck at the wall's inner foot, north-east and east:
    # where the land outside is lower, the blend sank the park's last 3 m into a ditch along the wall, too steep to climb
    # out of) inside the wall the ground never sags below the park's own: the wall holds the step
    # (round 40, the user at the Glòria gate: "this gate is inaccessible… make it so that the path is smooth. Both eastern
    # entrances need to be checked") but not at a gateway, where the path comes in from the road outside at the road's
    # level: there the ground eases as before, the hold fading in from 4 m to 9 m from the gate
    if r < 1.0:
        dg_ = min(math.hypot(x - gx_, z - gz_) for gx_, gz_ in list(GUELL['side_gates'].values()) + [PARK_GATE])
        hold_ = smooth(4.0, 9.0, dg_)
        if hold_ > 0.0 and ph_ - 0.1 > h:
            h = h + (ph_ - 0.1 - h) * hold_
    behind = smooth(-236, -300, z) * (1 - w)                 # the hill behind the park, up to the ridge
    # (round 25: no higher than the funfair's hilltop: the church stands on the highest point, as on the real Tibidabo)
    h = h + (45 * smooth(-236, -420, z) - 10 * smooth(-400, -470, z)) * smooth(-230, -300, z)
    # (round 26: the Collserola ridge carries on east of the funfair's hill behind the park, nearly as high, so the
    # skyline from the city doesn't drop away beside the church)
    h = h + 30.0 * smooth(-250, -340, z) * (1 - w)
    # (round 26: no lumps under Gràcia's streets: they climb evenly, as streets do)
    h = h + bumps(x, z) * 0.6 * smooth(0, 25, d) * (1 - w) * (1.0 - flat)
    top_ = gracia_top_h(x, z)
    if top_ is None:
        return h
    return h * (1.0 - top_[1]) + top_[0] * top_[1]


def height_base(x, z):
    # (round 26, the user, from La Rambla: "you can see the hill just drop away to the right") the two hills blend over
    # a narrow band only beside the village (which must sit on the gentle rise alone); behind the park the band is wide,
    # so the big hill's flank is a long slope and not a step
    t = smooth(-165.0, -250.0, z)
    x0 = EAST_X[0] * (1 - t) - 60.0 * t
    x1 = EAST_X[1] * (1 - t) + 70.0 * t
    w = smooth(x0, x1, x)
    return hill_west(x, z) * (1 - w) + hill_east(x, z) * w


_HC = {}
HILL_R = (-238.0, -296.0, -42.0, -100.0)          # where the hillside is shaped round the path (x0, z0, x1, z1)
HILL_ST = 2.0


def _hill_fit():
    """The hillside the path climbs, shaped round it: a smooth surface (a membrane, Laplace's equation solved on a
    2 m grid) held at the path's own heights all along it and at the plain slope round the edges, so the path, at
    its steady gradient, always lies on the hill and never in a trench or on a dyke."""
    if _HC:
        return _HC
    import numpy as np
    x0, z0, x1, z1 = HILL_R
    nx, nz = int((x1 - x0) / HILL_ST) + 1, int((z1 - z0) / HILL_ST) + 1
    X = x0 + np.arange(nx) * HILL_ST
    Z = z0 + np.arange(nz) * HILL_ST
    H = np.array([[height_base(x, z) for x in X] for z in Z])
    fixed = np.zeros_like(H, bool)
    fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True
    pts, _ = path_points()
    for (x, z, h) in pts:
        i, j = int(round((x - x0) / HILL_ST)), int(round((z - z0) / HILL_ST))
        if 0 < i < nx - 1 and 0 < j < nz - 1:
            H[j, i] = h
            fixed[j, i] = True
    # (round 25) and the banks' feet and tops: on the uphill side the top of the bank above the verge, on the downhill
    # side the foot of the bank below the railing (where the hillside is steep enough to have them), so the hillside
    # between the bends is laid gently between those instead of between the paths themselves
    acc, side_fix = {}, []
    # (which side is uphill: by the hillside laid round the path alone, first)
    H0 = H.copy()
    for _ in range(4000):
        avg = (np.roll(H0, 1, 0) + np.roll(H0, -1, 0) + np.roll(H0, 1, 1) + np.roll(H0, -1, 1)) / 4.0
        H0 = np.where(~fixed, avg, H0)

    def h0(x, z):
        fi, fj = min(max((x - x0) / HILL_ST, 0), nx - 1.001), min(max((z - z0) / HILL_ST, 0), nz - 1.001)
        i, j = int(fi), int(fj)
        ax, az = fi - i, fj - j
        return (H0[j, i] * (1 - ax) + H0[j, i + 1] * ax) * (1 - az) + (H0[j + 1, i] * (1 - ax) + H0[j + 1, i + 1] * ax) * az
    for k in range(2, len(pts) - 2, 2):
        x, z, h = pts[k]
        dx, dz = pts[k + 2][0] - pts[k - 2][0], pts[k + 2][1] - pts[k - 2][1]
        n = math.hypot(dx, dz) or 1.0
        nx_, nz_ = -dz / n, dx / n
        for sg in (1, -1):
            hb = h0(x + nx_ * sg * 5, z + nz_ * sg * 5)
            if hb > h + 1.0 and GLADE_R[0] < x < GLADE_R[2] and GLADE_R[1] < z < GLADE_R[3]:
                e, t = BANK_W + 3.0, h + VERGE_RISE * 3.0 + BANK * BANK_W          # (E3: the glade as in round 34)
            elif hb > h + 1.0:
                e, t = UP_BANK_W + VERGE, h + VERGE_RISE * VERGE + UP_BANK * UP_BANK_W
            elif hb < h - 1.0:
                e, t = 0.2 + BANK_W, h - BANK * BANK_W
            else:
                continue
            d = EDGE + e
            side_fix.append((x + nx_ * sg * d, z + nz_ * sg * d, t))
    for (x, z, t) in side_fix:
        if min(math.hypot(x - q[0], z - q[1]) for q in pts[::3]) < EDGE + 1.0:
            continue                                     # (on another stretch of the path: the path wins)
        i, j = int(round((x - x0) / HILL_ST)), int(round((z - z0) / HILL_ST))
        if 0 < i < nx - 1 and 0 < j < nz - 1 and not fixed[j, i]:
            acc.setdefault((j, i), []).append(t)
    for (j, i), ts in acc.items():
        H[j, i] = sum(ts) / len(ts)
        fixed[j, i] = True
    free = ~fixed
    for _ in range(4000):
        avg = (np.roll(H, 1, 0) + np.roll(H, -1, 0) + np.roll(H, 1, 1) + np.roll(H, -1, 1)) / 4.0
        H = np.where(free, avg, H)
    _HC.update({'H': H, 'nx': nx, 'nz': nz})
    return _HC


def fair_level(x, z, h):
    """(round 34) the funfair's plateau level at its own height, inside its retaining wall (1.8 m thick); outside it, a
    terrace wall about 4 m high and below that a steep wooded bank down to the hillside's own lie — not a sheer drop
    of up to 28 m (but round the funicular's portal, whose terraced masonry is the plateau's face there)."""
    fx_ = max(FAIR[0] - x, 0.0, x - FAIR[2])
    fz_ = max(FAIR[1] - z, 0.0, z - FAIR[3])
    d_ = math.hypot(fx_, fz_)
    if d_ > 0.0 and abs(x - CABLE_TOP[0]) < 3.5 and z > FAIR[3]:
        return h                                         # (the funicular's portal: its mouth open, not filled)
    kf = 1.0 - smooth(0.0, 1.2, d_)
    h = h * (1 - kf) + FAIR_H * kf
    if d_ > 0.0 and not (abs(x - CABLE_TOP[0]) < 21.5 and z > FAIR[3]):
        # (round 35, PATH_RULES E4, the user: "There is a sharp drop, it should be smaller") a 2.5 m terrace wall, and
        # below it a bank at 0.6 that eases into the hillside over 16 m (it was 4 m and then 0.9 all the way down)
        kb = 1.0 - smooth(10.0, 16.0, d_)
        h = max(h, h * (1 - kb) + (FAIR_H - 2.5 - 0.6 * max(0.0, d_ - 1.8)) * kb)
    return h


# (round 35, the user: "The slope should continue up at Tibidabo, so that it doesn't drop off and create a ridge.
# There will be a flat forest there, which is fine, if she runs into the forest, eventually she will get to a "hill"
# that she can't go up. that will go along to join the rope that comes up around the first bend") North of the top leg,
# west of the funfair, the bank beside the path stood as a 2 m ridge with a hollow behind it. Now the ground rises
# from the path at a walkable slope to a flat wood at the plateau's level, closed off by a steep rise (TOP_HILL) whose
# foot runs from the back of the funfair round the west to the end of the rope round the top-left hairpin.
TOP_HILL = [(-205.5, -269.2), (-209.5, -276.0), (-211.5, -288.0), (-206.0, -303.0), (-190.0, -316.0), (-165.0, -322.0),
            (-135.0, -324.0), (-108.5, -323.5)]
TOP_WOOD_H = 78.0                    # the wood's floor: the funfair's level
TOP_HILL_RISE = 4.5                  # the steep rise at its edge (over 3 m: no walking up it)
_TF = {}


def _seg_d(px, pz, a, b):
    ax, az, bx, bz = a[0], a[1], b[0], b[1]
    L2 = (bx - ax) ** 2 + (bz - az) ** 2 or 1e-9
    t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (pz - az) * (bz - az)) / L2))
    return math.hypot(px - ax - t * (bx - ax), pz - az - t * (bz - az))


def top_wood(x, z, h):
    if not (-250.0 < x < -100.0 and -345.0 < z < -255.0):
        return h
    if not _TF:
        pts, _ = path_points()
        leg = [p for p in pts if p[1] < -268.6 and p[0] < -104.0]
        _TF['leg'] = leg
        _TF['poly'] = [(q[0], q[1]) for q in TOP_HILL] + [(p[0], p[1]) for p in reversed(leg)]
    leg, poly = _TF['leg'], _TF['poly']
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, zi, xj, zj = poly[i][0], poly[i][1], poly[j][0], poly[j][1]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / ((zj - zi) or 1e-9) + xi:
            inside = not inside
        j = i
    db = min(_seg_d(x, z, a, b) for a, b in zip(TOP_HILL, TOP_HILL[1:]))
    # the path's height and distance (the top leg's nearest point)
    best = min(leg, key=lambda p: (p[0] - x) ** 2 + (p[1] - z) ** 2)
    dp, ph = math.hypot(best[0] - x, best[1] - z), best[2]
    e = max(0.0, dp - EDGE)
    rise = VERGE_RISE * min(e, VERGE) + UP_BANK * min(max(e - VERGE, 0.0), UP_BANK_W) + 0.18 * max(e - VERGE - UP_BANK_W, 0.0)
    wood = min(TOP_WOOD_H, ph + rise)                        # (from the path up to the wood's flat floor)
    if inside:
        return max(h, wood)
    # (round 35, the user: "The slope should continue up at Tibidabo, so that it doesn't drop off and create a ridge")
    # beyond its foot the steep hill: up TOP_HILL_RISE over 3 m, then a broad hilltop easing back into the hillside's
    # own lie over 25 m — a hill, not a thin ridge (it fell back within 12 m: a crest 6 m high west of the hairpin)
    if db < 25.0:
        edge_h = min(TOP_WOOD_H, ph + rise)
        up = edge_h + TOP_HILL_RISE * smooth(0.0, 3.0, db)
        k = 1.0 - smooth(6.0, 25.0, db)
        return max(h, h * (1 - k) + up * k)
    return h


def height(x, z):
    h = height_base(x, z)
    x0, z0, x1, z1 = HILL_R
    if not (x0 < x < x1 and z0 < z < z1):
        # (round 34: and its east end, beyond the fitted hillside, where the two hills' blend had sunk it too)
        return fair_level(x, z, top_wood(x, z, h))
    F = _hill_fit()
    fi, fj = (x - x0) / HILL_ST, (z - z0) / HILL_ST
    i, j = min(int(fi), F['nx'] - 2), min(int(fj), F['nz'] - 2)
    ax, az = fi - i, fj - j
    H = F['H']
    hm = (H[j, i] * (1 - ax) + H[j, i + 1] * ax) * (1 - az) + (H[j + 1, i] * (1 - ax) + H[j + 1, i + 1] * ax) * az
    edge = min(x - x0, x1 - x, z - z0, z1 - z)
    k = smooth(0.0, 12.0, edge)
    h = h * (1 - k) + float(hm) * k
    h = top_wood(x, z, h)
    # (round 34, the play-through: the funfair's southern 30 m — its forecourt, widened south to z -265 — lay inside
    # the hillside fitted round the path, and were smoothed into a slope from 67 to 77 m: she walked 7 m under its
    # paving and its rides, and couldn't climb to Rosalia. Level again at its own height, after the fit, its edge a
    # 2.5 m terrace wall as before)
    h = fair_level(x, z, h)
    # (round 26) a level pad under the funicular's bottom station and its forecourt, after every other shaping
    pad = 1.0 - smooth(6.0, 13.0, math.hypot(x - CABLE_LOW[0], z - CABLE_LOW[1]))
    h = h * (1 - pad) + 0.3 * pad
    # (round 27) the funicular's bed: the ground along the line cut and filled gently to the track's even climb
    # (round 30, the user: no level crossings at all — the walking path never touches the line now, so the track
    # runs in its own shallow cutting the whole way, the cut wide enough that the hillside never bulges over it)
    if not _FP_BUILDING[0] and FUNI_Z1 - 1.5 < z < FUNI_Z0 + 4.0:      # (round 34: on into the portal's mouth)
        d = abs(x - CABLE_LOW[0])
        if d < 7.5:
            fk = 1.0 - smooth(3.6, 7.5, d)
            h = h * (1 - fk) + (funi_profile(min(FUNI_Z0, max(FUNI_Z1, z))) - 0.35) * fk
    return h


# ------------------------------------------------------------------ the winding path up to the funfair
# The user: very long and winding, irregular; it sets off up the hill west-north-west, the second workman at the
# first bend; the ledge with the ball in the crook of a bend. Each leg climbs across the slope, so it is gentle
# though the hill is steep; the bends are hairpins. Control points (x, z), smoothed into a curve.

# The user's own drawing of it (round 22, over version A's picture: "a stylised view of the path, you don't have to
# follow it exactly"), read off the picture: it sets off west-north-west to workman 2, then zigzags up the west
# side of the hill in hairpins of all sizes, out to the far west (past the old map edge: the world grows), the
# ball's ledge in the crook of the big loop at the top left, and comes onto the funfair from its west side.
# (round 30, the user: the path's foot joins the pavement. Round 31, the user: dirt never lies over paving — the
# worn ribbon ends right where the paving begins, the grass apron lapping the paving's edge beside it)
# (round 40, the user: "the path… sort of hooks around. It should simply curve around to where it joins… it doesn't
# have to join at the footpath. So you can move the end of it a bit to the right": it came down east-south-east and
# turned hard south onto the pavement) one easy sweep down to the pavement 7 m further east
# (and the user: "The dirt path goes on top of the footpath when it should end at it without any visible gap": its first
# point lay 0.9 m onto the pavement) it ends at the pavement's back edge, z -102.35, coming in square to it
PATH_CTRL = [(-86.0, -102.35), (-86.05, -103.7), (-88.6, -106.2), (-99.0, -109.5), (-112.5, -112.8), (-133.3, -120.6), (-150.6, -125.7), (-165.3, -130.9),
             # (the user's second drawing, over the first: the first bend swings much further west)
             (-180.2, -136.4), (-194.0, -142.3), (-207.7, -148.3), (-216.5, -152.6), (-213.6, -155.2), (-205.7, -157.2),
             (-194.0, -159.2), (-179.2, -162.5), (-160.1, -164.0), (-156.1, -166.1), (-159.6, -168.1), (-173.1, -170.2),
             (-186.9, -173.0), (-193.5, -176.8), (-194.2, -181.6), (-190.0, -186.1), (-180.0, -186.5), (-167.9, -185.8),
             (-154.1, -188.0),
             # (and the middle, re-spaced: out east toward the funicular — round 30: the hairpin bends at the
             # line's fence and never crosses it — back west, a shorter hairpin east, west again)
             (-140.0, -188.9), (-107.6, -191.4),
             # (round 35, the user: the funicular bend "is choppy, it should be smooth": a round hairpin now, 6.2 m
             # about (-79, -199), its tip where the old one was, by the line's fence)
             (-79.0, -192.8), (-74.62, -194.62), (-72.8, -199.0), (-74.62, -203.38), (-79.0, -205.2),
             (-90.0, -205.6), (-115.5, -209.6), (-133.1, -213.6), (-140.6, -217.6), (-138.0, -221.1), (-123.3, -224.3),
             (-97.8, -225.9), (-93.5, -227.5), (-95.9, -229.4), (-115.5, -231.8), (-137.1, -237.4), (-153.7, -242.9),
             (-167.9, -245.6), (-180.0, -250.8), (-197.3, -256.7), (-202.8, -263.3), (-200.4, -270.2), (-192.1, -274.5),
             (-178.3, -275.7), (-161.0, -278.5), (-141.9, -282.0), (-122.9, -285.9), (-105.6, -290.4)]
# (round 41, the user at the funfair's gateway: "The path can be moved slightly to the right in this picture. So that
# it's not so close to the edge" — its end 2 m north, away from the plateau's south-west corner)
LOOKOUT = None
PATH_W = 2.4
WORKMEN = [(-93.5, -105.5), (-166.5, -131.5)]          # 1 blocks the way; 2 at the first bend
WORK_SITE = []                                         # (round 35: the site's level bay, set once the path is known)
GLADE_R = (-192.0, -274.0, -147.0, -244.0)            # (round 35, PATH_RULES E3) the ball's glade: no uphill bank
BALL_LEDGE = (-172.2, -261.5)                          # in the crook of the big loop at the top left (the user's mark)
# (round 25, the user: "ensure the ball is in a deep part of the forest where the floor is dark… It should look like the
# ball has fallen and was stopped by a tree (then rolled back a bit so it isn't against the tree). It shouldn't look
# placed, but should not be hidden by ferns") where it lies, just uphill of the tree that stopped it (north_build.py)
BALL = (-171.4, -262.1)
SLIDE = [(-171.3, -273.0), (-172.2, -261.5), (-170.3, -251.8)]   # off the leg above, down to the ledge, then on to the leg below


def catmull(pts, n=8):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def path_points():
    """The path's centre line, every metre or so, with its height: [(x, z, h)]. It climbs at one steady gradient
    from its foot to the plateau (the user: "it should follow a regular gradient"), and wanders a little from side to
    side as a worn path does (never a ruler-straight line)."""
    pts = catmull(PATH_CTRL, 10)
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    out = []
    for i, (p, l) in enumerate(zip(pts, L)):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dz) or 1.0
        w = 0.45 * math.sin(l * 0.13) + 0.3 * math.sin(l * 0.047 + 1.3)        # (the wander, metres to the side)
        w *= min(1.0, l / 6.0, (L[-1] - l) / 6.0)
        out.append((p[0] - dz / n * w, p[1] + dx / n * w, 0.05 + (FAIR_H - 0.05) * l / L[-1]))
    return out, L[-1]


def path_at(L_want):
    """The path's centre (x, z) and its heading (dx, dz), L_want metres up from its foot."""
    pts, _ = path_points()
    acc = 0.0
    for i in range(1, len(pts)):
        acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        if acc >= L_want:
            break
    a, b = pts[max(0, i - 3)], pts[min(len(pts) - 1, i + 3)]
    n = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    return pts[i][0], pts[i][1], (b[0] - a[0]) / n, (b[1] - a[1]) / n


# (round 24) the barrier stands a little below the first bend, not at the foot: the first stretch, under the first trees,
# is open from the start; Toni still works at the bend above it. (round 26, the user: "Put the workmen closer to the
# bottom") the barrier 14 m up from the gateway, Toni's work site just above it, beside the path
WORK_L = 21.0            # (round 30: the foot's new leg down to the pavement adds ~7 m; the barrier stays put)
# (round 40: the foot re-laid, the barrier and the workmen stay where they were — at the point on the path nearest
# the old place, (-108.16, -111.64))
_wp, _ = path_points()
_wl = 0.0
_wbest = (1e9, 0.0)
for _i in range(1, len(_wp)):
    _wl += math.hypot(_wp[_i][0] - _wp[_i - 1][0], _wp[_i][1] - _wp[_i - 1][1])
    _wd = math.hypot(_wp[_i][0] + 108.16, _wp[_i][1] + 111.64)
    if _wd < _wbest[0]:
        _wbest = (_wd, _wl)
WORK_L = _wbest[1]
WORKMEN[0] = path_at(WORK_L)[:2]


def path_width(l):
    """A worn path: wider and narrower as it goes."""
    return PATH_W + 0.35 * math.sin(l * 0.21) + 0.25 * math.sin(l * 0.073 + 0.8)


# ------------------------------------------------------------------ the funfair, as on the real summit
# (the Temple del Sagrat Cor at the back, on its crypt; the Panoramic Area's rides in front of it: the Giradabo wheel,
# the Talaia, the Avió out over the edge, the Carrusel, the old theatre that is the Museu d'Autòmats)
SAGRAT = (-63.0, -309.0)                 # the church's centre (its front faces south, over the city), set back
# (round 41, the user: "She cuts into the ground now. You just need to lift up the Ferris wheel a little bit": the
# bottom gondola's tub reached 0.85 m under the funfair's floor, her seat under the boarding platform; 1.6 m higher, the
# tub clears the platform)
WHEEL = {'x': -95.0, 'z': -283.5, 'r': 10.5, 'hub': 13.6, 'n': 12}   # (the user: "slightly bigger"; was 4.6 m)
TALAIA = (-40.0, -293.0)
AVIO = (-37.0, -281.0)
CARRUSEL = (-93.0, -309.0)          # (round 35: in the plateau's north-west corner, beside the church)
AUTOMATA = (-37.5, -307.0)

# ------------------------------------------------------------------ the ground as built: the natural slope, with the
# path's bench cut into it (flat across, at the path's height, blending back over 2 m), and the ball's ledge

_PG = {}


def _path_grid():
    if not _PG:
        pts, _ = path_points()
        _PG['pts'] = pts
        g = {}
        for i, (x, z, h) in enumerate(pts):
            g.setdefault((int(x // 6), int(z // 6)), []).append(i)
        _PG['g'] = g
        # the ledge: halfway between the path's heights on the legs above and below it
        lx, lz = BALL_LEDGE
        near = sorted(pts, key=lambda p: (p[0] - lx) ** 2 + (p[1] - lz) ** 2)
        hs = [p[2] for p in near[:40]]
        _PG['ledge_h'] = (min(hs) + max(hs)) / 2
    return _PG


def _on_line(x, z, i):
    """(round 35, PATH_RULES A7) the distance to the path's middle line near point i and its height there, taken on
    the line between the points (not at the nearest point: its height stepped from point to point, and the finer
    ground drew those steps across the path as shallow stairs)."""
    pts = _path_grid()['pts']
    best = None
    for j in (i - 1, i):
        if j < 0 or j + 1 >= len(pts):
            continue
        a, b = pts[j], pts[j + 1]
        dx, dz = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dz * dz or 1e-9
        t = max(0.0, min(1.0, ((x - a[0]) * dx + (z - a[1]) * dz) / L2))
        d = math.hypot(x - a[0] - dx * t, z - a[1] - dz * t)
        if best is None or d < best[0]:
            best = (d, a[2] + (b[2] - a[2]) * t)
    return best if best is not None else (math.hypot(x - pts[i][0], z - pts[i][1]), pts[i][2])


def path_near(x, z):
    """(distance to the path's centre line, the path's height there), on the line through the nearest points."""
    P = _path_grid()
    best, bi = 1e9, None
    cx, cz = int(x // 6), int(z // 6)
    for gx in (cx - 1, cx, cx + 1):
        for gz in (cz - 1, cz, cz + 1):
            for i in P['g'].get((gx, gz), ()):
                p = P['pts'][i]
                d = (p[0] - x) ** 2 + (p[1] - z) ** 2
                if d < best:
                    best, bi = d, i
    if bi is None:
        return math.sqrt(best), 0.0
    return _on_line(x, z, bi)


# (round 25, the user: "only have the railing on the lower side… The upper side can be more accessible (i.e., on the
# green), and the invisible barrier is only when it is steep. The upper and lower side should be steeper to accommodate
# this; that might mean that the areas in between that the user can't go are not as steep") the path's cross-section:
# on its uphill side a strip of gentle green she can walk on (VERGE), then a bank too steep to climb (BANK) up to the
# hillside; on its downhill side a short lip under the railing, then a bank as steep down. The banks take up the height
# near the path, so the hillside between the bends is gentler.
# (round 35, docs/PATH_RULES.md C3, the user: the 2 m strip "is too wide… you can just bring out the hill… steep enough
# for her not to walk up, then gentle incline then brief increase in slope before we reach the fence") uphill: a
# narrow green edge, then a bank just too steep to walk up (UP_BANK over UP_BANK_W, held as a floor, so it is there
# even where the hillside would be gentle), then the hillside, gently, to the bank below the next leg's lip
VERGE = 0.5              # metres of green past EDGE (so about 0.85 m beside the drawn track; was 3.0, then 2.0)
UP_BANK = 0.6            # its rise per metre: past her limit (north.gd MAX_UP 0.30), not a cliff
UP_BANK_W = 2.2          # its width (so about 1.3 m high)
VERGE_RISE = 0.14        # its slope (she can walk up 0.27: north.gd MAX_UP)
BANK = 1.3               # the banks above the verge and below the railing, rise per metre
BANK_W = 1.6             # their width, metres (so about 2 m high)
EDGE = PATH_W / 2 + 0.25


def path_runs_near(x, z, R=14.0):
    """For each stretch of the path within R metres of (x, z) (a hairpin's two legs are two stretches), the distance to
    its nearest point and the path's height there: [(d, h)]."""
    P = _path_grid()
    cx, cz = int(x // 6), int(z // 6)
    idx = []
    for gx in range(cx - 3, cx + 4):
        for gz in range(cz - 3, cz + 4):
            idx.extend(P['g'].get((gx, gz), ()))
    idx.sort()
    out, best, prev = [], None, None
    for i in idx:
        p = P['pts'][i]
        d2 = (p[0] - x) ** 2 + (p[1] - z) ** 2
        if d2 > R * R:
            continue
        if prev is not None and i - prev > 3 and best is not None:
            out.append(best)
            best = None
        if best is None or d2 < best[0]:
            best = (d2, p[2], i)
        prev = i
    if best is not None:
        out.append(best)
    return [_on_line(x, z, i) + (i,) for a, b, i in out]


_UP = []


def up_side(i):
    """(round 35) which side of path point i the hillside rises on: +1 its left normal's (-dz, dx), -1 the right, 0 too
    level to say. By the fitted hillside (height), 5 m out either side, as _hill_fit's banks are judged."""
    if not _UP:
        pts = _path_grid()['pts']
        for k in range(len(pts)):
            a, b = pts[max(0, k - 2)], pts[min(len(pts) - 1, k + 2)]
            n = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
            nx_, nz_ = -(b[1] - a[1]) / n, (b[0] - a[0]) / n
            x, z, h = pts[k]
            hl, hr = height(x + nx_ * 5, z + nz_ * 5), height(x - nx_ * 5, z - nz_ * 5)
            _UP.append(1 if hl > h + 1.0 and hl > hr else (-1 if hr > h + 1.0 and hr > hl else 0))
    return _UP[i]


def crook_legs(x, z, R=14.0):
    """(round 41) a hairpin's two legs either side of (x, z): the nearest point of the path, and the nearest on the
    far side of (x, z) from it, close along the path (under 60 points: a crook, not two far-off legs); each as
    (distance, height, index), lower first — or None."""
    P = _path_grid()
    cx, cz = int(x // 6), int(z // 6)
    near = []
    for gx in range(cx - 3, cx + 4):
        for gz in range(cz - 3, cz + 4):
            for i in P['g'].get((gx, gz), ()):
                p = P['pts'][i]
                d2 = (p[0] - x) ** 2 + (p[1] - z) ** 2
                if d2 < R * R:
                    near.append((d2, i))
    if not near:
        return None
    d1, i1 = min(near)
    p1 = P['pts'][i1]
    far = [(d2, i) for d2, i in near if abs(i - i1) >= 6 and abs(i - i1) < 60 and
           (P['pts'][i][0] - x) * (p1[0] - x) + (P['pts'][i][1] - z) * (p1[1] - z) < 0]
    if not far:
        return None
    d2, i2 = min(far)
    a, b = _on_line(x, z, i1) + (i1,), _on_line(x, z, i2) + (i2,)
    if abs(a[1] - b[1]) < 0.2:
        return None
    return (a, b) if a[1] < b[1] else (b, a)


def side_of(i, x, z):
    """+1 if (x, z) lies on path point i's left (normal (-dz, dx)), -1 its right."""
    pts = _path_grid()['pts']
    a, b = pts[max(0, i - 2)], pts[min(len(pts) - 1, i + 2)]
    return 1 if (-(b[1] - a[1])) * (x - pts[i][0]) + (b[0] - a[0]) * (z - pts[i][1]) > 0 else -1


def uphill_side(x, z):
    """Is (x, z) above the path nearest it (on its uphill side)?"""
    d, ph = path_near(x, z)
    return height(x, z) > ph


_RG = {}


def road_level(x, z):
    """(distance to the Carretera del Carmel, its height there.) (round 34, the user: "I would also like the path
    around the side to not have a ditch (so that whole path needs to be lowered)": graded evenly from end to end it
    rode up to 4 m above the hillside in the middle, a ditch between it and the park wall. It follows the hill's own
    lie now, smoothed over 12 m either way and never steeper than 0.16, its two ends where they were.)"""
    if not _RG:
        pts, side = [], []
        for a, b in zip(CARMEL_ROAD, CARMEL_ROAD[1:]):
            L_ = math.hypot(b[0] - a[0], b[1] - a[1])
            n_ = max(1, int(L_))
            for k in range(n_):
                pts.append((a[0] + (b[0] - a[0]) * k / n_, a[1] + (b[1] - a[1]) * k / n_))
                side.append(((b[1] - a[1]) / L_, -(b[0] - a[0]) / L_))
        pts.append(CARMEL_ROAD[-1])
        side.append(side[-1])
        # (round 34, the quick tests: from the road she must still run right up to the park wall — the road takes the
        # level of the ground along its wall side, 4.5 m over, not of the hillside under its middle: no ditch on that
        # side, no bank either; where the hill falls away outside, the road stands on its own shoulder)
        # (its two ends where they were: at the main gate it meets the gate's own ground — taken from the plaza beside
        # it, the gateway sank 0.15 m and left a lip at the plaza's paving)
        raw = [height(*p) if i in (0, len(pts) - 1)
               else height(p[0] + s_[0] * 4.5, p[1] + s_[1] * 4.5) for i, (p, s_) in enumerate(zip(pts, side))]
        sm = []
        for i in range(len(raw)):
            w = raw[max(0, i - 12):i + 13]
            sm.append(sum(w) / len(w))
        sm[0], sm[-1] = raw[0], raw[-1]
        # (the side gates stand above the hillside outside them — the Glòria gate 4 m: the road climbs to meet each
        # gate's path, 0.6 m below the gateway, and eases back down past it — no steeper than 0.16 either way)
        for (gx_, gz_), (tx_, tz_) in (((185.8, -183.0), (180.8, -188.3)), ((176.6, -228.1), (172.0, -227.3))):
            ig = min(range(len(pts)), key=lambda i: math.hypot(pts[i][0] - gx_, pts[i][1] - gz_))
            pin = height(tx_, tz_) - 0.6
            for i in range(len(sm)):
                sm[i] = max(sm[i], pin - 0.16 * abs(i - ig))
        for _ in range(3):                                   # (no steeper than 0.16 a metre, either way)
            for i in range(1, len(sm)):
                sm[i] = min(max(sm[i], sm[i - 1] - 0.16), sm[i - 1] + 0.16)
            for i in range(len(sm) - 2, -1, -1):
                sm[i] = min(max(sm[i], sm[i + 1] - 0.16), sm[i + 1] + 0.16)
        # (round 34, the walk round: the crest where it meets the Glòria gate was sharp, the grass poking through the
        # road's surface there: rounded off)
        for _ in range(2):
            sm2 = list(sm)
            for i in range(4, len(sm) - 4):
                sm2[i] = sum(sm[i - 4:i + 5]) / 9.0
            sm = sm2
        _RG.update(prof=sm)
    d, t, _ = _seg_near(x, z, CARMEL_ROAD)
    prof = _RG['prof']
    f = t * (len(prof) - 1)
    i = min(int(f), len(prof) - 2)
    return d, prof[i] + (prof[i + 1] - prof[i]) * (f - i)


def ground(x, z):
    h = height(x, z)
    if 100.0 < x < 195.0 and -240.0 < z < -132.0:
        d, rh = road_level(x, z)
        if d < 9.0:
            k = 1.0 - smooth(ROAD_W / 2 + 0.3, ROAD_W / 2 + 4.5, d)
            h = h * (1 - k) + rh * k
            # (round 34: between the road and the park wall the verge never dips below the road — no ditch)
            if _seg_near(x, z, CARMEL_ROAD)[2] < 0 and d < 7.5:
                h = max(h, rh)
                # (outside the wall the verge runs level to its foot, so she can walk right up to it: the wall holds
                # the park's higher ground behind it)
                # (not under the wall itself: that dug a gully along its inner foot, inside the park)
                if park_r(x, z) >= 1.0:
                    h = rh + 0.04 * max(0.0, d - ROAD_W / 2 - 0.3)
    # (round 35, PATH_RULES B2: no lip at the main gate — the gateway rises to the plaza's paving, 6.03 m, over the
    # 4 m from the forecourt)
    if 101.5 < x < 110.5 and -144.0 < z < -138.5:
        k = smooth(-138.8, -143.0, z) * (1.0 - smooth(1.0, 1.8, max(101.5 + 1.8 - x, x - 110.5 + 1.8, 0.0)))
        h = h * (1 - k) + 6.01 * k
    # (round 39, the user: "fix up the hill so it comes along and joins the stone wall, so Sandra can't get into that
    # area") the closed hill east of Gràcia (gracia_hill) rises from the eastern wood's top edge as a bank she can't
    # climb — 0.55 a metre over 3.3 m, two grid squares (08 #22) — then a gentle shelf (0.05 a metre) until the hill's
    # own rise overtakes it, so no ridge with a hollow behind (08 #32). From the drystone wall's line, where it meets the
    # bank down from the wall, east to the wood's own rise (3 m) at x 186-192. It only ever raises the ground.
    if GRACIA_WALL_X < x < 192.0 and -140.0 < z < GH_EDGE_Z + 0.01:
        e_ = max(0.0, GH_EDGE_Z - z)
        top_ = 0.25 + 0.55 * min(e_, 3.3) + 0.05 * max(0.0, e_ - 3.3)
        if top_ > h:
            h = h + (top_ - h) * (1.0 - smooth(186.0, 192.0, x))
    # (round 40, PATH_RULES G5: the whole-park walk check) between the east side stairs' outer wall and the switchback
    # path's rail the lawn lay 1.5 m under the path, a slot a metre wide she couldn't leave: it runs at the path's level
    ss_ = GUELL['side_stairs'][1]
    if ss_[2] < x < ss_[2] + 2.3 and -172.5 < z < -164.5:
        k_ = 1.0 - smooth(-166.6, -164.6, z)     # (eased back to the lawn's own lie past the porch wall's end: no new drop)
        h = max(h, h + k_ * (ground(ss_[2] + 2.3, z) - h))
    # (round 28: never on the funicular's own bed — the walking path's verge/bank clamp pulled the ground
    # between the two level crossings under the ballast, burying the track; the track's corridor wins there)
    on_funi_bed = abs(x - CABLE_LOW[0]) < 3.6 and FUNI_Z1 + 1.0 < z < FUNI_Z0 + 4.0
    if z < FOOT_Z + 4 and not on_funi_bed:
        runs = path_runs_near(x, z)
        if runs:
            # each stretch of path near: no higher than its verge and bank above it, no lower than its bank below it
            ceil_, floor_ = 1e9, -1e9
            ce_e, fl_e = 0.0, 0.0
            in_glade = GLADE_R[0] < x < GLADE_R[2] and GLADE_R[1] < z < GLADE_R[3]
            vg = 3.0 if in_glade else VERGE          # (round 35, E3: in the glade the edge as it was — she walks in)
            for d, ph, i in runs:
                e = d - EDGE
                c_ = ph + VERGE_RISE * min(max(e, 0.0), vg) + BANK * max(0.0, e - vg)
                f_ = ph - BANK * max(0.0, e - LIP)
                us = up_side(i)
                if us != 0 and side_of(i, x, z) == us and not in_glade:
                    # (C3: the uphill bank, steep enough that she can't walk up it, starting right past the green edge)
                    f_ = max(f_, ph + VERGE_RISE * min(max(e, 0.0), VERGE)
                             + UP_BANK * min(max(e - VERGE, 0.0), UP_BANK_W))
                if c_ < ceil_:
                    ceil_, ce_e = c_, max(e, 0.0)
                if f_ > floor_:
                    floor_, fl_e = f_, max(e, 0.0)
            if floor_ <= ceil_:
                h = min(ceil_, max(floor_, h))
            else:
                # (round 35, the user: "the path and fence go down the hill … Getting past it does not work") two legs
                # too close, one above the other, for a bank at the usual slope between them: the lower leg's ceiling
                # had won, and pulled the upper leg's own surface down by up to 2.7 m. Now each path keeps its level
                # on itself, and between them the bank is steeper, shared out by how far each one is
                w = fl_e / (fl_e + ce_e) if fl_e + ce_e > 1e-6 else 0.0
                h = floor_ * (1.0 - w) + ceil_ * w
            # (round 41, the user, at a hairpin: "can you make it slope with the street? It still looks bumpy") in a
            # hairpin's crook — on the lower leg's uphill side and the higher leg's downhill side, the two close along
            # the path — the ground is one even slope from the lower leg's edge up to the higher leg's lip, not the
            # uphill bank's step, flat and rise
            cl_ = None if in_glade else crook_legs(x, z)
            if cl_ is not None:
                lo_, hi_ = cl_
                us_lo, us_hi = up_side(lo_[2]), up_side(hi_[2])
                if us_lo != 0 and us_hi != 0 and side_of(lo_[2], x, z) == us_lo and side_of(hi_[2], x, z) != us_hi:
                    a_ = max(0.0, lo_[0] - EDGE - 0.3)
                    b_ = max(0.0, hi_[0] - EDGE - LIP)
                    if a_ + b_ > 0.3:
                        ramp_ = lo_[1] + (hi_[1] - lo_[1]) * a_ / (a_ + b_)
                        wk_ = 1.0 - smooth(10.0, 14.0, max(lo_[0], hi_[0]))
                        h = h * (1.0 - wk_) + ramp_ * wk_
        # (round 25: no flattened ledge for the ball any more: it lies on the wood's own slope, against a tree)
        # (round 35, PATH_RULES E3: the full play-through could not reach the ball — the glade between the legs had a
        # bank she couldn't walk up all along the leg below) the glade's own shape: from the top leg its lip and a short
        # bank down (2 m), then one even, gentle slope down to the leg below's edge
        if GLADE_R[0] < x < GLADE_R[2] and GLADE_R[1] < z < GLADE_R[3]:
            lo_r, hi_r = glade_legs(x, z)
            if True:
                    e_lo, e_hi = max(0.0, lo_r[0] - EDGE), max(0.0, hi_r[0] - EDGE)
                    foot = hi_r[1] - BANK * 2.0
                    if e_hi < LIP + 2.0:
                        ramp = hi_r[1] - BANK * max(0.0, e_hi - LIP)
                    else:
                        a_, b_ = max(0.0, e_lo - 0.5), e_hi - LIP - 2.0
                        ramp = lo_r[1] + (foot - lo_r[1]) * (a_ / max(0.01, a_ + b_))
                    # (blended in over 6 m from the glade's edges, so it meets the hillside round it without a step)
                    w = smooth(0.0, 6.0, min(x - GLADE_R[0], GLADE_R[2] - x, z - GLADE_R[1], GLADE_R[3] - z))
                    h = h * (1 - w) + ramp * w
        # (round 35, PATH_RULES C4) a bench's bay: the bank stepped back round it, level with the path beside it
        dmin_ = min((d for d, _, _ in runs), default=99.0)
        for (bx, bz, bh, _) in bench_spots():
            db = math.hypot(x - bx, z - bz)
            if db < 3.2:
                k = (1.0 - smooth(1.3, 3.2, db)) * smooth(EDGE, EDGE + 0.6, dmin_)     # (not on the path itself: A4)
                h = h * (1 - k) + bh * k
        # (round 35, C4: the workmen's site at the first bend in a level bay too — the full play-through: with the hill
        # brought in close, Toni stood 1.4 m up the bank, out of her reach)
        if WORK_SITE:
            wx, wz, wh = WORK_SITE[0]
            dw = math.hypot(x - wx, z - wz)
            if dw < 5.0:
                k = (1.0 - smooth(2.8, 5.0, dw)) * smooth(EDGE, EDGE + 0.6, dmin_)
                h = h * (1 - k) + wh * k
    # (round 40, the user at the hill path's foot: "there's a ditch… Please fix this so that the path doesn't go down then
    # come back up") between the pavement and the first bend the ground was lumpy, the bend in a shallow trench up to
    # 0.4 m deep: there it is the ground's own average over 3 m round, eased in over 2 m at the patch's edges
    if -102.0 < x < -76.0 and -111.0 < z < -101.0 and not _FOOT_SM.get('busy'):
        kf_ = smooth(0.0, 2.0, min(x + 102.0, -76.0 - x, z + 111.0, -101.0 - z))
        if kf_ > 0.0:
            _FOOT_SM['busy'] = True
            av_ = sum(ground(x + 1.5 * ox_, z + 1.5 * oz_) for ox_ in (-1, 0, 1) for oz_ in (-1, 0, 1)) / 9.0
            _FOOT_SM.pop('busy')
            h = h + (av_ - h) * kf_
    # (round 40, the user, on the plan round40/r4/plan_forest_wall.jpg: "The yellow line is good, but then the yellow line
    # should some way along, maybe halfway between the railway tracks and the buildings, start curving up and then pass the
    # corner of the buildings and keep going up into the fence. And this whole area should be a steeper hill that she
    # can't walk up. The stone wall is not necessary.") below the line (WOOD_EDGE) the hill's foot rises gently from
    # the pavement, 0.2 a metre, so she can wander in; along the line a steep bank, 3 m, up to the hill's own lie,
    # which above it is too steep to climb
    if -61.0 < x < 60.0 and -250.0 < z < -102.3 and not _YL.get('busy') and park_r(x, z) >= 1.0:
        sd_ = wood_edge_side(x, z)
        kx_ = smooth(12.0, 17.0, x) if z < -158.0 else 0.0     # (round 41: the new top edge, west of the park)
        if sd_ < 9.0 or (kx_ > 0.0 and sd_ < 50.0):
            hw_ = min(h, 0.05 + 0.2 * (-102.35 - z))
            if sd_ <= 0.0:
                h = hw_
            else:
                if sd_ < 3.0:
                    h = hw_ + (h - hw_) * smooth(0.0, 3.0, sd_)
                # (the walk check: by the park's west wall the hill beyond the line is gentle, and she walked on up past
                # the line's end — there the bank is a ridge at least 0.5 a metre steep for 6 m, more than she can climb
                # at any angle, easing back to the hill's own lie by 9 m)
                ridge_ = hw_ + 0.5 * min(sd_, 6.0)
                kr_ = 1.0 - smooth(6.0, 9.0, sd_)
                if ridge_ > h:
                    h = h + (ridge_ - h) * kr_
                # (round 41, "make it look more like a steeper hill") along the new top edge not a ridge but a hillside:
                # 0.8 a metre for 8 m (far past what she can climb), then on up at 0.15, easing back into the hill's own
                # lie 30–50 m in; by the park's wall no higher than 1.6 m over the park's ground inside (the wall holds it)
                if kx_ > 0.0:
                    st_ = hw_ + 0.8 * min(sd_, 8.0) + 0.15 * max(0.0, sd_ - 8.0)
                    rw_ = park_r(x, z)
                    if rw_ < 1.15:
                        cap_ = park_height(x, z) + 1.6
                        st_ = min(st_, cap_ + (st_ - cap_) * smooth(1.0, 1.15, rw_)) if st_ > cap_ else st_
                    if st_ > h:
                        h = h + (st_ - h) * kx_ * (1.0 - smooth(30.0, 50.0, sd_)) * smooth(0.0, 0.6, sd_)
    # (round 40, the user at the Glòria gate: "this gate is inaccessible. You can't walk in there from this direction.
    # Could you make it so that the path is smooth. Both eastern entrances need to be checked") the park's ground stood
    # up to 1.7 m above the road right in the gateway, a step she couldn't climb: through each side gate an even ramp,
    # from the road's own level in the gateway up to the park's ground 6 m inside
    if 40.0 < x < 200.0 and -260.0 < z < -130.0 and not _GATE_LV.get('busy'):
        for gk_, (gx_, gz_) in GUELL['side_gates'].items():
            dg_ = math.hypot(x - gx_, z - gz_)
            if dg_ < 6.0 and park_r(x, z) < 1.0:
                if gk_ not in _GATE_LV:
                    _GATE_LV['busy'] = True
                    _GATE_LV[gk_] = min(ground(gx_ + ox_, gz_ + oz_) for ox_, oz_ in ((1.2, 0), (-1.2, 0), (0, 1.2), (0, -1.2))
                                        if park_r(gx_ + ox_, gz_ + oz_) >= 1.0)
                    _GATE_LV.pop('busy')
                g0_ = _GATE_LV[gk_]
                if h > g0_:
                    h = g0_ + (h - g0_) * smooth(0.0, 6.0, dg_)
    # (round 41c, PATH_RULES B2, the user: "There is a gap here" — at the funfair's west gateway the hill path's end ran
    # 3 m into the plateau, sunk 0.3 m under its paving, and the stone threshold across the gateway stood over it with a
    # slot below) last of all, so the path's own shaping can't undo it: inside the gateway the ground at the plateau's
    # level, under the threshold at its top, and outside it easing back down to the path's own lie over 4.5 m; across
    # the opening only (it only ever raises the ground)
    # (then the user: "where it's blue, it's just a flat line": raised either side too, the ground buried the wall's
    # brick face and left its top lying flat on the grass — now the opening alone, so the wall stands to its sides; and
    # "the path goes over the top of the paved ground": the ground under the threshold just under its stone, so the
    # path's end tucks under it)
    gz_ = PATH_CTRL[-1][1]
    if FAIR[0] - 5.0 < x < FAIR[0] + 3.5 and abs(z - gz_) < PATH_W / 2 + 1.0:
        k = smooth(FAIR[0] - 4.5, FAIR[0] - 0.2, x) * (1.0 - smooth(PATH_W / 2 + 0.35, PATH_W / 2 + 0.95, abs(z - gz_)))
        h = max(h, h * (1 - k) + FAIR_H * k)
    return h


_FOOT_SM = {}                                        # (round 40: the hill path's foot smoothed, ground())
_YL = {}
# (round 40, the user's yellow line, corrected: from the funicular's fence east, curving up halfway to the buildings,
# past their north-west corner, on up to the park's wall) the wood's walkable edge above the city
# (round 41, the user, with the plan round41/hill_proposal.png: "Make the unwalkable hill to the west of the Guell Park 30
# meters further up the hill… so that it joins with the wall to the park and the steeper hill further to the west. Also
# make it look more like a steeper hill"; "go ahead") above the town's top-left corner the line no longer cuts across
# to the wall at a slant: it runs on up the west side (x 15–20) and then straight across at z −192 to the wall, so the
# whole corner below is gentle ground she can walk on
WOOD_EDGE = [(-60.5, -118.0), (-24.0, -118.0), (-13.0, -120.5), (-3.0, -127.0), (5.0, -137.0), (11.0, -149.0),
             (15.0, -160.5), (16.5, -172.0), (17.5, -184.0), (20.0, -190.5), (25.0, -192.0), (54.0, -192.0)]


def wood_edge_side(x, z):
    """How far (x, z) is beyond WOOD_EDGE, on the hill's side (+), or short of it, on the city's (-)."""
    best = (1e9, 1.0)
    for (ax, az), (bx, bz) in zip(WOOD_EDGE, WOOD_EDGE[1:]):
        dx, dz = bx - ax, bz - az
        t = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)))
        d = math.hypot(x - ax - dx * t, z - az - dz * t)
        if d < best[0]:
            cr = dx * (z - az) - dz * (x - ax)
            best = (d, 1.0 if cr < 0 else -1.0)
    return best[0] * best[1]

_GATE_LV = {}                                        # (round 40) the road's level outside each side gate, worked out once
_GL = {}


def glade_legs(x, z):
    """(round 35, E3) the two legs either side of the ball's glade: (distance, height) to the leg below and the leg
    above — each taken from its own stretch of the path, so the glade's slope never jumps from one stretch to another."""
    if not _GL:
        pts = _path_grid()['pts']
        near = [p for p in pts if GLADE_R[0] - 8 < p[0] < GLADE_R[2] + 8 and GLADE_R[1] - 8 < p[1] < GLADE_R[3] + 8]
        mid = (min(p[2] for p in near) + max(p[2] for p in near)) / 2
        _GL['lo'] = dense_pts([p for p in near if p[2] < mid])
        _GL['hi'] = dense_pts([p for p in near if p[2] >= mid])
    out = []
    for k in ('lo', 'hi'):
        best = min(_GL[k], key=lambda p: (p[0] - x) ** 2 + (p[1] - z) ** 2)
        out.append((math.hypot(best[0] - x, best[1] - z), best[2]))
    return out[0], out[1]


def dense_pts(ps):
    out = []
    for a, b in zip(ps, ps[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 4.0:
            continue
        for k in range(5):
            t = k / 5
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t))
    return out or ps


# (round 35, PATH_RULES C4, the user: "a bench somewhere suitable (on grass so not blocking the path) would be nice")
# the hill path's benches: at each viewpoint, on the grass beside the path — the uphill side, or at a hairpin the
# inside of the bend — 2.4 m from its middle, facing back over the path to the view; the bank steps back round it
VIEWPOINTS = [(-150.5, -125.9), (-72.8, -199.0), (-112.0, -191.2), (-95.0, -228.4), (-128.0, -284.6)]
VIEW_DIR = (0.196, 0.981)                      # (towards La Rambla and the sea)
_BS = []


def bench_spots():
    """[(x, z, ground height, facing (fx, fz))] for the hill path's benches."""
    if not _BS:
        pts = _path_grid()['pts']
        for (vx, vz) in VIEWPOINTS:
            i = min(range(len(pts)), key=lambda k: (pts[k][0] - vx) ** 2 + (pts[k][1] - vz) ** 2)
            a, b, c = pts[max(0, i - 8)], pts[i], pts[min(len(pts) - 1, i + 8)]
            t1 = (b[0] - a[0], b[1] - a[1])
            t2 = (c[0] - b[0], c[1] - b[1])
            l1, l2 = math.hypot(*t1) or 1.0, math.hypot(*t2) or 1.0
            dvx, dvz = (c[0] - a[0]), (c[1] - a[1])
            ln = math.hypot(dvx, dvz) or 1.0
            nx_, nz_ = -dvz / ln, dvx / ln
            turn = math.acos(max(-1.0, min(1.0, (t1[0] * t2[0] + t1[1] * t2[1]) / (l1 * l2))))
            if turn > 1.0:
                # (a hairpin: the inside of the bend, towards where the path's two legs come together)
                ins = (t2[0] / l2 - t1[0] / l1, t2[1] / l2 - t1[1] / l1)
                sd = 1 if ins[0] * nx_ + ins[1] * nz_ > 0 else -1
            else:
                sd = -1 if nx_ * VIEW_DIR[0] + nz_ * VIEW_DIR[1] > 0 else 1      # (the side away from the view)
            bx, bz = b[0] + nx_ * sd * 2.4, b[1] + nz_ * sd * 2.4
            fw_ = (-nx_ * sd, -nz_ * sd)
            if math.hypot(bx - FUNI_BEND[0], bz - FUNI_BEND[1]) < 8.0:
                # (round 41, the user: "this bench should be facing the city. Not directly a slight angle, so it's still
                # ever so slightly facing the railway line, but generally the city") the view, turned 20° towards the line
                a_ = math.atan2(VIEW_DIR[0], VIEW_DIR[1]) + math.radians(20.0)
                fw_ = (math.sin(a_), math.cos(a_))
            _BS.append((bx, bz, b[2] + 0.02, fw_))
    return _BS


# ------------------------------------------------------------------ the Funicular del Tibidabo
# (round 27, the user: "It is actually 'Tibidabo Funicular', can you follow real life, but stylised like the rest of
# the game") The cable car is gone: as on the real hill, a funicular climbs the flank on rails — a single track with
# a passing loop halfway, two counterbalanced cars, and at the top a stone portal where it slips under the
# plateau's edge into the upper station. (round 30, the user: no level crossings — the walking path stays west
# of the line and only bends up to its fence at the viewpoint.)

CABLE_LOW = (-66.0, -104.5)          # the lower station, down on the level, at the city's edge
CABLE_TOP = (-66.0, -278.0)          # the upper station, on the terrace above the portal
FUNI_Z0, FUNI_Z1 = -110.0, -275.5    # the track: from behind the lower station up to the portal in the bank
FUNI_BEND = (-70.3, -197.8)          # where the walking path bends up against the line's fence (round 30)

_FP = {}
_FP_BUILDING = [False]
FUNI_CAP = 0.92                      # (the steepest the track climbs over 2 m: 46%; round 41: the cars stand upright on it, 06 #96b)


def funi_profile(z):
    """The track's height at z (on x CABLE_LOW[0]): the hillside's own climb smoothed even and made monotone (a
    funicular only climbs)."""
    if not _FP:
        _FP_BUILDING[0] = True
        import numpy as np
        zs = np.arange(FUNI_Z0, FUNI_Z1 - 0.1, -2.0)
        hs = np.array([height(CABLE_LOW[0], float(zz)) for zz in zs])
        hs[0] = 0.34
        for _ in range(6):                                # smoothed, holding the ends
            mid = (hs[:-2] + hs[2:]) / 2.0
            hs[1:-1] = hs[1:-1] * 0.3 + mid * 0.7
        for i in range(1, len(hs)):
            hs[i] = max(hs[i], hs[i - 1] + 0.02)
        cap = FUNI_CAP                                    # the steepest a stretch may climb: it is a funicular
        for _ in range(3):
            for i in range(1, len(hs)):                   # the grade capped, climbing...
                hs[i] = min(max(hs[i], hs[i - 1] + 0.02), hs[i - 1] + cap)
            for i in range(len(hs) - 2, -1, -1):          # ...and looking back down
                hs[i] = max(hs[i], hs[i + 1] - cap)
        _FP.update({'zs': zs, 'hs': hs})
        _FP_BUILDING[0] = False
    zs, hs = _FP['zs'], _FP['hs']
    if z >= float(zs[0]):
        return float(hs[0])
    if z <= float(zs[-1]):
        return float(hs[-1])
    t = (float(zs[0]) - z) / 2.0
    i = min(int(t), len(zs) - 2)
    a = t - i
    return float(hs[i] * (1 - a) + hs[i + 1] * a)

# ------------------------------------------------------------------ Gràcia: small streets up to the park's gate

# (round 26, the user: "The buildings in the adjacent suburb are plain, why don't they have the same facades as the
# rest… You need to redo the neighbourhood too. Think about usability, would people live here, does it follow good city
# design, does the direction flow to the right location") The old village of Gràcia as a small grid, as the real one is:
# two level streets along the hill, narrow lanes up it, a square in the middle with houses facing in from every side,
# and Carrer de Larrard, the one wide street, climbing straight from the city's edge to the park's gate (plane trees and
# lamps along it, the forecourt at its top). Every block is a ring of the city kit's houses (north_build.py), lower than
# the Eixample's. Blocks: corners (x, z) metres, in order round each one; the park's wall clips the top row.
GRACIA_BLOCKS = [
    [(20, -100), (43, -100), (43, -115), (20, -115)],              # the row along the city's edge
    [(49, -100), (71, -100), (71, -115), (49, -115)],
    [(77, -100), (95.5, -100), (95.5, -115), (77, -115)],          # (its east side straight along Carrer de Larrard)
    [(106.5, -100), (124, -100), (124, -115), (106.5, -115)],      # across the street, against the hill (round 28,
                                                                   # the user: the street "is still narrowing" — both
                                                                   # rows now face it straight, a normal street's width)
    [(20, -122), (43, -122), (43, -136), (20, -136)],              # the middle row, either side of the square
    [(77, -122), (95.5, -122), (95.5, -136), (77, -136)],
    [(106.5, -122), (124, -122), (124, -133), (106.5, -133)],
    [(20, -143), (43, -143), (43, -156), (20, -156)],              # the top row, under the park's wall
    [(49, -143), (59, -143), (59, -155), (49, -155)],              # (the lane to the Larrard gate runs up its east side)
    [(66, -143), (82, -143), (82, -149.5), (66, -151.5)],          # (clipped to the wall's line)
]
GRACIA_PLACA = (49.0, -136.0, 71.0, -122.0)          # Plaça de la Vila: the open square between the middle row's blocks
GRACIA_PLACA_H = 4.1                                  # (round 26) its level: a terrace between the two streets, steps either side
GRACIA_LEVELS = [(-100.0, 0.0), (-115.0, 2.6), (-122.0, 2.6), (-136.0, 5.6), (-143.0, 5.6), (-157.0, 6.4)]   # (z, height): level
                                                      # streets at -115..-122 and -136..-143, ramps between


def gracia_profile(z):
    """The village's ground by z alone: the terraces and the ramps between them."""
    L = GRACIA_LEVELS
    if z >= L[0][0]:
        return 0.0
    for (za, ha), (zb, hb) in zip(L, L[1:]):
        if zb <= z <= za:
            return ha + (hb - ha) * (za - z) / (za - zb)
    return L[-1][1]
GRACIA_STREETS = {                                    # centrelines (for the lamps, the trees and their names), width
    'larrard': ('Carrer de Larrard', [(101.0, -97.0), (101.0, -136.0)], 5.0),
    'sant_salvador': ('Carrer de Sant Salvador', [(18.0, -118.5), (96.0, -118.5)], 7.0),
    'tres_senyores': ('Carrer de les Tres Senyores', [(18.0, -139.5), (99.0, -139.5)], 7.0),
    'lane_w': ("Carrer de l'Or", [(46.0, -100.0), (46.0, -156.0)], 6.0),
    'lane_e': ('Carrer de Verdi', [(74.0, -100.0), (74.0, -140.0)], 6.0),
    'larrard_gate': ('Baixada de la Glòria', [(62.5, -139.5), (62.5, -157.0)], 6.0),
    # (round 27, the user: "extend Gràcia south a bit so that it covers an extra eixample block… so that you walk
    # through the town to get to the park… as if it is an actual part of the town that people live in") one more
    # block south of the Diagonal, against the wood: Carrer del Torrent de l'Olla carrying Larrard's line on down,
    # the Plaça del Sol on its west side, Carrer de Provença's setts along the south, and Carrer de l'Alzina, the
    # back lane along the wood's edge, where the town ends at a low drystone wall with gaps for the dirt paths.
    'olla': ("Carrer del Torrent de l'Olla", [(101.0, -97.0), (101.0, -50.0)], 5.0),
    'provenca_e': ('Carrer de Provença', [(84.0, -51.0), (128.0, -51.0)], 4.4),
    'alzina': ("Carrer de l'Alzina", [(127.25, -50.0), (127.25, -97.0)], 2.9),
    'perla': ('Carrer de la Perla', [(104.0, -73.0), (130.0, -73.0)], 4.4),
    'travessera': ('Travessera de Dalt', [(86.0, -95.5), (130.0, -95.5)], 5.4),
}
GRACIA_UP = GRACIA_STREETS['larrard'][1]              # up to the gate
GRACIA_FORECOURT = (94.0, -141.0, 118.0, -134.0)      # paved, in front of the gate, where Carrer de Larrard arrives
GRACIA_ZONE = (18.0, -160.0, 130.0, -96.0)            # all of it: paved streets, no wood
GRACIA_EXT = (86.0, -96.0, 130.0, -46.0)              # (round 27) the quarter south of the Diagonal, to Provença's line
# (round 36, the user's approved mock-up: the whole quarter on ONE grid of shared lines — PATH_RULES H1–H5.
# x lines: 86 / 88 / 96.5 / 98.5 | street | 103.5 / 106.5 .. 124 / 125.8 | lane | 128.7 footpath 130.5 | wall | wood.
# z lines: -98.2 | street | -92.8 / -91 .. -77 / -75.2 | street | -70.8 / -69 .. -55 / -53.2 | street | -48.8 / -47.)
GRACIA_SOL = (88.0, -90.8, 96.5, -72.8)               # the Plaça del Sol's floor: its paving, trees, benches, the café's tables
GRACIA_SQUARE = (86.0, -92.8, 98.5, -53.2)            # the floor, the house closing its south side, and ONE footpath round both


def sol_spread(x, z):
    """(Round 36, the user: "spread out the things… so that it fills the square more fully, but still have a strip
    around the ends where there is nothing… in the current proportion") the Plaça del Sol's trees, benches, lamps,
    astrolabe and tables, laid out round GRACIA_SOL, moved out from the open floor's middle (the square north of the
    closing house) by 1.3 alike in both directions: the lamps stand 1.5 m and more in from its edges."""
    cx_, cz_, k_ = 92.25, -80.9, 1.3
    return cx_ + (x - cx_) * k_, cz_ + (z - cz_) * k_



# (round 36, the user: "the streetlights and the trees are too close together") the Plaça del Sol's lamps, one at the
# middle of each side, clear of the corner trees and of the café's tables along the east
SOL_LAMPS = [(87.9, -80.9), (96.6, -79.7), (92.25, -91.6), (92.25, -71.0)]
GRACIA_BLOCKS.append([(106.5, -77), (124, -77), (124, -91), (106.5, -91)])   # the quarter's north row, on the Travessera
GRACIA_BLOCKS.append([(106.5, -55), (124, -55), (124, -69), (106.5, -69)])   # its south row, Olla to the wood
GRACIA_BLOCKS.append([(88, -55), (96.5, -55), (96.5, -69), (88, -69)])       # the house closing the square's south side
GRACIA_FOOT_X = (128.7, 130.5)                        # the wood-side footpath: the cobbles end on it (H3)
GRACIA_WALL_X = 131.1                                 # the drystone wall's line, east of the footpath
GRACIA_WALL_GAPS = ((-97.2, -93.8), (-75.6, -70.4), (-52.6, -49.4))   # open where a street's end meets the wood's path
GH_EDGE_Z = -118.8                                    # (round 39) the eastern wood's top edge (2D tile row 9): the wood's
                                                      # own ground south of it, the closed hill's bank north of it
PARK_GATE = (106.0, -141.0)
# (round 36, H6, the user's approved mock-up) the top edge under the park's wall: ONE road (Carrer de les Tres
# Senyores) running on past Larrard's top in front of the gate and down the lane by the wood, cobbles only on it and
# on the lanes; everything else footpath, a footpath along the wall. These are its kerb lines (x, z).
# (The user, on the built top edge: "make the road/path follow the purple line, so straight and then… the footpath
# coming down the hill has a relatively constant width, and then it curves around the entrance and joins up with the
# outside eating area": the north kerb runs straight past the café's terrace, curves down round the gate's entrance —
# a small forecourt of footpath before it — and back up, then keeps 1.8 m off the wall to the gravel.)
def _top_kerb():
    pts = [(18.0, -141.2), (82.0, -141.2), (88.0, -141.0), (97.0, -141.0)]
    # (then "Please take a bit more off here": the forecourt only as wide as the gateway, the kerb easing down to it
    # over 6.7 m from the west lodge and back up from it at once on the east)
    for i in range(1, 11):                                # down round the entrance's west side
        t = i / 10.0
        pts.append((97.0 + 6.7 * t, -141.0 + 2.4 * (0.5 - 0.5 * math.cos(math.pi * t))))
    pts.append((109.4, -138.6))
    for i in range(1, 11):                                # and back up past the east lodge
        t = i / 10.0
        pts.append((109.4 + 6.1 * t, -138.6 - 2.0 * (0.5 - 0.5 * math.cos(math.pi * t))))
    pts += [(118.0, -140.75), (122.0, -141.2), (128.7, -143.1)]
    return pts


GRACIA_TOP_ROAD_N = _top_kerb()
GRACIA_TOP_ROAD_S = [(98.5, -137.8), (98.5, -133.0)]  # (Larrard's mouth; east of it the road's south kerb, below)
GRACIA_TOP_ROAD_SE = [(103.5, -133.0), (103.5, -134.8), (106.5, -134.8), (118.0, -136.0), (125.8, -138.0),
                      (125.8, -133.0)]
GRACIA_TOP_WALL = [(61.2, -160.0), (63.0, -157.0), (70.0, -155.0), (84.0, -152.0), (92.0, -145.5), (106.0, -141.0),
                   (122.0, -143.0), (128.7, -144.9)]
GRACIA_TOP_LANES = [(44.8, 47.2, -156.8), (60.8, 64.2, -155.2)]   # (x0, x1, the lane's top end): Carrer de l'Or, Glòria
GRACIA_TERRACE_H = 5.6                                # the café terrace: level with the road (H6.5)
GRACIA_GLORIA_H = 7.0                                 # the Glòria gate's level, which the steep footpath climbs to (H6.6)
GRACIA_CAFE = [(85.0, -143.9), (85.0, -146.7), (87.9, -144.1), (90.6, -143.6)]   # the Cafè del Parc's tables


def line_z(line, x):
    """A kerb line's z at x (the line runs west to east)."""
    for a, b in zip(line, line[1:]):
        if a[0] <= x <= b[0]:
            return a[1] + (b[1] - a[1]) * (x - a[0]) / max(1e-6, b[0] - a[0])
    return line[0][1] if x < line[0][0] else line[-1][1]


def top_wall_side(x, z):
    """Signed distance from the park's wall along Gràcia's top edge: + on the town's side."""
    best, sd = 1e9, 1
    W = GRACIA_TOP_WALL
    for a, b in zip(W, W[1:]):
        dx, dz = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dz * dz
        t = max(0.0, min(1.0, ((x - a[0]) * dx + (z - a[1]) * dz) / L2))
        dd = math.hypot(x - a[0] - dx * t, z - a[1] - dz * t)
        if dd < best:
            best, sd = dd, (1 if dx * (z - a[1]) - dz * (x - a[0]) > 0 else -1)
    return best * sd


def gracia_top_h(x, z):
    """(Round 36, H6.5/H6.6) where the top edge is reshaped, (the ground's height, how fully it holds), else None: the
    café terrace level with the road (the wall stands taller over it); the steep footpath behind the top-left block,
    from the terrace up to the Glòria gate's level (20%, under the 30% she can walk, north.gd MAX_UP); Baixada de la Glòria ramping to
    the same level, and the footpath north of the block beside it easing over to it. It reaches 1.8 m in under the
    wall, so the 1.65 m ground grid lays no slope along the wall's foot on the town side."""
    gate_ = math.hypot(x - 63.0, z + 157.0) < 3.0
    if not (53.0 <= x <= 94.6 and -162.0 < z < -139.0) or top_wall_side(x, z) < (-0.3 if gate_ else -1.8):
        return None                                         # (in the Glòria gateway only to the wall: the park's
                                                            #  own ground climbs on behind it; either side of it,
                                                            #  as along the terrace, 1.8 m under the wall — round 36,
                                                            #  the user's "weird path": a wedge at the wall's foot)
    # (round 40, the user by Casa Larrard: "There should not be a drop into the fence where you can get stuck";
    # --trapsim) the 1.8 m was measured from the top road's wall, but west of the gate the park's wall runs off at a
    # slant, and the town's level reached up to 1.8 m into the park behind it: a ditch at the street's level between
    # the wall and the house that she slid into and couldn't climb out of. Inside the park it stops at the wall's
    # own thickness (except in the gateway itself)
    if not gate_ and _in_wall(x, z) and (1.0 - park_r(x, z)) * 40.0 > 0.4:
        return None
    lo, hi = GRACIA_TERRACE_H, GRACIA_GLORIA_H
    if x >= 82.0:
        return (lo, 1.0) if z <= line_z(GRACIA_TOP_ROAD_N, x) else None
    if x >= 66.0:
        if z > -151.5 + (x - 66.0) * 0.125 + 0.3:          # (south of the block's north face: the block)
            return None
        return (lo + (hi - lo) * min(1.0, max(0.0, (80.0 - x) / 7.0)), 1.0)
    if x >= 58.5:
        if z > -141.2:
            return None
        return (lo + (hi - lo) * min(1.0, (-141.2 - z) / 9.8), 1.0)
    if z <= -156.8:
        return (hi, (x - 53.0) / 5.5)                       # (north of the next block: easing over to the gate's level)
    return None


# ------------------------------------------------------------------ Park Güell, stylised, as laid out in reality
# (south at the bottom): the gate in its wall with the two lodges either side (Casa del Guarda to the west), the
# dragon stairs up to the Hypostyle Room, the Nature Square on its roof with the wavy bench and the view, the
# Pòrtic de la Bugadera (leaning columns) to the west, the Casa Museu Gaudí (pink, a spire) and Casa Trias to the
# east, a ring of winding paths round it all.

GUELL = {
    'gate': PARK_GATE,                                     # in the wall, facing Gràcia
    'guarda': (98.0, -147.0),                              # Casa del Guarda, west of the gate (its door faces the plaza)
    'lodge': (114.0, -147.0),                              # the other lodge, east
    'plaza': (96.0, -154.0, 116.0, -143.0),                # the gate plaza, 6 m up (round 27: back to the stairs'
                                                           # foot; the gateway strip is painted sand in world2d)
    'stairs_r': (102.5, -166.0, 109.5, -154.0),            # the dragon stairs: 6 -> 9 m (round 27, the user: the gap
                                                           # by the lodge was too small: "Move it back")
    'porch': (85.0, -175.0, 127.0, -166.0),                # the terrace under and in front of the Hypostyle Room's columns, 9 m up
                                                           # (round 26: out to the side stairs' feet, so they start from its paving)
    'colonnade_z': -170.3,                                 # its front row of columns (the second row 2.3 m behind)
    'hypostyle': (93.0, -183.0, 119.0, -174.6),            # the hall behind them, under the square (an interior inside)
    # (round 25, the user: "The terrace seems too big, it shouldn't be small, but it takes away from other aspects of the
    # park"; "big enough, but not so that it feels like an open steppe") about two-thirds of round 24's
    'square_r': (90.0, -198.0, 122.0, -175.6),             # the Nature Square, on its roof (it overhangs the columns)
    'square_h': 15.4,
    # ("You should be able to reach the terrace like in real life") the stairs either side of the hall, from the porch's
    # ends up to the square's sides (9 -> 15.4 m), and two ways in at its own level: from the west past the leaning
    # columns, from the east off the Pont de Baix; walled all round otherwise (no way in at the back)
    'side_stairs': [(85.5, -186.0, 90.0, -167.0), (122.0, -186.0, 126.5, -167.0)],      # (a landing at the top, z < -182)
    'stairs_top_z': -182.0,
    # (round 34: the back corners open too — the covered walk along the square's back comes round them)
    'square_ways': [('w', -186.0, -181.5), ('e', -186.0, -181.5), ('w', -198.0, -191.5), ('e', -198.0, -190.5)],
    'bugadera': (91.0, -191.0, 7.0),                       # the portico's arc, by the square's west end: centre, radius
    'key': (65.4, -221.2),                                 # where Pere dropped the cellar key: half under a scrub bush
                                                           # north-west of the calvary (round 40, the user's yellow mark;
                                                           # it lay under the gravel of the path up to the gardens, unseen)
    # (round 33: 13 m, was 14 — the lawn before it is at 11.3, behind it 14.8; a metre down into its slope, and the lawn
    # leads up to it over 12 m, not 7: the slope below it was too steep to walk up)
    'museu': (141.0, -181.0), 'museu_r': (134.0, -188.0, 148.0, -174.0), 'museu_h': 13.0,
    # (round 34, the user's aerial view: Casa Trias stands high on the hill, well above and behind the Casa Museu and
    # the long covered walk, not beside them)
    'trias': (155.0, -226.0), 'trias_r': (147.0, -233.0, 163.0, -219.0), 'trias_h': 22.5,
    'calvari': (70.0, -217.0),                             # (round 24) the calvary's top, its three crosses
    # (round 25) Casa Larrard (Count Güell's house, now a school) by the Larrard gate; the Austria Gardens beyond it
    'larrard': (70.0, -167.0), 'larrard_r': (63.0, -172.0, 77.0, -162.0), 'larrard_h': 9.0,
    'austria': (56.0, -205.0, 78.5, -181.0),     # (round 33: 6 m further west, three beds across — it left 1.5 m
                                                 #  for the path beside the side stairs' wall)
    'side_gates': {'larrard': (63.0, -157.0), 'carmel': (171.25, -227.25), 'gloria': (180.1, -188.4)},
}

# (round 25: the plan the user agreed, round25/park_plan.png) footpaths of pale sauló, as in the real park: from the gate
# plaza west, past Casa Larrard to its gate, and up by the Austria Gardens; through the Pòrtic de la Bugadera onto the
# square's west end; on up to the calvary; east past the Casa Museu to Casa Trias and on to the Carmel gate; across to
# the Glòria gate; the upper walk along the hill (the Pont del Mig carries part of it) and the top walk (the Pont de
# Dalt); and off the square's east end along the Pont de Baix. (x, z) metres.
PARK_PATHS = [
    # (round 33, the user: "The whole park is in shambles… The footpaths don't line up… The dirt track is too steep; it
    # should curve up the hill… if you need to shift a whole area, do it and then clean it up") the network laid out
    # afresh: every path leaves from a real opening (the gate plaza's two open corners behind the lodges, the gates,
    # the houses' doors, the square's ways in) and meets the next at a junction; the climbs wind across the slope.
    # (round 34, the user, with the aerial view: "rearrange it around a stylised version of this… Look at how the paths
    # move") the interior laid out after it: the long covered walk round the square's back and on past the Casa Museu
    # with a walk on its roof (GALLERY), the hairpin that climbs from its east end back onto that roof, the switchbacks
    # up through the terraced beds from the gate to the Casa Museu, Casa Trias high on the hill behind.
    #  0  the west walk: the plaza's west corner, past Casa Larrard's front, to the Larrard gate
    # (round 33, third look: it began 3 m short of the plaza, a square end on the lawn, and ran at the wall's foot)
    [(97.0, -152.4), (93.0, -153.0), (87.0, -155.0), (80.0, -157.0), (72.0, -158.0), (65.5, -157.6), (63.0, -157.05)],   # (round 36: to the Glòria gate's middle)
    #  1  up to the Austria Gardens, winding up the slope east of Casa Larrard (it rose straight up at 0.28)
    # (round 33, second look: its first zigzag pressed against the porch's end wall: up the middle of the 8 m between
    # Casa Larrard and the porch now, a gentle S)
    [(80.0, -157.0), (81.6, -160.5), (80.6, -166.5), (81.0, -172.5), (82.0, -178.5), (82.0, -183.0)],
    #  2  the gardens' east edge to the covered walk's west end, at the square's level
    [(82.0, -183.0), (82.6, -187.4), (84.6, -190.9), (87.5, -193.0)],
    #  3  from the gardens' north edge round the calvary's rise to its steps
    # (round 40, the user at the calvary: the path stopped on the lawn beside its steps: it comes round and ends at their
    # foot, square on to them; north_build.py builds the flight down to here)
    # (round 40, the user: "the path next to the Austrian gardens goes up the hill a little bit, and there's like a square
    # there": it left the gardens' top walk at an angle up the bank) it carries straight on from the gardens' east walk
    [(76.0, -202.75), (76.0, -207.0), (73.4, -208.7), (70.0, -209.5), (70.0, -210.5)],
    #  4  (round 34) the switchbacks: from the plaza's east corner up through the terraced beds to the Casa Museu's door
    [(115.0, -152.4), (122.0, -153.0), (131.0, -154.6), (140.0, -156.8), (143.6, -159.4), (141.5, -162.0), (134.0, -163.2),
     (130.2, -165.0), (130.0, -167.8), (133.5, -169.6), (139.5, -170.8), (142.15, -172.6), (142.15, -176.7)],
    #  5  from the Casa Museu's path round its east side up to the covered walk's east end
    [(142.15, -172.6), (147.5, -172.8), (152.5, -177.5), (155.3, -184.5), (156.6, -191.0), (157.4, -197.6)],
    #  6  Casa Trias's portico path round the house's east side to the Carmel gate
    [(154.85, -218.5), (161.5, -218.8), (166.0, -221.8), (169.4, -225.0), (170.6, -226.2)],
    #  7  the Glòria gate in to the Casa Museu's path
    [(179.0, -188.2), (168.0, -186.5), (156.0, -186.0)],
    #  8  the lower walk on from the covered walk's east end to the foot of the hairpin
    [(154.0, -196.9), (157.4, -197.6), (163.0, -199.6), (167.5, -201.4)],
    #  9  the middle carriage road (over the Pont del Mig), from the calvary's rim to Casa Trias's path
    [(70.0, -220.6), (82.0, -228.0), (96.0, -230.0), (112.0, -228.0), (128.0, -224.0), (138.5, -218.6), (146.5, -213.2),
     (153.4, -209.5)],
    # 10  the top carriage road (the Pont de Dalt), looping back to the middle one (round 30)
    [(82.0, -228.0), (78.0, -238.0), (90.0, -244.0), (112.0, -246.0), (126.0, -244.5), (135.0, -239.0),
     (140.5, -229.5), (138.5, -218.6)],
    # 11  (round 34, the user: "There should be a path leading up to the portico") Casa Trias's portico steps down the
    # hill to the covered walk's roof
    [(155.1, -221.2), (154.6, -215.5), (153.4, -209.5), (152.9, -201.8)],
    # 12  (round 34) the hairpin: from the lower walk's end round and up onto the covered walk's roof
    [(167.5, -201.4), (172.0, -203.2), (173.8, -206.6), (171.0, -209.6), (165.0, -209.3), (159.5, -206.0), (155.5, -203.6),
     (152.9, -201.8)],
    # 13  the roof walk's west end down past the Austria Gardens' north-east corner to the calvary path (round 40: taken
    # out — "The hill should just be green" — then put back, the user: "you removed the path that went down to the
    # gardens from this point. Please put it back. It should be lightly sloping and then curving around"; PATH_RULES G3)
    [(82.7, -195.4), (81.1, -198.5), (79.7, -201.5), (78.3, -204.3), (76.0, -207.0)],
    # 14  (round 35b) the short link east of the Larrard house's level (its words lost in round 36; values as built)
    [(80.7, -167.0), (79.0, -167.0), (77.4, -167.0)],
]
# (round 34) which paths are graded (each an even climb between its ends); the carriage roads keep the hill's lie
GRADED_PATHS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14]

# (round 34, the user: the Pòrtic de la Bugadera "has a wall on the other side and you can walk on the top. There are
# also similar ones elsewhere. The most prominent one is between casa museu and the higher up casa"; the aerial view:
# a long curved arcade round the back of the Nature Square, running on east above the Casa Museu) the covered walk: its
# lower walk's middle line (x, z), at the square's level, leaning columns on its open side (towards the square and the
# Casa Museu), the hill held back by a rubble wall on the other, and a roof you walk on, level with the hill behind.
GALLERY = {
    'line': [(87.5, -193.0), (87.9, -196.0), (89.3, -198.6), (92.0, -199.9), (106.0, -199.9), (120.0, -199.9),
             (122.7, -198.6), (124.6, -196.6), (127.5, -195.3), (132.0, -194.8), (140.0, -195.4), (148.0, -196.2),
             (154.0, -196.9)],
    'h0': 15.4, 'h1': 15.8,          # its floor: the square's level to the square's NE corner, then rising gently east
    'flat_to': 124.6,                # (x where the rise begins)
    'roof': 4.3,                     # the roof's top above the floor
    'out': 2.3, 'wall': 1.9,         # the open side's edge and the hill wall, from the middle line
    'deck_in': 5.6,                  # how far the roof's paving reaches behind the wall, over the hill's edge
                                     # (round 34: past the ground's next height sample, 1.65 m behind the wall)
}


# (round 34: the aerial view's green terraces between the switchbacks below the Casa Museu: flower beds, open to the sun)
PARK_TERRACES = (118.0, -171.5, 146.0, -153.5)


def gallery_where(x, z):
    """(signed distance from the lower walk's middle line: + into the hill; how far along it 0..1; metres beyond its
    ends; its floor there)."""
    line = GALLERY['line']
    d, t, sd = _seg_near(x, z, line)
    s = d * -sd
    beyond = 0.0
    for (b, f, out_, end) in ((line[0], (line[1][0] - line[0][0], line[1][1] - line[0][1]), -1.0, 0.0),
                              (line[-1], (line[-1][0] - line[-2][0], line[-1][1] - line[-2][1]), 1.0, 1.0)):
        if abs(t - end) < 1e-6:
            L = math.hypot(f[0], f[1])
            beyond = max(beyond, out_ * ((x - b[0]) * f[0] + (z - b[1]) * f[1]) / L)
            # (the side, past the end: across the end segment's direction, + into the hill)
            s = ((x - b[0]) * f[1] - (z - b[1]) * f[0]) / L
    return s, t, beyond, gallery_floor(t)


def gallery_floor(t):
    line = GALLERY['line']
    tot = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(line, line[1:]))
    acc, at = 0.0, None
    for a, b in zip(line, line[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if at is None and a[0] >= GALLERY['flat_to'] - 0.01:
            at = acc
        acc += L
    u = t * tot
    if u <= at:
        return GALLERY['h0']
    return GALLERY['h0'] + (GALLERY['h1'] - GALLERY['h0']) * (u - at) / (tot - at)


# the three viaducts Gaudí built for the estate's carriage road (all real: the Pont de Baix, del Mig and de Dalt), each
# carrying a stretch of path along the hillside on rough stone columns, the slope falling away below; each different
VIADUCTS = {
    # (round 28: 'baix' removed — rerouting its path left its leaning columns stranded in the bank below the
    # south-east wall, reading as broken stumps, and its sunken walk dug the ditch the wall sat in)
    'mig': [(96.0, -230.0), (112.0, -228.0), (128.0, -224.0)],         # twin rows of columns, round arches
    'dalt': [(78.0, -238.0), (90.0, -244.0), (112.0, -246.0)],         # arches, great stone urns along its top
}
VIA_DROP = 3.0           # how far the ground below a viaduct falls away from the path on it
# (round 25) the Carretera del Carmel: the lane round the park's east side outside its wall, from the main gate past the
# Glòria gate to the Carmel gate, at an even gentle grade (so the side gates lead somewhere)
CARMEL_ROAD = [(108.0, -139.0), (130.0, -142.0), (150.0, -147.0), (170.0, -158.0), (184.0, -176.0), (187.0, -192.0),
               (186.0, -205.0), (182.0, -215.0), (177.0, -228.0), (174.0, -233.5)]
ROAD_W = 4.0


def _seg_near(x, z, line):
    """(distance to a line of points, how far along it 0..1, the side: +1 left of its direction, -1 right)."""
    best, tb, sd = 1e9, 0.0, 1
    tot = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(line, line[1:]))
    acc = 0.0
    for a, b in zip(line, line[1:]):
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz)
        t = max(0.0, min(1.0, ((x - a[0]) * dx + (z - a[1]) * dz) / (L * L)))
        d = math.hypot(x - a[0] - dx * t, z - a[1] - dz * t)
        if d < best:
            best, tb = d, (acc + t * L) / tot
            sd = 1 if dx * (z - a[1]) - dz * (x - a[0]) > 0 else -1
        acc += L
    return best, tb, sd


def gracia_hill(x, z):
    """(Round 39, the user: "make the forest around it like the one further down the hill… so Sandra can't get into
    that area") the closed hill east of Gràcia: east of the wood-side footpath's rope fence (x 131.1), north of the
    eastern wood's top edge (GH_EDGE_Z, its bank in ground()), outside the park, beyond the Carretera del Carmel's
    fence on its outer side (3 m from its middle; 3.8 m keeps a strip clear behind it), up to the road's top past the
    Carmel gate, east to the grid's edge. Planted as thick as the eastern wood (north_build.py); she never walks in it."""
    if not (GRACIA_WALL_X + 0.6 < x < 241.0 and -232.0 < z < GH_EDGE_Z) or park_r(x, z) < 1.0:
        return False
    d, _, sd = _seg_near(x, z, CARMEL_ROAD)
    return sd > 0 and d > ROAD_W / 0.85 / 2 + 1.45


def park_wood(x, z):
    """(round 33) Park Güell's wooded ground. (round 34, the user, with the aerial view: "You shouldn't be able to see
    much of the park, except at view points of the city") nearly all of it: everywhere inside the wall but the gate
    plaza, the porch and the stairs, the square and the covered walk round it, the terraced beds of the switchbacks,
    the Austria Gardens, the houses' own yards, the calvary's lookout and the gates' approaches. The planting
    (north_build.py) sets its trees close there, and the ground is the wood's floor (world2d.py, ParkFloor)."""
    G = GUELL
    if park_r(x, z) >= 1.0:
        return False
    if math.hypot(x - G['calvari'][0], z - G['calvari'][1]) < 9.0:
        return False
    if any(math.hypot(x - gx_, z - gz_) < 7.0 for gx_, gz_ in list(G['side_gates'].values()) + [PARK_GATE]):
        return False
    for r, pad in ((G['plaza'], 1.0), (G['porch'], 1.0), (G['stairs_r'], 1.0), (G['square_r'], 1.0), (G['larrard_r'], 2.0),
                   (G['austria'], 1.0), (G['museu_r'], 0.5), (G['trias_r'], 1.5), (PARK_TERRACES, 0.0)) + \
            tuple((sr, 1.0) for sr in G['side_stairs']):
        if rect_d(x, z, r) <= pad:
            return False
    s, t, beyond, fl = gallery_where(x, z)
    if -GALLERY['out'] - 1.0 < s < GALLERY['deck_in'] + 1.0 and beyond < 2.0:
        return False
    return True


if __name__ == '__main__':
    pts, L = path_points()
    print('path length %.0f m, rise %.0f m, grade %.1f%%' % (L, FAIR_H, 100 * FAIR_H / L))
    # how far the path is above or below the ground it crosses (the cut it needs)
    worst = max(abs(height(x, z) - h) for x, z, h in pts)
    print('worst cut/fill %.1f m' % worst)
    for x, z in WORKMEN + [BALL_LEDGE]:
        print('at', x, z, 'ground %.1f' % height(x, z))


# (round 26) Toni's work site just above the barrier, on the uphill side of the path (here, once the park is defined)
_wx, _wz, _wdx, _wdz = path_at(WORK_L + 16.0)
_up = 1.0 if height(_wx - _wdz * 4.0, _wz + _wdx * 4.0) > height(_wx + _wdz * 4.0, _wz - _wdx * 4.0) else -1.0
WORKMEN[1] = (_wx - _wdz * 4.6 * _up, _wz + _wdx * 4.6 * _up)
WORK_SITE.append((WORKMEN[1][0], WORKMEN[1][1], path_near(_wx, _wz)[1] + 0.05))
