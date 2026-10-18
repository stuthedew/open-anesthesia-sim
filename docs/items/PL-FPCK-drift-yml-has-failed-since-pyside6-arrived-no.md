---
id: PL-FPCK
title: drift.yml has failed since PySide6 arrived: no job installs libegl1, the interpreter job deletes the tracked .python-version that a test lists, and it never reaches a new CPython
priority: P2
effort: S
status: done
classes: infra
touches: .github/workflows/drift.yml
added: 2026-10-18
closed: 2026-10-18
pr: 1596
payoff: every drift.yml job reaches its test results on an unchanged tree, so a red run means a dependency, a new interpreter or a test order broke the suite, and not the runner
verify: grep -q 'check-latest: true' .github/workflows/drift.yml && grep -q 'Qt.s system libraries, for the offscreen platform plugin' .github/workflows/drift.yml && grep -q 'version_info.:3.). > .python-version' .github/workflows/drift.yml && ! grep -q 'rm -f .python-version' .github/workflows/drift.yml
---

**Problem.** The only scheduled `drift` run since the Qt port,
[run 36822855719](https://github.com/stuthedew/open-anesthesia-sim/actions/runs/36822855719)
on 2026-10-01, failed in both jobs. Nobody looked at it for 17 days. It had
two causes, and neither was the drift that the workflow exists to find.

1. **No job installs `libegl1`.** Qt's offscreen platform plugin links
   `libEGL.so.1`, and `ubuntu-latest` does not carry it. `PL-VHLZ` added the
   `apt-get install -y libegl1` step to `quality.yml` on 2026-09-14 and did not
   add it to `drift.yml`. So seven test modules that import `PySide6.QtGui` fail
   at collection in every job: 5463 passed, 7 errors in `dependencies`. The
   `order` job, added by `PL-75D9` on 2026-10-17, has the same gap. Its first
   weekly run is on Monday 2026-10-19, so it would have failed every week.
2. **The interpreter job deletes a tracked file.** The job removes
   `.python-version` so that uv uses the newer interpreter that setup-python
   installed. `tests/unit/test_workflow_paths_check.py::test_a_checkout_is_listed_by_git_rather_than_walked`
   asserts that the first 50 files `git ls-files` lists all exist, and
   `.python-version` is the 50th. So the job fails a test that passes on every
   other runner.

3. **The interpreter job never reached a new CPython.** `setup-python`'s
   `check-latest` defaults to false, so `python-version: '3.x'` takes the
   newest version already on the runner image. A run on this branch on
   2026-10-18 tested 3.14.8, while `actions/python-versions` already listed
   3.15.0 as stable. The job's own comment says '3.x' is "the version this job
   exists to try", so this is a gap against its stated intent, and the runner
   image can lag a new minor release by weeks.

The seven modules that never ran on 2026-10-01 may hide other failures. Only a
run with these fixes can say.

**Why it matters.** `drift.yml` is the only thing that notices when a
dependency release or a new CPython breaks this tree. While it fails on its own
setup, a red run carries no news, so a real break would arrive looking exactly
like the failures here and be ignored the same way. The header of the file
says that a check that is red as routine should be retired. This item fixes the
check so that the retirement question is asked about a check that works.

**Fix.**

- Add `quality.yml`'s `libegl1` step to each of the three jobs.
- In the interpreter job, overwrite `.python-version` with the version of the
  interpreter that setup-python installed, instead of deleting the file. uv
  still uses that interpreter, and the tracked file still exists.
- Set `check-latest: true` on the interpreter job's `setup-python` step.

**Done when.** The `verify:` line holds, and a `workflow_dispatch` run of
`drift.yml` on the branch gets past test collection in all three jobs. Any test
that still fails is a drift finding to capture, not a defect of this item.

**Closed 2026-10-18.** On this branch,
[run 39157643905](https://github.com/stuthedew/open-anesthesia-sim/actions/runs/39157643905)
passed all three jobs: `dependencies` and `interpreter` each ran 9,352 tests,
mypy was clean, and `uv pip list --outdated` named no release beyond a declared
bound. That run's interpreter job still tested 3.14.8, which led to the
`check-latest` fix. With that fix,
[run 39159017258](https://github.com/stuthedew/open-anesthesia-sim/actions/runs/39159017258)
tested CPython 3.15.0 against the pinned 3.14. Its interpreter job passed:
9,352 tests passed and 2 were skipped. Whether to move the pin is
`PL-J0P8`'s question, not this item's.
