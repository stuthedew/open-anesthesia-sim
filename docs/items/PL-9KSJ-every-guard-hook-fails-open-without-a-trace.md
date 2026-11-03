---
id: PL-9KSJ
title: Every guard hook fails open without a trace: each discards stderr and exits 0 on a crash, so a broken guard reads to the session exactly as a pass, including no-prune-guard.sh, the one guarding an irreversible loss
status: untriaged
feature: guards-say-when-they-cannot-check
added: 2026-11-03
---

**Problem.** Every guard hook fails open without a trace: each discards stderr and exits 0 on a crash, so a broken guard reads to the session exactly as a pass, including no-prune-guard.sh, the one guarding an irreversible loss
