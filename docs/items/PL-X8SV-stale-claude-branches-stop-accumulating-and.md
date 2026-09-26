---
id: PL-X8SV
title: Stale claude/ branches stop accumulating and today's 14 are cleared once: nothing deletes a branch whose own pull request never merges, so each hand-off between sessions leaves one behind
priority: P2
effort: M
status: done
classes: infra
touches: tools/branch_sweep.py, tools/open_pull_requests.py, tests/unit/test_branch_sweep.py, .github/workflows/branch-sweep.yml, subprojects/docket/src/docket/claims.py, docket.toml, docs/worker.md, docs/maintainer.md, docs/ARCHITECTURE.md, CLAUDE.md, .claude/skills/docket/modes/capture.md, docs/items, docs/pr-bodies
added: 2026-09-26
closed: 2026-09-26
pr: 1122
payoff: the remote holds main and live work only, and nobody deletes a branch by hand: a daily job archives each finished claude/ branch under refs/archive and deletes it
verify: grep -q 'tools/branch_sweep.py --apply' .github/workflows/branch-sweep.yml && grep -q 'refs/archive' tools/branch_sweep.py && grep -q 'branch-sweep.yml' CLAUDE.md
---

**Problem.** Stale claude/ branches stop accumulating and today's 14 are cleared once: nothing deletes a branch whose own pull request never merges, so each hand-off between sessions leaves one behind

**The owner's request, 2026-09-26:** "Ideally, the stale branches wouldn't
happen anymore and clean up is a one time thing." That lifts the generator
pause for this request.

**Why they happen** (traced 2026-09-26 by the session that filed this). A branch
is deleted only by GitHub's automatic deletion, and that fires only when the
branch's own pull request merges. A session cannot delete a branch
(`docs/worker.md` § "Ref operations a session cannot perform"). Of the 14 stale
branches on 2026-09-26:

- **6 were branches carrying only captured items**, from before `PL-WNCT`
  landed (2026-09-23 01:54 UTC). None have appeared since.
- **7 were hand-offs.** The successor session copies its predecessor's commits
  onto its own harness-named branch and merges from there. `PL-J6HP` landed via
  #937, `PL-N162` via #1002, `PL-979D` via #1068 and `PL-R17X` via #1102. This
  is still happening: since `PL-YJG1` (2026-09-25), hand-offs go to Projects
  threads.
- **1 was a branch reused after its merge.** Its pull request, #1045, was closed
  unmerged.

`PL-P99G` lists 13 of them with their tips. The 14th is
`claude/filed-findings-g90x9s`, tip `64c03cf86d`; its work (`PL-R17X`) landed
via #1102.

**Routes to weigh in the design round.** These are leads, not yet researched:

1. **A repository workflow that deletes a `claude/` branch** once all of these
   hold:
   - no pull request is open on it;
   - `bin/docket` reads it as settled;
   - `bin/docket stranded` finds nothing that exists only on it;
   - it is older than a grace period.

   This covers every source, including ones not yet seen, and its first run is
   the one-time cleanup. To verify:
   - that a workflow token can delete a branch (GitHub REST "Delete a
     reference", with `contents: write`);
   - how a deleted tip is restored;
   - whether settled plus stranded is safe as a deletion test. A branch holding
     the only copy of unlanded code must never pass it.
2. **A successor session continues on its predecessor's branch.** Look at
   `create_session`'s `outcome_branch`, and at how Projects threads get their
   branch. This removes only the hand-off source.
3. **Delete the head branch when a pull request closes unmerged.** This would
   have covered 2 of the 14 (#1045, #1101), which is not enough on its own.

**The owner asked for the fix now, 2026-09-26** ("Finish doing research etc. I
want to fix this now not file it for later"), so route 1 was researched and
built in the same session. The deletion risk is answered by making every
deletion reversible, and merging the pull request is the owner's decision
point, since nothing runs from a branch.

**The owner agreed with both recommendations, 2026-09-26** ("Agree with
recs"): land the sweep, and point `CLAUDE.md`'s housekeeping bullet, the
capture mode and `docs/worker.md` at it rather than at a list built by hand.

**What the research found.**

- **A workflow token can do it.** `permissions: contents: write` raises the
  `GITHUB_TOKEN` above a read-only default ("You can use `permissions` to modify
  the default permissions granted to the `GITHUB_TOKEN`, adding or removing
  access as required", GitHub Docs, *Workflow syntax for GitHub Actions*).
  GitHub's receive-pack advertises `atomic` and `delete-refs`: measured
  2026-09-26 with `GIT_TRACE_PACKET=1` on a dry-run push, agent
  `github/spokes-receive-pack`.
- **A tip can be kept without a branch.** GitHub accepts pushes to ref
  namespaces outside `refs/heads` and `refs/tags` and does not list them in its
  web interface (GitHub Community discussion #30507), and the REST "Create a
  reference" endpoint takes any name that starts with `refs` and has two
  slashes. A default fetch reads neither, so an archive ref clutters no clone.
- **Settled plus stranded is not a safe test on its own.** `settled_branches`
  asks only about refs in flight, and `stranded` also lists edits: four of the
  14 carry one (`PL-N162` on three hand-off drafts, `PL-PNJF` on
  `claude/project-thread-f3ybg7`), both items closed on `main`. The rule below
  composes every detector the digest reads, and an edit keeps a branch only
  while its item is open on `main`.
- **Route 2 removes one source at most.** `create_session`'s `outcome_branch`
  lets a spawning session name the branch its child pushes to, but Projects
  threads get harness-named branches this repository does not control, and an
  abandoned session or a pull request closed unmerged leaves a branch with no
  successor at all. Route 3 is what route 1 does after its grace period.

**The design, as built.** `tools/branch_sweep.py`, run daily by
`.github/workflows/branch-sweep.yml`. A `claude/` branch is kept while a pull
request is open from it or onto it, `docket` reads unfinished work or a release
cut on it, it holds the only copy of an item or an edit to an open one,
`vcs.orphaned` or `tools/left_behind_check.py` finds commits a merged pull
request left behind, or its last commit is under 72 hours old. Otherwise one
atomic push copies its tip to `refs/archive/<branch>/<tip>` and deletes it,
leased on the tip it was judged at. Any reading that fails archives nothing and
turns the run red. The first run is the one-time cleanup.

**Why it matters.** Every stale branch is re-read by `git branch -r`, `flight`,
`stranded` and the session-start digest, and today the only remedy is the
owner deleting them by hand, again each time they build up.

**Done when.** The sweep and its workflow are on `main`, its rule and its
archive-then-delete push are tested, and `PL-S8LZ`'s cleanup sentence in
`CLAUDE.md` points at the sweep rather than at a hand-made list.
