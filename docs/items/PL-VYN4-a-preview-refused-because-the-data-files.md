---
id: PL-VYN4
title: A preview refused because the data files changed says each value differs on the branch, where no branch exists
status: untriaged
feature: replay-findings
added: 2026-11-23
filed-pr: 2281
---

**Problem.** `SimulationController.preview_settings` in `src/anesthesia_sim/app/controller.py` rebuilds the run from its settings to check that a preview predicts this run's case. When the rebuild differs, it raises `SimulationConfigurationError` with "a preview would be drawn from values this run does not hold, so it would predict a different case", then the list that `_disagreements_with` writes. That method was written for a branch, and each entry reads "`<name>` is `<value>` in this run and `<value>` on the branch". A preview opens no branch, so the refusal tells its reader about a branch that does not exist. The entries also name each value by its field name, such as "muscle volume_l", rather than in words with a unit.

The mutation sort of `PL-00Y5` found it on 2026-11-23, while writing `tests/integration/controller/test_controller_preview.py::test_a_preview_of_a_run_whose_patient_file_changed_is_refused_naming_each_value`. That test checks each entry only up to the second value, so it does not pin the words "on the branch".

**What to do.** Give `_disagreements_with` the name of the second build ("on the branch" for a branch, "in the preview" for a preview), or return the pairs and let each caller word them. Extend the preview test to check the whole entry.
