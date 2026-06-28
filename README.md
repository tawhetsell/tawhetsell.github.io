# tawhetsell.github.io

Personal academic website for Travis A. Whetsell, deployed with GitHub Pages.
Plain static HTML/CSS/JS — no framework, no server-side build step.

The site has three pages, reachable from the top nav:

- **Overview** — `index.html` (homepage)
- **Blog** — `blog/` (research notes and essays)
- **CV** — `cv/` (the CV PDF shown inline)

## Site files

- `index.html` — homepage structure and small client-side scripts
- `styles.css` — site styling, theme tokens, and layout (shared by every page)
- `scholar-metrics.json` — citation metrics used by the Google Scholar cards
- `cv/index.html` — CV page; embeds the CV PDF inline
- `cv_whetsell_2026_03_26.pdf` — the CV file shown on the CV page
- `blog/` — the blog (see `blog/README.md` for how it works)
- `build.py` — turns the blog's Markdown sources into HTML pages
- `.nojekyll` — tells GitHub Pages to serve files as-is (no Jekyll processing)
- `wireframe_headshot_dark.png` / `wireframe_headshot_light.png` — portraits

## Writing a blog post

You write posts in Markdown and run one command — you never edit HTML by hand.

1. Copy `blog/src/_template.md` to `blog/src/<your-slug>.md` and write the post.
2. Put any figures in `blog/assets/` and reference them from the Markdown.
3. Run `python build.py` from the repo root to generate the post page and refresh
   the blog index.

Full details, including the front-matter fields and supported Markdown, are in
`blog/README.md`.

## Maintenance notes

- The site defaults to light mode on first visit; the theme preference is saved in
  `localStorage`.
- The Google Scholar cards load values from `scholar-metrics.json` (with fallback
  values hardcoded in `index.html` — update both when refreshing the numbers).
- If the CV filename changes, update the references in `cv/index.html`.
- `build.py` only rewrites files whose content actually changed.

## Deploying

GitHub Pages deploys from the repository after pushing to `main`.

```bash
git status
git add -A
git commit -m "Update site"
git push origin main
```

## Notes

- Built using a combination of ChatGPT and Claude Code.
