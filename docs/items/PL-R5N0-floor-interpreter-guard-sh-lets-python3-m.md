---
id: PL-R5N0
title: floor-interpreter-guard.sh lets 'python3 -m compileall src' and 'python3 -m pytest tests' through, because GUARDED needs a slash after the tree name, so the commonest spelling of a floor parse of the 3.14 trees is not refused
status: untriaged
touches: .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_floor_interpreter_guard.py
added: 2026-09-26
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

**Generator check.** One-off. It shares the `GUARDED` pattern with `PL-GVFC`'s
first cause, which was the opposite fault (the pattern reached too far, into
the docket subproject); two faults in one regex are not a mechanism handing
out members. The recurrence `docket new` recorded on `PL-GVFC` is that shared
file, not a shared cause.
