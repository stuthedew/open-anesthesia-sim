---
id: PL-VZYS
title: A hand-run 'uv run ruff check .' still reads the stale .ruff_cache that PL-QSJM's --no-cache removes from make check and make fix, so the guard sits at the entry point rather than where the tool reads it - the same shape as PL-0MLZ's finding about PYTHONDONTWRITEBYTECODE
status: untriaged
added: 2026-09-15
---

**Problem.** A hand-run 'uv run ruff check .' still reads the stale .ruff_cache that PL-QSJM's --no-cache removes from make check and make fix, so the guard sits at the entry point rather than where the tool reads it - the same shape as PL-0MLZ's finding about PYTHONDONTWRITEBYTECODE
