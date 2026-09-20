---
id: PL-THLT
title: A fresh capture carries no touches for the near-duplicate search to key on, so bin/docket new infers candidate paths from the working tree's own uncommitted and branch-local changes - the gap PL-0KQP fell straight through
status: ready
feature: recurrence-signal
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests
added: 2026-09-20
priority: P2
effort: S
classes: infra
payoff: closes the hole the fifth capture of the suppression defect fell through - a fresh capture has no touches, so the only key that works reads nothing
verify: grep -q 'def test_new_infers_candidate_paths_from_the_working_tree' subprojects/docket/tests/test_cli.py
---

**Problem.** A fresh capture carries no `touches` for the near-duplicate search
to key on, so `bin/docket new` infers candidate paths from the working tree's
own uncommitted and branch-local changes - the gap `PL-0KQP` fell straight
through.

**Why it matters.** The shared-path key is the only one that works - title
similarity catches 0 of 13 known duplicate pairs at any usable threshold
(`PL-TZ7T`) - and a fresh capture is exactly the moment it has nothing to read.
So without this, the detection mechanism is blind precisely where a duplicate is
being created, which is the only moment it can be stopped cheaply.

**Where it comes from, measured 2026-09-20.** Of thirteen known duplicate pairs,
nine share a declared `touches` path and the shared-path key finds them. **All
four misses are `PL-0KQP`**, the fifth capture of the suppression-check defect:
`bin/docket new` writes `status: untriaged` and no `touches`, so the item that
most needed the warning was the one carrying nothing to match on.

**Why the working tree answers it.** The session that filed `PL-0KQP` was on
`origin/claude/nice-wright-cjo9ve`, whose commits touch
`subprojects/docket/src/docket/verify.py` - the exact path all four items it
duplicates declare. The information was present; nothing read it. A capture is
made *while* working on the thing that produced it, which is what makes the
working tree a good proxy for a `touches` the item does not have yet.

**Constraint that shapes it.** The capture rule is deliberately unconditional
and cheap - "`bin/docket new` is the whole procedure". So this may not prompt,
may not refuse, and may not require the session to pass anything. It reads what
git already knows, and where git says nothing the search falls back to title
rank alone and the command behaves as it does today.

**Done when** a capture filed on a branch whose changes touch a path is matched
against the open items declaring that path, with no new argument required of the
session.
