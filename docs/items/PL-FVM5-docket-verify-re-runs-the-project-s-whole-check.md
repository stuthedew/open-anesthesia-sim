---
id: PL-FVM5
title: `docket verify` re-runs the project's whole check once per item, so a six-item batch takes two minutes
status: ready
priority: P3
effort: S
classes: session-cost
feature: delegation
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests, subprojects/docket/README.md
added: 2026-08-25
verify: uv run pytest subprojects/docket/tests/test_verify.py -k batch
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

**Built as the first option, not the flag.** `verify` splits into
`verify_item` (the item's own command, its declared scope, its commits — all
genuinely per item) and `project_check` (the tree's own check, which proves
the same thing however many items are asked about). `docket verify` now takes
several ids rather than one, so the batch case needs no flag to reach and the
single-item case is unchanged: one id still runs the project check.

An item that stops early — no `verify:` command, or nothing between its base
and `HEAD` — does not reach the shared check, because the check says nothing
about it either way.
