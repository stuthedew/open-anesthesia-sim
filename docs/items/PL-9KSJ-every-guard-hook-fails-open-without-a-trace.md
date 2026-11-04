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
