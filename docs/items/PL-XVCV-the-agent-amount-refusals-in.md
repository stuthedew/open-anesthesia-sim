---
id: PL-XVCV
title: The agent-amount refusals in AlveolarCompartment, TissueGroup and VenousBloodCompartment ('agent_amount_l exceeds the tissue capacity for a concentration fraction of 1', 'exceeds venous blood capacity') name neither the value, the capacity nor the docs/MODEL.md section, where require_room_for_the_agent_held refuses the same relation from the other side naming all three; and a vaporizer maximum written under the dial is refused in the dial's words ('8% requested'), so a refusal can name the field that was not written (found reviewing PL-19Y0)
priority: P2
effort: M
status: done
classes: defect, ux
milestone: v0.6.0
touches: src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/validation.py, tests/unit/test_alveolar.py, tests/unit/test_blood.py, tests/unit/test_tissue.py, tests/unit/test_validation.py, src/anesthesia_sim/core/circuit.py, tests/unit/test_circuit.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
closed: 2026-10-19
pr: 1676
payoff: a refused agent amount or vaporizer maximum names the value, the limit and where to read why, so a reader can trace the refusal to the input that caused it
verify: grep -q 'is more than the 4.0 L the test tissue holds at a' tests/unit/test_tissue.py && grep -q 'is below the 2% the dial is set to' tests/unit/test_circuit.py
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

**Checked 2026-10-19, and fixed on `claude/core-guard-defects-u39w8s`.** Still
real on `main` at `6fd84bd5`. Each agent-amount refusal now goes through
`core/validation.py`'s `require_within_the_capacity`, which names the amount,
the capacity and the `docs/MODEL.md` section, as the room guard does from the
other side. The circuit's `set_agent_amount` refused the same relation in the
same bare words, so it uses the guard too. A vaporizer maximum lowered under
the dial on a built circuit is refused in the maximum's words, for example
"max_delivered_concentration_percent of 1% is below the 2% the dial is set
to". The first write of a maximum, in a constructor, `replace`, a copy or a
pickle, still meets a dial written just beside it and is refused in the
dial's words, which name both values. The `verify:` greps two of the new
anchored messages, since the work reworded existing tests rather than adding
one under a new name.
