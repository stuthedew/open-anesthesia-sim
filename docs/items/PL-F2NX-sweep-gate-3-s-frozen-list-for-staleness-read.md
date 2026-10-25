---
id: PL-F2NX
title: Sweep Gate 3's frozen list for staleness: read each of v0.7.0's frozen entries against the tree, drop what no longer reproduces with its reason, and correct briefs that overstate what is left
priority: P2
effort: M
status: done
classes: housekeeping
feature: gate-staleness-sweep
touches: docs/items, ROADMAP.md
added: 2026-10-25
closed: 2026-10-25
pr: 1794
payoff: Gate 3 is worked on evidence: entries that no longer reproduce stop being ranked and offered, and briefs say what is actually left.
verify: grep -qE "^Swept on 20[0-9-]+" docs/items/PL-F2NX-*.md
---

**Problem.** Gate 3 froze on 2026-10-25, the day `PL-LF0P` scoped v0.7.0, and
nobody has read its entries against the tree yet. Beat 3 of `ROADMAP.md`
§ "The cadence" asks for that pass before any entry is worked. A `verify:`
command tests for the fix and never for the fault, so an entry whose problem
was solved another way fails forever and reads as outstanding work.

**Why it matters.** The two measured passes found 32% of one list dead or
overtaken (`PL-6ZQY`) and about 6.5% of Gate 2's (`PL-C4W8`). Without the
pass, sessions spend work on entries that no longer reproduce, and
`bin/docket next` keeps ranking them.

**Done when.** Each open entry of `ROADMAP.md` § "v0.7.0 - the schematic"
→ "Debt gate: the frozen list" has been read against the tree. Each one that
no longer reproduces is `dropped` with its reason. Each brief that overstates
what is left carries a dated `**Checked 2026-MM-DD:**` paragraph saying what
is left, as the docket skill's sweep rule asks.

Swept on 2026-10-25, against `cc31bef7` (the v0.6.5 cut) merged with `ff1a8d93`. Every one of the 24 entries `bin/docket wave` listed as open was read against the tree: the 13 this gate clears, the 9 v0.7.0 clears itself, and the 2 deferred to Gate 4. The session read 12 of them itself. Two subagents read the other 12, and the session checked each claim it acted on against the tree before writing it down.

**No entry's problem had gone, so nothing was dropped.** Five defects were run again on this tree, through the code paths their briefs name, and each failed as filed: `PL-QG52` (a circuit restore after a volume change loses agent), `PL-CQ1M` (the circuit's long washout reports 0), `PL-HSP8` (the halt and mark branches disagree about a change made on the halt), `PL-YH6Z` (the wash-in hover prints 1.00 at an elimination column) and `PL-88MK` (the dashed pen's square cap). The other 19 were read against the code, the data files and `docs/MODEL.md`.

**Six records were corrected.** Three briefs asked for more than is left. `PL-0S0V` (precision per unit) requires a one-sided bound on a precision no reader can set in v0.7.0. `PL-VJZK` (what a reader's price carries) is down to its `docs/MODEL.md` text, because v0.7.0's Required scope states the rest and ships no price. `PL-KZ99` (molar mass and liquid density) planned a schema bump from 2, where the files are already at 3, and a derivation `docs/MODEL.md` already carries. `PL-WZVZ` (attributing a difference between machines) waited on less than its record said, because two of its four blockers are done. Two entries waited on more than their `blocked-by` said. `PL-B4P7` (the teaching-default flow) now also waits on `PL-TBMK`, the second machine profile, and moves to `P3` with it. `PL-B396` (the agent cost View) now also waits on `PL-93B3`, the preferences file that keeps its unit.

**Eight briefs had stale citations repaired in place.** Line numbers in `PL-QG52`, `PL-YH6Z`, `PL-HSP8`, `PL-FPLQ`, `PL-WJJ8` and `PL-B396` are replaced by the symbol or section they pointed at. `PL-5B1N` and `PL-WZVZ` no longer call done items open.

**Measured against the two earlier passes.** None of 24 was dead and 3 overstated (about 12%), against 32% of one lane (`PL-6ZQY`) and about 6.5% of Gate 2 (`PL-C4W8`). The list was read on the day it froze, and 16 of the 24 were filed in the seven days before. Every overstated brief, and the one whose blockers had narrowed, was filed in September, and each had outlived a decision taken since: the v0.7.0 scoping, a schema bump, or two items closing. This is one gate's count, so it describes this gate and not the trend.

**Found and not fixed here.** The comment above `FLOW_DISPLAY_DECIMALS` in `src/anesthesia_sim/app/formatting.py` still describes Flet and an unquantized flow. `PL-0S0V`'s work corrects it, and its verdict says so, so no item was filed.
