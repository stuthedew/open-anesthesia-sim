---
id: PL-4X5B
title: tools/literal_home_check.py's baseline holds 29 bare layout literals in src/anesthesia_sim/app/ (14 in qt_widgets.py, 7 in qt_chart.py, among them 90 three times and 6 three times) and no open item names them
priority: P3
effort: M
status: ready
classes: refactor
feature: one-source-of-truth
touches: src/anesthesia_sim/app/, tools/literal_home_check.py
added: 2026-10-19
payoff: each layout spacing in the interface has one name, so changing it cannot leave a copy of the old value elsewhere on screen
verify: ! grep -qF '"src/anesthesia_sim/app/' tools/literal_home_check.py
---

**Problem.** tools/literal_home_check.py's baseline holds 29 bare layout literals in src/anesthesia_sim/app/ (14 in qt_widgets.py, 7 in qt_chart.py, among them 90 three times and 6 three times) and no open item names them

**Why it matters.** Each of these numbers is a spacing, margin or angle typed inline. Where one value is meant to match another, such as the three `90`s in `qt_chart.py`, nothing ties them together, so changing one leaves the others at the old value. `tools/literal_home_check.py` already refuses a new bare literal, so the baseline is the only place these copies can still live. It can only shrink, and no item was draining it.

**Done when.** Each of the 29 literals is a named constant in the module that uses it, or in one shared layout module where several modules use the same value. `BASELINE` in `tools/literal_home_check.py` has no `src/anesthesia_sim/app/` entry left. The interface looks the same before and after: a screenshot of the default run shows no change.

**Checked 2026-10-24.** `BASELINE` holds six `src/anesthesia_sim/app/` keys with 29 entries in all: `chart_frame.py` 2, `dashboard_frame.py` 2, `qt_chart.py` 7, `qt_widgets.py` 14, `run_surfaces.py` 1 and `run_view.py` 3.

**Generator check.** Bookkeeping. These are the baseline `tools/literal_home_check.py` recorded when it landed under `PL-40SJ`, so they are not new inflow, and nothing has added to them since.
