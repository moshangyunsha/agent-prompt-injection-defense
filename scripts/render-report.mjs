import fs from 'node:fs';
import { createCanvas, DOMMatrix, Path2D, ImageData } from '@napi-rs/canvas';
globalThis.DOMMatrix = DOMMatrix; globalThis.Path2D = Path2D; globalThis.ImageData = ImageData;
const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
const doc = await pdfjs.getDocument({ data: new Uint8Array(fs.readFileSync('input/提示注入攻击检测与防御_第一节课调研报告.pdf')), useSystemFonts: true }).promise;
for (const n of [5, 6, 8, 9, 10, 12]) {
  const page = await doc.getPage(n), viewport = page.getViewport({ scale: 2 });
  const canvas = createCanvas(viewport.width, viewport.height);
  await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
  fs.writeFileSync('assets/source/report-page' + String(n).padStart(2, '0') + '.png', canvas.toBuffer('image/png'));
}
console.log('Rendered four source pages.');
