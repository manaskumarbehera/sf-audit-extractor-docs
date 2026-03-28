# TrackForcePro: UI Architecture Strategy

## 1. Current State Analysis

### popup.html: 6,403 Lines, 9 Tabs

| Tab | Lines | Size | Complexity |
|-----|-------|------|------------|
| Audit Trails | 180–258 | 79 lines | Low — simple filter + log container |
| Platform Events | 260–346 | 87 lines | Low — event list + subscription form |
| **SOQL Builder** | 348–845 | **498 lines** | High — split view, builder, results |
| **GraphQL Builder** | 847–1499 | **653 lines** | High — 3 screens, split editors, pagination |
| **REST Explorer** | 1501–1970 | **470 lines** | High — sidebar, editor tabs, response viewer |
| Records | 1972–3044 | 1,073 lines | Very High — 6 sub-tabs, modals |
| Org Tools | 3047–3657 | 611 lines | High — 7 toggle panels |
| Org & Favicon | 3660–4087 | 428 lines | Medium — form-heavy |
| Settings | 4089–6097 | **2,009 lines** | Very High — 8 sections, org table, shortcuts |
| Help | 6098–6297 | 200 lines | Low — static content |

**Shared elements** (outside tab panels): header/nav (lines 1–128), command palette (130–177), footer (6363–6373), modals (6298–6361), scripts (6376–6402).

### Problems

1. **Unmanageable file size.** At 6,403 lines, popup.html is impossible to review in a single PR. Finding a specific element requires line-range knowledge.

2. **Merge conflicts.** Any two developers touching different tabs edit the same file, causing frequent conflicts.

3. **No separation of concerns.** Tab HTML, shared modals, script tags, and structural layout all live in one file.

4. **Accessibility gaps.** Many interactive regions lack ARIA roles. Buttons missing `aria-label`. Tab panels not properly linked to their tab buttons via `aria-controls`. No `role="toolbar"` on action bars.

5. **Inconsistent patterns.** Some tabs use `<section>` with headings, others use bare `<div>`. Some buttons have `aria-label`, others rely on emoji-only text. Filter bars inconsistently use `role="search"`.

---

## 2. Modular Template Architecture

### Strategy: Build-Time Composition

Each tab is extracted into its own HTML template file. A Node.js build script (`scripts/compose-popup.cjs`) reads a shell file (`popup-shell.html`) and replaces `{{TAB_*}}` placeholders with template contents, producing the final `popup.html`.

**Why build-time over dynamic rendering:**
- Zero runtime cost — no JS needed to load tab HTML
- No flash of empty content on tab switch
- Works with existing `<script>` loading order (IIFEs query DOM at load time)
- `getElementById` works immediately — no race conditions
- Extension CSP compliant — no `fetch()` for local HTML needed
- Build script validates ID uniqueness across all templates

### File Structure

```
templates/
├── tab-soql.html          ✅ Created (330 lines)
├── tab-graphql.html       ✅ Created (305 lines)
├── tab-rest.html          ✅ Created (268 lines)
├── tab-records.html       ⬜ Future (1,073 lines)
├── tab-orgtools.html      ⬜ Future (611 lines)
├── tab-orgfavicon.html    ⬜ Future (428 lines)
├── tab-settings.html      ⬜ Future (2,009 lines)
├── tab-audit.html         ⬜ Future (79 lines)
├── tab-platform.html      ⬜ Future (87 lines)
└── tab-help.html          ⬜ Future (200 lines)

scripts/
└── compose-popup.cjs      ✅ Created — build-time HTML composition

popup-shell.html           ⬜ Future — popup.html with placeholders
popup.html                 Output — generated from shell + templates
```

### popup-shell.html Structure

```html
<!doctype html>
<html lang="en">
<head>...</head>
<body>
  <div class="container">
    <header>...</header>           <!-- Nav tabs, brand, status -->
    <div id="command-palette">...</div>  <!-- Command palette dialog -->

    <section class="tab-contents">
      <!-- Inline: small tabs that don't benefit from extraction -->
      <div id="tab-sf">...</div>       <!-- Audit: 79 lines -->
      <div id="tab-platform">...</div> <!-- Platform: 87 lines -->

      <!-- Composed: large tabs injected at build time -->
      {{TAB_SOQL}}
      {{TAB_GRAPHQL}}
      {{TAB_REST}}
      {{TAB_RECORDS}}
      {{TAB_ORGTOOLS}}
      {{TAB_ORGFAVICON}}
      {{TAB_SETTINGS}}
      {{TAB_HELP}}
    </section>

    <!-- Shared modals -->
    <div id="pe-publish-modal">...</div>

    <footer>...</footer>
  </div>
  <!-- Scripts -->
</body>
</html>
```

### Build Integration

Add to `package.json`:

```json
{
  "scripts": {
    "compose": "node scripts/compose-popup.cjs",
    "prepackage": "npm run compose && npm run build:graphql"
  }
}
```

The composition runs before packaging, producing the final `popup.html` that gets bundled into browser ZIPs.

---

## 3. Template Conventions

### Each Template Must:

1. **Be a self-contained tab panel** — root element is `<div id="tab-{name}" class="tab-pane" ...>`
2. **Include a file header comment** with source line range and build-time inclusion note
3. **Use semantic sections** — `<section aria-labelledby="...">` for major regions
4. **Add sr-only headings** — `<h2 class="sr-only">` or `<h3 class="sr-only">` for screen readers
5. **Apply ARIA roles** — `role="toolbar"` on action bars, `role="search"` on filter inputs, `role="tablist"` on sub-tabs
6. **Mark decorative content** — `aria-hidden="true"` on emoji icons and separators
7. **No inline styles except `display: none`** for initially hidden panels
8. **No `<script>` tags** — JS stays in dedicated `.js` files loaded from popup-shell.html

### ID Naming Convention

All element IDs within a tab are prefixed with the tab name:

| Tab | ID Prefix | Example |
|-----|-----------|---------|
| SOQL | `soql-` | `soql-run`, `soql-query`, `soql-results` |
| GraphQL | `graphql-` | `graphql-run`, `graphql-query`, `graphql-results` |
| REST | `rest-` | `rest-send-btn`, `rest-url-input` |
| Records | `de-` or `data-` | `de-search`, `data-sub-tabs` |
| Org Tools | `orgtools-` | `orgtools-limits-panel` |
| Settings | `settings-` | `settings-theme-select` |

This prevents ID collisions when templates are composed into one file.

---

## 4. Accessibility Improvements

### Changes Applied in Extracted Templates

| Pattern | Before | After |
|---------|--------|-------|
| Action bars | `<div class="actions">` | `<div role="toolbar" aria-label="...">` |
| Filter inputs | `<input placeholder="Search...">` | `<div role="search"><input aria-label="...">` |
| Split views | `<div class="split">` | `<div aria-roledescription="split view">` |
| Splitters | `<div class="splitter">` | `<div role="separator" aria-orientation="vertical">` |
| Tab panels | Missing `role="tabpanel"` | Added `role="tabpanel"` with `aria-label` |
| Grouped controls | Loose checkboxes | `<fieldset><legend class="sr-only">` |
| Keyboard shortcuts | Undiscoverable | `aria-keyshortcuts="Control+Enter"` |
| Emoji icons | Read aloud by screen readers | `aria-hidden="true"` on decorative spans |
| Section headings | None | `<h2 class="sr-only">` for each major section |
| Status regions | `<span>` | `role="status"` or `aria-live="polite"` |
| Modal dialogs | `aria-label="..."` | `aria-labelledby="..."` pointing to visible title |

### Remaining Gaps (Future Work)

- Tab buttons in header need `aria-controls` pointing to their panel ID
- Focus management on tab switch (focus first interactive element)
- Escape key handling for all dropdown menus
- `aria-activedescendant` for virtual table keyboard navigation
- High contrast mode CSS variables

---

## 5. Migration Plan

### Phase 1: Three Query Tabs (Current)

| Deliverable | Status | Lines Extracted |
|-------------|--------|----------------|
| `templates/tab-soql.html` | ✅ Complete | 498 → 330 (accessibility-enhanced) |
| `templates/tab-graphql.html` | ✅ Complete | 653 → 305 (accessibility-enhanced) |
| `templates/tab-rest.html` | ✅ Complete | 470 → 268 (accessibility-enhanced) |
| `scripts/compose-popup.cjs` | ✅ Complete | Build script with validation |

**Impact:** 1,621 lines extracted from popup.html into maintainable, reviewable templates.

### Phase 2: Heavy Tabs

| Template | Priority | Lines | Rationale |
|----------|----------|-------|-----------|
| `tab-settings.html` | 🔴 High | 2,009 | Largest tab, most merge conflicts |
| `tab-records.html` | 🔴 High | 1,073 | 6 sub-tabs, highest complexity |
| `tab-orgtools.html` | 🟡 Medium | 611 | 7 panel toggles |
| `tab-orgfavicon.html` | 🟡 Medium | 428 | Form-heavy |

**Impact:** 4,121 additional lines extracted.

### Phase 3: Small Tabs + Shell

| Template | Priority | Lines |
|----------|----------|-------|
| `tab-help.html` | 🟢 Low | 200 |
| `tab-platform.html` | 🟢 Low | 87 |
| `tab-audit.html` | 🟢 Low | 79 |
| `popup-shell.html` | 🟢 Low | ~400 (header + footer + scripts) |

**Impact:** Full extraction. popup.html becomes a build artifact, not a source file.

### Migration Checklist (Per Tab)

1. Copy tab HTML from popup.html to `templates/tab-{name}.html`
2. Add file header comment with source line range
3. Add semantic `<section>` wrappers and sr-only headings
4. Add ARIA roles (`toolbar`, `search`, `tablist`, `separator`)
5. Add `aria-hidden="true"` to decorative content
6. Add `fieldset/legend` for grouped controls
7. Add placeholder to TEMPLATE_MAP in `compose-popup.cjs`
8. Run `node scripts/compose-popup.cjs --dry-run` to verify no duplicate IDs
9. Diff generated output against original popup.html
10. Run full test suite: `npm test`

---

## 6. Build Script Features

### `scripts/compose-popup.cjs`

| Feature | Description |
|---------|-------------|
| **Zero dependencies** | Uses only Node.js built-ins (fs, path) |
| **Indent preservation** | Detects placeholder indentation and applies to injected content |
| **Unresolved placeholder warning** | Reports any `{{TAB_*}}` tokens not found in TEMPLATE_MAP |
| **Duplicate ID detection** | Scans composed output for duplicate `id="..."` values |
| **Size reporting** | Logs shell size, template sizes, and total output size |
| **Dry-run mode** | `--dry-run` prints to stdout instead of writing file |
| **Custom output** | `--out path/to/file` writes to a different location |
| **Progressive adoption** | Templates not yet in TEMPLATE_MAP stay inline in the shell |

### Usage

```bash
# Compose and write to popup.html
node scripts/compose-popup.cjs

# Preview without writing
node scripts/compose-popup.cjs --dry-run

# Write to a different file
node scripts/compose-popup.cjs --out dist/popup.html

# Skip validation
node scripts/compose-popup.cjs --no-validate
```

---

## 7. Comparison: Before and After

### Before (popup.html monolith)

```
popup.html — 6,403 lines
├── Header + nav (128 lines)
├── Command palette (50 lines)
├── Audit tab (79 lines)
├── Platform Events tab (87 lines)
├── SOQL tab (498 lines)         ← buried at line 348
├── GraphQL tab (653 lines)      ← starts at line 847
├── REST tab (470 lines)         ← starts at line 1501
├── Records tab (1,073 lines)    ← starts at line 1972
├── Org Tools tab (611 lines)
├── Org & Favicon tab (428 lines)
├── Settings tab (2,009 lines)   ← 31% of the file
├── Help tab (200 lines)
├── Shared modals (65 lines)
├── Footer (12 lines)
└── Script tags (28 lines)
```

**Problems:** One person editing Settings conflicts with someone editing SOQL. PR reviewers must scan 6,403 lines. No way to review a tab in isolation.

### After (modular templates)

```
popup-shell.html — ~400 lines (header, nav, shared, footer, scripts)
templates/
├── tab-soql.html — 330 lines      ← self-contained, reviewable
├── tab-graphql.html — 305 lines   ← self-contained, reviewable
├── tab-rest.html — 268 lines      ← self-contained, reviewable
├── tab-records.html — ~1,000 lines (future)
├── tab-settings.html — ~1,900 lines (future)
└── ... (6 more)

scripts/compose-popup.cjs          ← build-time assembly
popup.html                         ← generated output (not edited directly)
```

**Benefits:** Each tab is a separate file. PRs touch only the relevant template. Accessibility improvements are per-tab reviewable. Build script catches ID collisions automatically.

---

## 8. Files Produced

| File | Lines | Purpose |
|------|-------|---------|
| `templates/tab-soql.html` | 330 | SOQL Builder tab with full ARIA improvements |
| `templates/tab-graphql.html` | 305 | GraphQL Builder tab with semantic sections |
| `templates/tab-rest.html` | 268 | REST Explorer tab with tablist/tabpanel ARIA |
| `scripts/compose-popup.cjs` | 165 | Build-time HTML composition with validation |
| `UI_ARCHITECTURE_STRATEGY.md` | — | This document |

---

## 9. Recommended Next Steps

1. **Create `popup-shell.html`** — Copy popup.html, replace the three extracted tabs (lines 348–845, 846–1499, 1500–1970) with `{{TAB_SOQL}}`, `{{TAB_GRAPHQL}}`, `{{TAB_REST}}` placeholders. Run `compose-popup.cjs` and diff against original to verify zero functional change.

2. **Add `npm run compose` to CI** — Ensure the build script runs in the GitHub Actions workflow before packaging.

3. **Extract Settings tab next** — At 2,009 lines (31% of the file), this is the highest-value extraction. Consider splitting into sub-templates: `tab-settings-general.html`, `tab-settings-appearance.html`, `tab-settings-org.html`.

4. **Extract Records tab** — At 1,073 lines with 6 sub-tabs, this benefits from per-sub-tab templates.

5. **Add `aria-controls` to header tab buttons** — Each `<button data-tab="soql">` should have `aria-controls="tab-soql"`.

6. **Add focus management** — When switching tabs, focus the first interactive element in the newly visible panel.

7. **Add `.gitattributes`** — Mark `popup.html` as generated: `popup.html linguist-generated=true` to exclude it from PR diffs.
