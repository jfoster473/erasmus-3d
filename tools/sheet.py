# contact sheet: sheet.py out.png w cols img...  (labels each tile with its file name)
import sys
from PIL import Image, ImageDraw
out, w, cols = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ims = [(p.split('/')[-1].rsplit('.', 1)[0], Image.open(p).convert('RGB')) for p in sys.argv[4:]]
h = int(w * ims[0][1].height / ims[0][1].width)
rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (w * cols, h * rows), 'white')
d = ImageDraw.Draw(S)
for i, (n, im) in enumerate(ims):
    x, y = (i % cols) * w, (i // cols) * h
    S.paste(im.resize((w, h)), (x, y))
    d.rectangle([x, y, x + 8 * len(n) + 8, y + 16], fill='black')
    d.text((x + 4, y + 2), n, fill='white')
S.save(out)
