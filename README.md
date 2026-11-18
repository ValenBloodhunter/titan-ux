# Titan-UX

An exhaustive, token-efficient **end-to-end frontend engineering and design skill suite** for all AI coding agents (`Claude Code`, `Codex`, `Antigravity`, `Gemini CLI`, `Cursor`, `Windsurf`, `Cline`, `OpenCode`, `GitHub Copilot`).

Inspired by the progressive-loading, deterministic-CLI architecture of [Scriptorium](https://github.com/AayushPandey2/scriptorium), **Titan-UX** unifies top frontend agent capabilities—aesthetic art direction, searchable design intelligence, anti-slop polish, OKLCH/WCAG/APCA color math, React/Next.js performance, compound UI composition, Emil-grade motion engineering, accessibility audits, Core Web Vitals, and Playwright browser QA—into a single **de-conflicted routing system**.

---

## Why Titan-UX?

Installing five standalone frontend skills simultaneously usually causes two failures:
1. **Context Bloat:** Dumping hundreds of KB of rules into every session crowds out project code.
2. **Rule Collisions:** Editorial aesthetics clash with compact SaaS tables; heavy hero choreography fights LCP/INP; Tailwind v3 patterns break Tailwind v4 `@theme`.

**Titan-UX solves both:**
- **Progressive-Loading Router (`SKILL.md`):** Reads **only** the active command section in [command_playbooks.md](references/command_playbooks.md) and **only** the conditionally needed reference modules.
- **5-Axis De-Confliction (`scripts/route_frontend.py`):** Resolves `command`, `surface` (`saas-app`, `marketing-editorial`, `docs-content`, `commerce-storefront`, `design-system`, `interactive-canvas`), `stack` (`nextjs-app`, `react-vite`, `vue-nuxt`, `svelte-kit`, `astro`, `vanilla-web`), `motion_tier` (`0|1|2`), and `density` (`compact|balanced|editorial`) **before** authoring code.
- **Zero-Dependency Deterministic Tooling (`scripts/`):** Python 3.10+ stdlib CLI tools handle stack/token indexing, OKLCH/WCAG/APCA contrast validation, offline design-intelligence search, locked manifest scaffolding, dependency/route/RSC graph analysis, and scoped static auditing—plus a Playwright headless browser QA script (`scripts/browser_audit.mjs`).

---

## Integrated Frontend Pillars

| Domain Pillar | Integrated Capabilities |
|---|---|
| **Aesthetic Direction & Anti-Slop** | Cohesive visual commitment, spatial hierarchy, domain-authentic copy/seed fixtures, explicit ban-list against generic AI gradients, card-in-card clutter, and `Lorem ipsum` stubs |
| **Offline Design Intelligence** | Searchable JSON registries (`references/data/`) of 10 design archetypes, 13 WCAG-verified light/dark palettes, 12 intentional font pairings, 8 UX workflow patterns, and 12 anti-slop rules |
| **OKLCH Tokens & Contrast Math** | Pure-Python OKLCH $\leftrightarrow$ sRGB conversion, WCAG 2.2 ratio + APCA $L^c$ perceptual contrast auditing, 50–950 scale generation, and automatic lightness repair |
| **React / Next.js Performance** | Waterfall elimination (`Promise.all`, `<Suspense>`, `React.cache()`), bundle splitting (`next/dynamic`), leaf `'use client'` boundaries, re-render hygiene, hydration determinism |
| **Compound UI Composition** | Context-backed compound components replacing boolean-prop explosion, `cva` variants, `cn()` merging, complete `loading`/`empty`/`error`/`pending`/`focus` states |
| **Motion Design Engineering** | Interactive UI timings `<= 300ms`, asymmetric `ease-out` / damped springs, compositor-only (`transform`, `opacity`, `clip-path`), origin-aware popovers, interruptibility, `prefers-reduced-motion` |
| **Accessibility (WCAG 2.2 AA/AAA)** | Semantic landmarks, native buttons/links, icon-button labels, form error wiring (`aria-describedby`), focus rings, touch targets (`>= 24px`/`44px`), zoom safety |
| **Core Web Vitals, 3D & Browser QA** | LCP/CLS/INP budgets, Three.js disposal & WebGL fallbacks, accessible data-viz, and multi-viewport Playwright verification (`375x812`, `768x1024`, `1440x900`) |

---

## Cross-Agent Installation

### Option 1: Universal Installer Script (Recommended)

**macOS / Linux / Git Bash:**
```bash
git clone https://github.com/ValenBloodhunter/titan-ux.git
cd titan-ux
./install.sh all          # Installs globally for all detected coding agents
./install.sh claude       # Or target one: claude | cursor | antigravity | gemini | windsurf | cline | codex | opencode | copilot
./install.sh cursor --project  # Or install locally inside the current repo
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/ValenBloodhunter/titan-ux.git
cd titan-ux
.\install.ps1 -Agent all
.\install.ps1 -Agent antigravity
.\install.ps1 -Agent claude -Project
```

### Option 2: `skills` CLI
```bash
npx skills add ValenBloodhunter/titan-ux
```

### Prerequisites
- **Python 3.10+** (zero third-party `pip` packages required for core scripts and tests)
- **Node.js 18+** & `playwright` (optional, only needed when running live browser QA via `scripts/browser_audit.mjs`)

---

## Commands Reference

| Command | Mode | Purpose |
|---|---|---|
| `/titan-discover [path]` | Read-only | Detect framework, router, TS strictness, Tailwind v3/v4, CSS tokens, fonts, routes & components |
| `/titan-architect <feature>` | Plan | Run design intelligence lookup, verify palette contrast, and lock `.titan-ux/titan-manifest.json` DAG |
| `/titan-tokens <style>` | Write tokens | Generate & contrast-audit OKLCH light/dark semantic CSS / Tailwind v4 `@theme` variables |
| `/titan-build <feature>` | Sequential build | Non-stopping `[1/NN]..[NN/NN]` implementation loop with full UI states and verification gates |
| `/titan-polish [target]` | Refactor | Remove AI-slop aesthetics, raw colors, weak copy, and missing empty/error/loading states |
| `/titan-motion [target]` | Motion & review | Upgrade to `<300ms` GPU-composited transitions, reduced-motion safety, and `Before/After/Why` tables |
| `/titan-a11y [target]` | Audit & fix | Enforce WCAG 2.2 AA/AAA semantics, ARIA, keyboard navigation, focus rings, and contrast |
| `/titan-perf [target]` | Audit & fix | Eliminate async waterfalls, shrink client bundles, fix RSC bleed, and improve LCP/CLS/INP |
| `/titan-verify [url/path]` | QA gate | Run static verifier, cycle/route/RSC graph checks, build checks, and headless Playwright QA |
| `/titan-migrate <goal>` | Refactor | Incrementally migrate Tailwind v3 $\to$ v4, hex $\to$ tokens, or boolean props $\to$ compound APIs |
| `/titan-compare <A> vs <B>` | Read-only | Generate a repository-grounded trade-off matrix for frontend libraries and architectures |

---

## Deterministic CLI Scripts (`scripts/`)

```bash
# 1. Discover project stack, Tailwind version, CSS variables, fonts, routes & components
python3 scripts/project_index.py "<project_root>" --discover

# 2. Extract targeted lines or exported symbols without reading entire files
python3 scripts/project_index.py "<project_root>" --extract "src/components/Button.tsx" --lines 1-60

# 3. Route a frontend request to exact minimal reference modules
python3 scripts/route_frontend.py "/titan-build fintech treasury dashboard" --stack nextjs-app

# 4. Query offline Design Intelligence (archetypes, palettes, font pairings, patterns, anti-slop)
python3 scripts/design_search.py --surface saas-app --query "fintech ledger" --anti-slop

# 5. Evaluate WCAG 2.2 + APCA contrast, suggest OKLCH fixes, or audit CSS token files
python3 scripts/color_contrast.py pair "#0F172A" "#F8FAFC"
python3 scripts/color_contrast.py suggest-fix "#94A3B8" "#FFFFFF" --target 4.5
python3 scripts/color_contrast.py audit-css "src/app/globals.css"

# 6. Scaffold scope-locked manifest, OKLCH token stylesheet, or accessible component skeleton
python3 scripts/scaffold_frontend.py tokens "<project_root>" --palette porcelain-teal-ledger --mode tailwind-v4 --output "src/app/globals.css"

# 7. Analyze dependency cycles, broken imports/routes, orphan components & RSC client bleed
python3 scripts/route_graph.py "<project_root>" --check-cycles --broken-links --rsc-bleed

# 8. Run scoped static verification (anti-slop, a11y, motion, perf, responsive, token contrast)
python3 scripts/verify_frontend.py "<project_root>" --manifest ".titan-ux/titan-manifest.json" --format text

# 9. Run headless Playwright multi-viewport QA (375x812, 768x1024, 1440x900)
node scripts/browser_audit.mjs "http://localhost:3000" --screenshot-dir ".titan-ux/screenshots"
```

---

## Repository Structure

```text
titan-ux/
├── SKILL.md                          # Progressive-loading command & 5-axis router
├── install.sh / install.ps1          # Cross-agent installers (Unix + Windows PowerShell)
├── LICENSE                           # MIT License
├── requirements.txt                  # Zero third-party Python dependencies
├── skills/                           # 11 cross-agent /titan-* wrapper skills
│   ├── titan-discover/SKILL.md
│   ├── titan-architect/SKILL.md
│   ├── titan-tokens/SKILL.md
│   ├── titan-build/SKILL.md
│   ├── titan-polish/SKILL.md
│   ├── titan-motion/SKILL.md
│   ├── titan-a11y/SKILL.md
│   ├── titan-perf/SKILL.md
│   ├── titan-verify/SKILL.md
│   ├── titan-migrate/SKILL.md
│   └── titan-compare/SKILL.md
├── references/
│   ├── command_playbooks.md          # Sectioned Command A–K playbooks
│   ├── pre_gen_gate.md               # 7-step pre-generation resolution & manifest gate
│   ├── routes.json                   # Surface, stack, and command resource contracts
│   ├── routing.md                    # 5-axis routing & multi-skill de-confliction rules
│   ├── modules/                      # 9 conditionally loaded expert rulebooks
│   ├── templates/                    # Manifest, checklist, comparison, motion review templates
│   └── data/                         # Searchable offline Design Intelligence JSON datasets
├── scripts/                          # Deterministic Python + Node CLI helpers
│   ├── titan_core.py
│   ├── project_index.py
│   ├── design_search.py
│   ├── color_contrast.py
│   ├── route_frontend.py
│   ├── scaffold_frontend.py
│   ├── route_graph.py
│   ├── verify_frontend.py
│   └── browser_audit.mjs
└── tests/                            # Zero-dependency unittest & pytest suite
```

---

## Verification & Tests

Run the full automated test suite (requires only Python 3.10+):
```bash
python -m unittest discover -s tests -v
```
Or with `pytest`:
```bash
pytest tests -v
```

## License

Released under the [MIT License](LICENSE).
