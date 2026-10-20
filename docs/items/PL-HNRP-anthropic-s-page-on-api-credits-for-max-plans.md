---
id: PL-HNRP
title: Anthropic's page on API credits for Max plans lists Claude Code as not covered, yet the headless worker runs claude -p on an API key and the Console's credit fell by the run's cost; find out whether the headless runner's use is covered before relying on it
status: untriaged
added: 2026-10-20
---

**Problem.** Anthropic's page on API credits for Max plans lists Claude Code as not covered, yet the headless worker runs claude -p on an API key and the Console's credit fell by the run's cost; find out whether the headless runner's use is covered before relying on it

**The conflict.** https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers (read 2026-10-20) has a "Doesn't cover" row that reads "Claude Code, extra usage in the Claude apps". It lists "Claude Agent SDK" as covered. Yet on 2026-10-19 the first headless run, `claude -p` on an API key, cost $2.10 by Claude Code's estimate, and the Console's credit fell from $200 to $197.72. So in practice the credit paid for it. Whether the page means Claude Code used through a Claude plan's own limits, or any use of Claude Code, the page does not say.

**Why it matters.** The whole runner is built on this credit. If the use is not covered, it could stop working or breach the program terms (https://www.anthropic.com/legal/credit-terms) without warning.

**Next step.** Read the program terms. If they do not settle it, the project owner asks Anthropic support. If the use is not covered, the runner could call the Agent SDK instead, which the page lists as covered.
