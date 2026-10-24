---
id: PL-Q3G9
title: app/dashboard_frame.py's PARAMETER_CONTROLS types the unit L/min for fresh gas flow, alveolar ventilation and cardiac output, which app/control_record.py's CONTROL_INPUT_UNITS already holds, so a change to a control's unit in one leaves the panel label or the recorded unit wrong in the other
status: untriaged
feature: one-source-of-truth
added: 2026-10-24
---

**Problem.** app/dashboard_frame.py's PARAMETER_CONTROLS types the unit L/min for fresh gas flow, alveolar ventilation and cardiac output, which app/control_record.py's CONTROL_INPUT_UNITS already holds, so a change to a control's unit in one leaves the panel label or the recorded unit wrong in the other

**Found 2026-10-24** on `main` at `345e8bb2`, while answering the owner's question about how complete `PL-K88Z`'s inventory was. `CONTROL_INPUT_UNITS` in `app/control_record.py` maps each `ControlInput` to the unit its value is recorded in. `PARAMETER_CONTROLS` in `app/dashboard_frame.py` builds the four control rows and types `"L/min"` again for the three flow controls. The delivered concentration differs on purpose: the record holds "percent of 1 atm" and the panel shows "%", and the comment above `CONTROL_INPUT_UNITS` says why. So the fix is not simply to read one map from the other. Someone has to decide whether the panel's unit and the recorded unit are one fact or two. If they are one fact for the flows, the panel should read them from the record. If they are two facts, each needs a name that says which one it is.

**Why it matters.** A unit shown beside a control is part of the displayed value under the safety-critical standard. A wrong unit beside a correct number is still a safety failure. Today the two copies agree, and no test or check would notice if one of them changed.
