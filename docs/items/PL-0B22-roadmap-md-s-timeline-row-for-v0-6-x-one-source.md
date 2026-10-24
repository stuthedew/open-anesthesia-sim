---
id: PL-0B22
title: ROADMAP.md's timeline row for v0.6.x - one source of truth still says 'Not yet scoped or sized' after PL-K88Z sized it on 2026-10-19, so the row and planned-milestone item 43 disagree
priority: P3
effort: S
status: ready
classes: docs
feature: one-source-of-truth
touches: ROADMAP.md
added: 2026-10-24
payoff: the roadmap's row and its milestone item agree that the one-source-of-truth work is sized and still to be scoped
verify: ! grep -qF 'Not yet scoped or sized' ROADMAP.md
---

**Problem.** ROADMAP.md's timeline row for v0.6.x - one source of truth still says 'Not yet scoped or sized' after PL-K88Z sized it on 2026-10-19, so the row and planned-milestone item 43 disagree

**Found 2026-10-24** on `main` at `345e8bb2`. Planned-milestone item 43 in `ROADMAP.md` records the size from `PL-K88Z` in a sentence that begins "Inventoried 2026-10-19". The row for the same work in § "The timeline" still ends "Not yet scoped or sized." The row is sized now. What is still missing is the scoping, meaning a decision about which of the feature's items the row needs before it counts as done. Fix the row so it says that, and do the scoping when the feature's 13 untriaged items are triaged.

**Why it matters.** The timeline row and planned-milestone item 43 describe the same work and now disagree about whether it has been sized. A session reading only the row would size it again, or would treat the work as further from ready than it is.

**Done when.** The `v0.6.x — one source of truth` row in § "The timeline" says the work is sized and points at item 43's "Inventoried 2026-10-19" sentence for the size, and says that scoping is still to come. Scoping itself, which decides which of the feature's items the row needs, is release work and is not part of this item.

**Checked 2026-10-24.** The row still ends "Not yet scoped or sized.", and item 43 carries the size.
