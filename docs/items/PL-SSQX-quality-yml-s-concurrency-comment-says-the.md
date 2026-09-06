---
id: PL-SSQX
title: quality.yml's concurrency comment says the repository is public and standard runners are free, and the repository is private
priority: P2
effort: S
status: done
classes: docs, infra
feature: ci-cost
milestone: v0.4.3
touches: .github/workflows/quality.yml
added: 2026-09-05
closed: 2026-09-05
pr: 369
verify: python3 tools/doc_check.py check && ! grep -q 'the repository is public and standard runners are free' .github/workflows/quality.yml
---

**Problem.** `.github/workflows/quality.yml`'s `concurrency` comment reads:

> What cancelling buys is no longer the minute - the repository is public and
> standard runners are free - but the runner slot

The repository is **private**. `GET /repos/stuthedew/open-anesthesia-sim`
returns `"private": true, "visibility": "private"` (read 2026-09-05). Minutes
on GitHub-hosted standard runners are billed for private repositories, with
each job's time rounded up to the whole minute, against a monthly included
allowance.

**Why it matters.** The sentence is not decoration - it is the stated reason
for a design choice, and it tells the next session that CI minutes are free
here. That is the premise a cost pass would read and stop at. `PL-D551` was
worked in the same file on the same day *on the opposite premise*, and the
merged file now carries both: line 16 says standard runners are free, and line
69 says the folded job "billed a whole minute for eight seconds". One of them
is wrong, and a reader has no way to tell which.

**The conclusion does not change; only its reason does.** Cancelling a
superseded run is worth *more* when minutes are billed, not less - it saves the
minute and the runner slot. So this is a one-sentence correction, not a
revisit of `PL-QD9K`.

**Where.** `.github/workflows/quality.yml`, the `concurrency` comment
(currently lines 14-19).

**Done when.** The comment states the true billing position - private
repository, minutes billed and rounded up per job - and names both things
cancelling buys, so no reader is left with a contradiction inside one file.

**Found while working the CI-cost items 2026-09-05**, checking whether
"reduce the Actions minute charge" was a real goal before spending work on it.

**Triaged and closed 2026-09-05, in the session that found it.** `P2`,
`docs`/`infra`: nothing computes a wrong number, but the sentence is the stated
premise of a design decision and it is false, which is the shape that stops a
later cost pass before it starts. Not `defect` - no check gives a wrong answer
- and not `P3`, because a premise a session reads and believes does not heal
on its own.

The comment now states the billing position that holds: private repository,
GitHub-hosted standard-runner minutes charged against the account's monthly
allowance, each job rounded up to the whole minute. `PL-QD9K`'s conclusion is
untouched and did not need re-deciding - cancelling a superseded run is worth
*more* when minutes are billed, so the correction strengthens the setting it
justifies rather than reopening it. The old sentence is quoted in the new
comment rather than merely replaced, so a reader meeting the contradiction
elsewhere can see it was found and answered.

The `verify:` command was run before being written down and exits 1 on the
tree without the work: `doc_check` passes and the `grep` matches, so the whole
command fails for the right reason.
