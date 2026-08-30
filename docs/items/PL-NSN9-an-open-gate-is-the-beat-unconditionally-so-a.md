---
id: PL-NSN9
title: A milestone that gates itself reports 'implement' when its gate clears, not 'release'
priority: P3
effort: S
status: ready
verify: uv run pytest subprojects/docket/tests/test_roadmap.py -k self_gating
classes: infra, session-cost
feature: planning-cadence
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py
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

---

**Rescoped 2026-08-30. The premise was wrong, and the decision is withdrawn.**

A release inserted ahead of an open gate *can* take the beat: it only has to
record a gate of its own. `wave()` picks `recorded[0]` from the unreleased
milestone sections sorted by version, so a v0.2.8 section carrying a
`### Debt gate` subsection becomes the nearest gate and the beat follows it.
Verified across the whole lifecycle against a patched `ROADMAP.md`: 17 of 17
open, then 11 of 17 after six close, then the gate clear, then - once v0.2.8
is released - the beat handing back to Gate 0 at "8 entries of 20 still open"
with the step returning to v0.3.0. No code change, and nothing about Gate 0's
binding on v0.4.0 changes.

So neither route in the withdrawn decision is needed, and the gate's
unconditional precedence is kept exactly as `ROADMAP.md` argues it should be.

**What is actually left, and it is small.** In that last-but-one state the beat
reads `implement v0.2.8 - its gate is clear`, when the act due is to cut the
release. `shipping_the_gate` tests `step.version < gate.milestone.version`,
which is false when a milestone gates itself, so the RELEASE branch is missed
and IMPLEMENT is taken. It is right for Gate 0, whose work ships as a
different version, and wrong only for a milestone whose own gate is its
content. It surfaces once per self-gating release, at the end.

**Also still true, and deliberately not fixed here.** A release inserted ahead
of a gate *without* recording a gate of its own still cannot take the beat.
That is the documented behaviour and the reason `ROADMAP.md` gives for it
stands; recording a gate is the supported way to say a release comes first.

**Done when.** A milestone whose gate is its own content reports the release
beat rather than the implement beat when that gate clears, and a test names the
self-gating case so the distinction from Gate 0's exception is written down.

**`touches` corrected 2026-08-30.** `ROADMAP.md` was dropped from the list. It
was declared under the original scope, which proposed that a milestone section
name the gate it ships; that scope is withdrawn. Every mention of `ROADMAP.md`
that remains in this item is a citation of what the file argues, not a file
this work edits - the change is `shipping_the_gate` in `roadmap.py` and a test
beside it. The stale entry mattered: it made `docket concurrent` report a
collision with `PL-51T3` (scope v0.2.8 and freeze its gate), which does edit
`ROADMAP.md`, and would have serialized two items that do not touch each other.
An instance of `PL-8JY7` (a declared `touches` path is never checked against
the tree, so it goes stale).
