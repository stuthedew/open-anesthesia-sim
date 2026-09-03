---
id: PL-FRGP
title: The slow-verify advisory says the named command sets the check's floor, but the pool is now throughput-bound: removing PL-GS5X measured 28.6 s to 23.7 s, not the ~24 s the sentence implies
status: untriaged
feature: dev-tooling
added: 2026-09-03
---

**Problem.** `docket check`'s slow-command advisory reads:

> `PL-GS5X` (24s) is what this check waits for: that command against a 0.7s median
> and 28s for the whole run. A pool cannot finish before its slowest member, so this
> sets the floor for every `make check` until the item closes - narrow the command if
> it can be narrowed, or accept the cost knowing what it is

The sentence is true about pools in general and misleading about this one. Measured
2026-09-03, four cores, eight workers, the same candidate set:

| | pool wall clock |
| --- | --- |
| all 78 candidates | **28.6 s** |
| all 78 except `PL-GS5X` | **23.7 s** |

Acting on the advisory in full - deleting the command it names outright, which is
more than it asks for - returns **4.9 s of 28.6 s**. A reader doing the arithmetic
the sentence invites ("28 s run, 24 s command") would expect something near 24 s.

**Why it matters.** This is CLAUDE.md's "gives a wrong answer silently" test: the
check passes, prints an actionable-looking instruction, and the action returns a
sixth of what the wording implies. The cost is not the 4.9 s - it is that the one
session placed to judge a heavy `verify:` command, which is the entire reason
`PL-VG7G` built this advisory, is handed a wrong estimate of what narrowing it buys.

**Why the model changed.** `PL-VG7G` was written when the pool was floor-bound: 49
candidates summing to ~34 s across eight workers is ~4 s of aggregate work against a
6.9 s slowest member, so the slowest member genuinely was the floor and everything
else hid behind it. The store has since grown to 78 candidates summing to 175.5 s,
which is ~22 s of aggregate work - now comparable to the 27.4 s slowest member rather
than a quarter of it. The pool is at the crossover between the two regimes, so
neither "the slowest command sets the floor" nor "the total sets it" is true alone,
and the advisory only knows the first.

**Where.** `subprojects/docket/src/docket/checks.py` - `_check_landed`, which composes
the sentence; `subprojects/docket/src/docket/verify.py` - `already_passing`, which
already measures both the pool's elapsed and every command's duration, so the
information needed to say the true thing is in hand and discarded.

**Done when.** The advisory's claim about what narrowing the named command would
save is one a reader can act on without re-measuring - or, if the honest answer is
that it can no longer be predicted from what the run knows, the advisory says what
the command cost and stops short of promising a saving.

**Note on scope.** `SLOW_COMMAND_RATIO`'s own justification is not in question here;
30x against a 0.64 s median still picks out exactly the command a reader would want
named. The defect is in what the sentence then tells them it is worth.
