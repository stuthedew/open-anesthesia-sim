---
id: PL-NSN9
title: An open gate is the beat unconditionally, so a release inserted ahead of it cannot become the beat
priority: P2
effort: M
status: needs-decision
classes: infra, session-cost
feature: planning-cadence
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py, ROADMAP.md
added: 2026-08-30
---

**Problem.** `wave()`'s first branch is
`if gate is not None and not gate.is_clear: beat = CLEAR`, taken before
anything else is considered. Gate 0 has eight open entries, so the beat is
`clear` regardless of what the timeline says. Inserting a release ahead of the
gate's own release changes `step` and leaves `beat` alone, which was verified
by running `wave()` against a patched `ROADMAP.md`: `step` became
"v0.2.8 - the workflow works" while `beat` stayed `clear`, subject
"v0.4.0 - the teachable case".

The session-start digest prints both, so the result is a contradiction in the
first two lines a session reads - the step naming one release and the beat
naming work in another. That is worse than either line alone, because a
session cannot tell which to follow and the `docket` skill's tie-break rule
("follow the beat") sends it to the work the owner deprioritized.

**Why it matters.** The beat is the one instruction that reaches every session
before it reads anything, so it is the only cheap channel for a standing
priority decision (`PL-20ZR`). While it cannot be moved, that channel is
unavailable and the ordering has to be restated by hand in each new session -
which is the cost `PL-20ZR` exists to remove.

**Where.** `subprojects/docket/src/docket/roadmap.py`, `wave()`.

**Why the obvious fix does not work.** "Beat is `clear` only when the current
step is the gate's release" needs the code to know which step ships the gate.
It cannot infer it: today `step.version` (0.3.0) is already less than
`gate.milestone.version` (0.4.0), the same comparison a step inserted ahead of
it would satisfy, so the existing `shipping_the_gate` test cannot separate the
two. The fact lives only in the timeline's prose ("Gate 0's frozen debt list,
recorded under v0.4.0 below").

**This is a decision, not a defect.** The behaviour is deliberate and named:
`test_an_open_gate_is_the_beat_whatever_else_is_written` calls itself "the
acceptance case". `ROADMAP.md`'s "Why the gates are on this list and not behind
it" gives the reason - "a gate that lives in a separate document, or in a
session's memory, is renegotiated every time it is inconvenient" - and an
unconditional beat is what makes that true. Anything here trades some of that
non-negotiability away, so it needs the owner's decision rather than a fix.

**The case for changing it anyway.** `ROADMAP.md`'s own rule is narrower than
the code: "the gate clears before that milestone's implementation begins" - it
binds v0.4.0, not everything that precedes it. Gate 0 ships as v0.3.0 by the
recorded exception, so a release inserted at v0.2.8 reorders releases without
touching what the gate binds: it still clears in v0.3.0, still before v0.4.0.
On that reading `wave()` over-applies the rule rather than enforcing it.

**Approach, if changed.** Make the relationship explicit rather than inferred:
have the milestone section that ships a gate name it, and have
`parse_milestones` read it, so `wave()` can ask "is the current step the gate's
release?" instead of guessing from version order. The beat is then the gate
from that step onward, and a release ahead of it takes the beat.

**The cheaper alternative, if not.** Leave the cadence alone and change only
what the digest renders: say the beat as the obligation it is ("clear the gate
- blocks v0.4.0") rather than as the instruction for right now. The step line
then carries the current work and the two stop contradicting each other, with
no change to what binds. This keeps the gate exactly as non-negotiable as it is
today and is much the smaller change.

**Whichever is chosen, do not weaken what the gate binds.** The rule that a
gate clears before the milestone it gates must survive unchanged.

**Related.** `PL-20ZR` (the workflow-before-features ordering is re-explained
every session) is blocked on this: it is the mechanism that would carry the
ordering. `PL-1TPM` (`docket next` ranks work the current milestone excludes)
and `PL-019F` (the "what next" rule answers one level below the roadmap step
that should decide it) are the same seam seen from the queue side.

**Decision needed.** Move the beat so an inserted release outranks an open
gate, or leave the cadence alone and change only how the digest says the
beat. The first makes the digest's step and beat agree by changing what the
beat means; the second by changing how it reads, giving up none of the
gate's non-negotiability. Recommendation: the second, unless the owner wants
the beat to be the single place a phase is declared.

**First step.** Answer the decision above. Both end with the digest's first two lines agreeing; they
differ in whether the gate's unconditional precedence is given up to get there.

**Done when.** The session-start digest's step and beat lines cannot name work
in different releases; `test_an_open_gate_is_the_beat_whatever_else_is_written`
is either still passing or deliberately replaced with a test that states the
new rule and says why; and what the gate binds is unchanged.
