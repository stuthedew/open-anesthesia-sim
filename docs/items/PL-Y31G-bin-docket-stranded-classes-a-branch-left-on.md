---
id: PL-Y31G
title: bin/docket stranded classes a branch left on pre-rewrite history as one whose pull request merged, because it compares file content and a rewrite leaves content unchanged
priority: P2
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-06
closed: 2026-09-12
pr: 504
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_branch_on_duplicated_history_is_not_reported_as_orphaned' subprojects/docket/tests/test_vcs.py
---

**Problem.** `format_orphaned` reports a branch under "carries work the default
branch does not hold, having already taken the rest of it", and the evidence it
uses is **file content**: `branch.landed` counts the files whose blobs the base
already holds. A history rewrite changes every commit hash and leaves file
content untouched, so a branch sitting on the pre-rewrite history reads as one
whose pull request merged and left a commit behind. `PL-YGF3` observed exactly
that on `claude/fresh-gas-flow-range-4bom2g`.

**Why it matters.** The report itself is safe - its recovery is `git checkout
<ref> -- <path>`, which copies rather than deletes. The hazard is the next step
a reader takes: the `docket` skill's remedy for a branch whose pull request
merged is `git branch -dr origin/<branch>` followed by `git checkout -B`, and
on a pre-rewrite branch that deletes the only ref carrying commits nothing else
holds. The skill's own guard - confirm the merge first - is answered
affirmatively by this report, which is what makes the misclassification
expensive rather than merely untidy.

**Where.** `subprojects/docket/src/docket/vcs.py`, `orphaned` and whatever it
uses to decide a branch's work landed. `_duplicated_history` in the same module
already answers "is this ref on a rewritten history" from one `git log`, so the
qualifier exists and is not wired to this read (`PL-YGF3` built it for
`branch_state`).

**Done when.** A branch whose divergence from the base is duplicated history is
either excluded from the orphaned report or named as such in it, so that no
reader reaches the branch-deletion recipe on a ref holding the only copy of a
commit.
