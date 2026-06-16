Quick Guide - TrackForcePro

Install
1. Install TrackForcePro from the Chrome Web Store or Firefox Add-ons.
2. Open a logged-in Salesforce tab.
3. Open TrackForcePro from the browser toolbar.

Use the right surface
- Launcher popup: start fast, check org context, and open the right tool.
- Workspace: use for deep work like SOQL, GraphQL, REST Explorer, Records, Org Tools, and Settings.
- Salesforce page overlays: use Show All Data, TF Sidebar, Command Palette (Page), and Setup Search when current page context matters.

Command and search surfaces
- Launcher or workspace Command Palette: open it from the header trigger or your shortcut. In launcher popup mode, the browser may intercept `Ctrl/Cmd+K`.
- Command Palette (Page): use on Salesforce pages for context-aware actions.
- Setup Search (Page): use on Salesforce pages to search Setup navigation and metadata by API name.
- Metadata Explorer: use in the workspace when you need broader results and deeper follow-up actions.

Shortcuts
- Go to Settings -> General to customize shortcuts.
- Shortcut groups include main actions, page actions, workspace tabs, Records tools, and Org Tools panels.
- TF Sidebar defaults to `Ctrl/Cmd+Shift+S`.
- Show All Data, Command Palette (Page), and Setup Search (Page) are available to assign even when no default is set.

Daily wins
- Find a flow or permission set by API name from Setup Search.
- Inspect a record from the page with Show All Data.
- Test a Salesforce REST endpoint in REST Explorer with collections, chain mode, and cURL import.
- Import a CSV into any SObject from Records -> Import (Insert/Update/Upsert/Delete, with mapping, preview, and a production-write confirmation).
- Find unused fields on an SObject with Records -> Fill Rate, then export the result.
- Compare two permission sets or profiles from Records -> Security Manager -> Compare (object CRUD + field FLS diff).
- Save, search, and reload your common queries from the saved query library in the SOQL and GraphQL builders.
- Select rows in the SOQL results grid for a mass Update/Set-null/Delete (needs Id in the query; production-gated).
- Jump into workspace tools when the task becomes multi-step.

In-page diagnostics (LWC Explorer)
- Open the LWC Explorer overlay on a Salesforce page, then turn on the opt-in diagnostics chips (built on its live network capture).
- Performance Profiler: spot the slowest Apex and likely N+1 calls.
- Capture -> Replay: open a captured call as an editable request in the REST/GraphQL/SOQL builder (session secrets stripped).
- Errors -> Root Cause: trace a failed page action to the failing call, component, and readable error body.
- Explain this Page (X-Ray): see which components ran and the Apex/UI API/GraphQL/SOQL each invoked.
- Flow & Automation trace (beta): see which Flows ran, with timing and faults.

Version
- Keep this file aligned with the version shown in `manifest.json` and the public docs pages.
