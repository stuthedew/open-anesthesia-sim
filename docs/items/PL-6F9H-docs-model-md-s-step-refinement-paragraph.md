---
id: PL-6F9H
title: docs/MODEL.md's step-refinement paragraph reports the measured gap across four values, and test_step_refinement_converges reads three
status: untriaged
feature: invariant-test-gaps
added: 2026-09-19
---

**Problem.** docs/MODEL.md's step-refinement paragraph reports the measured gap across four values, and test_step_refinement_converges reads three

**Where.** `docs/MODEL.md` § "Required tests", the "Step-refinement test"
subsection, in the paragraph opening "What the third point asserts changed
with the exact step": "Measured 2026-09-06, the worst successive-halving gap
across the four reported values is 8.1e-16". `test_step_refinement_converges`
in `tests/reference/test_sevo_patient.py` reads three values - the alveolar,
vessel-rich and mixed-venous partial-pressure fractions. The test's own
docstring says "The three steps docs/MODEL.md specifies", which counts steps
rather than values, so the two counts are not obviously the same thing.

**Why it matters.** The sentence is a dated measurement, so under `PL-4FBP`'s
fourth clause it is a record and may be exactly right about 2026-09-06; but a
reader checking the specification against the suite finds four in one and
three in the other, with nothing saying which value was measured by hand or
has since been dropped. A disagreement between the specification and its own
test, found 2026-09-19 by `PL-4FBP`'s measurement.

**Done when.** The paragraph and the test agree on what is compared - the
fourth value is added to the test, or the sentence names the three and says
what the fourth was - and the annotation pass (`PL-2M9N`) names the test
beside the heading.
