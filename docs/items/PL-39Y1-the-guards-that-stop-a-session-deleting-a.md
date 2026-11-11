---
id: PL-39Y1
title: The guards that stop a session deleting a branch, forcing a push or merging read the request and not GitHub's answer, so a fifth spelling passes after four fixes; refuse each action at GitHub with a ruleset and a required check, and keep session hooks as early warnings
status: untriaged
feature: irreversible-actions-refused-at-github
touches: .github/workflows/quality.yml, .claude/hooks/direct_merge_guard.py, .claude/hooks/push_check_guard.py, .claude/hooks/git/pre-push, tools/required_checks_check.py, subprojects/docket/src/docket/arming.py
added: 2026-11-11
reenters: PL-1ZZ0
---

**Problem.** The guards that stop a session deleting a branch, forcing a push or merging read the request and not GitHub's answer, so a fifth spelling passes after four fixes; refuse each action at GitHub with a ruleset and a required check, and keep session hooks as early warnings

**Asked by the project owner on 2026-11-11**, as a fresh look at a root cause fixed four times. The owner's request lifts the pause on new workflow mechanisms for this work.

**What each fix built, and what got past it.** Checked 2026-11-11 by reading the code. No destructive command was run.

1. `PL-61FT` (the Bash guards judge a command by its spelling, closed 2026-09-26). Built: a header on each guard saying what it promises, and a table of known gaps beside its tests. Got past it: twelve later items re-enter it. `PL-82J5` found ten spellings of a prune in the guard's own gap table, each of which deletes refs.
2. `PL-1ZZ0` (check each irreversible action where git performs it, closed 2026-11-03). Built: `.claude/hooks/git/reference-transaction`, which refuses a deletion of a remote-tracking ref; `.claude/hooks/git/pre-push`, which refuses a push that deletes a remote branch; `.claude/hooks/gh_write_guard.py`, which refuses a `gh` call that could write. Got past it:
   - `git push --no-verify origin --delete <branch>` and `git -c core.hooksPath=/dev/null push origin --delete <branch>` skip `pre-push`, and `push_targets` in `.claude/hooks/push_check_guard.py` asks `skips_hooks` only of a push for which `sends` is true, which a deleting push is not (`PL-95BJ`).
   - Both git hooks open with `[ -n "${CLAUDECODE:-}" ] || exit 0`, so `CLAUDECODE= git fetch --prune` and `CLAUDECODE= git push origin --delete <branch>` run with neither hook.
   - `bash -c 'gh pr merge ...'`: the header of `gh_write_guard.py` lists `gh` run by `bash -c` or a script as unread.
   - `curl` or Python's `urllib` sending a REST request: no hook reads it. `GH_TOKEN` holds the placeholder `proxy-injected`, and Anthropic's proxy substitutes the real credential on the way out, so any client can merge (`PUT .../pulls/N/merge`), delete a branch (`DELETE .../git/refs/heads/<branch>`) or force a branch (`PATCH .../git/refs/heads/<branch>` with `force`).
   - A force push: neither `push_check_guard.py` nor `pre-push` contains the word "force".
   - `.claude/hooks/direct_merge_guard.py` names `enable_pr_auto_merge` in `NOT_A_MERGE` and returns before judging it, so arming is never compared with what `bin/docket arm` answered. No CI job runs `bin/docket arm`.
3. `PL-TLPH` and `PL-ZCF9` (a guard on the wording of asks to the owner, 2026-10-19 and 2026-11-03). Built: lists of phrasings, then four context rules. Got past it: `PL-3D2F` measured 14 of 18 new phrasings refused wrongly and 20 of 33 unlisted asks passed. `PL-X4MD` then removed the wording match: `.claude/hooks/owner_ask_guard.py` now reads `bin/docket arm --owner-ask` and appends the recorded question, and refuses nothing. That is the one fix in this family that reads the recorded state, and it has not been re-entered.

**What a session is, to GitHub.** Measured 2026-11-11.

- Every push, pull request, merge and deletion from a session is recorded under the owner's account: 176 of 176 push events and 28 of 30 branch deletions from 2026-11-07 to 2026-11-10 name `stuthedew`, and the other 2 name `github-actions[bot]`, the branch sweep. The GitHub tools' `get_me` answers `stuthedew`. The account is the repository's admin.
- The credential never enters the container. "GitHub operations from the VM go through the GitHub proxy, which attaches the credential on the server side" (https://code.claude.com/docs/en/claude-code-on-the-web, read 2026-11-11).
- The proxy already refuses two actions, whatever the spelling: "the proxy rejects branch deletions and pushes of anything other than a branch, such as a tag. It doesn't limit which branches a push can update. To do that, use branch protection rules or rulesets on GitHub" (https://code.claude.com/docs/en/cloud-environments, section "GitHub proxy", read 2026-11-11). `docs/worker.md` § "Ref operations a session cannot perform" measured the deletion's `HTTP 403` on 2026-09-20 (`PL-ZM48`). So the push `PL-95BJ` describes never reaches GitHub. The proxy also rejects GraphQL, so `gh pr merge` fails there, and a REST merge does not.
- The Claude GitHub App holds Contents, Pull requests, Actions, Checks and Workflows with write access, Administration and Statuses with read access, and no Deployments permission (https://code.claude.com/docs/en/github-actions, section "GitHub App permissions", read 2026-11-11). A user access token is limited to what both the user and the app may do (https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-with-a-github-app-on-behalf-of-a-user). Creating or changing a ruleset or branch protection needs Administration with write access (https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps). So a session cannot change a rule the owner sets.
- No permission allows a push and refuses a deletion or a forced update: all three are under Contents (same page). Token permissions therefore cannot separate them, and rules must.
- `main` today: branch protection requires the checks `checks` and `pr-title` from GitHub Actions and binds admins (`enforcement_level: everyone`). The ruleset "Base" (id 21260116) adds restrict deletions, require a pull request and block force pushes, with an empty bypass list, and its `current_user_can_bypass` reads `never` for this account. Every other branch has no rule (`GET /repos/stuthedew/open-anesthesia-sim/rules/branches/<branch>` returns `[]`). The repository deletes a head branch when its pull request merges.

**Each irreversible action, and what at GitHub can refuse it.**

| Action | Routes a session has | Refused today by | What GitHub can add |
| --- | --- | --- | --- |
| Rewrite or delete `main` | any | the "Base" ruleset | nothing needed |
| Land a change on `main` without the required checks | REST or tool merge, auto-merge | branch protection, binding admins | nothing needed |
| Land a change on `main` that `bin/docket arm` holds | arm auto-merge, or merge, by any client | nothing: the hold is the session's own | a required check that runs the rule of `arm` on the pull request |
| Force another history onto a branch other than `main` | `git push --force`, REST `PATCH` | nothing | a ruleset on all branches with "Block force pushes" |
| Delete a branch other than `main` | `git push`: the proxy answers 403. REST `DELETE`: open | the proxy, for git only | "Restrict deletions", which also stops GitHub's deletion at merge and the sweep (see below) |
| Create, move or delete a release tag | `git push`: the proxy rejects it. REST: open | the proxy, for git only | a tag ruleset on `v*` with restrict deletions and block force pushes; `tools/tag_release.py` only creates tags |
| Change a rule, a secret or a setting | REST | the app's permissions | nothing needed |
| Publish text: a pull request body, a comment, a pushed commit | tools, `gh`, REST, `git push` | `tools/email_screen.py` in the session | nothing: GitHub has no rule that reads the text of a body |

GitHub's documentation for the rules, read 2026-11-11: "Block force pushes" and "Restrict deletions" are on by default in a new ruleset; a required check can be tied to one app, and "If the status is set by any other person or integration, merging won't be allowed"; rules from several rulesets are aggregated and "the most restrictive version of the rule applies" (https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets and https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets). "Branch protection rules and repository rules can also prevent branches being automatically deleted" (https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches).

**Recommendation, put to the owner 2026-11-11.**

1. A ruleset on all branches with "Block force pushes" and an empty bypass list. The route a session loses is the forced restart of a branch whose merged history is still on the remote, which five places recommend: `.claude/hooks/git/reference-transaction`, `docs/worker.md`, `.claude/skills/docket/modes/capture.md`, `subprojects/docket/src/docket/render.py` and the docstring of `tools/branch_sweep.py`. It becomes `git merge origin/main`. The build must check that the `landed` answer of `arm` and `vcs.carried_merge` accept a branch restarted that way.
2. A tag ruleset on `v*` with the two default rules.
3. A required check, `merge-hold`, in `.github/workflows/quality.yml`. On a pull request that is not a draft it runs the rule of `bin/docket arm`, from the copy of the tooling on `main`, and fails on `hold`. GitHub will not merge a draft. A pull request that waits on the owner's read then needs the owner's answer recorded before the check passes. Recommended: the session records the owner's words in a commit trailer, as every other record `arm` reads is written. The alternative is an approval the owner gives on GitHub through an environment with a required reviewer, which a session cannot give because the app has no Deployments permission; it costs the owner a click on each held pull request.
4. "Restrict deletions" on all branches is not recommended yet. It closes only the REST route, since the proxy refuses the git one. It stops GitHub deleting a merged branch and stops the sweep, so it needs a bypass actor that is not the owner's account. The documentation read does not say whether a personal repository's ruleset accepts a deploy key or GitHub Actions on its bypass list.
5. Session side, after the settings: one check that reads GitHub's rules for a `claude/` branch and for `main` and fails where a rule above is missing, which is each past escape replayed against the place that refuses it; `direct_merge_guard.py` and the merge wording in `guard.sh` and `guard.py` removed; the git hooks and `gh_write_guard.py` kept as early warnings and for the email screen, with headers that say GitHub is what refuses; `PL-95BJ` closed on the proxy's refusal, with no new spelling taught to `push_targets`.

**Generator check.** A family head over the fact `PL-1ZZ0` names, which action a request performs whatever its spelling, client or text field. `PL-95BJ` and the guard leads in `PL-VZ57` are its members. The earlier heads each moved the check closer to the action and stayed inside the session. This one moves the refusal to the system that performs the action.
