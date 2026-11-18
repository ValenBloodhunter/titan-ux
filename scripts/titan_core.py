"""Shared containment, route registry, file scanning, and manifest helpers for Titan-UX."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    "node_modules",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".astro",
    "dist",
    "build",
    "out",
    "coverage",
    ".git",
    ".turbo",
    ".cache",
    "__pycache__",
    ".venv",
    "venv",
    ".titan-ux",
}

FRONTEND_EXTENSIONS = {
    ".tsx",
    ".jsx",
    ".ts",
    ".js",
    ".mts",
    ".mjs",
    ".vue",
    ".svelte",
    ".astro",
    ".html",
    ".css",
    ".scss",
}


@lru_cache(maxsize=1)
def routes() -> dict:
    """Load the canonical Titan-UX routing configuration."""
    return json.loads((ROOT / "references" / "routes.json").read_text(encoding="utf-8"))


def resolve_project_root(explicit: str | None = None) -> Path:
    """Resolve and verify an existing project root directory."""
    candidate = Path(explicit).expanduser() if explicit else Path.cwd()
    resolved = candidate.resolve()
    if not resolved.exists() or not resolved.is_dir():
        raise ValueError(f"Project root does not exist or is not a directory: {candidate}")
    return resolved


def safe_path(root: Path, relative: str, *, allow_internal_dir: bool = False) -> Path:
    """Validate project-relative paths against traversal, escaping symlinks, and bad filenames."""
    raw = str(relative).replace("\\", "/")
    if not raw or PureWindowsPath(raw).drive or raw.startswith("/"):
        raise ValueError(f"Expected a project-relative path, got: {relative!r}")
    parts = raw.split("/")
    for idx, part in enumerate(parts):
        if part in {"", ".", ".."} or part.endswith((".", " ")):
            raise ValueError(f"Unsafe path component: {part!r}")
        if part.startswith("."):
            if not (allow_internal_dir and idx == 0 and part == ".titan-ux"):
                raise ValueError(f"Hidden path component rejected: {part!r}")
        if re.search(r'[<>:"|?*\x00-\x1f]', part) or re.match(
            r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", part, re.I
        ):
            raise ValueError(f"Invalid filename component: {part!r}")
    root_resolved = root.resolve()
    target = root_resolved.joinpath(*parts).resolve()
    if not target.is_relative_to(root_resolved):
        raise ValueError(f"Path or symlink escapes project root: {relative!r}")
    return target


def iter_source_files(root: Path, extensions: set[str] | None = None) -> list[Path]:
    """Walk source files under project root while skipping build/vendor/escaping paths."""
    root_resolved = root.resolve()
    allowed_exts = extensions or FRONTEND_EXTENSIONS
    results: list[Path] = []
    stack = [root_resolved]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda p: p.name)
        except OSError:
            continue
        for entry in entries:
            try:
                resolved = entry.resolve()
            except OSError:
                continue
            if not resolved.is_relative_to(root_resolved):
                continue
            if entry.is_dir():
                if entry.name in SKIP_DIRS or entry.name.startswith("."):
                    continue
                stack.append(entry)
            elif entry.is_file() and entry.suffix.lower() in allowed_exts:
                results.append(entry)
    return sorted(results)


def strip_comments_preserve_lines(text: str, ext: str = ".tsx") -> str:
    """Remove comments while keeping line indices aligned for accurate diagnostics."""
    ext = ext.lower()
    if ext in {".html", ".vue", ".svelte", ".astro"}:
        text = re.sub(r"<!--[\s\S]*?-->", lambda m: "\n" * m.group(0).count("\n"), text)
    if ext in {".css", ".scss"}:
        return re.sub(r"/\*[\s\S]*?\*/", lambda m: "\n" * m.group(0).count("\n"), text)

    out: list[str] = []
    i = 0
    n = len(text)
    in_str: str | None = None
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in {"'", '"', "`"}:
            in_str = ch
            out.append(ch)
            i += 1
        elif ch == "/" and nxt == "/":
            while i < n and text[i] != "\n":
                i += 1
        elif ch == "/" and nxt == "*":
            end = text.find("*/", i + 2)
            if end == -1:
                out.append("\n" * text[i:].count("\n"))
                break
            out.append("\n" * text[i : end + 2].count("\n"))
            i = end + 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def load_manifest(root: Path, rel_path: str = ".titan-ux/titan-manifest.json") -> dict:
    """Load and validate an operational Titan-UX manifest."""
    path = safe_path(root, rel_path, allow_internal_dir=True)
    if not path.is_file():
        raise FileNotFoundError(f"Manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(root: Path, data: dict, rel_path: str = ".titan-ux/titan-manifest.json") -> Path:
    """Write an operational Titan-UX manifest safely inside the project root."""
    path = safe_path(root, rel_path, allow_internal_dir=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
