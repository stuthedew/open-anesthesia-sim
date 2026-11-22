---
id: PL-T8DF
title: The wash-in View says 'Modelled, not measured' where every other View says 'Model outputs — not measurements.' for the same fact, and the line sits on the page background outside the View's panel
priority: P3
effort: S
status: done
classes: ux
feature: interface-design-review
milestone: v0.6.19
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/simulation_view/test_simulation_view_whole_interface.py, tests/integration/simulation_view/test_simulation_view_page.py, tests/integration/approved_interface_strings.json
added: 2026-11-22
closed: 2026-11-22
pr: 2206
payoff: the wash-in View states that its values are modelled in the same words and place as every other View
tests: tests/integration/simulation_view/test_simulation_view_whole_interface.py::test_the_wash_in_view_says_it_is_modelled_on_its_own_panel
---

**Problem.** The wash-in View says 'Modelled, not measured' where every other View says 'Model outputs — not measurements.' for the same fact, and the line sits on the page background outside the View's panel

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees.** The readouts, the compartment schematic and the agent
cost View each say "Model outputs — not measurements." inside their panel. The
wash-in View says "Modelled, not measured", on the grey page background between
its Area header and its panel, with no left margin to match the panel's text
(`view-wash_in-1366x768.png`).

**Why it matters.** One fact in two wordings invites a reader to wonder whether
they mean different things. The project's design rule is one home for one
fact, and `INTERPRETATION_DISCLAIMER_TEXT` is already that home. The line is
required by the safety standard, so it should read as part of the View it
qualifies, not as loose text between two Areas.

**What to do.** Show `INTERPRETATION_DISCLAIMER_TEXT` in the wash-in View's
pinned row, and draw the row on the panel surface with the panel's padding.
Keep the row pinned above the View's scroll box, as `PL-26BZ` built it, so
the words stay on screen wherever any part of the plot is. Delete
`WASH_IN_MODELLED_TEXT`.

**Done when.** The wash-in View's pinned row reads `INTERPRETATION_DISCLAIMER_TEXT`,
`WASH_IN_MODELLED_TEXT` no longer exists, and a test finds the row painted on
the panel colour.

**Reproduced 2026-11-22** on `a7eb53f`, offscreen: `view-wash_in-1366x768.png` shows the line on the page background.

**Generator check.** One fact with two homes: `WASH_IN_MODELLED_TEXT` was written beside `INTERPRETATION_DISCLAIMER_TEXT` for the same statement (`PL-F9TQ`). No other copy of the statement exists, so this is a one-off.

**Built 2026-11-22.** The pinned row holds a `modelled_label` reading `INTERPRETATION_DISCLAIMER_TEXT`, on a `_panel_row` with the panel's surface and padding. `WASH_IN_MODELLED_TEXT` is deleted, and the approved wording list loses its five copies of the old string.

**Regression run.** The new test, run against the code before the fix with the old `pinned_row` label in place of `modelled_label`, failed with `assert 'Modelled, not measured' == 'Model outputs — not measurements.'`.

**Docs swept 2026-11-22.** `docs/INTERFACE.md`, `docs/ARCHITECTURE.md` and `README.md`, searched for the changed wording and for the element's look; none states it, so none changed.
