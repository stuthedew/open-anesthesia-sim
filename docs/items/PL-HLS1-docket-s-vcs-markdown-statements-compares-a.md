---
id: PL-HLS1
title: docket's vcs._markdown_statements compares a paragraph without the heading section it sits under, so a ref that deletes a heading between two sections - moving the paragraphs below it under the heading above - reads as holding nothing more, and stranded drops the edit; latent
priority: P3
effort: S
status: done
classes: defect
feature: stranded-report-fidelity
milestone: v0.5.24
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1447
payoff: a branch whose only change is a deleted heading, moving paragraphs into another section, stays reported by stranded instead of reading as holding nothing the base lacks
verify: grep -q 'def test_a_removed_heading_is_a_change_to_the_section_it_ended' subprojects/docket/tests/test_vcs.py
---

**Problem.** docket's vcs._markdown_statements compares a paragraph without the heading section it sits under, so a ref that deletes a heading between two sections - moving the paragraphs below it under the heading above - reads as holding nothing more, and stranded drops the edit; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.vcs`. `_within` and `_standing` compare
each statement with its list-item markers but not the section it sits in.

```text
base:            ref:
## Allowed       ## Allowed
x                x
## Refused       y
y
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16: `_within` is true and `_standing` answers `behind`, though `y` now
reads as allowed. Latent: no ref in a fresh checkout carries such an edit.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: with blank lines between
the blocks, `_within` of the ref's statements in the base's is true and
`_standing` answers `behind`.

**Generator check.** Not a member of `PL-R417`: a heading ends at its line
and a section is no CommonMark block, so this is the statement's context, not
where it ends. `PL-NGKW` is the block-level form.
Its fact is the `PL-BHVM` family's, whether the base already holds a ref's
change, read here as statements; filed after those heads closed, it and
`PL-NGKW`, which `PL-R417` recorded, are two forms, short of a generator.

**Why it matters.** `stranded` and `_superseded` decide on this comparison
whether a ref holds work the base lacks, and everywhere else `vcs.py` fails
toward leaving a path outstanding. Here a ref whose only change is a deleted
heading, which moves every paragraph under it into the section above and can
turn a refused rule into an allowed one, reads as holding nothing more, so
the report drops it rather than leaving it for a reader to compare.

**Done when.** A removed heading counts as a change to the statements of the
section it ended, so the form above reads as outstanding; a test pins it.

**Fixed 2026-10-12** in `#1447`. `_markdown_statements` reads each block
under every heading whose section holds it, outermost first, beside the list
items holding it: a section runs to the next heading of its level or above
that as many containers hold, or to the first block fewer containers hold. So
the form above reads as outstanding, and so do a cut sub-heading, a setext
heading and a heading inside a list item, while cutting a whole section, or a
heading with nothing under it, still reads as held by the base.
`test_a_removed_heading_is_a_change_to_the_section_it_ended` pins all six.
Measured on this repository's history before the change: 7 of 3,894
removal-only Markdown edits change answer, each now outstanding where the base
had since inserted a heading mid-section, the direction `vcs.py` fails toward
everywhere else, and none of 6,576 item-file standings.
