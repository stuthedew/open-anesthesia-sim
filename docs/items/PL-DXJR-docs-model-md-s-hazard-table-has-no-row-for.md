---
id: PL-DXJR
title: docs/MODEL.md's hazard table has no row for entering an identifiable patient's parameters to predict for that patient, the foreseeable misuse its intended-use section names, so that misuse has a stated boundary and no listed mitigation or test
status: untriaged
feature: presentation-safety
added: 2026-11-02
---

**Problem.** `docs/MODEL.md` § "Intended use, and the safety class this
project holds itself to" names one foreseeable misuse: entering an identifiable
patient's weight, age or cardiac output to predict for that patient. ISO
14971:2019 clause 5.2 asks for that misuse to be documented with its
mitigation. Every row of the hazard table in § "Reasonably foreseeable misuse,
and the hazards the presentation carries" covers a misreading of the display
instead. Until `PL-J8CG`, two sentences in those sections said the misuse was
listed in the table with mitigations, which was not true. A blind review of
`PL-J8CG` found this (pass 2, finding F2), and that branch rewrote the sentence
to say the row does not exist yet.

**Why it matters.** The patient-covariate work planned in `ROADMAP.md` makes the
misuse possible. A boundary stated in prose, with no mitigation or test, is the
weakest control ISO 14971 recognises.

**How.** Decide what the mitigation is now, while the interface accepts no
patient covariates: probably the intended-use statement plus the fixed
reference patient, so the row can name a test that the patient is the shipped
reference adult. Add the row, or its declared-none form naming this item, and
reword the sentence in § "This is an engineering bar, not a regulatory status"
to point at it.

**Done when.** The hazard table has a row for the misuse, with its test or
``no test yet (`PL-XXXX`)`` naming an open item, and the sentence that
`PL-J8CG` wrote says the row exists.
