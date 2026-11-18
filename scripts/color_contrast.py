"""Zero-dependency OKLCH/sRGB color math, WCAG 2.2 contrast, and APCA Lc auditor."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    c = _clamp01(c)
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055


def oklch_to_rgb(L: float, C: float, H_deg: float) -> tuple[float, float, float]:
    """Convert OKLCH (L in 0..1, C >= 0, H in degrees) to clamped sRGB 0..1."""
    h_rad = math.radians(H_deg)
    a = C * math.cos(h_rad)
    b = C * math.sin(h_rad)

    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    r_lin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g_lin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    return (linear_to_srgb(r_lin), linear_to_srgb(g_lin), linear_to_srgb(b_lin))


def rgb_to_oklch(r: float, g: float, b: float) -> tuple[float, float, float]:
    """Convert sRGB (0..1) to OKLCH (L in 0..1, C, H in degrees)."""
    rl, gl, bl = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    l = math.copysign(abs(0.4122214708 * rl + 0.5363325363 * gl + 0.0514459929 * bl) ** (1 / 3),
                      0.4122214708 * rl + 0.5363325363 * gl + 0.0514459929 * bl)
    m = math.copysign(abs(0.2119034982 * rl + 0.6806995451 * gl + 0.1073969566 * bl) ** (1 / 3),
                      0.2119034982 * rl + 0.6806995451 * gl + 0.1073969566 * bl)
    s = math.copysign(abs(0.0883024619 * rl + 0.2817188376 * gl + 0.6299787005 * bl) ** (1 / 3),
                      0.0883024619 * rl + 0.2817188376 * gl + 0.6299787005 * bl)

    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    b_val = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    C = math.hypot(a, b_val)
    H = (math.degrees(math.atan2(b_val, a)) + 360.0) % 360.0 if C > 1e-6 else 0.0
    return (L, C, H)


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = (int(round(_clamp01(c) * 255)) for c in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def _hsl_to_rgb(h_deg: float, s: float, l: float) -> tuple[float, float, float]:
    h = (h_deg % 360.0) / 360.0
    if s == 0:
        return (l, l, l)
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q

    def hue2rgb(t: float) -> float:
        t = t % 1.0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    return (hue2rgb(h + 1 / 3), hue2rgb(h), hue2rgb(h - 1 / 3))


def parse_color(value: str) -> tuple[float, float, float]:
    """Parse hex, rgb/rgba, hsl/hsla, or oklch() CSS colors into sRGB (0..1)."""
    s = value.strip().lower()
    if s == "white":
        return (1.0, 1.0, 1.0)
    if s == "black":
        return (0.0, 0.0, 0.0)
    if s.startswith("#"):
        hx = s[1:]
        if len(hx) in {3, 4}:
            hx = "".join(c * 2 for c in hx[:3])
        elif len(hx) in {6, 8}:
            hx = hx[:6]
        else:
            raise ValueError(f"Unsupported hex color: {value!r}")
        return (int(hx[0:2], 16) / 255.0, int(hx[2:4], 16) / 255.0, int(hx[4:6], 16) / 255.0)

    m_rgb = re.match(r"^rgba?\((.+)\)$", s)
    if m_rgb:
        parts = [p for p in re.split(r"[\s,/]+", m_rgb.group(1).strip()) if p]
        if len(parts) < 3:
            raise ValueError(f"Invalid rgb() color: {value!r}")
        vals = []
        for p in parts[:3]:
            vals.append(float(p[:-1]) / 100.0 if p.endswith("%") else float(p) / 255.0)
        return (_clamp01(vals[0]), _clamp01(vals[1]), _clamp01(vals[2]))

    m_hsl = re.match(r"^hsla?\((.+)\)$", s)
    if m_hsl:
        parts = [p for p in re.split(r"[\s,/]+", m_hsl.group(1).strip()) if p]
        if len(parts) < 3:
            raise ValueError(f"Invalid hsl() color: {value!r}")
        h = float(re.sub(r"deg$", "", parts[0]))
        sat = float(parts[1].rstrip("%")) / 100.0
        lit = float(parts[2].rstrip("%")) / 100.0
        return _hsl_to_rgb(h, _clamp01(sat), _clamp01(lit))

    m_oklch = re.match(r"^oklch\((.+)\)$", s)
    if m_oklch:
        parts = [p for p in re.split(r"[\s,/]+", m_oklch.group(1).strip()) if p]
        if len(parts) < 3:
            raise ValueError(f"Invalid oklch() color: {value!r}")
        L = float(parts[0][:-1]) / 100.0 if parts[0].endswith("%") else float(parts[0])
        C = float(parts[1][:-1]) * 0.4 / 100.0 if parts[1].endswith("%") else float(parts[1])
        raw_h = parts[2]
        if raw_h.endswith("rad"):
            H = math.degrees(float(raw_h[:-3]))
        elif raw_h.endswith("turn"):
            H = float(raw_h[:-4]) * 360.0
        else:
            H = float(re.sub(r"deg$", "", raw_h))
        return oklch_to_rgb(L, C, H)

    raise ValueError(f"Unsupported color format: {value!r}")


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    rl, gl, bl = (srgb_to_linear(c) for c in rgb)
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl


def wcag_contrast(fg: str | tuple[float, float, float], bg: str | tuple[float, float, float]) -> float:
    """Return WCAG 2.1/2.2 contrast ratio (1.0 .. 21.0)."""
    fg_rgb = parse_color(fg) if isinstance(fg, str) else fg
    bg_rgb = parse_color(bg) if isinstance(bg, str) else bg
    l1 = relative_luminance(fg_rgb)
    l2 = relative_luminance(bg_rgb)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def apca_contrast(fg: str | tuple[float, float, float], bg: str | tuple[float, float, float]) -> float:
    """Compute APCA-W3 (0.0.98G-4g) perceptual contrast Lc (-108 .. +106)."""
    fg_rgb = parse_color(fg) if isinstance(fg, str) else fg
    bg_rgb = parse_color(bg) if isinstance(bg, str) else bg

    def y_srgb(rgb: tuple[float, float, float]) -> float:
        r, g, b = (c ** 2.4 for c in rgb)
        y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        return y if y >= 0.022 else y + (0.022 - y) ** 1.414

    txt_y = y_srgb(fg_rgb)
    bg_y = y_srgb(bg_rgb)
    if abs(bg_y - txt_y) < 0.0005:
        return 0.0

    if bg_y > txt_y:  # Dark text on light background (BoW)
        sapc = (bg_y ** 0.56 - txt_y ** 0.57) * 1.14
        return round((sapc - 0.027) * 100.0, 1) if sapc >= 0.1 else 0.0
    # Light text on dark background (WoB)
    sapc = (bg_y ** 0.65 - txt_y ** 0.62) * 1.14
    return round((sapc + 0.027) * 100.0, 1) if sapc <= -0.1 else 0.0


def evaluate_pair(fg: str, bg: str) -> dict:
    ratio = wcag_contrast(fg, bg)
    lc = apca_contrast(fg, bg)
    return {
        "fg": fg,
        "bg": bg,
        "wcag_ratio": ratio,
        "aa_normal": ratio >= 4.5,
        "aa_large_or_ui": ratio >= 3.0,
        "aaa_normal": ratio >= 7.0,
        "apca_lc": lc,
        "apca_body_pass": abs(lc) >= 60.0,
        "apca_ui_pass": abs(lc) >= 45.0,
    }


def suggest_fix(fg: str, bg: str, target_ratio: float = 4.5) -> dict:
    """Adjust foreground lightness in OKLCH space preserving hue to reach WCAG target_ratio."""
    fg_rgb = parse_color(fg)
    bg_rgb = parse_color(bg)
    bg_lum = relative_luminance(bg_rgb)
    L, C, H = rgb_to_oklch(*fg_rgb)
    if wcag_contrast(fg_rgb, bg_rgb) >= target_ratio:
        return {"original": fg, "suggested_hex": rgb_to_hex(fg_rgb), "oklch": f"oklch({L:.3f} {C:.3f} {H:.1f})",
                "wcag_ratio": wcag_contrast(fg_rgb, bg_rgb), "changed": False}

    # Try darkening toward 0 or lightening toward 1 depending on background luminance
    directions = [-1, 1] if bg_lum > 0.18 else [1, -1]
    best = None
    for direction in directions:
        for step in range(1, 201):
            cand_l = _clamp01(L + direction * (step / 200.0))
            cand_c = C * (1.0 - max(0.0, abs(cand_l - 0.5) - 0.35))
            rgb = oklch_to_rgb(cand_l, cand_c, H)
            ratio = wcag_contrast(rgb, bg_rgb)
            if ratio >= target_ratio:
                best = (cand_l, cand_c, H, rgb, ratio)
                break
            if cand_l in (0.0, 1.0):
                break
        if best:
            break
    if not best:
        fallback = "#000000" if bg_lum > 0.18 else "#FFFFFF"
        return {"original": fg, "suggested_hex": fallback, "oklch": fallback,
                "wcag_ratio": wcag_contrast(fallback, bg_rgb), "changed": True}
    nl, nc, nh, nrgb, nratio = best
    return {
        "original": fg,
        "suggested_hex": rgb_to_hex(nrgb),
        "oklch": f"oklch({nl:.3f} {nc:.3f} {nh:.1f})",
        "wcag_ratio": nratio,
        "changed": True,
    }


def generate_oklch_ramp(color: str, name: str = "primary") -> dict:
    """Generate a perceptually uniform 50..950 OKLCH scale and CSS tokens."""
    rgb = parse_color(color)
    _, base_c, base_h = rgb_to_oklch(*rgb)
    stops = {
        "50": (0.975, base_c * 0.18),
        "100": (0.940, base_c * 0.32),
        "200": (0.875, base_c * 0.52),
        "300": (0.785, base_c * 0.72),
        "400": (0.680, base_c * 0.90),
        "500": (0.575, base_c),
        "600": (0.485, base_c * 0.96),
        "700": (0.400, base_c * 0.86),
        "800": (0.320, base_c * 0.72),
        "900": (0.245, base_c * 0.56),
        "950": (0.175, base_c * 0.42),
    }
    scale = {}
    css_lines = []
    for k, (l_val, c_val) in stops.items():
        srgb = oklch_to_rgb(l_val, c_val, base_h)
        hx = rgb_to_hex(srgb)
        ok = f"oklch({l_val:.3f} {c_val:.3f} {base_h:.1f})"
        scale[k] = {"hex": hx, "oklch": ok}
        css_lines.append(f"  --color-{name}-{k}: {ok}; /* {hx} */")
    return {"name": name, "base": color, "scale": scale, "css": "\n".join(css_lines)}


def _extract_css_theme_vars(css_text: str) -> dict[str, dict[str, str]]:
    """Extract light (:root) and dark (.dark / [data-theme="dark"]) CSS custom properties."""
    cleaned = re.sub(r"/\*[\s\S]*?\*/", "", css_text)
    themes: dict[str, dict[str, str]] = {"light": {}, "dark": {}}
    block_re = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
    for selector, body in block_re.findall(cleaned):
        sel = selector.strip()
        target = None
        if ":root" in sel or "[data-theme=\"light\"]" in sel or "[data-theme='light']" in sel:
            target = "light"
        if any(tok in sel for tok in [".dark", "[data-theme=\"dark\"]", "[data-theme='dark']"]):
            target = "dark"
        if not target:
            continue
        for var_name, var_val in re.findall(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", body):
            themes[target][var_name.strip()] = var_val.strip()
    return themes


def _resolve_var(val: str, mapping: dict[str, str], depth: int = 0) -> str:
    if depth > 5:
        return val
    m = re.match(r"^var\(\s*(--[a-zA-Z0-9_-]+)\s*(?:,\s*([^)]+))?\)$", val.strip())
    if not m:
        return val
    ref = mapping.get(m.group(1))
    if ref:
        return _resolve_var(ref, mapping, depth + 1)
    return m.group(2).strip() if m.group(2) else val


def audit_css_tokens(css_path: Path) -> dict:
    """Audit semantic CSS token contrast ratios across light and dark blocks."""
    css_text = css_path.read_text(encoding="utf-8")
    themes = _extract_css_theme_vars(css_text)
    pair_specs = [
        ("--text", "--bg", 4.5, "primary text on bg"),
        ("--text", "--surface", 4.5, "primary text on surface"),
        ("--text", "--surface-elevated", 4.5, "primary text on elevated surface"),
        ("--text-muted", "--bg", 4.5, "muted text on bg"),
        ("--text-muted", "--surface", 4.5, "muted text on surface"),
        ("--accent-fg", "--accent", 4.5, "accent foreground on accent"),
        ("--accent", "--surface", 3.0, "accent UI contrast on surface"),
        ("--success", "--surface", 3.0, "success indicator on surface"),
        ("--warning", "--surface", 3.0, "warning indicator on surface"),
        ("--danger", "--surface", 3.0, "danger indicator on surface"),
    ]
    results = []
    failures = []
    for mode, vars_map in themes.items():
        if not vars_map:
            continue
        merged = {**themes["light"], **vars_map} if mode == "dark" else vars_map
        for fg_var, bg_var, min_ratio, label in pair_specs:
            if fg_var not in merged or bg_var not in merged:
                continue
            fg_raw = _resolve_var(merged[fg_var], merged)
            bg_raw = _resolve_var(merged[bg_var], merged)
            try:
                ev = evaluate_pair(fg_raw, bg_raw)
            except ValueError:
                continue
            passed = ev["wcag_ratio"] >= min_ratio
            row = {"theme": mode, "pair": f"{fg_var} on {bg_var}", "label": label, "min_ratio": min_ratio, "passed": passed, **ev}
            results.append(row)
            if not passed:
                failures.append(row)
    return {"file": str(css_path), "checked_pairs": len(results), "failures": failures, "results": results}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_pair = sub.add_parser("pair", help="Evaluate WCAG and APCA contrast for a fg/bg pair")
    p_pair.add_argument("fg")
    p_pair.add_argument("bg")

    p_fix = sub.add_parser("suggest-fix", help="Adjust fg lightness in OKLCH to meet WCAG ratio")
    p_fix.add_argument("fg")
    p_fix.add_argument("bg")
    p_fix.add_argument("--target", type=float, default=4.5)

    p_ramp = sub.add_parser("ramp", help="Generate a 50..950 OKLCH scale from a seed color")
    p_ramp.add_argument("color")
    p_ramp.add_argument("--name", default="primary")

    p_css = sub.add_parser("audit-css", help="Audit semantic CSS custom properties in :root/.dark")
    p_css.add_argument("css_file")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "pair":
            print(json.dumps(evaluate_pair(args.fg, args.bg), indent=2))
            return 0
        if args.cmd == "suggest-fix":
            print(json.dumps(suggest_fix(args.fg, args.bg, args.target), indent=2))
            return 0
        if args.cmd == "ramp":
            print(json.dumps(generate_oklch_ramp(args.color, args.name), indent=2))
            return 0
        if args.cmd == "audit-css":
            report = audit_css_tokens(Path(args.css_file))
            print(json.dumps(report, indent=2))
            return 1 if report["failures"] else 0
    except (ValueError, OSError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
