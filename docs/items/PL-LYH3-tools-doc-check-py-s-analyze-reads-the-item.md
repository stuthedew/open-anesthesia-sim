---
id: PL-LYH3
title: tools/doc_check.py's analyze() reads the item store seven times in one run (16,009 parse_item calls for about 2,300 items, via _read_store), about 10.6 s of a 59 s profiled whole-repository analysis on 2026-10-17, and a quality.yml checks job runs that analysis five times (the two doc_check.py check steps and three tests in tests/unit/test_doc_check.py), so reading the store once per analysis would cut each run by roughly a sixth (found working PL-H9KW)
status: untriaged
feature: ci-cost
added: 2026-10-17
---

**Problem.** tools/doc_check.py's analyze() reads the item store seven times in one run (16,009 parse_item calls for about 2,300 items, via _read_store), about 10.6 s of a 59 s profiled whole-repository analysis on 2026-10-17, and a quality.yml checks job runs that analysis five times (the two doc_check.py check steps and three tests in tests/unit/test_doc_check.py), so reading the store once per analysis would cut each run by roughly a sixth (found working PL-H9KW)
