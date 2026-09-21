---
id: PL-Y949
title: v0.5.0's Definition of done admits only done or dropped for a frozen-list entry outside Required scope, so PL-S5Q9's recorded deferral of PL-WZVZ leaves the cut unable to satisfy the milestone's own bullet
verify: python3 tools/doc_check.py check && grep -qF 'deferred to a later gate' ROADMAP.md
payoff: stops the v0.5.0 cut having to choose between dropping a safety-classed entry and holding the release, which is what a bullet admitting only done or dropped leaves a session meeting a deferred one
effort: S
priority: P2
status: ready
feature: wzvz-deferral-integrity
touches: ROADMAP.md
added: 2026-09-21
---

**Problem.** v0.5.0's Definition of done admits only done or dropped for a frozen-list entry outside Required scope, so PL-S5Q9's recorded deferral of PL-WZVZ leaves the cut unable to satisfy the milestone's own bullet

**Why it matters.** `ROADMAP.md:5139` states, as a condition of v0.5.0 being
complete, that "every item of the frozen list above outside this milestone's
Required scope is `done`, or `dropped` with its reason recorded". `PL-WZVZ` is
on Gate 1's frozen list, is outside v0.5.0's twenty Required scope ids, and
will be neither `done` nor `dropped` at the cut — it will be `blocked`,
deferred to Gate 2 by `PL-S5Q9` (project owner, 2026-09-20). So the same file
says both that v0.5.0 ships without the entry and that v0.5.0 is not complete
while the entry is open.

**This is the failure `PL-S5Q9` was filed to prevent, surviving one document
over.** Its own payoff line reads "stops the v0.5.0 cut meeting an open
safety-classed gate entry with no recorded destination and having to decide
what to do with it at release time". It recorded the destination in the Gate 1
section and its `Done when.` reached no further; `touches: ROADMAP.md` covered
the file but the edit covered one section of it. The question it removed from
the cut is therefore still asked at the cut, in a weaker form: not "where does
this entry go" but "does the Definition of done mean what it says".

**The project has already read the bullet as exhaustive, once, and paid for
it.** `PL-F0L8` records its own disposition as leaving "Gate 1 by the route its
own definition of done allows — '`dropped` with its reason recorded' — rather
than by deferral". That sentence is a session recognising that deferral is not
one of the bullet's two routes, and choosing `dropped` to stay inside them. A
session meeting `PL-WZVZ` at the cut with the same reading has two bad options:
drop a `safety`-classed entry whose hazard is real but not yet live, or hold the
release.

**What the fix is.** One rider on the bullet at `ROADMAP.md:5139`, naming the
third disposition and its condition — an entry deferred to a named later gate,
where the deferral is recorded in the gate section with its ground, per
§ "The gate is a snapshot, not a moving target", which already permits a
deferral "only where this section says so and says why". The rule exists; the
Definition of done simply does not cite it. Pitch the rider at the altitude
that survives: it is a statement about how a frozen list disposes of an entry,
not about `PL-WZVZ`, so it belongs in the same form on v0.2.8's bullet
(`ROADMAP.md:952`), v0.4.0's (`:1021`) and the cadence's (`:5855`) — or, if a
single sentence can carry all four, in whichever of them is the canonical
statement.

**Explicitly not this item.** Changing `PL-WZVZ`'s frontmatter, removing it from
the frozen list, or doing any of its work; `PL-S5Q9` already refused all three.

**Done when.** v0.5.0's Definition of done names the deferred-to-a-later-gate
disposition alongside `done` and `dropped`, with the condition under which it is
legitimate, so a session running the cut can satisfy the bullet against
`PL-WZVZ` by reading it rather than by interpreting it; and the same statement
is either made once where all four gate-clearing bullets can cite it, or
repeated in each.

## Ratified, 2026-09-21

**The rider lands before the v0.5.0 cut** (project owner, 2026-09-21, ratified,
over leaving the bullet to be interpreted at the cut by whoever runs it). The
case put was the one above: `PL-F0L8` shows the bullet has already been read as
exhaustive once, so a session meeting `PL-WZVZ` at the cut has to choose between
dropping a `safety`-classed entry whose hazard is real but not yet live and
holding the release.

**Where the rider goes, on the narrowest-rule test.** § "The cadence" beat 3
(`ROADMAP.md:5855`) is the canonical statement — "**Clear** it — every item
`done`, or `dropped` with its reason — before implementation of the milestone
begins" — and the three milestone bullets (`:952`, `:1021`, `:5139`) restate it.
So the rider belongs on the cadence, with the milestone bullets citing it rather
than each carrying its own copy.

**What would falsify it being a rule rather than an instance.** That no later
gate ever defers an entry. Gate 2 freezes when v0.5.0 ships and inherits
`PL-WZVZ` plus whatever v0.5.0's implementation turns up, so recurrence is
near-certain rather than speculative — it is a rule, and pitched at the cadence
it survives a milestone being renumbered.

**The rider's own condition, not a blanket third disposition.** Deferral is
legitimate only where § "The gate is a snapshot, not a moving target" already
requires: the deferral is recorded in the gate's section, with its ground, and
names the later gate it lands in. An entry deferred to nowhere still holds the
release — that is `PL-S5Q9`'s finding and the rider must not weaken it.

**The phrase `verify:` pins.** The rider must contain the literal string
`deferred to a later gate`, which appears nowhere in `ROADMAP.md` today. That is
the only wording constraint — everything around it is the implementing session's
to write.
