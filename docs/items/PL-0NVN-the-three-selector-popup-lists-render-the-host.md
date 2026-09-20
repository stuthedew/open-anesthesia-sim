---
id: PL-0NVN
title: The three selector popup lists render the host's surface, because a stylesheet on a combo box resets its popup's palette to the application's
priority: P2
effort: S
status: done
classes: defect, ux
feature: platform-palette
milestone: v0.4.34
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/test_dark_appearance.py
added: 2026-09-20
closed: 2026-09-20
pr: 762
payoff: the three lists a reader picks an agent, a time base and a playback rate from draw the interface's surface rather than the host's
verify: grep -q 'def test_a_selector_popup_draws_the_theme_rather_than_the_host_palette' tests/integration/test_dark_appearance.py
---

**Problem.** The three selector popup lists render the host's surface, because a stylesheet on a combo box resets its popup's palette to the application's

**Why it matters.** The agent selector, the time-base selector and the
playback-rate selector each declare their closed surface in a stylesheet -
`selector_stylesheet` for two of them, `_selector_stylesheet` in the running
agent's ISO 5360 pair for the third. A stylesheet on a widget makes its
children resolve from the *application* palette rather than from the widget, so
each selector's popup `QListView` draws the host's surface: measured
`Base #1e1e1e` with `Text #ffffff` on 2026-09-20 by walking the rendered widget
tree under a dark host palette.

White on near-black is legible, so nothing here is unreadable today. What is
wrong is which surface it is: these are the lists a reader picks an agent, a
time base and a playback rate from, and `docs/MODEL.md` requires the last two
to be displayed (`PL-SN2C`). `tools/contrast_check.py` measures `INK` on
`PANEL` for the selectors' text because that is what the stylesheet declares;
the popup is drawn in a pair it does not measure and cannot see.

**Not an agent-identity change.** The popup lists all three agents and carries
no agent colour. `_apply_agent_color_scheme` stays the single writer of agent
colour that `tools/agent_identity_check.py` reads the identity set off; a
palette is not one of the colours it governs.

**Done when.** The three selectors' popup views declare the interface's
palette, and a test holds them under a dark host palette.
