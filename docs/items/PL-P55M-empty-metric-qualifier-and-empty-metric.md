---
id: PL-P55M
title: EMPTY_METRIC_QUALIFIER and EMPTY_METRIC_SECONDARY_VALUE hold a no-break space for a Flet layout fact Qt does not share: under PySide6 6.11.2 an empty label is as tall as one holding U+00A0 (found closing PL-TMSN)
priority: P3
effort: S
status: ready
classes: refactor
touches: src/anesthesia_sim/app/dashboard_frame.py, tools/glyph_check.py, tests/unit/test_dashboard_frame.py, tests/integration/test_qt_widgets.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
payoff: The readout row's shared baseline is held by a test of its height instead of by an invisible character kept for a framework the app no longer uses
verify: grep -q 'def test_an_empty_gloss_line_is_as_tall_as_a_filled_one' tests/integration/test_qt_widgets.py
---

**Problem.** EMPTY_METRIC_QUALIFIER and EMPTY_METRIC_SECONDARY_VALUE hold a no-break space for a Flet layout fact Qt does not share: under PySide6 6.11.2 an empty label is as tall as one holding U+00A0 (found closing PL-TMSN)

Measured 2026-10-18 under the offscreen platform with the container's Inter:
`styled_label("")` and `styled_label("\xa0")` both report 15 px at
`METRIC_QUALIFIER_SIZE` (italic) and 16 px at `METRIC_SECONDARY_VALUE_SIZE`.
The comment above the two constants in `app/dashboard_frame.py` keeps the
character partly because `tools/glyph_check.py` cites them as its evidence,
which is circular now that the reason is gone. Whether to swap in an empty
string is a choice, so it is an item: it touches the readout row, and a test
asserts the line holds a value. Not checked on the owner's own font.

**Why it matters.** The comment gives a reason that no longer holds, and
`tools/glyph_check.py` cites these two constants as its evidence for U+00A0.
That evidence is circular. A reader cannot tell whether the character is needed.

**Done when.** The two constants hold `""`. A test in
`tests/integration/test_qt_widgets.py` shows that a readout with an empty gloss
line is as tall as one with a gloss, so the row's shared baseline is pinned by
a measurement instead of by a character. `tools/glyph_check.py` no longer cites
the constants, and `tests/unit/test_dashboard_frame.py` no longer asserts the
U+00A0 value. Look and placement are the session's to choose for now, so this
is decided here rather than put to the owner.

**Generator check.** A leftover of the Flet-to-Qt port (`qt-port`, complete).
No fact here is misread by other items, so it is a one-off.
