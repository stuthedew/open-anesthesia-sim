---
id: PL-S1P1
title: The in-flight ids reach docket next without the refs that went unread
status: untriaged
feature: parallel-sessions
added: 2026-08-31
---

**Problem.** `branches_in_flight` returns a `FlightReport` that names both what
is in flight and the refs whose merge-base with the default branch could not
be read - history a truncated clone does not hold. `in_flight_ids` drops the
second half, because a `set[str]` cannot carry it, and that set is what
`docket next`, `list`, `status`, `concurrent`, `delegable` and the session
digest all read. Only `docket flight` prints the gap.

**Why it matters.** It is the shape of failure this package guards against
everywhere else: `PullRequestHistory.declined` and `StrandedReport.declined`
both exist so a check that could not run is reported as such rather than as a
clean result. Here the same partial answer is presented as a complete one - a
session is told nothing is in flight when the truth is that one ref could not
be read - and the collision it prevents is discovered at push time.

The exposure is bounded: a ref must be fetched *and* truncated below its
merge-base for this to fire, which the container measured on 2026-08-31 was
not (all four refs resolved). It is a correctness-of-reporting hole rather
than an observed failure.

**Where.** `subprojects/docket/src/docket/vcs.py` - `in_flight_ids`; the
digest line in `render.format_digest`; `subprojects/docket/README.md`.

**Done when.** A session whose checkout could not read a ref is told so where
it reads the queue, not only when it runs `docket flight`, and a test covers
the digest saying it.
