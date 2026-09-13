---
id: PL-TQJ4
title: Triage the fourteen captures open on 2026-09-13
priority: P2
effort: S
status: done
classes: infra
feature: queue-hygiene
milestone: v0.4.18
touches: docs/items
added: 2026-09-13
closed: 2026-09-13
pr: 526
verify: test -z "$(grep -l '^status: untriaged' docs/items/*.md)"
---

**Problem.** Triage the fourteen captures open on 2026-09-13

**Why it matters.** Filed before the pass rather than after it, per
`CLAUDE.md`'s rule that housekeeping taking a commit of its own is filed first:
every in-flight guard this project has matches a `PL-` id, so a triage pass
run under no id is invisible to `bin/docket flight`, `show`, `next` and the
digest, and stays invisible after both sessions have pushed (`PL-CP74`).

**Done when.** The fourteen captures open on 2026-09-13 carry the fields
`bin/docket check` requires, each with the full brief, and nothing in
`docs/items/` is left at `status: untriaged`.
