---
id: PL-KL2Q
title: core/parameters.py now holds two overlapping percent/fraction vocabularies - Pydantic's PositivePercent which validates but does not type-check, and concentration.py's Percent which type-checks but does not validate - and nothing says which a new field takes
status: untriaged
added: 2026-09-13
---

**Problem.** core/parameters.py now holds two overlapping percent/fraction vocabularies - Pydantic's PositivePercent which validates but does not type-check, and concentration.py's Percent which type-checks but does not validate - and nothing says which a new field takes
