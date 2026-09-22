---
id: PL-6SV4
title: The tag commands the release mode prescribes tag origin/main, which is the release's merge commit only until the next merge lands: with sibling sessions merging minutes apart a tag can land on a later commit, and doc_check's version test cannot tell it apart because that commit still declares the same version
status: untriaged
feature: release-process
touches: .claude/skills/docket/modes/release.md, subprojects/docket/src/docket/cli.py
added: 2026-09-22
---

**Problem.** The tag commands the release mode prescribes tag origin/main, which is the release's merge commit only until the next merge lands: with sibling sessions merging minutes apart a tag can land on a later commit, and doc_check's version test cannot tell it apart because that commit still declares the same version

**Found 2026-09-22 while cutting v0.5.5 (`PL-3XWZ`).** `.claude/skills/docket/modes/release.md`
prescribes `git tag -a vX.Y.Z origin/main`, run "straight after the merge, when
`origin/main` *is* the merge commit", and `bin/docket release` prints
`MERGE_COMMIT` for the owner to fill. Both rest on nothing merging between the
release's merge and the owner's `git fetch`. In the hour of this cut `#919`,
`#920`, `#921` and `#922` merged within about twenty minutes of it, `#922`
seven seconds after the release's own pull request `#923` opened. A tag placed
on a later commit passes `tools/doc_check.py`'s `PL-YKSD` test, because that
commit still declares the released version, and it silently widens the tag's
span past the notes. A fix to what exists rather than a new mechanism, so the
generator pause does not hold it.

**Candidate.** Resolve the squash commit from the pull request number its
subject carries: `git log origin/main --format=%H --fixed-strings --grep='(#N)'
-1`, shown first with `--oneline` so the owner sees the subject before tagging;
the printed recipe and the release mode then name the pull request, which is
known when the recipe is given, rather than a commit that is not yet.
