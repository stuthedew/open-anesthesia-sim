---
id: PL-4RK2
title: A blocked live generator head's rank is still lost or misstated in the shapes PL-QFWF leaves: a head whose only startable work sits behind a blocked blocker, or which waits on a milestone alone, ranks nothing and nothing says so, and docket show on the head says it is ranked on the tier
priority: P2
effort: M
status: done
classes: defect
feature: generator-identification
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - filed after the freeze by PL-QFWF's close-out (2026-09-24), and not safety or science; generator-machinery defect
added: 2026-09-24
closed: 2026-09-24
payoff: a live generator stays ranked, or is named as unranked, whatever shape its blockers take, and docket show stops telling the reader a blocked head is ranked itself
verify: grep -q 'def test_a_blocked_live_head_whose_rank_reaches_no_startable_item_is_reported' subprojects/docket/tests/test_plan.py && grep -q 'def test_show_on_a_blocked_live_head_says_it_is_blocked_and_names_its_blockers' subprojects/docket/tests/test_cli.py
impairs-generators: plan.generator_blockers passes a blocked live head's rank only to its direct open item blockers, so a head whose rank reaches no startable item through a chain or a milestone blocker is ranked by nothing and nothing says so; cmd_show and plan.placement_line meanwhile tell the reader the blocked head itself is on the tier
recurrences: 2026-09-24 PL-Q4DF withdrawn 2026-09-24 PL-Q4DF
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

**Premise re-checked at triage, 2026-09-24.** The third shape is live today.
`bin/docket show PL-MB2W`, the one blocked live head, prints "ranked on the
generator tier - above every band but P0", and its plan line says the same.
Meanwhile `bin/docket next` ranks two of its blockers, `PL-331V` and `PL-DDYD`,
second and third as "unblocks generator PL-MB2W". The first two shapes are
latent. Of the four heads marked `generator: live`, three sit at
`needs-decision` with no blocker, and `PL-MB2W`'s one blocked blocker,
`PL-FX5Q`, is held by `PL-N162`, which is itself a direct blocker. No live head
has a milestone blocker. The code involved is `plan.generator_blockers`, which
walks only `blocking_items` and one edge, and `cmd_show` with
`plan.placement_line`, which read `model.ranks_as_generator`, a predicate that
never tests `blocked`.

**Generator check.** Not a new cluster. This is the work `PL-QFWF`'s fix left
and named in the commit that closed it, not a re-entry. The shape-three line
misreads the fact `PL-6T44` and `PL-8YXJ` state, an item's current queue
state, and `PL-RJLQ` is deciding that family.
