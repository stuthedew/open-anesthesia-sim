---
id: PL-QLNX
title: bin/docket record copies the guard refusal log into docs/hook-blocks/, which the claim check counts as work outside the queue, so a queue-only branch that records its pull request fails CI's claim check
priority: P2
effort: S
status: done
classes: defect
feature: guard-refusal-log
touches: subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_claims.py, subprojects/docket/tests/test_record_command.py, subprojects/docket/README.md, docket.toml, tools/hook_blocks.py, tests/unit/test_hook_blocks.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-04
closed: 2026-11-04
pr: 2009
payoff: a triage or capture branch that records its pull request number passes CI without claiming an item or throwing away the guard refusals it copied
verify: grep -q 'record_dir' subprojects/docket/src/docket/vcs.py && ! grep -q '^BLOCKS_DIR = "' tools/hook_blocks.py
---

**Problem.** bin/docket record copies the guard refusal log into docs/hook-blocks/, which the claim check counts as work outside the queue, so a queue-only branch that records its pull request fails CI's claim check

**Evidence.** Found 2026-11-04 on #1994, a branch that changed only item files. `bin/docket record 1994` ran `docket.toml`'s `record_command`, `python3 tools/hook_blocks.py copy`, which wrote two gate-status-guard refusals to `docs/hook-blocks/claude-burst-generator-eval.tsv`. CI's `checks-part-1` then failed in `tools/branch_id_check.py`: "this branch claims nothing ... It changes files outside the queue". `vcs.queue_records` lists the items directory, the roadmap, the working notes and the pull-request body records as "the records a queue workflow writes". It leaves out the directory that `record`'s own command writes. The check reads each commit, so deleting the file in a later commit did not clear it. The branch had to be folded into one commit, and its two refusals were lost from the repository's count, which `PL-SG93`'s keep-or-retire verdicts read.

**Why it matters.** Any branch that records a pull request number without claiming an item fails CI in the same way, as soon as the session has met a guard refusal. That includes a triage pass that closes an item, or a capture branch. The session then either discards real refusal data or claims an item it does not need.

**Likely fix.** Have `queue_records` include the directory that `record_command` writes, read from one record. For example, add a `docket.toml` key that both `tools/hook_blocks.py` (now the literal `BLOCKS_DIR`) and `queue_records` read. A test should record a pull request on a queue-only branch with a refusal in the local log, and find the claim check still passing.

**Generator check.** One-off. The fact misread is which paths a queue workflow writes. `queue_records` was built to hold that fact in one place (`PL-F6MM`), and `record_command` was added later without updating it. No other open item describes it.

**Done when.** One `docket.toml` key, `record_dir`, names the directory that `record_command` writes. `vcs.queue_records` lists it, so a branch that writes only item files and that directory owes no claim. `tools/hook_blocks.py` reads the same key and no longer spells the path itself. A test records a refusal file on a branch that changes nothing else and finds the claim check passing.
