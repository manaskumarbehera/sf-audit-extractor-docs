TrackForcePro — Docs Guide

This folder contains the public-facing HTML documentation for TrackForcePro. Use this guide to keep docs in sync with releases.

Files of interest
- index.html — Landing / marketing page
- quick-start-guide.html — Quick start for admins
- documentation.html — Full feature documentation
- help.html — FAQ / troubleshooting
- privacy-policy.html — Privacy policy

Keeping docs in sync
1. Bump version in `manifest.json`.
2. Run the docs updater to propagate the version into HTML files:

   node scripts/update-docs-version.js --changelog "Short description of changes"

3. Review `docs/` files and `DOCUMENTATION/CHANGELOG.md` for release notes.
4. Commit and push changes. Optionally run `npm run package` to build release zips.

Quick note about v1.8.7
- Small UI tweak: swapped positions for the Show All Data (green) and Setup Search (yellow) trigger buttons on record pages. See `content.js` for implementation details.

Contributing
- When adding new docs pages, place them under `docs/` and update the navigation links in `docs/index.html` and `docs/documentation.html`.
- Use the `scripts/update-docs-version.js` to keep version badges consistent.

