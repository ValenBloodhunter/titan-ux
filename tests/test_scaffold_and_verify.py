"""Scaffolder, static quality verifier, and scoped --fix preservation tests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import color_contrast as cc
import scaffold_frontend as sf
import verify_frontend as vf


class TestScaffoldAndVerifier(unittest.TestCase):
    def test_scaffold_tokens_passes_css_contrast_audit_across_all_palettes(self):
        palettes = json.loads((ROOT / "references/data/palettes.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for idx, p in enumerate(palettes):
                out = root / f"tokens-{idx}.css"
                css = sf.render_tokens_css(p["id"], mode="tailwind-v4" if idx % 2 == 0 else "css")
                out.write_text(css, encoding="utf-8")
                report = cc.audit_css_tokens(out)
                self.assertEqual(report["failures"], [], f"Contrast failure in generated CSS for {p['id']}: {report['failures']}")
                self.assertGreater(report["checked_pairs"], 10)

    def test_verifier_catches_slop_a11y_motion_perf_and_responsive_bugs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad_tsx = root / "src/components/BadCard.tsx"
            bad_tsx.parent.mkdir(parents=True)
            bad_tsx.write_text(
                "'use client';\n"
                "import * as three from 'three';\n"
                "import { LineChart } from 'recharts';\n"
                "export function BadCard({ items }: { items: string[] }) {\n"
                "  return (\n"
                "    <div className='min-h-screen bg-[#112233] transition-all duration-500' onClick={() => {}}>\n"
                "      <img src='/hero.png' />\n"
                "      <input placeholder='Email' />\n"
                "      <button className='outline-none'><svg /></button>\n"
                "      <a href='https://example.com' target='_blank'>External</a>\n"
                "      {items.map((x, idx) => <span key={idx}>{x}</span>)}\n"
                "    </div>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )
            bad_css = root / "src/styles/bad.css"
            bad_css.parent.mkdir(parents=True)
            bad_css.write_text(
                ".box { transition: width 450ms ease; height: 100vh; }\n"
                ".btn:focus { outline: none; }\n"
                "@keyframes slide { from { left: 0; } to { left: 100px; } }\n",
                encoding="utf-8",
            )

            report = vf.verify_files(root, [bad_tsx, bad_css])
            codes = {i["code"] for i in report["issues"]}
            expected = {
                "SLOP_RAW_COLOR",
                "SLOP_TRANSITION_ALL",
                "A11Y_DIV_ONCLICK",
                "A11Y_MISSING_ALT",
                "A11Y_UNLABELED_INPUT",
                "A11Y_OUTLINE_NONE",
                "A11Y_ICON_BUTTON_LABEL",
                "A11Y_BLANK_TARGET_UNSAFE",
                "MOTION_SLOW_UI",
                "MOTION_LAYOUT_ANIM",
                "MOTION_MISSING_REDUCED",
                "PERF_INDEX_KEY",
                "PERF_IMG_NO_DIMENSIONS",
                "RESP_100VH",
            }
            self.assertTrue(expected.issubset(codes), f"Missing expected codes: {expected - codes}")

    def test_scoped_fix_preserves_unrelated_files_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unrelated = root / "src/legacy.tsx"
            unrelated.parent.mkdir(parents=True)
            legacy_bytes = b"export const Legacy = () => <div className='min-h-screen'><a href='https://x.test' target='_blank'>X</a></div>;\n"
            unrelated.write_bytes(legacy_bytes)

            target = root / "src/NewLink.tsx"
            target.write_text(
                "export function NewLink() {\n"
                "  return (\n"
                "    <main className='min-h-screen'>\n"
                "      <a href='https://docs.example.com' target='_blank'>Docs</a>\n"
                "    </main>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )

            report = vf.verify_files(root, [target], fix=True)
            self.assertEqual(report["fixed_files"], ["src/NewLink.tsx"])
            self.assertEqual(report["error_count"], 0)
            self.assertEqual(report["warning_count"], 0)
            self.assertIn('rel="noopener noreferrer"', target.read_text(encoding="utf-8"))
            self.assertIn("min-h-dvh", target.read_text(encoding="utf-8"))
            self.assertEqual(unrelated.read_bytes(), legacy_bytes)


if __name__ == "__main__":
    unittest.main()
