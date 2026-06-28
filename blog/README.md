# Blog

You write posts in **Markdown** (`blog/src/*.md`) and run one command to generate the
styled HTML pages and the blog index. You never edit HTML by hand. The Markdown files are
the source of truth, so the writing stays portable if the host ever changes.

## To write a new post

1. **Make the file.** Copy `src/_template.md` to `src/<your-slug>.md` (any short, dashed
   name, e.g. `src/network-governance-notes.md`).

2. **Write it.** Fill in the front-matter at the top (between the `---` lines) and write the
   body in Markdown. Front-matter fields:
   - `title` — the post title (required)
   - `date` — `YYYY-MM-DD` (required; controls ordering on the index)
   - `status` — `published` shows it on the blog index; `draft` builds the page but keeps it
     off the index
   - `slug` — becomes `blog/<slug>.html` (defaults to the filename)
   - `excerpt` — one sentence shown under the title on the blog index
   - `subtitle` — optional one-liner under the title on the post page
   - `origin` — optional note shown in the post footer

3. **Add figures (optional).** Put image files in `blog/assets/` and reference them in the
   Markdown:

   ```markdown
   ![A description of the image](assets/your-image.jpg)

   > Source or caption text for the figure.
   ```

   An image on its own line becomes a framed figure; a `>` quote line right after it becomes
   the figure's caption.

4. **Build.** From the repo root, run:

   ```bash
   python build.py
   ```

   This regenerates every `blog/*.html` post page and rebuilds the post list on the index.
   Then commit and push.

## Markdown you can use

`## Heading` and `### Subheading` · paragraphs (blank line between them) · `**bold**` ·
`*italic*` · `` `code` `` · `[link text](https://url)` · `<https://url>` (bare link) ·
`- bullet` lists · `1.` numbered lists · `> quote` · `---` horizontal rule · images (above).

## Notes

- `build.py` uses only the Python standard library — nothing to install.
- The post list on `index.html` lives between the `<!-- POSTS:START -->` and
  `<!-- POSTS:END -->` markers and is overwritten on every build. Everything else on the
  index (the intro text, nav) is safe to edit by hand.
- `../styles.css` is shared with the homepage; blog styles live under the `/* Blog */`
  comment in that file.
- The root `.nojekyll` file keeps GitHub Pages serving everything as static files.
- Cross-posting to Substack: publish here first, then add an
  "originally published at traviswhetsell.com" backlink on Substack.
