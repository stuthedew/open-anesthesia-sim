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

## Design round 2026-10-03: recommendation

**Re-checked against the tree, 2026-10-03.** The corpus has grown from 187
files to 265, because `tools/pr_body_check.py --recover` writes one for each
squash commit that lost its body, in a batch at each release (`PL-3PH2`). Every
file opens with front matter `write_recovery` emits - `pr`, `recovered`,
`commit`, `merged`, `items`, `subject`, `squash` - and `recovered:` is the fetch
date, so `PL-73G8`'s half has landed; there is no `README.md`. Nothing reads a
record as current: `subprojects/docket/src/docket/arming.py` and `claims.py`
name the directory as `RECORDS`, `docket.toml` places it in `workflow_paths` as
"the pull-request record `tools/pr_body_check.py` writes", and
`tools/doc_check.py`'s `DOC_GLOBS` is `docs/*.md`, one level only, so the
directory is outside the citation sweep rather than excluded by name. No tool,
check or workflow cites a record as the authority for a present-day fact.
Angle-bracket placeholders now sit in 11 files, 16 of them (`<id>` three
times, `<ref>`, `<path>` and `<n>` twice each, seven singletons); the dead-path
and dead-sha counts were not retaken, since the answer does not turn on them.
`recovered()` lists only digit-named files, so a `README.md` beside the records
is safe for the tool.

**Q. Historical records, or current documentation?**
**Recommendation: historical records - the filed recommendation stands - and
one statement, met in both of the places a reader arrives by.** A one-paragraph
`docs/pr-bodies/README.md`, which a GitHub directory visitor meets, and one
header line in every record, which `cat` meets: written by `write_recovery`
for new records and backfilled once by a script across the 265 existing ones,
one commit a reviewer reads as a single diff. The statement says what a record
is: the body as GitHub served it on `recovered:`, verbatim; its citations
describe the tree at `merged:` and are not maintained; an angle-bracket
placeholder in it renders invisibly on GitHub. No citation is repaired - the
drift is not a finding, by the rule `.claude/rules/citation-drift.md` already
applies to a closed brief - and `tools/doc_check.py` stays outside the
directory by design, which the README records so the next reader does not
re-derive it. Size S rather than M. The README-only variant is cheaper and was
refused because a reader who opens a record directly never meets it, which is
what "Done when" asks for.

**What would change the answer.** Any reader - a tool, a check, a documented
workflow - that cites a record as current. None exists; one would make the
corpus documentation and flip this.
