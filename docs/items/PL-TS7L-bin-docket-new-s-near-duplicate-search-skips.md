---
id: PL-TS7L
title: bin/docket new's near-duplicate search skips every open item that declares no touches, so two untriaged captures of one defect never meet: PL-YZ17 was filed 2026-10-03 into a store already holding PL-5F76, the same 4.8e-304 s step overflow
status: untriaged
touches: subprojects/docket/src/docket/duplicates.py, subprojects/docket/tests/test_duplicates.py
added: 2026-10-03
---

**Problem.** bin/docket new's near-duplicate search skips every open item that declares no touches, so two untriaged captures of one defect never meet: PL-YZ17 was filed 2026-10-03 into a store already holding PL-5F76, the same 4.8e-304 s step overflow

**Measured 2026-10-03.** `duplicates.near_duplicates` skips every candidate
whose `touches` is empty (`if item.status in CLOSED_STATUSES or not
item.touches`), and capture leaves `touches` unset on most items until triage.
So two untriaged captures of one defect cannot meet, whatever paths the second
one declares or infers. The instance: `PL-5F76` reached `main` in #1292's
squash at 18:33 UTC; `PL-8H2R`'s branch was cut from `1d9e406a` (19:25 UTC),
whose store holds `PL-5F76`; `PL-YZ17` was filed on that branch at 19:46 UTC
(`43dac150`) naming the same overflow - below about 4.8e-304 s, 86 400 s over
the step is `inf` and `math.floor` raises `OverflowError`. Neither declares
`touches`; both declare `feature: numerical-domain`, and both titles open on
"A simulation step below about 4.8e-304 s".

**Not covered by.** `PL-9VPH` is the capture side: a capture with no paths
never runs the search. This is the candidate side: a capture with paths still
cannot meet an item without them. `PL-TZ7T`'s measurement (9 of 13 known pairs
share a declared path) was taken over triaged items, so it says nothing about
untriaged ones, where same-day duplicates sit.

**Carry to triage.** `PL-5F76`'s step half is `PL-YZ17`'s, which pull request
1306 is fixing; its count half (`step_count=10**5000` failing with
`ValueError` at Python's 4,300-digit int-to-str limit) is its own.

**Candidate fix.** Where either side declares no `touches`, select by a shared
`feature:` and rank by title as now. Measure it on the 13 known pairs and this
one before choosing.

**Done when.** A capture sharing `feature:` with an untriaged item that
declares no `touches`, under a near title, is shown that item, and a test pins
it on the `PL-5F76`/`PL-YZ17` pair.
