---
id: PL-VXM0
title: test_step_refinement_converges asserts a 0.5% relative / 1e-8 absolute tolerance that its own 1e-14 gap assertion makes redundant: any gap failing the first exceeds 1e-8 and so fails the second. Decide whether to keep the 0.5% check as the fallback a fork with an approximate method would use (and say so in the test) or remove it, and whether docs/MODEL.md's requirement to document a 'release comparison tolerance' still has a purpose
priority: P3
effort: S
status: ready
classes: docs
feature: prose-quality
touches: docs/MODEL.md, tests/reference/test_sevo_patient.py
added: 2026-11-02
payoff: the step-size test keeps only limits that can fail, so no displayed explanation has to justify a number that never decides anything
verify: ! grep -q STEP_REFINEMENT_RELATIVE_TOLERANCE tests/reference/test_sevo_patient.py && ! grep -q 'release comparison tolerance' docs/MODEL.md
---

**Problem.** test_step_refinement_converges asserts a 0.5% relative / 1e-8 absolute tolerance that its own 1e-14 gap assertion makes redundant: any gap failing the first exceeds 1e-8 and so fails the second. Decide whether to keep the 0.5% check as the fallback a fork with an approximate method would use (and say so in the test) or remove it, and whether docs/MODEL.md's requirement to document a 'release comparison tolerance' still has a purpose

**Why it matters.** `docs/MODEL.md` has to explain every limit it states to
a clinician and to a developer. A limit that never decides a result costs the
explanation and protects nothing, and the owner rejected five explanations of
this one on 2026-11-02.

**Generator check.** Not a generator: one leftover assertion from the first
build, found while rewriting its paragraph.

**Where the 0.5% came from** (traced 2026-11-02, after the project owner said
"We should absolutely know where that came from").

1. **Set without a reason, 2026-08-22.** Commit `875ba085` ("Build v0.1.0
   sevo patient simulation") wrote the first `test_step_refinement_converges`.
   It compared only 0.1 s with 0.05 s, as `rel=5e-3, abs=1e-8` literals. The
   same commit's `docs/MODEL.md` said "The release comparison tolerance must
   be documented before tagging". Neither the commit, the test nor the
   specification gives a reason for 5e-3 or 1e-8.
2. **Checked and kept, 2026-08-30.** Commit `60b3bb30` (PL-VP7N) made the test
   three steps and wrote the tolerance into `docs/MODEL.md`. Its comment says
   the tolerance was "unchanged from the two-step version", and that the
   coarsest and finest steps then differed by about 4e-4 relative in the
   alveolar fraction, "an order of magnitude inside this". That is a check
   that the figure passed, and no derivation of it.
3. **A possible basis was written down then and not used.** The same commit
   described the mixed-venous gap of 1.4e-6 in fraction as "a seventh of a
   count of the last displayed digit". Tying the tolerance to the displayed
   precision would give it a reason a reader can check. That is one option
   for this item's decision.

So the honest statement is that 0.5% was a starting figure picked when the
test was first written, later confirmed to pass under the old method, and
never derived from a requirement.

**The owner's question, 2026-11-03 03:21Z.** "What's the point of the 0.5% if
it never decides something and we don't know where it came from" (project
owner, on the thread for #1950).

**Recommendation: remove the 0.5% and 1e-8 assertion, and the requirement in
`docs/MODEL.md` § "Step-refinement test" to document a "release comparison
tolerance".** Keep the 1e-14 rounding limit as the test's only limit. The
reasons:

1. **It cannot change a result.** The assertion passes when a gap is within
   0.5% or within 1e-8 absolute. A gap that fails it is larger than 1e-8, so
   it also fails the 1e-14 limit in the same test. Removing it changes no
   pass or fail.
2. **No record gives it a purpose.** It was typed on 2026-08-22 with no
   reason, and on 2026-08-30 it was only confirmed to pass (see "Where the
   0.5% came from" above). A limit with no stated reason and no effect is the
   kind of number the owner asked not to keep (2026-11-02, "magic numbers").
3. **The case it might serve needs a different test.** A fork that switches
   to an approximate method should not fall back on a fixed 0.5%. The
   standard check for such a method is an order-of-accuracy test: halving
   the step should shrink each gap by the factor the method's order
   predicts, about 2 for a first-order method. This test made exactly that
   check under the operator split, before #376 replaced it with the exact
   step. A fixed percentage would pass a method whose error does not shrink
   at all, as long as the error is small. Sources: Oberkampf WL, Roy CJ.
   *Verification and Validation in Scientific Computing*. Cambridge
   University Press; 2010, chapter "Code verification", on the
   order-of-accuracy test
   (https://www.cambridge.org/core/books/abs/verification-and-validation-in-scientific-computing/code-verification/733E362E9B977EA1E3745BF9FAF607A0);
   Roache PJ. Quantification of uncertainty in computational fluid dynamics.
   *Annu Rev Fluid Mech*. 1997;29:123-160,
   https://doi.org/10.1146/annurev.fluid.29.1.123, on refinement studies and
   the observed order of convergence.
4. **What a forker needs instead is one sentence**, in the section's note for
   developers: a method that is not exact fails the 1e-14 limit, and should
   replace it with an order-of-accuracy test, not a looser fixed limit.

Option kept for the record: keep the assertion with a value derived from the
display, so that the step can never move a displayed digit. PL-VXM0's third
point above notes the old split's mixed-venous gap was a seventh of one
displayed count. That gives the number a reason, but it still never decides a
result while the method is exact, so it adds a number to explain and nothing
to check.

**Done when.** `test_step_refinement_converges` asserts only the rounding
limit, `STEP_REFINEMENT_RELATIVE_TOLERANCE` and
`STEP_REFINEMENT_ABSOLUTE_TOLERANCE` are gone, and `docs/MODEL.md`
§ "Step-refinement test" no longer requires a release comparison tolerance
and says in its note for developers what a fork with an approximate method
should test instead. This lands with the resumed `docs/MODEL.md` rewrite
(#1950), because that section is paused there.
