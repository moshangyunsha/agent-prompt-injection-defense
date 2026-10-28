"""Insert the agenda and replace only the plan, retaining the user's reviewed deck."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.dom import minidom as M
import json, copy, re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'output/archive/presentation-user-edited-before-agenda.pptx'
TARGET=ROOT/'output/presentation.pptx'
manifest=json.loads((ROOT/'output/page-manifest.json').read_text(encoding='utf-8'))
assert len(manifest)==27 and manifest[1]['oldPage']==0
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'

def doc(b): return M.parseString(b)
def xml(d): return d.toxml(encoding='UTF-8')
def value(n): return ''.join(c.data for c in n.childNodes if c.nodeType==c.TEXT_NODE)
def replace_text(n,t):
    for c in list(n.childNodes):n.removeChild(c)
    n.appendChild(n.ownerDocument.createTextNode(t))
def body(d):
    return next(s for s in d.getElementsByTagName('p:sp') if any(ph.getAttribute('type')=='body' for ph in s.getElementsByTagName('p:ph')))

with ZipFile(BASE) as z: entries={n:z.read(n) for n in z.namelist()}
with ZipFile(TARGET) as z: new={n:z.read(n) for n in z.namelist()}
notes_template=body(doc(entries['ppt/notesSlides/notesSlide1.xml'])).getElementsByTagName('p:txBody')[0]
template_p=notes_template.getElementsByTagName('a:p')[0]

def set_notes(raw,script):
    d=doc(raw); b=body(d); old=b.getElementsByTagName('p:txBody')[0]
    tx=d.importNode(notes_template,True)
    for c in list(tx.childNodes):
        if c.nodeType==c.ELEMENT_NODE and c.tagName=='a:p':tx.removeChild(c)
    for paragraph in script.splitlines():
        if not paragraph.strip():continue
        p=d.importNode(template_p,True)
        for c in list(p.childNodes):
            if c.nodeType==c.ELEMENT_NODE and c.tagName not in ['a:pPr','a:endParaRPr']:p.removeChild(c)
        r=d.createElementNS(A,'a:r')
        sample=template_p.getElementsByTagName('a:rPr')
        if sample:r.appendChild(d.importNode(sample[0],True))
        t=d.createElementNS(A,'a:t');t.appendChild(d.createTextNode(paragraph));r.appendChild(t)
        end=p.getElementsByTagName('a:endParaRPr')
        if end:p.insertBefore(r,end[0])
        else:p.appendChild(r)
        tx.appendChild(p)
    b.replaceChild(tx,old)
    return xml(d)

# Baseline parts remain in place. Actual presentation order inserts part 27 at position 2.
for item in manifest:
    old=item['oldPage']
    if old==0:continue
    slide_path=f'ppt/slides/slide{old}.xml'
    if old==25:
        entries[slide_path]=new['ppt/slides/slide26.xml']
    else:
        d=doc(entries[slide_path])
        updates={str(old).zfill(2):str(item['id']).zfill(2)} if old>=2 else {}
        if old==2:updates['邮件智能体防御架构']='应用控制点映射'
        if old==24:
            updates['邮件智能体的完整防御架构']=item['title']
            updates['在邮件读取、任务决策、实际执行和输出交付处建立控制点。']='以调研报告中的邮件总结任务为例，串联各类防御的作用位置。'
        for t in d.getElementsByTagName('a:t'):
            if value(t) in updates:replace_text(t,updates[value(t)])
        entries[slide_path]=xml(d)
    path=f'ppt/notesSlides/notesSlide{old}.xml'
    entries[path]=set_notes(entries[path],item['notes'])

entries['ppt/slides/slide27.xml']=new['ppt/slides/slide2.xml']
slide_rels=doc(entries['ppt/slides/_rels/slide2.xml.rels'])
for rel in slide_rels.getElementsByTagName('Relationship'):
    if rel.getAttribute('Type').endswith('/notesSlide'):rel.setAttribute('Target','../notesSlides/notesSlide27.xml')
entries['ppt/slides/_rels/slide27.xml.rels']=xml(slide_rels)
entries['ppt/notesSlides/notesSlide27.xml']=set_notes(entries['ppt/notesSlides/notesSlide1.xml'],manifest[1]['notes'])
note_rels=doc(entries['ppt/notesSlides/_rels/notesSlide1.xml.rels'])
for rel in note_rels.getElementsByTagName('Relationship'):
    if rel.getAttribute('Type').endswith('/slide'):rel.setAttribute('Target','../slides/slide27.xml')
entries['ppt/notesSlides/_rels/notesSlide27.xml.rels']=xml(note_rels)

rels=doc(entries['ppt/_rels/presentation.xml.rels'])
rid='rId'+str(max(int(r.getAttribute('Id')[3:]) for r in rels.getElementsByTagName('Relationship') if r.getAttribute('Id').startswith('rId'))+1)
r=rels.createElementNS(PKG,'Relationship');r.setAttribute('Id',rid)
r.setAttribute('Type',R+'/slide');r.setAttribute('Target','slides/slide27.xml');rels.documentElement.appendChild(r)
entries['ppt/_rels/presentation.xml.rels']=xml(rels)
pres=doc(entries['ppt/presentation.xml']);lst=pres.getElementsByTagName('p:sldIdLst')[0]
ids=lst.getElementsByTagName('p:sldId')
sid=pres.createElementNS(P,'p:sldId');sid.setAttribute('id',str(max(int(n.getAttribute('id')) for n in ids)+1));sid.setAttributeNS(R,'r:id',rid)
lst.insertBefore(sid,ids[1]);entries['ppt/presentation.xml']=xml(pres)

ct=doc(entries['[Content_Types].xml'])
for name,kind in [('ppt/slides/slide27.xml','slide'),('ppt/notesSlides/notesSlide27.xml','notesSlide')]:
    n=ct.createElementNS(ct.documentElement.namespaceURI,'Override');n.setAttribute('PartName','/'+name)
    n.setAttribute('ContentType','application/vnd.openxmlformats-officedocument.presentationml.'+kind+'+xml');ct.documentElement.appendChild(n)
entries['[Content_Types].xml']=xml(ct)
app=doc(entries['docProps/app.xml'])
for n in app.getElementsByTagName('Slides'):replace_text(n,'27')
for n in app.getElementsByTagName('TitlesOfParts'):
    v=n.getElementsByTagName('vt:vector')[0]
    items=v.getElementsByTagName('vt:lpstr')
    if len(items)==26:
        item=app.createElementNS(items[0].namespaceURI,'vt:lpstr');item.appendChild(app.createTextNode('汇报目录'))
        v.insertBefore(item,items[1]);v.setAttribute('size','27')
entries['docProps/app.xml']=xml(app)
temp=TARGET.with_name('presentation-revised.tmp.pptx')
with ZipFile(temp,'w',ZIP_DEFLATED) as z:
    for name,data in entries.items():z.writestr(name,data)
temp.replace(TARGET)
print('Preserved reviewed slide objects; inserted agenda; replaced plan; applied user paragraph note format.')
