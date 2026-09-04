---
id: PL-WW08
title: The stop hook picks its comparison point from a ref that merely resolves locally, so a merged branch's stale tracking ref makes it demand a push that would recreate a dead branch
priority: P2
effort: S
status: done
classes: defect, infra
feature: delegation
touches: CLAUDE.md, .claude/settings.json, tools/stop_hook_patch.py, tests/unit/test_stop_hook_patch.py, docs/ARCHITECTURE.md
added: 2026-09-03
closed: 2026-09-04
verify: uv run pytest tests/unit/test_stop_hook_patch.py && grep -q 'def test_the_correction_is_what_git_actually_answers' tests/unit/test_stop_hook_patch.py && grep -q 'tools/stop_hook_patch.py' .claude/settings.json
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

**Not the project owner's file either — corrected 2026-09-04.** The paragraph
this replaces said the hook lives in `~/.claude/`, so it is the owner's to
change and the change reaches all of their projects. It is not, and it does
not. In a cloud session `~/.claude/` is provisioned by the Claude Code Remote
environment manager at container start, and the hook is Anthropic's: it cites
internal Anthropic source paths (`api-go/ccr/e2e/byoc/`
`scenario_sign_commit_test.go:117`, `antique/cmd/aq/git.go`) and the public
issue `anthropics/claude-code#69586`, and it is wired by
`~/.claude/launcher-settings.json`, which the env-manager writes — the sibling
`stop-hook-reply-gate.py` says so in its own docstring. Every hook script in
`~/.claude/` carried this container's start time (04:02, container created
04:01:55). Editing the copy inside a container is erased at the next one.

Nor does the owner's own machine reach it: "If you have SessionStart hooks in
your user-level `~/.claude/settings.json`, don't expect them in the cloud.
User-level settings stay on your machine"
(https://code.claude.com/docs/en/cloud-environments, "Setup scripts vs.
SessionStart hooks", read 2026-09-04). A local patch would fix local sessions
only, and the sessions this fires in are the cloud ones.

An environment **setup script** is the wrong lever too: it runs *before* Claude
Code launches, and is skipped entirely once the environment cache exists (same
page, "Environment caching"), so it cannot reliably patch a file the harness
writes at container start.

**What was built** (project owner approved the substitution, 2026-09-04). A
repository **SessionStart hook** — which runs *after* Claude Code launches, on
every session including resumed (same page) — rewriting the line in this
container's copy. It is the only in-container route: a `Stop` hook that exits 2
blocks the stop, and no second hook can countermand it.

- `tools/stop_hook_patch.py`, wired ahead of the digest in
  `.claude/settings.json`. It matches the whole line and rewrites nothing when
  it is absent or doubled, so a change upstream is a clean miss rather than a
  partial edit to a script every stop executes. It writes through a rename, so
  the file is either the old script or the new one, and it exits 0 on every
  path: a session that will not start is worse than a spurious demand.
- It is **silent on the path it takes every session** — a SessionStart hook's
  stdout is resent on every turn, so reporting the ordinary success would cost
  tokens forever to say nothing needs deciding. It speaks only when the
  correction is *not* in place, and then carries the disproof commands, which
  is why `CLAUDE.md`'s bullet no longer spends resident lines on them (16 lines
  to 10).
- `tests/unit/test_stop_hook_patch.py` covers the edit and its blast radius,
  both refusal cases, the missing and unwritable file, the mode bit, and
  `bash -n` on the result.
  `test_the_correction_is_what_git_actually_answers` proves the claim rather
  than the edit: a real repository in the shape above, where
  `origin/feature..HEAD` counts 2 and `HEAD --not --remotes` counts 0, and both
  count 1 once work is genuinely unpushed.

**Two things it does not do, stated rather than hidden.** It reaches this
project's sessions only — the durable fix for every user is a report upstream,
which is not this repository's to land. And the two tests differ where a
branch's own remote ref is behind but the same commits sit on another remote
ref: there the new form stays silent. That is the right answer — the work is
published — but it is a real behavioural difference, not an equivalence.

**On the `verify:` command.** The original could not be satisfied: it grepped a
file this container regenerates, so it failed before the work for the wrong
reason (checked 2026-09-04 — the hook's only `--not --remotes` was the signing
block's `local_count=`, on a line of its own) and would have passed on a
container-local edit that survives nothing. The replacement pairs the new
suite with a grep for the test that carries the claim and a grep for the
wiring, since the tool never runs unless `.claude/settings.json` names it.

**Done when.** Finishing a session on a branch whose pull request has merged
produces no push demand, and no session spends commands disproving one.
