---
id: PL-SQV9
title: Test giving Projects threads the repository's hooks and skills as a plugin added in Project settings > Plugins, which Claude Code's Projects docs say loads into each new cloud thread; if its hooks fire there, it replaces PL-X6VN's setup-script stop-gap and also restores the four skills
priority: P2
effort: S
status: done
feature: projects-trial
touches: docs/items/PL-SQV9-test-giving-projects-threads-the-repository-s.md, docs/items/PL-XFDQ-record-from-a-projects-thread-with-the-thread.md, .claude-plugin/marketplace.json, .claude/thread-probe-plugin, tests/unit/test_thread_probe.py, docket.toml, tools/rules_paths_check.py
added: 2026-10-31
closed: 2026-10-31
pr: 1902
payoff: the owner knows whether a plugin added in Project settings > Plugins gives a Projects thread the repository's hooks and skills, and so whether it can replace PL-X6VN's setup-script stop-gap
verify: uv run pytest -q tests/unit/test_thread_probe.py
---

**Why it matters.** Every Projects thread runs without the repository's guard hooks and skills, and nothing tells it so. The setup-script stop-gap gives back only the hooks, through behaviour the documentation does not promise.

**Problem.** Test giving Projects threads the repository's hooks and skills as a plugin added in Project settings > Plugins, which Claude Code's Projects docs say loads into each new cloud thread; if its hooks fire there, it replaces PL-X6VN's setup-script stop-gap and also restores the four skills

**Evidence, read 2026-10-31.** Claude Code's Projects page, § "What threads pick up from your repositories" (https://code.claude.com/docs/en/claude-projects.md), lists "Plugins enabled in `.claude/settings.json`" as "Not loaded. Add the plugin in **Project settings > Plugins** instead". Its section "Get skills, plugins, connectors, and tools into threads" says plugins added there "load into each new cloud thread". A plugin can carry hooks and skills. The same table says hooks in `.claude/settings.json` are "Not run", and the only route it gives for them is running the thread on your own computer. So the page does not say whether a plugin's hooks run in a cloud thread. That is the question to test.

**Why it may be better than `PL-X6VN`.** The setup-script stop-gap relies on two undocumented behaviours: that a thread reads `~/.claude/settings.json`, and that it reloads that file mid-session. `PL-CR81` measured both on 2026-10-26, but the documentation promises neither. A plugin is the route the documentation names. It would also bring back the `docket`, `pull-request`, `run-the-app` and `model-review` skills, which the stop-gap does not.

**Others hit the same change.** `anthropics/claude-code#89215` (https://github.com/anthropics/claude-code/issues/89215) reported a repository's hooks silently ignored in a web session with two repositories. Its workaround was the same as `PL-X6VN`'s: a setup script that merges the hooks into `~/.claude/settings.json`, "Confirmed working". A bot closed it as stale on 2026-10-18, and Anthropic never replied. A third-party docs mirror dates the change for Projects threads to Claude Code v2.1.306 (https://github.com/thevibeworks/claude-code-docs/pull/1395).

**Open questions for the test.** Whether **Project settings > Plugins** can add a plugin from a private repository's marketplace. Whether a plugin's hook gets `CLAUDE_PROJECT_DIR` pointing at the checkout, which every repository hook script relies on. Whether the plugin's copy of the hooks can read `.claude/settings.json` at run time, so the two cannot drift apart. That last one matters because of the one-source-of-truth rule.

**Done when.** The test plugin is on `main`, where Project settings > Plugins can find it. Running it in a thread and recording what it showed is a separate item, so that this one can merge before the owner runs the test. The 2026-10-31 split put that step there.

**Generator check.** A one-off test of an external behaviour, not a mechanism that causes items. If the plugin route works, the item that builds the real plugin replaces `PL-X6VN`'s stop-gap rather than adding a second one.

**Test plugin built 2026-10-31.** The owner asked to test this route straight away, without first adding `PL-X6VN`'s setup script, so that a refusal in a thread can only come from the plugin. `.claude-plugin/marketplace.json` makes this repository a plugin marketplace with one plugin, `.claude/thread-probe-plugin/`. Its only hook, `hooks/probe.py`, refuses any Bash command containing `thread-probe-sentinel`. At session start it prints one line naming `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT`, the working directory, and whether the repository's `.claude/settings.json` can be read from there. Its one skill, `thread-probe`, replies `thread-probe skill loaded`. The plugin answers the open questions above except the first, which the owner answers by adding it: the documentation does not say which sources **Project settings > Plugins** accepts. `tests/unit/test_thread_probe.py` runs the hook as Claude Code would.

**To record from the thread, in `PL-XFDQ`.** Whether `echo thread-probe-sentinel` was refused, with the reason the hook gave. Whether the session start printed the `thread-probe:` line. Whether the Skill tool lists `thread-probe`. If all three hold, the next step is a real plugin whose hooks read `.claude/settings.json` when they run, so that the plugin holds no second copy of them. If they do not, the setup script in `docs/maintainer.md` remains the route, and the test plugin and the marketplace file are deleted.
