---
id: PL-F6T5
title: doc_check's _removed_headings decides that a heading changed only where the patch removed rows inside the heading's base span, so a setext heading changed from outside its rows - a line added to its text, or the blank line above it removed so the paragraph joins it - leaves the old title off the candidates list; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** doc_check's _removed_headings decides that a heading changed only where the patch removed rows inside the heading's base span, so a setext heading changed from outside its rows - a line added to its text, or the blank line above it removed so the paragraph joins it - leaves the old title off the candidates list; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s third part.
`changed_tokens` asks `_removed_headings` which headings a patch removed, and
it counts a heading only where the patch removed one of the rows of its base
span. A setext heading's text is a paragraph's lines (CommonMark 0.31.2
§ 4.3), so an added line under it, or a removed blank line above it, changes
the title without removing any of its rows (§ 4.8).

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against cmark-gfm 0.29, which renders the working copy below with
both old titles gone:

```text
base:
Intro para.

Keep Title
==========

Text.

Other Head
----------

working copy: "now longer" added under "Keep Title", and the blank line
above "Other Head" removed
```

`_removed_headings` returns nothing, while the tree's headings are now
`Keep Title now longer` and `Text. Other Head`; a citation of either old title
elsewhere is never listed as a candidate. Latent: the documents hold no setext
heading of their own (the front-matter form is `PL-WX79`).

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1388`: the gap closed `PL-B47B`'s fix left.

**Done when.** A heading counts as removed wherever its base title is absent
from the working tree's headings, whichever rows the patch touched, with a
test on both forms above.
