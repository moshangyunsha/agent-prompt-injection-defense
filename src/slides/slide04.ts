import { makeSlide } from './common.js';
import { addText } from '../components/text.js';
import { addArrow, addRoute } from '../components/connector.js';
import { module, rule } from '../components/editorial.js';
import { C } from '../theme.js';

export function slide04(pptx: any) {
  const s = makeSlide(pptx, 4);
  addText(s, '直接注入', 0.78, 1.86, 3.0, 0.4, 22, C.title, { bold: true });
  addText(s, '攻击者控制模型接收的输入', 0.78, 2.28, 5.8, 0.3, 14, C.muted);
  rule(s, 0.78, 2.73, 11.80);
  addText(s, '攻击者', 0.89, 3.19, 1.55, 0.44, 19, C.risk, { bold: true });
  addArrow(s, 2.52, 3.42, 3.22, 3.42, 'risk');
  module(s, '输入界面', 3.26, 3.10, 2.08, 0.69, 'risk', 17);
  addArrow(s, 5.38, 3.42, 6.21, 3.42, 'risk');
  module(s, '目标模型', 6.25, 3.10, 2.18, 0.69, 'neutral', 17);
  addArrow(s, 8.47, 3.42, 9.23, 3.42, 'risk', true);
  addText(s, '试图改变原有任务', 9.36, 3.19, 2.95, 0.44, 17, C.risk, { bold: true });
  addText(s, '攻击入口就在输入界面', 3.27, 3.95, 4.15, 0.30, 14, C.risk);
  rule(s, 0.78, 4.52, 11.80);
  addText(s, '间接注入', 0.78, 4.72, 3.0, 0.4, 22, C.title, { bold: true });
  addText(s, '攻击者先改变外部内容，正常任务再把它带入模型', 3.31, 4.80, 8.8, 0.3, 14, C.muted);
  addText(s, '攻击者', 0.89, 5.64, 1.55, 0.44, 19, C.risk, { bold: true });
  addArrow(s, 2.52, 5.87, 3.22, 5.87, 'risk');
  module(s, '被污染的网页 / 邮件', 3.26, 5.54, 2.65, 0.69, 'external', 16);
  addArrow(s, 5.95, 5.87, 6.58, 5.87, 'data');
  addText(s, '智能体读取', 6.71, 5.66, 1.70, 0.38, 17, C.title);
  addArrow(s, 8.52, 5.87, 9.19, 5.87, 'data');
  module(s, '目标模型', 9.23, 5.54, 2.18, 0.69, 'neutral', 17);
  addText(s, '正常任务带入', 6.69, 6.31, 2.2, 0.27, 13, C.external);
  addText(s, '差别在攻击入口；邮件案例属于间接注入。', 0.78, 6.60, 11.8, 0.30, 17, C.trusted, { bold: true });
  return s;
}
