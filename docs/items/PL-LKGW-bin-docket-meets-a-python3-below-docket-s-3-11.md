---
id: PL-LKGW
title: bin/docket meets a python3 below docket's 3.11 floor with render.py's ImportError traceback rather than naming the floor and the interpreter it found, so a Mac whose python3 is Apple's 3.9 gets a cryptic failure by hand and silent hooks with nothing saying why
priority: P3
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/__main__.py, subprojects/docket/tests/test_portability.py
added: 2026-09-14
verify: grep -q 'def test_an_interpreter_below_the_floor_names_the_floor_and_itself' subprojects/docket/tests/test_portability.py && uv run pytest subprojects/docket/tests/test_portability.py
---

**Problem.** bin/docket meets a python3 below docket's 3.11 floor with render.py's ImportError traceback rather than naming the floor and the interpreter it found, so a Mac whose python3 is Apple's 3.9 gets a cryptic failure by hand and silent hooks with nothing saying why

**Found 2026-09-14** while working `PL-Y6W9`, whose reproduction is the
evidence: with a 3.10 `python3` first on `PATH`, `bin/docket digest` exits
1 on `ImportError: cannot import name 'UTC' from 'datetime'` out of
`subprojects/docket/src/docket/render.py`, which is a traceback about a
module rather than a sentence about a version. Both hooks then swallow it and
exit 0 by contract, so a session on such a machine starts with no digest and
no line saying why.

**Where.** `subprojects/docket/src/docket/__main__.py`, before anything that
needs 3.11 is imported: a `sys.version_info` check that exits with the floor
`subprojects/docket/pyproject.toml` declares, the version found and
`sys.executable`, costs nothing on every other run. A guard in `bin/docket`
itself would cost an extra interpreter start per call.

**Done when.** `bin/docket` under a pre-3.11 `python3` prints one line naming
the floor and the interpreter it ran under, and exits non-zero.

**Why it matters.** The failure is silent exactly where a session cannot ask why.
By hand, `bin/docket` exits 1 on an `ImportError` naming `render.py` and
`datetime.UTC`, which reads as a defect in this repository rather than as a
statement about the interpreter - so the first move is to go and look at a file
that is fine. Through the hooks it is worse: both are written to swallow a
failure and exit 0 by contract, so a session on such a machine starts with no
digest, no queue state and no line saying why, and proceeds as though the queue
were empty. That is `CLAUDE.md`'s first compounding-friction test - a check
passing while the guarantee it stands for is void - and the whole session-start
digest is the guarantee being voided.

It is also cheap to make correct: a `sys.version_info` comparison in
`__main__.py` ahead of the first 3.11-only import costs nothing on every other
run, where a guard in `bin/docket` would cost an extra interpreter start per
call.
