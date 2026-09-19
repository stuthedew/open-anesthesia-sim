---
id: PL-TPS7
title: Cut the prose in docs/ARCHITECTURE.md and docs/maintainer.md
priority: P2
effort: S
status: ready
classes: docs
feature: prose-quality
touches: docs/ARCHITECTURE.md, docs/maintainer.md
added: 2026-09-05
not-delegable: readability is judged by a person, and no command separates trimmed prose from padded prose. A line-count ceiling would be met by deleting a statement to reach a number, and `doc_check.py check` passes today
---

**Problem.** `docs/ARCHITECTURE.md` (~550 lines) and `docs/maintainer.md` (~50)
are, in the project owner's reading (2026-09-05), more verbose than they need
to be. One of five per-target items split out of `PL-3VKZ` (rewrite the
human-facing markdown prose), which was `L` and therefore unstartable from the
queue. The two are one item because together they are smaller than any of the
other four.

**Why it matters.** `docs/ARCHITECTURE.md` is where a contributor goes to find
out how the pieces fit before changing one, and `docs/maintainer.md` is what
the project owner reads to act on something only they can act on. Both are
reference documents consulted under time pressure, which is the reading a long
paragraph serves worst. The standard is **human readability**, deliberately not
`PL-JK0M`'s routing standard for the agent-facing instruction files.

**Where.** `docs/ARCHITECTURE.md`, `docs/maintainer.md`. Counts are measured 2026-09-05 and rounded because they move every release; re-measure before starting rather than trusting them - they are here for ordering, not as a claim.

**Done when.** Both documents have been read end to end and cut: no paragraph
restating the one above it, no clause that adds nothing, no section that could
be a sentence. Every statement of *why* a boundary exists survives. `make
check` passes, so no package-map entry, citation or documented make target was
broken by the edit.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** No cut has landed - the only
commit naming this item is the triage split that created it, and every commit
touching `docs/ARCHITECTURE.md` since has added content for other items. Its
own instruction to re-measure is why the numbers are given rather than kept:
the two files were **576** and **49** lines at the filing commit `8250816`, and
are **1155** and **83** today. Both have roughly doubled, so the premise moved
in the direction that makes this item larger rather than smaller.
