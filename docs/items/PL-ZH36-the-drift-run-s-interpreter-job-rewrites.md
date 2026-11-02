---
id: PL-ZH36
title: The drift run's interpreter job rewrites requires-python and .python-version before it runs the suite, and three test_config_home_check tests added by #1765 on 2026-10-24 read the live tree, so they fail on the job's own rewrite rather than on a configuration copy anyone changed (drift run 41279184121, 2026-11-01)
priority: P2
effort: S
status: done
classes: defect
feature: drift-2026-11-01
touches: .github/workflows/drift.yml, tests/unit/test_config_home_check.py, tools/config_home_check.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-01
closed: 2026-11-02
pr: 1930
payoff: the monthly interpreter check fails only when a new CPython breaks something, not on the pin it rewrites itself
not-delegable: the proof is the next run of drift.yml's interpreter job, which rewrites the pin itself; no admitted verify shape runs it
---

**Problem.** The drift run's interpreter job rewrites requires-python and .python-version before it runs the suite, and three test_config_home_check tests added by #1765 on 2026-10-24 read the live tree, so they fail on the job's own rewrite rather than on a configuration copy anyone changed (drift run 41279184121, 2026-11-01)

**Evidence.** In the `interpreter` job of drift run 41279184121, on Python
3.15.2, three tests in `tests/unit/test_config_home_check.py` failed:
`test_the_repository_s_configuration_copies_all_match_their_homes`,
`test_every_copy_of_every_fact_is_found_in_the_repository` and
`test_a_changed_python_release_names_each_file_still_giving_the_old_one`. The
first two run the check on `REPO_ROOT`, the live tree. The job's step "relax
the interpreter pin for this run only" rewrites `requires-python` in
`pyproject.toml` to `>=3.14` before the suite runs. The third test's diff shows
the check reading that rewrite: it reports `.github/workflows/drift.yml` giving
`>=3.14,<3.16` where `>=3.14` is expected. The tests arrived with `PL-SH0W` in
`#1765` on 2026-10-24. The `interpreter` job had last run on 2026-10-19 (run
39218413328), so this run was the first to put the two together. The same
tests passed in the `dependencies` job, which does not rewrite the pin.

**Why it matters.** The `interpreter` job exists to show whether the next
CPython breaks the simulator. While three of its failures come from the job's
own rewrite, it is red every month whatever the new interpreter does. A real
break would then arrive among failures that everybody has learned to skip.

**Done when.** The `interpreter` job runs the suite without these three tests
failing on its own rewrite, and the tests still fail on a configuration copy
that really disagrees with its home. The next run of the job shows it.

**Generator check.** One-off. A check of the live tree and a job that edits the
tree before the suite each work alone, and they met for the first time in this
run.

**Closed 2026-11-02 in #1930.** The interpreter job now restores
`pyproject.toml` and `.python-version` after it rewrites them, and runs the
suite with `UV_NO_SYNC` set, so the suite uses the 3.15 environment already
built but reads the committed configuration.
`tests/unit/test_config_home_check.py::test_the_interpreter_job_puts_the_pins_back_before_its_suite`
holds that order. The proof that the job is green is the next `drift.yml` run of
the `interpreter` job, which only CI can make.
