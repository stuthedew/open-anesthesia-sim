---
id: PL-596J
title: The concentration chart's text alternative gives the MAC-awake band without the legend's words population, read against vessel-rich group trace, so a screen-reader user is not told which trace the band is read against
priority: P1
effort: S
status: done
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_chart_frame.py, tests/integration/approved_interface_strings.json, docs/INTERFACE.md, ROADMAP.md
added: 2026-11-28
closed: 2026-11-28
pr: 2361
filed-pr: 2360
payoff: a screen-reader user hears which trace the MAC-awake band is read against, as the legend tells a sighted user
tests: tests/unit/test_chart_frame.py::test_the_chart_s_text_alternative_says_which_trace_the_mac_awake_band_is_read_against, tests/unit/test_chart_frame.py::test_the_chart_s_text_alternative_gives_each_shown_trace_s_latest_value, tests/unit/test_chart_frame.py::test_the_chart_s_text_alternative_names_each_run_and_says_when_nothing_is_drawn
---

**Problem.** The concentration chart's legend labels the MAC-awake band "MAC-awake sevoflurane = 0.34 ×MAC (0.61%), band ±1 SD 0.52–0.70%; population, read against vessel-rich group trace" (`dashboard_frame.MAC_AWAKE_BAND_LEGEND_TEMPLATE`, drawn by `qt_chart`). The chart's text alternative, which a screen reader reads in place of the picture, ends with the same reference but without "; population, read against vessel-rich group trace", because `dashboard_frame.concentration_chart_description` takes `mac_awake_caption(frame)` alone. Before the band, the description gives each run's value on every trace shown, the alveolar (end-tidal-equivalent) value among them, and then the 1 MAC line.

**Why it matters.** `docs/INTERFACE.md` § "MAC-awake as a chart reference" says to read the band against the vessel-rich trace, and names reading it against the alveolar trace as the first of three misreadings that make emergence look faster than the model says. The legend's words are how the screen prevents that misreading. A screen-reader user hears the band after the run's values, with nothing to say that it is a population reference or which trace it belongs against. That is a wrong-context reading of a clinical reference, which `CLAUDE.md` § "Safety-critical clinical-output standard" treats as a presentation fault. I suggest P2.

**Approach.** Build the description's MAC-awake line from `MAC_AWAKE_BAND_LEGEND_TEMPLATE`, as the legend is built, so the two cannot differ again. Update the unit tests of the description in `tests/unit/test_chart_frame.py`, and rewrite the approved wording list. The added words are the legend's own, which the screen already shows, so the change adds no new clinical wording.

**Done when.** A test shows that the description's MAC-awake line is the legend's text, with "population, read against vessel-rich group trace".

**How it was found.** The first blind review of `PL-96MX`, 2026-11-28, read the approved strings it adds and found the description's line shorter than the legend's.

**Generator check.** No head states the fact misread here, which is that a text alternative must carry each qualifier its picture's labels carry. `PL-T9RB` built the description from the reference's caption rather than from the legend's text, and this is the first item to name it.

**Generator check.** No head states the fact misread here, which is that a text alternative names a chart reference in the same words as its legend entry. `PL-9XGQ`'s head is about each element's role and a name unique in its window, not about what a description says. The fix builds the description's two reference lines from the legend's own words, so the two cannot differ again.

**Fixed 2026-11-28.** `dashboard_frame.concentration_chart_description` now builds its last two lines from the legend's own words. The MAC-awake line is `MAC_AWAKE_BAND_LEGEND_TEMPLATE`, so it ends "; population, read against vessel-rich group trace". The 1 MAC line is `ONE_MAC_LINE_SPOKEN_TEMPLATE`, which starts with the same words as `ONE_MAC_LINE_LEGEND_TEMPLATE` and leaves out the line's style, so it reads "1 MAC sevoflurane (age 40) = 1.8%, reference adult (alveolar)". The wash-in plot's text alternative already leaves the line style out of its equilibrium line in the same way. `docs/INTERFACE.md`'s paragraph on the chart's text alternative says so, and the approved wording list holds the new lines.

**Regression check.** The new test fails on the code before the fix (`git checkout 6b55a983 -- src/anesthesia_sim/app/dashboard_frame.py`, then `pytest tests/unit/test_chart_frame.py::test_the_chart_s_text_alternative_says_which_trace_the_mac_awake_band_is_read_against`), because the band's line was "MAC-awake sevoflurane = 0.34 ×MAC (0.61%), band ±1 SD 0.52–0.70%" and did not end with "; population, read against vessel-rich group trace". The two older tests of the text alternative fail there too, at "'1 MAC sevoflurane (age 40) = 1.8%' != '1 MAC sevoflurane (age 40) = 1.8%, reference adult (alveolar)'".

**Blind review.** Two rounds of two passes ran on this branch, which closes `PL-MP1X` too. They found four things:

1. Round 1, pass 1, should-fix: neither reference line ended with a full stop, so a screen reader that reads the description as one passage ran "alveolar" straight into "MAC-awake". Fixed: each ends with one. Bohman, "Why Don't Screen Readers Always Read What's on the Screen? Part 1" (Deque, 2014, read 2026-11-28), reports that JAWS, NVDA and VoiceOver pause at a full stop, and that NVDA reads through a parenthesis without a pause.
2. Round 1, pass 2, should-fix: this item was still open in the reviewed tree, though `ROADMAP.md` says it closes in this pull request. Fixed: it closes here.
3. Round 1, pass 1, optional: `PL-MP1X` had been dropped, while a screen-reader user who drags with a pointer still heard only the drawn run. Fixed: `PL-MP1X` was reopened and is built here.
4. Round 2, pass 1 and pass 2, optional, repeated: with every compartment unchecked, the concentration chart's description left out a preview's label that the plot still draws. Fixed, with a check in the preview test.

**Documents checked.** `docs/INTERFACE.md`'s paragraphs on the concentration chart's and the wash-in plot's text alternatives, and § "A preview of an unapplied setting", which needed no change. `ROADMAP.md`'s frozen list, which this branch adds this item to. `docs/ARCHITECTURE.md`'s lines for `chart_frame.py` and `dashboard_frame.py` are still true. `docs/MODEL.md` does not describe the text alternatives.
