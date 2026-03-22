TrackForcePro Docs Guide

This Markdown file is the maintenance companion for the public docs in `docs/`.

Core docs pages
- `index.html` - landing page and product story
- `quick-start-guide.html` - first-run onboarding
- `guide.html` - trainer-facing learning path
- `documentation.html` - feature reference
- `help.html` - FAQ and troubleshooting
- `quiz.html` - learner reinforcement
- `privacy-policy.html` - legal and trust information

Current product model to teach
- Launcher popup for quick entry
- Workspace for deep tasks
- In-page overlays for contextual Salesforce actions

Command and search language rules
- Do not teach `Ctrl/Cmd+K` as guaranteed inside popup mode.
- Prefer: "Open the Command Palette from the header trigger or your shortcut; in launcher popup mode the browser may intercept Ctrl/Cmd+K."
- Distinguish clearly between:
  - launcher/workspace Command Palette
  - Command Palette (Page)
  - Setup Search (Page)
  - Metadata Explorer in the workspace

Shortcut documentation rules
- Use `Settings > General` as the shortcut settings path.
- Do not describe shortcuts as only a 3-action model.
- Reflect the grouped shortcut model:
  - main actions
  - page actions
  - workspace tabs
  - Records tools
  - Org Tools panels

Docs sync workflow
1. Update `manifest.json` version if this is a release change.
2. Run `node scripts/update-docs-version.js`.
3. Review all docs language that mentions shortcuts, surfaces, or setup flows.
4. Update `DOCUMENTATION/CHANGELOG.md` if the docs or training model changed materially.

Trainer review checklist
- Does the page teach the correct surface first?
- Does it describe popup/workspace/page actions accurately?
- Does shortcut guidance match the live Settings UI?
- Does it avoid promising browser-intercepted shortcuts as guaranteed?
- Does it help the user choose between Setup Search and Metadata Explorer?
