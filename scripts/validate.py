"""Validate OOXML, editable objects, preserved notes, source coverage and rendered assets."""
from pathlib import Path
from zipfile import ZipFile
import json, posixpath, re, sys
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def text(r): return ''.join(n.text or '' for n in r.findall('.//a:t',NS))
def compact(s): return re.sub(r'\s+','',s)

def run():
    manifest=json.loads((ROOT/'output/page-manifest.json').read_text(encoding='utf-8'))
    errors=[]; stats=[]; actual_notes=[]; actual_text=[]
    pptx=ROOT/'output/presentation.pptx'
    with ZipFile(pptx) as z:
        names=set(z.namelist())
        if z.testzip(): errors.append('ZIP checksum failure')
        relationships={r.get('Id'):posixpath.normpath('ppt/'+r.get('Target')) for r in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
        presentation=E.fromstring(z.read('ppt/presentation.xml'))
        slides=[relationships[s.get('{'+NS['r']+'}id')] for s in presentation.findall('p:sldIdLst/p:sldId',NS)]
        notes=[]
        for name in slides:
            relname=name.replace('/slides/','/slides/_rels/')+'.rels'
            rels=E.fromstring(z.read(relname))
            notes.append(next(posixpath.normpath('ppt/slides/'+r.get('Target')) for r in rels if r.get('Type','').endswith('/notesSlide')))
        if len(slides)!=len(manifest) or len(notes)!=len(manifest): errors.append('Slide/notes count differs from manifest')
        sz=E.fromstring(z.read('ppt/presentation.xml')).find('p:sldSz',NS)
        width,height=int(sz.get('cx')),int(sz.get('cy'))
        if abs(width/height-16/9)>.001: errors.append('Aspect ratio is not 16:9')
        for name in names:
            if not name.endswith(('.xml','.rels')): continue
            try: root=E.fromstring(z.read(name))
            except E.ParseError as exc:
                errors.append(f'Invalid XML {name}: {exc}');continue
            for c in root.findall('.//a:tcPr',NS):
                if c.get('anchor','ctr') not in {'t','ctr','b','just','dist'}: errors.append(f'Invalid table anchor in {name}')
            if name.endswith('.rels'):
                for rel in root:
                    target=rel.get('Target','')
                    if rel.get('TargetMode')=='External':
                        if not target.startswith('https://'): errors.append(f'Unexpected external target: {target}')
                        continue
                    base='' if name=='_rels/.rels' else name.split('/_rels/')[0]
                    resolved=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(base,target))
                    if resolved not in names: errors.append(f'Missing relationship {name} -> {target}')
        for i,name in enumerate(slides):
            root=E.fromstring(z.read(name)); body=text(root);actual_text.append(body)
            if compact(manifest[i]['title']) not in compact(body): errors.append(f'Title absent on page {i+1}')
            for forbidden in ['调研报告 pp','引度教育大学','陈教授','THANKS','教学示意','本团队实验结果','没有填写未测量','不跨论文拼接']:
                if forbidden in body: errors.append(f'Unwanted visible boilerplate on page {i+1}: {forbidden}')
            shapes=len(root.findall('.//p:sp',NS)); pictures=root.findall('.//p:pic',NS); tables=len(root.findall('.//a:tbl',NS))
            if shapes<5 and not tables: errors.append(f'Too few native objects on page {i+1}')
            out=0
            for xf in root.findall('.//a:xfrm',NS):
                off,ext=xf.find('a:off',NS),xf.find('a:ext',NS)
                if off is None or ext is None:continue
                x,y,w,h=[int(e.get(k)) for e,k in [(off,'x'),(off,'y'),(ext,'cx'),(ext,'cy')]]
                if x< -10000 or y< -10000 or x+w>width+10000 or y+h>height+10000:out+=1
            if out:errors.append(f'Page {i+1}: {out} objects outside canvas')
            for pic in pictures:
                ext=pic.find('p:spPr/a:xfrm/a:ext',NS)
                if ext is not None and int(ext.get('cx'))*int(ext.get('cy'))>width*height*.8:errors.append(f'Page {i+1}: full-slide bitmap')
            nr=E.fromstring(z.read(notes[i]))
            nb=next(s for s in nr.findall('.//p:sp',NS) if s.find('p:nvSpPr/p:nvPr/p:ph',NS) is not None and s.find('p:nvSpPr/p:nvPr/p:ph',NS).get('type')=='body')
            nt='\n'.join(text(p) for p in nb.findall('p:txBody/a:p',NS));actual_notes.append(nt)
            if any(t in nt for t in ['讲解台词','参考依据','用户调研报告第']):errors.append(f'Notes do not follow user plain-script format: page {i+1}')
            if not manifest[i].get('references'):errors.append(f'Academic basis absent from source map: page {i+1}')
            if '教学示意' in nt or '不宣称' in nt:errors.append(f'Disclaimer wording in notes: page {i+1}')
            if len(nt)<150:errors.append(f'Notes too short: page {i+1}')
            if compact(manifest[i]['notes']) != compact(nt):errors.append(f'Notes mismatch: page {i+1}')
            stats.append((i+1,shapes,len(pictures),tables))
        master=z.read('ppt/slideMasters/slideMaster1.xml').decode()
        if 'Template academic title rule' not in master or 'Template academic footer' not in master:errors.append('Native template geometry missing')
        if '普蓝-引度PPT' not in z.read('ppt/theme/theme1.xml').decode():errors.append('Template theme not applied')
    spec=(ROOT/'input/设计说明.md').read_text(encoding='utf-8')
    sections=re.findall(r'^## 第\d页：[^\n]*\n([\s\S]*?)(?=^## 第\d页：|^# 第三部分：)',spec,re.M)
    # User requested page-specific spoken scripts and removal of disclaimer copy.
    # Preserve the exact original nine notes in the archive, not as mismatched duplicates.
    all_notes=compact((ROOT/'output/archive/original-nine-speaker-notes.md').read_text(encoding='utf-8'))
    for i,section in enumerate(sections):
        match=re.search(r'### [EF]\. 讲解词\n([\s\S]*?)(?=\n------|$)',section)
        if not match or compact(match[1].replace('**','')) not in all_notes:errors.append(f'Original notes {i+1} not preserved')
    covered={n for d in manifest for n in d['pages']}
    if covered!=set(range(1,16)):errors.append(f'Report coverage incomplete: {sorted(covered)}')
    if manifest[1]['title']!='汇报目录':errors.append('Agenda is not immediately after cover')
    source_map=(ROOT/'output/source-map.md').read_text(encoding='utf-8')
    for d in manifest:
        if d['references'] not in source_map:errors.append(f'Source map mismatch: page {d["id"]}')
    for n in range(1,len(manifest)+1):
        if not (ROOT/f'output/previews/slide{n:02}.png').exists():errors.append(f'Preview missing: {n}')
    print(f'{len(manifest)} pages; {sum(v[1] for v in stats)} native shapes; {sum(v[2] for v in stats)} pictures; {sum(v[3] for v in stats)} native tables')
    print(f'{len(manifest)} plain spoken scripts checked; agenda after cover; sources stored separately; all 15 report pages mapped.')
    for v in stats:print(f'{v[0]:02}: shapes={v[1]}, pictures={v[2]}, tables={v[3]}')
    report=['# 结构与内容验证','',f'结果：{"FAIL" if errors else "PASS"}', '',f'页数：{len(manifest)}。原生形状：{sum(v[1] for v in stats)}。图片：{sum(v[2] for v in stats)}。原生表格：{sum(v[3] for v in stats)}。','',
      f'检查：ZIP/XML、实际演示顺序、关系目标、16:9、逐页标题与{len(manifest)}页对应纯讲稿备注、封面后目录、独立来源索引、原九页讲解词归档、15页调研覆盖、模板主题与原生线条、无整页位图、边界、预览存在。','',
      '参考文献中的HTTPS链接属于有意保留的外部关系。结构验证不替代实际视觉审查；逐页设计与渲染审查记录见design-review-final.md。','',
      '| 页 | 原生形状 | 图片 | 原生表格 |','|---:|---:|---:|---:|']
    report += [f'| {a} | {b} | {c} | {d} |' for a,b,c,d in stats]
    if errors:report += ['','## 待解决']+['- '+e for e in errors]
    (ROOT/'output/validation-report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    if errors:print('\n'.join(errors));return 1
    print('PASS');return 0
if __name__=='__main__':sys.exit(run())
