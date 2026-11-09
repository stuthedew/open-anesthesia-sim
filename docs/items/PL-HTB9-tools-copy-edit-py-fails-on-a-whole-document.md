---
id: PL-HTB9
title: tools/copy_edit.py fails on a whole-document request: on 2026-11-09 the first read of a 40-passage, 137 KB request from tools/new_prose.py (PL-T8RL's restructure of docs/interface-provenance.md) returned only the reply's last 16 KB, passage 40 and the end of 39, so the run stopped with 'no verdict' for passages 1-39 after 38 minutes; close-out step 8 gives no way to split a request, and the session split it by hand into eight batches of whole sections
status: untriaged
added: 2026-11-09
---

**Problem.** tools/copy_edit.py fails on a whole-document request: on 2026-11-09 the first read of a 40-passage, 137 KB request from tools/new_prose.py (PL-T8RL's restructure of docs/interface-provenance.md) returned only the reply's last 16 KB, passage 40 and the end of 39, so the run stopped with 'no verdict' for passages 1-39 after 38 minutes; close-out step 8 gives no way to split a request, and the session split it by hand into eight batches of whole sections
