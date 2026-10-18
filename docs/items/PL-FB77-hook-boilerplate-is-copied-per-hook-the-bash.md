---
id: PL-FB77
title: Hook boilerplate is copied per hook - the Bash command a payload carries (four .sh copies), which checkout a hook acts on (five sites) and the check-report headers push-check-guard.sh excerpts - and with CLAUDE_PROJECT_DIR unset docket-branch-guard.sh exits where the other four fall back to the hooks directory's grandparent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.28
touches: .claude/hooks/hook_input.py, .claude/hooks/docket-branch-guard.sh, .claude/hooks/docket-digest.sh, .claude/hooks/item_read_log.py, .claude/hooks/stop_hook_patch.py, .claude/hooks/push-check-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/no-prune-guard.sh, tests/unit/test_docket_branch_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
pr: 1562
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

**Resolved 2026-10-18.** The new `.claude/hooks/hook_input.py` holds both
readings. `project_root()` returns the checkout: `CLAUDE_PROJECT_DIR` when it
is set, and otherwise the clone the file sits in. `bash_call()` returns the
Bash command and working directory a payload carries, or `None` when the
payload is not a Bash call. The four Bash guards import it in place of their
four copies of the payload parse. `item_read_log.py` and `stop_hook_patch.py`
import `project_root` in place of their own. `docket-branch-guard.sh` and
`docket-digest.sh` run the module as a script, which prints the checkout. So
the branch guard now falls back as the others do, rather than exiting with
nothing said. `test_an_unset_project_dir_falls_back_as_the_other_hooks_do`
runs a copy of the guard with the variable unset and expects the claim
question. Against the guard on `origin/main` it fails with
`AssertionError: assert 'this branch claims nothing' in ''`. The test that
the guard lets an edit through when it cannot run had relied on the unset
variable, so it now names a checkout without `bin/docket`. The check-report
headers that `push-check-guard.sh` excerpts are left as they are: the
done-when names only the command and the checkout, and the headers still
agree with what `tools/doc_check.py` and `docket.render` print.
