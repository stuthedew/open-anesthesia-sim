---
id: PL-R74V
title: Under the drift run's upgraded pytest, test_a_predicted_wash_in_that_stops_ends_in_a_dot_as_the_run_s_does raises TypeError: pytest.approx() does not support nested data structures, because it compares a list of (instant, ratio) tuples in one approx call (drift run 41279184121, 2026-11-01)
status: untriaged
feature: restated-constants
added: 2026-11-01
---

**Problem.** Under the drift run's upgraded pytest, test_a_predicted_wash_in_that_stops_ends_in_a_dot_as_the_run_s_does raises TypeError: pytest.approx() does not support nested data structures, because it compares a list of (instant, ratio) tuples in one approx call (drift run 41279184121, 2026-11-01)

**Evidence.** Failed in the `dependencies` job of drift run 41279184121 with
`full sequence: [(352.0, 1.0078065732700932)]`. It passes on `uv.lock`.

**Generator check.** One-off: a test helper call that a newer pytest refuses.
