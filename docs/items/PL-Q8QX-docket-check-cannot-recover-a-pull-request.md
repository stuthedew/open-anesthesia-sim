---
id: PL-Q8QX
title: `docket check` cannot recover a pull request number when the squash-merge subject differs from the pull request title
status: untriaged
added: 2026-09-02
---

**Problem.** `docket check` cannot recover a pull request number when the squash-merge subject differs from the pull request title

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `docket check` recovers a closed item's `pr` from the newest
commit subject *naming that id*. A GitHub squash merge takes its subject from
whatever the merger typed, which need not be the pull request title, so an id
that led every commit on the branch and led the pull request title can still
be absent from the one subject that lands on `main`.

**Observed** 2026-09-02, cutting v0.3.0. Pull request 220 was titled
`PL-YHF1, PL-P909, PL-SS9Q: make blocked safety work claim its exemption...`
- three ids, exactly as `CLAUDE.md` requires. It squash-merged as
`Design anesthesia-machine abstraction and add safety checks for blocked
items (#220)`. All three items then failed `docket check` as errors
("no way back from the closure to the work that made it") and blocked the
release until backfilled by hand, even though `git log -- <item file>`
answers in one command.

**Why it matters.** The rule it enforces is real and worth keeping. But the
failure is not the session's - it followed the rule - and the error blocks a
release for a number sitting in plain view. It will recur: nothing in the
merge UI carries the branch's subject discipline across.

**Approach.** Fall back to the merge commit that last modified the item's own
file when no subject names the id, taking `(#N)` from its subject. That is
strictly more evidence than the current path, not less: the commit that wrote
`status: done` into the file *is* the closure. Keep the error for the case
where neither source answers. Consider raising it as an advisory naming the
recovered number, matching what the empty-`pr` path already does.

**Where.** `subprojects/docket/src/docket/checks.py` (or wherever
`recover_pull_request` lives), `subprojects/docket/tests/test_checks.py`.
