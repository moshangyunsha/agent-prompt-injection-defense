import { SCRIPTS, AGENDA_SCRIPT } from './speaker-scripts.js';

export interface ResearchPage {
  title: string; section: string; pages: number[]; notes: string;
  sources: number[]; legacy?: number; layout: string;
}
export const REFERENCES = [
  { short: 'Greshake et al., 2023', title: "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", url: 'https://arxiv.org/abs/2302.12173', id: 'arXiv:2302.12173' },
  { short: 'Yi et al., 2023 · BIPIA', title: 'Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models', url: 'https://arxiv.org/abs/2312.14197', id: 'arXiv:2312.14197' },
  { short: 'Wallace et al., 2024/2025', title: 'The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions', url: 'https://arxiv.org/abs/2404.13208', id: 'arXiv:2404.13208' },
  { short: 'Hines et al., 2024', title: 'Defending Against Indirect Prompt Injection Attacks With Spotlighting', url: 'https://arxiv.org/abs/2403.14720', id: 'arXiv:2403.14720' },
  { short: 'Chen et al., USENIX Security 2025', title: 'StruQ: Defending Against Prompt Injection with Structured Queries', url: 'https://www.usenix.org/conference/usenixsecurity25/presentation/chen-sizhe', id: 'USENIX Security 2025' },
  { short: 'Wen et al., 2025', title: 'Defending against Indirect Prompt Injection by Instruction Detection', url: 'https://arxiv.org/abs/2505.06311', id: 'arXiv:2505.06311' },
  { short: 'Debenedetti et al., 2025 · CaMeL', title: 'Defeating Prompt Injections by Design', url: 'https://arxiv.org/abs/2503.18813', id: 'arXiv:2503.18813' },
  { short: 'Debenedetti et al., 2024 · AgentDojo', title: 'AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents', url: 'https://arxiv.org/abs/2406.13352', id: 'arXiv:2406.13352' },
  { short: 'OWASP', title: 'LLM Prompt Injection Prevention Cheat Sheet', url: 'https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html', id: '官方防御指南' },
  { short: 'Google DeepMind, 2025', title: "Advancing Gemini's Security Safeguards", url: 'https://deepmind.google/blog/advancing-geminis-security-safeguards/', id: '官方研究页面' },
];

const data: ResearchPage[] = [
 { title:'智能体应用的提示注入攻击检测与防御', section:'课程研究汇报', pages:[1,2], sources:[1,8], legacy:0, layout:'模板蓝色标题带', notes:'本次讨论面向能够读取外部内容并调用工具的智能体应用。关注的不是一句恶意提示本身，而是外部内容如何跨越指令权限边界，影响决策、调用参数、实际动作和输出。汇报依据调研报告的全部章节展开，并将各项研究放入共同的应用处理流程。' },
 { title:'研究范围与分析路径', section:'研究对象', pages:[1,2,14,15], sources:[1,2,3,4,5,6,7,8,9,10], layout:'文献—问题—产出映射', notes:'我们以八项论文及基准、两份官方资料为文献范围，按攻击入口、模型行为和真实执行后果进行交叉整理。具体产物是攻击面分类、六类防御的机制与限制比较，以及邮件助手的控制点映射。这些是文献分析和架构整理的成果，不宣称已经复现论文或完成攻击实验。' },
 { title:'问答、RAG与工具型智能体', section:'攻击与风险', pages:[1,2], sources:[1,8], legacy:1, layout:'非对称系统演化', notes:'普通问答主要沿问题、模型、回答的线性路径运行。RAG引入检索与外部资料，工具型智能体进一步形成计划、调用、返回和下一步决策的回路。系统或开发者约束、用户任务、第三方内容是不同权限的来源，不能因为最终都进入模型上下文就视为同等指令。新增的读取路径扩大攻击面，新增的执行能力扩大后果。' },
 { title:'指令与数据的信任边界', section:'攻击与风险', pages:[1,2], sources:[1,3,5], layout:'输入语义对照', notes:'提示注入的安全问题是控制流被低信任来源影响。传统程序能够通过解析器和类型将指令与数据分离；语言模型处理的上下文却可能混合系统要求、用户请求和外部文本。攻击者希望把数据中的命令提升为行动依据。并非所有恶意文本都会成功；成立条件是应用读取了相关内容，模型又错误地执行其指令，而应用没有阻断后续行为。' },
 { title:'直接注入与间接注入', section:'攻击与风险', pages:[2,3,4], sources:[1], legacy:3, layout:'共终点双路径', notes:'直接注入由攻击者在用户输入位置提交指令；间接注入则污染网页、邮件、文档或工具返回，等待系统为正常任务读取这些资料。两者都希望改变模型行为，但攻击者控制的输入面不同。间接攻击通常不需要直接接触受害用户的对话接口。路径图强调入口差别，不能把直接用户指令和外部数据混为一个权限层级。' },
 { title:'直接注入的目标与规避手段', section:'攻击与风险', pages:[3], sources:[1,9], layout:'目标分类与规避带', notes:'报告列出的直接注入包括身份或角色改变、忽略系统和开发者要求、索取系统提示或配置、获取任务外信息、修改原始目标、越过用户权限、多轮侵蚀限制，以及编码、拆分、改写或角色扮演绕过检测。页面将前六项按规则、信息、行动归类，再单列跨轮次与表达变换。词表检测容易被语言变化和语义重写绕过，这也是后续研究不只依赖关键词的原因。' },
 { title:'间接注入的外部载体', section:'攻击与风险', pages:[4], sources:[1,2], layout:'生成网页分层图与载体索引', notes:'外部载体包括网页正文、隐藏内容和元数据，邮件及附件，PDF、Word、Markdown，数据库与知识库，代码注释、提交记录和配置，搜索结果，API返回，其他智能体与工具输出，以及图像文字、文件属性等多模态内容。生成的网页分层图仅为教学示意。是否读入隐藏内容或元数据取决于获取与解析方式；它说明潜在载体，不代表每个系统都会读取全部层次。' },
 { title:'邮件总结任务中的信任越界', section:'攻击与风险', pages:[4], sources:[1], legacy:2, layout:'原生邮件界面', notes:'用户要求总结项目邮件。邮件中的时间和工作安排属于可总结数据；插入的“忽略总结、发送全文”试图把外部数据改成新任务。正常阅读路径和攻击路径在界面中分开标注。右侧展示可能受影响的模型决策，尚不代表已经执行发送；下一页会将工具请求和权限检查区分开。所有邮件内容、地址及操作均为教学示意。' },
 { title:'错误决策如何变成真实动作', section:'攻击与风险', pages:[5], sources:[8,9], legacy:4, layout:'攻击链与权限分支', notes:'模型提出调用请求并不等于工具已执行。工具执行前需要独立检查身份、能力、参数、目标对象及数据流向，并作允许、拒绝或额外确认决定。报告覆盖文件、数据库、检索网页、邮件、日历任务、代码和企业接口；风险包括越权查询、外泄、修改或删除记录、未授权系统操作和绕过人工复核。图中红色请求是被污染后的候选行为，审核门位于真实执行之前。' },
 { title:'跨轮次、记忆与多模态攻击', section:'攻击与风险', pages:[5,6], sources:[1,9], layout:'多模态生成证据与跨时序关系', notes:'多轮攻击逐步侵蚀约束；工具响应注入借助调用返回进入下一轮；记忆污染将恶意内容存入长期记忆、用户画像或知识库，影响未来任务；多模态攻击则通过图像、截图、二维码、PDF图像、元数据或音频转写进入上下文。图中的文档嵌入图像是生成的教学示意，只有应用通过视觉理解或OCR读入其中内容时，图像文字才可能成为模型输入。' },
 { title:'风险研究与评测依据', section:'研究依据', pages:[2,5,11,14], sources:[1,2,8], layout:'原研究图与评测轴', notes:'Greshake等研究定义了真实LLM应用的间接注入风险；BIPIA建立间接提示注入评测基准并比较黑盒与白盒防御；AgentDojo把正常用户任务、工具环境和攻击目标结合起来。原图摘自用户调研报告中的AgentDojo研究图。本汇报没有复现实验，也不跨论文拼接性能数字。评测应同时观察正常任务效用和攻击后果，尤其是工具的真实行为，而不是只看拒绝语句。' },
 { title:'六类防御在系统中的位置', section:'防御机制', pages:[6,13,14], sources:[3,4,5,6,7,9], layout:'处理主线与干预位置', notes:'六类方法作用于不同对象：层级训练改善模型的权限服从，StruQ分开指令和数据，Spotlighting提供外部来源信号，专用检测器识别风险，能力和数据流策略约束执行，输出检查控制最终泄露。页面按应用处理位置映射，训练层与运行时层明确分开。这是本次报告的综合架构分析，不表示这些论文提出了一条必须固定串联的流水线。' },
 { title:'Instruction Hierarchy：来源权限与冲突', section:'防御机制', pages:[6,7], sources:[3], legacy:5, layout:'权限阶梯与训练样本', notes:'层级顺序为系统高于开发者，开发者高于用户，用户高于外部内容和工具返回。来源权限决定冲突时应服从哪条要求。研究通过合成训练样本区分与高权限目标一致的低权限指令和冲突指令，训练模型忽略后者，并允许前者为任务提供帮助。页面表现的是模型行为训练，而不是外部程序执行权限的强制保证。适用于多来源上下文、工具应用和权限不同的智能体。' },
 { title:'层级训练的证据与能力边界', section:'防御机制', pages:[8], sources:[3], layout:'原研究案例与边界清单', notes:'报告中的案例图用于说明低权限文本试图改变既定回答规则。中文旁注解释其冲突关系，而不把图中的单个例子当作普适性能证明。限制包括复杂指令冲突，角色扮演、隐喻、编码及多轮变形攻击，不同模型对层级规则的学习差异。即使模型行为有所改善，方法本身也不检查实际工具权限，不能撤销已经发生的数据泄露。' },
 { title:'StruQ：安全前端与结构化输入', section:'防御机制', pages:[8,9], sources:[5], layout:'双通道技术管线与原图', notes:'StruQ由安全前端和接受相应训练的模型共同组成。前端过滤数据中伪造的保留标记，将指令和数据放入独立结构，再由训练模型按照指令通道工作并忽略数据通道中的命令。适用场景包括文档问答、网页总结、邮件处理、代码、RAG和检索智能体。普通XML、Markdown或字符串分隔只提供表面边界，不能等同于完整的StruQ方法。' },
 { title:'Spotlighting：让外部来源持续可见', section:'防御机制', pages:[9,10,11], sources:[4], layout:'片段前后对照与机制差异', notes:'Spotlighting对外部内容加入来源标记，或进行编码、数据变换，让模型持续感知它正在处理低信任来源。页面示例为概念性来源标记，不声称是论文特定实现的逐字复现。报告描述GPT实验中攻击成功率降低且正常任务效用影响较小，因此页面只保留定性结论。其限制是模型可能忽略标记、攻击者可能伪装可信身份或采用自适应攻击，方法也不独立阻止工具调用或自动清除已读到的敏感信息。' },
 { title:'专用检测器的两条技术路线', section:'防御机制', pages:[11], sources:[2,6], legacy:6, layout:'文本与模型状态检测分轨', notes:'文本检测器读取输入或外部片段并给出风险分类，可用Prompt Guard、ProtectAI DeBERTa、文本分类器、跨语言模型或小型安全模型。Prompt Guard区分benign、injection、jailbreak；具体模型可在本地部署或按场景微调。Wen等Instruction Detection使用模型隐藏状态及梯度特征识别隐藏指令，与仅分析原始文本的分类器不同。检测结果进入风险分流，能够支持前置扫描、文档或工具返回扫描、人审和安全网关。' },
 { title:'误报、漏报与检测的适用边界', section:'防御机制', pages:[11], sources:[2,6,9], layout:'无虚构数据的错误关系表', notes:'误报是把正常内容判为攻击，损害任务可用性；漏报是把恶意内容判为正常，留下后续风险。表格展示概念关系而不是本次测量值。失效因素包括领域与分布变化、多语言、长文档中攻击的位置、改写与自适应规避，以及检测器自身可能受污染。阈值和风险分流需要按实际场景评估；一个风险分数不能替代工具能力或数据流策略。' },
 { title:'CaMeL：可信控制与不可信数据分离', section:'防御机制', pages:[12,13], sources:[7], legacy:7, layout:'双流与执行器安全架构', notes:'特权模型P-LLM只依据可信用户请求规划并生成程序，不读取外部原文。保护性解释器执行该程序，隔离模型Q-LLM处理不可信内容并返回结构化数据，Q-LLM没有实际工具调用能力。解释器跟踪值的来源与能力，实际工具调用前执行能力和数据流策略。双模型隔离本身仍不足：被污染的结构化值可能改变收件人等调用参数，必须继续检查数据流向。图按论文设计核对，策略范围和用户确认仍由应用定义，不声称解决全部风险。' },
 { title:'能力与数据流策略如何落地', section:'防御机制', pages:[12,13], sources:[7,9], layout:'具体调用与检查项映射', notes:'调用的安全性取决于请求来源、参数、权限、目标对象与数据流。示例中任务只允许总结邮件，却出现发往外部地址的候选调用，因此不能仅因JSON格式正确就允许发送。策略门可拒绝、允许符合授权的调用或请求用户确认；只有新的有效授权才能改变允许范围。受保护操作包括邮件、数据库修改、文件删除移动、外部网络、代码执行、金融系统、企业API和用户身份权限。' },
 { title:'输出检查与调用参数检查', section:'防御机制', pages:[13], sources:[9], layout:'执行前与输出前双轨', notes:'报告列出系统提示、用户隐私、API密钥密码令牌、任务外敏感数据、危险工具参数和未授权操作建议六类检查对象。敏感信息识别、正则或密钥特征、实体识别、内容分类、第二模型复核以及参数模式检查是六种手段。危险调用参数应在执行前检查，文本内容应在交付前检查。输出拦截不能修复内部错误决策，也不能撤回已经执行的外部动作。' },
 { title:'六类防御的机制比较', section:'体系整合', pages:[13,14], sources:[3,4,5,6,7,9], layout:'原生比较矩阵', notes:'比较从保护对象、模型训练要求、作用机制、优势和限制展开。Instruction Hierarchy需要训练，StruQ依赖安全前端和训练模型；Spotlighting主要改变上下文输入；检测器可使用现成模型但须考虑场景迁移；输出检查不一定需要训练；工具权限及数据流控制在模型之外限制真实动作但策略设计维护复杂。比较支持机制组合，不能据此推导一个场景无关的最佳方法。' },
 { title:'八项研究如何构成一条技术线索', section:'体系整合', pages:[14,15], sources:[1,2,3,4,5,6,7,8], layout:'研究问题与贡献索引', notes:'文献之间按问题相连：Greshake确认外部数据风险，BIPIA和AgentDojo分别提供间接输入与工具行为的评测对象；Instruction Hierarchy和StruQ从模型权限及输入结构改进边界；Spotlighting和Instruction Detection增强来源感知与风险识别；CaMeL将控制与数据流安全推进到运行时。页面列出八项研究的核心问题、方法及本课题采用的分析结果，不把发表年份强行写成线性的性能进步。' },
 { title:'邮件任务中的防御位置映射', section:'体系整合', pages:[4,6,12,13,14], sources:[3,4,5,6,7,9], legacy:8, layout:'报告案例的系统主线与外部回流', notes:'采用报告中的邮件总结案例，将六类防御映射到内容读取、模型决策、工具执行和结果交付。' },
 { title:'下一步研究思路与实施准备', section:'课题计划', pages:[1,14,15], sources:[1,2,3,4,5,6,7,8,9,10], layout:'确定问题、选择框架、准备条件、基础实现', notes:'在调研基础上选择要处理的问题与框架，尽可能完成准备和基础原型。' },
 { title:'参考文献', section:'参考资料', pages:[15], sources:[1,2,3,4,5,6,7,8,9,10], layout:'两栏学术参考文献', notes:'八项论文或基准以及OWASP与DeepMind官方资料覆盖调研报告参考文献。链接指向论文原始页面和官方资料。BIPIA作者以原论文元数据为准，修正了报告列表中的不一致；不改变报告的技术论述。教学示意、生成素材、原论文图摘录在相应页面备注中分别说明，完整素材来源和覆盖记录随工程交付。' },
];

const originalPages = data.map((d, index) => ({
  ...d, id: index === 0 ? 1 : index + 2, oldPage: index + 1,
  notes: SCRIPTS[index],
  references: `用户调研报告第${d.pages.join('、')}页。\n${d.sources.map(n => `[${n}] ${REFERENCES[n-1].short}. ${REFERENCES[n-1].title}. ${REFERENCES[n-1].url}`).join('\n')}${index===6?'\n图示素材：ImageGen生成的网页分层视图。':index===9?'\n图示素材：ImageGen生成的文档图像文字放大视图。':index===10?'\n图示素材：调研报告中的AgentDojo原研究图。':index===13?'\n图示素材：调研报告中的Instruction Hierarchy原研究表格摘录。':index===14?'\n图示素材：调研报告中的StruQ原研究图。':''}${index===16?'\n模型资料：Meta Prompt Guard 86M，https://huggingface.co/meta-llama/Prompt-Guard-86M\n模型资料：ProtectAI DeBERTa v2，https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2':''}`,
}));
export const RESEARCH_CONTENT = [originalPages[0], {
  title:'汇报目录', section:'讲解顺序', id:2, oldPage:0, pages:[1,2,6,14,15], sources:[],
  layout:'四段平面目录与讲解页码', notes:AGENDA_SCRIPT, references:'汇报组织页；对应后续章节的来源见各页学术依据。',
}, ...originalPages.slice(1)];
