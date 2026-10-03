---
id: PL-DVDY
title: The off-scale notice names the plot's top in MAC only (dashboard_frame.py OFF_SCALE_NOTICE_TEMPLATE via format_mac_multiple), so once the ceiling is reader-chosen it should name the top in both axis units, percent and MAC, as the axis labels do (PL-V67Q's design round)
status: untriaged
feature: chart-readout
added: 2026-10-03
---

**Problem.** The off-scale notice names the plot's top in MAC only (dashboard_frame.py OFF_SCALE_NOTICE_TEMPLATE via format_mac_multiple), so once the ceiling is reader-chosen it should name the top in both axis units, percent and MAC, as the axis labels do (PL-V67Q's design round)

**From `PL-V67Q`'s design round, 2026-10-03.** `OFF_SCALE_NOTICE_TEMPLATE` is formatted at `dashboard_frame.py:1923-1925` with `top=format_mac_multiple(...)`, so the notice says where the axis stops in MAC alone while the axis itself is labelled in percent and MAC. Once `PL-K1VH` lets a reader choose the ceiling, the notice should name the top in both units so a reader working in percent is not handed a MAC figure to convert. Small; rides `PL-K1VH`'s pull request or follows it.
