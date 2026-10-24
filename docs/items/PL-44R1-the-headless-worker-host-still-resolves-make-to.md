---
id: PL-44R1
title: The headless worker host still resolves make to /usr/bin/make (GNU Make 3.81), so make check fails the two GNU make comparison tests in tests/unit/test_makefile_reference.py on every worker run after PL-TSH9 closed, and no worker there can report the gate green
priority: P2
effort: S
status: ready
classes: defect
feature: worker-runs
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py
added: 2026-10-20
payoff: a worker run on a host with an old make or bash is refused before it spends credit, instead of reporting a red gate it cannot explain
verify: grep -q 'def test_an_old_make_on_path_is_refused_before_any_spend' tests/unit/test_headless_worker.py
reenters: PL-TSH9
---

**Problem.** The headless worker host still resolves make to /usr/bin/make (GNU Make 3.81), so make check fails the two GNU make comparison tests in tests/unit/test_makefile_reference.py on every worker run after PL-TSH9 closed, and no worker there can report the gate green

Observed 2026-10-20 by the headless worker on `PL-70M6`. `make check` exited 2. pytest reported "2 failed, 10103 passed, 3 skipped". The two failures were `test_the_makefile_readers_read_generated_makefiles_as_make_does` and `test_the_makefile_readers_read_the_tracked_makefile_as_make_does`, and each said "AssertionError: /usr/bin/make is GNU Make 3.81; the comparison needs version 4 or newer". `PL-TSH9` made the test name the cause, and it asked `docs/maintainer.md` to say how to install current GNU make on the Mac. The bash half of `PL-TSH9` is fixed on this host, because the shell tests passed. The make half is not: `make` on the worker's `PATH` is still Apple's 3.81.

**Why it matters.** A worker that cannot get `make check` green cannot tell its own failures from the host's, and the reviewing session cannot either. `docs/maintainer.md` already says how to install GNU Make 4 with Homebrew and put it first on `PATH`, so the remaining gap is that nothing refuses a run on a host where that has not happened. `tools/headless_worker.py`'s `check_tools` already refuses a missing `claude`, `uv` or `python3` and a `python3` older than 3.11 before any spend, but it does not read the versions of `make` or `bash`. **Checked 2026-10-24:** `check_tools` names only those three tools.

**Done when.** `check_tools` refuses a run, before any spend, when the `make` or `bash` on the run's `PATH` is older than the versions `docs/maintainer.md` names (GNU Make 4, bash 5.2), and the refusal names that section. `tests/unit/test_headless_worker.py` has `test_an_old_make_on_path_is_refused_before_any_spend`.

**Generator check.** A re-entry of `PL-TSH9` (the owner's Mac failing 90 tests on old bash and make), which closed on 2026-10-19 with a documentation fix. The misread fact is which `make` the worker's `PATH` runs. Its fix told the owner how to install the new one but gave the runner no way to notice the old one, so the same failure returned on the next run.
