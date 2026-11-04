---
id: PL-1XQP
title: arming's _read_change counts a file under docket.toml's record_dir (the copied guard refusals) as worked change, so a bin/docket record run after an Owner-ask or Owner-read record makes that record stop covering the branch; it should exclude vcs.queue_records' directories as in_queue does
status: untriaged
feature: guard-refusal-log
added: 2026-11-04
---

**Problem.** arming's _read_change counts a file under docket.toml's record_dir (the copied guard refusals) as worked change, so a bin/docket record run after an Owner-ask or Owner-read record makes that record stop covering the branch; it should exclude vcs.queue_records' directories as in_queue does

**Evidence.** Read 2026-11-04 while building `PL-52SV`. `arming._read_change` sets `worked` to every changed path outside the items directory and `vcs.RECORDS`. `_owner_ask` and `_owner_read` then count only records made since the newest commit that changed a `worked` path. Since `PL-QLNX`, `vcs.queue_records` also lists `record_dir`, but `_read_change` does not read it. Not reproduced on a branch yet.
