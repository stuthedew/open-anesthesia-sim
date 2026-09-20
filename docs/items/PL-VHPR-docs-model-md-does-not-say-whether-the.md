---
id: PL-VHPR
title: docs/MODEL.md does not say whether the delivered concentration is a volume fraction or a partial-pressure fraction, nor at what ambient pressure
status: untriaged
feature: delivery-semantics
added: 2026-09-19
---

**Problem.** docs/MODEL.md does not say whether the delivered concentration is a volume fraction or a partial-pressure fraction, nor at what ambient pressure
 — found while writing `docs/machine-survey.md` for `PL-4DCG`.

The model works in partial-pressure fractions throughout: the circuit's field is
`delivered_partial_pressure_fraction`, and `docs/MODEL.md` § "Concentrations"
sets the convention. What no document states is which convention *the dial the
user turns* follows, or at what ambient pressure the two coincide.

**Why it matters, and why it is not pedantry.** The two conventions are a real
device difference, not a notational one. Meyer et al., writing for a workstation
manufacturer, state it: "The desflurane vaporizer principle described here
delivers a fixed volume percentage, making it different from conventional
vaporizers, which deliver fixed partial pressures" (*Modern Anesthetics*,
Handbook of Experimental Pharmacology vol. 182, Springer 2008, p. 454; read at
full text 2026-09-19 from the private reference corpus). So a dial reading of 6%
means two different things depending on the device, and they diverge wherever
ambient pressure is not one atmosphere — which is every hospital above sea level.
`CLAUDE.md` puts this squarely in the safety-critical class: the correct number
with the wrong units is still a safety failure, and this is a units question
about the one control a learner maps onto a physical dial.

**The cheap half is probably all of it.** The model is internally consistent and
no computed value is wrong; what is missing is the sentence saying the simulator
holds partial-pressure fractions at one atmosphere, so a reader knows which
device convention the dial matches and which it does not. Whether the model
should ever carry ambient pressure is a bigger question and belongs to a
milestone, not here.

**Where.** `docs/MODEL.md` § "Concentrations" and § "Runtime controls";
`src/anesthesia_sim/core/concentration.py`; `docs/machine-survey.md` § "(b1)".

**Done when.** `docs/MODEL.md` states the convention the delivered concentration
follows and the ambient pressure it assumes, and says which real device class
that matches.
