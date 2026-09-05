---
id: PL-SSQX
title: quality.yml's concurrency comment says the repository is public and standard runners are free, and the repository is private
status: untriaged
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-05
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
