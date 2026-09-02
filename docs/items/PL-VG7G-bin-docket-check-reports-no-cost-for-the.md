---
id: PL-VG7G
title: bin/docket check reports no cost for the commands it ran, so a slow one arrives invisibly
priority: P2
effort: S
status: needs-decision
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py
added: 2026-09-02
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
