# Architecture & Design Manifest Template (`.titan-ux/titan-manifest.json`)

Scaffolded via `scripts/scaffold_frontend.py --manifest` during `/titan-architect` and enforced by `/titan-build` and `/titan-verify`.

## Required Structure

```json
{
  "operation_id": "op-20261118-feature",
  "scope_locked": true,
  "feature_name": "Billing & Usage Workspace",
  "surface": "saas-app",
  "stack": "nextjs-app",
  "motion_tier": 1,
  "density": "compact",
  "archetype": "linear-precision",
  "palette_id": "slate-cobalt-pro",
  "font_pairing": "geist-mono-precision",
  "tokens_file": "src/app/globals.css",
  "allowed_files": [
    "src/app/globals.css",
    "src/components/ui/card.tsx",
    "src/components/billing/usage-chart.tsx",
    "src/app/settings/billing/page.tsx"
  ],
  "excluded_features": [
    "Custom PDF invoice designer",
    "Multi-currency tax engine"
  ],
  "component_dag": [
    {
      "id": "tokens",
      "path": "src/app/globals.css",
      "depends_on": [],
      "boundary": "shared",
      "required_states": ["light", "dark", "reduced-motion"]
    },
    {
      "id": "card-primitive",
      "path": "src/components/ui/card.tsx",
      "depends_on": ["tokens"],
      "boundary": "server",
      "required_states": ["default"]
    },
    {
      "id": "usage-chart",
      "path": "src/components/billing/usage-chart.tsx",
      "depends_on": ["card-primitive"],
      "boundary": "client",
      "required_states": ["loading", "empty", "error", "data"]
    },
    {
      "id": "billing-page",
      "path": "src/app/settings/billing/page.tsx",
      "depends_on": ["usage-chart"],
      "boundary": "server",
      "required_states": ["loading", "error", "not-found", "responsive"]
    }
  ],
  "verification_gates": [
    "verify_frontend.py --manifest",
    "route_graph.py --check-cycles --broken-links",
    "color_contrast.py --audit-css src/app/globals.css"
  ]
}
```
