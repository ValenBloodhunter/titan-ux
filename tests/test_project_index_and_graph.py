"""Project indexer and import/route/RSC dependency graph tests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import project_index as pi
import route_graph as rg


def _write(base: Path, rel: str, content: str):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


class TestProjectIndexAndGraph(unittest.TestCase):
    def test_nextjs_tailwind_v4_discovery_and_extract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "package.json", json.dumps({
                "dependencies": {"next": "15.1.0", "react": "19.0.0", "tailwindcss": "^4.0.0", "lucide-react": "^0.400.0"},
                "devDependencies": {"vitest": "^2.0.0"},
                "scripts": {"dev": "next dev", "build": "next build"},
            }))
            _write(root, "pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
            _write(root, "tsconfig.json", json.dumps({"compilerOptions": {"strict": True, "paths": {"@/*": ["./src/*"]}}}))
            _write(root, "src/app/globals.css", '@import "tailwindcss";\n:root { --bg: #fff; --text: #111; }\n.dark { --bg: #111; }\n@media (prefers-reduced-motion: reduce) {}')
            _write(root, "src/app/layout.tsx", "import { Plus_Jakarta_Sans } from 'next/font/google';\nexport default function RootLayout({children}: {children: React.ReactNode}) { return <html><body>{children}</body></html>; }")
            _write(root, "src/components/Button.tsx", "'use client';\nexport function Button() {\n  return <button type='button'>Save</button>;\n}\n")
            _write(root, "src/app/page.tsx", "import Link from 'next/link';\nimport { Button } from '@/components/Button';\nexport default function Home() { return <main><Link href='/settings'>Go</Link><Button /></main>; }")
            _write(root, "src/app/settings/page.tsx", "export default function Settings() { return <main>Settings</main>; }")

            idx = pi.discover_project(root)
            self.assertEqual(idx["stack"]["framework"], "nextjs-app")
            self.assertEqual(idx["stack"]["router"], "app-router")
            self.assertEqual(idx["stack"]["package_manager"], "pnpm")
            self.assertTrue(idx["stack"]["typescript_strict"])
            self.assertEqual(idx["styling"]["tailwind_version"], "v4")
            self.assertEqual(idx["styling"]["dark_mode_strategy"], "class-or-attr")
            self.assertTrue(idx["styling"]["has_reduced_motion_guard"])
            self.assertIn("Plus_Jakarta_Sans", idx["styling"]["detected_fonts"])
            self.assertIn("src/app/settings/page.tsx", idx["routes"])
            self.assertTrue((root / ".titan-ux/cache/index.json").is_file())

            # Cache hit check + targeted extract
            idx_cached = pi.discover_project(root)
            self.assertEqual(idx_cached["fingerprint"], idx["fingerprint"])
            snippet = pi.extract_lines(root, "src/components/Button.tsx", "1-3")
            self.assertIn("export function Button", snippet["content"])

            graph = rg.analyze_graph(root)
            self.assertEqual(graph["cycles"], [])
            self.assertEqual(graph["broken_imports"], [])
            self.assertEqual(graph["broken_routes"], [])
            self.assertEqual(graph["orphans"], [])
            self.assertEqual(graph["rsc_bleeds"], [])
            self.assertIn("flowchart TD", rg.to_mermaid(graph))

    def test_graph_detects_cycles_broken_links_orphans_and_rsc_bleed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/app/page.tsx", "import Link from 'next/link';\nexport default function Page() { return <Link href='/missing-page'>Bad</Link>; }")
            _write(root, "src/components/A.tsx", "import { B } from './B';\nexport const A = () => <B />;")
            _write(root, "src/components/B.tsx", "import { A } from './A';\nimport { Nope } from './missing-file';\nexport const B = () => <A />;")
            _write(root, "src/components/ClientLeak.tsx", "'use client';\nimport fs from 'fs';\nexport const ClientLeak = () => null;")

            graph = rg.analyze_graph(root)
            self.assertTrue(len(graph["cycles"]) >= 1)
            self.assertTrue(any(b["import"] == "./missing-file" for b in graph["broken_imports"]))
            self.assertTrue(any(r["href"] == "/missing-page" for r in graph["broken_routes"]))
            self.assertIn("src/components/ClientLeak.tsx", graph["orphans"])
            self.assertTrue(any(x["import"] == "fs" for x in graph["rsc_bleeds"]))


if __name__ == "__main__":
    unittest.main()
