---
id: PL-BNYF
title: Audit the open queue and ROADMAP against the area/workspace layout model, so items scoped before it was decided are re-briefed or dropped rather than built and undone
priority: P2
effort: M
status: done
classes: planning
feature: interface-areas
touches: ROADMAP.md, docs/items/
added: 2026-09-16
closed: 2026-09-16
verify: bin/docket check && grep -qF '**item 34** is what turns them live' ROADMAP.md && test "$(grep -rlF 'Area-model audit (PL-BNYF)' docs/items | wc -l)" -ge 5
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
merely movable. `PL-TH35` (define the common Editor contract) is filed beside
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
*"item 34 makes this surface a separate Editor in an Area the reader can
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
Editor contract rather than as items, which is where the store check put them.

**`ROADMAP.md` said two incompatible things about who turns the Qt port's inert
splitter handles live**, and all three ordering lenses found it independently.
`:1540` and `:4545` said item 33, the visual pass; `:1615`, `:1633` and `:4770`
said item 34, the area system. The un-absorption of item 33 on 2026-09-16
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

**Left for the project owner**: item 34 has no row on "The timeline" at all.
That is a defect of record, but which row it takes is a scheduling call rather
than a session's, so it is raised rather than written in.

**Docs swept**: `ROADMAP.md` (edited), `docs/MODEL.md` § "Minimum displayed
outputs" (read; its second-window half is what `PL-W54S` now carries),
`docs/interface-provenance.md`, `docs/ARCHITECTURE.md` § "Where new code
belongs", `.claude/rules/ui-areas.md`. `make doc-check` passes.
