---
id: PL-043
title: Decide whether the vaporizer dial should move in real increments
priority: P2
effort: S
status: ready
classes: ux
feature: vaporizer-controls
touches: docs/MODEL.md
added: 2026-08-24
---

**Problem.** `_delivered_concentration_slider` has no `divisions`, so the
delivered-agent setting is continuous over 0 to the agent's dial maximum. A
user can set 4.37% sevoflurane. Real variable-bypass vaporizers are dialed in
discrete increments, and the Tec 6 desflurane vaporizer is dialed in steps
over most of its range.

**Why it matters.** The delivered concentration is the one number in this
interface a user maps onto a physical action at a real machine, so a control
offering positions no vaporizer has teaches a dial that does not exist.
Against that: the continuous control is a better instrument for exploring the
model's response, which is the simulator's actual purpose, and quantizing it
makes some of the model's behavior unreachable.

**Where.** `docs/MODEL.md` § "Runtime controls".

**Decided.** Leave the control continuous, and record the choice.

1. **Fidelity should match the learning objective.** This is a
   pharmacokinetic model explorer — six concentration traces against an
   equations document — not a machine trainer. There is no vaporizer graphic,
   no flowmeter, no machine check. Detent fidelity on one control raises
   apparent device realism without the substance behind it, which is worse for
   transfer than being plainly a model explorer: it invites trust in a device
   metaphor the rest of the tool never honours.
2. **The interface already does not claim to be a dial.**
   `formatting.format_delivered_label` renders "Delivered sevoflurane", not
   "Vaporizer".
   This item's title says dial; the interface never does.
3. **Consistency across the four runtime controls.** Ventilation and cardiac
   output are patient states, not dials. Fresh gas flow is a real flowmeter
   with real granularity and is continuous here too. Quantizing only this one
   would make a single control assert a physicality the others deny.
4. **Doing it to this repository's standard is well beyond `S`.** An increment
   is not one number: real variable-bypass dials are finer at the low end and
   coarser above it, and the Tec 6 is a different device class. Meeting the
   citation discipline this item itself demands — the same as
   `max_delivered_concentration_percent`, which carries a device specification
   and a note on what it does and does not license — means a per-agent
   *piecewise* increment schedule, each segment cited, in the agent JSON and
   the provenance table.
5. **It removes reachable model behavior**: smooth sweeps to see response
   shape, and small step changes.

Quantizing with a fine-adjust escape is rejected as the worst of both: it
carries the full citation cost and adds a coarse/fine mode, against
`CLAUDE.md`'s preference for minimizing hidden modes.

**Accepted cost.** A learner can set 4.37% sevoflurane, which no vaporizer
offers. If actual machine simulation is ever built — an interlock baseline, a
modeled vaporizer — this decision should be revisited, because the fidelity
argument reverses at that point.

**Better substitute for detents, already filed.** Marking what the current
setting is in MAC for the agent in use teaches what actually transfers to a
real machine, needs no new citations (`mac_percent` is already cited per
agent), and makes nothing unreachable. This does *not* need a new item:
PL-DHV7 already covers MAC as a display unit across `app/simulation_view.py`'s
labels and readouts, and carries the interpretation discipline a MAC label
requires. Fold the delivered-concentration control into that item rather than
labelling it separately.

**Also in scope.** `docs/MODEL.md` § "Runtime controls" still reads "delivered
*sevoflurane* concentration", stale since the application went multi-agent.

**Done when.** `docs/MODEL.md` § "Runtime controls" states what the
delivered-concentration control offers and why it is continuous, and no longer
names a single agent.
