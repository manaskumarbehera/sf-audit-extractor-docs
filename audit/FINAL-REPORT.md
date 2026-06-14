# TrackForce Pro — UX, Quality and Release Report

Branch: `improve/query-builders-adoption` (off `main` @ `f7888e1`). Date: 2026-06-14.

## 1. Executive summary

A six-specialist parallel static audit (SOQL, GraphQL, UX/a11y, Salesforce API/security, code-quality, product/adoption) produced ~50 evidence-cited findings against a healthy v2.4.6 baseline (203 suites / 8054 tests passing, lint clean). Every finding was **ground-truthed against the actual code before action** — which rejected one false-positive XSS claim and corrected one auditor's *wrong* fix recommendation. This pass fixed the five highest-value, verified, low-risk issues — three of them **P1 query-correctness bugs** in the SOQL builder that emit invalid SOQL for ordinary input — each with regression tests, keeping the suite green (now 8058 passing). The remaining real findings are documented and prioritized for the next iteration.

## 2. Baseline condition

See `00-baseline.md`. All gates green pre-change: lint (0 warnings), module-lint, 8054 tests, build, version checks. No pre-existing failures.

## 3. Most important findings

1. **SOQL string escaping breaks on backslashes** (P1) — `quoteSoqlValue` didn't escape `\`, so any value ending in a backslash produced an unterminated, invalid, injectable literal. **Fixed.**
2. **SOQL subquery filters mis-generate IN-lists and NULL checks** (P1) — child-subquery filters emitted `IN 'a, b'` and `= NULL` instead of `IN ('a','b')` and `IS NULL`. **Fixed.**
3. **LWC Explorer leaks a keydown listener** on every open/close (P2). **Fixed.**
4. **Session-expiry has no in-UI recovery action** (P2) — top remaining adoption barrier. **Recommended next.**
5. **GraphQL field-load failure offers no Retry/guidance** (P2). **Recommended next.**

## 4. SOQL Builder findings

Fixed: backslash escaping (Q1), subquery IN/NOT IN/INCLUDES/EXCLUDES lists (Q2), subquery `= NULL`/`!= NULL` → `IS [NOT] NULL` (Q3), object-dropdown HTML escaping (X1). Recommended: initial empty-state guidance (R7), invalid-object early validation, suggestion-panel stale-render guard (S1), OR-condition grouping (missing feature). Detail in `03`/`04`.

## 5. GraphQL Builder findings

The GraphQL builder is in better shape than reported: it already supports AND/OR `filterLogic` and a safe `useVars` mutation path (`$id: ID!`). Real items deferred: introspection cache not org/version-scoped (R5), mutation variable types hardcoded to `String` (R4), no Retry on schema-load failure (R2), identifier validation for hand-entered objects/fields (G1). The "unescaped record ID / cursor" findings were down-scoped — SF IDs and base64 cursors can't contain `"`.

## 6. General UX & onboarding findings

Session-expiry recovery (R1), record-lookup error toasts (R3), SOQL/GraphQL initial empty states (R7), command-palette stale-closure (P1). All verified; deferred by effort.

## 7. Accessibility findings

Settings drawer initial focus (U1), onboarding focus return (U2), REST URL input `aria-label` (U3). No a11y regressions were introduced by this pass. U3 is a 1-line quick win for next.

## 8. Security & Salesforce API findings

Fixed the one rule-violating unescaped `innerHTML` (X1). Documented defensive hardening: route all record-ID SOQL interpolation through a shared quoter (D1 — latent, not currently exploitable since IDs are `[A-Za-z0-9]`), and GraphQL identifier validation (G1). **No secrets** appear in source, tests, logs, or reports. No tokens/cookies/session IDs were logged or exposed.

## 9. Changes implemented

| Commit | Change |
|---|---|
| `d9eba9a` | `fix(soql)`: backslash-safe string escaping + subquery IN/NULL operators (+4 tests) |
| `5ec3316` | `fix(soql)`: escape object name before `innerHTML` in builder dropdown |
| `d968481` | `perf(lwc)`: stop Escape-handler leak on explorer open/close |

Files: `scripts/soql/soql_query_composer.js`, `soql_helper.js`, `content_lwc_explorer.js`, `tests/cov/soqlscripts_query_composer.test.js`.

## 10. Automated tests added

4 new composer regression tests (backslash escaping; subquery IN list; NOT IN/INCLUDES/EXCLUDES; `= NULL`/`!= NULL`). Suite: 8054 → **8058** passing.

## 11. Manual validation

Lint, module-lint, full Jest suite, build, version checks — all green (`05-test-report.md`). **Live Chrome + Salesforce smoke test is pending the user** (manual login required; automation must not bypass it).

## 12. Performance impact

Positive: removes an unbounded `keydown` listener leak in the LWC Explorer. Query-generation changes are O(same); no added work on hot paths.

## 13. Remaining risks

- Fixes are unit-verified but not yet exercised in a live org (recommend a 2-minute sandbox smoke test: build a child-subquery with an IN filter + a `IS NULL` filter and Run).
- Deferred P2 items (session recovery, GraphQL retry) remain real adoption friction until addressed.

## 14. Release recommendation

Patch release **v2.4.7** (bug fixes only, backward compatible). Version bump + tag **not performed** — tagging triggers the Edge-publish CI workflow and requires explicit approval.

## 15. Release notes

See `docs/audit/RELEASE-NOTES-v2.4.7-draft.md`.

## 16. Rollback plan

- Pre-release: `git checkout main` (branch is unmerged; nothing shipped).
- Post-merge, pre-publish: `git revert d968481 5ec3316 d9eba9a` (independent, cleanly revertible) or revert the squash-merge commit.
- Post-publish: re-publish the prior packaged artifact for v2.4.6 from `build/` and roll the store listing back to the previous submission. No storage-schema or manifest-permission changes were made, so rollback is data-safe.

## 16b. Second batch (post-initial-report)

After the initial report, implemented the next-iteration items the owner approved plus a P1 that **only live testing caught**:

- **NEW P1 — SOQL `IS NULL` is invalid.** SOQL has no `IS NULL`/`IS NOT NULL`; the builder's null filters generated them and Salesforce rejected the query ("unexpected token"). Unit tests masked it (asserted strings, never executed). Verified against a live developer org; fixed to emit `= null`/`!= null` in the main and subquery paths. Commit `bacba88`.
- **R1 done** — SOQL not-connected **Retry** action (`a201425`, +3 regression tests).
- **R2 done** — GraphQL related-object field-load **Retry** + permission hint (`bda9ee6`).
- **Released** — bumped to **v2.4.7**, synced docs + changelog, packaged all four browsers (`a23d888`). Not published (awaiting approval).

This is the headline lesson of the engagement: **static audit + unit tests were not enough** — running the generated SOQL against a real org is what exposed the most impactful correctness bug.

**Recommendation implemented:** added a SOQL grammar guard to CI — `tests/cov/soql_grammar_guard.test.js` fuzzes `composeQueryFromBuilder` across every operator × tricky value (apostrophes, backslashes, IN-lists) for both main and subquery filters, and asserts the output never contains SOQL-invalid shapes (`IS NULL`/`IS NOT NULL`, unterminated string literals, bare IN values). Self-check cases prove the detector actually flags those shapes, so the guard is not vacuous. It runs in the existing `code-quality.yml` jest job; a reintroduction of any of these bugs now fails CI. (A live contract test against a sandbox would add even more coverage but needs org credentials in CI, so the deterministic generator-side guard is the safe default.)

## 17. Suggested next iteration

In priority order: R2 (GraphQL field-load Retry) · U3 (REST aria-label, 1 line) · R7 (SOQL initial empty state) · R1 (session Reconnect action) · R3 (record-lookup error toasts) · R5 (org-scoped GraphQL introspection cache) · R4 (mutation variable types) · U1 (settings drawer focus). Each is independently shippable with a regression test.
