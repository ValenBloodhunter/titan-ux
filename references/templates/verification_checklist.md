# Frontend Semantic & Visual Verification Checklist

Run deterministic checks (`verify_frontend.py`, `route_graph.py`, `color_contrast.py`) first, then audit every touched UI surface against this semantic checklist:

1. **Aesthetic & Anti-Slop Integrity:**
   - [ ] Clear primary focal point per fold; zero unrequested generic AI gradients or uniform 3-card icon filler.
   - [ ] Authentic domain copy and realistic seed fixtures; zero `Lorem ipsum`, `Acme Corp`, `John Doe`, or `TODO` markers.
   - [ ] Zero hardcoded `#hex` / `rgb()` colors inside component logic; all styling uses semantic theme tokens.
2. **State & Edge-Case Completeness:**
   - [ ] Every async list/chart/form implements **loading** (geometry-matched skeleton), **empty** (contextual CTA), **error** (recoverable retry), and **pending/disabled** states.
   - [ ] Long names, `0` values, negative numbers, missing avatars, and single-item lists do not break layout or overlap text.
3. **Accessibility & Contrast:**
   - [ ] Native `<button>` / `<a href>` semantics, explicit `<label>` bindings, `aria-label` on icon-only buttons, visible `:focus-visible` rings, `Escape` + focus restoration on overlays.
   - [ ] Light and dark token pairs pass WCAG 2.2 AA (`>= 4.5:1` normal text, `>= 3.0:1` UI/large) and APCA checks.
4. **Motion & Responsiveness:**
   - [ ] Interactive UI transitions stay `<= 300ms` using compositor properties only (`transform`, `opacity`, `clip-path`); zero `transition: all` or `width`/`height` layout animations.
   - [ ] `@media (prefers-reduced-motion: reduce)` and/or `<MotionConfig reducedMotion="user">` active.
   - [ ] Verified across `375px`, `768px`, and `1440px` viewports with zero horizontal overflow (`scrollWidth <= innerWidth`).
5. **Performance & Boundaries:**
   - [ ] No sequential server `await` waterfalls; heavy client libs (`three`, charts, editors) dynamically split; `'use client'` pushed to leaf components; explicit dimensions on media (`CLS = 0`).
