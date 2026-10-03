---
id: PL-DVDY
title: The off-scale notice names the plot's top in MAC only (dashboard_frame.py OFF_SCALE_NOTICE_TEMPLATE via format_mac_multiple), so once the ceiling is reader-chosen it should name the top in both axis units, percent and MAC, as the axis labels do (PL-V67Q's design round)
priority: P3
effort: S
status: ready
classes: ux
feature: chart-readout
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py
added: 2026-10-03
payoff: a reader working in percent learns where the plot stops without converting a MAC figure
verify: grep -q 'def test_off_scale_notice_names_the_top_in_both_units' tests/unit/test_dashboard_frame.py
---

**Problem.** The off-scale notice names the plot's top in MAC only (dashboard_frame.py OFF_SCALE_NOTICE_TEMPLATE via format_mac_multiple), so once the ceiling is reader-chosen it should name the top in both axis units, percent and MAC, as the axis labels do (PL-V67Q's design round)

**From `PL-V67Q`'s design round, 2026-10-03.** `OFF_SCALE_NOTICE_TEMPLATE` is formatted at `dashboard_frame.py:1923-1925` with `top=format_mac_multiple(...)`, so the notice says where the axis stops in MAC alone while the axis itself is labelled in percent and MAC. Once `PL-K1VH` lets a reader choose the ceiling, the notice should name the top in both units so a reader working in percent is not handed a MAC figure to convert. Small; rides `PL-K1VH`'s pull request or follows it.

**Checked 2026-10-03 at triage.** `dashboard_frame.py:1925` formats the notice
with `top=format_mac_multiple(...)` alone, while the axis is labelled in
percent on the left and MAC on the right.

**Why it matters.** A reader working from the percent axis is told where the
plot stops in MAC, and has to convert it to know which of their percent values
are cut off; once `PL-K1VH` lets the ceiling move, that conversion moves with
it.

**Done when.** The off-scale notice names the plot's top in both of the axis's
units, percent and MAC, and a test pins both. It may ride `PL-K1VH`'s pull
request.
