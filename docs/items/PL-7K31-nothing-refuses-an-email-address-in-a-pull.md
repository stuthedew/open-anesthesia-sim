---
id: PL-7K31
title: Nothing refuses an email address in a pull request body before it is sent: no hook in .claude/settings.json matches create_pull_request or update_pull_request (the only GitHub matcher is merge_pull_request), and tools/pr_body_check.py recovers and anchors bodies rather than screening them, so an address a session writes into a body is public on GitHub at once, stays in the description's edit history after it is removed, and would land in main's history at the merge because the squash message is the body (found when #1480 opened with the owner's address, 2026-10-17)
priority: P2
effort: S
status: done
classes: infra, defect
touches: .claude/settings.json, .claude/hooks/pr-body-email-guard.sh, tools/pr_body_check.py, tests/unit/test_pr_body_check.py, docs/apparatus.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
closed: 2026-10-18
pr: 1536
payoff: an email address a session writes into a pull request is refused before GitHub publishes it, so it never reaches the description history or main's squash message
verify: grep -q 'def test_an_email_address_in_a_pull_request_body_is_refused' tests/unit/test_pr_body_check.py
---

**Problem.** Nothing refuses an email address in a pull request body before it is sent: no hook in .claude/settings.json matches create_pull_request or update_pull_request (the only GitHub matcher is merge_pull_request), and tools/pr_body_check.py recovers and anchors bodies rather than screening them, so an address a session writes into a body is public on GitHub at once, stays in the description's edit history after it is removed, and would land in main's history at the merge because the squash message is the body (found when #1480 opened with the owner's address, 2026-10-17)

**Checked 2026-10-17.** `.claude/settings.json` has one GitHub matcher,
`^mcp__.+__merge_pull_request$`. No hook runs before `create_pull_request` or
`update_pull_request`.

**Why it matters.** A pull request body is public once it is sent. Removing the
address later leaves it in the description's edit history, and a squash merge
copies the body into `main`'s history, which cannot be rewritten without a force
push. So the only point at which the leak can be stopped is before the call.

**Done when.** A `PreToolUse` hook refuses a `create_pull_request` or
`update_pull_request` call whose title or body contains an email address, and
names the address it found. A test pins the refusal. The one address that a
commit trailer needs, `noreply@anthropic.com`, is allowed, since it is not
personal.

**Generator check.** One-off. The fact is "what a pull request body may contain
before it is published", and no reader misread it: nothing has ever screened a
body. It is not a member of any head.

**The generator pause does not hold this.** `bin/docket generators` marked no
head "still generating" on 2026-10-17, so a new check may be built.
