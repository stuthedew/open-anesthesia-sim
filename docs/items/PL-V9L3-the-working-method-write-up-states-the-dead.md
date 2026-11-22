---
id: PL-V9L3
title: The working-method write-up states the dead-ends startup tier as live and dates its instrumentation to last week, when both sit unmerged on a branch
priority: P2
effort: S
status: ready
classes: docs
feature: public-history
added: 2026-09-13
not-delegable: the edit is to a published artifact outside this repository, which only its holder can change; nothing in this tree changes, so no command here can prove it
---

**Problem.** The working-method write-up (the "Coordinating Agents Through
Git" artifact, published 2026-09-13 from `claude/optimistic-mayer-sx57dq`;
`PL-928V` is the item behind it) closes with a paragraph describing the
dead-ends record in the present tense - "nine lines, about 2 KB, emitted at the
start of every session" - and dates its read-side instrumentation to "last
week". Neither holds. The whole mechanism (`docs/dead-ends.md`,
`tools/dead_ends.py`, the `docket-digest.sh` emit, `.claude/hooks/item_read_log.py`)
was committed on `claude/hopeful-allen-tetrje` on 2026-09-13 and reached no
session until `#527` merges. Verified by a session whose own `SessionStart`
digest carried no dead-ends block.
<!-- absent: .claude/hooks/item_read_log.py -->

**Why it matters.** The piece's stated position is that its numbers are
attached so the claims can be checked rather than taken. Two checkable claims
in its closing paragraph are wrong in the direction that flatters the project -
a mechanism reported as running that is running nowhere, and a date placing it
a week earlier than its commits. It is also the paragraph a reader is most
likely to act on, because it is the one offering the untested part honestly.

**Disposition.** Fix the tense and the date once `#527` lands, or reword to
"built, not yet merged" if it is published before then. Whoever holds the
artifact has to make the edit; this item is the record that it is owed.
**Done when.** The artifact's closing paragraph states the dead-ends tier's
status and its date correctly.

**Re-checked 2026-09-13, after the merge, because half of this has changed.**
The mechanism is now on `main` - `docs/dead-ends.md`, `tools/dead_ends.py` and
`.claude/hooks/item_read_log.py` are all present in the default branch, and this
session's own `SessionStart` digest carried the dead-ends block. So the
present-tense claim has become true since publication. The date claim has not:
the commits are 2026-09-13, not "last week". What is left is therefore the date,
plus a judgment the holder has to make - whether a claim that was false when
published and is true now is repaired by a silent edit or wants a line saying
so, given that the piece's stated position is that its numbers are attached to
be checked.
<!-- absent: .claude/hooks/item_read_log.py -->

**Re-checked 2026-11-11: the artifact can be edited from a session, and its
closing paragraph is now out of date in three ways.** It is the project owner's
own artifact, "Coordinating Agents Through Git"
(https://claude.ai/artifact/WXRgVEHTqSj9JiV4oQxGAd), last updated 2026-09-13
and private. It is not among the Projects trial's artifacts, but a session's
Artifact tool lists it as his and can read and republish it, so the edit does
not need him to make it by hand. A read on 2026-11-11 found the closing
paragraph unchanged since publication:

1. "The instrumentation went in last week and has no data yet." The
   instrumentation merged on 2026-09-13 in `#527`, the day the page was
   published.
2. The same instrumentation was removed on 2026-11-03 by `PL-3HQ6` (`#1989`),
   which found that it served no open decision. So the question the paragraph
   leaves open, whether the record is ever read, was never answered by it.
3. "nine lines, about 2 KB": the dead-ends record printed at session start now
   holds five entries.

What is left is the project owner's call, because the page is his own writing:
whether to edit it, and whether an edit carries a dated line saying what
changed. **Recommended:** a visible dated correction, because the page's own
position is that its numbers are attached to be checked. The item stays open
until he decides.

**Checked 2026-11-22** against `d4e8200`: still applies, and the remaining choice is the owner's. A read of the artifact on 2026-11-22 found its closing paragraph unchanged: it still says "nine lines, about 2 KB" and "The instrumentation went in last week and has no data yet." Today `tools/dead_ends.py emit` prints 7 lines and 2,249 bytes at session start. The read-side instrumentation is still gone since `PL-3HQ6`.

**Decision needed.** How to correct the owner's published write-up, whose closing paragraph still says the dead-ends instrumentation "went in last week", though it merged the day the page was published and was removed on 2026-11-03. **Recommendation:** a visible, dated correction rather than a silent edit, because readers may already have relied on the paragraph. Put to the owner on 2026-11-22.

**Answered 2026-11-22 (project owner, 2026-11-22, ratified, over a silent edit).** The owner asked that each item needing him be settled by standard practice. The write-up gets a visible, dated correction. The ICMJE recommendations on corrections and version control (https://icmje.acponline.org/recommendations/browse/publishing-and-editorial-issues/corrections-and-version-control.html, read 2026-11-22) say that a journal "should publish a correction notice as soon as possible detailing changes from and citing the original publication", and "should post a new article version with details of the changes from the original version and the date(s) on which the changes were made". The page is not a journal article, but its closing paragraph offers checkable numbers, and that is the case those rules are written for.

**Done when, as answered.** The artifact's closing paragraph states the instrumentation's dates and removal and the dead-ends record's present size correctly, and a dated line under it says what changed from the version of 2026-09-13.
