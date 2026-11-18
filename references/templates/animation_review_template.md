# Motion & Animation Review Rubric (`/titan-motion`)

Evaluate every transition, spring, keyframe, and gesture against Emil Kowalski's design-engineering baseline and output concrete code fixes in this exact format:

## 10-Point Motion Audit Criteria
1. Duration `<= 300ms` for interactive UI controls (exits faster than entrances).
2. Asymmetric `ease-out` for entrances; `ease-in-out` or critically damped spring for on-screen moves.
3. GPU compositor-only properties (`transform`, `opacity`, `clip-path`) — zero layout property animations (`width`, `height`, `top`, `left`, `margin`, `padding`).
4. Zero `transition: all` / `transition-all`.
5. Subtle entrance scale (`>= 0.94`, never `scale(0)`).
6. Origin-aware transforms (`transform-origin` anchored to trigger).
7. Fully interruptible mid-flight (hover/open reversals never reset or lock clicks).
8. Tactile active press feedback (`scale(0.97)`) on primary controls where appropriate.
9. Zero `opacity: 0` blocking above-the-fold LCP paint.
10. Complete `prefers-reduced-motion` degradation (`@media` and/or `<MotionConfig reducedMotion="user">`).

## Required Diff Review Table

| Component / Selector | Before (Problem) | After (Engineered Fix) | Why It Improves Feel & Perf |
|---|---|---|---|
| `<ExampleDropdown>` | `transition-all duration-500 scale-0` | `transition-[transform,opacity] duration-180 ease-out origin-top-right data-[state=closed]:scale-95` | Cuts sluggish 500ms delay, eliminates layout repaint risk, anchors scale to trigger |
