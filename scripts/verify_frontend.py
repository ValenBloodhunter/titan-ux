"""Scoped multi-engine static frontend verifier (anti-slop, a11y, motion, perf, responsive, contrast)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from color_contrast import audit_css_tokens
from titan_core import (
    FRONTEND_EXTENSIONS,
    iter_source_files,
    load_manifest,
    resolve_project_root,
    safe_path,
    strip_comments_preserve_lines,
)

ALL_CATEGORIES = {"slop", "a11y", "motion", "perf", "responsive", "tokens"}


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _is_token_stylesheet(rel: str, text: str) -> bool:
    name = Path(rel).name.lower()
    if any(tok in name for tok in ["token", "theme", "global", "variables", "palette"]):
        return True
    return "@theme" in text or (":root" in text and text.count("--") >= 5)


def check_file(
    root: Path,
    file_path: Path,
    *,
    checks: set[str] | None = None,
    project_has_reduced_motion: bool = True,
) -> list[dict]:
    """Run static quality audits on a single frontend source file."""
    active = checks or ALL_CATEGORIES
    rel = file_path.relative_to(root).as_posix()
    ext = file_path.suffix.lower()
    raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    clean = strip_comments_preserve_lines(raw_text, ext)
    issues: list[dict] = []

    def add(code: str, category: str, severity: str, line: int, message: str):
        if category in active:
            issues.append({
                "file": rel,
                "line": line,
                "code": code,
                "category": category,
                "severity": severity,
                "message": message,
            })

    # 1. Anti-Slop & Draft Completeness (also scan raw_text for TODO/TITAN_DRAFT comments!)
    if "slop" in active:
        for m in re.finditer(r"\b(?:TITAN_DRAFT|TODO|FIXME)\b|Lorem\s+ipsum|\bAcme\s+Corp\b|\bJohn\s+Doe\b|\bJane\s+Doe\b", raw_text, re.I):
            add("SLOP_UNFINISHED", "slop", "error", _line_of(raw_text, m.start()), f"Unfinished draft or placeholder marker: {m.group(0)!r}")

        if ext in {".tsx", ".jsx", ".vue", ".svelte", ".astro", ".html"}:
            for m in re.finditer(r"\b(?:bg|text|border|fill|stroke|ring|from|to|via)-\[#(?:[0-9a-fA-F]{3,8})\]", clean):
                add("SLOP_RAW_COLOR", "slop", "error", _line_of(clean, m.start()), f"Hardcoded arbitrary hex color utility {m.group(0)!r}; use semantic tokens")
            for m in re.finditer(r"style=\{\{[^}]*?(?:color|background(?:Color)?|borderColor)\s*:\s*['\"]#[0-9a-fA-F]{3,8}['\"]", clean):
                add("SLOP_RAW_COLOR", "slop", "error", _line_of(clean, m.start()), "Hardcoded hex literal inside inline JSX style; bind a CSS variable instead")
            if re.search(r"\bfrom-(?:purple|violet|fuchsia)-\d+\b[\s\S]{0,100}?\bto-(?:cyan|sky|indigo|blue)-\d+\b", clean):
                add("SLOP_AI_GRADIENT", "slop", "warning", 1, "Generic purple/indigo-to-cyan AI gradient detected; verify intentional brand alignment")

        for m in re.finditer(r"\btransition-all\b|transition\s*:\s*all\b", clean):
            add("SLOP_TRANSITION_ALL", "motion", "error", _line_of(clean, m.start()), "Avoid blanket 'transition-all'; specify GPU-safe properties explicitly")

    # 2. Accessibility & Web Design Guidelines
    if "a11y" in active and ext in {".tsx", ".jsx", ".vue", ".svelte", ".astro", ".html"}:
        for m in re.finditer(r"<img\b([^>]*)>", clean, re.I):
            attrs = m.group(1)
            if not re.search(r"\balt\s*=", attrs):
                add("A11Y_MISSING_ALT", "a11y", "error", _line_of(clean, m.start()), "<img> missing alt attribute (use descriptive text or alt='' if decorative)")

        for m in re.finditer(r"<(?:div|span)\b([^>]*)>", clean):
            attrs = m.group(1)
            if re.search(r"\b(?:onClick|@click)\b", attrs) and not (re.search(r"\brole\s*=", attrs) and re.search(r"\b(?:onKeyDown|onKeyUp|@keydown|@keyup)\b", attrs)):
                add("A11Y_DIV_ONCLICK", "a11y", "error", _line_of(clean, m.start()), "Interactive <div>/<span> missing native <button>/<a> or role + keyboard handler")

        for m in re.finditer(r'class(?:Name)?\s*=\s*(?:"([^"]*)"|\{`([^`]*)`\}|\{\'([^\']*)\'\})', clean):
            cls = m.group(1) or m.group(2) or m.group(3) or ""
            if re.search(r"\b(?:focus:)?outline-none\b", cls) and not re.search(r"(?:focus-visible:ring|focus-visible:outline|ring-[124])", cls):
                add("A11Y_OUTLINE_NONE", "a11y", "error", _line_of(clean, m.start()), "outline-none used without a visible focus-visible ring replacement")

        for m in re.finditer(r"\btabIndex\s*=\s*\{?\s*['\"]?([1-9]\d*)", clean, re.I):
            add("A11Y_POSITIVE_TABINDEX", "a11y", "error", _line_of(clean, m.start()), f"Positive tabIndex ({m.group(1)}) disrupts natural keyboard focus order")

        for m in re.finditer(r"(?:user-scalable\s*=\s*no|maximum-scale\s*=\s*1(?:\.0)?\b)", clean, re.I):
            add("A11Y_ZOOM_BLOCK", "a11y", "error", _line_of(clean, m.start()), "Do not disable pinch-to-zoom in viewport meta")

        for m in re.finditer(r"<button\b([^>]*)>([\s\S]{0,400}?)</button>", clean):
            attrs, inner = m.group(1), m.group(2)
            if re.search(r"\b(?:aria-label|aria-labelledby|title)\s*=", attrs) or "sr-only" in inner or "{..." in attrs:
                continue
            has_icon = bool(re.search(r"<svg\b|<[A-Z][A-Za-z0-9]*Icon\b", inner))
            text_stripped = re.sub(r"<[^>]+>", "", inner)
            if has_icon and not text_stripped.strip() and "{" not in text_stripped:
                add("A11Y_ICON_BUTTON_LABEL", "a11y", "error", _line_of(clean, m.start()), "Icon-only <button> lacks aria-label, aria-labelledby, or .sr-only text")

        has_label_tag = "<label" in clean.lower() or "htmlfor" in clean.lower()
        for m in re.finditer(r"<(input|select|textarea)\b([^>]*)/?>", clean, re.I):
            tag, attrs = m.group(1).lower(), m.group(2)
            if re.search(r'type\s*=\s*["\'](?:hidden|submit|button|reset)["\']', attrs, re.I) or "{..." in attrs:
                continue
            if not re.search(r"\b(?:aria-label|aria-labelledby|id)\s*=", attrs) and not has_label_tag:
                add("A11Y_UNLABELED_INPUT", "a11y", "error", _line_of(clean, m.start()), f"<{tag}> missing associated label, id, or aria-label")

        for m in re.finditer(r"<a\b([^>]*target\s*=\s*['\"]_blank['\"][^>]*)>", clean, re.I):
            attrs = m.group(1)
            if not re.search(r"\brel\s*=\s*['\"][^'\"]*noopener", attrs, re.I):
                add("A11Y_BLANK_TARGET_UNSAFE", "a11y", "error", _line_of(clean, m.start()), "target='_blank' link missing rel='noopener noreferrer'")

    if "a11y" in active and ext in {".css", ".scss"}:
        for m in re.finditer(r"([^{}]+)\{([^{}]*outline\s*:\s*(?:none|0)\b[^{}]*)\}", clean):
            sel, body = m.group(1), m.group(2)
            if ":focus-visible" in sel or "box-shadow" in body:
                continue
            add("A11Y_OUTLINE_NONE", "a11y", "error", _line_of(clean, m.start()), "CSS removes outline without a :focus-visible ring or box-shadow replacement")

    # 3. Motion Engineering (Emil Kowalski rules)
    if "motion" in active:
        if ext in {".css", ".scss"}:
            for m in re.finditer(r"transition(?:-property)?\s*:\s*([^;]+);", clean):
                prop = m.group(1).lower()
                if re.search(r"\b(?:width|height|top|left|right|bottom|margin|padding)\b", prop):
                    add("MOTION_LAYOUT_ANIM", "motion", "error", _line_of(clean, m.start()), f"Animating layout property ({prop.strip()}) triggers reflow; use transform/clip-path/grid-rows")
            for m in re.finditer(r"@keyframes\s+[A-Za-z0-9_-]+\s*\{([\s\S]*?)\n\}", clean):
                kf = m.group(1).lower()
                if re.search(r"\b(?:width|height|top|left|right|bottom|margin|padding)\s*:", kf):
                    add("MOTION_LAYOUT_ANIM", "motion", "error", _line_of(clean, m.start()), "Keyframe animates layout property; animate transform/opacity instead")
            for m in re.finditer(r"transition(?:-duration)?\s*:[^;]*\b([4-9]\d{2}|[1-9]\d{3})ms\b", clean):
                add("MOTION_SLOW_UI", "motion", "warning", _line_of(clean, m.start()), f"Transition duration {m.group(1)}ms exceeds crisp 300ms UI ceiling")

        for m in re.finditer(r"\bduration-(\d+)\b", clean):
            ms = int(m.group(1))
            if ms >= 400:
                add("MOTION_SLOW_UI", "motion", "warning", _line_of(clean, m.start()), f"Tailwind duration-{ms} exceeds crisp 300ms interactive UI ceiling")

        uses_motion = ("@keyframes" in clean) or ("framer-motion" in clean) or ('"motion/react"' in clean) or ("'motion/react'" in clean)
        if uses_motion and not project_has_reduced_motion and "useReducedMotion" not in clean and "MotionConfig" not in clean and "prefers-reduced-motion" not in clean:
            add("MOTION_MISSING_REDUCED", "motion", "error", 1, "Motion/keyframes used without prefers-reduced-motion CSS guard or MotionConfig reducedMotion='user'")

    # 4. React / Next.js Performance & CWV
    if "perf" in active and ext in {".tsx", ".jsx", ".ts", ".js"}:
        for m in re.finditer(r"\.map\([^)]*,\s*(idx|index|i)\s*\)[\s\S]{0,140}?key=\{\s*\1\s*\}", clean):
            add("PERF_INDEX_KEY", "perf", "warning", _line_of(clean, m.start()), f"Avoid using array index ({m.group(1)}) as React key on dynamic lists")

        is_client = bool(re.match(r"^\s*['\"]use client['\"]", clean))
        if is_client:
            for m in re.finditer(r"^\s*import\s+[^\n]+\s+from\s+['\"](three|recharts|echarts|monaco-editor)['\"]", clean, re.M):
                add("PERF_STATIC_HEAVY_LIB", "perf", "warning", _line_of(clean, m.start()), f"Static client import of heavy library {m.group(1)!r}; prefer next/dynamic or React.lazy")

        for m in re.finditer(r"<img\b([^>]*)>", clean, re.I):
            attrs = m.group(1)
            if not re.search(r"\b(?:width|height)\s*=", attrs) and "aspect-" not in attrs:
                add("PERF_IMG_NO_DIMENSIONS", "perf", "warning", _line_of(clean, m.start()), "<img> lacks explicit width/height or aspect-ratio class (CLS risk)")

        # Sequential fetch waterfall detector inside async functions
        for m in re.finditer(r"async\s+(?:function\s+\w+|\([^)]*\)\s*=>)\s*\{([\s\S]{0,1200}?)\n\}", clean):
            body = m.group(1)
            awaits = re.findall(r"=\s*await\s+(?:fetch|db\.|prisma\.|supabase\.)", body)
            if len(awaits) >= 3 and "Promise.all" not in body:
                add("PERF_WATERFALL_AWAIT", "perf", "warning", _line_of(clean, m.start()), "3+ sequential awaits without Promise.all(); verify independent fetches are parallelized")

    # 5. Responsive Hygiene
    if "responsive" in active:
        if ext in {".css", ".scss"}:
            for m in re.finditer(r"\b100vh\b", clean):
                line_num = _line_of(clean, m.start())
                line_str = clean.splitlines()[line_num - 1]
                if "100dvh" not in clean:
                    add("RESP_100VH", "responsive", "warning", line_num, f"Prefer 100dvh over bare 100vh ({line_str.strip()}) for mobile browser bar safety")
        if ext in {".tsx", ".jsx", ".vue", ".svelte", ".astro", ".html"}:
            for m in re.finditer(r"\b(?:min-)?h-screen\b", clean):
                add("RESP_100VH", "responsive", "warning", _line_of(clean, m.start()), f"Prefer min-h-dvh / h-dvh over {m.group(0)!r} for mobile dynamic viewport height")

    # 6. Token CSS Contrast Audit
    if "tokens" in active and ext == ".css" and _is_token_stylesheet(rel, raw_text):
        try:
            report = audit_css_tokens(file_path)
            for fail in report["failures"]:
                add("TOKEN_LOW_CONTRAST", "tokens", "error", 1,
                    f"{fail['theme']} pair {fail['pair']} has contrast {fail['wcag_ratio']}:1 (< {fail['min_ratio']}:1 required)")
        except OSError:
            pass

    return issues


def apply_safe_fixes(root: Path, files: list[Path]) -> list[str]:
    """Apply strictly deterministic, non-destructive mechanical fixes to targeted files."""
    fixed_files: list[str] = []
    for path in files:
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        updated = original
        ext = path.suffix.lower()

        if ext in {".tsx", ".jsx", ".vue", ".svelte", ".astro", ".html"}:
            # Add rel="noopener noreferrer" to target="_blank" links missing rel
            def _fix_blank(m: re.Match) -> str:
                attrs = m.group(1)
                if re.search(r"\brel\s*=", attrs, re.I):
                    return m.group(0)
                return f'<a{attrs} rel="noopener noreferrer">'
            updated = re.sub(r"<a([^>]*\btarget\s*=\s*['\"]_blank['\"][^>]*)>", _fix_blank, updated, flags=re.I)
            updated = re.sub(r"\bmin-h-screen\b", "min-h-dvh", updated)

        if ext in {".css", ".scss"} and "100dvh" not in updated:
            updated = re.sub(r"\b100vh\b", "100dvh", updated)

        if updated != original:
            path.write_text(updated, encoding="utf-8")
            fixed_files.append(path.relative_to(root).as_posix())
    return fixed_files


def verify_files(
    root: Path,
    files: list[Path],
    *,
    checks: set[str] | None = None,
    manifest: dict | None = None,
    fix: bool = False,
) -> dict:
    """Verify scoped files (and optional manifest) returning structured error/warning summary."""
    fixed: list[str] = []
    if fix:
        fixed = apply_safe_fixes(root, files)

    all_css = iter_source_files(root, {".css", ".scss"})
    project_reduced = any(
        "prefers-reduced-motion" in f.read_text(encoding="utf-8", errors="ignore")
        for f in all_css
    )

    issues: list[dict] = []
    if manifest:
        for rel in manifest.get("allowed_files", []):
            target = safe_path(root, rel)
            if not target.is_file():
                issues.append({
                    "file": rel,
                    "line": 1,
                    "code": "MANIFEST_MISSING_FILE",
                    "category": "slop",
                    "severity": "error",
                    "message": f"Locked manifest file missing on disk: {rel}",
                })

    for f in files:
        if f.is_file():
            issues.extend(check_file(root, f, checks=checks, project_has_reduced_motion=project_reduced))

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    return {
        "files_checked": len([f for f in files if f.is_file()]),
        "fixed_files": fixed,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": issues,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=None)
    parser.add_argument("--files", nargs="+", help="Project-relative files to audit")
    parser.add_argument("--manifest", help="Relative path to titan-manifest.json")
    parser.add_argument("--all", action="store_true", help="Audit all frontend files under project root")
    parser.add_argument("--checks", default="all", help="Comma-separated: slop,a11y,motion,perf,responsive,tokens")
    parser.add_argument("--fix", action="store_true", help="Apply safe mechanical fixes to targeted files only")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args(argv)

    try:
        root = resolve_project_root(args.project_root)
        checks = ALL_CATEGORIES if args.checks == "all" else {c.strip() for c in args.checks.split(",") if c.strip()}
        unknown = checks - ALL_CATEGORIES
        if unknown:
            raise ValueError(f"Unknown check categories: {', '.join(sorted(unknown))}")

        manifest_data = None
        target_files: list[Path] = []
        if args.manifest:
            manifest_data = load_manifest(root, args.manifest)
            rels = [manifest_data.get("tokens_file"), *manifest_data.get("allowed_files", [])]
            seen = set()
            for rel in rels:
                if rel and rel not in seen:
                    seen.add(rel)
                    target_files.append(safe_path(root, rel))
        elif args.files:
            for rel in args.files:
                target_files.append(safe_path(root, rel))
        elif args.all:
            target_files = iter_source_files(root, FRONTEND_EXTENSIONS)
        else:
            raise ValueError("Specify --files, --manifest, or --all")

        report = verify_files(root, target_files, checks=checks, manifest=manifest_data, fix=args.fix)
        if args.format == "text":
            print(f"Checked {report['files_checked']} file(s): {report['error_count']} error(s), {report['warning_count']} warning(s)")
            for iss in report["issues"]:
                print(f"  [{iss['severity'].upper()}] {iss['file']}:{iss['line']} {iss['code']} - {iss['message']}")
        else:
            print(json.dumps(report, indent=2))
        return 1 if report["error_count"] > 0 else 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
