---
id: PL-Q4DF
title: A blocked impairs-generators item passes its rank to nothing and nothing names it: generator_blockers lifts only a root-cause head's blockers, so a machinery defect waiting on another item drops off the generator tier silently
status: untriaged
feature: generator-identification
added: 2026-09-24
---

**Problem.** A blocked impairs-generators item passes its rank to nothing and nothing names it: generator_blockers lifts only a root-cause head's blockers, so a machinery defect waiting on another item drops off the generator tier silently

Found 2026-09-24 while fixing `PL-4RK2` (a blocked live generator head's rank
is lost or misstated). `plan.generator_blockers` hands a blocked item's tier
rank to its open blockers only when the item is a root-cause head
(`ranks_as_generator`). The tier's other entrance, a sound
`impairs-generators:`, gets no such pass. A machinery defect at `blocked`
therefore ranks nothing, its blockers rank on their bands, and
`plan.unranked_generators` does not name it either, because it reads heads
alone. `PL-4RK2` fixed only what `docket show` says about it: the line now
reads "blocked, so ranked nowhere until it can start" instead of "ranked on the
generator tier".
`docket generators` still says it ranks: `render._outside_clusters` counts every
open sound `impairs-generators:` item as "ranks on the generator tier", printing
`(blocked)` beside the id in the same sentence.

**Not a refiling of `PL-4RK2`.** `docket new` matched this capture to that item
on shared paths. It is the sibling entrance to the tier, with a decision of its
own to make: whether `CLAUDE.md`'s "ranks with one" for a machinery defect
reaches the work it waits on. `PL-QFWF` made that call for heads only. So the
match is withdrawn on `PL-4RK2` with this item as the reason.

**Done when.** A blocked `impairs-generators:` item either passes its rank to
its open blockers, on a recorded decision, or is named by `docket next` the way
`unranked_generators` names a head.
