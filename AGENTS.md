# AGENTS.md

## Scope and stack
- This repo is a **static documentation site** for TrackForcePro; there is no build system, package manifest, or test runner in this repo.
- Primary surface: standalone HTML files at project root (`index.html`, `documentation.html`, `quick-start-guide.html`, `help.html`, `privacy-policy.html`, `quiz.html`).
- Hosting assumption is GitHub Pages (`.nojekyll` exists), so pages must work from both repo root and `/repo-name/` paths.

## Big-picture architecture
- `index.html` is the landing hub linking all pages and carrying latest release highlights/changelog snippets.
- `documentation.html` is the canonical long-form doc with a multi-version UI: version picker + `switchVersion(version)` toggles `div.version-content` blocks (`id="content-<version>"`).
- `quick-start-guide.html` and `help.html` are workflow-focused pages; content mirrors key feature claims from `documentation.html`.
- `quiz.html` is a self-contained app (large inline CSS+JS) with multiple game modes, local signup, and local leaderboard.
- `privacy-policy.html` is the legal page; it repeats core privacy claims that must stay aligned with help/docs/quiz signup copy.

## Cross-page conventions you must preserve
- Favicon compatibility snippet is repeated on every page; keep ids `fav32`, `fav16`, `favshort` and GitHub Pages rewrite logic intact.
- Navigation is hardcoded per page (no shared template). If you rename/add pages, update nav links in each file manually.
- Most pages use Salesforce blue palette and card styling; keep visual tokens close to existing variables to avoid style drift.
- Version/date strings are duplicated across files (example: `index.html` changelog + `documentation.html` selector/header + page footers). Update all relevant occurrences together.

## Critical file-specific patterns
- `documentation.html`: sidebar anchors (`.sidebar-link`) must match section ids in active version content; broken ids silently break navigation and active-state observer.
- `documentation.html`: when adding a release, add both `<option value="x.y.z">` and corresponding `id="content-x.y.z"` block; keep default active content consistent.
- `quiz.html`: state is global and mode-specific (`switchMode`, `startQuiz`, `startMatchGame`, etc.); avoid introducing cross-mode side effects.
- `quiz.html`: localStorage keys are contract-like (`tfp_quiz_player`, `tfp_quiz_leaderboard`); changing keys resets user data.
- `quiz.html`: user-provided names are escaped through `escapeHtmlLocal`; keep this behavior for any new rendered user text.

## Developer workflow in this repo
- Local preview is file-based; open `index.html` directly in a browser for quick checks.
- Optional safer preview for relative links: run a simple static server from repo root (for example `python3 -m http.server 8000`) and open `/index.html`.
- There are no automated tests/lints here; validation is manual smoke testing across all pages and links.

## Integration points and external dependencies
- External links: Chrome Web Store and GitHub issues/repo URLs appear on multiple pages; keep URLs consistent.
- Asset dependencies are local under `icons/` (favicons) and `screenshots/` (currently minimal usage).
- `quiz.html` persists player/leaderboard data only in browser localStorage; no backend API exists in this repo.

## Discovered AI-instruction sources
- A glob search for existing AI instruction files (`.github/copilot-instructions.md`, `AGENT*.md`, `CLAUDE.md`, `.cursorrules`, etc.) returned no matches in this workspace.

