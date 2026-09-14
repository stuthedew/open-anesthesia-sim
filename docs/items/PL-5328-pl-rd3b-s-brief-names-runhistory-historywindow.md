---
id: PL-5328
title: PL-RD3B's brief names RunHistory, HistoryWindow and SimulationHistorySample, which PL-2FM6 deleted, and the test file its Done when rests on no longer exists
status: untriaged
added: 2026-09-14
---

**Problem.** PL-RD3B's brief names RunHistory, HistoryWindow and SimulationHistorySample, which PL-2FM6 deleted, and the test file its Done when rests on no longer exists

**Found 2026-09-14, mapping v0.5.0's open Required scope after Gate 1 cleared.**
`PL-RD3B` is one of its eleven open entries, is `ready`, and ranks third in
`bin/docket next`, so a session is being offered it now.

**What the brief says, and what the tree holds.** Its **Where** is
"`RecordedQuantity`, `RunHistory` and `HistoryWindow` out to
`src/anesthesia_sim/app/run_history.py`, with `SimulationHistorySample` moving
with them". Measured on `a002f91`:

| Named by the brief | In the tree |
| --- | --- |
| `RunHistory` | absent |
| `HistoryWindow` | absent |
| `SimulationHistorySample` | absent |
| `RecordedQuantity` | present, `app/controller.py:126` |
| `tests/unit/test_run_history.py` | absent |

`PL-2FM6` deleted the store: `app/controller.py:230` now holds `DrawnWindow`,
whose own docstring says "It replaces `HistoryWindow`". So three of the four
symbols the move was to move are gone, and the test file the **Done when**
rests on - "the existing tests pass unmodified except for their imports" -
does not exist to pass.

**Why it matters.** This is `PL-LKGL`'s shape exactly: an item whose problem
was solved another way reads as outstanding work, and here it does so from
inside a milestone's Required scope, where `ROADMAP.md` describes it as "The
controller's storage and its UI-to-core boundary are separated ... Two runs
need the boundary without a second copy of the storage." The boundary argument
may well still hold - `app/controller.py` is 1 064 lines, up from the 930 the
brief complains about - but what is left to extract is `RecordedQuantity`,
`COMPARTMENT_STATE_INDEX` and `DrawnWindow`, which is a different change from
the one the brief specifies and may be a different size.

**Where.** `docs/items/PL-RD3B-*.md` - its **Problem**, **Why it matters**,
**Where**, **Done when** and `touches`, which names two paths that do not
exist. `ROADMAP.md` § "v0.5.0 - the case you can branch" → "Required scope"
may need its bullet re-worded with it.

**Done when.** `PL-RD3B` describes the extraction that is actually available
against the current tree, or is dropped with a reason if the boundary argument
no longer survives `PL-2FM6`; either way no symbol it names is one the tree
does not hold, and its `touches` resolves.
