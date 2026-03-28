# TrackForcePro: Unified Error Handling Strategy

## 1. Audit Findings

### Scale of the Problem

| Metric | Count | Severity |
|--------|-------|----------|
| Total catch blocks across codebase | ~1,183 | — |
| Empty `catch {}` blocks (errors swallowed) | ~885 (75%) | CRITICAL |
| `console.error()` calls in helpers | 0 | CRITICAL |
| Removed log markers (`// (error removed)`) in background.js | 10+ | CRITICAL |
| Inconsistent error response formats | 5+ variants | HIGH |
| String-based HTTP status detection (regex on error text) | 30+ | HIGH |
| Duplicated error extraction logic | 10+ copies | MEDIUM |
| Functions with retry logic | 2 of 12 API callers | MEDIUM |

### Error Response Format Chaos

The codebase uses at least 5 different error response formats:

```javascript
// Pattern 1: Most common (background.js message handlers)
{ success: false, error: "message string" }

// Pattern 2: With status (FETCH_API only)
{ success: false, error: "message", status: 403 }

// Pattern 3: GraphQL special case
{ success: false, error: "msg", data: responseData }

// Pattern 4: Unknown action handler
{ ok: false, error: "Unknown action: X" }

// Pattern 5: Helpers throw Error objects (not responses)
throw new Error("Query failed (401): Unauthorized")
```

Callers cannot reliably detect auth failures, retryable errors, or distinguish API errors from network errors.

### Top 5 Most Dangerous Patterns

**1. Empty catches (885 occurrences).** Errors vanish with zero visibility. Debugging requires reproducing the exact conditions because no logs exist.

**2. Stripped error logs.** 10+ locations in background.js have `// (error removed)` or `// (warning removed)` — the original logging was intentionally removed, making the production service worker a diagnostic black hole.

**3. String-based auth detection.** `/(^|[^\d])(401|403)([^\d]|$)/.test(errStr)` in audit_helper.js is fragile. A Salesforce error message like "Field access denied for 403 records" would trigger a false positive.

**4. Duplicated error extraction.** The pattern of `try { JSON.parse(txt); if (Array.isArray(json) && json[0]?.message) ... } catch {}` appears in 10+ locations. Each copy is slightly different — some check `errorCode`, some don't; some include `res.status`, some don't.

**5. Toast failure masking.** `try { Utils.showToast('error...') } catch {}` means if the DOM is in a bad state, the user gets no feedback AND the original error is lost.

---

## 2. Unified Error System: `tfp_error.js`

### Architecture

```
                    ┌─────────────────────────┐
                    │      TFPError API        │
                    │                          │
  ┌────────────────►│  .create(module, msg)    │──── Ring Buffer (200 entries)
  │                 │  .catch(module, fn)       │        │
  │                 │  .apiError(module, res)   │        ▼
  │                 │  .assertOk(module, res)   │  .getErrors(filter)
  │                 │  .extractHttpError(res)   │  .summary()
  │                 │                          │
  │  ┌──────────────│  .response(success, err) │
  │  │              │  .errorResponse(entry)    │
  │  │              │                          │
  │  │              │  .log(module, level, ...) │──── Console Output
  │  │              │  .setDebug(true/false)    │     (tiered by severity)
  │  │              │  .setSilent(true/false)   │
  │  │              └─────────────────────────┘
  │  │
  │  │  Standardized Response Format:
  │  │  ┌──────────────────────────────────────┐
  │  │  │ { success: false,                     │
  │  │  │   error: "user-safe message",         │
  │  │  │   status: 401,           // optional  │
  │  │  │   retryable: true,       // optional  │
  │  │  │   ...data }              // merged    │
  │  │  └──────────────────────────────────────┘
  │  │
  │  └───── background.js sendResponse()
  └──────── helpers catch blocks
```

### Error Entry Structure

Every error created through TFPError produces a structured entry:

```javascript
{
    timestamp:   1711612800000,           // Date.now()
    module:      'soql',                  // Source: 'bg', 'soql', 'graphql', 'rest', 'content', etc.
    message:     'Query failed (401): Unauthorized',  // Developer-facing detail
    category:    'auth',                  // Classified: network|auth|api|parse|storage|messaging|dom|validation|permission|internal|unknown
    severity:    'error',                 // Logging tier: error|warn|info|silent
    userMessage: 'Session expired — please refresh the Salesforce tab.',  // Safe for toasts
    httpStatus:  401,                     // HTTP status if applicable
    retryable:   false,                   // Whether retry might succeed
    context:     { query: 'SELECT...', url: '/api/query' },  // Debug context
    stack:       'Error: ...\n    at ...',  // Original stack trace
    causeName:   'Error',                 // Original error name
    causeMsg:    'Unauthorized',          // Original error message
}
```

### Error Categories

| Category | Triggers | User Message | Retryable? |
|----------|----------|-------------|------------|
| `network` | Failed to fetch, timeout, DNS, AbortError | "Network error — check your connection" | Yes |
| `auth` | 401, 403, session expired | "Session expired — please refresh" | No |
| `api` | 429, 5xx, Salesforce API errors | "Salesforce API error" | 429/5xx: Yes |
| `parse` | JSON SyntaxError, unexpected token | "Unexpected response format" | No |
| `storage` | Quota exceeded, storage write fail | "Storage error" | No |
| `messaging` | Extension context invalidated, port closed | "Communication error" | No |
| `dom` | Element not found, render failure | "Display error" | No |
| `validation` | 400, 404, bad input | "Invalid input" | No |
| `internal` | Uncategorized code errors | "Something went wrong" | No |

### Logging Behavior

| Severity | Production Mode | Debug Mode |
|----------|----------------|------------|
| `ERROR` | `console.error('[TFP:module]', msg)` | + stack trace, context, HTTP status |
| `WARN` | `console.warn('[TFP:module]', msg)` | + context |
| `INFO` | Silent | `console.info('[TFP:module]', msg)` |
| `SILENT` | Silent | Silent (buffer only) |

All log output uses the `[TFP:{module}]` prefix format, consistent with the existing pattern in data_explorer_helper.js and background.js.

---

## 3. Standard Response Format

All chrome.runtime message handlers should return:

```javascript
// Success
{ success: true, orgName: "Acme" }        // data merged at top level
{ success: true, data: [...records] }      // or in data field

// Error
{ success: false, error: "User-safe message" }
{ success: false, error: "API 401: Unauthorized", status: 401 }
{ success: false, error: "Rate limited", status: 429, retryable: true }
```

**Rules:**
- Always `success: boolean` (never use `ok`)
- Error message is always `error: string` (never an object)
- HTTP status included as `status: number` when from an API call
- `retryable: true` included only when the operation can be retried
- Additional data fields merged at top level for backward compatibility

---

## 4. Migration Patterns

### Pattern A: Replace empty catches

```javascript
// BEFORE
try { chrome.tabs.sendMessage(tab.id, msg); } catch {}

// AFTER
try { chrome.tabs.sendMessage(tab.id, msg); } catch (e) {
    TFPError.create('bg', 'Failed to send message to tab', {
        category: TFPError.Category.MESSAGING,
        severity: TFPError.Severity.WARN,
        cause: e,
        context: { tabId: tab.id, action: msg.action },
    });
}
```

### Pattern B: Replace duplicated HTTP error extraction

```javascript
// BEFORE (duplicated 10+ times)
if (!res.ok) {
    const txt = await res.text();
    let errorMsg = res.statusText;
    try {
        const json = JSON.parse(txt);
        if (Array.isArray(json) && json[0]?.message) {
            errorMsg = json[0].message;
        }
    } catch {}
    return { success: false, error: `API ${res.status}: ${errorMsg}` };
}

// AFTER (single-line)
if (!res.ok) {
    const detail = await TFPError.extractHttpError(res);
    TFPError.apiError('bg', res, detail);
    return TFPError.response(false, `API ${res.status}: ${detail}`, { status: res.status });
}

// OR: throw-based (for functions like describeGlobal)
await TFPError.assertOk('bg', res, 'describeGlobal');
```

### Pattern C: Replace string-based auth detection

```javascript
// BEFORE (fragile regex)
const errStr = String(response?.error || '').toLowerCase();
const unauthorized = /(^|[^\d])(401|403)([^\d]|$)/.test(errStr);

// AFTER (structured check with fallback)
const unauthorized = !response?.success &&
    (response?.status === 401 || response?.status === 403);
```

### Pattern D: Replace toast-wrapped-in-catch

```javascript
// BEFORE
} catch (err) {
    try { Utils.showToast('Failed: ' + err.message, 'error'); } catch {}
}

// AFTER
} catch (err) {
    const entry = TFPError.create('soql', 'Query failed', { cause: err });
    Utils.showToast(entry.userMessage, 'error');
}
```

### Pattern E: Restore stripped error logs

```javascript
// BEFORE (background.js, 10+ locations)
} catch (err) {
    // (error removed)
    sendResponse({ success: false, error: String(err) });
}

// AFTER
} catch (err) {
    TFPError.create('bg', 'FETCH_ORG_NAME failed', {
        category: TFPError.classifyError(err),
        cause: err,
        context: { action: 'FETCH_ORG_NAME' },
    });
    sendResponse(TFPError.errorResponse(err));
}
```

---

## 5. Integration Plan

### Phase 1: Foundation (Week 1)

1. Add `<script src="tfp_error.js"></script>` to popup.html **before** all other scripts
2. Add `importScripts('tfp_error.js')` or equivalent to background.js service worker
3. Wire debug mode toggle in Settings tab: `TFPError.setDebug(enabled)`
4. No behavioral changes yet — just makes TFPError available

### Phase 2: Background.js (Week 2)

Priority: highest — this is the messaging hub and service worker.

1. Restore all stripped error logs (10+ `// (error removed)` locations)
2. Replace all empty catches in message handlers with `TFPError.create()`
3. Consolidate `extractHttpError` usage across EXECUTE_SOQL, FETCH_API, FETCH_ORG_NAME
4. Standardize all `sendResponse()` calls to use `TFPError.response()`
5. Add `status` field to error responses for structured auth detection

**Impact:** ~60 catch blocks, ~40 sendResponse calls.

### Phase 3: Popup-Side Helpers (Week 3-4)

Priority order based on risk and usage frequency:

| Helper | Empty Catches | Priority | Key Changes |
|--------|--------------|----------|-------------|
| soql_helper.js | ~94 | P1 | Replace toast-wrapped catches, query error logging |
| graphql_helper.js | ~100 | P1 | Schema sync errors, query execution |
| data_explorer_helper.js | ~50 | P1 | Inline edit, bulk operations, record loading |
| rest_explorer_helper.js | ~30 | P2 | Request send/receive, response parsing |
| content.js | ~50 | P2 | Extension context guards, storage reads |
| org_tools_helper.js | ~25 | P2 | Limits, metadata fetches |
| settings_helper.js | ~20 | P3 | Storage operations |
| audit_helper.js | ~10 | P3 | String-based auth detection |
| platform_helper.js | ~10 | P3 | Event streaming |
| security_helper.js | ~10 | P3 | Permission checks |

### Phase 4: Production Hardening (Week 5)

1. Add Settings UI for "Developer Mode" that toggles `TFPError.setDebug(true)`
2. Add "Error Log" panel (possibly in Help tab) showing `TFPError.summary()` and recent errors
3. Wire `TFPError.getErrors({ since: sessionStart })` into a "Copy Debug Info" button
4. Add retry wrapper for `runSoql` and `runGraphql` based on `entry.retryable`

---

## 6. Files Produced

| File | Lines | Tests | Purpose |
|------|-------|-------|---------|
| `tfp_error.js` | 380 | 74 | Central error handler with IIFE pattern |
| `tests/tfp_error.test.js` | 470 | 74 | Full test coverage of all APIs |
| `error_handling_migrations.js` | 290 | — | 10 concrete before/after refactoring examples |
| `docs/ERROR_HANDLING_STRATEGY.md` | — | — | This document |

### `tfp_error.js` API Surface

| Method | Purpose |
|--------|---------|
| `TFPError.create(module, msg, opts)` | Create structured error entry |
| `TFPError.catch(module, fn, msg, opts)` | Wrap sync/async fn with error handling |
| `TFPError.apiError(module, res, msg)` | Classify HTTP response errors |
| `TFPError.assertOk(module, res, action)` | Throw if response not ok |
| `TFPError.extractHttpError(res)` | Parse SF/GraphQL/generic error bodies |
| `TFPError.response(success, error, data)` | Build standardized response |
| `TFPError.errorResponse(err, data)` | Build error response from any error type |
| `TFPError.classifyError(err)` | Categorize thrown Error objects |
| `TFPError.classifyHttpStatus(status)` | Categorize HTTP status codes |
| `TFPError.isRetryableStatus(status)` | Check if status is retryable |
| `TFPError.log(module, level, ...args)` | Structured logging utility |
| `TFPError.getErrors(filter)` | Query error ring buffer |
| `TFPError.summary()` | Get diagnostic summary |
| `TFPError.setDebug(bool)` | Toggle debug/production mode |
| `TFPError.setSilent(bool)` | Suppress console (for tests) |

---

## 7. Backward Compatibility

The system is designed for incremental adoption:

- `TFPError.response()` produces objects that match the existing `{ success, error }` format
- Data fields are merged at top level (not nested under `data`) for backward compat
- `TFPError.errorResponse()` accepts strings, Error objects, or structured entries — works with any existing error type
- `classifyError()` handles all error patterns currently in the codebase
- Existing `catch {}` blocks can be replaced one at a time without breaking anything
- `if (window.TFPError)` guards allow gradual rollout per file
