import { C, GRID, PAGE, SIZE } from '../theme.js';
import { addText } from './text.js';
type Slide = any;
export function addSourceFooter(slide: Slide, source: string, page: number) {
  slide.addShape('line', { x: GRID.left, y: GRID.footerY - 0.13, w: PAGE.w - 2 * GRID.left, h: 0,
    line: { color: C.border, width: 0.7 } });
  addText(slide, source, GRID.left, GRID.footerY, PAGE.w - 2 * GRID.left - 0.6, 0.25, SIZE.footer, C.muted);
  addText(slide, String(page).padStart(2, '0'), PAGE.w - GRID.right - 0.38, GRID.footerY, 0.38, 0.25, SIZE.footer, C.muted, { align: 'right' });
}

