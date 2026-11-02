---
id: PL-VXM0
title: test_step_refinement_converges asserts a 0.5% relative / 1e-8 absolute tolerance that its own 1e-14 gap assertion makes redundant: any gap failing the first exceeds 1e-8 and so fails the second. Decide whether to keep the 0.5% check as the fallback a fork with an approximate method would use (and say so in the test) or remove it, and whether docs/MODEL.md's requirement to document a 'release comparison tolerance' still has a purpose
status: untriaged
added: 2026-11-02
---

**Problem.** test_step_refinement_converges asserts a 0.5% relative / 1e-8 absolute tolerance that its own 1e-14 gap assertion makes redundant: any gap failing the first exceeds 1e-8 and so fails the second. Decide whether to keep the 0.5% check as the fallback a fork with an approximate method would use (and say so in the test) or remove it, and whether docs/MODEL.md's requirement to document a 'release comparison tolerance' still has a purpose

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
