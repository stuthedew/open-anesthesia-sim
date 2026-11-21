---
id: PL-YKQP
title: The closing check refuses a test that gained a parameter set through a module-level table: done.test_code reads only the test function's own lines, so adding an entry to FIGURES in tests/reference/test_mac_awake_washout_figures.py counts as an unchanged test, and PL-7M65 cannot close with the test that shows its work
priority: P2
effort: S
status: done
classes: defect
feature: standing-weight
touches: subprojects/docket/src/docket/done.py, subprojects/docket/tests/test_done.py, subprojects/docket/README.md
added: 2026-11-21
closed: 2026-11-21
pr: 2202
payoff: a session can close an item on the table-driven test that shows its work, so a new reference case never has to be recorded a weaker way
tests: subprojects/docket/tests/test_done.py::test_a_case_added_to_the_table_a_test_reads_is_a_change, subprojects/docket/tests/test_done.py::test_a_change_reached_through_the_table_is_a_change, subprojects/docket/tests/test_done.py::test_a_module_change_the_test_does_not_use_is_no_change, subprojects/docket/tests/test_done.py::test_a_changed_fixture_or_helper_the_test_uses_is_a_change, subprojects/docket/tests/test_done.py::test_a_changed_method_of_the_test_s_own_class_is_a_change_when_it_is_used
---

**Problem.** The closing check refuses a test that gained a parameter set through a module-level table: done.test_code reads only the test function's own lines, so adding an entry to FIGURES in tests/reference/test_mac_awake_washout_figures.py counts as an unchanged test, and PL-7M65 cannot close with the test that shows its work

**Found 2026-11-21**, closing `PL-7M65` on `claude/project-thread-1sjsjg` (#2201). `bin/docket set PL-7M65 --status done --tests tests/reference/test_mac_awake_washout_figures.py::test_the_mac_awake_washout_figures_match_the_model` refused with "names a test this branch neither added nor changed, so it passed before the work and shows nothing about it". The branch added the entry "maintenance vessel-rich MAC" to the module-level `FIGURES` table, which `@pytest.mark.parametrize("figure", list(FIGURES))` turns into a new case of that test, and the case fails when the printed figure is edited. `test_code` in `subprojects/docket/src/docket/done.py` collects only the lines whose `places` value is the test's name, and a module-level assignment's place is `""`. Naming the case instead is refused by `node_refusal` ("names one parameter set"). So no form of `tests:` can record this work, and a `verify:` search of a Python file is refused too.

**Why it matters.** A table-driven test is this repository's usual way to add a reference case, and the safety-critical standard asks for one each time a displayed figure is pinned to the model. A check that refuses that work blocks the closing of correct product work, here `PL-7M65`, and leaves the session no form of `tests:` that it accepts.

**Done when.** `bin/docket set --status done --tests` accepts a test whose own lines are unchanged when a module-level table, fixture or helper in its file that it uses has changed. It still refuses a test whose own code and whatever it uses in its file are both unchanged.

**Generator check.** The fact misread is which code a named test runs. `PL-FN11`'s reader took it to be the test function's own lines. No head's `misread:` states that fact, and no other item misread it, so this is a one-off, found at the check's first use on a table-driven test on the day `PL-FN11` landed.

**A possible fix.** Count a test as changed when a module-level statement or top-level definition that its own code names has changed, one level deep. The trade-off is that a branch which changes a shared helper then gets credit for every test that calls it.
