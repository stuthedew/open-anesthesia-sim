---
id: PL-1XQP
title: arming's _read_change counts a file under docket.toml's record_dir (the copied guard refusals) as worked change, so a bin/docket record run after an Owner-ask or Owner-read record makes that record stop covering the branch; it should exclude vcs.queue_records' directories as in_queue does
priority: P3
effort: S
status: done
classes: defect
feature: guard-refusal-log
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_arming.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-04
closed: 2026-11-04
pr: 2016
payoff: copying a branch's guard refusals after its question for the owner is recorded no longer makes the merge gate ask for the question again
verify: grep -q 'def test_a_copied_refusal_log_leaves_the_recorded_ask_in_force' subprojects/docket/tests/test_arming.py
---

**Problem.** arming's _read_change counts a file under docket.toml's record_dir (the copied guard refusals) as worked change, so a bin/docket record run after an Owner-ask or Owner-read record makes that record stop covering the branch; it should exclude vcs.queue_records' directories as in_queue does

**Evidence.** Read 2026-11-04 while building `PL-52SV`. `arming._read_change` sets `worked` to every changed path outside the items directory and `vcs.RECORDS`. `_owner_ask` and `_owner_read` then count only records made since the newest commit that changed a `worked` path. Since `PL-QLNX`, `vcs.queue_records` also lists `record_dir`, but `_read_change` does not read it. Not reproduced on a branch yet.

**Why it matters.** A thread that records its question for the owner and then copies the guard refusals it met finds the merge gate asking for the question again, and the owner-ask guard stops it from messaging the owner. The copy is a record of the work, so it should count no more than an item file does.

**Done when.** `arming._read_change` leaves the record directory out of the worked change, read from `docket.toml`'s `record_dir` through the arm, flight and owner-ask paths. A test in `subprojects/docket/tests/test_arming.py` shows an `Owner-ask` record still answering after a later commit that only adds a file under the record directory.

**Generator check.** None. It is a missed reader of `record_dir`, the fact `PL-QLNX` gave one home.
