---
id: PL-R0P3
title: tools/doc_check.py's _read_store duplicates the config-and-store read that check_gate_reentries and check_gate_dispositions each spell inline, so three spellings of one question can disagree
status: untriaged
added: 2026-09-14
---

**Problem.** tools/doc_check.py's _read_store duplicates the config-and-store read that check_gate_reentries and check_gate_dispositions each spell inline, so three spellings of one question can disagree
