---
id: PL-MC8Z
title: The start-an-item guard checks who is on the item but never what files it touches, so overlap is found at merge
priority: P2
effort: S
status: done
classes: infra
feature: parallel-sessions
touches: .claude/skills/docket/SKILL.md, subprojects/docket/src/docket/concurrency.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_concurrency.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-02
closed: 2026-09-04
pr: 279
verify: uv run pytest subprojects/docket/tests/test_concurrency.py subprojects/docket/tests/test_vcs.py && grep -qF 'is another session in these files' .claude/skills/docket/SKILL.md && grep -q 'def test_observed_overlap_reports_the_branch_changing_the_file' subprojects/docket/tests/test_concurrency.py
---

**Problem.** The `docket` skill's "Mode: start an item" is a three-step guard —
`git fetch origin`, then `bin/docket show <id>`, then the `list_sessions` scan
— and all three answer the same question: *is another session on this item?*
None of them asks the other question, *is another session in these files?*,
even though `bin/docket concurrent <id>` already answers it and needs no
argument the session does not have.

**Observed 2026-09-02.** Two sessions worked `PL-P0QT` and `PL-2XTF`/`PL-SVRW`
concurrently. The guard behaved correctly at every step: different items, so
nothing was in flight, and neither session should have yielded. Both branches
then edited `subprojects/docket/src/docket/vcs.py` and
`subprojects/docket/tests/test_vcs.py`. `bin/docket concurrent PL-P0QT` listed
`PL-2XTF` under "Cannot run alongside" the whole time, and neither session ran
it, because nothing in the guard says to.

**Why it matters, and what it is not.** This is the cheap end of the problem
`PL-D4MZ` (nothing reserves work when it is recommended) covers, and it needs
no new mechanism at all — the command exists, is already documented under
"Mode: work several items at once", and is simply never reached from the mode
that would use it. `docket next` is not a substitute: the owner naming an item
directly skips `next` entirely, which is the same gap `PL-5KR2` closed for the
in-flight read and left open for this one.

It is not `PL-YHD3` (which of two sessions yields). Nothing here should yield:
two unrelated items legitimately touch one file, and the right outcome is that
both proceed knowing it, and the second to merge resolves deliberately rather
than discovering it.

**Where.** `.claude/skills/docket/SKILL.md`, "Mode: start an item". One line in
the existing guard, plus what to do with a non-empty answer — which is the part
worth thinking about, since the honest answer is usually "proceed, and expect
to resolve", not "pick something else".

Note that `concurrent` reports declared overlap only: an item with no `touches`
is unanalysed rather than safe, and the skill already says to report what it
rules out rather than what it certifies. A guard step that reads as a clean
bill of health would be worse than none.

**Done when.** The start-an-item guard names the file-overlap question, and
says what a session does with the answer.

**Worked 2026-09-04, with the scope extended by the project owner.** The brief
scopes a prose fix: one step in the guard telling a session to run
`bin/docket concurrent <id>`. That was built, and so was a second half, because
the prose half alone would not have caught the collision this session found on
its way to picking the item.

*The evidence.* Choosing between three apparatus items, `bin/docket concurrent
PL-20CQ` listed eleven items it could not run alongside and said nothing about
`origin/claude/perf-investigation-xnlfed`, which had commits from that morning
in `checks.py`, `verify.py` and `test_checks.py` — `PL-20CQ`'s entire file set.
It was found by hand, with `git diff --name-only origin/main...<ref>` over every
remote branch. `concurrent` was blind to it because it compares one item's
`touches` against another's, and `touches` is a prediction: the four items on
that branch had declared other paths, and the branch had wandered.

*So the guard reads the branches too.* `vcs.files_in_flight` diffs each
unmerged ref against the default branch, `concurrency.observed_conflicts`
matches those files against the item's `touches` with the same `_covers`
logic, and `docket concurrent <id>` prints them as their own section. Against
the case above it now names the ref, the four items on it, and the three files.

*Reported separately from declared overlap, deliberately.* They are different
kinds of evidence and only one of them says the collision has already happened;
merging them into a single verdict would lose exactly that. The observed half
also inherits the in-flight read's refusals rather than working around them: a
ref whose commits went unread is not diffed, and an empty diff on a ref holding
commits is named as unread rather than reported as a branch that changed
nothing — `_run_git` answers a failure with the same empty string a clean
branch gives, and conflating the two would be the false clean bill of health
this package exists to refuse.

*What it does not fix.* `touches` staying a prediction (`PL-PGZK` covers the
hub-path over-firing that follows from it), and the window before a session's
first push, which no ref can close (`PL-SK88`). The observed half narrows the
second only for work already pushed.

