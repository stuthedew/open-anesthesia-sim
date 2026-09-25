---
id: PL-140X
title: show says 'no item matching' for an id that next and flight name as a live claim, without pointing at stranded or the branch that holds it
priority: P3
effort: S
status: ready
classes: defect, infra
feature: one-snapshot
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
payoff: a session asking about an item another session holds is told which branch has it and how to read it, instead of 'no item matching'
verify: grep -q 'def test_show_names_the_branch_holding_an_item_absent_here' subprojects/docket/tests/test_cli.py
---

**Problem.** show says 'no item matching' for an id that next and flight name as a live claim, without pointing at stranded or the branch that holds it

Reproduced live with PL-DRRG: `next` `Excluded, already in flight: PL-DRRG (live claim)`; `show PL-DRRG` `no item matching 'PL-DRRG'`.

**Why it matters.** A dead end at the moment a session asks about work another session holds.

**Done when.** `show` on an id held only on a branch names the branch and how to read it.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

Reproduced 2026-09-25 against 46954a81, in scratch clones: a branch captured and claimed `PL-WF3C` and pushed it; in a second clone after a fetch, `next` printed `Excluded, already in flight: PL-WF3C (live claim)`, `flight` listed it on `origin/claude/scratch-lfnk`, and `show PL-WF3C` printed `no item matching 'PL-WF3C'` and exited 1.

**Generator check.** One-off: `show` looks only in this checkout's store, and its not-found line does not consult the refs `next` and `flight` already read. No freshness is misread, since the item was never on the base, so it is removed from PL-XBV4's `root-cause-of`.
