---
id: PL-GW26
title: docs/MODEL.md § "MAC multiples as a display unit" has two wrong statements: the 1.39x rescale it gives for a desflurane against a sevoflurane wash-in is the isoflurane against desflurane figure (desflurane against sevoflurane is 4.00/3.00 = 1.33x), and "which a ceiling of 2 could not do" says a 2 x MAC ceiling would put the 1 MAC line on the frame, when it puts it at half height
status: untriaged
added: 2026-11-04
---

**Problem.** `docs/MODEL.md` § "MAC multiples as a display unit" makes two wrong statements. It gives 1.39x as the rescale for a desflurane against a sevoflurane wash-in, but 1.39x is the isoflurane against desflurane figure. Desflurane against sevoflurane is 4.00/3.00 = 1.33x. Its clause "which a ceiling of 2 could not do" says that a 2 x MAC ceiling would put the 1 MAC line on the frame, when that ceiling puts the line at half height.

**Checked 2026-11-04.** The copy editor found both while it was being debugged under `PL-HGZS`, and queried them rather than changing them. The section's own `derived:` comments compute 1.39 from isoflurane's and desflurane's values (4.17 / 3.00). `PL-CC23`'s table gives the three pre-`PL-CC23` axis tops as 3.00 (desflurane), 4.17 (isoflurane) and 4.00 (sevoflurane) x MAC. So either the 1.39x sentence should name isoflurane, or its figure should be 1.33x. `PL-CC23`'s table puts the 1 MAC line at 50% of the plot height under a 2.0 x MAC ceiling, inside the plot. The clause "which a ceiling of 2 could not do" probably belongs to the next sentence, about keeping the 2-3x MAC overpressure range on the plot, which a 2 x MAC ceiling cannot do. Both sentences are history and rationale, not displayed values. The fix belongs with the section's rewrite, `PL-PS5H`.
