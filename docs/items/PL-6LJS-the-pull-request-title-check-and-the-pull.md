---
id: PL-6LJS
title: The pull-request title check and the pull-request number check refuse a branch for an item another pull request closed, when the branch was built on that pull request's branch before it merged
priority: P2
effort: S
status: done
classes: defect
feature: standing-weight
milestone: v0.6.20
touches: tools/pr_record_check.py, tests/unit
deferred-from: v0.7.0 - present at the freeze, deferred on a stated reason: it is paid only by a branch stacked on another open pull request, and the entries this gate still holds are independent items that need no stacking, so the compounding-friction count is near zero
added: 2026-11-21
closed: 2026-11-22
pr: 2224
filed-pr: 2176
payoff: A branch stacked on another open pull request goes green for the work it carries, so no session has to work around a required check that blames it for another branch.
tests: tests/unit/test_pr_record_check.py::test_a_closure_recording_another_number_is_refused
reenters: PL-HMZZ
---

**Problem.** The pull-request title check and the pull-request number check refuse a branch for an item another pull request closed, when the branch was built on that pull request's branch before it merged

**Why it matters.** `PL-LY24`'s count found 28 refusals of `tools/pr_title_check.py` and 3 of `tools/pr_record_check.py` that blamed a branch for an item that another pull request had closed. Each is a red required check that the session must work around. Examples: `claude/pl-26bz-wash-in-label` (#2157) was refused for `PL-CBYS`, which #2134 closed; `claude/project-thread-474f8h` (#1921) was refused for `PL-2881`, which records `pr: 1918`. Both checks compare the branch with the base branch, so a closure on the branch below it reads as this branch's own.

**What to do.** Make both checks leave out a closure that already records another pull request's number, or that another open pull request carries, and test it with a stacked branch.

**Done when.** A branch built on another open pull request's branch is told why it is refused and how the stack clears. (Rewritten 2026-11-22: passing it, the first goal, would let it merge first; see the Done note.)

**Checked 2026-11-22**, at `d4e8200c`. The fault is still there. `tools/pr_record_check.py` still holds every item closed at the head and not at the base to this branch's own number (`owed = {... if pr != str(number)}`), so an item that records another pull request's `pr:` is still counted as owed. Neither check reads the branch the work was stacked on. Both checks were present at the freeze (`git show 0947408:tools/pr_record_check.py`). `PL-LY24` (the count of what the workflow-record checks refused) recommends keeping both checks and fixing this item.

**Generator check.** An instance of the fact that `PL-XYQW` and `PL-HMZZ` state, "Which pull request carried an item's work", filed after both heads closed. Here the two checks read a closure on the branch below as this branch's own. So it is recorded as re-entering `PL-HMZZ`, whose `closures_on_base` reading these checks rely on.

**Done 2026-11-22, by a refusal that names the cause rather than an exception.** The first version left out a closure recording another open pull request's number, and two blind review passes showed why that is wrong. A branch built on another pull request's branch, with `main` as its base, could then go green and merge first. Its squash commit would land the lower branch's work and closure under its own subject, which names neither, and the checks do not re-run when the lower pull request closes. The two refusals are therefore correct, and the brief's done-when was the wrong goal. A stacked pull request whose base is the lower branch already passes both checks, because that base holds the closure, and once the lower one merges `main` holds it. So `tools/pr_record_check.py` now says so when a closure records another number: set this pull request's base to that branch until it merges, or wait for it and merge main in. `test_a_closure_recording_another_number_is_refused` pins the line, and `test_a_closure_recording_no_number_is_refused` pins its absence. Files checked: both module docstrings, `.github/workflows/pr-title.yml`, `.claude/skills/docket/modes/close-out.md` and `.claude/skills/pull-request/SKILL.md`, which need no change.
