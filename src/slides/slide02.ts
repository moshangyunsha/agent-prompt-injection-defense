import { makeSlide } from './common.js';
import { addText } from '../components/text.js';
import { addArrow, addRoute } from '../components/connector.js';
import { module, rule, marker } from '../components/editorial.js';
import { C } from '../theme.js';

export function slide02(pptx: any) {
  const s = makeSlide(pptx, 2);
  addText(s, '普通问答', 0.78, 1.86, 3.65, 0.4, 21, C.title, { bold: true });
  addText(s, '单次输入 → 单次输出', 0.78, 2.31, 3.65, 0.3, 14, C.muted);
  rule(s, 0.78, 2.74, 3.78, C.border);
  marker(s, '01', 0.82, 3.05, 'trusted'); addText(s, '用户问题', 1.30, 2.99, 2.7, 0.38, 20, C.title);
  addArrow(s, 1.0, 3.51, 1.0, 3.93, 'control');
  marker(s, '02', 0.82, 4.12); addText(s, '语言模型', 1.30, 4.06, 2.7, 0.38, 20, C.title);
  addArrow(s, 1.0, 4.58, 1.0, 5.00, 'data');
  marker(s, '03', 0.82, 5.18); addText(s, '文本回答', 1.30, 5.12, 2.7, 0.38, 20, C.title);
  s.addShape('line', { x: 4.91, y: 1.87, w: 0, h: 4.48, line: { color: C.border, width: 1 } });
  addText(s, '智能体应用', 5.38, 1.86, 4.0, 0.4, 21, C.title, { bold: true });
  addText(s, '新增外部数据路径与真实执行能力', 5.38, 2.31, 6.7, 0.3, 14, C.muted);
  rule(s, 5.38, 2.74, 7.18, C.border);
  addText(s, '可信控制', 5.40, 3.00, 1.3, 0.28, 13, C.trusted, { bold: true });
  addText(s, '系统 / 开发者要求', 5.40, 3.34, 2.25, 0.38, 16, C.title);
  addText(s, '用户任务', 5.40, 3.78, 2.25, 0.38, 16, C.title);
  s.addShape('line', { x: 7.52, y: 3.02, w: 0, h: 1.28, line: { color: C.border, width: 1 } });
  addText(s, '不可信数据', 7.89, 3.00, 1.6, 0.28, 13, C.external, { bold: true });
  addText(s, '邮件 / 网页 / 工具结果', 7.89, 3.34, 3.8, 0.38, 16, C.title);
  addArrow(s, 7.20, 4.34, 8.64, 4.65, 'control');
  addArrow(s, 9.30, 4.09, 9.30, 4.65, 'data');
  module(s, '语言模型', 8.15, 4.67, 2.45, 0.67, 'trusted', 17);
  addArrow(s, 9.38, 5.36, 9.38, 5.70, 'control');
  module(s, '工具接口 / 权限检查', 7.84, 5.72, 3.07, 0.58, 'review', 15);
  addText(s, '读取 · 查询 · 发送 / 修改', 5.38, 6.15, 2.35, 0.27, 14, C.body);
  addRoute(s, [[10.93, 6.00], [12.14, 6.00], [12.14, 4.99], [10.63, 4.99]], 'data');
  addText(s, '结果回流', 11.21, 5.44, 0.95, 0.25, 12, C.external);
  addText(s, '外部数据是任务输入，不因此获得指令权限。', 0.78, 6.59, 11.9, 0.32, 17, C.trusted, { bold: true });
  return s;
}
