# TrackForcePro Quick Reference

## 🌐 Live App
**URL**: https://trackforcepro-97277a4f93a1.herokuapp.com/

## 📁 Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | AI agent instruction guide (modern tech stack, patterns, conventions) |
| `server.js` | Node.js HTTP server (no external deps) |
| `package.json` | Node.js configuration (v1.0.0, node >=20) |
| `Procfile` | Heroku process specification |
| `assets/styles.css` | Glassmorphism dark theme (367 lines) |
| `assets/common.js` | Shared utilities (version switch, nav, YouTube embed) |
| `landing.html` | Hero landing page (route: `/`) |
| `index.html` | Documentation hub (route: `/docs`) |
| `documentation.html` | Multi-version canonical docs |
| `guide.html` | Visual guide with screenshots |
| `quick-start-guide.html` | Installation workflow |
| `help.html` | FAQ & troubleshooting |
| `quiz.html` | Interactive learning app |
| `privacy-policy.html` | Legal document |

## 🔧 Local Development

```bash
# Start server locally
node server.js
# Open http://localhost:3000

# No build step needed - edit and refresh!
# HTML: edit .html files
# CSS: modify assets/styles.css
# JS: update assets/common.js
```

## 🚀 Deploy to Heroku

```bash
# Commit changes
git add .
git commit -m "feat: description"
git push origin main

# Deploy
git push heroku main

# Monitor
heroku logs --tail --app trackforcepro
```

## 📊 Tech Stack

- **Runtime**: Node.js 24.14.0 LTS (Heroku)
- **Region**: EU (heroku-24 stack)
- **Frontend**: Vanilla HTML5 + CSS + JavaScript
- **Design**: Glassmorphism, dark Salesforce blue, responsive
- **State**: Browser localStorage only (quiz app)
- **Dependencies**: Zero external npm packages

## 🎨 Design System

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | #0b1020 | Main background |
| `--primary` | #5aa9ff | Links, buttons |
| `--accent` | #7af5c8 | Highlights, badges |
| `--text` | #e8ecff | Text, headings |
| `--surface` | #121a31 | Cards, panels |

## 🔗 Personal Branding

- **Buy Me Coffee**: https://buymeacoffee.com/manaskumarbehera
- **LinkedIn**: https://www.linkedin.com/in/manas-behera-68607547/
- **Portfolio**: https://www.manaskumarbehera.com/
- **GitHub Issues**: https://github.com/manaskumarbehera/sf-audit-extractor-docs/issues

## ⚡ Critical Patterns

### Multi-Version Docs
- Add `<option value="X.Y.Z">` in dropdown
- Add `<div id="content-X.Y.Z">` content block
- Update version strings everywhere (index, docs, footer)

### Cross-Page Consistency
- Navigation hardcoded per page
- Favicon IDs: `fav32`, `fav16`, `favshort`
- External links: keep URLs consistent

### Quiz App (quiz.html)
- Global state, mode-specific
- localStorage keys: `tfp_quiz_player`, `tfp_quiz_leaderboard`
- Escape user names: `escapeHtmlLocal()`

## 📝 Editor Notes

The repo is synced from a private repository. If files are removed during sync, they can be restored by:

1. Checking git history: `git show <commit>:<filepath>`
2. Re-creating files with correct specs
3. Committing: `git add . && git commit -m "restore: ..."`
4. Pushing: `git push origin main && git push heroku main`

## 🆘 Troubleshooting

**App won't deploy to Heroku?**
1. Check package.json exists at root
2. Verify Procfile points to server.js
3. Confirm server.js listens on `process.env.PORT`
4. Run: `heroku buildpacks:clear --app trackforcepro && heroku buildpacks:set heroku/nodejs --app trackforcepro`
5. Push: `git push heroku main`

**Heroku logs show errors?**
```bash
heroku logs --tail --app trackforcepro
```

**Files synced away?**
```bash
git log --oneline -- filename.ext  # Find last commit with file
git show <commit>:filename.ext     # View old version
# Recreate file and push
```

---

**Last Updated**: March 16, 2026  
**Status**: ✅ Live on Heroku EU  
**Next Check**: Monitor logs for 7 days post-deployment

