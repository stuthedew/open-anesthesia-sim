---
id: PL-BNYF
title: Audit the open queue and ROADMAP against the area/workspace layout model, so items scoped before it was decided are re-briefed or dropped rather than built and undone
priority: P2
effort: M
status: ready
classes: planning
feature: interface-areas
touches: ROADMAP.md, docs/items/
added: 2026-09-16
verify: bin/docket check && test "$(grep -rlF 'Area-model audit (PL-BNYF)' docs/items | wc -l)" -ge 5
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
