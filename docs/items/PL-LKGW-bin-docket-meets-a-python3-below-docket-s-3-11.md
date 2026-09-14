---
id: PL-LKGW
title: bin/docket meets a python3 below docket's 3.11 floor with render.py's ImportError traceback rather than naming the floor and the interpreter it found, so a Mac whose python3 is Apple's 3.9 gets a cryptic failure by hand and silent hooks with nothing saying why
status: untriaged
added: 2026-09-14
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
