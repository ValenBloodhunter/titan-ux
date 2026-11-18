"""End-to-end Titan-UX pipeline integration test (discover -> architect -> tokens -> build -> verify)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import color_contrast as cc
import project_index as pi
import route_frontend as rf
import route_graph as rg
import scaffold_frontend as sf
import verify_frontend as vf


class TestEndToEndPipeline(unittest.TestCase):
    def test_full_end_to_end_nextjs_feature_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(json.dumps({
                "dependencies": {"next": "15.1.0", "react": "19.0.0", "tailwindcss": "^4.0.0"}
            }), encoding="utf-8")
            (root / "tsconfig.json").write_text(json.dumps({
                "compilerOptions": {"strict": True, "paths": {"@/*": ["./src/*"]}}
            }), encoding="utf-8")

            # Step 1: Discover & Route
            idx = pi.discover_project(root)
            self.assertEqual(idx["stack"]["framework"], "nextjs-app")
            plan = rf.plan_frontend_task("/titan-build billing usage dashboard", stack="nextjs-app")
            self.assertEqual(plan["surface"], "saas-app")

            # Step 2: Architect manifest lock
            self.assertEqual(
                sf.main([
                    "manifest", str(root),
                    "--feature", "Billing Usage",
                    "--surface", "saas-app",
                    "--stack", "nextjs-app",
                    "--palette", "porcelain-teal-ledger",
                    "--tokens-file", "src/app/globals.css",
                    "--files", "src/components/billing/UsageSummary.tsx", "src/app/billing/page.tsx",
                ]),
                0,
            )

            # Step 3: Tokens generation
            self.assertEqual(
                sf.main([
                    "tokens", str(root),
                    "--palette", "porcelain-teal-ledger",
                    "--mode", "tailwind-v4",
                    "--output", "src/app/globals.css",
                ]),
                0,
            )

            # Step 4: Build components & pages sequentially without stubs
            comp = root / "src/components/billing/UsageSummary.tsx"
            comp.parent.mkdir(parents=True, exist_ok=True)
            comp.write_text(
                "'use client';\n"
                "import * as React from 'react';\n"
                "export interface UsageSummaryProps { invoicesCount: number; totalCents: number; }\n"
                "export function UsageSummary({ invoicesCount, totalCents }: UsageSummaryProps) {\n"
                "  return (\n"
                "    <section className='rounded-lg border border-border bg-surface p-6 text-text'>\n"
                "      <h2 className='text-lg font-semibold'>Monthly Usage</h2>\n"
                "      <p className='mt-2 text-2xl font-semibold tabular-nums'>${(totalCents / 100).toFixed(2)}</p>\n"
                "      <p className='mt-1 text-sm text-text-muted'>{invoicesCount} settled invoices</p>\n"
                "    </section>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )

            page = root / "src/app/billing/page.tsx"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(
                "import { UsageSummary } from '@/components/billing/UsageSummary';\n"
                "export default function BillingPage() {\n"
                "  return (\n"
                "    <main id='main-content' className='min-h-dvh bg-bg p-6 text-text'>\n"
                "      <h1 className='text-2xl font-bold tracking-tight'>Billing &amp; Usage</h1>\n"
                "      <UsageSummary invoicesCount={14} totalCents={42800} />\n"
                "    </main>\n"
                "  );\n"
                "}\n",
                encoding="utf-8",
            )

            # Step 5: Verify manifest, static rules, contrast, and dependency/route graph
            self.assertEqual(vf.main([str(root), "--manifest", ".titan-ux/titan-manifest.json"]), 0)
            self.assertEqual(rg.main([str(root), "--check-cycles", "--broken-links", "--rsc-bleed"]), 0)
            self.assertEqual(cc.main(["audit-css", str(root / "src/app/globals.css")]), 0)


if __name__ == "__main__":
    unittest.main()
