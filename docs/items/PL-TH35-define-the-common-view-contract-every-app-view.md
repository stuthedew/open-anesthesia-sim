---
id: PL-TH35
title: Define the common View contract every app/ view implements so any view is interchangeable in any area
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
as the model, where an Area holds one View and *any* view can occupy *any*
area. Nothing yet says what a View is, in this codebase, as a contract a view
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
`docs/ARCHITECTURE.md` § "Where new code belongs" is where a view becomes a
named pattern a session can route to.

**Done when.** A contract is written down, two existing views implement it, and
`docs/ARCHITECTURE.md` routes "a new view" the way it already routes a
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

---

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. Two are
learner-visible and the owner's: what a split does with the source View's
state, and whether any View is barred from a closeable Area.

**Q1. What the contract is, and where.** **Recommendation:** a
`typing.Protocol` on the Qt side (proposed `app/view_contract.py`), small,
and pruned by two tests: every registered kind's instance satisfies it, and
every member has at least one call site in the adapter (`PL-W9P6`). A member
nothing calls is deleted. This is the "design against the practised floor and
state the enforced one" the 2026-09-16 read asked for: the Protocol *is* the
enforced contract, and the practised one is whatever the two validating Views
need beyond it, which the tests then promote or refuse.

**Q2. Construction.** The registry factory (`PL-R1WQ`) is called as
`factory(context)`, where `ViewContext` carries exactly three things: the
**run binding** (the identity `PL-7Z84` defines, resolved by the adapter to
a narrow per-run frame source such as `drawn_window(start, stop, columns)`,
never the `BranchedCase`); the **shared-state handles** (time base,
compartment selection) as read-only values plus a change-request signal; and
`saved_state`, `None` on first creation and the Mapping the layout layer kept
otherwise. Eclipse's `IViewPart.init(site, memento)` has the same shape, the
memento null on first creation
(`bundles/org.eclipse.ui.workbench/eclipseui/org/eclipse/ui/IViewPart.java`,
eclipse-platform/eclipse.platform.ui, read 2026-09-27), and Blender separates
`create` from `blend_read_data` the same way. A View receives no parent, no
splitter and no reference to the Area it sits in.

**Q3. Data flow.** `refresh(run_state)` is pushed each tick by the adapter; a
chart pulls its own frame at its own width from the frame source and
re-requests on its own resize, which is `PL-9LNF`'s shape and needs its
`build_*` fix first. Both existing charts already take `draw(frame)`, so the
validation is a rename plus the context object, not a rewrite.

**Q4. Saved state.** `save_state() -> Mapping` returning drawing settings
only, with a `state_version` the View owns; the layout layer stores it
opaquely under Area id and kind (`PL-WV9K`) and never reads inside it. Saved
state the View cannot read: **start from defaults and say so in the
rectangle** until the reader changes a setting, at which point the next save
replaces it. Silent defaults are the stale-state failure the display standard
names.

**Q5. Minimum size.** A constant on the registry entry, not a method, per
`PL-K285`.

**Q6. Empty state.** Text stating what is absent, in the rectangle, never a
blank; the existing empty-state constants are the pattern and `PL-7Z84`'s
"run not present" state is the same mechanism.

**Q7. Controls.** A control over the View's own instance state may live in
the View. A control over shared state renders the handed value and emits a
request; it never owns the value (`PL-VN6M`, `PL-9LNF`).

**Q8. Constructible any number of times against one run.** Required; it is
what a split into three charts means.

**Q9. Is any View barred from a closeable Area?** **Recommendation
(learner-visible): no.** The unconditional values are region content and
never a View (`PL-NWTM`); the accounting tier is guaranteed by reachability
(`PL-50PZ`), not by pinning an Area. So no View needs a lock, and a lock would
be a hidden mode.

**Q10. What a split does with the source View's state.** **Recommendation
(learner-visible): the new Area gets a copy of the source's `save_state()`**,
so splitting a chart yields two identical charts the reader then diverges,
which is the owner's own three-chart example and Blender's
`SpaceType.duplicate`. `swap` moves instances with their state; `set_view`
displacement keeps one saved state per kind per Area and restores it when the
kind returns. *Alternative:* the new Area starts from defaults; refused
because the reader then rebuilds the settings they just had.

**Q11. Who draws the header.** **Recommendation: the container**, not the
View. The Area header carries the registry title, the run's name where the
View is bound (`PL-7Z84`'s display obligation), the chooser and the Area
operations - all container concerns - so a View never draws a title bar. This
is a recorded divergence from Blender, where the editor declares its header
region, and the reason is that here the header carries the run-name
obligation, which no View should be able to omit.

**Validation set.** `ConcentrationChart` and `WashInChart` implement it; the
readout row and the control-change record stay region content; the accounting
panel becomes a View. `docs/ARCHITECTURE.md` then routes "a new View" as: a
class satisfying the Protocol, one registry entry with a literal tag, an entry
in the shipped Workspace where it belongs, and the two pruning tests.

## Answers 2026-09-27

**Every recommendation above: ratified** (project owner, 2026-09-27,
ratified, over the alternative each names). The one decision the owner
specified otherwise is `PL-WV9K` Q4: layouts are saved by an explicit "Save
as default" action in the layout menu, not automatically; `PL-WV9K`
§ "Answers 2026-09-27" carries that design. Q4's "next save" is that explicit save.

**For the contract's names, from `PL-KZR1` (2026-10-04).** `RunView`'s eight
`build_*` methods each hand back a widget the run laid out once, the same
one on every call, so placing it again moves it. In Qt's idiom a `build_`
or `create_` name reads as a factory whose caller gets a new object to own.
The contract should name what a view hands an area for what it is; `PL-KZR1`
kept the prefix only so it is not renamed twice.
