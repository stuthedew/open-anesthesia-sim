---
id: PL-DM95
title: tools/copy_edit.py keeps only the last message of a read whose reply spans several messages, so the read is called unreadable and dropped: #2056's fourth read (8 turns) came back starting mid-passage, and its 16 verdicts were lost (2026-11-09)
status: untriaged
feature: repo-copy-edit
touches: tools/copy_edit.py
added: 2026-11-09
---

**Problem.** tools/copy_edit.py keeps only the last message of a read whose reply spans several messages, so the read is called unreadable and dropped: #2056's fourth read (8 turns) came back starting mid-passage, and its 16 verdicts were lost (2026-11-09)
