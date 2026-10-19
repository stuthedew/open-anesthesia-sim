---
id: PL-W38C
title: tools/headless_worker.py fails on the owner's Mac: it starts bin/docket, a bash script, with the Python interpreter, and the how-to runs it with python3, which is Xcode's 3.9 there, below the tools' 3.11 floor
status: untriaged
feature: api-credit-runs
added: 2026-10-19
---

**Problem.** tools/headless_worker.py fails on the owner's Mac: it starts bin/docket, a bash script, with the Python interpreter, and the how-to runs it with python3, which is Xcode's 3.9 there, below the tools' 3.11 floor
