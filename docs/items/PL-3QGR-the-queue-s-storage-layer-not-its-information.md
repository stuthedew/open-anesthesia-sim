---
id: PL-3QGR
title: The queue's storage layer, not its information model, is what blocks concurrent work
status: untriaged
touches: .claude/hooks/punch-list-digest.sh, .claude/skills/punch-list/SKILL.md, docs/PUNCH_LIST.md, tools/punch_list.py
added: 2026-08-24
---

`P2` · `L` · `session-cost`

**Problem.** `docs/PUNCH_LIST.md` is simultaneously the data store, the
human-readable view, and the coordination point. That conflation causes three
things the information model itself does not: every capture and every
close-out writes to the same regions of one file, so any two concurrent
sessions contend; ids are allocated by reading the file, so two branches
allocate the same one (observed 2026-08-24, PL-042 twice); and there is no
in-progress state, so nothing stops two sessions starting the same item.
**Why it matters.** It makes deliberate concurrent work impossible to reason
about, which is the capability the project owner has asked for. The entry
format, the cold-start brief, the mechanical validation, the disposal
ledger, and the model routing are all sound and should survive any change
here — the defect is where the data lives, not what it says.
**Where.** `docs/PUNCH_LIST.md`, `tools/punch_list.py`,
`.claude/skills/punch-list/SKILL.md`, `.claude/hooks/punch-list-digest.sh`.
**First step.** This is `L`. Per CLAUDE.md it is promoted into a scoped
`ROADMAP.md` milestone before implementation, not started from a note. Scope
it around three separable changes, in increasing cost: derive in-flight state
from remote git branches (no format change, prevents double-starting); one
file per item with `docs/PUNCH_LIST.md` generated rather than edited (removes
the conflict class); a structured `touches:` field feeding a conflict graph
and a `concurrent` command.
**Done when.** Scoped as a milestone with the storage decision made, or
archived with the reason it was not worth doing.
**Context.** 22 of 23 open entries already name concrete files in
`**Where.**`, and `app/simulation_view.py` appears in 9 of them, so the
conflict graph is computable from data already present — and a naive "work
these two in parallel" guess would be wrong often enough to matter.
