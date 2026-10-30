# The picture tour's sheets (round 32): tour_sheet.py <playthrough folder> [per sheet] [width]
# Reads index.txt and pictures/NNN.jpg from tests.gd --playthrough and lays them out, a caption under each one:
# its number, the place, the time into the play and the game's clock. Writes sheets/tour_NN.jpg in that folder.
import os
import sys
from PIL import Image, ImageDraw, ImageFont

src = sys.argv[1]
per = int(sys.argv[2]) if len(sys.argv) > 2 else 12
w = int(sys.argv[3]) if len(sys.argv) > 3 else 520
cols = 3 if per <= 9 else 4
rows_ = []
for line in open(os.path.join(src, "index.txt"), encoding="utf-8").read().splitlines()[1:]:
    f = line.split("\t")
    if len(f) >= 6 and os.path.exists(os.path.join(src, "pictures", f[0] + ".jpg")):
        rows_.append(f)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
except OSError:
    font = ImageFont.load_default()
out = os.path.join(src, "sheets")
os.makedirs(out, exist_ok=True)
for old in os.listdir(out):
    os.remove(os.path.join(out, old))
h = int(w * 800 / 1280)
cap = 22
for s in range(0, len(rows_), per):
    chunk = rows_[s:s + per]
    rows = (len(chunk) + cols - 1) // cols
    S = Image.new("RGB", (w * cols, (h + cap) * rows), "white")
    d = ImageDraw.Draw(S)
    for i, f in enumerate(chunk):
        im = Image.open(os.path.join(src, "pictures", f[0] + ".jpg")).convert("RGB")
        x, y = (i % cols) * w, (i // cols) * (h + cap)
        S.paste(im.resize((w, h)), (x, y))
        d.rectangle([x, y + h, x + w - 1, y + h + cap - 1], fill="black")
        d.text((x + 6, y + h + 3), "%s  %s  · play %s · clock %s" % (f[0], f[3], f[1], f[2]), fill="white", font=font)
    S.save(os.path.join(out, "tour_%02d.jpg" % (s // per + 1)), quality=88)
print("%d pictures on %d sheets in %s" % (len(rows_), (len(rows_) + per - 1) // per, out))
