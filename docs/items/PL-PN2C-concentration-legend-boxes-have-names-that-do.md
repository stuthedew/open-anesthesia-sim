---
id: PL-PN2C
title: Concentration legend boxes have names that do not contain the label each one shows
status: untriaged
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_chart.py
added: 2026-11-28
filed-pr: 2358
---

**Problem.** Each compartment's box in the concentration chart's legend shows
its legend words, such as "Alveolar (solid)", from `trace_legend_label` in
`app/dashboard_frame.py`. A screen reader calls the same box "Draw the
Alveolar compartment on the chart", from `TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE`.
The name does not start with the words shown, and does not contain them. Every
other named control here starts its name with the label it shows, which
`docs/INTERFACE.md` applies as WCAG 2.2 SC 2.5.3 ("Label in Name").

The adversarial review of `PL-XV64` found this on 2026-11-28. It is older than
that item: the template is on `main` unchanged, and `PL-XV64` only adds the
Area's name after it.

**Done when** each box's name starts with the words the box shows, a test
writes out the expected name for at least three compartments by hand, and
`docs/INTERFACE.md` names that test.
