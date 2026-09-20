---
id: PL-7JN7
title: Triage PL-GJPD and PL-WG7Q: both landed in #717 after PL-CSV0's triage pass was scoped, so no pass covers them and they stay invisible to bin/docket next
status: dropped
added: 2026-09-19
closed: 2026-09-20
reason: Superseded by PL-WQF1's triage pass, which seated both ids it names: PL-GJPD at P2/M/defect/ready and PL-WG7Q at P2/S/defect/blocked with blocked-by PL-GJPD. Nothing is left for a separate pass to do.
---

**Problem.** Triage PL-GJPD and PL-WG7Q: both landed in #717 after PL-CSV0's triage pass was scoped, so no pass covers them and they stay invisible to bin/docket next

**Dropped at triage, 2026-09-20: this pass is the pass it asks for.** `PL-WQF1`
(triage the 22 untriaged captures standing in the queue on 2026-09-20) covers
both ids it names. `PL-GJPD` is seated `P2`/`M`/`defect` at `ready` under
`feature: commit-provenance`; `PL-WG7Q` is seated `P2`/`S`/`defect` at
`blocked`, with `blocked-by: PL-GJPD` recording the sequencing its own brief
asked for. Both now carry a `verify:` and a `payoff:` and are visible to
`bin/docket next`, which is the whole of what this item wanted.

Recorded rather than deleted because the finding underneath it is real and
recurs: a capture landing between the moment a triage pass is scoped and the
moment it runs is covered by no pass, and nothing reports the gap. That is a
standing property of scoping a pass by a list rather than by a query, not a
defect in either pass, and the remedy is the one this item took - notice the
strays and file them. `bin/docket triage` reads the store live, so the next
pass sees whatever has landed; what it cannot see is a capture that arrives
while it is running.
