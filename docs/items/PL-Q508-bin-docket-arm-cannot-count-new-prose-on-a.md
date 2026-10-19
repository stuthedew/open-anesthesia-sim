---
id: PL-Q508
title: bin/docket arm cannot count new prose on a branch that changes src/anesthesia_sim/app_metadata.py or layout/store.py in a cloud container, because docket.toml's prose_count_command runs bare python3 (3.13 here) and those files use Python 3.14's unparenthesized except syntax (PEP 758), so arm holds correct work
priority: P2
effort: S
status: done
classes: defect
touches: docket.toml, tests/unit/test_new_prose.py, .claude/skills/docket/modes/close-out.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science: a workflow-lane defect in arm's prose count
added: 2026-10-19
closed: 2026-10-19
pr: 1667
payoff: bin/docket arm counts the prose on a branch that changes a file written in 3.14 syntax, instead of holding correct work it could not read
verify: grep -q 'prose_count_command = "uv run python tools/new_prose.py --count"' docket.toml && grep -q 'def test_arm_counts_prose_under_the_interpreter_src_targets' tests/unit/test_new_prose.py
---

**Problem.** bin/docket arm cannot count new prose on a branch that changes src/anesthesia_sim/app_metadata.py or layout/store.py in a cloud container, because docket.toml's prose_count_command runs bare python3 (3.13 here) and those files use Python 3.14's unparenthesized except syntax (PEP 758), so arm holds correct work

**Found 2026-10-19 on #1661.** `bin/docket arm` held the branch with
"`python3 tools/new_prose.py --count` exited 2: new_prose: not read:
src/anesthesia_sim/app_metadata.py: multiple exception types must be
parenthesized, line 92". Line 92 is `except OSError,
subprocess.SubprocessError:`, which `main` already carries. The same command
run with Python 3.14.7 (`uv python find 3.14`) first on `PATH` printed `21`.
`PL-JQJQ` records why a bare `python3` here is older than the simulator's
interpreter. Either the command in `docket.toml` names an interpreter that
can parse `src/`, or `new_prose.py` falls back to the tokenizer as `PL-TC2D`
did for `docket verify`.

**Reproduced 2026-10-19, at triage.** On a scratch commit over `main` at
`5df2f841` that changes only a comment on `app_metadata.py`'s line 92, the
bare interpreter (`/usr/bin/python3.13` here) running
`tools/new_prose.py --count` exited 2 with the same "not read" line. The same
commit counted `0` and exited 0 under `uv run python`, which is Python 3.14.7.

**Why it matters.** `arm` holds every simulator branch that touches one of
these files, so correct work waits on a hold the owner cannot clear, and a
session either routes around the hold or reports it as a real one. The number
of such files grows with every newer syntax `src/` adopts.

**Decided: run the count under `uv run python`, not a tokenizer fallback.**
`new_prose.py` needs the parse itself, not only the tokens. It reads
docstrings through `ast` and decides whether a test file is the simulator's by
its imports, so a tokenizer reading would have to rebuild both. The
repository already settles which interpreter a tool that reads 3.14 source
runs under: the `Makefile` runs `doc_check.py`, `possessive_section_check.py`
and eight others under `uv run python` for that reason (`PL-MB3F`), and the
floor-interpreter hook says so to every session that tries the bare one. What
it costs: `arm` now needs `uv` and the project environment. A session already
has both, since `make check` needs them. Where `uv` is missing or its first
sync outlasts `PROSE_COUNT_TIMEOUT`, `arm` holds and names the command, which
is a visible failure rather than a wrong count.

**Done when.** `docket.toml`'s `prose_count_command` runs `tools/new_prose.py`
under `uv run python`, its comment says why, and
`tests/unit/test_new_prose.py` gains
`test_arm_counts_prose_under_the_interpreter_src_targets`, which fails on
today's bare `python3` command.

**Generator check.** Not a member of any head `bin/docket generators` lists.
`PL-MB3F` (a `Makefile` line reading `src/` under the bare interpreter) and
`PL-JQJQ` (sessions parsing `src/` with it) came from the same deliberate
split between the 3.11 tools interpreter and the 3.14 simulator, which is a
design rather than a defect, so nothing is recorded as a generator. After
this fix no command in `docket.toml` parses `src/` under the bare
interpreter: `doc_check.py check` in `health_clauses` runs bare by design and
names each file it cannot parse, as `PL-MB3F` records.

**Done 2026-10-19.** The close-out mode's step 8 told a session to run the
same tool under the bare interpreter, which names those files as not read, so
both its commands now say `uv run python` as well.
