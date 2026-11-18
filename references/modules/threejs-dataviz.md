# Three.js / WebGL & Accessible Data Visualization

## 1. Three.js / React Three Fiber Production Discipline

1. **Dynamic Isolation & Zero LCP Blocking:** Load `<Canvas>` via `next/dynamic(..., { ssr: false })` or `React.lazy` inside a bounded `aspect-ratio` container with an instant poster/SVG fallback so SSR and LCP paint cleanly.
2. **GPU & Frame Budget:**
   - Clamp pixel ratio: `dpr={[1, 2]}` (`Math.min(window.devicePixelRatio, 2)`).
   - Use `frameloop="demand"` when the scene is static until user orbit/interaction; pause `requestAnimationFrame` when offscreen (`IntersectionObserver`) or `document.hidden === true`.
   - Prefer instancing (`InstancedMesh`) and compressed assets (`DRACO` / `KTX2`) over hundreds of individual draw calls.
3. **Strict Memory Disposal & Context Loss:** Dispose custom `BufferGeometry`, `Material`, `Texture`, and `WebGLRenderTarget` instances on unmount. Wrap the canvas in an `ErrorBoundary` AND listen to `webglcontextlost` to display an informative static fallback.
4. **Reduced Motion & Keyboard Parity:** Under `prefers-reduced-motion: reduce`, disable auto-rotation/camera flythroughs and render a crisp resting composition. Expose keyboard/button camera presets alongside pointer orbit.

## 2. Accessible Data Visualization (SVG / Charts)

- **Typography & Precision:** Always apply `font-variant-numeric: tabular-nums` on axis ticks, legends, and hover tooltips; format units explicitly (`$14.2k`, `42.5%`).
- **Colorblind-Safe Encoding:** Never encode meaning solely by red vs green! Pair distinct luminance contrast, line dash styles, point markers, or direct data labels.
- **Keyboard & Screen-Reader Parity:** Provide `role="img"` + descriptive `aria-label` summarizing key trends/outliers on `<svg>` charts, keyboard-focusable data points or series toggles, and an accessible summary table (visible or toggleable) for complex charts.
- **Empty & Sparse States:** Explicitly handle `0` data points, single-point series, negative values, and long category labels (truncate with tooltip or rotate cleanly without overlapping ticks).
