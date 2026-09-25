---
id: PL-KX73
title: claim refuses the web harness's own branch shape: every session branch starts with branch.<name>.merge=refs/heads/main, so claim exits 1 with 'pushes to origin/main, and a claim names one branch' until the session pushes with -u or unsets the upstream, and nothing in .claude/ or the README says so
priority: P2
effort: S
status: ready
classes: defect
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py, .claude/skills/docket/modes/start.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21) by PL-P0FP's stress test (2026-09-25), and not safety or science; a defect in PL-0TD9's claim writer, which merged after the freeze
added: 2026-09-25
payoff: a web session's first claim on a branch the harness made tracking main is written and pushed at once, instead of refused until the session repairs the branch's upstream by hand
verify: grep -q 'def test_a_branch_tracking_the_default_branch_is_pushed_with_an_upstream_of_its_own' subprojects/docket/tests/test_claiming.py
---

**Problem.** claim refuses the web harness's own branch shape: every session branch starts with branch.<name>.merge=refs/heads/main, so claim exits 1 with 'pushes to origin/main, and a claim names one branch' until the session pushes with -u or unsets the upstream, and nothing in .claude/ or the README says so

Confirmed read-only on this session's branch (`branch.claude/upbeat-heisenberg-27vafn.merge` is `refs/heads/main`) and reproduced in the simulation (scenario u). Adjacent to PL-WX87.

**Why it matters.** Every web session's first claim before its first push hits it.

**Done when.** `claim` sets the branch's own upstream (or pushes with `-u`) when the upstream is the default branch, or prints the one command that does; a test holds scenario u.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Reproduced 2026-09-25** in `subprojects/docket/tests/test_claiming.py`, as
the simulation's scenario u sets it up: a clone of a bare remote, `git checkout
-b claude/work-b7xq2n --track origin/main`, then `claim`. It exited 1 with
"claude/work-b7xq2n pushes to origin/main, and a claim names one branch; give
them one name first". Not every session branch has this shape: the one this
item was worked on, `claude/pl-kx73-slx116`, started with no upstream at all
and a tracking ref the harness wrote with nothing pushed, which is `PL-WX87`'s
shape instead.

**Generator check.** The second post-close instance of `PL-4Q9B`'s fact, after
`PL-WX87`: "The remote's current refs and tags, and whether the clone's local
copies still match them". Here the local copy is the branch's upstream
setting, which the harness points at the default branch, and which `_publish`
would have read as the branch's copy on the remote had `_branch` not refused
first. Both instances are one harness behaviour - it writes local git state at
session start that the remote never had - and a third would count as a
generator whose fix did not hold.
