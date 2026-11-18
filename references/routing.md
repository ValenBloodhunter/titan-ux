# Pre-Implementation 5-Axis Frontend Routing

To prevent contradictory guidance across integrated design, motion, accessibility, and performance rulebooks, resolve every task across five orthogonal axes **before** generating code or touching files.

## Pass 1: Resolve Command & Scope

1. **Explicit commands lock the operational mode.** `/titan-discover` is strictly read-only; `/titan-tokens` modifies only token/theme files; `/titan-motion` focuses on transitions/physics/reduced-motion; `/titan-a11y` enforces WCAG/APCA compliance; `/titan-perf` focuses on waterfalls/bundles/CWV; `/titan-verify` executes gates without silently rewriting unrelated features.
2. **Respect the existing codebase first.** Run `scripts/project_index.py` before assuming Next.js vs Vite vs Svelte vs Vanilla HTML, or Tailwind v4 vs v3 vs CSS Modules. Never introduce a competing UI library or CSS engine when the project already standardizes on one unless migrating via `/titan-migrate`.

## Pass 2: Classify the 5 Axes Independently

| Axis | Allowed Values | Routing Effect |
|---|---|---|
| **1. Surface Archetype** | `saas-app`, `marketing-editorial`, `docs-content`, `commerce-storefront`, `design-system`, `interactive-canvas` | Sets visual rhythm, copy voice, required states, and layout priorities |
| **2. Stack Profile** | `nextjs-app`, `react-vite`, `vue-nuxt`, `svelte-kit`, `astro`, `vanilla-web` | Determines RSC vs client boundaries, routing primitives, and perf rules |
| **3. Motion Tier** | `0` (Crisp Functional), `1` (Tactile Product Physics), `2` (Editorial / Spatial Choreography) | Resolves the tension between ultra-minimal latency and expressive storytelling |
| **4. Density Mode** | `compact`, `balanced`, `editorial` | Controls padding ladder, type scale ratio (`1.125`–`1.333`), and table/card breathing room |
| **5. Aesthetic Lock** | Named archetype + palette ID + font pairing from `scripts/design_search.py` | Prevents mid-build drift and AI-slop defaults |

## De-Confliction Matrix (How Super-OP Skills Harmonize)

1. **Aesthetics vs. SaaS Utility:**
   - For `marketing-editorial` and `interactive-canvas`, prioritize bold typographic contrast, asymmetric editorial grids, bespoke SVG/canvas craft, and distinct palettes (`frontend-design` + `taste-skill`).
   - For `saas-app` and `design-system`, prioritize scannable information hierarchy, `tabular-nums`, keyboard ergonomics, clean surface elevation ladders, and muted neutral chrome so data — not decorative gradients — owns attention (`impeccable` + `ui-ux-pro-max`).
2. **Motion vs. Core Web Vitals (INP / CLS):**
   - `Motion Tier 0` (`docs-content`, dense tables): instant state switches (`<= 120ms` micro-hover/focus only), zero entrance choreography.
   - `Motion Tier 1` (`saas-app`, `commerce-storefront`, `design-system`): Emil Kowalski product physics (`150ms–260ms`, `ease-out` entrances, `transform-origin` aware popovers, interruptible springs, compositor-only properties `transform`/`opacity`/`clip-path`).
   - `Motion Tier 2` (`marketing-editorial`, `interactive-canvas`): above-the-fold hero renders immediately with **zero** `opacity: 0` blocking LCP! Scroll reveals use IntersectionObserver / GPU transforms and degrade gracefully under `prefers-reduced-motion: reduce`.
3. **Server-First Perf vs. Rich Interactivity:**
   - Under `nextjs-app` (and `astro`/`svelte-kit`), keep layout shells, data fetches, and static chrome on the server; push `'use client'` boundaries strictly to interactive leaf islands (`react-best-practices`).
   - Dynamically import heavy client visualizations (charts, rich-text editors, Three.js canvases) with explicit layout-preserving skeleton dimensions (`CLS = 0`).
4. **Typography Discipline:**
   - Never default to `Inter` + `Space Grotesk` + purple gradient for editorial/brand pages.
   - Use `Inter` / `Geist` / `Plus Jakarta Sans` intentionally ONLY when `compact` SaaS legibility and crisp `tabular-nums` alignment justify them, paired with distinct display or monospace accents when appropriate.

## Compact Internal Routing Plan

```yaml
command: build
surface: saas-app
stack: nextjs-app
motion_tier: 1
density: compact
archetype: linear-precision
palette_id: slate-cobalt-pro
font_pairing: geist-mono-precision
resources:
  - references/modules/design-direction.md
  - references/modules/tokens-and-css.md
  - references/modules/composition-and-ui.md
  - references/modules/accessibility-wcag.md
  - references/modules/react-nextjs-perf.md
  - references/modules/motion-engineering.md
```

Use `python3 scripts/route_frontend.py "<request>"` to generate this plan deterministically and load only the returned `resources`.
