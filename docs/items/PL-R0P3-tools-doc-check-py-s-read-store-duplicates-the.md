---
id: PL-R0P3
title: tools/doc_check.py's _read_store duplicates the config-and-store read that check_gate_reentries and check_gate_dispositions each spell inline, so three spellings of one question can disagree
priority: P3
effort: S
status: ready
classes: refactor
feature: doc-consistency-checks
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_doc_check.py && [ "$(grep -c 'def _read_store' tools/doc_check.py)" = 1 ] && [ "$(grep -c '_read_store(root)' tools/doc_check.py)" -ge 3 ]
---


**Problem.** tools/doc_check.py's _read_store duplicates the config-and-store read that check_gate_reentries and check_gate_dispositions each spell inline, so three spellings of one question can disagree

**Verified 2026-09-14.** `tools/doc_check.py:1434` defines `_read_store` and
`:1528` is its only caller; `check_gate_reentries` (`:1781`) and
`check_gate_dispositions` (`:1911`) each read the config and the store inline
rather than through it, so one question has three spellings.

**Why it matters.** Three spellings of "read the queue" can disagree about which
items exist, and the two that bypass the helper are the two that decide gate
membership - whether an item re-entered a frozen gate, and whether its
disposition is recorded. A disagreement there is silent: each check answers
confidently from its own reading. This is a maintainability finding rather than
a live defect - no divergence is known today - which is why it sits at P3.

**Done when.** `check_gate_reentries` and `check_gate_dispositions` read the
store through `_read_store`, there is one spelling of the config-and-store read
in `tools/doc_check.py`, and `tests/unit/test_doc_check.py` still passes.
