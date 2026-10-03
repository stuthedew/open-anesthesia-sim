---
id: PL-TS7L
title: bin/docket new's near-duplicate search skips every open item that declares no touches, so two untriaged captures of one defect never meet: PL-YZ17 was filed 2026-10-03 into a store already holding PL-5F76, the same 4.8e-304 s step overflow
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/duplicates.py, subprojects/docket/tests/test_duplicates.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: two captures of one defect filed the same day meet at the second capture, before either is triaged or built twice
verify: grep -q 'def test_an_untriaged_item_without_touches_is_a_candidate' subprojects/docket/tests/test_duplicates.py
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

**Why it matters.** A same-day duplicate costs a triage pass and can cost a
build: `PL-YZ17` was fixed on its own branch while `PL-5F76` sat untriaged
beside it, and the triage that found the pair had to split `PL-5F76` by hand.
Same-day captures are where duplicates cluster, and they are the ones this
search cannot pair.

**Done when.** A capture sharing `feature:` with an untriaged item that
declares no `touches`, under a near title, is shown that item, and a test pins
it on the `PL-5F76`/`PL-YZ17` pair.

**Generator check.** An instance of `PL-TZ7T`'s fact, filed after that head
closed on 2026-09-20: whether an open item already describes the mechanism a
new capture names. The second post-close instance, after `PL-9VPH` (the
capture side, filed 2026-09-23), so one short of the three that read as a fix
that did not hold.
