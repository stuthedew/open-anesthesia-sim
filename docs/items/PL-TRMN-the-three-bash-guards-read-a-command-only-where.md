---
id: PL-TRMN
title: The three Bash guards read a command only where its name is the program itself, so a gate, a floor parse or a prune run through a wrapper passes all three: timeout 600 make check | tail -5, timeout 60 python3 -m compileall -q src/anesthesia_sim/, and timeout, env, command or a path to git ahead of git fetch --prune
priority: P2
effort: M
status: ready
classes: defect
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/no-prune-guard.sh, tests/unit/test_gate_status_guard.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: a gate, a floor parse or a prune run under timeout, env, nice, nohup, xargs, command or exec is refused like the same command on its own, so a red make check under timeout piped to tail no longer reaches a session as exit 0
verify: grep -q 'def test_a_wrapper_runs_the_command_after_it' tests/unit/test_gate_status_guard.py && grep -q 'def test_a_wrapper_runs_the_command_after_it' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_a_wrapper_runs_the_command_after_it' tests/unit/test_no_prune_guard.py
---

**Problem.** The three Bash guards read a command only where its name is the program itself, so a gate, a floor parse or a prune run through a wrapper passes all three: timeout 600 make check | tail -5, timeout 60 python3 -m compileall -q src/anesthesia_sim/, and timeout, env, command or a path to git ahead of git fetch --prune

**Found 2026-09-26 while working `PL-R17X`**, by piping each command as a
hook payload into the hooks on its branch. `make check | tail -5` is refused by
`gate-status-guard.sh` and `timeout 600 make check | tail -5` passes it;
`python3 -m compileall -q src/anesthesia_sim/` is refused by
`floor-interpreter-guard.sh` and `timeout 60 python3 -m compileall -q
src/anesthesia_sim/` passes it; and `no-prune-guard.sh` passes `timeout 60 git
fetch --prune`, `env GIT_TRACE=1 git fetch --prune`, `command git fetch
--prune` and `/usr/bin/git fetch --prune`. Those were run; `nice`, `nohup`,
`xargs` and `exec` are the same shape and were not.

`shell_split.command_words` drops what bash reads ahead of a command's name -
grouping, the reserved words that open a command, `time` and its options,
assignments - and each guard compares the first word left with the program it
guards. A program that runs another is read as the command, and a path to the
program as a different one. `timeout N make check 2>&1 | tail` is a spelling a
session reaches for on a long suite, which is the shape the gate guard exists
to refuse: a red check reaching the session as exit 0.

**Why it matters.** Each guard refuses a spelling that has already cost this
project a round or a ref: the gate guard a red `make check` reported green
(`PL-2JRC`), the floor guard a correct file reported as a SyntaxError on `main`
(`PL-JQJQ`), the prune guard an item held only by a stale remote ref
(`PL-HKF4`). `gate-status-guard.sh` left `timeout 900 make check | tail`
unguarded on purpose, on the ground that nobody had written it; this item has.
A guard that refuses `make check | tail -5` and passes the same command under
`timeout` reads as protection it does not give.

**Done when.** `shell_split.py` answers which program a command runs past a
wrapper that runs another - `timeout`, `env`, `nice`, `nohup`, `xargs`,
`command` and `exec`, each read by its own option grammar, nested, and named by
path as well as bare - and all three guards read a command's program through
it. Every spelling reproduced above is refused; `command -v git`, and a wrapper
around a command no guard names, are not. The gate guard still unwraps `uv run`,
with a wrapper on either side of it; the floor guard still admits an
interpreter named by path, its deliberate spelling; the prune guard reads a
path to `git` as `git`. The three hook suites pin each.

**Generator check.** One-off. The fact misread is which program a command runs
past a program that runs another, and no other item misreads it. `PL-0X0G`
(done, #1093) misread its neighbour in the same function - which word bash
reads as a command's name, past what bash reads ahead of it - and `PL-K9QL`,
the redirections ahead of a name, is a re-entry of that fix rather than a
member of this one. Each is a gap in the one answer the guards share, not a
second spelling of it, so none is `PL-PVW2`'s.
