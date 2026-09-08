---
id: PL-C92D
title: PL-YSZN's Flet frame table predates PL-2FM6 and measures a tree that no longer exists in two of its three stages, so the Qt/Flet comparison rests on one row
status: untriaged
added: 2026-09-08
---

**Problem.** PL-YSZN's Flet frame table predates PL-2FM6 and measures a tree that no longer exists in two of its three stages, so the Qt/Flet comparison rests on one row

**Where it came from.** `PL-55DH` built the Qt spike and instrumented it in
`PL-YSZN`'s three-stage split, so that `PL-X9T3`'s numbers would be
"comparable rather than merely favourable". Setting the two tables beside each
other showed that two of the three stages are not comparable at all.

**What changed underneath.** `PL-YSZN` measured on 2026-09-08, before
`PL-2FM6` merged the same day. Its `controller.advance` included recording a
sample into `RunHistory` on every step, and its `_refresh_view` included a
binary search over recorded samples plus M4 selection. Neither exists now:
the run keeps no history, and the chart's read is a closed-form evaluation of
the score. Measured on the spike, at the shipped 150-column budget:

| Stage | Flet, `PL-YSZN` 300x | Qt, `PL-55DH` 300x |
| --- | ---: | ---: |
| `advance` | 26.2 ms | 8.7 ms |
| `_refresh_view` / `refresh` | 4.6 ms | 6.2 ms |
| `page.update` / `handoff` | 45.5 ms | 1.2 ms |

The third row is a toolkit comparison. The first two are an architecture
comparison wearing a toolkit's clothes: `advance` fell threefold because the
history recording went, not because of Qt, and `refresh` rose because the
chart's read moved from selecting recorded samples to evaluating the score.

**Why it matters.** `PL-QXSB` is a decision about whether to leave Flet, and
`PL-X9T3` is the measurement it turns on. Both would be read against
`PL-YSZN`'s table, and two thirds of that table now describes a tree that no
longer exists. The headline - that handing a frame to the toolkit costs 1 ms
against 26-45 ms - survives untouched, which is why this is a `P2` correction
rather than something that changes the answer. What does not survive is any
statement of the *whole frame's* cost on either side.

**Done when** `PL-YSZN`'s frame table is re-taken on the post-`PL-2FM6` tree,
with the same harness (`tests/integration/test_chart_patching.py`'s real Flet
session), and the note in `docs/WORKING_NOTES.md` under "Built and measured:
the Qt spike runs" carries the corrected comparison. The three-stage split
stays; only the numbers change.
