---
id: PL-9RLM
title: Commit the 2026-11-10 reverse outline of docs/MODEL.md as docs/prose-review/model-reverse-outline.tsv, one row per paragraph with its reader, kind and best home
priority: P2
effort: S
status: done
classes: docs
feature: model-md-structure
touches: docs/prose-review/model-reverse-outline.tsv, docs/prose-review/README.md
added: 2026-11-10
closed: 2026-11-10
pr: 2088
payoff: the evidence for splitting docs/MODEL.md by reader survives the session that gathered it, so the draft and the decision can start from it
verify: grep -q 'U1721' docs/prose-review/model-reverse-outline.tsv
---

**Problem.** Commit the 2026-11-10 reverse outline of docs/MODEL.md as docs/prose-review/model-reverse-outline.tsv, one row per paragraph with its reader, kind and best home

**Why it matters.** The outline is the evidence behind `PL-P3GZ` (decide
whether to split `docs/MODEL.md` by reader) and the source that `PL-B07T`
(draft a clinician's model description) works from. Until this commit it
existed only in a session's scratch directory, which is deleted with its
container.

**How it was made, 2026-11-10.** The project owner asked for a reverse outline
of the whole document during a read-only review of the copy editor. The
outline describes `docs/MODEL.md` at commit `50af1a2e`, the last commit to
change that file before the review.

1. A script split the file into 1,721 units. A unit is one heading, one code
   block, or one run of lines between blank lines, which is a paragraph, a
   list or a table. The script recorded each unit's first and last line, its
   word count and the headings above it. Headings aside, the units hold
   129,170 words.
2. Seven model readers each labelled one seventh of the units, in one pass,
   with no second rater. Each label is therefore a judgement to check and not
   a measurement. The session spot-checked the labels of § "Reset behavior"
   and found them sensible.
3. Each reader gave every unit a reader, a kind, a best home, its point in
   one line, and the earlier unit it repeats, if any. A reader saw only its
   own seventh, so a repeat of a unit in a distant chapter is not recorded.

The columns of `docs/prose-review/model-reverse-outline.tsv`:

- `unit`, `first_line`, `last_line`, `words`, `type` and `section` come from
  the script. `section` is the unit's headings from level 2 down, joined by
  " > ".
- `reader` is who needs the unit: a clinician, a developer, or nobody but the
  project's own upkeep.
- `kind` is what the unit is: model, limitation or hazard, parameter source,
  numerical method, interface requirement, interface rationale, test
  description, validation against data, implementation detail, decision
  history, or about the document.
- `best_home` is where the unit would best live: a model description for a
  clinician, an interface requirements list, a verification and validation
  report, a parameter source register, the code (a docstring or a test), the
  item record, or nowhere (cut).
- `point` is the unit's point in one line, and `repeats_unit` names the
  earlier unit it repeats.

**What it found.** Words by best home: verification and validation report
29,975 (23%), code 23,578 (18%), interface requirements 22,665 (18%), item
record 22,073 (17%), model description 16,792 (13%), parameter source
register 11,370 (9%), cut 2,717 (2%). Words by reader: developer 92,473
(72%), clinician 29,711 (23%), project upkeep 6,986 (5%). 203 units (14,243
words) repeat an earlier unit.

**Done when.** `docs/prose-review/model-reverse-outline.tsv` is on `main`
with one row for each of the 1,721 units, and `docs/prose-review/README.md`
says what the file is.

**Generator check.** Work the owner asked for. The outline measures the
mechanism that `PL-J1ZM` (sessions over-explain in every kind of text)
records, and `PL-P3GZ` carries what it adds to that record.
