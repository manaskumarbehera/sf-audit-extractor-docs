# TrackForcePro Web Project

Modernized static documentation and quiz website for TrackForcePro, deployable on Heroku and compatible with GitHub Pages-style paths.

## Project layout
- `landing.html` -> Heroku landing page at `/`
- `index.html` -> docs home hub
- `documentation.html` -> versioned canonical docs
- `guide.html` -> richer visual guide with screenshots + toggle-ready YouTube embed
- `quick-start-guide.html` -> installation and onboarding
- `help.html` -> support and troubleshooting
- `privacy-policy.html` -> legal/privacy page
- `quiz.html` -> interactive quiz + feature match + local leaderboard
- `assets/styles.css` and `assets/common.js` -> shared UI and behavior

## Run locally
```bash
node server.js
```

Open:
- `http://localhost:3000/` (modern landing)
- `http://localhost:3000/docs` (docs home)
- `http://localhost:3000/guide` (visual guide)

## Heroku setup (EU)
```bash
heroku login
heroku create trackforcepro --region eu
heroku buildpacks:set heroku/nodejs --app trackforcepro
git push heroku main
heroku open --app trackforcepro
```

## GitHub Actions deploy (optional)
Set repository secrets:
- `HEROKU_API_KEY`
- `HEROKU_EMAIL`

Then use `.github/workflows/heroku-deploy.yml` to deploy on pushes to `main`.

## CI checks in GitHub Actions
The same workflow now runs CI checks on `push` and `pull_request` to `main` before deploy:
- PMD JavaScript static analysis (`category/ecmascript/errorprone.xml`, `bestpractices.xml`)
- Quota guardrails for max HTML/JS file size and total repo size
- Local route smoke checks using `server.js` (`/`, `/docs`, `/guide`, docs/help/privacy/quiz pages)

