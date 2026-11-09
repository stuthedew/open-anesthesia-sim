---
id: PL-HVLD
title: docs/MODEL.md heading 'The run is that record, and every state is derived from it' says the run is the control-input record, while its rows describe the run definition and § 'The control-input timeline' treats the two as separate records (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md, .claude/rules/run-is-its-definition.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-05
payoff: a developer looking for the record every displayed state is computed from is sent to the run definition, not to the control-input timeline
verify: ! grep -qF 'The run is that record, and every state is derived from it' docs/MODEL.md
---

**Problem.** docs/MODEL.md heading 'The run is that record, and every state is derived from it' says the run is the control-input record, while its rows describe the run definition and § 'The control-input timeline' treats the two as separate records (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6 the heading `#### The run is that record, and every state is derived from it` still sits under `### The control-input record`, after § "The control-input timeline". The section describes the run definition: settings in force and one keyframe per change, defined in `src/anesthesia_sim/core/run_definition.py`. The control-input timeline is a different record, in `src/anesthesia_sim/app/control_timeline.py`, with the values before and after each change and the user adjustment each belongs to. The heading's "that record" can only mean the control-input record. The heading is cited three times in `docs/MODEL.md` and once in `.claude/rules/run-is-its-definition.md`.

**Why it matters.** The run definition is the one record from which every displayed state is computed. A developer who reads the heading as "the run is the control-input record" looks for the state in the wrong module. They could also treat the timeline, which is kept for display and grouping, as the source of truth for what the model ran under.

**Done when.** The heading names the run definition, for example "A run is stored as its settings and keyframes, and every state is computed from them". Its four citations are updated in the same change, and the text says in one sentence how the run definition and the control-input timeline differ.

**Generator check.** One-off: a finding from the `docs/MODEL.md` structure-read sweep. A heading's pronoun pointed at the wrong record after the sections around it were reordered. No head's `misread:` states that fact.
