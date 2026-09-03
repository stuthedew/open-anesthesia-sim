---
id: PL-9NKK
title: verify.py's LANDED_TIMEOUT and landed_workers() record 48-49 candidates at 34.9 s serial and 6.9 s worst; measured 2026-09-03 it is 78 candidates at 175.5 s serial and 27.4 s worst
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
added: 2026-09-03
closed: 2026-09-03
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -rq 'def test_the_run_reports_what_it_cost' subprojects/docket/tests
---

**Problem.** Two constants in `subprojects/docket/src/docket/verify.py` carry
measurements from 2026-09-02 that the store has since outgrown. `LANDED_TIMEOUT`'s
comment records "48 candidate commands, 34.9s in total run serially and 6.9s at
worst"; `landed_workers()`'s docstring records "49 candidates on a four-core box:
33.9 s serially, 10.8 s at four workers, 10.1 s at eight".

**Measured 2026-09-03**, same checkout, four cores, warm caches, the candidate set
selected exactly as `already_passing` selects it (`status` in `ready`/`needs-decision`
and a `verify:` present):

| | recorded 2026-09-02 | measured 2026-09-03 |
| --- | --- | --- |
| candidate commands | 48-49 | **78** |
| sum of command durations (serial equivalent) | 33.9-34.9 s | **175.5 s** |
| slowest single command | 6.9 s | **27.4 s** (`PL-GS5X`) |
| pool at four workers | 10.8 s | **31.6 s** |
| pool at eight workers | 10.1 s | **28.0 s** |
| median command | 0.65-0.67 s | **0.64 s** |

`bin/docket check` as a whole measured **28.8 s** in the same run.

**Why it matters.** The comment on `LANDED_TIMEOUT` is, in its own words, "the only
record of the cost anyone reading this constant sees" - the same argument `PL-LXR3`
used to justify updating it last time. The worst case is the figure that constant
exists to bound, and it has moved from 6.9 s to 27.4 s: the margin under the 120 s
limit fell from ~17x to ~4.4x. The timeout still holds and nothing is failing, so
this is a record-keeping defect rather than a live fault - but it is the second
time the same two numbers have gone stale within a fortnight, which is the argument
for the second half below.

The median is unchanged at 0.64 s. The growth is entirely in the *number* of
candidates, which is what `PL-LXR3` predicted ("every item triaged to `ready` adds
its command's runtime permanently") and what the store's own growth delivered: 99
item files on 2026-08-25, 378 on 2026-09-03.

**Where.** `subprojects/docket/src/docket/verify.py` - the `LANDED_TIMEOUT` comment
and the `landed_workers()` docstring.

**Worth considering while fixing it.** These two figures have now gone stale twice
under the same mechanism: a hand-written measurement in a comment, invalidated by
ordinary queue growth nobody was watching. `bin/docket check` already computes every
one of them at run time - the pool's elapsed, each command's duration, the median,
the count - and `PL-VG7G` already put one of them on screen. Printing the count and
the pool's elapsed alongside the existing advisory would retire the comment's job
rather than re-doing it, which is the disposition CLAUDE.md's "prefer deterministic
tooling" section names first. Weigh that against the advisory-fatigue rule: a line
printed every run that changes no decision is a defect in the check.

**Done when.** Both figures match a measurement taken on the store as it stands, or
the comment is replaced by something the tool computes.

**Worked.** The comments do not carry a measurement any more; `check` reports
one, on the line under its headline:

```
docket: 141 open (…), 0 errors, 3 advisories
  verify: 82 commands in 31.1s (181.4s serially); slowest PL-GS5X 26.4s against a 120s limit
```

**A third stale copy turned up while fixing the two.**
`subprojects/docket/README.md` carried "2026-09-02, 47 candidates: 34.9 s
serially, 10.1 s concurrently" as well, which the brief above did not know
about. That is the argument for the disposition rather than against it: the
figure had been hand-copied to three places and every one of them was wrong,
because the mechanism that made them stale is copying rather than any one
author's oversight. All three are now replaced by the reading `check` takes at
run time.

**Two fields were missing and are added.** `LandedReport` carried `elapsed`
and `typical` but not the serial total, and named the slowest command only
when it cleared `SLOW_COMMAND_RATIO`. Both are on the line for reasons the
other findings do not cover:

- `serial` is the half that carries the news. Concurrency holds `elapsed`
  roughly flat as the store grows, so the number a session feels is the one
  that hides the growth - 10.1 s to 28.8 s while the serial total went 34.9 s
  to 175.5 s. Reporting only the wall clock would have hidden this item's own
  finding.
- `slowest` answers a different question from `slow`. `slow` fires on an
  outlier against the median and is silent on a store where everything is
  uniformly heavy, which is exactly the store whose margin against
  `LANDED_TIMEOUT` is closing. The margin always has an answer; whether an
  outlier arrived usually does not.

**Reported as a fact, not an advisory**, and kept out of `errors`,
`advisories` and `declined`. `CLAUDE.md` holds that a check firing every run
without changing a decision is a defect in the check - a rule about findings,
which demand judgment. This is the category of the open-item counts beside it:
scanned, acted on by nobody, and worth its line because a change in it is the
signal. `_note_cost`'s docstring carries the argument.

It stays silent where the run declined, where no caller asked, and where the
store holds no command to run, rather than printing zeros - an empty result
rendered as a measured one is the error this module is built to refuse. The
CI `floor` job is the live instance: no `uv` on that runner, so every command
returns 127, the run declines, and no cost line is printed.

**Tests.** Nine in `test_checks.py` over the reported line and its four silent
cases, five in `test_verify.py` over the two new fields - including that a
command killed at the limit counts into neither, since it was stopped rather
than having cost its duration. Each was checked against a mutated
implementation rather than only against the working one: removing the
`_note_cost` call fails six, and stubbing `serial` to zero fails one.

**Not done here.** `PL-FRGP` - the slow-command advisory that overstates what
narrowing the command it names would save - is the same file and was
deliberately left alone: it is a separate decision the project owner has not
taken, and the wording this item touches is the headline rather than that
advisory.
