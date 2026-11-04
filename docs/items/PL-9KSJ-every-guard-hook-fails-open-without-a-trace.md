---
id: PL-9KSJ
title: Every guard hook fails open without a trace: each discards stderr and exits 0 on a crash, so a broken guard reads to the session exactly as a pass, including no-prune-guard.sh, the one guarding an irreversible loss
priority: P1
effort: M
status: ready
classes: defect
feature: guards-say-when-they-cannot-check
touches: .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/push-check-guard.sh, .claude/hooks/docket-branch-guard.sh, .claude/hooks/direct-merge-guard.sh, .claude/hooks/pr-body-email-guard.sh, .claude/hooks/regex-guard.sh, .claude/hooks/hook_input.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
payoff: a guard that breaks says so in the session, instead of reading as a pass while the action it guards goes through
verify: grep -q 'def test_a_crashing_guard_says_it_did_not_check' tests/unit/test_no_prune_guard.py
root-cause-of: PL-B5K1, PL-DST3, PL-NDY5, PL-KW5K
generator: live - every guard hand-rolls its own failure path and each new guard copies the exit-0 shape, so a review of the hooks found four members on one day
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
