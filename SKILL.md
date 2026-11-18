---
name: titan-ux
description: >-
  Token-efficient, end-to-end frontend engineering & design router for all coding
  agents. Integrates aesthetic direction, design-intelligence palettes/typography,
  OKLCH/WCAG/APCA tokens, React/Next.js performance, compound composition,
  design-engineering motion, accessibility, anti-slop polishing, and browser QA.
  Supports /titan-discover, /titan-architect, /titan-tokens, /titan-build,
  /titan-polish, /titan-motion, /titan-a11y, /titan-perf, /titan-verify,
  /titan-migrate, and /titan-compare.
---

# Titan-UX — Progressive-Loading Frontend Router

Identify the active command or intent first, read **only** its section in `references/command_playbooks.md` plus the conditionally permitted references below, and delegate indexing, design-intelligence lookup, OKLCH/WCAG math, routing, scaffolding, dependency/route graph checks, and static/browser audits to `scripts/`.

## Progressive Loading Policy

| Command / Mode | Load Only | Deterministic Scripts |
|---|---|---|
| `/titan-discover` | `Command A` only (read-only; never load authoring/motion/perf guides) | `project_index.py` |
| `/titan-architect` | `Command B`, `pre_gen_gate.md`, `routing.md`, `design-direction.md`, `architect-manifest.md` | `project_index.py`, `route_frontend.py`, `design_search.py`, `color_contrast.py`, `scaffold_frontend.py` |
| `/titan-tokens` | `Command C`, `pre_gen_gate.md`, `tokens-and-css.md` | `project_index.py`, `design_search.py`, `color_contrast.py`, `scaffold_frontend.py` |
| `/titan-build` | `Command D`, `pre_gen_gate.md`, `routing.md`, plus ONLY route-selected `modules/*.md` | `project_index.py`, `route_frontend.py`, `scaffold_frontend.py`, `route_graph.py`, `verify_frontend.py` |
| `/titan-polish` | `Command E`, `design-direction.md`, `composition-and-ui.md`, `verification_checklist.md` | `project_index.py`, `design_search.py`, `verify_frontend.py` |
| `/titan-motion` | `Command F`, `motion-engineering.md`, `animation_review_template.md` | `project_index.py`, `verify_frontend.py` |
| `/titan-a11y` | `Command G`, `accessibility-wcag.md` | `project_index.py`, `color_contrast.py`, `verify_frontend.py` |
| `/titan-perf` | `Command H`, `react-nextjs-perf.md`, `cwv-seo-resilience.md` | `project_index.py`, `route_graph.py`, `verify_frontend.py` |
| `/titan-verify` | `Command I`, `verification_checklist.md`, `browser-qa.md` (only if browser/URL present) | `verify_frontend.py`, `route_graph.py`, `color_contrast.py`, `browser_audit.mjs` |
| `/titan-migrate` | `Command J`, `pre_gen_gate.md`, target `modules/*.md` only | `project_index.py`, `route_graph.py`, `verify_frontend.py` |
| `/titan-compare` | `Command K`, `comparison_template.md` | `project_index.py` |

## Security & Containment Policy

- **Project Containment:** Resolve `<project_root>` from explicit argument or current working directory. Reject `..` path traversal, absolute overrides escaping `<project_root>`, and symlinks escaping the project root.
- **Non-Destructive Discovery:** Indexing (`project_index.py`) skips `node_modules`, `.next`, `dist`, `build`, `.git`, `.svelte-kit`, `.nuxt`, and `coverage`, and writes caches only inside `<project_root>/.titan-ux/cache/` (or `--cache-dir`).
- **Scoped Verification:** Always validate modified/created files via `--files` or `--manifest` so unrelated legacy files stay byte-for-byte untouched unless explicitly targeted.
- **No Unverified Claims:** Never report passing typechecks, builds, contrast ratios, or browser/visual checks unless actually executed after the final edit.

## Exhaustive Non-Stopping Execution (`/titan-build` & `/titan-architect`)

1. **Lock Design & Scope First:** Before writing UI code for multi-file features or pages, execute the 7-step `references/pre_gen_gate.md` and write `.titan-ux/titan-manifest.json` (`scope_locked: true`) containing `allowed_files`, `excluded_features`, `tokens_contract`, `surface`, `stack`, `motion_tier`, and the acyclic `component_dag`.
2. **Sequential Write-and-Flush (`k = 1..NN`):** Print the complete `[1/NN]–[NN/NN]` manifest up front. Build foundational tokens $\to$ headless/UI primitives $\to$ layout shells $\to$ domain components $\to$ routes/pages $\to$ state/wiring sequentially, writing each file completely to disk and retaining **only** `{id, path, exports, props_summary}` in active context.
3. **Anti-Truncation & Anti-Slop Invariant:** **Never** stop after 2–3 files, leave `// TODO` / `TITAN_DRAFT` / `Lorem ipsum` stubs, hardcode hex colors inside components, invent ungrounded fake stats/metrics, or downgrade later pages into skeletal wrappers. Every component ships complete interactive states (`loading`, `empty`, `error`, `disabled`, `focus-visible`, responsive layout).

## Command Dispatch

Read **only** the matching `## Command ...` section in `references/command_playbooks.md`:
- **`/titan-discover [path]`** $\to$ `Command A` (read-only stack, token, route & component inventory)
- **`/titan-architect <feature-or-app>`** $\to$ `Command B` (design intelligence, OKLCH/WCAG palette lock & acyclic component DAG)
- **`/titan-tokens <brand-or-style>`** $\to$ `Command C` (semantic OKLCH ramps, Tailwind v4 `@theme` / CSS vars & contrast verification)
- **`/titan-build <page-or-feature>`** $\to$ `Command D` (non-stopping sequential `1..NN` build + scoped verification)
- **`/titan-polish [target]`** $\to$ `Command E` (anti-slop critique, typography/hierarchy/copy/state craft upgrade)
- **`/titan-motion [target]`** $\to$ `Command F` (Emil-grade `<300ms` compositor motion, springs, gestures & `Before/After/Why` review)
- **`/titan-a11y [target]`** $\to$ `Command G` (WCAG 2.2 AA/AAA, APCA contrast, semantic landmarks & keyboard audit/fix)
- **`/titan-perf [target]`** $\to$ `Command H` (waterfall elimination, RSC boundaries, bundle splitting, re-renders & CWV)
- **`/titan-verify [url-or-path]`** $\to$ `Command I` (static audit + route graph + build + headless Playwright multi-viewport QA)
- **`/titan-migrate <migration>`** $\to$ `Command J` (incremental Tailwind/token/compound-component migration)
- **`/titan-compare <A> vs <B>`** $\to$ `Command K` (codebase-grounded frontend architecture & library trade-off matrix)

## Per-Task 5-Axis Routing Before Implementation

When handling free-form requests (e.g., *"Build a fintech dashboard"* or *"Fix layout jank on mobile"*), run `python3 scripts/route_frontend.py "<request>"` (or inspect `references/routing.md` + `references/routes.json`) to resolve **Surface Archetype**, **Stack Profile**, **Motion Tier (`0|1|2`)**, **Density (`compact|balanced|editorial`)**, and the minimal set of reference modules **before** authoring code. This de-conflicts competing rules across aesthetics, performance, and motion automatically.
