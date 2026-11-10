---
id: PL-YSV3
title: bin/docket inflow counts a re-entry against the closed item it names and never against the fact that item's head misread, so the repeated-predicate fact, on its fifth root-cause item, reads as five answered lines
status: untriaged
feature: generator-measurement
added: 2026-11-10
---

**Problem.** bin/docket inflow counts a re-entry against the closed item it names and never against the fact that item's head misread, so the repeated-predicate fact, on its fifth root-cause item, reads as five answered lines

**Checked 2026-11-10:** in `subprojects/docket/src/docket/inflow.py` the re-entry count is `reentering.setdefault(closed, []).append(item.identifier)`, keyed on the closed item a filing's `reenters:` names. `bin/docket generators --misread` prints each head's fact and counts nothing across heads. A script over the store's front matter found 16 facts with two to five successive heads. The longest: the repeated predicate (`PL-PVW2`, `PL-KGYT`, `PL-5DZ8`, `PL-4S6C`, `PL-N4FP`); whether the base already holds a change (`PL-BHVM`, `PL-R808`, `PL-GHHW`, `PL-927J`, `PL-P813`); a document sentence against a tree fact (`PL-4FBP`, `PL-G424`, `PL-BLN0`); queue state (`PL-6T44`, `PL-8YXJ`, `PL-RJLQ`); who holds an item (`PL-7TVT`, `PL-8FJK`, `PL-MB2W`); gate dispositions (`PL-J6HP`, `PL-WD5Z`, `PL-8QMD`).

**Why it matters.** `.claude/skills/docket/modes/triage.md` treats three filings after a head closed as a generator whose fix did not hold, and `bin/docket inflow` is what names them. Each new head of a fact starts the count again at zero, and a closed line re-entered by a later head reads as answered by a successor. So the report cannot say that a fact is on its fifth fix, which is the case the count exists for.

**Done when.** `bin/docket inflow` counts re-entries per fact: a filing that re-enters any head whose `misread:` states the fact counts against that fact's first head. `bin/docket generators --misread` prints, for a fact with more than one head, how many heads it has had and the date of the first. A test in `subprojects/docket/tests/test_inflow.py` pins a three-head chain.

**Generator check.** A defect in the machinery that finds and ranks generators, recorded as `impairs-generators:`. A one-off as a mechanism.
