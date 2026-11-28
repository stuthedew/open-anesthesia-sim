---
id: PL-PN2C
title: Concentration legend boxes have names that do not contain the label each one shows
priority: P3
effort: S
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_chart.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it: each box shows its words and its checked state, and only its spoken name differs from them (triage 2026-11-28)
added: 2026-11-28
filed-pr: 2358
payoff: a speech-input user can say a legend box's shown words to click it, and a screen-reader user hears the words the box shows
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

**Why it matters.** A speech-input user clicks a control by saying the words it shows, and a screen-reader user hears its name. Understanding SC 2.5.3 (Label in Name, Level A; https://www.w3.org/WAI/WCAG22/Understanding/label-in-name, read 2026-11-28) says a mismatch makes the spoken command fail, and gives a text-to-speech user words that differ from the ones on screen. Its advice is "Where practical, make the control's text label and name match".

**Generator check.** Three items filed on 2026-11-28 share one cause: text a screen reader is told was written apart from the words the screen shows, and nothing compared the two. They are `PL-596J` (the band's line left out the legend's qualifier), `PL-MP1X` (the descriptions left out a preview's drawn label) and this item. The first two now build their lines from the words the chart draws. This item names each box by its own words, and adds a check over every button and box shown in each shipped Workspace that its name starts with the words it shows, so a later control cannot repeat the fault unseen. No head is filed, because these fixes remove the second copy in each place.

**Done when** each box's name starts with the words the box shows, a test
writes out the expected name for at least three compartments by hand, and
`docs/INTERFACE.md` names that test.
