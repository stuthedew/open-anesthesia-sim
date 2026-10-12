---
id: PL-0HLS
title: PL-TZ7T's mechanism is producing again: four captures filed since it closed on 2026-09-20 fell through gaps in its one key, a shared declared touches path - stale touches after a file move (PL-6SV4), a clean-tree capture (PL-9VPH), the store directory counted as a shared path (PL-SV0D), an untriaged candidate declaring none (PL-TS7L)
priority: P1
effort: M
status: ready
classes: defect
feature: recurrence-signal
touches: subprojects/docket/src/docket/duplicates.py, subprojects/docket/tests/test_duplicates.py, .claude/skills/docket/modes/capture.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; recorded as a generator head by PL-4097, 2026-10-12
added: 2026-10-12
payoff: a capture made before triage is shown the open item that already describes it, so a defect is diagnosed once rather than twice, and three open defects in the duplicate search close in one design instead of three patches that undo each other
verify: grep -q 'def test_an_untriaged_capture_meets_an_untriaged_item' subprojects/docket/tests/test_duplicates.py
root-cause-of: PL-6SV4, PL-9VPH, PL-SV0D, PL-TS7L
generator: live - duplicates.py's key is unchanged since PL-TZ7T closed, and every untriaged candidate, clean-tree capture, stale touches path and store-directory overlap still falls outside it or matches falsely, so each duplicate a session notices is another member; the last arrived 2026-10-03
misread: Whether an open item already describes the mechanism a new capture names
reenters: PL-TZ7T
---

**Problem.** PL-TZ7T's mechanism is producing again: four captures filed since it closed on 2026-09-20 fell through gaps in its one key, a shared declared touches path - stale touches after a file move (PL-6SV4), a clean-tree capture (PL-9VPH), the store directory counted as a shared path (PL-SV0D), an untriaged candidate declaring none (PL-TS7L)

**Why it is one mechanism.** `PL-TZ7T` closed on 2026-09-20 with one key for
whether an open item already describes a capture: a shared declared `touches`
path selects, title similarity orders, and a capture declaring none takes its
paths from the working tree (`PL-THLT`). `subprojects/docket/src/docket/duplicates.py`
has not changed since (`git log`, newest `a4cc4b09`, 2026-09-20). Each member
is a place that key is absent or wrong, and each one's **Generator check.**
names `PL-TZ7T`'s fact:

- `PL-6SV4` (2026-09-22, dropped as a duplicate of `PL-VYK1`): the older item's
  `touches` still named the file its section lived in before a move.
- `PL-9VPH` (2026-09-23): a capture made on a clean tree, which `capture.md`'s
  housekeeping recipe prescribes, has no paths, so the search never runs.
- `PL-SV0D` (2026-10-01): the store directory, which every capturing branch
  changes, counts as a shared path, and recorded `PL-DHGC` as a recurrence of
  `PL-JLBD`.
- `PL-TS7L` (2026-10-03): an open item declaring no `touches` is never a
  candidate, and capture leaves `touches` unset until triage, so same-day
  duplicates (`PL-YZ17`, `PL-5F76`) never meet.

Each filing counted at most two post-close instances, one short of the three
that read as a fix that did not hold, because each found only the instances its
own path or title led to. `PL-4097` read all four from their `reenters:`
records on 2026-10-12.

**Why it matters.** A missed duplicate costs a second brief and a triage pass
to drop or split it. 16 items filed from 2026-09-21 to 2026-10-05 were dropped
as duplicates (a grep of dropped items' `reason:` for "duplicate", 2026-10-12),
some caught by the search itself and at least four filed on a sibling branch
before either merged (`PL-9RJM`, `PL-H2V3`, `PL-XQY6`, `PL-P813`). And the
members' fixes conflict if taken one at a time: `PL-9VPH`'s makes a housekeeping
capture match on `docs/items`, the one path `PL-SV0D` asks the matcher to stop
counting. So one design has to decide what the store directory is worth as a
key, and what selects where either side has no path.

**Done when.** One key design in `duplicates.py`, measured against
`PL-TZ7T`'s 13 known pairs before it is chosen, pairs each member's instance -
`PL-YZ17` with `PL-5F76` (both untriaged, no `touches`), `PL-4CPP` with
`PL-BYN2` (a clean-tree capture), `PL-6SV4` with `PL-VYK1` (stale `touches`) -
and records no recurrence where the only shared path is the store directory
(`PL-DHGC`, `PL-JLBD`), each pinned by a test in
`subprojects/docket/tests/test_duplicates.py`, the untriaged pair's as
`test_an_untriaged_capture_meets_an_untriaged_item`. The open members close
with it. The head closes `spent` with a written bound for what no key can
see - a capture on a sibling branch before either merges, a paraphrase sharing
no path - naming what reopens it, as `PL-61FT`'s bound does, so its next miss
is an item at its own rank rather than another head.

**Generator check.** A head: `PL-TZ7T`'s fact, whether an open item already
describes the mechanism a new capture names, re-entered by the four filings
above after that head closed. Recorded by `PL-4097`'s design round.
