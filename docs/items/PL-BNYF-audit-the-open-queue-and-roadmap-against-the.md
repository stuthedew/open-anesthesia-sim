---
id: PL-BNYF
title: Audit the open queue and ROADMAP against the area/workspace layout model, so items scoped before it was decided are re-briefed or dropped rather than built and undone
priority: P2
effort: M
status: done
classes: planning
feature: interface-areas
milestone: v0.4.26
touches: ROADMAP.md, docs/items/
added: 2026-09-16
closed: 2026-09-16
pr: 625
verify: bin/docket check && grep -qF '**item 34** is what turns them live' ROADMAP.md && test "$(grep -rlF 'Area-model audit (PL-BNYF)' docs/items | wc -l)" -ge 5
sweep: audits the open queue and ROADMAP.md against the area and workspace layout model, and files each stale brief and missing prerequisite it finds
---

**Problem.** Audit the open queue and ROADMAP against the area/workspace layout model, so items scoped before it was decided are re-briefed or dropped rather than built and undone

**Why it matters** (project owner, 2026-09-16): "given this is a major design
decision with far reaching effects ... make sure this gets scoped, and current
items, goals, etc. work towards this goal, rather than have a bunch of outdated
items we do and then have to undo."

The top-level version of this worry is already answered and should not be
re-raised: `ROADMAP.md` item 34 records that the Qt port reserves for the area
system and builds none of it, on the same double-work argument the milestone
makes for absorbing item 33. `PL-LH18` (closed in PR #618, unmerged as of this
writing) adds the enforcement — a path-scoped rule for
`src/anesthesia_sim/app/**` recording that every main UI element is built to
become an area-type widget and that views must be *interchangeable* rather than
merely movable. `PL-TH35` (define the common View contract) is filed beside
it.

What is not answered is the per-item question: of the open items declaring
`app/` in `touches`, which were briefed before any of that was recorded, and
what does each one assume?

**The five dispositions to sort them into.** An item is only a finding if it
lands in one of these; "related to the UI" is not a finding.

1. **Would be undone** — its deliverable the area work deletes or rewrites.
2. **Would be done twice** — applies a decision to today's surface that must be
   re-applied to the area surface. This is the argument already made for item
   33 and for item 34's reservation; it generalises.
3. **Carries a false assumption** — not wrong yet, but its brief assumes a fixed
   position, a fixed neighbour, or a container that will not exist. Re-brief,
   do not drop.
4. **Is a missing prerequisite** — the gap direction. The area model implies
   contracts nobody has filed: each view owning its own serialization, each
   view declaring what it needs, deferred layout mutation. `PL-TH35` is one;
   find the rest.
5. **Becomes cheaper or unnecessary if sequenced after the layout** — an
   ordering win rather than a defect.

**Precedence, on conflict** (project owner, 2026-09-16): where this session's
Blender findings (`PL-FTP5`) and the area-widget rule landing in PR #618
disagree, **this session's findings win**; the other may add to them but not
overrule them. Recorded because the two were written independently within the
hour and the rule's branch is the one that merges first.

**Not in scope.** Deciding `PL-3J2P` (shared-vertex graph vs nested-`QSplitter`
tree). The audit records which items each answer would affect; it does not pick.

**Done when.** Every open item declaring `app/` in `touches` is sorted into one
of the five dispositions or explicitly cleared, the re-briefs are written, the
missing prerequisites are filed, and `ROADMAP.md`'s ordering reflects the
sequencing wins found.

**Population widened to the untriaged captures too** (project owner,
2026-09-16, mid-session: "include untriaged items in sweep"). The `touches`
filter alone would have missed them by construction: capture writes no
`touches`, so 13 of the 14 items at `status: untriaged` declare none at all and
no path filter can reach them. They are swept on their text instead, against the
same five dispositions. That makes the population **49** — 36 open items
declaring `app/` in `touches`, plus the 13 untriaged captures other than this
item itself.

## Area-model audit (PL-BNYF)

**Done 2026-09-16.** 49 items swept - the 36 open items declaring `app/` in
`touches`, and 13 of the 14 untriaged captures, which the `touches` filter
cannot reach because capture writes no `touches` at all.

**No item landed in disposition 1, 2, 3 or 5, and that is the finding rather
than an absence of one.** Fourteen candidates were raised and all fourteen were
refuted, two skeptics apiece, on one shared ground: each rested on a step of the
form
*"item 34 makes this surface a separate View in an Area the reader can
close"*, and no such step is decided. Item 34 defers the roster to item 36,
which is sequenced after it and has not been written, and
`.claude/rules/ui-areas.md` says so in terms. So the exposure this item was
filed against is real but **deferred**: it fires when item 36 is scoped, not
now. `PL-L6QR` carries the re-run, with that single trigger.

The second refutation ground, which caught the rest, is that the "finding" was
the item's own stated premise read back. `PL-RTG9` is the clean example: it was
called a sequencing win because the README attribution is owed only once the
area system ships - which is the item's own **title**. An audit that returns an
item's declared dependency as a discovery has found nothing.

**Nine missing prerequisites were filed** after a store check that deduplicated
two candidates against `PL-41YP` and rejected one as extrapolation: `PL-W54S`
(what a broken-out window owes the unconditional set), `PL-7Z84` (a run has no
identity to pin a workspace to), `PL-L8RN` (nothing enforces the one-adapter
`QSplitter` confinement), `PL-SSQW` (the saved-workspace file), `PL-WV9K`
(Workspace as an object above the layout tree), `PL-HJPY` (no multi-window
representation), `PL-NWTM` (the unconditional region has no structural home),
`PL-9LNF` (three more state-ownership sites beside `PL-VN6M`'s) and `PL-L6QR`
(the re-run above). Four further contracts went into `PL-TH35` as clauses of the
View contract rather than as items, which is where the store check put them.

**`ROADMAP.md` said two incompatible things about who turns the Qt port's inert
splitter handles live**, and all three ordering lenses found it independently.
`:1540`, `:4545` and `:1633` said item 33, the visual pass; `:1615` and `:4770`
said item 34, the area system. The third site was missed on the first pass and
found by this audit's own completeness critic, which is the check earning its
place: the first two were the ones a grep for "turns them live" returns, and
`:1633` says "*reserving* for item 33" instead. The un-absorption of item 33 on 2026-09-16
introduced it: that note pulled the visual pass out of the port and attached the
reservation's next step to it. Corrected in both places, and item 33's lever
list - "palette, type scale, spacing rhythm, density and layout" - no longer
claims `layout`, because the arrangement is the reader's under item 34 and so is
not a thing a design pass decides once.

**Checked at the source and reported clear**: the port's reservation *was* built
as described - `inert_splitter()` at `src/anesthesia_sim/app/qt_widgets.py:784`
disables every handle and refuses collapse, and `QSplitter` is imported by that
module and no other under `src/`. The largest available false finding, that the
port built the area system and it will be undone, does not hold.

**Five more filed after the completeness critic ran**, which is the critic
earning its place: `PL-NMTF` (no open item builds item 34's area system at all -
the decisions, the provenance and nine prerequisites exist and the build does
not), `PL-J4NW` (`docs/ARCHITECTURE.md` § "Where new code belongs" routes every
new panel by which container holds it, loaded on every `src/` read alongside
`.claude/rules/ui-areas.md`, which asks the opposite), `PL-R1WQ` (the view
registry and the kind tag), `PL-9PD6` (`docs/interface-provenance.md`
contradicts itself about the README attribution, which is what `PL-RTG9` was
refuted against) and `PL-D584` (`PL-TH35`'s `blocked-by` names an item that
closed on 2026-09-12, so the store advises promoting the View contract on
every run).

`PL-NMTF` is the one to read first, and it is why two other things here have no
clean fix: `PL-TH35` has nothing real to point its `blocked-by` at, and the
timeline cannot place item 34 as a release without a scope to place.

**Left for the project owner**: item 34 has no row on "The timeline" at all.
That is a defect of record, but which row it takes is a scheduling call rather
than a session's, so it is raised rather than written in.

**Docs swept**: `ROADMAP.md` (edited), `docs/MODEL.md` § "Minimum displayed
outputs" (read; its second-window half is what `PL-W54S` now carries),
`docs/interface-provenance.md`, `docs/ARCHITECTURE.md` § "Where new code
belongs", `.claude/rules/ui-areas.md`. `make doc-check` passes.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "Planned milestones" carried this paragraph under item 33, "The interface pass". In it, "this item" means item 33, "that list" is item 33's opening list of what the pass decides, and "here" means that entry. Item 33 keeps the paragraph under the label "*Arrangement belongs to item 34*"; the label's record that the list once named "layout" is kept here.

> *Arrangement is not on that list, and the word that used to be was "layout"* (corrected 2026-09-16, `PL-BNYF`). Item 34's entire content is which areas exist, where they sit, and what a reader may do to them. This item decides how the contents of those areas look. The two were separable on 2026-09-08, when this item was written against one fixed screen. They are not separable any more. Under item 34 the arrangement belongs to the *reader*, so it is not something a design pass can decide once.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-V8SJ`).** `ROADMAP.md`'s § "Completed: v0.4.26 - the interface moves to Qt" carried this note and, inside Required-scope item 2, the parenthetical that follows it. "The un-absorption note above" is the note that returned planned-milestone item 33 to the interface-pass row, "`Required scope` item 2 below" is the dashboard entry, and "this same scope item" is that entry.

> **Item 34 rather than item 33, corrected 2026-09-16 (`PL-BNYF`).** The un-absorption note above was written to pull the visual pass back out of this port. In passing, it attached the reservation's next step to item 33. But `Required scope` item 2 below and item 34's own entry both give that step to item 34. Item 33 decides how the interface *looks*. Item 34's whole content is what a reader may do to its *arrangement*: split, join, swap, break out, and save as a workspace. A session scoping the interface pass from the uncorrected sentence would have believed it owned building split and join.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-V8SJ`).** The parenthetical, from Required-scope item 2:

> (This said "item 33" until 2026-09-16, `PL-BNYF`. It was the fourth and last place where the un-absorption note's wording had attached the layout reservation to the visual pass. The error sat two lines after the sentence in which this same scope item gives the reservation to item 34.)

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Eighteen more came from the 2026-09-16 triage pass, in three groups.** All eighteen were captured on 2026-09-16, ten days after this gate was frozen, so "The gate is a snapshot" already places them in the next gate. Most were filed by `PL-BNYF`'s area-model queue audit. They are written down with their reasons rather than only listed, for two reasons. Each group is here for a reason of its own. And without this record, a reader who found them open would have to work out why.

> **Eight are apparatus findings, deferred for the reason this subsection already states.** They are `PL-1T6T` (re-test the refusal of compaction), `PL-2XM2` (reorder the docket skill so its four acted-on modes survive post-compaction truncation), `PL-6YL1` (a check for the verify-target class), `PL-B11M` (detect a silent model fallback), `PL-C6XD` (one renderer for the `RESERVED` release verdict), `PL-JTHW` (a cancelled `main` run reported rather than passed over), `PL-R0Q0` (the safety-class gate advisory that fires forever), and `PL-Y1L0` (`outstanding_roadmap_edits` naming the milestone section a cut has passed). Each one lies entirely in the workflow lane, and none can affect a reader of the simulator. So the refilling-queue arithmetic above applies to them unchanged.
