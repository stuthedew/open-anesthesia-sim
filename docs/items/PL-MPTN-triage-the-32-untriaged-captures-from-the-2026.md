---
id: PL-MPTN
title: Triage the 32 untriaged captures from the 2026-09-04/05 sessions
priority: P2
effort: M
status: done
classes: planning
feature: planning-cadence
milestone: v0.4.0
touches: docs/items
added: 2026-09-05
closed: 2026-09-05
pr: 330
not-delegable: a triage pass is proven by the state of the store at the moment it ran, and that state moves - captures arrive untriaged by design, three of them in this session - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid
---

**Problem.** Thirty-two captures from the 2026-09-04 and 2026-09-05 sessions
sat untriaged - past `docket.toml`'s `untriaged_stale_days` for none of them
yet, but far enough past the point where an untriaged queue becomes a second
queue nobody reads. Filed under `CLAUDE.md`'s rule that housekeeping taking a
commit of its own is filed before it is done, so the branch carries an id every
in-flight guard can see.

**Why it matters.** An untriaged item is invisible to `bin/docket next`: it has
no band, no effort and no lane, so no session is ever offered it however urgent
it is. Two of the thirty-two are `P2` presentation defects on the compartment
chart, which is the interface `ROADMAP.md` gives v0.4.0 to.

**What the pass did.** Set `priority`, `effort`, `classes`, `touches` and
`feature` on twenty-eight items; dropped four as duplicates with their evidence
folded into the survivors; repaired fifteen briefs whose real content sat below
a dead capture template; and wrote a `verify:` command for each of the fifteen
items reaching `ready`, each run first and watched to fail for the right reason.
Eleven items reached `needs-decision` rather than `ready`, each with a
`**Decision needed.**` section naming the question.

**Done when.** No item captured before this pass is still untriaged, and
`bin/docket check` reports no errors over the store. Both held on
2026-09-05.
