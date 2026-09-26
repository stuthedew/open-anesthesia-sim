---
id: PL-QHCP
title: docket-digest.sh and docket-branch-guard.sh run bin/docket with 2>/dev/null, so the one-line Python-floor refusal PL-LKGW added reaches a person at a terminal and never a session: a session whose python3 is below 3.11 still starts with no digest and nothing saying why
status: untriaged
added: 2026-09-26
---

**Problem.** docket-digest.sh and docket-branch-guard.sh run bin/docket with 2>/dev/null, so the one-line Python-floor refusal PL-LKGW added reaches a person at a terminal and never a session: a session whose python3 is below 3.11 still starts with no digest and nothing saying why

**Found 2026-09-26** while closing `PL-LKGW` (bin/docket names the Python
floor instead of an ImportError traceback), and re-observed under
`/usr/bin/python3.10` linked as `python3` first on `PATH`: `bin/docket digest`
prints `docket needs Python 3.11 or newer; this is Python 3.10.20, at
.../python3` and exits 1, but `bash .claude/hooks/docket-digest.sh` prints only
`tools/dead_ends.py`'s lines and exits 0. Its `bin/docket branch --brief` and
`bin/docket digest` calls send stderr to `/dev/null`, and
`.claude/hooks/docket-branch-guard.sh` does the same for its
`bin/docket branch --brief --if-stale`. So the half of `PL-LKGW`'s title about
silent hooks is still true: the line exists, and nothing a session reads
carries it.
