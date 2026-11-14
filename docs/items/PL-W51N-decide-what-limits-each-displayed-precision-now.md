---
id: PL-W51N
title: Decide what limits each displayed precision, now that one SD of the muscle tissue:gas coefficient moves the readouts by up to 90 counts and makes the readouts' two decimals, the schematic's two-figure amounts and whole-percent shares, and long runs' 0.1 L totals all finer than the seventh of an SD that docs/INTERFACE.md § Displayed precision allows
status: untriaged
feature: model-claims-held-by-tests
added: 2026-11-14
---

**Problem.** `docs/INTERFACE.md` § "Displayed precision" sets an upper limit
on every displayed precision from parameter uncertainty: a last digit may be
finer than the shift that one published SD of a partition coefficient causes,
but not far finer. Until `PL-TDX0` the section took every tissue SD from
Yasuda, Targ and Eger's brain:blood row, 3.9% to 6.4% of the mean. The SDs of
the coefficients the model stores are much wider for muscle: 37% to 45% of the
mean (Yasuda, Targ and Eger 1989, Table 1, p. 371, read at full text
2026-11-14). Re-measured with those SDs, the rule no longer allows what ships.
`tests/integration/test_parameter_uncertainty.py` holds each figure below.

1. **Readouts, two decimals.** One SD of the muscle coefficient moves a
   readout by 0.15 to 0.90 percentage points in the first hour at 1 MAC, which
   is 15 to 90 counts of the last digit. So that digit is a fifteenth to a
   ninetieth of an SD. The section refused a third decimal at a seventieth.
   One decimal would still be a ninth of an SD for desflurane, and the
   section's lower limit refuses one decimal because fat and muscle would read
   0.0% while they fill.
2. **Schematic amounts, two significant figures.** One SD of the muscle
   coefficient moves muscle's amount by up to 44% of it. At its finest, one
   step of the two figures is a twenty-fourth of an SD (sevoflurane's muscle
   at 3 h, 923 mL in steps of 10 mL).
3. **Schematic shares, whole percent.** One SD moves a share by up to 9.8
   percentage points (isoflurane's muscle at 24 h), so one step is a tenth of
   an SD.
4. **Run totals, 0.1 L.** At 1 MAC, one step is a sixth to a seventh of an SD
   at 24 h. At each agent's dial maximum and 10 L/min it is a twenty-first to
   a twenty-eighth of an SD at 24 h (`PL-0P3F`). The exhausted total in
   millilitres of liquid, in whole millilitres, is then a tenth to a
   fourteenth of an SD.

**Why it matters.** The section's own rule now says that four displayed
precisions claim more than the parameters support, while the same section
keeps them. A reader who checks the argument finds that it no longer reaches
its conclusion. The safety-critical standard asks that precision not imply
more certainty than the model supports, so the rule and the displays have to
be brought back into agreement one way or the other.

**Decision needed.** Should between-patient uncertainty in the partition
coefficients limit how finely the simulator shows a value? The answer changes
what a learner sees under B, and changes the stated reason for every
precision under A, so it is the owner's.

- **A. Keep every precision as shipped, and stop using parameter uncertainty
  as the upper limit.** The section would set each precision by what one run
  can tell apart and by legibility, and would state the one-SD shifts as a
  limitation on reading any value as a prediction for a patient. The learner
  sees no change on screen. The section would say plainly that a muscle or
  fat reading can differ between patients by many times its last digit.
- **B. Keep the rule, and coarsen what it refuses.** The readouts would drop
  to one decimal or fewer where the muscle coefficient reaches, the amounts
  to one significant figure, the shares to steps of 10 percentage points and
  the long-run totals to whole litres. The learner loses the slow
  compartments' wash-in, which the lower limit exists to keep: at one decimal
  muscle reads 0.0% for its first 3 to 15 minutes, and fat for 19 minutes with
  desflurane and for the whole first hour with the other two agents.

**Recommendation: A.** The SD measures how much one patient's muscle differs
from another's (Table 1's specimens came from autopsies, and Yasuda reports
that muscle solubility rises with age). Rounding a single simulated patient's
value does not show that spread, and it hides the within-run change that the
display exists to teach. The display already states that no value is a
prediction for a patient (`docs/MODEL.md` § "Known limitations"), and the
one-SD shifts are a measured size for that statement. A separate question,
not part of this decision, is whether the interface should show that spread
beside the tissue readouts.

**Done when.** The owner has chosen. Under A, § "Displayed precision" states
the upper limit as the owner chose it, and every paragraph that judges a
precision against "a seventh of an SD" is restated. Under B, each refused
precision is changed with its tests, and the approved interface wording is
updated.

**Generator check.** Not a generator. It is one consequence of `PL-TDX0`'s
correction, found once.
