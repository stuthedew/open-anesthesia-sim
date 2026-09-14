---
id: PL-66X4
title: bin/docket release reads each item's pr field to write the release notes, so a cut taken before docket record backfills the numbers the base owes ships those items with no pull request in the permanent record
priority: P2
effort: S
status: dropped
classes: defect
feature: commit-provenance
touches: subprojects/docket/src/docket/release.py
added: 2026-09-13
closed: 2026-09-14
reason: the same finding as PL-2M5T, filed the same day from the other end - this states the mechanism (notes are written from each item's `pr` field, which the cut's own commit has not yet backfilled) and PL-2M5T states the measured instance (9 of v0.4.22's 15 bullets name no pull request). PL-2M5T carries the brief and the fix; nothing here is lost
---


**Problem.** bin/docket release reads each item's pr field to write the release notes, so a cut taken before docket record backfills the numbers the base owes ships those items with no pull request in the permanent record
