---
id: PL-N7MM
title: A record's cross-field invariant is checked when the record is built and not when a field is written later, so a later write leaves a patient, a state or a run definition that breaks its own rule: four members from 2026-10-04 to 2026-10-18
priority: P1
effort: M
status: ready
classes: defect, refactor
feature: defect-review-2026-10
touches: src/anesthesia_sim/core, tests/unit
deferred-from: v0.7.0 - recorded as a generator head by PL-R4Y2's defect review on 2026-10-25; each member's safety finding was filed and placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-10-25
payoff: a core record cannot be left breaking its own rule by a later write, so a patient, a state or a run definition the simulator computes from is always one its constructor would accept
verify: grep -rq 'def test_every_cross_field_invariant_holds_after_a_field_write' tests/unit
root-cause-of: PL-Z0T3, PL-8W1W, PL-Z0HN, PL-XRN8
generator: live - members on 2026-10-04, 2026-10-17 and 2026-10-18, and each record guards later writes by a hand-written __setattr__ or not at all
misread: Whether a record's cross-field rule still holds after a later field write
---

**Problem.** A record's cross-field invariant is checked when the record is built and not when a field is written later, so a later write leaves a patient, a state or a run definition that breaks its own rule: four members from 2026-10-04 to 2026-10-18

**The fact the members misread.** A rule that ties two stored values together holds only while every write keeps it. Each of these records checked its rule in `__post_init__` and nowhere else:

- `PL-Z0T3`: `dataclasses.replace()` on `PatientCompartments` rewrote the tissue and venous flows of the original it shared those objects with.
- `PL-8W1W`: `SimulationState.step_count` and `simulation_step_s` could be assigned after construction with no check.
- `PL-Z0HN`: a tissue group's perfusion fraction could be changed on a built patient, so the fractions no longer summed to 1.
- `PL-XRN8`: a core setter called past `SimulationController` changed what the steps ran at without changing the run's recorded definition.

`PL-KFNP` is a spent head for one instance of this, the cardiac output and the tissue flows derived from it. This head is the general rule.

**Why it is live.** Two members were filed on 2026-10-04, one on 2026-10-17 and one on 2026-10-18. The records that guard their writes do it with a hand-written `__setattr__` per class, and `PL-6YKY`, filed on 2026-10-25, found those guards spelling field names as strings. Nothing makes a new record with a cross-field rule guard its writes.

**What to do.** Decide, per record, whether a later write is needed at all. Where it is not, make the record frozen, so a write is refused by construction. Where it is, route the write through one method that checks the whole rule. Add a test that walks the records with a cross-field rule and fails on one that admits a plain field write. This is core work, so it is held to the safety-critical standard in `CLAUDE.md`.

**Why it matters.** The simulator computes from these records. One that breaks its own rule after a later write gives plausible numbers from an impossible patient or state, which the safety-critical standard ranks below an obvious failure.

**Done when.** Every core record with a cross-field rule either refuses a later field write or checks the whole rule on it, and a test that walks those records fails on one that does neither.

**Generator check.** This item is the head.
