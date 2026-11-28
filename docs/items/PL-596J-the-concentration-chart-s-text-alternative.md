---
id: PL-596J
title: The concentration chart's text alternative gives the MAC-awake band without the legend's words population, read against vessel-rich group trace, so a screen-reader user is not told which trace the band is read against
status: untriaged
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_chart_frame.py, tests/integration/approved_interface_strings.json
added: 2026-11-28
filed-pr: 2360
---

**Problem.** The concentration chart's legend labels the MAC-awake band "MAC-awake sevoflurane = 0.34 ×MAC (0.61%), band ±1 SD 0.52–0.70%; population, read against vessel-rich group trace" (`dashboard_frame.MAC_AWAKE_BAND_LEGEND_TEMPLATE`, drawn by `qt_chart`). The chart's text alternative, which a screen reader reads in place of the picture, ends with the same reference but without "; population, read against vessel-rich group trace", because `dashboard_frame.concentration_chart_description` takes `mac_awake_caption(frame)` alone. Before the band, the description gives each run's value on every trace shown, the alveolar (end-tidal-equivalent) value among them, and then the 1 MAC line.

**Why it matters.** `docs/INTERFACE.md` § "MAC-awake as a chart reference" says to read the band against the vessel-rich trace, and names reading it against the alveolar trace as the first of three misreadings that make emergence look faster than the model says. The legend's words are how the screen prevents that misreading. A screen-reader user hears the band after the run's values, with nothing to say that it is a population reference or which trace it belongs against. That is a wrong-context reading of a clinical reference, which `CLAUDE.md` § "Safety-critical clinical-output standard" treats as a presentation fault. I suggest P2.

**Approach.** Build the description's MAC-awake line from `MAC_AWAKE_BAND_LEGEND_TEMPLATE`, as the legend is built, so the two cannot differ again. Update the unit tests of the description in `tests/unit/test_chart_frame.py`, and rewrite the approved wording list. The added words are the legend's own, which the screen already shows, so the change adds no new clinical wording.

**Done when.** A test shows that the description's MAC-awake line is the legend's text, with "population, read against vessel-rich group trace".

**How it was found.** The first blind review of `PL-96MX`, 2026-11-28, read the approved strings it adds and found the description's line shorter than the legend's.

**Generator check.** No head states the fact misread here, which is that a text alternative must carry each qualifier its picture's labels carry. `PL-T9RB` built the description from the reference's caption rather than from the legend's text, and this is the first item to name it.
