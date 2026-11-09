---
id: PL-6BW8
title: The fixed copy editor turned docs/MODEL.md's 'No error is raised at any of these steps [...] and still returns normally' (Supported simulation step) into 'The model reports no fault [...] and the model still reports none', and moved no exact form to the note for developers, so a developer loses that each tiny step returns normally
status: untriaged
feature: repo-copy-edit
added: 2026-11-09
---

**Problem.** The fixed copy editor turned docs/MODEL.md's 'No error is raised at any of these steps [...] and still returns normally' (Supported simulation step) into 'The model reports no fault [...] and the model still reports none', and moved no exact form to the note for developers, so a developer loses that each tiny step returns normally

**What happened.** `PL-F0Q2`'s end pass ran the fixed copy editor on part 37 of the frozen `docs/MODEL.md`, § "Supported simulation step", on 2026-11-09. Both meaning checks in its fifth round found nothing lost, and it kept 4 of the 5 statements that the earlier audit had found lost there. The fifth changed as follows.

- Before: "No error is raised at any of these steps. At $`10^{-14}`$ s, the change over those steps is a third wrong, and a single step's change is nearly half wrong, yet each is returned as an ordinary step. From about $`10^{-16}`$ s down, a step changes nothing, and still returns normally."
- After: "The model reports no fault at any of these steps, even at $`10^{-14}`$ s, where the change over the 10 000 steps is a third wrong and a single step's change is nearly half wrong. From about $`10^{-16}`$ s down, a step changes nothing, and the model still reports none."

The clinician's point survives: the model gives no sign that these steps are wrong. "Raised" and "returns normally" are software terms that the plain-writing rule keeps out of a clinician's sentence, so the edit was right to reword them there. It should have put the exact form in the section's note for developers, and it did not. The run's files are in the project's shared folder, `v0.7.0/copy-editor-f0q2/runs/fix11-p037/`.

**Decision.** The project owner chose to resume the paused copy edits with this result, over one more rule fix and a rerun of the section (2026-11-09, ratified). So this is fixed where `docs/MODEL.md` is line edited, not by rerunning the test set.

**Done when.** The line edit of `docs/MODEL.md` § "Supported simulation step" keeps, in the clinician's text or in its note for developers, that no error is raised at these steps and that each returns as an ordinary step. If the same kind of loss, where a statement about the software's behaviour is reworded for the clinician and its exact form goes nowhere, turns up again, add a rule for it to `.claude/agents/copy-editor.md` and test it on the set.
