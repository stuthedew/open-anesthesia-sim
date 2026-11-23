---
id: PL-FSXD
title: The wash-in plot gives no ratio for an inspired concentration that the Circuit readout shows as 0.01%, the value the interface document names as the limit
status: untriaged
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/wash_in.py, docs/INTERFACE.md
added: 2026-11-23
filed-pr: 2294
---

**Problem.** `read_wash_in` in `src/anesthesia_sim/app/wash_in.py` gives no ratio while the inspired fraction is below 1e-4, and `docs/INTERFACE.md` § "A point is drawn only inside two boundaries" calls that 0.01% limit "the smallest step of the concentration display". But `format_percent` in `src/anesthesia_sim/app/formatting.py` rounds to 0.01 percentage points and shows `<0.01%` only for a value that rounds to 0.00%. An inspired fraction from 5e-5 up to 1e-4 is therefore shown as "0.01%" in the Circuit readout (checked 2026-11-23: 5e-5, 7e-5 and 9.9e-5 all give "0.01%", and 4e-5 gives "<0.01%"). In that band the readout shows the very value the document names as the limit, while the caption beside the plot says "Not defined: the inspired concentration is too low to divide by." At another moment the same "0.01%" reading, from a fraction of 1e-4 or more, gives a drawn ratio. A washout passes through the band, and in a low-flow washout it can stay there for minutes.

Both blind review passes of `PL-P3ZL` found it on 2026-11-23. It is older than `PL-P3ZL`: the caption before that change said that no agent had reached the circuit, beside the same "0.01%".

**What to do.** Make the readout and the plot agree about which inspired concentrations the ratio is formed from. Research how a monitor or a display standard aligns a limit with a rounded readout, and record the sources here. Candidates are to test the limit against the value as the readout rounds it, to raise the limit to where the readout shows 0.02%, or to keep the limit and have the caption state it. Each changes when a learner sees a ratio, so if the research does not settle it, put the choice to the project owner with a recommendation.
