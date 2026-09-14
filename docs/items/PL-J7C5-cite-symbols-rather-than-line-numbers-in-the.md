---
id: PL-J7C5
title: Cite symbols rather than line numbers in the contrast table's reasons
priority: P3
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.22
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-02
closed: 2026-09-14
pr: 552
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_a_line_number_citation_is_refused' tests/unit/test_contrast_check.py
---

**Problem.** Each `Requirement` in `tools/contrast_check.py`'s `REQUIREMENTS`
table names where its colour pair appears by file and line —
`(simulation_view.py:532, :556, :595)`. Nothing checks those numbers, and any
edit above them moves what they point at. Found while working PL-8M05: the
`INK`/`PANEL` and `MUTED`/`PANEL` entries were pointing about ninety lines off
their subjects, having drifted across several unrelated changes, and the drift
was invisible until someone followed one.

**Why it matters.** `.claude/rules/ui-color.md` makes the requirement table
the specification for what gets checked, and the reason string is how a
reviewer confirms the pair named is the pair on screen. A citation that points
at unrelated code costs that reviewer the lookup and, worse, can be read as
saying the pair appears somewhere it does not. Refreshing them by hand is the
same work again after the next edit.

**Where.** `tools/contrast_check.py`, the `reason` field of each `Requirement`
in `REQUIREMENTS`.

**Approach.** Cite the symbol instead — `_build_metric_panel`,
`_build_chart_panel`, `_build_metric_value` — which does not move when lines
above it do. `tools/doc_check.py` already decides the dangling-citation
question for paths and could be extended to assert each cited symbol still
exists in the cited module, which turns a drifting comment into a checked one
for a few lines of standard library. Whether that extension is worth building,
or whether symbol names alone are enough, is the judgment in this item.

**Done when.** No reason string in `REQUIREMENTS` names a line number, and
either the symbols it names are checked by `make check` or the item records
why they are not.

**The same drift is in `docs/items/`, with fresh evidence** (recorded
2026-09-02 while working `PL-VG7G`). `PL-YMY7` cited "lines 402, 472-486,
529-539, 572, 621, 650, 724, 795, 1162-1168" of `app/simulation_view.py` on
2026-08-25. Re-measured 2026-09-02 they were eleven statements at entirely
different lines, and `PL-8M05` moved them again the same day - twice stale
inside nine days, in an item whose whole finding *is* which lines those are.

So the scope worth considering is not only the requirement table: item bodies
cite line numbers routinely, nothing checks them, and a reader who trusts one
is sent to unrelated code. The approach above covers both without changing -
`tools/doc_check.py` already decides the dangling-citation question for paths
across the documentation tree, and asserting that a cited symbol still exists
in the cited module is the same kind of question asked of a different token.
Worth deciding as one mechanism rather than two, and worth noting that item
files are the larger surface.

## Worked 2026-09-14: the requirement table is done, the item files are refused on a count, and this item's own `verify:` could never have passed

**The requirement table half is built, by `PL-GJDW` rather than here.** No
`reason` in `REQUIREMENTS` names a line number; `check_citations` refuses one
outright through `LINE_CITATION_RE` and resolves every cited symbol against
`app/theme.py` and `app/simulation_view.py` with `ast`. Both halves are tested -
`test_a_line_number_citation_is_refused` and, against the real tree rather than
a fixture, `test_every_requirement_names_a_symbol_that_exists`. That is the
"extend `tools/doc_check.py`" option this brief proposed, landed in
`contrast_check.py` where the table it guards lives.

**This item's `verify:` command could never have passed, and is corrected.**
`! grep -qE '[.]py:[0-9]' tools/contrast_check.py` matches exactly one line -
`tools/contrast_check.py:85`, the comment that documents `LINE_CITATION_RE` by
showing the form it refuses. A pattern cannot document itself without
containing an instance, so the command failed on the presence of the guard
rather than on its absence. It now names the test instead. Written away from
the work and never run, which is the failure the skill's `verify:` section
describes.

### The item-file half: refused, on the count this project asks for before tightening anything

The brief says item bodies "cite line numbers routinely, nothing checks them",
names item files "the larger surface", and asks whether the same mechanism
should cover them. Measured 2026-09-14 across `docs/items/`:

| | |
| --- | --- |
| `path.py:N` citations in item files | **268** across 103 files |
| whose path resolves in the tree | 264 |
| whose **line** is past end of file | **0** |
| whose **path** no longer exists | 4 |

**A line-existence check would catch nothing.** Zero of 264. The drift this
item was filed for - `PL-YMY7`'s eleven cited lines landing on entirely
different statements twice in nine days - moves a citation to a *valid line
holding different content*, which is the half no checker can decide. That is
the same line `CLAUDE.md` draws for `doc_check.py`: it decides whether a cited
path exists, never whether the sentence around it is still true.

**A path check over the 4 would fail correct prose.** `PL-69J3` cites
`verify_findings.py:83` inside a sentence whose subject *is* the retirement:
"PL-STNV retired `tools/review-verification/`, taking three of the original
sites ... with it". The citation is a historical record and the sentence says
so. One false positive against three real finds, on a hard error, is what this
file's own comments refuse repeatedly - and `PL-KJ63` already cost a rewording
of prose that was not wrong. Demoting it to an advisory fails `CLAUDE.md`'s
retirement test on arrival: four lines every run, one of them wrong, nobody
acting on them.

**So: symbol names alone are enough, and the rule is where a citation must
stay true rather than where it appears.** A `reason` in `REQUIREMENTS` is a
live specification and is checked. A line citation in an item brief is a dated
measurement - what a file said on a day, often a day on which it was about to
be deleted - and stays.

**The one genuinely misleading citation is fixed rather than checked.**
`PL-VP7N` cited `core/respiratory_system.py:138` twice, in sentences saying
nothing about a rename, so a reader followed it to a file that has not existed
since `PL-006` renamed it to `core/uptake_system.py`. Both now name
`core/uptake_system.py`'s `advance`, and the first records the old name and the
item that changed it.
