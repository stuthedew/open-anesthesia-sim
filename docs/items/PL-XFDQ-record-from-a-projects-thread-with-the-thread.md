---
id: PL-XFDQ
title: Record, from a Projects thread with the thread-probe plugin added in Project settings > Plugins, whether the plugin's hook refused echo thread-probe-sentinel, whether its SessionStart line printed, and whether the Skill tool lists thread-probe, so PL-SQV9's plugin route is proven or dropped
status: untriaged
feature: projects-trial
added: 2026-10-31
---

**Problem.** Record, from a Projects thread with the thread-probe plugin added in Project settings > Plugins, whether the plugin's hook refused echo thread-probe-sentinel, whether its SessionStart line printed, and whether the Skill tool lists thread-probe, so PL-SQV9's plugin route is proven or dropped

**How.** `PL-SQV9` put a test plugin, `thread-probe`, in this repository, which is also a plugin marketplace through `.claude-plugin/marketplace.json`. The owner adds it in the project's **Project settings > Plugins** and starts a new thread. The thread runs `echo thread-probe-sentinel` as its first command. The plugin's hook refuses that command if it runs, and gives the hook's environment as the reason. The thread then says whether the session start printed a `thread-probe:` line, and whether the Skill tool lists `thread-probe`.

**Done when.** A paragraph here records the three results and the hook's reason text. If all three hold, file the item that builds the real plugin, whose hooks read `.claude/settings.json` when they run. If they do not, delete `plugins/thread-probe/` and `.claude-plugin/`, and `PL-X6VN`'s setup script in `docs/maintainer.md` remains the route.
