---
id: PL-F2NX
title: Sweep Gate 3's frozen list for staleness: read each of v0.7.0's frozen entries against the tree, drop what no longer reproduces with its reason, and correct briefs that overstate what is left
priority: P2
effort: M
status: ready
classes: housekeeping
feature: gate-staleness-sweep
touches: docs/items
added: 2026-10-25
payoff: Gate 3 is worked on evidence: entries that no longer reproduce stop being ranked and offered, and briefs say what is actually left.
verify: grep -qE "^Swept on 20[0-9-]+" docs/items/PL-F2NX-*.md
---

**Problem.** Gate 3 froze on 2026-10-25, the day `PL-LF0P` scoped v0.7.0, and
nobody has read its entries against the tree yet. Beat 3 of `ROADMAP.md`
§ "The cadence" asks for that pass before any entry is worked. A `verify:`
command tests for the fix and never for the fault, so an entry whose problem
was solved another way fails forever and reads as outstanding work.

**Why it matters.** The two measured passes found 32% of one list dead or
overtaken (`PL-6ZQY`) and about 6.5% of Gate 2's (`PL-C4W8`). Without the
pass, sessions spend work on entries that no longer reproduce, and
`bin/docket next` keeps ranking them.

**Done when.** Each open entry of `ROADMAP.md` § "v0.7.0 - the schematic"
→ "Debt gate: the frozen list" has been read against the tree. Each one that
no longer reproduces is `dropped` with its reason. Each brief that overstates
what is left carries a dated `**Checked 2026-MM-DD:**` paragraph saying what
is left, as the docket skill's sweep rule asks.
