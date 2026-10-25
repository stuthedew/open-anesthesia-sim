---
id: PL-P0RG
title: The untied-restatement check reads each line of docs/MODEL.md on its own, so a math span that hard wrapping splits across two lines, such as one ending V_A = and the next starting 2.5, is read on neither line and its figure goes unchecked
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** The untied-restatement check reads each line of docs/MODEL.md on its own, so a math span that hard wrapping splits across two lines, such as one ending V_A = and the next starting 2.5, is read on neither line and its figure goes unchecked
