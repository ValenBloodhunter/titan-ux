# Aesthetic Direction, Anti-Slop & Visual Craft

Synthesizes Anthropic `frontend-design`, `impeccable`, and `taste-skill` into deterministic aesthetic commitments.

## 1. Commit to a Cohesive Design Direction Before Coding

Before emitting JSX/CSS, resolve these four questions via `scripts/design_search.py`:
1. **Mental Model & Tone:** Is the user operating a high-frequency workspace (`compact`, high scan density), reading technical docs (`balanced`, crisp hierarchy), or experiencing a brand/product narrative (`editorial`, generous negative space)?
2. **Primary Focal Point Per Fold:** Every screen/section has ONE unmistakable primary action or narrative focal point. Secondary actions step down visually (ghost/outline/muted).
3. **Elevation & Border Philosophy:** Pick ONE coherent surface grammar:
   - *Crisp Hairline (Linear/Vercel style):* Subtle `1px` semantic `--border` + minimal tonal surface step (`--bg` $\to$ `--surface` $\to$ `--surface-elevated`), zero heavy shadows.
   - *Tactile Editorial:* Generous padding, high typographic contrast, asymmetric 12-column grids, warm paper/stone or deep ink surfaces.
   - *Soft Layered:* Subtle multi-stop shadows (`0 1px 2px`, `0 8px 24px -8px`) paired with crisp inner borders (`1px solid var(--border)`).
4. **Copy & Seed Data Authenticity:** Write concise, domain-authentic copy and realistic fixture values (real names, believable currency/timestamps/statuses). **Ban** `Lorem ipsum`, `Acme Corp`, `John Doe`, `Test Item 1`, and marketing buzzword fluff (`"Revolutionize your workflow with AI-powered synergy"`).

## 2. Hard Anti-Slop Ban-List

| Anti-Slop Pattern | Why It Fails | Engineered Replacement |
|---|---|---|
| Unrequested purple/indigo-to-cyan gradients on `#0f172a` | Instantly signals generic AI template output | Commit to an industry-grounded OKLCH palette from `palettes.json` with intentional neutral hierarchy |
| Uniform 3-column icon-in-circle feature cards | Zero visual pacing; looks identical across every prompt | Use asymmetric 2-column / bento density or interactive split previews with concrete proof |
| Card-inside-card-inside-card nesting | Clutters hierarchy and wastes horizontal mobile space | Use whitespace, hairline dividers, and at most 2 elevation levels (`surface` + `surface-elevated`) |
| Hardcoded `#hex` / `rgb()` in component JSX/CSS | Breaks dark mode, theming, and contrast guarantees | Bind strictly to semantic tokens (`bg-surface`, `text-muted`, `border-border`, `var(--accent)`) |
| Unbounded prose lines (`> 85ch`) | Strains eye tracking across wide monitors | Constrain readable prose to `max-w-[65ch]` (`60ch–72ch`) |
| Misaligned tables/KPI numbers | Jittering columns hurt financial/metric scanning | Apply `font-variant-numeric: tabular-nums` (`tabular-nums`) on all numbers, timers, and tables |
| Fake vanity stats (`99.99% uptime`, `10M+ users`) | Erodes trust when fabricated | Show real schema-driven fields, empty states, or clearly labeled sample fixtures |

## 3. Spatial Rhythm & Responsive Geometry

- **4px / 8px Spacing Ladder:** Use consistent scale steps (`4, 8, 12, 16, 24, 32, 48, 64, 96px`). Never invent arbitrary `13px`, `27px`, or `37px` gaps.
- **Mobile-First Breakpoints:** Validate geometry at `375px` (single column, touch-safe `44px` tap targets, zero horizontal scroll), `768px` (collapsible rail / 2-col grid), and `1440px` (max container `1280px–1440px` for marketing, fluid split shell for apps).
- **Typographic Scale Ratio:** Use `1.125–1.200` for `compact` dashboards (`13px–14px` body, `20px–24px` panel titles), `1.250–1.333` for `editorial` pages (bold display headlines with tight `-0.025em` tracking + `1.05–1.15` line-height).
