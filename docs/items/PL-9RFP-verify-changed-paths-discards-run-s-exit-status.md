---
id: PL-9RFP
title: verify.changed_paths discards _run's exit status and _run returns combined stdout+stderr, so any base that does not resolve makes git's three-line fatal message come back as three changed paths and the commission audit reports them as findings while missing the real ones
status: untriaged
feature: evidence-declines
added: 2026-09-22
---

**Problem.** verify.changed_paths discards _run's exit status and _run returns combined stdout+stderr, so any base that does not resolve makes git's three-line fatal message come back as three changed paths and the commission audit reports them as findings while missing the real ones
