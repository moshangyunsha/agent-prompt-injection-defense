from pathlib import Path
import json
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
result=[]
for old in range(1,27):
    if old in [2,24,25]:continue
    new=old if old==1 else old+1
    a=Image.open(ROOT/f'output/user-baseline-previews/slide{old:02}.png').convert('RGB').crop((0,0,1600,830))
    b=Image.open(ROOT/f'output/previews/slide{new:02}.png').convert('RGB').crop((0,0,1600,830))
    bbox=ImageChops.difference(a,b).getbbox()
    result.append({'oldPage':old,'newPage':new,'bodyUnchanged':bbox is None,'difference':bbox})
(ROOT/'output/revision-preservation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(f'Unchanged page bodies: {sum(r["bodyUnchanged"] for r in result)} / {len(result)} (footer numbering excluded).')
for row in result:
    if not row['bodyUnchanged']:print(row)
if not all(r['bodyUnchanged'] for r in result):raise SystemExit(1)
