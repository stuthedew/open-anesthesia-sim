---
id: PL-XH1D
title: State how the project is developed, and what each attribution trailer means
priority: P2
effort: M
status: ready
classes: docs
feature: public-history
touches: README.md, CONTRIBUTING.md
added: 2026-08-30
verify: grep -qiF 'co-authored-by' CONTRIBUTING.md && python3 tools/doc_check.py check
not-delegable: the wording states publicly what the project owner did and did not write, and he approves it before the item closes; doc_check proves only that the citations resolve
---

**Problem.** The repository says nothing about how it is built. 168 of its 201
commits are authored by `Claude`, 139 carry a co-author trailer, and every one
of the project owner's own commits is a merge - but a reader has to infer all
of that from the log, and inference goes wrong in both directions. Nothing
states that the code is AI-written; nothing states that the owner specifies,
decides and reviews all of it. There is no `CONTRIBUTING.md`, and no way for
someone meeting `PL-VP7N` in a commit subject to learn that it resolves to a
file in `docs/items/`.

**Why it matters.** This is product, not scaffolding - it is read by anyone
evaluating whether to trust the simulator, and it is held to the standard in
`CLAUDE.md` § "Two standards, deliberately unequal", not to the scaffolding
bar the rest of this feature sits at. It is also what makes the attribution
trailers mean anything at all: without it a reader seeing `Author: Claude,
Co-authored-by: Stuart Feichtinger` learns nothing, and with it the whole
history becomes self-describing.

**The governing principle.** Attribution never claims more than the repository
can show. Everything below follows from it, and it is the reason the scheme is
this small: a finer per-commit gradation of who contributed how much would be
self-reported and unverifiable, which is the same false precision this project
already refuses for a displayed clinical value.

**Where.** A section in `README.md` and a new `CONTRIBUTING.md`.

**Approach.** Say the general truth once, prominently, in both directions -
the code is written by Claude; the project owner specifies the work, makes the
scientific and design calls, reviews every change and is accountable for all
of it; he has hand-written very little of it. A disclosure that says only "AI
wrote this" understates him and invites the opposite misreading, that he
prompted once and walked away.

Then document the trailers, which record only what is checkable:

  - `Author: Claude` on code Claude wrote - nearly everything. `git shortlog`
    and every blame view say so.
  - `Author: Stuart Feichtinger` on commits he writes himself.
  - `Co-authored-by:` for the other party where their input reached the code,
    used **only where it left a trace someone can read** - a review comment on
    the pull request, a decision recorded in the item file, a call quoted in
    the commit body the way `1565094` already does ("put to the project owner
    and answered"). Untraceable involvement is not claimed.
  - `Reviewed-by:` added at merge, because that is when the review happens.
    Say plainly that this one is a self-attestation rather than a checkable
    fact: GitHub forbids a pull request's author from approving it, and every
    pull request here is opened by the owner, so no approval exists to verify
    it against. It is the same standing as `Signed-off-by:` in kernel history,
    which is honest and conventional - but the document should not imply more.

**State the limit.** Much of the owner's input happens in sessions that are not
in the repository. Say so in one line, and say what its durable trace is - the
item briefs, the commit bodies, the pull request threads. Admitting the gap is
more credible than a scheme implying there is none, and the gap is smaller than
it sounds: `CLAUDE.md`, `ROADMAP.md` and 128 item briefs are all his direction,
in his voice, written before the code they produced.

**Note the contributor-graph caveat.** GitHub credits `Co-authored-by` in the
contributors graph, so on co-authored commits the two will read as roughly
co-equal there, while `git shortlog` - which counts authors - will correctly
show Claude dominant. The graph cannot be corrected; this document is what
corrects it.

**Also here.** One line pointing at `docs/items/` as the queue, so an item id
in a commit subject resolves for a stranger. Do not mirror the queue into
GitHub Issues; that doubles the state for nothing.

**Out of scope.** Rewriting the existing 201 commits. The substance of their
messages is good, early history being scrappier than later history is ordinary,
and a rewrite would break the `commit:` reference in every closed item - a
provenance loss in the one repository that should not take it.

**Done when.** `README.md` carries the disclosure, `CONTRIBUTING.md` documents
the attribution rule and the queue pointer, the project owner has approved the
wording of any statement made about him, and `python3 tools/doc_check.py check`
passes.

**The anchor `verify:` greps for.** `CONTRIBUTING.md` names the
`Co-authored-by` trailer literally, whatever capitalization the section
settles on. That token is what the command tests for, case-insensitively, so
it specifies the trailer scheme itself rather than betting on a phrase - and
the case-insensitivity is not fastidiousness: this repository's own history
carries both spellings, 266 `Co-authored-by` against 13 `Co-Authored-By`, so a
case-sensitive match would be a coin-flip that failed a finished item. The
previous command tested `test -f CONTRIBUTING.md`, which `PL-78JQ` satisfied
without doing any of this item's work; `PL-X7VY` is where that was found and
repaired.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Partly overtaken, and the census
the prescribed wording rests on has inverted.** `CONTRIBUTING.md` now exists
(`PL-78JQ`) and carries the queue pointer this item wanted: `:6-8` explains
that changes are made against "an internal development queue in
[`docs/items/`](docs/items), which is why almost every pull request is titled
`PL-XXXX: …`", with `README.md:209` saying the same. So a stranger meeting
`PL-VP7N` in a commit subject can now resolve it.

The disclosure itself is entirely absent, which is the item's real substance:
`grep -rniE 'AI-written|written by Claude|Author: Claude|Reviewed-by|attribution|large language model' README.md CONTRIBUTING.md CITATION.cff`
returns nothing, and `co-authored-by` appears nowhere in `CONTRIBUTING.md`.

**Re-measure before writing the wording.** The brief prescribes text on the
basis that "168 of its 201 commits are authored by `Claude` … and every one of
the project owner's own commits is a merge". Today, over 1,046 commits:
**728 Stuart Feichtinger, 300 Claude, 18 claude[bot]**, with 710 bodies
carrying a co-author trailer and **627 of Stuart's 728 non-merge** - squash
merges now land as `Author: Stuart Feichtinger` with a `Co-authored-by: Claude`
trailer. So `git shortlog` and blame no longer say what this brief says they
say, and the disclosure has to be written from the trailer scheme rather than
from the author field.
