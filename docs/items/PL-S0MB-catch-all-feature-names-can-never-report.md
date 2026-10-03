---
id: PL-S0MB
title: Catch-all feature names can never report completion: dev-tooling carries 174 items and queue-hygiene 29, so bin/docket feature <name> cannot answer 'yes, that is dealt with' for either, and 32 of 33 workflow features read as live
priority: P3
effort: M
status: ready
classes: infra
feature: convergence-visibility
touches: docs/items, docket.toml, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_checks.py
added: 2026-09-17
verify: grep -qF 'retired_features' docket.toml
---

**Problem.** Catch-all feature names can never report completion: dev-tooling carries 174 items and queue-hygiene 29, so bin/docket feature <name> cannot answer 'yes, that is dealt with' for either, and 32 of 33 workflow features read as live

**Observed 2026-09-17.** `CLAUDE.md` requires a group be named for what
*completes*. Two of the workflow lane's largest are named for an area instead,
and an area never finishes.

| feature | items | open | filed prev 7d | filed last 7d |
| --- | --- | --- | --- | --- |
| dev-tooling | 174 | 44 | 58 | 28 |
| parallel-sessions | 71 | 19 | 33 | 17 |
| queue-hygiene | 29 | 18 | 0 | 29 |

Across the whole lane: **33 workflow features, of which 5 have no open items
and 1 meets the stricter test of no open items and nothing filed for 7+ days.**
So 32 of 33 read as live work.

**Why it matters: the cost is not tidiness.** `.claude/rules/instruction-writing.md` rule 14
sends a reader to `bin/docket feature <name>` so that "is that dealt with?" has
a command behind it rather than a memory. For `dev-tooling` that command cannot
ever answer yes: something was filed against it yesterday and something will be
tomorrow, because the name admits anything touching a tool. The reader asking
whether progress is being made is told, correctly and uselessly, that 44 items
are open. This is a measurable contributor to the lane reading as
whack-a-mole when its severity mix says otherwise — 0 open P1, 51% of the open
backlog P3.

`queue-hygiene` is the same failure forming in real time: 0 items filed in the
week to 09-10, 29 in the week to 09-17. It is becoming the next bucket.

**Decision needed, and the counter-case to answer before it.** Whether
`dev-tooling`, `parallel-sessions` and `queue-hygiene` are split into groups
that terminate, or have the `feature` field dropped so the queue stops claiming
a grouping it does not have. The count that decides it: Some of these names may be doing
real work as lane or routing hints rather than as completion groups, and
splitting 174 items by hand is itself apparatus work of the kind `CLAUDE.md`
warns about becoming the project. The number that decides it: how many of
`dev-tooling`'s 44 open items fall into groups that *would* terminate. If the
answer is that they are genuinely unrelated one-offs with no completing group
among them, the remedy is not a split but dropping the feature field on them,
so the queue stops claiming a grouping it does not have.

**Do not resolve this by renaming alone.** A name that completes but still
carries unrelated items moves the problem rather than removing it.

**Done when.** `docket.toml` lists `dev-tooling`, `parallel-sessions` and
`queue-hygiene` as retired, `bin/docket check` errors on an open item carrying
one of them, no open item does, and each of the fourteen members below sits in
the group named for it or where the build thread placed it with its reason -
so that `bin/docket feature <name>` can answer "yes, that is dealt with" for
every group the reply block in `.claude/rules/instruction-writing.md` rule 14
would point a reader at. [Rewritten 2026-10-03 in the decided form; the filed
form asked for the count below to be run and the decision it settles taken.]

## Decided 2026-10-03 - split what completes, unname the rest, retire the three names

**The count the brief asked for, taken 2026-10-03.** The three names have
drained since filing: `dev-tooling` is 174 of 220 done with 10 open (44 open at
filing), `parallel-sessions` 76 of 90 with 5, `queue-hygiene` 26 of 39 with 5.
The lane now has 60 features underway, 11 not started and 55 finished
(`bin/docket status`), so "32 of 33 read as live" no longer describes it: the
rule `PL-N638` wrote into `CLAUDE.md` on 2026-09-16, name the group for what
completes, is being followed for new groups. But the three names are still
being handed members - 4, 6 and 2 items `added:` on or after 2026-09-26 - so
they do not drain to zero on their own, and `bin/docket feature <name>` still
cannot answer for any of them.

Of the 20 open members, 14 fall into a group that completes and 6 do not:

| open member | where it goes |
| --- | --- |
| `PL-X229`, `PL-S5YM`, `PL-DHJ7` (dev-tooling) | `doc-consistency-checks`, which already holds four `doc_check` defects |
| `PL-41YP`, `PL-8LDF` (dev-tooling) | one new name: both tie a `docs/MODEL.md` required list to the tests that hold it |
| `PL-L1NX`, `PL-NDGS` (dev-tooling) | one new name: both are `contrast_check --base` reading an entry wrongly |
| `PL-4ZK8`, `PL-7B3G` (parallel-sessions) | one new name: both are what `bin/docket concurrent` hands a fan-out |
| `PL-2C53` (parallel-sessions) | `landed-elsewhere`, which holds `tools/left_behind_check.py`'s remaining work |
| `PL-99YZ` (parallel-sessions) | `open-item-overlap-detection`: one defect taken up twice, as work rather than as items |
| `PL-037Y`, `PL-0R06` (queue-hygiene) | `closed-item-claims`: `docs/WORKING_NOTES.md` stating a closed item's state wrongly |
| `PL-PTD8` (queue-hygiene) | `merge-skew`, finished, and honestly reopened: the add/add route `PL-MTHC` left open |
| `PL-90CJ`, `PL-M3YJ`, `PL-QHCP`, `PL-KRGY`, `PL-YVV4`, `PL-YZKK` | no completing group: the `feature:` field comes off, and `bin/docket status` lists them under "Outside any feature - picked on priority alone", which is the honest place |

The build thread may place a member differently where a closer read of its
brief says so, with the reason in that member's file; the count decides the
remedy, not the exact homes. Fourteen of twenty have a completion to join, so
the remedy is the split the brief names, with the field dropped on the six -
not the field dropped on all twenty, which the brief reserved for the case
where no completing group existed.

**Then the names are retired by a check, because prose did not stop them.**
`CLAUDE.md` has said since 2026-09-16 that a group is named for what
completes, and 12 captures in the week to 2026-10-03 named one of these three
anyway - the "being routed around" test `CLAUDE.md` sets for a rule a script
should hold. `docket.toml` gains `retired_features = ["dev-tooling",
"parallel-sessions", "queue-hygiene"]`, read beside `process_classes` in
`config.py`, and `bin/docket check` errors on an **open** item carrying one,
next to `_check_feature_spellings`, which already reads every item's
`feature`. Closed items keep theirs, so the history stays readable and the
three names report as finished.

**Recommendation:** the split above, the field off the six, and the
retired-names check. **Decided 2026-10-03** by the design-round session as an
obvious call, over dropping the field on all twenty (which loses fourteen real
memberships) and over leaving the names to drain (they refill at a dozen a
week). It is a build, M: twenty front-matter edits by `bin/docket set
--feature`, three new names, one `docket.toml` list, one check with its test.
Not a rename of any of the three, which the brief refuses: a name that
completes but still carries unrelated items moves the problem.
