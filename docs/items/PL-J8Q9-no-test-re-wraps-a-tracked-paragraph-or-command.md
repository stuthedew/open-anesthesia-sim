---
id: PL-J8Q9
title: No test re-wraps a tracked paragraph or command and holds every check's answer unchanged, the metamorphic form of PL-R417's misread
priority: P3
effort: M
status: done
classes: test
feature: reader-checks
touches: tests/unit/test_doc_check.py
added: 2026-10-10
closed: 2026-10-12
pr: 1472
payoff: A reader that misreads a re-wrapped paragraph or re-split command fails a pull request instead of waiting for a sweep to find it, or the measured yield shows the test is not worth its code
verify: grep -qF 'Measured 2026-10-12: 2 of the 21 latent forms make it fail' docs/items/PL-J8Q9-no-test-re-wraps-a-tracked-paragraph-or-command.md
---

**Problem.** `PL-R417`'s misread is that a statement a format continues
across lines is read by its first physical line. Nothing tests the property
directly: re-wrapping a tracked paragraph, or re-splitting a shell or Makefile
command between words with backslash-newlines, should change no check's
answer. A metamorphic test of that kind needs no reference implementation.
The review left its yield unmeasured, and proposed keeping it only if at least
5 of link 23's twenty-one latent forms, written into a scratch copy of the
tree, make it fail.

**Found 2026-10-10** by the parsing review in `PL-R417`'s closing sweep thread
(link 23). The owner chose to have `PL-R417`'s last batch add the review's two
differential tests in CI, and this follow-up to be filed as an ordinary item.

**Reproduced 2026-10-11** on main at `16a20a4f`: no test re-wraps tracked text
and compares a check's answers. Searching `tests/unit/` and
`subprojects/docket/tests/` for `metamorphic` or `rewrap` finds only a
docstring in `test_doc_check.py` and `pr_body_check`'s case for a body GitHub
re-wrapped, neither of which re-wraps a tracked file. `PL-R417`'s guard,
`CONTINUED_STATEMENTS`, holds each reader to hand-written continuation forms,
not to the tree re-wrapped.

**Why it matters.** `PL-R417` closed spent on the ground that further members
are found only by sweeping for forms no tracked file holds. A metamorphic test
is that sweep run on every pull request with no reference implementation to
maintain, so a reader that misreads a re-wrapped statement fails CI instead of
waiting for the next sweep. Whether it catches enough to earn its code is the
measurement the problem names, and the item is closed either way.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** A test re-wraps tracked paragraphs and re-splits commands, and
holds every check's answer unchanged, or the yield measured as above says it
is not worth its code.

**Measured 2026-10-12: 2 of the 21 latent forms make it fail, under the bar
of 5, so the test is not built and the item closes on the measurement.** Each
form was written into a copy of the tree at `16a20a4f`, where every brief
re-confirmed it, and its misread reproduced there. Four transforms were then
applied to the file holding it: every paragraph joined onto one line, every
paragraph broken at each space that opens no block, every backslash-continued
command joined, and every simple command split between its words. The checks
`make check` runs over the tree - `doc_check.py check`, `bin/docket check`,
`dead_ends.py check` and nine `tools/*_check.py` scripts, `fixture_id_check.py`
among them - were compared, line numbers stripped, between the original and
each transform, and a difference counted only where a control copy given the
same transform without the form did not show it. Ruff, mypy, the rest of
pytest and the checks that read a branch or a pull request were not run.

- Caught: `PL-BVBB` (`bin/docket check`'s prerequisite window, under both
  paragraph transforms) and `PL-S4JL` (`fixture_id_check`'s fence join, under
  the joined commands). `PL-TJ1S` moves only `make check`'s Markdown reference
  test, which already fails on the form as written, so it adds nothing.
- Reached by a tree check but not caught (12): `PL-7454` (an HTML block, which
  no transform moves), `PL-4J5H` and `PL-J8ML` (front matter), `PL-Q8LJ` (a
  whitespace-collapsing comparison), `PL-9TZH` (silent however it is wrapped),
  `PL-W9VC` (a top-level comment, not a recipe line), `PL-7CQ5`, `PL-0CJC` and
  `PL-GJKN` (compound commands and here-document bodies, which a split leaves
  alone), `PL-703R` (an underline no check reads), and `PL-DQ9C` and `PL-L4X3`
  (each difference is a correct refusal disappearing, the same at the branch
  head where the misread is fixed).
- Reached by no tree check (6): `PL-F6T5` (`doc_check.py candidates`, a diff
  against a base), `PL-PNZB` and `PL-4DM0` (`docket verify`'s diff audits),
  `PL-63Y5` (a ref reader), `PL-6KHQ` (`docket release`) and `PL-QLQF`
  (`pr_body_check.py --compare`; `make check` runs `--anchors`).

The controls also show the transforms are not answer-preserving for four
checks by design, so a test would need an exclusion for each on top of its
transforms: a line citation into a file the join shortens (`docs/MODEL.md`,
`ROADMAP.md`), `docs/dead-ends.md`'s one line per entry, the coverage gate's
exact-text comparison, which holds the Makefile and CI to splitting a command
alike (`check_coverage_gate`), and the sentence `bin/docket check` quotes.
