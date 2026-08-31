---
id: PL-S1P1
title: The in-flight ids reach docket next without the refs that went unread
priority: P3
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-08-31
verify: uv run pytest subprojects/docket/tests/test_vcs.py -k unread
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

**Triaged 2026-08-31.** P3, `defect`/`infra`, `parallel-sessions` beside
`PL-CPSY` (a squash-merged branch whose ref survives reports its items in
flight forever) and `PL-KWC1` (read in-flight ids from the commits).

P3 rather than P2, and the split from `PL-CPSY` is deliberate. Both are holes
in the same function's answer, but `PL-CPSY` fires on a condition this project
meets today - squash-merge has been the merge strategy since 2026-08-30 - while
this one needs a ref that is fetched *and* truncated below its merge-base, which
the container measured on 2026-08-31 did not have. It is a
correctness-of-reporting hole with no observed instance, which is what the
lower band is for. It should not be worked ahead of `PL-CPSY`; they collide on
`vcs.py` anyway, so one session or a serialized pair.

The `verify:` command keys on `unread`, matching the word the Problem uses for
the dropped half of the `FlightReport`; nothing in `test_vcs.py` selects on it
today.

Not admitted to v0.2.8's frozen list: it completes no entry. `PL-KWC1` is an
entry and is `done`; this is `in_flight_ids` discarding a field `PL-KWC1` did
not add and does not depend on.
