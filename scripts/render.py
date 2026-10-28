from pathlib import Path
import argparse, json, math, subprocess, sys
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--input', type=Path, default=ROOT / 'output/presentation.pptx')
parser.add_argument('--output', type=Path, default=ROOT / 'output/previews')
args = parser.parse_args()
previews = args.output.resolve()
previews.mkdir(parents=True, exist_ok=True)
result = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                         str(ROOT / 'scripts/render.ps1'), '-InputPath', str(args.input.resolve()),
                         '-OutputDir', str(previews)], cwd=ROOT,
                        text=True, capture_output=True, timeout=600)
print(result.stdout)
if result.returncode:
    print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
meta = json.loads((previews / 'render-metadata.json').read_text(encoding='utf-8-sig'))
files = [previews / f'slide{i:02d}.png' for i in range(1, meta['slides'] + 1)]
if not all(p.exists() for p in files): sys.exit('Missing previews')

def montage(items, name, offset=0, thumb_w=480, cols=4):
    thumb_h = round(thumb_w * 9 / 16)
    row_h = thumb_h + 28
    sheet = Image.new('RGB', (cols * thumb_w, math.ceil(len(items) / cols) * row_h), '#e9eef1')
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(items):
        with Image.open(path) as im:
            thumb = ImageOps.fit(im.convert('RGB'), (thumb_w, thumb_h))
            x, y = (i % cols) * thumb_w, (i // cols) * row_h
            sheet.paste(thumb, (x, y))
            draw.text((x + 8, y + thumb_h + 6), f'{offset+i+1:02d}', fill='#172534')
    sheet.save(previews / name)
montage(files, 'overview.png', thumb_w=400)
for start in range(0, len(files), 12):
    montage(files[start:start+12], f'overview-{start//12+1:02d}.png', offset=start)
print(f'Rendered {len(files)} slides and montages.')
