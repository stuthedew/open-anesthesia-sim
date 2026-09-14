---
id: PL-BXB2
title: contrast_check reads only theme.py and simulation_view.py, so a colour declared in any other app/ module is measured by nothing and missed by nothing, and check_colors_live_in_the_theme inspects only the view
priority: P1
effort: S
status: done
classes: defect, safety, infra
feature: qt-port
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py, docs/ARCHITECTURE.md
added: 2026-09-14
closed: 2026-09-14
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_a_color_declared_in_any_other_app_module_is_measured' tests/unit/test_contrast_check.py
---


**Problem.** contrast_check reads only theme.py and simulation_view.py, so a colour declared in any other app/ module is measured by nothing and missed by nothing, and check_colors_live_in_the_theme inspects only the view

**Why it matters.** This check is the accessibility floor: WCAG 2.2 AA over
every declared pair, and the Brettel dichromacy projection over the chart
traces (`PL-JX0Z`). `PL-JRS3`'s probe D1 measured the hole on 2026-09-14: a new
module holding a selection colour at 1.07:1 on the panel passed with `0 errors`,
because `read_palette` and `read_symbols` iterate a two-path tuple - `THEME`
and `VIEW` - and `check_colors_live_in_the_theme` parses `VIEW` alone. A colour
the tool never reads is a contrast claim nobody measured, under a `make check`
that reports green. Nothing exploits it today - no hex constant sits outside
`app/theme.py` anywhere under `src/` - but `PL-25KS` builds the Qt view
decomposed from the start, so the port is exactly the change that creates the
modules this tool cannot see. It lands before the port's first commit for that
reason (`ROADMAP.md` § "v0.4.26 - the interface moves to Qt" → "Required
scope" item 4).

**Done when.** `read_palette`, `read_symbols` and
`check_colors_live_in_the_theme` read every module under
`src/anesthesia_sim/app/` - the theme first, so an alias of a theme name still
resolves - rather than two named paths, so a colour declared in any interface
module is measured, and any module but the theme declaring one is refused. The
report says how many modules it read, so a reader can see a decomposed view
being measured rather than assume it. A regression test reproduces probe D1
and asserts the error.

**What landed, 2026-09-14.** `app_modules` replaces the two-path tuple: every
`.py` under `src/anesthesia_sim/app/`, recursively, the theme first so an alias
of a theme name resolves. `read_palette`, `read_symbols` and
`check_colors_live_in_the_theme` iterate it. The last also refuses a hex
literal written inline outside the theme - one step past the brief's letter,
taken because a literal has no name a requirement can cite and so is the one
form of colour that widening the read could never measure; refusing it is the
only treatment that keeps "measured or refused" true for every module. The
report's first line states the module count. `PL-JRS3`'s probes D1 and C are
regression tests: D1 now errors twice, once below the ratio and once outside
the theme, and C resolves its citations instead of failing with 68.

**Triaged twice on 2026-09-14.** A second pass (`PL-6FJ5`, `PL-66X4`) verified
the finding independently and triaged it at `P2` under `dev-tooling`; the
fields above are the project owner's (`P1`, `safety`, `qt-port`, 2026-09-14),
and the work closed on that basis. The second pass's verification and brief
follow unchanged, because a merge that keeps one of two answers is what
`PL-N1JK` recorded, and its "Done when" is compared against what landed
where the two differ.

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
