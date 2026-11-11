---
id: PL-7KF5
title: Keep the effort trial running whatever model a session runs on, and compare high against xhigh only within one model
priority: P2
effort: S
status: done
classes: defect
feature: effort-trial
touches: docs/model-review.md, .claude/skills/model-review/SKILL.md, docs/maintainer.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-11
closed: 2026-11-11
pr: 2137
payoff: a change of model neither ends the effort trial nor mixes two models' sessions in one comparison
verify: grep -q 'Amended 2026-11-11 (`PL-7KF5`' docs/model-review.md && grep -q 'PL-7KF5' .claude/skills/model-review/SKILL.md
---

**Problem.** The trial is registered as "effort `xhigh` against `high` on Opus 5.5 cloud sessions" (`docs/model-review.md` § "Trials"). The model review's effort monitoring forms its two groups from items worked "on Opus 5.5" only (`.claude/skills/model-review/SKILL.md` § "Effort monitoring", step 1). So a session started on any other model drops out of the trial, and a switch of the default model would end the trial without the owner deciding to end it. The owner asked on 2026-11-11 that the trial continue regardless of the model chosen, with the comparison kept like for like (project owner, 2026-11-11: "session effort trial continues regardless of model chosen. (Should be comparing apples to apples)").

**What the hook does today.** `tools/effort_trial.py` reads no model. It draws the arm from the session id and writes the cap whatever model the session runs, so every cloud session already gets an arm. The restriction is only in the registration and in the review's analysis.

**Done when.**

1. The trial's registration says the trial runs on every model, and a change of model does not end it.
2. The review compares `high` against `xhigh` within one model at a time, with model as a stratum beside the split period, and never pools two models' sessions in one group. An item whose sessions ran on different models stays counted as mixed and left out, as the review already does for comparisons between settings.
3. `docs/maintainer.md` § on the trial says the same in one sentence.

**Not checked.** Whether every model the owner might pick accepts both `high` and `xhigh` as an effort level. A model that does not would need its sessions reported apart. The amendment says to check this when a new model first appears in the ledger.

**Generator check.** One-off. The model restriction was written into the registration by `PL-HYRM` when every session ran Opus 5.5, and no other item misreads it.
