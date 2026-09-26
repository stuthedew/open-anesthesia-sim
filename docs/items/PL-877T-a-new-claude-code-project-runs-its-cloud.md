---
id: PL-877T
title: A new Claude Code project runs its cloud threads in Anthropic's default environment until Project settings > Environment names Default, and nothing the owner reads when creating one says so, so the next project's threads will pay PL-QKXZ's uv and libegl1 repair again
status: untriaged
feature: projects-trial
added: 2026-09-26
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
