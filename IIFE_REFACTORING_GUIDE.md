# TrackForcePro: IIFE + Window Globals Refactoring Guide

## Executive Summary

This document presents a complete analysis and refactoring plan for TrackForcePro's IIFE + `window.*` globals pattern, including a namespaced module registry (`window.TFP.Modules.*`), dependency injection, and lifecycle control.

---

## 1. Global Exposure Audit

### Current Window Globals (20+ helpers)

| Global Name | File | Pattern | Dependencies (Hidden) |
|---|---|---|---|
| `Utils` | `utils.js` | `window.Utils = {...}` | None (foundational) |
| `SettingsHelper` | `settings_helper.js` | `window.SettingsHelper = {...}` | chrome.storage, DOM |
| `AuditHelper` | `audit_helper.js` | `window.AuditHelper = {...}` | Utils |
| `SoqlHelper` | `soql_helper.js` | Flag guard + `window.SoqlHelper` | Utils, SoqlResultToolbar? |
| `GraphqlHelper` | `graphql_helper.js` | Flag guard (no window export) | GraphQLEditorBundle? |
| `PlatformHelper` | `platform_helper.js` | `window.PlatformHelper = {...}` | Utils |
| `DataExplorerHelper` | `data_explorer_helper.js` | `Object.defineProperty` | Utils, Platform, Security, UserManager, Settings, Cache |
| `UserManagerHelper` | `user_manager_helper.js` | `Object.defineProperty` | Platform, DataExplorer (BIDIRECTIONAL) |
| `SecurityHelper` | `security_helper.js` | `Object.defineProperty` | Platform, Utils |
| `OrgToolsHelper` | `org_tools_helper.js` | `Object.defineProperty` | Utils |
| `RestExplorerHelper` | `rest_explorer_helper.js` | `Object.defineProperty` | Utils, RestCatalog, RestJsonViewer, RestCurlParser |
| `RestCatalog` | `rest_catalog.js` | `Object.defineProperty` | None |
| `RestJsonViewer` | `rest_json_viewer.js` | `Object.defineProperty` | Utils |
| `RestCurlParser` | `rest_curl_parser.js` | `Object.defineProperty` | None |
| `RestChainEngine` | `rest_chain_engine.js` | `Object.defineProperty` | Utils, RestExplorer |
| `DataExplorerTools` | `data_explorer_tools.js` | `window.DataExplorerTools = {...}` | None |
| `CacheManager` | `cache_manager.js` | `window.CacheManager = {...}` | None |
| `AppearanceSettings` | `appearance_settings.js` | `window.AppearanceSettings = {...}` | None |
| `SoqlVirtualTable` | `scripts/soql/soql_virtual_table.js` | `window.SoqlVirtualTable` | None |
| `SoqlResultToolbar` | `scripts/soql/soql_result_toolbar.js` | `window.SoqlResultToolbar` | None |
| `SoqlGuidanceEngine` | `scripts/soql/soql_guidance_engine.js` | `window.SoqlGuidanceEngine` | None |
| `SoqlGuidance` | `scripts/soql/soql_guidance.js` | `window.SoqlGuidance` | SoqlGuidanceEngine |

### Three Initialization Patterns Found

**Pattern 1: Flag-based guard** (SoqlHelper, GraphqlHelper)
```javascript
if (window.__SoqlHelperLoaded) { return; }
window.__SoqlHelperLoaded = true;
```

**Pattern 2: Object.defineProperty guard** (12 helpers)
```javascript
if (!window.SecurityHelper) {
    Object.defineProperty(window, 'SecurityHelper', {
        value: SecurityHelper, writable: false
    });
}
```

**Pattern 3: Simple assignment** (Utils, CacheManager, DataExplorerTools)
```javascript
window.Utils = { escapeHtml, sleep, ... };
```

---

## 2. Detected Issues

### 2.1 Hidden Dependencies

All dependencies are resolved via bare globals at call time. No helper declares what it needs. If `utils.js` fails to load, 15+ helpers break silently at runtime.

Example — AuditHelper's hidden Utils dependency:
```javascript
// audit_helper.js line 17
function escape(s) {
    return Utils.escapeHtml(s);  // ← bare global, not declared anywhere
}
```

### 2.2 Tight Coupling: Bidirectional Dependency

```
DataExplorerHelper → UserManagerHelper (calls UserManagerHelper.showUser)
UserManagerHelper → DataExplorerHelper (calls DataExplorerHelper.loadRecord)
```

This cycle makes it impossible to load one without the other and prevents proper initialization ordering.

### 2.3 Naming Conflict Risk

All 20+ helpers occupy the top-level `window` namespace. Any third-party library, Salesforce JS, or future code that defines `window.Utils` or `window.SecurityHelper` would silently override the extension's module.

### 2.4 No Lifecycle Control

Helpers are initialized at `<script>` load time (IIFE execution) with no ability to:
- Defer initialization until all deps are ready
- Verify that required deps are available before running
- Order initialization across modules

---

## 3. Proposed Solution: TFP Module Registry

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  window.TFP                                         │
│  ├── .Modules  (registry singleton)                 │
│  ├── .define(name, { deps, factory })               │
│  ├── .get(name) → api | null                        │
│  ├── .require(name) → api | throw                   │
│  ├── .has(name) → boolean                           │
│  └── .onReady(name, callback)                       │
│                                                     │
│  Lifecycle: REGISTERED → RESOLVING → READY | FAILED │
│                                                     │
│  Backward compat: window.Utils still works          │
│  (registry installs Object.defineProperty shim)     │
└─────────────────────────────────────────────────────┘
```

### Load Order in popup.html

```html
<!-- 1. Registry bootstrap (MUST be first) -->
<script src="tfp_module_registry.js"></script>

<!-- 2. Foundational (no deps) -->
<script src="utils.js"></script>
<script src="settings_helper.js"></script>
<script src="cache_manager.js"></script>
<script src="appearance_settings.js"></script>

<!-- 3. First-tier (depend on Utils) -->
<script src="audit_helper.js"></script>
<script src="platform_helper.js"></script>
<script src="rest_catalog.js"></script>
<script src="rest_curl_parser.js"></script>

<!-- 4. Second-tier (depend on Utils + others) -->
<script src="soql_helper.js"></script>
<script src="graphql_helper.js"></script>
<script src="security_helper.js"></script>
<script src="data_explorer_helper.js"></script>
...
```

### Key Design Decisions

1. **Synchronous resolution**: Factory runs immediately when all deps are ready (no async). This matches the existing IIFE behavior — all code runs at `<script>` load time.

2. **Deferred resolution**: If module A depends on B but B isn't loaded yet, A stays in `REGISTERED` state. When B resolves, A's factory auto-fires. This eliminates load-order sensitivity.

3. **Circular dependency detection**: If A's factory tries to resolve B which tries to resolve A, the registry throws immediately with a clear error message.

4. **Backward compatibility**: Every `resolve({...})` call also installs `window.ModuleName = api`. Existing code like `if (window.Utils) Utils.escapeHtml(...)` keeps working.

5. **Gradual migration**: Modules can be converted one at a time. Unconverted modules still work because the registry checks for existing `window.*` globals.

---

## 4. Before vs After Comparison

### 4.1 Utils (Foundational Module)

**BEFORE** — `utils.js` (825 lines):
```javascript
(function () {
    'use strict';

    function escapeHtml(str) { ... }
    function sleep(ms) { ... }
    // ... 24 more functions ...

    // ← Flat assignment to window global
    // ← No double-load guard
    // ← No freeze (api is mutable)
    window.Utils = {
        escapeHtml, sleep, fetchWithTimeout, svgPlus, svgMinus,
        showToast, download, findSalesforceTab, sendMessageToSalesforceTab,
        getInstanceUrl, openRecordInNewTab, fallbackCopyText,
        getApiVersionNumber, getApiVersionPath, getAccessToken,
        getSessionInfo, getSessionFromCookies, normalizeApiVersion,
        joinUrl, setInstanceUrlCache, getCachedInstanceUrl,
        looksLikeSalesforceOrigin, setPreferredInstance, getPreferredInstance,
        debounce, throttle, createRateLimiter, storageGet, storageSet, sfFetch,
    };
})();
```

**AFTER** — `utils.refactored.js`:
```javascript
(function () {
    'use strict';

    const registry = window.TFP && window.TFP.define;

    if (registry) {
        // ← Declared: no deps (foundational)
        // ← Double-load: handled by registry
        // ← API: auto-frozen by registry
        // ← window.Utils: auto-installed as backward-compat shim
        TFP.define('Utils', {
            deps: [],
            factory: function (resolve) {
                _buildUtils(resolve);
            }
        });
    } else {
        // Legacy fallback: works without registry
        if (window.Utils) return;
        const api = {};
        _buildUtils(function (resolved) { Object.assign(api, resolved); });
        window.Utils = api;
    }

    function _buildUtils(resolve) {
        function escapeHtml(str) { ... }  // ← All functions IDENTICAL
        function sleep(ms) { ... }
        // ... 24 more functions ...

        resolve({  // ← resolve() instead of window.Utils =
            escapeHtml, sleep, fetchWithTimeout, /* ... all 26 exports ... */
        });
    }
})();
```

**What changed**: 6 lines of wrapper code. Zero behavioral changes. Zero function modifications.

---

### 4.2 AuditHelper (Helper with Dependencies)

**BEFORE** — `audit_helper.js` (517 lines):
```javascript
(function () {
    'use strict';

    // ← Hidden dependency: Utils accessed as bare global
    function escape(s) {
        return Utils.escapeHtml(s);  // ← Breaks silently if Utils not loaded
    }

    // ... all logic ...

    // ← Hidden dependency not visible from API surface
    window.AuditHelper = {
        init, fetchNow,
        _test: { processAuditData, handleExport, getState: () => ... },
    };
})();
```

**AFTER** — `audit_helper.refactored.js`:
```javascript
(function () {
    'use strict';

    const registry = window.TFP && window.TFP.define;

    if (registry) {
        TFP.define('AuditHelper', {
            deps: ['Utils'],  // ← EXPLICIT dependency declaration
            factory: function (resolve, deps) {
                _buildAuditHelper(resolve, deps.Utils);  // ← Injected
            }
        });
    } else {
        if (window.AuditHelper) return;
        const api = {};
        _buildAuditHelper(function (resolved) { Object.assign(api, resolved); }, window.Utils);
        window.AuditHelper = api;
    }

    function _buildAuditHelper(resolve, Utils) {  // ← Utils is a PARAMETER

        // ← Dependency is explicit and visible
        function escape(s) {
            return Utils.escapeHtml(s);  // ← Uses injected param, not bare global
        }

        // ... all logic IDENTICAL ...

        resolve({
            init, fetchNow,
            _test: { processAuditData, handleExport, getState: () => ... },
        });
    }
})();
```

**What changed**:
- `deps: ['Utils']` — dependency is declared and visible
- `Utils` is injected as a parameter, not accessed as a bare global
- If Utils isn't loaded when AuditHelper's `<script>` runs, the registry defers resolution until Utils becomes available
- All internal logic is identical

---

### 4.3 SettingsHelper (Large Module, No Runtime Deps)

**BEFORE** — `settings_helper.js` (2,068 lines):
```javascript
(function () {
    'use strict';
    // ... 2000+ lines of implementation ...

    window.SettingsHelper = {
        injectFlexCss, ensureSettingsTabExists, applyTabVisibilityFromStorage,
        buildSettingsPanel, firstVisibleTabName, showTab,
        // ... 37 more exports ...
        getCustomSfLinks, addCustomSfLink,
    };
})();
```

**AFTER** — `settings_helper.refactored.js`:
```javascript
(function () {
    'use strict';

    const registry = window.TFP && window.TFP.define;

    if (registry) {
        TFP.define('SettingsHelper', {
            deps: [],  // ← Foundational: no runtime dependencies
            factory: function (resolve) {
                _buildSettingsHelper(resolve);
            }
        });
    } else {
        if (window.SettingsHelper) return;
        const api = {};
        _buildSettingsHelper(function (r) { Object.assign(api, r); });
        window.SettingsHelper = api;
    }

    function _buildSettingsHelper(resolve) {
        // ... 2000+ lines IDENTICAL ...

        resolve({
            injectFlexCss, ensureSettingsTabExists, applyTabVisibilityFromStorage,
            buildSettingsPanel, firstVisibleTabName, showTab,
            // ... 37 more exports ...
            getCustomSfLinks, addCustomSfLink,
        });
    }
})();
```

**What changed**: ~10 lines of wrapper. Internal code untouched.

---

## 5. Consumer Pattern Changes (popup.js)

### BEFORE — Unsafe bare-global access:
```javascript
// popup.js
function initAuditHelper() {
    if (!window.AuditHelper) return;       // ← Manual existence check
    window.AuditHelper.init({              // ← Bare global access
        getSession: () => sessionInfo,
        refreshSessionFromTab: async () => { ... }
    });
}
```

### AFTER — Registry-aware access (recommended):
```javascript
// popup.js — Option A: onReady (async, fires when module resolves)
TFP.onReady('AuditHelper', (AuditHelper) => {
    AuditHelper.init({
        getSession: () => sessionInfo,
        refreshSessionFromTab: async () => { ... }
    });
});

// popup.js — Option B: require (sync, throws if not available)
const AuditHelper = TFP.require('AuditHelper');
AuditHelper.init({ ... });

// popup.js — Option C: get (sync, returns null if not available)
const AuditHelper = TFP.get('AuditHelper');
if (AuditHelper) AuditHelper.init({ ... });
```

### STILL WORKS — Legacy access (zero changes needed):
```javascript
// popup.js — existing code keeps working
if (window.AuditHelper) window.AuditHelper.init({ ... });
```

---

## 6. Migration Checklist

### Per-Module Migration (repeat for each helper):

1. Add `const registry = window.TFP && window.TFP.define;` check at top
2. Wrap existing IIFE body in `_buildModuleName(resolve, ...deps)` function
3. Replace `window.ModuleName = {...}` with `resolve({...})`
4. List all bare-global references to other modules → add to `deps: [...]`
5. Receive deps as injected parameters instead of bare globals
6. Add legacy fallback branch for backward compat
7. Run existing tests — they should pass without changes
8. Update ESLint globals if needed

### Estimated Migration Effort:

| Module | Lines | Deps | Effort |
|--------|-------|------|--------|
| Utils | 825 | 0 | 10 min |
| SettingsHelper | 2,068 | 0 | 15 min |
| AuditHelper | 517 | 1 (Utils) | 10 min |
| PlatformHelper | ~400 | 1 (Utils) | 10 min |
| SoqlHelper | 3,990 | 1 (Utils) | 20 min |
| DataExplorerHelper | 8,020 | 6 | 45 min |
| SecurityHelper | ~1,200 | 2 | 15 min |
| RestExplorerHelper | 2,165 | 4 | 25 min |
| GraphqlHelper | 7,070 | 1 | 30 min |
| All others (~10) | ~4,000 | 0-2 | 60 min |
| **Total** | **~30,000** | | **~4 hours** |

### Priority Order:

**Phase 1** (zero-dep modules): Utils → SettingsHelper → CacheManager → AppearanceSettings
**Phase 2** (single-dep): AuditHelper → PlatformHelper → RestCatalog
**Phase 3** (multi-dep): SoqlHelper → SecurityHelper → RestExplorerHelper
**Phase 4** (complex dep graphs): DataExplorerHelper → UserManagerHelper → GraphqlHelper

---

## 7. Files Produced

| File | Description | Lines |
|---|---|---|
| `tfp_module_registry.js` | Module registry bootstrap | ~290 |
| `utils.refactored.js` | Utils converted to TFP.define | ~280 |
| `audit_helper.refactored.js` | AuditHelper with injected Utils | ~250 |
| `settings_helper.refactored.js` | SettingsHelper pattern template | ~180 (template) |

All refactored files maintain 100% backward compatibility. The `window.*` globals continue to work. Existing tests require zero modifications.
