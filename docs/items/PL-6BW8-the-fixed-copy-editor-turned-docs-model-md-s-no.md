---
id: PL-6BW8
title: The fixed copy editor turned docs/MODEL.md's 'No error is raised at any of these steps [...] and still returns normally' (Supported simulation step) into 'The model reports no fault [...] and the model still reports none', and moved no exact form to the note for developers, so a developer loses that each tiny step returns normally
priority: P3
effort: S
status: dropped
classes: docs
feature: repo-copy-edit
touches: docs/MODEL.md
deferred-from: v0.7.0 - not present at the freeze (817a4d88) or now: the loss is from a copy-editor test run of 2026-11-09, in no commit
added: 2026-11-09
closed: 2026-11-14
reason: The project owner chose on 2026-11-14 to remove the copy editor completely, and PL-GL45 removed it with its agents, the blind judge and their tests, so this work on the copy editor has nothing left to act on.
payoff: the next line edit of docs/MODEL.md can reword the clinician's sentence about tiny steps without losing the developer's fact that the code accepts them silently
verify: grep -qiF 'raises no exception' docs/MODEL.md
---

**Problem.** The fixed copy editor turned docs/MODEL.md's 'No error is raised at any of these steps [...] and still returns normally' (Supported simulation step) into 'The model reports no fault [...] and the model still reports none', and moved no exact form to the note for developers, so a developer loses that each tiny step returns normally

**What happened.** `PL-F0Q2`'s end pass ran the fixed copy editor on part 37 of the frozen `docs/MODEL.md`, § "Supported simulation step", on 2026-11-09. Both meaning checks in its fifth round found nothing lost, and it kept 4 of the 5 statements that the earlier audit had found lost there. The fifth changed as follows.

- Before: "No error is raised at any of these steps. At $`10^{-14}`$ s, the change over those steps is a third wrong, and a single step's change is nearly half wrong, yet each is returned as an ordinary step. From about $`10^{-16}`$ s down, a step changes nothing, and still returns normally."
- After: "The model reports no fault at any of these steps, even at $`10^{-14}`$ s, where the change over the 10 000 steps is a third wrong and a single step's change is nearly half wrong. From about $`10^{-16}`$ s down, a step changes nothing, and the model still reports none."

The clinician's point survives: the model gives no sign that these steps are wrong. "Raised" and "returns normally" are software terms that the plain-writing rule keeps out of a clinician's sentence, so the edit was right to reword them there. It should have put the exact form in the section's note for developers, and it did not. The run's files are in the project's shared folder, `v0.7.0/copy-editor-f0q2/runs/fix11-p037/`.

**Decision.** The project owner chose to resume the paused copy edits with this result, over one more rule fix and a rerun of the section (2026-11-09, ratified). So this is fixed where `docs/MODEL.md` is line edited, not by rerunning the test set.

**Done when.** The line edit of `docs/MODEL.md` § "Supported simulation step" keeps, in the clinician's text or in its note for developers, that no error is raised at these steps and that each returns as an ordinary step. If the same kind of loss, where a statement about the software's behaviour is reworded for the clinician and its exact form goes nowhere, turns up again, add a rule for it to `.claude/agents/copy-editor.md` and test it on the set.

**Checked 2026-11-09:** On cfd4a4b6, `grep -n 'No error is raised\|returns normally' docs/MODEL.md` finds the original sentences, unchanged, in § "Supported simulation step". The rewrite this item describes ran on a frozen copy and has not reached the tree. A later line edit of `docs/MODEL.md` will reach this paragraph again with the same copy editor.

**Why it matters.** "No error is raised" and "returns normally" tell a developer that the code accepts these tiny steps silently. Below the smallest supported step, nothing in the code signals that a result is wrong, so only the stated limit protects a caller. The plain-writing rule moves software terms out of a clinician's sentence and into the section's note for developers. The copy editor reworded them without moving them, so the next line edit will lose that fact unless it is already in the note for developers.

**Done when.** The note for developers of § "Supported simulation step" states that the step function raises no exception at any of the tabulated steps, and that from about 10⁻¹⁶ s down a step changes nothing and still returns normally. The clinician's sentence can then be reworded without losing the fact. Putting it in the note now, ahead of the line edit, is this session's choice of where the fix goes. It meets the owner's decision that the fix is made in `docs/MODEL.md`, and does not wait for a rerun of the copy editor.

**Generator check.** One-off: a single loss in a copy-editor test run. The brief's own condition for a copy-editor rule, a second loss of this kind, has not occurred. No head's `misread:` states that fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88 and on cfd4a4b6 the sentences are intact. The loss happened only in a copy-editor test run of 2026-11-09 under `PL-F0Q2`, and no commit carries it. The deferral stays with that reason.
