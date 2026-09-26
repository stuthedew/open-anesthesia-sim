---
id: PL-QMN0
title: gate-status-guard.sh unwraps uv run only where the program follows it directly, so a gate after uv run's own options - uv run --with pytest-xdist pytest -n 4 2>&1 | tail - is read as a command named --with and loses its status unrefused
priority: P3
effort: S
status: blocked
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
blocked-by: PL-61FT
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
---

**Problem.** gate-status-guard.sh unwraps uv run only where the program follows it directly, so a gate after uv run's own options - uv run --with pytest-xdist pytest -n 4 2>&1 | tail - is read as a command named --with and loses its status unrefused

**Found 2026-09-26 triaging `PL-TRMN`**: on `6d92df95` the hook passes
`uv run --with pytest-xdist pytest -n 4 2>&1 | tail` and refuses the same
command without `--with pytest-xdist`. `strip_prefixes` drops `uv run` and then
reads the next word as the program. Neither the `Makefile` nor the workflows
spell `uv run` with options, so it is unobserved here; reaching it means
reading uv's own option grammar, which `PL-TRMN` does for the wrappers it
names and deliberately not for `uv run`.

**Why it matters.** A false allowance: a gate run through `uv run` with uv's
own options loses its status down the pipe unrefused. Reproduced as filed on
`origin/main` (`6efd8c41`) at triage, 2026-09-26, beside `uv run pytest -n 4
2>&1 | tail`, which is refused.

**Generator check.** A member of `PL-61FT` (the Bash guards read what a
command does from its spelling): filed by `PL-TRMN`'s close, which read the
options of the wrappers it named and not uv's. Blocked on it, because the
bound it sets decides whether this spelling is worked, dropped or kept as a
known gap.
