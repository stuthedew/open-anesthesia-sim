---
id: PL-GXLX
title: docket verify's removed_assertions caches a parse by blob id and marks a file unparsed only on the first failed parse, so two identical unparseable files edited identically report one file's removed lines and name only the first; latent
status: untriaged
added: 2026-10-04
---

**Problem.** docket verify's removed_assertions caches a parse by blob id and marks a file unparsed only on the first failed parse, so two identical unparseable files edited identically report one file's removed lines and name only the first; latent

**Found 2026-10-04 by the triage pass**, reproducing `PL-MR8Z` against `main` at `8cc0698d`: `removed_assertions` in `subprojects/docket/src/docket/verify.py` caches each file's parse by blob id, but marks a file unparsed only on the first failed parse. Two identical unparseable files, edited identically, report "1 line(s)" and name only the first. The check still fails, so nothing passes that should not; the count and the file list come up short. Untriaged; with `PL-MR8Z`, the second instance of `PL-4W2L`'s fact since that head closed on 2026-09-23.
