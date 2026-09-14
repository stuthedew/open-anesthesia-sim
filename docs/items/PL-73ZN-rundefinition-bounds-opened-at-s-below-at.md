---
id: PL-73ZN
title: RunDefinition bounds opened_at_s below at induction but not above, so a definition may declare an opening past the 24 h envelope the model is claimed over
status: untriaged
added: 2026-09-14
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
