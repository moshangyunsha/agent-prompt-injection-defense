import { C } from '../theme.js';
import { addText } from './text.js';

type Slide = any;
export type Tone = 'trusted' | 'external' | 'risk' | 'review' | 'neutral';
const tone = { trusted: C.trusted, external: C.external, risk: C.risk, review: C.review, neutral: C.darkLine };
const fill = { trusted: C.paleTeal, external: C.paleGray, risk: C.paleRed, review: C.paleAmber, neutral: C.white };

/** A rectangle represents a real system boundary or interface, never a generic text card. */
export function module(slide: Slide, title: string, x: number, y: number, w: number, h: number,
  kind: Tone = 'neutral', size = 15) {
  slide.addShape('rect', { x, y, w, h, fill: { color: fill[kind] },
    line: { color: tone[kind], width: kind === 'neutral' ? 1 : 1.2 } });
  addText(slide, title, x + 0.12, y + 0.06, w - 0.24, h - 0.12, size,
    kind === 'risk' ? C.risk : C.title, { bold: true, align: 'center' });
}

export function rule(slide: Slide, x: number, y: number, w: number, color = C.border, width = 1,
  dashType: 'solid' | 'dash' = 'solid') {
  slide.addShape('line', { x, y, w, h: 0, line: { color, width, dashType } });
}

export function marker(slide: Slide, n: string, x: number, y: number, kind: Tone = 'neutral') {
  addText(slide, n, x, y, 0.4, 0.24, 11, tone[kind], { bold: true });
}

export function bar(slide: Slide, x: number, y: number, w: number, h: number, kind: Tone) {
  slide.addShape('rect', { x, y, w, h, fill: { color: fill[kind] }, line: { color: fill[kind] } });
  slide.addShape('line', { x, y, w: 0, h, line: { color: tone[kind], width: 2.2 } });
}
