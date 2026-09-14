---
id: PL-ZMRT
title: Decide whether a branch's run definition should open at the fork instant, leaving the app one simulated-time frame instead of two
status: untriaged
added: 2026-09-14
---

**Problem.** Decide whether a branch's run definition should open at the fork instant, leaving the app one simulated-time frame instead of two

**The decision is the project owner's**, because answering it re-words
`ROADMAP.md`'s `v0.5.0` Required-scope clause for `PL-J2TD` (the fork
resumption), which the owner settled on 2026-09-14. It is recorded rather than
raised because `PL-J2TD` shipped without needing it: the shipped seam satisfies
`docs/MODEL.md` as written and closes every safety finding the question turned
up. What is left is a design question about how many time frames the
application carries, and the evidence for answering it arrives with `PL-B9PY`
(rendering two runs at once) and `PL-2R2C` (the drawn columns not aligning).

**Where it stands today.** A branch's `SimulationState` clock is the case's;
its `RunDefinition` opens at its own zero and is re-based by subtracting the
fork instant, which `SimulationController.advance` and `drawn_window` do. So
the application carries two frames and the controller converts between them.
Everything the controller *exposes* is the case's - `snapshot().elapsed_s`,
every control-change stamp, `drawn_window`'s instants - with one exception:
`run_segments` hands out the definition's own keyframes, and `origin_s` is what
places them.

**The alternative.** `RunDefinition` takes an optional `opened_at_s`, so a
branch's definition opens *at* the fork instant carrying the parent's keyframe.
Then there is one frame, no conversion anywhere, `run_segments` needs no
caveat, `PL-2R2C`'s grids align for free, and the round-trip hazard
`docs/MODEL.md` records - `(900.0 + 1e-6) - 900.0` is 9.999999974752427e-07 -
stops being a rule a caller must follow and becomes unrepresentable, because
there is no offset to name.

**What was measured while `PL-J2TD` was built, so it need not be re-measured.**

- **Exactness does not decide it.** Both arrangements reproduce the parent
  bit-for-bit at every shared instant when used correctly: 0 of 6 probe
  instants differ either way, and 0 of 601 across a longer run. The clock
  disagreement figure sometimes quoted for this question - `origin + n x step`
  against the trunk's `(k + n) x step`, worst 1.5e-11 s - moves a compartment
  fraction by at most 3.6e-14 and an accumulator by 7.2e-13 L, six to nine
  orders below what a reader sees. **Any case resting on that number is
  wrong.**
- **The safety findings are already closed and do not select it.** The fresh
  24 h envelope, the clock reading zero at 45 minutes, the control marks drawn
  early: every one of those is a property of a branch whose *step count*
  restarts, and `PL-J2TD` continues the parent's. They are not arguments for
  this change.
- **What it costs.** `RunDefinition.__init__` gains a parameter; one paragraph
  of `docs/MODEL.md` § "The canonical evaluation rule" (19 lines) and one
  `ROADMAP.md` clause are re-worded; `tests/reference/test_canonical_evaluation.py`'s
  fork test gets shorter and strictly stronger. Outside the item files,
  "re-based" appears in exactly three places in the repository.
- **One cost is a real guard rather than prose, and it is blocking.**
  `_require_within_run`'s lower bound is hard-coded to `0.0`. Measured on a
  definition whose segments open at 600 s and 900 s: `state_at(0.0)`,
  `state_at(100.0)` and `state_at(599.9)` all returned 0.005664 alveolar
  fraction rather than refusing, because `_segment_index_at` returns `-1` and
  Python indexes the **last** segment; `evaluate_anchored(0, 500, 100)` then
  drew a *varying* curve - 0.005664, 0.005664, 0.005610, 0.005565, 0.005520,
  0.005664 - across a span the case spent at zero. That bound must move to the
  opening in the same change, and `_segment_index_at` must not wrap.

**The asymmetry worth weighing.** Under the arrangement shipped, the residual
hazard is a caller handing a case instant to a branch's `state_at` and getting
an exact, in-range, wrong-by-the-fork-instant answer that no bounds check can
refuse, because both frames are legal non-negative floats inside the run. It is
bounded today: `state_at` has **no production caller in `src/`** - only
`RunDefinition`'s own body and docstrings - so the discipline is needed at one
site rather than across the tree. Under the alternative that hazard cannot be
expressed, and the new one it creates *is* refusable, which is why the guard
above is the whole of its cost.
