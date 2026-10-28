import fs from 'node:fs';

export interface SlideContent { title: string; intro: string; source: string; notes: string; section: string }

const spec = fs.readFileSync(new URL('../input/设计说明.md', import.meta.url), 'utf8');
const sections = [...spec.matchAll(/^## 第(\d)页：[^\r\n]*\r?\n([\s\S]*?)(?=^## 第\d页：|^# 第三部分：)/gm)];
if (sections.length !== 9) throw new Error(`Expected nine slide sections; found ${sections.length}`);

const titles = [
  '智能体应用的提示注入攻击检测与防御',
  '从普通问答到智能体，系统发生了什么变化？',
  '一封普通邮件，怎样影响智能体的决策？',
  '攻击指令可以沿着两条不同路径进入模型',
  '为什么智能体中的提示注入更加危险？',
  '第一类防御：让模型区分指令权限与输入数据',
  '第二类防御：标记来源，并检测可疑指令',
  '第三类防御：把实际执行权限放在模型之外',
  '单一防御方法不够，智能体需要多层安全控制',
];
const intros = [
  '从不可信数据到模型决策与工具执行的安全风险',
  '模型不仅需要回答用户，还可能读取外部信息并调用工具。',
  '攻击者试图让模型把外部邮件中的内容当成新的任务指令。',
  '两类攻击的主要差别，是攻击者从哪里放入恶意指令。',
  '攻击可能从错误的文本回答，进一步影响真实工具的执行。',
  '既要知道不同指令的优先级，也要知道哪些内容本身不是指令。',
  '在应用层增加安全措施，降低外部内容诱导模型的风险。',
  '不能只要求模型不犯错，还要限制错误决策造成的实际后果。',
  '不同防御技术作用于不同位置，不能相互替代。',
];
const sources = [
  '调研报告 pp.1–2', '调研报告 pp.1–2', '调研报告 pp.2,4 · 教学示意',
  '调研报告 pp.3–4 · Greshake et al., 2023',
  '调研报告 p.5 · AgentDojo, 2024',
  '调研报告 pp.6–9 · Wallace et al.; Chen et al.',
  '调研报告 pp.9–11 · Hines et al.; Wen et al.',
  '调研报告 pp.12–13 · Debenedetti et al., 2025',
  '调研报告 pp.13–14',
];
const bibliographies = [
  '', '', '',
  "Greshake et al. (2023), Not What You've Signed Up For, arXiv:2302.12173.",
  'Debenedetti et al. (2024), AgentDojo, arXiv:2406.13352.',
  'Wallace et al. (2024/2025), The Instruction Hierarchy, arXiv:2404.13208. Chen et al. (2025), StruQ, USENIX Security 2025.',
  'Hines et al. (2024), Spotlighting, arXiv:2403.14720. Wen et al. (2025), Instruction Detection, arXiv:2505.06311.',
  'Debenedetti et al. (2025), Defeating Prompt Injections by Design, arXiv:2503.18813.',
  '',
];

export const CONTENT: SlideContent[] = sections.map((match, index) => {
  const body = match[2];
  const notesMatch = body.match(/### [EF]\. 讲解词\r?\n([\s\S]*?)(?=\r?\n------|$)/);
  if (!notesMatch) throw new Error(`Speaker notes missing on slide ${index + 1}`);
  const notes = notesMatch[1].replace(/\*\*/g, '').trim();
  return { title: titles[index], intro: intros[index], source: sources[index],
    notes: `${notes}\n\n${bibliographies[index]}`.trim(),
    section: index < 5 ? '01  攻击与风险' : index < 8 ? '02  防御机制' : '03  体系整合' };
});

