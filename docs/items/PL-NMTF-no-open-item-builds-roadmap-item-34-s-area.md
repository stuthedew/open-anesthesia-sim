---
id: PL-NMTF
title: No open item builds ROADMAP item 34's area system at all - PL-3J2P and PL-C842 decided the representation and the container, PL-FTP5 recorded the provenance, and every other interface-areas item is a prerequisite waiting on a build item that does not exist
priority: P2
effort: S
status: done
classes: planning
feature: interface-areas
touches: ROADMAP.md, docs/MODEL.md, docs/ARCHITECTURE.md, docs/interface-provenance.md, docs/WORKING_NOTES.md, docs/items, .claude/skills/docket/SKILL.md
added: 2026-09-16
closed: 2026-09-16
pr: 629
verify: python3 tools/doc_check.py check && bin/docket check && grep -qF "## v0.6.0 - the layout is the reader's" ROADMAP.md
---

**Problem.** No open item builds ROADMAP item 34's area system at all - PL-3J2P and PL-C842 decided the representation and the container, PL-FTP5 recorded the provenance, and every other interface-areas item is a prerequisite waiting on a build item that does not exist

**Why it matters.** `bin/docket feature interface-areas` lists decisions
(`PL-3J2P` the splitter tree, `PL-C842` the LayoutModel), provenance (`PL-FTP5`,
`PL-P5QX`), a path-scoped rule (`PL-LH18`), a contract waiting on the system
(`PL-TH35`), and nine prerequisites this audit filed. Not one of them *builds*
the thing. The Qt port has already paid for the reservation - `inert_splitter()`
at `src/anesthesia_sim/app/qt_widgets.py:784` disables every handle so that a
later item can enable them - and the item that enables them does not exist.

That is why two other problems have no honest fix. `PL-TH35` cannot re-point its
`blocked-by` at anything real (`PL-D584`), and `ROADMAP.md` § "The timeline"
cannot place item 34 as a release without a scope to place. A design held in
four closed items and a reservation held in inert code is the state this project
is worst at keeping: nothing in the queue decays visibly, and the next session
to open `app/` reads a rule telling it to build for a system nobody has
scheduled.

**Done when.** Either an item exists that builds the area system with a scope of
its own, or `ROADMAP.md` records item 34 as a milestone to be scoped and the
queue points at that - so that "who builds this, and when" has an answer a
session can read.

**Not a scoping round.** Scoping item 34 is the project owner's, and
`ROADMAP.md`'s development rules say a milestone gets a goal, required scope,
definition of done and an out-of-scope list before implementation begins. This
item is the observation that neither the milestone nor the item exists, not a
request to write one now.

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Surfaced 2026-09-16 by the area-model audit's completeness critic, after the main sweep had closed - which is the critic earning its place rather than a defect in the sweep.

**Decision needed.** Who builds `ROADMAP.md` item 34's area system, and when.
Two dispositions, and the queue needs one of them: **scope item 34 as a
milestone now** - a design round producing its goal, required scope, definition
of done and out-of-scope list, per `ROADMAP.md`'s development rules, which then
yields the build items - or **record it as deferred** with the trigger that
would bring it forward, and point the queue at that record.

This is the project owner's. It decides what enters `ROADMAP.md` and in what
order against the Qt port and `v0.5.0`, which `CLAUDE.md` puts on their side of
the division of labour: "The division of labour is theirs to set direction and
yours to make it real."

Eleven open items are `blocked-by` this one. They are the design prerequisites
the area system needs and none of them can be answered against an unscoped
milestone, so the answer here releases the cluster and nothing else does.

---

## Answered 2026-09-16: item 34 is scoped, split, and placed

**The design round the project owner asked for.** Three questions were theirs
and all three were put with a recommendation and answered:

1. **Where it goes and what version it takes.** After v0.5.0 - the case you can
   branch, and **split across two releases**: v0.6.0 "the layout is the reader's"
   (the tiled half) and v0.7.0 "the second screen" (break-out). The schematic
   (item 27) moves to v0.8.0 and multi-substance (items 6 and 7) to v0.9.0.
   Grounds, in order of weight: a Workspace pinning which run it shows has no
   content until v0.5.0 introduces a second run; placing it earlier would
   renumber a milestone already scoped with a frozen gate; and nothing is
   live-broken, because the handles are inert. The split is on the project's own
   "keep each milestone narrow" rule - undivided the milestone was roughly twice
   the largest this project has run - and the cut is at break-out because that is
   the one place it costs nothing structural.
2. **Whether it freezes a debt gate.** No. Gate 2 stays where the timeline puts
   it - frozen when v0.5.0 ships - and becomes v0.6.0's gate. Recorded as the
   second exception after v0.4.26 in § "The debt gate" -> "The cadence", with the
   condition written down, and `PL-KKRP` filed to re-examine the trigger itself
   rather than amending it in passing.
3. **`PL-W54S`.** Answered with a tier split neither of its readings stated:
   every top-level window carries the invariant tier and the run it shows, and
   the per-substance tier lives once in a main window that cannot be closed while
   another is open. `docs/MODEL.md` carries it.

**The fourteen prerequisites the 2026-09-16 audit filed are disposed of.**
Eleven are v0.6.0 `Required scope`; `PL-J4NW` and `PL-D584` closed in the same
session; `PL-L6QR` follows item 36. None was dropped - the audit ran against a
design that was already decided, so its findings were prerequisites rather than
guesses, and re-reading all fourteen found none made moot. Twelve build items
were filed alongside them.

**One thing left open and recorded rather than decided**: whether the `v0.5.x`
interface pass (item 33) should run before or after item 34, now that v0.6.0 has
stopped meaning the schematic. Item 33's own entry carries both arguments and
`docs/WORKING_NOTES.md` carries the thread.
