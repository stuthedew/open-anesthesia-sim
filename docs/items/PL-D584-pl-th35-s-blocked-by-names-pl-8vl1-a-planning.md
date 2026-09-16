---
id: PL-D584
title: PL-TH35's blocked-by names PL-8VL1, a planning item that closed 2026-09-12, so bin/docket check advises on every run that the Editor contract is ready to promote - the one thing ROADMAP.md and .claude/rules/ui-areas.md both say it must not do
priority: P2
effort: S
status: ready
classes: defect, docs
feature: interface-areas
touches: docs/items
added: 2026-09-16
verify: bin/docket check && grep -q '^blocked-by: PL-NMTF' docs/items/PL-TH35-*.md
---

**Problem.** PL-TH35's blocked-by names PL-8VL1, a planning item that closed 2026-09-12, so bin/docket check advises on every run that the Editor contract is ready to promote - the one thing ROADMAP.md and .claude/rules/ui-areas.md both say it must not do

**Why it matters.** `PL-8VL1` is `classes: planning, docs`, `touches:
ROADMAP.md` - the item that *recorded* the port's reservation, not the port that
built it - and it closed 2026-09-12. So `bin/docket check` prints "PL-TH35:
every blocker has closed; it is ready to promote" on every run, and a session
acting on that advisory would start the Editor contract while the area system
does not exist. `ROADMAP.md` and `.claude/rules/ui-areas.md` both say that is
the one thing it must not do: "a view's contract is whatever the area system
requires of its contents, so views built first are built against today's fixed
layout and rewritten".

**Why it cannot be fixed by re-pointing the field.** `blocked-by` takes an item
id or a version, and `checks.py` `_check_references` holds the version form to a
milestone the roadmap places. Item 34 is a planned-milestone entry, not a
version, and § "The timeline" gives it no row - so there is nothing to name
until `PL-NMTF` has an answer. `PL-9LNF` is the honest interim: it states the
blocking relationship in prose.

**Done when.** `PL-TH35`'s `blocked-by` names something that has not already
closed, and `bin/docket check` stops advising that the Editor contract is ready
to promote.

**Scope note.** Eight items carry that advisory today. This one is filed because
its ordering is load-bearing and documented in three places; the general
question of stale `blocked-by` fields across the store is not this item.

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Surfaced 2026-09-16 by the area-model audit's completeness critic, after the main sweep had closed - which is the critic earning its place rather than a defect in the sweep.
