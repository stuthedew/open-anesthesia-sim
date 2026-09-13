---
id: PL-VP40
title: docket verify reads per-commit patches, so a line a branch added and then removed still reads as added
priority: P3
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.21
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, tests/unit/test_ignore_check.py
added: 2026-09-05
closed: 2026-09-13
pr: 542
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_suppression_added_and_then_removed_is_not_reported' subprojects/docket/tests/test_verify.py
---

**Problem.** `_diff_text` in `subprojects/docket/src/docket/verify.py` runs
`git show --format= <commits>` when the item has commits of its own, which
concatenates one patch per commit rather than producing the branch's net
change. `_added_lines` and `_removed_lines` read `+` and `-` lines straight off
that concatenation, so a line a branch added in one commit and removed in the
next appears in both. Two checks consume them: "no suppression added" greps the
added lines for `SUPPRESSIONS`, and "no existing assertion removed" greps the
removed lines for `assert`.

**Why it matters.** The error runs in the safe direction - the checks
over-report, and nothing that survives to `HEAD` escapes either of them - so
the guarantee holds and what is lost is the check's credibility. A worker who
adds a `# type: ignore` while iterating and deletes it before pushing is still
told a suppression was added; one who cuts an assertion and restores it is
still told an assertion was dropped. Neither can see the cancelling commit in
the output, so neither can argue with the report, and the way that ends is
`CLAUDE.md`'s "an advisory nobody acts on" - reached here by the check being
wrong rather than by it being noisy.

**Where.** `subprojects/docket/src/docket/verify.py`: `_diff_text`,
`_added_lines`, `_removed_lines`.

**Approach.** A range diff is not available. An item's commits need not be
contiguous on the branch, so `git diff <first>^ <last>` would sweep in whatever
another item committed between them - which is the reason the per-commit form
is there. Fold the concatenation instead: within one file, cancel an added line
against an identical removed line. That is exactly as precise as the two checks
reading it, which are substring greps over line text rather than structural
readings, and it costs no new git call.

**Done when.** A branch that adds a suppression line in one commit and removes
it in a later one passes the "no suppression added" check, and one that removes
an assertion and restores it passes "no existing assertion removed", with a
test for each shape.

**Worked.** `_added_lines` and `_removed_lines` are replaced by one
`_net_line_changes`, which folds cancelling lines per file by *count* rather
than by set membership - so a file whose patches remove one `# type: ignore`
and add two still reports one added, which is the direction that would matter
if it broke. It also reads the diff once where the two helpers read it twice.

A line merely *moved* within a file cancels too, which was not in the brief
and is the right answer to both questions the checks ask: the suppression was
already there, and the assertion still is. The fold is applied to the
no-commits path as well as to the concatenation, for that reason.

`tests/unit/test_ignore_check.py` is in `touches` because the two new fixtures
broke it: it asserted that exactly *one* line of `test_verify.py` writes a
`type: ignore` inside a string literal, where what it means to say - and now
does, for every such line - is that a literal occurrence is not counted as a
directive. The tokenizer in `tools/ignore_check.py` was already right.
