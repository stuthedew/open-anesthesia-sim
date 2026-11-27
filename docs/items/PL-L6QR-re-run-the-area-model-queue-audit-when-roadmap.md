---
id: PL-L6QR
title: Re-run the area-model queue audit when ROADMAP item 36 is scoped, because every disposition PL-BNYF could not reach turned on which of today's surfaces become views - a question item 36 has not answered
priority: P3
effort: M
status: blocked
classes: planning
feature: interface-areas
touches: docs/items
blocked-by: 2027-02-27
added: 2026-09-16
---

**Problem.** Re-run the area-model queue audit when ROADMAP item 36 is scoped, because every disposition PL-BNYF could not reach turned on which of today's surfaces become views - a question item 36 has not answered

**Why it matters.** `PL-BNYF` audited 49 open and untriaged items against the
area/workspace model on 2026-09-16 and sorted **none** of them into
would-be-undone, done-twice, false-assumption or sequencing-win. That is a real
result rather than a null one, and the reason it came out that way is the thing
worth recording: every candidate finding rested on a step of the form *"item 34
makes this surface a separate View in an Area the reader can close"*, and no
such step is decided. `ROADMAP.md` item 34 defines Area, View and Workspace
and then defers the roster - "a **View** is what occupies an area - the thing
with the functionality. Item 36 is the catalogue of them" - with item 36
sequenced after item 34. `.claude/rules/ui-areas.md` says the same in terms:
"That contract is not designed yet and is not yours to invent mid-change."

So the exposure the project owner asked about on 2026-09-16 - "a bunch of
outdated items we do and then have to undo" - is real but **deferred**. It does
not fire now, because the decision that would falsify a brief's layout
assumption has not been taken. It fires when item 36 decides which of today's
surfaces - the legend, the readout row, the transport, the wash-in panel, the
control timeline - become views a workspace places rather than fixed parts of
one screen.

Ten findings were raised and all ten were refuted on that ground, two skeptics
apiece. `PL-MN4J` is the worked example: the auditor read the legend's
closeability out of `PL-VN6M`'s brief, which is an item's supposition about a
catalogue nobody has written, and the refutation traced `PL-MN4J`'s own case to
`docs/INTERFACE.md` § "The chart's hover readout", where the item already argues the
*opposite* - a hover box floats free of its surroundings, so the legend's
adjacency is worth nothing to it either way.

**Done when.** Item 36's scoping round has decided which surfaces become
views, and this audit has been re-run against the open queue with that roster
as the standard - so that the items whose briefs name a position survive or are
re-briefed on a decided premise rather than on a guess.

**Scope note.** This is not a standing obligation to re-audit on every change.
Its trigger is one event: item 36 being scoped. If item 36 is dropped or folded
into item 34, this item is dropped with it.

**What `blocked-by` names.** v0.8.0 from 2026-09-16 (#629), the first release
after item 34's two, which the schematic held. Since 2026-09-26, when break-out
came off the timeline (`PL-V1Y7`), that release is v0.7.0, and the field says
so. The trigger is unchanged: item 36 being scoped.

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** This item is the audit's own conclusion
rather than one of its findings.

**Re-pointed at v0.8.0, 2026-10-25.** v0.7.0 was scoped without item 36
(`PL-LF0P`): its § "Explicitly out of scope for v0.7.0" leaves the View
catalogue out, because the milestone adds two Views and decides nothing about
which of today's surfaces become Views. The trigger is unchanged, item 36 being
scoped, and v0.8.0 is the next release `ROADMAP.md` § "The timeline" names.

**This item's `blocked-by: v0.8.0` still applies, 2026-11-09 (`PL-5XG1`).** § "The timeline"'s v0.8.0 row no longer holds multi-substance, which came off the timeline. The row now names the next milestone with nothing chosen for it, and the trigger is still item 36 being scoped.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-YNFS`).** `ROADMAP.md`'s v0.7.0 section, § "Explicitly out of scope for v0.7.0", carried this sentence in its entry on the View catalogue, planned-milestone item 36, until then. This item's `blocked-by: v0.8.0` records the current fact.

> So `PL-L6QR`, which waits on item 36, now waits on v0.8.0 instead.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-B6V1`).** `ROADMAP.md`'s v0.6.0 section, § "Explicitly out of scope for v0.6.0", carried this sentence in its entry on the View catalogue, planned-milestone item 36. This item's `blocked-by: v0.8.0` holds the current fact.

> Queue item `PL-L6QR` is the queue audit that re-runs once item 36 is scoped.

**Checked 2026-11-22** against `d4e8200`: still applies, and still blocked. `ROADMAP.md` § "The timeline" row 11 still leaves v0.8.0 unscoped, and item 36 (the catalogue of Views) has no scoping round. Several of today's surfaces have become Views one at a time since this was filed. `src/anesthesia_sim/app/view_registry.py` now names eight View kinds, including bookmarks and branch, so the re-run audit will have fewer open questions than in 2026-09.

**Checked 2026-11-27:** v0.8.0 was scoped (`PL-8NDZ`) without planned-milestone item 36, so this audit still waits. The roadmap places no milestone after v0.8.0 yet, so its blocker is now a date three months out, at which to re-read it. The scoping of the milestone after v0.8.0 is the next point at which item 36 can be taken.
