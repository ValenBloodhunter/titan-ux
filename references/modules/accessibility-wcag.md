# Accessibility (WCAG 2.2 AA/AAA), APCA & Web Design Guidelines

Synthesizes Vercel `web-design-guidelines`, WAI-ARIA Authoring Practices, WCAG 2.2, and APCA perceptual contrast.

## 1. Document Landmarks & Heading Hierarchy

- Every page requires: `<html lang="...">`, a skip-to-content link (`<a href="#main-content" class="sr-only focus:not-sr-only ...">Skip to main content</a>`), `<header>`, `<nav aria-label="Primary">`, `<main id="main-content">`, and `<footer>`.
- Exactly one `<h1>` per route; never skip heading levels (`h1 -> h3` without `h2`). Use visual utility classes for styling rather than misusing heading levels.

## 2. Native Interactive Semantics & Accessible Names

- **Right Element First:** Actions that mutate state/submit/open overlays use `<button type="button|submit">`. Navigation uses `<a href>`. Never attach `onClick` to `<div>` or `<span>` without `role="button"`, `tabIndex={0}`, AND `Enter`/`Space` keyboard handling — better yet, always use `<button>`.
- **Icon-Only Controls:** Must have a concise `aria-label` (or `<span className="sr-only">Close settings</span>`); the inner SVG gets `aria-hidden="true"`.
- **Images:** Informative images carry meaningful `alt`; decorative shapes/patterns/icons get `alt=""` and `aria-hidden="true"`.
- **Links:** Never use `"Click here"` or `"Read more"` alone — make link text descriptive or extend via `aria-label`. External `target="_blank"` links include `rel="noopener noreferrer"`.

## 3. Focus Management, Keyboard Parity & Touch Targets

- **Focus Rings:** NEVER write `outline-none` / `outline: none` / `focus:outline-none` without immediately applying a high-contrast replacement (`focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2`).
- **Tab Order:** Never use positive `tabIndex` (`tabIndex={1+}`). Use `tabIndex={0}` (natural DOM order) or `-1` (roving tabindex widgets & programmatic focus targets).
- **Overlays & Composite Widgets:** Dialogs/Drawers trap focus while open, close on `Escape`, and restore focus to the invoking trigger on close. Tabs, menus, and listboxes implement arrow-key navigation + Home/End.
- **Touch Target Size:** Interactive targets MUST meet **`>= 24x24px`** (WCAG 2.2 SC `2.5.8` AA) and ideally **`>= 44x44px`** on mobile buttons, checkboxes, and nav items (expand hit area via padding or `::after` if visually compact).
- **Zoom & Orientation:** Never set `user-scalable=no` or `maximum-scale=1` in `<meta name="viewport">`.

## 4. Contrast & Sensory Independence

- **WCAG 2.2 AA Minimums:** `>= 4.5:1` for normal body text; `>= 3.0:1` for large text (`>= 24px` or `>= 18.66px bold`), focus rings, form borders, and active icons. Aim for **AAA (`>= 7.0:1`)** on long-form reading surfaces.
- **APCA Perceptual Targets:** $|L^c| \ge 60$ for body text, $|L^c| \ge 75$ for small dense labels/table cells, $|L^c| \ge 45$ for large headlines & UI icons.
- **Color Independence:** Validation errors, statuses, and chart series must pair color with text, icon, or pattern — never red/green color alone.

## 5. Forms & Live Regions

- Bind every `<input>`, `<select>`, and `<textarea>` with `<label htmlFor="...">` (never rely solely on `placeholder` as a label!).
- Wire inline field errors with `aria-invalid={Boolean(error)}` and `aria-describedby="field-error"`.
- Announce async feedback (saved toast, search result count, validation alert) using `role="status"` (`aria-live="polite"`) or `role="alert"` (`aria-live="assertive"` for blocking failures).
