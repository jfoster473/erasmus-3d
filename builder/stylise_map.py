# Turns the game's own picture of the world from straight above (tests.gd --mapshot) into the map shown
# with M: softened a little like a painted map (fine detail evened out, colours warmed and strengthened,
# the edges of things gently inked), on a cream paper border. The names of buildings and streets are not
# painted in: the game writes them on top, crisp at any size (main.gd, map labels).
#
# Round 24, the user: "Make the map just a city map like it was (that was good), with arrows to the other sections,
# with the names at the end of the arrow. Maybe those sections can be stylised at the end of the arrows, but the city
# is what she needs a map for." So: the city (with the river, the beach and the eastern wood) fills the map; above it,
# on the paper, an inked arrow from where each way out of town leaves it (the path and the cable car at the hill's
# foot; the street up through Gràcia) to a round picture of where it goes (the funfair on Tibidabo; Gràcia and Park
# Güell), painted the same way, with its name. world.json says where everything is, for the game's "you are here"
# (in one of the round pictures when she's up there).
#   python3 stylise_map.py <mapshot.png> <out dir: godot/map>   (writes world.png and world.json)
import sys, os, json, math
from PIL import Image, ImageFilter, ImageEnhance, ImageChops, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
shot = Image.open(src).convert('RGB')
meta = json.load(open(os.path.splitext(src)[0] + '.json'))      # the shot's own edges: x0, z0, w_m, h_m (metres)
SX, SZ = shot.size[0] / meta['w_m'], shot.size[1] / meta['h_m']   # pixels to the metre in the shot


def crop_m(x0, z0, x1, z1):
    return shot.crop((round((x0 - meta['x0']) * SX), round((z0 - meta['z0']) * SZ), round((x1 - meta['x0']) * SX), round((z1 - meta['z0']) * SZ)))


def paint(im, width):
    """The painted-map look: detail evened out, warmed, inked edges."""
    im = im.filter(ImageFilter.MedianFilter(5))
    im = im.resize((width, round(im.size[1] * width / im.size[0])), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.18)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    warm = Image.new('RGB', im.size, (255, 238, 210))
    im = Image.blend(im, ImageChops.multiply(im, warm), 0.35)
    edges = im.convert('L').filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 38 else int(v * 3))
    edges = edges.filter(ImageFilter.GaussianBlur(0.6))
    ink = Image.new('RGB', im.size, (92, 62, 40))
    return Image.composite(ink, im, edges.point(lambda v: int(v * 0.42)))


# the city: from the hill's foot to the sea, the river to the wood's far side
CITY = {'x0': meta['x0'], 'z0': -116.0, 'x1': meta['x0'] + meta['w_m'], 'z1': meta['z0'] + meta['h_m']}
TW = 2400
city = paint(crop_m(CITY['x0'], CITY['z0'], CITY['x1'], CITY['z1']), TW)
K = TW / (CITY['x1'] - CITY['x0'])                                 # map pixels to the metre

B = 46                    # the paper's border
BAND = 400                # the paper above the city, for the ways out (round 25: was 720)
INK = (92, 62, 40)
RULE = ((10, (138, 93, 59)), (16, (196, 106, 69)))
paper = Image.new('RGB', (TW + 2 * B, city.size[1] + BAND + 2 * B), (244, 234, 210))
paper.paste(city, (B, B + BAND))
d = ImageDraw.Draw(paper)
for k, col in RULE:
    d.rectangle([B - k, B - k, paper.size[0] - B + k - 1, paper.size[1] - B + k - 1], outline=col, width=3)
# (a fine rule along the city's top edge, where the paper begins)
d.line([(B, B + BAND - 2), (B + TW, B + BAND - 2)], fill=(138, 93, 59), width=3)


def city_px(x, z):
    return (B + (x - CITY['x0']) * K, B + BAND + (z - CITY['z0']) * K)


FONT = '/System/Library/Fonts/Supplemental/'
try:
    f_name = ImageFont.truetype(FONT + 'Georgia Bold Italic.ttf', 40)
    f_sub = ImageFont.truetype(FONT + 'Georgia Italic.ttf', 26)
except OSError:
    f_name = f_sub = ImageFont.load_default()

# the ways out: (name, small print, where it leaves the city (metres), the round picture's middle and half-size (metres),
# the picture's centre on the paper (pixels from the map's left), its radius (pixels))
# (round 25, the user: "the parts at the top are too large. Make them smaller, like the size of the buildings": a
# round picture about a city block across)
WAYS = [("Tibidabo", "the funfair, by the path or the cable car", (-80.0, -112.0), (-62.0, -281.0), 49.0, 640, 250),
        ("Gràcia & Park Güell", "up through Gràcia's little streets", (96.0, -112.0), (110.0, -196.0), 66.0, 1760, 250)]
insets = []
R = 105
for (name, sub, leave, mid, half, cx, cy) in WAYS:
    pic = paint(crop_m(mid[0] - half, mid[1] - half, mid[0] + half, mid[1] + half), 2 * R)
    mask = Image.new('L', pic.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 2 * R - 1, 2 * R - 1], fill=255)
    ccx, ccy = B + cx, B + cy
    paper.paste(pic, (ccx - R, ccy - R), mask)
    for k, col in ((0, (138, 93, 59)), (7, (196, 106, 69))):
        d.ellipse([ccx - R - k, ccy - R - k, ccx + R + k, ccy + R + k], outline=col, width=4)
    # the arrow: from where the way leaves the city, curving up to the picture's rim
    sx, sy = city_px(*leave)
    ex, ey = ccx + (sx - ccx) * 0.0, ccy + R + 18
    if abs(sx - ccx) > 40:
        ang = math.atan2(sy - ccy, sx - ccx)
        ex, ey = ccx + math.cos(ang) * (R + 18), ccy + math.sin(ang) * (R + 18)
    mx, my = (sx + ex) / 2 + (40 if sx < ex else -40), (sy + ey) / 2 + 30
    curve = [((1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * ex, (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t * t * ey)
             for t in [i / 40 for i in range(41)]]
    for i in range(0, 40, 2):                                          # (dashed, like a route on an old map)
        d.line([curve[i], curve[i + 1]], fill=INK, width=7)
    hx, hy = curve[-1]
    bx_, by_ = curve[-4]
    a = math.atan2(hy - by_, hx - bx_)
    for s in (2.6, -2.6):
        d.line([(hx, hy), (hx + math.cos(a + s) * 34, hy + math.sin(a + s) * 34)], fill=INK, width=8)
    d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=INK)
    # its name above the picture, the small print under the name
    tw = d.textlength(name, font=f_name)
    d.text((ccx - tw / 2 + 2, ccy - R - 92 + 2), name, font=f_name, fill=(255, 250, 238))
    d.text((ccx - tw / 2, ccy - R - 92), name, font=f_name, fill=(120, 52, 34))
    sw = d.textlength(sub, font=f_sub)
    d.text((ccx - sw / 2, ccy - R - 44), sub, font=f_sub, fill=(70, 50, 34))
    insets.append({'name': name, 'x0': mid[0] - half, 'z0': mid[1] - half, 'size_m': 2 * half, 'cx': ccx, 'cy': ccy, 'r': R})

paper.save(os.path.join(out, 'world.png'))
info = {'x0': CITY['x0'], 'z0': CITY['z0'], 'w_m': CITY['x1'] - CITY['x0'], 'h_m': CITY['z1'] - CITY['z0'],
        'border_px': B, 'off_px': [B, B + BAND], 'map_px': list(city.size), 'size_px': list(paper.size), 'insets': insets}
json.dump(info, open(os.path.join(out, 'world.json'), 'w'), indent=1)
print('map', paper.size, info)
