---
id: PL-BS6N
title: No writing rule says when a model limitation earns a sentence: the owner had a PL-J37P warning about a reversal smaller than one count of the last digit taken out ('You don't need to add a risk to everything. Only what needs it'), while the safety standard asks for limitations to be visible
status: untriaged
feature: reader-first-prose
added: 2026-11-04
---

**Problem.** No writing rule says when a model limitation earns a sentence: the owner had a PL-J37P warning about a reversal smaller than one count of the last digit taken out ('You don't need to add a risk to everything. Only what needs it'), while the safety standard asks for limitations to be visible.

**Evidence.** In the `PL-J37P` thread on 2026-11-04 the owner said: "You don't need to add a risk to everything. Only what needs it", then "More just it seems like sometimes you try to find something to warn about when it seems like not a real issue (I could be wrong)". The warning said a reader could be misled about two compartments that are crossing, where the true gap is far smaller than one count of the last digit. The sentence became "a reader can rely on the order shown". The owner asked for no rule.

**Recommended.** One sentence in `.claude/rules/plain-writing.md`: state a limitation where it could change what a clinician concludes from a displayed value, and leave out one below the display's own resolution. `CLAUDE.md`'s safety-critical standard asks that uncertainty and model limitations be visible, so where the line falls is the owner's decision, and this item should go to them as one.

**Answer** (project owner, 2026-11-04, ratified, over describing every model limitation): add the rule as recommended above.

**Next, 2026-11-04.** The session that took the answer passed its token budget and reset before building. Triage this item first, because it is untriaged. Then add the sentence to `.claude/rules/plain-writing.md`, in the paragraph that opens "Write what the reader needs to act on, and stop". That file is resident, so the commit names what the sentence replaces, or says why nothing can be cut. The same file says that "the safety-critical standard ... decides which facts ... must give, and this rule never cuts one". The new sentence must not read as licence to cut a limitation that standard requires: a limitation below the display's own resolution cannot change a displayed value, so it is the only kind the sentence leaves out. Run the copy editor at close-out, then close the item.
