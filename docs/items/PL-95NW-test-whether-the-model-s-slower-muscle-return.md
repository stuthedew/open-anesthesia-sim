---
id: PL-95NW
title: Test whether the model's slower muscle return explains the open-circuit washout tail's closest approach to Yasuda's fitted mean curves over hours 2 to 4, by varying the muscle tissue:gas coefficient in the late-washout module; docs/MODEL.md's first-24-hours subsection records that reading as inferred from the isolated time constants and not tested (PL-KK1Q)
priority: P1
effort: M
status: done
classes: science, test
feature: late-washout-evidence
touches: docs/MODEL.md, tests/reference/test_late_washout_against_published_fits.py
added: 2026-09-27
closed: 2026-10-03
pr: 1313
payoff: turns docs/MODEL.md's untested explanation of the late washout tail into a measured one, or corrects it
verify: ! grep -qF 'was not tested by varying them' docs/MODEL.md
recurrences: 2026-10-03 PL-921Y
---

**Problem.** Test whether the model's slower muscle return explains the open-circuit washout tail's closest approach to Yasuda's fitted mean curves over hours 2 to 4, by varying the muscle tissue:gas coefficient in the late-washout module; docs/MODEL.md's first-24-hours subsection records that reading as inferred from the isolated time constants and not tested (PL-KK1Q)

**Why it matters.** `docs/MODEL.md`'s first-24-hours subsection explains the
open-circuit tail's closest approach to Yasuda's fitted means over hours 2 to 4
by the model's slower muscle return, and says that reading "was not tested by
varying them". It is one of the explanations a reader leans on for where the
model departs from the data; tested, it is either confirmed or replaced.

**Done when.** The muscle tissue:gas coefficient has been varied in
`tests/reference/test_late_washout_against_published_fits.py`'s comparison, and
the subsection states what that did to the tail's approach in place of the
untested reading.

**Built (2026-10-03): the reading holds, and reaches the shipped tail too.**
`_washout_curve()` now takes a muscle tissue:gas coefficient the data files do
not hold and a run length, and
`test_the_muscle_group_s_slow_return_places_the_tail_s_rise_in_hours_2_to_4`
lowers the coefficient to 0.58-0.67 of the stored value, which makes the
group's isolated time constant each cohort's fitted one, then runs six hours
in both conditions.

- *The control.* The group holds only 4 to 10% less at discontinuation, since
  over a 30-minute wash-in it takes up agent about as fast as its blood flow
  brings it, so the variation moves how fast the store returns and not how
  much there is.
- *Open circuit.* The peak of model over fit after the early dip moves from
  2.17-3.92 h to 0.62-1.45 h, and at four hours the tail is 0.50, 0.62, 0.24
  and 0.70 of the fitted curve instead of 0.82, 0.85, 0.58 and 1.04.
- *Shipped.* The peak moves from 2.27-4.15 h to 0.65-1.97 h, and the stretch
  above the curve ends at 1.6, 3.7 and 4.5 h instead of 6.9, 7.3 and 8.4, and
  never opens for desflurane. So the shipped excess before the seventh hour is
  the slow muscle return carried by the rebreathing circuit, not the circuit
  alone, and the three passages of `docs/MODEL.md` that named the circuit
  alone - this subsection, § "Supported run length" and the
  intertissue-diffusion note - now name both.
- *Graded, not two-point.* At 0.8 of the stored coefficient, measured once and
  not pinned, the open-circuit peak sits at 2.80, 2.58 and 2.50 h for
  sevoflurane and the two isoflurane cohorts, between the stored and the
  lowered values.

The varied runs stop at six hours, a quarter of a full curve each, so the eight
new cases cost about two curves; the module ran in 71 s on four workers with
them. Found beside it and filed: `PL-921Y`, the subsection's isolated time
constant set against a fitted apparent one.
