"""Read-only frontend import DAG, cycle, broken-link, orphan, and RSC boundary analyzer."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from titan_core import FRONTEND_EXTENSIONS, iter_source_files, resolve_project_root

CODE_EXTS = {".tsx", ".jsx", ".ts", ".js", ".mts", ".mjs"}
RESOLVE_CANDIDATES = ("", ".tsx", ".ts", ".jsx", ".js", ".mts", ".mjs", ".css",
                      "/index.tsx", "/index.ts", "/index.jsx", "/index.js")

SERVER_ONLY_MODULES = {"fs", "fs/promises", "path", "child_process", "server-only", "next/headers", "next/cookies"}


def _load_ts_alias_prefixes(root: Path) -> dict[str, list[str]]:
    tsconfig = root / "tsconfig.json"
    if not tsconfig.is_file():
        return {"@/": ["src/", ""]}
    try:
        raw = re.sub(r"//.*|/\*[\s\S]*?\*/", "", tsconfig.read_text(encoding="utf-8"))
        data = json.loads(raw)
        paths = data.get("compilerOptions", {}).get("paths", {})
        mapping: dict[str, list[str]] = {}
        for k, targets in paths.items():
            prefix = k.rstrip("*")
            mapping[prefix] = [t.rstrip("*").lstrip("./") for t in targets]
        return mapping or {"@/": ["src/", ""]}
    except (OSError, json.JSONDecodeError):
        return {"@/": ["src/", ""]}


def _resolve_import(root: Path, src_file: Path, spec: str, aliases: dict[str, list[str]]) -> Path | None:
    if spec.startswith(("http://", "https://", "data:")):
        return None
    base_candidates: list[Path] = []
    if spec.startswith("."):
        base_candidates.append((src_file.parent / spec).resolve())
    else:
        matched_alias = False
        for prefix, targets in aliases.items():
            if spec.startswith(prefix):
                matched_alias = True
                rest = spec[len(prefix):]
                for t in targets:
                    base_candidates.append((root / t / rest).resolve())
        if not matched_alias:
            return None

    root_resolved = root.resolve()
    for base in base_candidates:
        for suffix in RESOLVE_CANDIDATES:
            cand = Path(str(base) + suffix)
            if cand.is_file() and cand.resolve().is_relative_to(root_resolved):
                return cand.resolve()
    return Path("__BROKEN__:" + spec)


def _known_routes(root: Path, files: list[Path]) -> tuple[set[str], bool]:
    routes_set = {"/"}
    found_route_files = False
    for f in files:
        rel = f.relative_to(root).as_posix()
        # Next.js App Router: app/**/page.tsx or src/app/**/page.tsx
        m_app = re.match(r"^(?:src/)?app/(.*/)?page\.(?:tsx|jsx|ts|js)$", rel)
        if m_app:
            found_route_files = True
            seg = "/" + (m_app.group(1) or "").strip("/")
            # Strip route groups like (marketing)
            seg = re.sub(r"/\([^/)]+\)", "", seg) or "/"
            routes_set.add(seg)
        # Next.js Pages Router / Astro pages
        m_pages = re.match(r"^(?:src/)?pages/(.*)\.(?:tsx|jsx|ts|js|astro)$", rel)
        if m_pages:
            found_route_files = True
            sub = m_pages.group(1)
            if not sub.startswith("_") and not sub.startswith("api/"):
                sub = re.sub(r"(?:^|/)index$", "", sub)
                routes_set.add("/" + sub.strip("/"))
        if rel.endswith(".html"):
            found_route_files = True
            routes_set.add("/" + rel)
    return routes_set, found_route_files


def _route_matches(href: str, known: set[str]) -> bool:
    clean = href.split("#", 1)[0].split("?", 1)[0].rstrip("/") or "/"
    if clean in known:
        return True
    for r in known:
        if "[" in r:
            pattern = "^" + re.sub(r"\[[^\]]+\]", r"[^/]+", re.escape(r).replace(r"\[", "[").replace(r"\]", "]")) + "$"
            if re.match(pattern, clean):
                return True
    return False


def analyze_graph(root: Path) -> dict:
    """Build dependency graph and detect cycles, broken imports/routes, orphans, and RSC bleed."""
    root = root.resolve()
    files = iter_source_files(root, FRONTEND_EXTENSIONS)
    aliases = _load_ts_alias_prefixes(root)
    known_routes, has_route_files = _known_routes(root, files)

    adj: dict[str, list[str]] = {}
    in_degree: dict[str, int] = {}
    client_flags: dict[str, bool] = {}
    broken_imports: list[dict] = []
    broken_routes: list[dict] = []
    rsc_bleeds: list[dict] = []

    rel_map = {f.resolve(): f.relative_to(root).as_posix() for f in files}
    for rel in rel_map.values():
        adj[rel] = []
        in_degree[rel] = 0

    import_re = re.compile(r"""(?:import|export)\s+(?:[\s\S]*?\s+from\s+)?['"]([^'"]+)['"]|import\(\s*['"]([^'"]+)['"]\s*\)""")
    link_re = re.compile(r"""<(?:Link|a)\b[^>]*\bhref\s*=\s*['"](/[^'"{}*]*)['"]""")

    for f in files:
        rel = rel_map[f.resolve()]
        if f.suffix.lower() not in CODE_EXTS:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        is_client = bool(re.match(r"^\s*['\"]use client['\"]", text))
        client_flags[rel] = is_client

        for m in import_re.finditer(text):
            spec = m.group(1) or m.group(2)
            if not spec:
                continue
            if is_client and (spec in SERVER_ONLY_MODULES or spec.startswith("node:")):
                rsc_bleeds.append({"file": rel, "import": spec, "issue": "Server-only module imported in 'use client' file"})
            resolved = _resolve_import(root, f, spec, aliases)
            if resolved is None:
                continue
            if str(resolved).startswith("__BROKEN__:"):
                broken_imports.append({"file": rel, "import": spec})
            elif resolved in rel_map:
                target_rel = rel_map[resolved]
                if target_rel not in adj[rel]:
                    adj[rel].append(target_rel)
                    in_degree[target_rel] = in_degree.get(target_rel, 0) + 1

        if has_route_files:
            for lm in link_re.finditer(text):
                href = lm.group(1)
                if href.startswith("/api/") or "." in Path(href).name:
                    continue
                if not _route_matches(href, known_routes):
                    broken_routes.append({"file": rel, "href": href})

    # Cycle detection (DFS)
    cycles: list[list[str]] = []
    state: dict[str, int] = {}  # 0=unvisited, 1=visiting, 2=done
    path_stack: list[str] = []

    def dfs(node: str):
        state[node] = 1
        path_stack.append(node)
        for nxt in adj.get(node, []):
            st = state.get(nxt, 0)
            if st == 1:
                idx = path_stack.index(nxt)
                cycles.append([*path_stack[idx:], nxt])
            elif st == 0:
                dfs(nxt)
        path_stack.pop()
        state[node] = 2

    for node in sorted(adj):
        if state.get(node, 0) == 0:
            dfs(node)

    # Orphans: code files in components/ or lib/ with in_degree == 0 (excluding entrypoints & tests)
    orphans = [
        rel
        for rel, deg in sorted(in_degree.items())
        if deg == 0
        and Path(rel).suffix.lower() in CODE_EXTS
        and not re.search(r"(?:^|/)(?:app|pages|routes)/|(?:page|layout|loading|error|not-found|main|index|app)\.|(?:\.test|\.spec)\.", rel, re.I)
        and ("components/" in rel or "lib/" in rel or "hooks/" in rel)
    ]

    return {
        "nodes": len(adj),
        "edges": sum(len(v) for v in adj.values()),
        "known_routes": sorted(known_routes),
        "cycles": cycles,
        "broken_imports": broken_imports,
        "broken_routes": broken_routes,
        "orphans": orphans,
        "rsc_bleeds": rsc_bleeds,
        "adjacency": {k: v for k, v in sorted(adj.items()) if v},
    }


def to_mermaid(report: dict) -> str:
    lines = ["flowchart TD"]
    ids: dict[str, str] = {}

    def node_id(rel: str) -> str:
        if rel not in ids:
            ids[rel] = f"N{len(ids) + 1}"
        return ids[rel]

    for src, targets in report["adjacency"].items():
        s_id = node_id(src)
        for tgt in targets:
            t_id = node_id(tgt)
            lines.append(f'  {s_id}["{src}"] --> {t_id}["{tgt}"]')
    if len(lines) == 1:
        lines.append('  EMPTY["No internal module edges detected"]')
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=None)
    parser.add_argument("--format", choices=["json", "mermaid", "text"], default="json")
    parser.add_argument("--check-cycles", action="store_true")
    parser.add_argument("--broken-links", action="store_true")
    parser.add_argument("--orphans", action="store_true")
    parser.add_argument("--rsc-bleed", action="store_true")
    args = parser.parse_args(argv)

    try:
        root = resolve_project_root(args.project_root)
        report = analyze_graph(root)
        if args.format == "mermaid":
            print(to_mermaid(report))
        elif args.format == "text":
            print(f"Nodes: {report['nodes']} | Edges: {report['edges']} | Cycles: {len(report['cycles'])} | Broken imports: {len(report['broken_imports'])} | Broken routes: {len(report['broken_routes'])} | RSC bleeds: {len(report['rsc_bleeds'])}")
        else:
            print(json.dumps(report, indent=2))

        failed = False
        if args.check_cycles and report["cycles"]:
            failed = True
        if args.broken_links and (report["broken_imports"] or report["broken_routes"]):
            failed = True
        if args.orphans and report["orphans"]:
            failed = True
        if args.rsc_bleed and report["rsc_bleeds"]:
            failed = True
        return 1 if failed else 0
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
