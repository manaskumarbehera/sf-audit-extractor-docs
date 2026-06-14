# 00 — Baseline Condition

_Captured before any change, on branch `improve/query-builders-adoption` (off `main` @ `f7888e1`)._
_Date: 2026-06-14._

## Architecture (verified facts)

- **Type:** Cross-browser Manifest V3 extension (Chrome, Edge, Firefox, Opera). Salesforce admin/dev tooling.
- **Two module systems (hard rule):** background service worker = ES modules (`background.js` → `bg_*.js`); all popup/content surfaces = IIFE + `window` globals. Enforced by `scripts/lint-module-misuse.cjs`.
- **UI model:** 3-mode nav (Explore / Debug / Analyze), 3 surfaces (launcher popup `launcher.html`, workspace tab `popup.html`, in-page overlays `content.js`).
- **Query builders (audit focus):**
  - SOQL: `soql_helper.js` (~4000 lines) + `scripts/soql/*` (virtual table, toolbar, guidance engine).
  - GraphQL: `graphql_helper.js` (~7000 lines) + `scripts/graphql_editor.js` (CodeMirror 6, esbuild IIFE bundle).
- **Salesforce API layer:** `bg_sf_api.js` (REST/Tooling/GraphQL), `bg_session_auth.js` (cookie-based session), `bg_command_dispatch.js` (message routing).
- **Versioning:** `manifest.json` is source of truth; `npm run check:versions` enforces docs consistency. Current version **2.4.6**.

## Relevant commands

| Command | Purpose |
|---|---|
| `npm test` | Jest, `--runInBand --detectOpenHandles --forceExit` |
| `npm run lint` | ESLint flat config, zero-warning CI policy |
| `npm run lint:modules` | IIFE/ESM cross-contamination linter |
| `npm run build:graphql` | Build `dist/graphql_editor.bundle.js` (required by CI) |
| `npm run check:versions` | manifest ↔ docs version consistency |
| `npm run check:bundle-size` | bundle-size budget |
| `npm run package` | Cross-browser zips (chrome/edge/firefox/opera) |

## Baseline results (all green)

| Check | Result |
|---|---|
| `npm run lint` | ✅ pass — 0 warnings |
| `npm run lint:modules` | ✅ pass — no module-system violations |
| `npm test` | ✅ **203 suites passed, 8054 tests passed, 1 skipped, 0 failed** (~54s) |
| `npm run build:graphql` | ✅ pass — `dist/graphql_editor.bundle.js` 572.4kb |
| `npm run check:versions` | ✅ pass — v2.4.6, all manifest fields/files present |

**No pre-existing failures.** Any new lint/type/test failure introduced by this work is a regression and must be fixed before release.

## Environment constraints / safety notes

- **Live browser exploration (Phase 3) requires the user.** Driving the extension against Salesforce needs a manual login/MFA that automation must not bypass. Static (read-only) code audit is where automated value is delivered without org risk.
- Salesforce orgs are connected locally (`mcp__salesforce-dx`, `.deplo1-qa-creds`). Per the safety rules these stay **read-only**; no DML, no metadata deploy, no production changes without explicit approval.
- No secrets (tokens, cookies, session IDs, org IDs) may appear in source, logs, screenshots, tests, or reports.
- Release packaging is allowed; **Chrome Web Store / Edge publish requires explicit user approval.**

## Method

Phase 1 (this doc) done. Phase 4 discovery runs as a parallel specialist static audit (SOQL, GraphQL, UX/a11y, Salesforce API/security, code-quality, product/adoption), each auditor returning evidence-cited findings (file:line) scored for prioritization. Findings synthesized in `03-prioritized-issues.md`; fixes implemented smallest-safe-first with regression tests.
