---
id: PL-BYJ5
title: possessive_section_check's POSSESSIVE_RE quotes across a blank line, so a possessive naming a file followed by a quotation a paragraph break separates is read as one quotation equal to a heading, a false names-a-section report; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/possessive_section_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1371
payoff: make check stops refusing a correct sentence quotation that merely wraps across a paragraph break
verify: grep -q 'def test_a_quotation_split_by_a_paragraph_break_is_not_reported' tests/unit/test_possessive_section_check.py
recurrences: 2026-10-05 PL-T73L withdrawn 2026-10-05 PL-T73L
---

**Problem.** possessive_section_check's POSSESSIVE_RE quotes across a blank line, so a possessive naming a file followed by a quotation a paragraph break separates is read as one quotation equal to a heading, a false names-a-section report; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

The quotation `[^"]{2,200}?` under DOTALL crosses a blank line, so the lines below are read as the quotation "What this project is", which equals a heading:

```markdown
`CLAUDE.md`'s "What this

project is"
```

The opposite direction from `PL-R417`'s, and its only consequence is a false report; `PL-XW87`'s soft break, block quote and list indent forms still read right. Latent.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`: in a scratch tree whose `CLAUDE.md` holds the heading `## What this project is`, `possessive_section_check.sites` read a `docs/notes.md` holding the fenced form above, a possessive citation of `CLAUDE.md` whose quotation opens on "What this" and closes after a blank line on "project is". It returned one site at line 1, reporting that the quotation "What this project is" names a section and should be written with `§`, and declined nothing; `POSSESSIVE_RE`'s `quoted` group held `What this`, two newlines, then `project is`.

**Why it matters.** `make check` runs this tool and fails on every site it reports, so a sentence quotation that wraps across a paragraph break, and whose two halves together equal a heading of the cited file, would be refused, with a remedy that rewrites it as a section citation it is not. The false report is the only consequence, so it stops a correct commit rather than passing a wrong one. Latent: no live brief or document holds the shape today.

**Generator check.** An instance of `PL-R417`'s fact, where one statement ends: the quotation runs past the paragraph end that closes it, the direction `PL-4ZDZ`'s version list and `PL-FP7J`'s paragraph readers take, both members. The sweep that filed it placed it outside the head as the opposite direction; that direction is already in the head, so it belongs there. Not added to `PL-R417`'s `root-cause-of:` here, since that file is on the head's own branch; put to its thread. Recorded there by that head's link 8 (`#1358`, 2026-10-05).

**Done when.** `POSSESSIVE_RE`'s quotation stops at a paragraph end, a blank line in or out of a block quote, while `PL-XW87`'s soft break, block quote and list indent forms still read as one quotation. `test_a_quotation_split_by_a_paragraph_break_is_not_reported` in `tests/unit/test_possessive_section_check.py` gives `sites` the two-paragraph form above and gets no site back.
