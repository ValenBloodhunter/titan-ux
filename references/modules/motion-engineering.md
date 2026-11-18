# Motion Design Engineering & Micro-Interactions

Synthesizes `emilkowalski/skills` (`animate`, `emil-design-eng`, `review-animations`, `gestures`) for crisp, tactile, zero-jank UI motion.

## 1. Non-Negotiable Physics & Timing Rules

1. **Speed Threshold (`<= 300ms` UI Transitions):** Everyday UI interactions (buttons, tooltips, dropdowns, tabs, modals, toasts) MUST complete within **`120ms–260ms`**. Exit transitions should be ~20–30% faster than entrances (`120ms–160ms`). Only dramatic `Motion Tier 2` editorial hero choreography may exceed `300ms` (capped around `450ms–600ms`).
2. **Asymmetric Easing:**
   - **Entrances & Popovers:** Strong `ease-out` (`cubic-bezier(0.16, 1, 0.3, 1)` or `cubic-bezier(0.22, 1, 0.36, 1)`) so UI feels instantly responsive at frame 1 and settles smoothly.
   - **On-Screen Moves / Morphs (Tabs, Drawers):** Crisp `ease-in-out` (`cubic-bezier(0.4, 0, 0.2, 1)`) or critically damped springs (`stiffness: 420, damping: 32, mass: 0.8`). Never bouncy/wobbly springs on productivity UI!
3. **Subtle Entrance Scale:** Popovers, context menus, and dialogs animate from `scale(0.96) translateY(-4px)` + `opacity: 0` $\to$ `scale(1) translateY(0)` + `opacity: 1`. NEVER zoom elements from `scale(0)`.
4. **Origin-Aware Motion:** Dropdowns and tooltips MUST expand from their trigger anchor (`transform-origin: var(--radix-popover-content-transform-origin)` or explicit `top left` / `top right`), never from center when anchored to a corner button.

## 2. GPU Compositor-Only Discipline

- **Animate ONLY:** `transform` (`translate3d`, `scale`, `rotate`), `opacity`, `clip-path`, and sparingly `filter`.
- **NEVER Animate Layout Properties:** `width`, `height`, `top`, `left`, `right`, `bottom`, `margin`, `padding`, `border-width`, or `font-size`.
  - *Accordion height trick:* Use CSS `display: grid; grid-template-rows: 0fr -> 1fr; transition: grid-template-rows 220ms var(--ease-out);` with inner `overflow: hidden`!
  - *Tab indicator glide:* Animate a shared pill via `transform: translateX(...) scaleX(...)` or Motion `layoutId` inside a `LayoutGroup`!
- **Ban `transition: all` / `transition-all`:** Explicitly declare transitions (`transition-[transform,opacity,background-color,border-color] duration-150 ease-out`) so layout/font changes never animate accidentally.

## 3. Interruptibility & Tactile Press States

- Hovering out or closing mid-animation MUST reverse cleanly from the current interpolated frame — never lock clicks with `pointer-events: none` during active controls or replay canned keyframe resets.
- Tactile buttons use `transition-transform duration-120 ease-out active:scale-[0.97]` so clicks feel physical without feeling sluggish.
- Drag/swipe drawers (mobile sheets) must project velocity (`velocity > threshold` dismisses smoothly; partial drag springs back) rather than rigid click-only toggles.

## 4. Mandatory `prefers-reduced-motion` Gate

Every CSS stylesheet and Motion/GSAP layer MUST degrade safely:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
For React/Motion, wrap the app root in `<MotionConfig reducedMotion="user">` so spatial translations simplify into instant or minimal opacity fades automatically.
