---
id: PL-J37P
title: Make docs/MODEL.md § "Displayed precision" readable for a clinician: move its decision history to the items and rewrite its phrasing
priority: P1
effort: M
status: done
classes: docs
feature: prose-quality
touches: docs/MODEL.md, docs/items/PL-040-stop-displaying-more-decimals-than-the-model.md, docs/items/PL-0M7K-test-displayed-ordering-reverses-only-at-a.md, docs/items/PL-X9KD-re-derive-displayed-precision-and-the-supported.md, docs/items/PL-Z4K6-decide-whether-seven-readout-columns-on-a-1366.md
added: 2026-11-02
closed: 2026-11-04
pr: 2022
payoff: a clinician reading this part of the model specification finds the equations, units and limitations without reading past decision history and padding
verify: uv run python tools/model_rewrite.py ids "Displayed precision"
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it. Readability is judged by a person: no command separates plain prose from padded prose.
---

**Problem.** The prose of docs/MODEL.md § "Displayed precision" still carries decision history and the
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

**Checked 2026-11-04, from `PL-BSYT`'s copy-editor pass.** The copy editor proposed moving four things into one "**For developers.**" note at the end of this section: the residual lines' replay protocol (the 81 runs, the v0.5.21 and v0.5.22 replay, the 2,511 samples), the six-decimal history under `PL-TG60`, the v0.7.0 scoping sentence, and every test and code name in the section. `PL-BSYT` kept each test name beside its paragraph instead. The documentation check accepts a note only for the run of paragraphs directly above it, so a single note at the section's end could not hold the first paragraph's test names. The moves are this item's work. Before cutting the history from docs/MODEL.md, check that `PL-TG60`, `PL-B396` and `PL-2881` record it.

**Closed, 2026-11-04.** The history pass moved what the cited items did not already hold to `PL-040`, `PL-X9KD`, `PL-0M7K` and `PL-Z4K6`, under dated "Moved from docs/MODEL.md" paragraphs. The rewrite split the section into eleven subsections, moved test and code names into a note for developers at the end of each, and stated each repeated figure once. One sentence changed meaning, to remove a contradiction. The paragraph saying that a change of decimal count changes only what a reader sees now also says that it changes which settings a slider can reach, as the paragraph on the two counts that set the slider steps already said. The section went from 8,142 words on `main` to 6,732, counting tables, markers and notes for developers. `tools/model_rewrite.py lost` lists no value that the rewrite added, and every dropped figure is either history that an item now holds or a duplicate of a figure that the section still states. The copy editor ran as a `general-purpose` agent given `.claude/agents/copy-editor.md`'s text, because a Projects thread cannot start the agent by name (`PL-TQ4J`). It read 8 passages and rewrote 8, and no edit was reverted. It raised four queries, settled as follows.

1. "Over a held hour" means an hour with the settings held constant, as in the reference test's held run.
2. The phrase "where a reader is least able to notice" was kept as written.
3. The 1320 px figure for a maximized 1366 px screen is the readout region's width. The claim that a 1280 px screen opens on seven columns may predate the region's split (`PL-LKX7`).
4. The six PL-040 readings carry no sample times, and the record cannot restore them.

**Blind review and the second copy-editor pass, 2026-11-04.** Both blind passes found the 1280 px claim, now stated as untested (`PL-LKX7`). The second found that "a gap between two readouts is as accurate as either reading" held only for solver error, and the section now adds the rounding of both readings. The second copy-editor pass, on those fixes, also found that "a reader who compares them in order cannot be misled by solver error" contradicted the paragraph above it, which says a reversal is possible while two compartments cross. The project owner judged that case not a real issue on 2026-11-04 (a reversal needs a true gap far smaller than one count of the last digit), so the sentence now says that a reader can rely on the order shown, and adds no warning. The first pass's bound on the last digit and the second pass's two accounting-panel ratios are unchanged from `main` and are filed as `PL-KG6S`.
