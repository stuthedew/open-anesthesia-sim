---
id: PL-TCD1
title: SimulationSnapshot still names six flat compartment floats, so the readouts cannot express a second substance now that the recorded run can
priority: P2
effort: M
status: needs-decision
classes: refactor, anticipated
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-09-05
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

**Decision needed.** Decide whether the snapshot's compartment fields follow the
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
