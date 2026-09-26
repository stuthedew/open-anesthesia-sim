---
id: PL-M0Q6
title: subprojects/docket/README.md says FlightReport.editing names, per item, a ref that changed the item's file; since PL-1X2C it names every such ref, and show and triage leave the reader's own branch out, which the paragraph does not say
status: untriaged
added: 2026-09-26
---

**Problem.** subprojects/docket/README.md says FlightReport.editing names, per item, a ref that changed the item's file; since PL-1X2C it names every such ref, and show and triage leave the reader's own branch out, which the paragraph does not say

**Found 2026-09-26** in `PL-1X2C`'s docs sweep. `subprojects/docket/README.md`
(the paragraph opening "So `FlightReport.editing` names, per item, a ref that
has changed that item's own file") still reads as one ref per item. Since
`PL-1X2C`, `claims._editing` keeps every carrier per item, and `cli._elsewhere`
drops the reader's own branch before `show` and `triage` print them. The
README was outside `PL-1X2C`'s `touches`, so it was not edited there.

**Why it matters.** The sentence is not false, since each named ref did change
the file. But a reader of the README would expect one branch per item and would
not learn that the reader's own branch is left out. That is the reading
`PL-1X2C` fixed in the output.

**Done when.** The paragraph says every ref is named, per item, and that `show`
and `triage` leave out the branch the reader is on.
