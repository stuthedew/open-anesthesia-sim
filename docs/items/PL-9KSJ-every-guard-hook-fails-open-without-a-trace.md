---
id: PL-9KSJ
title: Every guard hook fails open without a trace: each discards stderr and exits 0 on a crash, so a broken guard reads to the session exactly as a pass, including no-prune-guard.sh, the one guarding an irreversible loss
priority: P1
effort: M
status: done
classes: defect
feature: guards-say-when-they-cannot-check
milestone: v0.6.15
touches: .claude/hooks/guard.sh, .claude/hooks/guard.py, .claude/hooks/hook_input.py, .claude/settings.json, .claude/hooks/floor_interpreter_guard.py, .claude/hooks/gate_status_guard.py, .claude/hooks/gh_write_guard.py, .claude/hooks/push_check_guard.py, .claude/hooks/direct_merge_guard.py, .claude/hooks/docket_branch_guard.py, .claude/hooks/owner_ask_guard.py, .claude/hooks/shell_split.py, tools/regex_check.py, tools/pr_body_check.py, tests/unit/test_guard.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_gate_status_guard.py, tests/unit/test_gh_write_guard.py, tests/unit/test_push_check_guard.py, tests/unit/test_direct_merge_guard.py, tests/unit/test_docket_branch_guard.py, tests/unit/test_owner_ask_guard.py, tests/unit/test_regex_guard.py, tests/unit/test_pr_body_check.py, tests/unit/test_hook_blocks.py, tests/unit/test_line_splits.py, docs/apparatus.md, docs/maintainer.md, docs/worker.md, docs/resident-instructions.md, docs/hook-blocks/README.md, .claude/skills/docket/modes/coordinator.md, .claude/skills/pull-request/SKILL.md, docs/items/PL-SG93-the-bash-guard-hooks-account-for-74-defects.md, docs/items/PL-NDY5-pr-body-email-guard-sh-imports-docket-at-load.md, docs/items/PL-5R11-push-check-guard-sh-tells-a-session-to-push.md, docket.toml, docs/items/PL-X4MD-the-owner-ask-guard-guesses-which-projects.md
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-04
pr: 1990
payoff: a guard that breaks says so in the session, instead of reading as a pass while the action it guards goes through
verify: grep -q 'def test_a_crashing_guard_says_it_did_not_check' tests/unit/test_guard.py && grep -q 'def test_every_hook_on_a_tool_call_runs_through_the_entry_point' tests/unit/test_guard.py
root-cause-of: PL-B5K1, PL-DST3, PL-NDY5, PL-KW5K
generator: spent - every guard on a tool call now runs through guard.py, which writes the failure path once, and tests/unit/test_guard.py refuses a hook wired around it
misread: Whether a guard actually read and checked the call it let through
---

**Problem.** Every guard hook fails open without a trace: each discards stderr and exits 0 on a crash, so a broken guard reads to the session exactly as a pass, including no-prune-guard.sh, the one guarding an irreversible loss

**Reproduced 2026-11-03.** With a `json.py` that raises put first on
`PYTHONPATH`, `no-prune-guard.sh` given `git fetch --prune` exited 0 with empty
stdout and empty stderr. The same call without the poisoned path is refused.
So a crash inside a guard reads to the session exactly as a pass.

<!-- absent: no-prune-guard.sh -->

**Why it matters.** The guards exist for actions a session cannot take back: a
pruned ref, a merge, an email address published on GitHub. A guard that has
stopped working says nothing, so a session goes on trusting it, and the one
signal that it broke is the loss it was meant to prevent.
`.claude/rules/apparatus-standard.md` § "The floor" asks every answer the
apparatus gives to be true or to say what it could not read, and a silent pass
is neither.

**Done when.** A guard that cannot read or judge a call still lets it through,
but says so in the context the session reads, naming the guard and the error,
and a test runs each guard with a crashing interpreter and finds that note.

**Generator check.** The fact misread is whether a guard actually checked the
call it let through. No head's `misread:` states it. The four members below
misread it by different routes: a payload too large to hand over
(`PL-B5K1`), a check killed at its deadline (`PL-DST3`), an import that fails
on swallowed stderr (`PL-NDY5`) and an entrypoint the bridge does not
recognise (`PL-KW5K`). Each guard hand-rolls its own failure path, and every
new guard copies the exit-0 shape, so the cluster is live.

**Checked 2026-11-03, under `PL-2GDW`.** Fix this once, in one entry point that every guard runs through, and not as one fail-loud block per guard. This head's own generator line names the mechanism: each guard hand-rolls its failure path, and each new guard copies the shape. The Done-when above can be met by eight copies of one block, and the next guard to be written would then copy whichever one it was modelled on. `CLAUDE.md`'s rule that a shared fact has one source of truth asks for the shape fix instead. That means one module that reads the hook payload once from standard input, runs the guard's own check, and turns any crash or timeout into the note this item asks for. A test then refuses any hook named in `.claude/settings.json` that does not run through that module. The same module removes `PL-B5K1` (the payload handed over in an environment variable), and the per-guard interpreter start-up that `PL-NDY5` and `PL-J22P` measured. It is also where `PL-1ZZ0`'s single check of each action would live. `PL-S3TF` already moves every guard's Python into modules, and it was claimed with `PL-B5K1` on #1990 while `PL-1ZZ0`'s cluster was claimed on #1991, 30 minutes apart and on the same hook files. So build the entry point as part of `PL-S3TF`, and land this item and `PL-1ZZ0`'s guards on it, rather than in parallel. This is work on a live generator, so the pause on new workflow mechanisms does not hold it.

**Next steps, 2026-11-03.** The thread that took this item on #1990 reached
its spend budget after `PL-S3TF`'s first slice, `PL-B5K1`'s fix for four
guards, and `PL-DST3`. The carry thread on the same branch listed six steps:
port #1989's edits, port the last shell guard, build one entry point, test
it, check git's own hooks, then `PL-KW5K` and `PL-NDY5`.

**Done, 2026-11-04.** Every guard on a tool call now runs through one entry
point (project owner, 2026-11-03, ratified, over one fail-loud block copied
into each guard).

1. `.claude/settings.json` wires `.claude/hooks/guard.sh` once for each set
   of tools, with a group name: `pre-edit`, `pre-bash`, `pre-mcp` or
   `post-bash`. `guard.sh` starts `guard.py`, and `guard.py` runs every guard
   of the group from one Python start. `GROUPS` in `guard.py` lists them.
2. A guard that raises, prints something other than a hook's output, or runs
   past its deadline lets the call through, and the note names the guard and
   the error. Each guard's own deadline sits inside the wiring's `timeout`.
3. Two guards refuse instead, through their `unjudged` rule. The merge guard
   refuses a call that mentions a merge (`PL-NXRJ`), and the gh guard refuses
   a Bash call that names `gh` (`PL-3986`).
4. `guard.sh` gives the same note, or the same merge refusal, when `python3`
   is missing or dies before `guard.py` decides, as it does on a broken
   standard library.
5. `tests/unit/test_guard.py` runs every guard through both halves with a
   crashing rule, a failing `python3` and a planted `json.py`. It refuses any
   hook in `.claude/settings.json` that does not start at `guard.sh`, unless
   it names the hook with a reason.
6. The branch guard's Python moved into `docket_branch_guard.py`, which closes
   `PL-S3TF`. The per-guard launchers are gone, and with them the per-guard
   Python starts behind `PL-J22P`.
7. Git's own hooks in `.claude/hooks/git/` do not pass silently. `pre-push`
   prints a warning when the email screen cannot run, and
   `reference-transaction` refuses in shell and uses Python only to log.

**Left open.** `PL-KW5K` is a different mechanism: `thread_hooks.py` copies
the hooks into a thread, and judges no call. `PL-NDY5` keeps its cost: the
email guard still imports `docket` at load, about 150 ms on every MCP call.
An import failure there is now said in a note, so what is left is the cost
and keeping the screen working while `docket` is broken.

**Residual risk.** A line bash cannot parse in `guard.sh` makes bash exit 2,
which Claude Code takes for a refusal of every call it is wired on. The
script is kept short and free of rules so that a merge rarely touches it, and
a test runs `bash -n` on it.

`PL-TLPH`'s refusals stay as refusals. Turning any guard from refusing to
warning is the project owner's call.
