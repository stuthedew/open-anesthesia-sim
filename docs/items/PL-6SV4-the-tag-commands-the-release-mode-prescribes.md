---
id: PL-6SV4
title: The tag commands the release mode prescribes tag origin/main, which is the release's merge commit only until the next merge lands: with sibling sessions merging minutes apart a tag can land on a later commit, and doc_check's version test cannot tell it apart because that commit still declares the same version
status: dropped
feature: release-process
touches: .claude/skills/docket/modes/release.md, subprojects/docket/src/docket/cli.py
added: 2026-09-22
closed: 2026-09-23
reason: Duplicate of PL-VYK1 (ready since 2026-09-07): the same origin/main tag block in the release mode. Missed at capture because PL-VYK1's touches still name .claude/skills/docket/SKILL.md, where the release mode lived before modes/release.md, so the near-duplicate search shared no path with it. What this filing adds - the MERGE_COMMIT line cli._hand_off prints, cli._untagged_warning's grep that matches no v0.4 or v0.5 cut, the #919-#923 timing, and the version-bump commit as a key known before the pull request exists - belongs on PL-VYK1.
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

**Reproduced 2026-09-23.** `origin/main` is `a65b440c` (`#933`), two merges
past the v0.5.6 cut `cd5ad3f6` (`#931`), and `git show origin/main:pyproject.toml`
declares `version = "0.5.6"`. So `git tag -a v0.5.6 origin/main` run now would
tag `#933`, and `tools/doc_check.py`'s tag test would accept it, because it reads
only `pyproject.toml` at the tag. No tag has landed wrong yet: v0.5.3 to v0.5.6
each sit on their own cut commit. `cli._untagged_warning` has a sibling fault.
Its "find the commit" line, `git log --oneline --grep="Release vX.Y.Z"`, matched
the v0.3.x subjects and matches none of the seven v0.5.x cuts, whose subjects
read `PL-XXXX: cut vX.Y.Z, ...`. One constraint bears on the candidate:
`bin/docket release` prints its recipe (`cli._hand_off`) before the release's
pull request exists, so a `(#N)` lookup serves the release mode's pasted block
but not the command's own line. The commit that introduced the version is
resolvable from the version alone: `git log --reverse -S'version = "X.Y.Z"' --
pyproject.toml` gives `a4130bb9`, `c903f738` and `cd5ad3f6` for v0.5.4 to
v0.5.6, each the tagged cut.

**Duplicate of `PL-VYK1`** (`ready` since 2026-09-07), which describes the same
`git tag -a v0.3.0 origin/main` block, the same moving-ref argument, and the
completion condition this item would have repeated. What this filing adds belongs on
`PL-VYK1`: the `MERGE_COMMIT` line `cli._hand_off` prints,
`cli._untagged_warning`'s dead grep, the `#919`-`#923` timing, and the
constraint above. `PL-VYK1`'s `touches` also still names
`.claude/skills/docket/SKILL.md`, which held the release mode before it moved
to `modes/release.md`.

**Generator check.** This filing is itself a post-close instance of
`PL-TZ7T`'s mechanism (closed 2026-09-20: `bin/docket new` files a duplicate
without noticing). Replayed through `near_duplicates`, the two titles score
0.171 against the 0.15 floor, but they share no declared path, because of
`PL-VYK1`'s stale `touches`, so the search never compared them. With
`PL-4CPP` (`PL-9VPH`'s case), it is the second post-close instance, through a
different gap.
