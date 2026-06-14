# 04 — Solution Plan (implemented items)

For each fix: root cause, the smallest safe solution, expected UX/behavior, acceptance criteria, test coverage, affected files, and compatibility risk.

## Q1 — SOQL string escaping (P1)

- **Root cause:** `quoteSoqlValue()` did `s.replace(/'/g, "\\'")` — it escaped single quotes but never the backslash itself. Salesforce SOQL string literals escape with a backslash, so a value ending in `\` (e.g. `C:\`) became `'C:\'`, where the trailing `\'` escapes the closing quote → unterminated, invalid, and injectable literal.
- **Solution:** Escape backslashes **first**, then single quotes: `s.replace(/\\/g, '\\\\').replace(/'/g, "\\'")`.
- **Expected behavior:** Apostrophes keep working (`O'Brien` → `'O\'Brien'`, unchanged); backslash/Windows-path values produce balanced, terminated literals (`C:\temp` → `'C:\\temp'`).
- **Acceptance:** `quoteSoqlValue` output is always a balanced, single-quoted literal; existing apostrophe behavior preserved.
- **Tests:** New cases in `tests/cov/soqlscripts_query_composer.test.js` (`backslashes are escaped before quotes`).
- **Files:** `scripts/soql/soql_query_composer.js`.
- **Compat risk:** None. Pure widening of escaping; no existing valid output changes.

## Q2/Q3 — Subquery filter operators (P1)

- **Root cause:** Main-query filter composition handled `IN/NOT IN/INCLUDES/EXCLUDES` (split into a parenthesized list) and `= NULL` / `!= NULL` (→ `IS NULL` / `IS NOT NULL`), but the **child-subquery** filter branch did neither — it always emitted `field op quoteSoqlValue(value)`. So a subquery IN filter became `WHERE LeadSource IN 'Web, Phone'` and a null check became `WHERE Email = NULL` — both invalid SOQL.
- **Solution:** Mirror the main-query branch logic inside the subquery composition (NULL operators → `IS [NOT] NULL`; list operators → split, quote each, join in parens; else binary).
- **Expected behavior:** Child subqueries with list/NULL filters now generate valid SOQL identical in shape to top-level filters.
- **Acceptance:** `(SELECT … FROM Child WHERE F IN ('a', 'b'))`, `… WHERE F IS NULL`, `… WHERE F IS NOT NULL` all generated correctly.
- **Tests:** Three new cases (IN list split; NOT IN/INCLUDES/EXCLUDES; `= NULL`/`!= NULL`).
- **Files:** `scripts/soql/soql_query_composer.js`.
- **Compat risk:** None for previously-working binary filters (the `else` branch is byte-for-byte the old behavior).

## C1 — LWC Explorer Escape-handler leak (P2)

- **Root cause:** `wireExplorerEvents()` runs on every explorer open and attached a new `document` `keydown` listener each time, removing it only inside the handler when Escape was pressed. Closing via the close button or SPA navigation left the listener attached → one leaked listener per open/close cycle.
- **Solution:** Bind the listener once, guarded by `explorerState._escHandlerBound`. The handler already self-gates on `explorerState.isOpen`, so a single persistent listener is behaviorally identical and leak-free.
- **Expected behavior:** Escape still closes the open explorer; no listener accumulation.
- **Acceptance:** Repeated open/close does not add listeners; Escape-to-close still works.
- **Tests:** Existing `tests/lwc_explorer.test.js` covers the close behavior (green).
- **Files:** `content_lwc_explorer.js`.
- **Compat risk:** None. Same user-visible behavior.

## X1 — SOQL object dropdown escaping (P2, defensive)

- **Root cause:** Search highlighting wrote the matched object name into `innerHTML` without `escapeHtml`, violating the project's escape-everything rule (exploitability low — SObject API names are `[A-Za-z0-9_]`).
- **Solution:** `Utils.escapeHtml(name)` before applying the `<mark>` wrap.
- **Acceptance:** Highlighting still works; rendered name is HTML-escaped.
- **Tests:** Covered by existing SOQL builder dropdown tests (green); behavior unchanged for normal names.
- **Files:** `soql_helper.js`.
- **Compat risk:** None.

## Deferred (documented in 03 register, R1–R7/U1–U3/G1/D1/S1/P1)

These are verified-real but larger or riskier (effort 2–3, several touch UX flows). They are the recommended next iteration, ordered by score in `03-prioritized-issues.md`. The cheapest high-value quick wins to pick up next: **U3** (REST input aria-label, effort 1), **R2** (GraphQL field-load Retry button), **R7** (SOQL initial empty-state guidance), **R1** (session Reconnect action).
