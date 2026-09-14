---
id: PL-H27D
title: The completeness pass over PL-ZMRT found the accumulator claim false in three places and the retired frame language in five more, all outside what that item's own sweep reached
priority: P2
effort: S
status: done
classes: docs
feature: scenario-branching
touches: src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/app/chart_time_base.py, tests/unit, tests/integration, docs/items
added: 2026-09-14
closed: 2026-09-14
pr: 574
verify: python3 tools/doc_check.py check && grep -q 'cumulative from the start of the \*case\*' src/anesthesia_sim/core/run_definition.py
---

**Problem.** The completeness pass over PL-ZMRT found the accumulator claim false in three places and the retired frame language in five more, all outside what that item's own sweep reached

**Found by a completeness critic** run over the five surveys that mapped
`PL-ZMRT` (open a branch's run definition at the fork instant). Each survey
individually missed what follows; the critic's job was to ask what none of them
opened.

**The safety-critical one, in three copies.** `Keyframe`'s two accumulators
were documented as "cumulative from the start of the run it belongs to". They
are cumulative from the start of the *case*: a branch opens carrying its
parent's running totals, which is precisely what leaves it anything to carry,
so the sentence contradicted itself as well as the code. It was already false
before `PL-ZMRT` - a branch's keyframe carried the parent's litres whatever
instant it was stamped at - but that item's own constructor `Args` block now
states the correct version, so `core/run_definition.py` had come to disagree
with itself twenty lines apart. The claim is a statement about the
mass-balance readout, which is a displayed clinical value.
Corrected identically in `core/uptake_system.py`, `Keyframe.state` and
`tests/unit/test_resume_at.py`.

**Five more described the frame `PL-ZMRT` removed.** The sub-fork refusal's
test docstring still gave the retired reason while its source had been
rewritten to the surviving one, so one live guard carried two contradictory
justifications. `test_a_branch_s_drawn_window_is_on_the_case_s_axis` is the
suite's original exercise of the opening clamp and said nothing about it.
`chart_time_base.tick_times`, `test_anchored_columns_land_on_multiples_of_the_spacing`
and a `test_simulation_view` comment all still anchored the grid to "the run's
start" - contradicting `docs/MODEL.md` and, after the previous commit, the
`evaluate_anchored` docstring they describe.

**The miss that would have cost a decision is `PL-B8MK`** (a bookmark instant
is not forkable), which is open and in v0.5.0's Required scope. It prices two
routes against each other and bills the route it already recommends for four
edits; two of those are now deleted (`origin_s` and its readers) or already
paid (`drawn_window` clips at the run's opening). Re-priced in place at two
named edits, with the original paragraph kept as what the measurement was
weighed against rather than rewritten away.

**`PL-J2TD` and `PL-TFX5` carry dated amendments.** Both are closed and
accurate as records of what shipped, and both point at prose that now says the
opposite. `PL-J2TD`'s `verify:` command stopped resolving when the test it
greps for was renamed, and is deliberately left alone: a closed command is the
record of an experiment that was performed, and re-pointing one manufactures a
false provenance where there was a true one.

**Captured rather than fixed:** `PL-59WB` (`chart_time_base.fit_to_run` takes
`run_length_s` and is handed a case instant - the same defect the `duration_s`
rename removed, surviving one module over).
