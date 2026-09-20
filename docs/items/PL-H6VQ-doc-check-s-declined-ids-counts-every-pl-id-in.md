---
id: PL-H6VQ
title: doc_check's _declined_ids counts every PL- id in a Declined-to-Gate subsection, including ids the deferral's prose only cites, so an item mentioned in another item's reasoning reads as disposed and check_gate_dispositions goes silent on it
status: untriaged
added: 2026-09-20
---

**Problem.** doc_check's _declined_ids counts every PL- id in a Declined-to-Gate subsection, including ids the deferral's prose only cites, so an item mentioned in another item's reasoning reads as disposed and check_gate_dispositions goes silent on it

**Found 2026-09-20 while closing `PL-82B0`**, which fixed the adjacent defect
(only the first subsection was read) and left this one untouched deliberately:
it is a different question about the same function and wanted its own item.

**Where.** `tools/doc_check.py`'s `_declined_ids`, the
`re.findall(r"PL-[A-Z0-9]{4}", ...)` over each subsection's whole text.

**Measured 2026-09-20.** The one `### Declined to Gate ...` subsection in
`ROADMAP.md` holds 103 `- PL-` entry lines and mentions 385 distinct ids across
its prose. Every one of those 385 is returned as deferred, so an id a deferral
merely cites - as a cause, a precedent, or the item a ground was argued from -
is counted as having a recorded disposition it does not have.

**Why it matters, and why the direction is the safe one.** `PL-HJZW` made a
missing disposition a hard error rather than an advisory, so an id wrongly read
as disposed makes the check go quiet rather than fail: the failure mode is an
item silently escaping the gate's disposition rule, not a false red. That is
the safer direction and still a silent wrong answer, which is the shape
`CLAUDE.md` names first among its compounding-friction tests.

**Not urgent, and here is why.** The over-broad read only matters for an id
that is *open debt* and cited in the subsection without an entry of its own.
Nobody has counted how many that is; that count is the first thing to run, and
it decides whether this is a real gap or a theoretical one.

**Done when.** The count above has been run; and either `_declined_ids` reads
only the entry lines - `^- PL-XXXX` - with the prose left to explain rather than
to dispose, or the item records why reading the prose is right.

