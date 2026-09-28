---
id: PL-95NW
title: Test whether the model's slower muscle return explains the open-circuit washout tail's closest approach to Yasuda's fitted mean curves over hours 2 to 4, by varying the muscle tissue:gas coefficient in the late-washout module; docs/MODEL.md's first-24-hours subsection records that reading as inferred from the isolated time constants and not tested (PL-KK1Q)
priority: P1
effort: M
status: ready
classes: science, test
feature: late-washout-evidence
touches: docs/MODEL.md, tests/reference/test_late_washout_against_published_fits.py
added: 2026-09-27
payoff: turns docs/MODEL.md's untested explanation of the late washout tail into a measured one, or corrects it
verify: ! grep -qF 'was not tested by varying them' docs/MODEL.md
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
