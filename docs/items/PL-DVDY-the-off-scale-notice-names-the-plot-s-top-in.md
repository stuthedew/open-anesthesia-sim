---
id: PL-DVDY
title: The off-scale notice names the plot's top in MAC only (dashboard_frame.py OFF_SCALE_NOTICE_TEMPLATE via format_mac_multiple), so once the ceiling is reader-chosen it should name the top in both axis units, percent and MAC, as the axis labels do (PL-V67Q's design round)
priority: P3
effort: S
status: done
classes: ux
feature: chart-readout
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py, docs/INTERFACE.md
added: 2026-10-03
closed: 2026-11-22
pr: 2270
payoff: a reader working in percent learns where the plot stops without converting a MAC figure
tests: tests/unit/test_dashboard_frame.py::test_a_trace_above_the_standard_top_is_inside_the_high_top_and_above_the_low_one
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

**Checked 2026-11-22** against `d4e8200`: still applies. The off-scale notice in `app/dashboard_frame.py` still builds `top` with `format_mac_multiple` alone. `PL-K1VH` (the reader-chosen axis ceiling), which this item may ride, is still `ready` and unbuilt.

**Done 2026-11-22**, in `PL-K1VH`'s pull request. The off-scale notice names the plot's top in both units, percent first and the MAC multiple after it, as the two axes are labelled: "The axis stops at 5.40% (3.00 ×MAC)". `off_scale_lines` in `app/dashboard_frame.py` builds it from the frame the View drew, so it names the top the reader chose. `test_a_trace_above_the_standard_top_is_inside_the_high_top_and_above_the_low_one` in `tests/unit/test_dashboard_frame.py` checks the wording at the low top and that the high top gives no notice; the existing notice tests now expect both units.

Docs checked: `docs/INTERFACE.md` (the off-scale paragraph of § "The chart's fixed MAC axis", which now says the notice names the top in both units), `docs/MODEL.md` and `docs/VERIFICATION.md` (no statement of the notice's wording).
