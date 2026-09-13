---
id: PL-TCW5
title: FLOW_FRACTION_TOLERANCE is defined twice, so the two perfusion-sum guards can drift apart silently
status: done
priority: P3
effort: S
classes: refactor
touches: src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/patient.py
added: 2026-09-02
closed: 2026-09-13
verify: uv run pytest tests/unit/test_parameters.py && grep -q 'def test_the_perfusion_tolerance_is_defined_once_for_both_guards' tests/unit/test_parameters.py
---

**Problem.** `FLOW_FRACTION_TOLERANCE = 1e-12` is defined independently in
`core/parameters.py` and `core/patient.py`, and the "tissue perfusion
fractions must sum to 1" rule is implemented against each. Changing one
leaves the two guards disagreeing about what "sums to 1" means, with nothing
to say so.

**Why it matters.** The duplicated *check* is correct and should stay - the
loader guards the data file, `PatientCompartments.__post_init__` guards
direct construction, and defence in depth is the point. The duplicated
*constant* is the finding: it is a policy value that could reasonably change,
unlike `SECONDS_PER_MINUTE`, which is defined in four modules and is harmless
there because it cannot change. That distinction is the whole content of this
item, and it is why "de-duplicate the constants" would be the wrong reading.

**Where.** `src/anesthesia_sim/core/parameters.py` and
`src/anesthesia_sim/core/patient.py`.

**Decision needed.** Whether one definition imported by both is worth an
import edge from `patient.py` into `parameters.py` - which already exists,
since `patient.py` imports `AgentParameters` from it - or whether two
independent constants are acceptable at this size. If they are, say so in a
comment at each so the next reader does not file this again.

**Done when.** The decision is recorded, and either one definition remains
or both carry the note saying the duplication is deliberate.

**Measured 2026-09-02: nothing to run.** This one is static and was verified
by reading the tree rather than by a probe, which is the honest answer for
it. `grep -rn "FLOW_FRACTION_TOLERANCE = " src/` returns exactly two lines,
`core/parameters.py` and `core/patient.py`, both `1e-12`. There is no
behaviour to measure - the defect is that a future edit to one is invisible
to the other, and no probe can demonstrate a divergence that has not
happened yet.

**Decided 2026-09-13: one definition, in `core/parameters.py`.**
The question the brief poses - whether one definition is worth an import edge
from `patient.py` into `parameters.py` - answers itself on inspection, and
that is the reason this took no design round: `patient.py` line 12 already
reads `from anesthesia_sim.core.parameters import AgentParameters,
ReferenceAdultParameters`. The edge exists. Sharing the constant adds nothing
to the module graph, so the cost side of the trade the brief describes is
zero and only the benefit is real.

The brief's distinction is preserved exactly as it states it: the duplicated
*check* stays - the loader guards the data file, `PatientCompartments.__post_init__`
guards direct construction, and defence in depth is the point - while the
duplicated *number* goes. A comment at the surviving definition says which of
the two is deliberate, so the next reader does not file this again, and
`test_the_perfusion_tolerance_is_defined_once_for_both_guards` asserts the
shape rather than the value, so retuning the tolerance stays a one-line
change.
