# Titan-UX Command Playbooks

Read **only** the section matching the active command plus the resources listed for that command in `SKILL.md` / `route_frontend.py`.

---

## Command A: `/titan-discover [path]` (Read-Only)

**Restrictions:** Strictly read-only. Never modify source files, never install packages, and never load design-authoring, motion, or optimization manuals.

1. **Deterministic Index Scan:** Run `python3 <skill_dir>/scripts/project_index.py "<project_root>" --discover` to capture framework, router, TypeScript setup, styling engine (Tailwind v4 vs v3 vs CSS Modules/vanilla), UI primitives, fonts, design tokens, route map, and test tooling.
2. **Targeted Inspection (If Needed):** For specific files, run `python3 <skill_dir>/scripts/project_index.py "<project_root>" --extract "<rel_path>" --lines 1-120` instead of reading whole repositories into context.
3. **Structured Report:** Present a concise Stack & Design-System Snapshot covering: detected stack, token/theme architecture, component inventory, missing foundations (e.g., no reduced-motion baseline, hardcoded colors, missing error boundary, no tests), and recommended next `/titan-*` command.

---

## Command B: `/titan-architect <feature-or-app>` (End-to-End Blueprint & DAG)

1. **Gate & Route:** Load `references/pre_gen_gate.md`, `references/routing.md`, `references/modules/design-direction.md`, and `references/templates/architect-manifest.md`.
2. **Discover & Route:** Run `project_index.py "<project_root>" --discover` and `route_frontend.py "<feature-or-app>"`.
3. **Design Intelligence Lookup:** Run `python3 <skill_dir>/scripts/design_search.py --surface <surface> --query "<feature-or-app>"` to pick a unified aesthetic archetype, layout composition, palette ID, font pairing, and domain UX rules.
4. **Verify Palette Contrast:** Validate every planned light/dark color pair via `python3 <skill_dir>/scripts/color_contrast.py`.
5. **Lock Manifest & DAG:** Scaffold `.titan-ux/titan-manifest.json` (`scope_locked: true`) via `scripts/scaffold_frontend.py --manifest` defining:
   - Exact ordered file queue (`[1/NN]..[NN/NN]`: tokens $\to$ primitives $\to$ layout shells $\to$ domain widgets $\to$ routes/pages $\to$ tests)
   - Acyclic `component_dag` + RSC/Client boundaries (for Next.js/SSR)
   - Explicit `excluded_features` (prevents scope creep)
   - Required interactive states & verification gates (static + build + browser viewports)
6. **Output Blueprint:** Present the concise Architecture & Design Contract alongside the ready-to-execute `/titan-build` manifest.

---

## Command C: `/titan-tokens <brand-or-style>` (OKLCH Design Token & Theme Engine)

1. **Discover & Gate:** Load `references/pre_gen_gate.md` and `references/modules/tokens-and-css.md`. Run `project_index.py "<project_root>" --discover --fields styling,tokens,fonts`.
2. **Palette & Scale Selection:** Use `design_search.py --palette` (or parse explicit brand hex/OKLCH input) and run `color_contrast.py --generate-ramp` + `--audit-css` so every foreground/surface/border/status pair passes WCAG AA (`>= 4.5:1` text, `>= 3.0:1` UI) and APCA ($|L^c| \ge 60$ body, $\ge 45$ large/UI) in **both** light and dark modes.
3. **Deterministic Generation:** Generate or update the project's canonical token stylesheet (Tailwind v4 `@theme` + `@layer base`, Tailwind v3 CSS variables + config mapping, or pure CSS `:root` + `[data-theme="dark"]` / `.dark`) including fluid `clamp()` typography/spacing ramps, semantic elevation/radius tokens, focus ring tokens, and `prefers-reduced-motion` durations.
4. **Verify:** Run `color_contrast.py --audit-css <tokens_file>` and `verify_frontend.py "<project_root>" --files <tokens_file>` until `0` errors.

---

## Command D: `/titan-build <page-or-feature>` (Exhaustive Non-Stopping Sequential Build)

### Phase 1 — Gate, Route & Scope Lock
1. Load `references/pre_gen_gate.md`, `references/routing.md`, and ONLY the modules returned by `python3 <skill_dir>/scripts/route_frontend.py "<page-or-feature>"`.
2. Run `project_index.py "<project_root>" --discover`. If `.titan-ux/titan-manifest.json` does not exist for this feature, lock one up front (tokens $\to$ shared primitives $\to$ layout $\to$ feature modules $\to$ pages/routes $\to$ tests) and print the complete `[1/NN]–[NN/NN]` queue before coding.

### Phase 2 — Non-Stopping Sequential Write-and-Flush Loop (`k = 1..NN`)
1. Implement each file `1..NN` in dependency order (using `scaffold_frontend.py` when helpful for deterministic boilerplate) and write complete, production-ready code immediately to disk.
2. Retain **only** `{id, path, exports, props_summary}` in active context — never re-read entire completed files unnecessarily.
3. **Strict Completeness Rules:**
   - **Zero stubs:** No `TITAN_DRAFT`, `TODO`, `FIXME`, `Lorem ipsum`, or empty click handlers (`() => {}`).
   - **Token-only styling:** Zero hardcoded hex/rgb literals inside components; use semantic CSS vars / Tailwind theme tokens.
   - **Complete state parity:** Implement `loading` (layout-matched skeleton), `empty` (actionable guidance), `error` (recoverable retry), `disabled`, `focus-visible`, and responsive mobile (`375px`) $\to$ desktop (`1440px`) layouts.
   - **Do not pause mid-batch** or truncate later pages/components.

### Phase 3 — Batch Verification & Build Gate
1. Run `python3 <skill_dir>/scripts/route_graph.py "<project_root>" --check-cycles --broken-links`.
2. Run `python3 <skill_dir>/scripts/verify_frontend.py "<project_root>" --files <created_files> --fix` (or `--manifest`) until `0` errors.
3. Run the project's real typecheck/lint/build/test commands if configured (`tsc --noEmit`, `npm run build`, etc.) and report exact pass/fail status.

---

## Command E: `/titan-polish [target]` (Anti-Slop Critique & Visual Craft Upgrade)

1. Load `references/modules/design-direction.md`, `references/modules/composition-and-ui.md`, and `references/templates/verification_checklist.md`.
2. Run `project_index.py "<project_root>" --discover` and `verify_frontend.py "<project_root>" --files <target_files>` + `design_search.py --anti-slop`.
3. Audit target UI across 7 craft dimensions:
   - **AI-Slop Elimination:** Remove cliché purple-indigo gradients, generic 3-column icon cards, nested card-in-card boxes, fake vanity metrics, and generic filler copy.
   - **Visual Hierarchy & Typography:** Enforce crisp heading-to-body scale contrast, max readable measure (`60ch–72ch` prose), `tabular-nums` on numbers, and intentional alignment.
   - **Domain Copy & Realism:** Replace robotic labels with concise, action-oriented UI copy and authentic domain fixtures.
   - **State Completeness:** Add missing skeleton/empty/error/hover/active/focus-visible states.
   - **Token Discipline:** Replace raw hex/px magic numbers with semantic project tokens.
4. Apply targeted improvements preserving working business logic/APIs, then re-run `verify_frontend.py` until `0` errors.

---

## Command F: `/titan-motion [target]` (Design Engineering Motion & Micro-Interactions)

1. Load `references/modules/motion-engineering.md` and `references/templates/animation_review_template.md`.
2. Run `verify_frontend.py "<project_root>" --files <target_files> --checks motion` to flag layout-thrashing animations (`width`, `height`, `top`, `left`), `transition: all`, sluggish UI durations (`> 300ms`), and missing reduced-motion guards.
3. Upgrade motion using Emil Kowalski design-engineering standards:
   - Animate **only** GPU-composited properties (`transform`, `opacity`, `clip-path`).
   - UI interactions under `300ms` (`150ms–240ms` standard) with crisp `ease-out` / tuned springs; match origin point (`transform-origin`) for dropdowns/popovers/tooltips.
   - Ensure full **interruptibility** (reversing hover/open mid-flight never teleports or locks state).
   - Enforce `@media (prefers-reduced-motion: reduce)` and/or Motion `<MotionConfig reducedMotion="user">`.
4. When reviewing or refactoring existing motion, output the `Before / After / Why` table from `references/templates/animation_review_template.md`, then re-run `verify_frontend.py`.

---

## Command G: `/titan-a11y [target]` (WCAG 2.2 AA/AAA & Web Guidelines Audit/Fix)

1. Load `references/modules/accessibility-wcag.md`.
2. Run `verify_frontend.py "<project_root>" --files <target_files> --checks a11y` and `color_contrast.py --audit-css <css_files>`.
3. Audit and repair:
   - Semantic landmarks (`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`), single `<h1>`, strict heading order.
   - Native interactive controls (`<button>`, `<a href>`) over clickable `<div>`/`<span>`; accessible labels for icon-only controls & form inputs (`<label>`, `aria-describedby` for errors).
   - Keyboard reachability, Escape-to-close + focus restoration for dialogs/drawers/popovers, roving tabindex for tabs/menus, visible `:focus-visible` outlines.
   - Minimum `24x24px` (WCAG 2.2 AA) / `44x44px` preferred touch targets and `>= 4.5:1` (`>= 3.0:1` UI) contrast.
4. Re-run `verify_frontend.py` and `color_contrast.py` until `0` errors.

---

## Command H: `/titan-perf [target]` (React / Next.js / Bundle / CWV Optimization)

1. Load `references/modules/react-nextjs-perf.md` and `references/modules/cwv-seo-resilience.md`.
2. Run `project_index.py "<project_root>" --discover`, `route_graph.py "<project_root>" --check-cycles --rsc-bleed`, and `verify_frontend.py "<project_root>" --files <target_files> --checks perf`.
3. Execute prioritized optimizations:
   - **Critical — Eliminate Waterfalls:** Replace sequential `await` chains with `Promise.all()`, streaming `<Suspense>`, and preload helpers.
   - **Critical — Shrink Client Bundles:** Push `'use client'` down to leaf interactive nodes, eliminate barrel-file re-export pulls, `dynamic()` / `lazy()` split heavy charts/editors/3D canvases.
   - **High — Re-Renders & Lists:** Fix unstable inline object/callback props in hot lists, eliminate array-index `key` on mutable lists, derive state rather than duplicating in `useEffect`.
   - **High — Core Web Vitals (LCP/CLS/INP):** Set explicit dimensions/`aspect-ratio` on media/skeletons, `fetchpriority="high"` on LCP hero media, font `display: swap` + fallback metrics, yield heavy input handlers.
4. Re-run `verify_frontend.py`, `route_graph.py`, and project build/bundle checks if available.

---

## Command I: `/titan-verify [url-or-path]` (End-to-End Static + Build + Browser QA Gate)

1. Load `references/templates/verification_checklist.md` (and `references/modules/browser-qa.md` when testing a running URL or Playwright suite).
2. **Static Gate:** Run `verify_frontend.py "<project_root>" --all` (or `--manifest` / `--files`), `route_graph.py "<project_root>" --check-cycles --broken-links --orphans`, and `color_contrast.py --audit-css` on stylesheets.
3. **Build & Unit Gate:** Execute configured `typecheck`, `lint`, `test`, and `build` commands.
4. **Headless Browser QA (When URL or Dev Server Available):** Run `node <skill_dir>/scripts/browser_audit.mjs "<url>"` across `375x812`, `768x1024`, and `1440x900` viewports (light + dark + reduced-motion) verifying zero console/network errors, zero horizontal overflow, zero broken images, valid keyboard focus, and axe checks.
5. **Honest Reporting:** Report exact command results, exit codes, and remaining warnings/failures. Never mark checks as passing if skipped or unexecuted.

---

## Command J: `/titan-migrate <migration-goal>` (Safe Incremental Upgrade)

1. Load `references/pre_gen_gate.md` plus ONLY the modules matching `<migration-goal>` (e.g., `tokens-and-css.md` for Tailwind v3 $\to$ v4 or hex $\to$ tokens; `composition-and-ui.md` for prop-hell $\to$ compound components).
2. Run `project_index.py "<project_root>" --discover` and `route_graph.py "<project_root>"` to map blast radius before touching files.
3. Lock a scoped migration queue (`[1/NN]..[NN/NN]`), migrate incrementally preserving public component contracts/routes (or updating all call sites verified by `route_graph.py`), and run scoped `verify_frontend.py --files <changed>` + typecheck/build after each wave.

---

## Command K: `/titan-compare <A> vs <B>` (Frontend Architecture & Stack Matrix)

**Restrictions:** Read-only unless user asks to apply the choice.

1. Load `references/templates/comparison_template.md` and run `project_index.py "<project_root>" --discover` to ground the trade-offs in the **actual project's** bundle constraints, SSR/CSR architecture, team stack, and a11y/motion requirements.
2. Compare `<A>` vs `<B>` across: Bundle/Runtime Cost, SSR/RSC Compatibility, Accessibility Out-of-the-Box, Motion/Customization Control, DX/Maintenance, Migration Effort, and Edge Cases.
3. Output the complete Markdown trade-off matrix and a clear contextual recommendation tailored to the current repository.
