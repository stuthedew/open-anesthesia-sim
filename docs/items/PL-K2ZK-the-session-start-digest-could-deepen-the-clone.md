---
id: PL-K2ZK
title: The session-start digest could deepen the clone once so the in-flight read answers instead of declining
priority: P3
effort: S
status: needs-decision
classes: infra, session-cost
feature: parallel-sessions
touches: .claude/hooks/docket-digest.sh, subprojects/docket/README.md
added: 2026-08-31
---
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

**Decision needed.** Is a session-start fetch worth its latency? The measurement
that answers it is the added wall-clock of deepening this container's checkout
far enough for the in-flight walk to complete, against how often the walk
currently declines. Either the hook deepens the checkout and fails silently
without network, or the number says no and this is dropped with it.

**Measured 2026-09-02, in a session container of the ordinary kind.** The
number the decision asked for: `git fetch --unshallow origin` cost **3.4 s**
of wall clock, took the history from 52 to 542 commits, and grew `.git` from
8.8 MB to 11 MB. Before it, `bin/docket flight` declined on two refs (`main`
and `origin/Review_articles`) and the session-start digest carried the "2 refs
could not be compared with origin/main on the history this checkout holds"
line; immediately after it, `flight` answers and the line is gone. So the
whole of the declined answer is bought for 3.4 s, once per container, spent
before the session does anything — against a decline paid in every session for
the life of that container. `bin/docket stranded` read 0 both before and
after, so the deepening changed what the tools *can* answer without changing
what they did answer.

Two implementation notes the measurement raises. `--unshallow` is the whole
history and is cheap only because this repository is small; `--deepen=N` is
the bounded alternative if that stops being true. And the fetch must fail
silently — a container with no network must still start, per the guard
`PL-MGNC` put in, which this does not replace.

**Triaged 2026-09-01.** P3, `infra`/`session-cost`, `parallel-sessions`. Left
out of v0.2.8's frozen list: `PL-MGNC` made the declining behaviour correct on
purpose, so this asks the digest to answer a question it currently refuses to
answer wrongly - new capability, not a misfire.
