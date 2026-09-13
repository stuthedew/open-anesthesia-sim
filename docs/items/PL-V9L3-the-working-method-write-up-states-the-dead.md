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
