---
id: PL-X7RZ
title: Triage the 20 untriaged captures and record the gate disposition each newly seated debt item owes
priority: P2
effort: M
status: done
classes: planning
feature: queue-hygiene
touches: docs/items, ROADMAP.md
added: 2026-09-19
closed: 2026-09-19
verify: grep -qF 'Added 2026-09-19 under the unconditional safety/science exception' ROADMAP.md
---

**Problem.** Triage the 20 untriaged captures and record the gate disposition each newly seated debt item owes

**Why it matters.** Twenty captures had reached the store without a band, an
effort, a class or a `touches`, which is the second queue nobody reads that
`untriaged_stale_days` exists to name: `bin/docket next` cannot rank them,
`bin/docket concurrent` cannot reason about them, and neither lane claims them.
Filed under its own id because the pass takes a branch of its own, per
`CLAUDE.md`'s housekeeping rule, and because a triage pass that seats debt items
also owes `ROADMAP.md` a disposition for each - `tools/doc_check.py`'s
`records no disposition` check fails `make check` until it has one, which is how
the ROADMAP half of this pass came to be part of it rather than a separate
change.

**Done when.** Nineteen of the twenty carry a priority, an effort, a class set,
a `touches` and a status past `untriaged`, with a `verify:` on every one set
`ready` and a `**Decision needed.**` section on every one set `needs-decision`;
`PL-Q9Z1` is left alone because a branch already carries it; and every debt item
the pass seats is either on v0.5.0's frozen list or in its
`### Declined to Gate 2` subsection with a reason, so `make check` passes.
