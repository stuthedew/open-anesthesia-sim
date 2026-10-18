---
id: PL-N80K
title: A post-merge commit that only deletes a file is never reported as left behind: the branch's content split is all landed, so _unlanded_refs treats it as taken whole and orphaned never asks about it (found building PL-TFF9)
status: untriaged
feature: stranded-report-fidelity
added: 2026-10-18
---

**Problem.** A post-merge commit that only deletes a file is never reported as left behind: the branch's content split is all landed, so _unlanded_refs treats it as taken whole and orphaned never asks about it (found building PL-TFF9)
