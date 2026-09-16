---
id: PL-T83R
title: main's quality run has failed on 32.7% of the pushes that reached a verdict since 2026-09-05, including one unbroken stretch of 50, so the red-main digest line is closer to routine than to an alarm
status: untriaged
added: 2026-09-16
---

**Problem.** main's quality run has failed on 32.7% of the pushes that reached a verdict since 2026-09-05, including one unbroken stretch of 50, so the red-main digest line is closer to routine than to an alarm

**Measured while closing `PL-SMN4`**, over the same window and the same data:
every completed `main` push run of `.github/workflows/quality.yml` from
2026-09-05 22:22 UTC to 2026-09-16 01:22 UTC, read from
`/repos/.../actions/workflows/quality.yml/runs?branch=main&event=push&status=completed`.

| conclusion | runs |
| --- | --- |
| success | 152 |
| failure | 74 |
| cancelled | 31 |

Of the 226 that reached a verdict, **74 failed - 32.7%**. The cancelled 31 are
`PL-SMN4`'s eviction defect and are excluded here rather than counted either
way, because they judged nothing.

**The shape matters more than the rate.** Failures are not spread evenly across
the window: there are three unbroken red stretches of five or more, of lengths
**50, 9 and 5**. The longest ran from run #1397 (`99b6f4ab`, 2026-09-06 03:19
UTC) to run #1546 (`3d6d6ca5`, 2026-09-07 16:46 UTC) - **37 hours and fifty
consecutive merges during which `main`'s whole-store check was red the whole
time**.

**Why that is a finding rather than a statistic.** `CLAUDE.md` states that a
check firing every run without changing a decision is a defect in the check,
because it trains a session to skim the region where a real advisory appears.
The session-start digest's red-`main` line is exactly such a region, and
`tools/main_ci_status.py` was built (`PL-0ZGK`) on the premise that a red `main`
is the exception worth one HTTP call to surface. At a third of merges - and for
thirty-seven hours at a stretch - it is not the exception, and a session that
starts during one of those stretches gets a line about somebody else's breakage
that it can do nothing with.

**What is not measured, and should be before anything is designed.** The
breakdown of the 74 by cause. `bin/docket check --verify` replays every open
item's own `verify:` command on this event only, so a single stale command in
the store turns `main` red without anything being wrong with the tree -
`PL-GN8C` and `PL-S5YM` are both instances, and `PL-0ZGK`, `PL-D2GW` and
`PL-99Y4` describe three more mechanisms that redden `main` from the queue
rather than from the code. If most of the 74 are that class, the finding is
about the replay's failure mode rather than about code quality, and the answer
is different: the tree was never broken for thirty-seven hours, the store was.
Reading the failing step out of each run's `/jobs` is what settles it, and is a
morning's work rather than a guess.

**Done when.** The 74 are attributed to causes, and the project has either a
reason to accept the rate or one change that moves it. Whichever way that goes,
the digest line should end up meaning what it says.
