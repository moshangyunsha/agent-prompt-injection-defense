import { C, FONT, SIZE } from '../theme.js';
type Slide = any;
export function addNode(slide: Slide, label: string, x: number, y: number, w: number, h: number,
  kind: 'trusted' | 'external' | 'risk' | 'review' | 'neutral' = 'neutral', size = SIZE.node) {
  const style = {
    trusted: [C.paleTeal, C.trusted], external: [C.paleGray, C.external],
    risk: [C.paleRed, C.risk], review: [C.paleAmber, C.review], neutral: [C.white, C.border],
  }[kind];
  slide.addShape('roundRect', { x, y, w, h, rectRadius: 0.08, radius: 0.08,
    fill: { color: style[0] }, line: { color: style[1], width: kind === 'neutral' ? 1 : 1.5 } });
  slide.addText(label, { x: x + 0.08, y: y + 0.04, w: w - 0.16, h: h - 0.08,
    fontFace: FONT.body, fontSize: size, color: kind === 'risk' ? C.risk : C.title,
    bold: kind !== 'neutral', align: 'center', valign: 'mid', margin: 0,
    breakLine: false, fit: 'shrink' });
}

