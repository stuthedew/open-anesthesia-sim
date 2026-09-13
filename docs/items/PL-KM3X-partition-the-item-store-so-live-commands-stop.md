---
id: PL-KM3X
title: Partition closed item bodies out of the live store
status: untriaged
added: 2026-09-13
---

**Problem.** 576 of 814 item files (70.8%) are terminal and still sit in the live
`docs/items/` directory, which `store.read_items` globs and parses in full on
every `bin/docket` invocation (`subprojects/docket/src/docket/store.py:87-88`).

**The unit is the body, not the item.** Measured 2026-09-13: closed items'
front matter is 308.6 KB; closed items' bodies are 2,376.8 KB — 68% of the
entire store. Five commands genuinely need closed items, and every one of them
reads only front matter:

- `next` / `status` / `feature` — `plan.Feature` computes `progress` and
  `is_underway` from `status == "done"` (`plan.py:34-53`). Without closed items
  all 30 features report `0/N` and the finish-a-feature tie-break dies.
- `wave` — the frozen debt gate is fed `{id for item in items if not
  item.is_open}` (`cli.py:389`); without it the gate reads "0 cleared, 159 open".
- `release` — `release.unreleased` selects `done and not milestone`
  (`release.py:68-78`).
- `trend` — buckets by `item.closed` (`trend.py:218, 240`).
- `check` — resolves `blocked-by` edges against the whole store
  (`checks.py:903, 1025, 1362`).

Fields actually read on a closed item: `id`, `status`, `feature`, `milestone`,
`closed`, `pr`, `priority`, `effort`, `classes`. **Nothing reads a closed item's
body.** So a partition that moves closed bodies out while keeping a compact
index of closed front matter preserves all five dependencies exactly.

**Why it matters.** Not latency — that case does not hold and should not be
made. Measured: the full-store parse is 74 ms of a 0.68 s `docket next`, which
is dominated by 0.38 s across 62 git subprocess calls. Load scales cleanly
linearly at ~86 µs/item (814/1,628/3,256/6,512 files measured). The real
arguments are bounded growth in a directory that gained 116 items on its worst
day, and the context cost of a store an agent session may read directly.

**Prior art.** Every comparable live system partitions terminal work out of the
live set: Backlog.md ships `tasks/`, `completed/`, `archive/tasks/`, `drafts/`
and dogfoods 455 completed against 213 live; todo.txt auto-archives to
`done.txt` on completion by default; Taskwarrior 2.x split `pending.data` from
`completed.data`; OpenSpec's `archive <change>` is a mandatory dated step.
Backlog.md measurably collapsed at ~700 tasks (task view 4.42 s -> 0.85 s, no-op
edit 12.19 s -> 0.42 s) and fixed it by not scanning the whole corpus.

**Done when.** Closed bodies no longer load on an ordinary command; all five
dependent commands produce byte-identical output to today on the current store;
closed items remain readable on demand and in git history.

**Watch out.** 86.7% of items cite at least one other item (2,773 edges, mean
out-degree 3.41, max in-degree 49). This is a dense graph, not a pile — a
partition must keep closed items resolvable by id, not merely retained.
