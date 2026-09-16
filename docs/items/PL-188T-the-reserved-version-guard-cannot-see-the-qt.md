---
id: PL-188T
title: The reserved-version guard cannot see the Qt port's section once the port is numbered past the current patch, so a patch cut mid-port is offered the port's own number as free
priority: P3
effort: S
status: done
classes: defect, infra
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_release.py
added: 2026-09-14
closed: 2026-09-16
pr: 606
verify: uv run pytest subprojects/docket/tests/test_release.py && grep -q 'def test_a_version_named_ahead_of_the_current_one_is_reserved' subprojects/docket/tests/test_release.py
---

**Problem.** The reserved-version guard cannot see the Qt port's section once the port is numbered past the current patch, so a patch cut mid-port is offered the port's own number as free

**Found 2026-09-14** by the pre-port survey, and it is `PL-VFD8`'s defect by
a third door. `PL-6T4L` taught `release_offer`'s reserved-version guard to
read `plan.step` and `plan.milestone`. Once `PL-G7RD` cuts `v0.4.25` and the
port's section moves to `v0.4.26`, `wave` binds `step = v0.4.x` and
`milestone = v0.5.0` - the port section is neither - and a simulated
`release_offer` on a `0.4.26` bump returns `ReleaseOffer(kind='stands',
version='0.4.26')`. So any patch cut mid-port is offered the port's own
number as free, which is the collision `ROADMAP.md` § "the interface moves to
Qt" records as its one risk, arriving again from the tool that exists to
prevent it.

**Done when** the guard answers from every version the roadmap names ahead of
the current one - which is `PL-VFD8`'s "Done when" verbatim, so this is
evidence for that item rather than a second mechanism; close both together.
Until then, a patch cut during the port names `0.4.27` rather than accepting
the offer.

**Update 2026-09-14 (`PL-FWJF`).** `wave` now binds `milestone` to the port's
section while the port is the beat's work - a section-bearing `—` row between
the clear gate and the milestone that recorded it - so a `0.4.26` bump is
`RESERVED` naming the port, and `test_release.py` pins that arrangement. This
is the existing carrier reaching the port rather than the guard reading every
version ahead, so the "Done when" above still stands: once the port ships and
v0.5.0 is the milestone again, the guard sees exactly what it saw before, and
`PL-VFD8`'s v0.6.0 is still offered.

**Why it matters.** The guard exists so a release cut mid-milestone cannot be
handed a number another section has already spoken for, and `ROADMAP.md`
§ "the interface moves to Qt" records that collision as the port's one risk. A
guard answering from two bindings rather than from the roadmap fails in the
direction that looks like success: `release_offer` returns `stands`, which is
the word a session acts on without checking. `PL-FWJF`'s carrier closes the
window only while the port is the beat's work, so the exposure returns the
moment v0.5.0 is the milestone again - deferred, not removed.

**Triaged 2026-09-15.** Kept as its own item rather than folded into `PL-VFD8`:
the evidence here is a third reproduction path that `PL-VFD8`'s brief does not
carry. Close the two together, as the brief above provides.

**Fixed 2026-09-16 with `PL-VFD8`, in one commit**, by the shared "Done when":
`wave` carries every version `ROADMAP.md` names ahead of the current one and
`release_offer` checks the suggestion against all of them. That carries this
item's whole exposure rather than the window `PL-FWJF` closed - the port's
number is reserved by its timeline row and its section, not by being whatever
object the beat happens to bind.

**The measurement, on the live roadmap at `7aa507c`.** A `0.4.26` bump from
`0.4.25` returned `ReleaseOffer(kind='stands', version='0.4.26')` and now
returns `ReleaseOffer(kind='reserved', version='0.4.26', milestone='the
interface moves to Qt')`. Worth recording that the update above was optimistic:
`PL-FWJF`'s carrier reaches the port only once Gate 1 is *clear*, and the gate
is open, so on `main` the port's number was not reserved even while the port
was the work. `test_a_version_named_ahead_of_the_current_one_is_reserved` pins
that arrangement - the gate open, the step on the patch track, the beat's
milestone two rows past the port - beside the existing test for the cleared-gate
one.
