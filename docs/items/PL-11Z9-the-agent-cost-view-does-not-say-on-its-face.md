---
id: PL-11Z9
title: The agent cost View does not say on its face that its figures are modelled: 'Liquid used by the vaporizer' can read as a measured volume, and v0.7.0's definition of done asks the modelled label only of the schematic
status: untriaged
touches: src/anesthesia_sim/app/agent_cost.py, ROADMAP.md
added: 2026-11-07
---

**Problem.** The agent cost View does not say on its face that its figures are modelled: 'Liquid used by the vaporizer' can read as a measured volume, and v0.7.0's definition of done asks the modelled label only of the schematic

**What a learner sees.** The agent cost View states the delivered agent as "Liquid used by the vaporizer, at 20 degrees C." or "Vapour put out by the vaporizer, at 20 degrees C and 1 atm." (`LIQUID_CAPTION_TEMPLATE` and `VAPOUR_CAPTION_TEMPLATE` in `src/anesthesia_sim/app/agent_cost.py`). Nothing on the View says that the figure is modelled. A learner can read it as the liquid a real vaporizer used, which is a predicted value presented as a measurement. The other Views mark their values: the readouts are headed "Modelled concentrations: {agent}" (`dashboard_frame.py`), the wash-in section says "Modelled, not measured", and every chart hover opens with "Modelled" (`chart_frame.py`).

**How it got here.** v0.7.0's Goal says of the end state: "Every number on it is the number that the rest of the interface gives for the same run at the same instant, and the View says that its values are modelled." That sentence follows the one on the agent cost View, so "it" and "the View" read as the cost View. The Definition of done asks the modelled statement only of the schematic ("The schematic says on its face that its values are modelled"), and its agent cost bullets ask neither that nor a stated precision. The structure read of the section raised this as a query (chapter read 40; `PL-YNFS` quotes it).

**Done when.** The agent cost View says on its face, in words, that its amount and its cost are modelled, and a test asserts it. v0.7.0's Definition of done names the condition for the cost View as it does for the schematic.

**Found by** `PL-YNFS` (slice 5 of the `ROADMAP.md` restructure, 2026-11-07), while answering the structure read's queries against the tree. Filed rather than fixed, because it changes interface wording on the safety-critical path. It is a `safety` finding for triage to class and place on the gate.
