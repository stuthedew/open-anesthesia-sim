---
id: PL-CN5S
title: A case instant and a run's step count are a bare float and a bare int checked by hand where each enters - require_supported_case_instant at RunDefinition's two ways in, _require_step_count in SimulationState - so a new way in for either repeats the check or skips it; slice 2 of PL-51B7 gives each a checked type, CaseInstant in s and StepCount, an int subclass checking what a count can be checked for alone
priority: P2
effort: M
status: ready
classes: refactor
feature: parse-dont-validate
touches: src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/simulation_view.py, tests, docs/MODEL.md, .claude/rules/core-domain.md
blocked-by: PL-0YYV
added: 2026-10-04
payoff: no record or function can hold a case instant past the 24-hour run length, or a step count that is not a whole nonnegative number, so a new way in for either is checked without anyone remembering to
verify: grep -q 'opened_at_s: CaseInstant' src/anesthesia_sim/core/run_definition.py && grep -q 'step_count: StepCount' src/anesthesia_sim/core/simulation.py
---

**Problem.** A case instant and a run's step count are a bare float and a bare int checked by hand where each enters - require_supported_case_instant at RunDefinition's two ways in, _require_step_count in SimulationState - so a new way in for either repeats the check or skips it; slice 2 of PL-51B7 gives each a checked type, CaseInstant in s and StepCount, an int subclass checking what a count can be checked for alone

**Why it matters.** A case instant is bounded by the 24-hour run length the model
is claimed over (`docs/MODEL.md` § "Supported run length"). `RunDefinition`
checks it by hand where a run opens and where it advances, and `PL-73ZN`, closed
2026-10-03, was this pattern's last leak: the opening was bounded below and not
above. `app/bookmarks.py` and the instants a run is moved to take a bare
`float`. A step count is checked whole and nonnegative by `simulation.py`'s
`_require_step_count`, in one place, so a second holder of a count would have to
know to call it.

**What it is.** `PL-51B7`'s slice 2, as that item specifies it (project owner,
2026-10-04, ratified):

- `CaseInstant`, in s: a `float` subclass built only through
  `require_supported_case_instant`, for `RunDefinition`, `app/bookmarks.py` and
  the instants a run is moved to. 15 annotated `float` signatures and fields
  take an instant across `run_definition.py`, `supported_ranges.py` and
  `app/bookmarks.py`, counted 2026-10-04 by name, so a floor.
- `StepCount`: an `int` subclass checking what a count can be checked for alone,
  whole and nonnegative, which `_require_step_count` checks today. A count's
  supported range depends on the step, so `SimulationState` keeps checking the
  pair.
- A runtime check at each public entry point that refuses a bare value, as for
  the step and the flows.
- `docs/MODEL.md` says where each is enforced.

**Was blocked by `PL-0YYV`**, slice 1, which closed in pull request 1350 on
2026-10-04. The two slices share no code, since the quantities are
independent. They do share files, `app/controller.py`, `docs/MODEL.md` and
the tests, and the owner set the order: three slices, each green on its own,
run in order (`PL-51B7`) - so this one starts once 1350 has merged.

**Done when.** `CaseInstant` and `StepCount` exist and are built only through
their checks; `RunDefinition`'s instants, `app/bookmarks.py`'s and the instants a
run is moved to take `CaseInstant`; `SimulationState.step_count` takes
`StepCount`; each public entry point refuses a bare value at runtime; and
`docs/MODEL.md` says where each is enforced.

**Gate.** On v0.6.0's frozen list, in the product lane, with the rest of the
`parse-dont-validate` feature (project owner, 2026-10-04).
