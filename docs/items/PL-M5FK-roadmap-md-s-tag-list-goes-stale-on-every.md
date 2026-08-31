---
id: PL-M5FK
title: ROADMAP.md's tag statements go stale on every release and no check reads them
priority: P2
effort: S
status: ready
classes: docs, infra
feature: release-roadmap-seam
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
added: 2026-08-30
verify: uv run pytest tests/unit/test_doc_check.py -k tag_inventory
---

**Problem.** `ROADMAP.md` states which versions carry annotated tags in two
adjacent places, and nothing reads either one. On 2026-08-30 both were wrong:
the list read "v0.0.1, v0.0.2, v0.2.3, v0.2.4, v0.2.5 and v0.2.6" while the
repository also held annotated tags for v0.2.1 (`bc5f823`), v0.2.2
(`3099980`) and v0.2.7 (`db63b12`); the paragraph beneath it read "**Four
versions are untagged**" and named v0.2.1 and v0.2.2 as awaiting the tag
commands. `python3 tools/doc_check.py check` passed on that tree - it
validates the release train and the current baseline, but neither sentence.
Corrected by hand in `4d19dc4`; both will go stale again at the next release.

**Why it matters.** The sentences exist precisely because four versions went
out untagged and the gap could not be repaired with confidence afterwards
(`PL-J3ZK`). A statement about which releases are traceable, that is itself
not traceable, is the wrong way round. It is also decidable by reading the
repository - `git tag` against a list of names - which is exactly where
`CLAUDE.md` says the work belongs, and it recurs on a fixed schedule: every
release, forever.

**Where.** `tools/doc_check.py`, alongside the existing release-train check,
with tests in `tests/unit/test_doc_check.py`.

**Approach.** Read both sentences and compare them against `git tag`:

- a version the list claims as tagged that has no tag;
- a tag that exists but the list does not claim;
- a version the paragraph names as untagged that is in fact tagged;
- the paragraph's count word against the number of versions it names;
- the two sets being complements, so the sentences cannot disagree with each
  other even when each separately agrees with `git tag`.

Keep `vcs.py`'s discipline of saying nothing when git cannot answer, so a bare
or shallow checkout does not fail the check - a shallow clone is how `PL-J3ZK`
reached a wrong conclusion about v0.1.0 and v0.2.0 in the first place.

**Where the decidable half stops.** Two things in the paragraph stay prose and
must not be scripted: whether an untagged version is "settled" or an open
decision, and the shallow-checkout history reasoning about `97cc66a` and
`796bf4f`. This boundary is the item's design work - `PL-34B4`, now dropped
into this one, was filed because the original scope drew it one sentence too
early and excluded the count and the version names, which are as decidable as
the list above them.

**Live instance, 2026-08-31 - corrected, and the sixth direction withdrawn.**
A third decidable sentence in the same paragraph was false on `main`: "the only
nine it does not resolve are the unreleased commits after v0.2.7", against a
true count of 69. Repaired in the PL-8HJ2 branch by deleting the number rather
than by checking it, along with "all 214 commits on `main`" in the same
sentence.

Checking it, as this item originally proposed, would have been the wrong fix.
That number moves on every commit, not on every release, so a check reading it
turns `make check` red on `main` after each merge until somebody edits this
file - a check that fires on a fixed schedule of "always" and is switched off
within a week. The sentence loses nothing by not carrying a count: "the commits
it does not resolve are the unreleased ones after the newest tag" says the same
thing and cannot go stale. The general rule is worth stating, because the same
trap is available in the other directions: a number that ages with commits is
deleted, and only a number that ages with releases is worth a check.

**Two design findings from the PL-8HJ2 branch, 2026-08-31 - the approach above
needs a decision before it is built.**

*The newest release is untagged at the moment the check runs.* The tag is
placed on the merge commit, so between the release commit and the tag push
there is a version that is `Completed` in the table and absent from `git tag`.
Any of the directions above, phrased as an error, therefore fails `make check`
on every release branch - which is exactly the failure PL-8HJ2 was opened to
remove, arriving through a different door. Whatever the mechanism, the version
the table marks `current baseline` has to be an advisory rather than an error
until its tag exists.

*The tagged-version list duplicates the version table, and deleting it is
stronger than checking it.* The list restates which versions have shipped -
which the table above it already says - and adds one bit per version, tagged or
not, which `git tag` answers outright. So the recommendation is to drop the
list from the prose and hold the table's `Completed` rows to `git tag`
directly, keeping an explicit exception sentence (`**N versions are
untagged**: ...`, count checked against the names) for the case the project has
had before. That is one fewer hand-edit per release, no prose grammar for the
list, and it catches the failure the list cannot: a release that goes out
untagged *and* unmentioned reads as consistent under the original approach,
because the list and `git tag` agree that neither has it. Only the table knows
it shipped.

**Related.** `PL-8HJ2` (`make release` stops mid-way on the `ROADMAP.md` table
it does not write) is the other half of the same seam and shares this feature.
Decided 2026-08-30: `doc_check` grows the checks, `make release` does not grow
prose generation. `PL-J3ZK` (tag releases so a commit maps to its version) owns
the still-open v0.1.0/v0.2.0 decision the paragraph describes.

**Done when.** `doc_check` reports a mismatch in any of the five directions
above, says nothing when git cannot answer, and has tests covering a matching
pair of sentences, a missing tag, an unclaimed tag, a wrong count, and two
sentences that disagree with each other.
