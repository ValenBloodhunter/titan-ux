"""Offline Design Intelligence query engine over references/data/*.json."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from titan_core import ROOT

DATA_DIR = ROOT / "references" / "data"


def _load_dataset(name: str) -> list[dict]:
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


def _tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 1]


def _score_item(item: dict, tokens: list[str], surface: str | None = None) -> int:
    blob = json.dumps(item).lower()
    score = 0
    if surface:
        surfaces = item.get("surfaces") or item.get("best_for") or []
        if surface in surfaces:
            score += 8
    for tok in tokens:
        if tok in (item.get("id") or "").lower():
            score += 6
        if tok in [d.lower() for d in item.get("domains", [])]:
            score += 5
        if tok in blob:
            score += 2
    return score


def query_design(
    *,
    query: str = "",
    surface: str | None = None,
    archetype_id: str | None = None,
    palette_id: str | None = None,
    font_id: str | None = None,
    include_patterns: bool = True,
    include_anti_slop: bool = False,
    limit: int = 3,
) -> dict:
    """Query archetypes, palettes, font pairings, UI patterns, and anti-slop rules."""
    tokens = _tokenize(query)
    archetypes = _load_dataset("design_archetypes")
    palettes = _load_dataset("palettes")
    fonts = _load_dataset("font_pairings")
    patterns = _load_dataset("ui_patterns")
    anti_slop = _load_dataset("anti_slop_rules")

    def rank(items: list[dict], explicit_id: str | None, surface_match: bool = True) -> list[dict]:
        if explicit_id:
            exact = [i for i in items if i["id"] == explicit_id]
            if not exact:
                raise ValueError(f"Unknown ID {explicit_id!r}")
            return exact
        scored = sorted(
            items,
            key=lambda x: (_score_item(x, tokens, surface if surface_match else None), x["id"]),
            reverse=True,
        )
        return scored[:limit]

    result: dict = {
        "archetypes": rank(archetypes, archetype_id),
        "palettes": rank(palettes, palette_id, surface_match=False),
        "font_pairings": rank(fonts, font_id),
    }
    if include_patterns:
        result["ui_patterns"] = rank(patterns, None)
    if include_anti_slop:
        result["anti_slop_rules"] = anti_slop
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="")
    parser.add_argument("--surface", choices=["saas-app", "marketing-editorial", "docs-content",
                                              "commerce-storefront", "design-system", "interactive-canvas"])
    parser.add_argument("--archetype")
    parser.add_argument("--palette")
    parser.add_argument("--fonts")
    parser.add_argument("--no-patterns", action="store_true")
    parser.add_argument("--anti-slop", action="store_true")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        out = query_design(
            query=args.query,
            surface=args.surface,
            archetype_id=args.archetype,
            palette_id=args.palette,
            font_id=args.fonts,
            include_patterns=not args.no_patterns,
            include_anti_slop=args.anti_slop,
            limit=args.limit,
        )
        print(json.dumps(out, indent=2))
        return 0
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
