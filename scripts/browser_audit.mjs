#!/usr/bin/env node
/**
 * Titan-UX Headless Browser & Visual QA Auditor (Playwright).
 * Checks console/page errors, failed network assets, horizontal overflow across
 * 375x812 / 768x1024 / 1440x900 viewports, broken images, keyboard focus,
 * touch targets, optional axe-core accessibility, and screenshots.
 *
 * Usage:
 *   node scripts/browser_audit.mjs <url> [--screenshot-dir .titan-ux/screenshots] [--dark] [--reduced-motion]
 */

import fs from "node:fs";
import path from "node:path";

function parseArgs(argv) {
  const args = { url: null, screenshotDir: null, dark: false, reducedMotion: false, help: false };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--help" || a === "-h") args.help = true;
    else if (a === "--dark") args.dark = true;
    else if (a === "--reduced-motion") args.reducedMotion = true;
    else if (a === "--screenshot-dir" && argv[i + 1]) {
      args.screenshotDir = argv[i + 1];
      i += 1;
    } else if (!a.startsWith("-") && !args.url) {
      args.url = a;
    }
  }
  return args;
}

const VIEWPORTS = [
  { name: "mobile", width: 375, height: 812 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "desktop", width: 1440, height: 900 },
];

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || !opts.url) {
    console.log("Usage: node scripts/browser_audit.mjs <url> [--screenshot-dir <dir>] [--dark] [--reduced-motion]");
    process.exit(opts.help ? 0 : 2);
  }

  let playwright;
  try {
    playwright = await import("playwright");
  } catch {
    console.error(
      JSON.stringify({
        error: "Playwright is not installed in this project.",
        install_hint: "npm install -D playwright && npx playwright install chromium",
      }, null, 2)
    );
    process.exit(2);
  }

  let AxeBuilder = null;
  try {
    const axeMod = await import("@axe-core/playwright");
    AxeBuilder = axeMod.default || axeMod.AxeBuilder;
  } catch {
    // Optional dependency
  }

  if (opts.screenshotDir) {
    fs.mkdirSync(opts.screenshotDir, { recursive: true });
  }

  const browser = await playwright.chromium.launch({ headless: true });
  const results = [];

  try {
    for (const vp of VIEWPORTS) {
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        colorScheme: opts.dark ? "dark" : "light",
        reducedMotion: opts.reducedMotion ? "reduce" : "no-preference",
      });
      const page = await context.newPage();

      const consoleErrors = [];
      const pageErrors = [];
      const failedRequests = [];

      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });
      page.on("pageerror", (err) => pageErrors.push(String(err)));
      page.on("response", (res) => {
        if (res.status() >= 400) {
          failedRequests.push({ url: res.url(), status: res.status() });
        }
      });

      await page.goto(opts.url, { waitUntil: "networkidle", timeout: 30000 });

      const domAudit = await page.evaluate(() => {
        const overflow = document.documentElement.scrollWidth > window.innerWidth;
        const brokenImages = Array.from(document.querySelectorAll("img"))
          .filter((img) => img.complete && img.naturalWidth === 0)
          .map((img) => img.getAttribute("src") || "(inline)");

        const unnamedControls = Array.from(document.querySelectorAll("button, a[href]"))
          .filter((el) => {
            const text = (el.textContent || "").trim();
            const aria = el.getAttribute("aria-label") || el.getAttribute("aria-labelledby") || el.getAttribute("title");
            return !text && !aria;
          }).length;

        const undersizedTargets = Array.from(document.querySelectorAll("button, a[href], input, select"))
          .filter((el) => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0 && (r.width < 24 || r.height < 24);
          }).length;

        return {
          overflow,
          scrollWidth: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
          brokenImages,
          unnamedControls,
          undersizedTargets,
        };
      });

      // Verify keyboard Tab moves focus cleanly
      await page.keyboard.press("Tab");
      const activeTag = await page.evaluate(() => document.activeElement?.tagName || "NONE");

      let axeViolations = null;
      if (AxeBuilder) {
        const axeReport = await new AxeBuilder({ page }).analyze();
        axeViolations = axeReport.violations.map((v) => ({
          id: v.id,
          impact: v.impact,
          nodes: v.nodes.length,
        }));
      }

      let screenshotPath = null;
      if (opts.screenshotDir) {
        screenshotPath = path.join(opts.screenshotDir, `${vp.name}-${opts.dark ? "dark" : "light"}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
      }

      results.push({
        viewport: vp.name,
        dimensions: `${vp.width}x${vp.height}`,
        consoleErrors,
        pageErrors,
        failedRequests,
        ...domAudit,
        firstTabFocusTag: activeTag,
        axeViolations,
        screenshotPath,
      });

      await context.close();
    }
  } finally {
    await browser.close();
  }

  const hasErrors = results.some(
    (r) =>
      r.consoleErrors.length > 0 ||
      r.pageErrors.length > 0 ||
      r.failedRequests.length > 0 ||
      r.overflow ||
      r.brokenImages.length > 0 ||
      r.unnamedControls > 0 ||
      (r.axeViolations && r.axeViolations.length > 0)
  );

  console.log(JSON.stringify({ url: opts.url, passed: !hasErrors, results }, null, 2));
  process.exit(hasErrors ? 1 : 0);
}

main().catch((err) => {
  console.error(JSON.stringify({ error: String(err) }));
  process.exit(2);
});
