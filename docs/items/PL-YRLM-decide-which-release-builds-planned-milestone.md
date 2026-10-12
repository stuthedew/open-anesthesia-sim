---
id: PL-YRLM
title: Decide which release builds planned-milestone item 28, agent cost, so the liquid-equivalent readout PL-B396 decided, and the price, precision and constants waiting on it, have a release to wait on
priority: P2
effort: S
status: blocked
classes: planning
feature: liquid-agent-consumption
touches: ROADMAP.md, docs/items
blocked-by: v0.7.0
deferred-from: v0.6.0 - captured after the freeze to hold whether a release schedules planned-milestone item 28, a question Gate 3 inherits with the four entries waiting on it (PL-18BD), and not safety or science
added: 2026-09-27
---

**Problem.** Decide which release builds planned-milestone item 28, agent cost, so the liquid-equivalent readout PL-B396 decided, and the price, precision and constants waiting on it, have a release to wait on

**Where this came from.** `PL-18BD`, answered 2026-09-27 (project owner,
ratified, over teaching `bin/docket wave` to read a gate section's deferral
group, a `deferred-to:` field on the item, and leaving `wave` as it is). Until
then `PL-B396` held this question as the stand-in for planned-milestone item
28, and `PL-0S0V`, `PL-VJZK` and `PL-KZ99` waited on it. Item 28 has no id and
no release names it, so no `blocked-by` could say what the four were waiting
for, and `bin/docket wave` counted all four as work Gate 2 can clear although
`ROADMAP.md`'s v0.6.0 gate section defers them to Gate 3 (`PL-DB64`). This item
takes the question over, off the frozen list, and `PL-B396` is `blocked` on it,
which is the route `PL-0H5D` took for `PL-WZVZ` with `PL-TBMK` and `PL-4TWW`.

**Decision needed.** Whether `ROADMAP.md` § "Planned milestones" item 28 -
agent cost, whose readout reports millilitres of liquid equivalent by default
with a reader-set price later (project owner, 2026-09-16, recorded in
`PL-B396`) - is scheduled into a release now, and which.

*Recommendation: not yet.* Item 28 is an addition rather than a prerequisite
of anything a scheduled release builds, which is why it was kept out of v0.4.0,
and on 2026-09-27 the owner deferred the four entries waiting on it to Gate 3
rather than scheduling it. This item stays open as the handle until a release
takes item 28.

**Decided 2026-10-12, in the second workflow decision batch: the question is
v0.7.0's scoping round's, and this item waits on that round.** `ROADMAP.md`
§ "The planning model: a rolling wave" moves detail inward at two moments, a
row when a catalogue entry is placed and a section when the row is scoped, and
takes a decision sooner only where a nearer horizon depends on it. Nothing
nearer does: item 28 is a prerequisite of nothing v0.6.0 builds, which is why
it was kept out of v0.4.0 and why the four entries waiting on it were deferred
to Gate 3 rather than scheduled. A question only a scoping round resolves is
`blocked-by: <version>` rather than `needs-decision`
(`.claude/skills/docket/modes/triage.md`, the paragraph opening "Except where
the decision is a milestone being scoped"), so this item moves to `blocked` on
`v0.7.0`, the next release `ROADMAP.md` § "The timeline" names, and
`bin/docket check` advises the promote once v0.7.0's section carries its four
subsections. That round answers it one of two ways: it schedules item 28, and
this item closes with `PL-B396` taking `v0.7.0` in `blocked-by:`; or it does
not, and this item is blocked on `v0.8.0` instead while the four entries wait
on Gate 4's terms. Placing item 28 on a timeline row now, ahead of the round,
was weighed and not put to the owner: the round decides no later than Gate 3's
freeze, the later of v0.7.0's scoping and v0.6.0's ship (`ROADMAP.md` § "The
cadence"), so an earlier placement saves no deferral cycle, and the owner can
place item 28 on a row at any time without waiting for this item, which then
closes against the row. The "not yet" above stands as the placement until the
round. Decided in the round rather than offered, under rule 14 of
`.claude/rules/instruction-writing.md`: the roadmap's own planning model
settles which horizon the question belongs to.

**What v0.7.0's scoping round owes this question.** Item 27, the schematic,
draws where the agent *is* "in millilitres" (`ROADMAP.md` § "Planned
milestones"), and item 28's readout reports millilitres of liquid equivalent
(`PL-B396`). Those are different millilitres, vapour per compartment against
liquid drawn from the bottle, about 183 mL of vapour per mL of liquid
sevoflurane at 20 °C (`docs/MODEL.md` § "Agent amount": 182.8 derived from
the measured density, 184 as Biro's constant, 183 as Gas Man's). A display
carrying both without saying which is a unit a learner misreads, which
`CLAUDE.md`'s safety-critical standard treats as a wrong value; so the round
that schedules item 28 beside item 27 decides how the two readouts name their
unit, and `PL-0S0V` and `PL-KZ99`, the precision and the constants that
`PL-B396` holds behind it, are that decision's too.

**Why it matters.** It is the one question between four deferred entries and a
release that could build them. Held here, off the frozen list, `blocked-by`
can say what they wait on, so `bin/docket wave`, `next` and `check`'s promote
advisory read the deferral the gate section records instead of counting four
entries no work can close.

**Done when.** A release's row in `ROADMAP.md` § "The timeline", or its own
section, schedules item 28, `PL-B396` carries that version in `blocked-by:` in
place of this item, and this item closes. If the owner drops item 28 instead,
`PL-B396` and the three waiting on it are dispositioned with it.

**Generator check.** Bookkeeping rather than a finding: it gives `PL-B396`'s
holding condition an id, and the misread fact is `PL-18BD`'s.
