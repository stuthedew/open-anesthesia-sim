---
id: PL-HSP8
title: Returning to a mark opens the branch with a setting the trunk changed at that instant already in force, so the 'on your mark' branch repeats the trunk's own decision, though docs/MODEL.md calls it the branch the halt would have given
status: untriaged
feature: replay-findings
added: 2026-10-24
---

**Problem.** Returning to a mark opens the branch with a setting the trunk changed at that instant already in force, so the 'on your mark' branch repeats the trunk's own decision, though docs/MODEL.md calls it the branch the halt would have given

**Evidence.** All three panel reviewers and the generalist control in `PL-TCBJ`'s replay raised this independently on `#1451`, and a blind checker reproduced it at that merge commit. The sequence: a mark at 60 s halts the trunk at 2%, the learner turns the vaporizer to 0% while the trunk stands on the halt, and the trunk runs on. "1m, on your mark" then opens at 0%, while the halt branch taken before the change opened at 2%. On `origin/main` on 2026-10-24, `SimulationController._setting_at` in `app/controller.py` still takes a change at `elapsed_s <= instant_s` as in force, and `RunDefinition.segment_at` still picks the segment opening at the instant by `bisect_right`. So the fault looks present; it was not re-run on `main`.

**Why it matters.** A learner who returns to a decision point to try the alternative gets the trunk's own decision again, and the two traces coincide. `docs/MODEL.md` § the mark branch says "It is the branch the halt would have given" and that the two branches' provenance compares equal. A learner may conclude the decision made no difference.

**Done when.** The behaviour is reproduced on `main` and either the branch opens under the settings the reaching step was computed under, or `docs/MODEL.md` states this case and the branch shows it. A regression test changes a setting while the trunk stands on the mark.
