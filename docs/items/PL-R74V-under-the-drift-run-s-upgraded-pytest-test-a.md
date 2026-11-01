---
id: PL-R74V
title: Under the drift run's upgraded pytest, test_a_predicted_wash_in_that_stops_ends_in_a_dot_as_the_run_s_does raises TypeError: pytest.approx() does not support nested data structures, because it compares a list of (instant, ratio) tuples in one approx call (drift run 41279184121, 2026-11-01)
priority: P2
effort: S
status: ready
classes: defect, test
feature: drift-2026-11-01
touches: tests/integration/test_qt_chart.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-01
payoff: the monthly dependency check stops failing on a test that a newer pytest refuses, so its next red result names a real break
verify: ! grep -qF 'preview_terminus_points(0) == pytest.approx(ended)' tests/integration/test_qt_chart.py
---

**Problem.** Under the drift run's upgraded pytest, test_a_predicted_wash_in_that_stops_ends_in_a_dot_as_the_run_s_does raises TypeError: pytest.approx() does not support nested data structures, because it compares a list of (instant, ratio) tuples in one approx call (drift run 41279184121, 2026-11-01)

**Evidence.** Failed in the `dependencies` job of drift run 41279184121 with
`full sequence: [(352.0, 1.0078065732700932)]`. It passes on `uv.lock`.

**Reproduced 2026-11-01.** Under pytest 9.2.0, comparing
`[(352.0, 1.0078065732700932)]` with `pytest.approx` of the same list raises
`TypeError: pytest.approx() does not support nested data structures`. Under
pytest 9.1.1, the version in `uv.lock`, the same comparison returns `True`, and
the test passes in this container. The drift run's `interpreter` job, on
Python 3.15.2, failed on this test too.

**Why it matters.** The drift run's `dependencies` and `interpreter` jobs stay
red until this test changes, and `uv.lock` cannot take pytest 9.2. A job that
stays red for a known reason hides the next upgrade that breaks something real.

**Done when.** The assertion in
`test_a_predicted_wash_in_that_stops_ends_in_a_dot_as_the_run_s_does` in
`tests/integration/test_qt_chart.py` no longer passes a list of tuples to one
`pytest.approx` call. It compares each instant and each ratio with the same
tolerance as before, and the test passes under pytest 9.2.0 and 9.1.1.

**Generator check.** One-off: a test helper call that a newer pytest refuses.
