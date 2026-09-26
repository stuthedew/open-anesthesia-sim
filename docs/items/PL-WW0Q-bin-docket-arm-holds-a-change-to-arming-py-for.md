---
id: PL-WW0Q
title: bin/docket arm holds a change to arming.py for a read but arms one to what its answer is read through - vcs.changed_path_args and default_base, claims.holdings, cli.cmd_arm and the test_arm_ tests - so the gate can still be loosened unread from beside it
status: untriaged
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py
added: 2026-09-25
---

**Problem.** bin/docket arm holds a change to arming.py for a read but arms one to what its answer is read through - vcs.changed_path_args and default_base, claims.holdings, cli.cmd_arm and the test_arm_ tests - so the gate can still be loosened unread from beside it

**Found** building `PL-K6B2`, whose brief excepts `arming.py` alone, as `PL-SQTR`'s recommendation 2 worded it. Everything else under `subprojects/docket/` arms on green, the tests that pin `arm`'s answers included, so a change to `vcs.changed_path_args` that reads fewer paths, with its test edited to match, would merge unread and make every later answer `arm`. The existing guards are `verify --self`'s "no existing assertion removed" and a session's reluctance to weaken a test, neither of which a hold is.
