import fs from 'node:fs';
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';

const path = process.argv[2];
const data = new Uint8Array(fs.readFileSync(path));
const pdf = await getDocument({ data, useSystemFonts: true, disableFontFace: true }).promise;
const pages = [];
for (let i = 1; i <= pdf.numPages; i++) {
  const page = await pdf.getPage(i);
  const content = await page.getTextContent();
  pages.push(`\n\n===== PAGE ${i} =====\n` + content.items.map((item) => item.str).join(' '));
}
fs.writeFileSync('output/report-extracted.txt', pages.join(''), 'utf8');
console.log(`Extracted ${pdf.numPages} pages`);
