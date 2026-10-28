import { makeSlide } from './common.js';
import { addText } from '../components/text.js';
import { addArrow, addRoute } from '../components/connector.js';
import { module, rule, bar } from '../components/editorial.js';
import { C } from '../theme.js';

export function slide07(pptx: any) {
  const s = makeSlide(pptx, 7);
  addText(s, '01  来源标记  /  Spotlighting', 0.78, 1.83, 5.30, 0.39, 20, C.title, { bold: true });
  addText(s, '让来源信号随外部内容进入模型', 0.78, 2.22, 5.40, 0.28, 14, C.muted);
  rule(s, 0.78, 2.66, 11.80);
  // A transformation of data, not a row of generic modules.
  addText(s, '原始邮件', 0.82, 3.06, 1.45, 0.37, 18, C.external, { bold: true });
  addArrow(s, 2.34, 3.25, 2.84, 3.25, 'data');
  module(s, '标记来源 / 数据变换', 2.88, 2.94, 3.14, 0.62, 'review', 16);
  addArrow(s, 6.06, 3.25, 6.55, 3.25, 'data');
  s.addShape('rect', { x: 6.59, y: 2.94, w: 3.47, h: 0.62,
    fill: { color: C.paleGray }, line: { color: C.external, width: 1 } });
  addText(s, '外部来源  |  数据片段 A / B / C', 6.78, 3.10, 3.11, 0.27, 14, C.body);
  addArrow(s, 10.10, 3.25, 10.56, 3.25, 'data');
  addText(s, '模型识别来源', 10.63, 3.05, 1.86, 0.43, 16, C.trusted, { bold: true });
  addText(s, '教学示意：不代表论文完整算法。标记仍可能被忽略或遭适应性攻击。', 0.82, 3.78, 11.68, 0.32, 14, C.muted);
  rule(s, 0.78, 4.34, 11.80);
  addText(s, '02  风险判断  /  专用检测模型', 0.78, 4.56, 6.51, 0.39, 20, C.title, { bold: true });
  addText(s, '内容进入模型前，先判断是否含可疑指令', 0.78, 4.97, 8.18, 0.28, 14, C.muted);
  addText(s, '待检测内容', 0.82, 5.57, 2.05, 0.37, 17, C.external, { bold: true });
  addArrow(s, 2.81, 5.76, 3.31, 5.76, 'data');
  module(s, '安全分类模型', 3.35, 5.42, 2.48, 0.69, 'review', 16);
  addArrow(s, 5.87, 5.76, 6.34, 5.76, 'review');
  addText(s, '风险判断', 6.47, 5.56, 1.70, 0.37, 17, C.title, { bold: true });
  addRoute(s, [[8.08, 5.60], [8.55, 5.60], [8.55, 5.37], [9.02, 5.37]], 'control');
  addRoute(s, [[8.08, 5.91], [8.55, 5.91], [8.55, 6.17], [9.02, 6.17]], 'review');
  addText(s, '低风险  /  继续处理', 9.15, 5.20, 3.05, 0.35, 16, C.trusted, { bold: true });
  addText(s, '高风险  /  拦截或审核', 9.15, 6.00, 3.21, 0.35, 16, C.review, { bold: true });
  addText(s, '检测可能误报或漏报；两种机制均不能替代工具权限控制。', 0.78, 6.61, 11.80, 0.30, 15, C.trusted, { bold: true });
  return s;
}
