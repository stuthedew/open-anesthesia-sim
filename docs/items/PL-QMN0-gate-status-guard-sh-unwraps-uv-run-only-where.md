---
id: PL-QMN0
title: gate-status-guard.sh unwraps uv run only where the program follows it directly, so a gate after uv run's own options - uv run --with pytest-xdist pytest -n 4 2>&1 | tail - is read as a command named --with and loses its status unrefused
priority: P2
effort: S
status: done
classes: defect
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py, docs/items/PL-TRMN-the-three-bash-guards-read-a-command-only-where.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
payoff: a gate run by uv run after options of uv's own - uv run --with pytest-xdist pytest -n 4 2>&1 | tail, uv -q run pytest | tail - is refused like the same gate after a bare uv run, so a red suite run with an extra package or a frozen lockfile no longer reaches a session as exit 0
verify: grep -q 'def test_uv_run_runs_the_command_after_its_own_options' tests/unit/test_gate_status_guard.py
---

**Problem.** gate-status-guard.sh unwraps uv run only where the program follows it directly, so a gate after uv run's own options - uv run --with pytest-xdist pytest -n 4 2>&1 | tail - is read as a command named --with and loses its status unrefused

**Found 2026-09-26 triaging `PL-TRMN`**: on `6d92df95` the hook passes
`uv run --with pytest-xdist pytest -n 4 2>&1 | tail` and refuses the same
command without `--with pytest-xdist`. `strip_prefixes` drops `uv run` and then
reads the next word as the program. Neither the `Makefile` nor the workflows
spell `uv run` with options, so it is unobserved here; reaching it means
reading uv's own option grammar, which `PL-TRMN` does for the wrappers it
names and deliberately not for `uv run`.

**Reproduced 2026-09-26 on `6efd8c41`**, as hook payloads: `uv run --with
pytest-xdist pytest -n 4 2>&1 | tail` passes and `uv run pytest -n 4 2>&1 |
tail` is refused; `uv run --frozen mypy | tail` and `uv run -m pytest | tail`
pass too, and so does `uv -q run pytest -q 2>&1 | tail`, where an option ahead
of `run` hides the `uv run` itself from `strip_prefixes`. uv 0.12.19 runs
`pytest` or `mypy` in each. Its parser, clap, reads options up to the first
word that is not one and hands the rest to the command (`uv run --help`: "Usage:
uv run [OPTIONS] [COMMAND]"), and uv's global options stand on either side of
`run` (`uv --help`: "Usage: uv [OPTIONS] <COMMAND>").

**Why it matters.** It is the failure the guard exists for: a red gate reaching
a session as exit 0 (`PL-2JRC`). `uv run` is how this project spells most of
the gate list, and its options are how a session adds a package for one run
(`--with`), leaves the lockfile or the environment as they are (`--frozen`,
`--no-sync`), or picks an interpreter (`-p`). A guard that refuses `uv run
pytest | tail` and passes `uv run --frozen pytest | tail` reads as protection
it does not give, which is the reasoning `PL-TRMN` gave for a wrapper, one word
further on.

**Done when.** `.claude/hooks/shell_split.py` holds the option grammar of `uv`
and of `uv run`, read from uv 0.12.19's help and the clap definitions behind
it, hidden options included, and answers which command a `uv run` runs past the
options on both sides of `run`; `gate-status-guard.sh` reads past `uv run`
through it. No other guard does, since `uv run python3` runs the project's
interpreter and not the bare one the floor guard refuses. Each spelling above
is refused, and so is the reproduction with a wrapper on either side, a long
option's value after `=`, a short option's value in a bundle, and a `--` ahead
of the command. The value of `--with` is not read as the program, so `uv run
--with pytest python -c pass | tail` passes, and nothing after `uv run --help`
is read. The gate guard's suite pins each.

**Generator check.** `PL-TRMN`'s fact - which word is the program, builtin or
subcommand a guard reads, past the options ahead of it - at the site its triage
split off, with `PL-9RSP`, before its own work. Working this item found a third reader: `gate()` reads `bin/docket`'s
subcommand past none of docket's own options, filed as `PL-BM3Z`. `PL-TRMN`
states the mechanism and built the record every reader should consult, so three
items explained is the count `CLAUDE.md` records a head at, and it is recorded
there: spent, since once this item and `PL-BM3Z` land every word the three
guards read after a program is read through that program's grammar or found by
scanning all its words. Not `PL-PVW2`'s: a gap in the one answer the guards
share, not a second spelling of it. `PL-7PB9`, filed beside it, is a different
fact: which spellings of a listed gate the guard recognises once it has the
right word.
