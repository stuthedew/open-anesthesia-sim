---
id: PL-Q18P
title: An xdist worker crashed in test_a_layout_of_two_windows_is_refused on main's quality run 5949 (cc47f358), and the same test passed on the next run: AreaLayout raises ValueError from _drawable after QWidget.__init__ and QVBoxLayout(self) have run, so a half-built widget is left for the garbage collector
priority: P2
effort: S
status: done
classes: defect, test
feature: qt-teardown-crashes
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
closed: 2026-10-19
pr: 1686
payoff: A refused layout no longer leaves a half-built Qt widget that can crash a test worker and turn main red for no reason
verify: grep -q 'def test_a_refused_layout_leaves_no_widget' tests/integration/test_layout_adapter.py
---

**Problem.** An xdist worker crashed in test_a_layout_of_two_windows_is_refused on main's quality run 5949 (cc47f358), and the same test passed on the next run: AreaLayout raises ValueError from _drawable after QWidget.__init__ and QVBoxLayout(self) have run, so a half-built widget is left for the garbage collector

**What was seen.** Quality run 5949 (https://github.com/stuthedew/open-anesthesia-sim/actions/runs/39171870500), job `checks-part-2`, on `main` at cc47f358, 2026-10-18 22:26Z, ended with:

    FAILED tests/integration/test_layout_adapter.py::test_a_layout_of_two_windows_is_refused - worker 'gw1' crashed while running 'tests/integration/test_layout_adapter.py::test_a_layout_of_two_windows_is_refused'
    1 failed, 5693 passed, 2 skipped in 293.91s

The log shows no traceback, so the worker process died rather than the test failing. The next run on `main`, 5953 on 7780b0db, passed with the same test. The commit between the two changed only `.github/workflows/drift.yml` and item files, so nothing the test reaches changed. It has happened once, and nobody re-ran 5949.

**A likely mechanism, not yet confirmed.** `AreaLayout.__init__` in `src/anesthesia_sim/app/area_layout.py` calls `super().__init__(parent)` and builds `QVBoxLayout(self)` before `_drawable(model)` raises `ValueError` for a layout with two windows. The test then holds no reference, so the half-built Qt widget is destroyed by Python's garbage collector at an unpredictable moment, possibly on another test's turn. If that is the cause, checking the model before `super().__init__` removes it. The test also needs a way to reproduce the crash, for example by running it repeatedly under `-p no:randomly` with a forced `gc.collect()` after it. PySide6 has already crashed this suite once, through a different path (`PL-NDKC`).

**What a fix needs.** A reproduction, or a fix in the order of the constructor that leaves no Qt object behind when the model is refused, with a regression test showing that a refused layout creates no `QWidget`.

**Checked 2026-10-19.** `AreaLayout.__init__` in
`src/anesthesia_sim/app/area_layout.py` still calls `super().__init__(parent)`
and builds `QVBoxLayout(self)` before `_drawable(model)` can raise, so the
mechanism the brief names is present on `main`.

**Why it matters.** A worker crash turns `main` red for a reason unrelated to
any change. Under `CLAUDE.md`, a red `main` stops every session working until
the owner is told, so each recurrence costs a session and the owner's
attention.

**Done when.** `AreaLayout` checks its model before it builds any Qt object,
and a test in `tests/integration/test_layout_adapter.py` shows that a refused
layout leaves no new `QWidget` behind (for example, by comparing
`QApplication.allWidgets()` before and after).

**Done 2026-10-19.** The constructor's order was fixed by `PL-H9VT`
(`fe92980d`, #1651): `AreaLayout.__init__` calls `_drawable(model)` before
`super().__init__`. This item adds the test its Done-when asks for.
`test_a_refused_layout_leaves_no_widget_behind` keeps the refusal while it
counts `QApplication.allWidgets()`, since the refusal's traceback holds the
constructor's frame. With `super().__init__` moved back ahead of
`_drawable`, it fails with `assert 1 == 0`, naming the half-built
`AreaLayout`.
