---
id: PL-WJNS
title: docs/MODEL.md's circuit exhaust runs unconditionally, but a machine in closed-circuit mode shuts the surplus gas valve
priority: P1
effort: S
status: ready
classes: science, docs
feature: model-boundary-statements
touches: docs/MODEL.md
added: 2026-09-19
payoff: tells a reader whether closed-circuit machines were excluded from the model deliberately or overlooked, where today the document is silent
verify: grep -qF 'surplus gas valve' docs/MODEL.md
---

**Problem.** docs/MODEL.md's circuit exhaust runs unconditionally, but a machine in closed-circuit mode shuts the surplus gas valve
 — found while writing `docs/machine-survey.md` for `PL-4DCG`.

`docs/MODEL.md` § "Breathing circuit" states that "an equal fresh-gas volume
leaves through the exhaust at the current mixed-circuit concentration", and
§ "Circuit exhaust" and the mass-balance identity are built on that being
unconditional. It is how a semi-closed circle behaves and it is not how every
machine behaves in every mode.

**The evidence.** Meyer et al., describing the Zeus: "In the automatic controlled
mode of the Zeus anesthesia machine, the surplus gas valve can be closed to
prevent any loss of gas volume" (*Modern Anesthetics*, Handbook of Experimental
Pharmacology vol. 182, Springer 2008, p. 465; read at full text 2026-09-19 from
the private reference corpus). A machine running that way has no exhaust term at
all, so the circuit is not losing agent at the rate the identity assumes.

**Why it matters.** This is a boundary statement rather than a defect: the model
is correct for the machines it describes, and says nothing about the ones it does
not. But `docs/MODEL.md` § "Model boundary" and § "Assumptions" are where a
reader learns what the model claims, and neither records that a semi-closed
circle is being assumed — so a reader who knows closed-circuit machines exist
cannot tell whether the model excluded them or overlooked them.

It also matters ahead of `PL-FG9D`, and that is the reason to record it now: the
survey's conclusion is that this is the one machine variable reaching an
*equation* rather than a coefficient, which makes it the one an implementation is
most likely to represent as a small exhaust instead of as a different
conservation statement.

**Where.** `docs/MODEL.md` § "Breathing circuit", § "Circuit exhaust",
§ "Mass-balance identity", § "Assumptions"; `docs/machine-survey.md` § "(b11)".

**Done when.** `docs/MODEL.md` records that the exhaust term assumes a
semi-closed circle, and names closed-circuit operation as outside what the
current equations describe.
