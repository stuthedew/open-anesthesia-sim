---
id: PL-YRLM
title: Decide which release builds planned-milestone item 28, agent cost, so the liquid-equivalent readout PL-B396 decided, and the price, precision and constants waiting on it, have a release to wait on
priority: P3
effort: S
status: needs-decision
classes: planning
feature: liquid-agent-consumption
touches: ROADMAP.md, docs/items
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
