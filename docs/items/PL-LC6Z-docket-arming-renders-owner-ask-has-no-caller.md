---
id: PL-LC6Z
title: docket.arming.renders_owner_ask has no caller outside its tests since PL-X4MD removed the owner-ask guard's wording match; retiring it edits tests in subprojects/docket/tests/test_cli.py that pin arm's answers, so it waits on the owner's read
status: untriaged
feature: owner-ask-by-state
added: 2026-11-04
---

**Problem.** docket.arming.renders_owner_ask has no caller outside its tests since PL-X4MD removed the owner-ask guard's wording match; retiring it edits tests in subprojects/docket/tests/test_cli.py that pin arm's answers, so it waits on the owner's read
