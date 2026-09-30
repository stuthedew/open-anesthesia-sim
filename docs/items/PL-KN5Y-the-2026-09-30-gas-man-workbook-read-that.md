---
id: PL-KN5Y
title: The 2026-09-30 Gas Man Workbook read that located the 70 kg reference weight (Chapter 13, 'Patient Size', printed page 127) owes an extraction note under docs/references/README.md once PL-Z3V5 settles what one contains
priority: P2
effort: S
status: blocked
classes: docs
feature: provenance
touches: docs/references
blocked-by: PL-Z3V5
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-30
payoff: a later session checking where the 70 kg reference weight is stated finds the page in the corpus notes instead of re-reading the Workbook
---

**Problem.** The 2026-09-30 Gas Man Workbook read that located the 70 kg reference weight (Chapter 13, 'Patient Size', printed page 127) owes an extraction note under docs/references/README.md once PL-Z3V5 settles what one contains

**What was read, so the note can be written without re-reading the book.**
While closing `PL-9LXK` on 2026-09-30, a review pass doubted that the Gas Man
Workbook is the authority for `weight_kg`, because the Workbook entry in
`src/anesthesia_sim/data/patients/reference_adult.json` says "weight_kg 70.0 IS
STILL IN NEITHER APPENDIX". The session checked the whole Workbook's text
extraction in the private reference corpus
(`text/gasman_workbook/04_Ch13-19_Clinical_Techniques.txt`). Chapter 13,
"Patient Size", printed page 127, says: "Values for volumes and flows for a
70 kg patient are those found often in the literature: VA = 4 L/min, CO = 5
L/min, and oxygen consumption = 250 mL/min." That entry's citation and note
now name the page. What is still owed is the corpus-side extraction note in the
form `PL-Z3V5` settles, beside `PL-N701`'s two, which this one recurs.

**Why it matters.** `.claude/rules/citing-sources.md` says a read from the
corpus owes an extraction note, because otherwise the corpus is consulted once
per session rather than once per source. This read settled a provenance
question a review raised, and without the note the next session to doubt it
reads the book again.

**Done when.** The extraction note exists in the form `PL-Z3V5` settles. It
names the corpus file, the printed page and the quoted sentence.
