---
id: PL-34B4
title: ROADMAP.md's untagged-versions paragraph goes stale too, and PL-M5FK's check excludes it
status: dropped
feature: release-roadmap-seam
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
added: 2026-08-30
closed: 2026-08-30
reason: folded into PL-M5FK, which now covers both the tag list and this paragraph. They are one check over two adjacent sentences, so a second item would have been done the moment the first landed. The redrawn decidable/judgment boundary this item argued for is recorded in PL-M5FK's "Where the decidable half stops".
---

**Problem.** `PL-M5FK` was filed against `ROADMAP.md`'s tag *list* and
deliberately scoped out the paragraph beneath it, on the grounds that "which
untagged versions are settled" is judgment. Half of that paragraph is not
judgment. On 2026-08-30 the file still read "**Four versions are untagged**"
and named v0.2.1 (`bc5f823`) and v0.2.2 (`3099980`) as awaiting tags, while
both were annotated tags in the repository - the same failure mode as the tag
list, in the sentence `PL-M5FK` says a check will not read. Corrected by hand
alongside the tag list; the count is now two.

**Why it matters.** The tag list and this paragraph state the same fact from
opposite directions, so a check that reads only one of them leaves a
contradiction reachable: the list can be right while the paragraph beneath it
still names a tagged version as untagged. This is the provenance claim
`PL-J3ZK` exists to protect - which commit shipped in which release - so a
statement about it that is itself unverified is the wrong way round.

**Where.** `tools/doc_check.py`, in whatever check `PL-M5FK` adds; tests in
`tests/unit/test_doc_check.py`.

**The decidable/judgment line, redrawn.** Three things in the paragraph are
decidable from `git tag` and belong in the check:

- the count word ("Two versions are untagged") against the number named;
- every version named as untagged having no tag;
- the set named as untagged being exactly the complement of the tag list
  above it, so the two sentences cannot disagree.

Two things are not, and stay prose: whether an untagged version is "settled"
or an open decision, and the shallow-checkout history reasoning about
`97cc66a` and `796bf4f`.

**Related.** `PL-M5FK` (`ROADMAP.md`'s tag list goes stale on every release
and no check reads it) is the same check; fold this in rather than adding a
second one. `PL-8HJ2` (`make release` fails mid-way on the ROADMAP table it
does not write) is the third `ROADMAP.md` site the release path touches and
does not write. `PL-J3ZK` (tag releases so a commit maps to its version) owns
the still-open v0.1.0/v0.2.0 decision this paragraph describes.

**Done when.** `doc_check` reports a mismatch when the untagged-versions
sentence names a version that is tagged, omits one that is not, or disagrees
with its own count; it says nothing when git cannot answer; and the three
cases have tests.
