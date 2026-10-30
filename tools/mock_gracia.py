# Gràcia's south quarter, option A, sixth pass: every sidewalk is one seamless piece that wraps its building's
# corners (lines only on true outer edges); the cobbles are bounded by a continuous footpath that runs UNDER
# them at every street's end; ONE gravel path in the forest, well apart, the old one's remnants covered.
import sys
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]
A = Image.open(S + '/m2.png').convert('RGB')
k = 5148 / 429.0
X0, Z0, X1, Z1 = 62, -122, 146, -40


def P(x, z): return (round((x + 232) * k), round((z + 330) * k))
def L(x, z): return (round((x - X0) * k), round((z - Z0) * k))
def grab(x0, z0, x1, z1): return A.crop(P(x0, z0) + P(x1, z1))


SETT = grab(104, -60, 123, -55.2)
PAVE = grab(83.2, -80, 85.3, -60)
GRASS = grab(130.2, -61.8, 132.6, -54)
ROOF = grab(106.5, -115, 124, -100)
TREE = grab(95.6, -113.6, 100.2, -108.8)
FLOOR = grab(90.3, -72.8, 91.8, -71.3)
_c = sorted(FLOOR.getdata(), key=sum)[len(FLOOR.getdata()) * 3 // 4]
FLOOR = Image.new('RGB', (13, 13), _c)
_d = tuple(v - 10 for v in _c)
ImageDraw.Draw(FLOOR).line((0, 12, 12, 12), fill=_d)
ImageDraw.Draw(FLOOR).line((12, 0, 12, 12), fill=_d)
ASTRO = grab(91.6, -74.9, 93.4, -73.1)
TABLE = grab(95.3, -75.4, 97.1, -73.6)
KERBC = (122, 120, 118)
GRAVEL = (208, 200, 180)
STONE = (150, 140, 125)

tmask = TREE.copy().convert('L')
tp, mp = TREE.load(), tmask.load()
for j in range(TREE.height):
    for i in range(TREE.width):
        R, G, B = tp[i, j]
        mp[i, j] = 255 if (G > R + 8 and G > B + 20) else 0


def fill(img, tex, x0, z0, x1, z1):
    a, b = L(x0, z0), L(x1, z1)
    for y in range(a[1], b[1], tex.height):
        for x in range(a[0], b[0], tex.width):
            img.paste(tex.crop((0, 0, min(tex.width, b[0] - x), min(tex.height, b[1] - y))), (x, y))


def centre_paste(img, src, x, z):
    p = L(x, z)
    img.paste(src, (p[0] - src.width // 2, p[1] - src.height // 2))


def tree(img, x, z):
    p = L(x, z)
    img.paste(TREE, (p[0] - TREE.width // 2, p[1] - TREE.height // 2), tmask)


def path(img, pts, w):
    d = ImageDraw.Draw(img)
    q = [L(*p) for p in pts]
    d.line(q, fill=GRAVEL, width=round(w * k), joint='curve')
    for p in q:
        r = w * k / 2
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=GRAVEL)


def plan():
    img = A.crop(P(X0, Z0) + P(X1, Z1))
    d = ImageDraw.Draw(img)
    ln = lambda a, b: d.line(L(*a) + L(*b), fill=KERBC)
    # the gate street, straight through; its sidewalks wrap the blocks' corners in one piece
    fill(img, SETT, 98.5, -122.0, 103.5, -92.8)
    fill(img, PAVE, 95.5, -122.0, 98.5, -98.2)                 # west sidewalk, and round the corner westwards
    fill(img, PAVE, 75.2, -100.0, 95.5, -98.2)
    ln((98.5, -122.0), (98.5, -98.2)); ln((75.2, -98.2), (98.5, -98.2))
    fill(img, PAVE, 103.5, -122.0, 106.5, -98.2)               # east sidewalk, round the corner to the lane
    fill(img, PAVE, 106.5, -100.0, 125.8, -98.2)
    fill(img, PAVE, 124.0, -116.8, 125.8, -100.0)
    ln((103.5, -122.0), (103.5, -98.2)); ln((103.5, -98.2), (125.8, -98.2)); ln((125.8, -116.8), (125.8, -98.2))
    # the quarter: one field of setts, bounded east by the footpath
    fill(img, SETT, 86.0, -98.2, 128.8, -48.8)
    fill(img, SETT, 125.8, -122.0, 128.8, -98.2)               # the lane runs on north
    # the bounding footpath along the wood: continuous, the cobbles stop on it at every street's end
    fill(img, PAVE, 128.8, -122.0, 130.6, -47.0)
    ln((128.8, -122.0), (128.8, -48.8)); ln((130.6, -122.0), (130.6, -47.0))
    # the town's south edge: Provença's far pavement joins the footpath, grass beyond
    fill(img, PAVE, 86.0, -48.8, 128.8, -47.0)
    ln((86.0, -48.8), (128.8, -48.8))
    fill(img, GRASS, 86.0, -47.0, 130.6, -40.0)
    # the city street's own pavement runs through along the west, and the square's ring merges with it
    fill(img, PAVE, 84.3, -98.2, 86.0, -47.0)
    fill(img, PAVE, 84.3, -92.8, 98.5, -53.2)
    ln((98.5, -92.8), (98.5, -53.2)); ln((86.0, -92.8), (98.5, -92.8)); ln((86.0, -53.2), (98.5, -53.2))
    ln((84.3, -98.2), (84.3, -47.0))
    fill(img, FLOOR, 88.0, -90.8, 96.5, -72.8)
    centre_paste(img, ASTRO, 92.25, -81.8)
    for tz in (-78.0, -82.0, -86.0):
        centre_paste(img, TABLE, 95.1, tz)
    a, b = L(88.0, -69.0), L(96.5, -55.0)
    img.paste(ROOF.resize((b[0] - a[0], b[1] - a[1]), Image.LANCZOS), a)
    # the two house blocks, their sidewalks one ring each
    for (zt, zb) in ((-92.8, -75.2), (-70.8, -53.2)):
        fill(img, PAVE, 103.5, zt, 125.8, zb)
        d.rectangle(L(103.5, zt) + L(125.8, zb), outline=KERBC)
        a, b = L(106.5, zt + 1.8), L(124.0, zb - 1.8)
        img.paste(ROOF.resize((b[0] - a[0], b[1] - a[1]), Image.LANCZOS), a)
    # grass from the footpath to the forest, wide enough to cover the old path's remains
    fill(img, GRASS, 130.6, -122.0, 135.6, -40.0)
    # the drystone wall, gaps only at the streets' ends
    for (za, zb) in ((-121.0, -97.2), (-93.8, -75.6), (-70.4, -50.2)):
        d.rectangle(L(130.9, za) + L(131.5, zb), fill=STONE, outline=(110, 100, 90))
    # ONE gravel path in the forest, apart from the wall, entering the town at the streets' ends only
    path(img, [(133.6, -121.0), (133.2, -110.0), (133.7, -98.5), (133.2, -88.0), (133.7, -78.0),
               (133.2, -68.0), (133.7, -58.0), (133.4, -47.5), (133.2, -40.5)], 1.9)
    path(img, [(130.6, -95.5), (133.5, -95.5)], 1.9)
    path(img, [(130.6, -73.0), (133.4, -73.0)], 1.9)
    path(img, [(130.6, -47.9), (133.4, -47.9)], 1.9)
    # trees: the square's corners, and along the gate street's wide pavement
    for (tx, tz) in ((89.9, -88.6), (94.6, -88.6), (89.9, -75.0), (94.6, -75.0),
                     (105.0, -88.5), (105.0, -78.5), (105.0, -66.5), (105.0, -56.5)):
        tree(img, tx, tz)
    return img


def label(img, text):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia Bold.ttf', 40)
    d.rectangle((0, 0, img.width, 58), fill=(244, 234, 214))
    d.text((16, 6), text, fill=(110, 40, 30), font=f)
    return img


now = label(A.crop(P(X0, Z0) + P(X1, Z1)), 'Now')
a = plan()
zoom = a.crop(L(84.0, -122.0) + L(137.5, -40.0))
zoom = zoom.resize((round(zoom.width * 1.5), round(zoom.height * 1.5)), Image.LANCZOS)
zoom.save(S + '/gracia_mock7_zoom.jpg', quality=90)
jz = a.crop(L(88.0, -112.0) + L(114.0, -90.0))
jz = jz.resize((round(jz.width * 2.4), round(jz.height * 2.4)), Image.LANCZOS)
jz.save(S + '/gracia_mock7_junction.jpg', quality=90)
ez = a.crop(L(122.0, -100.0) + L(137.5, -44.0))
ez = ez.resize((round(ez.width * 2.2), round(ez.height * 2.2)), Image.LANCZOS)
ez.save(S + '/gracia_mock7_east.jpg', quality=90)
a = label(a, 'A, sixth pass')
W, H = now.size
sheet = Image.new('RGB', (W * 2 + 20, H), (244, 234, 214))
sheet.paste(now, (0, 0))
sheet.paste(a, (W + 20, 0))
sheet.save(S + '/gracia_mock7.jpg', quality=90)
print(sheet.size, zoom.size)
