---
id: PL-BSYT
title: Apply the prose review's rewrites of four docs/MODEL.md Displayed-precision and Agent-amount paragraphs, which use count, glyph position, floor and placeholder in private senses
status: untriaged
feature: prose-quality
added: 2026-11-03
---

**Problem.** The prose review on `PL-XQXK` (#1976) read four `docs/MODEL.md` paragraphs that the branch touched only to name a test or move a marker: the first paragraph of § "Displayed precision" (the 0.01-percentage-point resolution), the MAC-step paragraph after it, the paragraph on the exhausted total in millilitres of liquid, and the paragraph on why the schematic's amounts do not use the readouts' resolution. A clinician reader would not know "count" (one step of the last digit), "MAC line", "glyph position", "per-agent MAC resolution", "floor", "placeholder", "coarse in the allowed direction", "parameter spread", or why "exhaust total" and "exhausted total" are one quantity. `PL-XQXK` rewrote none of them, because `.claude/rules/plain-writing.md` makes rewriting untouched sentences work for the `prose-quality` feature.

**The reviewer's proposals.** Rerun the review on these paragraphs rather than reusing stale text, but the proposals were:

1. Fold "The resolution is the same across all six compartments" into the first sentence, and say "the label shown while the slider is dragged" for "drag label".
2. Say "step" for "count" and "digit" for "glyph position", cut "This property keeps the two units from contradicting each other" and "The unit conversion does not preserve information across agents", and use "MAC readout" consistently. The false claim in this paragraph is `PL-ZDZ0` and goes first.
3. State "One step of the litre display, 0.1 L of vapour, is 0.55 mL of sevoflurane liquid, 0.51 mL of isoflurane and 0.48 mL of desflurane", say "the smallest power of ten at or above all three is 1 mL", and use one name for the exhausted total. Check that "the exhaust total's shift" means the effect of one SD of the partition coefficients before rewording it.
4. Name what the resolution does not carry over to (the schematic's amounts), and say "It may understate the model's precision, never overstate it" for "coarse in the allowed direction".

The reviewer also proposed moving each test name to a "**For developers.**" note. Keep the names in the paragraph: `tools/doc_check.py` holds a numeric paragraph by the test it names, so moving them out would leave the figures unheld.

**Done when.** The four paragraphs pass close-out step 8's review with no listed term, and `python3 tools/model_rewrite.py lost` shows no value changed.
