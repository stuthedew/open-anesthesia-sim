---
id: PL-74T0
title: Record or refuse generator heads for the three clusters 2026-10-03's captures fall into - PL-KGYT's fact past its sweep, a frozen gate's entries past PL-WD5Z, and the supported step guarded entry point by entry point - once pull requests 1306, 1308 and 1309 merge
priority: P1
effort: M
status: ready
classes: housekeeping
touches: docs/items
added: 2026-10-03
payoff: the day's three candidate root causes are each ranked as a generator or refused with a reason, so their next members are stopped at the source rather than fixed one at a time
not-delegable: The deliverable is a judgment - whether each cluster's members misread one fact no head states - and a grep for the recorded fields would pass on a head recorded wrongly
---

**Problem.** Record or refuse generator heads for the three clusters 2026-10-03's captures fall into - PL-KGYT's fact past its sweep, a frozen gate's entries past PL-WD5Z, and the supported step guarded entry point by entry point - once pull requests 1306, 1308 and 1309 merge

**Found 2026-10-03**, answering the project owner's question whether the day's
new items come from known failure modes. All 13 captures untriaged that day
were filed in a squash commit closing another item, and seven more sit on open
pull requests 1306 to 1309. Read against `bin/docket generators --misread`,
three clusters share a fact. Most members of the second and third are not on
`main` yet, so they cannot be recorded here today.

1. **`PL-PVW2`'s and `PL-KGYT`'s fact: which spelling of a repeated predicate
   is the answer.** `PL-P72R` (docket's `shell.OPERATORS` and
   `.claude/hooks/shell_split.py`'s `OPERATORS`, held to each other by nothing)
   and `PL-Z8RS` (`_without_code` and `_marks_code` read code spans per line
   where `doc_check._code_spans` reads them per document) were filed after
   KGYT closed on 2026-10-01. KGYT's `generator:` says its sweep searched every
   export of `model`, `vcs` and `release`; `shell.py` and `doc_check`'s own
   readers sit outside those three. With `PL-Q9LK` after PVW2, the fact has
   re-entered after each of its two fixes. Two post-close instances of KGYT at
   the first triage pass, one short of the three the triage rule reads as a fix
   that did not hold; `PL-HNXS` made three at the second (below).
   `PL-F66M` (twelve hand-built store prefixes) reads `PL-NGBM`'s fact instead,
   and is a post-close instance of that head.
2. **A frozen gate's entries: which items it holds, each one's lane, and what
   clears it.** `PL-QWF8` and `PL-Z64T` on `main`, `PL-JV5Q` on 1309, `PL-D388`
   and `PL-W9BK` on 1308. `PL-J6HP` and `PL-WD5Z` closed 2026-09-23 on "A debt
   item's gate disposition"; WD5Z moved the disposition onto debt items, and
   J6HP's `generator:` records that "the record itself stayed prose". QWF8 and
   JV5Q are non-debt entries that `bin/docket gate`, reading open debt, never
   sees; Z64T is `ROADMAP.md`'s lane grouping restating what `Item.lane`
   computes. Three or more post-close instances once 1308 and 1309 merge.
3. **The supported step, guarded entry point by entry point.** `PL-YZ17`
   (closing on 1306), `PL-5F76`, and on 1306's branch `PL-BPRK`
   (`evaluate_anchored`, `steps_per_tick`), `PL-WP52` (each compartment's own
   `advance`) and `PL-6QYJ` (sample spacing with no floor), after `PL-73ZN`,
   `PL-BMY5` and `PL-8H2R` closed the same day. `src/anesthesia_sim/core/supported_ranges.py` holds
   the ranges, but every function taking a bare float has to remember its
   guard, and each one that does not becomes a capture. No head states this
   fact. Its candidate fix is a decision, not a repair: a validated step type
   built once and taken by every entry point, so the type checker finds the one
   that skips it.

**Why it matters.** An unrecorded generator ranks nowhere: until a head
carries `root-cause-of:`, `generator:` and `misread:`, nothing in the store
says these clusters exist, their members are triaged one at a time, and each
local fix leaves the mechanism to hand the store its next member. Cluster 2
alone has five members filed since its fact's heads closed on 2026-09-23.

**State at triage, 2026-10-03.** Pull requests 1308 (`bafb6438`) and 1309
(`8d916ddf`) have merged, so clusters 1 and 2 can be read on `main`; 1306,
which carries cluster 3's other members, merged as `7a6ec289` during this
pass, so all three can be read there now. The triage pass recorded each
member's own `**Generator check.**` and left the heads to this item: cluster 1
is `PL-P72R` and `PL-Z8RS`, with `PL-F66M` an instance of `PL-NGBM` instead;
cluster 2's members on `main` are `PL-QWF8`, `PL-JV5Q` and `PL-Z64T`, the last
blocked on this item; `PL-5F76` now keeps only its count half, the step half
being `PL-YZ17`'s.

**Second triage pass, 2026-10-03.** `PL-HNXS` joins cluster 1: which files
the repository holds is spelt as git's list in `workflow_paths_check.tracked_files`
and as a walk with its own skip list in `ruff_configs`, `fixture_id_check._walk`
(`PL-QJ5F`) and `doc_check._walk` (`PL-2P5L`), the last two classed one-offs at
capture. `PL-JCS3` (line-at-a-time readers, untriaged) claims `PL-Z8RS` for a
fact of its own, so cluster 1's count depends on it; judge the two together.
Cluster 3: `PL-0GJC`, the validated step type, is in flight, and `PL-WP52` is
blocked on its open question about compartments.

**`PL-JCS3`'s judgment, 2026-10-04.** `PL-Z8RS` has two causes and stays in
cluster 1: the per-line reading is a second spelling of where a code span is,
beside `doc_check._code_spans` (KGYT's fact), and that spelling is wrong because
a span continues across lines (`PL-R417`'s, recorded that day). `PL-Q9LK` is the
same shape against `PL-PVW2`. So cluster 1 counts `PL-P72R`, `PL-Z8RS` and
`PL-HNXS` as before.

**Done when.** Each cluster is recorded as a head - `root-cause-of:`,
`generator:` and `misread:` - or refused with its reason in this brief, after
1306, 1308 and 1309 have merged.

**Generator check.** Work the project owner asked for: this item is the recording step for three candidate heads, answering their 2026-10-03 question whether that day's captures come from known failure modes, and it is a member of no cluster.
