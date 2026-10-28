import { CONTENT } from '../content.js';
import { addTitle } from '../components/text.js';
import { addSourceFooter } from '../components/footer.js';

export function makeSlide(pptx: any, index: number) {
  const slide = pptx.addSlide();
  addTitle(slide, CONTENT[index - 1], index);
  addSourceFooter(slide, CONTENT[index - 1].source, index);
  slide.addNotes(CONTENT[index - 1].notes);
  return slide;
}

