---
id: PL-WW08
title: The stop hook picks its comparison point from a ref that merely resolves locally, so a merged branch's stale tracking ref makes it demand a push that would recreate a dead branch
priority: P2
effort: S
status: ready
classes: defect, infra
feature: delegation
touches: CLAUDE.md
added: 2026-09-03
verify: grep -q 'unpushed=.*--not --remotes' ~/.claude/stop-hook-git-check.sh && bash -n ~/.claude/stop-hook-git-check.sh
---

**Problem.** `~/.claude/stop-hook-git-check.sh` chooses what to compare `HEAD`
against like this:

```bash
if git rev-parse "origin/$current_branch" >/dev/null 2>&1; then
  upstream="origin/$current_branch"
else
  upstream="origin/HEAD"
fi
unpushed=$(git rev-list "$upstream..HEAD" --count 2>/dev/null) || unpushed=0
```

`git rev-parse` succeeds whenever the ref **resolves locally**. A merged pull
request deletes the head branch on the remote and leaves the tracking ref
behind, so the test passes against a ref naming a branch that no longer exists,
and every commit the default branch has gained since is counted as unpushed.

**Why it matters, and why this is not a filing to sit in the queue.** It fires
on the ordinary completion of a piece of work — twice in this session alone,
after `#267` and again after `#270`, both times false. Disproving it costs four
commands (`git ls-remote --heads origin <branch>`, `git log origin/main..HEAD`,
a content diff against the stale ref, and `bin/docket stranded` before touching
any ref). Obeying it instead recreates a dead branch identical to `main`, with
no content and no pull request.

That is `CLAUDE.md`'s **"being routed around"** test: a warning firing so
routinely that a session must reason past it every time. The danger is not the
wasted commands but the reflex the wrong fix invites — the natural response to
"stale tracking refs" is `git fetch --prune`, and such a ref can be the only
surviving copy of an item captured on a branch nobody merged. `PL-HKF4` came
within one prune of exactly that on 2026-09-03.

**`PL-1Q3S` already found this and fixed the wrong half.** It shipped in v0.2.8
`touches: CLAUDE.md` — a resident prose rule telling every session to check the
remote before obeying. That rule is correct and is why nothing has been lost,
but it puts the judgment on every future session forever rather than putting
the decidable part in code, which is the inversion `CLAUDE.md`'s
deterministic-tooling section exists to prevent. The question "is there
anything on `HEAD` that no remote ref holds" is exactly decidable and needs no
network.

**Where.** One line of `~/.claude/stop-hook-git-check.sh`:

```bash
unpushed=$(git rev-list HEAD --not --remotes --count 2>/dev/null) || unpushed=0
```

`HEAD --not --remotes` counts commits contained by **no** remote ref, so a
stale ref cannot be mistaken for a current one and the `upstream` selection
above stops mattering for this test. Three things recommend it over
`git ls-remote --exit-code --heads origin "$current_branch"`: it is offline, so
the hook keeps working in a container with no network; it is the idiom this
same hook already trusts a few lines above, where the signing check scopes
itself to "commits that are on NO remote ref"; and it is one line rather than a
restructure.

**A caveat, stated rather than hidden.** The two tests differ where a branch's
own remote ref is behind but the same commits sit on another remote ref. There
the new form stays silent. That is the right answer — the work is published —
but it is a real behavioural difference, not an equivalence.

**Not this repository's file.** The hook lives in `~/.claude/`, so it is the
project owner's to change and the change reaches all of their projects. This
item records the diagnosis and the exact patch; applying it is theirs.

**Done when.** Finishing a session on a branch whose pull request has merged
produces no push demand, and no session spends commands disproving one.
