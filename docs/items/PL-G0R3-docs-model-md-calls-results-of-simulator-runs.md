---
id: PL-G0R3
title: docs/MODEL.md calls results of simulator runs 'measured' in at least twelve chapters, which a clinician can read as patient or instrument data; say 'simulated' or 'from a run' and keep 'measured' for real measurements (copy editor structure read, 2026-11-05)
priority: P1
effort: M
status: done
classes: defect, safety, docs
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
closed: 2026-11-14
pr: 2155
payoff: a clinician checking the model against published patient data can tell every model result from a real measurement, as the interface already requires
verify: ! grep -qF 'the measured value at five minutes was 0.30 to 0.32' docs/MODEL.md && ! grep -qF 'These values were measured on 2026-09-07' docs/MODEL.md
---

**Problem.** docs/MODEL.md calls results of simulator runs 'measured' in at least twelve chapters, which a clinician can read as patient or instrument data; say 'simulated' or 'from a run' and keep 'measured' for real measurements (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** On cfd4a4b6, `grep -c -i -w measured docs/MODEL.md` counts 172 uses, and many still describe a run of this simulator. Two examples are in § "Published wash-in and elimination validation test", beside published patient data. "These values were measured on 2026-09-07" heads the table of the model's own ratios. "The measured value at five minutes was 0.30 to 0.32" gives the model's inspired-to-alveolar ratio. Others are in § "Mass-balance identity" ("That run was measured four ways on 2026-10-25") and § "Halting on a marked crossing" ("measured over 20 000 samples of a live run").

**Why it matters.** The document's own safety rule is that a modeled value must never read as a measurement. In the validation section, a model value called "measured" sits in the same paragraph as the published values measured in patients. A clinician checking the model against the literature can take the model's figure for the patients' figure, or the reverse. The interface already says that its readouts are model outputs and not measurements, and the specification should keep the same line.

**Done when.** Every use of "measured" in `docs/MODEL.md` that describes a result of running this simulator says "computed", "simulated" or "from a run" instead. "Measured" stays only for quantities measured in patients, in tissue or on equipment, and for timings and sizes measured on the software or the screen, such as a frame's cost or a window's width in pixels. The two validation-section sentences quoted above are reworded.

**Generator check.** One-off: a finding from the `docs/MODEL.md` structure-read sweep. The fact is which values in the document were measured in the world and which were computed by the model. No head's `misread:` states it, and no check reads it.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/MODEL.md` § "Published wash-in and elimination validation test" already called model results measured: the elimination table was headed "measured 2026-09-06 and re-measured 2026-09-07", and the inspired fraction "is 0.29 at the highest supported flow and measured at 0.30 to 0.32 at five minutes". The problem belongs on v0.7.0's frozen list, and the deferral is removed.

**Done 2026-11-14.** Every use of "measured" in `docs/MODEL.md` was read in
context (119 on this branch's base, after stage 1 of the split moved several
sections out). Twenty described a result of running this simulator, and now say
"simulated", "computed" or "come from runs on", in § "Mass-balance identity"
(three), § "Published wash-in and elimination validation test" (the two
sentences the brief quoted, the elimination and open-circuit table dates, and
the gap kept beside the comparison), § "Desflurane's residual, and why the parameter file was not changed" (the solved
table's date, the candidate table's three, the sixth row, the dead-space table
and its note for developers), § "The first 24 hours of elimination against the published mean curves" (its regression band,
the 24-hour table's dates and "the departures computed here"), § "Known limitations" (the run-length paragraph's "the gap between the modelled tail and the published curves"), and
the humidification note and its note for developers. The remaining 99 describe
patients, tissue, equipment, a published study or a clock, and stay. Two "(measured
below)" parentheses in § "Known limitations" point at Targ et al.'s circuit
measurements and Yasuda's patient curves, so they stay. The draft that
`PL-48MX` will make `docs/MODEL.md` was read too: its uses all describe real
measurements, and `PL-48MX` now says so.

Files checked in the docs sweep: `docs/MODEL.md`,
`docs/prose-review/model-description-draft.md`.

**Blind review, 2026-11-14.** Pass 1 found four uses of the verb "measure" for
simulator results, which the brief's "measured" did not catch: caveat 3 of the
validation test ("The paragraphs above measure the difference"), the opening of
§ "The first 24 hours of elimination against the published mean curves" ("This
subsection measures the late washout"), and two "measure(s) an omission". They
now say "put the difference at", "compares the model's late washout with the
published curves" and "show(s) an omission".
