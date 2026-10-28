import { makeSlide } from './common.js';
import { addText } from '../components/text.js';
import { addArrow } from '../components/connector.js';
import { rule } from '../components/editorial.js';
import { C } from '../theme.js';

export function slide09(pptx: any) {
  const s = makeSlide(pptx, 9);
  addText(s, '用户任务 + 外部内容', 0.78, 1.86, 4.18, 0.36, 17, C.title, { bold: true });
  addText(s, '处理位置', 3.50, 2.25, 2.12, 0.28, 13, C.muted, { bold: true });
  addText(s, '对应机制', 5.73, 2.25, 4.29, 0.28, 13, C.muted, { bold: true });
  addText(s, '主要作用', 10.55, 2.25, 2.0, 0.28, 13, C.muted, { bold: true });
  rule(s, 0.78, 2.64, 11.80, C.border);
  s.addShape('line', { x: 1.21, y: 2.91, w: 0, h: 3.29, line: { color: C.trusted, width: 1.6 } });
  const rows = [
    ['01', '输入处理', 'Spotlighting · 注入检测 · 输入结构处理', '识别来源，分流可疑内容', C.external],
    ['02', '模型处理', 'Instruction Hierarchy · StruQ', '减少对低可信指令的服从', C.trusted],
    ['03', '工具执行', 'CaMeL · 能力权限 · 参数与数据流检查', '阻止不符合策略的实际操作', C.review],
    ['04', '输出检查', '敏感信息识别 · 输出结果审查', '减少不安全结果输出', C.external],
  ] as const;
  rows.forEach(([num, stage, method, effect, accent], i) => {
    const y = 2.83 + i * 0.87;
    s.addShape('ellipse', { x: 1.07, y: y + 0.20, w: 0.28, h: 0.28,
      fill: { color: accent }, line: { color: accent, width: 1 } });
    addText(s, num, 1.65, y + 0.17, 0.53, 0.30, 13, accent, { bold: true });
    addText(s, stage, 2.18, y + 0.12, 2.85, 0.39, 19, C.title, { bold: true });
    addText(s, method, 5.73, y + 0.08, 4.57, 0.50, 15, C.body);
    addText(s, effect, 10.55, y + 0.08, 2.05, 0.50, 14, i === 2 ? C.review : C.muted);
    rule(s, 1.67, y + 0.72, 10.90, C.border, 0.75);
  });
  addArrow(s, 1.21, 6.25, 1.21, 6.47, 'control');
  addText(s, '最终结果', 1.65, 6.37, 2.1, 0.37, 17, C.title, { bold: true });
  addText(s, '各层仍可能有残余风险', 5.73, 6.41, 3.45, 0.30, 14, C.risk);
  addText(s, '模型参与决策；策略独立执行', 8.74, 6.39, 3.86, 0.34, 14, C.trusted, { bold: true, align: 'right' });
  return s;
}
