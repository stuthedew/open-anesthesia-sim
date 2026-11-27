---
id: PL-KQ0S
title: The share caption says the shares are of all the agent in the circuit and body, but the model leaves out lung tissue and pulmonary blood, a vessel-poor group and absorption by the circuit's plastics, so the whole is the six drawn compartments rather than all the agent in a real patient
status: untriaged
added: 2026-11-27
---

**Problem.** The share caption says the shares are of all the agent in the circuit and body, but the model leaves out lung tissue and pulmonary blood, a vessel-poor group and absorption by the circuit's plastics, so the whole is the six drawn compartments rather than all the agent in a real patient

**Why it matters.** The caption under the containers reads "Shares are of all
the agent in the circuit and body at this instant." The share is computed over
the model's six compartments: the circuit, the alveoli, venous blood, the
vessel-rich group, muscle and fat. `docs/MODEL.md` § "What the model does not
represent" lists three stores the model leaves out: lung tissue and pulmonary
blood, a vessel-poor tissue group, and absorption by the circuit's plastics and
rubber. § "Lung tissue and pulmonary blood" puts the first at about a fifth of
the fast pool, which is the alveolar gas, the venous blood and the vessel-rich
group. A clinician can read "body" as a real patient's body, and the caption
then claims a completeness the model does not have. The View's heading does
say "Model outputs — not measurements."

**Decision needed.** Which wording should the caption use?

1. Keep "Shares are of all the agent in the circuit and body at this
   instant", the wording in the mock-up approved on 2026-11-27.
2. **Recommended:** "Shares are of all the agent in the six containers at
   this instant." It states exactly what is computed and points at what is
   drawn. The circuit is one of the six containers, so it is still in the
   whole, and the instant is still named.

This changes the label of a displayed value, so it is the owner's call
(`tests/integration/test_interface_wording.py`'s docstring). The no-agent
line, "No shares yet: the circuit and body hold no agent.", would change to
match: "No shares yet: the six containers hold no agent."

**Done when** the caption and the no-agent line read as decided, the approved
wording list is rewritten, and `docs/INTERFACE.md` § "The compartment
schematic: what its heights, amounts and share bar assert" says what the share
is of in the same words.
