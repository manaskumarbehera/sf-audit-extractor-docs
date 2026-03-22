# TrackForcePro Quick Reference

## Live App

**URL**: https://trackforcepro-97277a4f93a1.herokuapp.com/

## Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | AI agent instruction guide (modern tech stack, patterns, conventions) |
| `server.js` | Node.js HTTP server (no external deps) |
| `package.json` | Node.js configuration (v1.0.0, node >=20) |
| `Procfile` | Heroku process specification |
| `shared.css` | Shared docs design system and browser availability component |
| `theme.js` | Shared theme toggling and page helpers |
| `index.html` | Documentation hub / landing page |
| `documentation.html` | Multi-version canonical docs |
| `guide.html` | Trainer-facing learning path |
| `guide.md` | Docs maintenance guide and language rules |
| `quick-start-guide.html` | Installation workflow |
| `quick_guide.md` | Short maintainer and user quick reference |
| `help.html` | FAQ & troubleshooting |
| `quiz.html` | Interactive learning app |
| `leaderboard.html` | Quiz ranking page |
| `privacy-policy.html` | Legal document |

## Local Development

\`\`\`bash
# Start server locally
node server.js
# Open http://localhost:3000

# No build step needed - edit and refresh
# HTML: edit .html files
# CSS: modify shared.css
# JS: update theme.js or page-local scripts when needed
\`\`\`

## Deploy to Heroku

\`\`\`bash
# Commit changes
git add .
git commit -m "feat: description"
git push origin main

# Deploy
git push heroku main

# Monitor
heroku logs --tail --app trackforcepro
\`\`\`

## Tech Stack

- **Runtime**: Node.js 24.14.0 LTS (Heroku)
- **Region**: EU (heroku-24 stack)
- **Frontend**: Vanilla HTML5 + CSS + JavaScript
- **Design**: Shared docs system, Salesforce-inspired surfaces, responsive layout
- **State**: Browser localStorage only (quiz app)
- **Dependencies**: Zero external npm packages

## Design System

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | #0b1020 | Main background |
| `--primary` | #5aa9ff | Links, buttons |
| `--accent` | #7af5c8 | Highlights, badges |
| `--text` | #e8ecff | Text, headings |
| `--surface` | #121a31 | Cards, panels |

## Personal Branding

- **Buy Me Coffee**: https://buymeacoffee.com/manaskumarbehera
- **LinkedIn**: https://www.linkedin.com/in/manas-behera-68607547/
- **Portfolio**: https://www.manaskumarbehera.com/
- **GitHub Issues**: https://github.com/manaskumarbehera/sf-audit-extractor-docs/issues

## Critical Patterns

### Version Sync
- `manifest.json` is the version source of truth
- Run `node scripts/update-docs-version.js`
- Update docs copy and `DOCUMENTATION/CHANGELOG.md` when release messaging changes

### Cross-Page Consistency
- Navigation hardcoded per page
- Favicon IDs: `fav32`, `fav16`, `favshort`
- External links: keep URLs consistent
- Keep the 3-surface language consistent: launcher, workspace, overlays
- Keep command/search surfaces distinct: popup/workspace Command Palette, Command Palette (Page), Setup Search (Page), Metadata Explorer

### Quiz App (quiz.html)
- Global state, mode-specific
- localStorage keys: `tfp_quiz_player`, `tfp_quiz_leaderboard`
- Escape user names: `escapeHtmlLocal()`

## Editor Notes

The repo is synced from a private repository. If files are removed during sync, they can be restored by:

1. Checking git history: `git show <commit>:<filepath>`
2. Re-creating files with correct specs
3. Re-creating files with current docs patterns
4. Re-testing local docs behavior before any commit or deploy

## Troubleshooting

**App won't deploy to Heroku?**

1. Check package.json exists at root
2. Verify Procfile points to server.js
3. Confirm server.js listens on `process.env.PORT`
4. Run: `heroku buildpacks:clear --app trackforcepro && heroku buildpacks:set heroku/nodejs --app trackforcepro`
5. Push: `git push heroku main`

**Heroku logs show errors?**

\`\`\`bash
heroku logs --tail --app trackforcepro
\`\`\`

**Files synced away?**

\`\`\`bash
git log --oneline -- filename.ext       # Find last commit with file
git show <commit>:filename.ext          # View old version
# Recreate file and push
\`\`\`

---

**Last Updated**: March 16, 2026
**Status**: Live on Heroku EU
**Next Check**: Monitor logs for 7 days post-deployment
