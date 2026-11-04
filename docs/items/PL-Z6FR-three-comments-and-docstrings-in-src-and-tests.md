---
id: PL-Z6FR
title: Three comments and docstrings in src/ and tests/ still call arterial blood flow-limited, and core/tissue.py writes "perfusion limited" unhyphenated, where docs/MODEL.md now says "perfusion-limited" for the lung's and each tissue's exchange with blood
priority: P3
effort: S
status: ready
classes: defect
feature: prose-quality
touches: src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/tissue.py, tests/unit/test_governing_equations.py
deferred-from: v0.7.0 - captured after the freeze; comment wording in core that changes no displayed value
added: 2026-11-04
payoff: a developer reading the gas-exchange code meets the same term, with the same meaning, as the model specification
verify: ! grep -r -q -i -E 'flow[- ]limited|perfusion limited' src/anesthesia_sim/core tests/unit
---

**Problem.** `PL-T9VT` made `docs/MODEL.md` use one term, "perfusion-limited", and defined it in § "Model boundary" as a property of the exchange between blood and the lung or a tissue, not of the blood. The code's comments and docstrings still use the old wording in four places, found on 2026-11-04 with `grep -rn -i -E "flow[- ]limited|perfusion limited" src tests`:

- the module docstring of `src/anesthesia_sim/core/blood.py` says "this model's flow-limited arterial simplification";
- a comment in `build_system_matrix` in `src/anesthesia_sim/core/governing_equations.py` says "Arterial blood is flow-limited";
- a comment in `test_each_tissue_row_is_that_group_s_balance` in `tests/unit/test_governing_equations.py` says "Arterial blood is flow-limited";
- the docstring of `TissueGroup.venous_outflow_partial_pressure_fraction` in `src/anesthesia_sim/core/tissue.py` writes "perfusion limited" without the hyphen.

`PL-T9VT` left them because they are in `core/` and the tests, where a fix made in passing is not allowed, and its brief named only `docs/MODEL.md`.

**Read at triage, 2026-11-04.** The same `grep` on `main` at `f369249fa` still
finds the four sites. It also finds the word "flow-limited" in
`src/anesthesia_sim/data/patients/reference_adult.json`, where it quotes Weber
et al.'s description of Gas Man. That quotation stays as written.

**Why it matters.** A developer who changes the gas-exchange equations reads
these comments beside the code. They describe arterial blood as
"flow-limited", while `docs/MODEL.md` § "Model boundary" defines
"perfusion-limited" as a property of the exchange between blood and the lung or
a tissue. The code's comments then contradict the specification's definition.

**Done when.** The four sites use "perfusion-limited" in the sense that
`docs/MODEL.md` § "Model boundary" defines. For example, arterial blood leaves
the lung at the alveolar partial pressure because the lung's exchange is
perfusion-limited. The search above then finds only the quotation in
`reference_adult.json`.

**Generator check.** One-off. This is the rest of `PL-T9VT`'s change of term.
That item's brief covered only `docs/MODEL.md`, because a change made in passing
is not allowed in `core/`, and it filed this item for the code. No head states
the term's definition as its fact.
