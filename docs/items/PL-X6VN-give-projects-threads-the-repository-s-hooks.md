---
id: PL-X6VN
title: Give Projects threads the repository's hooks through a setup script that writes a session-start entry into ~/.claude/settings.json, since Claude Code skips .claude/settings.json in a thread by design
priority: P2
effort: S
status: done
classes: infra
feature: projects-trial
touches: .claude/hooks/thread_hooks.py, .claude/hooks/hook_input.py, .claude/hooks/stop_hook_patch.py, tests/unit/test_thread_hooks.py, tests/unit/test_stop_hook_patch.py, tests/unit/test_line_splits.py, docket.toml, docs/maintainer.md, docs/items/PL-X6VN-give-projects-threads-the-repository-s-hooks.md, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md
added: 2026-10-26
closed: 2026-10-26
pr: 1848
payoff: a Projects thread runs the repository's guard hooks and session-start digest, read from the one .claude/settings.json, once the owner pastes one setup script
verify: grep -q 'def test_a_project_thread_gets_the_repository_hooks_in_its_user_settings' tests/unit/test_thread_hooks.py
---

**Problem.** A Claude Projects thread runs none of the repository's hooks: not the Bash guards, not the session-start digest and not the stop hook patch. Claude Code's Projects documentation says a cloud thread skips `.claude/settings.json` by design (`PL-CR81` § "Documented, not a fault"). Every thread in the project therefore works without the checks the hooks enforce, and nothing tells it so.

**Why it matters.** The guards exist because sessions made the mistakes they refuse. A piped gate whose failure is hidden, a prune that destroys an unmerged item, and a direct push past the checks all become possible again in a thread. Most of the project's work now runs in threads.

**Done when.** A tested hook copies the repository's hooks into the user settings at each session start in a Projects thread, and `docs/maintainer.md` carries the setup script that runs it, checked against the hook's own copy. The end-to-end proof needs the owner's setting first: a new thread, started after the owner adds the script, should refuse `uv run pytest --version | head -1` through `gate-status-guard.sh` and carry the session-start digest in its first turn. That thread records the result in `PL-CR81`.

**Evidence.** `PL-CR81`'s paragraph "Narrowed 2026-10-26" records the probe. Claude Code in a Projects thread reads `~/.claude/settings.json` and hot-reloads it, but skips `.claude/settings.json` and `.claude/settings.local.json`. Copying the repository's `hooks` block into the user file made every repository hook fire, with `CLAUDE_PROJECT_DIR` set to the checkout.

**What was tried first.** One line in the cloud environment's setup script that writes the user file from the checkout's settings, for example `python3 -c "import json,os; d=json.load(open('.claude/settings.json')); os.makedirs(os.path.expanduser('~/.claude'), exist_ok=True); json.dump({'hooks': d['hooks']}, open(os.path.expanduser('~/.claude/settings.json'), 'w'))"`. Then start a thread and run `uv run pytest --version | head -1`. If `gate-status-guard.sh` refuses it, the stop-gap works. Two things are unknown: whether the setup script runs in the checkout, and whether the harness overwrites `~/.claude` after the script runs. The setup script is the project owner's setting, so a session can only propose the line.

**Not a recurrence of `PL-CR81`.** `bin/docket new` matched this filing to `PL-CR81` on the shared feature and path. This item is a stop-gap for that fault, not a second report of it, so the match was withdrawn.

**Route taken 2026-10-26.** The setup script holds only a pointer, never a copy of the hooks. A copy written by the setup script would go stale, because the environment's snapshot keeps it for about seven days, and it would be a second copy of `.claude/settings.json`. The setup script instead adds one `SessionStart` entry to `~/.claude/settings.json`, which runs `.claude/hooks/thread_hooks.py` from the checkout. At each session start in a Projects thread (`CLAUDE_CODE_ENTRYPOINT=remote_projects`), that hook copies the repository's `hooks` block into the user settings beside its own entry. Claude Code reloads the file and applies the hooks from its next tool call on, as this thread measured. On the first write it also runs the repository's own `SessionStart` commands and prints their output, because Claude Code has already chosen which session-start hooks to run. In any other session it does nothing, since those sessions load the repository's settings and a copy would run each hook twice. `python3 .claude/hooks/thread_hooks.py --setup-script` prints the script, `docs/maintainer.md` § "Give Projects threads the repository's hooks with one setup script" carries the copy the owner pastes, and a test fails when the two differ. Only the hooks are copied. The repository's `permissions` and `env` are left out, because the thread's own permission mode is the harness's and this item is about the guards.

**Still unmeasured.** Whether a file the setup script writes under `~/.claude` is still there when Claude Code starts. The cloud-environments documentation's own example writes `~/.claude/CLAUDE.md` from a setup script, which suggests it is. The first thread after the owner adds the script settles it with the probe that **Done when** names.

**Generator check.** Not a generator, and caused by none. It is one missing configuration path, the user settings, and one hook fills it. The project owner asked for it in so many words ("Do x6vn", 2026-10-26), which lifts the pause on new workflow mechanisms for this item.
