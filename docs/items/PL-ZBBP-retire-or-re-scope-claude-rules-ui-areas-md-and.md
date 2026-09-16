---
id: PL-ZBBP
title: Retire or re-scope .claude/rules/ui-areas.md and re-point docs/ARCHITECTURE.md when the area system ships, since the rule is a standing prohibition on what v0.6.0 builds and its paths frontmatter does not reach a layout package outside app/
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: M
blocked-by: PL-W9P6
classes: docs
touches: .claude/rules/ui-areas.md, docs/ARCHITECTURE.md
---

**Problem.** Retire or re-scope .claude/rules/ui-areas.md and re-point docs/ARCHITECTURE.md when the area system ships, since the rule is a standing prohibition on what v0.6.0 builds and its paths frontmatter does not reach a layout package outside app/

**Why it matters.** `.claude/rules/ui-areas.md` is a standing prohibition on
exactly what this milestone builds - "Do not build splitting, joining, docking,
workspace tabs or layout persistence ahead of it" - and it tells a reader the
Editor contract does not exist yet. Shipped unchanged it would refuse the code
around it. Its `paths:` frontmatter is `/src/anesthesia_sim/app/**`, which does
not reach a layout package living outside `app/`, so it would also stop loading
for the code it most concerns. `docs/ARCHITECTURE.md` has the matching problem
from the other side: its routing bullet now states its own condition
(`PL-J4NW`), and the condition comes true here.

**Done when.** The rule is retired, or re-scoped to what still holds once the
area system exists with `paths:` that reach the layout package; and
`docs/ARCHITECTURE.md` § "Where new code belongs" routes a display surface by
what it is, with "a new Editor" as a named route, per `PL-TH35`.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 19.
