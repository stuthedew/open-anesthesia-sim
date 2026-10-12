---
id: PL-ZXCN
title: The hooks' shell scripts respell git facts vcs exports - where git's subcommand stands past git's own options (byte copies in no-prune-guard.sh and push-check-guard.sh), origin/main, the shallow test and git's output decoding - so `--git-dir X log` reads as subcommand X in vcs.subcommand_of and log in both hooks
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: .claude/hooks/no-prune-guard.sh, .claude/hooks/push-check-guard.sh, .claude/hooks/docket-digest.sh, subprojects/docket/src/docket/vcs.py, tests/unit/test_push_check_guard.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
payoff: git's command line reads one way in docket and in the hooks that guard a push or a prune
verify: grep -q 'def test_git_own_options_read_as_vcs_reads_them' tests/unit/test_push_check_guard.py
---

**Problem.** The hooks' shell scripts respell git facts vcs exports - where git's subcommand stands past git's own options (byte copies in no-prune-guard.sh and push-check-guard.sh), origin/main, the shallow test and git's output decoding - so `--git-dir X log` reads as subcommand X in vcs.subcommand_of and log in both hooks

- Where git's subcommand stands: `vcs.subcommand_of` takes a value only after `-c` and `-C`; `TAKES_A_WORD` and `own_options` in `no-prune-guard.sh` and `push-check-guard.sh` (copied, "as no-prune-guard.sh reads them") also take one after `--git-dir`, `--work-tree` and the rest. On `git --git-dir /x/.git log` vcs answers `/x/.git` and both hooks `log`. The hooks also share `EXPANDS` and `is_git` byte for byte.
- The remote and base: `push-check-guard.sh` passes `--verify-base origin/main` and `docket-digest.sh` names `origin`, beside `vcs.REMOTE` and `vcs.default_base`. They part on a clone whose default branch is `master`. `PL-9KLN` kept the literal deliberately and `PL-4NG0`'s literal sweep did not reach the `.sh` files.
- The shallow test: `docket-digest.sh` asks git itself beside `vcs.is_shallow`; they agree. `PL-4NG0` recorded that test as having no other reader.
- Decoding: `push-check-guard.sh`'s embedded `git()` runs with `text=True`, beside `lines.record_text`; a raw `\r` in a path from `rev-parse --show-toplevel` is translated there and kept by docket (`PL-0R4M`'s line-split test reads `.py` files only).

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** Each hook reads these facts through `docket.vcs` (or one shared helper both hooks import), and a test feeds `--git-dir /x/.git log` to `push-check-guard.sh` and asserts the subcommand vcs reads.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
