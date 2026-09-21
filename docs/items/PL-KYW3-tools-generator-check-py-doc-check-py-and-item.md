---
id: PL-KYW3
title: tools/generator_check.py, doc_check.py and item_reads.py each restate the item-id grammar, all three more loosely than store.ID_PATTERN, so a tool and docket check disagree about what is an id
status: untriaged
feature: one-id-grammar
touches: tools/generator_check.py, tools/doc_check.py, tools/item_reads.py
added: 2026-09-21
---

**Problem.** tools/generator_check.py, doc_check.py and item_reads.py each restate the item-id grammar, all three more loosely than store.ID_PATTERN, so a tool and docket check disagree about what is an id
