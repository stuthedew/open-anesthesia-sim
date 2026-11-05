---
id: PL-XT53
title: Make docs/MODEL.md § "The control-input timeline" through § "The six compartment traces: what separates them" readable for a clinician: move its decision history to the items and rewrite its phrasing
priority: P2
effort: M
status: done
classes: docs
feature: prose-quality
milestone: v0.6.16
touches: docs/MODEL.md, tools/model_rewrite.py, tests/unit/test_model_rewrite.py, src/anesthesia_sim/app/chart_frame.py
blocked-by: PL-HGZS
added: 2026-11-02
closed: 2026-11-05
pr: 2042
payoff: a clinician reading this part of the model specification finds the equations, units and limitations without reading past decision history and padding
verify: ! grep -qF '**What it is.** The timeline is a record' docs/MODEL.md && grep -qF '**The timeline records the settings that a run' docs/MODEL.md
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it. Readability is judged by a person: no command separates plain prose from padded prose.
---

**Problem.** The prose of docs/MODEL.md § "The control-input timeline" through § "The six compartment traces: what separates them" still carries decision history and the
phrasing patterns that `PL-ZT47` names. The history is item ids, re-measurement narratives, notes
on who supplied a source, ratification records and accounts of how a choice was
reached. The phrasing patterns are tautological asides, contrasts nobody
claimed, narration about the document, defensive scope statements, and table
cells or paragraphs that have grown into essays. The project owner judged the
document to read "like the worst kind of AI slop" on 2026-11-02, and decided
that it should be a document clinicians can read (project owner, 2026-11-02).

**Why it matters.** `docs/MODEL.md` is the document a clinician opens to decide
whether to trust a displayed number. History and padding bury the equation, the
unit and the limitation the reader came for.

**How.** `PL-ZT47` § "How each section part is done" is the procedure: take the
history out to the items first, in its own commit, then rewrite the phrasing,
and account for every line `tools/model_rewrite.py lost` prints. No equation,
unit, value, assumption, limitation, citation, marker, named test or
declared-none form may be lost. `PL-ZT47` built the rule and the tools this
uses.

**Generator check.** Work the owner asked for: one section part of `PL-ZT47`'s
decided split. The mechanism that let the history and padding accumulate,
`docs/MODEL.md` prose that no close-out review read, is `PL-ZT47`'s to fix.

**Done when.** `uv run python tools/model_rewrite.py ids` prints nothing for this part's sections, which its
`verify:` runs. The pull request body accounts for every line
`tools/model_rewrite.py lost` prints. The owner reads it only where
`PL-ZTZF`'s rule sends it: a changed value, equation, code span or citation,
or a sentence whose meaning needs their judgment.

**Blocked** (project owner, 2026-11-04). This rewrite waits for the writing rule and the copy editor that `PL-J1ZM`'s design builds through `PL-W8FL`, `PL-43GT`, `PL-22T5` and `PL-JP8X`. Done before them, it would be written under the rules that made the section verbose, and then rewritten again.

**Ready, 2026-11-04.** All four have closed, so the rewrite is written now, and the copy editor edits it at close-out step 8.

**Applied 2026-11-05.** The four sections are the copy editor's runs: color contrast and the six compartment traces from the runs the project owner approved during the `PL-HGZS` debugging, and the control-input timeline and F_A/F_I from fresh runs after `PL-HGZS` merged. The session answered the copy editor's questions from the code: a chart counts unmarked adjustments (`undrawn_control_marks`), the fixed control names guard against accessor renames (`ControlInput`'s docstring), and the wash-in crossing ceiling is `WASH_IN_TERMINUS_CEILING`. It fixed `tools/model_rewrite.py`, which crashed on a section number such as 1.4.11, and filed `PL-N8G4` (no recorded reason for the two display limits) and `PL-FCYQ` (no test replays a timeline into a fresh run). Two independent review passes found two faults, both fixed: the timeline still described a drag as a series of settings, though since `PL-5B1N` a drag applies once on release; and the claim that muscle and mixed venous are the most widely separated colour pair, which the pairwise table contradicts (they are second, after circuit and alveolar), also in `app/chart_frame.py`'s comment.

**Why `verify:` changed.** It ran `tools/model_rewrite.py ids` over the sections and passed only when that printed nothing. The rewrite keeps each item id that stands beside a recorded decision, so the command can never print nothing. The new command checks that a sentence of the old text is gone and that the rewritten one is present.
