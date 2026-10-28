import { makeSlide } from './common.js';
import { addText } from '../components/text.js';
import { addArrow, addLine, addRoute } from '../components/connector.js';
import { module, rule } from '../components/editorial.js';
import { C } from '../theme.js';

export function slide08(pptx: any) {
  const s = makeSlide(pptx, 8);
  addText(s, 'CaMeL  /  Defeating Prompt Injections by Design', 0.78, 1.76, 9.74, 0.39, 19, C.title, { bold: true });
  addText(s, '教学化简架构', 10.48, 1.82, 2.07, 0.28, 13, C.muted, { align: 'right' });
  // The frame marks the control plane: untrusted content never creates authority here.
  s.addShape('rect', { x: 0.78, y: 2.28, w: 11.78, h: 2.24,
    fill: { color: C.white, transparency: 100 }, line: { color: C.trusted, width: 1, dashType: 'dash' } });
  addText(s, '可信控制流程', 0.99, 2.39, 2.35, 0.30, 14, C.trusted, { bold: true });
  module(s, '用户授权任务', 0.98, 3.08, 1.72, 0.70, 'trusted', 14);
  addArrow(s, 2.72, 3.43, 3.10, 3.43, 'control');
  module(s, '特权模型\n规划控制流', 3.14, 3.08, 1.86, 0.70, 'trusted', 14);
  addArrow(s, 5.02, 3.43, 5.40, 3.43, 'control');
  module(s, '受约束的解释器\n执行控制流', 5.44, 3.00, 2.22, 0.86, 'trusted', 14);
  addArrow(s, 7.68, 3.43, 8.06, 3.43, 'control');
  s.addShape('rect', { x: 8.10, y: 2.76, w: 2.34, h: 1.35,
    fill: { color: C.paleAmber }, line: { color: C.review, width: 1.2 } });
  addText(s, '策略门', 8.27, 2.84, 1.96, 0.28, 14, C.review, { bold: true });
  rule(s, 8.27, 3.19, 1.96, C.review, 0.8);
  addText(s, '能力权限', 8.27, 3.27, 1.96, 0.26, 14, C.title);
  addText(s, '来源与数据流', 8.27, 3.62, 1.96, 0.26, 14, C.title);
  addArrow(s, 10.46, 3.43, 10.83, 3.43, 'control');
  module(s, '实际工具执行', 10.87, 3.08, 1.45, 0.70, 'trusted', 13);
  addRoute(s, [[9.27, 4.13], [9.27, 4.34], [9.75, 4.34]], 'review');
  addText(s, '任一策略不满足 → 拒绝', 9.86, 4.17, 2.47, 0.29, 12, C.review);
  addText(s, '信任边界：数据可参与计算，不可授予权限', 0.98, 4.71, 5.57, 0.34, 14, C.risk, { bold: true });
  addText(s, '受控数据入口', 6.74, 4.72, 1.70, 0.27, 12, C.external);
  rule(s, 0.78, 5.10, 11.78, C.external, 1.1, 'dash');
  addText(s, '不可信数据处理', 0.98, 5.18, 2.43, 0.30, 14, C.external, { bold: true });
  module(s, '外部邮件', 0.98, 5.62, 1.60, 0.62, 'external', 14);
  addArrow(s, 2.60, 5.93, 3.00, 5.93, 'data');
  module(s, '隔离模型处理', 3.04, 5.62, 2.14, 0.62, 'external', 14);
  addArrow(s, 5.20, 5.93, 5.60, 5.93, 'data');
  module(s, '带来源标记的数据结果', 5.64, 5.62, 3.13, 0.62, 'external', 14);
  addRoute(s, [[7.21, 5.60], [7.21, 5.29], [6.55, 5.29], [6.55, 3.88]], 'data');
  addText(s, '只把受控数据结果送入执行过程', 9.06, 5.72, 3.23, 0.40, 14, C.external);
  addText(s, '外部数据可参与计算，但工具权限只由可信控制与策略检查决定。', 0.78, 6.59, 11.78, 0.31, 15, C.trusted, { bold: true });
  return s;
}
