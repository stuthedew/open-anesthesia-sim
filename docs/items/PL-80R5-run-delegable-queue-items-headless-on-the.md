---
id: PL-80R5
title: Run delegable queue items headless on the monthly Claude Platform API credits: a script on the owner's machine that runs claude --bare -p on Sonnet 5.5 under docs/worker.md, one ready delegable item per run with a --max-budget-usd cap, records each run's total_cost_usd, and stops when the month's credit is spent (credits do not cover interactive or GitHub Action Claude Code, and expire unused each billing cycle)
status: untriaged
feature: api-credit-runs
added: 2026-10-19
---

**Problem.** Run delegable queue items headless on the monthly Claude Platform API credits: a script on the owner's machine that runs claude --bare -p on Sonnet 5.5 under docs/worker.md, one ready delegable item per run with a --max-budget-usd cap, records each run's total_cost_usd, and stops when the month's credit is spent (credits do not cover interactive or GitHub Action Claude Code, and expire unused each billing cycle)

**What the credit covers, read 2026-10-19.** Anthropic's support article
"Monthly API credits for Max and Team plans"
(https://support.claude.com/en/articles/17154008) gives Max 20x $200 a month
in one linked Claude Console organization. The credit covers the Messages API,
the Message Batches API, Claude Managed Agents and the Claude Agent SDK. It
covers `claude -p` only when it runs with an API key from the linked
organization. It does not cover interactive Claude Code on any surface, extra
usage, or runs started by the Claude Code GitHub Action, "even with `-p`".
Unused credit expires at the end of each billing cycle, so it is a monthly
budget and not a pot to save.

**How the run is shaped.** `claude --bare -p` reads `ANTHROPIC_API_KEY` and
never the subscription login, and `--output-format json` reports
`total_cost_usd`; `--max-budget-usd` caps one run
(https://code.claude.com/docs/en/headless, read 2026-10-19). Bare mode skips
`CLAUDE.md`, hooks and skills, so the script must pass `docs/worker.md` and
`CLAUDE.md` in itself and must decide which hooks a worker still needs.

**Pool, counted 2026-10-19.** 68 open items are delegable by
`Item.delegability`: 59 product, 8 crossing, 1 workflow; 53 `S` and 15 `M`.

**Cost estimate, inferred and not measured.** At Sonnet 5.5's $2 input and
$10 output per million tokens (docs/maintainer.md), with cache reads at a
tenth of input, an `S` item of about 50 turns at a mean context of 150,000
tokens costs roughly $2 to $4. That puts $200 at roughly 50 to 100 `S` items.
The first runs measure it; `PL-6FX6` is that trial.

**The likelier limit is review, not money.** A simulator change arms only
with an `Owner-read:` record, so each product pull request may wait on the
project owner. Size each month's batch to what they will read.
