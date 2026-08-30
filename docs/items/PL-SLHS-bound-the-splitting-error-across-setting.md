---
id: PL-SLHS
title: Bound the splitting error across setting changes, not one held operating point
priority: P1
effort: S
status: done
classes: safety, science
feature: numerical-domain
milestone: v0.2.7
touches: tests/reference/test_coupled_dynamics.py, docs/MODEL.md
added: 2026-08-30
closed: 2026-08-30
commit: a0ac750
verify: uv run pytest tests/reference/test_coupled_dynamics.py -k bounded_across_setting_changes
---

**Problem.** The release gate that bounds the operator split's error is
exceeded by a trajectory the four interface sliders permit.
`tests/reference/test_coupled_dynamics.py:176` sets
`SPLITTING_ERROR_BOUND_PER_STEP_SECOND = 1.5e-3`, but `_shipped_system` and its
oracle counterpart (`:392-402`, `:422-448`) each build a fresh system and hold
one `OperatingPoint` constant for the whole run. No setting *change* is ever
compared against the oracle, so the gate measures the split only on
trajectories that never turn.

Measured with an independent RK4 oracle, calibrated against
`docs/MODEL.md:912-917`'s own constant-setting table (reproduced to three
figures): desflurane at dial 18%, fresh gas flow 10 L/min, cardiac output
10 L/min, alveolar ventilation held at 0 for 300 s and then set to 12 L/min
gives a coefficient of 1.5245e-3 — above the bound. The same scenario gives
1.03e-3 for sevoflurane and 1.11e-3 for isoflurane, both up from about 7e-4
under constant settings.

**Why it matters.** `docs/MODEL.md:1188-1192` states that this gate and the
"Displayed precision" decision "are coupled and must be revised together" — the
two-decimal readout is justified by the measured error, and the gate is set
1.24x above it "precisely so that a change large enough to invalidate this
section fails the gate rather than passing it silently". Both statements are
currently false and CI is green, which is the worst combination: the mechanism
built to catch this cannot see the case. Every setting change is a case the
interface offers with a slider.

This is PL-042's defect one dimension over. That item widened the domain across
the *settings envelope*; it was never widened across *trajectories*, and a
piecewise-constant run is what the application actually produces.

**Where.** `tests/reference/test_coupled_dynamics.py:176` (the bound), `:392-402`
(`_shipped_system`), `:422-448` (the oracle driver); `docs/MODEL.md:912-917`
(the coefficient table) and `:1188-1192` (the coupling statement and the
"Displayed precision" derivation).

**Approach.** Drive both the shipped and the oracle solutions through a *phase
list* — a sequence of `(duration, OperatingPoint)` — rather than one held
point. The oracle already integrates piecewise-constant settings, so this is a
driver change and not a solver change. Then re-measure the worst coefficient
over the widened domain and reset the bound and both `docs/MODEL.md` sections
from the new measurement rather than from the old one.

Record in `docs/MODEL.md` that the error is a **signed lag, not noise**: the
shipped split runs below the reference throughout wash-in and above it
throughout washout, so a reader comparing two compartments sees a bias common
to both rather than independent uncertainty. That is the difference between an
error that cancels in a comparison and one that does not, and the current text
says neither.

**Done when.** The coupled-dynamics gate exercises setting changes on both the
shipped and oracle sides, `SPLITTING_ERROR_BOUND_PER_STEP_SECOND` is reset from
a measurement over that widened domain, `docs/MODEL.md`'s coefficient table and
its "Displayed precision" section are revised together from the same
measurement and record the error's sign, and the desflurane scenario above
passes.
