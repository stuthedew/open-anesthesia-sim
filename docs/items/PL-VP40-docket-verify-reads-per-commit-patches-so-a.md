---
id: PL-VP40
title: docket verify reads per-commit patches, so a line a branch added and then removed still reads as added
priority: P3
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-05
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_line_added_then_removed_is_not_reported_as_added' subprojects/docket/tests/test_verify.py
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
