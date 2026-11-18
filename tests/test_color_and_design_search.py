"""OKLCH/WCAG/APCA color math, dataset integrity, and Design Intelligence search tests."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import color_contrast as cc
import design_search as ds


class TestColorContrast(unittest.TestCase):
    def test_known_wcag_and_apca_values(self):
        self.assertEqual(cc.wcag_contrast("#000000", "#FFFFFF"), 21.0)
        self.assertEqual(cc.wcag_contrast("#334455", "#334455"), 1.0)
        self.assertGreaterEqual(cc.wcag_contrast("#767676", "#FFFFFF"), 4.5)

        bow = cc.apca_contrast("#000000", "#FFFFFF")
        wob = cc.apca_contrast("#FFFFFF", "#000000")
        self.assertGreater(bow, 100.0)
        self.assertLess(wob, -100.0)

    def test_oklch_parsing_and_suggest_fix(self):
        rgb = cc.parse_color("oklch(0.62 0.18 260deg)")
        self.assertEqual(len(rgb), 3)
        self.assertTrue(all(0.0 <= c <= 1.0 for c in rgb))

        fix = cc.suggest_fix("#94A3B8", "#FFFFFF", target_ratio=4.5)
        self.assertTrue(fix["changed"])
        self.assertGreaterEqual(fix["wcag_ratio"], 4.5)

        ramp = cc.generate_oklch_ramp("#1D4ED8", name="brand")
        self.assertEqual(len(ramp["scale"]), 11)
        self.assertIn("--color-brand-500:", ramp["css"])

    def test_all_curated_palettes_pass_wcag_aa_in_light_and_dark(self):
        palettes = json.loads((ROOT / "references/data/palettes.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(palettes), 12)
        pair_checks = [
            ("text", "bg", 4.5),
            ("text", "surface", 4.5),
            ("text", "surface-elevated", 4.5),
            ("text-muted", "bg", 4.5),
            ("text-muted", "surface", 4.5),
            ("accent-fg", "accent", 4.5),
            ("accent", "surface", 3.0),
            ("success", "surface", 3.0),
            ("warning", "surface", 3.0),
            ("danger", "surface", 3.0),
        ]
        for p in palettes:
            for mode in ("light", "dark"):
                for fg, bg, min_req in pair_checks:
                    ratio = cc.wcag_contrast(p[mode][fg], p[mode][bg])
                    self.assertGreaterEqual(
                        ratio,
                        min_req,
                        f"Palette {p['id']} ({mode}) {fg}/{bg} contrast {ratio} < {min_req}",
                    )


class TestDesignSearchIntegrity(unittest.TestCase):
    def test_archetype_cross_references_and_queries(self):
        archetypes = json.loads((ROOT / "references/data/design_archetypes.json").read_text(encoding="utf-8"))
        palette_ids = {p["id"] for p in json.loads((ROOT / "references/data/palettes.json").read_text(encoding="utf-8"))}
        font_ids = {f["id"] for f in json.loads((ROOT / "references/data/font_pairings.json").read_text(encoding="utf-8"))}
        for arch in archetypes:
            for pid in arch["recommended_palettes"]:
                self.assertIn(pid, palette_ids)
            for fid in arch["recommended_fonts"]:
                self.assertIn(fid, font_ids)

        res = ds.query_design(surface="saas-app", query="healthcare accessibility", limit=1, include_anti_slop=True)
        self.assertEqual(res["archetypes"][0]["id"], "clinical-clarity")
        self.assertTrue(len(res["anti_slop_rules"]) >= 10)

        with self.assertRaises(ValueError):
            ds.query_design(palette_id="nonexistent-palette")


if __name__ == "__main__":
    unittest.main()
