# TrackForcePro: Test Architecture Strategy

## 1. Current State Assessment

### Baseline Metrics (Pre-Intervention)

| Metric | Before | Threshold | Status |
|---|---|---|---|
| Test Suites | 106 | — | — |
| Tests | 4,648 | — | — |
| Lines | 44.23% | 60% | ❌ Below |
| Statements | 41.95% | 60% | ❌ Below |
| Functions | 42.69% | 50% | ❌ Below |
| Branches | 33.69% | 40% | ❌ Below |

**Current thresholds in package.json are failing:** The configured thresholds (60/60/50/40) are not met. The test suite passes only because Jest doesn't fail on threshold violations when using `--runInBand --detectOpenHandles` without `--coverage` in the default npm test command.

### After This Session

| Metric | Before | After | Delta |
|---|---|---|---|
| Test Suites | 106 | 109 | +3 |
| Tests | 4,648 | 4,712 | +64 |
| Functional Passes | 4,644 | 4,708 | +64 |

---

## 2. Coverage Gap Analysis

### Biggest Gaps (Uncovered Lines)

| File | Lines % | Functions % | Branches % | Uncovered Lines | Priority |
|---|---|---|---|---|---|
| **background.js** | 9.9% | 12.5% | 8.0% | 1,036 | 🔴 Critical |
| **popup.js** | 24.2% | 21.3% | 17.3% | 1,141 | 🔴 Critical |
| **org_tools_helper.js** | 27.4% | 23.8% | 19.0% | 1,171 | 🟡 High |
| **settings_helper.js** | 25.1% | 21.7% | 14.0% | 711 | 🟡 High |
| **platform_helper.js** | 20.5% | 18.9% | 11.4% | 625 | 🟡 High |
| **data_explorer_tools.js** | 40.2% | 36.7% | 31.2% | 594 | 🟡 High |
| **graphql_helper.js** | 56.5% | 53.8% | 47.7% | 1,655 | 🟢 Medium (large file) |
| **soql_helper.js** | 68.4% | 60.9% | 51.5% | 1,198 | 🟢 Medium (large file) |
| **audit_helper.js** | 23.3% | 32.5% | 10.9% | 184 | 🟢 Medium (small file) |

### Well-Covered Files (>80%)

| File | Coverage | Notes |
|---|---|---|
| constants.js | 100% | Pure data |
| oauth_helper.js | 95% | Good tests |
| url_helper.js | 91.7% | Good tests |

### Untested Critical Paths (Before This Session)

| Path | File | Impact | Now Tested? |
|---|---|---|---|
| `sendMessageToSalesforceTab` | utils.js | Every feature | ✅ Yes (5 tests) |
| `getInstanceUrl` 4-source chain | utils.js | Every API call | ✅ Yes (8 tests) |
| `getSessionFromCookies` | utils.js | SW crash recovery | ✅ Yes (5 tests) |
| `runSoql` with pagination | background.js | SOQL execution | ✅ Yes (10 tests) |
| `runGraphql` with introspection | background.js | GraphQL execution | ✅ Yes (9 tests) |
| Cache TTL + org switch | cache_manager.js | Data isolation | ✅ Yes (24 tests) |
| `createRateLimiter` queue | utils.js | Bulk operations | ✅ Yes (3 tests) |
| `isInlineEditBlocked` 4-source | settings_helper.js | Edit guard | ❌ Not yet |
| `handleFetch` 3-level fallback | audit_helper.js | Audit trail | ❌ Not yet |
| popup.js tab orchestration | popup.js | UI routing | ❌ Not yet |

---

## 3. Test Architecture Issues

### Issue 1: eval()-Based Test Pattern

**108 test files** use `fs.readFileSync` + `eval()` to load IIFE modules. This works but has drawbacks: no source maps for errors, no code coverage attribution for inner functions, and module-level state leaks between tests.

**Current pattern:**
```javascript
const code = fs.readFileSync(path.join(__dirname, '../helper.js'), 'utf8');
eval(code);
const Helper = window.Helper;
```

**Problems:**
- Stack traces show `<anonymous>` instead of file:line
- Module state persists unless window global is manually deleted
- Dependencies must be loaded in correct order via multiple eval() calls
- `eval` content not tracked by Istanbul/V8 coverage in some configurations

**Recommended replacement pattern:**

```javascript
// test_loader.js — shared test utility
function loadIIFE(relativePath, dependencies = {}) {
    // Set up dependency globals
    for (const [name, mock] of Object.entries(dependencies)) {
        window[name] = mock;
    }
    // Clean previous instance
    delete window[/* helper name */];

    const code = fs.readFileSync(path.resolve(__dirname, '..', relativePath), 'utf8');
    eval(code);
    return window[/* helper name */];
}
```

**Migration path:** Don't replace all at once. For new tests, use the `loadIIFE` pattern. For existing tests, refactor incrementally when touching the file for other reasons.

### Issue 2: No Shared Test Infrastructure

Each of the 109 test files creates its own chrome mock from scratch. This means:
- 109 slightly different mock implementations
- No consistency in which APIs are mocked
- Callback-based vs Promise-based mocks used inconsistently
- Some mocks are incomplete (missing lastError simulation)

**Recommended: Create `tests/helpers/chrome_mock_factory.js`**

```javascript
// Structured mock factory with consistent behavior
function createChromeMock(overrides = {}) {
    const store = {};
    return {
        storage: { local: { get: jest.fn(...), set: jest.fn(...) } },
        tabs: { query: jest.fn(...), sendMessage: jest.fn(...) },
        runtime: { sendMessage: jest.fn(...), lastError: null },
        cookies: { getAll: jest.fn(...) },
        _store: store  // test inspection
    };
}
module.exports = { createChromeMock };
```

This was implemented in `utils_messaging_integration.test.js` as a proof of concept.

### Issue 3: Inconsistent Test Environment

Tests use a mix of `@jest-environment node` and `@jest-environment jsdom` without clear guidelines:
- Node: faster, no DOM, used for ES module files
- jsdom: slower, has DOM, needed for IIFE files that touch `document`

**Guideline:** Use `node` for pure logic tests (background.js functions, URL helpers). Use `jsdom` for anything that touches `window`, `document`, or `localStorage`.

### Issue 4: background.js Is Nearly Untestable

background.js is an ES module (uses `import`/`export`) but Jest is configured with `node` environment and babel-jest transform. The ES module imports from `constants.js` and `url_helper.js` make it impossible to `require()` directly.

**Current approach:** Extract individual functions by line range (as done in `background_api_fetch.test.js`).

**Better approach:** Refactor background.js to separate pure functions into a testable module:

```javascript
// background_core.js (new file — pure functions, no chrome.* dependencies)
export { runSoql, runGraphql, describeGlobal, describeSObject, ... };

// background.js (thin orchestrator)
import { runSoql, runGraphql, ... } from './background_core.js';
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => { ... });
```

This would let tests import `background_core.js` directly without regex extraction.

---

## 4. Coverage Improvement Roadmap

### Phase 1: Quick Wins (Target: 55% lines, 45% branches)

| Action | Files Affected | Est. New Tests | Coverage Lift |
|---|---|---|---|
| ✅ Utils messaging tests | utils.js | 21 | +3% lines |
| ✅ Background API tests | background.js | 19 | +2% lines |
| ✅ Cache lifecycle tests | cache_manager.js | 24 | +1% lines |
| Add settings_helper tests | settings_helper.js | ~30 | +3% lines |
| Add audit_helper tests | audit_helper.js | ~15 | +1% lines |

### Phase 2: Medium Effort (Target: 65% lines, 55% branches)

| Action | Files Affected | Est. New Tests | Coverage Lift |
|---|---|---|---|
| Extract background_core.js | background.js | ~40 | +5% lines |
| popup.js tab orchestration | popup.js | ~35 | +4% lines |
| platform_helper event streaming | platform_helper.js | ~20 | +2% lines |
| org_tools_helper panels | org_tools_helper.js | ~25 | +3% lines |

### Phase 3: Deep Coverage (Target: 70%+ lines, 65%+ branches)

| Action | Files Affected | Est. New Tests | Coverage Lift |
|---|---|---|---|
| data_explorer_tools sub-tabs | data_explorer_tools.js | ~30 | +2% lines |
| GraphQL autocomplete/builder | graphql_helper.js | ~25 | +2% lines |
| SOQL suggestion engine | soql_helper.js | ~20 | +1% lines |
| Create shared test setup | all new tests | — | — (quality) |

### Updated Coverage Thresholds

```json
{
  "coverageThreshold": {
    "global": {
      "lines": 70,
      "statements": 70,
      "functions": 65,
      "branches": 55
    }
  }
}
```

---

## 5. New Mocking Strategy

### Tier 1: Chrome Mock Factory (All Tests)

Every test file should use the shared factory instead of inline mocks:

```javascript
const { createChromeMock } = require('./helpers/chrome_mock_factory');
const chromeMock = createChromeMock({
    tabs: { query: jest.fn(() => Promise.resolve([{ id: 1, url: 'https://test.my.salesforce.com' }])) }
});
global.chrome = chromeMock;
```

### Tier 2: Salesforce API Simulator (Integration Tests)

For tests that exercise full request/response cycles:

```javascript
const { createSfApiSimulator } = require('./helpers/sf_api_simulator');
const api = createSfApiSimulator({
    objects: ['Account', 'Contact'],
    records: { Account: [{ Id: '001xx', Name: 'Acme' }] }
});
global.fetch = api.fetch;  // Intercepts and responds to SF API calls
```

### Tier 3: Module Loader (IIFE Tests)

```javascript
const { loadIIFE } = require('./helpers/module_loader');
const Helper = loadIIFE('helper.js', {
    Utils: mockUtils,
    chrome: chromeMock
});
```

---

## 6. Eval Replacement Strategy

**Don't replace eval globally.** It works, it's proven, and there are 108 files using it. Instead:

1. **New tests:** Use the structured `loadIIFE` pattern with explicit dependency injection.
2. **Existing tests being modified:** Opportunistically refactor to use the factory pattern.
3. **Long-term:** When background.js is split into `background_core.js`, those tests can use standard `require()`/`import`.

The eval pattern is acceptable for IIFE files because it accurately reproduces how the browser loads them (sequential `<script>` tags). The key improvement is **consistent mock setup** and **proper cleanup between tests**.

---

## 7. Files Produced in This Session

| File | Tests | Coverage Target |
|---|---|---|
| `tests/utils_messaging_integration.test.js` | 21 | utils.js messaging + session |
| `tests/background_api_fetch.test.js` | 19 | background.js SOQL + GraphQL |
| `tests/cache_lifecycle.test.js` | 24 | cache_manager.js full lifecycle |
| `TEST_ARCHITECTURE_STRATEGY.md` | — | This document |

**Total: 64 new passing tests, 0 regressions, 3 new test suites.**

---

## 8. Recommended Next Steps

1. **Create `tests/helpers/` directory** with shared `chrome_mock_factory.js`, `module_loader.js`, and `sf_api_simulator.js`.
2. **Add settings_helper tests** — the `isInlineEditBlocked` 4-source chain is a high-value target with complex branching.
3. **Extract background_core.js** — separating pure API functions from chrome.runtime listeners would unlock +5% coverage with minimal risk.
4. **Add CI coverage enforcement** — update `.github/workflows/code-quality.yml` to run with `--coverage` and fail on threshold violations.
5. **Track coverage over time** — add coverage badge to README and set up coverage trend reporting.
