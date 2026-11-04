---
id: PL-3986
title: gh is installed with GH_TOKEN set, so gh pr merge, gh api .../merge and gh pr create --body reach every action the merge and email guards exist to stop, and no Bash guard reads them; direct-merge-guard.sh calls the gap safe because the base binds admins, which is the state the guard exists for losing
priority: P2
effort: M
status: done
classes: defect
feature: guards-keyed-on-the-action
touches: .claude/hooks/gh_write_guard.py, .claude/hooks/direct-merge-guard.sh, .claude/settings.json, tests/unit/test_gh_write_guard.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1991
payoff: a merge or a published body sent through gh in Bash meets the same guard as the same call through MCP
verify: grep -q 'def test_a_gh_call_that_could_write_is_refused' tests/unit/test_gh_write_guard.py
---

**Problem.** gh is installed with GH_TOKEN set, so gh pr merge, gh api .../merge and gh pr create --body reach every action the merge and email guards exist to stop, and no Bash guard reads them; direct-merge-guard.sh calls the gap safe because the base binds admins, which is the state the guard exists for losing

**Read 2026-11-03.** `gh` is at `/usr/local/bin/gh` and `GH_TOKEN` is set in
this container. `direct-merge-guard.sh` § "Known gap" says a merge made with
`gh pr merge` or a REST call from Bash meets no hook, and calls that safe while
the base branch binds admins.

**Why it matters.** The merge guard and the email guard read only MCP calls,
so `gh pr merge`, `gh api .../merge` and `gh pr create --body` reach the same
actions with no guard reading them. The admin binding is the state the merge
guard exists to protect against losing, so it cannot also be what makes the
gap safe.

**Done when.** A Bash call that would merge a pull request, or publish a title
or body on GitHub, through `gh` is judged by the same rule as the MCP call that
does the same thing, and a test runs each of the three spellings above through
the guards.

**Generator check.** Misreads which client can perform a guarded action, with
`PL-D16Y`. Grouped with the `PL-61FT` re-entry (`PL-82J5`), whose session
decides whether these make a head.

**Decided, 2026-11-03: `gh` is kept to reads, and its writes go through the
MCP tools.** The brief asked for a `gh` write to be judged by the same rule as
the MCP call. Judging it would mean teaching both guards `gh`'s commands,
flags and `gh api` endpoints, which is one more reader of a grammar GitHub owns
and changes. That is the head's misread, so it would re-enter `PL-1ZZ0`.
`.claude/hooks/gh_write_guard.py` instead refuses every `gh` call it cannot
show to be a read, and its message names the MCP tool that does the same
thing. The merge and email guards then see every change a session makes to
GitHub, with one copy of each rule. The cost is a retry: a session that tries
`gh pr merge` is sent to `merge_pull_request`. The harness gives a session
`gh` for searching, and every search form stays open. A client other than
`gh` that carries the token, such as `curl` with `$GH_TOKEN`, is not read, and
the hook's header records that gap. The `verify:` names the test that runs the
three spellings above, among 24 writes, because the commissioned test was for
a `gh` reader in `direct-merge-guard.sh` that this route does not build.
