---
id: PL-KRS6
title: bin/docket release counts the previous release's own cut item as releasable work, so every session after a release is offered an empty one
status: untriaged
added: 2026-09-07
---

**Problem.** `bin/docket release --dry-run`, run 2026-09-07 immediately after
v0.4.7 merged, printed:

    1 finished item(s) since 0.4.7:
      PL-H1GH "Cut the v0.4.7 release: the supported run length, the tolerance
               gate, and traces you can tell apart"
    Completes: release-process

`PL-H1GH` *is* the item that cut v0.4.7. It closes in the release commit, so it
is stamped with no `milestone:` of its own and reads as finished work belonging
to the *next* release. The offer is therefore for a release whose whole content
is the previous release's cut, and the session-start digest repeats it —
`Releasable: 1 finished item(s) since 0.4.7, completing release-process. Offer
0.4.8 before taking new work.`

**Why it matters.** It fires in every session from the moment a release merges
until the next real item closes, and the instruction attached to it ("before
taking new work") is the strongest form the digest has. A session that follows
it cuts an empty 0.4.8; a session that does not learns that the line can be
wrong, which is the cost `CLAUDE.md` names for an advisory nobody acts on. It is
the same family as `PL-D2GW` (done) — the digest offering a release that should
not be cut — but a different cause: `PL-D2GW` was the version naming a
milestone whose gate was open, this is the releasable *set* being non-empty when
it should be empty.

**Where.** `subprojects/docket/src/docket/release.py` computes the finished-set;
`render.py` and the digest print it. The decidable rule is small and exact: an
item whose closing commit is the release cut for version *V* belongs to *V*, not
to the release after it. `docs/items/PL-*-cut-the-v*.md` is a closed set of
eight such items, all sharing the `release-process` feature and a
`Cut the v… release` title, so there is more than one way to identify them —
prefer the structural one (closed by the commit that wrote the version) over
matching the title.

**Done when.** With `main` at a freshly merged release and nothing else closed
since, `bin/docket release --dry-run` reports no releasable work and the digest
prints its `No release to offer` line instead.
