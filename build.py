#!/usr/bin/env python3
"""
build.py — turn Markdown in blog/src/*.md into styled blog post pages and
rebuild the blog index. No external dependencies (standard library only).

Usage:
    python build.py

What it does:
  - Reads every blog/src/*.md (files starting with "_" are ignored, e.g. _template.md).
  - Each file has a small front-matter block at the top (between --- lines):
        ---
        title: My Post Title
        subtitle: Optional one-liner
        date: 2026-07-01
        status: published        # "published" shows in the index; "draft" is built but not listed
        slug: my-post-slug       # becomes blog/my-post-slug.html
        excerpt: One-sentence summary shown on the blog index.
        origin: Optional note shown in the post footer.
        ---
  - Converts the Markdown body to HTML and writes blog/<slug>.html.
  - Rebuilds the post list in blog/index.html (newest first), published posts only.

Supported Markdown: ## / ### headings, paragraphs, **bold**, *italic*, `code`,
[links](url), <https://autolinks>, - bullet lists, 1. numbered lists, > quotes,
--- horizontal rules, and images. An image on its own line becomes a figure;
if a > quote line follows it, that quote becomes the figure's caption.
"""

import html
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "blog" / "src"
OUT = ROOT / "blog"
INDEX = OUT / "index.html"

# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

def parse_front_matter(text):
    """Return (meta_dict, body_str). Front matter is the block between the
    first two '---' lines."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta = {}
    i = 1
    current_list_key = None
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            i += 1
            break
        # list item under a previous "key:" line
        m_item = re.match(r"\s+-\s+(.*)$", line)
        if m_item and current_list_key:
            meta.setdefault(current_list_key, [])
            meta[current_list_key].append(m_item.group(1).strip())
            i += 1
            continue
        m_kv = re.match(r"([A-Za-z0-9_]+):\s*(.*)$", line)
        if m_kv:
            key, val = m_kv.group(1), m_kv.group(2).strip()
            if val == "":
                current_list_key = key  # a list will follow
                meta[key] = []
            else:
                current_list_key = None
                meta[key] = val
        i += 1
    body = "\n".join(lines[i:]).strip("\n")
    return meta, body

# ---------------------------------------------------------------------------
# Inline Markdown -> HTML
# ---------------------------------------------------------------------------

_FOOTNOTES = {}  # label -> footnote number, set per post in render_body()
_FOOTNOTE_SEEN = set()  # labels already referenced (so only the first gets the anchor id)

def render_inline(text):
    """Convert inline Markdown (code, links, autolinks, bold, italic) to HTML."""
    # Pull out inline code spans first so their contents are not formatted.
    code_spans = []

    def stash_code(m):
        code_spans.append(m.group(1))
        return f"\x00CODE{len(code_spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash_code, text)

    # Escape HTML special characters in the remaining prose.
    text = html.escape(text, quote=False)

    # [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        text,
    )
    # <https://autolink>  (the angle brackets are now &lt; &gt;)
    text = re.sub(
        r"&lt;(https?://[^&\s]+)&gt;",
        lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>',
        text,
    )
    # **bold** then *italic*
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    # [^label] footnote references -> superscript links
    if _FOOTNOTES:
        def fn_ref(m):
            label = m.group(1)
            num = _FOOTNOTES.get(label)
            if not num:
                return m.group(0)
            # Only the first reference to a footnote carries the id its back-link targets.
            if label in _FOOTNOTE_SEEN:
                id_attr = ""
            else:
                _FOOTNOTE_SEEN.add(label)
                id_attr = f' id="fnref-{num}"'
            return (
                f'<sup class="footnote-ref"{id_attr}>'
                f'<a href="#fn-{num}">{num}</a></sup>'
            )

        text = re.sub(r"\[\^([\w-]+)\]", fn_ref, text)

    # Restore inline code with escaped contents.
    def restore_code(m):
        i = int(m.group(1))
        return f"<code>{html.escape(code_spans[i], quote=False)}</code>"

    text = re.sub(r"\x00CODE(\d+)\x00", restore_code, text)
    return text

# ---------------------------------------------------------------------------
# Block Markdown -> HTML
# ---------------------------------------------------------------------------

IMG_RE = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*$")

def is_block_start(line):
    s = line.strip()
    # Note: only "1." may begin an ordered list (CommonMark rule). This stops a
    # hard-wrapped sentence that happens to start with a number + period
    # (e.g. "2023. In these figures...") from being mistaken for a list.
    return (
        not s
        or s.startswith("#")
        or s.startswith(">")
        or s.startswith("- ")
        or s.startswith("* ")
        or re.match(r"^1\.\s", s)
        or IMG_RE.match(s)
        or re.match(r"^(-{3,}|\*{3,})$", s)
    )

def render_body(body):
    global _FOOTNOTES, _FOOTNOTE_SEEN
    _FOOTNOTE_SEEN = set()
    # Pull out footnote definitions ("[^label]: citation text") and number the
    # references by order of first appearance in the body.
    defs = {}
    kept = []
    for line in body.split("\n"):
        m = re.match(r"^\[\^([\w-]+)\]:\s+(.*)$", line)
        if m:
            defs[m.group(1)] = m.group(2).strip()
        else:
            kept.append(line)
    body = "\n".join(kept)
    order = []
    for m in re.finditer(r"\[\^([\w-]+)\]", body):
        lbl = m.group(1)
        if lbl in defs and lbl not in order:
            order.append(lbl)
    _FOOTNOTES = {lbl: idx + 1 for idx, lbl in enumerate(order)}

    lines = body.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Heading
        m_h = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m_h:
            level = len(m_h.group(1))
            out.append(f"<h{level}>{render_inline(m_h.group(2).strip())}</h{level}>")
            i += 1
            continue

        # Image -> figure (with optional following > caption)
        m_img = IMG_RE.match(stripped)
        if m_img:
            alt, src = m_img.group(1), m_img.group(2)
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            caption = None
            if j < n and lines[j].strip().startswith(">"):
                cap_lines = []
                while j < n and lines[j].strip().startswith(">"):
                    cap_lines.append(re.sub(r"^\s*>\s?", "", lines[j]))
                    j += 1
                caption = " ".join(part.strip() for part in cap_lines).strip()
                i = j  # consume the caption block
            else:
                i += 1
            fig = ['<figure class="post-figure">']
            fig.append(f'  <img src="{src}" alt="{html.escape(alt, quote=True)}">')
            if caption:
                fig.append(f"  <figcaption>{render_inline(caption)}</figcaption>")
            fig.append("</figure>")
            out.append("\n".join(fig))
            continue

        # Blockquote (standalone)
        if stripped.startswith(">"):
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            text = " ".join(part.strip() for part in quote_lines).strip()
            out.append(f"<blockquote><p>{render_inline(text)}</p></blockquote>")
            continue

        # Unordered list
        if stripped.startswith("- ") or stripped.startswith("* "):
            items = []
            while i < n and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            li = "\n".join(f"  <li>{render_inline(it)}</li>" for it in items)
            out.append(f"<ul>\n{li}\n</ul>")
            continue

        # Ordered list (begins only at "1."; subsequent items may be 2., 3., ...)
        if re.match(r"^1\.\s", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s", "", lines[i].strip()).strip())
                i += 1
            li = "\n".join(f"  <li>{render_inline(it)}</li>" for it in items)
            out.append(f"<ol>\n{li}\n</ol>")
            continue

        # Paragraph: gather lines until a blank line or a new block start
        para = [stripped]
        i += 1
        while i < n and lines[i].strip() and not is_block_start(lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{render_inline(' '.join(para))}</p>")

    body_html = "\n\n          ".join(out)

    # Render the footnotes section (numbered, in order of appearance).
    if order:
        items = []
        for lbl in order:
            num = _FOOTNOTES[lbl]
            items.append(
                f'  <li id="fn-{num}">{render_inline(defs[lbl])} '
                f'<a class="footnote-back" href="#fnref-{num}" aria-label="Back to text">&#8617;</a></li>'
            )
        body_html += (
            '\n\n          <hr class="footnotes-sep">\n'
            '          <ol class="footnotes">\n' + "\n".join(items) + "\n          </ol>"
        )

    return body_html

# ---------------------------------------------------------------------------
# Page templates
# ---------------------------------------------------------------------------

def fmt_date(value):
    dt = datetime.strptime(value.strip(), "%Y-%m-%d")
    return dt, f"{dt:%B} {dt.day}, {dt.year}"

HEAD_AND_NAV = '''<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Travis A. Whetsell</title>
  <meta name="description" content="{description}">
  <script>
    (() => {{
      try {{
        const savedTheme = localStorage.getItem("theme");
        const theme = savedTheme === "dark" ? "dark" : "light";
        document.documentElement.dataset.theme = theme;
      }} catch {{
        document.documentElement.dataset.theme = "light";
      }}
    }})();
  </script>
  <meta name="theme-color" content="#ece8e1">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=IBM+Plex+Sans:wght@400;500;600&amp;family=Space+Grotesk:wght@500;700&amp;display=swap"
    rel="stylesheet"
  >
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <div class="page-shell">
    <header class="site-header">
      <a class="site-mark" href="../index.html#top" aria-label="Go to home">TAW</a>
      <nav class="site-nav" aria-label="Primary">
        <a href="../index.html">Overview</a>
        <a href="./" aria-current="page">Blog</a>
        <a href="../cv/">CV</a>
      </nav>
      <div class="header-actions">
        <button
          class="theme-toggle"
          id="theme-toggle"
          type="button"
          role="switch"
          aria-checked="true"
          aria-label="Switch to dark mode"
        >
          <span class="theme-toggle-indicator" aria-hidden="true"></span>
          <span class="theme-toggle-label" id="theme-toggle-label">Light</span>
        </button>
      </div>
    </header>
'''

THEME_SCRIPT = '''  <script>
    (() => {
      const root = document.documentElement;
      const toggle = document.getElementById("theme-toggle");
      const toggleLabel = document.getElementById("theme-toggle-label");
      const themeColor = document.querySelector('meta[name="theme-color"]');
      const themeColors = {
        dark: "#0b0d10",
        light: "#ece8e1"
      };

      function getTheme() {
        return root.dataset.theme === "light" ? "light" : "dark";
      }

      function applyTheme(theme) {
        root.dataset.theme = theme;

        if (toggle) {
          const isLight = theme === "light";
          toggle.setAttribute("aria-checked", String(isLight));
          toggle.setAttribute(
            "aria-label",
            isLight ? "Switch to dark mode" : "Switch to light mode"
          );
        }

        if (toggleLabel) {
          toggleLabel.textContent = theme === "light" ? "Light" : "Dark";
        }

        if (themeColor) {
          themeColor.setAttribute("content", themeColors[theme]);
        }
      }

      applyTheme(getTheme());

      toggle?.addEventListener("click", () => {
        const nextTheme = getTheme() === "dark" ? "light" : "dark";
        applyTheme(nextTheme);

        try {
          localStorage.setItem("theme", nextTheme);
        } catch {
          // Ignore storage failures and keep the in-memory theme.
        }
      });
    })();
  </script>
</body>
</html>
'''

def render_post(meta, body_html):
    title = meta.get("title", "Untitled")
    description = meta.get("description") or meta.get("excerpt", "")
    _, date_display = fmt_date(meta["date"])
    subtitle = meta.get("subtitle")
    origin = meta.get("origin")

    parts = [HEAD_AND_NAV.format(title=html.escape(title), description=html.escape(description, quote=True))]
    parts.append('''
    <main id="top">
      <article class="article">
        <a class="back-link" href="./">&larr; All posts</a>

        <header class="article-header">
          <div class="article-meta">
            <time datetime="{date_iso}">{date_display}</time>
          </div>
          <h1>{title}</h1>'''.format(
        date_iso=meta["date"].strip(),
        date_display=date_display,
        title=html.escape(title),
    ))
    if subtitle:
        parts.append(f'\n          <p class="article-subtitle">{html.escape(subtitle)}</p>')
    parts.append('''
        </header>

        <div class="prose">
          {body}
        </div>
'''.format(body=body_html))
    if origin:
        parts.append(f'''
        <footer class="article-footer">
          <p>{render_inline(origin)}</p>
        </footer>''')
    parts.append('''
      </article>
    </main>

    <footer class="site-footer">
      <p>Travis A. Whetsell</p>
      <p><a href="./">All posts</a></p>
    </footer>
  </div>
''')
    parts.append(THEME_SCRIPT)
    return "".join(parts)

def render_index_items(posts):
    items = []
    for p in posts:
        items.append(
            '''        <li class="post-list-item">
          <a class="post-link" href="{slug}.html">
            <time class="post-date" datetime="{date_iso}">{date_display}</time>
            <div>
              <h2 class="post-list-title">{title}</h2>
              <p class="post-excerpt">
                {excerpt}
              </p>
            </div>
          </a>
        </li>'''.format(
                slug=p["slug"],
                date_iso=p["date_iso"],
                date_display=p["date_display"],
                title=html.escape(p["title"]),
                excerpt=html.escape(p["excerpt"]),
            )
        )
    return "\n".join(items)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not SRC.exists():
        print(f"No source folder at {SRC}", file=sys.stderr)
        return 1

    published = []
    built = 0
    for md_path in sorted(SRC.glob("*.md")):
        if md_path.name.startswith("_"):
            continue
        meta, body = parse_front_matter(md_path.read_text(encoding="utf-8"))
        if "title" not in meta or "date" not in meta:
            print(f"  skip {md_path.name}: missing title or date")
            continue
        slug = meta.get("slug") or md_path.stem
        meta["slug"] = slug
        body_html = render_body(body)
        page = render_post(meta, body_html)
        status = meta.get("status", "published").lower()
        flag = "" if status == "published" else f"  ({status}, not listed)"

        # Only write when the output actually changes, so untouched posts are
        # left alone (no needless rewrites, no git churn).
        out_path = OUT / f"{slug}.html"
        if out_path.exists() and out_path.read_text(encoding="utf-8") == page:
            print(f"  unchanged blog/{slug}.html{flag}")
        else:
            out_path.write_text(page, encoding="utf-8", newline="\n")
            built += 1
            print(f"  built blog/{slug}.html{flag}")

        if status == "published":
            dt, date_display = fmt_date(meta["date"])
            published.append({
                "slug": slug,
                "title": meta["title"],
                "excerpt": meta.get("excerpt", ""),
                "date_iso": meta["date"].strip(),
                "date_display": date_display,
                "_dt": dt,
            })

    # Newest first
    published.sort(key=lambda p: p["_dt"], reverse=True)

    old_index = INDEX.read_text(encoding="utf-8")
    new_items = render_index_items(published)
    replacement = f"<!-- POSTS:START (auto-generated by build.py — do not edit by hand) -->\n{new_items}\n        <!-- POSTS:END -->"
    new_index, count = re.subn(
        r"<!-- POSTS:START.*?POSTS:END -->",
        replacement,
        old_index,
        flags=re.DOTALL,
    )
    if count == 0:
        print(
            "  WARNING: could not find <!-- POSTS:START --> ... <!-- POSTS:END --> "
            "markers in blog/index.html; index not updated.",
            file=sys.stderr,
        )
    elif new_index == old_index:
        print(f"  unchanged blog/index.html ({len(published)} posts listed)")
    else:
        INDEX.write_text(new_index, encoding="utf-8", newline="\n")
        print(f"  updated blog/index.html ({len(published)} posts listed)")

    print(f"Done. Wrote {built} changed post page(s).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
