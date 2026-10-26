---
id: PL-X6VN
title: Try a setup-script line that copies .claude/settings.json's hooks into ~/.claude/settings.json, so Projects threads run the repository's guards until PL-CR81's product fault is fixed; a thread on 2026-10-26 showed that user settings are read and the copied hooks fire
status: untriaged
feature: projects-trial
added: 2026-10-26
---

**Problem.** Try a setup-script line that copies .claude/settings.json's hooks into ~/.claude/settings.json, so Projects threads run the repository's guards until PL-CR81's product fault is fixed; a thread on 2026-10-26 showed that user settings are read and the copied hooks fire

**Evidence.** `PL-CR81`'s paragraph "Narrowed 2026-10-26" records the probe. Claude Code in a Projects thread reads `~/.claude/settings.json` and hot-reloads it, but skips `.claude/settings.json` and `.claude/settings.local.json`. Copying the repository's `hooks` block into the user file made every repository hook fire, with `CLAUDE_PROJECT_DIR` set to the checkout.

**What to try.** One line in the cloud environment's setup script that writes the user file from the checkout's settings, for example `python3 -c "import json,os; d=json.load(open('.claude/settings.json')); os.makedirs(os.path.expanduser('~/.claude'), exist_ok=True); json.dump({'hooks': d['hooks']}, open(os.path.expanduser('~/.claude/settings.json'), 'w'))"`. Then start a thread and run `uv run pytest --version | head -1`. If `gate-status-guard.sh` refuses it, the stop-gap works. Two things are unknown: whether the setup script runs in the checkout, and whether the harness overwrites `~/.claude` after the script runs. The setup script is the project owner's setting, so a session can only propose the line.

**Not a recurrence of `PL-CR81`.** `bin/docket new` matched this filing to `PL-CR81` on the shared feature and path. This item is a stop-gap for that fault, not a second report of it, so the match was withdrawn.
