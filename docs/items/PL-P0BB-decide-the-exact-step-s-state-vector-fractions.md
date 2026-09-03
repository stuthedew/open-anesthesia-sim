---
id: PL-P0BB
title: "Decide the exact step's state vector: fractions or amounts, and whether a compartment or the system owns the trajectory"
priority: P1
effort: M
status: done
classes: science, planning
feature: numerical-domain
milestone: v0.3.2
touches: src/anesthesia_sim/core, docs/MODEL.md
added: 2026-09-03
closed: 2026-09-03
pr: 256
not-delegable: the next step is a decision about the numerical method's state representation and a safety-critical invariant, not code; no command can prove a decision, and the implementation it authorizes edits `core/` and `docs/MODEL.md`, both protected paths.
---

**Problem.** The project owner chose the exact matrix exponential over the
operator split on 2026-09-03 (`PL-SPMQ` option C). That choice forces a
representation question the split never had to answer, because the split let
each compartment own and advance its own state while a propagator advances all
six at once.

**Decision needed.** Three parts, and they are one decision:

1. **What is the state vector?** Fractions $`(F_C, F_A, F_v, F_1, F_2, F_3)`$,
   or amounts $`(M_C, M_A, M_v, M_1, M_2, M_3)`$. Both are linear with constant
   coefficients within a step, so both admit an exact exponential; the two
   matrices are similarity transforms of each other by the diagonal of
   compartment capacities.
2. **What owns the trajectory?** The compartment objects, with the solver
   reading and writing them; or the system, with the compartments reduced to
   parameters plus views onto the vector.
3. **What happens to the mass-conservation guarantee?** See below. This is the
   safety-critical part and is why the item is P1 and `science`-classed.

**Recommendation: fractions, with the amount derived per compartment.**
`docs/MODEL.md` § "Governing equations" is written in fractions, the domain's
own notation is $`F_D`$, $`F_I`$, $`F_A`$, and the whole purpose of the exact
step is that assembling the matrix *is* transcribing those equations. An
amount-based matrix would be correct and would read like nothing in the
literature. The retired harness's `build_system_matrix` already made this
choice, and its alveolar row is the worked example of why it is the right one.

The ownership half is left open deliberately: it is an architecture question
that the implementation is better placed to answer, and it interacts with
`PL-006` (clarify what `AgentUptakeSystem` actually owns).

**Why it matters — the conservation guarantee changes character.**
`docs/MODEL.md` § "Selected method (as implemented)" records that today "every
internal transfer is applied as an equal-and-opposite pair, so a wrong transfer
*rate* leaves the accounting residual at ~2e-15 L". Mass conservation is
therefore structural: the bookkeeping cannot fail to balance, which is exactly
why the document warns the residual proves less than it appears to.

A propagator has no paired transfers. Total stored agent is computed before and
after, and conservation holds only if the matrix is right. That is arguably a
*better* gate — it becomes capable of failing, which the current one is not for
this class of error — but it is a change to a safety-critical invariant and must
be made deliberately, with `AgentSimulationValidator`'s tolerance re-derived from
the new numerics rather than carried over.

**This item subsumes `PL-KZS3`,** which asked whether `BreathingCircuit` should
store the amount like the other three compartments. That question only exists
while each compartment owns its own state; parts 1 and 2 above answer it either
way, and answering the narrow version first would commit the broad one by
accident.

**Done when.** All three parts are recorded here and in `docs/MODEL.md`, and
`PL-GS5X` can be started without any representation question left open.

**Decided 2026-09-03 (project owner), all three parts as recommended.**

1. **The state vector is fractions** — $`(F_C, F_A, F_v, F_1, F_2, F_3)`$ plus
   the seventh augmented state carrying the constant fresh-gas forcing. Amounts
   are derived per compartment as capacity times fraction. The reason is the
   whole reason the exact step was chosen: `docs/MODEL.md`'s governing equations
   are written in fractions, so assembling the matrix is transcribing them, and
   an amount-based matrix would be equally correct while reading like nothing in
   the literature.
2. **Trajectory ownership is left to the implementation.** It is an architecture
   question that `PL-GS5X` is better placed to answer with the code in front of
   it, and it interacts with `PL-006` (clarify what `AgentUptakeSystem` actually
   owns). The constraint that survives regardless: whatever owns the vector,
   capture, restore and reset must round-trip it exactly, and no compartment may
   hold a second copy that can disagree with it.
3. **Mass conservation stops being structural, deliberately, and
   `AgentSimulationValidator`'s tolerance is re-derived rather than carried
   over.** Today the residual cannot fail to balance because every transfer is
   an equal-and-opposite pair, which `docs/MODEL.md` already notes is why it
   proves less than it appears to. Under a propagator the residual becomes a
   real test of whether the matrix is right — a stronger gate, because it can
   fail. `PL-GS5X` must state the new tolerance's derivation beside it, and must
   not reuse the ~2e-15 figure, which describes the old mechanism.
