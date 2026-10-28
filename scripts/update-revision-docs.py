from pathlib import Path
import re, json

ROOT=Path(__file__).resolve().parents[1]
def move_num(m):
    n=int(m.group(0)); return str(n if n==1 else n+1).zfill(2)
def shifted(s): return re.sub(r'\d{2}',move_num,s)

p=ROOT/'output/design-review-final.md'; s=p.read_text(encoding='utf-8')
(ROOT/'output/archive/design-review-26pages.md').write_text(s,encoding='utf-8')
start=s.index('## 逐页实质改进'); end=s.index('## 报告内容覆盖核对')
part=s[start:end]; out=[]
for line in part.splitlines():
    m=re.match(r'\| (\d{2}) \|',line)
    if not m:out.append(line);continue
    n=int(m.group(1));line=line.replace(f'| {n:02} |',f'| {(n if n==1 else n+1):02} |',1)
    if n==1:
        line='| 01 | 研究题目与对象 | 保留用户手改后的封面、汇报人姓名和蓝色标题带；补入引出目录的讲稿衔接。 |'
    elif n==2:
        line+=''
        line=line.replace('邮件架构三项产物','应用控制点映射三项产物')
    elif n==6:
        line='| 07 | 直接注入目标和规避方式 | 保留用户调整的规则、信息、行动三组目标，以及下方规避方式到各目标的红色连接关系。讲稿从直接入口承接到攻击意图，再引出外部载体。 |'
    elif n==24:
        line='| 25 | 邮件任务中的防御位置映射 | 保留现有主线、输出路径和工具回流，标题与导语明确邮件任务来自报告。讲稿说明完整映射是基于六类机制的综合分析，并引出下一阶段的问题与框架选择。 |'
    elif n==25:
        line='| 26 | 下一步研究思路与实施准备 | 重新组织为确定问题、选择框架、准备条件、基础实现四阶段。每阶段列出具体工作和产物，先形成可实施课题方案，再推进原型及后续评测。 |'
    out.append(line)
    if n==1:out.append('| 02 | 汇报目录 | 封面后新增四段平面目录，给出背景、攻击与评测、防御与比较、案例与计划的讲解顺序和实际页码范围。 |')
s=s[:start]+'\n'.join(out)+'\n\n'+s[end:]
start=s.index('## 报告内容覆盖核对');end=s.index('## 实际渲染与精修记录')
part=s[start:end];out=[]
for line in part.splitlines():
    if line.startswith('|'):
        cells=line.split('|')
        if len(cells)>3 and re.search(r'\d',cells[2]):cells[2]=shifted(cells[2]);line='|'.join(cells)
    out.append(line)
s=s[:start]+'\n'.join(out)+'\n\n'+s[end:]
start=s.index('## 讲解台词与文案清理');end=s.index('## 图片与可编辑性')
s=s[:start]+'''## 讲解台词与文案清理

27页采用用户修改的前两页格式：备注直接写讲稿，按段换行，不添加“讲解台词”标题、参考依据或来源页码段。学术依据单独保留在source-map.md，末页继续列出全部文献。

保留用户讲稿内容，并补入页间及页内衔接。衔接说明技术问题之间的联系：外部入口如何聚焦到邮件，候选请求如何追踪到执行授权，检测漏报如何引出运行时策略，研究比较如何回到应用位置，以及案例怎样支持后续问题与框架选择。具体台词见speaker-script.md。

影响技术结论的前提和限制继续保留，例如StruQ需要相应训练与安全前端、检测存在误报漏报、输出拦截不能撤回动作。原九页讲稿和用户修改的26页版本均已归档。

'''+s[end:]
start=s.index('## 图片与可编辑性');end=s.index('## 结构检查结果')
part=s[start:end];part=re.sub(r'第(\d{2})页',lambda m:'第'+str(int(m[1])+1).zfill(2)+'页',part)
s=s[:start]+part+s[end:]
s=s.replace('共26页。26页均有对应讲解台词，学术依据置于备注的独立部分。','共27页。备注采用用户修改的纯讲稿格式；学术依据单独保留在source-map.md。')
s=s.replace('在现有PptxGenJS工程内扩展为26页。','先在现有PptxGenJS工程内扩展为26页，本轮在用户手改版上增加目录并调整案例表述和课题计划，形成27页。')
s=s.replace('26页最新版本已经重新构建、实际渲染并验证。','本轮27页已重新构建、实际渲染并验证，目录、研究范围、案例映射和计划页已单页放大检查。23张其余页面主体与用户手改版本逐像素相同。')
s=s.replace('最终PPT含683个原生形状/文本对象','最终PPT含704个原生形状/文本对象')
s=s.replace('结构检查确认26页标题、26份讲解台词、参考依据、','结构检查确认27页标题、27份纯讲稿、独立来源索引、')
s=s.replace('模型资料已按报告对应版本核对，相关页备注附','模型资料已按报告对应版本核对，来源索引附')
s=s.replace('论文事实与模型卡资料分别在相关页备注中可追溯。','论文事实与模型卡资料在来源索引中可追溯。')
s=s.replace('用两行完整题目、研究对象和资料范围建立课程研究汇报的身份','用完整题目和汇报人建立课程研究汇报的身份')
s=s.replace('最终母版直接复用模板的原生标题线、底部蓝线及主题。','最终母版直接复用模板的原生标题线、底部蓝线及主题。邮件情景来自报告第4页，完整防御位置图为调研基础上的综合映射；具体课题框架将在下一阶段确定。')
p.write_text(s,encoding='utf-8')

p=ROOT/'output/design-plan-expanded.md';s=p.read_text(encoding='utf-8')
(ROOT/'output/archive/design-plan-26pages.md').write_text(s,encoding='utf-8')
lines=[]
for line in s.splitlines():
    m=re.match(r'\| (\d+) \|',line)
    if m:
        n=int(m[1]);line=line.replace(f'| {n} |',f'| {n if n==1 else n+1} |',1)
        if n==1:line='| 1 | 题目及汇报人 | 建立研究主题 | 保留用户手改封面及原生文字 | 引出目录和讲解顺序 |'
        if n==24:line='| 25 | 邮件任务中的防御位置映射 | 以报告案例串联六类机制 | 保留原生系统主线与工具回流；说明案例与综合分析的关系 | 转入课题开展思路 |'
        if n==25:line='| 26 | 下一步研究思路与实施准备 | 把调研转化为可实施课题 | 确定问题、选择框架、准备条件、基础实现四阶段及产物 | 参考文献 |'
        lines.append(line)
        if n==1:lines.append('| 2 | 汇报目录 | 说明四部分讲解顺序 | 平面目录、简短内容和实际页码范围 | 研究范围与背景 |')
    else:lines.append(line)
s='\n'.join(lines)+'\n'
s=s.replace('扩展为26页。按用户最新要求，26页分别编写可直接讲述的台词','先扩展为26页，本轮在用户手改版本上增加目录形成27页。按用户最新要求，27页采用直接讲稿、按段换行的备注格式，并补齐页间及页内衔接')
s=s.replace('作者、论文名作为内容的一部分出现，完整来源集中于末页和备注。','作者、论文名作为内容的一部分出现，完整来源集中于末页和source-map.md。')
s=s.replace('第7页生成','第8页生成').replace('第10页生成','第11页生成')
p.write_text(s,encoding='utf-8')

p=ROOT/'assets/generated/prompts.json';data=json.loads(p.read_text(encoding='utf-8'))
def change_page(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in ['page','slide'] and isinstance(v,int) and v in [7,10]:obj[k]=v+1
            else:change_page(v)
    elif isinstance(obj,list):
        for v in obj:change_page(v)
change_page(data);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated 27-page design plan, review, and asset page references; archived previous records.')
