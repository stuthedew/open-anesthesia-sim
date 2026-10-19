---
id: PL-ZBBP
title: Retire or re-scope .claude/rules/ui-areas.md and re-point docs/ARCHITECTURE.md when the area system ships, since the rule is a standing prohibition on what v0.6.0 builds and its paths frontmatter does not reach a layout package outside app/
priority: P2
effort: M
status: done
classes: docs
feature: interface-areas
milestone: v0.5.34
touches: .claude/rules/ui-areas.md, docs/ARCHITECTURE.md
blocked-by: PL-TH35
added: 2026-09-16
closed: 2026-10-19
pr: 1630
payoff: the rule that loads on the interface code describes the area system as built, and loads on the layout package too
verify: ! grep -q 'Do not build splitting, joining, docking' .claude/rules/ui-areas.md
---

**Problem.** Retire or re-scope .claude/rules/ui-areas.md and re-point docs/ARCHITECTURE.md when the area system ships, since the rule is a standing prohibition on what v0.6.0 builds and its paths frontmatter does not reach a layout package outside app/

**Why it matters.** `.claude/rules/ui-areas.md` is a standing prohibition on
exactly what this milestone builds - "Do not build splitting, joining, docking,
workspace tabs or layout persistence ahead of it" - and it tells a reader the
View contract does not exist yet. Shipped unchanged it would refuse the code
around it. Its `paths:` frontmatter is `/src/anesthesia_sim/app/**`, which does
not reach a layout package living outside `app/`, so it would also stop loading
for the code it most concerns. `docs/ARCHITECTURE.md` has the matching problem
from the other side: its routing bullet now states its own condition
(`PL-J4NW`), and the condition comes true here.

**Done when.** The rule is retired, or re-scoped to what still holds once the
area system exists with `paths:` that reach the layout package; and
`docs/ARCHITECTURE.md` § "Where new code belongs" routes a display surface by
what it is, with "a new View" as a named route, per `PL-TH35`.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 19.

## [superseded 2026-10-19] Blocked on `PL-TH35`, 2026-10-18

`PL-W9P6` closed on 2026-10-18 in `#1592`. This item's Done-when asks for a
route for a new View that follows `PL-TH35`'s View contract. That contract is
not written yet, so this item waits on it.

## Ready since `PL-TH35`, 2026-10-19

`PL-TH35` wrote the route for a new View into `docs/ARCHITECTURE.md`
§ "Where new code belongs", so that half of the Done-when is met. It also
replaced `.claude/rules/ui-areas.md`'s sentence saying the contract was not
designed yet with a pointer to `app/view_contract.py`. What is left is the
rule itself: its prohibition on building splitting, joining, docking,
Workspace tabs and layout persistence ahead of item 34, which v0.6.0 is now
building, and its `paths:`, which do not reach `src/anesthesia_sim/layout/`.
