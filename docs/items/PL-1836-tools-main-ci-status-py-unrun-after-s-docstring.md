---
id: PL-1836
title: tools/main_ci_status.py unrun_after's docstring and tests/unit/test_main_ci_status.py's say quality.yml runs four to nine (six to eleven) checks below the whole-store verify replay, but the replay is now the job's last step, so a replay failure skips nothing and the load-bearing reason the docstring gives no longer holds
priority: P3
effort: S
status: ready
classes: refactor, docs
touches: tools/main_ci_status.py, tests/unit/test_main_ci_status.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-03
payoff: nobody maintains or reasons from a branch of the red-main advisory that cannot fire, or from a fixture saying a replay failure still skips the checks PL-7K2C moved above it
verify: ! grep -q 'def unrun_after' tools/main_ci_status.py
---

**Problem.** tools/main_ci_status.py unrun_after's docstring and tests/unit/test_main_ci_status.py's say quality.yml runs four to nine (six to eleven) checks below the whole-store verify replay, but the replay is now the job's last step, so a replay failure skips nothing and the load-bearing reason the docstring gives no longer holds

**Found 2026-10-03, by `PL-40SJ`'s docs sweep, not caused by it.** In `.github/workflows/quality.yml` the step named `verify replay, the whole store` is the last step of the job; every `uv run python tools/*_check.py` line, `contrast_check` and `import_boundary_check` among them, runs above it. So `unrun_after(steps, REPLAY_STEP)` counts only what follows the replay, which is nothing but the runner's `Post` cleanup, and the docstring's reason it is "load-bearing rather than decoration" describes an earlier step order. `PL-40SJ` added one more check above the replay, which changes neither half. Whether the function still earns its place, or the line it guards should say something else, is the judgment here; check `git log -S "verify replay, the whole store" -- .github/workflows/quality.yml` for when the order changed.

**Generator check.** Not a head: one docstring and one test docstring describing a step order that has since changed; nothing else reads the order this way.

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`python3 -c "import sys; sys.path.insert(0, 'tools'); import main_ci_status as m; after = [l for l in sys.stdin.read().split('name: ' + m.REPLAY_STEP)[1].splitlines() if l.startswith('      - ')]; print(len(after), m.unrun_after(((m.REPLAY_STEP, 'failure'), *((a, 'skipped') for a in after)), m.REPLAY_STEP))" < .github/workflows/quality.yml`
printed `0 0`: no step of the `checks` job follows the replay, so on any replay
failure `unrun_after` counts nothing and `advisory` prints no tail. Over
`git show 71acdc75:.github/workflows/quality.yml` the same command prints
`12 12`. The suggested `git log -S` finds only `10d449ec` (2026-09-05), where
the step was named, since moving a step leaves the string's count unchanged;
counting the steps after the replay at each commit to the file dates the
reorder to `cf4bf7b2` (`#1259`, `PL-7K2C`, 2026-10-01), which also added
`test_the_whole_store_replay_is_the_last_step_in_the_job` in
`tests/unit/test_quality_step_order.py` to fail any step added after either
replay. The old order is described in two more places than the title names:
the queue-reading paragraph of `advisory`'s docstring, which says the
replay's failure skipped every check below it, and the `_REPLAY_STEPS`
fixture, which puts two of the job's own checks below the replay, the shape
that test now refuses.

**Why it matters.** Nothing prints wrong, and nothing can while the
step-order test stands: `unrun_after` runs only when the replay is the one
failing step, and a step added after the replay fails that test in the
pytest step above it, so that run never takes the queue branch. All 94
completed `main` push runs of `quality.yml` from `cf4bf7b2` to 2026-10-04
passed, so the function has not been called once. The cost is to a reader of
the code: both files say a replay failure on `main` leaves the contrast,
import-boundary, core-vocabulary and glyph checks unrun, the gap `PL-7K2C`
closed, and six tests and a fixture pin a workflow shape that can no longer
occur, which a session editing `advisory` would read as a live branch to
keep.

**Done when.** Retired, which is the recommendation over re-describing it:
`unrun_after`, `_CLEANUP_PREFIX` and the tail sentence in `advisory` are gone,
with the five `unrun_after` tests and
`test_never_calls_the_tree_clean_on_steps_the_failure_skipped`; `advisory`'s
docstring says the replay is the job's last step, held there by
`test_the_whole_store_replay_is_the_last_step_in_the_job` in
`tests/unit/test_quality_step_order.py`, so its failure skips nothing; the
`_REPLAY_STEPS` fixture puts no step of the job's own below the replay; and
`! grep -q 'def unrun_after' tools/main_ci_status.py` exits 0. Re-described
instead, the docstring would have to say the function returns 0 on every run,
which is the check `CLAUDE.md` says to retire rather than keep.
