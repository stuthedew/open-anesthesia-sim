---
id: PL-FRGP
title: The slow-verify advisory says the named command sets the check's floor, but the pool is now throughput-bound: removing PL-GS5X measured 28.6 s to 23.7 s, not the ~24 s the sentence implies
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
added: 2026-09-03
closed: 2026-09-03
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -rq 'def test_the_advisory_bounds_what_narrowing_would_leave' subprojects/docket/tests
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

**Worked.** The advisory no longer claims the named command sets the floor. It
says what narrowing it cannot buy, computed from the serial total and the
pool's width rather than asserted:

```
PL-GS5X (29s) is the costliest `verify:` command this check runs: against a
0.7s median and 33s for the whole run. Narrowing it cannot take the run below
about 21s: the other 81 commands are 164s of work across 8 workers, so the
pool is bounded by the size of the queue as well as by its slowest member -
narrow the command if it can be narrowed, or accept the cost knowing what it is
```

**A lower bound, deliberately, and not a prediction.** A pool never packs
perfectly, so the real run lands above it - the bound for the store measured in
this item's brief is 18.5 s against a run that measured 23.7 s. Saying what
narrowing cannot buy is honest; saying what it will buy is the error the old
wording made, and making that prediction more precise would have repeated it
rather than fixed it.

**One arithmetic covers both regimes**, which is why nothing here has to detect
which one it is in. Where the queue is small the remainder divided across the
pool is near zero, the bound is near zero, and narrowing genuinely collapses the
run - the 2026-09-02 store, where the old sentence was true. Where the queue is
large the bound is most of the elapsed time and the reader learns that before
spending an afternoon on it.

**The bound removes every named command, not only the worst.** Narrowing one of
two heavy commands leaves the other where it was, so a bound computed against
the worst alone would not be a bound. That is also the reasoning the advisory
already gave for naming all of them, now made arithmetic rather than prose.

**`workers` was the missing input**, and `serial` - added under `PL-9NKK` on the
same branch - was the other. `LandedReport` carried the total but not the
divisor, so the run knew what the queue cost and not what it cost *per pass*.
Where either is absent the sentence stops early instead of dividing by a number
nobody measured: an older report, a caller that built one by hand, or a store
whose named commands are the whole of the run.

**Tests.** Five in `test_checks.py` over the bound, its two silent cases and the
multi-command reading, replacing `test_the_advisory_says_why_one_command_sets_
the_floor` - which asserted the misleading sentence and so had to go rather than
be adjusted. Two in `test_verify.py` over the recorded width. Checked against a
mutated implementation: computing the bound without removing the named commands
fails three.

**Not changed.** `SLOW_COMMAND_RATIO` and its floor. 30x against a 0.64 s median
still picks out exactly the command a reader would want named; the defect was in
what the sentence then told them it was worth, which is what this item said.
