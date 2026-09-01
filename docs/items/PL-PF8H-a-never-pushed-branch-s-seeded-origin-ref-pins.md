---
id: PL-PF8H
title: A never-pushed branch's seeded origin/ ref pins the stop hook's comparison to the session-start main tip, so merely fetching main reports unpushed commits
priority: P2
effort: S
status: done
classes: infra, session-cost
feature: dev-tooling
milestone: v0.2.8
touches: CLAUDE.md
added: 2026-09-01
closed: 2026-09-01
pr: 162
verify: python3 tools/doc_check.py check && grep -qF 'check the remote before obeying a demand to push' CLAUDE.md
---

**Problem.** `~/.claude/stop-hook-git-check.sh` picks its comparison point with

    if git rev-parse "origin/$current_branch" >/dev/null 2>&1; then
      upstream="origin/$current_branch"

which `PL-1Q3S` diagnosed as testing whether the ref *resolves locally* rather
than whether the branch exists on the remote. `PL-1Q3S` recorded that defect in
its merged-pull-request guise and is `done`. This is the same defect reached by
a different route, and the habit `PL-1Q3S` wrote into `CLAUDE.md` does not
cover it.

The web harness seeds a remote-tracking ref for the branch it names a session,
before the session has pushed anything. Observed 2026-09-01 in a session on
`claude/next-priorities-regxtv`:

    $ git ls-remote --heads origin | sed 's#refs/heads/##'
    Review_articles
    add-claude-github-actions-1788276784576
    claude/working-notes-redundancy-4bp5xm
    main

    $ git rev-parse origin/claude/next-priorities-regxtv
    d5bfbff0dcf8c764550a5c57ded9eb44d7b552ab

The branch is on no remote, yet its `origin/` ref resolves - pinned at
`d5bfbff`, which was `origin/main`'s tip when the session started. The session
then did nothing but `git fetch origin` and a fast-forward onto the merge of
#159 (`fce85ff`). That single commit is `main`'s own, already on `origin/main`,
and `git log origin/main..HEAD` is empty - but the hook compares
`d5bfbff..HEAD`, finds one commit, and reports "There are 1 unpushed commit(s)
... Please push these changes".

**Why it matters.** Obeying it is worse than ignoring it, for the reason
`PL-1Q3S` gives: the push would create a remote branch identical to
`origin/main` with nothing of its own, which a concurrent session then has to
reason about. The new part is *when* it fires. `PL-1Q3S`'s trigger was a merged
pull request, and its remedy - `git branch -dr origin/<branch>` before
restarting the branch, now resident in `CLAUDE.md` - is keyed to that moment.
Here nothing merged and nothing was restarted, so no session reading that
bullet is prompted to check. The trigger is instead *any* session that fetches
`main` without committing, which is every read-only session: a "what should we
work on next", a status question, a design round. Those are exactly the
sessions with no work to push, so the hook's demand is unanswerable rather than
merely wrong, and the session either spends a turn proving it wrong or pushes
the empty branch.

It compounds with the same digest disagreement `PL-1Q3S` noted. The
session-start digest read "current with origin/main (0 ahead)" against the same
refs the hook read as one ahead, in the same session.

**Where.** The hook is `~/.claude/stop-hook-git-check.sh`, outside the
repository and not editable from a session - `PL-1Q3S` recorded the upstream
half for the same reason. What is fixable here is the guidance:
`CLAUDE.md`'s stale-tracking-ref bullet states the merged-branch case only, and
its `git branch -dr origin/<branch>` line is correct for this case too but is
introduced by a condition that excludes it.

**Approach.** Widen the existing bullet rather than adding one - the resident
line total is watched (`PL-H7XN`), and this is the same defect with a second
trigger, so a second bullet would restate the diagnosis. The edit is to the
condition, not the remedy: say the ref is stale whenever it resolves locally
but names no branch on the remote, whether that is because a merge deleted the
branch or because nothing ever pushed it, and give `git ls-remote --heads
origin` as the one-line test. Consider whether the check is better made
deterministic in `.claude/hooks/` - the repository owns `docket-branch-guard.sh`
and `docket-digest.sh` already, and "does `origin/<branch>` name a branch that
exists" is decidable, which is the tier-1 disposition in `CLAUDE.md`'s routing
rule. That would also let the digest and the hook stop disagreeing.

**Done when.** A session whose branch has never been pushed is told, by
something it reads before the stop hook fires, that an `origin/` ref resolving
to a branch absent from `git ls-remote` is stale and is not a reason to push.

**Done 2026-09-01, and why it stayed resident.** The existing bullet was
widened rather than joined by a second one, so the diagnosis is stated once:
`CLAUDE.md` +4 lines, which `doc_check` raises as an advisory against
`PL-H7XN`'s test. It buys the second trigger, the retitled condition, and the
two commands that decide it. The routing test puts it in tier 4 rather than
tier 1: the moment a session needs this is when the stop hook demands a push at
the *end* of a session, and no check in `.claude/hooks/` can fire then. The
session-start digest already answered correctly - "current with origin/main (0
ahead)" - in the very session that then spent four turns disproving the hook,
which is the evidence that an earlier deterministic signal is not what was
missing. What was missing was the bullet a session reaches for once the hook
has spoken, and that bullet's condition excluded this case.

**Relations.** `PL-1Q3S` (a merged PR leaves a stale tracking ref, so the stop
hook demands a push that would recreate a dead branch), `done` - same root
defect, merged-branch trigger, and the source of the `CLAUDE.md` bullet this
item widens. `PL-FLZ4` (the merged-branch restart leaves the branch upstream
pointing at a deleted ref, so `git status` warns the upstream is gone) is the
third instance of the family.
