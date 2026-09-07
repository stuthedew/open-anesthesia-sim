---
id: PL-WT07
title: docs/MODEL.md says the ventilator start binds the per-rate displacement table 'throughout', but at 300x it leads the unperfused load by only 3% (10.36 vs 10.03 pp) and 'throughout' reads as a comfortable margin
priority: P1
effort: S
status: needs-decision
classes: docs, science
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-07
---

**Problem.** `docs/MODEL.md` says the ventilator start binds the per-rate
displacement table "throughout", but at 300× it leads the unperfused load by
only 3% (10.36 vs 10.03 pp) and "throughout" reads as a comfortable margin.

**Why it matters.** `docs/MODEL.md` is the authoritative specification, and this
sentence states a property of the manoeuvre rather than a measured margin. A
reader — including a later session choosing which manoeuvre to test a step-size
change against — takes it as settled that the ventilator start is the worst case
at every rate.

**It is worse than the title says, and this is the part to act on.** The
paragraph does not merely omit the margin; it quantifies the narrowing against
the *wrong* competitor. It illustrates the gap with the case opening — "about
21× milder at 1×", narrowing "to 19× at 20×, 16× at 60× and about 7× at 300×" —
so a reader is told the binding case leads its nearest rival by seven times at
the coarsest grid. The nearest rival at 300× is not the case opening. It is the
unperfused load then dial off, at 1.033×, and it is not named in the comparison
at all. The reader is given a real number, correctly measured, about the
second-nearest manoeuvre, with nothing to indicate a third one sits 3% away.

CLAUDE.md's standard asks that model limitations be visible rather than that a
confident word imply more than the measurement supports. This is that failure in
the spec rather than in the interface, and the specific harm is that the stated
margin is off by a factor of about seven in the reassuring direction.

**Found while working `PL-ZVS7`** (the gate that pins both tables), 2026-09-07.

**The measurement.** Worst displacement per grid step, desflurane binding
throughout, in percentage points:

| Manoeuvre | 1× | 5× | 20× | 60× | 300× |
| --- | --- | --- | --- | --- | --- |
| Ventilator start | 1.43e-1 | 6.95e-1 | 2.51 | 5.83 | 1.04e1 |
| Unperfused load then dial off | 5.03e-2 | 2.50e-1 | 9.79e-1 | 2.76 | 1.00e1 |

The ventilator start leads by 2.8× at 1× and by 1.033× at 300×. It is still the
binding case, so `docs/MODEL.md` is not wrong today and
`tests/reference/test_control_resolution.py`'s
`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate` passes.

**Why it is worth recording.** The two converge because they saturate at
different rates — the ventilator start's transient has largely run inside a 30 s
grid step while the unperfused load's is still going — so the crossing is a real
possibility rather than a rounding artifact, and the published 1.0e1 pp figure
would survive it while the sentence naming the manoeuvre would not.

**Where.** `docs/MODEL.md` § "Supported simulation step" (the section opens at
~962): the per-rate table at ~1074-1081 and the paragraph following it at
~1082-1092, which is where the "binding case", the "throughout" and the
case-opening ratios are stated. `tests/reference/test_control_resolution.py:481`
holds the test that would fail if the ordering reversed; no change is owed
there.

**`PL-SR8F` is this paragraph's predecessor, and it is still open.** `PL-SR8F`
(MODEL.md calls the case-opening displacement 'two orders milder') is P1
`safety` against the same sentence, and its work has landed: the phrase it
names was present through `a6da69e` (2026-09-06) and gone by `67b279b`,
`PL-ZVS7`'s own commit, which replaced it with the explicit per-rate ratios the
paragraph carries today. `bin/docket check --verify` reports `PL-SR8F` as open
with a passing command for that reason.

So this item is about the sentence `PL-SR8F`'s fix produced, not the one it
found: the ratios are now stated per rate and are correct, and what is still
wrong is *which manoeuvre* they are stated against. Close `PL-SR8F` before
starting here, or work the two together — a second edit to one paragraph from a
session that has not read the first is how a corrected figure gets re-broken.

**Decision needed.** Which of the three options below the spec takes. All three
are edits to `docs/MODEL.md` alone.

1. **State the margin in the same sentence.** Costs a clause and makes the claim
   self-dating.
2. **Publish the second row of the measured table above.** The fuller answer,
   already measured by the gate, and the only option that lets a reader see the
   convergence rather than be told about it. *Recommended for whoever answers* —
   not because the other two are wrong, but because it is the only one that also
   repairs the case-opening comparison, which is the defect with a factor of
   seven in it.
3. **Leave it**, on the grounds that the gate now fails the moment the claim
   stops being true. Note that this option does not address the paragraph
   comparing against the case opening, which is misleading today rather than on
   a future parameter revision.

**Done when.** `docs/MODEL.md` § "Supported simulation step" no longer implies a
comfortable margin where there is a 3% one — either by stating the real nearest
competitor and its margin, or by recording explicitly why it does not — and the
decision is recorded there rather than only in this item.
