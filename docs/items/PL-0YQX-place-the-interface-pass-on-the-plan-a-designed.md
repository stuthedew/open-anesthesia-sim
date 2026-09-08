---
id: PL-0YQX
title: "Place the interface pass on the plan: a designed theme, type scale and layout have no roadmap item and no timeline row, and WORKING_NOTES shelved the thread pending the owner asking again"
priority: P2
effort: S
status: done
classes: planning, docs
touches: ROADMAP.md, docs/WORKING_NOTES.md
added: 2026-09-08
verify: python3 tools/doc_check.py check && grep -q 'Run the interface pass' ROADMAP.md
closed: 2026-09-08
---

**Problem.** A designed interface — palette, type scale, spacing rhythm,
density, layout — appears nowhere on the plan. `ROADMAP.md`'s "The timeline"
holds no row for it, and the three fragments in "Planned milestones" that look
adjacent are each something else: item 20 is one unscoped line about
accessibility, item 24 is a preferences panel whose "theme" means *a theme the
user picks* rather than *a designed theme*, and item 32 is the repository's
human-facing documents. The words *polish*, *styling*, *typography*, *dark
mode* and *look and feel* do not occur in the file.

It is not merely absent. `docs/WORKING_NOTES.md` § "Shelved: UI structure/form
mockups" records the thread as explicitly shelved on the project owner's call,
closing with "Do not resume this without the project owner asking again." The
project owner asked on 2026-09-08, which is that condition met.

**Why it matters.** Nothing surfaces the gap. No check reports it, nothing is
blocked on it, and the one document that records the decision is a notes file
whose own discovery instruction is circular (`PL-7QKY`). So the question
arrives fresh in each session that thinks to ask, and is answered from scratch
each time — which is what happened here.

It also decides work that is about to start. v0.5.0 adds bookmark lists, MAC
targets, a two-run overlay and per-run readouts. Every control built before the
display constants are consolidated spreads them further, which is the argument
`ROADMAP.md` § "Development pathway" Phase 2 already makes for ordering that
consolidation first. Leaving the pass unplaced leaves that ordering unstated
where a session implementing v0.5.0 would read it.

**Where.**

- `ROADMAP.md` § "Planned milestones" — the new item.
- `ROADMAP.md` § "The timeline" — the row that gives it a position. It is a
  patch-track row (`—` in the `#` column) rather than a numbered milestone:
  the version number is chosen for the capability boundary it crosses
  (§ "Versioning decision"), and a learner can do nothing after a restyle they
  could not do before. A numbered row would also freeze a gate of its own,
  which § "Why the gates are on this list and not behind it" makes the
  consequence of adding one.
- `docs/WORKING_NOTES.md` § "Shelved: UI structure/form mockups" — the
  resumption condition is met and the note should say so, and say where the
  thread went.

**Decision recorded (project owner, 2026-09-08).** Place the pass between
v0.5.0 and v0.6.0. Two alternatives were put and declined: after v0.6.0, on the
grounds that the schematic would teach the visual system what it needs; and
after v0.7.0, on the grounds that nitrous oxide changes what the readouts must
show. The owner also chose to fold the structural half — the display-constant
consolidation (`PL-2CS8`), an explicit `ft.Theme` (`PL-NGF7`'s decision) and
the component seam (`PL-B9PY`) — in ahead of v0.5.0's implementation rather
than deferring it to the pass. No design round was authorised.

**Done when.** `ROADMAP.md` carries the item and a timeline row placing it, and
`docs/WORKING_NOTES.md`'s shelving note records that the resumption condition
was met and where the thread now lives.
