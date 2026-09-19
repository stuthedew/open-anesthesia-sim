---
id: PL-6F9H
title: docs/MODEL.md's step-refinement paragraph reports the measured gap across four values, and test_step_refinement_converges reads three
priority: P3
effort: S
status: ready
classes: docs, test
feature: invariant-test-gaps
touches: docs/MODEL.md, tests/reference/test_sevo_patient.py
added: 2026-09-19
verify: grep -q 'successive-halving gap across the three' docs/MODEL.md
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

**What triage found, 2026-09-19, and it narrows the item.** The paragraph
immediately below the one at issue names the compared values outright: "The
release comparison tolerance is 5e-3 relative or 1e-8 absolute, either
satisfying, on the alveolar, vessel-rich and mixed-venous fractions after 60 s".
`_states_after_one_minute` in `tests/reference/test_sevo_patient.py` returns
those same three, and its own docstring calls them "The three compared states".
So `docs/MODEL.md` says three in one paragraph and four in the next, about the
same quantity - which makes "four" the stale count rather than the test being a
value short, and makes the narrowing route the likely one. It is not certain:
`STEP_REFINEMENT_STEPS_S` holds three steps and so two successive halvings, and
an earlier four-step list would have given three gaps, so "four" may be a stale
*step* count rather than a stale value count. Whoever takes this reads the
git history of the paragraph before rewriting it, and repoints `verify:` if the
answer turns out to be the other route.
