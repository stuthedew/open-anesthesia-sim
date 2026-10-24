---
id: PL-YF16
title: bin/docket show's session line names the configured model whenever it differs from the served one, and 292 of the ledger's 327 such rows differ only by a [1m] context-window suffix, so the note mostly flags sessions that never switched model and buries the 35 real fallbacks: compare with the suffix removed, or print the context window apart from the model
priority: P3
effort: S
status: ready
classes: defect
feature: model-evidence
touches: subprojects/docket/src/docket/sessions.py, subprojects/docket/tests/test_sessions.py
added: 2026-10-24
payoff: the session line flags only the sessions that really ran on another model, so the 35 real fallbacks stand out
verify: grep -q 'def test_a_context_window_suffix_alone_is_not_a_model_switch' subprojects/docket/tests/test_sessions.py
---

**Problem.** bin/docket show's session line names the configured model whenever it differs from the served one, and 292 of the ledger's 327 such rows differ only by a [1m] context-window suffix, so the note mostly flags sessions that never switched model and buries the 35 real fallbacks: compare with the suffix removed, or print the context window apart from the model

**Not a recurrence of PL-70M6.** `bin/docket new` matched this filing to PL-70M6 because both concern the same section of `docket show`. This item is a follow-up found while reviewing PL-70M6's worker branch, not a second report of the same problem, so the match was withdrawn on 2026-10-24.

**Reproduced 2026-10-24.** Reading `docs/session-ledger.tsv` directly: 1,188 rows, 327 where `configured_model` is set and differs from `last_served_model`, 292 of those differing only by the `[1m]` suffix, and 35 real differences. The comparison is at line 201 of `subprojects/docket/src/docket/sessions.py`.

**Why it matters.** The note exists to show a session that ran on a model other than the one configured, which is evidence for the model-review work. When 89% of the notes are false, a reader learns to skip the note, and the 35 real fallbacks are skipped with them.

**Route decided 2026-10-24 at triage: compare with the suffix removed.** The context window is not the model, so the note fires only when the models differ. Printing the window separately is not needed for the note's purpose.

**Done when.** The session line names the configured model only when it differs from the served model after the `[1m]` suffix is removed from both, and `subprojects/docket/tests/test_sessions.py` has `test_a_context_window_suffix_alone_is_not_a_model_switch`.

**Generator check.** A one-off. No head's `misread:` states which model a session ran, and no other open item misreads it.
