# TrackForcePro Documentation Mismatch Report

**Generated:** 2026-03-30 | **Product Version:** v2.1.7

## Critical Discrepancies

### 1. Audit Trail Mode Category (HIGH)

- **Docs claim:** guides/index.html lists Audit Trail under "Explore: Query & Data Tools"
- **Reality:** Audit Trail is in **Analyze** mode (green), mapped via `MODE_VIEW_MAP` → analyze.audit → tab: sf
- **Fix:** Move Audit Trail card to Analyze section in guides/index.html

### 2. Show All Data Default Shortcut (HIGH)

- **Docs claim:** quick-start-guide.html and guide.html reference `Ctrl+Shift+D` as the Show All Data shortcut
- **Reality:** Show All Data has **no default shortcut** — it must be configured in Settings → General → Keyboard
  Shortcuts. The only built-in shortcut is `Ctrl+Shift+S` (sidebar toggle)
- **Fix:** Correct all shortcut references; note that it's configurable, not default

### 3. Command Palette Shortcut (MEDIUM)

- **Docs claim:** `Ctrl+K` is the Command Palette shortcut
- **Reality:** `Ctrl+K` is handled in content.js but the manifest.json command has no suggested key. The in-popup
  palette uses Ctrl+K. This works but is not a browser-level `chrome.commands` shortcut
- **Fix:** Clarify that Ctrl+K works on Salesforce pages and in the workspace, but browsers may intercept it

### 4. Settings > Privacy & Data (HIGH)

- **Docs claim:** privacy-policy.html references "Settings > General > Privacy & Data"
- **Reality:** This section **does not exist**. Settings has 6 sub-tabs: Org Management, Appearance, General, Sidebar,
  Layout, Backup
- **Fix:** Remove the incorrect settings path reference

### 5. "TF Sidebar" Naming (MEDIUM)

- **Docs claim:** Multiple pages use "TF Sidebar"
- **Reality:** The UI labels it "TrackForcePro Quick Access" (aria-label) and "TrackForcePro" (header). No "TF Sidebar"
  label exists in the product
- **Fix:** Standardize to "Sidebar" throughout docs (matches CLAUDE.md convention)

### 6. Feature Guide Hub Wrong Sections (MEDIUM)

- **Docs claim:** guides/index.html organizes features into Explore / Analyze / In-Page Tools / Help
- **Reality:** Missing Debug mode entirely. Audit Trail in wrong section. Platform Events should be under Debug, not
  Analyze
- **Fix:** Restructure to match actual 3-mode architecture

## Minor Discrepancies

### 7. "Data Explorer" References

- Some docs still reference "Data Explorer" — renamed to "Records" in v1.8.0
- Found in: guide.html (training guide), some guide pages

### 8. UX Analysis Document

- `ux-analysis-tab-reorganization.html` is a v1.9.0 design proposal — changes were implemented in v1.8.0
- This is an internal planning doc, not user-facing documentation
- **Recommendation:** Remove from public docs nav or archive clearly

### 9. Context Menu Items

- Docs reference 5 items (Show All Data, Field History, Sharing, SOQL Builder, Copy Record ID)
- Code confirms 5 items: Open in SOQL Builder, Show All Data, View Field History, Check Sharing, Copy Record ID
- Naming slightly inconsistent but functionally correct

### 10. Org Tools Panel Labels

- Code uses short labels: Login As, Labels, Deployments, Scheduled, Debug Logs, Limits, Admin
- Docs use longer names: Custom Labels, Scheduled Jobs, Org Limits, Admin Utils
- Both are correct (short = UI tab label, long = full name)

## Sections to Remove

1. `ux-analysis-tab-reorganization.html` — internal design doc, not user documentation

## Sections Verified as Correct

- SOQL Builder guide (comprehensive, accurate)
- Privacy policy (mostly accurate, one settings path fix needed)
- Quiz content (no deprecated feature references found)
- Leaderboard (functional, current)
- All 7 Org Tools panel names confirmed
- LMS Beta status confirmed in code
- Browser support info confirmed (Chrome 88+, Edge 88+, Firefox 109+, Opera 74+)

## Validated Shortcuts (Source of Truth)

### Built-in Default

| Shortcut     | Action         | Platform  |
|--------------|----------------|-----------|
| Ctrl+Shift+S | Toggle Sidebar | Win/Linux |
| Cmd+Shift+S  | Toggle Sidebar | macOS     |

### Works by Default (code-level, not chrome.commands)

| Shortcut               | Action                | Context                  |
|------------------------|-----------------------|--------------------------|
| Ctrl+K / Cmd+K         | Command Palette       | On SF pages + workspace  |
| Ctrl+Enter / Cmd+Enter | Execute query/request | SOQL, GraphQL, REST      |
| Escape                 | Close any overlay     | Sidebar, palette, panels |

### Configurable (no default — must set in Settings)

| Action                   | Storage            |
|--------------------------|--------------------|
| Toggle Show All Data     | tfpCustomShortcuts |
| Toggle LWC Explorer      | tfpCustomShortcuts |
| Open SOQL Builder        | tfpCustomShortcuts |
| Open GraphQL Builder     | tfpCustomShortcuts |
| Open Setup Search        | tfpCustomShortcuts |
| Jump to any tab          | tfpCustomShortcuts |
| Jump to any subtab/panel | tfpCustomShortcuts |

### Editor-Specific

| Shortcut       | Action          | Context        |
|----------------|-----------------|----------------|
| Ctrl+B / Cmd+B | Format query    | GraphQL editor |
| Shift+Enter    | Format query    | GraphQL editor |
| Ctrl+S / Cmd+S | Save request    | REST Explorer  |
| Ctrl+L / Cmd+L | Focus URL input | REST Explorer  |
