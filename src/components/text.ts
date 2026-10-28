import { C, FONT, GRID, SIZE, PAGE } from '../theme.js';
import type { SlideContent } from '../content.js';

type Slide = any;
export function addText(slide: Slide, text: string, x: number, y: number, w: number, h: number, size = SIZE.body, color = C.body, opts: Record<string, unknown> = {}) {
  slide.addText(text, { x, y, w, h, fontFace: FONT.body, fontSize: size, color,
    margin: 0, breakLine: false, valign: 'mid', ...opts });
}
export function addTitle(slide: Slide, data: SlideContent, page: number) {
  slide.background = { color: C.bg };
  addText(slide, data.section, GRID.left, GRID.sectionY, 7, 0.23, 11, C.trusted, { bold: true, charSpacing: 0.8 });
  addText(slide, data.title, GRID.left, GRID.titleY, PAGE.w - 2 * GRID.left, 0.55, SIZE.title, C.title, { bold: true });
  addText(slide, data.intro, GRID.left, GRID.introY, PAGE.w - 2 * GRID.left, 0.43, SIZE.intro, C.muted);
}

