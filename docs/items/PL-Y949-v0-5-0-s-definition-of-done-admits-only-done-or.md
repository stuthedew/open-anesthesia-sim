---
id: PL-Y949
title: v0.5.0's Definition of done admits only done or dropped for a frozen-list entry outside Required scope, so PL-S5Q9's recorded deferral of PL-WZVZ leaves the cut unable to satisfy the milestone's own bullet
status: untriaged
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
