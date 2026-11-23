---
id: PL-VYN4
title: A preview refused because the data files changed says each value differs on the branch, where no branch exists
priority: P3
effort: S
status: done
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/app/controller.py, tests/integration/controller/test_controller_preview.py, docs/items/PL-412F-a-preview-refused-because-a-rebuilt-run.md
added: 2026-11-23
closed: 2026-11-23
pr: 2300
filed-pr: 2281
payoff: a refused preview's message names the preview it refused, not a branch that does not exist
tests: tests/integration/controller/test_controller_preview.py::test_a_preview_of_a_run_whose_patient_file_changed_is_refused_naming_each_value
---

**Problem.** `SimulationController.preview_settings` in `src/anesthesia_sim/app/controller.py` rebuilds the run from its settings to check that a preview predicts this run's case. When the rebuild differs, it raises `SimulationConfigurationError` with "a preview would be drawn from values this run does not hold, so it would predict a different case", then the list that `_disagreements_with` writes. That method was written for a branch, and each entry reads "`<name>` is `<value>` in this run and `<value>` on the branch". A preview opens no branch, so the refusal tells its reader about a branch that does not exist. The entries also name each value by its field name, such as "muscle volume_l", rather than in words with a unit.

The mutation sort of `PL-00Y5` found it on 2026-11-23, while writing `tests/integration/controller/test_controller_preview.py::test_a_preview_of_a_run_whose_patient_file_changed_is_refused_naming_each_value`. That test checks each entry only up to the second value, so it does not pin the words "on the branch".

**What to do.** Give `_disagreements_with` the name of the second build ("on the branch" for a branch, "in the preview" for a preview), or return the pairs and let each caller word them. Extend the preview test to check the whole entry.


**Done when.** A preview's refusal names the preview in each entry, "in the preview", and a branch's still says "on the branch". `tests/integration/controller/test_controller_preview.py::test_a_preview_of_a_run_whose_patient_file_changed_is_refused_naming_each_value` checks each whole entry.

**Generator check.** A one-off. The fact misread is which rebuilt run a difference belongs to, which `_disagreements_with` fixed as the branch when the preview became its second caller. No head's `misread:` names the wording of a rebuild check.

**Done 2026-11-23.** `SimulationController._disagreements_with` in `app/controller.py` takes `where`, the words that name the rebuilt run, and its two callers pass "on the branch" and "in the preview". Its parameters are now `rebuilt` and `settings_at_start`, since a preview starts at the second the run has reached rather than at a fork. The preview test now compares the whole list of entries with literals. Against the code before the fix it fails with "'muscle volume_l is 33.0 in this run and 34.0 on the branch' != 'muscle volume_l is 33.0 in this run and 34.0 in the preview'". The entries still name each value by its field name, such as "muscle volume_l". `RunView.request_preview` drops a refused preview without showing its message, so the message's only reader is a developer, in a test or a traceback, and a field name is what that reader searches for. The branch refusal, which a learner does see, already shows a sentence in words and keeps these entries in the exception's note (`PL-72X2`). Documents checked: `docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its parent" and `docs/INTERFACE.md` (neither quotes an entry).

**Blind review, 2026-11-23.** One pass. It found one older fault, which this change does not cause: `RunView.request_preview` drops a preview refused for a disagreement with no notice and no log entry, and its docstring says the release reports the refusal, which the run's own setter does not do for this reason. So no reader in the running app meets the corrected entries. That is filed as `PL-412F`.
