---
id: PL-M5FK
title: ROADMAP.md's tag list goes stale on every release and no check reads it
status: untriaged
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
added: 2026-08-30
---

**Problem.** `ROADMAP.md` line 51 names which versions carry annotated tags.
Tagging v0.2.7 made it stale immediately - it still read "v0.0.1, v0.0.2,
v0.2.3, v0.2.4, v0.2.5 and v0.2.6" with v0.2.7 tagged in the repository.
`python3 tools/doc_check.py check` passed on that tree: it validates the
release train and the current baseline, but nothing reads this sentence.
Corrected by hand this release; it will go stale again at the next one.

**Why it matters.** The sentence exists precisely because four versions went
out untagged and the gap could not be repaired with confidence afterwards
(`PL-J3ZK`). A statement about which releases are traceable, that is itself
not traceable, is the wrong way round. It is also decidable by reading the
repository - `git tag` against a list of names - which is exactly where
`CLAUDE.md` says the work belongs, and it recurs on a fixed schedule: every
release, forever.

**Where.** `tools/doc_check.py`, alongside the existing release-train check,
with tests in `tests/unit/test_doc_check.py`.

**Approach.** Compare the versions named in the tag sentence against
`git tag`, and report a mismatch in either direction: a version claimed as
tagged that is not, and a tag that exists but is unclaimed. Keep `vcs.py`'s
discipline of saying nothing when git cannot answer, so a bare or shallow
checkout does not fail the check - a shallow clone is how `PL-J3ZK` reached a
wrong conclusion about v0.1.0 and v0.2.0 in the first place.

**Do not script the paragraph below it.** The prose about which untagged
versions are settled and which are an open decision is judgment, and its
accuracy is not decidable from the tree.

**Related.** `PL-8HJ2` (`make release` fails mid-way on the ROADMAP table it
does not write) is the other half of the same seam: the release path touches
`ROADMAP.md` in three places - the version table row, the baseline section,
and this tag list - and writes none of them. Worth deciding together whether
the release command grows a `ROADMAP.md` step or `doc_check` grows the checks
that catch its absence.

**Done when.** `doc_check` reports a mismatch between the tag sentence and the
repository's tags in either direction, says nothing when git cannot answer,
and has tests covering a matching list, a missing tag, and an unclaimed one.
