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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "The plan" carried this paragraph under § "The timeline", after the paragraph on row 7. "Row 5" is the timeline's row for v0.5.0, and "here" is the timeline. § "Development pathway" -> "Phase 3 — reproducibility and comparison" keeps the paragraph's lasting fact: what v0.5.0 took, what it left out, and that it departs from Phase 3's sequence of items 9, 10, 11 and 12.

> Row 5's internal ordering put forking and comparison ahead of save/load and replay. That ordering was first recorded here as a proposal, not a decision. The reason given was that branching within one session is what does the teaching, while persistence is a convenience. Scoping row 5 decided the question, and the decision matched the proposal. v0.5.0 takes items 26, 12 and 11, with only the *replay driver* half of item 8. It puts save/load (item 9) and a user-facing replay control (item 10) out of scope. That is a deliberate departure from the Phase 3 sequence in "Development pathway". That sequence no longer applies to these four items.
