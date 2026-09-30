---
id: PL-9LXK
title: Nothing checks a prose claim about the tier or adoption of a stored value's source, though PL-1JDD made both machine-readable and three such claims went stale within a day
priority: P2
effort: M
status: ready
classes: defect, infra, docs
feature: provenance
touches: tools/doc_check.py, tests/unit/test_doc_check.py, tools/source_tier_counts.py, tests/unit/test_source_tier_counts.py, docs/MODEL.md, .claude/rules/sources-and-docstrings.md, src/anesthesia_sim/core/parameters.py, tests/unit/test_parameters.py, tests/reference/test_sevo_patient.py, src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json, src/anesthesia_sim/data/patients/reference_adult.json, src/anesthesia_sim/data/machines/reference_circle_system.json
added: 2026-09-07
verify: python3 tools/source_tier_counts.py && python3 tools/doc_check.py check
---

**Problem.** Nothing checks a prose claim about the tier or adoption of a stored value's source, though PL-1JDD made both machine-readable and three such claims went stale within a day

**What is decidable here.** Since `PL-1JDD` every `sources` entry declares
`tier` and `adopted`, so a prose claim of the form "all twelve partition
coefficients are the Gas Man set", "all eleven physiologic parameters are the
Gas Man default patient", or "of the 29 rows, 26 are tier 3" is answerable by
reading the data files. `tools/doc_check.py` already has the mechanism one
field over: `PROSE_MARKER_RE` reads a `<!-- provenance: ... -->` marker and
holds the figure beside it to the value in the named JSON file. A marker
asserting a tier or an adoption count is the same design, and would fail the
same way - loudly, at `make check`, naming the file and the line.

**What must not be scripted.** Whether a citation declared `primary` really is
a primary measurement of the quantity, which `check_source_tiers` already
refuses to guess at for the reason `CLAUDE.md` gives; and whether the *rule*
stated in prose matches the practice, which is the judgment `PL-J302` exists
to have made rather than automated. The line is between counting declared
fields and reading a paper.

**The gate this has to pass before it is built.** `CLAUDE.md` asks whether the
work genuinely recurs. The evidence for is that three such claims went stale
inside a single day - the seven data-file restatements `PL-FJGY` swept,
`PL-J302`, and `PL-7KDC` - each found by a session reading the files rather
than by anything that runs. The evidence against is that a marker only checks
the claims somebody remembers to mark, so the next unmarked sentence drifts
exactly as these did, and an unmarked claim is the common case. Decide that
first: if the answer is that marking is what the author will not do, the item
is a different one - a check that reads the *counts* out of the data and
prints them, so a session updating the paragraph has the true numbers in front
of it without having to trust prose.

**Found.** `PL-X19T` (align the tier-3 absolute in the instruction files with
the practice), 2026-09-07, after two stale-count findings in one pass.

**Decision needed.** Which of two mechanisms, and the choice turns on a
prediction about authors rather than on code. Either a `<!-- provenance: ... -->`
-style marker extended to assert a tier or an adoption count, which checks only
the claims somebody remembers to mark; or a command that reads the counts out of
the data files and prints them, so a session updating the paragraph has the true
numbers in front of it and marks nothing. The item's own text names the test:
if marking is what the author will not do, the second is the item.

Re-checked 2026-09-12: `check_prose_provenance` can assert numbers only -
`_lookup` returns `None` for anything that is not an `int` or `float`, and the
marker's value is parsed with `float()`. So a tier string or an `adopted`
boolean is not merely unchecked, it is inexpressible in the existing mechanism,
and either route is a real extension rather than a marker away.

**Why it matters.** Three claims of this shape went stale inside a single day -
`PL-FJGY`'s seven data-file restatements, `PL-J302`, and `PL-7KDC` - and every
one was found by a session reading the files rather than by anything that runs.
The claims sit in `docs/MODEL.md`'s source hierarchy, which is where a reader
goes to decide whether to trust a displayed value, so a stale tier claim reaches
that decision directly.

**Done when.** Either mechanism is built with tests, or the decision is recorded
that neither earns its place and the class is handled by the close-out sweep.

## Decided 2026-09-13: the printing command, not a marker

**Project owner's decision, 2026-09-13.** Of the two mechanisms this item named
- a `<!-- provenance: ... -->`-style marker extended to assert a tier or an
adoption count, or a command that reads the counts out of the data files and
prints them so a session updating the paragraph has the true numbers in front of
it and marks nothing - **the printing command is the item.**

**On this item's own test**, which is "if marking is what the author will not do,
the second is the item." Marking is what does not happen here, on three measured
instances rather than a prediction:

1. `docs/MODEL.md` § "Source hierarchy: what may be cited as the authority for a
   value" records its own failure in the file: the pair of counts that stood
   until 2026-09-13 - 29 rows, 26 tier 3 - "was written when both were true and
   survived two changes that made neither", and it names why, which is that
   "Nothing computed reads them".
2. `docs/resident-instructions.md` opens by naming two files that load at launch
   where `make check` reports three, unmarked and unread by anything (`PL-T9XJ`).
3. `.claude/rules/citing-sources.md` states that thirteen of twenty-six `sources`
   entries name a row, also as unmarked prose (`PL-LM8P`).

All three are hand-maintained counts in prose. None was marked, and a mechanism
that checks only what somebody remembered to mark would have caught none of
them - which is the prediction this item said the choice turned on, now answered
by observation.

**What the command owes its caller**, and it is the judgment half this project
does not script: it prints the counts and never rewrites the sentence. A tool
that edited the paragraph would be guessing at the rounding and the phrasing, and
`CLAUDE.md`'s tooling section refuses exactly that - the same line
`check_provenance` already holds when it reports that a derived figure must be
recomputed and names it rather than recomputing it.

**The `verify:` names `tools/source_tier_counts.py`, and that name is not part of
the decision.** If the counts land as a `doc_check` mode instead, update the
`verify:` with the work. What the command must do is print, from the data files,
the numbers `docs/MODEL.md` § "Source hierarchy" states in prose: the row total
and the per-tier split, and the adopted/not-adopted split.

**Scope note.** This closes the residual that `check_provenance` deliberately
leaves: it "decides that a documented key holds the stated value, never what tier
its source carries." The value half is already guarded in both directions; this
is the tier and adoption half.

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Unchanged, and owner-decided already (project owner, 2026-09-13). The counts
rule in `docs/MODEL.md` § "How this document is held to the tree" cites this
item as the decision it generalises beyond data-file rows.

## Re-confirmed 2026-09-30: changed shape - the per-row split is not in the data files

**The problem is still live, and the class is still producing.**
`docs/MODEL.md` § "Source hierarchy" states, unmarked: "Of the 37 rows in the
provenance table below, 16 are tier 3, one is tier 2, 18 are tier 1, and two
adopt no source of any tier." That is correct today, recounted by hand from the
notes: each agent file has 2 tier-3 rows and 6 tier-1 rows, the reference
patient has 10 tier-3 rows and 1 tier-2 row, and the machine file has 2 rows
with no source. Two more restatements of per-value adoption went stale on
2026-09-13, when `PL-FN5F` adopted Yasuda, Targ and Eger for the nine
tissue:gas coefficients, and nothing caught either one:

- The note openers in all three agent files (`PL-R1VD`, filed 2026-09-30).
- `.claude/rules/sources-and-docstrings.md`, which still said "The twelve
  partition coefficients are De Wolf et al.'s table" and that most stored
  values were lower-tier adoptions. It was corrected in this item's commit,
  since that correction is the same under either answer below.

**What the brief got wrong.** It says that since `PL-1JDD`, a claim of the form
"of the 29 rows, 26 are tier 3" is "answerable by reading the data files". It
is not:

- `tier` and `adopted` are declared per *source entry*, and there are 44.
- A row is a *stored value*, and there are 37: the numeric leaves that
  `check_provenance` holds the table to.
- Which stored value an adopted source is the authority for is written only
  in its note's prose, as in "now the authority for
  blood_gas_partition_coefficient alone" or "Used here as
  max_delivered_concentration_percent".

For example, `desflurane.json` adopts four sources for its eight values: one
tier 3 and three tier 1. Its fields cannot say that two of the eight values are
the tier-3 ones.

So the command chosen on 2026-09-13 cannot print the per-row split from the
files as they stand. What it can print is per-entry counts: 14 adopted (9 tier
1, 1 tier 2, 4 tier 3) and 30 cited but not adopted. No document asks that
question. Parsing the notes for key names would be the tool guessing at prose,
which `CLAUDE.md` refuses.

**Decision needed: how the value-to-source link gets recorded.** The decided
command cannot exist without that link. This does not reopen the
marker-versus-command choice of 2026-09-13, which is dated before the rule that
records a decision's kind, so its kind is unrecorded.

**Recommended: (A) record the link in the data files.**

- **The field.** Every `sources` entry gets an `authority_for` list: the
  dotted key paths of the stored values that entry is the authority for, in
  the same spelling the provenance table and `_leaf_numbers` already use. The
  list is empty exactly when `adopted` is false.
- **The rules, all exact.** The loader enforces them, and `check_source_tiers`
  repeats them so a checkout with no virtualenv still checks them. Each path is
  a numeric leaf of the same file. No leaf has two authorities. `adopted` is
  true exactly when the list is non-empty.
- **The command.** Standard library only, it prints each file's rows with
  their authority and tier, or "no adopted source", then the per-tier split
  `docs/MODEL.md` states. The paragraph then cites it.

Why A is the better route:

- **It puts the fact where `docs/MODEL.md` already says provenance belongs.**
  That document asks for "The tier, on the entry itself ... not a claim in
  prose that a reader has to reconstruct".
- **It becomes the one record** that the MODEL.md paragraph, the rules
  paragraph and the note openers each restate.
- **It is what FAIR principle R1.2 asks of scientific data:** detailed
  provenance attached to the data (Wilkinson MD et al., Sci Data
  2016;3:160018, doi:10.1038/sdata.2016.18).
- **The need recurs.** Per-value adoption has moved three times: on
  2026-09-07 (`PL-8ZJQ`), when the MAC-awake rows arrived, and on 2026-09-13
  (`PL-FN5F`). `ROADMAP.md` planned-milestone item 31, a primary coefficient
  set, would move it again.

What A costs:

- **A schema change.** `_SourcePayload` and `SourceReference` in
  `core/parameters.py` gain the field, and all three `SupportedSchemaVersions`
  windows move from 2 to 3.
- **Data edits.** All five data files take the field on 44 entries, 14 of them
  non-empty, and declare the new version.
- **Tests** in `tests/unit/test_parameters.py`, `tests/unit/test_doc_check.py`
  and `tests/reference/test_sevo_patient.py`, plus the MODEL.md paragraph.
- About one session. No stored value and no equation moves.

**(B) Decline the mechanism.** Date the MODEL.md counts, as the counts rule in
§ "How this document is held to the tree" allows, and build nothing. This
item's own "Done when" admits that outcome. It costs minutes, and the next
adoption change goes stale the same way and is found by reading.

**(C) Considered and not recommended: link from the MODEL.md provenance table
instead.** A fifth column naming each row's source avoids the schema change,
but it puts the fact in prose-bound documentation rather than on the entry.
Naming a source from a table cell also needs one of two things. Fuzzy citation
matching is unreliable: "Eger" appears in four of desflurane's nine citations.
A source `id` field is a schema change after all.

**Fields.** `touches` now names what route A reaches. Under B it shrinks to
`docs/MODEL.md` and the rules file, and the `verify:` changes with it.

**Answered 2026-09-30: route A** (project owner, 2026-09-30, ratified, over B,
dating the MODEL.md counts and building nothing, and C, a provenance-table
column naming each row's source). Being built on this branch. One consequence
found while mapping the entries: each agent file's De Wolf et al. note says it
"is now the authority for blood_gas_partition_coefficient alone", but the same
file's `provenance_gap` and its Nickalls and Mapleson notes name De Wolf as the
source of `mac_percent` too. `authority_for` records both, so that sentence is
corrected with the field, and `PL-R1VD` (the stale Yasuda openers) rides the
same edit.
