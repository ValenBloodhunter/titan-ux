"""Security containment, cross-agent wrapper integrity, and 5-axis routing tests."""
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import route_frontend as rf
import titan_core as tc


class TestSecurityAndWrappers(unittest.TestCase):
    def test_safe_path_blocks_escapes_and_reserved_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = tc.safe_path(root, "src/components/Button.tsx")
            self.assertEqual(valid, (root / "src/components/Button.tsx").resolve())

            for bad in ["../escape.tsx", "/etc/passwd", "C:\\Windows\\win.ini", ".git/config", "src/CON.tsx", "src/file "]:
                with self.assertRaises(ValueError, msg=f"Expected rejection for {bad}"):
                    tc.safe_path(root, bad)

            internal = tc.safe_path(root, ".titan-ux/titan-manifest.json", allow_internal_dir=True)
            self.assertTrue(internal.is_relative_to(root.resolve()))

    def test_safe_path_rejects_escaping_symlink_when_supported(self):
        with tempfile.TemporaryDirectory() as outer, tempfile.TemporaryDirectory() as inner:
            root = Path(inner)
            secret = Path(outer) / "secret.txt"
            secret.write_text("secret", encoding="utf-8")
            link_path = root / "leak.txt"
            try:
                os.symlink(secret, link_path)
            except OSError:
                self.skipTest("Symlink creation requires elevated privileges on this OS")
            with self.assertRaises(ValueError):
                tc.safe_path(root, "leak.txt")

    def test_routes_json_references_exist(self):
        cfg = tc.routes()
        playbooks_text = (ROOT / "references/command_playbooks.md").read_text(encoding="utf-8")
        for cmd, spec in cfg["commands"].items():
            self.assertIn(f"## {spec['playbook']}:", playbooks_text, f"Missing playbook section for {cmd}")
            for rel in [*spec["modules"], *spec["templates"]]:
                self.assertTrue((ROOT / rel).is_file(), f"Missing resource {rel}")
        for surf, spec in cfg["surfaces"].items():
            for rel in spec["conditional_modules"]:
                self.assertTrue((ROOT / rel).is_file(), f"Missing conditional module {rel} in {surf}")
        for stk, spec in cfg["stacks"].items():
            self.assertTrue((ROOT / spec["perf_module"]).is_file(), f"Missing perf module for {stk}")

    def test_cross_agent_wrapper_skills_are_valid(self):
        skills_dir = ROOT / "skills"
        wrapper_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
        self.assertEqual(len(wrapper_dirs), 11)
        playbooks = (ROOT / "references/command_playbooks.md").read_text(encoding="utf-8")
        for d in wrapper_dirs:
            skill_md = d / "SKILL.md"
            self.assertTrue(skill_md.is_file(), f"Missing {skill_md}")
            text = skill_md.read_text(encoding="utf-8")
            m = re.match(r"^---\n([\s\S]*?)\n---", text)
            self.assertIsNotNone(m, f"Missing YAML frontmatter in {skill_md}")
            fm = m.group(1)
            self.assertIn(f"name: {d.name}", fm)
            self.assertRegex(fm, r'description:\s*".+"')
            cmd_match = re.search(r"## (Command [A-K])", text)
            self.assertIsNotNone(cmd_match, f"Missing Command X target in {skill_md}")
            self.assertIn(f"## {cmd_match.group(1)}:", playbooks)


class TestFiveAxisRouting(unittest.TestCase):
    def test_progressive_loading_and_command_routing(self):
        disc = rf.plan_frontend_task("/titan-discover ./my-app")
        self.assertEqual(disc["command"], "discover")
        self.assertEqual(disc["resources"], [])

        motion = rf.plan_frontend_task("/titan-motion src/components/Popover.tsx")
        self.assertEqual(motion["command"], "motion")
        self.assertIn("references/modules/motion-engineering.md", motion["resources"])
        self.assertNotIn("references/modules/react-nextjs-perf.md", motion["resources"])

        build = rf.plan_frontend_task("/titan-build fintech treasury dashboard", stack="nextjs-app")
        self.assertEqual(build["command"], "build")
        self.assertEqual(build["surface"], "saas-app")
        self.assertEqual(build["density"], "compact")
        self.assertIn("references/modules/react-nextjs-perf.md", build["resources"])

        landing = rf.plan_frontend_task("Build an editorial product launch landing page", stack="astro")
        self.assertEqual(landing["surface"], "marketing-editorial")
        self.assertEqual(landing["motion_tier"], 2)
        self.assertEqual(landing["density"], "editorial")
        self.assertIn("references/modules/cwv-seo-resilience.md", landing["resources"])

    def test_invalid_or_conflicting_requests_raise(self):
        for bad in ["", "/unknown-cmd foo", "/titan-build", "/titan-architect"]:
            with self.assertRaises(ValueError):
                rf.plan_frontend_task(bad)
        with self.assertRaises(ValueError):
            rf.plan_frontend_task("/titan-discover app", surface="saas-app")


if __name__ == "__main__":
    unittest.main()
