---
id: PL-4YJK
title: Record what a manual generator sweep costs, so the fix-or-retire decision on tools/generator_check.py rests on a number rather than on the 0-for-8 record alone
priority: P3
effort: S
status: ready
classes: infra, session-cost
feature: generator-identification
touches: docs/WORKING_NOTES.md, docs/items
added: 2026-09-19
verify: grep -q 'manual generator sweep cost' docs/WORKING_NOTES.md
---

**Problem.** Record what a manual generator sweep costs, so the fix-or-retire decision on tools/generator_check.py rests on a number rather than on the 0-for-8 record alone

**Where it comes from.** `PL-LSR0` (the detector cannot see a store-drift
generator) establishes that `tools/generator_check.py` is 0-for-8: every
generator head this store carries came from a manual sweep instead. That number
alone cannot decide whether to fix the detector, narrow its stated scope, or
retire it — the missing half is what the sweeps it would replace actually cost.

**The numbers exist and are not written down anywhere the store can read.** The
two workflow-lane sweeps run on 2026-09-19 are reported by the session harness
as 456,600 tokens / $99.73 (the sweep that produced `PL-G424`) and 383,270
tokens / $95.34. Those figures live in a session list that is cleared when a
session is archived, so within days the only surviving evidence of what
generator identification costs will be gone.

**What this item is.** Record the per-sweep cost — tokens, dollars, items
examined, generators found — for the sweeps already run, in
`docs/WORKING_NOTES.md` under a heading naming the manual generator sweep cost,
and state the rule for recording the next one. Then `PL-LSR0`'s decision has
both halves of its trade.

**Why it is `S` and not larger.** The measurement is a read of the session
list plus three lines of prose. Nothing has to be built, and the judgment —
whether the cost justifies automating the sweep away — belongs to `PL-LSR0`.

**Scope note.** This feeds `PL-04KR` (the pre-registered apparatus-convergence
baseline) but does not depend on it: `PL-04KR` tracks whether apparatus inflow
is declining, where this records what one diagnostic pass costs. Keep them
separate.

**Why it matters.** `PL-LSR0`'s decision is a trade between a detector's
0-for-8 record and the cost of the manual sweeps that replaced it, and only one
side of that trade currently carries a number. `.claude/rules/expert-review.md`
names this exact failure — when one side of a trade is quantified and the other
is not, the numbered side wins on fluency rather than on merit — and the
unnumbered side here is the one arguing to keep the tool. The cost figures are
also perishable: they sit in a session list that clears on archive.

**Done when.** `docs/WORKING_NOTES.md` carries a heading naming the manual
generator sweep cost, with the per-sweep tokens, dollars, items examined and
generators found for the 2026-09-19 sweeps, and one line stating how the next
sweep's cost gets recorded.
