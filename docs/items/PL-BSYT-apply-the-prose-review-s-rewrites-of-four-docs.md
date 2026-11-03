---
id: PL-BSYT
title: Apply the prose review's rewrites of four docs/MODEL.md Displayed-precision and Agent-amount paragraphs, which use count, glyph position, floor and placeholder in private senses
priority: P2
effort: S
status: ready
classes: docs
feature: prose-quality
touches: docs/MODEL.md
blocked-by: PL-ZDZ0
added: 2026-11-03
payoff: a clinician can read how precisely the concentration, MAC and agent-amount readouts are shown without decoding private terms, and so judge how far to trust them
verify: ! grep -qF 'drag label' docs/MODEL.md && ! grep -qF 'The parameter spread gives the same answer' docs/MODEL.md && ! grep -qF 'coarse in the allowed' docs/MODEL.md
---

**Problem.** The prose review on `PL-XQXK` (#1976) read four `docs/MODEL.md` paragraphs that the branch touched only to name a test or move a marker: the first paragraph of § "Displayed precision" (the 0.01-percentage-point resolution), the MAC-step paragraph after it, the paragraph on the exhausted total in millilitres of liquid, and the paragraph on why the schematic's amounts do not use the readouts' resolution. A clinician reader would not know "count" (one step of the last digit), "MAC line", "glyph position", "per-agent MAC resolution", "floor", "placeholder", "coarse in the allowed direction", "parameter spread", or why "exhaust total" and "exhausted total" are one quantity. `PL-XQXK` rewrote none of them, because `.claude/rules/plain-writing.md` makes rewriting untouched sentences work for the `prose-quality` feature.

**The reviewer's proposals.** Rerun the review on these paragraphs rather than reusing stale text, but the proposals were:

1. Fold "The resolution is the same across all six compartments" into the first sentence, and say "the label shown while the slider is dragged" for "drag label".
2. Say "step" for "count" and "digit" for "glyph position", cut "This property keeps the two units from contradicting each other" and "The unit conversion does not preserve information across agents", and use "MAC readout" consistently. The false claim in this paragraph is `PL-ZDZ0` and goes first.
3. State "One step of the litre display, 0.1 L of vapour, is 0.55 mL of sevoflurane liquid, 0.51 mL of isoflurane and 0.48 mL of desflurane", say "the smallest power of ten at or above all three is 1 mL", and use one name for the exhausted total. Check that "the exhaust total's shift" means the effect of one SD of the partition coefficients before rewording it.
4. Name what the resolution does not carry over to (the schematic's amounts), and say "It may understate the model's precision, never overstate it" for "coarse in the allowed direction".

The reviewer also proposed moving each test name to a "**For developers.**" note. Keep the names in the paragraph: `tools/doc_check.py` holds a numeric paragraph by the test it names, so moving them out would leave the figures unheld.

**Reproduced 2026-11-03.** The listed terms are still in the four paragraphs of `docs/MODEL.md`: "drag label" in the first paragraph of § "Displayed precision", "One count of the MAC line" in the second, "The parameter spread gives the same answer" and "the exhaust total's shift" in the third, and "coarse in the allowed direction" in the fourth. "glyph position" also appears in two later paragraphs of the section, which this item does not cover.

**Why it matters.** `docs/MODEL.md` is what a clinician reads to decide how far to trust a displayed value. These four paragraphs explain how precisely the concentration, MAC and agent-amount readouts are shown, and a reader who cannot decode their terms cannot use them for that.

**Order.** The second paragraph holds the false sentence that `PL-ZDZ0` corrects. That item goes first, so this one is blocked by it and the two rewrites do not collide in one paragraph.

**Done when.** The four paragraphs pass close-out step 8's review with no listed term, and `python3 tools/model_rewrite.py lost` shows no value changed.

**Generator check.** One-off; prose-quality work the plain-writing rule routes to its own item.

**Checked 2026-11-03.** `PL-ZDZ0` rewrote the second of the four paragraphs (the MAC-step paragraph) through close-out's prose review: it now says "step" and "MAC readout", and "One count of the MAC line" is gone. It also rewrote the paragraph after it, which began "The unit conversion does not preserve information across agents", without "glyph position". Proposal 2 above is therefore done. Proposals 1, 3 and 4 still apply, and "glyph position" is still in the two later paragraphs this item does not cover.
