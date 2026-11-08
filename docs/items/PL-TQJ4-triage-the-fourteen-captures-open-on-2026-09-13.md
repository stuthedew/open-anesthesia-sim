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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Twelve more from the 2026-09-13 triage pass over the fourteen captures open that day** (`PL-TQJ4`). Nine lie wholly in the workflow lane and sit exactly where the first thirty do. They were found after the 2026-09-06 freeze, they are `P2` or `P3`, they are neither `safety` nor `science`, and they are apparatus held to `.claude/rules/apparatus-standard.md`'s deliberately lower bar. The refilling-queue arithmetic above is unchanged and is still the reason. The thirteenth item of that pass, `PL-V6M0`, is admitted above under the unconditional safety exception rather than declined.
