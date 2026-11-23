---
id: PL-LJK4
title: bin/docket inflow re-reads a past week's lanes against today's workflow path list, so deleting an apparatus test file moves old filings out of the workflow lane: the week of 2026-11-02 read 12 P1 apparatus filings at the v0.6.17 cut and 9 after #2149 deleted tests/unit/test_rejected_prose.py
priority: P3
effort: S
status: done
classes: defect
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, subprojects/docket/tests
deferred-from: v0.7.0 - filed after the gate froze; a history row of an apparatus report, with no effect on what a learner sees
added: 2026-11-23
closed: 2026-11-23
pr: 2307
filed-pr: 2301
payoff: a past week's row in docket inflow reads the same tomorrow as it did at the cut
tests: subprojects/docket/tests/test_inflow.py::test_deleting_a_listed_file_leaves_an_earlier_weeks_row_unchanged, subprojects/docket/tests/test_inflow.py::test_the_command_judges_a_filing_by_the_config_committed_on_its_day
---

**Problem.** bin/docket inflow re-reads a past week's lanes against today's workflow path list, so deleting an apparatus test file moves old filings out of the workflow lane: the week of 2026-11-02 read 12 P1 apparatus filings at the v0.6.17 cut and 9 after #2149 deleted tests/unit/test_rejected_prose.py

**Found 2026-11-23** while reading the week of 2026-11-02 for `PL-40ZB`. `docket inflow` decides each filing's lane from `docket.toml`'s `workflow_paths` as they are today. The list names each apparatus test file one by one, so #2149's deletion of `tests/unit/test_rejected_prose.py` took it off the list, and `PL-22T5`, `PL-556C` and `PL-F0Q2`, which name it, now read as crossing the lanes. A past week's row changes without saying so. A release verdict is not affected, because a cut reads the last complete week. A filing's lane at the time it was filed is a fact nobody records.
<!-- absent: tests/unit/test_rejected_prose.py -->

**Why it matters.** The owner reads `bin/docket inflow`'s history rows to see whether apparatus inflow is falling. A row that changes after the week was read can show a fall that did not happen.

**Done when.** A filing's lane is read as it stood when the item was filed, and a test pins that deleting an apparatus test file leaves an earlier week's row unchanged.

**Generator check.** One instance. It is a reader inferring a past fact from today's tree, the shape `.claude/rules/apparatus-standard.md` § "Read the fact from its record" describes.

**Done 2026-11-23.** `docket inflow` and the release cut now read `docket.toml`'s committed history through `vcs.file_revisions`, and `inflow.LaneHistory` judges each filing by the `workflow_paths` committed on its own day together with today's. Today's list is kept because an apparatus test file is listed only once it exists, after the item that filed the work to create it, so judging by the filing day alone would have moved those filings out instead. A shallow clone, a silent git or an unreadable text declines the history, and the table and the cut's miss lines then say each filing was judged by today's list alone. On this repository the change raises the count of new apparatus paths in six weeks, by one or two each, the week of 2026-11-02 from 36 to 38. No week's count of filings moved. Since `PL-7TB2` no prediction reads an item's lane, so what the deleted file had changed was the count of new paths. Files checked for stale statements: `subprojects/docket/README.md` (the inflow section, updated), `.claude/skills/docket/modes/release.md` and `.claude/skills/docket/modes/triage.md` (neither describes how inflow decides a lane).
