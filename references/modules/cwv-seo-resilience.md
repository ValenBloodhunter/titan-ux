# Core Web Vitals, Media, Fonts, SEO & Resilience

## 1. Core Web Vitals Budgets

- **LCP (Largest Contentful Paint `<= 2.5s`):**
  - Never hide above-the-fold hero text or hero media behind `opacity: 0` JavaScript animation states or client-side spinners! Paint initial HTML immediately.
  - Mark the primary hero `<img>` with `fetchpriority="high"` (`priority` in `next/image`) and explicit `sizes`. Never set `loading="lazy"` on above-the-fold images.
  - Self-host fonts (`next/font` or `@fontsource`) or preload critical WOFF2 subsets.
- **CLS (Cumulative Layout Shift `<= 0.1`):**
  - Always specify `width` + `height` or CSS `aspect-ratio` on images, videos, embeds, charts, and skeletons.
  - Match loading skeleton heights closely to loaded rows/cards so hydration doesn't jump vertically.
  - Use `font-display: swap` paired with metric-compatible fallback fonts (or `next/font` auto size-adjust).
- **INP (Interaction to Next Paint `<= 200ms`):**
  - Wrap expensive filtering/tab-switching state updates in React `startTransition` or debounce heavy queries (`150ms–250ms`).
  - Virtualize lists `> 100` complex rows (`@tanstack/react-virtual`).
  - Use `content-visibility: auto; contain-intrinsic-size: auto 500px;` for long below-the-fold sections.

## 2. Resilience & Failure Boundaries

Every production frontend route/feature must handle failure gracefully:
- **Route Error & Not-Found Boundaries:** Provide `error.tsx` (with reset button), `not-found.tsx` (actionable return link), and widget-level `ErrorBoundary` wrappers around fragile third-party charts/WebGL canvases.
- **Network & Mutation Safety:** Guard against double-submission (`pending` lock), show stale-data warning or retry affordance on failed fetches, and preserve unsaved form input across validation/network errors.

## 3. Technical SEO & Metadata Hygiene

- Include semantic `<title>` (`<= 60` chars), `<meta name="description">` (`120–155` chars), canonical `<link rel="canonical">`, Open Graph (`og:title`, `og:description`, `og:image`, `og:type`), and Twitter metadata on public routes.
- Use `<html lang="en">` (or matching locale), valid `robots.txt` / `sitemap.xml` for marketing/docs/commerce sites, and JSON-LD structured data (`Product`, `Article`, `SoftwareApplication`, `FAQPage`) where relevant.
