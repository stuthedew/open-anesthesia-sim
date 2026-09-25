---
id: PL-Y48N
title: next and show read items from the working tree while holds come from refs, so a fetched clone whose working tree is behind origin/main offers, and shows as ready, an item origin/main has closed - and claim then pushes a dead claim and calls it 'a defect in docket'
status: untriaged
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-25
---

**Problem.** next and show read items from the working tree while holds come from refs, so a fetched clone whose working tree is behind origin/main offers, and shows as ready, an item origin/main has closed - and claim then pushes a dead claim and calls it 'a defect in docket'

Reproduced (scenarios b, c, d): s2 branches; s1 claims X, closes it, is squash-merged; s2 fetches; s2's `next` offers X and `show X` says ready with no note; `claim X` commits and pushes a claim, prints "does not read back as a live claim ...; this is a defect in docket", exits 1. After `merge --ff-only`, correct. `claiming._branch` checks only HEAD's copy.

**Why it matters.** Duplicated work on a closed item, and a wrong diagnosis that sends the session hunting a docket bug.

**Done when.** `next`/`show`/`claim` read the item's status from origin/main when it is newer than the working tree's, or say the working tree is behind; a test holds scenario b.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
