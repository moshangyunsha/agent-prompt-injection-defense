import { createRequire } from 'node:module';
import { drawResearchDeck } from '../src/research-deck.js';
const require=createRequire(import.meta.url),Pptx=require('pptxgenjs');
for(const count of [1,6,10,16,26]) {
  const pptx=new Pptx();pptx.layout='LAYOUT_WIDE';
  pptx.defineSlideMaster({title:'LIGHT',background:{color:'FFFFFF'},objects:[]});
  drawResearchDeck(pptx);
  pptx._slides=pptx._slides.slice(0,count);
  await pptx.writeFile({fileName:`output/archive/diagnostic-${count}.pptx`});
}
