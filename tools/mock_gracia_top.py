# Gràcia's top edge, under Park Güell's wall (round 36, the user: "redo the footpaths and roads, just like we did at
# the bottom… just have the cobblestone roads as roads. Have everything else as a footpath… the wall should have the
# footpath along it. And then there's a cobblestone road that's continuous around the buildings"; the square "more
# open"; the gravel road ending at the town's edge; the gate lamp by the block; the Glòria gate's join tidied).
# Everything paved is footpath first; the roads (one continuous cobbled road round the blocks, bending with the
# wall in front of the gate, and the lanes) are laid over it at their own widths; the roofs are put back.
# usage: python3 tools/mock_gracia_top.py <overhead.png> <scene.json> <out.jpg>
import json
import sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
A = Image.open(sys.argv[1]).convert('RGB')
SJ = json.load(open(sys.argv[2]))
k = 5148 / 429.0
X0, Z0, X1, Z1 = 14, -166, 142, -112


def P(x, z): return (round((x + 232) * k), round((z + 330) * k))
def L(x, z): return (round((x - X0) * k), round((z - Z0) * k))
def grab(x0, z0, x1, z1): return A.crop(P(x0, z0) + P(x1, z1))


SETT = grab(105.0, -52.8, 122.0, -50.0)            # Provença's setts (no shade, no leaves)
PAVE = grab(129.0, -120.0, 130.2, -110.0)          # the wood-side footpath's panot
TREE = grab(112.9, -99.7, 117.6, -95.1)            # the Travessera's plane tree, from above
FOUNT = grab(58.8, -130.2, 61.2, -127.8)           # the square's fountain
KERBC = (122, 120, 118)
BENCH = (139, 94, 60)
WALL = [(61.2, -160.0), (63.0, -157.0), (70.0, -155.0), (84.0, -152.0), (92.0, -145.5), (106.0, -141.0),
        (122.0, -143.0), (128.7, -144.9)]
FP_X = 128.7                                        # the wood-side footpath's west edge: the town ends, the gravel starts

tm = TREE.convert('L')
tp, mp = TREE.load(), tm.load()
for j in range(TREE.height):
    for i in range(TREE.width):
        R, G, B = tp[i, j]
        mp[i, j] = 255 if (G > R + 8 and G > B + 15) else 0


def tiled(tex, size):
    out = Image.new('RGB', size)
    for y in range(0, size[1], tex.height):
        for x in range(0, size[0], tex.width):
            out.paste(tex, (x, y))
    return out


def poly(img, tex, pts, kerb=False):
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).polygon([L(*p) for p in pts], fill=255)
    img.paste(tiled(tex, img.size), (0, 0), m)
    if kerb:
        ImageDraw.Draw(img).line([L(*p) for p in pts + pts[:1]], fill=KERBC, width=2)


def rect(img, tex, x0, z0, x1, z1, kerb=False):
    poly(img, tex, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], kerb)


def put(img, src, x, z, mask=None):
    p = L(x, z)
    img.paste(src, (p[0] - src.width // 2, p[1] - src.height // 2), mask)


def plan():
    img = A.crop(P(X0, Z0) + P(X1, Z1))
    keep = img.copy()
    d = ImageDraw.Draw(img)
    # 1. footpath everywhere paved north of the top road's south kerb: up to the wall (and the town's north edge)
    poly(img, PAVE, [(18.0, -160.0)] + WALL + [(FP_X, -134.8), (103.5, -134.8), (103.5, -137.8), (18.0, -137.8)])
    # 2. the open square: one floor of footpath from road to road, no walls, no steps (a gentle slope instead)
    rect(img, PAVE, 47.2, -137.8, 72.8, -120.2)
    # 3. the roads, cobbled, at their own widths, one continuous road round the blocks
    # (it bends south past the west lodge, which stands out from the wall: footpath in front of it too)
    road = [(18.0, -141.2), (88.0, -141.2), (94.0, -140.0), (98.5, -139.4), (106.0, -139.2), (118.0, -140.4), (FP_X, -143.2),
            (FP_X, -138.8), (118.0, -136.0), (106.5, -134.8), (103.5, -134.8), (103.5, -133.0), (98.5, -133.0),
            (98.5, -137.8), (18.0, -137.8)]
    poly(img, SETT, road)
    d.line([L(*p) for p in road[:7]], fill=KERBC, width=2)
    d.line([L(*p) for p in road[7:11]], fill=KERBC, width=2)
    d.line(L(98.5, -137.8) + L(18.0, -137.8), fill=KERBC, width=2)
    rect(img, SETT, 125.8, -139.5, FP_X, -133.0)                   # the lane down the wood's side, from the road
    d.line(L(125.8, -137.0) + L(125.8, -133.0), fill=KERBC, width=2)
    rect(img, SETT, 60.8, -155.2, 64.2, -141.0)                    # Baixada de la Glòria, up to the gate's footpath
    d.line(L(60.8, -155.2) + L(60.8, -141.2), fill=KERBC, width=2)
    d.line(L(64.2, -155.2) + L(64.2, -141.2), fill=KERBC, width=2)
    d.line(L(60.8, -155.2) + L(64.2, -155.2), fill=KERBC, width=2)
    rect(img, SETT, 44.8, -156.8, 47.2, -141.0)                    # Carrer de l'Or, to the town's north footpath
    d.line(L(44.8, -156.8) + L(44.8, -141.2), fill=KERBC, width=2)
    d.line(L(47.2, -156.8) + L(47.2, -141.2), fill=KERBC, width=2)
    d.line(L(44.8, -156.8) + L(47.2, -156.8), fill=KERBC, width=2)
    rect(img, SETT, 44.8, -137.8, 47.2, -120.2)                    # (the lanes either side of the square, as they were)
    rect(img, SETT, 72.8, -137.8, 75.2, -120.2)
    for x_ in (44.8, 47.2, 72.8, 75.2):
        d.line(L(x_, -137.8) + L(x_, -120.2), fill=KERBC, width=2)
    # 4. the roofs and the lodges, as they are
    for blk in ([(20, -143), (43, -143), (43, -156), (20, -156)], [(49, -143), (59, -143), (59, -155), (49, -155)],
                [(66, -143), (82, -143), (82, -149.5), (66, -151.5)]):
        m = Image.new('L', img.size, 0)
        xs, zs = [p[0] for p in blk], [p[1] for p in blk]
        cx, cz = sum(xs) / len(xs), sum(zs) / len(zs)
        ImageDraw.Draw(m).polygon([L(cx + (x - cx) * 1.04, cz + (z - cz) * 1.06) for x, z in blk], fill=255)
        img.paste(keep, (0, 0), m)
    for (x0, z0, x1, z1) in ((94.3, -151.0, 101.7, -142.6), (110.3, -151.0, 117.9, -142.6)):
        a, b = L(x0, z0), L(x1, z1)
        img.paste(keep.crop(a + b), a)
    # 5. the square: plane trees round its edge, the fountain in the open middle, benches under the trees
    for (tx, tz) in ((50.6, -134.6), (60.0, -134.6), (69.4, -134.6), (50.6, -123.4), (60.0, -123.4), (69.4, -123.4)):
        put(img, TREE, tx, tz, tm)
    put(img, FOUNT, 60.0, -129.0)
    # the footpath's corner between the top-left block and the west lodge (the user: "an alfresco dining area… a
    # restaurant on the side of that building, like with awnings… someone sitting there"): the Cafè del Parc moved
    # up here from the top of Larrard, where its tables stood in the road; its front on the block's east side
    for j in range(12):                                             # the awning, red and cream stripes
        z0 = -148.6 + j * 0.38
        a, b = L(82.0, z0), L(83.1, z0 + 0.38)
        d.rectangle(a + b, fill=(196, 52, 46) if j % 2 == 0 else (240, 232, 214))
    for (cx, cz) in ((85.0, -143.9), (85.0, -146.7), (87.9, -144.1), (90.6, -143.6)):
        for (ox, oz) in ((-0.75, 0), (0.75, 0)):                    # two chairs a table
            a, b = L(cx + ox - 0.22, cz - 0.22), L(cx + ox + 0.22, cz + 0.22)
            d.rectangle(a + b, fill=(150, 104, 58))
        a, b = L(cx - 1.25, cz - 1.25), L(cx + 1.25, cz + 1.25)     # the parasol over it, cream and yellow
        for q in range(8):
            d.pieslice(a + b, q * 45, q * 45 + 45, fill=(246, 238, 220) if q % 2 else (232, 196, 70), outline=(190, 170, 120))
    # (the user: "flatten that part… the wall will be higher from that side… behind the building is a steep street
    # that goes up… between the wall and the building to bring up the level… for the next gate") the terrace level
    # with the road (dashed), the wall standing taller over it, the footpath behind the block ramping up to the gate
    terr = [(83.8, -141.3), (88.0, -141.3), (94.0, -140.1), (94.2, -142.3), (92.0, -145.5), (84.0, -152.0), (83.8, -151.0)]
    tq = [L(*p) for p in terr + terr[:1]]
    for a, b in zip(tq, tq[1:]):
        n_ = max(1, int(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 / 8))
        for i in range(0, n_, 2):
            d.line((a[0] + (b[0] - a[0]) * i / n_, a[1] + (b[1] - a[1]) * i / n_,
                    a[0] + (b[0] - a[0]) * (i + 1) / n_, a[1] + (b[1] - a[1]) * (i + 1) / n_), fill=(40, 90, 200), width=3)
    d.line([L(84.0, -152.0), L(92.0, -145.5), L(94.3, -143.6)], fill=(120, 80, 60), width=6)       # the taller wall
    for xc in (80.0, 76.0, 72.0, 68.0):                             # up the ramp behind the block, west to the gate
        zc = -152.4 + (82.0 - xc) * 0.12
        d.line([L(xc + 0.9, zc - 0.9), L(xc - 0.3, zc), L(xc + 0.9, zc + 0.9)], fill=(40, 90, 200), width=3)
    for (px_, pz_, col) in ((84.25, -146.7, (52, 72, 140)), (88.65, -144.1, (150, 50, 60))):   # people at two tables
        a, b = L(px_ - 0.3, pz_ - 0.3), L(px_ + 0.3, pz_ + 0.3)
        d.ellipse(a + b, fill=col)
        a, b = L(px_ - 0.15, pz_ - 0.15), L(px_ + 0.15, pz_ + 0.15)
        d.ellipse(a + b, fill=(70, 45, 30))
    for (bx, bz) in ((55.3, -132.2), (64.7, -132.2), (55.3, -125.8), (64.7, -125.8)):
        a, b = L(bx - 0.9, bz - 0.25), L(bx + 0.9, bz + 0.25)
        d.rectangle(a + b, fill=BENCH)
    # lamps: all as now, but the gate's east lamp at the block's kerb and the west one gone (it stood in the road)
    lamps = [tuple(l['pos']) for l in SJ['lamps'] if X0 < l['pos'][0] < X1 and Z0 < l['pos'][1] < Z1]
    lamps = [p for p in lamps if p not in ((100.0, -138.5), (112.0, -138.5)) and not (47 < p[0] < 73 and -137 < p[1] < -121)]
    lamps += [(87.6, -148.2), (112.0, -134.45), (48.0, -136.6), (72.0, -136.6), (48.0, -121.4), (72.0, -121.4)]
    for (x, z) in lamps:
        p = L(x, z)
        d.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), fill=(255, 215, 0), outline='black', width=2)
    return img


if __name__ == '__main__':
    before = A.crop(P(X0, Z0) + P(X1, Z1))
    after = plan()
    W = 1400
    sc = W / before.width
    before, after = before.resize((W, round(before.height * sc))), after.resize((W, round(after.height * sc)))
    f = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 24)
    out = Image.new('RGB', (W, before.height * 2 + 80), 'white')
    out.paste(before, (0, 34))
    out.paste(after, (0, before.height + 80))
    dd = ImageDraw.Draw(out)
    dd.text((10, 4), 'now', fill='black', font=f)
    dd.text((10, before.height + 48), 'mock-up  (yellow: street lamps;  blue dashes: the level terrace;  blue arrows: the ramp up to the gate)', fill='black', font=f)
    out.save(sys.argv[3], quality=90)
