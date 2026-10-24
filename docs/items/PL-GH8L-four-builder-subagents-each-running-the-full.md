---
id: PL-GH8L
title: Four builder subagents each running the full suite at once drove the container's load average to about 30 on 4 cores, so bin/docket verify --self's make check step hit its fixed 1,800 s limit and gave no answer on three branches
status: untriaged
added: 2026-10-24
---

**Problem.** Four builder subagents each running the full suite at once drove the container's load average to about 30 on 4 cores, so bin/docket verify --self's make check step hit its fixed 1,800 s limit and gave no answer on three branches
