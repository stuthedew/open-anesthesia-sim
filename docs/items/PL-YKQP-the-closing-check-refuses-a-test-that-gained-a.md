---
id: PL-YKQP
title: The closing check refuses a test that gained a parameter set through a module-level table: done.test_code reads only the test function's own lines, so adding an entry to FIGURES in tests/reference/test_mac_awake_washout_figures.py counts as an unchanged test, and PL-7M65 cannot close with the test that shows its work
status: untriaged
touches: subprojects/docket/src/docket/done.py, subprojects/docket/tests/test_done.py
added: 2026-11-21
---

**Problem.** The closing check refuses a test that gained a parameter set through a module-level table: done.test_code reads only the test function's own lines, so adding an entry to FIGURES in tests/reference/test_mac_awake_washout_figures.py counts as an unchanged test, and PL-7M65 cannot close with the test that shows its work

**Found 2026-11-21**, closing `PL-7M65` on `claude/project-thread-1sjsjg` (#2201). `bin/docket set PL-7M65 --status done --tests tests/reference/test_mac_awake_washout_figures.py::test_the_mac_awake_washout_figures_match_the_model` refused with "names a test this branch neither added nor changed, so it passed before the work and shows nothing about it". The branch added the entry "maintenance vessel-rich MAC" to the module-level `FIGURES` table, which `@pytest.mark.parametrize("figure", list(FIGURES))` turns into a new case of that test, and the case fails when the printed figure is edited. `test_code` in `subprojects/docket/src/docket/done.py` collects only the lines whose `places` value is the test's name, and a module-level assignment's place is `""`. Naming the case instead is refused by `node_refusal` ("names one parameter set"). So no form of `tests:` can record this work, and a `verify:` search of a Python file is refused too.

**A possible fix.** Count a test as changed when a module-level statement or top-level definition that its own code names has changed, one level deep. The trade-off is that a branch which changes a shared helper then gets credit for every test that calls it.
