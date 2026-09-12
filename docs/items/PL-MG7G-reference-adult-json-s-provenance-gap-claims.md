---
id: PL-MG7G
title: reference_adult.json's provenance_gap claims the perfusion fractions have no identified origin at all, which overstates what four readings established, and it has grown into a dated research log where the field's job is to say why no tier-1 source was adopted
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.13
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-10
closed: 2026-09-10
pr: 494
verify: uv run pytest tests/unit/test_parameters.py && python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/patients/reference_adult.json')); g=d['provenance_gap']; assert 'IT DOES NOT FOLLOW THAT NO ORIGIN EXISTS' in g and 'no identified origin at all' not in g"
---

**Problem.** reference_adult.json's provenance_gap claims the perfusion fractions have no identified origin at all, which overstates what four readings established, and it has grown into a dated research log where the field's job is to say why no tier-1 source was adopted

**Why it matters.** `docs/MODEL.md`'s source hierarchy gives this field one
job: say **why no tier-1 source was adopted**, for a file whose every
physiologic parameter is in that state. A clinician or reviewer reading it is
asking whether to trust the numbers. Two things had gone wrong with it in a
single afternoon of provenance work, and the first is a correctness problem
rather than a style one.

**The overstatement.** It ended: "So the perfusion fractions have no identified
origin **at all**, and that is now established rather than outstanding." That
fuses a defensible claim with an indefensible one. What four readings
established is that **figure 4.1b's flow column reproduces from none of the
four references Lowe and Ernst name for it** - a statement about four documents
somebody has read, and true. "No identified origin at all" reads as a claim
about the world, that no origin exists, and nothing supports it: the book
prints more than one table, Gas Man may lump differently, and nobody has looked
anywhere the chain does not name. It is the same error this file already
refuses elsewhere, in the words "THAT IS THIS PROJECT'S ARITHMETIC AND IT
CONVICTS NOBODY".

**It had also become a research log.** 3,217 characters, over half of them a
dated chronology naming six item ids, written by appending three times in one
session. Two clauses said the same thing 700 characters apart - "TERMINATES AT
TIER 2 ... REACHES TIER 1 NOWHERE" and "NO DOCUMENT IN THIS CHAIN MEASURED" -
which is the visible seam between the appends. Seven all-capital clauses, at
which density the convention stops signalling.

**What was done, on the project owner's decision of 2026-09-10.**

- The first block is unchanged: what is adopted, what carries a comparison, and
  what has none. That is the gap itself and was never the problem. One clause
  was added to its opening - "and none is available to adopt" - because that is
  the reader's actual question.
- The chronology is replaced by the chain stated as a shape rather than as a
  sequence of readings: three sentences, no dates beyond the one, two item ids
  instead of six.
- The flow finding is restated as what was checked. It now says the column
  "reproduces from none of the four references the book names for it", that the
  project "has read every source the chain names and has not found where the
  flow fractions came from", and then, in its own clause, **"IT DOES NOT FOLLOW
  THAT NO ORIGIN EXISTS"**.
- 3,217 characters to 2,396. Nothing is lost: the chain in full is in
  `docs/MODEL.md`'s "Parameter provenance" and the per-document detail is in the
  sixteen `sources` entries, and the field now points at both.

**One thing checked and left alone.** `docs/MODEL.md` and the Lowe and Ernst
`sources` entry already carried the narrowed form - "no identified origin **in
any reference the book names for them**" - so only `provenance_gap` was wrong.
What `docs/MODEL.md` gained is the same explicit clause, because "that is
established now rather than outstanding" is the sentence a reader could still
take too broadly.

**A wording bug fixed in passing.** The draft put to the project owner said
"the Workbook entry **below**" and "each source entry **below**". `sources` sits
*above* `provenance_gap` in the file, and the field's existing text said
"above". Corrected before it landed.

**The `verify:` command was run both ways**: exit 1 against `origin/main`, exit
0 here.
