---
id: PL-D9GM
title: Scope v0.5.0 - the case you can branch, and freeze Gate 1
priority: P2
effort: M
status: done
classes: planning
feature: scenario-branching
milestone: v0.4.5
touches: ROADMAP.md, docs/items
added: 2026-09-06
closed: 2026-09-06
pr: 380
verify: python3 tools/doc_check.py check && grep -qF '## v0.5.0 - the case you can branch' ROADMAP.md
---

**Problem.** `bin/docket wave` read the beat as *scope v0.5.0*, and the
milestone had no section: no goal, no required scope, no definition of done, no
out-of-scope list, and therefore no frozen debt gate. "The cadence" says a
milestone whose gate has not been recorded has not been scoped, whatever else
has been written about it.

**Why it matters.** v0.5.0 completes the MVP, and scoping is the act that
freezes Gate 1. Until it happened, the gate did not exist, `docket next` could
not place any of the milestone's work (placement is read from a milestone's own
Required scope), and the score architecture the 2026-09-05 design round filed
sat in the queue belonging to no step.

**Where.** `ROADMAP.md` - a new milestone section, the timeline rows for Gate 1
and v0.5.0, and the plan's paragraph naming which rows are still unscoped.

**Done when.** The section exists with all five parts; Gate 1 is recorded in it
as item ids with the date they were frozen; `tools/doc_check.py` holds the
stated counts to the listed entries; and `bin/docket wave` reads the gate and
reports the next beat from it.

**Closed 2026-09-06.** The gate froze at 119 entries - 111 decidable on the
day, plus eight the same day's triage pass admitted under the presence rule.
`bin/docket wave` now reports *clear the gate* against it. Three decisions the
project owner made during the round are recorded in place: the gate freezes
whole, item 8's replay half is the internal resimulation driver only, and two
branches overlay on one time axis rather than sitting in stacked panels.
