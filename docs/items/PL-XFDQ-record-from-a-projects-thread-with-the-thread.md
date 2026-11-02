---
id: PL-XFDQ
title: Record, from a Projects thread with the thread-probe plugin added in Project settings > Plugins, whether the plugin's hook refused echo thread-probe-sentinel, whether its SessionStart line printed, and whether the Skill tool lists thread-probe, so PL-SQV9's plugin route is proven or dropped
priority: P2
effort: S
status: ready
classes: infra
feature: projects-trial
touches: docs/items, .claude/thread-probe-plugin, .claude-plugin
added: 2026-10-31
payoff: the owner learns whether a plugin gives Projects threads the repository's hooks and skills, and so whether the setup-script stop-gap can go
verify: grep -q '^\*\*Run in a thread' docs/items/PL-XFDQ*.md
not-delegable: only a Projects thread can run the probe, after the owner adds the thread-probe plugin in Project settings > Plugins; no other session runs in the environment the test measures
---

**Problem.** Record, from a Projects thread with the thread-probe plugin added in Project settings > Plugins, whether the plugin's hook refused echo thread-probe-sentinel, whether its SessionStart line printed, and whether the Skill tool lists thread-probe, so PL-SQV9's plugin route is proven or dropped

**How.** `PL-SQV9` put a test plugin, `thread-probe`, in this repository, which is also a plugin marketplace through `.claude-plugin/marketplace.json`. The owner adds it in the project's **Project settings > Plugins** and starts a new thread. The thread runs `echo thread-probe-sentinel` as its first command. The plugin's hook refuses that command if it runs, and gives the hook's environment as the reason. The thread then says whether the session start printed a `thread-probe:` line, and whether the Skill tool lists `thread-probe`.

**Done when.** A paragraph here, opening `**Run in a thread`, records the three results and the hook's reason text. If all three hold, file the item that builds the real plugin, whose hooks read `.claude/settings.json` when they run. If they do not, delete `.claude/thread-probe-plugin/` and `.claude-plugin/`, and `PL-X6VN`'s setup script in `docs/maintainer.md` remains the route.

**Why it matters.** Projects threads do not run the repository's hooks. Without
`PL-X6VN`'s setup script, a thread works without the guards those hooks
enforce, such as the refusal of a pipe that hides a gate's exit status. That
script relies on two behaviours the documentation does not promise
(`PL-SQV9`). Threads also lack the `docket`, `pull-request`, `run-the-app` and
`model-review` skills. A plugin added in Project settings is the documented
route for both. The test plugin and the marketplace file stay on `main` until
this result decides whether to build on them or delete them.

**Generator check.** One-off. It records a measurement the owner asked for
(`PL-SQV9`), and does not misread a fact that causes other items.
