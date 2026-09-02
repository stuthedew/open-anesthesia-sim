---
id: PL-5TN8
title: Two core-guard-coverage items will each add a ~50 s full-suite --cov command to every make check when triaged
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.2.10
touches: docs/items/, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py
added: 2026-09-02
closed: 2026-09-02
pr: 195
---

**Problem.** `PL-NC2P` and `PL-YMY7` are open, `ready`, in
`core-guard-coverage`, and carry no `verify:` command yet. Every coverage item
in that feature has taken the shape `uv run pytest --cov=<module>
--cov-fail-under=100`, which is a full-suite run measured at ~50 s. Giving
those two the same shape puts two ~50 s commands into the set `bin/docket
check` executes on every `make check`.

**Why it matters.** `PL-LXR3` made that set run concurrently, which took
`bin/docket check` from 34.9 s to 10.1 s. A pool cannot go faster than its
slowest member, so two ~50 s commands would take the figure to roughly 50 s -
better than the ~140 s it would have been serially, but still five times where
it stands, and arriving in a single triage pass rather than gradually. The
shape of the cost has changed with concurrency: it is now set by the slowest
command rather than by the number of them, so one heavy command is worth more
attention than twenty light ones.

Recorded while resolving `PL-LXR3`'s merge, where the risk was raised by a
parallel triage branch and only partly closed: concurrency reduced it, and
nothing prevents it.

**Where.** `docs/items/` - the two named items' `verify:` fields when they are
triaged; `subprojects/docket/src/docket/verify.py` if the answer turns out to
be a rule rather than a per-item choice.

**Worth deciding first.** Whether the answer is per-item or structural. A
coverage item's command is a full-suite run *by necessity* - coverage of a
module is the union of everything that exercises it, which is why
`.claude/skills/docket/SKILL.md` prescribes that shape and warns against
scoping it to one file. So narrowing these two the way ordinary commands are
narrowed is not available, and the options are different in kind: accept the
~50 s floor; exclude `--cov` commands from the landed check and record why;
or give the landed check a cheaper proxy for a coverage item. The last is the
one that would need designing.

**Done when.** Either the two items are triaged with commands whose cost is
known and accepted, or `bin/docket check` no longer pays full-suite coverage
runs for open coverage items, with the reasoning recorded either way.

**Measured 2026-09-02, four cores, this checkout.** The brief's arithmetic
above is the wrong shape, and the measurement is what changes the decision.
Cost is a step at the *first* coverage command, not a charge per item:

| Full-suite `--cov` commands in the pool | `bin/docket check` | Marginal |
| --- | --- | --- |
| 0 (today) | **10.1 s** | - |
| 1 | **59.1 s** | +49.0 s |
| 2 | **62.6 s** | +3.5 s |
| 4 | **64.9 s** | +2.3 s |
| 6 | **87.0 s** | +11.1 s each |

The full suite is 56.3 s on its own and a `--cov` run over it 56.5 s, so the
concurrency `PL-LXR3` landed already absorbs the second, third and fourth
almost entirely; the pool only degrades past the core count. "Two items at
~50 s each" is therefore one item at 49 s and a second at 3.5 s.

**This dissolves the premise for the two items named.** Neither can carry the
coverage shape, for reasons recorded in each:

- `PL-NC2P` - `app/main.py`'s uncovered set includes line 36, `if __name__ ==
  "__main__": main()`, which pytest imports rather than executes.
  `--cov-fail-under=100` is unreachable without a coverage exclusion, and
  granting one is part of the decision the item asks for.
- `PL-YMY7` - its own finding is that the remaining statements need a
  rendering harness the project does not have, so the threshold could never be
  met by doing the work the item describes. Its `touches` is a `docs/items/`
  file; the work product is a recorded decision.

Both are disjunctive - "either covered, or the reason recorded" - so a
threshold command fails forever under the outcome the item explicitly allows.
The right command for each is the paired doc shape the skill already
prescribes, at well under a second. **No triage pass is going to put a ~50 s
command in the pool via these two.**

**The structural question is real but has no live instance.** Coverage items
recur - six have existed, all now `done` - so a seventh naming a module that
can genuinely reach 100% would cost the +49 s step. The three options in the
brief above, against the measurement:

- **A cheaper proxy** is the one the brief called "the one that would need
  designing", and the measurement rules it out. Batching every coverage item
  into one instrumented run lands at the n=1 figure, so it saves 3.5 s at two
  items and 5.8 s at four, in exchange for `docket` learning `pytest-cov`,
  parsing a coverage report, and attributing per-module results - breaking the
  standard-library-only, shells-out-never-imports separation that lets it run
  from a bare checkout. Not worth it at any item count the project will reach.
- **Excluding `--cov` commands** costs little to implement and removes the
  check where its hit rate is highest: a coverage item is done the moment its
  module reaches 100%, which routinely happens as a side effect of another
  item's tests, which is precisely the "work landed, item never closed" case
  the check exists to catch. Excluding them silently is the failure this
  module refuses everywhere else; excluding them *and reporting it* means
  paying for a mechanism whose output is "I did not look".
- **Accepting the floor** is correct, costs nothing to implement, and is paid
  only while a genuine coverage item is open - which is currently never.

**Recommendation: accept the floor, and make the cost visible instead of
banning it.** Captured as `PL-VG7G`. Nothing today tells a reader that one
item's command sets the floor for every `make check`; the run knows each
command's duration and says nothing about it. An advisory naming a command
over some threshold turns an invisible recurring cost into a visible one at
the moment it appears, without banning a command, without a proxy, and
without deciding anything in advance - which is the disposition this project
prefers for a decidable fact.

**`PL-T940` was found and fixed here**, and is the half that was not
optional. A command exceeding `LANDED_TIMEOUT` returned 1 - what a failing
test returns - so it fell out of every finding while still counting as
checked. Six concurrent full-suite runs peak at 76.0 s against the 120 s
limit (1.58x headroom), and half the cores would cross it, at which point six
items silently stopped being checked and the report stayed clean. That, not
the wall clock, was the dangerous part of letting heavy commands into this
pool, and it is fixed regardless of how the question above is answered.

**Resolved as neither branch of "Done when", which is why it is spelled out.**
The two items are not triaged - writing a `verify:` away from its work is what
the skill forbids and how all six wrong commands here came to exist - but each
now records that the coverage shape does not fit it and what its command will
cost instead (under a second), which is the substance the first branch asked
for. `bin/docket check` still runs full-suite coverage commands when one
exists; the reasoning for accepting that is above, and the residual - making
the cost visible - is `PL-VG7G`, left as a decision rather than built here.
Reopen if the third disposition is not wanted.
