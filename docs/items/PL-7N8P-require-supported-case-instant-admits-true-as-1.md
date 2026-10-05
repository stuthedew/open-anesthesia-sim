---
id: PL-7N8P
title: require_supported_case_instant admits True (as 1.0 s) and Decimal, and lets OverflowError escape for an int past the float range (CaseInstant(10**400)) rather than refusing in the simulator's words - the shape PL-LLMN records for the flows' _require_supported, so decide the two together; none is reachable from the interface (found reviewing #1354)
priority: P1
effort: S
status: done
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/supported_ranges.py, tests/unit/test_supported_ranges.py, src/anesthesia_sim/core/checked_number.py, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-10-04
closed: 2026-10-05
pr: 1373
payoff: a programming slip can no longer put an instant on the case axis as a plausible 1 s, and every refused instant is named with the supported run length in the simulator's own exception
verify: grep -q 'def test_a_case_instant_refuses_a_bool_a_decimal_and_an_overflowing_int_in_its_own_words' tests/unit/test_supported_ranges.py
---

**Problem.** require_supported_case_instant admits True (as 1.0 s) and Decimal, and lets OverflowError escape for an int past the float range (CaseInstant(10**400)) rather than refusing in the simulator's words - the shape PL-LLMN records for the flows' _require_supported, so decide the two together; none is reachable from the interface (found reviewing #1354)

**The docstrings follow the decision.** `CaseInstant`'s and
`require_supported_case_instant`'s Raises sections name only
`SimulationConfigurationError`, while a `str` raises `math.isfinite`'s own
`TypeError` and an `int` past the float range raises `OverflowError` (measured
2026-10-04 in #1354's second review pass). Whichever way this is decided, the
two docstrings are brought into line with it. `StepCount` already refuses
`bool` (`PL-CN5S`'s outcome says why), so refusing it here too would make the
two types of that slice agree.

**Reproduced 2026-10-04, at triage.** On Python 3.14.7, against `main` at
`8cc0698d`,
`uv run python -c "from decimal import Decimal; import numpy; from anesthesia_sim.core.supported_ranges import CaseInstant; print(repr(CaseInstant(True)), repr(CaseInstant(numpy.True_)), repr(CaseInstant(Decimal('2.5')))); CaseInstant(10**400)"`
printed `1.0 1.0 2.5` and then raised `OverflowError: int too large to
convert to float` from `math.isfinite` in `require_supported_case_instant`.
So `True` and `numpy.True_` were each built as an instant of 1 s and
`Decimal('2.5')` as one of 2.5 s, none of them refused, and an `int` past the
float range escaped as Python's exception instead of being refused against the
supported run length. Run the same way, `CaseInstant('2.5')` raised
`math.isfinite`'s `TypeError: must be real number, not str` and
`CaseInstant(Decimal('sNaN'))` a `ValueError` ("cannot convert signaling NaN
to float"), neither naming the instant or the span.

**Classed `safety`, and worked with `PL-LLMN`.** The refusal this needs is the
one `PL-LLMN` gives the flows' `_require_supported`, in the same file,
`core/supported_ranges.py`, so the two are best worked in one branch and worded
once; `StepCount` beside them already refuses a `bool` (`PL-CN5S`).

**Why it matters.** Nothing in the interface reaches it: the two places it
builds an instant, the fork-point selector's `selected_instant_s` and the
time-bookmark form's `entered_time_bookmark` in `app/qt_widgets.py`, each hand
`CaseInstant` a `float`. What reaches it is a caller building the type itself,
such as a notebook, a test or a value typed `Any`, which is the caller the type
exists for, and for that caller a `bool` becomes a plausible 1 s on the case's
axis - an opening, a reach, a mark or a fork - with no refusal, the silent
coercion of invalid data that `CLAUDE.md`'s safety-critical standard forbids.
An `int` past the float range, a string or a signaling NaN escapes as Python's
own exception, naming neither the instant nor the supported run length, and a
caller catching the `SimulationConfigurationError` both docstrings promise
does not catch it.

**Done when.** Built from a `bool`, `numpy.True_`, a `Decimal`
(`Decimal('sNaN')` included) or a `str`, `CaseInstant` raises a `TypeError` in
the simulator's own words, naming the value and its type, before any
comparison runs, as `PL-LLMN`'s Done when words it for the flows. Built from an
`int` past the float range, such as `10**400`, it raises the
`SimulationConfigurationError` naming the supported run length that any
instant outside the span raises, and names an `int` too long to print as
`describe_count` does. An `int` or a `float` inside the span is admitted as
today. The Raises sections of `CaseInstant` and
`require_supported_case_instant` name each exception raised and when. A test
in `tests/unit/test_supported_ranges.py` named
`test_a_case_instant_refuses_a_bool_a_decimal_and_an_overflowing_int_in_its_own_words`
pins it.
