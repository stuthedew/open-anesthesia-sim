---
id: PL-YHWG
title: ROADMAP's timeline places item 34's area system after v0.5.0 on a decision ratified 2026-09-16, and the project owner has reopened it: the modularity argument - that every UI decision taken before the area model is taken against a layout that is going away, and every new display is an edit to a monolith rather than one more widget - was not weighed in that round
status: untriaged
feature: interface-areas
touches: ROADMAP.md, docs/WORKING_NOTES.md, docs/items
added: 2026-09-16
---

**Problem.** ROADMAP's timeline places item 34's area system after v0.5.0 on a decision ratified 2026-09-16, and the project owner has reopened it: the modularity argument - that every UI decision taken before the area model is taken against a layout that is going away, and every new display is an edit to a monolith rather than one more widget - was not weighed in that round

**Why it matters.** `PL-NMTF` scoped item 34 on 2026-09-16 and placed it after
v0.5.0, ratified, "chosen over inserting item 34 ahead of v0.5.0". Its three
grounds, in its own order of weight, were: a Workspace pinning which run it
shows has no content until v0.5.0 introduces a second run; placing it earlier
renumbers a milestone already scoped with a frozen gate; and nothing is
live-broken because the Qt port's splitter handles are inert. None of the three
is the argument the project owner raised on 2026-09-16 - that the *order* is
what decides whether a new display is a widget registered against a contract or
an edit to whatever layout exists at the time.

That argument already has one instance in the record, caught the same day and
by a different route. `PL-J4NW` found `docs/ARCHITECTURE.md`'s "Where new code
belongs" routing every new display panel to `run_view.py` or
`simulation_view.py` by asking whose it is - "a fixed two-level layout the area
model refuses" - and `.claude/rules/where-new-code-goes.md` loading it on every
`src/` read. A second is standing: `.claude/rules/ui-areas.md` (`PL-LH18`) tells
every `app/` session to build as if the area system existed, which is a proxy
for it existing, and `PL-ZBBP` retires the proxy when the system ships.

**What the counting says, and it cuts against a straight re-order.** Measured
2026-09-16 against the store:

- **v0.5.0's Required scope is 13 of 20 `done`, and the monolithic half is the
  part that landed.** `PL-8PSW` (two branches overlaid on one time axis - the
  roadmap's own "largest new visual surface in the project") and `PL-1XPX`
  (what the readouts show while two branches are displayed) are both closed, as
  are the fork (`PL-TFX5`), the resumption (`PL-J2TD`) and the whole score
  architecture. What is left is the bookmarks chain - `PL-LPLD` -> `PL-CTD7` ->
  `PL-B8MK` -> `PL-Z3W6` - plus `PL-49R8` (the path-scoped rule against a new
  sample store), `PL-MN4J` (the hover naming which run) and `PL-W7H9` (what a
  branch comparison asserts, in `docs/MODEL.md`). **4 M and 3 S.**
- **v0.6.0 is 27 open items, 4 L / 16 M / 3 S.**
- **Gate 1 is clear** (167 of 170, the 3 remaining blocked outside it) and
  **v0.4.26's Required scope is 28 of 28 closed**, so nothing else stands
  between here and either order.

So the choice is not between two comparable blocks. It is between finishing a
4 M / 3 S tail and parking it behind a 23-item milestone - and the tail contains
no monolithic UI work for the modularity argument to bite on, because the
surface it would have been built against has already shipped.

**Where the argument does bite is everything after the MVP, and the timeline
already puts item 34 first there.** The schematic (planned item 27, v0.8.0),
multi-substance and its readouts (items 6 and 7, v0.9.0), the interface pass
(item 33, v0.7.x) and the open gas-volume display question are all behind
v0.6.0 today. What the timeline does *not* carry is the principle as a
**rule**: the ordering is implied by row order, so a session proposing a new
display surface before v0.6.0 has nothing to read that defers it, and the next
row move re-opens the question by accident.

**Done when.** Both of:

1. `ROADMAP.md`'s timeline records the order the project owner chooses, with
   the grounds, and - if it moves - `PL-NMTF`'s ratified placement is recorded
   as reopened rather than silently overwritten.
2. Item 34's entry carries the standing rule in its own sentence: that no new
   display surface is built before the area model, with the condition that
   would end it named, so it survives a row move. `.claude/rules/expert-review.md`
   § "Say what would falsify it" applies - the rule's condition is "until item
   34's Editor contract and view registry ship", which is an instance and not a
   permanent refusal.

**Not a scoping round, and not a session's decision.** Which order the timeline
takes is the project owner's, per `CLAUDE.md`'s division of labour. This item is
the record that the question is open again and the measurement that bears on it.
