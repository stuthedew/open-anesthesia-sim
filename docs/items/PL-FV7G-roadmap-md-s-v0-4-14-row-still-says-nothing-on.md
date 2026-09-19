---
id: PL-FV7G
title: ROADMAP.md's v0.4.14 row still says nothing on the documented close-out path names verify --self, which PL-7XTS made false
priority: P3
effort: S
status: ready
classes: docs
feature: release-roadmap-seam
touches: ROADMAP.md
added: 2026-09-15
verify: python3 tools/doc_check.py check && ! grep -qF 'names that mode yet' ROADMAP.md
---

**Problem.** ROADMAP.md's v0.4.14 row still says nothing on the documented close-out path names verify --self, which PL-7XTS made false

**Found 2026-09-15**, in `PL-7XTS`'s own close-out doc sweep.

`ROADMAP.md`'s `v0.4.14` row reads: "two shapes are exempt unconditionally, the
other three only under the new opt-in `verify --self`, and nothing on the
documented close-out path names that mode yet - `PL-7XTS` was filed in this
range to say so."

`PL-7XTS` landed step 5 of the `docket` skill's "Mode: close out an item",
which names `bin/docket verify --self <id>`. So the clause is now false as a
statement about the tree, and the forward reference to `PL-7XTS` resolves to a
closed item.

**The judgment this needs is whether a release row is history or current
state.** Read as "as of v0.4.14", the sentence is true and should not be
touched; read as a statement about the repository, it is stale. The word "yet"
is what makes it read as the second. Every other clause in that row is plainly
historical, so past-tensing this one - "nothing on the documented close-out
path named that mode, and `PL-7XTS` was filed in this range to say so" - keeps
the history and removes the live claim.

`tools/doc_check.py` cannot decide this: the citation resolves and the prose is
internally consistent. It is exactly the judgment half the close-out sweep
reserves for a reader.

**Why it matters.** `ROADMAP.md` is one of the two documents a later session
cites to *refuse* work, so a live-sounding claim in it is obeyed rather than
checked. The clause says nothing on the documented close-out path names
`verify --self`; `PL-7XTS` put exactly that into step 5 of the `docket` skill's
"Mode: close out an item" and closed. A session reading the row now is told the
gap is open, and the forward reference it offers - "`PL-7XTS` was filed in this
range to say so" - resolves to a closed item, which reads as work still owed by
somebody.

`tools/doc_check.py` cannot see it, and this is worth stating because the
close-out sweep leans on that tool: the citation resolves, the prose is
internally consistent, and every check passes. This is precisely the judgment
half the sweep reserves for a reader.

**Done when.** The `v0.4.14` row reads as history rather than as current state.
Past-tensing the clause - "nothing on the documented close-out path named that
mode, and `PL-7XTS` was filed in this range to say so" - is the fix the brief
argues for: every other clause in that row is plainly historical, the word
"yet" is what makes this one read as a live claim, and removing it keeps what
the range actually did. `python3 tools/doc_check.py check` passes afterwards.

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Past-tense the clause. A release row's "nothing ... yet" is a record under
clause 4 - it asserts what was true when the row was written - so the repair is
a tense, not a link, and the later fact goes in its own dated sentence.
