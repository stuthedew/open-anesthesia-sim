---
id: PL-73G8
title: The recovery file header claims the body verbatim, but it is the body as GitHub serves it today rather than at merge time, and its commit: sha silently dangles after a history rewrite with nothing checking it
status: untriaged
feature: pr-body-integrity
added: 2026-09-20
---

**Problem.** The recovery file header claims the body verbatim, but it is the body as GitHub serves it today rather than at merge time, and its commit: sha silently dangles after a history rewrite with nothing checking it
