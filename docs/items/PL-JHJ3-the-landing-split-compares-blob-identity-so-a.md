---
id: PL-JHJ3
title: The landing split compares blob identity, so a squash that merged content reads as unlanded and two sessions writing one record line read as landed
status: done
priority: P2
effort: S
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md
added: 2026-09-04
closed: 2026-09-04
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_stranded_is_silent_when_the_merge_took_the_commit_and_merged_it' subprojects/docket/tests/test_cli.py
---

**Problem.** `vcs._landing_split` asks whether the default branch has ever held
each blob a ref introduces. Blob identity is not the same question as "did this
work land". A squash merge writes the *result* of merging the branch into the
base, so where the base moved on a file the branch also touched, what lands is
neither side's blob - and the branch's copy then matches nothing the base has
ever held, while every line of its work is there.

**It fired falsely within the hour, in the digest of the session that shipped
it.** `PL-3D2M` merged at 22:32. The next session start read:

    Left on a branch after its pull request merged:
    origin/claude/snapshot-run-history-copy-dw6djz (3 files).

That branch carried the v0.3.8 release commit, squash-merged as `#312` while
`#311` was landing edits to the same `ROADMAP.md` prose. The merge wrote the
combined text, so three of that commit's ten paths matched no blob `main` had
held. Reading the diff, `main` was **ahead** of the branch on all three - it
held the branch's release edits *plus* the `PL-D9WD` cross-references added
afterwards. Nothing was missing from anywhere.

That is `CLAUDE.md`'s "an advisory being routed around": a line in text resent
on every turn of every session, saying work is lost when it is not.

**Fix.** The content split still selects candidates, and a second condition
decides: the branch must carry a **commit none of whose paths reached the base
at all**. A commit partly landed is a commit the merge took and merged; a commit
wholly absent is one nothing took. On the branch above, ten paths touched and
seven landed - silent. On `#284`'s dropped commit, every path outstanding -
reported. The reported paths are narrowed to those commits' own, so a file the
base merged differently is no longer offered for recovery, and `format_orphaned`
prints each commit's paths under it rather than the branch's after the last one.

**What the measurement was worth, and what it was not.** `PL-3D2M` argued
precision from 204 merged pull requests compared against the commit that landed
each, at 0 discrepancies and 0 conflicts. That was true of the 204 then merged
and did not cover the shape that broke it - a branch whose prose the base had
edited underneath, which `#312` produced twenty minutes later. Checked again
after the event: comparing that branch against its own landing commit conflicts
rather than resolving, so the landing-commit comparison would not have fixed it
either. The population a measurement covered is part of what it measured, and
the claim has been qualified everywhere it appears.

**What is still wrong, deliberately.** A commit pushed after the merge that
happens to leave one file in a state the base has held reads as partly landed
and goes unreported. Silence is this check's expensive direction everywhere
else; the trade is taken only because the alternative was firing in every
session.

**The exact test, and why it is not this item.** The invariant that admits no
heuristic is whether the branch ref points past the head the pull request
merged: `refs/pull/<n>/head` is frozen at merge, so a tip beyond it is precisely
the work left behind, with no content comparison and so no squash or rename
confound. It needs `refs/pull/*` fetched, which is a GitHub-ism `docket` must
not learn (`PL-SK88`), so it would live in `tools/` beside a CI job rather than
here. That is a design decision for the project owner, recorded as `PL-VV4D`.

**Done when.** The digest is silent on a branch whose commit the merge took and
merged, and still reports one carrying a commit nothing took. Done, with a
regression test built on real git for the first and the existing one for the
second.
