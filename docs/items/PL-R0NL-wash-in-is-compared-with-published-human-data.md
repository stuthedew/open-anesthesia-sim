---
id: PL-R0NL
title: Wash-in is compared with published human data at one instant, 30 minutes, so the first 15 minutes of the F_A/F_I rise, the phase the simulator most displays, are compared against nothing published and a doubled FRC that moves F_A/F_I at 1 min by -0.118 passes every gate
status: untriaged
feature: validation-resolving-power
added: 2026-10-17
---

**Problem.** Wash-in is compared with published human data at one instant, 30 minutes, so the first 15 minutes of the F_A/F_I rise, the phase the simulator most displays, are compared against nothing published and a doubled FRC that moves F_A/F_I at 1 min by -0.118 passes every gate

**Severity: high for validation coverage; nothing displayed is known to be
wrong.** Audit finding CMP-3, confirmed by the adversarial verifier.

**Evidence.** The only comparison of wash-in with published human data is
`test_thirty_minute_ratio_matches_published_human_measurement` in
`tests/reference/test_published_wash_in_and_elimination.py`. Through
`_wash_in_ratio`, it samples F_A/F_I once, at `WASH_IN_DURATION_S = 1800.0`.
The other reference modules compare elimination or self-consistency, not
early wash-in against published data.

A probe drove the validation protocol (FGF 10 L/min, 1% dial) on the module's
own configured system:

| Change | F_A/F_I at 1 min | at 5 min | at 30 min |
| --- | --- | --- | --- |
| Sevoflurane, alveolar gas volume (FRC) x2 | 0.443 to 0.325 (-0.118) | -0.033 | -0.0016 (-0.087 published SD) |
| Desflurane, FRC x2 | -0.145 | | -0.12 SD |
| Vessel-rich volume x0.5 | | +0.058 | +0.12 SD |
| FRC x1.1 (default operating point) | -0.0143 | | -0.0001 |
| Circuit volume x1.1 (default operating point) | -0.0047 | | -0.00005 |

So the one gated time point barely registers FRC or circuit volume.
`docs/MODEL.md` says so itself: the lineage "is worth least in the phase
the simulator most displays, the first minutes of the F_A/F_I rise".
`docs/references/README.md` records that only the 30-minute and 5-minute
ratios and the fits were taken from the papers, that the washout figures were
read only qualitatively, and that the wash-in apparatus methods were not read
in any pass. That the Yasuda figures carry an early time course that can be
extracted is inferred, not verified.

One nuance from the verifier: a parameter changed in the code still trips the
pins (an alveolar volume moved from 2.5 to 2.8 L fails
`test_control_resolution`). "Passes every gate" holds for an error that is
already in the shipped parameter set, which is how this finding is scoped.

**Why it matters.** A model or provenance error that makes the induction curve
wrong by 25-30% at 1-2 minutes would pass every gate. FRC, circuit mixing and
vessel-rich capacity are the likely sources. The 30-minute ratio moves by an
order of magnitude less than the published spread for such errors. The early
rise is the curve a learner watches most.

**Where.** `tests/reference/test_published_wash_in_and_elimination.py`
(`_wash_in_ratio`, `test_thirty_minute_ratio_matches_published_human_measurement`,
`WASH_IN_DURATION_S`); `docs/references/`; `docs/MODEL.md`.

**Recommended work.** Extract the Yasuda 1991 F_A/F_I time course from the
private reference corpus into `docs/references/`, for example at 1, 2, 3, 5,
10, 15, 20 and 25 min, as mean ± SD with page and figure locators. Add a test
that drives the published protocol with the inspired fraction held at the
airway. That needs an F_I-clamp driver like the existing open-circuit one,
since the shipped circuit lags by its time constant. Assert each time point
within the published SD. Where the model disagrees, assert a stated
regression band, as the elimination half does. Write down what a
disagreement in the early phase would mean before running the comparison.

**Done when.** Early wash-in time points, at least 1 to 5 minutes, are
compared against published values with locators, or this item records that
no published early time course exists to compare against.

**Related.** `PL-Z3V5` (ready) decides the format of an extraction note, which
the extracted time course would use. `PL-4QCJ` is the extraction note for the
Yasuda methods reading, from the same papers. `PL-9YHR` is the same feature,
for the stored parameters.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.
