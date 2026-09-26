---
id: PL-Y48N
title: next and show read items from the working tree while holds come from refs, so a fetched clone whose working tree is behind origin/main offers, and shows as ready, an item origin/main has closed - and claim then pushes a dead claim and calls it 'a defect in docket'
priority: P2
effort: M
status: done
classes: defect, infra
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_claiming.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
closed: 2026-09-26
pr: 1058
payoff: a session in a clone whose working tree is behind origin/main is neither offered nor allowed to claim an item another session already finished, and is not sent hunting a docket bug
verify: grep -q 'def test_next_does_not_offer_an_item_origin_main_has_closed' subprojects/docket/tests/test_cli.py
recurrences: 2026-09-26 PL-KS01
---

**Problem.** next and show read items from the working tree while holds come from refs, so a fetched clone whose working tree is behind origin/main offers, and shows as ready, an item origin/main has closed - and claim then pushes a dead claim and calls it 'a defect in docket'

Reproduced (scenarios b, c, d): s2 branches; s1 claims X, closes it, is squash-merged; s2 fetches; s2's `next` offers X and `show X` says ready with no note; `claim X` commits and pushes a claim, prints "does not read back as a live claim ...; this is a defect in docket", exits 1. After `merge --ff-only`, correct. `claiming._branch` checks only HEAD's copy.

**Why it matters.** Duplicated work on a closed item, and a wrong diagnosis that sends the session hunting a docket bug.

**Done when.** `next`/`show`/`claim` read the item's status from origin/main when it is newer than the working tree's, or say the working tree is behind; a test holds scenario b.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

Reproduced 2026-09-25 against 46954a81, in a scratch clone on a branch at `46954a81~1` with `origin/main` at `46954a81`, where `PL-FX5Q` is done: `next` offered `PL-FX5Q` first, `show PL-FX5Q` said `ready` with no note, and `claim PL-FX5Q` printed `claim written on s2 ... and pushed`, then `does not read back as a live claim by s2; this is a defect in docket`. `claiming._branch` (claiming.py:366) checks the status of `HEAD`'s copy only, so `touches` now carries `claiming.py` and its test.

**Generator check.** PL-XBV4's fact: the working tree's moment read as the moment of the refs beside it.

**Closed 2026-09-26.** `vcs.base_copies` reads the items the base changed after `HEAD` forked (`HEAD...<base>`), each with the base's copy, and marks the ones this checkout changed too, committed or not. `BaseCopy.supersedes` picks the copy to answer from: the base's where only the base changed the item, and this checkout's own edit where both did, except over a closure, which `holdings` releases every claim on (`BY_CLOSED`) whatever the branch's copy says. The whole copy is read rather than the `status:` line alone, because a base triage pass that readies an item also writes the priority and effort the ranking reads. `cli._from_base` applies it to `next` and `show` only, read-only, and only where the snapshot places the working tree behind. `next`'s line counts the status moves and names the closures: measured on this branch one commit behind `origin/main`, a triage pass had moved 21 statuses, and a line naming each buried the one closure among them. `claim` refuses by the read-back's own rule - the base's copy is closed - after its fetch, which also covers a branch reopening an item the base holds closed, and the read-back names a closure that lands between the two instead of calling it a defect in docket. The digest, `list`, `status` and `concurrent` still read the working tree: `PL-KS01`.
