---
id: PL-80R5
title: Run delegable queue items headless on the monthly Claude Platform API credits - a script on the owner's machine that runs claude -p under docs/worker.md, one ready delegable item per run with a --max-budget-usd cap, records each run's total_cost_usd, and stops when the cycle's credit is spent (credits do not cover interactive or GitHub Action Claude Code, and expire unused each billing cycle)
priority: P2
effort: M
status: done
feature: api-credit-runs
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, docs/maintainer.md, docs/worker.md, docs/items/PL-80R5-run-delegable-queue-items-headless-on-the.md
added: 2026-10-19
closed: 2026-10-19
verify: uv run pytest -q tests/unit/test_headless_worker.py
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

**Decided (project owner, 2026-10-19, ratified, over Sonnet 5.5 workers): the workers run on Opus 5.5.** The question as it was put follows. This brief
first named Sonnet 5.5, the `delegable` tier in `docs/maintainer.md`. That
tier rests on the owner's 2026-09-19 asymmetry: default to Opus whenever in
doubt. `PL-2D28` then kept Explore subagents on Opus and cheapened no search
(project owner, 2026-10-17, ratified, over Haiku 5.5 and Sonnet 5.5). Its
reason was that a cheaper model's miss enters the record and costs more later
than the saving. The monthly credit changes the cost side and nothing else.
It expires unused, so a dollar saved by a cheaper model buys nothing. The risk
side is unchanged. **Recommended:** run the workers on Opus 5.5 and accept
roughly half the items per month, about 25 to 50 `S` items by the estimate
above. That keeps the asymmetry and the `PL-2D28` decision intact. Keep Sonnet
5.5 out unless `PL-6FX6` measures it as safe.

**Next step, written 2026-10-19 before a context reset.** Build the runner.
Read `docs/worker.md` in full first, because its loop, its claim and its
closing note are what each headless run must follow. Then settle one open
mechanism and record the answer here. With `--bare`, billing is certain to go
to the API key, but `CLAUDE.md`, the hooks and the skills do not load. Without
`--bare`, they load, but a missing key would bill the subscription instead.
Check the authentication docs for which applies when `ANTHROPIC_API_KEY` is
set under `-p`. The runner also needs a `--model` option and a no-push mode,
because `PL-6FX6`'s trial runs Sonnet and Haiku copies that must never be
pushed. Its plumbing is tested with a fake `claude` executable, because no
session holds the key.

**Built 2026-10-19, and the `--bare` question settled.** The runner runs
without `--bare`. Anthropic's authentication page ranks the credentials, and
under `-p` "the key is always used when present"
(https://code.claude.com/docs/en/authentication, "Authentication precedence",
read 2026-10-19). Only cloud-provider selection and `ANTHROPIC_AUTH_TOKEN` rank
above the key, and a signed-in Claude apps gateway session sits outside the
list. So the runner refuses to start without `ANTHROPIC_API_KEY` and drops the
outranking variables from the run's environment. That makes the billing as
certain as bare mode would, and the run still loads `CLAUDE.md`, the skills and
the hooks. Bare mode was refused because the hooks are part of what keeps a
worker inside its rules. The gateway case cannot be detected and is named in
the script's docstring.

What was built:

- `tools/headless_worker.py` clones the repository for each run, borrowing this
  checkout's objects, and makes a branch named `claude/<id>-worker`. It starts
  one `claude -p` run on Opus 5.5 with `--max-budget-usd`, auto mode and
  permission prompts denied, and appends the reported `total_cost_usd` to a
  ledger. It stops before a run that the cycle's remaining credit cannot cover.
  A run whose cost cannot be read stops the batch, and the next start refuses
  until the ledger line is corrected.
- `--no-push` sets the clone's push URL to a name no remote answers to, so a
  trial copy cannot leave the machine whatever the worker does. `--model`
  selects the trial's other models.
- `bin/docket delegable --ids` prints the delegable list as bare ids, so the
  runner reads the one list that `docket` computes rather than parsing prose.
- `docs/maintainer.md` § "Spend the monthly API credit on delegable items" has
  the owner's steps, and `docs/worker.md`'s loop now tells a headless worker
  to use the branch the runner made.

Tested with a fake `claude` executable that records its arguments, commits and
tries to push (`tests/unit/test_headless_worker.py`). Nothing has run against
the real API yet: no session holds the key. The first real runs are
`PL-6FX6`'s trial, and they also check the cost estimate against the Console's
usage page.

**Generator check.** Not a head and not an instance: a new tool requested by the project owner, and it reads its one shared fact, the delegable list, from `bin/docket delegable --ids` rather than deriving it again.
