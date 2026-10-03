---
id: PL-1836
title: tools/main_ci_status.py unrun_after's docstring and tests/unit/test_main_ci_status.py's say quality.yml runs four to nine (six to eleven) checks below the whole-store verify replay, but the replay is now the job's last step, so a replay failure skips nothing and the load-bearing reason the docstring gives no longer holds
status: untriaged
touches: tools/main_ci_status.py, tests/unit/test_main_ci_status.py
added: 2026-10-03
---

**Problem.** tools/main_ci_status.py unrun_after's docstring and tests/unit/test_main_ci_status.py's say quality.yml runs four to nine (six to eleven) checks below the whole-store verify replay, but the replay is now the job's last step, so a replay failure skips nothing and the load-bearing reason the docstring gives no longer holds

**Found 2026-10-03, by `PL-40SJ`'s docs sweep, not caused by it.** In `.github/workflows/quality.yml` the step named `verify replay, the whole store` is the last step of the job; every `uv run python tools/*_check.py` line, `contrast_check` and `import_boundary_check` among them, runs above it. So `unrun_after(steps, REPLAY_STEP)` counts only what follows the replay, which is nothing but the runner's `Post` cleanup, and the docstring's reason it is "load-bearing rather than decoration" describes an earlier step order. `PL-40SJ` added one more check above the replay, which changes neither half. Whether the function still earns its place, or the line it guards should say something else, is the judgment here; check `git log -S "verify replay, the whole store" -- .github/workflows/quality.yml` for when the order changed.
