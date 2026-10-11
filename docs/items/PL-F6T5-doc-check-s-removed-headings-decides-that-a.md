---
id: PL-F6T5
title: doc_check's _removed_headings decides that a heading changed only where the patch removed rows inside the heading's base span, so a setext heading changed from outside its rows - a line added to its text, or the blank line above it removed so the paragraph joins it - leaves the old title off the candidates list; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: a setext heading retitled by a line added under it or a blank line removed above it lists its old title for the citation sweep, so a citation of it is not left naming a section no document has
verify: grep -q 'def test_a_setext_heading_changed_from_outside_its_rows_is_a_removed_title' tests/unit/test_doc_check.py
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

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, in a scratch git
repository holding the base and working copy above: `git diff -U0` gives one
row added under `Keep Title` and the blank line 7 removed, `_removed_headings`
returns an empty set, and the working copy's headings read as
`Keep Title now longer` and `Text. Other Head`.

**Why it matters.** `changed_tokens` lists the titles a branch removed so the
close-out sweep looks for citations of them elsewhere. A title missing from
that list is a citation the sweep never asks about, and it goes on naming a
section no document has.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1388`: the gap closed `PL-B47B`'s fix left. Latent - no tracked file holds the form - so it is an ordinary item
under the spent head, and one found live reopens it.

**Done when.** A heading counts as removed wherever its base title is absent
from the working tree's headings, whichever rows the patch touched, with a
test on both forms above.
