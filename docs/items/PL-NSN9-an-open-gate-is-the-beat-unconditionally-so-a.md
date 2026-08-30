---
id: PL-NSN9
title: An open gate is the beat unconditionally, so a release inserted ahead of it cannot become the beat
status: untriaged
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

**Approach.** Make the relationship explicit rather than inferred: have the
milestone section that ships a gate name it, and have `parse_milestones` read
it, so `wave()` can ask "is the current step the gate's release?" instead of
guessing from version order. Then the beat is the gate only from that step
onward; a release ahead of it takes the beat, and the gate still clears before
the milestone it gates, which is the cadence's actual rule.

**Do not weaken the gate.** The rule that a gate clears before the milestone it
gates is the point of the mechanism and must survive this unchanged. What
changes is only which *step* the gate is attached to, not whether it binds.

**Related.** `PL-20ZR` (the workflow-before-features ordering is re-explained
every session) is blocked on this: it is the mechanism that would carry the
ordering. `PL-1TPM` (`docket next` ranks work the current milestone excludes)
and `PL-019F` (the "what next" rule answers one level below the roadmap step
that should decide it) are the same seam seen from the queue side.

**Done when.** A milestone section can name the gate it ships; `wave()` makes
the gate the beat only from that step onward; a release inserted ahead of it
becomes the beat with the gate still recorded and still binding; and tests
cover the inserted-release case, the gate-release case, and the case after the
gate's release has shipped.
