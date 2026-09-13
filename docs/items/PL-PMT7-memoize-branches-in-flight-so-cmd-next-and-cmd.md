---
id: PL-PMT7
title: Memoize branches_in_flight so cmd_next and cmd_digest stop computing _flight twice per invocation
priority: P3
effort: S
status: done
classes: perf
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-03
closed: 2026-09-13
pr: 504
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_next_computes_the_flight_report_once' subprojects/docket/tests/test_cli.py
---

**Problem.** `cmd_next` and `cmd_digest` each compute the flight report twice.
Both call `_offered(root, items, config, args)`, which calls `_flight(args)`
internally (`subprojects/docket/src/docket/cli.py:199`), and then both call
`_flight(args)` again directly — `cli.py:445` for `next`, `cli.py:249` for
`digest`. `_flight` is not memoized and neither is `branches_in_flight`
(`vcs.py:275`); there is no `lru_cache` anywhere in either module. Each call
shells out to git once per branch ref.

**Why it matters.** Small, but it is on the two commands a session runs most,
and `next` is the one the queue exists to answer. Measured on a four-core
container: `next` issues 26 git subprocesses where `flight` and `status` issue
13, and `digest` issues 36. Roughly 180 ms of `next`'s ~460 ms is the repeated
work.

Correctness is the reason to keep the fix narrow rather than the reason to
skip it. `_flight` returns a whole `FlightReport` rather than a set of ids
precisely so that unread refs are never presented as a complete reading, and
`PL-3576` and `PL-S1P1` both closed defects in that area. Caching must be
per-invocation — one process, one answer — and must not outlive the command,
or a long-running caller would rank against a stale view of what is in flight.

**Where.** `subprojects/docket/src/docket/cli.py` (`_flight` at 85, the
duplicate call sites at 199/249/445), `subprojects/docket/src/docket/vcs.py`
(`branches_in_flight` at 275).

**Done when.** `cmd_next` and `cmd_digest` each compute the flight report once,
the git subprocess count for `next` drops to `flight`'s, and a test asserts the
single computation rather than only the timing. The `FlightReport` a caller
receives is unchanged, unread refs included.

**On this item's own `verify:` cost.** Measured 2026-09-05, before `#328`
(`PL-VZ8P`, size the pytest pool for a suite that waits on subprocesses),
`docket check --verify` named this item's `verify:` command among its five costliest at
22 s against a 0.7 s median, and asked for a judgment. After `#328` it is off
that list; the command itself still takes about 15 s standalone, so what moved
is the ranking rather than the cost.

The judgment either way is to keep it. `subprojects/docket/tests/test_cli.py`
is already the only suite covering `cmd_next`, and its runtime is git
subprocesses rather than test count - which is the same cost this item exists
to remove, so the command gets cheaper when the work lands. Do not re-litigate
it by scoping the run with `-k`: that would cost the paired shape's first half,
which is there to prove the file's suite healthy.
