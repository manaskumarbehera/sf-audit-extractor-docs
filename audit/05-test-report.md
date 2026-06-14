# 05 — Test & Validation Report

All commands run on branch `improve/query-builders-adoption`. Salesforce orgs were **not** touched (static, read-only audit; no live-org test ops were run — see note).

## Commands executed

| Command | Before (baseline `main`) | After (this branch) |
|---|---|---|
| `npm run lint` | ✅ 0 warnings | ✅ 0 warnings |
| `npm run lint:modules` | ✅ no violations | ✅ no violations |
| `npm test` | ✅ 203 suites / **8054** passed, 1 skipped, 0 failed | ✅ 203 suites / **8058** passed, 1 skipped, 0 failed |
| `npm run build:graphql` | ✅ 572.4kb | ✅ (unchanged source) |
| `npm run check:versions` | ✅ v2.4.6 | ✅ v2.4.6 |

Net: **+4 tests**, all green. No regressions. No new lint/type errors. Pre-commit hooks (lint-staged: eslint `--max-warnings 0` + prettier) passed on every commit.

## New regression tests (`tests/cov/soqlscripts_query_composer.test.js`)

- `quoteSoqlValue` — backslashes escaped before quotes; `C:\` → `'C:\\'`; `a\'b` → `'a\\\'b'`; `C:\temp` stays balanced. Existing `O'Brien` case still passes (escaping behavior preserved).
- `composeQueryFromBuilder` — subquery `IN` list split + parenthesized (not one string literal); `NOT IN`/`INCLUDES`/`EXCLUDES` parenthesized; subquery `= NULL` → `IS NULL` and `!= NULL` → `IS NOT NULL`.

Focused run: `npx jest tests/cov/soqlscripts_query_composer.test.js tests/soql_builder.test.js tests/lwc_explorer.test.js` → **3 suites / 237 tests passed**.

## What was NOT validated here (requires the user / live org)

- **Live extension load in Chrome + Salesforce.** Driving the popup against a real org needs a manual login/MFA that automation must not bypass. The fixes above are pure query-string / DOM-escaping / listener-lifecycle changes verified by unit tests; a manual smoke test of "build a subquery with an IN filter and Run" against a sandbox is the recommended human verification step before publish.
- **Chrome Web Store / Edge publish.** Not performed — requires explicit approval.

## Addendum — second batch (R1/R2 + live-org smoke + release)

Implemented after the first batch: **R1** (SOQL not-connected Retry action), **R2** (GraphQL related-object field-load Retry + guidance), and a **new P1 found by live smoke testing**.

### Live-org smoke test (read-only, `Deplo1Partner` developer org)

Ran the exact SOQL shapes the fixed composer now generates. This surfaced a P1 the unit tests had masked:

| Generated shape | Result |
|---|---|
| `… WHERE Email IS NULL` (old output) | ❌ **rejected** — "unexpected token: 'Email IS'" → SOQL has no `IS NULL` |
| `… WHERE Industry = null AND Name != null` (new output) | ✅ executes |
| `(SELECT Id FROM Contacts WHERE LeadSource IN ('Web','Other'))` | ✅ executes |
| `(SELECT Id FROM Contacts WHERE Email = null)` | ✅ executes |
| `WHERE Name = 'O\'Brien'` (apostrophe escaping) | ✅ executes |
| `WHERE Name = 'C:\\temp'` (backslash escaping) | ✅ executes |

Fix: composer now emits `= null` / `!= null` (main + subquery). Tests updated to assert executable syntax.

### Counts / gates (after second batch)

- `npm test`: ✅ 203 suites / **8061** passed, 1 skipped, 0 failed.
- `npm run lint`, `lint:modules`, `build:graphql`, `check:versions`: ✅ all green at v2.4.7.
- `npm run package`: ✅ 4 zips built — `build/{chrome,edge,firefox,opera}/TrackForcePro-v2.4.7-*.zip` (~2.0M each).
- New R1 regression tests (3) added in `tests/soql_builder.test.js`; composer null-syntax tests updated.

## Definition-of-done check

- [x] No new lint or type errors.
- [x] All existing tests pass; pre-existing skip count unchanged (1).
- [x] Every fixed P0/P1 (Q1, Q2, Q3) has regression coverage.
- [x] Extension builds (`build:graphql`, version checks green).
- [ ] Manual Chrome load + SOQL/GraphQL journey smoke test — **pending user** (needs live org login).
- [x] No secrets in source, tests, logs, or this report.
- [x] No accessibility regressions introduced (no a11y-affecting markup changed; X1 escaping is invisible to AT).
- [x] Rollback path documented (see release notes).
