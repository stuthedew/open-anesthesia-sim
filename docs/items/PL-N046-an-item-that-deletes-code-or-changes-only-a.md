---
id: PL-N046
title: An item that deletes code or changes only a document keeps one grep -qF or ! grep -qF condition, checked once when it closes and not replayed afterwards
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** An item that deletes code or changes only a document keeps one grep -qF or ! grep -qF condition, checked once when it closes and not replayed afterwards

**Why it matters.** The project owner chose this form on 2026-11-21 (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). Of the 794 `grep` conditions that name no test, 407 check a document and 79 more check only that code text is gone. A sentence in a developer document that restates a fact of the tree takes the form agreed under `PL-WKKH`: the requirement, then the test that checks it. Checking once at close ends the faults of `PL-RR1N` (a phrase split by line-wrapping) and `PL-205P` (a condition that read the remote), which both came from the replay running a condition long after the work.
