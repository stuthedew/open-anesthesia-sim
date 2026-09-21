---
id: PL-M6FY
title: cli.cmd_flight builds its own GitRunner instead of the invocation's, so flight loses the cat-file memo every other command shares
priority: P3
effort: S
status: ready
classes: perf
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-21
payoff: flight costs what every other branch-walking command costs, rather than re-asking git what the invocation already knows
verify: grep -q 'def test_flight_shares_the_invocations_git_runner' subprojects/docket/tests/test_cli.py
---

**Problem.** cli.cmd_flight builds its own GitRunner instead of the invocation's, so flight loses the cat-file memo every other command shares

**Measured 2026-09-21.** `cmd_flight` calls `branches_in_flight` with the root
and the items directory and no runner, so the library builds one of its own and
the memo `_runner` keeps for the life of the invocation is never reached.

**Why it matters.** A cost rather than a wrong answer - the report is identical
either way, which is why this is `perf` and sits in the bottom band. What it
loses is the one command whose whole job is a per-branch read: every other
command that walks the same refs shares a memo, and the command dedicated to
walking them does not.

**Done when.** `cmd_flight` passes the invocation's runner through, and a test
in `subprojects/docket/tests/test_cli.py` shows the same runner reaching the
library call.
