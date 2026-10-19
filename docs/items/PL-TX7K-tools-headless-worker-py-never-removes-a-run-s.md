---
id: PL-TX7K
title: tools/headless_worker.py never removes a run's clone: every run, failed or pushed, leaves a full clone and a log in ~/.local/state/open-anesthesia-sim/workers until the owner deletes it by hand. Keep failed runs' clones for diagnosis and remove a clone once its branch is pushed
priority: P3
effort: S
status: ready
classes: defect, infra
feature: api-credit-runs
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
payoff: the owner's machine stops gaining a full repository clone per credit run, while a failed run's clone stays for diagnosis
verify: grep -q 'def test_a_pushed_run_removes_its_clone_and_a_failed_run_keeps_it' tests/unit/test_headless_worker.py
---

**Problem.** tools/headless_worker.py never removes a run's clone: every run, failed or pushed, leaves a full clone and a log in ~/.local/state/open-anesthesia-sim/workers until the owner deletes it by hand. Keep failed runs' clones for diagnosis and remove a clone once its branch is pushed

**Checked 2026-10-19.** On `main` at `1e5cb9bd`, `tools/headless_worker.py`
names no `rmtree` or other removal. `work` makes each clone with
`git clone --reference ROOT --dissociate`, so every clone is a full copy of
the repository, whose `.git` is 41 MB here, and writes its log beside it.

**Why it matters.** Each run the owner starts leaves about 41 MB or more on
their machine, and a month of credit runs leaves one clone per item. Nothing
tells the owner the directory is growing, and deleting it by hand also
deletes the failed runs they may still want to read.

**Done when.** A run whose branch was pushed removes its clone and keeps its
log. A failed run, or a `--no-push` trial run, keeps both, and the report line
says where. A test in `tests/unit/test_headless_worker.py` covers both cases.

**Generator check.** A one-off. `PL-MZCN` and `PL-W38C` were also first-run
defects in this tool, but each misread a different fact (the run's output, and
which interpreter starts `bin/docket`), and no head's `misread:` states the
clone's lifetime.
