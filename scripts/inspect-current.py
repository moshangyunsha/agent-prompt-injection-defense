from pathlib import Path
from zipfile import ZipFile
import json
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with ZipFile(ROOT/'output/presentation.pptx') as z:
    data=[]
    for i in range(1,27):
        slide=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        root=E.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        body=next(s for s in root.findall('.//p:sp',NS) if (s.find('p:nvSpPr/p:nvPr/p:ph',NS) is not None and s.find('p:nvSpPr/p:nvPr/p:ph',NS).get('type')=='body'))
        paragraphs=[''.join(t.text or '' for t in p.findall('.//a:t',NS)) for p in body.findall('p:txBody/a:p',NS)]
        data.append({'oldPage':i,'notes':'\n'.join(paragraphs),'paragraphs':paragraphs,'visibleText':''.join(t.text or '' for t in slide.findall('.//a:t',NS)), 'bodyXml':E.tostring(body,encoding='unicode')})
    (ROOT/'output/archive/user-edited-notes.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    for i in [1,2,8,19,24,25,26]:
        print(f'\n=== PAGE {i} ===\n{data[i-1]["notes"]}')
    print('\n=== FORMAT PAGE 8 ===\n'+data[7]['bodyXml'][:6500])
