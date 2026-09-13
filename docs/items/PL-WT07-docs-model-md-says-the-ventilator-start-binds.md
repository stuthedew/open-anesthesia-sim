---
id: PL-WT07
title: docs/MODEL.md says the ventilator start binds the per-rate displacement table 'throughout', but at 300x it leads the unperfused load by only 3% (10.36 vs 10.03 pp) and 'throughout' reads as a comfortable margin
priority: P1
effort: S
status: done
classes: docs, science
feature: model-spec-accuracy
touches: docs/MODEL.md, tests/reference/test_control_resolution.py
added: 2026-09-07
closed: 2026-09-13
pr: 524
verify: uv run pytest tests/reference/test_control_resolution.py -q && python3 -c "import pathlib; t=' '.join(pathlib.Path('docs/MODEL.md').read_text().split()); raise SystemExit(0 if 'Second worst | Margin' in t and 'bound over the three manoeuvres' in t else 1)"
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

**`PL-SR8F` is this paragraph's predecessor, and it closed the day this item
was filed.** `PL-SR8F` (MODEL.md calls the case-opening displacement 'two
orders milder') is P1 `safety` against the same sentence; its work landed in
`67b279b`, `PL-ZVS7`'s own commit, which replaced the phrase with the explicit
per-rate ratios, and it was marked `done` on 2026-09-07 and shipped in v0.4.8
under `#420`. The sequencing warning below is therefore discharged rather than
outstanding — checked against the store on 2026-09-13, not recalled.

So this item is about the sentence `PL-SR8F`'s fix produced, not the one it
found: the ratios are now stated per rate and are correct, and what is still
wrong is *which manoeuvre* they are stated against. Close `PL-SR8F` before
starting here, or work the two together — a second edit to one paragraph from a
session that has not read the first is how a corrected figure gets re-broken.

**Decision needed — ANSWERED 2026-09-13, see below.** Which of the three
options below the spec takes. All three were filed as edits to `docs/MODEL.md`
alone, which turned out to be wrong for the one taken.

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

## Answered 2026-09-13 (project owner): options 1 and 2 together, with a test

Not either/or. Option 2 alone would have published a second row that reads
`1.0×10¹ pp` against the first row's `1.0×10¹ pp` at 300× — the convergence
visible, the ordering unreadable, and the margin still unstated. Option 1 alone
would have stated the margin without letting a reader see where it came from.
So the section now carries both: two new columns, **Second worst** and
**Margin**, and a rewritten paragraph beneath them.

**Re-measured before anything was written, 2026-09-13.** Worst displacement per
grid step, over all three agents, in percentage points:

| Manoeuvre | 1× | 5× | 20× | 60× | 300× |
| --- | --- | --- | --- | --- | --- |
| Ventilator start | 0.143 | 0.695 | 2.508 | 5.826 | 10.33 |
| Unperfused load then dial off | 0.0503 | 0.2502 | 0.9787 | 2.764 | 10.04 |
| Case opening | 0.00666 | 0.03315 | 0.1304 | 0.3751 | 1.508 |

Margin over the runner-up: 2.84× → 2.78× → 2.56× → 2.11× → **1.029×**. Over
the case opening: 21.5× → 21.0× → 19.2× → 15.5× → 6.85×. The brief's figures
(10.36 / 10.03, 1.033×) have drifted slightly against the shipped parameters
since 2026-09-07; the finding is unchanged and the published numbers are
today's.

**The item was wrong that this is a `docs/MODEL.md` edit alone, and that is the
part worth recording.** The same section states that "both tables in this
section are held by a test". A published runner-up column that nothing
re-measures would have been a figure in the specification with no gate under
it — precisely what `PL-ZVS7` closed for the two tables already there. So
`tests/reference/test_control_resolution.py` gains
`_ranked_over_manoeuvres`, the two published dictionaries, and
`test_the_second_worst_manoeuvre_and_the_margin_above_it`, parametrized over
the rate ladder like the columns beside it.

**The margin is pinned tighter than everything else in the module, at 1%
against `PUBLICATION_RELATIVE_TOLERANCE`'s 5%.** That 5% band around 1.03 spans
1.0, so at the tolerance the rest of the table uses, the column that exists to
make a reversal visible would admit one. Verified by mutation: setting the
300× margin to 1.10 fails with `Obtained: 1.0290778558182117`, and reverting
passes.

**Why the reversal is worth guarding rather than merely disclosing** — which is
what option 3 would have rested on. `PUBLICATION_RELATIVE_TOLERANCE` is 0.05
and the two manoeuvres differ by 2.9% at 300×, so
`test_the_displacement_per_grid_step_at_each_playback_rate` passes with either
manoeuvre producing the figure. Only the argmax assertion sees a crossing, and
only on the day it happens. The margin column turns that into a trend a reader
and a diff can both watch.

**No margin floor was added, deliberately.** A threshold below 1.029× has no
non-arbitrary value and one above it fails today. Pinning the measured margin
is what gives the warning; a floor would have been a number chosen to pass.

**What the prose now says.** The worst column is framed as a bound over the
three manoeuvres, with the attribution to the ventilator start stated as a
measured fact that a named test re-checks — so a future parameter revision that
reverses the top two leaves the published bound correct and invalidates only a
sentence. The case-opening comparison stays, correct as it always was, but is
now labelled as a third manoeuvre and explicitly not the measure of the bound's
headroom, which is the defect with a factor of seven in it.

`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate` needed no
behaviour change but its docstring quoted the sentence this item removed; it
now quotes the replacement and records why the claim is the one assertion in
the module a reversal would trip.
