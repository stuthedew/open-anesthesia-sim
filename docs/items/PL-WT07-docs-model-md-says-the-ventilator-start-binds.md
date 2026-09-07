---
id: PL-WT07
title: docs/MODEL.md says the ventilator start binds the per-rate displacement table 'throughout', but at 300x it leads the unperfused load by only 3% (10.36 vs 10.03 pp) and 'throughout' reads as a comfortable margin
status: untriaged
added: 2026-09-07
---

**Problem.** docs/MODEL.md says the ventilator start binds the per-rate displacement table 'throughout', but at 300x it leads the unperfused load by only 3% (10.36 vs 10.03 pp) and 'throughout' reads as a comfortable margin

**Why it matters.**

**Where.**

**Done when.**

**Found while working `PL-ZVS7`** (the gate that pins both tables), 2026-09-07.

**The measurement.** Worst displacement per grid step, desflurane binding
throughout, in percentage points:

| Manoeuvre | 1x | 5x | 20x | 60x | 300x |
| --- | --- | --- | --- | --- | --- |
| Ventilator start | 1.43e-1 | 6.95e-1 | 2.51 | 5.83 | 1.04e1 |
| Unperfused load then dial off | 5.03e-2 | 2.50e-1 | 9.79e-1 | 2.76 | 1.00e1 |

The ventilator start leads by 2.8x at 1x and by 1.033x at 300x. It is still the
binding case, so `docs/MODEL.md` is not wrong today and
`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate` passes.

**Why it is worth recording.** "Throughout" reads as a settled property of the
manoeuvre rather than as a 3% lead that a parameter revision could reverse. The
two converge because they saturate at different rates - the ventilator start's
transient has largely run inside a 30 s grid step while the unperfused load's is
still going - so the crossing is a real possibility rather than a rounding
artifact, and the published 1.0e1 pp figure would survive it while the sentence
naming the manoeuvre would not.

**Options.** Say the margin in the same sentence, which costs a clause and makes
the claim self-dating; or publish the second row of the table above, which is
the fuller answer and is what the gate already measures; or leave it, on the
grounds that the gate now fails the moment the claim stops being true, which is
the argument for doing nothing.

**Done when.** `docs/MODEL.md` § "Supported simulation step" no longer implies a
comfortable margin where there is a 3% one, or the decision to leave it is
recorded there.
