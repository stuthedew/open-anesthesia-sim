---
id: PL-ZG5J
title: Land the headless frame-cost harness that measured all of the above, so the simulation-versus-UI split can be re-measured rather than re-derived
status: untriaged
added: 2026-09-08
---

**Problem.** `PL-YSZN`, `PL-KP7H`, `PL-R2YM` and `PL-SQJ1` were all measured on
one throwaway harness: a real `SimulationController` and a real
`SimulationView` mounted on a real `flet.messaging.session.Session` whose
connection serializes each outbound message exactly as the WebSocket transport
does, driven frame by frame with `perf_counter` around each of
`controller.advance`, `_refresh_view` and `page.update()`. It answers "is this
the simulation or the interface" in about thirty seconds and needs no client,
no display and no browser.

`PL-0VM7`, `PL-Q197` and `PL-R460` each built something equivalent and each
discarded it; this is the fourth time the same scaffolding has been written.
`CLAUDE.md` asks for work that recurs to be moved out of the model.

**What is unresolved is where it goes.** New `tools/` scripts are required to
be standard-library only, so a hook or a bare checkout can run them without
the project virtualenv, and this one imports `flet`, `flet_charts`, `msgpack`
and the package itself. It is also not a check: it produces timings, which are
a judgment rather than a pass/fail, and `CLAUDE.md` is explicit that a check
which cannot decide is worse than none. So it is a third thing — a measurement
script — and the project has no home for one.

**Why it matters.** Modest. Nothing is blocked on it, and the argument against
is that the project's precedent is to measure ad hoc and record the numbers in
the item, which does preserve the finding. The argument for is that the
*method* is what gets re-derived, and it is subtle enough to get wrong: the
serializing connection is what puts the session into the state an incremental
patch is computed against, and a stand-in that skipped it would answer a
question the running app never asks.

**Decision needed.** Whether a measurement script has a home in this
repository — `tests/benchmarks/`, a `bench/` tree, or nowhere — and whether the
stdlib-only rule is a property of `tools/` or of anything runnable.

**First step.** Answer that, or close this as declined and record in
`docs/WORKING_NOTES.md` that measuring ad hoc is deliberate.
