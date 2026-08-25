---
id: PL-R0SR
title: `docs/worker.md` should say that corrections arrive by pulling the branch, never in chat
status: ready
priority: P2
effort: S
classes: defect, docs, session-cost
feature: worker-instructions
touches: docs/worker.md
added: 2026-08-25
---

**Problem.** `docs/worker.md` tells a worker to run the item's `verify:`
command, and says nothing about where a correction to that command comes from.
When six commissions shipped with broken commands, the corrections were sent
to the worker in chat with an explicit "you do not need to pull". The worker
ran the stale command from the item file instead — correctly, since that is
what the standing instruction says — and blocked all six a second time.

**Why it matters.** The commission is the item file. A worker that preferred
chat to the file would be a worker whose scope, checks and prohibitions could
all be loosened by conversation, which is precisely what the delegation design
must not allow. So the behaviour is right and the instructions are wrong: they
never say that the file is the only source, or how a corrected file reaches a
run already in progress.

**Where.** `docs/worker.md`, most naturally in **The loop** or beside **When a
brief is unclear**.

**First step.** State two things. Corrections arrive by pulling the base
branch, never in chat — if a message contradicts an item file, the file wins
and the worker should say so rather than comply. And a worker resuming after
blocking should re-read the item files first, since a block is the most likely
reason a commission has just changed.

**Done when.** `docs/worker.md` names the item file as the only source of a
commission, and tells a resuming worker to pull before re-running.
