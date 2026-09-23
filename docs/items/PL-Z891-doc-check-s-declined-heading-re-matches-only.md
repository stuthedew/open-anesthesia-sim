---
id: PL-Z891
title: doc_check's DECLINED_HEADING_RE matches only '### Declined to Gate', so a disposition the roadmap records under '### Sequenced past vX.Y.Z ...' or '### Deferred to vX.Y.Z ...' is not read and check_gate_dispositions reports its open debt items as owed
priority: P3
effort: S
status: done
classes: defect, infra
feature: gate-list-integrity
milestone: v0.5.4
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-2JRC's triage pass
added: 2026-09-21
closed: 2026-09-22
pr: 891
payoff: A gate disposition recorded under any heading the roadmap actually writes is read, so check_gate_dispositions stops reporting answered items as owed and the gate block stays worth reading.
verify: grep -q 'def test_a_sequenced_past_heading_is_read_as_a_disposition' tests/unit/test_doc_check.py
---

**Problem.** doc_check's DECLINED_HEADING_RE matches only '### Declined to Gate', so a disposition the roadmap records under '### Sequenced past vX.Y.Z ...' or '### Deferred to vX.Y.Z ...' is not read and check_gate_dispositions reports its open debt items as owed

**Found 2026-09-21 while closing `PL-H6VQ`**, which measured the opposite
direction of the same function and left this one alone: it reads too *little*
rather than too much, and wants its own item.

**Where.** `tools/doc_check.py`'s `DECLINED_HEADING_RE`, `^###\s+Declined to
Gate\b`, which `_declined_ids` matches each subsection heading against.

**Measured 2026-09-21.** `ROADMAP.md`'s v0.5.0 section carries four disposition
subsections and the pattern matches two of them. `### Sequenced past v0.5.0, so
not clearable before it begins` names 39 ids, of which `PL-TH35` and `PL-WZVZ`
are open debt; `### Deferred to v0.4.26, because the port dissolves the defect`
names one, closed. Neither heading is read, so those dispositions count for
nothing.

**Not live, and that is the reason it is not urgent rather than a reason to
drop it.** The current gate is v0.6.0, whose section carries no disposition
subsection of any form, so nothing is being mis-read today. It becomes live the
first time a gate records a deferral under a heading that does not use the
words "Declined to Gate" — and the failure is a false red, naming items that do
have a written disposition, which is the safe direction but still a wrong
answer from the apparatus.

**Why it matters.** `check_gate_dispositions` exists so that an open debt item
carrying a written disposition is not reported as owed. Where the heading does
not use the words "Declined to Gate" the disposition counts for nothing, and
the check names items the roadmap has already answered - a false red from the
apparatus, which is the direction that trains a session to skim the gate block
where a real one is printed. The v0.5.0 section is the measured instance: 40
ids across two subsections read as absent, `PL-TH35` and `PL-WZVZ` among them
still open. It is latent only because the current gate happens to carry no
disposition subsection of any form, so the next gate that records one under a
heading of its own makes it live with nothing warning that it has.

**Done when** `_declined_ids` reads every disposition subsection the roadmap
actually writes, or `ROADMAP.md` § "The debt gate" § "Recording it" fixes one
heading form and the check enforces it.

**Closed 2026-09-22 by widening the reader, not by fixing one heading form.**
"Done when" offered both. Fixing the form would have had to constrain the whole
heading, because the ground for a deferral is what the heading carries and no
two grounds are worded alike — so the rule would have been the narrow one
arriving again one word to the right, and it would have meant rewriting two
headings in a completed milestone's record to satisfy a check. Widening reads
what the roadmap already wrote and costs nothing already written.

What is fixed instead is the *verb*: `DEFERRAL_VERBS = ("Declined", "Deferred",
"Sequenced")` in `tools/doc_check.py`, with free prose after it.
`ROADMAP.md` § "Recording it" states the three and says that a fourth is an
edit to that tuple in the same change.

**The open vocabulary is made safe by the error naming itself.** A fourth verb
still goes unread, and the reason that was worth another paragraph rather than
a shrug is that the old failure pointed the wrong way: the ids came back as
debt the gate owed, under an error prescribing the `### Declined to Gate ...`
subsection the reader had already written. `_deferral_headings()` renders the
recognized forms from the same tuple the pattern is built from, so the error
now names all three and a fourth verb diagnoses itself in one read.
`test_the_disposition_error_names_every_heading_form_it_reads` pins that.

**Measured 2026-09-22 against the real roadmap.** The narrow pattern left two
subsections unread, both under v0.5.0: `### Deferred to v0.4.26, because the
port dissolves the defect` (1 id, closed) and `### Sequenced past v0.5.0, so
not clearable before it begins` (40 ids, of which `PL-TH35` and `PL-WZVZ` are
still open debt). The three it already read — v0.5.0's two `Declined` ones and
v0.6.0's — are unchanged, so `make check` gives the same answer before and
after and the fix lands with no gate movement to review.

**One thing the item did not record, found while fixing it.** v0.6.0's
deferral subsection says in its own entry for this item that it "was written to
match the pattern deliberately". The constraint was being routed around by the
author it constrained rather than merely being latent, which is `CLAUDE.md`'s
second test for friction that compounds.

**Two names kept deliberately.** `DECLINED_HEADING_RE` now matches three verbs
and `_declined_ids` reads all of them, so both names are narrower than what
they do. Renaming was refused on the record rather than on taste: `_declined_ids`
is named in seven `ROADMAP.md` lines, in `docs/releases/v0.4.35.md` and
`docs/releases/v0.5.1.md`, and in three pull request bodies, and
`DECLINED_HEADING_RE` in v0.6.0's own deferral entry for this item. Those
sentences are true about the day they were written, and a rename would leave a
dozen of them naming a symbol that does not exist. The comment above the
pattern says so.
