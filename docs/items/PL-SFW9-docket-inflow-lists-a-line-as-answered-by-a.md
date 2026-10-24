---
id: PL-SFW9
title: docket inflow lists a line as answered by a successor head whatever the successor's status, so a line re-entered after its successor closed spent still reads as settled, where a no-successor answer is reopened by three later filings; PL-5DZ8 read as answered by PL-4S6C (done) while PL-TSXD re-entered it (found recording PL-N4FP)
status: untriaged
feature: one-source-of-truth
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/, tools/
added: 2026-10-24
---

**Problem.** docket inflow lists a line as answered by a successor head whatever the successor's status, so a line re-entered after its successor closed spent still reads as settled, where a no-successor answer is reopened by three later filings; PL-5DZ8 read as answered by PL-4S6C (done) while PL-TSXD re-entered it (found recording PL-N4FP)
