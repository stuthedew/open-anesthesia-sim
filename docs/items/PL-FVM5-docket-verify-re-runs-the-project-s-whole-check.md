---
id: PL-FVM5
title: `docket verify` re-runs the project's whole check once per item, so a six-item batch takes two minutes
status: ready
priority: P3
effort: S
classes: session-cost
feature: delegation
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/cli.py
added: 2026-08-25
---

**Problem.** `docket verify` runs `config.check_command` (`make check` here)
for every item it verifies. Reviewing the six-item guard-coverage batch ran
the full suite six times and took over two minutes, five of those runs
proving something already proved.

**Why it matters.** Not correctness — the answer is right, just slow. But the
tier's whole claim is that accepting delegated work is cheap, and a reviewer
who waits two minutes for a batch will start skipping the command, which
costs the guarantee rather than the time. It gets worse linearly with batch
size.

**Where.** `subprojects/docket/src/docket/verify.py`, and whatever batch entry
point PL-ZR1R's listing suggests.

**First step.** The per-item checks are cheap and genuinely per-item; only the
project-wide check is shared. Splitting `verify` into the per-item half and a
batch half run once — or a `docket verify --batch` taking several ids and
running `check_command` a single time — keeps the meaning and removes the
repetition. Note that the item's own `verify:` command must still run per
item, since that is what makes each one individually acceptable or
rejectable.

**Done when.** Verifying a batch runs the project-wide check once, and a
single-item verify still runs it.
