---
id: PL-T8DF
title: The wash-in View says 'Modelled, not measured' where every other View says 'Model outputs — not measurements.' for the same fact, and the line sits on the page background outside the View's panel
status: untriaged
feature: interface-design-review
added: 2026-11-22
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
