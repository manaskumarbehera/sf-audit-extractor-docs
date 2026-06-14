# TrackForce Pro v2.4.7

Patch release. Correctness fixes for the SOQL Builder and recovery/usability improvements for the SOQL and GraphQL builders. Backward compatible — no settings, storage, or permission changes.

## Highlights

- The SOQL Builder now generates **valid, executable queries** for null checks, child-subquery filters, and values containing quotes or backslashes (previously some of these produced queries Salesforce rejected).
- Clearer recovery when you're not connected or when GraphQL fields fail to load.

## Fixed

- **SOQL null filters were invalid.** The "is null" / "is not null" filter operators generated SQL-style `IS NULL` / `IS NOT NULL`, which Salesforce SOQL does not support — the query failed with "unexpected token". They now generate `= null` / `!= null`. _(Verified against a live org.)_
- **SOQL child-subquery filters generated invalid SOQL** for `IN` / `NOT IN` / `INCLUDES` / `EXCLUDES` (the values were treated as one string instead of a list) and for null checks. Subquery filters now match the main query.
- **SOQL values with a backslash produced a broken query.** A value ending in `\` (e.g. a Windows path like `C:\`) created an unterminated string literal. Values are now escaped correctly; apostrophes (e.g. `O'Brien`) continue to work.

## Improved

- **Not connected to Salesforce** now shows a **Retry** button that re-runs your query after you log in, instead of only static guidance.
- **GraphQL related-object fields** that fail to load now show a permission hint and a **Retry** button instead of a dead-end message.
- **LWC Explorer** no longer leaks a keyboard listener on each open/close, reducing memory growth during long sessions.
- **SOQL object picker** HTML-escapes object names when highlighting search matches (defense-in-depth).

## Known limitations

- Session recovery still requires the user to log into Salesforce in a tab before retrying (no silent token refresh).
- GraphQL mutation variable types are still assumed `String` for create/update inputs (planned next).

## Verification

- 8061 automated tests passing; lint, module-lint, build, and version checks green.
- SOQL query-generation fixes verified end-to-end (read-only) against a live developer org: `= null` / `!= null`, child-subquery `IN (...)`, and backslash/apostrophe escaping all execute; the old `IS NULL` form is confirmed rejected.

## Rollback

Revert commits `bacba88`, `bda9ee6`, `a201425`, `d968481`, `5ec3316`, `d9eba9a` (independent), or re-publish the prior v2.4.6 build artifact. No data migration involved.
