# Pre-Generation Resolution Gate (Mandatory Before Writing Code)

Before creating, scaffolding, or refactoring UI files (`/titan-architect`, `/titan-tokens`, `/titan-build`, `/titan-migrate`), execute this 7-step deterministic gate:

1. **Resolve & Contain Project Root:** Validate `<project_root>` canonically. Reject `..` path traversal, absolute escapes, and escaping symlinks via `scripts/titan_core.py`.
2. **Discover Existing Stack & Design System:** Run `python3 <skill_dir>/scripts/project_index.py "<project_root>" --discover` to detect framework, router, language/TS strictness, Tailwind version/config, existing CSS custom properties (`--*`), fonts, icon set, UI primitives, and test runners. Never invent a parallel styling engine when one already exists.
3. **Reuse Existing Primitives & Tokens:** Inspect discovered components (`--fields components,tokens`) and reuse existing Button, Dialog, Form, Table, and `cn()` helpers instead of duplicating near-identical components.
4. **Query Design Intelligence & Lock Aesthetic:** Run `python3 <skill_dir>/scripts/design_search.py` to select a cohesive archetype, font pairing, and palette aligned to the domain (`surface` + `density`), or align cleanly with existing brand tokens discovered in Step 2.
5. **Verify Mathematical Contrast (WCAG + APCA):** Run `python3 <skill_dir>/scripts/color_contrast.py` on all planned surface/text/muted/accent/status token pairs in both light and dark modes (`>= 4.5:1` normal text, `>= 3.0:1` UI borders/large text, or `>= 7.0:1` when AAA requested). Fix failing pairs in OKLCH before writing CSS.
6. **Lock Operational Manifest (`.titan-ux/titan-manifest.json`):** Record `{operation_id, scope_locked: true, surface, stack, motion_tier, density, archetype, palette_id, tokens_file, allowed_files, excluded_features, component_dag}` via `scripts/scaffold_frontend.py --manifest` (or internal plan for single-file edits).
   - Preflight all target paths for collisions before writing; never silently overwrite unrelated user pages.
   - Do not expose manifest metadata inside rendered UI components.
7. **Scoped Verification After Each Wave:** Run `python3 <skill_dir>/scripts/verify_frontend.py "<project_root>" --files <created_or_edited_files>` (or `--manifest`) + `scripts/route_graph.py --check-cycles` + project typecheck/build so unrelated codebase files remain untouched.
