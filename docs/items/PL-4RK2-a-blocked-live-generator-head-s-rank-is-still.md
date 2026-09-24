---
id: PL-4RK2
title: A blocked live generator head's rank is still lost or misstated in the shapes PL-QFWF leaves: a head whose only startable work sits behind a blocked blocker, or which waits on a milestone alone, ranks nothing and nothing says so, and docket show on the head says it is ranked on the tier
status: untriaged
added: 2026-09-24
---

**Problem.** A blocked live generator head's rank is still lost or misstated in the shapes PL-QFWF leaves: a head whose only startable work sits behind a blocked blocker, or which waits on a milestone alone, ranks nothing and nothing says so, and docket show on the head says it is ranked on the tier

Found 2026-09-24 while fixing `PL-QFWF` (a blocked live generator head's open blockers rank in the generator tier). That fix passes the head's rank to its *direct* open blockers (`plan.generator_blockers`), which covers the one recorded shape: `PL-MB2W`'s design round blocked the head on each of eight build items. Three shapes are still unaccounted for:

- **A chain.** A head blocked on `B`, with `B` blocked on `A` and `A` startable, lifts nothing: `B` is not startable and `A` is not a direct blocker. Following the chain was considered and not built, because every extra edge is a hand-written `blocked-by` that nothing checks for this purpose, and the tier is the one rank above a `safety`-classed `P1`.
- **A milestone blocker alone.** A live head blocked only on a milestone has no item blocker to lift, so the generator is ranked by nothing until the milestone is scoped.
- **`docket show` on the blocked head itself** prints "ranked on the generator tier - above every band but P0" (`cli.py`'s show block, from `ranks_as_generator`), and its plan line says it ranks above every band. Neither is true of a blocked item, and neither names the blockers that carry the rank now.

**Why it matters.** The tier exists so a live generator is paid down before the sessions it taxes. In the first two shapes it goes unranked silently, which is `PL-QFWF`'s defect in a narrower form; the third misleads the session most likely to be reading it - one that named the head.

**Done when.**

- `docket next` or `docket check` names a live head that is blocked with no startable direct blocker, whether through a chain or a milestone, or the chain case is ranked, on a recorded decision about the evidence one more edge needs.
- `docket show` on a blocked live head says it is blocked and names the open blockers carrying its rank, rather than saying the head itself is ranked on the tier.
