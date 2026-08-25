---
id: PL-NWH4
title: Write `docs/worker.md`, the standing prompt for a delegated run
priority: P2
effort: S
status: done
classes: docs, session-cost
feature: delegation
milestone: v0.2.4
touches: docs/worker.md, AGENTS.md
added: 2026-08-25
closed: 2026-08-25
commit: e17e7c0
---

**Problem.** Handing a batch of items to a cheaper model requires telling it
how this repository expects delegated work to be done. Reconstructing that
instruction each time is the friction the delegation tier exists to remove,
and a reconstructed prompt is a different prompt — the rules that matter get
dropped exactly when the session is being run cheaply.

**Why it matters.** The worker's failure mode is confident improvisation, and
the single instruction that prevents it — stop and record the ambiguity
rather than guessing — is the one most likely to be lost when the prompt is
retyped from memory.

**Where.** A new `docs/worker.md`, referenced from `CLAUDE.md` so a session
knows it exists. `AGENTS.md` already points every agent at `CLAUDE.md` in
full, so a Codex worker arrives with the safety standard already loaded.

**First step.** Write it as a *narrowing* of `CLAUDE.md`, not an addition. A
worker that has read `CLAUDE.md` arrives carrying the design rules — propose
before building, decompose ideas, put a case to the owner — and will start
proposing improvements to its own brief instead of writing the tests. State
that for the duration of a worker run those rules are suspended: do not
propose, do not redesign, do not decompose. Capture is the one rule that is
never suspended.

The rest is the loop: take the items `bin/docket list` marks delegable; one
branch for the batch carrying every item id in its name; one commit per item,
so the reviewer can drop one without rejecting the batch; `bin/docket verify
<id>` after each; a `**Worked.**` note on the item listing only what the brief
did not decide, empty being the expected case; push. Plus the setup line Codex
needs — `uv sync --locked --dev` before `make check` will run.

The worker changes no `status`. A dedicated `in-review` state was considered
and deferred until the pilot shows it is needed: the branch name carries every
id, so `docket flight` already reports the batch, and the reviewer sets
`done` on merge through the ordinary close-out.

And the exit: **if a brief is ambiguous, stop, write the ambiguity into the
item, and move to the next one.** Never guess at a brief.

**Done when.** A worker session pointed at `docs/worker.md` with no other
context completes a batch and pushes it, and the file states the stop-rule and
the CLAUDE.md suspension explicitly enough that a cheap model follows both.

**Worked.** Built ahead of PL-D7JQ and PL-ZR1R, which it was written to expect,
because the owner is near a usage limit and this item is the only one standing
between them and a running worker. It degrades to the tools that exist today:
the worker is told to run each item's `verify:` command directly and to select
work with `docket list | grep delegable`, both of which `docket verify` and
`docket delegable` will later shorten without invalidating the instruction.

`CLAUDE.md` was dropped from `touches`: `AGENTS.md` is what a Codex worker
reads, and it already routes to `CLAUDE.md`, so a second pointer would have
cost a cache invalidation on every Claude session for no reach.
