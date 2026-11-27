---
id: PL-VQY1
title: Reword the teaching framing PL-PGVL left: 'teaches' used to mean 'shows' in docs/MODEL.md, docs/INTERFACE.md and docs/PARAMETERS.md (such as 'teaches an earlier wake-up'), the name TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN and the 'teaching default' label on the 4.0 L/min flow, and the ROADMAP.md headings 'Playback and teaching views' and item 44's 'for teaching'
priority: P3
effort: M
status: ready
classes: docs
touches: docs/MODEL.md, docs/INTERFACE.md, docs/PARAMETERS.md, ROADMAP.md, src/anesthesia_sim/core/circuit.py
added: 2026-11-27
filed-pr: 2328
payoff: the documents describe what a value shows rather than what it teaches, matching a general-purpose simulator
---

**Problem.** Reword the teaching framing PL-PGVL left: 'teaches' used to mean 'shows' in docs/MODEL.md, docs/INTERFACE.md and docs/PARAMETERS.md (such as 'teaches an earlier wake-up'), the name TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN and the 'teaching default' label on the 4.0 L/min flow, and the ROADMAP.md headings 'Playback and teaching views' and item 44's 'for teaching'

**Why it matters.** The project owner described the simulator on 2026-11-27 as general-purpose simulation software that can be used for teaching (`PL-PGVL`). `PL-PGVL` renamed the person using it from "learner" to "user" and reworded each statement of what the simulator is for. It left the sentences above, where "teaches" means that a displayed value shows a reader something, because rewording them is a sentence-by-sentence judgment, and the constant rename reaches `core/circuit.py`, the machine profile's data file and the tests that name it.

**Done when.** Each "teaches" that means "shows" in the three documents reads "shows" or an equivalent, the constant and its label name the flow as the default rather than a teaching default, and the two `ROADMAP.md` headings name what the views do. A heading that changes is renamed with every file that cites it.

**Generator check.** One-off: the remainder of `PL-PGVL`.
