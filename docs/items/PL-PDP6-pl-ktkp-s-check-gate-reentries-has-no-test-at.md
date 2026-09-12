---
id: PL-PDP6
title: PL-KTKP's check_gate_reentries has no test at all and its verify: only greps that the def exists, so the check built to stop a silent wrong answer is itself unverified
priority: P2
effort: S
status: ready
classes: defect, test, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-08
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_an_item_re_entering_a_frozen_gate_list_is_reported' tests/unit/test_doc_check.py
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
