---
id: PL-SQV9
title: Test giving Projects threads the repository's hooks and skills as a plugin added in Project settings > Plugins, which Claude Code's Projects docs say loads into each new cloud thread; if its hooks fire there, it replaces PL-X6VN's setup-script stop-gap and also restores the four skills
status: untriaged
feature: projects-trial
added: 2026-10-31
---

**Problem.** Test giving Projects threads the repository's hooks and skills as a plugin added in Project settings > Plugins, which Claude Code's Projects docs say loads into each new cloud thread; if its hooks fire there, it replaces PL-X6VN's setup-script stop-gap and also restores the four skills

**Evidence, read 2026-10-31.** Claude Code's Projects page, § "What threads pick up from your repositories" (https://code.claude.com/docs/en/claude-projects.md), lists "Plugins enabled in `.claude/settings.json`" as "Not loaded. Add the plugin in **Project settings > Plugins** instead". Its section "Get skills, plugins, connectors, and tools into threads" says plugins added there "load into each new cloud thread". A plugin can carry hooks and skills. The same table says hooks in `.claude/settings.json` are "Not run", and the only route it gives for them is running the thread on your own computer. So the page does not say whether a plugin's hooks run in a cloud thread. That is the question to test.

**Why it may be better than `PL-X6VN`.** The setup-script stop-gap relies on two undocumented behaviours: that a thread reads `~/.claude/settings.json`, and that it reloads that file mid-session. `PL-CR81` measured both on 2026-10-26, but the documentation promises neither. A plugin is the route the documentation names. It would also bring back the `docket`, `pull-request`, `run-the-app` and `model-review` skills, which the stop-gap does not.

**Others hit the same change.** `anthropics/claude-code#89215` (https://github.com/anthropics/claude-code/issues/89215) reported a repository's hooks silently ignored in a web session with two repositories. Its workaround was the same as `PL-X6VN`'s: a setup script that merges the hooks into `~/.claude/settings.json`, "Confirmed working". A bot closed it as stale on 2026-10-18, and Anthropic never replied. A third-party docs mirror dates the change for Projects threads to Claude Code v2.1.306 (https://github.com/thevibeworks/claude-code-docs/pull/1395).

**Open questions for the test.** Whether **Project settings > Plugins** can add a plugin from a private repository's marketplace. Whether a plugin's hook gets `CLAUDE_PROJECT_DIR` pointing at the checkout, which every repository hook script relies on. Whether the plugin's copy of the hooks can read `.claude/settings.json` at run time, so the two cannot drift apart. That last one matters because of the one-source-of-truth rule.

**Done when.** A thread in the project, started with the plugin added, runs `uv run pytest --version | head -1`, and this item records whether `gate-status-guard.sh` refused it and whether the Skill tool lists `docket`.
