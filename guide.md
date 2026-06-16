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
- Workspace for deep tasks (includes REST Explorer as a default tab)
- In-page overlays for contextual Salesforce actions

Data tooling to teach (v2.10.0)
- Teach these as data-management tasks, and always lead with the safety behavior: writes against a production org ask for confirmation first.
- CSV Import: Records > Import. Import a CSV into any SObject (Insert/Update/Upsert/Delete) with column mapping, a preview step, batched composite writes, per-row results, and a downloadable error-report CSV.
- Bulk grid actions: in the SOQL results grid, select rows for a mass Update/Set-null/Delete. Teach the requirement that the query include `Id`, and that the action is production-gated.
- Saved query library: in the SOQL and GraphQL builders, name/search/reload queries and export/import the library as JSON.
- Field fill-rate analyzer: Records > Fill Rate. Find unused fields on an SObject via batched COUNT() aggregates; results are sorted, filterable, and exportable.
- Permission set / profile comparison: Records > Security Manager > Compare. Diff object CRUD and field FLS between two permission sets or profiles.

LWC Explorer guidance
- Teach LWC Explorer as a page troubleshooting tool, not as raw framework noise.
- Use the live trace categories exactly as shown in product:
  - Apex
  - UI API
  - GraphQL
  - Fetch/API
  - Errors
- Explain that `Edit Code` and `Edit Apex` open the large in-overlay editor window directly from the explorer.
- Keep screenshots and walkthroughs consistent with the branded TrackForcePro headers used in the LWC Explorer, command palettes, and workspace surfaces.
- Teach the v2.10.0 in-page diagnostics as opt-in, on-demand chips built on the live network capture (a separate layer from the trace-filter chips above, which keep working unchanged). Stress that nothing runs until the user clicks a chip.
  - Performance Profiler: slowest Apex calls, N+1 detection, round-trip/type breakdown from captured traffic.
  - Capture -> Replay: open a captured call as an editable request in the REST/GraphQL/SOQL builder (session secrets stripped).
  - Errors -> Root Cause: correlate a failed page action to the failing Apex/UI API/GraphQL call, the triggering component, and the readable error body.
  - Explain this Page (X-Ray): inventory which components ran and the Apex/UI API/GraphQL/SOQL each invoked.
  - Flow & Automation trace (beta): which Flows ran on the interaction, with timing and faults. Label it beta.

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
