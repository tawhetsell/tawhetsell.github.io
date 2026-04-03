# tawhetsell.github.io

Personal academic website for Travis A. Whetsell, deployed with GitHub Pages.

If a colleague wants to build a similar site of their own using AI assistance, they can start by handing it this file `SITE_WORKFLOW.md`. It is written as a reusable build-and-deploy guide.

## Site Files

- `index.html` - homepage structure and small client-side scripts
- `styles.css` - site styling, theme tokens, and layout
- `scholar-metrics.json` - citation metrics used by the Google Scholar cards
- `cv_whetsell_2026_03_26.pdf` - public CV linked from the site
- `wireframe_headshot_dark.png` - dark-mode portrait
- `wireframe_headshot_light.png` - light-mode portrait
- `SITE_WORKFLOW.md` - handoff guide for building a similar site for another person

## Maintenance Notes

- The site currently defaults to light mode on first visit.
- Theme preference is saved in `localStorage`.
- The Google Scholar cards load values from `scholar-metrics.json`.
- If the CV filename changes, update the links in `index.html`.

## Updating The Site

Typical content updates:

- edit `index.html` for copy, links, sections, and structure
- edit `styles.css` for visual changes
- edit `scholar-metrics.json` to refresh citation counts
- replace the CV PDF or portrait assets as needed

## Deploying

GitHub Pages deploys from the repository after pushing to `main`.

Typical flow:

```bash
git status
git add index.html styles.css scholar-metrics.json README.md SITE_WORKFLOW.md <assets>
git commit -m "Update site"
git push origin main
```

## Notes

- Built using ChatGPT 5.4 Extra High via Codex App
