---
id: PL-P55M
title: EMPTY_METRIC_QUALIFIER and EMPTY_METRIC_SECONDARY_VALUE hold a no-break space for a Flet layout fact Qt does not share: under PySide6 6.11.2 an empty label is as tall as one holding U+00A0 (found closing PL-TMSN)
status: untriaged
added: 2026-10-18
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
