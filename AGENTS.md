# AGENTS.md

## Overview

**TrackForcePro Docs + Web Hub** is a modern Node.js-hosted documentation and interactive learning platform. It combines static HTML pages (docs, guides, privacy, quiz) with a lightweight Express-like server (`server.js`) for Heroku deployment and modern UX enhancements.

## Tech Stack & Deployment

- **Runtime**: Node.js LTS (v20+) on Heroku-24 stack in EU region
- **Server**: Custom minimal HTTP server (`server.js`) with routing and MIME-type handling
- **Frontend**: Vanilla HTML5 + shared CSS (`shared.css`) + vanilla JS (`theme.js`, `adaptive_quiz.js`)
- **UI Design**: Glassmorphism cards, dark Salesforce blue palette, responsive grid layouts
- **Hosting**: Heroku with GitHub Actions CI/CD (planned: PMD code quality checks)
- **State**: Browser localStorage only (quiz leaderboard, player names)

## Big-Picture Architecture

### Core Pages (Static HTML)

| File | Purpose | Key Features |
|------|---------|--------------|
| `landing.html` | Initial landing page | Hero CTA, feature highlights |
| `index.html` | Main hub/documentation home | Release notes, link catalog, version picker entry |
| `documentation.html` | Canonical long-form docs | Multi-version selector + `switchVersion()`, sidebar nav with section IDs |
| `guide.html` | Role-based training guide | Surface model, hands-on labs, trainer notes |
| `quick-start-guide.html` | Install + first-use workflow | Concise steps, integration flowchart |
| `help.html` | FAQ + troubleshooting | Searchable table, known issues, support links |
| `quiz.html` | Interactive learning app | Multiple game modes, localStorage leaderboard, HTML escaping via `escapeHtmlLocal` |
| `privacy-policy.html` | Legal document | Claims aligned with quiz signup copy, no external tracking |

### Server & Deployment

- **`server.js`**: Minimal Node.js HTTP server (no external frameworks)
  - Routes `/` -> `landing.html`, `/docs` -> `index.html` for clean URL aliases
  - Supports `.nojekyll` fallback for GitHub Pages testing
  - MIME-type detection for HTML, CSS, JS, images, JSON
  - URL normalization prevents directory traversal attacks
- **`Procfile`**: Heroku process specification (`web: node server.js`)
- **`package.json`**: Minimal metadata (v1.0.0, node >=20)

### Asset Pipeline

- **`shared.css`**: Shared design system, card layouts, navigation, badges, and responsive page scaffolding
  - Colors: `--bg` (#0b1020), `--primary` (#5aa9ff), `--accent` (#7af5c8)
  - Glassmorphism: backdrop-filter blur, subtle shadows
  - Responsive grid: `.grid`, `.col-8`, `.col-4`
- **`theme.js`**: Shared theme toggle and favicon helpers
- **`adaptive_quiz.js`**: Client-side quiz/game runtime
- **`icons/`**: Favicon set (16px-1024px) for Chrome Web Store compatibility
- **`screenshots/`**: Reference images for guide.html walkthroughs

## Critical Patterns & Conventions

### Multi-Version Documentation

- **`documentation.html`** version picker: `<select>` in header triggers `switchVersion(version)` JS function
- Each version has a `<div id="content-X.Y.Z" class="version-content">` block
- Sidebar `.sidebar-link` IDs must exactly match section IDs in active content (broken links = silent failures)
- **When adding release**: Update dropdown `<option value="X.Y.Z">` AND create corresponding content div

### Cross-Page State & Consistency

- **Version strings**: Duplicated in `index.html` (changelog), `documentation.html` (selector), page footers
- **Action**: Update ALL occurrences when bumping version (e.g., v1.4.5 -> v1.5.0)
- **Navigation**: Hardcoded per page (no shared template); if adding pages, update `<nav>` in each file
- **Favicon IDs**: Every page needs `id="fav32"`, `id="fav16"`, `id="favshort"` for GitHub Pages rewrite logic
- **External links**: Chrome Web Store, GitHub issues, LinkedIn, and buymeacoffee.com links appear on multiple pages; keep URLs consistent

### Quiz App (Standalone in `quiz.html`)

- State is global, mode-specific (`switchMode`, `startQuiz`, `startMatchGame`, `startLeaderboard`)
- **localStorage contracts**: `tfp_quiz_player` and `tfp_quiz_leaderboard` keys reset user data if changed
- **HTML escaping**: All user-rendered names must go through `escapeHtmlLocal()` to prevent XSS
- No server persistence; leaderboard is browser-local only

### Modern UI Patterns

- **Glassmorphism cards**: `.card` + backdrop-filter blur with rgba glass backgrounds
- **Hero sections**: Large responsive grids with accent gradients
- **Animations**: Page load fades, hover scale effects on links
- **Themes**: Light/dark variants driven by CSS variables and `theme.js`
- **Responsive**: Mobile-first `min(width, vw)` container constraints

## Heroku Deployment Workflow

### Prerequisites

1. Heroku CLI installed: `heroku login`
2. Repo origin set: `git remote add origin <github-url>`
3. Heroku app created: `heroku create trackforcepro --region eu` (EU stack)

### Deploy Steps

```bash
# From project root (must have package.json, Procfile, server.js)
git add .
git commit -m "Modernize: glassmorphism, guide, YouTube embeds, personal links"
git push origin main
git push heroku main    # Or connect GitHub for auto-deploy

# Verify
heroku logs --tail
heroku open             # Opens deployed app
```

### CI/CD Integration (GitHub Actions)

- Plan: Add PMD quality checks, ESLint for JS, Link validation
- Trigger on: PR to main, push to main
- Artifacts: Deploy logs to GitHub Pages if builds fail

## Developer Workflow

### Local Testing

```bash
# Start server on port 3000 (or custom PORT env var)
node server.js
# Open http://localhost:3000 in browser
```

### Editing Pages

- **HTML**: Edit `.html` files directly; server auto-reloads on refresh
- **CSS**: Modify `assets/styles.css`; changes apply immediately on reload
- **JS**: Update `assets/common.js` or inline `<script>` tags
- **No build step**: Changes are live after file save + page refresh

### Adding Features

1. **New page**: Create `.html` in root, update all `<nav>` elements, add favicon IDs
2. **Glassmorphism cards**: Use `.card` class + existing CSS variables
3. **YouTube embed toggle**: Add `data-youtube-id="<PLAYLIST_ID>"` button; `common.js` handles toggle via iframe injection
4. **Version content**: Add `<option value="X.Y.Z">` dropdown option + `<div id="content-X.Y.Z">` block
5. **External links**: Use full URLs (`https://buymeacoffee.com/...`, `https://linkedin.com/in/...`)

## Personal Links & Branding

- **Buy Me Coffee**: https://buymeacoffee.com/manaskumarbehera
- **LinkedIn**: https://www.linkedin.com/in/manas-behera-68607547/
- **Portfolio**: https://www.manaskumarbehera.com/
- **GitHub Issues**: https://github.com/manaskumarbehera/sf-audit-extractor-docs/issues

These appear in footer, hero CTAs, and help pages; update all occurrences if URL changes.

## Release History

### v1.9.6 — March 25, 2026

LMS Explorer redesign, beta phase launch, and stability improvements.

- **LMS detail pane architecture**: Channels render in the tree pane; selecting a channel shows schema, publish, and activity in the detail pane (same pattern as component selection). Replaces the old three-panel layout that was too wide.
- **LMS Beta badge & banner**: Purple "Beta" badge on LMS type pill and network filter; informational banner at top of LMS detail pane.
- **Network detail overflow fix**: Response panel no longer stretches when trace payloads contain long lines.
- **Extension context invalidated fix**: Inner try-catch in storage callbacks prevents uncaught errors after extension reload.
- **Files changed**: `content.js`, `manifest.json`, `CLAUDE.md`, `AGENTS.md`, `DOCUMENTATION/CHANGELOG.md`, `DOCUMENTATION/RELEASE_NOTES_v1.9.6.md`, `docs/index.html`
- **Tests**: 90 suites, 3,867 tests passing, zero lint warnings.

### v1.9.5 — March 25, 2026

LMS bridge rewrite, LWC Explorer live mode, SOQL relationship links, two-row header.

### v1.9.4 — March 24, 2026

LWC Explorer trace classification, large in-page editor, branded surfaces.

### v1.9.3 — March 24, 2026

Patch release: version sync, Edge submission artifacts, SOQL robustness.

## Known Limitations & Trade-Offs

- **No database**: All user quiz data is localStorage (lost on browser clear)
- **No API backend**: Static pages only; future webhook/form integrations would need service extension
- **No templating**: HTML repetition is intentional for GitHub Pages compatibility
- **Manual version management**: Version strings are duplicated; requires careful sync on release
- **Server simplicity**: `server.js` has no external deps (Express-like features are inline)
