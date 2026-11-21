---
id: PL-3DHK
title: A run stopped at the supported run length that then meets an error names the error in its status word and the run length on its mark rows
priority: P3
effort: S
status: done
classes: defect
feature: interface-matches-its-spec
touches: src/anesthesia_sim/app/dashboard_frame.py, docs/INTERFACE.md, tests/integration/controller/test_controller_supported_length.py
added: 2026-11-21
closed: 2026-11-21
pr: 2191
payoff: A run that stops for two reasons shows each reason in a stated place, and a test keeps the two places in step
tests: tests/integration/controller/test_controller_supported_length.py::test_a_run_at_the_supported_run_length_that_then_fails_gives_each_reason_in_its_place
---

**Problem.** A run stopped at the supported run length that then meets an error names the error in its status word and the run length on its mark rows

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` says "A run that has both reached the supported run length and met an error is reported as not reached within the supported run length." `_mac_target_standing` and `_time_bookmark_standing` in `app/bookmarks.py` test `stopped_at_cap` before `run_failed`, and `test_the_cap_answers_for_a_run_standing_at_it_that_then_failed` in `tests/unit/test_bookmarks.py` checks that. `status_word` in `app/dashboard_frame.py` tests `failure_reason` before `supported_limit_reason`, and its docstring says "The two cannot both arise from one run". A controller given both records through `halt_at_supported_limit(...)` and then `fail(...)` printed "status word: Stopped — simulation error" and "mark row: not reached within the supported run length". This was not reproduced through the interface. It needs a drawing error or a Reset error on a run that already stopped at 24 hours.

**Why it matters.** Both statements are true of such a run, and the learner reads two reasons for one stop. The comment above `MARK_STANDING_TEXT` says the wording was chosen to avoid "two accounts of one stop".

**Decided here** (2026-11-21): the two places keep their order, because the error is the run's last event and the run length is why a mark was not reached. The docstring of `status_word` is wrong and is corrected, and the document's sentence names both places.

**Done when.** A test builds a run that stopped at the supported run length and then failed, and checks the status word and a mark row together. The docstring of `status_word` and the document's sentence say what the two places show.

**Built 2026-11-21.** No code path changed. `test_a_run_at_the_supported_run_length_that_then_fails_gives_each_reason_in_its_place` builds a controller that records the supported run length and then an error, and checks that the status word reports the error and that the row of an unreached mark reports the run length. The docstring of `status_word` now says that one run can carry both records and why each place reports the one it does. `docs/INTERFACE.md` § "Halting on a marked crossing" says what the status word and the mark row show for such a run.

**Generator check.** One-off. The fact is whether one run can carry both stop records. The document said it can and the docstring of `status_word` said it cannot. Found by `PL-5FMC`, the check of the interface documents that the project owner asked for.
