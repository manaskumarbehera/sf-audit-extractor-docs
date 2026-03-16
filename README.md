# TrackForcePro Web (Heroku-ready)

This repo now runs as a Heroku web app without changing existing documentation pages.

## What was added
- `server.js`: lightweight static web server for Heroku.
- `package.json` + `Procfile`: Heroku runtime/start config.
- `landing.html`: modern entry page at `/` with guide + YouTube playlist placeholder.
- Existing docs stay unchanged and are available at `/docs` and direct HTML paths.

## Local run
```bash
node server.js
```
Open:
- `http://localhost:3000/` -> modern landing page
- `http://localhost:3000/docs` -> existing docs home (`index.html`)

## Create Heroku app in EU region
```bash
heroku login
heroku create trackforcepro --region eu
heroku git:remote -a trackforcepro
git push heroku main
heroku open
```

## Keep deployments in sync with main branch
Add these repository secrets for GitHub Actions:
- `HEROKU_API_KEY`
- `HEROKU_EMAIL`

Then use the workflow file `.github/workflows/heroku-deploy.yml` to auto-deploy on pushes to `main`.

