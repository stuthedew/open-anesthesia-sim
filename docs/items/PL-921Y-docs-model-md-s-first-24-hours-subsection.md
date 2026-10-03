---
id: PL-921Y
title: docs/MODEL.md's first-24-hours subsection compares the model's isolated muscle time constant with Yasuda's fitted one, which is an apparent constant read off the whole washout curve; read the same way, off the eigenvalues of the model's open-circuit system, the model's muscle term runs 1.9 to 2.0 times the fitted one at about half its amplitude (measured 2026-10-03), not 1.5 to 1.7
priority: P1
effort: S
status: done
classes: science, docs, test
feature: late-washout-evidence
touches: docs/MODEL.md, tests/reference/test_late_washout_against_published_fits.py, pyproject.toml, uv.lock, docs/ARCHITECTURE.md, docs/WORKING_NOTES.md
added: 2026-10-03
closed: 2026-10-03
pr: 1319
payoff: docs/MODEL.md's explanation of the washout tail's middle hours compares the model's muscle and fat terms with the fitted ones like for like, so the size of the difference it names is the real one
verify: grep -q 'def test_[a-z0-9_]*apparent' tests/reference/test_late_washout_against_published_fits.py
---

**Problem.** docs/MODEL.md's first-24-hours subsection compares the model's isolated muscle time constant with Yasuda's fitted one, which is an apparent constant read off the whole washout curve; read the same way, off the eigenvalues of the model's open-circuit system, the model's muscle term runs 1.9 to 2.0 times the fitted one at about half its amplitude (measured 2026-10-03), not 1.5 to 1.7

**What was measured, 2026-10-03.** Found while working `PL-95NW`. The model's
open-circuit system - its system matrix restricted to the alveolar, venous and
three tissue states, with the inspired fraction held at zero, which is the
limit `_discard_circuit_contents()` drives at every step - was decomposed into
its modes with `numpy.linalg.eig`, from the state at the end of the shipped
30-minute wash-in. The sum of those exponentials reproduces the stepped
open-circuit run to within 0.08% at 30, 60, 240, 600 and 1440 minutes for all
three agents, so it is the model's own five-term curve, the form Yasuda et al.
fitted to the volunteers. Its muscle term against the fitted one:

| Agent | Model tau (min) | Fitted tau (min) | Ratio | Model A (%) | Fitted A (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sevoflurane | 154.5 | 81.7 | 1.89 | 2.37 | 4.60 |
| Isoflurane | 161.4 | 85.0, 80.0 | 1.90, 2.02 | 4.31 | 7.19, 5.93 |
| Desflurane | 92.6 | 48.9 | 1.89 | 2.47 | 4.86 |

The isolated constants the subsection compares instead are 135.4, 126.9 and
84.7 minutes, 1.49 to 1.73 times the fitted. The apparent constant is the
longer one because part of what the muscle group returns comes back to it in
arterial blood rather than leaving in the exhaled gas. With the coefficient
lowered as `PL-95NW` lowered it, isolated constant equal to the fitted one,
the apparent constant is 93.4, 108.5 and 102.1, and 53.5 minutes, still 1.1 to
1.3 times the fitted. The fat term reads the same way: 2653, 2860 and 1543
minutes apparent against the subsection's isolated 2500, 2600 and 1500.

**Why it matters.** The subsection explains the tail by comparing the model's
time constants with the fitted ones, and the fitted ones are apparent
constants of the whole curve. Like for like, the model's muscle term is about
twice as slow as the fitted one and half as large, where the subsection says
1.5 to 1.7 times and says nothing of the amplitude, so its reading of the
tail's middle hours rests on a comparison that understates the difference it
names.

**Done when.** The subsection compares the model's apparent muscle and fat
constants, and their amplitudes, with the fitted ones, and a test in
`tests/reference/test_late_washout_against_published_fits.py` whose name says
it reads the apparent constants pins every number it prints, including the
reconstruction check above.

**How to pin it - recommended: declare numpy as a test dependency.** numpy is
installed only because pyqtgraph needs it, and no test imports it. Declaring
it for the tests and decomposing with `numpy.linalg.eig` adds no new code to
verify, and the reconstruction check is the test that the modes describe the
stepped run. The other route, a pure-Python solve of the 5-by-5 block, is code
that would need verifying in its own right.

**Built (2026-10-03).** The test writes the open circuit's elimination out as
five equations, those of `docs/MODEL.md` § "Governing equations" with nothing
inspired, from the parameter loaders alone, the way `test_coupled_dynamics.py`
builds its system. It does not read `core/governing_equations.py`'s matrix,
because `docs/ARCHITECTURE.md` keeps a reference case from reaching the code it
checks; the two agree to 2e-16 (measured once). Decomposed with
`numpy.linalg.eig` from the state each run held at discontinuation, the modes
reproduce the stepped open-circuit run to within 0.08% at every minute from the
fifth, the run lying above them. Halving the step halved that, 0.052 to 0.026%
at five minutes, so it is the driver re-breathing within each step and not the
decomposition. A 1% change to one rate moves the modes 2.1 to 2.3% off the run,
so the check fails on a wrong equation.

Two corrections to the brief above, which is left as it was written:

- Sevoflurane's and isoflurane's two fastest modes are a complex-conjugate
  pair, a damped oscillation that falls e-fold in about a quarter of a minute,
  so the model's curve is not five real exponentials. The three slower modes
  are real, and the comparison reads only those.
- At the coefficient `PL-95NW` ran, isoflurane's apparent muscle constant
  against the *Anesth Analg* cohort is 108.4 minutes, not 108.5.

numpy is declared in the `dev` group by the owner's rule in
`docs/WORKING_NOTES.md` § "Decided: no numpy", decide it in the commit that
wants it; that note and `docs/ARCHITECTURE.md` say so, and no module under
`src/` imports it. `docs/MODEL.md` now sets the model's apparent muscle and fat
terms against the fitted ones in a table, says why the isolated constants are
shorter, and says `PL-95NW`'s variation brings the apparent muscle constant to
1.09 to 1.28 times the fitted. `test_the_model_s_apparent_muscle_and_fat_terms_against_the_fitted_ones`
pins every number it prints.
