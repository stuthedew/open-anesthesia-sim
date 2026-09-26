---
id: PL-R5N0
title: floor-interpreter-guard.sh lets 'python3 -m compileall src' and 'python3 -m pytest tests' through, because GUARDED needs a slash after the tree name, so the commonest spelling of a floor parse of the 3.14 trees is not refused
priority: P2
effort: S
status: ready
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_floor_interpreter_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: python3 -m pytest tests and python3 -m compileall src meet the guard's refusal, which names the 3.11 floor, instead of a false SyntaxError
verify: grep -q 'def test_a_bare_tree_name_is_a_floor_parse' tests/unit/test_floor_interpreter_guard.py
---

**Problem.** floor-interpreter-guard.sh lets 'python3 -m compileall src' and 'python3 -m pytest tests' through, because GUARDED needs a slash after the tree name, so the commonest spelling of a floor parse of the 3.14 trees is not refused

**Found 2026-09-26 while working `PL-GVFC`**, by piping each command as a hook
payload into `bash .claude/hooks/floor-interpreter-guard.sh` on a tree where
`python3` is 3.11.15. All three are allowed:

    python3 -m compileall src
    python3 -m compileall ./src
    python3 -m pytest tests

`GUARDED` is `(?<![\w-])(?<!subprojects/docket/)(?:src|tests)/`, so the tree
name has to be followed by a slash, and every case in
`tests/unit/test_floor_interpreter_guard.py`'s `FLOOR_PARSE` writes one.
Without the slash it is still a floor parse of the whole tree, and meets the
`SyntaxError` in `src/anesthesia_sim/app_metadata.py` that the deny message
quotes.

**Why it matters.** The guard misses the commonest spelling of the exact
command it was built to refuse (`PL-JQJQ`), so a session or subagent that
writes it meets the false `SyntaxError` with no refusal to explain it.

**Done when.** A bare `python3` given `src` or `tests` as a whole path
argument - bare, after `./`, or absolute - is refused, while
`subprojects/docket/src` and a `-c` string that merely contains the word stay
admitted, all pinned in `tests/unit/test_floor_interpreter_guard.py`.

[superseded 2026-09-26: counted a member of `PL-61FT` at triage, below] **Generator check.** One-off. It shares the `GUARDED` pattern with `PL-GVFC`'s
first cause, which was the opposite fault (the pattern reached too far, into
the docket subproject); two faults in one regex are not a mechanism handing
out members. The recurrence `docket new` recorded on `PL-GVFC` is that shared
file, not a shared cause.

**Generator check, at triage 2026-09-26.** A member of `PL-61FT` (the Bash
guards read what a command does from its spelling): found by probing while
working `PL-GVFC` and filed by its close, which is the mechanism the other
eleven share, though the fault is in the guard's own path pattern rather than
its reading of bash. Owed under any bound `PL-61FT` sets, since `python3 -m
pytest tests` is the canonical spelling, so it is left ready. Reproduced as
filed on `origin/main` (`6efd8c41`) at triage, beside `python3 -m
compileall src/`, which is refused.
