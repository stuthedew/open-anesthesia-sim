---
id: PL-ZS13
title: gate-status-guard.sh's remedies name the gate it matched rather than the command it refused, so for python3 tools/possessive_section_check.py --help 2>&1 | tail the line it calls the one you want was set -o pipefail; tools/possessive_section_check.py 2>&1 | tail -45, which exits 126 since no tools/*_check.py is executable - met 2026-09-27 triaging PL-N6JP
priority: P3
effort: S
status: done
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/gate-status-guard.sh, .claude/hooks/shell_split.py, tests/unit/test_gate_status_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
closed: 2026-09-27
pr: 1152
payoff: a session refused for piping a check it runs through python3 or uv run is offered a line that runs that same check with its arguments, not one that exits 126 or runs another suite, so the retry the refusal asks for is the whole of its price
verify: grep -q 'def test_the_remedy_runs_the_gate_the_command_ran' tests/unit/test_gate_status_guard.py
---

**Problem.** gate-status-guard.sh's remedies name the gate it matched rather than the command it refused, so for python3 tools/possessive_section_check.py --help 2>&1 | tail the line it calls the one you want was set -o pipefail; tools/possessive_section_check.py 2>&1 | tail -45, which exits 126 since no tools/*_check.py is executable - met 2026-09-27 triaging PL-N6JP

**Met 2026-09-27, triaging `PL-N6JP`.** The guard refused `python3
tools/possessive_section_check.py --help 2>&1 | tail -4` and offered, as the
spelling "you want", `set -o pipefail; tools/possessive_section_check.py 2>&1
| tail -45`. Run as printed it exits 126, `Permission denied`: all 18
`tools/*_check.py` are mode `100644` in git and none has a shebang. The line
also drops the `--help` the refused command carried.

**Why.** `gate()` returns the gate "spelled for the message", and every remedy
line is built from that name; for a check run through an interpreter it is
`check_script`'s token alone, the script's path. Read from `gate()` rather
than met: `pytest`, `mypy` and `ruff` come back as the bare name, so `uv run
pytest -q tests/unit/t.py | tail` is offered `set -o pipefail; pytest 2>&1 |
tail -45`, without `uv run` and without the file it named; a `make` or
`bin/docket` gate comes back runnable, less its other arguments.

**Why it matters.** The header's case for the guard is that its remedy is one
token, so sessions do not learn to route around it. A remedy that fails when
copied costs the retry the refusal was meant to be the whole price of, and the
line it calls the one you want is the one a session copies.

**Reproduced 2026-09-27 on `origin/main` at `970bee11`.** Piped to the hook as
payloads, `python3 tools/possessive_section_check.py --help 2>&1 | tail -4`
and `python3 tools/doc_check.py check | head -40` were offered `set -o
pipefail; tools/possessive_section_check.py 2>&1 | tail -45` and the same line
for `tools/doc_check.py`, and each script run that way exits 126 in bash
5.2.21. `uv run pytest -q tests/unit/t.py | tail` was offered bare `pytest`,
which in the container resolves to `/root/.local/bin/pytest` rather than the
project's environment, over the whole suite rather than the file named;
`bin/docket verify PL-D0W8 | tail` was offered `bin/docket verify` with no id;
and `QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration 2>&1 | tail
-5` was offered `pytest` without the assignment it set.

**Generator check.** The fact misread is `PL-61FT`'s, what a shell command does
when run: here which program runs the gate and on what, since the remedy is
spelled from the gate's name, which keeps neither the interpreter or `uv run`
nor the arguments. An instance of that head's fact, filed in `ec74a5fa`
(`#1145`) after the head closed in `831493f7` (`#1138`). It sits inside that
head's bound on both of its tests - the bound counts the remedy a guard prints
among the spellings written out to be run, and a session met this one in
ordinary work - so it is worked at its own rank; it is not a `KNOWN_GAPS` row
met, which is what the head's reopening number counts. No new head.

**Done when.** Every remedy line the refusal prints spells the gate as the
refused command ran it - its assignments, a wrapper, `uv run` or the
interpreter, the program and its arguments, less the redirections the remedy
supplies and the grouping or reserved word that opened it - so `python3
tools/possessive_section_check.py --help 2>&1 | tail -4` is offered `set -o
pipefail; python3 tools/possessive_section_check.py --help 2>&1 | tail -45`.
The sentence naming the gate ("This command runs `pytest`") keeps the gate's
name. A test pins this item's command and the other spellings reproduced
above, and holds every remedy line the refusal prints to being admitted.
