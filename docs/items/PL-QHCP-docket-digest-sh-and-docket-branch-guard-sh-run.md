---
id: PL-QHCP
title: docket-digest.sh and docket-branch-guard.sh run bin/docket with 2>/dev/null, so the one-line Python-floor refusal PL-LKGW added reaches a person at a terminal and never a session: a session whose python3 is below 3.11 still starts with no digest and nothing saying why
priority: P3
effort: S
status: ready
classes: defect
feature: dev-tooling
touches: .claude/hooks/docket-digest.sh, .claude/hooks/docket-branch-guard.sh, tests/unit/test_docket_digest_hook.py, tests/unit/test_docket_branch_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-26
payoff: a session on a python3 below 3.11 is told at start which interpreter to fix, instead of starting with no digest and no reason
verify: grep -q 'def test_a_python_below_the_floor_is_named_at_session_start' tests/unit/test_docket_digest_hook.py && grep -q 'def test_branch_guard_names_a_python_below_the_floor' tests/unit/test_docket_branch_guard.py
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

Premise re-read 2026-09-26 against `origin/main` (`17c9f3ed`): both redirects
are still there, at `.claude/hooks/docket-digest.sh` lines 65 and 71 and
`.claude/hooks/docket-branch-guard.sh` line 66.

**Why it matters.** `PL-LKGW` made `bin/docket` name the Python floor so that a
session on an old interpreter is told what to fix. These two hooks are the only
channel a session reads at start and before its first edit, and both send that
line to `/dev/null`. So the session starts with no digest and no reason, and
nothing it reads points at the interpreter.

**Done when.** With a `python3` below 3.11 first on `PATH`, both hooks put
`bin/docket`'s floor line where the session reads it, and each still exits 0.
Above the floor, what each prints is unchanged. A test in each hook's test file
shows it.

**Generator check.** A one-off: the hook half of `PL-LKGW`'s title, which that
item's close left open and filed in its closing commit (`1139738d`, #1052). The
fact is which of `bin/docket`'s output streams a hook passes on to the session.
Each hook states it for itself, as `2>/dev/null`, and no head's `misread:`
covers it.
