---
id: PL-Z891
title: doc_check's DECLINED_HEADING_RE matches only '### Declined to Gate', so a disposition the roadmap records under '### Sequenced past vX.Y.Z ...' or '### Deferred to vX.Y.Z ...' is not read and check_gate_dispositions reports its open debt items as owed
status: untriaged
feature: gate-list-integrity
added: 2026-09-21
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

**Done when** `_declined_ids` reads every disposition subsection the roadmap
actually writes, or `ROADMAP.md` § "The debt gate" § "Recording it" fixes one
heading form and the check enforces it.
