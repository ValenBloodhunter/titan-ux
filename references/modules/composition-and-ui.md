# Component Composition, UI Primitives & State Completeness

Synthesizes Vercel `composition-patterns`, `shadcn/ui`, and headless accessibility primitives (Radix / React Aria / Base UI).

## 1. Kill Boolean-Prop Explosion with Compound Components

**Anti-pattern:** `<DataCard title="..." subtitle="..." showHeader compact bordered hasFooter footerAction={...} icon={...} />`
**Engineered Pattern:** Export composable subparts connected via React Context (or slotted primitives) plus concise variant props:
```tsx
<Card variant="outlined" density="compact">
  <Card.Header>
    <Card.Title>Invoices</Card.Title>
    <Card.Action><Button size="sm">Export</Button></Card.Action>
  </Card.Header>
  <Card.Body>{children}</Card.Body>
</Card>
```
- **Variant Matrices (`cva`):** Constrain discrete variations (`variant`: `primary | secondary | ghost | danger`, `size`: `sm | md | lg`).
- **Slot / `asChild` Forwarding:** Always forward `ref`, accept `...props`, merge `className` via `cn()`, and compose caller event handlers instead of overwriting `onClick`/`onKeyDown`.
- **Dual Controlled / Uncontrolled APIs:** Interactive primitives accept both `value` + `onValueChange` (controlled) and `defaultValue` (uncontrolled) without synchronization bugs.

## 2. Complete Interactive State Matrix (Zero Half-Built Views)

Every asynchronous or interactive UI module MUST implement all applicable states:

| State | Engineering Requirement |
|---|---|
| **Loading** | Geometry-matched skeleton (`animate-pulse` subtle, explicit height/aspect-ratio so `CLS = 0`) or button pending spinner preserving button width (`min-w`) |
| **Empty** | Clear explanation of why nothing is here + ONE contextual primary CTA (e.g., `"Create first API key"` or `"Clear 3 active filters"`) |
| **Error** | Inline recoverable banner/alert (`role="alert"`) preserving user form/filter inputs + explicit `"Retry"` action |
| **Disabled / Pending** | `disabled` or `aria-disabled="true"` + `aria-busy="true"` preventing double-submit races |
| **Optimistic / Feedback** | Immediate visual acknowledgment (`Sonner`/toast with `aria-live="polite"` or inline state) + rollback on server failure |
| **Focus & Active** | Crisp `:focus-visible` ring + tactile `active:scale-[0.98]` feedback (`Motion Tier >= 1`) |

## 3. Production Pattern Standards

- **Forms:** Validate with schema (`zod`/`valibot`) on blur/submit; display inline errors beneath fields wired with `aria-describedby` and `aria-invalid`; focus the first invalid field on failed submit; disable submit only while in-flight (or validate cleanly with error summary so users know why a form didn't submit).
- **Tables & Dense Lists:** Sticky `<thead>`, right-aligned `tabular-nums` numeric columns, `overflow-x-auto` wrapper with subtle scroll shadow on mobile (`375px`), clear row click vs action-button click separation (never nest `<button>` inside `<button>` or `<a>`).
- **Dialogs, Drawers & Popovers:** Use proven headless primitives (`Radix Dialog`, `Base UI`, `React Aria`, or native `<dialog>` with `showModal()`) for focus trapping, scroll lock, `Escape` dismissal, and trigger focus restoration. Never hand-roll `z-50 fixed inset-0` divs without focus management!
- **Destructive Actions:** Require explicit confirmation dialog or undo toast (`"Undo"` within 5s) naming the exact affected resource (`"Delete project titan-api?"`).
