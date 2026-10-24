---
id: PL-YF16
title: bin/docket show's session line names the configured model whenever it differs from the served one, and 292 of the ledger's 327 such rows differ only by a [1m] context-window suffix, so the note mostly flags sessions that never switched model and buries the 35 real fallbacks: compare with the suffix removed, or print the context window apart from the model
status: untriaged
feature: model-evidence
added: 2026-10-24
---

**Problem.** bin/docket show's session line names the configured model whenever it differs from the served one, and 292 of the ledger's 327 such rows differ only by a [1m] context-window suffix, so the note mostly flags sessions that never switched model and buries the 35 real fallbacks: compare with the suffix removed, or print the context window apart from the model

**Not a recurrence of PL-70M6.** `bin/docket new` matched this filing to PL-70M6 because both concern the same section of `docket show`. This item is a follow-up found while reviewing PL-70M6's worker branch, not a second report of the same problem, so the match was withdrawn on 2026-10-24.
