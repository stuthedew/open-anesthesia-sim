---
id: PL-WMCJ
title: docs/MODEL.md's Known limitations never names intertissue diffusion, the route Eger and Saidman 2005 describe for agent reaching fat, though every tissue group here exchanges only with arterial blood
status: untriaged
touches: docs/MODEL.md
added: 2026-09-23
---

**Problem.** docs/MODEL.md's Known limitations never names intertissue diffusion, the route Eger and Saidman 2005 describe for agent reaching fat, though every tissue group here exchanges only with arterial blood

**Found 2026-09-23 in `PL-QYBW`'s design round** (the chart's percent axis
compressing fat).

`src/anesthesia_sim/core/tissue.py` models each tissue group as exchanging
agent "with arterial blood in proportion to its own blood flow, independently
of every other tissue group". That excludes intertissue diffusion: agent
moving directly from a lean tissue into fat lying next to it. `docs/MODEL.md`
never names this, not in § "Assumptions" and not in § "Known limitations".
The list does have "diffusion limitation", which is a different mechanism.

The uptake literature names it for exactly the compartment the chart draws
near zero: "Obesity increases the depots available for storage of anesthetic,
including anesthetic that reaches fat by intertissue diffusion. Such
anesthetic returns to the circulation to delay recovery ... However, the
increased anesthetic in fat occurs at a lower partial pressure and thus might
not influence emergence materially." (Eger EI II, Saidman LJ. Illustrations of
inhaled anesthetic uptake, including intertissue diffusion to and from fat.
*Anesth Analg* 2005;100(4):1020-1033,
https://doi.org/10.1213/01.ANE.0000146961.70058.A1. Retrieved from PubMed,
PMID 15781517, and verified against the abstract 2026-09-23.) Carpenter et al.
needed a fifth compartment to fit human washout, with "a time constant that
lies between the time constants predicted for muscle and fat" (*Anesth Analg*
1986;65(6):575-82, PMID 3706798, https://doi.org/10.1213/00000539-198606000-00004;
the abstract, as read by this session's research agent, does not attribute it
to intertissue diffusion).

**Fix.** Add intertissue diffusion to § "Known limitations", saying which way
it biases fat's modelled partial pressure and amount, and with the source.
Establishing the direction and size needs more than an abstract, so check the
Eger and Saidman full text, or the private reference corpus's uptake chapters,
before writing the sentence.

**Done when.** § "Known limitations" names intertissue diffusion, its effect on
the fat compartment and its source.
