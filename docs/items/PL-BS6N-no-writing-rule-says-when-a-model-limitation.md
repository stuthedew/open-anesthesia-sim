---
id: PL-BS6N
title: No writing rule says when a model limitation earns a sentence: the owner had a PL-J37P warning about a reversal smaller than one count of the last digit taken out ('You don't need to add a risk to everything. Only what needs it'), while the safety standard asks for limitations to be visible
priority: P2
effort: S
status: needs-decision
classes: docs
feature: reader-first-prose
touches: .claude/rules/plain-writing.md, docs/resident-instructions.md
deferred-from: v0.7.0 - a wording question on a writing rule, outside the schematic milestone
added: 2026-11-04
payoff: sessions stop adding a warning beside a value about an effect too small to change it on screen, so a learner sees the warnings that could change a decision
verify: ! grep -q "display's own resolution" .claude/rules/plain-writing.md && grep -q 'PL-BS6N' .claude/rules/plain-writing.md
---

**Problem.** No writing rule says when a model limitation earns a sentence: the owner had a PL-J37P warning about a reversal smaller than one count of the last digit taken out ('You don't need to add a risk to everything. Only what needs it'), while the safety standard asks for limitations to be visible.

**Evidence.** In the `PL-J37P` thread on 2026-11-04 the owner said: "You don't need to add a risk to everything. Only what needs it", then "More just it seems like sometimes you try to find something to warn about when it seems like not a real issue (I could be wrong)". The warning said a reader could be misled about two compartments that are crossing, where the true gap is far smaller than one count of the last digit. The warning was replaced with "a reader can rely on the order shown". The owner asked for no rule.

**Why it matters.** The safety-critical standard asks that model limitations be visible and sets no threshold, so a session adds a warning beside every value. A warning about an effect too small to show on screen tells a learner to distrust a value they can rely on, and it buries the warnings that could change a decision.

**Done when.** The paragraph of `.claude/rules/plain-writing.md` that opens "Write what the reader needs to act on, and stop" says to state a model limitation where it could change what a clinician concludes from a displayed value, and to leave out only one smaller than the display's own resolution.

**Generator check.** This item is an instance of `PL-J1ZM`'s fact, what a reader can do without, applied to one kind of fact: a model limitation. It writes part of the fix for `PL-J1ZM`. `PL-J1ZM` is still open, so this item is not a re-entry, and it is not a new head.

**Recommended.** Add one sentence to `.claude/rules/plain-writing.md` that says to state a limitation where it could change what a clinician concludes from a displayed value, and to leave out one below the display's own resolution. `CLAUDE.md`'s safety-critical standard asks that uncertainty and model limitations be visible, so where the line falls is the owner's decision, and this item should go to them as one.

**Answer** (project owner, 2026-11-04, ratified, over describing every model limitation): add the rule as recommended above.

**Next, 2026-11-04.** The session that took the answer passed its token budget and reset before it built the change. Triage this item first, because it is untriaged. Then add the sentence to `.claude/rules/plain-writing.md`, in the paragraph that opens "Write what the reader needs to act on, and stop". That file is resident, so the commit names what the sentence replaces, or says why nothing can be cut. The same file says that "the safety-critical standard ... decides which facts ... must give, and this rule never cuts one". The new sentence must not read as licence to cut a limitation that standard requires. A limitation below the display's own resolution cannot change a displayed value, so it is the only kind the sentence leaves out. Run the copy editor at close-out, then close the item.

**Decision needed, 2026-11-04.** The project owner asked whether the two sentences added here are too specific for a file that every session loads: "That seems like an overly specific instruction". They handle a rare case, a limitation smaller than one count of the last digit shown. "Leave out only" also reads as requiring every larger limitation to be stated, even one that cannot change a clinical conclusion, which is the over-warning the owner objected to. **Recommended:** replace both sentences with one: "State a model limitation only where it could change what a clinician concludes from a displayed value (`PL-BS6N`)." The rule's closing paragraph still says that the safety-critical standard decides which facts a text must give, and that this rule never cuts one.
