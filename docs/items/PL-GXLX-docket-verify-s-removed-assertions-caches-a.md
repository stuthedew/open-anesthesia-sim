---
id: PL-GXLX
title: docket verify's removed_assertions caches a parse by blob id and marks a file unparsed only on the first failed parse, so two identical unparseable files edited identically report one file's removed lines and name only the first; latent
status: dropped
added: 2026-10-04
closed: 2026-10-05
reason: premise false on 2026-10-05: #1374 (a341dcd0, PL-TC2D) replaced the per-blob cache that kept a failed parse with _read_versions, which keeps only successful reads, so two identical unparseable files are now both named and both counted; reproduced at b67dace8
---

**Problem.** docket verify's removed_assertions caches a parse by blob id and marks a file unparsed only on the first failed parse, so two identical unparseable files edited identically report one file's removed lines and name only the first; latent

**Found 2026-10-04 by the triage pass**, reproducing `PL-MR8Z` against `main` at `8cc0698d`: `removed_assertions` in `subprojects/docket/src/docket/verify.py` caches each file's parse by blob id, but marks a file unparsed only on the first failed parse. Two identical unparseable files, edited identically, report "1 line(s)" and name only the first. The check still fails, so nothing passes that should not; the count and the file list come up short. Untriaged; with `PL-MR8Z`, the second instance of `PL-4W2L`'s fact since that head closed on 2026-09-23.

**Premise false on 2026-10-05, at triage.** `a341dcd0` (`PL-V2HK, PL-TC2D,
PL-R417`, #1374, merged 2026-10-05) replaced the `reading` closure that stored
an empty `AssertionReading()` under a blob id that failed to parse, with
`_read_versions`, which stores only a successful read, so the second identical
file fails again and is marked as the first was; `added_suppressions` moved
onto the same helper. Reproduced on `main` at `b67dace8` with two identical
files the tokenizer refuses too (an unterminated `"""`), both losing `assert y
== 2` in one commit: `removed_assertions` named both files in `unparsed` and
returned both removed lines; with two identical files only the tokenizer reads
(`type X = int`), it charged both in `absent`. No test pins the two-file case.

**Generator check.** An instance of `PL-4W2L`'s fact, whether a branch's diff
weakens its tests, filed after that head closed on 2026-09-23: the cache made
the report of which files lost assertions come up short. With `PL-MR8Z` it is
the second post-close instance (`bin/docket generators --misread`; `PL-CFWP`
and `PL-TC2D`, filed since, are `PL-R417`'s), one short of the three triage
reads as a fix that did not hold, so not a generator.
