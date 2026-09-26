---
id: PL-BBV7
title: The three Bash guard hooks split a command into programs three ways, so the floor-interpreter guard lets 'cd /x&&python3 src/a.py', 'true;python3 -m compileall src/' and '(python3 src/a.py)' through while denying the same commands with spaces
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: .claude/hooks/, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_gate_status_guard.py, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
closed: 2026-09-26
pr: 1064
payoff: the floor guard refuses a bare python3 aimed at src/ however the command is spaced or grouped, so no session is walked into the false SyntaxError it exists to prevent
verify: grep -q 'def test_an_unspaced_separator_still_ends_a_command' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_a_subshell_paren_does_not_hide_the_interpreter' tests/unit/test_floor_interpreter_guard.py
---

**Problem.** The three Bash guard hooks split a command into programs three ways, so the floor-interpreter guard lets 'cd /x&&python3 src/a.py', 'true;python3 -m compileall src/' and '(python3 src/a.py)' through while denying the same commands with spaces

Reproduced against `floor-interpreter-guard.sh` (plain `shlex.split`), `gate-status-guard.sh` (`punctuation_chars`) and `no-prune-guard.sh` (regex). PL-GVFC covers the false-refusal direction; this is the missed-refusal direction and `(` grouping.

**Re-confirmed 2026-09-25 against 46954a81** by piping each command as a hook payload into `floor-interpreter-guard.sh`. `cd /x&&python3 src/a.py` and `true;python3 -m compileall src/` are allowed, and their spaced forms are denied. `(python3 src/a.py)` is allowed, and so is `( python3 src/a.py )`: a `(` is never a separator to it, whatever the spacing. `no-prune-guard.sh`'s regex anchors on `[;&|\n(]` and denies the unspaced and parenthesised shapes, so a missed refusal of the ref-deleting kind was not found here.

**Why it matters.** A guard that a missing space defeats. What leaks through is a bare `python3` parse of `src/`, which costs a session a detour into the false `SyntaxError` PL-JQJQ exists to prevent, and loses no state. That is why this is P3.

**Work it with PL-GVFC** (ready, P3). It is the false-refusal half of the same `shlex.split` call in the same hook, and a shared `punctuation_chars` splitter fixes both.

**Generator check.** It is an instance of PL-PVW2's fact, which spelling of a repeated predicate is the answer. The predicate is how a shell command splits into programs. `gate-status-guard.sh`'s comment already records why plain `shlex.split` misses `check|tail`, and the floor guard never read it.

**Done when.** One splitter shared by the three hooks; a test holds each reproduction.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Closed 2026-09-26 with `PL-GVFC`, whose change fixed and pinned every reproduction above.** `floor-interpreter-guard.sh` now tokenises with `gate-status-guard.sh`'s lexer settings - `punctuation_chars`, a newline read as `;`, and `(`, `{` and `!` opening the command they precede - after first joining a line continued with a backslash. `cd /x&&python3 src/a.py`, `true;python3 -m compileall src/`, `(python3 src/a.py)` and `( python3 src/a.py )` are refused, and so are `true||python3 ...`, `{ python3 ...; }` and `! python3 ...`, under the two test names this item's `verify:` reads. The done-when's other clause, one splitter shared by the three hooks, is not built here: it is `PL-PVW2`'s how-a-shell-command-splits question, whose own done-when requires it, and `PL-R5RF` - the gate guard misreading a backslash continuation, in the one line where the two hooks now differ - is filed under the same `one-answer` feature as a reproduction for it. Left open, this item failed `docket check --verify`, an open item whose `verify:` already passes.
