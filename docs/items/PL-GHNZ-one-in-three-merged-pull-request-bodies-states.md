---
id: PL-GHNZ
title: One in three merged pull request bodies states nothing about what was verified, and the ones that do use three different headings for it
status: dropped
feature: pr-body-integrity
added: 2026-09-20
closed: 2026-09-20
reason: Refuted by the count: the 30 most recently merged pull requests state what was verified in 29 of 30 and a make check result in 29 of 30. The title came from a proxy (squash commit bodies), six of which were empty for the unrelated reason in PL-843V. Only the heading name varies, which is not a gap.
---

**Problem.** One in three merged pull request bodies states nothing about what was verified, and the ones that do use three different headings for it

**Dropped 2026-09-20, refuted by the count it was filed on.** The title was
written from a proxy - the bodies of the squash commits on `main` - before the
pull request bodies themselves had been read. Six of the sampled squash commits
turned out to carry no body at all (`PL-843V`), which read as six bodies with
no verification section and was nothing of the kind.

Read directly, the 30 most recently merged pull requests (#752-#782) state what
was verified in **29 of 30**, and state a `make check` result in **29 of 30**.
The single exception, #763, is a queue-only pull request with no code changes.
What actually varies is the *heading* - `## Checks` in 12, `## Verification` in
11, `## Tests` in 1, and the claim in prose without a heading in 5 - and a
heading name is not a gap. Six bodies carry the claim outside a dedicated
section, which costs a reader scanning `git log` a few seconds and nothing else.

Nothing to fix. Recorded rather than deleted because the corpus count is the
answer to "should the pull request body have required sections", and the next
session to ask should meet the number rather than the impression. `PL-NDQD`
carries the full table.
