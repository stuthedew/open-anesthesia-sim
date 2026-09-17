---
id: PL-D1RT
title: docs/WORKING_NOTES.md's UI-structure thread and PL-037Y still describe the port as following v0.5.0, which the 2026-09-14 reorder makes stale
priority: P2
effort: S
status: done
classes: docs, defect
feature: planning-cadence
touches: docs/WORKING_NOTES.md, ROADMAP.md
added: 2026-09-14
closed: 2026-09-16
pr: 645
verify: python3 tools/doc_check.py check && grep -qF '`v0.7.x` sitting after item 34' docs/WORKING_NOTES.md && grep -qF 'item 33 returns to the interface-pass row it held' ROADMAP.md
---

**Problem.** docs/WORKING_NOTES.md's UI-structure thread and PL-037Y still describe the port as following v0.5.0, which the 2026-09-14 reorder makes stale

**Found while landing `PL-RKWB`** (the 2026-09-14 decision moving the Qt port
ahead of v0.5.0's display half).

`ROADMAP.md`, the queue and `docs/WORKING_NOTES.md:684` were all re-pointed with
that change. What was not swept is the narrative around planned-milestone item
34, the tiled workspace: `ROADMAP.md` § "Planned milestones" records the timing
question as live against a port that follows v0.5.0, and `PL-037Y` carries a
related UI-structure thread written under the old order. Neither is wrong about
its *substance* - the port still rewrites every layout, and item 34 still waits
on it - but both reason from a sequence that has changed, and § "Planned
milestones" is where a reader goes to find out what is coming.

`tools/doc_check.py` cannot catch this: the citations all resolve, and what is
stale is the reasoning around them rather than any path or section name. That
is the line `CLAUDE.md` draws between the decidable half and the judgment half,
working as intended.

**Done when** item 34's timing paragraph and `PL-037Y` read correctly against a
port that precedes v0.5.0.

**Verified 2026-09-14, and the finding is wider than the title.** The row both
documents cite **no longer exists**. "The timeline" at 'The timeline' now runs v0.2.8, v0.3.0, v0.4.0, `v0.4.x`, Gate 1, **v0.4.26**, v0.5.0, MVP
complete, Gate 2, v0.6.0, Gate 3, v0.7.0, Beyond - there is no `v0.5.x - the
interface pass` row, because `ROADMAP.md` records that the port **absorbs**
planned-milestone item 33. Two places still point at the deleted row:

- `ROADMAP.md:4155`, item 33's own placement note: "the `v0.5.x - the interface
  pass` row of 'The timeline'. A patch track rather than a numbered milestone".
- `docs/WORKING_NOTES.md:666`, the "Shelved, then resumed: UI
  structure/form mockups" thread: item 33 has "the `v0.5.x - the interface
  pass` row of 'The timeline' giving it a position between v0.5.0 and v0.6.0".

**Why it matters.** Both sentences place the interface pass *after* v0.5.0, and
the 2026-09-14 reorder put it *before* - inside v0.4.25, which is the next
substantial work. A session reading either one concludes the interface work is
somebody else's problem for two milestones, when it is the milestone about to
start. `bin/docket wave` cannot correct the impression: it reads sections and
`Required scope`, not the prose in a planned-milestone entry or a notes thread.

**The `PL-037Y` half is in flight elsewhere.** That item - the same thread
glossing `PL-NGF7` as "decides the theme object" - is carried on
`origin/claude/bold-mayer-ij89qm` as of 2026-09-14, so it is not answered here.
The two edits are in the same paragraph and whichever lands second should read
the other's change rather than re-deriving it.

**Done when.** Neither `ROADMAP.md` nor `docs/WORKING_NOTES.md` cites a
`v0.5.x - the interface pass` timeline row, item 33's placement note says it is
absorbed by the port milestone, and the notes thread says the interface pass now runs
*ahead* of v0.5.0 rather than between v0.5.0 and v0.6.0.

**Re-checked 2026-09-14 after `#576` merged**, which cut `v0.4.25` and
renumbered the port's section to `v0.4.26`. Both citations survive the
renumber unchanged, because what they name is a row that no longer exists at
any number.

---

**Done, 2026-09-16 - by `PL-PHKP` and `PL-L9RD` rather than by this item**, and
closed here on the first of the two dispositions `bin/docket check --verify`
offers: the work landed and the item was never closed. Each clause of the
`Done when.` above, measured rather than argued:

| Clause | State |
| --- | --- |
| Neither `ROADMAP.md` nor `docs/WORKING_NOTES.md` cites a `v0.5.x - the interface pass` timeline row | **Satisfied** - 0 matches in both, since `#634` |
| Item 33's placement note says it is **absorbed by the port** | **Superseded** - the absorption was reversed (project owner, on `PL-L9RD`), and `ROADMAP.md:308` records it |
| The notes thread says where the interface pass now runs | **Satisfied** - `docs/WORKING_NOTES.md:668` carries both orderings, dated |

The second clause is why this looked like a question and is not one. It asks the
roadmap to say something a decision of record has since made false, so meeting it
would mean undoing `PL-L9RD`. Applying a decision already on the record is
ordinary work; nothing here rests on what the project is *for*.

**The `PL-037Y` half is that item's, as this brief already said.** Its remaining
`v0.5.x - the interface pass` mention sits inside its own reasoning about where a
missing item would be worked, and its `Done when.` is about a gloss naming an item
that exists. Untouched.

**The `verify:` command was replaced, and the replacement is the point.** The old
one was `! grep -qF` for a phrase - an *absence*, satisfiable by anyone who
deletes the string, which is what `#634` did when it renumbered the row `v0.5.x`
to `v0.7.x`. It had discriminated correctly until then: the phrase was present
twice at `57fdb8c`, the last green run, and absent from `52205f6` onward. The
replacement pins the *presence* of two sentences the work created, and was run
against `57fdb8c` first, where both greps exit 1.

That difference is `PL-879R`'s to generalize - `docket check` advises on a
command's outcome but never its shape - and `PL-KND7` carries the measurement.
