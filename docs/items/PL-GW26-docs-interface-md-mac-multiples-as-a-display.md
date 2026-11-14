---
id: PL-GW26
title: docs/INTERFACE.md § "MAC multiples as a display unit" has two wrong statements: the 1.39x rescale it gives for a desflurane against a sevoflurane wash-in is the isoflurane against desflurane figure (desflurane against sevoflurane is 4.00/3.00 = 1.33x), and "which a ceiling of 2 could not do" says a 2 x MAC ceiling would put the 1 MAC line on the frame, when it puts it at half height
priority: P2
effort: S
status: done
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md, docs/INTERFACE.md
added: 2026-11-04
closed: 2026-11-14
pr: 2158
payoff: the MAC axis's ceiling of 3 is defended by a true reason, so no later session lowers it to 2 on the strength of a false one
verify: ! grep -qF 'which a ceiling of 2 could not do' docs/INTERFACE.md
---

**Problem.** `docs/INTERFACE.md` § "MAC multiples as a display unit" makes two wrong statements. It gives 1.39x as the rescale for a desflurane against a sevoflurane wash-in, but 1.39x is the isoflurane against desflurane figure. Desflurane against sevoflurane is 4.00/3.00 = 1.33x. Its clause "which a ceiling of 2 could not do" says that a 2 x MAC ceiling would put the 1 MAC line on the frame, when that ceiling puts the line at half height.

**Checked 2026-11-04.** The copy editor found both while it was being debugged under `PL-HGZS`, and queried them rather than changing them. The section's own `derived:` comments compute 1.39 from isoflurane's and desflurane's values (4.17 / 3.00). `PL-CC23`'s table gives the three pre-`PL-CC23` axis tops as 3.00 (desflurane), 4.17 (isoflurane) and 4.00 (sevoflurane) x MAC. So either the 1.39x sentence should name isoflurane, or its figure should be 1.33x. `PL-CC23`'s table puts the 1 MAC line at 50% of the plot height under a 2.0 x MAC ceiling, inside the plot. The clause "which a ceiling of 2 could not do" probably belongs to the next sentence, about keeping the 2-3x MAC overpressure range on the plot, which a 2 x MAC ceiling cannot do. Both sentences are history and rationale, not displayed values. The fix belongs with the section's rewrite, `PL-PS5H`.

**Checked 2026-11-09:** On cfd4a4b6, `grep -n '1\.39\|ceiling of 2' docs/MODEL.md` shows that the restructure (`PL-BSMF`, #2054) removed the 1.39x rescale sentence from § "MAC multiples as a display unit". The second error is still there: "The ceiling puts the 1 MAC line at a third of the plot height, inside the plot rather than on its frame, which a ceiling of 2 could not do." A 2 x MAC ceiling would put the 1 MAC line at half height, which is also inside the plot. The same paragraph's next sentence gives the reason a ceiling of 2 fails, which is that the 2-3 x MAC range used in overpressure induction would leave the plot. `PL-PS5H`, the section's rewrite, closed without this fix, so this item carries it.

**Why it matters.** This paragraph gives the reason the MAC axis stops at 3 x MAC. A reason that is false invites a later session to lower the ceiling to 2, because the stated objection to 2 does not hold. The objection that does hold, keeping the overpressure range on the plot, is in the next sentence.

**Done when.** The clause "which a ceiling of 2 could not do" is removed from the sentence about the 1 MAC line, or attached to the overpressure-range sentence that it belongs to. The paragraph then gives a true reason for not choosing a ceiling of 2.

**Generator check.** One-off: a finding the copy editor raised as a query while it was being debugged. It is a wrong statement of chart arithmetic in prose, and no head's `misread:` states that fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/INTERFACE.md` § "MAC multiples as a display unit" already said the 3 x MAC ceiling puts the 1 MAC line "inside the plot rather than on its frame, which a ceiling of 2" could not do, and it also carried the 1.39x rescale sentence. The problem belongs on v0.7.0's frozen list, and the deferral is removed.

**Done 2026-11-14.** The clause "which a ceiling of 2 could not do" is removed from the sentence about the 1 MAC line, and the next sentence now opens "Unlike a ceiling of 2", so the reason given against a ceiling of 2 is the overpressure range, which is true. No value, test or displayed text changed. Docs swept: `docs/INTERFACE.md` (the only file that held the clause, by `grep -n 'ceiling of 2'`) and `docs/MODEL.md` (no 1.39x rescale sentence and no "ceiling of 2" clause remain).
