---
id: PL-BXB2
title: contrast_check reads only theme.py and simulation_view.py, so a colour declared in any other app/ module is measured by nothing and missed by nothing, and check_colors_live_in_the_theme inspects only the view
priority: P2
effort: M
status: ready
classes: defect, ux
feature: dev-tooling
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_a_colour_in_another_app_module_is_measured' tests/unit/test_contrast_check.py
---


**Problem.** contrast_check reads only theme.py and simulation_view.py, so a colour declared in any other app/ module is measured by nothing and missed by nothing, and check_colors_live_in_the_theme inspects only the view

**Verified 2026-09-14.** `tools/contrast_check.py:95-96` fixes the whole
surface to two files - `THEME = app/theme.py` and `VIEW = app/simulation_view.py` -
and `:76` states the consequence in the tool's own words: a colour "in a module
that is neither `app/theme.py` nor `app/simulation_view.py` is" outside what it
reads. `check_colors_live_in_the_theme` inspects `VIEW` only.

**Why it matters.** Contrast is an accessibility property of what a learner
sees, not of two files. `app/` already holds more than those two modules and the
Qt port adds more, so a colour declared in a third module is measured by nothing
and, because the check reports a pass over the files it did read, missed by
nothing either. The rule "colours live in the theme" is the one that keeps the
measurement possible at all, and it is currently enforced over one file, so the
rule can be broken anywhere else without the check noticing.

**Done when.** `tools/contrast_check.py` measures every colour declared anywhere
under `src/anesthesia_sim/app/`, and `check_colors_live_in_the_theme` fails on a
literal colour in any `app/` module rather than only in the view.
`tests/unit/test_contrast_check.py` covers a colour declared in a third module.
