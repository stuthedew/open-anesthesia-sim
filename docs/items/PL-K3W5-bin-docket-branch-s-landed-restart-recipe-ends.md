---
id: PL-K3W5
title: bin/docket branch's landed restart recipe ends at 'then push' without saying that a remote still holding the old branch - the case whenever a commit was pushed after the merge - refuses a plain push as non-fast-forward, so a session following it is left to choose between git pull, which brings the merged history back, and a force push the recipe never sanctioned
status: untriaged
added: 2026-09-27
---

**Problem.** bin/docket branch's landed restart recipe ends at 'then push' without saying that a remote still holding the old branch - the case whenever a commit was pushed after the merge - refuses a plain push as non-fast-forward, so a session following it is left to choose between git pull, which brings the merged history back, and a force push the recipe never sanctioned
