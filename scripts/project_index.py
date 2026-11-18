"""Read-only, token-efficient frontend codebase & design-system indexer."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from titan_core import FRONTEND_EXTENSIONS, iter_source_files, resolve_project_root, safe_path


def _detect_package_manager(root: Path) -> str:
    if (root / "pnpm-lock.yaml").is_file():
        return "pnpm"
    if (root / "bun.lockb").is_file() or (root / "bun.lock").is_file():
        return "bun"
    if (root / "yarn.lock").is_file():
        return "yarn"
    if (root / "package-lock.json").is_file():
        return "npm"
    return "none"


def _read_json_safe(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _detect_stack(root: Path, pkg: dict | None, files: list[Path]) -> dict:
    deps = {}
    if pkg:
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    framework = "vanilla-web"
    router = "static"
    if "next" in deps:
        framework = "nextjs-app"
        has_app_dir = any(
            ("/app/" in f.as_posix() or f.as_posix().endswith("/app/page.tsx") or f.as_posix().endswith("/app/layout.tsx"))
            for f in files
        )
        router = "app-router" if has_app_dir or (root / "app").is_dir() or (root / "src/app").is_dir() else "pages-router"
    elif "nuxt" in deps or "vue" in deps:
        framework = "vue-nuxt"
        router = "nuxt-pages" if "nuxt" in deps else "vue-router" if "vue-router" in deps else "spa"
    elif "@sveltejs/kit" in deps or "svelte" in deps:
        framework = "svelte-kit"
        router = "sveltekit" if "@sveltejs/kit" in deps else "spa"
    elif "astro" in deps:
        framework = "astro"
        router = "file-based"
    elif "react" in deps:
        framework = "react-vite"
        if "@tanstack/react-router" in deps:
            router = "tanstack-router"
        elif "react-router" in deps or "react-router-dom" in deps:
            router = "react-router"
        elif "vite" in deps:
            router = "vite-spa"

    tsconfig = _read_json_safe(root / "tsconfig.json")
    ts_strict = bool(tsconfig and tsconfig.get("compilerOptions", {}).get("strict"))
    language = "typescript" if tsconfig or any(f.suffix in {".ts", ".tsx"} for f in files) else "javascript"

    ui_libs = [
        lib
        for lib in [
            "radix-ui",
            "@radix-ui/react-dialog",
            "@base-ui-components/react",
            "react-aria-components",
            "lucide-react",
            "motion",
            "framer-motion",
            "gsap",
            "three",
            "@react-three/fiber",
            "@tanstack/react-query",
            "@tanstack/react-table",
            "swr",
            "zustand",
            "zod",
        ]
        if lib in deps or (lib == "radix-ui" and any(k.startswith("@radix-ui/") for k in deps))
    ]
    if (root / "components.json").is_file():
        ui_libs.append("shadcn-ui")

    tests = [
        t
        for t in ["vitest", "jest", "@playwright/test", "playwright", "@testing-library/react", "axe-core", "@axe-core/playwright"]
        if t in deps
    ]

    return {
        "framework": framework,
        "router": router,
        "language": language,
        "typescript_strict": ts_strict,
        "package_manager": _detect_package_manager(root),
        "scripts": list((pkg or {}).get("scripts", {}).keys()),
        "ui_libraries": sorted(set(ui_libs)),
        "test_tools": sorted(set(tests)),
    }


def _scan_styling_and_tokens(root: Path, pkg: dict | None, files: list[Path]) -> dict:
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})} if pkg else {}
    css_files = [f for f in files if f.suffix.lower() in {".css", ".scss"}]
    tailwind_version = "none"
    if "tailwindcss" in deps:
        raw_ver = str(deps["tailwindcss"])
        tailwind_version = "v4" if raw_ver.lstrip("^~>=").startswith("4") else "v3"
    if any((root / cfg).is_file() for cfg in ["tailwind.config.js", "tailwind.config.ts", "tailwind.config.mjs"]):
        if tailwind_version == "none":
            tailwind_version = "v3"

    token_files: list[str] = []
    css_vars: list[str] = []
    fonts: set[str] = set()
    has_reduced_motion = False
    dark_strategy = "none"

    for css_file in css_files:
        try:
            text = css_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = css_file.relative_to(root).as_posix()
        if '@import "tailwindcss"' in text or "@import 'tailwindcss'" in text or "@theme" in text:
            tailwind_version = "v4"
        found_vars = re.findall(r"(--[a-zA-Z0-9_-]+)\s*:", text)
        if found_vars or "@theme" in text:
            token_files.append(rel)
            for v in found_vars:
                if v not in css_vars:
                    css_vars.append(v)
        if "prefers-reduced-motion" in text:
            has_reduced_motion = True
        if ".dark" in text or '[data-theme="dark"]' in text or "[data-theme='dark']" in text:
            dark_strategy = "class-or-attr"
        elif "prefers-color-scheme: dark" in text and dark_strategy == "none":
            dark_strategy = "media-query"

    for f in files:
        if f.suffix.lower() in {".tsx", ".jsx", ".ts", ".js", ".html", ".astro", ".svelte", ".vue"}:
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in re.findall(r"next/font/google[\"';\s\S]{0,120}?import\s*\{([^}]+)\}", txt):
                for name in m.split(","):
                    if name.strip():
                        fonts.add(name.strip())
            for m in re.findall(r"fonts\.googleapis\.com/css2\?family=([^&\"']+)", txt):
                fonts.add(m.split(":")[0].replace("+", " "))

    return {
        "tailwind_version": tailwind_version,
        "token_files": sorted(set(token_files)),
        "css_variable_count": len(css_vars),
        "css_variables_sample": css_vars[:40],
        "dark_mode_strategy": dark_strategy,
        "has_reduced_motion_guard": has_reduced_motion,
        "detected_fonts": sorted(fonts),
    }


def _scan_components_and_routes(root: Path, files: list[Path]) -> tuple[list[dict], list[str]]:
    components: list[dict] = []
    routes: list[str] = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        name = f.name
        if re.search(r"(?:^|/)(?:app|pages|routes)/.*(?:page|layout|route|\+page|\+layout|index)\.(?:tsx|jsx|ts|js|vue|svelte|astro|html)$", rel):
            routes.append(rel)
        elif rel.endswith(".html"):
            routes.append(rel)

        if f.suffix.lower() in {".tsx", ".jsx", ".vue", ".svelte", ".astro"}:
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            exports = re.findall(r"export\s+(?:default\s+)?(?:async\s+)?(?:function|const|class)\s+([A-Z][A-Za-z0-9_]*)", text)
            is_client = bool(re.match(r"^\s*['\"]use client['\"]", text))
            components.append({
                "file": rel,
                "exports": exports[:10],
                "is_client": is_client,
                "lines": len(text.splitlines()),
            })
    return components, sorted(routes)


def _compute_fingerprint(root: Path, files: list[Path]) -> str:
    h = hashlib.sha256()
    pkg = root / "package.json"
    if pkg.is_file():
        st = pkg.stat()
        h.update(f"pkg:{st.st_mtime_ns}:{st.st_size}".encode())
    for f in files:
        try:
            st = f.stat()
            h.update(f"{f.relative_to(root).as_posix()}:{st.st_mtime_ns}:{st.st_size}".encode())
        except OSError:
            continue
    return h.hexdigest()[:16]


def discover_project(root: Path, *, use_cache: bool = True) -> dict:
    """Build or load cached stack, token, route, and component index for root."""
    files = iter_source_files(root, FRONTEND_EXTENSIONS)
    fingerprint = _compute_fingerprint(root, files)
    cache_path = root / ".titan-ux" / "cache" / "index.json"

    if use_cache and cache_path.is_file():
        cached = _read_json_safe(cache_path)
        if cached and cached.get("fingerprint") == fingerprint:
            return cached

    pkg = _read_json_safe(root / "package.json")
    stack = _detect_stack(root, pkg, files)
    styling = _scan_styling_and_tokens(root, pkg, files)
    components, routes = _scan_components_and_routes(root, files)

    index = {
        "project_root": str(root),
        "fingerprint": fingerprint,
        "file_count": len(files),
        "stack": stack,
        "styling": styling,
        "routes": routes,
        "components": components,
    }
    if use_cache:
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
        except OSError:
            pass
    return index


def extract_lines(root: Path, rel_path: str, line_spec: str = "1-120", symbols_only: bool = False) -> dict:
    """Extract a bounded line range or exported symbols from a project file safely."""
    target = safe_path(root, rel_path)
    if not target.is_file():
        raise FileNotFoundError(f"File not found: {rel_path}")
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    if symbols_only:
        text = "\n".join(lines)
        syms = re.findall(r"^(?:export\s+(?:default\s+)?(?:async\s+)?(?:function|const|type|interface|class)\s+[A-Za-z0-9_]+.*)$", text, re.M)
        return {"file": rel_path, "total_lines": len(lines), "symbols": syms}
    m = re.match(r"^(\d+)(?:-(\d+))?$", line_spec.strip())
    if not m:
        raise ValueError(f"Invalid line range {line_spec!r}; use e.g. 1-120")
    start = max(1, int(m.group(1)))
    end = min(len(lines), int(m.group(2) or start + 80))
    snippet = "\n".join(f"{idx}: {lines[idx - 1]}" for idx in range(start, end + 1))
    return {"file": rel_path, "range": f"{start}-{end}", "total_lines": len(lines), "content": snippet}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=None)
    parser.add_argument("--discover", action="store_true", help="Return stack, styling, routes, and component index")
    parser.add_argument("--fields", help="Comma-separated top-level fields (e.g. stack,styling,routes)")
    parser.add_argument("--extract", help="Relative file path to extract bounded lines or symbols from")
    parser.add_argument("--lines", default="1-120", help="Line range for --extract (default 1-120)")
    parser.add_argument("--symbols", action="store_true", help="Extract exported symbol signatures only")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args(argv)

    try:
        root = resolve_project_root(args.project_root)
        if args.extract:
            out = extract_lines(root, args.extract, args.lines, symbols_only=args.symbols)
            print(json.dumps(out, indent=2))
            return 0
        index = discover_project(root, use_cache=not args.no_cache)
        if args.fields:
            wanted = [f.strip() for f in args.fields.split(",") if f.strip()]
            index = {k: index[k] for k in wanted if k in index}
        print(json.dumps(index, indent=2))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
