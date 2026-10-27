---
id: PL-WRVX
title: mac_awake_band_percent checks only that the band's lower edge is positive, so a negative standard deviation returns the band upper edge first, an infinite fraction returns (inf, inf), and a band reaching past 1 MAC is accepted, though its docstring promises lower first and a refusal of an undrawable band
priority: P3
effort: S
status: done
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/app/formatting.py, tests/unit/test_formatting.py, src/anesthesia_sim/core/parameters.py, tests/unit/test_parameters.py
added: 2026-10-25
closed: 2026-10-27
pr: 1882
payoff: the function the band's safety tests target keeps the promise in its docstring, so an inverted or infinite band cannot be drawn if bad data ever reaches it
verify: grep -q 'def test_mac_awake_band_percent_refuses_an_inverted_infinite_or_over_one_mac_band' tests/unit/test_formatting.py
---

**Problem.** `mac_awake_band_percent` (`src/anesthesia_sim/app/formatting.py`) rejects only `fraction - sd <= 0`. `MacMultiple` is a `NewType` and checks nothing. Reproduced on main: an SD of -0.05 returns (0.78, 0.58), a fraction of `inf` returns (inf, inf), and 0.9 ± 0.2 at a 2.0% MAC returns (1.4, 2.2), past the 1 MAC line. The loader's `_MacAwakePayload` stops these from shipped data, so no reader sees them today.

**Why it matters.** This pure function is the one the band's safety tests target, and its docstring says it refuses a band it cannot draw. An inverted band draws with no fill and a label reading "0.78–0.58%". The fix is either to take the parsed `MacAwakeReference`, or to check `0 < lower < upper < mac_percent` and finiteness in the function itself.

**Done when.** `mac_awake_band_percent` refuses a band whose edges are not finite or not ordered as 0 < lower < upper < `mac_percent`, or takes the parsed `MacAwakeReference` so no such band can reach it. `tests/unit/test_formatting.py` has `test_mac_awake_band_percent_refuses_an_inverted_infinite_or_over_one_mac_band`, covering the three calls in the brief.

**Found by.** `PL-TBQS` reviewer replay on #288, finding r01 F3. Checked against main on 2026-10-25 with the three calls above.

**Built (2026-10-27).** The rule now lives in one function,
`mac_awake_band_fractions` in `core/parameters.py`, which returns the band's
edges as fractions of MAC or refuses the band. It refuses a fraction or
standard deviation that is not finite, a lower edge at or below zero, an upper
edge not above the lower edge, and an upper edge at or above 1 MAC. Both the
loader's `_MacAwakePayload` and `mac_awake_band_percent` call it. A first
version checked the band in `app/formatting.py` alone. The blind review found
that this copied the loader's rule, and that the copies already disagreed: the
loader accepted a standard deviation of 1e-17, whose two edges are the same
double, and the chart then refused it. The loader now refuses that file too,
which `test_rejects_a_mac_awake_band_whose_edges_coincide` pins. Each new
refusal's whole sentence is pinned in
`test_each_display_refusal_a_halt_can_show_is_pinned_whole`.
