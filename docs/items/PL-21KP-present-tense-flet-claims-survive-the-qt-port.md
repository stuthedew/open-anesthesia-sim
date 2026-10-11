---
id: PL-21KP
title: Present-tense Flet claims survive the Qt port in module docstrings - app/__init__.py calls the package a Flet application layer, app/formatting.py and app/wash_in.py say they are independent of Flet, and a formatting.py comment justifies FLOW_DISPLAY_DECIMALS by Flet's slider default - and five test modules cite tests/unit/test_simulation_view.py, which moved to tests/integration/
priority: P3
effort: S
status: ready
classes: docs
touches: src/anesthesia_sim/app/__init__.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/wash_in.py, src/anesthesia_sim/app/controller.py, tests/unit/test_formatting.py, tests/unit/test_wash_in.py, tests/unit/test_chart_time_base.py, tests/unit/test_dashboard_frame.py, tests/integration/test_sevo_controller.py
added: 2026-10-11
payoff: a contributor reading the interface package's docstrings learns the toolkit it actually uses and that it depends on the core, and every test citation resolves
verify: ! grep -qF 'Flet application layer' src/anesthesia_sim/app/__init__.py && ! grep -rqF --exclude=test_ignore_check.py 'tests/unit/test_simulation_view.py' tests/
---

**Problem.** Present-tense Flet claims survive the Qt port in module docstrings - app/__init__.py calls the package a Flet application layer, app/formatting.py and app/wash_in.py say they are independent of Flet, and a formatting.py comment justifies FLOW_DISPLAY_DECIMALS by Flet's slider default - and five test modules cite tests/unit/test_simulation_view.py, which moved to tests/integration/

**Found 2026-10-11, working `PL-W3Q5`.** The interface left Flet with `PL-25KS`,
and most of the 40-odd mentions left under `src/` and `tests/` are history that
should stay - "the Flet build's legend rows wrapped", the port's provenance in
`tests/integration/test_simulation_view.py`. These are present-tense claims
instead, and each is false now:

- `app/__init__.py`'s docstring opens "Flet application layer".
- `app/formatting.py`'s and `app/wash_in.py`'s docstrings open "independent of
  Flet and of the scientific core"; both import from `anesthesia_sim.core`, so
  the second half needs rewording too, not only the toolkit's name.
- `app/formatting.py`'s comment above `FLOW_DISPLAY_DECIMALS` justifies one
  decimal by Flet's slider default of 0, and `format_case_discard_warning`'s
  docstring says it is tested "without loading Flet".
- `BranchedCase`'s docstring in `app/controller.py` calls it "Flet-independent".
- `tests/unit/test_formatting.py` and `tests/unit/test_wash_in.py` say their
  subject is checkable "without constructing a Flet interface".
- `tests/unit/test_formatting.py`, `test_wash_in.py`, `test_chart_time_base.py`,
  `test_dashboard_frame.py` and `tests/integration/test_sevo_controller.py`
  cite `tests/unit/test_simulation_view.py`, which is
  `tests/integration/test_simulation_view.py` now.

<!-- absent: tests/unit/test_simulation_view.py -->

A sweep that re-reads each mention and changes only the present-tense ones; no
behaviour moves.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `app/__init__.py` still
opens "Flet application layer", and `grep -rlF tests/unit/test_simulation_view.py
tests/` names the five test modules above plus `tests/unit/test_ignore_check.py`,
whose mention is a mypy-output fixture string and stays.

**Why it matters.** A module docstring is the first thing a contributor reads. One
naming the wrong toolkit, or calling a module independent of the core it imports,
misleads anyone deciding where a calculation may live - and the rule that keeps
simulation out of interface code is stated to readers through these sentences.
The five test citations point at a file that moved.

**Done when.** Each present-tense claim listed above reads true for the Qt
interface or is removed, the five citations name
`tests/integration/test_simulation_view.py`, and the historical mentions are
unchanged.
