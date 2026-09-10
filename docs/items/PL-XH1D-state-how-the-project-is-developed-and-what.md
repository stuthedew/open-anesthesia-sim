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
verify: python3 tools/doc_check.py check && grep -qF 'Reviewed-by:' README.md CONTRIBUTING.md
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
`CLAUDE.md`'s "Two standards, deliberately unequal", not to the scaffolding
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

## The `verify:` command was rewritten 2026-09-10, before the work

The command read `test -f CONTRIBUTING.md && python3 tools/doc_check.py check`.
`CONTRIBUTING.md` was then created by `PL-78JQ` (write the contributor route) —
a different item, with different content — so from `4a4a483` onward the command
passed on a tree carrying none of this item's work. `bin/docket check --verify`
caught it correctly and failed `main`; run `#1699` on `7e0ff5bb` is the failure.

The replacement is the shape `.claude/skills/docket/SKILL.md` prescribes for a
documentation item: something that runs and passes today, paired with a `grep`
for what the work adds. `Reviewed-by:` is the trailer this item exists to
document and nothing in either file mentions it, so the grep is what fails
until the work lands. Measured 2026-09-10 on `7e0ff5bb`: the old command exits
0, the new one exits 1, and `doc_check.py check` alone exits 0.

It constrains the trailer names, which are git conventions rather than prose,
and not which of the two files carries the table — `grep` reads both.
