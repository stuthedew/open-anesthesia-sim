---
id: PL-979D
title: The squash commit on main is composed by whichever merge path lands it and nothing records the pull request's body at the merge, so each new way a path rewrites it - emptied, replaced, hard-wrapped, a subject frozen at arming - arrives as its own item: PL-WFFX's fact, reopened by three instances filed after it closed
priority: P2
effort: M
status: blocked
classes: defect
feature: pr-body-integrity
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py
blocked-by: PL-HMZZ
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: the reasoning behind each merged change survives however it was merged, and a new merge path's rewrite stops producing an item
root-cause-of: PL-Y1W0, PL-BZHX, PL-PNJF, PL-M7W1
generator: live - the merge paths still compose the squash body their own way (a hard-wrapping path landed 9 of 10 table bodies broken since 2026-09-22) and nothing records the pull request's body, so each new rewrite arrives as its own item
misread: The squash commit's subject and body as the merge sends them, not as the pull request shows them
---

**Problem.** The squash commit on main is composed by whichever merge path lands it and nothing records the pull request's body at the merge, so each new way a path rewrites it - emptied, replaced, hard-wrapped, a subject frozen at arming - arrives as its own item: PL-WFFX's fact, reopened by three instances filed after it closed

Found 2026-09-25 by the triage pass, from the post-close test in `.claude/skills/docket/modes/triage.md`. `PL-WFFX` closed `spent` on the empty `commit_message` from the GitHub iPhone app. Three items stating its `misread:` were filed after it closed: `PL-Y1W0` (eight bodies non-empty but different from their pull request's), `PL-BZHX` (bodies hard-wrapped at about 72 columns: 96 of the 140 bodies carrying a table since 2026-09-10 have broken rows, two landed unwrapped, so at least two merge paths exist) and `PL-PNJF` (27 differing bodies that `--recover` cannot record). `PL-M7W1` (the squash subject frozen when auto-merge is armed) is still open from before.

**Why it matters.** The squash body is the permanent record of why a change was made, and the project reads it back (`tools/pr_body_check.py`, `docket check`'s pull-request recovery). `PL-WFFX`'s fix removed one merge path's failure, and the fact itself stayed live: every other path still composes the body its own way, and no copy of the pull request's body is kept to compare against or recover from.

**Decision needed.** Which of two things is the permanent record of a pull request's reasoning. One option is the squash body, in which case every merge path used here has to be pinned to one that sends the body verbatim. The other is a copy recorded in the tree before the merge, in which case a path's rewrite stops mattering.

**Recommendation:** the copy recorded before the merge, built with `PL-HMZZ`, whose design round (#1011) already chose to record the carrying pull request before the merge, enforced by the pull request's own check. The body can ride the same record. That ends the whole family instead of chasing each merge path, and it turns `PL-BZHX` and `PL-PNJF` into recovery work against the record. It is the owner's call because it changes where the project's permanent history lives.

**Answered 2026-09-25** (project owner, 2026-09-25, ratified, over pinning every merge path to one that sends the body verbatim): a copy recorded in the tree before the merge, built with `PL-HMZZ`. Blocked by `PL-HMZZ` until its design is answered and built.

**Done when.** One of the two is recorded here as the answer, and each open member is re-scoped or closed against it.

**Generator check.** This is a head: `PL-WFFX`'s `misread:`, restated word for word so the two sort together, with three instances filed after `PL-WFFX` closed.
