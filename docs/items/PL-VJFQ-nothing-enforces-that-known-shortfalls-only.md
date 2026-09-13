---
id: PL-VJFQ
title: Nothing enforces that KNOWN_SHORTFALLS only shrinks, so the contrast ledger could become the suppression list ui-color.md forbids in prose
priority: P2
effort: S
status: needs-decision
classes: defect, infra
touches: tools/contrast_check.py, .claude/rules/ui-color.md, tests/unit/test_contrast_check.py
added: 2026-09-13
---

**Problem.** Nothing enforces that KNOWN_SHORTFALLS only shrinks, so the contrast ledger could become the suppression list ui-color.md forbids in prose

**Why it matters.** `.claude/rules/ui-color.md` gives `KNOWN_SHORTFALLS` two
jobs and forbids a third use in prose: an entry may not be added to make a
change go green. Nothing checks that. The ledger is the one structure in the
tree whose whole purpose is to hold a failing measurement without failing, so
it is also the one place where a colour change can be waved through by editing
a list rather than a colour.

`PL-MHQK` is where this surfaced, and it is the inverse of that item's
finding. That item asked whether the block prints too often; the answer was no,
*because the list is shrinking* - three entries when it was written, one today,
`PL-GNN1` and `PL-GVXP` having closed. The decision to leave the printing alone
rests on that direction continuing, and the direction is exactly what nothing
enforces.

**Where.** `tools/contrast_check.py`, `KNOWN_SHORTFALLS` and `format_report`;
`.claude/rules/ui-color.md`, the paragraph forbidding an entry added to go
green.

**Decision needed.** Whether a check can express "only shrinks" at all, and
against what baseline. A count compared to a number committed in the file is
the cheap version and is self-defeating - the number is edited in the same
commit as the entry. Comparing against the merge base is the real version and
needs the tool to read a ref, which it does not today and which `PL-MHQK`
declined to add for the printing question. A third option is to leave it to
review and record here that it is deliberate, which is honest only if the
reason is written down where a reviewer of a colour change will read it.

Worth deciding *before* the list next grows rather than after: the first
wrongly-added entry is the one nobody notices.

**Done when.** Either a check enforces the direction against a baseline that
cannot be edited in the same commit as the entry, or the decision to leave it
to review is written into `.claude/rules/ui-color.md` beside the prohibition it
backs, where a reviewer of a colour change will actually read it. Deferring
without recording one of the two is the outcome this item exists to prevent,
so it is not an available ending.
