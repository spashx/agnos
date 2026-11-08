---
name: agnos-meta-website
description: "AGNOS maintainer skill. Builds the AGNOS presentation website, a guided tour of the demo's Performance Center for CIOs, in English and French, from the Markdown text and the images of its assets, with the demo Performance Center page. USE FOR: regenerating the site after AGNOS, its demo or the site's text evolves. It writes a folder only: committing and publishing it stay with the maintainer."
argument-hint: "build --demo <demo repository> --out <folder>"
---

<!-- FTR-WEB-001; RQ-WEB-001, RQ-WEB-003, RQ-WEB-016 / ADR-WEB-001 (DEC-WEB-001, DEC-WEB-003, DEC-WEB-006) -->
# AGNOS Presentation Website

`<skill-folder>` is the folder holding this file. Run from any folder; Python's standard library only.

## Build

`python -I <skill-folder>/scripts/build_site.py build --demo <demo repository> --out <folder>`

| Argument | Meaning |
|---|---|
| `--demo <folder>` | The demo repository (`agnos-lightweight-process.demo`, built by `agnos-meta-demo`): its index is measured |
| `--out <folder>` | Where the site is written, typically the working copy of `spashx/agnos.site` |

- Exit `0`: the site is written; show the summary line.
- Exit `1`: nothing is written; each error names its file and its field. Correct the content, never the checks.

## Changing the site

Everything the reader sees comes from `assets/`:

| Path | Content |
|---|---|
| `assets/content/en.md`, `assets/content/fr.md` | The text, one `##` section per page element and one `###` field per text, the same in both files; the header comment of each file gives the format |
| `assets/screens/*.png` | The images the content links to; replace a file by one of the same name |
| `assets/template.html` | The page's layout, without text |

To change a word, edit the Markdown and build again. To add a field, add it to both languages and give it an element in
the template: the build refuses a field one language lacks or the template does not use.
