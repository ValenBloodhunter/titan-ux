"""Deterministic 5-axis frontend task router enforcing progressive module loading."""
from __future__ import annotations

import argparse
import json
import re
import shlex
import sys

from titan_core import routes


def _resolve_alias(value: str, table: dict) -> str:
    key = re.sub(r"[^a-z0-9]", "", value.lower())
    for name, spec in table.items():
        candidates = [name, *spec.get("aliases", [])]
        if key in {re.sub(r"[^a-z0-9]", "", c.lower()) for c in candidates}:
            return name
    raise ValueError(f"Unsupported option {value!r}. Expected one of: {', '.join(table)}")


def _infer_surface(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["three", "threejs", "webgl", "3d", "canvas", "shader"]):
        return "interactive-canvas"
    if any(k in lower for k in ["design system", "ui kit", "component library", "primitive"]):
        return "design-system"
    if any(k in lower for k in ["storefront", "ecommerce", "checkout", "cart", "product page", "shop"]):
        return "commerce-storefront"
    if any(k in lower for k in ["docs", "documentation", "mdx", "knowledge base", "blog"]):
        return "docs-content"
    if any(k in lower for k in ["landing", "marketing", "launch", "portfolio", "hero", "editorial"]):
        return "marketing-editorial"
    return "saas-app"


def _infer_command(tokens: list[str]) -> tuple[str | None, list[str]]:
    if tokens and tokens[0].startswith("/"):
        raw = tokens[0].lstrip("/").lower()
        if raw.startswith("titan-"):
            cmd = raw[len("titan-"):]
            if cmd == "ux":
                return (None, tokens[1:])
            cfg = routes()["commands"]
            if cmd not in cfg:
                raise ValueError(f"Unknown command /{raw}")
            return (cmd, tokens[1:])
        raise ValueError(f"Unknown slash command {tokens[0]!r}")
    return (None, tokens)


def plan_frontend_task(
    request: str,
    *,
    surface: str | None = None,
    stack: str | None = None,
    motion_tier: int | None = None,
    density: str | None = None,
) -> dict:
    """Resolve command, 5 routing axes, and minimal reference modules to load."""
    cfg = routes()
    tokens = shlex.split(request)
    if not tokens:
        raise ValueError("Supply a frontend task or /titan-* command")

    explicit_cmd, rest = _infer_command(tokens)
    payload = " ".join(rest).strip()
    if explicit_cmd and explicit_cmd not in {"discover", "polish", "motion", "a11y", "perf", "verify"} and not payload:
        raise ValueError(f"Usage: /titan-{explicit_cmd} <target or specification>")

    lower = payload.lower()
    command = explicit_cmd
    if not command:
        if re.search(r"\b(?:compare|versus|vs)\b", lower):
            command = "compare"
        elif re.search(r"\b(?:animation|motion|spring|transition|gesture)\b", lower) and not re.search(r"\b(?:build|create|implement)\b", lower):
            command = "motion"
        elif re.search(r"\b(?:a11y|accessibility|wcag|aria|screen reader|contrast)\b", lower) and not re.search(r"\b(?:build|create|implement)\b", lower):
            command = "a11y"
        elif re.search(r"\b(?:perf|performance|waterfall|bundle|lcp|cls|inp|vitals)\b", lower) and not re.search(r"\b(?:build|create|implement)\b", lower):
            command = "perf"
        elif re.search(r"\b(?:polish|anti-slop|critique|refine|redesign)\b", lower):
            command = "polish"
        elif re.search(r"\b(?:verify|qa|playwright|audit)\b", lower):
            command = "verify"
        elif re.search(r"\b(?:token|theme|palette|oklch)\b", lower) and not re.search(r"\b(?:page|app|dashboard|component)\b", lower):
            command = "tokens"
        elif re.search(r"\b(?:architect|plan|blueprint|spec)\b", lower):
            command = "architect"
        elif re.search(r"\b(?:migrate|upgrade)\b", lower):
            command = "migrate"
        elif re.search(r"\b(?:discover|inspect|scan|inventory)\b", lower):
            command = "discover"
        else:
            command = "build"

    if command in {"discover", "compare"} and surface:
        raise ValueError(f"/titan-{command} is read-only and does not take --surface overrides")

    resolved_surface = _resolve_alias(surface, cfg["surfaces"]) if surface else _infer_surface(payload or request)
    resolved_stack = _resolve_alias(stack, cfg["stacks"]) if stack else "nextjs-app"
    surface_spec = cfg["surfaces"][resolved_surface]
    stack_spec = cfg["stacks"][resolved_stack]

    resolved_motion = motion_tier if motion_tier is not None else surface_spec["default_motion_tier"]
    if resolved_motion not in (0, 1, 2):
        raise ValueError("motion_tier must be 0, 1, or 2")
    resolved_density = density or surface_spec["default_density"]

    cmd_spec = cfg["commands"][command]
    resources: list[str] = []

    def add(res: str):
        if res not in resources:
            resources.append(res)

    if command != "discover":
        if command in {"architect", "tokens", "build", "migrate"}:
            add("references/pre_gen_gate.md")
        if command in {"architect", "build"}:
            add("references/routing.md")
        for m in cmd_spec["modules"]:
            add(m)
        for t in cmd_spec["templates"]:
            add(t)
        if command in {"build", "architect"}:
            for m in surface_spec["conditional_modules"]:
                add(m)
            add(stack_spec["perf_module"])
        if command == "motion" or (command == "build" and resolved_motion >= 1):
            add("references/modules/motion-engineering.md")

    return {
        "command": command,
        "playbook": cmd_spec["playbook"],
        "mode": cmd_spec["mode"],
        "surface": resolved_surface,
        "stack": resolved_stack,
        "motion_tier": resolved_motion,
        "density": resolved_density,
        "archetype_hint": surface_spec["default_archetype"],
        "required_states": surface_spec["required_states"],
        "resources": resources,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request")
    parser.add_argument("--surface")
    parser.add_argument("--stack")
    parser.add_argument("--motion-tier", type=int, choices=[0, 1, 2], default=None)
    parser.add_argument("--density", choices=["compact", "balanced", "editorial"], default=None)
    args = parser.parse_args(argv)
    try:
        plan = plan_frontend_task(
            args.request,
            surface=args.surface,
            stack=args.stack,
            motion_tier=args.motion_tier,
            density=args.density,
        )
        print(json.dumps(plan, indent=2))
        return 0
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
