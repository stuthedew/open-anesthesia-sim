---
id: PL-C4F0
title: bin/docket inflow still lists PL-61FT under 'a generator whose fix did not hold' though the owner answered it 'no successor head' on 2026-10-12 (PL-4097, ratified): an answer naming no successor lives only in prose, so PL-0WT0's successor split cannot see it and every run re-asks it
priority: P2
effort: M
status: done
classes: defect
feature: generator-heads
milestone: v0.5.29
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
closed: 2026-10-18
pr: 1603
payoff: bin/docket inflow stops re-asking PL-61FT's line, which the owner answered, so its 'fix did not hold' heading lists only the lines still waiting for an answer
verify: grep -q 'def test_a_line_answered_with_no_successor_is_listed_apart' subprojects/docket/tests/test_inflow.py
---

**Problem.** bin/docket inflow still lists PL-61FT under 'a generator whose fix did not hold' though the owner answered it 'no successor head' on 2026-10-12 (PL-4097, ratified): an answer naming no successor lives only in prose, so PL-0WT0's successor split cannot see it and every run re-asks it

**Reproduced 2026-10-17.** `bin/docket inflow --no-fetch` prints, under
"Re-entered by three or more filings, a generator whose fix did not hold",
`PL-61FT  by PL-VM7C, PL-0FGH, PL-ZS13, PL-GZXY, PL-P95F, PL-RC4S, PL-6X0C,
PL-CDZ8`, beside `PL-0HPV`'s line. `inflow.analyze` fills `successors` only
from items `model.is_generator` accepts whose `reenters:` names the line, and
`PL-4097`'s "**Answered 2026-10-12 for `PL-61FT`: no successor head**" is a
paragraph in a brief, which nothing in `inflow.py` reads. Its eighth filing,
`PL-CDZ8` (added 2026-10-11), is one the owner's answer names as covered.
Filed in the commit that closed `PL-0WT0` (#1459), whose Done-when covered
successor heads only: this is the other kind of answer, left outside that
scope on purpose rather than missed by its fix.

**Why it matters.** The list is where `CLAUDE.md` § "What this project is"
expects a generator still producing to be found, and it re-asks a question the
owner has answered on every run: a session either re-derives `PL-4097`'s
reasoning or learns to skim the heading, which is where `PL-0HPV`'s genuinely
open line (`PL-SH4H`) sits. An answer that lives only in prose is also the
next session's to reconstruct, which is the failure `PL-4097` itself was.

**Not `impairs-generators:`, and why.** The defect over-reports a settled line;
it hides no generator and misranks none, so the reason the generator tier
exists - "while identification is broken a generator is never recorded" - is
not met. `PL-0WT0`, the same shape for the successor-head half, was triaged
`P2` `defect` on 2026-10-12 without it. Under `CLAUDE.md`'s generator pause it
needs no lift either way: what the finding machinery records is named there as
work the pause is for (`PL-5MYR`), so a field for the answer is not a new
workflow mechanism of the kind the pause holds.

**Done when.** A "none owed" answer to a re-entered line is a record in the
store, not prose: the item that gives it names the line in a front-matter
field `bin/docket inflow` reads (the field's name and home are the building
session's call - **recommended:** on the answering item, so the record carries
its own date and closing it does not rewrite the closed head). `inflow` lists
such a line apart from "a generator whose fix did not hold", naming the
answering item and its status, as `PL-0WT0` does for a successor; a line that
three or more filings re-enter *after* the answer's date prints under the
open heading again, so the record cannot silence a mechanism that resumes
(the three-post-close rule applied to the answer). `PL-4097`'s answer for
`PL-61FT` is written in that record, so `bin/docket inflow` no longer prints
`PL-61FT` under the open heading; the README's account of the list says so; and
`subprojects/docket/tests/test_inflow.py` gains
`test_a_line_answered_with_no_successor_is_listed_apart`, covering the listing
apart and the re-opening after three later filings.

**Generator check.** A follow-on, not an instance or a re-entry: the fact is
how a re-entered line is answered - its successor head, or the recorded reason
none is owed. `PL-4097` and `PL-0WT0` met the successor half and `PL-4097`
wrote that record; this item writes the other half, so it completes the one
record rather than adding a third reader beside it, and no head's `misread:`
states the fact (`bin/docket generators --misread`, 2026-10-17). `PL-0WT0` was
the narrower fix by its own Done-when, so `reenters:` is not set.

**Closed 2026-10-18.** The field is `no-successor:` on the answering item, as
recommended, and `bin/docket set --no-successor` writes it. The answer dates
from the answering item's `added:`. The review found that dating it from
`closed:` let closing the item hide filings made in between, and `added:` is
the conservative choice: it can only reopen a line sooner.
`inflow.Inflow.answered` holds each answered line, and `format_inflow` lists
it under a third heading naming the answering item. `PL-4097` carries
`no-successor: PL-61FT`, and on that day `bin/docket inflow --no-fetch` lists
`PL-61FT` under the new heading and prints no open heading at all. No check
holds the field's ids to real items: an id that names no re-entered line has
no effect, which `bin/docket inflow` shows by not listing it.
