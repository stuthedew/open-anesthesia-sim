---
id: PL-44SP
title: tools/headless_worker.py carries on to the next item after a run that failed because the API credit ran out, so one empty balance can start and fail every item left in the batch, each leaving a clone behind
status: untriaged
added: 2026-10-20
---

**Problem.** tools/headless_worker.py carries on to the next item after a run that failed because the API credit ran out, so one empty balance can start and fail every item left in the batch, each leaving a clone behind

**What happens now.** When the balance is empty, the API returns "Your credit balance is too low to access the Anthropic API" (https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers, § "When credits run out", read 2026-10-20). Claude Code classes that as `billing_error` (https://code.claude.com/docs/en/headless). `main()` in `tools/headless_worker.py` stops a batch only when a run's cost cannot be read. A run that failed on billing still reports a cost, so the loop starts the next item. Each later run fails at once, and each keeps its clone because nothing was pushed.

**Fix.** Stop the batch after a run that failed on billing, and say so in the report. Recognise it by Claude Code's `billing_error` category or the API's message. This belongs with the build of PL-NQ0M, which changes the same loop.

**Widened, 2026-10-20: stop the batch after any failed run, not only a billing failure.** The project owner asked what happens if the Mac sleeps or loses its internet connection mid-run. Each of those, like an empty credit, makes the next run fail too. Claude Code retries a failed request a limited number of times (`system/api_retry`, with `max_retries`, https://code.claude.com/docs/en/headless), so a long outage ends the run as an error. The runner then starts the next item, which fails the same way. A failure that is one item's own is rarer, and still wants a person to look before more credit is spent. So the fix is: after any run that ends in error, print why and stop the batch.
