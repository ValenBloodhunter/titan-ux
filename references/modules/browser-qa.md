# Playwright Headless Browser & Visual QA Protocol

## 1. When & How to Run Browser QA

Run `node <skill_dir>/scripts/browser_audit.mjs <url>` whenever a dev/preview server is reachable (requires `playwright` installed in the project or globally; optionally uses `@axe-core/playwright` if present).

## 2. Multi-Viewport & Mode Matrix

Verify every critical route across:
1. **Mobile (`375x812`)**: Check single-column stacking, bottom/drawer navigation, `44px` tap targets, and zero horizontal overflow (`scrollWidth <= innerWidth`).
2. **Tablet (`768x1024`)**: Check collapsible rails, grid breakpoints, and modal centering.
3. **Desktop (`1440x900`)**: Check max container rhythm, sticky headers/sidebars, and prose measure.
4. **Dark & Light Themes + `prefers-reduced-motion: reduce`**: Check contrast legibility, elevated surface hierarchy, and zero frozen/invisible elements under reduced motion.

## 3. Automated Runtime Checks (`browser_audit.mjs`)

- **Zero Console Errors & Uncaught Exceptions:** Any `console.error`, React hydration mismatch warning, or `pageerror` fails the QA gate.
- **Zero Failed Assets / HTTP `>= 400`:** Broken stylesheets, fonts, API calls, or `404` images fail immediately.
- **Broken Images (`naturalWidth === 0`):** Every visible `<img>` must decode cleanly.
- **Horizontal Overflow (`scrollWidth > innerWidth`):** Zero unwanted horizontal page scroll on any tested viewport.
- **Focus & Interactive Verification:** Programmatic `Tab` traversal verifies visible focus indicators, modal open/Escape close/focus return, and button/form interactive states.

## 4. Visual Screenshot Critique (Never Guess Rendering)

When screenshots are captured, inspect them directly for: overlapping text, clipped buttons, awkward widows/orphans, unbalanced whitespace, weak visual focal point, low-contrast muted labels, or generic AI-slop aesthetics — then fix and re-capture.
