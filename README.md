# TrackForcePro Web Project

Modernized static documentation and quiz website for TrackForcePro, deployable on Heroku and compatible with GitHub Pages-style paths.

## Project layout
- `landing.html` -> Heroku landing page at `/`
- `index.html` -> docs home hub
- `documentation.html` -> versioned canonical docs
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
