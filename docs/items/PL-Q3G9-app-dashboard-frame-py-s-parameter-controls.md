---
id: PL-Q3G9
title: app/dashboard_frame.py's PARAMETER_CONTROLS types the unit L/min for fresh gas flow, alveolar ventilation and cardiac output, which app/control_record.py's CONTROL_INPUT_UNITS already holds, so a change to a control's unit in one leaves the panel label or the recorded unit wrong in the other
priority: P1
effort: S
status: ready
classes: safety, defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/control_record.py, tests/unit/test_dashboard_frame.py
added: 2026-10-24
payoff: the unit beside a flow control and the unit its value is recorded in come from one place
verify: ! grep -q '"L/min"' src/anesthesia_sim/app/dashboard_frame.py
---

**Problem.** app/dashboard_frame.py's PARAMETER_CONTROLS types the unit L/min for fresh gas flow, alveolar ventilation and cardiac output, which app/control_record.py's CONTROL_INPUT_UNITS already holds, so a change to a control's unit in one leaves the panel label or the recorded unit wrong in the other

**Found 2026-10-24** on `main` at `345e8bb2`, while answering the owner's question about how complete `PL-K88Z`'s inventory was. `CONTROL_INPUT_UNITS` in `app/control_record.py` maps each `ControlInput` to the unit its value is recorded in. `PARAMETER_CONTROLS` in `app/dashboard_frame.py` builds the four control rows and types `"L/min"` again for the three flow controls. The delivered concentration differs on purpose: the record holds "percent of 1 atm" and the panel shows "%", and the comment above `CONTROL_INPUT_UNITS` says why. So the fix is not simply to read one map from the other. Someone has to decide whether the panel's unit and the recorded unit are one fact or two. If they are one fact for the flows, the panel should read them from the record. If they are two facts, each needs a name that says which one it is.

**Why it matters.** A unit shown beside a control is part of the displayed value under the safety-critical standard. A wrong unit beside a correct number is still a safety failure. Today the two copies agree, and no test or check would notice if one of them changed.

**Decision needed.** Are the panel's unit and the recorded unit one fact or two?

**Recommendation:** one fact, the unit, held once in `CONTROL_INPUT_UNITS`. The panel's label is then a display form of that unit, made by one function: "percent of 1 atm" is shown as "%", and "L/min" is shown as itself. That keeps the concentration's difference, which the comment above `CONTROL_INPUT_UNITS` explains, without a second copy of any unit. If `PL-G84G` adopts a unit type that carries its label, this item is that type's first use. It is a structure choice inside one module pair, so the session that starts the item can take it.

**Done when** (under the recommendation). `PARAMETER_CONTROLS` reads each control's unit from `CONTROL_INPUT_UNITS` through one display function. A test shows that changing a control's recorded unit changes the panel label too.

**Checked 2026-10-24.** `dashboard_frame.py` types `"L/min"` for fresh gas flow, alveolar ventilation and cardiac output, and `control_record.py`'s `CONTROL_INPUT_UNITS` holds the same three.

**Decided 2026-10-25: one fact, held once.** This is the recommendation above. `PL-G84G` decided on the same day to add a unit type that carries its label, in `app/`, so this item is that type's first use and is built in the same pull request. `CONTROL_INPUT_UNITS` maps each control to a member of the type, and `PARAMETER_CONTROLS` reads each control's label from that member. The delivered concentration's member records "percent of 1 atm" and shows "%", which keeps the difference the comment above `CONTROL_INPUT_UNITS` explains.
