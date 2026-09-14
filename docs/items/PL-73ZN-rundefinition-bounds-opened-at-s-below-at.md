---
id: PL-73ZN
title: RunDefinition bounds opened_at_s below at induction but not above, so a definition may declare an opening past the 24 h envelope the model is claimed over
priority: P2
effort: S
status: ready
classes: defect
feature: numerical-domain
touches: src/anesthesia_sim/core/run_definition.py, tests/unit/test_run_definition.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_run_definition.py && grep -q 'def test_opening_past_the_supported_envelope_is_refused' tests/unit/test_run_definition.py
---


**Problem.** RunDefinition bounds opened_at_s below at induction but not above, so a definition may declare an opening past the 24 h envelope the model is claimed over

**Found 2026-09-14** by an adversarial pass over `PL-ZMRT` (one
simulated-time frame), which is the change that made the question meaningful.

`RunDefinition.__init__` refuses a non-finite `opened_at_s` and one below zero,
and nothing else. Under the arrangement `PL-ZMRT` replaced, a definition's
instants were its own elapsed time and the supported run length had no business
in this module; under one frame they are absolute case instants, and
`docs/MODEL.md` § "Supported run length" is a statement about exactly that axis.

**Not reachable today, which is why it is an item rather than a fix.**
`SimulationController._resume_point_at` offers only the trunk's own keyframes,
and `SimulationState.advance` halts the trunk at
`MAXIMUM_ELAPSED_SIMULATION_TIME_S` (86 400.0 s), so no opening past the
envelope can be constructed through the application. The envelope is enforced
in one place, on the step count, and the definition side neither checks nor
needs to.

**What has to be decided before anything is added**, and it is a real
trade rather than an oversight: `core/run_definition.py` imports no
`supported_ranges` today, and the module is deliberately ignorant of the
session. A domain check here would give the envelope a second home, and
`CLAUDE.md`'s own test - a check earns its place every run, or it is retired -
is against a branch nothing can reach. The alternative is to say in the
constructor's docstring that the envelope is the step count's and not this
class's, which costs nothing and leaves one enforcement point.

Related: `PL-3LZB` was the same shape - a latent guard in this class that
nothing could reach - and it was worth landing because `PL-ZMRT` was about to
make it reachable. Nothing here is about to make this one reachable, so the
docstring answer is the likelier right one.

**Verified 2026-09-14.** `core/run_definition.py:262-267` checks `opened_at_s`
for finiteness and for `>= 0.0` - "a run opens at or after induction" - and
there is no upper bound. So a definition may declare an opening at any finite
instant, including one past the 24 h envelope the model is claimed over.

**Why it matters.** `CLAUDE.md`'s safety-critical standard asks for model
applicability to be validated *before* calculation rather than after, and this
is the boundary where a run's domain is declared. The declared opening is also
what a branch inherits, so an out-of-envelope instant does not stay in one
object: it becomes the origin of every instant the branch reports.

**Why not `safety`, stated rather than assumed.** Nothing downstream computes
from an out-of-envelope opening without refusing: the run-length guard fires on
the advancing path before any state is produced, so the failure mode is a late
error rather than a plausible wrong number. `CLAUDE.md` prefers an obvious
failure to a plausible-looking value, and the code already fails obviously - it
just fails later than the standard asks. `PL-BMY5` is the same shape one level
down, on `SimulationState`, and the two are worth doing together.

**Done when.** `RunDefinition.open` refuses an `opened_at_s` beyond the supported
run length with a message naming the envelope and the value, the bound is read
from `core/supported_ranges.py` rather than restated, and
`tests/unit/test_run_definition.py` covers both edges.
