---
id: PL-M0Q6
title: subprojects/docket/README.md says FlightReport.editing names, per item, a ref that changed the item's file; since PL-1X2C it names every such ref, and show and triage leave the reader's own branch out, which the paragraph does not say
priority: P3
effort: S
status: done
classes: docs
feature: carrier-detection
touches: subprojects/docket/README.md
added: 2026-09-26
closed: 2026-09-26
pr: 1061
payoff: a README reader expects every branch that edited an item's file to be named and knows show and triage leave out their own, matching what those commands print
verify: grep -qF '_elsewhere' subprojects/docket/README.md && ! grep -qF 'names, per item, a ref that has changed' subprojects/docket/README.md
---

**Problem.** subprojects/docket/README.md says FlightReport.editing names, per item, a ref that changed the item's file; since PL-1X2C it names every such ref, and show and triage leave the reader's own branch out, which the paragraph does not say

**Found 2026-09-26** in `PL-1X2C`'s docs sweep. `subprojects/docket/README.md`
(the paragraph opening "So `FlightReport.editing` names, per item, a ref that
has changed that item's own file") still reads as one ref per item. Since
`PL-1X2C`, `claims._editing` keeps every carrier per item, and `cli._elsewhere`
drops the reader's own branch before `show` and `triage` print them. The
README was outside `PL-1X2C`'s `touches`, so it was not edited there.

**Reproduced 2026-09-26** on `78b1a02b`: the paragraph still reads "names, per
item, a ref that has changed". `claims._editing`'s docstring says "Every branch
whose edit survives is reported", and `cli._elsewhere` removes `Holdings.head`
before `show` and `triage` print. The README does not mention `_elsewhere`
anywhere.

**Why it matters.** The sentence is not false, since each named ref did change
the file. But a reader of the README would expect one branch per item and would
not learn that the reader's own branch is left out. That is the reading
`PL-1X2C` fixed in the output.

**Done when.** The paragraph says every ref is named, per item, and that `show`
and `triage` leave out the branch the reader is on, naming `cli._elsewhere` as
what does.

**Generator check.** A one-off, which the close-out docs sweep caught as
designed. The fact misread is the link between a document sentence and the
tree fact it restates (`PL-4FBP`, `PL-G424`, both closed 2026-09-19), but
neither head's route claims this kind. `PL-4FBP` leaves a claim outside a
bound family to the close-out sweep "by decision rather than by oversight".
`PL-G424` leaves prose drift that is not a citation to judgment and the
capture rule, on purpose. `doc_check` decides whether a cited path exists,
never whether the sentence around it is still true.

**Worked.** Still true on `17c9f3ed` when picked up: the paragraph read "names,
per item, a ref that has changed". It now says every ref is named, with
`PL-1X2C`'s reason (keeping only the first left out the one that would
collide), and that `show` and `triage` leave out the reader's own branch
through `cli._elsewhere`. One clause the brief did not ask for: the paragraph
also says the measurement itself keeps that branch, as `claims._editing`'s
docstring does, so a reader of `FlightReport` directly is not told otherwise.
