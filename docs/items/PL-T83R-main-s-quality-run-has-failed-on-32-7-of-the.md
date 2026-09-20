---
id: PL-T83R
title: main's quality run has failed on 32.7% of the pushes that reached a verdict since 2026-09-05, including one unbroken stretch of 50, so the red-main digest line is closer to routine than to an alarm
priority: P2
effort: M
status: done
classes: infra, session-cost
feature: ci-cost
touches: tools/main_ci_status.py, tests/unit/test_main_ci_status.py, docs/ARCHITECTURE.md, docs/WORKING_NOTES.md
added: 2026-09-16
closed: 2026-09-20
verify: python3 tools/doc_check.py check && grep -qF 'attributed by failing step' docs/WORKING_NOTES.md
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

**Why it matters, and why this is a finding rather than a statistic.** `CLAUDE.md` states that a
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

## Attributed, 2026-09-20

**The whole record, not only the window.** All 819 completed `main` push runs
of `quality.yml` from 2026-08-22 to 2026-09-20 were read, and the failing step
of each of the 109 failures taken from `/repos/.../actions/runs/{id}/jobs`.

| first failing step | all 109 | the item's 74 |
| --- | --- | --- |
| `verify replay, the whole store` | 93 (85.3%) | 73 (98.6%) |
| `bin/docket check`, the bare floor-section run | 14 (12.8%) | 0 |
| the pytest/coverage line | 1 (0.9%) | 1 (1.4%) |
| no job ran at all (startup failure) | 1 (0.9%) | 0 |

**The hypothesis this item was filed on is confirmed at 98.6%.** Reading the
error text back out of every log agrees with the split exactly: the 93 are
`checks.py`'s *"open but its `verify:` command already passes"*, the 14 are
*"marked done but records no `pr`"*, and the one pytest failure is
`test_this_repository_records_a_disposition_for_every_open_debt_item`, which
asserts on `ROADMAP.md`. **Not one of the 109 was a defect in `src/`.**

**One fact settles it without reading a log at all.** In all 93, the bare
`bin/docket check` step ran earlier in the *same job on the same tree* and
passed - as did `ruff`, `mypy` and the full suite at 100% branch coverage. The
bare run is the same store validation without `--verify`, so a failure at the
replay and not at it isolates the cause to the one report `--verify` adds. The
tree was never broken for the thirty-seven hours `main` was red; the store was.

### The rate is the wrong statistic, and that is the finding under the finding

32.7% of pushes reads like a check firing so often nobody can act on it. It is
an artifact of counting *merges*: 74 failures are **8 episodes**, because
merges keep arriving while `main` is red.

| | episodes | longest | red wall-clock |
| --- | --- | --- | --- |
| the item's window | 8 | 50 runs / 37.7 h | **39.0%** |
| 2026-09-16 → 2026-09-20 | 4 | 10 runs / 4.0 h | **6.1%** |

Two episodes hold 87% of the window's red time, and each ended in one cheap
commit: `#432` closed two items whose work had already landed, `#493` rewrote
one command that did not discriminate. **What was wrong was the time to green,
not the count** - and since the window closed, episode length has collapsed to
about an hour without anything being changed.

### Why the rate is accepted rather than moved

Naming the number that would have to be wrong, per `.claude/rules/expert-review.md`:
suppressing this class - making `already_passing` an advisory on `main` - is
right only if enough of what it suppresses would not have mattered. The count
is **93 of 93 real**: every one was a genuine store defect that somebody later
fixed, and several closing commits say so in their own subject. That kills
suppression outright. Nor can the sweep move before the merge: these fire when
an *unrelated* merge flips a command to passing, which no pull request can
predict, and `PL-SDHR` already priced the whole-store replay on every branch at
87 s of a 152 s job, growing with the queue.

So the rate stands and the **line is made precise instead**.

### The change

`tools/main_ci_status.py` makes one more request - only on a run that was
already going to print a line, never on a green `main` - and names the failing
step. Where the replay is the *only* failing step it says so and hands over
`bin/docket check --verify`, which reproduces it locally in seconds; where
anything else failed it names the steps and interprets nothing, because the
bare check passing earlier in the same job is the whole of what makes the queue
reading sound. Before:

    main's quality run #2400 on 286da007 concluded failure - main is red and no
    pull request will show it. <url>

After, on that same real run:

    main's quality run #2400 on 286da007 concluded failure at "verify replay,
    the whole store", and nothing else in that job failed - so `main` is red on
    the queue rather than on the tree: an open item's `verify:` command has
    flipped to passing. `bin/docket check --verify` reproduces it here. <url>

The step name is a literal GitHub derives from `quality.yml`, so a test holds
`REPLAY_STEP` to that file: a rename fails a test rather than silently dropping
the attribution back to the plain line.
