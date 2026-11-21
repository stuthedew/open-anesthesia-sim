---
id: PL-3DHK
title: A run stopped at the supported run length that then meets an error names the error in its status word and the run length on its mark rows
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** A run stopped at the supported run length that then meets an error names the error in its status word and the run length on its mark rows

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` says "A run that has both reached the supported run length and met an error is reported as not reached within the supported run length." `_mac_target_standing` and `_time_bookmark_standing` in `app/bookmarks.py` test `stopped_at_cap` before `run_failed`, and `test_the_cap_answers_for_a_run_standing_at_it_that_then_failed` in `tests/unit/test_bookmarks.py` checks that. `status_word` in `app/dashboard_frame.py` tests `failure_reason` before `supported_limit_reason`, and its docstring says "The two cannot both arise from one run". A controller given both records through `halt_at_supported_limit(...)` and then `fail(...)` printed "status word: Stopped — simulation error" and "mark row: not reached within the supported run length". This was not reproduced through the interface. It needs a drawing error or a Reset error on a run that already stopped at 24 hours.

**Why it matters.** Both statements are true of such a run, and the learner reads two reasons for one stop. The comment above `MARK_STANDING_TEXT` says the wording was chosen to avoid "two accounts of one stop".

**Decided here** (2026-11-21): the two places keep their order, because the error is the run's last event and the run length is why a mark was not reached. The docstring of `status_word` is wrong and is corrected, and the document's sentence names both places.

**Done when.** A test builds a run that stopped at the supported run length and then failed, and checks the status word and a mark row together. The docstring of `status_word` and the document's sentence say what the two places show.
