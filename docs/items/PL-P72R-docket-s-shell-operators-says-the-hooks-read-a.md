---
id: PL-P72R
title: docket's shell.OPERATORS says the hooks read a command by the same table as .claude/hooks/shell_split.py's, and nothing checks it: the two differed by <<- until PL-Q9LK
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/shell.py, .claude/hooks/shell_split.py, subprojects/docket/tests/test_shell.py
added: 2026-10-03
---

**Problem.** docket's shell.OPERATORS says the hooks read a command by the same table as .claude/hooks/shell_split.py's, and nothing checks it: the two differed by \<\<- until PL-Q9LK
