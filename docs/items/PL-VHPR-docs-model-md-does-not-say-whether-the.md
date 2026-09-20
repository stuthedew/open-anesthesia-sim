---
id: PL-VHPR
title: docs/MODEL.md does not say whether the delivered concentration is a volume fraction or a partial-pressure fraction, nor at what ambient pressure
status: dropped
feature: delivery-semantics
added: 2026-09-19
closed: 2026-09-20
reason: Overtaken before capture: PL-5K5C (#458, merged 2026-09-07) recorded the sea-level assumption and the vaporizer-class dependence of the delivered-concentration dial in docs/MODEL.md. Every clause of this item's Done-when is answered there - the 760 mmHg assumption and that every concentration is a fraction of it, the note saying a gas-phase fraction and a partial pressure are interchangeable at that pressure, and the split between variable-bypass (sevoflurane, isoflurane) and gas-vapour blender (desflurane, Tec 6 class) with the Datex-Ohmeda operator instruction quoted. Checked clause by clause at triage 2026-09-20; the capture looked under the wrong two sections.
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

**Dropped at triage, 2026-09-20: the premise was already false when this was
captured.** The statement this item asks for is in `docs/MODEL.md` and has been
since `PL-5K5C` merged as `#458` on 2026-09-07, twelve days before the capture.
Checked line by line against the item's own "Done when":

- *the ambient pressure it assumes* — § "Assumptions": "ambient pressure is
  constant, and it is one atmosphere — 760 mmHg. Every concentration in this
  model is a fraction of that pressure, so the model is specified at sea level
  and nowhere else."
- *the convention the delivered concentration follows* — the note under that
  list, "What one atmosphere buys, and why nothing in the model is wrong
  today": a gas-phase fraction and a partial pressure are interchangeable at
  760 mmHg, "so … no statement in this document has to say which of them it
  means", followed by "The delivered-concentration control is where that
  assumption does the most work", which names the dial as a vaporizer dial
  carrying the unit *fraction of 1 atm*.
- *which real device class that matches* — § "Ambient pressure is not
  modelled…" separates **variable bypass** (sevoflurane and isoflurane here;
  delivered partial pressure approximately preserved as ambient pressure falls,
  with Boumphrey and Marshall's approximation worked) from the **gas–vapour
  blender** (desflurane here, the Tec 6 class; constant volumes percent and
  falling partial pressure, with the Datex-Ohmeda operator instruction quoted).

That last section is the same volume-percentage-versus-partial-pressure
contrast this item cites Meyer et al. for, reached from the same device
physics. It also carries the two things the item did not ask for and a reader
needs: the MAC divisor's sea-level nature, and why no $`1/P`$ correction factor
is stored.

**What the capture got right, and why this is a drop rather than a mistake.**
The question is the correct one to have asked, and the survey was right that it
is safety-critical. What went wrong is a search, not a judgment: the section
answering it sits under § "Assumptions" and § "Known limitations" rather than
under § "Concentrations" and § "Runtime controls", which is where the item's
"Where" line looked. Nothing here is owed to the document.
