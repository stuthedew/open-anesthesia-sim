---
id: PL-H9VT
title: AreaLayout builds its QWidget before refusing a layout of two windows, so the refusal test aborts a pytest worker with no QApplication and turns main red
status: done
added: 2026-10-19
closed: 2026-10-19
payoff: main's test run no longer fails on whichever run happens to schedule the two-window refusal test first on a fresh worker
verify: grep -q 'drawable = _drawable(model)' src/anesthesia_sim/app/area_layout.py
---

**Problem.** `AreaLayout.__init__` called `QWidget.__init__` before `_drawable` refused a layout of two windows. `test_a_layout_of_two_windows_is_refused` in `tests/integration/test_layout_adapter.py` takes no `application` fixture, so on a pytest-xdist worker that had not yet built a `QApplication`, Qt aborted the whole worker ("QWidget: Must construct a QApplication before a QWidget"). That crash turned main's quality run #6137 on `a408e4c9` red (https://github.com/stuthedew/open-anesthesia-sim/actions/runs/39247296380). It depends on test order, so it fails on whichever run happens to schedule that test first on a worker.

**Fix.** Refuse the layout before the widget is built. The refusal then needs no `QApplication`, which is what the test always assumed, and nothing is left half-built.

**Regression check.** Before the fix, `pytest tests/integration/test_layout_adapter.py::test_a_layout_of_two_windows_is_refused` run alone aborts with `Fatal Python error: Aborted` at `area_layout.py` line 379, exit 134. After it, the same command passes.
