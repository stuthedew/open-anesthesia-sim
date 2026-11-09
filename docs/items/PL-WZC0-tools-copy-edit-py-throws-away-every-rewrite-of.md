---
id: PL-WZC0
title: tools/copy_edit.py throws away every rewrite of a request when one meaning-check reply has two verdicts for a passage, even where the checker retracted the first itself; #2056's whole 16-passage edit came back as keep after 90 minutes because reader 2 corrected its [7] verdict in the same reply. Retry that reader once instead (2026-11-09)
status: untriaged
feature: repo-copy-edit
touches: tools/copy_edit.py
added: 2026-11-09
---

**Problem.** tools/copy_edit.py throws away every rewrite of a request when one meaning-check reply has two verdicts for a passage, even where the checker retracted the first itself; #2056's whole 16-passage edit came back as keep after 90 minutes because reader 2 corrected its [7] verdict in the same reply. Retry that reader once instead (2026-11-09)
