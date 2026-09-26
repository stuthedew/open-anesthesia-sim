---
id: PL-WGFY
title: no-prune-guard.sh finds a command position with its own regex rather than a shell split, so a ';' inside a quoted argument reads as a separator: on 2026-09-26 it refused a Bash call whose only 'git fetch --prune' was single-quoted text passed to a for loop
status: untriaged
feature: one-answer
added: 2026-09-26
---

**Problem.** no-prune-guard.sh finds a command position with its own regex rather than a shell split, so a ';' inside a quoted argument reads as a separator: on 2026-09-26 it refused a Bash call whose only 'git fetch --prune' was single-quoted text passed to a for loop
