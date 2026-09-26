---
id: PL-QMN0
title: gate-status-guard.sh unwraps uv run only where the program follows it directly, so a gate after uv run's own options - uv run --with pytest-xdist pytest -n 4 2>&1 | tail - is read as a command named --with and loses its status unrefused
priority: P3
effort: S
status: blocked
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
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

**Reproduced further 2026-09-26 on `6efd8c41`**, as hook payloads: `uv run
--frozen mypy | tail` and `uv run -m pytest | tail` pass too, and so does `uv
-q run pytest -q 2>&1 | tail`, where an option ahead of `run` hides the `uv
run` itself from `strip_prefixes`. uv 0.12.19 runs `pytest` or `mypy` in each.
Its parser, clap, reads options up to the first word that is not one and hands
the rest to the command (`uv run --help`: "Usage: uv run [OPTIONS] [COMMAND]"),
and uv's global options stand on either side of `run` (`uv --help`: "Usage: uv
[OPTIONS] <COMMAND>").

**Built, then parked 2026-09-26.** A session worked this before it was blocked,
and the work is on `claude/project-thread-qt3onr` at `59ea9d1c`: the option
grammar of `uv` and of `uv run` in `.claude/hooks/shell_split.py`, read from uv
0.12.19's help and the clap definitions behind it, hidden options included;
`uv_run_words`, which reads past both on either side of `run`; the gate guard
reading through it, and no other guard, since `uv run python3` runs the
project's interpreter and not the bare one the floor guard refuses; and
`test_uv_run_runs_the_command_after_its_own_options`, whose 13 refusal cases
fail on the hook this item was filed against. Its pull request, #1127, was
closed unmerged when `PL-61FT` blocked this item. If the bound keeps this
spelling, working it again starts from that commit; if it drops it, the branch
is discarded with it.

**Generator check.** A member of `PL-61FT` (the Bash guards read what a
command does from its spelling): filed by `PL-TRMN`'s close, which read the
options of the wrappers it named and not uv's. Blocked on it, because the
bound it sets decides whether this spelling is worked, dropped or kept as a
known gap. Working it filed two more spellings of the same kind, both found by
probing rather than met in ordinary work: `PL-BM3Z` (`bin/docket`'s own options
ahead of its subcommand) and `PL-7PB9` (a listed gate run as a module).
