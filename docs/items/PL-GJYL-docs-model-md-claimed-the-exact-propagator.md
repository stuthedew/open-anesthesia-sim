---
id: PL-GJYL
title: docs/MODEL.md claimed the exact propagator solves the governing equations at any positive gas volumes, which measurement contradicts below 1e-9 L
status: done
closed: 2026-09-06
priority: P1
effort: S
classes: safety, docs
feature: numerical-domain
touches: docs/MODEL.md
verify: python3 tools/doc_check.py check && ! grep -qF 'for any positive volumes' docs/MODEL.md
added: 2026-09-06
---

**Problem.** docs/MODEL.md claimed the exact propagator solves the governing equations at any positive gas volumes, which measurement contradicts below 1e-9 L

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `PL-GYH2` landed a sentence in `docs/MODEL.md`
§ "What is not bounded this way" reading "The exact propagator solves the
governing equations for any positive volumes whatever". It was written from
the argument rather than from a measurement, and the argument only needed the
claim at the volumes under discussion. Run, it is false.

Measured 2026-09-06 on sevoflurane at the shipped 0.1 s step, driving
`AlveolarCompartment.gas_volume_l` down and advancing three steps:

| `gas_volume_l` | Outcome |
| --- | --- |
| 0.005 L, 1e-6 L | advances, accounting passes |
| 1e-9 to 1e-30 L | `AgentSimulationValidationError` |
| 1e-100 L | `SimulationNumericalError`, step rolled back |
| 1e-300 L | advances, returns exactly 0, accounting passes (`PL-3PRZ`) |

Circuit volume has no such point: advanced to 1e300 L with accounting passing.

**Why it matters.** `docs/MODEL.md` is the authoritative specification and is
held to the safety-critical standard, under which an overclaim about numerical
robustness is a defect whether or not anything currently depends on it. This
one would have been read as a licence: a later session widening a range, or
choosing not to guard a volume, could cite the sentence as settling the
numerics.

**Fix.** State what was measured and at what values. That is also what the
physiological argument needs and no more - at any volume a caller would
plausibly pass, the equations solve and mass balance holds, so the refusal
rests on physiology rather than on arithmetic. The section additionally now
says the accounting guard is a *backstop* rather than a declared bound, so
1e-9 L is not read as a limit the document sets.

**How it was found, which is the reusable part.** By executing the claim
instead of re-reading it, during a recheck of `PL-GYH2`'s own delivered
documentation. Nothing in `make check` could have caught it: `doc_check`
decides whether a cited path exists and whether a marked value matches its
data file, never whether a sentence about the model's behaviour is true. That
line is deliberate (`CLAUDE.md`, "Do not script the judgment"), so this class
of error has no mechanical guard and is caught only by someone running the
claim.
