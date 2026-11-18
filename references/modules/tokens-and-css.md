# Design Tokens, OKLCH Color Science & Modern CSS

## 1. Semantic Token Contract (Never Raw Palette Literals in Components)

Components must reference **purpose-based semantic tokens**, never hardcoded hex values or raw palette shades (`bg-slate-900`, `text-[#6366f1]`):

- **Surfaces:** `--bg` (canvas), `--surface` (cards/panels), `--surface-elevated` (popovers/modals/active nav), `--surface-sunken` (inputs/wells/code blocks).
- **Text:** `--text` (primary ink), `--text-muted` (secondary labels/metadata), `--text-subtle` (placeholders/disabled), `--accent-fg` (text placed on `--accent`).
- **Borders & Focus:** `--border` (hairlines), `--border-strong` (hover/input bounds), `--ring` (high-contrast focus-visible outline).
- **Brand & Status:** `--accent`, `--accent-hover`, `--success`, `--warning`, `--danger` (plus `*-surface` subtle tinted backgrounds).

## 2. OKLCH Perceptual Color Engineering

Use `oklch(L C H)` (`L` = perceptual lightness `0..1`, `C` = chroma `0..0.37`, `H` = hue `0..360`):
- **Dark Mode Surface Ladder:** Step `L` UP subtly per elevation (`--bg: 0.14`, `--surface: 0.17`, `--surface-elevated: 0.21`) rather than using pure `#000000` canvas or dropping heavy opaque black shadows (which vanish on dark surfaces).
- **Light Mode Surface Ladder:** Keep `--bg` slightly off-pure (`0.985–0.995`) with crisp `--surface` (`1.0`) or subtle warm/cool tint (`--surface-sunken: 0.96`).
- **Contrast Guarantee:** Validate every foreground/background token pair in both light and dark modes via `python3 scripts/color_contrast.py --audit-css <file>` (`>= 4.5:1` text, `>= 3.0:1` UI borders/icons, APCA $|L^c| \ge 60$ body).

## 3. Tailwind CSS v4 vs v3 Token Wiring

### Tailwind v4 (`@import "tailwindcss";`)
```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *, [data-theme="dark"], [data-theme="dark"] *));

@theme inline {
  --color-bg: var(--bg);
  --color-surface: var(--surface);
  --color-surface-elevated: var(--surface-elevated);
  --color-text: var(--text);
  --color-text-muted: var(--text-muted);
  --color-border: var(--border);
  --color-accent: var(--accent);
  --color-accent-fg: var(--accent-fg);
  --font-sans: var(--font-body), ui-sans-serif, system-ui, sans-serif;
  --font-display: var(--font-heading), var(--font-sans);
  --font-mono: var(--font-code), ui-monospace, monospace;
}
```

### Tailwind v3 (`tailwind.config.*`)
Expose semantic CSS variables inside `theme.extend.colors` (`bg: "var(--bg)"`, or `oklch(var(--bg-oklch) / <alpha-value>)`) rather than scattering `dark:` overrides in every JSX tag! Defining light + dark values inside `:root` and `.dark` cuts component class bloat by 50%+.

## 4. Modern CSS Primitives

- **Viewport Height:** Use `min-h-dvh` (`100dvh` with `100vh` fallback) — never bare `100vh`, which clips mobile browser chrome.
- **Fluid Scales:** Use `clamp(min, preferred, max)` for editorial display typography and section spacing rather than abrupt jumps across 4 media queries.
- **Container Queries:** Use `@container` (`@sm:`, `@lg:`) on reusable widgets (cards, KPI tiles, product cards) so they adapt to sidebar vs main-grid placement automatically.
- **Class Merging:** Always provide `cn(...inputs)` (`clsx` + `tailwind-merge`) for component `className` overrides so caller utilities cleanly override defaults.
