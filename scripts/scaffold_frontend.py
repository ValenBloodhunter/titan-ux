"""Deterministic manifest, OKLCH design-token, and accessible component scaffolder."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from color_contrast import parse_color, rgb_to_oklch
from design_search import _load_dataset
from titan_core import resolve_project_root, routes, safe_path, save_manifest


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "feature"


def _hex_to_oklch_css(hex_val: str) -> str:
    r, g, b = parse_color(hex_val)
    L, C, H = rgb_to_oklch(r, g, b)
    return f"oklch({L:.3f} {C:.4f} {H:.1f})"


def render_tokens_css(palette_id: str, *, mode: str = "tailwind-v4") -> str:
    """Render semantic light/dark OKLCH CSS tokens + motion/a11y baseline."""
    palettes = _load_dataset("palettes")
    match = next((p for p in palettes if p["id"] == palette_id), None)
    if not match:
        raise ValueError(f"Unknown palette {palette_id!r}. Available: {', '.join(p['id'] for p in palettes)}")

    def block_lines(values: dict[str, str]) -> list[str]:
        lines = []
        for token, hex_val in values.items():
            ok = _hex_to_oklch_css(hex_val)
            lines.append(f"  --{token}: {ok}; /* {hex_val} */")
        return lines

    light_vars = "\n".join(block_lines(match["light"]))
    dark_vars = "\n".join(block_lines(match["dark"]))

    header = ""
    theme_bridge = ""
    if mode == "tailwind-v4":
        header = (
            '@import "tailwindcss";\n'
            '@custom-variant dark (&:where(.dark, .dark *, [data-theme="dark"], [data-theme="dark"] *));\n\n'
        )
        theme_bridge = """
@theme inline {
  --color-bg: var(--bg);
  --color-surface: var(--surface);
  --color-surface-elevated: var(--surface-elevated);
  --color-border: var(--border);
  --color-text: var(--text);
  --color-text-muted: var(--text-muted);
  --color-accent: var(--accent);
  --color-accent-fg: var(--accent-fg);
  --color-success: var(--success);
  --color-warning: var(--warning);
  --color-danger: var(--danger);
  --color-ring: var(--ring);
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
}
"""

    return f"""{header}/* Titan-UX Design Tokens — Palette: {match['name']} ({match['id']}) */
:root {{
{light_vars}
  --ring: var(--accent);
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --text-display: clamp(2rem, 1.4rem + 2.4vw, 3.5rem);
  --text-heading: clamp(1.375rem, 1.15rem + 0.9vw, 2rem);
  --space-section: clamp(3rem, 2rem + 4vw, 6.5rem);
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --duration-fast: 140ms;
  --duration-base: 220ms;
}}

.dark,
[data-theme="dark"] {{
{dark_vars}
  --ring: var(--accent);
}}
{theme_bridge}
@layer base {{
  html {{
    background-color: var(--bg);
    color: var(--text);
    color-scheme: light dark;
  }}

  :focus-visible {{
    outline: 2px solid var(--ring);
    outline-offset: 2px;
  }}
}}

@media (prefers-reduced-motion: reduce) {{
  *,
  *::before,
  *::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }}
}}
"""


def render_component_skeleton(name: str, *, stack: str = "nextjs-app", client: bool = False) -> str:
    """Render a framework-aware accessible component skeleton marked with TITAN_DRAFT."""
    clean = re.sub(r"[^A-Za-z0-9]", "", name) or "FeaturePanel"
    if stack in {"nextjs-app", "react-vite"}:
        directive = "'use client';\n\n" if client else ""
        return f"""{directive}/* TITAN_DRAFT: Replace placeholder structure and domain copy before shipping. */
import * as React from "react";

export interface {clean}Props {{
  title: string;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  children?: React.ReactNode;
}}

export function {clean}({{
  title,
  isLoading = false,
  error = null,
  onRetry,
  children,
}}: {clean}Props) {{
  if (isLoading) {{
    return (
      <section
        aria-busy="true"
        aria-label={{title}}
        className="rounded-lg border border-border bg-surface p-6"
      >
        <div className="h-5 w-40 animate-pulse rounded bg-surface-elevated" />
        <div className="mt-4 h-24 w-full animate-pulse rounded bg-surface-elevated" />
      </section>
    );
  }}

  if (error) {{
    return (
      <section
        role="alert"
        className="rounded-lg border border-danger/40 bg-surface p-6 text-text"
      >
        <h2 className="text-base font-semibold">{clean} unavailable</h2>
        <p className="mt-1 text-sm text-text-muted">{{error}}</p>
        {{onRetry ? (
          <button
            type="button"
            onClick={{onRetry}}
            className="mt-4 inline-flex min-h-10 items-center rounded-md bg-accent px-4 text-sm font-medium text-accent-fg transition-transform duration-150 ease-out active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Retry
          </button>
        ) : null}}
      </section>
    );
  }}

  return (
    <section className="rounded-lg border border-border bg-surface p-6 text-text">
      <h2 className="text-lg font-semibold tracking-tight">{{title}}</h2>
      <div className="mt-4">{{children}}</div>
    </section>
  );
}}
"""
    if stack == "vue-nuxt":
        return f"""<!-- TITAN_DRAFT: Replace placeholder structure and domain copy before shipping. -->
<script setup lang="ts">
defineProps<{{ title: string; isLoading?: boolean; error?: string | null }}>();
</script>

<template>
  <section class="rounded-lg border border-border bg-surface p-6 text-text">
    <h2 class="text-lg font-semibold">{{{{ title }}}}</h2>
    <p v-if="error" role="alert" class="mt-2 text-sm text-danger">{{{{ error }}}}</p>
    <div v-else class="mt-4"><slot /></div>
  </section>
</template>
"""
    if stack == "svelte-kit":
        return f"""<!-- TITAN_DRAFT: Replace placeholder structure and domain copy before shipping. -->
<script lang="ts">
  export let title: string;
  export let error: string | null = null;
</script>

<section class="rounded-lg border border-border bg-surface p-6 text-text">
  <h2 class="text-lg font-semibold">{{title}}</h2>
  {{#if error}}
    <p role="alert" class="mt-2 text-sm text-danger">{{error}}</p>
  {{:else}}
    <div class="mt-4"><slot /></div>
  {{/if}}
</section>
"""
    return f"""<!-- TITAN_DRAFT: Replace placeholder structure and domain copy before shipping. -->
<section class="titan-panel" aria-labelledby="{_slugify(clean)}-heading">
  <h2 id="{_slugify(clean)}-heading">{clean}</h2>
  <div class="titan-panel-body"></div>
</section>
"""


def create_manifest(
    root: Path,
    *,
    feature_name: str,
    surface: str,
    stack: str,
    palette_id: str,
    font_pairing: str,
    tokens_file: str,
    allowed_files: list[str],
    excluded_features: list[str],
    motion_tier: int,
    density: str,
) -> dict:
    """Construct and validate a scope-locked Titan-UX operational manifest."""
    for rel in [tokens_file, *allowed_files]:
        safe_path(root, rel)

    dag = []
    prev_id = None
    for idx, rel in enumerate(allowed_files, 1):
        node_id = f"node-{idx:02d}-{_slugify(Path(rel).stem)}"
        dag.append({
            "id": node_id,
            "path": rel.replace("\\", "/"),
            "depends_on": [prev_id] if prev_id else [],
            "required_states": routes()["surfaces"][surface]["required_states"],
        })
        prev_id = node_id

    return {
        "operation_id": f"op-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{_slugify(feature_name)}",
        "scope_locked": True,
        "feature_name": feature_name,
        "surface": surface,
        "stack": stack,
        "motion_tier": motion_tier,
        "density": density,
        "palette_id": palette_id,
        "font_pairing": font_pairing,
        "tokens_file": tokens_file.replace("\\", "/"),
        "allowed_files": [f.replace("\\", "/") for f in allowed_files],
        "excluded_features": excluded_features,
        "component_dag": dag,
    }


def _write_output(path: Path, content: str, *, dry_run: bool, overwrite: bool) -> dict:
    if path.exists() and not overwrite and not dry_run:
        raise FileExistsError(f"Refusing to overwrite existing file without --overwrite: {path}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return {"path": str(path), "dry_run": dry_run, "bytes": len(content.encode("utf-8"))}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_man = sub.add_parser("manifest", help="Create .titan-ux/titan-manifest.json")
    p_man.add_argument("project_root")
    p_man.add_argument("--feature", required=True)
    p_man.add_argument("--surface", default="saas-app", choices=list(routes()["surfaces"]))
    p_man.add_argument("--stack", default="nextjs-app", choices=list(routes()["stacks"]))
    p_man.add_argument("--palette", default="obsidian-cobalt")
    p_man.add_argument("--fonts", default="geist-mono-precision")
    p_man.add_argument("--tokens-file", default="src/app/globals.css")
    p_man.add_argument("--files", nargs="+", required=True)
    p_man.add_argument("--exclude", nargs="*", default=[])
    p_man.add_argument("--motion-tier", type=int, choices=[0, 1, 2], default=1)
    p_man.add_argument("--density", choices=["compact", "balanced", "editorial"], default="compact")
    p_man.add_argument("--dry-run", action="store_true")

    p_tok = sub.add_parser("tokens", help="Generate semantic OKLCH light/dark stylesheet")
    p_tok.add_argument("project_root")
    p_tok.add_argument("--palette", default="obsidian-cobalt")
    p_tok.add_argument("--mode", choices=["tailwind-v4", "tailwind-v3", "css"], default="tailwind-v4")
    p_tok.add_argument("--output", default="src/app/globals.css")
    p_tok.add_argument("--overwrite", action="store_true")
    p_tok.add_argument("--dry-run", action="store_true")

    p_comp = sub.add_parser("component", help="Scaffold a framework-aware accessible component")
    p_comp.add_argument("project_root")
    p_comp.add_argument("--name", required=True)
    p_comp.add_argument("--output", required=True)
    p_comp.add_argument("--stack", default="nextjs-app", choices=list(routes()["stacks"]))
    p_comp.add_argument("--client", action="store_true")
    p_comp.add_argument("--overwrite", action="store_true")
    p_comp.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    try:
        root = resolve_project_root(args.project_root)
        if args.cmd == "manifest":
            manifest = create_manifest(
                root,
                feature_name=args.feature,
                surface=args.surface,
                stack=args.stack,
                palette_id=args.palette,
                font_pairing=args.fonts,
                tokens_file=args.tokens_file,
                allowed_files=args.files,
                excluded_features=args.exclude,
                motion_tier=args.motion_tier,
                density=args.density,
            )
            if not args.dry_run:
                out_path = save_manifest(root, manifest)
                manifest["manifest_path"] = str(out_path)
            print(json.dumps(manifest, indent=2))
            return 0
        if args.cmd == "tokens":
            target = safe_path(root, args.output)
            css = render_tokens_css(args.palette, mode=args.mode)
            res = _write_output(target, css, dry_run=args.dry_run, overwrite=args.overwrite)
            if args.dry_run:
                res["preview"] = css
            print(json.dumps(res, indent=2))
            return 0
        if args.cmd == "component":
            target = safe_path(root, args.output)
            code = render_component_skeleton(args.name, stack=args.stack, client=args.client)
            res = _write_output(target, code, dry_run=args.dry_run, overwrite=args.overwrite)
            if args.dry_run:
                res["preview"] = code
            print(json.dumps(res, indent=2))
            return 0
    except (ValueError, FileExistsError, OSError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
