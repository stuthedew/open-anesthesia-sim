---
id: PL-8BLJ
title: The README's PRE-RELEASE warning uses two H1 headings inside a blockquote, so GitHub's outline leads with them instead of the project name
priority: P2
effort: S
status: ready
classes: docs, ux
feature: project-introduction
touches: README.md
added: 2026-09-06
verify: python3 tools/doc_check.py check && ! grep -q '^> # ' README.md
---

**Problem.** `#394` added a pre-release banner above the README's title:

```markdown
> [!WARNING]
> # PRE-RELEASE
> # Work in Progress

# Open Anesthesia Simulator
```

That puts three `#` headings in the document, two of them inside a blockquote
and both above the one naming the project.

**Why it matters.** `PL-N092` recorded GitHub's own guidance that a README's
headings are navigation rather than decoration - the **Outline** menu on the
rendered page is generated from them. So the outline of the project's front
page now reads *PRE-RELEASE / Work in Progress / What it is for / ...*, with
the project's name not at the top of it, and a screen-reader user walking the
heading tree meets the same order. Using a heading level for emphasis rather
than for structure, and repeating the top level three times, is the specific
pattern accessibility guidance warns against. `README.md` sits on the
simulator side of `CLAUDE.md`'s two-standards line, so it is held to the
specialist standard.

**The banner itself is not in question** - the pre-release status belongs at
the top of the page, it agrees with the GitHub "About" field, and stating it
prominently is right for a clinically flavored tool. What is in question is
carrying it on heading syntax.

**Where.** `README.md:1-4`.

**Done when.** The pre-release warning is still the first thing on the page
and still visually prominent, `# Open Anesthesia Simulator` is the document's
only `#` heading, and GitHub's Outline for the page leads with the project
name. Bold text inside the existing `> [!WARNING]` callout carries the same
emphasis without entering the heading tree; the callout already renders with
its own warning styling.

**Notes.** Nothing in `make check` decides this - `tools/doc_check.py` reads
`README.md` for path citations and math delimiters, not heading structure.
Whether that is worth a check is part of this item; a rule as narrow as "only
one `#` per document" is decidable, but it would fire once and then never
again, which is the retirement test in `CLAUDE.md`.
