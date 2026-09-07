---
id: PL-6BDX
title: "Two shipped items are reported in flight in every session's digest, because their branch refs outlived their merges: PL-GVXP (v0.4.7) and PL-S5LB (v0.4.6)"
priority: P2
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-07
verify: uv run pytest -q subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_closed_item_is_not_reported_in_flight' subprojects/docket/tests/test_vcs.py
---

**Problem.** Measured 2026-09-07 after a full fetch:

    PL-GVXP  done, milestone: v0.4.7
             IN FLIGHT on origin/claude/chart-traces-contrast-59clod
    PL-S5LB  done, milestone: v0.4.6
             IN FLIGHT on origin/claude/number-closing-rename-detection-3kgjlp

Both shipped - one two releases ago - and both are still named on the session
digest's `In flight on a branch:` line, under "do not start these again". The
mark is read from branch refs, and the refs outlived the merges that took their
work.

**Why it matters.** Not because it misroutes work: `bin/docket next` does not
offer closed items, so nothing is lost or duplicated. It matters because the
line fires in *every* session, tells each one not to start two items nobody
could start, and sits directly above the same line's true entries. `CLAUDE.md`
is explicit that a check firing every run without changing a decision is a
defect in the check, since it trains a session to skim the output where a real
one also appears - and this line's real entries are exactly the ones that stop
two sessions colliding.

**Where.** The immediate clearing is two ref deletions by name, which is the
project owner's to run and must not be a prune - a stale `origin/<branch>` can
be the only surviving copy of an item captured on a branch nobody merged, which
is what `.claude/hooks/no-prune-guard.sh` exists to refuse. `bin/docket
stranded` reports nothing on either of these, so both are safe to drop.

The durable half is whether the mark should read a closed item as in flight at
all. An item's `status` is on the same commit the mark is derived from, so
"closed on the base" is decidable where the mark is computed, and suppressing
those entries would leave the line carrying only what it is for. That is
narrower than expiring refs by age, which `flight` deliberately does not do
because it cannot tell an abandoned branch from a slow session.

**Done when.** A closed item is not reported in flight, and the two refs above
are gone.

**Triage note, 2026-09-07.** Re-checked against the store rather than carried
from the capture, and the count is worse than the title says: the digest names
*three* ids on its `In flight on a branch:` line today - `PL-GVXP`, `PL-S5LB`
and `PL-Y5WR` - and all three are `status: done` with a milestone (`v0.4.7`,
`v0.4.6`, `v0.4.7`). The line is therefore 100% false positives right now,
which is the strongest form of the argument above: there is no true entry
beside the stale ones for a reader to be trained past, so the only thing the
line teaches this week is to skip it.

`PL-CPSY` (v0.2.8) already fixed the containment test that made a squash-merged
branch's ref report in flight forever, and these three post-date it, so that
fix is not what is missing. The guard this item proposes - suppress an item the
base records as closed - is independent of *why* a ref survived, which is why
it is worth having in addition rather than instead.
