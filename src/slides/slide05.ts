import { makeSlide } from './common.js';
import { addText } from '../components/text.js';
import { addArrow, addRoute } from '../components/connector.js';
import { module, rule, bar } from '../components/editorial.js';
import { C } from '../theme.js';

export function slide05(pptx: any) {
  const s = makeSlide(pptx, 5);
  addText(s, '从被污染的内容到工具调用', 0.78, 1.84, 5.48, 0.41, 21, C.title, { bold: true });
  addText(s, '模型提出调用 ≠ 系统已经执行', 7.54, 1.91, 5.0, 0.30, 15, C.muted, { align: 'right' });
  rule(s, 0.78, 2.38, 11.8);
  addText(s, '外部邮件', 0.82, 2.91, 2.12, 0.38, 18, C.external, { bold: true });
  addArrow(s, 2.54, 3.10, 3.10, 3.10, 'data');
  addText(s, '智能体读取', 3.22, 2.91, 2.02, 0.38, 18, C.title);
  addArrow(s, 4.92, 3.10, 5.47, 3.10, 'risk', true);
  addText(s, '模型可能误判', 5.58, 2.91, 2.45, 0.38, 18, C.risk, { bold: true });
  addArrow(s, 7.96, 3.10, 8.56, 3.10, 'risk', true);
  module(s, '危险工具调用请求', 8.62, 2.72, 3.38, 0.76, 'risk', 17);
  // The independent policy gate is the primary visual object.
  addRoute(s, [[10.31, 3.50], [10.31, 3.88], [6.69, 3.88], [6.69, 4.16]], 'review');
  module(s, '执行权限与策略检查', 4.52, 4.20, 4.33, 0.97, 'review', 22);
  addText(s, '检查工具权限、调用参数与数据流向', 9.06, 4.53, 3.27, 0.61, 14, C.review);
  addRoute(s, [[5.16, 5.19], [5.16, 5.62], [2.79, 5.62], [2.79, 5.93]], 'control');
  addRoute(s, [[8.19, 5.19], [8.19, 5.57], [10.35, 5.57], [10.35, 5.87]], 'review');
  bar(s, 0.80, 5.95, 4.10, 0.66, 'trusted');
  addText(s, '不符合策略 → 拒绝执行', 1.04, 6.11, 3.71, 0.35, 17, C.trusted, { bold: true });
  bar(s, 8.36, 5.89, 4.18, 0.62, 'review');
  addText(s, '符合策略 → 允许工具执行', 8.60, 6.04, 3.75, 0.34, 16, C.review, { bold: true });
  addText(s, '若权限过宽或错误授权，危险操作可能落地', 8.39, 6.59, 4.20, 0.27, 12, C.risk);
  addText(s, '若错误执行，潜在影响包括', 0.82, 4.15, 3.35, 0.30, 14, C.muted);
  addText(s, '读取无关敏感信息', 0.82, 4.53, 3.35, 0.30, 14, C.body);
  addText(s, '向外发送数据', 0.82, 4.89, 3.35, 0.30, 14, C.body);
  addText(s, '修改或删除业务内容', 0.82, 5.25, 3.35, 0.30, 14, C.body);
  return s;
}
