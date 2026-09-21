---
id: PL-S5Q9
title: Defer PL-WZVZ from Gate 1 to Gate 2 in ROADMAP.md, recording why a safety-classed entry may be deferred
priority: P2
effort: S
status: done
classes: docs
milestone: v0.5.0
touches: ROADMAP.md
added: 2026-09-20
closed: 2026-09-20
pr: 777
payoff: stops the v0.5.0 cut meeting an open safety-classed gate entry with no recorded destination and having to decide what to do with it at release time
verify: grep -qF 'It clears in Gate 2, and v0.5.0 ships without it' ROADMAP.md
---

**Problem.** Defer PL-WZVZ from Gate 1 to Gate 2 in ROADMAP.md, recording why a safety-classed entry may be deferred

**Where this came from.** The project owner, 2026-09-20: *"Let's move PL-WZVZ
to gate to 0.6.0 if we aren't doing it till then."* The condition holds -
`PL-WZVZ` is `blocked-by: PL-TH35, PL-R1WQ`, the View contract and the view
registry, both placed by v0.6.0 - so it is not merely undone but unbuildable
before that release.

**What was already recorded, and what was missing.** `ROADMAP.md`'s Gate 1
section already carried `PL-WZVZ` as deferred, with the reason (item 34's
standing rule that no new display surface is built before the View contract).
What it did not say is *where the entry lands*. An entry deferred to nowhere is
what holds a release open: Gate 1 ships inside v0.5.0, so an open entry with no
named destination is a question asked at the cut rather than answered before it.

**What changed.** The deferral now names Gate 2 - which freezes when v0.5.0
ships and ships inside v0.6.0, the same release carrying both blockers - and
states that v0.5.0 ships without it.

**The entry stays on Gate 1's frozen list, deliberately.** § "The gate is a
snapshot, not a moving target" governs what enters a frozen list and is silent
on what leaves, because nothing is meant to: the list is what was found on
2026-09-06. Removing an entry because it turned out to need a later release is
exactly the renegotiation the freeze prevents. So the list is untouched and only
the disposition moves.

**Why a `safety`-classed entry may be deferred at all.** The unconditional
safety exception would otherwise forbid it. The hazard - a learner attributing a
curve difference to a brand rather than to the parameter that produced it - is
not live: one profile under `src/anesthesia_sim/data/machines/`, no selection
surface, no trade name displayed. Planned-milestone item 40 keeps it that way by
design rather than by accident. The band is owed the moment a second profile or
a machine-naming surface exists.

**Why it matters.** Without this, the v0.5.0 cut meets an open Gate 1 entry with
no recorded destination and has to decide at cut time what to do with a
`safety`-classed item - which is the decision this records in advance, with the
evidence, rather than leaving to whoever runs the release.

**Done when.** `ROADMAP.md`'s Gate 1 section names Gate 2 as where `PL-WZVZ`
clears, says v0.5.0 ships without it, records that the entry stays on the frozen
list and why, and states the ground on which a `safety`-classed entry may be
deferred.

**Explicitly not this item.** Changing `PL-WZVZ`'s own front matter, removing it
from the frozen list, or doing any of its work.
