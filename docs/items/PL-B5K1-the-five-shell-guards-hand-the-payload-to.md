---
id: PL-B5K1
title: The five shell guards hand the payload to Python through an environment variable, so any Bash command over about 128 KiB fails exec with E2BIG and passes every guard: a 140,000-character heredoc before git fetch --prune is let through
status: untriaged
feature: guards-say-when-they-cannot-check
added: 2026-11-03
---

**Problem.** The five shell guards hand the payload to Python through an environment variable, so any Bash command over about 128 KiB fails exec with E2BIG and passes every guard: a 140,000-character heredoc before git fetch --prune is let through
