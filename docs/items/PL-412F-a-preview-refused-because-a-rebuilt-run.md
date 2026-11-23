---
id: PL-412F
title: A preview refused because a rebuilt run disagrees with the run disappears with no notice, and the release reports nothing
priority: P3
effort: S
status: ready
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, tests/integration/controller/test_controller_preview.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
filed-pr: 2300
payoff: a learner whose dial preview is refused sees why, instead of a preview that silently vanishes
---

**Problem.** `RunView.request_preview` in `src/anesthesia_sim/app/run_view.py` drops a refused preview and says nothing. Its docstring says "The release then reports the refusal through `_apply_setting`, as it reports any refused setting." That holds for a value the core refuses, but not for the refusal that `SimulationController.preview_settings` raises when the trial run it builds disagrees with this run (`_disagreements_with`). That happens when a data file the run was built from changed during the session. The trial run reads the new file and the run does not, so every drag on that run draws no preview, while the release applies the value through the run's own setter, which builds no trial and refuses nothing. The learner sees the preview vanish with no notice, and nothing is logged.

**What happens.** Found by `PL-VYN4`'s blind review on 2026-11-23, by reading the code; not yet reproduced through a run. `PL-VYN4` made each entry of that refusal name the preview, so the message is right, but no reader in the running app meets it.

**What to do.** Decide how the interface reports a preview refused for this reason: a notice beside the slider, as a refused setting has, or a log entry, as a failed branch has. Correct the docstring to say which refusals the release reports. Add a test that changes the data a trial run reads and checks what the learner is shown.

**Why it matters.** A learner who drags a dial and sees no preview, with no notice, cannot tell a broken preview from one that is not offered. It happens only when a data file changes during a session, so few learners will meet it.

**Done when.** A test changes the data that a trial run reads and shows that dragging a dial puts a notice in the banner, worded as a refused setting is, naming the dial. The docstring of `RunView.request_preview` says which refusals the release reports.

**Placement decided 2026-11-23.** The notice goes in the banner, where every refused setting is already shown, so the learner looks in one place for both. This is a placeholder under the owner's rule that look, wording and placement are the session's.

**Generator check.** A one-off: a docstring claim that one kind of refusal reaches the reader, found by review.
