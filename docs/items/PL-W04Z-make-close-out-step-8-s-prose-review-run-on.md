---
id: PL-W04Z
title: Make close-out step 8's prose review run on every simulator branch that changes long prose: only 1 of the 6 simulator branches that held the step from 2026-10-18 to 2026-10-19 recorded running it (#1619), and the 5 that did not wrote prose rated 58% awkward against 22% for #1619 (PL-J6CK)
priority: P3
effort: M
status: needs-decision
classes: housekeeping
feature: prose-quality
touches: .claude/skills/docket/modes/close-out.md, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/config.py, docket.toml, tools/new_prose.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-19
payoff: a simulator branch's long docstrings and comments get the fresh review that cut awkward prose from 58% to 22% of verdicts, rather than skipping it five times in six
---

**Problem.** Close-out step 8 in `.claude/skills/docket/modes/close-out.md`
has a fresh reviewer rewrite each long docstring and comment that a branch adds
to the simulator. `PL-J6CK` measured it on 2026-10-19 and kept it. Six
simulator branches were cut after the step merged (#1598) and merged before
that measurement: #1606, #1609, #1612, #1617, #1618 and #1619. Only #1619 says
in its pull request body that the review ran, as step 8 asks. The prose of the
other five was rated awkward in 35 of 60 blind verdicts (58%), against 13 of 60
(22%) for #1619. So the step works when it runs, but most sessions skip it.

**What to find out.** Why the five sessions skipped the step. Step 8 sits after
steps 5 to 7 in the file but runs before step 5's audit, and nothing checks
that it ran. A check could refuse a simulator pull request whose body lacks the
counts line that step 8 asks for, whenever `tools/new_prose.py` prints a unit.
Whether that check is worth its cost, or a plainer place for the step is
enough, is the question for this item.

`/mnt/project-files/v0.6.0/plain-writing/remeasure-2026-10-19/` holds the
ratings and the scripts.

**Why it matters.** Long prose that skips the review reaches `main` awkward
more than half the time. `PL-J6CK`'s blind ratings put it at 58% of verdicts,
against 22% for the one branch that ran the review. Every such unit is either
read that way for years or rewritten later under the `prose-quality` feature.

**Found 2026-10-19.** The squash bodies on `main` show which close-out steps
each branch reported. Two of the five branches that skipped step 8, #1606 and
#1612, reported running step 5's `bin/docket verify --self`. The other three
reported no close-out step at all. That fits the brief's first guess for the
two: step 8 must run before step 5, but it is written after it, so a session
working down the list stops at step 5's `ACCEPT`. For the other three the
bodies give no reason, and the thread transcripts are not readable from here,
so that part is inferred, not measured.

**Done here, the same under either answer below.** Step 5 now opens by telling
a session on a simulator branch to run step 8 first. The step keeps its number,
because items and documents cite "step 8" by number.

**Decision needed.** Whether to make a skipped review stop the pull request
from arming, or to rely on the new pointer in step 5.

- **Recommended: `bin/docket arm` holds a simulator branch whose long prose
  has no recorded review.** Every session asks `arm` before arming, including
  the three that reported no close-out step, so this is the one moment the
  review cannot be passed over. Step 8 would record its counts as a commit
  trailer, `Prose-review: read N, rewrote M, rejected K`, the way `Owner-read:`
  is recorded now. `arm` would run a command named in `docket.toml`, such as
  `python3 tools/new_prose.py --count`, and hold when that command counts any
  unit and no `Prose-review:` trailer sits on a commit since the newest change
  to the simulator. Docket stays free of this repository's tools, as it is for
  `open_pull_requests_command`. The cost is about one M build in `arming.py`,
  `config.py`, `docket.toml` and `tools/new_prose.py`, with tests, and one more
  reason `arm` can answer `hold`. A forgotten review would then cost a session
  one more commit before it can arm.
- Rely on the pointer. It costs nothing more, and it reaches only a session
  that reads step 5. Measure the next five simulator branches and come back to
  the hold if more than one still skips the review.

Waiting for more branches is the cheaper route with its repayment made
conditional. Each skipped branch adds long prose that the `prose-quality`
feature would rewrite later, so the hold is recommended now.

**Generator check.** Its reader misread whether a close-out step had run,
which no head names. It is one step in one file, so it is an ordinary item.
