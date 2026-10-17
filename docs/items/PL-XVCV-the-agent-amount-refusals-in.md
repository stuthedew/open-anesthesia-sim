---
id: PL-XVCV
title: The agent-amount refusals in AlveolarCompartment, TissueGroup and VenousBloodCompartment ('agent_amount_l exceeds the tissue capacity for a concentration fraction of 1', 'exceeds venous blood capacity') name neither the value, the capacity nor the docs/MODEL.md section, where require_room_for_the_agent_held refuses the same relation from the other side naming all three; and a vaporizer maximum written under the dial is refused in the dial's words ('8% requested'), so a refusal can name the field that was not written (found reviewing PL-19Y0)
priority: P2
effort: M
status: ready
classes: defect, ux
touches: src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/validation.py, tests/unit/test_alveolar.py, tests/unit/test_blood.py, tests/unit/test_tissue.py, tests/unit/test_validation.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
payoff: a refused agent amount or vaporizer maximum names the value, the limit and where to read why, so a reader can trace the refusal to the input that caused it
verify: grep -q 'def test_the_agent_amount_refusal_names_the_amount_and_the_capacity' tests/unit/test_tissue.py
---

**Problem.** The agent-amount refusals in AlveolarCompartment, TissueGroup and VenousBloodCompartment ('agent_amount_l exceeds the tissue capacity for a concentration fraction of 1', 'exceeds venous blood capacity') name neither the value, the capacity nor the docs/MODEL.md section, where require_room_for_the_agent_held refuses the same relation from the other side naming all three; and a vaporizer maximum written under the dial is refused in the dial's words ('8% requested'), so a refusal can name the field that was not written (found reviewing PL-19Y0)

**Checked 2026-10-17.** The three messages are in `core/alveolar.py`,
`core/blood.py` and `core/tissue.py`, at the `agent_amount_l` write. The
vaporizer message is `core/validation.py`'s
"{name} exceeds the vaporizer maximum (X% requested, Y% maximum)", which reads
"requested" even when the write that failed was the maximum.

**Why it matters.** `.claude/rules/sources-and-docstrings.md` says a refusal
names the value that failed and where to read why. These name neither, so a
reader cannot trace the refusal to the input that caused it, and one names a
field that was not written.

**Done when.** Each agent-amount refusal names the amount, the capacity and the
`docs/MODEL.md` section, as `require_room_for_the_agent_held` does. A maximum
written below the dial is refused in words that name the maximum as the value
written. Tests pin each message whole.
