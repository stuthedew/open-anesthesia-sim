---
id: PL-139L
title: vcs reads git's subject-bearing log output with str.splitlines, which also breaks at \x0b, \x0c, \x1c-\x1e, \x85 and \u2028, so a commit whose subject carries one is split and misread
status: untriaged
added: 2026-09-24
---

**Problem.** vcs reads git's subject-bearing log output with str.splitlines, which also breaks at \x0b, \x0c, \x1c-\x1e, \x85 and \u2028, so a commit whose subject carries one is split and misread
