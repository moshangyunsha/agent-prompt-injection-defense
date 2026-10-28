import { makeSlide } from './common.js';
import { addText } from '../components/text.js';
import { addArrow, addLine } from '../components/connector.js';
import { module, rule, marker } from '../components/editorial.js';
import { C } from '../theme.js';

export function slide06(pptx: any) {
  const s = makeSlide(pptx, 6);
  addText(s, 'Instruction Hierarchy', 0.78, 1.85, 5.48, 0.38, 20, C.title, { bold: true });
  addText(s, '指令来源决定冲突时的优先级', 0.78, 2.26, 5.47, 0.28, 14, C.muted);
  s.addShape('line', { x: 6.57, y: 1.85, w: 0, h: 4.53, line: { color: C.border, width: 1 } });
  addText(s, 'StruQ  /  Structured Queries', 6.89, 1.85, 5.57, 0.38, 20, C.title, { bold: true });
  addText(s, '安全前端把指令与外部数据分开', 6.89, 2.26, 5.47, 0.28, 14, C.muted);
  const levels = [
    ['系统指令', C.trusted], ['开发者指令', C.trusted], ['用户任务', C.body], ['工具输出 / 外部数据', C.external]
  ] as const;
  levels.forEach(([label, color], i) => {
    const y = 2.82 + i * 0.72;
    marker(s, String(i + 1).padStart(2, '0'), 0.88, y + 0.07, i === 3 ? 'external' : 'trusted');
    addText(s, label, 1.43, y, 4.40, 0.37, 18, color, { bold: i < 2 });
    rule(s, 0.82, y + 0.49, 5.18, C.border);
  });
  addArrow(s, 5.40, 5.36, 5.40, 3.74, 'risk', true);
  s.addShape('line', { x: 5.21, y: 3.71, w: 0.38, h: 0, line: { color: C.risk, width: 2.3 } });
  addText(s, '低优先级内容不能覆盖更高优先级指令', 0.88, 5.86, 5.41, 0.54, 14, C.risk);
  module(s, '安全前端', 8.33, 2.83, 2.85, 0.62, 'review', 17);
  addText(s, '处理保留标记与输入边界', 7.02, 3.56, 2.36, 0.47, 12, C.review, { align: 'right' });
  addLine(s, 9.76, 3.46, 9.76, 3.93, 'control');
  addLine(s, 8.32, 3.93, 11.18, 3.93, 'control');
  addArrow(s, 8.32, 3.93, 8.32, 4.23, 'control');
  addArrow(s, 11.18, 3.93, 11.18, 4.23, 'data');
  module(s, 'Instruction\n应用任务', 7.18, 4.27, 2.30, 0.75, 'trusted', 15);
  module(s, 'Data\n外部内容', 10.01, 4.27, 2.30, 0.75, 'external', 15);
  addArrow(s, 8.32, 5.04, 9.12, 5.46, 'control');
  addArrow(s, 11.16, 5.04, 10.34, 5.46, 'data');
  module(s, '经过相应训练的模型', 8.20, 5.50, 3.12, 0.63, 'trusted', 15);
  addText(s, '文字分隔符本身不构成绝对保证；两种机制均依赖模型能力。', 0.78, 6.60, 11.87, 0.30, 15, C.trusted, { bold: true });
  return s;
}
