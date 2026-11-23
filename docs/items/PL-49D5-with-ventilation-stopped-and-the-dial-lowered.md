---
id: PL-49D5
title: With ventilation stopped and the dial lowered, the F_A/F_I trace climbs toward 1 because the circuit washes out, and the plot draws that climb as wash-in ending at equilibrium
status: untriaged
feature: interface-design-review
added: 2026-11-23
filed-pr: 2305
---

**Problem.** With ventilation stopped and the dial lowered, the F_A/F_I trace climbs toward 1 because the circuit washes out, and the plot draws that climb as wash-in ending at equilibrium

**Problem.** Rule 2 in `src/anesthesia_sim/app/wash_in.py`'s module docstring calls every ratio at or below 1 "the uptake regime", and the plot draws it as the textbook wash-in curve. With alveolar ventilation at zero that is not so. In `tests/unit/test_dashboard_frame.py::test_a_ratio_above_one_with_ventilation_stopped_names_no_elimination`, ventilation stops at 600 s of 4% sevoflurane and the dial drops to 0.5%. The ratio then climbs toward 1 because fresh gas washes the circuit out, not because the alveoli fill, and the plot draws that climb as wash-in ending on the equilibrium line.

**Found by** the first blind review pass of `PL-7PBB` on 2026-11-23, as an optional finding outside that item's change.

**What to decide.** Whether the plot should stop drawing, or caption, a ratio below 1 while alveolar ventilation is zero, and what the caption names. The number itself is the true quotient; the question is whether drawing it on the wash-in curve teaches a wash-in that is not happening.
