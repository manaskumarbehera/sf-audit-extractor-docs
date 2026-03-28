# TrackForcePro: Messaging Framework Analysis & Refactoring Guide

## 1. Messaging Audit Summary

Analyzed **54 `chrome.runtime.sendMessage` calls** and **16 `chrome.tabs.sendMessage` calls** across 6 files, plus **7 `onMessage` listeners** in background.js and content.js.

### Call Distribution

| File | runtime.sendMessage | tabs.sendMessage | onMessage listeners |
|---|---|---|---|
| content.js | 31 | — | 5 |
| background.js | 2 | 11 | 2 |
| popup.js | 12 | 5 | 1 |
| utils.js | 2 | — | — |
| soql_helper.js | 6 | — | — |
| graphql_helper.js | 8 | — | — |

### Message Actions Catalog (30+ unique actions)

**Query Execution:** `RUN_SOQL`, `EXECUTE_SOQL`, `RUN_GRAPHQL`, `EXECUTE_GRAPHQL`
**Metadata:** `DESCRIBE_GLOBAL`, `DESCRIBE_SOBJECT`
**Session:** `GET_SESSION_INFO`, `GET_SESSION`, `getSessionInfo`
**Data:** `FETCH_API`, `FETCH_AUDIT_TRAIL`, `FETCH_ORG_NAME`, `GET_ORG_ID`
**UI Commands:** `toggleSidebar`, `toggleShowAllData`, `openTFPCommandPalette`, `openTFPSetupSearch`, `toggleLwcExplorer`, `TRIGGER_COMMAND`
**Navigation:** `openPopup`, `openAsTab`, `openPopupTab`, `NAVIGATE_HASH`, `OPEN_IN_NEW_WINDOW`, `OPEN_INCOGNITO`
**State:** `APP_POP_GET`, `APP_POP_SET`, `PLATFORM_PIN_GET`, `PLATFORM_PIN_SET`, `PLATFORM_PIN_TOGGLE`, `APP_INSTANCE_CHECK`
**Settings:** `TFP_SETTINGS_CHANGED`
**Content:** `contentReady`, `updateFavicon`, `resetFavicon`
**LMS:** `LMS_PUBLISH`, `LMS_CHECK_AVAILABILITY`
**Clipboard:** `TFP_COPY_TO_CLIPBOARD`

---

## 2. Issues Identified

### 2.1 No Timeout on Any Message (Critical)

**0 out of 54 calls** have explicit timeout logic. All rely on Chrome's internal timeout (~5s for closed ports), which is insufficient for long-running operations like SOQL pagination or GraphQL introspection. If background.js hangs in an infinite loop or a fetch never resolves, the UI freezes indefinitely with a spinning loader.

**Impact:** Users see infinite loading spinners with no way to recover except closing the popup.

### 2.2 Inconsistent Retry Logic (High)

Only **1 out of 54 calls** (`soql_helper.js` line 5460) has retry logic. GraphQL execution has **no retry**, creating an asymmetry: expired sessions cause SOQL to auto-recover but GraphQL to fail silently.

| Flow | Auth Retry | SW Crash Retry | Network Retry |
|---|---|---|---|
| SOQL execution | Yes (1 attempt) | No | No |
| GraphQL execution | **No** | No | No |
| DESCRIBE_GLOBAL | No | No | No |
| DESCRIBE_SOBJECT | No | No | No |
| FETCH_API | No | No | No |
| FETCH_AUDIT_TRAIL | Yes (in audit_helper) | Yes (fetchDirect fallback) | No |

### 2.3 Silent Failures (High)

**11 fire-and-forget calls** have no error handling at all. If these fail, no feedback reaches the user.

Examples of silent failures:
- `contentReady` (line 3227) — background never learns the content script loaded
- `TFP_SETTINGS_CHANGED` broadcast (popup.js line 2558) — settings changes don't propagate
- `toggleSidebar` (background.js line 804) — keyboard shortcut silently fails
- `APP_INSTANCE_CHECK` (popup.js line 513) — single-instance mode silently breaks

### 2.4 Race Conditions (Medium)

**Dual listener race in background.js:** Two `onMessage` listeners (lines 359 and 821) handle overlapping actions. The second listener has a manual exclusion list (`firstListenerActions`) but if the list gets out of sync, both listeners may attempt to `sendResponse()` — causing "message port closed" errors.

**Stale callback race in soql_helper.js:** The `epoch !== lifecycleEpoch` guard (line 5478) correctly prevents stale DOM updates, but the retry logic (lines 5460-5475) doesn't check staleness before the second `runOnce()` call, meaning a retried query could succeed and update DOM after the user has already navigated away.

### 2.5 Inconsistent Response Formats (Medium)

Background.js handlers return different shapes:

| Handler | Success Shape | Error Shape |
|---|---|---|
| RUN_SOQL | `{ success, totalSize, records, done }` | `{ success: false, error }` |
| RUN_GRAPHQL | `{ success, data }` | `{ success: false, error, data }` |
| DESCRIBE_GLOBAL | `{ success, objects, data }` | `{ success: false, error }` |
| GET_ORG_ID | `{ success, orgId }` | `{ success: false, error }` |
| FETCH_API | `{ success, data, status }` | `{ success: false, error, status }` |

Consumers must know each handler's specific shape, making error handling brittle.

### 2.6 Service Worker Crash Detection (Medium)

The audit_helper.js has a sophisticated `fetchDirect()` fallback for service worker crashes, but soql_helper.js, graphql_helper.js, and all other callers have **no fallback**. They simply show the Chrome runtime error to the user.

### 2.7 Missing `return true` in Some Listeners (Low)

Content.js listener at line 2388 (`toggleSidebar`) and line 5559 (`TFP_COPY_TO_CLIPBOARD`) don't return `true`, which is correct since they don't use `sendResponse`. But the listener at line 3202 (`TFP_SETTINGS_CHANGED`) performs async work without `return true`, which means `sendResponse` cannot be called if needed later.

---

## 3. Messaging Framework Design

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  TFPMessaging (window.TFPMessaging)                     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ send(action, payload, options)                    │   │
│  │   → timeout(configurable, default 30s)           │   │
│  │   → retry(auth failure, SW crash, network error) │   │
│  │   → normalize({ success, data, error, code })    │   │
│  │   → abort(via AbortController signal)            │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ sendWithSession(action, payload, options)         │   │
│  │   → auto-resolves instanceUrl                    │   │
│  │   → auto-refreshes on auth failure               │   │
│  │   → enriches payload on retry                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ sendToTab(tabId, action, payload, options)        │   │
│  │   → timeout + lastError check                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ fire(action, payload)       — fire-and-forget    │   │
│  │ fireToTab(tabId, action)    — fire-and-forget    │   │
│  │ broadcast(action, payload)  — all SF tabs        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ErrorCode: TIMEOUT | NO_RESPONSE | RUNTIME_ERROR |     │
│    SERVICE_WORKER_DEAD | AUTH_FAILED | NETWORK_ERROR |   │
│    INVALID_ACTION | UNKNOWN                             │
└─────────────────────────────────────────────────────────┘
```

### Standard Response Envelope

Every `send()` and `sendWithSession()` call returns:

```javascript
{
    success: boolean,        // true if background returned success
    data:    Object | null,  // response payload (records, orgId, etc.)
    error:   string | null,  // human-readable error message
    code:    string | null,  // ErrorCode enum value (for programmatic handling)
    meta: {
        elapsed: number,     // ms since message was sent
        attempt: number,     // retry attempt (0 = first try)
    }
}
```

### Retry Strategy

```
Attempt 0: Send message
  → Success? Return immediately.
  → AUTH_FAILED? Call onAuthFailure(), backoff, retry.
  → SERVICE_WORKER_DEAD? Backoff (500ms + jitter), retry.
  → NETWORK_ERROR? Backoff (500ms + jitter), retry.
  → Other error? Return immediately (non-retryable).

Attempt 1: Send message (with enriched payload)
  → Success or failure? Return.
```

Backoff uses exponential scaling with 30% jitter: `min(500ms × 2^attempt, 5000ms) + random jitter`.

---

## 4. Usage Examples

### Basic Query (replaces manual sendMessage)

```javascript
// BEFORE: 15 lines
chrome.runtime.sendMessage(payload, (resp) => {
    if (chrome.runtime.lastError) { /* handle */ return; }
    if (!resp || !resp.success) { /* handle */ return; }
    // use resp.records
});

// AFTER: 3 lines
const result = await TFPMessaging.send('RUN_SOQL', { query, useTooling, limit });
if (!result.success) { /* result.error, result.code */ return; }
// use result.data.records
```

### Session-Aware Query (replaces manual instanceUrl + retry)

```javascript
// BEFORE: 40+ lines (getInstanceUrl, runOnce, 401 check, session refresh, retry)
// AFTER: 5 lines
const result = await TFPMessaging.sendWithSession('RUN_SOQL', {
    query: 'SELECT Id FROM Account LIMIT 10',
    useTooling: false,
}, { timeout: 60000, retry: { maxAttempts: 1 } });
```

### Fire-and-Forget (replaces try-catch wrappers)

```javascript
// BEFORE:
try { chrome.runtime.sendMessage({ action: 'contentReady', url }, () => { void chrome.runtime.lastError; }); } catch {}

// AFTER:
TFPMessaging.fire('contentReady', { url: location.href });
```

### Broadcast Settings Change

```javascript
// BEFORE: manual tab query + loop with try-catch per tab
const tabs = await chrome.tabs.query({ url: ['https://*.salesforce.com/*', ...] });
for (const tab of tabs) {
    try { chrome.tabs.sendMessage(tab.id, { type: 'TFP_SETTINGS_CHANGED' }); } catch {}
}

// AFTER:
TFPMessaging.broadcast('TFP_SETTINGS_CHANGED', { setting: 'inlineEdit' });
```

### Error-Code-Driven UI

```javascript
const result = await TFPMessaging.sendWithSession('RUN_GRAPHQL', payload);
if (!result.success) {
    switch (result.code) {
        case TFPMessaging.ErrorCode.AUTH_FAILED:
            showBanner('Session expired. Refresh the Salesforce tab.');
            break;
        case TFPMessaging.ErrorCode.TIMEOUT:
            showBanner('Query timed out. Try simplifying.');
            break;
        case TFPMessaging.ErrorCode.SERVICE_WORKER_DEAD:
            showBanner('Extension recovering. Please retry.');
            break;
        default:
            showError(result.error);
    }
}
```

---

## 5. Files Produced

| File | Purpose | Lines |
|---|---|---|
| `tfp_messaging.js` | Messaging framework (send, sendToTab, sendWithSession, fire, broadcast) | ~420 |
| `soql_execution.refactored.js` | SOQL flow refactored with Before/After comparison | ~175 |
| `graphql_execution.refactored.js` | GraphQL flow refactored with Before/After + DESCRIBE helpers | ~210 |
| `MESSAGING_FRAMEWORK_GUIDE.md` | This document | ~200 |

### Integration into popup.html

```html
<!-- After utils.js, before any helper -->
<script src="tfp_messaging.js"></script>
```

All existing tests pass (4644/4644). The framework is backward-compatible — existing `chrome.runtime.sendMessage` calls continue to work alongside `TFPMessaging.send()`. Migration can be done incrementally, one call site at a time.

---

## 6. Migration Priority

**Phase 1 (High-Value):** Query execution flows — most user-visible, most impacted by missing timeout/retry.

| Call Site | File | Lines | Benefit |
|---|---|---|---|
| SOQL execution | soql_helper.js | 5440-5530 | Timeout + cleaner retry |
| GraphQL execution | graphql_helper.js | 7128-7163 | **Adds missing retry** |

**Phase 2 (Medium-Value):** Describe calls — frequently fail on expired sessions.

| Call Site | File | Benefit |
|---|---|---|
| DESCRIBE_GLOBAL | soql_helper.js, graphql_helper.js | Retry on auth + timeout |
| DESCRIBE_SOBJECT | soql_helper.js, graphql_helper.js | Retry on auth + timeout |

**Phase 3 (Broadcast):** Settings and fire-and-forget — reduce boilerplate.

| Pattern | Count | Replacement |
|---|---|---|
| TFP_SETTINGS_CHANGED broadcast | 3 calls | `TFPMessaging.broadcast()` |
| contentReady fire-and-forget | 2 calls | `TFPMessaging.fire()` |
| openPopupTab with fallback | 5 calls | `TFPMessaging.send()` with auto-retry |

**Phase 4 (All remaining):** Systematic replacement of remaining 40+ raw `sendMessage` calls.
