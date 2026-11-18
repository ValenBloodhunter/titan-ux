# Frontend Stack & Architecture Comparison Template (`/titan-compare`)

Synthesize trade-offs grounded strictly in the active codebase profile (`project_index.py`) and primary library constraints.

## Format

### 1. Decision Context
- **Active Project Stack:** `<detected framework / styling / bundler>`
- **Primary Constraint:** `<SSR/RSC compatibility | bundle ceiling | a11y target | motion complexity | team maintenance>`

### 2. Side-by-Side Trade-Off Matrix

| Dimension | Option A (`<Name>`) | Option B (`<Name>`) |
|---|---|---|
| **Runtime & Bundle Footprint** | `<exact KB / tree-shaking / zero-runtime vs JS>` | `<...>` |
| **SSR / RSC Compatibility** | `<works in Server Components vs 'use client' boundary>` | `<...>` |
| **Accessibility & Keyboard Parity** | `<built-in WAI-ARIA/focus trap vs manual wiring>` | `<...>` |
| **Motion & Styling Control** | `<Tailwind/CSS tokens/WAAPI vs runtime overhead>` | `<...>` |
| **Migration & Long-Term Risk** | `<lock-in / upgrade path / maintenance>` | `<...>` |

### 3. When Option A Wins vs. When Option B Wins
- **Choose Option A when:** `<concrete conditions>`
- **Choose Option B when:** `<concrete conditions>`

### 4. Recommended Choice for This Repository
State ONE crisp recommendation tied directly to the project's detected stack, listing exact migration/integration impact and failure edge cases to watch.
