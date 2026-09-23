---
id: PL-59QW
title: ROADMAP.md's gate deferral entries narrate an item's status ('At needs-decision') and nothing re-reads them when the item closes - PL-WNCT's still said needs-decision after #941 merged; PL-8YXJ's brief-contradiction check reads briefs only, so this is its mechanism at a sibling site
priority: P3
effort: S
status: ready
classes: defect
feature: brief-state-agreement
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_checks.py, ROADMAP.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
payoff: the gate's deferral list stops telling a reader that a closed item still waits on a decision
verify: grep -q 'def test_a_deferral_entry_narrating_a_status_its_item_left_is_reported' subprojects/docket/tests/test_checks.py
---

**Problem.** ROADMAP.md's gate deferral entries narrate an item's status ('At needs-decision') and nothing re-reads them when the item closes - PL-WNCT's still said needs-decision after #941 merged; PL-8YXJ's brief-contradiction check reads briefs only, so this is its mechanism at a sibling site

**Reproduced at triage, 2026-09-23, on a different entry.** The `PL-WNCT` entry
cited above has since had its close appended ("Decided the same day, and closed
with it in `#941`"). `PL-YZJD`'s deferral entry ("deferred 2026-09-21") still
reads "At `needs-decision`" with the item `done` and nothing appended - found by
comparing each of the 27 deferral entries' narrated status with its item's front
matter.

**Why it matters.** The deferral list is what `bin/docket wave` and a scoping
round read the gate from, so a closed item described as awaiting a decision
sends the reader after a question already answered. The repair so far has been
by hand, one entry at a time, whenever somebody notices.

**Done when.** `bin/docket check` reports a gate deferral entry in `ROADMAP.md`
narrating a status its item's front matter contradicts, reading the entries
`docket.roadmap` already parses and honouring the exemptions `PL-8YXJ`'s brief
reading does - a dated `superseded` marker, a quotation, an appended close - and
`PL-YZJD`'s entry is repaired in the same change.

**Generator check.** An instance of `PL-8YXJ`'s mechanism - queue state stored
twice, the prose copy re-read by nothing when the front matter moves - at a
sibling site. Filed in `9d14b0ae`, after the head closed in `#935`: the first
post-close instance on record, and two more would make it a generator whose fix
did not hold.
