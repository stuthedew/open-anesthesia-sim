---
id: PL-0FGH
title: The gate-status guard refused make doc-check > log 2>&1 && git add ... && git commit ... && git push ... | grep -v remote, reading the later git push pipeline's grep as doc-check's last stage, though | binds tighter than && so doc-check's status gated the chain (met in ordinary work 2026-09-27, evidence for PL-61FT)
status: untriaged
added: 2026-09-27
---

**Problem.** The gate-status guard refused make doc-check > log 2>&1 && git add ... && git commit ... && git push ... | grep -v remote, reading the later git push pipeline's grep as doc-check's last stage, though | binds tighter than && so doc-check's status gated the chain (met in ordinary work 2026-09-27, evidence for PL-61FT)
