---
id: PL-9KSJ
title: Every guard hook fails open without a trace: each discards stderr and exits 0 on a crash, so a broken guard reads to the session exactly as a pass, including no-prune-guard.sh, the one guarding an irreversible loss
priority: P1
effort: M
status: ready
classes: defect
feature: guards-say-when-they-cannot-check
touches: .claude/hooks/no-prune-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/push-check-guard.sh, .claude/hooks/docket-branch-guard.sh, .claude/hooks/direct-merge-guard.sh, .claude/hooks/pr-body-email-guard.sh, .claude/hooks/regex-guard.sh, .claude/hooks/hook_input.py, tests/unit/test_no_prune_guard.py
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

**Next steps, 2026-11-03.** The thread that took this item on #1990 reached
its spend budget after `PL-S3TF`'s first slice, `PL-B5K1`'s fix for four
guards, and `PL-DST3`. In order:

1. #1989 (`PL-J22P` and seven others) merged on 2026-11-03 as `263b9ce9`.
   Merge `main` into this branch now, and again once #1991 (`PL-1ZZ0`)
   merges. #1989 changes Python that now lives in the new
   modules, so port it by hand: the floor guard's `-m` reading (`PL-SMM1`),
   the gate guard's `NO_VERDICT`, `ANNOUNCERS` and `announces` (`PL-9PPJ`),
   its `&&` remedy text (`PL-VDK9`), and the merge guard's timeout comment
   (`PL-KJN6`). #1991 edits the headers of the same four `.sh` files and the
   `PL-S3TF` item. Keep both sides.
2. Port `docket-branch-guard.sh`'s Python into a module and close
   `PL-S3TF`. Since `PL-J22P` the script holds a single `python3 -c`.
   `PL-B5K1` closes once #1991 has merged, when its `verify:` passes.
3. Build the one failure path. A draft is at
   `/mnt/project-files/v0.7.0/pl-9ksj/guard_launch.sh`. Each wired `.sh`
   sources it and starts its Python through `launch_guard`. When `python3`
   is missing or exits non-zero, `launch_guard` prints a note in
   `additionalContext` naming the guard and Python's last line on standard
   error. Putting the catch in the shell covers a crash on import, which a
   `try` in Python cannot. `regex-guard.sh` then uses it, and the catch-all in
   `tools/regex_check.py`'s `main` goes; its `unchecked` stays for a file that
   does not parse. The direct-merge guard keeps refusing a merge call when
   Python fails (`PL-NXRJ`) and gets the note on any other call. Cover
   `gh_write_guard.py` from #1991, which fails closed on `gh` alone, and
   `owner_ask_guard.py`, which `.claude/settings.json` runs as bare `python3`
   and #1984 is refactoring.
4. Make the next guard fail a test if it skips the launcher. Add
   `test_a_crashing_guard_says_it_did_not_check`, parametrized over every
   guard `.claude/settings.json` wires. It runs each with a `python3` on the
   `PATH` that exits 1, and with a `json.py` that raises first on
   `PYTHONPATH`, and finds the note, or the refusal for a merge call. A wired
   hook that does not start through `launch_guard` fails it unless the test
   lists the hook with a reason. Rewrite this item's `verify:` to that test,
   because #1991 deletes `tests/unit/test_no_prune_guard.py`.
5. Read what #1991's git hooks (`reference-transaction`, `pre-push`) do when
   their Python fails, and bring them under the same rule if they pass
   silently.
6. Then `PL-KW5K` (after #1989, which edits `thread_hooks.py`) and `PL-NDY5`
   (after #1991, which edits `tools/pr_body_check.py`).

`PL-TLPH`'s refusals stay as refusals. Turning any guard from refusing to
warning is the project owner's call.
