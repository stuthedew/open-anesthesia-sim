---
id: PL-1ZZ0
title: The guards judge a request by its surface - a command's spelling, the client that sends it, the field that carries its text - rather than by the action it performs, so each new spelling, client or field passes unread: PL-82J5, PL-3986 and PL-D16Y, after PL-61FT's spelling fix did not hold
priority: P1
effort: L
status: done
classes: defect
feature: guards-keyed-on-the-action
milestone: v0.6.15
touches: .claude/hooks/git/reference-transaction, .claude/hooks/git/pre-push, .claude/hooks/stop_hook_patch.py, .claude/hooks/gh_write_guard.py, .claude/hooks/direct-merge-guard.sh, .claude/hooks/pr-body-email-guard.sh, tools/pr_body_check.py, .claude/settings.json, .claude/skills/docket/modes/capture.md, docs/apparatus.md, docs/worker.md, docs/resident-instructions.md, ROADMAP.md, tests/unit/test_git_hooks.py, docs/items/PL-9KSJ-every-guard-hook-fails-open-without-a-trace.md, docs/items/PL-B5K1-the-five-shell-guards-hand-the-payload-to.md, docs/items/PL-S3TF-about-1-430-lines-of-guard-python-live-inside.md, docs/items/PL-SG93-the-bash-guard-hooks-account-for-74-defects.md
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1991
payoff: a merge, a published address or a ref deletion is checked whichever spelling, client or field carries it
verify: grep -q 'def test_an_address_in_a_commit_message_is_refused_and_nothing_is_sent' tests/unit/test_git_hooks.py
root-cause-of: PL-82J5, PL-3986, PL-D16Y
generator: spent - each irreversible action is checked where git or the one MCP screen performs it, and gh writes are refused, so a new spelling, client or field reaches no action unread; what stays unread is named in each hook's header
misread: Which action a request performs, whatever its spelling, client or text field
reenters: PL-61FT
---

**Problem.** The guards judge a request by its surface - a command's spelling, the client that sends it, the field that carries its text - rather than by the action it performs, so each new spelling, client or field passes unread: PL-82J5, PL-3986 and PL-D16Y, after PL-61FT's spelling fix did not hold

**What the members share.** `no-prune-guard.sh` reads the words of a command,
so a spelling its model of git lacks deletes refs unread (`PL-82J5`). The merge
and email guards read only MCP calls, so `gh` in Bash reaches the same merge
and the same published body unread (`PL-3986`). `tools/pr_body_check.py`
reads only a title and a body, so a merge's commit message and pushed file
content are published unread (`PL-D16Y`). In each case the guard names the
surface it reads, and the action it exists to stop arrives by a surface it
does not name.

<!-- absent: no-prune-guard.sh -->

**Why it matters.** Each guard protects an action that cannot be taken back. A
guard keyed on the surface is only as complete as its list of surfaces, and
`PL-61FT`'s fix showed that a list of known gaps keeps growing: after it
closed as spent, the review of 2026-11-03 found irreversible ref deletions
among its gaps.

**Done when.** Each guard that protects an irreversible action checks it where
the action happens, where such a point exists: git's `reference-transaction`
hook for ref deletions, and one screen that every route publishing text to
GitHub passes through, whichever client or field carries it. Where no such
point exists, the guard's header says what goes unread. `PL-82J5`, `PL-3986`
and `PL-D16Y` are closed by that work.

**Generator check.** A family head over `PL-61FT`'s fact, what a shell command
does when run, widened from spelling to client and field. `PL-9PPJ` and
`PL-SMM1` re-enter `PL-61FT` as false refusals, where no action point exists
to check instead, so they stay outside this head and are fixed at their own
rank.

**Closed, 2026-11-03.** Each irreversible action is now checked where it
happens. A ref deletion is checked in git's ref transaction (`PL-82J5`). A
push is checked in git's `pre-push` hook, for deleted branches and for email
addresses in its new commits. Text sent to GitHub is checked by one screen of
every field of every MCP call (`PL-D16Y`). `gh` writes are refused and sent to
that MCP route (`PL-3986`). Each hook's header names what it does not read:
`--no-verify`, `core.hooksPath` switched off, a hand edit of `.git/refs`, and
a client other than `gh` that carries the token. The `verify:` names the push
screen's test, the one place where a ref guard and a text guard meet.
