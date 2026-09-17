---
id: PL-FBXP
title: Record the seven pull request numbers owed by the closures that reached main on 2026-09-16
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.4.26
touches: docs/items/
added: 2026-09-16
closed: 2026-09-16
pr: 633
verify: bin/docket record
---

**Problem.** Seven closures reached `origin/main` on 2026-09-16 - `PL-9PD6`,
`PL-D584`, `PL-J4NW`, `PL-JQJQ`, `PL-NMTF`, `PL-R0Q0` and `PL-XWH4` - and none
carried the `pr` field yet. `bin/docket record` writes it only once the closure
is on the default branch, which is why it declines at merge time and the number
is owed afterwards; `docket check` recovers a closed item's pull request from
the newest commit subject naming it, so an unrecorded number leaves that
recovery doing the work on every read.

**Where.** `docs/items/`, seven front matters. `PL-NLP4` is the precedent: the
same job, batched the same way, rather than one commit per merge.

**Done when (met).** `bin/docket record` reports nothing owed.

**Filed before the work rather than after it.** No item named this, and every
in-flight guard this project has matches a `PL-` id, so the commit needed one
of its own to be visible to another session's `bin/docket next`. Recorded as
`pr: 629` for the five that shipped together, `pr: 628` for `PL-R0Q0` and
`pr: 630` for `PL-JQJQ`.
