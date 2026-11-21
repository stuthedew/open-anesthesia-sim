---
id: PL-QTZG
title: Remove the verify: shape rules and the replay's reading of commands once items no longer carry them, about 1,640 lines of docket code with their tests
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** Remove the verify: shape rules and the replay's reading of commands once items no longer carry them, about 1,640 lines of docket code with their tests

**Why it matters.** The project owner chose on 2026-11-21 that no item's done-condition is replayed after it closes (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). That leaves the shape rules in `checks.py`, the command reading in `verify.py` and `grep.py`, and `bin/docket check --verify` with nothing to read. `PL-LY24` counted 9 episodes in which that replay caught a real mistake, all before 2026-09-23, and recommended retiring it with the commands; `PL-KGPR` (which of the 13 workflow-record checks to retire) holds that decision. `subprojects/docket/src/docket/shell.py` stays, because the Bash guard hooks and `tools/doc_check.py` read commands with it. This work comes after `PL-FN11`, `PL-N046` and `PL-NY7Q`.
