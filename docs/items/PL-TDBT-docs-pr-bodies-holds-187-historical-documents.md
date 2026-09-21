---
id: PL-TDBT
title: docs/pr-bodies holds 187 historical documents that read as current: 21 cited paths no longer exist, 30 cite an unresolvable sha, and 22 angle-bracket placeholders in 15 files vanish in GitHub's own blob view, with doc_check blind to all of it by design
priority: P3
effort: M
status: needs-decision
classes: docs, infra
feature: pr-body-integrity
touches: docs/pr-bodies
added: 2026-09-20
---

**Problem.** docs/pr-bodies holds 187 historical documents that read as current: 21 cited paths no longer exist, 30 cite an unresolvable sha, and 22 angle-bracket placeholders in 15 files vanish in GitHub's own blob view, with doc_check blind to all of it by design

**Why it matters.** The corpus reads as current documentation and is indexed
as such: 187 files under `docs/pr-bodies/` with no statement that they are a
point-in-time archive, 21 citing paths that no longer exist, 30 citing an
unresolvable sha, and 22 angle-bracket placeholders across 15 files that vanish
in GitHub's own blob view. A session or a reader who opens one to answer "what
did this change do" gets a document whose citations resolve to nothing, with
nothing on the page saying why. `tools/doc_check.py` is blind to all of it by
design - the corpus is excluded from the citation sweep - so the one mechanism
that would ordinarily catch a dead path here is the one mechanism that has been
told not to look.

**Done when.** `docs/pr-bodies/` says what it is in a place every reader of a
file in it will meet, and the disposition of the individual defects - repair,
leave, or declare out of scope - is recorded once rather than left to whoever
next opens one.

**Decision needed.** Whether these 187 documents are historical records, in
which case their drift is not a finding and the whole fix is one statement
saying so, or current documentation, in which case 73 individual defects are
owed repairs.

**Recommended:** historical records, and one statement. This is exactly the
question `.claude/rules/citation-drift.md` answered for closed item briefs -
"a closed item's brief is a historical record, not a live assertion ... drift
in a `done` or `dropped` brief is **not a finding**" - and a merged pull
request's body has the identical property: it says what was true at merge, and
the tree has moved since. Extending that reading here costs a `README.md` in
`docs/pr-bodies/` and the per-file header wording `PL-73G8` is already
repairing; repairing 73 citations in 187 archived documents buys nobody
anything and has to be redone every time the tree moves again. Keep `PL-73G8`
separate: making *new* recovery files honest about when they were fetched is
live work whichever way this goes.

**What would change the answer.** Anything that reads these files as current -
a tool, a check, or a documented workflow that cites one as the authority for a
present-day fact. None is known; if one exists, the corpus is documentation and
the answer flips.
