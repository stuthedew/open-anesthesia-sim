---
id: PL-LSTW
title: tools/ignore_check.py is named for .gitignore but evaluates type: ignore directives, so a session looking for the gitignore check finds it and a session looking for the mypy one does not
status: untriaged
touches: tools/ignore_check.py, Makefile
added: 2026-09-15
---

**Problem.** tools/ignore_check.py is named for .gitignore but evaluates type: ignore directives, so a session looking for the gitignore check finds it and a session looking for the mypy one does not
