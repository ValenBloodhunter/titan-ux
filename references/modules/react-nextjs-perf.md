# React, Next.js & Frontend Runtime Performance

Synthesizes Vercel `react-best-practices` and `next-best-practices` prioritized by real-world user impact.

## Priority 1 — Eliminate Async Waterfalls (CRITICAL)

- **Parallelize Independent Awaits:** Never chain `const a = await fetchA(); const b = await fetchB();` when `b` does not depend on `a`. Use `const [a, b] = await Promise.all([fetchA(), fetchB()])` or start promises early and await at usage site.
- **Granular Streaming (`<Suspense>`):** Wrap independent slow server widgets (analytics chart, activity feed) in dedicated `<Suspense fallback={<WidgetSkeleton />}>` boundaries so the shell & primary content stream immediately.
- **Per-Request Deduplication (`React.cache()`):** Wrap shared server data readers (`getCurrentUser`, `getWorkspace`) with `React.cache()` so layout + nested server components share one fetch per render pass.
- **Defer Await Into Branches:** Check auth/early-return guards before awaiting heavy queries.

## Priority 2 — Bundle Size & Code Splitting (CRITICAL)

- **Avoid Barrel Re-Export Bloat:** Importing `{ IconA } from '@/components'` or huge barrel files can pull dozens of unused client modules. Import directly from source modules or configure `optimizePackageImports` for icon/UI packs.
- **Dynamic Client Islands:** Load heavy client-only widgets (`three`, `@monaco-editor/react`, `recharts`, `echarts`, rich-text editors) lazily via `next/dynamic(..., { ssr: false, loading: () => <Skeleton /> })` or `React.lazy()` + `<Suspense>`.
- **Zero Unused JS on Static Chrome:** Marketing headers, footers, prose sections, and icons do NOT need `'use client'`.

## Priority 3 — Server / Client Boundary Hygiene (HIGH)

- **Push `'use client'` to Leaf Nodes:** Keep layouts, pages, and data-fetching containers as Server Components; extract ONLY interactive inputs/toggles/menus into small `'use client'` leaves.
- **Composition Through Children:** Pass server-rendered `<ServerContent />` as `children` into `<ClientSidebarWrapper>{children}</ClientSidebarWrapper>` instead of marking `<ServerContent />` client-side!
- **Minimal Serialization:** Pass only the primitive fields a client component actually renders rather than huge serialized DB records across the RSC boundary.

## Priority 4 — Client State, Fetching & Re-Render Hygiene (MEDIUM-HIGH)

- **Derive During Render, Never Sync in `useEffect`:** Replace `useState(filtered)` + `useEffect(() => setFiltered(...), [items, query])` with direct computation (or `useMemo` only when genuinely expensive, `> 1000` items).
- **Avoid Object/Fn Churn on Hot Lists:** Never pass unstable inline objects (`style={{ ... }}` or `filters={{ ... }}`) into memoized rows inside virtualized/long lists.
- **Stable List Keys:** NEVER use `key={index}` on dynamic, reorderable, filterable, or editable lists — always use stable unique IDs (`item.id`).
- **Narrow Context Subscriptions:** Split frequently changing state (`ScrollContext` / `InputValueContext`) from stable dispatch/actions context (`ActionsContext`) to prevent whole-tree re-renders on every keystroke or tick.
- **Deduplicated Client Cache:** Prefer TanStack Query / SWR / router loaders with request deduplication and optimistic rollbacks over raw `useEffect` fetch boilerplate; if using raw `fetch` in `useEffect`, ALWAYS pass an `AbortController` cleanup.

## Priority 5 — Hydration & SSR Determinism (HIGH)

- Never branch JSX output on `typeof window !== 'undefined'`, `Date.now()`, `Math.random()`, or `localStorage` during the first render pass.
- For theme switching without FOUC (Flash of Unstyled Content), inject a tiny blocking inline script in `<head>` setting `.dark` / `data-theme` on `<html>` before first paint, paired with `suppressHydrationWarning` on `<html>` only.
