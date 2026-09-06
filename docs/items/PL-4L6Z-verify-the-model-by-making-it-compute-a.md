---
id: PL-4L6Z
title: 'Verify the model by making it compute a predictable event: recover a stored parameter from a simulated measurement, as Lerou and Booij recover alveolar volume by simulated helium dilution'
status: untriaged
feature: model-spec-accuracy
added: 2026-09-06
---

**Problem.** This project's verification rests on comparing the shipped step
against an oracle integrator and on mass-balance tolerances. Lerou and Booij
(Br J Anaesth 2001;86:12-28, read at full-text depth 2026-09-06) use a third
device this project has no instance of, and they name what it is for:
verification is "to ascertain its internal mathematical consistency, the
numerical accuracy of the computer processor and, **especially, the freedom
from designer-induced errors**". Their device is to make the model compute an
event whose answer is already known - they simulate the closed-circuit helium
dilution measurement of alveolar volume and check that the model recovers the
alveolar volume it was configured with.

That is a different class of test from an oracle comparison. An oracle checks
that the integrator solves the equations that were written; this checks that
the equations that were written are the ones intended, by running the model
through a procedure whose outcome is fixed by a stored parameter rather than by
the solver. A sign error, a swapped compartment or a units slip that an oracle
reproduces faithfully - because the oracle integrates the same wrong equations -
shows up here as a measurement that comes back wrong.

**Why it matters.** It is the one verification device that catches
designer-induced error rather than numerical error, which is the failure mode
`docs/MODEL.md`'s safety-critical standard is least protected against today:
every existing check would pass on a model that solves the wrong system
correctly. It is also cheap - it needs no new physics, only a scripted
procedure and an assertion.

Candidate procedures, in order of how little new machinery each needs:

1. **Recover a tissue volume from a washin.** Drive a compartment to a known
   fraction of equilibrium and recover its volume from the integrated uptake
   and the partition coefficient. Uses only what the model already exposes.
2. **Recover the alveolar volume** by an inert-tracer dilution, which is
   Lerou and Booij's own case, though it needs a second gas the model does not
   yet carry - see `PL-L2F2`, which is about exactly that gap.
3. **Recover cardiac output** from the Fick relation across a compartment at
   steady state.

**Where.** `tests/reference/`, alongside the existing oracle gate;
`docs/MODEL.md` - "Required tests", which is where the invariant would be
stated. `PL-8LDF` (tie MODEL.md's required invariants to named tests) and
`PL-GZP6` (two required tests are not implemented) are the neighbouring work,
and this would be a third entry rather than a replacement for either.

**Done when.** At least one procedure of this shape runs in the suite, asserts
recovery of a stored parameter to a stated tolerance, and is named in
`docs/MODEL.md` as a verification test distinct from the oracle comparison,
with a sentence saying what class of error it catches that the oracle does not.
