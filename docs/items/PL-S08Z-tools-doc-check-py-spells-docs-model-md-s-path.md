---
id: PL-S08Z
title: tools/doc_check.py spells docs/MODEL.md's path a third time, as MODEL = Path("docs/MODEL.md"), beside product_paths.MODEL_DOC, which PL-5S71 made the home; fact_home_check misses it because the name differs
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** tools/doc_check.py spells docs/MODEL.md's path a third time, as MODEL = Path("docs/MODEL.md"), beside product_paths.MODEL_DOC, which PL-5S71 made the home; fact_home_check misses it because the name differs
