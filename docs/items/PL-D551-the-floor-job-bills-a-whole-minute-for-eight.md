---
id: PL-D551
title: The floor job bills a whole minute for eight seconds; its steps could run in the checks job ahead of the uv install and keep the bare-interpreter contract
priority: P3
effort: S
status: needs-decision
classes: infra
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-05
---
**Problem.** `quality.yml`'s `floor` job is billed a whole Actions minute
for eight seconds of work: a checkout, a `setup-python`, and five
standard-library commands.

**Why it matters.** The same recurring per-run cost as `PL-9HDH`, and the two
have to be answered together — each proposes moving work into a job the other
proposes moving.

**Where.** `.github/workflows/quality.yml`, the `floor` and `checks` jobs.

**Decision needed.** What the stated approach costs: running `floor`'s steps
inside `checks` ahead of the `uv` install keeps the *bare-interpreter* half of
the contract — no virtualenv in front of them — and loses the other half.
`floor` pins `python-version: '3.11'` deliberately, and its own comment says
why: left unset the action reads `.python-version`, "the project interpreter,
the one version this job exists not to test". `checks` inherits exactly that.
So the merged job would prove the tools run under the project interpreter,
which needed no proving, and stop proving they run under the declared floor,
which is the guarantee `tests/unit/test_tools_portability.py` is built around.

Keeping both means two `setup-python` steps in one job — 3.11 first, the five
commands, then the project version — which works and is less legible than two
jobs. That legibility-against-a-minute trade is the decision, and it is the
same decision `PL-9HDH` poses from the other end.

**Done when.** The project owner has chosen between keeping `floor` separate
and merging it behind a two-interpreter step sequence, and the choice with its
reasoning is recorded here.
