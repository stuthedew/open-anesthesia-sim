---
id: PL-SY7G
title: Sort the interface document by reader after the split: move or cut each paragraph the reverse outline gives another home, and apply the structure findings for its sections (stage 3 of the split PL-P3GZ decided)
priority: P2
effort: L
status: blocked
classes: docs
feature: model-md-structure
touches: docs/MODEL.md
blocked-by: PL-48MX
added: 2026-11-11
payoff: each paragraph of the document is for its reader, and none restates what a docstring, a test or an item already says
---

**Problem.** Sort the interface document by reader after the split: move or cut each paragraph the reverse outline gives another home, and apply the structure findings for its sections (stage 3 of the split PL-P3GZ decided)

**Why it matters.** The project owner decided on 2026-11-11 to split
`docs/MODEL.md` by reader (`PL-P3GZ`). Stage 1 moves whole sections word for
word, so the interface document starts with every paragraph its sections held, whoever the
paragraph is for. The reverse outline
(`docs/prose-review/model-reverse-outline.tsv`, `PL-9RLM`) gives each
paragraph a best home. Those sections hold 59,940 words. § "Minimum displayed outputs" alone held 33,567 on 2026-11-10, of which the outline gives 1,856 to a model description.

**What to do.**

1. For each paragraph of the seven interface sections that `PL-CTXZ` moves that the outline gives another home,
   have a reader confirm the label, then move the paragraph there. The
   labels are one model's judgement with no second rater. The outline's
   line numbers are those of `docs/MODEL.md` at `50af1a2e`.
2. Cut a paragraph that restates a docstring, a test or an item only after
   confirming that the home holds the fact. Decision history goes to the
   item that took the decision, and planned work to `ROADMAP.md`.
3. Apply, for these sections, the structure findings of `PL-YKKC` (the
   second reverse outline) and `PL-1VXY` (the chapter reads of 2026-11-05),
   and fix any pointer of `PL-52KB` (five broken section pointers) that is
   still broken in them. The session that applies the last of `PL-1VXY`'s
   findings across the three stage 3 items closes `PL-1VXY`.
4. Re-point each citation of a heading that changes.

**What it must not do.** Change no value, unit, equation, condition or
citation. Set no word target (`PL-J1ZM`). `PL-P3GZ` decided that no table is
generated and that requirements keep their headings and get no numbers. If
this work finds a table that neither the provenance check nor the named-test
check holds, reopen that call there.

**What ends with it.** The owner's hold of 2026-11-10 on within-section
restructuring ends for this document when this item closes. The hold also
covered copy editor runs, and the copy editor was removed on 2026-11-14
(`PL-GL45`).

**Done when.** Each paragraph of the interface document is for its reader or has moved to
its home, no paragraph restates a docstring, a test or an item, the
findings named in step 3 are applied for these sections, and `make check`
passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.
