import { C } from '../theme.js';
type Slide = any;
export function addArrow(slide: Slide, x1: number, y1: number, x2: number, y2: number,
  kind: 'data' | 'control' | 'risk' | 'review' = 'data', dashed = false) {
  const color = { data: C.external, control: C.trusted, risk: C.risk, review: C.review }[kind];
  slide.addShape('line', { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001,
    h: Math.abs(y2 - y1) || 0.001, flipH: x2 < x1, flipV: y2 < y1,
    line: { color, width: kind === 'risk' ? 2 : 1.5, dashType: dashed ? 'dash' : 'solid', endArrowType: 'triangle' } });
}
export function addLine(slide: Slide, x1: number, y1: number, x2: number, y2: number,
  kind: 'data' | 'control' | 'risk' | 'review' = 'data', dashed = false) {
  const color = { data: C.external, control: C.trusted, risk: C.risk, review: C.review }[kind];
  slide.addShape('line', { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001,
    h: Math.abs(y2 - y1) || 0.001, flipH: x2 < x1, flipV: y2 < y1,
    line: { color, width: 1.5, dashType: dashed ? 'dash' : 'solid' } });
}
export function addRoute(slide: Slide, points: [number, number][],
  kind: 'data' | 'control' | 'risk' | 'review' = 'data', dashed = false) {
  if (points.length < 2) throw new Error('A route needs at least two points');
  for (let i = 0; i < points.length - 2; i++) {
    addLine(slide, ...points[i], ...points[i + 1], kind, dashed);
  }
  addArrow(slide, ...points[points.length - 2], ...points[points.length - 1], kind, dashed);
}
export function addTrustBoundary(slide: Slide, x: number, y: number, w: number, h: number) {
  slide.addShape('rect', { x, y, w, h, fill: { color: C.white, transparency: 100 },
    line: { color: C.external, width: 1.1, dashType: 'dash' } });
}

