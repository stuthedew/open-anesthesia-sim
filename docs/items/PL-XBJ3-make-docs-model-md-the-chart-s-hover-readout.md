---
id: PL-XBJ3
title: Make docs/MODEL.md § "The chart's hover readout: what the tooltip may show" through § "The compartment schematic: what its heights, amounts and share bar assert" readable for a clinician: move its decision history to the items and rewrite its phrasing
priority: P2
effort: M
status: done
classes: docs
feature: prose-quality
touches: docs/MODEL.md
blocked-by: PL-HGZS
added: 2026-11-02
closed: 2026-11-05
pr: 2042
payoff: a clinician reading this part of the model specification finds the equations, units and limitations without reading past decision history and padding
verify: ! grep -qF 'The argument that the pointer is already over one curve' docs/MODEL.md && grep -qF 'When the pointer rests over a trace, a small box' docs/MODEL.md
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it. Readability is judged by a person: no command separates plain prose from padded prose.
---

**Problem.** The prose of docs/MODEL.md § "The chart's hover readout: what the tooltip may show" through § "The compartment schematic: what its heights, amounts and share bar assert" still carries decision history and the
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

**Ready, 2026-11-04.** All four have closed, so the rewrite can be done now, and the copy editor edits it at close-out step 8.

**Checked 2026-11-04.** Its `verify:` command named § "Minimum displayed outputs", which runs to § "Assumptions" and so also covered the sections of `PL-J37P`, `PL-PS5H` and `PL-XT53`. It now names this item's four sections.

**Applied 2026-11-05.** The four subsections are the copy editor's fresh runs after `PL-HGZS` merged, the hover readout as one whole section. The session restored the decision record that the price is taken per bottle (`PL-VJZK`, 2026-10-26), which the run cut, and answered the copy editor's questions from the text and code: a price typed per millilitre makes the shown price per millilitre too low; the price is the one value shown that is not modelled; SC 1.4.11 is WCAG's; and § "MAC multiples as a display unit" gives the reason for the 3 MAC top. Two independent review passes found faults, all fixed: the hover's printed instant is rounded to a hundredth of a second, not to the simulation step; the compartment schematic exists, so the fat paragraph points at it; the four-line and three-line limits are measured results; a cost View's amount is not a vapour volume; and the end-to-end cost test is in `tests/integration/test_agent_cost_view.py`.

**Why `verify:` changed.** It ran `tools/model_rewrite.py ids` over the subsections and passed only when that printed nothing. The rewrite keeps each item id that stands beside a recorded decision, so the command can never print nothing. The new command checks that a sentence of the old text is gone and that the rewritten one is present.
