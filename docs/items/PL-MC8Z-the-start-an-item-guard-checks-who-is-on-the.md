---
id: PL-MC8Z
title: The start-an-item guard checks who is on the item but never what files it touches, so overlap is found at merge
priority: P2
effort: S
status: ready
classes: infra
feature: parallel-sessions
touches: .claude/skills/docket/SKILL.md
added: 2026-09-02
verify: python3 tools/doc_check.py check && grep -qF 'is another session in these files' .claude/skills/docket/SKILL.md
---

**Problem.** The `docket` skill's "Mode: start an item" is a three-step guard —
`git fetch origin`, then `bin/docket show <id>`, then the `list_sessions` scan
— and all three answer the same question: *is another session on this item?*
None of them asks the other question, *is another session in these files?*,
even though `bin/docket concurrent <id>` already answers it and needs no
argument the session does not have.

**Observed 2026-09-02.** Two sessions worked `PL-P0QT` and `PL-2XTF`/`PL-SVRW`
concurrently. The guard behaved correctly at every step: different items, so
nothing was in flight, and neither session should have yielded. Both branches
then edited `subprojects/docket/src/docket/vcs.py` and
`subprojects/docket/tests/test_vcs.py`. `bin/docket concurrent PL-P0QT` listed
`PL-2XTF` under "Cannot run alongside" the whole time, and neither session ran
it, because nothing in the guard says to.

**Why it matters, and what it is not.** This is the cheap end of the problem
`PL-D4MZ` (nothing reserves work when it is recommended) covers, and it needs
no new mechanism at all — the command exists, is already documented under
"Mode: work several items at once", and is simply never reached from the mode
that would use it. `docket next` is not a substitute: the owner naming an item
directly skips `next` entirely, which is the same gap `PL-5KR2` closed for the
in-flight read and left open for this one.

It is not `PL-YHD3` (which of two sessions yields). Nothing here should yield:
two unrelated items legitimately touch one file, and the right outcome is that
both proceed knowing it, and the second to merge resolves deliberately rather
than discovering it.

**Where.** `.claude/skills/docket/SKILL.md`, "Mode: start an item". One line in
the existing guard, plus what to do with a non-empty answer — which is the part
worth thinking about, since the honest answer is usually "proceed, and expect
to resolve", not "pick something else".

Note that `concurrent` reports declared overlap only: an item with no `touches`
is unanalysed rather than safe, and the skill already says to report what it
rules out rather than what it certifies. A guard step that reads as a clean
bill of health would be worse than none.

**Done when.** The start-an-item guard names the file-overlap question, and
says what a session does with the answer.
