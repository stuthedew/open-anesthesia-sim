---
id: PL-KQ0S
title: The share caption says the shares are of all the agent in the circuit and body, but the model leaves out lung tissue and pulmonary blood, a vessel-poor group and absorption by the circuit's plastics, so the whole is the six drawn compartments rather than all the agent in a real patient
priority: P1
effort: S
status: done
classes: defect, safety
feature: schematic
touches: src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/qt_schematic.py, docs/INTERFACE.md, ROADMAP.md, tests/integration/approved_interface_strings.json
deferred-from: v0.7.0 - filed on 2026-11-27 by PL-8PL4's code review, after the gate froze; it lands in PL-8PL4's pull request so that v0.7.0 does not ship the caption's claim
added: 2026-11-27
closed: 2026-11-27
pr: 2326
payoff: a learner reads the shares as fractions of the agent in the six drawn containers, not of all the agent in a real patient's body
tests: tests/unit/test_compartment_schematic.py::test_the_share_caption_says_the_shares_are_of_the_agent_held_at_this_instant, tests/unit/test_compartment_schematic.py::test_a_run_that_holds_no_agent_prints_no_share_and_says_why
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

The no-agent line, "No shares yet: the circuit and body hold no agent.",
changes to match: "No shares yet: the six containers hold no agent."

**Decided 2026-11-27: option 2, by this session.** Option 1 claims a
completeness the model does not have, which the safety-critical standard
refuses, so only option 2 is defensible. Among wordings that say what is
computed, the choice is wording, which `.claude/rules/instruction-writing.md`
rule 14 makes the session's. The coordinator relayed the owner's standing
instruction to take that call rather than put it to him. The first draft of
this brief called it the owner's, because the wording test's docstring sends a
change to a clinical value's label to the owner. That rule is there so that a
clinician checks a label that changes what a value means. Here the value and
its formula do not change. `docs/INTERFACE.md` already defines the share as a
fraction of the stored agent, the sum of the six compartments, and the new
caption says exactly that. So the pull request records that no read from the
owner is needed, and says why.

**Generator check.** No generator. The caption was written for the single
bar (`PL-S79P`) and named the whole in everyday words. The one other text
that shows this total, the accounting panel, calls it "Stored" and says
nothing about where the agent is held.

**Done when** the caption and the no-agent line read as decided, the approved
wording list is rewritten, and `docs/INTERFACE.md` § "The compartment
schematic: what its heights, amounts and share bar assert" says what the share
is of in the same words.

**Regression tests, run against the old caption on 2026-11-27.**
`uv run pytest -q tests/unit/test_compartment_schematic.py -k "share_caption_says
or holds_no_agent_prints"`, with `app/compartment_schematic.py` as it was before
the fix, failed both: `assert 'in the six containers at this instant' in 'Shares
are of all the agent in the circuit and body at this instant.'` and `assert 'the
six containers hold no agent' in 'No shares yet: the circuit and body hold no
agent.'`.

**Docs checked 2026-11-27.** `docs/INTERFACE.md` (the schematic section's share
paragraph), `ROADMAP.md` (v0.7.0's scope entry 4 and its definition of done),
`docs/VERIFICATION.md` (the hazard row on reading a height as an amount, which
says "its share of all the agent" and needs no change), `docs/MODEL.md` (§ "What
the model does not represent", which the new comment cites),
`src/anesthesia_sim/data/workspaces/__init__.py` (the Maintenance Workspace,
which says "its share of all the agent"), and the docstrings in
`app/compartment_schematic.py`, `app/qt_schematic.py` and `app/controller.py`.
`app/controller.py` describes `stored_agent_l` as all the agent that "the
circuit and the patient" hold, which a developer reads as the model's patient,
so it is unchanged.
