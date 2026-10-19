---
id: PL-70M6
title: bin/docket show prints, for a closed item, the sessions that worked it with each one's model, effort, served model and cost, joined from docs/session-ledger.tsv through the item's pull request, so one item can be read whole without storing session facts on it
priority: P2
effort: S
status: ready
classes: session-cost, infra
feature: model-evidence
touches: subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md
added: 2026-10-19
payoff: one item reads whole in bin/docket show, and the model review joins items to sessions through the same function instead of re-deriving the join each month
verify: grep -rq 'session-ledger.tsv' subprojects/docket/src/docket && grep -q 'session-ledger' subprojects/docket/README.md
---

**Problem.** bin/docket show prints, for a closed item, the sessions that worked it with each one's model, effort, served model and cost, joined from docs/session-ledger.tsv through the item's pull request, so one item can be read whole without storing session facts on it

**Why it matters.** On 2026-10-19 the project owner asked why a closed item does
not carry its model and effort directly. The facts belong to a session, not an
item. On 2026-10-19, 1,877 closed items joined to 916 sessions, about two items
per session. A session also keeps spending after the commit that closes its
item, for example on CI fixes and review rounds. So the ledger (`PL-92ZN`)
stores each session once. What the owner wanted from the per-item form is a
reading in which one item shows everything about it. A join at read time gives
that without a second copy of the facts.

The join is item, then its `pr:`, then the squash commit on `main` whose
subject ends `(#N)`, then that commit's `Claude-Session:` trailers, then
`docs/pr-bodies/` as the fallback, then the ledger rows. The model review
(`PL-63CB`) needs the same join every month. Writing it once in `docket`
follows `CLAUDE.md` § "Architecture and development discipline" (a shared fact
has one source of truth). It is data access, not analysis, so it does not
reopen the owner's refusal of a committed analysis tool recorded on `PL-92ZN`.

**Done when.** `bin/docket show` prints, under a closed item, one line per
joined session: session id, last served model, effort level and cost in USD.
It says so plainly when the item has no `pr:`, when no session joins, or when
a joined session has no ledger row. It must never print an empty list as if
the item had no sessions. A function in `docket` exposes the join for the model
review to call. A test covers the joined, unjoined and missing-row cases, and
`subprojects/docket/README.md` documents the file it reads.

**Generator check.** Asked for by the project owner on 2026-10-19 as a
follow-on to `PL-92ZN`; a one-off, not an instance of a head.
