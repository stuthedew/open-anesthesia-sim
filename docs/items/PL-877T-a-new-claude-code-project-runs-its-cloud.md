---
id: PL-877T
title: A new Claude Code project runs its cloud threads in Anthropic's default environment until Project settings > Environment names Default, and nothing the owner reads when creating one says so, so the next project's threads will pay PL-QKXZ's uv and libegl1 repair again
priority: P3
effort: S
status: ready
classes: docs
feature: projects-trial
touches: docs/maintainer.md
added: 2026-09-26
payoff: the next Claude Code project the owner creates starts its threads in Default, so none of them pays PL-QKXZ's uv and libegl1 repair before make check will run
verify: grep -qF 'Project settings > Environment' docs/maintainer.md
---

**Problem.** A new Claude Code project runs its cloud threads in Anthropic's default environment until Project settings > Environment names Default, and nothing the owner reads when creating one says so, so the next project's threads will pay PL-QKXZ's uv and libegl1 repair again

**Found 2026-09-26 while working `PL-QKXZ`.** The Projects docs put it in one
sentence (https://code.claude.com/docs/en/claude-projects, § "Choose an
environment for threads", fetched 2026-09-26): "Cloud threads use a default
Anthropic-hosted environment until you pick one in **Project settings >
Environment**." Both projects so far started there. "Clean up PL" was moved to
`Default` on 2026-09-26, and "Fix generators" had not been at 04:34 UTC that
day. `PL-QKXZ` records the setting as "owed again by any new project", but
only in its own brief, which nobody reads once it closes.

**Candidate carrier.** A line under `docs/maintainer.md` § "Settings that
make sessions cheaper": set **Cloud environment** to **Default** when creating
a project, and why. Whether the owner would read it at that moment is the open
question, and triage's to weigh against the alternative of leaving it to the
first thread to rediscover.

**Generator check.** Not a head: one observation, and the fact it rests on,
which environment a Projects thread runs in, is `PL-QKXZ`'s.

**Triaged 2026-09-26: the line goes in.** It costs two sentences in the
document the owner reads for settings only they can change, against a thread
per project paying the repair again until one notices. Whether the owner reads
it at the moment of creating a project is not the test: a session asked to
help set one up reads it there too, and `PL-NZC0`'s setup paragraph, the only
other carrier, closes with that trial.

**Why it matters.** A thread in Anthropic's default environment runs without
the owner's setup script, so before `make check` will run it repairs uv and
libegl1 as `PL-QKXZ` recorded, once per thread, with nothing it reads saying
why.

**Done when.** `docs/maintainer.md` § "Settings that make sessions cheaper"
tells the owner to set **Project settings > Environment** to `Default` when
creating a project, and why.
