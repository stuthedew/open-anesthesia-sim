---
id: PL-PXT7
title: contrast_check reads a colour only from a constant that is exactly #RRGGBB, treats only the :disabled literal as a disabled state, and lists files without -z, so a colour built from parts, a Qt :!enabled rule and a non-ASCII path go unread; latent
priority: P3
effort: S
status: ready
classes: defect
touches: tools/contrast_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: Every colour the interface authors outside the theme, and every disabled-state rule, is measured or refused, and the base comparison reads the whole palette
verify: grep -q 'def test_a_hex_colour_built_from_parts_or_inside_a_stylesheet_is_refused' tests/unit/test_contrast_check.py && grep -q 'def test_a_not_enabled_rule_no_requirement_cites_is_an_error' tests/unit/test_contrast_check.py && grep -q 'def test_a_base_module_whose_path_git_would_quote_is_read' tests/unit/test_contrast_check.py
recurrences: 2026-10-06 PL-JTCQ withdrawn 2026-10-06 PL-R417
---

**Problem.** contrast_check reads a colour only from a constant that is exactly #RRGGBB, treats only the :disabled literal as a disabled state, and lists files without -z, so a colour built from parts, a Qt :!enabled rule and a non-ASCII path go unread; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`HEX_COLOR_RE` (`^#[0-9A-Fa-f]{6}$`) reads a colour only from a string constant that is exactly `#RRGGBB`; the disabled-state reader knows `:disabled` and not Qt's `:!enabled`; and its `git ls-tree` runs without `-z`, so git C-quotes a non-ASCII path. Not members of `PL-R417`. Latent: the stylesheets use whole constants and `:disabled`, and no tracked path is non-ASCII.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, over scratch trees holding a one-line `theme.py` under `src/anesthesia_sim/app/`: `check_colors_live_in_the_theme`, over a view module holding `LOOSE = "#D9E2EC"`, `STRAY = "#D9E2" + "EC"` and a call `w.setStyleSheet("QLabel { color: #D9E2EC; }")`, reported `LOOSE` alone. `check_authored_disabled_colours_are_measured` reported one offender for an uncited `QPushButton:disabled` rule and none for the same rule spelled `QPushButton:!enabled`. In a scratch repository whose committed app modules include one named vué.py holding `EXTRA = "#123456"`, `git ls-tree -r --name-only` printed that path C-quoted, `"src/anesthesia_sim/app/vu\303\251.py"`, and `read_base` at `HEAD` returned a palette without `EXTRA`, while `read_palette` over the same tree on disk held it.

**Why it matters.** This tool holds the interface's colours to their contrast and colour-vision requirements, and it can only measure a colour it reads: one written inline in a stylesheet or built from parts outside `app/theme.py` is neither refused nor measured, and a `:!enabled` rule is an authored disabled colour that escapes the citation `PL-DHBX` requires of one. `read_base` dropping a module leaves the base palette short without saying so, so the comparison with the base answers from a partial reading, the case `_git_read` exists to refuse. Latent: the app's stylesheets interpolate whole theme constants and spell `:disabled`, and no tracked path under `src/anesthesia_sim/app/` is non-ASCII.

**Generator check.** A one-off reader: which colours a stylesheet applies, read only from whole `#RRGGBB` constants and the `:disabled` literal. Its `-z` half shares how git quotes a path it prints with `PL-MR8Z`; two items, and no head states it.

**Done when.** Three repairs, each with its test in `tests/unit/test_contrast_check.py`. `check_colors_live_in_the_theme` refuses a hex colour outside the theme written inside a longer string, such as a stylesheet's `color: #D9E2EC`, or concatenated from string parts: `test_a_hex_colour_built_from_parts_or_inside_a_stylesheet_is_refused`. `check_authored_disabled_colours_are_measured` reads a `:!enabled` rule as the disabled rule it is: `test_a_not_enabled_rule_no_requirement_cites_is_an_error`. `read_base` lists the base's modules with `ls-tree -z`, so a module whose path git would C-quote is read into the base palette: `test_a_base_module_whose_path_git_would_quote_is_read`.
