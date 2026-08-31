---
id: PL-019F
title: The 'what should we work on next' rule answers at feature altitude, one level below the roadmap step that should decide it
priority: P3
effort: S
status: ready
verify: python3 tools/doc_check.py check
classes: infra
feature: planning-cadence
touches: CLAUDE.md
added: 2026-08-26
---

**Problem.** `CLAUDE.md`'s rule reads: "Answer 'what should we work on next?'
at feature altitude. `bin/docket status` groups the project the way a decision
is actually made". Feature altitude is one level below the level that should
decide the answer. `ROADMAP.md`'s timeline has a *step* — clearing a gate,
implementing a scoped milestone, closing a release, or scoping the next
milestone from broad intent — and which step the project is on determines
whether any feature is the right answer at all.

**Why it matters.** A session can give a perfectly well-formed feature-altitude
answer while the correct answer is "v0.3.0 is complete; the next step is to
scope v0.4.0, and no queue item is the right work right now." The rule as
written cannot produce that answer, because `docket status` reads
`docs/items/` and the timeline step is not in `docs/items/`. The other rules
in the same section already assume the project-step view exists — "Clear
recorded debt before a new milestone begins", "Close the loop back to the
roadmap", "Offer the release; do not wait to be asked" — so the altitude rule
is the odd one out rather than a deliberate choice.

**Where.** `CLAUDE.md`, the "Answer 'what should we work on next?' at feature
altitude" bullet under "The queue, and how the project owner works". A small
edit: name the project step first, then drop to `docket status` for the
feature and `docket next` for the item.

**Done when.** The rule names the roadmap step as the first thing to answer
from, and feature altitude as the second.

**Context.** The one substantive point salvaged from a closed external
planning proposal (PRs #59/#60, a `docs/PLANNING.md` describing rolling-wave
planning), reviewed 2026-08-26. The rest of that proposal restated
`ROADMAP.md` and `CLAUDE.md` in a third file that nothing reads, and
duplicated the release train, so it was not adopted. Related but distinct from
`PL-F58L`, which makes the roadmap step *visible* at session start; this item
is about a session using it when asked directly. `PL-F58L` landing first would
make this edit more useful but is not a prerequisite.

**Note on a second finding folded in here.** That proposal also stated
"do not maintain a second long-range task-by-task implementation plan; it will
become stale faster than it can be kept authoritative." `ROADMAP.md` implies
this (rows 4-8 "are not yet scoped; each becomes real only when it gets its own
goal, required scope, definition of done and out-of-scope list here") but never
states the prohibition. Worth one sentence in `ROADMAP.md`'s development rules
while making the edit above; not worth its own item.

**Folded into `PL-DGM4`'s branch (2026-08-31)** (the instruction-writing rules and
the docket skill prescribe opposite openings for a 'what next' reply). That item had to edit this same `CLAUDE.md` bullet to make it agree with rule 10, so
the two were worked on one branch rather than contending on one paragraph. The
bullet now names the step `bin/docket wave` reports as the first thing to
answer from, `bin/docket status` second and `bin/docket next` third, and opens
the reply with the recommendation.
