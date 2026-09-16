---
id: PL-TH35
title: Define the common Editor contract every app/ view implements so any view is interchangeable in any area
priority: P2
effort: M
status: blocked
blocked-by: PL-1FT6
classes: refactor, ux
feature: interface-areas
touches: src/anesthesia_sim/app, docs/ARCHITECTURE.md
added: 2026-09-16
not-delegable: the deliverable is a contract to be agreed before it is coded, and no command can prove a protocol is the right one; the test arrives with the first two views written to it
---

**Problem.** `ROADMAP.md` planned-milestone item 34 takes Blender's area system
as the model, where an Area holds one Editor and *any* editor can occupy *any*
area. Nothing yet says what an editor is, in this codebase, as a contract a view
implements - so "modular" currently means the dashboard surfaces are separate
widgets, which is movability rather than interchangeability.

**Why it matters (project owner, 2026-09-16).** "Should be modular system where
each widget (graph, etc) has core common features that make them interchangeable
in any blender-style area section." Interchangeability is the property that makes
a layout the reader's to arrange: without a shared contract, an area system can
only put each view back where it already was, and the workspace presets item 34
is for - an induction workspace with the graph zoomed in, a big-picture
workspace for maintenance - are arrangements of interchangeable parts.

**What it has to settle**, drawn from what the existing surfaces already do
differently rather than from a blank page: how a view is titled in its area's
header; how it is given what it draws (`ChartFrame` is the pattern and the
readouts are not on it yet); how it reports the size it wants and behaves when
given less; what it does with a state it cannot draw ("nothing recorded yet",
a halted run); whether it carries its own controls or is given them; and which
views may *not* go in a closeable area at all, per `docs/MODEL.md` § "Minimum
displayed outputs".

**Why it is blocked rather than ready.** The roadmap already answers the
ordering question and answers it against writing this first: "a view's contract
is whatever the area system requires of its contents, so views built first are
built against today's fixed layout and rewritten". So the contract is written
*with* the area system, validated against two views that already exist, not
ahead of it. `PL-8VL1` is the port item that reserves for it.

**Meanwhile**, `.claude/rules/ui-areas.md` § "Interchangeable, not merely
movable" carries the interim rule it leaves behind: a capability added to one
view gets a name and a shape the next view could take, even while only one view
uses it.

**Where.** `src/anesthesia_sim/app/` (the views themselves);
`docs/ARCHITECTURE.md` § "Where new code belongs" is where an editor becomes a
named pattern a session can route to.

**Done when.** A contract is written down, two existing views implement it, and
`docs/ARCHITECTURE.md` routes "a new editor" the way it already routes a
compartment or a chart series.


---

## What the 2026-09-16 Blender read contributes to this contract

`docs/interface-provenance.md` § "What an editor must implement" is the
evidence. Three things it settles that this item would otherwise re-derive:

- **Three different answers to "what is required", and they must be kept
  apart.** Blender's *enforced* contract is three fields; its *practised* one is
  seven callbacks plus a region type per region; and the simplest real editor in
  its tree implements exactly the practised floor. Design against the practised
  one and state the enforced one.
- **A vtable-as-data contract accumulates dead members, and nothing surfaces
  it.** Blender ships two hooks with live call sites and zero implementations,
  and a field that is read and never assigned by any editor. Plan the pruning
  into the contract rather than discovering it later.
- **The editor declares its own header region**; the container does not supply
  a title bar. A view's chrome is the view's business.

One divergence this contract owes, which Blender does not supply: its editors
can reach the screen and every other area through the context they are handed,
and 10 of 21 do. Interchangeability with teeth means a view is *given* what it
draws and has no route to the container - a deliberate narrowing, not an
inheritance.

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`, answered here rather than by new items.** The
2026-09-16 audit's gap sweep raised five contracts the area model implies that
nothing had filed. Four of them are clauses this item's "What it has to settle"
list is missing rather than items of their own, and they are added here on the
audit's own store check, which found them unfiled and then found this item to be
where they belong. They are written as questions because this item is a contract
to be agreed, not a change to be made.

1. **What a view's saved state *is*, and who writes it.**
   `docs/interface-provenance.md` § "Adopted" takes Blender's delegation - "Each
   view serializes itself; the layout layer does not know what is in a pane" -
   and this item's list names serialization nowhere. The contract owes: what a
   view hands the layout layer, in what form, and what the layout layer promises
   never to inspect.
2. **What a view owes when it is handed state it cannot read.** `PL-C842`'s
   loud-failure rule stops at the *view kind*: a workspace naming a view this
   build lacks must say so. It says nothing about a view this build *does* have
   being handed state from an older or newer schema. `CLAUDE.md` prefers an
   obvious failure to a plausible-looking wrong result, and a chart silently
   falling back to a default time base is exactly the plausible-looking case.
3. **What split, swap and a pane-stack round trip each do to a view's state.**
   `PL-C842` adopted all three operations and `docs/interface-provenance.md`
   adopts "a stack of previously-open editors per area", so a view leaves and
   returns. Which of its state survives that, and which is rebuilt, is a
   contract question rather than an implementation detail - it decides whether
   a reader who swaps a pane away and back has lost their place.
4. **What the container does when a pane cannot honour the size a view needs.**
   `docs/interface-provenance.md` § "An editor cannot refuse a size, and there is
   no minimum-size contract at all" records that Blender has no such contract and
   collapses the region instead, and § "Diverged" refuses that answer here
   because a required value must never be hidden to make room. So this project
   needs the contract Blender does not have: whether a declared minimum is a
   request or a constraint, and what a split or a border drag does when it cannot
   be met.

A fifth candidate - what a view's header must name - was checked and is already
inside this item's existing first bullet ("how a view is titled in its area's
header"), so nothing is added for it.

**One thing the audit settles rather than asks**: keep the contract small and
re-check it against its implementers. `docs/interface-provenance.md` § "Prune
the contract" records that Blender's `SpaceType` carries two callbacks with live
call sites and zero implementations and a field no editor assigns, and that
nothing in its design surfaces either.
