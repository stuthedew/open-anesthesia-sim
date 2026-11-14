---
id: PL-KG6S
title: docs/INTERFACE.md § "Displayed precision" bounds the last displayed digit at 'between about a seventh of one parameter SD and seven times it' and calls one SD 'one to seven counts', but its own table's fat tissue:gas row, 8.7e-4 to 6.7e-3 pp, is 0.09 to 0.67 counts, which puts the digit at 1.5 to 11.5 SDs; no row gives the 'seven times' end, so the bound should be restated from the table or limited to the rows it comes from (found by PL-J37P's blind review)
priority: P1
effort: S
status: ready
classes: defect, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, docs/INTERFACE.md
added: 2026-11-04
payoff: a clinician checking why the readouts stop at two decimals finds every ratio in the argument matching the table it cites
verify: ! grep -q -F 'a seventh of one' docs/INTERFACE.md && ! grep -q -F 'a fiftieth' docs/INTERFACE.md
reenters: PL-B6YV
---

**Problem.** docs/INTERFACE.md § "Displayed precision" says the last displayed digit lies between about a seventh of one parameter SD and seven times it, and calls one SD "one to seven counts". Its own table does not support that range. The fat tissue:gas row's figures, 8.7e-4 to 6.7e-3 pp, are 0.09 to 0.67 counts, which puts the digit at 1.5 to 11.5 SDs for that row. No row gives the "seven times" end. The bound should be restated from the table, or limited to the rows it comes from. Found by `PL-J37P`'s blind review.

**Two more ratios in the same section do not follow from their figures** (the second blind review pass on `PL-J37P`, 2026-11-04). The accounting panel's shifts are 0.016 to 0.23 L. They put one 0.1 L count at about 0.43 to 6 SDs, where the section says "a quarter" to six. `PL-SP6H` already holds this one. They also put a 0.01 L count at about a twentieth of an SD at 24 h, where the section says "a fiftieth". The schematic subsection repeats "a fiftieth" as a comparison. None of these errors changes a chosen count, but they are the numbers a reader checks before trusting the argument.

**Read at triage, 2026-11-04**, by arithmetic on the table in `docs/INTERFACE.md`
§ "Displayed precision" at `f369249fa`. One count is 0.01 percentage points.
One SD moves the readout by 0.087 to 0.67 counts for fat, 1.5 to 5.4 for
blood:gas, 1.3 to 5.0 for vessel-rich and 1.3 to 6.8 for muscle. So "one to
seven counts" holds for three rows and not for fat. For those three rows one
count is 0.15 to 0.77 SD. For fat it is 1.5 to 11.5 SD. No row gives "seven
times". A third decimal would be 0.015 to 0.077 SD for the three rows, where
the text says "one seventieth to seven tenths". For the amounts, 0.01 L against
the 24 h shifts of 0.18 to 0.23 L is 0.043 to 0.056 SD, about a twentieth,
where the text says "a fiftieth". The same figures recur near the end of the
section: the readouts' third decimal "was refused at a seventieth of an SD",
and the totals' second decimal "at a fiftieth". Every one of these figures
appears in the text before `PL-J37P`'s rewrite (`53cd01239^`). The two-decimal
count still follows from the three larger rows, so no displayed value changes.

**Why it matters.** This paragraph is where a clinician decides whether to
trust the readouts' two decimals, and the table beside it is what they would
check it against. A reader who checks finds the stated bound wrong at its first
step, and has no way to tell that the conclusion still holds.

**Done when.** The bound, the "one to seven counts" heading, the third-decimal
sentence and the two "a fiftieth" statements are restated from the figures, or
limited to the rows they come from. The "quarter of an SD" for 0.1 L stays with
`PL-SP6H`, which already holds it. If restating them changes the argument for
two decimals, that is a new item rather than this one's work.

**Generator check.** An instance of `PL-B6YV`'s fact, whether a
`docs/MODEL.md` sentence about what the model computes matches what it
computes, filed after that head closed on 2026-11-02. `PL-B6YV` routed this
section's figures to `PL-19W8`'s tests. Those tests hold the table, not the
ratios derived from it.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. The fat row, "one to seven counts" and the seventh-to-seven-times bound were all in `docs/MODEL.md` at `817a4d88`. Only the recap and the schematic's repeats came later (`1f4717f2`). It is not deferred. A first reading deferred it as not live, because the two-decimal count still follows from the table's three larger rows. A review the same day found that premise unsafe. Those rows are the table that `PL-TDX0` says used the wrong SDs, and the tissue:gas SDs the agent files store are much wider: muscle 37% for desflurane (0.94 ± 0.35), 45% for isoflurane (4.40 ± 1.97) and 43% for sevoflurane (2.38 ± 1.03), and fat 17% to 19%. With those SDs, one SD of the muscle row could move the readout by tens of counts, so one count of the second decimal would fall below a seventh of an SD. That is finer than the band the section allows. So the check cannot find the hazard not live, and the item stays on the list beside `PL-TDX0`, whose fix restates the same table.