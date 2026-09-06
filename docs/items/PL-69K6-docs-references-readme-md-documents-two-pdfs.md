---
id: PL-69K6
title: docs/references/README.md documents two PDFs the copyright purge removed, and doc_check does not verify that a documented reference file exists
priority: P2
effort: S
status: done
classes: docs, defect
feature: provenance
milestone: v0.4.5
touches: docs/references, tools/doc_check.py
added: 2026-09-06
closed: 2026-09-06
pr: 389
verify: python3 tools/doc_check.py check && grep -q 'def _check_reference_files_exist' tools/doc_check.py
---

**Problem.** The 2026-09-06 history rewrite removed
`baker-farmery-2011-inert-gas-transport-in-blood-and-tissues.pdf` and
`schuttler-schwilden-2008-modern-anesthetics-hep-182.pdf` from the repository.
`docs/references/README.md` went on carrying a full entry for each - filename,
citation block and provenance note - and its "Redistribution" section still
said the repository was private and that the two "must come out before this
repository is ever made public", both of which had stopped being true. A reader
was told the repository holds two files it does not.

**Why it matters.** `CLAUDE.md` treats stale documentation as a safety issue
rather than tidiness, and this is the sharper form of it: the README is the
provenance record for the model's own sources. A reader following it to check
where a compartment structure or a coefficient came from finds nothing, and
cannot tell a deliberate removal from an accidental one - which is exactly the
question a provenance record exists to answer.

**The decision, and it was not the obvious one** (project owner, 2026-09-06).
The recommendation put to the owner was to delete both entries outright. The
answer was to keep them: *"I'm ok with referring to these papers that were
removed as citations when appropriate."* That is the correct distinction and a
better answer than the one proposed - **citing a work is not redistributing
it**, so what had to go was the claim to hold the file, not the bibliographic
record. The README had in fact anticipated this: it already said the citations
"are the part that survives such a removal, which is why they are recorded in
full here and not left implicit in the filenames".

**Correction to this brief as first written.** It claimed the remaining M4
paper "records no licence or redistribution basis". That was wrong, and came
from reading one section rather than the file: the entry stated CC BY-NC-ND
3.0 from the paper's own first page, and the "Redistribution" section already
called it the one file that could stay if the repository were made public.
Nothing about the M4 entry needed correcting on those grounds.

**The prose half, by `#388`.** Both entries now read "Not held here" with the
date and the reason and keep their citations, the "Redistribution" section is
rewritten for a public repository, and the M4 entry no longer describes itself
in the future tense as the one file that *may* stay. Two sessions fixed this
prose independently and `#388` merged first, so its wording stands; the line
numbers cited above were taken before it and no longer resolve.

**The check half, by this branch.** `tools/doc_check.py` gains
`_check_reference_files_exist`: a filename named as inline code in
`docs/references/README.md` must be present in `docs/references/`. An entry
naming no file passes, which is the shape a citation-only entry takes - so the
judgment half, whether an entry should keep its file or only its citation,
stays with a person and only the decidable half is automated.

Confirmed against `#388`'s README rather than against the version it replaced:
it reports 0 errors as written, and reintroducing either removed filename
produces the error naming the file and the remedy. That is what closes this
item - the prose was fixed twice, but a fix nothing enforces is the state this
item exists to end.

**Where.** `docs/references/README.md`; `tools/doc_check.py`
(`REFERENCE_FILE_RE`, `_check_reference_files_exist`, and its call in
`analyze`).

**Done when.** The README describes only files the repository holds, the
citations survive, and `doc_check` fails when an entry names an absent file -
so the next removal cannot leave the provenance record asserting something
untrue. Done.
