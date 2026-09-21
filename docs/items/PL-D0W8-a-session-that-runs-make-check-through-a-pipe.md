---
id: PL-D0W8
title: A session that runs make check through a pipe - make check 2>&1 | tail - reads the pipeline's exit status, which is tail's and always 0, so a red tree is reported and committed as green: it happened on PL-2JRC and the false claim reached both the commit message and the pull request body
status: untriaged
added: 2026-09-21
---

**Problem.** A session that runs make check through a pipe - make check 2>&1 | tail - reads the pipeline's exit status, which is tail's and always 0, so a red tree is reported and committed as green: it happened on PL-2JRC and the false claim reached both the commit message and the pull request body
