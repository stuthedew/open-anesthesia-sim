---
id: PL-9NKK
title: verify.py's LANDED_TIMEOUT and landed_workers() record 48-49 candidates at 34.9 s serial and 6.9 s worst; measured 2026-09-03 it is 78 candidates at 175.5 s serial and 27.4 s worst
status: untriaged
feature: dev-tooling
added: 2026-09-03
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
