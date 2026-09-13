---
id: PL-WZBX
title: bin/docket wave counts the four entries ROADMAP.md's gate places under 'Cleared by v0.5.0 itself' as clearable before the milestone begins, where the gate rule says the milestone clears them
priority: P2
effort: M
status: ready
classes: defect, infra
feature: planning-cadence
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py
added: 2026-09-13
verify: uv run pytest subprojects/docket/tests/test_roadmap.py -q && grep -rq 'def test_a_gate_is_open_when_its_only_open_entries_are_the_milestone_s_own_scope' subprojects/docket/tests/
---

**Problem.** bin/docket wave counts the four entries ROADMAP.md's gate places under 'Cleared by v0.5.0 itself' as clearable before the milestone begins, where the gate rule says the milestone clears them


Found while building `PL-SL70`, which split the gate's open entries into the
ones the gate can clear and the ones waiting on work outside it. This is the
gate's *other* carve-out, and `bin/docket wave` still does not model it.

`ROADMAP.md` § "Debt inside the milestone's own scope" says debt the milestone
itself exists to clear is cleared **by** it rather than before it, and that
"the gate is open when everything *outside* the milestone's scope is clear".
Gate 1 records that split in a group heading of its own - "Cleared by v0.5.0
itself" - which holds four open entries today: `PL-1PSX` (the control-input
timeline is regrouped in full every frame), `PL-B9PY` (decompose
`SimulationView` so two runs render), `PL-RD3B` (split the run's storage out of
`app/controller.py`) and `PL-TCD1` (`SimulationSnapshot`'s six flat compartment
floats). All four are counted in the 53 the beat now asks for.

**Why it matters.** The beat is right in the direction it now errs - the four
are real work and nobody is misled into thinking they are done - but the
transition is not: the gate opens, by `ROADMAP.md`'s own definition, when the
53 minus these four are closed, and `wave` will keep printing `clear the gate`
for four entries that the milestone's implementation is what closes. It is the
same failure `PL-SL70` fixed, one rule along.

**Where.** `subprojects/docket/src/docket/roadmap.py` - `gate_status`, beside
the `blocked_outside` walk `PL-SL70` added, and `MilestoneSection.scope_ids`,
which already reads the ids a section's `Required scope` places.

**The hard part is that the evidence is a group heading, not a field.** The
four are identified by the prose heading they sit under, which `_gate_entries`
deliberately does not read - "the prose around it ... is a person's summary of
the same facts, and reading it would mean parsing sentences". Two routes, and
the second looks cheaper: parse the group headings after all, narrowly; or read
the milestone's own `Required scope` ids, which `scope_ids` already exposes and
which § "Debt inside the milestone's own scope" names as *the* test ("The test
is whether the item appears in the milestone's `Required scope`"). The second
is the rule the roadmap actually states, so it is likely right - but v0.5.0's
`Required scope` has to be checked against the four before that is assumed, and
that check is the first step of the work rather than a conclusion here.

**Done when.** `bin/docket wave` reports entries the gated milestone clears
itself apart from the entries that clear before it begins, takes the beat from
the second, and treats the gate as open when that set is empty - with the rule
read from whatever `ROADMAP.md` § "Debt inside the milestone's own scope" names
as the test, and a test for a gate whose only open entries are its milestone's
own scope.
