---
id: PL-K2ZK
title: The session-start digest could deepen the clone once so the in-flight read answers instead of declining
status: untriaged
added: 2026-08-31
---

**Problem.** The session-start digest could deepen the clone once so the in-flight read answers instead of declining

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `PL-MGNC` stops `branches_in_flight` believing a walk the
checkout's history cannot support, which is right and is not the whole
opportunity: the answer it declines to give is one a single `git fetch` makes
available. The incident of 2026-08-31 was cured that way - `git fetch origin
main` deepened the clone and the same command in the same checkout then
reported nothing in flight.

So the guard converts a wrong answer into no answer, where a fetch would
convert it into the right one.

**Why it matters.** A truncated clone is the normal state of a session
container, not an edge case, so whatever share of refs the guard declines is
declined in every session. `docket next` cannot see what it declined
(`PL-S1P1`), so the cost is paid as items offered twice.

**Where.** The session-start hook rather than `vcs.py`, and that split is the
design. `merged_pull_requests` documents why the library must not fetch:
`docket check` runs from a bare tree with no network, and a read that reaches
for the network is one that cannot. A hook running at session start is the
opposite case - it has network, it runs once, and its cost is paid before the
session does anything.

**Done when.** Either the hook deepens the checkout enough for the in-flight
read to answer, with the cost measured and a failure that is silent when there
is no network, or the measurement shows it is not worth the session-start
latency and this is dropped with that number.

**Not a substitute for the guard.** A session with no network, or one whose
fetch fails, still gets a truncated history, and the guard is what stops that
answering wrongly.
