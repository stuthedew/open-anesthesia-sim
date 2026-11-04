---
id: PL-Z6FR
title: Three comments and docstrings in src/ and tests/ still call arterial blood flow-limited, and core/tissue.py writes "perfusion limited" unhyphenated, where docs/MODEL.md now says "perfusion-limited" for the lung's and each tissue's exchange with blood
status: untriaged
feature: prose-quality
added: 2026-11-04
---

**Problem.** `PL-T9VT` made `docs/MODEL.md` use one term, "perfusion-limited", and defined it in § "Model boundary" as a property of the exchange between blood and the lung or a tissue, not of the blood. The code's comments and docstrings still use the old wording in four places, found on 2026-11-04 with `grep -rn -i -E "flow[- ]limited|perfusion limited" src tests`:

- the module docstring of `src/anesthesia_sim/core/blood.py` says "this model's flow-limited arterial simplification";
- a comment in `build_system_matrix` in `src/anesthesia_sim/core/governing_equations.py` says "Arterial blood is flow-limited";
- a comment in `test_each_tissue_row_is_that_group_s_balance` in `tests/unit/test_governing_equations.py` says "Arterial blood is flow-limited";
- the docstring of `TissueGroup.venous_outflow_partial_pressure_fraction` in `src/anesthesia_sim/core/tissue.py` writes "perfusion limited" without the hyphen.

`PL-T9VT` left them because they are in `core/` and the tests, where a fix made in passing is not allowed, and its brief named only `docs/MODEL.md`.
