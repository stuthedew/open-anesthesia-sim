---
id: PL-96MX
title: The approved on-screen wording test leaves out what a screen reader hears from each chart and diagram, their names and long descriptions, so a change of that wording passes it unread
priority: P3
effort: S
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_interface_wording.py, tests/integration/approved_interface_strings.json
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; each description has its own tests and only the hand check of a later change is missing, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
payoff: a change to what a screen reader hears from a chart, a diagram or a control is read by hand before it merges, as on-screen wording is
---

**Problem.** `tests/integration/test_interface_wording.py` holds every string the dashboard shows to a list checked by hand (`approved_interface_strings.json`). It reads them through `SimulationView.interface_strings`, which collects each widget's shown text and a button's accessible name. It does not collect what a screen reader is told by an accessible interface: the name and long description of the concentration chart (`PL-T9RB`), of the wash-in plot and of each run's schematic (`PL-R1M6`), nor a selector's or a label's accessible name. A change to any of those sentences passes the wording test without anyone reading it.

**Why it matters.** Each of these sentences states clinical values in words, such as "Modelled sevoflurane at 10m: Circuit (inspired) 1.45%, 0.81 ×MAC", and says that they are modelled. A screen-reader user reads them in place of the picture, so a wrong label or a dropped "Modelled" there is the same presentation fault as on screen (`CLAUDE.md` § "Safety-critical clinical-output standard"). I suggest P3, because each sentence has its own tests and only the hand check of a later change is missing.

**Approach.** Have `SimulationView.interface_strings` also yield, for each widget, the name and description its accessible interface returns where they differ from the widget's shown text, split into lines as the descriptions are written. Then rerun the wording test, read the new strings and add them to the approved list.

**Done when.** The approved list holds the charts' and the schematic's names and description lines, and a test shows that a changed description line fails the wording test.

**How it was found.** Building `PL-R1M6`, 2026-11-28: its new descriptions passed the wording test without changing the approved list.

**Generator check.** No head states the fact misread here, which is which strings the wording test reads. `SimulationView.interface_strings` collects shown text and a button's accessible name, so a string given only to assistive technology is outside it. This is the first item to name the gap.
