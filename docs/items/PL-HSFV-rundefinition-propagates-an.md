---
id: PL-HSFV
title: RunDefinition propagates an UptakeEquationSettings whose flows are outside the supported ranges - cardiac output 1000 L/min, a hundred times the supported maximum, ran on 2026-10-04 - because the settings record checks only that the tissue flows sum to cardiac output, and the range guards run only in the compartments' constructors and setters, which a run built from a settings record never calls
priority: P1
effort: S
status: ready
classes: defect, safety
feature: numerical-domain
touches: src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/run_definition.py, tests/unit/test_governing_equations.py, tests/unit/test_run_definition.py, docs/MODEL.md, ROADMAP.md
added: 2026-10-04
payoff: a run built from a settings record is refused outside the supported flow ranges exactly as a control change is, so no caller - a notebook today, a saved-run loader later - can get a precise-looking trace for a patient the model does not represent
verify: grep -q 'def test_a_run_cannot_open_or_change_under_a_flow_outside_the_supported_ranges' tests/unit/test_run_definition.py && grep -q 'def test_rejects_a_flow_outside_its_supported_range' tests/unit/test_governing_equations.py
---

**Problem.** RunDefinition propagates an UptakeEquationSettings whose flows are outside the supported ranges - cardiac output 1000 L/min, a hundred times the supported maximum, ran on 2026-10-04 - because the settings record checks only that the tissue flows sum to cardiac output, and the range guards run only in the compartments' constructors and setters, which a run built from a settings record never calls

**Measured 2026-10-04**, reproduced on `main` at `45f8e9f3` under Python
3.14.7, from the settings `AgentUptakeSystem.for_agent("sevoflurane")` holds
with 2% dialled, rebuilt with `dataclasses.replace`:

- cardiac output 1000 L/min, the three tissue flows scaled to sum to it:
  `RunDefinition(...)` opened, and after `advance_to(60.0)` its `state_at(60.0)`
  returned an inspired fraction of 0.007423 and an alveolar fraction of
  0.000265;
- fresh gas flow 500 L/min: 0.019926 and 0.010674 at 60 s;
- alveolar ventilation 200 L/min: 0.006444 and 0.006299 at 60 s;
- the second way into a run, `record_change` to that 1000 L/min cardiac output
  at 30 s, was recorded too, and gave an alveolar fraction of 0.000264 at 60 s.

So all three flows, not cardiac output alone, and both of `RunDefinition`'s
entry points. `docs/MODEL.md` § "Supported input ranges" says a flow reaches
the model through `AgentUptakeSystem`, a compartment or a compartment's
constructor, and that "the compartment is the only point all three pass
through". The settings record is a fourth way in, and no compartment sees it.

**Why it matters.** The safety-critical standard prefers an obvious failure to
a plausible number, and `docs/MODEL.md` § "What a setting outside the range
costs" says the exact step makes an out-of-range answer worse rather than
better: a precise concentration for a patient nobody has, with nothing on
screen inviting doubt. Nothing in the application reaches it today, because
`app/controller.py` builds every run definition from
`AgentUptakeSystem.equation_settings()`, whose compartments refuse such a flow.
A direct caller - a notebook, a test - does, and so would the first path that
builds a run from a stored record instead of from compartments, such as a saved
run restored by a deserializer, which `RunDefinition.advance_to`'s docstring
already anticipates.

**Done when.** `PL-51B7`'s slice 1 has landed: `UptakeEquationSettings` types
its three flow fields with checked flow types, as `SimulationStep` is for the
step, so a record holding a flow outside its supported range cannot be built and
neither `RunDefinition(...)` nor `record_change` can be handed one; regression
tests replay the reproduction above for all three flows at both entry points,
and pin both endpoints and the first value past each maximum; and
`docs/MODEL.md` § "Supported input ranges" says where each range is enforced.

**Not in scope: the delivered concentration.** The same route carries a dial
above the agent's vaporizer maximum, but the record holds no agent and no
maximum to check it against, so closing it is a decision about what a run
definition records rather than a guard to add: `PL-BBMG`.

**Gate.** Captured after v0.6.0's debt gate froze, and `safety`-classed, so it
joins that gate's frozen list under the exception that admits a `safety`
finding whenever it is made, as `PL-5291` did; `ROADMAP.md` records it in the
product lane.

**Recommended fix, 2026-10-04: slice 1 of `PL-51B7`, not a check of its
own.** **Recommendation:** close this with `PL-51B7`'s first slice. That slice
types `UptakeEquationSettings`'s three flow fields, so a record holding an
out-of-range flow cannot be built. The narrow alternative, recommended when
this was filed, was a range check added to the record's `__post_init__`. It
is withdrawn, because the typed fields would delete it, and this project does
the durable fix once rather than the cheap one twice. Until the slice lands,
the gap stands. The application never builds a run this way, since its flows
come through the compartments' checked setters, but a notebook or a test can,
and it gets finite, plausible numbers from outside the range the model is
claimed over.

**Rebuilding as `PL-51B7`'s slice 1, 2026-10-04** (project owner, 2026-10-04,
over the range check in `__post_init__` that pull request 1342 built first).
That check, with its tests, was `c48a99be`, and `a8007351` reverted it whole.
**The Ship v0.6.0 project builds the slice** (project owner, 2026-10-04, over
building it on 1342), with the rest of the `parse-dont-validate` feature on
v0.6.0's gate; 1342 merged as records only, and this item's claim was yielded
for the slice's builder. Next, for that builder:

1. Claim the item that carries slice 1 and this one, and read `PL-51B7`'s
   brief for the design and the call-site count.
2. Carry `c48a99be`'s tests over in the slice's form. Fetch it with
   `git fetch origin pull/1342/head`, since its branch may be gone:
   `test_a_run_cannot_open_or_change_under_a_flow_outside_the_supported_ranges`
   and `test_rejects_a_flow_outside_its_supported_range`, the two names this
   item's `verify:` greps for, and
   `test_rejects_tissue_flows_that_do_not_sum_to_cardiac_output`'s mismatch
   moved inside the supported range, since 1.5 times 7.8 L/min is past it.
3. Revise `docs/MODEL.md` § "Supported input ranges" for where each range is
   then enforced: it still says the compartment is "the only point all three
   pass through", which this item's settings record disproves.
4. Close this item with the slice.
