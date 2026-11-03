---
id: PL-1ZZ0
title: The guards judge a request by its surface - a command's spelling, the client that sends it, the field that carries its text - rather than by the action it performs, so each new spelling, client or field passes unread: PL-82J5, PL-3986 and PL-D16Y, after PL-61FT's spelling fix did not hold
priority: P1
effort: L
status: ready
classes: defect
feature: guards-keyed-on-the-action
touches: .claude/hooks/no-prune-guard.sh, .claude/hooks/direct-merge-guard.sh, .claude/hooks/pr-body-email-guard.sh, tools/pr_body_check.py, .claude/hooks/stop_hook_patch.py, tests/unit/test_no_prune_guard.py, tests/unit/test_pr_body_check.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
payoff: a merge, a published address or a ref deletion is checked whichever spelling, client or field carries it
verify: grep -q 'def test_every_route_to_github_text_is_screened' tests/unit/test_pr_body_check.py
root-cause-of: PL-82J5, PL-3986, PL-D16Y
generator: live - each guard names the surfaces it reads, and the 2026-11-03 review found three actions arriving by surfaces none names, after PL-61FT's spelling fix closed as spent
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
