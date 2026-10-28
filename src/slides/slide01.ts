import { CONTENT } from '../content.js';
import { C, GRID } from '../theme.js';
import { addText } from '../components/text.js';
import { addArrow, addLine } from '../components/connector.js';

export function slide01(pptx: any) {
  const s = pptx.addSlide(); s.background = { color: C.title }; s.addNotes(CONTENT[0].notes);
  addText(s, '计算机安全  /  课程汇报', 0.8, 0.7, 6.4, 0.3, 14, 'A8C9CB', { bold: true, charSpacing: 1 });
  addText(s, '智能体应用的', 0.8, 1.70, 7.8, 0.76, 39, C.white, { bold: true });
  addText(s, '提示注入攻击', 0.8, 2.56, 7.8, 0.76, 39, C.white, { bold: true });
  addText(s, '检测与防御', 0.8, 3.42, 7.8, 0.76, 39, C.white, { bold: true });
  s.addShape('line', { x: 0.8, y: 4.48, w: 1.2, h: 0, line: { color: '6BA7AD', width: 2 } });
  addText(s, CONTENT[0].intro, 0.8, 4.76, 7.3, 0.48, 17, 'D8E5E9');
  addText(s, '外部内容', 8.10, 2.27, 2.17, 0.36, 18, 'C7D1D9');
  addText(s, '邮件 / 网页 / 工具结果', 8.10, 2.70, 2.40, 0.60, 14, 'A8BBC7');
  addLine(s, 10.22, 2.17, 10.22, 4.75, 'data');
  addArrow(s, 9.80, 3.35, 10.72, 3.35, 'risk', true);
  addText(s, '信任边界', 9.39, 3.64, 1.35, 0.25, 11, 'F0A49C');
  addText(s, '智能体决策', 10.78, 3.12, 2.20, 0.42, 19, C.white, { bold: true });
  addArrow(s, 11.76, 3.70, 11.76, 4.34, 'control');
  addText(s, '工具执行', 10.78, 4.53, 2.17, 0.40, 19, C.white, { bold: true });
  addText(s, '攻击风险：数据被误当成指令', 8.12, 5.74, 4.4, 0.42, 14, 'F0A49C');
  addText(s, '汇报人：待填写   /   日期：待填写', GRID.left, 6.77, 7.8, 0.25, 11, 'A8BBC7');
  addText(s, '来源：调研报告 pp.1–2', 9.8, 6.77, 2.9, 0.25, 11, 'A8BBC7', { align: 'right' });
  return s;
}
