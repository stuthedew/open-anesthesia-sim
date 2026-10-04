---
id: PL-CN5S
title: A case instant and a run's step count are a bare float and a bare int checked by hand where each enters - require_supported_case_instant at RunDefinition's two ways in, _require_step_count in SimulationState - so a new way in for either repeats the check or skips it; slice 2 of PL-51B7 gives each a checked type, CaseInstant in s and StepCount, an int subclass checking what a count can be checked for alone
priority: P2
effort: M
status: done
classes: refactor
feature: parse-dont-validate
touches: src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/simulation_view.py, tests, docs/MODEL.md, docs/ARCHITECTURE.md, .claude/rules/core-domain.md
blocked-by: PL-0YYV
added: 2026-10-04
closed: 2026-10-04
pr: 1354
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

[superseded 2026-10-04] **Was blocked by `PL-0YYV`**, slice 1, which closed in pull request 1350 on
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

**Outcome** (2026-10-04, pull request 1354). Built as specified, with four
calls taken in the build and put to the owner in the pull request for his read:

- **Instants a run is only asked about stay `float`**: `RunDefinition.state_at`,
  `segment_at`, `evaluate`, `evaluate_anchored` and the controller's drawn
  window. The run's own opening and reach bound every query, through
  `_require_within_run`, and a relation between a query and the record is the
  record's to check (`.claude/rules/core-domain.md`, "Where it stops"). Taking
  the type there would make every drawn window build two `CaseInstant`s from a
  viewport and check the span twice. What takes the type is every place an
  instant is kept or a run is moved to one.
- **`BookmarkSet.standings` loses `run_length_cap_s`.** It existed to answer a
  time bookmark past 24 h as unreachable at once; no such bookmark can be built
  now, so the parameter answered nothing and its docstring would have gone
  stale. The dialog's spin box was already capped at 86 400 s, so no learner
  could make one.
- **`StepCount` refuses `bool`**, which `SimulationState` accepted as 0 and 1.
  `2.0` is refused as before.
- **The fork panel stores plain floats as Qt `userData`** and rebuilds the
  `CaseInstant` on the way out: PySide6's `findData` matches a stored `float`
  subclass only by identity, so an equal `CaseInstant` built anew is not found
  (measured 2026-10-04, corrected by the second review pass).

Filed rather than done, being outside `touches`: `PL-RCYZ`, the control
record's instants (`ControlChange.elapsed_s`, an adjustment's start and end),
still annotated `float` though each is taken from a `CaseInstant`.

**Review passes** (three: the type boundary and state; domain invariants, what
a learner sees and whether the docs tell the truth; tests and dead code). No
wrong standing, no clinical value and no new exception a learner could reach.
Folded: a value built as another checked quantity - a `StepCount` handed in as
an instant, a `SimulationStep`, a flow - is refused by `require_case_instant`
and `require_step_count` as a swapped argument with no rebuild advice, since
`CaseInstant(StepCount(600))` would hold an instant of 600 s, and an unbuilt
value is told `CaseInstant(...)` rather than having its value echoed, which
advised `CaseInstant(True)`; `SimulationState`'s refusal of a count with no
step names a count past 4,300 digits through `describe_count` rather than
raising `ValueError`; and the docs were narrowed to the records that actually
refuse a bare value. Filed: `PL-8W1W` (`SimulationState`'s fields assignable
after construction without a check, to decide with `PL-LBQY`), `PL-7N8P`
(`CaseInstant` admits `True` and lets `OverflowError` escape, to decide with
`PL-LLMN`) and `PL-848D` (the step's and the flows' type refusals brought to
the same shape).

The third pass mutated the change and found five mutations the suite let
through: four that `mypy --strict` refuses in `src/`, and one it cannot see,
the fork panel handing `findData` the `CaseInstant` rather than its `float`,
which drops a reader's chosen fork point whenever the offer grows. That one now
has a test (`test_a_fork_instant_still_offered_stays_selected_when_the_offer_grows`),
as do three of mypy's (`test_a_state_keeps_the_checked_types_through_every_move`).
Twenty-one test lines that rebuilt an instant which was already a `CaseInstant`
were unwrapped, so those tests hold that what `fork_points_s` and a keyframe's
`instant_s` hand out, `fork_at` and `resumed_at` accept. Kept against the
pass's two nits: the seven tests that build only the type, in the test file of
the run they protect (`test_an_opening_no_case_reaches_cannot_be_built` and its
kin), because each keeps beside that run why its input is refused - a
non-finite opening would propagate `nan`, and `PL-73ZN`'s opening past the
envelope - at no cost but a duplicate of the type's own test; and
`RunDefinition`'s own `require_case_instant`, which the opening's `Keyframe`
would also refuse, so that the refusal names `opened_at_s`, the parameter the
caller used.
