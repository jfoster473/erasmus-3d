"""Plan maps of the hill path and Park Güell for the user to draw on (round 35).

Straight-down game pictures (tests.gd --views with a plan view, trees and plants hidden), stitched, each area cut
into quarters, with the paths, the railings, the walls and the other solid edges drawn over them from scene.json,
a lettered 10 m grid, and a legend.

  python3 tools/plan_maps.py views <dir>      writes <dir>/views.json (then run the game's --views on it)
  python3 tools/plan_maps.py sheets <dir>     stitches <dir>/tiles/*.png into <dir>/<area>_*.png
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCENE = os.path.join(HERE, '..', 'bigfiles', 'built', 'barcelona', 'scene.json')

PX = 20.0                    # pixels a metre in the game's pictures
TW, TH = 64.0, 40.0          # one picture: 1280 x 800 px
AREAS = {                    # (x0, z0, x1, z1): north (smaller z) at the top
    'hill': (-230.0, -300.0, -54.0, -96.0),
    'park': (44.0, -256.0, 192.0, -136.0),
}
OUT_PX = 15.0                # pixels a metre in the sheets
GRID = 10.0


def tiles(area):
    x0, z0, x1, z1 = AREAS[area]
    nx, nz = math.ceil((x1 - x0) / TW), math.ceil((z1 - z0) / TH)
    return [(i, j, x0 + TW * (i + 0.5), z0 + TH * (j + 0.5)) for j in range(nz) for i in range(nx)]


def write_views(d):
    v = {}
    for area in AREAS:
        for i, j, cx, cz in tiles(area):
            # [from, to, clock, Sandra far away, fov, plan size]
            v['%s_%d_%d' % (area, i, j)] = [cx, 200.0, cz, cx, 0.0, cz + 0.01, 720, 300.0, 300.0, 60, TH]
    os.makedirs(d, exist_ok=True)
    json.dump(v, open(os.path.join(d, 'views.json'), 'w'), indent=0)
    print('%d views' % len(v))


def font(sz):
    from PIL import ImageFont
    for f in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf',
              '/System/Library/Fonts/Helvetica.ttc'):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def col_name(k):
    s = ''
    k += 1
    while k:
        k, r = divmod(k - 1, 26)
        s = chr(65 + r) + s
    return s


def sheets(d):
    from PIL import Image, ImageDraw
    sc = json.load(open(SCENE))
    n = sc['north']
    park = n['park']
    for area in [a for a in AREAS if os.path.exists(os.path.join(d, 'tiles', '%s_0_0.png' % a))]:
        x0, z0, x1, z1 = AREAS[area]
        T = tiles(area)
        nx, nz = max(t[0] for t in T) + 1, max(t[1] for t in T) + 1
        big = Image.new('RGB', (int(nx * TW * PX), int(nz * TH * PX)))
        for i, j, cx, cz in T:
            big.paste(Image.open(os.path.join(d, 'tiles', '%s_%d_%d.png' % (area, i, j))).convert('RGB'),
                      (int(i * TW * PX), int(j * TH * PX)))
        big = big.crop((0, 0, int((x1 - x0) * PX), int((z1 - z0) * PX)))
        img = big.resize((int((x1 - x0) * OUT_PX), int((z1 - z0) * OUT_PX)), Image.LANCZOS)
        img = Image.blend(img, Image.new('RGB', img.size, (255, 255, 255)), 0.12)     # (a little paler: the marks show)
        dr = ImageDraw.Draw(img, 'RGBA')

        def P(x, z):
            return ((x - x0) * OUT_PX, (z - z0) * OUT_PX)

        # the grid, 10 m squares
        for k in range(int((x1 - x0) // GRID) + 1):
            dr.line([P(x0 + k * GRID, z0), P(x0 + k * GRID, z1)], fill=(255, 255, 255, 70), width=1)
        for k in range(int((z1 - z0) // GRID) + 1):
            dr.line([P(x0, z0 + k * GRID), P(x1, z0 + k * GRID)], fill=(255, 255, 255, 70), width=1)
        # what she can't walk through (walls, beds, columns, the funicular's line), outlined
        for poly in sc['solids']:
            if all(x0 - 5 <= q[0] <= x1 + 5 and z0 - 5 <= q[1] <= z1 + 5 for q in poly):
                dr.polygon([P(*q) for q in poly], outline=(230, 0, 230, 230))
        for b in sc['blocked']:
            if x0 <= b[0] <= x1 and z0 <= b[1] <= z1:
                dr.rectangle([P(b[0], b[1]), P(b[2], b[3])], outline=(230, 0, 230, 230))
        # the park wall
        if area == 'park':
            w = park['wall']
            dr.line([P(*q) for q in w], fill=(120, 20, 20, 255), width=6)
        # the railings (rope between posts): red, a dot at each post
        for r in n['rails']:
            a, b = P(r[0], r[1]), P(r[2], r[3])
            dr.line([a, b], fill=(235, 20, 20, 255), width=4)
            for q in (a, b):
                dr.ellipse([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(140, 0, 0, 255))
        # the paths' middle lines, yellow, numbered
        f_lab = font(22)
        if area == 'hill':
            pts = [(p[0], p[1]) for p in n['path']]
            dr.line([P(*q) for q in pts], fill=(255, 225, 0, 255), width=3)
            acc, nxt = 0.0, 0.0
            for a, b in zip(pts, pts[1:]):
                if acc >= nxt:
                    q = P(*a)
                    dr.ellipse([q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6], fill=(255, 225, 0, 255), outline=(0, 0, 0))
                    lab = '%d m' % nxt
                    dr.text((q[0] + 9, q[1] - 12), lab, font=f_lab, fill=(0, 0, 0), stroke_width=3, stroke_fill=(255, 255, 255))
                    nxt += 50.0
                acc += math.hypot(b[0] - a[0], b[1] - a[1])
        else:
            for k, pl in enumerate(park['paths']):
                dr.line([P(*q) for q in pl], fill=(255, 225, 0, 255), width=3)
            for k, pl in enumerate(park['paths']):
                lab = 'walk' if k == len(park['paths']) - 1 else str(k + 1)
                m_ = pl[len(pl) // 2] if len(pl) > 2 else ((pl[0][0] + pl[1][0]) / 2, (pl[0][1] + pl[1][1]) / 2)
                q = P(*m_)
                dr.ellipse([q[0] - 15, q[1] - 15, q[0] + 15, q[1] + 15], fill=(255, 225, 0, 255), outline=(0, 0, 0), width=2)
                tw = dr.textlength(lab, font=f_lab)
                dr.text((q[0] - tw / 2, q[1] - 13), lab, font=f_lab, fill=(0, 0, 0))
            rd = park['road']
            dr.line([P(*q) for q in rd], fill=(255, 150, 0, 255), width=3)
        # (the measured breaches of docs/PATH_RULES.md, from tools/path_rules.py, ringed with their rule)
        bf = os.path.join(d, 'breaches.json')
        if os.path.exists(bf):
            f_b = font(16)
            for b_ in json.load(open(bf)):
                if x0 <= b_['x'] <= x1 and z0 <= b_['z'] <= z1:
                    q = P(b_['x'], b_['z'])
                    dr.ellipse([q[0] - 14, q[1] - 14, q[0] + 14, q[1] + 14], outline=(0, 120, 255, 255), width=3)
                    dr.text((q[0] + 15, q[1] - 22), b_['rule'], font=f_b, fill=(0, 60, 200), stroke_width=2, stroke_fill=(255, 255, 255))
        img.save(os.path.join(d, '%s_whole.png' % area))
        # quarters, each with its grid letters and a legend
        W, H = img.size
        names = [('1 top left', 0, 0), ('2 top right', 1, 0), ('3 bottom left', 0, 1), ('4 bottom right', 1, 1)]
        ncol, nrow = int(math.ceil((x1 - x0) / GRID)), int(math.ceil((z1 - z0) / GRID))
        hc, hr = ncol // 2, nrow // 2
        for nm, qi, qj in names:
            c0, c1 = (0, hc + 1) if qi == 0 else (hc, ncol)          # (a square's overlap with the next quarter)
            r0, r1 = (0, hr + 1) if qj == 0 else (hr, nrow)
            box = (int(c0 * GRID * OUT_PX), int(r0 * GRID * OUT_PX), min(W, int(c1 * GRID * OUT_PX)), min(H, int(r1 * GRID * OUT_PX)))
            q = img.crop(box)
            M, LEG = 34, 70
            sheet = Image.new('RGB', (q.size[0] + M, q.size[1] + M + LEG), (255, 255, 255))
            sheet.paste(q, (M, M))
            ds = ImageDraw.Draw(sheet)
            f_g = font(18)
            for c in range(c0, c1):
                x_ = M + (c - c0 + 0.5) * GRID * OUT_PX
                if x_ < sheet.size[0]:
                    lab = col_name(c)
                    ds.text((x_ - ds.textlength(lab, font=f_g) / 2, 7), lab, font=f_g, fill=(0, 0, 0))
            for r in range(r0, r1):
                y_ = M + (r - r0 + 0.5) * GRID * OUT_PX
                if y_ < M + q.size[1]:
                    lab = str(r + 1)
                    ds.text((M - 5 - ds.textlength(lab, font=f_g), y_ - 10), lab, font=f_g, fill=(0, 0, 0))
            ly = M + q.size[1] + 10
            f_s = font(17)
            title = ('Hill path' if area == 'hill' else 'Park Güell') + ' — quarter ' + nm + '   (north at the top; squares 10 m)'
            ds.text((M, ly), title, font=f_s, fill=(0, 0, 0))
            lx, ly2 = M, ly + 28
            items = [((255, 225, 0), 'path (middle line)'), ((235, 20, 20), 'rope railing, dots = posts'),
                     ((230, 0, 230), 'solid edge (she can\'t walk through)')]
            if area == 'park':
                items += [((120, 20, 20), 'park wall'), ((255, 150, 0), 'road outside the wall')]
            for colr, txt in items:
                ds.rectangle([lx, ly2 + 4, lx + 26, ly2 + 14], fill=colr)
                ds.text((lx + 32, ly2), txt, font=f_s, fill=(0, 0, 0))
                lx += 32 + ds.textlength(txt, font=f_s) + 24
            sheet.save(os.path.join(d, '%s_%s.png' % (area, nm.split()[0])))
        # the whole area, small, with the quarters marked
        sm = img.resize((W // 2, H // 2), Image.LANCZOS)
        ds = ImageDraw.Draw(sm)
        for nm, qi, qj in names:
            c0, c1 = (0, hc + 1) if qi == 0 else (hc, ncol)
            r0, r1 = (0, hr + 1) if qj == 0 else (hr, nrow)
            bx = [c0 * GRID * OUT_PX / 2, r0 * GRID * OUT_PX / 2, min(W, c1 * GRID * OUT_PX) / 2 - 1, min(H, r1 * GRID * OUT_PX) / 2 - 1]
            ds.rectangle(bx, outline=(0, 0, 0), width=3)
            ds.text((bx[0] + 10, bx[1] + 8), nm.split()[0], font=font(40), fill=(0, 0, 0), stroke_width=3, stroke_fill=(255, 255, 255))
        sm.save(os.path.join(d, '%s_0_overview.png' % area))
        print(area, img.size)


if __name__ == '__main__':
    {'views': write_views, 'sheets': sheets}[sys.argv[1]](sys.argv[2])
