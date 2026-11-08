---
id: PL-DXJR
title: docs/MODEL.md's hazard table has no row for entering an identifiable patient's parameters to predict for that patient, the foreseeable misuse its intended-use section names, so that misuse has a stated boundary and no listed mitigation or test
priority: P1
effort: S
status: done
classes: docs, safety
feature: presentation-safety
milestone: v0.6.15
touches: docs/MODEL.md, ROADMAP.md, tests/integration/test_controller.py
added: 2026-11-02
closed: 2026-11-02
pr: 1948
payoff: the model specification names what keeps a real patient's data out of the simulator and the test that holds it, so the patient-factor work knows which safeguard it removes
verify: grep -q 'def test_every_run_simulates_the_shipped_reference_adult' tests/integration/test_controller.py && grep -q "What keeps a real patient's data out of a run" docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Intended use, and the safety class this
project holds itself to" names one foreseeable misuse: entering an identifiable
patient's weight, age or cardiac output to predict for that patient. ISO
14971:2019 clause 5.2 asks for that misuse to be documented with its
mitigation. Every row of the hazard table in § "Reasonably foreseeable misuse,
and the hazards the presentation carries" covers a misreading of the display
instead. Until `PL-J8CG`, two sentences in those sections said the misuse was
listed in the table with mitigations, which was not true. A blind review of
`PL-J8CG` found this (pass 2, finding F2), and that branch rewrote the sentence
to say the row does not exist yet.

**Why it matters.** The patient-covariate work planned in `ROADMAP.md` makes the
misuse possible. A boundary stated in prose, with no mitigation or test, is the
weakest control ISO 14971 recognises.

**How.** Decide what the mitigation is now, while the interface accepts no
patient covariates: probably the intended-use statement plus the fixed
reference patient, so the row can name a test that the patient is the shipped
reference adult. Add the row, or its declared-none form naming this item, and
reword the sentence in § "This is an engineering bar, not a regulatory status"
to point at it.

**Done when.** The hazard table has a row for the misuse, with its test or
``no test yet (`PL-XXXX`)`` naming an open item, and the sentence that
`PL-J8CG` wrote says the row exists.

**Generator check.** Not a generator. It is the one hazard the intended-use
section named that the table did not carry, and no other item shares its cause.

**Fixed 2026-11-02.** The mitigation was decided as the brief proposed. While
the interface accepts no patient covariates, two safeguards stand against
entering a real patient's data. The first is the use statement
(`USE_DISCLAIMER_TEXT`), which stays in view. The second is the fixed reference
adult: no control accepts a weight, age, sex, height or body composition, and
every run keeps `data/patients/reference_adult.json`'s compartment volumes and
perfusion fractions. `docs/MODEL.md` now has:

- a first row in the hazard table, "reading a run as a prediction for a real
  patient whose data was entered into it", naming four tests;
- a new subsection, § "What keeps a real patient's data out of a run", which
  lists the two safeguards and states the residual risk. A learner can still
  set cardiac output and alveolar ventilation to a patient's measured values,
  and nothing refuses that. Only the use statement stands against reading such
  a run as a prediction;
- the sentence in § "This is an engineering bar, not a regulatory status"
  rewritten to say the row exists and to point at the subsection.

The cell is one sentence and a pointer, with the detail in the subsection,
following `PL-ZT47`'s fifth pattern.

`tests/integration/test_controller.py` gains
`test_every_run_simulates_the_shipped_reference_adult`. It pins the ways a
patient could get into a run today: one JSON file under `data/patients/`,
`AgentUptakeSystem.for_agent` taking only an agent, the four learner controls,
and the controller's constructor arguments. It then moves every control,
changes the agent and resets, collecting each run's stretches before the next
run replaces them. Every stretch must hold the reference adult's alveolar and
venous volumes, tissue volumes and perfusion fractions. It fails when patient
factors arrive, on purpose. The two blind reviews on `#1948` found that a
first version checked only the stretch after the Reset and pinned no file or
builder, so the trip wire promised more than it held. Both are fixed, and the
table cell now names the residual case too.
`ROADMAP.md` planned-milestone item 30 gains a paragraph saying that the item
removes this safeguard and rewrites the subsection and its row.

The three disclaimer tests the row names already existed:
`test_the_educational_disclaimer_says_what_the_tool_is_not`,
`test_the_dashboard_carries_the_educational_disclaimer` and
`test_the_region_and_the_use_disclaimer_stay_in_the_viewport`.

**Decision, 2026-11-02.** The hazard row relies on the disclaimer alone when a
learner sets the cardiac output or ventilation dial to a real patient's value
(project owner, 2026-11-02, ratified, over a caption beside those two dials).
His words: "rely on disclaimer. I don't want to make it too busy with excess
text". He also said that changing cardiac output and ventilation is a core
feature, so the dials stay as they are.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "Planned milestones" carried this paragraph under item 30, "Patient factors". In it, "this item" means item 30, "here" means that entry, "this file" means `ROADMAP.md`, and "above" and "below" point within `ROADMAP.md` as it then stood. Item 30 keeps that this item rewrites that section and its hazard row.

> *It removes a safeguard that `docs/MODEL.md` names (`PL-DXJR`).* The fixed reference adult is one of the two safeguards in `docs/MODEL.md` § "What keeps a real patient's data out of a run". Once age, sex and weight are inputs, a run can be built from a real patient's data. So this item rewrites that section and its hazard row. `test_every_run_simulates_the_shipped_reference_adult` pins the one shipped patient file and the absence of any patient argument or control, so it fails when the inputs land, which makes the rewrite hard to miss.
