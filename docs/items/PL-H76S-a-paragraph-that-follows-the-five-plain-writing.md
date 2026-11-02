---
id: PL-H76S
title: A paragraph that follows the five plain-writing patterns is still unintelligible to a clinician when it uses another field's vocabulary ("operator split", "relative tolerance", "4e-4"), because the rule's reader is someone who knows anesthesia or Python
priority: P2
effort: S
status: needs-decision
classes: docs
feature: review-hold
touches: .claude/rules/plain-writing.md
added: 2026-11-02
---

**Problem.** On 2026-11-02 a rewritten paragraph of `docs/MODEL.md` passed the
five plain-writing patterns and was still unintelligible to the owner:

> The 5e-3 relative tolerance was chosen when the simulator used the operator
> split. At that time, the split showed a relative gap of 4e-4 in the alveolar
> fraction between steps of 0.1 s and 0.025 s, and 5e-3 is about ten times
> that gap. [...]

The owner's words (project owner, 2026-11-02, 20:04Z): "was this written with
the plain language guidelines? This is still unintelligible".

The rule's reader is "someone who knows anesthesia or Python". The "or" lets a
writer assume one specialty's vocabulary, and none of the five patterns is
about audience.

**Why it matters.** `docs/MODEL.md` is read by clinicians and educators. A
paragraph they cannot follow hides the model's limits from exactly the reader
the safety-critical standard is written for.

**Question for the owner.** Should `.claude/rules/plain-writing.md` gain a
sixth pattern, "vocabulary from another field"? It would say: write for a
clinician who is not a numerical-methods or software specialist; say what a
technical term does in plain words, or replace it; give numbers as a clinician
reads them (0.5%, "1 part in 7 trillion"), with the exact notation in brackets
only where an auditor needs it; and open with why the reader should care.

**Recommendation: add it to #1946**, which already edits this rule and waits
on the owner's read. Put to the owner on a decision card on 2026-11-02.

The worked example would be the paragraph above, rewritten:

> The simulator checks its own accuracy by running the same case with a long
> time step and a short one, then comparing the results. They may differ by at
> most 0.5% (5e-3). That limit was set when the simulator used an older,
> approximate method, whose two results differed by about 0.04%, so 0.5% left
> ten times that as headroom. The current method is exact, and the two
> results now agree to about 1 part in 7 trillion (measured 2026-10-03), so
> the limit is now a loose safety net. When a concentration is almost zero, a
> percentage means little, so any difference smaller than 1 part in 100
> million (1e-8) also passes.

**Done when.** The owner has answered, and the rule carries the sixth pattern
or the item records that it does not.
