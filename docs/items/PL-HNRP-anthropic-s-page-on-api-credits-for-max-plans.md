---
id: PL-HNRP
title: Anthropic's page on API credits for Max plans lists Claude Code as not covered, yet the headless worker runs claude -p on an API key and the Console's credit fell by the run's cost; find out whether the headless runner's use is covered before relying on it
priority: P2
effort: S
status: done
classes: infra
milestone: v0.6.3
touches: tools/headless_worker.py
added: 2026-10-20
closed: 2026-10-24
pr: 1758
not-delegable: the answer is an external terms question settled by the project owner's word; no command in this tree can check it
---

**Problem.** Anthropic's page on API credits for Max plans lists Claude Code as not covered, yet the headless worker runs claude -p on an API key and the Console's credit fell by the run's cost; find out whether the headless runner's use is covered before relying on it

**The conflict.** https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers (read 2026-10-20) has a "Doesn't cover" row that reads "Claude Code, extra usage in the Claude apps". It lists "Claude Agent SDK" as covered. Yet on 2026-10-19 the first headless run, `claude -p` on an API key, cost $2.10 by Claude Code's estimate, and the Console's credit fell from $200 to $197.72. So in practice the credit paid for it. Whether the page means Claude Code used through a Claude plan's own limits, or any use of Claude Code, the page does not say.

**Why it matters.** The whole runner is built on this credit. If the use is not covered, it could stop working or breach the program terms (https://www.anthropic.com/legal/credit-terms) without warning.

**Next step.** Read the program terms. If they do not settle it, the project owner asks Anthropic support. If the use is not covered, the runner could call the Agent SDK instead, which the page lists as covered.

**2026-10-20:** the project owner agreed to ask Anthropic support. Suggested wording: "Does the monthly API credit included with Max 20x cover running `claude -p` (Claude Code in print mode) with a Console API key from the linked organization?" Record the answer here.

**Done when.** The answer from the program terms or from Anthropic support is recorded here with its date. If the use is covered, this item closes. If it is not, the runner is moved to the Agent SDK under a new item.

**Decision needed.** Whether the headless runner keeps calling `claude -p` on the Console API key, or moves to the Claude Agent SDK, which the page lists as covered. It turns on support's answer.

**Recommended:** keep `claude -p` until support answers, and start no new runner work that depends on the credit in the meantime. Move to the Agent SDK only if support says the use is not covered.

**Decided 2026-10-24 (project owner, 2026-10-24):** the headless runner's use is covered. The owner answered "yes it is covered" when asked whether the Max plan's monthly API credit pays for `claude -p` on a Console API key from the linked organization. The owner based it on two things: a web search that said the use is covered, and the Console's credit balance falling by each run's cost, as it did on 2026-10-19. Neither is Anthropic support's answer or the program terms themselves. So the runner keeps calling `claude -p`, no move to the Agent SDK is needed, and this item closes as its Done-when says.

**Generator check.** One-off. An external terms question, not a misread fact in the tree.
