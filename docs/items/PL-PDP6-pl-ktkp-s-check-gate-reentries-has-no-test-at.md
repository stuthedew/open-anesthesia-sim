---
id: PL-PDP6
title: PL-KTKP's check_gate_reentries has no test at all and its verify: only greps that the def exists, so the check built to stop a silent wrong answer is itself unverified
priority: P2
effort: S
status: dropped
classes: defect, test, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-08
closed: 2026-09-12
reason: Already covered. check_gate_reentries has six tests in tests/unit/test_doc_check.py - a safety item the list does not place, a science item it does, one in Required scope, a closed one, one of another class, and the grouping of several into one advisory. They reach the function through doc_check.analyze rather than calling it by name, which is why a grep for 'check_gate_reentries' under tests/ finds only a comment and reads as no coverage; that comment is corrected in the same change. Verified 2026-09-12 by neutering the function, on which two of the six fail. PL-KTKP's own verify: command is still a weak one, but it is a closed item's record and the skill forbids re-pointing it.
---

**Problem.** PL-KTKP's check_gate_reentries has no test at all and its verify: only greps that the def exists, so the check built to stop a silent wrong answer is itself unverified

**Why it matters.** `check_gate_reentries` exists to stop a silent wrong answer
- an item re-entering a frozen gate list without being noticed - and it is
itself the only check in `tools/doc_check.py` with no test. Its `verify:`
command greps that the `def` exists, which is satisfied by an empty function
body, so nothing in the tree distinguishes the check working from the check
returning immediately. That is the shape `PL-20PT` was fixed for one file over:
a guard that reports PASS because it never looked.

`tests/unit/test_doc_check.py` already carries a comment naming this gap, so it
was known at the time and deferred rather than missed.

**Done when.** `check_gate_reentries` has tests that fail if its body is
removed - at minimum one re-entry it must report and one legitimate case it must
not - and its `verify:` command names one of them instead of grepping for the
`def`.
