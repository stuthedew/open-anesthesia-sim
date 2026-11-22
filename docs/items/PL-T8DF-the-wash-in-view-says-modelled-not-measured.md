---
id: PL-T8DF
title: The wash-in View says 'Modelled, not measured' where every other View says 'Model outputs — not measurements.' for the same fact, and the line sits on the page background outside the View's panel
priority: P3
effort: S
status: ready
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/simulation_view/test_simulation_view_whole_interface.py, tests/integration/simulation_view/test_simulation_view_page.py, tests/integration/approved_interface_strings.json
added: 2026-11-22
payoff: the wash-in View states that its values are modelled in the same words and place as every other View
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
