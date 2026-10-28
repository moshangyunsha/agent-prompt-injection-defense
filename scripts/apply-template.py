"""Reuse native template rule/footer and its theme, without its fictional affiliation."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import copy
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
for prefix, uri in NS.items(): E.register_namespace(prefix, uri)
E.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')

def apply():
    template = next(ROOT.joinpath('input').glob('*.pptx'))
    dest = ROOT / 'output/presentation.pptx'
    with ZipFile(template) as z:
        theme = z.read('ppt/theme/theme1.xml')
        layout = E.fromstring(z.read('ppt/slideLayouts/slideLayout14.xml'))
        header = layout.find('.//p:cxnSp', NS)
        source = E.fromstring(z.read('ppt/slides/slide67.xml'))
        footer = next(s for s in source.findall('.//p:sp', NS)
                      if s.find('p:nvSpPr/p:cNvPr', NS).get('name') == '矩形 94')
    raw = ROOT / 'output/archive/presentation-before-template.pptx'
    raw.write_bytes(dest.read_bytes())
    with ZipFile(dest) as z: files = {n: z.read(n) for n in z.namelist()}
    files['ppt/theme/theme1.xml'] = theme
    master = E.fromstring(files['ppt/slideMasters/slideMaster1.xml'])
    tree = master.find('p:cSld/p:spTree', NS)
    for index, shape in enumerate([header, footer]):
        native = copy.deepcopy(shape)
        if index == 1:
            # The template footer overscans its slide by 0.027in; clip to 16:9 canvas.
            xfrm = native.find('p:spPr/a:xfrm', NS)
            xfrm.find('a:ext', NS).set('cy', str(6858000 - int(xfrm.find('a:off', NS).get('y'))))
        ident = native.find('.//p:cNvPr', NS)
        ident.set('id', str(800 + index))
        ident.set('name', ['Template academic title rule', 'Template academic footer'][index])
        tree.append(native)
    files['ppt/slideMasters/slideMaster1.xml'] = E.tostring(master, encoding='utf-8', xml_declaration=True)
    with ZipFile(dest, 'w', ZIP_DEFLATED) as z:
        for name, content in files.items(): z.writestr(name, content)
    print('Applied native title rule/footer and blue academic theme from supplied template.')

if __name__ == '__main__': apply()
