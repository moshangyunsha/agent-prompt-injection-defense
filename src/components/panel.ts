import { C } from '../theme.js';
type Slide = any;
export function addPanel(slide: Slide, x: number, y: number, w: number, h: number, tint = C.white, stroke = C.border) {
  slide.addShape('rect', { x, y, w, h, fill: { color: tint }, line: { color: stroke, width: 1 } });
}

