# The everything-visit's sheets (round 35): visit_sheet.py <part folder> [per sheet] [width] [from picture]
# Lays out a --visit part's 10 s pictures, captioned from its pictures.txt (number, place, x,z, what she was at);
# writes sheets/s_NNN.jpg in that folder.
import os, sys
from PIL import Image, ImageDraw, ImageFont
src = sys.argv[1]; per = int(sys.argv[2]) if len(sys.argv) > 2 else 6; w = int(sys.argv[3]) if len(sys.argv) > 3 else 640
first = int(sys.argv[4]) if len(sys.argv) > 4 else 1
cols = 3
rows_ = [l.split("\t") for l in open(os.path.join(src, "pictures.txt"), encoding="utf-8").read().splitlines()[1:]]
rows_ = [f for f in rows_ if len(f) >= 5 and int(f[0]) >= first and os.path.exists(os.path.join(src, "pictures", f[0] + ".jpg"))]
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
out = os.path.join(src, "sheets"); os.makedirs(out, exist_ok=True)
h = int(w * 800 / 1280); cap = 22
for s in range(0, len(rows_), per):
    chunk = rows_[s:s + per]; rows = (len(chunk) + cols - 1) // cols
    S = Image.new("RGB", (w * cols, (h + cap) * rows), "white"); d = ImageDraw.Draw(S)
    for i, f in enumerate(chunk):
        im = Image.open(os.path.join(src, "pictures", f[0] + ".jpg")).convert("RGB")
        x, y = (i % cols) * w, (i // cols) * (h + cap)
        S.paste(im.resize((w, h)), (x, y))
        d.rectangle([x, y + h, x + w - 1, y + h + cap - 1], fill="black")
        d.text((x + 6, y + h + 3), "%s %s (%s) · %s" % (f[0], f[2][:28], f[3], f[4][:40]), fill="white", font=font)
    S.save(os.path.join(out, "s_%s.jpg" % chunk[0][0]), quality=86)
print(len(rows_), "pictures")
