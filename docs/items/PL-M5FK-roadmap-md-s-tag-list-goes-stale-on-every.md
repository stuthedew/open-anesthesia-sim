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

**Live instance, 2026-08-31.** A third decidable sentence in the same
paragraph is false on `main` today: "the only nine it does not resolve are the
unreleased commits after v0.2.7". `git rev-list --count v0.2.7..origin/main`
reports 67. It went stale the same way the list and the count did - by commits
landing, with nothing reading the sentence - so it belongs in the same check as
a sixth direction: the number named against the count of commits after the
newest tag. Like the others, it says nothing when git cannot answer, which a
shallow checkout cannot.

**Related.** `PL-8HJ2` (`make release` stops mid-way on the `ROADMAP.md` table
it does not write) is the other half of the same seam and shares this feature.
Decided 2026-08-30: `doc_check` grows the checks, `make release` does not grow
prose generation. `PL-J3ZK` (tag releases so a commit maps to its version) owns
the still-open v0.1.0/v0.2.0 decision the paragraph describes.

**Done when.** `doc_check` reports a mismatch in any of the five directions
above, says nothing when git cannot answer, and has tests covering a matching
pair of sentences, a missing tag, an unclaimed tag, a wrong count, and two
sentences that disagree with each other.
