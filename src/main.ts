import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { FONT } from './theme.js';
import { RESEARCH_CONTENT } from './research-content.js';
import { drawResearchDeck } from './research-deck.js';
import { CONTENT } from './content.js';

const require = createRequire(import.meta.url);
const PptxGenJS = require('pptxgenjs');
const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = '课程汇报';
pptx.subject = '智能体应用的提示注入攻击检测与防御';
pptx.title = '智能体应用的提示注入攻击检测与防御';
pptx.lang = 'zh-CN';
pptx.theme = { headFontFace: FONT.body, bodyFontFace: FONT.body, lang: 'zh-CN' };
pptx.defineSlideMaster({ title: 'LIGHT', background: { color: 'FFFFFF' }, objects: [] });
drawResearchDeck(pptx);
await pptx.writeFile({ fileName: fileURLToPath(new URL('../output/presentation.pptx', import.meta.url)) });
execFileSync('python', ['scripts/apply-template.py'], { stdio: 'inherit' });
fs.writeFileSync('output/page-manifest.json', JSON.stringify(RESEARCH_CONTENT, null, 2), 'utf8');
fs.writeFileSync('output/source-map.md',RESEARCH_CONTENT.map(d=>`# 第${d.id}页：${d.title}\n\n${d.references}`).join('\n\n'),'utf8');
fs.writeFileSync('output/archive/original-nine-speaker-notes.md',CONTENT.map((d,i)=>`# 第${i+1}页\n\n${d.notes}`).join('\n\n'),'utf8');
fs.writeFileSync('output/speaker-script.md',RESEARCH_CONTENT.map(d=>`# 第${d.id}页：${d.title}\n\n${d.notes.split('\n\n参考依据')[0]}`).join('\n\n'),'utf8');
if(!process.argv.includes('--regenerate-all') && fs.existsSync('output/archive/presentation-user-edited-before-agenda.pptx')) {
  execFileSync('python', ['scripts/preserve-user-edits.py'], { stdio:'inherit' });
}
console.log(`Built ${RESEARCH_CONTENT.length} research slides with native editable content.`);

