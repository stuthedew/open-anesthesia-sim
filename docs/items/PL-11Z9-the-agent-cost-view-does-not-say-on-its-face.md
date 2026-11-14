---
id: PL-11Z9
title: The agent cost View does not say on its face that its figures are modelled: 'Liquid used by the vaporizer' can read as a measured volume, and v0.7.0's definition of done asks the modelled label only of the schematic
priority: P1
effort: S
status: done
classes: safety, defect
touches: src/anesthesia_sim/app/agent_cost.py, tests/integration/test_agent_cost_view.py, ROADMAP.md
added: 2026-11-07
closed: 2026-11-11
pr: 2136
payoff: a learner reading the agent cost View is told on its face that the amount and the cost are modelled, so a prediction is not read as what a real vaporizer used
verify: grep -q 'def test_the_cost_view_says_its_amount_and_cost_are_modelled' tests/integration/test_agent_cost_view.py
reenters: PL-B396
---

**Problem.** The agent cost View does not say on its face that its figures are modelled: 'Liquid used by the vaporizer' can read as a measured volume, and v0.7.0's definition of done asks the modelled label only of the schematic

**What a learner sees.** The agent cost View states the delivered agent as "Liquid used by the vaporizer, at 20 degrees C." or "Vapour put out by the vaporizer, at 20 degrees C and 1 atm." (`LIQUID_CAPTION_TEMPLATE` and `VAPOUR_CAPTION_TEMPLATE` in `src/anesthesia_sim/app/agent_cost.py`). Nothing on the View says that the figure is modelled. A learner can read it as the liquid a real vaporizer used, which is a predicted value presented as a measurement. The other Views mark their values: the readouts are headed "Modelled concentrations: {agent}" (`dashboard_frame.py`), the wash-in section says "Modelled, not measured", and every chart hover opens with "Modelled" (`chart_frame.py`).

**How it got here.** v0.7.0's Goal says of the end state: "Every number on it is the number that the rest of the interface gives for the same run at the same instant, and the View says that its values are modelled." That sentence follows the one on the agent cost View, so "it" and "the View" read as the cost View. The Definition of done asks the modelled statement only of the schematic ("The schematic says on its face that its values are modelled"), and its agent cost bullets ask neither that nor a stated precision. The structure read of the section raised this as a query (chapter read 40; `PL-YNFS` quotes it).

**Done when.** The agent cost View says on its face, in words, that its amount and its cost are modelled, and a test asserts it. v0.7.0's Definition of done names the condition for the cost View as it does for the schematic.

**Found by** `PL-YNFS` (slice 5 of the `ROADMAP.md` restructure, 2026-11-07), while answering the structure read's queries against the tree. Filed rather than fixed, because it changes interface wording on the safety-critical path. It is a `safety` finding for triage to class and place on the gate.

**Checked 2026-11-09:** No string in `src/anesthesia_sim/app/agent_cost.py` or `src/anesthesia_sim/app/qt_agent_cost.py` says "modelled" or "modeled" (`grep -n -i "modell\?ed"`). `ROADMAP.md`'s v0.7.0 Definition of done still asks the modelled statement only of the schematic ("The schematic says on its face that its values are modelled").

**Why it matters.** A learner who reads "Liquid used by the vaporizer" as the liquid a real vaporizer used takes a predicted value for a measurement, and the cost beside it carries the same error. The safety-critical standard asks that a predicted value never be shown so that it could be taken for a measurement. `PL-B396`'s Done-when asked for this figure to be "labelled as liquid equivalent and as modelled", and it closed on 2026-11-02 without the modelled label.

**Generator check.** A re-entry of `PL-B396`, closed 2026-11-02, within 30 days, whose Done-when named this label. The fact is which displayed values say on their face that they are modelled; no head states it. Work it with `PL-RJN9`, which changes the same captions.

**Gate, 2026-11-09.** The problem is new: `src/anesthesia_sim/app/agent_cost.py` did not exist at `817a4d88`, the commit that froze Gate 3, and arrived with `PL-B396` on 2026-11-02. The hazard is live: the View shows the unlabelled figure today, so the item cannot be deferred and joins v0.7.0's frozen list under § "Captures after the cut". `bin/docket set` refuses a `safety` class until `ROADMAP.md` places the item, so `classes: safety, defect` and `status: ready` were written in the commit that added the entry.

**Built 2026-11-11.** The View already said it on its face. Since `PL-B396` (#1932), `AgentCostView` puts `INTERPRETATION_DISCLAIMER_TEXT`, "Model outputs — not measurements.", on its heading row beside "Vaporizer output" (`views.py`). The 2026-11-09 check grepped `agent_cost.py` and `qt_agent_cost.py`, which do not hold that row. What was missing was the definition of done and a test that names the statement's place. `ROADMAP.md`'s v0.7.0 definition of done now asks the cost View, as it asks the schematic, to say on its face that its amount and cost are modelled. `test_the_cost_view_says_its_amount_and_cost_are_modelled` in `tests/integration/test_agent_cost_view.py` checks that the statement is visible on the heading's row. It fails with "not enough values to unpack" when the row's statement is removed (checked by commenting out the `addWidget` line). The `verify:` command was rewritten to point at that file, because the statement is drawn by the Qt View and a test in `tests/unit/` builds no widget.
