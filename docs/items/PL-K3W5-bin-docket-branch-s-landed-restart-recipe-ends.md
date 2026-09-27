---
id: PL-K3W5
title: bin/docket branch's landed restart recipe ends at 'then push' without saying that a remote still holding the old branch - the case whenever a commit was pushed after the merge - refuses a plain push as non-fast-forward, so a session following it is left to choose between git pull, which brings the merged history back, and a force push the recipe never sanctioned
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
payoff: a session restarting a branch whose pull request merged is told how to push over the old remote branch, instead of choosing between a pull that brings the merged history back and an unsanctioned force push
verify: grep -rq 'def test_the_restart_recipe_says_what_the_push_meets' subprojects/docket/tests/
---

**Problem.** bin/docket branch's landed restart recipe ends at 'then push' without saying that a remote still holding the old branch - the case whenever a commit was pushed after the merge - refuses a plain push as non-fast-forward, so a session following it is left to choose between git pull, which brings the merged history back, and a force push the recipe never sanctioned

**Reproduced 2026-09-27** against scratch repositories: a branch pushed, its
work squash-merged onto `main` and the branch deleted, then one more commit
pushed to it. Following the recipe - `git checkout -B` onto `origin/main`,
carry the commit across with `git cherry-pick`, then push - the plain `git
push` is `rejected (non-fast-forward)`, and git's hint reads "the tip of your
current branch is behind". The recipe is `_merged_lines` in
`subprojects/docket/src/docket/render.py` ("Restart on the merged base and
carry them across, then push and open a new pull request"), and `arming.py`
repeats its "then push" when it points at `bin/docket branch`.

**Why it matters.** The refusal comes at the step where a session follows
instructions most literally, and git's own hint points it at `git pull`, which
merges the squash-merged history back in - the duplicated history the restart
exists to prevent. The push that works overwrites the remote branch, which no
session should do on a guess, and the recipe is silent on both.

**Done when.** The landed restart recipe, and `arming`'s pointer to it, say
what the push after a restart meets when the remote still holds the old branch
and what to run then - replacing the remote branch, since the restart carried
every commit it holds beyond the merge, and never `git pull` - and a test pins
the wording in the carried and the nothing-carried cases.

**Generator check.** An instance of `PL-MT3R`'s fact - the remote's current
refs, and whether the clone's copies still match them - filed after that head
closed (2026-09-26): the recipe assumes the remote no longer holds the branch,
which is true only until something is pushed after the merge. The first
instance filed since that close.
