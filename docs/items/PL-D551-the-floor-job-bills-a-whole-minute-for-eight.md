---
id: PL-D551
title: The floor job bills a whole minute for eight seconds; its steps could run in the checks job ahead of the uv install and keep the bare-interpreter contract
priority: P3
effort: S
status: done
classes: infra
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-05
closed: 2026-09-05
pr: 361
verify: ! grep -q '^  floor:' .github/workflows/quality.yml && test "$(grep -n 'setup-python@' .github/workflows/quality.yml | cut -d: -f1)" -lt "$(grep -n 'setup-uv@' .github/workflows/quality.yml | cut -d: -f1)"
---

**Problem.** The floor job bills a whole minute for eight seconds; its steps could run in the checks job ahead of the uv install and keep the bare-interpreter contract

**Why it matters.**

**Where.**

**Done when.**

**Done.** The `floor` job's steps now run inside `checks`, immediately after the
checkout and **before** `astral-sh/setup-uv`. Order is the whole design: the
separate job only *assumed* isolation from a parallel one, while here no
virtualenv and no `UV_*` variable exists yet to leak from, so the no-virtualenv
claim is stronger than it was rather than weaker. It also fails fast - a broken
doc reference costs one billable minute instead of five, because the suite never
starts.

Three jobs per pull-request push become two, which is a slot back against the
account-wide 20-concurrent-job cap. That cap, not minutes, is what throttles
several sessions running at once.

`PL-9HDH` proposed folding the pull-request title check in here too. It is
dropped rather than done; the reason is on that item.
