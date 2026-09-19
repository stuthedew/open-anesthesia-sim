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
verify: uv run pytest tests/unit/test_doc_check.py && [ "$(grep -c 'read_items(root / config.items_dir)' tools/doc_check.py)" = 0 ]
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

---

**`verify:` rewritten 2026-09-19, with the item still open, because CI caught
it passing on work nobody had done.** The old command was

    uv run pytest tests/unit/test_doc_check.py
      && [ "$(grep -c 'def _read_store' tools/doc_check.py)" = 1 ]
      && [ "$(grep -c '_read_store(root)' tools/doc_check.py)" -ge 3 ]

It counted *call sites* of `_read_store` and asked for three, on the reasoning
that the two inline readers converting would take the count from one to three.
Counting is what broke it: the threshold is reached by any three callers,
whoever added them and for whatever reason. On `refs/pull/692/merge` the three
were `check_gate_counts` (the original), `check_bound_families` (a new check
merged to `main` from another branch) and `check_scope_declarations` (added by
`PL-HWW1` on that branch) - and **neither** `check_gate_reentries` nor
`check_gate_dispositions` had been touched, so the command passed while every
line of this item's work was still outstanding. `bin/docket check --verify` is
what reported it, on the pull request rather than on `main`, which is the
window that flag exists for.

The replacement tests the property instead of counting the symptom:

    uv run pytest tests/unit/test_doc_check.py
      && [ "$(grep -c 'read_items(root / config.items_dir)' tools/doc_check.py)" = 0 ]

That spelling appears exactly where this item says it should not - twice today,
at `check_gate_reentries` and `check_gate_dispositions`, and nowhere else,
since `_read_store` reads `read_items(store)` after resolving the path. It goes
to zero only when both are converted, and no unrelated new caller of
`_read_store` can move it. A future check that reads the store inline keeps it
red, which is correct: that would be the fourth spelling this item exists to
prevent. Run before being recorded: exit 1 on this tree, and exit 1 on the
merge ref where the old command wrongly passed.

**The item's own work is untouched** - `status` stays `ready` and the
`Done when.` above is unchanged. Only the thing that would have proved it moved.
The generalisable half is filed as its own finding.