---
id: PL-H8NX
title: thread_hooks.py re-runs the repository's SessionStart commands when the hooks block changed between two starts in one container, while Claude Code already runs the copies it installed, so the digest, fetch and effort-trial write run twice
status: untriaged
feature: guard-review-2026-11
added: 2026-11-03
---

**Problem.** thread_hooks.py re-runs the repository's SessionStart commands when the hooks block changed between two starts in one container, while Claude Code already runs the copies it installed, so the digest, fetch and effort-trial write run twice
