---
id: PL-26BZ
title: In the Induction Workspace at 1366 by 768 the wash-in View is 271 px of content in a 146 px Area, so 'Modelled, not measured' and the F_A/F_I plot are never on screen together: with the View at its top the plot shows 8 of its 80 px, and scrolled to the plot the line is above the Area; decide whether the plot carries the words itself, such as in its axis title, or the wash-in Area gets room for its whole View
status: untriaged
feature: window-is-the-frame
added: 2026-11-14
---

**Problem.** In the Induction Workspace at 1366 by 768 the wash-in View is 271 px of content in a 146 px Area, so 'Modelled, not measured' and the F_A/F_I plot are never on screen together: with the View at its top the plot shows 8 of its 80 px, and scrolled to the plot the line is above the Area; decide whether the plot carries the words itself, such as in its axis title, or the wash-in Area gets room for its whole View

**Found by** the adversarial review of `PL-CBYS`'s pull request `#2134`, on
2026-11-14, reproduced offscreen. The project owner chose on 2026-11-11 that
Induction's charts stay stacked, and the second mock-up showed the wash-in
Area scrolling about 122 px inside itself at this size. `#2134` moved the
line out of the box that scrolls above the plot, which keeps it in view
wherever the View fits its Area. Where the View is taller than its Area, no
order of rows puts both on screen. The safety standard requires the words
beside the plot (`PL-F9TQ`), so whether a learner may see the plot without
them is the owner's decision.
