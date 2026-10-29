import sys, glob
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(f'{src}/slide-*.png'))
for k in range(0, len(files), 6):
    ims = [Image.open(f).resize((800, 450)) for f in files[k:k+6]]
    sheet = Image.new('RGB', (1620, 1390), 'white'); d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        x, y = 10 + (i % 2) * 810, 10 + (i // 2) * 460
        sheet.paste(im, (x, y)); d.text((x + 5, y + 5), files[k + i][-6:-4], fill='red')
    sheet.save(f'{out}-{k//6+1}.png')
print('ok')
