---
id: PL-W04Z
title: Make close-out step 8's prose review run on every simulator branch that changes long prose: only 1 of the 6 simulator branches that held the step from 2026-10-18 to 2026-10-19 recorded running it (#1619), and the 5 that did not wrote prose rated 58% awkward against 22% for #1619 (PL-J6CK)
priority: P3
effort: M
status: done
classes: housekeeping
feature: prose-quality
touches: .claude/skills/docket/modes/close-out.md, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, docket.toml, tools/new_prose.py, tests/unit/test_new_prose.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-19
closed: 2026-10-19
pr: 1645
payoff: a simulator branch's long docstrings and comments get the fresh review that cut awkward prose from 58% to 22% of verdicts, rather than skipping it five times in six
verify: grep -q 'def test_arm_holds_without_prose_review' subprojects/docket/tests/test_arming.py && grep -q 'def test_arm_holds_when_prose_count_fails' subprojects/docket/tests/test_arming.py && grep -q 'def test_counts_units_since_commit' tests/unit/test_new_prose.py && grep -q 'Prose-review:' .claude/skills/docket/modes/close-out.md
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

[superseded 2026-10-19: decided below.] **Decision needed.** Whether to make a skipped review stop the pull request
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

**Decided 2026-10-19: `bin/docket arm` holds a simulator branch whose long
prose has no recorded review.** This is the recommendation above. It was taken
in the workflow decision round without putting it to the owner, because one
option is clearly correct (`.claude/rules/instruction-writing.md` rule 14).
`CLAUDE.md` gives standing approval for putting the decidable part of a rule in
code. Whether `tools/new_prose.py` counts a unit and whether a trailer is
recorded are both decidable. Whether each rewrite is good stays with the
session and its reviewer. No open workflow-lane generator is live, so the
generator pause does not hold this back. The alternative, relying on the
pointer in step 5 and measuring five more branches, was refused. It is the
cheap route with its repayment made conditional, which
`.claude/rules/expert-review.md` says to count first. The count is already in
this item: five of six branches skipped the review, and each one added long
prose that the `prose-quality` feature would have to rewrite later.

The round settled four details of the build, all of them the session's to
decide:

1. **The record is a commit trailer**, `Prose-review: read N, rewrote M,
   rejected K`, read with the helper that reads `Owner-read:`. Step 8 still
   asks for the same counts in the pull request body, because a reader of the
   squash commit sees the body and not the branch's trailers.
2. **The count covers only prose added since the newest record.** `arm` runs
   the command named in `docket.toml` over the commits after the newest
   `Prose-review:` trailer, or over the whole branch when there is none, and
   holds when it counts any unit. A code fix after the review then needs no
   second review, while a new long docstring does. Holding on any simulator
   change since the record, as `Owner-read:` does, would ask for a review of
   prose that was already reviewed. `tools/new_prose.py` gains the option that
   counts from a given commit. Docket names no repository tool, so the command
   comes from `docket.toml`, as `open_pull_requests_command` does.
3. **One hold message names both missing records.** When a branch lacks both
   `Owner-read:` and `Prose-review:`, `arm` names both in one answer, so a
   single commit can carry both trailers and the session does not meet a second
   hold after clearing the first.
4. **A command that fails is a hold, not a pass.** When the configured command
   exits non-zero, `arm` holds and says the count could not be read. A branch
   whose prose could not be counted is never armed as though it had none.

Done when `bin/docket arm` holds a branch that adds a long unit with no
`Prose-review:` trailer after it, arms the same branch once the trailer is
recorded, and holds again when a later commit adds another long unit. Close-out
step 8 tells a session to record the trailer. The tests named in `verify:`
cover the three cases and the failing command.

**Done 2026-10-19.** `bin/docket arm` now holds a simulator branch while
`prose_count_command` counts any long docstring or comment that no
`Prose-review: read N, rewrote M, rejected K` trailer covers, and while that
count cannot be read. `docket.toml` names `python3 tools/new_prose.py --count`.
That mode reads the committed branch from the fork to `HEAD`. Given the commit
that carries the newest record, it counts a unit only when its text was not a
unit of the same file at that commit. So a code fix after the review needs no
second review, a new or reworded long unit does, and prose that a merge of the
default branch brings in is not counted, because it is not in the branch's
own diff. A record that is not in the trailer's form is named and covers
nothing. When a branch also lacks its `Owner-read:` record, one hold names
both, so one commit can carry both trailers. Close-out step 8 now tells a
session to record the trailer. `subprojects/docket/tests/test_arming.py` pins
the three cases, the failing count, the combined hold, a change outside the
simulator that is not counted, and the command's output contract.
`tests/unit/test_new_prose.py` pins the count, its reading of commits rather
than the working tree, the merge case, and the exit on a file Python refuses.
