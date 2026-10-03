---
id: PL-74T0
title: Record or refuse generator heads for the three clusters 2026-10-03's captures fall into - PL-KGYT's fact past its sweep, a frozen gate's entries past PL-WD5Z, and the supported step guarded entry point by entry point - once pull requests 1306, 1308 and 1309 merge
status: untriaged
added: 2026-10-03
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
   re-entered after each of its two fixes. Two post-close instances of KGYT:
   one short of the three the triage rule reads as a fix that did not hold.
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

**Done when.** Each cluster is recorded as a head - `root-cause-of:`,
`generator:` and `misread:` - or refused with its reason in this brief, after
1306, 1308 and 1309 have merged.
