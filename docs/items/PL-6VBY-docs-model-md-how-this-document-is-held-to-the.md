---
id: PL-6VBY
title: docs/MODEL.md § 'How this document is held to the tree' says in its note for developers that check_gate_counts applies clause 3, the declared-none form, but that check holds the counts a frozen list states about itself and calls a frozen count a dated fact, which is the Counts rule and clause 4; the copy editor flagged the clause number in three runs on 2026-11-04 (PL-HGZS)
status: done
touches: docs/MODEL.md
added: 2026-11-04
closed: 2026-11-05
pr: 2040
verify: ! grep -qF 'applies the fixed' docs/MODEL.md && grep -qF 'applies the rule on' docs/MODEL.md
---

**Problem.** The note for developers in `docs/MODEL.md` § "How this document is held to the tree" says that `check_gate_counts` applies clause 3, the declared-none form. That check applies the Counts rule and clause 4: it enforces the counts that a frozen list states about itself, and it calls a frozen count a dated fact. The copy editor flagged the clause number in three runs on 2026-11-04 (`PL-HGZS`).

**Generator check.** One wrong cross-reference, written by hand; the copy editor's instructions now tell it to query a statement the file contradicts (`PL-HGZS`), which is how this one was found. No mechanism to fix beyond that.

**Fixed 2026-11-05, with `PL-HRPK`.** The section's clauses are no longer numbered after `PL-HRPK`'s rewrite. The sentence now says that `check_gate_counts` applies the rule on counts: it checks each count a frozen list states about itself, in a group heading or a release table, against the list, and leaves a count in prose alone as a dated fact. That matches the function's docstring in `tools/doc_check.py`.
