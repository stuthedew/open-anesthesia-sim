---
id: PL-2J5X
title: PL-X3NY carries a real recommendation in its ninth paragraph with no marker on it, so the advisory PL-M21Q added reports it correctly and the four-character repair has not been made
priority: P3
effort: S
status: dropped
classes: housekeeping
touches: docs/items
added: 2026-09-20
closed: 2026-09-26
reason: no longer relevant. PL-X3NY's question was decided on 2026-09-22 for route 1, and #924, which recorded that decision in its bold `Decided 2026-09-22` paragraph, moved it from `needs-decision` to `ready`. The PL-M21Q advisory takes only `needs-decision` items (the `unmarked` list in `_groom`, `subprojects/docket/src/docket/checks.py`), so it no longer reports PL-X3NY: `bin/docket check` on origin/main 041e1603 names neither item. The unmarked paragraph is route 2, the answer the decision went against, so the marker this item's `verify:` asks for would now label the route not taken as the recommendation, beside the decision that superseded it
payoff: the recommendation PL-X3NY already carries becomes findable by the owner answering it, instead of sitting unmarked in a ninth paragraph
verify: grep -qE '[*][*]Recommend' docs/items/PL-X3NY-bin-docket-stranded-reports-in-flight-pull.md
---

**Problem.** PL-X3NY carries a real recommendation in its ninth paragraph with no marker on it, so the advisory PL-M21Q added reports it correctly and the four-character repair has not been made
