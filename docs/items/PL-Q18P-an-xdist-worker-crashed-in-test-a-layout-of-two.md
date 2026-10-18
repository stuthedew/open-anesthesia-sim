---
id: PL-Q18P
title: An xdist worker crashed in test_a_layout_of_two_windows_is_refused on main's quality run 5949 (cc47f358), and the same test passed on the next run: AreaLayout raises ValueError from _drawable after QWidget.__init__ and QVBoxLayout(self) have run, so a half-built widget is left for the garbage collector
status: untriaged
added: 2026-10-18
---

**Problem.** An xdist worker crashed in test_a_layout_of_two_windows_is_refused on main's quality run 5949 (cc47f358), and the same test passed on the next run: AreaLayout raises ValueError from _drawable after QWidget.__init__ and QVBoxLayout(self) have run, so a half-built widget is left for the garbage collector

**What was seen.** Quality run 5949 (https://github.com/stuthedew/open-anesthesia-sim/actions/runs/39171870500), job `checks-part-2`, on `main` at cc47f358, 2026-10-18 22:26Z, ended with:

    FAILED tests/integration/test_layout_adapter.py::test_a_layout_of_two_windows_is_refused - worker 'gw1' crashed while running 'tests/integration/test_layout_adapter.py::test_a_layout_of_two_windows_is_refused'
    1 failed, 5693 passed, 2 skipped in 293.91s

The log shows no traceback, so the worker process died rather than the test failing. The next run on `main`, 5953 on 7780b0db, passed with the same test. The commit between the two changed only `.github/workflows/drift.yml` and item files, so nothing the test reaches changed. It has happened once, and nobody re-ran 5949.

**A likely mechanism, not yet confirmed.** `AreaLayout.__init__` in `src/anesthesia_sim/app/area_layout.py` calls `super().__init__(parent)` and builds `QVBoxLayout(self)` before `_drawable(model)` raises `ValueError` for a layout with two windows. The test then holds no reference, so the half-built Qt widget is destroyed by Python's garbage collector at an unpredictable moment, possibly on another test's turn. If that is the cause, checking the model before `super().__init__` removes it. The test also needs a way to reproduce the crash, for example by running it repeatedly under `-p no:randomly` with a forced `gc.collect()` after it. PySide6 has already crashed this suite once, through a different path (`PL-NDKC`).

**What a fix needs.** A reproduction, or a fix in the order of the constructor that leaves no Qt object behind when the model is refused, with a regression test showing that a refused layout creates no `QWidget`.
