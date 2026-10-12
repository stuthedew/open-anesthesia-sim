---
id: PL-FB77
title: Hook boilerplate is copied per hook - the Bash command a payload carries (four .sh copies), which checkout a hook acts on (five sites) and the check-report headers push-check-guard.sh excerpts - and with CLAUDE_PROJECT_DIR unset docket-branch-guard.sh exits where the other four fall back to the hooks directory's grandparent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: .claude/hooks/docket-branch-guard.sh, .claude/hooks/docket-digest.sh, .claude/hooks/item_read_log.py, .claude/hooks/stop_hook_patch.py, .claude/hooks/push-check-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/no-prune-guard.sh, tests/unit/test_docket_branch_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
payoff: every hook acts on the same checkout and reads its payload one way
verify: grep -q 'def test_an_unset_project_dir_falls_back_as_the_other_hooks_do' tests/unit/test_docket_branch_guard.py
---

**Problem.** Hook boilerplate is copied per hook - the Bash command a payload carries (four .sh copies), which checkout a hook acts on (five sites) and the check-report headers push-check-guard.sh excerpts - and with CLAUDE_PROJECT_DIR unset docket-branch-guard.sh exits where the other four fall back to the hooks directory's grandparent

- The Bash command a hook payload carries: identical extraction in `floor-interpreter-guard.sh`, `gate-status-guard.sh`, `no-prune-guard.sh` and `push-check-guard.sh`; they agree today.
- Which checkout a hook acts on: `docket-branch-guard.sh`, `docket-digest.sh`, `item_read_log.repo_root`, `stop_hook_patch.project_root` and `push-check-guard.sh`. With `CLAUDE_PROJECT_DIR` unset, `docket-branch-guard.sh` answers none and exits, and the other four fall back to the hooks directory's grandparent.
- The section headers of a check report: `push-check-guard.sh`'s `excerpt` reads the headers `tools/doc_check.py` and `docket.render` print; they agree today.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** The hooks take the payload command and the checkout from one shared helper, `docket-branch-guard.sh` falls back as the others do (or all refuse alike), and a test runs it with the variable unset.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
