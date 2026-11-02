---
id: PL-NZJG
title: direct-merge-guard.sh and pr-body-email-guard.sh are wired on exact GitHub MCP tool names (merge_pull_request, create_pull_request, update_pull_request), so a rename by the GitHub server stops both guards with no sign; widen each to the namespace or say in its header what goes unchecked, as owner_ask_guard.py now does (found building PL-YN60)
priority: P2
effort: S
status: untriaged
classes: defect
feature: guard-tool-names
touches: .claude/hooks/direct-merge-guard.sh, .claude/hooks/pr-body-email-guard.sh, .claude/settings.json, tools/pr_body_check.py, tests/unit/test_direct_merge_guard.py, tests/unit/test_pr_body_check.py, tests/unit/test_hook_blocks.py, docs/apparatus.md, docs/items
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-02
payoff: a merge or an email address sent to GitHub is still checked after the GitHub server renames or folds its tools, instead of passing both guards unseen
---

**Problem.** direct-merge-guard.sh and pr-body-email-guard.sh are wired on exact GitHub MCP tool names (merge_pull_request, create_pull_request, update_pull_request), so a rename by the GitHub server stops both guards with no sign; widen each to the namespace or say in its header what goes unchecked, as owner_ask_guard.py now does (found building PL-YN60)

**Why it matters.** The merge guard is what stops a session landing a stale
branch on `main` while admins are exempt from its checks (`PL-NXRJ`), and
the email guard keeps the owner's address out of text that GitHub publishes
at once and never forgets (`PL-7K31`). Both were wired on exact tool names
that the GitHub server owns. A rename would have turned both off without a
sign, and their tests would still have passed, because the tests pinned the
same names. `PL-YN60` found the same failure in `owner_ask_guard.py` after
the Projects tools were renamed.

**Generator check.** Not a generator: two items so far. The mechanism is a
guard wired on tool names that another system owns, and its instances are
`PL-YN60` and this item. A search of `.claude/settings.json` on 2026-11-02
found no other hook wired on an MCP tool name. `PL-YN60` added the rule that
stops a third, in `.claude/rules/apparatus-standard.md` § "The floor".

**Next steps, written 2026-11-02 before a reset for length.** The project
owner asked for this fix on 2026-11-02, right after `PL-YN60`. Build it on a
fresh branch from `main` once `#1931` has merged, since this file arrives
with it.

1. Triage the item: priority, effort, classes, touches, payoff, Done when,
   verify.
2. Read both hooks whole. `direct-merge-guard.sh` lets a session's merge
   through only while GitHub holds it to the base branch's checks (`PL-NXRJ`).
   `pr-body-email-guard.sh` refuses a pull request title or body that holds
   the owner's email address.
3. Widen each `.claude/settings.json` matcher so that a renamed GitHub tool
   still reaches its hook, and let each script decide which calls it judges.
   This follows `.claude/rules/apparatus-standard.md` § "The floor", the
   paragraph on guards keyed on names another system owns. Two hazards to
   test: `enable_pr_auto_merge` contains "merge" and must pass the merge
   guard untouched, and most `pull_request` tools carry no title or body, so
   the email guard must pass any call without one. Where widening would
   refuse real work, say instead in the hook's header what goes unchecked
   when a name changes.
4. Add regression tests that fail against today's matchers: a renamed merge
   tool, and a renamed create or update tool carrying the email address.

**Done when.** A renamed GitHub tool still reaches both guards. A merge
under another name, or folded into a write tool with a `method` of `merge`,
is judged as a merge. An email address in a title or body sent to GitHub is
refused whatever the tool is called. `enable_pr_auto_merge`, reads and a
Projects thread's posts pass both guards untouched. Each hook's header says
what still goes unchecked after a rename.

**What was built, 2026-11-02.** Both guards are wired on one
`^mcp__.*$` entry in `.claude/settings.json`, and each script decides which
calls it judges.

- `direct-merge-guard.sh` takes a call for a merge when its tool's own name
  contains "merge", or when its `method` is `merge`. The GitHub server has
  already folded its issue and review tools into `issue_write` and
  `pull_request_review_write`, which take a `method` (read from this
  session's tool schemas, 2026-11-02). It names the two tools it skips,
  `enable_pr_auto_merge` and `disable_pr_auto_merge`. Where it cannot judge a
  call, because python3 fails or the payload names no tool, it refuses the
  call only if its text contains "merge". Before, it refused every such
  payload, which was safe only while the matcher had already chosen a merge.
- `pr_body_check.screen` reads a call by its fields, not its tool's name: a
  call that names a repository by `owner` and `repo` and carries a `title` or
  `body`. So an issue, a comment and a review are screened too, which is the
  namespace widening this item asked for. A Projects thread's post or an
  email names no repository and is not read. The read-back note moved into
  `pr_body_check.read_back`. It goes only on a pull request call that carries
  a title or a body, so that it does not follow every MCP call.

**Regression proof.** The new tests were copied into a worktree of
`origin/main` and run there with
`pytest -q tests/unit/test_direct_merge_guard.py tests/unit/test_pr_body_check.py tests/unit/test_hook_blocks.py`:
24 failed and 77 passed. Among the failures are
`test_a_merge_under_another_name_is_judged[renamed]`, where `main`'s hook let
`mcp__github__merge_pr` through while admins were exempt, and
`test_an_email_address_sent_to_github_under_any_tool_name_is_refused[comment]`,
where `main`'s screen let `add_issue_comment` publish the address. The seven
`read_back` cases fail there only because that function is new. On this
branch all 101 pass.

**Cost.** Every MCP call now runs both scripts, and Claude Code runs matching
hooks in parallel (https://code.claude.com/docs/en/hooks.md, read
2026-11-02). Measured here, the merge guard takes about 65 ms on a call it
does not judge and the email guard about 165 ms, most of it importing
`tools/pr_body_check.py`'s `docket` modules.
