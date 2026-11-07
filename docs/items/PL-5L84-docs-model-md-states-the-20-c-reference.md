---
id: PL-5L84
title: docs/MODEL.md states the 20 °C reference condition in 29 paragraphs with no marker tying them to core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS, so the numeric-paragraph check cannot read °C as a unit until each is tied
priority: P1
effort: M
status: ready
classes: defect, safety
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tools/doc_check.py
deferred-from: v0.7.0 - not live: checked 2026-11-07 (PL-8C8W): REFERENCE_TEMPERATURE_CELSIUS, the three agent files' 20.0 and the caption "at 20 degrees C" all agree with docs/MODEL.md's 20 °C, so no learner can see a wrong value now
added: 2026-11-03
payoff: a change to the 20 °C reference temperature behind the displayed millilitres of liquid agent cannot land while docs/MODEL.md still states the old value
verify: grep -qF '("_celsius", "°C")' tools/doc_check.py && grep -qF 'provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` states the 20 °C reference condition, behind every displayed millilitres-of-liquid figure, in 29 paragraphs. The value lives in `core/liquid_agent.py` as `REFERENCE_TEMPERATURE_CELSIUS = 20.0`, and in each agent file as `liquid_density.measured_at_celsius = 20.0`. Nothing ties those paragraphs to it, so a change to the reference temperature would leave them stale with no refusal.

**Found by.** Both blind review passes on `PL-XQXK` (#1976). That branch first listed °C as a unit no value is stored in, which would have made "20 °C" unmatchable for good. Reading °C as a stored unit instead raised 29 untied-restatement errors, all this one value. `PL-XQXK` left °C and grams in no unit list, which keeps the reading `main` had: a figure in °C is read as a bare number.

**Reproduced 2026-11-03.** `docs/MODEL.md` holds "20 °C" on 31 lines, in 23 blocks separated by blank lines, and none of those blocks names `REFERENCE_TEMPERATURE_CELSIUS`. `tools/doc_check.py` has no `_celsius` entry in `UNIT_ENDINGS` and no °C in `PROSE_UNITS`, and its comment above `UNSTORED_UNITS` names this item as the reason. The figure of 29 is the count of untied-restatement errors that `PL-XQXK`'s branch saw, so it counts figures rather than blocks.

**Why it matters.** The reference temperature converts a vapour volume into the millilitres of liquid agent the interface shows. The document states it 29 times as a second copy of the value in `core/liquid_agent.py`, which `CLAUDE.md`'s one-source-of-truth rule forbids. If the code's value changed, a clinician reading `docs/MODEL.md` would be told the wrong condition behind a displayed amount, and no check would say so.

**Done when.** `tools/doc_check.py` maps the `_celsius` ending to °C in `UNIT_ENDINGS` and lists °C in `PROSE_UNITS`. Each of the 29 paragraphs carries a `provenance:` marker naming `core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20.0`, or a `not-restated:` marker where 20 °C only coincides (such as the 37 °C comparison's companion figure). `doc_check.py check` reports no errors.

**Generator check.** Instance of the fact `PL-4FBP` and `PL-G424` state (the link between a document sentence and the tree fact it restates), filed after both closed; the feature model-claims-held-by-tests already works it. Not a new head.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The stored value it must agree with began after Gate 3 froze at `817a4d88`. The item is classed `safety`, so it joins v0.7.0's frozen list whatever that answer, and it stays deferred to the next gate: its `deferred-from:` records the check that no learner can see a wrong value now (`PL-8C8W`). At `817a4d88` nothing in `src/` stored the reference temperature, and `docs/MODEL.md` said that nothing the model computes reads it. `REFERENCE_TEMPERATURE_CELSIUS` and `measured_at_celsius` came with `c95177a6` (2026-10-26). 20 of the 31 lines it names predate the freeze.
