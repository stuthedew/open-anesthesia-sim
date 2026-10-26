---
paths:
  - "/subprojects/docket/**"
  - "/tools/**"
---

# Dead ends in the item store and the tools

These approaches were tried here, measured and refuted. Each line names the
item or the code that holds the full reasoning, and `bin/docket show <id>`
prints an item. They moved here from `docs/dead-ends.md` on 2026-10-26
(`PL-5J1S`). A session proposes them only while it works on the item store or
the tools, so they load when it opens a file there, rather than on every turn
of every session.

Edit this file one entry at a time, as `docs/dead-ends.md` says. An entry that
leaves this file goes back to that list, or into its retired section with the
reason its question no longer exists, because `tools/dead_ends.py check
--base` counts this file as the place the entries went.

## Store and queue design

- **An index, database or manifest committed beside the items** — rejected: anything an index holds is recomputable, and an index is one more thing two branches conflict over. `subprojects/docket/src/docket/store.py`
- **One shared queue document** — rejected: it serializes every writer, which is the property one-file-per-item exists to buy. `subprojects/docket/src/docket/model.py`
- **The items on a branch of their own, as a worktree** — refuted 2026-10-17: it ends only item-only pull requests, which merge unattended, and parts an item's closure from its work and its provenance from the 767 ids the simulator cites; beads built one and deleted it. `PL-3YNG`
- **Partitioning closed items out of the live store** — refuted 2026-09-13: parsing is 76 ms of an 830 ms command whose cost is git, and an 86.1% cross-referenced store stays flat. `PL-KM3X`; a separate reading surface was refused 2026-10-03. `PL-4V6B`
- **Open-backlog ratio as a health measure** — refuted 2026-09-13: the comparison set is multi-contributor projects where an open issue is a promise to a stranger. `PL-03XH`

## Provenance and merge detection

- **Commit-containment (`git branch --merged`) for in-flight and stranded detection** — rejected: a squash merge contains none of the branch's commits, so every squash-merged branch reads as unmerged forever.

## Classification and concurrency

- **`classes`-derived lanes instead of `touches`-derived** — refuted 2026-09-04: put 33 of 145 open items on the wrong side, 18 of them workflow defects that would have gone to a simulator session.
- **Treating a shared file as a concurrency refusal** — refuted 2026-09-06: excluded 27 of Gate 1's 112 open entries, all declaring `docs/MODEL.md`, from every batch. `PL-VRMK`
