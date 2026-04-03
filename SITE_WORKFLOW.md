# Personal Site Workflow

This document captures the workflow used to build a faculty/personal website like this one. It is written as a handoff guide for a coworker who wants a similar site, but with her own content, visual direction, and GitHub setup.

## Goal

Build a lightweight personal website on GitHub Pages using plain HTML, CSS, and a small amount of JavaScript.

Recommended stack:

- `index.html` for structure
- `styles.css` for visual design
- image/PDF assets stored in the repo
- optional small JSON files for data that may change over time, such as citation metrics

This approach is fast, easy to maintain, and well-suited to academic/personal websites.

## 1. GitHub Setup For A New User

If the person does not already have GitHub:

1. Create a personal GitHub account: [Creating an account on GitHub](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github)
2. Verify the email address used for the account.
3. Enable 2FA for security: [Getting started with your GitHub account](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account)
4. Install Git locally: [Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git)
5. Optionally install GitHub Desktop if she prefers not to use the terminal.

Recommended local Git setup:

```bash
git config --global user.name "Full Name"
git config --global user.email "GITHUB_NOREPLY_EMAIL"
```

If GitHub blocks a push because of private email settings, use the GitHub-provided `noreply` email and amend the last commit:

```bash
git config user.email "GITHUB_NOREPLY_EMAIL"
git commit --amend --reset-author --no-edit
git push origin main
```

Reference: [GitHub email addresses reference](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference)

## 2. Repository And GitHub Pages Setup

For a personal site, the cleanest setup is a user site repository named:

```text
<github-username>.github.io
```

For example:

```text
janeprofessor.github.io
```

GitHub Pages quickstart:

- [Quickstart for GitHub Pages](https://docs.github.com/en/pages/quickstart?library=true)
- [What is GitHub Pages?](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages?hmsr=joyk.com)

Notes:

- On GitHub Free, GitHub Pages works for public repositories.
- If she wants a personal site at `https://<username>.github.io/`, the repository name should match the username exactly.

## 3. Gather Content Before Building

Ask for the following before writing the first version:

- current CV PDF
- editable CV source if available
- short biosketch
- current appointment
- previous appointments
- education
- selected publications with DOI links
- external links such as Google Scholar, university profile, GitHub, ResearchGate
- teaching list
- press/policy coverage links
- one or more headshots
- whether the site should default to dark or light mode

Important:

- If there is an editable CV source, use that for CV changes.
- Do not edit a PDF directly unless there is no better option and the user explicitly wants that.
- If the PDF filename changes, update the website links to match the actual filename.

## 4. Ask About Style Before Building

Do not assume the site should look like this one. Ask the user for style direction first.

Questions to ask:

- Do you want dark mode, light mode, or both?
- Which mode should be the default on first visit?
- Do you want a more editorial, academic, minimal, technical, or portfolio-like feel?
- Are there example websites you like?
- Do you want a grid, large typography, cards, portraits, motion, or a stricter black-and-white look?
- Do you want the site to feel formal or more personal?
- Which sections are essential and which are optional?
- Do you want a headshot, and if so, should it be treated normally, grayscale, or stylized?

Good prompt to gather direction:

```text
Please share:
1. your preferred visual direction,
2. whether you want dark mode, light mode, or both,
3. 2 to 5 example websites you like,
4. the sections you want on the homepage,
5. anything you definitely do not want.
```

## 5. Recommended Build Workflow

Use this sequence:

1. Read the CV and extract core themes, appointments, education, teaching, publications, and public-facing impact.
2. Build a first-pass homepage in plain HTML/CSS.
3. Keep the first version structurally sound and visually coherent, but simple.
4. Iterate with the user in small passes:
   - change copy
   - adjust layout
   - refine colors and mode defaults
   - replace assets
   - add links and publication lists
5. Keep the content editable and transparent. Avoid overengineering.

Recommended files:

- `index.html`
- `styles.css`
- image assets
- `scholar-metrics.json` or similar if metric cards are needed

## 6. Good Design Process

A good first pass should:

- establish typography and hierarchy clearly
- create a strong landing section
- keep sections easy to scan
- make the CV and external links obvious
- use restrained styling unless the user explicitly wants something more expressive

When iterating:

- respond quickly to negative feedback on style
- remove weak or overly descriptive copy when the user asks
- prefer fewer, better sections over too much explanatory text
- keep cards and section headings purposeful

## 7. Suggested Homepage Content Structure

This structure worked well and is reusable:

- Hero section
  - name
  - title/appointment
  - CV button
  - selected work button
  - short biosketch
- Profile card
  - appointment
  - previous appointments
  - education
  - portrait
- External links section
- Research section
  - 3 theme cards
  - selected publications
- Teaching section
  - current institution courses
  - previous institution courses
- Impact section
  - citation/metric cards
  - press/policy links
- Acknowledgements or footer

## 8. Handling Citation Metrics

For Google Scholar metrics, the most practical short-term approach is:

- store the numbers in a local JSON file
- load them into cards on the site
- update the JSON manually or later with automation

Example file:

```json
{
  "source": "Google Scholar",
  "profile_url": "https://scholar.google.com/...",
  "as_of": "April 3, 2026",
  "metrics": {
    "citations": 1443,
    "h_index": 18,
    "i10_index": 21
  }
}
```

Important:

- Google Scholar does not provide a clean public API for this use case.
- A GitHub Action can update the JSON periodically, but scraper-based automation may fail occasionally.
- If stability matters more than matching Scholar exactly, OpenAlex is easier to automate but may report lower counts.

## 9. Deployment Workflow

Before pushing:

1. Run `git status`
2. Confirm only the intended site files are staged
3. Make sure ignored files were not already committed
4. Verify links to PDFs and assets use the actual filenames in the repo

Basic publish flow:

```bash
git status
git add index.html styles.css scholar-metrics.json <assets>
git commit -m "Update personal website"
git push origin main
```

If files were added before they were listed in `.gitignore`, untrack them:

```bash
git rm --cached path/to/file
git commit --amend --no-edit
```

## 10. Live-Site QA Checklist

After deployment, check:

- homepage loads
- CSS is loading
- portrait images load
- CV link works
- external profile links work
- publications link to the intended DOI pages
- theme toggle works and preserves preference
- the default theme is correct on first visit
- no stale filenames remain in links

If using a dated CV filename, verify that the site points at the dated file rather than an older generic name.

## 11. Practical Lessons From This Build

- Keep the site plain HTML/CSS unless there is a clear reason to add a library.
- Ask for visual references early.
- Do not overcommit to decorative motifs until the user sees them.
- If the user dislikes a visual experiment, remove it quickly and simplify.
- Treat copy as editable design material, not fixed text.
- For academic sites, the combination of biography, publications, teaching, and external links usually matters more than advanced interactivity.
- Keep CV handling explicit. PDF naming and link consistency matter.
- If a file should stay out of version control, add it to `.gitignore` before the first commit.

## 12. Prompt Template For Building A Coworker Site

Use this prompt with Codex or another coding assistant:

```text
The workspace contains my CV and website repo. Please inspect my CV first and build a first-pass academic personal website in plain HTML/CSS for GitHub Pages.

Requirements:
- Ask me for style direction before locking the design.
- Use my CV to extract appointments, education, research themes, teaching, selected publications, and public impact.
- Keep the site easy to maintain.
- Prefer plain HTML/CSS/JS unless there is a compelling reason to add a dependency.
- Include a CV link and external profile links.
- If I provide example sites, use them as visual references.
- If I provide dark/light preferences, follow them exactly.
- If a citation card is added, store metrics in a local JSON file rather than hardcoding them everywhere.
- If the repo only contains a CV PDF and not an editable source, do not edit the PDF directly unless I explicitly ask.

Before building, ask me:
1. what visual direction I want,
2. whether I want dark mode, light mode, or both,
3. which sections I want on the homepage,
4. which websites I want used as references,
5. what I definitely do not want.
```

## 13. Source Links

These GitHub instructions were checked against official GitHub documentation on April 3, 2026:

- [Creating an account on GitHub](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github)
- [Getting started with your GitHub account](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account)
- [Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git)
- [Quickstart for GitHub Pages](https://docs.github.com/en/pages/quickstart?library=true)
- [What is GitHub Pages?](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages?hmsr=joyk.com)
- [Email addresses reference](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference)
