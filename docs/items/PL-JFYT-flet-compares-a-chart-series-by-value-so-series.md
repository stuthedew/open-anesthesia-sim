---
id: PL-JFYT
title: Flet compares a chart series by value, so 'series in chart.data_series' and list.index answer for the first of an equal pair - invisible while one run drew each compartment once
priority: P2
effort: S
status: dropped
classes: test, defect
feature: teachable-case
touches: src/anesthesia_sim/app/chart_series.py, tests/unit/test_simulation_view.py
added: 2026-09-14
closed: 2026-09-15
reason: The Flet chart, whose series compared by value, left with PL-25KS on 2026-09-15; the Qt tests compare pyqtgraph items by identity and no port test reads a series by value
---


**Problem.** Flet compares a chart series by value, so 'series in chart.data_series' and list.index answer for the first of an equal pair - invisible while one run drew each compartment once

Found while building `PL-B9PY`'s two-run tests, 2026-09-14. Two `RunView`s
drawing the same recorded history produce two `fch.LineChartData` objects with
identical points, and `list.index` returned the *same* index for both, so an
assertion about the drawing order read as "these two lines are at the same
position" rather than failing loudly. The tests were rewritten to compare by
`id()`; nothing in the shipped code searches the list by value today.

**Why it matters.** It is a silent-wrong-answer shape rather than a crash. Any
`series in chart.data_series` test passes as soon as *some* equal series is on
the chart, which is exactly the assertion a reviewer would read as "this run's
line is drawn". Several tests already written that way were correct only
because one run drew each compartment exactly once, so no two series were ever
equal - a property this decomposition removes. `PL-8PSW` (overlay two branches
on one time axis) is the item that will make two-run drawing routine, so this
is worth settling before the assertions multiply.

**Where.** `tests/unit/test_simulation_view.py`, wherever a series is looked
for in `_concentration_chart.data_series` or `_wash_in_chart.data_series`;
`src/anesthesia_sim/app/simulation_view.py`'s `_chart_data_series` and
`_wash_in_chart_data_series` are what build the lists.

**Measured, so this is not a guess.** Against the shipped `flet-charts`,
`fch.LineChartData` is a dataclass and carries a generated
`LineChartData.__eq__` - `dataclasses.is_dataclass` is true and
`type(series).__eq__.__qualname__` is `LineChartData.__eq__`, over
`flet.controls.base_control.BaseControl` and `object`. Two freshly built
series with the same colour and stroke width compare equal while not being
identical, and `[a, b].index(b)` returns `0`.

**Open question.** Whether the right answer is a test helper that searches by
identity, a note in `chart_series.py` that a chart series must never be looked
up by value, or both - and whether the same hazard reaches the *other* Flet
control lists a frame assembles.

**Done when.** No assertion in the view tests can pass because a *different*
run's line happened to be equal to the one it asked about, and the reason is
recorded where the next person writing such an assertion will read it.

**Decision needed.** Which of three mechanisms stops a chart series ever being
searched for by value, now that `PL-B9PY`'s decomposition makes two equal series
possible. The brief's own "Open question" above names them; this records what
each costs so the question can be answered in one read.

1. **A test helper that searches by identity.** Cheapest, and it fixes the
   assertions that exist. It does not stop the next test being written the
   wrong way, so it relies on review catching it every time.
2. **A note in `chart_series.py` that a chart series must never be looked up by
   value.** Free, and it puts the reasoning where the lists are built - but a
   note is not a check, and `CLAUDE.md` prefers the decidable half be moved into
   code wherever it can be.
3. **A check that fails a test file using `in` or `.index` against
   `data_series`.** The only one that holds after the people who remember this
   have gone. It is also the one that can be wrong: a legitimate membership test
   would be refused, and `CLAUDE.md` warns that a check firing without changing
   a decision is itself a defect.

**This is a session's call rather than the project owner's** - it rests on what
the code should look like, not on what the project is for - so whoever picks it
up should choose, say why, and record the rejected two.

**The measurement is sound and does not need redoing.** `fch.LineChartData` is a
dataclass carrying a generated `__eq__`; two freshly built series with the same
colour and stroke width compare equal while not being identical, and
`[a, b].index(b)` returns `0`.

**Why P2 rather than P3.** Nothing shipped searches by value today, so nothing
is currently wrong. What makes it worth doing before `PL-8PSW` - overlay two
branches on one time axis - is that `PL-8PSW` is what makes two equal series
routine, and every assertion written between now and then is written against a
property that is about to stop holding.

**Dropped 2026-09-15, with `PL-25KS`.** The defect was Flet's: `fch.LineChartData`
compared by value, so a test's `list.index` over two equal series answered for
the first. The dashboard and its chart are on pyqtgraph now, the Flet series
module and its tests are deleted, and the port's tests read items by identity
(`ConcentrationChart.drawn_points(run, quantity)` addresses a run's own curve).
Nothing remains for this item to guard.
