---
id: PL-D824
title: gate-status-guard.sh carries about 570 lines of Python inside one single-quoted shell string, so an apostrophe in any message it prints closes the string and the broken hook refuses every Bash call in the session (hit on 2026-11-03 with the word owner's); move the Python into its own .py file as owner_ask_guard.py is
status: untriaged
feature: guard-code-structure
added: 2026-11-03
---

**Problem.** gate-status-guard.sh carries about 570 lines of Python inside one single-quoted shell string, so an apostrophe in any message it prints closes the string and the broken hook refuses every Bash call in the session (hit on 2026-11-03 with the word owner's); move the Python into its own .py file as owner_ask_guard.py is
