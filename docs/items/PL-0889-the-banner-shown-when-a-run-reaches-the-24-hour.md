---
id: PL-0889
title: The banner shown when a run reaches the 24-hour supported run length is drawn in bold WARNING, the interface's one failure colour, though the status word above it is MUTED and app/theme.py says that boundary must not be coloured as a fault
priority: P3
effort: S
status: ready
classes: ux
feature: supported-run-length-text
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tools/contrast_check.py, tests/integration/test_simulation_view.py
added: 2026-10-25
payoff: a correct stop at the supported run length no longer looks like a fault, so the interface's one warning colour keeps meaning a real failure
verify: grep -q 'def test_the_supported_limit_banner_is_not_drawn_in_the_failure_colour' tests/integration/test_simulation_view.py
---

**Problem.** `NoticeLabel` sets `foreground_stylesheet(WARNING)` once, in its
constructor (`app/qt_widgets.py`). `set_notice` changes only the text
and visibility. So the supported-run-length banner is bold WARNING text, the
same as "Simulation stopped — <error>". The status word for the same state is
MUTED (`status_word` in `app/dashboard_frame.py`). The comment above
`WARNING` in `app/theme.py` says the boundary
is shown in MUTED because colouring a correct model's boundary as a fault
"would teach a reader to distrust a number that is sound".

**Why it matters.** A learner sees a correct stop styled as a fault, directly
under a status word that says it is not one. That spends the interface's one
warning signal. A new colour pairing would need its contrast requirement in
`tools/contrast_check.py`.

**Done when.** The supported-run-length banner is drawn in MUTED, or another colour that does not mark a fault, while the failure banner stays WARNING. Any new colour pairing is declared in `tools/contrast_check.py`. `tests/integration/test_simulation_view.py` has `test_the_supported_limit_banner_is_not_drawn_in_the_failure_colour`.

**Found by.** `PL-TBQS` reviewer replay on #421, finding r04 F1 (written
against the Flet `_notice_text`; the Qt port carries the same behaviour).
Checked against main on 2026-10-25 by reading the code.

**Generator check.** A one-off. The banner's colour is fixed once in `NoticeLabel`'s constructor, and the item touches `tools/contrast_check.py` only to declare any colour pairing the fix adds.
