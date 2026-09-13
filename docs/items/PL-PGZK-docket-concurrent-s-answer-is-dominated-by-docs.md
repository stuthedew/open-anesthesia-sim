---
id: PL-PGZK
title: docket concurrent's answer is dominated by docs/MODEL.md, which nearly every item touches, so it rules out almost everything and cannot discriminate between real and nominal contention
status: ready
added: 2026-09-03
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_concurrency.py
verify: uv run pytest subprojects/docket/tests/test_concurrency.py && grep -q 'def test_shares_a_file_groups_by_path' subprojects/docket/tests/test_concurrency.py
---

**Problem.** `docket concurrent <id>` reports contention from declared
`touches` overlap. `docs/MODEL.md` is declared by a large fraction of the
queue, so it dominates every answer: measured 2026-09-03, `bin/docket
concurrent PL-ZRSP` returned 22 items it "cannot run alongside", and 16 of
those shared `docs/MODEL.md` and nothing else. `PL-DR1Z` returned the same
shape. Two items that both append a paragraph to different sections of
`docs/MODEL.md` are reported identically to two items that both rewrite
`simulation_view.py`'s run loop.

**Why it matters.** The command's stated contract is to rule work out, never
to certify it (`.claude/skills/docket/SKILL.md`, "Mode: work several items at
once"), so a false *positive* is the one failure it has no defence against. At
this hit rate the answer stops discriminating: a session planning a batch
inside `v0.4.0` is told that nearly every pair collides, which is the same
information as being told nothing, and the cheap response is to stop running
it. That is `CLAUDE.md`'s retirement test — a check that fires every run
without changing a decision.

**Where.** `subprojects/docket/src/docket/` (whatever computes the overlap),
and the `touches:` convention itself.

**Decision needed.** Which of the three options below to build. Recommended:
rank the collisions by how many items declare the shared path, so a hub file
reads as weak evidence and a rarely-touched source file as strong. It needs no
change to the `touches:` format, so no existing item has to be rewritten, and
it degrades gracefully - a path nothing else declares still reads as a hard
collision. Reject it only if a ranked answer turns out to be one a session
skims past, in which case the excluded-hub-set option is the fallback, since it
is the only one that changes what is *reported* rather than how it is ordered.

**Options, not yet decided.** Rank the collisions by how many items declare
the shared path, so a hub file reads as weak evidence and a rarely-touched
source file as strong; or let `touches:` name a section rather than a file for
documentation paths; or exclude a configured set of hub paths from the answer
and say so in the output. The first needs no format change and is the cheapest
to try.

**Found.** 2026-09-03, planning the `v0.4.0` implementation order. Not fixed
in that session.

**Done when.** `bin/docket concurrent` distinguishes contention on a hub path
from contention on a file few items touch, so a session planning a batch inside
one milestone gets an answer it can act on rather than a near-universal refusal.
Measured on the same two probes that produced this finding - `PL-ZRSP` returned
22 rule-outs of which 16 shared only `docs/MODEL.md`, and `PL-DR1Z` the same
shape - the reported set discriminates between those two kinds. The command's
contract is unchanged and restated in the output: it rules work out, it never
certifies it, so whatever it now reports as weak evidence is still reported
rather than silently dropped.


## Worked 2026-09-13: the defect as filed is already closed, and what is left is a different and much weaker problem

**The filed defect no longer reproduces on either of its own probes.** This brief
measured `bin/docket concurrent PL-ZRSP` on 2026-09-03 and recorded 22 items it
"cannot run alongside", 16 of them sharing `docs/MODEL.md` and nothing else.
Re-run today, on both probes this brief names:

| probe | `Cannot run alongside` (2026-09-03) | `Cannot run alongside` (2026-09-13) |
| --- | --- | --- |
| `PL-ZRSP` | 22 | **nothing** |
| `PL-DR1Z` | same shape | **nothing** |

`PL-VRMK` (done) is what changed it: a shared file is now reported in a
`Shares a file - proceed, and land the smaller change first` tier, and the
refusal tier is reserved for a `blocked-by` edge. Every one of the 22 moved out
of the refusal. **A hub path can no longer produce a false refusal at all**,
which is the failure this item was filed for and the only one the command's
stated contract has no defence against.

**Name the number that would change your mind, then count it.** The recommended
option — rank collisions by how many items declare the shared path — was
proposed to stop hub paths reading as hard collisions. It is worth building only
if it prevents false refusals that still occur. That count is now **zero**. The
option is not worth building, and neither is the excluded-hub-set fallback,
which was named only as the answer if a ranked list turned out to be skimmed.

**The residual is real, and it is list length rather than a wrong verdict.**
`PL-ZRSP` now prints 54 entries under `Shares a file`, of which **25 (46%)
share only `docs/MODEL.md`**. Measured across the store the same day:

- 237 open items declare **136** distinct paths.
- The largest hub is `docs/MODEL.md` at **32 items (13.5%)**, then
  `simulation_view.py` at 25 (10.5%). This brief's "a large fraction of the
  queue" overstates it by roughly fourfold.
- **72 of the 136 paths (53%) are declared by exactly one open item**, so more
  than half of all declared paths can never collide with anything.

So the distribution is a short head and a long tail, and a 54-line list is
reporting that shape one item per line.

**Decided: group the `Shares a file` tier by path instead of by item.** It is
the cheapest thing that fixes what is actually left. One line reading
`docs/MODEL.md - 25 items: PL-043, PL-10MX, ...` collapses 46% of the answer
into a line a session can skip deliberately, and a path declared by one other
item keeps its own line and reads as the strong evidence it is. The ranking the
brief recommended is a property of this grouping rather than a separate feature:
ordering the groups by size puts the rarely-declared paths, which are the ones
that matter, at the top.

What it does **not** change: the command still reports every entry, so the
contract — it rules work out, it never certifies it — is unchanged, and nothing
is silently dropped. No `touches:` format change, so no existing item is
rewritten. The third option (a section-level `touches:` for documentation paths)
stays unbuilt and is now clearly not worth its cost: it would have to be
backfilled across 32 items to improve an advisory list nobody is refused by.

**Effort drops `M` to `S`** — this is a rendering change in `cli.py`'s
`concurrent` printer, not a change to how overlap is computed.

**`touches:` corrected.** The brief named `render.py`; the two tier headings are
printed from `subprojects/docket/src/docket/cli.py:693-699`. The test file is
added because the `verify:` command names it.
