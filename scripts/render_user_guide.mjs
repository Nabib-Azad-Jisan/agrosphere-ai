import { chromium } from '../frontend/node_modules/@playwright/test/index.mjs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import { mkdir } from 'node:fs/promises';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.resolve(project, '..', 'AgroSphere_AI_User_Tutorial.pdf');
const browser = await chromium.launch({ channel: 'msedge' });
try {
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 }, deviceScaleFactor: 1 });
  await page.emulateMedia({ media: 'print' });
  await page.goto(pathToFileURL(path.join(project, 'docs/user-tutorial.html')).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const failures = await page.locator('.page').evaluateAll(pages => pages.flatMap((element, index) => {
    const body = element.querySelector('.content').getBoundingClientRect();
    const footer = element.querySelector('.footer').getBoundingClientRect();
    return body.bottom > footer.top - 8 ? [{ page: index + 1, overflowPx: Math.round(body.bottom - footer.top + 8) }] : [];
  }));
  if (failures.length) throw new Error(`Page content overlaps footer: ${JSON.stringify(failures)}`);
  const missing = await page.locator('img').evaluateAll(images => images.filter(img => !img.complete || !img.naturalWidth).map(img => img.src));
  if (missing.length) throw new Error(`Missing images: ${missing.join(', ')}`);
  await page.pdf({ path: output, format: 'A4', preferCSSPageSize: true, printBackground: true, tagged: true, outline: true });
  const previews = path.join(project, 'docs/previews/user-guide');
  await mkdir(previews, { recursive: true });
  for (const index of [0, 3, 8, 11]) {
    await page.locator('.page').nth(index).screenshot({ path: path.join(previews, `page-${index + 1}.png`) });
  }
  console.log(`Created PDF: ${output}`);
} finally {
  await browser.close();
}
