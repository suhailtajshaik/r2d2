#!/bin/bash
# Convert markdown to styled PDF using Puppeteer
# Usage: md-to-pdf.sh <input.md> <output.pdf>
# - No headers/footers except page numbers (bottom center)
# - Professional styling with proper margins

set -e

INPUT="$1"
OUTPUT="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
  echo "Usage: md-to-pdf.sh <input.md> <output.pdf>"
  exit 1
fi

TMPHTML=$(mktemp /tmp/md2pdf-XXXXXX.html)
TMPJS=$(mktemp /tmp/md2pdf-XXXXXX.js)

# Step 1: Convert MD to styled HTML
node -e "
const fs = require('fs');
const md = fs.readFileSync('${INPUT}', 'utf8');

let html = md
  .replace(/^#### (.*$)/gm, '<h4>\$1</h4>')
  .replace(/^### (.*$)/gm, '<h3>\$1</h3>')
  .replace(/^## (.*$)/gm, '<h2>\$1</h2>')
  .replace(/^# (.*$)/gm, '<h1>\$1</h1>')
  .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>\$1</em></strong>')
  .replace(/\*\*(.*?)\*\*/g, '<strong>\$1</strong>')
  .replace(/\*(.*?)\*/g, '<em>\$1</em>')
  .replace(/^\- \[ \] (.*$)/gm, '<li>☐ \$1</li>')
  .replace(/^\- \[x\] (.*$)/gm, '<li>☑ \$1</li>')
  .replace(/^\- (.*$)/gm, '<li>\$1</li>')
  .replace(/^\d+\. (.*$)/gm, '<li>\$1</li>')
  .replace(/\`\`\`[\\s\\S]*?\`\`\`/g, (match) => '<pre>' + match.replace(/\`\`\`\\w*/g, '').replace(/\`\`\`/g, '').replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</pre>')
  .replace(/\`([^\`]+)\`/g, '<code>\$1</code>')
  .replace(/^> (.*$)/gm, '<blockquote>\$1</blockquote>')
  .replace(/^---$/gm, '<hr>')
  .replace(/^\\|(.+)\\|$/gm, (match) => {
    const cells = match.split('|').filter(c => c.trim());
    if (cells.every(c => /^[\\s-:]+$/.test(c))) return '';
    const tag = 'td';
    return '<tr>' + cells.map(c => '<' + tag + '>' + c.trim() + '</' + tag + '>').join('') + '</tr>';
  })
  .replace(/(<tr>.*<\\/tr>\\n?)+/g, '<table>\$&</table>')
  .replace(/\\n\\n/g, '</p><p>');

const fullHtml = \`<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
body { font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; max-width: 780px; margin: 0 auto; padding: 0; font-size: 13px; line-height: 1.7; color: #2d2d2d; }
h1 { color: #111; border-bottom: 2.5px solid #1a1a2e; padding-bottom: 10px; font-size: 22px; margin-top: 10px; letter-spacing: -0.3px; }
h2 { color: #1a1a2e; margin-top: 28px; font-size: 16px; border-bottom: 1px solid #e0e0e0; padding-bottom: 6px; letter-spacing: -0.2px; }
h3 { color: #333; font-size: 14px; margin-top: 18px; }
h4 { color: #555; font-size: 13px; }
p { margin: 8px 0; }
pre { background: #f6f8fa; padding: 14px; border-radius: 6px; border: 1px solid #e1e4e8; overflow-x: auto; font-size: 11px; font-family: 'SF Mono', 'Fira Code', Consolas, monospace; white-space: pre-wrap; }
code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-size: 12px; }
li { margin: 3px 0; }
hr { border: none; border-top: 1px solid #dee2e6; margin: 25px 0; }
strong { color: #111; }
em { color: #555; }
blockquote { border-left: 3px solid #1a1a2e; margin: 15px 0; padding: 12px 20px; background: #f6f8fa; font-style: italic; color: #444; border-radius: 0 4px 4px 0; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 11.5px; }
th, td { border: 1px solid #d0d7de; padding: 7px 10px; text-align: left; }
th { background: #f0f4f8; font-weight: 600; color: #1a1a2e; }
tr:nth-child(even) { background: #f8f9fb; }
tr:first-child td { font-weight: 600; background: #eef2f7; color: #1a1a2e; }
</style>
</head><body><p>\${html}</p></body></html>\`;

fs.writeFileSync('${TMPHTML}', fullHtml);
"

# Step 2: Generate PDF via Puppeteer with page numbers only
cat > "${TMPJS}" << 'PUPPETEER_SCRIPT'
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const htmlPath = process.argv[2];
  const outputPath = process.argv[3];

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });

  await page.pdf({
    path: outputPath,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `
      <div style="width: 100%; text-align: center; font-size: 9px; color: #999; font-family: -apple-system, Arial, sans-serif; padding-top: 5px;">
        <span class="pageNumber"></span>
      </div>
    `,
    margin: {
      top: '50px',
      bottom: '60px',
      left: '45px',
      right: '45px'
    }
  });

  await browser.close();
})();
PUPPETEER_SCRIPT

NODE_PATH=/usr/lib/node_modules node "${TMPJS}" "${TMPHTML}" "${OUTPUT}"

rm -f "${TMPHTML}" "${TMPJS}"
echo "PDF created: ${OUTPUT}"
