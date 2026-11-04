---
id: PL-NDY5
title: pr-body-email-guard.sh imports docket at load for modes --screen never uses, which costs about 213 ms on every MCP call and lets an unrelated rename in docket switch the guard off with only an ImportError on swallowed stderr
priority: P2
effort: S
status: done
classes: defect, perf
feature: guards-say-when-they-cannot-check
touches: tools/pr_body_check.py, tools/email_screen.py, .claude/hooks/guard.py, .claude/hooks/git/pre-push, .claude/hooks/owner_ask_guard.py, tests/unit/test_pr_body_check.py, tests/unit/test_email_screen.py, tests/unit/test_hook_blocks.py, docs/apparatus.md, docs/resident-instructions.md, .claude/skills/pull-request/SKILL.md
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-04
pr: 2005
payoff: the guards on a GitHub call take about 56 ms instead of 149 ms, and a rename inside docket can no longer switch off the email guard
verify: grep -q 'def test_the_screen_still_refuses_with_docket_unimportable' tests/unit/test_email_screen.py
---

**Problem.** pr-body-email-guard.sh imports docket at load for modes --screen never uses, which costs about 213 ms on every MCP call and lets an unrelated rename in docket switch the guard off with only an ImportError on swallowed stderr

**Reproduced 2026-11-03.** `python3 tools/pr_body_check.py --screen` on an
MCP payload took about 171 ms against 14 ms for a bare `python3 -c pass`, and
`-X importtime` shows `docket.vcs` alone at about 45 ms of it. The hook runs
on every MCP call.

**Why it matters.** The cost is paid on every MCP call in every session. And an
unrelated rename inside `docket` makes the import fail, which the hook's
`|| true` and discarded stderr turn into a silent pass of the one guard that
keeps an email address off GitHub.

**Done when.** `--screen` imports nothing it does not use, so a payload is
screened without loading `docket`, and a test runs `--screen` with `docket`
unimportable and finds the refusal still given.

**Generator check.** A member of `PL-9KSJ`: an import failure passes the call
with nothing said.
