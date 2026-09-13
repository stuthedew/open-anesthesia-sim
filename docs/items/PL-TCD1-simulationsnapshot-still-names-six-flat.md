---
id: PL-TCD1
title: SimulationSnapshot still names six flat compartment floats, so the readouts cannot express a second substance now that the recorded run can
priority: P2
effort: M
status: done
classes: refactor, anticipated
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, tests/unit/test_simulation_view.py
added: 2026-09-05
closed: 2026-09-13
verify: uv run pytest tests/unit/test_simulation_view.py -q -k readout_row_names_the_substance
---

**Problem.** `PL-W3DD` re-keyed the recorded run by substance, but
`SimulationSnapshot` (`app/controller.py`) still carries
`circuit_concentration_fraction` and its five siblings as flat named floats,
and `simulation_view.py` formats the six readouts and the six MAC multiples
straight off them. The chart can now name the substance it draws; the numbers
beside it cannot.

**Why it matters.** Not a defect today - one substance is recorded, so the
readouts are correct and unambiguous. It matters when nitrous oxide lands
(`ROADMAP.md` planned item 6): a second substance reaches the chart as an
entry in a mapping and the readouts as six more fields, which is the shape
`PL-W3DD` removed from the recorded row for the reasons its brief gives.
The asymmetry is also a live reading hazard in its own right - the two halves
of one frame would describe the run in different terms.

**Where.** `app/controller.py` (`SimulationSnapshot`, `snapshot()`),
`app/simulation_view.py` (the compartment readouts and their MAC multiples),
`docs/MODEL.md` § "Interface boundary".

**Decision needed — ANSWERED 2026-09-13, see below.** Decide whether the snapshot's compartment fields follow the
recorded row's shape or stay flat with the substance named alongside. They are
not the same question: a snapshot is one instant's state for the *running*
agent, and a readout row that became a mapping would push the substance choice
into the formatting layer, where `PL-W3DD` deliberately did not put it.

**Done when.** One frame describes the run in one vocabulary: the snapshot's
compartment fields and the readouts beside the chart name the substance they
belong to, in whichever shape the decision above settles, and `docs/MODEL.md`
§ "Interface boundary" says which. Adding a second substance then adds no
field to `SimulationSnapshot`.

**Found.** Closing `PL-W3DD`, 2026-09-05. Deliberately out of that item's
scope: its "Done when" is about the recorded history, and widening it to the
readouts would have been scope this session did not have.

## Answered 2026-09-13 (project owner): neither shape as filed

**The naming half now, the reshape declined and dated.** The snapshot's
compartment fields stay flat; the interface states the substance they belong
to; `docs/MODEL.md` records why and when the mapping arrives.

**`ROADMAP.md` had already decided the structural half, and this item's
Done-when contradicted it.** § "Designed for forking", in the v0.4.0 section:

> What is deliberately *not* designed for in advance: **per-compartment agent
> amounts in the snapshot**, a schematic view, run comparison, or a snapshot
> policy. Those are cheap to add when their milestone arrives, and adding
> unused structure now would be speculative generality rather than
> groundwork. The distinction is whether retrofitting invalidates recorded
> runs or merely adds a field.

A snapshot is one instant's transient state: never stored, never compared
against a later run, never read back. Reshaping it later adds a field and
invalidates nothing, which puts it on the declined side of that line. The
recorded row was the opposite case, which is why `PL-W3DD` was right to
reshape it first. So this item's "Adding a second substance then adds no field
to `SimulationSnapshot`" is withdrawn — it is a requirement the roadmap
already declined, written into a brief by a session that had not read it
against that section.

**The item's second argument survives whole, and is what was built.** The
asymmetry was a live reading hazard on its own terms: the chart could name the
substance it drew and the six numbers above it could not, so one frame
described the run in two vocabularies and a reader carried the agent over from
the selector. `simulation_view.py` now heads the readout row with
`COMPARTMENT_SUBSTANCE_TEMPLATE` — "Modelled concentrations: Sevoflurane" —
refreshed from `snapshot.agent_display_name` in the same pass as
`_mac_reference_text`, so it cannot lag an agent change.

**The snapshot needed no field.** `agent_id` and `agent_display_name` already
travel with the six fractions; what was missing was saying that they belong
together, which is now a comment on the block making the same argument
`agent_mac_percent`'s docstring already made for the divisor.

**Where the decision is written.** `docs/MODEL.md` § "Interface boundary"
gains "What a snapshot is, and why it is not keyed the same way", beside the
"What a recorded sample is" paragraph it is the counterpart to. It names the
roadmap's test, the Phase 1 milestone the mapping arrives with, and the
constraint the asymmetry may not breach — that one frame may not describe the
run in two vocabularies.

**Test.** `test_the_readout_row_names_the_substance_its_numbers_belong_to`
asserts the label and that it follows an agent change, for the reason
`_mac_reference_text`'s own test gives: a confident label on the wrong agent's
numbers is the correct value under the wrong name.
