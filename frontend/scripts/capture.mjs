import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
await mkdir("../docs/previews", { recursive: true });
const browser = await chromium.launch({
  channel: process.env.PLAYWRIGHT_CHANNEL || "msedge",
});
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
for (const route of ["/", "/dashboard", "/devices"]) {
  await page.goto(`http://127.0.0.1:3000${route}`);
  await page.waitForTimeout(1500);
  await page.screenshot({
    path: `../docs/previews/${route === "/" ? "landing" : route.slice(1)}.png`,
    fullPage: true,
  });
}
await page.setViewportSize({ width: 390, height: 844 });
await page.goto("http://127.0.0.1:3000/dashboard");
await page.waitForTimeout(1500);
await page.screenshot({ path: "../docs/previews/mobile.png", fullPage: true });
await browser.close();
