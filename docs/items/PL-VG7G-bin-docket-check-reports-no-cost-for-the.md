---
id: PL-VG7G
title: bin/docket check reports no cost for the commands it ran, so a slow one arrives invisibly
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py
added: 2026-09-02
closed: 2026-09-02
pr: 198
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -rq 'def test_a_command_that_dominates_the_run_is_named' subprojects/docket/tests
---

**Problem.** `already_passing` runs every open item's `verify:` command and
reports what each *returned*. It never reports what any of them *cost*, though
it necessarily knows: the pool's wall clock is the slowest single command, and
nothing names that command or its duration. A `verify:` written into an item
during triage can take `bin/docket check` from 10 s to 59 s, and the only
symptom is that `make check` feels slower.

**Why it matters.** Since `PL-LXR3` made the commands run concurrently, the
cost is set by the slowest member rather than by the number of them. Measured
2026-09-02 on four cores (full detail in `PL-5TN8`):

| Full-suite `--cov` commands in the pool | `bin/docket check` |
| --- | --- |
| 0 (today) | 10.1 s |
| 1 | 59.1 s |
| 4 | 64.9 s |

So one heavy command is worth more attention than twenty light ones, and the
person who writes it is the only one positioned to reconsider it - but they
get no signal at all, and by the time anyone notices, the item is merged and
the cost is charged to every `make check` in every later session.

This is the same finding that produced `PL-5TN8`, generalized. That item asked
whether to ban or proxy a class of expensive command; the observation here is
that neither is needed if the cost simply becomes visible where the decision
is made. A ban decides in advance for commands nobody has written yet; an
advisory lets the one person who can judge it see the number.

**Where.** `subprojects/docket/src/docket/verify.py` - `already_passing`'s
probe already brackets each subprocess, so the duration is free to collect;
`LandedReport` to carry it; `subprojects/docket/src/docket/checks.py` -
`_check_landed`, which owns what the run says about itself.

**Decision needed.** Whether to report a slow `verify:` command at all -
`PL-5TN8` weighed this against banning or proxying the expensive class and
recommended reporting - and if so, whether the threshold is fixed or relative.

A fixed number (say 10 s) is simple and needs re-tuning as the suite grows. A
relative rule - name the slowest command whenever it is some multiple of the
median - needs no tuning and always names exactly the command that sets the
floor, which is the one a reader can act on. The second looks better and is
the reason this is `needs-decision` rather than `ready`.

Whether it is an advisory or purely informational also matters: an advisory
that fires on every run is one every session learns to skim, which
`_check_selects_nothing` already carries the scar tissue for.

**Done when.** A `bin/docket check` whose pool is dominated by one command
names that command, its item, and its duration, so the cost of a `verify:`
is visible to the session that writes it rather than discovered later as a
slower `make check`.

**Found.** 2026-09-02, while working `PL-5TN8` (whether full-suite `--cov`
commands belong in the landed check). Recorded as the recommended answer to
that item's structural question, and left for the project owner to decide
rather than built alongside it.

**Decided 2026-09-02 by the project owner:** build it, with a relative
threshold rather than a fixed one.

**The threshold, measured on this store the same day** rather than chosen.
46 commands, the pool at its configured width on four cores:

| | Wall clock | Median command | Slowest | Slowest / median |
| --- | --- | --- | --- | --- |
| Clean store | 9.5 s | 0.65 s | 8.95 s (`PL-7QKY`) | **14x** |
| One full-suite `--cov` added | 63.2 s | 0.67 s | 59.3 s | **88x** |

So 14x is what a healthy store already looks like and 88x is what the arrival
of a heavy command looks like. **30x** sits between them with roughly twice
the margin above the clean maximum, and lands at ~20 s on today's median -
which is the point where one command doubles the check rather than merely
sitting at its floor. Both figures go in the docstring so the next person can
move the number knowing what it was set against.

The median is the denominator that makes this need no re-tuning. Every command
here pays interpreter and `uv run` startup, so the typical command cannot
collapse toward zero however much the slow ones are narrowed - the two runs
above measured it at 0.65 s and 0.67 s with a 59 s command added to one of
them. A ratio against it therefore tracks *outliers* rather than the general
cost level, which is what rises as the suite grows.

**The alternative considered and not taken** was a counterfactual: report a
command when the check would be materially faster without it, computed by
re-deriving the pool's floor over the remaining durations. It needs no
constant at all and its message could name the exact saving. It was not taken
because it is more machinery for the same finding on the measurements above
(1.6x versus 6.7x separates the two cases, against 14x versus 88x here), and
because a measured constant with its measurement written beside it is how
`landed_workers()` and `LANDED_TIMEOUT` already carry their numbers. Recorded
rather than discarded: if the constant ever needs moving twice, this is the
thing to build instead.

**Durations are as measured under contention**, not standalone - the pool runs
at twice the core count, so every command is slowed by its neighbours. That is
the right basis for this finding, because it is the wall clock a session
actually waits through, and the ratio is what the rule reads rather than the
absolute figure.

**Worked.** `already_passing`'s probe brackets each subprocess, so the
durations were already free to collect; the pool's own wall clock is taken the
same way. `LandedReport` carries `slow` (the commands over the line, worst
first, as `SlowCommand(identifier, seconds)`), plus `typical` and `elapsed` so
the sentence can scale the number it prints rather than showing a bare
duration nobody can read. `_check_slow_commands` in `checks.py` writes the
advisory.

Only commands that ran to completion feed the median. A killed one did not
take its duration - it was stopped at the limit - and one the shell could not
find returns instantly, so either would move the median without having cost
what it appears to.

**A floor was needed under the ratio**, and it is the one thing not
anticipated in the brief. Where every command is trivial the median falls to a
few milliseconds, ordinary process-startup jitter is then tens of times it,
and a 30x rule would name a command that took 100 ms as the thing the check
waits for - the exact false positive this advisory exists not to become.
`SLOW_COMMAND_FLOOR` is one second, the bar for "long enough that a person
waited". On a real store it decides nothing: the median there is 0.65 s, so
the ratio gate stands at ~20 s and is what fires. It bites only where the pool
is small and fast, which is every test in this suite and no real run.

**Both states demonstrated end-to-end against the real store.** Silent as it
stands, 92 open items and 46 commands. With one full-suite `--cov` command put
into the pool:

```
  PL-VG7G (68s) is what this check waits for: that command against a 0.8s
  median and 71s for the whole run. A pool cannot finish before its slowest
  member, so this sets the floor for every `make check` until the item closes
  - narrow the command if it can be narrowed, or accept the cost knowing what
  it is
```

**Reported against the whole run rather than scoped to what `next` will
offer**, unlike `_check_selects_nothing`. That one is scoped because its
finding held for eighteen of thirty-one open items and could never reach zero;
this one holds for none of forty-six on a healthy store, and the threshold is
set against that measurement to keep it so. The cost is also paid regardless
of what is offered, so scoping it to the offer would hide it from the sessions
still paying it.

**Two standard-library imports were added to the portability allowlist** in
`subprojects/docket/tests/test_portability.py`: `time`, to measure a duration,
and `statistics`, for the median. The test guards the no-dependency promise
that lets a bare checkout run this package, and both are standard library, so
admitting them extends the enumeration without weakening what it protects -
a third-party import still fails. Recorded because editing a check to make it
pass is otherwise the shape of exactly the wrong move.

**Documentation swept.** `subprojects/docket/README.md`'s landed-check section
gains the advisory, the ratio and the reason it is a ratio. Checked and left
alone: `README.md`, `docs/worker.md`, `docs/ARCHITECTURE.md`, `CLAUDE.md` and
`.claude/skills/docket/SKILL.md` - the skill tells a session how to write a
`verify:` command and now has a check that answers afterwards, but it
prescribes no cost rule that this contradicts.
