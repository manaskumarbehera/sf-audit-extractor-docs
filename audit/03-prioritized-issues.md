# 03 — Prioritized Issue Register

Source: parallel static audit by 6 specialists (SOQL, GraphQL, UX/a11y, SF API/security, code-quality, adoption), each finding ground-truthed against the actual code before inclusion.

**Priority score = User impact × Frequency × Confidence ÷ Effort** (each input 1–5).

> **Ground-truthing changed conclusions.** Two auditor claims were rejected as false positives, and one auditor's *proposed fix was wrong*. See "Rejected / corrected" at the bottom — this is why findings were verified before any edit.

## Fixed this pass (highest-scoring, verified, tested)

| ID | Area | Issue | Type | Sev | Score | Status |
|----|------|-------|------|-----|-------|--------|
| Q1 | SOQL composer | `quoteSoqlValue` escaped quotes but **not backslashes** → a value ending in `\` (e.g. `C:\`) produced an unterminated, invalid, injectable string literal | bug | P1 | **100** | ✅ Fixed `d9eba9a` |
| Q2 | SOQL composer | Child-subquery filters emitted `IN/NOT IN/INCLUDES/EXCLUDES` values as one quoted string instead of a parenthesized list → invalid SOQL | bug | P1 | **37.5** | ✅ Fixed `d9eba9a` |
| Q3 | SOQL composer | Child-subquery filters emitted `= NULL` / `!= NULL` literally instead of `IS NULL` / `IS NOT NULL` → invalid SOQL | bug | P1 | **40** | ✅ Fixed `d9eba9a` |
| C1 | LWC Explorer | Escape-to-close `keydown` listener re-added on every open, removed only on Escape → unbounded listener leak across open/close cycles | perf | P2 | **60** | ✅ Fixed `d968481` |
| X1 | SOQL builder | Object-selector dropdown wrote unescaped object name into `innerHTML` for `<mark>` highlighting (rule violation; low exploitability) | security | P2 | 8 | ✅ Fixed `5ec3316` |

All five have regression coverage (Q1–Q3 via 4 new composer tests; C1 behavior covered by existing LWC suite; X1 path is a 1-line defensive escape).

## Recommended next iteration (verified real, larger effort — not done this pass)

| ID | Area | Issue | Type | Sev | Score | Notes |
|----|------|-------|------|-----|-------|-------|
| R1 | SF API / SOQL | Session-expiry shows technical "not connected" with no in-UI **Reconnect** action; user must guess to refresh the SF tab | ux | P2 | 16 | Highest-value adoption item. Add a Reconnect button that refreshes the SF tab and re-runs. Effort 3. |
| R2 | GraphQL | Field-introspection / schema-load failure shows "Could not load fields" with **no Retry** and no guidance | missing-guidance | P2 | 24 | Add Retry + "check the object exists / you have access". Effort 2. |
| R3 | Data Explorer | Record-lookup failures (404 / no access / network) surface **no error toast** — input just clears | ux | P2 | ~18 | Wrap `describeRecord()` and toast a plain-language error. Effort 2. |
| R4 | GraphQL | Update/Create mutation variable types hardcoded to `String` — wrong for Boolean/number/date fields → API type-mismatch | missing-guidance | P2 | 12 | Infer type from describe, or use a JSON scalar. Effort 3. |
| R5 | GraphQL | Introspection cache not scoped by org/API version → stale field suggestions after org switch ("Cannot query field X") | bug | P2 | 8 | Scope cache key `orgId_apiVersion_sobject`; clear on org change. Effort 2. |
| R6 | SF API | No API-version negotiation: if org < configured version, query fails with no auto-downshift offer | code-quality | P2 | ~7 | Detect org `ApiVersion`; retry lower on "version not supported". Effort 3. (Note: e9ec06f already downshifts on run errors — extend it.) |
| R7 | SOQL builder | Initial empty state shows "No records found" before any query has run — doesn't teach how to start | missing-guidance | P2 | 12 | Distinguish initial vs no-results empty states. Effort 2. |
| U1 | UX/a11y | Settings drawer doesn't move focus to first control on open (WCAG 3.2.1) | ux | P2 | 12 | Focus first control on open; restore on close. Effort 2. |
| U2 | UX/a11y | Onboarding Skip/Escape leaves focus orphaned | a11y | P3 | ~12 | Return focus to active tab on dismiss. Effort 1. |
| U3 | UX/a11y | REST Explorer URL input has no `aria-label` (placeholder only) | a11y | P3 | ~40 | Add `aria-label`. Effort 1. (Cheap; good quick win next.) |
| P1 | popup.js | Command-palette onclick closes over a stale `filtered` array → wrong command on rapid type+click | bug | P2 | 12 | Use dataset command-id lookup, not closure index. Effort 2. |
| D1 | Data Explorer / SOQL | Record IDs interpolated into WHERE clauses without escaping across helper files (latent — SF IDs are `[A-Za-z0-9]`, not currently exploitable) | security | P1* | 20 | Defensive: route all ID interpolation through a shared `quoteSoqlValue`. Effort 2. *Severity reflects defensive hardening, not an active break. |
| G1 | GraphQL | Object/field/mutation identifiers interpolated without `^[A-Za-z_][A-Za-z0-9_]*$` validation (names come from describe, so low real risk) | code-quality | P2/P3 | ~10 | Add `validateMutationState` identifier checks + an `escapeGraphQLIdentifier`. Effort 2. |
| S1 | SOQL builder | Suggestion panel async describe can render stale field list on fast object/tab switches (`panelUpdateSeq` not re-checked at render) | bug | P2 | ~12 | Thread seq into `renderFieldList` and bail if advanced. Effort 2. |

Plus lower-priority polish (P3): SOQL OR-condition grouping (missing-feature), GraphQL double-space when pageInfo disabled, audit-trail `LAST_N_DAYS` boundary drift, filter/subquery count badges, GraphQL mutation empty-state guidance.

## Rejected / corrected during ground-truthing

- **Rejected (false positive):** "XSS in `highlightLwcSearchText`" (content_lwc_explorer.js:642) — the function **already** escapes via `escapeHtml(text).replace(...)`. Safe.
- **Corrected fix:** The SOQL escaping finding (Q1) proposed switching to SQL-style quote-doubling (`''`). That is **wrong for Salesforce SOQL**, which uses backslash escaping — and it would have broken the existing passing test `quoteSoqlValue("O'Brien") === "'O\\'Brien'"`. The implemented fix keeps backslash escaping and adds backslash-first escaping.
- **Down-scoped:** GraphQL "unescaped record ID / `after` cursor" P1 findings — record IDs are `[A-Za-z0-9]` and Salesforce GraphQL cursors are base64 (`A-Za-z0-9+/=`); neither can contain a `"`, so no current break. The safe `useVars` mutation path (`$id: ID!`) already exists. Tracked as defensive (G1/D1), not P1 breaks.
