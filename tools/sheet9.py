import sys, os
from PIL import Image, ImageDraw, ImageFont
d, out, pre = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ''
names = sorted(f for f in os.listdir(d) if f.endswith('.png') and f.startswith(pre))
W, H, C = 560, 350, 3
f = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 18)
os.makedirs(out, exist_ok=True)
for s in range(0, len(names), 9):
    grp = names[s:s + 9]
    rows = (len(grp) + C - 1) // C
    sh = Image.new('RGB', (W * C, (H + 24) * rows), 'white')
    dr = ImageDraw.Draw(sh)
    for k, n in enumerate(grp):
        im = Image.open(os.path.join(d, n)).convert('RGB').resize((W, H))
        x, y = (k % C) * W, (k // C) * (H + 24)
        sh.paste(im, (x, y + 24)); dr.text((x + 6, y + 2), n[:-4], font=f, fill='black')
    sh.save(os.path.join(out, '%s%02d.jpg' % (pre or 's', s // 9)), quality=85)
print(len(names))
