---
id: PL-FV7G
title: ROADMAP.md's v0.4.14 row still says nothing on the documented close-out path names verify --self, which PL-7XTS made false
status: untriaged
added: 2026-09-15
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
