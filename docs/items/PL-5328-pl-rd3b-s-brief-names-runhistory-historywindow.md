---
id: PL-5328
title: PL-RD3B's brief names RunHistory, HistoryWindow and SimulationHistorySample, which PL-2FM6 deleted, and the test file its Done when rests on no longer exists
status: done
priority: P2
effort: S
classes: defect, docs
feature: queue-hygiene
touches: docs/items, ROADMAP.md
added: 2026-09-14
closed: 2026-09-14
verify: python3 tools/doc_check.py check && grep -qF 'Re-briefed 2026-09-14 under' docs/items/PL-RD3B-app-controller-py-holds-the-run-s-trace.md
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

**Resolved 2026-09-14: re-briefed, not dropped.** The project owner's call was
to decide between the two; the measurement says the item is real, so its brief
was rewritten against `9744d39` rather than the item retired.

**Why re-brief.** `PL-RD3B`'s *premise* survived `PL-2FM6` intact - only its
symbol list died. The premise is that the seam is a fact about the imports
rather than one the item invents, and that is still measurably true: of the
four modules importing `app/controller.py`, `app/chart_series.py` takes
`DrawnWindow` and `RecordedSeries` and nothing else, `app/control_timeline.py`
takes `ControlChange` and `ControlInput` and nothing else, and `app/main.py`
takes `SimulationController` and nothing else. Only `app/simulation_view.py`
wants the whole module. The file is also *larger* than when the item was
filed - 1 064 lines against the 930 its original complained about - of which
the controller proper is the last 564.

**What the re-brief corrected, beyond what this item reported.** Three further
staleness defects were in the same brief and are fixed with it:

- the three queue items it cited as its reasons - `PL-011`, `PL-WRKL` and
  `PL-RRWV` - are all `dropped`. They are replaced by the live instances:
  v0.5.0's `PL-J2TD`, `PL-TFX5`, `PL-Z3W6` and `PL-8PSW`, all of which operate
  on the extracted half, and `PL-CNCF`, a `perf` item on `drawn_window` itself;
- it placed the package map in `docs/MODEL.md`. The map is the tree in
  `docs/ARCHITECTURE.md`, which `tools/doc_check.py`'s `check_package_maps`
  holds to the files on disk in both directions;
- its `verify:` command ran `tests/unit/test_run_history.py`, a file that does
  not exist, so it could never have passed. The replacement pairs the two
  consumer test files with a grep asserting `app/chart_series.py` no longer
  imports from `app/controller.py` - run before the work and exits 1, for the
  grep rather than for a selector that matched nothing.

**The title was wrong too, and it is what a session reads first.** It said the
controller "now holds the run's storage"; there is no storage. Retitled, and
the file renamed with `git mv` to the slug `docket` generates. `ROADMAP.md`
carried the same stale noun twice - the Gate 1 entry under "Cleared by v0.5.0
itself" quotes the title, and v0.5.0's Required-scope bullet read "without a
second copy of the storage" - and both are corrected, with the scope itself
unchanged. Neither is held to the store by a check: `check_gate_counts` checks
counts and `check_gate_reentries` reads `classes`, so nothing would have caught
either.

**Not blocked on `PL-B9PY`, deliberately.** It is in flight in the one importer
that takes the whole module, so it lands first and `PL-RD3B` resolves against
it - but a shared file is a sequencing note rather than a refusal, which is
`PL-VRMK`'s refuted approach, so the item stays `ready` and the note is in its
brief instead.

**Captured, not fixed:** `PL-27H0` - `docs/MODEL.md` § "What a recorded sample
is" still specifies the per-step sample store and a display operation that
selects among recorded samples, both of which `PL-2FM6` deleted. Outside this
item's `touches`, and an edit to the authoritative model specification wants
its own doc sweep.
