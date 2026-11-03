---
id: PL-3HQ6
title: item_read_log.py starts Python on every Read, Grep and Glob call, about 50 ms each, never sees bin/docket show, and serves no open decision since PL-NB35 and PL-KM3X closed; retire it
status: untriaged
feature: guard-review-2026-11
added: 2026-11-03
---

**Problem.** item_read_log.py starts Python on every Read, Grep and Glob call, about 50 ms each, never sees bin/docket show, and serves no open decision since PL-NB35 and PL-KM3X closed; retire it
