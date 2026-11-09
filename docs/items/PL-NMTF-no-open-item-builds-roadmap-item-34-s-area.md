---
id: PL-NMTF
title: No open item builds ROADMAP item 34's area system at all - PL-3J2P and PL-C842 decided the representation and the container, PL-FTP5 recorded the provenance, and every other interface-areas item is a prerequisite waiting on a build item that does not exist
priority: P2
effort: S
status: done
classes: planning
feature: interface-areas
milestone: v0.4.26
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "Planned milestones" carried these paragraphs under item 34, "Blender's window management as the model for the interface". In them, "this item" means item 34, "here" means that entry, "this file" means `ROADMAP.md`, and "above" and "below" point within `ROADMAP.md` as it then stood. Item 34 keeps both decisions, their dated count and the rule the 2026-09-17 round produced. In the first quote, the per-window shape is settled by item 34's paragraph "What a second top-level window owes that set is settled too", not by the paragraph after it here. In the third, "the paragraph below" is item 34's "*No new display surface is built before this item*".

> *Tiled first, with break-out into a separate window* (project owner, 2026-09-15). **Scoped across two releases on 2026-09-16**. § "Completed: v0.6.0 - the layout is the reader's" (ratified 2026-09-16) builds the tiled no-overlap invariant, the View contract, the registry, workspaces, persistence and the unconditional region. Break-out occupied the release after it, "the second screen", until it came off the timeline on 2026-09-26 (see below). The split costs nothing structural. Break-out would otherwise force a rewrite of two things, and v0.6.0 builds both of them. First, the serialized layout root carries a set of windows from version 1. Second, the unconditional region is built in the per-window shape that the next paragraph settles. Together, the two halves build the no-overlap invariant above plus break-out. Break-out lets an area be taken into **its own top-level window**, which is itself a full window with its own areas. The Blender Manual's "Areas" page documents this as *View > Duplicate Area into New Window*, or Shift-LMB on an area's splitter widget. The manual describes the result as a fully functional window that belongs to the same running instance and is useful across multiple monitors. Every window is then tiled, so nothing inside a window covers anything else in it.

> *Given a version, and split, on 2026-09-16* (project owner, ratified on `PL-NMTF`, over the two alternatives put with it: inserting item 34 ahead of v0.5.0, which renumbers a scoped milestone, and shipping it undivided with break-out inside). Item 34 goes **after v0.5.0** rather than before it, on three grounds. First, a workspace that pins which run it shows has no content until more than one run exists. And v0.5.0 is what introduces the second run. Today `run_label` names a run `None` whenever it is shown alone. Second, inserting item 34 earlier would renumber a milestone already scoped with a frozen gate. Placing it after renumbers only rows that § "Planned milestones" already calls provisional. Third, no known failure is live yet. `PL-NWTM` and `PL-9LNF` are both `safety`-classed, and both are *pre-loaded* rather than live. The failures they name need a working handle, and the port's handles are inert. Item 34 then splits across two releases under the project's own "keep each milestone narrow" rule. Undivided, it was roughly twice the size of the largest milestone this project has run. The cut is taken at break-out, because that is the one place where the split costs nothing structural. As a consequence, the schematic (item 27) moves to v0.8.0, and multi-substance (items 6 and 7) moves to v0.9.0.

> *Reopened and re-affirmed, 2026-09-17* (project owner, ratified, chosen over moving item 34 ahead of v0.5.0, which is the alternative that was put). The placement above was reopened on an argument that the `PL-NMTF` round had not weighed. The argument is that the build order decides whether a new display is a widget registered against a contract, or an edit to whatever layout exists at the time. If so, every interface question settled before the area model is settled against a layout that is going away. The argument is sound, and the record has an instance of it. `PL-J4NW` found `docs/ARCHITECTURE.md` routing every new display panel to `run_view.py` or `simulation_view.py` "by asking whose it is". That routing is the fixed two-level layout that this item refuses. And `.claude/rules/ui-areas.md` is a standing substitute for the area system until the system exists. But the argument does not apply to the work actually left in front of this item, and the count shows why. **v0.5.0's Required scope is 13 of 20 `done`, and the monolithic half is the part that landed**. `PL-8PSW` and `PL-1XPX` are both closed. `PL-8PSW` is the two-branch overlay, which this file calls the largest new visual surface in the project. `PL-1XPX` is what the readouts show while two branches are displayed. The fork (`PL-TFX5`) and the resumption (`PL-J2TD`) are closed too. What remains is the bookmarks chain and three small items, **4 M and 3 S**, against this item's own 4 L / 16 M / 3 S. So the re-order would park an MVP a seventh the size behind this milestone, to protect a surface that has already shipped. It would also strand `PL-7Z84`, because the bookmarks and fork work is what gives a workspace a run identity to pin to. The order is kept. The argument does change the paragraph below. Until now, that paragraph's rule was only implied by the row order of § "The timeline". It is now written as a rule, because a session does not treat row order as a rule.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Waiting on planned-milestone item 34's area system, which v0.6.0 then scoped". "Nine concern" counts the second of the three groups that the paragraph quoted in `PL-BNYF`'s brief introduces.

> **Nine concern the area model, and the gate cannot come before the thing they are about.** That is the reason on which `PL-TH35` and `PL-VN6M` are already deferred, two paragraphs up. `PL-NMTF` (no open item builds `ROADMAP.md` item 34's area system) heads the group. The rest are `blocked-by` it, or are waiting on the same scoping round.

> **That scoping round happened on 2026-09-16, and it turns the deferral into a placement.** `PL-NMTF` closed by scoping item 34 as § "Completed: v0.6.0 - the layout is the reader's", plus a v0.7.0 row for break-out. So eight of the nine are now named in v0.6.0's `Required scope`. Under § "Debt inside the milestone's own scope", they are debt inside that milestone's scope, cleared *by* that milestone rather than before it. The ninth, `PL-J4NW`, closed in the same session. The entries below are left as the freeze wrote them, per § "The gate is a snapshot, not a moving target". This paragraph is their disposition.

> **Eight more were filed by that scoping round itself. They are disposed of here rather than added to the list.** Five are in v0.6.0's `Required scope`, and that milestone clears them under § "Debt inside the milestone's own scope". They are `PL-K285` (an Area that cannot be given the size its View needs says so rather than collapsing it), `PL-904Y` (the whole-interface visibility predicate, which stops meaning "can the reader see it" once an Area can be closed), `PL-G5SX` (the headless tests that drive every layout operation against the required set), `PL-50PZ` (the View chooser and the registry flag that make the accounting tier reachable) and `PL-JSY5` (two `docs/MODEL.md` statements that assume one window's width and one permanent surface). `PL-Y04W` (build break-out) belongs to v0.7.0 by the same rule, one release further out. The last two belong to neither milestone. `PL-KKRP` (re-examine the debt gate's own freeze trigger) is a decision about the cadence, not debt against a milestone. `PL-NDKC` (PySide6 segfaults on `QDataStream` over a temporary `QByteArray`) is a toolkit defect found while measuring. It was filed so that the persistence work finds it already written down. Every one of the eight is `anticipated`. Since 2026-09-16, that status is governed by a rule rather than by a reason this subsection gives for itself (`PL-83LS`). § "What counts" makes an `anticipated` finding **not debt until the hazard it describes exists**. Today the splitter handles can only resize an Area. So none of these hazards exists until the milestone that creates them is built. A gate that clears debt *before* a milestone cannot clear a hazard that the milestone introduces. So these eight are not deferred here. They are not debt against this gate at all. The placement named for each above is the whole of its disposition: v0.6.0's `Required scope`, v0.7.0's, or neither.

> Four of the nine are in the `safety` class. It is worth saying what that used to mean here, and no longer does. The four are `PL-7Z84` (a run has no identity a workspace can pin to), `PL-9LNF` (three `app/` surfaces own state a layout could duplicate or relocate), `PL-NWTM` (the unconditional displayed set has no structural home in the code) and `PL-W54S` (what a broken-out top-level window owes that set). The presence rule put them back on this gate regardless of when they were found. This subsection then had to argue them back off, one hazard at a time. `PL-83LS` turned that argument into the rule above. Each of the four is classed `anticipated`, so none of them is debt against this gate. Since `PL-W9P6` (2026-10-18) the handles are live. But they only resize an Area (`src/anesthesia_sim/app/area_layout.py`'s `AreaLayout`). No reader can close, replace or cover a required value until item 34's docking operations are built.

> Each of the four is named in v0.6.0's `Required scope`. That is where the rule puts a hazard, not where a deferral would leave it. The milestone that creates a hazard is the one that carries its guard. `tools/doc_check.py`'s `check_gate_reentries` now skips all ten `anticipated` findings. It decides this from the class and from the `blocked` status that dates each one, not from this prose. So these paragraphs record the reasoning, not the mechanism that enforces it. All ten are blocked on item 34 today. Each one returns to the gate when it is promoted, which happens when the hazard it names has been built.

> `PL-9PD6` (`docs/interface-provenance.md` contradicts itself about what `README.md` records), `PL-D584` (`PL-TH35`'s `blocked-by` names an item that has since closed, so the store advises every run that the View contract is ready to promote) and `PL-J4NW` (`docs/ARCHITECTURE.md` routes every new display panel by a fixed two-level layout) can be started today. They are deferred instead for the ordinary snapshot reason. They are `defect`s found after the freeze, neither `safety` nor `science`, and their problems do not predate the freeze. `PL-L8RN` (nothing enforces the one-adapter `QSplitter` confinement) is deferred because the boundary it would declare has no code to cover until the adapter exists.
